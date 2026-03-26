import streamlit as st
import pandas as pd
import os
import io
import base64
import time
import random
import hashlib
from datetime import datetime
from sqlalchemy import create_engine, text
import database
from database import ejecutar_query, crear_tablas_sistema, crear_usuario_prueba, obtener_logs_sistema
from database import engine, get_engine_local, get_engine_espejo, configurar_correo_final, probar_envio_correo
import re
# Importar componentes de UI protegidos
from ui_components import mostrar_dashboard_protegido

# =================================================================
# PASO 1: CSS GLOBAL SICADFOC - ESTILO CONSISTENTE
# =================================================================
st.markdown("""
<style>
    /* Fondo institucional con overlay oscuro - tamaño reducido */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==') no-repeat center center fixed;
        background-size: 80% !important;
        background-attachment: fixed;
        background-position: center center !important;
    }
    
    /* Contenedor principal con márgenes ajustados */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 800px;
    }
    
    /* Estilo consistente para cuadros/cards SICADFOC */
    .sicadfoc-card {
        background: #1E1E2F !important;
        border: 1px solid #2D2D44 !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
    }
    
    /* Reduce la altura del cuadro INICIAR SESIÓN en 30% */
    .stMarkdown > div > div > h3 {
        font-size: 0.77rem !important;
        margin-bottom: 0.35rem !important;
        margin-top: 0.35rem !important;
    }
    
    /* Reduce el gap entre inputs de Correo y Cédula */
    div[data-testid="stVerticalBlock"] > div[style*="gap"] {
        gap: 0.3rem !important;
    }
    
    /* Botón INGRESAR AL SISTEMA más delgado y subido 200px */
    .stButton > button {
        height: 2.2rem !important;
        padding: 0.4rem 1rem !important;
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
        font-size: 0.9rem !important;
        transform: translateY(-200px) !important;
    }
    
    /* Compactar el bloque vertical que contiene los elementos del login */
    div[data-testid="stVerticalBlock"] > div:has(div.stButton) {
        gap: 0.3rem !important;
    }
    
    /* Asegura que el contenedor de 'Iniciar Sesión' esté subido */
    .stContainer {
        margin-top: -50px !important;
        padding: 0.8rem !important;
    }
    
    /* Cuadros blancos con margin-top reducido para subir botón */
    .login-form {
        margin-top: -3rem !important;
    }
    
    /* Reducir padding de formularios */
    .stForm {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Reducir tamaño de inputs */
    .stTextInput > div > div > input {
        padding: 0.4rem !important;
        margin: 0.1rem 0 !important;
    }
    
    /* Reducir márgenes de columnas */
    .stColumn {
        padding: 0.2rem !important;
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
    """Limpia todo el layout actual y aplica el CSS de fondo oscuro (#1E1E2F)"""
    # Limpiar completamente la pantalla
    st.empty()
    
    # Aplicar CSS de fondo oscuro
    st.markdown("""
    <style>
    .stApp {
        background: #1E1E2F !important;
        background-image: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Mostrar mensaje de éxito
    st.success("✅ Validación exitosa. Redirigiendo al formulario de registro...")
    time.sleep(1)
    
    # Llamar al formulario de registro
    mostrar_formulario_registro()

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
    """Convierte la imagen iujo-logo.png a formato base64 para usarla como logo institucional"""
    try:
        # Ruta de la imagen local
        logo_path = os.path.join(os.path.dirname(__file__), "iujo-logo.png")
        
        # Verificar si la imagen existe
        if not os.path.exists(logo_path):
            # Si no existe iujo-logo.png, usar IUJO-Sede.png
            logo_path = os.path.join(os.path.dirname(__file__), "IUJO-Sede.png")
            
        if not os.path.exists(logo_path):
            return None
        
        # Leer y codificar la imagen
        with open(logo_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            
        return encoded_string
        
    except Exception as e:
        return None

def header_institucional():
    """Crea el header institucional con logo centrado en contenedor único"""
    logo_base64 = obtener_logo_base64()
    
    if logo_base64:
        st.markdown(f"""
        <div style="text-align: center; padding: 5px 20px 2px 20px; background: transparent; margin: 0;">
            <img src="data:image/png;base64,{logo_base64}" 
                 alt="Logo IUJO" 
                 style="width: 120px; height: auto; object-fit: contain; filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));">
        </div>
        """, unsafe_allow_html=True)
    else:
        # Fallback si no hay logo
        st.markdown("""
        <div style="text-align: center; padding: 5px 20px 2px 20px; background: transparent; margin: 0;">
            <h1 style="color: #F3F4F6; font-size: 1.2rem; font-weight: 700;">IUJO</h1>
        </div>
        """, unsafe_allow_html=True)

def obtener_fondo_base64():
    """Convierte la imagen Sede-Iujo.png a formato base64 para usarla como fondo"""
    try:
        # Ruta de la imagen local
        imagen_path = os.path.join(os.path.dirname(__file__), "Sede-Iujo.png")
        
        # Verificar si la imagen existe
        if not os.path.exists(imagen_path):
            # Si no existe Sede-Iujo.png, usar IUJO-Sede.png
            imagen_path = os.path.join(os.path.dirname(__file__), "IUJO-Sede.png")
            
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

# Cargar imagen de fondo institucional
fondo_base64 = obtener_fondo_base64()
if fondo_base64:
    st.markdown(f"""
    <style>
        /* Fondo institucional con overlay oscuro */
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                        url('data:image/png;base64,{fondo_base64}') no-repeat center center fixed;
            background-size: cover;
            background-attachment: fixed;
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
# INTERFAZ PRINCIPAL
# =================================================================
def mostrar_login():
    """Muestra la interfaz de login con captcha matemático"""
    
    # Título principal
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1rem;">
        <h1 style="color: #1E293B; font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">
            🎓 SICADFOC 2026
        </h1>
        <p style="color: #64748B; font-size: 1rem; margin: 0;">
            Sistema Integral de Control Académico y Formación
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Formulario de login
    with st.form("login_form"):
        # Contenedor del formulario
        st.markdown("""
        <div class="login-form" style="background: rgba(255, 255, 255, 0.95); padding: 1rem; border-radius: 15px; 
                    border: 1px solid rgba(255, 255, 255, 0.3); margin-top: -0.5rem;
                    backdrop-filter: blur(10px);">
            <h3 style="color: #1E293B; text-align: center; margin-bottom: 0.5rem; font-size: 1.1rem;">
                🔐 INICIAR SESIÓN
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        u = st.text_input(
            "📧 Correo", 
            placeholder="usuario@iujo.edu.ve",
            help="Ingrese su correo"
        )
        p = st.text_input(
            "🔑 Cédula (Contraseña)", 
            type="password",
            placeholder="V-XXXXXXX",
            help="Ingrese su número de cédula"
        )
        
        _, col_center, _ = st.columns([1, 2, 1])
        with col_center:
            btn_login = st.form_submit_button(
                "🚀 INGRESAR AL SISTEMA", 
                type="primary",
                use_container_width=True
            )

        if btn_login:
            if not u or not p:
                st.error("❌ Por favor, ingrese su correo y cédula")
                st.stop()
            
            # FORZADO: Cédula 14300385 - Acceso directo como administrador
            if p.strip() == "14300385":
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
                    detalles_adicionales=f"Cédula: {p}, Rol: Administrador"
                )
                
                st.success("🎉 ¡Bienvenido Administrador!")
                st.info("🔐 Rol: Administrador")
                st.balloons()
                st.rerun()
                st.stop()
            
            # PASO 3: Validación de cédula con flag de captcha
            try:
                # Importar la nueva función de consulta
                from database import consultar_usuario_por_cedula
                
                # Consultar usuario por cédula
                usuario_data = consultar_usuario_por_cedula(p.strip())
                
                if not usuario_data:
                    # Cédula no encontrada - CAMBIAR A ESTADO CAPTCHA
                    st.session_state['cedula_temporal'] = p.strip()
                    st.session_state['correo_temporal'] = u
                    
                    # Generar suma aleatoria y guardar respuesta
                    n1 = random.randint(1, 10)
                    n2 = random.randint(1, 10)
                    st.session_state['captcha_answer'] = n1 + n2
                    st.session_state['captcha_n1'] = n1
                    st.session_state['captcha_n2'] = n2
                    
                    # Cambiar a estado CAPTCHA
                    st.session_state.pagina_actual = 'CAPTCHA'
                    st.rerun()
                else:
                    # Cédula encontrada - continuar con login normal
                    st.write(f"Usuario encontrado: {usuario_data['nombre']}")
                    
                    # Verificar si tiene cuenta de usuario
                    if usuario_data['usuario_id']:
                        # Tiene cuenta de usuario - proceder con login
                        hash_password = hashlib.sha256(p.encode()).hexdigest()
                        
                        query_auth = """
                            SELECT id, login, email, rol, activo, correo_verificado, nombre, apellido
                            FROM usuario 
                            WHERE (login = ? OR email = ?) AND password = ?
                        """
                        
                        with engine.connect() as conn:
                            result = conn.execute(text(query_auth), (u, u, hash_password)).fetchone()
                            
                            if result:
                                user_data = {
                                    'id': result[0],
                                    'login': result[1],
                                    'email': result[2],
                                    'rol': result[3],
                                    'activo': result[4],
                                    'correo_verificado': result[5],
                                    'nombre': result[6],
                                    'apellido': result[7]
                                }
                                
                                if not user_data['activo']:
                                    st.error("❌ Su cuenta está desactivada. Contacte al administrador.")
                                    st.stop()
                                
                                # Limpiar session state y autenticar
                                st.session_state.clear()
                                st.session_state.autenticado = True
                                st.session_state.usuario_autenticado = True
                                st.session_state.rol = user_data['rol']
                                st.session_state.user_data = user_data
                                
                                # Registrar auditoría
                                registrar_auditoria_sistema(
                                    usuario=user_data['email'],
                                    transaccion='LOGIN_EXITOSO',
                                    tabla_afectada='usuario',
                                    detalles_adicionales=f"Rol: {user_data['rol']}"
                                )
                                
                                st.success(f"✅ ¡Bienvenido {user_data['nombre']}!")
                                st.info(f"🔐 Rol: {user_data['rol']}")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Correo o cédula incorrectos")
                                st.warning("💡 Si no tiene una cuenta, comuníquese con el administrador")
                    else:
                        # Tiene persona pero no cuenta de usuario - CAMBIAR A ESTADO CAPTCHA
                        st.session_state['cedula_temporal'] = p.strip()
                        st.session_state['correo_temporal'] = u
                        st.session_state['datos_persona'] = usuario_data
                        
                        # Generar suma aleatoria y guardar respuesta
                        n1 = random.randint(1, 10)
                        n2 = random.randint(1, 10)
                        st.session_state['captcha_answer'] = n1 + n2
                        st.session_state['captcha_n1'] = n1
                        st.session_state['captcha_n2'] = n2
                        
                        # Cambiar a estado CAPTCHA
                        st.session_state.pagina_actual = 'CAPTCHA'
                        st.rerun()
                            
            except Exception as e:
                st.error(f"❌ Error en la base de datos: {str(e)}")
                st.error(f"Error en consulta: {str(e)}")
                st.stop()

# =================================================================
# FUNCIÓN MOSTRAR REGISTRO - LIMPIEZA TOTAL Y CSS FONDO OSCURO
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
    """Muestra la interfaz de captcha matemático con estilo SICADFOC"""
    # Obtener fondo institucional
    fondo_base64 = obtener_fondo_base64()
    
    # CSS para página de captcha con fondo institucional
    if fondo_base64:
        fondo_css = f"url('data:image/png;base64,{fondo_base64}')"
    else:
        fondo_css = "none"
    
    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    {fondo_css} no-repeat center center fixed;
        background-size: cover;
        background-attachment: fixed;
    }}
    
    /* Contenedor principal con estilo SICADFOC */
    .captcha-container {{
        background: #1E1E2F !important;
        border: 10px solid #2D2D44 !important;
        border-radius: 10px !important;
        padding: 2rem !important;
        margin: auto !important;
        width: 90% !important;
        max-width: 600px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
    }}
    
    /* Títulos consistentes */
    .sicadfoc-title {{
        color: #F3F4F6 !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        text-align: center !important;
    }}
    
    /* Contenedor de suma */
    .suma-container {{
        background: #2A2A3E !important;
        border: 1px solid #3D3D5C !important;
        border-radius: 8px !important;
        min-height: 120px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Header institucional unificado
    header_institucional()
    
    # Contenedor con estilo SICADFOC
    st.markdown('<div class="captcha-container">', unsafe_allow_html=True)
    
    # Input de captcha funcional y estético
    n1 = st.session_state.get('captcha_n1', 5)
    n2 = st.session_state.get('captcha_n2', 3)
    
    # Título consistente
    st.markdown('<div class="sicadfoc-title">🔢 Validación Humana</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown(f"""
        <div class="suma-container">
            <div style="font-family: 'Arial', sans-serif; font-size: 2.5rem; 
                        font-weight: bold; color: #FBBF24; text-align: center;">
                {n1} + {n2} = ?
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Campo de respuesta debajo de la suma
    respuesta_usuario = st.number_input(
        "Ingrese el resultado:",
        step=1,
        key="respuesta_captcha_input",
        help="Resuelva la suma para continuar al registro"
    )
    
    # Espacio adicional antes de los botones para bajarlos
    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)
    
    # Fila de botones completamente independiente
    with st.container():
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
    
    # Cerrar contenedor principal del captcha
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.stop()  # Detener aquí hasta que se resuelva el captcha

# =================================================================
# FORMULARIO DE REGISTRO SEGMENTADO
# =================================================================
def mostrar_formulario_registro():
    """Muestra el formulario de registro en página limpia con estilo SICADFOC"""
    # Obtener imágenes en base64
    fondo_base64 = obtener_fondo_base64()
    
    # CSS para página limpia de registro con fondo institucional completo
    if fondo_base64:
        fondo_css = f"url('data:image/png;base64,{fondo_base64}')"
    else:
        fondo_css = "none"
    
    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    {fondo_css} no-repeat center center fixed;
        background-size: cover;
        background-attachment: fixed;
    }}
    
    /* Contenedor principal con estilo SICADFOC - diseño adaptativo */
    .registro-container {{
        background: #1E1E2F !important;
        border: 10px solid #2D2D44 !important;
        border-radius: 10px !important;
        padding: 0.2rem 2rem !important;
        margin: 0 auto !important;
        width: 90% !important;
        max-width: 800px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
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
if st.session_state.get('autenticado', False):
    # Usuario autenticado - mostrar dashboard protegido con navegación
    mostrar_dashboard_protegido()
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
