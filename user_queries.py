"""
CONSULTAS DE USUARIOS - SICADFOC 2026
Módulo independiente para consultas de usuarios y autenticación
DBA Senior & Full-Stack - WindSurf
"""
import logging
from sqlalchemy import text

# Importar conexión desde módulo independiente
from .connection import get_engine_local

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def consultar_usuario_por_cedula(cedula):
    """
    Consultar información de una persona por cédula
    Args:
        cedula (str): Número de cédula a consultar
    Returns:
        dict: Información del usuario o None si no existe
    """
    try:
        engine = get_engine_local()
        with engine.connect() as conn:
            # Buscar persona por cédula
            query_persona = """
                SELECT p.id_persona, p.cedula, p.nombre, p.apellido, p.email as email_persona,
                       p.telefono, p.carrera, p.semestre,
                       u.id as usuario_id, u.login, u.email as email_usuario, u.rol, u.activo
                FROM persona p
                LEFT JOIN usuario u ON p.id_persona = u.id_persona
                WHERE p.cedula = :cedula
            """
            
            result = conn.execute(text(query_persona), {'cedula': cedula}).fetchone()
            
            if result:
                return {
                    'id_persona': result[0],
                    'cedula': result[1],
                    'nombre': result[2],
                    'apellido': result[3],
                    'email_persona': result[4],
                    'telefono': result[5],
                    'carrera': result[6],
                    'semestre': result[7],
                    'usuario_id': result[8],
                    'login': result[9],
                    'email_usuario': result[10],
                    'rol': result[11],
                    'activo': result[12]
                }
            else:
                return None
                
    except Exception as e:
        logger.error(f"❌ Error consultando usuario por cédula {cedula}: {e}")
        return None

def consultar_usuario_por_email_o_login(email_o_login):
    """
    Consultar información de un usuario por email o login
    Args:
        email_o_login (str): Email o login a consultar
    Returns:
        dict: Información del usuario o None si no existe
    """
    try:
        engine = get_engine_local()
        with engine.connect() as conn:
            # Buscar usuario por email o login
            query_usuario = """
                SELECT u.id, u.login, u.email, u.rol, u.activo, u.correo_verificado,
                       p.id_persona, p.nombre, p.apellido, p.cedula
                FROM usuario u
                LEFT JOIN persona p ON u.id_persona = p.id_persona
                WHERE (u.login = :email_o_login OR u.email = :email_o_login)
            """
            
            result = conn.execute(text(query_usuario), {'email_o_login': email_o_login}).fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'login': result[1],
                    'email': result[2],
                    'rol': result[3],
                    'activo': result[4],
                    'correo_verificado': result[5],
                    'id_persona': result[6],
                    'nombre': result[7],
                    'apellido': result[8],
                    'cedula': result[9]
                }
            else:
                return None
                
    except Exception as e:
        logger.error(f"❌ Error consultando usuario por email/login {email_o_login}: {e}")
        return None

def verificar_credenciales(email, password):
    """
    Verificar las credenciales de un usuario
    Args:
        email (str): Email del usuario
        password (str): Contraseña del usuario (sin hashear)
    Returns:
        dict: Información del usuario si las credenciales son correctas, None en caso contrario
    """
    try:
        import hashlib
        engine = get_engine_local()
        
        # Hashear la contraseña
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        with engine.connect() as conn:
            # Buscar usuario con credenciales correctas
            query_auth = """
                SELECT u.id, u.login, u.email, u.rol, u.activo, u.correo_verificado,
                       p.id_persona, p.nombre, p.apellido, p.cedula
                FROM usuario u
                LEFT JOIN persona p ON u.id_persona = p.id_persona
                WHERE (u.login = :email OR u.email = :email) AND u.contrasena = :password
            """
            
            result = conn.execute(text(query_auth), {
                'email': email, 
                'password': password_hash
            }).fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'login': result[1],
                    'email': result[2],
                    'rol': result[3],
                    'activo': result[4],
                    'correo_verificado': result[5],
                    'id_persona': result[6],
                    'nombre': result[7],
                    'apellido': result[8],
                    'cedula': result[9]
                }
            else:
                return None
                
    except Exception as e:
        logger.error(f"❌ Error verificando credenciales para {email}: {e}")
        return None

def registrar_intento_login(email, exito=False, detalles=""):
    """
    Registrar un intento de login en la auditoría
    Args:
        email (str): Email del usuario
        exito (bool): Si el login fue exitoso
        detalles (str): Detalles adicionales
    Returns:
        bool: True si se registró correctamente
    """
    try:
        engine = get_engine_local()
        with engine.connect() as conn:
            # Insertar en tabla de auditoría
            query_auditoria = """
                INSERT INTO auditoria (accion, usuario, detalles, fecha)
                VALUES (:accion, :usuario, :detalles, CURRENT_TIMESTAMP)
            """
            
            accion = 'LOGIN_EXITOSO' if exito else 'LOGIN_FALLIDO'
            
            conn.execute(text(query_auditoria), {
                'accion': accion,
                'usuario': email,
                'detalles': detalles
            })
            
            conn.commit()
            logger.info(f"✅ Intento de login registrado: {email} - {accion}")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error registrando intento de login: {e}")
        return False

def obtener_usuarios_activos():
    """
    Obtener lista de usuarios activos
    Returns:
        list: Lista de usuarios activos
    """
    try:
        engine = get_engine_local()
        with engine.connect() as conn:
            query = """
                SELECT u.id, u.login, u.email, u.rol, u.correo_verificado,
                       p.nombres, p.apellidos, p.cedula
                FROM usuario u
                LEFT JOIN persona p ON u.id_persona = p.id_persona
                WHERE u.activo = TRUE
                ORDER BY u.rol, p.nombres
            """
            
            result = conn.execute(text(query)).fetchall()
            
            usuarios = []
            for row in result:
                usuarios.append({
                    'id': row[0],
                    'login': row[1],
                    'email': row[2],
                    'rol': row[3],
                    'correo_verificado': row[4],
                    'nombre': row[5],
                    'apellido': row[6],
                    'cedula': row[7]
                })
            
            return usuarios
            
    except Exception as e:
        logger.error(f"❌ Error obteniendo usuarios activos: {e}")
        return []

def verificar_cedula_existente(cedula):
    """
    Verificar si una cédula ya existe en el sistema
    Args:
        cedula (str): Cédula a verificar
    Returns:
        bool: True si existe, False en caso contrario
    """
    try:
        engine = get_engine_local()
        with engine.connect() as conn:
            query = "SELECT COUNT(*) FROM persona WHERE cedula = :cedula"
            result = conn.execute(text(query), {'cedula': cedula}).fetchone()[0]
            
            return result > 0
            
    except Exception as e:
        logger.error(f"❌ Error verificando cédula {cedula}: {e}")
        return False

def verificar_email_existente(email):
    """
    Verificar si un email ya existe en el sistema
    Args:
        email (str): Email a verificar
    Returns:
        bool: True si existe, False en caso contrario
    """
    try:
        engine = get_engine_local()
        with engine.connect() as conn:
            query = "SELECT COUNT(*) FROM usuario WHERE email = :email"
            result = conn.execute(text(query), {'email': email}).fetchone()[0]
            
            return result > 0
            
    except Exception as e:
        logger.error(f"❌ Error verificando email {email}: {e}")
        return False
