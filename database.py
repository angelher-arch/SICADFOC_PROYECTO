#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
database.py - Gestor de base de datos PostgreSQL
SICADFOC 2026 - Instituto Universitario Jesus Obrero
"""

import streamlit as st
import psycopg2
import psycopg2.pool
from psycopg2.extras import RealDictCursor
from psycopg2 import OperationalError
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, Any
from dotenv import load_dotenv
from config import get_database_config, log_environment

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseStructureError(Exception):
    """Excepción personalizada para errores de estructura de base de datos"""
    pass

class DatabaseManager:
    """Gestor de base de datos PostgreSQL mejorado y estable"""
    
    def __init__(self):
        """Inicialización segura con manejo robusto de conexiones"""
        self._connection = None
        self._load_config()
        self._validate_database_structure()
        
    def _load_config(self):
        """CONFIGURACIÓN CENTRALIZADA desde config.py"""
        # LIMPIEZA DE CACHÉ - Inicializar desde cero
        self._connection = None
        
        # Usar configuración centralizada desde config.py
        self.config = get_database_config()
        
        # Agregar sslmode según ambiente
        from config import is_production
        if is_production():
            self.config['sslmode'] = 'require'  # Requerido para Render
        else:
            self.config['sslmode'] = 'prefer'  # Opcional para desarrollo local
        
        # Log del ambiente para monitoreo
        log_environment()
    
    def _validate_database_structure(self):
        """Validar estructura crítica de base de datos al iniciar"""
        try:
            critical_tables = ['usuarios', 'persona', 'estudiante', 'profesor', 'configuracion_permisos']
            missing_tables = []
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            for table in critical_tables:
                try:
                    cursor.execute(f"SELECT 1 FROM {table} LIMIT 1")
                except Exception as e:
                    if "does not exist" in str(e).lower():
                        missing_tables.append(table)
                    else:
                        logger.warning(f"Error verificando tabla {table}: {e}")
            
            if missing_tables:
                error_msg = f"TABLAS CRÍTICAS FALTANTES: {', '.join(missing_tables)}"
                logger.error(error_msg)
                raise DatabaseStructureError(
                    f"La base de datos está incompleta. Faltan las tablas: {', '.join(missing_tables)}. "
                    f"Ejecute: psql -d {self.config['database']} -f sincronizacion_tablas.sql"
                )
            else:
                logger.info("Estructura de base de datos validada correctamente")
                
        except Exception as e:
            if isinstance(e, DatabaseStructureError):
                raise
            logger.error(f"Error validando estructura de base de datos: {e}")
            # No lanzar excepción para permitir funcionamiento parcial
        
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    @st.cache_resource
    def get_connection(_self):
        """Obtener conexión directa a la base de datos con persistencia y validación"""
        try:
            # Si ya existe una conexión y está abierta, validar y retornarla
            if _self._connection and not _self._connection.closed:
                # Validar que la conexión aún funciona con SELECT 1
                try:
                    cursor = _self._connection.cursor()
                    cursor.execute("SELECT 1")
                    cursor.close()
                    return _self._connection
                except:
                    # Si falla la validación, crear nueva conexión
                    _self._connection = None
            
            # Crear nueva conexión con sslmode dinámico
            connection_params = {
                'host': _self.config['host'],
                'port': _self.config['port'],
                'database': _self.config['database'],
                'user': _self.config['user'],
                'password': _self.config['password'],
                'cursor_factory': RealDictCursor
            }
            
            # Agregar sslmode si está configurado (Render lo requiere)
            if 'sslmode' in _self.config:
                connection_params['sslmode'] = _self.config['sslmode']
            
            _self._connection = psycopg2.connect(**connection_params)
            
            # VERIFICACIÓN DE ESQUEMA - Optimizada para rendimiento
            cursor = _self._connection.cursor()
            
            # Forzar esquema a public para consistencia
            cursor.execute("SET search_path TO public;")
            _self._connection.commit()
            
            logger.info("Nueva conexión establecida y validada exitosamente")
            return _self._connection
            
        except OperationalError as e:
            error_msg = f"Error de conexión a {_self.config['database']}@{_self.config['host']}:{_self.config['port']}: {e}"
            print(f"ERROR: {error_msg}")
            logger.error(error_msg)
            raise ConnectionError(f"No se pudo conectar a PostgreSQL: {e}")
        except Exception as e:
            error_msg = f"Error inesperado obteniendo conexión: {e}"
            print(f"ERROR: {error_msg}")
            logger.error(error_msg)
            raise
    
    def close_connection(self):
        """Cerrar conexión actual"""
        try:
            if self._connection and not self._connection.closed:
                self._connection.close()
                self._connection = None
                logger.info("Conexión cerrada exitosamente")
        except Exception as e:
            logger.error(f"Error cerrando conexión: {e}")
    
    def execute_query(self, query: str, params: Optional[Tuple] = None, 
                      fetch_one: bool = False, fetch_all: bool = False) -> Union[Dict, List[Dict], int]:
        """
        Ejecutar consulta SQL con manejo robusto de errores
        """
        start_time = datetime.now()
        conn = None
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Ejecutar consulta
            cursor.execute(query, params or ())
            
            # Determinar tipo de retorno
            if fetch_one:
                result = cursor.fetchone()
                return dict(result) if result else {}
            elif fetch_all:
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                return cursor.rowcount
                
        except OperationalError as e:
            logger.error(f"Error de conexión en execute_query: {e}")
            # Intentar reconectar
            self.close_connection()
            raise
        except Exception as e:
            logger.error(f"Error en execute_query: {e}")
            raise
        finally:
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"Query ejecutada en {elapsed:.3f}s: {query[:100]}...")
    
    def execute_transaction(self, queries: List[Tuple[str, Optional[Tuple]]]) -> bool:
        """
        Ejecutar múltiples consultas en una transacción
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Iniciar transacción
            for query, params in queries:
                cursor.execute(query, params or ())
            
            # Commit
            conn.commit()
            logger.info(f"Transacción completada exitosamente ({len(queries)} consultas)")
            return True
            
        except Exception as e:
            # Rollback en caso de error
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            logger.error(f"Error en transacción: {e}")
            return False
        finally:
            # No cerrar la conexión aquí, se reutilizará
            pass
    
    def test_connection(self) -> Dict[str, Any]:
        """Validar conexión con la base de datos"""
        test_result = {
            'status': False,
            'message': '',
            'database_info': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Test básico
            cursor.execute("SELECT 1")
            test_result['status'] = True
            test_result['message'] = 'Conexión exitosa'
            
            # Información de la base de datos
            cursor.execute("SELECT version()")
            version_info = cursor.fetchone()
            test_result['database_info']['version'] = version_info['version'] if version_info else 'Unknown'
            
            # Verificar tablas principales
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name IN ('usuarios', 'estudiante', 'carrera')
                ORDER BY table_name
            """)
            tables = [row['table_name'] for row in cursor.fetchall()]
            test_result['database_info']['tables'] = tables
            
            # Contar usuarios
            cursor.execute("SELECT COUNT(*) as count FROM usuarios")
            user_count = cursor.fetchone()
            test_result['database_info']['user_count'] = user_count['count'] if user_count else 0
            
            logger.info("Test de conexión exitoso")
            
        except Exception as e:
            test_result['status'] = False
            test_result['message'] = f'Error de conexión: {str(e)}'
            logger.error(f"Error en test de conexión: {e}")
        
        return test_result

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()

# Funciones globales para compatibilidad
def execute_query(query: str, params: Optional[Tuple] = None, 
                  fetch_one: bool = False, fetch_all: bool = False) -> Union[Dict, List[Dict], int]:
    """Función wrapper para execute_query del DatabaseManager"""
    return db_manager.execute_query(query, params, fetch_one, fetch_all)

def fetch_data(query: str, params: Optional[Tuple] = None, 
               fetch_one: bool = False) -> Union[Dict, List[Dict]]:
    """Función wrapper para fetch_data del DatabaseManager"""
    return db_manager.execute_query(query, params, fetch_one, not fetch_one)

def ejecutar_transaccion(queries: List[Tuple[str, Optional[Tuple]]]) -> Dict[str, Any]:
    """Función wrapper para ejecutar_transaccion del DatabaseManager"""
    return db_manager.execute_transaction(queries)

def test_database_connection() -> Dict[str, Any]:
    """Función wrapper para test_connection del DatabaseManager"""
    return db_manager.test_connection()

def execute_transaction(queries: List[Tuple[str, Optional[Tuple]]]) -> Dict[str, Any]:
    """
    Ejecutar múltiples consultas en una transacción
    Returns: {'success': bool, 'message': str}
    """
    try:
        result = db_manager.execute_transaction(queries)
        return {
            'success': result,
            'message': 'Transacción completada exitosamente' if result else 'Error en transacción'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error en transacción: {str(e)}'
        }

def get_database_info() -> Dict[str, Any]:
    """Obtener información de la base de datos"""
    return db_manager.test_connection()

def close_database():
    """Cerrar conexión a la base de datos"""
    db_manager.close_connection()

def get_db_session():
    """Obtener sesión de base de datos con diagnóstico y forzado de esquema"""
    try:
        # Obtener conexión
        conn = db_manager.get_connection()
        
        # DIAGNÓSTICO DE CONEXIÓN
        print(f"=== DIAGNÓSTICO DE CONEXIÓN ===")
        print(f"Host: {db_manager.config['host']}")
        print(f"Database: {db_manager.config['database']}")
        print(f"User: {db_manager.config['user']}")
        
        # FORZAR ESQUEMA PUBLIC
        cursor = conn.cursor()
        
        # Verificar search_path actual
        cursor.execute("SHOW search_path;")
        current_search_path = cursor.fetchone()
        print(f"Search Path Actual: {current_search_path['search_path'] if current_search_path else 'No definido'}")
        
        # FORZAR A PUBLIC
        cursor.execute("SET search_path TO public;")
        conn.commit()
        
        # Verificar nuevo search_path
        cursor.execute("SHOW search_path;")
        new_search_path = cursor.fetchone()
        print(f"Search Path Forzado: {new_search_path['search_path'] if new_search_path else 'No definido'}")
        
        # VERIFICACIÓN DE INTEGRIDAD - Tabla usuarios
        try:
            cursor.execute("SELECT COUNT(*) FROM usuarios;")
            user_count = cursor.fetchone()
            print(f"OK TABLA usuarios: {user_count['count']} registros encontrados")
            cursor.close()
        except Exception as e:
            cursor.close()
            error_msg = f"ERROR TABLA usuarios: {e}"
            print(f"ERROR: {error_msg}")
            print(f"INTENTADO CONECTAR A: {db_manager.config['database']}@{db_manager.config['host']}:{db_manager.config['port']}")
            raise Exception(f"Error de conexión a la BD: {db_manager.config['database']} en {db_manager.config['host']}")
        
        print(f"=== FIN DIAGNÓSTICO ===")
        return conn
        
    except Exception as e:
        print(f"ERROR CRÍTICO en get_db_session(): {e}")
        raise

def get_connection():
        """CONEXIÓN DIRECTA HARDCODED - Sin dependencias externas"""
        try:
            print(f"=== CONEXIÓN HARDCODED DIRECTA ===")
            
            # CONEXIÓN DIRECTA Y EXPLÍCITA
            conn = psycopg2.connect(
                dbname="db_foc26",
                user="postgres", 
                password="admin123",
                host="localhost",
                port="5432"
            )
            
            print(f"OK: Conexión establecida directamente a db_foc26@localhost:5432")
            
            # FORZAR ESQUEMA PUBLIC
            cursor = conn.cursor()
            cursor.execute("SET search_path TO public;")
            conn.commit()
            cursor.close()
            
            print(f"OK: Esquema forzado a public")
            
            return conn
            
        except Exception as e:
            print(f"ERROR CRÍTICO en conexión directa: {e}")
            raise Exception(f"Conexión fallida: la base de datos no reconoce la tabla usuarios")

def verificar_y_forzar_schema():
    """Función de verificación y forzado de esquema con detención si es necesario"""
    try:
        print("=== VERIFICACIÓN Y FORZADO DE ESQUEMA ===")
        
        # Obtener conexión limpia
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # 1. Verificar base de datos actual
        cursor.execute("SELECT current_database();")
        current_db = cursor.fetchone()
        print(f"BASE DE DATOS CONECTADA: {current_db['current_database']}")
        
        # 2. Forzar esquema a public
        cursor.execute("SET search_path TO public;")
        conn.commit()
        print("ESQUEMA FORZADO A 'public'")
        
        # 3. Verificar tablas en esquema public
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables_result = cursor.fetchall()
        table_names = [table['table_name'] for table in tables_result]
        
        print(f"TABLAS DETECTADAS: {len(table_names)}")
        print(f"LISTA: {table_names}")
        
        # 4. VERIFICACIÓN CRÍTICA - Tabla usuarios
        if 'usuarios' not in table_names:
            # DETENER SISTEMA CON ERROR CLARO
            error_msg = f"TABLA 'usuarios' NO EXISTE - Tablas detectadas: {table_names}"
            print(f"ERROR CRÍTICO: {error_msg}")
            print(f"SISTEMA DETENIDO - Base de datos: {current_db['current_database']}")
            
            cursor.close()
            conn.close()
            
            # Detener el sistema completamente
            raise SystemExit(error_msg)
        
        # 5. Validar acceso a tabla usuarios
        cursor.execute("SELECT COUNT(*) FROM usuarios;")
        result = cursor.fetchone()
        user_count = result['count']
        
        print(f"OK: TABLA 'usuarios' VALIDADA - {user_count} registros")
        
        cursor.close()
        conn.close()
        
        return {
            'status': True,
            'message': f'Esquema verificado - {user_count} usuarios',
            'database': current_db['current_database'],
            'tables': table_names,
            'user_count': user_count
        }
        
    except SystemExit:
        # Re-lanzar SystemExit para detener completamente
        raise
    except Exception as e:
        error_msg = f"Error en verificación de esquema: {e}"
        print(f"ERROR: {error_msg}")
        raise SystemExit(error_msg)

def verificar_estado_sistema():
    """Verificar estado del sistema al iniciar la aplicación"""
    try:
        print("=== VERIFICANDO ESTADO DEL SISTEMA ===")
        
        # Usar función de verificación y forzado
        resultado = verificar_y_forzar_schema()
        
        if resultado['status']:
            print(f"OK: Sistema operativo - {resultado['user_count']} usuarios en la BD")
            return {
                'status': True,
                'message': f'Sistema operativo - {resultado['user_count']} usuarios',
                'user_count': resultado['user_count']
            }
        else:
            return resultado
        
    except SystemExit as e:
        # El sistema fue detenido intencionalmente
        print(f"SISTEMA DETENIDO: {e}")
        return {
            'status': False,
            'message': str(e),
            'system_stopped': True
        }
    except Exception as e:
        error_msg = str(e)
        print(f"ERROR CRÍTICO DEL SISTEMA: {error_msg}")
        
        return {
            'status': False,
            'message': error_msg,
            'error': error_msg
        }

# Funciones específicas para Formación Complementaria
def guardar_nueva_formacion(nombre_taller, descripcion, fecha_inicio, fecha_fin, cupo_maximo, 
                           estado, cedula_usuario_creador, codigo_certificado, tomo, folio, facilitador):
    """Guardar nueva formación complementaria con transaccionalidad"""
    try:
        query_insert = """
        INSERT INTO formacion_complementaria 
        (nombre_taller, descripcion, fecha_inicio, fecha_fin, cupo_maximo, estado, 
         cedula_usuario_creador, codigo_certificado, tomo, folio, facilitador, cupo_actual)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
        RETURNING id_formacion
        """
        
        transaction_queries = [(query_insert, (
            nombre_taller, descripcion, fecha_inicio, fecha_fin, cupo_maximo, estado, 
            cedula_usuario_creador, codigo_certificado, tomo, folio, facilitador
        ))]
        
        result = execute_transaction(transaction_queries)
        
        if result.get('success', False):
            return {
                'success': True,
                'message': 'Formación complementaria creada exitosamente',
                'id_formacion': result.get('id_formacion')
            }
        else:
            return {
                'success': False,
                'message': 'Error al crear formación complementaria'
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al guardar formación: {str(e)}'
        }

def obtener_historial_formacion(limit=None):
    """Obtener historial de formaciones complementarias"""
    try:
        query = """
        SELECT id_formacion, nombre_taller, descripcion, fecha_inicio, fecha_fin, 
               cupo_maximo, cupo_actual, estado, codigo_certificado, tomo, folio, facilitador,
               cedula_usuario_creador, fecha_creacion
        FROM formacion_complementaria 
        ORDER BY fecha_creacion DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        result = execute_query(query, fetch_all=True)
        
        return {
            'success': True,
            'data': result if result else [],
            'count': len(result) if result else 0
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al obtener historial: {str(e)}',
            'data': [],
            'count': 0
        }

def actualizar_formacion(id_formacion, nombre_taller, descripcion, fecha_inicio, fecha_fin, 
                         cupo_maximo, estado, codigo_certificado, tomo, folio, facilitador):
    """Actualizar formación complementaria existente"""
    try:
        query_update = """
        UPDATE formacion_complementaria 
        SET nombre_taller = %s, descripcion = %s, fecha_inicio = %s, fecha_fin = %s,
            cupo_maximo = %s, estado = %s, codigo_certificado = %s, tomo = %s, 
            folio = %s, facilitador = %s
        WHERE id_formacion = %s
        """
        
        transaction_queries = [(query_update, (
            nombre_taller, descripcion, fecha_inicio, fecha_fin, cupo_maximo, estado,
            codigo_certificado, tomo, folio, facilitador, id_formacion
        ))]
        
        result = execute_transaction(transaction_queries)
        
        return {
            'success': result.get('success', False),
            'message': 'Formación actualizada exitosamente' if result.get('success', False) else 'Error al actualizar formación'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al actualizar formación: {str(e)}'
        }

def eliminar_formacion(id_formacion):
    """Eliminar formación complementaria con validaciones"""
    try:
        # Verificar si hay inscripciones activas
        inscripciones_query = """
        SELECT COUNT(*) as count FROM inscripcion 
        WHERE id_taller = %s AND estado_inscripcion = 'Activa'
        """
        
        inscripciones_result = execute_query(inscripciones_query, (id_formacion,), fetch_one=True)
        
        if inscripciones_result and inscripciones_result['count'] > 0:
            return {
                'success': False,
                'message': f'No se puede eliminar. Hay {inscripciones_result["count"]} inscripciones activas.'
            }
        
        # Eliminar formación
        query_delete = "DELETE FROM formacion_complementaria WHERE id_formacion = %s"
        
        transaction_queries = [(query_delete, (id_formacion,))]
        
        result = execute_transaction(transaction_queries)
        
        return {
            'success': result.get('success', False),
            'message': 'Formación eliminada exitosamente' if result.get('success', False) else 'Error al eliminar formación'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al eliminar formación: {str(e)}'
        }

def obtener_formacion_por_id(id_formacion):
    """Obtener detalles de una formación específica"""
    try:
        query = """
        SELECT * FROM formacion_complementaria WHERE id_formacion = %s
        """
        
        result = execute_query(query, (id_formacion,), fetch_one=True)
        
        return {
            'success': True,
            'data': result
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al obtener formación: {str(e)}',
            'data': None
        }

# Funciones de Gestión de Usuarios (integradas desde usuarios.py)
def obtener_usuarios_registrados():
    """Obtiene la lista de usuarios registrados desde la base de datos"""
    try:
        query = """
        SELECT cedula_usuario, login_usuario, rol, activo, 
               CASE WHEN activo THEN 'Activo' ELSE 'Inactivo' END as estado
        FROM usuarios 
        ORDER BY cedula_usuario
        """
        resultado = execute_query(query, fetch_all=True)
        
        if resultado:
            return resultado
        else:
            return []
            
    except Exception as e:
        print(f"Error obteniendo usuarios: {e}")
        return []

def verificar_cedula_existente(cedula):
    """Verifica si la cédula ya existe en la base de datos"""
    try:
        query = "SELECT COUNT(*) as count FROM usuarios WHERE cedula_usuario = %s"
        resultado = execute_query(query, (cedula.strip(),), fetch_one=True)
        
        if resultado:
            return resultado['count'] > 0
        
        return False
    except Exception as e:
        print(f"Error verificando cédula existente: {e}")
        return False

def hash_password_sha256(password):
    """Genera hash SHA-256 de la contraseña"""
    import hashlib
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def crear_usuario_transaccional(cedula_usuario, login_usuario, contrasena, rol, activo=True):
    """Crear usuario con transaccionalidad"""
    try:
        # Verificar si cédula ya existe
        if verificar_cedula_existente(cedula_usuario):
            return {
                'success': False,
                'message': 'La cédula ya está registrada en el sistema'
            }
        
        # Hash de contraseña
        contrasena_hash = hash_password_sha256(contrasena)
        
        # Insertar usuario
        query_insert = """
        INSERT INTO usuarios (cedula_usuario, login_usuario, contrasena, rol, activo)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        transaction_queries = [(query_insert, (cedula_usuario, login_usuario, contrasena_hash, rol, activo))]
        
        result = execute_transaction(transaction_queries)
        
        return {
            'success': result.get('success', False),
            'message': 'Usuario creado exitosamente' if result.get('success', False) else 'Error al crear usuario'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al crear usuario: {str(e)}'
        }

def actualizar_usuario_transaccional(cedula_usuario, login_usuario=None, rol=None, activo=None):
    """Actualizar usuario con transaccionalidad"""
    try:
        # Construir query dinámico
        campos_actualizar = []
        valores = []
        
        if login_usuario is not None:
            campos_actualizar.append("login_usuario = %s")
            valores.append(login_usuario)
        
        if rol is not None:
            campos_actualizar.append("rol = %s")
            valores.append(rol)
        
        if activo is not None:
            campos_actualizar.append("activo = %s")
            valores.append(activo)
        
        if not campos_actualizar:
            return {
                'success': False,
                'message': 'No se especificaron campos para actualizar'
            }
        
        valores.append(cedula_usuario)
        
        query_update = f"""
        UPDATE usuarios 
        SET {', '.join(campos_actualizar)}
        WHERE cedula_usuario = %s
        """
        
        transaction_queries = [(query_update, tuple(valores))]
        
        result = execute_transaction(transaction_queries)
        
        return {
            'success': result.get('success', False),
            'message': 'Usuario actualizado exitosamente' if result.get('success', False) else 'Error al actualizar usuario'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al actualizar usuario: {str(e)}'
        }

def eliminar_usuario_transaccional(cedula_usuario):
    """Eliminar usuario con validaciones"""
    try:
        # Verificar si existe
        if not verificar_cedula_existente(cedula_usuario):
            return {
                'success': False,
                'message': 'El usuario no existe en el sistema'
            }
        
        # No permitir eliminar administradores si es el único
        if cedula_usuario == 'admin':
            return {
                'success': False,
                'message': 'No se puede eliminar el usuario administrador principal'
            }
        
        # Eliminar usuario
        query_delete = "DELETE FROM usuarios WHERE cedula_usuario = %s"
        
        transaction_queries = [(query_delete, (cedula_usuario,))]
        
        result = execute_transaction(transaction_queries)
        
        return {
            'success': result.get('success', False),
            'message': 'Usuario eliminado exitosamente' if result.get('success', False) else 'Error al eliminar usuario'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al eliminar usuario: {str(e)}'
        }

# Motor Transaccional Central - Unificación de Operaciones
class MotorTransaccionalCentral:
    """Motor central de operaciones transaccionales para todo el sistema"""
    
    def __init__(self):
        """Inicialización del motor central"""
        self.db_manager = DatabaseManager()
    
    def operacion_crud_unificada(self, tabla, operacion, datos=None, filtros=None, orden=None):
        """Operación CRUD unificada para cualquier tabla"""
        try:
            if operacion.upper() == 'CREATE':
                return self._crear_registro(tabla, datos)
            elif operacion.upper() == 'READ':
                return self._leer_registros(tabla, filtros, orden)
            elif operacion.upper() == 'UPDATE':
                return self._actualizar_registro(tabla, datos, filtros)
            elif operacion.upper() == 'DELETE':
                return self._eliminar_registro(tabla, filtros)
            else:
                return {'success': False, 'message': f'Operación {operacion} no válida'}
        except Exception as e:
            return {'success': False, 'message': f'Error en {operacion}: {str(e)}'}
    
    def _crear_registro(self, tabla, datos):
        """Crear registro en cualquier tabla con transaccionalidad"""
        try:
            if not datos:
                return {'success': False, 'message': 'Datos requeridos para CREATE'}
            
            # Construir query dinámico
            columnas = list(datos.keys())
            valores = list(datos.values())
            placeholders = ', '.join(['%s'] * len(columnas))
            
            query_insert = f"""
            INSERT INTO {tabla} ({', '.join(columnas)})
            VALUES ({placeholders})
            """
            
            transaction_queries = [(query_insert, tuple(valores))]
            result = execute_transaction(transaction_queries)
            
            return {
                'success': result.get('success', False),
                'message': f'Registro creado en {tabla}' if result.get('success', False) else f'Error al crear en {tabla}'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error CREATE {tabla}: {str(e)}'}
    
    def _leer_registros(self, tabla, filtros=None, orden=None):
        """Leer registros de cualquier tabla"""
        try:
            query_base = f"SELECT * FROM {tabla}"
            valores = []
            
            # Agregar filtros
            if filtros:
                condiciones = []
                for campo, valor in filtros.items():
                    condiciones.append(f"{campo} = %s")
                    valores.append(valor)
                query_base += f" WHERE {' AND '.join(condiciones)}"
            
            # Agregar orden
            if orden:
                query_base += f" ORDER BY {orden}"
            
            resultado = execute_query(query_base, tuple(valores) if valores else None, fetch_all=True)
            
            return {
                'success': True,
                'data': resultado if resultado else [],
                'count': len(resultado) if resultado else 0
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error READ {tabla}: {str(e)}', 'data': []}
    
    def _actualizar_registro(self, tabla, datos, filtros):
        """Actualizar registro en cualquier tabla"""
        try:
            if not datos or not filtros:
                return {'success': False, 'message': 'Datos y filtros requeridos para UPDATE'}
            
            # Construir query dinámico
            campos_actualizar = []
            valores = []
            
            for campo, valor in datos.items():
                campos_actualizar.append(f"{campo} = %s")
                valores.append(valor)
            
            # Agregar filtros WHERE
            condiciones_where = []
            for campo, valor in filtros.items():
                condiciones_where.append(f"{campo} = %s")
                valores.append(valor)
            
            query_update = f"""
            UPDATE {tabla}
            SET {', '.join(campos_actualizar)}
            WHERE {' AND '.join(condiciones_where)}
            """
            
            transaction_queries = [(query_update, tuple(valores))]
            result = execute_transaction(transaction_queries)
            
            return {
                'success': result.get('success', False),
                'message': f'Registro actualizado en {tabla}' if result.get('success', False) else f'Error al actualizar en {tabla}'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error UPDATE {tabla}: {str(e)}'}
    
    def _eliminar_registro(self, tabla, filtros):
        """Eliminar registro de cualquier tabla"""
        try:
            if not filtros:
                return {'success': False, 'message': 'Filtros requeridos para DELETE'}
            
            # Construir query dinámico
            condiciones = []
            valores = []
            
            for campo, valor in filtros.items():
                condiciones.append(f"{campo} = %s")
                valores.append(valor)
            
            query_delete = f"""
            DELETE FROM {tabla}
            WHERE {' AND '.join(condiciones)}
            """
            
            transaction_queries = [(query_delete, tuple(valores))]
            result = execute_transaction(transaction_queries)
            
            return {
                'success': result.get('success', False),
                'message': f'Registro eliminado de {tabla}' if result.get('success', False) else f'Error al eliminar de {tabla}'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error DELETE {tabla}: {str(e)}'}
    
    def validar_permiso_usuario(self, rol_usuario, modulo, accion):
        """Validación centralizada de permisos"""
        try:
            from seguridad import tiene_permiso
            return tiene_permiso(rol_usuario, modulo, accion)
        except Exception as e:
            print(f"Error validando permiso: {e}")
            return False
    
    def ejecutar_consulta_personalizada(self, query, parametros=None, fetch_one=False):
        """Ejecutar consulta SQL personalizada"""
        try:
            resultado = execute_query(query, parametros, fetch_one=fetch_one)
            
            return {
                'success': True,
                'data': resultado
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error en consulta personalizada: {str(e)}',
                'data': None
            }

# Instancia global del motor central
motor_central = MotorTransaccionalCentral()

# Función de compatibilidad
def ensure_admin_exists():
    """Asegurar que exista un usuario administrador"""
    try:
        # Verificar si existe administrador
        result = execute_query(
            "SELECT COUNT(*) as count FROM usuarios WHERE rol = 'Administrador'",
            fetch_one=True
        )
        
        if result.get('count', 0) == 0:
            # Crear administrador por defecto
            admin_queries = [
                ("INSERT INTO persona (cedula, nombre_completo, telefono, direccion) VALUES (%s, %s, %s, %s)", 
                 ('V-00000000', 'Administrador del Sistema', '0000000000', 'N/A')),
                ("INSERT INTO usuarios (cedula_usuario, login_usuario, contrasena, rol, activo) VALUES (%s, %s, %s, %s, %s)",
                 ('V-00000000', 'admin', 'admin123', 'Administrador', True))
            ]
            
            resultado = ejecutar_transaccion(admin_queries)
            if resultado['success']:
                logger.info("Administrador por defecto creado exitosamente")
            else:
                logger.error(f"Error creando administrador: {resultado['message']}")
        else:
            logger.info("Administrador ya existe en el sistema")
            
    except Exception as e:
        logger.error(f"Error verificando administrador: {e}")

def authenticate_user(username, password):
    """Autenticar usuario en el sistema usando cédula como identificador único"""
    try:
        import hashlib
        import logging
        
        # Configurar logger para depuración
        logger = logging.getLogger(__name__)
        
        # LOG TEMPORAL: Verificar qué recibe la función
        logger.info(f"DEBUG: authenticate_user recibió - username: '{username}', password: '{password}'")
        
        # Limpieza del input de cédula
        cleaned_username = username.strip()
        logger.info(f"DEBUG: username después de strip(): '{cleaned_username}'")
        
        # Normalizar mayúsculas
        normalized_username = cleaned_username.upper()
        logger.info(f"DEBUG: username después de upper(): '{normalized_username}'")
        
        # Si es solo números, agregar V- al inicio
        if normalized_username.isdigit():
            normalized_username = f"V-{normalized_username}"
            logger.info(f"DEBUG: username normalizado a cédula: '{normalized_username}'")
        
        # Hashear la contraseña para comparación
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        logger.info(f"DEBUG: hash de contraseña: {hashed_password}")
        
        # Consulta SQL exacta por cédula o login_usuario
        query = """
        SELECT u.cedula_usuario, u.login_usuario, u.rol, u.activo, u.contrasena,
               p.nombre, p.apellido, p.telefono, p.direccion
        FROM usuarios u
        LEFT JOIN persona p ON u.cedula_usuario = p.cedula
        WHERE (u.cedula_usuario = %s OR u.login_usuario = %s) AND u.contrasena = %s AND u.activo = TRUE
        """
        
        logger.info(f"DEBUG: Ejecutando query con parámetros: ('{normalized_username}', '{cleaned_username}', '{hashed_password}')")
        
        # Primero buscar el usuario sin verificar contraseña para debug
        debug_query = """
        SELECT u.cedula_usuario, u.login_usuario, u.rol, u.activo, u.contrasena
        FROM usuarios u
        WHERE (u.cedula_usuario = %s OR u.login_usuario = %s) AND u.activo = TRUE
        """
        
        debug_result = execute_query(debug_query, (normalized_username, cleaned_username), fetch_one=True)
        
        if debug_result:
            logger.info(f"DEBUG: Usuario encontrado en BD:")
            logger.info(f"  - cedula_usuario: '{debug_result['cedula_usuario']}'")
            logger.info(f"  - login_usuario: '{debug_result['login_usuario']}'")
            logger.info(f"  - contrasena (hash): '{debug_result['contrasena']}'")
            logger.info(f"  - contrasena coincide: {debug_result['contrasena'] == hashed_password}")
        else:
            logger.warning(f"DEBUG: Usuario NO encontrado en BD con: '{normalized_username}' o '{cleaned_username}'")
        
        # Ejecutar consulta completa con verificación de contraseña
        try:
            result = execute_query(query, (normalized_username, cleaned_username, hashed_password), fetch_one=True)
        except Exception as e:
            logger.error(f"Error en execute_query final: {e}")
            raise
        
        logger.info(f"DEBUG: Resultado final de autenticación: {'EXITOSO' if result else 'FALLIDO'}")
        
        if result:
            # Combinar nombre y apellido para nombre_completo
            nombre_completo = f"{result.get('nombre', '')} {result.get('apellido', '')}".strip()
            
            logger.info(f"DEBUG: Autenticación exitosa para usuario: {result.get('login_usuario', 'N/A')}")
            
            return {
                'success': True,
                'user': {
                    'cedula_usuario': result['cedula_usuario'],
                    'login_usuario': result['login_usuario'],
                    'rol': result['rol'],
                    'nombre_completo': nombre_completo,
                    'telefono': result['telefono'],
                    'direccion': result['direccion']
                }
            }
        else:
            return {'success': False, 'message': 'Usuario o contraseña incorrectos'}
            
    except Exception as e:
        logger.error(f"Error en autenticación: {e}")
        return {'success': False, 'message': f'Error de autenticación: {str(e)}'}

if __name__ == "__main__":
    # Test del gestor de base de datos
    print("Testing DatabaseManager...")
    result = get_database_info()
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Database Info: {result['database_info']}")
    close_database()
