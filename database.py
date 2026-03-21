import streamlit as st
import pandas as pd
import os
import unicodedata
from sqlalchemy import create_engine, text

# 1. FUNCIÓN PARA EL GABINETE LOCAL (TU PC)
def get_connection_local():
    """
    Conecta al PostgreSQL instalado en tu máquina usando variables de entorno.
    """
    try:
        # Configuración para tu base de datos local FOC26 usando variables de entorno
        # Prioridad: 1) os.environ, 2) valor por defecto
        db_host = os.environ.get("DB_HOST", "localhost")
        db_port = os.environ.get("DB_PORT", "5432")
        db_name = os.environ.get("DB_NAME", "FOC26")
        db_user = os.environ.get("DB_USER", "postgres")
        db_password = os.environ.get("DB_PASSWORD", "Beba36*ad514xa")
        
        url_local = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(url_local)
        return engine
    except Exception as e:
        st.error(f"Error al crear el motor local: {e}")
        return None

# 2. FUNCIÓN PARA EL GABINETE RENDER (LA NUBE)
def get_connection_render():
    """
    Conecta al PostgreSQL de Render usando st.secrets o variables de entorno.
    Prioridad: 1) st.secrets, 2) os.environ, 3) error
    """
    try:
        # Opción 1: Usar st.secrets (recomendado para Render)
        if "connections" in st.secrets and "postgresql" in st.secrets["connections"]:
            url_nube = st.secrets["connections"]["postgresql"]["url"]
            # Forzamos modo SSL para Render si no está en la URL
            if "sslmode" not in url_nube:
                separator = "&" if "?" in url_nube else "?"
                url_nube += f"{separator}sslmode=require"
            engine = create_engine(url_nube)
            return engine
        
        # Opción 2: Usar variables de entorno (fallback)
        elif os.environ.get("RENDER_DB_URL"):
            url_nube = os.environ.get("RENDER_DB_URL")
            # Forzamos modo SSL para Render si no está en la URL
            if "sslmode" not in url_nube:
                separator = "&" if "?" in url_nube else "?"
                url_nube += f"{separator}sslmode=require"
            engine = create_engine(url_nube)
            return engine
        
        # Opción 3: Usar variables de entorno individuales
        elif all([os.environ.get("RENDER_DB_HOST"), os.environ.get("RENDER_DB_NAME"), 
                 os.environ.get("RENDER_DB_USER"), os.environ.get("RENDER_DB_PASSWORD")]):
            db_host = os.environ.get("RENDER_DB_HOST")
            db_port = os.environ.get("RENDER_DB_PORT", "5432")
            db_name = os.environ.get("RENDER_DB_NAME")
            db_user = os.environ.get("RENDER_DB_USER")
            db_password = os.environ.get("RENDER_DB_PASSWORD")
            
            url_nube = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            # Forzamos modo SSL para Render
            if "sslmode" not in url_nube:
                separator = "&" if "?" in url_nube else "?"
                url_nube += f"{separator}sslmode=require"
            engine = create_engine(url_nube)
            return engine
        
        else:
            return "No se encontró configuración de base de datos en st.secrets ni variables de entorno"
            
    except Exception as e:
        return f"Error al conectar a Render: {str(e)}"

# 3. FUNCIÓN DE CONSULTA CENTRALIZADA (SQLAlchemy)
def ejecutar_query(query, params=None, engine=None):
    """
    Ejecuta una consulta SQL y devuelve los resultados.
    Para SELECT devuelve una lista de diccionarios.
    Para INSERT/UPDATE/DELETE devuelve True si fue exitoso.
    """
    if engine is None:
        return None

    try:
        with engine.connect() as conn:
            # Si es una consulta de lectura (SELECT)
            if query.strip().upper().startswith("SELECT"):
                # Se usa text() por seguridad y compatibilidad con Pandas
                df = pd.read_sql(text(query), conn, params=params)
                return df.to_dict('records')

            # Si es una consulta de escritura (INSERT, UPDATE, DELETE)
            else:
                conn.execute(text(query), params)
                conn.commit()
                return True
    except Exception as e:
        st.error(f"Error en ejecución de SQL: {e}")
        return None


def _normalizar_texto(s):
    """Normaliza texto: minúsculas, sin acentos, sin espacios extra."""
    if pd.isna(s):
        return ""
    t = str(s).strip().lower()
    t = unicodedata.normalize('NFD', t)
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return t


