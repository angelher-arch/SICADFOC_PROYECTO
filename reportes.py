#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modulo_informes.py - Módulo de Informes y Reportes para SICADFOC 2026
Acceso total para administradores con permisos simplificados
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from seguridad import tiene_permiso, SeguridadFOC26

def reportes(db=None):
    """Módulo principal de informes y reportes con manejo robusto de errores"""
    
    try:
        # Verificar conexión antes de procesar
        from database import db_manager
        if not db_manager.test_connection().get('status', False):
            st.error("❌ Error de conexión antes de generar reportes")
            st.warning("Por favor, recargue la página e intente nuevamente.")
            return
        
        # Usar arquitectura centralizada de conexión
        if db is None:
            from database import db_manager
            db = db_manager.get_connection()
            
            # Verificar estado de conexión
            if not db:
                from database import db_manager
                status = db_manager.test_connection()
                st.error(f"Error de conexión a la base de datos: {status.get('message', 'Error desconocido')}")
                return
        
        st.title("Informes y Reportes")
        st.header("Panel de Reportes del Sistema")
        
        # Validar acceso - Admin tiene acceso total
        rol_usuario = st.session_state.user_role
        
        # ACCESO SIMPLIFICADO: Admin acceso total, otros según permisos
        if SeguridadFOC26.is_admin():
            # Admin tiene acceso irrestricto
            pass
        elif not tiene_permiso(rol_usuario, 'Informes', 'Consultar'):
            st.error("Acceso denegado. No tienes permisos para consultar informes.")
            return
        
        # Vista única sin tabs según rol
        if SeguridadFOC26.is_admin():
            st.markdown("### Reporte General")
            reporte_general(db)
            
            st.markdown("---")
            st.markdown("### Estudiantes")
            reporte_estudiantes(db)
            
            st.markdown("---")
            st.markdown("### Profesores")
            reporte_profesores(db)
            
            st.markdown("---")
            st.markdown("### Formación")
            reporte_formacion(db)
                
        elif SeguridadFOC26.is_profesor():
            st.markdown("### Mis Estudiantes")
            reporte_mis_estudiantes(db, rol_usuario)
            
            st.markdown("---")
            st.markdown("### Mis Talleres")
            reporte_mis_talleres(db, rol_usuario)
                
        elif SeguridadFOC26.is_estudiante():
            st.markdown("### Mi Progreso")
            reporte_mi_progreso(db, rol_usuario)
            st.markdown("### Mis Certificados")
            reporte_mis_certificados(db, rol_usuario)
        
    except Exception as e:
        st.error(f"Error en módulo de informes: {e}")

def reporte_general(db):
    """Reporte general del sistema"""
    st.subheader("Reporte General del Sistema")
    
    try:
        # Usar motor central unificado para estadísticas
        from formacion_complementaria import motor_formacion
        
        # Obtener estadísticas generales usando motor central
        estadisticas = motor_formacion.obtener_estadisticas_generales()
        
        # Estadísticas generales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Usuarios", estadisticas.get('total_usuarios', 0))
        
        with col2:
            st.metric("Estudiantes", estadisticas.get('total_estudiantes', 0))
        
        with col3:
            st.metric("Profesores", estadisticas.get('total_profesores', 0))
        
        with col4:
            st.metric("Formaciones", estadisticas.get('total_formaciones', 0))
        
        # Tabla de usuarios por rol usando motor central
        st.markdown("### Usuarios por Rol")
        usuarios_por_rol = motor_formacion.obtener_usuarios_por_rol()
        
        if usuarios_por_rol['success']:
            df_roles = pd.DataFrame(usuarios_por_rol['data'])
            st.dataframe(df_roles, use_container_width=True)
        else:
            st.error("Error al obtener usuarios por rol")
        
    except Exception as e:
        st.error(f"Error generando reporte general: {e}")

