#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gestion_estudiantil.py - Módulo de Gestión de Estudiantes
SICADFOC 2026 - Instituto Universitario Jesus Obrero

Arquitectura: Lista primero, Registro después
"""

import streamlit as st
import re
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
except ImportError as e:
    print(f"Error importando servicio unificado optimizado: {e}")
    sys.exit(1)

# Connection pooling con Streamlit cache
@st.cache_resource
def get_cached_connection():
    """Obtener conexión persistente cacheada para evitar múltiples conexiones"""
    try:
        servicio = obtener_servicio()
        return servicio
    except Exception as e:
        st.error(f"Error estableciendo conexión cacheada: {e}")
        return None

def ejecutar_query_seguro(query, params=None, fetch_all=False):
    """Ejecutar query con manejo seguro de conexiones y cierre garantizado"""
    conn = None
    cursor = None
    try:
        servicio = get_cached_connection()
        if servicio is None:
            return None
            
        resultado = ejecutar_query(query, params=params, fetch_all=fetch_all)
        return resultado
    except Exception as e:
        st.error(f"Error en consulta: {e}")
        logger.error(f"Error en consulta: {e}")
        return None
    finally:
        # Forzar limpieza de conexiones
        try:
            limpiar_conexiones()
        except:
            pass

# Configuración de logging
logger = logging.getLogger(__name__)

def obtener_listado_estudiantes():
    """Función unificada para obtener listado de estudiantes desde la base de datos"""
    try:
        columna_cedula = obtener_columna_cedula()
        
        query_estudiantes = f"""
        SELECT p.cedula, p.nombre, p.apellido, p.email_personal, p.telefono, 
               e.id_carrera, e.semestre_actual, e.estado_registro,
               u.login_usuario, u.rol, u.activo
        FROM persona p
        JOIN usuarios u ON p.cedula = u.{columna_cedula}
        LEFT JOIN estudiante e ON p.cedula = e.cedula_estudiante
        WHERE u.rol = 'Estudiante'
        ORDER BY p.apellido, p.nombre
        """
        
        resultado = ejecutar_query_seguro(query_estudiantes, fetch_all=True)
        
        if resultado and isinstance(resultado, list):
            return resultado
        else:
            return []
            
    except Exception as error:
        st.error(f"Error técnico en consulta de estudiantes: {error}")
        logger.error(f"Error en consulta de estudiantes: {error}")
        return []

def gestion_estudiantil():
    """Modulo completo para gestión de estudiantes con arquitectura corregida"""
    try:
        # Aplicar estilos globales de formularios (MANDATORIO)
        aplicar_estilo_consistente_global()
        
        st.header("Gestión de Estudiantes")
        
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
            if not tiene_permiso(rol_usuario, 'Estudiantes', 'Consultar'):
                st.error("Acceso denegado. No tienes permisos para consultar estudiantes.")
                st.stop()

        # Crear tabs simplificadas - SOLO CONSULTA Y EDICIÓN (OPTIMIZADO)
        if rol_usuario in ['Administrador', 'Admin'] or SeguridadFOC26.is_profesor():
            # Admin y Profesor: solo consulta y edición
            if tiene_permiso(rol_usuario, 'Estudiantes', 'Consultar'):
                tab1, tab2 = st.tabs(["Estudiantes Registrados", "Editar Estudiante"])
            else:
                st.error("Acceso denegado. No tienes permisos para consultar estudiantes.")
                st.stop()
        elif SeguridadFOC26.is_estudiante():
            # Estudiante: solo consulta y edición de su perfil
            if tiene_permiso(rol_usuario, 'Estudiantes', 'Consultar'):
                tab1, tab2 = st.tabs(["Mis Datos", "Editar Mi Perfil"])
            else:
                st.error("Acceso denegado. No tienes permisos para consultar datos.")
                st.stop()
        else:
            st.error("Rol no reconocido. Contacte al administrador.")
            st.stop()

        # TAB1: LISTADO DIRECTO (CARGA INMEDIATA)
        with tab1:
            if SeguridadFOC26.is_admin() or SeguridadFOC26.is_profesor():
                st.subheader("Estudiantes Registrados")
                
                # Obtener listado usando función unificada (carga directa)
                estudiantes = obtener_listado_estudiantes()

                # Manejo de estados vacíos optimizado
                if not estudiantes:
                    st.info("No se encontraron registros de estudiantes.")
                else:
                    # Mostrar exclusivamente la tabla de estudiantes (sin renderizado complejo)
                    _mostrar_tabla_estudiantes_optimizada(estudiantes)
                    
            elif SeguridadFOC26.is_estudiante():
                st.subheader("Mis Datos")
                
                # Estudiante solo ve su propio registro con manejo seguro de conexiones
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
                        e.carrera,
                        e.semestre_formacion,
                        e.estado_registro,
                        e.id as estudiante_id
                    FROM usuarios u
                    JOIN persona p ON u.{columna_cedula} = p.cedula
                    LEFT JOIN estudiante e ON p.cedula = e.cedula_estudiante
                    WHERE u.rol = 'Estudiante' AND u.{columna_cedula} = %s
                    """
                    
                    resultado = ejecutar_query_seguro(query, params=(user_cedula,))
                    
                    if resultado:
                        estudiante = resultado
                        st.write("**Información Personal:**")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Nombre:** {estudiante.get('nombre', 'N/A')}")
                            st.write(f"**Apellido:** {estudiante.get('apellido', 'N/A')}")
                            st.write(f"**Cédula:** {estudiante.get('cedula', 'N/A')}")
                            st.write(f"**Teléfono:** {estudiante.get('telefono', 'N/A')}")
                        
                        with col2:
                            st.write(f"**Email:** {estudiante.get('email', 'N/A')}")
                            st.write(f"**Carrera:** {estudiante.get('carrera', 'N/A')}")
                            st.write(f"**Semestre:** {estudiante.get('semestre_formacion', 'N/A')}")
                            st.write(f"**Estado:** {estudiante.get('estado_registro', 'N/A')}")
                    else:
                        st.error("No se encontró tu información de estudiante.")
                        
                except Exception as error:
                    st.error(f"Error al consultar tus datos: {error}")
                    logger.error(f"Error en consulta de estudiante: {error}")

        # TAB2: EDICIÓN (ÚNICA FUNCIÓN ADICIONAL)
        with tab2:
            if SeguridadFOC26.is_admin() or SeguridadFOC26.is_profesor():
                st.subheader("Editar Estudiante")
                
                # Verificar si hay una cédula para editar
                cedula_editar = st.session_state.get('editar_estudiante_cedula', None)
                
                if cedula_editar:
                    st.info(f"Editando estudiante con cédula: {cedula_editar}")
                    _mostrar_formulario_edicion_estudiante(cedula_editar)
                else:
                    st.info("Seleccione un estudiante desde la lista para editar.")
                    
            elif SeguridadFOC26.is_estudiante():
                st.subheader("Editar Mi Perfil")
                _mostrar_formulario_edicion_perfil()
            else:
                st.error("Rol no reconocido.")
                return

    except Exception as error:
        st.error(f"Error en el módulo de gestión de estudiantes: {error}")
        logger.error(f"Error en gestion_estudiantil: {error}")

