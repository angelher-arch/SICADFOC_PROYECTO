#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modulo_informes.py - Módulo de Informes y Reportes para SICADFOC 2026
Constructor de reportes inteligente con filtros avanzados
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from seguridad import tiene_permiso, SeguridadFOC26
from styles import aplicar_estilos_sicad, crear_tabla_configuracion

def reportes(db=None):
    """Módulo principal de informes y reportes con constructor inteligente"""
    
    try:
        # Aplicar estilos dinámicos
        aplicar_estilos_sicad()
        
        # Verificar conexión antes de procesar
        from database import db_manager
        if not db_manager.test_connection().get('status', False):
            st.error("❌ Error de conexión a la base de datos")
            st.warning("Por favor, recargue la página e intente nuevamente.")
            return
        
        # Usar arquitectura centralizada de conexión
        if db is None:
            from database import db_manager
            db = db_manager.get_connection()
            
            if not db:
                st.error("Error de conexión a la base de datos")
                return
        
        st.title("📊 Informes y Reportes")
        st.markdown("### Constructor de Reportes Inteligente")
        
        # Validar acceso - Admin tiene acceso total
        rol_usuario = st.session_state.user_role
        
        if SeguridadFOC26.is_admin():
            pass
        elif not tiene_permiso(rol_usuario, 'Informes', 'Consultar'):
            st.error("Acceso denegado. No tienes permisos para consultar informes.")
            return
        
        # Filtros principales del constructor de reportes
        st.markdown("#### 🎛️ Filtros del Reporte")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Selector de Módulo
            modulo_seleccionado = st.selectbox(
                "Módulo",
                ["Estudiantes", "Profesores", "Formación Complementaria", "Usuarios"],
                key="modulo_reporte"
            )
        
        with col2:
            # Tipo de Reporte
            tipo_reporte = st.selectbox(
                "Tipo de Reporte",
                ["Resumen Estadístico", "Listado Detallado", "Actividad por Rol"],
                key="tipo_reporte"
            )
        
        with col3:
            # Rango de Fechas
            fecha_inicio = st.date_input(
                "Fecha Inicio",
                value=date.today().replace(day=1),
                key="fecha_inicio"
            )
            fecha_fin = st.date_input(
                "Fecha Fin", 
                value=date.today(),
                key="fecha_fin"
            )
        
        st.markdown("---")
        
        # Botón para generar reporte
        if st.button("🔍 Generar Reporte", type="primary", use_container_width=True):
            with st.spinner("Generando reporte..."):
                try:
                    df = generar_reporte_inteligente(modulo_seleccionado, tipo_reporte, fecha_inicio, fecha_fin, db)
                    
                    if df is not None and not df.empty:
                        st.success(f"✅ Reporte generado: {len(df)} registros encontrados")
                        
                        # Mostrar datos con estilos dinámicos
                        st.markdown("#### 📋 Resultados del Reporte")
                        st.dataframe(df, use_container_width=True)
                        
                        # Botón de exportación
                        col_export1, col_export2, col_export3 = st.columns([1, 2, 1])
                        with col_export2:
                            if st.button("📥 Exportar a CSV", use_container_width=True):
                                csv = df.to_csv(index=False)
                                st.download_button(
                                    label="⬇️ Descargar CSV",
                                    data=csv,
                                    file_name=f"reporte_{modulo_seleccionado}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv"
                                )
                    else:
                        st.warning("⚠️ No se encontraron datos para los filtros seleccionados")
                        
                except Exception as e:
                    st.error("❌ Error generando reporte")
                    st.warning("Intente nuevamente con otros filtros")
        
    except Exception as e:
        st.error("❌ Error en el módulo de reportes")
        st.warning("Recargue la página e intente nuevamente")