def limpiar_columnas_estudiantes(df):
    """
    Limpia y mapea las columnas del DataFrame de estudiantes (Excel/CSV).
    Campos requeridos: Cedula, Apellido, Nombre, Genero, Telefono, Carrera, Semestre.
    No falla por mayúsculas o acentos en los nombres de columnas.

    Returns:
        tuple: (df_limpio, mapeo) si éxito, o (None, mapeo_parcial) si faltan columnas.
        df_limpio tiene: cedula, apellido, nombre, genero, telefono, carrera, semestre.
    """
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()
    columnas_estandar = ['cedula', 'apellido', 'nombre', 'genero', 'telefono', 'carrera', 'semestre']
    variantes = {
        'cedula': ['cedula', 'cédula', 'documento', 'ci', 'id', 'identificacion'],
        'apellido': ['apellido', 'apellidos', 'last_name', 'segundo_apellido'],
        'nombre': ['nombre', 'nombres', 'primer_nombre', 'first_name'],
        'genero': ['genero', 'género', 'sexo', 'gender'],
        'telefono': ['telefono', 'teléfono', 'tel', 'phone', 'celular', 'movil'],
        'carrera': ['carrera', 'programa', 'especialidad', 'major'],
        'semestre': ['semestre', 'nivel', 'año', 'ano', 'year']
    }

    mapeo = {}
    col_normalizadas = {_normalizar_texto(c): c for c in df.columns}

    for estandar in columnas_estandar:
        encontrado = False
        for variante in variantes.get(estandar, [estandar]):
            n = _normalizar_texto(variante)
            if n in col_normalizadas:
                mapeo[estandar] = col_normalizadas[n]
                encontrado = True
                break
        if not encontrado:
            mapeo[estandar] = None

    if any(v is None for v in mapeo.values()):
        return None, mapeo

    def _str_clean(serie):
        return serie.fillna('').astype(str).str.strip().replace('nan', '')

    df_limpio = pd.DataFrame({
        'cedula': _str_clean(df[mapeo['cedula']]),
        'apellido': _str_clean(df[mapeo['apellido']]).str.upper(),
        'nombre': _str_clean(df[mapeo['nombre']]).str.upper(),
        'genero': _str_clean(df[mapeo['genero']]).str.upper(),
        'telefono': _str_clean(df[mapeo['telefono']]),
        'carrera': _str_clean(df[mapeo['carrera']]).str.upper(),
        'semestre': _str_clean(df[mapeo['semestre']])
    })
    return df_limpio, mapeo


def limpiar_columnas_profesores(df):
    """
    Limpia columnas para archivo de profesores con mapeo completo.
    Soporta cedula, nombre, apellido, correo, especialidad, departamento.
    No falla por mayúsculas, acentos o espacios extra.
    """
    columnas_estandar = ['cedula', 'nombre', 'apellido', 'correo', 'especialidad', 'departamento']
    variantes = {
        'cedula': ['cedula', 'cédula', 'documento', 'ci', 'cédula '],
        'nombre': ['nombre', 'nombres', 'primer_nombre', 'nombre'],
        'apellido': ['apellido', 'apellidos', 'last_name', 'apellido'],
        'correo': ['correo', 'correo electrónico', 'email', 'mail', 'correo electronico'],
        'especialidad': ['especialidad', 'nivel académico', 'nivel academico', 'area', 'departamento'],
        'departamento': ['departamento', 'area', 'facultad', 'unidad']
    }
    mapeo = {}
    col_normalizadas = {_normalizar_texto(c): c for c in df.columns}
    for estandar in columnas_estandar:
        encontrado = False
        for variante in variantes.get(estandar, [estandar]):
            n = _normalizar_texto(variante)
            if n in col_normalizadas:
                mapeo[estandar] = col_normalizadas[n]
                encontrado = True
                break
        if not encontrado:
            return None, f"Columna '{estandar}' no encontrada. Columnas detectadas: {list(df.columns)}"
    
    # Verificar columnas mínimas requeridas
    if 'cedula' not in mapeo or 'nombre' not in mapeo or 'apellido' not in mapeo:
        return None, "Faltan columnas obligatorias: cedula, nombre, apellido"
    
    # Crear DataFrame limpio
    df_limpio = pd.DataFrame()
    for estandar, columna_original in mapeo.items():
        df_limpio[estandar] = df[columna_original]
    
    return df_limpio, mapeo


def asegurar_estructura_persona(engine=None):
    """Asegura que la tabla persona tenga las columnas necesarias para estudiantes."""
    if engine is None:
        engine = get_connection_local()
    if engine:
        _asegurar_columnas_persona(engine)


def _asegurar_columnas_persona(engine):
    """Asegura que la tabla persona exista y tenga: cedula, apellido, nombre, genero, telefono, carrera, semestre."""
    try:
        with engine.connect() as conn:
            r = conn.execute(text("""
                SELECT 1 FROM information_schema.tables
                WHERE table_schema='public' AND table_name='persona'
            """))
            if r.fetchone() is None:
                conn.execute(text("""
                    CREATE TABLE public.persona (
                        id_persona SERIAL PRIMARY KEY,
                        cedula VARCHAR(20) UNIQUE,
                        apellido VARCHAR(100),
                        nombre VARCHAR(100),
                        genero VARCHAR(20),
                        telefono VARCHAR(30),
                        carrera VARCHAR(150),
                        semestre VARCHAR(20)
                    )
                """))
                conn.commit()
                return

            columnas_nuevas = [
                ('apellido', 'VARCHAR(100)'),
                ('genero', 'VARCHAR(20)'),
                ('telefono', 'VARCHAR(30)'),
                ('carrera', 'VARCHAR(150)'),
                ('semestre', 'VARCHAR(20)'),
            ]
            for col, tipo in columnas_nuevas:
                r2 = conn.execute(text("""
                    SELECT 1 FROM information_schema.columns
                    WHERE table_schema='public' AND table_name='persona' AND column_name=:col
                """), {"col": col})
                if r2.fetchone() is None:
                    conn.execute(text(f"ALTER TABLE public.persona ADD COLUMN {col} {tipo}"))
                    conn.commit()
    except Exception:
        pass


