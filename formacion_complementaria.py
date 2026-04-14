#!/usr/bin/env python3
# Módulo de Formación Complementaria con Transacciones FOC-2026-XXXX

import streamlit as st
from datetime import datetime, timedelta
from configuracion import get_tipos_taller, get_generos, get_niveles_academicos
from transacciones import TransaccionFOC26
from seguridad import SeguridadFOC26, mostrar_boton_crear_taller, mostrar_boton_inscribirse, mostrar_alerta_permisos_denegados

def modulo_formacion_complementaria(db):
    """Módulo completo de Formación Complementaria con transacciones"""
    try:
        st.header("Formación Complementaria")
        
        trans_manager = TransaccionFOC26(db.connection)
        
        # Tabs para diferentes operaciones - CORREGIDO: Reestructurar para evitar tab3
        tab1, tab2 = st.tabs([
            "Creación de Taller", 
            "Talleres e Inscripciones"
        ])
        
        with tab1:
            st.subheader("Crear Nuevo Taller")
            
            # Verificar permisos para crear talleres
            if not SeguridadFOC26.can_create_taller():
                mostrar_alerta_permisos_denegados("Solo los profesores y administradores pueden crear talleres.")
                st.stop()
            
            with st.form("form_crear_taller"):
                col1, col2 = st.columns(2)
                
                with col1:
                    codigo_taller = st.text_input("Código del Taller*", placeholder="TAL-2026-001")
                    nombre_taller = st.text_input("Nombre del Taller*", placeholder="Programación Básica")
                    descripcion = st.text_area("Descripción", placeholder="Descripción detallada del taller")
                    tipo_taller = st.selectbox("Tipo de Taller*", get_tipos_taller(), key="tipo_taller_crear")
                    cupo_maximo = st.number_input("Cupo Máximo*", min_value=1, max_value=100, value=30)
                    fecha_inicio = st.date_input("Fecha de Inicio*", value=datetime.now().date())
                    duracion_semanas = st.number_input("Duración (semanas)*", min_value=1, max_value=16, value=4)
                    nivel_academico = st.selectbox("Nivel Académico*", get_niveles_academicos(), key="nivel_academico_crear")
                
                with col2:
                    st.write("📝 **Información Adicional:**")
                    st.info("El taller se creará con ID de transacción FOC-2026-XXXX")
                    st.info("Se registrará automáticamente en auditoría")
                    st.info("El cupo se actualizará con cada inscripción")
                    
                    profesores_disponibles = trans_manager.obtener_profesores_activos()
                    if profesores_disponibles:
                        opciones_profesores = ["Seleccione un instructor"] + [
                            f"{item['cedula_profesor']} - {item['apellido']}, {item['nombre']} ({item['especialidad']})"
                            for item in profesores_disponibles
                        ]
                        profesor_seleccionado = st.selectbox("Instructor*", opciones_profesores, key="profesor_crear")
                        cedula_profesor = profesor_seleccionado.split(' - ')[0] if profesor_seleccionado != "Seleccione un instructor" else None
                    else:
                        st.warning("No hay profesores activos registrados. Registre un profesor primero.")
                        cedula_profesor = None

                    requisitos = st.text_area("Requisitos", placeholder="Conocimientos previos requeridos")
                    material_didactico = st.text_area("Material Didáctico", placeholder="Libros, software, etc.")
                    
                    # Cálculo de fecha fin
                    if fecha_inicio and duracion_semanas:
                        fecha_fin = fecha_inicio + timedelta(weeks=duracion_semanas)
                        st.write(f"📅 **Fecha Fin:** {fecha_fin}")
                
                col_boton1, col_boton2 = st.columns(2)
                
                with col_boton1:
                    if st.form_submit_button("🏗️ Crear Taller"):
                        if (codigo_taller and nombre_taller and descripcion and tipo_taller and cupo_maximo and fecha_inicio and duracion_semanas and nivel_academico and cedula_profesor):
                            datos_taller = {
                                'codigo': codigo_taller.strip(),
                                'nombre_taller': nombre_taller.strip(),
                                'descripcion': descripcion.strip(),
                                'tipo_taller': tipo_taller,
                                'cupo_maximo': cupo_maximo,
                                'fecha_inicio': fecha_inicio,
                                'fecha_fin': fecha_inicio + timedelta(weeks=duracion_semanas),
                                'nivel_academico': nivel_academico,
                                'requisitos': requisitos.strip(),
                                'material_didactico': material_didactico.strip(),
                                'estado': 'Activo'
                            }
                            
                            resultado = trans_manager.crear_taller_transaccional(datos_taller, cedula_profesor)
                            
                            if resultado['exito']:
                                st.success(f"✅ Taller creado exitosamente")
                                st.info(f"📋 ID Transacción: {resultado['id_transaccion']}")
                                st.info(f"🏗️ ID Taller: {resultado['id_taller']}")
                                st.rerun()
                            else:
                                st.error(f"❌ Error: {resultado['error']}")
                        else:
                            st.error("⚠️ Complete todos los campos obligatorios y seleccione un profesor")
                
                with col_boton2:
                    if st.form_submit_button("🗑️ Limpiar Formulario"):
                        st.rerun()
        
        with tab2:
            st.subheader("📋 Talleres Disponibles")
            
            # Filtros de búsqueda
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filtro_tipo = st.selectbox("Tipo de Taller", ["Todos"] + get_tipos_taller())
                filtro_nivel = st.selectbox("Nivel Académico", ["Todos"] + get_niveles_academicos())
            
            with col2:
                filtro_estado = st.selectbox("Estado", ["Todos", "Activo", "Inactivo", "Finalizado"])
            
            with col3:
                if st.button("🔄 Actualizar Lista"):
                    st.rerun()
            
            # Construir consulta dinámica usando formación y taller con filtros de seguridad
            query = """
                SELECT f.id_formacion, t.id_taller, t.nombre_taller, f.nombre_cohorte, f.descripcion,
                       f.fecha_inicio, f.fecha_fin, f.cupos_maximos, f.cupos_disponibles,
                       f.instructor, f.estado
                FROM formacion f
                JOIN taller t ON f.id_taller = t.id_taller
                WHERE 1=1
            """
            
            # Aplicar filtros de seguridad
            params = []
            if SeguridadFOC26.is_estudiante():
                # Estudiante solo ve talleres activos
                query += " AND f.estado = 'Activo'"
            elif SeguridadFOC26.is_profesor():
                # Profesor solo ve sus talleres
                user_cedula = SeguridadFOC26.get_user_cedula()
                query += " AND f.instructor LIKE %s"
                params.append(f"%{user_cedula}%")
            # Admin ve todos (sin filtro adicional)
            params = []
            
            if filtro_tipo != "Todos":
                query += " AND f.nombre_cohorte ILIKE %s"
                params.append(f"%{filtro_tipo}%")
            
            if filtro_nivel != "Todos":
                query += " AND f.descripcion ILIKE %s"
                params.append(f"%{filtro_nivel}%")
            
            if filtro_estado != "Todos":
                query += " AND f.estado = %s"
                params.append(filtro_estado)
            
            query += " ORDER BY f.fecha_inicio DESC"
            
            resultado = db.ejecutar_consulta(query, params)
            
            if resultado is not None and len(resultado) > 0:
                st.dataframe(resultado, use_container_width=True)
                
                # Estadísticas de la vista
                st.write("---")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_formaciones = len(resultado)
                    st.metric("🏗️ Total Formaciones", total_formaciones)
                
                with col2:
                    formaciones_activas = len([r for r in resultado if r['estado'] == 'Activo'])
                    st.metric("✅ Formaciones Activas", formaciones_activas)
                
                with col3:
                    cupo_total = sum(r['cupos_maximos'] for r in resultado)
                    cupo_disponible = sum(r['cupos_disponibles'] for r in resultado)
                    st.metric(" Cupos Disponibles", cupo_disponible)
            else:
                st.info("No hay talleres disponibles")
        
        # CORREGIDO: Reestructurar tab2 para incluir listado e inscripciones
        with tab2:
            st.subheader("Listado de Talleres")
            
            # Filtros de búsqueda
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filtro_tipo = st.selectbox("Tipo de Taller", ["Todos"] + get_tipos_taller(), key="filtro_tipo_listado")
                filtro_nivel = st.selectbox("Nivel Académico", ["Todos"] + get_niveles_academicos(), key="filtro_nivel_listado")
            
            with col2:
                filtro_estado = st.selectbox("Estado", ["Todos", "Activo", "Inactivo", "Finalizado"], key="filtro_estado_listado")
            
            with col3:
                if st.button("Actualizar Lista"):
                    st.rerun()
            
            # Construir consulta dinámica usando formación y taller con filtros de seguridad
            query = """
                SELECT f.id_formacion, t.id_taller, t.nombre_taller, f.nombre_cohorte, f.descripcion,
                       f.fecha_inicio, f.fecha_fin, f.cupos_maximos, f.cupos_disponibles,
                       f.instructor, f.estado
                FROM formacion f
                JOIN taller t ON f.id_taller = t.id_taller
                WHERE 1=1
            """
            
            params = []
            
            if filtro_tipo != "Todos":
                query += " AND t.tipo_taller = %s"
                params.append(filtro_tipo)
            
            if filtro_nivel != "Todos":
                query += " AND t.nivel_academico = %s"
                params.append(filtro_nivel)
            
            if filtro_estado != "Todos":
                query += " AND f.estado = %s"
                params.append(filtro_estado)
            
            query += " ORDER BY f.fecha_inicio DESC"
            
            resultado = db.ejecutar_consulta(query, params)
            
            if resultado is not None and len(resultado) > 0:
                st.dataframe(resultado, use_container_width=True)
                
                # Estadísticas de la vista
                st.write("---")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_formaciones = len(resultado)
                    st.metric("Total Formaciones", total_formaciones)
                
                with col2:
                    formaciones_activas = len([r for r in resultado if r['estado'] == 'Activo'])
                    st.metric("Formaciones Activas", formaciones_activas)
                
                with col3:
                    cupo_total = sum(r['cupos_maximos'] for r in resultado)
                    cupo_disponible = sum(r['cupos_disponibles'] for r in resultado)
                    st.metric("Cupos Disponibles", cupo_disponible)
            else:
                st.info("No hay talleres disponibles")
            
            st.write("---")
            st.subheader("Gestión de Inscripciones")
            
            # Verificar permisos para inscripciones
            if SeguridadFOC26.is_estudiante():
                # Estudiante solo puede inscribirse a sí mismo
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("Inscribirse en Taller:")
                    
                    # Obtener datos del estudiante logueado
                    user_cedula = SeguridadFOC26.get_user_cedula()
                    estudiante_actual = db.ejecutar_consulta("""
                        SELECT u.id as id_usuario, p.nombre, p.apellido, e.cedula_estudiante
                        FROM estudiante e
                        JOIN usuario u ON e.id_usuario = u.id
                        JOIN persona p ON e.id_persona = p.id
                        WHERE u.cedula_usuario = %s AND u.rol = 'Estudiante'
                    """, (user_cedula,))
                    
                    if estudiante_actual is not None and len(estudiante_actual) > 0:
                        estudiante_datos = estudiante_actual[0]
                        id_estudiante = estudiante_datos['id_usuario']
                        st.info(f"Estudiante: {estudiante_datos['apellido']}, {estudiante_datos['nombre']}")
                        st.info(f"Cédula: {estudiante_datos['cedula_estudiante']}")
                        
                        # Seleccionar formación activa
                        formaciones = db.ejecutar_consulta("""
                            SELECT f.id_formacion, t.nombre_taller, f.nombre_cohorte, f.cupos_maximos, f.cupos_disponibles, f.estado
                            FROM formacion f
                            JOIN taller t ON f.id_taller = t.id_taller
                            WHERE f.estado = 'Activo' AND f.cupos_disponibles > 0
                            ORDER BY f.fecha_inicio
                        """)
                        
                        if formaciones is not None and len(formaciones) > 0:
                            opciones_formaciones = [f"{row['nombre_cohorte']} - {row['nombre_taller']} (Disponibles: {row['cupos_disponibles']})" for row in formaciones]
                            formacion_seleccionada = st.selectbox("Seleccionar Formación/Taller:", opciones_formaciones, key="formacion_seleccionar")
                            
                            nombre_cohorte_seleccionado = formacion_seleccionada.split(' - ')[0]
                            formacion_datos = next((r for r in formaciones if r['nombre_cohorte'] == nombre_cohorte_seleccionado), None)
                            if formacion_datos is None:
                                st.error("No se encontró la formación seleccionada")
                            else:
                                id_formacion = formacion_datos['id_formacion']
                                
                                if st.button("🎓 Inscribir Estudiante"):
                                    resultado = trans_manager.inscribir_estudiante_taller_transaccional(id_estudiante, id_formacion)
                                    
                                    if resultado['exito']:
                                        st.success(f"✅ Estudiante inscrito exitosamente")
                                        st.info(f"📋 ID Transacción: {resultado['id_transaccion']}")
                                        st.info(f"🎓 ID Inscripción: {resultado['id_inscripcion']}")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Error: {resultado['error']}")
                        else:
                            st.warning("No hay formaciones activas disponibles")
                    else:
                        st.warning("No hay estudiantes registrados")
            
            elif SeguridadFOC26.is_admin() or SeguridadFOC26.is_profesor():
                # Admin y profesor pueden ver inscripciones pero no inscribir
                col1, col2 = st.columns(2)
                
                with col2:
                    st.write("Consultar Inscripciones:")
                    
                    # Filtros de consulta
                    opciones_formaciones_ins = ["Todos"]
                    formaciones_ins = db.ejecutar_consulta("""
                        SELECT f.id_formacion, t.nombre_taller, f.nombre_cohorte
                        FROM formacion f
                        JOIN taller t ON f.id_taller = t.id_taller
                        ORDER BY f.fecha_inicio DESC
                    """)
                    if formaciones_ins is not None and len(formaciones_ins) > 0:
                        opciones_formaciones_ins += [f"{row['nombre_cohorte']} - {row['nombre_taller']}" for row in formaciones_ins]

                    filtro_taller = st.selectbox("Filtrar por Formación:", opciones_formaciones_ins, key="filtro_taller_inscripciones")
                    
                    if st.button("Consultar Inscripciones"):
                        query_inscripciones = """
                            SELECT i.id_inscripcion, i.fecha_inscripcion, i.estado,
                                   p.nombre, p.apellido, e.cedula_estudiante,
                                   t.nombre_taller, f.nombre_cohorte
                            FROM inscripcion i
                            JOIN usuario u ON i.id_usuario = u.id
                            JOIN persona p ON u.id_persona = p.id
                            JOIN estudiante e ON e.id_usuario = u.id
                            JOIN formacion f ON i.id_formacion = f.id_formacion
                            JOIN taller t ON f.id_taller = t.id_taller
                            WHERE 1=1
                        """
                        params_inscripciones = []
                        
                        if filtro_taller != "Todos":
                            query_inscripciones += " AND f.nombre_cohorte = %s"
                            params_inscripciones.append(filtro_taller)
                        
                        query_inscripciones += " ORDER BY i.fecha_inscripcion DESC"
                        
                        inscripciones = db.ejecutar_consulta(query_inscripciones, params_inscripciones)
                        
                        if inscripciones is not None and len(inscripciones) > 0:
                            st.dataframe(inscripciones, use_container_width=True)
                        else:
                            st.info("No hay inscripciones registradas")
        
            st.write("---")
            st.subheader("Reportes")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("📈 **Reporte de Transacciones:**")
                
                # Filtros de fecha
                fecha_inicio = st.date_input("Fecha Inicio", value=datetime.now().date() - timedelta(days=30))
                fecha_fin = st.date_input("Fecha Fin", value=datetime.now().date())
                
                if st.button("📊 Generar Reporte"):
                    resumen = trans_manager.obtener_resumen_transacciones(fecha_inicio, fecha_fin)
                    
                    if resumen:
                        st.dataframe(resumen, use_container_width=True)
                    else:
                        st.info("No hay transacciones en el período seleccionado")
            
            with col2:
                st.write("📋 **Reporte de Utilización:**")
                
                # Estadísticas de talleres
                stats_talleres = db.ejecutar_consulta("""
                    SELECT tipo_taller, COUNT(*) as total, SUM(cupo_maximo) as cupo_total, SUM(cupo_actual) as cupo_ocupado
                    FROM taller
                    GROUP BY tipo_taller
                """)
                
                if stats_talleres is not None and len(stats_talleres) > 0:
                    st.dataframe(stats_talleres, use_container_width=True)
                    
                    # Gráfico de utilización
                    st.write("---")
                    st.write("📊 **Gráfico de Utilización por Tipo de Taller:**")
                    
                    import pandas as pd
                    import matplotlib.pyplot as plt
                    
                    df_chart = pd.DataFrame(stats_talleres)
                    
                    if not df_chart.empty:
                        fig, ax = plt.subplots()
                        df_chart.plot(kind='bar', x='tipo_taller', y='total', ax=ax)
                        ax.set_title('Total de Talleres por Tipo')
                        ax.set_xlabel('Tipo de Taller')
                        ax.set_ylabel('Total')
                        plt.xticks(rotation=45)
                        plt.tight_layout()
                        
                        st.pyplot(fig)
                else:
                    st.info("No hay datos para generar reportes")
    
    except Exception as e:
        st.error(f"❌ Error en módulo de formación complementaria: {e}")
        print(f"Error en formación complementaria: {e}")
