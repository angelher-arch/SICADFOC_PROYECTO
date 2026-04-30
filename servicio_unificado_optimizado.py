#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
servicio_unificado_optimizado.py - SERVICIO CENTRALIZADO UNIFICADO (OPTIMIZADO)
SICADFOC 2026 - Instituto Universitario Jesus Obrero

Este servicio unifica:
1. Configuracion dual (local/produccion)
2. Lectura-escritura de base de datos con optimización de conexiones
3. Compatibilidad de esquemas
4. Manejo de errores centralizado
5. Cache y optimización
6. Gestión eficiente de conexiones para evitar "too many clients"
"""

import os
import logging
import json
import threading
import time
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import OperationalError
from dotenv import load_dotenv

# Configuracion de logging centralizada
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfiguracionDual:
    """Gestor de configuracion dual local/produccion"""
    
    def __init__(self):
        self._entorno = None
        self._config = {}
        self._detectar_entorno()
        self._cargar_configuracion()
    
    def _detectar_entorno(self):
        """Detecta automaticamente el entorno"""
        database_url = os.getenv('DATABASE_URL')
        
        if database_url and ('render.com' in database_url or 'railway.app' in database_url):
            self._entorno = 'produccion'
            logger.info("=== ENTORNO DE PRODUCCION DETECTADO ===")
        else:
            self._entorno = 'local'
            logger.info("=== ENTORNO LOCAL DETECTADO ===")
    
    def _cargar_configuracion(self):
        """Carga configuracion segun entorno"""
        if self._entorno == 'produccion':
            self._config = self._config_produccion()
        else:
            self._config = self._config_local()
    
    def _config_produccion(self) -> Dict[str, Any]:
        """Configuracion para produccion"""
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            raise ValueError("DATABASE_URL es requerido en produccion")
        
        # Parsear DATABASE_URL
        import urllib.parse
        parsed = urllib.parse.urlparse(database_url)
        
        return {
            'database_url': database_url,
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path.lstrip('/'),
            'user': parsed.username,
            'password': parsed.password,
            'sslmode': 'require',
            'connection_timeout': 30,
            'query_timeout': 30,
            'debug': False,
            'log_queries': False,
            'max_pool_size': 3,  # Reducido para producción
            'connection_ttl': 300  # 5 minutos TTL por conexión
        }
    
    def _config_local(self) -> Dict[str, Any]:
        """Configuracion para desarrollo local"""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'db_foc26'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'sslmode': os.getenv('DB_SSLMODE', 'prefer'),
            'connection_timeout': 10,
            'query_timeout': 20,
            'debug': os.getenv('DEBUG', 'False').lower() == 'true',
            'log_queries': os.getenv('LOG_QUERIES', 'False').lower() == 'true',
            'max_pool_size': 2,  # Reducido para desarrollo local
            'connection_ttl': 180  # 3 minutos TTL por conexión
        }
    
    @property
    def es_produccion(self) -> bool:
        return self._entorno == 'produccion'
    
    @property
    def es_local(self) -> bool:
        return self._entorno == 'local'
    
    def get(self, key: str, default=None):
        """Obtener valor de configuracion"""
        return self._config.get(key, default)
    
    def obtener_columna_cedula(self) -> str:
        """Retorna el nombre correcto de la columna de cedula segun entorno"""
        return 'cedula' if self.es_produccion else 'cedula_usuario'

class ConnectionPool:
    """Pool de conexiones optimizado para evitar 'too many clients'"""
    
    def __init__(self, max_size: int = 2, connection_ttl: int = 300):
        self.max_size = max_size
        self.connection_ttl = connection_ttl
        self._pool = []
        self._pool_lock = threading.Lock()
        self._created_connections = 0
        
    def _create_connection(self):
        """Crea una nueva conexión a la base de datos"""
        from servicio_unificado_optimizado import obtener_servicio
        servicio = obtener_servicio()
        config = servicio.config
        
        try:
            if config.es_produccion:
                conn = psycopg2.connect(
                    dsn=config.get('database_url'),
                    connect_timeout=config.get('connection_timeout', 30),
                    application_name='SICADFOC_2026'
                )
            else:
                conn = psycopg2.connect(
                    host=config.get('host'),
                    port=config.get('port'),
                    database=config.get('database'),
                    user=config.get('user'),
                    password=config.get('password'),
                    sslmode=config.get('sslmode'),
                    connect_timeout=config.get('connection_timeout', 10),
                    application_name='SICADFOC_2026'
                )
            
            # Configurar conexión para optimización
            conn.autocommit = False
            conn.set_session(isolation_level='READ COMMITTED')
            
            self._created_connections += 1
            logger.info(f"Nueva conexión creada. Total creadas: {self._created_connections}")
            
            return conn
            
        except Exception as e:
            logger.error(f"Error creando conexión: {e}")
            raise
    
    def _is_connection_valid(self, conn) -> bool:
        """Verifica si una conexión es válida y no está cerrada"""
        try:
            if conn is None or conn.closed:
                return False
            
            # Verificar si la conexión está respondiendo
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
                
        except Exception:
            return False
    
    def _cleanup_expired_connections(self):
        """Limpia conexiones expiradas o inválidas"""
        current_time = time.time()
        connections_to_remove = []
        
        for conn_info in self._pool:
            conn, created_time = conn_info
            age = current_time - created_time
            
            # Remover si expiró o es inválida
            if age > self.connection_ttl or not self._is_connection_valid(conn):
                connections_to_remove.append(conn_info)
                try:
                    if not conn.closed:
                        conn.close()
                except Exception:
                    pass
        
        # Remover del pool
        for conn_info in connections_to_remove:
            self._pool.remove(conn_info)
            logger.info(f"Conexión limpiada del pool. Pool size: {len(self._pool)}")
    
    def get_connection(self):
        """Obtiene una conexión del pool o crea una nueva"""
        with self._pool_lock:
            # Limpiar conexiones expiradas
            self._cleanup_expired_connections()
            
            # Buscar conexión válida en el pool
            for conn_info in self._pool:
                conn, created_time = conn_info
                if self._is_connection_valid(conn):
                    # Remover del pool temporalmente
                    self._pool.remove(conn_info)
                    return conn
            
            # Si no hay conexiones válidas y podemos crear más
            if len(self._pool) < self.max_size:
                return self._create_connection()
            
            # Si el pool está lleno pero no hay conexiones válidas
            raise Exception("No hay conexiones disponibles en el pool")
    
    def return_connection(self, conn):
        """Devuelve una conexión al pool"""
        with self._pool_lock:
            if conn is not None and not conn.closed and self._is_connection_valid(conn):
                # Resetear estado de la conexión
                try:
                    conn.rollback()  # Asegurar que no haya transacciones pendientes
                    self._pool.append((conn, time.time()))
                except Exception as e:
                    logger.warning(f"Error devolviendo conexión al pool: {e}")
                    try:
                        conn.close()
                    except Exception:
                        pass
            else:
                # Cerrar conexión inválida
                try:
                    conn.close()
                except Exception:
                    pass
    
    def close_all_connections(self):
        """Cierra todas las conexiones del pool"""
        with self._pool_lock:
            for conn, _ in self._pool:
                try:
                    if not conn.closed:
                        conn.close()
                except Exception:
                    pass
            self._pool.clear()
            logger.info("Todas las conexiones del pool han sido cerradas")

class GestorBaseDatosUnificado:
    """Gestor unificado de base de datos con pool de conexiones optimizado"""
    
    def __init__(self, configuracion: ConfiguracionDual):
        self.config = configuracion
        self._pool = ConnectionPool(
            max_size=self.config.get('max_pool_size', 1),
            connection_ttl=self.config.get('connection_ttl', 180)
        )
        self._validar_conexion()
    
    def _validar_conexion(self):
        """Valida la conexion al iniciar"""
        try:
            conn = self._pool.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 as test")
                resultado = cursor.fetchone()
            self._pool.return_connection(conn)
            
            if resultado:
                logger.info("Conexion a base de datos validada exitosamente")
            else:
                logger.warning("Conexion valida pero sin resultados")
        except Exception as e:
            logger.error(f"Error validando conexion: {e}")
            raise
    
    def ejecutar_query(self, query: str, params: Optional[Tuple] = None, 
                      fetch_one: bool = False, fetch_all: bool = True) -> Union[Dict, List, int]:
        """Ejecuta query con manejo unificado de errores y compatibilidad"""
        
        if self.config.get('log_queries'):
            logger.info(f"QUERY: {query}")
            logger.info(f"PARAMS: {params}")
        
        conn = None
        try:
            conn = self._pool.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params or ())
                
                if fetch_one:
                    resultado = cursor.fetchone()
                elif fetch_all:
                    resultado = cursor.fetchall()
                else:
                    resultado = cursor.rowcount
                
                conn.commit()
                
                # Adaptar resultados para compatibilidad
                if isinstance(resultado, list):
                    resultado = [self._adaptar_resultado(item) for item in resultado]
                elif isinstance(resultado, dict):
                    resultado = self._adaptar_resultado(resultado)
                
                return resultado
                
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error en query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            
            # Intentar con esquema alternativo
            return self._intentar_esquema_alternativo(query, params, fetch_one, fetch_all)
        finally:
            if conn:
                self._pool.return_connection(conn)
    
    def _adaptar_resultado(self, resultado: Dict) -> Dict:
        """Adapta resultado para estandarizar nombres de columnas"""
        if not isinstance(resultado, dict):
            return resultado
        
        # Estandarizar siempre a 'cedula'
        if 'cedula_usuario' in resultado:
            resultado['cedula'] = resultado.pop('cedula_usuario')
        elif 'cedula' in resultado and self.config.es_local:
            # Si estamos en local y viene 'cedula', mantenerla
            pass
        
        return resultado
    
    def _intentar_esquema_alternativo(self, query: str, params: Tuple = None, fetch_one: bool = False, fetch_all: bool = False):
        """Intentar ejecutar query con esquema alternativo si el principal falla"""
        if self.config.es_produccion:
            # Estamos en produccion, intentar con esquema local
            query_alt = query.replace('u.cedula', 'u.cedula_usuario')
            query_alt = query_alt.replace('usuarios.cedula', 'usuarios.cedula_usuario')
        else:
            # Estamos en local, intentar con esquema de produccion
            query_alt = query.replace('u.cedula_usuario', 'u.cedula')
            query_alt = query_alt.replace('usuarios.cedula_usuario', 'usuarios.cedula')
        
        try:
            logger.info("Intentando esquema alternativo...")
            # Ejecutar directamente sin recursión
            conn = self._pool.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query_alt, params or ())
                
                if fetch_one:
                    resultado = cursor.fetchone()
                elif fetch_all:
                    resultado = cursor.fetchall()
                else:
                    resultado = None
                    
                conn.commit()
                return resultado
            
        except Exception as e2:
            logger.error(f"Error tambien con esquema alternativo: {e2}")
            raise e2  # Lanzar el error del esquema alternativo
    
    def ejecutar_transaccion(self, queries_params: List[Tuple[str, Tuple]]) -> bool:
        """Ejecuta multiples queries en una transaccion"""
        
        conn = None
        try:
            conn = self._pool.get_connection()
            with conn.cursor() as cursor:
                for query, params in queries_params:
                    if self.config.get('log_queries'):
                        logger.info(f"TRANSACCION QUERY: {query}")
                        logger.info(f"TRANSACCION PARAMS: {params}")
                    
                    cursor.execute(query, params or ())
                
                conn.commit()
                return True
                
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error en transaccion: {e}")
            return False
        finally:
            if conn:
                self._pool.return_connection(conn)
    
    def construir_join_persona(self, alias_usuarios='u', alias_persona='p') -> str:
        """Construye JOIN compatible con ambos entornos"""
        columna_cedula = self.config.obtener_columna_cedula()
        
        return (f"LEFT JOIN persona {alias_persona} "
                f"ON CAST({alias_usuarios}.{columna_cedula} AS VARCHAR) = "
                f"CAST({alias_persona}.cedula AS VARCHAR)")
    
    def construir_select_usuarios(self, columnas_adicionales: List[str] = None) -> str:
        """Construye SELECT de usuarios compatible"""
        columna_cedula = self.config.obtener_columna_cedula()
        
        columnas_base = [
            f"u.{columna_cedula} as cedula",
            "u.login_usuario",
            "u.rol",
            "u.activo",
            "u.email"
        ]
        
        if columnas_adicionales:
            columnas_base.extend(columnas_adicionales)
        
        return ", ".join(columnas_base)
    
    def cleanup(self):
        """Limpia recursos del gestor de base de datos"""
        self._pool.close_all_connections()

class CacheUnificado:
    """Cache centralizado con soporte para multiples estrategias"""
    
    def __init__(self):
        self._cache = {}
        self._cache_timestamps = {}
        self._ttl = 300  # 5 minutos por defecto
    
    def get(self, key: str) -> Optional[Any]:
        """Obtener valor del cache"""
        if key not in self._cache:
            return None
        
        # Verificar TTL
        if key in self._cache_timestamps:
            if datetime.now().timestamp() - self._cache_timestamps[key] > self._ttl:
                self.delete(key)
                return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Establecer valor en cache"""
        self._cache[key] = value
        self._cache_timestamps[key] = datetime.now().timestamp()
        
        if ttl:
            self._ttl = ttl
    
    def delete(self, key: str):
        """Eliminar del cache"""
        self._cache.pop(key, None)
        self._cache_timestamps.pop(key, None)
    
    def clear(self):
        """Limpiar todo el cache"""
        self._cache.clear()
        self._cache_timestamps.clear()