def listar_estudiantes(engine=None):
    """
    Obtiene el listado de estudiantes de la tabla persona.
    Intenta con todas las columnas; si falla, usa columnas básicas.
    Returns:
        list: Lista de diccionarios con los datos, o [] si hay error.
    """
    if engine is None:
        engine = get_connection_local()
    if engine is None:
        return []

    queries = [
        """SELECT p.cedula as "Cédula", p.apellido as "Apellido", p.nombre as "Nombre",
           COALESCE(p.genero,'') as "Género", COALESCE(p.telefono,'') as "Teléfono",
           COALESCE(p.carrera,'') as "Carrera", COALESCE(p.semestre,'') as "Semestre"
           FROM public.persona p ORDER BY COALESCE(p.apellido,''), COALESCE(p.nombre,'')""",
        """SELECT p.cedula as "Cédula", COALESCE(p.apellido,'') as "Apellido", COALESCE(p.nombre,'') as "Nombre"
           FROM public.persona p ORDER BY COALESCE(p.apellido,''), COALESCE(p.nombre,'')""",
        """SELECT p.cedula as "Cédula", COALESCE(p.nombre,'') as "Nombre" FROM public.persona p ORDER BY p.nombre""",
    ]
    for q in queries:
        try:
            with engine.connect() as conn:
                df = pd.read_sql(text(q), conn)
                return df.to_dict('records')
        except Exception:
            continue
    return []


def insertar_estudiante(cedula, apellido, nombre, genero, telefono, carrera, semestre, engine=None):
    """
    Inserta o actualiza un estudiante en la tabla persona.
    Si la cédula ya existe, actualiza los demás campos.

    Returns:
        tuple: (éxito: bool, mensaje)
    """
    if engine is None:
        engine = get_connection_local()
    if engine is None:
        return False, "No se pudo conectar a la base de datos."

    try:
        _asegurar_columnas_persona(engine)

        sql_upsert = """
            INSERT INTO public.persona (cedula, apellido, nombre, genero, telefono, carrera, semestre)
            VALUES (:cedula, :apellido, :nombre, :genero, :telefono, :carrera, :semestre)
            ON CONFLICT (cedula) DO UPDATE SET
                apellido = EXCLUDED.apellido,
                nombre = EXCLUDED.nombre,
                genero = EXCLUDED.genero,
                telefono = EXCLUDED.telefono,
                carrera = EXCLUDED.carrera,
                semestre = EXCLUDED.semestre
        """
        
        # Normalización de datos para integridad
        params = {
            "cedula": str(cedula).strip().upper() if cedula else "",
            "apellido": str(apellido).strip().upper() if apellido else "",
            "nombre": str(nombre).strip().upper() if nombre else "",
            "genero": str(genero).strip().upper() if genero else "",
            "telefono": str(telefono).strip() if telefono else "",
            "carrera": str(carrera).strip().upper() if carrera else "",
            "semestre": str(semestre).strip() if semestre else "",
        }
        
        resultado = ejecutar_query(sql_upsert, params, engine=engine)
        
        if resultado is True:
            return True, "Estudiante guardado correctamente"
        else:
            return False, "Error al ejecutar la consulta"
            
    except Exception as e:
        return False, f"Error al insertar estudiante: {str(e)}"


def actualizar_estudiante(cedula, apellido=None, nombre=None, genero=None, telefono=None, carrera=None, semestre=None, engine=None):
    """
    Actualiza los datos de un estudiante existente.
    
    Returns:
        tuple: (éxito: bool, mensaje)
    """
    if engine is None:
        engine = get_connection_local()
    if engine is None:
        return False, "No se pudo conectar a la base de datos."

    try:
        # Construir dinámicamente la consulta UPDATE solo con los campos proporcionados
        campos_actualizar = []
        params = {"cedula": str(cedula).strip().upper()}
        
        if apellido is not None:
            campos_actualizar.append("apellido = :apellido")
            params["apellido"] = str(apellido).strip().upper()
        if nombre is not None:
            campos_actualizar.append("nombre = :nombre")
            params["nombre"] = str(nombre).strip().upper()
        if genero is not None:
            campos_actualizar.append("genero = :genero")
            params["genero"] = str(genero).strip().upper()
        if telefono is not None:
            campos_actualizar.append("telefono = :telefono")
            params["telefono"] = str(telefono).strip()
        if carrera is not None:
            campos_actualizar.append("carrera = :carrera")
            params["carrera"] = str(carrera).strip().upper()
        if semestre is not None:
            campos_actualizar.append("semestre = :semestre")
            params["semestre"] = str(semestre).strip()
        
        if not campos_actualizar:
            return False, "No se proporcionaron campos para actualizar"
        
        sql_update = f"""
            UPDATE public.persona 
            SET {', '.join(campos_actualizar)}
            WHERE cedula = :cedula
        """
        
        resultado = ejecutar_query(sql_update, params, engine=engine)
        
        if resultado is True:
            return True, "Estudiante actualizado correctamente"
        else:
            return False, "Error al ejecutar la actualización"
            
    except Exception as e:
        return False, f"Error al actualizar estudiante: {str(e)}"


