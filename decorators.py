"""
DECORADORES DE AUTENTICACIÓN Y ROLES - SICADFOC 2026
Sistema de decoradores para control de acceso basado en roles
DBA Senior & Full-Stack - WindSurf
"""
import functools
import streamlit as st
import logging
from datetime import datetime
from sqlalchemy import text

# Importar conexión desde módulo independiente
from database.connection import get_engine_local

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache para permisos de usuario (optimización)
PERMISOS_CACHE = {}

def obtener_rol_usuario(id_usuario):
    """Obtener el rol de un usuario desde la base de datos"""
    
    # Verificar cache primero
    if id_usuario in PERMISOS_CACHE:
        return PERMISOS_CACHE[id_usuario]
    
    try:
        engine = get_engine_local()
        with engine.connect() as conn:
            # CORRECCIÓN: Usar campo correcto según estructura de tabla
            # La tabla usuario tiene 'rol' (VARCHAR) y 'rol_id' (INTEGER)
            # Usamos 'rol' para obtener el nombre del rol directamente
            
            query = """
                SELECT u.rol as nombre_rol
                FROM usuario u
                WHERE u.id = :id_usuario
            """
            
            result = conn.execute(text(query), {'id_usuario': id_usuario}).fetchone()
            
            if result:
                rol_nombre = result[0]
                
                # Mapeo de roles a niveles de acceso
                niveles_acceso = {
                    'Administrador': 100,
                    'Profesor': 50,
                    'Estudiante': 10
                }
                
                nivel_acceso = niveles_acceso.get(rol_nombre, 0)
                
                # Obtener permisos según el rol
                permisos_por_rol = {
                    'Administrador': [
                        'usuario.crear', 'usuario.editar', 'usuario.ver', 'usuario.eliminar',
                        'curso.crear', 'curso.editar', 'curso.ver', 'curso.eliminar',
                        'taller.crear', 'taller.editar', 'taller.ver', 'taller.eliminar',
                        'auditoria.ver', 'sistema.configurar', 'sistema.backup'
                    ],
                    'Profesor': [
                        'curso.ver', 'curso.editar', 'taller.ver', 'taller.editar',
                        'auditoria.ver'
                    ],
                    'Estudiante': [
                        'curso.ver', 'taller.ver', 'auditoria.ver'
                    ]
                }
                
                permisos = permisos_por_rol.get(rol_nombre, [])
                modulos = list(set([p.split('.')[0] for p in permisos]))
                
                rol_info = {
                    'id_rol': id_usuario,  # Usamos ID de usuario como referencia
                    'nombre_rol': rol_nombre,
                    'nivel_acceso': nivel_acceso,
                    'permisos': permisos,
                    'modulos': modulos
                }
                
                # Guardar en cache
                PERMISOS_CACHE[id_usuario] = rol_info
                
                return rol_info
            else:
                logger.warning(f"⚠️ No se encontró rol para usuario {id_usuario}")
                return None
                
    except Exception as e:
        logger.error(f"❌ Error obteniendo rol del usuario {id_usuario}: {e}")
        return None
        logger.error(f"❌ Error obteniendo rol del usuario {id_usuario}: {e}")
        return None

def verificar_permiso(usuario, permiso_requerido):
    """Verificar si un usuario tiene un permiso específico"""
    
    if not usuario or 'id' not in usuario:
        return False
    
    rol_info = obtener_rol_usuario(usuario['id'])
    
    if not rol_info:
        return False
    
    # Administrador tiene todos los permisos
    if rol_info['nombre_rol'] == 'Administrador':
        return True
    
    # Verificar permiso específico
    return permiso_requerido in rol_info['permisos']

def verificar_permisos(usuario, permisos_requeridos):
    """Verificar si un usuario tiene todos los permisos requeridos"""
    
    if not usuario or 'id' not in usuario:
        return False
    
    rol_info = obtener_rol_usuario(usuario['id'])
    
    if not rol_info:
        return False
    
    # Administrador tiene todos los permisos
    if rol_info['nombre_rol'] == 'Administrador':
        return True
    
    # Verificar que tenga todos los permisos requeridos
    return all(permiso in rol_info['permisos'] for permiso in permisos_requeridos)

def verificar_rol(usuario, rol_requerido):
    """Verificar si un usuario tiene un rol específico"""
    
    if not usuario or 'rol' not in usuario:
        return False
    
    return usuario['rol'].lower() == rol_requerido.lower()

