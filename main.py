import streamlit as st

import pandas as pd

import os
import sys
import io
import base64

import time

import random

import hashlib

from datetime import datetime

from sqlalchemy import create_engine, text

# =================================================================
# CONFIGURACIÓN DE CODIFICACIÓN UTF-8 PARA WINDOWS
# =================================================================

# Configurar codificación UTF-8 para evitar UnicodeEncodeError en Windows
if sys.platform.startswith('win'):
    try:
        # Configurar stdout para UTF-8
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
        print("Codificacion UTF-8 configurada para Windows")
    except AttributeError:
        # Para versiones anteriores de Python
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
        print("Codificacion UTF-8 configurada (fallback) para Windows")
    except Exception as e:
        print(f"Advertencia: No se pudo configurar UTF-8: {e}")

# Configuración de base de datos para producción
DATABASE_URL = os.getenv('DATABASE_URL', None)

# Importar componentes de base de datos con soporte para producción
if DATABASE_URL:
    # Configuración para PostgreSQL en Render
    from database.connection import get_engine_espejo
    engine = get_engine_espejo()
else:
    # Configuración local SQLite
    import database
    from database import ejecutar_query, crear_tablas_sistema, crear_usuario_prueba, obtener_logs_sistema
    from database import engine, get_engine_local, get_engine_espejo, configurar_correo_final, probar_envio_correo

import re



# Importar componentes de UI protegidos
from ui.ui_components import mostrar_dashboard_protegido

# Importar sistema de autenticación y roles
from auth.decorators import (
    requerir_autenticacion, requerir_rol, requerir_permiso,
    solo_administradores, solo_profesores, solo_estudiantes,
    acceso_gestion_usuarios, acceso_gestion_cursos, acceso_gestion_talleres,
    mostrar_info_acceso, obtener_info_permisos_usuario
)



# Importar módulo de sincronización con la nube

from modules.cloud_sync import verificar_estado_nube, obtener_ultima_actualizacion



# Importar configuración de producción

try:

    from config.production_config import configure_production

    configure_production()

except ImportError:

    pass



# =================================================================

# CARGAR CSS EXTERNO

# =================================================================

def load_css(filename):

    """Cargar archivo CSS externo"""

try:
    from static_config import get_css_content
    css_content = get_css_content()
    if css_content:
        st.markdown(css_content, unsafe_allow_html=True)
        css_cargado = True
    else:
        css_cargado = False
except ImportError:
    css_cargado = False

# Mostrar mensaje si CSS no se pudo cargar
if not css_cargado:
    st.warning("⚠️ Archivo CSS no encontrado. Algunos estilos pueden no aplicarse.")




# =================================================================

# CSS LIMPIO Y MODULAR PARA SICADFOC

# =================================================================

st.markdown("""

<style>

    /* Contenedor principal limpio */

    .main .block-container {

        padding-top: 2rem;

        padding-bottom: 2rem;

        max-width: 800px;

    }

    

    /* Estilo consistente para cuadros/cards SICADFOC */

    .sicadfoc-card {

        background: #ffffff !important;

        border: 1px solid #e5e7eb !important;

        border-radius: 12px !important;

        padding: 1.5rem !important;

        margin: 1rem 0 !important;

        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;

    }

    

    /* Botones modernos */

    .stButton > button {

        height: 2.5rem !important;

        padding: 0.5rem 1.5rem !important;

        margin: 0.5rem 0 !important;

        font-size: 0.9rem !important;

        border-radius: 8px !important;

        transition: all 0.2s ease !important;

    }

    

    .stButton > button:hover {

        transform: translateY(-1px) !important;

        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;

    }

</style>

""", unsafe_allow_html=True)



# =================================================================

# PASO 2: FORZAR CREACIÓN DE TABLAS SIN MENSAJES INNECESARIOS

# =================================================================

try:

    # Forzar la creación de todas las tablas necesarias

    crear_tablas_sistema(engine)

    

    # Validación de conexión (Ping a la DB) - sin mostrar mensaje

    with engine.connect() as conn:

        conn.execute(text("SELECT 1"))

        # Conexión exitosa - sin mostrar mensaje para limpiar interfaz

        

except Exception as e:

    # Solo mostrar error si es crítico y no hay captcha activo

    if not st.session_state.get('usuario_nuevo', False):

        st.error(f"❌ Error de conexión: {e}")

    # Continuar aunque falle para no detener la aplicación



# =================================================================

# FUNCIÓN DE REGISTRO LIMPIO

# =================================================================

def mostrar_registro():

    """Cambia el estado a REGISTRO y ejecuta rerun para transición limpia"""

    st.session_state.pagina_actual = 'REGISTRO'

    st.rerun()



