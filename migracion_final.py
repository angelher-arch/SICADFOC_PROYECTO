#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script final para migración de cédulas usando el database.py existente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_connection

def migracion_final():
    """Ejecutar migración final usando get_connection"""
    print("=== MIGRACIÓN FINAL DE CÉDULAS ===")
    print()
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. Verificar usuarios actuales
        print("--- 1. Usuarios actuales ---")
        cursor.execute("SELECT cedula_usuario, login_usuario, rol FROM usuarios ORDER BY cedula_usuario")
        usuarios = cursor.fetchall()
        
        for usuario in usuarios:
            print("  {} - {} - {}".format(usuario[0], usuario[1], usuario[2]))
        print()
        
        # 2. Actualizar cédulas sin prefijo V-
        print("--- 2. Actualizando cédulas sin prefijo ---")
        cursor.execute("UPDATE usuarios SET cedula_usuario = 'V-' || cedula_usuario WHERE cedula_usuario NOT LIKE 'V-%' AND cedula_usuario NOT LIKE 'E-%'")
        conn.commit()
        
        print("Cédulas actualizadas: {}".format(cursor.rowcount))
        print()
        
        # 3. Verificar resultado
        print("--- 3. Usuarios después de migración ---")
        cursor.execute("SELECT cedula_usuario, login_usuario, rol FROM usuarios ORDER BY cedula_usuario")
        usuarios_actualizados = cursor.fetchall()
        
        for usuario in usuarios_actualizados:
            print("  {} - {} - {}".format(usuario[0], usuario[1], usuario[2]))
        
        print()
        print("MIGRACIÓN COMPLETADA EXITOSAMENTE")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print("ERROR en migración: {}".format(e))
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    migracion_final()
