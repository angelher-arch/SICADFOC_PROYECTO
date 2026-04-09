# -*- coding: utf-8 -*-
"""
FOC26.py - Sistema de Informacion de Control Academico de Formacion Complementaria
Instituto Universitario Jesus Obrero
Version 2.0 - Entorno de Desarrollo Limpio
"""

import streamlit as st
import pandas as pd
import psycopg2
import os
import locale
import hashlib
import sys
import random
import re

# Forzar UTF-8 a nivel del sistema
if sys.version_info[0] >= 3:
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'Spanish_Spain.1252')
        except:
            pass

# Importar módulos del sistema
from configuracion import get_carreras, get_semestres, get_estados_registro, get_generos
from transacciones import TransaccionFOC26
from gestion_estudiantil import modulo_gestion_estudiantil
from formacion_complementaria import modulo_formacion_complementaria
from ui_estilos import get_css_iujo
from version import get_version_info, display_version_info, get_short_version

# Forzar UTF-8 en variables de entorno
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LC_ALL'] = 'C.UTF-8'
os.environ['LANG'] = 'C.UTF-8'

# Variables globales para estado - DECLARADAS PRIMERO
db_connection = None
db_connected = False
db_error = None
debug_mode = os.getenv('DEBUG_MODE', 'False').lower() in ('1', 'true', 'yes')

