import streamlit as st
import pandas as pd
import os
import io
import shutil
from datetime import datetime
from sqlalchemy import text

# Importar módulos de base de datos
import database
from database import *

# =================================================================
# 1. SISTEMA DE ESTÉTICA PROFESIONAL (UI/UX)
# =================================================================

def inject_custom_css():
    """Inyecta CSS personalizado para diseño moderno y juvenil"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables de color - Paleta Slate/Midnight */
    :root {
        --bg-primary: #0F172A;
        --bg-secondary: #1E293B;
        --bg-tertiary: #334155;
        --text-primary: #F8FAFC;
        --text-secondary: #CBD5E1;
        --text-muted: #64748B;
        --accent-blue: #38BDF8;
        --accent-blue-dark: #0EA5E9;
        --accent-gradient: linear-gradient(135deg, #38BDF8 0%, #0EA5E9 100%);
        --border-subtle: #334155;
        --border-focus: #38BDF8;
        --success: #10B981;
        --warning: #F59E0B;
        --error: #EF4444;
    }
    
    /* Fuente global */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    /* Fondo principal */
    .stApp > div {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    
    /* Sidebar moderno */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    
    .css-1d391kg .css-17eqqhr {
        background-color: transparent !important;
    }
    
    /* Separación visual en sidebar */
    .sidebar-separator {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-subtle), transparent);
        margin: 1rem 0;
    }
    
    /* Logo IUJO styling */
    .logo-container {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid var(--border-subtle);
        margin-bottom: 1rem;
    }
    
    /* Botones modernos */
    .stButton > button {
        background: var(--accent-gradient) !important;
        border: none !important;
        border-radius: 10px !important;
        color: white !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.4) !important;
        background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }
    
    /* Botones tipo primary */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-blue-dark) 100%) !important;
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.4) !important;
    }
    
    /* Botones tipo secondary */
    .stButton > button[kind="secondary"] {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-subtle) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: var(--accent-gradient) !important;
        border-color: var(--accent-blue) !important;
    }
    
    /* Inputs de formulario modernos */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.75rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.1) !important;
        outline: none !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-muted) !important;
    }
    
    /* Labels de formularios */
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Radio buttons modernos */
    .stRadio > div[role="radiogroup"] > label {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        margin: 0.25rem 0 !important;
        transition: all 0.3s ease !important;
    }
    
    .stRadio > div[role="radiogroup"] > label:hover {
        border-color: var(--accent-blue) !important;
        background-color: var(--bg-tertiary) !important;
    }
    
    .stRadio > div[role="radiogroup"] > label[data-baseweb="radio-checked"] {
        background: var(--accent-gradient) !important;
        border-color: var(--accent-blue) !important;
        color: white !important;
    }
    
    /* Tabs modernos */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--bg-secondary) !important;
        border-radius: 10px !important;
        padding: 0.5rem !important;
        border: 1px solid var(--border-subtle) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: var(--bg-tertiary) !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--accent-gradient) !important;
        color: white !important;
    }
    
    /* DataFrames modernos */
    .dataframe {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }
    
    .dataframe th {
        background-color: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 1rem !important;
    }
    
    .dataframe td {
        background-color: var(--bg-secondary) !important;
        color: var(--text-secondary) !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.75rem 1rem !important;
        border-top: 1px solid var(--border-subtle) !important;
    }
    
    /* Métricas y cards */
    .stMetric {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stMetric label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stMetric div {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Expander modernos */
    .streamlit-expanderHeader {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .streamlit-expanderContent {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
    }
    
    /* Success, Warning, Error messages */
    .stSuccess {
        background-color: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid var(--success) !important;
        border-radius: 8px !important;
        color: var(--success) !important;
    }
    
    .stWarning {
        background-color: rgba(245, 158, 11, 0.1) !important;
        border: 1px solid var(--warning) !important;
        border-radius: 8px !important;
        color: var(--warning) !important;
    }
    
    .stError {
        background-color: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid var(--error) !important;
        border-radius: 8px !important;
        color: var(--error) !important;
    }
    
    .stInfo {
        background-color: rgba(56, 189, 248, 0.1) !important;
        border: 1px solid var(--accent-blue) !important;
        border-radius: 8px !important;
        color: var(--accent-blue) !important;
    }
    
    /* Headers y títulos */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* Texto general */
    p, span, div {
        color: var(--text-secondary) !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Iconos en sidebar */
    .module-icon {
        margin-right: 0.5rem;
        font-size: 1.2rem;
    }
    
    /* Scrollbar personalizado */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-primary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--bg-tertiary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-blue);
    }
    </style>
    """, unsafe_allow_html=True)

def get_module_icons():
    """Devuelve iconos modernos para los módulos"""
    return {
        "Inicio": "🏠",
        "Gestión Estudiantil": "📚",
        "Gestión de Profesores": "👨‍🏫",
        "Gestión de Formación Complementaria": "🎓",
        "Configuración": "⚙️",
        "Reportes": "📊",
        "Monitor de Sistema": "⚡",
        "⚙️ Gestión de Ambientes (ITIL)": "🛠️"
    }

# Inyectar CSS al inicio
inject_custom_css()

# Configuración de página para despliegue responsive
st.set_page_config(
    page_title="SICADFOC - Sistema de Control de Formación Complementaria",
    page_icon="🎓",
    layout="wide",  # Aprovecha mejor las pantallas de laptops
    initial_sidebar_state="expanded"
)

# =================================================================
# 2. VARIABLES GLOBALES Y MOTORES DE BASE DE DATOS
# =================================================================

# Obtener motores de base de datos
engine_l = database.get_engine_local()
engine_r = database.get_engine_espejo()

# Variable global para rol_actual
rol_actual = None

def actualizar_rol_actual():
    """Actualiza la variable global rol_actual desde session_state"""
    global rol_actual
    rol_actual = st.session_state.get('rol', 'estudiante')
    return rol_actual

def mostrar_toast(mensaje, tipo="info", duracion=3):
    """Muestra una notificación toast limpia sin errores púrpura"""
    # Usar st.toast que es más limpio que las alertas púrpura
    if tipo == "success":
        st.toast(f"✅ {mensaje}", icon="✅")
    elif tipo == "warning":
        st.toast(f"⚠️ {mensaje}", icon="⚠️")
    elif tipo == "error":
        st.toast(f"❌ {mensaje}", icon="❌")
    else:  # info
        st.toast(f"ℹ️ {mensaje}", icon="ℹ️")

def mostrar_mensaje_flotante(mensaje, tipo="info", icono="ℹ️"):
    """Muestra mensaje flotante con estilo moderno"""
    colores = {
        "success": "#10B981",
        "warning": "#F59E0B", 
        "error": "#EF4444",
        "info": "#38BDF8"
    }
    
    color = colores.get(tipo, "#38BDF8")
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color}22 0%, {color}11 100%);
        border: 1px solid {color};
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        color: {color};
        font-weight: 500;
        box-shadow: 0 4px 15px {color}33;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    ">
        <span style="font-size: 1.2rem;">{icono}</span>
        <span>{mensaje}</span>
    </div>
    """, unsafe_allow_html=True)

# Diferenciación visual según ambiente
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Ambiente Producción (Render) - Usar database_espejo.py como conexión principal
    # Fondo blanco absoluto con texto negro para diferenciar de local
    st.markdown("""
    <style>
    /* Estilo general para producción - fondo blanco absoluto */
    .stApp {
        background-color: #ffffff !important;
        color: #1f2937 !important;
    }
    .main .block-container {
        background-color: #ffffff !important;
        color: #1f2937 !important;
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Estilo de sidebar para producción */
    .stSidebar {
        background-color: #f8fafc !important;
        color: #1f2937 !important;
        border-right: 1px solid #e5e7eb !important;
    }
    
    /* Campos de entrada */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background-color: #ffffff !important;
        color: #1f2937 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px !important;
    }
    
    /* Botones */
    .stButton > button {
        background-color: #3b82f6 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
    }
    
    .stButton > button:hover {
        background-color: #2563eb !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #111827 !important;
        font-weight: 600 !important;
    }
    
    /* DataFrames y tablas */
    .stDataFrame {
        background-color: #ffffff !important;
        color: #1f2937 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 6px !important;
    }
    
    .stDataFrame table {
        background-color: #ffffff !important;
    }
    
    .stDataFrame th {
        background-color: #f9fafb !important;
        color: #374151 !important;
        font-weight: 600 !important;
    }
    
    /* Alertas y mensajes */
    .stAlert {
        background-color: #f0f9ff !important;
        color: #1e40af !important;
        border: 1px solid #bfdbfe !important;
        border-radius: 6px !important;
    }
    
    .stSuccess {
        background-color: #f0fdf4 !important;
        color: #166534 !important;
        border: 1px solid #bbf7d0 !important;
    }
    
    .stError {
        background-color: #fef2f2 !important;
        color: #dc2626 !important;
        border: 1px solid #fecaca !important;
    }
    
    .stWarning {
        background-color: #fffbeb !important;
        color: #d97706 !important;
        border: 1px solid #fed7aa !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f8fafc !important;
        color: #374151 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 6px !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f8fafc !important;
        border-bottom: 1px solid #e5e7eb !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #6b7280 !important;
        background-color: transparent !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #3b82f6 !important;
        background-color: #ffffff !important;
        border-bottom: 2px solid #3b82f6 !important;
    }
    
    /* Progress bar */
    .stProgress .progress-bar {
        background-color: #3b82f6 !important;
    }
    
    /* Slider */
    .stSlider .stSlider {
        color: #3b82f6 !important;
    }
    
    /* Checkbox */
    .stCheckbox {
        color: #374151 !important;
    }
    
    /* Radio buttons */
    .stRadio > div {
        color: #374151 !important;
    }
    
    /* Selectbox options */
    .stSelectbox option {
        background-color: #ffffff !important;
        color: #1f2937 !important;
    }
    
    /* Footer */
    .footer {
        background-color: #ffffff !important;
        color: #6b7280 !important;
        border-top: 1px solid #e5e7eb !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # En producción, usar database_espejo.py como conexión principal
    # Importar funciones de database_espejo.py para producción
    # from database_espejo import get_connection_espejo, get_connection_info as get_espejo_info
    
    # Reemplazar funciones de conexión para producción
    # get_connection = get_connection_espejo
    # get_connection_info = get_espejo_info
    
    print("AMBIENTE PRODUCCIÓN DETECTADO - Usando database_espejo.py con fondo blanco")
    
else:
    # Ambiente Local - Mantener diseño actual (oscuro/personalizado) y usar database.py
    st.markdown("""
    <style>
    /* Estilo local - diseño oscuro personalizado */
    .stApp {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
        color: #f1f5f9 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    print("AMBIENTE LOCAL DETECTADO - Usando database.py con diseño oscuro")
from database import (
    get_connection, get_connection_info,
    listar_estudiantes, insertar_estudiante, actualizar_estudiante, eliminar_estudiante,
    insertar_formacion, listar_formaciones, eliminar_formacion,
    inscribir_estudiante_taller, obtener_profesores, eliminar_profesor,
    registrar_auditoria, obtener_auditoria,
    guardar_config_correo, obtener_config_correo,
    crear_usuario_prueba, crear_tablas_sistema, ejecutar_query, insertar_profesor,
    limpiar_columnas_profesores, limpiar_columnas_estudiantes, asegurar_estructura_persona,
    get_metricas_dashboard,
    sincronizar_base_de_datos, generar_backup_sql, migrar_datos_a_nube, verificar_entorno_local, test_connection_to_render,
    sincronizar_espejo_a_nube_overwrite, get_connection_espejo, get_info_espejo
)

# --- FUNCIONES CALLBACK PARA BOTONES DE ACCIÓN ---

def callback_consultar_formacion(formacion_id, formacion_data):
    """Callback para botón consultar formación"""
    st.session_state.accion_pendiente = 'consultar_formacion'
    st.session_state.formacion_id_seleccionada = formacion_id
    st.session_state.formacion_editar = formacion_data
    st.session_state.modo_edicion = False
    st.session_state.tab_activa = 1

def callback_editar_formacion(formacion_id, formacion_data):
    """Callback para botón editar formación"""
    st.session_state.accion_pendiente = 'editar_formacion'
    st.session_state.formacion_id_seleccionada = formacion_id
    st.session_state.formacion_editar = formacion_data
    st.session_state.modo_edicion = True
    st.session_state.tab_activa = 1

def callback_eliminar_formacion(formacion_id, nombre_formacion):
    """Callback para botón eliminar formación"""
    st.session_state.accion_pendiente = 'eliminar_formacion'
    st.session_state.formacion_id_seleccionada = formacion_id
    st.session_state.nombre_formacion_eliminar = nombre_formacion

def callback_editar_profesor(profesor_id, profesor_data):
    """Callback para botón editar profesor"""
    st.session_state.accion_pendiente = 'editar_profesor'
    st.session_state.profesor_id_seleccionado = profesor_id
    st.session_state.profesor_editar = profesor_data
    st.session_state.tab_prof_activa = 2

def callback_eliminar_profesor(profesor_id, nombre_profesor):
    """Callback para botón eliminar profesor"""
    st.session_state.accion_pendiente = 'eliminar_profesor'
    st.session_state.profesor_id_seleccionado = profesor_id
    st.session_state.nombre_prof_eliminar = nombre_profesor

# =================================================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS (SISTEMA SICADFOC)
# =================================================================
st.set_page_config(
    page_title="SICADFOC - IUJO",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded"
)

# CSS Personalizado: Botones en Gris (#6c757d) para Ingresar y Finalizar Sesión
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }

    /* Botones de acción general (Rojo IUJO) */
    .stButton>button {
        background-color: #AA1914;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        height: 3.2em;
        width: 100%;
        transition: 0.3s;
    }

    /* BOTÓN INGRESAR y FINALIZAR SESIÓN - Gris #6c757d específicamente */
    div.stForm [data-testid="stFormSubmitButton"] > button,
    div[data-testid="stSidebar"] .stButton > button {
        background-color: #6c757d !important;
        color: white !important;
        border: 1px solid #5a6268 !important;
    }
    div.stForm [data-testid="stFormSubmitButton"] > button:hover,
    div[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #5a6268 !important;
        color: white !important;
        opacity: 0.9;
    }

    .stButton>button:hover { background-color: #5a6268; color: white; opacity: 0.9; }

    /* Estilo del Sidebar */
    [data-testid="stSidebar"] { background-color: #1e1e1e; color: white; }
    [data-testid="stSidebarNav"] { background-color: #1e1e1e; }

    /* Estilo de Tabs */
    .stTabs [aria-selected="true"] {
        background-color: #AA1914 !important;
        color: white !important;
        border-radius: 5px 5px 0 0;
    }

    /* Métricas */
    div[data-testid="stMetricValue"] { color: #AA1914; font-size: 2.4rem; font-weight: bold; }
    .footer { position: fixed; bottom: 10px; width: 100%; text-align: center; color: #888; font-size: 0.8em; }

    /* Tablas limpias */
    div[data-testid="stDataFrame"] {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .stDataFrame th { background-color: #AA1914 !important; color: white !important; font-weight: 600; }
    .stDataFrame td { padding: 8px 12px !important; }
    .tabla-contenedor { padding: 1rem; background: white; border-radius: 8px; border: 1px solid #dee2e6; margin: 0.5rem 0; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 2. INICIALIZACIÓN DE CONEXIONES Y SESIÓN
# =================================================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if 'id_persona_est' not in st.session_state:
    st.session_state.id_persona_est = None
    st.session_state.apellido_est = ""

# Motores de base de datos
engine_l = get_connection()
engine_r = get_connection()

# =================================================================
# 2.4. DETECCIÓN DE AMBIENTE Y CONFIGURACIÓN DE TEMAS
# =================================================================

def detectar_base_datos_conectada():
    """Detecta qué base de datos está conectada y devuelve el tipo de ambiente"""
    try:
        # Obtener la URL de conexión del engine
        engine_info = str(engine_l.url)
        
        if 'render.com' in engine_info:
            return 'nube_render'
        elif 'foc26_limpio.db' in engine_info:
            return 'desarrollo'
        elif 'Foc26_espejo.db' in engine_info:
            return 'produccion_local'
        else:
            return 'desconocido'
    except Exception as e:
        print(f'Error detectando base de datos: {e}')
        return 'desconocido'

def configurar_tema_segun_ambiente(tipo_ambiente):
    """Configura el tema de Streamlit según el ambiente detectado"""
    if tipo_ambiente == 'nube_render':
        # Banner superior para nube
        st.markdown("""
        <div style="background-color: #10b981; padding: 10px; border-radius: 5px; margin-bottom: 20px; text-align: center;">
            <h3 style="color: white; margin: 0;">🚀 EJECUTANDO EN NUBE (RENDER)</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Modo Claro para Render
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%) !important;
        }
        .main > div {
            background-color: #ffffff !important;
            color: #1e293b !important;
        }
        .stTextInput > div > div > input {
            background-color: #f8fafc !important;
            color: #1e293b !important;
            border: 1px solid #cbd5e1 !important;
        }
        .stButton > button {
            background-color: #10b981 !important;
            color: white !important;
            border: none !important;
        }
        .stSelectbox > div > div > select {
            background-color: #f8fafc !important;
            color: #1e293b !important;
        }
        .sidebar .sidebar-content {
            background-color: #ffffff !important;
            color: #1e293b !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #1e293b !important;
        }
        p, label, div {
            color: #475569 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
    elif tipo_ambiente == 'desarrollo':
        # Modo Oscuro para Desarrollo
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
        }
        .main > div {
            background-color: #1e293b !important;
            color: #f1f5f9 !important;
        }
        .stTextInput > div > div > input {
            background-color: #334155 !important;
            color: #f1f5f9 !important;
            border: 1px solid #475569 !important;
        }
        .stButton > button {
            background-color: #3b82f6 !important;
            color: white !important;
            border: none !important;
        }
        .stSelectbox > div > div > select {
            background-color: #334155 !important;
            color: #f1f5f9 !important;
        }
        .sidebar .sidebar-content {
            background-color: #1e293b !important;
            color: #f1f5f9 !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #f1f5f9 !important;
        }
        p, label, div {
            color: #e2e8f0 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
    elif tipo_ambiente == 'produccion_local':
        # Modo Claro para Producción Local
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%) !important;
        }
        .main > div {
            background-color: #ffffff !important;
            color: #1e293b !important;
        }
        .stTextInput > div > div > input {
            background-color: #f8fafc !important;
            color: #1e293b !important;
            border: 1px solid #cbd5e1 !important;
        }
        .stButton > button {
            background-color: #10b981 !important;
            color: white !important;
            border: none !important;
        }
        .stSelectbox > div > div > select {
            background-color: #f8fafc !important;
            color: #1e293b !important;
        }
        .sidebar .sidebar-content {
            background-color: #ffffff !important;
            color: #1e293b !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #1e293b !important;
        }
        p, label, div {
            color: #475569 !important;
        }
        </style>
        """, unsafe_allow_html=True)

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
# 2.4.1. PROCESAMIENTO DE CONFIRMACIÓN DE CORREO
# =================================================================

# Verificar si hay parámetros de confirmación en la URL
query_params = st.query_params
if 'confirmar' in query_params and 'email' in query_params:
    token = query_params['confirmar']
    email = query_params['email']
    
    st.header("📧 Confirmación de Correo Electrónico")
    
    with st.spinner("Procesando confirmación..."):
        try:
            from database import confirmar_correo_token
            exito, mensaje = confirmar_correo_token(token, email, engine_l)
            
            if exito:
                st.success("✅ ¡Correo Confirmado Exitosamente!")
                st.info(mensaje)
                st.balloons()
                
                # Mostrar información del usuario
                with engine_l.connect() as conn:
                    verificar = conn.execute(database.text('SELECT login, rol FROM usuario WHERE login = :email'), 
                                           {'email': email})
                    usuario = verificar.fetchone()
                    
                    if usuario:
                        st.success(f"👤 Usuario: {usuario[0]}")
                        st.success(f"🔐 Rol: {usuario[1]}")
                        st.success("✅ Correo verificado: Sí")
                
                st.info("🎉 Ahora puede iniciar sesión con su correo verificado.")
                
            else:
                st.error("❌ Error en la Confirmación")
                st.error(mensaje)
                
        except Exception as e:
            st.error(f"❌ Error procesando confirmación: {str(e)}")
    
    # Botón para ir al login
    if st.button("🚪 Ir al Inicio de Sesión"):
        # Limpiar parámetros de URL
        st.query_params.clear()
        st.rerun()
    
    st.stop()  # Detener ejecución para mostrar solo la confirmación

# =================================================================
# 2.5. SISTEMA DE ROLES Y PERFILES (RBAC)
# =================================================================
def obtener_rol_usuario():
    """Obtiene el rol del usuario desde st.session_state"""
    return st.session_state.get('rol', 'estudiante')

def registrar_auditoria_sistema(usuario, transaccion, tabla_afectada=None, detalles_adicionales=None):
    """Función auxiliar para registrar auditoría con formato correcto"""
    # Importar la función de database
    from database import registrar_auditoria
    
    rol_actual = obtener_rol_usuario()
    ip_address = st.context.headers.get('x-forwarded-for', 'localhost')
    
    # Construir detalles
    detalles = f"Transacción: {transaccion}"
    if tabla_afectada:
        detalles += f", Tabla: {tabla_afectada}"
    if detalles_adicionales:
        detalles += f", Detalles: {detalles_adicionales}"
    detalles += f", Rol: {rol_actual}, IP: {ip_address}"
    
    # Llamar a la función real de database.py
    registrar_auditoria(
        accion=transaccion,
        usuario=usuario,
        detalles=detalles
    )
    return st.session_state.get('rol', 'estudiante')

def es_admin():
    """Verifica si el usuario es administrador"""
    rol = obtener_rol_usuario()
    return rol == 'admin' or rol == 'administrador'

def es_super_admin():
    """Verifica si el usuario es Super-Admin (angelher@gmail.com) con privilegios completos"""
    return st.session_state.user_data.get('login') == 'angelher@gmail.com'

def es_admin_o_super_admin():
    """Verifica si el usuario es administrador o Super-Admin"""
    return es_admin() or es_super_admin()

def es_profesor():
    """Verifica si el usuario es profesor"""
    rol = obtener_rol_usuario()
    return rol == 'profesor'

def es_estudiante():
    """Verifica si el usuario es estudiante"""
    rol = obtener_rol_usuario()
    return rol == 'estudiante'

def es_admin_o_profesor():
    """Verifica si el usuario es administrador o profesor"""
    rol = obtener_rol_usuario()
    return rol in ['admin', 'administrador', 'profesor']

def mostrar_mensaje_restringido():
    """Muestra mensaje de acceso restringido según el rol"""
    rol = obtener_rol_usuario()
    if rol == 'estudiante':
        st.warning("🔒 Esta función está disponible solo para administradores y profesores.")
        st.info("Si necesita acceso, contacte al administrador del sistema.")
    elif rol == 'profesor':
        st.warning("🔒 Esta función está disponible solo para administradores.")
        st.info("Si necesita acceso, contacte al administrador del sistema.")

# =================================================================
# 3. INTERFAZ DE AUTENTICACIÓN (LOGIN) - DISEÑO MODERNO
# =================================================================
if not st.session_state.autenticado:
    # Contenedor principal del login
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
    
    # Formulario de login
    with st.form("login_form", clear_on_submit=False):
        st.markdown("""
        <div style="background: #1E293B; padding: 2rem; border-radius: 15px; 
                    border: 1px solid #334155; margin-top: -2rem;">
            <h3 style="color: #F8FAFC; text-align: center; margin-bottom: 1.5rem;">
                🔐 INICIAR SESIÓN
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Campos del formulario
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
        
        # Botón de login centrado
        _, col_center, _ = st.columns([1, 2, 1])
        with col_center:
            btn_login = st.form_submit_button(
                "🚀 INGRESAR AL SISTEMA", 
                type="primary",
                use_container_width=True
            )

        if btn_login:
            # Crear tablas del sistema si no existen
            crear_tablas_sistema(engine_l)
            
            # Crear usuario de prueba si no existe
            crear_usuario_prueba(engine_l)
            
            # Verificación en Gabinete Local con Correo/Cédula
            import hashlib
            # Hashear la contraseña ingresada
            hash_password = hashlib.sha256(p.encode()).hexdigest()
            
            query_auth = """
                SELECT * FROM usuario 
                WHERE (email = :email OR login = :email) AND contrasena = :password AND activo = TRUE
            """
            res_auth = ejecutar_query(query_auth, {"email": u, "password": hash_password}, engine=engine_l)

            if res_auth is not None and len(res_auth) > 0:
                # Convertir DataFrame a diccionario
                usuario_data = res_auth.iloc[0].to_dict()
                st.session_state.autenticado = True
                st.session_state.user_data = usuario_data
                st.session_state.rol = usuario_data.get('rol', 'estudiante')
                
                # Registrar auditoría de login
                registrar_auditoria_sistema(
                    usuario=usuario_data.get('login', u),
                    transaccion='LOGIN',
                    tabla_afectada='usuario'
                )
                
                st.success(f"🎉 ¡Bienvenido {usuario_data.get('login', u)}! Rol: {st.session_state.rol.title()}")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Error de autenticación. Verifique su correo y cédula.")
                st.info("💡 Si es su primer acceso, contacte al administrador del sistema.")
    
    st.stop()

