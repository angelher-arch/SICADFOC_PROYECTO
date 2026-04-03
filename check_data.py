"""
VERIFICACIÓN DE DATOS - SICADFOC 2026
Script simple para verificar datos existentes
"""
from database import get_engine_local
from sqlalchemy import text

def check_data_simple():
    """Verificar datos existentes de forma simple"""
    engine = get_engine_local()
    
    with engine.connect() as conn:
        # Verificar datos en persona
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM persona")).fetchone()
            print(f"Total registros persona: {result[0]}")
            
            if result[0] > 0:
                sample = conn.execute(text("SELECT id_persona, cedula, nombre, apellido FROM persona LIMIT 3")).fetchall()
                print("Muestra datos persona:")
                for row in sample:
                    print(f"  ID: {row[0]}, Cedula: {row[1]}, Nombre: {row[2]}, Apellido: {row[3]}")
        except Exception as e:
            print(f"Error consultando persona: {e}")
        
        # Verificar datos en usuario
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM usuario")).fetchone()
            print(f"Total registros usuario: {result[0]}")
            
            if result[0] > 0:
                sample = conn.execute(text("SELECT id, login, email, rol FROM usuario LIMIT 3")).fetchall()
                print("Muestra datos usuario:")
                for row in sample:
                    print(f"  ID: {row[0]}, Login: {row[1]}, Email: {row[2]}, Rol: {row[3]}")
        except Exception as e:
            print(f"Error consultando usuario: {e}")

if __name__ == "__main__":
    check_data_simple()