def _mostrar_tabla_estudiantes_optimizada(estudiantes: List[Dict]):
    """Mostrar tabla de estudiantes optimizada - solo datos, sin renderizado complejo"""
    try:
        if not estudiantes:
            st.info("No se encontraron estudiantes registrados.")
            return
        
        # Convertir a DataFrame para visualización
        df_estudiantes = pd.DataFrame(estudiantes)
        
        if df_estudiantes.empty:
            st.info("No hay datos de estudiantes para mostrar.")
            return
        
        # Mostrar tabla simple y directa - optimizada para velocidad
        st.dataframe(
            df_estudiantes[["nombre", "apellido", "cedula", "telefono", "email_personal", "id_carrera", "semestre_actual"]],
            use_container_width=True,
            hide_index=True
        )
        
        # Opción de edición simple (bajo demanda)
        if SeguridadFOC26.is_admin():
            st.subheader("Opciones de Edición")
            cedula_editar = st.text_input("Ingrese Cédula del Estudiante a Editar:", key="cedula_editar_estudiante")
            
            if cedula_editar:
                # Buscar estudiante por cédula
                estudiante_encontrado = next((e for e in estudiantes if e.get('cedula') == cedula_editar), None)
                
                if estudiante_encontrado:
                    st.success(f"Estudiante encontrado: {estudiante_encontrado.get('nombre', '')} {estudiante_encontrado.get('apellido', '')}")
                    
                    # Botón para editar
                    if st.button("Editar Estudiante", key="btn_editar_estudiante"):
                        st.session_state['editar_estudiante_cedula'] = cedula_editar
                        st.rerun()
                else:
                    st.error("Estudiante no encontrado.")
        
    except Exception as error:
        st.error(f"Error mostrando tabla de estudiantes: {error}")
        logger.error(f"Error en _mostrar_tabla_estudiantes_optimizada: {error}")

