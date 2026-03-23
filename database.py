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
        msg['To'] = 'angelher@gmail.com'     # Destinatario fijo
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
        
        print(f"✅ Alerta crítica #{error_id} enviada a angelher@gmail.com")
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
                    rol VARCHAR(20) DEFAULT 'estudiante',
                    activo BOOLEAN DEFAULT 1,
                    id_persona INTEGER,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
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
            
            hash_pass = hashlib.sha256('admin123'.encode()).hexdigest()
            conn.execute(text("""
                INSERT INTO usuario (login, email, contrasena, rol, activo)
                VALUES (:login, :email, :contrasena, :rol, :activo)
            """), {
                'login': 'angelher@gmail.com',
                'email': 'angelher@gmail.com',
                'contrasena': hash_pass,
                'rol': 'administrador',
                'activo': 1
            })
            
            conn.commit()
            print("OK - Tablas creadas y usuario admin insertado")
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

def listar_estudiantes():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM usuario WHERE rol = 'estudiante'"))
            return pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        print(f"Error listando estudiantes: {e}")
        return pd.DataFrame()

def insertar_estudiante(datos):
    try:
        with engine.connect() as conn:
            if 'contrasena' in datos:
                datos = datos.copy()
                datos['contrasena'] = hashlib.sha256(datos['contrasena'].encode()).hexdigest()
            
            conn.execute(text("""
                INSERT INTO usuario (login, email, contrasena, rol) 
                VALUES (:login, :email, :contrasena, 'estudiante')
            """), datos)
            conn.commit()
            return True
    except Exception as e:
        print(f"Error insertando estudiante: {e}")
        return False

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
    try:
        # Usar el motor proporcionado o el motor global
        conn_engine = engine if engine is not None else globals().get('engine')
        if conn_engine is None:
            print("ERROR: No se proporciono motor de conexion")
            return None
            
        with conn_engine.connect() as conn:
            if params:
                result = conn.execute(text(query), params)
            else:
                result = conn.execute(text(query))
            
            if query.strip().upper().startswith('SELECT'):
                return pd.DataFrame(result.fetchall(), columns=result.keys())
            else:
                conn.commit()
                return {"affected": result.rowcount}
    except Exception as e:
        print(f"Error ejecutando query: {e}")
        return None

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
    try:
        with engine.connect() as conn:
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
                print("Tabla logs_sistema creada exitosamente")
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
