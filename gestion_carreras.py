#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gestion_carreras.py - Módulo de Gestión de Carreras (Administrativo)
SICADFOC 2026 - Instituto Universitario Jesus Obrero
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import sys
import os

# Importar estilos globales de formularios (MANDATORIO)
from styles import aplicar_estilo_consistente_global

# Importaciones del sistema
try:
    from seguridad import tiene_permiso
    from database import execute_query, ejecutar_transaccion
except ImportError as e:
    st.error(f"Error importando módulos: {e}")
    sys.exit(1)

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
            # Aplicar estilos globales de formularios (MANDATORIO)
            aplicar_estilo_consistente_global()
            
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
        """Muestra listado de carreras con opciones de edición"""
        try:
            # Obtener carreras
            carreras = self.obtener_carreras()
            
            if not carreras:
                st.info("No hay carreras registradas en el sistema.")
                return
            
            st.subheader("📋 Listado de Carreras")
            
            # Convertir a DataFrame con validación
            if carreras and isinstance(carreras, list) and len(carreras) > 0 and isinstance(carreras[0], dict):
                df_carreras = pd.DataFrame(carreras)
            else:
                st.info("No hay carreras registradas.")
                return
            
            # Renombrar columnas para mejor visualización
            columnas_renombradas = {
                'id_carrera': 'ID',
                'nombre_carrera': 'Nombre de Carrera',
                'descripcion_carrera': 'Descripción'
            }
            df_carreras = df_carreras.rename(columns=columnas_renombradas)
            
            # Mostrar tabla
            st.dataframe(df_carreras, use_container_width=True)
            
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
            
            col1, col2 = st.columns(2)
            
            with col1:
                nombre_carrera = st.text_input(
                    "Nombre de Carrera*",
                    placeholder="Ej: Administración",
                    help="Nombre oficial de la carrera"
                )
            
            with col2:
                # Campo para código (opcional)
                codigo_carrera = st.text_input(
                    "Código de Carrera",
                    placeholder="Ej: ADM-001",
                    help="Código identificador de la carrera (opcional)"
                )
            
            descripcion_carrera = st.text_area(
                "Descripción*",
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
                self.agregar_carrera(nombre_carrera, descripcion_carrera, codigo_carrera)
            
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
                
                with col1:
                    nombre_editar = st.text_input(
                        "Nombre de Carrera*",
                        value=carrera['nombre_carrera'],
                        key=f"nombre_editar_{id_carrera}"
                    )
                
                with col2:
                    codigo_editar = st.text_input(
                        "Código de Carrera",
                        value=carrera.get('codigo_carrera', ''),
                        key=f"codigo_editar_{id_carrera}"
                    )
                
                descripcion_editar = st.text_area(
                    "Descripción*",
                    value=carrera['descripcion_carrera'],
                    height=100,
                    key=f"descripcion_editar_{id_carrera}"
                )
                
                col_save, col_cancel = st.columns(2)
                
                with col_save:
                    save_button = st.form_submit_button("💾 Guardar Cambios", type="primary")
                
                with col_cancel:
                    cancel_button = st.form_submit_button("❌ Cancelar")
                
                if save_button:
                    self.editar_carrera(id_carrera, nombre_editar, descripcion_editar, codigo_editar)
                
                if cancel_button:
                    st.rerun()
                    
        except Exception as e:
            st.error(f"Error mostrando formulario de edición: {e}")
    
    def agregar_carrera(self, nombre: str, descripcion: str, codigo: str = None):
        """Agrega una nueva carrera a la base de datos"""
        try:
            if not nombre or not descripcion:
                st.error("❌ El nombre y la descripción son obligatorios.")
                return
            
            # Verificar si ya existe
            query_check = "SELECT id_carrera FROM carrera WHERE nombre_carrera = %s"
            resultado = execute_query(query_check, (nombre,))
            
            if resultado and (isinstance(resultado, list) and len(resultado) > 0 or isinstance(resultado, dict)):
                st.error("❌ Ya existe una carrera con ese nombre.")
                return
            
            # Insertar nueva carrera
            query_insert = """
                INSERT INTO carrera (nombre_carrera, descripcion_carrera, codigo_carrera) 
                VALUES (%s, %s, %s)
            """
            
            execute_query(query_insert, (nombre, descripcion, codigo))
            
            st.success(f"✅ Carrera '{nombre}' agregada correctamente.")
            st.balloons()
            
            # Limpiar formulario
            st.session_state[f"form_agregar_carrera"] = {}
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error agregando carrera: {e}")
    
    def editar_carrera(self, id_carrera: int, nombre: str, descripcion: str, codigo: str = None):
        """Edita una carrera existente"""
        try:
            if not nombre or not descripcion:
                st.error("❌ El nombre y la descripción son obligatorios.")
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
                SET nombre_carrera = %s, descripcion_carrera = %s, codigo_carrera = %s 
                WHERE id_carrera = %s
            """
            
            execute_query(query_update, (nombre, descripcion, codigo, id_carrera))
            
            st.success(f"✅ Carrera '{nombre}' actualizada correctamente.")
            st.balloons()
            
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
            
            if carreras and isinstance(carreras, list) and len(carreras) > 0 and isinstance(carreras[0], dict):
                st.markdown("#### Listado Detallado")
                
                df_estadisticas = pd.DataFrame(carreras)
                
                # Renombrar columnas
                df_estadisticas = df_estadisticas.rename(columns={
                    'id_carrera': 'ID',
                    'nombre_carrera': 'Carrera',
                    'descripcion_carrera': 'Descripción',
                    'codigo_carrera': 'Código'
                })
                
                st.dataframe(df_estadisticas, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error mostrando estadísticas: {e}")
    
    def obtener_carreras(self) -> List[Dict]:
        """Obtiene todas las carreras de la base de datos"""
        try:
            query = """
                SELECT id_carrera, nombre_carrera, descripcion_carrera, codigo_carrera
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
                SELECT id_carrera, nombre_carrera, descripcion_carrera, codigo_carrera
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
                    INSERT INTO carrera (nombre_carrera, descripcion_carrera, codigo_carrera) 
                    VALUES (%s, %s, %s)
                """,
                (nombre, descripcion, codigo)
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
