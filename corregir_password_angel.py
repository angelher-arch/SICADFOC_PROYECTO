#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir la contraseña de Angel Hernandez
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_connection
import hashlib

def corregir_password_angel():
    """Corregir contraseña de Angel Hernandez a hash SHA256 correcto"""
    print("=== CORREGIR PASSWORD ANGEL HERNANDEZ ===")
    print()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Generar hash correcto para "123456"
        password_correcta = "123456"
        hash_correcto = hashlib.sha256(password_correcta.encode('utf-8')).hexdigest()
        
        print("Password correcta: {}".format(password_correcta))
        print("Hash SHA256 correcto: {}".format(hash_correcto))
        print()
        
        # 2. Verificar hash actual
        cursor.execute("SELECT cedula_usuario, login_usuario, contrasena FROM usuarios WHERE cedula_usuario = %s", ("V-14300385",))
        angel = cursor.fetchone()
        
        if angel:
            hash_actual = angel[2]
            print("Hash actual en BD: {}".format(hash_actual))
            print("¿Coinciden? {}".format(hash_actual == hash_correcto))
            print()
            
            # 3. Actualizar si no coinciden
            if hash_actual != hash_correcto:
                print("Actualizando contraseña...")
                cursor.execute("UPDATE usuarios SET contrasena = %s WHERE cedula_usuario = %s", (hash_correcto, "V-14300385"))
                conn.commit()
                print("Contraseña actualizada exitosamente")
                print()
                
                # 4. Verificar actualización
                cursor.execute("SELECT contrasena FROM usuarios WHERE cedula_usuario = %s", ("V-14300385",))
                nuevo_hash = cursor.fetchone()[0]
                print("Nuevo hash en BD: {}".format(nuevo_hash))
                print("¿Ahora coincide? {}".format(nuevo_hash == hash_correcto))
            else:
                print("La contraseña ya es correcta")
        else:
            print("ERROR: Angel Hernandez no encontrado")
        
        print()
        print("=== CONTRASEÑA CORREGIDA ===")
        
    except Exception as e:
        print("ERROR: {}".format(e))
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    corregir_password_angel()