def eliminar_estudiante(cedula, engine=None):
    """
    Elimina un estudiante de la base de datos por cédula.
    
    Returns:
        tuple: (éxito: bool, mensaje)
    """
    if engine is None:
        engine = get_connection_local()
    if engine is None:
        return False, "No se pudo conectar a la base de datos."

    try:
        sql_delete = "DELETE FROM public.persona WHERE cedula = :cedula"
        resultado = ejecutar_query(sql_delete, {"cedula": str(cedula).strip().upper()}, engine=engine)
        
        if resultado is True:
            return True, "Estudiante eliminado correctamente"
        else:
            return False, "No se encontró el estudiante o error al eliminar"
            
    except Exception as e:
        return False, f"Error al eliminar estudiante: {str(e)}"


def _asegurar_tabla_profesor(engine):
    try:
        # Verificar si profesor existe con columnas correctas; si no, recrear
        with engine.connect() as conn:
            r = conn.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema='public' AND table_name='profesor' AND column_name='cedula'
            """))
            tiene_cedula = r.fetchone() is not None

        if not tiene_cedula:
            # Tabla inexistente o con estructura incorrecta: recrear
            ejecutar_query("DROP TABLE IF EXISTS public.profesor CASCADE", engine=engine)

        ejecutar_query("""
            CREATE TABLE IF NOT EXISTS public.profesor (
                id_profesor SERIAL PRIMARY KEY,
                cedula VARCHAR(20) UNIQUE,
                nombre VARCHAR(100),
                apellido VARCHAR(100),
                especialidad VARCHAR(200),
                correo VARCHAR(150),
                departamento VARCHAR(100)
            )
        """, engine=engine)
        
        # Añadir columnas faltantes si la tabla ya existe
        try:
            with engine.connect() as conn:
                # Verificar si existe la columna especialidad
                r = conn.execute(text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema='public' AND table_name='profesor' AND column_name='especialidad'
                """))
                if r.fetchone() is None:
                    conn.execute(text("ALTER TABLE public.profesor ADD COLUMN especialidad VARCHAR(200)"))
                
                # Verificar si existe la columna correo
                r = conn.execute(text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema='public' AND table_name='profesor' AND column_name='correo'
                """))
                if r.fetchone() is None:
                    conn.execute(text("ALTER TABLE public.profesor ADD COLUMN correo VARCHAR(150)"))
                
                # Verificar si existe la columna departamento
                r = conn.execute(text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema='public' AND table_name='profesor' AND column_name='departamento'
                """))
                if r.fetchone() is None:
                    conn.execute(text("ALTER TABLE public.profesor ADD COLUMN departamento VARCHAR(100)"))
                
                conn.commit()
        except Exception:
            pass

        # Migrar de facilitador a profesor solo si existe la tabla antigua
        try:
            with engine.connect() as conn:
                r = conn.execute(text("""
                    SELECT 1 FROM information_schema.tables
                    WHERE table_schema='public' AND table_name='facilitador'
                """))
                if r.fetchone() is not None:
                    conn.execute(text("""
                        INSERT INTO public.profesor (cedula, nombre, apellido)
                        SELECT cedula, nombre, apellido FROM public.facilitador
                        ON CONFLICT (cedula) DO NOTHING
                    """))
                    conn.commit()
        except Exception:
            pass
    except Exception:
        pass


def crear_tablas_sistema(engine=None):
    """
    Crea todas las tablas necesarias para el sistema SICADFOC.
    """
    if engine is None:
        engine = get_connection_local()
    if engine is None:
        return False, "No se pudo conectar a la base de datos."

    try:
        with engine.connect() as conn:
            # Tabla de configuración de correo (config_correo)
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS config_correo (
                    id SERIAL PRIMARY KEY,
                    smtp_server VARCHAR(255) NOT NULL,
                    smtp_port INTEGER DEFAULT 587,
                    smtp_user VARCHAR(255) NOT NULL,
                    smtp_password TEXT NOT NULL,
                    email_remitente VARCHAR(255) NOT NULL,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    activo BOOLEAN DEFAULT TRUE
                )
            """))
            
            # Tabla de auditoría
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS auditoria (
                    id SERIAL PRIMARY KEY,
                    usuario VARCHAR(100) NOT NULL,
                    rol VARCHAR(20) NOT NULL,
                    transaccion VARCHAR(50) NOT NULL,
                    tabla_afectada VARCHAR(50),
                    registro_id VARCHAR(50),
                    detalles TEXT,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address VARCHAR(45)
                )
            """))
            
            # Actualizar tabla de usuarios para incluir rol y email
            conn.execute(text("""
                ALTER TABLE public.usuario 
                ADD COLUMN IF NOT EXISTS rol VARCHAR(20) DEFAULT 'estudiante',
                ADD COLUMN IF NOT EXISTS email VARCHAR(255),
                ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE
            """))
            
            # Crear índices para mejor rendimiento
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_auditoria_usuario ON auditoria(usuario)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON auditoria(fecha)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_usuario_email ON usuario(email)"))
            
            conn.commit()
            
        return True, "Tablas del sistema creadas correctamente"
    except Exception as e:
        return False, f"Error al crear tablas: {str(e)}"


