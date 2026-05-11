#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para probar homologación de cédulas en login
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import authenticate_user
from utils_homologacion import homologar_cedula

def probar_homologacion_simple():
    """Probar login con diferentes formatos de cédula"""
    print("=== PRUEBA DE HOMOLOGACIÓN EN LOGIN ===")
    print()
    
    # Casos de prueba con diferentes formatos de cédula
    test_cases = [
        ("V-14300385", "123456"),  # Formato estándar
        ("14300385", "123456"),   # Sin prefijo
        ("v-14300385", "123456"), # Minúscula
        ("V-12345678", "123456"), # Otro usuario
        ("12345678", "123456"),   # Otro usuario sin prefijo
        ("V-99999999", "123456"), # Usuario no existe
        ("99999999", "123456"),   # Usuario no existe sin prefijo
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
    
    # Probar caso específico del usuario Angel Hernandez
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
    probar_homologacion_simple()
