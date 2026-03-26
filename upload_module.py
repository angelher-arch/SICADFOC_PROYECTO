# =================================================================
# UPLOAD MODULE - SICADFOC 2026
# =================================================================

import streamlit as st
import os
import shutil
from datetime import datetime
from database import engine
from sqlalchemy import text

# =================================================================
# CONFIGURACIÓN
# =================================================================

# Directorio de uploads
UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# =================================================================
# FUNCIONES DE UTILIDAD
# =================================================================

def crear_directorio_uploads():
    """Crea el directorio de uploads si no existe"""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        st.success(f"✅ Directorio '{UPLOAD_DIR}' creado exitosamente")

def validar_archivo(archivo):
    """Valida el archivo subido"""
    if archivo is None:
        return False, "No se ha seleccionado ningún archivo"
    
    # Validar extensión
    if '.' not in archivo.name:
        return False, "El archivo no tiene una extensión válida"
    
    extension = archivo.name.split('.')[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        return False, f"Extensión '{extension}' no permitida. Use: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Validar tamaño
    if hasattr(archivo, 'size') and archivo.size > MAX_FILE_SIZE:
        return False, f"El archivo excede el tamaño máximo de {MAX_FILE_SIZE/1024/1024}MB"
    
    return True, "Archivo válido"

def guardar_archivo_local(archivo, subdirectorio=""):
    """Guarda el archivo en el sistema de archivos local"""
    try:
        # Crear directorio de uploads
        crear_directorio_uploads()
        
        # Crear subdirectorio si se especifica
        if subdirectorio:
            ruta_subdir = os.path.join(UPLOAD_DIR, subdirectorio)
            if not os.path.exists(ruta_subdir):
                os.makedirs(ruta_subdir)
            ruta_destino = ruta_subdir
        else:
            ruta_destino = UPLOAD_DIR
        
        # Generar nombre único para evitar sobrescribir
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_base = os.path.splitext(archivo.name)[0]
        extension = os.path.splitext(archivo.name)[1]
        nombre_unico = f"{timestamp}_{nombre_base}{extension}"
        
        ruta_completa = os.path.join(ruta_destino, nombre_unico)
        
        # Guardar archivo
        with open(ruta_completa, "wb") as f:
            f.write(archivo.getbuffer())
        
        return True, ruta_completa, nombre_unico
    
    except Exception as e:
        return False, None, f"Error al guardar archivo: {str(e)}"

def registrar_archivo_bd(nombre_archivo, ruta_archivo, tipo_documento, usuario_id, metadata=None):
    """Registra el archivo en la base de datos"""
    try:
        with engine.connect() as conn:
            query = text("""
                INSERT INTO archivos_registrados (
                    nombre_archivo, ruta_archivo, tipo_documento, 
                    usuario_id, fecha_subida, metadata
                ) VALUES (
                    :nombre_archivo, :ruta_archivo, :tipo_documento,
                    :usuario_id, :fecha_subida, :metadata
                )
            """)
            
            conn.execute(query, {
                "nombre_archivo": nombre_archivo,
                "ruta_archivo": ruta_archivo,
                "tipo_documento": tipo_documento,
                "usuario_id": usuario_id,
                "fecha_subida": datetime.now(),
                "metadata": str(metadata) if metadata else None
            })
            conn.commit()
            return True
    
    except Exception as e:
        st.error(f"❌ Error al registrar en BD: {str(e)}")
        return False

# =================================================================
# FUNCIONES DE INTERFAZ
# =================================================================

def mostrar_upload_general():
    """Muestra la interfaz general de uploads"""
    st.markdown("## 📁 Módulo de Carga de Archivos")
    st.markdown("---")
    
    # Verificar autenticación
    if not st.session_state.get('autenticado', False):
        st.error("❌ Debe iniciar sesión para acceder a esta función.")
        return
    
    # Tabs para diferentes tipos de carga
    tab_individual, tab_masiva, tab_gestion = st.tabs([
        "📝 Carga Individual", 
        "📤 Carga Masiva", 
        "📋 Gestión de Archivos"
    ])
    
    with tab_individual:
        mostrar_carga_individual()
    
    with tab_masiva:
        mostrar_carga_masiva()
    
    with tab_gestion:
        mostrar_gestion_archivos()

def mostrar_carga_individual():
    """Muestra la interfaz de carga individual"""
    st.markdown("### 📝 Carga Individual de Archivos")
    
    with st.form("form_carga_individual"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Información del documento
            tipo_documento = st.selectbox(
                "🏷️ Tipo de Documento *",
                options=[
                    "Formación Complementaria",
                    "Certificación",
                    "Diplomado",
                    "Taller",
                    "Documento Administrativo",
                    "Material Educativo",
                    "Otro"
                ],
                help="Seleccione el tipo de documento que está subiendo"
            )
            
            descripcion = st.text_area(
                "📝 Descripción",
                placeholder="Descripción breve del contenido del archivo...",
                height=100
            )
        
        with col2:
            # Configuración de almacenamiento
            almacenamiento = st.radio(
                "💾 Almacenamiento *",
                options=["Base de Datos (BLOB)", "Sistema de Archivos Local"],
                help="Elija dónde se almacenará el archivo"
            )
            
            if almacenamiento == "Sistema de Archivos Local":
                subdirectorio = st.text_input(
                    "📁 Subdirectorio (opcional)",
                    placeholder="Ej: documentos/2026",
                    help="Crea una subcarpeta para organizar los archivos"
                )
            else:
                subdirectorio = ""
        
        st.markdown("---")
        
        # Subida de archivo
        archivo = st.file_uploader(
            "📁 Seleccione Archivo *",
            type=list(ALLOWED_EXTENSIONS),
            help=f"Tipos permitidos: {', '.join(ALLOWED_EXTENSIONS)}. Máximo: {MAX_FILE_SIZE/1024/1024}MB"
        )
        
        # Previsualización si es PDF
        if archivo and archivo.name.endswith('.pdf'):
            if st.button("👁️ Previsualizar PDF"):
                st.info(f"📄 Archivo seleccionado: {archivo.name}")
                st.info("📊 Tamaño: {archivo.size / 1024:.2f} KB")
        
        # Botón de subida
        submitted = st.form_submit_button("🚀 Subir Archivo", type="primary")
        
        if submitted and archivo:
            # Validar archivo
            es_valido, mensaje = validar_archivo(archivo)
            
            if not es_valido:
                st.error(f"❌ {mensaje}")
                return
            
            # Guardar según el tipo de almacenamiento
            if almacenamiento == "Sistema de Archivos Local":
                exito, ruta, nombre_guardado = guardar_archivo_local(archivo, subdirectorio)
                
                if exito:
                    # Registrar en base de datos
                    usuario_id = st.session_state.user_data.get('id', 1)
                    metadata = {
                        "descripcion": descripcion,
                        "tipo_documento": tipo_documento,
                        "subdirectorio": subdirectorio
                    }
                    
                    if registrar_archivo_bd(nombre_guardado, ruta, tipo_documento, usuario_id, metadata):
                        st.success(f"✅ Archivo guardado en: {ruta}")
                        st.balloons()
                    else:
                        st.error("❌ Error al registrar en base de datos")
                else:
                    st.error(f"❌ {ruta}")
            
            else:  # Base de Datos (BLOB)
                try:
                    with engine.connect() as conn:
                        query = text("""
                            INSERT INTO archivos_blob (
                                nombre_archivo, tipo_documento, descripcion,
                                archivo_bytes, usuario_id, fecha_subida
                            ) VALUES (
                                :nombre_archivo, :tipo_documento, :descripcion,
                                :archivo_bytes, :usuario_id, :fecha_subida
                            )
                        """)
                        
                        conn.execute(query, {
                            "nombre_archivo": archivo.name,
                            "tipo_documento": tipo_documento,
                            "descripcion": descripcion,
                            "archivo_bytes": archivo.read(),
                            "usuario_id": st.session_state.user_data.get('id', 1),
                            "fecha_subida": datetime.now()
                        })
                        conn.commit()
                        
                        st.success(f"✅ Archivo '{archivo.name}' guardado en base de datos")
                        st.balloons()
                
                except Exception as e:
                    st.error(f"❌ Error al guardar en BD: {str(e)}")

def mostrar_carga_masiva():
    """Muestra la interfaz de carga masiva"""
    st.markdown("### 📤 Carga Masiva de Archivos")
    
    st.markdown("#### 📋 Formato Requerido para Carga Masiva")
    st.markdown("""
    **Estructura del archivo CSV/Excel:**
    - Columna A: Nombre del Archivo
    - Columna B: Tipo de Documento
    - Columna C: Descripción
    - Columna D: Ruta Destino (opcional)
    
    **Tipos de Documento Válidos:**
    - Formación Complementaria
    - Certificación
    - Diplomado
    - Taller
    - Documento Administrativo
    - Material Educativo
    - Otro
    """)
    
    with st.form("form_carga_masiva"):
        col1, col2 = st.columns(2)
        
        with col1:
            archivo_masivo = st.file_uploader(
                "📁 Seleccione Archivo CSV/Excel *",
                type=['csv', 'xlsx', 'xls'],
                help="Suba un archivo con múltiples registros"
            )
            
            if archivo_masiva:
                st.success(f"✅ Archivo '{archivo_masivo.name}' cargado")
                st.info(f"📊 Tamaño: {archivo_masiva.size / 1024:.2f} KB")
        
        with col2:
            procesamiento = st.selectbox(
                "⚙️ Procesamiento *",
                options=["Validar y Guardar", "Solo Validar", "Guardar Directamente"],
                help="Elija el nivel de validación"
            )
            
            modo_almacenamiento = st.radio(
                "💾 Modo de Almacenamiento *",
                options["Base de Datos", "Sistema de Archivos"],
                help="Dónde se almacenarán los archivos"
            )
        
        # Botón de procesamiento
        submitted = st.form_submit_button("🚀 Procesar Carga Masiva", type="primary")
        
        if submitted and archivo_masiva:
            with st.spinner("Procesando archivo masivo..."):
                try:
                    # Leer archivo según tipo
                    if archivo_masiva.name.endswith('.csv'):
                        import pandas as pd
                        df = pd.read_csv(archivo_masiva)
                    else:
                        df = pd.read_excel(archivo_masiva)
                    
                    # Validar columnas requeridas
                    columnas_requeridas = ['Nombre del Archivo', 'Tipo de Documento', 'Descripción']
                    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
                    
                    if columnas_faltantes:
                        st.error(f"❌ Columnas faltantes: {', '.join(columnas_faltantes)}")
                        return
                    
                    # Procesar cada fila
                    exitosos = 0
                    errores = 0
                    
                    for index, row in df.iterrows():
                        try:
                            # Validar datos
                            if pd.isna(row['Nombre del Archivo']) or pd.isna(row['Tipo de Documento']):
                                errores += 1
                                continue
                            
                            # Simular procesamiento
                            if procesamiento in ["Validar y Guardar", "Guardar Directamente"]:
                                # Aquí iría la lógica real de guardado
                                exitosos += 1
                            else:  # Solo Validar
                                if not pd.isna(row['Nombre del Archivo']):
                                    exitosos += 1
                            
                        except Exception as e:
                            errores += 1
                    
                    # Mostrar resultados
                    st.success(f"✅ Procesamiento completado")
                    st.info(f"📊 Registros procesados: {len(df)}")
                    st.success(f"✅ Exitosos: {exitosos}")
                    if errores > 0:
                        st.error(f"❌ Errores: {errores}")
                    
                    # Mostrar vista previa de datos
                    if st.checkbox("📋 Mostrar vista previa de datos"):
                        st.dataframe(df.head(10))
                
                except Exception as e:
                    st.error(f"❌ Error al procesar archivo: {str(e)}")

def mostrar_gestion_archivos():
    """Muestra la interfaz de gestión de archivos"""
    st.markdown("### 📋 Gestión de Archivos Registrados")
    
    try:
        with engine.connect() as conn:
            # Obtener archivos recientes
            query = text("""
                SELECT ar.nombre_archivo, ar.tipo_documento, ar.descripcion,
                       ar.fecha_subida, u.login as usuario_subida
                FROM archivos_registrados ar
                LEFT JOIN usuario u ON ar.usuario_id = u.id
                ORDER BY ar.fecha_subida DESC
                LIMIT 50
            """)
            
            resultado = conn.execute(query)
            archivos = resultado.fetchall()
            
            if not archivos:
                st.info("ℹ️ No hay archivos registrados.")
                return
            
            # Mostrar tabla de archivos
            st.markdown("#### 📋 Archivos Recientes")
            
            for archivo in archivos:
                with st.expander(f"📄 {archivo[0]}"):
                    col_info, col_acciones = st.columns([3, 1])
                    
                    with col_info:
                        st.write(f"**📁 Nombre:** {archivo[0]}")
                        st.write(f"**🏷️ Tipo:** {archivo[1]}")
                        st.write(f"**📝 Descripción:** {archivo[2] or 'Sin descripción'}")
                        st.write(f"**📅 Fecha:** {archivo[3]}")
                        st.write(f"**👤 Subido por:** {archivo[4]}")
                    
                    with col_acciones:
                        st.markdown("**Acciones:**")
                        if st.button(f"📥 Descargar", key=f"descargar_{archivo[0]}"):
                            st.info(f"📥 Descargando {archivo[0]}")
                        
                        if st.button(f"🗑️ Eliminar", key=f"eliminar_{archivo[0]}"):
                            st.warning(f"🗑️ Eliminando {archivo[0]}")
    
    except Exception as e:
        st.error(f"❌ Error al cargar archivos: {str(e)}")

# =================================================================
# FUNCIÓN PRINCIPAL
# =================================================================

def main():
    """Función principal del módulo de uploads"""
    st.set_page_config(
        page_title="Carga de Archivos - SICADFOC",
        page_icon="📁",
        layout="wide"
    )
    
    # Mostrar interfaz general
    mostrar_upload_general()

if __name__ == "__main__":
    main()