def verificar_nivel_acceso(usuario, nivel_minimo):
    """Verificar si un usuario tiene un nivel de acceso mínimo"""
    
    if not usuario or 'id' not in usuario:
        return False
    
    rol_info = obtener_rol_usuario(usuario['id'])
    
    if not rol_info:
        return False
    
    return rol_info['nivel_acceso'] >= nivel_minimo

# =================================================================
# DECORADORES PRINCIPALES
# =================================================================

def requerir_autenticacion(func):
    """Decorador para requerir autenticación básica"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Verificar si el usuario está autenticado
        if not st.session_state.get('autenticado', False):
            st.error("❌ Debe iniciar sesión para acceder a esta función")
            st.stop()
            return None
        
        # Verificar si hay datos de usuario
        if 'user_data' not in st.session_state or not st.session_state['user_data']:
            st.error("❌ Sesión inválida. Por favor, inicie sesión nuevamente")
            st.session_state.clear()
            st.rerun()
            return None
        
        return func(*args, **kwargs)
    
    return wrapper

def requerir_rol(rol_permitido):
    """Decorador para requerir un rol específico"""
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Verificar autenticación primero
            if not st.session_state.get('autenticado', False):
                st.error("❌ Debe iniciar sesión para acceder a esta función")
                st.stop()
                return None
            
            # Verificar rol
            if not verificar_rol(st.session_state['user_data'], rol_permitido):
                st.error(f"❌ Acceso denegado. Se requiere rol '{rol_permitido}'")
                st.info(f"📋 Su rol actual: {st.session_state['user_data'].get('rol', 'Desconocido')}")
                st.stop()
                return None
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def requerir_permiso(permiso_requerido):
    """Decorador para requerir un permiso específico"""
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Verificar autenticación primero
            if not st.session_state.get('autenticado', False):
                st.error("❌ Debe iniciar sesión para acceder a esta función")
                st.stop()
                return None
            
            # Verificar permiso
            if not verificar_permiso(st.session_state['user_data'], permiso_requerido):
                st.error(f"❌ Acceso denegado. Se requiere el permiso '{permiso_requerido}'")
                st.info("📋 Contacte al administrador si necesita este permiso")
                st.stop()
                return None
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def requerir_permisos(permisos_requeridos):
    """Decorador para requerir múltiples permisos"""
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Verificar autenticación primero
            if not st.session_state.get('autenticado', False):
                st.error("❌ Debe iniciar sesión para acceder a esta función")
                st.stop()
                return None
            
            # Verificar permisos
            if not verificar_permisos(st.session_state['user_data'], permisos_requeridos):
                st.error(f"❌ Acceso denegado. Se requieren los permisos: {', '.join(permisos_requeridos)}")
                st.info("📋 Contacte al administrador si necesita estos permisos")
                st.stop()
                return None
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def requerir_nivel_acceso(nivel_minimo):
    """Decorador para requerir un nivel de acceso mínimo"""
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Verificar autenticación primero
            if not st.session_state.get('autenticado', False):
                st.error("❌ Debe iniciar sesión para acceder a esta función")
                st.stop()
                return None
            
            # Verificar nivel de acceso
            if not verificar_nivel_acceso(st.session_state['user_data'], nivel_minimo):
                st.error(f"❌ Acceso denegado. Se requiere nivel de acceso mínimo {nivel_minimo}")
                st.info(f"📋 Su nivel de acceso actual: {obtener_rol_usuario(st.session_state['user_data']['id'])['nivel_acceso'] if obtener_rol_usuario(st.session_state['user_data']['id']) else 'Desconocido'}")
                st.stop()
                return None
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

# =================================================================
# DECORADORES ESPECÍFICOS POR ROL
# =================================================================

def solo_administradores(func):
    """Decorador para funciones solo accesibles por administradores"""
    return requerir_rol('Administrador')(func)

def solo_profesores(func):
    """Decorador para funciones accesibles por profesores y administradores"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Verificar autenticación primero
        if not st.session_state.get('autenticado', False):
            st.error("❌ Debe iniciar sesión para acceder a esta función")
            st.stop()
            return None
        
        # Verificar rol (Profesor o Administrador)
        rol_actual = st.session_state['user_data'].get('rol', '').lower()
        
        if rol_actual not in ['profesor', 'administrador']:
            st.error("❌ Acceso denegado. Esta función es solo para profesores y administradores")
            st.info(f"📋 Su rol actual: {st.session_state['user_data'].get('rol', 'Desconocido')}")
            st.stop()
            return None
        
        return func(*args, **kwargs)
    
    return wrapper

