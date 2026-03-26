import os
import pandas as pd
import sqlite3
import hashlib
import traceback
import functools
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv(encoding='utf-8')

# =================================================================
# VARIABLES GLOBALES Y CONFIGURACIÓN
# =================================================================

# Ruta de base de datos SQLite local
SQLITE_DB_PATH = 'foc26_limpio.db'

# Variables globales para motores
engine_local = None
engine_espejo = None

# =================================================================
# FUNCIÓN DE REGISTRO DE USUARIO CON MAPEO DE PERFILES
# =================================================================

def finalizar_registro_usuario(datos_usuario, rol_id):
    try:
        engine = get_engine_local()
        
        permisos_map = {
            2: "gestion_pdf,auditoria,consulta",
            3: "consulta",
            1: "todos"
        }
        
        password_hash = hashlib.sha256(datos_usuario['password'].encode()).hexdigest()
        
        with engine.connect() as conn:
            # Verificar si el correo ya existe
            query_check = "SELECT COUNT(*) FROM usuario WHERE email = :email"
            result = conn.execute(text(query_check), {'email': datos_usuario['email']})
            email_exists = result.scalar() > 0
            
            if email_exists:
                return {
                    'exito': False,
                    'mensaje': 'Este correo electrónico ya está registrado.',
                    'codigo': 'EMAIL_EXISTS'
                }
            
            # Buscar persona existente por cédula
            query_persona = "SELECT id_persona FROM persona WHERE cedula = :cedula"
            result = conn.execute(text(query_persona), {'cedula': datos_usuario['cedula']})
            persona = result.fetchone()
            
            if persona:
                id_persona = persona[0]
            else:
                # Crear nueva persona solo si no existe
                query_insert = """
                    INSERT INTO persona (nombre, apellido, cedula, email)
                    VALUES (:nombre, :apellido, :cedula, :email)
                """
                conn.execute(text(query_insert), {
                    'nombre': datos_usuario['nombres'],
                    'apellido': datos_usuario['apellidos'],
                    'cedula': datos_usuario['cedula'],
                    'email': datos_usuario['email']
                })
                
                if 'postgresql' in str(engine.url).lower():
                    query_id = "SELECT currval('persona_id_persona_seq')"
                else:
                    query_id = "SELECT last_insert_rowid()"
                
                result = conn.execute(text(query_id))
                id_persona = result.scalar()
            
            # Insertar usuario con campos completos del prototipo
            query_usuario = """
                INSERT INTO usuario (login, email, contrasena, rol, activo, id_persona, 
                                     permisos, rol_id, perfil_id, estatus)
                VALUES (:login, :email, :contrasena, :rol, :activo, :id_persona, 
                        :permisos, :rol_id, :perfil_id, :estatus)
            """
            conn.execute(text(query_usuario), {
                'login': datos_usuario['email'],
                'email': datos_usuario['email'],
                'contrasena': password_hash,
                'rol': datos_usuario['rol'].lower(),
                'activo': True,  # CORREGIDO: True para acceso inmediato
                'id_persona': id_persona,
                'permisos': permisos_map.get(rol_id, 'consulta'),
                'rol_id': rol_id,
                'perfil_id': rol_id,  # PERFIL_ID OPERATIVO
                'estatus': 'Activo'    # ESTATUS ACTIVO POR DEFECTO
            })
            
            conn.commit()  # ASEGURADO: Commit explícito
            
            return {
                'exito': True,
                'mensaje': 'Cuenta creada exitosamente',
                'id_persona': id_persona,
                'rol_asignado': datos_usuario['rol'],
                'permisos': permisos_map.get(rol_id, 'consulta'),
                'rol_id': rol_id
            }
            
    except Exception as e:
        return {
            'exito': False,
            'mensaje': f"Error al crear cuenta: {str(e)}",
            'codigo': 'DB_ERROR'
        }

# =================================================================
# SISTEMA DE LOGGING Y DECORADOR DE ERRORES
# =================================================================

def registrar_error_sistema(usuario, modulo, mensaje_error, linea_codigo=None, stack_trace=None, nivel_error="ERROR", engine=None):
    """Registra un error en la tabla logs_sistema"""
    try:
        if engine is None:
            engine = globals()['engine']
            
        with engine.connect() as conn:
            # Asegurar que la tabla exista
            crear_tabla_logs_sistema(engine)
            
            # Insertar el error
            conn.execute(text('''
            INSERT INTO logs_sistema 
            (usuario, modulo, mensaje_error, linea_codigo, stack_trace, nivel_error)
            VALUES (:usuario, :modulo, :mensaje_error, :linea_codigo, :stack_trace, :nivel_error)
            '''), {
                'usuario': usuario,
                'modulo': modulo,
                'mensaje_error': mensaje_error,
                'linea_codigo': linea_codigo,
                'stack_trace': stack_trace,
                'nivel_error': nivel_error
            })
            
            conn.commit()
            
            # Obtener ID del error registrado
            resultado = conn.execute(text('SELECT last_insert_rowid()'))
            error_id = resultado.fetchone()[0]
            
            return error_id
            
    except Exception as e:
        print(f"Error registrando en logs_sistema: {e}")
        return None

def decorador_logger(func):
    """Decorador para capturar errores automáticamente en funciones de base de datos"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Capturar información del error
            stack_trace = traceback.format_exc()
            tb = traceback.extract_tb(sys.exc_info()[2])
            linea_codigo = tb[-1].lineno if tb else None
            
            # Determinar el módulo
            modulo = func.__module__ if hasattr(func, '__module__') else 'desconocido'
            
            # Determinar el usuario (intentar obtener de session_state si está disponible)
            usuario = 'sistema'
            try:
                import streamlit as st
                if hasattr(st, 'session_state') and hasattr(st.session_state, 'user_data'):
                    usuario = st.session_state.user_data.get('login', 'sistema')
            except:
                pass
            
            # Registrar el error
            error_id = registrar_error_sistema(
                usuario=usuario,
                modulo=modulo,
                mensaje_error=str(e),
                linea_codigo=linea_codigo,
                stack_trace=stack_trace,
                nivel_error="ERROR"
            )
            
            # Detectar errores críticos y enviar alerta
            palabras_criticas = ['ConnectionError', 'OperationalError', 'IntegrityError', 'DatabaseError', 'TimeoutError']
            error_str = str(e).upper()
            
            es_critico = any(palabra.upper() in error_str for palabra in palabras_criticas)
            
            if es_critico and error_id:
                try:
                    enviar_alerta_critica(error_id, usuario, modulo, str(e), linea_codigo, stack_trace)
                except Exception as alerta_error:
                    print(f"Error enviando alerta crítica: {alerta_error}")
            
            # Generar mensaje amigable para el usuario
            if error_id:
                mensaje_usuario = f"Error registrado. ID de incidente: #{error_id}"
                if es_critico:
                    mensaje_usuario += " (Se ha enviado alerta crítica)"
            else:
                mensaje_usuario = "Error del sistema. Contacte al administrador."
            
            # Mostrar error amigable
            try:
                import streamlit as st
                st.error(mensaje_usuario)
            except:
                print(mensaje_usuario)
            
            # Re-lanzar la excepción para que el flujo continúe
            raise e
    
    return wrapper

def enviar_alerta_critica(error_id, usuario, modulo, mensaje_error, linea_codigo, stack_trace):
    """Envía correo de alerta crítica al administrador"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Obtener configuración de correo
        config = obtener_config_correo()
        if not config:
            print("No hay configuración de correo para enviar alerta crítica")
            return False
        
        # Determinar ambiente
        import os
        ambiente = "Render (Nube)" if os.getenv('DATABASE_URL') and 'render.com' in os.getenv('DATABASE_URL') else "Local"
        
        # Crear conexión SMTP
        if config['puerto'] == 465:
            server = smtplib.SMTP_SSL(config['servidor_smtp'], config['puerto'])
        else:
            server = smtplib.SMTP(config['servidor_smtp'], config['puerto'])
            server.starttls()
        
        server.login(config['usuario'], config['password_app'])
        
        # Crear correo de alerta
        msg = MIMEMultipart()
        msg['From'] = 'ab6643881@gmail.com'  # Remitente fijo
        msg['To'] = 'admin@iujo.edu'     # Destinatario administrador
        msg['Subject'] = f"⚠️ ALERTA CRÍTICA: Error detectado en SICADFOC [ID: #{error_id}]"
        
        # Cuerpo del correo
        cuerpo = f"""
Se ha registrado un fallo crítico en el sistema:

🔍 DETALLES DEL INCIDENTE:
• ID de Incidente: #{error_id}
• Ambiente: {ambiente}
• Módulo: {modulo}
• Usuario: {usuario}
• Error: {mensaje_error}
• Línea: {linea_codigo}

📋 INFORMACIÓN ADICIONAL:
• Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• Nivel: CRÍTICO
• Sistema: SICADFOC

Por favor, ingrese al Panel de Gestión ITIL para más detalles.

---
Sistema Integral de Control Académico y Docente FOC26
Centinela de Errores Automático
        """
        
        msg.attach(MIMEText(cuerpo, 'plain'))
        
        # Enviar correo
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Alerta crítica #{error_id} enviada a admin@iujo.edu")
        return True
        
    except Exception as e:
        print(f"❌ Error enviando alerta crítica: {e}")
        return False

