#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
configuracion.py - Módulo de Configuración y Monitoreo del Sistema
SICADFOC 2026 - Instituto Universitario Jesus Obrero
Panel de control para monitoreo de base de datos y actualizaciones del sistema
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time
import socket

# IMPORTACIONES LOCALES AL MÓDULO
try:
    from seguridad import tiene_permiso, SeguridadFOC26
    from database import motor_central, DatabaseManager
    from styles import aplicar_estilos_sicad, crear_tabla_configuracion, texto_adaptativo
except ImportError as e:
    st.error(f"Error importando módulos locales: {e}")
    sys.exit(1)

class MotorConfiguracion:
    """Motor para configuración y monitoreo del sistema"""
    
    def __init__(self):
        """Inicialización del motor de configuración"""
        self.motor = motor_central
        self.db_manager = DatabaseManager()
    
    def detectar_entorno_bd(self) -> Dict[str, Any]:
        """Detectar el entorno de base de datos (NUBE vs LOCAL)"""
        try:
            # Obtener configuración actual de la base de datos
            db_host = os.getenv('DB_HOST', 'localhost')
            db_name = os.getenv('DB_NAME', 'db_foc26')
            db_port = os.getenv('DB_PORT', '5432')
            
            # Determinar entorno basado en el host
            if 'render.com' in db_host.lower() or 'railway.app' in db_host.lower():
                entorno = 'NUBE'
                icono = '🟢'
                descripcion = 'Conectado a NUBE (Render)'
            elif 'localhost' in db_host.lower() or '127.0.0.1' in db_host:
                entorno = 'LOCAL'
                icono = '🔵'
                descripcion = 'Conectado a LOCAL (localhost)'
            else:
                entorno = 'EXTERNO'
                icono = '🟡'
                descripcion = f'Conectado a EXTERNO ({db_host})'
            
            # Probar conexión real
            try:
                test_conn = self.db_manager.test_connection()
                conexion_status = test_conn.get('status', False)
                conexion_msg = test_conn.get('message', 'Sin mensaje')
            except Exception as e:
                conexion_status = False
                conexion_msg = f'Error: {str(e)}'
            
            return {
                'entorno': entorno,
                'icono': icono,
                'descripcion': descripcion,
                'conexion_status': conexion_status,
                'conexion_msg': conexion_msg,
                'db_host': db_host,
                'db_name': db_name,
                'db_port': db_port,
                'db_user': os.getenv('DB_USER', 'postgres')
            }
            
        except Exception as e:
            return {
                'entorno': 'DESCONOCIDO',
                'icono': '🔴',
                'descripcion': f'Error detectando entorno: {str(e)}',
                'conexion_status': False,
                'conexion_msg': 'Error de configuración',
                'db_host': 'N/A',
                'db_name': 'N/A',
                'db_port': 'N/A',
                'db_user': 'N/A'
            }
    
    def verificar_actualizaciones_recientes(self) -> Dict[str, Any]:
        """Verificar actualizaciones recientes en archivos clave"""
        try:
            archivos_clave = [
                'main.py',
                'database.py',
                'configuracion.py',
                'seguridad.py'
            ]
            
            ahora = datetime.now()
            actualizaciones = []
            
            for archivo in archivos_clave:
                ruta_archivo = os.path.join(os.getcwd(), archivo)
                if os.path.exists(ruta_archivo):
                    mod_time = datetime.fromtimestamp(os.path.getmtime(ruta_archivo))
                    diferencia = ahora - mod_time
                    
                    if diferencia.total_seconds() < 300:  # Menos de 5 minutos
                        actualizaciones.append({
                            'archivo': archivo,
                            'fecha_modificacion': mod_time.strftime('%Y-%m-%d %H:%M:%S'),
                            'hace_segundos': int(diferencia.total_seconds()),
                            'hace_minutos': int(diferencia.total_seconds() / 60)
                        })
            
            hay_actualizaciones = len(actualizaciones) > 0
            mensaje_actualizacion = ''
            
            if hay_actualizaciones:
                mas_reciente = min(actualizaciones, key=lambda x: x['hace_segundos'])
                if mas_reciente['hace_minutos'] < 1:
                    mensaje_actualizacion = f"⚠️ Actualización detectada: Hace {mas_reciente['hace_segundos']} segundos en {mas_reciente['archivo']}"
                else:
                    mensaje_actualizacion = f"⚠️ Actualización detectada: Hace {mas_reciente['hace_minutos']} minutos en {mas_reciente['archivo']}"
            
            return {
                'hay_actualizaciones': hay_actualizaciones,
                'mensaje_actualizacion': mensaje_actualizacion,
                'actualizaciones': actualizaciones,
                'verificacion_fecha': ahora.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'hay_actualizaciones': False,
                'mensaje_actualizacion': f'Error verificando actualizaciones: {str(e)}',
                'actualizaciones': [],
                'verificacion_fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def obtener_info_sistema(self) -> Dict[str, Any]:
        """Obtener información completa del sistema"""
        try:
            # Información de base de datos
            info_bd = self.detectar_entorno_bd()
            
            # Información de actualizaciones
            info_actualizaciones = self.verificar_actualizaciones_recientes()
            
            # Información del sistema
            info_sistema = {
                'python_version': sys.version,
                'plataforma': sys.platform,
                'directorio_actual': os.getcwd(),
                'usuario_sistema': os.getenv('USER', os.getenv('USERNAME', 'Desconocido')),
                'hora_actual': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'uptime_streamlit': 'N/A'  # Streamlit no proporciona uptime fácilmente
            }
            
            # Información de memoria (básica)
            try:
                import psutil
                proceso = psutil.Process()
                info_memoria = {
                    'memoria_usada_mb': round(proceso.memory_info().rss / 1024 / 1024, 2),
                    'cpu_percent': round(proceso.cpu_percent(), 2)
                }
            except ImportError:
                info_memoria = {
                    'memoria_usada_mb': 'N/A (psutil no instalado)',
                    'cpu_percent': 'N/A (psutil no instalado)'
                }
            
            return {
                'base_datos': info_bd,
                'actualizaciones': info_actualizaciones,
                'sistema': info_sistema,
                'memoria': info_memoria
            }
            
        except Exception as e:
            st.error(f"Error obteniendo información del sistema: {e}")
            return {}
    
    def forzar_reconexion_bd(self) -> Dict[str, Any]:
        """Forzar re-conexión a la base de datos"""
        try:
            # Limpiar caché de conexiones si existe
            if hasattr(self.db_manager, 'connection_pool'):
                if hasattr(self.db_manager.connection_pool, 'closeall'):
                    self.db_manager.connection_pool.closeall()
            
            # Forzar nueva conexión
            nueva_conexion = self.db_manager.get_connection()
            
            # Probar la nueva conexión
            test_result = self.db_manager.test_connection()
            
            return {
                'success': test_result.get('status', False),
                'message': 'Re-conexión exitosa' if test_result.get('status', False) else f'Error en re-conexión: {test_result.get("message", "Error desconocido")}',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error forzando re-conexión: {str(e)}',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def ejecutar_query_prueba(self) -> Dict[str, Any]:
        """Ejecutar query de prueba para verificar conexión"""
        try:
            query_prueba = "SELECT version() as version, current_database() as database, current_user as user"
            resultado = self.motor.ejecutar_consulta_personalizada(query_prueba)
            
            if resultado.get('success') and resultado.get('data'):
                data = resultado['data']
                if isinstance(data, list) and len(data) > 0:
                    row = data[0]
                    if isinstance(row, dict):
                        return {
                            'success': True,
                            'version': row.get('version', 'N/A'),
                            'database': row.get('database', 'N/A'),
                            'user': row.get('user', 'N/A')
                        }
                    else:
                        return {
                            'success': True,
                            'version': row[0] if len(row) > 0 else 'N/A',
                            'database': row[1] if len(row) > 1 else 'N/A',
                            'user': row[2] if len(row) > 2 else 'N/A'
                        }
            
            return {
                'success': False,
                'message': 'No se obtuvieron resultados del query de prueba'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error ejecutando query de prueba: {str(e)}'
            }

def configuracion_main():
    """Función principal del módulo de configuración"""
    try:
        # Aplicar estilos dinámicos con contraste automático
        aplicar_estilos_sicad()
        
        st.markdown("## ⚙️ Configuración del Sistema")
        st.markdown("---")
        
        # Verificar permisos
        rol_usuario = st.session_state.get('user_role', '')
        if not tiene_permiso(rol_usuario, 'Configuración', 'acceso'):
            st.warning("⚠️ No tienes permisos para acceder a la configuración del sistema")
            return
        
        motor_config = MotorConfiguracion()
        
        # Obtener información del sistema
        with st.spinner("Cargando información del sistema..."):
            info_sistema = motor_config.obtener_info_sistema()
        
        # Mostrar alerta de actualizaciones si hay
        if info_sistema.get('actualizaciones', {}).get('hay_actualizaciones', False):
            st.warning(info_sistema['actualizaciones']['mensaje_actualizacion'])
            st.info("🔄 El sistema ha detectado cambios recientes. Considere recargar la aplicación.")
        
        # Tabs para diferentes secciones
        tab1, tab2, tab3 = st.tabs([
            "📊 Estado del Sistema", 
            "🗄️ Base de Datos",
            "🔧 Herramientas"
        ])
        
        with tab1:
            mostrar_estado_sistema(info_sistema)
        
        with tab2:
            mostrar_configuracion_bd(motor_config, info_sistema.get('base_datos', {}))
        
        with tab3:
            mostrar_herramientas_sistema(motor_config)
        
    except Exception as e:
        st.error(f"Error en módulo de configuración: {e}")
        st.exception(e)

def mostrar_estado_sistema(info_sistema: Dict[str, Any]):
    """Mostrar estado general del sistema"""
    st.markdown("### 📊 Estado General del Sistema")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🖥️ Información del Sistema")
            
            sistema_info = info_sistema.get('sistema', {})
            
            contenido_html = f"""
            <p><strong>Python:</strong> {sistema_info.get('python_version', 'N/A')[:50]}...</p>
            <p><strong>Plataforma:</strong> {sistema_info.get('plataforma', 'N/A')}</p>
            <p><strong>Directorio:</strong> {sistema_info.get('directorio_actual', 'N/A')}</p>
            <p><strong>Usuario:</strong> {sistema_info.get('usuario_sistema', 'N/A')}</p>
            <p><strong>Hora Actual:</strong> {sistema_info.get('hora_actual', 'N/A')}</p>
            """
            st.markdown(crear_tabla_configuracion(contenido_html), unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 💾 Recursos del Sistema")
            
            memoria_info = info_sistema.get('memoria', {})
            
            contenido_html = f"""
            <p><strong>Memoria Usada:</strong> {memoria_info.get('memoria_usada_mb', 'N/A')} MB</p>
            <p><strong>CPU:</strong> {memoria_info.get('cpu_percent', 'N/A')}%</p>
            <p><strong>Estado:</strong> 🟢 Operativo</p>
            """
            st.markdown(crear_tabla_configuracion(contenido_html), unsafe_allow_html=True)
        
        # Actualizaciones recientes
        st.markdown("#### 🔄 Monitoreo de Actualizaciones")
        
        actualizaciones_info = info_sistema.get('actualizaciones', {})
        
        if actualizaciones_info.get('hay_actualizaciones', False):
            st.warning("Se detectaron actualizaciones recientes:")
            
            for actualizacion in actualizaciones_info.get('actualizaciones', []):
                contenido_html = f"""
                <p><strong>Archivo:</strong> {actualizacion['archivo']}</p>
                <p><strong>Modificado:</strong> {actualizacion['fecha_modificacion']}</p>
                <p><strong>Hace:</strong> {actualizacion['hace_minutos']} minutos</p>
                """
                st.markdown(crear_tabla_configuracion(contenido_html), unsafe_allow_html=True)
        else:
            st.success("✅ No se detectaron actualizaciones recientes (últimos 5 minutos)")
        
        st.markdown(f"*Última verificación: {actualizaciones_info.get('verificacion_fecha', 'N/A')}*")

def mostrar_configuracion_bd(motor: MotorConfiguracion, info_bd: Dict[str, Any]):
    """Mostrar configuración de base de datos"""
    st.markdown("### 🗄️ Configuración de Base de Datos")
    
    # Estado de conexión
    st.markdown("#### 🔌 Estado de Conexión")
    
    if info_bd.get('conexion_status', False):
        contenido_html = f"""
        <p class="status-indicator">{info_bd.get('icono', '🔴')} {info_bd.get('descripcion', 'Entorno desconocido')}</p>
        <p>✅ Conexión establecida</p>
        <p><em>{info_bd.get('conexion_msg', 'Sin mensaje')}</em></p>
        """
        st.markdown(f'<div class="transparent-container">{contenido_html}</div>', unsafe_allow_html=True)
    else:
        contenido_html = f"""
        <p class="status-indicator">🔴 Error de conexión</p>
        <p>❌ No se pudo establecer conexión</p>
        <p><em>{info_bd.get('conexion_msg', 'Sin mensaje')}</em></p>
        """
        st.markdown(f'<div class="transparent-container">{contenido_html}</div>', unsafe_allow_html=True)
    
    # Parámetros de configuración
    st.markdown("#### 📋 Parámetros Actuales")
    
    # Ocultar contraseña por seguridad
    parametros_bd = {
        'DB_HOST': info_bd.get('db_host', 'N/A'),
        'DB_NAME': info_bd.get('db_name', 'N/A'),
        'DB_USER': info_bd.get('db_user', 'N/A'),
        'DB_PORT': info_bd.get('db_port', 'N/A'),
        'DB_PASSWORD': '***' + os.getenv('DB_PASSWORD', '')[-2:] if os.getenv('DB_PASSWORD') else 'N/A'
    }
    
    df_parametros = pd.DataFrame(list(parametros_bd.items()), columns=['Parámetro', 'Valor'])
    st.dataframe(df_parametros, use_container_width=True)
    
    # Query de prueba
    st.markdown("#### 🧪 Query de Prueba")
    
    if st.button("Ejecutar Query de Prueba"):
        with st.spinner("Ejecutando query de prueba..."):
            resultado_query = motor.ejecutar_query_prueba()
        
        if resultado_query.get('success', False):
            st.success("✅ Query ejecutado exitosamente")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Base de Datos", resultado_query.get('database', 'N/A'))
            with col2:
                st.metric("Usuario", resultado_query.get('user', 'N/A'))
            with col3:
                st.metric("Versión", resultado_query.get('version', 'N/A')[:20] + "...")
        else:
            st.error(f"❌ Error en query: {resultado_query.get('message', 'Error desconocido')}")

def mostrar_herramientas_sistema(motor: MotorConfiguracion):
    """Mostrar herramientas del sistema"""
    st.markdown("### 🔧 Herramientas del Sistema")
    
    st.markdown("#### 🔄 Conexión de Base de Datos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Forzar Re-conexión", type="primary"):
            with st.spinner("Forzando re-conexión..."):
                resultado_reconexion = motor.forzar_reconexion_bd()
            
            if resultado_reconexion.get('success', False):
                st.success("✅ " + resultado_reconexion.get('message', 'Re-conexión exitosa'))
            else:
                st.error("❌ " + resultado_reconexion.get('message', 'Error en re-conexión'))
            
            st.info(f"Timestamp: {resultado_reconexion.get('timestamp', 'N/A')}")
    
    with col2:
        if st.button("🧪 Testear Conexión"):
            with st.spinner("Testeando conexión..."):
                test_result = motor.db_manager.test_connection()
            
            if test_result.get('status', False):
                st.success("✅ Conexión exitosa")
            else:
                st.error("❌ Error de conexión")
            
            st.info(f"Mensaje: {test_result.get('message', 'Sin mensaje')}")
    
    st.markdown("---")
    
    st.markdown("#### 📊 Información Avanzada")
    
    with st.expander("🔍 Ver Logs del Sistema"):
        st.info("Función de logs en desarrollo...")
    
    with st.expander("🗂️ Estructura de Archivos"):
        st.info("Función de explorador de archivos en desarrollo...")
    
    with st.expander("⚙️ Variables de Entorno"):
        # Mostrar variables de entorno no sensibles
        vars_seguras = ['PYTHONPATH', 'LANG', 'LC_ALL', 'PYTHONIOENCODING']
        env_info = {}
        
        for var in vars_seguras:
            env_info[var] = os.getenv(var, 'No definida')
        
        df_env = pd.DataFrame(list(env_info.items()), columns=['Variable', 'Valor'])
        st.dataframe(df_env, use_container_width=True)

# Alias de compatibilidad
def configuracion():
    """Alias de compatibilidad para el orquestador principal"""
    configuracion_main()
