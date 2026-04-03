"""
VERIFICACIÓN DE ROLES Y PERMISOS - SICADFOC 2026
Script para diagnosticar problemas con el sistema de roles
"""
from database import get_engine_local
from sqlalchemy import text

def check_roles_system():
    """Verifica el estado del sistema de roles"""
    
    engine = get_engine_local()
    
    with engine.connect() as conn:
        print("=== VERIFICACIÓN DE ROLES Y PERMISOS ===")
        
        # 1. Verificar tablas relacionadas con roles
        print("\n1. TABLAS RELACIONADAS CON ROLES:")
        result = conn.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND (name LIKE '%rol%' OR name LIKE '%permiso%')
            ORDER BY name
        """)).fetchall()
        
        for table in result:
            print(f"   - {table[0]}")
        
        # 2. Verificar estructura de tabla rol
        print("\n2. ESTRUCTURA DE TABLA ROL:")
        try:
            result = conn.execute(text("PRAGMA table_info(rol)")).fetchall()
            for col in result:
                print(f"   - {col[1]} ({col[2]})")
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # 3. Verificar estructura de tabla permiso
        print("\n3. ESTRUCTURA DE TABLA PERMISO:")
        try:
            result = conn.execute(text("PRAGMA table_info(permiso)")).fetchall()
            for col in result:
                print(f"   - {col[1]} ({col[2]})")
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # 4. Verificar estructura de tabla rol_permiso
        print("\n4. ESTRUCTURA DE TABLA ROL_PERMISO:")
        try:
            result = conn.execute(text("PRAGMA table_info(rol_permiso)")).fetchall()
            for col in result:
                print(f"   - {col[1]} ({col[2]})")
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # 5. Verificar roles existentes
        print("\n5. ROLES EXISTENTES:")
        try:
            result = conn.execute(text("SELECT * FROM rol")).fetchall()
            for rol in result:
                print(f"   - ID: {rol[0]}, Nombre: {rol[1]}, Nivel: {rol[2]}")
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # 6. Verificar permisos existentes
        print("\n6. PERMISOS EXISTENTES:")
        try:
            result = conn.execute(text("SELECT * FROM permiso LIMIT 10")).fetchall()
            for perm in result:
                print(f"   - ID: {perm[0]}, Nombre: {perm[1]}, Módulo: {perm[2]}")
            print(f"   ... (mostrando primeros 10 de {len(conn.execute(text('SELECT COUNT(*) FROM permiso')).fetchone()[0])} permisos)")
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # 7. Verificar rol_permiso existentes
        print("\n7. ASIGNACIONES ROL-PERMISO:")
        try:
            result = conn.execute(text("SELECT * FROM rol_permiso LIMIT 10")).fetchall()
            for rp in result:
                print(f"   - Rol ID: {rp[0]}, Permiso ID: {rp[1]}")
            print(f"   ... (mostrando primeras 10 asignaciones)")
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # 8. Verificar usuario administrador
        print("\n8. USUARIO ADMINISTRADOR:")
        try:
            result = conn.execute(text("""
                SELECT u.id, u.rol, u.id_rol, r.nombre_rol 
                FROM usuario u 
                LEFT JOIN rol r ON u.id_rol = r.id_rol 
                WHERE u.email = 'angel_hernandez137@hotmail.com'
            """)).fetchall()
            
            for user in result:
                print(f"   - ID: {user[0]}")
                print(f"   - Rol (texto): {user[1]}")
                print(f"   - ID Rol: {user[2]}")
                print(f"   - Nombre Rol: {user[3]}")
                
                # Verificar si tiene permisos
                if user[2]:  # Si tiene id_rol
                    perm_result = conn.execute(text("""
                        SELECT COUNT(*) FROM rol_permiso WHERE id_rol = :id_rol
                    """), {'id_rol': user[2]}).fetchone()
                    print(f"   - Permisos asignados: {perm_result[0]}")
                else:
                    print(f"   - Permisos asignados: 0 (sin rol asignado)")
                    
        except Exception as e:
            print(f"   ERROR: {e}")

if __name__ == "__main__":
    check_roles_system()
