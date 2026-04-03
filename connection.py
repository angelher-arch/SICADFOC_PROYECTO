"""
CONEXIÓN A BASE DE DATOS - SICADFOC 2026
Módulo independiente para conexión y engine de base de datos
DBA Senior & Full-Stack - WindSurf
"""
import os
import sqlite3
from sqlalchemy import create_engine, text, event
from sqlalchemy.engine import Engine
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variables globales para conexión
_engine = None
_engine_espejo = None

def get_engine_local():
    """
    Obtiene el engine de la base de datos local (SQLite)
    Returns:
        Engine: Engine de SQLAlchemy para la base de datos local
    """
    global _engine
    
    if _engine is None:
        # Determinar la ruta de la base de datos
        db_path = os.path.join(os.path.dirname(__file__), '..', 'foc26_limpio.db')
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Crear engine SQLite
        _engine = create_engine(f'sqlite:///{db_path}', echo=False)
        
        # Configurar foreign keys para SQLite
        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        
        logger.info(f"✅ Conexión SQLite establecida: {db_path}")
    
    return _engine

def get_engine_espejo():
    """
    Obtiene el engine de la base de datos espejo (PostgreSQL en producción)
    Returns:
        Engine: Engine de SQLAlchemy para la base de datos espejo
    """
    global _engine_espejo
    
    if _engine_espejo is None:
        # Verificar si estamos en producción (Render)
        database_url = os.getenv('DATABASE_URL')
        
        if database_url and 'render.com' in database_url:
            # Producción - PostgreSQL en Render
            try:
                _engine_espejo = create_engine(database_url, echo=False)
                logger.info("✅ Conexión PostgreSQL (Render) establecida")
            except Exception as e:
                logger.error(f"❌ Error conectando a PostgreSQL: {e}")
                # Fallback a SQLite local
                _engine_espejo = get_engine_local()
        else:
            # Desarrollo - usar SQLite local
            _engine_espejo = get_engine_local()
            logger.info("ℹ️ Usando SQLite local como espejo")
    
    return _engine_espejo

def get_database_url():
    """
    Obtiene la URL de la base de datos actual
    Returns:
        str: URL de la base de datos
    """
    engine = get_engine_local()
    return str(engine.url).replace('sqlite:///', 'sqlite:///')

def test_connection():
    """
    Prueba la conexión a la base de datos
    Returns:
        bool: True si la conexión es exitosa, False en caso contrario
    """
    try:
        engine = get_engine_local()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            return result[0] == 1
    except Exception as e:
        logger.error(f"❌ Error en prueba de conexión: {e}")
        return False

def get_database_info():
    """
    Obtiene información sobre la base de datos
    Returns:
        dict: Información de la base de datos
    """
    try:
        engine = get_engine_local()
        
        # Obtener información básica
        info = {
            'database_type': 'SQLite',
            'database_url': str(engine.url),
            'connection_test': test_connection(),
            'tables': []
        }
        
        # Obtener lista de tablas
        with engine.connect() as conn:
            tables = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)).fetchall()
            
            info['tables'] = [table[0] for table in tables]
            info['table_count'] = len(info['tables'])
        
        return info
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo información de BD: {e}")
        return {
            'database_type': 'SQLite',
            'database_url': 'Error',
            'connection_test': False,
            'tables': [],
            'table_count': 0,
            'error': str(e)
        }

def reset_connections():
    """
    Resetea las conexiones a la base de datos
    Útil para pruebas o cambios de configuración
    """
    global _engine, _engine_espejo
    
    if _engine:
        _engine.dispose()
        _engine = None
    
    if _engine_espejo:
        _engine_espejo.dispose()
        _engine_espejo = None
    
    logger.info("🔄 Conexiones a base de datos reseteadas")

# Engine global para compatibilidad con código existente
engine = get_engine_local()

if __name__ == "__main__":
    # Pruebas del módulo de conexión
    print("🧪 Pruebas del módulo de conexión")
    print("=" * 50)
    
    # Probar conexión
    print("🔍 Probando conexión...")
    if test_connection():
        print("✅ Conexión exitosa")
    else:
        print("❌ Conexión fallida")
    
    # Mostrar información
    print("\n📊 Información de la base de datos:")
    info = get_database_info()
    for key, value in info.items():
        if key != 'tables':
            print(f"  {key}: {value}")
    
    print(f"\n📋 Tablas ({info['table_count']}):")
    for table in info['tables']:
        print(f"  • {table}")
    
    print(f"\n🔗 URL: {info['database_url']}")
