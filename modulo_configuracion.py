# -*- coding: utf-8 -*-
"""
modulo_configuracion.py - Módulo de Configuración para SICADFOC 2026
Instituto Universitario Jesus Obrero
Gestión de bases de datos, automatización de despliegue y configuración de entorno
"""

import streamlit as st
import os
import subprocess
import sys
from datetime import datetime
import json

def verificar_acceso_admin():
    """Verifica si el usuario actual es el administrador principal por cédula"""
    try:
        user = st.session_state.get('user', {})
        if user.get('rol') == 'Admin':
            # Verificación por cédula definitiva (superusuario)
            cedula_usuario = user.get('cedula_usuario', '')
            # Normalizar cédula para comparación (aceptar V14300385 y V-14300385)
            cedula_normalizada = cedula_usuario.replace('-', '').upper()
            if cedula_normalizada == 'V14300385':
                print(f"DEBUG: Acceso concedido - Cedula: {cedula_usuario}, Rol: {user.get('rol')}")
                return True
            else:
                print(f"DEBUG: Acceso denegado - Cedula: {cedula_usuario}, Rol: {user.get('rol')}")
        return False
    except Exception as e:
        print(f"DEBUG: Error en verificar_acceso_admin: {e}")
        return False

def interfaz_gestion_bases_datos():
    """Interfaz para gestión de bases de datos"""
    st.subheader("Gestión de Bases de Datos")
    
    # Estado actual de la conexión
    try:
        from conexion_simple_corregido import ConexionSimple
        db = ConexionSimple()
        if db.conectar():
            st.success("Conexión a base de datos activa")
        else:
            st.error("Conexión a base de datos inactiva")
    except Exception as e:
        st.error(f"Error verificando conexión: {e}")
    
    # Opciones de gestión
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Probar Conexión"):
            try:
                db = ConexionSimple()
                if db.conectar():
                    st.success("Conexión exitosa")
                else:
                    st.error("Fallo en conexión")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col2:
        if st.button("Verificar Usuarios"):
            try:
                db = ConexionSimple()
                if db.conectar():
                    result = db.ejecutar_consulta("SELECT COUNT(*) as total FROM usuario")
                    st.info(f"Usuarios en BD: {result[0]['total'] if result else 0}")
            except Exception as e:
                st.error(f"Error: {e}")

def interfaz_automatizacion_despliegue():
    """Interfaz para automatización de despliegue"""
    st.subheader("Automatización de Despliegue")
    
    st.info("Módulo de despliegue automatizado en desarrollo")
    
    # Estado del entorno
    st.write("Entorno actual:", os.getenv("ENVIRONMENT", "local"))
    st.write("Directorio actual:", os.getcwd())

def interfaz_validacion_sistema():
    """Interfaz para validación del sistema"""
    st.subheader("Validación del Sistema")
    
    # Validación de módulos
    modulos = {
        "streamlit": "Framework UI",
        "psycopg2": "Driver PostgreSQL", 
        "hashlib": "Hashing",
        "dotenv": "Variables de entorno"
    }
    
    for modulo, descripcion in modulos.items():
        try:
            __import__(modulo)
            st.success(f" {modulo}: {descripcion} - OK")
        except ImportError:
            st.error(f" {modulo}: {descripcion} - ERROR")

def interfaz_configuracion_entorno():
    """Interfaz para configuración del entorno"""
    st.subheader("Configuración del Entorno")
    
    # Variables de entorno
    st.write("Variables de entorno configuradas:")
    env_vars = [
        "ENVIRONMENT",
        "LOCAL_DB_HOST", 
        "LOCAL_DB_NAME",
        "LOCAL_DB_USER",
        "LOCAL_DB_PORT"
    ]
    
    for var in env_vars:
        valor = os.getenv(var, "No configurado")
        if var == "LOCAL_DB_PASSWORD":
            valor = "***" if valor else "No configurado"
        st.write(f" {var}: {valor}")

def modulo_configuracion():
    """Módulo completo de configuración para administrador"""
    try:
        # Verificación de acceso exclusivo
        if not verificar_acceso_admin():
            st.error("Acceso Denegado. Este módulo es exclusivo para Angel Hernandez (Admin).")
            st.stop()
        
        st.title("Configuración del Sistema")
        st.header("Panel de Administración Avanzada")
        
        # Crear tabs para organizar las funcionalidades
        tab1, tab2, tab3, tab4 = st.tabs(["Bases de Datos", "Despliegue", "Validación", "Entorno"])
        
        with tab1:
            interfaz_gestion_bases_datos()
        
        with tab2:
            interfaz_automatizacion_despliegue()
        
        with tab3:
            interfaz_validacion_sistema()
        
        with tab4:
            interfaz_configuracion_entorno()
            
    except Exception as e:
        st.error(f"Error en módulo de configuración: {e}")
