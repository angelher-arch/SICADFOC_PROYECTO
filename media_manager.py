#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
media_manager.py - Módulo para gestión de archivos multimedia
SICADFOC 2026 - Instituto Universitario Jesus Obrero
"""

import os
import shutil
from datetime import datetime
from typing import Optional, Dict, Any, List
import mimetypes

def ensure_media_directories():
    """Crea directorios necesarios para archivos multimedia"""
    directories = [
        'media',
        'media/certificaciones',
        'media/certificaciones/internos',
        'media/certificaciones/externos',
        'media/formacion',
        'media/estudiantes',
        'media/profesores',
        'media/documentos',
        'media/imagenes',
        'media/temp'
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def sanitize_filename(filename: str) -> str:
    """Sanitiza nombre de archivo para almacenamiento seguro"""
    import re
    # Eliminar caracteres peligrosos
    filename = re.sub(r'[<>:"/\\|?*]', '_', str(filename))
    # Reemplazar espacios con guiones bajos
    filename = re.sub(r'\s+', '_', filename)
    # Eliminar caracteres especiales excepto guiones y guiones bajos
    filename = re.sub(r'[^\w\-_.]', '', filename)
    # Limitar longitud
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    return filename

def get_file_type(filename: str) -> str:
    """Determina el tipo de archivo basado en extensión"""
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

def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
    """Valida si el tipo de archivo está permitido"""
    file_type = get_file_type(filename)
    return file_type in allowed_types

def save_uploaded_file(uploaded_file, target_directory: str, custom_name: Optional[str] = None) -> Dict[str, Any]:
    """Guarda archivo subido en el directorio especificado"""
    try:
        ensure_media_directories()
        
        if uploaded_file is None:
            return {'success': False, 'error': 'No se proporcionó archivo'}
        
        # Generar nombre de archivo
        if custom_name:
            filename = sanitize_filename(custom_name)
            ext = os.path.splitext(uploaded_file.name)[1]
            if not filename.endswith(ext):
                filename += ext
        else:
            filename = sanitize_filename(uploaded_file.name)
        
        # Agregar timestamp si el archivo ya existe
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        
        # Ruta completa
        filepath = os.path.join(target_directory, filename)
        
        # Guardar archivo
        with open(filepath, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        # Obtener información del archivo
        file_info = {
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'original_name': uploaded_file.name,
            'size': os.path.getsize(filepath),
            'type': get_file_type(filename),
            'mime_type': mimetypes.guess_type(filename)[0],
            'upload_time': datetime.now()
        }
        
        return file_info
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def save_certification_file(uploaded_file, cedula_estudiante: str, tipo: str = 'externo') -> Dict[str, Any]:
    """Guarda archivo de certificación asociado a un estudiante"""
    try:
        ensure_media_directories()
        
        # Determinar directorio según tipo
        if tipo == 'interno':
            target_dir = 'media/certificaciones/internos'
        else:
            target_dir = 'media/certificaciones/externos'
        
        # Generar nombre personalizado
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        custom_name = f"cert_{tipo}_{cedula_estudiante}_{timestamp}_{uploaded_file.name}"
        
        # Guardar archivo
        result = save_uploaded_file(uploaded_file, target_dir, custom_name)
        
        if result['success']:
            # Agregar información específica de certificación
            result.update({
                'cedula_estudiante': cedula_estudiante,
                'tipo_certificacion': tipo,
                'category': 'certificacion'
            })
        
        return result
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def save_formation_file(uploaded_file, id_formacion: str, tipo_archivo: str = 'material') -> Dict[str, Any]:
    """Guarda archivo de formación complementaria"""
    try:
        ensure_media_directories()
        
        target_dir = 'media/formacion'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        custom_name = f"{tipo_archivo}_{id_formacion}_{timestamp}_{uploaded_file.name}"
        
        result = save_uploaded_file(uploaded_file, target_dir, custom_name)
        
        if result['success']:
            result.update({
                'id_formacion': id_formacion,
                'tipo_archivo': tipo_archivo,
                'category': 'formacion'
            })
        
        return result
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def save_student_file(uploaded_file, cedula_estudiante: str, tipo_documento: str = 'general') -> Dict[str, Any]:
    """Guarda archivo de estudiante"""
    try:
        ensure_media_directories()
        
        target_dir = 'media/estudiantes'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        custom_name = f"{tipo_documento}_{cedula_estudiante}_{timestamp}_{uploaded_file.name}"
        
        result = save_uploaded_file(uploaded_file, target_dir, custom_name)
        
        if result['success']:
            result.update({
                'cedula_estudiante': cedula_estudiante,
                'tipo_documento': tipo_documento,
                'category': 'estudiante'
            })
        
        return result
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def delete_file(filepath: str) -> Dict[str, Any]:
    """Elimina un archivo del sistema"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return {'success': True, 'message': 'Archivo eliminado exitosamente'}
        else:
            return {'success': False, 'error': 'Archivo no encontrado'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_file_info(filepath: str) -> Dict[str, Any]:
    """Obtiene información de un archivo"""
    try:
        if not os.path.exists(filepath):
            return {'success': False, 'error': 'Archivo no encontrado'}
        
        stat = os.stat(filepath)
        
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

def list_files_in_directory(directory: str, pattern: str = "*") -> List[Dict[str, Any]]:
    """Lista archivos en un directorio con información"""
    try:
        ensure_media_directories()
        
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

def get_student_certifications(cedula_estudiante: str) -> List[Dict[str, Any]]:
    """Obtiene todos los certificados de un estudiante"""
    try:
        certificaciones = []
        
        # Certificados internos
        internos = list_files_in_directory('media/certificaciones/internos', f"*{cedula_estudiante}*")
        for cert in internos:
            cert['tipo'] = 'interno'
            certificaciones.append(cert)
        
        # Certificados externos
        externos = list_files_in_directory('media/certificaciones/externos', f"*{cedula_estudiante}*")
        for cert in externos:
            cert['tipo'] = 'externo'
            certificaciones.append(cert)
        
        # Ordenar por fecha
        certificaciones.sort(key=lambda x: x['modified_time'], reverse=True)
        
        return certificaciones
        
    except Exception as e:
        return []

def cleanup_temp_files(max_age_hours: int = 24) -> Dict[str, Any]:
    """Limpia archivos temporales antiguos"""
    try:
        temp_dir = 'media/temp'
        if not os.path.exists(temp_dir):
            return {'success': True, 'message': 'No hay directorio temporal', 'deleted_count': 0}
        
        current_time = datetime.now()
        deleted_count = 0
        
        for filename in os.listdir(temp_dir):
            filepath = os.path.join(temp_dir, filename)
            if os.path.isfile(filepath):
                # Verificar edad del archivo
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                age_hours = (current_time - file_time).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    os.remove(filepath)
                    deleted_count += 1
        
        return {
            'success': True,
            'message': f'Limpieza completada',
            'deleted_count': deleted_count
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def interfaz_media_manager():
    """Interfaz principal para gestión de archivos multimedia"""
    import streamlit as st
    
    st.title("Gestor de Archivos Multimedia")
    st.header("Sistema de Gestión de Archivos - SICADFOC 2026")
    
    # Tabs para diferentes tipos de gestión
    tab_upload, tab_browse, tab_certificaciones, tab_cleanup = st.tabs([
        "Subir Archivos", "Explorar Archivos", "Certificaciones", "Mantenimiento"
    ])
    
    with tab_upload:
        st.subheader("Subir Archivos")
        
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
                        if file_type == 'certificacion_externo' and cedula:
                            result = save_certification_file(uploaded_file, cedula, 'externo')
                        elif file_type == 'certificacion_interno' and cedula:
                            result = save_certification_file(uploaded_file, cedula, 'interno')
                        elif file_type == 'estudiante' and cedula:
                            result = save_student_file(uploaded_file, cedula)
                        else:
                            target_dir = 'media/documentos'
                            result = save_uploaded_file(uploaded_file, target_dir, custom_name)
                        
                        if result['success']:
                            st.success(f"Archivo subido exitosamente: {result['filename']}")
                            st.json(result)
                        else:
                            st.error(f"Error subiendo archivo: {result['error']}")
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
    
    with tab_certificaciones:
        st.subheader("Certificaciones por Estudiante")
        
        cedula = st.text_input("Cédula del Estudiante", placeholder="V-12345678")
        
        if st.button("Buscar Certificaciones") and cedula:
            certificaciones = get_student_certifications(cedula)
            
            if certificaciones:
                st.write(f"Se encontraron {len(certificaciones)} certificados:")
                
                for cert in certificaciones:
                    with st.expander(f"{cert['filename']} ({cert['tipo']})"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Tipo:** {cert['tipo']}")
                            st.write(f"**Tamaño:** {cert['size_mb']} MB")
                            st.write(f"**Fecha:** {cert['modified_time']}")
                        
                        with col2:
                            if cert['type'] == 'imagen':
                                st.image(cert['filepath'], width=100)
                            
                            # Botón de descarga
                            with open(cert['filepath'], 'rb') as f:
                                st.download_button(
                                    label="Descargar",
                                    data=f.read(),
                                    file_name=cert['filename'],
                                    mime=cert['mime_type'] or 'application/octet-stream'
                                )
            else:
                st.info("No se encontraron certificaciones para este estudiante")
    
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
                result = cleanup_temp_files(max_age)
                
                if result['success']:
                    st.success(f"{result['message']}: {result['deleted_count']} archivos eliminados")
                else:
                    st.error(f"Error en limpieza: {result['error']}")
        
        # Estadísticas del sistema
        st.subheader("Estadísticas del Sistema")
        
        stats = {}
        directories = ['media/certificaciones/internos', 'media/certificaciones/externos', 'media/formacion', 'media/estudiantes', 'media/documentos']
        
        for directory in directories:
            files = list_files_in_directory(directory)
            stats[directory] = len(files)
        
        st.write("**Cantidad de archivos por directorio:**")
        for directory, count in stats.items():
            st.write(f"- {directory}: {count} archivos")

if __name__ == "__main__":
    interfaz_media_manager()
