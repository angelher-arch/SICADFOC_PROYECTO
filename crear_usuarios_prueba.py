"""
CREACION DE USUARIOS DE PRUEBA - SICADFOC 2026
Script para insertar usuarios de prueba para validacion de roles
DBA Senior & Full-Stack - WindSurf
"""

import hashlib
import sys
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar configuracion
load_dotenv(encoding='utf-8')

def get_engine():
    """Obtener motor de base de datos"""
    try:
        # Intentar conexion a PostgreSQL si esta configurado
        if os.getenv('DATABASE_URL'):
            engine = create_engine(os.getenv('DATABASE_URL'))
        else:
            # Conexion local SQLite
            engine = create_engine('sqlite:///foc26_limpio.db')
        return engine
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def hash_password(password):
    """Generar hash SHA256 de la contrasena"""
    return hashlib.sha256(password.encode()).hexdigest()

def crear_usuario_profesor(engine):
    """Crear usuario de prueba con rol Profesor"""
    try:
        with engine.connect() as conn:
            # Verificar si ya existe
            result = conn.execute(text("SELECT COUNT(*) FROM usuario WHERE email = 'profesor@iujo.edu.ve'")).fetchone()
            
            if result[0] == 0:
                # Crear persona primero
                conn.execute(text("""
                    INSERT INTO persona (nombre, apellido, cedula, email, telefono)
                    VALUES ('Soporte', 'Docente', '0000000000', 'profesor@iujo.edu.ve', '0000000000')
                """))
                
                # Obtener ID de persona
                persona_result = conn.execute(text("SELECT id_persona FROM persona WHERE email = 'profesor@iujo.edu.ve'")).fetchone()
                persona_id = persona_result[0] if persona_result else 1
                
                # Crear usuario con rol profesor
                hash_pass = hash_password('Iujo2026*')
                conn.execute(text("""
                    INSERT INTO usuario (login, email, contrasena, rol, activo, correo_verificado, id_persona)
                    VALUES ('profesor@iujo.edu.ve', 'profesor@iujo.edu.ve', :contrasena, 'profesor', 1, 1, :persona_id)
                """), {'contrasena': hash_pass, 'persona_id': persona_id})
                
                conn.commit()
                print("OK - Usuario Profesor creado exitosamente")
                return True
            else:
                print("INFO - Usuario Profesor ya existe")
                return True
                
    except Exception as e:
        print(f"ERROR - Error creando usuario Profesor: {e}")
        return False

def crear_usuario_estudiante(engine):
    """Crear usuario de prueba con rol Estudiante"""
    try:
        with engine.connect() as conn:
            # Verificar si ya existe
            result = conn.execute(text("SELECT COUNT(*) FROM usuario WHERE email = 'estudiante@iujo.edu.ve'")).fetchone()
            
            if result[0] == 0:
                # Crear persona primero
                conn.execute(text("""
                    INSERT INTO persona (nombre, apellido, cedula, email, telefono)
                    VALUES ('Alumno', 'Prueba', '0000000001', 'estudiante@iujo.edu.ve', '0000000001')
                """))
                
                # Obtener ID de persona
                persona_result = conn.execute(text("SELECT id_persona FROM persona WHERE email = 'estudiante@iujo.edu.ve'")).fetchone()
                persona_id = persona_result[0] if persona_result else 2
                
                # Crear usuario con rol estudiante
                hash_pass = hash_password('Iujo2026*')
                conn.execute(text("""
                    INSERT INTO usuario (login, email, contrasena, rol, activo, correo_verificado, id_persona)
                    VALUES ('estudiante@iujo.edu.ve', 'estudiante@iujo.edu.ve', :contrasena, 'estudiante', 1, 1, :persona_id)
                """), {'contrasena': hash_pass, 'persona_id': persona_id})
                
                conn.commit()
                print("OK - Usuario Estudiante creado exitosamente")
                return True
            else:
                print("INFO - Usuario Estudiante ya existe")
                return True
                
    except Exception as e:
        print(f"ERROR - Error creando usuario Estudiante: {e}")
        return False

def verificar_usuarios_creados(engine):
    """Verificar que los usuarios fueron creados correctamente"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT login, email, rol, activo 
                FROM usuario 
                WHERE email IN ('profesor@iujo.edu.ve', 'estudiante@iujo.edu.ve')
                ORDER BY rol
            """)).fetchall()
            
            print("\nUsuarios creados:")
            print("-" * 60)
            for usuario in result:
                print(f"Usuario: {usuario[0]}")
                print(f"Email: {usuario[1]}")
                print(f"Rol: {usuario[2]}")
                print(f"Activo: {'Si' if usuario[3] else 'No'}")
                print("-" * 60)
                
            return len(result) == 2
            
    except Exception as e:
        print(f"ERROR - Error verificando usuarios: {e}")
        return False

def main():
    """Funcion principal"""
    print("CREACION DE USUARIOS DE PRUEBA - SICADFOC 2026")
    print("=" * 60)
    
    # Obtener conexion a base de datos
    engine = get_engine()
    if not engine:
        print("ERROR - No se pudo conectar a la base de datos")
        return False
    
    print("OK - Conexion a base de datos establecida")
    
    # Crear usuarios
    print("\nCreando usuarios de prueba...")
    
    profesor_ok = crear_usuario_profesor(engine)
    estudiante_ok = crear_usuario_estudiante(engine)
    
    if profesor_ok and estudiante_ok:
        print("\nOK - Usuarios creados exitosamente")
        
        # Verificar usuarios
        if verificar_usuarios_creados(engine):
            print("\nOK - Proceso completado exitosamente!")
            print("\nCredenciales para pruebas:")
            print("\nPERFIL: PROFESOR")
            print("Correo: profesor@iujo.edu.ve")
            print("Contrasena: Iujo2026*")
            print("\nPERFIL: ESTUDIANTE")
            print("Correo: estudiante@iujo.edu.ve")
            print("Contrasena: Iujo2026*")
            print("\nSistema disponible en: http://localhost:8501")
            return True
        else:
            print("\nERROR - Error verificando usuarios creados")
            return False
    else:
        print("\nERROR - Error creando usuarios")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
