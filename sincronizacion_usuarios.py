"""
Script de Sincronización de Lista de Usuarios
Implementa filtro estricto y manejo robusto de conexiones SSL
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
import time

class SincronizadorUsuarios:
    """Clase para sincronización robusta de lista de usuarios"""

    def __init__(self):
        self.max_reintentos = 3
        self.timeout_conexion = 30

    def obtener_usuarios_activos_con_reintento(self) -> Optional[List[Dict]]:
        """
        Obtener lista de usuarios activos con filtro estricto y reintentos de conexión

        Returns:
            Lista de usuarios activos o None si falla
        """
        for intento in range(self.max_reintentos):
            try:
                usuarios = self._consultar_usuarios_activos()

                if usuarios is not None:
                    return usuarios

            except Exception as e:
                print(f"Intento {intento + 1} falló: {e}")

                if intento < self.max_reintentos - 1:
                    print(f"Reintentando en {2 ** intento} segundos...")
                    time.sleep(2 ** intento)  # Backoff exponencial
                else:
                    print("Todos los intentos fallaron")
                    return None

        return None

    def _consultar_usuarios_activos(self) -> Optional[List[Dict]]:
        """
        Consulta interna de usuarios activos con filtro estricto

        Returns:
            Lista de usuarios o None si error
        """
        try:
            from database import execute_query

            # FILTRO ESTRICTO: Solo usuarios con cédula existente y estado activo
            query = """
            SELECT
                u.cedula_usuario,
                u.login_usuario,
                u.rol,
                u.activo,
                COALESCE(p.nombre || ' ' || p.apellido, 'Sin nombre registrado') as nombre_completo
            FROM usuarios u
            LEFT JOIN persona p ON u.cedula_usuario = p.cedula
            WHERE u.activo = TRUE
            AND u.cedula_usuario IS NOT NULL
            AND TRIM(u.cedula_usuario) != ''
            ORDER BY u.rol, p.nombre, p.apellido
            """

            resultado = execute_query(query, fetch_all=True)

            if resultado is None:
                return None

            # Validar que cada usuario tenga cédula válida
            usuarios_validos = []
            for usuario in resultado:
                cedula = usuario.get('cedula_usuario', '').strip()
                if cedula and len(cedula) > 0:
                    # Asegurar tipo string para cédula
                    usuario['cedula_usuario'] = str(cedula)
                    usuarios_validos.append(usuario)

            return usuarios_validos

        except Exception as e:
            print(f"Error en consulta de usuarios: {e}")
            raise  # Re-lanzar para que el reintento lo capture

    def sincronizar_cache_usuarios(self) -> bool:
        """
        Sincronizar lista de usuarios con cache de Streamlit

        Returns:
            True si sincronización exitosa, False si falla
        """
        try:
            usuarios = self.obtener_usuarios_activos_con_reintento()

            if usuarios is not None:
                # Actualizar cache de Streamlit
                st.session_state.usuarios_activos_cache = usuarios
                st.session_state.usuarios_cache_timestamp = time.time()

                # Limpiar cache antiguo si existe
                if 'usuarios_activos' in st.session_state:
                    del st.session_state.usuarios_activos

                return True
            else:
                return False

        except Exception as e:
            print(f"Error en sincronización de cache: {e}")
            return False

    def obtener_usuarios_cacheados(self, max_edad_cache: int = 300) -> Optional[List[Dict]]:
        """
        Obtener usuarios desde cache si está fresco, sino sincronizar

        Args:
            max_edad_cache: Edad máxima del cache en segundos (default 5 minutos)

        Returns:
            Lista de usuarios o None
        """
        try:
            # Verificar si hay cache fresco
            if ('usuarios_activos_cache' in st.session_state and
                'usuarios_cache_timestamp' in st.session_state):

                edad_cache = time.time() - st.session_state.usuarios_cache_timestamp

                if edad_cache < max_edad_cache:
                    return st.session_state.usuarios_activos_cache

            # Cache no existe o está viejo, sincronizar
            if self.sincronizar_cache_usuarios():
                return st.session_state.usuarios_activos_cache
            else:
                return None

        except Exception as e:
            print(f"Error obteniendo usuarios cacheados: {e}")
            return None

# Función global para acceso fácil
def sincronizar_lista_usuarios() -> Optional[List[Dict]]:
    """
    Función global para sincronizar lista de usuarios con manejo de errores

    Returns:
        Lista de usuarios activos o None si falla
    """
    try:
        sincronizador = SincronizadorUsuarios()
        return sincronizador.obtener_usuarios_activos_con_reintento()
    except Exception as e:
        st.error(f"Error sincronizando lista de usuarios: {e}")
        return None

def obtener_usuarios_para_interfaz() -> pd.DataFrame:
    """
    Obtener usuarios formateados para interfaz de usuario

    Returns:
        DataFrame de pandas con usuarios formateados
    """
    try:
        sincronizador = SincronizadorUsuarios()
        usuarios = sincronizador.obtener_usuarios_cacheados()

        if usuarios:
            # Crear DataFrame
            df = pd.DataFrame(usuarios)

            # Renombrar columnas para interfaz
            df = df.rename(columns={
                'cedula_usuario': 'Cédula',
                'login_usuario': 'Usuario',
                'rol': 'Rol',
                'nombre_completo': 'Nombre Completo',
                'fecha_creacion': 'Fecha Creación',
                'ultimo_acceso': 'Último Acceso'
            })

            # Formatear fechas si existen
            if 'Fecha Creación' in df.columns:
                df['Fecha Creación'] = pd.to_datetime(df['Fecha Creación'], errors='coerce').dt.strftime('%Y-%m-%d')

            if 'Último Acceso' in df.columns:
                df['Último Acceso'] = pd.to_datetime(df['Último Acceso'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M')

            return df
        else:
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Error obteniendo usuarios para interfaz: {e}")
        return pd.DataFrame()

# Función para refresco forzado tras operaciones
def refresco_forzado_post_operacion():
    """
    Ejecutar refresco forzado tras operaciones de modificación de usuarios
    """
    try:
        # Limpiar caches relacionados con usuarios
        st.cache_data.clear()

        # Forzar sincronización
        sincronizador = SincronizadorUsuarios()
        sincronizador.sincronizar_cache_usuarios()

        # Pequeño delay para estabilidad
        time.sleep(0.5)

    except Exception as e:
        print(f"Error en refresco forzado: {e}")

if __name__ == "__main__":
    # Test del sincronizador
    print("Probando sincronizador de usuarios...")

    sincronizador = SincronizadorUsuarios()
    usuarios = sincronizador.obtener_usuarios_activos_con_reintento()

    if usuarios:
        print(f"✅ Sincronización exitosa: {len(usuarios)} usuarios encontrados")
        for u in usuarios[:3]:  # Mostrar primeros 3
            print(f"  - {u['cedula_usuario']}: {u['login_usuario']} ({u['rol']})")
    else:
        print("❌ Error en sincronización")