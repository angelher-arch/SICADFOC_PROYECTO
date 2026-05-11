#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test completo de login para verificar que todo funciona
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_login_completo():
    """Test completo del flujo de login"""
    print("=== TEST LOGIN COMPLETO ===")
    print()
    
    try:
        # 1. Probar verificar_usuario (main.py)
        print("--- 1. Probando verificar_usuario() ---")
        
        from main import verificar_usuario
        
        test_cases = [
            ("V-14300385", "123456"),  # Angel Hernandez - Administrador
            ("14300385", "123456"),   # Sin prefijo
            ("v-14300385", "123456"), # Minúscula
        ]
        
        for cedula, password in test_cases:
            print("Probando: '{}' + '{}'".format(cedula, password))
            
            resultado = verificar_usuario(cedula, password)
            
            if resultado:
                print("  OK: Login exitoso")
                print("  Rol: {}".format(resultado.get('rol')))
                print("  Login: {}".format(resultado.get('login')))
                print("  Cedula: {}".format(resultado.get('cedula')))
            else:
                print("  ERROR: Login fallido")
            print()
        
        # 2. Probar authenticate_user directamente
        print("--- 2. Probando authenticate_user() directamente ---")
        
        from database import authenticate_user
        
        for cedula, password in test_cases:
            print("Probando authenticate_user: '{}' + '{}'".format(cedula, password))
            
            resultado = authenticate_user(cedula, password)
            
            if resultado and resultado.get('success', False):
                user = resultado.get('user', {})
                print("  OK: Autenticación exitosa")
                print("  Rol: {}".format(user.get('rol')))
                print("  Login: {}".format(user.get('login_usuario')))
                print("  Cedula: {}".format(user.get('cedula_usuario')))
            else:
                print("  ERROR: Autenticación fallida")
                print("  Mensaje: {}".format(resultado.get('message', 'Error desconocido')))
            print()
        
        # 3. Verificar homologación
        print("--- 3. Probando homologación ---")
        
        from utils_homologacion import homologar_cedula
        
        test_formats = ["V-14300385", "14300385", "v-14300385", "V-12345678", "12345678"]
        
        for fmt in test_formats:
            homologada = homologar_cedula(fmt)
            print("  '{}' -> '{}'".format(fmt, homologada))
        
        print()
        print("=== TEST COMPLETADO ===")
        
    except Exception as e:
        print("ERROR EN TEST: {}".format(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login_completo()
