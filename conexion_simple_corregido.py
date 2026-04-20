# -*- coding: utf-8 -*-
"""
conexion_simple_corregido.py - Conexión simple corregida para FOC26
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class ConexionSimple:
    """Clase para manejar conexión de forma más robusta"""
    
    def __init__(self):
        self.db = None
        self.db_connected = False
    
    def conectar(self):
        """Conectar a la base de datos FOC26"""
        try:
            # Verificar el ambiente configurado
            environment = os.getenv('ENVIRONMENT', 'local').lower().strip()
            print(f"Ambiente configurado: {environment}")

            if environment == 'cloud':
                # Usar configuración de nube (Render)
                database_url = os.getenv('DATABASE_URL')

                if not database_url:
                    # Construir desde variables individuales de cloud
                    db_user = os.getenv('CLOUD_DB_USER', 'foc26db_user')
                    db_password = os.getenv('CLOUD_DB_PASSWORD', '')
                    db_host = os.getenv('CLOUD_DB_HOST', 'localhost')
                    db_port = os.getenv('CLOUD_DB_PORT', '5432')
                    db_name = os.getenv('CLOUD_DB_NAME', 'foc26db')
                    ssl_mode = os.getenv('CLOUD_DB_SSL_MODE', 'require')

                    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?sslmode={ssl_mode}"

            else:
                # Usar configuración local (ambiente por defecto)
                db_name = os.getenv('LOCAL_DB_NAME', 'FOC26DB')
                db_user = os.getenv('LOCAL_DB_USER', 'postgres')
                db_password = os.getenv('LOCAL_DB_PASSWORD', 'admin123')
                db_host = os.getenv('LOCAL_DB_HOST', 'localhost')
                db_port = int(os.getenv('LOCAL_DB_PORT', '5432'))
                ssl_mode = os.getenv('LOCAL_DB_SSL_MODE', 'prefer')

                database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?sslmode={ssl_mode}"

            print(f"Conectando a base de datos...")
            print(f"Host: {db_host if 'db_host' in locals() else db_host}")
            print(f"Base de datos: {db_name if 'db_name' in locals() else db_name}")

            # Conectar directamente con psycopg2
            self.db = psycopg2.connect(
                database_url,
                cursor_factory=RealDictCursor,
                connect_timeout=10
            )

            # Configurar codificación para caracteres especiales
            self.db.set_client_encoding('LATIN1')

            # Probar conexión
            with self.db.cursor() as cursor:
                cursor.execute("SELECT version()")
                resultado = cursor.fetchone()
                print(f"Conectado exitosamente a PostgreSQL")
            
            self.db_connected = True
            print(f"Conexión establecida: db_connected={self.db_connected}")
            return True
            
        except Exception as e:
            print(f"Error conectando a base de datos: {e}")
            self.db_connected = False
            self.db = None
            return False
    
    def ejecutar_consulta(self, query, params=None):
        """Ejecutar consulta SELECT"""
        try:
            if not self.db_connected or not self.db:
                return None
            
            cursor = self.db.cursor()
            cursor.execute(query, params or ())
            resultado = cursor.fetchall()
            cursor.close()
            return resultado
                
        except Exception as e:
            print(f"Error ejecutando consulta: {e}")
            return None
    
    def ejecutar_actualizacion(self, query, params=None):
        """Ejecutar INSERT, UPDATE, DELETE"""
        try:
            if not self.db_connected or not self.db:
                return False
            
            cursor = self.db.cursor()
            cursor.execute(query, params or ())
            self.db.commit()
            cursor.close()
            return True
            
        except Exception as e:
            print(f"Error ejecutando actualización: {e}")
            if self.db:
                self.db.rollback()
            return False

# Instancia global única
_conexion_instance = None

def get_conexion():
    """Obtener instancia de conexión"""
    global _conexion_instance
    if _conexion_instance is None:
        _conexion_instance = ConexionSimple()
    return _conexion_instance

# Funciones compatibles con el código existente
def conectar_foc26db():
    """Conectar a la base de datos FOC26 (función de compatibilidad)"""
    conexion = get_conexion()
    return conexion.conectar()

# Propiedades para compatibilidad
@property
def db():
    """Obtener objeto de conexión"""
    return get_conexion().db

@property  
def db_connected():
    """Obtener estado de conexión"""
    return get_conexion().db_connected

# Para acceso directo
def get_db():
    """Obtener conexión directamente"""
    return get_conexion().db

def is_connected():
    """Verificar si está conectado"""
    return get_conexion().db_connected

if __name__ == "__main__":
    # Prueba de conexión
    if conectar_foc26db():
        print("Conexión exitosa a la base de datos")
        
        # Probar consulta
        resultado = get_conexion().ejecutar_consulta("SELECT version()")
        if resultado:
            print(f"Versión PostgreSQL: {resultado[0]['version'][:50]}...")
    else:
        print("Error de conexión")
