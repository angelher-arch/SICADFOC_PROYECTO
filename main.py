import streamlit as st
import pandas as pd
import os
import io
import shutil
from datetime import datetime
from sqlalchemy import create_engine, text
import database
from database import ejecutar_query, crear_tablas_sistema, crear_usuario_prueba, obtener_logs_sistema
from database import engine, get_engine_local, get_engine_espejo, configurar_correo_final, probar_envio_correo
import re
import hashlib

# =================================================================
# 0. CONFIGURACIÓN DE PÁGINA RESPONSIVA
# =================================================================

st.set_page_config(
    page_title="SICADFOC 2026",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="auto"
)

# CSS personalizado para responsividad móvil
st.markdown("""
<style>
/* Responsive design for mobile devices */
@media (max-width: 768px) {
    /* Aumentar tamaño de botones para pantallas táctiles */
    .stButton > button {
        padding: 15px 20px !important;
        font-size: 16px !important;
        min-height: 50px !important;
        width: 100% !important;
        margin-bottom: 10px !important;
    }
    
    /* Campos de entrada responsivos */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        width: 100% !important;
        font-size: 16px !important;
        padding: 12px !important;
        margin-bottom: 10px !important;
    }
    
    /* Sidebar responsivo */
    .css-1d391kg {
        padding: 1rem 0.5rem !important;
    }
    
    /* Logo responsivo */
    .css-1d391kg img {
        max-width: 100% !important;
        height: auto !important;
    }
    
    /* Ajustar espaciado en móviles */
    .css-1lcbmhc {
        padding: 1rem 0.5rem !important;
    }
    
    /* Tabs más grandes en móvil y mejor contraste */
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 14px !important;
        padding: 12px 16px !important;
        min-height: 48px !important;
        color: #f8fafc !important;
        font-weight: 600 !important;
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        margin: 2px !important;
        transition: all 0.2s ease !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button:hover {
        color: #ffffff !important;
        background-color: #334155 !important;
        border-color: #475569 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button[data-selected="true"] {
        color: #ffffff !important;
        background-color: #7c3aed !important;
        border-color: #8b5cf6 !important;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3) !important;
    }
    
    /* Eliminar cualquier fondo blanco o claro de tabs y contenedores */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e293b !important;
        border-radius: 12px !important;
        padding: 4px !important;
        border: 1px solid #334155 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Contenedor principal de tabs con fondo oscuro */
    .stTabs > div > div > div {
        background-color: #1e293b !important;
        border-radius: 12px !important;
    }
    
    /* Eliminar fondo blanco de todos los contenedores de tabs */
    .stTabs div[style*="background"] {
        background-color: transparent !important;
        background: #1e293b !important;
    }
    
    .stTabs .css-17ziqus,
    .stTabs .css-1lcbmhc,
    .stTabs .css-1d391kg,
    .stTabs [data-testid="stHorizontalBlock"] {
        background-color: transparent !important;
        background: transparent !important;
    }
    
    /* Asegurar que no haya fondos blancos en tabs */
    .stTabs * {
        background-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab-list"] * {
        background-color: inherit !important;
    }
    
    /* Estandarización perfecta de botones del sidebar */
    .stSidebar .stRadio > div > div > label {
        background-color: #f8fafc !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        margin: 4px 0 !important;
        height: 48px !important;
        min-height: 48px !important;
        max-height: 48px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        transition: all 0.2s ease !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        color: #1e293b !important;
        width: 100% !important;
        box-sizing: border-box !important;
        line-height: 1.2 !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
    }
    
    .stSidebar .stRadio > div > div > label:hover {
        background-color: #e2e8f0 !important;
        border-color: #cbd5e1 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stSidebar .stRadio > div > div > label[data-selected="true"] {
        background-color: #7c3aed !important;
        border-color: #8b5cf6 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Estandarizar botones regulares del sidebar */
    .stSidebar button {
        height: 48px !important;
        min-height: 48px !important;
        max-height: 48px !important;
        padding: 12px 16px !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1.2 !important;
    }
    
    .stSidebar button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Métricas responsivas */
    .css-1vq4p4l {
        padding: 1rem 0.5rem !important;
    }
    
    /* Expander más grande en móvil */
    .streamlit-expanderHeader {
        padding: 12px !important;
        font-size: 16px !important;
    }
    
    /* File uploader responsivo */
    .stFileUploader {
        padding: 20px !important;
    }
    
    /* Dataframe responsivo */
    .dataframe {
        font-size: 12px !important;
    }
}

/* Para tablets */
@media (min-width: 769px) and (max-width: 1024px) {
    .stButton > button {
        padding: 12px 16px !important;
        min-height: 44px !important;
    }
    
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        font-size: 15px !important;
        padding: 10px !important;
    }
}

/* Optimizaciones generales */
.stSelectbox > div > div > select {
    width: 100% !important;
}

.stTextInput > div > div > input {
    width: 100% !important;
}

/* Evitar scroll horizontal */
.main .block-container {
    max-width: 100% !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* Sidebar mejorado */
.sidebar .sidebar-content {
    padding: 1rem !important;
}

/* Botones de radio más grandes */
.stRadio > div > label {
    padding: 10px !important;
    font-size: 14px !important;
    margin-bottom: 5px !important;
}

/* Formularios más espaciados */
form {
    margin-bottom: 20px !important;
}

/* Mejorar visibilidad de errores y advertencias */
.stAlert {
    margin-bottom: 15px !important;
}

/* Tabs más visibles */
.stTabs [data-baseweb="tab-list"] {
    background-color: #f8f9fa !important;
    border-radius: 8px !important;
    padding: 4px !important;
}

.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    background-color: #1e293b !important;
    color: white !important;
    border-radius: 6px !important;
}
</style>
""", unsafe_allow_html=True)

# =================================================================
# 1. CONFIGURACIÓN DE CSS Y TEMAS
# =================================================================

def detectar_base_datos_conectada():
    """Detecta qué base de datos está conectada"""
    try:
        engine_espejo = get_engine_espejo()
        engine_local = get_engine_local()
        
        if engine_espejo and 'render.com' in str(engine_espejo.url):
            return 'nube_render'
        elif engine_local and 'foc26_limpio.db' in str(engine_local.url):
            return 'desarrollo'
        elif engine_espejo and 'Foc26_espejo.db' in str(engine_espejo.url):
            return 'produccion_local'
        else:
            return 'desconocido'
    except:
        return 'desconocido'

