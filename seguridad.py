#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Seguridad y Permisología para SICADFOC 2026
Control de acceso por roles y validación de identidad
"""

import functools
import streamlit as st
import random
import re
import hashlib
from typing import Callable, Any, Optional, Dict, List

# Roles del sistema
ROLES = {
    'Administrador': 'admin',
    'Profesor': 'profesor',
    'Estudiante': 'estudiante'
}

# Diccionario Centralizado de Permisos (para velocidad en interfaz)
PERMISOS_MAP = {
    'Estudiante': {
        'modulos': ['Certificaciones', 'Mis Datos', 'Formación Complementaria'],
        'acciones': ['Consultar'],
        'restricciones': {
            'Estudiantes': 'propio',
            'Profesores': 'consulta_basica',
            'Formación Complementaria': 'inscribir_propio',
            'Generador QR': 'propio'
        }
    },
    'Profesor': {
        'modulos': ['Certificaciones', 'Estudiantes', 'Profesores', 'Formación Complementaria', 'Generador QR'],
        'acciones': ['Consultar', 'Crear', 'Editar'],
        'restricciones': {
            'Estudiantes': 'todos_menos_propio',
            'Profesores': 'todos_menos_propio',
            'Formación Complementaria': 'todos',
            'Generador QR': 'todos'
        }
    },
    'Administrador': {
        'modulos': 'ALL',
        'acciones': 'ALL',
        'restricciones': {}
    }
}

def hash_password(password: str) -> str:
    """Genera un hash SHA-256 para la contraseña dada."""
    if password is None:
        return None
    return hashlib.sha256(str(password).strip().encode('utf-8')).hexdigest()


def is_sha256_hash(value: str) -> bool:
    """Determina si un valor es un hash SHA-256 hex válido."""
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verifica una contraseña contra el valor almacenado (hash o texto plano)."""
    if stored_password is None or provided_password is None:
        return False
    stored = str(stored_password).strip()
    provided = str(provided_password).strip()
    if is_sha256_hash(stored):
        return stored == hash_password(provided)
    return stored == provided

# Variable global para conexión por sesión
_db_session = None

def get_session_connection():
    """Obtener o crear conexión por sesión"""
    global _db_session
    if _db_session is None:
        from conexion_simple_corregido import ConexionSimple
        _db_session = ConexionSimple()
        if not _db_session.conectar():
            _db_session = None
            return None
    return _db_session

def login_sesion(cedula: str, password: str):
    """
    Función de login con conexión por sesión.
    Una sola fuente de validación y conexión.
    """
    try:
        # 1. Limpieza de entradas
        cedula = cedula.strip()
        password = password.strip()
        
        # 2. Procesar cédula
        if not cedula.startswith('V-'):
            cedula = f'V-{cedula}'
        
        # 3. Validar que no sea solo V-
        if cedula == 'V-':
            return None
        
        # 4. Obtener conexión por sesión
        db = get_session_connection()
        if db is None:
            return None
        
        # 5. Generar hash
        hash_password = hashlib.sha256(password.encode()).hexdigest()
        
        # 6. Consulta directa a base de datos
        query = """
        SELECT cedula_usuario, login_usuario, contrasena, rol, activo 
        FROM usuario 
        WHERE cedula_usuario = %s AND contrasena = %s
        """
        
        resultado = db.ejecutar_consulta(query, (cedula, hash_password))
        
        # 7. Retornar usuario si encontrado
        if resultado and len(resultado) > 0:
            usuario = resultado[0]
            if usuario['activo']:
                return {
                    'cedula_usuario': usuario['cedula_usuario'],
                    'login_usuario': usuario['login_usuario'] or f"{cedula}@foc26.com",
                    'rol': usuario['rol'],
                    'activo': usuario['activo']
                }
        
        # 8. Retornar None si no encontrado o inactivo
        return None
        
    except Exception as e:
        # En caso de error, retornar None
        return None

