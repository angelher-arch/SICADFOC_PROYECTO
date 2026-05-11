#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para ejecutar migración de homologación de cédulas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import execute_query

def migracion_simple():
    """Ejecutar migración simple de cédulas"""
    print("=== MIGRACIÓN SIMPLE DE CÉDULAS ===")
    print()
    
    try:
        # 1. Verificar usuarios actuales
        print("--- 1. Usuarios actuales ---")
        query = "SELECT cedula_usuario, login_usuario, rol FROM usuarios ORDER BY cedula_usuario"
        usuarios = execute_query(query)
        
        for usuario in usuarios:
            print("  {} - {} - {}".format(usuario['cedula_usuario'], usuario['login_usuario'], usuario['rol']))
        print()
        
        # 2. Actualizar cédulas sin prefijo V-
        print("--- 2. Actualizando cédulas sin prefijo ---")
        update_query = "UPDATE usuarios SET cedula_usuario = 'V-' || cedula_usuario WHERE cedula_usuario NOT LIKE 'V-%' AND cedula_usuario NOT LIKE 'E-%'"
        
        try:
            resultado = execute_query(update_query)
            print("Cédulas actualizadas: {}".format(resultado))
        except Exception as e:
            print("Error actualizando: {}".format(e))
        
        print()
        
        # 3. Verificar resultado
        print("--- 3. Usuarios después de migración ---")
        usuarios_actualizados = execute_query(query)
        
        for usuario in usuarios_actualizados:
            print("  {} - {} - {}".format(usuario['cedula_usuario'], usuario['login_usuario'], usuario['rol']))
        
        print()
        print("MIGRACIÓN COMPLETADA")
        
    except Exception as e:
        print("ERROR: {}".format(e))

if __name__ == "__main__":
    migracion_simple()
