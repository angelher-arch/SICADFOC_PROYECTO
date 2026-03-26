"""
CONFIGURACIÓN DE PRODUCCIÓN - OPTIMIZACIONES PARA RENDER
DBA Senior - WindSurf
"""
import os
import streamlit as st
from database import get_engine_local, crear_tablas_sistema

def configure_production():
    """Configurar Streamlit para producción"""
    
    # Desactivar analytics de Streamlit
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    # Configurar para producción
    if 'render.com' in os.getenv('DATABASE_URL', ''):
        st.set_page_config(
            page_title="SICADFOC 2026",
            page_icon="🎓",
            layout="centered",
            initial_sidebar_state="collapsed"
        )
        
        # Desactivar warnings en producción
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.set_option('deprecation.showfileUploaderEncoding', False)

def setup_database_production():
    """Configurar base de datos para producción"""
    try:
        engine = get_engine_local()
        
        # Forzar creación de tablas en producción
        with engine.connect() as conn:
            crear_tablas_sistema(engine)
            
            # Verificar conexión
            conn.execute(text("SELECT 1"))
            
        print("✅ Base de datos producción configurada")
        return True
        
    except Exception as e:
        print(f"❌ Error configurando BD: {e}")
        return False

def optimize_memory_usage():
    """Optimizar uso de memoria para producción"""
    
    # Configurar cache de Streamlit
    if hasattr(st, 'cache_data'):
        @st.cache_data(ttl=3600)  # Cache por 1 hora
        def get_cached_data():
            return {"status": "cached"}
    
    # Limitar tamaño de uploads
    st.set_option('server.maxUploadSize', 200)  # 200MB max

def setup_error_handling():
    """Configurar manejo de errores para producción"""
    
    # Capturar errores silenciosamente
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Desactivar traceback en producción
    st.set_option('client.showErrorDetails', False)

def check_production_environment():
    """Verificar que estamos en producción"""
    
    indicators = [
        'render.com' in os.getenv('DATABASE_URL', ''),
        'RENDER' in os.getenv('PATH', ''),
        os.getenv('APP_ENVIRONMENT') == 'production'
    ]
    
    return any(indicators)

# Aplicar configuración si estamos en producción
if check_production_environment():
    configure_production()
    optimize_memory_usage()
    setup_error_handling()
