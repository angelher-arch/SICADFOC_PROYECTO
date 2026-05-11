#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arreglar el problema de doble conexión en database.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def arreglar_conexion():
    """Arreglar conexión para que use la misma base de datos"""
    print("=== ARREGLANDO CONEXIÓN DATABASE ===")
    print()
    
    # Leer el archivo database.py
    try:
        with open('database.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        print("Buscando función authenticate_user...")
        
        # Reemplazar la consulta SQL para usar la estructura correcta
        query_vieja = """        query = """
        SELECT u.cedula_usuario, u.login_usuario, u.rol, u.activo, u.contrasena,
               p.nombre, p.apellido, p.telefono, p.direccion
        FROM usuarios u
        LEFT JOIN persona p ON u.cedula_usuario = p.cedula
        WHERE (u.login_usuario = %s OR u.cedula_usuario = %s OR u.cedula_usuario = %s OR u.cedula_usuario = %s) AND u.activo = TRUE
        LIMIT 1
        """"
        
        query_nueva = """        query = """
        SELECT u.cedula_usuario, u.login_usuario, u.rol, u.activo, u.contrasena,
               p.nombre, p.apellido, p.telefono, p.direccion
        FROM usuarios u
        LEFT JOIN persona p ON u.cedula_usuario = p.cedula
        WHERE (u.login_usuario = %s OR u.cedula_usuario = %s OR u.cedula_usuario = %s OR u.cedula_usuario = %s) AND u.activo = TRUE
        LIMIT 1
        """"
        
        # Buscar y reemplazar authenticate_user para usar get_connection directamente
        auth_viejo = """def authenticate_user(username, password):
    """Autenticar usuario usando canal único y consulta parametrizada unificada con homologación de cédulas."""
    try:
        import hashlib

        # Validación de entrada con tratamiento uniforme de tipos
        cleaned_username = str(username or "").strip()
        password_str = str(password or "")
        
        if not cleaned_username or not password_str:
            return {'success': False, 'message': 'Usuario o contraseña incorrectos'}

        # Homologar cédula para normalizar formato
        cedula_homologada = homologar_cedula(cleaned_username)
        
        # Generar hash SHA256 (librería consistente)
        hashed_password = hashlib.sha256(password_str.encode('utf-8')).hexdigest()

        # Consulta SQL corregida - usar nombres reales de columnas
        query = """
        SELECT u.cedula_usuario, u.login_usuario, u.rol, u.activo, u.contrasena,
               p.nombre, p.apellido, p.telefono, p.direccion
        FROM usuarios u
        LEFT JOIN persona p ON u.cedula_usuario = p.cedula
        WHERE (u.login_usuario = %s OR u.cedula_usuario = %s OR u.cedula_usuario = %s OR u.cedula_usuario = %s) AND u.activo = TRUE
        LIMIT 1
        """
        
        # Usar el canal único global - buscar por login_usuario y múltiples formatos de cédula
        user_row = execute_query(
            query,
            (cleaned_username, cedula_homologada, cleaned_username.replace('V-', '').replace('E-', ''), f"v-{cleaned_username.replace('V-', '').replace('E-', '')}"),
            fetch_one=True
        )"""
        
        auth_nuevo = """def authenticate_user(username, password):
    """Autenticar usuario usando get_connection directo con homologación de cédulas."""
    try:
        import hashlib

        # Validación de entrada con tratamiento uniforme de tipos
        cleaned_username = str(username or "").strip()
        password_str = str(password or "")
        
        if not cleaned_username or not password_str:
            return {'success': False, 'message': 'Usuario o contraseña incorrectos'}

        # Homologar cédula para normalizar formato
        cedula_homologada = homologar_cedula(cleaned_username)
        
        # Generar hash SHA256 (librería consistente)
        hashed_password = hashlib.sha256(password_str.encode('utf-8')).hexdigest()

        # Usar get_connection directo para evitar problemas de doble conexión
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Consulta SQL - usar nombres reales de columnas
            query = """
            SELECT u.cedula_usuario, u.login_usuario, u.rol, u.activo, u.contrasena,
                   p.nombre, p.apellido, p.telefono, p.direccion
            FROM usuarios u
            LEFT JOIN persona p ON u.cedula_usuario = p.cedula
            WHERE (u.login_usuario = %s OR u.cedula_usuario = %s OR u.cedula_usuario = %s OR u.cedula_usuario = %s) AND u.activo = TRUE
            LIMIT 1
            """
            
            # Ejecutar consulta con múltiples formatos de cédula
            cursor.execute(
                query,
                (cleaned_username, cedula_homologada, cleaned_username.replace('V-', '').replace('E-', ''), f"v-{cleaned_username.replace('V-', '').replace('E-', '')}")
            )
            user_row = cursor.fetchone()"""
        
        if auth_viejo in contenido:
            print("Reemplazando authenticate_user...")
            contenido = contenido.replace(auth_viejo, auth_nuevo)
        else:
            print("No se encontró el authenticate_user esperado")
            
            # Buscar el inicio de la función
            inicio = contenido.find("def authenticate_user(username, password):")
            if inicio != -1:
                print("Encontrado authenticate_user, reemplazando manualmente...")
                # Encontrar el fin de la función
                fin = contenido.find("\n\ndef ", inicio + 1)
                if fin == -1:
                    fin = len(contenido)
                
                # Extraer la función vieja
                funcion_vieja = contenido[inicio:fin]
                print("Función vieja encontrada:")
                print(funcion_vieja[:200] + "...")
                
                # Reemplazar con la nueva
                contenido = contenido[:inicio] + auth_nuevo + contenido[fin:]
        
        # Escribir el archivo modificado
        with open('database.py', 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print("✅ database.py actualizado correctamente")
        
    except Exception as e:
        print("❌ Error arreglando database.py: {}".format(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    arreglar_conexion()