def _mostrar_tabla_estudiantes(estudiantes: List[Dict]):
    """Función legacy - mantener por compatibilidad"""
    _mostrar_tabla_estudiantes_optimizada(estudiantes)

def _mostrar_formulario_registro_estudiante():
    """Formulario para registrar nuevo estudiante con estética profesional"""
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
        
        with st.form("form_registro_estudiante"):
            st.markdown("### Datos Personales del Estudiante")
            
            col1, col2 = st.columns(2)
            
            with col1:
                cedula_estudiante = st.text_input("Cédula del Estudiante*", key="cedula_estudiante", 
                                                  help="Formato: V-12345678 o 12345678")
                nombre = st.text_input("Nombres*", key="nombre_estudiante")
                apellido = st.text_input("Apellidos*", key="apellido_estudiante")
                email = st.text_input("Correo Electrónico*", key="email_estudiante")
                telefono = st.text_input("Teléfono", key="telefono_estudiante")
            
            with col2:
                fecha_nacimiento = st.date_input("Fecha de Nacimiento*", key="fecha_nacimiento_estudiante")
                genero = st.selectbox("Género*", ["Masculino", "Femenino"], key="genero_estudiante")
                direccion = st.text_area("Dirección", key="direccion_estudiante")
                
                # Obtener carreras disponibles dinámicamente desde gestión_carreras
                try:
                    from gestion_carreras import obtener_listado_carreras
                    carreras_disponibles = obtener_listado_carreras()
                    
                    if carreras_disponibles:
                        # Filtrar solo carreras activas
                        carreras_activas = [c for c in carreras_disponibles if c.get('activo', True)]
                        opciones_carreras = {f"{c['nombre_carrera']}": c['id_carrera'] for c in carreras_activas}
                    else:
                        opciones_carreras = {"Ingeniería de Sistemas": 1, "Administración": 2}
                    
                    carrera = st.selectbox("Carrera*", list(opciones_carreras.keys()), key="carrera_estudiante")
                    semestre = st.number_input("Semestre*", min_value=1, max_value=12, value=1, key="semestre_estudiante")
                    
                except Exception as error:
                    st.warning("Error al cargar carreras, usando opciones por defecto")
                    opciones_carreras = {"Ingeniería de Sistemas": 1, "Administración": 2}
                    carrera = st.selectbox("Carrera*", list(opciones_carreras.keys()), key="carrera_estudiante")
                    semestre = st.number_input("Semestre*", min_value=1, max_value=12, value=1, key="semestre_estudiante")
            
            # Contraseña para el usuario
            st.markdown("### Datos de Acceso")
            contrasena = st.text_input("Contraseña Temporal*", type="password", key="contrasena_estudiante",
                                      help="Esta contraseña será usada para el primer inicio de sesión")
            confirmar_contrasena = st.text_input("Confirmar Contraseña*", type="password", key="confirmar_contrasena_estudiante")
            
            # Botones de acción
            col1, col2 = st.columns(2)
            with col1:
                submit_button = st.form_submit_button("Registrar Estudiante", type="primary", use_container_width=True)
            with col2:
                limpiar_button = st.form_submit_button("Limpiar Formulario", use_container_width=True)
            
            if limpiar_button:
                st.rerun()
            
            if submit_button:
                # Validaciones
                if not all([cedula_estudiante, nombre, apellido, email, contrasena]):
                    st.error("Todos los campos marcados con * son obligatorios.")
                    return
                
                if contrasena != confirmar_contrasena:
                    st.error("Las contraseñas no coinciden.")
                    return
                
                if len(contrasena) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres.")
                    return
                
                # Validar formato de cédula
                cedula_limpia = cedula_estudiante.strip()
                if not cedula_limpia.startswith('V-'):
                    cedula_limpia = f'V-{cedula_limpia}'
                
                # Procesar registro con servicio unificado
                _procesar_registro_estudiante(cedula_limpia, nombre, apellido, email, telefono, 
                                            fecha_nacimiento, genero, direccion, carrera, semestre, contrasena)
        
        # Cerrar contenedor
        st.markdown("</div>", unsafe_allow_html=True)
                
    except Exception as error:
        st.error(f"Error en formulario de registro: {error}")
        logger.error(f"Error en _mostrar_formulario_registro_estudiante: {error}")

