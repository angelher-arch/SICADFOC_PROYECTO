#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
solicitud_formacion.py - Módulo de Solicitud de Formación Complementaria
SICADFOC 2026 - Instituto Universitario Jesus Obrero
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Any, Optional

# Importaciones del sistema
from database import execute_query, ejecutar_transaccion
from seguridad import tiene_permiso
from gestion_carreras import obtener_carreras_activas

class SolicitudFormacion:
    """Clase principal para gestión de solicitudes de formación"""
    
    def __init__(self):
        self.user_role = st.session_state.get('user_role', None)
        self.user_cedula = st.session_state.get('user_cedula', None)
        self.user_nombre = st.session_state.get('user_nombre', None)
    
    def solicitud_formacion(self):
        """Función principal del módulo de solicitud de formación"""
        try:
            st.header("📝 Solicitud de Formación Complementaria")
            st.info("Complete el formulario para solicitar inscripción en un taller")
            
            # Validar permisos
            if not tiene_permiso(self.user_role, 'Formación Complementaria', 'Consultar'):
                st.error("No tienes permisos para acceder a este módulo.")
                return
            
            # Dos pasos lógicos
            tab1, tab2 = st.tabs(["👤 Datos del Estudiante", "🎯 Selección de Formación"])
            
            with tab1:
                self.paso_datos_estudiante()
            
            with tab2:
                self.paso_seleccion_formacion()
                
        except Exception as e:
            st.error(f"Error en módulo de solicitud de formación: {e}")
    
    def paso_datos_estudiante(self):
        """Paso 1: Búsqueda y validación de datos del estudiante"""
        st.subheader("👤 Datos del Estudiante")
        
        with st.form("form_buscar_estudiante"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                cedula_busqueda = st.text_input(
                    "Ingrese Cédula del Estudiante*",
                    placeholder="Ej: V-12345678",
                    key="cedula_busqueda_solicitud"
                )
            
            with col2:
                st.write("")  # Espacio para alinear botón
                buscar_button = st.form_submit_button("🔍 Buscar Estudiante", type="primary")
            
            if buscar_button and cedula_busqueda:
                self.buscar_estudiante(cedula_busqueda)
    
    def buscar_estudiante(self, cedula: str):
        """Busca y muestra datos del estudiante por cédula"""
        try:
            if not cedula or len(cedula.strip()) < 5:
                st.error("Por favor, ingrese una cédula válida.")
                return
            
            # Normalizar cédula
            cedula_normalizada = cedula.strip().upper()
            
            # Consultar estudiante con datos de persona y carrera
            query = """
            SELECT 
                e.cedula_estudiante,
                p.nombre,
                p.apellido,
                p.email_personal,
                p.telefono,
                e.id_carrera,
                c.nombre_carrera,
                e.semestre_actual,
                e.estado_registro
            FROM estudiante e
            INNER JOIN persona p ON e.cedula_estudiante = p.cedula
            INNER JOIN carrera c ON e.id_carrera = c.id_carrera
            WHERE e.cedula_estudiante = %s
            """
            
            resultado = execute_query(query, (cedula_normalizada,), fetch_one=True)
            
            if resultado:
                # Guardar datos del estudiante en sesión
                st.session_state.estudiante_seleccionado = resultado
                
                # Mostrar datos en modo lectura
                st.success("✅ Estudiante encontrado")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.text_input("Cédula", value=resultado['cedula_estudiante'], disabled=True)
                    st.text_input("Nombre", value=resultado['nombre'], disabled=True)
                    st.text_input("Apellido", value=resultado['apellido'], disabled=True)
                    st.text_input("Email", value=resultado.get('email_personal', ''), disabled=True)
                
                with col2:
                    st.text_input("Teléfono", value=resultado.get('telefono', ''), disabled=True)
                    st.text_input("Carrera", value=resultado['nombre_carrera'], disabled=True)
                    st.text_input("Semestre", value=str(resultado['semestre_actual']), disabled=True)
                    st.text_input("Estado", value=resultado['estado_registro'], disabled=True)
                
                # Habilitar paso 2
                st.session_state.paso1_completado = True
                
            else:
                st.error("❌ Estudiante no encontrado en el sistema.")
                st.info("Verifique la cédula ingresada o contacte al administrador.")
                st.session_state.paso1_completado = False
                
        except Exception as e:
            st.error(f"Error buscando estudiante: {e}")
            st.session_state.paso1_completado = False
    
    def paso_seleccion_formacion(self):
        """Paso 2: Selección del taller/formación"""
        st.subheader("🎯 Selección de Formación")
        
        # Verificar que paso 1 esté completado
        if not st.session_state.get('paso1_completado', False):
            st.warning("⚠️ Primero debe buscar y seleccionar un estudiante en la pestaña 'Datos del Estudiante'.")
            return
        
        estudiante = st.session_state.get('estudiante_seleccionado')
        if not estudiante:
            st.error("No hay estudiante seleccionado.")
            return
        
        # Obtener talleres disponibles
        talleres = self.obtener_talleres_disponibles()
        
        if not talleres:
            st.info("No hay talleres disponibles en este momento.")
            return
        
        with st.form("form_seleccion_taller"):
            st.markdown("#### 📋 Talleres Disponibles")
            
            # Selector de talleres
            opciones_talleres = [f"{t['nombre_taller']} - {t['codigo_certificado']}" for t in talleres]
            taller_seleccionado = st.selectbox(
                "Seleccionar Taller*",
                options=opciones_talleres,
                key="selector_taller_solicitud"
            )
            
            if taller_seleccionado:
                # Obtener datos del taller seleccionado
                indice = opciones_talleres.index(taller_seleccionado)
                taller = talleres[indice]
                
                # Mostrar detalles del taller
                st.markdown("#### 📄 Detalles del Taller")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.text_input("Nombre del Taller", value=taller['nombre_taller'], disabled=True)
                    st.text_input("Código", value=taller['codigo_certificado'], disabled=True)
                    st.text_input("Estado", value=taller['estado'], disabled=True)
                    st.text_input("Cupo Disponible", value=f"{taller['cupo_maximo'] - taller['cupo_actual']}", disabled=True)
                
                with col2:
                    st.text_input("Fecha Inicio", value=str(taller['fecha_inicio']), disabled=True)
                    st.text_input("Fecha Fin", value=str(taller['fecha_fin']), disabled=True)
                    st.text_input("Horas", value=str(taller['horas']), disabled=True)
                    st.text_input("Tipo", value=taller['tipo_taller'], disabled=True)
                
                # Obtener y mostrar facilitador
                facilitador = self.obtener_facilitador_taller(taller['id_formacion'])
                
                if facilitador:
                    st.text_input("Facilitador", value=f"{facilitador['nombre']} {facilitador['apellido']}", disabled=True)
                else:
                    st.text_input("Facilitador", value="No asignado", disabled=True)
                
                # Validar duplicidad de solicitudes
                solicitud_existente = self.verificar_solicitud_existente(
                    estudiante['cedula_estudiante'], 
                    taller['id_formacion']
                )
                
                # Botón de confirmación
                st.markdown("#### ✅ Confirmación")
                
                if solicitud_existente:
                    st.warning("⚠️ Ya posees una solicitud activa o aprobada para este taller.")
                    st.info("No puedes registrar otra solicitud para el mismo taller.")
                    confirmar_button = st.form_submit_button("Registrar Solicitud", disabled=True)
                else:
                    st.info("Puedes proceder con el registro de tu solicitud.")
                    confirmar_button = st.form_submit_button("✅ Confirmar Inscripción", type="primary")
                
                if confirmar_button and not solicitud_existente:
                    self.registrar_solicitud(estudiante, taller, facilitador)
    
    def obtener_talleres_disponibles(self) -> List[Dict]:
        """Obtiene talleres disponibles para inscripción"""
        try:
            query = """
            SELECT 
                id_formacion,
                nombre_taller,
                codigo_certificado,
                estado,
                fecha_inicio,
                fecha_fin,
                horas,
                tipo_taller,
                cupo_maximo,
                cupo_actual,
                descripcion
            FROM formacion_complementaria
            WHERE estado = 'Activo' 
            AND cupo_actual < cupo_maximo
            AND fecha_inicio > CURRENT_DATE
            ORDER BY fecha_inicio ASC
            """
            
            resultado = execute_query(query, fetch_all=True)
            
            if resultado and len(resultado) > 0:
                return resultado
            else:
                return []
                
        except Exception as e:
            st.error(f"Error obteniendo talleres disponibles: {e}")
            return []
    
    def obtener_facilitador_taller(self, id_taller: int) -> Optional[Dict]:
        """Obtiene el facilitador asignado a un taller"""
        try:
            query = """
            SELECT 
                p.cedula,
                p.nombre,
                p.apellido,
                p.email_personal
            FROM formacion_complementaria fc
            INNER JOIN profesor pr ON fc.id_usuario = pr.cedula_profesor
            INNER JOIN persona p ON pr.cedula_profesor = p.cedula
            WHERE fc.id_formacion = %s
            """
            
            resultado = execute_query(query, (id_taller,), fetch_one=True)
            
            return resultado if resultado else None
            
        except Exception as e:
            st.error(f"Error obteniendo facilitador: {e}")
            return None
    
    def verificar_solicitud_existente(self, cedula_estudiante: str, id_taller: int) -> bool:
        """Verifica si ya existe una solicitud para el mismo taller"""
        try:
            query = """
            SELECT COUNT(*) as count
            FROM solicitudes_formacion
            WHERE cedula_estudiante = %s 
            AND id_formacion = %s 
            AND estado IN ('Pendiente', 'Aprobada')
            """
            
            resultado = execute_query(query, (cedula_estudiante, id_taller), fetch_one=True)
            
            if resultado and resultado['count'] > 0:
                return True
            else:
                return False
                
        except Exception as e:
            st.error(f"Error verificando solicitud existente: {e}")
            return False
    
    def registrar_solicitud(self, estudiante: Dict, taller: Dict, facilitador: Optional[Dict]):
        """Registra una nueva solicitud de formación"""
        try:
            # Preparar datos para inserción
            datos_solicitud = {
                'cedula_estudiante': estudiante['cedula_estudiante'],
                'id_formacion': taller['id_formacion'],
                'estado': 'Pendiente',
                'fecha_solicitud': datetime.now(),
                'cedula_solicitante': self.user_cedula,  # Quien registra la solicitud
                'observaciones': f"Solicitud generada por {self.user_nombre} ({self.user_cedula})"
            }
            
            # Insertar solicitud
            query_insert = """
            INSERT INTO solicitudes_formacion 
            (cedula_estudiante, id_formacion, estado, fecha_solicitud, cedula_solicitante, observaciones)
            VALUES (%(cedula_estudiante)s, %(id_formacion)s, %(estado)s, %(fecha_solicitud)s, %(cedula_solicitante)s, %(observaciones)s)
            """
            
            execute_query(query_insert, datos_solicitud)
            
            # Éxito
            st.success("✅ Solicitud registrada exitosamente")
            st.balloons()
            
            # Mostrar resumen
            st.markdown("#### 📋 Resumen de Solicitud")
            
            resumen_data = {
                'Estudiante': f"{estudiante['nombre']} {estudiante['apellido']}",
                'Cédula': estudiante['cedula_estudiante'],
                'Carrera': estudiante['nombre_carrera'],
                'Taller': taller['nombre_taller'],
                'Código': taller['codigo_certificado'],
                'Fecha Inicio': str(taller['fecha_inicio']),
                'Facilitador': f"{facilitador['nombre']} {facilitador['apellido']}" if facilitador else "No asignado",
                'Estado': 'Pendiente',
                'Fecha Solicitud': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            df_resumen = pd.DataFrame(list(resumen_data.items()), columns=['Campo', 'Valor'])
            st.dataframe(df_resumen, use_container_width=True)
            
            # Limpiar sesión para nueva solicitud
            if st.button("📝 Nueva Solicitud"):
                st.session_state.paso1_completado = False
                st.session_state.estudiante_seleccionado = None
                st.rerun()
                
        except Exception as e:
            st.error(f"Error registrando solicitud: {e}")

# Función principal para compatibilidad con el orquestador
def solicitud_formacion_main():
    """Función principal del módulo de solicitud de formación"""
    try:
        if not tiene_permiso(st.session_state.get('user_role'), 'Formación Complementaria', 'Consultar'):
            st.error("No tienes permisos para acceder a este módulo.")
            return
        
        gestor = SolicitudFormacion()
        gestor.solicitud_formacion()
        
    except Exception as e:
        st.error(f"Error en el módulo de solicitud de formación: {e}")

# Alias de compatibilidad
def solicitud_formacion():
    """Alias de compatibilidad para el orquestador principal"""
    solicitud_formacion_main()
