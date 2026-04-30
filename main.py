# -*- coding: utf-8 -*-
"""
main.py - Sistema de Informacion de Control Academico de Formacion Complementaria
Instituto Universitario Jesus Obrero
Version 3.0 - Arquitectura Unificada Local/Nube
"""

import streamlit as st  # type: ignore
import logging
import sys
import locale
import os

# Importar estilos globales de formularios
from styles import aplicar_estilo_consistente_global

# CONFIGURACIÓN DE FONDO INSTITUCIONAL
def configurar_fondo_institucional():
    """Aplica imagen de fondo institucional IUJO-Sede con transparencia"""
    st.markdown("""
    <style>
    /* Fondo institucional para toda la aplicación */
    .stApp {
        background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77yQAAAABJRU5ErkJggg==");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    /* Fondo principal con transparencia */
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 10px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px);
    }
    
    /* Sidebar con transparencia */
    .css-1d391kg {
        background-color: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(5px);
    }
    
    /* Formularios con fondo semitransparente */
    .stForm {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Dataframes con fondo legible */
    .stDataFrame {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 8px;
    }
    
    /* Botones con mejor contraste */
    .stButton > button {
        background-color: rgba(0, 123, 255, 0.9);
        color: white;
        border: none;
        border-radius: 5px;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: rgba(0, 86, 179, 0.95);
    }
    
    /* Input fields con mejor visibilidad */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        background-color: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(0, 0, 0, 0.2);
        border-radius: 5px;
    }
    
    /* Headers con buen contraste */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1a1a1a;
        text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Cargar imagen de fondo desde archivo local
    try:
        import base64
        from pathlib import Path
        
        # Ruta a la imagen IUJO-Sede
        image_path = Path("assets/IUJO-Sede.png")
        
        if image_path.exists():
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode()
                
            # Aplicar imagen de fondo real
            st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded_image}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
            """, unsafe_allow_html=True)
        else:
            # Imagen por defecto si no encuentra el archivo
            st.markdown("""
            <style>
            .stApp {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            </style>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        # Fallback a gradiente si hay error
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        </style>
        """, unsafe_allow_html=True)

# FORZAR UTF-8 EN TODA LA APLICACIÓN
if sys.platform.startswith('win'):
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
    except:
        pass

def asegurar_estructura_bd():
    """Función de autoreparación de base de datos"""
    try:
        print("=== INICIANDO AUTOREPARACIÓN DE BASE DE DATOS ===")
        
        # 1. Importar y verificar configuración
        from database import DatabaseManager, get_db_connection
        db_manager = DatabaseManager()
        
        print(f"BD DETECTADA: {db_manager.config['database']}")
        print(f"HOST: {db_manager.config['host']}")
        print(f"USER: {db_manager.config['user']}")
        
        # 2. Verificar si tabla usuarios existe
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT 1 FROM usuarios LIMIT 1")
            cursor.close()
            print("OK: TABLA 'usuarios' YA EXISTE - SIN REPARACIÓN NECESARIA")
            conn.close()
            return True
        except Exception as e:
            print(f"DIAGNÓSTICO: Tabla 'usuarios' NO EXISTE - {e}")
            cursor.close()
        
        # 3. Ejecutar script de sincronización
        script_path = os.path.join(os.path.dirname(__file__), 'sincronizacion_tablas.sql')
        
        if not os.path.exists(script_path):
            print(f"ERROR: Script no encontrado: {script_path}")
            conn.close()
            return False
        
        print(f"EJECUTANDO SCRIPT: {script_path}")
        
        # Leer y ejecutar script
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        cursor = conn.cursor()
        cursor.execute(sql_content)
        conn.commit()
        cursor.close()
        conn.close()
        
        print("OK: SCRIPT DE SINCRONIZACIÓN EJECUTADO EXITOSAMENTE")
        
        # 4. Verificar post-reparación
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM usuarios LIMIT 1")
        cursor.close()
        conn.close()
        
        print("OK: TABLA 'usuarios' CREADA Y VALIDADA POST-REPARACIÓN")
        return True
        
    except Exception as e:
        print(f"ERROR CRÍTICO EN AUTOREPARACIÓN: {e}")
        return False

