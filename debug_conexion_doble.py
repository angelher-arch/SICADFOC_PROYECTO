#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug para entender por qué hay dos conexiones diferentes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_conexion_doble():
    """Debug para entender el problema de doble conexión"""
    print("=== DEBUG CONEXIÓN DOBLE ===")
    print()
    
    # 1. Probar get_connection directo
    print("--- 1. get_connection() directo ---")
    try:
        from database import get_connection
        conn1 = get_connection()
        cursor1 = conn1.cursor()
        
        cursor1.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'usuarios' AND table_schema = 'public'")
        cols1 = cursor1.fetchall()
        
        print("Columnas encontradas con get_connection():")
        for col in cols1:
            print("  {}".format(col[0]))
        
        cursor1.close()
        conn1.close()
        
    except Exception as e:
        print("ERROR con get_connection(): {}".format(e))
    
    print()
    
    # 2. Probar execute_query
    print("--- 2. execute_query() ---")
    try:
        from database import execute_query
        
        query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'usuarios' AND table_schema = 'public'
        """
        
        cols2 = execute_query(query)
        
        print("Columnas encontradas con execute_query():")
        if cols2:
            for col in cols2:
                if isinstance(col, dict):
                    print("  {}".format(col.get('column_name', 'N/A')))
                else:
                    print("  {}".format(col[0] if col else 'N/A'))
        else:
            print("  No se encontraron columnas")
        
    except Exception as e:
        print("ERROR con execute_query(): {}".format(e))
    
    print()
    
    # 3. Verificar DatabaseManager
    print("--- 3. DatabaseManager ---")
    try:
        from database import DatabaseManager, db_manager
        
        print("Tipo de db_manager: {}".format(type(db_manager)))
        
        if hasattr(db_manager, 'connection_config'):
            print("Config de conexión:")
            for key, value in db_manager.connection_config.items():
                if key == 'password':
                    print("  {}: {}".format(key, '*' * len(str(value))))
                else:
                    print("  {}: {}".format(key, value))
        
        # Probar conexión directa del manager
        conn3 = db_manager.get_connection()
        cursor3 = conn3.cursor()
        
        cursor3.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'usuarios' AND table_schema = 'public'")
        cols3 = cursor3.fetchall()
        
        print("Columnas encontradas con DatabaseManager:")
        for col in cols3:
            print("  {}".format(col[0]))
        
        cursor3.close()
        conn3.close()
        
    except Exception as e:
        print("ERROR con DatabaseManager: {}".format(e))

if __name__ == "__main__":
    debug_conexion_doble()
