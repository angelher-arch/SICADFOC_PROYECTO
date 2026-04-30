"""
SICADFOC 2026 - Estilos Globales de Formularios
Función centralizada para aplicar estilos de legibilidad a todos los formularios del sistema
"""

def aplicar_estilo_formularios():
    """
    Aplica estilos globales de legibilidad a todos los formularios del proyecto
    Función mandatoria para asegurar consistencia visual en todo el sistema
    """
    import streamlit as st
    
    st.markdown("""
    <style>
    /* ESTILOS GLOBALES DE FORMULARIOS - SICADFOC 2026 */
    
    /* CAMPOS DE ENTRADA - FUENTE OSCURA OBLIGATORIA */
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
        color: #1E293B !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
        color: #1E293B !important;
        background-color: #FFFFFF !important;
        border-color: #2563EB !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* PLACEHOLDERS - GRIS OSCURA LEGIBLE */
    .stTextInput input::placeholder, .stNumberInput input::placeholder, .stTextArea textarea::placeholder {
        color: #64748B !important;
        font-weight: 400 !important;
        opacity: 1 !important;
    }
    
    /* ETIQUETAS DE CAMPOS - CONTRASTE ALTO */
    .stWidgetLabel, .stForm label, .stTextInput label, .stNumberInput label, .stSelectbox label, .stTextArea label {
        color: #0F172A !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        margin-bottom: 6px !important;
        display: block !important;
        text-shadow: none !important;
    }
    
    /* CONTENEDORES DE FORMULARIO - FONDO CON OPACIDAD ADECUADA */
    .stForm, .stForm > div {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        padding: 20px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* BOTONES DE ACCIÓN PRINCIPAL - ESTILO INSTITUCIONAL */
    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #AA1914 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background-color: #8B1510 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(170, 25, 20, 0.3) !important;
    }
    
    /* BOTONES SECUNDARIOS */
    div[data-testid="stButton"] > button:not([kind="primary"]) {
        background-color: #F8FAFC !important;
        color: #1E293B !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 6px !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease !important;
    }
    
    div[data-testid="stButton"] > button:not([kind="primary"]):hover {
        background-color: #F1F5F9 !important;
        border-color: #CBD5E1 !important;
    }
    
    /* CHECKBOXES Y RADIO BUTTONS */
    .stCheckbox label, .stRadio label {
        color: #1E293B !important;
        font-weight: 500 !important;
        font-size: 14px !important;
    }
    
    /* SELECTBOX - ESTILO ESPECÍFICO */
    .stSelectbox[data-baseweb="select"] > div > div {
        color: #1E293B !important;
        background-color: #FFFFFF !important;
    }
    
    /* MENSAJES DE ERROR Y ÉXITO */
    .stException, .stAlert {
        color: #1E293B !important;
        font-weight: 500 !important;
    }
    
    /* TÍTULOS DE FORMULARIO */
    .stForm h1, .stForm h2, .stForm h3, .stForm h4 {
        color: #0F172A !important;
        font-weight: 700 !important;
        margin-bottom: 16px !important;
    }
    
    /* TEXTO DE AYUDA */
    .stHelpText {
        color: #64748B !important;
        font-size: 12px !important;
        font-weight: 400 !important;
    }
    
    /* SLIDERS */
    .stSlider label {
        color: #1E293B !important;
        font-weight: 600 !important;
    }
    
    /* DATE INPUTS */
    .stDateInput input {
        color: #1E293B !important;
        background-color: #FFFFFF !important;
    }
    
    /* TIME INPUTS */
    .stTimeInput input {
        color: #1E293B !important;
        background-color: #FFFFFF !important;
    }
    
    /* FILE UPLOADERS */
    .stFileUploader label {
        color: #1E293B !important;
        font-weight: 600 !important;
    }
    
    /* COLOR PICKERS */
    .stColorPicker label {
        color: #1E293B !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def aplicar_estilo_botones_principales():
    """
    Aplica estilo específico a botones de acción principal
    Para ser usado en conjunto con aplicar_estilo_formularios()
    """
    import streamlit as st
    
    st.markdown("""
    <style>
    /* BOTONES PRINCIPALES - ESTILO INSTITUCIONAL REFORZADO */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #AA1914 0%, #8B1510 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        box-shadow: 0 2px 4px rgba(170, 25, 20, 0.2) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #8B1510 0%, #6D100C 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 16px rgba(170, 25, 20, 0.3) !important;
    }
    
    div[data-testid="stButton"] > button[kind="primary"]:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 4px rgba(170, 25, 20, 0.2) !important;
    }
    
    /* EFECTO DE ONDA EN BOTONES PRINCIPALES */
    div[data-testid="stButton"] > button[kind="primary"]::before {
        content: "" !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        width: 0 !important;
        height: 0 !important;
        border-radius: 50% !important;
        background: rgba(255, 255, 255, 0.3) !important;
        transform: translate(-50%, -50%) !important;
        transition: width 0.6s, height 0.6s !important;
    }
    
    div[data-testid="stButton"] > button[kind="primary"]:hover::before {
        width: 300px !important;
        height: 300px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def aplicar_estilo_consistente_global():
    """
    Función combinada que aplica todos los estilos de forma global
    Uso recomendado al inicio de cada módulo con formularios
    """
    aplicar_estilo_formularios()
    aplicar_estilo_botones_principales()