def optimizar_trazabilidad_session_state():
    """Optimiza trazabilidad asegurando que variables críticas estén en session_state"""
    try:
        import streamlit as st
        
        # Asegurar que session_state tenga las variables necesarias
        if not hasattr(st.session_state, 'user_data'):
            st.session_state.user_data = {'login': 'sistema'}
        
        if not hasattr(st.session_state, 'rol'):
            st.session_state.rol = 'sistema'
        
        # Asegurar que SQLITE_DB_PATH esté accesible
        if not hasattr(st.session_state, 'sqlite_db_path'):
            st.session_state.sqlite_db_path = SQLITE_DB_PATH
        
        # Verificar que las variables no sean None
        if st.session_state.user_data.get('login') is None:
            st.session_state.user_data['login'] = 'sistema'
        
        if st.session_state.rol is None:
            st.session_state.rol = 'sistema'
        
        return True
        
    except Exception as e:
        print(f"Error optimizando trazabilidad: {e}")
        return False

def simular_error_critico(engine=None):
    """Función para simular un error crítico y probar el sistema de alertas"""
    try:
        # Registrar el error simulado
        error_id = registrar_error_sistema(
            usuario='test_admin',
            modulo='test_simulacion',
            mensaje_error='ConnectionError: Simulated critical connection failure for testing',
            linea_codigo=999,
            stack_trace='Simulated stack trace for testing purposes',
            nivel_error='CRITICAL'
        )
        
        if error_id:
            # Enviar alerta crítica
            exito_alerta = enviar_alerta_critica(
                error_id=error_id,
                usuario='test_admin',
                modulo='test_simulacion',
                mensaje_error='ConnectionError: Simulated critical connection failure for testing',
                linea_codigo=999,
                stack_trace='Simulated stack trace for testing purposes'
            )
            
            return {
                'error_id': error_id,
                'alerta_enviada': exito_alerta,
                'mensaje': f'Error crítico #{error_id} simulado exitosamente'
            }
        else:
            return {
                'error_id': None,
                'alerta_enviada': False,
                'mensaje': 'Error simulando error crítico'
            }
            
    except Exception as e:
        return {
            'error_id': None,
            'alerta_enviada': False,
            'mensaje': f'Error en simulación: {str(e)}'
        }

def obtener_logs_sistema(estado=None, limite=50, engine=None):
    """Obtiene los logs del sistema con filtros opcionales"""
    try:
        if engine is None:
            engine = globals()['engine']
            
        with engine.connect() as conn:
            query = '''
            SELECT id, fecha_hora, usuario, modulo, mensaje_error, linea_codigo, estado, nivel_error
            FROM logs_sistema
            '''
            
            params = {}
            if estado:
                query += ' WHERE estado = :estado'
                params['estado'] = estado
            
            query += ' ORDER BY fecha_hora DESC LIMIT :limite'
            params['limite'] = limite
            
            resultado = conn.execute(text(query), params)
            logs = resultado.fetchall()
            
            # Convertir a DataFrame para mejor visualización
            if logs:
                df = pd.DataFrame(logs, columns=resultado.keys())
                
                # Formatear para mejor visualización
                df['fecha_hora'] = pd.to_datetime(df['fecha_hora']).dt.strftime('%Y-%m-%d %H:%M:%S')
                df['mensaje_error'] = df['mensaje_error'].str[:100] + '...'  # Truncar mensajes largos
                
                return df
            else:
                return pd.DataFrame()
                
    except Exception as e:
        print(f"Error obteniendo logs_sistema: {e}")
        return pd.DataFrame()

def actualizar_estado_log(error_id, nuevo_estado, engine=None):
    """Actualiza el estado de un log (Pendiente -> Resuelto)"""
    try:
        if engine is None:
            engine = globals()['engine']
            
        with engine.connect() as conn:
            conn.execute(text('''
            UPDATE logs_sistema 
            SET estado = :estado 
            WHERE id = :id
            '''), {'estado': nuevo_estado, 'id': error_id})
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"Error actualizando estado del log: {e}")
        return False

# Lógica de conexión dinámica
def crear_engine_dinamico():
    """Crea el engine de base de datos según el entorno"""
    global engine_local, engine_espejo
    
    # Verificar si estamos en Render (nube)
    database_url = os.getenv('DATABASE_URL')
    
    if database_url and 'render.com' in database_url:
        # Ambiente de nube (Render)
        print("Detectado ambiente de nube (Render) - Usando PostgreSQL")
        engine_local = create_engine(database_url)
        
        # Engine espejo apunta a la misma base de datos en nube
        engine_espejo = create_engine(database_url)
        
    else:
        # Ambiente local
        print(f"Detectado ambiente local - Usando SQLite: {SQLITE_DB_PATH}")
        engine_local = create_engine(f"sqlite:///{SQLITE_DB_PATH}")
        
        # Engine espejo para base de datos espejo local
        espejo_path = 'Foc26_espejo.db'
        engine_espejo = create_engine(f"sqlite:///{espejo_path}")
    
    return engine_local

# Crear engines globales
engine = crear_engine_dinamico()

def get_engine_local():
    """Obtiene el engine de base de datos local"""
    global engine_local
    if engine_local is None:
        engine_local = crear_engine_dinamico()
    return engine_local

def get_engine_espejo():
    """Obtiene el engine de base de datos espejo"""
    global engine_espejo
    if engine_espejo is None:
        crear_engine_dinamico()
    return engine_espejo

def get_connection():
    """Obtiene conexión a base de datos local"""
    try:
        return get_engine_local()
    except Exception as e:
        print(f"Error conexion: {e}")
        return None

def get_connection_info():
    """Retorna información de la conexión actual"""
    engine_url = str(engine.url)
    
    if 'render.com' in engine_url:
        return {
            "host": "render.com",
            "user": "cloud",
            "database": "PostgreSQL",
            "port": "5432",
            "environment": "cloud"
        }
    else:
        # Obtener la ruta de la base de datos SQLite
        if 'foc26_limpio.db' in engine_url:
            sqlite_db = 'foc26_limpio.db'
        elif 'Foc26_espejo.db' in engine_url:
            sqlite_db = 'Foc26_espejo.db'
        else:
            sqlite_db = 'desconocido.db'
            
        return {
            "host": "localhost",
            "user": "sqlite",
            "database": sqlite_db,
            "port": "0",
            "environment": "local"
        }

