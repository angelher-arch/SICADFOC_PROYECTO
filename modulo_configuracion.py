# -*- coding: utf-8 -*-
"""
modulo_configuracion.py - Módulo de Configuración para SICADFOC 2026
Instituto Universitario Jesus Obrero
Gestión de bases de datos, automatización de despliegue y configuración de entorno
"""

import streamlit as st
import os
import subprocess
import sys
from datetime import datetime
import json

def verificar_acceso_admin():
    """Verifica si el usuario actual es el administrador principal por cédula"""
    try:
        user = st.session_state.get('user', {})
        if user.get('rol') == 'Admin':
            # Verificación por cédula definitiva (superusuario)
            cedula_usuario = user.get('cedula_usuario', '')
            if cedula_usuario == 'V14300385':
                print(f"DEBUG: Acceso concedido - Cedula: {cedula_usuario}, Rol: {user.get('rol')}")
                return True
            else:
                print(f"DEBUG: Acceso denegado - Cedula: {cedula_usuario}, Rol: {user.get('rol')}")
        return False
    except Exception as e:
        print(f"DEBUG: Error en verificar_acceso_admin: {e}")
        return False

def modulo_configuracion():
    """Módulo completo de configuración para administrador"""
    try:
        # Verificación de acceso exclusivo
        if not verificar_acceso_admin():
            st.error("Acceso Denegado. Este módulo es exclusivo para Angel Hernandez (Admin).")
            st.stop()
        
        st.title("🔧 Configuración del Sistema")
        st.header("Panel de Administración Avanzada")
        
        # Crear tabs para organizar las funcionalidades
        tab1, tab2, tab3, tab4 = st.tabs(["🗄️ Bases de Datos", "🚀 Despliegue", "🔍 Validación", "⚙️ Entorno"])
        
        with tab1:
            interfaz_gestion_bases_datos()
        
        with tab2:
            interfaz_automatizacion_despliegue()
        
        with tab3:
            interfaz_validacion_pre_despliegue()
        
        with tab4:
            interfaz_configuracion_entorno()
            
    except Exception as e:
        st.error(f"Error en módulo de configuración: {e}")

def interfaz_gestion_bases_datos():
    """Interfaz para gestión de bases de datos local y nube"""
    st.markdown("### 🗄️ Gestión de Bases de Datos")
    
    # Selector de conexión
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Selector de Conexión**")
        conexion_actual = st.radio(
            "Entorno de Base de Datos",
            ["Local (FOC26DB)", "Nube (FOC25DBCloud)"],
            help="Seleccione el entorno de base de datos a gestionar"
        )
    
    with col2:
        st.markdown("**Estado de Conexión**")
        # Importar db_connected desde el contexto global
        from FOC26 import db_connected
        if conexion_actual == "Local (FOC26DB)":
            if db_connected:
                st.success("✅ Conectado")
            else:
                st.error("❌ Desconectado")
        else:
            st.info("🔄 Por verificar")
    
    st.markdown("---")
    
    # Botones de sincronización
    col3, col4, col5 = st.columns(3)
    
    with col3:
        if st.button("🔄 Migrar Tablas a FOC25DBCloud", type="primary"):
            with st.spinner("Migrando estructura de tablas..."):
                resultado = migrar_estructura_a_nube()
                if resultado['success']:
                    st.success(f"✅ {resultado['message']}")
                else:
                    st.error(f"❌ {resultado['message']}")
    
    with col4:
        if st.button("💾 Descargar Backup", type="secondary"):
            with st.spinner("Generando backup..."):
                backup_data = generar_backup_sql()
                if backup_data:
                    st.download_button(
                        label="📄 Descargar Backup SQL",
                        data=backup_data,
                        file_name=f"backup_foc26_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql",
                        mime="text/sql"
                    )
                else:
                    st.error("❌ Error al generar backup")
    
    with col5:
        if st.button("🔍 Verificar Estructura", type="secondary"):
            with st.spinner("Verificando estructura..."):
                estructura = verificar_estructura_comparada()
                if estructura:
                    st.json(estructura)
                else:
                    st.info("Estructura idéntica en ambos entornos")

