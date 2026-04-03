"""
VERIFICACIÓN DE ESQUEMA - SICADFOC 2026
Script para verificar la estructura de tablas
"""
from database import get_engine_local
from sqlalchemy import text

def check_persona_schema():
    """Verificar esquema de tabla persona"""
    engine = get_engine_local()
    
    with engine.connect() as conn:
        # Verificar estructura de tabla persona
        result = conn.execute(text("PRAGMA table_info(persona)")).fetchall()
        
        print("=== ESTRUCTURA TABLA PERSONA ===")
        for row in result:
            print(f"Columna: {row[1]}, Tipo: {row[2]}, NotNull: {row[3]}, Default: {row[4]}")
        
        # Verificar si existe la tabla
        table_check = conn.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='persona'
        """)).fetchone()
        
        if table_check:
            print("\n✅ Tabla persona existe")
        else:
            print("\n❌ Tabla persona no existe")

def check_usuario_schema():
    """Verificar esquema de tabla usuario"""
    engine = get_engine_local()
    
    with engine.connect() as conn:
        # Verificar estructura de tabla usuario
        result = conn.execute(text("PRAGMA table_info(usuario)")).fetchall()
        
        print("\n=== ESTRUCTURA TABLA USUARIO ===")
        for row in result:
            print(f"Columna: {row[1]}, Tipo: {row[2]}, NotNull: {row[3]}, Default: {row[4]}")
        
        # Verificar si existe la tabla
        table_check = conn.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='usuario'
        """)).fetchone()
        
        if table_check:
            print("\n✅ Tabla usuario existe")
        else:
            print("\n❌ Tabla usuario no existe")

def check_data():
    """Verificar datos existentes"""
    engine = get_engine_local()
    
    with engine.connect() as conn:
        # Verificar datos en persona
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM persona")).fetchone()
            print(f"\n=== DATOS PERSONA ===")
            print(f"Total registros: {result[0]}")
            
            if result[0] > 0:
                sample = conn.execute(text("SELECT * FROM persona LIMIT 3")).fetchall()
                print("Muestra de datos:")
                for row in sample:
                    print(f"  {row}")
        except Exception as e:
            print(f"Error consultando persona: {e}")
        
        # Verificar datos en usuario
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM usuario")).fetchone()
            print(f"\n=== DATOS USUARIO ===")
            print(f"Total registros: {result[0]}")
            
            if result[0] > 0:
                sample = conn.execute(text("SELECT id, login, email, rol FROM usuario LIMIT 3")).fetchall()
                print("Muestra de datos:")
                for row in sample:
                    print(f"  {row}")
        except Exception as e:
            print(f"Error consultando usuario: {e}")

if __name__ == "__main__":
    check_persona_schema()
    check_usuario_schema()
    check_data()