def registrar_auditoria(usuario, rol, transaccion, tabla_afectada=None, registro_id=None, 
                       detalles=None, ip_address=None, engine=None):
    """
    Registra una transacción en la tabla de auditoría.
    """
    if engine is None:
        engine = get_connection_local()
    if engine is None:
        return False, "No se pudo conectar a la base de datos."

    try:
        sql_auditoria = """
            INSERT INTO public.auditoria 
            (usuario, rol, transaccion, tabla_afectada, registro_id, detalles, ip_address)
            VALUES (:usuario, :rol, :transaccion, :tabla, :reg_id, :detalles, :ip)
        """
        
        params = {
            "usuario": str(usuario),
            "rol": str(rol),
            "transaccion": str(transaccion),
            "tabla": str(tabla_afectada) if tabla_afectada else None,
            "reg_id": str(registro_id) if registro_id else None,
            "detalles": str(detalles) if detalles else None,
            "ip": str(ip_address) if ip_address else None
        }
        
        resultado = ejecutar_query(sql_auditoria, params, engine=engine)
        return resultado is True, "Auditoría registrada" if resultado is True else "Error en auditoría"
        
    except Exception as e:
        return False, f"Error al registrar auditoría: {str(e)}"


def obtener_config_correo(engine=None):
    """
    Obtiene la configuración de correo actual.
    """
    if engine is None:
        engine = get_connection_local()
    if engine is None:
        return None

    try:
        sql = "SELECT * FROM public.config_correo WHERE activo = TRUE ORDER BY fecha_actualizacion DESC LIMIT 1"
        resultado = ejecutar_query(sql, engine=engine)
        return resultado[0] if resultado else None
    except Exception:
        return None


def guardar_config_correo(smtp_server, smtp_port, smtp_user, smtp_password, email_remitente, engine=None):
    """
    Guarda la configuración de correo SMTP.
    """
    if engine is None:
        engine = get_connection_local()
    if engine is None:
        return False, "No se pudo conectar a la base de datos."

    try:
        # Desactivar configuraciones anteriores
        ejecutar_query("UPDATE public.config_correo SET activo = FALSE", engine=engine)
        
        # Insertar nueva configuración
        sql = """
            INSERT INTO public.config_correo 
            (smtp_server, smtp_port, smtp_user, smtp_password, email_remitente)
            VALUES (:server, :port, :user, :pass, :email)
        """
        
        params = {
            "server": str(smtp_server),
            "port": int(smtp_port),
            "user": str(smtp_user),
            "pass": str(smtp_password),
            "email": str(email_remitente)
        }
        
        resultado = ejecutar_query(sql, params, engine=engine)
        return resultado is True, "Configuración guardada" if resultado is True else "Error al guardar"
        
    except Exception as e:
        return False, f"Error al guardar configuración: {str(e)}"


def obtener_auditoria(filtro_usuario=None, filtro_rol=None, filtro_transaccion=None, 
                     fecha_inicio=None, fecha_fin=None, engine=None):
    """
    Obtiene registros de auditoría con filtros opcionales.
    """
    if engine is None:
        engine = get_connection_local()
    if engine is None:
        return []

    try:
        sql = "SELECT * FROM public.auditoria WHERE 1=1"
        params = {}
        
        if filtro_usuario:
            sql += " AND usuario = :usuario"
            params["usuario"] = str(filtro_usuario)
        if filtro_rol:
            sql += " AND rol = :rol"
            params["rol"] = str(filtro_rol)
        if filtro_transaccion:
            sql += " AND transaccion = :transaccion"
            params["transaccion"] = str(filtro_transaccion)
        if fecha_inicio:
            sql += " AND fecha >= :inicio"
            params["inicio"] = str(fecha_inicio)
        if fecha_fin:
            sql += " AND fecha <= :fin"
            params["fin"] = str(fecha_fin)
            
        sql += " ORDER BY fecha DESC LIMIT 1000"
        
        resultado = ejecutar_query(sql, params, engine=engine)
        return resultado if resultado else []
    except Exception:
        return []