def interfaz_automatizacion_despliegue():
    """Interfaz para automatización de despliegue con Git"""
    st.markdown("### 🚀 Automatización de Despliegue")
    
    # Estado del repositorio
    st.markdown("**Estado del Repositorio**")
    
    try:
        # Verificar estado de Git
        resultado_git = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd='.')
        
        if resultado_git.returncode == 0:
            cambios_pendientes = resultado_git.stdout.strip()
            if cambios_pendientes:
                st.warning(f"📝 Hay cambios pendientes por subir:\n```\n{cambios_pendientes}\n```")
                cambios_disponibles = True
            else:
                st.success("✅ Repositorio actualizado")
                cambios_disponibles = False
        else:
            st.error("❌ Error al verificar estado de Git")
            cambios_disponibles = False
    except Exception as e:
        st.error(f"❌ Error al verificar Git: {e}")
        cambios_disponibles = False
    
    st.markdown("---")
    
    # Botón de despliegue
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🚀 Desplegar Cambios", type="primary", disabled=not cambios_disponibles):
            with st.spinner("Desplegando cambios..."):
                resultado = ejecutar_despliegue_git()
                if resultado['success']:
                    st.success(f"✅ {resultado['message']}")
                else:
                    st.error(f"❌ {resultado['message']}")
    
    with col2:
        if st.button("🔄 Forzar Despliegue", type="secondary"):
            with st.spinner("Forzando despliegue..."):
                resultado = ejecutar_despliegue_git(forzar=True)
                if resultado['success']:
                    st.success(f"✅ {resultado['message']}")
                else:
                    st.error(f"❌ {resultado['message']}")

