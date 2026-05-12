#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
database.py - Gestor de Base de Datos PostgreSQL
SICADFOC 2026 - Instituto Universitario Jesus Obrero
"""

import os
import psycopg2
import datetime
from psycopg2.extras import RealDictCursor
from psycopg2 import OperationalError
import logging
from contextlib import contextmanager
from typing import Dict, Any, List, Optional, Tuple, Union
import streamlit as st
from utils_homologacion import homologar_cedula, crear_condicion_cedula_sql

# Diagnóstico de conexión al importar el módulo
def test_db_connection():
    """Función de diagnóstico inmediato que se ejecuta al importar"""
    try:
        print("DEBUG_DB_INIT: Iniciando diagnóstico de conexión...")
        
        # Obtener DATABASE_URL del entorno
        database_url = os.getenv("DATABASE_URL")
        print(f"DEBUG_DB_INIT: DATABASE_URL encontrada: {'SÍ' if database_url else 'NO'}")
        
        if not database_url:
            print("DEBUG_DB_INIT_ERROR: DATABASE_URL no encontrada en el entorno")
            print("DEBUG_DB_INIT_ERROR: Variables DATABASE/DB disponibles:")
            for key, value in os.environ.items():
                if 'DATABASE' in key or 'DB' in key:
                    print(f"  {key}: {'***' if 'PASSWORD' in key else value}")
            return False
        
        # Debug de la URL completa (sin contraseña)
        import urllib.parse
        parsed = urllib.parse.urlparse(database_url)
        safe_url = database_url.replace(parsed.password, '***') if parsed.password else database_url
        print(f"DEBUG_DB_INIT: URL parseada: {safe_url}")
        print(f"DEBUG_DB_INIT: Host: {parsed.hostname}")
        print(f"DEBUG_DB_INIT: Port: {parsed.port}")
        print(f"DEBUG_DB_INIT: Database: {parsed.path[1:] if parsed.path else 'N/A'}")
        print(f"DEBUG_DB_INIT: User: {parsed.username}")
        print(f"DEBUG_DB_INIT: SSL params: {urllib.parse.parse_qs(parsed.query)}")
        
        # Detectar ambiente y configurar SSL apropiado
        is_production = os.getenv('DATABASE_URL') is not None
        ssl_mode = 'require' if is_production else 'prefer'
        
        print(f"DEBUG_DB_INIT: Ambiente detectado: {'PRODUCCIÓN' if is_production else 'DESARROLLO'}")
        print(f"DEBUG_DB_INIT: Usando SSL mode: {ssl_mode}")
        
        # Intentar conexión con SSL apropiado
        try:
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path[1:] if parsed.path else 'foc26db',
                user=parsed.username,
                password=parsed.password,
                sslmode=ssl_mode,
                connect_timeout=10
            )
            print(f"DEBUG_DB_INIT: Conexión exitosa con SSL {ssl_mode}")
            test_connection_and_close(conn)
            return True
        except Exception as e1:
            print(f"DEBUG_DB_INIT: Conexión con SSL {ssl_mode} falló: {e1}")
            
            # Si falla y es desarrollo local, intentar sin SSL
            if not is_production and ssl_mode != 'disable':
                print("DEBUG_DB_INIT: Intentando conexión sin SSL (desarrollo local)")
                try:
                    conn = psycopg2.connect(
                        host=parsed.hostname,
                        port=parsed.port or 5432,
                        database=parsed.path[1:] if parsed.path else 'foc26db',
                        user=parsed.username,
                        password=parsed.password,
                        sslmode='disable',
                        connect_timeout=10
                    )
                    print("DEBUG_DB_INIT: Conexión exitosa sin SSL (desarrollo local)")
                    test_connection_and_close(conn)
                    return True
                except Exception as e2:
                    print(f"DEBUG_DB_INIT: Conexión sin SSL falló: {e2}")
            
        print("DEBUG_DB_INIT_ERROR: Todos los métodos de conexión fallaron")
        return False
        
    except OperationalError as e:
        print("DEBUG_DB_INIT_ERROR: Error de conexión a PostgreSQL:")
        print(f"  Código PostgreSQL (pgcode): {getattr(e, 'pgcode', 'N/A')}")
        print(f"  Error PostgreSQL (pgerror): {getattr(e, 'pgerror', 'N/A')}")
        print(f"  Error completo: {e}")
        
        # Diagnóstico específico extendido
        pgcode = getattr(e, 'pgcode', None)
        if pgcode == '08001':
            print("DEBUG_DB_INIT_DIAGNÓSTICO: Error de red/firewall/SSL (08001)")
            print("DEBUG_DB_INIT_SOLUCIÓN: Verificar firewall, red o configuración SSL")
        elif pgcode == '28P01':
            print("DEBUG_DB_INIT_DIAGNÓSTICO: Error de autenticación/contraseña (28P01)")
            print("DEBUG_DB_INIT_SOLUCIÓN: Verificar usuario y contraseña en DATABASE_URL")
        elif pgcode == '3D000':
            print("DEBUG_DB_INIT_DIAGNÓSTICO: Base de datos no existe (3D000)")
            print("DEBUG_DB_INIT_SOLUCIÓN: Verificar nombre de la base de datos")
        elif pgcode == '28000':
            print("DEBUG_DB_INIT_DIAGNÓSTICO: Error de autorización (28000)")
            print("DEBUG_DB_INIT_SOLUCIÓN: Verificar permisos del usuario")
        else:
            print(f"DEBUG_DB_INIT_DIAGNÓSTICO: Error no identificado: {pgcode}")
            print("DEBUG_DB_INIT_SOLUCIÓN: Revisar configuración completa de conexión")
        
        return False
    except Exception as e:
        print(f"DEBUG_DB_INIT_ERROR: Error inesperado: {e}")
        import traceback
        print(f"DEBUG_DB_INIT_TRACEBACK: {traceback.format_exc()}")
        return False

def test_connection_and_close(conn):
    """Prueba conexión y la cierra correctamente"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        print(f"DEBUG_DB_INIT: Conexión probada exitosamente - PostgreSQL {version[0]}")
    except Exception as e:
        print(f"DEBUG_DB_INIT_ERROR: Error probando conexión: {e}")
        try:
            conn.close()
        except:
            pass

# Ejecutar diagnóstico al importar
test_db_connection()

from dotenv import load_dotenv
from config import get_database_config, log_environment

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseStructureError(Exception):
    """Excepción personalizada para errores de estructura de base de datos"""
    pass

# Canal único de conexión global
db_connection = None

