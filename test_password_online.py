#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para verificar hash online de Angel Hernandez
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_connection
import hashlib

def test_password_online():
    """Test para verificar hash online"""
    print("=== TEST HASH ONLINE ===")
    print()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener hash de Angel
        cursor.execute("SELECT cedula_usuario, login_usuario, contrasena FROM usuarios WHERE cedula_usuario = %s", ("V-14300385",))
        angel = cursor.fetchone()
        
        if angel:
            hash_bd = angel[2]
            print("Hash BD de Angel Hernandez:")
            print(hash_bd)
            print()
            
            # El hash 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
            # corresponde a "123456" en SHA256 según verificación online
            
            print("Verificación online:")
            print("SHA256('123456') = 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9")
            print()
            
            # Verificar localmente
            hash_local = hashlib.sha256("123456".encode('utf-8')).hexdigest()
            print("Hash local SHA256('123456'):")
            print(hash_local)
            print()
            
            print("¿Coinciden?")
            print(hash_bd == hash_local)
            print()
            
            if hash_bd == hash_local:
                print("✅ LA CONTRASEÑA ES: 123456")
                
                # Probar login con contraseña correcta
                print()
                print("--- Probando login con contraseña correcta ---")
                
                query = """
                SELECT cedula_usuario, login_usuario, rol, activo, contrasena
                FROM usuarios 
                WHERE (login_usuario = %s OR cedula_usuario = %s) AND activo = TRUE
                LIMIT 1
                """
                
                test_formats = ["V-14300385", "14300385", "v-14300385"]
                
                for fmt in test_formats:
                    cursor.execute(query, (fmt, fmt))
                    resultado = cursor.fetchone()
                    
                    if resultado and resultado[4] == hash_local:
                        print("✅ Login EXITOSO con formato: '{}'".format(fmt))
                        print("   Usuario: {} - {}".format(resultado[0], resultado[1]))
                    else:
                        print("❌ Login fallido con formato: '{}'".format(fmt))
            else:
                print("❌ Los hashes no coinciden")
        
        else:
            print("❌ Angel Hernandez no encontrado")
        
    except Exception as e:
        print("ERROR: {}".format(e))
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_password_online()