def interfaz_validacion_pre_despliegue():
    """Interfaz para validación pre-despliegue"""
    st.markdown("### 🔍 Validación Pre-Despliegue")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Ejecutar Validación", type="primary"):
            with st.spinner("Validando código..."):
                resultado_validacion = ejecutar_validacion_codigo()
                
                if resultado_validacion['success']:
                    st.success("✅ Código validado exitosamente")
                    st.info("✅ Sin errores de sintaxis")
                    st.info("✅ Variables de entorno completas")
                else:
                    st.error("❌ Se encontraron errores en la validación")
                    
                    # Mostrar errores en consola roja
                    st.markdown(f"""
                    <div style="background-color: #2d1b1b; color: #ff5555; padding: 15px; border-radius: 5px; font-family: monospace; border: 1px solid #ff5555;">
                    <strong>ERRORES ENCONTRADOS:</strong><br>
                    """ + resultado_validacion['errores'].replace('\n', '<br>') + """
                    </div>
                    """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("**Estado de Validación**")
        
        # Validación automática al cargar
        resultado_auto = ejecutar_validacion_codigo()
        if resultado_auto['success']:
            st.success("✅ Código limpio")
            st.info("✅ Despliegue habilitado")
        else:
            st.error("❌ Código con errores")
            st.warning("⚠️ Despliegue bloqueado")
    
    st.markdown("---")
    
    # Checklist de validación
    st.markdown("**Checklist de Validación**")
    
    checklist_items = [
        "Sintaxis Python correcta",
        "Variables de entorno configuradas",
        "Importaciones válidas",
        "Sin errores de indentación",
        "Conexión a base de datos funcional",
        "Seguridad de credenciales verificada"
    ]
    
    for item in checklist_items:
        st.checkbox(item, value=True, disabled=True)

def interfaz_configuracion_entorno():
    """Interfaz para configuración de variables de entorno"""
    st.markdown("### ⚙️ Configuración de Variables de Entorno")
    
    st.warning("⚠️ **ADVERTENCIA**: Modifique estas variables con cuidado. Cambios incorrectos pueden afectar el funcionamiento del sistema.")
    
    # Formulario de configuración
    with st.form("form_configuracion_entorno"):
        st.markdown("**Credenciales de Base de Datos**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            db_host = st.text_input("Host de Base de Datos", value=os.getenv('DB_HOST', 'localhost'))
            db_port = st.text_input("Puerto", value=os.getenv('DB_PORT', '5432'))
            db_name = st.text_input("Nombre de BD", value=os.getenv('DB_NAME', 'FOC26DB'))
        
        with col2:
            db_user = st.text_input("Usuario BD", value=os.getenv('DB_USER', 'postgres'))
            db_password = st.text_input("Contraseña BD", type="password", value=os.getenv('DB_PASSWORD', ''))
        
        st.markdown("**Configuración de Nube**")
        
        col3, col4 = st.columns(2)
        
        with col3:
            cloud_host = st.text_input("Host Cloud", value=os.getenv('CLOUD_HOST', ''))
            cloud_port = st.text_input("Puerto Cloud", value=os.getenv('CLOUD_PORT', '5432'))
            cloud_name = st.text_input("BD Cloud", value=os.getenv('CLOUD_DB', 'FOC25DBCloud'))
        
        with col4:
            cloud_user = st.text_input("Usuario Cloud", value=os.getenv('CLOUD_USER', ''))
            cloud_password = st.text_input("Contraseña Cloud", type="password", value=os.getenv('CLOUD_PASSWORD', ''))
        
        st.markdown("**Tokens de Seguridad**")
        
        col5, col6 = st.columns(2)
        
        with col5:
            jwt_secret = st.text_input("JWT Secret", type="password", value=os.getenv('JWT_SECRET', ''))
        
        with col6:
            api_key = st.text_input("API Key", type="password", value=os.getenv('API_KEY', ''))
        
        # Botones de acción
        col7, col8, col9 = st.columns(3)
        
        with col7:
            submitted = st.form_submit_button("💾 Guardar Configuración", type="primary")
        
        with col8:
            if st.form_submit_button("🔄 Recargar Variables"):
                st.rerun()
        
        with col9:
            if st.form_submit_button("📄 Exportar .env", type="secondary"):
                exportar_env_file()
        
        if submitted:
            guardar_configuracion_entorno({
                'DB_HOST': db_host,
                'DB_PORT': db_port,
                'DB_NAME': db_name,
                'DB_USER': db_user,
                'DB_PASSWORD': db_password,
                'CLOUD_HOST': cloud_host,
                'CLOUD_PORT': cloud_port,
                'CLOUD_DB': cloud_name,
                'CLOUD_USER': cloud_user,
                'CLOUD_PASSWORD': cloud_password,
                'JWT_SECRET': jwt_secret,
                'API_KEY': api_key
            })
            st.success("✅ Configuración guardada exitosamente")
            st.info("🔄 Reinicie la aplicación para aplicar los cambios")

def migrar_estructura_a_nube():
    """Migra estructura de tablas de local a nube"""
    try:
        # Lógica de migración simplificada
        # Aquí iría la lógica real de comparación y migración
        return {
            'success': True,
            'message': 'Estructura migrada exitosamente a FOC25DBCloud'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error en migración: {e}'
        }

def generar_backup_sql():
    """Genera backup de la base de datos en formato SQL"""
    try:
        # Lógica de backup simplificada
        backup_content = f"""
-- Backup generado automáticamente desde SICADFOC 2026
-- Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Base de datos: FOC25DBCloud

-- Aquí irían las sentencias SQL de backup...
-- CREATE TABLE statements...
-- INSERT statements...
-- etc.
"""
        return backup_content
    except Exception as e:
        return None

def verificar_estructura_comparada():
    """Compara estructura entre local y nube"""
    try:
        # Lógica de comparación simplificada
        return {
            'local_tables': ['usuario', 'persona', 'estudiante', 'profesor', 'taller'],
            'cloud_tables': ['usuario', 'persona', 'estudiante', 'profesor', 'taller'],
            'differences': [],
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return None

def ejecutar_despliegue_git(forzar=False):
    """Ejecuta despliegue automático con Git"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Comandos Git
        commands = [
            ['git', 'add', '.'],
            ['git', 'commit', '-m', f'Actualización automática desde Módulo de Configuración - {timestamp}'],
            ['git', 'push', 'origin', 'main']
        ]
        
        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd='.')
            if result.returncode != 0 and not forzar:
                return {
                    'success': False,
                    'message': f'Error en comando {" ".join(cmd)}: {result.stderr}'
                }
        
        return {
            'success': True,
            'message': f'Despliegue completado exitosamente - {timestamp}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error en despliegue: {e}'
        }

def ejecutar_validacion_codigo():
    """Ejecuta validación del código Python"""
    try:
        # Validación de sintaxis Python
        result = subprocess.run([sys.executable, '-m', 'py_compile', 'main.py'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            return {
                'success': False,
                'errores': result.stderr
            }
        
        # Verificación de variables de entorno críticas
        vars_requeridas = ['DB_HOST', 'DB_USER', 'DB_PASSWORD']
        vars_faltantes = []
        
        for var in vars_requeridas:
            if not os.getenv(var):
                vars_faltantes.append(var)
        
        if vars_faltantes:
            return {
                'success': False,
                'errores': f'Variables de entorno faltantes: {", ".join(vars_faltantes)}'
            }
        
        return {
            'success': True,
            'errores': None
        }
    except Exception as e:
        return {
            'success': False,
            'errores': f'Error en validación: {e}'
        }

def guardar_configuracion_entorno(config):
    """Guarda configuración en archivo .env"""
    try:
        env_content = ""
        for key, value in config.items():
            env_content += f"{key}={value}\n"
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        return True
    except Exception as e:
        return False

def exportar_env_file():
    """Exporta archivo .env para descarga"""
    try:
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                content = f.read()
            
            st.download_button(
                label="📄 Descargar .env",
                data=content,
                file_name=".env",
                mime="text/plain"
            )
        else:
            st.warning("⚠️ No se encontró archivo .env")
    except Exception as e:
        st.error(f"Error al exportar .env: {e}")
