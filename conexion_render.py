#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
conexion_render.py - Conexión optimizada para PostgreSQL en Render
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from render_config import get_render_config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConexionRender:
    """Clase especializada para conexión en Render"""
    
    def __init__(self):
        self.db = None
        self.db_connected = False
        self.config = None
        self.connection_attempts = 0
        self.max_attempts = 3
    
    def conectar(self):
        """Conectar a PostgreSQL en Render con robustez"""
        
        # Cargar configuración específica de Render
        try:
            self.config = get_render_config()
            logger.info("Configuración Render cargada exitosamente")
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return False
        
        # Intentar conexión con reintentos
        for attempt in range(self.max_attempts):
            self.connection_attempts = attempt + 1
            logger.info(f"Intento de conexión {self.connection_attempts}/{self.max_attempts}")
            
            try:
                # Usar DATABASE_URL directamente (método recomendado por Render)
                connection_string = self.config.get_connection_string()
                
                logger.info("Conectando a PostgreSQL...")
                logger.info(f"Host: {self.config.db_config['host']}")
                logger.info(f"Database: {self.config.db_config['dbname']}")
                logger.info(f"User: {self.config.db_config['user']}")
                logger.info(f"SSL Mode: {self.config.db_config['sslmode']}")
                
                # Conectar con psycopg2 usando la URL completa
                self.db = psycopg2.connect(
                    connection_string,
                    cursor_factory=RealDictCursor,
                    connect_timeout=30,  # Mayor timeout para Render
                    application_name="SICADFOC2026"
                )
                
                # Configuración optimizada para Render
                self.db.set_client_encoding('UTF8')  # UTF8 es mejor que LATIN1
                
                # Probar conexión con consulta simple
                with self.db.cursor() as cursor:
                    cursor.execute("SELECT version(), current_database(), current_user")
                    resultado = cursor.fetchone()
                    logger.info(f"✅ Conexión exitosa a PostgreSQL")
                    logger.info(f"Versión: {resultado['version'][:50]}...")
                    logger.info(f"Base de datos: {resultado['current_database']}")
                    logger.info(f"Usuario: {resultado['current_user']}")
                
                self.db_connected = True
                return True
                
            except psycopg2.OperationalError as e:
                logger.error(f"Error operativo (intento {self.connection_attempts}): {e}")
                if "password authentication failed" in str(e).lower():
                    logger.error("❌ Error de autenticación - Verificar DATABASE_URL")
                    break
                elif "connection refused" in str(e).lower():
                    logger.error("❌ Conexión rechazada - Verificar host y puerto")
                    break
                elif "timeout" in str(e).lower():
                    logger.warning("⏰ Timeout - Reintentando...")
                    continue
                    
            except Exception as e:
                logger.error(f"Error inesperado (intento {self.connection_attempts}): {e}")
                break
        
        self.db_connected = False
        self.db = None
        return False
    
    def ejecutar_consulta(self, query, params=None):
        """Ejecutar consulta SELECT con manejo de errores"""
        try:
            if not self.db_connected or not self.db:
                logger.error("Base de datos no conectada")
                return None
            
            with self.db.cursor() as cursor:
                cursor.execute(query, params or ())
                resultado = cursor.fetchall()
                return resultado
                
        except psycopg2.Error as e:
            logger.error(f"Error PostgreSQL en consulta: {e}")
            logger.error(f"Query: {query[:100]}...")
            return None
        except Exception as e:
            logger.error(f"Error general en consulta: {e}")
            return None
    
    def ejecutar_actualizacion(self, query, params=None):
        """Ejecutar INSERT, UPDATE, DELETE con transacción segura"""
        try:
            if not self.db_connected or not self.db:
                logger.error("Base de datos no conectada")
                return {'exito': False, 'error': 'Base de datos no conectada'}
            
            with self.db.cursor() as cursor:
                cursor.execute(query, params or ())
                affected_rows = cursor.rowcount
                self.db.commit()
                
                logger.info(f"Query ejecutado: {affected_rows} filas afectadas")
                return {'exito': True, 'filas_afectadas': affected_rows}
                
        except psycopg2.Error as e:
            logger.error(f"Error PostgreSQL en actualización: {e}")
            logger.error(f"Query: {query[:100]}...")
            if self.db:
                self.db.rollback()
            return {'exito': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error general en actualización: {e}")
            if self.db:
                self.db.rollback()
            return {'exito': False, 'error': str(e)}
    
    def test_connection(self):
        """Probar conexión con consulta completa"""
        try:
            resultado = self.ejecutar_consulta("""
                SELECT 
                    version() as postgresql_version,
                    current_database() as database_name,
                    current_user as current_user,
                    inet_server_addr() as server_ip,
                    inet_server_port() as server_port
            """)
            
            if resultado:
                logger.info("✅ Test de conexión exitoso:")
                for key, value in resultado[0].items():
                    logger.info(f"  {key}: {value}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error en test de conexión: {e}")
            return False
    
    def desconectar(self):
        """Cerrar conexión de forma segura"""
        try:
            if self.db:
                self.db.close()
                self.db_connected = False
                logger.info("Conexión cerrada")
        except Exception as e:
            logger.error(f"Error cerrando conexión: {e}")

# Instancia global para compatibilidad
_conexion_render_instance = None

def get_conexion_render():
    """Obtener instancia de conexión Render"""
    global _conexion_render_instance
    if _conexion_render_instance is None:
        _conexion_render_instance = ConexionRender()
    return _conexion_render_instance

# Funciones compatibles con código existente
def conectar_foc26db_render():
    """Conectar a FOC26DB en Render"""
    conexion = get_conexion_render()
    return conexion.conectar()

def get_db_render():
    """Obtener conexión de base de datos Render"""
    return get_conexion_render().db

def is_connected_render():
    """Verificar estado de conexión Render"""
    return get_conexion_render().db_connected

# Test standalone
if __name__ == "__main__":
    logger.info("=== TEST DE CONEXIÓN RENDER ===")
    
    conexion = get_conexion_render()
    
    if conexion.conectar():
        logger.info("✅ Conexión establecida")
        
        if conexion.test_connection():
            logger.info("✅ Test de conexión exitoso")
        else:
            logger.error("❌ Test de conexión falló")
        
        conexion.desconectar()
    else:
        logger.error("❌ No se pudo establecer conexión")
    
    logger.info("=== FIN TEST ===")