def crear_usuario_prueba(engine=None):
    """
    Crea un usuario de prueba para testing (angelher@gmail.com / admin123)
    con rol Admin permanente y blindado.
    """
    if engine is None:
        engine = get_connection_local()
    if engine is None:
        return False, "No se pudo conectar a la base de datos."

    try:
        # Forzar rol Admin para angelher@gmail.com siempre
        sql_check = "SELECT * FROM public.usuario WHERE email = :email OR login = :login"
        resultado = ejecutar_query(sql_check, {"email": "angelher@gmail.com", "login": "angelher@gmail.com"}, engine=engine)
        
        if resultado:
            # Verificar si tiene rol Admin, si no, actualizarlo
            usuario_existente = resultado[0]
            if usuario_existente.get('rol') != 'admin':
                sql_update = """
                    UPDATE public.usuario 
                    SET rol = 'admin', activo = TRUE 
                    WHERE email = :email OR login = :login
                """
                ejecutar_query(sql_update, {"email": "angelher@gmail.com", "login": "angelher@gmail.com"}, engine=engine)
                return True, "Rol Admin actualizado para usuario existente"
            return True, "Usuario Admin ya existe y está blindado"
        
        # Insertar usuario Admin blindado
        sql_insert = """
            INSERT INTO public.usuario (login, email, contrasena, rol, activo)
            VALUES (:login, :email, :password, :rol, :activo)
            ON CONFLICT (email) DO UPDATE SET
                rol = EXCLUDED.rol,
                activo = EXCLUDED.activo,
                contrasena = EXCLUDED.contrasena
        """
        
        params = {
            "login": "angelher@gmail.com",
            "email": "angelher@gmail.com", 
            "password": "admin123",
            "rol": "admin",
            "activo": True
        }
        
        resultado = ejecutar_query(sql_insert, params, engine=engine)
        if resultado:
            return True, "Usuario Admin creado exitosamente"
        else:
            return False, "Error al crear usuario Admin"
            
    except Exception as e:
        return False, f"Error al crear usuario de prueba: {str(e)}"


def _asegurar_tablas_formacion(engine=None):
    """
    Crea las tablas necesarias para gestión de formación complementaria
    """
    if engine is None:
        engine = get_connection_local()
    if engine is None:
        return False
    
    try:
        with engine.connect() as conn:
            # Tabla formacion_complementaria
            sql_formacion = """
                CREATE TABLE IF NOT EXISTS public.formacion_complementaria (
                    id_formacion SERIAL PRIMARY KEY,
                    codigo_formacion VARCHAR(50) UNIQUE NOT NULL,
                    tipo_taller VARCHAR(100) NOT NULL,
                    nombre_taller VARCHAR(200) NOT NULL,
                    cedula_profesor VARCHAR(20) NOT NULL,
                    fecha_inicio DATE NOT NULL,
                    fecha_fin DATE NOT NULL,
                    cupos INTEGER DEFAULT 30,
                    estado_registro VARCHAR(20) DEFAULT 'Activo' 
                        CHECK (estado_registro IN ('Activo', 'Inactivo', 'Finalizado')),
                    observaciones TEXT,
                    fecha_creacion TIMESTAMP DEFAULT NOW(),
                    fecha_actualizacion TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (cedula_profesor) REFERENCES public.profesor(cedula)
                )
            """
            conn.execute(text(sql_formacion))
            
            # Tabla inscripcion_taller
            sql_inscripcion = """
                CREATE TABLE IF NOT EXISTS public.inscripcion_taller (
                    id_inscripcion SERIAL PRIMARY KEY,
                    id_formacion INTEGER NOT NULL,
                    cedula_estudiante VARCHAR(20) NOT NULL,
                    fecha_inscripcion TIMESTAMP DEFAULT NOW(),
                    estado_inscripcion VARCHAR(20) DEFAULT 'Pendiente'
                        CHECK (estado_inscripcion IN ('Pendiente', 'Aprobada', 'Rechazada', 'Completada')),
                    observaciones TEXT,
                    FOREIGN KEY (id_formacion) REFERENCES public.formacion_complementaria(id_formacion),
                    FOREIGN KEY (cedula_estudiante) REFERENCES public.persona(cedula),
                    UNIQUE(id_formacion, cedula_estudiante)
                )
            """
            conn.execute(text(sql_inscripcion))
            
            # Crear índices
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_formacion_codigo ON public.formacion_complementaria(codigo_formacion)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_formacion_profesor ON public.formacion_complementaria(cedula_profesor)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_formacion_estado ON public.formacion_complementaria(estado_registro)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_inscripcion_formacion ON public.inscripcion_taller(id_formacion)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_inscripcion_estudiante ON public.inscripcion_taller(cedula_estudiante)"))
            
            conn.commit()
            return True
    except Exception as e:
        return False


def insertar_formacion(codigo_formacion, tipo_taller, nombre_taller, cedula_profesor, 
                      fecha_inicio, fecha_fin, cupos=30, estado_registro='Activo', 
                      observaciones=None, engine=None):
    """
    Inserta una nueva formación complementaria
    """
    if engine is None:
        engine = get_connection_local()
    if engine is None:
        return False, "No se pudo conectar a la base de datos."
    
    try:
        _asegurar_tablas_formacion(engine)
        
        sql_insert = """
            INSERT INTO public.formacion_complementaria 
            (codigo_formacion, tipo_taller, nombre_taller, cedula_profesor, 
             fecha_inicio, fecha_fin, cupos, estado_registro, observaciones)
            VALUES (:codigo, :tipo, :nombre, :profesor, :inicio, :fin, :cupos, :estado, :obs)
            ON CONFLICT (codigo_formacion) DO UPDATE SET
                tipo_taller = EXCLUDED.tipo_taller,
                nombre_taller = EXCLUDED.nombre_taller,
                cedula_profesor = EXCLUDED.cedula_profesor,
                fecha_inicio = EXCLUDED.fecha_inicio,
                fecha_fin = EXCLUDED.fecha_fin,
                cupos = EXCLUDED.cupos,
                estado_registro = EXCLUDED.estado_registro,
                observaciones = EXCLUDED.observaciones,
                fecha_actualizacion = NOW()
            RETURNING id_formacion
        """
        
        params = {
            "codigo": codigo_formacion.strip().upper(),
            "tipo": tipo_taller.strip().upper(),
            "nombre": nombre_taller.strip().upper(),
            "profesor": cedula_profesor.strip().upper(),
            "inicio": fecha_inicio,
            "fin": fecha_fin,
            "cupos": cupos,
            "estado": estado_registro,
            "obs": observaciones.strip().upper() if observaciones else None
        }
        
        resultado = ejecutar_query(sql_insert, params, engine=engine)
        if resultado and len(resultado) > 0:
            return True, resultado[0]['id_formacion']
        else:
            return False, "Error al insertar formación"
            
    except Exception as e:
        return False, f"Error al insertar formación: {str(e)}"


