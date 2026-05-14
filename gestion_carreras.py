#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gestion_carreras.py - Módulo de Gestión de Carreras (Administrativo)
SICADFOC 2026 - Instituto Universitario Jesus Obrero
"""

import streamlit as st
import pandas as pd
import datetime
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

class GestionCarreras:
    """Clase principal para gestión de carreras"""
    
    def __init__(self):
        self.user_role = st.session_state.get('user_role', None)
        self.user_cedula = st.session_state.get('user_cedula', None)
    
    @requiere_administrador
    def gestion_carreras(self):
        """Función principal del módulo de gestión de carreras"""
        try:
            st.header("🎓 Gestión de Carreras")
            st.info("📋 Módulo administrativo para gestionar las carreras del sistema")
            
            # Tabs para diferentes funcionalidades
            tab1, tab2, tab3 = st.tabs(["📋 Listado", "➕ Agregar", "📊 Estadísticas"])
            
            with tab1:
                self.mostrar_listado_carreras()
            
            with tab2:
                if tiene_permiso(self.user_role, 'Gestión Carreras', 'Registrar'):
                    self.formulario_agregar_carrera()
                else:
                    st.warning("No tienes permisos para registrar nuevas carreras.")
            
            with tab3:
                self.mostrar_estadisticas_carreras()
                
        except Exception as e:
            st.error(f"Error en módulo de carreras: {e}")
    
    def mostrar_listado_carreras(self):
        """Muestra el listado de carreras con contador de estudiantes"""
        try:
            carreras = self.obtener_carreras()
            
            if not carreras:
                st.info("No hay carreras registradas en el sistema.")
                return
            
            st.subheader("📋 Listado de Carreras")
            
            # Obtener conteo de estudiantes por carrera
            query_estudiantes = """
                SELECT c.id_carrera, c.nombre_carrera, COUNT(e.cedula_estudiante) as estudiantes_count
                FROM carrera c
                LEFT JOIN estudiante e ON c.id_carrera = e.id_carrera
                GROUP BY c.id_carrera, c.nombre_carrera
                ORDER BY c.nombre_carrera
            """
            
            resultado_conteo = execute_query(query_estudiantes, fetch_all=True)
            
            # Crear diccionario de conteos
            conteo_por_carrera = {}
            if resultado_conteo:
                conteo_por_carrera = {row['id_carrera']: row['estudiantes_count'] for row in resultado_conteo}
            
            # Agregar conteo a cada carrera
            for carrera in carreras:
                carrera['estudiantes_count'] = conteo_por_carrera.get(carrera['id_carrera'], 0)
            
            # Convertir a DataFrame
            df_carreras = pd.DataFrame(carreras)
            
            # Renombrar columnas para mejor visualización
            columnas_renombradas = {
                'id_carrera': 'ID',
                'nombre_carrera': 'Nombre de Carrera',
                'estudiantes_count': 'Estudiantes Inscritos'
            }
            df_carreras = df_carreras.rename(columns=columnas_renombradas)
            
            # Mostrar tabla con contador
            st.dataframe(df_carreras, use_container_width=True)
            
            # Mostrar estadísticas generales
            total_carreras = len(carreras)
            total_estudiantes = sum(carrera['estudiantes_count'] for carrera in carreras)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Carreras", total_carreras)
            with col2:
                st.metric("Total Estudiantes Inscritos", total_estudiantes)
            
            # Opciones de edición
            st.markdown("#### ⚙️ Opciones de Gestión")
            
            # Selector para edición
            opciones_carreras = [f"{c['nombre_carrera']} (ID: {c['id_carrera']})" for c in carreras]
            
            col1, col2 = st.columns(2)
            
            with col1:
                carrera_seleccionada = st.selectbox(
                    "Seleccionar Carrera para Editar",
                    options=opciones_carreras,
                    key="carrera_editar_selector"
                )
                
                if carrera_seleccionada:
                    # Extraer ID y nombre
                    id_carrera = int(carrera_seleccionada.split("(ID: ")[1].replace(")", ""))
                    self.mostrar_formulario_edicion(id_carrera)
            
            with col2:
                carrera_eliminar = st.selectbox(
                    "Seleccionar Carrera para Eliminar",
                    options=opciones_carreras,
                    key="carrera_eliminar_selector"
                )
                
                if st.button("🗑️ Eliminar Carrera", type="secondary"):
                    if carrera_eliminar:
                        id_carrera = int(carrera_eliminar.split("(ID: ")[1].replace(")", ""))
                        self.eliminar_carrera(id_carrera)
                        
        except Exception as e:
            st.error(f"Error mostrando listado de carreras: {e}")
    
    def formulario_agregar_carrera(self):
        """Formulario para agregar nueva carrera"""
        st.subheader("➕ Agregar Nueva Carrera")
        
        with st.form("form_agregar_carrera"):
            st.markdown("#### 📝 Información de la Carrera")
            
            nombre_carrera = st.text_input(
                "Nombre de Carrera*",
                placeholder="Ej: Administración",
                help="Nombre oficial de la carrera"
            )
            
            descripcion_carrera = st.text_area(
                "Descripción",
                placeholder="Describe brevemente la carrera...",
                height=100,
                help="Descripción detallada de la carrera"
            )
            
            # Botones de acción
            col_submit, col_cancel = st.columns(2)
            
            with col_submit:
                submit_button = st.form_submit_button("💾 Agregar Carrera", type="primary")
            
            with col_cancel:
                cancel_button = st.form_submit_button("❌ Cancelar")
            
            if submit_button:
                self.agregar_carrera(nombre_carrera, descripcion_carrera)
            
            if cancel_button:
                st.rerun()
    
    def mostrar_formulario_edicion(self, id_carrera: int):
        """Muestra formulario para editar carrera existente"""
        try:
            # Obtener datos de la carrera
            carrera = self.obtener_carrera_por_id(id_carrera)
            
            if not carrera:
                st.error("Carrera no encontrada.")
                return
            
            st.markdown("#### ✏️ Editar Carrera")
            
            with st.form(f"form_editar_carrera_{id_carrera}"):
                col1, col2 = st.columns(2)
                
                nombre_editar = st.text_input(
                    "Nombre de Carrera*",
                    value=carrera['nombre_carrera'],
                    key=f"nombre_editar_{id_carrera}"
                )
                
                descripcion_editar = st.text_area(
                    "Descripción",
                    value=carrera.get('descripcion_carrera', ''),
                    placeholder="Describe brevemente la carrera...",
                    height=100,
                    help="Descripción detallada de la carrera",
                    key=f"descripcion_editar_{id_carrera}"
                )
                
                col_save, col_cancel = st.columns(2)
                
                with col_save:
                    save_button = st.form_submit_button("💾 Guardar Cambios", type="primary")
                
                with col_cancel:
                    cancel_button = st.form_submit_button("❌ Cancelar")
                
                if save_button:
                    self.editar_carrera(id_carrera, nombre_editar, descripcion_editar)
                
                if cancel_button:
                    st.rerun()
                    
        except Exception as e:
            st.error(f"Error mostrando formulario de edición: {e}")
    
    def agregar_carrera(self, nombre: str, descripcion: str):
        """Agrega una nueva carrera a la base de datos con validación mejorada"""
        try:
            if not nombre:
                st.error("El nombre es obligatorio.")
                return
            
            # Insertar nueva carrera
            query_insert = """
                INSERT INTO carrera (nombre_carrera, descripcion_carrera, activo) 
                VALUES (%s, %s, true)
            """
            
            execute_query(query_insert, (nombre, descripcion))
            
            st.success(f"Carrera '{nombre}' agregada correctamente.")
            st.rerun()
            
        except Exception as e:
            # Manejo específico de error de duplicación
            if "duplicate key" in str(e).lower() or "llave duplicada" in str(e).lower():
                st.error("Error: La carrera ya existe en el sistema. Por favor, verifica el nombre y código.")
            else:
                st.error(f"Error agregando carrera: {e}")
    
    def editar_carrera(self, id_carrera: int, nombre: str, descripcion: str):
        """Edita una carrera existente"""
        try:
            if not nombre:
                st.error("❌ El nombre es obligatorio.")
                return
            
            # Verificar si existe otra carrera con el mismo nombre
            query_check = "SELECT id_carrera FROM carrera WHERE nombre_carrera = %s AND id_carrera != %s"
            resultado = execute_query(query_check, (nombre, id_carrera))
            
            if resultado and (isinstance(resultado, list) and len(resultado) > 0 or isinstance(resultado, dict)):
                st.error("❌ Ya existe otra carrera con ese nombre.")
                return
            
            # Actualizar carrera
            query_update = """
                UPDATE carrera 
                SET nombre_carrera = %s, descripcion_carrera = %s 
                WHERE id_carrera = %s
            """
            
            execute_query(query_update, (nombre, descripcion, id_carrera))
            
            st.success(f"Carrera '{nombre}' actualizada correctamente.")
            
            # Limpiar formulario
            st.session_state[f"form_editar_carrera_{id_carrera}"] = {}
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error editando carrera: {e}")
    
    def eliminar_carrera(self, id_carrera: int):
        """Elimina una carrera de la base de datos"""
        try:
            # Obtener nombre de la carrera para confirmación
            carrera = self.obtener_carrera_por_id(id_carrera)
            
            if not carrera:
                st.error("Carrera no encontrada.")
                return
            
            # Confirmación
            st.warning(f"⚠️ ¿Está seguro de eliminar la carrera '{carrera['nombre_carrera']}'?")
            
            col_confirm, col_cancel = st.columns(2)
            
            with col_confirm:
                if st.button(f"🗑️ Sí, Eliminar", type="primary", key=f"confirmar_eliminar_{id_carrera}"):
                    self.confirmar_eliminacion(id_carrera)
            
            with col_cancel:
                if st.button("❌ Cancelar", key=f"cancelar_eliminar_{id_carrera}"):
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Error en proceso de eliminación: {e}")
    
    def confirmar_eliminacion(self, id_carrera: int):
        """Confirma y ejecuta la eliminación de la carrera"""
        try:
            # Verificar si hay estudiantes asociados
            query_check = "SELECT COUNT(*) as count FROM estudiante WHERE id_carrera = %s"
            resultado = execute_query(query_check, (id_carrera,))
            
            if resultado and (isinstance(resultado, list) and len(resultado) > 0 or isinstance(resultado, dict)):
                count = resultado[0]['count'] if isinstance(resultado, list) else resultado['count']
                if count > 0:
                    st.error(f"❌ No se puede eliminar la carrera porque tiene {count} estudiantes asociados.")
                    return
            
            # Eliminar carrera
            query_delete = "DELETE FROM carrera WHERE id_carrera = %s"
            execute_query(query_delete, (id_carrera,))
            
            st.success("✅ Carrera eliminada correctamente.")
            st.balloons()
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error eliminando carrera: {e}")
    
    def mostrar_estadisticas_carreras(self):
        """Muestra estadísticas de carreras"""
        try:
            st.subheader("📊 Estadísticas de Carreras")
            
            # Estadísticas generales
            query_total = "SELECT COUNT(*) as total FROM carrera"
            query_activas = "SELECT COUNT(*) as activas FROM carrera"
            
            resultado_total = execute_query(query_total)
            resultado_activas = execute_query(query_activas)
            
            # Mostrar métricas
            col1, col2 = st.columns(2)
            
            with col1:
                if resultado_total:
                    total = resultado_total[0]['total'] if isinstance(resultado_total, list) else resultado_total['total']
                    st.metric("Total Carreras", total)
            
            with col2:
                if resultado_activas:
                    activas = resultado_activas[0]['activas'] if isinstance(resultado_activas, list) else resultado_activas['activas']
                    st.metric("Carreras Activas", activas)
            
            # Listado detallado
            carreras = self.obtener_carreras()
            
            if carreras:
                st.markdown("#### 📋 Listado Detallado")
                
                df_estadisticas = pd.DataFrame(carreras)
                
                # Renombrar columnas
                df_estadisticas = df_estadisticas.rename(columns={
                    'id_carrera': 'ID',
                    'nombre_carrera': 'Carrera',
                    'descripcion_carrera': 'Descripción'
                })
                
                st.dataframe(df_estadisticas, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error mostrando estadísticas: {e}")
    
    def obtener_carreras(self) -> List[Dict]:
        """Obtiene todas las carreras de la base de datos"""
        try:
            query = """
                SELECT id_carrera, nombre_carrera, descripcion_carrera, activo
                FROM carrera
                ORDER BY nombre_carrera
            """
            resultado = execute_query(query)
            
            if resultado and (isinstance(resultado, list) and len(resultado) > 0 or isinstance(resultado, dict)):
                return resultado if isinstance(resultado, list) else [resultado]
            
            return []
            
        except Exception as e:
            st.error(f"Error obteniendo carreras: {e}")
            return []
    
    def obtener_carrera_por_id(self, id_carrera: int) -> Dict:
        """Obtiene una carrera específica por su ID"""
        try:
            query = """
                SELECT id_carrera, nombre_carrera, descripcion_carrera
                FROM carrera 
                WHERE id_carrera = %s
            """
            resultado = execute_query(query, (id_carrera,), fetch_one=True)
            
            return resultado or {}
            
        except Exception as e:
            st.error(f"Error obteniendo carrera {id_carrera}: {e}")
            return {}

def precargar_carreras_iniciales():
    """Precarga las carreras iniciales del sistema"""
    try:
        carreras_iniciales = [
            ('Administración', 'Carrera enfocada en la gestión empresarial y administrativa', 'ADM'),
            ('Contaduría', 'Carrera especializada en contabilidad y finanzas', 'CON'),
            ('Educación Integral', 'Formación integral en educación básica y media', 'EDU'),
            ('Educación PreEscolar', 'Especialización en educación inicial y preescolar', 'PRE'),
            ('Electrotecnia', 'Carrera técnica en electricidad y electrónica', 'ELEC'),
            ('Informática', 'Formación en sistemas computacionales y TI', 'INF')
        ]
        
        # Verificar carreras existentes para evitar duplicados
        query_check = "SELECT nombre_carrera FROM carrera"
        resultado = execute_query(query_check, fetch_all=True)
        
        carreras_existentes = set()
        if resultado and isinstance(resultado, list):
            carreras_existentes = {row['nombre_carrera'] for row in resultado}
        
        # Filtrar solo las carreras que no existen
        carreras_a_insertar = []
        for nombre, descripcion, codigo in carreras_iniciales:
            if nombre not in carreras_existentes:
                carreras_a_insertar.append((nombre, descripcion, codigo))
        
        if not carreras_a_insertar:
            print(f"OK Todas las carreras iniciales ya existen en la base de datos.")
            return
        
        print(f"Insertando {len(carreras_a_insertar)} carreras nuevas...")
        
        # Insertar solo las carreras que no existen
        queries = []
        for nombre, descripcion, codigo in carreras_a_insertar:
            queries.append((
                """
                    INSERT INTO carrera (nombre_carrera, descripcion_carrera, activo) 
                    VALUES (%s, %s, true)
                """,
                (nombre, descripcion)
            ))
        
        # Ejecutar transacción
        resultado = ejecutar_transaccion(queries)
        
        if resultado['success']:
            print(f"OK {len(carreras_a_insertar)} carreras nuevas precargadas correctamente.")
        else:
            print(f"Error precargando carreras: {resultado['message']}")
            
    except Exception as e:
        print(f"Error precargando carreras iniciales: {e}")

def mostrar_gestion_carreras():
    """Función principal para mostrar el módulo de gestión de carreras"""
    if not tiene_permiso(st.session_state.get('user_role'), 'Gestión Carreras', 'Consultar'):
        st.error("❌ No tienes permisos para acceder a la gestión de carreras.")
        return
    
    gestor = GestionCarreras()
    gestor.gestion_carreras()

def gestion_carreras():
    """Función principal del módulo de gestión de carreras (compatibilidad)"""
    try:
        if not tiene_permiso(st.session_state.get('user_role'), 'Gestión Carreras', 'Consultar'):
            st.error("No tienes permisos para acceder a la gestión de carreras.")
            return
        
        gestor = GestionCarreras()
        gestor.gestion_carreras()
    except Exception as e:
        st.error(f"Error en el módulo de gestión de carreras: {e}")

# Función global para obtener carreras activas (proveedora de datos maestros)
def obtener_carreras_activas() -> List[Dict[str, Any]]:
    """
    Función global que devuelve las carreras activas del sistema.
    Utilizada por otros módulos para selectores dinámicos.
    """
    try:
        from database import execute_query
        
        query = """
            SELECT id_carrera, nombre_carrera, descripcion_carrera
            FROM carrera 
            WHERE activo = true
            ORDER BY nombre_carrera
        """
        
        resultado = execute_query(query, fetch_all=True)
        
        if resultado and len(resultado) > 0:
            return resultado
        else:
            return []
            
    except Exception as e:
        # En caso de error, retornar lista vacía para no romper otros módulos
        print(f"Error obteniendo carreras activas: {e}")
        return []

# Función para obtener carreras disponibles (compatibilidad con código existente)
def obtener_carreras_disponibles() -> List[Dict[str, Any]]:
    """
    Función de compatibilidad que obtiene carreras disponibles.
    Alias de obtener_carreras_activas() para mantener compatibilidad.
    """
    return obtener_carreras_activas()
