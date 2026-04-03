# =================================================================
# UI COMPONENTS - SICADFOC 2026
# =================================================================

import streamlit as st
import pandas as pd
import time
from datetime import datetime

# =================================================================
# DEFINICIÓN DE MÓDULOS POR ROL
# =================================================================

# Módulos para Administrador
modulos_admin = [
    "👥 Usuarios", 
    "👨‍🏫 Profesores",
    "👨‍🎓 Estudiantes",
    "📚 Formación Complementaria",
    "📊 Reportes",
    "⚙️ Configuración"
]

# Módulos para Profesor
modulos_profesor = [
    "📚 Formación Complementaria",
    "👨‍🎓 Estudiantes",
    "📊 Reportes"
]

# Módulos para Estudiante
modulos_estudiante = [
    "📚 Formación Complementaria",
    "📁 Mis Documentos",
    "📊 Mi Progreso"
]

# =================================================================
# FUNCIONES DE NAVEGACIÓN
# =================================================================

def obtener_modulos_por_rol(rol):
    """Obtiene la lista de módulos según el rol del usuario"""
    if rol.lower() == "administrador":
        return modulos_admin
    elif rol.lower() == "profesor":
        return modulos_profesor
    elif rol.lower() == "estudiante":
        return modulos_estudiante
    else:
        # Rol no detectado - módulos por defecto
        return ["🏠 Dashboard Principal"]

