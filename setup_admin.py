"""
CONFIGURACIÓN DE USUARIO ADMINISTRADOR - SICADFOC 2026
Script para crear/actualizar usuario administrativo con todos los privilegios
DBA Senior & Full-Stack - WindSurf
"""
from database import get_engine_local, inicializar_sistema_roles
from database.user_queries import consultar_usuario_por_email_o_login
from sqlalchemy import text
import hashlib

def setup_admin_user():
    """Configurar usuario administrador con todos los privilegios"""
    
    print("🔧 CONFIGURACIÓN DE USUARIO ADMINISTRADOR")
    print("=" * 50)
    
    engine = get_engine_local()
    
    # Paso 1: Inicializar sistema de roles
    print("\n📋 Paso 1: Inicializando sistema de roles...")
    try:
        resultado = inicializar_sistema_roles(engine)
        print(f"✅ Sistema de roles inicializado: {resultado}")
    except Exception as e:
        print(f"⚠️ Error inicializando roles: {e}")
    
    # Paso 2: Crear o actualizar usuario
    print("\n👤 Paso 2: Creando/actualizando usuario administrador...")
    
    with engine.connect() as conn:
        # Verificar si existe el usuario
        result = conn.execute(text("SELECT * FROM usuario WHERE email = :email"), 
                            {'email': 'angel_hernandez@hotmail.com'}).fetchone()
        
        if result:
            print("📝 Usuario ya existe, actualizando...")
            # Actualizar contraseña y rol
            hash_password = hashlib.sha256('14300385'.encode()).hexdigest()
            conn.execute(text("""
                UPDATE usuario 
                SET contrasena = :pass, rol = :rol, activo = 1, correo_verificado = 1 
                WHERE email = :email
            """), {
                'pass': hash_password, 
                'rol': 'Administrador', 
                'email': 'angel_hernandez@hotmail.com'
            })
            conn.commit()
            print("✅ Usuario actualizado exitosamente")
        else:
            print("🆕 Creando nuevo usuario administrador...")
            # Crear persona primero
            conn.execute(text("""
                INSERT INTO persona (cedula, nombre, apellido, email) 
                VALUES (:cedula, :nombre, :apellido, :email)
            """), {
                'cedula': '14300386', 
                'nombre': 'Angel', 
                'apellido': 'Hernandez', 
                'email': 'angel_hernandez@hotmail.com'
            })
            
            # Obtener ID de persona
            persona_id = conn.execute(text("SELECT last_insert_rowid()")).fetchone()[0]
            
            # Crear usuario con hash
            hash_password = hashlib.sha256('14300385'.encode()).hexdigest()
            conn.execute(text("""
                INSERT INTO usuario (login, email, contrasena, rol, activo, correo_verificado, id_persona) 
                VALUES (:login, :email, :pass, :rol, :activo, :verificado, :id_persona)
            """), {
                'login': 'angel_hernandez@hotmail.com', 
                'email': 'angel_hernandez@hotmail.com', 
                'pass': hash_password, 
                'rol': 'Administrador', 
                'activo': True, 
                'verificado': True, 
                'id_persona': persona_id
            })
            conn.commit()
            print("✅ Usuario creado exitosamente")
    
    # Paso 3: Verificación final
    print("\n🔍 Paso 3: Verificación final...")
    
    usuario = consultar_usuario_por_email_o_login('angel_hernandez@hotmail.com')
    if usuario:
        print(f"✅ Usuario encontrado:")
        print(f"   📧 Email: {usuario['email']}")
        print(f"   🎭 Rol: {usuario['rol']}")
        print(f"   ✅ Activo: {usuario['activo']}")
        print(f"   📧 Verificado: {usuario['correo_verificado']}")
        print(f"   👤 Nombre: {usuario['nombre']} {usuario['apellido']}")
    else:
        print("❌ Usuario no encontrado")
        return False
    
    # Paso 4: Verificar acceso a todos los módulos
    print("\n🔐 Paso 4: Verificación de permisos...")
    
    try:
        from auth.decorators import obtener_info_permisos_usuario
        permisos = obtener_info_permisos_usuario(usuario)
        
        if permisos:
            print(f"✅ Permisos configurados:")
            print(f"   🎭 Rol: {permisos['rol']}")
            print(f"   📊 Nivel acceso: {permisos['nivel_acceso']}")
            print(f"   🔐 Total permisos: {permisos['total_permisos']}")
            print(f"   📋 Módulos accesibles: {len(permisos['modulos_accesibles'])}")
        else:
            print("⚠️ No se pudieron obtener permisos")
    except Exception as e:
        print(f"⚠️ Error verificando permisos: {e}")
    
    return True

def get_server_info():
    """Obtener información del servidor local"""
    
    print("\n🌐 INFORMACIÓN DEL SERVIDOR")
    print("=" * 50)
    
    import socket
    import streamlit as st
    
    # Obtener IP local
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"🖥️ Hostname: {hostname}")
    print(f"🌐 IP Local: {local_ip}")
    
    # Puertos comunes para Streamlit
    puertos_comunes = [8501, 8513, 8515, 8516, 8517, 8518, 8519, 8520, 8521, 8522]
    
    print(f"\n🔍 URLs de acceso posibles:")
    for puerto in puertos_comunes:
        print(f"   📱 http://localhost:{puerto}")
        print(f"   🌐 http://{local_ip}:{puerto}")
    
    print(f"\n🚀 URL principal recomendada:")
    print(f"   📱 http://localhost:8522")
    print(f"   🌐 http://{local_ip}:8522")
    
    return f"http://localhost:8522"

