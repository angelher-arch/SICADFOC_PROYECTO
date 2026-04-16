# -*- coding: utf-8 -*-
"""
FOC26.py - Sistema de Informacion de Control Academico de Formacion Complementaria
Instituto Universitario Jesus Obrero
Version 2.0 - Entorno de Desarrollo Limpio
"""

import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import psycopg2  # type: ignore
from psycopg2.extras import RealDictCursor  # type: ignore
from psycopg2 import OperationalError, InterfaceError, DatabaseError  # type: ignore
import os
import locale
import hashlib
import sys
import random
import re
from conexion_postgresql import ConexionPostgreSQL

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
from modulo_configuracion import get_configuracion, get_informacion_institucional
from styles import get_global_styles
from version import get_version_info, display_version_info, get_short_version
from seguridad import (
    SeguridadFOC26,
    admin_required,
    profesor_required,
    estudiante_required,
    login_required,
    registro_usuario_dinamico,
    modulo_recuperacion_contrasena,
    hash_password,
    verify_password,
    is_sha256_hash
)

# Forzar UTF-8 en variables de entorno
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LC_ALL'] = 'C.UTF-8'
os.environ['LANG'] = 'C.UTF-8'

# Variables globales para estado - DECLARADAS PRIMERO
db_connection = None
db_connected = False
db_error = None
debug_mode = os.getenv('DEBUG_MODE', 'False').lower() in ('1', 'true', 'yes')

# Clase de base de datos PostgreSQL con conexión dinámica para Railway
class DatabaseFOC26:
    """Gestor de base de datos PostgreSQL para FOC26DB con configuración dinámica"""
    
    def __init__(self):
        self.connection = None
        self.is_connected = False
        self.db_error = None
        self.conexion_manager = ConexionPostgreSQL()
        
        # Obtener información de conexión
        info = self.conexion_manager.obtener_info_conexion()
        self.db_settings = {
            'dbname': info['database'],
            'user': info['user'],
            'password': info.get('password', ''),
            'host': info['host'],
            'port': info['port'],
            'sslmode': info['sslmode']
        }
        
        # URL de conexión para debugging (sin contraseña)
        self.database_url = f"postgresql://{info['user']}@{info['host']}:{info['port']}/{info['database']}?sslmode={info['sslmode']}"
        
        if info['source'] == 'railway':
            print("Database FOC26 inicializado para Railway")
        else:
            print("Database FOC26 inicializado para Local")
        
        print(f"Database: {info['database']}")
        print(f"Host: {info['host']}")
        print(f"Port: {info['port']}")
        print(f"User: {info['user']}")
        print(f"SSL: {info['sslmode']}")
        print(f"Source: {info['source']}")
    
    def conectar(self):
        """Conectar a la base de datos FOC26DB usando conexión dinámica"""
        try:
            if not self.connection or not self.is_connected:
                if debug_mode:
                    print(f"Intentando conectar con settings: {self.db_settings}")
                
                # Usar conexión dinámica con fallback
                self.connection = self.conexion_manager.conectar()
                self.is_connected = True
                self.db_error = None
                print("Conexión exitosa a PostgreSQL FOC26DB")
            return self.connection
        except OperationalError as e:
            error_msg = f"Error de conexión a PostgreSQL: {str(e)}"
            print(f"ERROR: {error_msg}")
            self.db_error = error_msg
            self.connection = None
            self.is_connected = False
            return None
        except InterfaceError as e:
            error_msg = f"Error de interfaz PostgreSQL: {str(e)}"
            print(f"ERROR: {error_msg}")
            self.db_error = error_msg
            self.connection = None
            self.is_connected = False
            return None
        except DatabaseError as e:
            error_msg = f"Error de base de datos PostgreSQL: {str(e)}"
            print(f"ERROR: {error_msg}")
            self.db_error = error_msg
            self.connection = None
            print(f"Posibles causas: Base de datos no existe, permisos insuficientes")
            self.is_connected = False
            return False
            
        except Exception as e:
            error_msg = f"ERROR DESCONOCIDO POSTGRESQL: {type(e).__name__}: {str(e)}"
            print(f"ERROR: {error_msg}")
            self.db_error = error_msg
            if debug_mode:
                print(f"Error inesperado - revisar configuración y variables de entorno")
            self.is_connected = False
            return False
    
    def desconectar(self):
        """Desconectar de la base de datos"""
        try:
            # Usar conexión dinámica
            if hasattr(self, 'conexion_manager'):
                self.conexion_manager.desconectar()
            
            if self.connection and not self.connection.closed:
                self.connection.close()
                self.is_connected = False
                print("🔌 Desconexión exitosa de PostgreSQL FOC26DB")
        except Exception as e:
            print(f"Error desconectando: {e}")
    
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
                    
                    if cursor.description is not None:
                        resultados = cursor.fetchall()
                        # Commit INSERT ... RETURNING results; SELECT queries do not need commit.
                        if not query.strip().upper().startswith('SELECT'):
                            self.connection.commit()
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
                    print(f"Comparación clave: '{clave_clean}' == '{db_clave_clean}'")

                if verify_password(db_clave_clean, clave_clean):
                    # Migrar contraseñas almacenadas en texto plano a hash al primer login exitoso
                    if not is_sha256_hash(db_clave_clean) and db_clave_clean == clave_clean:
                        hashed = hash_password(clave_clean)
                        self.ejecutar_consulta(
                            "UPDATE usuario SET contrasena = %s WHERE cedula_usuario = %s",
                            (hashed, usuario_clean)
                        )

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
            
            # Cargar valores del administrador desde variables de entorno
            ADMIN_CEDULA = os.getenv('ADMIN_CEDULA', 'V-00000000')
            ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@iujo.edu')
            ADMIN_LOGIN = os.getenv('ADMIN_LOGIN', 'admin')
            ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'change_me')
            ADMIN_ROLE = os.getenv('ADMIN_ROLE', 'Admin')

            # Verificar si ya existe el admin por login, email o cédula
            query_verificar = "SELECT COUNT(*) as total FROM usuario WHERE login_usuario = %s OR email = %s OR cedula_usuario = %s"
            params = (ADMIN_LOGIN, ADMIN_EMAIL, ADMIN_CEDULA)
            
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
            
            id_persona = resultado_persona[0]['id'] if resultado_persona else None
            if not id_persona:
                # Si la persona ya existía, leer su id desde la tabla
                persona_existente = self.ejecutar_consulta("SELECT id FROM persona WHERE email = %s", (ADMIN_EMAIL,))
                id_persona = persona_existente[0]['id'] if persona_existente else None
            
            if not id_persona:
                return False, "Error al crear persona para administrador"
            
            ADMIN_CEDULA = os.getenv('ADMIN_CEDULA', 'V-00000000')
            ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@iujo.edu')
            ADMIN_LOGIN = os.getenv('ADMIN_LOGIN', 'admin')
            ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'change_me')
            ADMIN_ROLE = os.getenv('ADMIN_ROLE', 'Admin')
            ADMIN_PASSWORD_HASH = hash_password(ADMIN_PASSWORD)

            # Crear usuario admin
            query_usuario = """
            INSERT INTO usuario (id_persona, cedula_usuario, login_usuario, email, contrasena, rol, activo) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (login_usuario) DO NOTHING
            """
            params_usuario = (id_persona, ADMIN_CEDULA, ADMIN_LOGIN, ADMIN_EMAIL, ADMIN_PASSWORD_HASH, ADMIN_ROLE, True)
            
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

