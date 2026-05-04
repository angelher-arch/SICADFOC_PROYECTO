#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
debug_estudiantes.py - Script de depuración para estudiantes
SICADFOC 2026 - Verificar datos existentes en base de datos
"""

import sys
import os
from database import execute_query, DatabaseManager

def main():
    """Función principal de depuración"""
    print("🔍 DEPURACIÓN DE ESTUDIANTES - SICADFOC 2026")
    print("=" * 50)
    
    try:
        # Verificar conexión
        db_manager = DatabaseManager()
        test_conn = db_manager.test_connection()
        print(f"📊 Estado conexión: {test_conn}")
        
        if not test_conn.get('status', False):
            print("❌ Error de conexión a base de datos")
            return
        
        print("\n📋 1. Verificar tabla PERSONA")
        query_persona = "SELECT cedula, nombre, apellido FROM persona LIMIT 10"
        resultado_persona = execute_query(query_persona, fetch_all=True)
        
        if resultado_persona:
            print(f"✅ Se encontraron {len(resultado_persona)} registros en PERSONA:")
            for i, row in enumerate(resultado_persona[:5], 1):
                print(f"   {i}. Cédula: {row[0]} - Nombre: {row[1]} {row[2]}")
        else:
            print("❌ No se encontraron registros en PERSONA")
        
        print("\n📋 2. Verificar tabla USUARIOS")
        query_usuarios = """
        SELECT cedula_usuario, login_usuario, rol, activo 
        FROM usuarios 
        WHERE rol = 'Estudiante' 
        LIMIT 10
        """
        resultado_usuarios = execute_query(query_usuarios, fetch_all=True)
        
        if resultado_usuarios:
            print(f"✅ Se encontraron {len(resultado_usuarios)} estudiantes en USUARIOS:")
            for i, row in enumerate(resultado_usuarios[:5], 1):
                print(f"   {i}. Cédula: {row[0]} - Login: {row[1]} - Activo: {row[3]}")
        else:
            print("❌ No se encontraron estudiantes en USUARIOS")
        
        print("\n📋 3. Verificar tabla ESTUDIANTE")
        query_estudiante = """
        SELECT cedula_estudiante, id_carrera, semestre_actual, estado_registro 
        FROM estudiante 
        LIMIT 10
        """
        resultado_estudiante = execute_query(query_estudiante, fetch_all=True)
        
        if resultado_estudiante:
            print(f"✅ Se encontraron {len(resultado_estudiante)} registros en ESTUDIANTE:")
            for i, row in enumerate(resultado_estudiante[:5], 1):
                print(f"   {i}. Cédula: {row[0]} - Carrera: {row[1]} - Semestre: {row[2]} - Estado: {row[3]}")
        else:
            print("❌ No se encontraron registros en ESTUDIANTE")
        
        print("\n📋 4. Verificar JOIN completo (estudiantes activos)")
        query_completo = """
        SELECT 
            u.cedula_usuario,
            p.nombre,
            p.apellido,
            e.id_carrera,
            e.semestre_actual,
            c.nombre_carrera,
            e.estado_registro
        FROM usuarios u
        INNER JOIN persona p ON u.cedula_usuario = p.cedula
        LEFT JOIN estudiante e ON p.cedula = e.cedula_estudiante
        LEFT JOIN carrera c ON e.id_carrera = c.id_carrera
        WHERE u.rol = 'Estudiante' AND u.activo = true
        LIMIT 10
        """
        resultado_completo = execute_query(query_completo, fetch_all=True)
        
        if resultado_completo:
            print(f"✅ Se encontraron {len(resultado_completo)} estudiantes activos:")
            for i, row in enumerate(resultado_completo[:5], 1):
                print(f"   {i}. Cédula: {row[0]} - Nombre: {row[1]} {row[2]} - Carrera: {row[6]} - Semestre: {row[4]}")
        else:
            print("❌ No se encontraron estudiantes activos en el JOIN")
        
        print("\n📋 5. Buscar cédulas específicas de prueba")
        cedulas_prueba = ['V-12345678', '12345678', 'V-00000000', 'admin']
        
        for cedula in cedulas_prueba:
            print(f"\n🔍 Buscando cédula: '{cedula}'")
            
            # Buscar en persona
            query_test = "SELECT cedula, nombre, apellido FROM persona WHERE cedula = %s"
            resultado_test = execute_query(query_test, (cedula,), fetch_one=True)
            
            if resultado_test:
                print(f"   ✅ Encontrado en PERSONA: {resultado_test[1]} {resultado_test[2]}")
                
                # Buscar en usuarios
                query_user = "SELECT cedula_usuario, rol, activo FROM usuarios WHERE cedula_usuario = %s"
                resultado_user = execute_query(query_user, (cedula,), fetch_one=True)
                
                if resultado_user:
                    print(f"   ✅ Encontrado en USUARIOS: Rol={resultado_user[1]}, Activo={resultado_user[2]}")
                else:
                    print(f"   ❌ No encontrado en USUARIOS")
            else:
                print(f"   ❌ No encontrado en PERSONA")
        
        print("\n📋 6. Estadísticas generales")
        stats_queries = [
            ("Total PERSONA", "SELECT COUNT(*) as total FROM persona"),
            ("Total USUARIOS", "SELECT COUNT(*) as total FROM usuarios"),
            ("Estudiantes en USUARIOS", "SELECT COUNT(*) as total FROM usuarios WHERE rol = 'Estudiante'"),
            ("Total ESTUDIANTE", "SELECT COUNT(*) as total FROM estudiante"),
            ("Estudiantes activos", "SELECT COUNT(*) as total FROM usuarios WHERE rol = 'Estudiante' AND activo = true")
        ]
        
        for name, query in stats_queries:
            resultado = execute_query(query, fetch_one=True)
            total = resultado[0] if resultado else 0
            print(f"   📊 {name}: {total}")
        
    except Exception as e:
        print(f"❌ Error en depuración: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
