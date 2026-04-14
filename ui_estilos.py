#!/usr/bin/env python3
# Módulo de Estilos UI - Diseño Neutro PowerPoint-like y Responsive

def get_css_iujo():
    """Retorna CSS neutro PowerPoint-like con diseño responsive"""
    return """
    <style>
    /* Colores Neutros PowerPoint-like */
    :root {
        --fondo-principal: #FFFFFF;
        --fondo-secundario: #F8F8F8;
        --texto-principal: #000000;
        --texto-secundario: #666666;
        --borde: #CCCCCC;
        --borde-activo: #999999;
        --sombra: rgba(0, 0, 0, 0.1);
        --azul-claro: #E6F3FF;
        --verde-claro: #E6FFE6;
        --rojo-claro: #FFE6E6;
        --amarillo-claro: #FFFFE6;
    }
    
    /* Estilos Generales */
    .stApp {
        background-color: var(--fondo-principal);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main .block-container {
        padding: 1rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Headers */
    .main h1 {
        color: var(--texto-principal);
        text-align: center;
        font-weight: 700;
        margin-bottom: 2rem;
        font-size: 2.5rem;
        border-bottom: 3px solid var(--borde);
        padding-bottom: 1rem;
    }
    
    .main h2 {
        color: var(--texto-principal);
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-size: 2rem;
        border-left: 5px solid var(--borde-activo);
        padding-left: 1rem;
    }
    
    .main h3 {
        color: var(--texto-principal);
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-size: 1.5rem;
    }
    
    /* Botones Principales */
    .stButton > button {
        background-color: var(--fondo-secundario);
        color: var(--texto-principal);
        border: 2px solid var(--borde);
        border-radius: 5px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        background-color: var(--borde);
        color: var(--fondo-principal);
        border-color: var(--borde-activo);
    }
    
    .stButton > button:active {
        background-color: var(--borde-activo);
    }
    
    /* Campos de Formulario */
    .stTextInput > div > div > input,
    .stSelectbox > div > select,
    .stDateInput > div > input,
    .stTextArea > div > textarea {
        background-color: var(--fondo-principal);
        border: 2px solid var(--borde);
        border-radius: 5px;
        padding: 0.75rem;
        color: var(--texto-principal);
        font-weight: 500;
        font-size: 1rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > select:focus,
    .stDateInput > div > input:focus,
    .stTextArea > div > textarea:focus {
        border-color: var(--borde-activo);
        outline: none;
        box-shadow: 0 0 5px var(--sombra);
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > textarea::placeholder {
        color: var(--texto-secundario);
    }
    
    /* Métricas */
    .metric-container {
        background-color: var(--fondo-principal);
        border: 2px solid var(--borde);
        border-radius: 5px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px var(--sombra);
    }
    
    .metric-label {
        color: var(--texto-secundario);
        font-weight: 600;
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        color: var(--texto-principal);
        font-weight: 700;
        font-size: 1.5rem;
    }
    
    /* DataFrames */
    .dataframe {
        background-color: var(--fondo-principal);
        border: 2px solid var(--borde);
        border-radius: 5px;
        overflow-x: auto;
        box-shadow: 0 2px 4px var(--sombra);
    }
    
    .dataframe th {
        background-color: var(--fondo-secundario);
        color: var(--texto-principal);
        font-weight: 600;
        text-align: left;
        padding: 0.75rem;
        border-bottom: 2px solid var(--borde);
    }
    
    .dataframe td {
        border-bottom: 1px solid var(--borde);
        padding: 0.75rem;
        color: var(--texto-principal);
    }
    
    .dataframe tr:hover {
        background-color: var(--fondo-secundario);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="true"] > div > div > div > div > div > ul {
        background-color: var(--fondo-principal);
        border-bottom: 2px solid var(--borde);
        padding: 0;
        margin: 0;
    }
    
    .stTabs [data-baseweb="true"] > div > div > div > div > div > ul > li {
        background-color: transparent;
        color: var(--texto-principal);
        border: none;
        padding: 0.75rem 1rem;
        margin: 0;
        font-weight: 500;
        transition: background-color 0.3s ease;
        cursor: pointer;
    }
    
    .stTabs [data-baseweb="true"] > div > div > div > div > div > ul > li:hover {
        background-color: var(--fondo-secundario);
    }
    
    .stTabs [data-baseweb="true"] > div > div > div > div > div > ul > li[data-testid="stTab"] {
        background-color: var(--borde-activo);
        color: var(--fondo-principal);
        border-radius: 5px 5px 0 0;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background-color: var(--verde-claro);
        color: #006400;
        border: 2px solid #90EE90;
        border-radius: 5px;
        padding: 1rem;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    .stError {
        background-color: var(--rojo-claro);
        color: #8B0000;
        border: 2px solid #FFB6C1;
        border-radius: 5px;
        padding: 1rem;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    .stWarning {
        background-color: var(--amarillo-claro);
        color: #8B8000;
        border: 2px solid #FFFF99;
        border-radius: 5px;
        padding: 1rem;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    .stInfo {
        background-color: var(--azul-claro);
        color: #00008B;
        border: 2px solid #ADD8E6;
        border-radius: 5px;
        padding: 1rem;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    /* Sidebar */
    .css-1l4ldy {
        background-color: var(--fondo-secundario);
        border-right: 2px solid var(--borde);
    }
    
    /* Responsive Design */
    @media (max-width: 1200px) {
        .main .block-container {
            max-width: 100%;
            padding: 1rem;
        }
    }
    
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.5rem;
        }
        
        .main h1 {
            font-size: 2rem;
            margin-bottom: 1rem;
        }
        
        .main h2 {
            font-size: 1.5rem;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }
        
        .main h3 {
            font-size: 1.25rem;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }
        
        .stButton > button {
            padding: 1rem;
            font-size: 0.9rem;
        }
        
        .stTextInput > div > div > input,
        .stSelectbox > div > select,
        .stDateInput > div > input,
        .stTextArea > div > textarea {
            padding: 1rem;
            font-size: 16px; /* Previene zoom en móviles */
        }
        
        .dataframe {
            font-size: 0.875rem;
        }
        
        .dataframe th,
        .dataframe td {
            padding: 0.5rem;
        }
        
        .metric-container {
            padding: 0.75rem;
        }
        
        .metric-label {
            font-size: 0.8rem;
        }
        
        .metric-value {
            font-size: 1.25rem;
        }
        
        /* Columnas responsive */
        .stColumns > div {
            margin-bottom: 1rem;
        }
    }
    
    @media (max-width: 480px) {
        .main h1 {
            font-size: 1.5rem;
            padding-bottom: 0.5rem;
        }
        
        .main h2 {
            font-size: 1.25rem;
            padding-left: 0.5rem;
        }
        
        .main h3 {
            font-size: 1.125rem;
        }
        
        .stButton > button {
            padding: 1.25rem;
            font-size: 0.8rem;
        }
        
        .dataframe {
            font-size: 0.75rem;
        }
        
        .dataframe th,
        .dataframe td {
            padding: 0.375rem;
        }
        
        .metric-container {
            padding: 0.5rem;
        }
        
        .metric-label {
            font-size: 0.75rem;
        }
        
        .metric-value {
            font-size: 1rem;
        }
    }
    
    /* Animaciones sutiles */
    .main > div {
        animation: fadeIn 0.3s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Scrollbar simple */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--fondo-secundario);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--borde-activo);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--texto-secundario);
    }
    </style>
    """

def get_css_login():
    """CSS específico para pantalla de login con diseño neutro"""
    return """
    <style>
    .login-container {
        max-width: 500px;
        margin: 2rem auto;
        padding: 2rem;
        background: var(--fondo-principal);
        border: 2px solid var(--borde);
        border-radius: 10px;
        box-shadow: 0 4px 8px var(--sombra);
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-header h1 {
        color: var(--rojo-principal);
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .login-form {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .login-button {
        background: linear-gradient(135deg, var(--rojo-principal), var(--rojo-secundario));
        color: var(--texto-claro);
        border: none;
        border-radius: 8px;
        padding: 1rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .login-button:hover {
        background: linear-gradient(135deg, var(--rojo-secundario), var(--rojo-principal));
        transform: translateY(-2px);
        box-shadow: 0 6px 12px var(--sombra);
    }
    </style>
    """