def get_db_connection():
    """Función global que retorna el canal único de conexión ya configurado (solo parámetros estándar psycopg2)"""
    global db_connection
    
    if db_connection and not db_connection.closed:
        return db_connection
    
    # Si no existe conexión, crear una nueva
    from config import get_database_config
    config = get_database_config()
    
    try:
        # Solo parámetros estándar de psycopg2
        connection_params = {
            'host': config['host'],
            'port': config['port'],
            'database': config['database'],
            'user': config['user'],
            'password': config['password'],
            'cursor_factory': RealDictCursor,
            'sslmode': config.get('sslmode', 'prefer'),
            'connect_timeout': 10
        }
        
        db_connection = psycopg2.connect(**connection_params)
        print("DEBUG_DB: Nuevo canal único creado")
        return db_connection
    except Exception as e:
        print(f"DEBUG_DB_ERROR: Error creando canal único: {e}")
        raise e

class DatabaseManager:
    """Gestor de base de datos PostgreSQL con canal único de conexión"""
    
    @staticmethod
    def _row_to_dict(row, description=None):
        """Convertir filas tuple/RealDictRow/dict a dict normal."""
        if row is None:
            return {}
        if isinstance(row, dict):
            return dict(row)
        if description:
            columns = [col[0] for col in description]
            try:
                return dict(zip(columns, row))
            except Exception:
                return {}
        return {}

    def __init__(self):
        """Inicialización con canal único de conexión basado en detección de entorno"""
        global db_connection
        
        # Si ya existe una conexión, reutilizarla (Canal Único)
        if db_connection and not db_connection.closed:
            self._connection = db_connection
            self.config = self._get_existing_config()
            return
        
        # Primera vez: establecer canal único
        self._connection = None
        self._load_config()
        
        # DEBUG: Mostrar configuración real que se está usando
        print("=== DEBUG: CONFIGURACIÓN REAL ===")
        print(f"Host: {self.config.get('host', 'NO DEFINIDO')}")
        print(f"Port: {self.config.get('port', 'NO DEFINIDO')}")
        print(f"Database: {self.config.get('database', 'NO DEFINIDO')}")
        print(f"User: {self.config.get('user', 'NO DEFINIDO')}")
        print(f"Environment: {self.config.get('environment', 'NO DEFINIDO')}")
        print("=== FIN DEBUG CONFIGURACIÓN ===")
        
        # Establecer canal único basado en detección de entorno
        try:
            # Eliminar pool_pre_ping que causa el error
            connection_params = {
                'host': self.config['host'],
                'port': self.config['port'],
                'database': self.config['database'],
                'user': self.config['user'],
                'password': self.config['password'],
                'cursor_factory': RealDictCursor,
                'sslmode': self.config.get('sslmode', 'prefer'),
                'connect_timeout': 10
            }
            
            self._connection = psycopg2.connect(**connection_params)
            
            # Guardar conexión global (Canal Único)
            db_connection = self._connection
            print("DEBUG_DB: Canal único de conexión establecido exitosamente")
            
            # VERIFICACIÓN INMEDIATA: Probar conexión real
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1 as test_connection")
            result = cursor.fetchone()
            cursor.close()
            print(f"DEBUG_DB: Conexión verificada - Resultado: {result}")
            
        except Exception as e:
            print(f"DEBUG_DB_ERROR: Error conectando a base de datos: {e}")
            print(f"DEBUG_DB_ERROR: Tipo de error: {type(e).__name__}")
            raise Exception("No se puede conectar a la base de datos local")
    
    def _get_existing_config(self):
        """Obtener configuración existente de la conexión global"""
        try:
            # Extraer configuración de la conexión existente
            if hasattr(db_connection, 'dsn'):
                # Parsear DSN para obtener configuración
                import psycopg2.extensions
                dsn_params = psycopg2.extensions.parse_dsn(db_connection.dsn)
                return {
                    'host': dsn_params.get('host', 'localhost'),
                    'port': dsn_params.get('port', 5432),
                    'database': dsn_params.get('dbname', 'foc26db'),
                    'user': dsn_params.get('user', 'postgres'),
                    'sslmode': dsn_params.get('sslmode', 'prefer'),
                    'environment': 'production' if dsn_params.get('host') and 'render.com' in dsn_params.get('host', '') else 'development'
                }
            else:
                # Configuración por defecto si no se puede obtener
                return {
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'foc26db',
                    'user': 'postgres',
                    'sslmode': 'prefer',
                    'environment': 'development'
                }
        except Exception:
            return {
                'host': 'localhost',
                'port': 5432,
                'database': 'foc26db',
                'user': 'postgres',
                'sslmode': 'prefer',
                'environment': 'development'
            }
        
    def get_connection(self):
        """Obtener conexión básica a base de datos"""
        if self._connection and not self._connection.closed:
            return self._connection
            
        try:
            self._connection = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                sslmode='prefer',
                connect_timeout=10
            )
            return self._connection
        except Exception as e:
            raise Exception("No se puede conectar a la base de datos local")

    def _load_config(self):
        """CONFIGURACIÓN CENTRALIZADA desde config.py"""
        # LIMPIEZA DE CACHÉ - Inicializar desde cero
        self._connection = None
        
        try:
            # Usar configuración centralizada desde config.py
            self.config = get_database_config()
            print(f"DEBUG_DB: Configuración cargada: {list(self.config.keys())}")
            
            # Configurar SSL según ambiente
            if self.config.get('environment') == 'production':
                self.config['sslmode'] = 'require'  # Requerido para Render y nube
                print("DEBUG_DB: SSL requerido para producción (nube)")
            else:
                self.config['sslmode'] = 'prefer'  # Flexible para desarrollo local
                print("DEBUG_DB: SSL prefer para desarrollo local")
            
            # Log del ambiente para monitoreo
            log_environment()
            
        except Exception as e:
            print(f"DEBUG_DB_ERROR: Error cargando configuración - {e}")
            raise
    
    def _check_connection(self):
        """Verificar conexión a base de datos al inicio con diagnóstico robusto"""
        import time
        
        print(f"DEBUG_DB: Verificando conexión a {self.config.get('host', 'unknown')}...")
        print(f"DEBUG_DB: Configuración completa:")
        print(f"  Host: {self.config.get('host', 'unknown')}")
        print(f"  Port: {self.config.get('port', 'unknown')}")
        print(f"  Database: {self.config.get('database', 'unknown')}")
        print(f"  User: {self.config.get('user', 'unknown')}")
        print(f"  Password: {'*' * len(str(self.config.get('password', '')))}")
        print(f"  SSL Mode: {self.config.get('sslmode', 'unknown')}")
        print(f"  Environment: {self.config.get('environment', 'unknown')}")
        
        # Diagnóstico de credenciales
        self._diagnose_credentials()
        
        for intento in range(1, 4):
            try:
                print(f"DEBUG_DB: Intento {intento}/3 de conexión...")
                
                # Intentar conexión con SSL apropiado según ambiente
                ssl_mode = self.config.get('sslmode', 'prefer')
                print(f"DEBUG_DB: Intento {intento}/3 con SSL mode: {ssl_mode}")
                
                test_conn = psycopg2.connect(
                    host=self.config['host'],
                    port=self.config['port'],
                    database=self.config['database'],
                    user=self.config['user'],
                    password=self.config['password'],
                    sslmode=ssl_mode,
                    connect_timeout=10
                )
                
                # Probar consulta simple
                cursor = test_conn.cursor()
                cursor.execute("SELECT version()")
                version = cursor.fetchone()
                cursor.close()
                test_conn.close()
                
                print(f"DEBUG_DB: Conexión exitosa (intento {intento}) - PostgreSQL {version[0]}")
                return  # Salir si la conexión fue exitosa
                
            except OperationalError as e:
                print(f"DEBUG_DB_ERROR: Error de conexión a PostgreSQL (intento {intento}):")
                print(f"  Código PostgreSQL (pgcode): {getattr(e, 'pgcode', 'N/A')}")
                print(f"  Error PostgreSQL (pgerror): {getattr(e, 'pgerror', 'N/A')}")
                print(f"  Error completo: {e}")
                print(f"  Host: {self.config.get('host', 'unknown')}")
                print(f"  Port: {self.config.get('port', 'unknown')}")
                print(f"  Database: {self.config.get('database', 'unknown')}")
                print(f"  User: {self.config.get('user', 'unknown')}")
                print(f"  SSL Mode: {ssl_mode}")
                
                # Si es desarrollo local y SSL falló, intentar sin SSL en el último intento
                if intento == 3 and self.config.get('environment') != 'production' and ssl_mode != 'disable':
                    print("DEBUG_DB: Intentando fallback sin SSL (desarrollo local)")
                    try:
                        test_conn = psycopg2.connect(
                            host=self.config['host'],
                            port=self.config['port'],
                            database=self.config['database'],
                            user=self.config['user'],
                            password=self.config['password'],
                            sslmode='disable',
                            connect_timeout=10
                        )
                        cursor = test_conn.cursor()
                        cursor.execute("SELECT version()")
                        version = cursor.fetchone()
                        cursor.close()
                        test_conn.close()
                        print(f"DEBUG_DB: Conexión exitosa sin SSL - PostgreSQL {version[0]}")
                        return
                    except Exception as fallback_error:
                        print(f"DEBUG_DB_ERROR: Fallback sin SSL también falló: {fallback_error}")
                        print("DEBUG_DB_ERROR: Intentando conexión a postgres por defecto...")
                        # Último intento: conectar a postgres por defecto
                        try:
                            test_conn = psycopg2.connect(
                                host=self.config['host'],
                                port=self.config['port'],
                                database='postgres',  # Base de datos por defecto
                                user=self.config['user'],
                                password=self.config['password'],
                                sslmode='disable',
                                connect_timeout=10
                            )
                            cursor = test_conn.cursor()
                            cursor.execute("SELECT version()")
                            version = cursor.fetchone()
                            cursor.close()
                            test_conn.close()
                            print(f"DEBUG_DB: Conexión exitosa a postgres por defecto - PostgreSQL {version[0]}")
                            print("DEBUG_DB_WARNING: La base de datos '{self.config['database']}' no existe. Debes crearla.")
                            return
                        except Exception as final_error:
                            print(f"DEBUG_DB_ERROR: Conexión a postgres por defecto también falló: {final_error}")
                
                if intento < 3:
                    print(f"DEBUG_DB: Esperando 2 segundos antes del siguiente intento...")
                    time.sleep(2)
                else:
                    print("DEBUG_DB_ERROR: Se agotaron los 3 intentos de conexión")
                    raise Exception(f"No se puede conectar a la base de datos después de 3 intentos. Último error: {e}")
                    
            except Exception as e:
                print(f"DEBUG_DB_ERROR: Error inesperado en conexión (intento {intento}): {e}")
                if intento < 3:
                    print(f"DEBUG_DB: Esperando 2 segundos antes del siguiente intento...")
                    time.sleep(2)
                else:
                    raise Exception(f"No se puede conectar a la base de datos después de 3 intentos. Último error: {e}")
    
    def _diagnose_credentials(self):
        """Diagnóstico específico de credenciales y configuración"""
        print("DEBUG_DB: Iniciando diagnóstico de credenciales...")
        
        # Verificar parámetros básicos
        host = self.config.get('host')
        port = self.config.get('port')
        database = self.config.get('database')
        user = self.config.get('user')
        password = self.config.get('password')
        
        issues = []
        
        if not host:
            issues.append("Host no configurado")
        elif host not in ['localhost', '127.0.0.1'] and not '.' in host:
            issues.append(f"Host inválido: {host}")
            
        if not port or port <= 0 or port > 65535:
            issues.append(f"Puerto inválido: {port}")
            
        if not database:
            issues.append("Base de datos no configurada")
            
        if not user:
            issues.append("Usuario no configurado")
            
        if not password:
            issues.append("Contraseña no configurada")
        elif len(password) < 4:
            issues.append("Contraseña demasiado corta")
        
        if issues:
            print("DEBUG_DB_ERROR: Problemas de configuración detectados:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("DEBUG_DB: Credenciales y configuración válidas")
            
        # Diagnóstico de red (solo para localhost)
        if host in ['localhost', '127.0.0.1']:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, port))
                sock.close()
                if result == 0:
                    print(f"DEBUG_DB: Puerto {port} accesible en {host}")
                else:
                    print(f"DEBUG_DB_ERROR: Puerto {port} no accesible en {host} (código: {result})")
            except Exception as e:
                print(f"DEBUG_DB_ERROR: Error diagnóstico de red: {e}")
    
    def _validate_database_structure(self):
        """Validar estructura crítica de base de datos al iniciar"""
        try:
            print("DEBUG_DB: Iniciando validación de estructura de base de datos...")
            critical_tables = ['usuarios', 'persona', 'estudiante', 'profesor', 'configuracion_permisos']
            missing_tables = []
            existing_tables = []
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            for table in critical_tables:
                try:
                    print(f"DEBUG_DB: Verificando tabla '{table}'...")
                    cursor.execute(f"SELECT 1 FROM {table} LIMIT 1")
                    existing_tables.append(table)
                    print(f"DEBUG_DB: Tabla '{table}' existe y es accesible")
                except Exception as e:
                    if "does not exist" in str(e).lower():
                        missing_tables.append(table)
                        print(f"DEBUG_DB_ERROR: Tabla '{table}' no existe")
                    else:
                        logger.warning(f"Error verificando tabla {table}: {e}")
                        print(f"DEBUG_DB_ERROR: Error verificando tabla '{table}': {e}")
            
            print(f"DEBUG_DB: Tablas existentes: {existing_tables}")
            print(f"DEBUG_DB: Tablas faltantes: {missing_tables}")
            
            if missing_tables:
                error_msg = f"TABLAS CRÍTICAS FALTANTES: {', '.join(missing_tables)}"
                logger.error(error_msg)
                print(f"DEBUG_DB_ERROR: {error_msg}")
                raise DatabaseStructureError(
                    f"La base de datos está incompleta. Faltan las tablas: {', '.join(missing_tables)}. "
                    f"Ejecute: psql -d {self.config['database']} -f sincronizacion_tablas.sql"
                )
            else:
                logger.info("Estructura de base de datos validada correctamente")
                print("DEBUG_DB: Estructura de base de datos validada correctamente")
                
        except Exception as e:
            logger.error(f"Error validando estructura: {e}")
            print(f"DEBUG_DB_ERROR: Error en validación de estructura: {e}")
            print(f"DEBUG_DB_ERROR: Tipo de error: {type(e).__name__}")
            # No lanzar excepción para permitir funcionamiento parcial
        
        finally:
            if 'conn' in locals() and conn:
                conn.close()
                print("DEBUG_DB: Conexión cerrada después de validación")
    
    def close_connection(self):
        """Cerrar conexión actual"""
        try:
            if self._connection and not self._connection.closed:
                self._connection.close()
                self._connection = None
                logger.info("Conexión cerrada exitosamente")
        except Exception as e:
            logger.error(f"Error cerrando conexión: {e}")
    
    def execute_query(self, query: str, params: Optional[Tuple] = None, 
                      fetch_one: bool = False, fetch_all: bool = False) -> Union[Dict, List[Dict], int]:
        """
        Ejecutar consulta SQL con manejo robusto de errores
        """
        start_time = datetime.datetime.now()
        conn = None
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Ejecutar consulta
            cursor.execute(query, params or ())
            query_normalized = query.lstrip().upper()
            is_read_query = query_normalized.startswith(("SELECT", "WITH", "SHOW", "EXPLAIN"))
            
            # Determinar tipo de retorno
            if fetch_one:
                result = cursor.fetchone()
                return self._row_to_dict(result, cursor.description)
            elif fetch_all or is_read_query:
                results = cursor.fetchall()
                return [self._row_to_dict(row, cursor.description) for row in results]
            else:
                # Persistir explícitamente operaciones de escritura (solo si no es AUTOCOMMIT)
                if self.config.get('environment') != 'production':
                    conn.commit()
                return cursor.rowcount
                
        except OperationalError as e:
            logger.error(f"Error de conexión en execute_query: {e}")
            # Intentar reconectar
            self.close_connection()
            raise
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.error(f"Error en execute_query: {e}")
            raise
        finally:
            elapsed = (datetime.datetime.now() - start_time).total_seconds()
            logger.info(f"Query ejecutada en {elapsed:.3f}s: {query[:100]}...")
    
    def execute_transaction(self, queries: List[Tuple[str, Optional[Tuple]]]) -> Dict[str, Any]:
        """
        Ejecutar múltiples consultas en una transacción
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Iniciar transacción (manejo compatible con AUTOCOMMIT)
            if self.config.get('environment') == 'production':
                # En producción con AUTOCOMMIT, usar BEGIN explícito
                cursor.execute("BEGIN")
            
            for query, params in queries:
                cursor.execute(query, params or ())
            
            # Commit (solo en desarrollo, en producción AUTOCOMMIT maneja)
            if self.config.get('environment') != 'production':
                conn.commit()
            else:
                cursor.execute("COMMIT")
            
            logger.info(f"Transacción completada exitosamente ({len(queries)} consultas)")
            return {
                'success': True,
                'message': 'Transacción completada exitosamente'
            }
            
        except Exception as e:
            # Rollback en caso de error
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            logger.error(f"Error en transacción: {e}")
            return {
                'success': False,
                'message': f'Error en transacción: {str(e)}'
            }
        finally:
            # No cerrar la conexión aquí, se reutilizará
            pass
    
    def test_connection(self) -> Dict[str, Any]:
        """Validar conexión con la base de datos"""
        test_result = {
            'status': False,
            'message': '',
            'database_info': {},
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        try:
            print("DEBUG_TEST: Iniciando test_connection()...")
            conn = self.get_connection()
            print(f"DEBUG_TEST: Conexión obtenida: {type(conn)}")
            cursor = conn.cursor()
            print("DEBUG_TEST: Cursor creado")
            
            # Test básico
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"DEBUG_TEST: Test básico exitoso: {result}")
            test_result['status'] = True
            test_result['message'] = 'Conexión exitosa'
            
            # Información de la base de datos
            cursor.execute("SELECT version()")
            version_info = cursor.fetchone()
            version_dict = self._row_to_dict(version_info, cursor.description)
            test_result['database_info']['version'] = (
                version_dict.get('version')
                or next(iter(version_dict.values()), 'Unknown')
            )
            
            # Verificar tablas principales
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name IN ('usuarios', 'estudiante', 'carrera')
                ORDER BY table_name
            """)
            tables = []
            for row in cursor.fetchall():
                row_dict = self._row_to_dict(row, cursor.description)
                tables.append(row_dict.get('table_name') or next(iter(row_dict.values()), None))
            tables = [t for t in tables if t]
            test_result['database_info']['tables'] = tables
            
            # Contar usuarios
            cursor.execute("SELECT COUNT(*) as count FROM usuarios")
            user_count = cursor.fetchone()
            user_count_dict = self._row_to_dict(user_count, cursor.description)
            test_result['database_info']['user_count'] = (
                user_count_dict.get('count')
                or next(iter(user_count_dict.values()), 0)
            )
            
            cursor.close()
            print(f"DEBUG_TEST: Test connection completado - Status: {test_result['status']}")
            logger.info("Test de conexión exitoso")
            
        except Exception as e:
            print(f"DEBUG_TEST_ERROR: Error en test_connection: {e}")
            print(f"DEBUG_TEST_ERROR: Tipo: {type(e).__name__}")
            test_result['status'] = False
            test_result['message'] = f'Error de conexión: {str(e)}'
            logger.error(f"Error en test de conexión: {e}")
        
        return test_result

