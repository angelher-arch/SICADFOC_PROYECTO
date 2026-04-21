#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Formación Complementaria - SICADFOC 2026
Gestión de talleres y formación complementaria
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date

def modulo_formacion_complementaria(db=None):
    """Módulo principal de formación complementaria"""
    
    try:
        if db is None:
            from conexion_simple_corregido import ConexionSimple
            db = ConexionSimple()
            if not db.conectar():
                st.error("Error de conexión a la base de datos")
                return
        
        st.title("Formación Complementaria")
        st.header("Gestión de Talleres")
        
        # Validar acceso usando sistema de autorización dinámica
        from seguridad import tiene_permiso, SeguridadFOC26
        rol_usuario = SeguridadFOC26.get_user_role()
        
        if not tiene_permiso(rol_usuario, 'Formación Complementaria', 'Consultar'):
            st.error("Acceso denegado. No tienes permisos para consultar formación complementaria.")
            return
        
        # Tabs según rol
        if SeguridadFOC26.is_admin() or SeguridadFOC26.is_profesor():
            tab1, tab2, tab3 = st.tabs(["Talleres", "Inscripciones", "Reportes"])
            
            with tab1:
                gestion_talleres(db, rol_usuario)
            with tab2:
                gestion_inscripciones(db, rol_usuario)
            with tab3:
                reportes_formacion(db, rol_usuario)
                
        elif SeguridadFOC26.is_estudiante():
            tab1, tab2 = st.tabs(["Talleres Disponibles", "Mis Inscripciones"])
            
            with tab1:
                talleres_disponibles(db, rol_usuario)
            with tab2:
                mis_inscripciones(db, rol_usuario)
        
    except Exception as e:
        st.error(f"Error en módulo de formación complementaria: {e}")

def gestion_talleres(db, rol_usuario):
    """Gestión de talleres para admin/profesor"""
    
    st.subheader("Gestión de Talleres")
    
    # Validar permisos para crear talleres
    if not tiene_permiso(rol_usuario, 'Formación Complementaria', 'Crear'):
        st.warning("No tienes permisos para crear talleres.")
        return
    
    # Formulario para crear nuevo taller
    with st.form("form_nuevo_taller"):
        st.markdown("### Nuevo Taller")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_taller = st.text_input("Nombre del Taller*", placeholder="Introducción a Python")
            descripcion = st.text_area("Descripción*", placeholder="Taller básico de programación en Python")
            fecha_inicio = st.date_input("Fecha de Inicio*", value=date.today())
            fecha_fin = st.date_input("Fecha de Fin*", value=date.today())
            
        with col2:
            cupo_maximo = st.number_input("Cupo Máximo*", min_value=1, value=30)
            estado = st.selectbox("Estado", ["Activo", "Inactivo", "Próximo"])
            
        submit_taller = st.form_submit_button("Crear Taller")
        
        if submit_taller:
            if nombre_taller and descripcion:
                # Insertar nuevo taller
                query = """
                INSERT INTO formacion_complementaria 
                (nombre_taller, descripcion, fecha_inicio, fecha_fin, cupo_maximo, estado, id_profesor)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                # Obtener ID del profesor actual (simplificado)
                id_profesor = 1  # Debería obtenerse del usuario logueado
                
                try:
                    from utilidades_transaccion import ejecutar_transaccion
                    
                    resultado = ejecutar_transaccion(
                        db,
                        """
                        INSERT INTO formacion_complementaria 
                        (nombre_taller, descripcion, fecha_inicio, fecha_fin, cupo_maximo, estado, id_profesor)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (nombre_taller, descripcion, fecha_inicio, fecha_fin, 
                         cupo_maximo, estado, id_profesor),
                        "INSERT"
                    )
                    
                    if resultado['exito']:
                        st.success("Taller creado exitosamente")
                        st.rerun()
                    else:
                        st.error(f"Error al crear taller: {resultado['error']}")
                except Exception as e:
                    st.error(f"Error al crear taller: {e}")
            else:
                st.error("Complete todos los campos obligatorios")
    
    # Listado de talleres existentes
    st.markdown("---")
    st.subheader("Talleres Existentes")
    
    query_talleres = """
    SELECT fc.*, p.nombre as profesor_nombre, p.apellido as profesor_apellido
    FROM formacion_complementaria fc
    LEFT JOIN persona p ON fc.id_profesor = p.id
    ORDER BY fc.fecha_inicio DESC
    """
    
    resultado = db.ejecutar_consulta(query_talleres)
    
    if resultado:
        df = pd.DataFrame(resultado)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay talleres registrados")

def talleres_disponibles(db, rol_usuario):
    """Mostrar talleres disponibles para estudiantes"""
    
    st.subheader("Talleres Disponibles")
    
    query = """
    SELECT fc.*, p.nombre as profesor_nombre, p.apellido as profesor_apellido
    FROM formacion_complementaria fc
    LEFT JOIN persona p ON fc.id_profesor = p.id
    WHERE fc.estado = 'Activo' AND fc.fecha_fin >= CURRENT_DATE
    ORDER BY fc.fecha_inicio ASC
    """
    
    resultado = db.ejecutar_consulta(query)
    
    if resultado:
        for taller in resultado:
            with st.expander(f"{taller['nombre_taller']} - {taller['profesor_nombre']} {taller['profesor_apellido']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Descripción:** {taller['descripcion']}")
                    st.write(f"**Fecha:** {taller['fecha_inicio']} al {taller['fecha_fin']}")
                    st.write(f"**Cupo:** {taller['cupo_maximo']} personas")
                
                with col2:
                    # Aplicar autorización dinámica para inscribirse
                    if tiene_permiso(rol_usuario, 'Formación Complementaria', 'Inscribir'):
                        if st.button("Inscribirse", key=f"inscribir_{taller['id']}"):
                            inscribir_taller(db, taller['id'], rol_usuario)
                    else:
                        st.button("Inscribirse", key=f"inscribir_{taller['id']}", disabled=True,
                                 help="No tienes permisos para inscribirte en talleres")
    else:
        st.info("No hay talleres disponibles en este momento")

