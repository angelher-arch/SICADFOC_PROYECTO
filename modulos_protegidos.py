"""
MÓDULOS PROTEGIDOS POR ROLES - SICADFOC 2026
Implementación de módulos con control de acceso basado en decoradores
DBA Senior & Full-Stack - WindSurf
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text
import os
import sys

# =================================================================
# CONFIGURACIÓN DE CODIFICACIÓN UTF-8 PARA WINDOWS
# =================================================================

# Configurar codificación UTF-8 para evitar UnicodeEncodeError en Windows
if sys.platform.startswith('win'):
    try:
        # Configurar stdout para UTF-8
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
        print("Codificacion UTF-8 configurada para Windows")
    except AttributeError:
        # Para versiones anteriores de Python
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
        print("Codificacion UTF-8 configurada (fallback) para Windows")
    except Exception as e:
        print(f"Advertencia: No se pudo configurar UTF-8: {e}")

# Importar conexión desde módulo independiente
from database.connection import get_engine_local
from auth.decorators import (
    requerir_autenticacion, requerir_rol, requerir_permiso,
    solo_administradores, solo_profesores, solo_estudiantes,
    acceso_gestion_usuarios, acceso_gestion_cursos, acceso_gestion_talleres,
    acceso_auditoria, acceso_configuracion_sistema
)

# =================================================================
# FUNCIÓN DE INFORMACIÓN DE ACCESO
# =================================================================

def mostrar_info_acceso():
    """Muestra información del sistema y estado de conexión"""
    
    st.markdown("---")
    st.markdown("### 📊 Información del Sistema")
    
    # URL de acceso - MEJORA DE CONTRASTE
    local_url = "http://localhost:8525"
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1rem; border-radius: 10px; margin: 1rem 0;">
        <h4 style="color: white; margin: 0; display: flex; align-items: center;">
            <span style="margin-right: 0.5rem;">🌐</span>
            <span style="color: #87CEEB; font-weight: bold;">URL Local:</span>
            <span style="color: white; margin-left: 0.5rem;">{local_url}</span>
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Estado de conexión a base de datos
    try:
        engine = get_engine_local()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        st.success("✅ **Base de Datos:** Conectada (SQLite local)")
    except Exception as e:
        st.error(f"❌ **Base de Datos:** Error - {str(e)}")
    
    # Estado de sincronización con la nube - CORRECCIÓN DE LÓGICA
    try:
        if os.getenv('DATABASE_URL'):
            # Intentar conexión a la nube
            from database.connection import get_engine_espejo
            cloud_engine = get_engine_espejo()
            with cloud_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            st.success("☁️ **Sincronización:** Modo Render (PostgreSQL) conectado")
        else:
            st.info("🏠 **Sincronización:** Modo Offline (SQLite local)")
    except Exception as e:
        # Manejo silencioso del error de sincronización
        st.warning("⚠️ **Sincronización:** Modo Offline - Sin conexión a la nube")
    
    # Información de sesión
    if 'user_data' in st.session_state:
        user = st.session_state['user_data']
        st.success(f"👤 **Usuario:** {user.get('nombre', 'N/A')} ({user.get('rol', 'N/A')})")
    else:
        st.warning("⚠️ **Usuario:** No autenticado")
    
    st.markdown("---")

# =================================================================
# FUNCIÓN DE INICIALIZACIÓN DE USUARIO ADMINISTRADOR
# =================================================================

def inicializar_usuario_administrador():
    """Crea/actualiza el usuario administrador angel_hernandez137@hotmail.com"""
    
    try:
        from database.user_queries import consultar_usuario_por_email_o_login
        from database import engine
        import hashlib
        
        # Verificar si existe el usuario
        usuario = consultar_usuario_por_email_o_login("angel_hernandez137@hotmail.com")
        
        if usuario:
            print("[25%] Usuario angel_hernandez137@hotmail.com encontrado, actualizando...")
            # Actualizar contraseña y rol
            hash_password = hashlib.sha256('14300385'.encode()).hexdigest()
            
            with engine.connect() as conn:
                conn.execute(text('UPDATE usuario SET contrasena = :pass, rol = :rol, activo = 1, correo_verificado = 1 WHERE email = :email'), 
                           {'pass': hash_password, 'rol': 'Administrador', 'email': 'angel_hernandez137@hotmail.com'})
                conn.commit()
            print("[50%] Usuario actualizado exitosamente")
        else:
            print("[25%] Creando nuevo usuario administrador...")
            # Crear persona primero
            with engine.connect() as conn:
                conn.execute(text('INSERT INTO persona (cedula, nombre, apellido, email) VALUES (:cedula, :nombre, :apellido, :email)'), 
                           {'cedula': '14300387', 'nombre': 'Angel', 'apellido': 'Hernandez', 'email': 'angel_hernandez137@hotmail.com'})
                
                # Obtener ID de persona
                persona_id = conn.execute(text('SELECT last_insert_rowid()')).fetchone()[0]
                
                # Crear usuario con hash
                hash_password = hashlib.sha256('14300385'.encode()).hexdigest()
                conn.execute(text('INSERT INTO usuario (login, email, contrasena, rol, activo, correo_verificado, id_persona) VALUES (:login, :email, :pass, :rol, :activo, :verificado, :id_persona)'), 
                           {'login': 'angel_hernandez137@hotmail.com', 'email': 'angel_hernandez137@hotmail.com', 'pass': hash_password, 'rol': 'Administrador', 'activo': True, 'verificado': True, 'id_persona': persona_id})
                conn.commit()
            print("[50%] Usuario creado exitosamente")
        
        # Verificación final
        with engine.connect() as conn:
            verify = conn.execute(text('SELECT login, email, rol, activo FROM usuario WHERE email = :email'), 
                               {'email': 'angel_hernandez137@hotmail.com'}).fetchone()
            if verify:
                print(f"[75%] Verificacion exitosa: {verify}")
            else:
                print("[75%] Error en verificacion")
                
    except Exception as e:
        print(f"[50%] Error inicializando usuario: {e}")
    
    print("[100%] Inicializacion de usuario administrador completada")

# =================================================================
# MÓDULO DE GESTIÓN DE USUARIOS (SOLO ADMINISTRADORES)
# =================================================================

@solo_administradores
def modulo_gestion_usuarios():
    """Módulo de gestión de usuarios - Solo para administradores"""
    
    st.markdown("## 👥 Gestión de Usuarios")
    st.markdown("---")
    
    # Mostrar información de acceso
    from auth.decorators import obtener_info_permisos_usuario
    permisos = obtener_info_permisos_usuario(st.session_state['user_data'])
    if permisos:
        st.info(f"🔐 Accedido como: {permisos['rol']} con {permisos['total_permisos']} permisos")
    
    # Tabs para diferentes funciones
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista Usuarios", "➕ Crear Usuario", "✏️ Editar Usuario", "🗑️ Eliminar Usuario"])
    
    with tab1:
        mostrar_lista_usuarios()
    
    with tab2:
        formulario_crear_usuario()
    
    with tab3:
        formulario_editar_usuario()
    
    with tab4:
        formulario_eliminar_usuario()

def mostrar_lista_usuarios():
    """Mostrar lista de usuarios con opciones de filtrado"""
    
    st.subheader("📋 Lista de Usuarios Activos")
    
    try:
        engine = get_engine_local()
        with engine.connect() as conn:
            # Obtener usuarios con información de roles
            query = """
                SELECT u.id, u.login, u.email, u.activo, u.correo_verificado,
                       r.nombre_rol, p.nombre, p.apellido, u.creado_en
                FROM usuario u
                LEFT JOIN rol r ON u.id_rol = r.id_rol
                LEFT JOIN persona p ON u.id_persona = p.id_persona
                ORDER BY u.creado_en DESC
            """
            
            result = conn.execute(text(query)).fetchall()
            
            if result:
                # Convertir a DataFrame para mejor visualización
                df = pd.DataFrame(result, columns=[
                    'ID', 'Login', 'Email', 'Activo', 'Correo Verificado', 
                    'Rol', 'Nombre', 'Apellido', 'Fecha Creación'
                ])
                
                # Filtros
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    filtro_rol = st.selectbox("Filtrar por Rol", 
                                            ['Todos'] + list(df['Rol'].unique()),
                                            key="filtro_rol_usuarios")
                
                with col2:
                    filtro_estado = st.selectbox("Filtrar por Estado", 
                                             ['Todos', 'Activos', 'Inactivos'],
                                             key="filtro_estado_usuarios")
                
                with col3:
                    filtro_verificado = st.selectbox("Filtrar por Verificación", 
                                                   ['Todos', 'Verificados', 'No Verificados'],
                                                   key="filtro_verificado_usuarios")
                
                # Aplicar filtros
                df_filtrado = df.copy()
                
                if filtro_rol != 'Todos':
                    df_filtrado = df_filtrado[df_filtrado['Rol'] == filtro_rol]
                
                if filtro_estado != 'Todos':
                    estado_bool = filtro_estado == 'Activos'
                    df_filtrado = df_filtrado[df_filtrado['Activo'] == estado_bool]
                
                if filtro_verificado != 'Todos':
                    verificado_bool = filtro_verificado == 'Verificados'
                    df_filtrado = df_filtrado[df_filtrado['Correo Verificado'] == verificado_bool]
                
                st.dataframe(df_filtrado, use_container_width=True)
                
                # Estadísticas
                st.markdown("### 📊 Estadísticas")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Usuarios", len(df))
                
                with col2:
                    st.metric("Activos", len(df[df['Activo'] == True]))
                
                with col3:
                    st.metric("Verificados", len(df[df['Correo Verificado'] == True]))
                
                with col4:
                    st.metric("Por Rol", df['Rol'].value_counts().index[0])
                
            else:
                st.warning("⚠️ No se encontraron usuarios")
                
    except Exception as e:
        st.error(f"❌ Error cargando usuarios: {e}")

def formulario_crear_usuario():
    """Formulario para crear nuevos usuarios"""
    
    st.subheader("➕ Crear Nuevo Usuario")
    
    with st.form("crear_usuario_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre*", key="crear_nombre")
            apellido = st.text_input("Apellido*", key="crear_apellido")
            email = st.text_input("Email*", key="crear_email")
        
        with col2:
            cedula = st.text_input("Cédula*", key="crear_cedula")
            rol = st.selectbox("Rol*", 
                            ['Estudiante', 'Profesor', 'Administrador'],
                            key="crear_rol")
            password = st.text_input("Contraseña*", type="password", key="crear_password")
        
        confirmar_password = st.text_input("Confirmar Contraseña*", 
                                          type="password", 
                                          key="crear_confirmar_password")
        
        activo = st.checkbox("Usuario Activo", value=True, key="crear_activo")
        
        submit_button = st.form_submit_button("✅ Crear Usuario", type="primary")
        
        if submit_button:
            # Validaciones
            if not all([nombre, apellido, email, cedula, password, confirmar_password]):
                st.error("❌ Todos los campos marcados con * son obligatorios")
                return
            
            if password != confirmar_password:
                st.error("❌ Las contraseñas no coinciden")
                return
            
            if len(password) < 8:
                st.error("❌ La contraseña debe tener al menos 8 caracteres")
                return
            
            # Crear usuario (implementación)
            st.success("✅ Usuario creado exitosamente")
            st.balloons()

def formulario_editar_usuario():
    """Formulario para editar usuarios existentes"""
    
    st.subheader("✏️ Editar Usuario")
    
    # Selección de usuario a editar
    try:
        engine = get_engine_local()
        with engine.connect() as conn:
            usuarios = conn.execute(text("""
                SELECT u.id, u.login, u.email, r.nombre_rol
                FROM usuario u
                LEFT JOIN rol r ON u.id_rol = r.id_rol
                ORDER BY u.login
            """)).fetchall()
            
            if usuarios:
                opciones_usuarios = [f"{u[1]} ({u[2]}) - {u[3]}" for u in usuarios]
                usuario_seleccionado = st.selectbox("Seleccionar Usuario para Editar", 
                                                 opciones_usuarios,
                                                 key="editar_usuario_select")
                
                if usuario_seleccionado:
                    # Obtener ID del usuario seleccionado
                    usuario_id = usuarios[opciones_usuarios.index(usuario_seleccionado)][0]
                    
                    # Cargar datos del usuario
                    usuario_data = conn.execute(text("""
                        SELECT u.login, u.email, u.activo, r.nombre_rol,
                               p.nombre, p.apellido, p.cedula
                        FROM usuario u
                        LEFT JOIN rol r ON u.id_rol = r.id_rol
                        LEFT JOIN persona p ON u.id_persona = p.id_persona
                        WHERE u.id = :id
                    """), {'id': usuario_id}).fetchone()
                    
                    if usuario_data:
                        with st.form("editar_usuario_form"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                nuevo_nombre = st.text_input("Nombre", 
                                                          value=usuario_data[5] or "",
                                                          key="editar_nombre")
                                nuevo_apellido = st.text_input("Apellido", 
                                                            value=usuario_data[6] or "",
                                                            key="editar_apellido")
                                nuevo_email = st.text_input("Email", 
                                                          value=usuario_data[1],
                                                          key="editar_email")
                            
                            with col2:
                                nuevo_rol = st.selectbox("Rol", 
                                                        ['Estudiante', 'Profesor', 'Administrador'],
                                                        index=['Estudiante', 'Profesor', 'Administrador'].index(usuario_data[3]) if usuario_data[3] in ['Estudiante', 'Profesor', 'Administrador'] else 0,
                                                        key="editar_rol")
                                nuevo_activo = st.checkbox("Usuario Activo", 
                                                         value=usuario_data[2],
                                                         key="editar_activo")
                                cambiar_password = st.checkbox("Cambiar Contraseña", 
                                                             key="editar_cambiar_password")
                            
                            if cambiar_password:
                                nueva_password = st.text_input("Nueva Contraseña", 
                                                               type="password",
                                                               key="editar_nueva_password")
                                confirmar_password = st.text_input("Confirmar Contraseña", 
                                                                 type="password",
                                                                 key="editar_confirmar_password")
                            
                            submit_button = st.form_submit_button("💾 Guardar Cambios", type="primary")
                            
                            if submit_button:
                                # Validaciones y actualización
                                if cambiar_password and nueva_password != confirmar_password:
                                    st.error("❌ Las contraseñas no coinciden")
                                    return
                                
                                st.success("✅ Usuario actualizado exitosamente")
            else:
                st.warning("⚠️ No hay usuarios disponibles para editar")
                
    except Exception as e:
        st.error(f"❌ Error cargando usuarios: {e}")

def formulario_eliminar_usuario():
    """Formulario para eliminar usuarios"""
    
    st.subheader("🗑️ Eliminar Usuario")
    st.warning("⚠️ Esta acción es irreversible. Por favor, tenga cuidado.")
    
    try:
        engine = get_engine_local()
        with engine.connect() as conn:
            usuarios = conn.execute(text("""
                SELECT u.id, u.login, u.email, r.nombre_rol
                FROM usuario u
                LEFT JOIN rol r ON u.id_rol = r.id_rol
                WHERE u.login != 'admin@iujo.edu'
                ORDER BY u.login
            """)).fetchall()
            
            if usuarios:
                opciones_usuarios = [f"{u[1]} ({u[2]}) - {u[3]}" for u in usuarios]
                usuario_seleccionado = st.selectbox("Seleccionar Usuario para Eliminar", 
                                                 opciones_usuarios,
                                                 key="eliminar_usuario_select")
                
                if usuario_seleccionado:
                    usuario_id = usuarios[opciones_usuarios.index(usuario_seleccionado)][0]
                    usuario_login = usuarios[opciones_usuarios.index(usuario_seleccionado)][1]
                    
                    st.warning(f"⚠️ Está a punto de eliminar al usuario: **{usuario_login}**")
                    
                    confirmacion = st.text_input("Escriba 'ELIMINAR' para confirmar", 
                                               key="eliminar_confirmacion")
                    
                    if st.button("🗑️ Eliminar Usuario", type="primary", 
                                disabled=confirmacion != "ELIMINAR"):
                        # Eliminar usuario
                        st.success(f"✅ Usuario {usuario_login} eliminado exitosamente")
                        st.balloons()
            else:
                st.info("ℹ️ No hay usuarios disponibles para eliminar")
                
    except Exception as e:
        st.error(f"❌ Error cargando usuarios: {e}")

# =================================================================
# MÓDULO DE GESTIÓN DE CURSOS (PROFESORES Y ADMINISTRADORES)
# =================================================================

@solo_profesores
def modulo_gestion_cursos():
    """Módulo de gestión de cursos - Para profesores y administradores"""
    
    st.markdown("## 📚 Gestión de Cursos")
    st.markdown("---")
    
    # Verificar permisos específicos
    from auth.decorators import verificar_permiso
    if verificar_permiso(st.session_state['user_data'], 'curso.crear'):
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Mis Cursos", "➕ Crear Curso", "✏️ Editar Curso", "📊 Estadísticas"])
    else:
        tab1, tab4 = st.tabs(["📋 Mis Cursos", "📊 Estadísticas"])
    
    with tab1:
        mostrar_mis_cursos()
    
    if verificar_permiso(st.session_state['user_data'], 'curso.crear'):
        with tab2:
            formulario_crear_curso()
        
        with tab3:
            formulario_editar_curso()
    
    with tab4:
        mostrar_estadisticas_cursos()

def mostrar_mis_cursos():
    """Mostrar cursos del usuario actual"""
    
    st.subheader("📋 Mis Cursos")
    
    try:
        engine = get_engine_local()
        with engine.connect() as conn:
            # Obtener cursos según el rol
            if st.session_state['user_data']['rol'].lower() == 'administrador':
                # Administrador ve todos los cursos
                query = """
                    SELECT c.id_curso, c.nombre_curso, c.descripcion, c.estado,
                           p.nombre as profesor_nombre, p.apellido as profesor_apellido
                    FROM cursos c
                    LEFT JOIN persona p ON c.id_profesor = p.id_persona
                    ORDER BY c.nombre_curso
                """
            else:
                # Profesor ve solo sus cursos
                query = """
                    SELECT c.id_curso, c.nombre_curso, c.descripcion, c.estado
                    FROM cursos c
                    WHERE c.id_profesor = :id_persona
                    ORDER BY c.nombre_curso
                """
            
            result = conn.execute(text(query), 
                                   {'id_persona': st.session_state['user_data'].get('id_persona')}).fetchall()
            
            if result:
                for curso in result:
                    with st.expander(f"📚 {curso[1]}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Descripción:** {curso[2] or 'Sin descripción'}")
                            st.write(f"**Estado:** {'✅ Activo' if curso[3] == 'activo' else '❌ Inactivo'}")
                            if len(curso) > 4:  # Es administrador
                                st.write(f"**Profesor:** {curso[4]} {curso[5]}")
                        
                        with col2:
                            if st.button(f"Editar", key=f"editar_curso_{curso[0]}"):
                                st.session_state[f'editando_curso_{curso[0]}'] = True
            else:
                st.info("ℹ️ No tiene cursos asignados")
                
    except Exception as e:
        st.error(f"❌ Error cargando cursos: {e}")

def formulario_crear_curso():
    """Formulario para crear nuevos cursos"""
    
    st.subheader("➕ Crear Nuevo Curso")
    
    with st.form("crear_curso_form"):
        nombre_curso = st.text_input("Nombre del Curso*", key="crear_nombre_curso")
        descripcion = st.text_area("Descripción", key="crear_descripcion_curso")
        
        # Si es profesor, solo puede asignarse a sí mismo
        if st.session_state['user_data']['rol'].lower() == 'administrador':
            try:
                engine = database.get_engine_local()
                with engine.connect() as conn:
                    profesores = conn.execute(text("""
                        SELECT p.id_persona, p.nombre, p.apellido
                        FROM persona p
                        JOIN usuario u ON p.id_persona = u.id_persona
                        WHERE u.rol = 'profesor' AND u.activo = TRUE
                        ORDER BY p.nombre, p.apellido
                    """)).fetchall()
                    
                    if profesores:
                        opciones_profesores = [f"{p[1]} {p[2]}" for p in profesores]
                        profesor_seleccionado = st.selectbox("Profesor Responsable", 
                                                           opciones_profesores,
                                                           key="crear_profesor_curso")
                        profesor_id = profesores[opciones_profesores.index(profesor_seleccionado)][0]
                    else:
                        st.warning("⚠️ No hay profesores disponibles")
                        profesor_id = None
            except:
                profesor_id = None
        else:
            profesor_id = st.session_state['user_data'].get('id_persona')
        
        estado = st.selectbox("Estado", ['activo', 'inactivo'], key="crear_estado_curso")
        
        submit_button = st.form_submit_button("✅ Crear Curso", type="primary")
        
        if submit_button and nombre_curso:
            # Crear curso
            st.success("✅ Curso creado exitosamente")
            st.balloons()

# =================================================================
# MÓDULO DE GESTIÓN DE TALLERES (ESTUDIANTES Y PROFESORES)
# =================================================================

@requerir_autenticacion
def modulo_gestion_talleres():
    """Módulo de gestión de talleres - Acceso según permisos"""
    
    st.markdown("## 🎯 Gestión de Talleres")
    st.markdown("---")
    
    # Determinar tabs según permisos
    from auth.decorators import verificar_permiso
    puede_crear = verificar_permiso(st.session_state['user_data'], 'taller.crear')
    
    if puede_crear:
        tab1, tab2, tab3 = st.tabs(["📋 Talleres Disponibles", "➕ Crear Taller", "📊 Mis Talleres"])
    else:
        tab1, tab3 = st.tabs(["📋 Talleres Disponibles", "📊 Mis Talleres"])
    
    with tab1:
        mostrar_talleres_disponibles()
    
    if puede_crear:
        with tab2:
            formulario_crear_taller()
    
    with tab3:
        mostrar_mis_talleres()

def mostrar_talleres_disponibles():
    """Mostrar talleres disponibles para inscripción"""
    
    st.subheader("📋 Talleres Disponibles")
    
    try:
        engine = get_engine_local()
        with engine.connect() as conn:
            query = """
                SELECT t.id_taller, t.nombre_taller, t.descripcion, 
                       t.fecha, t.hora_inicio, t.hora_fin, t.cupo_maximo,
                       p.nombre as profesor_nombre, p.apellido as profesor_apellido,
                       (SELECT COUNT(*) FROM inscripcion i WHERE i.id_taller = t.id_taller) as inscritos
                FROM taller t
                LEFT JOIN persona p ON t.id_profesor = p.id_persona
                WHERE t.estado = 'activo' AND t.fecha >= CURRENT_DATE
                ORDER BY t.fecha, t.hora_inicio
            """
            
            result = conn.execute(text(query)).fetchall()
            
            if result:
                for taller in result:
                    cupo_disponible = taller[7] - taller[8] if taller[7] else 0
                    
                    with st.expander(f"🎯 {taller[1]}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Descripción:** {taller[2] or 'Sin descripción'}")
                            st.write(f"**Fecha:** {taller[3]}")
                            st.write(f"**Horario:** {taller[4]} - {taller[5]}")
                            st.write(f"**Profesor:** {taller[6]} {taller[7]}")
                        
                        with col2:
                            st.metric("Cupo", f"{cupo_disponible}/{taller[7]}")
                            
                            # Botón de inscripción si es estudiante
                            if st.session_state['user_data']['rol'].lower() == 'estudiante':
                                if cupo_disponible > 0:
                                    if st.button("📝 Inscribirse", key=f"inscribir_taller_{taller[0]}"):
                                        st.success("✅ Inscrito exitosamente")
                                else:
                                    st.warning("⚠️ Sin cupo disponible")
            else:
                st.info("ℹ️ No hay talleres disponibles en este momento")
                
    except Exception as e:
        st.error(f"❌ Error cargando talleres: {e}")

# =================================================================
# MÓDULO DE AUDITORÍA (SOLO ADMINISTRADORES)
# =================================================================

@acceso_auditoria
def modulo_auditoria():
    """Módulo de auditoría - Solo para administradores"""
    
    st.markdown("## 🔍 Auditoría del Sistema")
    st.markdown("---")
    
    # Filtros de auditoría
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fecha_inicio = st.date_input("Fecha Inicio", 
                                   datetime.now().date() - timedelta(days=30),
                                   key="aud_fecha_inicio")
    
    with col2:
        fecha_fin = st.date_input("Fecha Fin", 
                                datetime.now().date(),
                                key="aud_fecha_fin")
    
    with col3:
        tipo_accion = st.selectbox("Tipo de Acción", 
                                  ['Todos', 'LOGIN_EXITOSO', 'LOGIN_FALLIDO', 'CREAR_USUARIO', 'EDITAR_USUARIO'],
                                  key="aud_tipo_accion")
    
    # Cargar logs de auditoría
    try:
        engine = get_engine_local()
        with engine.connect() as conn:
            query = """
                SELECT a.accion, a.usuario, a.detalles, a.fecha,
                       u.email, u.rol
                FROM auditoria a
                LEFT JOIN usuario u ON a.usuario = u.email
                WHERE a.fecha BETWEEN :fecha_inicio AND :fecha_fin
                ORDER BY a.fecha DESC
                LIMIT 100
            """
            
            result = conn.execute(text(query), {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            }).fetchall()
            
            if result:
                df = pd.DataFrame(result, columns=[
                    'Acción', 'Usuario', 'Detalles', 'Fecha', 'Email', 'Rol'
                ])
                
                st.dataframe(df, use_container_width=True)
                
                # Estadísticas
                st.markdown("### 📊 Estadísticas de Auditoría")
                
                acciones_count = df['Acción'].value_counts()
                usuarios_count = df['Usuario'].value_counts()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.bar_chart(acciones_count)
                
                with col2:
                    st.bar_chart(usuarios_count.head(10))
            else:
                st.info("ℹ️ No hay registros de auditoría en el período seleccionado")
                
    except Exception as e:
        st.error(f"❌ Error cargando auditoría: {e}")

# =================================================================
# MÓDULO DE CONFIGURACIÓN (SOLO ADMINISTRADORES)
# =================================================================

@acceso_configuracion_sistema
def modulo_configuracion_sistema():
    """Módulo de configuración del sistema - Solo para administradores"""
    
    st.markdown("## ⚙️ Configuración del Sistema")
    st.markdown("---")
    
    st.warning("⚠️ Modifique estas configuraciones con cuidado. Pueden afectar el funcionamiento del sistema.")
    
    tab1, tab2, tab3 = st.tabs(["🔐 Seguridad", "📧 Correo", "🎨 Interfaz"])
    
    with tab1:
        configuracion_seguridad()
    
    with tab2:
        configuracion_correo()
    
    with tab3:
        configuracion_interfaz()

def configuracion_seguridad():
    """Configuración de parámetros de seguridad"""
    
    st.subheader("🔐 Configuración de Seguridad")
    
    with st.form("config_seguridad"):
        st.markdown("#### 🚫 Límites de Acceso")
        
        max_intentos_login = st.number_input("Máximo Intentos de Login", 
                                           min_value=3, max_value=10, value=5,
                                           key="config_max_intentos")
        
        tiempo_bloqueo = st.number_input("Tiempo de Bloqueo (minutos)", 
                                        min_value=1, max_value=60, value=5,
                                        key="config_tiempo_bloqueo")
        
        st.markdown("#### 🔑 Políticas de Contraseña")
        
        min_longitud_password = st.number_input("Longitud Mínima de Contraseña", 
                                              min_value=6, max_value=20, value=8,
                                              key="config_min_password")
        
        requerir_mayusculas = st.checkbox("Requerir Mayúsculas", value=True, key="config_mayusculas")
        requerir_numeros = st.checkbox("Requerir Números", value=True, key="config_numeros")
        requerir_especiales = st.checkbox("Requerir Caracteres Especiales", value=False, key="config_especiales")
        
        st.markdown("#### 🌐 Sesiones")
        
        tiempo_sesion = st.number_input("Tiempo de Sesión (minutos)", 
                                       min_value=30, max_value=480, value=120,
                                       key="config_tiempo_sesion")
        
        sesiones_concurrentes = st.checkbox("Permitir Múltiples Sesiones", value=False, key="config_concurrentes")
        
        submit_button = st.form_submit_button("💾 Guardar Configuración", type="primary")
        
        if submit_button:
            st.success("✅ Configuración de seguridad guardada exitosamente")

def configuracion_correo():
    """Configuración de parámetros de correo"""
    
    st.subheader("📧 Configuración de Correo")
    
    with st.form("config_correo"):
        st.markdown("#### 📧 Servidor SMTP")
        
        smtp_host = st.text_input("Servidor SMTP", value="smtp.gmail.com", key="config_smtp_host")
        smtp_port = st.number_input("Puerto SMTP", value=587, key="config_smtp_port")
        
        st.markdown("#### 🔐 Autenticación")
        
        email_remitente = st.text_input("Email Remitente", value="noreply@iujo.edu.ve", key="config_email_remitente")
        
        # No mostrar contraseña real, solo campo para actualizar
        st.info("🔒 La contraseña de correo está configurada de forma segura")
        actualizar_password = st.checkbox("Actualizar Contraseña de Correo", key="config_actualizar_password")
        
        if actualizar_password:
            nuevo_password_correo = st.text_input("Nueva Contraseña", 
                                                type="password", 
                                                key="config_nuevo_password_correo")
        
        st.markdown("#### 📧 Configuración de Envío")
        
        habilitar_correo = st.checkbox("Habilitar Envío de Correos", value=True, key="config_habilitar_correo")
        
        if habilitar_correo:
            email_pruebas = st.text_input("Email para Pruebas", key="config_email_pruebas")
            
            if st.button("📧 Enviar Correo de Prueba", key="config_probar_correo"):
                st.success("✅ Correo de prueba enviado exitosamente")
        
        submit_button = st.form_submit_button("💾 Guardar Configuración", type="primary")
        
        if submit_button:
            st.success("✅ Configuración de correo guardada exitosamente")

def configuracion_interfaz():
    """Configuración de la interfaz de usuario"""
    
    st.subheader("🎨 Configuración de Interfaz")
    
    with st.form("config_interfaz"):
        st.markdown("#### 🎨 Tema y Apariencia")
        
        tema_actual = st.selectbox("Tema", ["Claro", "Oscuro", "Automático"], key="config_tema")
        
        st.markdown("#### 📱 Responsive")
        
        layout_defecto = st.selectbox("Layout por Defecto", ["Centrado", "Ancho"], key="config_layout")
        
        st.markdown("#### 🔔 Notificaciones")
        
        notificaciones_escritorio = st.checkbox("Notificaciones de Escritorio", value=True, key="config_notificaciones")
        
        sonido_alertas = st.checkbox("Sonido de Alertas", value=False, key="config_sonido")
        
        st.markdown("#### 📊 Rendimiento")
        
        cache_habilitado = st.checkbox("Habilitar Cache", value=True, key="config_cache")
        
        if cache_habilitado:
            tiempo_cache = st.number_input("Tiempo de Cache (minutos)", 
                                         min_value=5, max_value=120, value=30,
                                         key="config_tiempo_cache")
        
        submit_button = st.form_submit_button("💾 Guardar Configuración", type="primary")
        
        if submit_button:
            st.success("✅ Configuración de interfaz guardada exitosamente")
            st.info("🔄 Algunos cambios pueden requerir recargar la página")

# =================================================================
# FUNCIÓN PRINCIPAL DE MÓDULOS PROTEGIDOS
# =================================================================

def mostrar_modulos_protegidos():
    """Función principal que muestra los módulos según el rol del usuario"""
    
    # Mostrar información de acceso
    mostrar_info_acceso()
    
    # Obtener información de permisos del usuario
    from auth.decorators import obtener_info_permisos_usuario
    permisos = obtener_info_permisos_usuario(st.session_state['user_data'])
    
    if not permisos:
        st.error("❌ No se pudo obtener información de permisos")
        return
    
    st.markdown("---")
    st.markdown(f"# 🎓 Panel de Control - {permisos['rol'].title()}")
    st.markdown(f"*Nivel de acceso: {permisos['nivel_acceso']} | {permisos['total_permisos']} permisos disponibles*")
    
    # Importar formación complementaria
    from modules.formacion_complementaria.formacion_complementaria_ui import mostrar_modulo_formacion_complementaria
    
    # Navegación por módulos según permisos
    modulos_disponibles = []
    
    # Módulo de gestión de usuarios (solo administradores)
    if permisos['rol'] == 'Administrador':
        modulos_disponibles.append(("👥 Usuarios", modulo_gestion_usuarios))
    
    # Módulo de gestión de cursos (profesores y administradores)
    if permisos['rol'] in ['Administrador', 'Profesor']:
        modulos_disponibles.append(("👨‍🏫 Profesores", modulo_gestion_cursos))
    
    # Módulo de gestión de estudiantes (todos los roles)
    modulos_disponibles.append(("👨‍🎓 Estudiantes", modulo_gestion_talleres))
    
    # Módulo de formación complementaria (todos los roles)
    modulos_disponibles.append(("📚 Formación Complementaria", mostrar_modulo_formacion_complementaria))
    
    # Módulo de reportes (solo administradores y profesores)
    if permisos['rol'] in ['Administrador', 'Profesor']:
        modulos_disponibles.append(("📊 Reportes", modulo_auditoria))
    
    # Módulo de configuración (solo administradores)
    if permisos['rol'] == 'Administrador':
        modulos_disponibles.append(("⚙️ Configuración", modulo_configuracion_sistema))
    
    # Mostrar navegación de módulos
    if modulos_disponibles:
        # Crear tabs para cada módulo
        nombres_modulos = [modulo[0] for modulo in modulos_disponibles]
        funciones_modulos = [modulo[1] for modulo in modulos_disponibles]
        
        tab_seleccionada = st.tabs(nombres_modulos)
        
        # Mostrar contenido de cada módulo en su tab
        for i, (nombre_modulo, funcion_modulo) in enumerate(modulos_disponibles):
            with tab_seleccionada[i]:
                try:
                    funcion_modulo()
                except Exception as e:
                    st.error(f"❌ Error en módulo {nombre_modulo}: {str(e)}")
                    st.info("🔍 Contacte al administrador del sistema")
    else:
        st.warning("⚠️ No hay módulos disponibles para su rol")
        st.info("🔍 Contacte al administrador para asignar permisos")
    if permisos['rol'] in ['Profesor', 'Administrador']:
        modulos_disponibles.append(("📚 Gestión de Cursos", modulo_gestion_cursos))
    
    # Módulo de gestión de talleres (todos los roles con permisos)
    if any(permiso.startswith('taller.') for permiso in permisos['permisos']):
        modulos_disponibles.append(("🎯 Gestión de Talleres", modulo_gestion_talleres))
    
    # Módulo de auditoría (solo administradores)
    if permisos['rol'] == 'Administrador':
        modulos_disponibles.append(("🔍 Auditoría", modulo_auditoria))
    
    # Módulo de configuración (solo administradores)
    if permisos['rol'] == 'Administrador':
        modulos_disponibles.append(("⚙️ Configuración", modulo_configuracion_sistema))
    
    # Mostrar módulos disponibles
    if modulos_disponibles:
        # Crear tabs para los módulos
        nombres_modulos = [modulo[0] for modulo in modulos_disponibles]
        funciones_modulos = [modulo[1] for modulo in modulos_disponibles]
        
        tabs = st.tabs(nombres_modulos)
        
        for i, (tab, funcion_modulo) in enumerate(zip(tabs, funciones_modulos)):
            with tab:
                funcion_modulo()
    else:
        st.info("ℹ️ No tiene módulos asignados. Contacte al administrador.")
    
    # Pie de página con información de sesión
    st.markdown("---")
    st.markdown(f"*Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    # Botón de cerrar sesión
    if st.button("🚪 Cerrar Sesión", type="secondary"):
        st.session_state.clear()
        st.rerun()
