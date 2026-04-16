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
        """Configurar conexión dinámica priorizando Render"""
        try:
            # PRIORIDAD 1: Variable de entorno DATABASE_URL (Render)
            database_url = os.getenv('DATABASE_URL')
            
            if database_url and database_url.strip():
                logger.info("Usando conexión Render (DATABASE_URL)")
                self.db_url = database_url.strip()
                self._parsear_database_url()
            else:
                logger.warning("DATABASE_URL no encontrada, usando fallback local")
                self._configurar_local()
                
        except Exception as e:
            logger.error(f"Error configurando conexión: {e}")
            self._configurar_local()
    
    def _parsear_database_url(self):
        """Parsear DATABASE_URL de Render"""
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
                        self.source = 'render'
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
        """Establecer conexión robusta usando DATABASE_URL con fallback local"""
        connection = None
        try:
            # Verificar si ya existe una conexión activa
            if self.connection and not self.connection.closed:
                return self.connection
            
            # PRIORIDAD 1: Usar DATABASE_URL si está disponible (Render)
            database_url = os.getenv('DATABASE_URL')
            
            if database_url and database_url.strip():
                logger.info("Conectando a Render usando DATABASE_URL")
                try:
                    # SSL obligatorio para Render
                    connection = psycopg2.connect(
                        database_url,
                        cursor_factory=RealDictCursor,
                        connect_timeout=15,
                        application_name='sicad_foc26_2026',
                        sslmode='require'  # SSL obligatorio para Render
                    )
                    self.connection = connection
                    logger.info("Conexión Render establecida exitosamente con SSL")
                    return connection
                except psycopg2.OperationalError as e:
                    logger.error(f"Error operacional con DATABASE_URL: {e}")
                    if "SSL" in str(e):
                        logger.error("Error de SSL. Verificando configuración...")
                    raise
                except psycopg2.Error as e:
                    logger.error(f"Error de PostgreSQL con DATABASE_URL: {e}")
                    raise
                except Exception as e:
                    logger.error(f"Error inesperado con DATABASE_URL: {e}")
                    raise
            
            # FALLBACK: Conexión local
            logger.info(f"DATABASE_URL no disponible. Conectando a PostgreSQL local en {self.host}:{self.port}/{self.database}")
            
            password_value = self.password if self.password is not None else ''
            if self.password is None:
                logger.warning("DB_PASSWORD no definida; la conexión podría fallar si el servidor la requiere.")
            
            connection_params = {
                'host': self.host,
                'port': self.port,
                'database': self.database,
                'user': self.user,
                'password': password_value,
                'cursor_factory': RealDictCursor,
                'sslmode': self.sslmode,
                'connect_timeout': 15,
                'application_name': 'sicad_foc26_2026'
            }
            
            connection = psycopg2.connect(**connection_params)
            self.connection = connection
            logger.info("Conexión local establecida exitosamente")
            return connection
            
        except psycopg2.OperationalError as e:
            error_msg = f"Error operacional de PostgreSQL: {e}"
            if "authentication failed" in str(e).lower():
                error_msg += ". Verifique credenciales en DATABASE_URL o variables locales."
            elif "connection refused" in str(e).lower():
                error_msg += ". Verifique que el servidor PostgreSQL esté activo y accesible."
            elif "timeout" in str(e).lower():
                error_msg += ". Tiempo de espera agotado. Verifique conexión de red."
            logger.error(error_msg)
            raise Exception(error_msg)
        except psycopg2.DatabaseError as e:
            logger.error(f"Error de base de datos: {e}")
            raise Exception(f"Error de base de datos: {e}")
        except Exception as e:
            logger.error(f"Error general de conexión: {e}")
            raise Exception(f"Error general de conexión: {e}")
        finally:
            # Asegurar que la conexión se cierre si hay error
            if connection and 'connection' in locals() and connection is not self.connection:
                try:
                    connection.close()
                except:
                    pass
    
    def desconectar(self):
        """Cerrar conexión"""
        try:
            if self.connection and not self.connection.closed:
                self.connection.close()
                logger.info("Conexión cerrada")
        except Exception as e:
            logger.error(f"Error cerrando conexión: {e}")
    
    def ejecutar_consulta(self, query, params=None):
        """Ejecutar consulta con manejo robusto de errores y gestión de conexiones"""
        conn = None
        try:
            conn = self.conectar()
            if not conn:
                logger.error("No se pudo establecer conexión para ejecutar consulta")
                return None
            
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                logger.debug(f"Consulta ejecutada exitosamente: {len(result) if result else 0} filas")
                return result
                
        except psycopg2.ProgrammingError as e:
            logger.error(f"Error de programación SQL: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Parámetros: {params}")
            return None
        except psycopg2.OperationalError as e:
            logger.error(f"Error operacional en consulta: {e}")
            logger.error(f"Query: {query}")
            return None
        except psycopg2.Error as e:
            logger.error(f"Error de PostgreSQL en consulta: {e}")
            logger.error(f"Query: {query}")
            return None
        except Exception as e:
            logger.error(f"Error general en consulta: {e}")
            logger.error(f"Query: {query}")
            return None
        finally:
            # No cerramos la conexión aquí para permitir reuso
            # La conexión se cerrará automáticamente cuando sea necesario
            pass
    
    def ejecutar_actualizacion(self, query, params=None):
        """Ejecutar consulta de actualización (INSERT/UPDATE/DELETE) con manejo robusto de transacciones"""
        conn = None
        try:
            conn = self.conectar()
            if not conn:
                logger.error("No se pudo establecer conexión para ejecutar actualización")
                return False
            
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                conn.commit()
                logger.debug(f"Actualización ejecutada exitosamente")
                return True
                
        except psycopg2.IntegrityError as e:
            if conn:
                conn.rollback()
            logger.error(f"Error de integridad de datos: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Parámetros: {params}")
            return False
        except psycopg2.ProgrammingError as e:
            if conn:
                conn.rollback()
            logger.error(f"Error de programación SQL en actualización: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Parámetros: {params}")
            return False
        except psycopg2.OperationalError as e:
            if conn:
                conn.rollback()
            logger.error(f"Error operacional en actualización: {e}")
            logger.error(f"Query: {query}")
            return False
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Error de PostgreSQL en actualización: {e}")
            logger.error(f"Query: {query}")
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error general en actualización: {e}")
            logger.error(f"Query: {query}")
            return False
        finally:
            # No cerramos la conexión aquí para permitir reuso
            pass
    
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
