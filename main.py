import streamlit as st
import pandas as pd
import os
import io
import shutil
from datetime import datetime
from sqlalchemy import text

# Configuración de página para despliegue responsive
st.set_page_config(
    page_title="SICADFOC - Sistema de Control de Formación Complementaria",
    page_icon="🎓",
    layout="wide",  # Aprovecha mejor las pantallas de laptops
    initial_sidebar_state="expanded"
)
from database import (
    get_connection, get_connection_info,
    listar_estudiantes, insertar_estudiante, actualizar_estudiante, eliminar_estudiante,
    insertar_formacion, listar_formaciones, eliminar_formacion,
    inscribir_estudiante_taller, obtener_profesores, eliminar_profesor,
    registrar_auditoria, obtener_auditoria,
    guardar_config_correo, obtener_config_correo,
    crear_usuario_prueba, crear_tablas_sistema, ejecutar_query, insertar_profesor,
    limpiar_columnas_profesores, limpiar_columnas_estudiantes, asegurar_estructura_persona,
    get_metricas_dashboard,
    sincronizar_base_de_datos, generar_backup_sql, migrar_datos_a_nube, verificar_entorno_local
)

# --- FUNCIONES CALLBACK PARA BOTONES DE ACCIÓN ---

def callback_consultar_formacion(formacion_id, formacion_data):
    """Callback para botón consultar formación"""
    st.session_state.accion_pendiente = 'consultar_formacion'
    st.session_state.formacion_id_seleccionada = formacion_id
    st.session_state.formacion_editar = formacion_data
    st.session_state.modo_edicion = False
    st.session_state.tab_activa = 1

def callback_editar_formacion(formacion_id, formacion_data):
    """Callback para botón editar formación"""
    st.session_state.accion_pendiente = 'editar_formacion'
    st.session_state.formacion_id_seleccionada = formacion_id
    st.session_state.formacion_editar = formacion_data
    st.session_state.modo_edicion = True
    st.session_state.tab_activa = 1

def callback_eliminar_formacion(formacion_id, nombre_formacion):
    """Callback para botón eliminar formación"""
    st.session_state.accion_pendiente = 'eliminar_formacion'
    st.session_state.formacion_id_seleccionada = formacion_id
    st.session_state.nombre_formacion_eliminar = nombre_formacion

def callback_editar_profesor(profesor_id, profesor_data):
    """Callback para botón editar profesor"""
    st.session_state.accion_pendiente = 'editar_profesor'
    st.session_state.profesor_id_seleccionado = profesor_id
    st.session_state.profesor_editar = profesor_data
    st.session_state.tab_prof_activa = 2

def callback_eliminar_profesor(profesor_id, nombre_profesor):
    """Callback para botón eliminar profesor"""
    st.session_state.accion_pendiente = 'eliminar_profesor'
    st.session_state.profesor_id_seleccionado = profesor_id
    st.session_state.nombre_prof_eliminar = nombre_profesor

# =================================================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS (SISTEMA SICADFOC)
# =================================================================
st.set_page_config(
    page_title="SICADFOC - IUJO",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded"
)

