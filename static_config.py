"""
CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS PARA RENDER
Configuración para servir CSS y otros recursos estáticos en producción
DBA Senior & Full-Stack - WindSurf
"""

import os
from pathlib import Path

# Obtener la ruta base del proyecto
BASE_DIR = Path(__file__).parent

# Configuración de archivos estáticos
STATIC_DIR = BASE_DIR / "ui" / "css"
ASSETS_DIR = BASE_DIR / "ui" / "assets"

# Mapeo de archivos estáticos
STATIC_FILES = {
    "css/diseños_streamlit.css": str(STATIC_DIR / "diseños_streamlit.css"),
    "images/iujo-logo.png": str(ASSETS_DIR / "iujo-logo.png"),
    "images/IUJO-Sede.png": str(ASSETS_DIR / "IUJO-Sede.png"),
}

def get_static_file_path(file_path):
    """
    Obtiene la ruta absoluta de un archivo estático
    Args:
        file_path (str): Ruta relativa del archivo estático
    Returns:
        str: Ruta absoluta del archivo
    """
    if file_path in STATIC_FILES:
        return STATIC_FILES[file_path]
    
    # Buscar en directorios estáticos
    full_path = BASE_DIR / file_path
    if full_path.exists():
        return str(full_path)
    
    return None

def serve_static_file(file_path):
    """
    Sirve un archivo estático para Streamlit/Render
    Args:
        file_path (str): Ruta del archivo estático
    Returns:
        str: Contenido del archivo o None si no existe
    """
    full_path = get_static_file_path(file_path)
    
    if full_path and os.path.exists(full_path):
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error leyendo archivo estático {file_path}: {e}")
            return None
    
    return None

def get_css_content(css_file="css/diseños_streamlit.css"):
    """
    Obtiene el contenido de un archivo CSS
    Args:
        css_file (str): Nombre del archivo CSS
    Returns:
        str: Contenido CSS formateado o None
    """
    content = serve_static_file(css_file)
    
    if content:
        return f"<style>{content}</style>"
    
    return None

def verify_static_files():
    """
    Verifica que todos los archivos estáticos necesarios existan
    Returns:
        dict: Estado de los archivos estáticos
    """
    status = {
        "css_files": {},
        "image_files": {},
        "total_files": len(STATIC_FILES),
        "found_files": 0,
        "missing_files": []
    }
    
    for file_path, full_path in STATIC_FILES.items():
        exists = os.path.exists(full_path)
        status["found_files"] += 1 if exists else 0
        
        if not exists:
            status["missing_files"].append(file_path)
        
        # Clasificar por tipo
        if file_path.endswith('.css'):
            status["css_files"][file_path] = exists
        elif file_path.endswith(('.png', '.jpg', '.jpeg', '.svg')):
            status["image_files"][file_path] = exists
    
    return status

def setup_static_environment():
    """
    Configura el entorno para producción en Render
    """
    # Verificar archivos estáticos
    status = verify_static_files()
    
    print("🔍 Verificación de archivos estáticos:")
    print(f"   📁 Total archivos: {status['total_files']}")
    print(f"   ✅ Archivos encontrados: {status['found_files']}")
    print(f"   ❌ Archivos faltantes: {len(status['missing_files'])}")
    
    if status['missing_files']:
        print(f"   📋 Archivos faltantes: {status['missing_files']}")
    
    # Verificar directorios
    directories = [STATIC_DIR, ASSETS_DIR]
    print("\n📁 Verificación de directorios:")
    
    for directory in directories:
        exists = directory.exists()
        print(f"   {'✅' if exists else '❌'} {directory}: {'Existe' if exists else 'No existe'}")
        
        if exists:
            file_count = len(list(directory.glob("*")))
            print(f"      📄 Archivos en directorio: {file_count}")
    
    return status

# Configuración para producción
PRODUCTION_CONFIG = {
    "static_url": "/static",
    "css_directory": "ui/css",
    "assets_directory": "ui/assets",
    "default_css": "diseños_streamlit.css",
    "cache_control": "public, max-age=31536000",  # 1 año
    "compression": True
}