# EJECUTAR AUTOREPARACIÓN ANTES DE CARGAR MÓDULOS
print("=== VERIFICANDO ESTRUCTURA DE BASE DE DATOS AL INICIAR ===")
reparacion_exitosa = asegurar_estructura_bd()
if not reparacion_exitosa:
    print("ADVERTENCIA: LA AUTOREPARACIÓN FALLÓ - EL SISTEMA PUEDE NO FUNCIONAR CORRECTAMENTE")
else:
    print("OK: ESTRUCTURA DE BASE DE DATOS VERIFICADA Y REPARADA SI FUE NECESARIO")

# LIMPIEZA DE CACHÉ - MODO DE SEGURIDAD
st.cache_resource.clear()
st.cache_data.clear()

# LIMPIEZA EN CAMBIO DE MÓDULO - RESET EXPLÍCITO
if 'modulo_anterior' in st.session_state and st.session_state.modulo_anterior != st.session_state.get('modulo_actual', ''):
    print(f"Cambio de módulo detectado: {st.session_state.modulo_anterior} -> {st.session_state.modulo_actual}")
    
    # Cerrar todas las conexiones forzosamente
    try:
        from database import close_database
        close_database()
        print("OK Conexiones forzadamente cerradas al cambiar de módulo")
    except Exception as e:
        print(f"Error cerrando conexiones: {e}")
    
    # Limpiar variables de estado relacionadas con BD
    keys_to_clean = [key for key in st.session_state.keys() 
                     if any(term in key.lower() for term in ['db', 'connection', 'usuario', 'modulo', 'transaccion'])]
    
    for key in keys_to_clean:
        del st.session_state[key]
    
    print(f"Limpieza por cambio de módulo: eliminadas {len(keys_to_clean)} variables")
    
    # Actualizar módulo anterior
    st.session_state.modulo_anterior = st.session_state.get('modulo_actual', '')

# DETECCIÓN DE TRANSACCIÓN ABORTADA - RESET DE EMERGENCIA
if 'transaccion_abortada' in st.session_state:
    print("ALERTA TRANSACCION ABORTADA - EJECUTANDO RESET TOTAL")
    # Limpiar estado de transacción
    del st.session_state.transaccion_abortada
    
    # Limpiar variables de conexión
    keys_to_clean = [key for key in st.session_state.keys() 
                     if any(term in key.lower() for term in ['db', 'connection', 'usuario', 'modulo'])]
    
    for key in keys_to_clean:
        del st.session_state[key]
    
    print(f"Limpieza por transacción abortada: eliminadas {len(keys_to_clean)} variables de estado")
    
    # Forzar reconexión en siguiente interacción
    st.session_state.forzar_reconexion = True