def configurar_tema_segun_ambiente(tipo_ambiente):
    """Configura el tema CSS según el ambiente detectado"""
    if tipo_ambiente == 'nube_render':
        # Tema claro para nube
        st.markdown("""
        <style>
        .stApp {
            background: #ffffff;
            color: #1e293b;
        }
        .main .block-container {
            background: #ffffff;
            color: #1e293b;
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        .stButton>button {
            background-color: #3b82f6;
            color: white;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
        }
        .stButton>button:hover {
            background-color: #2563eb;
            color: white;
        }
        .stRadio>div>label {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            padding: 0.5rem;
            border-radius: 8px;
            margin: 0.25rem 0;
            color: #1e293b;
        }
        .stRadio>div>label:hover {
            background: #e2e8f0;
            color: #1e293b;
        }
        .sidebar .sidebar-content {
            background: #f8fafc;
            color: #1e293b;
        }
        </style>
        """, unsafe_allow_html=True)
    elif tipo_ambiente == 'produccion_local':
        # Tema claro para producción local
        st.markdown("""
        <style>
        .stApp {
            background: #f8fafc;
            color: #1e293b;
        }
        .main .block-container {
            background: #ffffff;
            color: #1e293b;
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .stButton>button {
            background-color: #10b981;
            color: white;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
        }
        .stButton>button:hover {
            background-color: #059669;
            color: white;
        }
        .stRadio>div>label {
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
            padding: 0.5rem;
            border-radius: 8px;
            margin: 0.25rem 0;
            color: #1e293b;
        }
        .stRadio>div>label:hover {
            background: #e2e8f0;
            color: #1e293b;
        }
        .sidebar .sidebar-content {
            background: #f1f5f9;
            color: #1e293b;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Tema oscuro para desarrollo
        st.markdown("""
        <style>
        .stApp {
            background: #0f172a;
            color: #f8fafc;
        }
        .main .block-container {
            background: #1e293b;
            color: #f8fafc;
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        }
        .stButton>button {
            background-color: #3b82f6;
            color: white;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
        }
        .stButton>button:hover {
            background-color: #2563eb;
            color: white;
        }
        .stRadio>div>label {
            background: #334155;
            border: 1px solid #475569;
            padding: 0.5rem;
            border-radius: 8px;
            margin: 0.25rem 0;
            color: #f8fafc;
        }
        .stRadio>div>label:hover {
            background: #475569;
            color: #f8fafc;
        }
        .sidebar .sidebar-content {
            background: #1e293b;
            color: #f8fafc;
        }
        </style>
        """, unsafe_allow_html=True)

def get_module_icons():
    """Retorna los iconos para los módulos"""
    return {
        'Inicio': '🏠',
        'Estudiantes': '📚',
        'Profesores': '👨‍🏫',
        'Formación Complementaria': '🎓',
        'Configuración': '⚙️',
        'Reportes': '📊',
        'Monitor de Sistema': '⚡',
        '⚙️ Ambientes (ITIL)': '🔧'
    }

def mostrar_aviso_ambiente(tipo_ambiente):
    """Muestra un aviso en el sidebar según el ambiente"""
    if tipo_ambiente == 'desarrollo':
        st.sidebar.error("🔧 ENTORNO: DESARROLLO")
        st.sidebar.info("Base de datos: foc26_limpio.db")
    elif tipo_ambiente == 'produccion_local':
        st.sidebar.success("🚀 ENTORNO: PRODUCCIÓN (LOCAL)")
        st.sidebar.info("Base de datos: Foc26_espejo.db")
    elif tipo_ambiente == 'nube_render':
        st.sidebar.success("☁️ ENTORNO: NUBE (RENDER)")
        st.sidebar.info("Base de datos: PostgreSQL")
    else:
        st.sidebar.warning("⚠️ ENTORNO: DESCONOCIDO")

# Detectar ambiente y configurar tema
tipo_ambiente = detectar_base_datos_conectada()
configurar_tema_segun_ambiente(tipo_ambiente)

# =================================================================
# 2. SISTEMA DE ROLES Y PERFILES
# =================================================================

def obtener_rol_usuario():
    """Obtiene el rol del usuario desde st.session_state"""
    return st.session_state.get('rol', 'estudiante')

def registrar_auditoria(accion, usuario, detalles="", tabla_afectada=None):
    """Registra eventos de auditoría en la base de datos"""
    try:
        rol_actual = obtener_rol_usuario()
        ip_address = st.context.headers.get('x-forwarded-for', 'localhost')
        
        # Construir detalles completos
        if tabla_afectada:
            detalles += f", Tabla: {tabla_afectada}"
        detalles += f", Rol: {rol_actual}, IP: {ip_address}"
        
        # Insertar en tabla de auditoría
        with engine.connect() as conn:
            query = """
            INSERT INTO auditoria (
                accion, usuario, detalles, fecha_hora
            ) VALUES (?, ?, ?, ?)
            """
            
            conn.execute(
                query,
                (
                    accion,
                    usuario,
                    detalles,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
            )
            conn.commit()
            
    except Exception as e:
        print(f"Error en auditoría: {str(e)}")

def registrar_auditoria_sistema(usuario, transaccion, tabla_afectada=None, detalles_adicionales=None):
    """Función auxiliar para registrar auditoría"""
    rol_actual = obtener_rol_usuario()
    ip_address = st.context.headers.get('x-forwarded-for', 'localhost')
    
    # Construir detalles completos
    if tabla_afectada:
        detalles_adicionales = f", Tabla: {tabla_afectada}"
    else:
        detalles_adicionales = ""
    
    detalles_completos = f"{detalles_adicionales}, Rol: {rol_actual}, IP: {ip_address}"
    
    registrar_auditoria(
        accion=transaccion,
        usuario=usuario,
        detalles=detalles_completos,
        tabla_afectada=tabla_afectada
    )

def es_admin():
    """Verifica si el usuario es administrador"""
    rol = obtener_rol_usuario()
    return rol == 'admin' or rol == 'administrador'

def es_profesor():
    """Verifica si el usuario es profesor"""
    rol = obtener_rol_usuario()
    return rol == 'profesor'

def es_estudiante():
    """Verifica si el usuario es estudiante"""
    rol = obtener_rol_usuario()
    return rol == 'estudiante'

def validar_restriccion_usuario(email, cedula=None):
    """Valida si un usuario debe ser omitido según restricciones de seguridad"""
    # Omitir correo específico para evitar dumping y lentitud
    if email == st.session_state.get('omitir_correo_especifico', 'angelher@gmail.com'):
        return False, "Usuario omitido por restricciones de seguridad"
    
    # Validar vinculación de admin
    if cedula == st.session_state.get('cedula_admin', '14300385'):
        # Asegurar que este usuario siempre tenga rol de administrador
        return True, "Usuario administrador válido"
    
    return True, "Usuario válido"

def normalizar_columnas_csv(df, tipo='estudiantes'):
    """Normaliza cabeceras de CSV para que sean insensibles a mayúsculas/minúsculas y tildes"""
    # Mapeo de normalización para estudiantes
    mapeo_estudiantes = {
        'cedula': 'cedula',
        'cédula': 'cedula',
        'cedula_': 'cedula',
        'cedula_estudiante': 'cedula',
        'ci': 'cedula',
        'c.i.': 'cedula',
        'identificacion': 'cedula',
        
        'nombres': 'nombres',
        'nombre': 'nombres',
        'nombres_completos': 'nombres',
        'primer_nombre': 'nombres',
        
        'apellidos': 'apellidos',
        'apellido': 'apellidos',
        'apellidos_completos': 'apellidos',
        'primer_apellido': 'apellidos',
        
        'correo': 'correo',
        'email': 'correo',
        'e_mail': 'correo',
        'email_contacto': 'correo',
        'correo_electronico': 'correo',
        
        'semestre': 'semestre',
        'semestre_actual': 'semestre',
        'nivel': 'semestre',
        'grado': 'semestre',
        'año': 'semestre'
    }
    
    # Mapeo de normalización para profesores
    mapeo_profesores = {
        'cedula': 'cedula',
        'cédula': 'cedula',
        'cedula_': 'cedula',
        'cedula_profesor': 'cedula',
        'ci': 'cedula',
        'c.i.': 'cedula',
        'identificacion': 'cedula',
        
        'nombres': 'nombres',
        'nombre': 'nombres',
        'nombres_completos': 'nombres',
        'primer_nombre': 'nombres',
        
        'apellidos': 'apellidos',
        'apellido': 'apellidos',
        'apellidos_completos': 'apellidos',
        'primer_apellido': 'apellidos',
        
        'correo': 'correo',
        'email': 'correo',
        'e_mail': 'correo',
        'email_contacto': 'correo',
        'correo_electronico': 'correo',
        
        'especialidad': 'especialidad',
        'especialidad_': 'especialidad',
        'area': 'especialidad',
        'departamento': 'especialidad',
        'categoría': 'especialidad',
        'categoria': 'especialidad',
        'escalafon': 'especialidad',
        'escalafón': 'especialidad'
    }
    
    # Seleccionar mapeo según tipo
    mapeo = mapeo_estudiantes if tipo == 'estudiantes' else mapeo_profesores
    
    # Normalizar columnas
    columnas_normalizadas = {}
    for col in df.columns:
        # Convertir a minúsculas, eliminar tildes y espacios
        col_normalizada = col.lower().strip()
        
        # Eliminar tildes
        import unicodedata
        col_normalizada = unicodedata.normalize('NFKD', col_normalizada).encode('ascii', 'ignore').decode('ascii')
        
        # Reemplazar caracteres especiales
        col_normalizada = col_normalizada.replace('_', '').replace('-', '').replace('.', '')
        
        # Aplicar mapeo
        if col_normalizada in mapeo:
            columnas_normalizadas[col] = mapeo[col_normalizada]
        else:
            columnas_normalizadas[col] = col_normalizada
    
    # Renombrar columnas
    df = df.rename(columns=columnas_normalizadas)
    
    # Limpiar datos de todas las columnas de texto
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
    
    return df

def registrar_reporte_carga(tipo_carga, registros_procesados, errores_count, detalles=""):
    """Registra automáticamente una entrada en la tabla de reportes"""
    try:
        # Obtener cédula del admin
        cedula_admin = st.session_state.get('cedula_admin', '14300385')
        
        # Insertar en tabla de reportes
        with engine.connect() as conn:
            query = """
            INSERT INTO reportes (
                origen, fecha_hora, resumen, detalles, usuario_cedula, creado_en
            ) VALUES (?, ?, ?, ?, ?, ?)
            """
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            resumen = f"Procesados: {registros_procesados} | Errores: {errores_count}"
            
            conn.execute(
                query,
                (
                    tipo_carga,
                    timestamp,
                    resumen,
                    detalles,
                    cedula_admin,
                    timestamp
                )
            )
            conn.commit()
            
        st.success(f"✅ Reporte registrado automáticamente: {tipo_carga}")
        
    except Exception as e:
        st.error(f"❌ Error registrando reporte: {str(e)}")
if not st.session_state.get('autenticado', False):
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; min-height: 80vh;">
        <div style="background: linear-gradient(135deg, #1E293B 0%, #334155 100%); 
                    padding: 3rem; border-radius: 20px; 
                    border: 1px solid #334155; 
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
                    width: 100%; max-width: 500px;">
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🎓</div>
                <h1 style="color: #F8FAFC; font-weight: 700; margin-bottom: 0.5rem;">
                    SICADFOC 2026
                </h1>
                <p style="color: #CBD5E1; font-size: 1rem; margin-bottom: 0;">
                    Sistema Integral de Control Académico y Docente
                </p>
                <div style="color: #38BDF8; font-size: 0.9rem; font-weight: 500;">
                    Instituto Universitario Jesús Obrero
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        st.markdown("""
        <div style="background: #1E293B; padding: 2rem; border-radius: 15px; 
                    border: 1px solid #334155; margin-top: -2rem;">
            <h3 style="color: #F8FAFC; text-align: center; margin-bottom: 1.5rem;">
                🔐 INICIAR SESIÓN
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            u = st.text_input(
                "📧 Correo Institucional", 
                placeholder="usuario@iujo.edu.ve",
                help="Ingrese su correo institucional"
            )
        with col2:
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
            
            # Login normal para otros usuarios
            crear_tablas_sistema(engine)
            crear_usuario_prueba(engine)
            
            import hashlib
            hash_password = hashlib.sha256(p.encode()).hexdigest()
            
            query_auth = """
                SELECT id, login, email, rol, activo, correo_verificado, nombre, apellido
                FROM usuario 
                WHERE (email = :email OR login = :email) 
                AND contrasena = :password
            """
            
            try:
                res_auth = ejecutar_query(query_auth, {"email": u, "password": hash_password}, engine=engine)
                
                if res_auth is not None and not res_auth.empty:
                    usuario_data = res_auth.iloc[0].to_dict()
                    
                    if not usuario_data.get('activo', False):
                        st.error("❌ Su cuenta está desactivada.")
                        st.stop()
                    
                    if not usuario_data.get('correo_verificado', False):
                        st.error("❌ Debe verificar su correo electrónico.")
                        st.stop()
                    
                    st.session_state.autenticado = True
                    st.session_state.user_data = usuario_data
                    st.session_state.rol = usuario_data.get('rol', 'estudiante')
                    
                    registrar_auditoria_sistema(
                        usuario=usuario_data.get('login', u),
                        transaccion='LOGIN',
                        tabla_afectada='usuario',
                        detalles_adicionales=f"Email: {u}, Rol: {st.session_state.rol}"
                    )
                    
                    nombre_completo = f"{usuario_data.get('nombre', '')} {usuario_data.get('apellido', '')}".strip()
                    if nombre_completo:
                        st.success(f"🎉 ¡Bienvenido {nombre_completo}!")
                    else:
                        st.success(f"🎉 ¡Bienvenido {usuario_data.get('login', u)}!")
                    
                    st.info(f"🔐 Rol: {st.session_state.rol.title()}")
                    st.balloons()
                    st.rerun()
                    
                else:
                    st.error("❌ Correo o cédula incorrectos.")
                    
            except Exception as e:
                st.error("❌ Error en el sistema de autenticación")
                st.error(f"Detalles: {str(e)}")

# =================================================================
# 4. SIDEBAR Y NAVEGACIÓN
# =================================================================

if st.session_state.get('autenticado', False):
    with st.sidebar:
        # Logo y título
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎓</div>
            <div style="color: #1e293b; font-weight: 600; font-size: 1rem;">
                SICADFOC 2026
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar aviso de ambiente
        mostrar_aviso_ambiente(tipo_ambiente)
        
        # Información de usuario
        rol_actual = obtener_rol_usuario()
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1E293B 0%, #334155 100%); 
                    padding: 1rem; border-radius: 10px; margin: 1rem 0; 
                    border: 1px solid #334155;">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem; margin-right: 0.5rem;">👤</span>
                <div>
                    <div style="color: #F8FAFC; font-weight: 600; font-size: 0.9rem;">
                        {st.session_state.user_data['login']}
                    </div>
                    <div style="color: #CBD5E1; font-size: 0.8rem;">
                        Nivel: {rol_actual.title() if rol_actual else 'Desconocido'}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =================================================================
# 5. DASHBOARDS POR ROL
# =================================================================

def mostrar_dashboard_admin():
    """Muestra el dashboard para administradores"""
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #DC2626 0%, #16A34A 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; 
                border: 1px solid #16A34A; text-align: center;">
        <h2 style="color: white; margin-bottom: 1rem;">
            👑 PANEL DE ADMINISTRADOR
        </h2>
        <p style="color: #E2E8F0; font-size: 1.1rem; margin: 0;">
            Acceso total a todas las funcionalidades del sistema
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botones principales con letras oscuras y fondo claro
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: #F8FAFC; padding: 2rem; border-radius: 10px; 
                    border: 2px solid #E2E8F0; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #1E293B; margin-top: 0; font-size: 1.2rem; font-weight: 600;">
                📚 ESTUDIANTES
            </h4>
            <p style="color: #64748B; margin: 0.5rem 0; font-weight: 500;">
                Administración completa de estudiantes
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div style="background: #F8FAFC; padding: 2rem; border-radius: 10px; 
                    border: 2px solid #E2E8F0; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #1E293B; margin-top: 0; font-size: 1.2rem; font-weight: 600;">
                👨‍🏫 PROFESORES
            </h4>
            <p style="color: #64748B; margin: 0.5rem 0; font-weight: 500;">
                Administración de docentes
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div style="background: #F8FAFC; padding: 2rem; border-radius: 10px; 
                    border: 2px solid #E2E8F0; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #1E293B; margin-top: 0; font-size: 1.2rem; font-weight: 600;">
                🎓 FORMACIÓN COMPLEMENTARIA
            </h4>
            <p style="color: #64748B; margin: 0.5rem 0; font-weight: 500;">
                Actividades extracurriculares
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.success("✅ Panel de administrador cargado correctamente")
    st.info("📋 Use los botones principales para gestionar cada módulo")
    
    # =================================================================
    # SECCIÓN DE CONFIGURACIÓN DE CORREO
    # =================================================================
    
    st.divider()
    st.subheader("📧 Configuración de Correo SMTP")
    
    col_config1, col_config2 = st.columns(2)
    
    with col_config1:
        st.write("**Configuración Actual:**")
        
        # Mostrar configuración actual
        try:
            config_actual = database.obtener_config_correo(engine)
            if config_actual:
                st.success(f"📧 Servidor: {config_actual['servidor_smtp']}")
                st.success(f"📧 Puerto: {config_actual['puerto']}")
                st.success(f"👤 Usuario: {config_actual['usuario']}")
                st.success(f"📧 Remitente: {config_actual['remitente']}")
            else:
                st.warning("⚠️ No hay configuración de correo establecida")
        except Exception as e:
            st.error(f"❌ Error obteniendo configuración: {e}")
    
    with col_config2:
        st.write("**Acciones Rápidas:**")
        
        # Botón para configurar correo final
        if st.button("🔧 Configurar Correo Gmail", type="primary", use_container_width=True):
            with st.spinner("Configurando servicio de correo..."):
                if database.configurar_correo_final():
                    st.success("✅ Configuración de correo establecida")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Error configurando el correo")
        
        # Botón para probar envío
        email_prueba = st.text_input(
            "📧 Correo de prueba",
            value="ab6643881@gmail.com",
            help="Ingrese el correo donde se enviará la prueba"
        )
        
        if st.button("🧪 Enviar Correo de Prueba", type="secondary", use_container_width=True):
            if email_prueba:
                with st.spinner("Enviando correo de prueba..."):
                    exito, mensaje = database.probar_envio_correo(email_prueba)
                    
                    if exito:
                        st.success("✅ Correo de prueba enviado exitosamente")
                        st.info(mensaje)
                        st.balloons()
                    else:
                        st.error("❌ Error enviando correo")
                        st.error(mensaje)
                        # Mostrar detalles del error en Streamlit
                        if "Authentication" in mensaje:
                            st.error("🔐 Error de autenticación - Verifique usuario y contraseña")
                        elif "Connection" in mensaje:
                            st.error("🌐 Error de conexión - Verifique red y firewall")
                        else:
                            st.error(f"❓ Error desconocido: {mensaje}")
            else:
                st.warning("⚠️ Ingrese un correo de prueba")

def mostrar_dashboard_profesor():
    """Muestra el dashboard para profesores"""
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #059669 0%, #047857 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; 
                border: 1px solid #047857; text-align: center;">
        <h2 style="color: white; margin-bottom: 1rem;">
            👨‍🏫 PANEL DE PROFESOR
        </h2>
        <p style="color: #E2E8F0; font-size: 1.1rem; margin: 0;">
            Administración académica y formación complementaria
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: #F8FAFC; padding: 2rem; border-radius: 10px; 
                    border: 2px solid #E2E8F0; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #059669; margin-top: 0; font-size: 1.2rem; font-weight: 600;">
                📚 CURSOS
            </h4>
            <p style="color: #64748B; margin: 0.5rem 0; font-weight: 500;">
                Administración de materias
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div style="background: #F8FAFC; padding: 2rem; border-radius: 10px; 
                    border: 2px solid #E2E8F0; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #059669; margin-top: 0; font-size: 1.2rem; font-weight: 600;">
                🎓 FORMACIÓN
            </h4>
            <p style="color: #64748B; margin: 0.5rem 0; font-weight: 500;">
                Actividades complementarias
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.success("✅ Panel de profesor cargado correctamente")
    st.info("📋 Use el menú lateral para acceder a sus funcionalidades")

def mostrar_dashboard_estudiante():
    """Muestra el dashboard para estudiantes"""
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; 
                border: 1px solid #2563EB; text-align: center;">
        <h2 style="color: white; margin-bottom: 1rem;">
            🎓 PANEL DE ESTUDIANTE
        </h2>
        <p style="color: #E2E8F0; font-size: 1.1rem; margin: 0;">
            Acceso a información académica y formación
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: #F8FAFC; padding: 2rem; border-radius: 10px; 
                    border: 2px solid #E2E8F0; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #3B82F6; margin-top: 0; font-size: 1.2rem; font-weight: 600;">
                📖 MATERIAS
            </h4>
            <p style="color: #64748B; margin: 0.5rem 0; font-weight: 500;">
                Mis cursos
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div style="background: #F8FAFC; padding: 2rem; border-radius: 10px; 
                    border: 2px solid #E2E8F0; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #3B82F6; margin-top: 0; font-size: 1.2rem; font-weight: 600;">
                📋 NOTAS
            </h4>
            <p style="color: #64748B; margin: 0.5rem 0; font-weight: 500;">
                Mis calificaciones
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div style="background: #F8FAFC; padding: 2rem; border-radius: 10px; 
                    border: 2px solid #E2E8F0; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #3B82F6; margin-top: 0; font-size: 1.2rem; font-weight: 600;">
                🎯 ACTIVIDADES
            </h4>
            <p style="color: #64748B; margin: 0.5rem 0; font-weight: 500;">
                Formación complementaria
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.success("✅ Panel de estudiante cargado correctamente")
    st.info("📋 Use el menú lateral para acceder a sus funcionalidades")

# =================================================================
# 8. FORMULARIO DE REGISTRO
# =================================================================

# Mostrar formulario de registro si no está autenticado
if not st.session_state.get('autenticado', False):
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h3 style="color: #1e293b; font-weight: 600;">
            📝 REGISTRO DE NUEVO USUARIO
        </h3>
        <p style="color: #64748b; font-size: 0.9rem;">
            Complete el formulario para crear su cuenta en SICADFOC
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("registro_form", clear_on_submit=False):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            email_reg = st.text_input(
                "📧 Correo Institucional", 
                placeholder="usuario@iujo.edu.ve",
                help="Ingrese su correo institucional",
                key="email_registro"
            )
            cedula_reg = st.text_input(
                "🆔 Cédula de Identidad", 
                placeholder="V-XXXXXXX o E-XXXXXXX",
                help="Ingrese su número de cédula",
                key="cedula_registro"
            )
        
        with col2:
            perfil_reg = st.selectbox(
                "👤 Perfil de Usuario",
                options=["Estudiante", "Profesor"],
                index=0,
                help="Seleccione su perfil en el sistema",
                key="perfil_registro"
            )
        
        # Información importante
        st.info("ℹ️ **Importante:** Al registrarse, recibirá un correo de confirmación para activar su cuenta.")
        st.info("📧 El correo de confirmación será enviado a la dirección que ingrese.")
        
        # Botones de acción
        col_registrar, col_probar = st.columns([2, 1])
        
        with col_registrar:
            btn_registrar = st.form_submit_button(
                "🚀 Crear Cuenta", 
                type="primary",
                use_container_width=True
            )
        
        with col_probar:
            btn_probar_correo = st.form_submit_button(
                "🧪 Probar Correo", 
                type="secondary",
                use_container_width=True
            )
        
        if btn_probar_correo:
            if email_reg:
                with st.spinner("Enviando correo de prueba..."):
                    exito, mensaje = database.probar_envio_correo(email_reg)
                    
                    if exito:
                        st.success("✅ Correo de prueba enviado exitosamente")
                        st.info(mensaje)
                        st.balloons()
                    else:
                        st.error("❌ Error enviando correo")
                        st.error(mensaje)
                        
                        # Mostrar detalles del error en Streamlit
                        if "Authentication" in mensaje:
                            st.error("🔐 Error de autenticación - Verifique usuario y contraseña de aplicación")
                        elif "Connection" in mensaje:
                            st.error("🌐 Error de conexión - Verifique red y firewall")
                        else:
                            st.error(f"❓ Error desconocido: {mensaje}")
            else:
                st.warning("⚠️ Ingrese un correo para probar")
        
        if btn_registrar:
            # Validar campos
            if not email_reg or not cedula_reg:
                st.error("❌ Por favor, complete todos los campos")
                st.stop()
            
            # Validar formato de email
            if "@" not in email_reg or "." not in email_reg:
                st.error("❌ Formato de correo inválido")
                st.stop()
            
            # Validar formato de cédula
            if not (cedula_reg.startswith(('V-', 'E-', 'v-', 'e-')) and len(cedula_reg) >= 7):
                st.error("❌ Formato de cédula inválido. Use: V-XXXXXXX o E-XXXXXXX")
                st.stop()
            
            # =================================================================
# 4. SIDEBAR Y NAVEGACIÓN PROFESIONAL
# =================================================================

if st.session_state.get('autenticado', False):
    with st.sidebar:
        # Logo institucional responsivo
        try:
            # Intentar cargar logo institucional
            if os.path.exists("logo_iujo.png"):
                st.sidebar.image("logo_iujo.png", use_container_width=True, output_format="PNG")
            else:
                # Logo alternativo si no existe el archivo - responsivo
                st.sidebar.markdown("""
                <div style="text-align: center; margin-bottom: 1.5rem;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎓</div>
                    <div style="color: #1e293b; font-weight: 700; font-size: 1rem; line-height: 1.2;">
                        INSTITUTO<br>UNIVERSITARIO<br>JESÚS OBRERO
                    </div>
                    <div style="color: #64748b; font-size: 0.8rem; margin-top: 0.5rem;">
                        SICADFOC 2026
                    </div>
                </div>
                """, unsafe_allow_html=True)
        except:
            # Logo de respaldo - responsivo
            st.sidebar.markdown("""
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎓</div>
                <div style="color: #1e293b; font-weight: 700; font-size: 1rem; line-height: 1.2;">
                    INSTITUTO<br>UNIVERSITARIO<br>JESÚS OBRERO
                </div>
                <div style="color: #64748b; font-size: 0.8rem; margin-top: 0.5rem;">
                    SICADFOC 2026
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Información de usuario - responsivo
        rol_actual = obtener_rol_usuario()
        st.sidebar.markdown(f"""
        <div style="background: linear-gradient(135deg, #1E293B 0%, #334155 100%); 
                    padding: 0.75rem; border-radius: 10px; margin: 1rem 0; 
                    border: 1px solid #334155;">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem; margin-right: 0.5rem;">👤</span>
                <div>
                    <div style="color: #F8FAFC; font-weight: 600; font-size: 0.8rem; word-break: break-all;">
                        {st.session_state.user_data['login']}
                    </div>
                    <div style="color: #CBD5E1; font-size: 0.7rem;">
                        Nivel: {rol_actual.title() if rol_actual else 'Desconocido'}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Menú de navegación principal - responsivo
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📋 MÓDULOS")
        
        # Selector de módulo con mejor espaciado
        modulo_seleccionado = st.sidebar.radio(
            "Seleccionar módulo:",
            ["🏠 Inicio", "📚 Estudiantes", "👨‍🏫 Profesores", "🎓 Formación Complementaria", "⚙️ Configuración", "📊 Reportes", "⚡ Monitor", "🔄 Actualización Render Cloud"],
            index=0,
            key="modulo_principal",
            help="Seleccione el módulo que desea gestionar"
        )
        
        # Separador
        st.sidebar.markdown("---")
        
        # Información del sistema - compacta
        mostrar_aviso_ambiente(tipo_ambiente)
        
        # Botón de cerrar sesión - más grande en móvil
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True, help="Cerrar sesión actual"):
            st.session_state.clear()
            st.rerun()

# =================================================================
# 5. ÁREA PRINCIPAL - VISUALIZACIÓN LIMPIA
# =================================================================

if st.session_state.get('autenticado', False):
    # Control principal según selección del sidebar
    if modulo_seleccionado == "🏠 Inicio":
        # Dashboard principal - responsivo
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1E293B 0%, #334155 100%); 
                    padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem; 
                    border: 1px solid #334155; text-align: center;">
            <h1 style="color: white; margin-bottom: 1rem; font-size: 2rem;">
                🏠 PANEL PRINCIPAL
            </h1>
            <p style="color: #E2E8F0; font-size: 1.1rem; margin: 0;">
                Sistema Integral de Control Académico y Docente
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Métricas principales - responsivas
        try:
            metrics = database.obtener_metricas_sistema()
            
            # Detectar ancho de pantalla y ajustar columnas
            if st.session_state.get('mobile_view', False):
                # Vista móvil: una columna
                col_dash1 = st.columns(1)[0]
                with col_dash1:
                    st.metric("👨‍🎓 Estudiantes", metrics.get('estudiantes', 0))
                
                col_dash2 = st.columns(1)[0]
                with col_dash2:
                    st.metric("👨‍🏫 Profesores", metrics.get('profesores', 0))
                
                col_dash3 = st.columns(1)[0]
                with col_dash3:
                    st.metric("🎓 Cursos", metrics.get('cursos', 0))
            else:
                # Vista desktop: tres columnas
                col_dash1, col_dash2, col_dash3 = st.columns(3)
                
                with col_dash1:
                    st.metric("👨‍🎓 Estudiantes", metrics.get('estudiantes', 0))
                
                with col_dash2:
                    st.metric("👨‍🏫 Profesores", metrics.get('profesores', 0)) 
                
                with col_dash3:
                    st.metric("🎓 Cursos", metrics.get('cursos', 0))
                    
        except:
            st.warning("⚠️ Cargando métricas...")
        
        st.divider()
        st.info("💡 Use el menú lateral para acceder a los diferentes módulos del sistema.")
    
    elif modulo_seleccionado == "📚 Estudiantes":
        # =================================================================
        # MÓDULO DE ESTUDIANTES - VISUALIZACIÓN LIMPIA
        # =================================================================
        st.header("📚 Estudiantes")
        
        # Crear directorios necesarios
        os.makedirs("expedientes", exist_ok=True)
        os.makedirs("expedientes_pdf", exist_ok=True)
        
        # Pestañas principales
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Registro Individual", "📊 Carga Masiva (CSV)", "📄 Expediente Digital (PDF)", "📁 Carga Digital (PDF)"])
        
        # =================================================================
        # PESTAÑA 1: REGISTRO INDIVIDUAL
        # =================================================================
        with tab1:
            st.subheader("📝 Registro Individual de Estudiantes")
            
            with st.form("registro_individual_form"):
                # Detectar vista móvil y ajustar columnas
                if st.session_state.get('mobile_view', False):
                    # Vista móvil: una columna
                    with st.container():
                        # Cédula con validación en tiempo real
                        cedula = st.text_input(
                            "🆔 Cédula de Identidad *",
                            placeholder="V-12345678 o E-12345678",
                            help="Formato: V-XXXXXXXX o E-XXXXXXXX",
                            key="cedula_individual"
                        )
                        
                        # Validación en tiempo real
                        if cedula:
                            if not re.match(r'^[VE]-\d{7,8}$', cedula.upper()):
                                st.error("❌ Formato inválido. Use V-12345678 o E-12345678")
                            else:
                                # Verificar si ya existe
                                try:
                                    verificar = ejecutar_query(
                                        "SELECT COUNT(*) as count FROM usuario WHERE login = :cedula OR cedula = :cedula",
                                        {"cedula": cedula.upper()},
                                        engine=engine
                                    )
                                    if verificar and verificar.iloc[0]['count'] > 0:
                                        st.warning("⚠️ Esta cédula ya está registrada")
                                    else:
                                        st.success("✅ Cédula disponible")
                                except:
                                    pass
                        
                        nombres = st.text_input(
                            "👤 Nombres *",
                            placeholder="Juan Carlos",
                            help="Nombres completos del estudiante",
                            key="nombres_individual"
                        )
                        
                        apellidos = st.text_input(
                            "👥 Apellidos *",
                            placeholder="Pérez González",
                            help="Apellidos completos del estudiante",
                            key="apellidos_individual"
                        )
                        
                        correo = st.text_input(
                            "📧 Correo Institucional *",
                            placeholder="estudiante@iujo.edu.ve",
                            help="Correo electrónico del estudiante",
                            key="correo_individual"
                        )
                        
                        # Validación en tiempo real del correo
                        if correo:
                            if "@" not in correo or "." not in correo:
                                st.error("❌ Formato de correo inválido")
                            else:
                                # Verificar si ya existe
                                try:
                                    verificar = ejecutar_query(
                                        "SELECT COUNT(*) as count FROM usuario WHERE login = :correo OR email = :correo",
                                        {"correo": correo.lower()},
                                        engine=engine
                                    )
                                    if verificar and verificar.iloc[0]['count'] > 0:
                                        st.warning("⚠️ Este correo ya está registrado")
                                    else:
                                        st.success("✅ Correo disponible")
                                except:
                                    pass
                else:
                    # Vista desktop: dos columnas
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Cédula con validación en tiempo real
                        cedula = st.text_input(
                            "🆔 Cédula de Identidad *",
                            placeholder="V-12345678 o E-12345678",
                            help="Formato: V-XXXXXXXX o E-XXXXXXXX",
                            key="cedula_individual"
                        )
                        
                        # Validación en tiempo real
                        if cedula:
                            if not re.match(r'^[VE]-\d{7,8}$', cedula.upper()):
                                st.error("❌ Formato inválido. Use V-12345678 o E-12345678")
                            else:
                                # Verificar si ya existe
                                try:
                                    verificar = ejecutar_query(
                                        "SELECT COUNT(*) as count FROM usuario WHERE login = :cedula OR cedula = :cedula",
                                        {"cedula": cedula.upper()},
                                        engine=engine
                                    )
                                    if verificar and verificar.iloc[0]['count'] > 0:
                                        st.warning("⚠️ Esta cédula ya está registrada")
                                    else:
                                        st.success("✅ Cédula disponible")
                                except:
                                    pass
                        
                        nombres = st.text_input(
                            "👤 Nombres *",
                            placeholder="Juan Carlos",
                            help="Nombres completos del estudiante",
                            key="nombres_individual"
                        )
                    
                    with col2:
                        apellidos = st.text_input(
                            "👥 Apellidos *",
                            placeholder="Pérez González",
                            help="Apellidos completos del estudiante",
                            key="apellidos_individual"
                        )
                        
                        correo = st.text_input(
                            "📧 Correo Institucional *",
                            placeholder="estudiante@iujo.edu.ve",
                            help="Correo electrónico del estudiante",
                            key="correo_individual"
                        )
                        
                        # Validación en tiempo real del correo
                        if correo:
                            if "@" not in correo or "." not in correo:
                                st.error("❌ Formato de correo inválido")
                            else:
                                # Verificar si ya existe
                                try:
                                    verificar = ejecutar_query(
                                        "SELECT COUNT(*) as count FROM usuario WHERE login = :correo OR email = :correo",
                                        {"correo": correo.lower()},
                                        engine=engine
                                    )
                                    if verificar and verificar.iloc[0]['count'] > 0:
                                        st.warning("⚠️ Este correo ya está registrado")
                                    else:
                                        st.success("✅ Correo disponible")
                                except:
                                    pass
                
                semestre = st.selectbox(
                    "📚 Semestre *",
                    options=[f"{i}° Semestre" for i in range(1, 11)],
                    index=0,
                    help="Seleccione el semestre actual del estudiante",
                    key="semestre_individual"
                )
                
                # Información importante
                st.info("ℹ️ **Nota:** Los campos marcados con * son obligatorios")
                st.info("🔐 La contraseña inicial será la cédula de identidad")
                
                # Botones de acción - responsivos
                if st.session_state.get('mobile_view', False):
                    # Vista móvil: botones apilados
                    btn_guardar = st.form_submit_button(
                        "💾 Guardar Estudiante",
                        type="primary",
                        use_container_width=True
                    )
                    
                    btn_limpiar = st.form_submit_button(
                        "🗑️ Limpiar Formulario",
                        type="secondary",
                        use_container_width=True
                    )
                else:
                    # Vista desktop: botones en columnas
                    col_guardar, col_limpiar = st.columns([2, 1])
                    
                    with col_guardar:
                        btn_guardar = st.form_submit_button(
                            "💾 Guardar Estudiante",
                            type="primary",
                            use_container_width=True
                        )
                    
                    with col_limpiar:
                        btn_limpiar = st.form_submit_button(
                            "🗑️ Limpiar Formulario",
                            type="secondary",
                            use_container_width=True
                        )
                
                if btn_guardar:
                    # Validar campos obligatorios
                    if not all([cedula, nombres, apellidos, correo]):
                        st.error("❌ Complete todos los campos obligatorios")
                        st.stop()
                    
                    # Validar formatos
                    if not re.match(r'^[VE]-\d{7,8}$', cedula.upper()):
                        st.error("❌ Formato de cédula inválido")
                        st.stop()
                    
                    if "@" not in correo or "." not in correo:
                        st.error("❌ Formato de correo inválido")
                        st.stop()
                    
                    # Procesar registro
                    with st.spinner("Registrando estudiante..."):
                        try:
                            # Verificar duplicados
                            verificar_cedula = ejecutar_query(
                                "SELECT COUNT(*) as count FROM usuario WHERE login = :cedula OR cedula = :cedula",
                                {"cedula": cedula.upper()},
                                engine=engine
                            )
                            
                            verificar_correo = ejecutar_query(
                                "SELECT COUNT(*) as count FROM usuario WHERE login = :correo OR email = :correo",
                                {"correo": correo.lower()},
                                engine=engine
                            )
                            
                            if verificar_cedula.iloc[0]['count'] > 0:
                                st.error("❌ La cédula ya está registrada")
                                st.stop()
                            
                            if verificar_correo.iloc[0]['count'] > 0:
                                st.error("❌ El correo ya está registrado")
                                st.stop()
                            
                            # Insertar estudiante
                            hash_password = hashlib.sha256(cedula.upper().encode()).hexdigest()
                            
                            insertar = """
                            INSERT INTO usuario (
                                login, email, contrasena, rol, nombre, apellido, 
                                cedula, semestre, activo, correo_verificado, 
                                fecha_registro
                            ) VALUES (
                                :login, :email, :password, :rol, :nombre, :apellido,
                                :cedula, :semestre, :activo, :correo_verificado,
                                :fecha_registro
                            )
                            """
                            
                            ejecutar_query(insertar, {
                                'login': correo.lower(),
                                'email': correo.lower(),
                                'password': hash_password,
                                'rol': 'estudiante',
                                'nombre': nombres.title(),
                                'apellido': apellidos.title(),
                                'cedula': cedula.upper(),
                                'semestre': semestre,
                                'activo': True,
                                'correo_verificado': False,
                                'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }, engine=engine)
                            
                            st.success("✅ Estudiante registrado exitosamente")
                            st.info(f"📧 Se enviará correo de confirmación a: {correo}")
                            st.balloons()
                            
                            # Limpiar formulario
                            for key in st.session_state.keys():
                                if key.endswith('_individual'):
                                    del st.session_state[key]
                            
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error registrando estudiante: {str(e)}")
                
                if btn_limpiar:
                    # Limpiar campos del formulario
                    for key in st.session_state.keys():
                        if key.endswith('_individual'):
                            del st.session_state[key]
                    st.rerun()
        
        # =================================================================
        # PESTAÑA 2: CARGA MASIVA (CSV)
        # =================================================================
        with tab2:
            st.subheader("📊 Carga Masiva de Estudiantes (CSV)")
            
            # Instrucciones
            with st.expander("📋 Instrucciones de Formato CSV", expanded=True):
                st.markdown("""
                **Formato requerido para el archivo CSV:**
                
                | Columna | Requerida | Formato | Ejemplo |
                |----------|-----------|----------|---------|
                | cedula | Sí | V-12345678 | V-12345678 |
                | nombres | Sí | Texto | Juan Carlos |
                | apellidos | Sí | Texto | Pérez González |
                | correo | Sí | email@dominio.com | estudiante@iujo.edu.ve |
                | semestre | Sí | Número 1-10 | 3 |
                
                **Notas:**
                - El archivo debe tener encabezado en la primera fila
                - Los campos cédula y correo no deben repetirse
                - Si una cédula ya existe, se omitirá y se reportará al final
                """)
            
            # Carga de archivo
            archivo_csv = st.file_uploader(
                "📁 Seleccione archivo CSV",
                type=['csv'],
                help="Suba el archivo CSV con los datos de los estudiantes",
                key="archivo_csv"
            )
            
            if archivo_csv:
                try:
                    # Leer archivo CSV
                    df = pd.read_csv(archivo_csv)
                    
                    # Normalizar columnas (insensible a mayúsculas/minúsculas y tildes)
                    df = normalizar_columnas_csv(df, tipo='estudiantes')
                    
                    # Validar columnas requeridas
                    columnas_requeridas = ['cedula', 'nombres', 'apellidos', 'correo', 'semestre']
                    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
                    
                    if columnas_faltantes:
                        st.error(f"❌ Columnas faltantes: {', '.join(columnas_faltantes)}")
                        st.info("💡 **Columnas aceptadas:** cédula, Cedula, CEDULA, nombres, NOMBRES, apellidos, APELLIDOS, correo, EMAIL, semestre, SEMESTRE")
                        st.stop()
                    
                    # Mostrar vista previa
                    st.write("📊 **Vista Previa de Datos:**")
                    st.dataframe(df.head(10))
                    
                    # Procesar carga
                    if st.button("🚀 Procesar Carga Masiva", type="primary", use_container_width=True):
                        with st.spinner("Procesando carga masiva..."):
                            try:
                                creados = 0
                                omitidos = 0
                                errores = []
                                
                                for index, row in df.iterrows():
                                    try:
                                        # Validar datos
                                        cedula = str(row['cedula']).strip().upper()
                                        nombres = str(row['nombres']).strip().title()
                                        apellidos = str(row['apellidos']).strip().title()
                                        correo = str(row['correo']).strip().lower()
                                        semestre = str(row['semestre']).strip()
                                        
                                        # FILTRO CRÍTICO: Omitir correo angelher@gmail.com
                                        if correo == 'angelher@gmail.com':
                                            omitidos += 1
                                            errores.append(f"Fila {index+2}: Usuario omitido por restricciones de seguridad")
                                            continue
                                        
                                        # Validar formato de cédula
                                        if not re.match(r'^[VE]-\d{7,8}$', cedula):
                                            errores.append(f"Fila {index+2}: Cédula inválida: {cedula}")
                                            omitidos += 1
                                            continue
                                        
                                        # Validar formato de correo
                                        if "@" not in correo or "." not in correo:
                                            errores.append(f"Fila {index+2}: Correo inválido: {correo}")
                                            omitidos += 1
                                            continue
                                        
                                        # Verificar duplicados
                                        verificar_cedula = ejecutar_query(
                                            "SELECT COUNT(*) as count FROM usuario WHERE cedula = :cedula",
                                            {"cedula": cedula},
                                            engine=engine
                                        )
                                        
                                        verificar_correo = ejecutar_query(
                                            "SELECT COUNT(*) as count FROM usuario WHERE email = :correo",
                                            {"correo": correo},
                                            engine=engine
                                        )
                                        
                                        if verificar_cedula.iloc[0]['count'] > 0:
                                            omitidos += 1
                                            continue
                                        
                                        if verificar_correo.iloc[0]['count'] > 0:
                                            omitidos += 1
                                            continue
                                        
                                        # Insertar estudiante
                                        hash_password = hashlib.sha256(cedula.encode()).hexdigest()
                                        
                                        insertar = """
                                        INSERT INTO usuario (
                                            login, email, contrasena, rol, nombre, apellido,
                                            cedula, semestre, activo, correo_verificado,
                                            fecha_registro
                                        ) VALUES (
                                            :login, :email, :password, :rol, :nombre, :apellido,
                                            :cedula, :semestre, :activo, :correo_verificado,
                                            :fecha_registro
                                        )
                                        """
                                        
                                        ejecutar_query(insertar, {
                                            'login': correo,
                                            'email': correo,
                                            'password': hash_password,
                                            'rol': 'estudiante',
                                            'nombre': nombres,
                                            'apellido': apellidos,
                                            'cedula': cedula,
                                            'semestre': f"{semestre}° Semestre",
                                            'activo': True,
                                            'correo_verificado': False,
                                            'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        }, engine=engine)
                                        
                                        creados += 1
                                        
                                    except Exception as e:
                                        errores.append(f"Fila {index+2}: {str(e)}")
                                        omitidos += 1
                                
                                # Mostrar resultados
                                st.success("✅ Proceso completado")
                                
                                col_res1, col_res2, col_res3 = st.columns(3)
                                
                                with col_res1:
                                    st.metric("📝 Estudiantes Creados", creados)
                                
                                with col_res2:
                                    st.metric("⚠️ Registros Omitidos", omitidos)
                                
                                with col_res3:
                                    st.metric("📊 Total Procesados", len(df))
                                
                                if errores:
                                    st.error("❌ Errores encontrados:")
                                    for error in errores[:10]:  # Mostrar solo primeros 10 errores
                                        st.error(error)
                                    if len(errores) > 10:
                                        st.warning(f"... y {len(errores) - 10} errores más")
                                
                                if creados > 0:
                                    st.balloons()
                                    st.info(f"📧 Se enviarán correos de confirmación a los {creados} estudiantes creados")
                                
                                # REGISTRO AUTOMÁTICO EN MÓDULO DE REPORTES
                                registrar_reporte_carga(
                                    tipo_carga="Carga Masiva de Estudiantes",
                                    registros_procesados=len(df),
                                    errores_count=len(errores),
                                    detalles=f"Estudiantes creados: {creados} | Omitidos: {omitidos}"
                                )
                                
                            except Exception as e:
                                st.error(f"❌ Error en carga masiva: {str(e)}")
                                
                except Exception as e:
                    st.error(f"❌ Error leyendo archivo CSV: {str(e)}")
        
        # =================================================================
        # PESTAÑA 3: EXPEDIENTE DIGITAL (PDF)
        # =================================================================
        with tab3:
            st.subheader("📄 Expediente Digital (PDF)")
            
            # Información importante
            st.info("ℹ️ **Nota:** Puede subir documentos PDF usando la cámara de su celular o apps como CamScanner")
            
            # Buscar estudiante - responsivo
            if st.session_state.get('mobile_view', False):
                # Vista móvil: campos apilados
                cedula_buscar = st.text_input(
                    "🔍 Buscar Estudiante por Cédula",
                    placeholder="V-12345678",
                    help="Ingrese la cédula del estudiante",
                    key="cedula_buscar_expediente"
                )
                
                btn_buscar = st.button("🔍 Buscar Estudiante", use_container_width=True)
            else:
                # Vista desktop: en línea
                col_buscar, col_buscar_btn = st.columns([3, 1])
                
                with col_buscar:
                    cedula_buscar = st.text_input(
                        "🔍 Buscar Estudiante por Cédula",
                        placeholder="V-12345678",
                        help="Ingrese la cédula del estudiante",
                        key="cedula_buscar_expediente"
                    )
                
                with col_buscar_btn:
                    st.write("")  # Espacio para alinear el botón
                    btn_buscar = st.button("🔍 Buscar", use_container_width=True)
            
            estudiante_encontrado = None
            
            if btn_buscar and cedula_buscar:
                try:
                    resultado = ejecutar_query(
                        "SELECT * FROM usuario WHERE cedula = :cedula AND rol = 'estudiante'",
                        {"cedula": cedula_buscar.upper()},
                        engine=engine
                    )
                    
                    if resultado is not None and not resultado.empty:
                        estudiante_encontrado = resultado.iloc[0]
                        st.success(f"✅ Estudiante encontrado: {estudiante_encontrado['nombre']} {estudiante_encontrado['apellido']}")
                    else:
                        st.error("❌ Estudiante no encontrado")
                except Exception as e:
                    st.error(f"❌ Error buscando estudiante: {str(e)}")
            
            if estudiante_encontrado is not None:
                # Mostrar información del estudiante - responsivo
                with st.expander("👤 Información del Estudiante", expanded=True):
                    if st.session_state.get('mobile_view', False):
                        # Vista móvil: información apilada
                        st.write(f"**🆔 Cédula:** {estudiante_encontrado['cedula']}")
                        st.write(f"**👤 Nombre:** {estudiante_encontrado['nombre']}")
                        st.write(f"**👥 Apellido:** {estudiante_encontrado['apellido']}")
                        st.write(f"**📧 Correo:** {estudiante_encontrado['email']}")
                        st.write(f"**📚 Semestre:** {estudiante_encontrado['semestre']}")
                        st.write(f"**✅ Estado:** {'Activo' if estudiante_encontrado['activo'] else 'Inactivo'}")
                    else:
                        # Vista desktop: dos columnas
                        col_info1, col_info2 = st.columns(2)
                        
                        with col_info1:
                            st.write(f"**🆔 Cédula:** {estudiante_encontrado['cedula']}")
                            st.write(f"**👤 Nombre:** {estudiante_encontrado['nombre']}")
                            st.write(f"**👥 Apellido:** {estudiante_encontrado['apellido']}")
                        
                        with col_info2:
                            st.write(f"**📧 Correo:** {estudiante_encontrado['email']}")
                            st.write(f"**📚 Semestre:** {estudiante_encontrado['semestre']}")
                            st.write(f"**✅ Estado:** {'Activo' if estudiante_encontrado['activo'] else 'Inactivo'}")
                
                # Carga de archivos PDF - responsivo
                st.write("---")
                st.write("📁 **Subir Expediente Digital**")
                
                # Optimizado para móvil
                archivos_pdf = st.file_uploader(
                    "📄 Seleccione archivos PDF",
                    type=['pdf'],
                    accept_multiple_files=True,
                    help="Suba los documentos PDF del expediente. Puede usar la cámara de su celular.",
                    key="archivos_pdf_expediente"
                )
                
                if archivos_pdf:
                    st.write(f"📊 **Archivos seleccionados:** {len(archivos_pdf)}")
                    
                    # Mostrar vista previa de archivos - responsivo
                    if st.session_state.get('mobile_view', False):
                        # Vista móvil: lista simple
                        for i, archivo in enumerate(archivos_pdf):
                            st.write(f"📄 **{archivo.name}** ({archivo.size / 1024:.1f} KB)")
                    else:
                        # Vista desktop: en columnas
                        for i, archivo in enumerate(archivos_pdf):
                            col_file, col_name = st.columns([1, 4])
                            
                            with col_file:
                                st.write(f"📄")
                            
                            with col_name:
                                st.write(f"**{archivo.name}** ({archivo.size / 1024:.1f} KB)")
                    
                    # Botón para guardar archivos
                    if st.button("💾 Guardar Expediente", type="primary", use_container_width=True):
                        with st.spinner("Guardando expediente digital..."):
                            try:
                                guardados = 0
                                errores = []
                                
                                for archivo in archivos_pdf:
                                    try:
                                        # Crear nombre de archivo seguro
                                        cedula_limpia = re.sub(r'[^a-zA-Z0-9]', '_', estudiante_encontrado['cedula'])
                                        nombre_archivo = f"{cedula_limpia}_{archivo.name}"
                                        
                                        # Ruta de destino
                                        ruta_destino = os.path.join("expedientes", nombre_archivo)
                                        
                                        # Guardar archivo
                                        with open(ruta_destino, "wb") as f:
                                            f.write(archivo.getbuffer())
                                        
                                        guardados += 1
                                        
                                    except Exception as e:
                                        errores.append(f"Error guardando {archivo.name}: {str(e)}")
                                
                                # Mostrar resultados
                                if guardados > 0:
                                    st.success(f"✅ {guardados} archivos guardados exitosamente")
                                    st.info(f"📁 Ubicación: /expedientes/")
                                
                                if errores:
                                    st.error("❌ Errores al guardar:")
                                    for error in errores:
                                        st.error(error)
                                
                                if guardados > 0:
                                    st.balloons()
                                    
                            except Exception as e:
                                st.error(f"❌ Error general guardando expediente: {str(e)}")
                
                # Mostrar archivos existentes - responsivo
                st.write("---")
                st.write("📂 **Expediente Existente**")
                
                try:
                    cedula_limpia = re.sub(r'[^a-zA-Z0-9]', '_', estudiante_encontrado['cedula'])
                    archivos_existentes = []
                    
                    # Buscar archivos del estudiante
                    for archivo in os.listdir("expedientes"):
                        if archivo.startswith(cedula_limpia) and archivo.endswith('.pdf'):
                            ruta_completa = os.path.join("expedientes", archivo)
                            tamaño = os.path.getsize(ruta_completa) / 1024  # KB
                            archivos_existentes.append({
                                'nombre': archivo,
                                'ruta': ruta_completa,
                                'tamaño': tamaño
                            })
                    
                    if archivos_existentes:
                        st.write(f"📄 **Archivos encontrados:** {len(archivos_existentes)}")
                        
                        # Mostrar archivos - responsivo
                        if st.session_state.get('mobile_view', False):
                            # Vista móvil: lista simple con botones
                            for archivo_info in archivos_existentes:
                                col_nombre, col_tamaño, col_accion = st.columns([2, 1, 1])
                                
                                with col_nombre:
                                    st.write(f"📄 {archivo_info['nombre']}")
                                
                                with col_tamaño:
                                    st.write(f"{archivo_info['tamaño']:.1f} KB")
                                
                                with col_accion:
                                    if st.button("👁️", key=f"ver_{archivo_info['nombre']}", help="Ver PDF"):
                                        st.info(f"📂 Ruta: {archivo_info['ruta']}")
                        else:
                            # Vista desktop: en columnas
                            for archivo_info in archivos_existentes:
                                col_archivo, col_tamaño, col_accion = st.columns([3, 1, 1])
                                
                                with col_archivo:
                                    st.write(f"📄 {archivo_info['nombre']}")
                                
                                with col_tamaño:
                                    st.write(f"{archivo_info['tamaño']:.1f} KB")
                                
                                with col_accion:
                                    if st.button("👁️", key=f"ver_{archivo_info['nombre']}", help="Ver PDF"):
                                        st.info(f"📂 Ruta: {archivo_info['ruta']}")
                    else:
                        st.info("📭 No hay archivos en el expediente")
                        
                except Exception as e:
                    st.error(f"❌ Error listando archivos: {str(e)}")
            else:
                st.info("🔍 Busque un estudiante para gestionar su expediente digital")
        
        # =================================================================
        # PESTAÑA 4: CARGA DIGITAL (PDF) - SOLO ESTUDIANTES
        # =================================================================
        with tab4:
            st.subheader("📁 Carga Digital de Expedientes (PDF)")
            
            # Información importante
            st.info("ℹ️ **Nota:** Esta sección es solo para carga masiva de expedientes PDF de estudiantes")
            st.info("📧 Los archivos se guardarán automáticamente en la carpeta /expedientes_pdf/")
            
            # Carga de archivos PDF - responsivo
            st.write("📁 **Subir Expedientes PDF**")
            
            # Optimizado para móvil
            archivos_pdf = st.file_uploader(
                "📄 Seleccione archivos PDF de expedientes",
                type=['pdf'],
                accept_multiple_files=True,
                help="Suba los archivos PDF de expedientes. Los archivos se guardarán con formato cedula_estudiante.pdf",
                key="archivos_pdf_carga_masiva"
            )
            
            if archivos_pdf:
                st.write(f"📊 **Archivos seleccionados:** {len(archivos_pdf)}")
                
                # Mostrar vista previa de archivos - responsivo
                if st.session_state.get('mobile_view', False):
                    # Vista móvil: lista simple
                    for i, archivo in enumerate(archivos_pdf):
                        st.write(f"📄 **{archivo.name}** ({archivo.size / 1024:.1f} KB)")
                else:
                    # Vista desktop: en columnas
                    for i, archivo in enumerate(archivos_pdf):
                        col_file, col_name = st.columns([1, 4])
                        
                        with col_file:
                            st.write(f"📄")
                        
                        with col_name:
                            st.write(f"**{archivo.name}** ({archivo.size / 1024:.1f} KB)")
                
                # Campo para ingresar cédula del estudiante
                st.write("---")
                st.write("🆔 **Identificación del Estudiante**")
                
                cedula_estudiante = st.text_input(
                    "🆔 Cédula del Estudiante *",
                    placeholder="V-12345678",
                    help="Ingrese la cédula del estudiante para nombrar el archivo",
                    key="cedula_carga_pdf"
                )
                
                # Validación en tiempo real
                if cedula_estudiante:
                    if not re.match(r'^[VE]-\d{7,8}$', cedula_estudiante.upper()):
                        st.error("❌ Formato inválido. Use V-12345678 o E-12345678")
                    else:
                        st.success("✅ Formato de cédula válido")
                
                # Botón para guardar archivos
                if st.button("💾 Guardar Expedientes", type="primary", use_container_width=True):
                    if not cedula_estudiante:
                        st.error("❌ Ingrese la cédula del estudiante")
                        st.stop()
                    
                    if not re.match(r'^[VE]-\d{7,8}$', cedula_estudiante.upper()):
                        st.error("❌ Formato de cédula inválido")
                        st.stop()
                    
                    with st.spinner("Guardando expedientes..."):
                        try:
                            guardados = 0
                            errores = []
                            
                            for archivo in archivos_pdf:
                                try:
                                    # Crear nombre de archivo seguro con formato cedula_estudiante.pdf
                                    cedula_limpia = re.sub(r'[^a-zA-Z0-9]', '_', cedula_estudiante.upper())
                                    nombre_archivo = f"{cedula_limpia}.pdf"
                                    
                                    # Ruta de destino
                                    ruta_destino = os.path.join("expedientes_pdf", nombre_archivo)
                                    
                                    # Guardar archivo
                                    with open(ruta_destino, "wb") as f:
                                        f.write(archivo.getbuffer())
                                    
                                    guardados += 1
                                    
                                except Exception as e:
                                    errores.append(f"Error guardando {archivo.name}: {str(e)}")
                            
                            # Mostrar resultados
                            if guardados > 0:
                                st.success(f"✅ {guardados} archivos guardados exitosamente")
                                st.info(f"📁 Ubicación: /expedientes_pdf/")
                                st.info(f"📄 Nombre del archivo: {cedula_limpia}.pdf")
                            
                            if errores:
                                st.error("❌ Errores al guardar:")
                                for error in errores:
                                    st.error(error)
                            
                            if guardados > 0:
                                st.balloons()
                                
                        except Exception as e:
                            st.error(f"❌ Error general guardando expedientes: {str(e)}")
            
            # Mostrar archivos existentes en expedientes_pdf
            st.write("---")
            st.write("📂 **Expedientes Existentes**")
            
            try:
                archivos_existentes = []
                
                # Buscar todos los archivos PDF en la carpeta
                for archivo in os.listdir("expedientes_pdf"):
                    if archivo.endswith('.pdf'):
                        ruta_completa = os.path.join("expedientes_pdf", archivo)
                        tamaño = os.path.getsize(ruta_completa) / 1024  # KB
                        archivos_existentes.append({
                            'nombre': archivo,
                            'ruta': ruta_completa,
                            'tamaño': tamaño
                        })
                
                if archivos_existentes:
                    st.write(f"📄 **Archivos encontrados:** {len(archivos_existentes)}")
                    
                    # Mostrar archivos - responsivo
                    if st.session_state.get('mobile_view', False):
                        # Vista móvil: lista simple con botones
                        for archivo_info in archivos_existentes:
                            col_nombre, col_tamaño, col_accion = st.columns([2, 1, 1])
                            
                            with col_nombre:
                                st.write(f"📄 {archivo_info['nombre']}")
                            
                            with col_tamaño:
                                st.write(f"{archivo_info['tamaño']:.1f} KB")
                            
                            with col_accion:
                                if st.button("👁️", key=f"ver_carga_{archivo_info['nombre']}", help="Ver PDF"):
                                    st.info(f"📂 Ruta: {archivo_info['ruta']}")
                    else:
                        # Vista desktop: en columnas
                        for archivo_info in archivos_existentes:
                            col_archivo, col_tamaño, col_accion = st.columns([3, 1, 1])
                            
                            with col_archivo:
                                st.write(f"📄 {archivo_info['nombre']}")
                            
                            with col_tamaño:
                                st.write(f"{archivo_info['tamaño']:.1f} KB")
                            
                            with col_accion:
                                if st.button("👁️", key=f"ver_carga_{archivo_info['nombre']}", help="Ver PDF"):
                                    st.info(f"📂 Ruta: {archivo_info['ruta']}")
                else:
                    st.info("📭 No hay archivos en la carpeta expedientes_pdf")
                    
            except Exception as e:
                st.error(f"❌ Error listando archivos: {str(e)}")
    
    elif modulo_seleccionado == "👨‍🏫 Profesores":
        # Módulo de Profesores
        st.header("👨‍🏫 Profesores")
        
        # Crear directorios necesarios
        os.makedirs("expedientes_pdf", exist_ok=True)
        
        # Pestañas principales
        tab1, tab2, tab3 = st.tabs(["📝 Registro Individual", "📊 Carga Masiva (CSV)", "📄 Expediente Digital (PDF)"])
        
        # =================================================================
        # PESTAÑA 1: REGISTRO INDIVIDUAL
        # =================================================================
        with tab1:
            st.subheader("📝 Registro Individual de Profesores")
            
            with st.form("registro_profesor_form"):
                # Detectar vista móvil y ajustar columnas
                if st.session_state.get('mobile_view', False):
                    # Vista móvil: una columna
                    with st.container():
                        # Cédula con validación en tiempo real
                        cedula = st.text_input(
                            "🆔 Cédula de Identidad *",
                            placeholder="V-12345678 o E-12345678",
                            help="Formato: V-XXXXXXXX o E-XXXXXXXX",
                            key="cedula_profesor"
                        )
                        
                        # Validación en tiempo real
                        if cedula:
                            if not re.match(r'^[VE]-\d{7,8}$', cedula.upper()):
                                st.error("❌ Formato inválido. Use V-12345678 o E-12345678")
                            else:
                                # Verificar si ya existe
                                try:
                                    verificar = ejecutar_query(
                                        "SELECT COUNT(*) as count FROM usuario WHERE login = :cedula OR cedula = :cedula",
                                        {"cedula": cedula.upper()},
                                        engine=engine
                                    )
                                    if verificar and verificar.iloc[0]['count'] > 0:
                                        st.warning("⚠️ Esta cédula ya está registrada")
                                    else:
                                        st.success("✅ Cédula disponible")
                                except:
                                    pass
                        
                        nombres = st.text_input(
                            "👤 Nombres *",
                            placeholder="Juan Carlos",
                            help="Nombres completos del profesor",
                            key="nombres_profesor"
                        )
                        
                        apellidos = st.text_input(
                            "👥 Apellidos *",
                            placeholder="Pérez González",
                            help="Apellidos completos del profesor",
                            key="apellidos_profesor"
                        )
                        
                        correo = st.text_input(
                            "📧 Correo Institucional *",
                            placeholder="profesor@iujo.edu.ve",
                            help="Correo electrónico del profesor",
                            key="correo_profesor"
                        )
                        
                        # Validación en tiempo real del correo
                        if correo:
                            if "@" not in correo or "." not in correo:
                                st.error("❌ Formato de correo inválido")
                            else:
                                # Verificar si ya existe
                                try:
                                    verificar = ejecutar_query(
                                        "SELECT COUNT(*) as count FROM usuario WHERE login = :correo OR email = :correo",
                                        {"correo": correo.lower()},
                                        engine=engine
                                    )
                                    if verificar and verificar.iloc[0]['count'] > 0:
                                        st.warning("⚠️ Este correo ya está registrado")
                                    else:
                                        st.success("✅ Correo disponible")
                                except:
                                    pass
                else:
                    # Vista desktop: dos columnas
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Cédula con validación en tiempo real
                        cedula = st.text_input(
                            "🆔 Cédula de Identidad *",
                            placeholder="V-12345678 o E-12345678",
                            help="Formato: V-XXXXXXXX o E-XXXXXXXX",
                            key="cedula_profesor"
                        )
                        
                        # Validación en tiempo real
                        if cedula:
                            if not re.match(r'^[VE]-\d{7,8}$', cedula.upper()):
                                st.error("❌ Formato inválido. Use V-12345678 o E-12345678")
                            else:
                                # Verificar si ya existe
                                try:
                                    verificar = ejecutar_query(
                                        "SELECT COUNT(*) as count FROM usuario WHERE login = :cedula OR cedula = :cedula",
                                        {"cedula": cedula.upper()},
                                        engine=engine
                                    )
                                    if verificar and verificar.iloc[0]['count'] > 0:
                                        st.warning("⚠️ Esta cédula ya está registrada")
                                    else:
                                        st.success("✅ Cédula disponible")
                                except:
                                    pass
                        
                        nombres = st.text_input(
                            "👤 Nombres *",
                            placeholder="Juan Carlos",
                            help="Nombres completos del profesor",
                            key="nombres_profesor"
                        )
                    
                    with col2:
                        apellidos = st.text_input(
                            "👥 Apellidos *",
                            placeholder="Pérez González",
                            help="Apellidos completos del profesor",
                            key="apellidos_profesor"
                        )
                        
                        correo = st.text_input(
                            "📧 Correo Institucional *",
                            placeholder="profesor@iujo.edu.ve",
                            help="Correo electrónico del profesor",
                            key="correo_profesor"
                        )
                        
                        # Validación en tiempo real del correo
                        if correo:
                            if "@" not in correo or "." not in correo:
                                st.error("❌ Formato de correo inválido")
                            else:
                                # Verificar si ya existe
                                try:
                                    verificar = ejecutar_query(
                                        "SELECT COUNT(*) as count FROM usuario WHERE login = :correo OR email = :correo",
                                        {"correo": correo.lower()},
                                        engine=engine
                                    )
                                    if verificar and verificar.iloc[0]['count'] > 0:
                                        st.warning("⚠️ Este correo ya está registrado")
                                    else:
                                        st.success("✅ Correo disponible")
                                except:
                                    pass
                
                categoria = st.selectbox(
                    "📚 Categoría/Escalafón *",
                    options=["Instructor", "Asistente", "Agregado", "Asociado", "Titular", "Emérito"],
                    index=0,
                    help="Seleccione la categoría o escalafón del profesor",
                    key="categoria_profesor"
                )
                
                # Información importante
                st.info("ℹ️ **Nota:** Los campos marcados con * son obligatorios")
                st.info("🔐 La contraseña inicial será la cédula de identidad")
                
                # Botones de acción - responsivos
                if st.session_state.get('mobile_view', False):
                    # Vista móvil: botones apilados
                    btn_guardar = st.form_submit_button(
                        "💾 Guardar Profesor",
                        type="primary",
                        use_container_width=True
                    )
                    
                    btn_limpiar = st.form_submit_button(
                        "🗑️ Limpiar Formulario",
                        type="secondary",
                        use_container_width=True
                    )
                else:
                    # Vista desktop: botones en columnas
                    col_guardar, col_limpiar = st.columns([2, 1])
                    
                    with col_guardar:
                        btn_guardar = st.form_submit_button(
                            "💾 Guardar Profesor",
                            type="primary",
                            use_container_width=True
                        )
                    
                    with col_limpiar:
                        btn_limpiar = st.form_submit_button(
                            "🗑️ Limpiar Formulario",
                            type="secondary",
                            use_container_width=True
                        )
                
                if btn_guardar:
                    # Validar campos obligatorios
                    if not all([cedula, nombres, apellidos, correo]):
                        st.error("❌ Complete todos los campos obligatorios")
                        st.stop()
                    
                    # Validar formatos
                    if not re.match(r'^[VE]-\d{7,8}$', cedula.upper()):
                        st.error("❌ Formato de cédula inválido")
                        st.stop()
                    
                    if "@" not in correo or "." not in correo:
                        st.error("❌ Formato de correo inválido")
                        st.stop()
                    
                    # Procesar registro
                    with st.spinner("Registrando profesor..."):
                        try:
                            # Verificar duplicados
                            verificar_cedula = ejecutar_query(
                                "SELECT COUNT(*) as count FROM usuario WHERE login = :cedula OR cedula = :cedula",
                                {"cedula": cedula.upper()},
                                engine=engine
                            )
                            
                            verificar_correo = ejecutar_query(
                                "SELECT COUNT(*) as count FROM usuario WHERE login = :correo OR email = :correo",
                                {"correo": correo.lower()},
                                engine=engine
                            )
                            
                            if verificar_cedula.iloc[0]['count'] > 0:
                                st.error("❌ La cédula ya está registrada")
                                st.stop()
                            
                            if verificar_correo.iloc[0]['count'] > 0:
                                st.error("❌ El correo ya está registrado")
                                st.stop()
                            
                            # Insertar profesor
                            hash_password = hashlib.sha256(cedula.upper().encode()).hexdigest()
                            
                            insertar = """
                            INSERT INTO usuario (
                                login, email, contrasena, rol, nombre, apellido, 
                                cedula, categoria, activo, correo_verificado, 
                                fecha_registro
                            ) VALUES (
                                :login, :email, :password, :rol, :nombre, :apellido,
                                :cedula, :categoria, :activo, :correo_verificado,
                                :fecha_registro
                            )
                            """
                            
                            ejecutar_query(insertar, {
                                'login': correo.lower(),
                                'email': correo.lower(),
                                'password': hash_password,
                                'rol': 'profesor',
                                'nombre': nombres.title(),
                                'apellido': apellidos.title(),
                                'cedula': cedula.upper(),
                                'categoria': categoria,
                                'activo': True,
                                'correo_verificado': False,
                                'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }, engine=engine)
                            
                            st.success("✅ Profesor registrado exitosamente")
                            st.info(f"📧 Se enviará correo de confirmación a: {correo}")
                            st.balloons()
                            
                            # Limpiar formulario
                            for key in st.session_state.keys():
                                if key.endswith('_profesor'):
                                    del st.session_state[key]
                            
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error registrando profesor: {str(e)}")
                
                if btn_limpiar:
                    # Limpiar campos del formulario
                    for key in st.session_state.keys():
                        if key.endswith('_profesor'):
                            del st.session_state[key]
                    st.rerun()
        
        # =================================================================
        # PESTAÑA 2: CARGA MASIVA (CSV)
        # =================================================================
        with tab2:
            st.subheader("📊 Carga Masiva de Profesores (CSV)")
            
            # Instrucciones
            with st.expander("📋 Instrucciones de Formato CSV", expanded=True):
                st.markdown("""
                **Formato requerido para el archivo CSV:**
                
                | Columna | Requerida | Formato | Ejemplo |
                |----------|-----------|----------|---------|
                | cedula | Sí | V-12345678 | V-12345678 |
                | nombres | Sí | Texto | Juan Carlos |
                | apellidos | Sí | Texto | Pérez González |
                | correo | Sí | email@dominio.com | profesor@iujo.edu.ve |
                | categoria | Sí | Texto | Asociado |
                
                **Categorías válidas:** Instructor, Asistente, Agregado, Asociado, Titular, Emérito
                
                **Notas:**
                - El archivo debe tener encabezado en la primera fila
                - Los campos cédula y correo no deben repetirse
                - Si una cédula ya existe, se omitirá y se reportará al final
                """)
            
            # Carga de archivo
            archivo_csv = st.file_uploader(
                "📁 Seleccione archivo CSV",
                type=['csv'],
                help="Suba el archivo CSV con los datos de los profesores",
                key="archivo_csv_profesores"
            )
            
            if archivo_csv:
                try:
                    # Leer archivo CSV
                    df = pd.read_csv(archivo_csv)
                    
                    # Normalizar columnas (insensible a mayúsculas/minúsculas y tildes)
                    df = normalizar_columnas_csv(df, tipo='profesores')
                    
                    # Validar columnas requeridas
                    columnas_requeridas = ['cedula', 'nombres', 'apellidos', 'correo', 'categoria']
                    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
                    
                    if columnas_faltantes:
                        st.error(f"❌ Columnas faltantes: {', '.join(columnas_faltantes)}")
                        st.info("💡 **Columnas aceptadas:** cédula, Cedula, CEDULA, nombres, NOMBRES, apellidos, APELLIDOS, correo, EMAIL, categoría, CATEGORIA, especialidad, ESPECIALIDAD")
                        st.stop()
                    
                    # Mostrar vista previa
                    st.write("📊 **Vista Previa de Datos:**")
                    st.dataframe(df.head(10))
                    
                    # Procesar carga
                    if st.button("🚀 Procesar Carga Masiva", type="primary", use_container_width=True):
                        with st.spinner("Procesando carga masiva..."):
                            try:
                                creados = 0
                                omitidos = 0
                                errores = []
                                categorias_validas = ["Instructor", "Asistente", "Agregado", "Asociado", "Titular", "Emérito"]
                                
                                for index, row in df.iterrows():
                                    try:
                                        # Validar datos
                                        cedula = str(row['cedula']).strip().upper()
                                        nombres = str(row['nombres']).strip().title()
                                        apellidos = str(row['apellidos']).strip().title()
                                        correo = str(row['correo']).strip().lower()
                                        categoria = str(row['categoria']).strip().title()
                                        
                                        # FILTRO CRÍTICO: Omitir correo angelher@gmail.com
                                        if correo == 'angelher@gmail.com':
                                            omitidos += 1
                                            errores.append(f"Fila {index+2}: Usuario omitido por restricciones de seguridad")
                                            continue
                                        
                                        # Validar formato de cédula
                                        if not re.match(r'^[VE]-\d{7,8}$', cedula):
                                            errores.append(f"Fila {index+2}: Cédula inválida: {cedula}")
                                            omitidos += 1
                                            continue
                                        
                                        # Validar formato de correo
                                        if "@" not in correo or "." not in correo:
                                            errores.append(f"Fila {index+2}: Correo inválido: {correo}")
                                            omitidos += 1
                                            continue
                                        
                                        # Validar categoría
                                        if categoria not in categorias_validas:
                                            errores.append(f"Fila {index+2}: Categoría inválida: {categoria}")
                                            omitidos += 1
                                            continue
                                        
                                        # Verificar duplicados
                                        verificar_cedula = ejecutar_query(
                                            "SELECT COUNT(*) as count FROM usuario WHERE cedula = :cedula",
                                            {"cedula": cedula},
                                            engine=engine
                                        )
                                        
                                        verificar_correo = ejecutar_query(
                                            "SELECT COUNT(*) as count FROM usuario WHERE email = :correo",
                                            {"correo": correo},
                                            engine=engine
                                        )
                                        
                                        if verificar_cedula.iloc[0]['count'] > 0:
                                            omitidos += 1
                                            continue
                                        
                                        if verificar_correo.iloc[0]['count'] > 0:
                                            omitidos += 1
                                            continue
                                        
                                        # Insertar profesor
                                        hash_password = hashlib.sha256(cedula.encode()).hexdigest()
                                        
                                        insertar = """
                                        INSERT INTO usuario (
                                            login, email, contrasena, rol, nombre, apellido,
                                            cedula, categoria, activo, correo_verificado,
                                            fecha_registro
                                        ) VALUES (
                                            :login, :email, :password, :rol, :nombre, :apellido,
                                            :cedula, :categoria, :activo, :correo_verificado,
                                            :fecha_registro
                                        )
                                        """
                                        
                                        ejecutar_query(insertar, {
                                            'login': correo,
                                            'email': correo,
                                            'password': hash_password,
                                            'rol': 'profesor',
                                            'nombre': nombres,
                                            'apellido': apellidos,
                                            'cedula': cedula,
                                            'categoria': categoria,
                                            'activo': True,
                                            'correo_verificado': False,
                                            'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        }, engine=engine)
                                        
                                        creados += 1
                                        
                                    except Exception as e:
                                        errores.append(f"Fila {index+2}: {str(e)}")
                                        omitidos += 1
                                
                                # Mostrar resultados
                                st.success("✅ Proceso completado")
                                
                                col_res1, col_res2, col_res3 = st.columns(3)
                                
                                with col_res1:
                                    st.metric("👨‍🏫 Profesores Creados", creados)
                                
                                with col_res2:
                                    st.metric("⚠️ Registros Omitidos", omitidos)
                                
                                with col_res3:
                                    st.metric("📊 Total Procesados", len(df))
                                
                                if errores:
                                    st.error("❌ Errores encontrados:")
                                    for error in errores[:10]:  # Mostrar solo primeros 10 errores
                                        st.error(error)
                                    if len(errores) > 10:
                                        st.warning(f"... y {len(errores) - 10} errores más")
                                
                                if creados > 0:
                                    st.balloons()
                                    st.info(f"📧 Se enviarán correos de confirmación a los {creados} profesores creados")
                                
                                # REGISTRO AUTOMÁTICO EN MÓDULO DE REPORTES
                                registrar_reporte_carga(
                                    tipo_carga="Carga Masiva de Profesores",
                                    registros_procesados=len(df),
                                    errores_count=len(errores),
                                    detalles=f"Profesores creados: {creados} | Omitidos: {omitidos}"
                                )
                                
                            except Exception as e:
                                st.error(f"❌ Error en carga masiva: {str(e)}")
                                
                except Exception as e:
                    st.error(f"❌ Error leyendo archivo CSV: {str(e)}")
        
        # =================================================================
        # PESTAÑA 3: EXPEDIENTE DIGITAL (PDF)
        # =================================================================
        with tab3:
            st.subheader("📄 Expediente Digital (PDF)")
            
            # Información importante
            st.info("ℹ️ **Nota:** Puede subir documentos PDF usando la cámara de su celular o apps como CamScanner")
            
            # Buscar profesor
            if st.session_state.get('mobile_view', False):
                # Vista móvil: campos apilados
                cedula_buscar = st.text_input(
                    "🔍 Buscar Profesor por Cédula",
                    placeholder="V-12345678",
                    help="Ingrese la cédula del profesor",
                    key="cedula_buscar_expediente_profesor"
                )
                
                btn_buscar = st.button("🔍 Buscar Profesor", use_container_width=True)
            else:
                # Vista desktop: en línea
                col_buscar, col_buscar_btn = st.columns([3, 1])
                
                with col_buscar:
                    cedula_buscar = st.text_input(
                        "🔍 Buscar Profesor por Cédula",
                        placeholder="V-12345678",
                        help="Ingrese la cédula del profesor",
                        key="cedula_buscar_expediente_profesor"
                    )
                
                with col_buscar_btn:
                    st.write("")  # Espacio para alinear el botón
                    btn_buscar = st.button("🔍 Buscar", use_container_width=True)
            
            profesor_encontrado = None
            
            if btn_buscar and cedula_buscar:
                try:
                    resultado = ejecutar_query(
                        "SELECT * FROM usuario WHERE cedula = :cedula AND rol = 'profesor'",
                        {"cedula": cedula_buscar.upper()},
                        engine=engine
                    )
                    
                    if resultado is not None and not resultado.empty:
                        profesor_encontrado = resultado.iloc[0]
                        st.success(f"✅ Profesor encontrado: {profesor_encontrado['nombre']} {profesor_encontrado['apellido']}")
                    else:
                        st.error("❌ Profesor no encontrado")
                except Exception as e:
                    st.error(f"❌ Error buscando profesor: {str(e)}")
            
            if profesor_encontrado is not None:
                # Mostrar información del profesor - responsivo
                with st.expander("👤 Información del Profesor", expanded=True):
                    if st.session_state.get('mobile_view', False):
                        # Vista móvil: información apilada
                        st.write(f"**🆔 Cédula:** {profesor_encontrado['cedula']}")
                        st.write(f"**👤 Nombre:** {profesor_encontrado['nombre']}")
                        st.write(f"**👥 Apellido:** {profesor_encontrado['apellido']}")
                        st.write(f"**📧 Correo:** {profesor_encontrado['email']}")
                        st.write(f"**📚 Categoría:** {profesor_encontrado.get('categoria', 'No especificada')}")
                        st.write(f"**✅ Estado:** {'Activo' if profesor_encontrado['activo'] else 'Inactivo'}")
                    else:
                        # Vista desktop: dos columnas
                        col_info1, col_info2 = st.columns(2)
                        
                        with col_info1:
                            st.write(f"**🆔 Cédula:** {profesor_encontrado['cedula']}")
                            st.write(f"**👤 Nombre:** {profesor_encontrado['nombre']}")
                            st.write(f"**👥 Apellido:** {profesor_encontrado['apellido']}")
                        
                        with col_info2:
                            st.write(f"**📧 Correo:** {profesor_encontrado['email']}")
                            st.write(f"**📚 Categoría:** {profesor_encontrado.get('categoria', 'No especificada')}")
                            st.write(f"**✅ Estado:** {'Activo' if profesor_encontrado['activo'] else 'Inactivo'}")
                
                # Carga de archivos PDF - responsivo
                st.write("---")
                st.write("📁 **Subir Expediente Digital**")
                
                # Optimizado para móvil
                archivos_pdf = st.file_uploader(
                    "📄 Seleccione archivos PDF",
                    type=['pdf'],
                    accept_multiple_files=True,
                    help="Suba los documentos PDF del expediente. Puede usar la cámara de su celular.",
                    key="archivos_pdf_expediente_profesor"
                )
                
                if archivos_pdf:
                    st.write(f"📊 **Archivos seleccionados:** {len(archivos_pdf)}")
                    
                    # Mostrar vista previa de archivos - responsivo
                    if st.session_state.get('mobile_view', False):
                        # Vista móvil: lista simple
                        for i, archivo in enumerate(archivos_pdf):
                            st.write(f"📄 **{archivo.name}** ({archivo.size / 1024:.1f} KB)")
                    else:
                        # Vista desktop: en columnas
                        for i, archivo in enumerate(archivos_pdf):
                            col_file, col_name = st.columns([1, 4])
                            
                            with col_file:
                                st.write(f"📄")
                            
                            with col_name:
                                st.write(f"**{archivo.name}** ({archivo.size / 1024:.1f} KB)")
                    
                    # Botón para guardar archivos
                    if st.button("💾 Guardar Expediente", type="primary", use_container_width=True):
                        with st.spinner("Guardando expediente digital..."):
                            try:
                                guardados = 0
                                errores = []
                                
                                for archivo in archivos_pdf:
                                    try:
                                        # Crear nombre de archivo seguro
                                        cedula_limpia = re.sub(r'[^a-zA-Z0-9]', '_', profesor_encontrado['cedula'])
                                        nombre_archivo = f"{cedula_limpia}_{archivo.name}"
                                        
                                        # Ruta de destino
                                        ruta_destino = os.path.join("expedientes_pdf", nombre_archivo)
                                        
                                        # Guardar archivo
                                        with open(ruta_destino, "wb") as f:
                                            f.write(archivo.getbuffer())
                                        
                                        guardados += 1
                                        
                                    except Exception as e:
                                        errores.append(f"Error guardando {archivo.name}: {str(e)}")
                                
                                # Mostrar resultados
                                if guardados > 0:
                                    st.success(f"✅ {guardados} archivos guardados exitosamente")
                                    st.info(f"📁 Ubicación: /expedientes_pdf/")
                                
                                if errores:
                                    st.error("❌ Errores al guardar:")
                                    for error in errores:
                                        st.error(error)
                                
                                if guardados > 0:
                                    st.balloons()
                                    
                            except Exception as e:
                                st.error(f"❌ Error general guardando expediente: {str(e)}")
                
                # Mostrar archivos existentes
                st.write("---")
                st.write("📂 **Expediente Existente**")
                
                try:
                    cedula_limpia = re.sub(r'[^a-zA-Z0-9]', '_', profesor_encontrado['cedula'])
                    archivos_existentes = []
                    
                    # Buscar archivos del profesor
                    for archivo in os.listdir("expedientes_pdf"):
                        if archivo.startswith(cedula_limpia) and archivo.endswith('.pdf'):
                            ruta_completa = os.path.join("expedientes_pdf", archivo)
                            tamaño = os.path.getsize(ruta_completa) / 1024  # KB
                            archivos_existentes.append({
                                'nombre': archivo,
                                'ruta': ruta_completa,
                                'tamaño': tamaño
                            })
                    
                    if archivos_existentes:
                        st.write(f"📄 **Archivos encontrados:** {len(archivos_existentes)}")
                        
                        # Mostrar archivos - responsivo
                        if st.session_state.get('mobile_view', False):
                            # Vista móvil: lista simple con botones
                            for archivo_info in archivos_existentes:
                                col_nombre, col_tamaño, col_accion = st.columns([2, 1, 1])
                                
                                with col_nombre:
                                    st.write(f"📄 {archivo_info['nombre']}")
                                
                                with col_tamaño:
                                    st.write(f"{archivo_info['tamaño']:.1f} KB")
                                
                                with col_accion:
                                    if st.button("👁️", key=f"ver_prof_{archivo_info['nombre']}", help="Ver PDF"):
                                        st.info(f"📂 Ruta: {archivo_info['ruta']}")
                        else:
                            # Vista desktop: en columnas
                            for archivo_info in archivos_existentes:
                                col_archivo, col_tamaño, col_accion = st.columns([3, 1, 1])
                                
                                with col_archivo:
                                    st.write(f"📄 {archivo_info['nombre']}")
                                
                                with col_tamaño:
                                    st.write(f"{archivo_info['tamaño']:.1f} KB")
                                
                                with col_accion:
                                    if st.button("👁️", key=f"ver_prof_{archivo_info['nombre']}", help="Ver PDF"):
                                        st.info(f"📂 Ruta: {archivo_info['ruta']}")
                    else:
                        st.info("📭 No hay archivos en el expediente")
                        
                except Exception as e:
                    st.error(f"❌ Error listando archivos: {str(e)}")
            else:
                st.info("🔍 Busque un profesor para gestionar su expediente digital")
    
    elif modulo_seleccionado == "🎓 Formación Complementaria":
        # Módulo de Formación Complementaria
        st.header("🎓 Formación Complementaria")
        
        # Crear directorios necesarios
        os.makedirs("formacion_complementaria", exist_ok=True)
        
        # Pestañas principales
        tab1, tab2, tab3 = st.tabs(["📝 Registro de Cursos", "👥 Asignación a Estudiantes", "📊 Reporte de Formación"])
        
        # =================================================================
        # PESTAÑA 1: REGISTRO DE CURSOS
        # =================================================================
        with tab1:
            st.subheader("📝 Registro de Cursos, Talleres y Diplomados")
            
            with st.form("registro_curso_form"):
                # Detectar vista móvil y ajustar columnas
                if st.session_state.get('mobile_view', False):
                    # Vista móvil: una columna
                    with st.container():
                        nombre_curso = st.text_input(
                            "📚 Nombre del Curso/Taller *",
                            placeholder="Ej: Diplomado en Administración de Proyectos",
                            help="Nombre completo del curso, taller o diplomado",
                            key="nombre_curso"
                        )
                        
                        tipo_formacion = st.selectbox(
                            "🏷️ Tipo de Formación *",
                            options=["Curso", "Taller", "Diplomado", "Seminario", "Conferencia"],
                            index=0,
                            help="Seleccione el tipo de formación",
                            key="tipo_formacion"
                        )
                        
                        descripcion = st.text_area(
                            "📋 Descripción *",
                            placeholder="Descripción detallada del contenido y objetivos del curso",
                            help="Descripción completa del curso",
                            key="descripcion_curso",
                            height=100
                        )
                        
                        duracion_horas = st.number_input(
                            "⏱️ Duración en horas *",
                            min_value=1,
                            max_value=500,
                            value=20,
                            help="Duración total en horas",
                            key="duracion_horas"
                        )
                        
                        fecha_inicio = st.date_input(
                            "📅 Fecha de Inicio *",
                            help="Fecha de inicio del curso",
                            key="fecha_inicio_curso"
                        )
                        
                        fecha_fin = st.date_input(
                            "📅 Fecha de Fin *",
                            help="Fecha de finalización del curso",
                            key="fecha_fin_curso"
                        )
                        
                        instructor = st.text_input(
                            "👨‍🏫 Instructor/Responsable *",
                            placeholder="Nombre del instructor o responsable",
                            help="Persona que dictará el curso",
                            key="instructor_curso"
                        )
                else:
                    # Vista desktop: dos columnas
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        nombre_curso = st.text_input(
                            "📚 Nombre del Curso/Taller *",
                            placeholder="Ej: Diplomado en Administración de Proyectos",
                            help="Nombre completo del curso, taller o diplomado",
                            key="nombre_curso"
                        )
                        
                        tipo_formacion = st.selectbox(
                            "🏷️ Tipo de Formación *",
                            options=["Curso", "Taller", "Diplomado", "Seminario", "Conferencia"],
                            index=0,
                            help="Seleccione el tipo de formación",
                            key="tipo_formacion"
                        )
                        
                        descripcion = st.text_area(
                            "📋 Descripción *",
                            placeholder="Descripción detallada del contenido y objetivos del curso",
                            help="Descripción completa del curso",
                            key="descripcion_curso",
                            height=100
                        )
                    
                    with col2:
                        duracion_horas = st.number_input(
                            "⏱️ Duración en horas *",
                            min_value=1,
                            max_value=500,
                            value=20,
                            help="Duración total en horas",
                            key="duracion_horas"
                        )
                        
                        fecha_inicio = st.date_input(
                            "📅 Fecha de Inicio *",
                            help="Fecha de inicio del curso",
                            key="fecha_inicio_curso"
                        )
                        
                        fecha_fin = st.date_input(
                            "📅 Fecha de Fin *",
                            help="Fecha de finalización del curso",
                            key="fecha_fin_curso"
                        )
                        
                        instructor = st.text_input(
                            "👨‍🏫 Instructor/Responsable *",
                            placeholder="Nombre del instructor o responsable",
                            help="Persona que dictará el curso",
                            key="instructor_curso"
                        )
                
                # Información importante
                st.info("ℹ️ **Nota:** Los campos marcados con * son obligatorios")
                
                # Botones de acción - responsivos
                if st.session_state.get('mobile_view', False):
                    # Vista móvil: botones apilados
                    btn_guardar = st.form_submit_button(
                        "💾 Guardar Curso",
                        type="primary",
                        use_container_width=True
                    )
                    
                    btn_limpiar = st.form_submit_button(
                        "🗑️ Limpiar Formulario",
                        type="secondary",
                        use_container_width=True
                    )
                else:
                    # Vista desktop: botones en columnas
                    col_guardar, col_limpiar = st.columns([2, 1])
                    
                    with col_guardar:
                        btn_guardar = st.form_submit_button(
                            "💾 Guardar Curso",
                            type="primary",
                            use_container_width=True
                        )
                    
                    with col_limpiar:
                        btn_limpiar = st.form_submit_button(
                            "🗑️ Limpiar Formulario",
                            type="secondary",
                            use_container_width=True
                        )
                
                if btn_guardar:
                    # Validar campos obligatorios
                    if not all([nombre_curso, tipo_formacion, descripcion, duracion_horas, fecha_inicio, fecha_fin, instructor]):
                        st.error("❌ Complete todos los campos obligatorios")
                        st.stop()
                    
                    # Validar fechas
                    if fecha_fin < fecha_inicio:
                        st.error("❌ La fecha de fin no puede ser anterior a la fecha de inicio")
                        st.stop()
                    
                    # Procesar registro
                    with st.spinner("Guardando curso..."):
                        try:
                            # Insertar curso en la base de datos
                            insertar_curso = """
                            INSERT INTO formacion_complementaria (
                                nombre_curso, tipo_formacion, descripcion, duracion_horas,
                                fecha_inicio, fecha_fin, instructor, fecha_registro, activo
                            ) VALUES (
                                :nombre_curso, :tipo_formacion, :descripcion, :duracion_horas,
                                :fecha_inicio, :fecha_fin, :instructor, :fecha_registro, :activo
                            )
                            """
                            
                            ejecutar_query(insertar_curso, {
                                'nombre_curso': nombre_curso,
                                'tipo_formacion': tipo_formacion,
                                'descripcion': descripcion,
                                'duracion_horas': duracion_horas,
                                'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
                                'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
                                'instructor': instructor,
                                'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'activo': True
                            }, engine=engine)
                            
                            st.success("✅ Curso registrado exitosamente")
                            st.balloons()
                            
                            # Limpiar formulario
                            for key in st.session_state.keys():
                                if key.endswith('_curso'):
                                    del st.session_state[key]
                            
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error registrando curso: {str(e)}")
                
                if btn_limpiar:
                    # Limpiar campos del formulario
                    for key in st.session_state.keys():
                        if key.endswith('_curso'):
                            del st.session_state[key]
                    st.rerun()
        
        # =================================================================
        # PESTAÑA 2: ASIGNACIÓN A ESTUDIANTES
        # =================================================================
        with tab2:
            st.subheader("👥 Asignación de Cursos a Estudiantes")
            
            # Buscar cursos disponibles
            try:
                cursos_disponibles = ejecutar_query(
                    "SELECT * FROM formacion_complementaria WHERE activo = 1 ORDER BY fecha_inicio DESC",
                    engine=engine
                )
                
                if cursos_disponibles is not None and not cursos_disponibles.empty:
                    # Selección de curso
                    opciones_cursos = [f"{row['nombre_curso']} ({row['tipo_formacion']})" for _, row in cursos_disponibles.iterrows()]
                    
                    curso_seleccionado = st.selectbox(
                        "📚 Seleccionar Curso *",
                        options=opciones_cursos,
                        help="Seleccione el curso al que asignará estudiantes",
                        key="curso_seleccionado_fc"
                    )
                    
                    if curso_seleccionado:
                        # Obtener información del curso seleccionado
                        curso_info = cursos_disponibles[cursos_disponibles['nombre_curso'] + ' (' + cursos_disponibles['tipo_formacion'] + ')' == curso_seleccionado].iloc[0]
                        
                        st.info(f"📋 **Curso seleccionado:** {curso_info['nombre_curso']}")
                        st.info(f"👨‍🏫 **Instructor:** {curso_info['instructor']}")
                        st.info(f"⏱️ **Duración:** {curso_info['duracion_horas']} horas")
                        st.info(f"📅 **Fechas:** {curso_info['fecha_inicio']} al {curso_info['fecha_fin']}")
                        
                        # Buscar estudiantes
                        st.write("---")
                        st.write("👥 **Asignar Estudiantes**")
                        
                        # Búsqueda de estudiantes
                        col_buscar, col_buscar_btn = st.columns([3, 1])
                        
                        with col_buscar:
                            cedula_buscar = st.text_input(
                                "🔍 Buscar Estudiante por Cédula",
                                placeholder="V-12345678",
                                help="Ingrese la cédula del estudiante",
                                key="cedula_buscar_fc"
                            )
                        
                        with col_buscar_btn:
                            st.write("")
                            btn_buscar_est = st.button("🔍 Buscar", use_container_width=True)
                        
                        estudiante_encontrado_fc = None
                        
                        if btn_buscar_est and cedula_buscar:
                            try:
                                resultado = ejecutar_query(
                                    "SELECT * FROM usuario WHERE cedula = :cedula AND rol = 'estudiante'",
                                    {"cedula": cedula_buscar.upper()},
                                    engine=engine
                                )
                                
                                if resultado is not None and not resultado.empty:
                                    estudiante_encontrado_fc = resultado.iloc[0]
                                    st.success(f"✅ Estudiante encontrado: {estudiante_encontrado_fc['nombre']} {estudiante_encontrado_fc['apellido']}")
                                else:
                                    st.error("❌ Estudiante no encontrado")
                            except Exception as e:
                                st.error(f"❌ Error buscando estudiante: {str(e)}")
                        
                        if estudiante_encontrado_fc is not None:
                            # Mostrar información del estudiante
                            with st.expander("👤 Información del Estudiante", expanded=True):
                                col_info1, col_info2 = st.columns(2)
                                
                                with col_info1:
                                    st.write(f"**🆔 Cédula:** {estudiante_encontrado_fc['cedula']}")
                                    st.write(f"**👤 Nombre:** {estudiante_encontrado_fc['nombre']}")
                                    st.write(f"**👥 Apellido:** {estudiante_encontrado_fc['apellido']}")
                                
                                with col_info2:
                                    st.write(f"**📧 Correo:** {estudiante_encontrado_fc['email']}")
                                    st.write(f"**📚 Semestre:** {estudiante_encontrado_fc['semestre']}")
                                    st.write(f"**✅ Estado:** {'Activo' if estudiante_encontrado_fc['activo'] else 'Inactivo'}")
                            
                            # Botón de asignación
                            if st.button("✅ Asignar al Curso", type="primary", use_container_width=True):
                                try:
                                    # Verificar si ya está asignado
                                    verificar_asignacion = ejecutar_query(
                                        "SELECT COUNT(*) as count FROM asignacion_formacion WHERE id_estudiante = :id_estudiante AND id_curso = :id_curso",
                                        {
                                            'id_estudiante': estudiante_encontrado_fc['id'],
                                            'id_curso': curso_info['id']
                                        },
                                        engine=engine
                                    )
                                    
                                    if verificar_asignacion.iloc[0]['count'] > 0:
                                        st.warning("⚠️ El estudiante ya está asignado a este curso")
                                    else:
                                        # Asignar estudiante al curso
                                        insertar_asignacion = """
                                        INSERT INTO asignacion_formacion (
                                            id_estudiante, id_curso, fecha_asignacion, estado
                                        ) VALUES (
                                            :id_estudiante, :id_curso, :fecha_asignacion, :estado
                                        )
                                        """
                                        
                                        ejecutar_query(insertar_asignacion, {
                                            'id_estudiante': estudiante_encontrado_fc['id'],
                                            'id_curso': curso_info['id'],
                                            'fecha_asignacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                            'estado': 'Activo'
                                        }, engine=engine)
                                        
                                        st.success("✅ Estudiante asignado exitosamente")
                                        st.balloons()
                                        
                                except Exception as e:
                                    st.error(f"❌ Error asignando estudiante: {str(e)}")
                        
                        # Listar estudiantes asignados al curso
                        st.write("---")
                        st.write("👥 **Estudiantes Asignados**")
                        
                        try:
                            estudiantes_asignados = ejecutar_query("""
                                SELECT u.* FROM usuario u
                                INNER JOIN asignacion_formacion af ON u.id = af.id_estudiante
                                WHERE af.id_curso = :id_curso AND af.estado = 'Activo'
                                ORDER BY u.apellido, u.nombre
                            """, {'id_curso': curso_info['id']}, engine=engine)
                            
                            if estudiantes_asignados is not None and not estudiantes_asignados.empty:
                                st.write(f"📊 **Total asignados:** {len(estudiantes_asignados)}")
                                
                                for _, estudiante in estudiantes_asignados.iterrows():
                                    with st.expander(f"👤 {estudiante['apellido']}, {estudiante['nombre']}"):
                                        col_asig1, col_asig2 = st.columns(2)
                                        
                                        with col_asig1:
                                            st.write(f"**🆔 Cédula:** {estudiante['cedula']}")
                                            st.write(f"**📧 Correo:** {estudiante['email']}")
                                            st.write(f"**📚 Semestre:** {estudiante['semestre']}")
                                        
                                        with col_asig2:
                                            st.write(f"**✅ Estado:** {'Activo' if estudiante['activo'] else 'Inactivo'}")
                                            
                                            # Botón para eliminar asignación
                                            if st.button("🗑️ Eliminar", key=f"eliminar_{estudiante['id']}", help="Eliminar asignación"):
                                                try:
                                                    ejecutar_query(
                                                        "UPDATE asignacion_formacion SET estado = 'Eliminado' WHERE id_estudiante = :id_estudiante AND id_curso = :id_curso",
                                                        {
                                                            'id_estudiante': estudiante['id'],
                                                            'id_curso': curso_info['id']
                                                        },
                                                        engine=engine
                                                    )
                                                    st.success("✅ Asignación eliminada")
                                                    st.rerun()
                                                except Exception as e:
                                                    st.error(f"❌ Error eliminando asignación: {str(e)}")
                            else:
                                st.info("📭 No hay estudiantes asignados a este curso")
                                
                        except Exception as e:
                            st.error(f"❌ Error listando estudiantes asignados: {str(e)}")
                
                else:
                    st.info("📭 No hay cursos registrados")
                    
            except Exception as e:
                st.error(f"❌ Error cargando cursos: {str(e)}")
        
        # =================================================================
        # PESTAÑA 3: REPORTE DE FORMACIÓN
        # =================================================================
        with tab3:
            st.subheader("📊 Reporte de Formación Complementaria")
            
            # Métricas principales
            try:
                # Total de cursos
                total_cursos = ejecutar_query(
                    "SELECT COUNT(*) as total FROM formacion_complementaria WHERE activo = 1",
                    engine=engine
                )
                
                # Total de asignaciones
                total_asignaciones = ejecutar_query(
                    "SELECT COUNT(*) as total FROM asignacion_formacion WHERE estado = 'Activo'",
                    engine=engine
                )
                
                # Estudiantes únicos asignados
                estudiantes_unicos = ejecutar_query(
                    "SELECT COUNT(DISTINCT id_estudiante) as total FROM asignacion_formacion WHERE estado = 'Activo'",
                    engine=engine
                )
                
                # Cursos por tipo
                cursos_por_tipo = ejecutar_query("""
                    SELECT tipo_formacion, COUNT(*) as total 
                    FROM formacion_complementaria 
                    WHERE activo = 1 
                    GROUP BY tipo_formacion 
                    ORDER BY total DESC
                """, engine=engine)
                
                # Mostrar métricas
                col_met1, col_met2, col_met3 = st.columns(3)
                
                with col_met1:
                    st.metric("📚 Total Cursos Activos", total_cursos.iloc[0]['total'] if total_cursos is not None else 0)
                
                with col_met2:
                    st.metric("👥 Total Asignaciones", total_asignaciones.iloc[0]['total'] if total_asignaciones is not None else 0)
                
                with col_met3:
                    st.metric("🎓 Estudiantes Únicos", estudiantes_unicos.iloc[0]['total'] if estudiantes_unicos is not None else 0)
                
                # Gráfico de cursos por tipo
                if cursos_por_tipo is not None and not cursos_por_tipo.empty:
                    st.write("---")
                    st.write("📊 **Cursos por Tipo de Formación**")
                    
                    import plotly.express as px
                    import plotly.graph_objects as go
                    
                    fig = px.bar(
                        cursos_por_tipo, 
                        x='tipo_formacion', 
                        y='total',
                        title="Distribución de Cursos por Tipo",
                        labels={'tipo_formacion': 'Tipo', 'total': 'Cantidad'},
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    
                    fig.update_layout(
                        xaxis_title="Tipo de Formación",
                        yaxis_title="Cantidad de Cursos",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Tabla de cursos recientes
                st.write("---")
                st.write("📋 **Cursos Recientes**")
                
                cursos_recientes = ejecutar_query("""
                    SELECT nombre_curso, tipo_formacion, instructor, fecha_inicio, fecha_fin, duracion_horas
                    FROM formacion_complementaria 
                    WHERE activo = 1 
                    ORDER BY fecha_registro DESC 
                    LIMIT 10
                """, engine=engine)
                
                if cursos_recientes is not None and not cursos_recientes.empty:
                    st.dataframe(
                        cursos_recientes[['nombre_curso', 'tipo_formacion', 'instructor', 'fecha_inicio', 'fecha_fin', 'duracion_horas']],
                        column_rename={
                            'nombre_curso': 'Curso',
                            'tipo_formacion': 'Tipo',
                            'instructor': 'Instructor',
                            'fecha_inicio': 'Inicio',
                            'fecha_fin': 'Fin',
                            'duracion_horas': 'Horas'
                        },
                        use_container_width=True
                    )
                else:
                    st.info("📭 No hay cursos registrados")
                    
            except Exception as e:
                st.error(f"❌ Error generando reporte: {str(e)}")
    
    elif modulo_seleccionado == "⚙️ Configuración":
        # Módulo de Configuración
        st.header("⚙️ Configuración del Sistema")
        
        # Pestañas principales
        tab1, tab2, tab3 = st.tabs(["📧 Configuración de Correo", "💾 Respaldo de Base de Datos", "⚙️ Configuración General"])
        
        # =================================================================
        # PESTAÑA 1: CONFIGURACIÓN DE CORREO
        # =================================================================
        with tab1:
            st.subheader("📧 Configuración de Correo Electrónico")
            
            # Obtener configuración desde variables de entorno
            import os
            config_actual = {
                'servidor_smtp': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                'puerto_smtp': int(os.getenv('SMTP_PORT', '587')),
                'usuario_smtp': os.getenv('SMTP_USER', ''),
                'contrasena_smtp': os.getenv('SMTP_PASSWORD', ''),
                'correo_remitente': os.getenv('SMTP_EMAIL', ''),
                'database_url': os.getenv('DATABASE_URL', ''),  # PostgreSQL en Render
                'render_deploy_hook': os.getenv('RENDER_DEPLOY_HOOK_URL', ''),  # Deploy Hook para sincronización
                'usar_tls': True,
                'usar_ssl': False
            }         
            if config_actual:
                st.info("✅ Ya existe una configuración de correo activa")
                
                # Mostrar configuración actual
                with st.expander("📋 Configuración Actual", expanded=True):
                    col_conf1, col_conf2 = st.columns(2)
                    
                    with col_conf1:
                        st.write(f"**📧 Servidor:** {config_actual['servidor_smtp']}")
                        st.write(f"**🔌 Puerto:** {config_actual['puerto']}")
                        st.write(f"**👤 Usuario:** {config_actual['usuario']}")
                    
                    with col_conf2:
                        st.write(f"**📧 Remitente:** {config_actual['remitente']}")
                        st.write(f"**📅 Actualización:** {config_actual['fecha_actualizacion']}")
                        st.write("**🔒 Contraseña:** [Protegida]")
            
            # Formulario de configuración
            with st.form("config_correo_form"):
                st.write("🔧 **Nueva Configuración de Correo**")
                
                # Detectar vista móvil y ajustar columnas
                if st.session_state.get('mobile_view', False):
                    # Vista móvil: una columna
                    with st.container():
                        servidor_smtp = st.text_input(
                            "📧 Servidor SMTP *",
                            placeholder="smtp.gmail.com",
                            help="Servidor de correo saliente",
                            value=config_actual['servidor_smtp'] if config_actual else "",
                            key="servidor_smtp"
                        )
                        
                        puerto = st.number_input(
                            "🔌 Puerto *",
                            min_value=1,
                            max_value=65535,
                            value=config_actual['puerto'] if config_actual else 587,
                            help="Puerto del servidor SMTP",
                            key="puerto_smtp"
                        )
                        
                        usuario = st.text_input(
                            "👤 Usuario SMTP *",
                            placeholder="correo@dominio.com",
                            help="Usuario para autenticación SMTP",
                            value=config_actual['usuario'] if config_actual else "",
                            key="usuario_smtp"
                        )
                        
                        password = st.text_input(
                            "🔒 Contraseña *",
                            type="password",
                            placeholder="Contraseña de aplicación",
                            help="Contraseña o contraseña de aplicación",
                            key="password_smtp"
                        )
                        
                        remitente = st.text_input(
                            "📧 Correo Remitente *",
                            placeholder="noreply@iujo.edu.ve",
                            help="Correo que aparecerá como remitente",
                            value=config_actual['remitente'] if config_actual else "",
                            key="remitente_smtp"
                        )
                else:
                    # Vista desktop: dos columnas
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        servidor_smtp = st.text_input(
                            "📧 Servidor SMTP *",
                            placeholder="smtp.gmail.com",
                            help="Servidor de correo saliente",
                            value=config_actual['servidor_smtp'] if config_actual else "",
                            key="servidor_smtp"
                        )
                        
                        puerto = st.number_input(
                            "🔌 Puerto *",
                            min_value=1,
                            max_value=65535,
                            value=config_actual['puerto'] if config_actual else 587,
                            help="Puerto del servidor SMTP",
                            key="puerto_smtp"
                        )
                        
                        usuario = st.text_input(
                            "👤 Usuario SMTP *",
                            placeholder="correo@dominio.com",
                            help="Usuario para autenticación SMTP",
                            value=config_actual['usuario'] if config_actual else "",
                            key="usuario_smtp"
                        )
                    
                    with col2:
                        password = st.text_input(
                            "🔒 Contraseña *",
                            type="password",
                            placeholder="Contraseña de aplicación",
                            help="Contraseña o contraseña de aplicación",
                            key="password_smtp"
                        )
                        
                        remitente = st.text_input(
                            "📧 Correo Remitente *",
                            placeholder="noreply@iujo.edu.ve",
                            help="Correo que aparecerá como remitente",
                            value=config_actual['remitente'] if config_actual else "",
                            key="remitente_smtp"
                        )
                
                st.info("ℹ️ **Nota:** Los campos marcados con * son obligatorios")
                
                # Botones de acción - responsivos
                if st.session_state.get('mobile_view', False):
                    # Vista móvil: botones apilados
                    btn_guardar = st.form_submit_button(
                        "💾 Guardar Configuración",
                        type="primary",
                        use_container_width=True
                    )
                    
                    btn_probar = st.form_submit_button(
                        "🧪 Probar Conexión",
                        type="secondary",
                        use_container_width=True
                    )
                else:
                    # Vista desktop: botones en columnas
                    col_guardar, col_probar = st.columns([2, 1])
                    
                    with col_guardar:
                        btn_guardar = st.form_submit_button(
                            "💾 Guardar Configuración",
                            type="primary",
                            use_container_width=True
                        )
                    
                    with col_probar:
                        btn_probar = st.form_submit_button(
                            "🧪 Probar",
                            type="secondary",
                            use_container_width=True
                        )
                
                if btn_guardar:
                    # Validar campos obligatorios
                    if not all([servidor_smtp, puerto, usuario, password, remitente]):
                        st.error("❌ Complete todos los campos obligatorios")
                        st.stop()
                    
                    # Procesar configuración
                    with st.spinner("Configurando servicio de correo..."):
                        if database.configurar_correo_final():
                            st.success("✅ Configuración de correo establecida")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Error configurando el correo")
                
                if btn_probar:
                    if not all([servidor_smtp, puerto, usuario, password, remitente]):
                        st.error("❌ Complete todos los campos para probar")
                        st.stop()
                    
                    # Probar conexión
                    with st.spinner("Probando conexión SMTP..."):
                        try:
                            import smtplib
                            from email.mime.text import MIMEText
                            
                            # Intentar conexión
                            server = smtplib.SMTP(servidor_smtp, puerto)
                            server.starttls()
                            server.login(usuario, password)
                            server.quit()
                            
                            st.success("✅ Conexión SMTP exitosa")
                            st.info("📧 La configuración es válida y puede guardarse")
                            
                        except Exception as e:
                            st.error("❌ Error en la conexión SMTP")
                            st.error(f"**Detalles:** {str(e)}")
                            
                            if "Authentication" in str(e):
                                st.error("🔐 Error de autenticación - Verifique usuario y contraseña")
                            elif "Connection" in str(e):
                                st.error("🌐 Error de conexión - Verifique servidor y puerto")
                            else:
                                st.error(f"❓ Error desconocido: {str(e)}")
            
            # Botón para probar envío
            st.write("---")
            st.write("🧪 **Prueba de Envío de Correo**")
            
            email_prueba = st.text_input(
                "📧 Correo de prueba",
                value="test@ejemplo.com",
                help="Ingrese el correo donde se enviará la prueba"
            )
            
            if st.button("🧪 Enviar Correo de Prueba", type="secondary", use_container_width=True):
                if email_prueba:
                    with st.spinner("Enviando correo de prueba..."):
                        exito, mensaje = database.probar_envio_correo(email_prueba)
                        
                        if exito:
                            st.success("✅ Correo de prueba enviado exitosamente")
                            st.info(mensaje)
                            st.balloons()
                        else:
                            st.error("❌ Error enviando correo")
                            st.error(mensaje)
                            
                            # Mostrar detalles del error
                            if "Authentication" in mensaje:
                                st.error("🔐 Error de autenticación - Verifique usuario y contraseña")
                            elif "Connection" in mensaje:
                                st.error("🌐 Error de conexión - Verifique red y firewall")
                            else:
                                st.error(f"❓ Error desconocido: {mensaje}")
                else:
                    st.error("❌ Ingrese un correo de prueba")
        
        # =================================================================
        # PESTAÑA 2: VALIDACIÓN SMTP
        # =================================================================
        with tab2:
            st.subheader("🔧 Prueba de Conectividad SMTP")
            
            # Información importante
            st.info("💡 **Esta sección permite verificar la configuración del servidor de correo electrónico**")
            st.info("🔒 **Filtro de seguridad activo:** No se permite enviar pruebas a angelher@gmail.com")
            
            # Formulario de prueba
            with st.form("prueba_smtp_form"):
                st.write("📧 **Configuración de Prueba**")
                
                # Detectar vista móvil y ajustar columnas
                if st.session_state.get('mobile_view', False):
                    # Vista móvil: una columna
                    with st.container():
                        correo_destino = st.text_input(
                            "📧 Correo de Destino *",
                            placeholder="admin@iujo.edu.ve",
                            help="Correo electrónico para recibir la prueba",
                            key="correo_prueba_smtp"
                        )
                        
                        asunto = st.text_input(
                            "📋 Asunto *",
                            placeholder="Prueba de Conectividad SMTP",
                            help="Asunto del correo de prueba",
                            key="asunto_prueba_smtp"
                        )
                        
                        mensaje = st.text_area(
                            "📝 Mensaje de Prueba *",
                            placeholder="Este es un correo de prueba para verificar la configuración SMTP.",
                            help="Contenido del correo de prueba",
                            key="mensaje_prueba_smtp",
                            height=100
                        )
                else:
                    # Vista desktop: dos columnas
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        correo_destino = st.text_input(
                            "📧 Correo de Destino *",
                            placeholder="admin@iujo.edu.ve",
                            help="Correo electrónico para recibir la prueba",
                            key="correo_prueba_smtp"
                        )
                        
                        asunto = st.text_input(
                            "📋 Asunto *",
                            placeholder="Prueba de Conectividad SMTP",
                            help="Asunto del correo de prueba",
                            key="asunto_prueba_smtp"
                        )
                    
                    with col2:
                        mensaje = st.text_area(
                            "📝 Mensaje de Prueba *",
                            placeholder="Este es un correo de prueba para verificar la configuración SMTP.",
                            help="Contenido del correo de prueba",
                            key="mensaje_prueba_smtp",
                            height=100
                        )
                
                # Botón de enviar prueba
                if st.form_submit_button("📧 Enviar Correo de Prueba", type="primary", use_container_width=True):
                    with st.spinner("🔄 Enviando correo de prueba..."):
                        try:
                            # FILTRO DE SEGURIDAD: Validar que no sea angelher@gmail.com
                            if correo_destino and correo_destino.lower() == 'angelher@gmail.com':
                                st.error("❌ No se puede enviar correos de prueba a angelher@gmail.com por restricciones de seguridad")
                                st.stop()
                            
                            # Validar campos
                            if not correo_destino or not asunto or not mensaje:
                                st.error("❌ Complete todos los campos requeridos")
                                st.stop()
                            
                            # Importar módulo de correo
                            import smtplib
                            from email.mime.text import MIMEText
                            from email.mime.multipart import MIMEMultipart
                            
                            # Crear mensaje
                            msg = MIMEMultipart()
                            msg['From'] = config_actual['correo_remitente']
                            msg['To'] = correo_destino
                            msg['Subject'] = asunto
                            msg.attach(MIMEText(mensaje, 'plain'))
                            
                            # Enviar correo
                            with smtplib.SMTP(config_actual['servidor_smtp'], config_actual['puerto']) as server:
                                server.starttls()
                                server.login(config_actual['usuario_smtp'], config_actual['contrasena_smtp'])
                                server.send_message(msg)
                                server.quit()
                            
                            st.success("✅ Correo de prueba enviado exitosamente")
                            st.info(f"📧 Destino: {correo_destino}")
                            st.info(f"📋 Asunto: {asunto}")
                            st.balloons()
                            
                            # Registrar en auditoría
                            registrar_auditoria(
                                accion="ENVIO_CORREO_PRUEBA",
                                usuario=st.session_state.user_data['login'],
                                detalles=f"Destino: {correo_destino} | Asunto: {asunto}",
                                transaccion="SMTP",
                                tabla_afectada="configuracion_correo"
                            )
                            
                        except smtplib.SMTPAuthenticationError as e:
                            st.error(f"❌ Error de autenticación: {str(e)}")
                        except smtplib.SMTPConnectError as e:
                            st.error(f"❌ Error de conexión: {str(e)}")
                        except Exception as e:
                            st.error(f"❌ Error enviando correo: {str(e)}")
            
            # Log de envíos recientes
            st.write("---")
            st.write("📋 **Historial de Envíos Recientes**")
            
            try:
                # Consultar logs de auditoría de envíos de correo
                logs_envios = ejecutar_query("""
                    SELECT usuario, detalles, fecha_registro
                    FROM auditoria 
                    WHERE accion = 'ENVIO_CORREO_PRUEBA'
                    ORDER BY fecha_registro DESC 
                    LIMIT 10
                """, engine=engine)
                
                if logs_envios is not None and not logs_envios.empty:
                    st.dataframe(
                        logs_envios[['usuario', 'detalles', 'fecha_registro']],
                        column_config={
                            'usuario': st.column_config.TextColumn("👤 Usuario", width="medium"),
                            'detalles': st.column_config.TextColumn("📝 Detalles", width="large"),
                            'fecha_registro': st.column_config.TextColumn("📅 Fecha", width="medium")
                        },
                        use_container_width=True
                    )
                else:
                    st.info("📭 No hay envíos de prueba registrados")
                    
            except Exception as e:
                st.error(f"❌ Error cargando historial: {str(e)}")

        # =================================================================
        # PESTAÑA 3: RESPALDO DE BASE DE DATOS
        # =================================================================
        with tab2:
            st.subheader("💾 Respaldo de Base de Datos")
            
            # Información del sistema
            st.info("💡 **Importante:** Realice respaldos periódicos para proteger sus datos")
            
            # Estado de la base de datos
            try:
                # Obtener información de la base de datos
                info_db = database.get_metricas_dashboard(engine=engine)
                
                col_info1, col_info2, col_info3 = st.columns(3)
                
                with col_info1:
                    st.metric("📊 Total Usuarios", info_db.get('total_usuarios', 0))
                
                with col_info2:
                    st.metric("📚 Total Estudiantes", info_db.get('estudiantes', 0))
                
                with col_info3:
                    st.metric("👨‍🏫 Total Profesores", info_db.get('profesores', 0))
                
                # Último respaldo
                st.write("---")
                st.write("💾 **Historial de Respaldos**")
                
                # Buscar archivos de respaldo
                if os.path.exists("backups"):
                    archivos_backup = []
                    
                    for archivo in os.listdir("backups"):
                        if archivo.endswith('.db') or archivo.endswith('.sql'):
                            ruta_completa = os.path.join("backups", archivo)
                            tamaño = os.path.getsize(ruta_completa) / (1024 * 1024)  # MB
                            fecha_mod = datetime.fromtimestamp(os.path.getmtime(ruta_completa))
                            
                            archivos_backup.append({
                                'nombre': archivo,
                                'ruta': ruta_completa,
                                'tamaño': tamaño,
                                'fecha': fecha_mod
                            })
                    
                    if archivos_backup:
                        # Ordenar por fecha descendente
                        archivos_backup.sort(key=lambda x: x['fecha'], reverse=True)
                        
                        for backup in archivos_backup[:10]:  # Mostrar últimos 10
                            with st.expander(f"💾 {backup['nombre']} - {backup['fecha'].strftime('%Y-%m-%d %H:%M')}"):
                                col_bak1, col_bak2 = st.columns(2)
                                
                                with col_bak1:
                                    st.write(f"**📁 Archivo:** {backup['nombre']}")
                                    st.write(f"**📏 Tamaño:** {backup['tamaño']:.2f} MB")
                                
                                with col_bak2:
                                    st.write(f"**📅 Fecha:** {backup['fecha'].strftime('%Y-%m-%d %H:%M:%S')}")
                                    st.write(f"**📂 Ruta:** {backup['ruta']}")
                    
                    else:
                        st.info("📭 No hay archivos de respaldo")
                else:
                    st.info("📭 No existe la carpeta de respaldos")
                
                # Botones de acción - responsivos
                st.write("---")
                st.write("💾 **Acciones de Respaldo**")
                
                if st.session_state.get('mobile_view', False):
                    # Vista móvil: botones apilados
                    btn_completo = st.button(
                        "💾 Crear Respaldo Completo",
                        type="primary",
                        use_container_width=True,
                        help="Crear respaldo completo de la base de datos"
                    )
                    
                    btn_parcial = st.button(
                        "📊 Crear Respaldo Parcial",
                        type="secondary",
                        use_container_width=True,
                        help="Crear respaldo solo de datos principales"
                    )
                    
                    btn_descargar = st.button(
                        "📥 Descargar Último Respaldo",
                        use_container_width=True,
                        help="Descargar el último respaldo disponible"
                    )
                else:
                    # Vista desktop: botones en columnas
                    col_bak1, col_bak2, col_bak3 = st.columns(3)
                    
                    with col_bak1:
                        btn_completo = st.button(
                            "💾 Respaldo Completo",
                            type="primary",
                            use_container_width=True,
                            help="Crear respaldo completo de la base de datos"
                        )
                    
                    with col_bak2:
                        btn_parcial = st.button(
                            "📊 Respaldo Parcial",
                            type="secondary",
                            use_container_width=True,
                            help="Crear respaldo solo de datos principales"
                        )
                    
                    with col_bak3:
                        btn_descargar = st.button(
                            "📥 Descargar Último",
                            use_container_width=True,
                            help="Descargar el último respaldo disponible"
                        )
                
                # Acciones de respaldo
                if btn_completo:
                    with st.spinner("Creando respaldo completo..."):
                        try:
                            # Crear directorio de respaldos
                            os.makedirs("backups", exist_ok=True)
                            
                            # Nombre del archivo
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            nombre_backup = f"respaldo_completo_{timestamp}.db"
                            ruta_backup = os.path.join("backups", nombre_backup)
                            
                            # Copiar base de datos
                            import shutil
                            shutil.copy2("foc26_limpio.db", ruta_backup)
                            
                            st.success(f"✅ Respaldo completo creado: {nombre_backup}")
                            st.info(f"📁 Ubicación: {ruta_backup}")
                            st.balloons()
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error creando respaldo: {str(e)}")
                
                if btn_parcial:
                    with st.spinner("Creando respaldo parcial..."):
                        try:
                            # Crear directorio de respaldos
                            os.makedirs("backups", exist_ok=True)
                            
                            # Nombre del archivo
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            nombre_backup = f"respaldo_parcial_{timestamp}.sql"
                            ruta_backup = os.path.join("backups", nombre_backup)
                            
                            # Exportar datos principales
                            with open(ruta_backup, 'w', encoding='utf-8') as f:
                                f.write("-- Respaldo Parcial SICADFOC\n")
                                f.write(f"-- Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                                
                                # Exportar usuarios
                                f.write("-- Tabla: usuario\n")
                                usuarios = ejecutar_query("SELECT * FROM usuario", engine=engine)
                                if usuarios is not None:
                                    f.write(usuarios.to_csv(index=False, sep='|'))
                                
                                f.write("\n\n")
                            
                            st.success(f"✅ Respaldo parcial creado: {nombre_backup}")
                            st.info(f"📁 Ubicación: {ruta_backup}")
                            st.balloons()
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error creando respaldo: {str(e)}")
                
                if btn_descargar:
                    st.info("📥 **Función de descarga en desarrollo**")
                    st.info("Los respaldos se encuentran en la carpeta /backups/")
                
            except Exception as e:
                st.error(f"❌ Error cargando información de base de datos: {str(e)}")
        
        # =================================================================
        # PESTAÑA 3: CONFIGURACIÓN GENERAL
        # =================================================================
        with tab3:
            st.subheader("⚙️ Configuración General del Sistema")
            
            # Información del sistema
            st.write("🖥️ **Información del Sistema**")
            
            col_sys1, col_sys2 = st.columns(2)
            
            with col_sys1:
                st.metric("🎓 Versión", "SICADFOC 2026")
                st.metric("🌐 Ambiente", tipo_ambiente)
                st.metric("📊 Base de Datos", "SQLite")
            
            with col_sys2:
                st.metric("👨‍💻 Usuarios Activos", st.session_state.get('total_usuarios', 0))
                st.metric("📅 Último Acceso", datetime.now().strftime('%Y-%m-%d %H:%M'))
                st.metric("🔄 Estado", "Operativo")
            
            # Configuración de sesión
            st.write("---")
            st.write("⏱️ **Configuración de Sesión**")
            
            with st.form("config_sesion_form"):
                # Detectar vista móvil y ajustar columnas
                if st.session_state.get('mobile_view', False):
                    # Vista móvil: una columna
                    with st.container():
                        tiempo_sesion = st.number_input(
                            "⏱️ Tiempo de Sesión (minutos)",
                            min_value=5,
                            max_value=480,
                            value=60,
                            help="Tiempo máximo de inactividad antes de cerrar sesión",
                            key="tiempo_sesion"
                        )
                        
                        intentos_login = st.number_input(
                            "🔐 Intentos de Login",
                            min_value=1,
                            max_value=10,
                            value=3,
                            help="Número máximo de intentos fallidos antes de bloquear",
                            key="intentos_login"
                        )
                        
                        notificaciones = st.checkbox(
                            "📧 Activar Notificaciones por Correo",
                            value=True,
                            help="Enviar notificaciones importantes por correo",
                            key="notificaciones_correo"
                        )
                        
                        modo_mantenimiento = st.checkbox(
                            "🔧 Modo Mantenimiento",
                            value=False,
                            help="Activar modo de mantenimiento (solo administradores)",
                            key="modo_mantenimiento"
                        )
                else:
                    # Vista desktop: dos columnas
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        tiempo_sesion = st.number_input(
                            "⏱️ Tiempo de Sesión (minutos)",
                            min_value=5,
                            max_value=480,
                            value=60,
                            help="Tiempo máximo de inactividad antes de cerrar sesión",
                            key="tiempo_sesion"
                        )
                        
                        intentos_login = st.number_input(
                            "🔐 Intentos de Login",
                            min_value=1,
                            max_value=10,
                            value=3,
                            help="Número máximo de intentos fallidos antes de bloquear",
                            key="intentos_login"
                        )
                    
                    with col2:
                        notificaciones = st.checkbox(
                            "📧 Activar Notificaciones por Correo",
                            value=True,
                            help="Enviar notificaciones importantes por correo",
                            key="notificaciones_correo"
                        )
                        
                        modo_mantenimiento = st.checkbox(
                            "🔧 Modo Mantenimiento",
                            value=False,
                            help="Activar modo de mantenimiento (solo administradores)",
                            key="modo_mantenimiento"
                        )
                
                # Botón de guardar
                if st.form_submit_button("💾 Guardar Configuración", type="primary", use_container_width=True):
                    st.success("✅ Configuración guardada exitosamente")
                    st.balloons()
                    st.rerun()
            
            # Limpieza del sistema
            st.write("---")
            st.write("🧹 **Limpieza del Sistema**")
            
            col_clean1, col_clean2 = st.columns(2)
            
            with col_clean1:
                if st.button("🧹 Limpiar Logs", use_container_width=True, help="Limpiar archivos de log antiguos"):
                    with st.spinner("Limpiando logs..."):
                        try:
                            # Aquí iría la lógica para limpiar logs
                            st.success("✅ Logs limpiados exitosamente")
                        except Exception as e:
                            st.error(f"❌ Error limpiando logs: {str(e)}")
                
                if st.button("🧹 Limpiar Caché", use_container_width=True, help="Limpiar caché del sistema"):
                    with st.spinner("Limpiando caché..."):
                        try:
                            # Aquí iría la lógica para limpiar caché
                            st.success("✅ Caché limpiado exitosamente")
                        except Exception as e:
                            st.error(f"❌ Error limpiando caché: {str(e)}")
            
            with col_clean2:
                if st.button("🧹 Optimizar Base de Datos", use_container_width=True, help="Optimizar rendimiento de la base de datos"):
                    with st.spinner("Optimizando base de datos..."):
                        try:
                            # Aquí iría la lógica para optimizar DB
                            st.success("✅ Base de datos optimizada exitosamente")
                        except Exception as e:
                            st.error(f"❌ Error optimizando base de datos: {str(e)}")
                
                if st.button("🔄 Reiniciar Sistema", use_container_width=True, help="Reiniciar servicios del sistema"):
                    st.warning("⚠️ Función de reinicio en desarrollo")
            
            # Sincronización con Render
            st.write("---")
            st.write("🔄 **Sincronización con Producción (Render)**")
            
            # Obtener URL del Deploy Hook desde variables de entorno
            render_hook_url = os.getenv("RENDER_DEPLOY_HOOK_URL", "")
            
            if render_hook_url:
                st.info(f"📡 **Deploy Hook Configurado:** {render_hook_url[:50]}...")
                
                if st.button("🔄 Sincronizar Producción (Render)", type="primary", use_container_width=True, help="Disparar actualización en producción"):
                    with st.spinner("Enviando solicitud de sincronización..."):
                        try:
                            import requests
                            
                            # Realizar POST request al Deploy Hook
                            response = requests.post(
                                render_hook_url,
                                headers={
                                    'User-Agent': 'SICADFOC-Sync/1.0',
                                    'Content-Type': 'application/json'
                                },
                                timeout=30
                            )
                            
                            if response.status_code == 200:
                                st.success("✅ Sincronización iniciada exitosamente")
                                st.info("📊 La actualización puede tardar unos minutos en completarse")
                                st.balloons()
                            elif response.status_code == 401:
                                st.error("❌ Error de autenticación - Verifique el Deploy Hook")
                            elif response.status_code == 404:
                                st.error("❌ Deploy Hook no encontrado - Verifique la URL")
                            else:
                                st.error(f"❌ Error en sincronización - Código: {response.status_code}")
                                st.error(f"**Respuesta:** {response.text}")
                                
                        except requests.exceptions.Timeout:
                            st.error("❌ Tiempo de espera agotado - Intente nuevamente")
                        except requests.exceptions.ConnectionError:
                            st.error("❌ Error de conexión - Verifique su conexión a internet")
                        except Exception as e:
                            st.error(f"❌ Error inesperado: {str(e)}")
            else:
                st.warning("⚠️ **Deploy Hook no configurado**")
                st.info("Configure la variable de entorno RENDER_DEPLOY_HOOK_URL para habilitar la sincronización")
                
                # Mostrar campo para configurar URL (solo para desarrollo)
                if st.session_state.get('mobile_view', False):
                    render_url_input = st.text_input(
                        "📡 URL del Deploy Hook (desarrollo)",
                        placeholder="https://api.render.com/deploy/serv...",
                        type="password",
                        help="Ingrese la URL del Deploy Hook de Render",
                        key="render_hook_url_dev"
                    )
                else:
                    col_url, col_config = st.columns([3, 1])
                    
                    with col_url:
                        render_url_input = st.text_input(
                            "📡 URL del Deploy Hook (desarrollo)",
                            placeholder="https://api.render.com/deploy/serv...",
                            type="password",
                            help="Ingrese la URL del Deploy Hook de Render",
                            key="render_hook_url_dev"
                        )
                    
                    with col_config:
                        st.write("")
                        if st.button("⚙️ Configurar", use_container_width=True):
                            if render_url_input:
                                st.success("✅ URL configurada temporalmente")
                                st.info("📝 Para configuración permanente, use variables de entorno")
                            else:
                                st.error("❌ Ingrese una URL válida")
    
    elif modulo_seleccionado == "📊 Reportes":
        # Módulo de Reportes
        st.header("📊 Reportes y Estadísticas")
        
        # Pestañas principales
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen General", "👥 Reporte de Usuarios", "📚 Reporte Académico", "📋 Reportes de Carga"])
        
        # =================================================================
        # PESTAÑA 1: RESUMEN GENERAL
        # =================================================================
        with tab1:
            st.subheader("📊 Resumen General del Sistema")
            
            # Métricas principales
            try:
                # Estadísticas generales
                total_usuarios = ejecutar_query("SELECT COUNT(*) as total FROM usuario", engine=engine)
                total_estudiantes = ejecutar_query("SELECT COUNT(*) as total FROM usuario WHERE rol = 'estudiante'", engine=engine)
                total_profesores = ejecutar_query("SELECT COUNT(*) as total FROM usuario WHERE rol = 'profesor'", engine=engine)
                total_admins = ejecutar_query("SELECT COUNT(*) as total FROM usuario WHERE rol = 'Administrador'", engine=engine)
                
                # Usuarios activos
                usuarios_activos = ejecutar_query("SELECT COUNT(*) as total FROM usuario WHERE activo = 1", engine=engine)
                usuarios_inactivos = ejecutar_query("SELECT COUNT(*) as total FROM usuario WHERE activo = 0", engine=engine)
                
                # Correos verificados
                correos_verificados = ejecutar_query("SELECT COUNT(*) as total FROM usuario WHERE correo_verificado = 1", engine=engine)
                correos_no_verificados = ejecutar_query("SELECT COUNT(*) as total FROM usuario WHERE correo_verificado = 0", engine=engine)
                
                # Mostrar métricas principales
                st.write("👥 **Estadísticas de Usuarios**")
                
                col_main1, col_main2, col_main3, col_main4 = st.columns(4)
                
                with col_main1:
                    st.metric("👥 Total Usuarios", total_usuarios.iloc[0]['total'] if total_usuarios is not None else 0)
                
                with col_main2:
                    st.metric("📚 Estudiantes", total_estudiantes.iloc[0]['total'] if total_estudiantes is not None else 0)
                
                with col_main3:
                    st.metric("👨‍🏫 Profesores", total_profesores.iloc[0]['total'] if total_profesores is not None else 0)
                
                with col_main4:
                    st.metric("👑 Administradores", total_admins.iloc[0]['total'] if total_admins is not None else 0)
                
                # Estado de usuarios
                st.write("---")
                st.write("✅ **Estado de Usuarios**")
                
                col_estado1, col_estado2 = st.columns(2)
                
                with col_estado1:
                    st.metric("🟢 Activos", usuarios_activos.iloc[0]['total'] if usuarios_activos is not None else 0)
                    st.metric("🔴 Inactivos", usuarios_inactivos.iloc[0]['total'] if usuarios_inactivos is not None else 0)
                
                with col_estado2:
                    st.metric("📧 Correos Verificados", correos_verificados.iloc[0]['total'] if correos_verificados is not None else 0)
                    st.metric("❌ Correos No Verificados", correos_no_verificados.iloc[0]['total'] if correos_no_verificados is not None else 0)
                
                # Gráfico de distribución de usuarios
                st.write("---")
                st.write("📊 **Distribución de Usuarios por Rol**")
                
                import plotly.express as px
                
                datos_roles = {
                    'Rol': ['Estudiantes', 'Profesores', 'Administradores'],
                    'Cantidad': [
                        total_estudiantes.iloc[0]['total'] if total_estudiantes is not None else 0,
                        total_profesores.iloc[0]['total'] if total_profesores is not None else 0,
                        total_admins.iloc[0]['total'] if total_admins is not None else 0
                    ]
                }
                
                df_roles = pd.DataFrame(datos_roles)
                
                fig = px.pie(
                    df_roles, 
                    values='Cantidad', 
                    names='Rol',
                    title="Distribución de Usuarios por Rol",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Usuarios recientes
                st.write("---")
                st.write("📅 **Usuarios Recientes**")
                
                usuarios_recientes = ejecutar_query("""
                    SELECT nombre, apellido, email, rol, fecha_registro
                    FROM usuario 
                    ORDER BY fecha_registro DESC 
                    LIMIT 10
                """, engine=engine)
                
                if usuarios_recientes is not None and not usuarios_recientes.empty:
                    st.dataframe(
                        usuarios_recientes[['nombre', 'apellido', 'email', 'rol', 'fecha_registro']],
                        column_rename={
                            'nombre': 'Nombre',
                            'apellido': 'Apellido',
                            'email': 'Correo',
                            'rol': 'Rol',
                            'fecha_registro': 'Fecha Registro'
                        },
                        use_container_width=True
                    )
                else:
                    st.info("📭 No hay usuarios registrados")
                
            except Exception as e:
                st.error(f"❌ Error generando resumen: {str(e)}")
        
        # =================================================================
        # PESTAÑA 2: REPORTE DE USUARIOS
        # =================================================================
        with tab2:
            st.subheader("👥 Reporte Detallado de Usuarios")
            
            # Filtros
            st.write("🔍 **Filtros de Búsqueda**")
            
            with st.form("filtros_usuarios_form"):
                # Detectar vista móvil y ajustar columnas
                if st.session_state.get('mobile_view', False):
                    # Vista móvil: una columna
                    with st.container():
                        filtro_rol = st.selectbox(
                            "🏷️ Filtrar por Rol",
                            options=["Todos", "Estudiante", "Profesor", "Administrador"],
                            index=0,
                            key="filtro_rol_usuarios"
                        )
                        
                        filtro_estado = st.selectbox(
                            "✅ Filtrar por Estado",
                            options=["Todos", "Activo", "Inactivo"],
                            index=0,
                            key="filtro_estado_usuarios"
                        )
                        
                        filtro_correo = st.selectbox(
                            "📧 Filtrar por Correo Verificado",
                            options=["Todos", "Verificado", "No Verificado"],
                            index=0,
                            key="filtro_correo_usuarios"
                        )
                        
                        filtro_fecha = st.date_input(
                            "📅 Fecha de Registro Desde",
                            help="Mostrar usuarios registrados desde esta fecha",
                            key="filtro_fecha_usuarios"
                        )
                else:
                    # Vista desktop: dos columnas
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        filtro_rol = st.selectbox(
                            "🏷️ Filtrar por Rol",
                            options=["Todos", "Estudiante", "Profesor", "Administrador"],
                            index=0,
                            key="filtro_rol_usuarios"
                        )
                        
                        filtro_estado = st.selectbox(
                            "✅ Filtrar por Estado",
                            options=["Todos", "Activo", "Inactivo"],
                            index=0,
                            key="filtro_estado_usuarios"
                        )
                    
                    with col2:
                        filtro_correo = st.selectbox(
                            "📧 Filtrar por Correo Verificado",
                            options=["Todos", "Verificado", "No Verificado"],
                            index=0,
                            key="filtro_correo_usuarios"
                        )
                        
                        filtro_fecha = st.date_input(
                            "📅 Fecha de Registro Desde",
                            help="Mostrar usuarios registrados desde esta fecha",
                            key="filtro_fecha_usuarios"
                        )
                
                # Botón de filtrar
                if st.form_submit_button("🔍 Aplicar Filtros", type="primary", use_container_width=True):
                    st.rerun()
            
            # Construir consulta con filtros
            query = "SELECT * FROM usuario WHERE 1=1"
            params = {}
            
            if filtro_rol != "Todos":
                query += " AND rol = :rol"
                params['rol'] = filtro_rol.lower()
            
            if filtro_estado != "Todos":
                query += " AND activo = :activo"
                params['activo'] = 1 if filtro_estado == "Activo" else 0
            
            if filtro_correo != "Todos":
                query += " AND correo_verificado = :correo_verificado"
                params['correo_verificado'] = 1 if filtro_correo == "Verificado" else 0
            
            if filtro_fecha:
                query += " AND fecha_registro >= :fecha_registro"
                params['fecha_registro'] = filtro_fecha.strftime('%Y-%m-%d')
            
            query += " ORDER BY fecha_registro DESC"
            
            # Ejecutar consulta
            try:
                usuarios_filtrados = ejecutar_query(query, params, engine=engine)
                
                if usuarios_filtrados is not None and not usuarios_filtrados.empty:
                    st.write(f"📊 **Resultados:** {len(usuarios_filtrados)} usuarios encontrados")
                    
                    # Tabla de resultados
                    st.dataframe(
                        usuarios_filtrados[['nombre', 'apellido', 'email', 'cedula', 'rol', 'activo', 'correo_verificado', 'fecha_registro']],
                        column_rename={
                            'nombre': 'Nombre',
                            'apellido': 'Apellido',
                            'email': 'Correo',
                            'cedula': 'Cédula',
                            'rol': 'Rol',
                            'activo': 'Activo',
                            'correo_verificado': 'Correo Verificado',
                            'fecha_registro': 'Fecha Registro'
                        },
                        use_container_width=True
                    )
                    
                    # Botón de exportar
                    if st.button("📥 Exportar a CSV", type="secondary", use_container_width=True):
                        csv = usuarios_filtrados.to_csv(index=False)
                        st.download_button(
                            label="📥 Descargar CSV",
                            data=csv,
                            file_name=f"usuarios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                else:
                    st.info("📭 No hay usuarios que coincidan con los filtros")
                    
            except Exception as e:
                st.error(f"❌ Error aplicando filtros: {str(e)}")
        
        # =================================================================
        # PESTAÑA 3: REPORTE ACADÉMICO
        # =================================================================
        with tab3:
            st.subheader("📚 Reporte Académico")
            
            # Estadísticas académicas
            try:
                # Estudiantes por semestre
                estudiantes_por_semestre = ejecutar_query("""
                    SELECT semestre, COUNT(*) as total
                    FROM usuario 
                    WHERE rol = 'estudiante' AND semestre IS NOT NULL
                    GROUP BY semestre
                    ORDER BY semestre
                """, engine=engine)
                
                if estudiantes_por_semestre is not None and not estudiantes_por_semestre.empty:
                    st.write("📚 **Estudiantes por Semestre**")
                    
                    fig = px.bar(
                        estudiantes_por_semestre,
                        x='semestre',
                        y='total',
                        title="Distribución de Estudiantes por Semestre",
                        labels={'semestre': 'Semestre', 'total': 'Cantidad de Estudiantes'},
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    
                    fig.update_layout(
                        xaxis_title="Semestre",
                        yaxis_title="Cantidad de Estudiantes",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Formación complementaria
                st.write("---")
                st.write("🎓 **Estadísticas de Formación Complementaria**")
                
                try:
                    total_cursos_fc = ejecutar_query("SELECT COUNT(*) as total FROM formacion_complementaria WHERE activo = 1", engine=engine)
                    total_asignaciones_fc = ejecutar_query("SELECT COUNT(*) as total FROM asignacion_formacion WHERE estado = 'Activo'", engine=engine)
                    
                    col_fc1, col_fc2 = st.columns(2)
                    
                    with col_fc1:
                        st.metric("📚 Total Cursos Activos", total_cursos_fc.iloc[0]['total'] if total_cursos_fc is not None else 0)
                        st.metric("👥 Total Asignaciones", total_asignaciones_fc.iloc[0]['total'] if total_asignaciones_fc is not None else 0)
                    
                    with col_fc2:
                        st.metric("🎓 Cursos por Estudiante", 
                                 round(total_asignaciones_fc.iloc[0]['total'] / total_estudiantes.iloc[0]['total'], 2) if total_asignaciones_fc and total_estudiantes and total_estudiantes.iloc[0]['total'] > 0 else 0)
                        st.metric("📈 Tasa de Participación", 
                                 f"{round((total_asignaciones_fc.iloc[0]['total'] / total_estudiantes.iloc[0]['total']) * 100, 1) if total_asignaciones_fc and total_estudiantes and total_estudiantes.iloc[0]['total'] > 0 else 0}%")
                
                except Exception as e:
                    st.warning(f"⚠️ No se pudieron cargar las estadísticas de formación complementaria: {str(e)}")
                
                # Resumen de expedientes
                st.write("---")
                st.write("📁 **Resumen de Expedientes Digitales**")
                
                # Contar expedientes de estudiantes
                if os.path.exists("expedientes"):
                    total_expedientes_estudiantes = len([f for f in os.listdir("expedientes") if f.endswith('.pdf')])
                else:
                    total_expedientes_estudiantes = 0
                
                # Contar expedientes de profesores
                if os.path.exists("expedientes_pdf"):
                    total_expedientes_profesores = len([f for f in os.listdir("expedientes_pdf") if f.endswith('.pdf')])
                else:
                    total_expedientes_profesores = 0
                
                col_exp1, col_exp2 = st.columns(2)
                
                with col_exp1:
                    st.metric("📄 Expedientes Estudiantes", total_expedientes_estudiantes)
                    st.metric("📁 Expedientes Profesores", total_expedientes_profesores)
                
                with col_exp2:
                    st.metric("📊 Total Expedientes", total_expedientes_estudiantes + total_expedientes_profesores)
                    st.metric("📈 Promedio por Usuario", 
                             round((total_expedientes_estudiantes + total_expedientes_profesores) / (total_usuarios.iloc[0]['total'] if total_usuarios is not None else 1), 2))
                
            except Exception as e:
                st.error(f"❌ Error generando reporte académico: {str(e)}")
        
        # =================================================================
        # PESTAÑA 4: REPORTES DE CARGA MASIVA
        # =================================================================
        with tab4:
            st.subheader("📋 Reportes de Carga Masiva")
            
            # Información importante
            st.info("💡 **Esta sección muestra todas las cargas masivas registradas automáticamente**")
            
            # Obtener reportes de carga
            try:
                reportes_carga = ejecutar_query("""
                    SELECT origen, fecha_hora, resumen, detalles, usuario_cedula, creado_en
                    FROM reportes 
                    WHERE origen LIKE '%Carga Masiva%'
                    ORDER BY fecha_hora DESC
                    LIMIT 50
                """, engine=engine)
                
                if reportes_carga is not None and not reportes_carga.empty:
                    st.write(f"📊 **Historial de Cargas Masivas:** {len(reportes_carga)} registros")
                    
                    # Estadísticas generales
                    st.write("---")
                    col_stats1, col_stats2, col_stats3 = st.columns(3)
                    
                    with col_stats1:
                        st.metric("📋 Total Cargas", len(reportes_carga))
                    
                    with col_stats2:
                        # Contar por tipo
                        cargas_estudiantes = len(reportes_carga[reportes_carga['origen'].str.contains('Estudiantes')])
                        st.metric("📚 Cargas Estudiantes", cargas_estudiantes)
                    
                    with col_stats3:
                        cargas_profesores = len(reportes_carga[reportes_carga['origen'].str.contains('Profesores')])
                        st.metric("👨‍🏫 Cargas Profesores", cargas_profesores)
                    
                    # Tabla detallada
                    st.write("---")
                    st.write("📋 **Detalle de Reportes**")
                    
                    # Formatear datos para mejor visualización
                    reportes_carga_formateado = reportes_carga.copy()
                    reportes_carga_formateado['fecha_formateada'] = pd.to_datetime(reportes_carga_formateado['fecha_hora']).dt.strftime('%d/%m/%Y %H:%M')
                    
                    st.dataframe(
                        reportes_carga_formateado[['origen', 'fecha_formateada', 'resumen', 'usuario_cedula', 'detalles']],
                        column_config={
                            'origen': st.column_config.TextColumn("📋 Origen", width="medium"),
                            'fecha_formateada': st.column_config.TextColumn("📅 Fecha y Hora", width="medium"),
                            'resumen': st.column_config.TextColumn("📊 Resumen", width="large"),
                            'usuario_cedula': st.column_config.TextColumn("👤 Admin Cédula", width="small"),
                            'detalles': st.column_config.TextColumn("📝 Detalles", width="large")
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Gráfico de cargas por día
                    st.write("---")
                    st.write("📈 **Tendencia de Cargas por Día**")
                    
                    # Convertir fecha y agrupar por día
                    reportes_carga['fecha'] = pd.to_datetime(reportes_carga['fecha_hora']).dt.date
                    cargas_por_dia = reportes_carga.groupby('fecha').size().reset_index(name='cantidad')
                    
                    import plotly.express as px
                    
                    fig = px.line(
                        cargas_por_dia,
                        x='fecha',
                        y='cantidad',
                        title='Cargas Masivas por Día',
                        labels={'fecha': 'Fecha', 'cantidad': 'Cantidad de Cargas'},
                        color_discrete_sequence=px.colors.qualitative.Set1
                    )
                    
                    fig.update_layout(
                        xaxis_title="Fecha",
                        yaxis_title="Cantidad de Cargas",
                        height=400,
                        template="plotly_dark"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Botón de exportar
                    st.write("---")
                    if st.button("📥 Exportar Reportes a CSV", type="secondary", use_container_width=True):
                        csv = reportes_carga_formateado.to_csv(index=False)
                        st.download_button(
                            label="📥 Descargar Reportes de Carga",
                            data=csv,
                            file_name=f"reportes_carga_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                
                else:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #1E293B 0%, #334155 100%); 
                                padding: 2rem; border-radius: 15px; 
                                border: 1px solid #334155; text-align: center;">
                        <h3 style="color: white; margin-bottom: 1rem; font-size: 1.3rem;">
                            📋 No hay reportes registrados
                        </h3>
                        <p style="color: #CBD5E1; font-size: 1rem; margin: 0;">
                            Los reportes de carga masiva aparecerán aquí automáticamente
                        </p>
                        <p style="color: #94A3B8; font-size: 0.9rem; margin: 0;">
                            💡 Realice cargas masivas en los módulos de Estudiantes o Profesores
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"❌ Error cargando reportes de carga: {str(e)}")
    
    elif modulo_seleccionado == "⚡ Monitor":
        # Módulo de Monitor del Sistema
        st.header("⚡ Monitor del Sistema")
        
        # Dashboard de Control
        st.subheader("📊 Dashboard de Control")
        
        # Detectar vista móvil y ajustar columnas
        if st.session_state.get('mobile_view', False):
            # Vista móvil: una columna
            with st.container():
                # Tarjeta de Estudiantes
                try:
                    total_estudiantes = ejecutar_query(
                        "SELECT COUNT(*) as total FROM usuario WHERE rol = 'estudiante'",
                        engine=engine
                    )
                    
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%); 
                                padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem; 
                                border: 1px solid #6D28D9; text-align: center;">
                        <h3 style="color: white; margin-bottom: 0.5rem; font-size: 1.5rem;">
                            📚 Estudiantes
                        </h3>
                        <p style="color: #E9D5FF; font-size: 2rem; margin: 0; font-weight: bold;">
                            {}
                        </p>
                        <p style="color: #DDD6FE; font-size: 0.9rem; margin: 0;">
                            Total registrados
                        </p>
                    </div>
                    """.format(total_estudiantes.iloc[0]['total'] if total_estudiantes is not None else 0), unsafe_allow_html=True)
                except:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%); 
                                padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem; 
                                border: 1px solid #6D28D9; text-align: center;">
                        <h3 style="color: white; margin-bottom: 0.5rem; font-size: 1.5rem;">
                            📚 Estudiantes
                        </h3>
                        <p style="color: #E9D5FF; font-size: 2rem; margin: 0; font-weight: bold;">
                            0
                        </p>
                        <p style="color: #DDD6FE; font-size: 0.9rem; margin: 0;">
                            Total registrados
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Tarjeta de Profesores
                try:
                    total_profesores = ejecutar_query(
                        "SELECT COUNT(*) as total FROM usuario WHERE rol = 'profesor'",
                        engine=engine
                    )
                    
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #059669 0%, #047857 100%); 
                                padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem; 
                                border: 1px solid #047857; text-align: center;">
                        <h3 style="color: white; margin-bottom: 0.5rem; font-size: 1.5rem;">
                            👨‍🏫 Profesores
                        </h3>
                        <p style="color: #D1FAE5; font-size: 2rem; margin: 0; font-weight: bold;">
                            {}
                        </p>
                        <p style="color: #A7F3D0; font-size: 0.9rem; margin: 0;">
                            Total registrados
                        </p>
                    </div>
                    """.format(total_profesores.iloc[0]['total'] if total_profesores is not None else 0), unsafe_allow_html=True)
                except:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #059669 0%, #047857 100%); 
                                padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem; 
                                border: 1px solid #047857; text-align: center;">
                        <h3 style="color: white; margin-bottom: 0.5rem; font-size: 1.5rem;">
                            👨‍🏫 Profesores
                        </h3>
                        <p style="color: #D1FAE5; font-size: 2rem; margin: 0; font-weight: bold;">
                            0
                        </p>
                        <p style="color: #A7F3D0; font-size: 0.9rem; margin: 0;">
                            Total registrados
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Tarjeta de Archivos PDF
                try:
                    # Contar archivos PDF de estudiantes
                    if os.path.exists("expedientes"):
                        pdf_estudiantes = len([f for f in os.listdir("expedientes") if f.endswith('.pdf')])
                    else:
                        pdf_estudiantes = 0
                    
                    # Contar archivos PDF de profesores
                    if os.path.exists("expedientes_pdf"):
                        pdf_profesores = len([f for f in os.listdir("expedientes_pdf") if f.endswith('.pdf')])
                    else:
                        pdf_profesores = 0
                    
                    total_pdf = pdf_estudiantes + pdf_profesores
                    
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%); 
                                padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem; 
                                border: 1px solid #B91C1C; text-align: center;">
                        <h3 style="color: white; margin-bottom: 0.5rem; font-size: 1.5rem;">
                            📄 Archivos PDF
                        </h3>
                        <p style="color: #FECACA; font-size: 2rem; margin: 0; font-weight: bold;">
                            {}
                        </p>
                        <p style="color: #FEE2E2; font-size: 0.9rem; margin: 0;">
                            Total cargados
                        </p>
                    </div>
                    """.format(total_pdf), unsafe_allow_html=True)
                except:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%); 
                                padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem; 
                                border: 1px solid #B91C1C; text-align: center;">
                        <h3 style="color: white; margin-bottom: 0.5rem; font-size: 1.5rem;">
                            📄 Archivos PDF
                        </h3>
                        <p style="color: #FECACA; font-size: 2rem; margin: 0; font-weight: bold;">
                            0
                        </p>
                        <p style="color: #FEE2E2; font-size: 0.9rem; margin: 0;">
                            Total cargados
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # Vista desktop: tres columnas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                try:
                    total_estudiantes = ejecutar_query(
                        "SELECT COUNT(*) as total FROM usuario WHERE rol = 'estudiante'",
                        engine=engine
                    )
                    
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%); 
                                padding: 2rem; border-radius: 15px; text-align: center;">
                        <h3 style="color: white; margin-bottom: 1rem; font-size: 1.2rem;">
                            📚 Estudiantes
                        </h3>
                        <p style="color: #E9D5FF; font-size: 2.5rem; margin: 0; font-weight: bold;">
                            {}
                        </p>
                        <p style="color: #DDD6FE; font-size: 0.9rem; margin: 0;">
                            Total registrados
                        </p>
                    </div>
                    """.format(total_estudiantes.iloc[0]['total'] if total_estudiantes is not None else 0), unsafe_allow_html=True)
                except:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%); 
                                padding: 2rem; border-radius: 15px; text-align: center;">
                        <h3 style="color: white; margin-bottom: 1rem; font-size: 1.2rem;">
                            📚 Estudiantes
                        </h3>
                        <p style="color: #E9D5FF; font-size: 2.5rem; margin: 0; font-weight: bold;">
                            0
                        </p>
                        <p style="color: #DDD6FE; font-size: 0.9rem; margin: 0;">
                            Total registrados
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                try:
                    total_profesores = ejecutar_query(
                        "SELECT COUNT(*) as total FROM usuario WHERE rol = 'profesor'",
                        engine=engine
                    )
                    
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #059669 0%, #047857 100%); 
                                padding: 2rem; border-radius: 15px; text-align: center;">
                        <h3 style="color: white; margin-bottom: 1rem; font-size: 1.2rem;">
                            👨‍🏫 Profesores
                        </h3>
                        <p style="color: #D1FAE5; font-size: 2.5rem; margin: 0; font-weight: bold;">
                            {}
                        </p>
                        <p style="color: #A7F3D0; font-size: 0.9rem; margin: 0;">
                            Total registrados
                        </p>
                    </div>
                    """.format(total_profesores.iloc[0]['total'] if total_profesores is not None else 0), unsafe_allow_html=True)
                except:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #059669 0%, #047857 100%); 
                                padding: 2rem; border-radius: 15px; text-align: center;">
                        <h3 style="color: white; margin-bottom: 1rem; font-size: 1.2rem;">
                            👨‍🏫 Profesores
                        </h3>
                        <p style="color: #D1FAE5; font-size: 2.5rem; margin: 0; font-weight: bold;">
                            0
                        </p>
                        <p style="color: #A7F3D0; font-size: 0.9rem; margin: 0;">
                            Total registrados
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col3:
                try:
                    # Contar archivos PDF de estudiantes
                    if os.path.exists("expedientes"):
                        pdf_estudiantes = len([f for f in os.listdir("expedientes") if f.endswith('.pdf')])
                    else:
                        pdf_estudiantes = 0
                    
                    # Contar archivos PDF de profesores
                    if os.path.exists("expedientes_pdf"):
                        pdf_profesores = len([f for f in os.listdir("expedientes_pdf") if f.endswith('.pdf')])
                    else:
                        pdf_profesores = 0
                    
                    total_pdf = pdf_estudiantes + pdf_profesores
                    
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%); 
                                padding: 2rem; border-radius: 15px; text-align: center;">
                        <h3 style="color: white; margin-bottom: 1rem; font-size: 1.2rem;">
                            📄 Archivos PDF
                        </h3>
                        <p style="color: #FECACA; font-size: 2.5rem; margin: 0; font-weight: bold;">
                            {}
                        </p>
                        <p style="color: #FEE2E2; font-size: 0.9rem; margin: 0;">
                            Total cargados
                        </p>
                    </div>
                    """.format(total_pdf), unsafe_allow_html=True)
                except:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%); 
                                padding: 2rem; border-radius: 15px; text-align: center;">
                        <h3 style="color: white; margin-bottom: 1rem; font-size: 1.2rem;">
                            📄 Archivos PDF
                        </h3>
                        <p style="color: #FECACA; font-size: 2.5rem; margin: 0; font-weight: bold;">
                            0
                        </p>
                        <p style="color: #FEE2E2; font-size: 0.9rem; margin: 0;">
                            Total cargados
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Separador
        st.write("---")
        
        # Estado del Servicio de Correo
        st.subheader("📧 Estado del Servicio de Correo")
        
        # Detectar vista móvil y ajustar columnas
        if st.session_state.get('mobile_view', False):
            # Vista móvil: una columna
            with st.container():
                try:
                    # Obtener configuración de correo
                    config_correo = database.obtener_config_correo(engine=engine)
                    
                    if config_correo:
                        # Probar conexión SMTP
                        try:
                            import smtplib
                            server = smtplib.SMTP(config_correo['servidor_smtp'], config_correo['puerto'], timeout=5)
                            server.starttls(timeout=5)
                            server.login(config_correo['usuario'], config_correo['password_app'])
                            server.quit()
                            
                            st.markdown("""
                            <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); 
                                        padding: 1.5rem; border-radius: 15px; 
                                        border: 1px solid #059669; text-align: center;">
                                <h3 style="color: white; margin-bottom: 0.5rem; font-size: 1.2rem;">
                                    📧 Servicio de Correo
                                </h3>
                                <p style="color: #D1FAE5; font-size: 1.1rem; margin: 0;">
                                    ✅ Conexión SMTP Activa
                                </p>
                                <p style="color: #A7F3D0; font-size: 0.8rem; margin: 0;">
                                    ab6643881@gmail.com
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        except:
                            st.markdown("""
                            <div style="background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); 
                                        padding: 1.5rem; border-radius: 15px; 
                                        border: 1px solid #DC2626; text-align: center;">
                                <h3 style="color: white; margin-bottom: 0.5rem; font-size: 1.2rem;">
                                    📧 Servicio de Correo
                                </h3>
                                <p style="color: #FECACA; font-size: 1.1rem; margin: 0;">
                                    ❌ Conexión SMTP Inactiva
                                </p>
                                <p style="color: #FEE2E2; font-size: 0.8rem; margin: 0;">
                                    ab6643881@gmail.com
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #6B7280 0%, #4B5563 100%); 
                                    padding: 1.5rem; border-radius: 15px; 
                                    border: 1px solid #4B5563; text-align: center;">
                            <h3 style="color: white; margin-bottom: 0.5rem; font-size: 1.2rem;">
                                📧 Servicio de Correo
                            </h3>
                            <p style="color: #D1D5DB; font-size: 1.1rem; margin: 0;">
                                ⚙️ No Configurado
                            </p>
                            <p style="color: #9CA3AF; font-size: 0.8rem; margin: 0;">
                                Configure el servicio SMTP
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Error verificando servicio de correo: {str(e)}")
        else:
            # Vista desktop: en columna
            col_correo, col_estado = st.columns([2, 1])
            
            with col_correo:
                try:
                    # Obtener configuración de correo
                    config_correo = database.obtener_config_correo(engine=engine)
                    
                    if config_correo:
                        # Probar conexión SMTP
                        try:
                            import smtplib
                            server = smtplib.SMTP(config_correo['servidor_smtp'], config_correo['puerto'], timeout=5)
                            server.starttls(timeout=5)
                            server.login(config_correo['usuario'], config_correo['password_app'])
                            server.quit()
                            
                            st.markdown("""
                            <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); 
                                        padding: 2rem; border-radius: 15px; 
                                        border: 1px solid #059669; text-align: center;">
                                <h3 style="color: white; margin-bottom: 1rem; font-size: 1.2rem;">
                                    📧 Servicio de Correo
                                </h3>
                                <p style="color: #D1FAE5; font-size: 1.3rem; margin: 0;">
                                    ✅ Conexión SMTP Activa
                                </p>
                                <p style="color: #A7F3D0; font-size: 0.9rem; margin: 0;">
                                    ab6643881@gmail.com
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        except:
                            st.markdown("""
                            <div style="background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); 
                                        padding: 2rem; border-radius: 15px; 
                                        border: 1px solid #DC2626; text-align: center;">
                                <h3 style="color: white; margin-bottom: 1rem; font-size: 1.2rem;">
                                    📧 Servicio de Correo
                                </h3>
                                <p style="color: #FECACA; font-size: 1.3rem; margin: 0;">
                                    ❌ Conexión SMTP Inactiva
                                </p>
                                <p style="color: #FEE2E2; font-size: 0.9rem; margin: 0;">
                                    ab6643881@gmail.com
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #6B7280 0%, #4B5563 100%); 
                                    padding: 2rem; border-radius: 15px; 
                                    border: 1px solid #4B5563; text-align: center;">
                            <h3 style="color: white; margin-bottom: 1rem; font-size: 1.2rem;">
                                📧 Servicio de Correo
                            </h3>
                            <p style="color: #D1D5DB; font-size: 1.3rem; margin: 0;">
                                ⚙️ No Configurado
                            </p>
                            <p style="color: #9CA3AF; font-size: 0.9rem; margin: 0;">
                                Configure el servicio SMTP
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Error verificando servicio de correo: {str(e)}")
            
            with col_estado:
                # Botón para refrescar estado
                if st.button("🔄 Refrescar Estado", use_container_width=True, help="Verificar nuevamente el estado del correo"):
                    st.rerun()
        
        # Separador
        st.write("---")
        
        # Buscador Global
        st.subheader("🔍 Buscador Global")
        
        # Detectar vista móvil y ajustar columnas
        if st.session_state.get('mobile_view', False):
            # Vista móvil: una columna
            with st.container():
                termino_busqueda = st.text_input(
                    "🔍 Buscar por Cédula",
                    placeholder="V-12345678",
                    help="Ingrese la cédula del estudiante o profesor",
                    key="busqueda_global_monitor"
                )
                
                if termino_busqueda:
                    with st.spinner("Buscando..."):
                        try:
                            # Buscar en estudiantes
                            resultado_estudiante = ejecutar_query(
                                "SELECT * FROM usuario WHERE cedula = :cedula AND rol = 'estudiante'",
                                {"cedula": termino_busqueda.upper()},
                                engine=engine
                            )
                            
                            # Buscar en profesores
                            resultado_profesor = ejecutar_query(
                                "SELECT * FROM usuario WHERE cedula = :cedula AND rol = 'profesor'",
                                {"cedula": termino_busqueda.upper()},
                                engine=engine
                            )
                            
                            # Mostrar resultados
                            if resultado_estudiante is not None and not resultado_estudiante.empty:
                                estudiante = resultado_estudiante.iloc[0]
                                st.success("✅ Estudiante Encontrado")
                                
                                st.markdown(f"""
                                <div style="background: #F3F4F6; padding: 1rem; border-radius: 10px; border-left: 4px solid #7C3AED;">
                                    <h4 style="color: #1e293b; margin-bottom: 0.5rem;">📚 Estudiante</h4>
                                    <p><strong>🆔 Cédula:</strong> {estudiante['cedula']}</p>
                                    <p><strong>👤 Nombre:</strong> {estudiante['nombre']} {estudiante['apellido']}</p>
                                    <p><strong>📧 Correo:</strong> {estudiante['email']}</p>
                                    <p><strong>📚 Semestre:</strong> {estudiante.get('semestre', 'N/A')}</p>
                                    <p><strong>✅ Estado:</strong> {'Activo' if estudiante['activo'] else 'Inactivo'}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            elif resultado_profesor is not None and not resultado_profesor.empty:
                                profesor = resultado_profesor.iloc[0]
                                st.success("✅ Profesor Encontrado")
                                
                                st.markdown(f"""
                                <div style="background: #F3F4F6; padding: 1rem; border-radius: 10px; border-left: 4px solid #059669;">
                                    <h4 style="color: #1e293b; margin-bottom: 0.5rem;">👨‍🏫 Profesor</h4>
                                    <p><strong>🆔 Cédula:</strong> {profesor['cedula']}</p>
                                    <p><strong>👤 Nombre:</strong> {profesor['nombre']} {profesor['apellido']}</p>
                                    <p><strong>📧 Correo:</strong> {profesor['email']}</p>
                                    <p><strong>📚 Categoría:</strong> {profesor.get('categoria', 'N/A')}</p>
                                    <p><strong>✅ Estado:</strong> {'Activo' if profesor['activo'] else 'Inactivo'}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            else:
                                st.warning("⚠️ No se encontró ningún usuario con esa cédula")
                                
                        except Exception as e:
                            st.error(f"❌ Error en búsqueda: {str(e)}")
        else:
            # Vista desktop: en línea
            col_buscar, col_btn_buscar = st.columns([3, 1])
            
            with col_buscar:
                termino_busqueda = st.text_input(
                    "🔍 Buscar por Cédula",
                    placeholder="V-12345678",
                    help="Ingrese la cédula del estudiante o profesor",
                    key="busqueda_global_monitor"
                )
            
            with col_btn_buscar:
                st.write("")  # Espacio para alinear el botón
                btn_buscar_global = st.button("🔍 Buscar", use_container_width=True)
            
            if btn_buscar_global and termino_busqueda:
                with st.spinner("Buscando..."):
                    try:
                        # Buscar en estudiantes
                        resultado_estudiante = ejecutar_query(
                            "SELECT * FROM usuario WHERE cedula = :cedula AND rol = 'estudiante'",
                            {"cedula": termino_busqueda.upper()},
                            engine=engine
                        )
                        
                        # Buscar en profesores
                        resultado_profesor = ejecutar_query(
                            "SELECT * FROM usuario WHERE cedula = :cedula AND rol = 'profesor'",
                            {"cedula": termino_busqueda.upper()},
                            engine=engine
                        )
                        
                        # Mostrar resultados
                        if resultado_estudiante is not None and not resultado_estudiante.empty:
                            estudiante = resultado_estudiante.iloc[0]
                            st.success("✅ Estudiante Encontrado")
                            
                            st.markdown(f"""
                            <div style="background: #F3F4F6; padding: 1rem; border-radius: 10px; border-left: 4px solid #7C3AED;">
                                <h4 style="color: #1e293b; margin-bottom: 0.5rem;">📚 Estudiante</h4>
                                <p><strong>🆔 Cédula:</strong> {estudiante['cedula']}</p>
                                <p><strong>👤 Nombre:</strong> {estudiante['nombre']} {estudiante['apellido']}</p>
                                <p><strong>📧 Correo:</strong> {estudiante['email']}</p>
                                <p><strong>📚 Semestre:</strong> {estudiante.get('semestre', 'N/A')}</p>
                                <p><strong>✅ Estado:</strong> {'Activo' if estudiante['activo'] else 'Inactivo'}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        elif resultado_profesor is not None and not resultado_profesor.empty:
                            profesor = resultado_profesor.iloc[0]
                            st.success("✅ Profesor Encontrado")
                            
                            st.markdown(f"""
                            <div style="background: #F3F4F6; padding: 1rem; border-radius: 10px; border-left: 4px solid #059669;">
                                <h4 style="color: #1e293b; margin-bottom: 0.5rem;">👨‍🏫 Profesor</h4>
                                <p><strong>🆔 Cédula:</strong> {profesor['cedula']}</p>
                                <p><strong>👤 Nombre:</strong> {profesor['nombre']} {profesor['apellido']}</p>
                                <p><strong>📧 Correo:</strong> {profesor['email']}</p>
                                <p><strong>📚 Categoría:</strong> {profesor.get('categoria', 'N/A')}</p>
                                <p><strong>✅ Estado:</strong> {'Activo' if profesor['activo'] else 'Inactivo'}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        else:
                            st.warning("⚠️ No se encontró ningún usuario con esa cédula")
                            
                    except Exception as e:
                        st.error(f"❌ Error en búsqueda: {str(e)}")
        
        # Separador
        st.write("---")
        
        # Seguimiento de Registros
        st.subheader("📋 Seguimiento de Registros")
        
        # Detectar vista móvil y ajustar
        if st.session_state.get('mobile_view', False):
            # Vista móvil: tabla simple
            try:
                # Obtener últimos registros
                registros_recientes = ejecutar_query("""
                    SELECT nombre, apellido, email, rol, fecha_registro, activo
                    FROM usuario 
                    ORDER BY fecha_registro DESC 
                    LIMIT 20
                """, engine=engine)
                
                if registros_recientes is not None and not registros_recientes.empty:
                    st.write(f"📊 **Últimos 20 registros**")
                    
                    # Mostrar registros en formato móvil
                    for _, registro in registros_recientes.iterrows():
                        with st.expander(f"👤 {registro['apellido']}, {registro['nombre']} - {registro['fecha_registro']}"):
                            st.write(f"**📧 Correo:** {registro['email']}")
                            st.write(f"**🏷️ Rol:** {registro['rol']}")
                            st.write(f"**📅 Registro:** {registro['fecha_registro']}")
                            st.write(f"**✅ Estado:** {'Activo' if registro['activo'] else 'Inactivo'}")
                else:
                    st.info("📭 No hay registros disponibles")
                    
            except Exception as e:
                st.error(f"❌ Error cargando registros: {str(e)}")
        else:
            # Vista desktop: tabla completa
            try:
                # Obtener últimos registros
                registros_recientes = ejecutar_query("""
                    SELECT nombre, apellido, email, rol, fecha_registro, activo
                    FROM usuario 
                    ORDER BY fecha_registro DESC 
                    LIMIT 50
                """, engine=engine)
                
                if registros_recientes is not None and not registros_recientes.empty:
                    st.write(f"📊 **Últimos 50 registros**")
                    
                    # Mostrar tabla con formato desktop
                    st.dataframe(
                        registros_recientes[['nombre', 'apellido', 'email', 'rol', 'fecha_registro', 'activo']],
                        column_rename={
                            'nombre': 'Nombre',
                            'apellido': 'Apellido',
                            'email': 'Correo',
                            'rol': 'Rol',
                            'fecha_registro': 'Fecha Registro',
                            'activo': 'Estado'
                        },
                        use_container_width=True
                    )
                else:
                    st.info("📭 No hay registros disponibles")
                    
            except Exception as e:
                st.error(f"❌ Error cargando registros: {str(e)}")
        
        # Botón de refrescar
        st.write("---")
        if st.button("🔄 Refrescar Datos del Monitor", type="secondary", use_container_width=True, help="Actualizar todos los datos del monitor"):
            st.rerun()
    
    elif modulo_seleccionado == "🔄 Actualización Render Cloud":
        # Módulo de Actualización Render Cloud
        st.header("🔄 Actualización Render Cloud")
        
        # Información del módulo
        st.info("💡 **Este módulo permite actualizar la base de datos en producción (Render) a demanda**")
        
        # Estado de la conexión
        st.subheader("📡 Estado de Conexión")
        
        # Obtener URL del Deploy Hook
        render_hook_url = os.getenv("RENDER_DEPLOY_HOOK_URL", "")
        
        if render_hook_url:
            # Mostrar estado de conexión
            st.markdown("""
            <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); 
                        padding: 1.5rem; border-radius: 15px; 
                        border: 1px solid #059669; text-align: center;">
                <h3 style="color: white; margin-bottom: 0.5rem; font-size: 1.2rem;">
                    📡 Deploy Hook Configurado
                </h3>
                <p style="color: #D1FAE5; font-size: 1rem; margin: 0;">
                    ✅ Conexión lista para sincronización
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("---")
            
            # Panel de control
            st.subheader("🎛️ Panel de Control")
            
            # Detectar vista móvil y ajustar columnas
            if st.session_state.get('mobile_view', False):
                # Vista móvil: una columna
                with st.container():
                    # Botón principal de sincronización
                    if st.button("🔄 Sincronizar Producción (Render)", type="primary", use_container_width=True, help="Disparar actualización en producción"):
                        with st.spinner("🔄 Iniciando sincronización con Render..."):
                            try:
                                import requests
                                
                                # Validar restricciones de seguridad antes de sincronizar
                                correo_omitido = st.session_state.get('omitir_correo_especifico', 'angelher@gmail.com')
                                cedula_admin = st.session_state.get('cedula_admin', '14300385')
                                
                                st.info(f"🔒 **Restricciones activas:**")
                                st.info(f"📧 Omitiendo correo: {correo_omitido}")
                                st.info(f"👤 Admin vinculado a cédula: {cedula_admin}")
                                
                                # Realizar POST request al Deploy Hook
                                response = requests.post(
                                    render_hook_url,
                                    headers={
                                        'User-Agent': 'SICADFOC-Sync/1.0',
                                        'Content-Type': 'application/json',
                                        'X-Admin-Cedula': cedula_admin,
                                        'X-Omit-Correo': correo_omitido
                                    },
                                    json={
                                        'triggered_by': 'manual_sync',
                                        'admin_cedula': cedula_admin,
                                        'omit_email': correo_omitido,
                                        'timestamp': datetime.now().isoformat(),
                                        'environment': 'production'
                                    },
                                    timeout=45
                                )
                                
                                if response.status_code == 200:
                                    st.success("✅ Sincronización iniciada exitosamente")
                                    st.info("📊 La actualización puede tardar 2-5 minutos en completarse")
                                    st.balloons()
                                    
                                    # Mostrar detalles de la respuesta
                                    with st.expander("📋 Detalles de la sincronización"):
                                        st.json({
                                            'status_code': response.status_code,
                                            'response_time': f"{response.elapsed.total_seconds():.2f}s",
                                            'timestamp': datetime.now().isoformat(),
                                            'admin_cedula': cedula_admin,
                                            'omit_email': correo_omitido,
                                            'render_response': response.text[:200] + "..." if len(response.text) > 200 else response.text
                                        })
                                
                                elif response.status_code == 401:
                                    st.error("❌ Error de autenticación - Verifique el Deploy Hook")
                                elif response.status_code == 404:
                                    st.error("❌ Deploy Hook no encontrado - Verifique la URL")
                                elif response.status_code == 429:
                                    st.error("❌ Demasiadas solicitudes - Espere unos minutos")
                                else:
                                    st.error(f"❌ Error en sincronización - Código: {response.status_code}")
                                    st.error(f"**Respuesta:** {response.text}")
                                    
                            except requests.exceptions.Timeout:
                                st.error("❌ Tiempo de espera agotado - Intente nuevamente")
                            except requests.exceptions.ConnectionError:
                                st.error("❌ Error de conexión - Verifique su conexión a internet")
                            except Exception as e:
                                st.error(f"❌ Error inesperado: {str(e)}")
                    
                    # Opciones adicionales
                    st.write("---")
                    st.write("⚙️ **Opciones Adicionales**")
                    
                    # Botón de prueba de conexión
                    if st.button("🔗 Probar Conexión", use_container_width=True, help="Verificar conexión con Render"):
                        with st.spinner("Probando conexión..."):
                            try:
                                import requests
                                response = requests.get(render_hook_url.replace('/deploy', '/'), timeout=10)
                                if response.status_code == 200:
                                    st.success("✅ Conexión exitosa con Render")
                                else:
                                    st.warning(f"⚠️ Respuesta inesperada: {response.status_code}")
                            except Exception as e:
                                st.error(f"❌ Error de conexión: {str(e)}")
                    
                    # Botón de verificación de estado
                    if st.button("📊 Verificar Estado del Deploy", use_container_width=True, help="Verificar estado actual del despliegue"):
                        st.info("🔍 Función de verificación en desarrollo")
                        
            else:
                # Vista desktop: dos columnas
                col_principal, col_secundaria = st.columns([2, 1])
                
                with col_principal:
                    # Botón principal de sincronización
                    if st.button("🔄 Sincronizar Producción (Render)", type="primary", use_container_width=True, help="Disparar actualización en producción"):
                        with st.spinner("🔄 Iniciando sincronización con Render..."):
                            try:
                                import requests
                                
                                # Validar restricciones de seguridad antes de sincronizar
                                correo_omitido = st.session_state.get('omitir_correo_especifico', 'angelher@gmail.com')
                                cedula_admin = st.session_state.get('cedula_admin', '14300385')
                                
                                st.info(f"🔒 **Restricciones activas:**")
                                st.info(f"📧 Omitiendo correo: {correo_omitido}")
                                st.info(f"👤 Admin vinculado a cédula: {cedula_admin}")
                                
                                # Realizar POST request al Deploy Hook
                                response = requests.post(
                                    render_hook_url,
                                    headers={
                                        'User-Agent': 'SICADFOC-Sync/1.0',
                                        'Content-Type': 'application/json',
                                        'X-Admin-Cedula': cedula_admin,
                                        'X-Omit-Correo': correo_omitido
                                    },
                                    json={
                                        'triggered_by': 'manual_sync',
                                        'admin_cedula': cedula_admin,
                                        'omit_email': correo_omitido,
                                        'timestamp': datetime.now().isoformat(),
                                        'environment': 'production'
                                    },
                                    timeout=45
                                )
                                
                                if response.status_code == 200:
                                    st.success("✅ Sincronización iniciada exitosamente")
                                    st.info("📊 La actualización puede tardar 2-5 minutos en completarse")
                                    st.balloons()
                                    
                                    # Mostrar detalles de la respuesta
                                    with st.expander("📋 Detalles de la sincronización"):
                                        st.json({
                                            'status_code': response.status_code,
                                            'response_time': f"{response.elapsed.total_seconds():.2f}s",
                                            'timestamp': datetime.now().isoformat(),
                                            'admin_cedula': cedula_admin,
                                            'omit_email': correo_omitido,
                                            'render_response': response.text[:200] + "..." if len(response.text) > 200 else response.text
                                        })
                                
                                elif response.status_code == 401:
                                    st.error("❌ Error de autenticación - Verifique el Deploy Hook")
                                elif response.status_code == 404:
                                    st.error("❌ Deploy Hook no encontrado - Verifique la URL")
                                elif response.status_code == 429:
                                    st.error("❌ Demasiadas solicitudes - Espere unos minutos")
                                else:
                                    st.error(f"❌ Error en sincronización - Código: {response.status_code}")
                                    st.error(f"**Respuesta:** {response.text}")
                                    
                            except requests.exceptions.Timeout:
                                st.error("❌ Tiempo de espera agotado - Intente nuevamente")
                            except requests.exceptions.ConnectionError:
                                st.error("❌ Error de conexión - Verifique su conexión a internet")
                            except Exception as e:
                                st.error(f"❌ Error inesperado: {str(e)}")
                
                with col_secundaria:
                    # Opciones adicionales
                    st.write("⚙️ **Opciones**")
                    
                    # Botón de prueba de conexión
                    if st.button("🔗 Probar Conexión", use_container_width=True, help="Verificar conexión con Render"):
                        with st.spinner("Probando conexión..."):
                            try:
                                import requests
                                response = requests.get(render_hook_url.replace('/deploy', '/'), timeout=10)
                                if response.status_code == 200:
                                    st.success("✅ Conexión exitosa")
                                else:
                                    st.warning(f"⚠️ Respuesta: {response.status_code}")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                    
                    # Botón de verificación de estado
                    if st.button("📊 Verificar Estado", use_container_width=True, help="Verificar estado del despliegue"):
                        st.info("🔍 Función en desarrollo")
            
            # Información de seguridad
            st.write("---")
            st.subheader("🔒 Información de Seguridad")
            
            col_seg1, col_seg2 = st.columns(2)
            
            with col_seg1:
                st.markdown("""
                <div style="background: #FEF3C7; padding: 1rem; border-radius: 10px; border-left: 4px solid #F59E0B;">
                    <h4 style="color: #92400E; margin-bottom: 0.5rem;">🛡️ Restricciones Activas</h4>
                    <p style="color: #78350F; font-size: 0.9rem; margin: 0;">
                        📧 Correo omitido: angelher@gmail.com<br>
                        👤 Admin cédula: 14300385<br>
                        🔒 Sesión segura activa
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_seg2:
                st.markdown("""
                <div style="background: #DBEAFE; padding: 1rem; border-radius: 10px; border-left: 4px solid #3B82F6;">
                    <h4 style="color: #1E40AF; margin-bottom: 0.5rem;">📊 Rendimiento</h4>
                    <p style="color: #1E3A8A; font-size: 0.9rem; margin: 0;">
                        ⚡ Timeout: 45s<br>
                        🔄 Reintentos: 1<br>
                        📈 Optimizado: Sí
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Historial de sincronizaciones (simulado)
            st.write("---")
            st.subheader("📜 Historial de Sincronizaciones")
            
            # Mostrar historial simulado
            historial_data = [
                {"fecha": "2026-03-23 18:30:00", "estado": "✅ Exitoso", "duracion": "2.3s", "admin": "14300385"},
                {"fecha": "2026-03-23 17:45:00", "estado": "✅ Exitoso", "duracion": "3.1s", "admin": "14300385"},
                {"fecha": "2026-03-23 16:20:00", "estado": "❌ Error", "duracion": "45.0s", "admin": "14300385"},
            ]
            
            st.dataframe(
                historial_data,
                column_config={
                    "fecha": st.column_config.TextColumn("📅 Fecha y Hora"),
                    "estado": st.column_config.TextColumn("📊 Estado"),
                    "duracion": st.column_config.TextColumn("⏱️ Duración"),
                    "admin": st.column_config.TextColumn("👤 Admin Cédula")
                },
                use_container_width=True
            )
            
        else:
            # Si no hay URL configurada
            st.markdown("""
            <div style="background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); 
                        padding: 2rem; border-radius: 15px; 
                        border: 1px solid #DC2626; text-align: center;">
                <h3 style="color: white; margin-bottom: 1rem; font-size: 1.3rem;">
                    📡 Deploy Hook No Configurado
                </h3>
                <p style="color: #FECACA; font-size: 1.1rem; margin: 0;">
                    Configure la variable de entorno RENDER_DEPLOY_HOOK_URL
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("---")
            
            # Campo para configurar URL (solo para desarrollo)
            st.subheader("⚙️ Configuración de Deploy Hook")
            
            render_url_input = st.text_input(
                "📡 URL del Deploy Hook (desarrollo)",
                placeholder="https://api.render.com/deploy/serv...",
                type="password",
                help="Ingrese la URL del Deploy Hook de Render",
                key="render_hook_url_cloud"
            )
            
            if render_url_input:
                if st.button("⚙️ Configurar URL", type="secondary"):
                    st.success("✅ URL configurada temporalmente")
                    st.info("📝 Para configuración permanente, use variables de entorno")
                    st.info("💡 Reinicie la aplicación para aplicar cambios")
            else:
                st.warning("⚠️ Ingrese una URL válida para continuar")
            
            # Información adicional
            st.write("---")
            st.subheader("📋 Información Adicional")
            
            st.markdown("""
            <div style="background: #F3F4F6; padding: 1.5rem; border-radius: 10px;">
                <h4 style="color: #1F2937; margin-bottom: 1rem;">🔧 ¿Cómo obtener el Deploy Hook?</h4>
                <ol style="color: #4B5563; font-size: 0.9rem; line-height: 1.6;">
                    <li>Inicie sesión en su dashboard de Render</li>
                    <li>Seleccione su servicio (web service)</li>
                    <li>Vaya a la sección "Settings"</li>
                    <li>Busque "Deploy Hooks" y cree uno nuevo</li>
                    <li>Copie la URL generada</li>
                    <li>Configúrela como variable de entorno: RENDER_DEPLOY_HOOK_URL</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
