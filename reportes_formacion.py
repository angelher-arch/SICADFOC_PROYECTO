#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reportes_formacion.py - Módulo de Reportes de Formación Complementaria
SICADFOC 2026 - Instituto Universitario Jesus Obrero
Módulo para generar reportes específicos de formación complementaria
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime, date
from typing import Dict, List, Optional, Any

# IMPORTACIONES LOCALES AL MÓDULO
try:
    from seguridad import tiene_permiso, SeguridadFOC26
    from database import motor_central
except ImportError as e:
    st.error(f"Error importando módulos locales: {e}")
    sys.exit(1)

class ReportesFormacion:
    """Clase para generar reportes de formación complementaria"""
    
    def __init__(self):
        """Inicialización del motor de reportes"""
        self.motor = motor_central
    
    def obtener_estadisticas_generales(self) -> Dict[str, Any]:
        """Obtener estadísticas generales de formación complementaria"""
        try:
            stats = {}
            
            # Total de talleres
            query_talleres = "SELECT COUNT(*) as total FROM taller WHERE estado = 'activo'"
            resultado_talleres = self.motor.ejecutar_consulta_personalizada(query_talleres)
            stats['total_talleres'] = resultado_talleres.get('data', [{}])[0].get('total', 0) if resultado_talleres.get('success') else 0
            
            # Total de formaciones
            query_formaciones = "SELECT COUNT(*) as total FROM formacion_complementaria"
            resultado_formaciones = self.motor.ejecutar_consulta_personalizada(query_formaciones)
            stats['total_formaciones'] = resultado_formaciones.get('data', [{}])[0].get('total', 0) if resultado_formaciones.get('success') else 0
            
            # Total de estudiantes inscritos
            query_inscritos = """
            SELECT COUNT(DISTINCT i.cedula_estudiante) as total 
            FROM inscripcion i 
            WHERE i.estado IN ('inscrito', 'en_curso')
            """
            resultado_inscritos = self.motor.ejecutar_consulta_personalizada(query_inscritos)
            stats['total_inscritos'] = resultado_inscritos.get('data', [{}])[0].get('total', 0) if resultado_inscritos.get('success') else 0
            
            return stats
            
        except Exception as e:
            st.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def obtener_talleres_populares(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Obtener los talleres con más inscripciones"""
        try:
            query = """
            SELECT 
                fc.nombre as taller,
                COUNT(i.id_inscripcion) as total_inscripciones,
                t.capacidad_maxima,
                ROUND((COUNT(i.id_inscripcion) * 100.0 / t.capacidad_maxima), 2) as porcentaje_ocupacion
            FROM formacion_complementaria fc
            LEFT JOIN taller t ON fc.id_taller = t.id_taller
            LEFT JOIN inscripcion i ON fc.id_formacion = i.id_formacion
            WHERE t.estado = 'activo'
            GROUP BY fc.id_formacion, fc.nombre, t.capacidad_maxima
            ORDER BY total_inscripciones DESC
            LIMIT %s
            """
            
            resultado = self.motor.ejecutar_consulta_personalizada(query, (limite,))
            
            if resultado.get('success') and resultado.get('data'):
                return resultado['data']
            return []
            
        except Exception as e:
            st.error(f"Error obteniendo talleres populares: {e}")
            return []
    
    def obtener_progreso_estudiantes(self) -> List[Dict[str, Any]]:
        """Obtener progreso de estudiantes en talleres"""
        try:
            query = """
            SELECT 
                p.nombre,
                p.apellido,
                COUNT(i.id_inscripcion) as total_talleres,
                COUNT(CASE WHEN i.estado = 'completado' THEN 1 END) as talleres_completados,
                COUNT(CASE WHEN i.estado = 'en_curso' THEN 1 END) as talleres_en_curso,
                AVG(i.calificacion) as promedio_calificacion
            FROM inscripcion i
            LEFT JOIN estudiante e ON i.cedula_estudiante = e.cedula_estudiante
            LEFT JOIN persona p ON e.cedula_estudiante = p.cedula
            WHERE i.estado IN ('inscrito', 'en_curso', 'completado')
            GROUP BY p.cedula, p.nombre, p.apellido
            ORDER BY total_talleres DESC
            LIMIT 20
            """
            
            resultado = self.motor.ejecutar_consulta_personalizada(query)
            
            if resultado.get('success') and resultado.get('data'):
                return resultado['data']
            return []
            
        except Exception as e:
            st.error(f"Error obteniendo progreso de estudiantes: {e}")
            return []

def reportes_formacion(db, rol_usuario):
    """Función principal de reportes de formación complementaria"""
    try:
        st.markdown("## 📊 Reportes de Formación Complementaria")
        st.markdown("---")
        
        # Verificar permisos
        if not tiene_permiso(rol_usuario, 'Formación Complementaria', 'leer'):
            st.warning("⚠️ No tienes permisos para ver los reportes de formación complementaria")
            return
        
        reportes = ReportesFormacion()
        
        # Tabs para diferentes tipos de reportes
        tab1, tab2, tab3 = st.tabs([
            "📈 Estadísticas Generales",
            "🏆 Talleres Populares", 
            "👥 Progreso Estudiantes"
        ])
        
        with tab1:
            st.markdown("### 📈 Estadísticas Generales")
            
            with st.spinner("Cargando estadísticas..."):
                stats = reportes.obtener_estadisticas_generales()
            
            if stats:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="Total de Talleres Activos",
                        value=stats.get('total_talleres', 0)
                    )
                
                with col2:
                    st.metric(
                        label="Total de Formaciones",
                        value=stats.get('total_formaciones', 0)
                    )
                
                with col3:
                    st.metric(
                        label="Estudiantes Inscritos",
                        value=stats.get('total_inscritos', 0)
                    )
            else:
                st.warning("No se pudieron cargar las estadísticas generales")
        
        with tab2:
            st.markdown("### 🏆 Talleres Populares")
            
            with st.spinner("Cargando talleres populares..."):
                talleres_populares = reportes.obtener_talleres_populares()
            
            if talleres_populares:
                df_talleres = pd.DataFrame(talleres_populares)
                
                # Renombrar columnas para mejor visualización
                df_talleres.columns = ['Taller', 'Total Inscripciones', 'Capacidad Máxima', '% Ocupación']
                
                st.dataframe(df_talleres, use_container_width=True)
                
                # Gráfico de barras
                st.bar_chart(df_talleres.set_index('Taller')['Total Inscripciones'])
            else:
                st.warning("No se encontraron datos de talleres populares")
        
        with tab3:
            st.markdown("### 👥 Progreso de Estudiantes")
            
            with st.spinner("Cargando progreso de estudiantes..."):
                progreso_estudiantes = reportes.obtener_progreso_estudiantes()
            
            if progreso_estudiantes:
                df_progreso = pd.DataFrame(progreso_estudiantes)
                
                # Renombrar columnas
                df_progreso.columns = [
                    'Nombre', 'Apellido', 'Total Talleres', 
                    'Completados', 'En Curso', 'Promedio Calificación'
                ]
                
                # Agregar nombre completo
                df_progreso['Nombre Completo'] = df_progreso['Nombre'] + ' ' + df_progreso['Apellido']
                
                # Mostrar tabla
                columnas_mostrar = [
                    'Nombre Completo', 'Total Talleres', 'Completados', 
                    'En Curso', 'Promedio Calificación'
                ]
                st.dataframe(df_progreso[columnas_mostrar], use_container_width=True)
            else:
                st.warning("No se encontraron datos de progreso de estudiantes")
        
        # Opciones de exportación
        st.markdown("---")
        st.markdown("### 📤 Opciones de Exportación")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Exportar Estadísticas (CSV)"):
                if stats:
                    df_stats = pd.DataFrame([stats])
                    csv = df_stats.to_csv(index=False)
                    st.download_button(
                        label="Descargar CSV",
                        data=csv,
                        file_name=f'estadisticas_formacion_{datetime.now().strftime("%Y%m%d")}.csv',
                        mime='text/csv'
                    )
        
        with col2:
            if st.button("📊 Generar Reporte Completo"):
                st.info("Función de reporte completo en desarrollo")
        
    except Exception as e:
        st.error(f"Error en módulo de reportes de formación: {e}")
        st.exception(e)