def solo_estudiantes(func):
    """Decorador para funciones accesibles por estudiantes y administradores"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Verificar autenticación primero
        if not st.session_state.get('autenticado', False):
            st.error("❌ Debe iniciar sesión para acceder a esta función")
            st.stop()
            return None
        
        # Verificar rol (Estudiante o Administrador)
        rol_actual = st.session_state['user_data'].get('rol', '').lower()
        
        if rol_actual not in ['estudiante', 'administrador']:
            st.error("❌ Acceso denegado. Esta función es solo para estudiantes y administradores")
            st.info(f"📋 Su rol actual: {st.session_state['user_data'].get('rol', 'Desconocido')}")
            st.stop()
            return None
        
        return func(*args, **kwargs)
    
    return wrapper

# =================================================================
# DECORADORES DE MODULOS ESPECÍFICOS
# =================================================================

def acceso_gestion_usuarios(func):
    """Decorador para acceso a gestión de usuarios"""
    return requerir_permisos(['usuario.crear', 'usuario.editar', 'usuario.ver'])(func)

def acceso_gestion_cursos(func):
    """Decorador para acceso a gestión de cursos"""
    return requerir_permisos(['curso.crear', 'curso.editar', 'curso.ver'])(func)

def acceso_gestion_talleres(func):
    """Decorador para acceso a gestión de talleres"""
    return requerir_permisos(['taller.crear', 'taller.editar', 'taller.ver'])(func)

def acceso_auditoria(func):
    """Decorador para acceso a auditoría"""
    return requerir_permiso('auditoria.ver')(func)

def acceso_configuracion_sistema(func):
    """Decorador para acceso a configuración del sistema"""
    return requerir_permiso('sistema.configurar')(func)

# =================================================================
# FUNCIONES AUXILIARES
# =================================================================

def limpiar_cache_permisos():
    """Limpiar el cache de permisos"""
    global PERMISOS_CACHE
    PERMISOS_CACHE.clear()
    logger.info("🧹 Cache de permisos limpiado")

def obtener_info_permisos_usuario(usuario):
    """Obtener información detallada de permisos de un usuario"""
    
    if not usuario or 'id' not in usuario:
        return None
    
    rol_info = obtener_rol_usuario(usuario['id'])
    
    if not rol_info:
        return None
    
    return {
        'rol': rol_info['nombre_rol'],
        'nivel_acceso': rol_info['nivel_acceso'],
        'permisos': rol_info['permisos'],
        'modulos': rol_info['modulos'],
        'total_permisos': len(rol_info['permisos'])
    }

def mostrar_info_acceso():
    """Mostrar información de acceso del usuario actual en la interfaz"""
    
    if st.session_state.get('autenticado', False) and 'user_data' in st.session_state:
        usuario = st.session_state['user_data']
        permisos_info = obtener_info_permisos_usuario(usuario)
        
        if permisos_info:
            with st.sidebar:
                st.markdown("---")
                st.markdown("### 🔐 Información de Acceso")
                st.write(f"**Rol:** {permisos_info['rol']}")
                st.write(f"**Nivel:** {permisos_info['nivel_acceso']}")
                st.write(f"**Permisos:** {permisos_info['total_permisos']}")
                
                # Mostrar módulos accesibles
                if st.checkbox("📋 Ver módulos accesibles"):
                    st.write("**Módulos:**")
                    for modulo in sorted(permisos_info['modulos']):
                        st.write(f"  • {modulo.title()}")

# Decorador para registrar auditoría automáticamente
def registrar_auditoria(accion):
    """Decorador para registrar auditoría automáticamente"""
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Ejecutar función original
            resultado = func(*args, **kwargs)
            
            # Registrar auditoría
            if st.session_state.get('autenticado', False) and 'user_data' in st.session_state:
                try:
                    engine = get_engine_local()
                    with engine.connect() as conn:
                        conn.execute(text("""
                            INSERT INTO auditoria_roles (id_usuario, accion, tabla_afectada, fecha)
                            VALUES (:id_usuario, :accion, :tabla, :fecha)
                        """), {
                            'id_usuario': st.session_state['user_data']['id'],
                            'accion': accion,
                            'tabla': func.__name__,
                            'fecha': datetime.now()
                        })
                        conn.commit()
                except Exception as e:
                    logger.error(f"❌ Error registrando auditoría: {e}")
            
            return resultado
        
        return wrapper
    return decorator
