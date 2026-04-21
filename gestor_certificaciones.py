#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor de Certificaciones Unificado - SICADFOC 2026
Fusiona certificados internos (automáticos) y externos (cargados) en un solo módulo
"""

import streamlit as st
import os
import re
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

# Importaciones con lazy loading para evitar errores
def lazy_import(module_name, file_name=None):
    """Importación segura con manejo de errores"""
    try:
        if file_name:
            module = __import__(file_name, fromlist=[module_name])
            return getattr(module, module_name)
        else:
            return __import__(module_name)
    except ImportError:
        return None

def ensure_certificacion_directories():
    """Crea directorios necesarios para certificaciones"""
    directories = [
        'media/certificaciones',
        'media/certificaciones/internos',
        'media/certificaciones/externos',
        'media/certificaciones/qr'
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def sanitize_filename(filename):
    """Sanitiza nombre de archivo para almacenamiento seguro"""
    return re.sub(r'[^A-Za-z0-9_.-]', '_', str(filename))

class GestorCertificaciones:
    """Clase principal para gestión unificada de certificaciones"""
    
    def __init__(self):
        ensure_certificacion_directories()
        self.user_cedula = self.get_user_cedula()
        self.user_role = self.get_user_role()
    
    def get_user_cedula(self) -> str:
        """Obtiene cédula del usuario autenticado"""
        try:
            from seguridad import SeguridadFOC26
            return SeguridadFOC26.get_user_cedula() or ""
        except:
            return st.session_state.get('user', {}).get('cedula_usuario', '')
    
    def get_user_role(self) -> str:
        """Obtiene rol del usuario autenticado"""
        try:
            from seguridad import SeguridadFOC26
            if SeguridadFOC26.is_admin():
                return 'admin'
            elif SeguridadFOC26.is_profesor():
                return 'profesor'
            elif SeguridadFOC26.is_estudiante():
                return 'estudiante'
        except:
            return st.session_state.get('user', {}).get('rol', '').lower()
    
    def generar_certificado_interno(self, taller_info: Dict[str, Any]) -> Dict[str, Any]:
        """Genera certificado interno automáticamente cuando un taller se culmina"""
        try:
            # Generar ID único para certificado
            cert_id = f"CERT_{self.user_cedula}_{taller_info['id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Preparar datos para QR
            qr_data = {
                'cert_id': cert_id,
                'cedula_estudiante': self.user_cedula,
                'nombre_estudiante': st.session_state.get('user', {}).get('login_usuario', ''),
                'nombre_taller': taller_info['nombre'],
                'fecha_culminacion': taller_info['fecha_culminacion'],
                'duracion_horas': taller_info.get('duracion_horas', 0),
                'fecha_generacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Generar QR
            qr_path = self.generar_qr_certificado(qr_data)
            
            # Guardar registro en base de datos
            certificado_data = {
                'id': cert_id,
                'cedula_estudiante': self.user_cedula,
                'id_taller': taller_info['id'],
                'nombre_taller': taller_info['nombre'],
                'fecha_culminacion': taller_info['fecha_culminacion'],
                'qr_path': qr_path,
                'tipo': 'interno',
                'fecha_generacion': datetime.now(),
                'estado': 'activo'
            }
            
            # Usar transacciones para guardar
            self.guardar_certificado_db(certificado_data)
            
            return {
                'success': True,
                'cert_id': cert_id,
                'qr_path': qr_path,
                'message': 'Certificado interno generado exitosamente'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Error al generar certificado interno'
            }
    
    def generar_qr_certificado(self, qr_data: Dict[str, Any]) -> str:
        """Genera QR para certificado usando qr_generator.py"""
        try:
            # Intentar importar qr_generator
            qr_module = lazy_import('generar_qr_certificado', 'qr_generator')
            
            if qr_module:
                # Usar función del módulo si existe
                qr_content = f"CERTIFICADO ID: {qr_data['cert_id']}\n"
                qr_content += f"Estudiante: {qr_data['nombre_estudiante']}\n"
                qr_content += f"Cédula: {qr_data['cedula_estudiante']}\n"
                qr_content += f"Taller: {qr_data['nombre_taller']}\n"
                qr_content += f"Fecha: {qr_data['fecha_culminacion']}\n"
                qr_content += f"Generado: {qr_data['fecha_generacion']}"
                
                # Generar archivo QR
                qr_filename = f"qr_{qr_data['cert_id']}.png"
                qr_path = os.path.join('media/certificaciones/qr', qr_filename)
                
                # Llamar a la función del módulo
                return qr_module(qr_content, qr_path)
            else:
                # Implementación básica si no existe el módulo
                import qrcode
                qr_content = f"ID: {qr_data['cert_id']}"
                qr = qrcode.QRCode(box_size=10, border=2)
                qr.add_data(qr_content)
                qr.make(fit=True)
                img = qr.make_image(fill_color='black', back_color='white')
                
                qr_filename = f"qr_{qr_data['cert_id']}.png"
                qr_path = os.path.join('media/certificaciones/qr', qr_filename)
                img.save(qr_path)
                
                return qr_path
                
        except Exception as e:
            st.error(f"Error generando QR: {e}")
            return ""
    
    def guardar_certificado_db(self, certificado_data: Dict[str, Any]):
        """Guarda certificado en base de datos usando transacciones.py"""
        try:
            # Intentar usar transacciones
            trans_module = lazy_import('TransaccionFOC26', 'transacciones')
            
            if trans_module:
                # Usar la clase de transacciones si existe
                trans = trans_module()
                trans.insertar_certificacion(certificado_data)
            else:
                # Implementación directa si no existe el módulo
                from conexion_simple_corregido import ConexionSimple
                db = ConexionSimple()
                if db.conectar():
                    query = """
                    INSERT INTO certificaciones 
                    (id, cedula_estudiante, id_taller, nombre_taller, fecha_culminacion, qr_path, tipo, fecha_generacion, estado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    params = (
                        certificado_data['id'],
                        certificado_data['cedula_estudiante'],
                        certificado_data['id_taller'],
                        certificado_data['nombre_taller'],
                        certificado_data['fecha_culminacion'],
                        certificado_data['qr_path'],
                        certificado_data['tipo'],
                        certificado_data['fecha_generacion'],
                        certificado_data['estado']
                    )
                    db.ejecutar_consulta(query, params)
                    
        except Exception as e:
            st.error(f"Error guardando certificado en BD: {e}")
    
    def subir_certificado_externo(self, uploaded_file, descripcion: str = "") -> Dict[str, Any]:
        """Sube certificado externo usando media_manager.py"""
        try:
            if uploaded_file is None:
                return {'success': False, 'message': 'No se seleccionó archivo'}
            
            # Validar tipo de archivo
            allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
            if uploaded_file.type not in allowed_types:
                return {'success': False, 'message': 'Tipo de archivo no permitido'}
            
            # Generar nombre único
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"cert_externo_{self.user_cedula}_{timestamp}_{uploaded_file.name}"
            filename = sanitize_filename(filename)
            
            # Guardar archivo
            save_path = os.path.join('media/certificaciones/externos', filename)
            with open(save_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # Guardar registro en base de datos
            certificado_data = {
                'id': f"EXT_{self.user_cedula}_{timestamp}",
                'cedula_estudiante': self.user_cedula,
                'nombre_archivo': uploaded_file.name,
                'ruta_archivo': save_path,
                'descripcion': descripcion,
                'tipo': 'externo',
                'fecha_subida': datetime.now(),
                'estado': 'activo'
            }
            
            self.guardar_certificado_externo_db(certificado_data)
            
            return {
                'success': True,
                'filename': filename,
                'path': save_path,
                'message': 'Certificado externo subido exitosamente'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'message': 'Error al subir certificado externo'}
    
    def guardar_certificado_externo_db(self, certificado_data: Dict[str, Any]):
        """Guarda certificado externo en base de datos"""
        try:
            from conexion_simple_corregido import ConexionSimple
            db = ConexionSimple()
            if db.conectar():
                query = """
                INSERT INTO certificaciones_externos 
                (id, cedula_estudiante, nombre_archivo, ruta_archivo, descripcion, tipo, fecha_subida, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    certificado_data['id'],
                    certificado_data['cedula_estudiante'],
                    certificado_data['nombre_archivo'],
                    certificado_data['ruta_archivo'],
                    certificado_data['descripcion'],
                    certificado_data['tipo'],
                    certificado_data['fecha_subida'],
                    certificado_data['estado']
                )
                db.ejecutar_consulta(query, params)
                
        except Exception as e:
            st.error(f"Error guardando certificado externo en BD: {e}")
    
    def obtener_certificados_internos(self) -> List[Dict[str, Any]]:
        """Obtiene certificados internos del usuario actual"""
        try:
            from conexion_simple_corregido import ConexionSimple
            db = ConexionSimple()
            if db.conectar():
                query = """
                SELECT id, nombre_taller, fecha_culminacion, qr_path, fecha_generacion, estado
                FROM certificaciones 
                WHERE cedula_estudiante = %s AND tipo = 'interno'
                ORDER BY fecha_generacion DESC
                """
                result = db.ejecutar_consulta(query, (self.user_cedula,))
                return [dict(row) for row in result] if result else []
            return []
        except Exception as e:
            st.error(f"Error obteniendo certificados internos: {e}")
            return []
    
    def obtener_certificados_externos(self) -> List[Dict[str, Any]]:
        """Obtiene certificados externos del usuario actual"""
        try:
            from conexion_simple_corregido import ConexionSimple
            db = ConexionSimple()
            if db.conectar():
                query = """
                SELECT id, nombre_archivo, ruta_archivo, descripcion, fecha_subida, estado
                FROM certificaciones_externos 
                WHERE cedula_estudiante = %s AND tipo = 'externo'
                ORDER BY fecha_subida DESC
                """
                result = db.ejecutar_consulta(query, (self.user_cedula,))
                return [dict(row) for row in result] if result else []
            return []
        except Exception as e:
            st.error(f"Error obteniendo certificados externos: {e}")
            return []
    
    def validar_certificado(self, cert_id: str) -> Dict[str, Any]:
        """Valida un certificado por su ID"""
        try:
            from conexion_simple_corregido import ConexionSimple
            db = ConexionSimple()
            if db.conectar():
                # Buscar en certificados internos
                query = """
                SELECT id, cedula_estudiante, nombre_taller, fecha_culminacion, qr_path, tipo, fecha_generacion, estado
                FROM certificaciones 
                WHERE id = %s
                """
                result = db.ejecutar_consulta(query, (cert_id,))
                if result:
                    return {'success': True, 'certificado': dict(result[0]), 'tipo': 'interno'}
                
                # Buscar en certificados externos
                query = """
                SELECT id, cedula_estudiante, nombre_archivo, ruta_archivo, descripcion, tipo, fecha_subida, estado
                FROM certificaciones_externos 
                WHERE id = %s
                """
                result = db.ejecutar_consulta(query, (cert_id,))
                if result:
                    return {'success': True, 'certificado': dict(result[0]), 'tipo': 'externo'}
                
                return {'success': False, 'message': 'Certificado no encontrado'}
                
        except Exception as e:
            return {'success': False, 'error': str(e), 'message': 'Error validando certificado'}

def interfaz_certificados_internos(gestor: GestorCertificaciones):
    """Interfaz para certificados internos generados automáticamente"""
    st.subheader("Mis Certificaciones Internas")
    
    # Obtener certificados del usuario
    certificados = gestor.obtener_certificados_internos()
    
    if not certificados:
        st.info("No tienes certificados internos generados. Los certificados se generan automáticamente al culminar talleres.")
        return
    
    # Mostrar certificados
    for cert in certificados:
        with st.expander(f"Certificado: {cert['nombre_taller']} - {cert['fecha_culminacion']}"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**ID:** {cert['id']}")
                st.write(f"**Taller:** {cert['nombre_taller']}")
                st.write(f"**Fecha de Culminación:** {cert['fecha_culminacion']}")
                st.write(f"**Fecha de Generación:** {cert['fecha_generacion']}")
                st.write(f"**Estado:** {cert['estado']}")
            
            with col2:
                if cert['qr_path'] and os.path.exists(cert['qr_path']):
                    st.image(cert['qr_path'], caption="Código QR del Certificado", width=150)
                else:
                    st.warning("QR no disponible")
            
            with col3:
                if st.button(f"Validar", key=f"validate_int_{cert['id']}"):
                    validacion = gestor.validar_certificado(cert['id'])
                    if validacion['success']:
                        st.success("Certificado válido")
                    else:
                        st.error("Certificado no válido")

def interfaz_certificados_externos(gestor: GestorCertificaciones):
    """Interfaz para carga y gestión de certificados externos"""
    st.subheader("Carga de Certificados Externos")
    
    # Formulario de subida
    with st.expander("Subir Nuevo Certificado", expanded=True):
        with st.form("form_cert_externo"):
            uploaded_file = st.file_uploader(
                "Seleccionar archivo (PDF, JPG, PNG)",
                type=['pdf', 'jpg', 'jpeg', 'png'],
                help="Sube tus certificados externos para validarlos en el sistema"
            )
            
            descripcion = st.text_area(
                "Descripción (opcional)",
                placeholder="Describe el certificado que estás subiendo..."
            )
            
            submit_button = st.form_submit_button("Subir Certificado")
            
            if submit_button and uploaded_file:
                with st.spinner("Procesando certificado..."):
                    resultado = gestor.subir_certificado_externo(uploaded_file, descripcion)
                    
                    if resultado['success']:
                        st.success(resultado['message'])
                        st.rerun()
                    else:
                        st.error(f"Error: {resultado['message']}")
    
    # Mostrar certificados existentes
    st.subheader("Mis Certificados Externos")
    certificados = gestor.obtener_certificados_externos()
    
    if not certificados:
        st.info("No has subido certificados externos.")
        return
    
    # Mostrar certificados
    for cert in certificados:
        with st.expander(f"Certificado: {cert['nombre_archivo']} - {cert['fecha_subida']}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**ID:** {cert['id']}")
                st.write(f"**Nombre del Archivo:** {cert['nombre_archivo']}")
                st.write(f"**Descripción:** {cert['descripcion'] or 'Sin descripción'}")
                st.write(f"**Fecha de Subida:** {cert['fecha_subida']}")
                st.write(f"**Estado:** {cert['estado']}")
            
            with col2:
                # Botón para visualizar/validar
                if st.button(f"Visualizar", key=f"view_ext_{cert['id']}"):
                    if os.path.exists(cert['ruta_archivo']):
                        if cert['ruta_archivo'].endswith('.pdf'):
                            st.info("Para visualizar PDF, descarga el archivo:")
                            with open(cert['ruta_archivo'], 'rb') as f:
                                st.download_button(
                                    label="Descargar PDF",
                                    data=f.read(),
                                    file_name=cert['nombre_archivo'],
                                    mime='application/pdf'
                                )
                        else:
                            st.image(cert['ruta_archivo'], caption=cert['nombre_archivo'])
                    else:
                        st.error("Archivo no encontrado")
                
                # Botón de validación
                if st.button(f"Validar", key=f"validate_ext_{cert['id']}"):
                    validacion = gestor.validar_certificado(cert['id'])
                    if validacion['success']:
                        st.success("Certificado válido y registrado")
                    else:
                        st.error("Certificado no válido")

def gestor_certificaciones_unificado():
    """Función principal del gestor de certificaciones unificado"""
    try:
        # Verificar autenticación
        if 'autenticado' not in st.session_state or not st.session_state['autenticado']:
            st.error("Debes iniciar sesión para acceder a tus certificados.")
            st.stop()
        
        # Inicializar gestor
        gestor = GestorCertificaciones()
        
        # Título principal
        st.title("Certificaciones")
        st.header("Centro unificado de certificaciones")
        
        # Información del usuario
        user_info = st.session_state.get('user', {})
        st.info(f"Usuario: {user_info.get('login_usuario', 'N/A')} | Cédula: {gestor.user_cedula}")
        
        # Tabs para internos/externos/gestion
        tab_internos, tab_externos, tab_gestion = st.tabs([
            "Certificados Internos", 
            "Certificados Externos", 
            "Gestión de Archivos"
        ])
        
        with tab_internos:
            interfaz_certificados_internos(gestor)
        
        with tab_externos:
            interfaz_certificados_externos(gestor)
        
        with tab_gestion:
            interfaz_gestion_multimedia(gestor)
        
        # Sección de validación (fuera de tabs)
        st.markdown("---")
        st.subheader("Validación de Certificados")
        st.write("Ingresa el ID de un certificado para validar su autenticidad:")
        
        cert_id = st.text_input("ID del Certificado", placeholder="Ej: CERT_V12345678_1_20240420103000")
        
        if st.button("Validar Certificado"):
            if cert_id:
                with st.spinner("Validando certificado..."):
                    validacion = gestor.validar_certificado(cert_id)
                    
                    if validacion['success']:
                        st.success("Certificado válido y auténtico")
                        cert_data = validacion['certificado']
                        st.json(cert_data)
                    else:
                        st.error(f"Error: {validacion['message']}")
            else:
                st.warning("Por favor ingresa un ID de certificado")
        
        # Información adicional
        with st.expander("Información del Sistema", expanded=False):
            st.write("""
            **Tipos de Certificados:**
            - **Internos:** Generados automáticamente al culminar talleres del sistema
            - **Externos:** Documentos subidos por el usuario para validación
            
            **Proceso de Validación:**
            - Todos los certificados tienen un ID único
            - Los certificados internos incluyen código QR
            - Los certificados externos se validan contra la base de datos
            """)
            
    except Exception as e:
        st.error(f"Error en el gestor de certificaciones: {e}")
        st.exception(e)

def interfaz_gestion_multimedia(gestor: GestorCertificaciones):
    """Interfaz de gestión multimedia integrada en el módulo de certificaciones"""
    st.subheader("Gestión de Archivos Multimedia")
    
    # Tabs para diferentes tipos de gestión
    tab_upload, tab_browse, tab_cleanup = st.tabs([
        "Subir Archivos", "Explorar Archivos", "Mantenimiento"
    ])
    
    with tab_upload:
        st.subheader("Subir Archivos de Certificación")
        
        uploaded_file = st.file_uploader(
            "Seleccionar archivo",
            type=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'txt'],
            help="Selecciona un archivo para subir al sistema"
        )
        
        if uploaded_file:
            col1, col2 = st.columns(2)
            
            with col1:
                file_type = st.selectbox(
                    "Tipo de archivo",
                    ["certificacion_externo", "certificacion_interno", "formacion", "estudiante", "general"]
                )
                
                if file_type in ['certificacion_externo', 'certificacion_interno', 'estudiante']:
                    cedula = st.text_input("Cédula del Estudiante", placeholder="V-12345678")
                else:
                    cedula = ""
            
            with col2:
                custom_name = st.text_input(
                    "Nombre personalizado (opcional)",
                    placeholder="Deja en blanco para usar el nombre original"
                )
            
            if st.button("Subir Archivo"):
                if uploaded_file:
                    with st.spinner("Subiendo archivo..."):
                        # Usar funciones del gestor existente
                        if file_type == 'certificacion_externo' and cedula:
                            result = gestor.subir_certificado_externo(uploaded_file, custom_name or "Certificado externo")
                        elif file_type == 'certificacion_interno' and cedula:
                            # Para certificados internos, usar la función existente
                            result = gestor.subir_certificado_externo(uploaded_file, custom_name or "Certificado interno")
                        elif file_type == 'estudiante' and cedula:
                            # Implementar lógica para estudiantes
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            filename = f"estudiante_{cedula}_{timestamp}_{uploaded_file.name}"
                            filename = sanitize_filename(filename)
                            save_path = os.path.join('media/estudiantes', filename)
                            
                            with open(save_path, 'wb') as f:
                                f.write(uploaded_file.getbuffer())
                            
                            result = {
                                'success': True,
                                'filename': filename,
                                'filepath': save_path,
                                'message': 'Archivo de estudiante subido exitosamente'
                            }
                        else:
                            # Archivo general
                            target_dir = 'media/documentos'
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            if not custom_name:
                                filename = f"general_{timestamp}_{uploaded_file.name}"
                            else:
                                filename = f"{custom_name}_{timestamp}_{uploaded_file.name}"
                            filename = sanitize_filename(filename)
                            save_path = os.path.join(target_dir, filename)
                            
                            with open(save_path, 'wb') as f:
                                f.write(uploaded_file.getbuffer())
                            
                            result = {
                                'success': True,
                                'filename': filename,
                                'filepath': save_path,
                                'message': 'Archivo general subido exitosamente'
                            }
                        
                        if result['success']:
                            st.success(f"Archivo subido exitosamente: {result['filename']}")
                        else:
                            st.error(f"Error subiendo archivo: {result.get('error', 'Error desconocido')}")
                else:
                    st.warning("Por favor selecciona un archivo")
    
    with tab_browse:
        st.subheader("Explorar Archivos")
        
        directory = st.selectbox(
            "Seleccionar directorio",
            ["media/certificaciones/internos", "media/certificaciones/externos", "media/formacion", "media/estudiantes", "media/documentos"]
        )
        
        if st.button("Listar Archivos"):
            files = list_files_in_directory(directory)
            
            if files:
                st.write(f"Se encontraron {len(files)} archivos:")
                
                for file_info in files:
                    with st.expander(f"{file_info['filename']} ({file_info['size_mb']} MB)"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Ruta:** {file_info['filepath']}")
                            st.write(f"**Tipo:** {file_info['type']}")
                            st.write(f"**Tamaño:** {file_info['size_mb']} MB")
                            st.write(f"**Modificado:** {file_info['modified_time']}")
                        
                        with col2:
                            if file_info['type'] == 'imagen':
                                st.image(file_info['filepath'], width=100)
                            
                            # Botón de descarga
                            with open(file_info['filepath'], 'rb') as f:
                                st.download_button(
                                    label="Descargar",
                                    data=f.read(),
                                    file_name=file_info['filename'],
                                    mime=file_info['mime_type'] or 'application/octet-stream'
                                )
            else:
                st.info("No se encontraron archivos en este directorio")
    
    with tab_cleanup:
        st.subheader("Mantenimiento del Sistema")
        
        st.write("Limpieza de archivos temporales")
        
        max_age = st.number_input(
            "Edad máxima de archivos temporales (horas)",
            min_value=1,
            max_value=168,
            value=24
        )
        
        if st.button("Limpiar Archivos Temporales"):
            with st.spinner("Limpiando archivos temporales..."):
                temp_dir = 'media/temp'
                if os.path.exists(temp_dir):
                    current_time = datetime.now()
                    deleted_count = 0
                    
                    for filename in os.listdir(temp_dir):
                        filepath = os.path.join(temp_dir, filename)
                        if os.path.isfile(filepath):
                            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                            age_hours = (current_time - file_time).total_seconds() / 3600
                            
                            if age_hours > max_age:
                                os.remove(filepath)
                                deleted_count += 1
                    
                    st.success(f"Limpieza completada: {deleted_count} archivos eliminados")
                else:
                    st.info("No hay directorio temporal")
        
        # Estadísticas del sistema
        st.subheader("Estadísticas del Sistema")
        
        stats = {}
        directories = ['media/certificaciones/internos', 'media/certificaciones/externos', 'media/formacion', 'media/estudiantes', 'media/documentos']
        
        for directory in directories:
            if os.path.exists(directory):
                files = list_files_in_directory(directory)
                stats[directory] = len(files)
            else:
                stats[directory] = 0
        
        st.write("**Cantidad de archivos por directorio:**")
        for directory, count in stats.items():
            st.write(f"- {directory}: {count} archivos")

def list_files_in_directory(directory: str, pattern: str = "*") -> List[Dict[str, Any]]:
    """Lista archivos en un directorio con información"""
    try:
        ensure_certificacion_directories()
        
        if not os.path.exists(directory):
            return []
        
        files = []
        import glob
        
        for filepath in glob.glob(os.path.join(directory, pattern)):
            file_info = get_file_info(filepath)
            if file_info['success']:
                files.append(file_info)
        
        # Ordenar por fecha de modificación descendente
        files.sort(key=lambda x: x['modified_time'], reverse=True)
        
        return files
        
    except Exception as e:
        return []

def get_file_info(filepath: str) -> Dict[str, Any]:
    """Obtiene información de un archivo"""
    try:
        if not os.path.exists(filepath):
            return {'success': False, 'error': 'Archivo no encontrado'}
        
        stat = os.stat(filepath)
        import mimetypes
        
        return {
            'success': True,
            'filepath': filepath,
            'filename': os.path.basename(filepath),
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'type': get_file_type(filepath),
            'mime_type': mimetypes.guess_type(filepath)[0],
            'created_time': datetime.fromtimestamp(stat.st_ctime),
            'modified_time': datetime.fromtimestamp(stat.st_mtime),
            'exists': True
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_file_type(filename: str) -> str:
    """Determina el tipo de archivo basado en extensión"""
    import mimetypes
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type:
        if mime_type.startswith('image/'):
            return 'imagen'
        elif mime_type == 'application/pdf':
            return 'pdf'
        elif mime_type.startswith('text/'):
            return 'texto'
        elif mime_type.startswith('video/'):
            return 'video'
        elif mime_type.startswith('audio/'):
            return 'audio'
    return 'otro'

# Función para integración con formacion_complementaria.py
def detectar_y_generar_certificado(taller_info: Dict[str, Any], cedula_estudiante: str):
    """Función que se llama desde formacion_complementaria.py cuando un taller se culmina"""
    try:
        # Crear gestor temporal
        gestor = GestorCertificaciones()
        gestor.user_cedula = cedula_estudiante
        
        # Generar certificado interno
        resultado = gestor.generar_certificado_interno(taller_info)
        
        if resultado['success']:
            print(f"Certificado generado: {resultado['cert_id']}")
        else:
            print(f"Error generando certificado: {resultado['message']}")
            
    except Exception as e:
        print(f"Error en detección de certificado: {e}")

if __name__ == "__main__":
    gestor_certificaciones_unificado()