# Función para generar reportes dinámicos
def generar_reporte_dinamico(tipo_reporte, db_instance):
    """Genera reportes dinámicos basados en el tipo seleccionado"""
    try:
        if not db_instance or not db_instance.verificar_conexion():
            st.error("No hay conexión a la base de datos")
            return
        
        query = ""
        
        if tipo_reporte == "Formación Complementaria":
            query = """
            SELECT 
                fc.id as id_formacion,
                fc.nombre_taller,
                fc.descripcion,
                fc.fecha_inicio,
                fc.fecha_fin,
                fc.cupo_maximo,
                fc.estado,
                p.nombre as profesor_nombre,
                p.apellido as profesor_apellido,
                COUNT(i.id_estudiante) as inscritos
            FROM formacion_complementaria fc
            LEFT JOIN persona p ON fc.id_profesor = p.id
            LEFT JOIN inscripcion i ON fc.id = i.id_formacion
            GROUP BY fc.id, fc.nombre_taller, fc.descripcion, fc.fecha_inicio, 
                     fc.fecha_fin, fc.cupo_maximo, fc.estado, p.nombre, p.apellido
            ORDER BY fc.fecha_inicio DESC
            """
            
        elif tipo_reporte == "Profesores":
            query = """
            SELECT 
                p.id,
                p.nombre,
                p.apellido,
                p.cedula,
                p.email,
                p.telefono,
                p.fecha_nacimiento,
                p.genero,
                p.direccion,
                u.login_usuario,
                u.rol,
                u.activo,
                COUNT(fc.id) as talleres_asignados
            FROM persona p
            JOIN usuario u ON p.cedula = u.cedula_usuario
            LEFT JOIN formacion_complementaria fc ON p.id = fc.id_profesor
            WHERE u.rol = 'Profesor'
            GROUP BY p.id, p.nombre, p.apellido, p.cedula, p.email, p.telefono,
                     p.fecha_nacimiento, p.genero, p.direccion, u.login_usuario, u.rol, u.activo
            ORDER BY p.apellido, p.nombre
            """
            
        elif tipo_reporte == "Estudiantes":
            query = """
            SELECT 
                p.id,
                p.nombre,
                p.apellido,
                p.cedula,
                p.email,
                p.telefono,
                p.fecha_nacimiento,
                p.genero,
                p.direccion,
                u.login_usuario,
                u.rol,
                u.activo,
                COUNT(i.id_formacion) as talleres_inscritos
            FROM persona p
            JOIN usuario u ON p.cedula = u.cedula_usuario
            LEFT JOIN inscripcion i ON u.id = i.id_estudiante
            WHERE u.rol = 'Estudiante'
            GROUP BY p.id, p.nombre, p.apellido, p.cedula, p.email, p.telefono,
                     p.fecha_nacimiento, p.genero, p.direccion, u.login_usuario, u.rol, u.activo
            ORDER BY p.apellido, p.nombre
            """
        
        # Ejecutar consulta
        resultado = db_instance.ejecutar_consulta(query)
        
        if resultado:
            st.session_state['reporte_datos'] = resultado
            st.success(f"Reporte '{tipo_reporte}' generado con {len(resultado)} registros")
        else:
            st.warning(f"No se encontraron datos para '{tipo_reporte}'")
            st.session_state['reporte_datos'] = []
            
    except Exception as e:
        st.error(f"Error al generar reporte: {str(e)}")
        st.session_state['reporte_datos'] = []

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
                return True
            else:
                db_connected = False
                db_error = db.db_error or "No se pudo establecer conexion con FOC26DB"
                return False
        else:
            db_connected = False
            db_error = "Database no disponible"
            return False
            
    except Exception as e:
        db_connected = False
        db_error = str(e)
        return False

# CSS basico eliminado - usar styles.py para mantener consistencia

