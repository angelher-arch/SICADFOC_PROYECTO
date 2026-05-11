#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar las columnas reales de la tabla formacion_complementaria
"""

import psycopg2
from database import get_connection

def check_table_columns():
    """Verificar las columnas exactas de la tabla formacion_complementaria"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Consulta para obtener información de las columnas
        query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'formacion_complementaria'
            ORDER BY ordinal_position;
        """
        
        cursor.execute(query)
        columns = cursor.fetchall()
        
        print("=== COLUMNAS DE LA TABLA formacion_complementaria ===")
        print(f"Total de columnas: {len(columns)}")
        print()
        
        for i, col in enumerate(columns, 1):
            print(f"{i}. {col[0]}")
            print(f"   Tipo: {col[1]}")
            print(f"   Nullable: {col[2]}")
            print(f"   Default: {col[3]}")
            print()
        
        cursor.close()
        conn.close()
        
        # Generar lista de nombres para copiar y pegar
        column_names = [col[0] for col in columns]
        print("=== LISTA DE COLUMNAS (para copiar) ===")
        print("columnas_bd = [")
        for i, col in enumerate(column_names):
            if i < len(column_names) - 1:
                print(f"    '{col}',")
            else:
                print(f"    '{col}'")
        print("]")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_table_columns()
