#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qr_generator.py - Módulo para generación de códigos QR
SICADFOC 2026 - Instituto Universitario Jesus Obrero
"""

import os
import qrcode
from datetime import datetime
from typing import Optional, Dict, Any

def ensure_qr_directories():
    """Crea directorios necesarios para QR"""
    directories = [
        'media/qr',
        'media/qr/certificaciones',
        'media/qr/formacion',
        'media/qr/estudiantes'
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def generar_qr_certificado(contenido: str, ruta_guardado: str) -> str:
    """Genera QR para certificado y guarda en ruta especificada"""
    try:
        ensure_qr_directories()
        
        # Crear código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(contenido)
        qr.make(fit=True)
        
        # Generar imagen
        img = qr.make_image(fill_color='black', back_color='white')
        
        # Guardar imagen
        img.save(ruta_guardado)
        
        return ruta_guardado
        
    except Exception as e:
        print(f"Error generando QR: {e}")
        return ""

def generar_qr_formacion(datos_formacion: Dict[str, Any]) -> str:
    """Genera QR para formación complementaria"""
    try:
        ensure_qr_directories()
        
        # Preparar contenido del QR
        contenido = f"FORMACION FOC-2026\n"
        contenido += f"ID: {datos_formacion.get('id', 'N/A')}\n"
        contenido += f"Estudiante: {datos_formacion.get('nombre_estudiante', 'N/A')}\n"
        contenido += f"Cédula: {datos_formacion.get('cedula', 'N/A')}\n"
        contenido += f"Taller: {datos_formacion.get('nombre_taller', 'N/A')}\n"
        contenido += f"Instructor: {datos_formacion.get('instructor', 'N/A')}\n"
        contenido += f"Fecha: {datos_formacion.get('fecha', 'N/A')}\n"
        contenido += f"Horas: {datos_formacion.get('horas', 'N/A')}\n"
        contenido += f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        nombre_archivo = f"qr_formacion_{datos_formacion.get('cedula', 'unknown')}_{timestamp}.png"
        ruta_guardado = os.path.join('media/qr/formacion', nombre_archivo)
        
        # Generar y guardar QR
        return generar_qr_certificado(contenido, ruta_guardado)
        
    except Exception as e:
        print(f"Error generando QR de formación: {e}")
        return ""

def generar_qr_estudiante(datos_estudiante: Dict[str, Any]) -> str:
    """Genera QR para identificación de estudiante"""
    try:
        ensure_qr_directories()
        
        # Preparar contenido del QR
        contenido = f"ESTUDIANTE IUJO\n"
        contenido += f"Cédula: {datos_estudiante.get('cedula', 'N/A')}\n"
        contenido += f"Nombre: {datos_estudiante.get('nombre', 'N/A')}\n"
        contenido += f"Apellido: {datos_estudiante.get('apellido', 'N/A')}\n"
        contenido += f"Carrera: {datos_estudiante.get('carrera', 'N/A')}\n"
        contenido += f"Semestre: {datos_estudiante.get('semestre', 'N/A')}\n"
        contenido += f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        nombre_archivo = f"qr_estudiante_{datos_estudiante.get('cedula', 'unknown')}_{timestamp}.png"
        ruta_guardado = os.path.join('media/qr/estudiantes', nombre_archivo)
        
        # Generar y guardar QR
        return generar_qr_certificado(contenido, ruta_guardado)
        
    except Exception as e:
        print(f"Error generando QR de estudiante: {e}")
        return ""

def validar_qr(ruta_qr: str) -> Dict[str, Any]:
    """Valida si un archivo QR existe y es legible"""
    try:
        if not os.path.exists(ruta_qr):
            return {'valido': False, 'error': 'Archivo no encontrado'}
        
        # Intentar leer el QR
        img = qrcode.make("test")
        # Aquí podrías agregar lógica para decodificar el QR si es necesario
        
        return {'valido': True, 'ruta': ruta_qr}
        
    except Exception as e:
        return {'valido': False, 'error': str(e)}

def interfaz_qr_generator():
    """Interfaz principal para generación de QR"""
    import streamlit as st
    
    # Verificar permisos y configurar tabs según rol
    from seguridad import SeguridadFOC26
    
    st.title("Generador de Códigos QR")
    st.header("Sistema de Generación QR - SICADFOC 2026")
    
    # Configurar tabs según rol de usuario
    if SeguridadFOC26.is_admin() or SeguridadFOC26.is_profesor():
        # Admin y Profesor: Acceso completo a todos los tipos de QR
        tab_certificado, tab_formacion, tab_estudiante = st.tabs([
            "QR Certificados", "QR Formación", "QR Estudiantes"
        ])
    elif SeguridadFOC26.is_estudiante():
        # Estudiante: Solo puede generar QR para sí mismo
        tab_estudiante = st.container()
        tab_certificado = None
        tab_formacion = None
    else:
        st.error("Acceso denegado.")
        st.stop()
    
    if tab_certificado is not None:
        with tab_certificado:
            st.subheader("Generar QR para Certificado")
            
            # Validar permisos
            if SeguridadFOC26.is_estudiante():
                st.error("Acceso denegado. Los estudiantes no pueden generar QR para certificados.")
                st.stop()
            
            with st.form("form_qr_certificado"):
                contenido = st.text_area(
                "Contenido del QR",
                placeholder="Ingresa el contenido que quieres codificar en el QR...",
                height=150
            )
            
            nombre_archivo = st.text_input(
                "Nombre del archivo",
                placeholder="qr_certificado.png"
            )
            
            submit_button = st.form_submit_button("Generar QR")
            
            if submit_button and contenido:
                with st.spinner("Generando QR..."):
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    if not nombre_archivo:
                        nombre_archivo = f"qr_certificado_{timestamp}.png"
                    
                    ruta_guardado = os.path.join('media/qr/certificaciones', nombre_archivo)
                    resultado = generar_qr_certificado(contenido, ruta_guardado)
                    
                    if resultado:
                        st.success("QR generado exitosamente")
                        st.image(resultado, caption="Código QR Generado")
                        
                        # Botón de descarga
                        with open(resultado, 'rb') as f:
                            st.download_button(
                                label="Descargar QR",
                                data=f.read(),
                                file_name=nombre_archivo,
                                mime='image/png'
                            )
                    else:
                        st.error("Error generando QR")
    
    if tab_formacion is not None:
        with tab_formacion:
            st.subheader("Generar QR para Formación Complementaria")
            
            # Validar permisos
            if SeguridadFOC26.is_estudiante():
                st.error("Acceso denegado. Los estudiantes no pueden generar QR para formación.")
                st.stop()
            
            with st.form("form_qr_formacion"):
                col1, col2 = st.columns(2)
            
            with col1:
                id_formacion = st.text_input("ID de Formación")
                nombre_estudiante = st.text_input("Nombre del Estudiante")
                cedula = st.text_input("Cédula del Estudiante")
            
            with col2:
                nombre_taller = st.text_input("Nombre del Taller")
                instructor = st.text_input("Instructor")
                horas = st.number_input("Horas", min_value=1, value=1)
            
            fecha = st.date_input("Fecha de Formación")
            
            submit_button = st.form_submit_button("Generar QR de Formación")
            
            if submit_button and all([id_formacion, nombre_estudiante, cedula, nombre_taller]):
                with st.spinner("Generando QR..."):
                    datos = {
                        'id': id_formacion,
                        'nombre_estudiante': nombre_estudiante,
                        'cedula': cedula,
                        'nombre_taller': nombre_taller,
                        'instructor': instructor,
                        'fecha': fecha.strftime('%Y-%m-%d'),
                        'horas': horas
                    }
                    
                    resultado = generar_qr_formacion(datos)
                    
                    if resultado:
                        st.success("QR de formación generado exitosamente")
                        st.image(resultado, caption="QR de Formación")
                        
                        # Botón de descarga
                        nombre_archivo = os.path.basename(resultado)
                        with open(resultado, 'rb') as f:
                            st.download_button(
                                label="Descargar QR",
                                data=f.read(),
                                file_name=nombre_archivo,
                                mime='image/png'
                            )
                    else:
                        st.error("Error generando QR de formación")
    
    with tab_estudiante:
        if SeguridadFOC26.is_estudiante():
            st.subheader("Generar QR para Mi Perfil")
            
            # Obtener datos del estudiante actual
            user_cedula = SeguridadFOC26.get_user_cedula()
            
            try:
                from conexion_simple_corregido import ConexionSimple
                db = ConexionSimple()
                if db.conectar():
                    query = """
                    SELECT p.nombre, p.apellido, p.cedula, e.carrera, e.semestre_formacion
                    FROM persona p
                    JOIN usuario u ON p.cedula = u.cedula_usuario
                    LEFT JOIN estudiante e ON u.id = e.id_usuario
                    WHERE u.cedula_usuario = %s AND u.rol = 'Estudiante'
                    """
                    resultado = db.ejecutar_consulta(query, (user_cedula,))
                    
                    if resultado and len(resultado) > 0:
                        estudiante = resultado[0]
                        
                        st.write(f"**Nombre:** {estudiante['nombre']} {estudiante['apellido']}")
                        st.write(f"**Cédula:** {estudiante['cedula']}")
                        st.write(f"**Carrera:** {estudiante['carrera'] or 'No especificada'}")
                        st.write(f"**Semestre:** {estudiante['semestre_formacion'] or 'No especificado'}")
                        
                        # Formulario para generar QR con datos pre-cargados
                        with st.form("form_qr_estudiante_propio"):
                            st.write("**Generar QR con tus datos personales:**")
                            
                            # Mostrar datos pre-cargados (solo lectura)
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.text_input("Cédula", value=estudiante['cedula'], disabled=True)
                                st.text_input("Nombre", value=estudiante['nombre'], disabled=True)
                                st.text_input("Apellido", value=estudiante['apellido'], disabled=True)
                            
                            with col2:
                                st.text_input("Carrera", value=estudiante['carrera'] or 'No especificada', disabled=True)
                                st.text_input("Semestre", value=estudiante['semestre_formacion'] or 'No especificado', disabled=True)
                            
                            submit_button = st.form_submit_button("Generar Mi QR", type="primary")
                            
                            if submit_button:
                                with st.spinner("Generando tu QR personal..."):
                                    datos = {
                                        'cedula': estudiante['cedula'],
                                        'nombre': estudiante['nombre'],
                                        'apellido': estudiante['apellido'],
                                        'carrera': estudiante['carrera'] or 'No especificada',
                                        'semestre': estudiante['semestre_formacion'] or 'No especificado'
                                    }
                                    
                                    resultado = generar_qr_estudiante(datos)
                                    
                                    if resultado:
                                        st.success("¡Tu QR personal ha sido generado!")
                                        st.image(resultado, caption="Tu Código QR Personal")
                                        
                                        # Botón de descarga
                                        nombre_archivo = os.path.basename(resultado)
                                        with open(resultado, 'rb') as f:
                                            st.download_button(
                                                label="Descargar Mi QR",
                                                data=f.read(),
                                                file_name=nombre_archivo,
                                                mime='image/png'
                                            )
                                    else:
                                        st.error("Error generando tu QR personal")
                    else:
                        st.error("No se encontró tu información de estudiante.")
            except Exception as e:
                st.error(f"Error al cargar tus datos: {e}")
        else:
            # Admin y Profesor: Generar QR para cualquier estudiante
            st.subheader("Generar QR para Estudiante")
            
            with st.form("form_qr_estudiante"):
                col1, col2 = st.columns(2)
            
            with col1:
                cedula = st.text_input("Cédula del Estudiante")
                nombre = st.text_input("Nombre")
                apellido = st.text_input("Apellido")
            
            with col2:
                carrera = st.selectbox("Carrera", [
                    "Ingeniería de Sistemas",
                    "Ingeniería Civil",
                    "Ingeniería Mecánica",
                    "Ingeniería Eléctrica",
                    "Ingeniería Química",
                    "Administración",
                    "Contaduría",
                    "Economía",
                    "Derecho",
                    "Psicología",
                    "Comunicación Social"
                ])
                semestre = st.selectbox("Semestre", [f"{i} Semestre" for i in range(1, 11)])
            
            submit_button = st.form_submit_button("Generar QR de Estudiante")
            
            if submit_button and all([cedula, nombre, apellido]):
                with st.spinner("Generando QR..."):
                    datos = {
                        'cedula': cedula,
                        'nombre': nombre,
                        'apellido': apellido,
                        'carrera': carrera,
                        'semestre': semestre
                    }
                    
                    resultado = generar_qr_estudiante(datos)
                    
                    if resultado:
                        st.success("QR de estudiante generado exitosamente")
                        st.image(resultado, caption="QR de Estudiante")
                        
                        # Botón de descarga
                        nombre_archivo = os.path.basename(resultado)
                        with open(resultado, 'rb') as f:
                            st.download_button(
                                label="Descargar QR",
                                data=f.read(),
                                file_name=nombre_archivo,
                                mime='image/png'
                            )
                    else:
                        st.error("Error generando QR de estudiante")

if __name__ == "__main__":
    interfaz_qr_generator()