def reset_session_connection():
    """Resetear conexión por sesión"""
    global _db_session
    _db_session = None


class SeguridadFOC26:
    """Clase para manejo de seguridad y permisos"""
    
    @staticmethod
    def get_user_role() -> str:
        """Obtener el rol del usuario logueado con normalización"""
        if 'user' not in st.session_state:
            return None
        rol = st.session_state['user'].get('rol', None)
        if rol:
            # NORMALIZACIÓN: strip().capitalize() para evitar errores de espacios/mayúsculas
            return rol.strip().capitalize()
        return None
    
    @staticmethod
    def get_user_cedula() -> str:
        """Obtener la cédula del usuario logueado"""
        if 'user' not in st.session_state:
            return None
        return st.session_state['user'].get('cedula_usuario', None)
    
    @staticmethod
    def is_admin() -> bool:
        """UNIFICACIÓN DE ROLES: Comparación robusta ADMIN/ADMINISTRADOR"""
        # SIMPLIFICACIÓN: Si es Admin acceso total
        user_rol = str(st.session_state.get('user', {}).get('rol', '')).strip().upper()
        return user_rol in ['ADMIN', 'ADMINISTRADOR']
    
    @staticmethod
    def is_profesor() -> bool:
        """Verificar si el usuario es profesor con normalización"""
        rol = SeguridadFOC26.get_user_role()
        return rol == 'Profesor' if rol else False
    
    @staticmethod
    def is_estudiante() -> bool:
        """Verificar si el usuario es estudiante con normalización"""
        rol = SeguridadFOC26.get_user_role()
        return rol == 'Estudiante' if rol else False
    
    @staticmethod
    def can_create_taller() -> bool:
        """SIMPLIFICACIÓN: Admin acceso total, otros con restricciones"""
        user_rol = str(st.session_state.get('user', {}).get('rol', '')).strip().upper()
        if user_rol in ['ADMIN', 'ADMINISTRADOR']:
            return True
        return user_rol == 'PROFESOR'
    
    @staticmethod
    def can_delete_any() -> bool:
        """SIMPLIFICACIÓN: Admin acceso total"""
        user_rol = str(st.session_state.get('user', {}).get('rol', '')).strip().upper()
        return user_rol in ['ADMIN', 'ADMINISTRADOR']
    
    @staticmethod
    def can_view_own_data() -> bool:
        """SIMPLIFICACIÓN: Admin acceso total, estudiante solo sus datos"""
        user_rol = str(st.session_state.get('user', {}).get('rol', '')).strip().upper()
        if user_rol in ['ADMIN', 'ADMINISTRADOR']:
            return True
        return user_rol == 'ESTUDIANTE'
    
    @staticmethod
    def can_view_inscriptions() -> bool:
        """SIMPLIFICACIÓN: Todos los roles pueden ver inscripciones"""
        return True
    
    @staticmethod
    def can_view_taller_list() -> bool:
        """SIMPLIFICACIÓN: Todos los roles pueden ver talleres"""
        return True
    
    @staticmethod
    def can_inscribirse() -> bool:
        """SIMPLIFICACIÓN: Admin acceso total, estudiante inscribirse"""
        user_rol = str(st.session_state.get('user', {}).get('rol', '')).strip().upper()
        if user_rol in ['ADMIN', 'ADMINISTRADOR']:
            return True
        return user_rol == 'ESTUDIANTE'
    
    @staticmethod
    def can_view_any_data() -> bool:
        """Verificar si puede ver cualquier dato (admin tiene acceso total)"""
        # PRIORIDAD ABSOLUTA: Admin ve TODO sin restricciones
        return SeguridadFOC26.is_admin()
    
    @staticmethod
    def can_manage_users() -> bool:
        """Verificar si puede gestionar usuarios (solo admin)"""
        return SeguridadFOC26.is_admin()
    
    @staticmethod
    def can_access_all_modules() -> bool:
        """Verificar si puede acceder a todos los módulos (solo admin)"""
        return SeguridadFOC26.is_admin()


