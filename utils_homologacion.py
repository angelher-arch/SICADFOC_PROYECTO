#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidades para homologación y normalización de cédulas
Evita errores de login/autenticación por diferentes formatos de cédula
"""

import re

def homologar_cedula(cedula_input):
    """
    Homologa cualquier formato de cédula al formato estándar V-XXXXX
    
    Args:
        cedula_input (str): Cédula en cualquier formato (14300385, V-14300385, v-14300385, etc.)
        
    Returns:
        str: Cédula normalizada al formato V-XXXXX
    """
    if not cedula_input:
        return ""
    
    # Convertir a string y limpiar espacios
    cedula = str(cedula_input).strip()
    
    # Si ya está en formato V-XXXXX, retornar directamente
    if re.match(r'^V-\d+$', cedula.upper()):
        return cedula.upper()
    
    # Extraer solo los dígitos
    solo_digitos = re.sub(r'[^\d]', '', cedula)
    
    # Si no hay dígitos, retornar vacío
    if not solo_digitos:
        return ""
    
    # Formatear como V-XXXXX
    return f"V-{solo_digitos}"

def normalizar_cedula_para_bd(cedula_input):
    """
    Normaliza cédula para almacenamiento/consulta en base de datos
    
    Args:
        cedula_input (str): Cédula en cualquier formato
        
    Returns:
        str: Cédula normalizada para BD (V-XXXXX)
    """
    return homologar_cedula(cedula_input)

def normalizar_cedula_para_display(cedula_bd):
    """
    Normaliza cédula para mostrar en interfaz (puede usar diferentes formatos)
    
    Args:
        cedula_bd (str): Cédula de la base de datos (V-XXXXX)
        
    Returns:
        str: Cédula formateada para display
    """
    if not cedula_bd:
        return ""
    
    # Por ahora, mantenemos el formato V-XXXXX para consistencia
    return cedula_bd.upper()

def crear_condicion_cedula_sql(columna_cedula, cedula_input):
    """
    Crea condición SQL para buscar cédula independientemente del formato
    
    Args:
        columna_cedula (str): Nombre de la columna en la BD
        cedula_input (str): Cédula en cualquier formato
        
    Returns:
        tuple: (condicion_sql, parametros)
    """
    cedula_normalizada = homologar_cedula(cedula_input)
    
    # Condición que busca tanto el formato normalizado como posibles variantes
    condicion = f"""
        ({columna_cedula} = %s 
         OR {columna_cedula} = %s 
         OR {columna_cedula} = %s)
    """
    
    # Buscar en múltiples formatos
    solo_digitos = re.sub(r'[^\d]', '', cedula_input)
    parametros = [
        cedula_normalizada,      # V-14300385
        solo_digitos,           # 14300385
        f"v-{solo_digitos}"    # v-14300385
    ]
    
    return condicion, parametros

def probar_homologacion():
    """Prueba la función de homologación con diferentes formatos"""
    print("=== PRUEBA DE HOMOLOGACIÓN DE CÉDULAS ===")
    print()
    
    test_cases = [
        "14300385",
        "V-14300385", 
        "v-14300385",
        "V-14300385 ",
        " 14300385",
        "V-12345678",
        "12345678",
        "V-5.430.424",
        "5430424",
        "",
        None,
        "texto sin numeros"
    ]
    
    for test_case in test_cases:
        resultado = homologar_cedula(test_case)
        print(f"Entrada: '{test_case}' -> Salida: '{resultado}'")
    
    print()
    print("=== PRUEBA DE CONDICIÓN SQL ===")
    print()
    
    cedula_test = "14300385"
    condicion, params = crear_condicion_cedula_sql("cedula_usuario", cedula_test)
    
    print(f"Cédula de entrada: {cedula_test}")
    print(f"Condición SQL: {condicion}")
    print(f"Parámetros: {params}")

if __name__ == "__main__":
    probar_homologacion()