def mostrar_sidebar_protegido():
    """Muestra el menú lateral con navegación protegida y estilo dark mode"""
    
    # CSS para sidebar con dark mode
    st.sidebar.markdown("""
    <style>
    /* Sidebar Dark Mode */
    .css-1lcbm8y {
        background-color: rgba(30, 41, 59, 0.95) !important;
        backdrop-filter: blur(10px);
    }
    
    .css-1lcbm8y .stSelectbox {
        background-color: rgba(51, 65, 85, 0.8) !important;
        color: #f1f5f9 !important;
        border: 1px solid #475569 !important;
    }
    
    .css-1lcbm8y .stButton {
        background-color: rgba(51, 65, 85, 0.8) !important;
        color: #f1f5f9 !important;
        border: 1px solid #475569 !important;
        transition: all 0.3s ease !important;
    }
    
    .css-1lcbm8y .stButton:hover {
        background-color: rgba(71, 85, 105, 0.9) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .css-1lcbm8y .stButton:active {
        background-color: rgba(99, 102, 241, 0.8) !important;
        transform: translateY(0px);
    }
    
    /* Botón activo */
    .css-1lcbm8y button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: 1px solid #667eea !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .css-1lcbm8y button[data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Texto del sidebar */
    .css-1lcbm8y h1, .css-1lcbm8y h2, .css-1lcbm8y h3, 
    .css-1lcbm8y h4, .css-1lcbm8y p, .css-1lcbm8y span {
        color: #f1f5f9 !important;
    }
    
    /* Separadores */
    .css-1lcbm8y hr {
        border-color: rgba(71, 85, 105, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Obtener rol y módulos (lógica intacta)
    rol_usuario = st.session_state.get('rol', 'Desconocido')
    modulos_disponibles = obtener_modulos_por_rol(rol_usuario)
    
    # Header del sidebar con estilo institucional
    st.sidebar.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.95) 100%);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(71, 85, 105, 0.3);
        text-align: center;
    ">
        <div style="display: flex; align-items: center; justify-content: center; gap: 15px;">
            <img src="app/logo_IUJO.png" alt="IUJO Logo" style="width: 50px; height: 50px; object-fit: contain;">
            <h1 style="color: #f1f5f9; font-size: 1.5rem; font-weight: 700; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                IUJO
            </h1>
        </div>
        <p style="color: #cbd5e1; font-size: 0.9rem; margin: 5px 0 0 0;">
            Instituto Universitario Jesús Obrero
        </p>
        <p style="color: #94a3b8; font-size: 0.8rem; margin: 0;">
            Sistema Integrado de Control Académico 2026
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Información del usuario
    st.sidebar.markdown("---")
    user_data = st.session_state.get('user_data', {})
    
    # Tarjeta de información del usuario
    st.sidebar.markdown(f"""
    <div style="
        background: rgba(51, 65, 85, 0.8);
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
        border: 1px solid rgba(71, 85, 105, 0.3);
    ">
        <h3 style="color: #f1f5f9; margin: 0 0 10px 0; font-size: 1rem;">
            👤 Información de Usuario
        </h3>
        <p style="color: #cbd5e1; margin: 5px 0;">
            <strong style="color: #f1f5f9;">Nombre:</strong> {user_data.get('nombre', 'N/A')}
        </p>
        <p style="color: #cbd5e1; margin: 5px 0;">
            <strong style="color: #f1f5f9;">Rol:</strong> <span style="color: #10b981;">{rol_usuario.title()}</span>
        </p>
        <p style="color: #cbd5e1; margin: 5px 0;">
            <strong style="color: #f1f5f9;">Email:</strong> {user_data.get('email', 'N/A')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Título de módulos
    st.sidebar.markdown("""
    <h3 style="color: #f1f5f9; margin: 20px 0 10px 0; font-size: 1rem;">
        📋 Módulos Disponibles
    </h3>
    """, unsafe_allow_html=True)
    
    # Obtener módulo actual del session state (con persistencia)
    modulo_actual = st.session_state.get('modulo_actual', modulos_disponibles[0])
    
    # Asegurar que el módulo actual esté en la lista de disponibles
    if modulo_actual not in modulos_disponibles:
        modulo_actual = modulos_disponibles[0]
        st.session_state['modulo_actual'] = modulo_actual
    
    # Botones individuales verticales para cada módulo
    pagina_seleccionada = modulo_actual
    
    for modulo in modulos_disponibles:
        # Determinar si este módulo está activo
        is_active = (modulo == modulo_actual)
        
        # Agregar espaciado entre botones
        st.sidebar.markdown('<div style="margin-bottom: 8px;"></div>', unsafe_allow_html=True)
        
        # Crear botón con estilo según estado
        if is_active:
            # Botón activo (azul institucional)
            st.sidebar.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                text-align: center;
                font-weight: 600;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
                transition: all 0.3s ease;
                cursor: pointer;
            ">
                🔵 {modulo}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Botón inactivo (oscuro semitransparente) - HTML personalizado con funcionalidad
            st.sidebar.markdown(f"""
            <div style="
                background: rgba(51, 65, 85, 0.6);
                border: 1px solid rgba(71, 85, 105, 0.3);
                border-radius: 8px;
                padding: 12px 16px;
                text-align: center;
                font-weight: 600;
                color: #f1f5f9;
                transition: all 0.3s ease;
                cursor: pointer;
                margin-bottom: 12px;
            " onclick="window.location.href='?modulo={modulo.lower().replace(' ', '_').replace('👥', '').replace('👨‍🏫', '').replace('👨‍🎓', '').replace('📚', '').replace('📊', '').replace('⚙️', '').replace('🏠', '').strip()}'">
                ⚪ {modulo}
            </div>
            """, unsafe_allow_html=True)
    
    # Separador final
    st.sidebar.markdown("""
    <div style="
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid rgba(71, 85, 105, 0.3);
    "></div>
    """, unsafe_allow_html=True)
    
    # Botón de cambiar contraseña con estilo dark
    st.sidebar.markdown(f"""
    <div style="
        background: rgba(51, 65, 85, 0.6);
        border: 1px solid rgba(71, 85, 105, 0.3);
        border-radius: 8px;
        padding: 12px 16px;
        text-align: center;
        font-weight: 600;
        color: #f1f5f9;
        transition: all 0.3s ease;
        cursor: pointer;
        margin-bottom: 15px;
    " onclick="window.location.href='#change_password'">
        🔑 Cambiar Contraseña
    </div>
    """, unsafe_allow_html=True)
    
    # Botón oculto para la navegación real
    if st.sidebar.button("change_password", key="change_password"):
        st.session_state['mostrar_cambio_clave'] = True
        st.rerun()
    
    # Separador final
    st.sidebar.markdown('<div style="margin-bottom: 20px;"></div>', unsafe_allow_html=True)
    
    # Botón de cerrar sesión con estilo dark
    st.sidebar.markdown(f"""
    <div style="
        background: rgba(239, 68, 68, 0.8);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 8px;
        padding: 12px 16px;
        text-align: center;
        font-weight: 600;
        color: white;
        transition: all 0.3s ease;
        cursor: pointer;
        margin-bottom: 15px;
    " onclick="window.location.href='#logout'">
        🚪 Cerrar Sesión
    </div>
    """, unsafe_allow_html=True)
    
    # Botón oculto para la navegación real
    if st.sidebar.button("logout", key="logout"):
        st.session_state.clear()
        st.rerun()
    
    # Padding bottom para no tocar el borde
    st.sidebar.markdown('<div style="margin-bottom: 30px;"></div>', unsafe_allow_html=True)
    
    return pagina_seleccionada

# =================================================================
# FUNCIONES DE MÓDULOS
# =================================================================

def mostrar_dashboard_principal():
    """Muestra el dashboard principal"""
    st.markdown("## 🏠 Dashboard Principal")
    st.markdown("---")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Usuarios", "150")
    with col2:
        st.metric("📁 Archivos PDF", "1,234")
    with col3:
        st.metric("🔍 Auditorías", "89")
    with col4:
        st.metric("⚡ Actividad", "98%")
    
    st.markdown("---")
    
    # Gráficos y actividad reciente
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Actividad Reciente")
        st.write("• 5 usuarios nuevos registrados")
        st.write("• 12 archivos PDF procesados")
        st.write("• 3 auditorías completadas")
        
    with col2:
        st.markdown("### 🎯 Tareas Pendientes")
        st.write("• 2 usuarios por aprobar")
        st.write("• 5 archivos por validar")
        st.write("• 1 configuración pendiente")

def mostrar_dashboard_protegido():
    """Dashboard protegido con acceso a todos los módulos - Alias para mostrar_dashboard_principal"""
    
    # Verificar si el usuario está autenticado
    if not st.session_state.get('autenticado', False):
        st.error("❌ Debe iniciar sesión para acceder al dashboard")
        st.stop()
        return
    
    # Mostrar información del usuario
    user_data = st.session_state.get('user_data', {})
    rol_usuario = user_data.get('rol', 'Desconocido')
    
    st.markdown("## 🏠 Dashboard Principal")
    st.markdown("---")
    
    # Información de sesión
    st.markdown("### 👤 Información de Sesión")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**Usuario:** {user_data.get('nombre', 'N/A')}")
    
    with col2:
        st.info(f"**Rol:** {rol_usuario}")
    
    with col3:
        st.info(f"**Email:** {user_data.get('email', 'N/A')}")
    
    st.markdown("---")
    
    # Métricas principales según rol
    st.markdown("### 📊 Métricas del Sistema")
    
    if rol_usuario.lower() == 'administrador':
        # Métricas para administrador
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Total Usuarios", "150")
        with col2:
            st.metric("👨‍🏫 Profesores", "25")
        with col3:
            st.metric("👨‍🎓 Estudiantes", "125")
        with col4:
            st.metric("📚 Formaciones", "89")
            
        st.markdown("---")
        
        # Acceso rápido a módulos
        st.markdown("### 🚀 Acceso Rápido a Módulos")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("👥 Gestionar Usuarios", use_container_width=True):
                st.session_state['modulo_actual'] = '👥 Usuarios'
                st.rerun()
                
        with col2:
            if st.button("📚 Formación Complementaria", use_container_width=True):
                st.session_state['modulo_actual'] = '📚 Formación Complementaria'
                st.rerun()
                
        with col3:
            if st.button("⚙️ Configuración", use_container_width=True):
                st.session_state['modulo_actual'] = '⚙️ Configuración'
                st.rerun()
    
    elif rol_usuario.lower() == 'profesor':
        # Métricas para profesor
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("👨‍🎓 Estudiantes", "45")
        with col2:
            st.metric("📚 Cursos Activos", "12")
        with col3:
            st.metric("📊 Reportes", "8")
            
        st.markdown("---")
        
        # Acceso rápido a módulos
        st.markdown("### 🚀 Acceso Rápido a Módulos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👨‍🎓 Mis Estudiantes", use_container_width=True):
                st.session_state['modulo_actual'] = '👨‍🎓 Estudiantes'
                st.rerun()
                
        with col2:
            if st.button("📚 Formación Complementaria", use_container_width=True):
                st.session_state['modulo_actual'] = '📚 Formación Complementaria'
                st.rerun()
    
    elif rol_usuario.lower() == 'estudiante':
        # Métricas para estudiante
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📚 Cursos Inscritos", "6")
        with col2:
            st.metric("📊 Progreso", "75%")
        with col3:
            st.metric("📁 Documentos", "24")
            
        st.markdown("---")
        
        # Acceso rápido a módulos
        st.markdown("### 🚀 Acceso Rápido a Módulos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📚 Mi Formación", use_container_width=True):
                st.session_state['modulo_actual'] = '📚 Formación Complementaria'
                st.rerun()
                
        with col2:
            if st.button("📁 Mis Documentos", use_container_width=True):
                st.session_state['modulo_actual'] = '📁 Mis Documentos'
                st.rerun()
    
    else:
        st.warning("⚠️ Rol no reconocido")
        st.info("🔍 Contacte al administrador del sistema")
    
    # Actividad reciente (común para todos)
    st.markdown("---")
    st.markdown("### 📈 Actividad Reciente del Sistema")
    
    actividad_reciente = [
        {"usuario": "Juan Pérez", "accion": "Inició sesión", "hora": "Hace 5 min"},
        {"usuario": "María García", "accion": "Subió documento", "hora": "Hace 12 min"},
        {"usuario": "Carlos López", "accion": "Completó formación", "hora": "Hace 25 min"},
        {"usuario": "Ana Martínez", "accion": "Generó reporte", "hora": "Hace 1 hora"}
    ]
    
    for actividad in actividad_reciente:
        with st.expander(f"🔍 {actividad['usuario']} - {actividad['accion']}"):
            st.write(f"**Usuario:** {actividad['usuario']}")
            st.write(f"**Acción:** {actividad['accion']}")
            st.write(f"**Hora:** {actividad['hora']}")
    
    # Footer informativo
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        🎓 SICADFOC 2026 - Sistema de Gestión Académica<br>
        <em>Panel de control principal</em>
    </div>
    """, unsafe_allow_html=True)

def mostrar_gestion_usuarios():
    """Muestra el módulo de gestión de usuarios con estilo unificado"""
    st.markdown("## 👥 Gestión de Usuarios")
    st.markdown("---")
    
    # Tabs para diferentes funciones
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Usuarios", "✅ Aprobaciones", "➕ Nuevo Usuario"])
    
    with tab1:
        st.markdown("### 📋 Lista de Usuarios Registrados")
        
        # Datos de usuarios con estado
        usuarios = [
            {"nombre": "Juan Pérez", "email": "juan@iujo.edu", "rol": "Estudiante", "cedula": "V-12345678", "estado": "✅ Activo"},
            {"nombre": "María García", "email": "maria@iujo.edu", "rol": "Profesor", "cedula": "V-87654321", "estado": "✅ Activo"},
            {"nombre": "Carlos López", "email": "carlos@iujo.edu", "rol": "Administrador", "cedula": "V-45678912", "estado": "⏳ Por aprobar"}
        ]
        
        # Tabla compacta con estilo unificado
        st.markdown("""
        <style>
        .tabla-usuarios {
            background-color: rgba(30, 41, 59, 0.9);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        .tabla-usuarios table {
            width: 100%;
            border-collapse: collapse;
            color: #f1f5f9;
        }
        .tabla-usuarios th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9rem;
            border: none;
        }
        .tabla-usuarios td {
            padding: 10px 12px;
            border-bottom: 1px solid rgba(71, 85, 105, 0.3);
            vertical-align: middle;
        }
        .tabla-usuarios tr:last-child td {
            border-bottom: none;
        }
        .tabla-usuarios tr:hover {
            background-color: rgba(71, 85, 105, 0.3);
        }
        .badge-activo {
            background-color: #10b981;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .badge-pendiente {
            background-color: #f59e0b;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .btn-accion {
            background-color: rgba(51, 65, 85, 0.8);
            border: 1px solid rgba(71, 85, 105, 0.3);
            color: #f1f5f9;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 0 2px;
        }
        .btn-accion:hover {
            background-color: rgba(71, 85, 105, 0.9);
            transform: translateY(-1px);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Construir tabla HTML
        tabla_html = """
        <div class="tabla-usuarios">
            <table>
                <thead>
                    <tr>
                        <th>👤 Nombre</th>
                        <th>📧 Email</th>
                        <th>🎓 Rol</th>
                        <th>🆔 Cédula</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, usuario in enumerate(usuarios):
            estado_class = "badge-activo" if "Activo" in usuario['estado'] else "badge-pendiente"
            tabla_html += f"""
                    <tr>
                        <td>{usuario['nombre']}</td>
                        <td>{usuario['email']}</td>
                        <td>{usuario['rol']}</td>
                        <td>{usuario['cedula']}</td>
                        <td><span class="{estado_class}">{usuario['estado']}</span></td>
                        <td>
                            <button class="btn-accion" onclick="alert('Editando {usuario['nombre']}')">✏️</button>
                            <button class="btn-accion" onclick="alert('Eliminando {usuario['nombre']}')">🗑️</button>
                        </td>
                    </tr>
            """
        
        tabla_html += """
                </tbody>
            </table>
        </div>
        """
        
        st.markdown(tabla_html, unsafe_allow_html=True)
        
        # Botones ocultos para la funcionalidad real
        for i, usuario in enumerate(usuarios):
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"Editar {usuario['nombre']}", key=f"editar_user_{i}"):
                    st.info(f"✏️ Editando {usuario['nombre']}")
            with col2:
                if st.button(f"Eliminar {usuario['nombre']}", key=f"eliminar_user_{i}"):
                    st.warning(f"🗑️ Eliminando {usuario['nombre']}")
    
    with tab2:
        st.markdown("### ✅ Usuarios por Aprobar (Captcha Validados)")
        st.warning("🔍 Usuarios que completaron el captcha y esperan aprobación")
        
        # Lista de usuarios por aprobar
        por_aprobar = [
            {"nombre": "Ana Martínez", "cedula": "V-12345678", "email": "ana@iujo.edu"},
            {"nombre": "Luis Rodríguez", "cedula": "V-87654321", "email": "luis@iujo.edu"}
        ]
        
        # Tabla compacta para usuarios por aprobar
        st.markdown("""
        <style>
        .tabla-aprobaciones {
            background-color: rgba(30, 41, 59, 0.9);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        .tabla-aprobaciones table {
            width: 100%;
            border-collapse: collapse;
            color: #f1f5f9;
        }
        .tabla-aprobaciones th {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9rem;
            border: none;
        }
        .tabla-aprobaciones td {
            padding: 10px 12px;
            border-bottom: 1px solid rgba(71, 85, 105, 0.3);
            vertical-align: middle;
        }
        .tabla-aprobaciones tr:last-child td {
            border-bottom: none;
        }
        .tabla-aprobaciones tr:hover {
            background-color: rgba(71, 85, 105, 0.3);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Construir tabla HTML para aprobaciones
        tabla_aprob_html = """
        <div class="tabla-aprobaciones">
            <table>
                <thead>
                    <tr>
                        <th>👤 Nombre</th>
                        <th>🆔 Cédula</th>
                        <th>📧 Email</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for usuario in por_aprobar:
            tabla_aprob_html += f"""
                    <tr>
                        <td>{usuario['nombre']}</td>
                        <td>{usuario['cedula']}</td>
                        <td>{usuario['email']}</td>
                        <td>
                            <button class="btn-accion" onclick="alert('Aprobando {usuario['nombre']}')">✅</button>
                            <button class="btn-accion" onclick="alert('Rechazando {usuario['nombre']}')">❌</button>
                        </td>
                    </tr>
            """
        
        tabla_aprob_html += """
                </tbody>
            </table>
        </div>
        """
        
        st.markdown(tabla_aprob_html, unsafe_allow_html=True)
        
        # Botones ocultos para la funcionalidad real
        for usuario in por_aprobar:
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"Aprobar {usuario['nombre']}", key=f"aprobar_{usuario['cedula']}"):
                    st.success(f"✅ {usuario['nombre']} aprobado exitosamente")
            with col2:
                if st.button(f"Rechazar {usuario['nombre']}", key=f"rechazar_{usuario['cedula']}"):
                    st.error(f"❌ {usuario['nombre']} rechazado")
    
    with tab3:
        st.markdown("### ➕ Crear Nuevo Usuario")
        with st.form("crear_usuario"):
            nombre = st.text_input("👤 Nombre Completo")
            email = st.text_input("📧 Email")
            cedula = st.text_input("🆔 Cédula")
            rol = st.selectbox("🎓 Rol", ["Estudiante", "Profesor", "Administrador"])
            
            if st.form_submit_button("🚀 Crear Usuario"):
                st.success(f"✅ Usuario {nombre} creado exitosamente")

def mostrar_carga_pdf():
    """Muestra el módulo de carga de archivos PDF"""
    st.markdown("## 📁 Carga de PDF")
    st.markdown("---")
    
    # Área de carga
    uploaded_files = st.file_uploader(
        "📤 Subir archivos PDF",
        type=['pdf'],
        accept_multiple_files=True,
        help="Seleccione uno o más archivos PDF para digitalizar"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} archivo(s) seleccionado(s)")
        
        for file in uploaded_files:
            with st.expander(f"📄 {file.name}"):
                st.write(f"📏 Tamaño: {file.size / 1024:.2f} KB")
                st.write(f"📅 Fecha: {file.get('lastModified', 'N/A')}")
                
                # Botones de acción
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"🔍 Procesar {file.name}", key=f"procesar_{file.name}"):
                        st.success(f"✅ {file.name} procesado exitosamente")
                with col2:
                    if st.button(f"👀 Vista Previa {file.name}", key=f"vista_{file.name}"):
                        st.info(f"👀 Vista previa de {file.name}")
                with col3:
                    if st.button(f"🗑️ Eliminar {file.name}", key=f"eliminar_{file.name}"):
                        st.error(f"🗑️ {file.name} eliminado")
    
    # Archivos existentes
    st.markdown("---")
    st.markdown("### 📚 Archivos Existentes")
    
    archivos_existentes = [
        {"nombre": "documento1.pdf", "fecha": "2024-01-15", "estado": "✅ Procesado"},
        {"nombre": "reporte_anual.pdf", "fecha": "2024-01-20", "estado": "🔍 Procesando"},
        {"nombre": "manual_usuario.pdf", "fecha": "2024-01-25", "estado": "⏳ Pendiente"}
    ]
    
    for archivo in archivos_existentes:
        with st.expander(f"📄 {archivo['nombre']}"):
            st.write(f"📅 Fecha: {archivo['fecha']}")
            st.write(f"📊 Estado: {archivo['estado']}")

def mostrar_reportes():
    """Muestra el módulo de reportes con estilo unificado"""
    st.markdown("## 📊 Reportes")
    st.markdown("---")
    
    # Pestañas para diferentes tipos de reportes
    tab1, tab2, tab3 = st.tabs(["📈 Estadísticas", "👥 Usuarios", "📚 Actividad Académica"])
    
    with tab1:
        st.subheader("📈 Estadísticas Generales")
        
        # Métricas principales con estilo unificado
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="curso-card" style="text-align: center;">
                <h3 style="color: #f1f5f9; margin: 0;">👥 Total Usuarios</h3>
                <p style="font-size: 2rem; color: #10b981; margin: 10px 0;">150</p>
                <p style="color: #10b981; margin: 0;">+12%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="curso-card" style="text-align: center;">
                <h3 style="color: #f1f5f9; margin: 0;">📚 Cursos Activos</h3>
                <p style="font-size: 2rem; color: #10b981; margin: 10px 0;">45</p>
                <p style="color: #10b981; margin: 0;">+5%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="curso-card" style="text-align: center;">
                <h3 style="color: #f1f5f9; margin: 0;">🎓 Graduados</h3>
                <p style="font-size: 2rem; color: #10b981; margin: 10px 0;">89</p>
                <p style="color: #10b981; margin: 0;">+8%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="curso-card" style="text-align: center;">
                <h3 style="color: #f1f5f9; margin: 0;">📊 Tasa de Éxito</h3>
                <p style="font-size: 2rem; color: #10b981; margin: 10px 0;">94%</p>
                <p style="color: #10b981; margin: 0;">+2%</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Tabla de tendencias con estilo unificado
        st.subheader("� Tendencias del Sistema")
        
        tendencias = [
            {"indicador": "Inscripciones", "valor": "+15%", "estado": "✅ Positivo"},
            {"indicador": "Cursos Virtuales", "valor": "+20%", "estado": "✅ Positivo"},
            {"indicador": "Tasa Aprobación", "valor": "+10%", "estado": "✅ Positivo"},
            {"indicador": "Usuarios Activos", "valor": "+8%", "estado": "✅ Positivo"}
        ]
        
        for tendencia in tendencias:
            st.markdown(f"""
            <div class="curso-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="color: #f1f5f9; margin: 0;">📊 {tendencia['indicador']}</h4>
                        <p style="color: #cbd5e1; margin: 5px 0;">Crecimiento mensual</p>
                    </div>
                    <div style="text-align: right;">
                        <p style="color: #10b981; font-size: 1.2rem; font-weight: bold; margin: 0;">{tendencia['valor']}</p>
                        <span style="color: #10b981; font-weight: bold;">{tendencia['estado']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("👥 Reportes de Usuarios")
        
        # Filtros con estilo unificado
        col1, col2 = st.columns(2)
        with col1:
            rol_filtro = st.selectbox("Filtrar por Rol", ["Todos", "Estudiante", "Profesor", "Administrador"])
        
        with col2:
            estado_filtro = st.selectbox("Filtrar por Estado", ["Todos", "Activo", "Inactivo"])
        
        if st.button("🔍 Aplicar Filtros", use_container_width=True):
            st.success(f"✅ Filtros aplicados: {rol_filtro}, {estado_filtro}")
        
        st.markdown("---")
        
        # Tabla compacta para reportes de usuarios
        st.markdown("""
        <style>
        .tabla-reportes {
            background-color: rgba(30, 41, 59, 0.9);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        .tabla-reportes table {
            width: 100%;
            border-collapse: collapse;
            color: #f1f5f9;
        }
        .tabla-reportes th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9rem;
            border: none;
        }
        .tabla-reportes td {
            padding: 10px 12px;
            border-bottom: 1px solid rgba(71, 85, 105, 0.3);
            vertical-align: middle;
        }
        .tabla-reportes tr:last-child td {
            border-bottom: none;
        }
        .tabla-reportes tr:hover {
            background-color: rgba(71, 85, 105, 0.3);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Construir tabla HTML para reportes
        tabla_reporte_html = """
        <div class="tabla-reportes">
            <table>
                <thead>
                    <tr>
                        <th>👤 Nombre</th>
                        <th>🎓 Rol</th>
                        <th>Estado</th>
                        <th>📅 Último Acceso</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, usuario in enumerate(usuarios_reporte):
            tabla_reporte_html += f"""
                    <tr>
                        <td>{usuario['nombre']}</td>
                        <td>{usuario['rol']}</td>
                        <td><span class="badge-activo">{usuario['estado']}</span></td>
                        <td>{usuario['ultimo_acceso']}</td>
                        <td>
                            <button class="btn-accion" onclick="alert('Detalles de {usuario['nombre']}')">📈</button>
                            <button class="btn-accion" onclick="alert('Reporte de {usuario['nombre']}')">📊</button>
                        </td>
                    </tr>
            """
        
        tabla_reporte_html += """
                </tbody>
            </table>
        </div>
        """
        
        st.markdown(tabla_reporte_html, unsafe_allow_html=True)
        
        # Botones ocultos para la funcionalidad real
        for i, usuario in enumerate(usuarios_reporte):
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"Detalles {usuario['nombre']}", key=f"detalles_user_{i}"):
                    st.info(f"📈 Viendo detalles de {usuario['nombre']}")
            with col2:
                if st.button(f"Reporte {usuario['nombre']}", key=f"reporte_user_{i}"):
                    st.success(f"📊 Reporte generado para {usuario['nombre']}")
            
            st.markdown("---")
    
    with tab3:
        st.subheader("📚 Actividad Académica")
        
        # Estadísticas por curso con estilo unificado
        cursos_stats = [
            {"curso": "Python Avanzado", "inscritos": 45, "aprobados": 42, "tasa": "93%", "profesor": "Ing. López"},
            {"curso": "Machine Learning", "inscritos": 38, "aprobados": 35, "tasa": "92%", "profesor": "Dr. Pérez"},
            {"curso": "Web Development", "inscritos": 52, "aprobados": 48, "tasa": "92%", "profesor": "Dra. García"}
        ]
        
        for i, curso in enumerate(cursos_stats):
            st.markdown(f"""
            <div class="curso-card">
                <h4 style="color: #f1f5f9; margin: 0;">📚 {curso['curso']}</h4>
                <p style="color: #cbd5e1; margin: 5px 0;">�‍🏫 Profesor: {curso['profesor']}</p>
                
                <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                    <div style="text-align: center;">
                        <p style="color: #cbd5e1; margin: 0; font-size: 0.9rem;">Inscritos</p>
                        <p style="color: #f1f5f9; font-weight: bold; margin: 0;">{curso['inscritos']}</p>
                    </div>
                    <div style="text-align: center;">
                        <p style="color: #cbd5e1; margin: 0; font-size: 0.9rem;">Aprobados</p>
                        <p style="color: #10b981; font-weight: bold; margin: 0;">{curso['aprobados']}</p>
                    </div>
                    <div style="text-align: center;">
                        <p style="color: #cbd5e1; margin: 0; font-size: 0.9rem;">Tasa</p>
                        <p style="color: #10b981; font-weight: bold; margin: 0;">{curso['tasa']}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Botones de acción
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"📈 Ver Estadísticas", key=f"stats_curso_{i}", use_container_width=True):
                    st.info(f"� Estadísticas de {curso['curso']}")
            with col2:
                if st.button(f"📊 Reporte Completo", key=f"reporte_curso_{i}", use_container_width=True):
                    st.success(f"📊 Reporte generado para {curso['curso']}")
            
            st.markdown("---")

def mostrar_configuracion():
    """Muestra el módulo de configuración del sistema"""
    st.markdown("## ⚙️ Configuración")
    st.markdown("---")
    
    # Tabs de configuración (simplificado - eliminada pestaña Correo)
    tab1, tab2 = st.tabs(["🔧 General", "🔒 Seguridad"])
    
    with tab1:
        st.markdown("### 🔧 Configuración General")
        
        # Configuración básica
        nombre_sistema = st.text_input("🏷️ Nombre del Sistema", value="SICADFOC 2026")
        version = st.text_input("📦 Versión", value="1.0.0")
        modo_mantenimiento = st.checkbox("🔧 Modo Mantenimiento")
        
        if st.button("💾 Guardar Configuración General"):
            st.success("✅ Configuración guardada exitosamente")
    
    with tab2:
        st.markdown("###  Configuración de Seguridad")
        
        # Política de contraseñas
        longitud_minima = st.number_input("📏 Longitud Mínima de Contraseña", value=8)
        requerir_mayusculas = st.checkbox("🔤 Requerir Mayúsculas")
        requerir_numeros = st.checkbox("🔢 Requerir Números")
        requerir_especiales = st.checkbox("🌟 Requerir Caracteres Especiales")
        
        # Configuración de sesión
        tiempo_sesion = st.number_input("⏰ Tiempo de Sesión (minutos)", value=120)
        intentos_login = st.number_input("🚫 Intentos Máximos de Login", value=3)
        
        if st.button("🔒 Guardar Configuración de Seguridad"):
            st.success("✅ Configuración de seguridad guardada")

def mostrar_mis_documentos():
    """Muestra los documentos del estudiante"""
    st.markdown("## 📁 Mis Documentos")
    st.markdown("---")
    
    st.info("📚 Aquí puedes ver y gestionar tus documentos personales")
    
    # Documentos del estudiante
    documentos_estudiante = [
        {"nombre": "Acta de Notas", "fecha": "2024-01-15", "tipo": "Académico"},
        {"nombre": "Certificado de Estudio", "fecha": "2024-01-20", "tipo": "Oficial"},
        {"nombre": "Constancia de Inscripción", "fecha": "2024-01-25", "tipo": "Administrativo"}
    ]
    
    for doc in documentos_estudiante:
        with st.expander(f"📄 {doc['nombre']}"):
            st.write(f"📅 Fecha: {doc['fecha']}")
            st.write(f"🏷️ Tipo: {doc['tipo']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"👀 Ver {doc['nombre']}", key=f"ver_{doc['nombre']}"):
                    st.info(f"👀 Visualizando {doc['nombre']}")
            with col2:
                if st.button(f"📥 Descargar {doc['nombre']}", key=f"descargar_{doc['nombre']}"):
                    st.success(f"📥 Descargando {doc['nombre']}")

def mostrar_mi_progreso():
    """Muestra el progreso académico del estudiante"""
    st.markdown("## 📊 Mi Progreso")
    st.markdown("---")
    
    # Métricas académicas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Materias Aprobadas", "24")
    with col2:
        st.metric("📈 Promedio", "8.5")
    with col3:
        st.metric("⏰ Créditos", "180")
    with col4:
        st.metric("🎯 Semestre", "6to")
    
    st.markdown("---")
    
    # Gráfico de progreso
    st.markdown("### 📈 Progreso Académico")
    
    progreso_data = {
        'Semestre': ['1ro', '2do', '3ro', '4to', '5to', '6to'],
        'Promedio': [7.5, 8.0, 8.2, 8.3, 8.4, 8.5],
        'Créditos Acumulados': [30, 60, 90, 120, 150, 180]
    }
    
    st.dataframe(pd.DataFrame(progreso_data))
    
    # Materias actuales
    st.markdown("---")
    st.markdown("### 📚 Materias Actuales")
    
    materias_actuales = [
        {"nombre": "Matemáticas Avanzadas", "profesor": "Dr. Pérez", "nota": "8.0"},
        {"nombre": "Física Cuántica", "profesor": "Dra. García", "nota": "9.0"},
        {"nombre": "Programación Web", "profesor": "Ing. López", "nota": "8.5"}
    ]
    
    for materia in materias_actuales:
        with st.expander(f"📖 {materia['nombre']}"):
            st.write(f"👨‍🏫 Profesor: {materia['profesor']}")
            st.write(f"📊 Nota: {materia['nota']}")

def mostrar_gestion_profesores():
    """Muestra el módulo de gestión de profesores con estilo unificado"""
    st.markdown("## 👨‍🏫 Profesores")
    st.markdown("---")
    
    # Pestañas principales con coherencia
    tab_lista, tab_aprobaciones, tab_cargas = st.tabs(["📋 Lista de Profesores", "✅ Aprobaciones", "📁 Cargas Académicas"])
    
    with tab1:
        st.markdown("### 📋 Lista de Profesores Registrados")
        
        # Datos de ejemplo con estado
        profesores = [
            {"nombre": "Dr. Juan Pérez", "cedula": "V-12345678", "departamento": "Matemáticas", "email": "jperez@iujo.edu", "estado": "✅ Activo"},
            {"nombre": "Dra. María García", "cedula": "V-87654321", "departamento": "Física", "email": "mgarcia@iujo.edu", "estado": "✅ Activo"},
            {"nombre": "Ing. Carlos López", "cedula": "V-45678912", "departamento": "Computación", "email": "clopez@iujo.edu", "estado": "⏳ Por aprobar"}
        ]
        
        # Tabla compacta para profesores
        st.markdown("""
        <style>
        .tabla-profesores {
            background-color: rgba(30, 41, 59, 0.9);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        .tabla-profesores table {
            width: 100%;
            border-collapse: collapse;
            color: #f1f5f9;
        }
        .tabla-profesores th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9rem;
            border: none;
        }
        .tabla-profesores td {
            padding: 10px 12px;
            border-bottom: 1px solid rgba(71, 85, 105, 0.3);
            vertical-align: middle;
        }
        .tabla-profesores tr:last-child td {
            border-bottom: none;
        }
        .tabla-profesores tr:hover {
            background-color: rgba(71, 85, 105, 0.3);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Construir tabla HTML para profesores
        tabla_profesores_html = """
        <div class="tabla-profesores">
            <table>
                <thead>
                    <tr>
                        <th>👤 Nombre</th>
                        <th>📧 Email</th>
                        <th>🏢 Departamento</th>
                        <th>🆔 Cédula</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, prof in enumerate(profesores):
            estado_class = "badge-activo" if "Activo" in prof['estado'] else "badge-pendiente"
            tabla_profesores_html += f"""
                    <tr>
                        <td>{prof['nombre']}</td>
                        <td>{prof['email']}</td>
                        <td>{prof['departamento']}</td>
                        <td>{prof['cedula']}</td>
                        <td><span class="{estado_class}">{prof['estado']}</span></td>
                        <td>
                            <button class="btn-accion" onclick="alert('Editando {prof['nombre']}')">✏️</button>
                            <button class="btn-accion" onclick="alert('Eliminando {prof['nombre']}')">🗑️</button>
                        </td>
                    </tr>
            """
        
        tabla_profesores_html += """
                </tbody>
            </table>
        </div>
        """
        
        st.markdown(tabla_profesores_html, unsafe_allow_html=True)
        
        # Botones ocultos para la funcionalidad real
        for i, prof in enumerate(profesores):
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"Editar {prof['nombre']}", key=f"editar_prof_{i}"):
                    st.info(f"✏️ Editando {prof['nombre']}")
            with col2:
                if st.button(f"Eliminar {prof['nombre']}", key=f"eliminar_prof_{i}"):
                    st.warning(f"🗑️ Eliminando {prof['nombre']}")
            
            st.markdown("---")
    
    with tab_aprobaciones:
        st.markdown("### ✅ Profesores por Aprobar")
        st.warning("🔍 Profesores que completaron el registro y esperan aprobación")
        
        # Lista de profesores por aprobar
        por_aprobar = [
            {"nombre": "Dr. Ana Martínez", "cedula": "V-98765432", "departamento": "Química", "email": "amartinez@iujo.edu"},
            {"nombre": "Ing. Luis Rodríguez", "cedula": "V-13579246", "departamento": "Biología", "email": "lrodriguez@iujo.edu"}
        ]
        
        for prof in por_aprobar:
            st.markdown(f"""
            <div class="curso-card">
                <h4 style="color: #f1f5f9; margin: 0;">👨‍🏫 {prof['nombre']}</h4>
                <p style="color: #cbd5e1; margin: 5px 0;">🆔 {prof['cedula']}</p>
                <p style="color: #cbd5e1; margin: 5px 0;">📧 {prof['email']}</p>
                <p style="color: #cbd5e1; margin: 5px 0;">🏢 {prof['departamento']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ Aprobar {prof['nombre']}", key=f"aprobar_prof_{prof['cedula']}", use_container_width=True):
                    st.success(f"✅ {prof['nombre']} aprobado exitosamente")
            with col2:
                if st.button(f"❌ Rechazar {prof['nombre']}", key=f"rechazar_prof_{prof['cedula']}", use_container_width=True):
                    st.error(f"❌ {prof['nombre']} rechazado")
            
            st.markdown("---")
    
    with tab3:
        st.markdown("### ➕ Agregar Nuevo Profesor")
        with st.form("form_profesor"):
            nombre = st.text_input("👤 Nombre Completo")
            cedula = st.text_input("🆔 Cédula")
            departamento = st.selectbox("🏢 Departamento", ["Matemáticas", "Física", "Computación", "Química", "Biología"])
            email = st.text_input("📧 Email Institucional")
            
            if st.form_submit_button("🚀 Agregar Profesor"):
                st.success(f"✅ Profesor {nombre} agregado exitosamente")
    
    with tab_cargas:
        # Mostrar opciones de carga
        mostrar_opciones_carga()

def mostrar_gestion_estudiantes():
    """Muestra el módulo de gestión de estudiantes con estilo unificado"""
    st.markdown("## 👨‍🎓 Estudiantes")
    st.markdown("---")
    
    # Pestañas principales con coherencia
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Estudiantes", "✅ Aprobaciones", "📁 Cargas Académicas"])
    
    with tab1:
        st.markdown("### 📋 Lista de Estudiantes Registrados")
        
        # Datos de ejemplo con estado
        estudiantes = [
            {"nombre": "Ana Martínez", "cedula": "V-23456789", "carrera": "Ingeniería", "semestre": "6to", "email": "amartinez@iujo.edu", "promedio": "8.5", "estado": "✅ Activo"},
            {"nombre": "Luis Rodríguez", "cedula": "V-34567890", "carrera": "Matemáticas", "semestre": "4to", "email": "lrodriguez@iujo.edu", "promedio": "9.0", "estado": "✅ Activo"},
            {"nombre": "Sofía Hernández", "cedula": "V-45678901", "carrera": "Física", "semestre": "5to", "email": "shernandez@iujo.edu", "promedio": "8.8", "estado": "⏳ Por aprobar"}
        ]
        
        # Tabla con estilo unificado como Usuarios
        for i, est in enumerate(estudiantes):
            st.markdown(f"""
            <div class="curso-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0; color: #f1f5f9;">👨‍🎓 {est['nombre']}</h4>
                        <p style="margin: 5px 0; color: #cbd5e1;">🆔 {est['cedula']}</p>
                        <p style="margin: 5px 0; color: #cbd5e1;">📧 {est['email']}</p>
                        <p style="margin: 5px 0; color: #cbd5e1;">🎓 {est['carrera']} - {est['semestre']}</p>
                        <p style="margin: 5px 0; color: #cbd5e1;">� Promedio: {est['promedio']}</p>
                    </div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="color: #10b981; font-weight: bold;">{est['estado']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Botones de acción como en Usuarios
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✏️ Editar", key=f"editar_est_{i}", use_container_width=True):
                    st.info(f"✏️ Editando {est['nombre']}")
            with col2:
                if st.button(f"🗑️ Eliminar", key=f"eliminar_est_{i}", use_container_width=True):
                    st.warning(f"🗑️ Eliminando {est['nombre']}")
            
            st.markdown("---")
    
    with tab2:
        st.markdown("### ✅ Estudiantes por Aprobar")
        st.warning("� Estudiantes que completaron el registro y esperan aprobación")
        
        # Lista de estudiantes por aprobar
        por_aprobar = [
            {"nombre": "Carlos López", "cedula": "V-56789012", "carrera": "Química", "semestre": "3ro", "email": "clopez@iujo.edu"},
            {"nombre": "María González", "cedula": "V-67890123", "carrera": "Biología", "semestre": "2do", "email": "mgonzalez@iujo.edu"}
        ]
        
        for est in por_aprobar:
            st.markdown(f"""
            <div class="curso-card">
                <h4 style="color: #f1f5f9; margin: 0;">👨‍🎓 {est['nombre']}</h4>
                <p style="color: #cbd5e1; margin: 5px 0;">🆔 {est['cedula']}</p>
                <p style="color: #cbd5e1; margin: 5px 0;">📧 {est['email']}</p>
                <p style="color: #cbd5e1; margin: 5px 0;">🎓 {est['carrera']} - {est['semestre']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ Aprobar {est['nombre']}", key=f"aprobar_est_{est['cedula']}", use_container_width=True):
                    st.success(f"✅ {est['nombre']} aprobado exitosamente")
            with col2:
                if st.button(f"❌ Rechazar {est['nombre']}", key=f"rechazar_est_{est['cedula']}", use_container_width=True):
                    st.error(f"❌ {est['nombre']} rechazado")
            
            st.markdown("---")
    
    with tab3:
        st.markdown("### ➕ Agregar Nuevo Estudiante")
        with st.form("form_estudiante"):
            nombre = st.text_input("👤 Nombre Completo")
            cedula = st.text_input("🆔 Cédula")
            carrera = st.selectbox("🎓 Carrera", ["Ingeniería", "Matemáticas", "Física", "Química", "Biología"])
            semestre = st.selectbox("📚 Semestre", ["1ro", "2do", "3ro", "4to", "5to", "6to", "7mo", "8vo", "9no", "10mo"])
            email = st.text_input("📧 Email Personal")
            
            if st.form_submit_button("🚀 Agregar Estudiante"):
                st.success(f"✅ Estudiante {nombre} agregado exitosamente")
    
    with tab_cargas:
        # Mostrar opciones de carga
        mostrar_opciones_carga()

def mostrar_formacion_complementaria():
    """Muestra el módulo de formación complementaria"""
    st.markdown("## 📚 Formación Complementaria")
    st.markdown("---")
    
    # Pestañas para diferentes secciones
    tab1, tab2, tab3, tab4 = st.tabs(["📖 Cursos", "🏆 Certificaciones", "📅 Eventos", "📁 Gestión de Documentos"])
    
    with tab1:
        st.subheader("📖 Cursos Disponibles")
        
        cursos = [
            {"nombre": "Python Avanzado", "duracion": "40 horas", "modalidad": "Virtual", "profesor": "Ing. López"},
            {"nombre": "Machine Learning", "duracion": "60 horas", "modalidad": "Híbrida", "profesor": "Dr. Pérez"},
            {"nombre": "Web Development", "duracion": "45 horas", "modalidad": "Presencial", "profesor": "Dra. García"}
        ]
        
        # Vista de tarjetas con diseño mejorado
        cols = st.columns(3)
        for i, curso in enumerate(cursos):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="curso-card">
                    <h4>📚 {curso['nombre']}</h4>
                    <p>⏱️ Duración: {curso['duracion']}</p>
                    <p>🏢 Modalidad: {curso['modalidad']}</p>
                    <p>👨‍🏫 Profesor: {curso['profesor']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"📝 Inscribirse", key=f"inscribir_{curso['nombre']}", use_container_width=True):
                    st.success(f"✅ Inscrito en {curso['nombre']}")
    
    with tab2:
        st.subheader("🏆 Certificaciones")
        
        certificaciones = [
            {"nombre": "CCNA", "fecha": "2024-01-15", "estado": "Vigente"},
            {"nombre": "AWS Cloud Practitioner", "fecha": "2024-03-20", "estado": "Vigente"},
            {"nombre": "Scrum Master", "fecha": "2023-11-10", "estado": "Por Renovar"}
        ]
        
        # Vista de tarjetas con diseño mejorado
        cols = st.columns(3)
        for i, cert in enumerate(certificaciones):
            with cols[i % 3]:
                color_estado = "🟢" if cert['estado'] == "Vigente" else "🟡"
                st.markdown(f"""
                <div class="curso-card">
                    <h4>🏆 {cert['nombre']}</h4>
                    <p>📅 Fecha: {cert['fecha']}</p>
                    <p><strong>{color_estado} {cert['estado']}</strong></p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        st.subheader("📅 Próximos Eventos")
        
        eventos = [
            {"nombre": "Hackathon IUJO 2026", "fecha": "2026-04-15", "tipo": "Competencia"},
            {"nombre": "Seminario de IA", "fecha": "2026-04-20", "tipo": "Seminario"},
            {"nombre": "Feria de Empleo", "fecha": "2026-04-25", "tipo": "Networking"}
        ]
        
        # Vista de tarjetas con diseño mejorado
        cols = st.columns(3)
        for i, evento in enumerate(eventos):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="curso-card">
                    <h4>📅 {evento['nombre']}</h4>
                    <p>📋 Tipo: {evento['tipo']}</p>
                    <p>🗓️ Fecha: {evento['fecha']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"📝 Registrarse", key=f"registro_{evento['nombre']}", use_container_width=True):
                    st.success(f"✅ Registrado en {evento['nombre']}")
    
    with tab4:
        # Mostrar opciones de carga
        mostrar_opciones_carga()

# =================================================================
# FUNCIONES DE DASHBOARD
# =================================================================

def mostrar_modulo_seleccionado():
    """Muestra el contenido del módulo seleccionado con estructura de tabs"""
    
    # Obtener módulo actual
    modulo_actual = st.session_state.get('modulo_actual', '🏠 Dashboard Principal')
    
    # Mapeo de módulos a funciones locales con tabs
    modulos_funciones = {
        "👥 Usuarios": "mostrar_gestion_usuarios",
        "👨‍🏫 Profesores": "mostrar_gestion_profesores",
        "👨‍🎓 Estudiantes": "mostrar_gestion_estudiantes", 
        "📚 Formación Complementaria": "mostrar_formacion_complementaria",
        "📊 Reportes": "mostrar_reportes",
        "⚙️ Configuración": "mostrar_configuracion",
        "🏠 Dashboard Principal": "mostrar_dashboard_principal"
    }
    
    # Importar y ejecutar función correspondiente
    if modulo_actual in modulos_funciones:
        nombre_funcion = modulos_funciones[modulo_actual]
        
        # Ejecutar función local con tabs
        if nombre_funcion == "mostrar_dashboard_principal":
            mostrar_dashboard_principal()
        elif nombre_funcion == "mostrar_gestion_usuarios":
            mostrar_gestion_usuarios()
        elif nombre_funcion == "mostrar_gestion_profesores":
            mostrar_gestion_profesores()
        elif nombre_funcion == "mostrar_gestion_estudiantes":
            mostrar_gestion_estudiantes()
        elif nombre_funcion == "mostrar_formacion_complementaria":
            mostrar_formacion_complementaria()
        elif nombre_funcion == "mostrar_reportes":
            mostrar_reportes()
        elif nombre_funcion == "mostrar_configuracion":
            mostrar_configuracion()
        else:
            st.error(f"❌ Módulo '{modulo_actual}' no encontrado")
            st.info("🔍 Contacte al administrador del sistema")
    else:
        st.error(f"❌ Módulo '{modulo_actual}' no está disponible")
        st.info("🔍 Seleccione un módulo válido del menú lateral")

def mostrar_reportes():
    """Muestra el módulo de reportes con tabs"""
    st.markdown("## 📊 Reportes")
    st.markdown("---")
    
    # Pestañas para diferentes tipos de reportes
    tab1, tab2, tab3 = st.tabs(["📈 Estadísticas", "👥 Usuarios", "📚 Actividad Académica"])
    
    with tab1:
        st.subheader("📈 Estadísticas Generales")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Total Usuarios", "150", "+12%")
        with col2:
            st.metric("📚 Cursos Activos", "45", "+5%")
        with col3:
            st.metric("🎓 Graduados", "89", "+8%")
        with col4:
            st.metric("📊 Tasa de Éxito", "94%", "+2%")
        
        st.markdown("---")
        
        # Gráficos simulados
        st.subheader("📈 Tendencias")
        st.write("• Crecimiento del 15% en inscripciones")
        st.write("• Aumento del 20% en cursos virtuales")
        st.write("• Mejora del 10% en tasas de aprobación")
    
    with tab2:
        st.subheader("👥 Reportes de Usuarios")
        
        # Tabla de usuarios
        usuarios_data = {
            'Nombre': ['Juan Pérez', 'María García', 'Carlos López'],
            'Rol': ['Estudiante', 'Profesor', 'Administrador'],
            'Estado': ['Activo', 'Activo', 'Activo'],
            'Último Acceso': ['2024-03-30', '2024-03-31', '2024-03-31']
        }
        
        st.dataframe(pd.DataFrame(usuarios_data))
        
        # Filtros
        st.markdown("### 🔍 Filtros")
        col1, col2 = st.columns(2)
        
        with col1:
            rol_filtro = st.selectbox("Filtrar por Rol", ["Todos", "Estudiante", "Profesor", "Administrador"])
        
        with col2:
            estado_filtro = st.selectbox("Filtrar por Estado", ["Todos", "Activo", "Inactivo"])
        
        if st.button("🔍 Aplicar Filtros"):
            st.success(f"✅ Filtros aplicados: {rol_filtro}, {estado_filtro}")
    
    with tab3:
        st.subheader("📚 Actividad Académica")
        
        # Estadísticas por curso
        cursos_stats = [
            {"curso": "Python Avanzado", "inscritos": 45, "aprobados": 42, "tasa": "93%"},
            {"curso": "Machine Learning", "inscritos": 38, "aprobados": 35, "tasa": "92%"},
            {"curso": "Web Development", "inscritos": 52, "aprobados": 48, "tasa": "92%"}
        ]
        
        for curso in cursos_stats:
            with st.expander(f"📚 {curso['curso']}"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("👥 Inscritos", curso['inscritos'])
                with col2:
                    st.metric("✅ Aprobados", curso['aprobados'])
                with col3:
                    st.metric("📊 Tasa", curso['tasa'])
                with col4:
                    if st.button(f"📈 Detalles", key=f"detalles_{curso['curso']}"):
                        st.info(f"📈 Ver detalles de {curso['curso']}")

def mostrar_configuracion():
    """Muestra el módulo de configuración con tabs"""
    st.markdown("## ⚙️ Configuración")
    st.markdown("---")
    
    # Pestañas para diferentes secciones de configuración
    tab1, tab2, tab3, tab4 = st.tabs(["🔐 Seguridad", "📧 Correo", "🎨 Interfaz", "🌐 Sistema"])
    
    with tab1:
        st.subheader("🔐 Configuración de Seguridad")
        
        with st.form("form_seguridad"):
            st.write("**Políticas de Contraseña**")
            
            longitud_minima = st.number_input("Longitud Mínima", min_value=6, max_value=20, value=8)
            requerir_mayusculas = st.checkbox("Requerir Mayúsculas", value=True)
            requerir_numeros = st.checkbox("Requerir Números", value=True)
            requerir_especiales = st.checkbox("Requerir Caracteres Especiales", value=False)
            
            st.write("**Sesiones**")
            tiempo_sesion = st.number_input("Tiempo de Sesión (minutos)", min_value=15, max_value=480, value=120)
            
            submit_button = st.form_submit_button("💾 Guardar Configuración de Seguridad")
            
            if submit_button:
                st.success("✅ Configuración de seguridad guardada exitosamente")
    
    with tab2:
        st.subheader("📧 Configuración de Correo")
        
        with st.form("form_correo"):
            st.write("**Servidor SMTP**")
            
            smtp_server = st.text_input("Servidor SMTP", value="smtp.gmail.com")
            smtp_puerto = st.number_input("Puerto", min_value=1, max_value=65535, value=587)
            smtp_usuario = st.text_input("Usuario SMTP")
            smtp_password = st.text_input("Contraseña SMTP", type="password")
            
            st.write("**Configuración de Envío**")
            email_remitente = st.text_input("Email Remitente", value="noreply@iujo.edu.ve")
            nombre_remitente = st.text_input("Nombre Remitente", value="SICADFOC 2026")
            
            submit_button = st.form_submit_button("💾 Guardar Configuración de Correo")
            
            if submit_button:
                st.success("✅ Configuración de correo guardada exitosamente")
    
    with tab3:
        st.subheader("🎨 Configuración de Interfaz")
        
        with st.form("form_interfaz"):
            st.write("**Apariencia**")
            
            tema = st.selectbox("Tema", ["Claro", "Oscuro", "Automático"])
            idioma = st.selectbox("Idioma", ["Español", "Inglés"])
            
            st.write("**Notificaciones**")
            notificaciones_escritorio = st.checkbox("Notificaciones de Escritorio", value=True)
            sonido_alertas = st.checkbox("Sonido de Alertas", value=False)
            
            st.write("**Rendimiento**")
            cache_habilitado = st.checkbox("Habilitar Cache", value=True)
            
            if cache_habilitado:
                tiempo_cache = st.number_input("Tiempo de Cache (minutos)", min_value=5, max_value=120, value=30)
            
            submit_button = st.form_submit_button("💾 Guardar Configuración de Interfaz")
            
            if submit_button:
                st.success("✅ Configuración de interfaz guardada exitosamente")
                st.info("🔄 Algunos cambios pueden requerir recargar la página")
    
    with tab4:
        st.subheader("🌐 Configuración del Sistema")
        
        with st.form("form_sistema"):
            st.write("**Configuración General**")
            
            modo_mantenimiento = st.checkbox("Modo Mantenimiento")
            mensaje_mantenimiento = st.text_area("Mensaje de Mantenimiento", 
                                                value="Sistema en mantenimiento. Volvemos pronto.")
            
            st.write("**Copias de Seguridad**")
            backup_automatico = st.checkbox("Backup Automático", value=True)
            
            if backup_automatico:
                frecuencia_backup = st.selectbox("Frecuencia", ["Diario", "Semanal", "Mensual"])
                hora_backup = st.time_input("Hora de Backup", value=datetime.strptime("02:00", "%H:%M").time())
            
            st.write("**Límites del Sistema**")
            max_usuarios = st.number_input("Máximo de Usuarios", min_value=100, max_value=10000, value=1000)
            max_archivos = st.number_input("Tamaño Máximo de Archivos (MB)", min_value=1, max_value=100, value=50)
            
            submit_button = st.form_submit_button("💾 Guardar Configuración del Sistema")
            
            if submit_button:
                st.success("✅ Configuración del sistema guardada exitosamente")
                st.warning("⚠️ Algunos cambios requieren reiniciar el sistema")

def mostrar_banner_informativo():
    """Muestra información del sistema sin banner (eliminado)"""
    st.markdown("---")
    
    # Grid de información
    st.markdown("### 📊 Información del Sistema")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>👥 Estudiantes</h4>
            <h2>1,250</h2>
            <p style="color: #10b981;">↑ 12% este mes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h4>👨‍🏫 Profesores</h4>
            <h2>85</h2>
            <p style="color: #10b981;">↑ 5% este mes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-card">
            <h4>📚 Cursos</h4>
            <h2>45</h2>
            <p style="color: #f59e0b;">8 en progreso</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="info-card">
            <h4>📁 Documentos</h4>
            <h2>3,420</h2>
            <p style="color: #10b981;">↑ 23% esta semana</p>
        </div>
        """, unsafe_allow_html=True)

def mostrar_opciones_carga():
    """Muestra opciones de carga masiva e individual"""
    st.markdown("### 📁 Opciones de Carga")
    
    tab1, tab2 = st.tabs(["📤 Carga Masiva", "📝 Carga Individual"])
    
    with tab1:
        st.markdown("#### 📤 Carga Masiva de Archivos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_file = st.file_uploader(
                "📁 Seleccione archivo CSV/Excel",
                type=['csv', 'xlsx', 'xls'],
                help="Suba un archivo con múltiples registros"
            )
            
            if uploaded_file:
                st.success(f"✅ Archivo '{uploaded_file.name}' cargado")
                
                if st.button("🚀 Procesar Carga Masiva", type="primary"):
                    with st.spinner("Procesando archivo..."):
                        time.sleep(2)
                    st.success("✅ Carga masiva completada exitosamente")
                    st.balloons()
        
        with col2:
            st.markdown("#### 📋 Formato Requerido")
            st.markdown("""
            **Columnas requeridas:**
            - Nombre (texto)
            - Apellido (texto)
            - Cédula (número)
            - Email (email)
            - Rol (texto)
            
            **Formatos aceptados:**
            - CSV (.csv)
            - Excel (.xlsx, .xls)
            """)
    
    with tab2:
        st.markdown("#### 📝 Carga Individual de Registros")
        
        with st.form("form_carga_individual"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("👤 Nombre")
                apellido = st.text_input("👥 Apellido")
                cedula = st.text_input("🆔 Cédula")
            
            with col2:
                email = st.text_input("📧 Email")
                rol = st.selectbox("🎓 Rol", ["Estudiante", "Profesor", "Administrador"])
                telefono = st.text_input("📱 Teléfono (opcional)")
            
            if st.form_submit_button("🚀 Agregar Registro", type="primary"):
                if nombre and apellido and cedula and email:
                    st.success(f"✅ Registro de {nombre} {apellido} agregado")
                    st.balloons()
                else:
                    st.error("❌ Complete los campos obligatorios")
