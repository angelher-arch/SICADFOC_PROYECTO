#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gestion_estudiantil.py - Módulo de Gestión de Estudiantes
SICADFOC 2026 - Instituto Universitario Jesus Obrero
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional

# Importaciones del sistema
from formacion_complementaria import motor_formacion
from seguridad import tiene_permiso, SeguridadFOC26

class GestionEstudiantil:
    """Clase principal para gestión de estudiantes"""
    
    def __init__(self):
        self.user_role = st.session_state.get('user_role', None)
        self.user_cedula = st.session_state.get('user_cedula', None)
        self.user_nombre = st.session_state.get('user_nombre', None)
    
    def gestion_estudiantil(self):
        """Función principal del módulo de gestión estudiantil"""
        print("DEBUG_ESTUDIANTIL: Iniciando gestión estudiantil")
        try:
            # Validar permisos de acceso
            if not tiene_permiso(self.user_role, 'Gestión Estudiantil', 'Consultar'):
                st.error("Acceso denegado. No tienes permisos para consultar estudiantes.")
                return
            
            st.header("👨‍🎓 Gestión de Estudiantes")
            
            # Estructura unificada de 3 pestañas principales
            tab1, tab2, tab3 = st.tabs(["Listado de Estudiantes", "Registrar Nuevo Estudiante", "Consultar/Editar"])
            
            with tab1:
                st.subheader("Listado de Estudiantes")
                self.listar_estudiantes()
            
            with tab2:
                st.subheader("Registrar Nuevo Estudiante")
                if tiene_permiso(self.user_role, 'Gestión Estudiantil', 'Registrar'):
                    self.registro_estudiantes()
                else:
                    st.warning("No tienes permisos para registrar nuevos estudiantes.")
            
            with tab3:
                st.subheader("Consultar/Editar Estudiante")
                self.consultar_editar_estudiante()
                    
        except Exception as e:
            st.error(f"Error en el módulo de gestión estudiantil: {e}")
    
    def listar_estudiantes(self):
        """Función optimizada para listar estudiantes con un solo llamado a la DB"""
        try:
            from database import execute_query
            import pandas as pd
            import streamlit as st
            
            # Consulta SQL optimizada para traer todos los datos necesarios (misma estructura que profesores)
            query = """
            SELECT 
                e.cedula_estudiante,
                e.nombres,
                e.apellidos,
                e.id_carrera,
                c.nombre_carrera
            FROM estudiante e
            LEFT JOIN carrera c ON e.id_carrera = c.id_carrera
            ORDER BY e.apellidos, e.nombres
            """
            
            # Ejecutar consulta única
            result = execute_query(query, fetch_all=True)
            
            if result and len(result) > 0:
                # Convertir a DataFrame
                df = pd.DataFrame(result)
                
                # Renombrar columnas para mejor visualización (solo 5 columnas reales)
                df.columns = ['Cédula', 'Nombre', 'Apellido', 'Carrera', 'Nombre Carrera']
                
                # Mostrar estadísticas
                st.info(f"Total de estudiantes registrados: {len(df)}")
                
                # Mostrar DataFrame con opciones de filtrado
                st.dataframe(df, width='stretch', hide_index=True)
                
                # Opciones de exportación con control RBAC
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Exportar a CSV", key="export_estudiantes"):
                        csv = df.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="Descargar CSV",
                            data=csv,
                            file_name="estudiantes.csv",
                            mime="text/csv"
                        )
                
                with col2:
                    # Solo administradores pueden actualizar
                    is_admin = st.session_state.get('usuario_rol') == 'Administrador'
                    if st.button("Actualizar Lista", key="refresh_estudiantes", disabled=not is_admin):
                        st.rerun()
                    
            else:
                st.warning("No se encontraron estudiantes registrados.")
                is_admin = st.session_state.get('usuario_rol') == 'Administrador'
                if is_admin:
                    st.info("Use la pestaña 'Registrar Nuevo Estudiante' para agregar nuevos registros.")
            
        except Exception as e:
            st.error(f"Error al cargar el listado de estudiantes: {e}")
            st.warning("Por favor, recargue la página e intente nuevamente.")
    
    def consultar_editar_estudiante(self):
        """Función para consultar y editar estudiante por cédula"""
        try:
            # Control de acceso - Solo administradores pueden editar
            is_admin = st.session_state.get('usuario_rol') == 'Administrador'
            
            # Formulario de búsqueda por cédula
            cedula_busqueda = st.text_input("Ingrese Cédula del Estudiante:", key="cedula_busqueda_estudiante")

            # Botón de búsqueda con control RBAC
            button_label = "Buscar Estudiante" if is_admin else "Ver Estudiante (Solo Lectura)"
            button_type = "primary" if is_admin else "secondary"
            
            if st.button(button_label, type=button_type, key="btn_buscar_estudiante"):
                if cedula_busqueda:
                    self.mostrar_formulario_edicion_estudiante(cedula_busqueda, allow_edit=is_admin)
                else:
                    st.warning("Por favor, ingrese una cédula para buscar.")

        except Exception as e:
            st.error(f"Error en sección de consulta/edición: {e}")
    
    def mostrar_formulario_edicion_estudiante(self, cedula, allow_edit=True):
        """Mostrar formulario para editar estudiante existente"""
        try:
            from database import execute_query
            from gestion_carreras import obtener_carreras_activas
            
            # Buscar estudiante por cédula
            query = """
            SELECT 
                e.cedula_estudiante,
                p.nombre,
                p.apellido,
                p.email,
                p.telefono,
                p.fecha_nacimiento,
                p.genero,
                p.direccion,
                e.id_carrera,
                e.id_semestre_formacion,
                e.id_estado_registro
            FROM estudiante e
            LEFT JOIN persona p ON e.id_persona = p.id
            WHERE e.cedula_estudiante = %s
            """
            
            resultado = execute_query(query, (cedula,), fetch_one=True)
            
            if not resultado:
                st.error(f"No se encontró estudiante con cédula: {cedula}")
                return
            
            st.success(f"Estudiante encontrado: {resultado['nombre']} {resultado['apellido']}")
            
            # Formulario de edición
            with st.form("form_editar_estudiante"):
                st.subheader("Editar Datos del Estudiante")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    nombre = st.text_input("Nombre*", value=resultado['nombre'], key="edit_nombre")
                    apellido = st.text_input("Apellido*", value=resultado['apellido'], key="edit_apellido")
                    email = st.text_input("Email", value=resultado.get('email', ''), key="edit_email")
                    telefono = st.text_input("Teléfono", value=resultado['telefono'], key="edit_telefono")
                
                with col2:
                    fecha_nacimiento = st.date_input(
                        "Fecha de Nacimiento", 
                        value=pd.to_datetime(resultado['fecha_nacimiento']).date() if resultado['fecha_nacimiento'] else None,
                        key="edit_fecha_nacimiento"
                    )
                    sexo = st.selectbox(
                        "Género", 
                        ["Masculino", "Femenino"], 
                        index=0 if resultado['sexo'] == "Masculino" else 1,
                        key="edit_sexo"
                    )
                    direccion = st.text_area("Dirección", value=resultado['direccion'], key="edit_direccion")
                
                # Obtener carreras dinámicamente
                carreras = obtener_carreras_activas()
                if carreras:
                    carrera_opciones = {c['nombre_carrera']: c['id_carrera'] for c in carreras}
                    carrera_nombre = st.selectbox(
                        "Carrera*",
                        options=list(carrera_opciones.keys()),
                        index=list(carrera_opciones.values()).index(resultado['id_carrera']) if resultado['id_carrera'] in carrera_opciones.values() else 0,
                        key="edit_carrera"
                    )
                    id_carrera = carrera_opciones[carrera_nombre]
                else:
                    st.warning("No hay carreras disponibles")
                    id_carrera = resultado['id_carrera']
                
                col3, col4 = st.columns(2)
                with col3:
                    semestre = st.number_input(
                        "Semestre", 
                        min_value=1, 
                        max_value=20, 
                        value=int(resultado['semestre_actual']) if resultado['semestre_actual'] else 1,
                        key="edit_semestre"
                    )
                with col4:
                    estado = st.selectbox(
                        "Estado de Registro",
                        ["Activo", "Inactivo", "Suspendido"],
                        index=0 if resultado['estado_registro'] == "Activo" else 1 if resultado['estado_registro'] == "Inactivo" else 2,
                        key="edit_estado"
                    )
                
                col5, col6 = st.columns(2)
                with col5:
                    # Validar permisos de edición
                    from seguridad import tiene_permiso
                    if tiene_permiso(st.session_state.get('user_role'), 'Gestión Estudiantil', 'editar'):
                        if st.form_submit_button("Actualizar Estudiante", type="primary"):
                            # Validar campos obligatorios
                            if not nombre or not apellido:
                                st.error("Nombre y apellido son obligatorios")
                                return
                            
                            # Actualizar datos
                            update_queries = [
                                (
                                    """UPDATE persona SET 
                                        nombre = %s, apellido = %s, email = %s, telefono = %s, 
                                        fecha_nacimiento = %s, genero = %s, direccion = %s 
                                        WHERE cedula = %s""",
                                    (nombre, apellido, email, telefono, fecha_nacimiento, genero, direccion, cedula)
                                ),
                                (
                                    """UPDATE estudiante SET 
                                        id_carrera = %s, semestre_actual = %s, estado_registro = %s 
                                        WHERE cedula_estudiante = %s""",
                                    (id_carrera, semestre, estado, cedula)
                                )
                            ]
                            
                            from database import ejecutar_transaccion
                            resultado_update = ejecutar_transaccion(update_queries)
                            
                            if resultado_update.get('success'):
                                st.success("Estudiante actualizado exitosamente")
                                st.rerun()
                            else:
                                st.error(f"Error al actualizar estudiante: {resultado_update.get('message', 'Error desconocido')}")
                    else:
                        st.warning("No tienes permisos para editar estudiantes.")

                with col6:
                    if st.form_submit_button("Cancelar", type="secondary"):
                        st.rerun()

        except Exception as e:
            st.error(f"Error al cargar formulario de edición: {e}")
    
    def registro_estudiantes(self):
        """Formulario para registrar nuevos estudiantes"""
        try:
            from database import execute_query, ejecutar_transaccion
            from gestion_carreras import obtener_carreras_activas
            
            with st.form("form_registro_estudiante"):
                st.subheader("Registrar Nuevo Estudiante")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    cedula = st.text_input("Cédula*", key="reg_cedula")
                    nombre = st.text_input("Nombre*", key="reg_nombre")
                    apellido = st.text_input("Apellido*", key="reg_apellido")
                    email = st.text_input("Email", key="reg_email")
                    telefono = st.text_input("Teléfono", key="reg_telefono")
                
                with col2:
                    fecha_nacimiento = st.date_input("Fecha de Nacimiento", key="reg_fecha_nacimiento")
                    sexo = st.selectbox("Género", ["Masculino", "Femenino"], key="reg_sexo")
                    direccion = st.text_area("Dirección", key="reg_direccion")
                
                # Obtener carreras dinámicamente
                carreras = obtener_carreras_activas()
                if carreras:
                    carrera_opciones = {c['nombre_carrera']: c['id_carrera'] for c in carreras}
                    carrera_nombre = st.selectbox("Carrera*", options=list(carrera_opciones.keys()), key="reg_carrera")
                    id_carrera = carrera_opciones[carrera_nombre]
                else:
                    st.error("No hay carreras disponibles")
                    return
                
                semestre = st.number_input("Semestre*", min_value=1, max_value=20, value=1, key="reg_semestre")
                estado = st.selectbox("Estado", ["Activo", "Inactivo"], key="reg_estado")
                
                if st.form_submit_button("Registrar Estudiante", type="primary"):
                    # Validaciones
                    if not cedula or not nombre or not apellido:
                        st.error("Cédula, nombre y apellido son obligatorios")
                        return
                    
                    if not id_carrera:
                        st.error("Debe seleccionar una carrera")
                        return
                    
                    # Validar permisos de creación
                    from seguridad import tiene_permiso
                    if not tiene_permiso(st.session_state.get('user_role'), 'Gestión Estudiantil', 'crear'):
                        st.warning("No tienes permisos para registrar nuevos estudiantes.")
                        return
                    
                    # Verificar si ya existe
                    check_query = "SELECT cedula FROM persona WHERE cedula = %s"
                    existing = execute_query(check_query, (cedula,), fetch_one=True)
                    
                    if existing:
                        st.error("Ya existe una persona con esta cédula")
                        return
                    
                    # Insertar datos
                    insert_queries = [
                        (
                            """INSERT INTO persona (cedula, nombre, apellido, email, telefono, 
                                fecha_nacimiento, genero, direccion, creado_en) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)""",
                            (cedula, nombre, apellido, email, telefono, fecha_nacimiento, genero, direccion)
                        ),
                        (
                            """INSERT INTO estudiante (cedula_estudiante, id_carrera, semestre_actual, 
                                estado_registro, fecha_ingreso, fecha_creacion) 
                                VALUES (%s, %s, %s, %s, CURRENT_DATE, CURRENT_TIMESTAMP)""",
                            (cedula, id_carrera, semestre, estado)
                        )
                    ]
                    
                    resultado = ejecutar_transaccion(insert_queries)
                    
                    if resultado.get('success'):
                        st.success("Estudiante registrado exitosamente")
                        st.rerun()
                    else:
                        st.error(f"Error al registrar estudiante: {resultado.get('message', 'Error desconocido')}")

        except Exception as e:
            st.error(f"Error en formulario de registro: {e}")

# Función principal para compatibilidad
def gestion_estudiantil_main():
    """Función principal para el módulo de gestión estudiantil"""
    print("DEBUG_ESTUDIANTIL_MAIN: Iniciando función principal")
    try:
        gestion = GestionEstudiantil()
        print("DEBUG_ESTUDIANTIL_MAIN: Instancia creada, llamando a gestión_estudiantil()")
        gestion.gestion_estudiantil()
        print("DEBUG_ESTUDIANTIL_MAIN: gestión_estudiantil() completada")
    except Exception as e:
        print(f"DEBUG_ESTUDIANTIL_ERROR: Error en módulo: {e}")
        import traceback
        print(f"DEBUG_ESTUDIANTIL_ERROR: Traceback: {traceback.format_exc()}")
        st.error(f"Error al iniciar módulo de gestión estudiantil: {e}")
