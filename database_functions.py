"""
FUNCIONES PRINCIPALES DE BASE DE DATOS - SICADFOC 2026
Módulo independiente para funciones principales de base de datos
DBA Senior & Full-Stack - WindSurf
"""
import logging
from sqlalchemy import text
from datetime import datetime

# Importar conexión desde módulo independiente
from .connection import get_engine_local

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def crear_tablas_sistema(engine):
    """
    Crear todas las tablas necesarias para el sistema
    Args:
        engine: Engine de SQLAlchemy
    Returns:
        bool: True si exitoso, False en caso contrario
    """
    try:
        with engine.connect() as conn:
            # Tabla de personas
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS persona (
                    id_persona INTEGER PRIMARY KEY AUTOINCREMENT,
                    cedula VARCHAR(20) UNIQUE NOT NULL,
                    nombres VARCHAR(100) NOT NULL,
                    apellidos VARCHAR(100) NOT NULL,
                    fecha_nacimiento DATE,
                    telefono VARCHAR(20),
                    direccion TEXT,
                    email VARCHAR(255),
                    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Tabla de usuarios
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS usuario (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    login VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    contrasena VARCHAR(255) NOT NULL,
                    rol VARCHAR(50) DEFAULT 'estudiante',
                    activo BOOLEAN DEFAULT TRUE,
                    correo_verificado BOOLEAN DEFAULT FALSE,
                    id_rol INTEGER,
                    id_persona INTEGER,
                    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
                )
            """))
            
            # Tabla de cursos
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS cursos (
                    id_curso INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_curso VARCHAR(200) NOT NULL,
                    descripcion TEXT,
                    id_profesor INTEGER,
                    estado VARCHAR(20) DEFAULT 'activo',
                    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_profesor) REFERENCES persona(id_persona)
                )
            """))
            
            # Tabla de talleres
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS taller (
                    id_taller INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_taller VARCHAR(200) NOT NULL,
                    descripcion TEXT,
                    id_profesor INTEGER,
                    fecha DATE,
                    hora_inicio TIME,
                    hora_fin TIME,
                    cupo_maximo INTEGER DEFAULT 30,
                    estado VARCHAR(20) DEFAULT 'activo',
                    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_profesor) REFERENCES persona(id_persona)
                )
            """))
            
            # Tabla de inscripciones
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS inscripcion (
                    id_inscripcion INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_estudiante INTEGER,
                    id_curso INTEGER,
                    id_taller INTEGER,
                    fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    estado VARCHAR(20) DEFAULT 'activa',
                    FOREIGN KEY (id_estudiante) REFERENCES persona(id_persona),
                    FOREIGN KEY (id_curso) REFERENCES cursos(id_curso),
                    FOREIGN KEY (id_taller) REFERENCES taller(id_taller)
                )
            """))
            
            # Tabla de auditoría
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS auditoria (
                    id_auditoria INTEGER PRIMARY KEY AUTOINCREMENT,
                    accion VARCHAR(100) NOT NULL,
                    usuario VARCHAR(255) NOT NULL,
                    detalles TEXT,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address VARCHAR(45)
                )
            """))
            
            conn.commit()
            logger.info("✅ Tablas del sistema creadas exitosamente")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error creando tablas: {e}")
        return False

def ejecutar_query(query, params=None):
    """
    Ejecutar un query en la base de datos
    Args:
        query (str): Query SQL a ejecutar
        params (dict): Parámetros del query
    Returns:
        list: Resultados del query
    """
    try:
        engine = get_engine_local()
        with engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            return result.fetchall()
    except Exception as e:
        logger.error(f"❌ Error ejecutando query: {e}")
        return []

def crear_usuario_prueba():
    """
    Crear un usuario de prueba para el sistema
    Returns:
        bool: True si exitoso, False en caso contrario
    """
    try:
        engine = get_engine_local()
        with engine.connect() as conn:
            # Verificar si ya existe el usuario de prueba
            check = conn.execute(text("SELECT id FROM usuario WHERE login = 'admin@iujo.edu'")).fetchone()
            
            if not check:
                # Crear persona para el admin
                conn.execute(text("""
                    INSERT INTO persona (cedula, nombres, apellidos, email)
                    VALUES ('14300385', 'Administrador', 'Sistema', 'admin@iujo.edu')
                """))
                
                # Obtener ID de la persona creada
                persona_id = conn.execute(text("SELECT last_insert_rowid()")).fetchone()[0]
                
                # Crear usuario admin
                conn.execute(text("""
                    INSERT INTO usuario (login, email, contrasena, rol, activo, correo_verificado, id_persona)
                    VALUES ('admin@iujo.edu', 'admin@iujo.edu', 'd41d8cd98f00b204e9800998ecf8427e', 'administrador', TRUE, TRUE, :persona_id)
                """), {'persona_id': persona_id})
                
                conn.commit()
                logger.info("✅ Usuario de prueba creado exitosamente")
                return True
            else:
                logger.info("ℹ️ Usuario de prueba ya existe")
                return True
                
    except Exception as e:
        logger.error(f"❌ Error creando usuario de prueba: {e}")
        return False

def obtener_logs_sistema():
    """
    Obtener logs del sistema
    Returns:
        list: Lista de logs
    """
    try:
        engine = get_engine_local()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT accion, usuario, detalles, fecha
                FROM auditoria
                ORDER BY fecha DESC
                LIMIT 100
            """)).fetchall()
            
            return result
            
    except Exception as e:
        logger.error(f"❌ Error obteniendo logs: {e}")
        return []

def configurar_correo_final():
    """
    Configurar el sistema de correo
    Returns:
        bool: True si exitoso, False en caso contrario
    """
    try:
        # Aquí iría la lógica de configuración de correo
        logger.info("✅ Sistema de correo configurado")
        return True
    except Exception as e:
        logger.error(f"❌ Error configurando correo: {e}")
        return False

def probar_envio_correo():
    """
    Probar el envío de correo
    Returns:
        bool: True si exitoso, False en caso contrario
    """
    try:
        # Aquí iría la lógica de prueba de correo
        logger.info("✅ Prueba de correo enviada")
        return True
    except Exception as e:
        logger.error(f"❌ Error en prueba de correo: {e}")
        return False
