#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
debug_conexion_render.py - Script de diagnóstico para conexión PostgreSQL en Render
"""

import os
import sys
import logging
from urllib.parse import urlparse

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def diagnosticar_entorno():
    """Diagnóstico completo del entorno Render"""
    
    print("🔍 === DIAGNÓSTICO DE ENTORNO RENDER ===\n")
    
    # 1. Variables de entorno críticas
    print("📋 VARIABLES DE ENTORNO:")
    critical_vars = [
        'DATABASE_URL',
        'ENVIRONMENT', 
        'PORT',
        'PYTHONPATH',
        'HOME'
    ]
    
    for var in critical_vars:
        value = os.getenv(var)
        if value:
            # Ocultar información sensible
            if 'PASSWORD' in var or 'TOKEN' in var:
                display_value = f"'{value[:10]}...{value[-4:]}'" if len(value) > 15 else "'***'"
            else:
                display_value = f"'{value}'"
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: <no definida>")
    
    print()
    
    # 2. Analizar DATABASE_URL si existe
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print("🔗 ANÁLISIS DE DATABASE_URL:")
        try:
            parsed = urlparse(database_url)
            print(f"  Esquema: {parsed.scheme}")
            print(f"  Usuario: {parsed.username}")
            print(f"  Host: {parsed.hostname}")
            print(f"  Puerto: {parsed.port}")
            print(f"  Base de datos: {parsed.path[1:] if parsed.path else '<sin nombre>'}")
            print(f"  SSL: {'require' in database_url.lower()}")
            
            # Validar formato
            if parsed.scheme not in ['postgresql', 'postgres']:
                print(f"  ⚠️  Esquema inválido: {parsed.scheme}")
            if not parsed.hostname:
                print(f"  ⚠️  Host no especificado")
            if not parsed.username:
                print(f"  ⚠️  Usuario no especificado")
                
        except Exception as e:
            print(f"  ❌ Error parseando DATABASE_URL: {e}")
    else:
        print("❌ DATABASE_URL no encontrada")
    
    print()
    
    # 3. Información del sistema
    print("💻 INFORMACIÓN DEL SISTEMA:")
    print(f"  Python: {sys.version}")
    print(f"  Directorio actual: {os.getcwd()}")
    print(f"  Usuario: {os.getenv('USER', os.getenv('USERNAME', '<no definido>')}")
    
    # 4. Módulos disponibles
    print("\n📚 MÓDULOS DISPONIBLES:")
    modules_to_check = ['psycopg2', 'psycopg2-binary', 'dotenv', 'urllib3']
    for module in modules_to_check:
        try:
            __import__(module)
            print(f"  ✅ {module}: disponible")
        except ImportError:
            print(f"  ❌ {module}: no disponible")
    
    print()

def probar_conexion_psycopg2():
    """Probar conexión directa con psycopg2"""
    print("🔌 === PRUEBA DE CONEXIÓN PSYCOPG2 ===\n")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL no disponible para prueba")
        return False
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        print("Conectando a PostgreSQL...")
        print(f"URL: postgresql://***@{urlparse(database_url).hostname}:{urlparse(database_url).port}/{urlparse(database_url).path[1:]}")
        
        # Intento de conexión
        conn = psycopg2.connect(
            database_url,
            cursor_factory=RealDictCursor,
            connect_timeout=10,
            application_name="SICADFOC2026_Debug"
        )
        
        print("✅ Conexión establecida")
        
        # Probar consulta simple
        with conn.cursor() as cursor:
            cursor.execute("SELECT version(), current_database(), current_user")
            result = cursor.fetchone()
            print(f"Versión PostgreSQL: {result['version'][:60]}...")
            print(f"Base de datos: {result['current_database']}")
            print(f"Usuario actual: {result['current_user']}")
        
        conn.close()
        print("✅ Conexión cerrada exitosamente")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Error operativo: {e}")
        if "authentication failed" in str(e).lower():
            print("💡 Posible causa: Credenciales incorrectas en DATABASE_URL")
        elif "connection refused" in str(e).lower():
            print("💡 Posible causa: Host incorrecto o firewall bloqueando")
        elif "timeout" in str(e).lower():
            print("💡 Posible causa: Problemas de red o servidor lento")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {type(e).__name__}: {e}")
        return False

def probar_conexion_render_config():
    """Probar conexión usando render_config.py"""
    print("\n🎯 === PRUEBA CON render_config.py ===\n")
    
    try:
        from render_config import get_render_config
        from conexion_render import get_conexion_render
        
        print("Cargando configuración Render...")
        config = get_render_config()
        
        print("Probando conexión con clase especializada...")
        conexion = get_conexion_render()
        
        if conexion.conectar():
            print("✅ Conexión exitosa")
            
            # Probar test completo
            if conexion.test_connection():
                print("✅ Test de conexión completo exitoso")
                conexion.desconectar()
                return True
            else:
                print("❌ Test de conexión falló")
                return False
        else:
            print("❌ No se pudo conectar")
            return False
            
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

def generar_recomendaciones():
    """Generar recomendaciones basadas en el diagnóstico"""
    print("\n💡 === RECOMENDACIONES ===\n")
    
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ CRÍTICO: DATABASE_URL no está definida")
        print("   Solución: Configurar DATABASE_URL en variables de entorno de Render")
        print("   Ejemplo: postgresql://usuario:password@host:port/database?sslmode=require")
        return
    
    try:
        parsed = urlparse(database_url)
        
        if not parsed.scheme or parsed.scheme not in ['postgresql', 'postgres']:
            print("⚠️  Esquema inválido en DATABASE_URL")
            print("   Solución: Usar 'postgresql://' o 'postgres://' al inicio")
        
        if not parsed.hostname:
            print("⚠️  Host no especificado")
            print("   Solución: Verificar que DATABASE_URL contenga el host correcto")
        
        if not parsed.username:
            print("⚠️  Usuario no especificado")
            print("   Solución: Incluir usuario en DATABASE_URL")
        
        if not parsed.password:
            print("⚠️  Contraseña no especificada")
            print("   Solución: Incluir contraseña en DATABASE_URL")
        
        if 'sslmode' not in database_url.lower():
            print("⚠️  SSL no configurado")
            print("   Solución: Agregar '?sslmode=require' a DATABASE_URL")
        
    except Exception:
        print("⚠️  No se pudo analizar DATABASE_URL")
        print("   Solución: Verificar formato de DATABASE_URL")
    
    print("\n📋 PASOS PARA SOLUCIONAR:")
    print("1. Verificar que DATABASE_URL esté configurada en Render")
    print("2. Confirmar que las credenciales sean correctas")
    print("3. Asegurar que SSL esté habilitado (sslmode=require)")
    print("4. Verificar que la base de datos esté accesible desde Render")
    print("5. Revisar logs de Render para errores específicos")

if __name__ == "__main__":
    print("🚀 INICIANDO DIAGNÓSTICO DE CONEXIÓN RENDER\n")
    
    # Ejecutar diagnóstico completo
    diagnosticar_entorno()
    exito_psycopg2 = probar_conexion_psycopg2()
    exito_render_config = probar_conexion_render()
    
    # Generar recomendaciones
    generar_recomendaciones()
    
    # Resumen final
    print(f"\n📊 === RESUMEN ===")
    print(f"Conexión psycopg2 directa: {'✅' if exito_psycopg2 else '❌'}")
    print(f"Conexión render_config: {'✅' if exito_render_config else '❌'}")
    
    if exito_psycopg2 and exito_render_config:
        print("🎉 Todas las pruebas exitosas - La conexión debería funcionar")
    else:
        print("⚠️  Hay problemas que deben resolverse antes del despliegue")