# PRIMER COMANDO STREAMLIT - Configuración de página
st.set_page_config(
    page_title="SICADFOC 2026 - IUJO",
    page_icon="IUJO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
from database import get_db_session, authenticate_user, get_database_info, close_database, ensure_admin_exists, DatabaseManager
from gestion_permisos import mostrar_gestion_permisos
from gestion_carreras import mostrar_gestion_carreras, precargar_carreras_iniciales

# Ejecutar ensure_admin_exists() al inicio para garantizar administradores
try:
    ensure_admin_exists()
    print("OK Administradores verificados/creados")
except Exception as e:
    print(f"Error verificando administradores: {e}")

# Precargar carreras iniciales si no existen
try:
    precargar_carreras_iniciales()
    print("OK Carreras iniciales verificadas/precargadas")
except Exception as e:
    print(f"Error precargando carreras: {e}")

def gestion_permisos():
    """Módulo de Gestión de Permisos - Solo para Administradores"""
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
            password="admin123"
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Obtener todos los usuarios
        cursor.execute("""
            SELECT u.cedula_usuario, u.login_usuario, u.rol, u.activo,
                   p.nombre, p.apellido, u.modulos_permitidos
            FROM usuarios u
            LEFT JOIN persona p ON u.cedula_usuario = p.cedula
            ORDER BY u.rol, p.apellido, p.nombre
        """)
        usuarios = cursor.fetchall()
        
        if not usuarios:
            st.warning("No hay usuarios registrados en el sistema")
            return
        
        # Módulos disponibles para asignar
        modulos_disponibles = [
            "Configuración",
            "Gestión Estudiantil", 
            "Reportes",
            "Formación Complementaria",
            "Registro Estudiantes",
            "Registro Profesores",
            "Gestión Profesores",
            "Historial Estudiantil",
            "Gestión Carreras"
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
                            UPDATE usuarios 
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
            FROM usuarios
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
    try:
        print("VALIDANDO ESQUEMA PRINCIPAL...")
        
        # Limpiar caché para garantizar conexión fresca
        st.cache_resource.clear()
        st.cache_data.clear()
        
        # Obtener manager y ejecutar test de conexión
        db_manager = DatabaseManager()
        test_result = db_manager.test_connection()
        
        if not test_result['status']:
            st.error(f"❌ ERROR CRÍTICO DE CONEXIÓN: {test_result['message']}")
            st.error("❌ ACCIONES REQUERIDAS:")
            st.error("1. Ejecute: psql -h localhost -U postgres -d db_foc26 -f sincronizacion_tablas.sql")
            st.error("2. Verifique que PostgreSQL esté corriendo: pg_isready -h localhost -p 5432")
            st.error("3. Revise los logs del sistema para más detalles")
            st.stop()
            return False
        
        # Verificar tablas críticas
        db_info = test_result.get('database_info', {})
        usuarios_existe = db_info.get('usuarios_table_exists', False)
        estudiante_existe = db_info.get('estudiante_table_exists', False)
        
        if not usuarios_existe:
            st.error("❌ TABLA 'usuarios' NO EXISTE")
            st.error("Ejecute: psql -h localhost -U postgres -d db_foc26 -f sincronizacion_tablas.sql")
            st.stop()
            return False
        
        if not estudiante_existe:
            st.error("❌ TABLA 'estudiante' NO EXISTE")
            st.error("Ejecute: psql -h localhost -U postgres -d db_foc26 -f sincronizacion_tablas.sql")
            st.stop()
            return False
        
        print("✅ ESQUEMA VALIDADO - SISTEMA OPERATIVO")
        return True
        
    except Exception as e:
        st.error(f"❌ ERROR VALIDANDO ESQUEMA: {e}")
        st.error("Revise la configuración de la base de datos")
        st.stop()
        return False

# Importaciones de módulos principales (actualizados a nombres oficiales)
from gestion_estudiantil import gestion_estudiantil
from gestion_profesores import gestion_profesores_main
from gestion_profesores import registro_profesores_main
from gestion_estudiantil import registro_estudiantes_main
from formacion_complementaria import modulo_formacion_complementaria, gestion_formacion_complementaria
from gestor_certificaciones import gestor_certificaciones_unificado, solicitud_formacion_main, gestion_solicitudes_main
# from modulo_configuracion import modulo_configuracion  # Eliminado en limpieza
from reportes import reportes
# from registro_publico import registro_publico_usuarios  # Eliminado en limpieza
from auth_unificado import gestion_usuarios_main, registro_usuario_main
from gestion_permisos import gestion_permisos
from gestion_carreras import gestion_carreras
from seguridad import SeguridadFOC26, tiene_permiso

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
        'configuracion_temporal',
        # Claves específicas de formación complementaria
        'inscripcion_exitosa',
        'solicitud_seleccionada',
        'taller_inscripcion',
        'cupos_verificados',
        'codigo_generado',
        'estado_actualizado'
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
    """Limpia todas las conexiones residuales antes de cambiar de módulo"""
    try:
        # Limpiar cachés de Streamlit
        st.cache_resource.clear()
        st.cache_data.clear()
        
        # Forzar cierre de conexiones en database
        try:
            from database import close_database
            close_database()
            print("OK Conexiones forzadamente cerradas al limpiar caché")
        except Exception as e:
            print(f"⚠️ Error cerrando conexiones: {e}")
        
        # Eliminar cualquier conexión residual en session_state
        keys_to_remove = []
        for key in st.session_state.keys():
            if 'db' in key.lower() or 'connection' in key.lower():
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del st.session_state[key]
        
        print(f"🧹 Limpieza de sesión DB completada. Eliminadas {len(keys_to_remove)} conexiones residuales.")
        
    except Exception as e:
        print(f"⚠️ Error en limpieza de sesión DB: {e}")

def conectar_foc26db():
    """Conexión centralizada a la base de datos usando db_manager.py"""
    global db_connection, db_connected, db_error
    
    try:
        if debug_mode:
            st.write("=== MODO DEBUG: CONEXIÓN A FOC26DB ===")
            st.write(f"Timestamp: {datetime.now().isoformat()}")
            st.write(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
        
        # Usar database.py como Single Source of Truth
        from database import get_db_connection
        db_connection = get_db_connection()
        
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
    """Autenticación segura usando database.py con 4 capas de seguridad"""
    try:
        # Importar el nuevo database
        from database import authenticate_user
        
        # Capturar cédula del formulario
        cedula_limpia = usuario_input.strip().upper()
        
        # BYPASS DE EMERGENCIA PARA ADMINISTRADOR - TEMPORALMENTE ACTIVADO PARA DEBUG
        if cedula_limpia == 'V-14300385':
            print("BYPASS DE EMERGENCIA ACTIVADO")
            st.success("Acceso de emergencia como Administrador")
            return {
                'rol': 'Administrador', 
                'login': 'Administrator Angel Hernandez',
                'cedula': 'V-14300385',
                'es_superusuario': True
            }
        
        # Usar autenticación segura con database.py
        resultado_auth = authenticate_user(cedula_limpia, clave_input)
        
        if resultado_auth:
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
                'message': 'Usuario o contraseña incorrectos'
            }
        
        if resultado['success']:
            usuario_data = resultado['data']
            
            st.success(f"Bienvenido {usuario_data['rol']}: {usuario_data['nombre_usuario']}")
            
            return {
                'rol': resultado['data']['rol'], 
                'login': resultado['data']['nombre_usuario'],
                'cedula': resultado['data']['cedula_usuario'],
                'es_superusuario': resultado['data']['es_superusuario']
            }
        else:
            # Mostrar error específico
            if 'no encontrado' in resultado['message'].lower():
                st.error("Usuario no encontrado o inactivo")
            elif 'contraseña' in resultado['message'].lower():
                st.error("Contraseña incorrecta")
            else:
                st.error(f"Error: {resultado['message']}")
            return None
            
    except Exception as e:
        st.error("Error de autenticación. Contacte al administrador.")
        if debug_mode:
            st.error(f"Error: {e}")
        return None

def main():
    """Función principal unificada para local y nube"""
    
    # Aplicar estilos globales de formularios (MANDATORIO)
    aplicar_estilo_consistente_global()
    
    # Aplicar fondo institucional IUJO-Sede
    configurar_fondo_institucional()
    
    # Configuración optimizada de página
    st.set_page_config(
        page_title="SICADFOC 2026",
        page_icon="",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # CSS global
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
    
    # Login o contenido principal
    if not st.session_state.logged_in:
        # CSS CORREGIDO PARA LEGIBILIDAD - Texto oscuro y sin fondos azules
        st.markdown("""
        <style>
        /* CONTENEDORES CON TRANSPARENCIA CONTROLADA */
        .main .block-container {
            background-color: rgba(255, 255, 255, 0.9) !important;
            border-radius: 12px !important;
            padding: 2rem !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        }
        
        form[data-testid="stForm"] {
            background-color: rgba(255, 255, 255, 0.95) !important;
            border-radius: 8px !important;
            padding: 1.5rem !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        }
        
        /* TÍTULOS OSCUROS CON ALTO CONTRASTE */
        h1, h2, h3, h4,
        .stMarkdown h1,
        .stMarkdown h2,
        .stMarkdown h3,
        .stMarkdown h4 {
            color: #0D1117 !important;
            font-weight: 800 !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8) !important;
        }
        
        /* ETIQUETAS DE CAMPOS OSCURECIDAS */
        label,
        .stTextInput label,
        .stSelectbox label,
        .stTextArea label,
        .stCheckbox label,
        div[data-testid="stTextInput"] label,
        div[data-testid="stSelectbox"] label,
        div[data-testid="stTextArea"] label,
        div[data-testid="stCheckbox"] label {
            color: #0D1117 !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            background-color: transparent !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.7) !important;
        }
        
        /* TEXTO MARKDOWN OSCURECIDO */
        .stMarkdown,
        .stMarkdown *,
        div[data-testid="stMarkdownContainer"],
        div[data-testid="stMarkdownContainer"] * {
            color: #0D1117 !important;
            font-weight: 600 !important;
            background-color: transparent !important;
            text-shadow: 1px 1px 1px rgba(255, 255, 255, 0.6) !important;
        }
        
        /* INPUTS CON TEXTO OSCURO */
        input[type="text"],
        input[type="password"],
        input[type="email"],
        textarea,
        select,
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stSelectbox"] select {
            background-color: white !important;
            color: #0D1117 !important;
            border: 2px solid #2563EB !important;
            border-radius: 6px !important;
            padding: 10px !important;
            font-weight: 600 !important;
        }
        
        /* PLACEHOLDERS OSCUROS CON CONTRASTE */
        input::placeholder,
        textarea::placeholder,
        div[data-testid="stTextInput"] input::placeholder,
        div[data-testid="stTextArea"] textarea::placeholder {
            color: #4A4A4A !important;
            font-weight: 500 !important;
            opacity: 1 !important;
            background-color: transparent !important;
        }
        
        /* TEXTO DE AYUDA Y DESCRIPCIÓN OSCURECIDO */
        div[data-testid="stHelpText"],
        .stHelpText,
        .stCaption,
        div[data-testid="stCaption"] {
            color: #2A2A2A !important;
            font-weight: 500 !important;
            background-color: transparent !important;
            text-shadow: 1px 1px 1px rgba(255, 255, 255, 0.5) !important;
        }
        
        /* BOTÓN PRINCIPAL MANTENIDO */
        button[kind="primary"] {
            background-color: #2563EB !important;
            color: white !important;
            font-weight: 600 !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 10px 20px !important;
        }
        
        /* TABS CON TEXTO OSCURO */
        .stTabs [data-baseweb="tab-list"] {
            background-color: rgba(255, 255, 255, 0.8) !important;
            border-radius: 8px !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #0D1117 !important;
            font-weight: 700 !important;
            background-color: transparent !important;
            text-shadow: 1px 1px 1px rgba(255, 255, 255, 0.6) !important;
        }
        
        /* ELIMINAR FONDOS AZULES NO DESEADOS */
        .element-container,
        .stElementContainer {
            background-color: transparent !important;
        }
        
        /* TEXTO DE ERROR Y ÉXITO OSCURECIDO */
        .stException,
        .stAlert,
        .stSuccess,
        div[data-testid="stException"],
        div[data-testid="stAlert"],
        div[data-testid="stSuccess"] {
            color: #0D1117 !important;
            font-weight: 600 !important;
            background-color: rgba(255, 255, 255, 0.9) !important;
            text-shadow: 1px 1px 1px rgba(255, 255, 255, 0.7) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<h3 style="color: #0A0A0A !important; font-weight: 800 !important; text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.9), 1px 1px 2px rgba(0, 0, 0, 0.8) !important; margin-bottom: 2rem !important;">Iniciar Sesión</h3>', unsafe_allow_html=True)
        
        # Crear tabs para Login y Registro
        tab_login, tab_registro = st.tabs(["Iniciar Sesión", "Registrar Usuario"])
        
        # Tab de Iniciar Sesión
        with tab_login:
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                with st.form("login_form"):
                    st.markdown('<h4 style="color: #0A0A0A !important; font-weight: 800 !important; text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.9), 1px 1px 2px rgba(0, 0, 0, 0.8) !important; margin-bottom: 1.5rem !important;">Acceso al Sistema</h4>', unsafe_allow_html=True)
                    
                    usuario = st.text_input("Cédula o Usuario", placeholder="Ej: V-12345678")
                    clave = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
                    
                    submit_button = st.form_submit_button("Iniciar Sesión", use_container_width=True)
                    
                    if submit_button:
                        if not usuario or not clave:
                            st.error("Por favor ingrese usuario y contraseña")
                        else:
                            print(f"INTENTO DE LOGIN: usuario={usuario}")
                            
                            try:
                                # Verificar usuario
                                resultado = verificar_usuario(usuario, clave)
                                print(f"RESULTADO verificar_usuario: {resultado}")
                                
                                if resultado:
                                    print("LOGIN EXITOSO - Configurando sesión")
                                    st.session_state.logged_in = True
                                    st.session_state.user_role = resultado['rol']
                                    st.session_state.user_cedula = resultado['cedula']
                                    st.session_state.es_superusuario = resultado.get('es_superusuario', False)
                                    # Agregar información completa de usuario para configuración
                                    st.session_state.user = {
                                        'rol': resultado['rol'],
                                        'cedula_usuario': resultado['cedula'],
                                        'login_usuario': resultado['login'],
                                        'es_superusuario': resultado.get('es_superusuario', False),
                                        'rol_descripcion': resultado.get('rol_descripcion', '')
                                    }
                                    st.success(f"Bienvenido {resultado['login']}!")
                                    if resultado.get('es_superusuario', False):
                                        st.warning("Acceso de Superusuario activado")
                                    print("SESION CONFIGURADA - Ejecutando st.rerun()")
                                    st.rerun()
                                else:
                                    print("LOGIN FALLIDO - resultado es None")
                                    st.error("Usuario o contraseña incorrectos")
                                    st.warning("Verifique sus credenciales e intente nuevamente.")
                                    
                            except Exception as e:
                                print(f"ERROR EN LOGIN: {e}")
                                import traceback
                                print(f"TRACEBACK LOGIN: {traceback.format_exc()}")
                                st.error("Error en el proceso de login")
                                st.warning("Intente nuevamente o contacte al administrador")
        
        # Tab de Registrar Usuario
        with tab_registro:
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown("#### Registro de Nuevo Usuario")
                
                # Verificar conexión antes de permitir registro
                connection_ok = False
                try:
                    from database import get_database_info
                    result = get_database_info()
                    connection_ok = result and result.get('status', False)
                except Exception as e:
                    connection_ok = False
                
                # Solo permitir registro si hay conexión
                if connection_ok:
                    # Mostrar formulario de registro
                    registro_usuario_main()
                else:
                    st.error("No se puede registrar usuarios sin conexión a la base de datos")
                    st.info("Por favor, reconecte e intente nuevamente")
        
            
    else:
        # Usuario autenticado - mostrar sidebar con módulos y contenido principal
        with st.sidebar:
            # Información del usuario actual
            if st.session_state.get('logged_in', False):
                user_info = st.session_state.get('user', {})
                st.markdown(f"### {user_info.get('login_usuario', 'Usuario')}")
                st.caption(f"Rol: {st.session_state.get('user_role', 'N/A')}")
            else:
                st.markdown("### Sistema")
            
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
                    st.session_state.es_superusuario = False
                    st.session_state.user = None
                    st.rerun()
                    
            except Exception as e:
                print(f"Error verificando conexión: {e}")
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
            st.markdown("### Módulos Operativos")
            
            # MÓDULOS OPERATIVOS PRINCIPALES
            st.markdown("#### Gestión Académica")
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
            
            if st.button("Gestión Carreras", key="btn_gestion_carreras", use_container_width=True):
                limpiar_estado_modulo_anterior()
                limpiar_sesion_db()
                st.session_state.modulo_actual = "Gestión Carreras"
                st.rerun()
            
            st.markdown("#### Formación Complementaria")
            
            # Control de acceso por permisos (no por rol fijo)
            from seguridad import tiene_permiso
            user_role = st.session_state.get('user_role', '')
            
            # Botón Solicitud Formación - disponible para todos con permiso de consulta
            if tiene_permiso(user_role, 'Solicitud Formación Complementaria', 'Consultar'):
                if st.button("Solicitud Formación", key="btn_solicitud_formacion", use_container_width=True):
                    limpiar_estado_modulo_anterior()
                    limpiar_sesion_db()
                    st.session_state.modulo_actual = "Solicitud Formación Complementaria"
                    st.rerun()
            
            # Botón Formación Complementaria - disponible según permisos configurados
            if tiene_permiso(user_role, 'Formación Complementaria', 'Consultar'):
                if st.button("Formación Complementaria", key="btn_formacion", use_container_width=True):
                    limpiar_estado_modulo_anterior()
                    limpiar_sesion_db()
                    st.session_state.modulo_actual = "Formación Complementaria"
                    st.rerun()
            
            # Botón Gestión Solicitudes - disponible según permisos configurados
            if tiene_permiso(user_role, 'Gestión Solicitud Formación Complementaria', 'Consultar'):
                if st.button("Gestión Solicitudes", key="btn_gestion_solicitud", use_container_width=True):
                    limpiar_estado_modulo_anterior()
                    limpiar_sesion_db()
                    st.session_state.modulo_actual = "Gestión Solicitud Formación Complementaria"
                    st.rerun()
            
            st.markdown("#### Servicios Académicos")
            if st.button("Historial Estudiantil", key="btn_historial", use_container_width=True):
                limpiar_estado_modulo_anterior()
                limpiar_sesion_db()
                st.session_state.modulo_actual = "Historial Estudiantil"
                st.rerun()
            
            if st.button("Formación Extemporánea", key="btn_formacion_extemporanea", use_container_width=True):
                limpiar_estado_modulo_anterior()
                limpiar_sesion_db()
                st.session_state.modulo_actual = "Formación Complementaria Extemporánea"
                st.rerun()
            
            if st.button("Certificados", key="btn_certificados", use_container_width=True):
                limpiar_estado_modulo_anterior()
                limpiar_sesion_db()
                st.session_state.modulo_actual = "Certificados"
                st.rerun()
            
            st.markdown("#### Reportes y Análisis")
            if st.button("Reportes", key="btn_reportes", use_container_width=True):
                limpiar_estado_modulo_anterior()
                limpiar_sesion_db()
                st.session_state.modulo_actual = "Reportes"
                st.rerun()
            
            # MÓDULOS DE ADMINISTRACIÓN - Solo para Administradores
            if st.session_state.get('user_role') == 'Administrador':
                st.markdown("#### Administración del Sistema")
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
                
                if st.button("Gestión de Permisos", key="btn_gestion_permisos", use_container_width=True):
                    limpiar_estado_modulo_anterior()
                    limpiar_sesion_db()
                    st.session_state.modulo_actual = "Gestión de Permisos"
                    st.rerun()
            
            if st.button("Configuración", key="btn_configuracion", use_container_width=True):
                limpiar_estado_modulo_anterior()
                limpiar_sesion_db()
                st.session_state.modulo_actual = "Configuración"
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
                print(f"Error verificando permisos: {e}")
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
                # Mapeo de módulos a funciones (nombres oficiales)
                modulos_map = {
                    'Registro Estudiantes': registro_estudiantes_main,
                    'Registro Profesores': registro_profesores_main,
                    'Gestión Estudiantil': gestion_estudiantil,
                    'Gestión Profesores': gestion_profesores_main,
                    'Formación Complementaria': modulo_formacion_complementaria,
                    'Certificados': gestor_certificaciones_unificado,
                    'Solicitud Formación Complementaria': solicitud_formacion_main,
                    'Gestión Solicitud Formación Complementaria': gestion_solicitudes_main,
                    'Reportes': reportes,
                    'Gestión Usuarios': gestion_usuarios_main,
                    'Registrar Usuario': registro_usuario_main,
                    'Gestión de Permisos': gestion_permisos,
                    'Gestión Carreras': gestion_carreras
                }
                
                # Ejecutar módulo correspondiente con validación de emergencia
                if modulo_seleccionado in modulos_map:
                    try:
                        # Validación de conexión silenciosa
                        from database import get_db_connection
                        connection = get_db_connection()
                        
                        # Ejecutar módulo
                        try:
                            modulos_map[modulo_seleccionado]()
                        except NameError as ne:
                            st.error(f"Error de definición en módulo {modulo_seleccionado}: {ne}")
                            logger.error(f"NameError en {modulo_seleccionado}: {ne}")
                        except UnboundLocalError as ule:
                            st.error(f"Error de variable local en módulo {modulo_seleccionado}: {ule}")
                            logger.error(f"UnboundLocalError en {modulo_seleccionado}: {ule}")
                        except Exception as module_error:
                            st.error(f"Error ejecutando módulo {modulo_seleccionado}: {module_error}")
                            logger.error(f"Error en módulo {modulo_seleccionado}: {module_error}")
                    except Exception as e:
                        st.error(f"Error de conexión al ejecutar módulo {modulo_seleccionado}: {e}")
                        logger.error(f"Error de conexión en {modulo_seleccionado}: {e}")
                else:
                    st.error(f"Módulo '{modulo_seleccionado}' no encontrado")
                    logger.warning(f"Módulo no encontrado: {modulo_seleccionado}")
            else:
                st.error("No tienes acceso a este módulo")
                st.warning("Por favor, contacta al administrador del sistema")
                logger.warning(f"Acceso denegado para {st.session_state.user_role} al módulo {modulo_seleccionado}")
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
                "Gestión Formación Complementaria",
                "Certificados",
                "Reportes"
            ]
        elif user_role == 'Estudiante':
            modulos_disponibles = [
                "Gestión Estudiantil",
                "Formación Complementaria",
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
        if st.button("Cerrar Sesión", type="secondary"):
            # Limpiar sesión
            st.session_state.logged_in = False
            st.session_state.user = {}
            st.session_state.user_role = None
            st.session_state.user_cedula = None
            st.session_state.user_nombre = None
            st.session_state.modulo_actual = None
            st.rerun()
            
    except Exception as e:
        st.error(f"Error en el menú principal: {e}")
        logger.error(f"Error en mostrar_menu_principal(): {e}")

if __name__ == "__main__":
    main()
