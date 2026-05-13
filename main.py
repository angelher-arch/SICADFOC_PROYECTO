# -*- coding: utf-8 -*-
"""
main.py - Sistema de Informacion de Control Academico de Formacion Complementaria
Instituto Universitario Jesus Obrero
Version 3.0 - Arquitectura Unificada Local/Nube
"""

import streamlit as st  # type: ignore
import logging
import sys
import datetime
import locale
import os

# PRIMER COMANDO STREAMLIT - Configuración de página (DEBE SER EL PRIMERO)
st.set_page_config(
    page_title="SICADFOC 2026 - IUJO",
    page_icon="IUJO",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def apply_background_css():
    """Aplicar CSS de fondo IUJO desde archivo estático persistente"""
    st.markdown(
        '<link rel="stylesheet" type="text/css" href="/static/styles.css">',
        unsafe_allow_html=True
    )

# Aplicar fondo al inicio
apply_background_css()

# FORZAR UTF-8 EN TODA LA APLICACIÓN
if sys.platform.startswith('win'):
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
    except:
        pass

# FORZAR UTF-8 EN TODA LA APLICACIÓN

def asegurar_estructura_bd():
    """Función de autoreparación de base de datos - optimizada para producción"""
    try:
        # 1. Importar y verificar configuración
        from database import DatabaseManager
        db_manager = DatabaseManager()
        
        # 2. Verificar si tabla usuarios existe
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT 1 FROM public.usuarios LIMIT 1")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            cursor.close()
            # Tabla no encontrada, intentar reparación silenciosa
            pass
        
        # 3. Ejecutar script de sincronización si existe
        script_path = os.path.join(os.path.dirname(__file__), 'sincronizacion_tablas.sql')
        
        if os.path.exists(script_path):
            try:
                # Leer y ejecutar script línea por línea
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    statements = [stmt.strip() for stmt in content.split(';') if stmt.strip()]
                
                for statement in statements:
                    try:
                        cursor.execute(statement)
                    except Exception:
                        # Continuar con la siguiente sentencia
                        pass
                
                conn.commit()
                
                # 4. Verificar post-reparación
                cursor.execute("SELECT 1 FROM public.usuarios LIMIT 1")
                cursor.close()
                conn.close()
                
                return True
                
            except Exception:
                pass
        else:
            conn.close()
        
        return False
        
    except Exception:
        return False

# EJECUTAR AUTOREPARACIÓN ANTES DE CARGAR MÓDULOS
# Verificando estructura de base de datos al iniciar
reparacion_exitosa = asegurar_estructura_bd()
if not reparacion_exitosa:
    pass  # Advertencia: La autoreparación falló
else:
    pass  # Estructura de base de datos verificada y reparada si fue necesario

# LIMPIEZA DE CACHÉ - MODO DE SEGURIDAD
st.cache_resource.clear()
st.cache_data.clear()

# LIMPIEZA EN CAMBIO DE MÓDULO - RESET EXPLÍCITO
if 'modulo_anterior' in st.session_state and st.session_state.modulo_anterior != st.session_state.get('modulo_actual', ''):
    # Cambio de módulo detectado
    
    # Cerrar todas las conexiones forzosamente
    try:
        from database import close_database
        close_database()
        # Conexiones forzadamente cerradas al cambiar de módulo
    except Exception as e:
        pass  # Error cerrando conexiones
    
    # Limpiar variables de estado relacionadas con BD
    keys_to_clean = [key for key in st.session_state.keys() 
                     if any(term in key.lower() for term in ['db', 'connection', 'usuario', 'modulo', 'transaccion'])]
    
    for key in keys_to_clean:
        del st.session_state[key]
    
    pass  # Limpieza por cambio de módulo completada
    
    # Actualizar módulo anterior
    st.session_state.modulo_anterior = st.session_state.get('modulo_actual', '')

# DETECCIÓN DE TRANSACCIÓN ABORTADA - RESET DE EMERGENCIA
if 'transaccion_abortada' in st.session_state:
    # Alerta transacción abortada - ejecutando reset total
    # Limpiar estado de transacción
    del st.session_state.transaccion_abortada
    
    # Limpiar variables de conexión
    keys_to_clean = [key for key in st.session_state.keys() 
                     if any(term in key.lower() for term in ['db', 'connection', 'usuario', 'modulo'])]
    
    for key in keys_to_clean:
        del st.session_state[key]
    
    # Limpieza por transacción abortada completada
    
    # Forzar reconexión en siguiente interacción
    st.session_state.forzar_reconexion = True

# st.set_page_config() movido al inicio del archivo - línea 15

import os
import hashlib
import sys

# Configurar logging para validación de emergencia
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
import random
import re
from datetime import datetime

# Forzar UTF-8 a nivel del sistema
if sys.version_info[0] >= 3:
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'Spanish_Spain.1252')
        except:
            pass

