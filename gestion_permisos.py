#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gestion_permisos.py - Módulo de Gestión de Permisos (Exclusivo Administrador)
SICADFOC 2026 - Instituto Universitario Jesus Obrero
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any
from database import execute_query, ejecutar_transaccion
from seguridad import tiene_permiso

def requiere_administrador(func):
    """Decorador para requerir rol de Administrador"""
    def wrapper(*args, **kwargs):
        user_role = st.session_state.get('user_role', None)
        if user_role != 'Administrador':
            st.error("❌ Acceso denegado. Esta función está disponible solo para Administradores.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

class GestionPermisos:
    """Clase principal para gestión de permisos del sistema"""
    
    def __init__(self):
        self.user_role = st.session_state.get('user_role', None)
        self.user_cedula = st.session_state.get('user_cedula', None)
    
    @requiere_administrador
    def gestion_permisos(self):
        """Función principal del módulo de gestión de permisos"""
        try:
            st.header("🔐 Gestión de Permisos del Sistema")
            st.info("📋 Módulo exclusivo para Administradores - Configuración de permisos por rol y módulo")
            
            # Tabs para diferentes funcionalidades
            tab1, tab2 = st.tabs(["📋 Configuración de Permisos", "👥 Gestión de Roles"])
            
            with tab1:
                self.configurar_permisos()
            
            with tab2:
                self.gestionar_roles()
                
        except Exception as e:
            st.error(f"Error en módulo de permisos: {e}")
    
    def configurar_permisos(self):
        """Interfaz para configurar permisos con checkboxes"""
        st.subheader("⚙️ Configuración de Permisos por Rol")
        
        # Obtener roles y módulos del sistema
        roles = self.obtener_roles()
        modulos = self.obtener_modulos()
        acciones = ['Consultar', 'Registrar', 'Editar', 'Eliminar', 'Estadísticas']
        
        if not roles or not modulos:
            st.warning("No se pudieron cargar los roles o módulos del sistema.")
            return
        
        # Selector de rol
        rol_seleccionado = st.selectbox(
            "👤 Seleccionar Rol",
            options=roles,
            key="rol_permisos_selector"
        )
        
        if rol_seleccionado:
            st.markdown(f"### 📋 Configurando permisos para: **{rol_seleccionado}**")
            
            # Obtener permisos actuales del rol
            permisos_actuales = self.obtener_permisos_rol(rol_seleccionado)
            
            # Crear matriz de permisos
            st.markdown("#### 🎛️ Matriz de Permisos")
            
            permisos_a_actualizar = []
            
            for modulo in modulos:
                st.markdown(f"**📁 {modulo}**")
                
                cols = st.columns(len(acciones))
                for i, accion in enumerate(acciones):
                    with cols[i]:
                        # Verificar si el permiso ya existe
                        permiso_key = f"permiso_{rol_seleccionado}_{modulo}_{accion}"
                        permiso_existente = any(
                            p['rol'] == rol_seleccionado and 
                            p['modulo'] == modulo and 
                            p['accion'] == accion 
                            for p in permisos_actuales
                        )
                        
                        # Checkbox para el permiso
                        permiso_concedido = st.checkbox(
                            accion,
                            value=permiso_existente,
                            key=permiso_key,
                            help=f"Permitir {accion.lower()} en {modulo}"
                        )
                        
                        if permiso_concedido:
                            permisos_a_actualizar.append({
                                'rol': rol_seleccionado,
                                'modulo': modulo,
                                'accion': accion,
                                'acceso_limitado_propio': rol_seleccionado != 'Administrador'
                            })
                
                st.divider()
            
            # Botón para guardar cambios
            if st.button("💾 Guardar Cambios de Permisos", type="primary"):
                self.guardar_permisos(rol_seleccionado, permisos_a_actualizar)
    
    def gestionar_roles(self):
        """Gestión básica de roles"""
        st.subheader("👥 Gestión de Roles")
        
        roles = self.obtener_roles()
        
        if roles:
            st.markdown("#### 📋 Roles Actuales del Sistema")
            
            df_roles = pd.DataFrame(roles, columns=['Rol'])
            df_roles.index = df_roles.index + 1
            
            st.dataframe(df_roles, use_container_width=True)
            
            # Estadísticas de roles
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Roles", len(roles))
            
            with col2:
                total_permisos = sum(len(self.obtener_permisos_rol(rol)) for rol in roles)
                st.metric("Total Permisos Configurados", total_permisos)
        else:
            st.info("No hay roles configurados en el sistema.")
    
    def obtener_roles(self) -> List[str]:
        """Obtener la lista de roles del sistema"""
        try:
            query = """
            SELECT DISTINCT nombre_rol as rol 
            FROM configuracion_permisos 
            WHERE nombre_rol IS NOT NULL 
            ORDER BY nombre_rol
            """
            resultado = execute_query(query)
            
            if resultado and (isinstance(resultado, list) and len(resultado) > 0 or isinstance(resultado, dict)):
                roles_list = resultado if isinstance(resultado, list) else [resultado]
                return [rol['rol'] for rol in roles_list]
            
            # Roles por defecto si no hay en BD
            return ['Administrador', 'Profesor', 'Estudiante']
            
        except Exception as e:
            st.error(f"Error obteniendo roles: {e}")
            return ['Administrador', 'Profesor', 'Estudiante']
    
    def obtener_modulos(self) -> List[str]:
        """Obtener la lista de módulos del sistema"""
        try:
            query = """
            SELECT DISTINCT nombre_modulo as modulo 
            FROM configuracion_permisos 
            WHERE nombre_modulo IS NOT NULL 
            ORDER BY nombre_modulo
            """
            resultado = execute_query(query)
            
            if resultado and (isinstance(resultado, list) and len(resultado) > 0 or isinstance(resultado, dict)):
                modulos_list = resultado if isinstance(resultado, list) else [resultado]
                return [mod['modulo'] for mod in modulos_list]
            
            # Módulos por defecto si no hay en BD
            return [
                'Gestión Profesores',
                'Gestión Estudiantes', 
                'Formación Complementaria',
                'Gestión Carreras',
                'Reportes',
                'Configuración'
            ]
            
        except Exception as e:
            st.error(f"Error obteniendo módulos: {e}")
            return [
                'Gestión Profesores',
                'Gestión Estudiantes', 
                'Formación Complementaria',
                'Gestión Carreras',
                'Reportes',
                'Configuración'
            ]
    
    def obtener_permisos_rol(self, rol: str) -> List[Dict]:
        """Obtener permisos actuales de un rol específico"""
        try:
            query = """
            SELECT rol, modulo, accion, acceso_limitado_propio
            FROM configuracion_permisos 
            WHERE rol = %s
            """
            resultado = execute_query(query, (rol,))
            
            if resultado and (isinstance(resultado, list) and len(resultado) > 0 or isinstance(resultado, dict)):
                return resultado if isinstance(resultado, list) else [resultado]
            
            return []
            
        except Exception as e:
            st.error(f"Error obteniendo permisos del rol {rol}: {e}")
            return []
    
    def guardar_permisos(self, rol: str, permisos: List[Dict]):
        """Guardar configuración de permisos para un rol"""
        try:
            # Iniciar transacción
            queries = []
            
            # Eliminar permisos existentes del rol
            queries.append((
                "DELETE FROM configuracion_permisos WHERE rol = %s",
                (rol,)
            ))
            
            # Insertar nuevos permisos
            for permiso in permisos:
                queries.append((
                    """
                    INSERT INTO configuracion_permisos 
                    (rol, modulo, accion, acceso_limitado_propio) 
                    VALUES (%s, %s, %s, %s)
                    """,
                    (permiso['rol'], permiso['modulo'], permiso['accion'], permiso['acceso_limitado_propio'])
                ))
            
            # Ejecutar transacción
            resultado = ejecutar_transaccion(queries)
            
            if resultado['success']:
                st.success(f"Permisos del rol '{rol}' actualizados correctamente.")
                st.balloons()
                
                # Limpiar caché de permisos
                if 'cache_permisos' in st.session_state:
                    del st.session_state['cache_permisos']
            else:
                st.error(f"Error actualizando permisos: {resultado['message']}")
                
        except Exception as e:
            st.error(f"Error en la operación: {e}")

def mostrar_gestion_permisos():
    """Función principal para mostrar el módulo de gestión de permisos"""
    if not tiene_permiso(st.session_state.get('user_role'), 'Configuración', 'Consultar'):
        st.error("❌ No tienes permisos para acceder a la configuración del sistema.")
        return

    gestor = GestionPermisos()
    gestor.gestion_permisos()

def gestion_permisos():
    """Función principal del módulo de gestión de permisos (compatibilidad)"""
    try:
        if not tiene_permiso(st.session_state.get('user_role'), 'Configuración', 'Consultar'):
            st.error("No tienes permisos para acceder a la configuración del sistema.")
            return

        gestor = GestionPermisos()
        gestor.gestion_permisos()
    except Exception as e:
        st.error(f"Error en el módulo de gestión de permisos: {e}")
