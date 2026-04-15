#!/usr/bin/env python3
# Módulo de Gestión Estudiantil con Perfiles de Estudiantes y Profesores

import streamlit as st
import pandas as pd
from configuracion import get_carreras, get_semestres, get_estados_registro, get_generos
from transacciones import TransaccionFOC26
from seguridad import SeguridadFOC26, admin_required, profesor_required, estudiante_required, mostrar_alerta_permisos_denegados, filtrar_datos_por_usuario


def modulo_gestion_estudiantil(db):
    """Módulo completo de gestión estudiantil con perfiles y búsquedas dinámicas"""
    try:
        st.header("Gestión de Perfiles Académicos")
        trans_manager = TransaccionFOC26(db.connection)

        # Definir tabs según rol de usuario
        tabs_disponibles = []
        
        if SeguridadFOC26.is_admin():
            tabs_disponibles = [
                "Estudiantes", "Nuevo Estudiante", 
                "Profesores", "Nuevo Profesor", 
                "Estadísticas"
            ]
        elif SeguridadFOC26.is_profesor():
            tabs_disponibles = [
                "Estudiantes", "Profesores", "Estadísticas"
            ]
        elif SeguridadFOC26.is_estudiante():
            tabs_disponibles = [
                "Estudiantes"  # Solo puede ver su propio perfil
            ]
        else:
            mostrar_alerta_permisos_denegados("No tiene permisos para acceder a la gestión estudiantil.")
            st.stop()
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(tabs_disponibles + [""] * (5 - len(tabs_disponibles)))

        with tab1:
            st.subheader("🔍 Buscar Estudiantes")
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                search_cedula = st.text_input("Cédula", placeholder="V-12345678")
                search_nombre = st.text_input("Nombre o apellido", placeholder="Juan Pérez")
            with col2:
                search_carrera = st.text_input("Carrera", placeholder="Ingeniería de Sistemas")
                search_semestre = st.text_input("Semestre", placeholder="III Semestre")
            with col3:
                if st.button("🔎 Buscar Estudiantes"):
                    st.session_state['_buscar_estudiantes'] = True
                if st.button("🔄 Limpiar filtros"):
                    for key in ['_buscar_estudiantes']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.experimental_rerun()

            if st.session_state.get('_buscar_estudiantes', False) or any([search_cedula, search_nombre, search_carrera, search_semestre]):
                # Aplicar filtros de seguridad según rol
                if SeguridadFOC26.is_estudiante():
                    # Estudiante solo busca su propio perfil
                    user_cedula = SeguridadFOC26.get_user_cedula()
                    search_cedula = user_cedula
                    search_nombre = ""
                    search_carrera = ""
                    search_semestre = ""
                    st.info(f"Mostrando su perfil (Cédula: {user_cedula})")
                
                estudiantes = trans_manager.buscar_estudiantes(
                    cedula=search_cedula,
                    nombre=search_nombre,
                    carrera=search_carrera,
                    semestre=search_semestre
                )
                
                # Filtrar resultados según rol
                if estudiantes and not SeguridadFOC26.is_admin():
                    estudiantes = filtrar_datos_por_usuario(estudiantes, 'cedula')
                
                if estudiantes:
                    df_estudiantes = pd.DataFrame(estudiantes)
                    st.dataframe(df_estudiantes, use_container_width=True)

                    estudiante_cedula = st.selectbox("Seleccionar estudiante para editar", df_estudiantes['cedula'].tolist())
                    seleccionado = df_estudiantes[df_estudiantes['cedula'] == estudiante_cedula].iloc[0]

                    with st.expander("Editar perfil del estudiante"):
                        col1, col2 = st.columns(2)
                        with col1:
                            nombre_actual = st.text_input("Nombre", value=seleccionado['nombre'])
                            apellido_actual = st.text_input("Apellido", value=seleccionado['apellido'])
                            email_actual = st.text_input("Email", value=seleccionado['email'])
                            telefono_actual = st.text_input("Teléfono", value=seleccionado['telefono'])
                        with col2:
                            carrera_actual = st.selectbox(
                                "Carrera",
                                get_carreras(),
                                index=get_carreras().index(seleccionado['carrera']) if seleccionado.get('carrera') in get_carreras() else 0
                            )
                            semestre_actual = st.selectbox(
                                "Semestre",
                                get_semestres(),
                                index=get_semestres().index(seleccionado['semestre_actual']) if seleccionado.get('semestre_actual') in get_semestres() else 0
                            )
                            estado_actual = st.selectbox(
                                "Estado",
                                get_estados_registro(),
                                index=get_estados_registro().index(seleccionado['estado']) if seleccionado.get('estado') in get_estados_registro() else 0
                            )

                        if st.button("Actualizar Estudiante"):
                            db.ejecutar_consulta(
                                "UPDATE persona SET nombre = %s, apellido = %s, email = %s, telefono = %s WHERE id = %s",
                                (nombre_actual.strip(), apellido_actual.strip(), email_actual.strip(), telefono_actual.strip(), seleccionado['id'])
                            )
                            db.ejecutar_consulta(
                                "UPDATE estudiante SET id_carrera = %s, id_semestre_formacion = %s, id_estado_registro = %s WHERE id_persona = %s",
                                (
                                    trans_manager.obtener_id_carrera(carrera_actual),
                                    trans_manager.obtener_id_semestre(semestre_actual),
                                    trans_manager.obtener_id_estado_registro(estado_actual),
                                    seleccionado['id']
                                )
                            )
                            st.success("Perfil de estudiante actualizado correctamente.")
                            st.experimental_rerun()
                else:
                    st.info("No se encontraron estudiantes con los filtros aplicados.")
            else:
                st.info("Use los filtros para buscar estudiantes.")

        with tab2:
            st.subheader("➕ Registrar Estudiante")
            with st.form("form_nuevo_estudiante"):
                col1, col2 = st.columns(2)
                with col1:
                    nombre = st.text_input("Nombre*", placeholder="Juan")
                    apellido = st.text_input("Apellido*", placeholder="Pérez González")
                    cedula = st.text_input("Cédula*", placeholder="V-12345678")
                    email = st.text_input("Email*", placeholder="juan.perez@iujo.edu")
                    telefono = st.text_input("Teléfono", placeholder="+58-212-1234567")
                with col2:
                    fecha_nacimiento = st.date_input("Fecha de Nacimiento")
                    genero = st.selectbox("Género", get_generos())
                    codigo_estudiantil = st.text_input("Código Estudiantil*", placeholder="EST-2026-001")
                    carrera = st.selectbox("Carrera*", get_carreras())
                    semestre_actual = st.selectbox("Semestre Actual*", get_semestres())
                    estado_registro = st.selectbox("Estado de Registro*", get_estados_registro())
                st.markdown("**El login y la contraseña temporal serán la cédula ingresada.**")
                if st.form_submit_button("Guardar Estudiante"):
                    if nombre and apellido and cedula and email and codigo_estudiantil and carrera and semestre_actual and estado_registro:
                        datos_estudiante = {
                            'nombre': nombre.strip(),
                            'apellido': apellido.strip(),
                            'cedula': str(cedula).strip(),
                            'email': email.strip(),
                            'telefono': telefono.strip(),
                            'fecha_nacimiento': fecha_nacimiento,
                            'genero': genero,
                            'direccion': '',
                            'codigo_estudiantil': codigo_estudiantil.strip(),
                            'carrera': carrera,
                            'semestre_actual': semestre_actual,
                            'estado': estado_registro
                        }
                        resultado = trans_manager.crear_estudiante_transaccional(datos_estudiante)
                        if resultado['exito']:
                            st.success('Estudiante registrado correctamente.')
                            st.info(f"Login temporal: {datos_estudiante['cedula']}")
                            st.info(f"Contraseña temporal: {datos_estudiante['cedula']}")
                        else:
                            st.error(f"Error: {resultado['error']}")
                    else:
                        st.error('Complete todos los campos obligatorios.')

        with tab3:
            st.subheader("🔍 Buscar Profesores")
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                search_cedula = st.text_input("Cédula", placeholder="V-12345678", key='prof_cedula')
                search_nombre = st.text_input("Nombre o apellido", placeholder="María López", key='prof_nombre')
            with col2:
                search_departamento = st.text_input("Departamento", placeholder="Computación", key='prof_departamento')
            with col3:
                if st.button("🔎 Buscar Profesores"):
                    st.session_state['_buscar_profesores'] = True
                if st.button("🔄 Limpiar filtros profesores"):
                    for key in ['_buscar_profesores']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.experimental_rerun()

            if st.session_state.get('_buscar_profesores', False) or any([search_cedula, search_nombre, search_departamento]):
                profesores = trans_manager.buscar_profesores(
                    cedula=search_cedula,
                    nombre=search_nombre,
                    departamento=search_departamento
                )
                if profesores:
                    df_profesores = pd.DataFrame(profesores)
                    st.dataframe(df_profesores, use_container_width=True)

                    profesor_cedula = st.selectbox("Seleccionar profesor para editar", df_profesores['cedula'].tolist())
                    seleccionado = df_profesores[df_profesores['cedula'] == profesor_cedula].iloc[0]
                    with st.expander("Editar perfil del profesor"):
                        col1, col2 = st.columns(2)
                        with col1:
                            nombre_actual = st.text_input("Nombre", value=seleccionado['nombre'])
                            apellido_actual = st.text_input("Apellido", value=seleccionado['apellido'])
                            email_actual = st.text_input("Email", value=seleccionado['email'])
                            telefono_actual = st.text_input("Teléfono", value=seleccionado['telefono'])
                        with col2:
                            especialidad_actual = st.text_input("Especialidad", value=seleccionado['especialidad'])
                            departamento_actual = st.text_input("Departamento", value=seleccionado['departamento'])
                            categoria_actual = st.text_input("Categoría", value=seleccionado['categoria'])
                            estado_actual = st.selectbox("Estado", ['Activo', 'Inactivo'], index=0 if seleccionado['estado'] == 'Activo' else 1)
                        if st.button("Actualizar Profesor"):
                            db.ejecutar_consulta(
                                "UPDATE persona SET nombre = %s, apellido = %s, email = %s, telefono = %s WHERE id = %s",
                                (nombre_actual.strip(), apellido_actual.strip(), email_actual.strip(), telefono_actual.strip(), seleccionado['id'])
                            )
                            db.ejecutar_consulta(
                                "UPDATE profesor SET especialidad = %s, departamento = %s, categoria = %s, estado = %s WHERE id_profesor = %s",
                                (especialidad_actual.strip(), departamento_actual.strip(), categoria_actual.strip(), estado_actual, seleccionado['id_profesor'])
                            )
                            st.success('Perfil de profesor actualizado correctamente.')
                            st.experimental_rerun()
                else:
                    st.info('No se encontraron profesores con los filtros aplicados.')
            else:
                st.info('Use los filtros para buscar profesores.')

        with tab4:
            st.subheader("➕ Registrar Profesor")
            with st.form("form_nuevo_profesor"):
                col1, col2 = st.columns(2)
                with col1:
                    nombre = st.text_input("Nombre*", placeholder="María")
                    apellido = st.text_input("Apellido*", placeholder="López Pérez")
                    cedula = st.text_input("Cédula*", placeholder="V-12345678")
                    email = st.text_input("Email*", placeholder="maria.lopez@iujo.edu")
                    telefono = st.text_input("Teléfono", placeholder="+58-212-1234567")
                with col2:
                    codigo_profesor = st.text_input("Código Profesor*", placeholder="PROF-2026-001")
                    especialidad = st.text_input("Especialidad*", placeholder="Matemáticas Aplicadas")
                    departamento = st.text_input("Departamento*", placeholder="Ingeniería de Sistemas")
                    categoria = st.text_input("Categoría*", placeholder="Titular")
                    estado = st.selectbox("Estado", ['Activo', 'Inactivo'])
                st.markdown("**El login y la contraseña temporal serán la cédula ingresada.**")
                if st.form_submit_button("Guardar Profesor"):
                    if nombre and apellido and cedula and email and codigo_profesor and especialidad and departamento and categoria:
                        datos_profesor = {
                            'nombre': nombre.strip(),
                            'apellido': apellido.strip(),
                            'cedula': str(cedula).strip(),
                            'email': email.strip(),
                            'telefono': telefono.strip(),
                            'direccion': '',
                            'codigo_profesor': codigo_profesor.strip(),
                            'especialidad': especialidad.strip(),
                            'departamento': departamento.strip(),
                            'categoria': categoria.strip(),
                            'estado': estado
                        }
                        resultado = trans_manager.crear_profesor_transaccional(datos_profesor)
                        if resultado['exito']:
                            st.success('Profesor registrado correctamente.')
                            st.info(f"Login temporal: {datos_profesor['cedula']}")
                            st.info(f"Contraseña temporal: {datos_profesor['cedula']}")
                        else:
                            st.error(f"Error: {resultado['error']}")
                    else:
                        st.error('Complete todos los campos obligatorios.')

        with tab5:
            st.subheader("📊 Estadísticas de perfiles")
            col1, col2, col3, col4 = st.columns(4)
            personas = db.ejecutar_consulta("SELECT COUNT(*) as total FROM persona") or [{'total': 0}]
            usuarios = db.ejecutar_consulta("SELECT COUNT(*) as total FROM usuario") or [{'total': 0}]
            estudiantes = db.ejecutar_consulta("SELECT COUNT(*) as total FROM estudiante") or [{'total': 0}]
            profesores = db.ejecutar_consulta("SELECT COUNT(*) as total FROM profesor") or [{'total': 0}]

            st.metric("👥 Total Personas", personas[0]['total'])
            st.metric("👤 Total Usuarios", usuarios[0]['total'])
            st.metric("🎓 Estudiantes", estudiantes[0]['total'])
            st.metric("👨‍🏫 Profesores", profesores[0]['total'])

            st.write("---")
            st.write("### Estudiantes por carrera")
            stats_carrera = db.ejecutar_consulta(
                "SELECT carrera, COUNT(*) as total FROM estudiante GROUP BY carrera ORDER BY total DESC"
            )
            if stats_carrera:
                st.dataframe(pd.DataFrame(stats_carrera), use_container_width=True)

            st.write("### Profesores por departamento")
            stats_prof = db.ejecutar_consulta(
                "SELECT departamento, COUNT(*) as total FROM profesor GROUP BY departamento ORDER BY total DESC"
            )
            if stats_prof:
                st.dataframe(pd.DataFrame(stats_prof), use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error en módulo de gestión estudiantil: {e}")
        print(f"Error en gestión estudiantil: {e}")