# Importar database.py como Single Source of Truth
from database import (
    get_db_session, 
    authenticate_user, 
    get_database_info, 
    close_database, 
    ensure_admin_exists, 
    DatabaseManager,
    db_manager
)
from gestion_permisos import mostrar_gestion_permisos
from gestion_carreras import mostrar_gestion_carreras, precargar_carreras_iniciales

# Ejecutar ensure_admin_exists() al inicio para garantizar administradores
try:
    ensure_admin_exists()
    pass  # Administradores verificados/creados
except Exception as e:
    pass  # Error verificando administradores

# Precargar carreras iniciales si no existen
try:
    precargar_carreras_iniciales()
    pass  # Carreras iniciales verificadas/precargadas
except Exception as e:
    pass  # Error precargando carreras

def normalizar_cedula(cedula_str):
    """
    Normaliza un número de identificación (cédula) venezolana.
    
    Reglas:
    - Limpieza: Elimina puntos, espacios y caracteres especiales innecesarios.
    - Si solo números, añade 'V-'.
    - Si 'v' o 'V' seguidas de números (con o sin guion), convierte a 'V-'.
    - Formato final: V-12345678
    - Si inválido, retorna mensaje de error.
    """
    import re
    
    # Limpiar: quitar puntos, espacios, y caracteres no alfanuméricos excepto guiones
    cedula_str = re.sub(r'[^\w-]', '', cedula_str)
    
    # Ahora, verificar
    if cedula_str.isdigit():
        return f'V-{cedula_str}'
    elif re.match(r'^[vV]-?\d+$', cedula_str):
        # Extraer números
        numero = re.sub(r'[^0-9]', '', cedula_str)
        return f'V-{numero}'
    else:
        return "Formato inválido. Por favor, ingresa una cédula válida (solo números o V- seguido de números)."

def gestion_permisos():
    """Módulo de Gestión de Permisos - Solo para Administradores"""
    apply_background_css()  # Aplicar fondo persistente
    # Usar el nuevo módulo de gestión de permisos
    mostrar_gestion_permisos()
    
    try:
        from database import get_db_session
        from psycopg2.extras import RealDictCursor
        
        # Obtener conexión directa para mayor control
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="db_foc26",
            user="postgres",
            password="admin123",
            connect_timeout=10,
            options='-c client_encoding=UTF8 -c search_path=public'
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Obtener todos los usuarios
        cursor.execute("""
            SELECT u.cedula_usuario, u.login_usuario, u.rol, u.activo,
                   p.nombre, p.apellido, u.modulos_permitidos
            FROM public.usuarios u
            LEFT JOIN persona p ON u.cedula_usuario = p.cedula
            ORDER BY u.rol, p.apellido, p.nombre
        """)
        usuarios = cursor.fetchall()
        
        if not usuarios:
            st.warning("No hay usuarios registrados en el sistema")
            return
        
        # Módulos disponibles para asignar
        modulos_disponibles = [
            "Configuracion",
            "Gestion Estudiantil", 
            "Reportes",
            "Formacion Complementaria",
            "Registro Estudiantes",
            "Registro Profesores",
            "Gestion Profesores",
            "Historial Estudiantil",
            "Gestion Carreras"
        ]
        
        st.markdown("#### Lista de Usuarios y Permisos")
        
        # Formulario para actualizar permisos
        with st.form("form_permisos"):
            st.markdown("**Seleccione los módulos a los que cada usuario puede acceder:**")
            
            # Para cada usuario, crear checkboxes para módulos
            permisos_actualizados = {}
            
            for usuario in usuarios:
                st.markdown(f"**{usuario['nombre']} {usuario['apellido']}** ({usuario['rol']})")
                st.caption(f"Cédula: {usuario['cedula_usuario']} - Estado: {'Activo' if usuario['activo'] else 'Inactivo'}")
                
                # Obtener permisos actuales del usuario
                permisos_actuales = usuario.get('modulos_permitidos', '')
                permisos_lista = permisos_actuales.split(',') if permisos_actuales else []
                
                # Checkboxes para cada módulo
                seleccionados = []
                cols = st.columns(4)
                for i, modulo in enumerate(modulos_disponibles):
                    with cols[i % 4]:
                        checked = modulo in permisos_lista
                        if st.checkbox(modulo, key=f"perm_{usuario['cedula_usuario']}_{modulo}", value=checked):
                            seleccionados.append(modulo)
                
                # Guardar permisos seleccionados
                permisos_actualizados[usuario['cedula_usuario']] = ','.join(seleccionados)
                st.markdown("---")
            
            # Botón de actualización
            if st.form_submit_button("Actualizar Permisos", type="primary"):
                try:
                    # Actualizar permisos en la base de datos
                    for cedula, modulos in permisos_actualizados.items():
                        cursor.execute("""
                            UPDATE public.usuarios 
                            SET modulos_permitidos = %s 
                            WHERE cedula_usuario = %s
                        """, (modulos, cedula))
                    
                    conn.commit()
                    st.success("Permisos actualizados exitosamente")
                    st.rerun()
                    
                except Exception as e:
                    conn.rollback()
                    st.error(f"Error actualizando permisos: {e}")
        
        # Mostrar resumen actual
        st.markdown("#### Resumen de Permisos Actuales")
        
        cursor.execute("""
            SELECT rol, COUNT(*) as total_usuarios
            FROM public.usuarios
            GROUP BY rol
            ORDER BY rol
        """)
        resumen_roles = cursor.fetchall()
        
        if resumen_roles:
            col1, col2, col3 = st.columns(3)
            for i, rol_info in enumerate(resumen_roles):
                with [col1, col2, col3][i % 3]:
                    st.metric(
                        f"Usuarios {rol_info['rol']}", 
                        rol_info['total_usuarios']
                    )
        
        conn.close()
        
    except Exception as e:
        st.error(f"Error en el módulo de gestión de permisos: {e}")
        import traceback
        traceback.print_exc()

