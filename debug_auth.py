#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debug del proceso de autenticación
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import execute_query
from utils_homologacion import homologar_cedula

def debug_auth_process():
    """Debug del proceso de autenticación"""
    print("=== DEBUG AUTENTICACIÓN ===")
    print()
    
    # 1. Verificar que el usuario existe en la BD
    print("--- 1. Verificar usuario en BD ---")
    query_check = "SELECT cedula_usuario, login_usuario, rol, activo FROM usuarios WHERE cedula_usuario = %s"
    
    # Probar diferentes formatos
    formats_to_test = ["V-14300385", "14300385", "v-14300385"]
    
    for fmt in formats_to_test:
        print("Probando formato: '{}'".format(fmt))
        result = execute_query(query_check, (fmt,), fetch_one=True)
        print("Resultado: {}".format(result))
        print()
    
    # 2. Verificar contraseña hash
    print("--- 2. Verificar hash de contraseña ---")
    query_hash = "SELECT cedula_usuario, login_usuario, password_hash FROM usuarios WHERE cedula_usuario = %s"
    
    result = execute_query(query_hash, ("V-14300385",), fetch_one=True)
    if result:
        print("Usuario encontrado:")
        print("  Cedula: {}".format(result['cedula_usuario']))
        print("  Login: {}".format(result['login_usuario']))
        print("  Hash: {}".format(result['password_hash']))
        
        # Probar hash con contraseña "123456"
        import hashlib
        test_hash = hashlib.sha256("123456".encode('utf-8')).hexdigest()
        print("  Hash test (123456): {}".format(test_hash))
        print("  Hash coincide: {}".format(result['password_hash'] == test_hash))
    else:
        print("Usuario no encontrado")
    
    print()
    
    # 3. Probar consulta completa de authenticate_user
    print("--- 3. Probar consulta completa ---")
    query_full = """
    SELECT u.cedula_usuario, u.login_usuario, u.rol, u.activo, u.password_hash,
           p.nombre, p.apellido, p.telefono, p.direccion
    FROM usuarios u
    LEFT JOIN persona p ON u.cedula_usuario = p.cedula
    WHERE (u.username = %s OR u.cedula_usuario = %s OR u.cedula_usuario = %s OR u.cedula_usuario = %s) AND u.activo = TRUE
    LIMIT 1
    """
    
    test_cedula = "14300385"
    cedula_homologada = homologar_cedula(test_cedula)
    params = (
        test_cedula, 
        cedula_homologada, 
        test_cedula.replace('V-', '').replace('E-', ''), 
        "v-{}".format(test_cedula.replace('V-', '').replace('E-', ''))
    )
    
    print("Cédula original: '{}'".format(test_cedula))
    print("Cédula homologada: '{}'".format(cedula_homologada))
    print("Parámetros: {}".format(params))
    
    result = execute_query(query_full, params, fetch_one=True)
    print("Resultado: {}".format(result))
    
    print()
    
    # 4. Verificar estructura exacta de la tabla
    print("--- 4. Estructura tabla usuarios ---")
    query_struct = """
    SELECT column_name, data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_name = 'usuarios' 
    AND table_schema = 'public'
    ORDER BY ordinal_position
    """
    
    columns = execute_query(query_struct)
    print("Columnas de usuarios:")
    for col in columns:
        print("  {}: {} (nullable: {})".format(col['column_name'], col['data_type'], col['is_nullable']))

if __name__ == "__main__":
    debug_auth_process()