# Instancia global del gestor de base de datos con manejo de errores
db_manager = None

def initialize_db_manager():
    """Inicializar DatabaseManager con fallback automático a producción"""
    global db_manager
    
    if db_manager is not None:
        return db_manager
    
    try:
        # Intentar inicialización normal (local o producción según configuración)
        db_manager = DatabaseManager()
        print("DEBUG_DB: DatabaseManager inicializado exitosamente")
        return db_manager
    except Exception as e:
        print(f"DEBUG_DB_ERROR: Error inicializando DatabaseManager: {e}")
        print("DEBUG_DB_ERROR: Intentando usar ambiente de producción como fallback...")
        
        # Fallback a producción si falla la conexión local
        import os
        os.environ['DATABASE_URL'] = 'postgresql://foc26db_user:IZfArPXgOciy8iKsiRDbOosUiR7BAc8u@dpg-d7gfpi28qa3s73ci36d0-a.oregon-postgres.render.com/foc26db'
        
        try:
            # Forzar recarga de configuración
            import importlib
            import config
            importlib.reload(config)
            
            # Crear nueva instancia con configuración de producción
            db_manager = DatabaseManager()
            print("DEBUG_DB: DatabaseManager inicializado exitosamente con fallback a producción")
            return db_manager
        except Exception as fallback_error:
            print(f"DEBUG_DB_ERROR: Error en fallback a producción: {fallback_error}")
            print("DEBUG_DB_ERROR: No se pudo inicializar DatabaseManager")
            raise Exception("No se puede conectar ni a base de datos local ni a producción")

