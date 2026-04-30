#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gestion_profesores.py - Módulo de Gestión de Profesores
SICADFOC 2026 - Instituto Universitario Jesus Obrero
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional

# Importar estilos globales de formularios (MANDATORIO)
from styles import aplicar_estilo_consistente_global

# Importaciones del sistema
from formacion_complementaria import motor_formacion
from seguridad import tiene_permiso, SeguridadFOC26

class GestionProfesores:
    """Clase principal para gestión de profesores"""
    
    def __init__(self):
        self.user_role = st.session_state.get('user_role', None)
        self.user_cedula = st.session_state.get('user_cedula', None)
        self.user_nombre = st.session_state.get('user_nombre', None)
    
    def gestion_profesores(self):
        """Función principal del módulo de gestión de profesores"""
        try:
            # Aplicar estilos globales de formularios (MANDATORIO)
            aplicar_estilo_consistente_global()
            
            # Validar permisos de acceso
            if not tiene_permiso(self.user_role, 'Gestión Profesores', 'Consultar'):
                st.error("Acceso denegado. No tienes permisos para consultar profesores.")
                return
            
            st.header("👨‍🏫 Gestión de Profesores")
            
            # Tabs para diferentes funcionalidades
            tab1, tab2, tab3 = st.tabs(["📋 Listado", "➕ Registro", "📊 Estadísticas"])
            
            with tab1:
                self.mostrar_listado_profesores()
            
            with tab2:
                if tiene_permiso(self.user_role, 'Gestión Profesores', 'Registrar'):
                    self.registro_profesores()
                else:
                    st.warning("No tienes permisos para registrar nuevos profesores.")
            
            with tab3:
                if tiene_permiso(self.user_role, 'Gestión Profesores', 'Estadísticas'):
                    self.mostrar_estadisticas_profesores()
                else:
                    st.warning("No tienes permisos para ver estadísticas.")
                    
        except Exception as e:
            st.error(f"Error en el módulo de gestión de profesores: {e}")
    
    def mostrar_listado_profesores(self):
        """Muestra el listado de profesores"""
        try:
            st.subheader("Listado de Profesores")
            
            # USAR MOTOR CENTRAL UNIFICADO PARA PROFESORES
            resultado = motor_formacion.leer_profesores(orden='apellido, nombre')
            
            if resultado['success']:
                profesores = resultado['data']
                
                if profesores and isinstance(profesores, list) and len(profesores) > 0:
                    # Verificar que los datos tengan la estructura correcta
                    if isinstance(profesores[0], dict):
                        df = pd.DataFrame(profesores)
                    else:
                        st.warning("Formato de datos de profesores incorrecto")
                        return
                else:
                    st.info("No hay profesores registrados.")
                    return
                    
                # Renombrar columnas para mejor visualización
                columnas_renombradas = {
                    'cedula_usuario': 'Cédula Usuario',
                    'nombre': 'Nombres',
                    'apellido': 'Apellidos',
                    'cedula': 'Cédula',
                    'telefono': 'Teléfono',
                    'fecha_nacimiento': 'Fecha Nacimiento',
                    'sexo': 'Sexo',
                    'direccion': 'Dirección',
                    'email_profesor': 'Email',
                    'especialidad': 'Especialidad',
                    'fecha_contratacion': 'Fecha Contratación',
                    'estado_profesor': 'Estado'
                }
                df = df.rename(columns=columnas_renombradas)
                
                # Mostrar DataFrame
                st.dataframe(df, use_container_width=True)
                
                # Opciones de acción
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if tiene_permiso(self.user_role, 'Gestión Profesores', 'Editar'):
                        if st.button("Edit Editar Profesor", key="editar_profesor_btn"):
                            st.session_state.mostrar_formulario_edicion = True
                            st.rerun()
                
                with col2:
                    if tiene_permiso(self.user_role, 'Gestión Profesores', 'Eliminar'):
                        if st.button("Eliminar Profesor", key="eliminar_profesor_btn"):
                            st.session_state.mostrar_formulario_eliminacion = True
                            st.rerun()
                
                with col3:
                    if st.button("Exportar CSV", key="exportar_profesores_csv"):
                        csv = df.to_csv(index=False)
                        st.download_button(
                            "Descargar Listado",
                            csv,
                            "profesores.csv",
                            "text/csv"
                        )
                    
                    # Formulario de edición si está activado
                    if st.session_state.get('mostrar_formulario_edicion', False):
                        self.formulario_edicion_profesor()
                    
                    # Formulario de eliminación si está activado
                    if st.session_state.get('mostrar_formulario_eliminacion', False):
                        self.formulario_eliminacion_profesor()
                        
            else:
                st.error(f"Error al obtener profesores: {resultado['message']}")
                
        except Exception as e:
            st.error(f"Error al mostrar listado de profesores: {e}")
    
    def registro_profesores(self):
        """Formulario de registro de nuevos profesores"""
        try:
            st.subheader("Registro de Nuevo Profesor")
            
            with st.form("form_registro_profesor"):
                col1, col2 = st.columns(2)
                
                with col1:
                    cedula = st.text_input("Cédula*", placeholder="Ej: 12345678")
                    nombre_completo = st.text_input("Nombre Completo*", placeholder="Ej: Juan Pérez")
                    especialidad = st.text_input("Especialidad*", placeholder="Ej: Matemáticas")
                    email = st.text_input("Email", placeholder="profesor@ejemplo.com")
                
                with col2:
                    telefono = st.text_input("Teléfono", placeholder="0414-1234567")
                    fecha_contratacion = st.date_input("Fecha Contratación", value=datetime.now().date())
                    estado = st.selectbox("Estado", ["Activo", "Inactivo"], index=0)
                    
                    # Campos para usuario
                    st.markdown("**Datos de Acceso**")
                    password = st.text_input("Contraseña*", type="password", placeholder="Mínimo 6 caracteres")
                    confirmar_password = st.text_input("Confirmar Contraseña*", type="password")
                
                submitted = st.form_submit_button("Registrar Profesor", type="primary")
                
                if submitted:
                    self.procesar_registro_profesor(
                        cedula, nombre_completo, especialidad, email, telefono,
                        fecha_contratacion, estado, password, confirmar_password
                    )
                    
        except Exception as e:
            st.error(f"Error en el formulario de registro: {e}")
    
    def procesar_registro_profesor(self, cedula: str, nombre_completo: str, especialidad: str,
                                 email: str, telefono: str, fecha_contratacion, estado: str,
                                 password: str, confirmar_password: str):
        """Procesa el registro de un nuevo profesor"""
        try:
            # Validaciones básicas
            if not all([cedula, nombre_completo, especialidad, password]):
                st.error("Los campos marcados con * son obligatorios.")
                return
            
            if password != confirmar_password:
                st.error("Las contraseñas no coinciden.")
                return
            
            if len(password) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres.")
                return
            
            # Verificar si la cédula ya existe
            query_check = "SELECT cedula_profesor FROM profesor WHERE cedula_profesor = %s"
            resultado = execute_query(query_check, (cedula,))
            
            if resultado and len(resultado) > 0:
                st.error("Ya existe un profesor con esta cédula.")
                return
            
            # Verificar si el usuario ya existe
            query_check_user = "SELECT cedula_usuario FROM usuarios WHERE cedula_usuario = %s"
            resultado_user = execute_query(query_check_user, (cedula,))
            
            if resultado_user and len(resultado_user) > 0:
                st.error("Ya existe un usuario con esta cédula.")
                return
            
            # Transacción para insertar profesor y usuario
            queries = [
                # Insertar usuario
                (
                    "INSERT INTO usuarios (cedula_usuario, login_usuario, rol, contrasena, activo, fecha_creacion) VALUES (%s, %s, 'Profesor', %s, TRUE, %s)",
                    (cedula, nombre_completo, SeguridadFOC26.hash_password(password), datetime.now())
                ),
                # Insertar profesor
                (
                    """
                    INSERT INTO profesor 
                    (cedula_profesor, especialidad, fecha_contratacion, categoria, activo, fecha_creacion)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (cedula, especialidad, fecha_contratacion, estado, True, datetime.now())
                )
            ]
            
            resultado_transaccion = ejecutar_transaccion(queries)
            
            if resultado_transaccion['success']:
                st.success(f"Profesor {nombre_completo} registrado exitosamente.")
                
                # Limpiar formulario
                st.session_state.clear()
                st.rerun()
            else:
                st.error(f"Error al registrar profesor: {resultado_transaccion['message']}")
                
        except Exception as e:
            st.error(f"Error al procesar registro: {e}")
    
    def formulario_edicion_profesor(self):
        """Formulario para editar profesor existente"""
        try:
            st.subheader("Editar Profesor")
            
            # Lista de profesores para selección
            query_profesores = "SELECT p.cedula_profesor, per.nombre FROM profesor p JOIN persona per ON p.cedula_profesor = per.cedula ORDER BY per.nombre"
            resultado_profesores = execute_query(query_profesores)
            
            if resultado_profesores:
                profesores_dict = {f"{p['nombre_completo']} ({p['cedula']})": p['cedula'] 
                                for p in resultado_profesores}
                
                profesor_seleccionado = st.selectbox(
                    "Seleccionar Profesor",
                    options=list(profesores_dict.keys())
                )
                
                if profesor_seleccionado:
                    cedula_seleccionada = profesores_dict[profesor_seleccionado]
                    
                    # Obtener datos del profesor
                    query_datos = """
                    SELECT p.*, per.nombre, per.apellido, per.telefono, per.email 
                    FROM profesor p 
                    JOIN persona per ON p.cedula_profesor = per.cedula 
                    WHERE p.cedula_profesor = %s
                    """
                    resultado_datos = execute_query(query_datos, (cedula_seleccionada,))
                    
                    if resultado_datos and len(resultado_datos) > 0:
                        profesor = resultado_datos[0]
                        
                        with st.form("form_editar_profesor"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                nombre_completo = st.text_input(
                                    "Nombre Completo*", 
                                    value=profesor.get('nombre', '') + ' ' + profesor.get('apellido', '')
                                )
                                especialidad = st.text_input(
                                    "Especialidad*", 
                                    value=profesor.get('especialidad', '')
                                )
                                email = st.text_input(
                                    "Email", 
                                    value=profesor.get('email', '')
                                )
                            
                            with col2:
                                telefono = st.text_input(
                                    "Teléfono", 
                                    value=profesor.get('telefono', '')
                                )
                                fecha_contratacion = st.date_input(
                                    "Fecha Contratación",
                                    value=pd.to_datetime(profesor.get('fecha_contratacion')).date()
                                )
                                estado = st.selectbox(
                                    "Estado",
                                    ["Activo", "Inactivo"],
                                    index=0 if profesor.get('estado') == 'Activo' else 1
                                )
                            
                            col_submit, col_cancel = st.columns(2)
                            
                            with col_submit:
                                submitted = st.form_submit_button("Actualizar", type="primary")
                            
                            with col_cancel:
                                if st.form_submit_button("Cancelar"):
                                    st.session_state.mostrar_formulario_edicion = False
                                    st.rerun()
                            
                            if submitted:
                                self.procesar_edicion_profesor(
                                    cedula_seleccionada, nombre_completo, especialidad,
                                    email, telefono, fecha_contratacion, estado
                                )
            else:
                st.error("No hay profesores disponibles para editar.")
                
        except Exception as e:
            st.error(f"Error en el formulario de edición: {e}")
    
    def procesar_edicion_profesor(self, cedula: str, nombre_completo: str, especialidad: str,
                                email: str, telefono: str, fecha_contratacion, estado: str):
        """Procesa la edición de un profesor"""
        try:
            if not all([nombre_completo, especialidad]):
                st.error("Los campos marcados con * son obligatorios.")
                return
            
            # Actualizar datos del profesor
            query_update = """
            UPDATE profesor SET
                nombre_completo = %s,
                especialidad = %s,
                email = %s,
                telefono = %s,
                fecha_contratacion = %s,
                estado = %s,
                fecha_actualizacion = %s
            WHERE cedula = %s
            """
            
            # Verificar conexión antes de procesar
            from database import test_database_connection
            conn_result = test_database_connection()
            if not conn_result or conn_result.get('status') != 'SUCCESS':
                st.error("❌ Error de conexión antes de actualizar profesor")
                st.warning("Por favor, recargue la página e intente nuevamente.")
                return
            
            resultado = execute_query(query_update, (
                nombre_completo, especialidad, email, telefono,
                fecha_contratacion, estado, datetime.now(), cedula
            ))
            
            if resultado:
                # Actualizar nombre en tabla usuario también
                query_update_usuario = "UPDATE usuario SET nombre = %s WHERE cedula = %s"
                execute_query(query_update_usuario, (nombre_completo, cedula))
                
                st.success("Profesor actualizado exitosamente.")
                st.session_state.mostrar_formulario_edicion = False
                st.rerun()
            else:
                st.error("❌ Error al actualizar profesor.")
                
        except Exception as e:
            # DETECCIÓN Y RECUPERACIÓN AUTOMÁTICA
            print(f"❌ Error procesando edición de profesor: {e}")
            st.error("❌ Ocurrió un error inesperado al actualizar profesor")
            st.info("🔄 El sistema intentará recuperar la conexión automáticamente...")
            
            # Marcar para recuperación en siguiente interacción
            st.session_state.transaccion_abortada = True
            st.session_state.error_actualizacion = str(e)
    
    def formulario_eliminacion_profesor(self):
        """Formulario para eliminar profesor"""
        try:
            st.subheader("Eliminar Profesor")
            st.warning("⚠️ Esta acción es irreversible. ¿Está seguro de continuar?")
            
            # Lista de profesores para selección
            query_profesores = "SELECT cedula_profesor, nombre || ' ' || apellido AS nombre_completo FROM profesor ORDER BY nombre"
            resultado_profesores = execute_query(query_profesores)
            
            if resultado_profesores:
                profesores_dict = {f"{p['nombre_completo']} ({p['cedula']})": p['cedula'] 
                                for p in resultado_profesores}
                
                profesor_seleccionado = st.selectbox(
                    "Seleccionar Profesor a Eliminar",
                    options=list(profesores_dict.keys())
                )
                
                col_confirm, col_cancel = st.columns(2)
                
                with col_confirm:
                    if st.button("🗑️ Eliminar", type="primary"):
                        cedula_seleccionada = profesores_dict[profesor_seleccionado]
                        self.procesar_eliminacion_profesor(cedula_seleccionada)
                
                with col_cancel:
                    if st.button("Cancelar"):
                        st.session_state.mostrar_formulario_eliminacion = False
                        st.rerun()
            else:
                st.error("No hay profesores disponibles para eliminar.")
                
        except Exception as e:
            st.error(f"Error en el formulario de eliminación: {e}")
    
    def procesar_eliminacion_profesor(self, cedula: str):
        """Procesa la eliminación de un profesor con manejo robusto de errores"""
        try:
            # Verificar conexión antes de procesar
            from database import test_database_connection
            conn_result = test_database_connection()
            if not conn_result or conn_result.get('status') != 'SUCCESS':
                st.error("❌ Error de conexión antes de eliminar profesor")
                st.warning("Por favor, recargue la página e intente nuevamente.")
                return
            
            # Verificar si el profesor tiene talleres asignados
            query_check_talleres = "SELECT COUNT(*) as count FROM formacion_complementaria WHERE id_profesor = %s"
            resultado_talleres = execute_query(query_check_talleres, (cedula,))
            
            if resultado_talleres and resultado_talleres[0]['count'] > 0:
                st.error("No se puede eliminar el profesor porque tiene talleres asignados.")
                return
            
            # Transacción para eliminar profesor y usuario
            queries = [
                # Eliminar profesor
                ("DELETE FROM profesor WHERE cedula_profesor = %s", (cedula,)),
                # Eliminar usuario
                ("DELETE FROM usuarios WHERE cedula_usuario = %s", (cedula,))
            ]
            
            resultado_transaccion = ejecutar_transaccion(queries)
            
            if resultado_transaccion['success']:
                st.success("Profesor eliminado exitosamente.")
                st.session_state.mostrar_formulario_eliminacion = False
                st.rerun()
            else:
                st.error(f"❌ Error al eliminar profesor: {resultado_transaccion['message']}")
                
        except Exception as e:
            # DETECCIÓN Y RECUPERACIÓN AUTOMÁTICA
            print(f"❌ Error procesando eliminación de profesor: {e}")
            st.error("❌ Ocurrió un error inesperado al eliminar profesor")
            st.info("🔄 El sistema intentará recuperar la conexión automáticamente...")
            
            # Marcar para recuperación en siguiente interacción
            st.session_state.transaccion_abortada = True
            st.session_state.error_eliminacion = str(e)
    
    def mostrar_estadisticas_profesores(self):
        """Muestra estadísticas de profesores"""
        try:
            st.subheader("Estadísticas de Profesores")
            
            # Estadísticas generales - Corregido para esquema con columna activo (boolean)
            query_total = "SELECT COUNT(*) as total FROM profesor"
            query_activos = "SELECT COUNT(*) as activos FROM profesor WHERE activo = true"
            query_inactivos = "SELECT COUNT(*) as inactivos FROM profesor WHERE activo = false"
            
            resultado_total = execute_query(query_total)
            resultado_activos = execute_query(query_activos)
            resultado_inactivos = execute_query(query_inactivos)
            
            # Mostrar métricas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if resultado_total:
                    st.metric("Total Profesores", resultado_total[0]['total'])
            
            with col2:
                if resultado_activos:
                    st.metric("Profesores Activos", resultado_activos[0]['activos'])
            
            with col3:
                if resultado_inactivos:
                    st.metric("Profesores Inactivos", resultado_inactivos[0]['inactivos'])
            
            # Profesores por especialidad
            query_especialidades = """
            SELECT especialidad, COUNT(*) as cantidad 
            FROM profesor 
            WHERE especialidad IS NOT NULL AND especialidad != ''
            GROUP BY especialidad 
            ORDER BY cantidad DESC
            """
            
            resultado_especialidades = execute_query(query_especialidades)
            
            if resultado_especialidades and isinstance(resultado_especialidades, list) and len(resultado_especialidades) > 0 and isinstance(resultado_especialidades[0], dict):
                st.subheader("Profesores por Especialidad")
                
                df_especialidades = pd.DataFrame(resultado_especialidades)
                df_especialidades.columns = ['Especialidad', 'Cantidad']
                
                st.bar_chart(df_especialidades.set_index('Especialidad'))
            
            # Profesores contratados por año
            query_contrataciones = """
            SELECT YEAR(fecha_contratacion) as año, COUNT(*) as cantidad
            FROM profesor 
            WHERE fecha_contratacion IS NOT NULL
            GROUP BY YEAR(fecha_contratacion)
            ORDER BY año DESC
            """
            
            resultado_contrataciones = execute_query(query_contrataciones)
            
            if resultado_contrataciones and isinstance(resultado_contrataciones, list) and len(resultado_contrataciones) > 0 and isinstance(resultado_contrataciones[0], dict):
                st.subheader("Contrataciones por Año")
                
                df_contrataciones = pd.DataFrame(resultado_contrataciones)
                df_contrataciones.columns = ['Año', 'Cantidad']
                
                st.line_chart(df_contrataciones.set_index('Año'))
                
        except Exception as e:
            st.error(f"Error al mostrar estadísticas: {e}")

def gestion_profesores_main():
    """Función principal del módulo de gestión de profesores"""
    try:
        gestor = GestionProfesores()
        gestor.gestion_profesores()
    except Exception as e:
        st.error(f"Error en el módulo de gestión de profesores: {e}")

def registro_profesores_main():
    """Función principal del módulo de registro de profesores"""
    try:
        gestor = GestionProfesores()
        gestor.registro_profesores()
    except Exception as e:
        st.error(f"Error en el módulo de registro de profesores: {e}")

if __name__ == "__main__":
    gestion_profesores_main()
