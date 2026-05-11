#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple de login con estructura correcta
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_connection
from utils_homologacion import homologar_cedula
import hashlib

def test_login_simple():
    """Test simple de login"""
    print("=== TEST LOGIN SIMPLE ===")
    print()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Verificar estructura
        print("--- 1. Verificando usuarios ---")
        cursor.execute("SELECT cedula_usuario, login_usuario, rol, contrasena FROM usuarios WHERE cedula_usuario = %s", ("V-14300385",))
        usuario = cursor.fetchone()
        
        if usuario:
            print("Usuario encontrado:")
            print("  Cedula: {}".format(usuario[0]))
            print("  Login: {}".format(usuario[1]))
            print("  Rol: {}".format(usuario[2]))
            print("  Contrasena: {}".format(usuario[3][:20] + "..."))
        else:
            print("Usuario NO encontrado")
        print()
        
        # 2. Probar hash
        print("--- 2. Probando hash ---")
        password_test = "123456"
        hash_test = hashlib.sha256(password_test.encode('utf-8')).hexdigest()
        print("Hash generado: {}".format(hash_test))
        
        if usuario:
            hash_bd = usuario[3]
            print("Hash BD: {}".format(hash_bd))
            print("Coinciden: {}".format(hash_bd == hash_test))
        print()
        
        # 3. Probar login directo
        print("--- 3. Probando login directo ---")
        query = """
        SELECT cedula_usuario, login_usuario, rol, activo, contrasena
        FROM usuarios 
        WHERE (login_usuario = %s OR cedula_usuario = %s) AND activo = TRUE
        LIMIT 1
        """
        
        test_cedula = "V-14300385"
        cursor.execute(query, (test_cedula, test_cedula))
        resultado = cursor.fetchone()
        
        if resultado:
            print("Login directo exitoso:")
            print("  Cedula: {}".format(resultado[0]))
            print("  Login: {}".format(resultado[1]))
            print("  Rol: {}".format(resultado[2]))
            print("  Activo: {}".format(resultado[3]))
            
            # Validar contraseña
            if resultado[4] == hash_test:
                print("  Contraseña: CORRECTA")
            else:
                print("  Contraseña: INCORRECTA")
        else:
            print("Login directo fallido")
        
        print()
        
        # 4. Probar con homologación
        print("--- 4. Probando con homologación ---")
        
        test_formats = ["V-14300385", "14300385", "v-14300385"]
        
        for fmt in test_formats:
            print("Probando formato: '{}'".format(fmt))
            
            # Homologar
            homologada = homologar_cedula(fmt)
            print("  Homologada: '{}'".format(homologada))
            
            # Buscar
            cursor.execute(query, (fmt, homologada))
            res = cursor.fetchone()
            
            if res:
                print("  OK: Encontrado - {}".format(res[1]))
                if res[4] == hash_test:
                    print("  OK: Contraseña correcta")
                else:
                    print("  ERROR: Contraseña incorrecta")
            else:
                print("  ERROR: No encontrado")
            print()
        
    except Exception as e:
        print("ERROR: {}".format(e))
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_login_simple()
