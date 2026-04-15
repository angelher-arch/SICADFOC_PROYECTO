#!/usr/bin/env python3
"""
Módulo de Conexión PostgreSQL para SICADFOC 2026
Configuración dinámica para Railway con fallback local
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConexionPostgreSQL:
    """Clase de conexión PostgreSQL con configuración dinámica"""
    
    def __init__(self):
        self.connection = None
        self.db_url = None
        self._configurar_conexion()
    
    def _configurar_conexion(self):
        """Configurar conexión dinámica priorizando Railway"""
        try:
            # PRIORIDAD 1: Variable de entorno DATABASE_URL (Railway)
            database_url = os.getenv('DATABASE_URL')
            
            if database_url and database_url.strip():
                logger.info("Usando conexión Railway (DATABASE_URL)")
                self.db_url = database_url.strip()
                self._parsear_database_url()
            else:
                logger.warning("DATABASE_URL no encontrada, usando fallback local")
                self._configurar_local()
                
        except Exception as e:
            logger.error(f"Error configurando conexión: {e}")
            self._configurar_local()
    
    def _parsear_database_url(self):
        """Parsear DATABASE_URL de Railway"""
        try:
            # Formato esperado: postgresql://user:password@host:port/database
            if self.db_url.startswith('postgresql://'):
                # Extraer componentes de la URL
                url_parts = self.db_url.replace('postgresql://', '').split('@')
                if len(url_parts) == 2:
                    user_pass = url_parts[0].split(':')
                    host_db = url_parts[1].split('/')
                    
                    if len(user_pass) == 2 and len(host_db) == 2:
                        self.user = user_pass[0]
                        self.password = user_pass[1]
                        host_port = host_db[0].split(':')
                        
                        if len(host_port) == 2:
                            self.host = host_port[0]
                            self.port = int(host_port[1])
                        else:
                            self.host = host_port[0]
                            self.port = 5432
                            
                        self.database = host_db[1]
                        self.sslmode = 'require'
                        self.source = 'railway'
                        logger.info(f"URL parseada: {self.host}:{self.port}/{self.database}")
                        return
                        
            logger.error("Formato de DATABASE_URL inválido")
            self._configurar_local()
            
        except Exception as e:
            logger.error(f"Error parseando DATABASE_URL: {e}")
            self._configurar_local()
    
    def _configurar_local(self):
        """Configuración local como fallback"""
        logger.info("Usando configuración local (fallback)")
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '5432'))
        self.database = os.getenv('DB_NAME', 'FOC26DB')
        self.user = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD')
        self.sslmode = 'prefer'
        self.source = 'local'
    
    def conectar(self):
        """Establecer conexión con SSL obligatorio"""
        try:
            if self.connection and not self.connection.closed:
                return self.connection
                
            logger.info(f"Conectando a PostgreSQL en {self.host}:{self.port}/{self.database}")
            
            password_value = self.password if self.password is not None else ''
            if self.password is None:
                logger.warning("DB_PASSWORD no definida; si el servidor requiere contraseña, la conexión fallará.")
            
            connection_params = {
                'host': self.host,
                'port': self.port,
                'database': self.database,
                'user': self.user,
                'password': password_value,
                'cursor_factory': RealDictCursor,
                'sslmode': self.sslmode,
                'connect_timeout': 10,
                'application_name': 'sicad_foc26_2026'
            }
            
            self.connection = psycopg2.connect(**connection_params)
            logger.info("Conexión establecida exitosamente")
            return self.connection
            
        except psycopg2.Error as e:
            msg = f"Error de conexión PostgreSQL: {e}"
            if 'no password supplied' in str(e).lower() or 'password authentication failed' in str(e).lower():
                msg += ". Verifique que DB_PASSWORD esté definida en su archivo .env o en las variables de entorno."
            logger.error(msg)
            raise Exception(f"Error conectando a PostgreSQL: {msg}")
        except Exception as e:
            logger.error(f"Error general de conexión: {e}")
            raise Exception(f"Error general de conexión: {e}")
    
    def desconectar(self):
        """Cerrar conexión"""
        try:
            if self.connection and not self.connection.closed:
                self.connection.close()
                logger.info("Conexión cerrada")
        except Exception as e:
            logger.error(f"Error cerrando conexión: {e}")
    
    def ejecutar_consulta(self, query, params=None):
        """Ejecutar consulta con manejo de errores"""
        try:
            conn = self.conectar()
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                return result
        except psycopg2.Error as e:
            logger.error(f"Error en consulta: {e}")
            logger.error(f"Query: {query}")
            return None
        except Exception as e:
            logger.error(f"Error general en consulta: {e}")
            return None
        finally:
            self.desconectar()
    
    def ejecutar_actualizacion(self, query, params=None):
        """Ejecutar consulta de actualización (INSERT/UPDATE/DELETE)"""
        try:
            conn = self.conectar()
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                conn.commit()
                return True
        except psycopg2.Error as e:
            logger.error(f"Error en actualización: {e}")
            logger.error(f"Query: {query}")
            conn.rollback()
            return False
        except Exception as e:
            logger.error(f"Error general en actualización: {e}")
            return False
        finally:
            self.desconectar()
    
    def probar_conexion(self):
        """Probar conexión sin ejecutar consultas"""
        try:
            conn = self.conectar()
            if conn and not conn.closed:
                logger.info("Conexión probada exitosamente")
                return True
            return False
        except Exception as e:
            logger.error(f"Error probando conexión: {e}")
            return False
        finally:
            self.desconectar()
    
    def obtener_info_conexion(self):
        """Obtener información de la conexión actual"""
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password,
            'sslmode': self.sslmode,
            'source': self.source
        }

# Función de conveniencia para compatibilidad
def crear_conexion():
    """Crear instancia de conexión PostgreSQL"""
    return ConexionPostgreSQL()

# Función para testing
def test_connection():
    """Función de prueba de conexión"""
    try:
        conexion = ConexionPostgreSQL()
        info = conexion.obtener_info_conexion()
        logger.info(f"📊 Info conexión: {info}")
        
        if conexion.probar_conexion():
            logger.info("🎉 Conexión exitosa!")
            return True
        else:
            logger.error("Conexión fallida!")
            return False
    except Exception as e:
        logger.error(f"Error en prueba: {e}")
        return False

if __name__ == "__main__":
    # Prueba de conexión
    test_connection()
