#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para ejecutar la migración de la tabla inscripciones_talleres
"""

import psycopg2
from database import get_connection

def main():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("🔄 Ejecutando migración de tabla inscripciones_talleres...")

        # Leer y ejecutar el script de migración
        with open('fix_inscripciones_table.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()

        cursor.execute(sql_script)
        conn.commit()

        print('✅ Migración de tabla inscripciones_talleres ejecutada exitosamente')

        # Verificar el resultado
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'inscripciones_talleres'
            AND column_name = 'id_facilitador'
        """)

        result = cursor.fetchone()
        if result:
            print(f'✅ Columna id_facilitador: {result[1]} (nullable: {result[2]})')
        else:
            print('❌ Columna id_facilitador no encontrada')

    except Exception as e:
        print(f'❌ Error en migración: {e}')
        import traceback
        traceback.print_exc()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()