# Pantalla de login institucional
def pantalla_login():
    """Pantalla de login con diseño institucional limpio"""
    try:
        # Logo central prominente (350px)
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <img src="./assets/Logo_IUJO.png" alt="IUJO" style="width: 350px; height: auto; display: block; margin: 0 auto;">
        </div>
        """, unsafe_allow_html=True)
        
        # Formulario de login limpio
        with st.form("login_form"):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                cedula_input = st.text_input("Cédula", placeholder="V12345678", key="login_cedula")
                password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña", key="login_password")
                
                submit_button = st.form_submit_button("Iniciar Sesión", type="primary", use_container_width=True)
            
            if submit_button:
                if cedula_input and password:
                    # Verificar credenciales
                    if db_connected and db is not None:
                        resultado = db.ejecutar_consulta(
                            "SELECT id, cedula_usuario, login_usuario, rol, activo FROM usuario WHERE cedula_usuario = %s AND contrasena = %s",
                            (cedula_input.strip(), hash_password(password.strip()))
                        )
                        
                        if resultado and len(resultado) > 0:
                            usuario = resultado[0]
                            if usuario['activo']:
                                # Guardar sesión
                                st.session_state['autenticado'] = True
                                st.session_state['user'] = dict(usuario)
                                st.success(f"Bienvenido: {usuario['login_usuario']}")
                                st.rerun()
                            else:
                                st.error("Usuario inactivo. Contacte al administrador.")
                        else:
                            st.error("Cédula o contraseña incorrectos.")
                    else:
                        st.error("No hay conexión a la base de datos.")
                else:
                    st.error("Complete todos los campos.")
    
    except Exception as e:
        st.error(f"Error en pantalla de login: {e}")

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
        
        # SIMPLIFICACIÓN: Si es Admin acceso total
        st.success(f"Bienvenido {user['login_usuario']} ({user['rol']})")
        
        # Panel de permisos y seguridad
        from seguridad import mostrar_panel_permisos
        mostrar_panel_permisos()
        
        # Información de versión
        with st.expander("Información del Sistema", expanded=False):
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

# Modulo de Estudiantes - LÓGICA COMPLETA RESTAURADA
def modulo_estudiantes():
    """Modulo completo para gestión de estudiantes con PostgreSQL"""
    try:
        st.header("Gestión de Estudiantes")

        # Crear tabs para estudiantes
        tab1, tab2, tab3 = st.tabs(["Estudiantes Registrados", "Registrar Nuevo Estudiante", "Consultar/Editar"])

        with tab1:
            st.subheader("Estudiantes Registrados")

            if db_connected and db is not None:
                # RESTAURACIÓN DE VISTAS GLOBALES: Sin filtros WHERE cedula para admin
                if str(st.session_state.get('user', {}).get('rol', '')).strip().upper() in ['ADMIN', 'ADMINISTRADOR']:
                    # VISTA GLOBAL: Admin ve TODOS los estudiantes sin filtros
                    query = """
                    SELECT
                        u.id as usuario_id,
                        u.login_usuario as email,
                        u.rol,
                        p.nombre,
                        p.apellido,
                        p.cedula,
                        p.telefono,
                        p.fecha_nacimiento,
                        p.genero as sexo,
                        p.direccion,
                        u.activo as activo,
                        u.login_usuario as fecha_registro,
                        e.carrera,
                        e.semestre_formacion,
                        e.estado_registro,
                        e.id as estudiante_id
                    FROM usuario u
                    JOIN persona p ON u.cedula_usuario = p.cedula
                    LEFT JOIN estudiante e ON u.id = e.id_usuario
                    WHERE u.rol = 'Estudiante'
                    ORDER BY p.apellido, p.nombre
                    """
                elif SeguridadFOC26.is_estudiante():
                    # Estudiante solo ve su propio registro
                    user_cedula = SeguridadFOC26.get_user_cedula()
                    query = f"""
                    SELECT
                        u.id as usuario_id,
                        u.login_usuario as email,
                        u.rol,
                        p.nombre,
                        p.apellido,
                        p.cedula,
                        p.telefono,
                        p.fecha_nacimiento,
                        p.genero as sexo,
                        p.direccion,
                        u.activo as activo,
                        u.login_usuario as fecha_registro,
                        e.carrera,
                        e.semestre_formacion,
                        e.estado_registro,
                        e.id as estudiante_id
                    FROM usuario u
                    JOIN persona p ON u.cedula_usuario = p.cedula
                    LEFT JOIN estudiante e ON u.id = e.id_usuario
                    WHERE u.rol = 'Estudiante' AND u.cedula_usuario = '{user_cedula}'
                    ORDER BY p.apellido, p.nombre
                    """
                else:
                    # Profesor ve todos los estudiantes
                    query = """
                    SELECT
                        u.id as usuario_id,
                        u.login_usuario as email,
                        u.rol,
                        p.nombre,
                        p.apellido,
                        p.cedula,
                        p.telefono,
                        p.fecha_nacimiento,
                        p.genero as sexo,
                        p.direccion,
                        u.activo as activo,
                        u.login_usuario as fecha_registro,
                        e.carrera,
                        e.semestre_formacion,
                        e.estado_registro,
                        e.id as estudiante_id
                    FROM usuario u
                    JOIN persona p ON u.cedula_usuario = p.cedula
                    LEFT JOIN estudiante e ON u.id = e.id_usuario
                    WHERE u.rol = 'Estudiante'
                    ORDER BY p.apellido, p.nombre
                    """

                resultado = db.ejecutar_consulta(query)

                if resultado is not None and len(resultado) > 0:
                    df_resultado = pd.DataFrame(resultado)

                    # EXCLUSIVIDAD BOTÓN ELIMINAR: Solo para rol admin con comparación robusta
                    user_rol = str(st.session_state.get('user', {}).get('rol', '')).strip().upper()
                    if user_rol in ['ADMIN', 'ADMINISTRADOR']:
                        # Admin ve tabla con acciones completas
                        st.dataframe(
                            df_resultado[["nombre", "apellido", "cedula", "telefono", "email", "carrera", "semestre_formacion", "estado_registro", "activo"]],
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "nombre": st.column_config.TextColumn("Nombres"),
                                "apellido": st.column_config.TextColumn("Apellidos"),
                                "cedula": st.column_config.TextColumn("Cédula"),
                                "telefono": st.column_config.TextColumn("Teléfono"),
                                "email": st.column_config.TextColumn("Correo"),
                                "carrera": st.column_config.TextColumn("Carrera"),
                                "semestre_formacion": st.column_config.TextColumn("Semestre"),
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
                                if st.button("✏️ Editar", type="primary", key="btn_editar_estudiante"):
                                    st.info(f"Editar estudiante: {estudiante_seleccionado}")
                            
                            with col2:
                                if st.button("🗑️ Eliminar", type="secondary", key="btn_eliminar_estudiante"):
                                    if st.confirm(f"¿Está seguro de eliminar al estudiante {estudiante_seleccionado}?"):
                                        # Lógica de eliminación
                                        st.success(f"Estudiante {estudiante_seleccionado} eliminado")
                                        st.rerun()
                            
                            with col3:
                                if st.button("📊 Ver Historial", key="btn_historial_estudiante"):
                                    st.info(f"Historial de: {estudiante_seleccionado}")
                            
                            with col4:
                                if st.button("🔄 Activar/Desactivar", key="btn_toggle_estudiante"):
                                    st.success(f"Estado cambiado para: {estudiante_seleccionado}")
                                    st.rerun()
                        
                        # Exportación de datos
                        st.markdown("---")
                        if st.button("📥 Exportar Estudiantes a CSV", type="primary", use_container_width=True):
                            csv = df_resultado.to_csv(index=False)
                            st.download_button(
                                label="Descargar Estudiantes.csv",
                                data=csv,
                                file_name="estudiantes_registrados.csv",
                                mime="text/csv"
                            )
                    else:
                        # Otros roles ven tabla sin botones de acción
                        st.dataframe(
                            df_resultado[["nombre", "apellido", "cedula", "telefono", "email", "carrera", "semestre_formacion", "estado_registro", "activo"]],
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "nombre": st.column_config.TextColumn("Nombres"),
                                "apellido": st.column_config.TextColumn("Apellidos"),
                                "cedula": st.column_config.TextColumn("Cédula"),
                                "telefono": st.column_config.TextColumn("Teléfono"),
                                "email": st.column_config.TextColumn("Correo"),
                                "carrera": st.column_config.TextColumn("Carrera"),
                                "semestre_formacion": st.column_config.TextColumn("Semestre"),
                                "estado_registro": st.column_config.TextColumn("Estado"),
                                "activo": st.column_config.TextColumn("Activo")
                            }
                        )

                    # Estadísticas con diseño IUJO
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
                    st.warning("No hay estudiantes registrados")
            else:
                st.error("No hay conexión a la base de datos")

        with tab2:
            st.subheader("Registrar Nuevo Estudiante")
            
            # Validar permisos - solo admin puede registrar nuevos estudiantes
            if not SeguridadFOC26.is_admin():
                st.error("Acceso denegado. Solo los administradores pueden registrar nuevos estudiantes.")
                st.stop()

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
                contraseña = st.text_input("Contraseña Temporal", type="password", placeholder="Estudiante123", help="Contraseña temporal para el estudiante")

                # Botones de acción
                col5, col6 = st.columns([3, 1])

                trans_manager = TransaccionFOC26(db.connection)

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
                                        INSERT INTO usuario (id_persona, cedula_usuario, login_usuario, email, contrasena, rol, activo)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                                        RETURNING id
                                        """
                                        usuario_result = db.ejecutar_consulta(usuario_query, (
                                            id_persona, cedula, email, email, contraseña or 'Estudiante123', 'Estudiante',
                                            estado_registro == 'Activo'
                                        ))

                                        if usuario_result is not None and len(usuario_result) > 0:
                                            id_usuario = usuario_result[0]['id']

                                            id_sexo = trans_manager.obtener_id_sexo(sexo)
                                            id_carrera = trans_manager.obtener_id_carrera(carrera)
                                            id_semestre = trans_manager.obtener_id_semestre(semestre)
                                            id_estado = trans_manager.obtener_id_estado_registro(estado_registro)

                                            estudiante_query = """
                                            INSERT INTO estudiante (
                                                cedula_estudiante,
                                                nombres,
                                                apellidos,
                                                id_sexo,
                                                telefono,
                                                correo,
                                                id_carrera,
                                                id_semestre_formacion,
                                                id_estado_registro,
                                                id_usuario,
                                                id_persona
                                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                            """
                                            estudiante_result = db.ejecutar_consulta(estudiante_query, (
                                                cedula,
                                                nombre,
                                                apellido,
                                                id_sexo,
                                                telefono,
                                                email,
                                                id_carrera,
                                                id_semestre,
                                                id_estado,
                                                id_usuario,
                                                id_persona
                                            ))

                                            if estudiante_result is not None:
                                                st.success(f"Estudiante {nombre} {apellido} registrado exitosamente!")
                                                st.info(f"Usuario: {email} | Contraseña temporal: {contraseña or 'Estudiante123'}")
                                                st.rerun()
                                            else:
                                                st.error("Error al registrar los datos de estudiante")
                                        else:
                                            st.error("Error al registrar el usuario del estudiante")
                                    else:
                                        st.error("Error al registrar los datos personales del estudiante")
                        except Exception as e:
                            st.error(f"Error al registrar estudiante: {e}")
                    else:
                        st.error("Por favor, complete todos los campos obligatorios (*)")

        with tab3:
            st.subheader("Consultar/Editar Estudiante")
            
            # Búsqueda de estudiante
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                termino_busqueda = st.text_input("Buscar por Cédula, Nombre o Email", placeholder="V-12345678 o Juan Pérez")
            with col2:
                if st.button("🔍 Buscar", type="primary"):
                    if termino_busqueda:
                        # Lógica de búsqueda
                        query = """
                        SELECT
                            u.id as usuario_id,
                            u.login_usuario as email,
                            u.rol,
                            p.nombre,
                            p.apellido,
                            p.cedula,
                            p.telefono,
                            p.fecha_nacimiento,
                            p.genero as sexo,
                            p.direccion,
                            u.activo as activo,
                            u.login_usuario as fecha_registro,
                            e.carrera,
                            e.semestre_formacion,
                            e.estado_registro,
                            e.id as estudiante_id
                        FROM usuario u
                        JOIN persona p ON u.cedula_usuario = p.cedula
                        LEFT JOIN estudiante e ON u.id = e.id_usuario
                        WHERE u.rol = 'Estudiante' AND (
                            p.cedula ILIKE %s OR 
                            p.nombre ILIKE %s OR 
                            p.apellido ILIKE %s OR 
                            u.login_usuario ILIKE %s
                        )
                        ORDER BY p.apellido, p.nombre
                        """
                        
                        resultado = db.ejecutar_consulta(query, (f"%{termino_busqueda}%", f"%{termino_busqueda}%", f"%{termino_busqueda}%", f"%{termino_busqueda}%"))
                        
                        if resultado:
                            st.session_state['resultados_busqueda_estudiante'] = resultado
                        else:
                            st.warning("No se encontraron estudiantes con esos criterios.")
            
            with col3:
                if st.button("🔄 Limpiar Búsqueda", key="limpiar_busqueda_estudiante"):
                    if 'resultados_busqueda_estudiante' in st.session_state:
                        del st.session_state['resultados_busqueda_estudiante']
                    st.rerun()
            
            # Mostrar resultados de búsqueda
            if 'resultados_busqueda_estudiante' in st.session_state:
                st.markdown("---")
                st.subheader("Resultados de Búsqueda")
                
                df_busqueda = pd.DataFrame(st.session_state['resultados_busqueda_estudiante'])
                st.dataframe(
                    df_busqueda[["nombre", "apellido", "cedula", "telefono", "email", "carrera", "semestre_formacion", "estado_registro", "activo"]],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "nombre": st.column_config.TextColumn("Nombres"),
                        "apellido": st.column_config.TextColumn("Apellidos"),
                        "cedula": st.column_config.TextColumn("Cédula"),
                        "telefono": st.column_config.TextColumn("Teléfono"),
                        "email": st.column_config.TextColumn("Correo"),
                        "carrera": st.column_config.TextColumn("Carrera"),
                        "semestre_formacion": st.column_config.TextColumn("Semestre"),
                        "estado_registro": st.column_config.TextColumn("Estado"),
                        "activo": st.column_config.TextColumn("Activo")
                    }
                )

    except Exception as e:
        st.error(f"Error en módulo de estudiantes: {e}")
        if db_connected:
            print(f"Error detallado en módulo estudiantes: {e}")