def listar_formaciones(filtro_codigo=None, filtro_tipo=None, filtro_estado=None, engine=None):
    """
    Lista las formaciones complementarias con filtros opcionales
    """
    if engine is None:
        engine = get_connection_local()
    if engine is None:
        return []
    
    try:
        sql_base = """
            SELECT fc.id_formacion, fc.codigo_formacion, fc.tipo_taller, fc.nombre_taller,
                   fc.cedula_profesor, p.nombre as nombre_profesor, p.apellido as apellido_profesor,
                   fc.fecha_inicio, fc.fecha_fin, fc.cupos, fc.estado_registro, 
                   fc.observaciones, fc.fecha_creacion, fc.fecha_actualizacion,
                   (SELECT COUNT(*) FROM public.inscripcion_taller it 
                    WHERE it.id_formacion = fc.id_formacion AND it.estado_inscripcion = 'Aprobada') as inscritos
            FROM public.formacion_complementaria fc
            LEFT JOIN public.profesor p ON fc.cedula_profesor = p.cedula
            WHERE 1=1
        """
        
        params = {}
        if filtro_codigo:
            sql_base += " AND fc.codigo_formacion ILIKE :codigo"
            params["codigo"] = f"%{filtro_codigo}%"
        if filtro_tipo:
            sql_base += " AND fc.tipo_taller ILIKE :tipo"
            params["tipo"] = f"%{filtro_tipo}%"
        if filtro_estado:
            sql_base += " AND fc.estado_registro = :estado"
            params["estado"] = filtro_estado
            
        sql_base += " ORDER BY fc.fecha_creacion DESC"
        
        resultado = ejecutar_query(sql_base, params, engine=engine)
        return resultado if resultado else []
        
    except Exception as e:
        return []


def eliminar_formacion(id_formacion, engine=None):
    """
    Elimina una formación complementaria (solo admin)
    """
    if engine is None:
        engine = get_connection_local()
    if engine is None:
        return False, "No se pudo conectar a la base de datos."
    
    try:
        # Primero eliminar inscripciones relacionadas
        sql_delete_inscripciones = "DELETE FROM public.inscripcion_taller WHERE id_formacion = :id"
        ejecutar_query(sql_delete_inscripciones, {"id": id_formacion}, engine=engine)
        
        # Luego eliminar la formación
        sql_delete_formacion = "DELETE FROM public.formacion_complementaria WHERE id_formacion = :id"
        resultado = ejecutar_query(sql_delete_formacion, {"id": id_formacion}, engine=engine)
        
        if resultado:
            return True, "Formación eliminada exitosamente"
        else:
            return False, "No se encontró la formación a eliminar"
            
    except Exception as e:
        return False, f"Error al eliminar formación: {str(e)}"


def eliminar_profesor(cedula, engine=None):
    """
    Elimina un profesor de la base de datos por cédula (solo admin)
    """
    if engine is None:
        engine = get_connection_local()
    if engine is None:
        return False, "No se pudo conectar a la base de datos."
    
    try:
        # Verificar si el profesor existe
        sql_check = "SELECT cedula FROM public.profesor WHERE cedula = :cedula"
        resultado_check = ejecutar_query(sql_check, {"cedula": cedula}, engine=engine)
        
        if not resultado_check:
            return False, f"No se encontró un profesor con cédula: {cedula}"
        
        # Verificar si el profesor tiene formaciones asignadas
        sql_check_formaciones = "SELECT COUNT(*) as count FROM public.formacion_complementaria WHERE cedula_profesor = :cedula"
        resultado_formaciones = ejecutar_query(sql_check_formaciones, {"cedula": cedula}, engine=engine)
        
        if resultado_formaciones and resultado_formaciones[0]['count'] > 0:
            return False, f"No se puede eliminar el profesor. Tiene {resultado_formaciones[0]['count']} formaciones asignadas"
        
        # Eliminar el profesor
        sql_delete = "DELETE FROM public.profesor WHERE cedula = :cedula"
        resultado = ejecutar_query(sql_delete, {"cedula": cedula}, engine=engine)
        
        if resultado:
            return True, "Profesor eliminado exitosamente"
        else:
            return False, "No se pudo eliminar el profesor"
            
    except Exception as e:
        return False, f"Error al eliminar profesor: {str(e)}"


