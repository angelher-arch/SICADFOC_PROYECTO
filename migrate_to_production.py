#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
migrate_to_production.py - Script de migración para SICADFOC 2026
Script para sincronizar cambios estructurales de base de datos local a producción (Render)
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from config import get_database_config, is_production, log_environment
from dotenv import load_dotenv

class DatabaseMigrator:
    """Gestor de migración entre ambientes"""
    
    def __init__(self):
        load_dotenv()
        self.local_config = self._get_local_config()
        self.production_config = self._get_production_config()
        
    def _get_local_config(self):
        """Configuración de base de datos local"""
        return {
            'host': 'localhost',
            'port': 5432,
            'database': 'db_foc26',
            'user': 'postgres',
            'password': os.getenv('DB_PASSWORD', 'admin123'),
            'sslmode': 'prefer'
        }
    
    def _get_production_config(self):
        """Configuración de base de datos de producción"""
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL no encontrada. Configure las variables de producción.")
        
        import urllib.parse
        parsed = urllib.parse.urlparse(database_url)
        
        return {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path[1:],
            'user': parsed.username,
            'password': parsed.password,
            'sslmode': 'require'
        }
    
    def get_connection(self, config):
        """Obtener conexión con configuración específica"""
        try:
            conn = psycopg2.connect(**config)
            conn.autocommit = False
            return conn
        except Exception as e:
            print(f"Error conectando a base de datos: {e}")
            return None
    
    def get_table_schema(self, conn, table_name):
        """Obtener esquema de una tabla"""
        try:
            cursor = conn.cursor()
            query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
            """
            cursor.execute(query, (table_name,))
            columns = cursor.fetchall()
            cursor.close()
            return columns
        except Exception as e:
            print(f"Error obteniendo esquema de {table_name}: {e}")
            return []
    
    def get_table_indexes(self, conn, table_name):
        """Obtener índices de una tabla"""
        try:
            cursor = conn.cursor()
            query = """
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = %s
            """
            cursor.execute(query, (table_name,))
            indexes = cursor.fetchall()
            cursor.close()
            return indexes
        except Exception as e:
            print(f"Error obteniendo índices de {table_name}: {e}")
            return []
    
    def get_table_constraints(self, conn, table_name):
        """Obtener restricciones de una tabla"""
        try:
            cursor = conn.cursor()
            query = """
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints
            WHERE table_name = %s
            """
            cursor.execute(query, (table_name,))
            constraints = cursor.fetchall()
            cursor.close()
            return constraints
        except Exception as e:
            print(f"Error obteniendo restricciones de {table_name}: {e}")
            return []
    
    def compare_schemas(self, local_conn, prod_conn):
        """Comparar esquemas entre local y producción"""
        print("\n🔍 COMPARANDO ESQUEMAS DE BASE DE DATOS...")
        
        # Obtener lista de tablas locales
        local_cursor = local_conn.cursor()
        local_cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        local_tables = [row[0] for row in local_cursor.fetchall()]
        local_cursor.close()
        
        # Obtener lista de tablas de producción
        prod_cursor = prod_conn.cursor()
        prod_cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        prod_tables = [row[0] for row in prod_cursor.fetchall()]
        prod_cursor.close()
        
        print(f"\n📊 Tablas locales: {len(local_tables)}")
        print(f"📊 Tablas producción: {len(prod_tables)}")
        
        # Tablas faltantes en producción
        missing_in_prod = set(local_tables) - set(prod_tables)
        if missing_in_prod:
            print(f"\n❌ Tablas faltantes en producción: {missing_in_prod}")
        
        # Tablas extra en producción
        extra_in_prod = set(prod_tables) - set(local_tables)
        if extra_in_prod:
            print(f"⚠️  Tablas extra en producción: {extra_in_prod}")
        
        # Comparar esquemas de tablas comunes
        common_tables = set(local_tables) & set(prod_tables)
        schema_differences = []
        
        for table in common_tables:
            local_schema = self.get_table_schema(local_conn, table)
            prod_schema = self.get_table_schema(prod_conn, table)
            
            if len(local_schema) != len(prod_schema):
                schema_differences.append(table)
                print(f"⚠️  Diferencia en columnas de tabla: {table}")
        
        return missing_in_prod, extra_in_prod, schema_differences
    
    def generate_migration_script(self, missing_tables):
        """Generar script de migración para tablas faltantes"""
        if not missing_tables:
            return None
        
        print(f"\n📝 Generando script de migración para {len(missing_tables)} tablas...")
        
        # Leer el script de sincronización original
        script_path = os.path.join(os.path.dirname(__file__), 'sincronizacion_tablas.sql')
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                full_script = f.read()
            
            # Extraer solo las tablas faltantes
            migration_lines = []
            current_table = None
            in_create_statement = False
            
            for line in full_script.split('\n'):
                line_upper = line.upper().strip()
                
                # Detectar inicio de CREATE TABLE
                if line_upper.startswith('CREATE TABLE IF NOT EXISTS'):
                    in_create_statement = True
                    # Extraer nombre de tabla
                    table_name = line.split('(')[0].split()[-1].strip()
                    current_table = table_name
                    
                    if current_table in missing_tables:
                        migration_lines.append(line)
                
                # Continuar líneas si estamos en una tabla faltante
                elif in_create_statement and current_table in missing_tables:
                    migration_lines.append(line)
                    
                    # Detectar fin de CREATE TABLE
                    if line.strip().endswith(');'):
                        in_create_statement = False
                        current_table = None
                        migration_lines.append('')  # Línea en blanco separadora
            
            if migration_lines:
                migration_script = '\n'.join(migration_lines)
                return migration_script
            else:
                print("⚠️  No se encontraron definiciones de tablas en el script original")
                return None
                
        except Exception as e:
            print(f"❌ Error leyendo script de sincronización: {e}")
            return None
    
    def execute_migration(self, prod_conn, migration_script):
        """Ejecutar script de migración en producción"""
        if not migration_script:
            print("⚠️  No hay script de migración para ejecutar")
            return False
        
        print("\n🚀 EJECUTANDO MIGRACIÓN EN PRODUCCIÓN...")
        print("⚠️  ESTA ACCIÓN MODIFICARÁ LA BASE DE DATOS DE PRODUCCIÓN")
        
        confirm = input("¿Desea continuar? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Migración cancelada")
            return False
        
        try:
            cursor = prod_conn.cursor()
            
            # Ejecutar script completo
            cursor.execute(migration_script)
            prod_conn.commit()
            
            cursor.close()
            print("✅ Migración ejecutada exitosamente")
            return True
            
        except Exception as e:
            prod_conn.rollback()
            print(f"❌ Error ejecutando migración: {e}")
            return False
    
    def run_migration(self):
        """Ejecutar proceso completo de migración"""
        print("🔄 SICADFOC 2026 - Script de Migración a Producción")
        print("=" * 60)
        
        # Conectar a base de datos local
        print("\n🔌 Conectando a base de datos local...")
        local_conn = self.get_connection(self.local_config)
        if not local_conn:
            print("❌ No se pudo conectar a base de datos local")
            return False
        
        # Conectar a base de datos de producción
        print("\n🔌 Conectando a base de datos de producción...")
        prod_conn = self.get_connection(self.production_config)
        if not prod_conn:
            print("❌ No se pudo conectar a base de datos de producción")
            local_conn.close()
            return False
        
        try:
            # Comparar esquemas
            missing_tables, extra_tables, schema_diffs = self.compare_schemas(local_conn, prod_conn)
            
            if not missing_tables and not schema_diffs:
                print("\n✅ No se requieren migraciones. Las bases de datos están sincronizadas.")
                return True
            
            # Generar script de migración
            migration_script = self.generate_migration_script(missing_tables)
            
            if migration_script:
                print(f"\n📄 Script de migración generado:")
                print("-" * 40)
                print(migration_script[:500] + "..." if len(migration_script) > 500 else migration_script)
                print("-" * 40)
                
                # Ejecutar migración
                success = self.execute_migration(prod_conn, migration_script)
                
                if success:
                    print("\n🎉 Migración completada exitosamente")
                    print("📊 Base de datos de producción actualizada")
                else:
                    print("\n❌ La migración falló")
                
                return success
            else:
                print("\n⚠️  No se pudo generar script de migración")
                return False
                
        finally:
            local_conn.close()
            prod_conn.close()

def main():
    """Función principal"""
    print("🚀 SICADFOC 2026 - Herramienta de Migración")
    print("🔄 Sincronización de base de datos local a producción (Render)")
    
    # Verificar que no estemos en producción
    if is_production():
        print("❌ Este script debe ejecutarse solo en ambiente local")
        print("📍 Ambiente actual: PRODUCCIÓN")
        return False
    
    try:
        migrator = DatabaseMigrator()
        return migrator.run_migration()
        
    except Exception as e:
        print(f"❌ Error en proceso de migración: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