def inscribir_taller(db, id_taller, rol_usuario):
    """Incribir estudiante en taller"""
    
    # Validar permisos de inscripción
    if not tiene_permiso(rol_usuario, 'Formación Complementaria', 'Inscribir'):
        st.error("Acceso denegado. No tienes permisos para inscribirte en talleres.")
        return
    
    try:
        # Obtener ID del estudiante
        from seguridad import SeguridadFOC26
        cedula_estudiante = SeguridadFOC26.get_user_cedula()
        
        query_usuario = "SELECT id FROM usuario WHERE cedula_usuario = %s"
        resultado_usuario = db.ejecutar_consulta(query_usuario, (cedula_estudiante,))
        
        if resultado_usuario:
            id_estudiante = resultado_usuario[0]['id']
            
            # Verificar si ya está inscrito
            query_verificar = """
            SELECT COUNT(*) as inscrito 
            FROM inscripcion 
            WHERE id_estudiante = %s AND id_formacion = %s
            """
            
            resultado_verificar = db.ejecutar_consulta(query_verificar, (id_estudiante, id_taller))
            
            if resultado_verificar[0]['inscrito'] == 0:
                # Realizar inscripción
                query_inscribir = """
                INSERT INTO inscripcion (id_estudiante, id_formacion, fecha_inscripcion, estado_inscripcion)
                VALUES (%s, %s, CURRENT_DATE, 'Activa')
                """
                
                db.ejecutar_consulta(query_inscribir, (id_estudiante, id_taller))
                st.success("Inscripción realizada exitosamente")
                st.rerun()
            else:
                st.warning("Ya estás inscrito en este taller")
        else:
            st.error("No se pudo encontrar tu información de usuario")
            
    except Exception as e:
        st.error(f"Error al realizar inscripción: {e}")

def mis_inscripciones(db, rol_usuario):
    """Mostrar inscripciones del estudiante actual"""
    
    st.subheader("Mis Inscripciones")
    
    try:
        from seguridad import SeguridadFOC26
        cedula_estudiante = SeguridadFOC26.get_user_cedula()
        
        query = """
        SELECT fc.*, i.fecha_inscripcion, i.estado_inscripcion
        FROM inscripcion i
        JOIN formacion_complementaria fc ON i.id_formacion = fc.id
        JOIN usuario u ON i.id_estudiante = u.id
        WHERE u.cedula_usuario = %s
        ORDER BY i.fecha_inscripcion DESC
        """
        
        resultado = db.ejecutar_consulta(query, (cedula_estudiante,))
        
        if resultado:
            df = pd.DataFrame(resultado)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No tienes inscripciones registradas")
            
    except Exception as e:
        st.error(f"Error al consultar inscripciones: {e}")

def gestion_inscripciones(db, rol_usuario):
    """Gestión de inscripciones para admin/profesor"""
    
    st.subheader("Gestión de Inscripciones")
    
    query = """
    SELECT i.*, fc.nombre_taller, u.cedula_usuario, 
           p.nombre as estudiante_nombre, p.apellido as estudiante_apellido
    FROM inscripcion i
    JOIN formacion_complementaria fc ON i.id_formacion = fc.id
    JOIN usuario u ON i.id_estudiante = u.id
    JOIN persona p ON u.cedula_usuario = p.cedula
    ORDER BY i.fecha_inscripcion DESC
    """
    
    resultado = db.ejecutar_consulta(query)
    
    if resultado:
        df = pd.DataFrame(resultado)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay inscripciones registradas")

def reportes_formacion(db, rol_usuario):
    """Reportes de formación complementaria"""
    
    st.subheader("Reportes")
    
    # Estadísticas básicas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_talleres = db.ejecutar_consulta("SELECT COUNT(*) as total FROM formacion_complementaria")
        if total_talleres:
            st.metric("Total Talleres", total_talleres[0]['total'])
    
    with col2:
        talleres_activos = db.ejecutar_consulta("SELECT COUNT(*) as total FROM formacion_complementaria WHERE estado = 'Activo'")
        if talleres_activos:
            st.metric("Talleres Activos", talleres_activos[0]['total'])
    
    with col3:
        total_inscripciones = db.ejecutar_consulta("SELECT COUNT(*) as total FROM inscripcion")
        if total_inscripciones:
            st.metric("Total Inscripciones", total_inscripciones[0]['total'])
    
    # Gráfico de talleres por estado
    st.markdown("---")
    st.subheader("Talleres por Estado")
    
    query_estados = """
    SELECT estado, COUNT(*) as cantidad
    FROM formacion_complementaria
    GROUP BY estado
    ORDER BY cantidad DESC
    """
    
    resultado_estados = db.ejecutar_consulta(query_estados)
    
    if resultado_estados:
        df_estados = pd.DataFrame(resultado_estados)
        st.bar_chart(df_estados.set_index('estado')['cantidad'])

if __name__ == "__main__":
    modulo_formacion_complementaria()