class ServicioUnificado:
    """SERVICIO CENTRALIZADO UNIFICADO - Punto unico de acceso (OPTIMIZADO)"""
    
    _instancia = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instancia is None:
            with cls._lock:
                if cls._instancia is None:
                    cls._instancia = super().__new__(cls)
        return cls._instancia
    
    def __init__(self):
        if not hasattr(self, '_inicializado'):
            self._inicializado = True
            self.config = ConfiguracionDual()
            self.db = GestorBaseDatosUnificado(self.config)
            self.cache = CacheUnificado()
            
            # Registrar cleanup al salir
            import atexit
            atexit.register(self.cleanup)
    
    def cleanup(self):
        """Limpia recursos del servicio"""
        try:
            self.db.cleanup()
            logger.info("Recursos del servicio unificado limpiados")
        except Exception as e:
            logger.error(f"Error en cleanup: {e}")
    
    # Metodos de conveniencia para configuracion
    @property
    def es_produccion(self) -> bool:
        return self.config.es_produccion
    
    @property
    def es_local(self) -> bool:
        return self.config.es_local
    
    def obtener_columna_cedula(self) -> str:
        return self.config.obtener_columna_cedula()
    
    # Metodos de base de datos unificados
    def ejecutar_query(self, query: str, params: Optional[Tuple] = None, 
                      fetch_one: bool = False, fetch_all: bool = True) -> Union[Dict, List, int]:
        """Ejecuta query con cache opcional"""
        cache_key = f"query:{hash(query)}:{str(params)}" if params else f"query:{hash(query)}"
        
        # Solo usar cache para consultas de lectura
        if query.strip().upper().startswith('SELECT') and not self.config.get('debug'):
            resultado_cache = self.cache.get(cache_key)
            if resultado_cache is not None:
                return resultado_cache
        
        resultado = self.db.ejecutar_query(query, params, fetch_one, fetch_all)
        
        # Guardar en cache solo si es SELECT
        if query.strip().upper().startswith('SELECT') and not self.config.get('debug'):
            self.cache.set(cache_key, resultado)
        
        return resultado
    
    def ejecutar_transaccion(self, queries_params: List[Tuple[str, Tuple]]) -> bool:
        """Ejecuta transaccion y limpia cache relevante"""
        resultado = self.db.ejecutar_transaccion(queries_params)
        
        # Limpiar cache si la transaccion fue exitosa
        if resultado:
            self.cache.clear()
        
        return resultado
    
    # Metodos de construccion SQL compatibles
    def construir_join_persona(self, alias_usuarios='u', alias_persona='p') -> str:
        return self.db.construir_join_persona(alias_usuarios, alias_persona)
    
    def construir_select_usuarios(self, columnas_adicionales: List[str] = None) -> str:
        return self.db.construir_select_usuarios(columnas_adicionales)
    
    # Metodos de utilidad
    def test_conexion(self) -> Dict[str, Any]:
        """Prueba completa de conexion"""
        try:
            # Test basico
            resultado = self.db.ejecutar_query("SELECT 1 as test", fetch_one=True)
            
            # Test de tabla usuarios
            usuarios = self.db.ejecutar_query(
                f"SELECT COUNT(*) as total FROM usuarios WHERE {self.obtener_columna_cedula()} IS NOT NULL",
                fetch_one=True
            )
            
            return {
                'status': True,
                'entorno': self.config._entorno,
                'test_query': resultado is not None,
                'usuarios_registrados': usuarios.get('total', 0) if usuarios else 0,
                'config': {
                    'database': self.config.get('database'),
                    'host': self.config.get('host'),
                    'port': self.config.get('port'),
                    'columna_cedula': self.obtener_columna_cedula(),
                    'max_pool_size': self.config.get('max_pool_size'),
                    'connection_ttl': self.config.get('connection_ttl')
                }
            }
            
        except Exception as e:
            return {
                'status': False,
                'error': str(e),
                'entorno': self.config._entorno
            }

