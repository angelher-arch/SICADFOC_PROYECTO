#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_sincronizacion.py - Sincronización automática de base de datos
SICADFOC 2026 - Instituto Universitario Jesus Obrero
"""

import os
import sys
import subprocess
import logging
from typing import Dict, Any

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_database_empty() -> bool:
    """Verificar si la base de datos está vacía"""
    try:
        from database import DatabaseManager
        
        db_manager = DatabaseManager()
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Contar tablas en el esquema public
        cursor.execute("""
            SELECT COUNT(*) as table_count 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        result = cursor.fetchone()
        table_count = result['table_count'] if result else 0
        
        conn.close()
        
        logger.info(f"Tablas encontradas: {table_count}")
        return table_count < 5  # Considerar vacía si hay menos de 5 tablas
        
    except Exception as e:
        logger.error(f"Error verificando si la base de datos está vacía: {e}")
        return False

def execute_sincronizacion_script() -> Dict[str, Any]:
    """Ejecutar script de sincronización"""
    try:
        from config import get_database_config
        config = get_database_config()
        
        script_path = os.path.join(os.path.dirname(__file__), 'sincronizacion_tablas.sql')
        
        if not os.path.exists(script_path):
            return {
                'status': False,
                'error': f"Script no encontrado: {script_path}",
                'message': "El archivo sincronizacion_tablas.sql no existe"
            }
        
        # Construir comando psql
        psql_cmd = [
            'psql',
            f'-d{config["database"]}',
            f'-h{config["host"]}',
            f'-p{config["port"]}',
            f'-U{config["user"]}',
            '-f', script_path
        ]
        
        logger.info(f"Ejecutando: {' '.join(psql_cmd)}")
        
        # Ejecutar el script
        result = subprocess.run(
            psql_cmd,
            capture_output=True,
            text=True,
            timeout=60  # Timeout de 60 segundos
        )
        
        if result.returncode == 0:
            logger.info("Script de sincronización ejecutado exitosamente")
            return {
                'status': True,
                'message': 'Sincronización completada exitosamente',
                'output': result.stdout,
                'return_code': result.returncode
            }
        else:
            logger.error(f"Error ejecutando script: {result.stderr}")
            return {
                'status': False,
                'error': result.stderr,
                'output': result.stdout,
                'return_code': result.returncode,
                'message': 'Error durante la ejecución del script'
            }
            
    except subprocess.TimeoutExpired:
        return {
            'status': False,
            'error': 'Timeout ejecutando script',
            'message': 'La ejecución del script tomó demasiado tiempo'
        }
    except Exception as e:
        logger.error(f"Error ejecutando sincronización: {e}")
        return {
            'status': False,
            'error': str(e),
            'message': 'Error inesperado durante la sincronización'
        }

def auto_sincronize_if_needed() -> Dict[str, Any]:
    """Sincronizar automáticamente si la base de datos está vacía"""
    try:
        logger.info("Verificando si se requiere sincronización automática...")
        
        # Verificar si la base de datos está vacía
        if not check_database_empty():
            logger.info("Base de datos ya contiene datos - no se requiere sincronización")
            return {
                'status': True,
                'message': 'Base de datos ya inicializada',
                'action': 'none'
            }
        
        logger.warning("Base de datos vacía o incompleta - iniciando sincronización automática")
        
        # Ejecutar sincronización
        result = execute_sincronizacion_script()
        
        if result['status']:
            logger.info("Sincronización automática completada exitosamente")
            return {
                'status': True,
                'message': 'Base de datos sincronizada automáticamente',
                'action': 'synchronized',
                'details': result
            }
        else:
            logger.error("Falló la sincronización automática")
            return {
                'status': False,
                'message': 'Falló la sincronización automática',
                'action': 'failed',
                'details': result
            }
            
    except Exception as e:
        logger.error(f"Error en sincronización automática: {e}")
        return {
            'status': False,
            'error': str(e),
            'message': 'Error crítico en sincronización automática'
        }

def main():
    """Función principal para ejecutar sincronización automática"""
    print("=" * 80)
    print("SINCRONIZACIÓN AUTOMÁTICA - SICADFOC 2026")
    print("Instituto Universitario Jesus Obrero")
    print("=" * 80)
    
    result = auto_sincronize_if_needed()
    
    print(f"\nEstado: {'EXITOSO' if result['status'] else 'FALLIDO'}")
    print(f"Mensaje: {result['message']}")
    
    if 'action' in result:
        print(f"Acción: {result['action']}")
    
    if 'details' in result and result['details']:
        print("\nDetalles:")
        if 'output' in result['details']:
            print(result['details']['output'][:500] + "..." if len(result['details']['output']) > 500 else result['details']['output'])
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
