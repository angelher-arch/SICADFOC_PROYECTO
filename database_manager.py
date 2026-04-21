#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
database_manager.py - Gestor centralizado de base de datos con transacciones robustas
"""

import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from database_config import get_database_config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor centralizado de base de datos con manejo robusto de transacciones"""
    
    def __init__(self):
        self.config = get_database_config()
        self.connection = None
        self.is_connected = False
        self.connection_pool_size = 1
    
    def connect(self):
        """Establecer conexión a la base de datos"""
        try:
            logger.info("Conectando a la base de datos...")
            
            # Usar configuración centralizada
            connection_string = self.config.get_connection_string()
            
            self.connection = psycopg2.connect(
                connection_string,
                cursor_factory=RealDictCursor,
                connect_timeout=30,
                application_name="SICADFOC2026_CloudReady"
            )
            
            # Configuración optimizada
            self.connection.set_client_encoding('UTF8')
            
            # Configurar autocommit en False para manejo explícito de transacciones
            self.connection.autocommit = False
            
            self.is_connected = True
            logger.info("Conexión establecida exitosamente")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Error conectando a base de datos: {e}")
            self.is_connected = False
            self.connection = None
            return False
    
    def disconnect(self):
        """Cerrar conexión de forma segura"""
        try:
            if self.connection:
                self.connection.close()
                self.is_connected = False
                logger.info("Conexión cerrada")
        except Exception as e:
            logger.error(f"Error cerrando conexión: {e}")
    
    def health_check(self):
        """Health check de la conexión"""
        try:
            if not self.is_connected or not self.connection:
                return False
            
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1 as health_check")
                result = cursor.fetchone()
                return result and result['health_check'] == 1
                
        except Exception as e:
            logger.error(f"Error en health check: {e}")
            return False
    
    @contextmanager
    def get_cursor(self):
        """Context manager para cursor con manejo automático de errores"""
        if not self.is_connected or not self.connection:
            raise RuntimeError("Base de datos no conectada")
        
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
        finally:
            cursor.close()
    
    def execute_query(self, query, params=None, fetch_all=True):
        """Ejecutar consulta SELECT con manejo robusto de errores"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                
                if fetch_all:
                    result = cursor.fetchall()
                else:
                    result = cursor.fetchone()
                
                logger.debug(f"Consulta ejecutada: {len(result) if isinstance(result, list) else 1} filas")
                return result
                
        except psycopg2.Error as e:
            logger.error(f"Error en consulta SELECT: {e}")
            logger.error(f"Query: {query[:100]}...")
            return None
        except Exception as e:
            logger.error(f"Error general en consulta: {e}")
            return None
    
    def execute_update(self, query, params=None):
        """Ejecutar INSERT, UPDATE, DELETE con commit explícito"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                affected_rows = cursor.rowcount
                
                # Commit explícito
                self.connection.commit()
                
                logger.info(f"Transacción ejecutada: {affected_rows} filas afectadas")
                return {
                    'exito': True,
                    'filas_afectadas': affected_rows,
                    'error': None
                }
                
        except psycopg2.Error as e:
            logger.error(f"Error en transacción: {e}")
            logger.error(f"Query: {query[:100]}...")
            
            # Rollback explícito
            if self.connection:
                try:
                    self.connection.rollback()
                    logger.info("Rollback ejecutado")
                except Exception as rollback_error:
                    logger.error(f"Error en rollback: {rollback_error}")
            
            return {
                'exito': False,
                'filas_afectadas': 0,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error general en transacción: {e}")
            
            # Rollback explícito
            if self.connection:
                try:
                    self.connection.rollback()
                except Exception:
                    pass
            
            return {
                'exito': False,
                'filas_afectadas': 0,
                'error': str(e)
            }
    
    def execute_transaction(self, queries):
        """Ejecutar múltiples queries en una sola transacción"""
        try:
            with self.get_cursor() as cursor:
                results = []
                
                for query_data in queries:
                    if isinstance(query_data, dict):
                        query = query_data['query']
                        params = query_data.get('params')
                    else:
                        query = query_data
                        params = None
                    
                    cursor.execute(query, params)
                    
                    if query.strip().upper().startswith('SELECT'):
                        result = cursor.fetchall()
                        results.append(result)
                    else:
                        results.append({'filas_afectadas': cursor.rowcount})
                
                # Commit único para toda la transacción
                self.connection.commit()
                
                logger.info(f"Transacción múltiple ejecutada: {len(queries)} queries")
                return {
                    'exito': True,
                    'resultados': results,
                    'error': None
                }
                
        except psycopg2.Error as e:
            logger.error(f"Error en transacción múltiple: {e}")
            
            # Rollback explícito
            if self.connection:
                try:
                    self.connection.rollback()
                except Exception:
                    pass
            
            return {
                'exito': False,
                'resultados': [],
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error general en transacción múltiple: {e}")
            
            # Rollback explícito
            if self.connection:
                try:
                    self.connection.rollback()
                except Exception:
                    pass
            
            return {
                'exito': False,
                'resultados': [],
                'error': str(e)
            }
    
    def test_connection(self):
        """Test completo de conexión"""
        try:
            result = self.execute_query("""
                SELECT 
                    version() as postgresql_version,
                    current_database() as database_name,
                    current_user as current_user,
                    inet_server_addr() as server_ip,
                    inet_server_port() as server_port
            """)
            
            if result:
                logger.info("=== TEST DE CONEXIÓN EXITOSO ===")
                for key, value in result[0].items():
                    logger.info(f"{key}: {value}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error en test de conexión: {e}")
            return False

# Instancia global
_database_manager_instance = None

def get_database_manager():
    """Obtener instancia del gestor de base de datos"""
    global _database_manager_instance
    if _database_manager_instance is None:
        _database_manager_instance = DatabaseManager()
        # Conectar automáticamente
        _database_manager_instance.connect()
    return _database_manager_instance

# Funciones de compatibilidad con código existente
def conectar_foc26db():
    """Conectar a FOC26DB (función de compatibilidad)"""
    manager = get_database_manager()
    return manager.is_connected

def get_db():
    """Obtener conexión de base de datos"""
    manager = get_database_manager()
    return manager.connection

def is_connected():
    """Verificar estado de conexión"""
    manager = get_database_manager()
    return manager.is_connected

# Funciones CRUD mejoradas
def ejecutar_consulta(query, params=None):
    """Ejecutar consulta SELECT (compatibilidad)"""
    manager = get_database_manager()
    return manager.execute_query(query, params)

def ejecutar_actualizacion(query, params=None):
    """Ejecutar INSERT/UPDATE/DELETE (compatibilidad)"""
    manager = get_database_manager()
    return manager.execute_update(query, params)

def ejecutar_transaccion(queries):
    """Ejecutar transacción múltiple (compatibilidad)"""
    manager = get_database_manager()
    return manager.execute_transaction(queries)

if __name__ == "__main__":
    # Test del gestor
    logger.info("=== TEST DE DATABASE MANAGER ===")
    
    manager = get_database_manager()
    
    if manager.is_connected:
        logger.info("Conexión establecida")
        
        if manager.test_connection():
            logger.info("Test de conexión exitoso")
        else:
            logger.error("Test de conexión falló")
        
        manager.disconnect()
    else:
        logger.error("No se pudo establecer conexión")
    
    logger.info("=== FIN TEST ===")
