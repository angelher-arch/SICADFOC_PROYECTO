#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para migración directa de cédulas usando conexión PostgreSQL directa
"""

import psycopg2
import os
from psycopg2.extras import RealDictCursor

def get_direct_connection():
    """Obtener conexión directa a PostgreSQL"""
    try:
        # Conexión a producción
        conn = psycopg2.connect(
            host="dpg-d7gfpi28qa3s73ci36d0-a.oregon-postgres.render.com",
            port="5432",
            database="foc26db",
            user="foc26db_user",
            password="UPf1aEp5tBk2i3RZlY2GkXqLwRvF3J6d",
            sslmode="require"
        )
        return conn
    except Exception as e:
        print("ERROR conectando: {}".format(e))
        return None

def migracion_directa():
    """Ejecutar migración directa"""
    print("=== MIGRACIÓN DIRECTA DE CÉDULAS ===")
    print()
    
    conn = get_direct_connection()
    if not conn:
        print("No se pudo conectar a la base de datos")
        return
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Verificar usuarios actuales
        print("--- 1. Usuarios actuales ---")
        cursor.execute("SELECT cedula_usuario, login_usuario, rol FROM usuarios ORDER BY cedula_usuario")
        usuarios = cursor.fetchall()
        
        for usuario in usuarios:
            print("  {} - {} - {}".format(usuario['cedula_usuario'], usuario['login_usuario'], usuario['rol']))
        print()
        
        # 2. Actualizar cédulas sin prefijo V-
        print("--- 2. Actualizando cédulas sin prefijo ---")
        cursor.execute("UPDATE usuarios SET cedula_usuario = 'V-' || cedula_usuario WHERE cedula_usuario NOT LIKE 'V-%' AND cedula_usuario NOT LIKE 'E-%'")
        conn.commit()
        
        print("Cédulas actualizadas: {}".format(cursor.rowcount))
        print()
        
        # 3. Verificar resultado
        print("--- 3. Usuarios después de migración ---")
        cursor.execute("SELECT cedula_usuario, login_usuario, rol FROM usuarios ORDER BY cedula_usuario")
        usuarios_actualizados = cursor.fetchall()
        
        for usuario in usuarios_actualizados:
            print("  {} - {} - {}".format(usuario['cedula_usuario'], usuario['login_usuario'], usuario['rol']))
        
        print()
        print("MIGRACIÓN COMPLETADA EXITOSAMENTE")
        
        cursor.close()
        
    except Exception as e:
        print("ERROR en migración: {}".format(e))
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migracion_directa()