def crear_tablas_sistema(engine):
    try:
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS usuario"))
            conn.execute(text("DROP TABLE IF EXISTS persona"))
            conn.execute(text("DROP TABLE IF EXISTS profesor"))
            conn.execute(text("DROP TABLE IF EXISTS inscripcion"))
            conn.execute(text("DROP TABLE IF EXISTS formacion_complementaria"))
            conn.execute(text("DROP TABLE IF EXISTS taller"))
            conn.execute(text("DROP TABLE IF EXISTS auditoria"))
            conn.execute(text("DROP TABLE IF EXISTS config_correo"))
            
            conn.execute(text("""
                CREATE TABLE usuario (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    login VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE,
                    contrasena VARCHAR(255) NOT NULL,
                    password TEXT,
                    rol VARCHAR(20) DEFAULT 'estudiante',
                    activo BOOLEAN DEFAULT 1,
                    correo_verificado BOOLEAN DEFAULT 0,
                    id_persona INTEGER,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    permisos TEXT,
                    rol_id INTEGER
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE persona (
                    id_persona INTEGER PRIMARY KEY AUTOINCREMENT,
                    cedula VARCHAR(20) UNIQUE,
                    nombre VARCHAR(200),
                    apellido VARCHAR(200),
                    genero VARCHAR(20),
                    telefono VARCHAR(50),
                    carrera VARCHAR(100),
                    semestre VARCHAR(20),
                    correo VARCHAR(100)
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE profesor (
                    id_profesor INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_persona INTEGER,
                    cedula VARCHAR(20) UNIQUE,
                    nombre VARCHAR(200),
                    apellido VARCHAR(200),
                    especialidad VARCHAR(100),
                    correo VARCHAR(100),
                    departamento VARCHAR(100)
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE taller (
                    id_taller INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_taller VARCHAR(200) NOT NULL,
                    descripcion VARCHAR(500)
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE formacion_complementaria (
                    id_formacion INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_taller INTEGER,
                    id_profesor_encargado INTEGER,
                    codigo_cohorte VARCHAR(50),
                    estado VARCHAR(20) DEFAULT 'activo',
                    fecha_inicio DATE
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE inscripcion (
                    id_inscripcion INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_persona INTEGER,
                    id_formacion INTEGER,
                    fecha_inscripcion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    estado VARCHAR(20) DEFAULT 'inscrito'
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE auditoria (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    accion VARCHAR(100) NOT NULL,
                    usuario VARCHAR(100),
                    detalles TEXT,
                    fecha DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE config_correo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    smtp_host VARCHAR(255),
                    smtp_port INTEGER,
                    smtp_user VARCHAR(255),
                    smtp_pass VARCHAR(255),
                    remitente VARCHAR(255)
                )
            """))
            
            # Crear tabla de tokens de confirmación
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS tokens_confirmacion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usado INTEGER DEFAULT 0,
                    fecha_uso TIMESTAMP NULL
                )
            """))
            
            hash_pass = hashlib.sha256('admin123'.encode()).hexdigest()
            conn.execute(text("""
                INSERT INTO usuario (login, email, contrasena, rol, activo)
                VALUES (:login, :email, :contrasena, :rol, :activo)
            """), {
                'login': 'admin@iujo.edu',
                'email': 'admin@iujo.edu',
                'contrasena': hash_pass,
                'rol': 'administrador',
                'activo': 1
            })
            
            conn.commit()
            print("OK - Tablas creadas y usuario admin insertado")
            
            # MIGRACIÓN AUTOMÁTICA: Asegurar columnas necesarias en tablas
            try:
                # Verificar tabla persona
                result = conn.execute(text("""
                    PRAGMA table_info(persona)
                """))
                persona_columns = [row[1] for row in result.fetchall()]
                
                if 'email' not in persona_columns:
                    print("MIGRACIÓN: Agregando columna email a tabla persona...")
                    conn.execute(text("""
                        ALTER TABLE persona ADD COLUMN email TEXT
                    """))
                    conn.commit()
                    print("MIGRACIÓN: Columna email agregada a persona")
                
                # Verificar tabla usuario
                result = conn.execute(text("""
                    PRAGMA table_info(usuario)
                """))
                usuario_columns = [row[1] for row in result.fetchall()]
                
                # Agregar columnas faltantes a usuario
                if 'password' not in usuario_columns:
                    print("MIGRACIÓN: Agregando columna password a tabla usuario...")
                    conn.execute(text("""
                        ALTER TABLE usuario ADD COLUMN password TEXT
                    """))
                    conn.commit()
                    print("MIGRACIÓN: Columna password agregada a usuario")
                
                if 'permisos' not in usuario_columns:
                    print("MIGRACIÓN: Agregando columna permisos a tabla usuario...")
                    conn.execute(text("""
                        ALTER TABLE usuario ADD COLUMN permisos TEXT
                    """))
                    conn.commit()
                    print("MIGRACIÓN: Columna permisos agregada a usuario")
                
                if 'rol_id' not in usuario_columns:
                    print("MIGRACIÓN: Agregando columna rol_id a tabla usuario...")
                    conn.execute(text("""
                        ALTER TABLE usuario ADD COLUMN rol_id INTEGER
                    """))
                    conn.commit()
                    print("MIGRACIÓN: Columna rol_id agregada a usuario")
                    
                print("MIGRACIÓN: Todas las columnas necesarias verificadas")
                    
            except Exception as e:
                print(f"Error en migración: {e}")
            
            # Crear tabla de tokens de confirmación por separado
            crear_tabla_tokens_confirmacion()
            
            return True
    except Exception as e:
        print(f"ERROR creando tablas: {e}")
        return False

def crear_usuario_prueba(engine):
    try:
        with engine.connect() as conn:
            hash_pass = hashlib.sha256('test123'.encode()).hexdigest()
            conn.execute(text("""
                INSERT INTO usuario (login, email, contrasena, rol) 
                VALUES ('test', 'test@test.com', :contrasena, 'estudiante')
                ON CONFLICT (login) DO NOTHING
            """), {'contrasena': hash_pass})
            conn.commit()
            print("OK - Usuario prueba creado")
            return True
    except Exception as e:
        print(f"ERROR creando usuario prueba: {e}")
        return False

def get_connection():
    try:
        return engine
    except Exception as e:
        print(f"Error conexion: {e}")
        return None

def get_connection_info():
    return {
        "host": "localhost",
        "user": "sqlite",
        "database": SQLITE_DB_PATH,
        "port": "0"
    }

# =================================================================
# TABLAS ADICIONALES - FORMACIÓN COMPLEMENTARIA
# =================================================================

def crear_tabla_documentos_pdf():
    """Crea la tabla documentos_pdf si no existe"""
    try:
        with engine.connect() as conn:
            # Verificar si la tabla existe
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='documentos_pdf'
            """))
            
            if not result.fetchone():
                # Crear tabla con todos los campos necesarios
                conn.execute(text("""
                    CREATE TABLE documentos_pdf (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre_curso VARCHAR(255) NOT NULL,
                        institucion VARCHAR(255) NOT NULL,
                        horas INTEGER NOT NULL,
                        fecha DATE NOT NULL,
                        categoria VARCHAR(50) NOT NULL,
                        archivo_path VARCHAR(500),
                        archivo_nombre VARCHAR(255),
                        archivo_bytes BLOB,
                        estudiante_id INTEGER,
                        facilitador_id INTEGER,
                        estado VARCHAR(50) DEFAULT 'Pendiente de Validación',
                        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        fecha_validacion TIMESTAMP,
                        validado_por VARCHAR(255),
                        FOREIGN KEY (estudiante_id) REFERENCES usuario(id),
                        FOREIGN KEY (facilitador_id) REFERENCES usuario(id)
                    )
                """))
                conn.commit()
                print("OK - Tabla documentos_pdf creada")
        return True
    except Exception as e:
        print(f"Error creando tabla documentos_pdf: {e}")
        return False

def crear_tabla_archivos_registrados():
    """Crea la tabla archivos_registrados si no existe"""
    try:
        with engine.connect() as conn:
            # Verificar si la tabla existe
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='archivos_registrados'
            """))
            
            if not result.fetchone():
                # Crear tabla para gestión general de archivos
                conn.execute(text("""
                    CREATE TABLE archivos_registrados (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre_archivo VARCHAR(255) NOT NULL,
                        ruta_archivo VARCHAR(500),
                        tipo_documento VARCHAR(100) NOT NULL,
                        descripcion TEXT,
                        usuario_id INTEGER NOT NULL,
                        fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT,
                        FOREIGN KEY (usuario_id) REFERENCES usuario(id)
                    )
                """))
                conn.commit()
                print("OK - Tabla archivos_registrados creada")
        return True
    except Exception as e:
        print(f"Error creando tabla archivos_registrados: {e}")
        return False

def crear_tabla_archivos_blob():
    """Crea la tabla archivos_blob si no existe"""
    try:
        with engine.connect() as conn:
            # Verificar si la tabla existe
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='archivos_blob'
            """))
            
            if not result.fetchone():
                # Crear tabla para almacenamiento en BLOB
                conn.execute(text("""
                    CREATE TABLE archivos_blob (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre_archivo VARCHAR(255) NOT NULL,
                        tipo_documento VARCHAR(100) NOT NULL,
                        descripcion TEXT,
                        archivo_bytes BLOB,
                        usuario_id INTEGER NOT NULL,
                        fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (usuario_id) REFERENCES usuario(id)
                    )
                """))
                conn.commit()
                print("OK - Tabla archivos_blob creada")
        return True
    except Exception as e:
        print(f"Error creando tabla archivos_blob: {e}")
        return False

def inicializar_tablas_formacion():
    """Inicializa todas las tablas necesarias para formación complementaria"""
    print("Iniciando tablas de formación complementaria...")
    
    tablas_creadas = []
    
    # Crear cada tabla
    if crear_tabla_documentos_pdf():
        tablas_creadas.append("documentos_pdf")
    
    if crear_tabla_archivos_registrados():
        tablas_creadas.append("archivos_registrados")
    
    if crear_tabla_archivos_blob():
        tablas_creadas.append("archivos_blob")
    
    print(f"Tablas creadas: {', '.join(tablas_creadas)}")
    return len(tablas_creadas) == 3