# Clase de base de datos PostgreSQL exclusiva
class DatabaseFOC26:
    """Gestor de base de datos PostgreSQL para FOC26DB"""
    
    def __init__(self):
        self.connection = None
        self.is_connected = False
        
        # Configuración para PostgreSQL (local o Render)
        db_host = os.getenv('DB_HOST', 'localhost')
        
        # SSL solo para hosts externos (Render), no para localhost
        ssl_mode = 'require' if db_host != 'localhost' and 'render.com' in db_host else 'prefer'
        
        # Para localhost usar contraseña por defecto, para Render usar variable de entorno
        db_password = os.getenv('DB_PASSWORD', 'admin123') if db_host == 'localhost' else os.getenv('DB_PASSWORD', '')
        
        self.db_settings = {
            'dbname': os.getenv('DB_NAME', 'FOC26DB'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': db_password,
            'host': db_host,
            'port': int(os.getenv('DB_PORT', '5432')),
            'sslmode': ssl_mode
        }
        
        # Construir URL completa para Render
        password_part = f":{self.db_settings['password']}" if self.db_settings['password'] else ""
        self.database_url = f"postgresql://{self.db_settings['user']}{password_part}@{self.db_settings['host']}:{self.db_settings['port']}/{self.db_settings['dbname']}?sslmode={self.db_settings['sslmode']}"
        
        print(f"Database FOC26 inicializado para {self.db_settings['dbname']}")
        print(f"Host: {self.db_settings['host']}")
        print(f"Port: {self.db_settings['port']}")
        print(f"User: {self.db_settings['user']}")
        print(f"SSL Mode: {self.db_settings['sslmode']}")
        print(f"URL de conexion: {self.database_url}")
    
    def conectar(self):
        """Conectar a la base de datos FOC26DB usando variables de entorno"""
        try:
            if not self.connection or not self.is_connected:
                import psycopg2
                from psycopg2.extras import RealDictCursor
                from psycopg2 import OperationalError, InterfaceError, DatabaseError
                
                if debug_mode:
                    print(f"Intentando conectar con settings: {self.db_settings}")
                
                self.connection = psycopg2.connect(
                    cursor_factory=RealDictCursor,
                    client_encoding='utf8',
                    **self.db_settings
                )
                
                with self.connection.cursor() as cursor:
                    cursor.execute("SET client_encoding TO 'UTF8'")
                    cursor.execute("SET standard_conforming_strings TO ON")
                
                self.is_connected = True
                if debug_mode:
                    print("CONEXIÓN EXITOSA A POSTGRESQL")
                return True
                
        except OperationalError as e:
            error_msg = f"ERROR OPERACIONAL POSTGRESQL: {str(e)}"
            print(f"ERROR: {error_msg}")
            if debug_mode:
                print(f"Posibles causas: Credenciales incorrectas, host inaccesible, o firewall bloqueando")
            self.is_connected = False
            return False
            
        except InterfaceError as e:
            error_msg = f"ERROR DE INTERFAZ POSTGRESQL: {str(e)}"
            print(f"ERROR: {error_msg}")
            if debug_mode:
                print(f"Posibles causas: Problema de red, conexión SSL, o timeout")
            self.is_connected = False
            return False
            
        except DatabaseError as e:
            error_msg = f"ERROR DE BASE DE DATOS POSTGRESQL: {str(e)}"
            print(f"ERROR: {error_msg}")
            if debug_mode:
                print(f"Posibles causas: Base de datos no existe, permisos insuficientes")
            self.is_connected = False
            return False
            
        except Exception as e:
            error_msg = f"ERROR DESCONOCIDO POSTGRESQL: {type(e).__name__}: {str(e)}"
            print(f"ERROR: {error_msg}")
            if debug_mode:
                print(f"Error inesperado - revisar configuración y variables de entorno")
            self.is_connected = False
            return False
    
    def desconectar(self):
        """Desconectar de la base de datos"""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
                self.is_connected = False
                print("Desconexion exitosa de FOC26DB")
        except Exception as e:
            print(f"Error al desconectar de FOC26DB: {e}")
    
    def ejecutar_consulta(self, query, params=None):
        """Ejecutar consulta SQL con parametros"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Blindaje: asegurar conexión activa antes de usarla
                if not self.connection or not self.is_connected:
                    if not self.conectar():
                        return None
                
                # Blindaje adicional: verificar que connection no sea None
                if self.connection is None:
                    print("ERROR: self.connection es None, reintentando conexión")
                    self.is_connected = False
                    continue
                
                with self.connection.cursor() as cursor:
                    cursor.execute(query, params)
                    
                    if query.strip().upper().startswith('SELECT'):
                        resultados = cursor.fetchall()
                        # Devolver lista de diccionarios directamente
                        if resultados:
                            return [dict(row) for row in resultados]
                        else:
                            return []
                    else:
                        self.connection.commit()
                        return cursor.rowcount
            except Exception as e:
                print(f"Error ejecutando consulta (intento {attempt + 1}): {e}")
                if self.connection:
                    try:
                        self.connection.rollback()
                    except:
                        pass
                if attempt == max_retries - 1:
                    return None
                # Reintentar conexión
                self.is_connected = False
                continue
        return None
    
    def verificar_usuario(self, usuario_input, clave_input):
        """Verificar usuario y contrasena - ESQUEMA ESTRICTO"""
        try:
            if debug_mode:
                print(f"=== MODO DEBUG: VALIDACIÓN DE ACCESO ===")
                print(f"Usuario input: '{usuario_input}'")
                print(f"Clave input: '{clave_input}'")
            
            # Usar la conexión gestionada por self.conectar() y ejecutar directamente la consulta
            query = "SELECT contrasena, rol, login_usuario FROM usuario WHERE cedula_usuario = %s"
            if debug_mode:
                print(f"Query: {query}")
                print(f"Param: {usuario_input.strip()}")
            
            resultado = self.ejecutar_consulta(query, (usuario_input.strip(),))
            
            if debug_mode:
                print(f"Resultado de query: {resultado}")
            
            row = resultado[0] if resultado else None
            
            if row:
                db_clave = row.get('contrasena')
                db_rol = row.get('rol')
                db_email = row.get('login_usuario')
                
                # 2. Limpieza de espacios y comparación directa
                usuario_clean = str(usuario_input).strip()
                clave_clean = str(clave_input).strip()
                db_email_clean = str(db_email).strip() if db_email else ""
                db_clave_clean = str(db_clave).strip() if db_clave else ""
                
                if debug_mode:
                    print(f"Longitud clave input: {len(clave_clean)}")
                    print(f"Longitud clave DB: {len(db_clave_clean)}")
                    print(f"Clave input (repr): {repr(clave_clean)}")
                    print(f"Clave DB (repr): {repr(db_clave_clean)}")
                    print(f"Comparación clave: '{clave_clean}' == '{db_clave_clean}' -> {clave_clean == db_clave_clean}")
                
                # Solo comparar la contraseña ya que la cédula ya se validó en la query
                if clave_clean == db_clave_clean:
                    if debug_mode:
                        print(f"Acceso concedido para: {db_rol}")
                    
                    # 3. Construir datos completos del usuario
                    user_data = {
                        'rol': db_rol,
                        'login_usuario': db_email_clean,
                        'email': db_email_clean,
                        'cedula_usuario': usuario_clean,
                        'nombre': 'Usuario',
                        'apellido': 'Sistema'
                    }
                    
                    # 4. Actualizar variable global de estado de conexión
                    global db_connected, db_error
                    db_connected = True
                    db_error = None
                    if debug_mode:
                        print(f"Estado de conexión actualizado: db_connected={db_connected}")
                    
                    return user_data
                else:
                    if debug_mode:
                        print("Credenciales incorrectas - Contraseña no coincide")
                    return None
            else:
                if debug_mode:
                    print("Usuario no encontrado en la base de datos")
                return None
                
        except Exception as e:
            if debug_mode:
                print(f"Error crítico en verificar_usuario: {e}")
            return None
    
    def crear_usuario_admin(self):
        """Crear usuario administrador si no existe - SOLO POSTGRESQL"""
        try:
            if not self.conectar():
                return False, "No se pudo conectar a la base de datos"
            
            # Verificar si ya existe el admin
            query_verificar = "SELECT COUNT(*) as total FROM usuario WHERE login_usuario = %s"
            params = ('admin',)
            
            resultado = self.ejecutar_consulta(query_verificar, params)
            
            if resultado is not None and len(resultado) > 0:
                total = resultado[0]['total']
                if total > 0:
                    return True, "Usuario administrador ya existe"
            
            # Crear persona para el admin
            ADMIN_CEDULA = os.getenv('ADMIN_CEDULA', 'V-00000000')
            ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@iujo.edu')
            ADMIN_LOGIN = os.getenv('ADMIN_LOGIN', 'admin')
            ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'change_me')
            ADMIN_ROLE = os.getenv('ADMIN_ROLE', 'Admin')
            
            query_persona = """
            INSERT INTO persona (nombre, apellido, email, cedula, telefono) 
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
            RETURNING id
            """
            params_persona = ('Administrador', 'Sistema', ADMIN_EMAIL, ADMIN_CEDULA, '+58-212-0000000')
            
            resultado_persona = self.ejecutar_consulta(query_persona, params_persona)
            
            ADMIN_CEDULA = os.getenv('ADMIN_CEDULA', 'V-00000000')
            ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@iujo.edu')
            ADMIN_LOGIN = os.getenv('ADMIN_LOGIN', 'admin')
            ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'change_me')
            ADMIN_ROLE = os.getenv('ADMIN_ROLE', 'Admin')

            # Crear usuario admin
            query_usuario = """
            INSERT INTO usuario (id_persona, cedula_usuario, login_usuario, email, contrasena, rol, activo) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (login_usuario) DO NOTHING
            """
            params_usuario = (id_persona, ADMIN_CEDULA, ADMIN_LOGIN, ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_ROLE, True)
            
            resultado_usuario = self.ejecutar_consulta(query_usuario, params_usuario)
            
            if resultado_usuario is not None:
                return True, "Usuario administrador creado exitosamente"
            else:
                return False, "Error al crear usuario administrador"
                
        except Exception as e:
            print(f"Error al crear usuario admin: {e}")
            return False, f"Error al crear usuario administrador: {e}"
    
    def verificar_conexion(self):
        """Verificar estado de conexion"""
        try:
            if not self.is_connected or not self.connection:
                return self.conectar()
            
            # Ejecutar consulta simple para verificar
            resultado = self.ejecutar_consulta("SELECT 1 as test")
            return resultado is not None and len(resultado) > 0
            
        except Exception as e:
            print(f"Error al verificar conexion: {e}")
            self.is_connected = False
            return False

# Instancia global del gestor de base de datos
db = DatabaseFOC26()

# Conexion a base de datos FOC26DB - SOLO POSTGRESQL
def conectar_foc26db():
    """Conectar a la base de datos FOC26DB"""
    global db_connected, db_error
    
    try:
        if db is not None:
            if db.verificar_conexion():
                db_connected = True
                db_error = None
                print("FOC26DB conectado exitosamente")
                return True
            else:
                db_connected = False
                db_error = "No se pudo establecer conexion con FOC26DB"
                print("ERROR: No se pudo conectar a FOC26DB")
                print("REQUERIDO: PostgreSQL debe estar instalado y corriendo")
                return False
        else:
            db_connected = False
            db_error = "Database no disponible"
            print("ERROR: Database no disponible")
            return False
            
    except Exception as e:
        db_connected = False
        db_error = str(e)
        print(f"Error en conexion FOC26DB: {e}")
        return False

# CSS basico y limpio sin colores institucionales
def get_css_basico():
    """CSS basico y limpio para login con diseño neutro PowerPoint-like"""
    try:
        return """
<style>
/* Ocultar sidebar completamente en login */
[data-testid="stSidebar"] {
    display: none !important;
}

/* Botones principales */
.stButton > button {
    background-color: #F8F8F8;
    color: #000000;
    border: 2px solid #CCCCCC;
    border-radius: 5px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
    width: 100%;
    cursor: pointer;
}

.stButton > button:hover {
    background-color: #CCCCCC;
    border-color: #999999;
}

/* Campos de entrada */
.stTextInput > div > div > input {
    background: #FFFFFF;
    border: 2px solid #CCCCCC;
    border-radius: 5px;
    padding: 0.75rem;
    font-size: 1rem;
    color: #000000;
}

.stTextInput > div > div > input:focus {
    border-color: #999999;
    outline: none;
}

/* Alertas */
.stAlert {
    border-radius: 5px;
    margin: 1rem 0;
    padding: 1rem;
    border: 2px solid;
}

.stSuccess {
    background-color: #E6FFE6;
    color: #006400;
    border-color: #90EE90;
}

.stError {
    background-color: #FFE6E6;
    color: #8B0000;
    border-color: #FFB6C1;
}

.stWarning {
    background-color: #FFFFE6;
    color: #8B8000;
    border-color: #FFFF99;
}

.stInfo {
    background-color: #E6F3FF;
    color: #00008B;
    border-color: #ADD8E6;
}
</style>
"""
    except Exception as e:
        print(f"Error generando CSS: {e}")
        return ""

# Pantalla de login basica
def pantalla_login():
    """Pantalla de login basica y funcional"""
    try:
        # Logo con manejo seguro
        if os.path.exists("assets/Logo_IUJO.png"):
            st.markdown("""
            <div style="text-align: center; padding: 2rem;">
                <img src="assets/Logo_IUJO.png" alt="IUJO Logo" style="width: 120px; height: auto; margin-bottom: 1rem; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));">
            </div>
            """, unsafe_allow_html=True)
        
        # Titulos sin caracteres problemáticos
        st.markdown("### Sistema de Información de Control Académico de Formación Complementaria")
        st.markdown("### Instituto Universitario Jesús Obrero")
        
        # Verificar conexion y crear usuario admin si es necesario
        if db_connected and db is not None:
            try:
                # Crear usuario admin si no existe
                resultado = db.crear_usuario_admin()
                if resultado and len(resultado) == 2:
                    creado, mensaje = resultado
                    if creado:
                        st.success(f"{mensaje}")
                    else:
                        st.info(f"{mensaje}")
            except Exception as e:
                st.warning(f"Error en inicializacion: {e}")
        
        # Tabs para Login y Registro
        tab_login, tab_registro = st.tabs(["Iniciar Sesión", "Registrarse"])
        
        with tab_login:
            st.markdown("## Iniciar Sesión")
            
            with st.form("login_form"):
                cedula_input = st.text_input("Cédula", placeholder="Cédula (ej: V12345678)")
                password = st.text_input("Contrasena", type="password", placeholder="Contraseña segura")
                
                if st.form_submit_button("Iniciar Sesion"):
                    if cedula_input and password:
                        # Forzar reintento de conexión antes de validar
                        if debug_mode:
                            print("=== BOTÓN INICIAR SESIÓN PRESIONADO ===")
                            print("Forzando reintento de conexión a PostgreSQL...")
                        
                        # Reiniciar conexión para asegurar estado fresco
                        db.is_connected = False
                        db.connection = None
                        
                        # Intentar conexión explícita
                        if db.conectar():
                            if debug_mode:
                                print("Conexión establecida, verificando credenciales...")
                            usuario = db.verificar_usuario(cedula_input, password)
                            
                            if usuario:
                                st.session_state['autenticado'] = True
                                st.session_state['user'] = usuario
                                st.success(f"Bienvenido {usuario['email']}!")
                                st.rerun()
                            else:
                                st.error("Credenciales incorrectas")
                        else:
                            # Solo mostrar error si la base de datos es inalcanzable
                            st.error("No se puede conectar a la base de datos. Verifique que PostgreSQL esté corriendo.")
                    else:
                        st.error("Por favor, completa todos los campos")
        
        with tab_registro:
            st.info("Módulo de registro en desarrollo")
    
    except Exception as e:
        if debug_mode:
            print(f"Error en pantalla_login: {e}")
        st.error("Error en la pantalla de login")

# Dashboard basico
def dashboard_basico():
    """Dashboard basico y funcional"""
    try:
        st.header("Dashboard")
        
        # Asegurar sesión persistente - verificar conexión activa
        global db_connected, db_error
        if not db_connected or db is None:
            if db.conectar():
                db_connected = True
                db_error = None
                print("Sesión persistente: Conexión restaurada")
            else:
                db_connected = False
                db_error = "No se pudo restaurar conexión"
                print("Sesión persistente: Error restaurando conexión")
        
        user = st.session_state['user']
        st.success(f"Bienvenido {user['email']} ({user['rol']})")
        
        # Información de versión
        with st.expander("ℹ️ Información del Sistema", expanded=False):
            version_info = get_version_info()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Versión", version_info['version'])
                st.metric("Plataforma", version_info['platform'])
            with col2:
                st.metric("Build Date", version_info['build_date'])
                st.metric("Git Branch", version_info['git_branch'])
            if version_info['git_commit'] != 'N/A':
                st.info(f"Último Commit: {version_info['git_commit']}")
        
        # Eliminados banners de error para UI limpia
        # st.markdown("### Sistema Operativo")
        # st.markdown("El frontend esta funcionando correctamente.")
        # st.markdown(f"**Base de Datos:** FOC26DB (PostgreSQL)")
        # st.markdown(f"**Estado Conexion:** {'Conectada' if db_connected else 'Desconectada'}")
        
        # if db_error:
        #     st.error(f"Error: {db_error}")
        
        # Boton de cerrar sesion - mantener persistencia
        if st.button("Cerrar Sesion"):
            st.session_state['autenticado'] = False
            st.session_state['user'] = None
            # Opcional: cerrar conexión al salir
            if db and db.connection:
                db.desconectar()
                print("Sesión cerrada: Conexión terminada")

    except Exception as e:
        st.error(f"Error en dashboard: {e}")

# Modulo de Estudiantes
def modulo_estudiantes():
    """Modulo para gestion de estudiantes"""
    try:
        st.header("Gestión de Estudiantes")

        # Crear tabs para estudiantes
        tab1, tab2 = st.tabs(["Estudiantes Registrados", "Registrar Nuevo Estudiante"])

        with tab1:
            st.subheader("Estudiantes Registrados")

            if db_connected and db is not None:
                # Consultar estudiantes con tablas reales
                query = """
                SELECT
                    u.id_usuario as usuario_id,
                    u.login_usuario as email,
                    u.rol,
                    p.nombre,
                    p.apellido,
                    p.cedula,
                    p.telefono,
                    p.fecha_nacimiento,
                    p.genero as sexo,
                    p.direccion,
                    u.rol as estado_registro,
                    u.login_usuario as fecha_registro
                FROM usuario u
                JOIN persona p ON u.cedula_usuario = p.cedula
                WHERE u.rol = 'Estudiante'
                ORDER BY p.apellido, p.nombre
                """

                resultado = db.ejecutar_consulta(query)

                if resultado is not None and len(resultado) > 0:
                    # Dataframe con estilo
                    st.dataframe(
                        resultado[['nombre', 'apellido', 'cedula', 'telefono', 'email', 'estado_registro']],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "nombre": st.column_config.TextColumn("Nombres"),
                            "apellido": st.column_config.TextColumn("Apellidos"),
                            "cedula": st.column_config.TextColumn("Cédula"),
                            "telefono": st.column_config.TextColumn("Teléfono"),
                            "email": st.column_config.TextColumn("Correo"),
                            "estado_registro": st.column_config.TextColumn("Estado")
                        }
                    )

                    # Estadísticas con diseño IUJO
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Total Estudiantes", len(resultado), delta="Activos")
                    with col2:
                        activos = resultado[resultado['estado_registro'] == True]
                        st.metric("Estudiantes Activos", len(activos))
                    with col3:
                        femeninos = resultado[resultado['sexo'] == 'Femenino']
                        st.metric("Estudiantes Mujeres", len(femeninos))
                    with col4:
                        masculinos = resultado[resultado['sexo'] == 'Masculino']
                        st.metric("Estudiantes Hombres", len(masculinos))
                else:
                    st.info("No hay estudiantes registrados")
            else:
                st.error("No hay conexión a la base de datos")

        with tab2:
            st.subheader("Registrar Nuevo Estudiante")

            with st.form("form_estudiante_registro"):
                st.markdown("### Datos Personales")

                # Primera fila de campos
                col1, col2 = st.columns(2)

                with col1:
                    nombre = st.text_input("Nombres*", placeholder="Juan Carlos", help="Nombres completos del estudiante")
                    cedula = st.text_input("Cédula Estudiante*", placeholder="V-12345678", help="Número de cédula con formato V-XXXXXXXX")
                    telefono = st.text_input("Teléfono", placeholder="+58-212-1234567", help="Teléfono de contacto")

                with col2:
                    apellido = st.text_input("Apellidos*", placeholder="Pérez González", help="Apellidos completos del estudiante")
                    email = st.text_input("Correo Electrónico*", placeholder="juan.perez@iujo.edu", help="Correo institucional o personal")
                    sexo = st.selectbox("Sexo", ["Masculino", "Femenino", "Otro"], help="Género del estudiante")

                # Segunda fila de campos
                col3, col4 = st.columns(2)

                with col3:
                    fecha_nacimiento = st.date_input("Fecha de Nacimiento", help="Fecha de nacimiento del estudiante")
                    carrera = st.selectbox("Carrera", [
                        "Ingeniería de Sistemas",
                        "Ingeniería Civil",
                        "Ingeniería Electrónica",
                        "Administración",
                        "Contaduría Pública",
                        "Derecho",
                        "Psicología",
                        "Comunicación Social",
                        "Otra"
                    ], help="Carrera que cursa el estudiante")

                with col4:
                    semestre = st.number_input("Semestre Actual", min_value=1, max_value=12, value=1, help="Semestre que cursa actualmente")
                    estado_registro = st.selectbox("Estado Registro", ["Activo", "Inactivo", "Suspendido"], help="Estado académico del estudiante")
                    direccion = st.text_area("Dirección", placeholder="Dirección completa del estudiante", help="Dirección de residencia")

                # Campos adicionales
                st.markdown("### Datos de Acceso")
                contrasena = st.text_input("Contraseña Temporal", type="password", placeholder="Estudiante123", help="Contraseña temporal para el estudiante")

                # Botones de acción
                col5, col6 = st.columns([3, 1])

                with col5:
                    submit_button = st.form_submit_button("Registrar Estudiante", type="primary")

                with col6:
                    limpiar_button = st.form_submit_button("Limpiar")

                if submit_button:
                    if nombre and apellido and cedula and email:
                        try:
                            # Verificar si la cédula ya existe
                            cedula_existe = db.ejecutar_consulta("SELECT id FROM persona WHERE cedula = %s", (cedula,))
                            if cedula_existe is not None and len(cedula_existe) > 0:
                                st.error("Ya existe una persona con esta cédula")
                            else:
                                # Verificar si el email ya existe
                                email_existe = db.ejecutar_consulta("SELECT id FROM persona WHERE email = %s", (email,))
                                if email_existe is not None and len(email_existe) > 0:
                                    st.error("Ya existe una persona con este correo electrónico")
                                else:
                                    # Insertar en tabla persona
                                    persona_query = """
                                    INSERT INTO persona (nombre, apellido, email, cedula, telefono, fecha_nacimiento, genero, direccion)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                    RETURNING id
                                    """
                                    persona_result = db.ejecutar_consulta(persona_query, (
                                        nombre, apellido, email, cedula, telefono, fecha_nacimiento, sexo, direccion
                                    ))

                                    if persona_result is not None and len(persona_result) > 0:
                                        id_persona = persona_result[0]['id']

                                        # Insertar en tabla usuario
                                        usuario_query = """
                                        INSERT INTO usuario (id_persona, email, contrasena, rol, activo)
                                        VALUES (%s, %s, %s, %s, %s)
                                        """
                                        usuario_result = db.ejecutar_consulta(usuario_query, (
                                            id_persona, email, contrasena or 'Estudiante123', 'Estudiante',
                                            estado_registro == 'Activo'
                                        ))

                                        if usuario_result is not None:
                                            st.success(f"Estudiante {nombre} {apellido} registrado exitosamente!")
                                            st.info(f"Usuario: {email} | Contraseña temporal: {contrasena or 'Estudiante123'}")
                                            st.rerun()
                                        else:
                                            st.error("Error al registrar el usuario del estudiante")
                                    else:
                                        st.error("Error al registrar los datos personales del estudiante")
                        except Exception as e:
                            st.error(f"Error al registrar estudiante: {e}")
                    else:
                        st.error("Por favor, complete todos los campos obligatorios (*)")

    except Exception as e:
        st.error(f"Error en módulo de estudiantes: {e}")

# Modulo de Profesores
def modulo_profesores():
    """Módulo para gestión de profesores"""
    try:
        st.header("Gestión de Profesores")
        trans_manager = TransaccionFOC26(db.connection)

        if not db_connected or db is None:
            st.error("No hay conexión a la base de datos")
            return

        tab1, tab2 = st.tabs(["Lista de Profesores", "Registrar Profesor"])

        with tab1:
            st.subheader("Profesores registrados")
            query = """
                SELECT pr.id_profesor, pr.cedula_profesor, p.nombre, p.apellido, p.email as email_institucional,
                       pr.correo_personal, pr.especialidad, pr.departamento, pr.estado, u.id as id_usuario, pr.id_persona
                FROM profesor pr
                JOIN persona p ON pr.id_persona = p.id
                JOIN usuario u ON pr.id_usuario = u.id
                ORDER BY p.apellido, p.nombre
            """
            profesores = db.ejecutar_consulta(query)

            if profesores is None or len(profesores) == 0:
                st.info("No hay profesores registrados")
            else:
                df_profesores = pd.DataFrame(profesores)
                st.dataframe(
                    df_profesores[[
                        'cedula_profesor', 'nombre', 'apellido', 'especialidad',
                        'departamento', 'correo_personal', 'estado'
                    ]],
                    use_container_width=True
                )

                selected_option = st.selectbox(
                    "Seleccionar profesor",
                    [f"{row['cedula_profesor']} - {row['apellido']}, {row['nombre']}" for _, row in df_profesores.iterrows()]
                )
                selected_cedula = selected_option.split(' - ')[0]
                profesor_seleccionado = df_profesores[df_profesores['cedula_profesor'] == selected_cedula].iloc[0]
                accion = st.radio("Acción", ["Consultar", "Editar", "Eliminar"])

                if accion == "Consultar":
                    st.markdown("### Detalles del profesor")
                    st.write({
                        'Cédula Profesor': profesor_seleccionado['cedula_profesor'],
                        'Nombre': profesor_seleccionado['nombre'],
                        'Apellido': profesor_seleccionado['apellido'],
                        'Email Institucional': profesor_seleccionado['email_institucional'],
                        'Correo Personal': profesor_seleccionado['correo_personal'],
                        'Especialidad': profesor_seleccionado['especialidad'],
                        'Departamento': profesor_seleccionado['departamento'],
                        'Estado': profesor_seleccionado['estado']
                    })

                elif accion == "Editar":
                    with st.form("form_editar_profesor"):
                        col1, col2 = st.columns(2)
                        with col1:
                            nombre = st.text_input("Nombre*", value=profesor_seleccionado['nombre'])
                            apellido = st.text_input("Apellido*", value=profesor_seleccionado['apellido'])
                            email_institucional = st.text_input("Email Institucional*", value=profesor_seleccionado['email_institucional'])
                            correo_personal = st.text_input("Correo Personal", value=profesor_seleccionado['correo_personal'] or "")
                        with col2:
                            especialidad = st.text_input("Especialidad", value=profesor_seleccionado['especialidad'] or "")
                            departamento = st.text_input("Departamento", value=profesor_seleccionado['departamento'] or "")
                            estado = st.selectbox(
                                "Estado", ['Activo', 'Inactivo'],
                                index=0 if profesor_seleccionado['estado'] == 'Activo' else 1
                            )
                            st.write(f"**Cédula:** {profesor_seleccionado['cedula_profesor']}")

                        if st.form_submit_button("Guardar cambios"):
                            if not re.match(r"[^@]+@[^@]+\.[^@]+", email_institucional):
                                st.error("Formato de correo institucional inválido")
                            elif correo_personal and not re.match(r"[^@]+@[^@]+\.[^@]+", correo_personal):
                                st.error("Formato de correo personal inválido")
                            else:
                                db.ejecutar_consulta(
                                    "UPDATE persona SET nombre = %s, apellido = %s, email = %s WHERE id = %s",
                                    (nombre.strip(), apellido.strip(), email_institucional.strip(), profesor_seleccionado['id_persona'])
                                )
                                db.ejecutar_consulta(
                                    "UPDATE usuario SET email = %s WHERE id = %s",
                                    (email_institucional.strip(), profesor_seleccionado['id_usuario'])
                                )
                                db.ejecutar_consulta(
                                    "UPDATE profesor SET correo_personal = %s, especialidad = %s, departamento = %s, estado = %s WHERE id_profesor = %s",
                                    (correo_personal.strip(), especialidad.strip(), departamento.strip(), estado, profesor_seleccionado['id_profesor'])
                                )
                                st.success("Datos de profesor actualizados correctamente")
                                st.experimental_rerun()

                elif accion == "Eliminar":
                    st.warning("La acción de eliminar desactivará el usuario y pondrá el profesor como inactivo.")
                    if st.button("Eliminar profesor"):
                        db.ejecutar_consulta(
                            "UPDATE usuario SET activo = FALSE WHERE id = %s",
                            (profesor_seleccionado['id_usuario'],)
                        )
                        db.ejecutar_consulta(
                            "UPDATE profesor SET estado = 'Inactivo' WHERE id_profesor = %s",
                            (profesor_seleccionado['id_profesor'],)
                        )
                        st.success("Profesor desactivado correctamente")
                        st.experimental_rerun()

        with tab2:
            st.subheader("Registrar Profesor")
            with st.form("form_nuevo_profesor"):
                col1, col2 = st.columns(2)
                with col1:
                    nombre = st.text_input("Nombre*", placeholder="María")
                    apellido = st.text_input("Apellido*", placeholder="López Pérez")
                    cedula = st.text_input("Cédula Profesor*", placeholder="V-12345678")
                    email_institucional = st.text_input("Email Institucional*", placeholder="maria.lopez@iujo.edu")
                    correo_personal = st.text_input("Correo Personal*", placeholder="maria.personal@gmail.com")
                with col2:
                    codigo_profesor = st.text_input("Código Profesor", placeholder="PROF-2026-001")
                    especialidad = st.text_input("Especialidad*", placeholder="Matemáticas Aplicadas")
                    departamento = st.text_input("Departamento*", placeholder="Ingeniería de Sistemas")
                    estado = st.selectbox("Estado", ['Activo', 'Inactivo'])

                st.markdown("**El login y la contraseña inicial del profesor serán la cédula ingresada.**")
                if st.form_submit_button("Guardar Profesor"):
                    if nombre and apellido and cedula and email_institucional and correo_personal and especialidad and departamento:
                        if not re.match(r"[^@]+@[^@]+\.[^@]+", email_institucional):
                            st.error("Formato de correo institucional inválido")
                        elif not re.match(r"[^@]+@[^@]+\.[^@]+", correo_personal):
                            st.error("Formato de correo personal inválido")
                        else:
                            datos_profesor = {
                                'nombre': nombre.strip(),
                                'apellido': apellido.strip(),
                                'cedula': str(cedula).strip(),
                                'email': email_institucional.strip(),
                                'telefono': '',
                                'direccion': '',
                                'correo_personal': correo_personal.strip(),
                                'codigo_profesor': codigo_profesor.strip() if codigo_profesor else None,
                                'especialidad': especialidad.strip(),
                                'departamento': departamento.strip(),
                                'categoria': None,
                                'estado': estado
                            }
                            resultado = trans_manager.crear_profesor_transaccional(datos_profesor)
                            if resultado['exito']:
                                st.success('Profesor registrado correctamente.')
                                st.info(f"Login inicial: {datos_profesor['cedula']}")
                                st.info(f"Contraseña inicial: {datos_profesor['cedula']}")
                                st.experimental_rerun()
                            else:
                                st.error(f"Error: {resultado['error']}")
                    else:
                        st.error('Complete todos los campos obligatorios.')

    except Exception as e:
        st.error(f"Error en módulo de profesores: {e}")

# El módulo de formación complementaria se importa desde formacion_complementaria.py
# y se ejecuta directamente en la navegación principal.

# Modulo de Registro de Usuario
def modulo_registro_usuario():
    """Modulo para registro de nuevos usuarios con CAPTCHA"""
    try:
        st.header("Registro de Nuevo Usuario")
        
        # Generar CAPTCHA si no existe en session_state
        if 'captcha_code' not in st.session_state:
            st.session_state['captcha_code'] = str(random.randint(1000, 9999))
        
        with st.form("form_registro_usuario"):
            st.markdown("### Datos de Registro")
            
            col1, col2 = st.columns(2)
            
            with col1:
                cedula = st.text_input("Cédula*", placeholder="V12345678", help="Número de cédula con formato V-XXXXXXXX")
                email = st.text_input("Correo Electrónico*", placeholder="usuario@iujo.edu", help="Correo electrónico válido")
            
            with col2:
                contrasena = st.text_input("Contraseña*", type="password", placeholder="Mínimo 6 caracteres", help="Contraseña segura")
                confirmar_contrasena = st.text_input("Confirmar Contraseña*", type="password", placeholder="Repita la contraseña", help="Debe coincidir con la contraseña")
            
            st.markdown("### Validación CAPTCHA")
            
            col3, col4 = st.columns([1, 2])
            
            with col3:
                st.markdown("**Código CAPTCHA:**")
                st.markdown(f"<h2 style='color: #000; font-weight: bold; text-align: center;'>{st.session_state['captcha_code']}</h2>", unsafe_allow_html=True)
            
            with col4:
                captcha_input = st.text_input("Ingrese el código CAPTCHA*", placeholder="1234", help="Copie exactamente el código mostrado arriba")
            
            # Botones
            col5, col6 = st.columns([3, 1])
            
            with col5:
                submit_button = st.form_submit_button("Registrar Usuario", type="primary")
            
            with col6:
                refresh_button = st.form_submit_button("Nuevo CAPTCHA")
            
            if refresh_button:
                st.session_state['captcha_code'] = str(random.randint(1000, 9999))
                st.rerun()
            
            if submit_button:
                if cedula and email and contrasena and confirmar_contrasena and captcha_input:
                    # Validar CAPTCHA
                    if captcha_input.strip() != st.session_state['captcha_code']:
                        st.error("Código CAPTCHA incorrecto. Intente nuevamente.")
                        st.session_state['captcha_code'] = str(random.randint(1000, 9999))
                        return
                    
                    # Validar contraseñas
                    if contrasena != confirmar_contrasena:
                        st.error("Las contraseñas no coinciden.")
                        return
                    
                    if len(contrasena) < 6:
                        st.error("La contraseña debe tener al menos 6 caracteres.")
                        return
                    
                    # Validar cédula: convertir a str y verificar formato
                    cedula_str = str(cedula).strip()
                    if not cedula_str.startswith('V') or len(cedula_str) < 9:
                        st.error("Formato de cédula inválido. Debe comenzar con V y tener al menos 9 caracteres.")
                        return
                    
                    # Validar cédula: convertir a str y verificar formato
                    cedula_str = str(cedula).strip()
                    if not cedula_str.startswith('V') or len(cedula_str) < 9:
                        st.error("Formato de cédula inválido. Debe comenzar con V y tener al menos 9 caracteres.")
                        return
                    
                    try:
                        if db_connected and db is not None:
                            # Verificar si la cédula ya existe
                            cedula_existe = db.ejecutar_consulta("SELECT id_usuario FROM usuario WHERE cedula_usuario = %s", (cedula_str,))
                            if cedula_existe is not None and len(cedula_existe) > 0:
                                st.error("Ya existe un usuario con esta cédula.")
                                return
                            
                            # Verificar si el email ya existe
                            email_existe = db.ejecutar_consulta("SELECT id_usuario FROM usuario WHERE login_usuario = %s", (email,))
                            if email_existe is not None and len(email_existe) > 0:
                                st.error("Ya existe un usuario con este correo electrónico.")
                                return
                            
                            # Insertar directamente en tabla usuario
                            usuario_query = """
                            INSERT INTO usuario (cedula_usuario, login_usuario, contrasena, rol, activo)
                            VALUES (%s, %s, %s, %s, %s)
                            """
                            usuario_result = db.ejecutar_consulta(usuario_query, (cedula_str, email, contrasena, 'Estudiante', True))
                            
                            if usuario_result is not None:
                                st.success(f"Usuario registrado exitosamente!")
                                st.info(f"Cédula: {cedula_str}")
                                st.info(f"Email: {email}")
                                st.info("Ahora puede iniciar sesión con sus credenciales.")
                                
                                # Limpiar CAPTCHA
                                st.session_state['captcha_code'] = str(random.randint(1000, 9999))
                                
                                # Opcional: redirigir a login
                                st.session_state['pagina'] = 'Inicio'  # O cambiar a login si existe
                                st.rerun()
                            else:
                                st.error("Error al registrar el usuario.")
                        else:
                            st.error("No hay conexión a la base de datos.")
                    except Exception as e:
                        st.error(f"Error al registrar usuario: {e}")
                else:
                    st.error("Por favor, complete todos los campos obligatorios (*).")
    
    except Exception as e:
        st.error(f"Error en módulo de registro: {e}")

# Funcion principal basica
def main():
    """Funcion principal basica y funcional"""
    try:
        # Configuracion de pagina basica
        st.set_page_config(
            page_title="SICADFOC 2026",
            page_icon="",
            layout="centered",
            initial_sidebar_state="collapsed"
        )
        
        # Aplicar CSS basico
        st.markdown(get_css_basico(), unsafe_allow_html=True)
        
        # Intentar conexion a FOC26DB
        conectar_foc26db()
        
        # Siempre mostrar login primero
        if not st.session_state.get('autenticado', False):
            pantalla_login()
        else:
            # Mostrar sidebar solo despues de login exitoso
            st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                display: block !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Sidebar dinamico con navegacion
            with st.sidebar:
                st.markdown("### Navegacion")
                
                # Informacion del usuario
                user = st.session_state['user']
                st.success(f"**{user['email']}**")
                st.info(f"Rol: {user['rol']}")
                st.markdown("---")
                
                # Menu de navegacion dinamico
                pagina = st.radio(
                    "Seleccionar Módulo:",
                    ['Inicio', 'Estudiantes', 'Profesores', 'Formacion Complementaria'],
                    key='pagina'
                )
                
                st.markdown("---")
                
                # Boton de cerrar sesion
                if st.button("Cerrar Sesion", type="secondary"):
                    st.session_state['autenticado'] = False
                    st.session_state['user'] = None
                    st.rerun()
            
            # Mostrar el modulo correspondiente
            if st.session_state['pagina'] == 'Inicio':
                dashboard_basico()
            elif st.session_state['pagina'] == 'Estudiantes':
                modulo_estudiantes()
            elif st.session_state['pagina'] == 'Profesores':
                modulo_profesores()
            elif st.session_state['pagina'] == 'Formacion Complementaria':
                modulo_formacion_complementaria(db)
        
    except Exception as e:
        st.error(f"Error critico en la aplicacion: {e}")
        st.markdown("### La aplicacion ha encontrado un error inesperado")
        st.markdown("Por favor, recarga la pagina.")

if __name__ == "__main__":
    # Inicializacion de sesion basica
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    if 'pagina' not in st.session_state:
        st.session_state['pagina'] = 'dashboard'
    
    # EJECUTAR SIEMPRE
    main()