# =================================================================
# 4. PANEL DE NAVEGACIÓN (SIDEBAR) - DISEÑO MODERNO
# =================================================================
with st.sidebar:
    # Logo IUJO con contenedor moderno
    st.markdown("""
    <div class="logo-container">
        <img src="https://via.placeholder.com/120x80/0F172A/38BDF8?text=IUJO" 
             style="border-radius: 8px; margin-bottom: 0.5rem;" 
             alt="IUJO Logo">
        <div style="color: #F8FAFC; font-size: 0.8rem; font-weight: 500;">
            SICADFOC 2026
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if os.path.exists("iujo-logo.png"):
        st.markdown("""
        <div class="logo-container">
            <img src="data:image/png;base64,{}" 
                 style="border-radius: 8px; margin-bottom: 0.5rem;" 
                 alt="IUJO Logo">
            <div style="color: #F8FAFC; font-size: 0.8rem; font-weight: 500;">
                SICADFOC 2026
            </div>
        </div>
        """.format(
            st.image("iujo-logo.png", width=120, output_format="PNG", use_column_width=False)
        ), unsafe_allow_html=True)
    
    # Separador visual
    st.markdown('<div class="sidebar-separator"></div>', unsafe_allow_html=True)
    
    # Mostrar aviso de ambiente
    mostrar_aviso_ambiente(tipo_ambiente)
    
    # Separador visual
    st.markdown('<div class="sidebar-separator"></div>', unsafe_allow_html=True)
    
    # Información de usuario con diseño moderno
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
    
    # Separador visual
    st.markdown('<div class="sidebar-separator"></div>', unsafe_allow_html=True)
    
    # Menú de navegación principal con iconos modernos
    st.markdown("""
    <div style="color: #CBD5E1; font-weight: 600; font-size: 0.9rem; margin-bottom: 1rem;">
        📋 MÓDULOS OPERATIVOS
    </div>
    """, unsafe_allow_html=True)
    
    # Obtener iconos
    icons = get_module_icons()
    
    # Crear opciones con iconos
    opciones_modulos = [
        f"{icons['Inicio']} Inicio",
        f"{icons['Gestión Estudiantil']} Gestión Estudiantil", 
        f"{icons['Gestión de Profesores']} Gestión de Profesores",
        f"{icons['Gestión de Formación Complementaria']} Gestión de Formación Complementaria",
        f"{icons['Configuración']} Configuración",
        f"{icons['Reportes']} Reportes",
        f"{icons['Monitor de Sistema']} Monitor de Sistema",
        f"{icons['⚙️ Gestión de Ambientes (ITIL)']} ⚙️ Gestión de Ambientes (ITIL)"
    ]
    
    # Radio buttons personalizados
    seleccion = st.radio(
        "",
        opciones_modulos,
        index=0,
        label_visibility="collapsed"
    )
    
    # Extraer el nombre del módulo (sin icono)
    modulo = seleccion.split(" ", 1)[1] if " " in seleccion else seleccion
    
    # Separador visual
    st.markdown('<div class="sidebar-separator"></div>', unsafe_allow_html=True)
    
    # Botón de cerrar sesión con estilo moderno
    if st.button("🚪 Finalizar Sesión", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# =================================================================
# 5. DESARROLLO DE MÓDULOS OPERATIVOS
# =================================================================

# --- MÓDULO A: INICIO ---
if modulo == "Inicio":
    st.header("🏠 Panel Principal de Control")
    st.write(f"Resumen de operaciones para el usuario: **{st.session_state.user_data['login']}**")

    col_dash1, col_dash2, col_dash3 = st.columns(3)

    try:
        metricas = get_metricas_dashboard(engine_l)
        t_talleres = metricas['talleres']
        t_estudiantes = metricas['estudiantes']
        t_profesores = metricas['profesores']

        col_dash1.metric("Talleres Activos", t_talleres)
        col_dash2.metric("Estudiantes Registrados", t_estudiantes)
        col_dash3.metric("Profesores", t_profesores)

    except Exception as e:
        st.warning("⚠️ Sincronizando datos con el Gabinete Local...")

    st.divider()
    st.info("💡 **Aviso:** El Monitor de Infraestructura ahora se encuentra en el menú lateral para una vista más limpia.")

# --- MÓDULO B: MONITOR DE SISTEMA (GABINETES) ---
elif modulo == "Monitor de Sistema":
    st.header("⚡ Monitor de Infraestructura de Datos")
    st.write("Verificación de gabinetes FOC26 (Local y Cloud).")

    col_mon1, col_mon2 = st.columns(2)

    with col_mon1:
        st.subheader("🖥️ Gabinete Local (PC)")
        if engine_l:
            try:
                with engine_l.connect() as conn:
                    res_l = conn.execute(text("SELECT current_database(), current_user, version()")).fetchone()
                    st.success("✅ Servidor Local: ONLINE")
                    st.table(pd.DataFrame([{
                        "Base de Datos": res_l[0],
                        "Usuario": res_l[1],
                        "Estado": "Sincronizado"
                    }]))
            except Exception as e:
                st.error(f"❌ Error de conexión Local: {e}")

    with col_mon2:
        st.subheader("☁️ Gabinete Render (Cloud)")
        if engine_r and not isinstance(engine_r, str):
            try:
                with engine_r.connect() as conn:
                    res_r = conn.execute(text("SELECT current_database()")).fetchone()
                    st.success("✅ Servidor Render: CONECTADO")
                    st.table(pd.DataFrame([{
                        "Base de Datos": res_r[0],
                        "Región": "USA-East",
                        "Plataforma": "Render.com"
                    }]))
            except Exception as e:
                st.error(f"❌ Error de conexión Cloud: {e}")
        else:
            st.warning("⚠️ Conexión Cloud no detectada o configurada.")

# --- MÓDULO C: GESTIÓN ESTUDIANTIL ---
elif modulo == "Gestión Estudiantil":
    asegurar_estructura_persona(engine_l)
    st.header("📂 Gestión de Matrícula Estudiantil")
    t1, t2, t3, t4, t5, t6 = st.tabs([
        "📝 Inscripción y Carga", "📋 Listado de Estudiantes", "📊 Seguimiento Académico", 
        "🎓 Digitalización PDF", "📜 Historial", "👤 Registro Individual"
    ])

    with t1:
        st.subheader("Proceso de Carga Masiva (Excel/CSV)")
        st.write("Cargue listados de alumnos directamente a la base de datos local.")
        file_bulk = st.file_uploader("Subir archivo de estudiantes", type=['xlsx', 'csv'], key="bulk_est")

        if file_bulk:
            try:
                if file_bulk.name.endswith('.xlsx'):
                    df_b = pd.read_excel(file_bulk)
                else:
                    # Intentar lectura automática de separadores
                    try:
                        df_b = pd.read_csv(file_bulk, sep=None, engine='python', encoding='utf-8-sig')
                    except UnicodeDecodeError:
                        try:
                            df_b = pd.read_csv(file_bulk, sep=None, engine='python', encoding='latin-1')
                        except Exception:
                            df_b = pd.read_csv(file_bulk, sep=None, engine='python', encoding='utf-8')
                    
                    # Limpiar nombres de columnas
                    df_b.columns = df_b.columns.astype(str).str.strip()
                    
                    # Verificar si sigue con una sola columna (fallback)
                    if len(df_b.columns) == 1 and ';' in str(df_b.iloc[0, 0]):
                        st.warning("🔍 Detectando separador punto ycoma...")
                        try:
                            df_b = pd.read_csv(file_bulk, sep=';', encoding='utf-8-sig')
                            df_b.columns = df_b.columns.astype(str).str.strip()
                        except UnicodeDecodeError:
                            df_b = pd.read_csv(file_bulk, sep=';', encoding='latin-1')
                            df_b.columns = df_b.columns.astype(str).str.strip()
                    
                    # Validar que el DataFrame tenga múltiples columnas
                    if len(df_b.columns) == 1:
                        raise ValueError("El archivo no pudo ser procesado correctamente. Solo se detectó una columna. Verifique el separador usado.")
                        
            except Exception as ex:
                st.error(f"❌ Error al leer el archivo: {ex}")
                st.info("💡 Asegúrese de que el archivo use coma (,), punto ycoma (;) o tabulación como separador.")
                df_b = None

            if df_b is not None and not df_b.empty:
                df_limpio, mapeo = limpiar_columnas_estudiantes(df_b)

                if df_limpio is None:
                    st.error("⚠️ El archivo debe contener al menos: Cedula y Nombre. Las demás columnas son opcionales (Apellido, Genero, Telefono, Carrera, Semestre).")
                    st.write("**Columnas detectadas:**", list(df_b.columns))
                    # Solo mostrar vista previa si el DataFrame fue procesado correctamente
                    if len(df_b.columns) > 1:
                        st.markdown("**Vista previa:**")
                        st.dataframe(df_b.head(5), use_container_width=True, hide_index=True)
                else:
                    st.markdown("**Vista previa de datos a cargar**")
                    st.dataframe(df_limpio, use_container_width=True, hide_index=True)
                    st.caption(f"Total: {len(df_limpio)} registros. Columnas: Cedula, Apellido, Nombre, Genero, Telefono, Carrera, Semestre.")

                    if st.button("🚀 Ejecutar Carga en PostgreSQL"):
                        progreso = st.progress(0)
                        total_filas = len(df_limpio)
                        exitosos = 0
                        fallidos = 0
                        errores = []
                        
                        for i, row in df_limpio.iterrows():
                            # Usar .get() para columnas opcionales, solo exigir 'cedula' y 'nombre'
                            cedula = row.get('cedula', '').strip()
                            nombre = row.get('nombre', '').strip()
                            
                            if not cedula or not nombre:
                                fallidos += 1
                                errores.append(f"Fila {i+1}: Cédula y nombre son obligatorios")
                                progreso.progress((i + 1) / total_filas)
                                continue
                            
                            # Columnas opcionales con valores por defecto
                            apellido = row.get('apellido', '').strip()
                            genero = row.get('genero', '').strip()
                            telefono = row.get('telefono', '').strip()
                            carrera = row.get('carrera', '').strip()
                            semestre = row.get('semestre', '').strip()
                            
                            exito, mensaje = insertar_estudiante(
                                cedula=cedula,
                                apellido=apellido,
                                nombre=nombre,
                                genero=genero,
                                telefono=telefono,
                                carrera=carrera,
                                semestre=semestre,
                                engine=engine_l
                            )
                            
                            if exito:
                                exitosos += 1
                            else:
                                fallidos += 1
                                errores.append(f"Fila {i+1}: {mensaje}")
                            
                            progreso.progress((i + 1) / total_filas)
                        
                        # Mostrar resumen de resultados
                        if exitosos > 0:
                            st.success(f"✅ {exitosos} registros procesados exitosamente.")
                        if fallidos > 0:
                            st.error(f"❌ {fallidos} registros fallaron.")
                            with st.expander("Ver detalles de errores"):
                                for error in errores[:10]:  # Limitar a 10 errores para no saturar
                                    st.write(f"• {error}")
                                if len(errores) > 10:
                                    st.write(f"... y {len(errores) - 10} errores más.")
                        
                        st.info("💡 Vaya a la pestaña «Listado de Estudiantes» para verificar los datos cargados.")

    with t2:
        st.subheader("📋 Listado de Estudiantes Registrados")
        st.write("Estudiantes cargados en la base de datos.")
        data_est = listar_estudiantes(engine_l)
        if data_est:
            # Mostrar métricas para admin/profesor
            if es_admin_o_profesor():
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("👥 Total Estudiantes", len(data_est))
                col_m2.metric("✅ Activos", len([e for e in data_est if e.get('Cédula')]))
                col_m3.metric("📊 Registros Hoy", len(data_est))  # TODO: Implementar filtro por fecha
            
            # Convertir a DataFrame para mejor manipulación
            df_est = pd.DataFrame(data_est)
            
            # Tabla de visualización limpia (sin botones)
            st.dataframe(df_est, use_container_width=True, hide_index=True)
            
            # Panel de Gestión Unificado
            if es_admin_o_profesor() and data_est:
                st.subheader("🔧 Panel de Gestión de Estudiantes")
                
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        # Selectbox para elegir estudiante por cédula
                        opciones_estudiantes = [f"{e.get('Cédula', 'N/A')} - {e.get('Nombre', 'N/A')} {str(e.get('Apellido', '')).replace('None', '').strip()}" for e in data_est]
                        estudiante_seleccionado = st.selectbox(
                            "Seleccionar Estudiante:",
                            options=opciones_estudiantes,
                            help="Elija un estudiante para gestionar"
                        )
                    
                    with col2:
                        confirmar_accion = st.checkbox("✅ Confirmar Acción", help="Marque para habilitar los botones")
                    
                    with col3:
                        st.write("")  # Espacio vacío para alineación
                
                if estudiante_seleccionado and confirmar_accion:
                    # Extraer cédula del estudiante seleccionado
                    cedula_seleccionada = estudiante_seleccionado.split(" - ")[0]
                    
                    # Encontrar datos completos del estudiante
                    estudiante_data = next((e for e in data_est if e.get('Cédula') == cedula_seleccionada), None)
                    
                    if estudiante_data:
                        col_edit, col_delete = st.columns(2)
                        
                        with col_edit:
                            if st.button("📝 Editar Estudiante", type="primary", use_container_width=True):
                                # Guardar ID para edición
                                st.session_state.id_a_editar = cedula_seleccionada
                                st.session_state.tab_index = 3  # Cambiar a pestaña Registro Individual
                                st.rerun()
                        
                        with col_delete:
                            if st.button("🗑️ Eliminar Estudiante", type="secondary", use_container_width=True):
                                # Confirmación y eliminación
                                st.warning(f"⚠️ ¿Está seguro de eliminar al estudiante '{estudiante_data.get('Nombre', '')} {estudiante_data.get('Apellido', '')}'?")
                                col_confirm, col_cancel = st.columns(2)
                                
                                with col_confirm:
                                    if st.button("✅ Sí, Eliminar", key="confirm_eliminar_estudiante"):
                                        exito, mensaje = eliminar_estudiante(cedula_seleccionada, engine=engine_l)
                                        if exito:
                                            # Registrar auditoría
                                            registrar_auditoria(
                                                usuario=st.session_state.user_data.get('login'),
                                                rol=obtener_rol_usuario(),
                                                transaccion='DELETE',
                                                tabla_afectada='persona',
                                                registro_id=cedula_seleccionada,
                                                detalles=f"cedula:{cedula_seleccionada}, nombre:{estudiante_data.get('Nombre', '')} {estudiante_data.get('Apellido', '')}",
                                                engine=engine_l
                                            )
                                            st.success("✅ Estudiante eliminado exitosamente")
                                            st.rerun()
                                        else:
                                            st.error(f"❌ Error al eliminar: {mensaje}")
                                
                                with col_cancel:
                                    if st.button("❌ Cancelar", key="cancel_eliminar_estudiante"):
                                        st.rerun()
                else:
                    st.info("� Seleccione un estudiante y confirme la acción para habilitar los botones")
            else:
                # Estudiante solo ve datos básicos
                st.dataframe(df_est[['Cédula', 'Nombre', 'Apellido']], use_container_width=True, hide_index=True)
                mostrar_mensaje_restringido()
                
            st.caption(f"Total: {len(data_est)} estudiantes registrados.")
        else:
            st.info("No hay estudiantes registrados. Cargue un archivo CSV en la pestaña «Inscripción y Carga».")

    with t3:
        st.subheader("Seguimiento de Inscritos")
        q_list = """
            SELECT p.cedula as "Cédula", p.apellido as "Apellido", p.nombre as "Nombre",
                   p.genero as "Género", p.telefono as "Teléfono", p.carrera as "Carrera", p.semestre as "Semestre",
                   t.nombre_taller as "Formación", fc.estado as "Estatus"
            FROM public.inscripcion i
            JOIN public.persona p ON i.id_persona = p.id_persona
            JOIN public.formacion_complementaria fc ON i.id_formacion = fc.id_formacion
            JOIN public.taller t ON fc.id_taller = t.id_taller
        """
        data_list = ejecutar_query(q_list, engine=engine_l)
        if data_list:
            st.dataframe(pd.DataFrame(data_list), use_container_width=True, hide_index=True)
            st.caption(f"Total: {len(data_list)} inscripciones.")
        else:
            st.info("No hay inscripciones registradas para mostrar.")

    with t4:
        st.subheader("🎓 Digitalización Real de Expedientes")
        st.write("Asocie documentos PDF escaneados al expediente del alumno.")

        c_p1, c_p2 = st.columns(2)
        with c_p1:
            ced_pdf = st.text_input("Cédula para vincular:")
        with c_p2:
            tipo_doc = st.selectbox("Tipo de Documento:", ["Cédula", "Título", "Certificado Notas", "Otros"])

        f_pdf = st.file_uploader("Subir Archivo (Solo PDF)", type=['pdf'])

        if st.button("📤 Guardar Documento Digital"):
            if ced_pdf and f_pdf:
                # CREACIÓN FÍSICA DE CARPETAS
                base_dir = "expedientes_digitales_foc26"
                est_dir = os.path.join(base_dir, ced_pdf)

                if not os.path.exists(est_dir):
                    os.makedirs(est_dir)

                final_path = os.path.join(est_dir, f"{tipo_doc}_{f_pdf.name}")

                with open(final_path, "wb") as f:
                    f.write(f_pdf.getbuffer())

                st.success(f"✅ Archivo almacenado en: {final_path}")
            else:
                st.error("⚠️ Ingrese la cédula y cargue el archivo PDF.")

    with t5:
        st.subheader("📜 Consulta de Historial Académico")
        c_bus = st.text_input("Cédula a consultar:")
        if c_bus:
            q_h = """
                SELECT t.nombre_taller, fc.codigo_cohorte, fc.estado
                FROM public.inscripcion i
                JOIN public.persona p ON i.id_persona = p.id_persona
                JOIN public.formacion_complementaria fc ON i.id_formacion = fc.id_formacion
                JOIN public.taller t ON fc.id_taller = t.id_taller
                WHERE p.cedula = :c
            """
            res_h = ejecutar_query(q_h, {"c": c_bus}, engine_l)

    with t6:
        st.subheader("👤 Registro Individual de Estudiantes")
        st.write("Ingrese los datos del estudiante de forma manual.")
        
        # Verificar si hay datos para editar
        estudiante_editar = st.session_state.get('estudiante_editar')
        
        with st.form("form_estudiante_individual"):
            col1, col2 = st.columns(2)
            with col1:
                cedula_ind = st.text_input("Cédula*", help="Campo obligatorio", 
                                         value=estudiante_editar.get('Cédula', '') if estudiante_editar else '',
                                         disabled=bool(estudiante_editar))  # Deshabilitar cédula en edición
                nombre_ind = st.text_input("Nombre*", help="Campo obligatorio",
                                         value=estudiante_editar.get('Nombre', '') if estudiante_editar else '')
                telefono_ind = st.text_input("Teléfono",
                                         value=estudiante_editar.get('Teléfono', '') if estudiante_editar else '')
            with col2:
                apellido_ind = st.text_input("Apellido",
                                         value=estudiante_editar.get('Apellido', '') if estudiante_editar else '')
                correo_ind = st.text_input("Correo Electrónico", help="Formato: usuario@dominio.com",
                                         value=estudiante_editar.get('Correo', '') if estudiante_editar else '')
                direccion_ind = st.text_input("Dirección",
                                         value=estudiante_editar.get('Dirección', '') if estudiante_editar else '')
            
            # Campos adicionales opcionales
            col3, col4 = st.columns(2)
            with col3:
                genero_ind = st.selectbox("Género", ["", "M", "F"],
                                        index=["", "M", "F"].index(estudiante_editar.get('Género', '')) if estudiante_editar and estudiante_editar.get('Género') in ["", "M", "F"] else 0)
                carrera_ind = st.text_input("Carrera",
                                         value=estudiante_editar.get('Carrera', '') if estudiante_editar else '')
            with col4:
                semestre_ind = st.text_input("Semestre",
                                         value=estudiante_editar.get('Semestre', '') if estudiante_editar else '')
            
            btn_guardar_est = st.form_submit_button("💾 Guardar Estudiante", type="primary")
            
            if btn_guardar_est:
                # Validaciones
                if not cedula_ind.strip():
                    st.error("⚠️ La Cédula es un campo obligatorio.")
                elif not nombre_ind.strip():
                    st.error("⚠️ El Nombre es un campo obligatorio.")
                elif correo_ind and "@" not in correo_ind:
                    st.error("⚠️ El correo electrónico debe tener un formato válido (contener @).")
                else:
                    # Normalizar datos a mayúsculas
                    params_est = {
                        "cedula": cedula_ind.strip().upper(),
                        "nombre": nombre_ind.strip().upper(),
                        "apellido": apellido_ind.strip().upper() if apellido_ind else "",
                        "genero": genero_ind.strip().upper() if genero_ind else "",
                        "telefono": telefono_ind.strip() if telefono_ind else "",
                        "carrera": carrera_ind.strip().upper() if carrera_ind else "",
                        "semestre": semestre_ind.strip() if semestre_ind else ""
                    }
                    
                    # Determinar si es inserción o actualización
                    if estudiante_editar:
                        # Modo edición - actualizar estudiante existente
                        exito, mensaje = actualizar_estudiante(
                            cedula=params_est["cedula"],
                            apellido=params_est["apellido"],
                            nombre=params_est["nombre"],
                            genero=params_est["genero"],
                            telefono=params_est["telefono"],
                            carrera=params_est["carrera"],
                            semestre=params_est["semestre"],
                            engine=engine_l
                        )
                        transaccion_tipo = 'UPDATE'
                    else:
                        # Modo inserción - nuevo estudiante
                        exito, mensaje = insertar_estudiante(
                            cedula=params_est["cedula"],
                            apellido=params_est["apellido"],
                            nombre=params_est["nombre"],
                            genero=params_est["genero"],
                            telefono=params_est["telefono"],
                            carrera=params_est["carrera"],
                            semestre=params_est["semestre"],
                            engine=engine_l
                        )
                        transaccion_tipo = 'REGISTRO_MANUAL_ESTUDIANTE'
                        
                        # Si el estudiante se registró exitosamente y tiene correo, enviar confirmación
                        if exito and correo_ind:
                            try:
                                # Crear usuario en tabla usuario con correo_verificado = 0
                                import hashlib
                                password_temp = params_est["cedula"]  # Usar cédula como contraseña temporal
                                hashed_password = hashlib.sha256(password_temp.encode()).hexdigest()
                                
                                with engine_l.connect() as conn:
                                    # Verificar si ya existe usuario
                                    verificar_usuario = conn.execute(database.text('SELECT login FROM usuario WHERE login = :email'), 
                                                                   {'email': correo_ind})
                                    usuario_existente = verificar_usuario.fetchone()
                                    
                                    if not usuario_existente:
                                        # Insertar nuevo usuario
                                        conn.execute(database.text('''
                                        INSERT INTO usuario (cedula, nombre, email, contrasena, rol, activo, correo_verificado)
                                        VALUES (:cedula, :nombre, :email, :password, :rol, 1, 0)
                                        '''), {
                                            'cedula': params_est["cedula"],
                                            'nombre': f"{params_est['nombre']} {params_est['apellido']}".strip(),
                                            'email': correo_ind,
                                            'password': hashed_password,
                                            'rol': 'estudiante'
                                        })
                                        conn.commit()
                                        
                                        # Enviar correo de confirmación
                                        from database import enviar_confirmacion_registro
                                        exito_correo, mensaje_correo = enviar_confirmacion_registro(correo_ind, engine_l)
                                        
                                        if exito_correo:
                                            st.info(f"📧 Correo de confirmación enviado a {correo_ind}")
                                            st.info("📋 Datos de acceso:")
                                            st.code(f"Usuario: {correo_ind}\nContraseña: {params_est['cedula']}")
                                            st.info("El estudiante debe validar su correo para activar su cuenta")
                                        else:
                                            st.warning(f"⚠️ No se pudo enviar correo de confirmación: {mensaje_correo}")
                                            st.info("El estudiante fue registrado pero no se pudo enviar el correo")
                            except Exception as e:
                                st.warning(f"⚠️ Error creando usuario/enviando correo: {e}")
                                st.info("El estudiante fue registrado en persona pero no se pudo crear el usuario del sistema")
                    
                    if exito:
                        # Registrar auditoría
                        registrar_auditoria(
                            usuario=st.session_state.user_data.get('login'),
                            rol=obtener_rol_usuario(),
                            transaccion=transaccion_tipo,
                            tabla_afectada='persona',
                            registro_id=params_est["cedula"],
                            detalles=f"cedula:{params_est['cedula']}, nombre:{params_est['nombre']}, apellido:{params_est['apellido']}",
                            engine=engine_l
                        )
                        
                        # Limpiar session_state si estaba en modo edición
                        if 'estudiante_editar' in st.session_state:
                            del st.session_state.estudiante_editar
                        
                        mensaje_exito = "✅ Estudiante actualizado exitosamente" if estudiante_editar else "✅ Registro guardado exitosamente"
                        st.success(mensaje_exito)
                        st.rerun()  # Limpiar campos
                    else:
                        st.error(f"❌ Error al guardar: {mensaje}")

# --- MÓDULO D: GESTIÓN DE PROFESORES ---
elif modulo == "Gestión de Profesores":
    if es_admin():
        st.header("👨‍🏫 Gestión de Profesores")
        t1_prof, t2_prof, t3_prof = st.tabs(["📝 Carga Masiva", "📋 Listado de Profesores", "👤 Registro Individual"])
        
        # PROCESAR ACCIONES PENDIENTES AL INICIO DEL MÓDULO
        accion_pendiente = st.session_state.get('accion_pendiente')
        
        if accion_pendiente == 'editar_profesor':
            # Cambiar a pestaña de registro individual
            st.session_state.tab_prof_activa = 2
            st.session_state.accion_pendiente = None  # Limpiar acción
            
        elif accion_pendiente == 'eliminar_profesor':
            # Mostrar confirmación de eliminación
            profesor_id = st.session_state.get('profesor_id_seleccionado')
            nombre_profesor = st.session_state.get('nombre_prof_eliminar', '')
            
            if profesor_id:
                st.warning(f"⚠️ ¿Está seguro de eliminar al profesor '{nombre_profesor}'?")
                col_confirm, col_cancel = st.columns(2)
                
                with col_confirm:
                    if st.button("✅ Sí, Eliminar", key="confirm_eliminar_profesor"):
                        # Aquí iría la lógica de eliminación real
                        # Por ahora, mostrar mensaje de desarrollo
                        st.info("🗑️ Función de eliminación de profesores en desarrollo")
                        
                        # Limpiar estado
                        for key in ['accion_pendiente', 'profesor_id_seleccionado', 'nombre_prof_eliminar']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
                
                with col_cancel:
                    if st.button("❌ Cancelar", key="cancel_eliminar_profesor"):
                        # Limpiar estado
                        for key in ['accion_pendiente', 'profesor_id_seleccionado', 'nombre_prof_eliminar']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
        
        # Verificar si se debe cambiar a pestaña específica
        tab_prof_activa = st.session_state.get('tab_prof_activa', 0)
        if tab_prof_activa > 0 and tab_prof_activa < len([t1_prof, t2_prof, t3_prof]):
            # Forzar cambio de pestaña
            if tab_prof_activa == 1:
                t2_prof.write()
            elif tab_prof_activa == 2:
                t3_prof.write()
            tab_prof_activa = 0  # Resetear después de usar
            st.session_state.tab_prof_activa = 0
        
        with t1_prof:
            st.subheader("🛠️ Carga Masiva de Profesores")
            st.write("Importe la nómina de profesores encargados de los talleres.")
            f_doc = st.file_uploader("Subir archivo de profesores", type=['xlsx', 'csv'], key="up_prof_main")

            if f_doc:
                try:
                    if f_doc.name.endswith('.xlsx'):
                        df_f = pd.read_excel(f_doc)
                        # Limpiar nombres de columnas para Excel también
                        df_f.columns = df_f.columns.str.strip().str.lower()
                    else:
                        # Lectura directa con delimitador punto y coma y utf-8-sig para SICADFOC_01_Profesores.csv
                        try:
                            df_f = pd.read_csv(f_doc, sep=';', encoding='utf-8-sig')
                        except UnicodeDecodeError:
                            try:
                                df_f = pd.read_csv(f_doc, sep=';', encoding='latin-1')
                            except Exception:
                                # Fallback a detección automática
                                try:
                                    df_f = pd.read_csv(f_doc, sep=None, engine='python', encoding='utf-8-sig')
                                except Exception:
                                    df_f = pd.read_csv(f_doc, sep=None, engine='python', encoding='utf-8')
                        
                        # Limpiar nombres de columnas: eliminar espacios y estandarizar a minúsculas
                        df_f.columns = df_f.columns.str.strip().str.lower()
                        
                        # Verificar si todavía hay problema con columnas
                        if len(df_f.columns) == 1:
                            st.warning("🔍 Detectando separador automático...")
                            try:
                                df_f = pd.read_csv(f_doc, sep=None, engine='python', encoding='utf-8-sig')
                                df_f.columns = df_f.columns.str.strip().str.lower()
                            except Exception:
                                df_f = pd.read_csv(f_doc, sep=None, engine='python', encoding='utf-8')
                                df_f.columns = df_f.columns.str.strip().str.lower()
                        
                        if len(df_f.columns) == 1:
                            raise ValueError("No se detectaron múltiples columnas. Verifique el separador.")
                        
                except Exception as ex:
                    st.error(f"❌ Error al leer archivo: {ex}")
                    df_f = None
                    
                if df_f is not None and not df_f.empty:
                    df_limpio_prof, mapeo_prof = limpiar_columnas_profesores(df_f)

                    if df_limpio_prof is None:
                        st.error("⚠️ El archivo debe contener: cedula, nombre, apellido.")
                        st.write("**Columnas detectadas:**", list(df_f.columns))
                        if len(df_f.columns) > 1:
                            st.dataframe(df_f.head(3), use_container_width=True, hide_index=True)
                    else:
                        st.dataframe(df_limpio_prof, use_container_width=True, hide_index=True)

                        if st.button("🚀 Actualizar Base de Profesores"):
                            insertados = 0
                            duplicados = 0
                            errores = []
                            
                            for i, r_f in df_limpio_prof.iterrows():
                                try:
                                    # Extraer campos con valores por defecto para opcionales
                                    cedula_val = str(r_f['cedula']).strip()
                                    nombre_val = str(r_f['nombre']).strip().upper()
                                    apellido_val = str(r_f['apellido']).strip().upper()
                                    especialidad_val = str(r_f.get('especialidad', '')).strip().upper() if pd.notna(r_f.get('especialidad')) else None
                                    correo_val = str(r_f.get('correo', '')).strip().upper() if pd.notna(r_f.get('correo')) else None
                                    departamento_val = str(r_f.get('departamento', '')).strip().upper() if pd.notna(r_f.get('departamento')) else None
                                    
                                    exito, mensaje = insertar_profesor(
                                        cedula=cedula_val,
                                        nombre=nombre_val,
                                        apellido=apellido_val,
                                        especialidad=especialidad_val,
                                        correo=correo_val,
                                        departamento=departamento_val,
                                        engine=engine_l
                                    )
                                    # Registrar auditoría
                                    registrar_auditoria(
                                        usuario=st.session_state.user_data.get('login'),
                                        rol=obtener_rol_usuario(),
                                        transaccion='INSERT',
                                        tabla_afectada='profesor',
                                        registro_id=r_f['cedula'],
                                        detalles=f"cedula:{r_f['cedula']}, nombre:{r_f['nombre']}, apellido:{r_f['apellido']}",
                                        engine=engine_l
                                    )
                                    
                                    if exito:
                                        insertados += 1
                                    else:
                                        duplicados += 1
                                except Exception as e:
                                    errores.append(f"Fila {i+1}: {str(e)}")
                            
                            st.success(f"✅ Base actualizada. Insertados: {insertados}, existían: {duplicados}.")
                            if errores:
                                st.error(f"❌ {len(errores)} errores:")
                                for error in errores[:3]:
                                    st.write(f"• {error}")

        with t2_prof:
            st.subheader("📋 Listado de Profesores Registrados")
            
            # Obtener todos los profesores con campos completos
            data_prof = obtener_profesores(engine=engine_l)
            
            if data_prof:
                # Convertir a DataFrame y renombrar columnas con encabezados profesionales
                df_prof = pd.DataFrame(data_prof)
                
                # Renombrar columnas para encabezados profesionales
                df_prof.columns = ['ID', 'Cédula', 'Nombre', 'Apellido', 'Especialidad', 'Correo', 'Departamento']
                
                # Tabla de visualización limpia (sin botones)
                st.dataframe(df_prof, use_container_width=True, hide_index=True)
                st.caption(f"Total: {len(data_prof)} profesores registrados.")
                
                # Métricas
                col_m1, col_m2 = st.columns(2)
                col_m1.metric("👥 Total Profesores", len(data_prof))
                col_m2.metric("✅ Activos", len(data_prof))
                
                # Panel de Gestión Unificado
                if es_admin() and data_prof:
                    st.subheader("🔧 Panel de Gestión de Profesores")
                    
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            # Selectbox para elegir profesor por cédula
                            opciones_profesores = [f"{prof['cedula']} - {prof['nombre']} {prof['apellido']}" for prof in data_prof]
                            profesor_seleccionado = st.selectbox(
                                "Seleccionar Profesor:",
                                options=opciones_profesores,
                                help="Elija un profesor para gestionar"
                            )
                        
                        with col2:
                            confirmar_accion = st.checkbox("✅ Confirmar Acción", help="Marque para habilitar los botones")
                        
                        with col3:
                            st.write("")  # Espacio vacío para alineación
                    
                    if profesor_seleccionado and confirmar_accion:
                        # Extraer cédula del profesor seleccionado
                        cedula_seleccionada = profesor_seleccionado.split(" - ")[0]
                        
                        # Encontrar datos completos del profesor
                        profesor_data = next((prof for prof in data_prof if prof['cedula'] == cedula_seleccionada), None)
                        
                        if profesor_data:
                            col_edit, col_delete = st.columns(2)
                            

                            with col_edit:
                                if st.button("📝 Editar Profesor", type="primary", use_container_width=True):
                                    # Guardar ID para edición
                                    st.session_state.id_a_editar = cedula_seleccionada
                                    st.session_state.tab_index = 2  # Cambiar a pestaña Registro Individual
                                    st.rerun()
                            

                            with col_delete:
                                if st.button("🗑️ Eliminar Profesor", type="secondary", use_container_width=True):
                                    # Confirmación y eliminación
                                    st.warning(f"⚠️ ¿Está seguro de eliminar al profesor '{profesor_data['nombre']} {profesor_data['apellido']}'?")
                                    col_confirm, col_cancel = st.columns(2)
                                    
                                    with col_confirm:
                                        if st.button("✅ Sí, Eliminar", key="confirm_eliminar_profesor_final"):
                                            exito, mensaje = eliminar_profesor(cedula_seleccionada, engine=engine_l)
                                            if exito:
                                                # Registrar auditoría
                                                registrar_auditoria(
                                                    usuario=st.session_state.user_data.get('login'),
                                                    rol=obtener_rol_usuario(),
                                                    transaccion='DELETE',
                                                    tabla_afectada='profesor',
                                                    registro_id=cedula_seleccionada,
                                                    detalles=f"cedula:{cedula_seleccionada}, nombre:{profesor_data['nombre']} {profesor_data['apellido']}",
                                                    engine=engine_l
                                                )
                                                st.success("✅ Profesor eliminado exitosamente")
                                                st.rerun()
                                            else:
                                                st.error(f"❌ Error al eliminar: {mensaje}")
                                    
                                    with col_cancel:
                                        if st.button("❌ Cancelar", key="cancel_eliminar_profesor_final"):
                                            st.rerun()
                    else:
                        st.info("💡 Seleccione un profesor y confirme la acción para habilitar los botones")
            else:
                st.info("No hay profesores registrados. Cargue un archivo en la pestaña «Carga Masiva».")
        
        with t3_prof:
            st.subheader("👤 Registro Individual de Profesores")
            st.write("Ingrese los datos del profesor de forma manual.")
            
            # Verificar si hay datos para editar
            profesor_editar = st.session_state.get('profesor_editar')
            
            with st.form("form_profesor_individual"):
                col1, col2 = st.columns(2)
                with col1:
                    cedula_prof = st.text_input("Cédula*", help="Campo obligatorio",
                                             value=profesor_editar.get('cedula', '') if profesor_editar else '',
                                             disabled=bool(profesor_editar))  # Deshabilitar cédula en edición
                    nombre_prof = st.text_input("Nombre*", help="Campo obligatorio",
                                             value=profesor_editar.get('nombre', '') if profesor_editar else '')
                    especialidad_prof = st.text_input("Especialidad",
                                                     value=profesor_editar.get('especialidad', '') if profesor_editar else '')
                with col2:
                    apellido_prof = st.text_input("Apellido*",
                                                 value=profesor_editar.get('apellido', '') if profesor_editar else '')
                    correo_prof = st.text_input("Correo Electrónico", help="Formato: usuario@dominio.com",
                                                 value=profesor_editar.get('correo', '') if profesor_editar else '')
                    departamento_prof = st.text_input("Departamento",
                                                    value=profesor_editar.get('departamento', '') if profesor_editar else '')
                
                btn_guardar_prof = st.form_submit_button("💾 Guardar Profesor", type="primary")
                
                if btn_guardar_prof:
                    # Validaciones
                    if not cedula_prof.strip():
                        st.error("⚠️ La Cédula es un campo obligatorio.")
                    elif not nombre_prof.strip():
                        st.error("⚠️ El Nombre es un campo obligatorio.")
                    elif not apellido_prof.strip():
                        st.error("⚠️ El Apellido es un campo obligatorio.")
                    elif correo_prof and "@" not in correo_prof:
                        st.error("⚠️ El correo electrónico debe tener un formato válido (contener @).")
                    else:
                        # Normalizar datos a mayúsculas
                        params_prof = {
                            "cedula": cedula_prof.strip().upper(),
                            "nombre": nombre_prof.strip().upper(),
                            "apellido": apellido_prof.strip().upper(),
                            "especialidad": especialidad_prof.strip().upper() if especialidad_prof else "",
                            "correo": correo_prof.strip().upper() if correo_prof else "",
                            "departamento": departamento_prof.strip().upper() if departamento_prof else ""
                        }
                        
                        # Insertar profesor usando la función existente
                        exito, mensaje = insertar_profesor(
                            cedula=params_prof["cedula"],
                            nombre=params_prof["nombre"],
                            apellido=params_prof["apellido"],
                            especialidad=params_prof["especialidad"],
                            correo=params_prof["correo"],
                            departamento=params_prof["departamento"],
                            engine=engine_l
                        )
                        
                        if exito:
                            # Si el profesor se registró exitosamente y tiene correo, enviar confirmación
                            if correo_prof:
                                try:
                                    # Crear usuario en tabla usuario con correo_verificado = 0
                                    import hashlib
                                    password_temp = params_prof["cedula"]  # Usar cédula como contraseña temporal
                                    hashed_password = hashlib.sha256(password_temp.encode()).hexdigest()
                                    
                                    with engine_l.connect() as conn:
                                        # Verificar si ya existe usuario
                                        verificar_usuario = conn.execute(database.text('SELECT login FROM usuario WHERE login = :email'), 
                                                                       {'email': correo_prof})
                                        usuario_existente = verificar_usuario.fetchone()
                                        
                                        if not usuario_existente:
                                            # Insertar nuevo usuario
                                            conn.execute(database.text('''
                                            INSERT INTO usuario (cedula, nombre, email, contrasena, rol, activo, correo_verificado)
                                            VALUES (:cedula, :nombre, :email, :password, :rol, 1, 0)
                                            '''), {
                                                'cedula': params_prof["cedula"],
                                                'nombre': f"{params_prof['nombre']} {params_prof['apellido']}".strip(),
                                                'email': correo_prof,
                                                'password': hashed_password,
                                                'rol': 'profesor'
                                            })
                                            conn.commit()
                                            
                                            # Enviar correo de confirmación
                                            from database import enviar_confirmacion_registro
                                            exito_correo, mensaje_correo = enviar_confirmacion_registro(correo_prof, engine_l)
                                            
                                            if exito_correo:
                                                st.info(f"📧 Correo de confirmación enviado a {correo_prof}")
                                                st.info("📋 Datos de acceso:")
                                                st.code(f"Usuario: {correo_prof}\nContraseña: {params_prof['cedula']}")
                                                st.info("El profesor debe validar su correo para activar su cuenta")
                                            else:
                                                st.warning(f"⚠️ No se pudo enviar correo de confirmación: {mensaje_correo}")
                                                st.info("El profesor fue registrado pero no se pudo enviar el correo")
                                except Exception as e:
                                    st.warning(f"⚠️ Error creando usuario/enviando correo: {e}")
                                    st.info("El profesor fue registrado en persona pero no se pudo crear el usuario del sistema")
                            
                            # Registrar auditoría
                            registrar_auditoria(
                                usuario=st.session_state.user_data.get('login'),
                                rol=obtener_rol_usuario(),
                                transaccion='REGISTRO_MANUAL_PROFESOR',
                                tabla_afectada='profesor',
                                registro_id=params_prof["cedula"],
                                detalles=f"cedula:{params_prof['cedula']}, nombre:{params_prof['nombre']}, apellido:{params_prof['apellido']}, especialidad:{params_prof['especialidad']}",
                                engine=engine_l
                            )
                            st.success("✅ Registro guardado exitosamente")
                            st.rerun()  # Limpiar campos
                        else:
                            st.error(f"❌ Error al guardar: {mensaje}")
    
    else:
        st.header("👨‍🏫 Gestión de Profesores")
        mostrar_mensaje_restringido()

# --- MÓDULO D: GESTIÓN DE FORMACIÓN COMPLEMENTARIA ---
elif modulo == "Gestión de Formación Complementaria":
    st.header("🎓 Gestión de Formación Complementaria")
    
    # Matriz de permisos según rol
    rol_actual = obtener_rol_usuario()
    
    # Definir columnas al inicio para evitar UnboundLocalError
    col1, col2, col3 = st.columns(3)
    
    # PROCESAR ACCIONES PENDIENTES AL INICIO DEL MÓDULO
    accion_pendiente = st.session_state.get('accion_pendiente')
    
    if accion_pendiente == 'consultar_formacion':
        # Cargar modo consulta
        st.session_state.modo_edicion = False
        st.session_state.tab_activa = 1
        st.session_state.accion_pendiente = None  # Limpiar acción
        
    elif accion_pendiente == 'editar_formacion':
        # Cargar modo edición
        st.session_state.modo_edicion = True
        st.session_state.tab_activa = 1
        st.session_state.accion_pendiente = None  # Limpiar acción
        
    elif accion_pendiente == 'eliminar_formacion':
        # Mostrar confirmación de eliminación
        formacion_id = st.session_state.get('formacion_id_seleccionada')
        nombre_formacion = st.session_state.get('nombre_formacion_eliminar', '')
        
        if formacion_id:
            st.warning(f"⚠️ ¿Está seguro de eliminar la formación '{nombre_formacion}'?")
            col_confirm, col_cancel = st.columns(2)
            
            with col_confirm:
                if st.button("✅ Sí, Eliminar", key="confirm_eliminar_formacion"):
                    exito, mensaje = eliminar_formacion(formacion_id, engine=engine_l)
                    if exito:
                        # Registrar auditoría
                        registrar_auditoria(
                            usuario=st.session_state.user_data.get('login'),
                            rol=obtener_rol_usuario(),
                            transaccion='DELETE',
                            tabla_afectada='formacion_complementaria',
                            registro_id=formacion_id,
                            detalles=f"codigo:{nombre_formacion}",
                            engine=engine_l
                        )
                        st.success("✅ Formación eliminada exitosamente")
                        st.rerun()
                    else:
                        st.error(f"❌ Error al eliminar: {mensaje}")
                        
                        # Limpiar estado
                        for key in ['accion_pendiente', 'formacion_id_seleccionada', 'nombre_formacion_eliminar']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
            
            with col_cancel:
                if st.button("❌ Cancelar", key="cancel_eliminar_formacion"):
                    # Limpiar estado
                    for key in ['accion_pendiente', 'formacion_id_seleccionada', 'nombre_formacion_eliminar']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
    
    # Verificar si se debe cambiar a pestaña específica
    tab_activa = st.session_state.get('tab_activa', 0)
    
    if rol_actual == 'admin':
        # ADMIN: Acceso total
        tabs_formacion = st.tabs(["📋 Listado", "🔧 Gestión Individual", "📤 Carga Masiva"])
        # Usar tab_activa para cambiar automáticamente
        if tab_activa > 0 and tab_activa < len(tabs_formacion):
            tabs_formacion[tab_activa].write()  # Forzar cambio de pestaña
            tab_activa = 0  # Resetear después de usar
            st.session_state.tab_activa = 0
    elif rol_actual == 'profesor':
        # PROFESOR: Crear, Consultar, Editar (no eliminar)
        tabs_formacion = st.tabs(["📋 Listado", "🔧 Gestión Individual"])
        # Usar tab_activa para cambiar automáticamente
        if tab_activa > 0 and tab_activa < len(tabs_formacion):
            tabs_formacion[tab_activa].write()  # Forzar cambio de pestaña
            tab_activa = 0  # Resetear después de usar
            st.session_state.tab_activa = 0
    else:
        # ESTUDIANTE: Consultar y Crear (solicitud)
        tabs_formacion = st.tabs(["📋 Listado", "📝 Solicitar Taller"])
    
    # --- PESTAÑA 1: LISTADO ---
    with tabs_formacion[0]:
        st.subheader("📋 Listado de Formaciones Complementarias")
        
        # Filtros de búsqueda
        with st.expander("🔍 Filtros de Búsqueda"):
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                filtro_codigo = st.text_input("Código de Formación")
            with col_f2:
                filtro_tipo = st.text_input("Tipo de Taller")
            with col_f3:
                filtro_estado = st.selectbox("Estado", ["Todos", "Activo", "Inactivo", "Finalizado"])
            
            if st.button("🔍 Aplicar Filtros"):
                st.rerun()
        
        # Obtener datos con filtros
        formaciones = listar_formaciones(
            filtro_codigo=filtro_codigo if filtro_codigo else None,
            filtro_tipo=filtro_tipo if filtro_tipo else None,
            filtro_estado=filtro_estado if filtro_estado != "Todos" else None,
            engine=engine_l
        )
        
        if formaciones:
            # Convertir a DataFrame
            df_formaciones = pd.DataFrame(formaciones)
            
            # Métricas
            if es_admin_o_profesor():
                col_m1, col_m2, col_m3 = st.columns(3)
                total_formaciones = len(formaciones)
                activas = len([f for f in formaciones if f.get('estado_registro') == 'Activo'])
                total_inscritos = sum([f.get('inscritos', 0) for f in formaciones])
                
                col_m1.metric("🎓 Total Formaciones", total_formaciones)
                col_m2.metric("✅ Activas", activas)
                col_m3.metric("👥 Total Inscritos", total_inscritos)
            
            # Tabla de visualización limpia (sin botones)
            df_vista = df_formaciones[['codigo_formacion', 'tipo_taller', 'nombre_taller', 'nombre_profesor', 'apellido_profesor', 'fecha_inicio', 'fecha_fin', 'cupos', 'inscritos', 'estado_registro']]
            df_vista.columns = ['Código', 'Tipo', 'Nombre', 'Profesor', 'Apellido', 'Inicio', 'Fin', 'Cupos', 'Inscritos', 'Estado']
            st.dataframe(df_vista, use_container_width=True, hide_index=True)
            
            # Panel de Gestión Unificado
            if rol_actual in ['admin', 'profesor']:
                st.subheader("🔧 Panel de Gestión de Formaciones")
                
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        # Selectbox para elegir formación por código
                        opciones_formaciones = [f"{f['codigo_formacion']} - {f['nombre_taller']}" for f in formaciones]
                        formacion_seleccionada = st.selectbox(
                            "Seleccionar Formación:",
                            options=opciones_formaciones,
                            help="Elija una formación para gestionar"
                        )
                    
                    with col2:
                        confirmar_accion = st.checkbox("✅ Confirmar Acción", help="Marque para habilitar los botones")
                    
                    with col3:
                        st.write("")  # Espacio vacío para alineación
                
                if formacion_seleccionada and confirmar_accion:
                    # Extraer código de la formación seleccionada
                    codigo_seleccionado = formacion_seleccionada.split(" - ")[0]
                    
                    # Encontrar datos completos de la formación
                    formacion_data = next((f for f in formaciones if f['codigo_formacion'] == codigo_seleccionado), None)
                    
                    if formacion_data:
                        col_consult, col_edit, col_delete = st.columns(3)
                        
                        with col_consult:
                            if st.button("🔍 Consultar", type="secondary", use_container_width=True):
                                # Cargar datos para consulta
                                st.session_state.formacion_editar = formacion_data
                                st.session_state.modo_edicion = False
                                st.session_state.tab_activa = 1  # Cambiar a pestaña Gestión Individual
                                st.rerun()
                        
                        with col_edit:
                            if st.button("📝 Editar", type="primary", use_container_width=True):
                                # Guardar ID para edición
                                st.session_state.id_a_editar = formacion_data['id_formacion']
                                st.session_state.tab_index = 1  # Cambiar a pestaña Gestión Individual
                                st.rerun()
                        
                        with col_delete:
                            if rol_actual == 'admin':
                                if st.button("🗑️ Eliminar", type="secondary", use_container_width=True):
                                    # Confirmación y eliminación
                                    st.warning(f"⚠️ ¿Está seguro de eliminar la formación '{formacion_data['nombre_taller']}'?")
                                    col_confirm, col_cancel = st.columns(2)
                                    
                                    with col_confirm:
                                        if st.button("✅ Sí, Eliminar", key="confirm_eliminar_formacion_final"):
                                            exito, mensaje = eliminar_formacion(formacion_data['id_formacion'], engine=engine_l)
                                            if exito:
                                                # Registrar auditoría
                                                registrar_auditoria(
                                                    usuario=st.session_state.user_data.get('login'),
                                                    rol=obtener_rol_usuario(),
                                                    transaccion='DELETE',
                                                    tabla_afectada='formacion_complementaria',
                                                    registro_id=formacion_data['id_formacion'],
                                                    detalles=f"codigo:{formacion_data['codigo_formacion']}",
                                                    engine=engine_l
                                                )
                                                st.success("✅ Formación eliminada exitosamente")
                                                st.rerun()
                                            else:
                                                st.error(f"❌ Error al eliminar: {mensaje}")
                                    
                                    with col_cancel:
                                        if st.button("❌ Cancelar", key="cancel_eliminar_formacion_final"):
                                            st.rerun()
                    else:
                        st.info("💡 Seleccione una formación y confirme la acción para habilitar los botones")
            else:
                # ESTUDIANTE: Solo vista y solicitud
                df_vista_estudiante = df_formaciones[['codigo_formacion', 'tipo_taller', 'nombre_taller', 'nombre_profesor', 'apellido_profesor', 'fecha_inicio', 'fecha_fin', 'cupos', 'inscritos', 'estado_registro']]
                df_vista_estudiante.columns = ['Código', 'Tipo', 'Nombre', 'Profesor', 'Apellido', 'Inicio', 'Fin', 'Cupos', 'Inscritos', 'Estado']
                st.dataframe(df_vista_estudiante, use_container_width=True, hide_index=True)
                
                # Botón de inscripción
                st.subheader("📝 Solicitar Inscripción a Taller")
                selected_taller = st.selectbox(
                    "Seleccionar Taller para Inscribirse:",
                    options=[f"{f['id_formacion']} - {f['codigo_formacion']} - {f['nombre_taller']}" for f in formaciones if f.get('estado_registro') == 'Activo'],
                    format_func=lambda x: x.split(" - ", 2)[2] if " - " in x else x
                )
                
                if selected_taller and st.button("📝 Solicitar Inscripción"):
                    taller_id = int(selected_taller.split(" - ")[0])
                    # Aquí iría la lógica de inscripción del estudiante
                    st.success("✅ Solicitud de inscripción enviada (pendiente de aprobación)")
        
        else:
            st.info("📋 No hay formaciones complementarias registradas.")
    
    # --- PESTAÑA 2: GESTIÓN INDIVIDUAL ---
    if len(tabs_formacion) > 1:
        with tabs_formacion[1]:
            if rol_actual in ['admin', 'profesor']:
                st.subheader("🔧 Gestión Individual de Formaciones")
                
                # Verificar si hay datos para editar/consultar
                if 'formacion_editar' in st.session_state and st.session_state.formacion_editar:
                    formacion_data = st.session_state.formacion_editar
                    modo_edicion = st.session_state.get('modo_edicion', False)
                    
                    st.write(f"**{'📝 Editando' if modo_edicion else '🔍 Consultando'}:** {formacion_data['nombre_taller']}")
                else:
                    formacion_data = None
                    modo_edicion = True  # Nuevo registro
                    st.write("**📝 Nueva Formación Complementaria**")
                
                with st.form("form_formacion_individual"):
                    # Definir columnas al inicio del formulario
                    col1, col2 = st.columns(2)
                    col3, col4 = st.columns(2)
                    
                    with col1:
                        codigo_form = st.text_input(
                            "Código de Formación*", 
                            value=formacion_data['codigo_formacion'] if formacion_data else "",
                            disabled=not modo_edicion
                        )
                        tipo_taller = st.text_input(
                            "Tipo de Taller*", 
                            value=formacion_data['tipo_taller'] if formacion_data else "",
                            disabled=not modo_edicion
                        )
                        nombre_taller = st.text_input(
                            "Nombre del Taller*", 
                            value=formacion_data['nombre_taller'] if formacion_data else "",
                            disabled=not modo_edicion
                        )
                    with col2:
                        # Obtener lista de profesores
                        profesores = ejecutar_query("SELECT id_profesor, cedula, nombre, apellido, especialidad, correo, departamento FROM public.profesor ORDER BY apellido, nombre", engine=engine_l)
                        if profesores:
                            opciones_profesores = [f"{p['cedula']} - {p['nombre']} {p['apellido']}" for p in profesores]
                            profesor_actual = f"{formacion_data['cedula_profesor']} - {formacion_data['nombre_profesor']} {formacion_data['apellido_profesor']}" if formacion_data else ""
                            profesor_sel = st.selectbox(
                                "Profesor*", 
                                options=opciones_profesores,
                                index=opciones_profesores.index(profesor_actual) if profesor_actual in opciones_profesores else 0,
                                disabled=not modo_edicion
                            )
                        else:
                            st.warning("⚠️ No hay profesores registrados. Registre profesores primero.")
                            profesor_sel = ""
                        
                        cupos = st.number_input(
                            "Cupos", 
                            min_value=1, 
                            max_value=100, 
                            value=formacion_data.get('cupos', 30) if formacion_data else 30,
                            disabled=not modo_edicion
                        )
                        estado_reg = st.selectbox(
                            "Estado de Registro", 
                            ["Activo", "Inactivo", "Finalizado"],
                            index=["Activo", "Inactivo", "Finalizado"].index(formacion_data['estado_registro']) if formacion_data else 0,
                            disabled=not modo_edicion
                        )
                    
                    with col3:
                        fecha_inicio = st.date_input(
                            "Fecha de Inicio*", 
                            value=pd.to_datetime(formacion_data['fecha_inicio']).date() if formacion_data else datetime.now().date(),
                            disabled=not modo_edicion
                        )
                    with col4:
                        fecha_fin = st.date_input(
                            "Fecha de Fin*", 
                            value=pd.to_datetime(formacion_data['fecha_fin']).date() if formacion_data else datetime.now().date(),
                            disabled=not modo_edicion
                        )
                    
                    observaciones = st.text_area(
                        "Observaciones", 
                        value=formacion_data.get('observaciones', '') if formacion_data else "",
                        disabled=not modo_edicion
                    )
                    
                    # Botones según modo
                    if modo_edicion:
                        btn_guardar = st.form_submit_button("💾 Guardar Formación", type="primary")
                    else:
                        btn_volver = st.form_submit_button("🔙 Volver a Edición")
                    
                    if modo_edicion and btn_guardar:
                        # Validaciones
                        if not codigo_form.strip() or not tipo_taller.strip() or not nombre_taller.strip():
                            st.error("⚠️ Complete los campos obligatorios: Código, Tipo y Nombre del Taller")
                        elif not profesor_sel:
                            st.error("⚠️ Seleccione un profesor")
                        elif fecha_fin < fecha_inicio:
                            st.error("⚠️ La fecha de fin debe ser posterior a la fecha de inicio")
                        else:
                            # Extraer cédula del profesor seleccionado
                            cedula_profesor = profesor_sel.split(" - ")[0]
                            
                            # Insertar o actualizar formación
                            exito, resultado = insertar_formacion(
                                codigo_formacion=codigo_form.strip(),
                                tipo_taller=tipo_taller.strip(),
                                nombre_taller=nombre_taller.strip(),
                                cedula_profesor=cedula_profesor,
                                fecha_inicio=fecha_inicio,
                                fecha_fin=fecha_fin,
                                cupos=cupos,
                                estado_registro=estado_reg,
                                observaciones=observaciones.strip() if observaciones else None,
                                engine=engine_l
                            )
                            
                            if exito:
                                # Registrar auditoría
                                accion = 'UPDATE' if formacion_data else 'INSERT'
                                registrar_auditoria(
                                    usuario=st.session_state.user_data.get('login'),
                                    rol=obtener_rol_usuario(),
                                    transaccion=accion,
                                    tabla_afectada='formacion_complementaria',
                                    registro_id=resultado,
                                    detalles=f"codigo:{codigo_form}, nombre:{nombre_taller}, profesor:{cedula_profesor}",
                                    engine=engine_l
                                )
                                st.success("✅ Formación guardada exitosamente")
                                # Limpiar sesión
                                if 'formacion_editar' in st.session_state:
                                    del st.session_state.formacion_editar
                                if 'modo_edicion' in st.session_state:
                                    del st.session_state.modo_edicion
                                st.rerun()
                            else:
                                st.error(f"❌ Error al guardar: {resultado}")
                    
                    elif not modo_edicion and btn_volver:
                        # Volver al modo edición
                        st.session_state.modo_edicion = True
                        st.rerun()
            
            elif rol_actual == 'estudiante':
                st.subheader("📝 Solicitar Taller")
                st.write("Complete el formulario para solicitar su inscripción en un taller.")
                
                # Obtener formaciones activas
                formaciones_activas = listar_formaciones(filtro_estado='Activo', engine=engine_l)
                
                if formaciones_activas:
                    with st.form("form_solicitud_taller"):
                        # Selección de taller
                        opciones_talleres = [f"{f['id_formacion']} - {f['codigo_formacion']} - {f['nombre_taller']}" for f in formaciones_activas]
                        taller_sel = st.selectbox("Seleccione el Taller*", options=opciones_talleres)
                        
                        observaciones_solicitud = st.text_area("Observaciones (opcional)")
                        
                        btn_solicitar = st.form_submit_button("📝 Enviar Solicitud", type="primary")
                        
                        if btn_solicitar:
                            taller_id = int(taller_sel.split(" - ")[0])
                            # Aquí iría la lógica de inscripción
                            st.success("✅ Solicitud enviada correctamente. Pendiente de aprobación.")
                else:
                    st.info("📋 No hay talleres activos disponibles para inscripción.")
    
    # --- PESTAÑA 3: CARGA MASIVA (solo admin) ---
    if len(tabs_formacion) > 2 and rol_actual == 'admin':
        with tabs_formacion[2]:
            st.subheader("📤 Carga Masiva de Formaciones")
            st.write("Importe formaciones complementarias desde archivo CSV/Excel")
            
            file_formaciones = st.file_uploader("Subir archivo de formaciones", type=['xlsx', 'csv'])
            
            if file_formaciones:
                try:
                    if file_formaciones.name.endswith('.xlsx'):
                        df_form = pd.read_excel(file_formaciones)
                    else:
                        df_form = pd.read_csv(file_formaciones, encoding='utf-8-sig')
                    
                    # Validar columnas requeridas
                    columnas_requeridas = ['codigo_formacion', 'tipo_taller', 'nombre_taller', 'cedula_profesor', 'fecha_inicio', 'fecha_fin']
                    columnas_faltantes = [col for col in columnas_requeridas if col not in df_form.columns]
                    
                    if columnas_faltantes:
                        st.error(f"⚠️ Columnas faltantes: {', '.join(columnas_faltantes)}")
                        st.info("💡 Columnas requeridas: " + ", ".join(columnas_requeridas))
                    else:
                        st.dataframe(df_form.head(), use_container_width=True, hide_index=True)
                        
                        if st.button("🚀 Procesar Carga Masiva"):
                            procesados = 0
                            errores = []
                            
                            for i, row in df_form.iterrows():
                                try:
                                    exito, resultado = insertar_formacion(
                                        codigo_formacion=str(row['codigo_formacion']),
                                        tipo_taller=str(row['tipo_taller']),
                                        nombre_taller=str(row['nombre_taller']),
                                        cedula_profesor=str(row['cedula_profesor']),
                                        fecha_inicio=pd.to_datetime(row['fecha_inicio']).date(),
                                        fecha_fin=pd.to_datetime(row['fecha_fin']).date(),
                                        cupos=int(row.get('cupos', 30)),
                                        estado_registro=str(row.get('estado_registro', 'Activo')),
                                        observaciones=str(row.get('observaciones', '')) if pd.notna(row.get('observaciones')) else None,
                                        engine=engine_l
                                    )
                                    
                                    if exito:
                                        procesados += 1
                                    else:
                                        errores.append(f"Fila {i+1}: {resultado}")
                                except Exception as e:
                                    errores.append(f"Fila {i+1}: {str(e)}")
                            
                            st.success(f"✅ {procesados} formaciones procesadas exitosamente")
                            if errores:
                                st.error(f"❌ {len(errores)} errores encontrados")
                                with st.expander("Ver errores"):
                                    for error in errores[:10]:
                                        st.write(f"• {error}")
                
                except Exception as e:
                    st.error(f"❌ Error al procesar archivo: {str(e)}")

# --- MÓDULO E: REPORTES ---
elif modulo == "Reportes":
    if es_admin_o_profesor():
        st.header("📊 Reportes del Sistema")
        tabs_reportes = st.tabs(["👥 Usuarios", "🎓 Estudiantes", "👨‍🏫 Profesores", "🔍 Log de Transacciones"])
        
        with tabs_reportes[0]:
            st.subheader("👥 Reporte de Usuarios del Sistema")
            q_usuarios = """
                SELECT login, email, rol, activo, 
                       CASE WHEN activo THEN 'Sí' ELSE 'No' END as estado
                FROM public.usuario 
                ORDER BY rol, login
            """
            data_usuarios = ejecutar_query(q_usuarios, engine=engine_l)
            
            if data_usuarios:
                df_usuarios = pd.DataFrame(data_usuarios)
                st.dataframe(df_usuarios, use_container_width=True, hide_index=True)
                
                # Métricas
                col_m1, col_m2, col_m3 = st.columns(3)
                total_usuarios = len(data_usuarios)
                usuarios_activos = len([u for u in data_usuarios if u.get('activo')])
                admins = len([u for u in data_usuarios if u.get('rol') == 'admin'])
                
                col_m1.metric("👥 Total Usuarios", total_usuarios)
                col_m2.metric("✅ Activos", usuarios_activos)
                col_m3.metric("🔑 Administradores", admins)
            else:
                st.info("No hay usuarios registrados en el sistema.")
        
        with tabs_reportes[1]:
            st.subheader("🎓 Reporte de Estudiantes")
            q_estudiantes_reporte = """
                SELECT cedula as "Cédula", apellido as "Apellido", nombre as "Nombre",
                       genero as "Género", telefono as "Teléfono", carrera as "Carrera", semestre as "Semestre"
                FROM public.persona 
                WHERE cedula IS NOT NULL AND nombre IS NOT NULL
                ORDER BY apellido, nombre
            """
            data_estudiantes_reporte = ejecutar_query(q_estudiantes_reporte, engine=engine_l)
            
            if data_estudiantes_reporte:
                df_est_rep = pd.DataFrame(data_estudiantes_reporte)
                st.dataframe(df_est_rep, use_container_width=True, hide_index=True)
                
                # Métricas
                col_m1, col_m2, col_m3 = st.columns(3)
                total_est = len(data_estudiantes_reporte)
                
                # Conteo mejorado de género (insensible a mayúsculas y múltiples formatos)
                masculino = 0
                femenino = 0
                no_definido = 0
                
                for est in data_estudiantes_reporte:
                    gen = str(est.get('Género', '')).strip().upper()
                    if gen in ['M', 'MASCULINO', 'MALE']:
                        masculino += 1
                    elif gen in ['F', 'FEMENINO', 'FEMALE']:
                        femenino += 1
                    else:
                        no_definido += 1
                
                col_m1.metric("🎓 Total Estudiantes", total_est)
                col_m2.metric("♂️ Masculino", masculino)
                col_m3.metric("♀️ Femenino", femenino)
                
                # Mostrar adicionalmente los no definidos si existen
                if no_definido > 0:
                    st.caption(f"📊 Género no definido: {no_definido} estudiante(s)")
            else:
                st.info("No hay estudiantes registrados.")
        
        with tabs_reportes[2]:
            st.subheader("👨‍🏫 Reporte de Profesores")
            q_profesores_reporte = """
                SELECT id_profesor as "ID", cedula as "Cédula", nombre as "Nombre", apellido as "Apellido", 
                       especialidad as "Especialidad", correo as "Correo", departamento as "Departamento"
                FROM public.profesor 
                ORDER BY apellido, nombre
            """
            data_profesores_reporte = ejecutar_query(q_profesores_reporte, engine=engine_l)
            
            if data_profesores_reporte:
                df_prof_rep = pd.DataFrame(data_profesores_reporte)
                st.dataframe(df_prof_rep, use_container_width=True, hide_index=True)
                
                # Métricas
                col_m1, col_m2 = st.columns(2)
                total_prof = len(data_profesores_reporte)
                col_m1.metric("👨‍🏫 Total Profesores", total_prof)
                col_m2.metric("✅ Disponibles", total_prof)
            else:
                st.info("No hay profesores registrados.")
        
        with tabs_reportes[3]:
            st.subheader("🔍 Log de Transacciones (Auditoría)")
            
            # Filtros de auditoría
            with st.expander("🔍 Filtros de Búsqueda"):
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    filtro_usuario = st.text_input("Usuario")
                    filtro_rol = st.selectbox("Rol", ["Todos", "admin", "profesor", "estudiante"])
                with col_f2:
                    filtro_accion = st.selectbox("Acción", ["Todas", "INSERT", "UPDATE", "DELETE", "LOGIN", "REGISTRO_MANUAL_ESTUDIANTE", "REGISTRO_MANUAL_PROFESOR"])
                    filtro_fecha_inicio = st.date_input("Desde", datetime.now().replace(day=1))
                with col_f3:
                    filtro_fecha_fin = st.date_input("Hasta", datetime.now())
                
                if st.button("🔍 Aplicar Filtros", key="filtros_reportes"):
                    st.rerun()
            
            # Obtener datos de auditoría
            datos_auditoria_reportes = obtener_auditoria(
                filtro_usuario=filtro_usuario if filtro_usuario else None,
                filtro_rol=filtro_rol if filtro_rol != "Todos" else None,
                filtro_transaccion=filtro_accion if filtro_accion != "Todas" else None,
                fecha_inicio=filtro_fecha_inicio,
                fecha_fin=filtro_fecha_fin,
                engine=engine_l
            )
            
            if datos_auditoria_reportes:
                df_audit = pd.DataFrame(datos_auditoria_reportes)
                st.dataframe(df_audit, use_container_width=True, hide_index=True)
                st.caption(f"Total: {len(datos_auditoria_reportes)} registros de auditoría.")
                
                # Métricas de auditoría
                col_m1, col_m2, col_m3 = st.columns(3)
                transacciones_hoy = len([a for a in datos_auditoria_reportes if a.get('fecha', '').date() == datetime.now().date()])
                por_tipo = {}
                for a in datos_auditoria_reportes:
                    tipo = a.get('transaccion', 'OTRO')
                    por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
                
                col_m1.metric("📊 Total Logs", len(datos_auditoria_reportes))
                col_m2.metric("📅 Hoy", transacciones_hoy)
                col_m3.metric("🔄 INSERT/UPDATE", por_tipo.get('INSERT', 0) + por_tipo.get('UPDATE', 0))
            else:
                st.info("No se encontraron registros de auditoría con los filtros seleccionados.")
    
    else:
        st.header("📊 Reportes")
        mostrar_mensaje_restringido()

# --- MÓDULO F: CONFIGURACIÓN ---
elif modulo == "Configuración":
    if es_admin_o_super_admin():
        st.header(" Configuración del Sistema")
        st.write("Parámetros del servidor de correo electrónico")
        
        # Obtener configuración actual
        config_actual = obtener_config_correo(engine_l)
        if config_actual is None:
            config_actual = {}
        
        with st.form("config_form"):
            st.subheader(" Configuración SMTP")
            
            col1, col2 = st.columns(2)
            with col1:
                smtp_server = st.text_input("Servidor SMTP", value=config_actual.get('servidor', ''))
                smtp_port = st.text_input("Puerto", value=config_actual.get('puerto', '587'))
                smtp_user = st.text_input("Usuario SMTP", value=config_actual.get('usuario', ''))
            with col2:
                smtp_password = st.text_input("Contraseña SMTP", value=config_actual.get('contrasena', ''), type="password")
                smtp_use_tls = st.checkbox("Usar TLS", value=config_actual.get('usar_tls', True))
            
            btn_guardar_config = st.form_submit_button("💾 Guardar Configuración", type="primary")
            
            if btn_guardar_config:
                if smtp_server and smtp_port and smtp_user:
                    # Guardar configuración
                    exito = guardar_config_correo(
                        servidor=smtp_server,
                        puerto=smtp_port,
                        usuario=smtp_user,
                        contrasena=smtp_password,
                        usar_tls=smtp_use_tls,
                        engine=engine_l
                    )
                    
                    if exito:
                        # Registrar auditoría
                        registrar_auditoria(
                            usuario=st.session_state.user_data.get('login'),
                            rol=obtener_rol_usuario(),
                            transaccion='UPDATE',
                            tabla_afectada='config_correo',
                            detalles=f"servidor:{smtp_server}, puerto:{smtp_port}, usuario:{smtp_user}",
                            engine=engine_l
                        )
                        st.success("✅ Configuración guardada exitosamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al guardar la configuración")
                else:
                    st.error("⚠️ Complete los campos obligatorios: Servidor, Puerto y Usuario")
        
        # Sección de sincronización (solo en entorno local)
        st.divider()
        st.subheader("🔄 Sincronización de Datos")
        
        # Verificar si estamos en entorno local
        if verificar_entorno_local():
            st.write("📍 Entorno detectado: **Local**")
            
            # Mostrar información de base de datos espejo
            espejo_info = get_info_espejo()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🪞 Base de Datos Espejo (Shadow DB):**")
                st.code(f"""
Database: {espejo_info['espejo']['database']}
Host: {espejo_info['espejo']['host']}
Port: {espejo_info['espejo']['port']}
User: {espejo_info['espejo']['user']}
Modo Desarrollo: {espejo_info['espejo']['modo_desarrollo']}
                """)
            
            with col2:
                st.write("**☁️ Base de Datos en la Nube:**")
                render_url = os.environ.get("RENDER_EXTERNAL_URL", "No configurada")
                st.code(f"""
URL: {render_url[:50] + '...' if len(render_url) > 50 else render_url}
Estado: {'Configurada' if render_url != 'No configurada' else 'No configurada'}
                """)
            
            st.info("💡 Esta sección permite sincronizar datos desde el espejo local (foc26_espejo) hacia la nube (Render).")
            
            # Advertencia de seguridad
            st.warning("⚠️ **ADVERTENCIA DE SINCRONIZACIÓN OVERWRITE**")
            st.write("""
            Esta operación **SOBREESCRIBIRÁ COMPLETAMENTE** la base de datos de producción en la nube 
            con los datos del espejo local (foc26_espejo).
            
            🔄 **Lógica de Sincronización "Overwrite":**
            1. **Leer datos** desde foc26_espejo (base de datos espejo)
            2. **Limpiar tablas** en Render (DELETE FROM table)
            3. **Insertar datos** del espejo en la nube
            
            ⚠️ **ESTA ES UNA OPERACIÓN DESTRUCTIVA**
            """)
            
            # Botón de sincronización OVERWRITE
            if st.button("🔄 Sincronizar Espejo Local -> Nube (Render)", type="primary", use_container_width=True):
                # Mostrar diálogo de confirmación
                if 'confirmar_sincro_overwrite' not in st.session_state:
                    st.session_state.confirmar_sincro_overwrite = False
                
                if not st.session_state.confirmar_sincro_overwrite:
                    st.error("🛡️ **CONFIRMACIÓN REQUERIDA - OVERWRITE**")
                    st.warning("""
                    ¿Estás seguro de SOBREESCRIBIR la base de datos de producción con el espejo local?
                    
                    Esta acción OVERWRITE:
                    ✅ Leerá datos desde foc26_espejo
                    ✅ Limpiará completamente las tablas en Render
                    ✅ Insertará los datos del espejo en la nube
                    ⚠️ **PERDERÁ TODOS LOS DATOS EXISTENTES EN RENDER**
                    
                    Presiona el botón nuevamente para confirmar el OVERWRITE.
                    """)
                    
                    # Botón de confirmación
                    if st.button("🔓 Sí, confirmar OVERWRITE", type="secondary", use_container_width=True):
                        st.session_state.confirmar_sincro_overwrite = True
                        st.rerun()
                else:
                    # Ejecutar sincronización OVERWRITE
                    with st.spinner("🔄 Ejecutando sincronización OVERWRITE..."):
                        try:
                            # 1. Validar configuración inicial
                            import os
                            render_url = os.environ.get("RENDER_EXTERNAL_URL")
                            if not render_url or render_url.strip() == "":
                                st.error("❌ RENDER_EXTERNAL_URL no configurada")
                                st.error("""
                                Para sincronizar con la nube:
                                
                                1. Abra el archivo .env en la raíz del proyecto
                                2. Configure la variable:
                                   RENDER_EXTERNAL_URL=postgresql://usuario:password@host:puerto/database?sslmode=require
                                3. Use la "External Database URL" del panel de Render
                                4. Guarde el archivo y reinicie la aplicación
                                """)
                                st.session_state.confirmar_sincro_overwrite = False
                                st.stop()
                            
                            # 2. Probar conexión a la nube antes de sincronizar
                            st.info("🔗 Probando conexión con la nube...")
                            conexion_render, conexion_msg = test_connection_to_render(render_url)
                            
                            if not conexion_render:
                                st.error("❌ Error de conexión a la nube")
                                st.error(conexion_msg)
                                st.session_state.confirmar_sincro_overwrite = False
                                st.stop()
                            
                            st.success("✅ Conexión a la nube establecida")
                            
                            # 3. Iniciar sincronización OVERWRITE usando database_espejo.py
                            st.info("🔄 Iniciando sincronización desde foc26_espejo hacia Render...")
                            
                            # Importar database_espejo.py solo para sincronización
                            # from database_espejo import sincronizar_espejo_a_render
                            
                            # exito, mensaje = sincronizar_espejo_a_render()
                            
                            # if exito:
                            #     st.success("✅ Sincronización OVERWRITE completada")
                            #     st.info(mensaje)
                            # else:
                            #     st.error("❌ Error en la sincronización OVERWRITE")
                            #     st.error(mensaje)
                            
                            # Resetear confirmación
                            st.session_state.confirmar_sincro_overwrite = False
                            
                        except Exception as e:
                            st.error(f"❌ Error general: {str(e)}")
                            st.warning("💡 Verifique su conexión a internet y la configuración de RENDER_EXTERNAL_URL")
                            st.session_state.confirmar_sincro_overwrite = False
            
            # Información adicional
            with st.expander("📋 Información de Configuración Espejo"):
                st.write("""
                **Estructura de Base de Datos Espejo (Shadow DB):**
                
                🪞 **foc26_espejo** (Base de Datos Espejo):
                - Aquí realizas todos los cambios y pruebas
                - Es el origen de la sincronización OVERWRITE
                - Protege tus datos de producción
                - Se activa con MODO_DESARROLLO=True
                
                ☁️ **Render** (Base en la Nube):
                - Base de datos de producción en la nube
                - Se sobreescribe completamente con datos del espejo
                - Operación destructiva OVERWRITE
                
                **Variables de entorno en .env:**
                ```
                MODO_DESARROLLO=True
                DB_NAME=foc26_espejo
                RENDER_EXTERNAL_URL=postgresql://usuario:password@host:puerto/database?sslmode=require
                ```
                
                **Para crear el espejo:**
                1. Ejecute: python setup_espejo.py
                2. Esto creará la base de datos foc26_espejo
                3. Configurará automáticamente la estructura
                
                **Flujo de trabajo recomendado:**
                1. Configure MODO_DESARROLLO=True en .env
                2. Trabaje en foc26_espejo (ambiente seguro)
                3. Pruebe los cambios thoroughly
                4. Use el botón OVERWRITE para sincronizar
                5. Los datos en la nube serán reemplazados completamente
                """)
        else:
            st.write("📍 Entorno detectado: **Nube (Render)**")
            st.info("ℹ️ La sincronización espejo solo está disponible en entorno local.")
            st.warning("⚠️ Esta función no se puede ejecutar en la nube por seguridad.")
    
    else:
        st.header("⚙️ Configuración")
        st.error("🔒 Esta sección está disponible únicamente para el administrador principal (angelher@gmail.com)")
        mostrar_mensaje_restringido()

# --- MÓDULO G: GESTIÓN DE AMBIENTES (ITIL) ---
elif modulo == "⚙️ Gestión de Ambientes (ITIL)":
    if es_admin_o_super_admin():
        st.header("⚙️ Gestión de Ambientes (ITIL)")
        st.write("Administración de ambientes y protocolos de transición")
        
        # Tabs para diferentes secciones
        tab_protocolos, tab_logs = st.tabs(["📋 Protocolos", "🐞 Log de Errores"])
        
        with tab_protocolos:
            # Protocolo de Transición
            st.subheader("🔄 Protocolo de Transición de Ambientes")
            
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.write("**📍 Entorno Actual:**")
                if verificar_entorno_local():
                    st.success("🏠 Desarrollo Local (SQLite)")
                else:
                    st.info("☁️ Producción (Render)")
            
            with col_info2:
                st.write("**🗄️ Base de Datos:**")
                conn_info = database.get_connection_info()
                st.code(f"""
    Host: {conn_info['host']}
    Database: {conn_info['database']}
    User: {conn_info['user']}
                """)
            
            st.divider()
            
            # Configuración de Correo
            st.subheader("📧 Configuración de Correo SMTP")
            
            # Obtener configuración actual
            config_actual = database.obtener_config_correo(engine_l)
            
            with st.form("form_config_correo"):
                col1, col2 = st.columns(2)
                
                with col1:
                    smtp_server = st.text_input("Servidor SMTP", value=config_actual.get('servidor_smtp', '') if config_actual else '')
                    smtp_port = st.number_input("Puerto", value=config_actual.get('puerto', 587) if config_actual else 587, min_value=1, max_value=65535)
                
                with col2:
                    smtp_user = st.text_input("Usuario", value=config_actual.get('usuario', '') if config_actual else '')
                    smtp_password = st.text_input("Password App", type="password", value=config_actual.get('password_app', '') if config_actual else '')
                
                smtp_remitente = st.text_input("Remitente", value=config_actual.get('remitente', '') if config_actual else '')
                smtp_use_tls = st.checkbox("Usar TLS", value=True)
                
                col_guardar, col_probar = st.columns(2)
                
                with col_guardar:
                    btn_guardar_config = st.form_submit_button("💾 Guardar Configuración", type="primary")
                
                with col_probar:
                    btn_probar_config = st.form_submit_button("🧪 Probar Conexión", type="secondary")
            
            if btn_guardar_config:
                if smtp_server and smtp_port and smtp_user:
                    # Guardar configuración
                    exito = database.guardar_config_correo(
                        servidor=smtp_server,
                        puerto=smtp_port,
                        usuario=smtp_user,
                        contrasena=smtp_password,
                        remitente=smtp_remitente,
                        usar_tls=smtp_use_tls,
                        engine=engine_l
                    )
                    
                    if exito:
                        # Registrar auditoría
                        registrar_auditoria(
                            usuario=st.session_state.user_data.get('login'),
                            rol=obtener_rol_usuario(),
                            transaccion='UPDATE',
                            tabla_afectada='config_correo',
                            detalles=f"servidor:{smtp_server}, puerto:{smtp_port}, usuario:{smtp_user}",
                            engine=engine_l
                        )
                        st.success("✅ Configuración guardada exitosamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al guardar la configuración")
                else:
                    st.error("⚠️ Complete los campos obligatorios: Servidor, Puerto y Usuario")
            
            if btn_probar_config:
                if smtp_server and smtp_port and smtp_user:
                    with st.spinner("Probando conexión SMTP..."):
                        exito, mensaje = database.probar_configuracion_correo(engine_l)
                        
                        if exito:
                            st.success("✅ Conexión SMTP exitosa")
                            st.info(mensaje)
                        else:
                            st.error("❌ Error en la conexión SMTP")
                            st.error(mensaje)
                else:
                    st.error("⚠️ Complete los campos obligatorios para probar")
            
            st.divider()
            
            # Prueba de flujo de validación
            st.subheader("📧 Prueba de Flujo de Validación")
            
            email_prueba = st.text_input(
                "Correo de prueba", 
                placeholder="angelher@gmail.com",
                help="Correo al que se enviará el mensaje de prueba"
            )
            
            if st.button("📧 Probar Flujo de Validación", type="primary"):
                if email_prueba and config_actual:
                    with st.spinner("Enviando correo de confirmación..."):
                        try:
                            # Actualizar remitente a ab6643881@gmail.com
                            database.guardar_config_correo(
                                servidor=config_actual['servidor_smtp'], 
                                puerto=config_actual['puerto'], 
                                usuario=config_actual['usuario'], 
                                contrasena=config_actual['password_app'], 
                                remitente='ab6643881@gmail.com',
                                usar_tls=None,
                                engine=engine_l
                            )
                            
                            # Enviar correo de confirmación
                            exito, mensaje = database.enviar_confirmacion_registro(email_prueba, engine_l)
                            
                            if exito:
                                st.success("✅ Correo de confirmación enviado")
                                st.info(mensaje)
                                
                                # Mostrar enlace generado (para pruebas)
                                import hashlib
                                import time
                                timestamp = str(int(time.time()))
                                token_data = f"{email_prueba}:{timestamp}"
                                token = hashlib.sha256(token_data.encode()).hexdigest()[:32]
                                
                                st.markdown("**🔗 Enlace de prueba (para desarrollo):**")
                                st.code(f"https://sicadfoc-proyecto.onrender.com?confirmar={token}&email={email_prueba}")
                            else:
                                st.warning("⚠️ No se pudo enviar el correo")
                                st.error(mensaje)
                        except Exception as e:
                            st.error(f"❌ Error en el proceso: {e}")
                else:
                    st.warning("⚠️ Ingrese un correo de prueba y asegúrese que la configuración SMTP esté guardada")
        
        with tab_logs:
            st.subheader("🐞 Log de Errores del Sistema")
            st.write("Visualización y gestión de errores registrados automáticamente")
            
            # Filtros
            col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
            
            with col_filtro1:
                estado_filtro = st.selectbox(
                    "Filtrar por estado:",
                    ["Todos", "Pendiente", "Resuelto"],
                    key="filtro_estado"
                )
            
            with col_filtro2:
                limite_registros = st.selectbox(
                    "Límite de registros:",
                    [10, 25, 50, 100],
                    index=2,
                    key="limite_logs"
                )
            
            with col_filtro3:
                if st.button("🔄 Actualizar Logs", type="secondary"):
                    st.rerun()
            
            # Obtener logs
            try:
                estado_param = None if estado_filtro == "Todos" else estado_filtro
                logs_df = database.obtener_logs_sistema(estado=estado_param, limite=limite_registros, engine=engine_l)
                
                if not logs_df.empty:
                    # Estadísticas
                    col_stats1, col_stats2, col_stats3 = st.columns(3)
                    
                    with col_stats1:
                        total_logs = len(logs_df)
                        st.metric("Total Logs", total_logs)
                    
                    with col_stats2:
                        pendientes = len(logs_df[logs_df['estado'] == 'Pendiente'])
                        st.metric("Pendientes", pendientes)
                    
                    with col_stats3:
                        errores_bd = len(logs_df[logs_df['modulo'].str.contains('database', case=False, na=False)])
                        st.metric("Errores BD", errores_bd)
                    
                    st.divider()
                    
                    # Tabla de logs con estilo
                    st.write("**📋 Registro de Errores:**")
                    
                    # Formatear DataFrame para visualización
                    display_df = logs_df.copy()
                    
                    # Resaltar errores de base de datos
                    def highlight_errors(row):
                        styles = [''] * len(row)
                        if 'database' in str(row['modulo']).lower():
                            styles[display_df.columns.get_loc('modulo')] = 'background-color: #ffcccc; color: #cc0000; font-weight: bold;'
                        if row['estado'] == 'Pendiente':
                            styles[display_df.columns.get_loc('estado')] = 'background-color: #fff3cd; color: #856404; font-weight: bold;'
                        return styles
                    
                    # Aplicar estilos
                    styled_df = display_df.style.apply(highlight_errors, axis=1)
                    
                    # Mostrar tabla
                    st.dataframe(styled_df, use_container_width=True)
                    
                    # Acciones sobre logs seleccionados
                    st.divider()
                    st.write("**⚡ Acciones:**")
                    
                    col_accion1, col_accion2 = st.columns(2)
                    
                    with col_accion1:
                        if st.button("✅ Marcar seleccionados como Resueltos", type="secondary"):
                            mostrar_toast("Función de actualización masiva en desarrollo", "info")
                    
                    with col_accion2:
                        if st.button("🗑️ Limpiar logs antiguos (más de 30 días)", type="secondary"):
                            mostrar_toast("Función de limpieza en desarrollo", "info")
                    
                    # Detalles del error seleccionado
                    if st.checkbox("📝 Mostrar detalles de error seleccionado"):
                        error_id = st.selectbox(
                            "Seleccionar error para ver detalles:",
                            logs_df['id'].tolist(),
                            format_func=lambda x: f"Error #{x} - {logs_df[logs_df['id'] == x]['fecha_hora'].values[0]}"
                        )
                        
                        if error_id:
                            error_detalle = logs_df[logs_df['id'] == error_id].iloc[0]
                            
                            st.markdown(f"""
                            **📋 Detalles del Error #{error_id}:**
                            
                            - **Fecha/Hora:** {error_detalle['fecha_hora']}
                            - **Usuario:** {error_detalle['usuario']}
                            - **Módulo:** {error_detalle['modulo']}
                            - **Línea:** {error_detalle['linea_codigo']}
                            - **Estado:** {error_detalle['estado']}
                            - **Nivel:** {error_detalle['nivel_error']}
                            
                            **Mensaje de Error:**
                            ```
                            {error_detalle['mensaje_error']}
                            ```
                            """)
                            
                            if error_detalle['stack_trace']:
                                with st.expander("🔍 Stack Trace Completo"):
                                    st.code(error_detalle['stack_trace'], language="python")
                            
                            # Botón para cambiar estado
                            col_estado1, col_estado2 = st.columns(2)
                            
                            with col_estado1:
                                if st.button(f"✅ Marcar como Resuelto #{error_id}", type="primary"):
                                    if database.actualizar_estado_log(error_id, "Resuelto", engine_l):
                                        mostrar_toast(f"Error #{error_id} marcado como resuelto", "success")
                                        st.rerun()
                                    else:
                                        mostrar_toast("Error actualizando estado", "error")
                            
                            with col_estado2:
                                if st.button(f"🔄 Reabrir Error #{error_id}", type="secondary"):
                                    if database.actualizar_estado_log(error_id, "Pendiente", engine_l):
                                        mostrar_toast(f"Error #{error_id} reabierto", "info")
                                        st.rerun()
                                    else:
                                        mostrar_toast("Error actualizando estado", "error")
                
                else:
                    st.info("ℹ️ No hay errores registrados en el sistema")
                    
                    # Botón para crear tabla si no existe
                    if st.button("🔧 Crear tabla de logs", type="secondary"):
                        if database.crear_tabla_logs_sistema(engine_l):
                            mostrar_toast("Tabla de logs creada exitosamente", "success")
                            st.rerun()
                        else:
                            mostrar_toast("Error creando tabla de logs", "error")
                    
                    # Botón de prueba de estrés
                    st.divider()
                    st.write("**🧪 Prueba de Estrés del Centinela:**")
                    
                    col_test1, col_test2 = st.columns(2)
                    
                    with col_test1:
                        if st.button("🚨 Simular Error Crítico", type="primary"):
                            with st.spinner("Simulando error crítico y enviando alerta..."):
                                try:
                                    # Optimizar trazabilidad antes de la prueba
                                    database.optimizar_trazabilidad_session_state()
                                    
                                    # Simular error crítico
                                    resultado = database.simular_error_critico(engine_l)
                                    
                                    if resultado['error_id']:
                                        st.success(f"✅ {resultado['mensaje']}")
                                        
                                        if resultado['alerta_enviada']:
                                            st.info("📧 Alerta crítica enviada a angelher@gmail.com")
                                            st.code(f"ID de incidente: #{resultado['error_id']}")
                                        else:
                                            st.warning("⚠️ Alerta no enviada (revisar configuración SMTP)")
                                    else:
                                        st.error(f"❌ {resultado['mensaje']}")
                                        
                                except Exception as e:
                                    st.error(f"❌ Error en prueba de estrés: {e}")
                    
                    with col_test2:
                        if st.button("🔍 Verificar Configuración", type="secondary"):
                            try:
                                # Verificar variables críticas
                                database.optimizar_trazabilidad_session_state()
                                
                                # Verificar configuración de correo
                                config = database.obtener_config_correo(engine_l)
                                
                                st.write("**📋 Estado del Sistema:**")
                                
                                if config:
                                    st.success("✅ Configuración SMTP encontrada")
                                    st.code(f"""
Servidor: {config.get('servidor_smtp', 'N/A')}
Puerto: {config.get('puerto', 'N/A')}
Usuario: {config.get('usuario', 'N/A')}
Remitente: {config.get('remitente', 'N/A')}
                                    """)
                                else:
                                    st.warning("⚠️ No hay configuración SMTP")
                                
                                # Verificar variables de session_state
                                st.write("**🔍 Variables de Trazabilidad:**")
                                st.code(f"""
Usuario: {st.session_state.user_data.get('login', 'N/A')}
Rol: {st.session_state.get('rol', 'N/A')}
SQLite Path: {st.session_state.get('sqlite_db_path', 'N/A')}
                                """)
                                
                            except Exception as e:
                                st.error(f"❌ Error verificando configuración: {e}")
                
            except Exception as e:
                st.error(f"❌ Error obteniendo logs: {e}")
                mostrar_toast("Error cargando logs del sistema", "error")
        
        # Sección de sincronización (solo en entorno local)
        st.divider()
        st.subheader("🔄 Sincronización de Datos")
        
        # Verificar si estamos en entorno local
        if verificar_entorno_local():
            st.write("📍 Entorno detectado: **Local**")
            
            # Mostrar información de base de datos espejo
            espejo_info = get_info_espejo()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🪞 Base de Datos Espejo (Shadow DB):**")
                st.code(f"""
Database: {espejo_info['espejo']['database']}
Host: {espejo_info['espejo']['host']}
Port: {espejo_info['espejo']['port']}
User: {espejo_info['espejo']['user']}
Modo Desarrollo: {espejo_info['espejo']['modo_desarrollo']}
                """)
            
            with col2:
                st.write("**☁️ Base de Datos en la Nube:**")
                render_url = os.environ.get("RENDER_EXTERNAL_URL", "No configurada")
                st.code(f"""
URL: {render_url[:50] + '...' if len(render_url) > 50 else render_url}
Estado: {'Configurada' if render_url != 'No configurada' else 'No configurada'}
                """)
            
            st.info("💡 Esta sección permite sincronizar datos desde el espejo local (foc26_espejo) hacia la nube (Render).")
            
            # Botones de sincronización
            col_sync1, col_sync2 = st.columns(2)
            
            with col_sync1:
                if st.button("📤 Subir a la Nube", type="primary", help="Sincronizar datos locales hacia la nube"):
                    with st.spinner("Sincronizando datos hacia la nube..."):
                        try:
                            resultado = sincronizar_hacia_nube(engine_l, engine_r)
                            if resultado['status'] == 'success':
                                st.success(f"✅ Sincronización exitosa: {resultado['registros']} registros")
                                registrar_auditoria_sistema(
                                    usuario=st.session_state.user_data.get('login'),
                                    transaccion='SYNC_TO_CLOUD',
                                    detalles_adicionales=f"Registros: {resultado['registros']}"
                                )
                            else:
                                st.error(f"❌ Error en sincronización: {resultado['message']}")
                        except Exception as e:
                            st.error(f"❌ Error crítico: {str(e)}")
            
            with col_sync2:
                if st.button("📥 Bajar de la Nube", type="secondary", help="Traer datos desde la nube hacia local"):
                    with st.spinner("Descargando datos desde la nube..."):
                        try:
                            resultado = traer_de_nube(engine_r, engine_l)
                            if resultado['status'] == 'success':
                                st.success(f"✅ Descarga exitosa: {resultado['registros']} registros")
                                registrar_auditoria_sistema(
                                    usuario=st.session_state.user_data.get('login'),
                                    transaccion='SYNC_FROM_CLOUD',
                                    detalles_adicionales=f"Registros: {resultado['registros']}"
                                )
                            else:
                                st.error(f"❌ Error en descarga: {resultado['message']}")
                        except Exception as e:
                            st.error(f"❌ Error crítico: {str(e)}")
            
            # Estado de sincronización
            st.divider()
            st.subheader("📊 Estado de Sincronización")
            
            try:
                # Obtener métricas de sincronización
                metrics_local = get_metricas_dashboard(engine_l)
                metrics_nube = get_metricas_dashboard(engine_r)
                
                col_comp1, col_comp2, col_comp3 = st.columns(3)
                
                with col_comp1:
                    st.metric("📊 Registros Locales", metrics_local.get('total_usuarios', 0))
                
                with col_comp2:
                    st.metric("☁️ Registros Nube", metrics_nube.get('total_usuarios', 0))
                
                with col_comp3:
                    diferencia = metrics_local.get('total_usuarios', 0) - metrics_nube.get('total_usuarios', 0)
                    st.metric("🔄 Diferencia", diferencia)
                
                # Logs de sincronización
                logs_sync = obtener_logs_sincronizacion(engine_l)
                
                if logs_sync and len(logs_sync) > 0:
                    st.write("📋 **Historial de Sincronización:**")
                    df_logs = pd.DataFrame(logs_sync)
                    df_logs['fecha'] = pd.to_datetime(df_logs['fecha']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    st.dataframe(df_logs[['fecha', 'operacion', 'registros', 'estado']].rename(columns={
                        'fecha': 'Fecha/Hora',
                        'operacion': 'Operación',
                        'registros': 'Registros',
                        'estado': 'Estado'
                    }), use_container_width=True)
                else:
                    st.info("ℹ️ No hay historial de sincronización")
                    
            except Exception as e:
                st.error(f"❌ Error obteniendo estado: {e}")
            
        else:
            st.warning("⚠️ Esta sección de sincronización solo está disponible en entorno local")
            st.info("💡 Para sincronizar datos, ejecute el sistema en su entorno local")
        
        # Protocolos de ITIL
        st.divider()
        st.subheader("📋 Protocolos ITIL")
        
        with st.expander("🔄 Protocolo de Transición de Servicios"):
            st.markdown("""
            **Fase 1: Evaluación**
            - Verificar integridad de datos locales
            - Validar estructura de tablas
            - Revisar consistency de relaciones
            
            **Fase 2: Preparación**
            - Backup de base de datos actual
            - Crear puntos de restauración
            - Documentar estado actual
            
            **Fase 3: Ejecución**
            - Sincronizar datos hacia nube
            - Validar transferencia
            - Verificar integridad
            
            **Fase 4: Validación**
            - Pruebas funcionales
            - Verificación de datos
            - Aprobación de stakeholders
            
            **Fase 5: Cierre**
            - Documentación de cambios
            - Actualización de registros
            - Comunicación a usuarios
            """)
        
        with st.expander("🔧 Protocolo de Gestión de Cambios"):
            st.markdown("""
            **1. Solicitud de Cambio**
            - Identificar necesidad
            - Evaluar impacto
            - Documentar requerimientos
            
            **2. Evaluación**
            - Análisis de riesgos
            - Viabilidad técnica
            - Recursos requeridos
            
            **3. Aprobación**
            - Revisión por stakeholders
            - Autorización formal
            - Planificación
            
            **4. Implementación**
            - Ejecución del cambio
            - Monitoreo continuo
            - Documentación
            
            **5. Verificación**
            - Pruebas de aceptación
            - Validación funcional
            - Retroalimentación
            """)
        
        with st.expander("📊 Protocolo de Monitoreo"):
            st.markdown("""
            **Métricas Clave:**
            - Disponibilidad del sistema
            - Tiempo de respuesta
            - Tasa de errores
            - Uso de recursos
            
            **Alertas:**
            - Caídas de servicio
            - Errores críticos
            - Rendimiento degradado
            - Problemas de seguridad
            
            **Reportes:**
            - Diarios: Estado general
            - Semanales: Tendencias
            - Mensuales: Análisis profundo
            - Anuales: Estratégicos
            """)
        
        # Botón de diagnóstico completo
        st.divider()
        
        col_diag1, col_diag2 = st.columns(2)
        
        with col_diag1:
            if st.button("🔍 Ejecutar Diagnóstico Completo", type="primary"):
                with st.spinner("Ejecutando diagnóstico del sistema..."):
                    try:
                        # Verificar tablas
                        tablas_ok = verificar_tablas_sistema(engine_l)
                        
                        # Verificar conexiones
                        conn_local = database.get_connection_info()
                        
                        # Verificar logs
                        logs_count = len(database.obtener_logs_sistema(limite=1, engine=engine_l))
                        
                        st.success("✅ Diagnóstico completado")
                        st.json({
                            "tablas_sistema": tablas_ok,
                            "conexion_local": conn_local,
                            "logs_activos": logs_count > 0,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                    except Exception as e:
                        st.error(f"❌ Error en diagnóstico: {e}")
        
        with col_diag2:
            if st.button("📊 Generar Reporte de Sistema", type="secondary"):
                with st.spinner("Generando reporte..."):
                    try:
                        # Recopilar métricas
                        metrics = get_metricas_dashboard(engine_l)
                        logs = database.obtener_logs_sistema(limite=10, engine=engine_l)
                        
                        st.info("📋 Reporte generado exitosamente")
                        
                        # Mostrar resumen
                        col_rep1, col_rep2 = st.columns(2)
                        
                        with col_rep1:
                            st.metric("Usuarios Totales", metrics.get('total_usuarios', 0))
                            st.metric("Estudiantes", metrics.get('estudiantes', 0))
                        
                        with col_rep2:
                            st.metric("Profesores", metrics.get('profesores', 0))
                            st.metric("Admins", metrics.get('administradores', 0))
                        
                        if not logs.empty:
                            st.write("📋 **Errores Recientes:**")
                            st.dataframe(logs[['fecha_hora', 'modulo', 'mensaje_error', 'estado']].head(5))
                        
                    except Exception as e:
                        st.error(f"❌ Error generando reporte: {e}")
        
    else:
        st.header("⚙️ Gestión de Ambientes (ITIL)")
        st.error("🔒 Esta sección está disponible únicamente para el administrador principal (angelher@gmail.com)")
        mostrar_mensaje_restringido()
        st.info("""
        📋 **PROTOCOL DE TRANSICIÓN DE AMBIENTES**
        
        🔒 **RESPALDO OBLIGATORIO**: Antes de sincronizar, volcado SQL en Desktop/PROYECTO_IUJO_SICADFOC
        
        🛠️ **AMBIENTE DESARROLLO**: 
        - Base de datos: foc26_limpio.db
        - Tema: Modo Oscuro
        - Uso: Desarrollo y pruebas
        - Conexión: database.py (SQLite local)
        
        🚀 **AMBIENTE PRODUCCIÓN (ESPEJO)**: 
        - Base de datos: Foc26_espejo.db
        - Tema: Modo Claro (Blanco)
        - Uso: Producción local
        - Conexión: database.py (SQLite local)
        
        ☁️ **AMBIENTE NUBE (RENDER)**:
        - Base de datos: PostgreSQL en Render
        - Tema: Modo Claro forzado
        - Uso: Producción en la nube
        - Conexión: database_espejo.py (PostgreSQL en nube)
        
        📖 **REGLA DE ORO VISUAL**:
        - Si usa funciones de database.py → Tema automático (oscuro/claro según BD local)
        - Si usa funciones de database_espejo.py → Tema forzado a Blanco + banner nube
        """)
        
        st.divider()
        
        # Documentación de Conexiones
        with st.expander("📚 Documentación de Conexiones"):
            st.markdown("""
            ### **SISTEMA DE CONEXIONES DUPLAS**
            
            **🗄️ database.py (Conexión Local)**
            - **Propósito**: Desarrollo y producción local
            - **Bases**: foc26_limpio.db (desarrollo) / Foc26_espejo.db (producción local)
            - **Motor**: SQLite
            - **Tema Visual**: Automático según base de datos detectada
            - **Funciones**: `get_connection()`, `ejecutar_query()`, etc.
            
            **☁️ database_espejo.py (Conexión Nube)**
            - **Propósito**: Producción en la nube (Render)
            - **Base**: PostgreSQL en Render
            - **Motor**: PostgreSQL
            - **Tema Visual**: Forzado a Modo Claro + banner verde
            - **Funciones**: `get_connection_espejo()`, `ejecutar_query_nube()`, etc.
            
            ### **REGLA DE SEGURIDAD VISUAL**
            ```
            SI (función_usada == database_espejo.*) {
                tema = "MODO CLARO FORZADO"
                mostrar_banner("🚀 EJECUTANDO EN NUBE (RENDER)")
            } SINO {
                tema = "AUTOMÁTICO SEGÚN BASE LOCAL"
                // Oscuro para foc26_limpio.db
                // Claro para Foc26_espejo.db
            }
            ```
            
            ### **FLUJO DE TRABAJO RECOMENDADO**
            1. **Desarrollo**: Usar `database.py` con `foc26_limpio.db` → Tema oscuro
            2. **Pruebas**: Cambiar a `Foc26_espejo.db` → Tema claro local
            3. **Producción**: Usar `database_espejo.py` → Tema claro + banner nube
            4. **Validación**: El tema visual indica automáticamente el entorno activo
            """)
        
        st.divider()
        
        # Sección de acciones rápidas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🛠️ Desarrollo")
            if st.button("🔄 Cambiar a Desarrollo", type="secondary"):
                import subprocess
                result = subprocess.run(['python', 'cambiar_bd.py', 'desarrollo'], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("✅ Cambiado a ambiente de desarrollo")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result.stderr}")
        
        with col2:
            st.subheader("🚀 Producción Local")
            if st.button("🔄 Cambiar a Producción", type="secondary"):
                import subprocess
                result = subprocess.run(['python', 'cambiar_bd.py', 'espejo'], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("✅ Cambiado a ambiente de producción local")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result.stderr}")
        
        with col3:
            st.subheader("💾 Respaldo")
            if st.button("📥 Crear Respaldo", type="secondary"):
                import subprocess
                result = subprocess.run(['python', 'respaldar_bd.py'], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("✅ Respaldo creado exitosamente")
                else:
                    st.error(f"❌ Error: {result.stderr}")
        
        st.divider()
        
        # Historial de Versiones
        st.subheader("📜 Historial de Versiones")
        
        # Crear DataFrame para el historial
        if 'historial_versiones' not in st.session_state:
            st.session_state.historial_versiones = [
                {"Fecha": "2026-03-22", "Versión": "v1.0.0", "Cambio": "Implementación inicial del sistema SICADFOC", "Ambiente": "Desarrollo"},
                {"Fecha": "2026-03-22", "Versión": "v1.0.1", "Cambio": "Corrección de autenticación y auditoría", "Ambiente": "Desarrollo"},
                {"Fecha": "2026-03-22", "Versión": "v1.1.0", "Cambio": "Protocolo de seguridad y clonación de ambientes", "Ambiente": "Producción Local"}
            ]
        
        # Formulario para agregar nueva versión
        with st.expander("➕ Agregar Nueva Versión"):
            with st.form("form_version"):
                col_fecha, col_version, col_ambiente = st.columns(3)
                
                with col_fecha:
                    nueva_fecha = st.date_input("Fecha", value=datetime.now().date())
                
                with col_version:
                    nueva_version = st.text_input("Versión", placeholder="ej: v1.2.0")
                
                with col_ambiente:
                    nuevo_ambiente = st.selectbox("Ambiente", ["Desarrollo", "Producción Local", "Nube (Render)"])
                
                nuevo_cambio = st.text_area("Descripción del Cambio", placeholder="Describa los cambios realizados...")
                
                if st.form_submit_button("📝 Agregar Versión"):
                    if nueva_version and nuevo_cambio:
                        st.session_state.historial_versiones.append({
                            "Fecha": nueva_fecha.strftime("%Y-%m-%d"),
                            "Versión": nueva_version,
                            "Cambio": nuevo_cambio,
                            "Ambiente": nuevo_ambiente
                        })
                        st.success("✅ Versión agregada al historial")
                        st.rerun()
                    else:
                        st.error("⚠️ Complete la versión y la descripción")
        
        # Mostrar historial
        import pandas as pd
        df_historial = pd.DataFrame(st.session_state.historial_versiones)
        st.dataframe(df_historial, use_container_width=True)
        
        # Estado actual del sistema
        st.divider()
        st.subheader("🔍 Estado Actual del Sistema")
        
        col_estado1, col_estado2 = st.columns(2)
        
        with col_estado1:
            st.write("**Información de Conexión:**")
            engine_info = str(engine_l.url)
            st.code(engine_info)
            
            if 'foc26_limpio.db' in engine_info:
                st.success("🛠️ Ambiente Actual: DESARROLLO")
            elif 'Foc26_espejo.db' in engine_info:
                st.success("🚀 Ambiente Actual: PRODUCCIÓN LOCAL")
            else:
                st.warning("⚠️ Ambiente Actual: DESCONOCIDO")
        
        with col_estado2:
            st.write("**Configuración de Temas:**")
            if 'foc26_limpio.db' in engine_info:
                st.info("🎨 Tema: Modo Oscuro")
            elif 'Foc26_espejo.db' in engine_info:
                st.info("🎨 Tema: Modo Claro")
            
            st.write("**Usuario Actual:**")
            st.code(f"👤 {st.session_state.user_data['login']} ({st.session_state.rol})")
        
        # Información de despliegue
        st.divider()
        st.subheader("☁️ Información de Despliegue")
        
        with st.expander("📋 Archivos de Configuración para Render"):
            st.code("""
# runtime.txt
python-3.10.11

# requirements.txt
streamlit==1.28.1
sqlalchemy==2.0.21
pandas==2.1.1
psycopg2-binary==2.9.7
python-dotenv==1.0.0

# Procfile
web: streamlit run main.py --server.port $PORT --server.address 0.0.0.0
            """)
        
        # Verificación de archivos de despliegue
        st.write("**Estado de Archivos de Despliegue:**")
        
        archivos_requeridos = ["runtime.txt", "requirements.txt", "Procfile", "database_espejo.py"]
        for archivo in archivos_requeridos:
            if os.path.exists(archivo):
                st.success(f"✅ {archivo} - Existe")
            else:
                st.warning(f"⚠️ {archivo} - No encontrado")
        
        st.divider()
        
        # Validación de Seguridad
        st.subheader("🔐 Validación de Seguridad")
        
        col_val1, col_val2 = st.columns(2)
        
        with col_val1:
            st.write("**Pruebas de Conexión:**")
            
            # Probar conexión local
            if st.button("🧪 Probar Conexión Local", type="secondary"):
                try:
                    import database
                    conn_info = database.get_connection_info()
                    st.success(f"✅ Conexión Local: {conn_info['environment']}")
                    st.code(f"Base: {conn_info['database']}")
                except Exception as e:
                    st.error(f"❌ Error conexión local: {e}")
            
            # Probar conexión nube
            if st.button("🧪 Probar Conexión Nube", type="secondary"):
                try:
                    import database_espejo
                    if database_espejo.verificar_conexion_nube():
                        st.success("✅ Conexión Nube: Activa")
                        nube_info = database_espejo.get_info_espejo()
                        st.code(f"Host: {nube_info['host']}")
                    else:
                        st.error("❌ Conexión Nube: Inactiva")
                except Exception as e:
                    st.error(f"❌ Error conexión nube: {e}")
        
        with col_val2:
            st.write("**Validación de Reglas Visuales:**")
            
            # Detectar ambiente actual
            engine_info = str(engine_l.url)
            
            if 'render.com' in engine_info:
                st.success("🎨 Regla Activa: Tema Claro Forzado (Nube)")
                st.info("🚀 Banner: EJECUTANDO EN NUBE (RENDER)")
            elif 'foc26_limpio.db' in engine_info:
                st.success("🎨 Regla Activa: Tema Oscuro (Desarrollo)")
                st.info("🛠️ Aviso: ENTORNO DESARROLLO")
            elif 'Foc26_espejo.db' in engine_info:
                st.success("🎨 Regla Activa: Tema Claro (Producción Local)")
                st.info("🚀 Aviso: ENTORNO PRODUCCIÓN (LOCAL)")
            else:
                st.warning("⚠️ Regla Visual: No detectada")
        
        st.divider()
        
        # Sección de sincronización
        st.subheader("🔄 Sincronización de Datos")
        
        col_sync1, col_sync2 = st.columns(2)
        
        with col_sync1:
            st.write("**Sincronización Local → Nube:**")
            if st.button("📤 Sincronizar a Render", type="primary"):
                try:
                    import database_espejo
                    with st.spinner("Sincronizando datos a la nube..."):
                        exito, mensaje = database_espejo.sincronizar_espejo_a_render()
                        
                    if exito:
                        st.success("✅ Sincronización completada")
                        st.info(mensaje)
                    else:
                        st.error("❌ Error en sincronización")
                        st.error(mensaje)
                        
                except Exception as e:
                    st.error(f"❌ Error general: {e}")
        
        with col_sync2:
            st.write("**Estado de Sincronización:**")
            
            # Obtener métricas locales
            try:
                import database
                metricas_locales = database.get_metricas_dashboard(engine_l)
                st.metric("Usuarios Locales", metricas_locales.get('estudiantes', 0))
            except:
                st.metric("Usuarios Locales", 0)
            
            # Obtener métricas nube
            try:
                import database_espejo
                metricas_nube = database_espejo.obtener_metricas_nube()
                st.metric("Usuarios Nube", metricas_nube.get('estudiantes', 0))
            except:
                st.metric("Usuarios Nube", 0)
        
        st.divider()
        
        # Pestaña de Configuración de Correo
        st.subheader("📧 Configuración de Correo SMTP")
        
        # Crear tabla si no existe
        database.crear_tabla_configuracion_correo()
        
        # Obtener configuración actual
        config_actual = database.obtener_config_correo(engine_l)
        
        # Formulario de configuración
        with st.form("form_correo_smtp"):
            col1, col2 = st.columns(2)
            
            with col1:
                servidor_smtp = st.text_input(
                    "Servidor SMTP", 
                    value=config_actual.get('servidor_smtp', '') if config_actual else 'smtp.gmail.com',
                    help="Ej: smtp.gmail.com, smtp.outlook.com"
                )
                puerto = st.number_input(
                    "Puerto", 
                    value=config_actual.get('puerto', 587) if config_actual else 587,
                    min_value=1, max_value=65535
                )
                usuario = st.text_input(
                    "Usuario SMTP", 
                    value=config_actual.get('usuario', '') if config_actual else '',
                    help="Correo completo para autenticación"
                )
            
            with col2:
                password_app = st.text_input(
                    "Password de Aplicación", 
                    value=config_actual.get('password_app', '') if config_actual else '',
                    type="password",
                    help="Use password de aplicación, no la contraseña normal del correo"
                )
                remitente = st.text_input(
                    "Correo Remitente", 
                    value=config_actual.get('remitente', '') if config_actual else 'noreply@iujo.edu',
                    help="Correo desde donde se enviarán los mensajes"
                )
            
            col_guardar, col_probar = st.columns(2)
            
            with col_guardar:
                btn_guardar = st.form_submit_button("💾 Guardar Configuración", type="primary")
            
            with col_probar:
                btn_probar = st.form_submit_button("🧪 Probar Conexión", type="secondary")
        
        # Procesar formulario
        if btn_guardar:
            if servidor_smtp and puerto and usuario and password_app and remitente:
                if database.guardar_config_correo(servidor_smtp, puerto, usuario, password_app, remitente, usar_tls=None, engine=engine_l):
                    st.success("✅ Configuración de correo guardada exitosamente")
                    st.rerun()
                else:
                    st.error("❌ Error al guardar la configuración")
            else:
                st.error("⚠️ Complete todos los campos obligatorios")
        
        if btn_probar:
            if servidor_smtp and puerto and usuario and password_app and remitente:
                with st.spinner("Probando conexión SMTP..."):
                    exito, mensaje = database.probar_configuracion_correo(engine_l)
                    
                if exito:
                    st.success("✅ Prueba exitosa")
                    st.info(mensaje)
                else:
                    st.error("❌ Error en la prueba")
                    st.error(mensaje)
            else:
                st.error("⚠️ Complete todos los campos antes de probar")
        
        # Mostrar configuración actual
        if config_actual:
            st.divider()
            st.write("**Configuración Actual:**")
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.metric("Servidor", config_actual['servidor_smtp'])
                st.metric("Puerto", config_actual['puerto'])
            
            with col_info2:
                st.metric("Usuario", config_actual['usuario'])
                st.metric("Remitente", config_actual['remitente'])
            
            st.caption(f"Última actualización: {config_actual.get('fecha_actualizacion', 'N/A')}")
        
        st.divider()
        
        # Prueba de Flujo de Validación
        st.subheader("🧪 Prueba de Flujo de Validación")
        st.write("**Enviar correo de confirmación a mi correo personal**")
        
        col_flujo1, col_flujo2 = st.columns(2)
        
        with col_flujo1:
            email_prueba = st.text_input(
                "Correo para prueba", 
                value="ab6643881@gmail.com",
                help="Correo al que se enviará el mensaje de prueba"
            )
        
        with col_flujo2:
            if st.button("📧 Probar Flujo de Validación", type="primary"):
                if email_prueba and config_actual:
                    with st.spinner("Enviando correo de confirmación..."):
                        try:
                            # Actualizar remitente a ab6643881@gmail.com
                            database.guardar_config_correo(
                                servidor=config_actual['servidor_smtp'], 
                                puerto=config_actual['puerto'], 
                                usuario=config_actual['usuario'], 
                                contrasena=config_actual['password_app'], 
                                remitente='ab6643881@gmail.com',
                                usar_tls=None,
                                engine=engine_l
                            )
                            
                            # Enviar correo de confirmación
                            exito, mensaje = database.enviar_confirmacion_registro(email_prueba, engine_l)
                            
                            if exito:
                                st.success("✅ Correo de confirmación enviado")
                                st.info(mensaje)
                                
                                # Mostrar enlace generado (para pruebas)
                                with st.expander("🔗 Ver enlace generado (pruebas)"):
                                    st.code("Enlace de confirmación generado. Revise su correo.")
                                    st.caption("El enlace contiene un token único que expira en 24 horas.")
                                
                            else:
                                st.error("❌ Error enviando correo")
                                st.error(mensaje)
                                
                        except Exception as e:
                            st.error(f"❌ Error general: {e}")
                else:
                    st.error("⚠️ Complete el correo de prueba y asegúrese de tener configuración SMTP")
        
        # Mostrar estado de verificación de usuarios
        st.divider()
        st.subheader("📋 Estado de Verificación de Correos")
        
        try:
            with engine_l.connect() as conn:
                # Obtener usuarios y su estado de verificación
                usuarios = conn.execute(database.text('''
                SELECT login, rol, correo_verificado, activo 
                FROM usuario 
                ORDER BY rol, login
                ''')).fetchall()
                
                if usuarios:
                    df_usuarios = pd.DataFrame(usuarios, columns=['Login', 'Rol', 'Correo Verificado', 'Activo'])
                    
                    # Formatear para mejor visualización
                    df_usuarios['Correo Verificado'] = df_usuarios['Correo Verificado'].apply(
                        lambda x: '✅ Sí' if x == 1 else '❌ No'
                    )
                    df_usuarios['Activo'] = df_usuarios['Activo'].apply(
                        lambda x: '✅ Sí' if x == 1 else '❌ No'
                    )
                    
                    st.dataframe(df_usuarios, use_container_width=True)
                    
                    # Estadísticas
                    total = len(df_usuarios)
                    verificados = len(df_usuarios[df_usuarios['Correo Verificado'] == '✅ Sí'])
                    
                    col_stat1, col_stat2, col_stat3 = st.columns(3)
                    with col_stat1:
                        st.metric("👥 Total Usuarios", total)
                    with col_stat2:
                        st.metric("✅ Correos Verificados", verificados)
                    with col_stat3:
                        st.metric("📊 Porcentaje Verificado", f"{(verificados/total*100):.1f}%")
                        
                else:
                    st.info("No hay usuarios registrados")
                    
        except Exception as e:
            st.error(f"Error obteniendo estado de verificación: {e}")
        
        st.divider()
        
        # Interfaz de Sincronización
        st.subheader("🔄 Sincronización de Datos")
        
        col_sync1, col_sync2 = st.columns(2)
        
        with col_sync1:
            st.write("**Subir a la Nube (Ambiente Blanco):**")
            if st.button("⬆️ Subir cambios a la Nube", type="primary"):
                # Confirmación
                st.warning("⚠️ **ADVERTENCIA DE SINCRONIZACIÓN**")
                st.write("""
                Esta acción sobrescribirá los datos en la nube con los datos locales.
                
                **Acciones a realizar:**
                - Leer datos de la base local (foc26_limpio.db)
                - Aplicar lógica de Upsert en la nube (actualizar si existe, insertar si no)
                - Registrar log de sincronización
                
                **¿Desea continuar?**
                """)
                
                if st.button("✅ Confirmar Subida a Nube", key="confirm_subir"):
                    with st.spinner("Sincronizando hacia la nube..."):
                        try:
                            import pivote_datos
                            resultados = pivote_datos.sincronizar_todas_tablas_hacia_nube()
                            
                            st.success("✅ Sincronización completada")
                            
                            for resultado in resultados:
                                if resultado['exito']:
                                    st.success(f"📊 {resultado['tabla']}: {resultado['mensaje']}")
                                else:
                                    st.error(f"❌ {resultado['tabla']}: {resultado['mensaje']}")
                                    
                        except Exception as e:
                            st.error(f"❌ Error en sincronización: {e}")
        
        with col_sync2:
            st.write("**Bajar a Desarrollo (Ambiente Oscuro):**")
            if st.button("⬇️ Bajar cambios a Desarrollo", type="primary"):
                # Confirmación
                st.warning("⚠️ **ADVERTENCIA DE SOBRESCRITURA**")
                st.write("""
                Esta acción REEMPLAZARÁ completamente los datos locales con los de la nube.
                
                **Acciones a realizar:**
                - Descargar todos los datos desde la nube (Render)
                - Limpiar tablas locales (foc26_limpio.db)
                - Insertar datos de la nube en tablas locales
                - Registrar log de sincronización
                
                **¿Desea continuar?**
                """)
                
                if st.button("✅ Confirmar Bajada a Desarrollo", key="confirm_bajar"):
                    with st.spinner("Descargando desde la nube..."):
                        try:
                            import pivote_datos
                            resultados = pivote_datos.traer_todas_tablas_desde_nube()
                            
                            st.success("✅ Descarga completada")
                            
                            for resultado in resultados:
                                if resultado['exito']:
                                    st.success(f"📊 {resultado['tabla']}: {resultado['mensaje']}")
                                else:
                                    st.error(f"❌ {resultado['tabla']}: {resultado['mensaje']}")
                                    
                        except Exception as e:
                            st.error(f"❌ Error en descarga: {e}")
        
        # Mostrar último log de sincronización
        st.divider()
        st.subheader("📜 Historial de Sincronización")
        
        try:
            import pivote_datos
            logs = pivote_datos.obtener_ultima_sincronizacion()
            
            if logs is not None and len(logs) > 0:
                st.dataframe(logs, use_container_width=True)
            else:
                st.info("No hay registros de sincronización")
                
        except Exception as e:
            st.error(f"Error obteniendo logs: {e}")
        
        st.header("⚙️ Gestión de Ambientes (ITIL)")
        st.error("🔒 Esta sección está disponible únicamente para el administrador principal (angelher@gmail.com)")
        mostrar_mensaje_restringido()