def reporte_estudiantes(db):
    """Reporte de estudiantes"""
    st.subheader("Reporte de Estudiantes")
    
    try:
        # Usar execute_query en lugar de cursor directo
        from database import execute_query
        
        # Listado completo de estudiantes
        query = """
        SELECT p.cedula, p.nombre, p.apellido, e.carrera, e.semestre_formacion,
               u.login_usuario, u.rol, u.activo
        FROM persona p
        JOIN usuarios u ON p.cedula = u.cedula_usuario
        LEFT JOIN estudiante e ON p.cedula = e.cedula_estudiante
        WHERE u.rol = 'Estudiante'
        ORDER BY p.apellido, p.nombre
        """
        
        estudiantes = execute_query(query)
        
        if estudiantes:
            df = pd.DataFrame(estudiantes)
            st.dataframe(df, use_container_width=True)
            
            # Opciones de exportación
            if st.button("Exportar a CSV", key="exportar_estudiantes_csv"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Descargar CSV",
                    data=csv,
                    file_name=f"estudiantes_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No hay estudiantes registrados")
            
    except Exception as e:
        st.error(f"Error generando reporte de estudiantes: {e}")

def reporte_profesores(db):
    """Reporte de profesores"""
    st.subheader("Reporte de Profesores")
    
    try:
        # Usar execute_query en lugar de cursor directo
        from database import execute_query
        
        # Listado completo de profesores
        query = """
        SELECT p.cedula, p.nombre, p.apellido, pr.especialidad,
               u.login_usuario, u.rol, u.activo
        FROM persona p
        JOIN usuarios u ON p.cedula = u.cedula_usuario
        LEFT JOIN profesor pr ON p.cedula = pr.cedula_profesor
        WHERE u.rol = 'Profesor'
        ORDER BY p.apellido, p.nombre
        """
        
        profesores = execute_query(query)
        
        if profesores:
            df = pd.DataFrame(profesores)
            st.dataframe(df, use_container_width=True)
            
            # Opciones de exportación
            if st.button("Exportar a CSV", key="exportar_profesores_csv"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Descargar CSV",
                    data=csv,
                    file_name=f"profesores_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No hay profesores registrados")
            
    except Exception as e:
        st.error(f"Error generando reporte de profesores: {e}")

def reporte_formacion(db):
    """Reporte de formación complementaria"""
    st.subheader("Reporte de Formación Complementaria")
    
    try:
        # Usar execute_query en lugar de cursor directo
        from database import execute_query
        
        # Estadísticas de talleres
        col1, col2, col3 = st.columns(3)
        
        with col1:
            talleres_activos = execute_query("""
                SELECT COUNT(*) as total FROM taller 
                WHERE estado = 'Activo'
            """)
            if talleres_activos:
                st.metric("Talleres Activos", talleres_activos[0]['total'])
        
        with col2:
            total_inscripciones = execute_query("""
                SELECT COUNT(*) as total FROM inscripcion
            """)
            if total_inscripciones:
                st.metric("Total Inscripciones", total_inscripciones[0]['total'])
        
        with col3:
            talleres_completados = execute_query("""
                SELECT COUNT(*) as total FROM taller 
                WHERE estado = 'Completado'
            """)
            if talleres_completados:
                st.metric("Talleres Completados", talleres_completados[0]['total'])
        
        # Listado de talleres
        st.markdown("### Listado de Talleres")
        talleres = execute_query("""
            SELECT id, nombre_taller, descripcion, estado, cupo_maximo,
                   fecha_inicio, fecha_fin
            FROM taller
            ORDER BY fecha_inicio DESC
        """)
        
        if talleres:
            df = pd.DataFrame(talleres)
            st.dataframe(df, use_container_width=True)
            
            # Opciones de exportación
            if st.button("Exportar Talleres a CSV", key="exportar_talleres_csv"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Descargar CSV",
                    data=csv,
                    file_name=f"talleres_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No hay talleres registrados")
            
    except Exception as e:
        st.error(f"Error generando reporte de formación: {e}")

def reporte_mis_estudiantes(db, rol_usuario):
    """Reporte de estudiantes asignados a un profesor"""
    st.subheader("Mis Estudiantes")
    
    try:
        # Usar execute_query en lugar de cursor directo
        from database import execute_query
        
        cedula_profesor = SeguridadFOC26.get_user_cedula()
        
        # Estudiantes asignados al profesor
        query = """
        SELECT p.cedula, p.nombre, p.apellido, e.carrera, e.semestre_formacion
        FROM persona p
        JOIN estudiante e ON p.cedula = e.cedula_estudiante
        WHERE e.id_profesor = (
            SELECT id FROM profesor WHERE cedula_profesor = %s
        )
        ORDER BY p.apellido, p.nombre
        """
        
        estudiantes = execute_query(query, (cedula_profesor,))
        
        if estudiantes:
            df = pd.DataFrame(estudiantes)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No tienes estudiantes asignados")
            
    except Exception as e:
        st.error(f"Error generando reporte de mis estudiantes: {e}")

