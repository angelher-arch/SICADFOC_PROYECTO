#!/usr/bin/env python3
"""
Script de Migración de Datos para SICADFOC 2026 - Render
Migra datos de FOC26DB local a FOC26DBCloud en Render
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MigracionRender:
    """Clase para manejar migración de datos a Render"""
    
    def __init__(self):
        self.local_conn = None
        self.render_conn = None
        self.tablas_migrar = [
            'persona',
            'usuario', 
            'estudiante',
            'profesor',
            'formacion_complementaria',
            'inscripcion'
        ]
    
    def conectar_local(self):
        """Conectar a base de datos local FOC26DB"""
        try:
            logger.info("Conectando a base de datos local FOC26DB...")
            self.local_conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', '5432')),
                database=os.getenv('DB_NAME', 'FOC26DB'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', ''),
                cursor_factory=RealDictCursor
            )
            logger.info("Conexión local establecida exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error conectando a base local: {e}")
            return False
    
    def conectar_render(self):
        """Conectar a base de datos Render usando DATABASE_URL"""
        try:
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                logger.error("DATABASE_URL no encontrada en variables de entorno")
                return False
            
            logger.info("Conectando a base de datos Render (DATABASE_URL)...")
            self.render_conn = psycopg2.connect(
                database_url,
                cursor_factory=RealDictCursor
            )
            logger.info("Conexión Render establecida exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error conectando a Render: {e}")
            return False
    
    def verificar_esquemas(self):
        """Verificar que los esquemas sean idénticos"""
        try:
            logger.info("Verificando esquemas de base de datos...")
            
            # Obtener estructura de tablas locales
            local_schema = {}
            with self.local_conn.cursor() as cursor:
                for tabla in self.tablas_migrar:
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns 
                        WHERE table_name = %s 
                        ORDER BY ordinal_position
                    """, (tabla,))
                    local_schema[tabla] = cursor.fetchall()
            
            # Obtener estructura de tablas Render
            render_schema = {}
            with self.render_conn.cursor() as cursor:
                for tabla in self.tablas_migrar:
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns 
                        WHERE table_name = %s 
                        ORDER BY ordinal_position
                    """, (tabla,))
                    render_schema[tabla] = cursor.fetchall()
            
            # Comparar esquemas
            esquemas_iguales = True
            for tabla in self.tablas_migrar:
                if tabla not in local_schema or tabla not in render_schema:
                    logger.error(f"Tabla {tabla} no encontrada en una de las bases de datos")
                    esquemas_iguales = False
                    continue
                
                local_cols = {(col['column_name'], col['data_type']) for col in local_schema[tabla]}
                render_cols = {(col['column_name'], col['data_type']) for col in render_schema[tabla]}
                
                if local_cols != render_cols:
                    logger.error(f"Estructura de tabla {tabla} no coincide")
                    logger.error(f"Local: {local_cols}")
                    logger.error(f"Render: {render_cols}")
                    esquemas_iguales = False
                else:
                    logger.info(f"Tabla {tabla}: Esquema OK")
            
            return esquemas_iguales
            
        except Exception as e:
            logger.error(f"Error verificando esquemas: {e}")
            return False
    
    def limpiar_datos_render(self):
        """Limpiar datos existentes en Render antes de migrar"""
        try:
            logger.info("Limpiando datos existentes en Render...")
            
            # Orden de eliminación (respetar foreign keys)
            orden_eliminar = ['inscripcion', 'formacion_complementaria', 'estudiante', 'profesor', 'usuario', 'persona']
            
            with self.render_conn.cursor() as cursor:
                for tabla in orden_eliminar:
                    cursor.execute(f"DELETE FROM {tabla}")
                    logger.info(f"Datos eliminados de tabla {tabla}")
                
                self.render_conn.commit()
                logger.info("Datos de Render limpiados exitosamente")
                return True
                
        except Exception as e:
            logger.error(f"Error limpiando datos Render: {e}")
            self.render_conn.rollback()
            return False
    
    def migrar_tabla(self, tabla):
        """Migrar datos de una tabla específica"""
        try:
            logger.info(f"Migrando tabla: {tabla}")
            
            # Leer datos de local
            with self.local_conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {tabla}")
                datos = cursor.fetchall()
                logger.info(f"Leídos {len(datos)} registros de {tabla}")
            
            if not datos:
                logger.info(f"No hay datos para migrar en tabla {tabla}")
                return True
            
            # Insertar en Render
            with self.render_conn.cursor() as cursor:
                columnas = list(datos[0].keys())
                placeholders = ', '.join(['%s'] * len(columnas))
                columnas_str = ', '.join(columnas)
                
                query = f"INSERT INTO {tabla} ({columnas_str}) VALUES ({placeholders})"
                
                for registro in datos:
                    valores = [registro[col] for col in columnas]
                    cursor.execute(query, valores)
                
                self.render_conn.commit()
                logger.info(f"Migrados {len(datos)} registros a tabla {tabla}")
                return True
                
        except Exception as e:
            logger.error(f"Error migrando tabla {tabla}: {e}")
            self.render_conn.rollback()
            return False
    
    def migrar_todo(self):
        """Ejecutar migración completa"""
        try:
            logger.info("Iniciando migración completa a Render...")
            
            # Conectar a ambas bases de datos
            if not self.conectar_local():
                return False
            
            if not self.conectar_render():
                return False
            
            # Verificar esquemas
            if not self.verificar_esquemas():
                logger.error("Los esquemas no coinciden. Abortando migración.")
                return False
            
            # Limpiar datos existentes en Render
            if not self.limpiar_datos_render():
                return False
            
            # Migrar tablas en orden correcto
            orden_migrar = ['persona', 'usuario', 'estudiante', 'profesor', 'formacion_complementaria', 'inscripcion']
            
            for tabla in orden_migrar:
                if tabla in self.tablas_migrar:
                    if not self.migrar_tabla(tabla):
                        logger.error(f"Fallo migrando tabla {tabla}")
                        return False
            
            logger.info("Migración completada exitosamente!")
            return True
            
        except Exception as e:
            logger.error(f"Error en migración completa: {e}")
            return False
        finally:
            # Cerrar conexiones
            if self.local_conn:
                self.local_conn.close()
            if self.render_conn:
                self.render_conn.close()
    
    def generar_reporte(self):
        """Generar reporte de migración"""
        try:
            logger.info("Generando reporte de migración...")
            
            with self.render_conn.cursor() as cursor:
                reporte = {}
                for tabla in self.tablas_migrar:
                    cursor.execute(f"SELECT COUNT(*) as total FROM {tabla}")
                    resultado = cursor.fetchone()
                    reporte[tabla] = resultado['total']
            
            logger.info("REPORTE DE MIGRACIÓN:")
            logger.info("=" * 50)
            for tabla, count in reporte.items():
                logger.info(f"{tabla}: {count} registros")
            logger.info("=" * 50)
            
            return reporte
            
        except Exception as e:
            logger.error(f"Error generando reporte: {e}")
            return None

def main():
    """Función principal"""
    print("=" * 60)
    print("MIGRACIÓN SICADFOC 2026 - RENDER")
    print("=" * 60)
    print()
    
    # Verificar variables de entorno
    if not os.getenv('DATABASE_URL'):
        print("ERROR: DATABASE_URL no está configurada")
        print("Configure la variable de entorno con la URL de conexión a Render")
        return False
    
    # Ejecutar migración
    migrador = MigracionRender()
    
    if migrador.migrar_todo():
        print("\nMIGRACIÓN COMPLETADA EXITOSAMENTE")
        
        # Generar reporte
        reporte = migrador.generar_reporte()
        if reporte:
            print("\nResumen de datos migrados:")
            for tabla, count in reporte.items():
                print(f"  {tabla}: {count} registros")
        
        return True
    else:
        print("\nERROR: La migración falló. Revise los logs para detalles.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
