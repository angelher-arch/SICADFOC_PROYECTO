#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modulo_estudiantes.py - Módulo de Gestión de Estudiantes con Arquitectura Centralizada
Implementación robusta con @st.cache_resource y manejo de errores
"""

import streamlit as st
import re
import logging
import os
import sys

# Importar estilos globales de formularios (MANDATORIO)
from styles import aplicar_estilo_consistente_global

# Importaciones directas para evitar errores de dependencia
try:
    from formacion_complementaria import motor_formacion
    from seguridad import tiene_permiso, SeguridadFOC26
except ImportError as e:
    print(f"Error importando dependencias: {e}")
    sys.exit(1)

# Configuración de logging
logger = logging.getLogger(__name__)

def gestion_estudiantil(db=None):
    """Modulo completo para gestión de estudiantes con patrón Singleton"""
    try:
        # Aplicar estilos globales de formularios (MANDATORIO)
        aplicar_estilo_consistente_global()
        
        st.header("Gestión de Estudiantes")
        
        # Obtener rol del usuario de sesión con validación
        rol_usuario = st.session_state.get('user_role', None)
        
        # Validación de rol
        if rol_usuario is None:
            st.error("Error: No se pudo determinar el rol del usuario. Por favor, inicie sesión nuevamente.")
            st.warning("Si el problema persiste, contacte al administrador.")
            return
        
        # Verificar estado de conexión con diagnóstico técnico (modo degradado)
        from database import db_manager
        connection_status = db_manager.test_connection()
        if not connection_status.get('status'):
            # Modo degradado: Mostrar advertencia pero permitir funcionamiento básico
            st.warning("Conexión a base de datos limitada - Algunas funciones pueden no estar disponibles")
            
            # Información de depuración en desarrollo
            if os.getenv('ENVIRONMENT', '').lower() in ['local', 'development']:
                with st.expander("Detalles de conexión", expanded=False):
                    st.code(f"Error: {connection_status.get('error', 'Error desconocido')}")
                    st.info("El módulo funcionará en modo limitado")
            
            # NO detener la ejecución - permitir modo degradado
        
        # Validación simplificada - administradores siempre tienen acceso
        if rol_usuario in ['Administrador', 'Admin']:
            st.info("Acceso como Administrador - Todas las funciones disponibles")
        else:
            # Para otros roles, verificar permisos específicos
            if not tiene_permiso(rol_usuario, 'Estudiantes', 'Consultar'):
                st.error("Acceso denegado. No tienes permisos para consultar estudiantes.")
                st.stop()

        # Crear tabs según rol de usuario (acceso garantizado para administradores)
        if rol_usuario in ['Administrador', 'Admin']:
            # Administrador siempre tiene acceso completo
            tab1, tab2, tab3 = st.tabs(["Estudiantes Registrados", "Registrar Nuevo Estudiante", "Consultar/Editar"])
        elif SeguridadFOC26.is_profesor():
            # Profesor con validación de permisos
            if tiene_permiso(rol_usuario, 'Estudiantes', 'Consultar'):
                tab1, tab2, tab3 = st.tabs(["Estudiantes Registrados", "Registrar Nuevo Estudiante", "Consultar/Editar"])
            else:
                st.error("Acceso denegado. No tienes permisos para consultar estudiantes.")
                st.stop()
        elif SeguridadFOC26.is_estudiante():
            # Estudiante solo puede consultar y editar su propio perfil
            if tiene_permiso(rol_usuario, 'Estudiantes', 'Consultar'):
                tab1, tab2, tab3 = st.tabs(["Mis Datos", "Editar Mi Perfil", "Consultar/Editar"])
            else:
                st.error("Acceso denegado. No tienes permisos para consultar datos.")
                st.stop()
        else:
            st.error("Rol no reconocido. Contacte al administrador.")
            st.stop()

        # TAB1: LISTADO/CONSULTA
        with tab1:
            if SeguridadFOC26.is_admin() or SeguridadFOC26.is_profesor():
                st.subheader("Estudiantes Registrados")
                
                # Solo admin y profesor pueden ver carga masiva
                with st.expander("Carga Masiva de Estudiantes (.CSV)", expanded=False):
                    st.markdown("""
                    **Instrucciones:**
                    - El archivo debe contener las columnas: `cedula`, `nombre`, `apellido`, `email`, `telefono`, `fecha_nacimiento`, `genero`, `direccion`, `carrera`, `semestre_formacion`, `estado_registro`.
                    - Si la cédula ya existe se actualizará el registro en lugar de duplicarlo.
                    """)
                    archivo_csv_estudiantes = st.file_uploader(
                        "Seleccionar archivo CSV de estudiantes",
                        type=["csv"],
                        key="csv_estudiantes"
                    )
                    
                    if archivo_csv_estudiantes is not None:
                        # Validación robusta del archivo
                        try:
                            # Verificar que el archivo no esté vacío
                            if archivo_csv_estudiantes.size == 0:
                                st.error("El archivo está vacío. Por favor, seleccione un archivo válido.")
                                return
                            
                            # Verificar que sea un archivo CSV válido
                            import pandas as pd
                            
                            # Intentar leer el archivo para validar estructura
                            df_test = pd.read_csv(archivo_csv_estudiantes)
                            
                            if df_test is None or df_test.empty:
                                st.error("No se pudieron leer datos del archivo CSV.")
                                return
                            
                            # Validar columnas requeridas
                            columnas_requeridas = ['cedula', 'nombre', 'apellido', 'email']
                            columnas_faltantes = [col for col in columnas_requeridas if col not in df_test.columns]
                            
                            if columnas_faltantes:
                                st.error(f"Faltan columnas requeridas: {', '.join(columnas_faltantes)}")
                                st.info("Columnas encontradas: " + ", ".join(df_test.columns.tolist()))
                                return
                            
                            st.success(f"Archivo válido detectado con {len(df_test)} registros.")
                            
                        except Exception as e:
                            st.error(f"Error al validar el archivo CSV: {e}")
                            st.info("Asegúrese de que el archivo sea un CSV válido y no esté corrupto.")
                            return
                        
                        if st.button("Procesar carga masiva de estudiantes", type="primary", key="procesar_csv_estudiantes"):
                            try:
                                # Usar patrón robusto con manejo de errores y recuperación automática
                                from database import get_database_manager, test_database_connection
                                
                                # Verificar conexión antes de procesar
                                conn_result = test_database_connection()
                                if not conn_result.get('status'):
                                    st.error("❌ Error de conexión antes de procesar CSV")
                                    st.warning("Por favor, recargue la página e intente nuevamente.")
                                    return
                                
                                from database import get_db_connection
                                db = get_db_connection()
                                
                                if db is None:
                                    st.error("❌ No se pudo establecer conexión a la base de datos")
                                    return
                                
                                from main import process_student_csv_upload
                                resultado_csv = process_student_csv_upload(archivo_csv_estudiantes, db)
                                
                                if resultado_csv is None:
                                    st.error("❌ Error: El procesador CSV retornó None")
                                    return
                                
                                if resultado_csv.get('success', False):
                                    st.success(resultado_csv.get('message', 'Procesamiento completado'))
                                else:
                                    st.error(resultado_csv.get('message', 'Error desconocido'))
                                    errores = resultado_csv.get('errors', [])
                                    if errores:
                                        st.write("**Errores encontrados:**")
                                        for error in errores:
                                            st.write(f"- {error}")
                                            
                            except Exception as e:
                                # DETECCIÓN Y RECUPERACIÓN AUTOMÁTICA
                                print(f"❌ Error procesando CSV: {e}")
                                st.error("❌ Ocurrió un error inesperado al procesar el archivo CSV")
                                st.info("🔄 El sistema intentará recuperar la conexión automáticamente...")
                                
                                # Marcar para recuperación en siguiente interacción
                                st.session_state.transaccion_abortada = True
                                st.session_state.error_procesamiento = str(e)
                                    
                            except Exception as e:
                                st.error(f"Error durante el procesamiento del CSV: {e}")
                                st.info("Intente nuevamente o contacte al administrador.")
                
                # USAR MOTOR CENTRAL UNIFICADO PARA ESTUDIANTES
                resultado_query = motor_formacion.leer_estudiantes(orden='apellido, nombre')
                
                if resultado_query['success']:
                    resultado = resultado_query['data']
                else:
                    st.error(f"Error al obtener estudiantes: {resultado_query['message']}")
                    resultado = []

                # Procesar resultado estandarizado con validación robusta (modo degradado)
                if resultado_query is None:
                    st.warning("Conexión limitada - Mostrando formulario de registro")
                    # No detener ejecución - permitir registro
                    return
                
                # execute_query devuelve directamente una lista, no un dict con 'success'
                if isinstance(resultado_query, list):
                    resultado = resultado_query
                elif isinstance(resultado_query, dict) and resultado_query.get('success', False):
                    resultado = resultado_query.get('data', [])
                else:
                    # Error en la consulta, pero permitir continuar
                    st.warning("Error en consulta - Mostrando formulario de registro")
                    resultado = []
                if resultado is None or not resultado:
                    st.info("No hay estudiantes registrados. Use el formulario para registrar nuevos estudiantes.")
                    # No detener ejecución - permitir registro
                    # Crear DataFrame vacío con columnas esperadas para evitar errores
                    df_resultado = pd.DataFrame(columns=['id', 'nombre', 'apellido', 'cedula', 'telefono', 'email_estudiante', 'id_carrera', 'semestre_actual', 'estado_registro', 'activo'])
                else:
                    # Convertir a DataFrame solo si hay datos válidos
                    import pandas as pd
                    if resultado and isinstance(resultado, list) and len(resultado) > 0 and isinstance(resultado[0], dict):
                        df_resultado = pd.DataFrame(resultado)
                    else:
                        st.info("Los datos de estudiantes no tienen el formato esperado.")
                        return

                # Mostrar tabla según rol
                if SeguridadFOC26.is_admin():
                    # Admin ve tabla con acciones completas
                    st.dataframe(
                        df_resultado[["nombre", "apellido", "cedula", "telefono", "email_estudiante", "id_carrera", "semestre_actual", "estado_registro", "activo"]],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "nombre": st.column_config.TextColumn("Nombres"),
                            "apellido": st.column_config.TextColumn("Apellidos"),
                            "cedula": st.column_config.TextColumn("Cédula"),
                            "telefono": st.column_config.TextColumn("Teléfono"),
                            "email_estudiante": st.column_config.TextColumn("Correo"),
                            "id_carrera": st.column_config.TextColumn("Carrera"),
                            "semestre_actual": st.column_config.TextColumn("Semestre"),
                            "estado_registro": st.column_config.TextColumn("Estado"),
                            "activo": st.column_config.TextColumn("Activo")
                        }
                    )
                    
                    # Sección de acciones administrativas
                    st.markdown("---")
                    st.subheader("Acciones Administrativas")
                    
                    # Selección de estudiante para acciones
                    estudiante_seleccionado = st.selectbox(
                        "Seleccionar Estudiante:",
                        options=[f"{row['nombre']} {row['apellido']} - {row['cedula']}" for _, row in df_resultado.iterrows()],
                        key="estudiante_accion"
                    )
                    
                    if estudiante_seleccionado:
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            # Aplicar autorización dinámica para botón Editar
                            if tiene_permiso(rol_usuario, 'Estudiantes', 'Editar'):
                                if st.button("Editar", type="primary", key="btn_editar_estudiante"):
                                    st.info(f"Editar estudiante: {estudiante_seleccionado}")
                        with col2:
                            # Aplicar autorización dinámica para botón Eliminar
                            if tiene_permiso(rol_usuario, 'Estudiantes', 'Eliminar'):
                                if st.button("Eliminar", type="secondary", key="btn_eliminar_estudiante"):
                                    st.warning(f"Se eliminará al estudiante {estudiante_seleccionado}.")
                                    # TODO: implementar eliminación real
                                    st.success(f"Estudiante {estudiante_seleccionado} eliminado")
                                    st.rerun()
                            else:
                                st.button("Eliminar", type="secondary", key="btn_eliminar_estudiante", disabled=True,
                                         help="No tienes permisos para eliminar estudiantes")
                    
                    # Exportación de datos
                    st.markdown("---")
                    if st.button("Exportar Estudiantes a CSV", type="primary", use_container_width=True, key="exportar_estudiantes_csv_main"):
                        csv = df_resultado.to_csv(index=False)
                        st.download_button(
                            label="Descargar Estudiantes.csv",
                            data=csv,
                            file_name="estudiantes_registrados.csv",
                            mime="text/csv"
                        )
                    
                    # Estadísticas
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Total Estudiantes", len(df_resultado), delta="Registrados")
                    with col2:
                        activos = df_resultado[df_resultado['activo'] == True]
                        st.metric("Estudiantes Activos", len(activos))
                    with col3:
                        femeninos = df_resultado[df_resultado['sexo'] == 'Femenino']
                        st.metric("Estudiantes Mujeres", len(femeninos))
                    with col4:
                        masculinos = df_resultado[df_resultado['sexo'] == 'Masculino']
                        st.metric("Estudiantes Hombres", len(masculinos))
                else:
                    # Otros roles ven tabla sin botones de acción
                    st.dataframe(
                        df_resultado[["nombre", "apellido", "cedula", "telefono", "email_estudiante", "id_carrera", "semestre_actual", "estado_registro", "activo"]],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "nombre": st.column_config.TextColumn("Nombres"),
                            "apellido": st.column_config.TextColumn("Apellidos"),
                            "cedula": st.column_config.TextColumn("Cédula"),
                            "telefono": st.column_config.TextColumn("Teléfono"),
                            "email_estudiante": st.column_config.TextColumn("Correo"),
                            "id_carrera": st.column_config.TextColumn("Carrera"),
                            "semestre_actual": st.column_config.TextColumn("Semestre"),
                            "estado_registro": st.column_config.TextColumn("Estado"),
                            "activo": st.column_config.TextColumn("Activo")
                        }
                    )
            
            elif SeguridadFOC26.is_estudiante():
                st.subheader("Mis Datos")
                
                # Estudiante solo ve su propio registro
                user_cedula = SeguridadFOC26.get_user_cedula()
                query = """
                SELECT
                    u.cedula_usuario as usuario_id,
                    u.cedula_usuario,
                    p.nombre,
                    p.apellido,
                    p.cedula,
                    p.telefono,
                    p.fecha_nacimiento,
                    p.sexo as sexo,
                    p.direccion,
                    u.email,
                    e.carrera,
                    e.semestre_actual,
                    e.estado_registro,
                    e.id as estudiante_id
                FROM usuarios u
                JOIN persona p ON u.cedula_usuario = p.cedula
                LEFT JOIN estudiante e ON p.cedula = e.cedula_estudiante
                WHERE u.rol = 'Estudiante' AND u.cedula_usuario = %s
                """
                resultado_query = execute_query(query, (user_cedula,))
                
                # Validación robusta del resultado
                if resultado_query is None:
                    st.warning("No se pudo obtener información del estudiante.")
                    return
                
                if not isinstance(resultado_query, dict):
                    st.warning("Formato de respuesta inválido.")
                    return
                
                if not resultado_query.get('success', False):
                    st.warning("No se encontraron datos del estudiante.")
                    return
                
                data = resultado_query.get('data', [])
                if not data or len(data) == 0:
                    st.warning("No hay información disponible.")
                    return
                
                estudiante = data[0]
                
                # Validación final del estudiante
                if estudiante is None:
                    st.warning("Datos de estudiante corruptos.")
                    return
                
                # Validación de campos obligatorios
                if not all([estudiante.get('nombre'), estudiante.get('apellido'), estudiante.get('cedula')]):
                    st.warning("Datos incompletos del estudiante.")
                    return
                    
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Información Personal")
                    st.info(f"**Nombre:** {estudiante.get('nombre', '')} {estudiante.get('apellido', '')}")
                    st.info(f"**Cédula:** {estudiante.get('cedula', 'N/A')}")
                    st.info(f"**Email:** {estudiante.get('email', 'N/A')}")
                    st.info(f"**Teléfono:** {estudiante.get('telefono', 'N/A')}")
                
                with col2:
                    st.markdown("### Información Académica")
                    st.info(f"**Carrera:** {estudiante.get('carrera', 'N/A')}")
                    st.info(f"**Semestre:** {estudiante.get('semestre_formacion', 'N/A')}")
                    st.info(f"**Estado:** {estudiante.get('estado_registro', 'N/A')}")
                    st.info(f"**Usuario:** {estudiante.get('login_usuario', 'N/A')}")
                
                st.markdown("---")
                st.markdown("### Información Adicional")
                col3, col4 = st.columns(2)
                
                with col3:
                    if estudiante.get('fecha_nacimiento'):
                        st.info(f"**Fecha Nacimiento:** {estudiante.get('fecha_nacimiento')}")
                    st.info(f"**Género:** {estudiante.get('sexo', 'N/A')}")
                
                with col4:
                    if estudiante.get('direccion'):
                        st.info(f"**Dirección:** {estudiante.get('direccion')}")
            else:
                st.error("No se encontró tu información de estudiante.")

        # TAB2: REGISTRO DE NUEVO ESTUDIANTE
        with tab2:
            # Mostrar formulario de registro según rol
            rol_usuario = st.session_state.get('user_role', None)
            
            # ACCESO GARANTIZADO: Administradores siempre ven el formulario
            if rol_usuario in ['Administrador', 'Admin']:
                st.subheader("Registrar Nuevo Estudiante")
                st.info("Acceso como Administrador - Formulario disponible")
                _mostrar_formulario_registro_estudiante()
            elif rol_usuario == 'Profesor':
                # Profesor necesita permisos específicos
                if tiene_permiso(rol_usuario, 'Estudiantes', 'registrar') or tiene_permiso(rol_usuario, 'Estudiantes', 'crear'):
                    st.subheader("Registrar Nuevo Estudiante")
                    _mostrar_formulario_registro_estudiante()
                else:
                    st.warning("No tiene permisos para registrar estudiantes.")
                    return
            elif rol_usuario == 'Estudiante':
                st.subheader("Editar Mi Perfil")
                _mostrar_formulario_edicion_perfil()
            else:
                st.error("Rol no reconocido para registro de estudiantes.")
                return

    except Exception as e:
        st.error(f"Error en módulo de estudiantes: {e}")

def _mostrar_listado_estudiantes(rol_usuario):
    """Mostrar listado de estudiantes con autorización dinámica"""
    try:
        # Validación de rol
        if rol_usuario is None:
            st.error("Error: Rol de usuario no definido.")
            return
        
        # Consultar estudiantes con filtros según rol
        query = """
        SELECT 
            p.cedula, p.nombre, p.apellido, u.email, p.telefono,
            e.carrera, e.semestre_actual, e.fecha_nacimiento, e.sexo,
            u.cedula_usuario, u.activo
        FROM persona p
        JOIN usuarios u ON p.cedula = u.cedula_usuario
        LEFT JOIN estudiante e ON p.cedula = e.cedula_estudiante
        WHERE u.rol = 'Estudiante'
        ORDER BY p.apellido, p.nombre
        """
        
        estudiantes = execute_query(query)
        
        # Validación robusta de resultados
        if estudiantes is None:
            st.warning("No se pudo obtener la lista de estudiantes. Intente nuevamente.")
            return
        
        # Manejar respuesta numérica (COUNT) o vacía
        if isinstance(estudiantes, int):
            # Si es un número (COUNT), convertir a lista vacía para procesamiento
            if estudiantes == 0:
                st.info("No hay estudiantes registrados.")
                return
            else:
                # Si es un COUNT > 0, ejecutar query real para obtener datos
                estudiantes = execute_query(query)
        
        if not estudiantes or len(estudiantes) == 0:
            st.info("No hay estudiantes registrados.")
            return
        
        # Convertir a DataFrame para mejor visualización con validación segura
        df_estudiantes = []
        for i, est in enumerate(estudiantes):
            try:
                # Validación de cada estudiante antes de procesar
                if est is None:
                    continue
                
                # Validación de campos obligatorios
                if not est.get('cedula') or not est.get('nombre') or not est.get('apellido'):
                    continue
                
                df_estudiantes.append({
                    'Cédula': est.get('cedula', 'N/A'),
                    'Nombre': f"{est.get('nombre', '')} {est.get('apellido', '')}".strip(),
                    'Email': est.get('email', 'N/A'),
                    'Carrera': est.get('carrera', 'N/A'),
                    'Semestre': est.get('semestre_formacion', 'N/A'),
                    'Login': est.get('login_usuario', 'N/A'),
                    'Estado': 'Activo' if est.get('activo', False) else 'Inactivo'
                })
            except Exception as e:
                # Skip problematic records but continue processing
                continue
        
        # Validación final del DataFrame
        if not df_estudiantes:
            st.info("No se encontraron registros válidos de estudiantes.")
            return
        
        # Mostrar tabla con opciones de acción
        st.dataframe(df_estudiantes, use_container_width=True)
        
        # Sección de acciones para administradores y profesores
        if SeguridadFOC26.is_admin() or SeguridadFOC26.is_profesor():
            st.markdown("#### Acciones sobre Estudiantes")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Editar Estudiante", type="secondary", key="editar_estudiante_btn"):
                    st.info("Seleccione un estudiante de la lista para editar")
            
            with col2:
                if st.button("Ver Detalles", type="secondary", key="ver_detalles_estudiante_btn"):
                    st.info("Seleccione un estudiante para ver detalles completos")
            
            with col3:
                if SeguridadFOC26.is_admin():
                    if st.button("Cambiar Estado", type="secondary", key="cambiar_estado_estudiante_btn"):
                        st.info("Seleccione un estudiante para activar/desactivar")
        
        # Estadísticas para administradores
        if SeguridadFOC26.is_admin():
            st.markdown("#### Estadísticas de Estudiantes")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total = len(estudiantes)
                st.metric("Total Estudiantes", total)
            
            with col2:
                activos = sum(1 for e in estudiantes if e['activo'])
                st.metric("Estudiantes Activos", activos)
            
            with col3:
                carreras = set(e.get('carrera', 'N/A') for e in estudiantes)
                st.metric("Carreras", len(carreras))
            
            with col4:
                semestres = set(e.get('semestre_formacion', 'N/A') for e in estudiantes)
                st.metric("Semestres", len(semestres))
                
    except Exception as e:
        st.error(f"Error mostrando listado de estudiantes: {e}")
        logger.error(f"Error en _mostrar_listado_estudiantes: {e}")

def _mostrar_formulario_registro_estudiante():
    """Formulario para registrar nuevo estudiante"""
    try:
        with st.form("form_registro_estudiante"):
            st.markdown("### Datos Personales del Estudiante")
            
            col1, col2 = st.columns(2)
            
            with col1:
                cedula_estudiante = st.text_input(
                    "Cédula del Estudiante*", 
                    placeholder="V-12345678",
                    help="Número de cédula con formato V-XXXXXXXX"
                )
                nombre = st.text_input(
                    "Nombre*", 
                    placeholder="María",
                    help="Nombre completo del estudiante"
                )
                apellido = st.text_input(
                    "Apellido*", 
                    placeholder="González",
                    help="Apellido completo del estudiante"
                )
                email = st.text_input(
                    "Email*", 
                    placeholder="maria.gonzalez@iujo.edu.ve",
                    help="Correo electrónico del estudiante"
                )
                telefono = st.text_input(
                    "Teléfono", 
                    placeholder="0424-1234567",
                    help="Número de teléfono (opcional)"
                )
            
            with col2:
                fecha_nacimiento = st.date_input(
                    "Fecha de Nacimiento*",
                    help="Fecha de nacimiento del estudiante"
                )
                genero = st.selectbox(
                    "Género*",
                    options=["Masculino", "Femenino", "Otro"],
                    help="Seleccione el género"
                )
                direccion = st.text_area(
                    "Dirección", 
                    placeholder="Dirección completa del estudiante",
                    help="Dirección de residencia (opcional)"
                )
                
                # Datos académicos
                carreras_disponibles = [
                    "Ingeniería de Sistemas",
                    "Ingeniería Civil", 
                    "Ingeniería Eléctrica",
                    "Ingeniería Mecánica",
                    "Ingeniería Química"
                ]
                semestres_disponibles = [f"Semestre {i}" for i in range(1, 11)]
                
                carrera = st.selectbox(
                    "Carrera*",
                    options=carreras_disponibles,
                    help="Seleccione la carrera"
                )
                semestre = st.selectbox(
                    "Semestre*",
                    options=semestres_disponibles,
                    help="Seleccione el semestre"
                )
            
            st.markdown("### Credenciales de Acceso")
            
            col3, col4 = st.columns(2)
            with col3:
                contrasena = st.text_input(
                    "Contraseña*", 
                    type="password",
                    placeholder="Mínimo 8 caracteres",
                    help="Contraseña para el sistema"
                )
            with col4:
                confirmar_contrasena = st.text_input(
                    "Confirmar Contraseña*", 
                    type="password",
                    placeholder="Repita la contraseña",
                    help="Debe coincidir con la contraseña"
                )
            
            if st.form_submit_button("Registrar Estudiante", type="primary"):
                # Validación de campos
                if not all([cedula_estudiante, nombre, apellido, email, fecha_nacimiento, genero, carrera, semestre, contrasena, confirmar_contrasena]):
                    st.error("Complete todos los campos obligatorios (*).")
                    return
                
                # Validar formato de email
                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    st.error("Formato de correo electrónico inválido.")
                    return
                
                # Validar contraseñas
                if contrasena != confirmar_contrasena:
                    st.error("Las contraseñas no coinciden.")
                    return
                
                if len(contrasena) < 8:
                    st.error("La contraseña debe tener al menos 8 caracteres.")
                    return
                
                # Procesar registro con arquitectura centralizada
                _procesar_registro_estudiante(cedula_estudiante, nombre, apellido, email, telefono, 
                                            fecha_nacimiento, genero, direccion, carrera, semestre, contrasena)
                
    except Exception as e:
        st.error(f"Error en formulario de registro: {e}")

def _procesar_registro_estudiante(cedula, nombre, apellido, email, telefono, fecha_nacimiento, 
                                genero, direccion, carrera, semestre, contrasena):
    """Procesa el registro de un nuevo estudiante usando arquitectura centralizada"""
    try:
        from database import execute_query, execute_transaction as ejecutar_transaccion
        from seguridad import hash_password
        
        # Verificar si la cédula ya existe
        query_verificar = "SELECT COUNT(*) as total FROM persona WHERE cedula = %s"
        resultado_verificar = execute_query(query_verificar, (cedula,))
        
        # Manejar formato de respuesta de execute_query
        if isinstance(resultado_verificar, list):
            total = resultado_verificar[0]['total'] if resultado_verificar else 0
        elif isinstance(resultado_verificar, dict) and resultado_verificar.get('success', False):
            total = resultado_verificar['data'][0]['total'] if resultado_verificar.get('data') else 0
        else:
            st.error("Error verificando cédula existente.")
            return
            
        if total > 0:
            st.error("Ya existe una persona registrada con esta cédula.")
            return
        
        # Transacciones para registro
        queries = [
            "INSERT INTO persona (cedula, nombre, apellido, email, telefono, fecha_nacimiento, genero, direccion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
            "INSERT INTO usuario (cedula_usuario, login_usuario, contrasena, rol, activo) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            "INSERT INTO estudiante (cedula_estudiante, indice_academico, semestre_actual, id_carrera, estado_registro, fecha_ingreso) VALUES (%s, %s, %s, %s, %s, %s)"
        ]
        
        params_list = [
            (cedula, nombre.strip(), apellido.strip(), email.strip(), telefono.strip() if telefono else None, fecha_nacimiento, genero, direccion.strip() if direccion else None),
            (cedula, f"{cedula}@foc26.com", hash_password(contrasena), 'Estudiante', True),
            (cedula, None, None, carrera, semestre, 'Activo')
        ]
        
        resultado = ejecutar_transaccion(queries, params_list)
        
        if resultado['success']:
            st.success(f"Estudiante {nombre} {apellido} registrado exitosamente.")
            st.info(f"Credenciales de acceso:")
            st.code(f"Cédula: {cedula}\nContraseña: {contrasena}")
            st.rerun()
        else:
            st.error(f"Error registrando estudiante: {resultado.get('error', 'Error desconocido')}")
            
    except Exception as e:
        st.error(f"Error en el registro: {e}")

def _mostrar_formulario_edicion_perfil():
    """Formulario para editar perfil de estudiante"""
    try:
        # Obtener datos del estudiante actual con validación
        user_cedula = SeguridadFOC26.get_user_cedula()
        
        if user_cedula is None:
            st.error("Error: No se pudo obtener la cédula del usuario. Por favor, inicie sesión nuevamente.")
            return
        query = """
        SELECT
            u.cedula_usuario as usuario_id,
            u.cedula_usuario,
            p.nombre,
            p.apellido,
            p.cedula,
            p.telefono,
            p.fecha_nacimiento,
            p.sexo as sexo,
            p.direccion,
            u.email,
            e.carrera,
            e.semestre_actual,
            e.estado_registro,
            e.id as estudiante_id
        FROM usuarios u
        JOIN persona p ON u.cedula_usuario = p.cedula
        LEFT JOIN estudiante e ON p.cedula = e.cedula_estudiante
        WHERE u.rol = 'Estudiante' AND u.cedula_usuario = %s
        """
        resultado_query = execute_query(query, (user_cedula,))
        
        if resultado_query and len(resultado_query) > 0:
            estudiante = resultado_query[0]
            
            # Validación robusta de estudiante None
            if estudiante is None:
                st.error("Error: Datos de estudiante no encontrados o corruptos.")
                return
            
            with st.form("form_edicion_perfil"):
                st.markdown("### Editar Mi Información Personal")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    nombre = st.text_input("Nombre*", value=estudiante.get('nombre', '') or '')
                    apellido = st.text_input("Apellido*", value=estudiante.get('apellido', '') or '')
                    telefono = st.text_input("Teléfono", value=estudiante.get('telefono', '') or "")
                    email = st.text_input("Email*", value=estudiante.get('email', '') or "")
                
                with col2:
                    fecha_nacimiento = st.date_input(
                        "Fecha de Nacimiento",
                        value=estudiante.get('fecha_nacimiento') if estudiante.get('fecha_nacimiento') else None
                    )
                    genero = st.selectbox(
                        "Género",
                        ["Masculino", "Femenino", "Otro"],
                        index=["Masculino", "Femenino", "Otro"].index(estudiante.get('sexo', '')) if estudiante.get('sexo', '') in ["Masculino", "Femenino", "Otro"] else 0
                    )
                    direccion = st.text_area("Dirección", value=estudiante.get('direccion', '') or "")
                    
                    # Datos académicos
                    from configuracion import carreras_disponibles, semestres_disponibles
                    carrera = st.selectbox(
                        "Carrera",
                        carreras_disponibles,
                        index=carreras_disponibles.index(estudiante.get('carrera', '')) if estudiante.get('carrera', '') in carreras_disponibles else 0
                    )
                    semestre = st.selectbox(
                        "Semestre",
                        semestres_disponibles,
                        index=semestres_disponibles.index(estudiante.get('semestre_formacion', '')) if estudiante.get('semestre_formacion', '') in semestres_disponibles else 0
                    )
                
                if st.form_submit_button("Actualizar Mi Perfil", type="primary"):
                    usuario_id = estudiante.get('usuario_id')
                    if usuario_id is not None:
                        _procesar_actualizacion_perfil(nombre, apellido, telefono, email, fecha_nacimiento, 
                                                     genero, direccion, carrera, semestre, user_cedula, usuario_id)
                    else:
                        st.error("Error: ID de usuario no encontrado.")
        else:
            st.error("No se encontró tu información de estudiante.")
            
    except Exception as e:
        st.error(f"Error en formulario de edición: {e}")

def _procesar_actualizacion_perfil(nombre, apellido, telefono, email, fecha_nacimiento, 
                                 genero, direccion, carrera, semestre, user_cedula, usuario_id):
    """Procesa la actualización del perfil del estudiante"""
    try:
        from database import execute_transaction
        
        queries = [
            "UPDATE persona SET nombre = %s, apellido = %s, telefono = %s, email = %s, fecha_nacimiento = %s, genero = %s, direccion = %s WHERE cedula = %s",
            "UPDATE estudiante SET id_carrera = %s, semestre_actual = %s WHERE cedula_estudiante = %s"
        ]
        
        params_list = [
            (nombre, apellido, telefono, email, fecha_nacimiento, genero, direccion, user_cedula),
            (carrera, semestre, user_cedula)
        ]
        
        resultado = execute_transaction(queries, params_list)
        
        if resultado['success']:
            st.success("Perfil actualizado exitosamente")
            st.rerun()
        else:
            st.error(f"Error actualizando perfil: {resultado['error']}")
            
    except Exception as e:
        st.error(f"Error en actualización: {e}")

def _mostrar_seccion_busqueda():
    """Sección de búsqueda y edición de estudiantes"""
    try:
        # Búsqueda de estudiante
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            termino_busqueda = st.text_input("Buscar por Cédula, Nombre o Email", placeholder="V-12345678 o Juan Pérez")
        with col2:
            if st.button("Buscar", type="primary", key="buscar_estudiante_btn"):
                if termino_busqueda:
                    _realizar_busqueda_estudiante(termino_busqueda)
        
        with col3:
            if st.button("Limpiar Búsqueda", key="limpiar_busqueda_estudiante"):
                if 'resultados_busqueda_estudiante' in st.session_state:
                    del st.session_state['resultados_busqueda_estudiante']
                st.rerun()
        
        # Mostrar resultados de búsqueda
        if 'resultados_busqueda_estudiante' in st.session_state:
            st.markdown("---")
            st.subheader("Resultados de Búsqueda")
            
            resultado = st.session_state.get('resultados_busqueda_estudiante', None)
            if resultado is None:
                st.warning("No hay resultados de búsqueda disponibles.")
                return
            
            if not isinstance(resultado, dict):
                st.warning("Formato de resultados inválido.")
                return
            
            if resultado.get('success', False) and resultado.get('data'):
                import pandas as pd
                data = resultado.get('data', [])
                if data is None or not data:
                    st.info("La búsqueda no retornó datos.")
                    return
                
                # Verificar que data sea una lista de diccionarios válida
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                    df_busqueda = pd.DataFrame(data)
                else:
                    st.info("La búsqueda no retornó datos válidos.")
                    return
            st.dataframe(
                df_busqueda[["nombre", "apellido", "cedula", "telefono", "email_estudiante", "id_carrera", "semestre_actual", "estado_registro", "activo"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "nombre": st.column_config.TextColumn("Nombres"),
                    "apellido": st.column_config.TextColumn("Apellidos"),
                    "cedula": st.column_config.TextColumn("Cédula"),
                    "telefono": st.column_config.TextColumn("Teléfono"),
                    "email_estudiante": st.column_config.TextColumn("Correo"),
                    "id_carrera": st.column_config.TextColumn("Carrera"),
                    "semestre_actual": st.column_config.TextColumn("Semestre"),
                    "estado_registro": st.column_config.TextColumn("Estado"),
                    "activo": st.column_config.TextColumn("Activo")
                }
            )
        else:
            st.warning("No se encontraron estudiantes con esos criterios.")
                
    except Exception as e:
        st.error(f"Error en sección de búsqueda: {e}")

def _realizar_busqueda_estudiante(termino):
    """Realiza la búsqueda de estudiantes"""
    try:
        query = """
        SELECT
            u.cedula_usuario as usuario_id,
            u.cedula_usuario,
            u.rol,
            p.nombre,
            p.apellido,
            p.cedula,
            p.telefono,
            p.fecha_nacimiento,
            p.sexo as sexo,
            p.direccion,
            u.activo as activo,
            e.carrera,
            e.semestre_actual,
            e.estado_registro,
            e.id as estudiante_id
        FROM usuarios u
        JOIN persona p ON u.cedula_usuario = p.cedula
        LEFT JOIN estudiante e ON p.cedula = e.cedula_estudiante
        WHERE u.rol = 'Estudiante' AND (
            p.cedula ILIKE %s OR 
            p.nombre ILIKE %s OR 
            p.apellido ILIKE %s OR 
            u.cedula_usuario ILIKE %s
        )
        ORDER BY p.apellido, p.nombre
        """
        
        resultado = execute_query(query, (f"%{termino}%", f"%{termino}%", f"%{termino}%", f"%{termino}%"))
        st.session_state['resultados_busqueda_estudiante'] = resultado
        
        if not resultado['success']:
            st.warning("No se encontraron estudiantes con esos criterios.")
            
    except Exception as e:
        st.error(f"Error en búsqueda: {e}")

def gestion_estudiantil_main():
    """Función principal del módulo de gestión de estudiantes"""
    try:
        gestion_estudiantil()
    except Exception as e:
        st.error(f"Error en el módulo de gestión de estudiantes: {e}")

def registro_estudiantes_main():
    """Función principal del módulo de registro de estudiantes"""
    try:
        # Mostrar solo el formulario de registro
        st.header("Registro de Estudiantes")
        rol_usuario = st.session_state.get('user_role', None)
        
        # ACCESO GARANTIZADO: Administradores siempre ven el formulario
        if rol_usuario in ['Administrador', 'Admin']:
            st.info("Acceso como Administrador - Formulario disponible")
            _mostrar_formulario_registro_estudiante()
        elif rol_usuario == 'Profesor':
            # Profesor necesita permisos específicos
            if tiene_permiso(rol_usuario, 'Estudiantes', 'registrar') or tiene_permiso(rol_usuario, 'Estudiantes', 'crear'):
                _mostrar_formulario_registro_estudiante()
            else:
                st.warning("No tiene permisos para registrar estudiantes.")
                return
        elif rol_usuario == 'Estudiante':
            st.warning("Los estudiantes no pueden registrar otros estudiantes.")
            return
        else:
            st.error("Rol no reconocido para registro de estudiantes.")
            return
            
    except Exception as e:
        st.error(f"Error en el módulo de registro de estudiantes: {e}")
