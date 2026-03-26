# =================================================================
# FORMACIÓN COMPLEMENTARIA - SICADFOC 2026
# =================================================================

import streamlit as st
import pandas as pd
import io
from datetime import datetime
import os
from database import engine, get_engine_local
from sqlalchemy import text
import base64

# =================================================================
# FUNCIONES DE BASE DE DATOS
# =================================================================

def crear_tabla_documentos_pdf():
    """Crea la tabla documentos_pdf si no existe"""
    try:
        with engine.connect() as conn:
            # Verificar si la tabla existe
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='documentos_pdf'
            """))
            
            if not result.fetchone():
                # Crear tabla con todos los campos necesarios
                conn.execute(text("""
                    CREATE TABLE documentos_pdf (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre_curso VARCHAR(255) NOT NULL,
                        institucion VARCHAR(255) NOT NULL,
                        horas INTEGER NOT NULL,
                        fecha DATE NOT NULL,
                        categoria VARCHAR(50) NOT NULL,
                        archivo_path VARCHAR(500),
                        archivo_nombre VARCHAR(255),
                        archivo_bytes BLOB,
                        estudiante_id INTEGER,
                        facilitador_id INTEGER,
                        estado VARCHAR(50) DEFAULT 'Pendiente de Validación',
                        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        fecha_validacion TIMESTAMP,
                        validado_por VARCHAR(255),
                        FOREIGN KEY (estudiante_id) REFERENCES usuario(id),
                        FOREIGN KEY (facilitador_id) REFERENCES usuario(id)
                    )
                """))
                conn.commit()
                st.success("✅ Tabla documentos_pdf creada exitosamente")
        return True
    except Exception as e:
        st.error(f"❌ Error al crear tabla: {str(e)}")
        return False

def obtener_usuarios_por_rol(rol):
    """Obtiene usuarios filtrados por rol"""
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT id, login, email, nombre 
                FROM usuario 
                WHERE rol = :rol AND activo = 1
                ORDER BY nombre
            """)
            result = conn.execute(query, {"rol": rol})
            usuarios = result.fetchall()
            
            # Formatear para el combobox
            return [
                {
                    "id": user[0],
                    "display": f"{user[2]} ({user[1]})" if user[2] else user[1]
                }
                for user in usuarios
            ]
    except Exception as e:
        st.error(f"❌ Error al obtener usuarios: {str(e)}")
        return []

def guardar_documento_pdf(datos_formulario, archivo_bytes, archivo_nombre):
    """Guarda el documento PDF en la base de datos"""
    try:
        with engine.connect() as conn:
            query = text("""
                INSERT INTO documentos_pdf (
                    nombre_curso, institucion, horas, fecha, categoria,
                    archivo_path, archivo_nombre, archivo_bytes,
                    estudiante_id, facilitador_id, estado
                ) VALUES (
                    :nombre_curso, :institucion, :horas, :fecha, :categoria,
                    :archivo_path, :archivo_nombre, :archivo_bytes,
                    :estudiante_id, :facilitador_id, :estado
                )
            """)
            
            conn.execute(query, {
                "nombre_curso": datos_formulario["nombre_curso"],
                "institucion": datos_formulario["institucion"],
                "horas": datos_formulario["horas"],
                "fecha": datos_formulario["fecha"],
                "categoria": datos_formulario["categoria"],
                "archivo_path": datos_formulario.get("archivo_path", ""),
                "archivo_nombre": archivo_nombre,
                "archivo_bytes": archivo_bytes,
                "estudiante_id": datos_formulario["estudiante_id"],
                "facilitador_id": datos_formulario["facilitador_id"],
                "estado": "Pendiente de Validación"
            })
            conn.commit()
            return True
    except Exception as e:
        st.error(f"❌ Error al guardar documento: {str(e)}")
        return False

