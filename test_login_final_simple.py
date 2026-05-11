#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test final simple de login con estructura correcta
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_connection
from utils_homologacion import homologar_cedula
import hashlib

def test_login_final_simple():
    """Test final simple de login"""
    print("=== TEST LOGIN FINAL SIMPLE ===")
    print()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Probar login simple directo
        print("--- 1. Login directo ---")
        query = """
        SELECT cedula_usuario, login_usuario, rol, activo, contrasena
        FROM usuarios 
        WHERE (login_usuario = %s OR cedula_usuario = %s) AND activo = TRUE
        LIMIT 1
        """
        
        test_formats = ["V-14300385", "14300385", "v-14300385"]
        password_test = "123456"
        hash_test = hashlib.sha256(password_test.encode('utf-8')).hexdigest()
        
        print("Hash de prueba para '123456': {}".format(hash_test))
        print()
        
        for fmt in test_formats:
            print("Probando formato: '{}'".format(fmt))
            
            # Buscar usuario
            cursor.execute(query, (fmt, fmt))
            resultado = cursor.fetchone()
            
            if resultado:
                print("  Usuario encontrado: {} - {}".format(resultado[0], resultado[1]))
                
                # Validar contraseña
                if resultado[4] == hash_test:
                    print("  OK: Contraseña CORRECTA")
                    print("  OK: Login EXITOSO")
                else:
                    print("  ERROR: Contraseña incorrecta")
                    print("  Hash BD: {}".format(resultado[4][:20] + "..."))
                    print("  Hash test: {}".format(hash_test))
            else:
                print("  ERROR: Usuario no encontrado")
            print()
        
        # 2. Probar authenticate_user corregido
        print("--- 2. Probar authenticate_user corregido ---")
        
        # Importar authenticate_user corregido
        from database import authenticate_user
        
        for fmt in test_formats:
            print("Probando authenticate_user con: '{}'".format(fmt))
            
            resultado = authenticate_user(fmt, password_test)
            
            if resultado and resultado.get('success', False):
                user = resultado.get('user', {})
                print("  OK: Login exitoso")
                print("  Usuario: {} - {} - {}".format(user.get('cedula_usuario'), user.get('login_usuario'), user.get('rol')))
            else:
                print("  ERROR: Login fallido")
                print("  Mensaje: {}".format(resultado.get('message', 'Error desconocido')))
            print()
        
    except Exception as e:
        print("ERROR: {}".format(e))
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_login_final_simple()
