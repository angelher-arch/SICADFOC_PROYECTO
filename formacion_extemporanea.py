#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
formacion_extemporanea.py - Módulo de Formación Complementaria Extemporánea
SICADFOC 2026 - Instituto Universitario Jesus Obrero
Módulo para procesar certificados escaneados mediante OCR y persistencia de datos
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import re
import io
from PIL import Image
import base64

# IMPORTACIONES LOCALES AL MÓDULO
try:
    from seguridad import tiene_permiso, SeguridadFOC26
    from database import motor_central
    from styles import aplicar_estilos_sicad, crear_tabla_configuracion, texto_adaptativo
except ImportError as e:
    st.error(f"Error importando módulos locales: {e}")
    sys.exit(1)

# Importar y configurar OCR (solo cuando se accede al módulo)
OCR_AVAILABLE = False
TESSERACT_VERSION = None
TESSERACT_PATH = ""

def _configurar_tesseract_bajo_demanda():
    """Configurar Tesseract solo bajo demanda - optimización de rendimiento"""
    global OCR_AVAILABLE, TESSERACT_VERSION, TESSERACT_PATH
    
    # Si ya está configurado, no hacer nada
    if OCR_AVAILABLE:
        return
    
    try:
        import pytesseract
        import os
        
        # Configuración silenciosa para producción (sin mensajes en UI)
        try:
            TESSERACT_VERSION = pytesseract.get_tesseract_version()
            OCR_AVAILABLE = True
            # Solo log a consola para producción
            return
        except Exception:
            pass  # Continuar en silencio absoluto
        
        # Detectar sistema operativo y configurar ruta OCR automáticamente
        import platform
        sistema = platform.system()
        
        if sistema == 'Linux':
            # Docker/Render - usar ruta estándar de Linux
            rutas_posibles = [
                '/usr/bin/tesseract',  # Ruta estándar en Docker/Render
                '/usr/local/bin/tesseract'
            ]
        else:
            # Windows - usar rutas de Windows
            rutas_posibles = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Tesseract-OCR\tesseract.exe'
            ]
        
        for ruta in rutas_posibles:
            ruta_expandida = os.path.expandvars(ruta)
            if os.path.exists(ruta_expandida):
                try:
                    pytesseract.pytesseract.tesseract_cmd = ruta_expandida
                    TESSERACT_VERSION = pytesseract.get_tesseract_version()
                    OCR_AVAILABLE = True
                    TESSERACT_PATH = ruta_expandida
                    # Silenciar logs en producción
                    return
                except Exception:
                    continue
        
        # Silenciar mensajes de error en producción
        OCR_AVAILABLE = False
        
    except ImportError:
        OCR_AVAILABLE = False
    except Exception as e:
        OCR_AVAILABLE = False

# NO inicializar Tesseract al cargar módulo - solo bajo demanda
# _configurar_tesseract_bajo_demanda() se llamará solo cuando se necesite OCR