# CSS Personalizado: Botones en Gris (#6c757d) para Ingresar y Finalizar Sesión
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }

    /* Botones de acción general (Rojo IUJO) */
    .stButton>button {
        background-color: #AA1914;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        height: 3.2em;
        width: 100%;
        transition: 0.3s;
    }

    /* BOTÓN INGRESAR y FINALIZAR SESIÓN - Gris #6c757d específicamente */
    div.stForm [data-testid="stFormSubmitButton"] > button,
    div[data-testid="stSidebar"] .stButton > button {
        background-color: #6c757d !important;
        color: white !important;
        border: 1px solid #5a6268 !important;
    }
    div.stForm [data-testid="stFormSubmitButton"] > button:hover,
    div[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #5a6268 !important;
        color: white !important;
        opacity: 0.9;
    }

    .stButton>button:hover { background-color: #5a6268; color: white; opacity: 0.9; }

    /* Estilo del Sidebar */
    [data-testid="stSidebar"] { background-color: #1e1e1e; color: white; }
    [data-testid="stSidebarNav"] { background-color: #1e1e1e; }

    /* Estilo de Tabs */
    .stTabs [aria-selected="true"] {
        background-color: #AA1914 !important;
        color: white !important;
        border-radius: 5px 5px 0 0;
    }

    /* Métricas */
    div[data-testid="stMetricValue"] { color: #AA1914; font-size: 2.4rem; font-weight: bold; }
    .footer { position: fixed; bottom: 10px; width: 100%; text-align: center; color: #888; font-size: 0.8em; }

    /* Tablas limpias */
    div[data-testid="stDataFrame"] {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .stDataFrame th { background-color: #AA1914 !important; color: white !important; font-weight: 600; }
    .stDataFrame td { padding: 8px 12px !important; }
    .tabla-contenedor { padding: 1rem; background: white; border-radius: 8px; border: 1px solid #dee2e6; margin: 0.5rem 0; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 2. INICIALIZACIÓN DE CONEXIONES Y SESIÓN
# =================================================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if 'id_persona_est' not in st.session_state:
    st.session_state.id_persona_est = None
    st.session_state.nombre_est = ""
    st.session_state.apellido_est = ""

# Motores de base de datos
engine_l = get_connection()
engine_r = get_connection()

# =================================================================
# 2.5. SISTEMA DE ROLES Y PERFILES (RBAC)
# =================================================================
def obtener_rol_usuario():
    """Obtiene el rol del usuario desde st.session_state.rol"""
    return st.session_state.get('rol', 'estudiante')

def es_admin():
    """Verifica si el usuario es administrador"""
    return obtener_rol_usuario() == 'admin'

def es_profesor():
    """Verifica si el usuario es profesor"""
    return obtener_rol_usuario() == 'profesor'

def es_estudiante():
    """Verifica si el usuario es estudiante"""
    return obtener_rol_usuario() == 'estudiante'

def es_admin_o_profesor():
    """Verifica si el usuario es administrador o profesor"""
    rol = obtener_rol_usuario()
    return rol in ['admin', 'profesor']

def mostrar_mensaje_restringido():
    """Muestra mensaje de acceso restringido según el rol"""
    rol = obtener_rol_usuario()
    if rol == 'estudiante':
        st.warning("🔒 Esta función está disponible solo para administradores y profesores.")
        st.info("Si necesita acceso, contacte al administrador del sistema.")
    elif rol == 'profesor':
        st.warning("🔒 Esta función está disponible solo para administradores.")
        st.info("Si necesita acceso, contacte al administrador del sistema.")

# =================================================================
# 3. INTERFAZ DE AUTENTICACIÓN (LOGIN)
# =================================================================
if not st.session_state.autenticado:
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        if os.path.exists("iujo-logo.png"):
            st.image("iujo-logo.png", width=280)
        st.title("SICADFOC 2026")
        st.subheader("Control Académico IUJO")

        with st.form("login_form"):
            u = st.text_input("Correo Institucional")
            p = st.text_input("Cédula (Contraseña)", type="password")
            btn_login = st.form_submit_button("INGRESAR AL SISTEMA")

            if btn_login:
                # Crear tablas del sistema si no existen
                crear_tablas_sistema(engine_l)
                
                # Crear usuario de prueba si no existe
                crear_usuario_prueba(engine_l)
                
                # Verificación en Gabinete Local con Correo/Cédula
                query_auth = """
                    SELECT * FROM public.usuario 
                    WHERE (email = :email OR login = :email) AND contrasena = :password AND activo = TRUE
                """
                res_auth = ejecutar_query(query_auth, {"email": u, "password": p}, engine=engine_l)

                if res_auth:
                    usuario_data = res_auth[0]
                    st.session_state.autenticado = True
                    st.session_state.user_data = usuario_data
                    st.session_state.rol = usuario_data.get('rol', 'estudiante')
                    
                    # Registrar auditoría de login
                    registrar_auditoria(
                        usuario=usuario_data.get('login', u),
                        rol=st.session_state.rol,
                        transaccion='LOGIN',
                        tabla_afectada='usuario',
                        ip_address=st.context.headers.get('x-forwarded-for', 'localhost'),
                        engine=engine_l
                    )
                    
                    st.success(f"✅ Bienvenido {usuario_data.get('login', u)}. Rol: {st.session_state.rol.title()}")
                    st.rerun()
                else:
                    st.error("❌ Error de autenticación. Verifique su correo y cédula.")
                    st.info("💡 Si es su primer acceso, contacte al administrador del sistema.")
    st.stop()

# =================================================================
# 4. PANEL DE NAVEGACIÓN (SIDEBAR)
# =================================================================
with st.sidebar:
    if os.path.exists("iujo-logo.png"):
        st.image("iujo-logo.png", width=160)

    st.markdown(f"### 👤 {st.session_state.user_data['login']}")
    rol_actual = obtener_rol_usuario()
    st.caption(f"Nivel: {rol_actual.title() if rol_actual else 'Desconocido'}")
    st.divider()

    # Menú de navegación principal
    modulo = st.radio(
        "Módulos Operativos:",
        ["Inicio", "Gestión Estudiantil", "Gestión de Profesores", "Gestión de Formación Complementaria", "Configuración", "Reportes", "Monitor de Sistema"],
        index=0
    )

    st.markdown("<br>" * 10, unsafe_allow_html=True)
    if st.button("🚪 Finalizar Sesión"):
        st.session_state.clear()
        st.rerun()

# =================================================================
# 5. DESARROLLO DE MÓDULOS OPERATIVOS
# =================================================================

# --- MÓDULO A: INICIO ---
if modulo == "Inicio":
    st.header("🏠 Panel Principal de Control")
    st.write(f"Resumen de operaciones para el usuario: **{st.session_state.user_data['login']}**")

    col_dash1, col_dash2, col_dash3 = st.columns(3)

    try:
        metricas = get_metricas_dashboard(engine_l)
        t_talleres = metricas['talleres']
        t_estudiantes = metricas['estudiantes']
        t_profesores = metricas['profesores']

        col_dash1.metric("Talleres Activos", t_talleres)
        col_dash2.metric("Estudiantes Registrados", t_estudiantes)
        col_dash3.metric("Profesores", t_profesores)

    except Exception as e:
        st.warning("⚠️ Sincronizando datos con el Gabinete Local...")

    st.divider()
    st.info("💡 **Aviso:** El Monitor de Infraestructura ahora se encuentra en el menú lateral para una vista más limpia.")

# --- MÓDULO B: MONITOR DE SISTEMA (GABINETES) ---
elif modulo == "Monitor de Sistema":
    st.header("⚡ Monitor de Infraestructura de Datos")
    st.write("Verificación de gabinetes FOC26 (Local y Cloud).")

    col_mon1, col_mon2 = st.columns(2)

    with col_mon1:
        st.subheader("🖥️ Gabinete Local (PC)")
        if engine_l:
            try:
                with engine_l.connect() as conn:
                    res_l = conn.execute(text("SELECT current_database(), current_user, version()")).fetchone()
                    st.success("✅ Servidor Local: ONLINE")
                    st.table(pd.DataFrame([{
                        "Base de Datos": res_l[0],
                        "Usuario": res_l[1],
                        "Estado": "Sincronizado"
                    }]))
            except Exception as e:
                st.error(f"❌ Error de conexión Local: {e}")

    with col_mon2:
        st.subheader("☁️ Gabinete Render (Cloud)")
        if engine_r and not isinstance(engine_r, str):
            try:
                with engine_r.connect() as conn:
                    res_r = conn.execute(text("SELECT current_database()")).fetchone()
                    st.success("✅ Servidor Render: CONECTADO")
                    st.table(pd.DataFrame([{
                        "Base de Datos": res_r[0],
                        "Región": "USA-East",
                        "Plataforma": "Render.com"
                    }]))
            except Exception as e:
                st.error(f"❌ Error de conexión Cloud: {e}")
        else:
            st.warning("⚠️ Conexión Cloud no detectada o configurada.")

# --- MÓDULO C: GESTIÓN ESTUDIANTIL ---
elif modulo == "Gestión Estudiantil":
    asegurar_estructura_persona(engine_l)
    st.header("📂 Gestión de Matrícula Estudiantil")
    t1, t2, t3, t4, t5, t6 = st.tabs([
        "📝 Inscripción y Carga", "📋 Listado de Estudiantes", "📊 Seguimiento Académico", 
        "🎓 Digitalización PDF", "📜 Historial", "👤 Registro Individual"
    ])

    with t1:
        st.subheader("Proceso de Carga Masiva (Excel/CSV)")
        st.write("Cargue listados de alumnos directamente a la base de datos local.")
        file_bulk = st.file_uploader("Subir archivo de estudiantes", type=['xlsx', 'csv'], key="bulk_est")

        if file_bulk:
            try:
                if file_bulk.name.endswith('.xlsx'):
                    df_b = pd.read_excel(file_bulk)
                else:
                    # Intentar lectura automática de separadores
                    try:
                        df_b = pd.read_csv(file_bulk, sep=None, engine='python', encoding='utf-8-sig')
                    except UnicodeDecodeError:
                        try:
                            df_b = pd.read_csv(file_bulk, sep=None, engine='python', encoding='latin-1')
                        except Exception:
                            df_b = pd.read_csv(file_bulk, sep=None, engine='python', encoding='utf-8')
                    
                    # Limpiar nombres de columnas
                    df_b.columns = df_b.columns.astype(str).str.strip()
                    
                    # Verificar si sigue con una sola columna (fallback)
                    if len(df_b.columns) == 1 and ';' in str(df_b.iloc[0, 0]):
                        st.warning("🔍 Detectando separador punto ycoma...")
                        try:
                            df_b = pd.read_csv(file_bulk, sep=';', encoding='utf-8-sig')
                            df_b.columns = df_b.columns.astype(str).str.strip()
                        except UnicodeDecodeError:
                            df_b = pd.read_csv(file_bulk, sep=';', encoding='latin-1')
                            df_b.columns = df_b.columns.astype(str).str.strip()
                    
                    # Validar que el DataFrame tenga múltiples columnas
                    if len(df_b.columns) == 1:
                        raise ValueError("El archivo no pudo ser procesado correctamente. Solo se detectó una columna. Verifique el separador usado.")
                        
            except Exception as ex:
                st.error(f"❌ Error al leer el archivo: {ex}")
                st.info("💡 Asegúrese de que el archivo use coma (,), punto ycoma (;) o tabulación como separador.")
                df_b = None

            if df_b is not None and not df_b.empty:
                df_limpio, mapeo = limpiar_columnas_estudiantes(df_b)

                if df_limpio is None:
                    st.error("⚠️ El archivo debe contener al menos: Cedula y Nombre. Las demás columnas son opcionales (Apellido, Genero, Telefono, Carrera, Semestre).")
                    st.write("**Columnas detectadas:**", list(df_b.columns))
                    # Solo mostrar vista previa si el DataFrame fue procesado correctamente
                    if len(df_b.columns) > 1:
                        st.markdown("**Vista previa:**")
                        st.dataframe(df_b.head(5), use_container_width=True, hide_index=True)
                else:
                    st.markdown("**Vista previa de datos a cargar**")
                    st.dataframe(df_limpio, use_container_width=True, hide_index=True)
                    st.caption(f"Total: {len(df_limpio)} registros. Columnas: Cedula, Apellido, Nombre, Genero, Telefono, Carrera, Semestre.")

                    if st.button("🚀 Ejecutar Carga en PostgreSQL"):
                        progreso = st.progress(0)
                        total_filas = len(df_limpio)
                        exitosos = 0
                        fallidos = 0
                        errores = []
                        
                        for i, row in df_limpio.iterrows():
                            # Usar .get() para columnas opcionales, solo exigir 'cedula' y 'nombre'
                            cedula = row.get('cedula', '').strip()
                            nombre = row.get('nombre', '').strip()
                            
                            if not cedula or not nombre:
                                fallidos += 1
                                errores.append(f"Fila {i+1}: Cédula y nombre son obligatorios")
                                progreso.progress((i + 1) / total_filas)
                                continue
                            
                            # Columnas opcionales con valores por defecto
                            apellido = row.get('apellido', '').strip()
                            genero = row.get('genero', '').strip()
                            telefono = row.get('telefono', '').strip()
                            carrera = row.get('carrera', '').strip()
                            semestre = row.get('semestre', '').strip()
                            
                            exito, mensaje = insertar_estudiante(
                                cedula=cedula,
                                apellido=apellido,
                                nombre=nombre,
                                genero=genero,
                                telefono=telefono,
                                carrera=carrera,
                                semestre=semestre,
                                engine=engine_l
                            )
                            
                            if exito:
                                exitosos += 1
                            else:
                                fallidos += 1
                                errores.append(f"Fila {i+1}: {mensaje}")
                            
                            progreso.progress((i + 1) / total_filas)
                        
                        # Mostrar resumen de resultados
                        if exitosos > 0:
                            st.success(f"✅ {exitosos} registros procesados exitosamente.")
                        if fallidos > 0:
                            st.error(f"❌ {fallidos} registros fallaron.")
                            with st.expander("Ver detalles de errores"):
                                for error in errores[:10]:  # Limitar a 10 errores para no saturar
                                    st.write(f"• {error}")
                                if len(errores) > 10:
                                    st.write(f"... y {len(errores) - 10} errores más.")
                        
                        st.info("💡 Vaya a la pestaña «Listado de Estudiantes» para verificar los datos cargados.")

    with t2:
        st.subheader("📋 Listado de Estudiantes Registrados")
        st.write("Estudiantes cargados en la base de datos.")
        data_est = listar_estudiantes(engine_l)
        if data_est:
            # Mostrar métricas para admin/profesor
            if es_admin_o_profesor():
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("👥 Total Estudiantes", len(data_est))
                col_m2.metric("✅ Activos", len([e for e in data_est if e.get('Cédula')]))
                col_m3.metric("📊 Registros Hoy", len(data_est))  # TODO: Implementar filtro por fecha
            
            # Convertir a DataFrame para mejor manipulación
            df_est = pd.DataFrame(data_est)
            
            # Tabla de visualización limpia (sin botones)
            st.dataframe(df_est, use_container_width=True, hide_index=True)
            
            # Panel de Gestión Unificado
            if es_admin_o_profesor() and data_est:
                st.subheader("🔧 Panel de Gestión de Estudiantes")
                
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        # Selectbox para elegir estudiante por cédula
                        opciones_estudiantes = [f"{e.get('Cédula', 'N/A')} - {e.get('Nombre', 'N/A')} {str(e.get('Apellido', '')).replace('None', '').strip()}" for e in data_est]
                        estudiante_seleccionado = st.selectbox(
                            "Seleccionar Estudiante:",
                            options=opciones_estudiantes,
                            help="Elija un estudiante para gestionar"
                        )
                    
                    with col2:
                        confirmar_accion = st.checkbox("✅ Confirmar Acción", help="Marque para habilitar los botones")
                    
                    with col3:
                        st.write("")  # Espacio vacío para alineación
                
                if estudiante_seleccionado and confirmar_accion:
                    # Extraer cédula del estudiante seleccionado
                    cedula_seleccionada = estudiante_seleccionado.split(" - ")[0]
                    
                    # Encontrar datos completos del estudiante
                    estudiante_data = next((e for e in data_est if e.get('Cédula') == cedula_seleccionada), None)
                    
                    if estudiante_data:
                        col_edit, col_delete = st.columns(2)
                        
                        with col_edit:
                            if st.button("📝 Editar Estudiante", type="primary", use_container_width=True):
                                # Guardar ID para edición
                                st.session_state.id_a_editar = cedula_seleccionada
                                st.session_state.tab_index = 3  # Cambiar a pestaña Registro Individual
                                st.rerun()
                        
                        with col_delete:
                            if st.button("🗑️ Eliminar Estudiante", type="secondary", use_container_width=True):
                                # Confirmación y eliminación
                                st.warning(f"⚠️ ¿Está seguro de eliminar al estudiante '{estudiante_data.get('Nombre', '')} {estudiante_data.get('Apellido', '')}'?")
                                col_confirm, col_cancel = st.columns(2)
                                
                                with col_confirm:
                                    if st.button("✅ Sí, Eliminar", key="confirm_eliminar_estudiante"):
                                        exito, mensaje = eliminar_estudiante(cedula_seleccionada, engine=engine_l)
                                        if exito:
                                            # Registrar auditoría
                                            registrar_auditoria(
                                                usuario=st.session_state.user_data.get('login'),
                                                rol=obtener_rol_usuario(),
                                                transaccion='DELETE',
                                                tabla_afectada='persona',
                                                registro_id=cedula_seleccionada,
                                                detalles=f"cedula:{cedula_seleccionada}, nombre:{estudiante_data.get('Nombre', '')} {estudiante_data.get('Apellido', '')}",
                                                engine=engine_l
                                            )
                                            st.success("✅ Estudiante eliminado exitosamente")
                                            st.rerun()
                                        else:
                                            st.error(f"❌ Error al eliminar: {mensaje}")
                                
                                with col_cancel:
                                    if st.button("❌ Cancelar", key="cancel_eliminar_estudiante"):
                                        st.rerun()
                else:
                    st.info("� Seleccione un estudiante y confirme la acción para habilitar los botones")
            else:
                # Estudiante solo ve datos básicos
                st.dataframe(df_est[['Cédula', 'Nombre', 'Apellido']], use_container_width=True, hide_index=True)
                mostrar_mensaje_restringido()
                
            st.caption(f"Total: {len(data_est)} estudiantes registrados.")
        else:
            st.info("No hay estudiantes registrados. Cargue un archivo CSV en la pestaña «Inscripción y Carga».")

    with t3:
        st.subheader("Seguimiento de Inscritos")
        q_list = """
            SELECT p.cedula as "Cédula", p.apellido as "Apellido", p.nombre as "Nombre",
                   p.genero as "Género", p.telefono as "Teléfono", p.carrera as "Carrera", p.semestre as "Semestre",
                   t.nombre_taller as "Formación", fc.estado as "Estatus"
            FROM public.inscripcion i
            JOIN public.persona p ON i.id_persona = p.id_persona
            JOIN public.formacion_complementaria fc ON i.id_formacion = fc.id_formacion
            JOIN public.taller t ON fc.id_taller = t.id_taller
        """
        data_list = ejecutar_query(q_list, engine=engine_l)
        if data_list:
            st.dataframe(pd.DataFrame(data_list), use_container_width=True, hide_index=True)
            st.caption(f"Total: {len(data_list)} inscripciones.")
        else:
            st.info("No hay inscripciones registradas para mostrar.")

    with t4:
        st.subheader("🎓 Digitalización Real de Expedientes")
        st.write("Asocie documentos PDF escaneados al expediente del alumno.")

        c_p1, c_p2 = st.columns(2)
        with c_p1:
            ced_pdf = st.text_input("Cédula para vincular:")
        with c_p2:
            tipo_doc = st.selectbox("Tipo de Documento:", ["Cédula", "Título", "Certificado Notas", "Otros"])

        f_pdf = st.file_uploader("Subir Archivo (Solo PDF)", type=['pdf'])

        if st.button("📤 Guardar Documento Digital"):
            if ced_pdf and f_pdf:
                # CREACIÓN FÍSICA DE CARPETAS
                base_dir = "expedientes_digitales_foc26"
                est_dir = os.path.join(base_dir, ced_pdf)

                if not os.path.exists(est_dir):
                    os.makedirs(est_dir)

                final_path = os.path.join(est_dir, f"{tipo_doc}_{f_pdf.name}")

                with open(final_path, "wb") as f:
                    f.write(f_pdf.getbuffer())

                st.success(f"✅ Archivo almacenado en: {final_path}")
            else:
                st.error("⚠️ Ingrese la cédula y cargue el archivo PDF.")

    with t5:
        st.subheader("📜 Consulta de Historial Académico")
        c_bus = st.text_input("Cédula a consultar:")
        if c_bus:
            q_h = """
                SELECT t.nombre_taller, fc.codigo_cohorte, fc.estado
                FROM public.inscripcion i
                JOIN public.persona p ON i.id_persona = p.id_persona
                JOIN public.formacion_complementaria fc ON i.id_formacion = fc.id_formacion
                JOIN public.taller t ON fc.id_taller = t.id_taller
                WHERE p.cedula = :c
            """
            res_h = ejecutar_query(q_h, {"c": c_bus}, engine_l)

    with t6:
        st.subheader("👤 Registro Individual de Estudiantes")
        st.write("Ingrese los datos del estudiante de forma manual.")
        
        # Verificar si hay datos para editar
        estudiante_editar = st.session_state.get('estudiante_editar')
        
        with st.form("form_estudiante_individual"):
            col1, col2 = st.columns(2)
            with col1:
                cedula_ind = st.text_input("Cédula*", help="Campo obligatorio", 
                                         value=estudiante_editar.get('Cédula', '') if estudiante_editar else '',
                                         disabled=bool(estudiante_editar))  # Deshabilitar cédula en edición
                nombre_ind = st.text_input("Nombre*", help="Campo obligatorio",
                                         value=estudiante_editar.get('Nombre', '') if estudiante_editar else '')
                telefono_ind = st.text_input("Teléfono",
                                         value=estudiante_editar.get('Teléfono', '') if estudiante_editar else '')
            with col2:
                apellido_ind = st.text_input("Apellido",
                                         value=estudiante_editar.get('Apellido', '') if estudiante_editar else '')
                correo_ind = st.text_input("Correo Electrónico", help="Formato: usuario@dominio.com",
                                         value=estudiante_editar.get('Correo', '') if estudiante_editar else '')
                direccion_ind = st.text_input("Dirección",
                                         value=estudiante_editar.get('Dirección', '') if estudiante_editar else '')
            
            # Campos adicionales opcionales
            col3, col4 = st.columns(2)
            with col3:
                genero_ind = st.selectbox("Género", ["", "M", "F"],
                                        index=["", "M", "F"].index(estudiante_editar.get('Género', '')) if estudiante_editar and estudiante_editar.get('Género') in ["", "M", "F"] else 0)
                carrera_ind = st.text_input("Carrera",
                                         value=estudiante_editar.get('Carrera', '') if estudiante_editar else '')
            with col4:
                semestre_ind = st.text_input("Semestre",
                                         value=estudiante_editar.get('Semestre', '') if estudiante_editar else '')
            
            btn_guardar_est = st.form_submit_button("💾 Guardar Estudiante", type="primary")
            
            if btn_guardar_est:
                # Validaciones
                if not cedula_ind.strip():
                    st.error("⚠️ La Cédula es un campo obligatorio.")
                elif not nombre_ind.strip():
                    st.error("⚠️ El Nombre es un campo obligatorio.")
                elif correo_ind and "@" not in correo_ind:
                    st.error("⚠️ El correo electrónico debe tener un formato válido (contener @).")
                else:
                    # Normalizar datos a mayúsculas
                    params_est = {
                        "cedula": cedula_ind.strip().upper(),
                        "nombre": nombre_ind.strip().upper(),
                        "apellido": apellido_ind.strip().upper() if apellido_ind else "",
                        "genero": genero_ind.strip().upper() if genero_ind else "",
                        "telefono": telefono_ind.strip() if telefono_ind else "",
                        "carrera": carrera_ind.strip().upper() if carrera_ind else "",
                        "semestre": semestre_ind.strip() if semestre_ind else ""
                    }
                    
                    # Determinar si es inserción o actualización
                    if estudiante_editar:
                        # Modo edición - actualizar estudiante existente
                        exito, mensaje = actualizar_estudiante(
                            cedula=params_est["cedula"],
                            apellido=params_est["apellido"],
                            nombre=params_est["nombre"],
                            genero=params_est["genero"],
                            telefono=params_est["telefono"],
                            carrera=params_est["carrera"],
                            semestre=params_est["semestre"],
                            engine=engine_l
                        )
                        transaccion_tipo = 'UPDATE'
                    else:
                        # Modo inserción - nuevo estudiante
                        exito, mensaje = insertar_estudiante(
                            cedula=params_est["cedula"],
                            apellido=params_est["apellido"],
                            nombre=params_est["nombre"],
                            genero=params_est["genero"],
                            telefono=params_est["telefono"],
                            carrera=params_est["carrera"],
                            semestre=params_est["semestre"],
                            engine=engine_l
                        )
                        transaccion_tipo = 'REGISTRO_MANUAL_ESTUDIANTE'
                    
                    if exito:
                        # Registrar auditoría
                        registrar_auditoria(
                            usuario=st.session_state.user_data.get('login'),
                            rol=obtener_rol_usuario(),
                            transaccion=transaccion_tipo,
                            tabla_afectada='persona',
                            registro_id=params_est["cedula"],
                            detalles=f"cedula:{params_est['cedula']}, nombre:{params_est['nombre']}, apellido:{params_est['apellido']}",
                            engine=engine_l
                        )
                        
                        # Limpiar session_state si estaba en modo edición
                        if 'estudiante_editar' in st.session_state:
                            del st.session_state.estudiante_editar
                        
                        mensaje_exito = "✅ Estudiante actualizado exitosamente" if estudiante_editar else "✅ Registro guardado exitosamente"
                        st.success(mensaje_exito)
                        st.rerun()  # Limpiar campos
                    else:
                        st.error(f"❌ Error al guardar: {mensaje}")

# --- MÓDULO D: GESTIÓN DE PROFESORES ---
elif modulo == "Gestión de Profesores":
    if es_admin():
        st.header("👨‍🏫 Gestión de Profesores")
        t1_prof, t2_prof, t3_prof = st.tabs(["📝 Carga Masiva", "📋 Listado de Profesores", "👤 Registro Individual"])
        
        # PROCESAR ACCIONES PENDIENTES AL INICIO DEL MÓDULO
        accion_pendiente = st.session_state.get('accion_pendiente')
        
        if accion_pendiente == 'editar_profesor':
            # Cambiar a pestaña de registro individual
            st.session_state.tab_prof_activa = 2
            st.session_state.accion_pendiente = None  # Limpiar acción
            
        elif accion_pendiente == 'eliminar_profesor':
            # Mostrar confirmación de eliminación
            profesor_id = st.session_state.get('profesor_id_seleccionado')
            nombre_profesor = st.session_state.get('nombre_prof_eliminar', '')
            
            if profesor_id:
                st.warning(f"⚠️ ¿Está seguro de eliminar al profesor '{nombre_profesor}'?")
                col_confirm, col_cancel = st.columns(2)
                
                with col_confirm:
                    if st.button("✅ Sí, Eliminar", key="confirm_eliminar_profesor"):
                        # Aquí iría la lógica de eliminación real
                        # Por ahora, mostrar mensaje de desarrollo
                        st.info("🗑️ Función de eliminación de profesores en desarrollo")
                        
                        # Limpiar estado
                        for key in ['accion_pendiente', 'profesor_id_seleccionado', 'nombre_prof_eliminar']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
                
                with col_cancel:
                    if st.button("❌ Cancelar", key="cancel_eliminar_profesor"):
                        # Limpiar estado
                        for key in ['accion_pendiente', 'profesor_id_seleccionado', 'nombre_prof_eliminar']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
        
        # Verificar si se debe cambiar a pestaña específica
        tab_prof_activa = st.session_state.get('tab_prof_activa', 0)
        if tab_prof_activa > 0 and tab_prof_activa < len([t1_prof, t2_prof, t3_prof]):
            # Forzar cambio de pestaña
            if tab_prof_activa == 1:
                t2_prof.write()
            elif tab_prof_activa == 2:
                t3_prof.write()
            tab_prof_activa = 0  # Resetear después de usar
            st.session_state.tab_prof_activa = 0
        
        with t1_prof:
            st.subheader("🛠️ Carga Masiva de Profesores")
            st.write("Importe la nómina de profesores encargados de los talleres.")
            f_doc = st.file_uploader("Subir archivo de profesores", type=['xlsx', 'csv'], key="up_prof_main")

            if f_doc:
                try:
                    if f_doc.name.endswith('.xlsx'):
                        df_f = pd.read_excel(f_doc)
                        # Limpiar nombres de columnas para Excel también
                        df_f.columns = df_f.columns.str.strip().str.lower()
                    else:
                        # Lectura directa con delimitador punto y coma y utf-8-sig para SICADFOC_01_Profesores.csv
                        try:
                            df_f = pd.read_csv(f_doc, sep=';', encoding='utf-8-sig')
                        except UnicodeDecodeError:
                            try:
                                df_f = pd.read_csv(f_doc, sep=';', encoding='latin-1')
                            except Exception:
                                # Fallback a detección automática
                                try:
                                    df_f = pd.read_csv(f_doc, sep=None, engine='python', encoding='utf-8-sig')
                                except Exception:
                                    df_f = pd.read_csv(f_doc, sep=None, engine='python', encoding='utf-8')
                        
                        # Limpiar nombres de columnas: eliminar espacios y estandarizar a minúsculas
                        df_f.columns = df_f.columns.str.strip().str.lower()
                        
                        # Verificar si todavía hay problema con columnas
                        if len(df_f.columns) == 1:
                            st.warning("🔍 Detectando separador automático...")
                            try:
                                df_f = pd.read_csv(f_doc, sep=None, engine='python', encoding='utf-8-sig')
                                df_f.columns = df_f.columns.str.strip().str.lower()
                            except Exception:
                                df_f = pd.read_csv(f_doc, sep=None, engine='python', encoding='utf-8')
                                df_f.columns = df_f.columns.str.strip().str.lower()
                        
                        if len(df_f.columns) == 1:
                            raise ValueError("No se detectaron múltiples columnas. Verifique el separador.")
                        
                except Exception as ex:
                    st.error(f"❌ Error al leer archivo: {ex}")
                    df_f = None
                    
                if df_f is not None and not df_f.empty:
                    df_limpio_prof, mapeo_prof = limpiar_columnas_profesores(df_f)

                    if df_limpio_prof is None:
                        st.error("⚠️ El archivo debe contener: cedula, nombre, apellido.")
                        st.write("**Columnas detectadas:**", list(df_f.columns))
                        if len(df_f.columns) > 1:
                            st.dataframe(df_f.head(3), use_container_width=True, hide_index=True)
                    else:
                        st.dataframe(df_limpio_prof, use_container_width=True, hide_index=True)

                        if st.button("🚀 Actualizar Base de Profesores"):
                            insertados = 0
                            duplicados = 0
                            errores = []
                            
                            for i, r_f in df_limpio_prof.iterrows():
                                try:
                                    # Extraer campos con valores por defecto para opcionales
                                    cedula_val = str(r_f['cedula']).strip()
                                    nombre_val = str(r_f['nombre']).strip().upper()
                                    apellido_val = str(r_f['apellido']).strip().upper()
                                    especialidad_val = str(r_f.get('especialidad', '')).strip().upper() if pd.notna(r_f.get('especialidad')) else None
                                    correo_val = str(r_f.get('correo', '')).strip().upper() if pd.notna(r_f.get('correo')) else None
                                    departamento_val = str(r_f.get('departamento', '')).strip().upper() if pd.notna(r_f.get('departamento')) else None
                                    
                                    exito, mensaje = insertar_profesor(
                                        cedula=cedula_val,
                                        nombre=nombre_val,
                                        apellido=apellido_val,
                                        especialidad=especialidad_val,
                                        correo=correo_val,
                                        departamento=departamento_val,
                                        engine=engine_l
                                    )
                                    # Registrar auditoría
                                    registrar_auditoria(
                                        usuario=st.session_state.user_data.get('login'),
                                        rol=obtener_rol_usuario(),
                                        transaccion='INSERT',
                                        tabla_afectada='profesor',
                                        registro_id=r_f['cedula'],
                                        detalles=f"cedula:{r_f['cedula']}, nombre:{r_f['nombre']}, apellido:{r_f['apellido']}",
                                        engine=engine_l
                                    )
                                    
                                    if exito:
                                        insertados += 1
                                    else:
                                        duplicados += 1
                                except Exception as e:
                                    errores.append(f"Fila {i+1}: {str(e)}")
                            
                            st.success(f"✅ Base actualizada. Insertados: {insertados}, existían: {duplicados}.")
                            if errores:
                                st.error(f"❌ {len(errores)} errores:")
                                for error in errores[:3]:
                                    st.write(f"• {error}")

        with t2_prof:
            st.subheader("📋 Listado de Profesores Registrados")
            
            # Obtener todos los profesores con campos completos
            data_prof = obtener_profesores(engine=engine_l)
            
            if data_prof:
                # Convertir a DataFrame y renombrar columnas con encabezados profesionales
                df_prof = pd.DataFrame(data_prof)
                
                # Renombrar columnas para encabezados profesionales
                df_prof.columns = ['ID', 'Cédula', 'Nombre', 'Apellido', 'Especialidad', 'Correo', 'Departamento']
                
                # Tabla de visualización limpia (sin botones)
                st.dataframe(df_prof, use_container_width=True, hide_index=True)
                st.caption(f"Total: {len(data_prof)} profesores registrados.")
                
                # Métricas
                col_m1, col_m2 = st.columns(2)
                col_m1.metric("👥 Total Profesores", len(data_prof))
                col_m2.metric("✅ Activos", len(data_prof))
                
                # Panel de Gestión Unificado
                if es_admin() and data_prof:
                    st.subheader("🔧 Panel de Gestión de Profesores")
                    
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            # Selectbox para elegir profesor por cédula
                            opciones_profesores = [f"{prof['cedula']} - {prof['nombre']} {prof['apellido']}" for prof in data_prof]
                            profesor_seleccionado = st.selectbox(
                                "Seleccionar Profesor:",
                                options=opciones_profesores,
                                help="Elija un profesor para gestionar"
                            )
                        
                        with col2:
                            confirmar_accion = st.checkbox("✅ Confirmar Acción", help="Marque para habilitar los botones")
                        
                        with col3:
                            st.write("")  # Espacio vacío para alineación
                    
                    if profesor_seleccionado and confirmar_accion:
                        # Extraer cédula del profesor seleccionado
                        cedula_seleccionada = profesor_seleccionado.split(" - ")[0]
                        
                        # Encontrar datos completos del profesor
                        profesor_data = next((prof for prof in data_prof if prof['cedula'] == cedula_seleccionada), None)
                        
                        if profesor_data:
                            col_edit, col_delete = st.columns(2)
                            

                            with col_edit:
                                if st.button("📝 Editar Profesor", type="primary", use_container_width=True):
                                    # Guardar ID para edición
                                    st.session_state.id_a_editar = cedula_seleccionada
                                    st.session_state.tab_index = 2  # Cambiar a pestaña Registro Individual
                                    st.rerun()
                            

                            with col_delete:
                                if st.button("🗑️ Eliminar Profesor", type="secondary", use_container_width=True):
                                    # Confirmación y eliminación
                                    st.warning(f"⚠️ ¿Está seguro de eliminar al profesor '{profesor_data['nombre']} {profesor_data['apellido']}'?")
                                    col_confirm, col_cancel = st.columns(2)
                                    
                                    with col_confirm:
                                        if st.button("✅ Sí, Eliminar", key="confirm_eliminar_profesor_final"):
                                            exito, mensaje = eliminar_profesor(cedula_seleccionada, engine=engine_l)
                                            if exito:
                                                # Registrar auditoría
                                                registrar_auditoria(
                                                    usuario=st.session_state.user_data.get('login'),
                                                    rol=obtener_rol_usuario(),
                                                    transaccion='DELETE',
                                                    tabla_afectada='profesor',
                                                    registro_id=cedula_seleccionada,
                                                    detalles=f"cedula:{cedula_seleccionada}, nombre:{profesor_data['nombre']} {profesor_data['apellido']}",
                                                    engine=engine_l
                                                )
                                                st.success("✅ Profesor eliminado exitosamente")
                                                st.rerun()
                                            else:
                                                st.error(f"❌ Error al eliminar: {mensaje}")
                                    
                                    with col_cancel:
                                        if st.button("❌ Cancelar", key="cancel_eliminar_profesor_final"):
                                            st.rerun()
                    else:
                        st.info("💡 Seleccione un profesor y confirme la acción para habilitar los botones")
            else:
                st.info("No hay profesores registrados. Cargue un archivo en la pestaña «Carga Masiva».")
        
        with t3_prof:
            st.subheader("👤 Registro Individual de Profesores")
            st.write("Ingrese los datos del profesor de forma manual.")
            
            # Verificar si hay datos para editar
            profesor_editar = st.session_state.get('profesor_editar')
            
            with st.form("form_profesor_individual"):
                col1, col2 = st.columns(2)
                with col1:
                    cedula_prof = st.text_input("Cédula*", help="Campo obligatorio",
                                             value=profesor_editar.get('cedula', '') if profesor_editar else '',
                                             disabled=bool(profesor_editar))  # Deshabilitar cédula en edición
                    nombre_prof = st.text_input("Nombre*", help="Campo obligatorio",
                                             value=profesor_editar.get('nombre', '') if profesor_editar else '')
                    especialidad_prof = st.text_input("Especialidad",
                                                     value=profesor_editar.get('especialidad', '') if profesor_editar else '')
                with col2:
                    apellido_prof = st.text_input("Apellido*",
                                                 value=profesor_editar.get('apellido', '') if profesor_editar else '')
                    correo_prof = st.text_input("Correo Electrónico", help="Formato: usuario@dominio.com",
                                                 value=profesor_editar.get('correo', '') if profesor_editar else '')
                    departamento_prof = st.text_input("Departamento",
                                                    value=profesor_editar.get('departamento', '') if profesor_editar else '')
                
                btn_guardar_prof = st.form_submit_button("💾 Guardar Profesor", type="primary")
                
                if btn_guardar_prof:
                    # Validaciones
                    if not cedula_prof.strip():
                        st.error("⚠️ La Cédula es un campo obligatorio.")
                    elif not nombre_prof.strip():
                        st.error("⚠️ El Nombre es un campo obligatorio.")
                    elif not apellido_prof.strip():
                        st.error("⚠️ El Apellido es un campo obligatorio.")
                    elif correo_prof and "@" not in correo_prof:
                        st.error("⚠️ El correo electrónico debe tener un formato válido (contener @).")
                    else:
                        # Normalizar datos a mayúsculas
                        params_prof = {
                            "cedula": cedula_prof.strip().upper(),
                            "nombre": nombre_prof.strip().upper(),
                            "apellido": apellido_prof.strip().upper(),
                            "especialidad": especialidad_prof.strip().upper() if especialidad_prof else "",
                            "correo": correo_prof.strip().upper() if correo_prof else "",
                            "departamento": departamento_prof.strip().upper() if departamento_prof else ""
                        }
                        
                        # Insertar profesor usando la función existente
                        exito, mensaje = insertar_profesor(
                            cedula=params_prof["cedula"],
                            nombre=params_prof["nombre"],
                            apellido=params_prof["apellido"],
                            especialidad=params_prof["especialidad"],
                            correo=params_prof["correo"],
                            departamento=params_prof["departamento"],
                            engine=engine_l
                        )
                        
                        if exito:
                            # Registrar auditoría
                            registrar_auditoria(
                                usuario=st.session_state.user_data.get('login'),
                                rol=obtener_rol_usuario(),
                                transaccion='REGISTRO_MANUAL_PROFESOR',
                                tabla_afectada='profesor',
                                registro_id=params_prof["cedula"],
                                detalles=f"cedula:{params_prof['cedula']}, nombre:{params_prof['nombre']}, apellido:{params_prof['apellido']}, especialidad:{params_prof['especialidad']}",
                                engine=engine_l
                            )
                            st.success("✅ Registro guardado exitosamente")
                            st.rerun()  # Limpiar campos
                        else:
                            st.error(f"❌ Error al guardar: {mensaje}")
    
    else:
        st.header("👨‍🏫 Gestión de Profesores")
        mostrar_mensaje_restringido()

# --- MÓDULO D: GESTIÓN DE FORMACIÓN COMPLEMENTARIA ---
elif modulo == "Gestión de Formación Complementaria":
    st.header("🎓 Gestión de Formación Complementaria")
    
    # Matriz de permisos según rol
    rol_actual = obtener_rol_usuario()
    
    # Definir columnas al inicio para evitar UnboundLocalError
    col1, col2, col3 = st.columns(3)
    
    # PROCESAR ACCIONES PENDIENTES AL INICIO DEL MÓDULO
    accion_pendiente = st.session_state.get('accion_pendiente')
    
    if accion_pendiente == 'consultar_formacion':
        # Cargar modo consulta
        st.session_state.modo_edicion = False
        st.session_state.tab_activa = 1
        st.session_state.accion_pendiente = None  # Limpiar acción
        
    elif accion_pendiente == 'editar_formacion':
        # Cargar modo edición
        st.session_state.modo_edicion = True
        st.session_state.tab_activa = 1
        st.session_state.accion_pendiente = None  # Limpiar acción
        
    elif accion_pendiente == 'eliminar_formacion':
        # Mostrar confirmación de eliminación
        formacion_id = st.session_state.get('formacion_id_seleccionada')
        nombre_formacion = st.session_state.get('nombre_formacion_eliminar', '')
        
        if formacion_id:
            st.warning(f"⚠️ ¿Está seguro de eliminar la formación '{nombre_formacion}'?")
            col_confirm, col_cancel = st.columns(2)
            
            with col_confirm:
                if st.button("✅ Sí, Eliminar", key="confirm_eliminar_formacion"):
                    exito, mensaje = eliminar_formacion(formacion_id, engine=engine_l)
                    if exito:
                        # Registrar auditoría
                        registrar_auditoria(
                            usuario=st.session_state.user_data.get('login'),
                            rol=obtener_rol_usuario(),
                            transaccion='DELETE',
                            tabla_afectada='formacion_complementaria',
                            registro_id=formacion_id,
                            detalles=f"codigo:{nombre_formacion}",
                            engine=engine_l
                        )
                        st.success("✅ Formación eliminada exitosamente")
                        st.rerun()
                    else:
                        st.error(f"❌ Error al eliminar: {mensaje}")
                        
                        # Limpiar estado
                        for key in ['accion_pendiente', 'formacion_id_seleccionada', 'nombre_formacion_eliminar']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
            
            with col_cancel:
                if st.button("❌ Cancelar", key="cancel_eliminar_formacion"):
                    # Limpiar estado
                    for key in ['accion_pendiente', 'formacion_id_seleccionada', 'nombre_formacion_eliminar']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
    
    # Verificar si se debe cambiar a pestaña específica
    tab_activa = st.session_state.get('tab_activa', 0)
    
    if rol_actual == 'admin':
        # ADMIN: Acceso total
        tabs_formacion = st.tabs(["📋 Listado", "🔧 Gestión Individual", "📤 Carga Masiva"])
        # Usar tab_activa para cambiar automáticamente
        if tab_activa > 0 and tab_activa < len(tabs_formacion):
            tabs_formacion[tab_activa].write()  # Forzar cambio de pestaña
            tab_activa = 0  # Resetear después de usar
            st.session_state.tab_activa = 0
    elif rol_actual == 'profesor':
        # PROFESOR: Crear, Consultar, Editar (no eliminar)
        tabs_formacion = st.tabs(["📋 Listado", "🔧 Gestión Individual"])
        # Usar tab_activa para cambiar automáticamente
        if tab_activa > 0 and tab_activa < len(tabs_formacion):
            tabs_formacion[tab_activa].write()  # Forzar cambio de pestaña
            tab_activa = 0  # Resetear después de usar
            st.session_state.tab_activa = 0
    else:
        # ESTUDIANTE: Consultar y Crear (solicitud)
        tabs_formacion = st.tabs(["📋 Listado", "📝 Solicitar Taller"])
    
    # --- PESTAÑA 1: LISTADO ---
    with tabs_formacion[0]:
        st.subheader("📋 Listado de Formaciones Complementarias")
        
        # Filtros de búsqueda
        with st.expander("🔍 Filtros de Búsqueda"):
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                filtro_codigo = st.text_input("Código de Formación")
            with col_f2:
                filtro_tipo = st.text_input("Tipo de Taller")
            with col_f3:
                filtro_estado = st.selectbox("Estado", ["Todos", "Activo", "Inactivo", "Finalizado"])
            
            if st.button("🔍 Aplicar Filtros"):
                st.rerun()
        
        # Obtener datos con filtros
        formaciones = listar_formaciones(
            filtro_codigo=filtro_codigo if filtro_codigo else None,
            filtro_tipo=filtro_tipo if filtro_tipo else None,
            filtro_estado=filtro_estado if filtro_estado != "Todos" else None,
            engine=engine_l
        )
        
        if formaciones:
            # Convertir a DataFrame
            df_formaciones = pd.DataFrame(formaciones)
            
            # Métricas
            if es_admin_o_profesor():
                col_m1, col_m2, col_m3 = st.columns(3)
                total_formaciones = len(formaciones)
                activas = len([f for f in formaciones if f.get('estado_registro') == 'Activo'])
                total_inscritos = sum([f.get('inscritos', 0) for f in formaciones])
                
                col_m1.metric("🎓 Total Formaciones", total_formaciones)
                col_m2.metric("✅ Activas", activas)
                col_m3.metric("👥 Total Inscritos", total_inscritos)
            
            # Tabla de visualización limpia (sin botones)
            df_vista = df_formaciones[['codigo_formacion', 'tipo_taller', 'nombre_taller', 'nombre_profesor', 'apellido_profesor', 'fecha_inicio', 'fecha_fin', 'cupos', 'inscritos', 'estado_registro']]
            df_vista.columns = ['Código', 'Tipo', 'Nombre', 'Profesor', 'Apellido', 'Inicio', 'Fin', 'Cupos', 'Inscritos', 'Estado']
            st.dataframe(df_vista, use_container_width=True, hide_index=True)
            
            # Panel de Gestión Unificado
            if rol_actual in ['admin', 'profesor']:
                st.subheader("🔧 Panel de Gestión de Formaciones")
                
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        # Selectbox para elegir formación por código
                        opciones_formaciones = [f"{f['codigo_formacion']} - {f['nombre_taller']}" for f in formaciones]
                        formacion_seleccionada = st.selectbox(
                            "Seleccionar Formación:",
                            options=opciones_formaciones,
                            help="Elija una formación para gestionar"
                        )
                    
                    with col2:
                        confirmar_accion = st.checkbox("✅ Confirmar Acción", help="Marque para habilitar los botones")
                    
                    with col3:
                        st.write("")  # Espacio vacío para alineación
                
                if formacion_seleccionada and confirmar_accion:
                    # Extraer código de la formación seleccionada
                    codigo_seleccionado = formacion_seleccionada.split(" - ")[0]
                    
                    # Encontrar datos completos de la formación
                    formacion_data = next((f for f in formaciones if f['codigo_formacion'] == codigo_seleccionado), None)
                    
                    if formacion_data:
                        col_consult, col_edit, col_delete = st.columns(3)
                        
                        with col_consult:
                            if st.button("🔍 Consultar", type="secondary", use_container_width=True):
                                # Cargar datos para consulta
                                st.session_state.formacion_editar = formacion_data
                                st.session_state.modo_edicion = False
                                st.session_state.tab_activa = 1  # Cambiar a pestaña Gestión Individual
                                st.rerun()
                        
                        with col_edit:
                            if st.button("📝 Editar", type="primary", use_container_width=True):
                                # Guardar ID para edición
                                st.session_state.id_a_editar = formacion_data['id_formacion']
                                st.session_state.tab_index = 1  # Cambiar a pestaña Gestión Individual
                                st.rerun()
                        
                        with col_delete:
                            if rol_actual == 'admin':
                                if st.button("🗑️ Eliminar", type="secondary", use_container_width=True):
                                    # Confirmación y eliminación
                                    st.warning(f"⚠️ ¿Está seguro de eliminar la formación '{formacion_data['nombre_taller']}'?")
                                    col_confirm, col_cancel = st.columns(2)
                                    
                                    with col_confirm:
                                        if st.button("✅ Sí, Eliminar", key="confirm_eliminar_formacion_final"):
                                            exito, mensaje = eliminar_formacion(formacion_data['id_formacion'], engine=engine_l)
                                            if exito:
                                                # Registrar auditoría
                                                registrar_auditoria(
                                                    usuario=st.session_state.user_data.get('login'),
                                                    rol=obtener_rol_usuario(),
                                                    transaccion='DELETE',
                                                    tabla_afectada='formacion_complementaria',
                                                    registro_id=formacion_data['id_formacion'],
                                                    detalles=f"codigo:{formacion_data['codigo_formacion']}",
                                                    engine=engine_l
                                                )
                                                st.success("✅ Formación eliminada exitosamente")
                                                st.rerun()
                                            else:
                                                st.error(f"❌ Error al eliminar: {mensaje}")
                                    
                                    with col_cancel:
                                        if st.button("❌ Cancelar", key="cancel_eliminar_formacion_final"):
                                            st.rerun()
                    else:
                        st.info("💡 Seleccione una formación y confirme la acción para habilitar los botones")
            else:
                # ESTUDIANTE: Solo vista y solicitud
                df_vista_estudiante = df_formaciones[['codigo_formacion', 'tipo_taller', 'nombre_taller', 'nombre_profesor', 'apellido_profesor', 'fecha_inicio', 'fecha_fin', 'cupos', 'inscritos', 'estado_registro']]
                df_vista_estudiante.columns = ['Código', 'Tipo', 'Nombre', 'Profesor', 'Apellido', 'Inicio', 'Fin', 'Cupos', 'Inscritos', 'Estado']
                st.dataframe(df_vista_estudiante, use_container_width=True, hide_index=True)
                
                # Botón de inscripción
                st.subheader("📝 Solicitar Inscripción a Taller")
                selected_taller = st.selectbox(
                    "Seleccionar Taller para Inscribirse:",
                    options=[f"{f['id_formacion']} - {f['codigo_formacion']} - {f['nombre_taller']}" for f in formaciones if f.get('estado_registro') == 'Activo'],
                    format_func=lambda x: x.split(" - ", 2)[2] if " - " in x else x
                )
                
                if selected_taller and st.button("📝 Solicitar Inscripción"):
                    taller_id = int(selected_taller.split(" - ")[0])
                    # Aquí iría la lógica de inscripción del estudiante
                    st.success("✅ Solicitud de inscripción enviada (pendiente de aprobación)")
        
        else:
            st.info("📋 No hay formaciones complementarias registradas.")
    
    # --- PESTAÑA 2: GESTIÓN INDIVIDUAL ---
    if len(tabs_formacion) > 1:
        with tabs_formacion[1]:
            if rol_actual in ['admin', 'profesor']:
                st.subheader("🔧 Gestión Individual de Formaciones")
                
                # Verificar si hay datos para editar/consultar
                if 'formacion_editar' in st.session_state and st.session_state.formacion_editar:
                    formacion_data = st.session_state.formacion_editar
                    modo_edicion = st.session_state.get('modo_edicion', False)
                    
                    st.write(f"**{'📝 Editando' if modo_edicion else '🔍 Consultando'}:** {formacion_data['nombre_taller']}")
                else:
                    formacion_data = None
                    modo_edicion = True  # Nuevo registro
                    st.write("**📝 Nueva Formación Complementaria**")
                
                with st.form("form_formacion_individual"):
                    # Definir columnas al inicio del formulario
                    col1, col2 = st.columns(2)
                    col3, col4 = st.columns(2)
                    
                    with col1:
                        codigo_form = st.text_input(
                            "Código de Formación*", 
                            value=formacion_data['codigo_formacion'] if formacion_data else "",
                            disabled=not modo_edicion
                        )
                        tipo_taller = st.text_input(
                            "Tipo de Taller*", 
                            value=formacion_data['tipo_taller'] if formacion_data else "",
                            disabled=not modo_edicion
                        )
                        nombre_taller = st.text_input(
                            "Nombre del Taller*", 
                            value=formacion_data['nombre_taller'] if formacion_data else "",
                            disabled=not modo_edicion
                        )
                    with col2:
                        # Obtener lista de profesores
                        profesores = ejecutar_query("SELECT id_profesor, cedula, nombre, apellido, especialidad, correo, departamento FROM public.profesor ORDER BY apellido, nombre", engine=engine_l)
                        if profesores:
                            opciones_profesores = [f"{p['cedula']} - {p['nombre']} {p['apellido']}" for p in profesores]
                            profesor_actual = f"{formacion_data['cedula_profesor']} - {formacion_data['nombre_profesor']} {formacion_data['apellido_profesor']}" if formacion_data else ""
                            profesor_sel = st.selectbox(
                                "Profesor*", 
                                options=opciones_profesores,
                                index=opciones_profesores.index(profesor_actual) if profesor_actual in opciones_profesores else 0,
                                disabled=not modo_edicion
                            )
                        else:
                            st.warning("⚠️ No hay profesores registrados. Registre profesores primero.")
                            profesor_sel = ""
                        
                        cupos = st.number_input(
                            "Cupos", 
                            min_value=1, 
                            max_value=100, 
                            value=formacion_data.get('cupos', 30) if formacion_data else 30,
                            disabled=not modo_edicion
                        )
                        estado_reg = st.selectbox(
                            "Estado de Registro", 
                            ["Activo", "Inactivo", "Finalizado"],
                            index=["Activo", "Inactivo", "Finalizado"].index(formacion_data['estado_registro']) if formacion_data else 0,
                            disabled=not modo_edicion
                        )
                    
                    with col3:
                        fecha_inicio = st.date_input(
                            "Fecha de Inicio*", 
                            value=pd.to_datetime(formacion_data['fecha_inicio']).date() if formacion_data else datetime.now().date(),
                            disabled=not modo_edicion
                        )
                    with col4:
                        fecha_fin = st.date_input(
                            "Fecha de Fin*", 
                            value=pd.to_datetime(formacion_data['fecha_fin']).date() if formacion_data else datetime.now().date(),
                            disabled=not modo_edicion
                        )
                    
                    observaciones = st.text_area(
                        "Observaciones", 
                        value=formacion_data.get('observaciones', '') if formacion_data else "",
                        disabled=not modo_edicion
                    )
                    
                    # Botones según modo
                    if modo_edicion:
                        btn_guardar = st.form_submit_button("💾 Guardar Formación", type="primary")
                    else:
                        btn_volver = st.form_submit_button("🔙 Volver a Edición")
                    
                    if modo_edicion and btn_guardar:
                        # Validaciones
                        if not codigo_form.strip() or not tipo_taller.strip() or not nombre_taller.strip():
                            st.error("⚠️ Complete los campos obligatorios: Código, Tipo y Nombre del Taller")
                        elif not profesor_sel:
                            st.error("⚠️ Seleccione un profesor")
                        elif fecha_fin < fecha_inicio:
                            st.error("⚠️ La fecha de fin debe ser posterior a la fecha de inicio")
                        else:
                            # Extraer cédula del profesor seleccionado
                            cedula_profesor = profesor_sel.split(" - ")[0]
                            
                            # Insertar o actualizar formación
                            exito, resultado = insertar_formacion(
                                codigo_formacion=codigo_form.strip(),
                                tipo_taller=tipo_taller.strip(),
                                nombre_taller=nombre_taller.strip(),
                                cedula_profesor=cedula_profesor,
                                fecha_inicio=fecha_inicio,
                                fecha_fin=fecha_fin,
                                cupos=cupos,
                                estado_registro=estado_reg,
                                observaciones=observaciones.strip() if observaciones else None,
                                engine=engine_l
                            )
                            
                            if exito:
                                # Registrar auditoría
                                accion = 'UPDATE' if formacion_data else 'INSERT'
                                registrar_auditoria(
                                    usuario=st.session_state.user_data.get('login'),
                                    rol=obtener_rol_usuario(),
                                    transaccion=accion,
                                    tabla_afectada='formacion_complementaria',
                                    registro_id=resultado,
                                    detalles=f"codigo:{codigo_form}, nombre:{nombre_taller}, profesor:{cedula_profesor}",
                                    engine=engine_l
                                )
                                st.success("✅ Formación guardada exitosamente")
                                # Limpiar sesión
                                if 'formacion_editar' in st.session_state:
                                    del st.session_state.formacion_editar
                                if 'modo_edicion' in st.session_state:
                                    del st.session_state.modo_edicion
                                st.rerun()
                            else:
                                st.error(f"❌ Error al guardar: {resultado}")
                    
                    elif not modo_edicion and btn_volver:
                        # Volver al modo edición
                        st.session_state.modo_edicion = True
                        st.rerun()
            
            elif rol_actual == 'estudiante':
                st.subheader("📝 Solicitar Taller")
                st.write("Complete el formulario para solicitar su inscripción en un taller.")
                
                # Obtener formaciones activas
                formaciones_activas = listar_formaciones(filtro_estado='Activo', engine=engine_l)
                
                if formaciones_activas:
                    with st.form("form_solicitud_taller"):
                        # Selección de taller
                        opciones_talleres = [f"{f['id_formacion']} - {f['codigo_formacion']} - {f['nombre_taller']}" for f in formaciones_activas]
                        taller_sel = st.selectbox("Seleccione el Taller*", options=opciones_talleres)
                        
                        observaciones_solicitud = st.text_area("Observaciones (opcional)")
                        
                        btn_solicitar = st.form_submit_button("📝 Enviar Solicitud", type="primary")
                        
                        if btn_solicitar:
                            taller_id = int(taller_sel.split(" - ")[0])
                            # Aquí iría la lógica de inscripción
                            st.success("✅ Solicitud enviada correctamente. Pendiente de aprobación.")
                else:
                    st.info("📋 No hay talleres activos disponibles para inscripción.")
    
    # --- PESTAÑA 3: CARGA MASIVA (solo admin) ---
    if len(tabs_formacion) > 2 and rol_actual == 'admin':
        with tabs_formacion[2]:
            st.subheader("📤 Carga Masiva de Formaciones")
            st.write("Importe formaciones complementarias desde archivo CSV/Excel")
            
            file_formaciones = st.file_uploader("Subir archivo de formaciones", type=['xlsx', 'csv'])
            
            if file_formaciones:
                try:
                    if file_formaciones.name.endswith('.xlsx'):
                        df_form = pd.read_excel(file_formaciones)
                    else:
                        df_form = pd.read_csv(file_formaciones, encoding='utf-8-sig')
                    
                    # Validar columnas requeridas
                    columnas_requeridas = ['codigo_formacion', 'tipo_taller', 'nombre_taller', 'cedula_profesor', 'fecha_inicio', 'fecha_fin']
                    columnas_faltantes = [col for col in columnas_requeridas if col not in df_form.columns]
                    
                    if columnas_faltantes:
                        st.error(f"⚠️ Columnas faltantes: {', '.join(columnas_faltantes)}")
                        st.info("💡 Columnas requeridas: " + ", ".join(columnas_requeridas))
                    else:
                        st.dataframe(df_form.head(), use_container_width=True, hide_index=True)
                        
                        if st.button("🚀 Procesar Carga Masiva"):
                            procesados = 0
                            errores = []
                            
                            for i, row in df_form.iterrows():
                                try:
                                    exito, resultado = insertar_formacion(
                                        codigo_formacion=str(row['codigo_formacion']),
                                        tipo_taller=str(row['tipo_taller']),
                                        nombre_taller=str(row['nombre_taller']),
                                        cedula_profesor=str(row['cedula_profesor']),
                                        fecha_inicio=pd.to_datetime(row['fecha_inicio']).date(),
                                        fecha_fin=pd.to_datetime(row['fecha_fin']).date(),
                                        cupos=int(row.get('cupos', 30)),
                                        estado_registro=str(row.get('estado_registro', 'Activo')),
                                        observaciones=str(row.get('observaciones', '')) if pd.notna(row.get('observaciones')) else None,
                                        engine=engine_l
                                    )
                                    
                                    if exito:
                                        procesados += 1
                                    else:
                                        errores.append(f"Fila {i+1}: {resultado}")
                                except Exception as e:
                                    errores.append(f"Fila {i+1}: {str(e)}")
                            
                            st.success(f"✅ {procesados} formaciones procesadas exitosamente")
                            if errores:
                                st.error(f"❌ {len(errores)} errores encontrados")
                                with st.expander("Ver errores"):
                                    for error in errores[:10]:
                                        st.write(f"• {error}")
                
                except Exception as e:
                    st.error(f"❌ Error al procesar archivo: {str(e)}")

# --- MÓDULO E: REPORTES ---
elif modulo == "Reportes":
    if es_admin_o_profesor():
        st.header("📊 Reportes del Sistema")
        tabs_reportes = st.tabs(["👥 Usuarios", "🎓 Estudiantes", "👨‍🏫 Profesores", "🔍 Log de Transacciones"])
        
        with tabs_reportes[0]:
            st.subheader("👥 Reporte de Usuarios del Sistema")
            q_usuarios = """
                SELECT login, email, rol, activo, 
                       CASE WHEN activo THEN 'Sí' ELSE 'No' END as estado
                FROM public.usuario 
                ORDER BY rol, login
            """
            data_usuarios = ejecutar_query(q_usuarios, engine=engine_l)
            
            if data_usuarios:
                df_usuarios = pd.DataFrame(data_usuarios)
                st.dataframe(df_usuarios, use_container_width=True, hide_index=True)
                
                # Métricas
                col_m1, col_m2, col_m3 = st.columns(3)
                total_usuarios = len(data_usuarios)
                usuarios_activos = len([u for u in data_usuarios if u.get('activo')])
                admins = len([u for u in data_usuarios if u.get('rol') == 'admin'])
                
                col_m1.metric("👥 Total Usuarios", total_usuarios)
                col_m2.metric("✅ Activos", usuarios_activos)
                col_m3.metric("🔑 Administradores", admins)
            else:
                st.info("No hay usuarios registrados en el sistema.")
        
        with tabs_reportes[1]:
            st.subheader("🎓 Reporte de Estudiantes")
            q_estudiantes_reporte = """
                SELECT cedula as "Cédula", apellido as "Apellido", nombre as "Nombre",
                       genero as "Género", telefono as "Teléfono", carrera as "Carrera", semestre as "Semestre"
                FROM public.persona 
                WHERE cedula IS NOT NULL AND nombre IS NOT NULL
                ORDER BY apellido, nombre
            """
            data_estudiantes_reporte = ejecutar_query(q_estudiantes_reporte, engine=engine_l)
            
            if data_estudiantes_reporte:
                df_est_rep = pd.DataFrame(data_estudiantes_reporte)
                st.dataframe(df_est_rep, use_container_width=True, hide_index=True)
                
                # Métricas
                col_m1, col_m2, col_m3 = st.columns(3)
                total_est = len(data_estudiantes_reporte)
                
                # Conteo mejorado de género (insensible a mayúsculas y múltiples formatos)
                masculino = 0
                femenino = 0
                no_definido = 0
                
                for est in data_estudiantes_reporte:
                    gen = str(est.get('Género', '')).strip().upper()
                    if gen in ['M', 'MASCULINO', 'MALE']:
                        masculino += 1
                    elif gen in ['F', 'FEMENINO', 'FEMALE']:
                        femenino += 1
                    else:
                        no_definido += 1
                
                col_m1.metric("🎓 Total Estudiantes", total_est)
                col_m2.metric("♂️ Masculino", masculino)
                col_m3.metric("♀️ Femenino", femenino)
                
                # Mostrar adicionalmente los no definidos si existen
                if no_definido > 0:
                    st.caption(f"📊 Género no definido: {no_definido} estudiante(s)")
            else:
                st.info("No hay estudiantes registrados.")
        
        with tabs_reportes[2]:
            st.subheader("👨‍🏫 Reporte de Profesores")
            q_profesores_reporte = """
                SELECT id_profesor as "ID", cedula as "Cédula", nombre as "Nombre", apellido as "Apellido", 
                       especialidad as "Especialidad", correo as "Correo", departamento as "Departamento"
                FROM public.profesor 
                ORDER BY apellido, nombre
            """
            data_profesores_reporte = ejecutar_query(q_profesores_reporte, engine=engine_l)
            
            if data_profesores_reporte:
                df_prof_rep = pd.DataFrame(data_profesores_reporte)
                st.dataframe(df_prof_rep, use_container_width=True, hide_index=True)
                
                # Métricas
                col_m1, col_m2 = st.columns(2)
                total_prof = len(data_profesores_reporte)
                col_m1.metric("👨‍🏫 Total Profesores", total_prof)
                col_m2.metric("✅ Disponibles", total_prof)
            else:
                st.info("No hay profesores registrados.")
        
        with tabs_reportes[3]:
            st.subheader("🔍 Log de Transacciones (Auditoría)")
            
            # Filtros de auditoría
            with st.expander("🔍 Filtros de Búsqueda"):
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    filtro_usuario = st.text_input("Usuario")
                    filtro_rol = st.selectbox("Rol", ["Todos", "admin", "profesor", "estudiante"])
                with col_f2:
                    filtro_accion = st.selectbox("Acción", ["Todas", "INSERT", "UPDATE", "DELETE", "LOGIN", "REGISTRO_MANUAL_ESTUDIANTE", "REGISTRO_MANUAL_PROFESOR"])
                    filtro_fecha_inicio = st.date_input("Desde", datetime.now().replace(day=1))
                with col_f3:
                    filtro_fecha_fin = st.date_input("Hasta", datetime.now())
                
                if st.button("🔍 Aplicar Filtros", key="filtros_reportes"):
                    st.rerun()
            
            # Obtener datos de auditoría
            datos_auditoria_reportes = obtener_auditoria(
                filtro_usuario=filtro_usuario if filtro_usuario else None,
                filtro_rol=filtro_rol if filtro_rol != "Todos" else None,
                filtro_transaccion=filtro_accion if filtro_accion != "Todas" else None,
                fecha_inicio=filtro_fecha_inicio,
                fecha_fin=filtro_fecha_fin,
                engine=engine_l
            )
            
            if datos_auditoria_reportes:
                df_audit = pd.DataFrame(datos_auditoria_reportes)
                st.dataframe(df_audit, use_container_width=True, hide_index=True)
                st.caption(f"Total: {len(datos_auditoria_reportes)} registros de auditoría.")
                
                # Métricas de auditoría
                col_m1, col_m2, col_m3 = st.columns(3)
                transacciones_hoy = len([a for a in datos_auditoria_reportes if a.get('fecha', '').date() == datetime.now().date()])
                por_tipo = {}
                for a in datos_auditoria_reportes:
                    tipo = a.get('transaccion', 'OTRO')
                    por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
                
                col_m1.metric("📊 Total Logs", len(datos_auditoria_reportes))
                col_m2.metric("📅 Hoy", transacciones_hoy)
                col_m3.metric("🔄 INSERT/UPDATE", por_tipo.get('INSERT', 0) + por_tipo.get('UPDATE', 0))
            else:
                st.info("No se encontraron registros de auditoría con los filtros seleccionados.")
    
    else:
        st.header("📊 Reportes")
        mostrar_mensaje_restringido()

# --- MÓDULO F: CONFIGURACIÓN ---
elif modulo == "Configuración":
    if es_admin() and st.session_state.user_data.get('login') == 'angelher@gmail.com':
        st.header(" Configuración del Sistema")
        st.write("Parámetros del servidor de correo electrónico")
        
        # Obtener configuración actual
        config_actual = obtener_config_correo(engine_l)
        if config_actual is None:
            config_actual = {}
        
        with st.form("config_form"):
            st.subheader(" Configuración SMTP")
            
            col1, col2 = st.columns(2)
            with col1:
                smtp_server = st.text_input("Servidor SMTP", value=config_actual.get('servidor', ''))
                smtp_port = st.text_input("Puerto", value=config_actual.get('puerto', '587'))
                smtp_user = st.text_input("Usuario SMTP", value=config_actual.get('usuario', ''))
            with col2:
                smtp_password = st.text_input("Contraseña SMTP", value=config_actual.get('contrasena', ''), type="password")
                smtp_use_tls = st.checkbox("Usar TLS", value=config_actual.get('usar_tls', True))
            
            btn_guardar_config = st.form_submit_button("💾 Guardar Configuración", type="primary")
            
            if btn_guardar_config:
                if smtp_server and smtp_port and smtp_user:
                    # Guardar configuración
                    exito = guardar_config_correo(
                        servidor=smtp_server,
                        puerto=smtp_port,
                        usuario=smtp_user,
                        contrasena=smtp_password,
                        usar_tls=smtp_use_tls,
                        engine=engine_l
                    )
                    
                    if exito:
                        # Registrar auditoría
                        registrar_auditoria(
                            usuario=st.session_state.user_data.get('login'),
                            rol=obtener_rol_usuario(),
                            transaccion='UPDATE',
                            tabla_afectada='config_correo',
                            detalles=f"servidor:{smtp_server}, puerto:{smtp_port}, usuario:{smtp_user}",
                            engine=engine_l
                        )
                        st.success("✅ Configuración guardada exitosamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al guardar la configuración")
                else:
                    st.error("⚠️ Complete los campos obligatorios: Servidor, Puerto y Usuario")
        
        # Sección de sincronización (solo en entorno local)
        st.divider()
        st.subheader("🔄 Sincronización de Datos")
        
        # Verificar si estamos en entorno local
        if verificar_entorno_local():
            st.write("📍 Entorno detectado: **Local**")
            st.info("💡 Esta función permite sincronizar la base de datos local con la nube (Render).")
            
            # Mostrar información de conexión actual
            conn_info = get_connection_info()
            st.write(f"🔗 Conexión actual: {conn_info['host']}:{conn_info['port']}/{conn_info['database']}")
            
            # Botón de sincronización
            if st.button("🚀 Sincronizar Base de Datos Local con la Nube", type="primary", use_container_width=True):
                with st.spinner("🔄 Sincronizando datos con la nube..."):
                    try:
                        exito, mensaje = migrar_datos_a_nube()
                        
                        if exito:
                            st.success("✅ Datos sincronizados exitosamente")
                            st.info(mensaje)
                        else:
                            st.error("❌ Error en la sincronización")
                            st.error(mensaje)
                            
                    except Exception as e:
                        st.error(f"❌ Error de conexión: {str(e)}")
                        st.warning("💡 Verifique su conexión a internet y la configuración de RENDER_DATABASE_URL")
            
            # Información adicional
            with st.expander("📋 Información de Configuración"):
                st.write("""
                **Para usar la sincronización:**
                
                1. Configure la variable de entorno `RENDER_DATABASE_URL` con la URL de su base de datos en Render
                2. Asegúrese de tener conexión a internet
                3. Presione el botón de sincronización
                
                **Formato de RENDER_DATABASE_URL:**
                ```
                RENDER_DATABASE_URL=postgresql://usuario:password@host:puerto/database?sslmode=require
                ```
                
                **Tablas que se sincronizarán:**
                - persona (estudiantes)
                - profesor (profesores)
                - formacion_complementaria (formaciones)
                - inscripcion_taller (inscripciones)
                - auditoria (registros)
                - config_correo (configuración)
                """)
        else:
            st.write("📍 Entorno detectado: **Nube (Render)**")
            st.info("ℹ️ La sincronización solo está disponible en entorno local.")
            st.warning("⚠️ Esta función no se puede ejecutar en la nube por seguridad.")
    
    else:
        st.header("⚙️ Configuración")
        st.error("🔒 Esta sección está disponible únicamente para el administrador principal (angelher@gmail.com)")
        mostrar_mensaje_restringido()