def reporte_mis_talleres(db, rol_usuario):
    """Reporte de talleres dictados por un profesor"""
    st.subheader("Mis Talleres")
    
    try:
        # Usar execute_query en lugar de cursor directo
        from database import execute_query
        
        cedula_profesor = SeguridadFOC26.get_user_cedula()
        
        # Talleres del profesor
        query = """
        SELECT id, nombre_taller, descripcion, estado, cupo_maximo,
               fecha_inicio, fecha_fin
        FROM taller
        WHERE id_profesor = (
            SELECT id FROM profesor WHERE cedula_profesor = %s
        )
        ORDER BY fecha_inicio DESC
        """
        
        talleres = execute_query(query, (cedula_profesor,))
        
        if talleres:
            df = pd.DataFrame(talleres)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No tienes talleres asignados")
            
    except Exception as e:
        st.error(f"Error generando reporte de mis talleres: {e}")

def reporte_mi_progreso(db, rol_usuario):
    """Reporte de progreso del estudiante"""
    st.subheader("Mi Progreso Académico")
    
    try:
        # Usar execute_query en lugar de cursor directo
        from database import execute_query
        
        cedula_estudiante = SeguridadFOC26.get_user_cedula()
        
        # Datos del estudiante
        query_estudiante = """
        SELECT p.cedula, p.nombre, p.apellido, e.carrera, e.semestre_formacion
        FROM persona p
        JOIN estudiante e ON p.cedula = e.cedula_estudiante
        WHERE p.cedula = %s
        """
        
        estudiante = execute_query(query_estudiante, (cedula_estudiante,))
        
        if estudiante:
            est_data = estudiante[0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Nombre:** {est_data['nombre']} {est_data['apellido']}")
                st.write(f"**Cédula:** {est_data['cedula']}")
            with col2:
                st.write(f"**Carrera:** {est_data['carrera']}")
                st.write(f"**Semestre:** {est_data['semestre_formacion']}")
            
            # Inscripciones a talleres
            st.markdown("### Mis Inscripciones a Talleres")
            query_inscripciones = """
            SELECT t.nombre_taller, t.estado, i.fecha_inscripcion
            FROM inscripcion i
            JOIN taller t ON i.id_taller = t.id
            WHERE i.cedula_estudiante = %s
            ORDER BY i.fecha_inscripcion DESC
            """
            
            inscripciones = execute_query(query_inscripciones, (cedula_estudiante,))
            
            if inscripciones:
                df = pd.DataFrame(inscripciones)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No tienes inscripciones a talleres")
        else:
            st.error("No se encontraron tus datos de estudiante")
            
    except Exception as e:
        # DETECCIÓN Y RECUPERACIÓN AUTOMÁTICA
        print(f"❌ Error generando reporte de mi progreso: {e}")
        st.error("❌ Ocurrió un error inesperado al generar reporte de progreso")
        st.info("🔄 El sistema intentará recuperar la conexión automáticamente...")
        
        # Marcar para recuperación en siguiente interacción
        st.session_state.transaccion_abortada = True
        st.session_state.error_reporte_progreso = str(e)

def reporte_mis_certificados(db, rol_usuario):
    """Reporte de certificados del estudiante"""
    st.subheader("Mis Certificados")
    
    try:
        # Usar execute_query en lugar de cursor directo
        from database import execute_query
        
        cedula_estudiante = SeguridadFOC26.get_user_cedula()
        
        # Certificados del estudiante
        query = """
        SELECT id, nombre_taller, fecha_culminacion, tipo, estado
        FROM certificaciones
        WHERE cedula_estudiante = %s
        ORDER BY fecha_culminacion DESC
        """
        
        certificados = execute_query(query, (cedula_estudiante,))
        
        if certificados:
            df = pd.DataFrame(certificados)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No tienes certificados registrados")
            
    except Exception as e:
        st.error(f"Error generando reporte de mis certificados: {e}")
