import streamlit as st
import pandas as pd
import os
import io
import shutil
from datetime import datetime
from sqlalchemy import create_engine, text
import database
from database import ejecutar_query, crear_tablas_sistema, crear_usuario_prueba, obtener_logs_sistema
from database import engine, get_engine_local, get_engine_espejo, configurar_correo_final, probar_envio_correo
import re
import hashlib

# =================================================================
# 1. CONFIGURACIÓN DE CSS Y TEMAS
# =================================================================

def detectar_base_datos_conectada():
    """Detecta qué base de datos está conectada"""
    try:
        engine_espejo = get_engine_espejo()
        engine_local = get_engine_local()
        
        if engine_espejo and 'render.com' in str(engine_espejo.url):
            return 'nube_render'
        elif engine_local and 'foc26_limpio.db' in str(engine_local.url):
            return 'desarrollo'
        elif engine_espejo and 'Foc26_espejo.db' in str(engine_espejo.url):
            return 'produccion_local'
        else:
            return 'desconocido'
    except:
        return 'desconocido'

def configurar_tema_segun_ambiente(tipo_ambiente):
    """Configura el tema CSS según el ambiente detectado"""
    if tipo_ambiente == 'nube_render':
        # Tema claro para nube
        st.markdown("""
        <style>
        .stApp {
            background: #ffffff;
            color: #1e293b;
        }
        .main .block-container {
            background: #ffffff;
            color: #1e293b;
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        .stButton>button {
            background-color: #3b82f6;
            color: white;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
        }
        .stButton>button:hover {
            background-color: #2563eb;
            color: white;
        }
        .stRadio>div>label {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            padding: 0.5rem;
            border-radius: 8px;
            margin: 0.25rem 0;
            color: #1e293b;
        }
        .stRadio>div>label:hover {
            background: #e2e8f0;
            color: #1e293b;
        }
        .sidebar .sidebar-content {
            background: #f8fafc;
            color: #1e293b;
        }
        </style>
        """, unsafe_allow_html=True)
    elif tipo_ambiente == 'produccion_local':
        # Tema claro para producción local
        st.markdown("""
        <style>
        .stApp {
            background: #f8fafc;
            color: #1e293b;
        }
        .main .block-container {
            background: #ffffff;
            color: #1e293b;
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .stButton>button {
            background-color: #10b981;
            color: white;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
        }
        .stButton>button:hover {
            background-color: #059669;
            color: white;
        }
        .stRadio>div>label {
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
            padding: 0.5rem;
            border-radius: 8px;
            margin: 0.25rem 0;
            color: #1e293b;
        }
        .stRadio>div>label:hover {
            background: #e2e8f0;
            color: #1e293b;
        }
        .sidebar .sidebar-content {
            background: #f1f5f9;
            color: #1e293b;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Tema oscuro para desarrollo
        st.markdown("""
        <style>
        .stApp {
            background: #0f172a;
            color: #f8fafc;
        }
        .main .block-container {
            background: #1e293b;
            color: #f8fafc;
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        }
        .stButton>button {
            background-color: #3b82f6;
            color: white;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
        }
        .stButton>button:hover {
            background-color: #2563eb;
            color: white;
        }
        .stRadio>div>label {
            background: #334155;
            border: 1px solid #475569;
            padding: 0.5rem;
            border-radius: 8px;
            margin: 0.25rem 0;
            color: #f8fafc;
        }
        .stRadio>div>label:hover {
            background: #475569;
            color: #f8fafc;
        }
        .sidebar .sidebar-content {
            background: #1e293b;
            color: #f8fafc;
        }
        </style>
        """, unsafe_allow_html=True)

def get_module_icons():
    """Retorna los iconos para los módulos"""
    return {
        'Inicio': '🏠',
        'Gestión Estudiantil': '📚',
        'Gestión de Profesores': '👨‍🏫',
        'Gestión de Formación Complementaria': '🎓',
        'Configuración': '⚙️',
        'Reportes': '📊',
        'Monitor de Sistema': '⚡',
        '⚙️ Gestión de Ambientes (ITIL)': '🔧'
    }

def mostrar_aviso_ambiente(tipo_ambiente):
    """Muestra un aviso en el sidebar según el ambiente"""
    if tipo_ambiente == 'desarrollo':
        st.sidebar.error("🔧 ENTORNO: DESARROLLO")
        st.sidebar.info("Base de datos: foc26_limpio.db")
    elif tipo_ambiente == 'produccion_local':
        st.sidebar.success("🚀 ENTORNO: PRODUCCIÓN (LOCAL)")
        st.sidebar.info("Base de datos: Foc26_espejo.db")
    elif tipo_ambiente == 'nube_render':
        st.sidebar.success("☁️ ENTORNO: NUBE (RENDER)")
        st.sidebar.info("Base de datos: PostgreSQL")
    else:
        st.sidebar.warning("⚠️ ENTORNO: DESCONOCIDO")

# Detectar ambiente y configurar tema
tipo_ambiente = detectar_base_datos_conectada()
configurar_tema_segun_ambiente(tipo_ambiente)

# =================================================================
# 2. SISTEMA DE ROLES Y PERFILES
# =================================================================

def obtener_rol_usuario():
    """Obtiene el rol del usuario desde st.session_state"""
    return st.session_state.get('rol', 'estudiante')

def registrar_auditoria_sistema(usuario, transaccion, tabla_afectada=None, detalles_adicionales=None):
    """Función auxiliar para registrar auditoría"""
    from database import registrar_auditoria
    rol_actual = obtener_rol_usuario()
    ip_address = st.context.headers.get('x-forwarded-for', 'localhost')
    
    detalles = f"Transacción: {transaccion}"
    if tabla_afectada:
        detalles += f", Tabla: {tabla_afectada}"
    if detalles_adicionales:
        detalles += f", Detalles: {detalles_adicionales}"
    detalles += f", Rol: {rol_actual}, IP: {ip_address}"
    
    registrar_auditoria(
        accion=transaccion,
        usuario=usuario,
        detalles=detalles
    )

def es_admin():
    """Verifica si el usuario es administrador"""
    rol = obtener_rol_usuario()
    return rol == 'admin' or rol == 'administrador'

def es_profesor():
    """Verifica si el usuario es profesor"""
    rol = obtener_rol_usuario()
    return rol == 'profesor'

def es_estudiante():
    """Verifica si el usuario es estudiante"""
    rol = obtener_rol_usuario()
    return rol == 'estudiante'

def mostrar_mensaje_restringido():
    """Muestra mensaje de acceso restringido"""
    st.warning("🔒 Esta función está disponible solo para administradores.")
    st.info("Contacte al administrador del sistema.")

# =================================================================
# 3. INTERFAZ DE LOGIN
# =================================================================

if not st.session_state.get('autenticado', False):
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; min-height: 80vh;">
        <div style="background: linear-gradient(135deg, #1E293B 0%, #334155 100%); 
                    padding: 3rem; border-radius: 20px; 
                    border: 1px solid #334155; 
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
                    width: 100%; max-width: 500px;">
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🎓</div>
                <h1 style="color: #F8FAFC; font-weight: 700; margin-bottom: 0.5rem;">
                    SICADFOC 2026
                </h1>
                <p style="color: #CBD5E1; font-size: 1rem; margin-bottom: 0;">
                    Sistema Integral de Control Académico y Docente
                </p>
                <div style="color: #38BDF8; font-size: 0.9rem; font-weight: 500;">
                    Instituto Universitario Jesús Obrero
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        st.markdown("""
        <div style="background: #1E293B; padding: 2rem; border-radius: 15px; 
                    border: 1px solid #334155; margin-top: -2rem;">
            <h3 style="color: #F8FAFC; text-align: center; margin-bottom: 1.5rem;">
                🔐 INICIAR SESIÓN
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            u = st.text_input(
                "📧 Correo Institucional", 
                placeholder="usuario@iujo.edu.ve",
                help="Ingrese su correo institucional"
            )
        with col2:
            p = st.text_input(
                "🔑 Cédula (Contraseña)", 
                type="password",
                placeholder="V-XXXXXXX",
                help="Ingrese su número de cédula"
            )
        
        _, col_center, _ = st.columns([1, 2, 1])
        with col_center:
            btn_login = st.form_submit_button(
                "🚀 INGRESAR AL SISTEMA", 
                type="primary",
                use_container_width=True
            )

        if btn_login:
            if not u or not p:
                st.error("❌ Por favor, ingrese su correo y cédula")
                st.stop()
            
            # FORZADO: Cédula 14300385 - Acceso directo como administrador
            if p.strip() == "14300385":
                # Limpiar session state y forzar rol
                st.session_state.clear()
                st.session_state.autenticado = True
                st.session_state.usuario_autenticado = True
                st.session_state.rol = 'Administrador'
                st.session_state.user_data = {
                    'id': 1,
                    'login': 'admin@iujo.edu',
                    'email': 'admin@iujo.edu',
                    'rol': 'Administrador',
                    'activo': True,
                    'correo_verificado': True,
                    'nombre': 'Administrador',
                    'apellido': 'Sistema'
                }
                
                # Registrar auditoría
                registrar_auditoria_sistema(
                    usuario='admin@iujo.edu',
                    transaccion='LOGIN_ADMIN_FORZADO',
                    tabla_afectada='usuario',
                    detalles_adicionales=f"Cédula: {p}, Rol: Administrador"
                )
                
                st.success("🎉 ¡Bienvenido Administrador!")
                st.info("🔐 Rol: Administrador")
                st.balloons()
                st.rerun()
                st.stop()
            
            # Login normal para otros usuarios
            crear_tablas_sistema(engine)
            crear_usuario_prueba(engine)
            
            import hashlib
            hash_password = hashlib.sha256(p.encode()).hexdigest()
            
            query_auth = """
                SELECT id, login, email, rol, activo, correo_verificado, nombre, apellido
                FROM usuario 
                WHERE (email = :email OR login = :email) 
                AND contrasena = :password
            """
            
            try:
                res_auth = ejecutar_query(query_auth, {"email": u, "password": hash_password}, engine=engine)
                
                if res_auth is not None and not res_auth.empty:
                    usuario_data = res_auth.iloc[0].to_dict()
                    
                    if not usuario_data.get('activo', False):
                        st.error("❌ Su cuenta está desactivada.")
                        st.stop()
                    
                    if not usuario_data.get('correo_verificado', False):
                        st.error("❌ Debe verificar su correo electrónico.")
                        st.stop()
                    
                    st.session_state.autenticado = True
                    st.session_state.user_data = usuario_data
                    st.session_state.rol = usuario_data.get('rol', 'estudiante')
                    
                    registrar_auditoria_sistema(
                        usuario=usuario_data.get('login', u),
                        transaccion='LOGIN',
                        tabla_afectada='usuario',
                        detalles_adicionales=f"Email: {u}, Rol: {st.session_state.rol}"
                    )
                    
                    nombre_completo = f"{usuario_data.get('nombre', '')} {usuario_data.get('apellido', '')}".strip()
                    if nombre_completo:
                        st.success(f"🎉 ¡Bienvenido {nombre_completo}!")
                    else:
                        st.success(f"🎉 ¡Bienvenido {usuario_data.get('login', u)}!")
                    
                    st.info(f"🔐 Rol: {st.session_state.rol.title()}")
                    st.balloons()
                    st.rerun()
                    
                else:
                    st.error("❌ Correo o cédula incorrectos.")
                    
            except Exception as e:
                st.error("❌ Error en el sistema de autenticación")
                st.error(f"Detalles: {str(e)}")

# =================================================================
# 4. SIDEBAR Y NAVEGACIÓN
# =================================================================

if st.session_state.get('autenticado', False):
    with st.sidebar:
        # Logo y título
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎓</div>
            <div style="color: #1e293b; font-weight: 600; font-size: 1rem;">
                SICADFOC 2026
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar aviso de ambiente
        mostrar_aviso_ambiente(tipo_ambiente)
        
        # Información de usuario
        rol_actual = obtener_rol_usuario()
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1E293B 0%, #334155 100%); 
                    padding: 1rem; border-radius: 10px; margin: 1rem 0; 
                    border: 1px solid #334155;">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem; margin-right: 0.5rem;">👤</span>
                <div>
                    <div style="color: #F8FAFC; font-weight: 600; font-size: 0.9rem;">
                        {st.session_state.user_data['login']}
                    </div>
                    <div style="color: #CBD5E1; font-size: 0.8rem;">
                        Nivel: {rol_actual.title() if rol_actual else 'Desconocido'}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Menú de navegación
        st.markdown("""
        <div style="color: #1e293b; font-weight: 600; font-size: 0.9rem; margin-bottom: 1rem;">
            📋 MÓDULOS OPERATIVOS
        </div>
        """, unsafe_allow_html=True)
        
        # Opciones con nombres limpios y sin "Gestión"
        opciones_modulos = [
            "🏠 Inicio",
            "📚 Estudiantes", 
            "👨‍🏫 Profesores",
            "🎓 Formación Complementaria",
            "⚙️ Configuración",
            "📊 Reportes",
            "⚡ Monitor",
            "🔧 Ambientes (ITIL)"
        ]
        
        seleccion = st.radio(
            "",
            opciones_modulos,
            index=0,
            label_visibility="collapsed"
        )
        
        # Extraer el nombre del módulo (sin icono)
        modulo = seleccion.split(" ", 1)[1] if " " in seleccion else seleccion
        
        # Botón de cerrar sesión
        if st.button("🚪 Finalizar Sesión", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# =================================================================
# 5. DASHBOARDS POR ROL
# =================================================================

def mostrar_dashboard_admin():
    """Muestra el dashboard para administradores"""
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #DC2626 0%, #16A34A 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; 
                border: 1px solid #16A34A; text-align: center;">
        <h2 style="color: white; margin-bottom: 1rem;">
            👑 PANEL DE ADMINISTRADOR
        </h2>
        <p style="color: #E2E8F0; font-size: 1.1rem; margin: 0;">
            Acceso total a todas las funcionalidades del sistema
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botones principales con letras oscuras y fondo claro
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: #F8FAFC; padding: 2rem; border-radius: 10px; 
                    border: 2px solid #E2E8F0; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #1E293B; margin-top: 0; font-size: 1.2rem; font-weight: 600;">
                📚 ESTUDIANTES
            </h4>
            <p style="color: #64748B; margin: 0.5rem 0; font-weight: 500;">
                Gestión completa de estudiantes
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div style="background: #F8FAFC; padding: 2rem; border-radius: 10px; 
                    border: 2px solid #E2E8F0; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #1E293B; margin-top: 0; font-size: 1.2rem; font-weight: 600;">
                👨‍🏫 PROFESORES
            </h4>
            <p style="color: #64748B; margin: 0.5rem 0; font-weight: 500;">
                Administración de docentes
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div style="background: #F8FAFC; padding: 2rem; border-radius: 10px; 
                    border: 2px solid #E2E8F0; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #1E293B; margin-top: 0; font-size: 1.2rem; font-weight: 600;">
                🎓 FORMACIÓN COMPLEMENTARIA
            </h4>
            <p style="color: #64748B; margin: 0.5rem 0; font-weight: 500;">
                Actividades extracurriculares
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.success("✅ Panel de administrador cargado correctamente")
    st.info("📋 Use los botones principales para gestionar cada módulo")
    
    # =================================================================
    # SECCIÓN DE CONFIGURACIÓN DE CORREO
    # =================================================================
    
    st.divider()
    st.subheader("📧 Configuración de Correo SMTP")
    
    col_config1, col_config2 = st.columns(2)
    
    with col_config1:
        st.write("**Configuración Actual:**")
        
        # Mostrar configuración actual
        try:
            config_actual = database.obtener_config_correo(engine)
            if config_actual:
                st.success(f"📧 Servidor: {config_actual['servidor_smtp']}")
                st.success(f"📧 Puerto: {config_actual['puerto']}")
                st.success(f"👤 Usuario: {config_actual['usuario']}")
                st.success(f"📧 Remitente: {config_actual['remitente']}")
            else:
                st.warning("⚠️ No hay configuración de correo establecida")
        except Exception as e:
            st.error(f"❌ Error obteniendo configuración: {e}")
    
    with col_config2:
        st.write("**Acciones Rápidas:**")
        
        # Botón para configurar correo final
        if st.button("🔧 Configurar Correo Gmail", type="primary", use_container_width=True):
            with st.spinner("Configurando servicio de correo..."):
                if database.configurar_correo_final():
                    st.success("✅ Configuración de correo establecida")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Error configurando el correo")
        
        # Botón para probar envío
        email_prueba = st.text_input(
            "📧 Correo de prueba",
            value="ab6643881@gmail.com",
            help="Ingrese el correo donde se enviará la prueba"
        )
        
        if st.button("🧪 Enviar Correo de Prueba", type="secondary", use_container_width=True):
            if email_prueba:
                with st.spinner("Enviando correo de prueba..."):
                    exito, mensaje = database.probar_envio_correo(email_prueba)
                    
                    if exito:
                        st.success("✅ Correo de prueba enviado exitosamente")
                        st.info(mensaje)
                        st.balloons()
                    else:
                        st.error("❌ Error enviando correo")
                        st.error(mensaje)
                        # Mostrar detalles del error en Streamlit
                        if "Authentication" in mensaje:
                            st.error("🔐 Error de autenticación - Verifique usuario y contraseña")
                        elif "Connection" in mensaje:
                            st.error("🌐 Error de conexión - Verifique red y firewall")
                        else:
                            st.error(f"❓ Error desconocido: {mensaje}")
            else:
                st.warning("⚠️ Ingrese un correo de prueba")

def mostrar_dashboard_profesor():
    """Muestra el dashboard para profesores"""
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #059669 0%, #047857 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; 
                border: 1px solid #047857; text-align: center;">
        <h2 style="color: white; margin-bottom: 1rem;">
            👨‍🏫 PANEL DE PROFESOR
        </h2>
        <p style="color: #E2E8F0; font-size: 1.1rem; margin: 0;">
            Gestión académica y formación complementaria
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: #F8FAFC; padding: 2rem; border-radius: 10px; 
                    border: 2px solid #E2E8F0; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #059669; margin-top: 0; font-size: 1.2rem; font-weight: 600;">
                📚 CURSOS
            </h4>
            <p style="color: #64748B; margin: 0.5rem 0; font-weight: 500;">
                Gestión de materias
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div style="background: #F8FAFC; padding: 2rem; border-radius: 10px; 
                    border: 2px solid #E2E8F0; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #059669; margin-top: 0; font-size: 1.2rem; font-weight: 600;">
                🎓 FORMACIÓN
            </h4>
            <p style="color: #64748B; margin: 0.5rem 0; font-weight: 500;">
                Actividades complementarias
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.success("✅ Panel de profesor cargado correctamente")
    st.info("📋 Use el menú lateral para acceder a sus funcionalidades")

def mostrar_dashboard_estudiante():
    """Muestra el dashboard para estudiantes"""
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; 
                border: 1px solid #2563EB; text-align: center;">
        <h2 style="color: white; margin-bottom: 1rem;">
            🎓 PANEL DE ESTUDIANTE
        </h2>
        <p style="color: #E2E8F0; font-size: 1.1rem; margin: 0;">
            Acceso a información académica y formación
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: #F8FAFC; padding: 2rem; border-radius: 10px; 
                    border: 2px solid #E2E8F0; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #3B82F6; margin-top: 0; font-size: 1.2rem; font-weight: 600;">
                📖 MATERIAS
            </h4>
            <p style="color: #64748B; margin: 0.5rem 0; font-weight: 500;">
                Mis cursos
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div style="background: #F8FAFC; padding: 2rem; border-radius: 10px; 
                    border: 2px solid #E2E8F0; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #3B82F6; margin-top: 0; font-size: 1.2rem; font-weight: 600;">
                📋 NOTAS
            </h4>
            <p style="color: #64748B; margin: 0.5rem 0; font-weight: 500;">
                Mis calificaciones
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div style="background: #F8FAFC; padding: 2rem; border-radius: 10px; 
                    border: 2px solid #E2E8F0; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #3B82F6; margin-top: 0; font-size: 1.2rem; font-weight: 600;">
                🎯 ACTIVIDADES
            </h4>
            <p style="color: #64748B; margin: 0.5rem 0; font-weight: 500;">
                Formación complementaria
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.success("✅ Panel de estudiante cargado correctamente")
    st.info("📋 Use el menú lateral para acceder a sus funcionalidades")

# =================================================================
# 8. FORMULARIO DE REGISTRO
# =================================================================

# Mostrar formulario de registro si no está autenticado
if not st.session_state.get('autenticado', False):
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h3 style="color: #1e293b; font-weight: 600;">
            📝 REGISTRO DE NUEVO USUARIO
        </h3>
        <p style="color: #64748b; font-size: 0.9rem;">
            Complete el formulario para crear su cuenta en SICADFOC
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("registro_form", clear_on_submit=False):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            email_reg = st.text_input(
                "📧 Correo Institucional", 
                placeholder="usuario@iujo.edu.ve",
                help="Ingrese su correo institucional",
                key="email_registro"
            )
            cedula_reg = st.text_input(
                "🆔 Cédula de Identidad", 
                placeholder="V-XXXXXXX o E-XXXXXXX",
                help="Ingrese su número de cédula",
                key="cedula_registro"
            )
        
        with col2:
            perfil_reg = st.selectbox(
                "👤 Perfil de Usuario",
                options=["Estudiante", "Profesor"],
                index=0,
                help="Seleccione su perfil en el sistema",
                key="perfil_registro"
            )
        
        # Información importante
        st.info("ℹ️ **Importante:** Al registrarse, recibirá un correo de confirmación para activar su cuenta.")
        st.info("📧 El correo de confirmación será enviado a la dirección que ingrese.")
        
        # Botones de acción
        col_registrar, col_probar = st.columns([2, 1])
        
        with col_registrar:
            btn_registrar = st.form_submit_button(
                "🚀 Crear Cuenta", 
                type="primary",
                use_container_width=True
            )
        
        with col_probar:
            btn_probar_correo = st.form_submit_button(
                "🧪 Probar Correo", 
                type="secondary",
                use_container_width=True
            )
        
        if btn_probar_correo:
            if email_reg:
                with st.spinner("Enviando correo de prueba..."):
                    exito, mensaje = database.probar_envio_correo(email_reg)
                    
                    if exito:
                        st.success("✅ Correo de prueba enviado exitosamente")
                        st.info(mensaje)
                        st.balloons()
                    else:
                        st.error("❌ Error enviando correo")
                        st.error(mensaje)
                        
                        # Mostrar detalles del error en Streamlit
                        if "Authentication" in mensaje:
                            st.error("🔐 Error de autenticación - Verifique usuario y contraseña de aplicación")
                        elif "Connection" in mensaje:
                            st.error("🌐 Error de conexión - Verifique red y firewall")
                        else:
                            st.error(f"❓ Error desconocido: {mensaje}")
            else:
                st.warning("⚠️ Ingrese un correo para probar")
        
        if btn_registrar:
            # Validar campos
            if not email_reg or not cedula_reg:
                st.error("❌ Por favor, complete todos los campos")
                st.stop()
            
            # Validar formato de email
            if "@" not in email_reg or "." not in email_reg:
                st.error("❌ Formato de correo inválido")
                st.stop()
            
            # Validar formato de cédula
            if not (cedula_reg.startswith(('V-', 'E-', 'v-', 'e-')) and len(cedula_reg) >= 7):
                st.error("❌ Formato de cédula inválido. Use: V-XXXXXXX o E-XXXXXXX")
                st.stop()
            
            # =================================================================
# 4. SIDEBAR Y NAVEGACIÓN PROFESIONAL
# =================================================================

if st.session_state.get('autenticado', False):
    with st.sidebar:
        # Logo institucional
        try:
            # Intentar cargar logo institucional
            if os.path.exists("logo_iujo.png"):
                st.sidebar.image("logo_iujo.png", width=200, use_column_width=True)
            else:
                # Logo alternativo si no existe el archivo
                st.sidebar.markdown("""
                <div style="text-align: center; margin-bottom: 2rem;">
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">🎓</div>
                    <div style="color: #1e293b; font-weight: 700; font-size: 1.2rem; line-height: 1.2;">
                        INSTITUTO<br>UNIVERSITARIO<br>JESÚS OBRERO
                    </div>
                    <div style="color: #64748b; font-size: 0.9rem; margin-top: 0.5rem;">
                        SICADFOC 2026
                    </div>
                </div>
                """, unsafe_allow_html=True)
        except:
            # Logo de respaldo
            st.sidebar.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">🎓</div>
                <div style="color: #1e293b; font-weight: 700; font-size: 1.2rem; line-height: 1.2;">
                    INSTITUTO<br>UNIVERSITARIO<br>JESÚS OBRERO
                </div>
                <div style="color: #64748b; font-size: 0.9rem; margin-top: 0.5rem;">
                    SICADFOC 2026
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Información de usuario
        rol_actual = obtener_rol_usuario()
        st.sidebar.markdown(f"""
        <div style="background: linear-gradient(135deg, #1E293B 0%, #334155 100%); 
                    padding: 1rem; border-radius: 10px; margin: 1rem 0; 
                    border: 1px solid #334155;">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem; margin-right: 0.5rem;">👤</span>
                <div>
                    <div style="color: #F8FAFC; font-weight: 600; font-size: 0.9rem;">
                        {st.session_state.user_data['login']}
                    </div>
                    <div style="color: #CBD5E1; font-size: 0.8rem;">
                        Nivel: {rol_actual.title() if rol_actual else 'Desconocido'}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Menú de navegación principal
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📋 MÓDULOS PRINCIPALES")
        
        # Selector de módulo
        modulo_seleccionado = st.sidebar.radio(
            "Seleccionar Módulo:",
            ["🏠 Inicio", "📚 Estudiantes", "👨‍🏫 Profesores", "🎓 Formación Complementaria"],
            index=0,
            key="modulo_principal"
        )
        
        # Separador
        st.sidebar.markdown("---")
        
        # Información del sistema
        mostrar_aviso_ambiente(tipo_ambiente)
        
        # Botón de cerrar sesión
        if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# =================================================================
# 5. ÁREA PRINCIPAL - VISUALIZACIÓN LIMPIA
# =================================================================

if st.session_state.get('autenticado', False):
    # Control principal según selección del sidebar
    if modulo_seleccionado == "🏠 Inicio":
        # Dashboard principal
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1E293B 0%, #334155 100%); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 2rem; 
                    border: 1px solid #334155; text-align: center;">
            <h1 style="color: white; margin-bottom: 1rem;">
                🏠 PANEL PRINCIPAL
            </h1>
            <p style="color: #E2E8F0; font-size: 1.2rem; margin: 0;">
                Sistema Integral de Control Académico y Docente
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Métricas principales
        try:
            metrics = database.obtener_metricas_sistema()
            col_dash1, col_dash2, col_dash3 = st.columns(3)
            
            with col_dash1:
                st.metric("👨‍🎓 Estudiantes", metrics.get('estudiantes', 0))
            
            with col_dash2:
                st.metric("👨‍🏫 Profesores", metrics.get('profesores', 0)) 
            
            with col_dash3:
                st.metric("🎓 Cursos", metrics.get('cursos', 0))
        except:
            st.warning("⚠️ Cargando métricas...")
        
        st.divider()
        st.info("💡 Use el menú lateral para acceder a los diferentes módulos del sistema.")
    
    elif modulo_seleccionado == "📚 Estudiantes":
        # =================================================================
        # MÓDULO DE ESTUDIANTES - VISUALIZACIÓN LIMPIA
        # =================================================================
        st.header("📚 Gestión de Estudiantes")
        
        # Crear directorios necesarios
        os.makedirs("expedientes", exist_ok=True)
        
        # Pestañas principales
        tab1, tab2, tab3 = st.tabs(["📝 Registro Individual", "📊 Carga Masiva (CSV)", "📄 Expediente Digital (PDF)"])
        
        # =================================================================
        # PESTAÑA 1: REGISTRO INDIVIDUAL
        # =================================================================
        with tab1:
            st.subheader("📝 Registro Individual de Estudiantes")
            
            with st.form("registro_individual_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Cédula con validación en tiempo real
                    cedula = st.text_input(
                        "🆔 Cédula de Identidad *",
                        placeholder="V-12345678 o E-12345678",
                        help="Formato: V-XXXXXXXX o E-XXXXXXXX",
                        key="cedula_individual"
                    )
                    
                    # Validación en tiempo real
                    if cedula:
                        if not re.match(r'^[VE]-\d{7,8}$', cedula.upper()):
                            st.error("❌ Formato inválido. Use V-12345678 o E-12345678")
                        else:
                            # Verificar si ya existe
                            try:
                                verificar = ejecutar_query(
                                    "SELECT COUNT(*) as count FROM usuario WHERE login = :cedula OR cedula = :cedula",
                                    {"cedula": cedula.upper()},
                                    engine=engine
                                )
                                if verificar and verificar.iloc[0]['count'] > 0:
                                    st.warning("⚠️ Esta cédula ya está registrada")
                                else:
                                    st.success("✅ Cédula disponible")
                            except:
                                pass
                    
                    nombres = st.text_input(
                        "👤 Nombres *",
                        placeholder="Juan Carlos",
                        help="Nombres completos del estudiante",
                        key="nombres_individual"
                    )
                
                with col2:
                    apellidos = st.text_input(
                        "👥 Apellidos *",
                        placeholder="Pérez González",
                        help="Apellidos completos del estudiante",
                        key="apellidos_individual"
                    )
                    
                    correo = st.text_input(
                        "📧 Correo Institucional *",
                        placeholder="estudiante@iujo.edu.ve",
                        help="Correo electrónico del estudiante",
                        key="correo_individual"
                    )
                    
                    # Validación en tiempo real del correo
                    if correo:
                        if "@" not in correo or "." not in correo:
                            st.error("❌ Formato de correo inválido")
                        else:
                            # Verificar si ya existe
                            try:
                                verificar = ejecutar_query(
                                    "SELECT COUNT(*) as count FROM usuario WHERE login = :correo OR email = :correo",
                                    {"correo": correo.lower()},
                                    engine=engine
                                )
                                if verificar and verificar.iloc[0]['count'] > 0:
                                    st.warning("⚠️ Este correo ya está registrado")
                                else:
                                    st.success("✅ Correo disponible")
                            except:
                                pass
                
                semestre = st.selectbox(
                    "📚 Semestre *",
                    options=[f"{i}° Semestre" for i in range(1, 11)],
                    index=0,
                    help="Seleccione el semestre actual del estudiante",
                    key="semestre_individual"
                )
                
                # Información importante
                st.info("ℹ️ **Nota:** Los campos marcados con * son obligatorios")
                st.info("🔐 La contraseña inicial será la cédula de identidad")
                
                # Botones de acción
                col_guardar, col_limpiar = st.columns([2, 1])
                
                with col_guardar:
                    btn_guardar = st.form_submit_button(
                        "💾 Guardar Estudiante",
                        type="primary",
                        use_container_width=True
                    )
                
                with col_limpiar:
                    btn_limpiar = st.form_submit_button(
                        "🗑️ Limpiar Formulario",
                        type="secondary",
                        use_container_width=True
                    )
                
                if btn_guardar:
                    # Validar campos obligatorios
                    if not all([cedula, nombres, apellidos, correo]):
                        st.error("❌ Complete todos los campos obligatorios")
                        st.stop()
                    
                    # Validar formatos
                    if not re.match(r'^[VE]-\d{7,8}$', cedula.upper()):
                        st.error("❌ Formato de cédula inválido")
                        st.stop()
                    
                    if "@" not in correo or "." not in correo:
                        st.error("❌ Formato de correo inválido")
                        st.stop()
                    
                    # Procesar registro
                    with st.spinner("Registrando estudiante..."):
                        try:
                            # Verificar duplicados
                            verificar_cedula = ejecutar_query(
                                "SELECT COUNT(*) as count FROM usuario WHERE login = :cedula OR cedula = :cedula",
                                {"cedula": cedula.upper()},
                                engine=engine
                            )
                            
                            verificar_correo = ejecutar_query(
                                "SELECT COUNT(*) as count FROM usuario WHERE login = :correo OR email = :correo",
                                {"correo": correo.lower()},
                                engine=engine
                            )
                            
                            if verificar_cedula.iloc[0]['count'] > 0:
                                st.error("❌ La cédula ya está registrada")
                                st.stop()
                            
                            if verificar_correo.iloc[0]['count'] > 0:
                                st.error("❌ El correo ya está registrado")
                                st.stop()
                            
                            # Insertar estudiante
                            hash_password = hashlib.sha256(cedula.upper().encode()).hexdigest()
                            
                            insertar = """
                            INSERT INTO usuario (
                                login, email, contrasena, rol, nombre, apellido, 
                                cedula, semestre, activo, correo_verificado, 
                                fecha_registro
                            ) VALUES (
                                :login, :email, :password, :rol, :nombre, :apellido,
                                :cedula, :semestre, :activo, :correo_verificado,
                                :fecha_registro
                            )
                            """
                            
                            ejecutar_query(insertar, {
                                'login': correo.lower(),
                                'email': correo.lower(),
                                'password': hash_password,
                                'rol': 'estudiante',
                                'nombre': nombres.title(),
                                'apellido': apellidos.title(),
                                'cedula': cedula.upper(),
                                'semestre': semestre,
                                'activo': True,
                                'correo_verificado': False,
                                'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }, engine=engine)
                            
                            st.success("✅ Estudiante registrado exitosamente")
                            st.info(f"📧 Se enviará correo de confirmación a: {correo}")
                            st.balloons()
                            
                            # Limpiar formulario
                            for key in st.session_state.keys():
                                if key.endswith('_individual'):
                                    del st.session_state[key]
                            
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error registrando estudiante: {str(e)}")
                
                if btn_limpiar:
                    # Limpiar campos del formulario
                    for key in st.session_state.keys():
                        if key.endswith('_individual'):
                            del st.session_state[key]
                    st.rerun()
        
        # =================================================================
        # PESTAÑA 2: CARGA MASIVA (CSV)
        # =================================================================
        with tab2:
            st.subheader("📊 Carga Masiva de Estudiantes (CSV)")
            
            # Instrucciones
            with st.expander("📋 Instrucciones de Formato CSV", expanded=True):
                st.markdown("""
                **Formato requerido para el archivo CSV:**
                
                | Columna | Requerida | Formato | Ejemplo |
                |----------|-----------|----------|---------|
                | cedula | Sí | V-12345678 | V-12345678 |
                | nombres | Sí | Texto | Juan Carlos |
                | apellidos | Sí | Texto | Pérez González |
                | correo | Sí | email@dominio.com | estudiante@iujo.edu.ve |
                | semestre | Sí | Número 1-10 | 3 |
                
                **Notas:**
                - El archivo debe tener encabezado en la primera fila
                - Los campos cédula y correo no deben repetirse
                - Si una cédula ya existe, se omitirá y se reportará al final
                """)
            
            # Carga de archivo
            archivo_csv = st.file_uploader(
                "📁 Seleccione archivo CSV",
                type=['csv'],
                help="Suba el archivo CSV con los datos de los estudiantes",
                key="archivo_csv"
            )
            
            if archivo_csv:
                try:
                    # Leer archivo CSV
                    df = pd.read_csv(archivo_csv)
                    
                    # Validar columnas requeridas
                    columnas_requeridas = ['cedula', 'nombres', 'apellidos', 'correo', 'semestre']
                    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
                    
                    if columnas_faltantes:
                        st.error(f"❌ Columnas faltantes: {', '.join(columnas_faltantes)}")
                        st.stop()
                    
                    # Mostrar vista previa
                    st.write("📊 **Vista Previa de Datos:**")
                    st.dataframe(df.head(10))
                    
                    # Procesar carga
                    if st.button("🚀 Procesar Carga Masiva", type="primary", use_container_width=True):
                        with st.spinner("Procesando carga masiva..."):
                            try:
                                creados = 0
                                omitidos = 0
                                errores = []
                                
                                for index, row in df.iterrows():
                                    try:
                                        # Validar datos
                                        cedula = str(row['cedula']).strip().upper()
                                        nombres = str(row['nombres']).strip().title()
                                        apellidos = str(row['apellidos']).strip().title()
                                        correo = str(row['correo']).strip().lower()
                                        semestre = str(row['semestre']).strip()
                                        
                                        # Validar formato de cédula
                                        if not re.match(r'^[VE]-\d{7,8}$', cedula):
                                            errores.append(f"Fila {index+2}: Cédula inválida: {cedula}")
                                            omitidos += 1
                                            continue
                                        
                                        # Validar formato de correo
                                        if "@" not in correo or "." not in correo:
                                            errores.append(f"Fila {index+2}: Correo inválido: {correo}")
                                            omitidos += 1
                                            continue
                                        
                                        # Verificar duplicados
                                        verificar_cedula = ejecutar_query(
                                            "SELECT COUNT(*) as count FROM usuario WHERE cedula = :cedula",
                                            {"cedula": cedula},
                                            engine=engine
                                        )
                                        
                                        verificar_correo = ejecutar_query(
                                            "SELECT COUNT(*) as count FROM usuario WHERE email = :correo",
                                            {"correo": correo},
                                            engine=engine
                                        )
                                        
                                        if verificar_cedula.iloc[0]['count'] > 0:
                                            omitidos += 1
                                            continue
                                        
                                        if verificar_correo.iloc[0]['count'] > 0:
                                            omitidos += 1
                                            continue
                                        
                                        # Insertar estudiante
                                        hash_password = hashlib.sha256(cedula.encode()).hexdigest()
                                        
                                        insertar = """
                                        INSERT INTO usuario (
                                            login, email, contrasena, rol, nombre, apellido,
                                            cedula, semestre, activo, correo_verificado,
                                            fecha_registro
                                        ) VALUES (
                                            :login, :email, :password, :rol, :nombre, :apellido,
                                            :cedula, :semestre, :activo, :correo_verificado,
                                            :fecha_registro
                                        )
                                        """
                                        
                                        ejecutar_query(insertar, {
                                            'login': correo,
                                            'email': correo,
                                            'password': hash_password,
                                            'rol': 'estudiante',
                                            'nombre': nombres,
                                            'apellido': apellidos,
                                            'cedula': cedula,
                                            'semestre': f"{semestre}° Semestre",
                                            'activo': True,
                                            'correo_verificado': False,
                                            'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        }, engine=engine)
                                        
                                        creados += 1
                                        
                                    except Exception as e:
                                        errores.append(f"Fila {index+2}: {str(e)}")
                                        omitidos += 1
                                
                                # Mostrar resultados
                                st.success("✅ Proceso completado")
                                
                                col_res1, col_res2, col_res3 = st.columns(3)
                                
                                with col_res1:
                                    st.metric("📝 Estudiantes Creados", creados)
                                
                                with col_res2:
                                    st.metric("⚠️ Registros Omitidos", omitidos)
                                
                                with col_res3:
                                    st.metric("📊 Total Procesados", len(df))
                                
                                if errores:
                                    st.error("❌ Errores encontrados:")
                                    for error in errores[:10]:  # Mostrar solo primeros 10 errores
                                        st.error(error)
                                    if len(errores) > 10:
                                        st.warning(f"... y {len(errores) - 10} errores más")
                                
                                if creados > 0:
                                    st.balloons()
                                    st.info(f"📧 Se enviarán correos de confirmación a los {creados} estudiantes creados")
                                
                            except Exception as e:
                                st.error(f"❌ Error en carga masiva: {str(e)}")
                                
                except Exception as e:
                    st.error(f"❌ Error leyendo archivo CSV: {str(e)}")
        
        # =================================================================
        # PESTAÑA 3: EXPEDIENTE DIGITAL (PDF)
        # =================================================================
        with tab3:
            st.subheader("📄 Expediente Digital (PDF)")
            
            # Información importante
            st.info("ℹ️ **Nota:** Puede subir documentos PDF usando la cámara de su celular o apps como CamScanner")
            
            # Buscar estudiante
            col_buscar, col_buscar_btn = st.columns([3, 1])
            
            with col_buscar:
                cedula_buscar = st.text_input(
                    "🔍 Buscar Estudiante por Cédula",
                    placeholder="V-12345678",
                    help="Ingrese la cédula del estudiante",
                    key="cedula_buscar_expediente"
                )
            
            with col_buscar_btn:
                st.write("")  # Espacio para alinear el botón
                btn_buscar = st.button("🔍 Buscar", use_container_width=True)
            
            estudiante_encontrado = None
            
            if btn_buscar and cedula_buscar:
                try:
                    resultado = ejecutar_query(
                        "SELECT * FROM usuario WHERE cedula = :cedula AND rol = 'estudiante'",
                        {"cedula": cedula_buscar.upper()},
                        engine=engine
                    )
                    
                    if resultado is not None and not resultado.empty:
                        estudiante_encontrado = resultado.iloc[0]
                        st.success(f"✅ Estudiante encontrado: {estudiante_encontrado['nombre']} {estudiante_encontrado['apellido']}")
                    else:
                        st.error("❌ Estudiante no encontrado")
                except Exception as e:
                    st.error(f"❌ Error buscando estudiante: {str(e)}")
            
            if estudiante_encontrado is not None:
                # Mostrar información del estudiante
                with st.expander("👤 Información del Estudiante", expanded=True):
                    col_info1, col_info2 = st.columns(2)
                    
                    with col_info1:
                        st.write(f"**🆔 Cédula:** {estudiante_encontrado['cedula']}")
                        st.write(f"**👤 Nombre:** {estudiante_encontrado['nombre']}")
                        st.write(f"**👥 Apellido:** {estudiante_encontrado['apellido']}")
                    
                    with col_info2:
                        st.write(f"**📧 Correo:** {estudiante_encontrado['email']}")
                        st.write(f"**📚 Semestre:** {estudiante_encontrado['semestre']}")
                        st.write(f"**✅ Estado:** {'Activo' if estudiante_encontrado['activo'] else 'Inactivo'}")
                
                # Carga de archivos PDF
                st.write("---")
                st.write("📁 **Subir Expediente Digital**")
                
                # Optimizado para móvil
                archivos_pdf = st.file_uploader(
                    "📄 Seleccione archivos PDF",
                    type=['pdf'],
                    accept_multiple_files=True,
                    help="Suba los documentos PDF del expediente. Puede usar la cámara de su celular.",
                    key="archivos_pdf_expediente"
                )
                
                if archivos_pdf:
                    st.write(f"📊 **Archivos seleccionados:** {len(archivos_pdf)}")
                    
                    # Mostrar vista previa de archivos
                    for i, archivo in enumerate(archivos_pdf):
                        col_file, col_name = st.columns([1, 4])
                        
                        with col_file:
                            st.write(f"📄")
                        
                        with col_name:
                            st.write(f"**{archivo.name}** ({archivo.size / 1024:.1f} KB)")
                    
                    # Botón para guardar archivos
                    if st.button("💾 Guardar Expediente", type="primary", use_container_width=True):
                        with st.spinner("Guardando expediente digital..."):
                            try:
                                guardados = 0
                                errores = []
                                
                                for archivo in archivos_pdf:
                                    try:
                                        # Crear nombre de archivo seguro
                                        cedula_limpia = re.sub(r'[^a-zA-Z0-9]', '_', estudiante_encontrado['cedula'])
                                        nombre_archivo = f"{cedula_limpia}_{archivo.name}"
                                        
                                        # Ruta de destino
                                        ruta_destino = os.path.join("expedientes", nombre_archivo)
                                        
                                        # Guardar archivo
                                        with open(ruta_destino, "wb") as f:
                                            f.write(archivo.getbuffer())
                                        
                                        guardados += 1
                                        
                                    except Exception as e:
                                        errores.append(f"Error guardando {archivo.name}: {str(e)}")
                                
                                # Mostrar resultados
                                if guardados > 0:
                                    st.success(f"✅ {guardados} archivos guardados exitosamente")
                                    st.info(f"📁 Ubicación: /expedientes/")
                                
                                if errores:
                                    st.error("❌ Errores al guardar:")
                                    for error in errores:
                                        st.error(error)
                                
                                if guardados > 0:
                                    st.balloons()
                                    
                            except Exception as e:
                                st.error(f"❌ Error general guardando expediente: {str(e)}")
                
                # Mostrar archivos existentes
                st.write("---")
                st.write("📂 **Expediente Existente**")
                
                try:
                    cedula_limpia = re.sub(r'[^a-zA-Z0-9]', '_', estudiante_encontrado['cedula'])
                    archivos_existentes = []
                    
                    # Buscar archivos del estudiante
                    for archivo in os.listdir("expedientes"):
                        if archivo.startswith(cedula_limpia) and archivo.endswith('.pdf'):
                            ruta_completa = os.path.join("expedientes", archivo)
                            tamaño = os.path.getsize(ruta_completa) / 1024  # KB
                            archivos_existentes.append({
                                'nombre': archivo,
                                'ruta': ruta_completa,
                                'tamaño': tamaño
                            })
                    
                    if archivos_existentes:
                        st.write(f"📄 **Archivos encontrados:** {len(archivos_existentes)}")
                        
                        for archivo_info in archivos_existentes:
                            col_archivo, col_tamaño, col_accion = st.columns([3, 1, 1])
                            
                            with col_archivo:
                                st.write(f"📄 {archivo_info['nombre']}")
                            
                            with col_tamaño:
                                st.write(f"{archivo_info['tamaño']:.1f} KB")
                            
                            with col_accion:
                                if st.button("👁️", key=f"ver_{archivo_info['nombre']}", help="Ver PDF"):
                                    st.info(f"📂 Ruta: {archivo_info['ruta']}")
                    else:
                        st.info("📭 No hay archivos en el expediente")
                        
                except Exception as e:
                    st.error(f"❌ Error listando archivos: {str(e)}")
            else:
                st.info("🔍 Busque un estudiante para gestionar su expediente digital")
    
    elif modulo_seleccionado == "👨‍🏫 Profesores":
        # Módulo de Profesores
        st.header("👨‍🏫 Gestión de Profesores")
        st.info("🔧 Módulo en desarrollo - Próximamente disponible")
    
    elif modulo_seleccionado == "🎓 Formación Complementaria":
        # Módulo de Formación Complementaria
        st.header("🎓 Formación Complementaria")
        st.info("🔧 Módulo en desarrollo - Próximamente disponible")
