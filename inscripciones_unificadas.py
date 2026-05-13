#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inscripciones_unificadas.py - Módulo Unificado de Inscripciones
SICADFOC 2026 - Instituto Universitario Jesus Obrero
Unificación de Solicitud de Formación e Inscripciones en una sola funcionalidad
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Any, Optional

# Importaciones del sistema
from database import execute_query, ejecutar_transaccion, get_connection
from seguridad import tiene_permiso

class InscripcionesUnificadas:
    """Clase principal para gestión unificada de inscripciones"""
    
    def __init__(self):
        self.user_role = st.session_state.get('user_role', None)
        self.user_cedula = st.session_state.get('user_cedula', None)
        self.user_nombre = st.session_state.get('user_nombre', None)
    
    def inscripciones_main(self):
        """Función principal del módulo unificado de inscripciones"""
        try:
            st.header("🎓 Inscripciones a Talleres")
            st.info("Complete el proceso de inscripción en talleres de formación complementaria")
            
            # Validar permisos
            if not tiene_permiso(self.user_role, 'Inscripciones', 'Consultar'):
                st.error("No tienes permisos para acceder a este módulo.")
                return
            
            # Proceso de inscripción en pasos
            tab1, tab2, tab3, tab4 = st.tabs(["👤 Validar Estudiante", "📋 Talleres Disponibles", "✅ Confirmar Inscripción", "📊 Mi Historial"])
            
            with tab1:
                self.paso_validar_estudiante()
            
            with tab2:
                self.paso_seleccion_taller()
            
            with tab3:
                self.paso_confirmar_inscripcion()
            
            with tab4:
                self.paso_historial_estudiante()
                
        except Exception as e:
            st.error(f"Error en módulo de inscripciones: {e}")
    
    def paso_validar_estudiante(self):
        """Paso 1: Validación de datos del estudiante desde Gestión Estudiantil"""
        st.subheader("👤 Validación de Estudiante")
        
        with st.form("form_validar_estudiante"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                cedula_busqueda = st.text_input(
                    "Ingrese Cédula del Estudiante*",
                    placeholder="Ej: V-12345678",
                    key="cedula_busqueda_inscripcion"
                )
            
            with col2:
                st.write("")  # Espacio para alinear botón
                buscar_button = st.form_submit_button("🔍 Validar Estudiante", type="primary")
            
            if buscar_button and cedula_busqueda:
                self.validar_estudiante(cedula_busqueda)
        
        # Mostrar datos del estudiante validado (fuera del formulario para persistencia)
        if st.session_state.get('datos_alumno'):
            estudiante = st.session_state['datos_alumno']
            st.success("✅ Estudiante validado exitosamente")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input("Cédula", value=estudiante.get('cedula_estudiante', ''), disabled=True, key="cedula_validada")
                st.text_input("Nombre", value=estudiante.get('nombre', ''), disabled=True, key="nombre_validado")
                st.text_input("Apellido", value=estudiante.get('apellido', ''), disabled=True, key="apellido_validado")
                st.text_input("Email", value=estudiante.get('email', ''), disabled=True, key="email_validado")
            
            with col2:
                st.text_input("Teléfono", value=estudiante.get('telefono', ''), disabled=True, key="telefono_validado")
                st.text_input("Carrera", value=estudiante.get('nombre_carrera', ''), disabled=True, key="carrera_validada")
                st.text_input("Semestre", value=str(estudiante.get('id_semestre_formacion', 'N/A')), disabled=True, key="semestre_validado")
    
    def validar_estudiante(self, cedula: str):
        """Valida y muestra datos del estudiante desde Gestión Estudiantil"""
        try:
            if not cedula or len(cedula.strip()) < 5:
                st.error("Por favor, ingrese una cédula válida.")
                return
            
            # Normalizar cédula
            cedula_normalizada = cedula.strip().upper()
            if not cedula_normalizada.startswith('V-'):
                cedula_normalizada = f'V-{cedula_normalizada}'
            
            # Consulta simplificada solo con tablas estudiante y carrera
            query = """
                SELECT 
                    e.cedula_estudiante,
                    e.nombres as nombre,
                    e.apellidos as apellido,
                    e.correo as email,
                    e.telefono,
                    e.id_carrera,
                    c.nombre_carrera,
                    e.id_semestre_formacion
                FROM estudiante e
                LEFT JOIN carrera c ON e.id_carrera = c.id_carrera
                WHERE e.cedula_estudiante = %s
                LIMIT 1
            """
            
            estudiantes = execute_query(query, (cedula_normalizada,))
            
            if estudiantes:
                estudiante = estudiantes[0]
                
                # Guardar datos del estudiante en sesión
                st.session_state.datos_estudiante = estudiante
                st.session_state.datos_alumno = estudiante  # Alias para consistencia
                st.session_state.estudiante_validado = estudiante
                st.session_state.paso1_completado = True
                
                # No mostrar datos aquí - se muestran fuera del formulario
                
            else:
                st.error("❌ Estudiante no encontrado o no está activo.")
                st.info("Verifique la cédula ingresada o contacte al administrador.")
                st.session_state.paso1_completado = False
                
        except Exception as e:
            st.error(f"Error validando estudiante: {e}")
            st.session_state.paso1_completado = False
    
    def paso_seleccion_taller(self):
        """Paso 2: Selección de talleres disponibles"""
        st.subheader("📋 Talleres Disponibles")
        
        # Verificar que exista estudiante validado (múltiples formas de verificar)
        estudiante_validado = (
            st.session_state.get('datos_alumno') or
            st.session_state.get('datos_estudiante') or
            st.session_state.get('estudiante_validado')
        )
        
        if not estudiante_validado:
            st.warning("⚠️ Primero debe validar un estudiante en la pestaña 'Validar Estudiante'.")
            return
        
        # Obtener talleres disponibles
        talleres = self.obtener_talleres_disponibles()
        
        if not talleres:
            st.info("No hay talleres disponibles en este momento.")
            return
        
        st.markdown("#### 📄 Listado de Talleres Activos")
        
        # Crear tabla de talleres
        df_talleres = pd.DataFrame(talleres)
        
        # Formatear datos para visualización
        df_talleres['Cupos Restantes'] = df_talleres.apply(
            lambda row: self.calcular_cupos_restantes(row['id_taller']), axis=1
        )
        
        # Renombrar columnas para mejor visualización
        columnas_mostrar = {
            'id_taller': 'ID Taller',
            'nombre_taller': 'Nombre del Taller',
            'facilitador': 'Facilitador',
            'fecha_inicio': 'Fecha Inicio'
        }
        
        df_visualizacion = df_talleres.rename(columns=columnas_mostrar)
        df_visualizacion = df_visualizacion[list(columnas_mostrar.values()) + ['Cupos Restantes']]
        
        # Mostrar tabla con formato
        st.dataframe(
            df_visualizacion,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID Taller": st.column_config.TextColumn("ID Taller", width="small"),
                "Nombre del Taller": st.column_config.TextColumn("Nombre del Taller", width="large"),
                "Facilitador": st.column_config.TextColumn("Facilitador", width="medium"),
                "Fecha Inicio": st.column_config.DateColumn("Fecha Inicio", width="medium"),
                "Cupos Restantes": st.column_config.NumberColumn("Cupos Restantes", width="small")
            }
        )
        
        # Selector de taller
        with st.form("form_seleccionar_taller"):
            opciones_talleres = [f"{t['id_taller']} - {t['nombre_taller']}" for t in talleres]
            seleccion = st.radio(
                "Seleccionar Taller*",
                options=opciones_talleres,
                key="selector_taller_inscripcion"
            )

            confirmar_button = st.form_submit_button("Seleccionar Taller", type="primary")

            if confirmar_button:
                if seleccion:
                    indice = opciones_talleres.index(seleccion)
                    taller = talleres[indice]
                    st.session_state.taller_seleccionado = taller
                    st.session_state.paso2_completado = True
                    st.success("✅ Taller seleccionado correctamente")
                else:
                    st.warning("Por favor, seleccione un taller antes de continuar.")

        if st.session_state.get('taller_seleccionado'):
            taller = st.session_state['taller_seleccionado']
            st.markdown("#### 📄 Detalles del Taller Seleccionado")
            col1, col2 = st.columns(2)

            with col1:
                st.text_input("ID Taller", value=taller.get('id_taller', 'N/A'), disabled=True)
                st.text_input("Nombre del Taller", value=taller.get('nombre_taller', 'N/A'), disabled=True)
                st.text_input("Facilitador", value=taller.get('facilitador', 'N/A'), disabled=True)
                st.text_input("Cupo Máximo", value=str(taller.get('cupo_maximo', 'N/A')), disabled=True)

            with col2:
                st.text_input("Fecha de Inicio", value=str(taller.get('fecha_inicio', 'N/A')), disabled=True)
                st.text_input("Duración", value=f"{taller.get('duracion_horas', 'N/A')} horas", disabled=True)
                cupos_restantes = self.calcular_cupos_restantes(taller['id_taller'])
                st.text_input("Cupos Disponibles", value=str(cupos_restantes), disabled=True)
                if cupos_restantes <= 0:
                    st.error("⚠️ Sin cupos disponibles")
                elif cupos_restantes <= 5:
                    st.warning(f"⚠️ Solo {cupos_restantes} cupos restantes")
    
    def paso_confirmar_inscripcion(self):
        """Paso 3: Confirmación final de la inscripción"""
        st.subheader("✅ Confirmar Inscripción")
        
        # Verificar que los pasos anteriores estén completados
        estudiante_validado = (
            st.session_state.get('datos_alumno') or
            st.session_state.get('datos_estudiante') or
            st.session_state.get('estudiante_validado')
        )
        
        if not estudiante_validado:
            st.warning("⚠️ Primero debe validar un estudiante en la pestaña 'Validar Estudiante'.")
            return
        
        if not st.session_state.get('taller_seleccionado'):
            st.warning("⚠️ Primero debe seleccionar un taller en la pestaña 'Talleres Disponibles'.")
            return
        
        estudiante = st.session_state['datos_alumno']
        taller = st.session_state['taller_seleccionado']
        
        # Verificar cupos disponibles
        cupos_restantes = self.calcular_cupos_restantes(taller['id_taller'])
        if cupos_restantes <= 0:
            st.error("❌ No hay cupos disponibles para este taller.")
            return
        
        # Mostrar resumen de la inscripción
        st.markdown("#### 📋 Resumen de Inscripción")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**👤 Datos del Estudiante:**")
            st.info(f"""
            **Cédula:** {estudiante.get('cedula_estudiante', 'N/A')}
            **Nombre:** {estudiante.get('nombre', 'N/A')} {estudiante.get('apellido', 'N/A')}
            **Carrera:** {estudiante.get('nombre_carrera', 'N/A')}
            **Semestre:** {estudiante.get('id_semestre_formacion', 'N/A')}
            """)
        
        with col2:
            st.markdown("**📚 Datos del Taller:**")
            st.info(f"""
            **ID Taller:** {taller.get('id_taller', 'N/A')}
            **Nombre:** {taller.get('nombre_taller', 'N/A')}
            **Facilitador:** {taller.get('facilitador', 'N/A')}
            **Fecha Inicio:** {taller.get('fecha_inicio', 'N/A')}
            **Duración:** {taller.get('duracion_horas', 'N/A')} horas
            **Cupos Disponibles:** {cupos_restantes}
            """)
        
        # Formulario de confirmación
        with st.form("form_confirmar_inscripcion"):
            st.markdown("#### ✍️ Confirmación")
            
            # Campo de observaciones opcionales
            observaciones = st.text_area(
                "Observaciones (opcional)",
                placeholder="Ingrese cualquier observación adicional...",
                height=100,
                key="observaciones_inscripcion"
            )
            
            # Checkbox de aceptación de términos
            aceptar_terminos = st.checkbox(
                "✅ Acepto los términos y condiciones del taller",
                key="aceptar_terminos_inscripcion"
            )
            
            # Botón de confirmación
            confirmar_inscripcion = st.form_submit_button(
                "🎓 Confirmar Inscripción",
                type="primary"
            )
            
            if confirmar_inscripcion:
                if not aceptar_terminos:
                    st.error("❌ Debe aceptar los términos y condiciones para continuar.")
                    return
                
                # Procesar la inscripción
                self.procesar_inscripcion(estudiante, taller, observaciones)
    
    def paso_historial_estudiante(self):
        """Paso 4: Historial de inscripciones del estudiante"""
        st.subheader("📊 Mi Historial de Inscripciones")

        # Verificar que tengamos cédula del estudiante (desde sesión o validación previa)
        cedula_estudiante = None

        # Primero intentar obtener de estudiante validado en sesión
        if st.session_state.get('datos_alumno'):
            cedula_estudiante = st.session_state['datos_alumno']['cedula_estudiante']
        elif st.session_state.get('estudiante_validado'):
            cedula_estudiante = st.session_state['estudiante_validado']['cedula_estudiante']
        # Si no, usar la cédula del usuario actual (si es estudiante)
        elif self.user_role == 'Estudiante' and self.user_cedula:
            cedula_estudiante = self.user_cedula

        if not cedula_estudiante:
            st.warning("⚠️ Primero debe validar un estudiante o iniciar sesión como estudiante para ver el historial.")
            return

        # Obtener historial de inscripciones
        historial = self.obtener_historial_estudiante(cedula_estudiante)

        if not historial:
            st.info("📝 No tienes inscripciones registradas aún.")
            return

        st.markdown(f"**📋 Historial para: {cedula_estudiante}**")

        # Convertir a DataFrame para mejor visualización
        df_historial = pd.DataFrame(historial)

        # Mostrar métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Inscripciones", len(df_historial))
        with col2:
            por_inscribir = len(df_historial[df_historial['estado_estudiante'] == 'Por Inscribir'])
            st.metric("Por Inscribir", por_inscribir)
        with col3:
            inscritos = len(df_historial[df_historial['estado_estudiante'] == 'Inscrito'])
            st.metric("Inscritos", inscritos)
        with col4:
            otros = len(df_historial) - por_inscribir - inscritos
            st.metric("Otros Estados", otros)

        # Tabla de historial
        st.markdown("#### 📄 Detalle de Inscripciones")

        # Formatear datos para visualización
        df_visualizacion = df_historial[[
            'nombre_taller', 'estado_estudiante', 'estado_academico',
            'fecha_creacion', 'fecha_cambio', 'observaciones'
        ]].copy()

        df_visualizacion.columns = [
            'Taller', 'Estado Estudiante', 'Estado Académico',
            'Fecha Inscripción', 'Última Modificación', 'Observaciones'
        ]

        st.dataframe(
            df_visualizacion,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Taller": st.column_config.TextColumn("Taller", width="large"),
                "Estado Estudiante": st.column_config.TextColumn("Estado Estudiante", width="medium"),
                "Estado Académico": st.column_config.TextColumn("Estado Académico", width="medium"),
                "Fecha Inscripción": st.column_config.DateColumn("Fecha Inscripción", width="medium"),
                "Última Modificación": st.column_config.DateColumn("Última Modificación", width="medium"),
                "Observaciones": st.column_config.TextColumn("Observaciones", width="large")
            }
        )

        # Mostrar detalles expandidos
        st.markdown("#### 📋 Detalles Expandidos")
        for idx, row in df_historial.iterrows():
            with st.expander(f"📚 {row['nombre_taller']} - {row['estado_estudiante']}", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Información del Taller:**")
                    st.text(f"• Nombre: {row['nombre_taller']}")
                    st.text(f"• Facilitador: {row.get('facilitador', 'No asignado')}")
                    st.text(f"• Fecha Inicio: {row.get('fecha_inicio', 'N/A')}")

                with col2:
                    st.markdown("**Estados:**")
                    st.text(f"• Estado Estudiante: {row['estado_estudiante']}")
                    st.text(f"• Estado Académico: {row.get('estado_academico', 'No definido')}")
                    st.text(f"• Fecha Inscripción: {row['fecha_creacion']}")
                    st.text(f"• Última Modificación: {row['fecha_cambio']}")

                if row.get('observaciones'):
                    st.markdown("**Observaciones:**")
                    st.text(row['observaciones'])

    def obtener_historial_estudiante(self, cedula_estudiante: str) -> List[Dict]:
        """Obtiene el historial de inscripciones de un estudiante"""
        try:
            query = """
                SELECT
                    it.id_inscripcion,
                    it.cedula_estudiante,
                    it.id_taller,
                    t.nombre_taller,
                    CONCAT(p.nombre, ' ', p.apellido) as facilitador,
                    t.fecha_inicio,
                    it.estado_estudiante,
                    it.estado_academico,
                    it.fecha_creacion,
                    it.fecha_cambio,
                    it.observaciones
                FROM inscripciones_talleres it
                LEFT JOIN taller t ON it.id_taller = t.id_taller
                LEFT JOIN profesor pr ON it.id_facilitador = pr.cedula_profesor
                LEFT JOIN persona p ON pr.cedula_profesor = p.cedula
                WHERE it.cedula_estudiante = %s
                ORDER BY it.fecha_creacion DESC
            """

            return execute_query(query, (cedula_estudiante,))
        except Exception as e:
            st.error(f"Error obteniendo historial: {e}")
            return []
        
        # Mostrar resumen
        st.markdown("#### 📋 Resumen de Inscripción")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Datos del Estudiante:**")
            st.text(f"• Cédula: {estudiante['cedula_estudiante']}")
            st.text(f"• Nombre: {estudiante['nombre']} {estudiante['apellido']}")
            st.text(f"• Carrera: {estudiante['nombre_carrera']}")
            st.text(f"• Semestre: {estudiante.get('id_semestre_formacion', 'N/A')}")
        
        with col2:
            st.markdown("**Datos del Taller:**")
            st.text(f"• ID Taller: {taller.get('id_taller', 'N/A')}")
            st.text(f"• Nombre: {taller['nombre_taller']}")
            st.text(f"• Facilitador: {taller.get('facilitador_nombre', 'N/A')}")
            st.text(f"• Fecha Inicio: {taller['fecha_inicio']}")
            st.text(f"• Cupos Restantes: {cupos_restantes}")
        
        # Procesar inscripción
        with st.form("form_confirmar_inscripcion"):
            st.markdown("---")
            
            terminos_aceptados = st.checkbox(
                "Acepto los términos y condiciones de la inscripción",
                key="terminos_inscripcion"
            )
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                cancelar_button = st.form_submit_button("Cancelar", type="secondary")
            
            with col2:
                inscribir_button = st.form_submit_button("✅ Confirmar Inscripción", type="primary")
            
            if inscribir_button and terminos_aceptados:
                self.procesar_inscripcion(estudiante, taller)
    
    def procesar_inscripcion(self, estudiante: Dict, taller: Dict, observaciones: str = ""):
        """Procesa la inscripción del estudiante en el taller usando la nueva tabla de estados"""
        try:
            # Verificar si ya está inscrito en la nueva tabla
            inscripcion_existente = execute_query("""
                SELECT id_inscripcion
                FROM inscripciones_talleres
                WHERE cedula_estudiante = %s
                AND id_taller = %s
            """, (estudiante['cedula_estudiante'], taller['id_taller']))

            if inscripcion_existente:
                st.error("❌ Ya tienes una inscripción registrada en este taller.")
                return

            # Obtener cédula del facilitador desde el taller
            facilitador_query = """
                SELECT t.cedula_profesor
                FROM taller t
                WHERE t.id_taller = %s
                LIMIT 1
            """
            facilitador_result = execute_query(facilitador_query, (taller['id_taller'],))
            cedula_facilitador = facilitador_result[0]['cedula_profesor'] if facilitador_result else None

            # Preparar observaciones
            observaciones_completas = f"Inscripción generada el {datetime.now().strftime('%d/%m/%Y %H:%M')} por {self.user_nombre}"
            if observaciones.strip():
                observaciones_completas += f". Observaciones: {observaciones.strip()}"

            # Crear inscripción en la nueva tabla con estado 'Por Inscribir'
            datos_inscripcion = {
                'cedula_estudiante': estudiante['cedula_estudiante'],
                'id_taller': taller['id_taller'],
                'id_facilitador': cedula_facilitador,
                'estado_estudiante': 'Por Inscribir',
                'observaciones': observaciones_completas
            }

            # Ejecutar inserción
            resultado = ejecutar_transaccion([(
                "INSERT INTO inscripciones_talleres (cedula_estudiante, id_taller, id_facilitador, estado_estudiante, observaciones) VALUES (%(cedula_estudiante)s, %(id_taller)s, %(id_facilitador)s, %(estado_estudiante)s, %(observaciones)s)",
                datos_inscripcion
            )])

            if resultado and resultado.get('success'):
                st.success("✅ Inscripción registrada exitosamente")
                st.info("📋 Tu inscripción está en estado 'Por Inscribir'. El facilitador revisará y actualizará tu estado académico.")

                # Limpiar sesión para nueva inscripción
                for key in ['paso1_completado', 'paso2_completado', 'estudiante_validado', 'taller_seleccionado']:
                    if key in st.session_state:
                        del st.session_state[key]

                st.rerun()
            else:
                st.error("❌ Error al procesar la inscripción. Intente nuevamente.")

        except Exception as e:
            st.error(f"Error procesando inscripción: {e}")
            st.error(f"Error procesando inscripción: {e}")
    
    def obtener_talleres_disponibles(self) -> List[Dict]:
        """Obtiene lista de talleres disponibles con estado activo"""
        try:
            query = """
                SELECT
                    t.id_taller,
                    t.nombre_taller,
                    CONCAT(p.nombre, ' ', p.apellido) as facilitador,
                    t.fecha_inicio,
                    t.duracion_horas,
                    t.capacidad_maxima as cupo_maximo,
                    t.cedula_profesor
                FROM taller t
                LEFT JOIN profesor pr ON t.cedula_profesor = pr.cedula_profesor
                LEFT JOIN persona p ON pr.cedula_profesor = p.cedula
                WHERE LOWER(t.estado) = 'activo'
                ORDER BY t.fecha_inicio ASC NULLS LAST
            """

            talleres = execute_query(query)
            return talleres if talleres else []

        except Exception as e:
            st.error(f"Error obteniendo talleres: {e}")
            return []
    
    def calcular_cupos_restantes(self, id_taller: int) -> int:
        """Calcula cupos restantes: Total - inscripciones activas para el taller."""
        try:
            # Obtener capacidad máxima desde la tabla taller
            query_cupo = """
                SELECT capacidad_maxima
                FROM taller
                WHERE id_taller = %s
                LIMIT 1
            """
            resultado = execute_query(query_cupo, (id_taller,))
            if not resultado:
                return 0

            capacidad_maxima = resultado[0].get('capacidad_maxima', 0) or 0

            # Contar inscripciones activas (no canceladas) desde la nueva tabla
            query_inscripciones = """
                SELECT COUNT(*) as activas
                FROM inscripciones_talleres
                WHERE id_taller = %s
                AND estado_estudiante != 'No Inscrito'
            """
            resultado_inscripciones = execute_query(query_inscripciones, (id_taller,))
            activas = resultado_inscripciones[0].get('activas', 0) if resultado_inscripciones else 0

            return max(0, capacidad_maxima - activas)

        except Exception as e:
            print(f"Error calculando cupos: {e}")
            return 0

# Función principal para el módulo
def inscripciones_unificadas_main():
    """Punto de entrada principal del módulo"""
    app = InscripcionesUnificadas()
    app.inscripciones_main()

if __name__ == "__main__":
    inscripciones_unificadas_main()
