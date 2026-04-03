"""
VERIFICACIÓN DE USUARIO - SICADFOC 2026
Script para verificar la estructura y datos del usuario
"""
from database import get_engine_local
from sqlalchemy import text

def check_usuario_system():
    """Verifica el estado del sistema de usuarios"""
    
    engine = get_engine_local()
    
    with engine.connect() as conn:
        print("=== VERIFICACIÓN DE USUARIO ===")
        
        # 1. Verificar estructura de tabla usuario
        print("\n1. ESTRUCTURA DE TABLA USUARIO:")
        result = conn.execute(text("PRAGMA table_info(usuario)")).fetchall()
        for col in result:
            print(f"   - {col[1]} ({col[2]})")
        
        # 2. Verificar usuario administrador
        print("\n2. USUARIO ADMINISTRADOR:")
        result = conn.execute(text("""
            SELECT * FROM usuario 
            WHERE email = 'angel_hernandez137@hotmail.com'
        """)).fetchall()
        
        for user in result:
            print(f"   - ID: {user[0]}")
            print(f"   - Login: {user[1]}")
            print(f"   - Email: {user[2]}")
            print(f"   - Rol: {user[3]}")
            print(f"   - Contraseña: {user[4]}")
            print(f"   - Activo: {user[5]}")
            print(f"   - Correo verificado: {user[6]}")
            print(f"   - ID Persona: {user[7]}")
        
        # 3. Verificar todos los usuarios
        print("\n3. TODOS LOS USUARIOS:")
        result = conn.execute(text("""
            SELECT id, login, email, rol, activo 
            FROM usuario 
            LIMIT 5
        """)).fetchall()
        
        for user in result:
            print(f"   - ID: {user[0]}, Login: {user[1]}, Email: {user[2]}, Rol: {user[3]}, Activo: {user[4]}")

if __name__ == "__main__":
    check_usuario_system()