# Inicializar al importar el módulo
initialize_db_manager()

# Funciones globales para compatibilidad - ESQUEMA UNIFICADO
def execute_query(query: str, params: Optional[Tuple] = None, 
                  fetch_one: bool = False, fetch_all: bool = False) -> Union[Dict, List[Dict], int]:
    """Función wrapper para execute_query del DatabaseManager - CONEXIÓN UNIFICADA db_foc26"""
    print(f">>> DB_QUERY: Ejecutando consulta - {query[:50]}...")
    result = db_manager.execute_query(query, params, fetch_one, fetch_all)
    print(f">>> DB_QUERY: Resultado obtenido - {type(result)}")
    return result

def fetch_data(query: str, params: Optional[Tuple] = None, 
               fetch_one: bool = False) -> Union[Dict, List[Dict]]:
    """Función wrapper para fetch_data del DatabaseManager - CONEXIÓN UNIFICADA db_foc26"""
    print(f">>> DB_FETCH: Obteniendo datos - {query[:50]}...")
    result = db_manager.execute_query(query, params, fetch_one, not fetch_one)
    print(f">>> DB_FETCH: Datos obtenidos - {len(result) if isinstance(result, list) else 1} registros")
    return result

def ejecutar_transaccion(queries: List[Tuple[str, Optional[Tuple]]]) -> Dict[str, Any]:
    """Función wrapper para ejecutar_transaccion del DatabaseManager - CONEXIÓN UNIFICADA db_foc26"""
    print(f">>> DB_TRANS: Iniciando transacción con {len(queries)} consultas")
    result = db_manager.execute_transaction(queries)
    print(f">>> DB_TRANS: Transacción completada - Success: {result.get('success', False)}")
    return result

