#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config.py - Configuration Manager for SICADFOC 2026
Environment-based configuration with python-dotenv
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any
import urllib.parse

class ConfigManager:
    """
    Gestor de configuración centralizado con environment switching
    """
    
    def __init__(self):
        """Cargar configuración basada en APP_ENV"""
        load_dotenv()
        self._config = self._load_environment_config()
    
    def _load_environment_config(self) -> Dict[str, Any]:
        """Cargar configuración según ambiente con detección automática"""
        # Detectar automáticamente si está en producción (Render) o desarrollo local
        if self._is_render_environment() or self._has_database_url():
            return self._get_production_config()
        else:
            return self._get_development_config()
    
    def _is_render_environment(self) -> bool:
        """Detectar si está corriendo en Render"""
        return bool(os.getenv('RENDER') or os.getenv('RENDER_SERVICE_NAME'))
    
    def _has_database_url(self) -> bool:
        """Verificar si existe DATABASE_URL (ambiente de producción)"""
        return bool(os.getenv('DATABASE_URL'))
    
    def _get_development_config(self) -> Dict[str, Any]:
        """Configuración para desarrollo (base de datos local)"""
        return {
            'environment': 'development',
            'database': {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', 5432)),
                'database': os.getenv('DB_NAME', 'db_foc26'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', 'admin123'),
            },
            'pool': {
                'min_connections': 2,
                'max_connections': 10,
                'connection_timeout': 30,
            },
            'debug': os.getenv('APP_DEBUG', 'true').lower() == 'true',
            'log_level': os.getenv('APP_LOG_LEVEL', 'INFO'),
        }
    
    def _get_production_config(self) -> Dict[str, Any]:
        """Configuración para producción (base de datos en nube)"""
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL es requerida para producción")
        
        # Parsear DATABASE_URL
        parsed = urllib.parse.urlparse(database_url)
        
        return {
            'environment': 'production',
            'database': {
                'host': parsed.hostname or 'localhost',
                'port': parsed.port or 5432,
                'database': parsed.path[1:] if parsed.path else 'db_foc26',
                'user': parsed.username or 'postgres',
                'password': parsed.password or '',
            },
            'pool': {
                'min_connections': 2,
                'max_connections': 10,
                'connection_timeout': 30,
            },
            'debug': os.getenv('APP_DEBUG', 'false').lower() == 'true',
            'log_level': os.getenv('APP_LOG_LEVEL', 'WARNING'),
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Obtener configuración completa"""
        return self._config
    
    def get_database_config(self) -> Dict[str, Any]:
        """Obtener solo configuración de base de datos"""
        return self._config['database']
    
    def get_pool_config(self) -> Dict[str, Any]:
        """Obtener configuración de pool de conexiones"""
        return self._config['pool']
    
    def is_development(self) -> bool:
        """Verificar si está en modo desarrollo"""
        return self._config['environment'] == 'development'
    
    def is_production(self) -> bool:
        """Verificar si está en modo producción"""
        return self._config['environment'] == 'production'
    
    def get_environment(self) -> str:
        """Obtener ambiente actual"""
        return self._config['environment']

# Instancia global del gestor de configuración
config_manager = ConfigManager()

# Funciones de conveniencia para la aplicación
def get_config() -> Dict[str, Any]:
    """Obtener configuración completa"""
    return config_manager.get_config()

def get_database_config() -> Dict[str, Any]:
    """Obtener configuración de base de datos"""
    return config_manager.get_database_config()

def is_development() -> bool:
    """Verificar si está en modo desarrollo"""
    return config_manager.is_development()

def is_production() -> bool:
    """Verificar si está en modo producción"""
    return config_manager.is_production()

def get_environment() -> str:
    """Obtener ambiente actual"""
    return config_manager.get_environment()

def log_environment():
    """Mensaje para monitoreo del Technology Coordinator"""
    env = get_environment()
    print(f"Conectado exitosamente al ambiente: {env.upper()}")
