#!/usr/bin/env python3
"""
SICADFOC 2026 - Sistema de Estilos Dark-Mode Institucional
Modo Oscuro Moderno con Glassmorphism y Diseño Responsivo
Instituto Universitario Jesús Obrero
"""

def get_dark_modern_styles():
    """
    Retorna CSS completo para diseño Dark-Mode Institucional
    Implementa Glassmorphism, fondo oscuro y diseño responsivo
    """
    return """
    <style>
    /* Variables de Color - Dark Mode Institucional */
    :root {
        --fondo-principal: #0F0F0F;
        --fondo-secundario: #1A1A1A;
        --fondo-terciario: #252525;
        --fondo-glass: rgba(255, 255, 255, 0.05);
        --texto-principal: #E0E0E0;
        --texto-secundario: #B0B0B0;
        --texto-inverso: #0F0F0F;
        --borde: #333333;
        --borde-activo: #444444;
        --rojo-institucional: #AA1914;
        --rojo-institucional-hover: #CC1F1A;
        --sombra: rgba(0, 0, 0, 0.3);
        --sombra-glass: rgba(0, 0, 0, 0.1);
        --azul-claro: #1E3A5F;
        --verde-claro: #0F4C0F;
        --rojo-claro: #3D0A0A;
        --sidebar-bg: #1A1A1A;
        --accent-color: #AA1914;
        --accent-hover: #CC1F1A;
    }
    
    /* Estilos Globales */
    body {
        background: linear-gradient(135deg, var(--fondo-principal) 0%, var(--fondo-secundario) 100%);
        color: var(--texto-principal);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        margin: 0;
        padding: 0;
        min-height: 100vh;
    }
    
    /* Fondo con imagen institucional */
    .stApp {
        background: linear-gradient(135deg, var(--fondo-principal) 0%, var(--fondo-secundario) 100%);
        background-attachment: fixed;
        background-position: center;
        background-repeat: no-repeat;
        background-size: cover;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: url('./IUJO-Sede.png') center/cover no-repeat;
        filter: brightness(0.4);
        z-index: -1;
        opacity: 0.3;
    }
    
    /* Sidebar - Modo Oscuro */
    .stSidebar {
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--borde);
        box-shadow: 2px 0 10px var(--sombra);
    }
    
    .stSidebar .stMarkdown {
        color: var(--texto-principal) !important;
    }
    
    /* Glassmorphism - Contenedores principales */
    .stApp > div > div > div > div > div > div {
        background: var(--fondo-glass) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px var(--sombra-glass) !important;
        margin: 0.5rem !important;
        padding: 1rem !important;
    }
    
    /* Formularios - Glassmorphism */
    .stForm {
        background: var(--fondo-glass) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px var(--sombra-glass) !important;
        padding: 1.5rem !important;
    }
    
    /* Campos de entrada - Dark Mode */
    .stTextInput > div > div > input,
    .stSelectbox > div > select,
    .stDateInput > div > input,
    .stTextArea > div > textarea,
    .stNumberInput > div > input {
        background: var(--fondo-terciario) !important;
        color: var(--texto-principal) !important;
        border: 1px solid var(--borde) !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > select:focus,
    .stDateInput > div > input:focus,
    .stTextArea > div > textarea:focus {
        border-color: var(--accent-color) !important;
        outline: none !important;
        box-shadow: 0 0 0 3px var(--accent-color) !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > textarea::placeholder {
        color: var(--texto-secundario) !important;
    }
    
    /* Botones - Rojo Institucional */
    .stButton > button {
        background: var(--rojo-institucional) !important;
        color: var(--texto-principal) !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px var(--sombra) !important;
    }
    
    .stButton > button:hover {
        background: var(--rojo-institucional-hover) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px var(--sombra) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Botones primarios */
    .stButton[kind="primary"] > button {
        background: var(--accent-color) !important;
        border: 2px solid var(--accent-color) !important;
    }
    
    .stButton[kind="primary"] > button:hover {
        background: var(--accent-hover) !important;
        border-color: var(--accent-hover) !important;
    }
    
    /* Métricas - Glassmorphism */
    .metric-container {
        background: var(--fondo-glass) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        text-align: center !important;
        box-shadow: 0 8px 32px var(--sombra-glass) !important;
    }
    
    .metric-label {
        color: var(--texto-secundario) !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .metric-value {
        color: var(--texto-principal) !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
    }
    
    /* DataFrames - Dark Mode */
    .dataframe {
        background: var(--fondo-glass) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        overflow-x: auto !important;
        box-shadow: 0 8px 32px var(--sombra-glass) !important;
    }
    
    .dataframe th {
        background: var(--fondo-terciario) !important;
        color: var(--texto-principal) !important;
        border: 1px solid var(--borde) !important;
        padding: 0.75rem !important;
        font-weight: 600 !important;
    }
    
    .dataframe td {
        background: var(--fondo-secundario) !important;
        color: var(--texto-principal) !important;
        border: 1px solid var(--borde) !important;
        padding: 0.75rem !important;
    }
    
    .dataframe tr:hover td {
        background: var(--fondo-terciario) !important;
    }
    
    /* Tabs - Dark Mode */
    .stTabs [data-baseweb="st"] {
        background: var(--fondo-glass) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px var(--sombra-glass) !important;
    }
    
    .stTabs [data-baseweb="st"] > div > div > div > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    .stTabs [data-baseweb="st"] > div > div > div > div > div {
        color: var(--texto-principal) !important;
        background: var(--fondo-terciario) !important;
        border: 1px solid var(--borde) !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        margin: 0.25rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [data-baseweb="st"] > div > div > div > div > div:hover {
        background: var(--accent-color) !important;
        border-color: var(--accent-color) !important;
    }
    
    /* Selectbox - Dark Mode */
    .stSelectbox > div > div {
        background: var(--fondo-terciario) !important;
        border: 1px solid var(--borde) !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox > div > div > div {
        background: var(--fondo-secundario) !important;
        color: var(--texto-principal) !important;
    }
    
    /* Checkbox - Dark Mode */
    .stCheckbox > div > label {
        color: var(--texto-principal) !important;
    }
    
    /* Radio - Dark Mode */
    .stRadio > div > label {
        color: var(--texto-principal) !important;
    }
    
    /* Alertas y Mensajes */
    .stAlert {
        background: var(--fondo-glass) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px var(--sombra-glass) !important;
    }
    
    .stAlert > div {
        color: var(--texto-principal) !important;
    }
    
    /* Progress Bar */
    .stProgress .progress-bar {
        background: var(--accent-color) !important;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: var(--accent-color) !important;
    }
    
    /* Expander */
    .stExpander {
        background: var(--fondo-glass) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px var(--sombra-glass) !important;
    }
    
    .stExpander > div > div > div > span {
        color: var(--texto-principal) !important;
    }
    
    /* Sidebar - Contenido */
    .stSidebar .stMarkdown h1,
    .stSidebar .stMarkdown h2,
    .stSidebar .stMarkdown h3 {
        color: var(--texto-principal) !important;
    }
    
    .stSidebar .stMarkdown p,
    .stSidebar .stMarkdown span {
        color: var(--texto-secundario) !important;
    }
    
    /* Scrollbar - Dark Mode */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--fondo-secundario);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--borde-activo);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--texto-secundario);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .stApp > div > div > div > div > div > div {
            margin: 0.25rem !important;
            padding: 0.75rem !important;
        }
        
        .stForm {
            padding: 1rem !important;
        }
        
        .stButton > button {
            padding: 0.5rem 1rem !important;
            font-size: 0.9rem !important;
        }
        
        .metric-container {
            padding: 1rem !important;
        }
    }
    
    @media (max-width: 480px) {
        .stApp > div > div > div > div > div > div {
            margin: 0.125rem !important;
            padding: 0.5rem !important;
        }
        
        .stForm {
            padding: 0.75rem !important;
        }
        
        .stButton > button {
            padding: 0.4rem 0.8rem !important;
            font-size: 0.8rem !important;
        }
        
        .dataframe {
            font-size: 0.8rem !important;
        }
    }
    
    /* Animaciones */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); }
        to { transform: translateX(0); }
    }
    
    .stApp > div > div > div > div > div > div {
        animation: fadeIn 0.5s ease-out;
    }
    
    .stSidebar {
        animation: slideIn 0.3s ease-out;
    }
    </style>
    """

