#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gestion_inscripciones_facilitador.py - Gestión de Inscripciones para Facilitadores
SICADFOC 2026 - Instituto Universitario Jesus Obrero
Módulo para que los facilitadores gestionen el estado académico de estudiantes inscritos
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional

# Importaciones del sistema
from database import execute_query, ejecutar_transaccion, get_connection
from seguridad import tiene_permiso
from gestor_certificaciones import GestorCertificaciones

class GestionInscripcionesFacilitador:
    """Clase para gestión de inscripciones desde la perspectiva del facilitador"""

    def __init__(self):
        self.user_role = st.session_state.get('user_role', None)
        self.user_cedula = st.session_state.get('user_cedula', None)
        self.user_nombre = st.session_state.get('user_nombre', None)
        self.gestor_cert = GestorCertificaciones()

    def main(self):
        """Función principal del módulo"""
        try:
            st.header("👨‍🏫 Gestión de Inscripciones - Facilitador")
            st.info("Gestione el estado académico de estudiantes inscritos en sus talleres")

            # Validar permisos
            if not tiene_permiso(self.user_role, 'Inscripciones', 'Consultar'):
                st.error("No tienes permisos para acceder a este módulo.")
                return

            # Obtener información del profesor
            profesor_info = self.obtener_info_profesor()
            if not profesor_info:
                st.error("No se encontró información de profesor para tu usuario.")
                return

            st.subheader(f"👤 Facilitador: {profesor_info['nombre_completo']}")

            # Filtros
            with st.form("filtros_inscripciones"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    filtro_taller = st.selectbox(
                        "Filtrar por Taller",
                        options=["Todos"] + [f"{t['id_taller']} - {t['nombre_taller']}" for t in self.obtener_talleres_profesor(profesor_info['id_profesor'])],
                        key="filtro_taller_facilitador"
                    )

                with col2:
                    filtro_estado = st.selectbox(
                        "Filtrar por Estado Académico",
                        options=["Todos", "Inscrito", "En Curso", "Aprobado", "No Aprobado"],
                        key="filtro_estado_academico"
                    )

                filtrar_button = st.form_submit_button("🔍 Aplicar Filtros", type="primary")

            # Obtener y mostrar inscripciones
            if filtrar_button or 'inscripciones_cache' not in st.session_state:
                self.cargar_inscripciones(profesor_info['id_profesor'], filtro_taller, filtro_estado)

            if 'inscripciones_cache' in st.session_state and st.session_state.inscripciones_cache:
                self.mostrar_tabla_inscripciones()
            else:
                st.info("No hay inscripciones que mostrar con los filtros aplicados.")

        except Exception as e:
            st.error(f"Error en módulo de gestión de facilitador: {e}")

    def obtener_info_profesor(self) -> Optional[Dict]:
        """Obtiene información del profesor basado en la cédula del usuario"""
        try:
            query = """
                SELECT
                    p.cedula_profesor as id_profesor,
                    CONCAT(pr.nombre, ' ', pr.apellido) as nombre_completo,
                    p.cedula_profesor,
                    p.especialidad
                FROM profesor p
                LEFT JOIN persona pr ON p.cedula_profesor = pr.cedula
                WHERE p.cedula_profesor = %s
                LIMIT 1
            """
            resultado = execute_query(query, (self.user_cedula,))
            return resultado[0] if resultado else None
        except Exception as e:
            st.error(f"Error obteniendo info del profesor: {e}")
            return None

    def obtener_talleres_profesor(self, cedula_profesor: str) -> List[Dict]:
        """Obtiene talleres asignados al profesor"""
        try:
            query = """
                SELECT DISTINCT
                    t.id_taller,
                    t.nombre_taller,
                    t.fecha_inicio,
                    t.fecha_fin
                FROM taller t
                WHERE t.cedula_profesor = %s
                AND t.estado = 'activo'
                ORDER BY t.fecha_inicio DESC
            """
            return execute_query(query, (cedula_profesor,))
        except Exception as e:
            st.error(f"Error obteniendo talleres: {e}")
            return []

    def cargar_inscripciones(self, cedula_profesor: str, filtro_taller: str, filtro_estado: str):
        """Carga inscripciones con filtros aplicados"""
        try:
            # Base query
            query = """
                SELECT
                    it.id_inscripcion,
                    it.cedula_estudiante,
                    CONCAT(e.nombres, ' ', e.apellidos) as nombre_estudiante,
                    it.id_taller,
                    t.nombre_taller,
                    it.estado_estudiante,
                    it.estado_academico,
                    it.fecha_cambio,
                    it.fecha_creacion,
                    it.observaciones,
                    CONCAT(p.nombre, ' ', p.apellido) as nombre_facilitador
                FROM inscripciones_talleres it
                LEFT JOIN estudiante e ON it.cedula_estudiante = e.cedula_estudiante
                LEFT JOIN taller t ON it.id_taller = t.id_taller
                LEFT JOIN profesor pr ON it.id_facilitador = pr.cedula_profesor
                LEFT JOIN persona p ON pr.cedula_profesor = p.cedula
                WHERE it.id_facilitador = %s
            """

            params = [cedula_profesor]

            # Aplicar filtro de taller
            if filtro_taller != "Todos":
                id_taller = int(filtro_taller.split(' - ')[0])
                query += " AND it.id_taller = %s"
                params.append(id_taller)

            # Aplicar filtro de estado académico
            if filtro_estado != "Todos":
                query += " AND it.estado_academico = %s"
                params.append(filtro_estado)

            query += " ORDER BY it.fecha_cambio DESC"

            inscripciones = execute_query(query, tuple(params))
            st.session_state.inscripciones_cache = inscripciones if inscripciones else []

        except Exception as e:
            st.error(f"Error cargando inscripciones: {e}")
            st.session_state.inscripciones_cache = []

    def mostrar_tabla_inscripciones(self):
        """Muestra tabla de inscripciones con opciones de edición"""
        st.subheader("📋 Inscripciones de Estudiantes")

        # Convertir a DataFrame para mejor visualización
        df = pd.DataFrame(st.session_state.inscripciones_cache)

        # Mostrar métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Inscripciones", len(df))
        with col2:
            inscritos = len(df[df['estado_academico'] == 'Inscrito'])
            st.metric("Inscritos", inscritos)
        with col3:
            en_curso = len(df[df['estado_academico'] == 'En Curso'])
            st.metric("En Curso", en_curso)
        with col4:
            aprobados = len(df[df['estado_academico'] == 'Aprobado'])
            st.metric("Aprobados", aprobados)

        # Tabla con opciones de edición
        for idx, row in df.iterrows():
            with st.expander(f"📚 {row['nombre_estudiante']} - {row['nombre_taller']}", expanded=False):
                col1, col2, col3 = st.columns([2, 2, 1])

                with col1:
                    st.markdown("**Datos del Estudiante:**")
                    st.text(f"• Cédula: {row['cedula_estudiante']}")
                    st.text(f"• Nombre: {row['nombre_estudiante']}")
                    st.text(f"• Estado Estudiante: {row['estado_estudiante']}")

                with col2:
                    st.markdown("**Datos del Taller:**")
                    st.text(f"• ID Taller: {row['id_taller']}")
                    st.text(f"• Nombre: {row['nombre_taller']}")
                    st.text(f"• Estado Académico: {row['estado_academico'] or 'No definido'}")

                with col3:
                    st.markdown("**Acciones:**")
                    if st.button(f"✏️ Editar Estado", key=f"edit_{row['id_inscripcion']}"):
                        st.session_state[f"editing_{row['id_inscripcion']}"] = True

                    if st.button(f"👁️ Ver Detalles", key=f"view_{row['id_inscripcion']}"):
                        self.mostrar_detalles_inscripcion(row)

                # Formulario de edición si está activado
                if st.session_state.get(f"editing_{row['id_inscripcion']}", False):
                    self.formulario_editar_estado(row)

    def formulario_editar_estado(self, inscripcion: Dict):
        """Formulario para editar el estado académico"""
        st.markdown("---")
        st.markdown("**📝 Editar Estado Académico**")

        with st.form(f"form_editar_estado_{inscripcion['id_inscripcion']}"):
            nuevo_estado = st.selectbox(
                "Nuevo Estado Académico",
                options=["Inscrito", "En Curso", "Aprobado", "No Aprobado"],
                index=["Inscrito", "En Curso", "Aprobado", "No Aprobado"].index(inscripcion['estado_academico']) if inscripcion['estado_academico'] in ["Inscrito", "En Curso", "Aprobado", "No Aprobado"] else 0,
                key=f"estado_academico_{inscripcion['id_inscripcion']}"
            )

            observaciones = st.text_area(
                "Observaciones (opcional)",
                value=inscripcion.get('observaciones', ''),
                key=f"observaciones_{inscripcion['id_inscripcion']}"
            )

            col1, col2 = st.columns([1, 1])

            with col1:
                guardar_button = st.form_submit_button("💾 Guardar Cambios", type="primary")

            with col2:
                cancelar_button = st.form_submit_button("❌ Cancelar")

            if guardar_button:
                self.actualizar_estado_academico(
                    inscripcion['id_inscripcion'],
                    nuevo_estado,
                    observaciones
                )
                # Limpiar estado de edición
                del st.session_state[f"editing_{inscripcion['id_inscripcion']}"]
                st.rerun()

            if cancelar_button:
                # Limpiar estado de edición
                del st.session_state[f"editing_{inscripcion['id_inscripcion']}"]
                st.rerun()

    def actualizar_estado_academico(self, id_inscripcion: int, nuevo_estado: str, observaciones: str):
        """Actualiza el estado académico y dispara automatización si es necesario"""
        try:
            # Actualizar estado
            query_update = """
                UPDATE inscripciones_talleres
                SET estado_academico = %s,
                    observaciones = %s,
                    fecha_cambio = NOW()
                WHERE id_inscripcion = %s
            """

            result = ejecutar_transaccion([(query_update, (nuevo_estado, observaciones, id_inscripcion))])

            if result.get('success'):
                st.success(f"✅ Estado académico actualizado a '{nuevo_estado}'")

                # Automatización: Si el estado es 'Aprobado', generar certificado
                if nuevo_estado == 'Aprobado':
                    self.generar_certificado_automatico(id_inscripcion)

                # Limpiar cache para refrescar datos
                if 'inscripciones_cache' in st.session_state:
                    del st.session_state.inscripciones_cache

            else:
                st.error("❌ Error al actualizar el estado académico")

        except Exception as e:
            st.error(f"Error actualizando estado: {e}")

    def generar_certificado_automatico(self, id_inscripcion: int):
        """Genera certificado automáticamente cuando el estado académico es 'Aprobado'"""
        try:
            # Obtener datos de la inscripción
            query_inscripcion = """
                SELECT
                    it.cedula_estudiante,
                    it.id_taller,
                    t.nombre_taller,
                    CONCAT(p.nombre, ' ', p.apellido) as nombre_facilitador,
                    t.fecha_inicio,
                    t.fecha_fin,
                    t.duracion_horas
                FROM inscripciones_talleres it
                LEFT JOIN taller t ON it.id_taller = t.id_taller
                LEFT JOIN profesor pr ON t.cedula_profesor = pr.cedula_profesor
                LEFT JOIN persona p ON pr.cedula_profesor = p.cedula
                WHERE it.id_inscripcion = %s
            """

            datos = execute_query(query_inscripcion, (id_inscripcion,))

            if datos:
                inscripcion = datos[0]

                # Preparar datos para el certificado usando el formato esperado
                taller_info = {
                    'id': inscripcion['id_taller'],
                    'nombre': inscripcion['nombre_taller'],
                    'fecha_culminacion': inscripcion['fecha_fin'] or datetime.now().date(),
                    'duracion_horas': inscripcion['duracion_horas']
                }

                # Generar certificado usando el gestor
                resultado_cert = self.gestor_cert.generar_certificado_interno(taller_info)

                if resultado_cert.get('success'):
                    st.success("🎓 Certificado generado automáticamente")
                    # Actualizar estado del certificado en la inscripción si es necesario
                else:
                    st.warning("⚠️ El certificado se marcará como 'Listo para Generar' - Revisa el módulo de certificados")

        except Exception as e:
            st.error(f"Error en generación automática de certificado: {e}")

    def mostrar_detalles_inscripcion(self, inscripcion: Dict):
        """Muestra detalles completos de una inscripción"""
        st.markdown("**📄 Detalles de la Inscripción**")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Información General:**")
            st.text(f"ID Inscripción: {inscripcion['id_inscripcion']}")
            st.text(f"Fecha Creación: {inscripcion['fecha_creacion']}")
            st.text(f"Última Modificación: {inscripcion['fecha_cambio']}")

        with col2:
            st.markdown("**Estados:**")
            st.text(f"Estado Estudiante: {inscripcion['estado_estudiante']}")
            st.text(f"Estado Académico: {inscripcion['estado_academico'] or 'No definido'}")

        if inscripcion.get('observaciones'):
            st.markdown("**Observaciones:**")
            st.text_area("", value=inscripcion['observaciones'], disabled=True, height=100)


# Función principal para el módulo
def gestion_inscripciones_facilitador_main():
    """Punto de entrada principal del módulo"""
    app = GestionInscripcionesFacilitador()
    app.main()

if __name__ == "__main__":
    gestion_inscripciones_facilitador_main()