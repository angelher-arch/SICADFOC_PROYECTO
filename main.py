# -*- coding: utf-8 -*-
"""
main.py - Sistema de Informacion de Control Academico de Formacion Complementaria
Instituto Universitario Jesus Obrero
Version 2.0 - Entorno de Desarrollo Limpio
"""

import streamlit as st  # type: ignore

# PRIMER COMANDO STREAMLIT - Configuración de página
st.set_page_config(
    page_title="SICADFOC 2026 - IUJO",
    page_icon="IUJO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import os
import hashlib
import sys
import random
import re

# Aplicar CSS global con imagen de fondo
# from css_global import get_global_css
# st.markdown(get_global_css(), unsafe_allow_html=True)

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

# Importar solo lo esencial para carga rápida
def hash_password(password):
    """Hash de contraseña simple"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

# LAZY LOADING - Cargar módulos pesados solo cuando se necesiten
_imports_cache = {}

def lazy_import(module_name, from_module=None):
    """Importación bajo demanda con caché"""
    cache_key = f"{from_module}.{module_name}" if from_module else module_name
    
    if cache_key not in _imports_cache:
        try:
            if from_module:
                module = __import__(from_module, fromlist=[module_name])
                _imports_cache[cache_key] = getattr(module, module_name)
            else:
                _imports_cache[cache_key] = __import__(module_name)
        except ImportError as e:
            st.error(f"Error importando {cache_key}: {e}")
            return None
    
    return _imports_cache[cache_key]

# Funciones wrapper con lazy loading
def get_carreras():
    configuracion = lazy_import('get_carreras', 'configuracion')
    return configuracion() if configuracion else []

def get_semestres():
    configuracion = lazy_import('get_semestres', 'configuracion')
    return configuracion() if configuracion else []

def get_estados_registro():
    configuracion = lazy_import('get_estados_registro', 'configuracion')
    return configuracion() if configuracion else []

def get_generos():
    configuracion = lazy_import('get_generos', 'configuracion')
    return configuracion() if configuracion else []

def get_version_info():
    version = lazy_import('get_version_info', 'version')
    return version() if version else {}

def display_version_info():
    version = lazy_import('display_version_info', 'version')
    return version() if version else None

def get_short_version():
    version = lazy_import('get_short_version', 'version')
    return version() if version else "1.0.0"

def modulo_formacion_complementaria(db=None):
    fc_module = lazy_import('modulo_formacion_complementaria', 'formacion_complementaria')
    return fc_module() if fc_module else None

def gestor_certificaciones_unificado():
    """Función wrapper para el gestor de certificaciones unificado"""
    try:
        from gestor_certificaciones import gestor_certificaciones_unificado as gc_func
        return gc_func()
    except ImportError:
        st.error("Módulo de certificaciones no disponible")
        return None

def get_pandas():
    """Lazy loading para pandas"""
    return lazy_import('pandas')

def get_TransaccionFOC26():
    """Lazy loading para TransaccionFOC26"""
    return lazy_import('TransaccionFOC26', 'transacciones')

def verify_password(stored_password, provided_password):
    seguridad = lazy_import('verify_password', 'seguridad')
    return seguridad(stored_password, provided_password) if seguridad else False

def is_sha256_hash(input_string):
    seguridad = lazy_import('is_sha256_hash', 'seguridad')
    return seguridad(input_string) if seguridad else False

# Clases con lazy loading
class SeguridadFOC26:
    """Wrapper con lazy loading para SeguridadFOC26"""
    
    @staticmethod
    def is_admin():
        seguridad = lazy_import('SeguridadFOC26', 'seguridad')
        return seguridad.is_admin() if seguridad else False
    
    @staticmethod
    def is_profesor():
        seguridad = lazy_import('SeguridadFOC26', 'seguridad')
        return seguridad.is_profesor() if seguridad else False
    
    @staticmethod
    def is_estudiante():
        seguridad = lazy_import('SeguridadFOC26', 'seguridad')
        return seguridad.is_estudiante() if seguridad else False
    
    @staticmethod
    def get_user_cedula():
        seguridad = lazy_import('SeguridadFOC26', 'seguridad')
        return seguridad.get_user_cedula() if seguridad else ""

# Database con lazy loading
class DatabaseFOC26:
    """Database con lazy loading de psycopg2"""
    
    def __init__(self):
        self.connection = None
        self.is_connected = False
        self.db_error = None
        self._conexion_manager = None
    
    @property
    def conexion_manager(self):
        if self._conexion_manager is None:
            conexion_postgresql = lazy_import('ConexionSimple', 'conexion_simple_corregido')
            self._conexion_manager = conexion_postgresql() if conexion_postgresql else None
        return self._conexion_manager
    
    def conectar(self):
        try:
            if not self.connection or not self.is_connected:
                if self.conexion_manager:
                    self.connection = self.conexion_manager.conectar()
                    self.is_connected = True
                    self.db_error = None
                    return self.connection
            return None
        except Exception as e:
            self.db_error = str(e)
            self.is_connected = False
            return None
    
    def verificar_conexion(self):
        return self.is_connected and self.connection is not None
    
    def ejecutar_consulta(self, query, params=None):
        try:
            if not self.verificar_conexion():
                if not self.conectar():
                    return None
            
            # Importar psycopg2 bajo demanda
            psycopg2 = lazy_import('psycopg2')
            if not psycopg2:
                return None
            
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                
                if cursor.description is not None:
                    resultados = cursor.fetchall()
                    if not query.strip().upper().startswith('SELECT'):
                        self.connection.commit()
                    return resultados if resultados else []
                else:
                    self.connection.commit()
                    return cursor.rowcount
        except Exception as e:
            print(f"Error ejecutando consulta: {e}")
            return None

# Forzar UTF-8 en variables de entorno
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LC_ALL'] = 'C.UTF-8'
os.environ['LANG'] = 'C.UTF-8'

# Variables globales para estado - DECLARADAS PRIMERO
db_connection = None
db_connected = False
db_error = None
debug_mode = os.getenv('DEBUG_MODE', 'False').lower() in ('1', 'true', 'yes')
db = None  # Database instance - se creará bajo demanda

# Clase de base de datos PostgreSQL con conexión dinámica para Railway
class DatabaseFOC26:
    """Gestor de base de datos PostgreSQL para FOC26DB con configuración dinámica"""
    
    def __init__(self):
        self.connection = None
        self.is_connected = False
        self.db_error = None
        self._conexion_manager = None
        self.db_settings = None
        self.database_url = None
    
    @property
    def conexion_manager(self):
        """Lazy loading del gestor de conexión"""
        if self._conexion_manager is None:
            conexion_postgresql = lazy_import('ConexionSimple', 'conexion_simple_corregido')
            if conexion_postgresql:
                self._conexion_manager = conexion_postgresql()
                # Configuración por defecto para ConexionSimple
                self.db_settings = {
                    'dbname': os.getenv('LOCAL_DB_NAME', 'FOC26DB'),
                    'user': os.getenv('LOCAL_DB_USER', 'postgres'),
                    'password': os.getenv('LOCAL_DB_PASSWORD', 'admin123'),
                    'host': os.getenv('LOCAL_DB_HOST', 'localhost'),
                    'port': os.getenv('LOCAL_DB_PORT', '5432'),
                    'sslmode': os.getenv('LOCAL_DB_SSL_MODE', 'prefer')
                }
                
                # URL de conexión para debugging (sin contraseña)
                self.database_url = f"postgresql://{self.db_settings['user']}@{self.db_settings['host']}:{self.db_settings['port']}/{self.db_settings['dbname']}?sslmode={self.db_settings['sslmode']}"
                
                print("Database FOC26 inicializado para Local")
                print(f"Database: {self.db_settings['dbname']}")
                print(f"Host: {self.db_settings['host']}")
                print(f"Port: {self.db_settings['port']}")
                print(f"User: {self.db_settings['user']}")
                print(f"SSL: {self.db_settings['sslmode']}")
                print(f"Source: local")
            else:
                self.db_error = "No se pudo importar ConexionSimple"
        
        return self._conexion_manager
    
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
                # Debug: mostrar estado antes de ejecutar
                print(f"DEBUG EJECUTAR CONSULTA - Intento {attempt + 1}")
                print(f"  self.is_connected: {self.is_connected}")
                print(f"  self.connection: {self.connection}")
                print(f"  Query: {query}")
                print(f"  Params: {params}")
                
                # Blindaje: asegurar conexión activa antes de usarla
                if not self.connection or not self.is_connected:
                    print("  Conexión no activa, intentando conectar...")
                    if not self.conectar():
                        print("  No se pudo conectar")
                        return None
                
                # Blindaje adicional: verificar que connection no sea None
                if self.connection is None:
                    print("ERROR: self.connection es None, reintentando conexión")
                    self.is_connected = False
                    continue
                
                print("  Ejecutando consulta...")
                with self.connection.cursor() as cursor:
                    cursor.execute(query, params)
                    print("  Consulta ejecutada exitosamente")
                    
                    if cursor.description is not None:
                        resultados = cursor.fetchall()
                        print(f"  Resultados fetchall: {resultados}")
                        # Commit INSERT ... RETURNING results; SELECT queries do not need commit.
                        if not query.strip().upper().startswith('SELECT'):
                            self.connection.commit()
                        if resultados:
                            print(f"  Retornando {len(resultados)} resultados")
                            return [dict(row) for row in resultados]
                        else:
                            print("  No hay resultados, retornando lista vacía")
                            return []
                    else:
                        print("  Cursor.description es None, haciendo commit")
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
    
    def asegurar_campos_media(self):
        """Asegura que las columnas de imagen y QR existan en la base de datos."""
        try:
            if not self.verificar_conexion():
                return False

            ddl_statements = [
                "ALTER TABLE persona ADD COLUMN IF NOT EXISTS foto_perfil_path TEXT",
                "ALTER TABLE estudiante ADD COLUMN IF NOT EXISTS qr_code_path TEXT",
                "ALTER TABLE taller ADD COLUMN IF NOT EXISTS imagen_path TEXT",
                "ALTER TABLE taller ADD COLUMN IF NOT EXISTS qr_code_path TEXT"
            ]
            for ddl in ddl_statements:
                self.ejecutar_consulta(ddl)
            return True
        except Exception as e:
            print(f"Error asegurando campos de media: {e}")
            return False

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

            # Verificar si ya existe el admin por login o cédula
            query_verificar = "SELECT COUNT(*) as total FROM usuario WHERE login_usuario = %s OR cedula_usuario = %s"
            params = (ADMIN_LOGIN, ADMIN_CEDULA)
            
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


def ensure_media_directories():
    media_paths = [
        os.path.join('media', 'photos'),
        os.path.join('media', 'formacion'),
        os.path.join('media', 'qr', 'estudiantes'),
        os.path.join('media', 'qr', 'formacion')
    ]
    for path in media_paths:
        os.makedirs(path, exist_ok=True)


def sanitize_identifier(identifier):
    return re.sub(r'[^A-Za-z0-9_-]', '_', str(identifier))


def save_uploaded_image(uploaded_file, target_folder, target_name):
    ensure_media_directories()
    filename = sanitize_identifier(target_name)
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ['.png', '.jpg', '.jpeg']:
        ext = '.png'
    target_path = os.path.join(target_folder, f"{filename}{ext}")
    with open(target_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return target_path


def create_qr_image(content, save_path=None):
    ensure_media_directories()
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    if save_path:
        img.save(save_path)
    buffer = io.BytesIO()
    img.save(buffer, 'PNG')
    buffer.seek(0)
    return buffer, img


def process_student_csv_upload(uploaded_file, db_instance):
    try:
        pd = get_pandas()
        if not pd:
            return {'success': False, 'message': 'Error: pandas no disponible'}
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        return {
            'success': False,
            'message': f'Error leyendo CSV: {e}',
            'processed': 0,
            'updated': 0,
            'errors': []
        }

    expected_columns = [
        'cedula', 'nombre', 'apellido', 'email', 'telefono',
        'fecha_nacimiento', 'genero', 'direccion', 'carrera',
        'semestre_formacion', 'estado_registro'
    ]

    df_columns = {col.strip().lower(): col for col in df.columns}
    missing_columns = [col for col in expected_columns if col not in df_columns]
    if missing_columns:
        return {
            'success': False,
            'message': f'El archivo CSV debe contener las columnas: {", ".join(expected_columns)}.',
            'processed': 0,
            'updated': 0,
            'errors': [f'Missing columns: {missing_columns}']
        }

    processed = 0
    updated = 0
    errors = []

    for index, raw_row in df.iterrows():
        try:
            row = {key: raw_row[df_columns[key]] if df_columns[key] in raw_row else None for key in expected_columns}
            cedula = str(row['cedula']).strip() if get_pandas().notna(row['cedula']) else ''
            row_number = int(index) + 2 if isinstance(index, (int, float)) else index
            if not cedula:
                errors.append(f'Fila {row_number}: Cédula vacía')
                continue

            nombre = str(row['nombre']).strip() if get_pandas().notna(row['nombre']) else ''
            apellido = str(row['apellido']).strip() if get_pandas().notna(row['apellido']) else ''
            email = str(row['email']).strip() if get_pandas().notna(row['email']) else ''
            telefono = str(row['telefono']).strip() if get_pandas().notna(row['telefono']) else ''
            direccion = str(row['direccion']).strip() if get_pandas().notna(row['direccion']) else ''
            genero = str(row['genero']).strip() if get_pandas().notna(row['genero']) else ''
            carrera = str(row['carrera']).strip() if get_pandas().notna(row['carrera']) else ''
            semestre_formacion = str(row['semestre_formacion']).strip() if get_pandas().notna(row['semestre_formacion']) else ''
            estado_registro = str(row['estado_registro']).strip() if get_pandas().notna(row['estado_registro']) else 'Activo'
            fecha_nacimiento = None
            if get_pandas().notna(row['fecha_nacimiento']):
                fecha_nacimiento = get_pandas().to_datetime(row['fecha_nacimiento'], errors='coerce').date()

            if not nombre or not apellido or not email:
                errors.append(f'Fila {row_number}: Nombre, apellido o email faltante')
                continue

            # Persona upsert
            persona_query = """
            INSERT INTO persona (nombre, apellido, email, cedula, telefono, fecha_nacimiento, genero, direccion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (cedula) DO UPDATE SET
                nombre = EXCLUDED.nombre,
                apellido = EXCLUDED.apellido,
                email = EXCLUDED.email,
                telefono = EXCLUDED.telefono,
                fecha_nacimiento = EXCLUDED.fecha_nacimiento,
                genero = EXCLUDED.genero,
                direccion = EXCLUDED.direccion
            RETURNING id
            """
            persona_result = db_instance.ejecutar_consulta(persona_query, (
                nombre, apellido, email, cedula, telefono, fecha_nacimiento, genero, direccion
            ))
            if not persona_result:
                errors.append(f'Fila {row_number}: Error creando/actualizando persona')
                continue

            persona_id = persona_result[0]['id']

            # Mantener contraseña existente si no se envía una nueva
            usuario_password_hash = None
            existing_password = db_instance.ejecutar_consulta(
                'SELECT contrasena FROM usuario WHERE cedula_usuario = %s',
                (cedula,)
            )
            if existing_password and len(existing_password) > 0:
                usuario_password_hash = existing_password[0].get('contrasena')

            if not usuario_password_hash:
                usuario_password_hash = hash_password('Estudiante123')

            login_usuario = email if email else cedula
            usuario_query = """
            INSERT INTO usuario (id_persona, cedula_usuario, login_usuario, email, contrasena, rol, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (cedula_usuario) DO UPDATE SET
                id_persona = EXCLUDED.id_persona,
                login_usuario = EXCLUDED.login_usuario,
                email = EXCLUDED.email,
                contrasena = EXCLUDED.contrasena,
                activo = EXCLUDED.activo
            RETURNING id
            """
            usuario_result = db_instance.ejecutar_consulta(usuario_query, (
                persona_id, cedula, login_usuario, email, usuario_password_hash, 'Estudiante', True
            ))
            if not usuario_result:
                errors.append(f'Fila {row_number}: Error creando/actualizando usuario')
                continue

            usuario_id = usuario_result[0]['id']

            # Estudiante insert/update
            estudiante_id_query = db_instance.ejecutar_consulta(
                'SELECT id_estudiante FROM estudiante WHERE id_usuario = %s',
                (usuario_id,)
            )
            if estudiante_id_query and len(estudiante_id_query) > 0:
                db_instance.ejecutar_consulta(
                    'UPDATE estudiante SET carrera = %s, semestre_formacion = %s, estado_registro = %s WHERE id_usuario = %s',
                    (carrera, semestre_formacion, estado_registro, usuario_id)
                )
                updated += 1
            else:
                db_instance.ejecutar_consulta(
                    'INSERT INTO estudiante (id_persona, id_usuario, carrera, semestre_formacion, estado_registro) VALUES (%s, %s, %s, %s, %s)',
                    (persona_id, usuario_id, carrera, semestre_formacion, estado_registro)
                )
                processed += 1

        except Exception as e:
            errors.append(f'Fila {row_number}: {e}')

    return {
        'success': len(errors) == 0,
        'message': f'Carga finalizada: {processed} insertados, {updated} actualizados.',
        'processed': processed,
        'updated': updated,
        'errors': errors
    }

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

# Conexion a base de datos FOC26DB - SOLO POSTGRESQL
def conectar_foc26db():
    """Conectar a la base de datos FOC26DB"""
    global db_connected, db_error, db
    
    try:
        # Crear instancia solo cuando se necesite
        if 'db' not in globals() or db is None:
            db = DatabaseFOC26()
        
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

# Función de login definitivo que funciona
def validar_login_directo(cedula, password):
    """Función de login definitiva con conexión por sesión"""
    try:
        from seguridad import login_sesion
        
        # Usar función login_sesion
        resultado = login_sesion(cedula, password)
        
        if resultado:
            return {
                'success': True,
                'usuario': resultado,
                'message': f"Bienvenido: {resultado['login_usuario']}"
            }
        else:
            return {'success': False, 'message': 'Cédula o contraseña incorrectos'}
            
    except Exception as e:
        return {'success': False, 'message': f'Error: {str(e)}'}
# Pantalla de login institucional
def pantalla_login():
    """Pantalla de login institucional IUJO"""
    try:
        st.title("SICADFOC 2026 - IUJO")
        st.header("Inicio de Sesión")
        st.markdown("### Ingrese sus credenciales para continuar")

        # Formulario de login reparado
        with st.form("login_form"):
            # Campo de cédula con V- por defecto
            cedula_input = st.text_input("Cédula", value="V-", placeholder="V-12345678", key="login_cedula", help="Solo ingrese los números después de V-")
            password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña", key="login_password")
            submit_button = st.form_submit_button("Iniciar Sesión", use_container_width=True)

            if submit_button:
                if cedula_input and password:
                    # Validar y procesar login con función directa
                    resultado_login = validar_login_directo(cedula_input.strip(), password.strip())
                    
                    if resultado_login['success']:
                        # Guardar sesión
                        st.session_state['autenticado'] = True
                        st.session_state['user'] = resultado_login['usuario']
                        st.success(f"Bienvenido: {resultado_login['usuario']['login_usuario']}")
                        st.rerun()
                    else:
                        st.error(resultado_login['message'])
                else:
                    st.error("Complete todos los campos.")

        st.markdown("---")
        if st.button("¿No tienes cuenta? Regístrate"):
            st.session_state['show_registration'] = True
            st.rerun()
    except Exception as e:
        st.error(f"Error en pantalla de login: {e}")


def dashboard_basico():
    """Panel de Control basico y funcional"""
    try:
        st.header("Panel de Control")
        
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
        
        # Mensaje simplificado de bienvenida según rol
        rol_formateado = user['rol'].strip().capitalize()
        if rol_formateado == 'Admin':
            st.success("Bienvenido Administrador")
        elif rol_formateado == 'Profesor':
            st.success("Bienvenido Profesor")
        elif rol_formateado == 'Estudiante':
            st.success("Bienvenido Estudiante")
        else:
            st.success(f"Bienvenido {rol_formateado}")
        
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
        
        # Validar acceso usando sistema de autorización dinámica
        from seguridad import tiene_permiso, SeguridadFOC26
        
        rol_usuario = SeguridadFOC26.get_user_role()
        if not tiene_permiso(rol_usuario, 'Estudiantes', 'Consultar'):
            st.error("Acceso denegado. No tienes permisos para consultar estudiantes.")
            st.stop()

        # Crear tabs según rol de usuario (usando validación centralizada)
        if SeguridadFOC26.is_admin() or SeguridadFOC26.is_profesor():
            # Validar permisos específicos para admin/profesor
            if tiene_permiso(rol_usuario, 'Estudiantes', 'Consultar'):
                tab1, tab2, tab3 = st.tabs(["Estudiantes Registrados", "Registrar Nuevo Estudiante", "Consultar/Editar"])
            else:
                st.error("Acceso denegado. No tienes permisos para consultar estudiantes.")
                st.stop()
        elif SeguridadFOC26.is_estudiante():
            # Estudiante solo puede consultar y editar su propio perfil
            if tiene_permiso(rol_usuario, 'Estudiantes', 'Consultar'):
                tab1, tab2, tab3 = st.tabs(["Mis Datos", "Editar Mi Perfil", "Consultar/Editar"])
            else:
                st.error("Acceso denegado. No tienes permisos para consultar datos.")
                st.stop()
        else:
            tab1 = st.container()
            tab2 = None
            tab3 = None

        with tab1:
            st.subheader("Estudiantes Registrados")

            # Solo admin y profesor pueden ver carga masiva
            if not SeguridadFOC26.is_estudiante():
                with st.expander("Carga Masiva de Estudiantes (.CSV)", expanded=False):
                    st.markdown("""
                    **Instrucciones:**
                    - El archivo debe contener las columnas: `cedula`, `nombre`, `apellido`, `email`, `telefono`, `fecha_nacimiento`, `genero`, `direccion`, `carrera`, `semestre_formacion`, `estado_registro`.
                    - Si la cédula ya existe se actualizará el registro en lugar de duplicarlo.
                    """)
                    archivo_csv_estudiantes = st.file_uploader(
                        "Seleccionar archivo CSV de estudiantes",
                        type=["csv"],
                        key="csv_estudiantes"
                    )
                    if archivo_csv_estudiantes is not None:
                        if st.button("Procesar carga masiva de estudiantes", type="primary", key="procesar_csv_estudiantes"):
                            resultado_csv = process_student_csv_upload(archivo_csv_estudiantes, db)
                            if resultado_csv['success']:
                                st.success(resultado_csv['message'])
                            else:
                                st.error(resultado_csv['message'])
                                if resultado_csv['errors']:
                                    for error in resultado_csv['errors']:
                                        st.write(f"- {error}")

            if db_connected and db is not None:
                # RESTAURACIÓN DE VISTAS GLOBALES: Sin filtros WHERE cedula para admin
                if str(st.session_state.get('user', {}).get('rol', '')).strip().upper() in ['ADMIN', 'ADMINISTRADOR']:
                    # VISTA GLOBAL: Admin ve TODOS los estudiantes sin filtros
                    query = """
                    SELECT
                        u.id as usuario_id,
                        u.login_usuario,
                        u.rol,
                        p.nombre,
                        p.apellido,
                        p.cedula,
                        p.telefono,
                        p.fecha_nacimiento,
                        p.genero as sexo,
                        p.direccion,
                        u.activo as activo,
                        u.fecha_registro,
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
                        u.login_usuario,
                        u.rol,
                        p.nombre,
                        p.apellido,
                        p.cedula,
                        p.telefono,
                        p.fecha_nacimiento,
                        p.genero as sexo,
                        p.direccion,
                        u.activo as activo,
                        u.fecha_registro,
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
                        u.login_usuario,
                        u.rol,
                        p.nombre,
                        p.apellido,
                        p.cedula,
                        p.telefono,
                        p.fecha_nacimiento,
                        p.genero as sexo,
                        p.direccion,
                        u.activo as activo,
                        u.fecha_registro,
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
                    df_resultado = get_pandas().DataFrame(resultado)

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
                                # Aplicar autorización dinámica para botón Editar
                                if tiene_permiso(rol_usuario, 'Estudiantes', 'Editar'):
                                    if st.button("✏️ Editar", type="primary", key="btn_editar_estudiante"):
                                        st.info(f"Editar estudiante: {estudiante_seleccionado}")
                            with col2:
                                # Aplicar autorización dinámica para botón Eliminar
                                if tiene_permiso(rol_usuario, 'Estudiantes', 'Eliminar'):
                                    if st.button("🗑️ Eliminar", type="secondary", key="btn_eliminar_estudiante"):
                                        st.warning(f"Se eliminará al estudiante {estudiante_seleccionado}.")
                                        # TODO: reemplazar esta acción de ejemplo por la eliminación real en la base de datos.
                                        st.success(f"Estudiante {estudiante_seleccionado} eliminado")
                                        st.rerun()
                                else:
                                    st.button("🗑️ Eliminar", type="secondary", key="btn_eliminar_estudiante", disabled=True,
                                             help="No tienes permisos para eliminar estudiantes")
                        
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
                    st.markdown("""
                    <div class="empty-state-card">
                        <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">📭</div>
                        <h3>No hay estudiantes registrados</h3>
                        <p>Actualmente no existen registros de estudiantes. Cambie a la pestaña "Registrar Nuevo Estudiante" para ingresar un nuevo perfil o a "Consultar/Editar" para revisar los datos existentes.</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("No hay conexión a la base de datos")

        if tab2 is not None:
            with tab2:
                if SeguridadFOC26.is_estudiante():
                    st.subheader("Editar Mi Perfil")
                    
                    # Obtener datos del estudiante actual
                    user_cedula = SeguridadFOC26.get_user_cedula()
                    query = """
                    SELECT
                        u.id as usuario_id,
                        u.login_usuario,
                        p.nombre,
                        p.apellido,
                        p.cedula,
                        p.telefono,
                        p.fecha_nacimiento,
                        p.genero as sexo,
                        p.direccion,
                        p.email,
                        e.carrera,
                        e.semestre_formacion,
                        e.estado_registro,
                        e.id as estudiante_id
                    FROM usuario u
                    JOIN persona p ON u.cedula_usuario = p.cedula
                    LEFT JOIN estudiante e ON u.id = e.id_usuario
                    WHERE u.rol = 'Estudiante' AND u.cedula_usuario = %s
                    """
                    resultado = db.ejecutar_consulta(query, (user_cedula,))
                    
                    if resultado and len(resultado) > 0:
                        estudiante = resultado[0]
                        
                        with st.form("form_editar_perfil"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                nombre = st.text_input("Nombre*", value=estudiante['nombre'])
                                apellido = st.text_input("Apellido*", value=estudiante['apellido'])
                                telefono = st.text_input("Teléfono", value=estudiante['telefono'] or "")
                                email = st.text_input("Email*", value=estudiante['email'])
                            
                            with col2:
                                fecha_nacimiento = st.date_input(
                                    "Fecha de Nacimiento",
                                    value=estudiante['fecha_nacimiento'] if estudiante['fecha_nacimiento'] else None
                                )
                                genero = st.selectbox(
                                    "Género",
                                    ["Masculino", "Femenino", "Otro"],
                                    index=["Masculino", "Femenino", "Otro"].index(estudiante['sexo']) if estudiante['sexo'] in ["Masculino", "Femenino", "Otro"] else 0
                                )
                                direccion = st.text_area("Dirección", value=estudiante['direccion'] or "")
                                
                                # Datos académicos
                                from configuracion import carreras_disponibles, semestres_disponibles
                                carrera = st.selectbox(
                                    "Carrera",
                                    carreras_disponibles,
                                    index=carreras_disponibles.index(estudiante['carrera']) if estudiante['carrera'] in carreras_disponibles else 0
                                )
                                semestre = st.selectbox(
                                    "Semestre",
                                    semestres_disponibles,
                                    index=semestres_disponibles.index(estudiante['semestre_formacion']) if estudiante['semestre_formacion'] in semestres_disponibles else 0
                                )
                            
                            if st.form_submit_button("Actualizar Mi Perfil", type="primary"):
                                # Actualizar persona con transacción segura
                                from utilidades_transaccion import ejecutar_transaccion
                                
                                resultado_persona = ejecutar_transaccion(
                                    db,
                                    """
                                    UPDATE persona 
                                    SET nombre = %s, apellido = %s, telefono = %s, email = %s, 
                                        fecha_nacimiento = %s, genero = %s, direccion = %s
                                    WHERE cedula = %s
                                    """,
                                    (nombre, apellido, telefono, email, fecha_nacimiento, genero, direccion, user_cedula),
                                    "UPDATE"
                                )
                                
                                if resultado_persona['exito']:
                                    # Actualizar estudiante con transacción segura
                                    resultado_estudiante = ejecutar_transaccion(
                                        db,
                                        """
                                        UPDATE estudiante 
                                        SET carrera = %s, semestre_formacion = %s
                                        WHERE id_usuario = %s
                                        """,
                                        (carrera, semestre, estudiante['usuario_id']),
                                        "UPDATE"
                                    )
                                    
                                    if resultado_estudiante['exito']:
                                        st.success("Perfil actualizado exitosamente")
                                        st.rerun()
                                    else:
                                        st.error(f"Error actualizando estudiante: {resultado_estudiante['error']}")
                                else:
                                    st.error(f"Error actualizando persona: {resultado_persona['error']}")
                    else:
                        st.error("No se encontró tu información de estudiante.")
                else:
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
                            u.login_usuario,
                            u.rol,
                            p.nombre,
                            p.apellido,
                            p.cedula,
                            p.telefono,
                            p.fecha_nacimiento,
                            p.genero as sexo,
                            p.direccion,
                            u.activo as activo,
                            u.fecha_registro,
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
                
                df_busqueda = get_pandas().DataFrame(st.session_state['resultados_busqueda_estudiante'])
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

# Modulo de Mis Datos (para estudiantes)
def modulo_mis_datos():
    """Módulo para que los estudiantes vean y completen su información personal"""
    try:
        # Verificar si necesita completar registro
        if st.session_state.get('completar_registro_estudiante', False):
            st.header("Completar Registro de Usuario")
            st.info("Por favor completa tu información para poder acceder a todos los módulos.")
            mostrar_formulario_completar_registro()
            return
        
        st.header("Mis Datos Personales")
        
        if not db_connected or db is None:
            st.error("No hay conexión a la base de datos")
            return
        
        # Obtener información del usuario logueado
        user = st.session_state['user']
        user_cedula = SeguridadFOC26.get_user_cedula()
        
        # Consultar información completa del estudiante
        query_info = """
        SELECT 
            p.nombre,
            p.apellido,
            p.cedula,
            p.email,
            p.telefono,
            p.fecha_nacimiento,
            p.genero,
            p.direccion,
            u.login_usuario,
            u.fecha_registro as fecha_registro_usuario
        FROM persona p
        JOIN usuario u ON p.cedula = u.cedula_usuario
        WHERE u.cedula_usuario = %s AND u.rol = 'Estudiante'
        """
        
        resultado = db.ejecutar_consulta(query_info, (user_cedula,))
        
        if resultado and len(resultado) > 0:
            info = resultado[0]
            
            # Mostrar información en formato amigable
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📋 Información Personal")
                st.info(f"**Nombre:** {info['nombre']} {info['apellido']}")
                st.info(f"**Cédula:** {info['cedula']}")
                st.info(f"**Email:** {info['email']}")
                st.info(f"**Teléfono:** {info['telefono']}")
                
            with col2:
                st.markdown("### 🎓 Información Académica")
                st.info(f"**Carrera:** {info['carrera']}")
                st.info(f"**Semestre:** {info['semestre_formacion']}")
                st.info(f"**Estado:** {info['estado_estudiante']}")
                st.info(f"**Usuario:** {info['login_usuario']}")
            
            st.markdown("---")
            st.markdown("### 📅 Información Adicional")
            col3, col4 = st.columns(2)
            
            with col3:
                if info['fecha_nacimiento']:
                    st.info(f"**Fecha Nacimiento:** {info['fecha_nacimiento']}")
                st.info(f"**Género:** {info['genero']}")
            
            with col4:
                if info['direccion']:
                    st.info(f"**Dirección:** {info['direccion']}")
                st.info(f"**Registro:** {info['fecha_registro_usuario']}")
            
            # Mostrar talleres inscritos
            st.markdown("---")
            st.markdown("### 📚 Talleres Inscritos")
            
            query_talleres = """
            SELECT 
                fc.nombre_taller,
                fc.descripcion,
                fc.fecha_inicio,
                fc.fecha_fin,
                fc.estado,
                i.fecha_inscripcion
            FROM inscripcion i
            JOIN formacion_complementaria fc ON i.id_formacion = fc.id
            JOIN usuario u ON i.id_estudiante = u.id
            WHERE u.cedula_usuario = %s
            ORDER BY i.fecha_inscripcion DESC
            """
            
            talleres = db.ejecutar_consulta(query_talleres, (user_cedula,))
            
            if talleres and len(talleres) > 0:
                df_talleres = get_pandas().DataFrame(talleres)
                st.dataframe(
                    df_talleres[["nombre_taller", "fecha_inicio", "fecha_fin", "estado", "fecha_inscripcion"]],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "nombre_taller": st.column_config.TextColumn("Taller"),
                        "fecha_inicio": st.column_config.DateColumn("Inicio"),
                        "fecha_fin": st.column_config.DateColumn("Fin"),
                        "estado": st.column_config.TextColumn("Estado"),
                        "fecha_inscripcion": st.column_config.DateColumn("Inscripción")
                    }
                )
            else:
                st.warning("No estás inscrito en ningún taller actualmente.")
                
        else:
            st.error("No se encontró tu información de estudiante.")
            
    except Exception as e:
        st.error(f"Error en módulo Mis Datos: {e}")

def mostrar_formulario_completar_registro():
    """Formulario para completar registro de usuario con asignación de rol"""
    try:
        user = st.session_state['user']
        user_cedula = SeguridadFOC26.get_user_cedula()
        
        st.markdown("### Información Personal")
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombres*", help="Nombres completos", key="form_nombre")
            cedula = st.text_input("Cédula", value=user_cedula, disabled=True, help="Cédula del usuario")
            whatsapp = st.text_input("WhatsApp*", help="Formato: +58 4XX XXX XXXX", key="form_whatsapp")
            
        with col2:
            apellido = st.text_input("Apellidos*", help="Apellidos completos", key="form_apellido")
            email = st.text_input("Correo Electrónico*", help="Correo electrónico válido", key="form_email")
            fecha_nacimiento = st.date_input("Fecha de Nacimiento*", help="Fecha de nacimiento", key="form_fecha")
        
        st.markdown("### Información de Rol")
        col3, col4 = st.columns(2)
        
        with col3:
            rol_asignar = st.selectbox("Rol a Asignar*", ["Estudiante", "Profesor"], help="Seleccione el rol que tendrá el usuario", key="form_rol")
            
        with col4:
            if rol_asignar == "Estudiante":
                carrera = st.selectbox("Carrera*", get_carreras() if get_carreras() else [], help="Carrera que estudia", key="form_carrera")
                semestre = st.selectbox("Semestre*", get_semestres() if get_semestres() else [], help="Semestre actual", key="form_semestre")
            else:
                # Generar código automático para profesores
                from datetime import datetime
                año_actual = datetime.now().year
                codigo_autogenerado = f"PROF-{año_actual}-{user_cedula}"
                codigo_profesor = st.text_input("Código Profesor", value=codigo_autogenerado, disabled=True, help="Código generado automáticamente", key="form_codigo")
        
        genero = st.selectbox("Género*", get_generos() if get_generos() else [], help="Género del usuario", key="form_genero")
        
        # Botón de guardar
        if st.button("Guardar Información", type="primary", use_container_width=True):
            # Validación de campos obligatorios según rol
            campos_validos = True
            campos_faltantes = []
            
            if not nombre:
                campos_validos = False
                campos_faltantes.append("Nombres")
            if not apellido:
                campos_validos = False
                campos_faltantes.append("Apellidos")
            if not email:
                campos_validos = False
                campos_faltantes.append("Correo Electrónico")
            if not whatsapp:
                campos_validos = False
                campos_faltantes.append("WhatsApp")
            if not fecha_nacimiento:
                campos_validos = False
                campos_faltantes.append("Fecha de Nacimiento")
            if not genero:
                campos_validos = False
                campos_faltantes.append("Género")
            
            # Validaciones específicas por rol
            if rol_asignar == "Estudiante":
                if not carrera:
                    campos_validos = False
                    campos_faltantes.append("Carrera")
                if not semestre:
                    campos_validos = False
                    campos_faltantes.append("Semestre")
            # Nota: Código de profesor se genera automáticamente, no requiere validación
            
            if campos_validos:
                try:
                    # Validar formato de WhatsApp
                    if not whatsapp.startswith("+58") or len(whatsapp) < 12:
                        st.error("El WhatsApp debe tener formato: +58 4XX XXX XXXX")
                        return
                    
                    # Actualizar persona con transacción segura
                    from utilidades_transaccion import ejecutar_transaccion
                    
                    resultado_persona = ejecutar_transaccion(
                        db,
                        """
                        UPDATE persona 
                        SET nombre = %s, apellido = %s, email = %s, telefono = %s, 
                            fecha_nacimiento = %s, genero = %s
                        WHERE cedula = %s
                        """,
                        (nombre.strip(), apellido.strip(), email.strip(), whatsapp.strip(),
                         fecha_nacimiento, genero.strip(), user_cedula),
                        "UPDATE"
                    )
                    
                    if resultado_persona['exito']:
                        # Actualizar rol en tabla usuario con transacción segura
                        resultado_rol = ejecutar_transaccion(
                            db,
                            "UPDATE usuario SET rol = %s WHERE id = %s",
                            (rol_asignar, user['id']),
                            "UPDATE"
                        )
                        
                        if resultado_rol['exito']:
                            # Insertar en tabla específica según rol con transacción segura
                            if rol_asignar == "Estudiante":
                                resultado_estudiante = ejecutar_transaccion(
                                    db,
                                    """
                                    INSERT INTO estudiante (id_usuario, carrera, semestre_formacion, estado_registro)
                                    VALUES (%s, %s, %s, 'Activo')
                                    ON CONFLICT (id_usuario) DO UPDATE SET
                                        carrera = EXCLUDED.carrera,
                                        semestre_formacion = EXCLUDED.semestre_formacion,
                                        estado_registro = EXCLUDED.estado_registro
                                    """,
                                    (user['id'], carrera.strip(), semestre.strip()),
                                    "INSERT"
                                )
                                
                                if resultado_estudiante['exito']:
                                    st.success("Información guardada exitosamente")
                                    st.rerun()
                                else:
                                    st.error(f"Error guardando estudiante: {resultado_estudiante['error']}")
                            else:  # Profesor
                                # Generar código automático para guardar en base de datos
                                from datetime import datetime
                                año_actual = datetime.now().year
                                codigo_autogenerado_final = f"PROF-{año_actual}-{user_cedula}"
                                
                                resultado_profesor = ejecutar_transaccion(
                                    db,
                                    """
                                    INSERT INTO profesor (id_usuario, codigo_profesor, estado_registro)
                                    VALUES (%s, %s, 'Activo')
                                    ON CONFLICT (id_usuario) DO UPDATE SET
                                        codigo_profesor = EXCLUDED.codigo_profesor,
                                        estado_registro = EXCLUDED.estado_registro
                                    """,
                                    (user['id'], codigo_autogenerado_final.strip()),
                                    "INSERT"
                                )
                                
                                if resultado_profesor['exito']:
                                    st.success("Información guardada exitosamente")
                                    st.rerun()
                                else:
                                    st.error(f"Error guardando profesor: {resultado_profesor['error']}")
                        else:
                            st.error(f"Error actualizando rol: {resultado_rol['error']}")
                    else:
                        st.error(f"Error actualizando persona: {resultado_persona['error']}")
                    
                    # Actualizar sesión para reflejar nuevo rol
                    st.session_state['user']['rol'] = rol_asignar
                    st.session_state['completar_registro_estudiante'] = False
                    
                    st.success(f"¡Información guardada exitosamente! Rol asignado: {rol_asignar}")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error al guardar información: {e}")
            else:
                st.error(f"Por favor complete los siguientes campos obligatorios: {', '.join(campos_faltantes)}")
                
    except Exception as e:
        st.error(f"Error en formulario de completar registro: {e}")

# Modulo de Profesores
def modulo_profesores():
    """Módulo para gestión de profesores"""
    try:
        st.header("Gestión de Profesores")
        
        # Validar acceso usando sistema de autorización dinámica
        from seguridad import tiene_permiso, SeguridadFOC26
        
        rol_usuario = SeguridadFOC26.get_user_role()
        if not tiene_permiso(rol_usuario, 'Profesores', 'Consultar'):
            st.error("Acceso denegado. No tienes permisos para consultar profesores.")
            st.stop()
        TransaccionFOC26_class = get_TransaccionFOC26()
        trans_manager = TransaccionFOC26_class(db.connection) if TransaccionFOC26_class else None

        if not db_connected or db is None:
            st.error("No hay conexión a la base de datos")
            return

        # Definir tabs según rol de usuario
        if SeguridadFOC26.is_admin() or SeguridadFOC26.is_profesor():
            tab1, tab2 = st.tabs(["Listado de Profesores", "Registro de Nuevo Profesor"])
        else:
            # Estudiante solo puede consultar
            tab1 = st.container()
            tab2 = None

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
                df_profesores = get_pandas().DataFrame(profesores)

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
                acciones_disponibles = []
                
                if SeguridadFOC26.is_admin():
                    acciones_disponibles = ["Consultar", "Editar", "Eliminar"]
                elif SeguridadFOC26.is_profesor():
                    acciones_disponibles = ["Consultar", "Editar"]
                elif SeguridadFOC26.is_estudiante():
                    acciones_disponibles = ["Consultar"]
                
                if not acciones_disponibles:
                    st.warning("No tienes permisos para realizar acciones en este módulo.")
                    return
                
                accion = st.radio("Acción", acciones_disponibles)

                if accion == "Consultar":
                    st.markdown("### Detalles del profesor")
                    
                    # Formulario en dos columnas
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Columna 1: Cédula, Nombre, Apellido
                        cedula_profesor = st.text_input(
                            "Cédula Profesor", 
                            value=profesor_seleccionado['cedula_profesor'], 
                            disabled=True,
                            help="Cédula del profesor (solo lectura)"
                        )
                        nombre = st.text_input(
                            "Nombre", 
                            value=profesor_seleccionado['nombre'],
                            disabled=True,
                            help="Nombre del profesor (solo lectura)"
                        )
                        apellido = st.text_input(
                            "Apellido", 
                            value=profesor_seleccionado['apellido'],
                            disabled=True,
                            help="Apellido del profesor (solo lectura)"
                        )
                    
                    with col2:
                        # Columna 2: Email Institucional, Correo Personal, Especialidad
                        email_institucional = st.text_input(
                            "Email Institucional", 
                            value=profesor_seleccionado['email_institucional'],
                            disabled=True,
                            help="Email institucional (solo lectura)"
                        )
                        
                        # Correo Personal editable si es NULL
                        correo_personal_value = profesor_seleccionado.get('correo_personal', '') or ''
                        correo_personal = st.text_input(
                            "Correo Personal", 
                            value=correo_personal_value,
                            help="Correo personal (editable si está vacío)"
                        )
                        
                        # Especialidad como dropdown
                        especialidades_opciones = ['Electrónica', 'Informática', 'Industrial', 'Civil', 'Mecánica', 'Química', 'Eléctrica', 'Otras']
                        especialidad_actual = profesor_seleccionado.get('especialidad', '') or ''
                        especialidad = st.selectbox(
                            "Especialidad",
                            opciones=especialidades_opciones,
                            index=especialidades_opciones.index(especialidad_actual) if especialidad_actual in especialidades_opciones else 0,
                            help="Seleccione la especialidad del profesor"
                        )
                        
                        # Departamento como dropdown
                        departamentos_opciones = ['Ciencias Sociales', 'Tecnología', 'Ingeniería', 'Ciencias Básicas', 'Humanidades', 'Administración']
                        departamento_actual = profesor_seleccionado.get('departamento', '') or ''
                        departamento = st.selectbox(
                            "Departamento",
                            opciones=departamentos_opciones,
                            index=departamentos_opciones.index(departamento_actual) if departamento_actual in departamentos_opciones else 0,
                            help="Seleccione el departamento del profesor"
                        )
                    
                    # Estado como badge/etiqueta
                    estado_profesor = profesor_seleccionado.get('estado', 'Activo')
                    if estado_profesor == 'Activo':
                        st.markdown(
                            f'<span style="background-color: #28a745; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold;">{estado_profesor}</span>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f'<span style="background-color: #dc3545; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold;">{estado_profesor}</span>',
                            unsafe_allow_html=True
                        )
                elif accion == "Eliminar":
                    try:
                        from utilidades_transaccion import ejecutar_transaccion
                            
                        # Eliminar registro de profesor con transacción segura
                        resultado = ejecutar_transaccion(
                            db,
                            "DELETE FROM profesor WHERE id_profesor = %s",
                            (profesor_seleccionado['id_profesor'],),
                            "DELETE"
                        )
                            
                        if resultado['exito']:
                            # Actualizar rol del usuario a inactivo
                            resultado_usuario = ejecutar_transaccion(
                                db,
                                "UPDATE usuario SET activo = false WHERE id = %s",
                                (profesor_seleccionado['id_usuario'],),
                                "UPDATE"
                            )
                                
                            if resultado_usuario['exito']:
                                st.success(f"Profesor eliminado exitosamente")
                                st.rerun()
                            else:
                                st.error(f"Error actualizando usuario: {resultado_usuario['error']}")
                        else:
                            st.error(f"Error eliminando profesor: {resultado['error']}")
                    except Exception as e:
                        st.error(f"Error al eliminar profesor: {e}")
                elif accion == "Editar":
                    # Validar permisos de edición
                    if SeguridadFOC26.is_estudiante():
                        st.error("Acceso denegado. Los estudiantes no pueden editar profesores.")
                        st.stop()
                    
                    st.markdown("### Detalles del profesor")
                    
                    # Formulario en dos columnas para vista previa antes de editar
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Columna 1: Cédula, Nombre, Apellido
                        cedula_profesor = st.text_input(
                            "Cédula Profesor", 
                            value=profesor_seleccionado['cedula_profesor'], 
                            disabled=True,
                            help="Cédula del profesor (solo lectura)"
                        )
                        nombre = st.text_input(
                            "Nombre", 
                            value=profesor_seleccionado['nombre'],
                            disabled=True,
                            help="Nombre del profesor (solo lectura)"
                        )
                        apellido = st.text_input(
                            "Apellido", 
                            value=profesor_seleccionado['apellido'],
                            disabled=True,
                            help="Apellido del profesor (solo lectura)"
                        )
                    
                    with col2:
                        # Columna 2: Email Institucional, Correo Personal, Especialidad
                        email_institucional = st.text_input(
                            "Email Institucional", 
                            value=profesor_seleccionado['email_institucional'],
                            disabled=True,
                            help="Email institucional (solo lectura)"
                        )
                        
                        # Correo Personal editable si es NULL
                        correo_personal_value = profesor_seleccionado.get('correo_personal', '') or ''
                        correo_personal = st.text_input(
                            "Correo Personal", 
                            value=correo_personal_value,
                            disabled=True,
                            help="Correo personal (vista previa)"
                        )
                        
                        # Especialidad como dropdown (solo lectura en vista previa)
                        especialidades_opciones = ['Electrónica', 'Informática', 'Industrial', 'Civil', 'Mecánica', 'Química', 'Eléctrica', 'Otras']
                        especialidad_actual = profesor_seleccionado.get('especialidad', '') or ''
                        especialidad = st.selectbox(
                            "Especialidad",
                            opciones=especialidades_opciones,
                            index=especialidades_opciones.index(especialidad_actual) if especialidad_actual in especialidades_opciones else 0,
                            disabled=True,
                            help="Especialidad del profesor (vista previa)"
                        )
                        
                        # Departamento como dropdown (solo lectura en vista previa)
                        departamentos_opciones = ['Ciencias Sociales', 'Tecnología', 'Ingeniería', 'Ciencias Básicas', 'Humanidades', 'Administración']
                        departamento_actual = profesor_seleccionado.get('departamento', '') or ''
                        departamento = st.selectbox(
                            "Departamento",
                            opciones=departamentos_opciones,
                            index=departamentos_opciones.index(departamento_actual) if departamento_actual in departamentos_opciones else 0,
                            disabled=True,
                            help="Departamento del profesor (vista previa)"
                        )
                    
                    # Estado como badge/etiqueta
                    estado_profesor = profesor_seleccionado.get('estado', 'Activo')
                    if estado_profesor == 'Activo':
                        st.markdown(
                            f'<span style="background-color: #28a745; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold;">{estado_profesor}</span>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f'<span style="background-color: #dc3545; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold;">{estado_profesor}</span>',
                            unsafe_allow_html=True
                        )
                    
                    st.markdown("---")
                    st.info("Use el formulario de abajo para editar los datos del profesor.")

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
                            from utilidades_transaccion import ejecutar_transaccion
                            
                            email_institucional = str(email_institucional or "")
                            correo_personal = str(correo_personal or "")
                            if not re.match(r"[^@]+@[^@]+\.[^@]+", email_institucional):
                                st.error("Formato de correo institucional inválido")
                            elif correo_personal and not re.match(r"[^@]+@[^@]+\.[^@]+", correo_personal):
                                st.error("Formato de correo personal inválido")
                            else:
                                # Actualizar persona con transacción segura
                                resultado_persona = ejecutar_transaccion(
                                    db,
                                    "UPDATE persona SET nombre = %s, apellido = %s, email = %s WHERE id = %s",
                                    (nombre.strip(), apellido.strip(), email_institucional.strip(), profesor_seleccionado['id_persona']),
                                    "UPDATE"
                                )
                                
                                if resultado_persona['exito']:
                                    # Actualizar profesor con transacción segura
                                    resultado_profesor = ejecutar_transaccion(
                                        db,
                                        "UPDATE profesor SET correo_personal = %s, especialidad = %s, departamento = %s, estado = %s WHERE id_profesor = %s",
                                        (correo_personal.strip(), especialidad.strip(), departamento.strip(), estado, profesor_seleccionado['id_profesor']),
                                        "UPDATE"
                                    )
                                    
                                    if resultado_profesor['exito']:
                                        st.success("Datos de profesor actualizados correctamente")
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
        st.title("SICADFOC 2026 - IUJO")
        st.header("Registro de Nuevo Usuario")
        
        # Generar CAPTCHA si no existe en session_state
        if 'captcha_code' not in st.session_state:
            st.session_state['captcha_code'] = str(random.randint(1000, 9999))
        
        with st.form("form_registro_usuario"):
            st.markdown("### Datos de Registro")
            
            col1, col2 = st.columns(2)
            
            with col1:
                cedula = st.text_input("Cédula*", placeholder="V12345678", help="Número de cédula con formato V-XXXXXXXX", key="registro_cedula")
                email = st.text_input("Correo Electrónico*", placeholder="usuario@iujo.edu", help="Correo electrónico válido", key="registro_email")
            
            with col2:
                contrasena = st.text_input("Contraseña*", type="password", placeholder="Mínimo 8 caracteres", help="Contraseña segura", key="registro_contrasena")
                confirmar_contrasena = st.text_input("Confirmar Contraseña*", type="password", placeholder="Repita la contraseña", help="Debe coincidir con la contraseña", key="registro_confirmar")
            
            st.markdown("### Validación CAPTCHA")
            
            col3, col4 = st.columns([1, 2])
            
            with col3:
                st.markdown("**Código CAPTCHA:**")
                st.code(st.session_state['captcha_code'], language='')
            
            with col4:
                captcha_input = st.text_input("Ingrese el código CAPTCHA*", placeholder="1234", help="Copie exactamente el código mostrado arriba", key="registro_captcha")
            
            # Botones
            col5, col6 = st.columns([3, 1])
            
            with col5:
                submit_button = st.form_submit_button("Registrar Usuario")
            
            with col6:
                refresh_button = st.form_submit_button("Nuevo CAPTCHA")
            
            if refresh_button:
                st.session_state['captcha_code'] = str(random.randint(1000, 9999))
                st.rerun()
            
            if submit_button:
                # Variables para resaltar campos en conflicto
                campo_conflicto = None
                mensaje_error = ""
                
                # Validación de campos vacíos
                if not cedula:
                    mensaje_error = "Por favor, ingrese su Cédula."
                    campo_conflicto = "cedula"
                elif not email:
                    mensaje_error = "Por favor, ingrese su Correo Electrónico."
                    campo_conflicto = "email"
                elif not contrasena:
                    mensaje_error = "Por favor, ingrese su Contraseña."
                    campo_conflicto = "contrasena"
                elif not confirmar_contrasena:
                    mensaje_error = "Por favor, confirme su Contraseña."
                    campo_conflicto = "confirmar_contrasena"
                elif not captcha_input:
                    mensaje_error = "Por favor, ingrese el código CAPTCHA."
                    campo_conflicto = "captcha"
                else:
                    # Validar CAPTCHA
                    if captcha_input.strip() != st.session_state['captcha_code']:
                        mensaje_error = "Código CAPTCHA incorrecto. Intente nuevamente."
                        campo_conflicto = "captcha"
                        st.session_state['captcha_code'] = str(random.randint(1000, 9999))
                    # Validar contraseñas
                    elif contrasena != confirmar_contrasena:
                        mensaje_error = "Las contraseñas no coinciden."
                        campo_conflicto = "confirmar_contrasena"
                    # Resaltar campo en conflicto con CSS
                    if campo_conflicto:
                        css_resaltado = f"""
                        <style>
                        div[data-testid="stTextInput"] > div > div > input[data-testid="stTextInput{campo_conflicto.capitalize()}"] {{
                            border: 2px solid #ff4444 !important;
                            box-shadow: 0 0 8px rgba(255, 68, 68, 0.3) !important;
                        }}
                        </style>
                        """
                        st.markdown(css_resaltado, unsafe_allow_html=True)
                    
                    return
                
                # Si no hay errores, proceder con el registro
                try:
                    if db_connected and db is not None:
                        # Importar utilidades de normalización
                        from utilidades_bd import normalizar_cedula, verificar_cedula_existente, insertar_usuario_normalizado
                        
                        # Preparar datos del usuario
                        datos_usuario = {
                            'cedula': str(cedula).strip(),
                            'contrasena': contrasena,
                            'rol': 'Estudiante',
                            'login': email,
                            'email': email
                        }
                        
                        # Insertar usuario con normalización y verificación
                        resultado = insertar_usuario_normalizado(db, datos_usuario)
                        
                        if resultado['exito']:
                            st.success(resultado['mensaje'])
                            st.info(f"Cédula normalizada: {resultado['cedula']}")
                            st.info(f"Email: {email}")
                            st.info("Ahora puede iniciar sesión con sus credenciales.")
                            
                            # Limpiar CAPTCHA
                            st.session_state['captcha_code'] = str(random.randint(1000, 9999))
                            st.session_state['show_registration'] = False
                            
                            # Opcional: redirigir a login
                            st.session_state['pagina'] = 'Panel de Control'
                            st.rerun()
                        else:
                            st.error(resultado['error'])
                    else:
                        st.error("No hay conexión a la base de datos.")
                except Exception as e:
                    st.error(f"Error al registrar usuario: {e}")
    except Exception as e:
        st.error(f"Error en módulo de registro: {e}")

# Funcion principal basica
def main():
    """Funcion principal basica y funcional"""
    try:
        # Intentar conexion a FOC26DB
        conectar_foc26db()
        
        # Siempre mostrar login primero
        if not st.session_state.get('autenticado', False):
            if st.session_state.get('show_registration', False):
                modulo_registro_usuario()
                if st.button("Volver a iniciar sesión"):
                    st.session_state['show_registration'] = False
                    st.rerun()
            else:
                pantalla_login()
        else:
            # Mostrar sidebar solo despues de login exitoso
            
            # Sidebar dinamico con navegacion institucional
            with st.sidebar:
                
                st.markdown("### Navegación")
                
                # Informacion del usuario
                user = st.session_state['user']
                
                # REFRESCO DE SESIÓN: Normalizar rol en sidebar también
                if 'rol' in user and user['rol']:
                    user['rol'] = user['rol'].strip().capitalize()
                    st.session_state['user'] = user  # Actualizar sesión inmediatamente
                
                st.info(f"Rol: {user['rol']}")
                st.markdown("---")
                
                # Menu de navegacion exclusivo según rol de usuario
                opciones_menu = ['Panel de Control']
                
                # NAVEGACIÓN EXCLUSIVA: Profesores, Estudiantes, Formación, Reportes, Configuración
                if str(st.session_state.get('user', {}).get('rol', '')).strip().upper() in ['ADMIN', 'ADMINISTRADOR']:
                    opciones_menu.extend(['Profesores', 'Estudiantes', 'Formación Complementaria', 'Certificaciones', 'Generador QR', 'Reportes', 'Configuración'])
                elif SeguridadFOC26.is_profesor():
                    # PERFIL PROFESOR: Módulos habilitados
                    opciones_menu.extend(['Profesores', 'Estudiantes', 'Formación Complementaria', 'Certificaciones'])
                elif SeguridadFOC26.is_estudiante():
                    # PERFIL ESTUDIANTE: Módulos restringidos
                    opciones_menu.extend(['Mis Datos', 'Formación Complementaria', 'Certificaciones'])
                
                pagina_default = st.session_state.get('pagina')
                pagina_index = opciones_menu.index(pagina_default) if pagina_default in opciones_menu else 0
                pagina = st.radio(
                    "Seleccionar Módulo:",
                    opciones_menu,
                    index=pagina_index,
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
                if st.session_state['pagina'] == 'Panel de Control':
                    dashboard_basico()
                elif st.session_state['pagina'] == 'Mis Datos':
                    modulo_mis_datos()
                elif st.session_state['pagina'] == 'Profesores':
                    modulo_profesores()
                elif st.session_state['pagina'] == 'Estudiantes':
                    modulo_estudiantes()
                elif st.session_state['pagina'] == 'Formación Complementaria':
                    # Ejecutar módulo de formación complementaria local
                    modulo_formacion_complementaria(db)
                elif st.session_state['pagina'] == 'Certificaciones':
                    # Ejecutar gestor de certificaciones unificado
                    gestor_certificaciones_unificado()
                elif st.session_state['pagina'] == 'Generador QR':
                    # Ejecutar módulo generador de QR
                    from qr_generator import interfaz_qr_generator
                    interfaz_qr_generator()
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
                            
                            df_resultados = get_pandas().DataFrame(st.session_state['consulta_resultados'])
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
                                excel_buffer = io.BytesIO()
                                with get_pandas().ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                                    df_resultados.to_excel(writer, index=False)
                                excel_buffer.seek(0)
                                st.download_button(
                                    label="📊 Descargar Excel",
                                    data=excel_buffer.getvalue(),
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
                            
                            df_reporte = get_pandas().DataFrame(st.session_state['reporte_predefinido_datos'])
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
                                    df_rol = get_pandas().DataFrame(resultado_rol)
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
                                    df_talleres = get_pandas().DataFrame(resultado_talleres)
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
                                    df_inscripciones = get_pandas().DataFrame(resultado_inscripciones)
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
                                    df_carreras = get_pandas().DataFrame(resultado_carreras)
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
                                    df_prof_talleres = get_pandas().DataFrame(resultado_prof_talleres)
                                    st.dataframe(df_prof_talleres, use_container_width=True, hide_index=True)
                        else:
                            st.error("Acceso denegado. Solo los administradores pueden ver reportes.")
                            st.stop()
                elif st.session_state['pagina'] == 'Configuración':
                    from modulo_configuracion import modulo_configuracion
                    modulo_configuracion()
            except Exception as e:
                st.error(f"Error critico en la aplicacion: {e}")
                st.markdown("### La aplicacion ha encontrado un error inesperado")
                st.markdown("Por favor, recarga la pagina.")

    except Exception as e:
        st.error(f"Error critico en la aplicacion principal: {e}")
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
        st.session_state['pagina'] = 'Panel de Control'
    if 'show_registration' not in st.session_state:
        st.session_state['show_registration'] = False
    
    # EJECUTAR SIEMPRE
    main()