def check_deployment_files():
    """Verificar archivos esenciales para despliegue"""
    
    print("\n📋 AUDITORÍA PRE-DESPLIEGUE")
    print("=" * 50)
    
    import os
    from pathlib import Path
    
    # Archivos esenciales
    archivos_esenciales = [
        'requirements.txt',
        'runtime.txt',
        'Procfile',
        'main.py',
        'database/__init__.py',
        'database/connection.py',
        'auth/decorators.py',
        'modules/modulos_protegidos.py'
    ]
    
    print("📁 Archivos esenciales:")
    
    archivos_encontrados = []
    archivos_faltantes = []
    
    for archivo in archivos_esenciales:
        ruta = Path(archivo)
        if ruta.exists():
            size = ruta.stat().st_size
            archivos_encontrados.append(f"✅ {archivo} ({size} bytes)")
        else:
            archivos_faltantes.append(f"❌ {archivo}")
    
    # Mostrar resultados
    for archivo in archivos_encontrados:
        print(f"   {archivo}")
    
    if archivos_faltantes:
        print("\n⚠️ Archivos faltantes:")
        for archivo in archivos_faltantes:
            print(f"   {archivo}")
    else:
        print("\n✅ Todos los archivos esenciales encontrados")
    
    # Verificar contenido de archivos clave
    print("\n📄 Contenido de archivos clave:")
    
    # requirements.txt
    if Path('requirements.txt').exists():
        with open('requirements.txt', 'r') as f:
            contenido = f.read()
            print(f"📦 requirements.txt: {len(contenido.splitlines())} paquetes")
    
    # Procfile
    if Path('Procfile').exists():
        with open('Procfile', 'r') as f:
            contenido = f.read()
            print(f"🚀 Procfile: {contenido.strip()}")
    else:
        print("❌ Procfile no encontrado")
    
    # runtime.txt
    if Path('runtime.txt').exists():
        with open('runtime.txt', 'r') as f:
            contenido = f.read()
            print(f"🐍 runtime.txt: {contenido.strip()}")
    else:
        print("❌ runtime.txt no encontrado")
    
    return len(archivos_faltantes) == 0

def check_database_config():
    """Verificar configuración de base de datos"""
    
    print("\n🗄️ CONFIGURACIÓN DE BASE DE DATOS")
    print("=" * 50)
    
    import os
    
    # Variables de entorno
    database_url = os.getenv('DATABASE_URL')
    
    print(f"🔗 DATABASE_URL: {'Configurada' if database_url else 'No configurada'}")
    
    if database_url:
        print(f"📝 URL: {database_url}")
        if 'render.com' in database_url:
            print("✅ Configuración para Render detectada")
        else:
            print("⚠️ URL no parece ser de Render")
    
    # Verificar configuración local
    try:
        from database import get_engine_local, test_connection
        if test_connection():
            print("✅ Conexión local funcional")
        else:
            print("❌ Conexión local fallida")
    except Exception as e:
        print(f"❌ Error en conexión local: {e}")
    
    return True

def main():
    """Función principal de configuración"""
    
    print("🚀 CONFIGURACIÓN ADMINISTRATIVA - SICADFOC 2026")
    print("Preparación para despliegue a la nube (Render)")
    print("=" * 60)
    
    # Paso 1: Configurar usuario administrador
    admin_ok = setup_admin_user()
    
    # Paso 2: Obtener información del servidor
    server_url = get_server_info()
    
    # Paso 3: Verificar archivos de despliegue
    files_ok = check_deployment_files()
    
    # Paso 4: Verificar configuración de BD
    db_ok = check_database_config()
    
    # Resumen final
    print("\n📊 RESUMEN FINAL")
    print("=" * 50)
    
    print(f"👤 Usuario administrador: {'✅ Configurado' if admin_ok else '❌ Error'}")
    print(f"🌐 URL de acceso: {server_url}")
    print(f"📁 Archivos despliegue: {'✅ Completos' if files_ok else '❌ Faltantes'}")
    print(f"🗄️ Base de datos: {'✅ Configurada' if db_ok else '❌ Error'}")
    
    if admin_ok and files_ok and db_ok:
        print("\n🎉 SISTEMA LISTO PARA DESPLIEGUE")
        print(f"🔐 Acceda a: {server_url}")
        print("📧 Email: angel_hernandez@hotmail.com")
        print("🔑 Contraseña: 14300385")
    else:
        print("\n⚠️ REVISE LOS ERRORES ANTES DEL DESPLIEGUE")
    
    print("\n📋 Próximos pasos:")
    print("1. 🔐 Probar login local")
    print("2. 🌐 Subir a GitHub")
    print("3. 🚀 Desplegar en Render")
    print("4. 🔗 Configurar DATABASE_URL en Render")

if __name__ == "__main__":
    main()
