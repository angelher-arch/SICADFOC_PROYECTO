#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para consultar el perfil/rol de las cédulas específicas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_connection

def consultar_perfil_simple():
    """Consultar el perfil/rol de las cédulas específicas"""
    print("=== CONSULTA DE PERFIL/ROL DE USUARIOS ===")
    print("Cédulas a verificar: 14300385, V-14300385, v-14300385")
    print()
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Primero ver la estructura de la tabla
        print("--- ESTRUCTURA DE LA TABLA USUARIOS ---")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'usuarios' 
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        
        columnas = cursor.fetchall()
        print("Columnas encontradas:")
        for col in columnas:
            print(f"• {col[0]} - {col[1]}")
        print()
        
        # Construir consulta dinámica con las columnas existentes
        column_names = [col[0] for col in columnas]
        
        # Buscar columnas clave
        cedula_col = None
        rol_col = None
        nombre_col = None
        
        for col in column_names:
            col_lower = col.lower()
            if 'cedula' in col_lower:
                cedula_col = col
            elif 'rol' in col_lower or 'perfil' in col_lower:
                rol_col = col
            elif 'nombre' in col_lower and 'nombre' not in nombre_col:
                nombre_col = col
        
        print(f"Columna de cédula: {cedula_col}")
        print(f"Columna de rol/perfil: {rol_col}")
        print(f"Columna de nombre: {nombre_col}")
        print()
        
        # Consultar las cédulas específicas
        if cedula_col:
            query = f"SELECT * FROM usuarios WHERE {cedula_col} IN %s"
            cursor.execute(query, (tuple(['14300385', 'V-14300385', 'v-14300385']),))
            resultados = cursor.fetchall()
            
            if resultados:
                print(f"--- RESULTADOS ENCONTRADOS ({len(resultados)} registros) ---")
                for i, row in enumerate(resultados, 1):
                    print(f"Registro {i}:")
                    for j, value in enumerate(row):
                        print(f"  {column_names[j]}: {value}")
                    print()
            else:
                print("--- NO SE ENCONTRARON REGISTROS ---")
                print("Las cédulas 14300385, V-14300385, v-14300385 no existen en la base de datos.")
                print()
        
        # Verificar todas las cédulas que existen
        print("--- TODAS LAS CÉDULAS EXISTENTES ---")
        if cedula_col:
            cursor.execute(f"SELECT {cedula_col} FROM usuarios ORDER BY {cedula_col} LIMIT 10")
            todas_cedulas = cursor.fetchall()
            
            if todas_cedulas:
                print("Primeras 10 cédulas en la base de datos:")
                for cedula in todas_cedulas:
                    print(f"• {cedula[0]}")
                print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    consultar_perfil_simple()
