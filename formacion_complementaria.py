import streamlit as st
import pandas as pd
import sys
import os
from datetime import date, datetime
from PIL import Image, ImageDraw, ImageFont
import io

@st.cache_data(ttl=3600)  # Cache por 1 hora para consultas estáticas
def obtener_lista_profesores_cache():
    """Obtener lista de profesores con cache - ESQUEMA UNIFICADO db_foc26"""
    print(">> FORMACION: Obteniendo lista de profesores (conexión unificada)")
    try:
        from database import execute_query
        query = """
        SELECT p.cedula, p.nombre, p.apellido, pr.especialidad
        FROM persona p
        JOIN usuarios u ON p.cedula = u.cedula_usuario
        LEFT JOIN profesor pr ON p.cedula = pr.cedula_profesor
        WHERE u.rol = 'Profesor' AND u.activo = true
        ORDER BY p.apellido, p.nombre
        """
        result = execute_query(query)
        print(f">> FORMACION: Profesores obtenidos - {len(result) if isinstance(result, list) else 1}")
        return result
    except Exception as e:
        print(f">> ERROR FORMACION: {e}")
        return []

@st.cache_data(ttl=3600)  # Cache por 1 hora para tipos de talleres
def obtener_tipos_talleres_cache():
    """Obtener tipos de talleres con cache"""
    try:
        from database import execute_query
        query = """
        SELECT DISTINCT tipo_taller
        FROM taller
        WHERE tipo_taller IS NOT NULL
        ORDER BY tipo_taller
        """
        result = execute_query(query)
        return [item['tipo_taller'] for item in result] if result else []
    except Exception:
        return []

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
    
    def leer_formaciones(self, filtros=None, orden='codigo_formacion DESC'):
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
            u.cedula_usuario, u.rol, u.activo, u.email as email_estudiante,
            p.nombre, p.apellido, p.cedula, p.telefono, p.fecha_nacimiento, p.sexo, p.direccion,
            e.id_carrera, e.semestre_actual, e.estado_registro
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
            pr.especialidad, pr.fecha_contratacion, pr.estado as estado_profesor
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
        
        # Agrupar contenido en tabs para evitar scroll
        if SeguridadFOC26.is_admin() or SeguridadFOC26.is_profesor():
            tab1, tab2, tab3, tab4 = st.tabs([
                "📋 Gestión de Talleres", 
                "👥 Gestión de Participación", 
                "🎨 Editor de Certificados", 
                "📊 Reportes"
            ])
            
            with tab1:
                gestion_talleres(db, rol_usuario)
            
            with tab2:
                # Importar y mostrar el nuevo módulo de gestión de participación
                try:
                    from inscripciones import mostrar_formulario_inscripcion
                    mostrar_formulario_inscripcion()
                except ImportError as e:
                    st.error(f"Error importando módulo de gestión: {e}")
                    st.info("Función de gestión de participación en desarrollo")
            
            with tab3:
                st.info("El Editor de Certificados ha sido movido al sidebar principal")
                st.write("Utilice el botón 'Editor de Certificados' en el menú lateral para acceder a esta función.")
            
            with tab4:
                try:
                    from reportes_formacion import reportes_formacion
                    reportes_formacion(db, rol_usuario)
                except ImportError as e:
                    st.error(f"Error importando módulo de reportes: {e}")
                    st.info("Función de reportes en desarrollo")
                
        elif SeguridadFOC26.is_estudiante():
            tab1, tab2 = st.tabs([
                "📚 Talleres Disponibles", 
                "📝 Mi Participación"
            ])
            
            with tab1:
                talleres_disponibles(db, rol_usuario)
            
            with tab2:
                # Importar y mostrar el nuevo módulo de participación del estudiante
                try:
                    from inscripciones import mostrar_mis_inscripciones
                    mostrar_mis_inscripciones()
                except ImportError as e:
                    st.error(f"Error importando módulo de participación: {e}")
                    st.info("Función de mi participación en desarrollo")
        
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
            cohorte = st.selectbox("Cohorte*", options=[1, 2], help="Seleccione la cohorte del taller")
            estado = st.selectbox("Estado", ["Activo", "Inactivo", "Próximo"])
            
        st.markdown("### Datos del Certificado")
        col3, col4 = st.columns(2)
        
        with col3:
            tomo = st.text_input("Tomo*", placeholder="001", help="Número de tomo del certificado")
            folio = st.text_input("Folio*", placeholder="12345", help="Número de folio del certificado")
            
        with col4:
            facilitador = st.text_input("Facilitador", placeholder="Nombre del facilitador")
            
            # Generar código automático con formato IU-FOC-[Año]-[Cohorte]-[Tomo]
            if tomo and cohorte:
                año_actual = date.today().year
                tomo_formateado = tomo.zfill(3)  # Formatear a 3 dígitos (001, 002, etc.)
                codigo_certificado = f"IU-FOC-{año_actual}-{cohorte}-{tomo_formateado}"
            else:
                codigo_certificado = ""
            
            st.text_input("Código del Certificado", 
                         value=codigo_certificado,
                         disabled=True)
            
        submit_taller = st.form_submit_button("Crear Taller")
        
        if submit_taller:
            # VALIDACIÓN DE CAMPOS OBLIGATORIOS
            campos_obligatorios = [nombre_taller, descripcion, tomo, cohorte]
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
                        'cohorte': cohorte,
                        'facilitador': facilitador,
                        'fecha_inicio': datetime.now().date()
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
        resultado = motor_formacion.leer_formaciones(orden='codigo_formacion DESC')
        
        if not resultado['success']:
            st.error(f"Error al obtener talleres: {resultado['message']}")
            return
        
        talleres = resultado['data']
        
        if not talleres:
            st.info("No hay talleres registrados")
            return
        
        # CONVERTIR A DATAFRAME PARA VISUALIZACIÓN
        df = pd.DataFrame(talleres)
        
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
        resultado = motor_formacion.leer_formaciones(orden='codigo_formacion DESC')
        
        if not resultado['success']:
            # Si hay error, simplemente mostrar mensaje amigable
            st.info("No hay talleres disponibles en este momento")
            return
        
        talleres = resultado['data']
        
        # FILTRAR TALLERES ACTIVOS Y DISPONIBLES
        talleres_disponibles = []
        for t in talleres:
            try:
                # Verificar si el taller está activo y tiene cupo disponible
                estado = t.get('id_estado_registro', 1)  # 1 = Activo por defecto
                cupo_actual = t.get('cupo_actual', 0)
                cupo_maximo = t.get('cupo_maximo', 1)
                
                if estado == 1 and cupo_actual < cupo_maximo:
                    talleres_disponibles.append(t)
            except Exception:
                # Si hay error al procesar un taller, simplemente omitirlo
                continue
        
        if not talleres_disponibles:
            st.info("No hay talleres disponibles en este momento")
            return
        
        # CONVERTIR A DATAFRAME PARA VISUALIZACIÓN
        df = pd.DataFrame(talleres_disponibles)
        
        # FORMATEAR COLUMNAS
        df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio']).dt.strftime('%Y-%m-%d')
        df['fecha_fin'] = pd.to_datetime(df['fecha_fin']).dt.strftime('%Y-%m-%d')
        df['cupo_disponible'] = df['cupo_maximo'] - df['cupo_actual']
        
        # MOSTRAR TABLA CON COLUMNAS RELEVANTES
        st.dataframe(
            df[['nombre_taller', 'descripcion', 'fecha_inicio', 'fecha_fin', 
                'cupo_disponible', 'estado', 'codigo_certificado']],
            column_config={
                'nombre_taller': 'Nombre del Taller',
                'descripcion': 'Descripción',
                'fecha_inicio': 'Fecha Inicio',
                'fecha_fin': 'Fecha Fin',
                'cupo_disponible': 'Cupos Disponibles',
                'estado': 'Estado',
                'codigo_certificado': 'Código Certificado'
            },
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"Error al cargar talleres disponibles: {e}")

def gestion_participacion_formacion(db, rol_usuario):
    """Gestión de participación en talleres"""
    st.subheader("Gestión de Participación")
    st.info("Función de gestión de participación en desarrollo")

def mi_participacion(db, rol_usuario):
    """Mostrar participación del estudiante actual"""
    st.subheader("Mi Participación")
    
    # Aquí iría la lógica para mostrar la participación del estudiante actual
    st.info("Función en desarrollo...")