class MotorFormacionExtemporanea:
    """Motor para procesamiento de formación complementaria extemporánea"""
    
    def __init__(self):
        """Inicialización del motor"""
        self.motor = motor_central
    
    def extraer_datos_ocr(self, imagen: Image.Image) -> Dict[str, str]:
        """Extraer datos del certificado mediante OCR"""
        # Inicializar Tesseract solo bajo demanda
        _configurar_tesseract_bajo_demanda()
        
        if not OCR_AVAILABLE:
            return {
                'error': 'OCR no disponible',
                'nombre_taller': '',
                'nombre_estudiante': '',
                'duracion': '',
                'objetivo': '',
                'texto_completo': ''
            }
        
        try:
            # Configurar idioma español para Tesseract
            texto = pytesseract.image_to_string(imagen, lang='spa')
            
            # Extraer datos específicos usando expresiones regulares
            datos_extraidos = {
                'texto_completo': texto,
                'nombre_taller': self._extraer_nombre_taller(texto),
                'nombre_estudiante': self._extraer_nombre_estudiante(texto),
                'duracion': self._extraer_duracion(texto),
                'objetivo': self._extraer_objetivo(texto)
            }
            
            return datos_extraidos
            
        except Exception as e:
            return {
                'error': f'Error en OCR: {str(e)}',
                'nombre_taller': '',
                'nombre_estudiante': '',
                'duracion': '',
                'objetivo': '',
                'texto_completo': ''
            }
    
    def _extraer_nombre_taller(self, texto: str) -> str:
        """Extraer nombre del taller usando patrones comunes"""
        patrones = [
            r'(?:TALLER|CURSO|DIPLOMADO)[\s:]+([^\n]+)',
            r'Certificado de (?:aprobación|participación|cumplimiento)[\s:]+en[^\n]+([^\n]+)',
            r'Que (?:ha|ha participado|ha completado)[^\n]+([^\n]+)',
        ]
        
        for patron in patrones:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ''
    
    def _extraer_nombre_estudiante(self, texto: str) -> str:
        """Extraer nombre del estudiante"""
        patrones = [
            r'([A-Z][a-z]+ [A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'Nombre:[\s]+([A-Z][a-z]+ [A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'Participante:[\s]+([A-Z][a-z]+ [A-Z][a-z]+(?: [A-Z][a-z]+)*)',
        ]
        
        for patron in patrones:
            matches = re.findall(patron, texto)
            if matches:
                # Devolver el nombre más largo (probablemente el correcto)
                return max(matches, key=len)
        
        return ''
    
    def _extraer_duracion(self, texto: str) -> str:
        """Extraer duración del taller"""
        patrones = [
            r'(\d+)\s*horas?',
            r'duración[:\s]+(\d+)\s*horas?',
            r'(\d+)\s*hs\.?',
        ]
        
        for patron in patrones:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                return f"{match.group(1)} horas"
        
        return ''
    
    def _extraer_objetivo(self, texto: str) -> str:
        """Extraer objetivo del taller"""
        # Buscar párrafos que contengan palabras clave de objetivos
        lineas = texto.split('\n')
        objetivos = []
        
        palabras_clave = ['objetivo', 'propósito', 'finalidad', 'competencia', 'habilidad']
        
        for linea in lineas:
            if any(palabra in linea.lower() for palabra in palabras_clave):
                objetivos.append(linea.strip())
        
        # Si no se encuentra objetivo específico, devolver un resumen
        if not objetivos:
            # Tomar las primeras 2-3 líneas significativas
            lineas_significativas = [l.strip() for l in lineas if len(l.strip()) > 20][:3]
            return ' | '.join(lineas_significativas)
        
        return ' | '.join(objetivos)
    
    def guardar_certificado_extemporaneo(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Guardar certificado extemporáneo en base de datos"""
        try:
            # Preparar datos para inserción
            datos_db = {
                'nombre_taller': datos.get('nombre_taller', ''),
                'nombre_estudiante': datos.get('nombre_estudiante', ''),
                'duracion': datos.get('duracion', ''),
                'objetivo': datos.get('objetivo', ''),
                'texto_ocr': datos.get('texto_completo', ''),
                'imagen_certificado': datos.get('imagen_base64', ''),
                'fecha_procesamiento': datetime.now(),
                'cedula_usuario_procesador': st.session_state.get('user_cedula', ''),
                'estado': 'procesado'
            }
            
            # Usar motor central para guardar
            resultado = self.motor.operacion_crud_unificada('certificados_extemporaneos', 'CREATE', datos_db)
            
            return resultado
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error guardando certificado: {str(e)}'
            }
    
    def listar_certificados_extemporaneos(self) -> List[Dict[str, Any]]:
        """Listar certificados extemporáneos procesados"""
        try:
            resultado = self.motor.operacion_crud_unificada('certificados_extemporaneos', 'READ')
            
            if resultado.get('success'):
                return resultado.get('data', [])
            return []
            
        except Exception as e:
            st.error(f"Error listando certificados: {e}")
            return []

def formacion_extemporanea_main():
    """Función principal del módulo de formación complementaria extemporánea"""
    try:
        # Aplicar estilos dinámicos con contraste automático
        aplicar_estilos_sicad()
        
        st.markdown("## 📋 Formación Complementaria Extemporánea")
        st.markdown("---")
        
        # Verificar permisos
        rol_usuario = st.session_state.get('user_role', '')
        if not tiene_permiso(rol_usuario, 'Formación Complementaria', 'Crear'):
            st.warning("⚠️ No tienes permisos para procesar certificados extemporáneos")
            return
        
        motor_extemporaneo = MotorFormacionExtemporanea()
        
        # Tabs para diferentes funciones
        tab1, tab2 = st.tabs([
            "📤 Procesar Certificado", 
            "📋 Historial de Certificados"
        ])
        
        with tab1:
            procesar_certificado(motor_extemporaneo)
        
        with tab2:
            mostrar_historial_certificados(motor_extemporaneo)
        
    except Exception as e:
        st.error(f"Error en módulo de formación extemporánea: {e}")
        st.exception(e)

def procesar_certificado(motor: MotorFormacionExtemporanea):
    """Procesar un certificado escaneado"""
    st.markdown("### 📤 Subir y Procesar Certificado")
    
    # Subida de imagen
    st.markdown("#### 1. Subir Imagen del Certificado")
    archivo_subido = st.file_uploader(
        "Seleccione una imagen del certificado (JPG, PNG)",
        type=['jpg', 'jpeg', 'png'],
        help="Suba una imagen clara del certificado para procesamiento OCR"
    )
    
    if archivo_subido is not None:
        # Mostrar imagen subida
        imagen = Image.open(archivo_subido)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(imagen, caption="Certificado Subido", use_container_width=True)
        
        with col2:
            st.markdown("#### 2. Procesamiento OCR")
            
            if st.button("🔍 Extraer Datos con OCR", type="primary"):
                with st.spinner("Procesando imagen con OCR..."):
                    datos_extraidos = motor.extraer_datos_ocr(imagen)
                
                # Almacenar en session state
                st.session_state.datos_ocr = datos_extraidos
                st.session_state.imagen_procesada = imagen
                st.session_state.archivo_subido = archivo_subido
                
                if 'error' in datos_extraidos:
                    st.error(datos_extraidos['error'])
                else:
                    st.success("✅ Datos extraídos exitosamente")
                    st.rerun()
    
    # Mostrar datos extraídos si existen
    if 'datos_ocr' in st.session_state:
        datos = st.session_state.datos_ocr
        
        st.markdown("#### 3. Validar y Corregir Datos Extraídos")
        
        with st.form("form_validacion_datos"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre_taller = st.text_input(
                    "Nombre del Taller*",
                    value=datos.get('nombre_taller', ''),
                    help="Nombre del taller o curso"
                )
                
                nombre_estudiante = st.text_input(
                    "Nombre del Estudiante*",
                    value=datos.get('nombre_estudiante', ''),
                    help="Nombre completo del estudiante"
                )
            
            with col2:
                duracion = st.text_input(
                    "Duración*",
                    value=datos.get('duracion', ''),
                    help="Duración total del taller (ej: 40 horas)"
                )
                
                objetivo = st.text_area(
                    "Objetivo del Taller",
                    value=datos.get('objetivo', ''),
                    help="Objetivos o competencias desarrolladas"
                )
            
            # Mostrar texto OCR completo (opcional) con contraste dinámico
            with st.expander("📄 Ver texto OCR completo"):
                texto_ocr_html = f"""
                <div class="config-table">
                <p><strong>Texto completo extraído por OCR:</strong></p>
                <p>{datos.get('texto_completo', 'No se extrajo texto')}</p>
                </div>
                """
                st.markdown(texto_ocr_html, unsafe_allow_html=True)
            
            col_guardar, col_cancelar = st.columns(2)
            with col_guardar:
                guardar_button = st.form_submit_button("💾 Guardar Certificado", type="primary")
            with col_cancelar:
                cancelar_button = st.form_submit_button("❌ Cancelar")
            
            if cancelar_button:
                # Limpiar session state
                if 'datos_ocr' in st.session_state:
                    del st.session_state.datos_ocr
                if 'imagen_procesada' in st.session_state:
                    del st.session_state.imagen_procesada
                if 'archivo_subido' in st.session_state:
                    del st.session_state.archivo_subido
                st.rerun()
            
            if guardar_button:
                # Validar campos obligatorios
                if not all([nombre_taller, nombre_estudiante, duracion]):
                    st.error("⚠️ Los campos marcados con * son obligatorios")
                    return
                
                # Convertir imagen a base64 para almacenamiento
                imagen_base64 = ""
                if 'imagen_procesada' in st.session_state:
                    buffered = io.BytesIO()
                    st.session_state.imagen_procesada.save(buffered, format="PNG")
                    imagen_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                # Preparar datos para guardar
                datos_guardar = {
                    'nombre_taller': nombre_taller,
                    'nombre_estudiante': nombre_estudiante,
                    'duracion': duracion,
                    'objetivo': objetivo,
                    'texto_completo': datos.get('texto_completo', ''),
                    'imagen_base64': imagen_base64
                }
                
                # Guardar en base de datos
                with st.spinner("Guardando certificado..."):
                    resultado = motor.guardar_certificado_extemporaneo(datos_guardar)
                
                if resultado.get('success'):
                    st.success("✅ Certificado guardado exitosamente")
                    st.balloons()
                    
                    # Limpiar session state
                    if 'datos_ocr' in st.session_state:
                        del st.session_state.datos_ocr
                    if 'imagen_procesada' in st.session_state:
                        del st.session_state.imagen_procesada
                    if 'archivo_subido' in st.session_state:
                        del st.session_state.archivo_subido
                    
                    st.rerun()
                else:
                    st.error(f"❌ Error guardando certificado: {resultado.get('message', 'Error desconocido')}")

def mostrar_historial_certificados(motor: MotorFormacionExtemporanea):
    """Mostrar historial de certificados procesados"""
    st.markdown("### 📋 Historial de Certificados Procesados")
    
    with st.spinner("Cargando historial..."):
        certificados = motor.listar_certificados_extemporaneos()
    
    if not certificados:
        st.info("No se encontraron certificados procesados")
        return
    
    # Convertir a DataFrame para mejor visualización
    df = pd.DataFrame(certificados)
    
    # Seleccionar columnas a mostrar
    columnas_mostrar = [
        'id_certificado',
        'nombre_taller', 
        'nombre_estudiante',
        'duracion',
        'fecha_procesamiento',
        'estado'
    ]
    
    # Renombrar columnas para mejor visualización
    df_mostrar = df[columnas_mostrar].copy()
    df_mostrar.columns = [
        'ID',
        'Taller',
        'Estudiante',
        'Duración',
        'Fecha Procesamiento',
        'Estado'
    ]
    
    st.dataframe(df_mostrar, use_container_width=True)
    
    # Opciones de exportación
    st.markdown("### 📥 Opciones de Exportación")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Exportar a CSV"):
            csv = df_mostrar.to_csv(index=False)
            st.download_button(
                label="Descargar CSV",
                data=csv,
                file_name=f'certificados_extemporaneos_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv'
            )
    
    with col2:
        if st.button("🖼️ Ver Imágenes"):
            st.info("Función de visualización de imágenes en desarrollo")

# Alias de compatibilidad
def formacion_extemporanea():
    """Alias de compatibilidad para el orquestador principal"""
    formacion_extemporanea_main()