def get_login_logo_html():
    """
    Retorna HTML para logo en pantalla de login con rutas relativas
    """
    return """
    <div style="text-align: center; margin-bottom: 2rem; animation: fadeIn 0.8s ease-out;">
        <img src="./Logo_IUJO.png" 
             alt="Logo IUJO" 
             style="max-width: 150px; height: auto; border-radius: 8px; box-shadow: 0 4px 12px var(--sombra);">
        <h1 style="color: var(--texto-principal); margin: 0.5rem 0; font-weight: 700;">
            SICADFOC 2026
        </h1>
        <p style="color: var(--texto-secundario); font-size: 0.9rem; margin: 0;">
            Instituto Universitario Jesús Obrero
        </p>
    </div>
    """

def get_sidebar_logo_html():
    """
    Retorna HTML para logo en sidebar con rutas relativas
    """
    return """
    <div style="text-align: center; padding: 1rem; border-bottom: 1px solid var(--borde); animation: slideIn 0.5s ease-out;">
        <img src="./Logo_IUJO.png" 
             alt="Logo IUJO" 
             style="max-width: 120px; height: auto; border-radius: 6px;">
        <div style="margin-top: 0.5rem;">
            <strong style="color: var(--texto-principal); font-size: 0.8rem; display: block;">IUJO</strong>
            <small style="color: var(--texto-secundario); font-size: 0.7rem; display: block; margin-top: 0.25rem;">
                Instituto Universitario Jesús Obrero
            </small>
        </div>
    </div>
    """

def get_global_styles(hide_sidebar=False):
    """
    Retorna CSS global para toda la aplicación
    """
    css = get_dark_modern_styles()
    
    if hide_sidebar:
        css += """
        .stSidebar {
            visibility: hidden;
            }
        """
    
    return css

def get_background_image_css():
    """
    Retorna CSS específico para fondo con imagen institucional
    """
    return """
    <style>
    .stApp {
        background: linear-gradient(135deg, rgba(15, 15, 15, 0.95) 0%, rgba(26, 26, 26, 0.95) 100%);
        background-attachment: fixed;
        background-position: center;
        background-repeat: no-repeat;
        background-size: cover;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: url('./IUJO-Sede.png') center/cover no-repeat;
        filter: brightness(0.4);
        z-index: -1;
        opacity: 0.3;
    }
    </style>
    """