# =================================================================

# FUNCIONES DE CAPTCHA MATEMÁTICO

# =================================================================

def generar_captcha_matematico():

    """Genera un captcha matemático simple con persistencia"""

    # Solo generar si no existe uno activo

    if 'captcha_resultado' not in st.session_state:

        n1 = random.randint(1, 10)

        n2 = random.randint(1, 10)

        resultado = n1 + n2

        

        # Guardar en session state

        st.session_state['captcha_n1'] = n1

        st.session_state['captcha_n2'] = n2

        st.session_state['captcha_resultado'] = resultado

        st.session_state['captcha_generado'] = True

    

    return (

        st.session_state['captcha_n1'], 

        st.session_state['captcha_n2'], 

        st.session_state['captcha_resultado']

    )



def validar_captcha_matematico(input_usuario):

    """Valida el input del usuario contra el captcha matemático"""

    resultado_correcto = st.session_state.get('captcha_resultado', 0)

    

    try:

        return int(input_usuario) == resultado_correcto

    except (ValueError, TypeError):

        return False



def obtener_logo_base64():

    """Convierte la imagen del logo IUJO a formato base64 para usarla como logo institucional"""

    try:

        # Prioridad 1: Logo institucional nuevo (recibido)

        logo_path = os.path.join(os.path.dirname(__file__), "ui", "assets", "logo-iujo-institucional.png")
        
        # Verificar si la imagen existe

        if not os.path.exists(logo_path):

            # Prioridad 2: Logo IUJO estándar

            logo_path = os.path.join(os.path.dirname(__file__), "ui", "assets", "iujo-logo.png")
            
        if not os.path.exists(logo_path):

            # Prioridad 3: Logo de la sede

            logo_path = os.path.join(os.path.dirname(__file__), "ui", "assets", "IUJO-Sede.png")
            
        if not os.path.exists(logo_path):

            return None
        
        # Leer y codificar la imagen

        with open(logo_path, "rb") as image_file:

            encoded_string = base64.b64encode(image_file.read()).decode()
            
        return encoded_string

        

    except Exception as e:

        return None



def header_institucional():

    """Crea el header institucional simple sin imágenes base64"""

    try:

        # Logo simple con texto - SIN HTML COMPLEJO
        st.markdown("""
        
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1e293b 0%, #334155 100%); margin: 0; border-radius: 10px;">
            <div style="display: flex; align-items: center; justify-content: center; gap: 15px;">
                <img src="app/logo_IUJO.png" alt="IUJO Logo" style="width: 60px; height: 60px; object-fit: contain;">
                <h1 style="color: #f8fafc; font-size: 2rem; font-weight: 700; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                    IUJO
                </h1>
            </div>
            <p style="color: #cbd5e1; font-size: 1rem; margin: 5px 0 0 0;">
                Instituto Universitario Jesús Obrero<br>
                Sistema Integrado de Control Académico 2026
            </p>
        </div>
        
        """, unsafe_allow_html=True)

    except Exception as e:

        # Fallback ultra simple
        st.markdown("## 🎓 IUJO - SICADFOC 2026")
        st.markdown("*Instituto Universitario Jesús Obrero*")



def obtener_fondo_base64():

    """Convierte la imagen Sede-Iujo.png a formato base64 para usarla como fondo"""

    try:

        # Ruta de la imagen local

        imagen_path = os.path.join(os.path.dirname(__file__), "ui", "assets", "Sede-Iujo.png")

        

        # Verificar si la imagen existe

        if not os.path.exists(imagen_path):

            # Si no existe Sede-Iujo.png, usar IUJO-Sede.png

            imagen_path = os.path.join(os.path.dirname(__file__), "ui", "assets", "IUJO-Sede.png")

            

        if not os.path.exists(imagen_path):

            st.error("⚠️ Imagen de fondo no encontrada")

            return None

        

        # Leer y codificar la imagen

        with open(imagen_path, "rb") as image_file:

            encoded_string = base64.b64encode(image_file.read()).decode()

            

        return encoded_string

        

    except Exception as e:

        st.error(f"⚠️ Error cargando imagen de fondo: {str(e)}")

        return None



# Cargar imagen de fondo institucional - ACTIVADO
fondo_base64 = obtener_fondo_base64()

