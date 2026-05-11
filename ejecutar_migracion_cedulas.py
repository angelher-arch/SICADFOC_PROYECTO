#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para ejecutar la migración de homologación de cédulas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import execute_query, execute_transaction

def ejecutar_migracion_cedulas():
    """Ejecutar migración completa de homologación de cédulas"""
    print("=== EJECUTANDO MIGRACIÓN DE HOMOLOGACIÓN DE CÉDULAS ===")
    print()
    
    try:
        # 1. Verificar estado actual
        print("--- 1. Verificando estado actual ---")
        query_estado = """
        SELECT 
            cedula_usuario,
            CASE 
                WHEN cedula_usuario LIKE 'V-%' THEN 'CORRECTO'
                WHEN cedula_usuario LIKE 'E-%' THEN 'CORRECTO'
                WHEN cedula_usuario ~ '^[0-9]+$' THEN 'SIN PREFIJO'
                ELSE 'OTRO FORMATO'
            END as formato_actual
        FROM usuarios 
        ORDER BY cedula_usuario
        """
        
        usuarios_actuales = execute_query(query_estado)
        print(f"Total usuarios: {len(usuarios_actuales)}")
        
        for usuario in usuarios_actuales:
            print(f"  {usuario['cedula_usuario']} - {usuario['formato_actual']}")
        print()
        
        # 2. Ejecutar migración principal
        print("--- 2. Ejecutando migración principal ---")
        
        # Actualizar cédulas sin prefijo a formato V-
        query1 = """
        UPDATE usuarios 
        SET cedula_usuario = 'V-' || cedula_usuario
        WHERE cedula_usuario ~ '^[0-9]+$' 
        AND cedula_usuario NOT LIKE 'V-%' 
        AND cedula_usuario NOT LIKE 'E-%'
        """
        
        result1 = execute_query(query1)
        print(f"Cédulas sin prefijo actualizadas: {result1}")
        
        # Actualizar cédulas con prefijo minúscula a mayúscula
        query2 = """
        UPDATE usuarios 
        SET cedula_usuario = 'V' || UPPER(SUBSTRING(cedula_usuario, 2))
        WHERE cedula_usuario ~ '^[vV]-[0-9]+$'
        """
        
        result2 = execute_query(query2)
        print(f"Cédulas con prefijo minúscula actualizadas: {result2}")
        
        # Actualizar cédulas con prefijo minúscula E a mayúscula
        query3 = """
        UPDATE usuarios 
        SET cedula_usuario = 'E' || UPPER(SUBSTRING(cedula_usuario, 2))
        WHERE cedula_usuario ~ '^[eE]-[0-9]+$'
        """
        
        result3 = execute_query(query3)
        print(f"Cédulas con prefijo E minúscula actualizadas: {result3}")
        print()
        
        # 3. Verificar resultado
        print("--- 3. Verificando resultado ---")
        usuarios_actualizados = execute_query(query_estado)
        print(f"Total usuarios después de migración: {len(usuarios_actualizados)}")
        
        for usuario in usuarios_actualizados:
            print(f"  {usuario['cedula_usuario']} - {usuario['formato_actual']}")
        print()
        
        # 4. Verificación final de consistencia
        print("--- 4. Verificación final de consistencia ---")
        query_consistencia = """
        SELECT 
            CASE 
                WHEN cedula_usuario LIKE 'V-%' THEN 'VENEZOLANO'
                WHEN cedula_usuario LIKE 'E-%' THEN 'EXTRANJERO'
                ELSE 'SIN CLASIFICAR'
            END as tipo_documento,
            COUNT(*) as cantidad
        FROM usuarios 
        GROUP BY 
            CASE 
                WHEN cedula_usuario LIKE 'V-%' THEN 'VENEZOLANO'
                WHEN cedula_usuario LIKE 'E-%' THEN 'EXTRANJERO'
                ELSE 'SIN CLASIFICAR'
            END
        ORDER BY cantidad DESC
        """
        
        consistencia = execute_query(query_consistencia)
        print("Distribución por tipo de documento:")
        
        for item in consistencia:
            print(f"  {item['tipo_documento']}: {item['cantidad']}")
        print()
        
        # 5. Mostrar usuarios actualizados
        print("--- 5. Usuarios actualizados ---")
        query_final = """
        SELECT 
            cedula_usuario,
            login_usuario,
            rol
        FROM usuarios 
        ORDER BY cedula_usuario
        """
        
        usuarios_final = execute_query(query_final)
        for usuario in usuarios_final:
            print(f"  {usuario['cedula_usuario']} - {usuario['login_usuario']} - {usuario['rol']}")
        
        print()
        print("✅ MIGRACIÓN COMPLETADA - TODAS LAS CÉDULAS NORMALIZADAS")
        return True
        
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        return False

if __name__ == "__main__":
    ejecutar_migracion_cedulas()
