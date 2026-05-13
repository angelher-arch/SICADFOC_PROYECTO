#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inscripciones.py - Módulo Independiente de Gestión de Inscripciones
SICADFOC 2026 - Instituto Universitario Jesus Obrero
Módulo centralizado para inscripciones con integración cross-module
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Any
import logging

# CONFIGURACIÓN DE LOGGING
logger = logging.getLogger(__name__)

# IMPORTACIONES LOCALES AL MÓDULO - MOTOR CENTRAL UNIFICADO
try:
    from database import motor_central
    from seguridad import tiene_permiso
    from styles import aplicar_estilos_sicad, crear_tabla_configuracion, texto_adaptativo
except ImportError as e:
    st.error(f"Error importando módulos locales: {e}")
    sys.exit(1)

class MotorInscripciones:
    """Motor central de Inscripciones que consume MotorTransaccionalCentral"""
    
    def __init__(self):
        """Inicialización del motor central"""
        self.motor = motor_central
    
    # ========================================
    # CONSULTAS CROSS-MODULE - ESTUDIANTES
    # ========================================
    
    def obtener_datos_estudiante(self, cedula: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos completos del estudiante por cédula
        Retorna: Cédula, Correo, Carrera, Semestre, Nombre, Apellido
        """
        try:
            # Normalizar cédula - limpiar espacios y caracteres especiales
            cedula_normalizada = cedula.strip().upper()
            
            # Query simplificado - buscar directamente en persona primero
            query_persona = """
            SELECT cedula, nombre, apellido
            FROM persona
            WHERE cedula = %s
            LIMIT 1
            """
            
            resultado_persona = self.motor.ejecutar_consulta_personalizada(query_persona, (cedula_normalizada,))
            
            if resultado_persona.get('success') and resultado_persona.get('data'):
                data_persona = resultado_persona['data']
                
                # Si encontramos persona, buscar en usuarios y estudiante
                query_completa = """
                SELECT 
                    u.cedula_usuario,
                    u.email as email_estudiante,
                    p.nombre,
                    p.apellido,
                    e.id_carrera,
                    e.semestre_actual,
                    c.nombre_carrera,
                    e.estado_registro
                FROM usuarios u
                INNER JOIN persona p ON u.cedula_usuario = p.cedula
                LEFT JOIN estudiante e ON p.cedula = e.cedula_estudiante
                LEFT JOIN carrera c ON e.id_carrera = c.id_carrera
                WHERE u.cedula_usuario = %s AND u.rol = 'Estudiante' AND u.activo = true
                """
                
                resultado = self.motor.ejecutar_consulta_personalizada(query_completa, (cedula_normalizada,))
                
                if resultado.get('success') and resultado.get('data'):
                    data = resultado['data']
                    
                    if isinstance(data, list) and len(data) > 0:
                        estudiante_data = dict(data[0]) if not isinstance(data[0], dict) else data[0]
                        return estudiante_data
                    elif isinstance(data, dict):
                        return data
                else:
                    pass  # No se encontró estudiante activo
            else:
                pass  # Cédula no encontrada en tabla persona
            
            return None
            
        except Exception as e:
            st.error(f"Error consultando estudiante: {e}")
            return None
    
    def listar_estudiantes_activos(self) -> List[Dict[str, Any]]:
        """Lista todos los estudiantes activos para selector"""
        try:
            query = """
            SELECT 
                u.cedula_usuario,
                p.nombre,
                p.apellido,
                e.semestre_actual,
                c.nombre_carrera
            FROM usuarios u
            LEFT JOIN persona p ON u.cedula_usuario = p.cedula
            LEFT JOIN estudiante e ON p.cedula = e.cedula_estudiante
            LEFT JOIN carrera c ON e.id_carrera = c.id_carrera
            WHERE u.rol = 'Estudiante' AND u.activo = true AND e.estado_registro = 'Activo'
            ORDER BY p.apellido, p.nombre
            """
            
            resultado = self.motor.ejecutar_consulta_personalizada(query)
            
            if resultado.get('success') and resultado.get('data'):
                data = resultado['data']
                if isinstance(data, list):
                    return [dict(row) if not isinstance(row, dict) else row for row in data]
                elif isinstance(data, dict):
                    return [data]
            return []
            
        except Exception as e:
            st.error(f"Error listando estudiantes: {e}")
            return []
    
    # ========================================
    # CONSULTAS CROSS-MODULE - TALLERES
    # ========================================
    
    def obtener_talleres_disponibles(self) -> List[Dict[str, Any]]:
        """
        Obtiene talleres disponibles para inscripción
        Retorna: Nombre, Estado, Fecha Inicio, Facilitador, Código Certificado
        """
        try:
            query = """
            SELECT 
                fc.id_formacion,
                fc.nombre,
                fc.descripcion,
                fc.codigo_certificado,
                fc.horas,
                t.nombre_taller,
                t.fecha_inicio,
                t.fecha_fin,
                t.capacidad_maxima,
                t.estado as estado_taller,
                p.nombre as nombre_facilitador,
                p.apellido as apellido_facilitador,
                pr.especialidad
            FROM formacion_complementaria fc
            LEFT JOIN taller t ON fc.id_taller = t.id_taller
            LEFT JOIN profesor pr ON t.cedula_profesor = pr.cedula_profesor
            LEFT JOIN persona p ON pr.cedula_profesor = p.cedula
            WHERE t.estado = 'activo' 
            AND t.fecha_inicio >= CURRENT_DATE
            ORDER BY t.fecha_inicio ASC
            """
            
            resultado = self.motor.ejecutar_consulta_personalizada(query)
            
            if resultado.get('success') and resultado.get('data'):
                data = resultado['data']
                if isinstance(data, list):
                    return [dict(row) if not isinstance(row, dict) else row for row in data]
                elif isinstance(data, dict):
                    return [data]
            return []
            
        except Exception as e:
            st.error(f"Error consultando talleres disponibles: {e}")
            return []
    
    def obtener_datos_taller(self, id_formacion: int) -> Optional[Dict[str, Any]]:
        """Obtiene datos completos de un taller específico"""
        try:
            query = """
            SELECT 
                fc.id_formacion,
                fc.nombre,
                fc.descripcion,
                fc.codigo_certificado,
                fc.horas,
                t.nombre_taller,
                t.fecha_inicio,
                t.fecha_fin,
                t.capacidad_maxima,
                t.estado as estado_taller,
                p.nombre as nombre_facilitador,
                p.apellido as apellido_facilitador,
                pr.especialidad
            FROM formacion_complementaria fc
            LEFT JOIN taller t ON fc.id_taller = t.id_taller
            LEFT JOIN profesor pr ON t.cedula_profesor = pr.cedula_profesor
            LEFT JOIN persona p ON pr.cedula_profesor = p.cedula
            WHERE fc.id_formacion = %s
            """
            
            resultado = self.motor.ejecutar_consulta_personalizada(query, (id_formacion,))
            
            if resultado.get('success') and resultado.get('data'):
                data = resultado['data']
                if isinstance(data, list) and len(data) > 0:
                    return dict(data[0]) if not isinstance(data[0], dict) else data[0]
                elif isinstance(data, dict):
                    return data
            return None
            
        except Exception as e:
            st.error(f"Error consultando taller: {e}")
            return None
    
    # ========================================
    # GESTIÓN DE INSCRIPCIONES
    # ========================================
    
    def verificar_inscripcion_existente(self, cedula_estudiante: str, id_formacion: int) -> bool:
        """Verifica si el estudiante ya está inscrito en el taller"""
        try:
            query = """
            SELECT COUNT(*) as existe 
            FROM inscripcion 
            WHERE cedula_estudiante = %s AND id_formacion = %s
            AND estado IN ('inscrito', 'en_curso')
            """
            
            resultado = self.motor.ejecutar_consulta_personalizada(query, (cedula_estudiante, id_formacion))
            
            if resultado.get('success') and resultado.get('data'):
                data = resultado['data']
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get('existe', 0) > 0
                elif isinstance(data, dict):
                    return data.get('existe', 0) > 0
            return False
            
        except Exception as e:
            st.error(f"Error verificando inscripción existente: {e}")
            return False
    
    def contar_inscripciones_taller(self, id_formacion: int) -> int:
        """Cuenta cuántos estudiantes están inscritos en un taller"""
        try:
            query = """
            SELECT COUNT(*) as total_inscritos
            FROM inscripcion 
            WHERE id_formacion = %s 
            AND estado IN ('inscrito', 'en_curso')
            """
            
            resultado = self.motor.ejecutar_consulta_personalizada(query, (id_formacion,))
            
            if resultado.get('success') and resultado.get('data'):
                data = resultado['data']
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get('total_inscritos', 0)
                elif isinstance(data, dict):
                    return data.get('total_inscritos', 0)
            return 0
            
        except Exception as e:
            st.error(f"Error contando inscripciones: {e}")
            return 0
    
    def crear_inscripcion(self, cedula_estudiante: str, id_formacion: int, observaciones: str = None) -> Dict[str, Any]:
        """
        Crea una nueva inscripción con validaciones completas
        Retorna: dict con éxito/error y mensaje
        """
        try:
            # 1. Verificar que el estudiante exista y esté activo
            estudiante = self.obtener_datos_estudiante(cedula_estudiante)
            if not estudiante:
                return {
                    'exito': False,
                    'mensaje': f'Estudiante con cédula {cedula_estudiante} no encontrado o inactivo'
                }
            
            # 2. Verificar que el taller exista y esté disponible
            taller = self.obtener_datos_taller(id_formacion)
            if not taller:
                return {
                    'exito': False,
                    'mensaje': f'Taller con ID {id_formacion} no encontrado o no disponible'
                }
            
            # 3. Verificar inscripción duplicada
            if self.verificar_inscripcion_existente(cedula_estudiante, id_formacion):
                return {
                    'exito': False,
                    'mensaje': f'El estudiante ya está inscrito en este taller'
                }
            
            # 4. Verificar capacidad del taller
            inscritos_actuales = self.contar_inscripciones_taller(id_formacion)
            capacidad_maxima = taller.get('capacidad_maxima', 30)
            
            if inscritos_actuales >= capacidad_maxima:
                return {
                    'exito': False,
                    'mensaje': f'Taller lleno. Capacidad máxima: {capacidad_maxima}, Inscritos: {inscritos_actuales}'
                }
            
            # 5. Crear inscripción
            datos_inscripcion = {
                'cedula_estudiante': cedula_estudiante,
                'id_formacion': id_formacion,
                'observaciones': observaciones or f'Inscripción automática - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                'estado': 'inscrito'
            }
            
            resultado = self.motor.operacion_crud_unificada('inscripcion', 'CREATE', datos_inscripcion)
            
            if resultado.get('exito', False):
                return {
                    'exito': True,
                    'mensaje': f'Inscripción exitosa para {estudiante["nombre"]} {estudiante["apellido"]} en el taller "{taller["nombre"]}"',
                    'datos': {
                        'estudiante': estudiante,
                        'taller': taller,
                        'inscripcion_id': resultado.get('id_generado')
                    }
                }
            else:
                return {
                    'exito': False,
                    'mensaje': f'Error al crear inscripción: {resultado.get("mensaje", "Error desconocido")}'
                }
                
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error en proceso de inscripción: {str(e)}'
            }
    
    def listar_inscripciones_estudiante(self, cedula_estudiante: str) -> List[Dict[str, Any]]:
        """Lista todas las inscripciones de un estudiante"""
        try:
            query = """
            SELECT 
                i.id_inscripcion,
                i.fecha_inscripcion,
                i.estado,
                i.calificacion,
                i.observaciones,
                fc.nombre as nombre_taller,
                fc.codigo_certificado,
                t.fecha_inicio,
                t.fecha_fin,
                p.nombre as nombre_facilitador,
                p.apellido as apellido_facilitador
            FROM inscripcion i
            LEFT JOIN formacion_complementaria fc ON i.id_formacion = fc.id_formacion
            LEFT JOIN taller t ON fc.id_taller = t.id_taller
            LEFT JOIN profesor pr ON t.cedula_profesor = pr.cedula_profesor
            LEFT JOIN persona p ON pr.cedula_profesor = p.cedula
            WHERE i.cedula_estudiante = %s
            ORDER BY i.fecha_inscripcion DESC
            """
            
            resultado = self.motor.ejecutar_consulta_personalizada(query, (cedula_estudiante,))
            
            if resultado.get('success') and resultado.get('data'):
                data = resultado['data']
                if isinstance(data, list):
                    return [dict(row) if not isinstance(row, dict) else row for row in data]
                elif isinstance(data, dict):
                    return [data]
            return []
            
        except Exception as e:
            st.error(f"Error listando inscripciones del estudiante: {e}")
            return []
    
    def listar_inscripciones_taller(self, id_formacion: int) -> List[Dict[str, Any]]:
        """Lista todos los estudiantes inscritos en un taller"""
        try:
            query = """
            SELECT 
                i.id_inscripcion,
                i.fecha_inscripcion,
                i.estado,
                i.calificacion,
                i.observaciones,
                p.nombre,
                p.apellido,
                p.cedula,
                u.email,
                e.semestre_actual,
                c.nombre_carrera
            FROM inscripcion i
            LEFT JOIN estudiante e ON i.cedula_estudiante = e.cedula_estudiante
            LEFT JOIN persona p ON i.cedula_estudiante = p.cedula
            LEFT JOIN usuarios u ON p.cedula = u.cedula_usuario
            LEFT JOIN carrera c ON e.id_carrera = c.id_carrera
            WHERE i.id_formacion = %s
            ORDER BY p.apellido, p.nombre
            """
            
            resultado = self.motor.ejecutar_consulta_personalizada(query, (id_formacion,))
            
            if resultado.get('success') and resultado.get('data'):
                data = resultado['data']
                if isinstance(data, list):
                    return [dict(row) if not isinstance(row, dict) else row for row in data]
                elif isinstance(data, dict):
                    return [data]
            return []
            
        except Exception as e:
            st.error(f"Error listando inscripciones del taller: {e}")
            return []

# ========================================
# INTERFAZ DE USUARIO STREAMLIT
# ========================================

def mostrar_formulario_inscripcion():
    """Formulario dinámico de gestión académica con búsqueda reactiva por cédula"""
    
    st.markdown("## 📝 Formulario de Gestión Académica")
    
    # Aplicar estilos dinámicos con contraste automático
    aplicar_estilos_sicad()
    
    st.markdown("---")
    
    motor_inscripciones = MotorInscripciones()
    
    # Estado para controlar el flujo
    if 'cedula_ingresada' not in st.session_state:
        st.session_state.cedula_ingresada = ''
    if 'estudiante_validado' not in st.session_state:
        st.session_state.estudiante_validado = None
    if 'taller_seleccionado' not in st.session_state:
        st.session_state.taller_seleccionado = None
    
    # Paso 1: Búsqueda por cédula
    st.markdown("### 🔍 Búsqueda de Estudiante")
    
    cedula_input = st.text_input(
        "Ingrese la Cédula del Estudiante:",
        value=st.session_state.cedula_ingresada,
        key="cedula_input",
        placeholder="Ej: V-12345678"
    )
    
    # Actualizar estado cuando se ingresa cédula
    if cedula_input != st.session_state.cedula_ingresada:
        st.session_state.cedula_ingresada = cedula_input
        st.session_state.estudiante_validado = None
        st.session_state.taller_seleccionado = None
        st.rerun()
    
    # Validar estudiante cuando se ingresa cédula
    if cedula_input and not st.session_state.estudiante_validado:
        with st.spinner("Validando estudiante..."):
            datos_estudiante = motor_inscripciones.obtener_datos_estudiante(cedula_input)
            
            if datos_estudiante:
                st.session_state.estudiante_validado = datos_estudiante
                st.success(f"✅ Estudiante encontrado: {datos_estudiante['nombre']} {datos_estudiante['apellido']}")
                st.rerun()
            else:
                st.warning("⚠️ Estudiante no encontrado. Debe registrarse primero en el módulo de Gestión Estudiantil.")
                return
    
    # Mostrar datos del estudiante si está validado
    if st.session_state.estudiante_validado:
        estudiante = st.session_state.estudiante_validado
        
        st.markdown("### 👤 Datos del Estudiante (Solo Lectura)")
        
        with st.container():
            st.markdown('<div class="transparent-container">', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Cédula:", value=estudiante['cedula_usuario'], disabled=True)
                st.text_input("Nombre:", value=f"{estudiante['nombre']} {estudiante['apellido']}", disabled=True)
                st.text_input("Carrera:", value=estudiante.get('nombre_carrera', 'N/A'), disabled=True)
            
            with col2:
                st.text_input("Semestre:", value=str(estudiante.get('semestre_actual', 'N/A')), disabled=True)
                st.text_input("Email:", value=estudiante.get('email_estudiante', 'N/A'), disabled=True)
                st.text_input("Estado:", value=estudiante.get('estado_registro', 'N/A'), disabled=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📚 Selección de Taller")
        
        # Obtener talleres disponibles
        talleres = motor_inscripciones.obtener_talleres_disponibles()
        
        if not talleres:
            st.warning("No hay talleres disponibles para inscripción")
            return
        
        # Selector de taller
        opciones_talleres = [f"{t['id_formacion']} - {t['nombre']} (Inicio: {t.get('fecha_inicio', 'N/D')})" for t in talleres]
        indice_taller = st.selectbox(
            "Seleccione un taller:",
            opciones_talleres,
            key="selector_taller"
        )
        
        if indice_taller:
            taller_seleccionado = talleres[opciones_talleres.index(indice_taller)]
            id_formacion = taller_seleccionado['id_formacion']
            
            # Actualizar estado del taller seleccionado
            st.session_state.taller_seleccionado = taller_seleccionado
            
            # Obtener datos completos del taller
            datos_taller = motor_inscripciones.obtener_datos_taller(id_formacion)
            
            if datos_taller:
                st.markdown("### 📋 Datos del Taller (Solo Lectura)")
                
                with st.container():
                    st.markdown('<div class="transparent-container">', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text_input("Nombre del Taller:", value=datos_taller['nombre'], disabled=True)
                        st.text_input("Facilitador:", value=f"{datos_taller.get('nombre_facilitador', '')} {datos_taller.get('apellido_facilitador', '')}".strip(), disabled=True)
                        st.text_input("Especialidad:", value=datos_taller.get('especialidad', 'N/A'), disabled=True)
                    
                    with col2:
                        st.text_input("Fecha de Inicio:", value=str(datos_taller.get('fecha_inicio', 'N/A')), disabled=True)
                        st.text_input("Fecha de Fin:", value=str(datos_taller.get('fecha_fin', 'N/A')), disabled=True)
                        st.text_input("Código Certificado:", value=datos_taller.get('codigo_certificado', 'N/A'), disabled=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Mostrar capacidad e inscritos actuales
                inscritos_actuales = motor_inscripciones.contar_inscripciones_taller(id_formacion)
                capacidad_maxima = datos_taller.get('capacidad_maxima', 30)
                
                st.markdown(f"**👥 Cupos Disponibles:** {capacidad_maxima - inscritos_actuales}/{capacidad_maxima}")
                
                if inscritos_actuales >= capacidad_maxima:
                    st.error("⚠️ Este taller está lleno")
                    return
        
        st.markdown("---")
        st.markdown("### 📝 Observaciones")
        observaciones = st.text_area(
            "Observaciones (opcional):",
            placeholder="Ingrese cualquier observación relevante sobre la inscripción...",
            key="observaciones_inscripcion"
        )
        
        # Botones de acción
        col1, col2 = st.columns(2)
        with col1:
            submit_button = st.form_submit_button("✅ Confirmar Inscripción", type="primary")
        with col2:
            limpiar_button = st.form_submit_button("🔄 Limpiar Formulario")
        
        if limpiar_button:
            st.rerun()
        
        if submit_button:
            if not st.session_state.estudiante_validado or not st.session_state.taller_seleccionado:
                st.error("❌ Por favor, ingrese una cédula válida y seleccione un taller")
                return
            
            # Procesar inscripción
            with st.spinner("Procesando inscripción..."):
                resultado = motor_inscripciones.crear_inscripcion(
                    cedula_estudiante=st.session_state.estudiante_validado['cedula_usuario'],
                    id_formacion=st.session_state.taller_seleccionado['id_formacion'],
                    observaciones=observaciones
                )
            
            if resultado['exito']:
                st.success(f"✅ {resultado['mensaje']}")
                
                # Mostrar resumen
                st.markdown("---")
                st.markdown("### 📋 Resumen de la Inscripción")
                
                resumen_datos = resultado['datos']
                est = resumen_datos['estudiante']
                tall = resumen_datos['taller']
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Estudiante:**")
                    st.write(f"- 🎓 {est['nombre']} {est['apellido']}")
                    st.write(f"- 📧 {est.get('email_estudiante', 'N/A')}")
                    st.write(f"- 📚 {est.get('nombre_carrera', 'N/A')}")
                
                with col2:
                    st.markdown("**Taller:**")
                    st.write(f"- 📖 {tall['nombre']}")
                    st.write(f"- 👨‍🏫 {tall.get('nombre_facilitador', '')} {tall.get('apellido_facilitador', '')}".strip())
                    st.write(f"- 📅 Inicio: {tall.get('fecha_inicio', 'N/A')}")
                
                # Botón para nueva inscripción
                if st.button("🆕 Nueva Inscripción"):
                    st.rerun()
                    
            else:
                st.error(f"❌ {resultado['mensaje']}")

def mostrar_mis_inscripciones():
    """Muestra las inscripciones del estudiante actual"""
    
    st.markdown("## 📚 Mis Inscripciones")
    st.markdown("---")
    
    # Obtener cédula del estudiante actual
    cedula_estudiante = st.session_state.get('user_cedula')
    
    if not cedula_estudiante:
        st.error("No se pudo identificar al estudiante actual")
        return
    
    motor_inscripciones = MotorInscripciones()
    inscripciones = motor_inscripciones.listar_inscripciones_estudiante(cedula_estudiante)
    
    if not inscripciones:
        st.info("No tienes inscripciones registradas")
        return
    
    # Mostrar inscripciones en tabla
    df_inscripciones = pd.DataFrame(inscripciones)
    
    st.markdown("### 📋 Historial de Inscripciones")
    st.dataframe(
        df_inscripciones[[
            'nombre_taller',
            'nombre_facilitador',
            'apellido_facilitador',
            'fecha_inicio',
            'fecha_fin',
            'estado',
            'calificacion'
        ]],
        use_container_width=True,
        hide_index=True
    )

def mostrar_gestion_inscripciones():
    """Interfaz principal de gestión de inscripciones"""
    
    st.markdown("# 🎓 Gestión de Inscripciones")
    st.markdown("---")
    
    # Verificar permisos
    if not tiene_permiso(st.session_state.get('user_role', ''), 'Formación Complementaria', 'acceso'):
        st.error("❌ No tienes permisos para acceder a este módulo")
        return
    
    # Tabs para diferentes funciones
    tab1, tab2, tab3 = st.tabs(["📝 Nueva Inscripción", "👤 Mis Inscripciones", "📊 Reportes"])
    
    with tab1:
        mostrar_formulario_inscripcion()
    
    with tab2:
        mostrar_mis_inscripciones()
    
    with tab3:
        st.info("📊 Reportes de inscripciones en desarrollo...")
        # Aquí se pueden agregar reportes estadísticos

def inscripciones_main():
    """Función principal para el módulo de inscripciones"""
    try:
        mostrar_gestion_inscripciones()
    except Exception as e:
        st.error(f"Error en el módulo de inscripciones: {e}")
        logger.error(f"Error en inscripciones_main(): {e}")

# ========================================
# FUNCIÓN DE ENTRADA PRINCIPAL
# ========================================

if __name__ == "__main__":
    inscripciones_main()
