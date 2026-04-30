#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gestion_profesores.py - Módulo de Gestión de Profesores
SICADFOC 2026 - Instituto Universitario Jesus Obrero

Arquitectura: Lista primero, Registro después
"""

import streamlit as st
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd

# Importar estilos globales de formularios (MANDATORIO)
from styles import aplicar_estilo_consistente_global

# Importación del servicio unificado optimizado (único punto de acceso)
try:
    from servicio_unificado_optimizado import (
        obtener_servicio, ejecutar_query, ejecutar_transaccion,
        obtener_columna_cedula, construir_join_persona,
        es_produccion, es_local, test_conexion, limpiar_conexiones
    )
    from seguridad import tiene_permiso, SeguridadFOC26
except ImportError as error:
    print(f"Error importando servicio unificado optimizado: {error}")
    sys.exit(1)

# Connection pooling con Streamlit cache
@st.cache_resource
def get_cached_connection():
    """Obtener conexión persistente cacheada para evitar múltiples conexiones"""
    try:
        servicio = obtener_servicio()
        return servicio
    except Exception as error:
        st.error(f"Error estableciendo conexión cacheada: {error}")
        return None

def ejecutar_query_seguro(query, params=None, fetch_all=False):
    """Ejecutar query con manejo seguro de conexiones y cierre garantizado"""
    try:
        servicio = get_cached_connection()
        if servicio is None:
            return None
        resultado = ejecutar_query(query, params=params, fetch_all=fetch_all)
        return resultado
    except Exception as error:
        st.error(f"Error en consulta: {error}")
        logger.error(f"Error en consulta: {error}")
        return None
    finally:
        # Forzar limpieza de conexiones
        try:
            limpiar_conexiones()
        except:
            pass

# Configuración de logging
logger = logging.getLogger(__name__)

def obtener_listado_profesores():
    """Función unificada para obtener listado de profesores desde la base de datos"""
    try:
        columna_cedula = obtener_columna_cedula()
        
        query_profesores = f"""
        SELECT p.cedula, p.nombre, p.apellido, p.email_personal, p.telefono, 
               pr.especialidad, pr.fecha_contratacion, pr.activo as estado_profesor, pr.categoria,
               u.login_usuario, u.rol, u.activo
        FROM persona p
        JOIN usuarios u ON p.cedula = u.{columna_cedula}
        LEFT JOIN profesor pr ON p.cedula = pr.cedula_profesor
        WHERE u.rol = 'Profesor'
        ORDER BY p.apellido, p.nombre
        """
        
        resultado = ejecutar_query_seguro(query_profesores, fetch_all=True)
        
        if resultado and isinstance(resultado, list):
            return resultado
        else:
            return []
            
    except Exception as error:
        # No mostrar error técnico en UI, solo registrar en log
        # st.error(f"Error técnico en consulta de profesores: {error}")
        logger.error(f"Error en consulta de profesores: {error}")
        return []

def gestion_profesores_main():
    """Modulo completo para gestión de profesores con arquitectura corregida"""
    try:
        # Aplicar estilos globales de formularios (MANDATORIO)
        aplicar_estilo_consistente_global()
        
        st.header("Gestión de Profesores")
        
        # Obtener rol del usuario de sesión con validación
        rol_usuario = st.session_state.get('user_role', None)
        
        # Validación de rol
        if rol_usuario is None:
            st.error("Error: No se pudo determinar el rol del usuario. Por favor, inicie sesión nuevamente.")
            st.warning("Si el problema persiste, contacte al administrador.")
            return
        
        # Validación simplificada - administradores siempre tienen acceso
        if rol_usuario in ['Administrador', 'Admin']:
            st.info("Acceso como Administrador - Todas las funciones disponibles")
        else:
            # Para otros roles, verificar permisos específicos
            if not tiene_permiso(rol_usuario, 'Profesores', 'Consultar'):
                st.error("Acceso denegado. No tienes permisos para consultar profesores.")
                st.stop()

        # Crear tabs simplificadas - SOLO CONSULTA Y EDICIÓN (OPTIMIZADO)
        if rol_usuario in ['Administrador', 'Admin']:
            # Admin: solo consulta y edición
            tab1, tab2 = st.tabs(["Profesores Registrados", "Editar Profesor"])
        elif SeguridadFOC26.is_profesor():
            # Profesor: solo consulta y edición de su perfil
            if tiene_permiso(rol_usuario, 'Profesores', 'Consultar'):
                tab1, tab2 = st.tabs(["Mis Datos", "Editar Mi Perfil"])
            else:
                st.error("Acceso denegado. No tienes permisos para consultar datos.")
                st.stop()
        else:
            st.error("Rol no reconocido para gestión de profesores.")
            st.stop()

        # TAB1: LISTADO DIRECTO (CARGA INMEDIATA)
        with tab1:
            if SeguridadFOC26.is_admin():
                st.subheader("Profesores Registrados")
                
                # Obtener listado usando función unificada (carga directa)
                profesores = obtener_listado_profesores()

                # Manejo de estados vacíos optimizado
                if not profesores:
                    st.info("No se encontraron registros de profesores.")
                else:
                    # Mostrar exclusivamente la tabla de profesores (sin renderizado complejo)
                    _mostrar_tabla_profesores_optimizada(profesores)
                    
            elif SeguridadFOC26.is_profesor():
                st.subheader("Mis Datos")
                
                # Profesor solo ve su propio registro con manejo seguro de conexiones
                try:
                    user_cedula = SeguridadFOC26.get_user_cedula()
                    columna_cedula = obtener_columna_cedula()
                    
                    query = f"""
                    SELECT
                        u.{columna_cedula} as usuario_id,
                        p.nombre,
                        p.apellido,
                        p.cedula,
                        p.telefono,
                        p.fecha_nacimiento,
                        p.sexo as sexo,
                        p.direccion,
                        u.email,
                        pr.especialidad,
                        pr.estado_profesor,
                        pr.id as profesor_id
                    FROM usuarios u
                    JOIN persona p ON u.{columna_cedula} = p.cedula
                    LEFT JOIN profesor pr ON p.cedula = pr.cedula_profesor
                    WHERE u.rol = 'Profesor' AND u.{columna_cedula} = %s
                    """
                    
                    resultado = ejecutar_query(query, params=(user_cedula,), fetch_one=True)
                    
                    if resultado:
                        with st.container():
                            st.write(f"**Nombre:** {resultado.get('nombre', '')} {resultado.get('apellido', '')}")
                            st.write(f"**Cédula:** {resultado.get('cedula', 'N/A')}")
                            st.write(f"**Email:** {resultado.get('email', 'N/A')}")
                            st.write(f"**Teléfono:** {resultado.get('telefono', 'N/A')}")
                            st.write(f"**Especialidad:** {resultado.get('especialidad', 'N/A')}")
                            st.write(f"**Estado:** {resultado.get('estado_profesor', 'N/A')}")
                    else:
                        st.error("No se encontró tu información de profesor.")
                        
                except Exception as error:
                    st.error(f"Error al consultar tus datos: {error}")
                    logger.error(f"Error en consulta de profesor: {error}")

        # TAB2: EDICIÓN (ÚNICA FUNCIÓN ADICIONAL)
        with tab2:
            if SeguridadFOC26.is_admin() or SeguridadFOC26.is_profesor():
                st.subheader("Editar Profesor")
                
                # Verificar si hay una cédula para editar
                cedula_editar = st.session_state.get('editar_profesor_cedula', None)
                
                if cedula_editar:
                    st.info(f"Editando profesor con cédula: {cedula_editar}")
                    _mostrar_formulario_edicion_profesor(cedula_editar)
                else:
                    st.info("Seleccione un profesor desde la lista para editar.")
                    
            elif SeguridadFOC26.is_profesor():
                st.subheader("Editar Mi Perfil")
                _mostrar_formulario_edicion_perfil()
            else:
                st.error("Rol no reconocido.")
                return

    except Exception as error:
        st.error(f"Error en el módulo de gestión de profesores: {error}")
        logger.error(f"Error en gestion_profesores_main: {error}")

def _mostrar_tabla_profesores_optimizada(profesores: List[Dict]):
    """Mostrar tabla de profesores optimizada - solo datos, sin renderizado complejo"""
    try:
        if not profesores:
            st.info("No se encontraron profesores registrados.")
            return
        
        # Convertir a DataFrame para visualización
        df_profesores = pd.DataFrame(profesores)
        
        if df_profesores.empty:
            st.info("No hay datos de profesores para mostrar.")
            return
        
        # Mostrar tabla simple y directa - optimizada para velocidad
        st.dataframe(
            df_profesores[["nombre", "apellido", "cedula", "telefono", "email_personal", "especialidad", "estado_profesor"]],
            use_container_width=True,
            hide_index=True
        )
        
        # Opción de edición simple (bajo demanda)
        if SeguridadFOC26.is_admin():
            st.subheader("Opciones de Edición")
            cedula_editar = st.text_input("Ingrese Cédula del Profesor a Editar:", key="cedula_editar_profesor")
            
            if cedula_editar:
                # Buscar profesor por cédula
                profesor_encontrado = next((p for p in profesores if p.get('cedula') == cedula_editar), None)
                
                if profesor_encontrado:
                    st.success(f"Profesor encontrado: {profesor_encontrado.get('nombre', '')} {profesor_encontrado.get('apellido', '')}")
                    
                    # Botón para editar
                    if st.button("Editar Profesor", key="btn_editar_profesor"):
                        st.session_state['editar_profesor_cedula'] = cedula_editar
                        st.rerun()
                else:
                    st.error("Profesor no encontrado.")
        
    except Exception as error:
        st.error(f"Error mostrando tabla de profesores: {error}")
        logger.error(f"Error en _mostrar_tabla_profesores_optimizada: {error}")

def _mostrar_formulario_edicion_profesor(cedula: str):
    """Formulario para editar profesor existente"""
    try:
        st.info(f"Función de edición para profesor con cédula: {cedula}")
        st.warning("Función de edición en desarrollo - use la opción de edición desde la tabla principal")
    except Exception as error:
        st.error(f"Error en formulario de edición: {error}")

def _mostrar_formulario_edicion_perfil():
    """Formulario para editar perfil propio de profesor"""
    try:
        st.info("Edición de perfil propio en desarrollo")
    except Exception as error:
        st.error(f"Error en edición de perfil: {error}")

def registro_profesores_main():
    """Modulo de registro de profesores - DESACTIVADO POR OPTIMIZACIÓN"""
    st.info("Módulo de registro desactivado para optimizar rendimiento.")
    st.info("Use la opción de edición desde el módulo principal de Profesores.")

def _mostrar_formulario_edicion_estudiante(cedula: str):
    """Formulario para editar estudiante existente"""
    try:
        st.info(f"Función de edición para estudiante con cédula: {cedula}")
        st.warning("Función de edición en desarrollo - use la opción de edición desde la tabla principal")
    except Exception as error:
        st.error(f"Error en formulario de edición: {error}")

def _mostrar_formulario_registro_profesor():
    """Formulario para registrar nuevo profesor con estética profesional"""
    try:
        # Contenedor transparente con estética profesional
        st.markdown("""
        <div style="
            background-color: rgba(0,0,0,0); 
            backdrop-filter: blur(10px); 
            border: 1px solid rgba(255,255,255,0.1); 
            border-radius: 10px; 
            padding: 20px; 
            margin: 10px 0;
        ">
        """, unsafe_allow_html=True)
        
        with st.form("form_registro_profesor"):
            st.markdown("### Datos Personales del Profesor")
            
            col1, col2 = st.columns(2)
            
            with col1:
                cedula_profesor = st.text_input("Cédula del Profesor*", key="cedula_profesor", 
                                               help="Formato: V-12345678 o 12345678")
                nombre = st.text_input("Nombres*", key="nombre_profesor")
                apellido = st.text_input("Apellidos*", key="apellido_profesor")
                email = st.text_input("Correo Electrónico*", key="email_profesor")
                telefono = st.text_input("Teléfono", key="telefono_profesor")
            
            with col2:
                fecha_nacimiento = st.date_input("Fecha de Nacimiento*", key="fecha_nacimiento_profesor")
                genero = st.selectbox("Género*", ["Masculino", "Femenino"], key="genero_profesor")
                direccion = st.text_area("Dirección", key="direccion_profesor")
                
                # Campos específicos de profesor
                especialidad = st.text_input("Especialidad*", key="especialidad_profesor")
                departamento = st.selectbox("Departamento*", [
                    "Departamento de Ingeniería", 
                    "Departamento de Administración", 
                    "Departamento de Educación", 
                    "Departamento de Ciencias"
                ], key="departamento_profesor")
            
            # Contraseña para el usuario
            st.markdown("### Datos de Acceso")
            contrasena = st.text_input("Contraseña Temporal*", type="password", key="contrasena_profesor",
                                      help="Esta contraseña será usada para el primer inicio de sesión")
            confirmar_contrasena = st.text_input("Confirmar Contraseña*", type="password", key="confirmar_contrasena_profesor")
            
            # Botones de acción
            col1, col2 = st.columns(2)
            with col1:
                submit_button = st.form_submit_button("Registrar Profesor", type="primary", use_container_width=True)
            with col2:
                limpiar_button = st.form_submit_button("Limpiar Formulario", use_container_width=True)
            
            if limpiar_button:
                st.rerun()
            
            if submit_button:
                # Validaciones
                if not all([cedula_profesor, nombre, apellido, email, especialidad, contrasena]):
                    st.error("Todos los campos marcados con * son obligatorios.")
                    return
                
                if contrasena != confirmar_contrasena:
                    st.error("Las contraseñas no coinciden.")
                    return
                
                if len(contrasena) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres.")
                    return
                
                # Validar formato de cédula
                cedula_limpia = cedula_profesor.strip()
                if not cedula_limpia.startswith('V-'):
                    cedula_limpia = f'V-{cedula_limpia}'
                
                # Procesar registro con servicio unificado
                _procesar_registro_profesor(cedula_limpia, nombre, apellido, email, telefono, 
                                           fecha_nacimiento, genero, direccion, especialidad, departamento, contrasena)
        
        # Cerrar contenedor
        st.markdown("</div>", unsafe_allow_html=True)
                
    except Exception as error:
        st.error(f"Error en formulario de registro: {error}")
        logger.error(f"Error en _mostrar_formulario_registro_profesor: {error}")

def _procesar_registro_profesor(cedula: str, nombre: str, apellido: str, email: str, telefono: str, 
                              fecha_nacimiento, genero: str, direccion: str, especialidad: str, 
                              departamento: str, contrasena: str):
    """Procesa el registro de un nuevo profesor usando servicio unificado"""
    try:
        from seguridad import hash_password
        
        # Hash de la contraseña
        hash_contrasena = hash_password(contrasena)
        
        # Transacción para registrar profesor usando servicio unificado
        columna_cedula = obtener_columna_cedula()
        
        queries_params = [
            # 1. Insertar en tabla usuarios
            (f"""
            INSERT INTO usuarios ({columna_cedula}, login_usuario, contrasena, rol, activo, email)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT ({columna_cedula}) 
            DO UPDATE SET 
                login_usuario = EXCLUDED.login_usuario,
                contrasena = EXCLUDED.contrasena,
                rol = EXCLUDED.rol,
                activo = EXCLUDED.activo,
                email = EXCLUDED.email
            """, (cedula, f"{nombre.lower()}.{apellido.lower()}", hash_contrasena, 'Profesor', True, email)),
            
            # 2. Insertar en tabla persona
            ("""
            INSERT INTO persona (cedula, nombre, apellido, fecha_nacimiento, telefono, direccion, email_personal, sexo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (cedula) 
            DO UPDATE SET 
                nombre = EXCLUDED.nombre,
                apellido = EXCLUDED.apellido,
                telefono = EXCLUDED.telefono,
                direccion = EXCLUDED.direccion,
                email_personal = EXCLUDED.email_personal,
                sexo = EXCLUDED.sexo
            """, (cedula, nombre, apellido, fecha_nacimiento, telefono, direccion, email, genero)),
            
            # 3. Insertar en tabla profesor
            ("""
            INSERT INTO profesor (cedula_profesor, especialidad, departamento, estado_profesor)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (cedula_profesor) 
            DO UPDATE SET 
                especialidad = EXCLUDED.especialidad,
                departamento = EXCLUDED.departamento,
                estado_profesor = EXCLUDED.estado_profesor
            """, (cedula, especialidad, departamento, 'Activo'))
        ]
        
        # Ejecutar transacción usando servicio unificado
        resultado = ejecutar_transaccion(queries_params)
        
        if resultado:
            st.success(f"Profesor {nombre} {apellido} registrado exitosamente.")
            st.info(f"Cédula: {cedula} | Usuario: {nombre.lower()}.{apellido.lower()} | Contraseña temporal: {contrasena}")
            st.balloons()
        else:
            st.error("Error al registrar el profesor. Por favor, intente nuevamente.")
            
    except Exception as error:
        st.error(f"Error en el proceso de registro: {error}")
        logger.error(f"Error en _procesar_registro_profesor: {error}")

def _mostrar_formulario_edicion_perfil():
    """Formulario para que los profesores editen su propio perfil"""
    try:
        st.subheader("Editar Mi Perfil")
        
        user_cedula = SeguridadFOC26.get_user_cedula()
        if not user_cedula:
            st.error("No se pudo obtener tu información de usuario.")
            return
        
        # Obtener información actual usando servicio unificado
        try:
            query = """
            SELECT p.cedula, p.nombre, p.apellido, p.email_personal, p.telefono, 
                   p.direccion, p.sexo, p.fecha_nacimiento,
                   pr.especialidad, pr.departamento
            FROM persona p
            LEFT JOIN profesor pr ON p.cedula = pr.cedula_profesor
            WHERE p.cedula = %s
            """
            
            resultado = ejecutar_query(query, (user_cedula,))
            
            if resultado:
                datos_actuales = resultado
                
                # Contenedor transparente con estética profesional
                st.markdown("""
                <div style="
                    background-color: rgba(0,0,0,0); 
                    backdrop-filter: blur(10px); 
                    border: 1px solid rgba(255,255,255,0.1); 
                    border-radius: 10px; 
                    padding: 20px; 
                    margin: 10px 0;
                ">
                """, unsafe_allow_html=True)
                
                with st.form("form_edicion_perfil_profesor"):
                    st.markdown("### Actualizar Datos Personales")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        nuevo_nombre = st.text_input("Nombres*", value=datos_actuales.get('nombre', ''), key="edit_nombre_profesor")
                        nuevo_apellido = st.text_input("Apellidos*", value=datos_actuales.get('apellido', ''), key="edit_apellido_profesor")
                        nuevo_email = st.text_input("Correo Electrónico*", value=datos_actuales.get('email_personal', ''), key="edit_email_profesor")
                        nuevo_telefono = st.text_input("Teléfono", value=datos_actuales.get('telefono', ''), key="edit_telefono_profesor")
                    
                    with col2:
                        nueva_direccion = st.text_area("Dirección", value=datos_actuales.get('direccion', ''), key="edit_direccion_profesor")
                        nuevo_genero = st.selectbox("Género", ["Masculino", "Femenino"], 
                                                 index=0 if datos_actuales.get('sexo') == 'Masculino' else 1,
                                                 key="edit_genero_profesor")
                        nueva_fecha_nac = st.date_input("Fecha de Nacimiento", 
                                                     value=datos_actuales.get('fecha_nacimiento') or datetime.now().date(),
                                                     key="edit_fecha_nac_profesor")
                        
                        # Campos específicos de profesor
                        nueva_especialidad = st.text_input("Especialidad*", value=datos_actuales.get('especialidad', ''), key="edit_especialidad_profesor")
                        nuevo_departamento = st.selectbox("Departamento*", [
                            "Departamento de Ingeniería", 
                            "Departamento de Administración", 
                            "Departamento de Educación", 
                            "Departamento de Ciencias"
                        ], index=0 if datos_actuales.get('departamento') == "Departamento de Ingeniería" else 1,
                        key="edit_departamento_profesor")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        submit_button = st.form_submit_button("Actualizar Perfil", type="primary", use_container_width=True)
                    with col2:
                        cancelar_button = st.form_submit_button("Cancelar", use_container_width=True)
                    
                    if submit_button:
                        if not all([nuevo_nombre, nuevo_apellido, nuevo_email, nueva_especialidad]):
                            st.error("Los campos marcados con * son obligatorios.")
                            return
                        
                        # Actualizar datos usando servicio unificado
                        queries_params = [
                            # Actualizar tabla persona
                            ("""
                            UPDATE persona 
                            SET nombre = %s, apellido = %s, email_personal = %s, telefono = %s, 
                                direccion = %s, sexo = %s, fecha_nacimiento = %s
                            WHERE cedula = %s
                            """, (nuevo_nombre, nuevo_apellido, nuevo_email, nuevo_telefono, 
                                  nueva_direccion, nuevo_genero, nueva_fecha_nac, user_cedula)),
                            
                            # Actualizar tabla profesor
                            ("""
                            UPDATE profesor 
                            SET especialidad = %s, departamento = %s
                            WHERE cedula_profesor = %s
                            """, (nueva_especialidad, nuevo_departamento, user_cedula))
                        ]
                        
                        resultado_update = ejecutar_transaccion(queries_params)
                        
                        if resultado_update:
                            st.success("Perfil actualizado exitosamente.")
                            st.rerun()
                        else:
                            st.error("Error al actualizar el perfil.")
                
                # Cerrar contenedor
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error("No se encontró tu información.")
                
        except Exception as error:
            st.error(f"Error al cargar tus datos: {error}")
            
    except Exception as error:
        st.error(f"Error en el formulario de edición: {error}")
        logger.error(f"Error en _mostrar_formulario_edicion_perfil: {error}")

def registro_profesores_main():
    """Función principal del módulo de registro de profesores usando servicio unificado"""
    try:
        st.header("Registro de Profesores")
        rol_usuario = st.session_state.get('user_role', None)
        
        # ACCESO GARANTIZADO: Administradores siempre ven el formulario
        if rol_usuario in ['Administrador', 'Admin']:
            st.info("Acceso como Administrador - Formulario disponible")
            _mostrar_formulario_registro_profesor()
        else:
            st.warning("Este módulo está disponible para administradores.")
            
    except Exception as error:
        st.error(f"Error en el módulo de registro: {error}")
        logger.error(f"Error en registro_profesores_main: {error}")
