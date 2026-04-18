#!/usr/bin/env python3
"""
Módulo de Conexión PostgreSQL para SICADFOC 2026
Configuración dinámica para Railway con fallback local
"""

import os
import logging
from urllib.parse import quote_plus, urlparse, parse_qs
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConexionPostgreSQL:
    """Clase de conexión PostgreSQL con configuración dinámica y pooling SQLAlchemy."""
    
    def __init__(self):
        self.connection = None
        self.engine = None
        self.db_url = None
        self.pool_size = int(os.getenv('DB_POOL_SIZE', '5'))
        self.max_overflow = int(os.getenv('DB_MAX_OVERFLOW', '10'))
        self._configurar_conexion()
    
    def _configurar_conexion(self):
        """Configurar conexión dinámica utilizando DATABASE_URL o variables individuales."""
        try:
            self.db_url = os.getenv('DATABASE_URL', '').strip() or os.getenv('DB_URL', '').strip()
            if self.db_url:
                self._configurar_from_database_url()
                return

            environment = os.getenv('ENVIRONMENT', 'local').lower().strip()
            logger.info(f"Configurando conexión para ambiente: {environment}")
            
            if environment == 'cloud':
                self._configurar_cloud()
            else:
                self._configurar_local()
        except Exception as e:
            logger.error(f"Error configurando conexión: {e}")
            self._configurar_local()
    
    def _configurar_from_database_url(self):
        """Configurar la conexión directamente desde DATABASE_URL de Render."""
        logger.info("Configurando conexión desde DATABASE_URL")
        try:
            parsed = urlparse(self.db_url)
            self.user = parsed.username
            self.password = parsed.password
            self.host = parsed.hostname or 'localhost'
            self.port = parsed.port or 5432
            self.database = parsed.path.lstrip('/')
            self.sslmode = 'require'
            self.source = 'render'

            query_params = parse_qs(parsed.query)
            if 'sslmode' in query_params:
                self.sslmode = query_params['sslmode'][0]
            
            sqlalchemy_url = self.db_url
            if sqlalchemy_url.startswith('postgresql://'):
                sqlalchemy_url = sqlalchemy_url.replace('postgresql://', 'postgresql+psycopg2://', 1)

            self.engine = self._crear_engine(sqlalchemy_url, require_ssl=True)
            logger.info(f"DATABASE_URL configurada: {self.host}:{self.port}/{self.database}")
        except Exception as e:
            logger.error(f"Error configurando DATABASE_URL: {e}")
            self._configurar_local()
    
    def _configurar_cloud(self):
        """Configuración para ambiente Cloud (FOC26DBCloud)"""
        logger.info("Configurando conexión Cloud (FOC26DBCloud)")
        
        self.host = os.getenv('CLOUD_DB_HOST', 'dpg-d7gfpi28qa3s73ci36d0-a.oregon-postgres.render.com')
        self.port = int(os.getenv('CLOUD_DB_PORT', '5432'))
        self.database = os.getenv('CLOUD_DB_NAME', 'foc26db')
        self.user = os.getenv('CLOUD_DB_USER', 'foc26db_user')
        self.password = os.getenv('CLOUD_DB_PASSWORD')
        self.sslmode = os.getenv('CLOUD_DB_SSL_MODE', 'require')  # OBLIGATORIO para Cloud
        self.source = 'cloud'
        
        # Verificar que sslmode sea 'require' para cloud
        if self.sslmode != 'require':
            logger.warning("Forzando sslmode='require' para conexión Cloud")
            self.sslmode = 'require'
    
    def _configurar_local(self):
        """Configuración para ambiente Local (FOC26DB)"""
        logger.info("Configurando conexión Local (FOC26DB)")
        
        self.host = os.getenv('LOCAL_DB_HOST', 'localhost')
        self.port = int(os.getenv('LOCAL_DB_PORT', '5432'))
        self.database = os.getenv('LOCAL_DB_NAME', 'FOC26DB')
        self.user = os.getenv('LOCAL_DB_USER', 'postgres')
        self.password = os.getenv('LOCAL_DB_PASSWORD')
        self.sslmode = os.getenv('LOCAL_DB_SSL_MODE', 'prefer')
        self.source = 'local'

    def _build_sqlalchemy_url(self):
        """Construir URL SQLAlchemy para conexiones sin DATABASE_URL."""
        user = quote_plus(self.user or '')
        password = quote_plus(self.password or '')
        url = f"postgresql+psycopg2://{user}:{password}@{self.host}:{self.port}/{self.database}"
        if self.sslmode:
            url += f"?sslmode={self.sslmode}"
        return url

    def _crear_engine(self, url, require_ssl=False):
        """Crear un engine SQLAlchemy con pooling de conexiones."""
        connect_args = {'connect_timeout': 15}
        if require_ssl:
            connect_args['sslmode'] = 'require'
        elif self.sslmode:
            connect_args['sslmode'] = self.sslmode

        try:
            engine = create_engine(
                url,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_pre_ping=True,
                future=True,
                connect_args=connect_args
            )
            logger.info(f"SQLAlchemy engine creado: pool_size={self.pool_size}, max_overflow={self.max_overflow}")
            return engine
        except SQLAlchemyError as e:
            logger.error(f"Error creando SQLAlchemy engine: {e}")
            raise

    def conectar(self):
        """Establecer conexión robusta usando SQLAlchemy."""
        connection = None
        try:
            if self.connection and not self.connection.closed:
                return self.connection

            logger.info(f"Conectando a PostgreSQL {self.source} en {self.host}:{self.port}/{self.database}")

            if self.engine is None:
                if self.db_url:
                    sqlalchemy_url = self.db_url
                    if sqlalchemy_url.startswith('postgresql://'):
                        sqlalchemy_url = sqlalchemy_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
                    self.engine = self._crear_engine(sqlalchemy_url, require_ssl=True)
                else:
                    sqlalchemy_url = self._build_sqlalchemy_url()
                    self.engine = self._crear_engine(sqlalchemy_url)

            connection = self.engine.raw_connection()
            self.connection = connection
            logger.info(f"Conexión {self.source} establecida exitosamente")
            return connection

        except SQLAlchemyError as e:
            error_msg = f"Error de SQLAlchemy al conectar: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)
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
    def obtener_info_conexion(self):
        """Obtener información de conexión actual"""
        environment = os.getenv('ENVIRONMENT', 'local')
        return {
            'environment': environment,
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': '***' if self.password else None,  # Ocultar contraseña
            'sslmode': self.sslmode,
            'source': self.source
        }

    def obtener_ambiente_actual(self):
        """Obtener el ambiente configurado (local/cloud)"""
        return os.getenv('ENVIRONMENT', 'local')

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