def test_database_connection() -> Dict[str, Any]:
    """Función wrapper para test_connection del DatabaseManager - CONEXIÓN UNIFICADA db_foc26"""
    print(">> DB_TEST: Verificando conexión unificada...")
    result = db_manager.test_connection()
    print(f">> DB_TEST: Conexión verificada - Status: {result.get('status', False)}")
    return result

def execute_transaction(queries: List[Tuple[str, Optional[Tuple]]]) -> Dict[str, Any]:
    """
    Ejecutar múltiples consultas en una transacción - CONEXIÓN UNIFICADA db_foc26
    Returns: {'success': bool, 'message': str}
    """
    try:
        print(f">> DB_TRANS_UNIFIED: Ejecutando {len(queries)} consultas en transacción")
        result = db_manager.execute_transaction(queries)
        print(f">> DB_TRANS_UNIFIED: Resultado transacción - Success: {result.get('success', False)}")
        return result
    except Exception as e:
        return {
            'success': False,
            'message': f'Error en transacción: {str(e)}'
        }

def get_database_info() -> Dict[str, Any]:
    """Obtener información de la base de datos"""
    return db_manager.test_connection()

def close_database():
    """Cerrar conexión a la base de datos"""
    db_manager.close_connection()

def get_db_session():
    """Obtener sesión de base de datos básica con debugging"""
    try:
        print("=== DEBUG: get_db_session() INICIADO ===")
        
        # Obtener conexión sin diagnóstico complejo
        conn = db_manager.get_connection()
        print(f"DEBUG: Conexión obtenida: {type(conn)}")
        print(f"DEBUG: Conexión cerrada: {conn.closed if hasattr(conn, 'closed') else 'NO APLICABLE'}")
        
        cursor = conn.cursor()
        print("DEBUG: Cursor creado exitosamente")
        
        # FORZAR A PUBLIC
        cursor.execute("SET search_path TO public;")
        conn.commit()
        print("DEBUG: Esquema forzado a 'public'")
        
        # VERIFICACIÓN FINAL: Probar consulta real
        cursor.execute("SELECT COUNT(*) as total FROM usuarios")
        result = cursor.fetchone()
        print(f"DEBUG: Consulta de prueba ejecutada - Total usuarios: {result}")
        
        cursor.close()
        print("DEBUG: Cursor cerrado")
        
        print("=== DEBUG: get_db_session() COMPLETADO ===")
        return conn
        
    except Exception as e:
        print(f"ERROR CRÍTICO en get_db_session(): {e}")
        print(f"ERROR: Tipo de error: {type(e).__name__}")
        import traceback
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        raise Exception("No se puede conectar a la base de datos local")

def get_connection():
        """CONEXIÓN DIRECTA HARDCODED - Sin dependencias externas"""
        try:
            print(f"=== CONEXIÓN HARDCODED DIRECTA ===")
            
            # CONEXIÓN DIRECTA Y EXPLÍCITA
            conn = psycopg2.connect(
                dbname="db_foc26",
                user="postgres", 
                password="admin123",
                host="localhost",
                port="5432"
            )
            
            print(f"OK: Conexión establecida directamente a db_foc26@localhost:5432")
            
            # FORZAR ESQUEMA PUBLIC
            cursor = conn.cursor()
            cursor.execute("SET search_path TO public;")
            conn.commit()
            cursor.close()
            
            print(f"OK: Esquema forzado a public")
            
            return conn
            
        except Exception as e:
            print(f"ERROR CRÍTICO en conexión directa: {e}")
            raise Exception(f"Conexión fallida: la base de datos no reconoce la tabla usuarios")

def verificar_y_forzar_schema():
    """Función de verificación y forzado de esquema con detención si es necesario"""
    try:
        print("=== VERIFICACIÓN Y FORZADO DE ESQUEMA ===")
        
        # Obtener conexión limpia
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # 1. Verificar base de datos actual
        cursor.execute("SELECT current_database();")
        current_db = cursor.fetchone()
        print(f"BASE DE DATOS CONECTADA: {current_db['current_database']}")
        
        # 2. Forzar esquema a public
        cursor.execute("SET search_path TO public;")
        conn.commit()
        print("ESQUEMA FORZADO A 'public'")
        
        # 3. Verificar tablas en esquema public
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables_result = cursor.fetchall()
        table_names = [table['table_name'] for table in tables_result]
        
        print(f"TABLAS DETECTADAS: {len(table_names)}")
        print(f"LISTA: {table_names}")
        
        # 4. VERIFICACIÓN CRÍTICA - Tabla usuarios
        if 'usuarios' not in table_names:
            # DETENER SISTEMA CON ERROR CLARO
            error_msg = f"TABLA 'usuarios' NO EXISTE - Tablas detectadas: {table_names}"
            print(f"ERROR CRÍTICO: {error_msg}")
            print(f"SISTEMA DETENIDO - Base de datos: {current_db['current_database']}")
            
            cursor.close()
            conn.close()
            
            # Detener el sistema completamente
            raise SystemExit(error_msg)
        
        # 5. Validar acceso a tabla usuarios
        cursor.execute("SELECT COUNT(*) FROM usuarios;")
        result = cursor.fetchone()
        user_count = result['count']
        
        print(f"OK: TABLA 'usuarios' VALIDADA - {user_count} registros")
        
        cursor.close()
        conn.close()
        
        return {
            'status': True,
            'message': f'Esquema verificado - {user_count} usuarios',
            'database': current_db['current_database'],
            'tables': table_names,
            'user_count': user_count
        }
        
    except SystemExit:
        # Re-lanzar SystemExit para detener completamente
        raise
    except Exception as e:
        error_msg = f"Error en verificación de esquema: {e}"
        print(f"ERROR: {error_msg}")
        raise SystemExit(error_msg)