def validar_esquema_principal():
    """Valida que las tablas principales existan antes de permitir operaciones"""
    apply_background_css()  # Aplicar fondo persistente
    try:
        # Obtener manager y ejecutar test de conexión
        db_manager = DatabaseManager()
        test_result = db_manager.test_connection()
        
        if not test_result['status']:
            st.error(f"❌ Error de conexión a la base de datos")
            st.error("Por favor contacte al administrador del sistema")
            st.stop()
            return False
        
        # Verificar tablas críticas
        db_info = test_result.get('database_info', {})
        usuarios_existe = db_info.get('usuarios_table_exists', False)
        estudiante_existe = db_info.get('estudiante_table_exists', False)
        
        if not usuarios_existe:
            st.error("❌ Error en la configuracion del sistema")
            st.error("Por favor contacte al administrador")
            st.stop()
            return False
        
        if not estudiante_existe:
            st.error("❌ Error en la configuracion del sistema")
            st.error("Por favor contacte al administrador")
            st.stop()
            return False
        
        # Esquema validado - sistema operativo
        return True
        
    except Exception as e:
        st.error("❌ Error del sistema")
        st.error("Por favor contacte al administrador")
        st.stop()
        return False

# IMPORTACIONES DE MÓDULOS PRINCIPALES
try:
    from auth_unificado import AuthSystemUnificado, gestion_usuarios_main, registro_usuario_main
    from seguridad import tiene_permiso, SeguridadFOC26
    from gestion_estudiantil import gestion_estudiantil_main
    from gestion_profesores import gestion_profesores_main
    from formacion_complementaria import modulo_formacion_complementaria
    from inscripciones_unificadas import inscripciones_unificadas_main
    from gestion_inscripciones_facilitador import gestion_inscripciones_facilitador_main
    from gestor_certificaciones import gestor_certificaciones_unificado
    from editor_certificados import editor_certificados_main
    from reportes import reportes
    from gestion_permisos import gestion_permisos
    from gestion_carreras import gestion_carreras
    from gestion_solicitudes import gestion_solicitudes_main
    from formacion_extemporanea import formacion_extemporanea_main
    from configuracion import configuracion_main
    
except ImportError as e:
    st.error(f"Error al cargar el sistema: {e}")
    st.error("Por favor contacte al administrador")
    sys.exit(1)

# Forzar UTF-8 en variables de entorno
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LC_ALL'] = 'C.UTF-8'
os.environ['LANG'] = 'C.UTF-8'

def limpiar_estado_modulo_anterior():
    """Limpiar estado de sesión al cambiar de módulo para evitar conflictos"""
    # Limpiar variables de sesión específicas de módulos
    keys_to_remove = [
        'resultados_busqueda_estudiante',
        'estudiante_seleccionado',
        'csv_estudiantes',
        'profesor_seleccionado',
        'taller_seleccionado',
        'certificado_seleccionado',
        'qr_data',
        'informe_filtro',
        'configuracion_temporal'
    ]
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    
    # Limpiar mensajes de error o éxito temporales
    if 'temp_messages' in st.session_state:
        del st.session_state['temp_messages']