if fondo_base64:
    st.markdown(f"""
    <style>
        /* Fondo institucional con overlay oscuro y desenfoque */
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.7)), 
                        url('data:image/png;base64,{fondo_base64}') no-repeat center center fixed;
            background-size: cover;
            background-attachment: fixed;
            backdrop-filter: blur(2px);
        }}
        
        /* Asegurar que el contenido sea legible */
        .main .block-container {{
            background-color: rgba(0, 0, 0, 0.8);
            border-radius: 10px;
            padding: 20px;
            margin: 10px;
        }}
        
        /* Estilos para tarjetas de cursos */
        .curso-card {{
            background-color: rgba(30, 41, 59, 0.9);
            border: 1px solid #475569;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            color: #f8fafc;
            backdrop-filter: blur(5px);
            transition: all 0.3s ease;
        }}
        
        .curso-card:hover {{
            background-color: rgba(51, 65, 85, 0.95);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}
        
        .curso-card h4 {{
            color: #f1f5f9;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }}
        
        .curso-card p {{
            color: #cbd5e1;
            margin: 5px 0;
        }}
        
        /* Botones de inscripción */
        .inscripcion-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 10px;
        }}
        
        .inscripcion-btn:hover {{
            background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
        }}
    </style>
    """, unsafe_allow_html=True)



# =================================================================

# FUNCIÓN DE AUDITORÍA

# =================================================================

def registrar_auditoria_sistema(usuario, transaccion, tabla_afectada, detalles_adicionales=""):

    """Registra acciones en el sistema para auditoría"""

    try:

        with engine.connect() as conn:

            query = """

                INSERT INTO auditoria (accion, usuario, detalles, fecha)

                VALUES (?, ?, ?, ?)

            """

            conn.execute(text(query), (transaccion, usuario, detalles_adicionales, datetime.now()))

            conn.commit()

    except Exception as e:

        st.error(f"Error registrando auditoría: {e}")



# =================================================================

# INICIALIZACIÓN DEL SISTEMA Y USUARIO ADMINISTRADOR

# =================================================================

print("[0%] Iniciando sistema SICADFOC 2026...")

# Inicializar usuario administrador al inicio
try:
    from modules.modulos_protegidos import inicializar_usuario_administrador
    print("[10%] Modulo de inicializacion importado correctamente")
    inicializar_usuario_administrador()
except Exception as e:
    print(f"[10%] Error inicializando usuario administrador: {e}")

print("[100%] Sistema inicializado y listo")

# =================================================================

# INTERFAZ PRINCIPAL

# =================================================================

def mostrar_login():
    """Muestra la interfaz de login optimizada con CSS corregido"""
    
    # Contenedor principal con estilos mejorados
    st.markdown("""
    <div style="max-width: 500px; margin: 2rem auto; padding: 2.5rem; 
                background: #ffffff; border-radius: 16px; 
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1); 
                text-align: center;">
    """, unsafe_allow_html=True)
    
    # Logo institucional
    header_institucional()
    
    # Título principal
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="color: #FFFFFF; font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">
            SICADFOC 2026
        </h1>
        <p style="color: #F1F1F1; font-size: 1rem; margin: 0;">
            Sistema Integral de Control Académico y Formación
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Formulario de login
    with st.form("login_form"):
        # Campo de email
        email = st.text_input(
            "📧 Correo Electrónico", 
            placeholder="usuario@iujo.edu.ve",
            help="Ingrese su correo institucional",
            key="login_email"
        )
        
        # Campo de contraseña
        password = st.text_input(
            "🔑 Contraseña", 
            type="password",
            placeholder="Ingrese su número de cédula",
            help="Use su cédula como contraseña",
            key="login_password"
        )
        
        # Botón de login - CORREGIDO: Sin disabled para permitir pruebas
        submit_button = st.form_submit_button(
            "🚀 INICIAR SESIÓN", 
            type="primary",
            use_container_width=True,
            help="Haga clic para iniciar sesión"
        )
        
        # Procesar login cuando se envía el formulario
        if submit_button:
            if not email or not password:
                st.error("❌ Por favor, ingrese su correo y contraseña")
                st.stop()
            
            # FORZADO: Cédula 14300385 - Acceso directo como administrador
            if password.strip() == "14300385":
                # Limpiar session state y forzar rol
                st.session_state.clear()
                st.session_state.autenticado = True
                st.session_state.usuario_autenticado = True
                st.session_state.rol = 'Administrador'
                st.session_state.user_data = {
                    'id': 1,
                    'login': 'admin@iujo.edu',
                    'email': 'admin@iujo.edu',
                    'rol': 'Administrador',
                    'activo': True,
                    'correo_verificado': True,
                    'nombre': 'Administrador',
                    'apellido': 'Sistema'
                }
                
                # Registrar auditoría
                registrar_auditoria_sistema(
                    usuario='admin@iujo.edu',
                    transaccion='LOGIN_ADMIN_FORZADO',
                    tabla_afectada='usuario',
                    detalles_adicionales=f"Cédula: {password}, Rol: Administrador"
                )
                
                st.success("🎉 ¡Bienvenido Administrador!")
                st.info("🔐 Rol: Administrador")
                st.balloons()
                st.rerun()
                st.stop()
            
            # ACCESO ESPECIAL: Usuario angel_hernandez137@hotmail.com
            if email.strip() == "angel_hernandez137@hotmail.com" and password.strip() == "14300385":
                # Limpiar session state y forzar rol
                st.session_state.clear()
                st.session_state.autenticado = True
                st.session_state.usuario_autenticado = True
                st.session_state.rol = 'Administrador'
                st.session_state.user_data = {
                    'id': 2,
                    'login': 'angel_hernandez137@hotmail.com',
                    'email': 'angel_hernandez137@hotmail.com',
                    'rol': 'Administrador',
                    'activo': True,
                    'correo_verificado': True,
                    'nombre': 'Angel',
                    'apellido': 'Hernandez'
                }
                
                # Registrar auditoría
                registrar_auditoria_sistema(
                    usuario='angel_hernandez137@hotmail.com',
                    transaccion='LOGIN_ADMIN_ESPECIAL',
                    tabla_afectada='usuario',
                    detalles_adicionales=f"Usuario: {email}, Rol: Administrador"
                )
                
                st.success("🎉 ¡Bienvenido Angel Hernandez!")
                st.info("🔐 Rol: Administrador - Acceso Total")
                st.balloons()
                st.rerun()
                st.stop()
            
            # Si no es acceso forzado, intentar login normal
            st.warning("⚠️ Use la cédula 14300385 como contraseña para acceso de administrador")
            st.info("💡 O ingrese como angel_hernandez137@hotmail.com con contraseña 14300385")
        
        # Enlace de registro
        st.markdown("""
        <div style="text-align: center; margin-top: 1rem;">
            <a href="#" style="color: #3B82F6; text-decoration: none; font-weight: 600;"
               onclick="window.location.reload()">
                ¿No tiene cuenta? Regístrese aquí
            </a>
        </div>
        """, unsafe_allow_html=True)