def verificar_estado_sistema():
    """Verificar estado del sistema al iniciar la aplicación"""
    try:
        print("=== VERIFICANDO ESTADO DEL SISTEMA ===")
        
        # Usar función de verificación y forzado
        resultado = verificar_y_forzar_schema()
        
        if resultado['status']:
            print(f"OK: Sistema operativo - {resultado['user_count']} usuarios en la BD")
            return {
                'status': True,
                'message': f"Sistema operativo - {resultado['user_count']} usuarios",
                'user_count': resultado['user_count']
            }
        else:
            return resultado
        
    except SystemExit as e:
        # El sistema fue detenido intencionalmente
        print(f"SISTEMA DETENIDO: {e}")
        return {
            'status': False,
            'message': str(e),
            'system_stopped': True
        }
    except Exception as e:
        error_msg = str(e)
        print(f"ERROR CRÍTICO DEL SISTEMA: {error_msg}")
        
        return {
            'status': False,
            'message': error_msg,
            'error': error_msg
        }

# Funciones específicas para Formación Complementaria
def guardar_nueva_formacion(nombre_taller, descripcion, fecha_inicio, fecha_fin, cupo_maximo, 
                           estado, cedula_usuario_creador, codigo_certificado, tomo, folio, facilitador):
    """Guardar nueva formación complementaria con transaccionalidad"""
    try:
        profesor_cedula = None
        if facilitador:
            profesor = execute_query(
                "SELECT cedula_profesor FROM profesor WHERE cedula_profesor = %s",
                (facilitador,),
                fetch_one=True
            )
            if profesor:
                profesor_cedula = profesor.get('cedula_profesor') or next(iter(profesor.values()), None)

        conn = db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("BEGIN")

            query_insert_taller = """
            INSERT INTO taller (
                nombre_taller,
                descripcion_taller,
                cedula_profesor,
                capacidad_maxima,
                duracion_horas,
                fecha_inicio,
                fecha_fin,
                estado,
                tipo_taller
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_taller
            """

            cursor.execute(query_insert_taller, (
                nombre_taller,
                descripcion,
                profesor_cedula,
                cupo_maximo,
                20,
                fecha_inicio,
                fecha_fin,
                estado.lower() if estado else 'activo',
                'regular'
            ))
            id_taller = cursor.fetchone()['id_taller']

            query_insert_formacion = """
            INSERT INTO formacion_complementaria (
                id_taller,
                nombre,
                descripcion,
                horas,
                codigo_certificado,
                id_usuario
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_formacion
            """

            cursor.execute(query_insert_formacion, (
                id_taller,
                nombre_taller,
                descripcion,
                20,
                codigo_certificado,
                cedula_usuario_creador
            ))
            id_formacion = cursor.fetchone()['id_formacion']

            conn.commit()
            return {
                'success': True,
                'message': 'Formación complementaria creada exitosamente',
                'data': {
                    'id_taller': id_taller,
                    'id_formacion': id_formacion
                }
            }

        except Exception as e:
            conn.rollback()
            return {
                'success': False,
                'message': f'Error al guardar formación: {str(e)}'
            }

        finally:
            cursor.close()

    except Exception as e:
        return {
            'success': False,
            'message': f'Error al guardar formación: {str(e)}'
        }

def obtener_historial_formacion(limit=None):
    """Obtener historial de formaciones complementarias"""
    try:
        query = """
        SELECT id_formacion, id_taller, nombre, descripcion, horas, codigo_certificado,
               id_usuario, fecha_creacion, codigo_referencia
        FROM formacion_complementaria 
        ORDER BY id_formacion DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        result = execute_query(query, fetch_all=True)
        
        return {
            'success': True,
            'data': result if result else [],
            'count': len(result) if result else 0
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al obtener historial: {str(e)}',
            'data': [],
            'count': 0
        }

def actualizar_formacion(id_formacion, nombre_taller, descripcion, fecha_inicio, fecha_fin, 
                         cupo_maximo, estado, codigo_certificado, tomo, folio, facilitador):
    """Actualizar formación complementaria existente"""
    try:
        query_update = """
        UPDATE formacion_complementaria 
        SET nombre = %s, descripcion = %s, horas = %s, codigo_certificado = %s
        WHERE id_formacion = %s
        """
        
        transaction_queries = [(query_update, (
            nombre_taller, descripcion, cupo_maximo, codigo_certificado, id_formacion
        ))]
        
        result = execute_transaction(transaction_queries)
        
        return {
            'success': result.get('success', False),
            'message': 'Formación actualizada exitosamente' if result.get('success', False) else 'Error al actualizar formación'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al actualizar formación: {str(e)}'
        }

def eliminar_formacion(id_formacion):
    """Eliminar formación complementaria con validaciones"""
    try:
        # Verificar si hay inscripciones activas
        inscripciones_query = """
        SELECT COUNT(*) as count FROM inscripcion 
        WHERE id_taller = %s AND estado_inscripcion = 'Activa'
        """
        
        inscripciones_result = execute_query(inscripciones_query, (id_formacion,), fetch_one=True)
        
        if inscripciones_result and inscripciones_result['count'] > 0:
            return {
                'success': False,
                'message': f'No se puede eliminar. Hay {inscripciones_result["count"]} inscripciones activas.'
            }
        
        # Eliminar formación
        query_delete = "DELETE FROM formacion_complementaria WHERE id_formacion = %s"
        
        transaction_queries = [(query_delete, (id_formacion,))]
        
        result = execute_transaction(transaction_queries)
        
        return {
            'success': result.get('success', False),
            'message': 'Formación eliminada exitosamente' if result.get('success', False) else 'Error al eliminar formación'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al eliminar formación: {str(e)}'
        }

def obtener_formacion_por_id(id_formacion):
    """Obtener detalles de una formación específica"""
    try:
        query = """
        SELECT * FROM formacion_complementaria WHERE id_formacion = %s
        """
        
        result = execute_query(query, (id_formacion,), fetch_one=True)
        
        return {
            'success': True,
            'data': result
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al obtener formación: {str(e)}',
            'data': None
        }

# Funciones de Gestión de Usuarios (integradas desde usuarios.py)
def obtener_usuarios_registrados():
    """Obtiene la lista de usuarios registrados desde la base de datos"""
    try:
        query = """
        SELECT cedula_usuario, login_usuario, rol, activo, 
               CASE WHEN activo THEN 'Activo' ELSE 'Inactivo' END as estado
        FROM usuarios 
        ORDER BY cedula_usuario
        """
        resultado = execute_query(query, fetch_all=True)
        
        if resultado:
            return resultado
        else:
            return []
            
    except Exception as e:
        print(f"Error obteniendo usuarios: {e}")
        return []

def verificar_cedula_existente(cedula):
    """Verifica si la cédula ya existe en la base de datos"""
    try:
        query = "SELECT COUNT(*) as count FROM usuarios WHERE cedula_usuario = %s"
        resultado = execute_query(query, (cedula.strip(),), fetch_one=True)
        
        if resultado:
            return resultado['count'] > 0
        
        return False
    except Exception as e:
        print(f"Error verificando cédula existente: {e}")
        return False

def hash_password_sha256(password):
    """Genera hash SHA-256 de la contraseña"""
    import hashlib
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def crear_usuario_transaccional(cedula_usuario, login_usuario, contrasena, rol, activo=True):
    """Crear usuario con transaccionalidad"""
    try:
        # Verificar si cédula ya existe
        if verificar_cedula_existente(cedula_usuario):
            return {
                'success': False,
                'message': 'La cédula ya está registrada en el sistema'
            }
        
        # Hash de contraseña
        contrasena_hash = hash_password_sha256(contrasena)
        
        # Insertar usuario
        query_insert = """
        INSERT INTO usuarios (cedula_usuario, login_usuario, contrasena, rol, activo)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        transaction_queries = [(query_insert, (cedula_usuario, login_usuario, contrasena_hash, rol, activo))]
        
        result = execute_transaction(transaction_queries)
        
        return {
            'success': result.get('success', False),
            'message': 'Usuario creado exitosamente' if result.get('success', False) else 'Error al crear usuario'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al crear usuario: {str(e)}'
        }