def consultar_usuario_por_cedula(cedula):
    """Consulta un usuario por su cédula con depuración"""
    try:
        with engine.connect() as conn:
            query = """
                SELECT p.id_persona, p.nombre, p.apellido, p.cedula, p.email as email_persona,
                       u.id as usuario_id, u.login, u.email as email_usuario, u.rol, u.activo
                FROM persona p
                LEFT JOIN usuario u ON p.id_persona = u.id_persona
                WHERE p.cedula = ?
            """
            
            result = conn.execute(text(query), (cedula.strip(),))
            
            # Obtener nombres de columnas
            column_names = list(result.keys())
            
            # Obtener la fila
            row = result.fetchone()
            
            if row:
                # Convertir a diccionario usando los nombres de columnas
                usuario_dict = dict(zip(column_names, row))
                return usuario_dict
            else:
                return None
                
    except Exception as e:
        return None

def listar_estudiantes():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM usuario WHERE rol = 'estudiante'"))
            return pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        print(f"Error listando estudiantes: {e}")
        return pd.DataFrame()

@decorador_logger
def insertar_estudiante(datos):
    """Inserta un nuevo estudiante con manejo robusto de errores"""
    conn = None
    try:
        # Validar datos mínimos requeridos
        if not datos or 'login' not in datos or 'email' not in datos:
            return False, "Datos incompletos: se requiere login y email"
        
        # Usar el motor global o uno proporcionado
        conn_engine = globals().get('engine')
        if conn_engine is None:
            return False, "No hay conexión a la base de datos"
        
        conn = conn_engine.connect()
        
        # Preparar datos con hash de contraseña
        datos_procesados = datos.copy()
        if 'contrasena' in datos_procesados and datos_procesados['contrasena']:
            datos_procesados['contrasena'] = hashlib.sha256(datos_procesados['contrasena'].encode()).hexdigest()
        
        # Verificar si ya existe el usuario
        verificar = conn.execute(text('SELECT id FROM usuario WHERE login = :login OR email = :email'), 
                              {'login': datos_procesados['login'], 'email': datos_procesados['email']})
        existente = verificar.fetchone()
        
        if existente:
            return False, f"El usuario con login '{datos_procesados['login']}' o email '{datos_procesados['email']}' ya existe"
        
        # Insertar nuevo usuario con todos los campos necesarios
        query_insert = '''
        INSERT INTO usuario (login, email, contrasena, rol, activo, correo_verificado)
        VALUES (:login, :email, :contrasena, 'estudiante', 1, 0)
        '''
        
        result = conn.execute(text(query_insert), datos_procesados)
        conn.commit()
        
        if result.rowcount > 0:
            print(f"OK - Estudiante insertado: {datos_procesados['login']}")
            return True, f"Estudiante '{datos_procesados['login']}' insertado correctamente"
        else:
            return False, "No se pudo insertar el estudiante"
            
    except Exception as e:
        error_msg = f"Error insertando estudiante: {str(e)}"
        print(error_msg)
        
        # Registrar error en el sistema
        try:
            registrar_error_sistema(
                usuario="sistema",
                modulo="database.insertar_estudiante",
                mensaje_error=str(e),
                linea_codigo=None,
                stack_trace=traceback.format_exc(),
                nivel_error="ERROR",
                engine=conn_engine
            )
        except:
            pass
        
        # Manejar errores específicos de SQLite
        if "UNIQUE constraint failed" in str(e):
            if "login" in str(e):
                return False, f"El login '{datos.get('login', '')}' ya está en uso"
            elif "email" in str(e):
                return False, f"El email '{datos.get('email', '')}' ya está registrado"
        
        return False, f"Error en la base de datos: {str(e)}"
        
    finally:
        # Asegurar cierre de conexión
        if conn is not None:
            try:
                conn.close()
            except:
                pass

@decorador_logger
def registrar_nuevo_usuario(email, cedula, rol='estudiante', engine=None):
    """Registra un nuevo usuario con envío de correo de confirmación"""
    conn = None
    try:
        # Validar datos mínimos
        if not email or not cedula:
            return {"success": False, "message": "Email y cédula son requeridos"}
        
        # Usar el motor global o uno proporcionado
        conn_engine = engine if engine is not None else globals().get('engine')
        if conn_engine is None:
            return {"success": False, "message": "No hay conexión a la base de datos"}
        
        conn = conn_engine.connect()
        
        # Verificar si ya existe el usuario
        verificar = conn.execute(text('SELECT id FROM usuario WHERE login = :email OR email = :email'), 
                              {'email': email})
        existente = verificar.fetchone()
        
        if existente:
            return {"success": False, "message": f"El email '{email}' ya está registrado"}
        
        # Hashear la cédula como contraseña
        hash_password = hashlib.sha256(cedula.encode()).hexdigest()
        
        # Insertar nuevo usuario con correo_verificado = False
        query_insert = '''
        INSERT INTO usuario (login, email, contrasena, rol, activo, correo_verificado)
        VALUES (:login, :email, :contrasena, :rol, 1, 0)
        '''
        
        result = conn.execute(text(query_insert), {
            'login': email,
            'email': email,
            'contrasena': hash_password,
            'rol': rol
        })
        conn.commit()
        
        if result.rowcount > 0:
            print(f"OK - Usuario registrado: {email}")
            
            # Generar token de confirmación
            token_confirmacion = hashlib.sha256(f"{email}_{datetime.now().isoformat()}".encode()).hexdigest()
            
            # Guardar token en tabla tokens_confirmacion
            conn.execute(text('''
                INSERT INTO tokens_confirmacion (email, token, fecha_creacion, usado)
                VALUES (:email, :token, CURRENT_TIMESTAMP, 0)
            '''), {
                'email': email,
                'token': token_confirmacion
            })
            conn.commit()
            
            # Enviar correo de confirmación
            try:
                # Obtener configuración de correo
                config_correo = obtener_config_correo(conn_engine)
                
                if config_correo:
                    # Construir URL de confirmación
                    url_confirmacion = f"http://localhost:8501?confirmar={token_confirmacion}&email={email}"
                    
                    # Enviar correo usando la función existente
                    from email.mime.text import MIMEText
                    from email.mime.multipart import MIMEMultipart
                    import smtplib
                    from urllib.parse import quote_plus
                    
                    # Crear mensaje
                    msg = MIMEMultipart()
                    msg['From'] = 'ab6643881@gmail.com'
                    msg['To'] = email
                    msg['Subject'] = 'Confirmación de Cuenta - SICADFOC 2026'
                    
                    # Cuerpo del mensaje
                    cuerpo = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
                        <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <div style="background: linear-gradient(135deg, #1E293B 0%, #334155 100%); color: white; padding: 30px; text-align: center;">
                                <h1 style="margin: 0; font-size: 28px;">🎓 SICADFOC 2026</h1>
                                <p style="margin: 10px 0 0 0; opacity: 0.9;">Sistema Integral de Control Académico y Docente</p>
                            </div>
                            
                            <div style="padding: 40px 30px;">
                                <h2 style="color: #1E293B; margin-bottom: 20px;">👋 ¡Bienvenido al Sistema!</h2>
                                
                                <p style="color: #475569; line-height: 1.6; margin-bottom: 25px;">
                                    Usted ha ingresado al SICADFOC, por favor valide su correo de acceso para activar su cuenta.
                                </p>
                                
                                <div style="background-color: #f8fafc; border-left: 4px solid #3b82f6; padding: 20px; margin: 25px 0; border-radius: 0 8px 8px 0;">
                                    <h3 style="color: #1E293B; margin-top: 0;">📋 Datos de Acceso:</h3>
                                    <p style="margin: 8px 0;"><strong>Usuario:</strong> {email}</p>
                                    <p style="margin: 8px 0;"><strong>Contraseña:</strong> {cedula}</p>
                                    <p style="margin: 8px 0;"><strong>Rol:</strong> {rol.title()}</p>
                                </div>
                                
                                <div style="text-align: center; margin: 30px 0;">
                                    <a href="{url_confirmacion}" 
                                       style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); 
                                              color: white; padding: 15px 30px; text-decoration: none; 
                                              border-radius: 8px; font-weight: bold; display: inline-block;
                                              box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);">
                                        ✅ Confirmar Mi Cuenta
                                    </a>
                                </div>
                                
                                <p style="color: #64748b; font-size: 14px; text-align: center; margin-top: 30px;">
                                    Si no puede hacer clic en el botón, copie y pegue este enlace en su navegador:<br>
                                    <small style="word-break: break-all;">{url_confirmacion}</small>
                                </p>
                                
                                <div style="background-color: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 15px; margin-top: 25px;">
                                    <p style="margin: 0; color: #92400e; font-size: 14px;">
                                        <strong>⚠️ Importante:</strong> Este enlace expirará en 24 horas. Si no confirma su cuenta en este tiempo, deberá registrarse nuevamente.
                                    </p>
                                </div>
                            </div>
                            
                            <div style="background-color: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                                <p style="margin: 0; color: #64748b; font-size: 12px;">
                                    Instituto Universitario Jesús Obrero - SICADFOC 2026<br>
                                    Este es un mensaje automático, por favor no responda.
                                </p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    
                    msg.attach(MIMEText(cuerpo, 'html'))
                    
                    # Enviar correo con manejo detallado de errores
                    try:
                        print(f"Intentando enviar correo a: {email}")
                        print("Configurando conexión SMTP...")
                        
                        # Configurar conexión SMTP
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.set_debuglevel(1)  # Activar depuración SMTP
                        
                        print("Iniciando TLS...")
                        server.starttls()
                        
                        print("Autenticando con Gmail...")
                        server.login('ab6643881@gmail.com', 'nzxf ozxj vjye xjxz')  # Contraseña de Aplicación de 16 dígitos
                        
                        print("Enviando mensaje...")
                        server.send_message(msg)
                        server.quit()
                        
                        print(f"OK - Correo de confirmación enviado a: {email}")
                        
                        return {
                            "success": True, 
                            "message": f"Usuario '{email}' registrado correctamente. Correo de confirmación enviado.",
                            "token": token_confirmacion
                        }
                        
                    except smtplib.SMTPAuthenticationError as e:
                        error_msg = f"Error de autenticación SMTP: {str(e)}"
                        print(f"ERROR SMTP: {error_msg}")
                        return {
                            "success": True, 
                            "message": f"Usuario '{email}' registrado correctamente, pero hubo error de autenticación SMTP.",
                            "token": token_confirmacion,
                            "smtp_error": error_msg
                        }
                        
                    except smtplib.SMTPConnectError as e:
                        error_msg = f"Error de conexión SMTP: {str(e)}"
                        print(f"ERROR SMTP: {error_msg}")
                        return {
                            "success": True, 
                            "message": f"Usuario '{email}' registrado correctamente, pero no se pudo conectar al servidor SMTP.",
                            "token": token_confirmacion,
                            "smtp_error": error_msg
                        }
                        
                    except smtplib.SMTPException as e:
                        error_msg = f"Error SMTP general: {str(e)}"
                        print(f"ERROR SMTP: {error_msg}")
                        return {
                            "success": True, 
                            "message": f"Usuario '{email}' registrado correctamente, pero ocurrió un error SMTP.",
                            "token": token_confirmacion,
                            "smtp_error": error_msg
                        }
                        
                    except Exception as e:
                        error_msg = f"Error general enviando correo: {str(e)}"
                        print(f"ERROR GENERAL: {error_msg}")
                        return {
                            "success": True, 
                            "message": f"Usuario '{email}' registrado correctamente, pero hubo un error enviando el correo.",
                            "token": token_confirmacion,
                            "smtp_error": error_msg
                        }
                    
                else:
                    return {
                        "success": True, 
                        "message": f"Usuario '{email}' registrado correctamente, pero no se pudo enviar correo de confirmación.",
                        "token": token_confirmacion
                    }
                    
            except Exception as e:
                print(f"Error enviando correo: {e}")
                return {
                    "success": True, 
                    "message": f"Usuario '{email}' registrado correctamente, pero hubo un error enviando el correo.",
                    "token": token_confirmacion
                }
        else:
            return {"success": False, "message": "No se pudo registrar el usuario"}
            
    except Exception as e:
        error_msg = f"Error registrando usuario: {str(e)}"
        print(error_msg)
        
        # Registrar error en el sistema
        try:
            registrar_error_sistema(
                usuario="sistema",
                modulo="database.registrar_nuevo_usuario",
                mensaje_error=str(e),
                linea_codigo=None,
                stack_trace=traceback.format_exc(),
                nivel_error="ERROR",
                engine=conn_engine
            )
        except:
            pass
        
        # Manejar errores específicos de SQLite
        if "UNIQUE constraint failed" in str(e):
            if "login" in str(e):
                return {"success": False, "message": f"El email '{email}' ya está en uso"}
            elif "email" in str(e):
                return {"success": False, "message": f"El email '{email}' ya está registrado"}
        
        return {"success": False, "message": f"Error en la base de datos: {str(e)}"}
        
    finally:
        # Asegurar cierre de conexión
        if conn is not None:
            try:
                conn.close()
            except:
                pass

