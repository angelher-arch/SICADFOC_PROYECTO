#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_config.py - Configuración específica para despliegue en Render
"""

import os
import logging
from urllib.parse import urlparse

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RenderConfig:
    """Configuración específica para entorno Render"""
    
    def __init__(self):
        self.database_url = None
        self.db_config = {}
        self.load_environment()
    
    def load_environment(self):
        """Cargar y validar variables de entorno"""
        
        # 1. Verificar DATABASE_URL (variable principal de Render)
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            logger.info("✅ DATABASE_URL encontrada en entorno")
            self.database_url = database_url
            self.parse_database_url()
        else:
            logger.error("❌ DATABASE_URL no encontrada en entorno")
            logger.info("Variables disponibles:")
            for key, value in os.environ.items():
                if 'DB' in key.upper() or 'DATABASE' in key.upper():
                    logger.info(f"  {key}: {'*' * 10 if 'PASSWORD' in key.upper() else value}")
            raise ValueError("DATABASE_URL es requerida para conexión a PostgreSQL")
    
    def parse_database_url(self):
        """Parsear DATABASE_URL y extraer componentes"""
        try:
            parsed = urlparse(self.database_url)
            
            self.db_config = {
                'dbname': parsed.path[1:],  # Remover el '/' inicial
                'user': parsed.username,
                'password': parsed.password,
                'host': parsed.hostname,
                'port': parsed.port or 5432,
                'sslmode': 'require'  # Render requiere SSL
            }
            
            # Loggear configuración (sin contraseña)
            safe_config = self.db_config.copy()
            safe_config['password'] = '*' * 8
            logger.info(f"Configuración parseada: {safe_config}")
            
        except Exception as e:
            logger.error(f"Error parseando DATABASE_URL: {e}")
            raise
    
    def get_connection_string(self):
        """Retornar cadena de conexión para psycopg2"""
        return self.database_url
    
    def get_psycopg2_params(self):
        """Retornar parámetros para psycopg2.connect()"""
        return self.db_config
    
    def debug_environment(self):
        """Imprimir información de debug del entorno"""
        logger.info("=== DEBUG DE ENTORNO RENDER ===")
        logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'no_definido')}")
        logger.info(f"Python version: {os.sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        # Verificar variables críticas
        critical_vars = ['DATABASE_URL', 'ENVIRONMENT', 'PORT']
        for var in critical_vars:
            value = os.getenv(var)
            if value:
                masked_value = value if 'PASSWORD' not in var else '*' * 10
                logger.info(f"✅ {var}: {masked_value}")
            else:
                logger.warning(f"❌ {var}: no definida")
        
        logger.info("=== FIN DEBUG ===")

# Función para obtener configuración
def get_render_config():
    """Obtener instancia de configuración Render"""
    return RenderConfig()

# Test de configuración
if __name__ == "__main__":
    try:
        config = get_render_config()
        config.debug_environment()
        print("✅ Configuración Render cargada exitosamente")
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