def inscribir_estudiante_taller(id_formacion, cedula_estudiante, observaciones=None, engine=None):
    """
    Inscribir un estudiante en un taller
    """
    if engine is None:
        engine = get_connection_local()
    if engine is None:
        return False, "No se pudo conectar a la base de datos."
    
    try:
        _asegurar_tablas_formacion(engine)
        
        sql_insert = """
            INSERT INTO public.inscripcion_taller 
            (id_formacion, cedula_estudiante, observaciones)
            VALUES (:id_formacion, :cedula, :obs)
            ON CONFLICT (id_formacion, cedula_estudiante) DO UPDATE SET
                fecha_inscripcion = NOW(),
                estado_inscripcion = 'Pendiente',
                observaciones = EXCLUDED.observaciones
            RETURNING id_inscripcion
        """
        
        params = {
            "id_formacion": id_formacion,
            "cedula": cedula_estudiante.strip().upper(),
            "obs": observaciones.strip().upper() if observaciones else None
        }
        
        resultado = ejecutar_query(sql_insert, params, engine=engine)
        if resultado and len(resultado) > 0:
            return True, resultado[0]['id_inscripcion']
        else:
            return False, "Error al inscribir estudiante"
            
    except Exception as e:
        return False, f"Error al inscribir estudiante: {str(e)}"

def get_metricas_dashboard(engine=None):
    """
    Obtiene las métricas para el dashboard de Inicio: Talleres, Estudiantes y Profesores.

    Returns:
        dict: {'talleres': int, 'estudiantes': int, 'profesores': int}
        Retorna 0 para cualquier métrica si la tabla no existe o hay error.
    """
    if engine is None:
        engine = get_connection_local()
    if engine is None:
        return {'talleres': 0, 'estudiantes': 0, 'profesores': 0}

    _asegurar_tabla_profesor(engine)

    metricas = {'talleres': 0, 'estudiantes': 0, 'profesores': 0}

    try:
        r_t = ejecutar_query("SELECT count(*) as total FROM public.taller", engine=engine)
        if r_t:
            metricas['talleres'] = r_t[0]['total']
    except Exception:
        pass

    try:
        r_e = ejecutar_query("SELECT count(*) as total FROM public.persona", engine=engine)
        if r_e:
            metricas['estudiantes'] = r_e[0]['total']
    except Exception:
        pass

    try:
        r_p = ejecutar_query("SELECT count(*) as total FROM public.profesor", engine=engine)
        if r_p:
            metricas['profesores'] = r_p[0]['total']
    except Exception:
        pass

    return metricas


def obtener_profesores(engine=None):
    """
    Obtiene todos los profesores con todos sus campos.
    
    Returns:
        list: Lista de diccionarios con los datos de profesores
    """
    if engine is None:
        engine = get_connection_local()
    if engine is None:
        return []
    
    try:
        _asegurar_tabla_profesor(engine)
        
        sql = """
            SELECT id_profesor, cedula, nombre, apellido, especialidad, correo, departamento
            FROM public.profesor 
            ORDER BY apellido, nombre
        """
        
        resultado = ejecutar_query(sql, engine=engine)
        return resultado if resultado else []
        
    except Exception as e:
        return []


def insertar_profesor(cedula, nombre, apellido, especialidad=None, correo=None, departamento=None, engine=None):
    """
    Inserta un profesor en la base de datos.
    Asegura que la cédula no se repita; si ya existe, no inserta y retorna False.

    Args:
        cedula: Cédula del profesor (identificador único)
        nombre: Nombre del profesor
        apellido: Apellido del profesor
        especialidad: Especialidad del profesor (opcional)
        correo: Correo electrónico del profesor (opcional)
        departamento: Departamento del profesor (opcional)
        engine: Motor de SQLAlchemy (opcional, usa get_connection_local() si no se pasa)

    Returns:
        tuple: (éxito: bool, id_profesor o mensaje)
            - (True, id_profesor) si se insertó correctamente
            - (False, "La cédula ya está registrada.") si la cédula ya existe
            - (False, mensaje_error) si ocurrió un error
    """
    if engine is None:
        engine = get_connection_local()

    if engine is None:
        return False, "No se pudo conectar a la base de datos."

    try:
        _asegurar_tabla_profesor(engine)

        # Insertar solo si la cédula no existe (ON CONFLICT DO NOTHING)
        sql_insert = """
            INSERT INTO public.profesor (cedula, nombre, apellido, especialidad, correo, departamento)
            VALUES (:c, :n, :a, :e, :co, :d)
            ON CONFLICT (cedula) DO NOTHING
            RETURNING id_profesor
        """
        with engine.connect() as conn:
            result = conn.execute(
                text(sql_insert),
                {
                    "c": str(cedula).strip(), 
                    "n": str(nombre).strip().upper(), 
                    "a": str(apellido).strip().upper(),
                    "e": str(especialidad).strip().upper() if especialidad else None,
                    "co": str(correo).strip().upper() if correo else None,
                    "d": str(departamento).strip().upper() if departamento else None
                }
            )
            row = result.fetchone()
            conn.commit()

        if row is not None:
            return True, row[0]
        else:
            return False, "La cédula ya está registrada."
    except Exception as e:
        st.error(f"Error al insertar profesor: {e}")
        return False, str(e)