def actualizar_usuario_transaccional(cedula_usuario, login_usuario=None, rol=None, activo=None):
    """Actualizar usuario con transaccionalidad"""
    try:
        # Construir query dinámico
        campos_actualizar = []
        valores = []
        
        if login_usuario is not None:
            campos_actualizar.append("login_usuario = %s")
            valores.append(login_usuario)
        
        if rol is not None:
            campos_actualizar.append("rol = %s")
            valores.append(rol)
        
        if activo is not None:
            campos_actualizar.append("activo = %s")
            valores.append(activo)
        
        if not campos_actualizar:
            return {
                'success': False,
                'message': 'No se especificaron campos para actualizar'
            }
        
        valores.append(cedula_usuario)
        
        query_update = f"""
        UPDATE usuarios 
        SET {', '.join(campos_actualizar)}
        WHERE cedula_usuario = %s
        """
        
        transaction_queries = [(query_update, tuple(valores))]
        
        result = execute_transaction(transaction_queries)
        
        return {
            'success': result.get('success', False),
            'message': 'Usuario actualizado exitosamente' if result.get('success', False) else 'Error al actualizar usuario'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al actualizar usuario: {str(e)}'
        }

def eliminar_usuario_transaccional(cedula_usuario):
    """Eliminar usuario con validaciones"""
    try:
        # Verificar si existe
        if not verificar_cedula_existente(cedula_usuario):
            return {
                'success': False,
                'message': 'El usuario no existe en el sistema'
            }
        
        # No permitir eliminar administradores si es el único
        if cedula_usuario == 'admin':
            return {
                'success': False,
                'message': 'No se puede eliminar el usuario administrador principal'
            }
        
        # Eliminar usuario
        query_delete = "DELETE FROM usuarios WHERE cedula_usuario = %s"
        
        transaction_queries = [(query_delete, (cedula_usuario,))]
        
        result = execute_transaction(transaction_queries)
        
        return {
            'success': result.get('success', False),
            'message': 'Usuario eliminado exitosamente' if result.get('success', False) else 'Error al eliminar usuario'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al eliminar usuario: {str(e)}'
        }

