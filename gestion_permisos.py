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
            tab1, tab2, tab3 = st.tabs(["📋 Configuración de Permisos", "� Reporte de Permisos", "� Gestión de Roles"])
            
            with tab1:
                self.configurar_permisos()
            
            with tab2:
                self.reporte_permisos()
            
            with tab3:
                self.gestionar_roles()
                
        except Exception as e:
            st.error(f"Error en módulo de permisos: {e}")
    
    def configurar_permisos(self):
        """Interfaz RBAC para configurar permisos con matriz de checkboxes"""
        st.subheader("🔐 Control de Acceso Basado en Roles (RBAC)")

        # Definir módulos del sistema
        modulos_sistema = [
            "Gestión Estudiantil",
            "Gestión Profesores",
            "Registro Estudiantes",
            "Registro Profesores",
            "Formación Complementaria",
            "Inscripciones Unificadas",
            "Gestión Formación Complementaria",
            "Certificados",
            "Reportes",
            "Gestión Usuarios",
            "Registrar Usuario",
            "Gestión de Permisos",
            "Gestión Carreras"
        ]

        # Definir acciones
        acciones = ['puede_ver', 'puede_consultar', 'puede_editar', 'puede_eliminar']
        acciones_display = ['Ver', 'Consultar', 'Editar', 'Eliminar']

        # Obtener roles del sistema (excluyendo Administrador que siempre tiene acceso total)
        roles = ['Profesor', 'Estudiante']

        st.markdown("### 👥 Configuración de Permisos por Rol")
        st.info("💡 Como Administrador, tienes acceso total automático. Configura permisos para otros roles:")

        # Procesar cada rol
        for rol in roles:
            st.markdown(f"#### 🎭 Rol: **{rol}**")

            # Obtener permisos actuales del rol
            permisos_actuales = self.obtener_permisos_rbac_rol(rol)

            # Crear diccionario de permisos actuales para fácil acceso
            permisos_dict = {}
            for p in permisos_actuales:
                key = p['modulo_nombre']
                permisos_dict[key] = {
                    'puede_ver': p.get('puede_ver', False),
                    'puede_consultar': p.get('puede_consultar', False),
                    'puede_editar': p.get('puede_editar', False),
                    'puede_eliminar': p.get('puede_eliminar', False)
                }

            # Crear tabla/matriz de permisos
            permisos_actualizar = {}

            # Header de la tabla
            col_modulo, *cols_acciones = st.columns([3] + [1] * len(acciones))
            with col_modulo:
                st.markdown("**📁 Módulo**")
            for i, accion_display in enumerate(acciones_display):
                with cols_acciones[i]:
                    st.markdown(f"**{accion_display}**")

            st.markdown("---")

            # Filas para cada módulo
            for modulo in modulos_sistema:
                col_modulo, *cols_acciones = st.columns([3] + [1] * len(acciones))

                with col_modulo:
                    st.markdown(f"**{modulo}**")

                modulo_permisos = permisos_dict.get(modulo, {
                    'puede_ver': False,
                    'puede_consultar': False,
                    'puede_editar': False,
                    'puede_eliminar': False
                })

                permisos_actualizar[modulo] = {}

                for i, (accion, accion_display) in enumerate(zip(acciones, acciones_display)):
                    with cols_acciones[i]:
                        valor_actual = modulo_permisos.get(accion, False)
                        nuevo_valor = st.checkbox(
                            "",
                            value=valor_actual,
                            key=f"{rol}_{modulo}_{accion}",
                            label_visibility="collapsed"
                        )
                        permisos_actualizar[modulo][accion] = nuevo_valor

            # Botón para guardar permisos del rol
            if st.button(f"💾 Guardar Permisos para {rol}", type="primary", key=f"guardar_{rol}"):
                self.guardar_permisos_rbac(rol, permisos_actualizar)
                st.success(f"✅ Permisos actualizados para el rol {rol}")
                st.rerun()

            st.markdown("---")
    
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
            SELECT DISTINCT rol 
            FROM configuracion_permisos 
            WHERE rol IS NOT NULL 
            ORDER BY rol
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
            # Módulos actualizados del sistema basados en auditoría
            return [
                'Gestión Estudiantil',
                'Gestión Profesores', 
                'Formación Complementaria',
                'Inscripciones',
                'Gestión Carreras',
                'Solicitud Formación Complementaria',
                'Gestión Solicitud Formación Complementaria',
                'Editor de Certificados',
                'Reportes',
                'Gestión Usuarios',
                'Registrar Usuario',
                'Gestión de Permisos'
            ]
            
        except Exception as e:
            st.error(f"Error obteniendo módulos: {e}")
            return [
                'Gestión Estudiantil',
                'Gestión Profesores', 
                'Formación Complementaria',
                'Inscripciones',
                'Gestión Carreras',
                'Solicitud Formación Complementaria',
                'Gestión Solicitud Formación Complementaria',
                'Editor de Certificados',
                'Reportes'
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
    
    def reporte_permisos(self):
        """Reporte de permisos actuales por usuario"""
        st.subheader("📊 Reporte de Permisos Actuales")
        
        try:
            # Obtener todos los usuarios con sus roles
            query_usuarios = """
            SELECT u.cedula_usuario, u.login_usuario, u.rol, p.nombre, p.apellido
            FROM usuarios u
            LEFT JOIN persona p ON u.cedula_usuario = p.cedula
            WHERE u.activo = true
            ORDER BY u.rol, p.apellido, p.nombre
            """
            usuarios = execute_query(query_usuarios)
            
            if not usuarios:
                st.info("No hay usuarios activos en el sistema.")
                return
            
            # Obtener todos los permisos configurados
            query_permisos = """
            SELECT rol, modulo, accion
            FROM configuracion_permisos 
            ORDER BY rol, modulo, accion
            """
            permisos_config = execute_query(query_permisos)
            
            if not permisos_config:
                st.info("No hay permisos configurados en el sistema.")
                return
            
            # Crear reporte por usuario
            st.markdown("#### 📋 Permisos por Usuario")
            
            for usuario in usuarios:
                with st.expander(f"👤 {usuario['nombre']} {usuario['apellido']} ({usuario['rol']}) - {usuario['cedula_usuario']}"):
                    
                    # Filtrar permisos para este rol
                    permisos_usuario = [p for p in permisos_config if p['rol'] == usuario['rol']]
                    
                    if permisos_usuario:
                        # Agrupar por módulo
                        modulos_usuario = {}
                        for permiso in permisos_usuario:
                            if permiso['modulo'] not in modulos_usuario:
                                modulos_usuario[permiso['modulo']] = []
                            modulos_usuario[permiso['modulo']].append(permiso['accion'])
                        
                        # Mostrar por módulo
                        for modulo, acciones in modulos_usuario.items():
                            st.markdown(f"**📁 {modulo}**: {', '.join(acciones)}")
                    else:
                        st.info("No tiene permisos configurados.")
            
            # Estadísticas generales
            st.markdown("#### 📈 Estadísticas de Permisos")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Usuarios", len(usuarios))
            
            with col2:
                st.metric("Total Permisos", len(permisos_config))
            
            with col3:
                roles_unicos = len(set(u['rol'] for u in usuarios))
                st.metric("Total Roles", roles_unicos)
            
            with col4:
                modulos_unicos = len(set(p['modulo'] for p in permisos_config))
                st.metric("Módulos con Permisos", modulos_unicos)
            
            # Tabla resumen
            st.markdown("#### 📋 Tabla Resumen de Permisos")
            
            # Crear DataFrame para tabla
            datos_tabla = []
            for permiso in permisos_config:
                datos_tabla.append({
                    'Rol': permiso['rol'],
                    'Módulo': permiso['modulo'],
                    'Acción': permiso['accion']
                })
            
            if datos_tabla:
                df_permisos = pd.DataFrame(datos_tabla)
                st.dataframe(df_permisos, use_container_width=True)
                
                # Botón para exportar
                if st.button("📥 Exportar Reporte CSV"):
                    csv = df_permisos.to_csv(index=False)
                    st.download_button(
                        label="Descargar reporte_permisos.csv",
                        data=csv,
                        file_name="reporte_permisos.csv",
                        mime="text/csv"
                    )
            
        except Exception as e:
            st.error(f"Error generando reporte de permisos: {e}")

    def obtener_permisos_rbac_rol(self, rol: str) -> List[Dict]:
        """Obtener permisos RBAC actuales de un rol específico"""
        try:
            query = """
            SELECT rol, modulo_nombre, puede_ver, puede_consultar, puede_editar, puede_eliminar
            FROM permisos_rol
            WHERE rol = %s AND activo = TRUE
            """
            resultado = execute_query(query, (rol,))

            if resultado and (isinstance(resultado, list) and len(resultado) > 0 or isinstance(resultado, dict)):
                return resultado if isinstance(resultado, list) else [resultado]

            return []

        except Exception as e:
            st.error(f"Error obteniendo permisos RBAC del rol {rol}: {e}")
            return []

    def guardar_permisos_rbac(self, rol: str, permisos_modulos: Dict[str, Dict[str, bool]]):
        """Guardar configuración RBAC de permisos para un rol"""
        try:
            # Iniciar transacción
            queries = []

            # Para cada módulo, actualizar o insertar permisos
            for modulo, acciones in permisos_modulos.items():
                queries.append((
                    """
                    INSERT INTO permisos_rol
                    (rol, modulo_nombre, puede_ver, puede_consultar, puede_editar, puede_eliminar, activo, fecha_actualizacion)
                    VALUES (%s, %s, %s, %s, %s, %s, TRUE, CURRENT_TIMESTAMP)
                    ON CONFLICT (rol, modulo_nombre)
                    DO UPDATE SET
                        puede_ver = EXCLUDED.puede_ver,
                        puede_consultar = EXCLUDED.puede_consultar,
                        puede_editar = EXCLUDED.puede_editar,
                        puede_eliminar = EXCLUDED.puede_eliminar,
                        fecha_actualizacion = CURRENT_TIMESTAMP
                    """,
                    (
                        rol,
                        modulo,
                        acciones.get('puede_ver', False),
                        acciones.get('puede_consultar', False),
                        acciones.get('puede_editar', False),
                        acciones.get('puede_eliminar', False)
                    )
                ))

            # Ejecutar transacción
            resultado = ejecutar_transaccion(queries)

            if resultado['success']:
                st.success(f"✅ Permisos RBAC del rol '{rol}' actualizados correctamente.")
            else:
                st.error(f"❌ Error actualizando permisos RBAC: {resultado['message']}")

        except Exception as e:
            st.error(f"❌ Error en la operación RBAC: {e}")

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
