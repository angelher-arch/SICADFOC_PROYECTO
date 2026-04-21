#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
database_config.py - Configuración centralizada de base de datos para entornos Local y Render
"""

import os
import logging
from urllib.parse import urlparse
import psycopg2
from psycopg2.extras import RealDictCursor

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Configuración centralizada y robusta para PostgreSQL"""
    
    def __init__(self):
        self.database_url = None
        self.db_config = {}
        self.is_cloud = False
        self.load_and_validate_config()
    
    def load_and_validate_config(self):
        """Cargar y validar configuración de base de datos"""
        
        # 1. Detectar entorno
        self.is_cloud = os.getenv('ENVIRONMENT', '').lower() in ['cloud', 'render', 'production']
        
        # 2. Obtener DATABASE_URL (obligatorio)
        self.database_url = os.getenv('DATABASE_URL')
        
        if not self.database_url:
            if self.is_cloud:
                # En producción, DATABASE_URL es obligatoria
                logger.error("CRÍTICO: DATABASE_URL no encontrada en entorno de producción")
                raise ValueError("DATABASE_URL es requerida en entorno de producción")
            else:
                # En local, construir desde variables individuales
                self.build_local_database_url()
        
        # 3. Validar y parsear URL
        self.validate_and_parse_url()
        
        # 4. Asegurar puerto 5432 si no está presente
        self.ensure_default_port()
        
        logger.info(f"Configuración {'Cloud' if self.is_cloud else 'Local'} cargada exitosamente")
    
    def build_local_database_url(self):
        """Construir DATABASE_URL para entorno local"""
        db_name = os.getenv('LOCAL_DB_NAME', 'FOC26DB')
        db_user = os.getenv('LOCAL_DB_USER', 'postgres')
        db_password = os.getenv('LOCAL_DB_PASSWORD', 'admin123')
        db_host = os.getenv('LOCAL_DB_HOST', 'localhost')
        db_port = os.getenv('LOCAL_DB_PORT', '5432')
        ssl_mode = os.getenv('LOCAL_DB_SSL_MODE', 'prefer')
        
        self.database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?sslmode={ssl_mode}"
        logger.info("DATABASE_URL construida para entorno local")
    
    def validate_and_parse_url(self):
        """Validar y parsear DATABASE_URL"""
        try:
            parsed = urlparse(self.database_url)
            
            # Validaciones básicas
            if not parsed.scheme or parsed.scheme not in ['postgresql', 'postgres']:
                raise ValueError(f"Esquema inválido: {parsed.scheme}. Debe ser 'postgresql://'")
            
            if not parsed.hostname:
                raise ValueError("Host no especificado en DATABASE_URL")
            
            if not parsed.username:
                raise ValueError("Usuario no especificado en DATABASE_URL")
            
            # Extraer componentes
            self.db_config = {
                'dbname': parsed.path[1:] if parsed.path else 'foc26db',
                'user': parsed.username,
                'password': parsed.password or '',
                'host': parsed.hostname,
                'port': parsed.port or 5432,
                'sslmode': self.extract_ssl_mode(parsed.query)
            }
            
            # Log seguro (sin contraseña)
            safe_config = self.db_config.copy()
            safe_config['password'] = '*' * len(safe_config['password']) if safe_config['password'] else '<vacía>'
            logger.info(f"Configuración parseada: {safe_config}")
            
        except Exception as e:
            logger.error(f"Error validando DATABASE_URL: {e}")
            raise
    
    def extract_ssl_mode(self, query_string):
        """Extraer sslmode de la query string"""
        if not query_string:
            return 'require' if self.is_cloud else 'prefer'
        
        params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
        return params.get('sslmode', 'require' if self.is_cloud else 'prefer')
    
    def ensure_default_port(self):
        """Asegurar que el puerto 5432 esté configurado"""
        if not self.db_config.get('port') or self.db_config['port'] == '':
            self.db_config['port'] = 5432
            logger.info("Puerto por defecto 5432 configurado")
    
    def get_connection_string(self):
        """Retornar cadena de conexión completa"""
        return self.database_url
    
    def get_psycopg2_params(self):
        """Retornar parámetros para psycopg2.connect()"""
        return self.db_config
    
    def is_production(self):
        """Verificar si es entorno de producción"""
        return self.is_cloud
    
    def debug_config(self):
        """Imprimir información de debug (sin credenciales)"""
        logger.info("=== DEBUG CONFIGURACIÓN BASE DE DATOS ===")
        logger.info(f"Entorno: {'Cloud/Producción' if self.is_cloud else 'Local/Desarrollo'}")
        logger.info(f"DATABASE_URL encontrada: {'Sí' if self.database_url else 'No'}")
        
        if self.db_config:
            safe_config = self.db_config.copy()
            safe_config['password'] = '*' * len(safe_config['password']) if safe_config['password'] else '<vacía>'
            logger.info(f"Configuración: {safe_config}")
        
        logger.info("=== FIN DEBUG ===")

# Instancia global
_db_config_instance = None

def get_database_config():
    """Obtener instancia de configuración de base de datos"""
    global _db_config_instance
    if _db_config_instance is None:
        _db_config_instance = DatabaseConfig()
    return _db_config_instance

# Función de compatibilidad
def get_database_url():
    """Retornar DATABASE_URL configurada"""
    return get_database_config().get_connection_string()

if __name__ == "__main__":
    # Test de configuración
    try:
        config = get_database_config()
        config.debug_config()
        print("Configuración de base de datos exitosa")
    except Exception as e:
        print(f"Error en configuración: {e}")
