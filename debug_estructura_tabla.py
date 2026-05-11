#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug de estructura de tabla usuarios
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_connection

def debug_estructura_tabla():
    """Debug de estructura de tabla usuarios"""
    print("=== DEBUG ESTRUCTURA TABLA USUARIOS ===")
    print()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Verificar estructura exacta
        print("--- 1. Estructura exacta de tabla usuarios ---")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'usuarios' 
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        
        columnas = cursor.fetchall()
        
        print("Columnas encontradas:")
        for col in columnas:
            print("  {}: {} (nullable: {})".format(col[0], col[1], col[2]))
        print()
        
        # 2. Verificar usuarios existentes
        print("--- 2. Usuarios existentes ---")
        
        # Construir query dinámico con las columnas reales
        column_names = [col[0] for col in columnas]
        query_select = "SELECT " + ", ".join(column_names) + " FROM usuarios ORDER BY cedula_usuario"
        
        cursor.execute(query_select)
        usuarios = cursor.fetchall()
        
        for usuario in usuarios:
            print("  Usuario:")
            for i, valor in enumerate(usuario):
                print("    {}: {}".format(column_names[i], valor))
            print()
        
        # 3. Identificar columna de contraseña
        print("--- 3. Identificar columna de contraseña ---")
        
        password_column = None
        for col in columnas:
            col_lower = col[0].lower()
            if 'password' in col_lower or 'contra' in col_lower or 'pass' in col_lower:
                password_column = col[0]
                break
        
        if password_column:
            print("Columna de contraseña encontrada: {}".format(password_column))
            
            # Verificar hash de Angel Hernandez
            cursor.execute("SELECT {} FROM usuarios WHERE cedula_usuario = %s".format(password_column), ("V-14300385",))
            hash_result = cursor.fetchone()
            
            if hash_result:
                print("Hash de Angel Hernandez: {}".format(hash_result[0]))
            else:
                print("No se encontró hash de Angel Hernandez")
        else:
            print("NO se encontró columna de contraseña")
        
        print()
        
        # 4. Verificar si hay columna username
        print("--- 4. Verificar columna username ---")
        
        username_column = None
        for col in columnas:
            col_lower = col[0].lower()
            if 'user' in col_lower and 'name' in col_lower:
                username_column = col[0]
                break
        
        if username_column:
            print("Columna username encontrada: {}".format(username_column))
        else:
            print("NO se encontró columna username")
        
    except Exception as e:
        print("ERROR: {}".format(e))
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    debug_estructura_tabla()
