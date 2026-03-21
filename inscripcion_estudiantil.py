import streamlit as st
import pandas as pd
import os
from datetime import datetime
from database import ejecutar_query, get_connection_local, get_metricas_dashboard

# =================================================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO VISUAL (CSS)
# =================================================================
st.set_page_config(
    page_title="SICADFOC - IUJO",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded"
)

# Inyección de CSS: Botones grises (#6c757d) para Ingresar y Cerrar Sesión
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #003366;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00509e;
        border: 1px solid #ffffff;
    }
    /* BOTÓN INGRESAR y CERRAR SESIÓN - Gris #6c757d */
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
    .sidebar .sidebar-content {
        background-image: linear-gradient(#2e7bcf, #2e7bcf);
        color: white;
    }
    .metric-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    div.stDataFrame {
        border: 1px solid #003366;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 2. MANEJO DE ESTADO DE SESIÓN (SESSION STATE)
# =================================================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "menu_actual" not in st.session_state:
    st.session_state.menu_actual = "Inicio"
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "intentos_login" not in st.session_state:
    st.session_state.intentos_login = 0

engine_local = get_connection_local()

# =================================================================
# 3. MÓDULO DE AUTENTICACIÓN (LOGIN)
# =================================================================
if not st.session_state.autenticado:
    _, col_login, _ = st.columns([1, 2, 1])

    with col_login:
        st.write("#")
        if os.path.exists("iujo-logo.png"):
            st.image("iujo-logo.png", use_container_width=True)

        with st.container():
            st.markdown("<h2 style='text-align: center; color: #003366;'>SICADFOC</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center;'>Sistema de Control de Administración de Formación Complementaria</p>", unsafe_allow_html=True)

            with st.form("formulario_acceso"):
                usuario_input = st.text_input("Usuario del Sistema", key="user")
                clave_input = st.text_input("Contraseña", type="password", key="pass")

                boton_acceso = st.form_submit_button("INGRESAR")

                if boton_acceso:
                    if usuario_input and clave_input:
                        try:
                            sql_login = "SELECT * FROM public.usuario WHERE login=:u AND contrasena=:p"
                            resultado = ejecutar_query(
                                sql_login,
                                {"u": usuario_input, "p": clave_input},
                                engine=engine_local
                            )

                            if resultado:
                                st.session_state.autenticado = True
                                st.session_state.user_data = resultado[0]
                                st.session_state.intentos_login = 0
                                st.success("✅ Acceso exitoso. Bienvenido(a).")
                                st.rerun()
                            else:
                                st.session_state.intentos_login += 1
                                st.error(f"❌ Credenciales incorrectas (Intento {st.session_state.intentos_login})")
                        except Exception as e:
                            st.error(f"⚠️ Error de conexión a la Base de Datos: {e}")
                    else:
                        st.warning("⚠️ Por favor complete ambos campos para continuar.")
    st.stop()

# =================================================================
# 4. BARRA LATERAL DE NAVEGACIÓN (SIDEBAR)
# =================================================================
with st.sidebar:
    st.image("iujo-logo.png", width=160) if os.path.exists("iujo-logo.png") else st.title("SICADFOC")

    st.markdown(f"### 👤 {st.session_state.user_data['login']}")
    st.info(f"Nivel: Administrador")
    st.markdown("---")

    if st.button("🏠 Inicio", use_container_width=True):
        st.session_state.menu_actual = "Inicio"

    if st.button("📝 Gestión Estudiantil", use_container_width=True):
        st.session_state.menu_actual = "Inscripción"

    if st.button("📊 Reportes y Consultas", use_container_width=True):
        st.session_state.menu_actual = "Reportes"

    if st.button("⚙️ Configuración", use_container_width=True):
        st.session_state.menu_actual = "Config"

    st.markdown("---")
    if st.button("🚪 Finalizar Sesión"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# =================================================================
# 5. DESARROLLO DEL CONTENIDO PRINCIPAL
# =================================================================

# --- MÓDULO: INICIO ---
if st.session_state.menu_actual == "Inicio":
    st.title("🚀 (Sistema de Control de Administración de Formación Complementaria) SICADFOC")
    st.markdown("---")

    st.write(f"### ¡Bienvenidos, **{st.session_state.user_data['login']}**!")
    st.markdown("""
        Bienvenido al entorno de gestión académica del **Instituto Universitario Jesús Obrero (IUJO)**.
        Este sistema permite centralizar la información de los talleres y la formación complementaria de los estudiantes.
    """)

    # Métricas usando database.py
    metricas = get_metricas_dashboard(engine_local)
    col_inf1, col_inf2, col_inf3 = st.columns(3)
    with col_inf1:
        st.metric(label="Talleres Activos", value=metricas['talleres'])
    with col_inf2:
        st.metric(label="Estudiantes Registrados", value=metricas['estudiantes'])
    with col_inf3:
        st.metric(label="Profesores", value=metricas['profesores'])

    st.success("✅ Sistema listo para procesar solicitudes. Seleccione un módulo en el menú lateral.")

# --- MÓDULO: INSCRIPCIÓN (GESTIÓN ESTUDIANTIL) ---
elif st.session_state.menu_actual == "Inscripción":
    def app():
        st.header("📝 Gestión de Inscripciones")
        st.write("Módulo de inscripción estudiantil. Utilice el menú principal (main.py) para la gestión completa.")
        st.info("Para cargar estudiantes y gestionar matrícula, ejecute: streamlit run main.py")

    app()

# --- MÓDULO: REPORTES Y CONSULTAS ---
elif st.session_state.menu_actual == "Reportes":
    st.header("📊 Centro de Reportes y Consultas")
    st.write("Visualización de datos maestros del sistema.")

    tab_personal, tab_formaciones, tab_stats = st.tabs(["👥 Personal", "📚 Formaciones", "📈 Estadísticas"])

    with tab_personal:
        st.subheader("Personal Administrativo y Usuarios")
        query_usuarios = """
            SELECT p.cedula as "Cédula", p.nombre as "Nombre", p.apellido as "Apellido", u.login as "Usuario"
            FROM public.usuario u
            JOIN public.persona p ON u.id_persona = p.id_persona
            ORDER BY p.apellido ASC
        """
        try:
            datos_u = ejecutar_query(query_usuarios, engine=engine_local)
            if datos_u:
                st.dataframe(pd.DataFrame(datos_u), use_container_width=True, hide_index=True)
            else:
                st.info("No hay registros de usuarios para mostrar.")
        except Exception as e:
            st.error(f"Error al consultar usuarios: {e}")

    with tab_formaciones:
        st.subheader("Histórico de Talleres y Cohortes")
        query_formaciones = """
            SELECT fc.codigo_cohorte as "Cohorte", t.nombre_taller as "Taller",
                   p.nombre || ' ' || p.apellido as "Profesor",
                   fc.fecha_inicio as "Fecha de Inicio", fc.estado as "Estatus"
            FROM public.formacion_complementaria fc
            JOIN public.taller t ON fc.id_taller = t.id_taller
            JOIN public.persona p ON fc.id_profesor_encargado = p.id_persona
            ORDER BY fc.id_formacion DESC
        """
        try:
            datos_f = ejecutar_query(query_formaciones, engine=engine_local)
            if datos_f:
                st.dataframe(pd.DataFrame(datos_f), use_container_width=True, hide_index=True)
            else:
                st.info("No se registran formaciones activas.")
        except Exception as e:
            st.error(f"Error al consultar formaciones: {e}")

    with tab_stats:
        st.subheader("Resumen General")
        st.write("Módulo de analítica visual en desarrollo.")
        st.info("Aquí se mostrarán los gráficos de barras y pasteles sobre la participación estudiantil.")

# --- MÓDULO: CONFIGURACIÓN (PLACEHOLDER) ---
elif st.session_state.menu_actual == "Config":
    st.title("⚙️ Configuración y Parámetros")
    st.markdown("---")
    st.write("Módulo reservado para la gestión de variables de entorno y mantenimiento de la base de datos.")
    if st.checkbox("Ver detalles técnicos de conexión"):
        st.code("Host: localhost | Port: 5432 | DB: FOC26")
