#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
editor_certificados.py - Módulo de Editor de Certificados
SICADFOC 2026 - Instituto Universitario Jesus Obrero
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import date, datetime
from PIL import Image, ImageDraw, ImageFont
import io

# Importaciones del sistema
from database import execute_query
from seguridad import tiene_permiso, SeguridadFOC26

class EditorCertificados:
    """Clase principal para el editor de certificados"""
    
    def __init__(self):
        self.user_role = st.session_state.get('user_role', None)
        self.user_cedula = st.session_state.get('user_cedula', None)
        self.user_nombre = st.session_state.get('user_nombre', None)
    
    def editor_certificados_main(self):
        """Función principal del módulo de editor de certificados"""
        try:
            # Solo administradores pueden acceder al editor
            if not tiene_permiso(self.user_role, 'Certificados', 'Generar'):
                st.warning("El editor de certificados está disponible solo para administradores.")
                return
            
            st.header("🎨 Editor de Certificados")
            st.info("Configure y genere certificados para los talleres")
            
            # Tabs para diferentes funcionalidades
            tab1, tab2, tab3 = st.tabs(["⚙️ Configuración", "👁️ Previsualización", "📥 Generación"])
            
            with tab1:
                self.configuracion_plantillas()
            
            with tab2:
                self.previsualizacion_certificado()
            
            with tab3:
                self.generacion_certificados()
                
        except Exception as e:
            st.error(f"Error en editor de certificados: {e}")
    
    def configuracion_plantillas(self):
        """Configuración de plantillas de certificados"""
        try:
            st.markdown("#### Configuración de Plantillas")
            
            # Obtener configuración actual
            config_actual = self.obtener_configuracion_certificados()
            
            # Subida de imágenes
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Imagen Anverso**")
                anverso_file = st.file_uploader(
                    "Subir imagen anverso", 
                    type=['jpg', 'jpeg', 'png'],
                    key="anverso_upload"
                )
                
                if anverso_file:
                    # Guardar imagen
                    self.guardar_imagen_certificado(anverso_file, "anverso")
                    st.success("Imagen anverso subida exitosamente")
            
            with col2:
                st.markdown("**Imagen Reverso**")
                reverso_file = st.file_uploader(
                    "Subir imagen reverso", 
                    type=['jpg', 'jpeg', 'png'],
                    key="reverso_upload"
                )
                
                if reverso_file:
                    # Guardar imagen
                    self.guardar_imagen_certificado(reverso_file, "reverso")
                    st.success("Imagen reverso subida exitosamente")
            
            st.markdown("---")
            st.markdown("#### Posicionamiento de Elementos")
            
            # Configuración de posición y tamaño
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Anverso**")
                
                # Nombre Estudiante
                st.markdown("##### Nombre Estudiante")
                nombre_x = st.slider("Posición X", 0, 1000, config_actual.get('nombre_x', 100), key="nombre_x")
                nombre_y = st.slider("Posición Y", 0, 1000, config_actual.get('nombre_y', 200), key="nombre_y")
                nombre_tamano = st.slider("Tamaño Fuente", 10, 100, config_actual.get('nombre_tamano', 24), key="nombre_tamano")
                
                # Horas
                st.markdown("##### Horas")
                horas_x = st.slider("Posición X", 0, 1000, config_actual.get('horas_x', 100), key="horas_x")
                horas_y = st.slider("Posición Y", 0, 1000, config_actual.get('horas_y', 250), key="horas_y")
                horas_tamano = st.slider("Tamaño Fuente", 10, 100, config_actual.get('horas_tamano', 18), key="horas_tamano")
                
                # Tutor/Facilitador
                st.markdown("##### Tutor/Facilitador")
                tutor_x = st.slider("Posición X", 0, 1000, config_actual.get('tutor_x', 100), key="tutor_x")
                tutor_y = st.slider("Posición Y", 0, 1000, config_actual.get('tutor_y', 300), key="tutor_y")
                tutor_tamano = st.slider("Tamaño Fuente", 10, 100, config_actual.get('tutor_tamano', 18), key="tutor_tamano")
            
            with col2:
                st.markdown("**Reverso**")
                
                # Código Curso
                st.markdown("##### Código Curso")
                codigo_x = st.slider("Posición X", 0, 1000, config_actual.get('codigo_x', 100), key="codigo_x")
                codigo_y = st.slider("Posición Y", 0, 1000, config_actual.get('codigo_y', 150), key="codigo_y")
                codigo_tamano = st.slider("Tamaño Fuente", 10, 100, config_actual.get('codigo_tamano', 16), key="codigo_tamano")
                
                # Contenido
                st.markdown("##### Contenido")
                contenido_x = st.slider("Posición X", 0, 1000, config_actual.get('contenido_x', 100), key="contenido_x")
                contenido_y = st.slider("Posición Y", 0, 1000, config_actual.get('contenido_y', 200), key="contenido_y")
                contenido_tamano = st.slider("Tamaño Fuente", 10, 100, config_actual.get('contenido_tamano', 14), key="contenido_tamano")
                contenido_ancho = st.slider("Ancho Máximo", 100, 800, config_actual.get('contenido_ancho', 600), key="contenido_ancho")
            
            # Botón para guardar configuración
            if st.button("💾 Guardar Configuración", type="primary"):
                config = {
                    'nombre_x': nombre_x, 'nombre_y': nombre_y, 'nombre_tamano': nombre_tamano,
                    'horas_x': horas_x, 'horas_y': horas_y, 'horas_tamano': horas_tamano,
                    'tutor_x': tutor_x, 'tutor_y': tutor_y, 'tutor_tamano': tutor_tamano,
                    'codigo_x': codigo_x, 'codigo_y': codigo_y, 'codigo_tamano': codigo_tamano,
                    'contenido_x': contenido_x, 'contenido_y': contenido_y, 'contenido_tamano': contenido_tamano,
                    'contenido_ancho': contenido_ancho
                }
                self.guardar_configuracion_certificados(config)
                st.success("Configuración guardada exitosamente")
                st.rerun()
                
        except Exception as e:
            st.error(f"Error en configuración de plantillas: {e}")
    
    def previsualizacion_certificado(self):
        """Previsualización de certificados"""
        try:
            st.markdown("#### Previsualización de Certificado")
            
            # Obtener un taller de ejemplo
            query = """
            SELECT fc.*, COUNT(i.id_inscripcion) as inscritos,
                   p.nombre as estudiante_nombre, p.apellido as estudiante_apellido,
                   pr.nombre as profesor_nombre, pr.apellido as profesor_apellido
            FROM formacion_complementaria fc
            LEFT JOIN inscripcion i ON fc.id_formacion = i.id_formacion
            LEFT JOIN estudiante e ON fc.id_usuario = e.cedula_estudiante
            LEFT JOIN persona p ON e.cedula_estudiante = p.cedula
            LEFT JOIN usuarios u ON fc.id_usuario = u.cedula_usuario
            LEFT JOIN profesor pr ON fc.id_usuario = pr.cedula_profesor
            WHERE fc.fecha_creacion >= CURRENT_DATE - INTERVAL '1 year'
            LIMIT 1
            """
            
            resultado = execute_query(query, fetch_one=True)
            
            if not resultado:
                st.info("No hay talleres disponibles para previsualización")
                return
            
            # Datos de ejemplo
            datos_ejemplo = {
                'nombre': f"{resultado.get('estudiante_nombre', 'Juan')} {resultado.get('estudiante_apellido', 'Pérez')}",
                'horas': resultado.get('horas', 40),
                'tutor': f"{resultado.get('profesor_nombre', 'Dr. María')} {resultado.get('profesor_apellido', 'González')}",
                'codigo_curso': resultado.get('codigo_certificado', 'FC-2024-001'),
                'contenido': 'El participante ha completado satisfactoriamente el taller de formación complementaria, demostrando competencias y conocimientos adquiridos durante el proceso de formación.'
            }
            
            # Generar previsualización
            config = self.obtener_configuracion_certificados()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Anverso**")
                anverso_img = self.generar_certificado_anverso(datos_ejemplo, config)
                if anverso_img:
                    st.image(anverso_img, use_column_width=True)
            
            with col2:
                st.markdown("**Reverso**")
                reverso_img = self.generar_certificado_reverso(datos_ejemplo, config)
                if reverso_img:
                    st.image(reverso_img, use_column_width=True)
            
            # Mostrar configuración actual
            with st.expander("Configuración Actual"):
                st.json(config)
                
        except Exception as e:
            st.error(f"Error en previsualización: {e}")
    
    def generacion_certificados(self):
        """Generación de certificados para talleres"""
        try:
            st.markdown("#### Generación de Certificados")
            
            # Obtener talleres finalizados con inscritos
            query = """
            SELECT fc.*, COUNT(i.id_inscripcion) as inscritos
            FROM formacion_complementaria fc
            LEFT JOIN inscripcion i ON fc.id_formacion = i.id_formacion
            WHERE fc.fecha_fin < CURRENT_DATE - INTERVAL '7 days'
            GROUP BY fc.id_formacion
            HAVING COUNT(i.id_inscripcion) > 0
            ORDER BY fc.fecha_fin DESC
            """
            
            resultado = execute_query(query, fetch_all=True)
            
            if not resultado:
                st.info("No hay talleres finalizados con inscritos para generar certificados")
                return
            
            # Selector de taller
            opciones_talleres = [f"{t['nombre_taller']} ({t['inscritos']} inscritos)" for t in resultado]
            taller_seleccionado = st.selectbox("Seleccionar Taller", opciones_talleres)
            
            if taller_seleccionado:
                indice = opciones_talleres.index(taller_seleccionado)
                taller = resultado[indice]
                
                # Botón de generación
                if st.button("📥 Generar Certificados", type="primary", key="generar_certificados_taller"):
                    with st.spinner("Generando certificados..."):
                        self.generar_certificados_taller(taller['id_formacion'])
                    
                    st.success(f"Certificados generados para '{taller['nombre_taller']}'")
                    
        except Exception as e:
            st.error(f"Error en generación de certificados: {e}")
    
    def obtener_configuracion_certificados(self):
        """Obtiene la configuración actual de certificados"""
        try:
            query = "SELECT * FROM configuracion_certificados ORDER BY fecha_creacion DESC LIMIT 1"
            resultado = execute_query(query, fetch_one=True)
            
            if resultado:
                return {
                    'nombre_x': resultado.get('nombre_x', 100),
                    'nombre_y': resultado.get('nombre_y', 200),
                    'nombre_tamano': resultado.get('nombre_tamano', 24),
                    'horas_x': resultado.get('horas_x', 100),
                    'horas_y': resultado.get('horas_y', 250),
                    'horas_tamano': resultado.get('horas_tamano', 18),
                    'tutor_x': resultado.get('tutor_x', 100),
                    'tutor_y': resultado.get('tutor_y', 300),
                    'tutor_tamano': resultado.get('tutor_tamano', 18),
                    'codigo_x': resultado.get('codigo_x', 100),
                    'codigo_y': resultado.get('codigo_y', 150),
                    'codigo_tamano': resultado.get('codigo_tamano', 16),
                    'contenido_x': resultado.get('contenido_x', 100),
                    'contenido_y': resultado.get('contenido_y', 200),
                    'contenido_tamano': resultado.get('contenido_tamano', 14),
                    'contenido_ancho': resultado.get('contenido_ancho', 600)
                }
            else:
                # Valores por defecto
                return {
                    'nombre_x': 100, 'nombre_y': 200, 'nombre_tamano': 24,
                    'horas_x': 100, 'horas_y': 250, 'horas_tamano': 18,
                    'tutor_x': 100, 'tutor_y': 300, 'tutor_tamano': 18,
                    'codigo_x': 100, 'codigo_y': 150, 'codigo_tamano': 16,
                    'contenido_x': 100, 'contenido_y': 200, 'contenido_tamano': 14,
                    'contenido_ancho': 600
                }
        except Exception as e:
            st.error(f"Error obteniendo configuración: {e}")
            return {}
    
    def guardar_configuracion_certificados(self, config):
        """Guarda la configuración de certificados"""
        try:
            # Verificar si existe configuración
            query_check = "SELECT COUNT(*) as count FROM configuracion_certificados"
            resultado = execute_query(query_check, fetch_one=True)
            
            if resultado and resultado['count'] > 0:
                # Actualizar configuración existente
                query_update = """
                UPDATE configuracion_certificados SET
                    nombre_x = %s, nombre_y = %s, nombre_tamano = %s,
                    horas_x = %s, horas_y = %s, horas_tamano = %s,
                    tutor_x = %s, tutor_y = %s, tutor_tamano = %s,
                    codigo_x = %s, codigo_y = %s, codigo_tamano = %s,
                    contenido_x = %s, contenido_y = %s, contenido_tamano = %s, contenido_ancho = %s
                """
                params = (
                    config['nombre_x'], config['nombre_y'], config['nombre_tamano'],
                    config['horas_x'], config['horas_y'], config['horas_tamano'],
                    config['tutor_x'], config['tutor_y'], config['tutor_tamano'],
                    config['codigo_x'], config['codigo_y'], config['codigo_tamano'],
                    config['contenido_x'], config['contenido_y'], config['contenido_tamano'], config['contenido_ancho']
                )
                execute_query(query_update, params)
            else:
                # Insertar nueva configuración
                query_insert = """
                INSERT INTO configuracion_certificados (
                    nombre_x, nombre_y, nombre_tamano,
                    horas_x, horas_y, horas_tamano,
                    tutor_x, tutor_y, tutor_tamano,
                    codigo_x, codigo_y, codigo_tamano,
                    contenido_x, contenido_y, contenido_tamano, contenido_ancho
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    config['nombre_x'], config['nombre_y'], config['nombre_tamano'],
                    config['horas_x'], config['horas_y'], config['horas_tamano'],
                    config['tutor_x'], config['tutor_y'], config['tutor_tamano'],
                    config['codigo_x'], config['codigo_y'], config['codigo_tamano'],
                    config['contenido_x'], config['contenido_y'], config['contenido_tamano'], config['contenido_ancho']
                )
                execute_query(query_insert, params)
                
        except Exception as e:
            st.error(f"Error guardando configuración: {e}")
    
    def guardar_imagen_certificado(self, archivo, tipo):
        """Guardar imagen de certificado"""
        try:
            # Crear directorio assets si no existe
            if not os.path.exists('assets'):
                os.makedirs('assets')
            
            # Guardar archivo
            ruta = f'assets/certificado_{tipo}_actual.jpg'
            with open(ruta, 'wb') as f:
                f.write(archivo.getbuffer())
            
            return ruta
        except Exception as e:
            st.error(f"Error guardando imagen: {e}")
            return None
    
    def generar_certificado_anverso(self, datos, config):
        """Genera el anverso del certificado"""
        try:
            # Cargar imagen base
            ruta_anverso = 'assets/certificado_anverso_actual.jpg'
            if not os.path.exists(ruta_anverso):
                # Crear imagen base si no existe
                img = Image.new('RGB', (1200, 800), 'white')
                draw = ImageDraw.Draw(img)
                draw.rectangle([50, 50, 1150, 750], outline='black', width=2)
            else:
                img = Image.open(ruta_anverso)
                draw = ImageDraw.Draw(img)
            
            # Cargar fuentes
            try:
                font_nombre = ImageFont.truetype("arial.ttf", config.get('nombre_tamano', 24))
                font_horas = ImageFont.truetype("arial.ttf", config.get('horas_tamano', 18))
                font_tutor = ImageFont.truetype("arial.ttf", config.get('tutor_tamano', 18))
            except:
                font_nombre = ImageFont.load_default()
                font_horas = ImageFont.load_default()
                font_tutor = ImageFont.load_default()
            
            # Dibujar elementos
            draw.text(
                (config.get('nombre_x', 100), config.get('nombre_y', 200)),
                f"Certificamos que: {datos['nombre']}",
                fill='black',
                font=font_nombre
            )
            
            draw.text(
                (config.get('horas_x', 100), config.get('horas_y', 250)),
                f"Horas académicas: {datos['horas']}",
                fill='black',
                font=font_horas
            )
            
            draw.text(
                (config.get('tutor_x', 100), config.get('tutor_y', 300)),
                f"Tutor: {datos['tutor']}",
                fill='black',
                font=font_tutor
            )
            
            return img
            
        except Exception as e:
            st.error(f"Error generando anverso: {e}")
            return None
    
    def generar_certificado_reverso(self, datos, config):
        """Genera el reverso del certificado"""
        try:
            # Cargar imagen base
            ruta_reverso = 'assets/certificado_reverso_actual.jpg'
            if not os.path.exists(ruta_reverso):
                # Crear imagen base si no existe
                img = Image.new('RGB', (1200, 800), 'white')
                draw = ImageDraw.Draw(img)
                draw.rectangle([50, 50, 1150, 750], outline='black', width=2)
            else:
                img = Image.open(ruta_reverso)
                draw = ImageDraw.Draw(img)
            
            # Cargar fuentes
            try:
                font_codigo = ImageFont.truetype("arial.ttf", config.get('codigo_tamano', 16))
                font_contenido = ImageFont.truetype("arial.ttf", config.get('contenido_tamano', 14))
            except:
                font_codigo = ImageFont.load_default()
                font_contenido = ImageFont.load_default()
            
            # Dibujar código
            draw.text(
                (config.get('codigo_x', 100), config.get('codigo_y', 150)),
                datos['codigo_curso'],
                fill='black',
                font=font_codigo
            )
            
            # Dibujar contenido con ajuste automático
            texto_ajustado = self.ajustar_texto_caja(
                datos['contenido'], 
                config.get('contenido_ancho', 600),
                font_contenido
            )
            
            # Dibujar cada línea del contenido
            y_actual = config.get('contenido_y', 200)
            for linea in texto_ajustado:
                draw.text(
                    (config.get('contenido_x', 100), y_actual),
                    linea,
                    fill='black',
                    font=font_contenido
                )
                y_actual += 20
            
            return img
            
        except Exception as e:
            st.error(f"Error generando reverso: {e}")
            return None
    
    def ajustar_texto_caja(self, texto, ancho_maximo, fuente):
        """Ajusta texto a una caja de ancho máximo"""
        try:
            palabras = texto.split(' ')
            lineas = []
            linea_actual = []
            
            for palabra in palabras:
                # Probar agregar la palabra a la línea actual
                linea_con_palabra = ' '.join(linea_actual + [palabra])
                bbox = fuente.getbbox(linea_con_palabra)
                ancho_linea = bbox[2] - bbox[0]
                
                if ancho_linea <= ancho_maximo:
                    linea_actual.append(palabra)
                else:
                    # La palabra no cabe, empezar nueva línea
                    if linea_actual:
                        lineas.append(' '.join(linea_actual))
                    linea_actual = [palabra]
            
            # Agregar la última línea
            if linea_actual:
                lineas.append(' '.join(linea_actual))
            
            return lineas
            
        except Exception as e:
            st.error(f"Error ajustando texto: {e}")
            return [texto]
    
    def generar_certificados_taller(self, id_taller):
        """Genera certificados para todos los inscritos en un taller"""
        try:
            # Obtener datos del taller
            query_taller = """
            SELECT fc.*, p.nombre as profesor_nombre, p.apellido as profesor_apellido
            FROM formacion_complementaria fc
            LEFT JOIN profesor pr ON fc.id_usuario = pr.cedula_profesor
            LEFT JOIN persona p ON pr.cedula_profesor = p.cedula
            WHERE fc.id_formacion = %s
            """
            
            taller = execute_query(query_taller, (id_taller,), fetch_one=True)
            
            if not taller:
                st.error("Taller no encontrado")
                return
            
            # Obtener inscritos
            query_inscritos = """
            SELECT e.cedula_estudiante, p.nombre, p.apellido
            FROM inscripcion i
            INNER JOIN estudiante e ON i.cedula_estudiante = e.cedula_estudiante
            INNER JOIN persona p ON e.cedula_estudiante = p.cedula
            WHERE i.id_formacion = %s AND i.estado = 'Activa'
            """
            
            inscritos = execute_query(query_inscritos, (id_taller,), fetch_all=True)
            
            if not inscritos:
                st.info("No hay inscritos activos en este taller")
                return
            
            # Obtener configuración
            config = self.obtener_configuracion_certificados()
            
            # Generar certificados para cada inscrito
            certificados_generados = 0
            for inscrito in inscritos:
                datos = {
                    'nombre': f"{inscrito['nombre']} {inscrito['apellido']}",
                    'horas': taller['horas'],
                    'tutor': f"{taller.get('profesor_nombre', 'N/A')} {taller.get('profesor_apellido', '')}",
                    'codigo_curso': taller['codigo_certificado'],
                    'contenido': f"El participante ha completado satisfactoriamente el taller '{taller['nombre_taller']}', demostrando competencias y conocimientos adquiridos durante el proceso de formación."
                }
                
                # Generar anverso y reverso
                anverso = self.generar_certificado_anverso(datos, config)
                reverso = self.generar_certificado_reverso(datos, config)
                
                if anverso and reverso:
                    # Guardar certificado
                    nombre_archivo = f"certificado_{taller['codigo_certificado']}_{inscrito['cedula_estudiante']}"
                    
                    # Guardar imágenes
                    anverso.save(f"assets/{nombre_archivo}_anverso.jpg")
                    reverso.save(f"assets/{nombre_archivo}_reverso.jpg")
                    
                    # Registrar en base de datos
                    self.registrar_certificado(inscrito['cedula_estudiante'], id_taller, nombre_archivo)
                    
                    certificados_generados += 1
            
            st.success(f"Se generaron {certificados_generados} certificados")
            
        except Exception as e:
            st.error(f"Error generando certificados del taller: {e}")
    
    def registrar_certificado(self, cedula_estudiante, id_taller, nombre_archivo):
        """Registra un certificado en la base de datos"""
        try:
            query = """
            INSERT INTO certificado 
            (cedula_estudiante, id_formacion, nombre_archivo, fecha_generacion, generado_por)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s)
            ON CONFLICT (cedula_estudiante, id_formacion) 
            DO UPDATE SET 
                nombre_archivo = EXCLUDED.nombre_archivo,
                fecha_generacion = EXCLUDED.fecha_generacion,
                generado_por = EXCLUDED.generado_por
            """
            
            execute_query(query, (cedula_estudiante, id_taller, nombre_archivo, self.user_cedula))
            
        except Exception as e:
            st.error(f"Error registrando certificado: {e}")

# Función principal para compatibilidad con el orquestador
def editor_certificados_main():
    """Función principal del módulo de editor de certificados"""
    try:
        if not tiene_permiso(st.session_state.get('user_role'), 'Certificados', 'Generar'):
            st.warning("El editor de certificados está disponible solo para administradores.")
            return
        
        gestor = EditorCertificados()
        gestor.editor_certificados_main()
        
    except Exception as e:
        st.error(f"Error en el módulo de editor de certificados: {e}")

# Alias de compatibilidad
def gestion_formacion_complementaria():
    """Alias de compatibilidad para el orquestador principal"""
    editor_certificados_main()