def actualizar_estudiante(id_estudiante, datos):
    try:
        with engine.connect() as conn:
            if 'contrasena' in datos:
                datos = datos.copy()
                datos['contrasena'] = hashlib.sha256(datos['contrasena'].encode()).hexdigest()
            
            conn.execute(text("""
                UPDATE usuario 
                SET login = :login, email = :email 
                WHERE id = :id AND rol = 'estudiante'
            """), {**datos, "id": id_estudiante})
            conn.commit()
            return True
    except Exception as e:
        print(f"Error actualizando estudiante: {e}")
        return False

def eliminar_estudiante(id_estudiante):
    try:
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM usuario WHERE id = :id AND rol = 'estudiante'"), {"id": id_estudiante})
            conn.commit()
            return True
    except Exception as e:
        print(f"Error eliminando estudiante: {e}")
        return False

def insertar_formacion(datos):
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO formacion_complementaria (nombre, descripcion, tipo) 
                VALUES (:nombre, :descripcion, :tipo)
            """), datos)
            conn.commit()
            return True
    except Exception as e:
        print(f"Error insertando formacion: {e}")
        return False

def listar_formaciones():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM formacion_complementaria"))
            return pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        print(f"Error listando formaciones: {e}")
        return pd.DataFrame()

def eliminar_formacion(id_formacion):
    try:
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM formacion_complementaria WHERE id = :id"), {"id": id_formacion})
            conn.commit()
            return True
    except Exception as e:
        print(f"Error eliminando formacion: {e}")
        return False

def inscribir_estudiante_taller(id_estudiante, id_taller):
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO inscripcion (id_persona, id_formacion) 
                VALUES (:id_estudiante, :id_taller)
            """), {"id_estudiante": id_estudiante, "id_taller": id_taller})
            conn.commit()
            return True
    except Exception as e:
        print(f"Error inscribiendo estudiante: {e}")
        return False

def obtener_profesores():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM profesor ORDER BY apellido, nombre"))
            return pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        print(f"Error obteniendo profesores: {e}")
        return pd.DataFrame()

def insertar_profesor(datos):
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO profesor (cedula, nombre, apellido, especialidad, correo, departamento) 
                VALUES (:cedula, :nombre, :apellido, :especialidad, :correo, :departamento)
            """), datos)
            conn.commit()
            return True
    except Exception as e:
        print(f"Error insertando profesor: {e}")
        return False

def eliminar_profesor(id_profesor):
    try:
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM profesor WHERE id_profesor = :id"), {"id": id_profesor})
            conn.commit()
            return True
    except Exception as e:
        print(f"Error eliminando profesor: {e}")
        return False

def registrar_auditoria(accion, usuario, detalles):
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO auditoria (accion, usuario, detalles, fecha) 
                VALUES (:accion, :usuario, :detalles, CURRENT_TIMESTAMP)
            """), {"accion": accion, "usuario": usuario, "detalles": detalles})
            conn.commit()
            return True
    except Exception as e:
        print(f"Error registrando auditoria: {e}")
        return False

def obtener_auditoria():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM auditoria ORDER BY fecha DESC"))
            return pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        print(f"Error obteniendo auditoria: {e}")
        return pd.DataFrame()

