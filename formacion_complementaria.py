import streamlit as st
import pandas as pd
import sys
import os
from datetime import date, datetime
from PIL import Image, ImageDraw, ImageFont
import io

# Importar estilos globales de formularios (MANDATORIO)
from styles import aplicar_estilo_consistente_global

# IMPORTACIONES LOCALES AL MÓDULO - MOTOR CENTRAL UNIFICADO
try:
    from seguridad import tiene_permiso, SeguridadFOC26
    from database import motor_central
except ImportError as e:
    st.error(f"Error importando módulos locales: {e}")
    sys.exit(1)

class MotorFormacionComplementaria:
    """Motor central de Formación Complementaria que consume MotorTransaccionalCentral"""
    
    def __init__(self):
        """Inicialización del motor central"""
        self.motor = motor_central
    
    # Operaciones de Formación Complementaria (existentes)
    def crear_formacion(self, datos):
        """Crear nueva formación complementaria"""
        return self.motor.operacion_crud_unificada('formacion_complementaria', 'CREATE', datos)
    
    def leer_formaciones(self, filtros=None, orden='fecha_creacion DESC'):
        """Leer formaciones complementarias"""
        return self.motor.operacion_crud_unificada('formacion_complementaria', 'READ', filtros=filtros, orden=orden)
    
    def actualizar_formacion(self, datos, filtros):
        """Actualizar formación complementaria"""
        return self.motor.operacion_crud_unificada('formacion_complementaria', 'UPDATE', datos, filtros)
    
    def eliminar_formacion(self, filtros):
        """Eliminar formación complementaria"""
        return self.motor.operacion_crud_unificada('formacion_complementaria', 'DELETE', filtros=filtros)
    
    # Operaciones de Estudiantes (centralizadas)
    def crear_estudiante(self, datos):
        """Crear nuevo estudiante"""
        return self.motor.operacion_crud_unificada('estudiante', 'CREATE', datos)
    
    def leer_estudiantes(self, filtros=None, orden='apellido, nombre'):
        """Leer estudiantes con información de persona"""
        # Consulta personalizada para estudiantes con datos de persona
        query = """
        SELECT 
            p.nombre, p.apellido, p.cedula, p.telefono, u.email as email_estudiante,
            e.id_carrera, e.semestre_actual, e.estado_registro, u.activo
        FROM usuarios u
        LEFT JOIN persona p ON u.cedula_usuario = p.cedula
        LEFT JOIN estudiante e ON p.cedula = e.cedula_estudiante
        WHERE u.rol = 'Estudiante'
        """
        
        if filtros:
            condiciones = []
            valores = []
            for campo, valor in filtros.items():
                if campo in ['u.cedula_usuario', 'p.nombre', 'p.apellido', 'p.cedula']:
                    condiciones.append(f"{campo} = %s")
                    valores.append(valor)
            
            if condiciones:
                query += f" AND {' AND '.join(condiciones)}"
                return self.motor.ejecutar_consulta_personalizada(query, tuple(valores))
        
        return self.motor.ejecutar_consulta_personalizada(query)
    
    def actualizar_estudiante(self, datos, filtros):
        """Actualizar estudiante"""
        return self.motor.operacion_crud_unificada('estudiante', 'UPDATE', datos, filtros)
    
    def eliminar_estudiante(self, filtros):
        """Eliminar estudiante"""
        return self.motor.operacion_crud_unificada('estudiante', 'DELETE', filtros)
    
    # Operaciones de Profesores (centralizadas)
    def crear_profesor(self, datos):
        """Crear nuevo profesor"""
        return self.motor.operacion_crud_unificada('profesor', 'CREATE', datos)
    
    def leer_profesores(self, filtros=None, orden='apellido, nombre'):
        """Leer profesores con información de persona"""
        # Consulta personalizada para profesores con datos de persona
        query = """
        SELECT 
            u.cedula_usuario, u.rol, u.activo, u.email as email_profesor,
            p.nombre, p.apellido, p.cedula, p.telefono, p.fecha_nacimiento, p.sexo, p.direccion,
            pr.especialidad, pr.fecha_contratacion, pr.activo as estado_profesor, pr.categoria
        FROM usuarios u
        LEFT JOIN persona p ON u.cedula_usuario = p.cedula
        LEFT JOIN profesor pr ON p.cedula = pr.cedula_profesor
        WHERE u.rol = 'Profesor'
        """
        
        if filtros:
            condiciones = []
            valores = []
            for campo, valor in filtros.items():
                if campo in ['u.cedula_usuario', 'p.nombre', 'p.apellido', 'p.cedula']:
                    condiciones.append(f"{campo} = %s")
                    valores.append(valor)
            
            if condiciones:
                query += f" AND {' AND '.join(condiciones)}"
                return self.motor.ejecutar_consulta_personalizada(query, tuple(valores))
        
        return self.motor.ejecutar_consulta_personalizada(query)
    
    def actualizar_profesor(self, datos, filtros):
        """Actualizar profesor"""
        return self.motor.operacion_crud_unificada('profesor', 'UPDATE', datos, filtros)
    
    def eliminar_profesor(self, filtros):
        """Eliminar profesor"""
        return self.motor.operacion_crud_unificada('profesor', 'DELETE', filtros)
    
    # Operaciones de Usuarios (centralizadas)
    def leer_usuarios(self, filtros=None, orden='cedula_usuario'):
        """Leer usuarios del sistema"""
        return self.motor.operacion_crud_unificada('usuarios', 'READ', filtros=filtros, orden=orden)
    
    # Operaciones de Reportes (centralizadas)
    def obtener_estadisticas_generales(self):
        """Obtener estadísticas generales del sistema"""
        queries = {
            'total_usuarios': "SELECT COUNT(*) as total FROM usuarios",
            'total_estudiantes': "SELECT COUNT(*) as total FROM estudiante",
            'total_profesores': "SELECT COUNT(*) as total FROM profesor",
            'total_formaciones': "SELECT COUNT(*) as total FROM formacion_complementaria"
        }
        
        resultados = {}
        for key, query in queries.items():
            resultado = self.motor.ejecutar_consulta_personalizada(query, fetch_one=True)
            if resultado['success']:
                resultados[key] = resultado['data']['total'] if resultado['data'] else 0
            else:
                resultados[key] = 0
        
        return resultados
    
    def obtener_usuarios_por_rol(self):
        """Obtener usuarios agrupados por rol"""
        query = """
        SELECT rol, COUNT(*) as cantidad 
        FROM usuarios 
        GROUP BY rol 
        ORDER BY cantidad DESC
        """
        return self.motor.ejecutar_consulta_personalizada(query)
    
    def validar_permiso(self, rol_usuario, modulo, accion):
        """Validar permisos de forma centralizada"""
        return self.motor.validar_permiso_usuario(rol_usuario, modulo, accion)

