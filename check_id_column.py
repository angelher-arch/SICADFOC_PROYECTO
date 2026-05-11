#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar el tipo de la columna id_taller en formacion_complementaria
"""

import psycopg2
from database import get_connection

def check_id_taller_column():
    """Verificar el tipo de la columna id_taller"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Consulta para obtener información de la columna específica
        query = """
            SELECT column_name, data_type, is_nullable, column_default, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'formacion_complementaria'
            AND column_name = 'id_taller';
        """
        
        cursor.execute(query)
        column_info = cursor.fetchone()
        
        if column_info:
            print("=== INFORMACIÓN DE LA COLUMNA id_taller ===")
            print(f"Column Name: {column_info[0]}")
            print(f"Data Type: {column_info[1]}")
            print(f"Nullable: {column_info[2]}")
            print(f"Default: {column_info[3]}")
            print(f"Max Length: {column_info[4]}")
            
            # Verificar si es SERIAL
            if 'serial' in column_info[1].lower() or 'integer' in column_info[1].lower():
                print("\n🔍 TIPO DETECTADO: INTEGER/SERIAL")
                print("✅ Puede usar valores numéricos")
            elif 'varchar' in column_info[1].lower() or 'character' in column_info[1].lower():
                print("\n🔍 TIPO DETECTADO: VARCHAR/CHARACTER")
                print("✅ Puede usar texto formateado como ID")
                print(f"⚠️  Longitud máxima: {column_info[4]} caracteres")
            else:
                print(f"\n🔍 TIPO DESCONOCIDO: {column_info[1]}")
        else:
            print("❌ La columna 'id_taller' no existe en la tabla 'formacion_complementaria'")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_id_taller_column()