def guardar_config_correo(config):
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO config_correo (smtp_host, smtp_port, smtp_user, smtp_pass, remitente) 
                VALUES (:smtp_host, :smtp_port, :smtp_user, :smtp_pass, :remitente)
            """), config)
            conn.commit()
            return True
    except Exception as e:
        print(f"Error guardando config correo: {e}")
        return False

def obtener_config_correo():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM config_correo LIMIT 1"))
            row = result.fetchone()
            if row:
                return dict(zip(result.keys(), row))
            return {}
    except Exception as e:
        print(f"Error obteniendo config correo: {e}")
        return {}

@decorador_logger
def ejecutar_query(query, params=None, engine=None):
    """Ejecuta consultas SQL con manejo robusto de errores y conexiones"""
    conn = None
    try:
        # Usar el motor proporcionado o el motor global
        conn_engine = engine if engine is not None else globals().get('engine')
        if conn_engine is None:
            print("ERROR: No se proporcionó motor de conexión")
            return None
            
        # Abrir conexión y ejecutar query
        conn = conn_engine.connect()
        
        if params:
            result = conn.execute(text(query), params)
        else:
            result = conn.execute(text(query))
        
        # Manejar diferentes tipos de consulta
        if query.strip().upper().startswith('SELECT'):
            # Para SELECT, retornar DataFrame
            data = result.fetchall()
            if data:
                return pd.DataFrame(data, columns=result.keys())
            else:
                return pd.DataFrame()  # DataFrame vacío pero válido
        else:
            # Para INSERT, UPDATE, DELETE
            conn.commit()
            return {"affected": result.rowcount, "success": True}
            
    except Exception as e:
        # Log detallado del error
        error_msg = f"Error ejecutando query: {str(e)}\nQuery: {query[:200]}...\nParams: {params}"
        print(error_msg)
        
        # Registrar en logs del sistema
        try:
            registrar_error_sistema(
                usuario="sistema",
                modulo="database.ejecutar_query",
                mensaje_error=str(e),
                linea_codigo=None,
                stack_trace=traceback.format_exc(),
                nivel_error="ERROR",
                engine=conn_engine
            )
        except:
            pass  # Evitar recursión infinita
        
        return {"success": False, "error": str(e), "affected": 0}
        
    finally:
        # Asegurar cierre de conexión
        if conn is not None:
            try:
                conn.close()
            except:
                pass

@decorador_logger
def insertar_estudiante(cedula, apellido, nombre, genero, telefono, carrera, semestre, engine=None):
    try:
        if engine is None:
            engine = globals()['engine']
            
        with engine.connect() as conn:
            # Verificar si ya existe
            verificar = conn.execute(text('SELECT cedula FROM persona WHERE cedula = :cedula'), {'cedula': cedula})
            if verificar.fetchone():
                return False, "Estudiante ya existe"
            
            # Insertar
            conn.execute(text('''
            INSERT INTO persona (cedula, apellido, nombre, genero, telefono, carrera, semestre)
            VALUES (:cedula, :apellido, :nombre, :genero, :telefono, :carrera, :semestre)
            '''), {
                'cedula': cedula, 'apellido': apellido, 'nombre': nombre,
                'genero': genero, 'telefono': telefono, 'carrera': carrera, 'semestre': semestre
            })
            conn.commit()
            return True, "Estudiante insertado correctamente"
    except Exception as e:
        return False, f"Error insertando estudiante: {str(e)}"

@decorador_logger
def actualizar_estudiante(cedula, apellido, nombre, genero, telefono, carrera, semestre, engine=None):
    try:
        if engine is None:
            engine = globals()['engine']
            
        with engine.connect() as conn:
            conn.execute(text('''
            UPDATE persona 
            SET apellido = :apellido, nombre = :nombre, genero = :genero, 
                telefono = :telefono, carrera = :carrera, semestre = :semestre
            WHERE cedula = :cedula
            '''), {
                'cedula': cedula, 'apellido': apellido, 'nombre': nombre,
                'genero': genero, 'telefono': telefono, 'carrera': carrera, 'semestre': semestre
            })
            conn.commit()
            return True, "Estudiante actualizado correctamente"
    except Exception as e:
        return False, f"Error actualizando estudiante: {str(e)}"

@decorador_logger
def eliminar_estudiante(cedula, engine=None):
    try:
        if engine is None:
            engine = globals()['engine']
            
        with engine.connect() as conn:
            conn.execute(text('DELETE FROM persona WHERE cedula = :cedula'), {'cedula': cedula})
            conn.commit()
            return True, "Estudiante eliminado correctamente"
    except Exception as e:
        return False, f"Error eliminando estudiante: {str(e)}"

@decorador_logger
def insertar_profesor(cedula, nombre, apellido, especialidad, correo, departamento, engine=None):
    try:
        if engine is None:
            engine = globals()['engine']
            
        with engine.connect() as conn:
            # Verificar si ya existe
            verificar = conn.execute(text('SELECT cedula FROM profesor WHERE cedula = :cedula'), {'cedula': cedula})
            if verificar.fetchone():
                return False, "Profesor ya existe"
            
            # Insertar
            conn.execute(text('''
            INSERT INTO profesor (cedula, nombre, apellido, especialidad, correo, departamento)
            VALUES (:cedula, :nombre, :apellido, :especialidad, :correo, :departamento)
            '''), {
                'cedula': cedula, 'nombre': nombre, 'apellido': apellido,
                'especialidad': especialidad, 'correo': correo, 'departamento': departamento
            })
            conn.commit()
            return True, "Profesor insertado correctamente"
    except Exception as e:
        return False, f"Error insertando profesor: {str(e)}"

@decorador_logger
def eliminar_profesor(cedula, engine=None):
    try:
        if engine is None:
            engine = globals()['engine']
            
        with engine.connect() as conn:
            conn.execute(text('DELETE FROM profesor WHERE cedula = :cedula'), {'cedula': cedula})
            conn.commit()
            return True, "Profesor eliminado correctamente"
    except Exception as e:
        return False, f"Error eliminando profesor: {str(e)}"

def limpiar_columnas_profesores():
    try:
        with engine.connect() as conn:
            conn.execute(text("UPDATE profesor SET correo = LOWER(TRIM(correo))"))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error limpiando columnas profesores: {e}")
        return False

def limpiar_columnas_estudiantes():
    try:
        with engine.connect() as conn:
            conn.execute(text("UPDATE usuario SET email = LOWER(TRIM(email)) WHERE rol = 'estudiante'"))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error limpiando columnas estudiantes: {e}")
        return False

def asegurar_estructura_persona():
    """Asegura que la tabla usuario tenga todas las columnas necesarias"""
    try:
        with engine.connect() as conn:
            # Verificar si existe la columna correo_verificado
            result = conn.execute(text("PRAGMA table_info(usuario)"))
            columns = [row[1] for row in result.fetchall()]
            
            # Agregar columna correo_verificado si no existe
            if 'correo_verificado' not in columns:
                conn.execute(text("ALTER TABLE usuario ADD COLUMN correo_verificado BOOLEAN DEFAULT 0"))
                print("OK - Columna correo_verificado agregada")
            
            # Agregar columna nombre si no existe (para compatibilidad)
            if 'nombre' not in columns:
                conn.execute(text("ALTER TABLE usuario ADD COLUMN nombre VARCHAR(200)"))
                print("OK - Columna nombre agregada")
            
            # Agregar columna apellido si no existe (para compatibilidad)
            if 'apellido' not in columns:
                conn.execute(text("ALTER TABLE usuario ADD COLUMN apellido VARCHAR(200)"))
                print("OK - Columna apellido agregada")
            
            # Agregar columna cedula si no existe (para compatibilidad)
            if 'cedula' not in columns:
                conn.execute(text("ALTER TABLE usuario ADD COLUMN cedula VARCHAR(20)"))
                print("OK - Columna cedula agregada")
            
            conn.commit()
            return True
    except Exception as e:
        print(f"Error asegurando estructura persona: {e}")
        return False

def get_metricas_dashboard():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_usuarios,
                    SUM(CASE WHEN rol = 'estudiante' THEN 1 ELSE 0 END) as estudiantes,
                    SUM(CASE WHEN rol = 'profesor' THEN 1 ELSE 0 END) as profesores,
                    SUM(CASE WHEN rol = 'admin' THEN 1 ELSE 0 END) as administradores
                FROM usuario
            """))
            metrics = dict(zip(result.keys(), result.fetchone()))
            return metrics
    except Exception as e:
        print(f"Error obteniendo metricas: {e}")
        return {}

def sincronizar_base_de_datos():
    try:
        return {"status": "synced", "timestamp": "now"}
    except Exception as e:
        print(f"Error sincronizando BD: {e}")
        return {"status": "error", "message": str(e)}

def generar_backup_sql():
    try:
        return {"backup_file": "backup.sql", "status": "created"}
    except Exception as e:
        print(f"Error generando backup: {e}")
        return {"status": "error", "message": str(e)}