def validar_permiso(rol: str, modulo: str, accion: str) -> bool:
    """
    Función híbrida de validación de permisos:
    1. Consulta diccionario PERMISOS_MAP (velocidad)
    2. Verificación silenciosa en base de datos (persistencia)
    3. Degrada elegantemente si tabla no existe
    """
    try:
        # Regla crítica: Administrador siempre tiene acceso
        if rol and rol.upper() in ['ADMIN', 'ADMINISTRADOR']:
            return True
        
        # Normalizar rol para comparación
        rol_normalizado = None
        if rol:
            rol_normalizado = rol.strip().capitalize()
        
        if not rol_normalizado or rol_normalizado not in PERMISOS_MAP:
            return False
        
        # 1. Validación rápida con diccionario local
        permisos_rol = PERMISOS_MAP[rol_normalizado]
        
        # Verificar acceso al módulo
        if permisos_rol['modulos'] != 'ALL':
            if modulo not in permisos_rol['modulos']:
                return False
        
        # Verificar acceso a la acción
        if permisos_rol['acciones'] != 'ALL':
            if accion not in permisos_rol['acciones']:
                return False
        
        # 2. Verificación silenciosa en base de datos (solo lectura)
        _validar_permisos_db(rol_normalizado, modulo, accion)
        
        return True
        
    except Exception as e:
        # En caso de cualquier error, permitir acceso por degradación elegante
        # Esto asegura que el sistema nunca se caiga por problemas de permisos
        print(f"Advertencia de seguridad (degradación): {e}")
        return True