def generar_reporte_inteligente(modulo, tipo_reporte, fecha_inicio, fecha_fin, db):
    """Genera reporte según los filtros seleccionados"""
    
    try:
        # Convertir fechas a string para SQL
        fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
        fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')
        
        # Construir consulta según módulo y tipo
        if modulo == "Estudiantes":
            if tipo_reporte == "Resumen Estadístico":
                query = """
                SELECT 
                    COUNT(*) as total_estudiantes,
                    COUNT(CASE WHEN e.estado_registro = 'Activo' THEN 1 END) as activos,
                    COUNT(CASE WHEN e.estado_registro = 'Inactivo' THEN 1 END) as inactivos,
                    COUNT(DISTINCT e.id_carrera) as carreras_distintas
                FROM estudiante e
                WHERE e.fecha_registro BETWEEN %s AND %s
                """
                params = (fecha_inicio_str, fecha_fin_str)
                
            elif tipo_reporte == "Listado Detallado":
                query = """
                SELECT 
                    p.cedula,
                    p.nombre,
                    p.apellido,
                    c.nombre_carrera,
                    e.semestre_actual,
                    e.estado_registro,
                    e.fecha_registro
                FROM estudiante e
                JOIN persona p ON e.cedula_estudiante = p.cedula
                LEFT JOIN carrera c ON e.id_carrera = c.id_carrera
                WHERE e.fecha_registro BETWEEN %s AND %s
                ORDER BY e.fecha_registro DESC
                """
                params = (fecha_inicio_str, fecha_fin_str)
                
            else:  # Actividad por Rol
                query = """
                SELECT 
                    u.rol,
                    COUNT(*) as total,
                    COUNT(CASE WHEN u.activo THEN 1 END) as activos
                FROM usuarios u
                WHERE u.rol = 'Estudiante'
                AND u.fecha_registro BETWEEN %s AND %s
                GROUP BY u.rol
                """
                params = (fecha_inicio_str, fecha_fin_str)
        
        elif modulo == "Profesores":
            if tipo_reporte == "Resumen Estadístico":
                query = """
                SELECT 
                    COUNT(*) as total_profesores,
                    COUNT(CASE WHEN p.estado = 'Activo' THEN 1 END) as activos,
                    COUNT(CASE WHEN p.estado = 'Inactivo' THEN 1 END) as inactivos
                FROM profesores p
                WHERE p.fecha_registro BETWEEN %s AND %s
                """
                params = (fecha_inicio_str, fecha_fin_str)
                
            elif tipo_reporte == "Listado Detallado":
                query = """
                SELECT 
                    p.cedula,
                    p.nombre,
                    p.apellido,
                    p.especialidad,
                    p.estado,
                    p.fecha_registro
                FROM profesores p
                WHERE p.fecha_registro BETWEEN %s AND %s
                ORDER BY p.fecha_registro DESC
                """
                params = (fecha_inicio_str, fecha_fin_str)
                
            else:  # Actividad por Rol
                query = """
                SELECT 
                    u.rol,
                    COUNT(*) as total,
                    COUNT(CASE WHEN u.activo THEN 1 END) as activos
                FROM usuarios u
                WHERE u.rol = 'Profesor'
                AND u.fecha_registro BETWEEN %s AND %s
                GROUP BY u.rol
                """
                params = (fecha_inicio_str, fecha_fin_str)
        
        elif modulo == "Formación Complementaria":
            if tipo_reporte == "Resumen Estadístico":
                query = """
                SELECT 
                    COUNT(*) as total_talleres,
                    COUNT(CASE WHEN fc.estado = 'Activo' THEN 1 END) as activos,
                    COUNT(CASE WHEN fc.estado = 'Inactivo' THEN 1 END) as inactivos,
                    COUNT(DISTINCT fc.id_taller) as talleres_distintos
                FROM formacion_complementaria fc
                WHERE fc.fecha_creacion BETWEEN %s AND %s
                """
                params = (fecha_inicio_str, fecha_fin_str)
                
            elif tipo_reporte == "Listado Detallado":
                query = """
                SELECT 
                    fc.codigo_certificado,
                    t.nombre_taller,
                    p.nombre,
                    p.apellido,
                    fc.estado,
                    fc.fecha_creacion
                FROM formacion_complementaria fc
                JOIN talleres t ON fc.id_taller = t.id_taller
                JOIN persona p ON fc.cedula_estudiante = p.cedula
                WHERE fc.fecha_creacion BETWEEN %s AND %s
                ORDER BY fc.fecha_creacion DESC
                """
                params = (fecha_inicio_str, fecha_fin_str)
                
            else:  # Actividad por Rol
                query = """
                SELECT 
                    'Estudiante' as rol,
                    COUNT(*) as total
                FROM formacion_complementaria fc
                WHERE fc.fecha_creacion BETWEEN %s AND %s
                """
                params = (fecha_inicio_str, fecha_fin_str)
        
        else:  # Usuarios
            if tipo_reporte == "Resumen Estadístico":
                query = """
                SELECT 
                    COUNT(*) as total_usuarios,
                    COUNT(CASE WHEN u.activo THEN 1 END) as activos,
                    COUNT(CASE WHEN NOT u.activo THEN 1 END) as inactivos,
                    COUNT(DISTINCT u.rol) as roles_distintos
                FROM usuarios u
                WHERE u.fecha_registro BETWEEN %s AND %s
                """
                params = (fecha_inicio_str, fecha_fin_str)
                
            elif tipo_reporte == "Listado Detallado":
                query = """
                SELECT 
                    u.cedula_usuario,
                    u.login_usuario,
                    u.rol,
                    CASE WHEN u.activo THEN 'Activo' ELSE 'Inactivo' END as estado,
                    u.fecha_registro
                FROM usuarios u
                WHERE u.fecha_registro BETWEEN %s AND %s
                ORDER BY u.fecha_registro DESC
                """
                params = (fecha_inicio_str, fecha_fin_str)
                
            else:  # Actividad por Rol
                query = """
                SELECT 
                    u.rol,
                    COUNT(*) as total,
                    COUNT(CASE WHEN u.activo THEN 1 END) as activos
                FROM usuarios u
                WHERE u.fecha_registro BETWEEN %s AND %s
                GROUP BY u.rol
                ORDER BY total DESC
                """
                params = (fecha_inicio_str, fecha_fin_str)
        
        # Ejecutar consulta y devolver DataFrame
        from database import execute_query
        resultado = execute_query(query, params)
        
        if resultado and len(resultado) > 0:
            return pd.DataFrame(resultado)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        return None