def _procesar_registro_estudiante(cedula: str, nombre: str, apellido: str, email: str, telefono: str, 
                                fecha_nacimiento, genero: str, direccion: str, carrera: str, semestre: int, contrasena: str):
    """Procesa el registro de un nuevo estudiante usando servicio unificado"""
    try:
        from seguridad import hash_password
        
        # Validar que la cédula no exista
        columna_cedula = obtener_columna_cedula()
        query_validacion = f"SELECT COUNT(*) as existe FROM persona WHERE cedula = %s"
        resultado_validacion = ejecutar_query_seguro(query_validacion, params=(cedula,))
        
        if resultado_validacion and resultado_validacion.get('existe', 0) > 0:
            st.error(f"❌ Error: Ya existe un registro con la cédula {cedula}")
            return
        
        # Hash de la contraseña
        hash_contrasena = hash_password(contrasena)
        
        # Transacción para registrar estudiante usando servicio unificado
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
            """, (cedula, f"{nombre.lower()}.{apellido.lower()}", hash_contrasena, 'Estudiante', True, email)),
            
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
            
            # 3. Insertar en tabla estudiante
            ("""
            INSERT INTO estudiante (cedula_estudiante, carrera, semestre_formacion, estado_registro)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (cedula_estudiante) 
            DO UPDATE SET 
                carrera = EXCLUDED.carrera,
                semestre_formacion = EXCLUDED.semestre_formacion,
                estado_registro = EXCLUDED.estado_registro
            """, (cedula, carrera, semestre, 'Activo'))
        ]
        
        # Ejecutar transacción usando servicio unificado con manejo seguro de conexiones
        resultado = None
        try:
            resultado = ejecutar_transaccion(queries_params)
            
            if resultado:
                st.success(f"Estudiante {nombre} {apellido} registrado exitosamente.")
                st.info(f"Cédula: {cedula} | Usuario: {nombre.lower()}.{apellido.lower()} | Contraseña temporal: {contrasena}")
                st.balloons()
            else:
                st.error("Error al registrar el estudiante. Por favor, intente nuevamente.")
                
        except Exception as error:
            st.error(f"Error en el proceso de registro: {error}")
            logger.error(f"Error en _procesar_registro_estudiante: {error}")
        finally:
            # Forzar limpieza de conexiones
            try:
                limpiar_conexiones()
            except:
                pass
                
    except Exception as error:
        st.error(f"Error en el proceso de registro: {error}")
        logger.error(f"Error en _procesar_registro_estudiante: {error}")

def _mostrar_formulario_edicion_perfil():
    """Formulario para que los estudiantes editen su propio perfil"""
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
                   p.direccion, p.sexo, p.fecha_nacimiento
            FROM persona p
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
                
                with st.form("form_edicion_perfil"):
                    st.markdown("### Actualizar Datos Personales")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        nuevo_nombre = st.text_input("Nombres*", value=datos_actuales.get('nombre', ''), key="edit_nombre")
                        nuevo_apellido = st.text_input("Apellidos*", value=datos_actuales.get('apellido', ''), key="edit_apellido")
                        nuevo_email = st.text_input("Correo Electrónico*", value=datos_actuales.get('email_personal', ''), key="edit_email")
                        nuevo_telefono = st.text_input("Teléfono", value=datos_actuales.get('telefono', ''), key="edit_telefono")
                    
                    with col2:
                        nueva_direccion = st.text_area("Dirección", value=datos_actuales.get('direccion', ''), key="edit_direccion")
                        nuevo_genero = st.selectbox("Género", ["Masculino", "Femenino"], 
                                                 index=0 if datos_actuales.get('sexo') == 'Masculino' else 1,
                                                 key="edit_genero")
                        nueva_fecha_nac = st.date_input("Fecha de Nacimiento", 
                                                     value=datos_actuales.get('fecha_nacimiento') or datetime.now().date(),
                                                     key="edit_fecha_nac")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        submit_button = st.form_submit_button("Actualizar Perfil", type="primary", use_container_width=True)
                    with col2:
                        cancelar_button = st.form_submit_button("Cancelar", use_container_width=True)
                    
                    if submit_button:
                        if not all([nuevo_nombre, nuevo_apellido, nuevo_email]):
                            st.error("Los campos marcados con * son obligatorios.")
                            return
                        
                        # Actualizar datos usando servicio unificado
                        query_update = """
                        UPDATE persona 
                        SET nombre = %s, apellido = %s, email_personal = %s, telefono = %s, 
                            direccion = %s, sexo = %s, fecha_nacimiento = %s
                        WHERE cedula = %s
                        """
                        
                        resultado_update = ejecutar_query(query_update, 
                                                         (nuevo_nombre, nuevo_apellido, nuevo_email, 
                                                          nuevo_telefono, nueva_direccion, 
                                                          nuevo_genero, nueva_fecha_nac, user_cedula))
                        
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

def registro_estudiantes_main():
    """Función principal del módulo de registro de estudiantes usando servicio unificado"""
    try:
        st.header("Registro de Estudiantes")
        rol_usuario = st.session_state.get('user_role', None)
        
        # ACCESO GARANTIZADO: Administradores siempre ven el formulario
        if rol_usuario in ['Administrador', 'Admin']:
            st.info("Acceso como Administrador - Formulario disponible")
            _mostrar_formulario_registro_estudiante()
        elif rol_usuario == 'Profesor':
            if tiene_permiso(rol_usuario, 'Estudiantes', 'registrar') or tiene_permiso(rol_usuario, 'Estudiantes', 'crear'):
                st.info("Acceso como Profesor - Formulario disponible")
                _mostrar_formulario_registro_estudiante()
            else:
                st.warning("No tienes permisos para registrar estudiantes.")
        else:
            st.warning("Este módulo está disponible para administradores y profesores.")
            
    except Exception as error:
        st.error(f"Error en el módulo de registro: {error}")
        logger.error(f"Error en registro_estudiantes_main: {error}")
