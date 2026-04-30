#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor de Formación Complementaria y Certificaciones - SICADFOC 2026
Módulos unificados: Formación Complementaria y Solicitud de Formación con control de cupos
"""

import streamlit as st
import os
import re
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

# Importar estilos globales de formularios (MANDATORIO)
from styles import aplicar_estilo_consistente_global

# Importaciones del sistema
try:
    from seguridad import tiene_permiso, SeguridadFOC26
    from database import execute_query, ejecutar_transaccion
except ImportError as e:
    st.error(f"Error importando módulos: {e}")
    st.stop()

def sanitize_filename(filename):
    """Sanitiza nombre de archivo para almacenamiento seguro"""
    return re.sub(r'[^A-Za-z0-9_.-]', '_', str(filename))

class GestorFormacionComplementaria:
    """Clase principal para gestión unificada de formación complementaria y solicitudes"""
    
    def __init__(self):
        self.user_cedula = self.get_user_cedula()
        self.user_role = self.get_user_role()
        self.user_info = self.get_user_info()
    
    def get_user_cedula(self) -> str:
        """Obtiene cédula del usuario autenticado"""
        try:
            from seguridad import SeguridadFOC26
            return SeguridadFOC26.get_user_cedula() or ""
        except:
            return st.session_state.get('user', {}).get('cedula_usuario', '')
    
    def get_user_role(self) -> str:
        """Obtiene rol del usuario autenticado"""
        try:
            from seguridad import SeguridadFOC26
            if SeguridadFOC26.is_admin():
                return 'Administrador'
            elif SeguridadFOC26.is_profesor():
                return 'Profesor'
            elif SeguridadFOC26.is_estudiante():
                return 'Estudiante'
        except:
            return st.session_state.get('user', {}).get('rol', '')
    
    def get_user_info(self) -> Dict[str, Any]:
        """Obtiene información completa del usuario"""
        return st.session_state.get('user', {})
    
    def generar_codigo_certificado(self, año_inscripcion: str, tomo: str, folio: str) -> str:
        """Genera código de certificado con formato IU-FOC-YYYY-T-FFF"""
        año_formateado = año_inscripcion[-4:] if len(año_inscripcion) > 4 else año_inscripcion
        folio_formateado = folio.zfill(3)  # Rellenar con ceros a la izquierda
        return f"IU-FOC-{año_formateado}-{tomo}-{folio_formateado}"
    
    def obtener_talleres_disponibles(self) -> List[Dict[str, Any]]:
        """Obtiene talleres disponibles con información de cupos"""
        query = """
        SELECT 
            t.id_taller as id,
            t.nombre_taller,
            t.descripcion_taller as descripcion,
            t.fecha_inicio,
            t.fecha_fin,
            t.duracion_horas,
            t.tipo_taller as nombre_categoria,
            t.capacidad_maxima as cupos_disponibles,
            t.estado as estado_taller
        FROM taller t
        WHERE t.estado = 'activo'
        ORDER BY t.fecha_inicio ASC
        """
        resultado = execute_query(query)
        
        if resultado and isinstance(resultado, list) and len(resultado) > 0 and isinstance(resultado[0], dict):
            return resultado
        return []
    
    def verificar_cupos_disponibles(self, id_taller: int) -> Dict[str, Any]:
        """Verifica cupos disponibles de un taller específico"""
        query = """
        SELECT capacidad_maxima as cupos_disponibles, estado 
        FROM taller 
        WHERE id_taller = %s
        """
        resultado = execute_query(query, (id_taller,))
        
        if resultado and isinstance(resultado, list) and len(resultado) > 0:
            taller = resultado[0]
            cupos = taller.get('cupos_disponibles', 0)
            estado = taller.get('estado', '')
            
            return {
                'cupos_disponibles': cupos,
                'estado': estado,
                'agotado': cupos <= 0,
                'disponible': estado == 'activo' and cupos > 0
            }
        
        return {'cupos_disponibles': 0, 'estado': 'Inactivo', 'agotado': True, 'disponible': False}
    
    def inscribir_estudiante_taller(self, id_taller: int, cedula_estudiante: str) -> Dict[str, Any]:
        """Inscribe a un estudiante en un taller con control transaccional de cupos"""
        try:
            # Verificar disponibilidad antes de inscribir
            disponibilidad = self.verificar_cupos_disponibles(id_taller)
            
            if not disponibilidad['disponible']:
                if disponibilidad['agotado']:
                    return {'success': False, 'message': 'Taller agotado - No hay cupos disponibles'}
                else:
                    return {'success': False, 'message': 'Taller no disponible para inscripción'}
            
            # Verificar si el estudiante ya está inscrito
            query_verificar = """
            SELECT id_inscripcion FROM inscripcion i
            JOIN formacion_complementaria fc ON i.id_formacion = fc.id_formacion
            WHERE i.cedula_estudiante = %s AND fc.id_taller = %s
            """
            ya_inscrito = execute_query(query_verificar, (cedula_estudiante, id_taller))
            
            if ya_inscrito and len(ya_inscrito) > 0:
                return {'success': False, 'message': 'El estudiante ya está inscrito en este taller'}
            
            # Primero obtener o crear el registro en formacion_complementaria
            query_fc = """
            SELECT id_formacion FROM formacion_complementaria 
            WHERE id_taller = %s
            """
            fc_resultado = execute_query(query_fc, (id_taller,))
            
            if not fc_resultado or len(fc_resultado) == 0:
                # Crear registro en formacion_complementaria
                query_insert_fc = """
                INSERT INTO formacion_complementaria (id_taller, nombre, descripcion, horas)
                SELECT nombre_taller, descripcion_taller, duracion_horas
                FROM taller WHERE id_taller = %s
                RETURNING id_formacion
                """
                fc_nuevo = execute_query(query_insert_fc, (id_taller,))
                if fc_nuevo and len(fc_nuevo) > 0:
                    id_formacion = fc_nuevo[0]['id_formacion']
                else:
                    return {'success': False, 'message': 'Error al crear registro de formación'}
            else:
                id_formacion = fc_resultado[0]['id_formacion']
            
            # Transacción: Insertar inscripción y actualizar cupos
            queries = [
                # Insertar inscripción
                """
                INSERT INTO inscripcion (cedula_estudiante, id_formacion, fecha_inscripcion, estado)
                VALUES (%s, %s, %s, 'inscrito')
                """,
                # Actualizar cupos disponibles
                """
                UPDATE taller 
                SET capacidad_maxima = capacidad_maxima - 1 
                WHERE id_taller = %s AND capacidad_maxima > 0
                """
            ]
            
            params = [
                (cedula_estudiante, id_formacion, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                (id_taller,)
            ]
            
            resultado_transaccion = ejecutar_transaccion(queries, params)
            
            if resultado_transaccion['success']:
                return {
                    'success': True, 
                    'message': 'Inscripción realizada exitosamente',
                    'id_inscripcion': resultado_transaccion.get('last_id')
                }
            else:
                return {'success': False, 'message': f'Error en la inscripción: {resultado_transaccion["message"]}'}
                
        except Exception as e:
            return {'success': False, 'message': f'Error al procesar inscripción: {str(e)}'}
    
    def obtener_solicitudes_estudiante(self, cedula_estudiante: str) -> List[Dict[str, Any]]:
        """Obtiene solicitudes de formación de un estudiante"""
        query = """
        SELECT 
            i.id_inscripcion as id,
            i.id_formacion,
            i.fecha_inscripcion,
            i.estado,
            i.observaciones,
            t.nombre_taller,
            t.descripcion_taller as descripcion,
            t.fecha_inicio,
            t.fecha_fin,
            t.duracion_horas,
            t.tipo_taller as nombre_categoria
        FROM inscripcion i
        JOIN formacion_complementaria fc ON i.id_formacion = fc.id_formacion
        JOIN taller t ON fc.id_taller = t.id_taller
        WHERE i.cedula_estudiante = %s
        ORDER BY i.fecha_inscripcion DESC
        """
        resultado = execute_query(query, (cedula_estudiante,))
        
        if resultado and isinstance(resultado, list) and len(resultado) > 0 and isinstance(resultado[0], dict):
            return resultado
        return []
    
    def obtener_todas_solicitudes(self) -> List[Dict[str, Any]]:
        """Obtiene todas las solicitudes para gestión administrativa"""
        query = """
        SELECT 
            i.id_inscripcion as id,
            i.cedula_estudiante,
            i.id_formacion,
            i.fecha_inscripcion,
            i.estado,
            i.observaciones,
            t.nombre_taller,
            t.descripcion_taller as descripcion,
            t.fecha_inicio,
            t.fecha_fin,
            t.duracion_horas,
            t.tipo_taller as nombre_categoria,
            p.nombre,
            p.apellido
        FROM inscripcion i
        JOIN formacion_complementaria fc ON i.id_formacion = fc.id_formacion
        JOIN taller t ON fc.id_taller = t.id_taller
        JOIN persona p ON i.cedula_estudiante = p.cedula
        ORDER BY i.fecha_inscripcion DESC
        """
        resultado = execute_query(query)
        
        if resultado and isinstance(resultado, list) and len(resultado) > 0 and isinstance(resultado[0], dict):
            return resultado
        return []
    
    def actualizar_estado_solicitud(self, id_inscripcion: int, nuevo_estado: str, tomo: str = "", folio: str = "") -> Dict[str, Any]:
        """Actualiza el estado de una solicitud y genera código de certificado si es necesario"""
        try:
            # Obtener información de la inscripción
            query_info = """
            SELECT i.cedula_estudiante, i.fecha_inscripcion, fc.nombre_taller
            FROM inscripcion i
            JOIN formacion_complementaria fc ON i.id_formacion = fc.id_formacion
            WHERE i.id_inscripcion = %s
            """
            info = execute_query(query_info, (id_inscripcion,))
            
            if not info or len(info) == 0:
                return {'success': False, 'message': 'Solicitud no encontrada'}
            
            inscripcion_info = info[0]
            codigo_certificado = None
            
            # Si el estado es "Inscrito" o "Aprobado", generar código de certificado
            if nuevo_estado in ['Inscrito', 'Aprobado', 'Certificado'] and tomo and folio:
                año_inscripcion = inscripcion_info['fecha_inscripcion'].year
                codigo_certificado = self.generar_codigo_certificado(str(año_inscripcion), tomo, folio)
            
            # Actualizar estado y código de certificado
            query_update = """
            UPDATE inscripcion 
            SET estado = %s, observaciones = %s, fecha_creacion = %s
            WHERE id_inscripcion = %s
            """
            
            resultado = execute_query(query_update, (
                nuevo_estado, 
                codigo_certificado, 
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                id_inscripcion
            ))
            
            if resultado is not None:
                mensaje = f'Estado actualizado a "{nuevo_estado}" exitosamente'
                if codigo_certificado:
                    mensaje += f'. Código de certificado: {codigo_certificado}'
                
                return {
                    'success': True, 
                    'message': mensaje,
                    'codigo_certificado': codigo_certificado
                }
            else:
                return {'success': False, 'message': 'Error al actualizar el estado'}
                
        except Exception as e:
            return {'success': False, 'message': f'Error al actualizar estado: {str(e)}'}
    
    def modulo_formacion_complementaria(self):
        """Módulo unificado de Formación Complementaria"""
        # Aplicar estilos globales (MANDATORIO)
        aplicar_estilo_consistente_global()
        
        st.header("Formación Complementaria")
        st.info("Módulo unificado para gestión de talleres y formación complementaria")
        
        # Tabs según rol
        if self.user_role in ['Administrador', 'Profesor']:
            tab1, tab2, tab3 = st.tabs(["Talleres Disponibles", "Gestión de Talleres", "Estadísticas"])
            
            with tab1:
                self.mostrar_talleres_disponibles_admin()
            
            with tab2:
                self.gestion_talleres_admin()
            
            with tab3:
                self.estadisticas_formacion()
        
        else:  # Estudiante
            tab1, tab2 = st.tabs(["Talleres Disponibles", "Mis Solicitudes"])
            
            with tab1:
                self.mostrar_talleres_disponibles_estudiante()
            
            with tab2:
                self.mostrar_mis_solicitudes()
    
    def modulo_solicitud_formacion(self):
        """Módulo de Solicitud de Formación (vista Estudiante)"""
        # Aplicar estilos globales (MANDATORIO)
        aplicar_estilo_consistente_global()
        
        st.header("Solicitud de Formación Complementaria")
        st.info("Inscríbete en los talleres disponibles y gestiona tus solicitudes")
        
        self.mostrar_talleres_disponibles_estudiante()
    
    def modulo_gestion_solicitudes(self):
        """Módulo de Gestión de Solicitudes (vista Administrador/Profesor)"""
        # Aplicar estilos globales (MANDATORIO)
        aplicar_estilo_consistente_global()
        
        st.header("Gestión de Solicitudes de Formación")
        st.info("Gestiona las solicitudes de los estudiantes y genera certificados")
        
        self.mostrar_todas_solicitudes_admin()
    
    def mostrar_talleres_disponibles_estudiante(self):
        """Muestra talleres disponibles para inscripción (vista estudiante)"""
        talleres = self.obtener_talleres_disponibles()
        
        if not talleres:
            st.info("No hay talleres disponibles en este momento.")
            return
        
        st.subheader("Talleres Disponibles para Inscripción")
        
        for taller in talleres:
            with st.expander(f"**{taller['nombre_taller']}**", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Descripción:** {taller['descripcion'] or 'No disponible'}")
                    st.markdown(f"**Categoría:** {taller['nombre_categoria'] or 'Sin categoría'}")
                    st.markdown(f"**Duración:** {taller['duracion_horas']} horas")
                    st.markdown(f"**Fecha Inicio:** {taller['fecha_inicio']}")
                    st.markdown(f"**Fecha Fin:** {taller['fecha_fin']}")
                
                with col2:
                    # Verificar cupos disponibles
                    disponibilidad = self.verificar_cupos_disponibles(taller['id'])
                    
                    if disponibilidad['agotado']:
                        st.error("Agotado")
                        st.caption("No hay cupos disponibles")
                    elif not disponibilidad['disponible']:
                        st.warning("No disponible")
                        st.caption("Taller inactivo")
                    else:
                        st.success(f"{disponibilidad['cupos_disponibles']} cupos")
                        
                        if st.button(f"Inscribirse", key=f"inscribir_{taller['id']}"):
                            with st.spinner("Procesando inscripción..."):
                                resultado = self.inscribir_estudiante_taller(taller['id'], self.user_cedula)
                                
                                if resultado['success']:
                                    st.success(resultado['message'])
                                    st.rerun()
                                else:
                                    st.error(resultado['message'])
    
    def mostrar_mis_solicitudes(self):
        """Muestra las solicitudes del estudiante actual"""
        solicitudes = self.obtener_solicitudes_estudiante(self.user_cedula)
        
        if not solicitudes:
            st.info("No tienes solicitudes de formación registradas.")
            return
        
        st.subheader("Mis Solicitudes de Formación")
        
        for solicitud in solicitudes:
            with st.expander(f"**{solicitud['nombre_taller']}**", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Fecha de Inscripción:** {solicitud['fecha_inscripcion']}")
                    st.markdown(f"**Categoría:** {solicitud['nombre_categoria'] or 'Sin categoría'}")
                    st.markdown(f"**Duración:** {solicitud['duracion_horas']} horas")
                    st.markdown(f"**Fecha Inicio:** {solicitud['fecha_inicio']}")
                    st.markdown(f"**Fecha Fin:** {solicitud['fecha_fin']}")
                    
                    # Estado con color
                    estado = solicitud['estado']
                    if estado == 'Pendiente':
                        st.markdown(f"**Estado:** :orange[{estado}]")
                    elif estado == 'Inscrito':
                        st.markdown(f"**Estado:** :green[{estado}]")
                    elif estado == 'Certificado':
                        st.markdown(f"**Estado:** :blue[{estado}]")
                    else:
                        st.markdown(f"**Estado:** {estado}")
                    
                    if solicitud['codigo_certificado']:
                        st.markdown(f"**Código Certificado:** `{solicitud['codigo_certificado']}`")
                
                with col2:
                    # Acciones según estado
                    if estado == 'Pendiente':
                        st.info("En revisión")
                    elif estado == 'Inscrito':
                        st.success("Activo")
                    elif estado == 'Certificado':
                        st.success("Certificado emitido")
    
    def mostrar_talleres_disponibles_admin(self):
        """Muestra talleres disponibles (vista administrador)"""
        talleres = self.obtener_talleres_disponibles()
        
        if not talleres:
            st.info("No hay talleres disponibles.")
            return
        
        st.subheader("Talleres Disponibles")
        
        # Convertir a DataFrame para mejor visualización
        import pandas as pd
        
        df_talleres = pd.DataFrame(talleres)
        
        # Renombrar columnas para mejor visualización
        columnas_renombradas = {
            'nombre_taller': 'Taller',
            'nombre_categoria': 'Categoría',
            'duracion_horas': 'Duración (hrs)',
            'fecha_inicio': 'Fecha Inicio',
            'fecha_fin': 'Fecha Fin',
            'cupos_disponibles': 'Cupos Disponibles',
            'estado_taller': 'Estado'
        }
        
        df_talleres = df_talleres.rename(columns=columnas_renombradas)
        
        # Seleccionar columnas a mostrar
        columnas_mostrar = ['Taller', 'Categoría', 'Duración (hrs)', 'Fecha Inicio', 'Fecha Fin', 'Cupos Disponibles', 'Estado']
        
        st.dataframe(
            df_talleres[columnas_mostrar],
            use_container_width=True,
            hide_index=True
        )
    
    def mostrar_todas_solicitudes_admin(self):
        """Muestra todas las solicitudes para gestión administrativa"""
        solicitudes = self.obtener_todas_solicitudes()
        
        if not solicitudes:
            st.info("No hay solicitudes de formación registradas.")
            return
        
        st.subheader("Gestión de Solicitudes de Formación")
        
        # Convertir a DataFrame para mejor visualización
        import pandas as pd
        
        df_solicitudes = pd.DataFrame(solicitudes)
        
        # Renombrar columnas para mejor visualización
        columnas_renombradas = {
            'id': 'ID',
            'cedula_estudiante': 'Cédula',
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'nombre_taller': 'Taller',
            'nombre_categoria': 'Categoría',
            'fecha_inscripcion': 'Fecha Inscripción',
            'estado': 'Estado',
            'codigo_certificado': 'Código Certificado'
        }
        
        df_solicitudes = df_solicitudes.rename(columns=columnas_renombradas)
        
        # Seleccionar columnas a mostrar
        columnas_mostrar = ['ID', 'Cédula', 'Nombre', 'Apellido', 'Taller', 'Fecha Inscripción', 'Estado', 'Código Certificado']
        
        st.dataframe(
            df_solicitudes[columnas_mostrar],
            use_container_width=True,
            hide_index=True
        )
        
        # Sección de gestión de solicitudes
        st.markdown("---")
        st.subheader("Actualizar Estado de Solicitud")
        
        # Selector de solicitud
        opciones_solicitudes = [f"{s['id']} - {s['nombre']} {s['apellido']} - {s['nombre_taller']}" for s in solicitudes]
        solicitud_seleccionada = st.selectbox("Seleccionar Solicitud", opciones_solicitudes)
        
        if solicitud_seleccionada:
            # Obtener ID de la solicitud seleccionada
            id_solicitud = int(solicitud_seleccionada.split(" - ")[0])
            
            # Obtener información de la solicitud
            solicitud_info = next((s for s in solicitudes if s['id'] == id_solicitud), None)
            
            if solicitud_info:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    nuevo_estado = st.selectbox(
                        "Nuevo Estado",
                        ["Pendiente", "Inscrito", "Certificado", "Cancelado"],
                        index=["Pendiente", "Inscrito", "Certificado", "Cancelado"].index(solicitud_info['estado'])
                    )
                
                with col2:
                    tomo = st.text_input("Tomo", placeholder="Ej: 1")
                
                with col3:
                    folio = st.text_input("Folio", placeholder="Ej: 001")
                
                if st.button("Actualizar Estado", type="primary"):
                    if nuevo_estado in ['Inscrito', 'Certificado'] and (not tomo or not folio):
                        st.error("Para generar certificado debe ingresar Tomo y Folio")
                    else:
                        with st.spinner("Actualizando estado..."):
                            resultado = self.actualizar_estado_solicitud(
                                id_solicitud, 
                                nuevo_estado, 
                                tomo, 
                                folio
                            )
                            
                            if resultado['success']:
                                st.success(resultado['message'])
                                st.rerun()
                            else:
                                st.error(resultado['message'])
    
    def gestion_talleres_admin(self):
        """Gestión de talleres (vista administrador)"""
        st.subheader("Gestión de Talleres")
        st.info("Funcionalidad de gestión de talleres - En desarrollo")
    
    def estadisticas_formacion(self):
        """Estadísticas de formación (vista administrador)"""
        st.subheader("Estadísticas de Formación")
        st.info("Funcionalidad de estadísticas - En desarrollo")

# Funciones principales para exportación
def formacion_complementaria_main():
    """Función principal del módulo unificado de Formación Complementaria"""
    try:
        # Validar permisos de acceso
        rol_usuario = st.session_state.get('user_role', None)
        
        if rol_usuario is None:
            st.error("Error: No se pudo determinar el rol del usuario")
            return
        
        if not tiene_permiso(rol_usuario, 'Formación Complementaria', 'Consultar'):
            st.error("Acceso denegado. No tienes permisos para consultar formación complementaria.")
            return
        
        # Crear instancia del gestor
        gestor = GestorFormacionComplementaria()
        
        # Mostrar módulo principal
        gestor.modulo_formacion_complementaria()
        
    except Exception as e:
        st.error(f"Error en el módulo de formación complementaria: {e}")

def solicitud_formacion_main():
    """Función principal del módulo de Solicitud de Formación (vista estudiante)"""
    try:
        # Validar permisos (sin restricción de rol)
        rol_usuario = st.session_state.get('user_role', None)
        
        if not tiene_permiso(rol_usuario, 'Solicitud Formación Complementaria', 'Consultar'):
            st.error("Acceso denegado. No tienes permisos para solicitar formación.")
            return
        
        # Crear instancia del gestor
        gestor = GestorFormacionComplementaria()
        
        # Mostrar módulo de solicitud
        gestor.modulo_solicitud_formacion()
        
    except Exception as e:
        st.error(f"Error en el módulo de solicitud de formación: {e}")

def gestion_solicitudes_main():
    """Función principal del módulo de Gestión de Solicitudes (vista administrador/profesor)"""
    try:
        # Validar rol
        rol_usuario = st.session_state.get('user_role', None)
        
        if rol_usuario not in ['Administrador', 'Profesor']:
            st.error("Este módulo está disponible solo para administradores y profesores.")
            return
        
        # Validar permisos
        if not tiene_permiso(rol_usuario, 'Formación Complementaria', 'Editar'):
            st.error("Acceso denegado. No tienes permisos para gestionar solicitudes.")
            return
        
        # Crear instancia del gestor
        gestor = GestorFormacionComplementaria()
        
        # Mostrar módulo de gestión
        gestor.modulo_gestion_solicitudes()
        
    except Exception as e:
        st.error(f"Error en el módulo de gestión de solicitudes: {e}")

# Función de compatibilidad para el sistema existente
def gestor_certificaciones_unificado():
    """Función principal unificada con compatibilidad para el sistema existente"""
    try:
        # Obtener rol del usuario
        rol_usuario = st.session_state.get('user_role', None)
        
        if rol_usuario is None:
            st.error("Error: No se pudo determinar el rol del usuario")
            return
        
        # Validar permisos de acceso
        if not tiene_permiso(rol_usuario, 'Formación Complementaria', 'Consultar'):
            st.error("Acceso denegado. No tienes permisos para consultar formación complementaria.")
            return
        
        # Crear instancia del gestor
        gestor = GestorFormacionComplementaria()
        
        st.header("Formación Complementaria y Certificaciones")
        
        # Tabs según rol
        if rol_usuario in ['Administrador', 'Profesor']:
            tab1, tab2, tab3 = st.tabs(["Formación Complementaria", "Gestión de Solicitudes", "Estadísticas"])
            
            with tab1:
                gestor.modulo_formacion_complementaria()
            
            with tab2:
                gestor.modulo_gestion_solicitudes()
            
            with tab3:
                gestor.estadisticas_formacion()
        
        else:  # Estudiante
            tab1, tab2 = st.tabs(["Talleres Disponibles", "Mis Solicitudes"])
            
            with tab1:
                gestor.modulo_solicitud_formacion()
            
            with tab2:
                gestor.mostrar_mis_solicitudes()
                
    except Exception as e:
        st.error(f"Error en el módulo de formación complementaria: {e}")

if __name__ == "__main__":
    gestor_certificaciones_unificado()