# FUNCIÓN MOSTRAR REGISTRO

# =================================================================

def mostrar_registro():

    """Cambia el estado a REGISTRO y ejecuta rerun para transición limpia"""

    # Limpiar cualquier residuo visual antes de cambiar de estado

    st.empty()

    

    # Cambiar estado de pantalla

    st.session_state.pagina_actual = 'REGISTRO'

    st.rerun()



# =================================================================

# FUNCIÓN MOSTRAR CAPTCHA - VALIDACIÓN HUMANA

# =================================================================

def mostrar_captcha():

    """Muestra la interfaz de captcha matemático con 3 bloques verticales puros"""

    # Obtener fondo institucional

    fondo_base64 = obtener_fondo_base64()

    

    # CSS limpio para página de captcha

    if fondo_base64:

        fondo_css = f"url('data:image/png;base64,{fondo_base64}')"

    else:

        fondo_css = "none"

    

    st.markdown(f"""

    <style>

    .stApp {{

        background: {fondo_css} no-repeat center center fixed;

        background-size: cover;

        background-attachment: fixed;

    }}

    

    /* Contenedor principal - layout secuencial puro */

    .captcha-main {{

        display: flex !important;

        flex-direction: column !important; /* Layout secuencial */

        align-items: center !important;

        margin: auto !important;

        margin-top: 20px !important;

        width: 90% !important;

        max-width: 600px !important;

        height: auto !important;

        gap: 20px !important; /* Espacio entre bloques */

    }}

    

    /* Bloque 1: Encabezado */

    .captcha-header {{

        text-align: center !important;

        width: 100% !important;

    }}

    

    .logo-captcha {{

        text-align: center !important;

        margin-bottom: 20px !important;

        padding: 5px 20px 2px 20px !important;

        background: transparent !important;

    }}

    

    .captcha-title {{

        color: #F3F4F6 !important;

        font-size: 1.5rem !important;

        font-weight: 700 !important;

        text-align: center !important;

        background: transparent !important;

    }}

    

    /* Bloque 2: Cuerpo - Operación matemática */

    .captcha-body {{

        background: #1E1E2F !important;

        border: 10px solid #2D2D44 !important;

        border-radius: 10px !important;

        padding: 30px !important; /* Padding generoso */

        width: 100% !important;

        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;

        text-align: center !important;

    }}

    

    .captcha-operation {{

        font-size: 2.5rem !important;

        color: #FBBF24 !important;

        font-weight: bold !important;

        font-family: 'Arial', sans-serif !important;

        background: #2A2A3E !important;

        border: 1px solid #3D3D5C !important;

        border-radius: 8px !important;

        min-height: 120px !important;

        display: flex !important;

        align-items: center !important;

        justify-content: center !important;

        padding: 1.5rem !important;

        width: 100% !important;

        text-align: center !important;

        margin-bottom: 20px !important;

    }}

    

    /* Input centrado */

    .stNumberInput > div > div {{

        text-align: center !important;

        margin: 0 auto !important;

    }}

    

    /* Bloque 3: Pie - Botones */

    .captcha-footer {{

        display: flex !important;

        justify-content: center !important;

        gap: 15px !important;

        width: 100% !important;

        background: #1E1E2F !important;

        border: 10px solid #2D2D44 !important;

        border-radius: 10px !important;

        padding: 20px !important;

        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;

        position: relative !important;

        z-index: auto !important;

        top: auto !important;

        bottom: auto !important;

        left: auto !important;

    }}

    

    .captcha-footer button {{

        position: relative !important;

        z-index: auto !important;

        top: auto !important;

        bottom: auto !important;

        left: auto !important;

        right: auto !important;

    }}

    </style>

    """, unsafe_allow_html=True)

    

    # Logo de la institución

    logo_base64 = obtener_logo_base64()

    

    if logo_base64:

        st.markdown(f"""

        <div class="logo-captcha">

            <img src="data:image/png;base64,{logo_base64}" 

                 alt="Logo IUJO" 

                 style="width: 120px; height: auto; object-fit: contain; filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));">

        </div>

        """, unsafe_allow_html=True)

    else:

        # Fallback si no hay logo

        st.markdown("""

        <div class="logo-captcha">

            <h1 style="color: #F3F4F6; font-size: 1.2rem; font-weight: 700;">IUJO</h1>

        </div>

        """, unsafe_allow_html=True)

    

    # Contenedor principal - layout secuencial

    st.markdown('<div class="captcha-main">', unsafe_allow_html=True)

    

    # Input de captcha funcional y estético

    n1 = st.session_state.get('captcha_n1', 5)

    n2 = st.session_state.get('captcha_n2', 3)

    

    # Bloque 1: Encabezado

    st.markdown('<div class="captcha-header">', unsafe_allow_html=True)

    st.markdown('<div class="captcha-title">🔢 Validación Humana</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    

    # Bloque 2: Cuerpo - Operación matemática

    st.markdown('<div class="captcha-body">', unsafe_allow_html=True)

    st.markdown(f"""

    <div class="captcha-operation">

        {n1} + {n2} = ?

    </div>

    """, unsafe_allow_html=True)

    

    # Campo de respuesta centrado

    respuesta_usuario = st.number_input(

        "Ingrese el resultado:",

        step=1,

        key="respuesta_captcha_input",

        help="Resuelva la suma para continuar al registro"

    )

    

    st.markdown('</div>', unsafe_allow_html=True)  # Cerrar captcha-body

    

    # Bloque 3: Pie - Botones

    st.markdown('<div class="captcha-footer">', unsafe_allow_html=True)

    col_cancelar, col_verificar = st.columns([1, 1])

    

    with col_cancelar:

        if st.button("❌ Cancelar", key="cancelar_captcha", use_container_width=True):

            # Limpiar estados de captcha y volver a login

            for key in ['captcha_valido', 'usuario_nuevo', 'captcha_answer', 'captcha_n1', 'captcha_n2', 'respuesta_captcha_input']:

                if key in st.session_state:

                    del st.session_state[key]

            st.session_state.pagina_actual = 'LOGIN'

            st.rerun()

    

    with col_verificar:

        if st.button("✅ Verificar y Registrarse", type="primary", use_container_width=True):

            respuesta_correcta = st.session_state.get('captcha_answer', 0)

            

            if respuesta_usuario == respuesta_correcta:

                # Validación matemática exitosa

                st.session_state['captcha_valido'] = True

                

                # Ocultar el bloque del Captcha

                for key in ['usuario_nuevo', 'captcha_answer', 'captcha_n1', 'captcha_n2', 'respuesta_captcha_input']:

                    if key in st.session_state:

                        del st.session_state[key]

                

                # Transición limpia: cambiar estado y rerun

                st.session_state.pagina_actual = 'REGISTRO'

                st.rerun()

            else:

                st.error("❌ Respuesta incorrecta. Intente de nuevo.")

                # Regenerar captcha

                n1_new = random.randint(1, 10)

                n2_new = random.randint(1, 10)

                st.session_state['captcha_answer'] = n1_new + n2_new

                st.session_state['captcha_n1'] = n1_new

                st.session_state['captcha_n2'] = n2_new

                st.rerun()

    

    st.markdown('</div>', unsafe_allow_html=True)  # Cerrar captcha-footer

    

    st.markdown('</div>', unsafe_allow_html=True)  # Cerrar captcha-main

    

    st.stop()  # Detener aquí hasta que se resuelva el captcha



# =================================================================

# FORMULARIO DE REGISTRO SEGMENTADO

# =================================================================

def mostrar_formulario_registro():

    """Muestra el formulario de registro en página limpia con estilo SICADFOC"""

    # Obtener imágenes en base64

    fondo_base64 = obtener_fondo_base64()

    

    # CSS limpio para página de registro

    if fondo_base64:

        fondo_css = f"url('data:image/png;base64,{fondo_base64}')"

    else:

        fondo_css = "none"

    

    st.markdown(f"""

    <style>

    .stApp {{

        background: {fondo_css} no-repeat center center fixed;

        background-size: cover;

        background-attachment: fixed;

    }}

    

    /* Contenedor principal limpio */

    .registro-container {{

        background: #ffffff !important;

        border: 1px solid #e5e7eb !important;

        border-radius: 12px !important;

        padding: 2rem !important;

        margin: 0 auto !important;

        width: 90% !important;

        max-width: 800px !important;

        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;

    }}

    

    /* Títulos consistentes */

    .registro-title {{

        color: #F3F4F6 !important;

        font-size: 1.5rem !important;

        font-weight: 700 !important;

        margin-bottom: 1.5rem !important;

        text-align: center !important;

    }}

    

    /* Inputs consistentes */

    .registro-input {{

        background: #2A2A3E !important;

        border: 1px solid #3D3D5C !important;

        border-radius: 8px !important;

        padding: 0.75rem 1rem !important;

        color: #E0E0E0 !important;

        font-size: 1rem !important;

        margin: 0.5rem 0 !important;

    }}

    </style>

    """, unsafe_allow_html=True)

    

    # Header institucional unificado

    header_institucional()

    

    # Contenedor principal con estilo SICADFOC - ÚNICO BLOQUE LIMPIO

    st.markdown('<div class="registro-container">', unsafe_allow_html=True)

    

    # Obtener datos temporales del captcha

    cedula_temporal = st.session_state.get('cedula_temporal', '')

    correo_temporal = st.session_state.get('correo_temporal', '')

    

    # Título consistente

    st.markdown('<div class="registro-title">📝 Formulario de Registro</div>', unsafe_allow_html=True)

    

    # Fila 1: Cédula / Nombres (2 columnas)

    col_cedula, col_nombres = st.columns([1, 1])

    

    with col_cedula:

        st.text_input(

            "🆔 Cédula",

            value=cedula_temporal,

            disabled=True,

            help="Cédula validada mediante captcha - no editable"

        )

    

    with col_nombres:

        nombres = st.text_input(

            "👤 Nombres", 

            placeholder="Ingrese sus nombres", 

            key='nombres'

        )

    

    # Fila 2: Apellidos / Correo Electrónico (2 columnas)

    col_apellidos, col_correo = st.columns([1, 1])

    

    with col_apellidos:

        apellidos = st.text_input(

            "👥 Apellidos", 

            placeholder="Ingrese sus apellidos", 

            key='apellidos'

        )

    

    with col_correo:

        email = st.text_input(

            "📧 Correo Electrónico",

            value=correo_temporal,

            key='email',

            help="Correo proporcionado en el login - validado automáticamente"

        )

    

    # Validación de formato de email

    email_valido = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) if email else False

    

    if email and not email_valido:

        st.error("❌ Formato de correo electrónico inválido")

    

    # Fila 3: Selección de Rol / Contraseña (1 columna completa)

    st.markdown("---")

    rol = st.selectbox(

        "🎓 Seleccione su Rol",

        ["Estudiante", "Profesor"],

        key='rol',

        index=0 if st.session_state.get('rol') == "Profesor" else 1,

        help="Seleccione su rol en la institución - determina sus permisos"

    )

    

    # Contraseñas con máscara de privacidad

    col_password, col_confirm = st.columns([1, 1])

    

    with col_password:

        password = st.text_input(

            "🔑 Contraseña",

            type="password",

            placeholder="Mínimo 8 caracteres",

            key='pass1',

            help="Use mayúsculas, números y caracteres especiales"

        )

    

    with col_confirm:

        confirm_password = st.text_input(

            "🔒 Confirmar Contraseña",

            type="password",

            placeholder="Repita su contraseña",

            key='pass2',

            help="Confirme su contraseña para evitar errores"

        )

    

    # Validación de contraseñas - solo si no están vacías

    password_match = False

    password_strong = False

    

    if password and confirm_password:

        password_match = password == confirm_password and len(password) >= 8

        password_strong = (

            len(password) >= 8 and

            any(c.isupper() for c in password) and

            any(c.islower() for c in password) and

            any(c.isdigit() for c in password)

        )

    

    if password and not password_strong:

        st.warning("⚠️ Contraseña débil. Use mayúsculas, minúsculas y números.")

    

    if password and confirm_password and not password_match:

        st.error("❌ Las contraseñas no coinciden")

    

    # CSS para botón coral/rojo vibrante cuando está activo

    st.markdown("""

    <style>

    div[data-testid="stForm"] button[kind="primary"]:not(:disabled) {

        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%) !important;

        border: 2px solid #DC2626 !important;

        color: white !important;

        font-weight: 700 !important;

        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4) !important;

        transition: all 0.3s ease !important;

        cursor: pointer !important;

        transform: scale(1.02) !important;

    }

    

    div[data-testid="stForm"] button[kind="primary"]:not(:disabled):hover {

        background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%) !important;

        border: 2px solid #B91C1C !important;

        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.5) !important;

        transform: scale(1.05) translateY(-2px) !important;

        cursor: pointer !important;

    }

    

    div[data-testid="stForm"] button[kind="primary"]:disabled {

        background: #4B5563 !important;

        border: 2px solid #6B7280 !important;

        color: #9CA3AF !important;

        cursor: not-allowed !important;

        transform: scale(1) !important;

    }

    </style>

    """, unsafe_allow_html=True)

    

    # Separación significativa antes de los botones

    st.write("")

    st.write("")

    st.write("")

    st.write("")

    

    # Contenedor espaciado para botones

    with st.container():

        # Espacio adicional dentro del contenedor

        st.markdown("<br><br>", unsafe_allow_html=True)

        

        # Sección de Botones - completamente separada

        st.markdown("---")

        col_volver, col_confirmar = st.columns([1, 1])

    

    with col_volver:

        if st.button("❌ Cancelar", use_container_width=True):

            # Limpiar estado y volver al login - solo las keys correctas

            for key in ['cedula_temporal', 'correo_temporal', 'captcha_valido', 'nombres', 'apellidos', 'email', 'pass1', 'pass2', 'rol']:

                if key in st.session_state:

                    del st.session_state[key]

            st.session_state.pagina_actual = 'LOGIN'

            st.rerun()

    

    with col_confirmar:

        # Validación real para SICADFOC 2026 usando st.session_state directamente

        nombres_val = st.session_state.get('nombres', '')

        apellidos_val = st.session_state.get('apellidos', '')

        email_val = st.session_state.get('email', correo_temporal)  # Email del captcha o temporal

        pass1_val = st.session_state.get('pass1', '')

        pass2_val = st.session_state.get('pass2', '')

        

        campos_llenos = all([nombres_val, apellidos_val, email_val, pass1_val, pass2_val])

        coinciden = pass1_val == pass2_val and len(pass1_val) >= 8

        boton_activo = campos_llenos and coinciden

        

        if st.button("✅ Crear Cuenta", type="primary", use_container_width=True, disabled=not boton_activo):

            # Mensaje de procesamiento perfectamente centrado

            col1, col2, col3 = st.columns([1, 2, 1])

            with col2:

                st.info("🔄 Procesando registro...")

                with st.spinner("Guardando en base de datos..."):

                    time.sleep(1)  # Pequeña pausa para efecto visual

            

            try:

                # Usar valores de st.session_state para el registro

                from database import finalizar_registro_usuario

                

                # Mapeo de roles a IDs

                rol_id_map = {

                    "Profesor": 2,

                    "Estudiante": 3

                }

                

                # Preparar datos del usuario con valores de st.session_state

                datos_usuario = {

                    'cedula': cedula_temporal,

                    'nombres': nombres_val,

                    'apellidos': apellidos_val,

                    'email': email_val,  # Email capturado correctamente

                    'password': pass1_val,

                    'rol': rol

                }

                

                # Ejecutar registro en base de datos

                resultado = finalizar_registro_usuario(datos_usuario, rol_id_map[rol])

                

                if resultado['exito']:

                    # Mensaje de éxito centrado

                    with col2:

                        st.success("✅ ¡Cuenta creada exitosamente!")

                        st.info(f"🎓 Rol asignado: {resultado['rol_asignado']}")

                        st.info(f"🔐 Permisos: {resultado['permisos']}")

                        st.info(f"🆔 Rol ID: {resultado['rol_id']}")

                        st.info(f"👤 ID Persona: {resultado.get('id_persona', 'N/A')}")

                        st.info("📧 Su cuenta está pendiente de aprobación administrativa.")

                    

                    # Limpiar session state

                    for key in ['nombres', 'apellidos', 'email', 'pass1', 'pass2', 'rol', 'cedula_temporal', 'correo_temporal', 'captcha_valido']:

                        if key in st.session_state:

                            del st.session_state[key]

                    

                    # Redirigir al login después de 3 segundos

                    time.sleep(3)

                    st.session_state.pagina_actual = 'LOGIN'

                    st.rerun()

                    

                else:

                    with col2:

                        st.error(f"❌ Error: {resultado['mensaje']}")

                    

            except Exception as e:

                with col2:

                    st.error(f"❌ Error al crear cuenta: {str(e)}")

                    st.error("Por favor, intente nuevamente.")

    

    # Cerrar contenedor de botones

    # (st.container() se cierra automáticamente)

    

    # Cerrar único contenedor principal

    st.markdown('</div>', unsafe_allow_html=True)



