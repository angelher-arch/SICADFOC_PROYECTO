#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para encontrar la contraseña correcta de Angel Hernandez
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_connection
import hashlib

def test_password_correcta():
    """Test para encontrar contraseña correcta"""
    print("=== TEST CONTRASEÑA CORRECTA ===")
    print()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Obtener hash de Angel
        cursor.execute("SELECT cedula_usuario, login_usuario, contrasena FROM usuarios WHERE cedula_usuario = %s", ("V-14300385",))
        angel = cursor.fetchone()
        
        if angel:
            print("Datos de Angel Hernandez:")
            print("  Cedula: {}".format(angel[0]))
            print("  Login: {}".format(angel[1]))
            print("  Hash BD: {}".format(angel[2]))
            print()
            
            hash_bd = angel[2]
            
            # 2. Probar contraseñas comunes
            passwords_comunes = [
                "123456",
                "password",
                "admin",
                "123456789",
                "qwerty",
                "angel",
                "hernandez",
                "angelhernandez",
                "Angel",
                "Hernandez",
                "AngelHernandez",
                "admin123",
                "1234",
                "12345",
                "1234567",
                "12345678",
                "1234567890",
                "password123",
                "root",
                "user",
                "test",
                "demo"
            ]
            
            print("--- Probando contraseñas comunes ---")
            for pwd in passwords_comunes:
                hash_test = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
                if hash_test == hash_bd:
                    print("✅ CONTRASEÑA ENCONTRADA: '{}'".format(pwd))
                    return pwd
                else:
                    print("X '{}' - No coincide".format(pwd))
            
            print()
            print("❌ No se encontró contraseña común")
            
            # 3. Probar hash inverso (si es MD5 o SHA1)
            print()
            print("--- Verificando si es otro algoritmo ---")
            
            # Probar MD5
            import hashlib as hl
            for pwd in ["123456", "admin", "password"]:
                md5_hash = hl.md5(pwd.encode('utf-8')).hexdigest()
                sha1_hash = hl.sha1(pwd.encode('utf-8')).hexdigest()
                
                if md5_hash == hash_bd:
                    print("✅ Es MD5: '{}'".format(pwd))
                    return pwd
                if sha1_hash == hash_bd:
                    print("✅ Es SHA1: '{}'".format(pwd))
                    return pwd
            
            print("No es MD5 ni SHA1 con contraseñas comunes")
            
        else:
            print("❌ Angel Hernandez no encontrado")
        
    except Exception as e:
        print("ERROR: {}".format(e))
    finally:
        cursor.close()
        conn.close()
    
    return None

if __name__ == "__main__":
    password = test_password_correcta()
    if password:
        print()
        print("=== CONTRASEÑA CORRECTA: {} ===".format(password))
    else:
        print()
        print("=== NO SE PUDO DETERMINAR LA CONTRASEÑA ===")