# Motor Transaccional Central - Unificación de Operaciones
class MotorTransaccionalCentral:
    """Motor central de operaciones transaccionales para todo el sistema"""
    
    def __init__(self):
        """Inicialización del motor central"""
        self.db_manager = DatabaseManager()
    
    def operacion_crud_unificada(self, tabla, operacion, datos=None, filtros=None, orden=None):
        """Operación CRUD unificada para cualquier tabla"""
        try:
            if operacion.upper() == 'CREATE':
                return self._crear_registro(tabla, datos)
            elif operacion.upper() == 'READ':
                return self._leer_registros(tabla, filtros, orden)
            elif operacion.upper() == 'UPDATE':
                return self._actualizar_registro(tabla, datos, filtros)
            elif operacion.upper() == 'DELETE':
                return self._eliminar_registro(tabla, filtros)
            else:
                return {'success': False, 'message': f'Operación {operacion} no válida'}
        except Exception as e:
            return {'success': False, 'message': f'Error en {operacion}: {str(e)}'}
    
    def _crear_registro(self, tabla, datos):
        """Crear registro en cualquier tabla con transaccionalidad"""
        try:
            if not datos:
                return {'success': False, 'message': 'Datos requeridos para CREATE'}
            
            # Construir query dinámico
            columnas = list(datos.keys())
            valores = list(datos.values())
            placeholders = ', '.join(['%s'] * len(columnas))
            
            query_insert = f"""
            INSERT INTO {tabla} ({', '.join(columnas)})
            VALUES ({placeholders})
            """
            
            transaction_queries = [(query_insert, tuple(valores))]
            result = execute_transaction(transaction_queries)
            
            return {
                'success': result.get('success', False),
                'message': f'Registro creado en {tabla}' if result.get('success', False) else f'Error al crear en {tabla}'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error CREATE {tabla}: {str(e)}'}
    
    def _leer_registros(self, tabla, filtros=None, orden=None):
        """Leer registros de cualquier tabla"""
        try:
            query_base = f"SELECT * FROM {tabla}"
            valores = []
            
            # Agregar filtros
            if filtros:
                condiciones = []
                for campo, valor in filtros.items():
                    condiciones.append(f"{campo} = %s")
                    valores.append(valor)
                query_base += f" WHERE {' AND '.join(condiciones)}"
            
            # Agregar orden
            if orden:
                query_base += f" ORDER BY {orden}"
            
            resultado = execute_query(query_base, tuple(valores) if valores else None, fetch_all=True)
            
            return {
                'success': True,
                'data': resultado if resultado else [],
                'count': len(resultado) if resultado else 0
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error READ {tabla}: {str(e)}', 'data': []}
    
    def _actualizar_registro(self, tabla, datos, filtros):
        """Actualizar registro en cualquier tabla"""
        try:
            if not datos or not filtros:
                return {'success': False, 'message': 'Datos y filtros requeridos para UPDATE'}
            
            # Construir query dinámico
            campos_actualizar = []
            valores = []
            
            for campo, valor in datos.items():
                campos_actualizar.append(f"{campo} = %s")
                valores.append(valor)
            
            # Agregar filtros WHERE
            condiciones_where = []
            for campo, valor in filtros.items():
                condiciones_where.append(f"{campo} = %s")
                valores.append(valor)
            
            query_update = f"""
            UPDATE {tabla}
            SET {', '.join(campos_actualizar)}
            WHERE {' AND '.join(condiciones_where)}
            """
            
            transaction_queries = [(query_update, tuple(valores))]
            result = execute_transaction(transaction_queries)
            
            return {
                'success': result.get('success', False),
                'message': f'Registro actualizado en {tabla}' if result.get('success', False) else f'Error al actualizar en {tabla}'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error UPDATE {tabla}: {str(e)}'}
    
    def _eliminar_registro(self, tabla, filtros):
        """Eliminar registro de cualquier tabla"""
        try:
            if not filtros:
                return {'success': False, 'message': 'Filtros requeridos para DELETE'}
            
            # Construir query dinámico
            condiciones = []
            valores = []
            
            for campo, valor in filtros.items():
                condiciones.append(f"{campo} = %s")
                valores.append(valor)
            
            query_delete = f"""
            DELETE FROM {tabla}
            WHERE {' AND '.join(condiciones)}
            """
            
            transaction_queries = [(query_delete, tuple(valores))]
            result = execute_transaction(transaction_queries)
            
            return {
                'success': result.get('success', False),
                'message': f'Registro eliminado de {tabla}' if result.get('success', False) else f'Error al eliminar de {tabla}'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error DELETE {tabla}: {str(e)}'}
    
    def validar_permiso_usuario(self, rol_usuario, modulo, accion):
        """Validación centralizada de permisos"""
        try:
            from seguridad import tiene_permiso
            return tiene_permiso(rol_usuario, modulo, accion)
        except Exception as e:
            print(f"Error validando permiso: {e}")
            return False
    
    def ejecutar_consulta_personalizada(self, query, parametros=None, fetch_one=False):
        """Ejecutar consulta SQL personalizada"""
        try:
            resultado = execute_query(query, parametros, fetch_one=fetch_one)
            
            return {
                'success': True,
                'data': resultado
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error en consulta personalizada: {str(e)}',
                'data': None
            }

# Instancia global del motor central
motor_central = MotorTransaccionalCentral()

# Función de compatibilidad
def ensure_admin_exists():
    """Asegurar que exista un usuario administrador"""
    try:
        # Verificar si existe administrador
        result = execute_query(
            "SELECT COUNT(*) as count FROM usuarios WHERE rol = 'Administrador'",
            fetch_one=True
        )
        
        if result.get('count', 0) == 0:
            # Crear administrador por defecto
            admin_password_hash = hash_password_sha256('admin123')
            admin_queries = [
                ("INSERT INTO persona (cedula, nombre, apellido, telefono, direccion) VALUES (%s, %s, %s, %s, %s)", 
                 ('V-00000000', 'Administrador', 'del Sistema', '0000000000', 'N/A')),
                ("INSERT INTO usuarios (cedula_usuario, login_usuario, contrasena, rol, activo) VALUES (%s, %s, %s, %s, %s)",
                 ('V-00000000', 'admin', admin_password_hash, 'Administrador', True))
            ]
            
            resultado = ejecutar_transaccion(admin_queries)
            if resultado['success']:
                logger.info("Administrador por defecto creado exitosamente")
            else:
                logger.error(f"Error creando administrador: {resultado['message']}")
        else:
            logger.info("Administrador ya existe en el sistema")
            
    except Exception as e:
        logger.error(f"Error verificando administrador: {e}")

def authenticate_user(username, password):
    """Autenticar usuario usando get_connection directo con homologación de cédulas."""
    try:
        import hashlib

        # Validación de entrada con tratamiento uniforme de tipos
        cleaned_username = str(username or "").strip()
        password_str = str(password or "")
        
        if not cleaned_username or not password_str:
            return {'success': False, 'message': 'Usuario o contraseña incorrectos'}

        # Generar múltiples formatos para búsqueda flexible sobre cédula/login
        possible_values = set()
        possible_values.add(cleaned_username)
        possible_values.add(cleaned_username.lower())
        possible_values.add(cleaned_username.upper())

        cedula_homologada = homologar_cedula(cleaned_username)
        possible_values.add(cedula_homologada)

        solo_digitos = ''.join(ch for ch in cleaned_username if ch.isdigit())
        if solo_digitos:
            possible_values.add(solo_digitos)
            possible_values.add(f"V-{solo_digitos}")
            possible_values.add(f"v-{solo_digitos}")
            possible_values.add(f"{solo_digitos}")

        if '.' in cleaned_username:
            sin_puntos = cleaned_username.replace('.', '')
            possible_values.add(sin_puntos)
            possible_values.add(sin_puntos.lower())
            possible_values.add(sin_puntos.upper())
            possible_values.add(homologar_cedula(sin_puntos))

        cedula_list = list(possible_values)
        placeholders = ', '.join(['%s'] * len(cedula_list))

        hashed_password = hashlib.sha256(password_str.encode('utf-8')).hexdigest()

        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            query = f"""
            SELECT u.cedula_usuario, u.login_usuario, u.rol, u.activo,
                   COALESCE(u.contrasena, u.password_hash, '') AS stored_password,
                   p.nombre, p.apellido, p.telefono, p.direccion
            FROM usuarios u
            LEFT JOIN persona p ON u.cedula_usuario = p.cedula
            WHERE (u.cedula_usuario IN ({placeholders}) OR u.login_usuario IN ({placeholders}))
              AND u.activo = TRUE
            LIMIT 1
            """

            cursor.execute(query, tuple(cedula_list + cedula_list))
            user_row = cursor.fetchone()

            if not user_row:
                return {'success': False, 'message': 'Usuario o contraseña incorrectos'}

            stored_password = str(user_row[4] or '').strip()
            password_ok = stored_password == hashed_password

            if not password_ok:
                return {'success': False, 'message': 'Usuario o contraseña incorrectos'}

            nombre_completo = f"{user_row[5] if user_row[5] else ''} {user_row[6] if user_row[6] else ''}".strip()
            rol_usuario = user_row[2] or 'Administrador'

            return {
                'success': True,
                'user': {
                    'cedula_usuario': user_row[0],
                    'login_usuario': user_row[1],
                    'rol': rol_usuario,
                    'nombre_completo': nombre_completo,
                    'telefono': user_row[7] if len(user_row) > 7 else None,
                    'direccion': user_row[8] if len(user_row) > 8 else None
                }
            }
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        logger.error(f"Error en autenticación: {e}")
        return {'success': False, 'message': f'Error de autenticación: {str(e)}'}

if __name__ == "__main__":
    # Test del gestor de base de datos
    print("Testing DatabaseManager...")
    result = get_database_info()
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Database Info: {result['database_info']}")
    close_database()
