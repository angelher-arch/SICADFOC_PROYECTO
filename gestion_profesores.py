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
        print(">>> PROFESORES: Iniciando gestión de profesores")
        try:
            # Validar permisos de acceso
            if not tiene_permiso(self.user_role, 'Gestión Profesores', 'Consultar'):
                st.error("Acceso denegado. No tienes permisos para consultar profesores.")
                return
            
            st.header("👨‍🏫 Gestión de Profesores")
            
            # Estructura unificada de 3 pestañas principales
            tab1, tab2, tab3 = st.tabs(["Listado de Profesores", "Registrar Nuevo Profesor", "Consultar/Editar"])
            
            with tab1:
                st.subheader("Listado de Profesores")
                self.listar_profesores()
            
            with tab2:
                st.subheader("Registrar Nuevo Profesor")
                if tiene_permiso(self.user_role, 'Gestión Profesores', 'Registrar'):
                    self.registro_profesores()
                else:
                    st.warning("No tienes permisos para registrar nuevos profesores.")
            
            with tab3:
                st.subheader("Consultar/Editar Profesor")
                self.consultar_editar_profesor()
                    
        except Exception as e:
            st.error(f"Error en el módulo de gestión de profesores: {e}")
    
    def listar_profesores(self):
        """Función optimizada para listar profesores con un solo llamado a la DB"""
        try:
            from database import execute_query
            import pandas as pd
            
            # Consulta SQL optimizada para traer todos los datos necesarios
            query = """
            SELECT 
                p.cedula,
                p.nombre,
                p.apellido,
                p.email_personal,
                p.telefono,
                pr.especialidad,
                pr.fecha_contratacion,
                pr.activo,
                u.login_usuario
            FROM profesor pr
            JOIN persona p ON pr.cedula_profesor = p.cedula
            LEFT JOIN usuarios u ON pr.cedula_profesor = u.cedula_usuario
            ORDER BY p.apellido, p.nombre
            """
            
            # Ejecutar consulta única
            result = execute_query(query, fetch_all=True)
            
            if result and len(result) > 0:
                # Convertir a DataFrame
                df = pd.DataFrame(result)
                
                # Renombrar columnas para mejor visualización
                df.columns = ['Cédula', 'Nombre', 'Apellido', 'Email', 'Teléfono', 
                             'Especialidad', 'Fecha Contratación', 'Activo', 'Usuario']
                
                # Mostrar estadísticas
                st.info(f"Total de profesores registrados: {len(df)}")
                
                # Mostrar DataFrame con opciones de filtrado
                st.dataframe(df, width='stretch', hide_index=True)
                
                # Opciones de exportación
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Exportar a CSV", key="export_profesores"):
                        csv = df.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="Descargar CSV",
                            data=csv,
                            file_name="profesores.csv",
                            mime="text/csv"
                        )
                
                with col2:
                    if st.button("Actualizar Lista", key="refresh_profesores"):
                        st.rerun()
                        
            else:
                st.warning("No se encontraron profesores registrados.")
                st.info("Use la pestaña 'Registrar Nuevo Profesor' para agregar nuevos registros.")
                
        except Exception as e:
            st.error(f"Error al cargar el listado de profesores: {e}")
            st.warning("Por favor, recargue la página e intente nuevamente.")
    
    def consultar_editar_profesor(self):
        """Función para consultar y editar profesor por cédula"""
        try:
            # Formulario de búsqueda por cédula
            cedula_busqueda = st.text_input("Ingrese Cédula del Profesor:", key="cedula_busqueda_profesor")
            
            if st.button("Buscar Profesor", type="primary", key="btn_buscar_profesor"):
                if cedula_busqueda:
                    self.mostrar_formulario_edicion_profesor(cedula_busqueda)
                else:
                    st.warning("Por favor, ingrese una cédula para buscar.")
                    
        except Exception as e:
            st.error(f"Error en sección de consulta/edición: {e}")
    
    def mostrar_formulario_edicion_profesor(self, cedula):
        """Mostrar formulario para editar profesor existente"""
        try:
            from database import execute_query
            
            # Buscar profesor por cédula
            query = """
            SELECT 
                p.cedula,
                p.nombre,
                p.apellido,
                p.email_personal,
                p.telefono,
                pr.especialidad,
                pr.fecha_contratacion,
                pr.activo
            FROM profesor pr
            JOIN persona p ON pr.cedula_profesor = p.cedula
            WHERE pr.cedula_profesor = %s
            """
            
            resultado = execute_query(query, (cedula,), fetch_one=True)
            
            if not resultado:
                st.error(f"No se encontró profesor con cédula: {cedula}")
                return
            
            st.success(f"Profesor encontrado: {resultado['nombre']} {resultado['apellido']}")
            
            # Formulario de edición
            with st.form("form_editar_profesor"):
                st.subheader("Editar Datos del Profesor")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    nombre = st.text_input("Nombre*", value=resultado['nombre'], key="edit_nombre_prof")
                    apellido = st.text_input("Apellido*", value=resultado['apellido'], key="edit_apellido_prof")
                    email = st.text_input("Email", value=resultado['email_personal'], key="edit_email_prof")
                    telefono = st.text_input("Teléfono", value=resultado['telefono'], key="edit_telefono_prof")
                
                with col2:
                    especialidad = st.text_input("Especialidad*", value=resultado['especialidad'], key="edit_especialidad_prof")
                    fecha_contratacion = st.date_input(
                        "Fecha Contratación", 
                        value=pd.to_datetime(resultado['fecha_contratacion']).date() if resultado['fecha_contratacion'] else None,
                        key="edit_fecha_contratacion_prof"
                    )
                    estado = st.selectbox(
                        "Estado",
                        [True, False],
                        index=0 if resultado['activo'] else 1,
                        key="edit_estado_prof",
                        format_func=lambda x: "Activo" if x else "Inactivo"
                    )
                
                col3, col4 = st.columns(2)
                with col3:
                    if st.form_submit_button("Actualizar Profesor", type="primary"):
                        # Validar campos obligatorios
                        if not nombre or not apellido or not especialidad:
                            st.error("Nombre, apellido y especialidad son obligatorios")
                            return
                        
                        # Actualizar datos
                        update_queries = [
                            (
                                """UPDATE persona SET 
                                    nombre = %s, apellido = %s, email_personal = %s, telefono = %s 
                                    WHERE cedula = %s""",
                                (nombre, apellido, email, telefono, cedula)
                            ),
                            (
                                """UPDATE profesor SET 
                                    especialidad = %s, fecha_contratacion = %s, activo = %s 
                                    WHERE cedula_profesor = %s""",
                                (especialidad, fecha_contratacion, estado, cedula)
                            )
                        ]
                        
                        from database import ejecutar_transaccion
                        resultado_update = ejecutar_transaccion(update_queries)
                        
                        if resultado_update.get('success'):
                            st.success("Profesor actualizado exitosamente")
                            st.rerun()
                        else:
                            st.error(f"Error al actualizar profesor: {resultado_update.get('message', 'Error desconocido')}")
                
                with col4:
                    if st.form_submit_button("Cancelar", type="secondary"):
                        st.rerun()
                        
        except Exception as e:
            st.error(f"Error al cargar formulario de edición: {e}")
    
    def mostrar_listado_profesores(self):
        """Muestra el listado de profesores (mantenido para compatibilidad)"""
        self.listar_profesores()
    
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
            
            if resultado_especialidades:
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
            
            if resultado_contrataciones:
                st.subheader("Contrataciones por Año")
                
                df_contrataciones = pd.DataFrame(resultado_contrataciones)
                df_contrataciones.columns = ['Año', 'Cantidad']
                
                st.line_chart(df_contrataciones.set_index('Año'))
                
        except Exception as e:
            st.error(f"Error al mostrar estadísticas: {e}")

def gestion_profesores_main():
    """Función principal del módulo de gestión de profesores"""
    print(">>> PROFESORES_MAIN: Iniciando función principal")
    try:
        gestor = GestionProfesores()
        print(">>> PROFESORES_MAIN: Instancia creada, llamando a gestión_profesores()")
        gestor.gestion_profesores()
        print(">>> PROFESORES_MAIN: gestión_profesores() completada")
    except Exception as e:
        print(f">>> ERROR PROFESORES_MAIN: {e}")
        import traceback
        print(f">> ERROR PROFESORES_MAIN: Traceback - {traceback.format_exc()}")
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