# Variables globales para estado
db_connection = None
db_connected = False
db_error = None
debug_mode = os.getenv('DEBUG_MODE', 'False').lower() in ('1', 'true', 'yes')

def hash_password(password):
    """Hash de contraseña simple"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def limpiar_sesion_db():
    """Limpia solo el estado específico al cambiar de módulo (optimizado para rendimiento)"""
    try:
        # NO limpiar cachés de Streamlit para mantener conexiones cacheadas
        # Solo limpiar estado específico de módulos
        
        # Eliminar variables de sesión específicas de módulos
        keys_to_remove = []
        for key in st.session_state.keys():
            if any(temp_key in key.lower() for temp_key in ['resultado', 'busqueda', 'seleccionado', 'temporal']):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del st.session_state[key]
        
        pass  # Limpieza de sesión DB completada
        
    except Exception as e:
        pass  # Error en limpieza de sesión DB

def conectar_foc26db():
    """Conexión centralizada a la base de datos usando db_manager.py"""
    global db_connection, db_connected, db_error
    
    try:
        if debug_mode:
            st.write("=== MODO DEBUG: CONEXIÓN A FOC26DB ===")
            st.write(f"Timestamp: {datetime.datetime.now().isoformat()}")
            st.write(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
        
        # Usar database.py como Single Source of Truth
        from database import db_manager
        db_connection = db_manager.get_connection()
        
        if db_connection:
            db_connected = True
            db_error = None
            if debug_mode:
                st.success("Conexión exitosa a FOC26DB")
            return True
        else:
            db_connected = False
            db_error = "No se pudo establecer conexión"
            if debug_mode:
                st.error("Error de conexión a FOC26DB")
            return False
            
    except Exception as e:
        db_connected = False
        db_error = str(e)
        if debug_mode:
            st.error(f"Error crítico de conexión: {e}")
        return False

def verificar_usuario(usuario_input, clave_input):
    """Autenticación segura usando database.py con 4 capas de seguridad y homologación de cédulas"""
    try:
        # Importar el nuevo database y utilidades de homologación
        from database import authenticate_user
        from utils_homologacion import homologar_cedula
        
        # Capturar el valor ingresado en el formulario
        cedula_limpia = usuario_input.strip()
        
        # Usar autenticación segura con database.py (incluye homologación interna)
        resultado_auth = authenticate_user(cedula_limpia, clave_input)

        if resultado_auth and resultado_auth.get('success', False):
            # Construir resultado compatible con formato esperado
            resultado = {
                'success': True,
                'data': {
                    'cedula_usuario': resultado_auth['user']['cedula_usuario'],
                    'nombre_usuario': resultado_auth['user']['login_usuario'],
                    'rol': resultado_auth['user']['rol'],
                    'rol_id': 1 if resultado_auth['user']['rol'] == 'Administrador' else 2,
                    'es_superusuario': resultado_auth['user']['rol'] == 'Administrador'
                },
                'message': 'Autenticación exitosa'
            }
        else:
            resultado = {
                'success': False,
                'message': (resultado_auth or {}).get('message', 'Usuario o contraseña incorrectos')
            }
        
        if resultado['success']:
            usuario_data = resultado['data']
            
                        
            return {
                'rol': resultado['data']['rol'], 
                'login': resultado['data']['nombre_usuario'],
                'cedula': resultado['data']['cedula_usuario'],
                'es_superusuario': resultado['data']['es_superusuario']
            }
        else:
            return None
            
    except Exception as e:
        print(f"LOGIN_DEBUG_ERROR_AUTH: {e}")
        import traceback
        traceback.print_exc()
        st.error("Error de autenticación. Contacte al administrador.")
        return None

def main():
    """Función principal unificada para local y nube"""
    
    # st.set_page_config() eliminado - ya está configurado al inicio del archivo
    
    # Aplicar estilos dinámicos globales
    try:
        from styles import aplicar_estilos_sicad
        aplicar_estilos_sicad()
    except ImportError:
        # CSS de respaldo si styles.py no está disponible
        st.markdown("""
        <style>
            .main-header {
                background: linear-gradient(90deg, #1e3c72, #2a5298);
                color: white;
                padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }
        .module-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 10px 0;
        }
        .error-message {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #c62828;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1> Sistema de Información de Control Académico </h1>
        <h2> Formación Complementaria - IUJO </h2>
        <h3> SICADFOC 2026 </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Lógica de autenticación
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_cedula = None
        st.session_state.cedula = None
    
    # Login o contenido principal
    if not st.session_state.logged_in:
        st.markdown("### Iniciar Sesión")
        
        # Crear tabs para Login y Registro
        tab_login, tab_registro = st.tabs(["Iniciar Sesión", "Registrar Usuario"])
        
        # Tab de Iniciar Sesión
        with tab_login:
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                with st.form("login_form"):
                    st.markdown("#### Acceso al Sistema")
                    
                    usuario = st.text_input("Cédula o Usuario", placeholder="Ej: V-12345678")
                    clave = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
                    
                    submit_button = st.form_submit_button("Iniciar Sesión", use_container_width=True)
                    
                    if submit_button:
                        if not usuario or not clave:
                            st.error("Por favor ingrese usuario y contraseña")
                        else:
                            try:
                                # Verificar usuario
                                resultado = verificar_usuario(usuario, clave)
                                
                                if resultado:
                                    # Validar que todos los campos necesarios existan antes de actualizar sesión
                                    if all(key in resultado for key in ['rol', 'login', 'cedula']):
                                        st.session_state.logged_in = True
                                        st.session_state.user_role = resultado['rol']
                                        st.session_state.user_cedula = resultado['cedula']
                                        st.session_state.cedula = resultado['cedula']
                                        st.session_state.es_superusuario = resultado.get('es_superusuario', False)
                                        # Agregar información completa de usuario para configuracion
                                        st.session_state.user = {
                                            'rol': resultado['rol'],
                                            'cedula_usuario': resultado['cedula'],
                                            'login_usuario': resultado['login'],
                                            'es_superusuario': resultado.get('es_superusuario', False),
                                            'rol_descripcion': resultado.get('rol_descripcion', '')
                                        }
                                        print(f"LOGIN_DEBUG: Sesión actualizada correctamente para {resultado['login']}")
                                        st.rerun()
                                    else:
                                        print(f"LOGIN_DEBUG_ERROR: Campos faltantes en resultado: {resultado.keys()}")
                                        st.error("Error en la validación del usuario")
                                else:
                                    st.error("Usuario o contraseña incorrectos")
                                    
                            except Exception as e:
                                print(f"LOGIN_DEBUG_ERROR: {e}")
                                import traceback
                                traceback.print_exc()
                                st.error("Error en el proceso de login")
        
        # Tab de Registrar Usuario
        with tab_registro:
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown("#### Registro de Nuevo Usuario")
                
                # Verificar conexión antes de permitir registro
                connection_ok = False
                try:
                    print("DEBUG_REGISTRO: Iniciando verificación de conexión...")
                    from database import test_database_connection
                    result = test_database_connection()
                    print(f"DEBUG_REGISTRO: Resultado de test_connection: {result}")
                    connection_ok = result and result.get('status', False)
                    print(f"DEBUG_REGISTRO: Conexión verificada - Status: {connection_ok}")
                    print(f"DEBUG_REGISTRO: Mensaje: {result.get('message', 'No message') if result else 'No result'}")
                except Exception as e:
                    print(f"DEBUG_REGISTRO_ERROR: Error verificando conexión - {e}")
                    import traceback
                    print(f"DEBUG_REGISTRO_ERROR: Traceback: {traceback.format_exc()}")
                    connection_ok = False
                
                # Solo permitir registro si hay conexión
                if connection_ok:
                    # Mostrar formulario de registro
                    print("DEBUG_REGISTRO: Llamando a registro_usuario_main()...")
                    registro_usuario_main()
                    print("DEBUG_REGISTRO: registro_usuario_main() completado")
                else:
                    st.error("No se puede registrar usuarios sin conexión a la base de datos")
        
            
    else:
        # Usuario autenticado - mostrar sidebar con módulos y contenido principal
        with st.sidebar:
            # Información del usuario actual
            if st.session_state.get('logged_in', False):
                user_info = st.session_state.get('user', {})
                st.markdown(f"### {user_info.get('login_usuario', 'Usuario')}")
                st.caption(f"Rol: {st.session_state.get('user_role', 'N/A')}")
                print(f"DEBUG_LOGIN: Usuario logueado - {user_info.get('login_usuario', 'Usuario')} - Rol: {st.session_state.get('user_role', 'N/A')}")
            else:
                st.markdown("### Sistema")
                print("DEBUG_LOGIN: No hay usuario logueado")
            
            # Verificar conexión de forma silenciosa
            connection_ok = False
            try:
                from database import test_database_connection
                result = test_database_connection()
                connection_ok = result and result.get('status', False)
                
                # Si BD desconectada y usuario logueado, cerrar sesión silenciosamente
                if not connection_ok and st.session_state.get('logged_in', True):
                    st.session_state.logged_in = False
                    st.session_state.user_role = None
                    st.session_state.user_cedula = None
                    st.session_state.cedula = None
                    st.session_state.es_superusuario = False
                    st.session_state.user = None
                    st.rerun()
                    
            except Exception as e:
                connection_ok = False
            
            # Botón de reconexión solo si es necesario
            if not connection_ok:
                if st.button("Reconectar", type="primary", use_container_width=True):
                    try:
                        st.cache_resource.clear()
                        st.cache_data.clear()
                        
                        # Intentar reconexión con database.py
                        from database import DatabaseManager
                        db_manager = DatabaseManager()
                        connection_status = db_manager.test_connection()
                        
                        if connection_status.get('status', False):
                            st.success("Conexión restablecida exitosamente")
                            st.rerun()
                        else:
                            st.error("No se pudo restablecer la conexión")
                    except Exception as e:
                        st.error(f"Error al reconectar: {e}")
            st.markdown("### Módulos del Sistema")
            
            # Navegación por módulos con botones (sin dependencia de BD)
            
            # Navegación por módulos - botones limpios (botones de registro eliminados para unificar)
            
            if st.button("Gestión Estudiantil", key="btn_gestion_estudiantil", use_container_width=True):
                limpiar_estado_modulo_anterior()
                limpiar_sesion_db()
                st.session_state.modulo_actual = "Gestión Estudiantil"
                st.rerun()
            
            if st.button("Gestión Profesores", key="btn_gestion_profesores", use_container_width=True):
                limpiar_estado_modulo_anterior()
                limpiar_sesion_db()
                st.session_state.modulo_actual = "Gestión Profesores"
                st.rerun()
            
            if st.button("Formación Complementaria", key="btn_formacion", use_container_width=True):
                limpiar_estado_modulo_anterior()
                limpiar_sesion_db()
                st.session_state.modulo_actual = "Formación Complementaria"
                st.rerun()
            
            
            if st.button("Inscripciones", key="btn_inscripciones", use_container_width=True):
                limpiar_estado_modulo_anterior()
                limpiar_sesion_db()
                st.session_state.modulo_actual = "Inscripciones Unificadas"
                st.rerun()
            
            # Módulo para Facilitadores/Profesores
            if st.session_state.get('user_role') in ['Profesor', 'Administrador']:
                if st.button("Gestión Inscripciones", key="btn_gestion_inscripciones", use_container_width=True):
                    limpiar_estado_modulo_anterior()
                    limpiar_sesion_db()
                    st.session_state.modulo_actual = "Gestión Inscripciones Facilitador"
                    st.rerun()
            
            if st.button("Editor de Certificados", key="btn_editor_certificados", use_container_width=True):
                limpiar_estado_modulo_anterior()
                limpiar_sesion_db()
                st.session_state.modulo_actual = "Editor de Certificados"
                st.rerun()
            
            if st.button("Gestión Carreras", key="btn_gestion_carreras", use_container_width=True):
                limpiar_estado_modulo_anterior()
                limpiar_sesion_db()
                st.session_state.modulo_actual = "Gestión Carreras"
                st.rerun()
            
            if st.button("Formación Extemporánea", key="btn_formacion_extemporanea", use_container_width=True):
                limpiar_estado_modulo_anterior()
                limpiar_sesion_db()
                st.session_state.modulo_actual = "Formación Complementaria Extemporánea"
                st.rerun()
            
            if st.button("Reportes", key="btn_reportes", use_container_width=True):
                limpiar_estado_modulo_anterior()
                limpiar_sesion_db()
                st.session_state.modulo_actual = "Reportes"
                st.rerun()
            
            # Módulos de Gestión de Usuarios - Solo para Administradores
            if st.session_state.get('user_role') == 'Administrador':
                if st.button("Gestión Usuarios", key="btn_gestion_usuarios", use_container_width=True):
                    limpiar_estado_modulo_anterior()
                    limpiar_sesion_db()
                    st.session_state.modulo_actual = "Gestión Usuarios"
                    st.rerun()
                
                if st.button("Registrar Usuario", key="btn_registrar_usuario", use_container_width=True):
                    limpiar_estado_modulo_anterior()
                    limpiar_sesion_db()
                    st.session_state.modulo_actual = "Registrar Usuario"
                    st.rerun()
            
            # Módulo de Gestión de Permisos - Solo para Administradores
            if st.session_state.get('user_role') == 'Administrador':
                if st.button("Gestión de Permisos", key="btn_gestion_permisos", use_container_width=True):
                    limpiar_estado_modulo_anterior()
                    limpiar_sesion_db()
                    st.session_state.modulo_actual = "Gestión de Permisos"
                    st.rerun()
            
            if st.button("Configuracion", key="btn_configuracion", use_container_width=True):
                limpiar_estado_modulo_anterior()
                limpiar_sesion_db()
                st.session_state.modulo_actual = "Configuracion"
                st.rerun()
            
            # Botón de logout
            if st.button("Cerrar Sesión", key="logout", use_container_width=True):
                limpiar_sesion_db()
                st.session_state.logged_in = False
                st.session_state.user_role = None
                st.session_state.user = {}
                st.rerun()
            
            st.markdown("---")
            
                    
        # Contenido principal según módulo seleccionado (con botones)
        if 'modulo_actual' in st.session_state:
            modulo_seleccionado = st.session_state.modulo_actual
            st.markdown(f"### {modulo_seleccionado}")
            
            # Verificar permiso para el módulo seleccionado - MODO DE SEGURIDAD
            from seguridad import tiene_permiso
            
            try:
                tiene_acceso = tiene_permiso(st.session_state.user_role, modulo_seleccionado, 'acceso')
            except Exception as e:
                tiene_acceso = True
            
            # Si no hay acceso, verificar si es un problema de conexión y ofrecer reparación
            if not tiene_acceso:
                try:
                    from database import get_database_info
                    db_info = get_database_info()
                    if db_info.get('status') != 'connected':
                        st.error("Error de conexión a la base de datos")
                        st.markdown("#### Solución Automática")
                        st.write("El sistema ha detectado un problema de conexión. Puede repararlo automáticamente:")
                        
                        if st.button("Reparar Conexión PostgreSQL", type="primary"):
                            try:
                                # Usar DatabaseManager para reparación en lugar de fix_postgresql
                                from database import DatabaseManager
                                db_manager = DatabaseManager()
                                connection_status = db_manager.test_connection()
                                
                                if connection_status.get('status', False):
                                    st.success("Reparación completada. Reinicie la aplicación.")
                                    st.rerun()
                                else:
                                    st.error("No se pudo reparar la conexión")
                            except Exception as repair_error:
                                st.error(f"Error en reparación: {repair_error}")
                except Exception as e:
                    st.error(f"Error verificando estado de la base de datos: {e}")
            
            if tiene_acceso:
                # Router de navegación optimizado - Ejecución selectiva por módulo
                print(f"DEBUG_MODULO: Ejecutando módulo: {st.session_state.modulo_actual}")
                
                if st.session_state.modulo_actual == "Reportes":
                    print("DEBUG_MODULO: Llamando a reportes()")
                    reportes()
                elif st.session_state.modulo_actual == "Formación Complementaria Extemporánea":
                    print("DEBUG_MODULO: Llamando a formacion_extemporanea_main()")
                    formacion_extemporanea_main()
                elif st.session_state.modulo_actual == "Gestión Estudiantil":
                    print("DEBUG_MODULO: Llamando a gestion_estudiantil_main()")
                    gestion_estudiantil_main()
                elif st.session_state.modulo_actual == "Gestión Profesores":
                    print("DEBUG_MODULO: Llamando a gestion_profesores_main()")
                    gestion_profesores_main()
                elif st.session_state.modulo_actual == "Formación Complementaria":
                    print("DEBUG_MODULO: Llamando a modulo_formacion_complementaria()")
                    modulo_formacion_complementaria()
                elif st.session_state.modulo_actual == "Inscripciones Unificadas":
                    inscripciones_unificadas_main()
                elif st.session_state.modulo_actual == "Gestión Inscripciones Facilitador":
                    gestion_inscripciones_facilitador_main()
                elif st.session_state.modulo_actual == "Editor de Certificados":
                    print("DEBUG_MODULO: Llamando a editor_certificados_main()")
                    editor_certificados_main()
                elif st.session_state.modulo_actual == "Gestión Usuarios":
                    gestion_usuarios_main()
                elif st.session_state.modulo_actual == "Registrar Usuario":
                    registro_usuario_main()
                elif st.session_state.modulo_actual == "Gestión de Permisos":
                    gestion_permisos()
                elif st.session_state.modulo_actual == "Gestión Carreras":
                    gestion_carreras()
                # Módulo unificado reemplaza a solicitud_formacion - eliminado completamente
                elif st.session_state.modulo_actual == "Gestión Solicitud Formación Complementaria":
                    gestion_solicitudes_main()
                elif st.session_state.modulo_actual == "Configuracion":
                    configuracion_main()
            else:
                st.error("No tienes acceso a este módulo")
                st.warning("Por favor, contacta al administrador del sistema")
                logger.warning(f"Acceso denegado para {st.session_state.user_role} al módulo {st.session_state.modulo_actual}")
        else:
            st.info("Por favor, selecciona un módulo del menú para comenzar")
            st.markdown("---")
            st.markdown("### Módulos Disponibles")
            
            # Mostrar módulos disponibles según rol
            from seguridad import tiene_permiso
            
            modulos_disponibles = []
            if tiene_permiso(st.session_state.user_role, 'Registro Estudiantes', 'acceso'):
                modulos_disponibles.append("Registro Estudiantes")
            if tiene_permiso(st.session_state.user_role, 'Registro Profesores', 'acceso'):
                modulos_disponibles.append("Registro Profesores")
            if tiene_permiso(st.session_state.user_role, 'Gestión Estudiantil', 'acceso'):
                modulos_disponibles.append("Gestión Estudiantil")
            if tiene_permiso(st.session_state.user_role, 'Gestión Profesores', 'acceso'):
                modulos_disponibles.append("Gestión Profesores")
            if tiene_permiso(st.session_state.user_role, 'Formación Complementaria', 'acceso'):
                modulos_disponibles.append("Formación Complementaria")
            if tiene_permiso(st.session_state.user_role, 'Certificados', 'acceso'):
                modulos_disponibles.append("Certificados")
            if tiene_permiso(st.session_state.user_role, 'Reportes', 'acceso'):
                modulos_disponibles.append("Reportes")
            if tiene_permiso(st.session_state.user_role, 'Configuracion', 'acceso'):
                modulos_disponibles.append("Configuracion")
            
            if modulos_disponibles:
                st.write("Puedes acceder a los siguientes módulos:")
                for modulo in modulos_disponibles:
                    st.write(f"  - {modulo}")
            else:
                st.warning("No tienes módulos disponibles asignados")

def mostrar_login():
    """Función para mostrar el formulario de login"""
    try:
        # Importar el sistema de autenticación unificado
        from auth_unificado import AuthSystemUnificado
        
        # Crear instancia del sistema de autenticación
        auth_system = AuthSystemUnificado()
        
        # Mostrar formulario de login
        auth_system.mostrar_formulario_login()
        
    except Exception as e:
        st.error(f"Error en el sistema de login: {e}")
        logger.error(f"Error en mostrar_login(): {e}")

def mostrar_menu_principal():
    """Función para mostrar el menú principal cuando el usuario está logueado"""
    try:
        # Mostrar información del usuario logueado
        user_role = st.session_state.get('user_role', 'Desconocido')
        user_nombre = st.session_state.get('user_nombre', 'Usuario')
        user_cedula = st.session_state.get('user_cedula', 'N/A')
        
        # Header con información del usuario
        st.markdown("---")
        st.markdown(f"### Bienvenido, **{user_nombre}**")
        st.info(f"Rol: {user_role} | Cédula: {user_cedula}")
        
        # Selección de módulo
        st.markdown("## Seleccione un módulo:")
        
        # Lista de módulos disponibles según rol
        modulos_disponibles = []
        
        if user_role == 'Administrador':
            modulos_disponibles = [
                "Gestión Estudiantil",
                "Gestión Profesores", 
                "Registro Estudiantes",
                "Registro Profesores", 
                "Formación Complementaria",
                "Inscripciones Unificadas",
                "Gestión Formación Complementaria",
                "Certificados",
                "Reportes",
                "Gestión Usuarios",
                "Registrar Usuario",
                "Gestión de Permisos",
                "Gestión Carreras"
            ]
        elif user_role == 'Profesor':
            modulos_disponibles = [
                "Gestión Estudiantil",
                "Gestión Profesores",
                "Formación Complementaria",
                "Inscripciones Unificadas",
                "Gestión Formación Complementaria",
                "Certificados",
                "Reportes"
            ]
        elif user_role == 'Estudiante':
            modulos_disponibles = [
                "Gestión Estudiantil",
                "Formación Complementaria",
                "Inscripciones Unificadas",
                "Certificados",
                "Reportes"
            ]
        
        # Selector de módulo
        if modulos_disponibles:
            modulo_seleccionado = st.selectbox("Elija un módulo para acceder:", modulos_disponibles)
            
            # Botón para acceder al módulo
            if st.button("Acceder al Módulo", type="primary"):
                # Guardar el módulo seleccionado en sesión
                st.session_state.modulo_actual = modulo_seleccionado
                st.rerun()
        else:
            st.warning("No hay módulos disponibles para tu rol.")
        
        # Botón de logout
        st.markdown("---")
        if st.button("Cerrar Sesión", type="secondary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = {}
            st.session_state.user_role = None
            st.session_state.user_cedula = None
            st.session_state.cedula = None
            st.session_state.user_nombre = None
            st.session_state.modulo_actual = None
            st.rerun()
            
    except Exception as e:
        st.error(f"Error en el menú principal: {e}")
        logger.error(f"Error en mostrar_menu_principal(): {e}")

if __name__ == "__main__":
    main()