# Instancia global del motor de formación complementaria
motor_formacion = MotorFormacionComplementaria()

def modulo_formacion_complementaria(db=None):
    """Módulo principal de Formación Complementaria"""
    try:
        rol_usuario = st.session_state.user_role
        
        if not tiene_permiso(rol_usuario, 'Formación Complementaria', 'Consultar'):
            st.error("Acceso denegado. No tienes permisos para consultar formación complementaria.")
            return
        
        # Determinar tabs según permisos específicos en lugar de rol fijo
        tabs_disponibles = []
        
        # Tabs para todos los usuarios con permiso de consulta
        if tiene_permiso(rol_usuario, 'Formación Complementaria', 'Consultar'):
            tabs_disponibles.extend([
                ("Talleres Disponibles", talleres_disponibles),
                ("Mis Inscripciones", mis_inscripciones)
            ])
        
        # Tabs para usuarios con permisos de gestión
        if tiene_permiso(rol_usuario, 'Formación Complementaria', 'Crear'):
            tabs_disponibles.insert(0, ("Gestión de Talleres", gestion_talleres))
        
        if tiene_permiso(rol_usuario, 'Formación Complementaria', 'Actualizar'):
            # Añadir tab de inscripciones si tiene permiso de actualizar
            if not any(tab[0] == "Inscripciones" for tab in tabs_disponibles):
                tabs_disponibles.append(("Inscripciones", inscripciones_formacion))
        
        if tiene_permiso(rol_usuario, 'Formación Complementaria', 'Eliminar'):
            # Añadir tab de editor de certificados y reportes
            if not any(tab[0] == "Editor de Certificados" for tab in tabs_disponibles):
                tabs_disponibles.extend([
                    ("Editor de Certificados", editor_certificados),
                    ("Reportes", reportes_formacion)
                ])
        
        # Crear tabs dinámicamente según permisos
        if tabs_disponibles:
            tab_names = [tab[0] for tab in tabs_disponibles]
            tabs = st.tabs(tab_names)
            
            for i, (tab_name, tab_function) in enumerate(tabs_disponibles):
                with tabs[i]:
                    tab_function(db, rol_usuario)
        else:
            st.info("No tienes permisos configurados para este módulo. Contacta al administrador.")
                
    except Exception as e:
        st.error(f"Error en módulo de formación complementaria: {e}")

def gestion_talleres(db, rol_usuario):
    """Gestión de talleres con CRUD transaccional completo"""
    
    st.subheader("Gestión de Talleres")
    
    # Validar permisos para crear talleres
    if not tiene_permiso(rol_usuario, 'Formación Complementaria', 'Crear'):
        st.warning("No tienes permisos para crear talleres.")
        return
    
    # Tabs para CRUD: Crear, Listar, Editar
    tab_crear, tab_listar = st.tabs(["Crear Taller", "Listar Talleres"])
    
    with tab_crear:
        crear_taller_transaccional(rol_usuario)
    
    with tab_listar:
        listar_y_editar_talleres(rol_usuario)