# Modulo de Profesores
def modulo_profesores():
    """Módulo para gestión de profesores"""
    try:
        st.header("Módulo de Profesores")
        trans_manager = TransaccionFOC26(db.connection)

        if not db_connected or db is None:
            st.error("No hay conexión a la base de datos")
            return

        tab1, tab2 = st.tabs(["Listado de Profesores", "Registro de Nuevo Profesor"])

        with tab1:
            st.subheader("Nómina de Profesores Registrados")
            
            # Consultar profesores con filtros de seguridad - Admin ve todos
            if SeguridadFOC26.is_admin():
                # Admin ve todos los profesores con filtro explícito por rol
                query = """
                    SELECT pr.id_profesor, pr.cedula_profesor, p.nombre, p.apellido, p.email as email_institucional,
                           pr.correo_personal, pr.especialidad, pr.departamento, pr.estado, u.id as id_usuario, pr.id_persona
                    FROM profesor pr
                    JOIN persona p ON pr.id_persona = p.id
                    JOIN usuario u ON pr.id_usuario = u.id
                    WHERE u.rol = 'Profesor'
                    ORDER BY p.apellido, p.nombre
                """
            elif SeguridadFOC26.is_profesor():
                # Profesor solo ve su propio registro
                user_cedula = SeguridadFOC26.get_user_cedula()
                query = f"""
                    SELECT pr.id_profesor, pr.cedula_profesor, p.nombre, p.apellido, p.email as email_institucional,
                           pr.correo_personal, pr.especialidad, pr.departamento, pr.estado, u.id as id_usuario, pr.id_persona
                    FROM profesor pr
                    JOIN persona p ON pr.id_persona = p.id
                    JOIN usuario u ON pr.id_usuario = u.id
                    WHERE u.rol = 'Profesor' AND pr.cedula_profesor = '{user_cedula}'
                    ORDER BY p.apellido, p.nombre
                """
            else:
                # Estudiante no puede ver profesores (o ve lista básica)
                query = """
                    SELECT pr.id_profesor, pr.cedula_profesor, p.nombre, p.apellido, p.email as email_institucional,
                           pr.correo_personal, pr.especialidad, pr.departamento, pr.estado, u.id as id_usuario, pr.id_persona
                    FROM profesor pr
                    JOIN persona p ON pr.id_persona = p.id
                    JOIN usuario u ON pr.id_usuario = u.id
                    WHERE u.rol = 'Profesor' AND pr.estado = 'Activo'
                    ORDER BY p.apellido, p.nombre
                """
            profesores = db.ejecutar_consulta(query)

            if profesores is None or len(profesores) == 0:
                st.info("No hay profesores registrados")
            else:
                df_profesores = pd.DataFrame(profesores)

                df_display = df_profesores[[
                    'cedula_profesor', 'nombre', 'apellido', 'especialidad', 'estado'
                ]].rename(columns={
                    'cedula_profesor': 'Cédula',
                    'nombre': 'Nombre',
                    'apellido': 'Apellido',
                    'especialidad': 'Especialidad',
                    'estado': 'Estado'
                })

                st.dataframe(
                    df_display,
                    use_container_width=True,
                    height=420,
                    hide_index=True
                )

                selected_option = st.selectbox(
                    "Seleccionar profesor",
                    [f"{row['cedula_profesor']} - {row['apellido']}, {row['nombre']}" for _, row in df_profesores.iterrows()]
                )
                selected_cedula = selected_option.split(' - ')[0]
                profesor_seleccionado = df_profesores[df_profesores['cedula_profesor'] == selected_cedula].iloc[0]
                # Definir acciones según rol
                acciones_disponibles = ["Consultar", "Editar"]
                if SeguridadFOC26.is_admin():
                    acciones_disponibles.append("Eliminar")
                
                accion = st.radio("Acción", acciones_disponibles)

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
                elif accion == "Eliminar":
                    # Validar permisos de eliminación
                    if not SeguridadFOC26.is_admin():
                        st.error("Acceso denegado. Solo los administradores pueden eliminar profesores.")
                        st.stop()
                    
                    # Confirmación de eliminación
                    if st.button(f"Eliminar Profesor {profesor_seleccionado['nombre']} {profesor_seleccionado['apellido']}", type="secondary"):
                        try:
                            # Lógica de eliminación aquí
                            st.success(f"Profesor eliminado exitosamente")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al eliminar profesor: {e}")
                elif accion == "Editar":
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
                                'estado': estado,
                                'rol': 'Profesor'
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
                    
                    if len(contrasena) < 8:
                        st.error("La contraseña debe tener al menos 8 caracteres.")
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
                            cedula_existe = db.ejecutar_consulta("SELECT id FROM usuario WHERE cedula_usuario = %s", (cedula_str,))
                            if cedula_existe is not None and len(cedula_existe) > 0:
                                st.error("Ya existe un usuario con esta cédula.")
                                return
                            
                            # Verificar si el email ya existe
                            email_existe = db.ejecutar_consulta("SELECT id FROM usuario WHERE login_usuario = %s", (email,))
                            if email_existe is not None and len(email_existe) > 0:
                                st.error("Ya existe un usuario con este correo electrónico.")
                                return
                            
                            # Insertar directamente en tabla usuario
                            usuario_query = """
                            INSERT INTO usuario (cedula_usuario, login_usuario, contrasena, rol, activo)
                            VALUES (%s, %s, %s, %s, %s)
                            """
                            usuario_result = db.ejecutar_consulta(
                                usuario_query,
                                (cedula_str, email, hash_password(contrasena), 'Estudiante', True)
                            )
                            
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
        
        # Aplicar estilos globales centralizados
        st.markdown(get_global_styles(hide_sidebar=not st.session_state.get('autenticado', False)), unsafe_allow_html=True)
        
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
            
            # Sidebar dinamico con navegacion institucional
            with st.sidebar:
                # Logo_IUJO.png en cuadro verde superior izquierdo
                st.markdown("""
                <div style="background: rgba(0, 150, 0, 0.1); border: 2px solid rgba(0, 150, 0, 0.3); border-radius: 10px; padding: 1rem; margin-bottom: 1rem;">
                    <img src="./assets/Logo_IUJO.png" alt="IUJO" style="width: 100%; height: auto; display: block; margin: 0 auto;">
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### Navegación")
                
                # Informacion del usuario
                user = st.session_state['user']
                
                # REFRESCO DE SESIÓN: Normalizar rol en sidebar también
                if 'rol' in user and user['rol']:
                    user['rol'] = user['rol'].strip().capitalize()
                    st.session_state['user'] = user  # Actualizar sesión inmediatamente
                
                st.success(f"**{user['email']}**")
                st.info(f"Rol: {user['rol']}")
                st.markdown("---")
                
                # Menu de navegacion exclusivo según rol de usuario
                opciones_menu = ['Inicio']
                
                # NAVEGACIÓN EXCLUSIVA: Profesores, Estudiantes, Formación, Reportes, Configuración
                if str(st.session_state.get('user', {}).get('rol', '')).strip().upper() in ['ADMIN', 'ADMINISTRADOR']:
                    opciones_menu.extend(['Profesores', 'Estudiantes', 'Formación Complementaria', 'Reportes', 'Configuración'])
                elif SeguridadFOC26.is_profesor():
                    opciones_menu.extend(['Profesores', 'Formación Complementaria'])
                elif SeguridadFOC26.is_estudiante():
                    opciones_menu.extend(['Formación Complementaria'])
                
                pagina = st.radio(
                    "Seleccionar Módulo:",
                    opciones_menu,
                    key='pagina'
                )
                
                st.markdown("---")
                
                # Boton de cerrar sesion
                if st.button("Cerrar Sesion", type="secondary"):
                    st.session_state['autenticado'] = False
                    st.session_state['user'] = None
                    st.rerun()
            
            # Mostrar el modulo correspondiente - navegación exclusiva
            try:
                if st.session_state['pagina'] == 'Inicio':
                    dashboard_basico()
                elif st.session_state['pagina'] == 'Profesores':
                    modulo_profesores()
                elif st.session_state['pagina'] == 'Estudiantes':
                    modulo_estudiantes()
                elif st.session_state['pagina'] == 'Formación Complementaria':
                    # Ejecutar módulo de formación complementaria local
                    modulo_formacion_complementaria()
                elif st.session_state['pagina'] == 'Reportes':
                    # Módulo completo de Reportes con PostgreSQL
                    st.header("Reportes del Sistema")
                    
                    # Crear tabs para reportes
                    tab1, tab2, tab3 = st.tabs(["Data a Demanda", "Reportes Predefinidos", "Estadísticas"])
                    
                    with tab1:
                        st.subheader("Data a Demanda")
                        
                        # Selectbox dinámico para consultas personalizadas
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            tipo_consulta = st.selectbox(
                                "Seleccionar Tipo de Consulta:",
                                [
                                    "Todos los Profesores",
                                    "Todos los Estudiantes", 
                                    "Todos los Talleres",
                                    "Inscripciones por Taller",
                                    "Estudiantes por Carrera",
                                    "Profesores por Departamento",
                                    "Talleres por Profesor",
                                    "Certificados Emitidos",
                                    "Usuarios Activos vs Inactivos"
                                ],
                                key="tipo_consulta"
                            )
                        
                        with col2:
                            if st.button("🔊 Ejecutar Consulta", type="primary"):
                                ejecutar_consulta_dinamica(tipo_consulta)
                        
                        # Mostrar resultados de la consulta
                        if 'consulta_resultados' in st.session_state and st.session_state['consulta_resultados']:
                            st.markdown("---")
                            st.subheader(f"Resultados: {tipo_consulta}")
                            
                            df_resultados = pd.DataFrame(st.session_state['consulta_resultados'])
                            st.dataframe(
                                df_resultados,
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            # Botones de exportación
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                csv = df_resultados.to_csv(index=False)
                                st.download_button(
                                    label="📥 Descargar CSV",
                                    data=csv,
                                    file_name=f"consulta_{tipo_consulta.lower().replace(' ', '_')}.csv",
                                    mime="text/csv"
                                )
                            
                            with col2:
                                json_data = df_resultados.to_json(orient='records')
                                st.download_button(
                                    label="📄 Descargar JSON",
                                    data=json_data,
                                    file_name=f"consulta_{tipo_consulta.lower().replace(' ', '_')}.json",
                                    mime="application/json"
                                )
                            
                            with col3:
                                excel_data = df_resultados.to_excel(index=False)
                                st.download_button(
                                    label="📊 Descargar Excel",
                                    data=excel_data,
                                    file_name=f"consulta_{tipo_consulta.lower().replace(' ', '_')}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                    
                    with tab2:
                        st.subheader("Reportes Predefinidos")
                        
                        # Reportes predefinidos con filtros
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            reporte_seleccionado = st.selectbox(
                                "Seleccionar Reporte:",
                                [
                                    "Reporte de Profesores Activos",
                                    "Reporte de Estudiantes por Semestre",
                                    "Reporte de Talleres Disponibles",
                                    "Reporte de Inscripciones del Mes",
                                    "Reporte de Certificados Emitidos",
                                    "Reporte de Usuarios por Rol"
                                ],
                                key="reporte_predefinido"
                            )
                        
                        with col2:
                            # Filtros adicionales según el reporte
                            if "Mes" in reporte_seleccionado:
                                mes_seleccionado = st.selectbox(
                                    "Mes:",
                                    ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                                     "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
                                    key="mes_filtro"
                                )
                            elif "Semestre" in reporte_seleccionado:
                                semestre_filtro = st.number_input(
                                    "Semestre:", min_value=1, max_value=12, value=1, key="semestre_filtro"
                                )
                        
                        if st.button("📊 Generar Reporte", type="primary"):
                            generar_reporte_predefinido(reporte_seleccionado)
                        
                        # Mostrar resultados del reporte predefinido
                        if 'reporte_predefinido_datos' in st.session_state and st.session_state['reporte_predefinido_datos']:
                            st.markdown("---")
                            st.subheader(f"Reporte: {reporte_seleccionado}")
                            
                            df_reporte = pd.DataFrame(st.session_state['reporte_predefinido_datos'])
                            st.dataframe(
                                df_reporte,
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            # Estadísticas del reporte
                            st.markdown("---")
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Total Registros", len(df_reporte))
                            with col2:
                                if 'activo' in df_reporte.columns:
                                    activos = df_reporte[df_reporte['activo'] == True]
                                    st.metric("Registros Activos", len(activos))
                            with col3:
                                if 'estado' in df_reporte.columns:
                                    estados_unicos = df_reporte['estado'].nunique()
                                    st.metric("Estados Únicos", estados_unicos)
                            with col4:
                                if 'fecha' in df_reporte.columns or 'fecha_' in df_reporte.columns.str.lower():
                                    st.metric("Con Datos de Fecha", "Sí")
                                else:
                                    st.metric("Con Datos de Fecha", "No")
                    
                    with tab3:
                        st.subheader("Estadísticas Generales")

                        if db_connected and db is not None:
                            # Estadísticas generales del sistema
                            col1, col2, col3, col4 = st.columns(4)

                            with col1:
                                # Total de usuarios
                                total_usuarios = db.ejecutar_consulta("SELECT COUNT(*) as total FROM usuario")
                                if total_usuarios:
                                    st.metric("Total Usuarios", total_usuarios[0]['total'], delta="Registrados")

                            with col2:
                                # Total de profesores
                                total_profesores = db.ejecutar_consulta("SELECT COUNT(*) as total FROM usuario WHERE rol = 'Profesor'")
                                if total_profesores:
                                    st.metric("Total Profesores", total_profesores[0]['total'])

                            with col3:
                                # Total de estudiantes
                                total_estudiantes = db.ejecutar_consulta("SELECT COUNT(*) as total FROM usuario WHERE rol = 'Estudiante'")
                                if total_estudiantes:
                                    st.metric("Total Estudiantes", total_estudiantes[0]['total'])

                            with col4:
                                # Total de talleres
                                total_talleres = db.ejecutar_consulta("SELECT COUNT(*) as total FROM formacion_complementaria")
                                if total_talleres:
                                    st.metric("Total Talleres", total_talleres[0]['total'])

                            # Gráficos y análisis
                            st.markdown("---")
                            col1, col2 = st.columns(2)

                            with col1:
                                st.subheader("Distribución por Rol")
                                query_rol = """
                                SELECT rol, COUNT(*) as cantidad
                                FROM usuario
                                GROUP BY rol
                                ORDER BY cantidad DESC
                                """
                                resultado_rol = db.ejecutar_consulta(query_rol)
                                
                                if resultado_rol:
                                    df_rol = pd.DataFrame(resultado_rol)
                                    st.bar_chart(df_rol.set_index('rol'))

                            with col2:
                                st.subheader("Talleres por Estado")
                                query_talleres = """
                                SELECT estado, COUNT(*) as cantidad
                                FROM formacion_complementaria
                                GROUP BY estado
                                ORDER BY cantidad DESC
                                """
                                resultado_talleres = db.ejecutar_consulta(query_talleres)
                                
                                if resultado_talleres:
                                    df_talleres = pd.DataFrame(resultado_talleres)
                                    st.bar_chart(df_talleres.set_index('estado'))

                            # Estadísticas adicionales
                            st.markdown("---")
                            st.subheader("Análisis Detallado")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                # Inscripciones por mes
                                query_inscripciones = """
                                SELECT 
                                    EXTRACT(MONTH FROM fecha_inscripcion) as mes,
                                    COUNT(*) as total_inscripciones
                                FROM inscripcion
                                WHERE fecha_inscripcion >= CURRENT_DATE - INTERVAL '12 months'
                                GROUP BY mes
                                ORDER BY mes
                                """
                                resultado_inscripciones = db.ejecutar_consulta(query_inscripciones)
                                
                                if resultado_inscripciones:
                                    st.write("**Inscripciones por Mes (Últimos 12 meses)**")
                                    df_inscripciones = pd.DataFrame(resultado_inscripciones)
                                    st.line_chart(df_inscripciones.set_index('mes'))

                            with col2:
                                # Carreras más populares
                                query_carreras = """
                                SELECT 
                                    e.carrera,
                                    COUNT(*) as total_estudiantes
                                FROM estudiante e
                                JOIN usuario u ON e.id_usuario = u.id
                                WHERE u.rol = 'Estudiante'
                                GROUP BY e.carrera
                                ORDER BY total_estudiantes DESC
                                LIMIT 10
                                """
                                resultado_carreras = db.ejecutar_consulta(query_carreras)
                                
                                if resultado_carreras:
                                    st.write("**Top 10 Carreras más Populares**")
                                    df_carreras = pd.DataFrame(resultado_carreras)
                                    st.dataframe(df_carreras, use_container_width=True, hide_index=True)

                            with col3:
                                # Profesores con más talleres
                                query_prof_talleres = """
                                SELECT 
                                    p.nombre || ' ' || p.apellido as profesor,
                                    COUNT(fc.id) as total_talleres
                                FROM formacion_complementaria fc
                                JOIN persona p ON fc.id_profesor = p.id
                                GROUP BY p.id, p.nombre, p.apellido
                                ORDER BY total_talleres DESC
                                LIMIT 10
                                """
                                resultado_prof_talleres = db.ejecutar_consulta(query_prof_talleres)
                                
                                if resultado_prof_talleres:
                                    st.write("**Top 10 Profesores con más Talleres**")
                                    df_prof_talleres = pd.DataFrame(resultado_prof_talleres)
                                    st.dataframe(df_prof_talleres, use_container_width=True, hide_index=True)
                        else:
                            st.error("Acceso denegado. Solo los administradores pueden ver reportes.")
                            st.stop()
                elif st.session_state['pagina'] == 'Configuración':
                    if SeguridadFOC26.is_admin():
                        st.error("Módulo de configuración en desarrollo")
                    else:
                        st.error("Acceso denegado. Solo administradores pueden acceder a Configuración.")
                        st.stop()
            except Exception as e:
                st.error(f"Error critico en la aplicacion: {e}")
                st.markdown("### La aplicacion ha encontrado un error inesperado")
                st.markdown("Por favor, recarga la pagina.")

def ejecutar_consulta_dinamica(tipo_consulta):
    """Ejecuta consultas dinámicas según el tipo seleccionado"""
    try:
        if db_connected and db is not None:
            if tipo_consulta == "Todos los Profesores":
                query = """
                SELECT 
                    p.nombre,
                    p.apellido,
                    p.cedula,
                    p.email,
                    pr.especialidad,
                    pr.departamento,
                    pr.estado,
                    u.activo
                FROM persona p
                JOIN usuario u ON p.cedula = u.cedula_usuario
                LEFT JOIN profesor pr ON p.id = pr.id_persona
                WHERE u.rol = 'Profesor'
                ORDER BY p.apellido, p.nombre
                """
            
            elif tipo_consulta == "Todos los Estudiantes":
                query = """
                SELECT 
                    p.nombre,
                    p.apellido,
                    p.cedula,
                    p.email,
                    e.carrera,
                    e.semestre_formacion,
                    e.estado_registro,
                    u.activo
                FROM persona p
                JOIN usuario u ON p.cedula = u.cedula_usuario
                LEFT JOIN estudiante e ON u.id = e.id_usuario
                WHERE u.rol = 'Estudiante'
                ORDER BY p.apellido, p.nombre
                """
            
            elif tipo_consulta == "Todos los Talleres":
                query = """
                SELECT 
                    fc.nombre_taller,
                    fc.descripcion,
                    fc.fecha_inicio,
                    fc.fecha_fin,
                    fc.cupo_maximo,
                    fc.estado,
                    p.nombre as profesor_nombre,
                    p.apellido as profesor_apellido,
                    COUNT(i.id) as inscritos
                FROM formacion_complementaria fc
                JOIN persona p ON fc.id_profesor = p.id
                LEFT JOIN inscripcion i ON fc.id = i.id_formacion
                GROUP BY fc.id, fc.nombre_taller, fc.descripcion, fc.fecha_inicio, fc.fecha_fin,
                         fc.cupo_maximo, fc.estado, p.nombre, p.apellido
                ORDER BY fc.fecha_inicio DESC
                """
            
            elif tipo_consulta == "Inscripciones por Taller":
                query = """
                SELECT 
                    fc.nombre_taller,
                    p.nombre as estudiante_nombre,
                    p.apellido as estudiante_apellido,
                    i.fecha_inscripcion,
                    i.estado_inscripcion,
                    p.cedula as estudiante_cedula
                FROM inscripcion i
                JOIN formacion_complementaria fc ON i.id_formacion = fc.id
                JOIN usuario u ON i.id_estudiante = u.id
                JOIN persona p ON u.cedula_usuario = p.cedula
                ORDER BY fc.nombre_taller, i.fecha_inscripcion DESC
                """
            
            elif tipo_consulta == "Estudiantes por Carrera":
                query = """
                SELECT 
                    e.carrera,
                    COUNT(*) as total_estudiantes,
                    COUNT(CASE WHEN u.activo = true THEN 1 END) as activos,
                    COUNT(CASE WHEN u.activo = false THEN 1 END) as inactivos
                FROM estudiante e
                JOIN usuario u ON e.id_usuario = u.id
                WHERE u.rol = 'Estudiante'
                GROUP BY e.carrera
                ORDER BY total_estudiantes DESC
                """
            
            elif tipo_consulta == "Profesores por Departamento":
                query = """
                SELECT 
                    pr.departamento,
                    COUNT(*) as total_profesores,
                    COUNT(CASE WHEN u.activo = true THEN 1 END) as activos,
                    COUNT(CASE WHEN u.activo = false THEN 1 END) as inactivos
                FROM profesor pr
                JOIN persona p ON pr.id_persona = p.id
                JOIN usuario u ON p.cedula = u.cedula_usuario
                WHERE u.rol = 'Profesor'
                GROUP BY pr.departamento
                ORDER BY total_profesores DESC
                """
            
            elif tipo_consulta == "Talleres por Profesor":
                query = """
                SELECT 
                    p.nombre || ' ' || p.apellido as profesor,
                    COUNT(fc.id) as total_talleres,
                    COUNT(CASE WHEN fc.estado = 'Activo' THEN 1 END) as talleres_activos,
                    COUNT(i.id) as total_inscripciones
                FROM formacion_complementaria fc
                JOIN persona p ON fc.id_profesor = p.id
                LEFT JOIN inscripcion i ON fc.id = i.id_formacion
                GROUP BY p.id, p.nombre, p.apellido
                ORDER BY total_talleres DESC
                """
            
            elif tipo_consulta == "Certificados Emitidos":
                query = """
                SELECT 
                    p.nombre as estudiante_nombre,
                    p.apellido as estudiante_apellido,
                    fc.nombre_taller,
                    i.fecha_completacion,
                    i.codigo_certificado,
                    pf.nombre as profesor_nombre,
                    pf.apellido as profesor_apellido
                FROM inscripcion i
                JOIN formacion_complementaria fc ON i.id_formacion = fc.id
                JOIN usuario u ON i.id_estudiante = u.id
                JOIN persona p ON u.cedula_usuario = p.cedula
                JOIN persona pf ON fc.id_profesor = pf.id
                WHERE i.estado_inscripcion = 'Completada' AND i.codigo_certificado IS NOT NULL
                ORDER BY i.fecha_completacion DESC
                """
            
            elif tipo_consulta == "Usuarios Activos vs Inactivos":
                query = """
                SELECT 
                    rol,
                    COUNT(*) as total_usuarios,
                    COUNT(CASE WHEN activo = true THEN 1 END) as usuarios_activos,
                    COUNT(CASE WHEN activo = false THEN 1 END) as usuarios_inactivos,
                    ROUND(COUNT(CASE WHEN activo = true THEN 1 END) * 100.0 / COUNT(*), 2) as porcentaje_activos
                FROM usuario
                GROUP BY rol
                ORDER BY total_usuarios DESC
                """
            
            else:
                st.error("Tipo de consulta no reconocido")
                return
            
            resultado = db.ejecutar_consulta(query)
            
            if resultado:
                st.session_state['consulta_resultados'] = resultado
                st.success(f"Consulta ejecutada: {len(resultado)} registros encontrados")
            else:
                st.warning("No se encontraron resultados para esta consulta")
                st.session_state['consulta_resultados'] = []
    
    except Exception as e:
        st.error(f"Error al ejecutar consulta: {e}")
        st.session_state['consulta_resultados'] = []

def generar_reporte_predefinido(reporte_seleccionado):
    """Genera reportes predefinidos con filtros específicos"""
    try:
        if db_connected and db is not None:
            if reporte_seleccionado == "Reporte de Profesores Activos":
                query = """
                SELECT 
                    p.nombre,
                    p.apellido,
                    p.cedula,
                    p.email,
                    p.telefono,
                    pr.especialidad,
                    pr.departamento,
                    pr.correo_personal,
                    u.login_usuario,
                    u.fecha_registro
                FROM persona p
                JOIN usuario u ON p.cedula = u.cedula_usuario
                LEFT JOIN profesor pr ON p.id = pr.id_persona
                WHERE u.rol = 'Profesor' AND u.activo = true
                ORDER BY p.apellido, p.nombre
                """
            
            elif reporte_seleccionado == "Reporte de Estudiantes por Semestre":
                semestre = st.session_state.get('semestre_filtro', 1)
                query = f"""
                SELECT 
                    p.nombre,
                    p.apellido,
                    p.cedula,
                    p.email,
                    e.carrera,
                    e.semestre_formacion,
                    e.estado_registro,
                    u.fecha_registro,
                    COUNT(i.id_formacion) as talleres_inscritos
                FROM persona p
                JOIN usuario u ON p.cedula = u.cedula_usuario
                LEFT JOIN estudiante e ON u.id = e.id_usuario
                LEFT JOIN inscripcion i ON u.id = i.id_estudiante
                WHERE u.rol = 'Estudiante' AND e.semestre_formacion = {semestre}
                GROUP BY p.id, p.nombre, p.apellido, p.cedula, p.email, e.carrera, 
                         e.semestre_formacion, e.estado_registro, u.fecha_registro
                ORDER BY p.apellido, p.nombre
                """
            
            elif reporte_seleccionado == "Reporte de Talleres Disponibles":
                query = """
                SELECT 
                    fc.nombre_taller,
                    fc.descripcion,
                    fc.fecha_inicio,
                    fc.fecha_fin,
                    fc.cupo_maximo,
                    COUNT(i.id) as inscritos,
                    fc.cupo_maximo - COUNT(i.id) as cupo_disponible,
                    p.nombre as profesor_nombre,
                    p.apellido as profesor_apellido,
                    fc.estado
                FROM formacion_complementaria fc
                JOIN persona p ON fc.id_profesor = p.id
                LEFT JOIN inscripcion i ON fc.id = i.id_formacion
                WHERE fc.estado = 'Activo' AND fc.fecha_fin >= CURRENT_DATE
                GROUP BY fc.id, fc.nombre_taller, fc.descripcion, fc.fecha_inicio, fc.fecha_fin,
                         fc.cupo_maximo, p.nombre, p.apellido, fc.estado
                ORDER BY fc.fecha_inicio ASC
                """
            
            elif reporte_seleccionado == "Reporte de Inscripciones del Mes":
                mes = st.session_state.get('mes_filtro', 'Enero')
                mes_numero = {
                    'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5, 'Junio': 6,
                    'Julio': 7, 'Agosto': 8, 'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12
                }[mes]
                
                query = f"""
                SELECT 
                    fc.nombre_taller,
                    p.nombre as estudiante_nombre,
                    p.apellido as estudiante_apellido,
                    p.cedula as estudiante_cedula,
                    i.fecha_inscripcion,
                    i.estado_inscripcion,
                    pf.nombre as profesor_nombre,
                    pf.apellido as profesor_apellido
                FROM inscripcion i
                JOIN formacion_complementaria fc ON i.id_formacion = fc.id
                JOIN usuario u ON i.id_estudiante = u.id
                JOIN persona p ON u.cedula_usuario = p.cedula
                JOIN persona pf ON fc.id_profesor = pf.id
                WHERE EXTRACT(MONTH FROM i.fecha_inscripcion) = {mes_numero}
                ORDER BY i.fecha_inscripcion DESC
                """
            
            elif reporte_seleccionado == "Reporte de Certificados Emitidos":
                query = """
                SELECT 
                    p.nombre as estudiante_nombre,
                    p.apellido as estudiante_apellido,
                    p.cedula as estudiante_cedula,
                    fc.nombre_taller,
                    i.fecha_completacion,
                    i.codigo_certificado,
                    pf.nombre as profesor_nombre,
                    pf.apellido as profesor_apellido,
                    EXTRACT(YEAR FROM i.fecha_completacion) as anio
                FROM inscripcion i
                JOIN formacion_complementaria fc ON i.id_formacion = fc.id
                JOIN usuario u ON i.id_estudiante = u.id
                JOIN persona p ON u.cedula_usuario = p.cedula
                JOIN persona pf ON fc.id_profesor = pf.id
                WHERE i.estado_inscripcion = 'Completada' AND i.codigo_certificado IS NOT NULL
                ORDER BY i.fecha_completacion DESC
                """
            
            elif reporte_seleccionado == "Reporte de Usuarios por Rol":
                query = """
                SELECT 
                    rol,
                    COUNT(*) as total_usuarios,
                    COUNT(CASE WHEN activo = true THEN 1 END) as usuarios_activos,
                    COUNT(CASE WHEN activo = false THEN 1 END) as usuarios_inactivos,
                    MIN(fecha_registro) as fecha_primer_registro,
                    MAX(fecha_registro) as fecha_ultimo_registro
                FROM usuario
                GROUP BY rol
                ORDER BY total_usuarios DESC
                """
            
            else:
                st.error("Reporte no reconocido")
                return
            
            resultado = db.ejecutar_consulta(query)
            
            if resultado:
                st.session_state['reporte_predefinido_datos'] = resultado
                st.success(f"Reporte generado: {len(resultado)} registros")
            else:
                st.warning("No se encontraron datos para este reporte")
                st.session_state['reporte_predefinido_datos'] = []
    
    except Exception as e:
        st.error(f"Error al generar reporte: {e}")
        st.session_state['reporte_predefinido_datos'] = []

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
