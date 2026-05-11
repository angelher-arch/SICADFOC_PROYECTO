#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gestion_solicitudes.py - Módulo de Gestión de Solicitudes de Formación
SICADFOC 2026 - Instituto Universitario Jesus Obrero
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Any, Optional

# Importaciones del sistema
from database import execute_query, ejecutar_transaccion
from seguridad import tiene_permiso

class GestionSolicitudes:
    """Clase principal para gestión de solicitudes de formación"""
    
    def __init__(self):
        self.user_role = st.session_state.get('user_role', None)
        self.user_cedula = st.session_state.get('user_cedula', None)
        self.user_nombre = st.session_state.get('user_nombre', None)
    
    def gestion_solicitudes(self):
        """Función principal del módulo de gestión de solicitudes"""
        try:
            st.header("📋 Gestión de Solicitudes de Formación")
            st.info("Panel administrativo para controlar la oferta de talleres y procesar solicitudes")
            
            # Validar permisos
            if not tiene_permiso(self.user_role, 'Formación Complementaria', 'Aprobar'):
                st.error("No tienes permisos para acceder a este módulo.")
                return
            
            # Tabs para diferentes funcionalidades
            tab1, tab2, tab3 = st.tabs(["🏢 Disponibilidad de Talleres", "✅ Validación de Solicitudes", "👨‍🏫 Historial por Facilitador"])
            
            with tab1:
                self.mostrar_disponibilidad_talleres()
            
            with tab2:
                self.mostrar_validacion_solicitudes()
            
            with tab3:
                self.mostrar_historial_facilitador()
                
        except Exception as e:
            st.error(f"Error en módulo de gestión de solicitudes: {e}")
    
    def mostrar_disponibilidad_talleres(self):
        """Muestra disponibilidad de talleres con control de cupos"""
        st.subheader("🏢 Disponibilidad de Talleres")
        st.info("Visualice los talleres disponibles y controle los cupos")
        
        try:
            # Obtener talleres con información de cupos
            query = """
            SELECT fc.id_formacion,
                   fc.nombre,
                   fc.codigo_referencia,
                   fc.codigo_certificado,
                   fc.fecha_inicio,
                   fc.fecha_fin,
                   fc.cupo_maximo,
                   COUNT(i.id_inscripcion) as inscritos,
                   p.nombre as facilitador_nombre,
                   p.apellido as facilitador_apellido
            FROM formacion_complementaria fc
            LEFT JOIN inscripcion i ON fc.id_formacion = i.id_formacion AND i.estado = 'Activa'
            LEFT JOIN profesor pr ON fc.id_usuario = pr.cedula_profesor
            LEFT JOIN persona p ON pr.cedula_profesor = p.cedula
            WHERE fc.fecha_inicio >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY fc.id_formacion, fc.nombre, fc.codigo_referencia, fc.codigo_certificado, fc.fecha_inicio, fc.fecha_fin, fc.cupo_maximo, p.nombre, p.apellido
            ORDER BY fc.fecha_inicio DESC
            """
            
            resultado = execute_query(query, fetch_all=True)
            
            if not resultado:
                st.info("No hay talleres disponibles en este momento")
                return
            
            # Procesar datos para mostrar
            datos_talleres = []
            for taller in resultado:
                inscritos = taller['inscritos'] or 0
                cupo_maximo = taller.get('cupo_maximo', 30)
                cupos_disponibles = cupo_maximo - inscritos
                estado_cupo = "Disponible" if cupos_disponibles > 0 else "Completo"
                codigo_taller = taller.get('codigo_referencia') or taller.get('codigo_certificado') or 'N/A'
                
                datos_talleres.append({
                    'Nombre Taller': taller.get('nombre') or 'N/A',
                    'Código': codigo_taller,
                    'Facilitador': f"{taller.get('facilitador_nombre', 'N/A')} {taller.get('facilitador_apellido', '')}",
                    'Fecha Inicio': taller['fecha_inicio'].strftime('%d/%m/%Y') if taller.get('fecha_inicio') else 'N/A',
                    'Fecha Fin': taller['fecha_fin'].strftime('%d/%m/%Y') if taller.get('fecha_fin') else 'N/A',
                    'Inscritos': inscritos,
                    'Cupo Máximo': cupo_maximo,
                    'Disponibles': cupos_disponibles,
                    'Estado': estado_cupo
                })
            
            df = pd.DataFrame(datos_talleres)
            
            # Mostrar tabla con formato
            st.dataframe(
                df,
                column_config={
                    'Nombre Taller': st.column_config.TextColumn("Nombre Taller", width="large"),
                    'Código': st.column_config.TextColumn("Código", width="medium"),
                    'Facilitador': st.column_config.TextColumn("Facilitador", width="large"),
                    'Fecha Inicio': st.column_config.TextColumn("Inicio", width="small"),
                    'Fecha Fin': st.column_config.TextColumn("Fin", width="small"),
                    'Inscritos': st.column_config.NumberColumn("Inscritos", width="small"),
                    'Cupo Máximo': st.column_config.NumberColumn("Cupo", width="small"),
                    'Disponibles': st.column_config.NumberColumn("Disponibles", width="small"),
                    'Estado': st.column_config.TextColumn("Estado", width="small")
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Alertas visuales para talleres completos
            talleres_completos = [t for t in datos_talleres if t['Estado'] == 'Completo']
            if talleres_completos:
                st.warning(f"⚠️ {len(talleres_completos)} taller(es) han alcanzado su cupo máximo")
                
        except Exception as e:
            st.error(f"Error al cargar la disponibilidad de talleres: {str(e)}")
            st.info("Por favor, intente nuevamente más tarde")
    
    def mostrar_validacion_solicitudes(self):
        """Valida y procesa solicitudes de estudiantes"""
        st.subheader("✅ Validación de Solicitudes")
        st.info("Procese las solicitudes de inscripción de estudiantes")
        
        try:
            # Obtener solicitudes pendientes
            query = """
            SELECT sf.*, 
                   p.nombre as estudiante_nombre, 
                   p.apellido as estudiante_apellido,
                   fc.nombre as nombre_taller,
                   fc.codigo_referencia,
                   fc.codigo_certificado
            FROM solicitudes_formacion sf
            INNER JOIN estudiante e ON sf.cedula_estudiante = e.cedula_estudiante
            INNER JOIN persona p ON e.cedula_estudiante = p.cedula
            INNER JOIN formacion_complementaria fc ON sf.id_formacion = fc.id_formacion
            WHERE sf.estado = 'Pendiente'
            ORDER BY sf.fecha_solicitud DESC
            """
            
            resultado = execute_query(query, fetch_all=True)
            
            if not resultado:
                st.info("No hay solicitudes pendientes de aprobación")
                return
            
            # Mostrar solicitudes pendientes
            for i, solicitud in enumerate(resultado):
                with st.expander(f"📄 {solicitud['estudiante_nombre']} {solicitud['estudiante_apellido']} - {solicitud['nombre_taller']}", expanded=i == 0):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Estudiante:** {solicitud['estudiante_nombre']} {solicitud['estudiante_apellido']}")
                        st.write(f"**Cédula:** {solicitud['cedula_estudiante']}")
                        st.write(f"**Taller:** {solicitud['nombre_taller']}")
                        st.write(f"**Código:** {solicitud['codigo_certificado']}")
                    
                    with col2:
                        st.write(f"**Fecha Solicitud:** {solicitud['fecha_solicitud'].strftime('%d/%m/%Y %H:%M') if solicitud.get('fecha_solicitud') else 'N/A'}")
                        st.write(f"**Estado Actual:** {solicitud['estado']}")
                        st.write(f"**Código Taller:** {solicitud.get('codigo_referencia') or solicitud.get('codigo_certificado') or 'N/A'}")
                    
                    decision = st.radio(
                        "Decisión",
                        ["Pendiente", "Aprobada", "Rechazada"],
                        index=0,
                        key=f"decision_{solicitud['id_solicitud']}"
                    )
                    
                    if st.button("Guardar decisión", key=f"guardar_decision_{solicitud['id_solicitud']}"):
                        if decision == 'Aprobada':
                            self.aprobar_solicitud(solicitud['id_solicitud'])
                        elif decision == 'Rechazada':
                            self.rechazar_solicitud(solicitud['id_solicitud'])
                        else:
                            st.info("Seleccione Aprobada o Rechazada para procesar la solicitud")
                    
                    st.divider()
                
        except Exception as e:
            st.error(f"Error al cargar las solicitudes pendientes: {str(e)}")
            st.info("Por favor, intente nuevamente más tarde")
    
    def mostrar_historial_facilitador(self):
        """Muestra historial por facilitador con GROUP BY"""
        st.subheader("👨‍🏫 Historial por Facilitador")
        st.info("Consulte el rendimiento histórico por profesor")
        
        try:
            # Obtener lista de facilitadores
            query_facilitadores = """
            SELECT DISTINCT p.nombre, p.apellido, pr.cedula_profesor
            FROM profesor pr
            INNER JOIN persona p ON pr.cedula_profesor = p.cedula
            INNER JOIN formacion_complementaria fc ON pr.cedula_profesor = fc.id_usuario
            ORDER BY p.nombre, p.apellido
            """
            
            facilitadores = execute_query(query_facilitadores, fetch_all=True)
            
            if not facilitadores:
                st.info("No hay facilitadores con talleres asignados")
                return
            
            # Selector de facilitador
            opciones_facilitadores = [
                f"{f['nombre']} {f['apellido']}" for f in facilitadores
            ]
            
            facilitador_seleccionado = st.selectbox(
                "Seleccionar Facilitador",
                opciones_facilitadores,
                key="selector_facilitador"
            )
            
            if facilitador_seleccionado:
                indice = opciones_facilitadores.index(facilitador_seleccionado)
                facilitador = facilitadores[indice]
                cedula_facilitador = facilitador['cedula_profesor']
                
                # Obtener historial del facilitador
                query_historial = """
                SELECT 
                    fc.nombre_taller,
                    fc.codigo_certificado,
                    fc.fecha_inicio,
                    fc.fecha_fin,
                    COUNT(sf.id_solicitud) as total_solicitudes,
                    SUM(CASE WHEN sf.estado = 'Aprobada' THEN 1 ELSE 0 END) as aprobadas,
                    SUM(CASE WHEN sf.estado = 'Rechazada' THEN 1 ELSE 0 END) as rechazadas,
                    SUM(CASE WHEN sf.estado = 'Diferida' THEN 1 ELSE 0 END) as diferidas,
                    COUNT(i.id_inscripcion) as inscritos_finales
                FROM formacion_complementaria fc
                LEFT JOIN solicitudes_formacion sf ON fc.id_formacion = sf.id_formacion
                LEFT JOIN inscripcion i ON fc.id_formacion = i.id_formacion AND i.estado = 'Activa'
                WHERE fc.id_usuario = %s
                GROUP BY fc.id_formacion, fc.nombre_taller, fc.codigo_certificado, fc.fecha_inicio, fc.fecha_fin
                ORDER BY fc.fecha_inicio DESC
                """
                
                historial = execute_query(query_historial, (cedula_facilitador,), fetch_all=True)
                
                if not historial:
                    st.info(f"El facilitador {facilitador_seleccionado} no tiene historial de talleres")
                    return
                
                # Mostrar estadísticas generales
                st.write(f"### 📊 Estadísticas de {facilitador_seleccionado}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_talleres = len(historial)
                    st.metric("Talleres Dictados", total_talleres)
                
                with col2:
                    total_solicitudes = sum(h['total_solicitudes'] or 0 for h in historial)
                    st.metric("Total Solicitudes", total_solicitudes)
                
                with col3:
                    total_aprobadas = sum(h['aprobadas'] or 0 for h in historial)
                    st.metric("Solicitudes Aprobadas", total_aprobadas)
                
                with col4:
                    total_inscritos = sum(h['inscritos_finales'] or 0 for h in historial)
                    st.metric("Inscritos Finales", total_inscritos)
                
                # Tabla detallada
                st.write("### 📋 Detalle por Taller")
                
                datos_historial = []
                for h in historial:
                    tasa_aprobacion = 0
                    if (h['total_solicitudes'] or 0) > 0:
                        tasa_aprobacion = ((h['aprobadas'] or 0) / (h['total_solicitudes'] or 0)) * 100
                    
                    datos_historial.append({
                        'Taller': h['nombre_taller'],
                        'Código': h['codigo_certificado'],
                        'Fecha Inicio': h['fecha_inicio'].strftime('%d/%m/%Y'),
                        'Fecha Fin': h['fecha_fin'].strftime('%d/%m/%Y'),
                        'Solicitudes': h['total_solicitudes'] or 0,
                        'Aprobadas': h['aprobadas'] or 0,
                        'Rechazadas': h['rechazadas'] or 0,
                        'Diferidas': h['diferidas'] or 0,
                        'Inscritos': h['inscritos_finales'] or 0,
                        'Tasa Aprobación': f"{tasa_aprobacion:.1f}%"
                    })
                
                df_historial = pd.DataFrame(datos_historial)
                
                st.dataframe(
                    df_historial,
                    column_config={
                        'Taller': st.column_config.TextColumn("Taller", width="large"),
                        'Código': st.column_config.TextColumn("Código", width="medium"),
                        'Fecha Inicio': st.column_config.TextColumn("Inicio", width="small"),
                        'Fecha Fin': st.column_config.TextColumn("Fin", width="small"),
                        'Solicitudes': st.column_config.NumberColumn("Solicitudes", width="small"),
                        'Aprobadas': st.column_config.NumberColumn("Aprobadas", width="small"),
                        'Rechazadas': st.column_config.NumberColumn("Rechazadas", width="small"),
                        'Diferidas': st.column_config.NumberColumn("Diferidas", width="small"),
                        'Inscritos': st.column_config.NumberColumn("Inscritos", width="small"),
                        'Tasa Aprobación': st.column_config.TextColumn("Tasa", width="small")
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
        except Exception as e:
            st.error("Error al cargar el historial del facilitador")
            st.info("Por favor, intente nuevamente más tarde")
    
    def aprobar_solicitud(self, id_solicitud):
        """Aprueba una solicitud y crea inscripción"""
        try:
            # Obtener datos de la solicitud
            query_solicitud = """
            SELECT sf.*, fc.cupo_maximo
            FROM solicitudes_formacion sf
            INNER JOIN formacion_complementaria fc ON sf.id_formacion = fc.id_formacion
            WHERE sf.id_solicitud = %s
            """
            
            solicitud = execute_query(query_solicitud, (id_solicitud,), fetch_one=True)
            
            if not solicitud:
                st.error("Solicitud no encontrada")
                return
            
            # Verificar cupos disponibles
            query_inscritos = """
            SELECT COUNT(*) as inscritos
            FROM inscripcion
            WHERE id_formacion = %s AND estado = 'Activa'
            """
            
            resultado_inscritos = execute_query(query_inscritos, (solicitud['id_formacion'],), fetch_one=True)
            inscritos_actuales = resultado_inscritos['inscritos']
            cupo_maximo = solicitud.get('cupo_maximo', 30)
            
            if inscritos_actuales >= cupo_maximo:
                st.error("No hay cupos disponibles en este taller")
                return
            
            # Ejecutar transacción atómica (actualizar solicitud + crear/actualizar inscripción)
            transaccion_queries = [
                (
                    """
                    UPDATE solicitudes_formacion 
                    SET estado = 'Aprobada', 
                        fecha_resolucion = CURRENT_TIMESTAMP,
                        resuelto_por = %s
                    WHERE id_solicitud = %s
                    """,
                    (self.user_cedula, id_solicitud)
                ),
                (
                    """
                    INSERT INTO inscripcion (cedula_estudiante, id_formacion, fecha_inscripcion, estado)
                    VALUES (%s, %s, CURRENT_TIMESTAMP, 'Activa')
                    ON CONFLICT (cedula_estudiante, id_formacion) 
                    DO UPDATE SET estado = 'Activa', fecha_inscripcion = CURRENT_TIMESTAMP
                    """,
                    (solicitud['cedula_estudiante'], solicitud['id_formacion'])
                )
            ]
            
            resultado_tx = ejecutar_transaccion(transaccion_queries)
            if not resultado_tx.get('success'):
                st.error("No se pudo aprobar la solicitud por un error de transacción")
                return
            
            st.success("✅ Solicitud aprobada exitosamente")
            st.rerun()
            
        except Exception as e:
            st.error("Error al aprobar la solicitud")
            st.info("Por favor, intente nuevamente")
    
    def rechazar_solicitud(self, id_solicitud):
        """Rechaza una solicitud con motivo obligatorio"""
        try:
            # Formulario para motivo de rechazo
            with st.form(f"form_rechazo_{id_solicitud}"):
                st.write("**Motivo de Rechazo (obligatorio):**")
                motivo = st.text_area(
                    "Explique por qué se rechaza esta solicitud",
                    key=f"motivo_rechazo_{id_solicitud}",
                    help="Este motivo será visible para el estudiante"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("Confirmar Rechazo", type="primary"):
                        if not motivo.strip():
                            st.error("El motivo de rechazo es obligatorio")
                            return
                        
                        # Actualizar solicitud
                        query = """
                        UPDATE solicitudes_formacion 
                        SET estado = 'Rechazada', 
                            fecha_resolucion = CURRENT_TIMESTAMP,
                            resuelto_por = %s,
                            motivo_rechazo = %s
                        WHERE id_solicitud = %s
                        """
                        
                        execute_query(query, (self.user_cedula, motivo.strip(), id_solicitud))
                        
                        st.success("❌ Solicitud rechazada exitosamente")
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("Cancelar"):
                        st.info("Operación cancelada")
                        st.rerun()
            
        except Exception as e:
            st.error("Error al rechazar la solicitud")
            st.info("Por favor, intente nuevamente")
    
    def diferir_solicitud(self, id_solicitud):
        """Difiere una solicitud"""
        try:
            # Formulario para observaciones
            with st.form(f"form_diferir_{id_solicitud}"):
                st.write("**Observaciones (opcional):**")
                observaciones = st.text_area(
                    "Añada observaciones sobre la diferición",
                    key=f"obs_diferir_{id_solicitud}",
                    help="Información adicional para el estudiante"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("Confirmar Diferición", type="primary"):
                        # Actualizar solicitud
                        query = """
                        UPDATE solicitudes_formacion 
                        SET estado = 'Diferida', 
                            fecha_resolucion = CURRENT_TIMESTAMP,
                            resuelto_por = %s,
                            observaciones = %s
                        WHERE id_solicitud = %s
                        """
                        
                        execute_query(query, (self.user_cedula, observaciones.strip(), id_solicitud))
                        
                        st.success("⏳ Solicitud diferida exitosamente")
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("Cancelar"):
                        st.info("Operación cancelada")
                        st.rerun()
            
        except Exception as e:
            st.error("Error al diferir la solicitud")
            st.info("Por favor, intente nuevamente")

# Función principal para compatibilidad con el orquestador
def gestion_solicitudes_main():
    """Función principal del módulo de gestión de solicitudes"""
    try:
        if not tiene_permiso(st.session_state.get('user_role'), 'Formación Complementaria', 'Aprobar'):
            st.error("No tienes permisos para acceder a este módulo.")
            return
        
        gestor = GestionSolicitudes()
        gestor.gestion_solicitudes()
        
    except Exception as e:
        st.error(f"Error en el módulo de gestión de solicitudes: {e}")
