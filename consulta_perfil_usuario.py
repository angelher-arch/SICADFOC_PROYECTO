#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para consultar el perfil/rol de las cédulas específicas
Verificar qué rol tienen las cédulas: 14300385, V-14300385, v-14300385
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_connection

def consultar_perfil_usuario():
    """Consultar el perfil/rol de las cédulas específicas"""
    print("=== CONSULTA DE PERFIL/ROL DE USUARIOS ===")
    print("Cédulas a verificar: 14300385, V-14300385, v-14300385")
    print()
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Lista de cédulas a buscar
        cedulas_buscar = ['14300385', 'V-14300385', 'v-14300385']
        
        # Intentar diferentes consultas según la estructura de la tabla
        queries = [
            # Consulta 1: Estructura estándar
            """
            SELECT 
                cedula_usuario,
                nombre_usuario,
                apellido_usuario,
                rol,
                email,
                estado,
                fecha_creacion
            FROM usuarios 
            WHERE cedula_usuario IN %s
            ORDER BY cedula_usuario
            """,
            
            # Consulta 2: Nombres alternativos
            """
            SELECT 
                cedula,
                nombre,
                apellido,
                perfil,
                correo,
                estatus,
                fecha_registro
            FROM usuarios 
            WHERE cedula IN %s
            ORDER BY cedula
            """,
            
            # Consulta 3: Todas las columnas
            """
            SELECT *
            FROM usuarios 
            WHERE cedula_usuario IN %s OR cedula IN %s
            ORDER BY cedula_usuario, cedula
            """
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"--- Consulta {i} ---")
            try:
                if i == 3:
                    cursor.execute(query, (tuple(cedulas_buscar), tuple(cedulas_buscar)))
                else:
                    cursor.execute(query, (tuple(cedulas_buscar),))
                
                resultados = cursor.fetchall()
                
                if resultados:
                    # Obtener nombres de columnas
                    column_names = [desc[0] for desc in cursor.description]
                    print(f"Columnas: {', '.join(column_names)}")
                    print()
                    
                    for j, row in enumerate(resultados, 1):
                        print(f"Registro {j}:")
                        for k, (col_name, value) in enumerate(zip(column_names, row)):
                            print(f"  {col_name}: {value}")
                        print()
                else:
                    print("No se encontraron resultados con esta consulta.")
                    print()
                
                # Si encontramos resultados, no necesitamos más consultas
                if resultados:
                    break
                    
            except Exception as e:
                print(f"Error en consulta {i}: {e}")
                print()
        
        # Consultar estructura de la tabla usuarios
        print("--- ESTRUCTURA DE LA TABLA USUARIOS ---")
        try:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'usuarios' 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """)
            
            columnas = cursor.fetchall()
            print(f"Total de columnas: {len(columnas)}")
            print()
            
            for col in columnas:
                print(f"• {col[0]} - {col[1]} (Nullable: {col[2]}, Default: {col[3]})")
            print()
            
        except Exception as e:
            print(f"Error al consultar estructura: {e}")
            print()
        
        # Verificar si existen tablas de roles/perfiles
        print("--- TABLAS RELACIONADAS CON ROLES/PERFILES ---")
        try:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND (table_name LIKE '%rol%' OR table_name LIKE '%perfil%' OR table_name LIKE '%permiso%')
                ORDER BY table_name
            """)
            
            tablas = cursor.fetchall()
            if tablas:
                for tabla in tablas:
                    print(f"• {tabla[0]}")
            else:
                print("No se encontraron tablas relacionadas con roles/perfiles.")
            print()
            
        except Exception as e:
            print(f"Error al consultar tablas: {e}")
            print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error general: {e}")
        return False
    
    return True

if __name__ == "__main__":
    consultar_perfil_usuario()