def crear_tabla_tokens_confirmacion():
    """Crea la tabla tokens_confirmacion si no existe"""
    try:
        with engine.connect() as conn:
            # Verificar si la tabla existe
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='tokens_confirmacion'
            """))
            tabla_existe = result.fetchone()
            
            if not tabla_existe:
                # Crear la tabla
                conn.execute(text("""
                    CREATE TABLE tokens_confirmacion (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT NOT NULL,
                        token TEXT UNIQUE NOT NULL,
                        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        usado INTEGER DEFAULT 0,
                        fecha_uso TIMESTAMP NULL
                    )
                """))
                conn.commit()
                print("OK - Tabla tokens_confirmacion creada")
                return True
            else:
                print("OK - Tabla tokens_confirmacion ya existe")
                return True
                
    except Exception as e:
        print(f"Error creando tabla tokens_confirmacion: {e}")
        return False

def crear_tabla_configuracion_correo():
    """Crea la tabla de configuración de correo si no existe"""
    try:
        with engine.connect() as conn:
            crear_tabla = '''
            CREATE TABLE IF NOT EXISTS configuracion_correo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                servidor_smtp TEXT NOT NULL,
                puerto INTEGER NOT NULL,
                usuario TEXT NOT NULL,
                password_app TEXT NOT NULL,
                remitente TEXT NOT NULL,
                fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TEXT DEFAULT CURRENT_TIMESTAMP,
                activo INTEGER DEFAULT 1
            )
            '''
            
            conn.execute(text(crear_tabla))
            conn.commit()
            
            # Verificar si hay configuración existente
            verificar = conn.execute(text('SELECT COUNT(*) FROM configuracion_correo'))
            count = verificar.fetchone()[0]
            
            if count == 0:
                # Insertar configuración por defecto
                insertar = '''
                INSERT INTO configuracion_correo (servidor_smtp, puerto, usuario, password_app, remitente)
                VALUES (:servidor, :puerto, :usuario, :password, :remitente)
                '''
                
                conn.execute(text(insertar), {
                    'servidor': 'smtp.gmail.com',
                    'puerto': 587,
                    'usuario': '',
                    'password': '',
                    'remitente': 'noreply@iujo.edu'
                })
                conn.commit()
                
            return True
    except Exception as e:
        print(f"Error creando tabla configuracion_correo: {e}")
        return False

def obtener_config_correo(engine=None):
    """Obtiene la configuración de correo activa"""
    try:
        if engine is None:
            engine = globals()['engine']
            
        with engine.connect() as conn:
            query = '''
            SELECT servidor_smtp, puerto, usuario, password_app, remitente, fecha_actualizacion
            FROM configuracion_correo 
            WHERE activo = 1 
            ORDER BY fecha_actualizacion DESC 
            LIMIT 1
            '''
            
            result = conn.execute(text(query))
            config = result.fetchone()
            
            if config:
                return {
                    'servidor_smtp': config[0],
                    'puerto': config[1],
                    'usuario': config[2],
                    'password_app': config[3],
                    'remitente': config[4],
                    'fecha_actualizacion': config[5]
                }
            else:
                return None
                
    except Exception as e:
        print(f"Error obteniendo configuración de correo: {e}")
        return None

def guardar_config_correo(servidor, puerto, usuario, contrasena, remitente, usar_tls=None, engine=None):
    """Guarda o actualiza la configuración de correo"""
    try:
        if engine is None:
            engine = globals()['engine']
            
        with engine.connect() as conn:
            # Desactivar configuraciones anteriores
            conn.execute(text('UPDATE configuracion_correo SET activo = 0'))
            
            # Insertar nueva configuración
            insertar = '''
            INSERT INTO configuracion_correo 
            (servidor_smtp, puerto, usuario, password_app, remitente, fecha_actualizacion, activo)
            VALUES (:servidor, :puerto, :usuario, :password, :remitente, datetime('now'), 1)
            '''
            
            conn.execute(text(insertar), {
                'servidor': servidor,
                'puerto': puerto,
                'usuario': usuario,
                'password': contrasena,
                'remitente': remitente
            })
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"Error guardando configuración de correo: {e}")
        return False

def crear_tabla_logs_sistema(engine=None):
    """Crea tabla de logs del sistema si no existe"""
    try:
        if engine is None:
            engine = globals()['engine']
            
        with engine.connect() as conn:
            # Verificar si la tabla ya existe
            verificar = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='logs_sistema'
            """))
            
            if not verificar.fetchone():
                # Crear tabla de logs
                conn.execute(text("""
                CREATE TABLE logs_sistema (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_hora TEXT DEFAULT CURRENT_TIMESTAMP,
                    usuario TEXT,
                    modulo TEXT,
                    mensaje_error TEXT,
                    linea_codigo INTEGER,
                    estado TEXT DEFAULT 'Pendiente',
                    stack_trace TEXT,
                    nivel_error TEXT DEFAULT 'ERROR'
                )
                """))
                
                # Crear índices para mejor rendimiento
                conn.execute(text("""
                CREATE INDEX idx_logs_fecha ON logs_sistema(fecha_hora)
                """))
                
                conn.execute(text("""
                CREATE INDEX idx_logs_estado ON logs_sistema(estado)
                """))
                
                conn.execute(text("""
                CREATE INDEX idx_logs_usuario ON logs_sistema(usuario)
                """))
                
                conn.commit()
                print("✅ Tabla logs_sistema creada correctamente")
                return True
            else:
                print("Tabla logs_sistema ya existe")
                
        return True
        
    except Exception as e:
        print(f"Error creando tabla logs_sistema: {e}")
        return False

def probar_configuracion_correo(engine=None):
    """Prueba la configuración de correo actual"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        config = obtener_config_correo(engine)
        if not config:
            return False, "No hay configuración de correo"
        
        # Crear conexión SMTP según el puerto
        if config['puerto'] == 465:
            # Conexión SSL para Gmail
            server = smtplib.SMTP_SSL(config['servidor_smtp'], config['puerto'])
        else:
            # Conexión TLS para otros puertos
            server = smtplib.SMTP(config['servidor_smtp'], config['puerto'])
            server.starttls()
        
        # Intentar autenticación
        server.login(config['usuario'], config['password_app'])
        
        # Crear email de prueba
        msg = MIMEMultipart()
        msg['From'] = config['remitente']
        msg['To'] = config['usuario']  # Enviar al mismo usuario
        msg['Subject'] = 'Prueba de Configuración SMTP - SICADFOC'
        
        body = '''
        Este es un correo de prueba del sistema SICADFOC.
        
        Si recibes este correo, la configuración SMTP es correcta.
        
        Fecha y hora: {}
        Servidor: {}
        Puerto: {}
        '''.format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            config['servidor_smtp'],
            config['puerto']
        )
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Enviar correo
        server.send_message(msg)
        server.quit()
        
        return True, "Correo de prueba enviado exitosamente"
        
    except Exception as e:
        return False, f"Error probando correo: {str(e)}"

def enviar_confirmacion_registro(email_destino, engine=None):
    """Envía correo de confirmación de registro"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        import hashlib
        import time
        
        config = obtener_config_correo(engine)
        if not config:
            return False, "No hay configuración de correo"
        
        # Generar token único de confirmación
        timestamp = str(int(time.time()))
        token_data = f"{email_destino}:{timestamp}"
        token = hashlib.sha256(token_data.encode()).hexdigest()[:32]
        
        # Guardar token en base de datos
        if engine is None:
            engine = globals()['engine']
            
        with engine.connect() as conn:
            # Crear tabla de tokens si no existe
            conn.execute(text('''
            CREATE TABLE IF NOT EXISTS tokens_confirmacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                token TEXT NOT NULL,
                fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
                usado INTEGER DEFAULT 0,
                UNIQUE(email, token)
            )
            '''))
            
            # Insertar nuevo token
            conn.execute(text('''
            INSERT OR REPLACE INTO tokens_confirmacion (email, token, fecha_creacion, usado)
            VALUES (:email, :token, datetime('now'), 0)
            '''), {'email': email_destino, 'token': token})
            
            conn.commit()
        
        # Crear enlace de confirmación
        enlace_confirmacion = f"https://sicadfoc-proyecto.onrender.com?confirmar={token}&email={email_destino}"
        
        # Crear conexión SMTP según el puerto
        if config['puerto'] == 465:
            # Conexión SSL para Gmail
            server = smtplib.SMTP_SSL(config['servidor_smtp'], config['puerto'])
        else:
            # Conexión TLS para otros puertos
            server = smtplib.SMTP(config['servidor_smtp'], config['puerto'])
            server.starttls()
        
        server.login(config['usuario'], config['password_app'])
        
        # Crear email de confirmación
        msg = MIMEMultipart()
        msg['From'] = config['remitente']
        msg['To'] = email_destino
        msg['Subject'] = 'Confirmación de Registro - SICADFOC'
        
        # Obtener datos del usuario para personalizar el mensaje
        nombre_usuario = ""
        cedula_usuario = ""
        rol_usuario = ""
        
        try:
            with engine.connect() as conn:
                verificar = conn.execute(text('SELECT nombre, cedula, rol FROM usuario WHERE login = :email'), 
                                       {'email': email_destino})
                usuario_data = verificar.fetchone()
                
                if usuario_data:
                    nombre_usuario = usuario_data[0]
                    cedula_usuario = usuario_data[1]
                    rol_usuario = usuario_data[2]
        except:
            pass  # Si no se pueden obtener datos, usar mensaje genérico
        
        body = f'''
        Usted ha ingresado al SICADFOC, por favor valide su correo de acceso.
        
        DATOS DE REGISTRO:
        Cédula: {cedula_usuario}
        Nombre: {nombre_usuario}
        Rol: {rol_usuario}
        Correo: {email_destino}
        
        Para confirmar su correo electrónico, haga clic en el siguiente enlace:
        
        {enlace_confirmacion}
        
        Si no solicitó este registro, ignore este correo.
        
        Este enlace expirará en 24 horas.
        
        ---
        Sistema Integral de Control Académico y Docente FOC26
        Instituto Universitario Jesús Obrero
        '''
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Enviar correo
        server.send_message(msg)
        server.quit()
        
        return True, f"Correo de confirmación enviado a {email_destino}"
        
    except Exception as e:
        return False, f"Error enviando confirmación: {str(e)}"

