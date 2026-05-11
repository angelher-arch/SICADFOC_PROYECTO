#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar login después de homologación de cédulas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import authenticate_user
from utils_homologacion import homologar_cedula

def test_login_homologado():
    """Probar login con diferentes formatos después de migración"""
    print("=== TEST LOGIN DESPUÉS DE HOMOLOGACIÓN ===")
    print()
    
    # Casos de prueba
    test_cases = [
        ("V-14300385", "123456"),  # Formato estándar (Angel Hernandez)
        ("14300385", "123456"),   # Sin prefijo (debe funcionar con homologación)
        ("v-14300385", "123456"), # Minúscula (debe funcionar con homologación)
        ("V-12345678", "123456"), # Otro usuario
        ("12345678", "123456"),   # Otro usuario sin prefijo
        ("V-99999999", "123456"), # Usuario no existe
    ]
    
    for cedula, password in test_cases:
        print("--- Probando login con cedula: '{}' ---".format(cedula))
        
        # Mostrar homologación
        cedula_homologada = homologar_cedula(cedula)
        print("Cedula original: '{}' -> Homologada: '{}'".format(cedula, cedula_homologada))
        
        # Intentar autenticación
        resultado = authenticate_user(cedula, password)
        
        if resultado and resultado.get('success', False):
            user = resultado.get('user', {})
            print("OK: Login exitoso:")
            print("   Cedula: {}".format(user.get('cedula_usuario')))
            print("   Nombre: {}".format(user.get('login_usuario')))
            print("   Rol: {}".format(user.get('rol')))
        else:
            print("ERROR: Login fallido: {}".format(resultado.get('message', 'Error desconocido')))
        
        print()
    
    # Probar específicamente a Angel Hernandez
    print("=== CASO ESPECÍFICO: ANGEL HERNANDEZ ===")
    print()
    
    angel_cases = [
        "V-14300385",
        "14300385", 
        "v-14300385"
    ]
    
    for cedula in angel_cases:
        print("Probando Angel con cedula: '{}'".format(cedula))
        resultado = authenticate_user(cedula, "123456")
        
        if resultado and resultado.get('success', False):
            user = resultado.get('user', {})
            print("OK: Angel encontrado: {} - {}".format(user.get('login_usuario'), user.get('rol')))
        else:
            print("ERROR: No encontrado: {}".format(resultado.get('message')))
        print()

if __name__ == "__main__":
    test_login_homologado()
