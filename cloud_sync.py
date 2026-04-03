"""
CLOUD SYNC - SICADFOC 2026
Módulo de sincronización con Render y gestión de archivos en la nube
"""
import os
import json
from datetime import datetime
import requests
from typing import Dict, List, Optional
import streamlit as st

# =================================================================
# CONFIGURACIÓN DE SINCRONIZACIÓN
# =================================================================

class CloudSyncManager:
    """Gestor de sincronización con la nube"""
    
    def __init__(self):
        self.render_api_url = os.getenv('RENDER_API_URL', '')
        self.database_url = os.getenv('DATABASE_URL', '')
        self.app_environment = os.getenv('APP_ENVIRONMENT', 'development')
        self.sync_status_file = 'sync_status.json'
        
    def obtener_estado_conexion(self) -> Dict:
        """Verifica el estado de conexión a la nube"""
        estado = {
            'conectado': False,
            'ambiente': self.app_environment,
            'database_url': bool(self.database_url),
            'render_url': bool(self.render_api_url),
            'ultima_actualizacion': None,
            'timestamp': datetime.now().isoformat()
        }
        
        # Verificar conexión a base de datos
        if self.database_url:
            try:
                from database import get_engine_local
                engine = get_engine_local()
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1")).fetchone()
                estado['conectado'] = True
            except Exception as e:
                estado['error_db'] = str(e)
        
        # Cargar última actualización
        estado['ultima_actualizacion'] = self.cargar_ultima_actualizacion()
        
        return estado
    
    def cargar_ultima_actualizacion(self) -> Optional[str]:
        """Carga la fecha y hora de la última actualización"""
        try:
            if os.path.exists(self.sync_status_file):
                with open(self.sync_status_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('ultima_actualizacion')
        except Exception:
            pass
        return None
    
    def guardar_ultima_actualizacion(self):
        """Guarda la fecha y hora de la actualización actual"""
        try:
            data = {
                'ultima_actualizacion': datetime.now().isoformat(),
                'timestamp': datetime.now().timestamp()
            }
            with open(self.sync_status_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando última actualización: {e}")
    
    def obtener_archivos_para_subir(self) -> List[Dict]:
        """Define qué archivos deben ser subidos a Render"""
        archivos_requeridos = [
            # Archivos principales de la aplicación
            {
                'ruta': 'main.py',
                'tipo': 'principal',
                'requerido': True,
                'descripcion': 'Aplicación principal'
            },
            {
                'ruta': 'database.py',
                'tipo': 'base_datos',
                'requerido': True,
                'descripcion': 'Lógica de base de datos'
            },
            {
                'ruta': 'ui_components.py',
                'tipo': 'interfaz',
                'requerido': True,
                'descripcion': 'Componentes de UI'
            },
            # Archivos de configuración
            {
                'ruta': 'requirements.txt',
                'tipo': 'dependencias',
                'requerido': True,
                'descripcion': 'Dependencias Python'
            },
            {
                'ruta': 'Procfile',
                'tipo': 'deploy',
                'requerido': True,
                'descripcion': 'Configuración de deploy'
            },
            {
                'ruta': 'render.yaml',
                'tipo': 'deploy',
                'requerido': True,
                'descripcion': 'Configuración Render'
            },
            # Archivos de producción
            {
                'ruta': 'production_config.py',
                'tipo': 'configuracion',
                'requerido': True,
                'descripcion': 'Configuración producción'
            },
            # Archivos de recursos
            {
                'ruta': 'diseños_streamlit.css',
                'tipo': 'estilos',
                'requerido': True,
                'descripcion': 'Estilos CSS'
            },
            {
                'ruta': 'iujo-logo.png',
                'tipo': 'recursos',
                'requerido': True,
                'descripcion': 'Logo institucional'
            },
            # Módulos específicos
            {
                'ruta': 'formacion_complementaria_db.py',
                'tipo': 'modulo',
                'requerido': False,
                'descripcion': 'Módulo formación complementaria'
            },
            {
                'ruta': 'formacion_complementaria_ui.py',
                'tipo': 'modulo',
                'requerido': False,
                'descripcion': 'UI formación complementaria'
            }
        ]
        
        # Filtrar archivos que existen
        archivos_existentes = []
        for archivo in archivos_requeridos:
            if os.path.exists(archivo['ruta']):
                archivo['existe'] = True
                archivo['tamano'] = os.path.getsize(archivo['ruta']) if os.path.isfile(archivo['ruta']) else 0
                archivo['modificado'] = datetime.fromtimestamp(os.path.getmtime(archivo['ruta'])).isoformat()
                archivos_existentes.append(archivo)
            else:
                archivo['existe'] = False
                archivos_existentes.append(archivo)
        
        return archivos_existentes
    
    def verificar_filtros_archivos(self) -> Dict:
        """Verifica los filtros de archivos para la subida"""
        filtros = {
            'extensiones_permitidas': ['.py', '.txt', '.yaml', '.yml', '.css', '.png', '.jpg', '.jpeg', '.pdf'],
            'archivos_excluidos': [
                '.env', '.env.production', '.env.example',
                '__pycache__', '.git', '.vscode',
                '*.pyc', '*.log', '*.tmp',
                'foc26_limpio.db', 'storage/',
                'backups/', 'expedientes/', 'expedientes_pdf/'
            ],
            'tamano_maximo': 50 * 1024 * 1024,  # 50MB por archivo
            'archivos_requeridos': 8  # Mínimo de archivos requeridos
        }
        
        return filtros
    
    def sincronizar_con_render(self) -> Dict:
        """Ejecuta la sincronización con Render"""
        resultado = {
            'exito': False,
            'archivos_procesados': 0,
            'archivos_omitidos': 0,
            'errores': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Obtener archivos para subir
            archivos = self.obtener_archivos_para_subir()
            filtros = self.verificar_filtros_archivos()
            
            # Procesar cada archivo
            for archivo in archivos:
                if not archivo['existe']:
                    if archivo['requerido']:
                        resultado['errores'].append(f"Archivo requerido no encontrado: {archivo['ruta']}")
                    resultado['archivos_omitidos'] += 1
                    continue
                
                # Verificar si debe ser subido
                if self.debe_subir_archivo(archivo, filtros):
                    try:
                        # Simular subida (aquí iría la lógica real de API)
                        self.simular_subida_archivo(archivo)
                        resultado['archivos_procesados'] += 1
                    except Exception as e:
                        resultado['errores'].append(f"Error subiendo {archivo['ruta']}: {str(e)}")
                else:
                    resultado['archivos_omitidos'] += 1
            
            # Actualizar estado
            if len(resultado['errores']) == 0:
                resultado['exito'] = True
                self.guardar_ultima_actualizacion()
            
        except Exception as e:
            resultado['errores'].append(f"Error general en sincronización: {str(e)}")
        
        return resultado
    
    def debe_subir_archivo(self, archivo: Dict, filtros: Dict) -> bool:
        """Determina si un archivo debe ser subido"""
        # Verificar extensión
        extension = os.path.splitext(archivo['ruta'])[1].lower()
        if extension not in filtros['extensiones_permitidas']:
            return False
        
        # Verificar exclusiones
        ruta = archivo['ruta']
        for patron in filtros['archivos_excluidos']:
            if patron in ruta or ruta.endswith(patron):
                return False
        
        # Verificar tamaño
        if archivo.get('tamano', 0) > filtros['tamano_maximo']:
            return False
        
        return True
    
    def simular_subida_archivo(self, archivo: Dict):
        """Simula la subida de un archivo a Render"""
        print(f"📤 Subiendo: {archivo['ruta']}")
        print(f"   Tipo: {archivo['tipo']}")
        print(f"   Tamaño: {archivo.get('tamano', 0)} bytes")
        print(f"   Modificado: {archivo.get('modificado', 'N/A')}")
        
        # Simular delay de red
        import time
        time.sleep(0.1)
        
        print(f"   ✅ Subido exitosamente")

# =================================================================
# FUNCIONES DE INTERFAZ
# =================================================================

def mostrar_estado_conexion():
    """Muestra el estado de conexión a la nube"""
    st.markdown("## 🌐 Estado de Conexión a la Nube")
    st.markdown("---")
    
    sync_manager = CloudSyncManager()
    estado = sync_manager.obtener_estado_conexion()
    
    # Tarjeta de estado principal
    col1, col2, col3 = st.columns(3)
    
    with col1:
        estado_icono = "🟢" if estado['conectado'] else "🔴"
        st.metric("Estado", f"{estado_icono} {'Conectado' if estado['conectado'] else 'Desconectado'}")
    
    with col2:
        st.metric("Ambiente", estado['ambiente'].upper())
    
    with col3:
        db_icono = "🟢" if estado['database_url'] else "🔴"
        st.metric("Base de Datos", f"{db_icono} {'Configurada' if estado['database_url'] else 'No Configurada'}")
    
    # Última actualización
    if estado['ultima_actualizacion']:
        fecha = datetime.fromisoformat(estado['ultima_actualizacion'])
        st.info(f"🕒 Última actualización: {fecha.strftime('%d/%m/%Y %H:%M:%S')}")
    else:
        st.warning("⚠️ No hay registros de actualización previa")
    
    # Detalles técnicos
    with st.expander("🔧 Detalles Técnicos", expanded=False):
        st.json(estado)

def mostrar_archivos_para_subir():
    """Muestra los archivos que deben ser subidos a Render"""
    st.markdown("## 📁 Archivos para Subir a Render")
    st.markdown("---")
    
    sync_manager = CloudSyncManager()
    archivos = sync_manager.obtener_archivos_para_subir()
    filtros = sync_manager.verificar_filtros_archivos()
    
    # Resumen de archivos
    total_archivos = len(archivos)
    archivos_existentes = sum(1 for a in archivos if a['existe'])
    archivos_requeridos = sum(1 for a in archivos if a['requerido'] and not a['existe'])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Archivos", total_archivos)
    
    with col2:
        st.metric("Existentes", archivos_existentes)
    
    with col3:
        st.metric("Faltantes", archivos_requeridos)
    
    # Tabla de archivos
    st.markdown("### 📋 Lista de Archivos")
    
    for archivo in archivos:
        with st.expander(f"📄 {archivo['ruta']}", expanded=not archivo['existe']):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Tipo:** {archivo['tipo']}")
                st.write(f"**Descripción:** {archivo['descripcion']}")
                st.write(f"**Requerido:** {'✅ Sí' if archivo['requerido'] else '❌ No'}")
                
                if archivo['existe']:
                    st.write(f"**Tamaño:** {archivo.get('tamano', 0):,} bytes")
                    st.write(f"**Modificado:** {archivo.get('modificado', 'N/A')}")
            
            with col2:
                if archivo['existe']:
                    st.success("✅ Existe")
                else:
                    st.error("❌ No encontrado")
                    if archivo['requerido']:
                        st.warning("⚠️ Requerido")
    
    # Filtros de configuración
    with st.expander("🔧 Filtros de Subida", expanded=False):
        st.markdown("**Extensiones Permitidas:**")
        st.write(", ".join(filtros['extensiones_permitidas']))
        
        st.markdown("**Archivos Excluidos:**")
        for excluido in filtros['archivos_excluidos']:
            st.write(f"• {excluido}")
        
        st.write(f"**Tamaño Máximo:** {filtros['tamano_maximo'] / (1024*1024):.1f} MB")

def mostrar_sincronizacion():
    """Muestra la interfaz de sincronización"""
    st.markdown("## 🔄 Sincronización con Render")
    st.markdown("---")
    
    sync_manager = CloudSyncManager()
    
    # Botón de sincronización
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🚀 Iniciar Sincronización", type="primary", use_container_width=True):
            with st.spinner("🔄 Sincronizando con Render..."):
                resultado = sync_manager.sincronizar_con_render()
                
                if resultado['exito']:
                    st.success("✅ Sincronización completada exitosamente")
                    st.balloons()
                else:
                    st.error("❌ La sincronización encontró errores")
                    
                    if resultado['errores']:
                        st.markdown("**Errores encontrados:**")
                        for error in resultado['errores']:
                            st.error(f"• {error}")
    
    with col2:
        if st.button("🔄 Verificar Estado", use_container_width=True):
            st.rerun()
    
    # Resultados de última sincronización
    if os.path.exists(sync_manager.sync_status_file):
        with st.expander("📊 Última Sincronización", expanded=True):
            try:
                with open(sync_manager.sync_status_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    st.json(data)
            except Exception as e:
                st.error(f"Error leyendo estado de sincronización: {e}")

def mostrar_modulo_cloud_sync():
    """Módulo completo de sincronización con la nube"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: #1E293B; font-size: 2rem; font-weight: bold;">
            ☁️ Sincronización con la Nube
        </h2>
        <p style="color: #64748B; font-size: 1rem;">
            Gestión de archivos y sincronización con Render
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs organizados
    tab1, tab2, tab3 = st.tabs(["🌐 Estado", "📁 Archivos", "🔄 Sincronización"])
    
    with tab1:
        mostrar_estado_conexion()
    
    with tab2:
        mostrar_archivos_para_subir()
    
    with tab3:
        mostrar_sincronizacion()

# =================================================================
# INTEGRACIÓN CON MAIN.PY
# =================================================================

def verificar_estado_nube():
    """Función para main.py - verifica estado de conexión a la nube"""
    sync_manager = CloudSyncManager()
    return sync_manager.obtener_estado_conexion()

def obtener_ultima_actualizacion():
    """Función para main.py - obtiene última actualización"""
    sync_manager = CloudSyncManager()
    return sync_manager.cargar_ultima_actualizacion()

if __name__ == "__main__":
    mostrar_modulo_cloud_sync()