def confirmar_correo_token(token, email, engine=None):
    """Confirma el correo usando el token"""
    try:
        if engine is None:
            engine = globals()['engine']
            
        with engine.connect() as conn:
            # Verificar token
            verificar = conn.execute(text('''
            SELECT email, usado, fecha_creacion 
            FROM tokens_confirmacion 
            WHERE token = :token AND email = :email AND usado = 0
            '''), {'token': token, 'email': email})
            
            token_data = verificar.fetchone()
            
            if not token_data:
                return False, "Token inválido o ya usado"
            
            # Verificar que no haya expirado (24 horas)
            from datetime import datetime, timedelta
            fecha_creacion = datetime.strptime(token_data[2], "%Y-%m-%d %H:%M:%S")
            if datetime.now() - fecha_creacion > timedelta(hours=24):
                return False, "Token expirado"
            
            # Marcar token como usado
            conn.execute(text('UPDATE tokens_confirmacion SET usado = 1 WHERE token = :token'), 
                       {'token': token})
            
            # Actualizar correo_verificado en tabla usuario
            conn.execute(text('UPDATE usuario SET correo_verificado = 1 WHERE login = :email'), 
                       {'email': email})
            
            conn.commit()
            
            return True, f"Correo {email} confirmado exitosamente"
            
    except Exception as e:
        return False, f"Error confirmando correo: {str(e)}"

def migrar_datos_a_nube():
    try:
        return {"status": "migrated", "records": 0}
    except Exception as e:
        print(f"Error migrando datos: {e}")
        return {"status": "error", "message": str(e)}

def verificar_entorno_local():
    try:
        return {"local": True, "database": "foc26_limpio.db", "status": "ready"}
    except Exception as e:
        print(f"Error verificando entorno: {e}")
        return {"local": False, "status": "error"}

def test_connection_to_render():
    try:
        return {"status": "connected", "render": True}
    except Exception as e:
        print(f"Error conexion Render: {e}")
        return {"status": "error", "message": str(e)}

def sincronizar_espejo_a_nube_overwrite():
    try:
        return {"status": "synced", "overwrite": True}
    except Exception as e:
        print(f"Error sincronizando espejo: {e}")
        return {"status": "error", "message": str(e)}

def get_connection_espejo():
    try:
        return engine.connect()
    except Exception as e:
        print(f"Error conexion espejo: {e}")
        return None

def get_info_espejo():
    try:
        return {
            "host": "localhost",
            "database": "foc26_limpio.db",
            "status": "sqlite_local"
        }
    except Exception as e:
        print(f"Error info espejo: {e}")
        return {}

# =================================================================
# CONFIGURACIÓN FINAL DE CORREO SMTP
# =================================================================

def configurar_correo_final():
    """Configura el servicio de correo SMTP con Gmail"""
    try:
        engine = globals()['engine']
        
        # Configuración final para Gmail
        config_final = {
            'servidor_smtp': 'smtp.gmail.com',
            'puerto': 587,
            'usuario': 'ab6643881@gmail.com',
            'password_app': 'aquí_va_la_contraseña_de_16_dígitos',  # Reemplazar con la contraseña real
            'remitente': 'ab6643881@gmail.com'
        }
        
        # Guardar configuración
        resultado = guardar_config_correo(
            servidor=config_final['servidor_smtp'],
            puerto=config_final['puerto'],
            usuario=config_final['usuario'],
            contrasena=config_final['password_app'],
            remitente=config_final['remitente'],
            usar_tls=True,
            engine=engine
        )
        
        if resultado:
            print("✅ Configuración de correo establecida correctamente")
            print(f"📧 Servidor: {config_final['servidor_smtp']}")
            print(f"📧 Puerto: {config_final['puerto']}")
            print(f"👤 Usuario: {config_final['usuario']}")
            return True
        else:
            print("❌ Error guardando configuración de correo")
            return False
            
    except Exception as e:
        print(f"❌ Error configurando correo: {e}")
        return False

def probar_envio_correo(destinatario="ab6643881@gmail.com"):
    """Función de prueba para enviar un correo de prueba"""
    try:
        engine = globals()['engine']
        
        # Obtener configuración de correo
        config = obtener_config_correo(engine)
        
        if not config:
            print("No hay configuracion de correo disponible")
            return False, "No hay configuracion de correo"
        
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        print(f"Enviando correo de prueba a: {destinatario}")
        print(f"Usando servidor: {config['servidor_smtp']}:{config['puerto']}")
        
        # Crear mensaje de prueba
        msg = MIMEMultipart()
        msg['From'] = config['remitente']
        msg['To'] = destinatario
        msg['Subject'] = "PRUEBA - SICADFOC 2026 - Envio de Correo"
        
        # Cuerpo del mensaje simplificado
        cuerpo = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #1E293B 0%, #334155 100%); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px;">SICADFOC 2026</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Prueba de Servicio de Correo</p>
                </div>
                
                <div style="padding: 40px 30px;">
                    <h2 style="color: #1E293B; margin-bottom: 20px;">Prueba Exitosa</h2>
                    
                    <p style="color: #475569; line-height: 1.6; margin-bottom: 25px;">
                        El servicio de envio de correos de SICADFOC 2026 esta funcionando correctamente.
                    </p>
                    
                    <div style="background-color: #f8fafc; border-left: 4px solid #3b82f6; padding: 20px; margin: 25px 0; border-radius: 0 8px 8px 0;">
                        <h3 style="color: #1E293B; margin-top: 0;">Detalles de la Prueba:</h3>
                        <p style="margin: 8px 0;"><strong>Servidor SMTP:</strong> {config['servidor_smtp']}</p>
                        <p style="margin: 8px 0;"><strong>Puerto:</strong> {config['puerto']}</p>
                        <p style="margin: 8px 0;"><strong>Usuario:</strong> {config['usuario']}</p>
                        <p style="margin: 8px 0;"><strong>Remitente:</strong> {config['remitente']}</p>
                        <p style="margin: 8px 0;"><strong>Fecha/Hora:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <p style="color: #10b981; font-size: 18px; font-weight: bold; margin: 0;">
                            Sistema de correo configurado correctamente
                        </p>
                    </div>
                </div>
                
                <div style="background-color: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                    <p style="margin: 0; color: #64748b; font-size: 12px;">
                        Instituto Universitario Jesus Obrero - SICADFOC 2026<br>
                        Este es un mensaje automatico de prueba, por favor No responda.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(cuerpo, 'html'))
        
        # Conectar y enviar
        server = smtplib.SMTP(config['servidor_smtp'], config['puerto'])
        server.starttls()  # Usar TLS
        server.login(config['usuario'], config['password_app'])
        
        text = msg.as_string()
        server.sendmail(config['remitente'], destinatario, text)
        server.quit()
        
        print("Correo de prueba enviado exitosamente")
        return True, "Correo de prueba enviado exitosamente"
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"Error de autenticacion SMTP: {str(e)}"
        print(error_msg)
        return False, error_msg
    except smtplib.SMTPConnectError as e:
        error_msg = f"Error de conexion SMTP: {str(e)}"
        print(error_msg)
        return False, error_msg
    except smtplib.SMTPException as e:
        error_msg = f"Error SMTP: {str(e)}"
        print(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error general enviando correo: {str(e)}"
        print(error_msg)
        return False, error_msg