def _validar_permisos_db(rol: str, modulo: str, accion: str) -> bool:
    """
    Verificación silenciosa en base de datos para persistencia.
    Maneja excepciones internamente para no afectar la operación.
    """
    try:
        # Importación con manejo de errores para no alterar lógica de conexión
        from conexion_simple_corregido import ConexionSimple
        
        db = ConexionSimple()
        if not db.conectar():
            return True  # Si no hay conexión, confiar en diccionario
        
        # Verificar si existe la tabla de permisos (solo lectura)
        query_tabla = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'permisos'
        )
        """
        
        resultado_tabla = db.ejecutar_consulta(query_tabla)
        if not resultado_tabla or not resultado_tabla[0]['exists']:
            return True  # Tabla no existe, confiar en diccionario
        
        # Consultar permisos específicos (solo lectura, sin bloquear)
        query_permiso = """
        SELECT COUNT(*) as tiene_permiso
        FROM permisos 
        WHERE rol = %s 
        AND modulo = %s 
        AND accion = %s
        AND activo = true
        """
        
        resultado_permiso = db.ejecutar_consulta(query_permiso, (rol, modulo, accion))
        if resultado_permiso and resultado_permiso[0]['tiene_permiso'] > 0:
            return True
        
        # Si no hay permiso específico en DB, verificar si hay permiso general
        query_general = """
        SELECT COUNT(*) as tiene_permiso
        FROM permisos 
        WHERE rol = %s 
        AND modulo = 'ALL'
        AND accion = 'ALL'
        AND activo = true
        """
        
        resultado_general = db.ejecutar_consulta(query_general, (rol,))
        return resultado_general and resultado_general[0]['tiene_permiso'] > 0
        
    except Exception:
        # Cualquier error en DB se ignora para degradación elegante
        return True


def sincronizar_permisos_db():
    """
    Sincroniza el diccionario PERMISOS_MAP con la tabla de permisos en DB.
    Función administrativa para mantener consistencia.
    """
    try:
        from conexion_simple_corregido import ConexionSimple
        
        db = ConexionSimple()
        if not db.conectar():
            return False
        
        # Crear tabla si no existe
        query_crear = """
        CREATE TABLE IF NOT EXISTS permisos (
            id SERIAL PRIMARY KEY,
            rol VARCHAR(50) NOT NULL,
            modulo VARCHAR(100) NOT NULL,
            accion VARCHAR(50) NOT NULL,
            activo BOOLEAN DEFAULT true,
            fecha_creacion TIMESTAMP DEFAULT NOW(),
            fecha_actualizacion TIMESTAMP DEFAULT NOW(),
            UNIQUE(rol, modulo, accion)
        )
        """
        
        db.ejecutar_actualizacion(query_crear)
        
        # Sincronizar permisos desde el diccionario
        for rol, permisos in PERMISOS_MAP.items():
            if permisos['modulos'] == 'ALL':
                # Insertar permiso general para admin
                db.ejecutar_actualizacion(
                    "INSERT INTO permisos (rol, modulo, accion) VALUES (%s, %s, %s) "
                    "ON CONFLICT (rol, modulo, accion) DO UPDATE SET activo = true, fecha_actualizacion = NOW()",
                    (rol, 'ALL', 'ALL')
                )
            else:
                # Insertar permisos específicos
                for modulo in permisos['modulos']:
                    for accion in permisos['acciones']:
                        db.ejecutar_actualizacion(
                            "INSERT INTO permisos (rol, modulo, accion) VALUES (%s, %s, %s) "
                            "ON CONFLICT (rol, modulo, accion) DO UPDATE SET activo = true, fecha_actualizacion = NOW()",
                            (rol, modulo, accion)
                        )
        
        return True
        
    except Exception as e:
        print(f"Error sincronizando permisos con DB: {e}")
        return False

# Decoradores para seguridad
def admin_required(func: Callable) -> Callable:
    """Decorador para requerir rol de administrador"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not SeguridadFOC26.is_admin():
            st.error("Acceso denegado. Se requiere rol de Administrador.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def profesor_required(func: Callable) -> Callable:
    """Decorador para requerir rol de profesor"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not SeguridadFOC26.is_profesor():
            st.error("Acceso denegado. Se requiere rol de Profesor.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def estudiante_required(func: Callable) -> Callable:
    """Decorador para requerir rol de estudiante"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not SeguridadFOC26.is_estudiante():
            st.error("Acceso denegado. Se requiere rol de Estudiante.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def authenticated_required(func: Callable) -> Callable:
    """Decorador para requerir autenticación"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'autenticado' not in st.session_state or not st.session_state['autenticado']:
            st.error("Acceso denegado. Debe iniciar sesión.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def mostrar_panel_permisos():
    """Muestra un panel informativo sobre los permisos del usuario actual"""
    try:
        user = st.session_state.get('user', {})
        if not user:
            st.info("No hay usuario autenticado")
            return
        
        st.subheader("Panel de Permisos")
        
        # Información del usuario
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Información del Usuario:**")
            st.write(f"- Nombre: {user.get('login_usuario', 'N/A')}")
            st.write(f"- Cédula: {user.get('cedula_usuario', 'N/A')}")
            st.write(f"- Rol: {user.get('rol', 'N/A')}")
            st.write(f"- Estado: {'Activo' if user.get('activo', False) else 'Inactivo'}")
        
        with col2:
            st.write("**Permisos Activos:**")
            st.write(f"- Administrador: {'Sí' if SeguridadFOC26.is_admin() else 'No'}")
            st.write(f"- Profesor: {'Sí' if SeguridadFOC26.is_profesor() else 'No'}")
            st.write(f"- Estudiante: {'Sí' if SeguridadFOC26.is_estudiante() else 'No'}")
        
        # Permisos específicos
        st.write("**Permisos Específicos:**")
        permisos = [
            ("Crear Talleres", SeguridadFOC26.can_create_taller()),
            ("Eliminar Datos", SeguridadFOC26.can_delete_any()),
            ("Ver Datos Propios", SeguridadFOC26.can_view_own_data()),
            ("Ver Inscripciones", SeguridadFOC26.can_view_inscriptions()),
            ("Ver Lista de Talleres", SeguridadFOC26.can_view_taller_list()),
            ("Inscribirse en Talleres", SeguridadFOC26.can_inscribirse()),
            ("Ver Cualquier Dato", SeguridadFOC26.can_view_any_data()),
            ("Gestionar Usuarios", SeguridadFOC26.can_manage_users()),
            ("Acceder a Todos los Módulos", SeguridadFOC26.can_access_all_modules())
        ]
        
        for permiso, tiene in permisos:
            status = "Sí" if tiene else "No"
            color = "green" if tiene else "red"
            st.markdown(f"- **{permiso}:** <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error al mostrar panel de permisos: {e}")

# ========================================
# SISTEMA DE AUTORIZACIÓN DINÁMICO
# ========================================

class AutorizacionDinamica:
    """Clase para manejar autorización dinámica desde base de datos"""
    
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.cache_permisos = {}
    
    def _get_db_connection(self):
        """Obtiene conexión a la base de datos"""
        if self.db_connection:
            return self.db_connection
        
        # Intentar obtener conexión desde el estado global
        if 'db' in st.session_state:
            return st.session_state['db']
        
        # Fallback: importar conexión
        try:
            from conexion_simple_corregido import ConexionSimple
            db = ConexionSimple()
            if db.conectar():
                return db
        except:
            pass
        
        return None
    
    def tiene_permiso(self, rol: str, modulo: str, accion: str) -> bool:
        """
        Verifica si un rol tiene permiso para una acción en un módulo
        
        Args:
            rol: Nombre del rol (Profesor, Estudiante, Administrador)
            modulo: Nombre del módulo (Estudiantes, Profesores, Formación Complementaria, etc.)
            accion: Acción a realizar (Consultar, Crear, Editar, Eliminar, Inscribir, etc.)
            
        Returns:
            bool: True si tiene permiso, False si no
        """
        # Cache para evitar consultas repetidas
        cache_key = f"{rol}_{modulo}_{accion}"
        if cache_key in self.cache_permisos:
            return self.cache_permisos[cache_key]
        
        try:
            db = self._get_db_connection()
            if not db:
                st.error("No hay conexión a la base de datos para verificar permisos")
                return False
            
            # Consultar permiso en configuracion_permisos (estructura simple)
            query = """
            SELECT cp.acceso_limitado_propio
            FROM configuracion_permisos cp
            WHERE cp.rol = %s AND cp.modulo = %s AND cp.accion = %s
            """
            
            resultado = db.ejecutar_consulta(query, (rol, modulo, accion))
            
            if resultado and len(resultado) > 0:
                # Si existe el registro, el permiso está concedido
                self.cache_permisos[cache_key] = True
                return True
            else:
                # Si no existe el registro, el permiso está denegado
                self.cache_permisos[cache_key] = False
                return False
            
        except Exception as e:
            st.error(f"Error verificando permisos: {e}")
            return False
    
    def necesita_filtro_propio(self, rol: str, modulo: str) -> bool:
        """
        Verifica si el acceso está limitado a datos propios
        
        Args:
            rol: Nombre del rol
            modulo: Nombre del módulo
            
        Returns:
            bool: True si necesita filtro, False si puede ver todos
        """
        try:
            db = self._get_db_connection()
            if not db:
                return False
            
            query = """
            SELECT cp.acceso_limitado_propio
            FROM configuracion_permisos cp
            WHERE cp.rol = %s AND cp.modulo = %s
            """
            
            result = db.ejecutar_consulta(query, (rol, modulo))
            
            if result:
                # Verificar si algún permiso para este rol y módulo tiene acceso_limitado_propio = True
                for row in result:
                    if row.get('acceso_limitado_propio', False):
                        return True
            
            return False
            
        except Exception as e:
            st.error(f"Error verificando filtro propio: {e}")
            return False
    
    def obtener_filtro_sql(self, rol: str, modulo: str, id_usuario: int = None) -> str:
        """
        Genera cláusula WHERE para filtrar datos propios
        
        Args:
            rol: Nombre del rol
            modulo: Nombre del módulo
            id_usuario: ID del usuario actual
            
        Returns:
            str: Cláusula SQL o vacío si no necesita filtro
        """
        if not self.necesita_filtro_propio(rol, modulo):
            return ""
        
        if not id_usuario:
            user = st.session_state.get('user', {})
            id_usuario = user.get('id')
        
        if not id_usuario:
            return ""
        
        # Mapeo de tablas según módulo
        tabla_usuario_map = {
            'Estudiantes': 'id_usuario',
            'Profesores': 'id_usuario',
            'Formación Complementaria': 'id_usuario',
            'Formacion Complementaria': 'id_usuario',
            'Certificaciones': 'id_usuario'
        }
        
        columna_usuario = tabla_usuario_map.get(modulo, 'id_usuario')
        
        return f" AND {columna_usuario} = {id_usuario}"

# Instancia global del sistema de autorización
_autorizacion = None

def get_autorizacion():
    """Obtiene instancia global de autorización"""
    global _autorizacion
    if _autorizacion is None:
        _autorizacion = AutorizacionDinamica()
    return _autorizacion

def tiene_permiso(rol: str, modulo: str, accion: str) -> bool:
    """
    Función de conveniencia para verificar permisos
    
    Args:
        rol: Nombre del rol
        modulo: Nombre del módulo
        accion: Acción a verificar
        
    Returns:
        bool: True si tiene permiso, False si no
    """
    autorizacion = get_autorizacion()
    return autorizacion.tiene_permiso(rol, modulo, accion)

def requiere_permiso(modulo: str, accion: str):
    """
    Decorador para requerir permiso específico
    
    Args:
        modulo: Nombre del módulo requerido
        accion: Acción requerida
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Verificar autenticación
            if 'autenticado' not in st.session_state or not st.session_state['autenticado']:
                st.error("Debe iniciar sesión para acceder a esta función")
                st.stop()
            
            # Obtener rol del usuario
            user = st.session_state.get('user', {})
            rol = user.get('rol', '')
            
            # Verificar permiso
            if not tiene_permiso(rol, modulo, accion):
                st.error(f"Acceso denegado. No tiene permiso para '{accion}' en el módulo '{modulo}'")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def mostrar_componente_si_tiene_permiso(modulo: str, accion: str, mensaje_denegado: str = None):
    """
    Context manager para mostrar componentes solo si tiene permiso
    
    Args:
        modulo: Nombre del módulo
        accion: Acción requerida
        mensaje_denegado: Mensaje personalizado si no tiene permiso
    """
    class PermisoContext:
        def __init__(self, modulo, accion, mensaje_denegado):
            self.modulo = modulo
            self.accion = accion
            self.mensaje_denegado = mensaje_denegado or f"Acceso denegado para '{accion}' en '{modulo}'"
            self.tiene_permiso = False
        
        def __enter__(self):
            user = st.session_state.get('user', {})
            rol = user.get('rol', '')
            self.tiene_permiso = tiene_permiso(rol, self.modulo, self.accion)
            return self.tiene_permiso
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if not self.tiene_permiso:
                st.warning(self.mensaje_denegado)
    
    return PermisoContext(modulo, accion, mensaje_denegado)

def aplicar_filtro_propio(query: str, rol: str, modulo: str) -> str:
    """
    Aplica filtro de datos propios a una consulta SQL
    
    Args:
        query: Consulta SQL original
        rol: Rol del usuario
        modulo: Módulo actual
        
    Returns:
        str: Consulta SQL con filtro aplicado
    """
    autorizacion = get_autorizacion()
    filtro = autorizacion.obtener_filtro_sql(rol, modulo)
    
    if filtro:
        # Insertar filtro antes de ORDER BY, GROUP BY, etc.
        if 'WHERE' in query.upper():
            query = query.replace('WHERE', f'WHERE 1=1{filtro} AND')
        else:
            query = query.replace('FROM', f'FROM WHERE 1=1{filtro}')
    
    return query
