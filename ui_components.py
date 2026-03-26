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
    " Reportes",
    "⚙️ Configuración"
]

# Módulos para Profesor
modulos_profesor = [
    "📚 Formación Complementaria",
    "�‍🎓 Estudiantes",
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
    """Muestra el menú lateral con navegación protegida y persistencia"""
    
    # DEBUG: Mostrar módulos disponibles
    rol_usuario = st.session_state.get('rol', 'Desconocido')
    modulos_disponibles = obtener_modulos_por_rol(rol_usuario)
    st.sidebar.write(f"🔍 DEBUG - Rol: {rol_usuario}")
    st.sidebar.write(f"🔍 DEBUG - Módulos: {modulos_disponibles}")
    
    # Sidebar header con estilo mejorado
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎓 SICADFOC 2026")
    st.sidebar.markdown(f"**Usuario:** {st.session_state.user_data.get('nombre', 'Usuario')}")
    st.sidebar.markdown(f"**Rol:** {rol_usuario.title()}")
    st.sidebar.markdown("---")
    
    # Obtener módulo actual del session state (con persistencia)
    modulo_actual = st.session_state.get('modulo_actual', modulos_disponibles[0])
    
    # Asegurar que el módulo actual esté en la lista de disponibles
    if modulo_actual not in modulos_disponibles:
        modulo_actual = modulos_disponibles[0]
        st.session_state['modulo_actual'] = modulo_actual
    
    # Crear botones de navegación individuales (lista de opciones, no desplegable)
    st.sidebar.markdown("### 📋 Módulos")
    
    pagina_seleccionada = modulo_actual
    
    for modulo in modulos_disponibles:
        # Determinar si este módulo está activo
        is_active = (modulo == modulo_actual)
        
        # Crear botón con estilo según estado
        if is_active:
            # Botón activo (azul)
            if st.sidebar.button(f"🔵 {modulo}", key=f"nav_{modulo}", use_container_width=True, help="Módulo actual"):
                pagina_seleccionada = modulo
        else:
            # Botón inactivo (gris)
            if st.sidebar.button(f"⚪ {modulo}", key=f"nav_{modulo}", use_container_width=True, help=f"Ir a {modulo}"):
                pagina_seleccionada = modulo
                st.session_state['modulo_actual'] = modulo
                st.session_state['mensaje_bienvenida'] = False
                st.rerun()
    
    # Botón de cerrar sesión al final del menú
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    
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

def mostrar_gestion_usuarios():
    """Muestra el módulo de gestión de usuarios"""
    st.markdown("## 👥 Gestión de Usuarios")
    st.markdown("---")
    
    # Tabs para diferentes funciones
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Usuarios", "✅ Aprobaciones", "➕ Nuevo Usuario"])
    
    with tab1:
        st.markdown("### 📋 Lista de Usuarios Registrados")
        
        # Tabla de usuarios simulada
        usuarios_data = {
            'Nombre': ['Juan Pérez', 'María García', 'Carlos López'],
            'Email': ['juan@iujo.edu', 'maria@iujo.edu', 'carlos@iujo.edu'],
            'Rol': ['Estudiante', 'Profesor', 'Administrador'],
            'Estado': ['✅ Activo', '✅ Activo', '⏳ Por aprobar']
        }
        
        st.dataframe(pd.DataFrame(usuarios_data))
    
    with tab2:
        st.markdown("### ✅ Usuarios por Aprobar (Captcha Validados)")
        st.warning("🔍 Usuarios que completaron el captcha y esperan aprobación")
        
        # Lista de usuarios por aprobar
        por_aprobar = [
            {"nombre": "Ana Martínez", "cedula": "V-12345678", "email": "ana@iujo.edu"},
            {"nombre": "Luis Rodríguez", "cedula": "V-87654321", "email": "luis@iujo.edu"}
        ]
        
        for usuario in por_aprobar:
            with st.expander(f"👤 {usuario['nombre']} - {usuario['cedula']}"):
                st.write(f"📧 Email: {usuario['email']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Aprobar {usuario['nombre']}", key=f"aprobar_{usuario['cedula']}"):
                        st.success(f"✅ {usuario['nombre']} aprobado exitosamente")
                with col2:
                    if st.button(f"❌ Rechazar {usuario['nombre']}", key=f"rechazar_{usuario['cedula']}"):
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
    """Muestra el módulo de reportes y auditoría"""
    st.markdown("## 📊 Reportes y Auditoría")
    st.markdown("---")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        fecha_inicio = st.date_input("📅 Fecha Inicio")
    with col2:
        fecha_fin = st.date_input("📅 Fecha Fin")
    with col3:
        tipo_reporte = st.selectbox("📋 Tipo de Reporte", ["Todos", "Usuarios", "Archivos", "Sistema"])
    
    # Generar reporte
    if st.button("🔍 Generar Reporte"):
        st.success("✅ Reporte generado exitosamente")
        
        # Tabla de auditoría simulada
        auditoria_data = {
            'Fecha': ['2024-01-25', '2024-01-24', '2024-01-23'],
            'Usuario': ['admin', 'juan.perez', 'maria.garcia'],
            'Acción': ['Login', 'Subir PDF', 'Crear Usuario'],
            'Resultado': ['✅ Éxito', '✅ Éxito', '❌ Error']
        }
        
        st.dataframe(pd.DataFrame(auditoria_data))
    
    # Estadísticas
    st.markdown("---")
    st.markdown("### 📈 Estadísticas de Auditoría")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔐 Total Logins", "1,234")
    with col2:
        st.metric("📁 Archivos Procesados", "567")
    with col3:
        st.metric("👤 Usuarios Creados", "89")
    with col4:
        st.metric("⚠️ Errores", "12")

def mostrar_configuracion():
    """Muestra el módulo de configuración del sistema"""
    st.markdown("## ⚙️ Configuración")
    st.markdown("---")
    
    # Tabs de configuración
    tab1, tab2, tab3 = st.tabs(["🔧 General", "📧 Correo", "🔒 Seguridad"])
    
    with tab1:
        st.markdown("### 🔧 Configuración General")
        
        # Configuración básica
        nombre_sistema = st.text_input("🏷️ Nombre del Sistema", value="SICADFOC 2026")
        version = st.text_input("📦 Versión", value="1.0.0")
        modo_mantenimiento = st.checkbox("🔧 Modo Mantenimiento")
        
        if st.button("💾 Guardar Configuración General"):
            st.success("✅ Configuración guardada exitosamente")
    
    with tab2:
        st.markdown("### 📧 Configuración de Correo")
        
        email_host = st.text_input("🌐 Servidor SMTP", value="smtp.gmail.com")
        email_puerto = st.number_input("📡 Puerto", value=587)
        email_usuario = st.text_input("👤 Usuario Email")
        email_password = st.text_input("🔑 Contraseña", type="password")
        
        if st.button("🧪 Probar Conexión Email"):
            st.success("✅ Conexión email exitosa")
    
    with tab3:
        st.markdown("### 🔒 Configuración de Seguridad")
        
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
    """Muestra el módulo de gestión de profesores"""
    st.markdown("## 👨‍🏫 Profesores")
    st.markdown("---")
    
    # Pestañas principales
    tab_lista, tab_cargas = st.tabs(["📋 Lista de Profesores", "📁 Gestión de Documentos"])
    
    with tab_lista:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Lista de Profesores")
            
            # Datos de ejemplo
            profesores = [
                {"nombre": "Dr. Juan Pérez", "cedula": "12345678", "departamento": "Matemáticas", "email": "jperez@iujo.edu"},
                {"nombre": "Dra. María García", "cedula": "87654321", "departamento": "Física", "email": "mgarcia@iujo.edu"},
                {"nombre": "Ing. Carlos López", "cedula": "45678912", "departamento": "Computación", "email": "clopez@iujo.edu"}
            ]
            
            # Crear tabla limpia sin expanders
            for i, prof in enumerate(profesores):
                col_nombre, col_info, col_acciones = st.columns([2, 2, 1])
                
                with col_nombre:
                    st.write(f"**👨‍🏫 {prof['nombre']}**")
                
                with col_info:
                    st.write(f"🆔 {prof['cedula']}")
                    st.write(f"📧 {prof['email']}")
                    st.write(f"🏢 {prof['departamento']}")
                
                with col_acciones:
                    if st.button(f"✏️", key=f"editar_prof_{i}", help="Editar"):
                        st.info(f"✏️ Editando {prof['nombre']}")
                    if st.button(f"🗑️", key=f"eliminar_prof_{i}", help="Eliminar"):
                        st.warning(f"🗑️ Eliminando {prof['nombre']}")
                
                st.markdown("---")
        
        with col2:
            st.subheader("➕ Agregar Profesor")
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
    """Muestra el módulo de gestión de estudiantes"""
    st.markdown("## 👨‍🎓 Estudiantes")
    st.markdown("---")
    
    # Pestañas principales
    tab_lista, tab_cargas = st.tabs(["📋 Lista de Estudiantes", "📁 Gestión de Documentos"])
    
    with tab_lista:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Lista de Estudiantes")
            
            # Datos de ejemplo
            estudiantes = [
                {"nombre": "Ana Martínez", "cedula": "23456789", "carrera": "Ingeniería", "semestre": "6to", "promedio": "8.5"},
                {"nombre": "Luis Rodríguez", "cedula": "34567890", "carrera": "Matemáticas", "semestre": "4to", "promedio": "9.0"},
                {"nombre": "Sofía Hernández", "cedula": "45678901", "carrera": "Física", "semestre": "5to", "promedio": "8.8"}
            ]
            
            # Crear tabla limpia sin expanders
            for i, est in enumerate(estudiantes):
                col_nombre, col_info, col_acciones = st.columns([2, 2, 1])
                
                with col_nombre:
                    st.write(f"**👨‍🎓 {est['nombre']}**")
                
                with col_info:
                    st.write(f"🆔 {est['cedula']}")
                    st.write(f"🎓 {est['carrera']}")
                    st.write(f"📚 {est['semestre']}")
                    st.write(f"📊 Promedio: {est['promedio']}")
                
                with col_acciones:
                    if st.button(f"✏️", key=f"editar_est_{i}", help="Editar"):
                        st.info(f"✏️ Editando {est['nombre']}")
                    if st.button(f"🗑️", key=f"eliminar_est_{i}", help="Eliminar"):
                        st.warning(f"🗑️ Eliminando {est['nombre']}")
                
                st.markdown("---")
        
        with col2:
            st.subheader("➕ Agregar Estudiante")
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
        
        # Vista de tarjetas sin expanders
        cols = st.columns(3)
        for i, curso in enumerate(cursos):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; background-color: #f9f9f9;">
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
        
        # Vista de tarjetas sin expanders
        cols = st.columns(3)
        for i, cert in enumerate(certificaciones):
            with cols[i % 3]:
                color_estado = "🟢" if cert['estado'] == "Vigente" else "🟡"
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; background-color: #f9f9f9;">
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
        
        # Vista de tarjetas sin expanders
        cols = st.columns(3)
        for i, evento in enumerate(eventos):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; background-color: #f9f9f9;">
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

def mostrar_dashboard_protegido():
    """Muestra el dashboard principal con navegación protegida"""
    
    # Limpiar mensajes de bienvenida después de 3 segundos
    if 'mensaje_bienvenida' not in st.session_state:
        st.session_state['mensaje_bienvenida'] = True
        st.session_state['tiempo_bienvenida'] = time.time()
    
    # Eliminar mensaje de bienvenida después de 3 segundos
    if time.time() - st.session_state.get('tiempo_bienvenida', 0) > 3:
        st.session_state['mensaje_bienvenida'] = False
    
    # Mostrar mensaje de bienvenida solo si está activo
    if st.session_state.get('mensaje_bienvenida', False):
        st.success(f"✅ Bienvenido {st.session_state.user_data.get('nombre', 'Usuario')}")
        st.info(f"🔐 Rol: {st.session_state.rol}")
    
    # Obtener página seleccionada del sidebar
    pagina = mostrar_sidebar_protegido()
    
    # Mostrar contenido según la página seleccionada
    if pagina == "👥 Usuarios":
        mostrar_gestion_usuarios()
    elif pagina == "👨‍🏫 Profesores":
        mostrar_gestion_profesores()
    elif pagina == "👨‍🎓 Estudiantes":
        mostrar_gestion_estudiantes()
    elif pagina == "📚 Formación Complementaria":
        mostrar_formacion_complementaria()
    elif pagina == " Reportes":
        mostrar_reportes()
    elif pagina == "⚙️ Configuración":
        mostrar_configuracion()
    elif pagina == "📁 Mis Documentos":
        mostrar_mis_documentos()
    elif pagina == "📊 Mi Progreso":
        mostrar_mi_progreso()
    else:
        # Módulo no reconocido - mostrar banner por defecto
        mostrar_banner_informativo()

def mostrar_banner_informativo():
    """Muestra un banner informativo con desplazamiento de izquierda a derecha"""
    st.markdown("---")
    
    # CSS para banner con desplazamiento
    st.markdown("""
    <style>
    .banner-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
        overflow: hidden;
        position: relative;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .banner-content {
        display: flex;
        animation: scroll 20s linear infinite;
        white-space: nowrap;
    }
    
    .banner-item {
        color: white;
        font-size: 16px;
        font-weight: 600;
        padding: 0 50px;
        display: flex;
        align-items: center;
    }
    
    @keyframes scroll {
        0% {
            transform: translateX(100%);
        }
        100% {
            transform: translateX(-100%);
        }
    }
    
    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
        margin-top: 30px;
    }
    
    .info-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Banner con desplazamiento
    st.markdown("""
    <div class="banner-container">
        <div class="banner-content">
            <div class="banner-item">🎓 SICADFOC 2026 - Sistema Integrado de Control Académico</div>
            <div class="banner-item">📅 Año Lectivo 2026</div>
            <div class="banner-item">👥 1,250 Estudiantes Activos</div>
            <div class="banner-item">👨‍🏫 85 Profesores</div>
            <div class="banner-item">📚 45 Cursos Disponibles</div>
            <div class="banner-item">🏆 Convocatoria Abierta</div>
            <div class="banner-item">📊 Sistema en Línea - 99.9% Uptime</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