def obtener_documentos_pendientes():
    """Obtiene documentos pendientes de validación"""
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT d.id, d.nombre_curso, d.institucion, d.horas, d.fecha, d.categoria,
                       d.archivo_nombre, d.fecha_registro,
                       e_s.login as estudiante_login, e_s.nombre as estudiante_nombre,
                       f_s.login as facilitador_login, f_s.nombre as facilitador_nombre
                FROM documentos_pdf d
                LEFT JOIN usuario e_s ON d.estudiante_id = e_s.id
                LEFT JOIN usuario f_s ON d.facilitador_id = f_s.id
                WHERE d.estado = 'Pendiente de Validación'
                ORDER BY d.fecha_registro DESC
            """)
            result = conn.execute(query)
            return result.fetchall()
    except Exception as e:
        st.error(f"❌ Error al obtener documentos: {str(e)}")
        return []

def validar_documento(documento_id, usuario_validador):
    """Valida un documento pendiente"""
    try:
        with engine.connect() as conn:
            query = text("""
                UPDATE documentos_pdf 
                SET estado = 'Validado', 
                    fecha_validacion = CURRENT_TIMESTAMP,
                    validado_por = :validador
                WHERE id = :documento_id
            """)
            conn.execute(query, {
                "documento_id": documento_id,
                "validador": usuario_validador
            })
            conn.commit()
            return True
    except Exception as e:
        st.error(f"❌ Error al validar documento: {str(e)}")
        return False

# =================================================================
# FUNCIONES DE INTERFAZ
# =================================================================

def mostrar_preview_pdf(archivo_bytes, archivo_nombre):
    """Muestra una previsualización del PDF"""
    try:
        # Convertir bytes a base64 para mostrar
        base64_pdf = base64.b64encode(archivo_bytes).decode('utf-8')
        
        st.markdown(f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <h3>📄 Previsualización: {archivo_nombre}</h3>
            <iframe 
                src="data:application/pdf;base64,{base64_pdf}" 
                width="100%" 
                height="600px" 
                style="border: 1px solid #ccc;">
            </iframe>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón de descarga
        st.download_button(
            label="📥 Descargar PDF",
            data=archivo_bytes,
            file_name=archivo_nombre,
            mime="application/pdf"
        )
        
    except Exception as e:
        st.error(f"❌ Error al mostrar previsualización: {str(e)}")

def mostrar_formulario_ingreso():
    """Muestra el formulario principal de ingreso"""
    st.markdown("## 📚 Ingreso de Formación Complementaria")
    st.markdown("---")
    
    # Verificar que la tabla exista
    if not crear_tabla_documentos_pdf():
        st.error("❌ No se puede continuar sin la tabla de documentos")
        return
    
    # Verificar rol del usuario
    rol_usuario = st.session_state.get('rol', '').lower()
    if rol_usuario not in ['profesor', 'administrador']:
        st.warning("⚠️ Solo usuarios con rol de Profesor o Administrador pueden acceder a esta función.")
        return
    
    # Tabs principales
    tab_ingreso, tab_validacion = st.tabs(["📝 Ingreso de Documentos", "✅ Validación de Documentos"])
    
    with tab_ingreso:
        mostrar_formulario_carga()
    
    with tab_validacion:
        mostrar_validacion_documentos()

def mostrar_formulario_carga():
    """Muestra el formulario de carga de documentos"""
    st.markdown("### 📝 Formulario de Carga")
    
    with st.form("form_formacion_complementaria"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_curso = st.text_input(
                "📚 Nombre del Curso *",
                placeholder="Ej: Python Avanzado",
                help="Nombre completo del curso o diplomado"
            )
            
            institucion = st.text_input(
                "🏛️ Institución *",
                placeholder="Ej: IUJO",
                help="Nombre de la institución que emite el certificado"
            )
            
            horas = st.number_input(
                "⏰ Horas *",
                min_value=1,
                max_value=500,
                value=40,
                help="Número total de horas del curso"
            )
        
        with col2:
            fecha = st.date_input(
                "📅 Fecha *",
                help="Fecha de emisión o finalización del curso",
                value=datetime.now().date()
            )
            
            categoria = st.selectbox(
                "🏷️ Categoría *",
                options=["Curso", "Diplomado", "Taller"],
                help="Tipo de formación complementaria"
            )
        
        st.markdown("---")
        
        # Selección de usuarios
        col_est, col_fac = st.columns(2)
        
        with col_est:
            st.markdown("#### 👨‍🎓 Estudiante Beneficiario")
            
            # Obtener lista de estudiantes
            estudiantes = obtener_usuarios_por_rol('estudiante')
            
            if estudiantes:
                opciones_estudiantes = ["Seleccione un estudiante..."] + [
                    est["display"] for est in estudiantes
                ]
                
                estudiante_seleccionado = st.selectbox(
                    "🔍 Buscar Estudiante *",
                    options=opciones_estudiantes,
                    help="Escriba o seleccione al estudiante beneficiario"
                )
                
                # Obtener ID del estudiante seleccionado
                estudiante_id = None
                if estudiante_seleccionado != "Seleccione un estudiante...":
                    for est in estudiantes:
                        if est["display"] == estudiante_seleccionado:
                            estudiante_id = est["id"]
                            break
            else:
                st.warning("⚠️ No hay estudiantes registrados en el sistema")
                estudiante_id = None
        
        with col_fac:
            st.markdown("#### 👨‍🏫 Facilitador Responsable")
            
            # Obtener lista de profesores
            profesores = obtener_usuarios_por_rol('profesor')
            
            if profesores:
                opciones_profesores = ["Seleccione un facilitador..."] + [
                    prof["display"] for prof in profesores
                ]
                
                facilitador_seleccionado = st.selectbox(
                    "🔍 Buscar Facilitador *",
                    options=opciones_profesores,
                    help="Escriba o seleccione al facilitador responsable"
                )
                
                # Obtener ID del facilitador seleccionado
                facilitador_id = None
                if facilitador_seleccionado != "Seleccione un facilitador...":
                    for prof in profesores:
                        if prof["display"] == facilitador_seleccionado:
                            facilitador_id = prof["id"]
                            break
            else:
                st.warning("⚠️ No hay profesores registrados en el sistema")
                facilitador_id = None
        
        st.markdown("---")
        
        # Subida de archivo
        st.markdown("#### 📁 Archivo PDF")
        archivo_subido = st.file_uploader(
            "Seleccione el archivo PDF *",
            type=['pdf'],
            help="Suba el certificado o documento en formato PDF"
        )
        
        # Previsualización si hay archivo
        archivo_bytes = None
        archivo_nombre = None
        
        if archivo_subido:
            archivo_bytes = archivo_subido.read()
            archivo_nombre = archivo_subido.name
            
            st.success(f"✅ Archivo '{archivo_nombre}' cargado exitosamente")
            
            # Botón de previsualización
            if st.button("👁️ Previsualizar PDF", type="secondary"):
                mostrar_preview_pdf(archivo_bytes, archivo_nombre)
        
        # Botón de guardado
        submitted = st.form_submit_button("💾 Guardar Documento", type="primary")
        
        if submitted:
            # Validaciones
            errores = []
            
            if not nombre_curso:
                errores.append("Nombre del curso es obligatorio")
            if not institucion:
                errores.append("Institución es obligatoria")
            if not horas:
                errores.append("Horas son obligatorias")
            if not fecha:
                errores.append("Fecha es obligatoria")
            if not estudiante_id:
                errores.append("Debe seleccionar un estudiante")
            if not facilitador_id:
                errores.append("Debe seleccionar un facilitador")
            if not archivo_bytes:
                errores.append("Debe subir un archivo PDF")
            
            if errores:
                for error in errores:
                    st.error(f"❌ {error}")
            else:
                # Preparar datos para guardar
                datos_formulario = {
                    "nombre_curso": nombre_curso,
                    "institucion": institucion,
                    "horas": horas,
                    "fecha": fecha,
                    "categoria": categoria,
                    "estudiante_id": estudiante_id,
                    "facilitador_id": facilitador_id,
                    "archivo_path": f"/uploads/{archivo_nombre}" if archivo_nombre else ""
                }
                
                # Guardar en base de datos
                if guardar_documento_pdf(datos_formulario, archivo_bytes, archivo_nombre):
                    st.success("✅ Documento guardado exitosamente")
                    st.balloons()
                    
                    # Limpiar formulario
                    st.rerun()

def mostrar_validacion_documentos():
    """Muestra la interfaz de validación de documentos"""
    st.markdown("### ✅ Validación de Documentos")
    
    # Verificar rol para validación
    rol_usuario = st.session_state.get('rol', '').lower()
    if rol_usuario not in ['profesor', 'administrador']:
        st.warning("⚠️ Solo usuarios con rol de Profesor o Administrador pueden validar documentos.")
        return
    
    # Obtener documentos pendientes
    documentos_pendientes = obtener_documentos_pendientes()
    
    if not documentos_pendientes:
        st.info("ℹ️ No hay documentos pendientes de validación.")
        return
    
    st.markdown(f"#### 📋 Documentos Pendientes: {len(documentos_pendientes)}")
    
    # Mostrar cada documento
    for doc in documentos_pendientes:
        with st.expander(f"📄 {doc[1]} - {doc[2]}"):
            col_info, col_acciones = st.columns([3, 1])
            
            with col_info:
                st.write(f"**📚 Curso:** {doc[1]}")
                st.write(f"**🏛️ Institución:** {doc[2]}")
                st.write(f"**⏰ Horas:** {doc[3]}")
                st.write(f"**📅 Fecha:** {doc[4]}")
                st.write(f"**🏷️ Categoría:** {doc[5]}")
                st.write(f"**👨‍🎓 Estudiante:** {doc[9]} ({doc[8]})")
                st.write(f"**👨‍🏫 Facilitador:** {doc[11]} ({doc[10]})")
                st.write(f"**📁 Archivo:** {doc[6]}")
                st.write(f"**📅 Registro:** {doc[7]}")
            
            with col_acciones:
                st.markdown("**Acciones:**")
                
                if st.button(f"✅ Validar", key=f"validar_{doc[0]}", help="Validar este documento"):
                    usuario_actual = st.session_state.user_data.get('login', 'sistema')
                    
                    if validar_documento(doc[0], usuario_actual):
                        st.success(f"✅ Documento '{doc[1]}' validado exitosamente")
                        st.rerun()
                    else:
                        st.error(f"❌ Error al validar documento '{doc[1]}'")

# =================================================================
# FUNCIÓN PRINCIPAL
# =================================================================

def main():
    """Función principal del módulo de formación complementaria"""
    st.set_page_config(
        page_title="Formación Complementaria - SICADFOC",
        page_icon="📚",
        layout="wide"
    )
    
    # Verificar autenticación
    if not st.session_state.get('autenticado', False):
        st.error("❌ Debe iniciar sesión para acceder a esta función.")
        return
    
    # Mostrar formulario principal
    mostrar_formulario_ingreso()

if __name__ == "__main__":
    main()
