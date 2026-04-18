# Rutas de imágenes para CSS global
# Usar los assets institucionales IUJO

BACKGROUND_IUJO = "./assets/IUJO-Sede.png"

LOGO_IUJO = "./assets/Logo_IUJO.png"

def get_global_css():
    """CSS global con fondo translúcido y UI visible."""
    return f"""
    <style>
    html, body, #root, .stApp {{
        min-height: 100vh;
        margin: 0;
        padding: 0;
        background-image: linear-gradient(rgba(0, 0, 0, 0.45), rgba(0, 0, 0, 0.45)), url('{BACKGROUND_IUJO}');
        background-size: cover !important;
        background-position: center center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
        color: #FFFFFF !important;
    }}

    [data-testid='stAppViewContainer'] > .main {{
        background: rgba(0, 0, 0, 0.65) !important;
        border-radius: 24px !important;
        box-shadow: 0 24px 80px rgba(0, 0, 0, 0.45) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        padding: 1rem !important;
    }}

    .css-1lcbmhc.e1fqkh3o3, .block-container, .stForm {{
        background: rgba(0, 0, 0, 0.72) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 20px !important;
        position: relative;
        z-index: 1;
    }}

    .stButton > button, .stTextInput > div > div > input, .stSelectbox > div > div > select, .stTextArea > div > div > textarea {{
        color: #FFFFFF !important;
    }}

    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {{
        background: rgba(255, 255, 255, 0.12) !important;
        border: 1px solid rgba(255, 255, 255, 0.22) !important;
        color: #FFFFFF !important;
    }}

    [data-testid='stSidebar'] {{
        background: rgba(0, 0, 0, 0.82) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.16) !important;
    }}

    .stButton > button {{
        background: rgba(255, 255, 255, 0.18) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        color: #FFFFFF !important;
    }}

    h1, h2, h3, h4, h5, h6,
    p, span, div, label,
    .stMarkdown, .stText, .stTitle,
    .stHeader, .stSubheader,
    .stMetric, .stCaption,
    .stInfo, .stSuccess, .stWarning, .stError,
    .stDataFrame, .stTable {{
        color: #FFFFFF !important;
    }}
    </style>
    """