# Instancia global del servicio unificado (lazy initialization)
servicio_unificado = None

def obtener_servicio() -> ServicioUnificado:
    """Obtener instancia del servicio unificado (lazy initialization)"""
    global servicio_unificado
    if servicio_unificado is None:
        servicio_unificado = ServicioUnificado()
    return servicio_unificado

def ejecutar_query(query: str, params: Optional[Tuple] = None, 
                  fetch_one: bool = False, fetch_all: bool = True) -> Union[Dict, List, int]:
    """Ejecutar query usando el servicio unificado"""
    servicio = obtener_servicio()
    return servicio.ejecutar_query(query, params, fetch_one, fetch_all)

def ejecutar_transaccion(queries_params: List[Tuple[str, Tuple]]) -> bool:
    """Ejecutar transaccion usando el servicio unificado"""
    servicio = obtener_servicio()
    return servicio.ejecutar_transaccion(queries_params)

def obtener_columna_cedula() -> str:
    """Obtener nombre de columna de cedula segun entorno"""
    servicio = obtener_servicio()
    return servicio.obtener_columna_cedula()

def construir_join_persona(alias_usuarios='u', alias_persona='p') -> str:
    """Construir JOIN compatible usando el servicio unificado"""
    servicio = obtener_servicio()
    return servicio.construir_join_persona(alias_usuarios, alias_persona)

def es_produccion() -> bool:
    """Verificar si estamos en produccion"""
    servicio = obtener_servicio()
    return servicio.es_produccion

def es_local() -> bool:
    """Verificar si estamos en local"""
    servicio = obtener_servicio()
    return servicio.es_local

def test_conexion() -> Dict[str, Any]:
    """Probar conexion usando el servicio unificado"""
    servicio = obtener_servicio()
    return servicio.test_conexion()

def limpiar_conexiones():
    """Función utilitaria para limpiar todas las conexiones"""
    global servicio_unificado
    if servicio_unificado:
        servicio_unificado.cleanup()
        servicio_unificado = None
