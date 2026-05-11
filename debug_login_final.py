#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug final del problema de login
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_connection
from utils_homologacion import homologar_cedula
import hashlib

def debug_login_final():
    """Debug final del login"""
    print("=== DEBUG FINAL LOGIN ===")
    print()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Verificar usuarios existentes
        print("--- 1. Usuarios existentes ---")
        cursor.execute("SELECT cedula_usuario, login_usuario, rol, password_hash FROM usuarios ORDER BY cedula_usuario")
        usuarios = cursor.fetchall()
        
        for usuario in usuarios:
            print("  {} - {} - {} - {}".format(usuario[0], usuario[1], usuario[2], usuario[3][:20] + "..."))
        print()
        
        # 2. Probar consulta exacta de authenticate_user
        print("--- 2. Probar consulta authenticate_user ---")
        test_cedula = "V-14300385"
        test_password = "123456"
        
        # Generar hash
        hashed_password = hashlib.sha256(test_password.encode('utf-8')).hexdigest()
        print("Hash generado para '123456': {}".format(hashed_password))
        print()
        
        # Consulta exacta
        query = """
        SELECT u.cedula_usuario, u.login_usuario, u.rol, u.activo, u.password_hash,
               p.nombre, p.apellido, p.telefono, p.direccion
        FROM usuarios u
        LEFT JOIN persona p ON u.cedula_usuario = p.cedula
        WHERE (u.username = %s OR u.cedula_usuario = %s OR u.cedula_usuario = %s OR u.cedula_usuario = %s) AND u.activo = TRUE
        LIMIT 1
        """
        
        cedula_homologada = homologar_cedula(test_cedula)
        params = (
            test_cedula, 
            cedula_homologada, 
            test_cedula.replace('V-', '').replace('E-', ''), 
            "v-{}".format(test_cedula.replace('V-', '').replace('E-', ''))
        )
        
        print("Cédula test: {}".format(test_cedula))
        print("Cédula homologada: {}".format(cedula_homologada))
        print("Parámetros: {}".format(params))
        print()
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        
        if result:
            print("Usuario encontrado:")
            print("  Cédula: {}".format(result[0]))
            print("  Login: {}".format(result[1]))
            print("  Rol: {}".format(result[2]))
            print("  Activo: {}".format(result[3]))
            print("  Hash BD: {}".format(result[4]))
            print("  Hash test: {}".format(hashed_password))
            print("  Hash coincide: {}".format(result[4] == hashed_password))
        else:
            print("USUARIO NO ENCONTRADO")
        
        print()
        
        # 3. Probar búsqueda simple
        print("--- 3. Búsqueda simple por cédula ---")
        cursor.execute("SELECT * FROM usuarios WHERE cedula_usuario = %s", (test_cedula,))
        simple_result = cursor.fetchone()
        
        if simple_result:
            print("Búsqueda simple encontró:")
            print("  Registro completo: {}".format(simple_result))
        else:
            print("Búsqueda simple NO encontró usuario")
        
        print()
        
        # 4. Verificar si hay problema con la consulta compleja
        print("--- 4. Probar consulta simplificada ---")
        simple_query = """
        SELECT cedula_usuario, login_usuario, rol, activo, password_hash
        FROM usuarios 
        WHERE cedula_usuario = %s AND activo = TRUE
        """
        
        cursor.execute(simple_query, (test_cedula,))
        simple_auth = cursor.fetchone()
        
        if simple_auth:
            print("Consulta simplificada encontró:")
            print("  Cédula: {}".format(simple_auth[0]))
            print("  Login: {}".format(simple_auth[1]))
            print("  Rol: {}".format(simple_auth[2]))
            print("  Activo: {}".format(simple_auth[3]))
            print("  Hash: {}".format(simple_auth[4]))
            print("  Hash coincide: {}".format(simple_auth[4] == hashed_password))
        else:
            print("Consulta simplificada NO encontró usuario")
        
    except Exception as e:
        print("ERROR: {}".format(e))
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    debug_login_final()