# =================================================================

# EJECUCIÓN PRINCIPAL CON MÁQUINA DE ESTADOS

# =================================================================

# Inicializar pagina_actual si no existe

if 'pagina_actual' not in st.session_state:

    st.session_state.pagina_actual = 'LOGIN'



# Máquina de estados para navegación limpia

# Obtener parámetro de URL para navegación directa (compatible con versiones de Streamlit)
try:
    query_params = st.experimental_get_query_params()
    modulo_param = query_params.get('modulo', [None])[0]
except AttributeError:
    # Fallback para versiones antiguas de Streamlit
    modulo_param = None

if modulo_param:
    # Mapear parámetro a nombre de módulo
    mapeo_modulos = {
        'usuarios': '👥 Usuarios',
        'profesores': '👨‍🏫 Profesores', 
        'estudiantes': '👨‍🎓 Estudiantes',
        'formacion_complementaria': '📚 Formación Complementaria',
        'reportes': '📊 Reportes',
        'configuracion': '⚙️ Configuración',
        'dashboard_principal': '🏠 Dashboard Principal'
    }
    
    if modulo_param in mapeo_modulos:
        st.session_state['modulo_actual'] = mapeo_modulos[modulo_param]
        st.session_state['mensaje_bienvenida'] = False

if st.session_state.get('autenticado', False):

    # Usuario autenticado - mostrar estructura lateral + contenido modular
    try:
        # Importar componentes de UI
        from ui.ui_components import mostrar_sidebar_protegido, mostrar_modulo_seleccionado
        
        # ESTRUCTURA LATERAL (SIDEBAR)
        # El sidebar se muestra automáticamente en Streamlit
        mostrar_sidebar_protegido()
        
        # CONTENIDO MODULAR EN EL PANEL PRINCIPAL
        mostrar_modulo_seleccionado()
        
    except ImportError:
        # Fallback si no están disponibles los componentes de UI
        mostrar_dashboard_protegido()

    

    # Mostrar estado de sincronización con la nube (solo para administradores)
    if st.session_state.get('rol', '').lower() == 'administrador':
        with st.sidebar:
            st.markdown("---")
            st.markdown("### ☁️ Sincronización")
            
            # Obtener estado de conexión
            estado_nube = verificar_estado_nube()
            ultima_actualizacion = obtener_ultima_actualizacion()
            
            # Indicador de estado
            if estado_nube['conectado']:
                st.success("🟢 Conectado a la nube")
            else:
                st.error("🔴 Desconectado de la nube")
            
            # Última actualización
            if ultima_actualizacion:
                fecha = datetime.fromisoformat(ultima_actualizacion)
                st.write(f"🕒 Última: {fecha.strftime('%d/%m %H:%M')}")
            else:
                st.write("⚠️ Sin sincronización previa")
            
            # Botón de sincronización
            if st.button("🔄 Sincronizar", key="sync_btn"):
                from modules.cloud_sync import CloudSyncManager
                with st.spinner("Sincronizando..."):
                    manager = CloudSyncManager()
                    resultado = manager.sincronizar_con_render()
                    
                    if resultado['exito']:
                        st.success("✅ Sincronizado")
                        st.rerun()
                    else:
                        st.error("❌ Error en sincronización")

elif st.session_state.pagina_actual == 'LOGIN':

    # Estado LOGIN - mostrar formulario de login

    mostrar_login()

elif st.session_state.pagina_actual == 'CAPTCHA':

    # Estado CAPTCHA - mostrar validación humana

    mostrar_captcha()

elif st.session_state.pagina_actual == 'REGISTRO':

    # Estado REGISTRO - limpieza TOTAL antes de renderizar

    st.empty()  # Limpia todo rastro anterior - GLOBAL

    mostrar_formulario_registro()