def crear_taller_transaccional(rol_usuario):
    """Crear taller usando motor central unificado"""
    st.markdown("### Nuevo Taller")
    
    with st.form("form_crear_taller"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_taller = st.text_input("Nombre del Taller*", placeholder="Introducción a Python")
            descripcion = st.text_area("Descripción*", placeholder="Taller básico de programación en Python")
            fecha_inicio = st.date_input("Fecha de Inicio*", value=date.today())
            fecha_fin = st.date_input("Fecha de Fin*", value=date.today())
            
        with col2:
            cupo_maximo = st.number_input("Cupo Máximo*", min_value=1, value=30)
            estado = st.selectbox("Estado", ["Activo", "Inactivo", "Próximo"])
            
        st.markdown("### Datos del Certificado")
        col3, col4 = st.columns(2)
        
        with col3:
            tomo = st.text_input("Tomo*", placeholder="001", help="Número de tomo del certificado")
            folio = st.text_input("Folio*", placeholder="12345", help="Número de folio del certificado")
            
        with col4:
            facilitador = st.text_input("Facilitador", placeholder="Nombre del facilitador")
            
            # Generar código automático
            if tomo and folio:
                año_actual = date.today().year
                codigo_certificado = f"IU-FOC-{año_actual}-{tomo}-{folio}"
            else:
                codigo_certificado = ""
            
            st.text_input("Código del Certificado", 
                         value=codigo_certificado,
                         disabled=True)
            
        submit_taller = st.form_submit_button("Crear Taller")
        
        if submit_taller:
            # VALIDACIÓN DE CAMPOS OBLIGATORIOS
            campos_obligatorios = [nombre_taller, descripcion, tomo, folio]
            if all(campos_obligatorios):
                try:
                    # VALIDACIÓN DE FECHAS
                    if fecha_fin < fecha_inicio:
                        st.error("La fecha de fin no puede ser anterior a la fecha de inicio")
                        return
                    
                    # VALIDACIÓN DE CUPO
                    if cupo_maximo < 1:
                        st.error("El cupo máximo debe ser al menos 1")
                        return
                    
                    # OBTENER CÉDULA DEL USUARIO ACTUAL
                    user_data = st.session_state.get('user', {})
                    cedula_usuario = user_data.get('cedula_usuario', '')
                    
                    if not cedula_usuario:
                        st.error("No se pudo identificar al usuario actual")
                        return
                    
                    # USAR MOTOR CENTRAL UNIFICADO
                    datos_formacion = {
                        'nombre_taller': nombre_taller,
                        'descripcion': descripcion,
                        'fecha_inicio': fecha_inicio,
                        'fecha_fin': fecha_fin,
                        'cupo_maximo': cupo_maximo,
                        'cupo_actual': 0,
                        'estado': estado,
                        'cedula_usuario_creador': cedula_usuario,
                        'codigo_certificado': codigo_certificado,
                        'tomo': tomo,
                        'folio': folio,
                        'facilitador': facilitador,
                        'fecha_creacion': datetime.now()
                    }
                    
                    resultado = motor_formacion.crear_formacion(datos_formacion)
                    
                    if resultado['success']:
                        st.success(resultado['message'])
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(resultado['message'])
                        
                except Exception as e:
                    # VERIFICACIÓN DE SEGURIDAD - Manejo de errores específicos
                    error_msg = str(e).lower()
                    if 'duplicate key' in error_msg or 'unique' in error_msg:
                        st.error("Error: Ya existe un taller con ese código de certificado")
                    elif 'foreign key' in error_msg:
                        st.error("Error: El usuario no está registrado en el sistema")
                    elif 'null' in error_msg:
                        st.error("Error: Campos obligatorios vacíos")
                    else:
                        st.error(f"Error al crear taller: {e}")
            else:
                st.error("Por favor, complete todos los campos obligatorios (*)")

def listar_y_editar_talleres(rol_usuario):
    """Listar talleres con opciones de edición y eliminación - MOTOR CENTRAL"""
    st.markdown("### Talleres Registrados")
    
    try:
        # USAR MOTOR CENTRAL UNIFICADO
        resultado = motor_formacion.leer_formaciones(orden='fecha_creacion DESC')
        
        if not resultado['success']:
            st.error(f"Error al obtener talleres: {resultado['message']}")
            return
        
        talleres = resultado['data']
        
        if not talleres:
            st.info("No hay talleres registrados")
            return
        
        # CONVERTIR A DATAFRAME PARA VISUALIZACIÓN CON VALIDACIÓN
        if talleres and isinstance(talleres, list) and len(talleres) > 0 and isinstance(talleres[0], dict):
            df = pd.DataFrame(talleres)
        else:
            st.info("No hay datos de talleres válidos para mostrar")
            return
        
        # FORMATEAR COLUMNAS PARA MEJOR VISUALIZACIÓN
        df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio']).dt.strftime('%Y-%m-%d')
        df['fecha_fin'] = pd.to_datetime(df['fecha_fin']).dt.strftime('%Y-%m-%d')
        df['cupo_info'] = df['cupo_actual'].astype(str) + '/' + df['cupo_maximo'].astype(str)
        
        # MOSTRAR TABLA
        st.dataframe(
            df[['id_formacion', 'nombre_taller', 'descripcion', 'fecha_inicio', 'fecha_fin', 
                'cupo_info', 'estado', 'codigo_certificado']],
            column_config={
                'id_formacion': 'ID',
                'nombre_taller': 'Nombre del Taller',
                'descripcion': 'Descripción',
                'fecha_inicio': 'Fecha Inicio',
                'fecha_fin': 'Fecha Fin',
                'cupo_info': 'Cupo (Actual/Max)',
                'estado': 'Estado',
                'codigo_certificado': 'Código Certificado'
            },
            use_container_width=True
        )
        
        # SELECCIÓN PARA EDICIÓN/ELIMINACIÓN
        st.markdown("### Acciones sobre Talleres")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Selección de taller para editar
            opciones_taller = {f"{t['nombre_taller']} (ID: {t['id_formacion']})": t['id_formacion'] 
                             for t in talleres}
            taller_seleccionado = st.selectbox("Seleccionar Taller para Editar:", list(opciones_taller.keys()))
            id_taller_editar = opciones_taller[taller_seleccionado]
            
            if st.button("Editar Taller Seleccionado", type="secondary"):
                editar_taller(id_taller_editar, rol_usuario)
        
        with col2:
            # Selección de taller para eliminar
            taller_eliminar = st.selectbox("Seleccionar Taller para Eliminar:", list(opciones_taller.keys()))
            id_taller_eliminar = opciones_taller[taller_eliminar]
            
            if st.button("Eliminar Taller Seleccionado", type="primary"):
                eliminar_taller(id_taller_eliminar, rol_usuario)
                
    except Exception as e:
        st.error(f"Error al listar talleres: {e}")

def editar_taller(id_taller, rol_usuario):
    """Editar taller existente usando motor central unificado"""
    # Validar permisos para editar
    if not tiene_permiso(rol_usuario, 'Formación Complementaria', 'Actualizar'):
        st.error("No tienes permisos para editar talleres.")
        return
    
    try:
        # USAR MOTOR CENTRAL UNIFICADO
        resultado = motor_formacion.leer_formaciones(filtros={'id_formacion': id_taller})
        
        if not resultado['success']:
            st.error(f"Error al obtener taller: {resultado['message']}")
            return
        
        talleres = resultado['data']
        
        if not talleres:
            st.error("Taller no encontrado")
            return
        
        taller_actual = talleres[0]
        
        st.markdown(f"### Editar Taller: {taller_actual['nombre_taller']}")
        
        with st.form("form_editar_taller"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre_taller = st.text_input("Nombre del Taller*", value=taller_actual['nombre_taller'])
                descripcion = st.text_area("Descripción*", value=taller_actual['descripcion'])
                fecha_inicio = st.date_input("Fecha de Inicio*", value=pd.to_datetime(taller_actual['fecha_inicio']).date())
                fecha_fin = st.date_input("Fecha de Fin*", value=pd.to_datetime(taller_actual['fecha_fin']).date())
                
            with col2:
                cupo_maximo = st.number_input("Cupo Máximo*", min_value=1, value=int(taller_actual['cupo_maximo']))
                estado = st.selectbox("Estado", ["Activo", "Inactivo", "Próximo"], 
                                     index=["Activo", "Inactivo", "Próximo"].index(taller_actual['estado']))
                
            st.markdown("### Datos del Certificado")
            col3, col4 = st.columns(2)
            
            with col3:
                tomo = st.text_input("Tomo*", value=taller_actual['tomo'])
                folio = st.text_input("Folio*", value=taller_actual['folio'])
                
            with col4:
                facilitador = st.text_input("Facilitador", value=taller_actual.get('facilitador', ''))
                
                # Actualizar código automáticamente
                if tomo and folio:
                    año_actual = date.today().year
                    codigo_certificado = f"IU-FOC-{año_actual}-{tomo}-{folio}"
                else:
                    codigo_certificado = ""
                
                st.text_input("Código del Certificado", value=codigo_certificado, disabled=True)
            
            col_guardar, col_cancelar = st.columns(2)
            with col_guardar:
                submit_editar = st.form_submit_button("Guardar Cambios", type="primary")
            with col_cancelar:
                submit_cancelar = st.form_submit_button("Cancelar", type="secondary")
            
            if submit_editar:
                # VALIDACIÓN DE CAMPOS OBLIGATORIOS
                campos_obligatorios = [nombre_taller, descripcion, tomo, folio]
                if all(campos_obligatorios):
                    try:
                        # VALIDACIÓN DE FECHAS
                        if fecha_fin < fecha_inicio:
                            st.error("La fecha de fin no puede ser anterior a la fecha de inicio")
                            return
                        
                        # USAR MOTOR CENTRAL UNIFICADO
                        datos_actualizar = {
                            'nombre_taller': nombre_taller,
                            'descripcion': descripcion,
                            'fecha_inicio': fecha_inicio,
                            'fecha_fin': fecha_fin,
                            'cupo_maximo': cupo_maximo,
                            'estado': estado,
                            'codigo_certificado': codigo_certificado,
                            'tomo': tomo,
                            'folio': folio,
                            'facilitador': facilitador
                        }
                        
                        resultado_actualizar = motor_formacion.actualizar_formacion(
                            datos=datos_actualizar,
                            filtros={'id_formacion': id_taller}
                        )
                        
                        if resultado_actualizar['success']:
                            st.success(resultado_actualizar['message'])
                            st.rerun()
                        else:
                            st.error(resultado_actualizar['message'])
                            
                    except Exception as e:
                        st.error(f"Error al actualizar taller: {e}")
                else:
                    st.error("Por favor, complete todos los campos obligatorios (*)")
                    
    except Exception as e:
        st.error(f"Error al cargar datos del taller: {e}")

def eliminar_taller(id_taller, rol_usuario):
    """Eliminar taller usando motor central unificado"""
    # Validar permisos para eliminar
    if not tiene_permiso(rol_usuario, 'Formación Complementaria', 'Eliminar'):
        st.error("No tienes permisos para eliminar talleres.")
        return
    
    try:
        # OBTENER DATOS DEL TALLER PARA CONFIRMACIÓN
        resultado_taller = motor_formacion.leer_formaciones(filtros={'id_formacion': id_taller})
        
        if not resultado_taller['success']:
            st.error(f"Error al obtener taller: {resultado_taller['message']}")
            return
        
        talleres = resultado_taller['data']
        
        if not talleres:
            st.error("Taller no encontrado")
            return
        
        taller = talleres[0]
        
        # CONFIRMACIÓN DE ELIMINACIÓN
        st.warning(f"¿Está seguro que desea eliminar el taller '{taller['nombre_taller']}'?")
        
        col_confirmar, col_cancelar = st.columns(2)
        with col_confirmar:
            if st.button("Sí, Eliminar", type="primary"):
                try:
                    # USAR MOTOR CENTRAL UNIFICADO
                    resultado_eliminar = motor_formacion.eliminar_formacion(filtros={'id_formacion': id_taller})
                    
                    if resultado_eliminar['success']:
                        st.success(resultado_eliminar['message'])
                        st.rerun()
                    else:
                        st.error(resultado_eliminar['message'])
                        
                except Exception as e:
                    st.error(f"Error al eliminar taller: {e}")
        
        with col_cancelar:
            if st.button("No, Cancelar", type="secondary"):
                st.info("Eliminación cancelada")
                
    except Exception as e:
        st.error(f"Error al verificar taller: {e}")

def talleres_disponibles(db, rol_usuario):
    """Mostrar talleres disponibles para estudiantes - MOTOR CENTRAL"""
    
    st.subheader("Talleres Disponibles")
    
    try:
        # USAR MOTOR CENTRAL UNIFICADO
        resultado = motor_formacion.leer_formaciones(orden='fecha_creacion DESC')
        
        if not resultado['success']:
            st.error(f"Error al obtener talleres: {resultado['message']}")
            return
        
        talleres = resultado['data']
        
        # FILTRAR TALLERES ACTIVOS Y DISPONIBLES (adaptado a estructura real)
        talleres_disponibles = [
            t for t in talleres 
            if t.get('estado', 'Inactivo') == 'activo' and t.get('capacidad_maxima', 0) > 0
        ]
        
        if not talleres_disponibles:
            st.info("No hay talleres disponibles en este momento")
            return
        
        # CONVERTIR A DATAFRAME PARA VISUALIZACIÓN CON VALIDACIÓN
        if talleres_disponibles and isinstance(talleres_disponibles, list) and len(talleres_disponibles) > 0 and isinstance(talleres_disponibles[0], dict):
            df = pd.DataFrame(talleres_disponibles)
        else:
            st.info("No hay talleres disponibles con datos válidos")
            return
        
        # FORMATEAR COLUMNAS (adaptado a estructura real)
        if 'fecha_inicio' in df.columns:
            df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio']).dt.strftime('%Y-%m-%d')
        if 'fecha_fin' in df.columns:
            df['fecha_fin'] = pd.to_datetime(df['fecha_fin']).dt.strftime('%Y-%m-%d')
        
        # Usar capacidad_maxima como cupos disponibles
        df['cupo_disponible'] = df.get('capacidad_maxima', 0)
        
        # SELECCIONAR COLUMNAS DISPONIBLES
        columnas_disponibles = ['nombre_taller', 'descripcion_taller', 'fecha_inicio', 'fecha_fin', 'cupo_disponible']
        columnas_finales = []
        
        for col in columnas_disponibles:
            if col in df.columns:
                columnas_finales.append(col)
        
        # MOSTRAR TABLA CON COLUMNAS RELEVANTES
        st.dataframe(
            df[columnas_finales],
            column_config={
                'nombre_taller': 'Nombre del Taller',
                'descripcion_taller': 'Descripción',
                'fecha_inicio': 'Fecha Inicio',
                'fecha_fin': 'Fecha Fin',
                'cupo_disponible': 'Cupos Disponibles'
            },
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"Error al cargar talleres disponibles: {e}")

def inscripciones_formacion(db, rol_usuario):
    """Gestión de inscripciones"""
    st.subheader("Gestión de Inscripciones")
    st.info("Función de inscripciones en desarrollo")

def mis_inscripciones(db, rol_usuario):
    """Mostrar inscripciones del estudiante actual"""
    st.subheader("Mis Inscripciones")
    
    # Aquí iría la lógica para mostrar las inscripciones del estudiante actual
    st.info("Función en desarrollo...")

def editor_certificados(db, rol_usuario):
    """Editor de Certificados - Solo para Administradores"""
    try:
        # Solo administradores pueden acceder al editor
        if not SeguridadFOC26.is_admin():
            st.warning("El editor de certificados está disponible solo para administradores.")
            return
        
        st.subheader("🎨 Editor de Certificados")
        
        # Tabs para diferentes funcionalidades
        tab1, tab2, tab3 = st.tabs(["⚙️ Configuración", "👁️ Previsualización", "📥 Generación"])
        
        with tab1:
            configuracion_plantillas(db)
        
        with tab2:
            previsualizacion_certificado(db)
        
        with tab3:
            generacion_certificados(db)
            
    except Exception as e:
        st.error(f"Error en editor de certificados: {e}")

def configuracion_plantillas(db):
    """Configuración de plantillas de certificados"""
    try:
        st.markdown("#### Configuración de Plantillas")
        
        # Obtener configuración actual
        config_actual = obtener_configuracion_certificados()
        
        # Subida de imágenes
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Imagen Anverso**")
            anverso_file = st.file_uploader(
                "Subir imagen anverso", 
                type=['jpg', 'jpeg', 'png'],
                key="anverso_upload"
            )
            
            if anverso_file:
                # Guardar imagen
                guardar_imagen_certificado(anverso_file, "anverso")
                st.success("Imagen anverso subida exitosamente")
        
        with col2:
            st.markdown("**Imagen Reverso**")
            reverso_file = st.file_uploader(
                "Subir imagen reverso", 
                type=['jpg', 'jpeg', 'png'],
                key="reverso_upload"
            )
            
            if reverso_file:
                # Guardar imagen
                guardar_imagen_certificado(reverso_file, "reverso")
                st.success("Imagen reverso subida exitosamente")
        
        st.markdown("---")
        st.markdown("#### Posicionamiento de Elementos")
        
        # Configuración de posición y tamaño
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Anverso**")
            
            # Nombre Estudiante
            st.markdown("##### Nombre Estudiante")
            nombre_x = st.slider("Posición X", 0, 1000, config_actual.get('nombre_x', 100), key="nombre_x")
            nombre_y = st.slider("Posición Y", 0, 1000, config_actual.get('nombre_y', 200), key="nombre_y")
            nombre_tamano = st.slider("Tamaño Fuente", 10, 100, config_actual.get('nombre_tamano', 24), key="nombre_tamano")
            
            # Horas
            st.markdown("##### Horas")
            horas_x = st.slider("Posición X", 0, 1000, config_actual.get('horas_x', 100), key="horas_x")
            horas_y = st.slider("Posición Y", 0, 1000, config_actual.get('horas_y', 250), key="horas_y")
            horas_tamano = st.slider("Tamaño Fuente", 10, 100, config_actual.get('horas_tamano', 18), key="horas_tamano")
            
            # Tutor/Facilitador
            st.markdown("##### Tutor/Facilitador")
            tutor_x = st.slider("Posición X", 0, 1000, config_actual.get('tutor_x', 100), key="tutor_x")
            tutor_y = st.slider("Posición Y", 0, 1000, config_actual.get('tutor_y', 300), key="tutor_y")
            tutor_tamano = st.slider("Tamaño Fuente", 10, 100, config_actual.get('tutor_tamano', 18), key="tutor_tamano")
        
        with col2:
            st.markdown("**Reverso**")
            
            # Código Curso
            st.markdown("##### Código Curso")
            codigo_x = st.slider("Posición X", 0, 1000, config_actual.get('codigo_x', 100), key="codigo_x")
            codigo_y = st.slider("Posición Y", 0, 1000, config_actual.get('codigo_y', 150), key="codigo_y")
            codigo_tamano = st.slider("Tamaño Fuente", 10, 100, config_actual.get('codigo_tamano', 16), key="codigo_tamano")
            
            # Contenido
            st.markdown("##### Contenido")
            contenido_x = st.slider("Posición X", 0, 1000, config_actual.get('contenido_x', 100), key="contenido_x")
            contenido_y = st.slider("Posición Y", 0, 1000, config_actual.get('contenido_y', 200), key="contenido_y")
            contenido_tamano = st.slider("Tamaño Fuente", 10, 100, config_actual.get('contenido_tamano', 14), key="contenido_tamano")
            contenido_ancho = st.slider("Ancho Máximo", 100, 800, config_actual.get('contenido_ancho', 600), key="contenido_ancho")
        
        # Botón de guardar
        if st.button("💾 Guardar Configuración", type="primary", key="guardar_config_certificados"):
            guardar_configuracion_certificados({
                'nombre_x': nombre_x, 'nombre_y': nombre_y, 'nombre_tamano': nombre_tamano,
                'horas_x': horas_x, 'horas_y': horas_y, 'horas_tamano': horas_tamano,
                'tutor_x': tutor_x, 'tutor_y': tutor_y, 'tutor_tamano': tutor_tamano,
                'codigo_x': codigo_x, 'codigo_y': codigo_y, 'codigo_tamano': codigo_tamano,
                'contenido_x': contenido_x, 'contenido_y': contenido_y, 
                'contenido_tamano': contenido_tamano, 'contenido_ancho': contenido_ancho
            })
            st.success("Configuración guardada exitosamente")
            st.rerun()
            
    except Exception as e:
        st.error(f"Error en configuración de plantillas: {e}")

def obtener_configuracion_certificados():
    """Obtener configuración actual de certificados"""
    try:
        query = "SELECT * FROM configuracion_certificados ORDER BY id DESC LIMIT 1"
        resultado = execute_query(query)
        
        if resultado and len(resultado) > 0:
            return resultado[0]
        else:
            # Valores por defecto
            return {
                'nombre_x': 100, 'nombre_y': 200, 'nombre_tamano': 24,
                'horas_x': 100, 'horas_y': 250, 'horas_tamano': 18,
                'tutor_x': 100, 'tutor_y': 300, 'tutor_tamano': 18,
                'codigo_x': 100, 'codigo_y': 150, 'codigo_tamano': 16,
                'contenido_x': 100, 'contenido_y': 200, 'contenido_tamano': 14, 'contenido_ancho': 600
            }
    except Exception as e:
        st.error(f"Error obteniendo configuración: {e}")
        return {}

def guardar_configuracion_certificados(config):
    """Guardar configuración de certificados"""
    try:
        # Verificar si ya existe configuración
        query_check = "SELECT COUNT(*) as count FROM configuracion_certificados"
        resultado = execute_query(query_check)
        
        if resultado and resultado[0]['count'] > 0:
            # Actualizar configuración existente
            query_update = """
            UPDATE configuracion_certificados SET
                nombre_x = %s, nombre_y = %s, nombre_tamano = %s,
                horas_x = %s, horas_y = %s, horas_tamano = %s,
                tutor_x = %s, tutor_y = %s, tutor_tamano = %s,
                codigo_x = %s, codigo_y = %s, codigo_tamano = %s,
                contenido_x = %s, contenido_y = %s, contenido_tamano = %s, contenido_ancho = %s,
                fecha_actualizacion = %s
            WHERE id = (SELECT id FROM configuracion_certificados ORDER BY id DESC LIMIT 1)
            """
            params = (
                config['nombre_x'], config['nombre_y'], config['nombre_tamano'],
                config['horas_x'], config['horas_y'], config['horas_tamano'],
                config['tutor_x'], config['tutor_y'], config['tutor_tamano'],
                config['codigo_x'], config['codigo_y'], config['codigo_tamano'],
                config['contenido_x'], config['contenido_y'], config['contenido_tamano'], config['contenido_ancho'],
                datetime.now()
            )
            execute_query(query_update, params)
        else:
            # Insertar nueva configuración
            query_insert = """
            INSERT INTO configuracion_certificados (
                nombre_x, nombre_y, nombre_tamano,
                horas_x, horas_y, horas_tamano,
                tutor_x, tutor_y, tutor_tamano,
                codigo_x, codigo_y, codigo_tamano,
                contenido_x, contenido_y, contenido_tamano, contenido_ancho,
                fecha_creacion
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                config['nombre_x'], config['nombre_y'], config['nombre_tamano'],
                config['horas_x'], config['horas_y'], config['horas_tamano'],
                config['tutor_x'], config['tutor_y'], config['tutor_tamano'],
                config['codigo_x'], config['codigo_y'], config['codigo_tamano'],
                config['contenido_x'], config['contenido_y'], config['contenido_tamano'], config['contenido_ancho'],
                datetime.now()
            )
            execute_query(query_insert, params)
            
    except Exception as e:
        st.error(f"Error guardando configuración: {e}")

def guardar_imagen_certificado(archivo, tipo):
    """Guardar imagen de certificado"""
    try:
        # Crear directorio assets si no existe
        if not os.path.exists('assets'):
            os.makedirs('assets')
        
        # Guardar archivo
        ruta = f'assets/certificado_{tipo}_actual.jpg'
        with open(ruta, 'wb') as f:
            f.write(archivo.getbuffer())
        
        return ruta
    except Exception as e:
        st.error(f"Error guardando imagen: {e}")
        return None

def previsualizacion_certificado(db):
    """Previsualización de certificados"""
    try:
        st.markdown("#### Previsualización de Certificado")
        
        # Obtener un taller de ejemplo
        query = """
        SELECT fc.*, COUNT(i.id_inscripcion) as inscritos,
               p.nombre as estudiante_nombre, p.apellido as estudiante_apellido,
               pr.nombre as profesor_nombre, pr.apellido as profesor_apellido
        FROM formacion_complementaria fc
        LEFT JOIN inscripcion i ON fc.id_formacion = i.id_formacion
        LEFT JOIN estudiante e ON fc.id_usuario = e.cedula_estudiante
        LEFT JOIN persona p ON e.cedula_estudiante = p.cedula
        LEFT JOIN usuarios u ON fc.id_usuario = u.cedula_usuario
        LEFT JOIN profesor pr ON fc.id_usuario = pr.cedula_profesor
        WHERE fc.fecha_creacion >= CURRENT_DATE - INTERVAL '1 year'
        LIMIT 1
        """
        
        resultado = execute_query(query)
        
        if not resultado:
            st.warning("No hay talleres disponibles para previsualización")
            return
        
        taller = resultado[0]
        
        # Datos de ejemplo
        datos_ejemplo = {
            'nombre_estudiante': f"{taller.get('estudiante_nombre', 'Juan')} {taller.get('estudiante_apellido', 'Pérez')}",
            'horas': taller.get('horas', 40),
            'tutor': f"{taller.get('profesor_nombre', 'María')} {taller.get('profesor_apellido', 'González')}",
            'codigo_curso': taller.get('codigo_certificado', 'IU-FOC-2024-001'),
            'contenido': f"El participante ha completado satisfactoriamente el taller '{taller.get('nombre', 'Taller Ejemplo')}' con una duración de {taller.get('horas', 40)} horas académicas. Este certificado se expide en reconocimiento a su dedicación y compromiso durante el período de formación complementaria."
        }
        
        # Generar certificado
        imagen_certificado = generar_imagen_certificado(datos_ejemplo)
        
        if imagen_certificado:
            st.image(imagen_certificado, caption="Previsualización del Certificado", use_container_width=True)
            
            # Botón de descarga
            img_buffer = io.BytesIO()
            imagen_certificado.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            st.download_button(
                label=" Descargar Previsualización",
                data=img_buffer,
                file_name="certificado_previsualizacion.png",
                mime="image/png"
            )
        else:
            st.error("No se pudo generar la previsualización")
            
    except Exception as e:
        st.error(f"Error en previsualización: {e}")

def generacion_certificados(db):
    """Generación de certificados para talleres"""
    try:
        st.markdown("#### Generación de Certificados")
        
        # Listar talleres finalizados con inscritos
        query = """
        SELECT fc.*, COUNT(i.id_inscripcion) as inscritos
        FROM formacion_complementaria fc
        LEFT JOIN inscripcion i ON fc.id_formacion = i.id_formacion
        WHERE fc.fecha_creacion < CURRENT_DATE - INTERVAL '30 days'
        GROUP BY fc.id_formacion
        HAVING COUNT(i.id_inscripcion) > 0
        ORDER BY fc.fecha_creacion DESC
        """
        
        resultado = execute_query(query)
        
        if not resultado:
            st.info("No hay talleres finalizados con inscritos")
            return
        
        # Selector de taller
        opciones_talleres = [f"{t['nombre']} ({t['inscritos']} inscritos)" for t in resultado]
        taller_seleccionado = st.selectbox("Seleccionar Taller", opciones_talleres)
        
        if taller_seleccionado:
            indice = opciones_talleres.index(taller_seleccionado)
            taller = resultado[indice]
            
            # Botón de generación con manejo robusto de errores
            if st.button(" Generar Certificados", type="primary", key="generar_certificados_taller"):
                try:
                    # Verificar conexión antes de procesar
                    from db_manager import verificar_conexion
                    if not verificar_conexion():
                        st.error(" Error de conexión antes de generar certificados")
                        st.warning("Por favor, recargue la página e intente nuevamente.")
                        return
                    
                    with st.spinner("Generando certificados..."):
                        generar_certificados_taller(taller['id'])
                    
                    st.success(f"Certificados generados para '{taller['nombre']}'")
                    
                except Exception as e:
                    # DETECCIÓN Y RECUPERACIÓN AUTOMÁTICA
                    print(f" Error generando certificados: {e}")
                    st.error(" Ocurrió un error inesperado al generar certificados")
                    st.info(" El sistema intentará recuperar la conexión automáticamente...")
                    
                    # Marcar para recuperación en siguiente interacción
                    st.session_state.transaccion_abortada = True
                    st.session_state.error_certificados = str(e)
                
    except Exception as e:
        # DETECCIÓN Y RECUPERACIÓN AUTOMÁTICA
        print(f" Error general en generación de certificados: {e}")
        st.error(" Ocurrió un error inesperado en el módulo de certificados")
        st.info(" El sistema intentará recuperar la conexión automáticamente...")
        
        # Marcar para recuperación en siguiente interacción
        st.session_state.transaccion_abortada = True
        st.session_state.error_certificados = str(e)

def generar_imagen_certificado(datos):
    """Generar imagen del certificado usando Pillow"""
    try:
        config = obtener_configuracion_certificados()
        
        # Cargar imágenes de fondo
        ruta_anverso = "assets/certificado_anverso_actual.jpg"
        ruta_reverso = "assets/certificado_reverso_actual.jpg"
        
        # Usar imágenes por defecto si no existen
        if not os.path.exists(ruta_anverso):
            ruta_anverso = "assets/certificado_anverso_default.jpg"
        if not os.path.exists(ruta_reverso):
            ruta_reverso = "assets/certificado_reverso_default.jpg"
        
        # Crear imagen combinada (anverso y reverso)
        if os.path.exists(ruta_anverso):
            anverso = Image.open(ruta_anverso)
        else:
            # Imagen por defecto
            anverso = Image.new('RGB', (800, 600), color='white')
        
        # Dibujar sobre el anverso
        draw = ImageDraw.Draw(anverso)
        
        try:
            # Intentar usar fuentes del sistema
            font_nombre = ImageFont.truetype("arial.ttf", config.get('nombre_tamano', 24))
            font_horas = ImageFont.truetype("arial.ttf", config.get('horas_tamano', 18))
            font_tutor = ImageFont.truetype("arial.ttf", config.get('tutor_tamano', 18))
        except:
            # Usar fuente por defecto
            font_nombre = ImageFont.load_default()
            font_horas = ImageFont.load_default()
            font_tutor = ImageFont.load_default()
        
        # Dibujar texto en el anverso
        draw.text(
            (config.get('nombre_x', 100), config.get('nombre_y', 200)),
            datos['nombre_estudiante'],
            fill='black',
            font=font_nombre
        )
        
        draw.text(
            (config.get('horas_x', 100), config.get('horas_y', 250)),
            f"Horas: {datos['horas']}",
            fill='black',
            font=font_horas
        )
        
        draw.text(
            (config.get('tutor_x', 100), config.get('tutor_y', 300)),
            f"Tutor: {datos['tutor']}",
            fill='black',
            font=font_tutor
        )
        
        # Procesar reverso si existe la imagen
        if os.path.exists(ruta_reverso):
            reverso = Image.open(ruta_reverso)
            draw_reverso = ImageDraw.Draw(reverso)
            
            try:
                font_codigo = ImageFont.truetype("arial.ttf", config.get('codigo_tamano', 16))
                font_contenido = ImageFont.truetype("arial.ttf", config.get('contenido_tamano', 14))
            except:
                font_codigo = ImageFont.load_default()
                font_contenido = ImageFont.load_default()
            
            # Dibujar código en el reverso
            draw_reverso.text(
                (config.get('codigo_x', 100), config.get('codigo_y', 150)),
                datos['codigo_curso'],
                fill='black',
                font=font_codigo
            )
            
            # Dibujar contenido con ajuste automático de texto
            texto_ajustado = ajustar_texto_caja(
                datos['contenido'], 
                config.get('contenido_ancho', 600),
                font_contenido
            )
            
            # Dibujar cada línea del contenido
            y_actual = config.get('contenido_y', 200)
            for linea in texto_ajustado:
                draw_reverso.text(
                    (config.get('contenido_x', 100), y_actual),
                    linea,
                    fill='black',
                    font=font_contenido
                )
                y_actual += config.get('contenido_tamano', 14) + 2  # Espacio entre líneas
            
            # Combinar anverso y reverso verticalmente
            ancho_final = max(anverso.width, reverso.width)
            alto_final = anverso.height + reverso.height
            
            imagen_final = Image.new('RGB', (ancho_final, alto_final), color='white')
            imagen_final.paste(anverso, (0, 0))
            imagen_final.paste(reverso, (0, anverso.height))
            
            return imagen_final
        
        return anverso
        
    except Exception as e:
        st.error(f"Error generando imagen: {e}")
        return None

def ajustar_texto_caja(texto, ancho_maximo, fuente):
    """Ajusta texto para que quepa en un ancho máximo con saltos de línea automáticos"""
    try:
        palabras = texto.split(' ')
        lineas = []
        linea_actual = []
        
        for palabra in palabras:
            # Probar añadir la palabra a la línea actual
            linea_temp = ' '.join(linea_actual + [palabra])
            
            # Obtener el ancho del texto
            try:
                bbox = fuente.getbbox(linea_temp)
                ancho_texto = bbox[2] - bbox[0]
            except:
                # Si no podemos obtener el bbox, usar estimación simple
                ancho_texto = len(linea_temp) * (fuente.size or 14) * 0.6
            
            # Si el texto excede el ancho máximo, empezar nueva línea
            if ancho_texto > ancho_maximo and linea_actual:
                lineas.append(' '.join(linea_actual))
                linea_actual = [palabra]
            else:
                linea_actual.append(palabra)
        
        # Añadir la última línea
        if linea_actual:
            lineas.append(' '.join(linea_actual))
        
        return lineas
        
    except Exception as e:
        # Si hay error, devolver el texto original dividido por longitud
        return [texto[i:i+50] for i in range(0, len(texto), 50)]

def generar_certificados_taller(taller_id):
    """Generar certificados para todos los inscritos en un taller"""
    try:
        # Obtener inscritos del taller
        query = """
        SELECT i.*, e.nombre as estudiante_nombre, e.apellido as estudiante_apellido,
               fc.nombre as taller_nombre, fc.horas, fc.codigo_certificado,
               pr.nombre as profesor_nombre, pr.apellido as profesor_apellido
        FROM inscripcion i
        LEFT JOIN students e ON u.user_id = e.student_id
        LEFT JOIN formacion_complementaria fc ON i.id_formacion = fc.id
        LEFT JOIN usuario u ON fc.id_usuario = u.id
        LEFT JOIN profesor pr ON u.cedula = pr.cedula
        WHERE i.id_formacion = %s AND i.estado = 'Completado'
        """
        
        resultado = execute_query(query, (taller_id,))
        
        if not resultado:
            st.warning("No hay inscritos completados en este taller")
            return
        
        certificados_generados = 0
        
        for inscripcion in resultado:
            datos = {
                'nombre_estudiante': f"{inscripcion['estudiante_nombre']} {inscripcion['estudiante_apellido']}",
                'horas': inscripcion['horas'],
                'tutor': f"{inscripcion['profesor_nombre']} {inscripcion['profesor_apellido']}",
                'codigo_curso': inscripcion['codigo_certificado'],
                'contenido': f"Ha completado el taller '{inscripcion['taller_nombre']}'"
            }
            
            # Generar imagen
            imagen = generar_imagen_certificado(datos)
            
            if imagen:
                # Guardar certificado (aquí se podría guardar en BD o sistema de archivos)
                certificados_generados += 1
        
        st.info(f"Se generaron {certificados_generados} certificados")
        
    except Exception as e:
        st.error(f"Error generando certificados del taller: {e}")

def reportes_formacion(db, rol_usuario):
    """Reportes de formación complementaria"""
    st.subheader("Reportes de Formación")
    st.info("Función de reportes en desarrollo")

def gestion_formacion_complementaria():
    """Función principal del módulo de gestión de formación complementaria"""
    try:
        # Obtener rol del usuario
        rol_usuario = st.session_state.get('user_role', None)
        
        if rol_usuario is None:
            st.error("No se pudo determinar el rol del usuario")
            return
        
        # Importar el motor central
        from database import motor_central
        
        # Mostrar interface principal de formación complementaria
        st.header("Gestión de Formación Complementaria")
        
        # Opciones principales
        tab1, tab2, tab3 = st.tabs(["Talleres", "Inscripciones", "Reportes"])
        
        with tab1:
            gestion_talleres(motor_central, rol_usuario)
        
        with tab2:
            inscripciones_talleres(motor_central, rol_usuario)
        
        with tab3:
            reportes_formacion(motor_central, rol_usuario)
            
    except Exception as e:
        st.error(f"Error en el módulo de gestión de formación complementaria: {e}")
