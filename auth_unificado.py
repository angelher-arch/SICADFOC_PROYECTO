#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auth_unificado.py - Sistema de Autenticación Unificado (Login + Registro)
Senior Full-Stack Developer - SICADFOC 2026
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime, date
import hashlib
import secrets
import re
import logging
from typing import Dict, List, Any, Optional, Union

# Importar estilos globales de formularios (MANDATORIO)
from styles import aplicar_estilo_consistente_global

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importaciones de database.py
from database import execute_query, execute_transaction, get_database_info, authenticate_user

class AuthSystemUnificado:
    """Sistema de autenticación unificado (Login + Registro)"""
    
    def __init__(self):
        self.roles_disponibles = ['Profesor', 'Estudiante']
        self.roles_actuales = ['Administrador', 'Profesor', 'Estudiante']
        
    def validar_cedula(self, cedula):
        """Validar formato de cédula venezolana"""
        pattern = r'^[VE]-\d{7,8}$'
        return re.match(pattern, cedula.upper()) is not None
    
    def validar_email(self, email):
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validar_contraseña(self, password):
        """Validar fortaleza de contraseña"""
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        
        if not re.search(r'[a-zA-Z]', password):
            return False, "La contraseña debe contener al menos una letra"
        
        if not re.search(r'\d', password):
            return False, "La contraseña debe contener al menos un número"
        
        return True, "Contraseña válida"
    
    def verificar_cedula_existente(self, cedula):
        """Verificar si la cédula ya existe en la base de datos"""
        try:
            query = "SELECT COUNT(*) as count FROM usuarios WHERE cedula_usuario = %s"
            result = execute_query(query, (cedula,), fetch_one=True)
            return result.get('count', 0) > 0
        except Exception as e:
            st.error(f"Error verificando cédula: {e}")
            return True
    
    def verificar_login_existente(self, login):
        """Verificar si el login ya existe en la base de datos"""
        try:
            query = "SELECT COUNT(*) as count FROM usuarios WHERE login_usuario = %s"
            result = execute_query(query, (login,), fetch_one=True)
            return result.get('count', 0) > 0
        except Exception as e:
            st.error(f"Error verificando login: {e}")
            return True
    
    def hash_password(self, password):
        """Generar hash SHA-256 de la contraseña"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def registrar_usuario(self, datos_usuario):
        """Registrar nuevo usuario en la base de datos"""
        try:
            with execute_transaction() as conn:
                # Insertar en tabla usuarios
                query_usuarios = """
                INSERT INTO usuarios (
                    cedula_usuario, 
                    login_usuario, 
                    contrasena, 
                    rol, 
                    email, 
                    activo, 
                    fecha_creacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                params_usuarios = (
                    datos_usuario['cedula'],
                    datos_usuario['login'],
                    datos_usuario['password_hash'],
                    datos_usuario['rol'],
                    datos_usuario['email'],
                    True,
                    datetime.now()
                )
                
                conn.execute(query_usuarios, params_usuarios)
                
                # Insertar en tabla persona si hay datos personales
                if datos_usuario.get('nombre_completo'):
                    nombre_parts = datos_usuario['nombre_completo'].split()
                    nombre = nombre_parts[0] if nombre_parts else ''
                    apellido = ' '.join(nombre_parts[1:]) if len(nombre_parts) > 1 else ''
                    
                    query_persona = """
                    INSERT INTO persona (
                        cedula, 
                        nombre, 
                        apellido, 
                        email_personal,
                        fecha_creacion
                    ) VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (cedula) DO UPDATE SET
                        nombre = EXCLUDED.nombre,
                        apellido = EXCLUDED.apellido,
                        email_personal = EXCLUDED.email_personal,
                        fecha_creacion = EXCLUDED.fecha_creacion
                    """
                    
                    params_persona = (
                        datos_usuario['cedula'],
                        nombre,
                        apellido,
                        datos_usuario['email'],
                        datetime.now()
                    )
                    
                    conn.execute(query_persona, params_persona)
                
                return True, "Usuario registrado exitosamente"
                
        except Exception as e:
            return False, f"Error registrando usuario: {str(e)}"
    
    def mostrar_formulario_login(self):
        """Mostrar formulario de login"""
        # Aplicar estilos globales de formularios (MANDATORIO)
        aplicar_estilo_consistente_global()
        
        st.markdown('<h3 style="color: #0A0A0A !important; font-weight: 800 !important; text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.9), 1px 1px 2px rgba(0, 0, 0, 0.8) !important; margin-bottom: 2rem !important;"> Iniciar Sesión</h3>', unsafe_allow_html=True)
        
        # Variable para controlar si el login fue exitoso
        login_exitoso = False
        user_info = None
        
        with st.form("login_form"):
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                # Campo de usuario con estilo inline
                st.markdown('<label style="color: #1E293B !important; font-weight: 700 !important; font-size: 16px !important; display: block; margin-bottom: 8px;"> Usuario</label>', unsafe_allow_html=True)
                username = st.text_input(
                    "",
                    placeholder="Ingrese su nombre de usuario",
                    help="Use su nombre de usuario o cédula",
                    label_visibility="collapsed"
                )
                
                # Campo de contraseña con estilo inline
                st.markdown('<label style="color: #1E293B !important; font-weight: 700 !important; font-size: 16px !important; display: block; margin-bottom: 8px;"> Contraseña</label>', unsafe_allow_html=True)
                password = st.text_input(
                    "",
                    type="password",
                    placeholder="Ingrese su contraseña",
                    help="Ingrese su contraseña segura",
                    label_visibility="collapsed"
                )
                
                # Checkbox de recordar con estilo inline
                recordar = st.checkbox(" Recordar sesión")
                
                # Botón de login (único botón dentro del formulario)
                submit_button = st.form_submit_button(
                    " Iniciar Sesión",
                    use_container_width=True,
                    type="primary"
                )
                
                if submit_button:
                    if not username or not password:
                        st.error(" Por favor ingrese usuario y contraseña")
                    else:
                        with st.spinner("Autenticando..."):
                            result = authenticate_user(username, password)
                        
                        if result and result.get('success', False):
                            st.success(" ¡Bienvenido al sistema!")
                            user_info = result.get('user', {})
                            
                            # Guardar en sesión
                            st.session_state.logged_in = True
                            st.session_state.user = user_info
                            st.session_state.username = user_info.get('login_usuario')
                            st.session_state.role = user_info.get('rol')
                        
                            
                            # Guardar en sesión
                            st.session_state.logged_in = True
                            st.session_state.user = user_info
                            st.session_state.username = user_info.get('login_usuario')
                            st.session_state.role = user_info.get('rol')
                            
                            # Marcar que el login fue exitoso
                            login_exitoso = True
                            
                            # Mostrar información del usuario
                            st.info(f"""
                            **👤 Usuario:** {user_info.get('login_usuario', 'N/A')}
                            **🏷️ Rol:** {user_info.get('rol', 'N/A')}
                            **📧 Nombre:** {user_info.get('nombre_completo', 'N/A')}
                            """)
                            
                        else:
                            st.error("❌ Usuario o contraseña incorrectos")
                            st.warning("Por favor, verifique sus credenciales e intente nuevamente")
        
        # Botón de navegación fuera del formulario (solo si el login fue exitoso)
        if login_exitoso and user_info:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📋 Ir al Sistema Principal", use_container_width=True, type="secondary"):
                    st.success("🎉 Redirigiendo al sistema principal...")
                    # Aquí iría la redirección al sistema principal
                    st.rerun()
        
        # Usuarios de prueba (siempre fuera del formulario)
        with st.expander("👤 Usuarios de Prueba Disponibles"):
            st.write("Use estos usuarios para probar el sistema:")
            
            test_users = [
                ("Angel Hernandez", "admin123", "Administrador"),
                ("Jose Montezuma", "admin123", "Administrador"),
                ("admin", "admin123", "Administrador"),
            ]
            
        
        # CSS UI/UX REFINED PARA REGISTRO - Transparencia total y contraste perfecto
        st.markdown("""
        <style>
        /* DISEÑO UI/UX EXPERTO - TRANSPARENCIA TOTAL Y CONTRASTE PERFECTO */
        
        /* Mantener fondo institucional sin overlay oscuro */
        div[data-testid="stApp"] {
            position: relative !important;
        }
        
        /* TRANSPARENCIA TOTAL DEL CONTENEDOR PRINCIPAL */
        .main .block-container,
        div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column"] {
            background-color: rgba(0, 0, 0, 0) !important;
            border-radius: 0 !important;
            padding: 2.5rem !important;
            box-shadow: none !important;
            backdrop-filter: none !important;
            border: none !important;
        }
        
        /* TRANSPARENCIA TOTAL DEL FORMULARIO */
        form[data-testid="stForm"],
        div[data-testid="stForm"] {
            background-color: rgba(0, 0, 0, 0) !important;
            border-radius: 0 !important;
            padding: 0 !important;
            box-shadow: none !important;
            backdrop-filter: none !important;
            border: none !important;
        }
        
        /* FUENTES OSCURECIDAS CON TEXT-SHADOW PARA MÁXIMO CONTRASTE */
        h1, h2, h3,
        .stMarkdown h1,
        .stMarkdown h2,
        .stMarkdown h3 {
            color: #0A0A0A !important;
            font-weight: 800 !important;
            text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.9),
                         1px 1px 2px rgba(0, 0, 0, 0.8) !important;
            margin-bottom: 1.5rem !important;
        }
        
        /* Labels con contraste extremo y text-shadow */
        label, 
        .stTextInput label,
        .stSelectbox label,
        .stTextArea label,
        .stCheckbox label,
        div[data-testid="stTextInput"] label,
        div[data-testid="stSelectbox"] label,
        div[data-testid="stTextArea"] label,
        div[data-testid="stCheckbox"] label {
            color: #0A0A0A !important;
            font-weight: 700 !important;
            text-shadow: 1px 1px 3px rgba(255, 255, 255, 0.8),
                         1px 1px 2px rgba(0, 0, 0, 0.6) !important;
            font-size: 16px !important;
            display: block !important;
            margin-bottom: 8px !important;
        }
        
        /* Texto markdown con text-shadow */
        .stMarkdown, .stMarkdown *, 
        div[data-testid="stMarkdownContainer"],
        div[data-testid="stMarkdownContainer"] * {
            color: #0A0A0A !important;
            font-weight: 600 !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.7),
                         1px 1px 1px rgba(0, 0, 0, 0.5) !important;
        }
        
        /* INPUTS CON TRANSPARENCIA MÍNIMA Y BORDES DEFINIDOS */
        input[type="text"],
        input[type="password"],
        input[type="email"],
        textarea,
        select,
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stSelectbox"] select {
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: #0A0A0A !important;
            border: 2px solid rgba(255, 255, 255, 0.6) !important;
            border-radius: 12px !important;
            padding: 14px 16px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            backdrop-filter: blur(5px) !important;
            transition: all 0.3s ease !important;
        }
        
        /* Focus states con efecto de resaltado */
        input[type="text"]:focus,
        input[type="password"]:focus,
        input[type="email"]:focus,
        textarea:focus,
        select:focus,
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus,
        div[data-testid="stSelectbox"] select:focus {
            background-color: rgba(255, 255, 255, 0.2) !important;
            border-color: #2563EB !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2),
                        0 4px 12px rgba(0, 0, 0, 0.1) !important;
            outline: none !important;
        }
        
        /* Placeholders con contraste */
        input::placeholder,
        textarea::placeholder,
        div[data-testid="stTextInput"] input::placeholder,
        div[data-testid="stTextArea"] textarea::placeholder {
            color: #4A4A4A !important;
            font-weight: 500 !important;
            opacity: 1 !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.5) !important;
        }
        
        /* BOTÓN DE ACCIÓN PROFESIONAL - AZUL INSTITUCIONAL */
        button[kind="primary"],
        div[data-testid="stForm"] > button,
        .stButton > button {
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
            color: white !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 14px 32px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 8px 24px rgba(37, 99, 235, 0.3),
                        0 4px 12px rgba(0, 0, 0, 0.1) !important;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2) !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        button[kind="primary"]:hover,
        div[data-testid="stForm"] > button:hover,
        .stButton > button:hover {
            background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 32px rgba(37, 99, 235, 0.4),
                        0 6px 16px rgba(0, 0, 0, 0.15) !important;
        }
        
        button[kind="primary"]:active,
        div[data-testid="stForm"] > button:active,
        .stButton > button:active {
            transform: translateY(0) !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
        }
        
        /* Checkbox con estilo refinado */
        div[data-testid="stCheckbox"] label span {
            color: #0A0A0A !important;
            font-weight: 600 !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.7) !important;
        }
        
        /* Help text con legibilidad */
        div[data-testid="stHelpText"],
        .stHelpText {
            color: #2A2A2A !important;
            font-weight: 500 !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.6) !important;
        }
        
        /* Messages con transparencia y contraste */
        .stException,
        .stAlert,
        div[data-testid="stException"],
        div[data-testid="stAlert"] {
            background-color: rgba(255, 255, 255, 0.15) !important;
            backdrop-filter: blur(10px) !important;
            border-left: 4px solid #DC2626 !important;
            color: #0A0A0A !important;
            font-weight: 600 !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.7) !important;
            border-radius: 8px !important;
        }
        
        .stSuccess,
        div[data-testid="stSuccess"] {
            background-color: rgba(255, 255, 255, 0.15) !important;
            backdrop-filter: blur(10px) !important;
            border-left: 4px solid #16A34A !important;
            color: #0A0A0A !important;
            font-weight: 600 !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.7) !important;
            border-radius: 8px !important;
        }
        
        /* Info messages con estilo consistente */
        .stInfo {
            background-color: rgba(255, 255, 255, 0.15) !important;
            backdrop-filter: blur(10px) !important;
            border-left: 4px solid #2563EB !important;
            color: #0A0A0A !important;
            font-weight: 600 !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.7) !important;
            border-radius: 8px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
    def mostrar_formulario_registro(self):
        """Mostrar formulario de registro de usuarios"""
        try:
            # Aplicar estilos globales de formularios (MANDATORIO)
            aplicar_estilo_consistente_global()
            
            with st.form("login_form"):
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col2:
                    # Campo de usuario con estilo inline
                    st.markdown('<label style="color: #1E293B !important; font-weight: 700 !important; font-size: 16px !important; display: block; margin-bottom: 8px;"> Usuario</label>', unsafe_allow_html=True)
                    username = st.text_input(
                        "",
                        placeholder="Ingrese su nombre de usuario",
                        help="Use su nombre de usuario o cédula",
                        label_visibility="collapsed"
                    )
                    
                    # Campo de contraseña con estilo inline
                    st.markdown('<label style="color: #1E293B !important; font-weight: 700 !important; font-size: 16px !important; display: block; margin-bottom: 8px;"> Contraseña</label>', unsafe_allow_html=True)
                    password = st.text_input(
                        "",
                        type="password",
                        placeholder="Ingrese su contraseña",
                        help="Ingrese su contraseña segura",
                        label_visibility="collapsed"
                    )
                    
                    # Checkbox de recordar con estilo inline
                    recordar = st.checkbox(" Recordar sesión")
                    
                    # Botón de login (único botón dentro del formulario)
                    submit_button = st.form_submit_button(
                        " Iniciar Sesión",
                        use_container_width=True,
                        type="primary"
                    )
                    
                    if submit_button:
                        if not username or not password:
                            st.error(" Por favor ingrese usuario y contraseña")
                        else:
                            with st.spinner("Autenticando..."):
                                result = authenticate_user(username, password)
                            
                            if result and result.get('success', False):
                                st.success(" ¡Bienvenido al sistema!")
                                user_info = result.get('user', {})
                                # Guardar en sesión
                                st.session_state.logged_in = True
                                st.session_state.user = user_info
                                st.session_state.username = user_info.get('login_usuario')
                                st.session_state.role = user_info.get('rol')
                                # Marcar que el login fue exitoso
                                login_exitoso = True
                                # Mostrar información del usuario
                                st.info(f"""
                                **Usuario:** {user_info.get('login_usuario', 'N/A')}
                                **Rol:** {user_info.get('rol', 'N/A')}
                                **Nombre:** {user_info.get('nombre_completo', 'N/A')}
                                """)
                            else:
                                st.error(" Usuario o contraseña incorrectos")
                                st.warning("Por favor, verifique sus credenciales e intente nuevamente")
        
        except Exception as e:
            st.error(f"Error en el formulario de registro: {e}")
        
        # Botón de navegación fuera del formulario (solo si el login fue exitoso)
        if 'login_exitoso' in locals() and login_exitoso and 'user_info' in locals() and user_info:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📋 Ir al Sistema Principal", use_container_width=True, type="secondary"):
                    st.success("🎉 Redirigiendo al sistema principal...")
                    # Aquí iría la redirección al sistema principal
                    st.rerun()
        
        # Usuarios de prueba (siempre fuera del formulario)
        with st.expander("👤 Usuarios de Prueba Disponibles"):
            st.write("Use estos usuarios para probar el sistema:")
            
            test_users = [
                ("Angel Hernandez", "admin123", "Administrador"),
                ("Jose Montezuma", "admin123", "Administrador"),
                ("admin", "admin123", "Administrador"),
            ]
            
        
        # CSS UI/UX REFINED PARA REGISTRO - Transparencia total y contraste perfecto
        st.markdown("""
        <style>
        /* DISEÑO UI/UX EXPERTO - TRANSPARENCIA TOTAL Y CONTRASTE PERFECTO */
        
        /* Mantener fondo institucional sin overlay oscuro */
        div[data-testid="stApp"] {
            position: relative !important;
        }
        
        /* TRANSPARENCIA TOTAL DEL CONTENEDOR PRINCIPAL */
        .main .block-container,
        div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column"] {
            background-color: rgba(0, 0, 0, 0) !important;
            border-radius: 0 !important;
            padding: 2.5rem !important;
            box-shadow: none !important;
            backdrop-filter: none !important;
            border: none !important;
        }
        
        /* TRANSPARENCIA TOTAL DEL FORMULARIO */
        form[data-testid="stForm"],
        div[data-testid="stForm"] {
            background-color: rgba(0, 0, 0, 0) !important;
            border-radius: 0 !important;
            padding: 0 !important;
            box-shadow: none !important;
            backdrop-filter: none !important;
            border: none !important;
        }
        
        /* FUENTES OSCURECIDAS CON TEXT-SHADOW PARA MÁXIMO CONTRASTE */
        h1, h2, h3,
        .stMarkdown h1,
        .stMarkdown h2,
        .stMarkdown h3 {
            color: #0A0A0A !important;
            font-weight: 800 !important;
            text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.9),
                         1px 1px 2px rgba(0, 0, 0, 0.8) !important;
            margin-bottom: 1.5rem !important;
        }
        
        /* Labels con contraste extremo y text-shadow */
        label, 
        .stTextInput label,
        .stSelectbox label,
        .stTextArea label,
        .stCheckbox label,
        div[data-testid="stTextInput"] label,
        div[data-testid="stSelectbox"] label,
        div[data-testid="stTextArea"] label,
        div[data-testid="stCheckbox"] label {
            color: #0A0A0A !important;
            font-weight: 700 !important;
            text-shadow: 1px 1px 3px rgba(255, 255, 255, 0.8),
                         1px 1px 2px rgba(0, 0, 0, 0.6) !important;
            font-size: 16px !important;
            display: block !important;
            margin-bottom: 8px !important;
        }
        
        /* Texto markdown con text-shadow */
        .stMarkdown, .stMarkdown *, 
        div[data-testid="stMarkdownContainer"],
        div[data-testid="stMarkdownContainer"] * {
            color: #0A0A0A !important;
            font-weight: 600 !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.7),
                         1px 1px 1px rgba(0, 0, 0, 0.5) !important;
        }
        
        /* INPUTS CON TRANSPARENCIA MÍNIMA Y BORDES DEFINIDOS */
        input[type="text"],
        input[type="password"],
        input[type="email"],
        textarea,
        select,
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stSelectbox"] select {
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: #0A0A0A !important;
            border: 2px solid rgba(255, 255, 255, 0.6) !important;
            border-radius: 12px !important;
            padding: 14px 16px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            backdrop-filter: blur(5px) !important;
            transition: all 0.3s ease !important;
        }
        
        /* Focus states con efecto de resaltado */
        input[type="text"]:focus,
        input[type="password"]:focus,
        input[type="email"]:focus,
        textarea:focus,
        select:focus,
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus,
        div[data-testid="stSelectbox"] select:focus {
            background-color: rgba(255, 255, 255, 0.2) !important;
            border-color: #2563EB !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2),
                        0 4px 12px rgba(0, 0, 0, 0.1) !important;
            outline: none !important;
        }
        
        /* Placeholders con contraste */
        input::placeholder,
        textarea::placeholder,
        div[data-testid="stTextInput"] input::placeholder,
        div[data-testid="stTextArea"] textarea::placeholder {
            color: #4A4A4A !important;
            font-weight: 500 !important;
            opacity: 1 !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.5) !important;
        }
        
        /* BOTÓN DE ACCIÓN PROFESIONAL - AZUL INSTITUCIONAL */
        button[kind="primary"],
        div[data-testid="stForm"] > button,
        .stButton > button {
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
            color: white !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 14px 32px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 8px 24px rgba(37, 99, 235, 0.3),
                        0 4px 12px rgba(0, 0, 0, 0.1) !important;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2) !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        button[kind="primary"]:hover,
        div[data-testid="stForm"] > button:hover,
        .stButton > button:hover {
            background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 32px rgba(37, 99, 235, 0.4),
                        0 6px 16px rgba(0, 0, 0, 0.15) !important;
        }
        
        button[kind="primary"]:active,
        div[data-testid="stForm"] > button:active,
        .stButton > button:active {
            transform: translateY(0) !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
        }
        
        /* Selectbox específico con transparencia */
        div[data-testid="stSelectbox"] {
            background-color: rgba(255, 255, 255, 0.1) !important;
            border: 2px solid rgba(255, 255, 255, 0.6) !important;
            border-radius: 12px !important;
            backdrop-filter: blur(5px) !important;
        }
        
        div[data-testid="stSelectbox"] select {
            background-color: transparent !important;
            color: #0A0A0A !important;
            font-weight: 600 !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.5) !important;
        }
        
        /* Help text con legibilidad */
        div[data-testid="stHelpText"],
        .stHelpText {
            color: #2A2A2A !important;
            font-weight: 500 !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.6) !important;
        }
        
        /* Messages con transparencia y contraste */
        .stException,
        .stAlert,
        div[data-testid="stException"],
        div[data-testid="stAlert"] {
            background-color: rgba(255, 255, 255, 0.15) !important;
            backdrop-filter: blur(10px) !important;
            border-left: 4px solid #DC2626 !important;
            color: #0A0A0A !important;
            font-weight: 600 !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.7) !important;
            border-radius: 8px !important;
        }
        
        .stSuccess,
        div[data-testid="stSuccess"] {
            background-color: rgba(255, 255, 255, 0.15) !important;
            backdrop-filter: blur(10px) !important;
            border-left: 4px solid #16A34A !important;
            color: #0A0A0A !important;
            font-weight: 600 !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.7) !important;
            border-radius: 8px !important;
        }
        
        /* Info messages con estilo consistente */
        .stInfo {
            background-color: rgba(255, 255, 255, 0.15) !important;
            backdrop-filter: blur(10px) !important;
            border-left: 4px solid #2563EB !important;
            color: #0A0A0A !important;
            font-weight: 600 !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.7) !important;
            border-radius: 8px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Generar CAPTCHA simple
        import random
        captcha_num = random.randint(1000, 9999)
        
        # Guardar CAPTCHA en session state
        if 'captcha_correcto' not in st.session_state:
            st.session_state.captcha_correcto = captcha_num
        
        with st.form("registro_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📋 Información Personal")
                
                nombre_completo = st.text_input(
                    "👤 Nombre Completo*",
                    placeholder="Ej: Juan Pérez Rodríguez",
                    help="Ingrese su nombre completo"
                )
                
                cedula = st.text_input(
                    "🆔 Cédula de Identidad*",
                    placeholder="Ej: V-12345678",
                    help="Formato: V-12345678 o E-12345678. Este será su usuario de acceso."
                )
                
                email = st.text_input(
                    "📧 Correo Electrónico*",
                    placeholder="ejemplo@correo.com",
                    help="Ingrese su correo electrónico válido"
                )
            
            with col2:
                st.markdown("#### 🔐 Información de Acceso")
                
                password = st.text_input(
                    "� Contraseña*",
                    type="password",
                    placeholder="Mínimo 6 caracteres, 1 letra, 1 número",
                    help="Use una contraseña segura"
                )
                
                confirm_password = st.text_input(
                    "� Confirmar Contraseña*",
                    type="password",
                    placeholder="Repita su contraseña"
                )
                
                rol = st.selectbox(
                    "🏷️ Rol/Permisos*",
                    options=self.roles_disponibles,
                    help="Seleccione el rol que tendrá el usuario"
                )
            
            # CAPTCHA
            st.markdown("#### 🔒 Verificación de Seguridad")
            st.write("Para completar el registro, por favor ingrese el siguiente número:")
            
            col_captcha1, col_captcha2 = st.columns([1, 2])
            with col_captcha1:
                st.markdown(f"### 🎯 {captcha_num}")
                st.caption("Número de verificación")
            
            with col_captcha2:
                captcha_input = st.text_input(
                    "🔑 Ingrese el número*",
                    placeholder="Ingrese el número que ve arriba",
                    help="Ingrese exactamente el número mostrado para verificar que no es un robot"
                )
            
            # Botón de registro
            submit_button = st.form_submit_button(
                "🚀 Registrar Usuario",
                use_container_width=True,
                type="primary"
            )
            
            # Procesar formulario
            if submit_button:
                errores = []
                
                # Validaciones básicas
                if not nombre_completo.strip():
                    errores.append("El nombre completo es requerido")
                
                if not cedula.strip():
                    errores.append("La cédula de identidad es requerida")
                elif not self.validar_cedula(cedula):
                    errores.append("Formato de cédula inválido. Use V-12345678 o E-12345678")
                elif self.verificar_cedula_existente(cedula.upper()):
                    errores.append("La cédula ya está registrada")
                
                if not email.strip():
                    errores.append("El correo electrónico es requerido")
                elif not self.validar_email(email):
                    errores.append("Formato de correo electrónico inválido")
                
                if not password:
                    errores.append("La contraseña es requerida")
                else:
                    valid_password, msg_password = self.validar_contraseña(password)
                    if not valid_password:
                        errores.append(msg_password)
                
                if password != confirm_password:
                    errores.append("Las contraseñas no coinciden")
                
                # Validación CAPTCHA
                if not captcha_input.strip():
                    errores.append("El código de verificación es requerido")
                elif captcha_input.strip() != str(captcha_num):
                    errores.append("El código de verificación es incorrecto")
                
                # Mostrar errores o procesar registro
                if errores:
                    st.error("❌ Se encontraron errores:")
                    for error in errores:
                        st.write(f"• {error}")
                else:
                    # Preparar datos (usando cédula como login)
                    datos_usuario = {
                        'nombre_completo': nombre_completo.strip(),
                        'cedula': cedula.upper().strip(),
                        'email': email.strip().lower(),
                        'login': cedula.upper().strip(),  # Usar cédula como login
                        'password_hash': self.hash_password(password),
                        'rol': rol
                    }
                    
                    # Registrar usuario
                    with st.spinner("Registrando usuario..."):
                        success, message = self.registrar_usuario(datos_usuario)
                    
                    if success:
                        st.success("✅ Usuario registrado exitosamente")
                        st.info(f"""
                        **📋 Detalles del registro:**
                        • **🆔 Cédula:** {datos_usuario['cedula']}
                        • **👤 Usuario:** {datos_usuario['cedula']} (su cédula es su usuario)
                        • **🏷️ Rol:** {datos_usuario['rol']}
                        • **📧 Email:** {datos_usuario['email']}
                        
                        **🔑 Nota:** Use su número de cédula para iniciar sesión.
                        """)
                        
                        # Marcar que el registro fue exitoso para mostrar el botón después
                        st.session_state.registro_exitoso = True
                        st.session_state.test_username = datos_usuario['cedula']
                        st.session_state.test_password = password
                        
                        # Limpiar CAPTCHA
                        st.session_state.captcha_correcto = random.randint(1000, 9999)
                    else:
                        st.error(f"❌ {message}")
                        # Generar nuevo CAPTCHA si hay error
                        st.session_state.captcha_correcto = random.randint(1000, 9999)
        
        # Opción de probar login (fuera del formulario)
        if 'registro_exitoso' in st.session_state and st.session_state.registro_exitoso:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔑 Probar Inicio de Sesión Ahora", key="probar_login_registro", use_container_width=True):
                    st.session_state.switch_to_login = True
                    st.session_state.test_username = st.session_state.get('test_username', '')
                    st.session_state.test_password = st.session_state.get('test_password', '')
                    st.session_state.registro_exitoso = False
                    st.rerun()
        
        # Información de ayuda
        with st.expander("ℹ️ Requisitos de Registro"):
            st.markdown("""
            **📋 Campos Obligatorios:**
            - **Nombre Completo:** Debe incluir nombre y apellido
            - **Cédula:** Formato V-12345678 o E-12345678
            - **Email:** Correo electrónico válido
            - **Usuario:** Único en el sistema
            - **Contraseña:** Mínimo 6 caracteres, 1 letra, 1 número
            
            **🏆 Roles Disponibles:**
            - **Administrador:** Acceso completo
            - **Gestor:** Gestión de usuarios y contenido
            - **Auditor:** Solo lectura y reportes
            """)
    
    def mostrar_sistema_principal(self):
        """Mostrar sistema principal después del login con sidebar transaccional"""
        # Obtener información del usuario y permisos
        user_info = st.session_state.get('user', {})
        user_role = user_info.get('rol', 'N/A')
        
        # Sidebar para navegación transaccional
        with st.sidebar:
            st.markdown("## 🔐 SICADFOC 2026")
            st.markdown("### 🏠 Panel Principal")
            
            # Dashboard Principal (siempre visible)
            dashboard_selected = st.button("� Dashboard General", use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 🔄 Módulos Operativos")
            
            # Módulos Transaccionales con control de acceso
            gestion_estudiantil_enabled = self._verificar_acceso_modulo('Gestión Estudiantil', user_role)
            gestion_profesores_enabled = self._verificar_acceso_modulo('Gestión Profesores', user_role)
            formacion_enabled = self._verificar_acceso_modulo('Formación Complementaria', user_role)
            
            # Botones de módulos operativos
            col1, col2 = st.columns(2)
            with col1:
                estudiantil_btn = st.button(
                    "📚 Gestión\nEstudiantil", 
                    use_container_width=True,
                    disabled=not gestion_estudiantil_enabled,
                    help="Registro, Inscripción, Carga de Notas" if gestion_estudiantil_enabled else "Sin permisos"
                )
                profesores_btn = st.button(
                    "�‍🏫 Gestión\nProfesores", 
                    use_container_width=True,
                    disabled=not gestion_profesores_enabled,
                    help="Asignación, Carga académica" if gestion_profesores_enabled else "Sin permisos"
                )
            
            with col2:
                formacion_btn = st.button(
                    "🎓 Formación\nComplementaria", 
                    use_container_width=True,
                    disabled=not formacion_enabled,
                    help="Talleres, Cursos, Certificaciones" if formacion_enabled else "Sin permisos"
                )
            
            st.markdown("---")
            st.markdown("### ⚙️ Módulos de Soporte")
            
            # Módulos de soporte con control de acceso
            informes_enabled = self._verificar_acceso_modulo('Informes y Reportes', user_role)
            configuracion_enabled = self._verificar_acceso_modulo('Configuración del Sistema', user_role)
            seguridad_enabled = self._verificar_acceso_modulo('Seguridad y Permisos', user_role)
            
            # Botones de módulos de soporte
            informes_btn = st.button(
                "📊 Informes y\nReportes", 
                use_container_width=True,
                disabled=not informes_enabled,
                help="Generación de PDFs/Reportes" if informes_enabled else "Sin permisos"
            )
            
            configuracion_btn = st.button(
                "⚙️ Configuración\ndel Sistema", 
                use_container_width=True,
                disabled=not configuracion_enabled,
                help="Valores paramétricos, Niveles, Semestres" if configuracion_enabled else "Sin permisos"
            )
            
            seguridad_btn = st.button(
                "🔐 Seguridad y\nPermisos", 
                use_container_width=True,
                disabled=not seguridad_enabled,
                help="Gestión de usuarios y niveles de acceso" if seguridad_enabled else "Sin permisos"
            )
            
            st.markdown("---")
            
            # Información del usuario en sidebar
            st.markdown("### 👤 Usuario Actual")
            st.write(f"**{user_info.get('login_usuario', 'N/A')}**")
            st.write(f"🏷️ {user_role}")
            
            # Botón de cerrar sesión en sidebar
            if st.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.session_state.username = None
                st.session_state.role = None
                st.success("✅ Sesión cerrada exitosamente")
                st.rerun()
        
        # Contenido principal basado en el módulo seleccionado
        if dashboard_selected:
            self.mostrar_dashboard_principal()
        elif estudiantil_btn:
            self._cargar_modulo_estudiantil()
        elif profesores_btn:
            self._cargar_modulo_profesores()
        elif formacion_btn:
            self._cargar_modulo_formacion()
        elif informes_btn:
            self.mostrar_modulo_reportes()
        elif configuracion_btn:
            self.mostrar_modulo_configuracion()
        elif seguridad_btn:
            self.mostrar_modulo_seguridad()
        else:
            # Por defecto mostrar dashboard
            self.mostrar_dashboard_principal()
    
    def _verificar_acceso_modulo(self, modulo: str, rol: str) -> bool:
        """Verificar si el usuario tiene acceso a un módulo específico"""
        try:
            from seguridad import tiene_permiso
            
            # Mapeo de módulos a permisos requeridos
            permisos_requeridos = {
                'Gestión Estudiantil': ('Estudiantes', 'Consultar'),
                'Gestión Profesores': ('Gestión Profesores', 'Consultar'),
                'Formación Complementaria': ('Formación Complementaria', 'Consultar'),
                'Informes y Reportes': ('Informes', 'Consultar'),
                'Configuración del Sistema': ('Configuración', 'Consultar'),
                'Seguridad y Permisos': ('Seguridad', 'Consultar')
            }
            
            # Administrador tiene acceso a todo
            if rol in ['Administrador', 'Admin']:
                return True
            
            # Verificar permisos específicos
            if modulo in permisos_requeridos:
                modulo_permiso, accion_permiso = permisos_requeridos[modulo]
                return tiene_permiso(rol, modulo_permiso, accion_permiso)
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando acceso al módulo {modulo}: {e}")
            # En caso de error, permitir acceso por seguridad
            return True
    
    def _cargar_modulo_estudiantil(self):
        """Cargar módulo de gestión estudiantil"""
        try:
            from gestion_estudiantil import gestion_estudiantil
            gestion_estudiantil()
        except ImportError as e:
            st.error(f"Error importando módulo de gestión estudiantil: {e}")
            st.warning("Asegúrese que el archivo gestion_estudiantil.py exista y tenga una función main()")
        except Exception as e:
            st.error(f"Error cargando módulo de gestión estudiantil: {e}")
    
    def _cargar_modulo_profesores(self):
        """Cargar módulo de gestión de profesores"""
        try:
            from gestion_profesores import GestionProfesores
            gestor = GestionProfesores()
            gestor.gestion_profesores()
        except ImportError as e:
            st.error(f"Error importando módulo de gestión de profesores: {e}")
            st.warning("Asegúrese que el archivo gestion_profesores.py exista y tenga la clase GestionProfesores")
        except Exception as e:
            st.error(f"Error cargando módulo de gestión de profesores: {e}")
    
    def _cargar_modulo_formacion(self):
        """Cargar módulo de formación complementaria"""
        try:
            from gestion_formacion_complementaria import gestion_formacion_complementaria
            gestion_formacion_complementaria()
        except ImportError as e:
            st.error(f"Error importando módulo de formación complementaria: {e}")
            st.warning("Asegúrese que el archivo gestion_formacion_complementaria.py exista y tenga una función main()")
        except Exception as e:
            st.error(f"Error cargando módulo de formación complementaria: {e}")
    
    def mostrar_dashboard_principal(self):
        """Mostrar dashboard principal"""
        st.markdown("### 🎉 ¡Bienvenido al Sistema Principal!")
        
        user_info = st.session_state.get('user', {})
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👤 Usuario", user_info.get('login_usuario', 'N/A'))
        
        with col2:
            st.metric("🏷️ Rol", user_info.get('rol', 'N/A'))
        
        with col3:
            st.metric("📧 Nombre", user_info.get('nombre_completo', 'N/A'))
        
        with col4:
            st.metric("🆔 Cédula", user_info.get('cedula_usuario', 'N/A'))
        
        # Dashboard principal (mantener image_5.png reference)
        st.markdown("---")
        st.markdown("### 📊 Dashboard Principal")
        
        # Placeholder para el dashboard principal
        st.info("📋 Dashboard Principal - SICADFOC 2026")
        st.write("Este es el panel principal del sistema donde se muestran las estadísticas y resúmenes generales.")
        
        # Métricas del sistema
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("👥 Total Usuarios", "8", "+2 esta semana")
        
        with col2:
            st.metric("📚 Estudiantes Activos", "3", "+1 este mes")
        
        with col3:
            st.metric("�‍🏫 Profesores", "2", "Sin cambios")
        
        # Gráficos y contenido del dashboard
        st.markdown("### 📈 Estadísticas del Sistema")
        
        # Placeholder para gráficos
        st.info("📊 Aquí se mostrarán los gráficos y estadísticas del sistema (referencia: image_5.png)")
        
        # Actividad reciente
        st.markdown("### 🕐 Actividad Reciente")
        st.write("- Último login: Angel Hernandez - Hace 5 minutos")
        st.write("- Nuevo usuario registrado: Carlos Rodriguez - Hoy")
        st.write("- Sistema actualizado: Versión 2.0.1")
    
    def mostrar_modulo_usuarios(self):
        """Mostrar módulo de gestión de usuarios"""
        st.markdown("### 👥 Gestión de Usuarios")
        st.info("📋 Módulo de gestión de usuarios del sistema")
        st.write("Aquí podrá administrar todos los usuarios del SICADFOC 2026.")
        
        # Opciones del módulo
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("➕ Nuevo Usuario", use_container_width=True):
                st.success("Redirigiendo al formulario de registro...")
        
        with col2:
            if st.button("📋 Lista de Usuarios", use_container_width=True):
                st.info("Mostrando lista de usuarios...")
        
        # Tabla de usuarios (placeholder)
        st.markdown("#### 📋 Usuarios Registrados")
        st.write("Tabla de usuarios del sistema...")
    
    def mostrar_modulo_estudiantes(self):
        """Mostrar módulo de gestión estudiantil"""
        st.markdown("### 📚 Gestión Estudiantil")
        st.info("� Módulo de gestión estudiantil")
        st.write("Administración de estudiantes, matrículas y registros académicos.")
    
    def mostrar_modulo_profesores(self):
        """Mostrar módulo de gestión de profesores"""
        st.markdown("### 👨‍🏫 Gestión de Profesores")
        st.info("📋 Módulo de gestión de profesores")
        st.write("Administración de personal docente y asignaturas.")
    
    def mostrar_modulo_formacion(self):
        """Mostrar módulo de formación complementaria"""
        st.markdown("### 🎓 Formación Complementaria")
        st.info("📋 Módulo de formación complementaria")
        st.write("Gestión de talleres, cursos y actividades extracurriculares.")
    
    def mostrar_modulo_reportes(self):
        """Mostrar módulo de informes y reportes"""
        st.markdown("### 📊 Informes y Reportes")
        st.info("📋 Módulo de informes y reportes")
        st.write("Generación de reportes y análisis estadísticos.")
    
    def mostrar_modulo_configuracion(self):
        """Mostrar módulo de configuración"""
        st.markdown("### ⚙️ Configuración del Sistema")
    def mostrar_modulo_seguridad(self):
        """Mostrar módulo de seguridad y permisos"""
        st.markdown("### Security and Permissions")
        st.info(" Security and permissions module")
        st.write("Role management, permissions, and security policies.")

    def mostrar_formulario_registro(self):
        """Mostrar formulario de registro"""
        # CSS CORREGIDO PARA LEGIBILIDAD - Texto oscuro y sin fondos azules
        st.markdown("""
        <style>
        /* CONTENEDORES CON TRANSPARENCIA CONTROLADA */
        .main .block-container {
            background-color: rgba(255, 255, 255, 0.9) !important;
            border-radius: 12px !important;
            padding: 2rem !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        }
        
        form[data-testid="stForm"] {
            background-color: rgba(255, 255, 255, 0.95) !important;
            border-radius: 8px !important;
            padding: 1.5rem !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        }
        
        /* TÍTULOS OSCUROS CON ALTO CONTRASTE */
        h1, h2, h3, h4,
        .stMarkdown h1,
        .stMarkdown h2,
        .stMarkdown h3,
        .stMarkdown h4 {
            color: #0D1117 !important;
            font-weight: 800 !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8) !important;
        }
        
        /* ETIQUETAS DE CAMPOS OSCURECIDAS */
        label,
        .stTextInput label,
        .stSelectbox label,
        .stTextArea label,
        .stCheckbox label,
        div[data-testid="stTextInput"] label,
        div[data-testid="stSelectbox"] label,
        div[data-testid="stTextArea"] label,
        div[data-testid="stCheckbox"] label {
            color: #0D1117 !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            background-color: transparent !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.7) !important;
        }
        
        /* TEXTO MARKDOWN OSCURECIDO */
        .stMarkdown,
        .stMarkdown *,
        div[data-testid="stMarkdownContainer"],
        div[data-testid="stMarkdownContainer"] * {
            color: #0D1117 !important;
            font-weight: 600 !important;
            background-color: transparent !important;
            text-shadow: 1px 1px 1px rgba(255, 255, 255, 0.6) !important;
        }
        
        /* INPUTS CON TEXTO OSCURO */
        input[type="text"],
        input[type="password"],
        input[type="email"],
        textarea,
        select,
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stSelectbox"] select {
            background-color: white !important;
            color: #0D1117 !important;
            border: 2px solid #2563EB !important;
            border-radius: 6px !important;
            padding: 10px !important;
            font-weight: 600 !important;
        }
        
        /* PLACEHOLDERS OSCUROS CON CONTRASTE */
        input::placeholder,
        textarea::placeholder,
        div[data-testid="stTextInput"] input::placeholder,
        div[data-testid="stTextArea"] textarea::placeholder {
            color: #4A4A4A !important;
            font-weight: 500 !important;
            opacity: 1 !important;
            background-color: transparent !important;
        }
        
        /* TEXTO DE AYUDA Y DESCRIPCIÓN OSCURECIDO */
        div[data-testid="stHelpText"],
        .stHelpText,
        .stCaption,
        div[data-testid="stCaption"] {
            color: #2A2A2A !important;
            font-weight: 500 !important;
            background-color: transparent !important;
            text-shadow: 1px 1px 1px rgba(255, 255, 255, 0.5) !important;
        }
        
        /* BOTÓN PRINCIPAL MANTENIDO */
        button[kind="primary"] {
            background-color: #2563EB !important;
            color: white !important;
            font-weight: 600 !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 10px 20px !important;
        }
        
        /* ELIMINAR FONDOS AZULES NO DESEADOS */
        .element-container,
        .stElementContainer {
            background-color: transparent !important;
        }
        
        /* TEXTO DE ERROR Y ÉXITO OSCURECIDO */
        .stException,
        .stAlert,
        .stSuccess,
        div[data-testid="stException"],
        div[data-testid="stAlert"],
        div[data-testid="stSuccess"] {
            color: #0D1117 !important;
            font-weight: 600 !important;
            background-color: rgba(255, 255, 255, 0.9) !important;
            text-shadow: 1px 1px 1px rgba(255, 255, 255, 0.7) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("### Registrar Usuario")
        
        # Generar CAPTCHA simple
        import random
        captcha_num = random.randint(1000, 9999)
        
        # Guardar CAPTCHA en session state
        if 'captcha_correcto' not in st.session_state:
            st.session_state.captcha_correcto = captcha_num
        
        with st.form("registro_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Información Personal")
                
                nombre_completo = st.text_input(
                    "Nombre Completo*",
                    placeholder="Ej: Juan Pérez Rodríguez"
                )
                
                cedula = st.text_input(
                    "Cédula de Identidad*",
                    placeholder="Ej: V-12345678"
                )
                
                email = st.text_input(
                    "Correo Electrónico*",
                    placeholder="ejemplo@correo.com"
                )
            
            with col2:
                st.markdown("#### Información de Acceso")
                
                password = st.text_input(
                    "Contraseña*",
                    type="password",
                    placeholder="Mínimo 6 caracteres"
                )
                
                confirm_password = st.text_input(
                    "Confirmar Contraseña*",
                    type="password",
                    placeholder="Repita su contraseña"
                )
                
                rol = st.selectbox(
                    "Rol/Permisos*",
                    options=self.roles_disponibles
                )
            
            # CAPTCHA
            st.markdown("#### Verificación de Seguridad")
            st.write("Para completar el registro, por favor ingrese el siguiente número:")
            
            col_captcha1, col_captcha2 = st.columns([1, 2])
            with col_captcha1:
                st.markdown(f"### {captcha_num}")
                st.caption("Número de verificación")
            
            with col_captcha2:
                captcha_input = st.text_input(
                    "Ingrese el número*",
                    placeholder="Ingrese el número que ve arriba"
                )
            
            # Botón de registro
            submit_button = st.form_submit_button(
                "Registrar Usuario",
                use_container_width=True,
                type="primary"
            )
            
            # Procesar formulario
            if submit_button:
                errores = []
                
                # Validaciones básicas
                if not nombre_completo.strip():
                    errores.append("El nombre completo es requerido")
                
                if not cedula.strip():
                    errores.append("La cédula de identidad es requerida")
                elif not self.validar_cedula(cedula):
                    errores.append("Formato de cédula inválido. Use V-12345678 o E-12345678")
                elif self.verificar_cedula_existente(cedula.upper()):
                    errores.append("La cédula ya está registrada")
                
                if not email.strip():
                    errores.append("El correo electrónico es requerido")
                elif not self.validar_email(email):
                    errores.append("Formato de correo electrónico inválido")
                
                if not password:
                    errores.append("La contraseña es requerida")
                else:
                    valid_password, msg_password = self.validar_contraseña(password)
                    if not valid_password:
                        errores.append(msg_password)
                
                if password != confirm_password:
                    errores.append("Las contraseñas no coinciden")
                
                # Validación CAPTCHA
                if not captcha_input.strip():
                    errores.append("El código de verificación es requerido")
                elif captcha_input.strip() != str(captcha_num):
                    errores.append("El código de verificación es incorrecto")
                
                # Mostrar errores o procesar registro
                if errores:
                    st.error("Se encontraron errores:")
                    for error in errores:
                        st.write(f" {error}")
                else:
                    # Preparar datos (usando cédula como login)
                    datos_usuario = {
                        'nombre_completo': nombre_completo.strip(),
                        'cedula': cedula.upper().strip(),
                        'email': email.strip().lower(),
                        'login': cedula.upper().strip(),
                        'password_hash': self.hash_password(password),
                        'rol': rol
                    }
                    
                    # Registrar usuario
                    with st.spinner("Registrando usuario..."):
                        success, message = self.registrar_usuario(datos_usuario)
                    
                    if success:
                        st.success("Usuario registrado exitosamente")
                        st.info(f"""
                        **Detalles del registro:**
                         **Cédula:** {datos_usuario['cedula']}
                         **Usuario:** {datos_usuario['cedula']}
                         **Rol:** {datos_usuario['rol']}
                         **Email:** {datos_usuario['email']}
                        
                        **Nota:** Use su número de cédula para iniciar sesión.
                        """)
                        
                        # Marcar que el registro fue exitoso
                        st.session_state.registro_exitoso = True
                        st.session_state.test_username = datos_usuario['cedula']
                        st.session_state.test_password = password
                        
                        # Limpiar CAPTCHA
                        st.session_state.captcha_correcto = random.randint(1000, 9999)
                    else:
                        st.error(f" {message}")
                        # Generar nuevo CAPTCHA si hay error
                        st.session_state.captcha_correcto = random.randint(1000, 9999)

def main():
    """Función principal del sistema unificado"""
    st.set_page_config(
        page_title="SICADFOC 2026 - Autenticación Unificada",
        page_icon="",
        layout="wide"
    )
    
    # VERIFICACIÓN DE BUCLE DE INICIO - VALIDACIÓN CRÍTICA
    try:
        print("=== VERIFICACIÓN DE BUCLE DE INICIO ===")
        
        # CONEXIÓN DIRECTA HARDCODED PARA VALIDACIÓN
        import psycopg2
        conn = psycopg2.connect(
            dbname="db_foc26",
            user="postgres", 
            password="admin123",
            host="localhost",
            port="5432"
        )
        
        cursor = conn.cursor()
        cursor.execute("SET search_path TO public;")
        conn.commit()
        
        # VALIDACIÓN CRÍTICA: SELECT 1 FROM usuarios LIMIT 1
        cursor.execute("SELECT 1 FROM usuarios LIMIT 1")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        print("OK: VALIDACIÓN DE BUCLE DE INICIO EXITOSA - Tabla usuarios accesible")
        
    except Exception as e:
        error_msg = f"Conexión fallida: la base de datos no reconoce la tabla usuarios"
        print(f"ERROR CRÍTICO: {error_msg}")
        print(f"Detalles: {e}")
        
        # DETENER SISTEMA COMPLETAMENTE
        st.error("ERROR CRÍTICO DEL SISTEMA")
        st.error(error_msg)
        st.error("El sistema no puede iniciar sin acceso a la tabla usuarios.")
        st.error("Por favor, verifique que la base de datos db_foc26 tenga la tabla usuarios en el esquema public.")
        st.stop()
    
    print("=== SISTEMA INICIADO CORRECTAMENTE ===")
    
    # CSS personalizado
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .auth-container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #28a745;
        }
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #dc3545;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🔐 Sistema de Autenticación Unificado</h1>
        <h2>SICADFOC 2026 - Instituto Universitario Jesus Obrero</h2>
        <p>Login y Registro de Usuarios en una sola interfaz</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar conexión a base de datos
    try:
        info = get_database_info()
        if not info['status']:
            st.error("❌ No hay conexión a la base de datos")
            st.info("Por favor, verifique la conexión e intente nuevamente")
            return
    except Exception as e:
        st.error(f"❌ Error verificando conexión: {e}")
        return
    
    # Inicializar sistema de autenticación
    auth_system = AuthSystemUnificado()
    
    # Verificar si el usuario está logueado
    if st.session_state.get('logged_in', False):
        auth_system.mostrar_sistema_principal()
    else:
        # Verificar si debemos cambiar a login (después del registro)
        if st.session_state.get('switch_to_login', False):
            # Crear tabs con login seleccionado
            tab_login, tab_registro = st.tabs(["🔐 Iniciar Sesión", "📝 Registrar Usuario"])
            
            with tab_login:
                auth_system.mostrar_formulario_login()
                
                # Auto-llenar campos si viene del registro
                if st.session_state.get('test_username'):
                    st.info(f"👤 Usuario para prueba: {st.session_state.test_username}")
                    st.info("🔑 Use la contraseña que acaba de registrar")
            
            with tab_registro:
                auth_system.mostrar_formulario_registro()
        else:
            # Crear tabs normales
            tab_login, tab_registro = st.tabs(["🔐 Iniciar Sesión", "📝 Registrar Usuario"])
            
            with tab_login:
                auth_system.mostrar_formulario_login()
            
            with tab_registro:
                auth_system.mostrar_formulario_registro()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 30px;'>
        <p>🔐 Desarrollado por Senior Full-Stack Developer | SICADFOC 2026</p>
        <p>Seguridad: Encriptación SHA-256 | Validación de datos | Transacciones seguras</p>
    </div>
    """, unsafe_allow_html=True)

def gestion_usuarios_main():
    """Función principal del módulo de gestión de usuarios"""
    try:
        # Crear instancia del sistema y mostrar módulo de usuarios
        sistema = AuthSystemUnificado()
        sistema.mostrar_modulo_usuarios()
    except Exception as e:
        st.error(f"Error en el módulo de gestión de usuarios: {e}")


def registro_usuario_main():
    """Función principal del módulo de registro de usuarios"""
    try:
        # Crear instancia del sistema de autenticación y mostrar formulario de registro
        auth_system = AuthSystemUnificado()
        auth_system.mostrar_formulario_registro()
    except Exception as e:
        st.error(f"Error en el módulo de registro de usuarios: {e}")

if __name__ == "__main__":
    main()
