#!/usr/bin/env python3
"""
SICADFOC 2026 - Sistema de Backup Total
=====================================

Script para realizar backup completo del sistema:
1. Backup de código fuente (comprimido)
2. Backup de base de datos (PostgreSQL dump)

Autor: Ingeniería DevOps SICADFOC 2026
Fecha: 2026-04-29
"""

import os
import sys
import subprocess
import zipfile
import shutil
from datetime import datetime
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup_sistema.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BackupSistema:
    """Clase principal para backup completo del sistema SICADFOC 2026"""
    
    def __init__(self):
        self.fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = "backups_seguridad"
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        
        # Configuración de base de datos
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'db_foc26',
            'user': 'postgres',
            'password': 'admin123'
        }
        
        # Asegurar que existe el directorio de backups
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def backup_codigo_fuente(self):
        """Realizar backup del código fuente del proyecto"""
        try:
            logger.info("=== INICIANDO BACKUP DE CÓDIGO FUENTE ===")
            
            # Nombre del archivo de backup
            nombre_zip = f"SICADFOC2026_codigo_{self.fecha_actual}.zip"
            ruta_zip = os.path.join(self.backup_dir, nombre_zip)
            
            # Archivos y directorios a excluir (basado en .gitignore)
            exclusiones = {
                '__pycache__', '.git', '.vscode', '.idea',
                '.streamlit', 'backups_seguridad', '*.log',
                '*.tmp', '*.bak', '*.pyc', '*.pyo',
                '.env', '*.db', '*.sqlite', '*.sqlite3'
            }
            
            with zipfile.ZipFile(ruta_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.project_root):
                    # Excluir directorios no deseados
                    dirs[:] = [d for d in dirs if d not in exclusiones]
                    
                    for file in files:
                        # Excluir archivos no deseados
                        if not any(file.endswith(ext.replace('*', '')) for ext in exclusiones if ext.startswith('*')):
                            if not any(excl in file for excl in exclusiones if not excl.startswith('*')):
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, self.project_root)
                                zipf.write(file_path, arcname)
            
            # Verificar tamaño del backup
            tamaño_mb = os.path.getsize(ruta_zip) / (1024 * 1024)
            logger.info(f"Backup de código completado: {nombre_zip}")
            logger.info(f"Tamaño: {tamaño_mb:.2f} MB")
            
            return ruta_zip
            
        except Exception as e:
            logger.error(f"Error en backup de código fuente: {e}")
            return None
    
    def backup_base_datos(self):
        """Realizar backup de la base de datos PostgreSQL"""
        try:
            logger.info("=== INICIANDO BACKUP DE BASE DE DATOS ===")
            
            # Nombre del archivo de backup
            nombre_sql = f"SICADFOC2026_db_{self.fecha_actual}.sql"
            ruta_sql = os.path.join(self.backup_dir, nombre_sql)
            
            # Construir comando pg_dump
            pg_dump_cmd = [
                'pg_dump',
                f'--host={self.db_config["host"]}',
                f'--port={self.db_config["port"]}',
                f'--username={self.db_config["user"]}',
                f'--dbname={self.db_config["database"]}',
                '--verbose',
                '--clean',
                '--no-owner',
                '--no-privileges',
                '--create',
                f'--file={ruta_sql}'
            ]
            
            # Variable de entorno para contraseña
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            logger.info(f"Ejecutando pg_dump para base de datos: {self.db_config['database']}")
            
            # Ejecutar backup
            resultado = subprocess.run(
                pg_dump_cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos máximo
            )
            
            if resultado.returncode == 0:
                # Verificar tamaño del backup
                tamaño_mb = os.path.getsize(ruta_sql) / (1024 * 1024)
                logger.info(f"Backup de base de datos completado: {nombre_sql}")
                logger.info(f"Tamaño: {tamaño_mb:.2f} MB")
                
                # Verificar contenido básico
                with open(ruta_sql, 'r', encoding='utf-8') as f:
                    primeras_lineas = f.read(500)
                    if 'PostgreSQL database dump' in primeras_lineas:
                        logger.info("Backup de base de datos verificado - formato correcto")
                    else:
                        logger.warning("Backup de base de datos puede estar corrupto")
                
                return ruta_sql
            else:
                logger.error(f"Error en pg_dump: {resultado.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout en backup de base de datos (5 minutos)")
            return None
        except Exception as e:
            logger.error(f"Error en backup de base de datos: {e}")
            return None
    
    def generar_resumen(self, backup_codigo, backup_db):
        """Generar archivo de resumen del backup"""
        try:
            resumen_path = os.path.join(self.backup_dir, f"resumen_backup_{self.fecha_actual}.txt")
            
            with open(resumen_path, 'w', encoding='utf-8') as f:
                f.write("=== RESUMEN DE BACKUP SICADFOC 2026 ===\n")
                f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Proyecto: SICADFOC 2026 - Sistema Integral de Control Académico\n\n")
                
                f.write("ARCHIVOS GENERADOS:\n")
                f.write("-" * 50 + "\n")
                
                if backup_codigo:
                    tamaño_codigo = os.path.getsize(backup_codigo) / (1024 * 1024)
                    f.write(f"Código Fuente: {os.path.basename(backup_codigo)}\n")
                    f.write(f"  Tamaño: {tamaño_codigo:.2f} MB\n")
                
                if backup_db:
                    tamaño_db = os.path.getsize(backup_db) / (1024 * 1024)
                    f.write(f"Base de Datos: {os.path.basename(backup_db)}\n")
                    f.write(f"  Tamaño: {tamaño_db:.2f} MB\n")
                
                f.write("\nCONFIGURACIÓN DE BASE DE DATOS:\n")
                f.write("-" * 50 + "\n")
                f.write(f"Host: {self.db_config['host']}\n")
                f.write(f"Port: {self.db_config['port']}\n")
                f.write(f"Database: {self.db_config['database']}\n")
                f.write(f"User: {self.db_config['user']}\n")
                
                f.write("\nINSTRUCCIONES DE RESTAURACIÓN:\n")
                f.write("-" * 50 + "\n")
                f.write("1. Restaurar Base de Datos:\n")
                f.write("   psql -h localhost -U postgres -d db_foc26 < archivo_backup.sql\n\n")
                f.write("2. Restaurar Código Fuente:\n")
                f.write("   unzip archivo_codigo.zip -d /ruta/del/proyecto\n\n")
                f.write("3. Instalar Dependencias:\n")
                f.write("   pip install -r requirements.txt\n")
            
            logger.info(f"Resumen de backup generado: {os.path.basename(resumen_path)}")
            return resumen_path
            
        except Exception as e:
            logger.error(f"Error generando resumen: {e}")
            return None
    
    def limpiar_backups_antiguos(self, dias_retencion=7):
        """Eliminar backups más antiguos que el período de retención"""
        try:
            logger.info(f"=== LIMPIEZA DE BACKUPS ANTIGUOS (> {dias_retencion} días) ===")
            
            fecha_limite = datetime.now().timestamp() - (dias_retencion * 24 * 3600)
            eliminados = 0
            
            for archivo in os.listdir(self.backup_dir):
                ruta_archivo = os.path.join(self.backup_dir, archivo)
                
                if os.path.isfile(ruta_archivo):
                    fecha_modificacion = os.path.getmtime(ruta_archivo)
                    
                    if fecha_modificacion < fecha_limite:
                        os.remove(ruta_archivo)
                        eliminados += 1
                        logger.info(f"Eliminado backup antiguo: {archivo}")
            
            logger.info(f"Limpieza completada. {eliminados} archivos eliminados.")
            
        except Exception as e:
            logger.error(f"Error en limpieza de backups antiguos: {e}")
    
    def ejecutar_backup_completo(self):
        """Ejecutar el proceso completo de backup"""
        logger.info("=== INICIANDO BACKUP COMPLETO SICADFOC 2026 ===")
        logger.info(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Directorio del proyecto: {self.project_root}")
        
        # Ejecutar backups
        backup_codigo = self.backup_codigo_fuente()
        backup_db = self.backup_base_datos()
        
        # Generar resumen
        resumen = self.generar_resumen(backup_codigo, backup_db)
        
        # Limpiar backups antiguos
        self.limpiar_backups_antiguos()
        
        # Resumen final
        logger.info("=== BACKUP COMPLETO FINALIZADO ===")
        
        if backup_codigo and backup_db:
            logger.info("SUCCESS: Todos los backups completados exitosamente")
            return True
        else:
            logger.warning("WARNING: Algunos backups fallaron")
            return False

def main():
    """Función principal"""
    try:
        # Verificar que estamos en el directorio correcto
        if not os.path.exists('main.py'):
            logger.error("Error: No se encuentra main.py. Ejecute desde el directorio raíz del proyecto.")
            sys.exit(1)
        
        # Crear instancia y ejecutar backup
        backup_system = BackupSistema()
        exito = backup_system.ejecutar_backup_completo()
        
        if exito:
            logger.info("Backup completado exitosamente. Revise la carpeta 'backups_seguridad'.")
            sys.exit(0)
        else:
            logger.error("El backup encontró errores. Revise los logs.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Backup cancelado por el usuario.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
