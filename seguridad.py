#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Seguridad y Permisología para SICADFOC 2026
Control de acceso por roles y validación de identidad
"""

import functools
import streamlit as st
from typing import Callable, Any

# Roles del sistema
ROLES = {
    'Administrador': 'admin',
    'Profesor': 'profesor',
    'Estudiante': 'estudiante'
}

class SeguridadFOC26:
    """Clase para manejo de seguridad y permisos"""
    
    @staticmethod
    def get_user_role() -> str:
        """Obtener el rol del usuario logueado con normalización"""
        if 'user' not in st.session_state:
            return None
        rol = st.session_state['user'].get('rol', None)
        if rol:
            # NORMALIZACIÓN: strip().capitalize() para evitar errores de espacios/mayúsculas
            return rol.strip().capitalize()
        return None
    
    @staticmethod
    def get_user_cedula() -> str:
        """Obtener la cédula del usuario logueado"""
        if 'user' not in st.session_state:
            return None
        return st.session_state['user'].get('cedula_usuario', None)
    
    @staticmethod
    def is_admin() -> bool:
        """UNIFICACIÓN DE ROLES: Comparación robusta ADMIN/ADMINISTRADOR"""
        # SIMPLIFICACIÓN: Si es Admin acceso total
        user_rol = str(st.session_state.get('user', {}).get('rol', '')).strip().upper()
        return user_rol in ['ADMIN', 'ADMINISTRADOR']
    
    @staticmethod
    def is_profesor() -> bool:
        """Verificar si el usuario es profesor con normalización"""
        rol = SeguridadFOC26.get_user_role()
        return rol == 'Profesor' if rol else False
    
    @staticmethod
    def is_estudiante() -> bool:
        """Verificar si el usuario es estudiante con normalización"""
        rol = SeguridadFOC26.get_user_role()
        return rol == 'Estudiante' if rol else False
    
    @staticmethod
    def can_create_taller() -> bool:
        """SIMPLIFICACIÓN: Admin acceso total, otros con restricciones"""
        user_rol = str(st.session_state.get('user', {}).get('rol', '')).strip().upper()
        if user_rol in ['ADMIN', 'ADMINISTRADOR']:
            return True
        return user_rol == 'PROFESOR'
    
    @staticmethod
    def can_delete_any() -> bool:
        """SIMPLIFICACIÓN: Admin acceso total"""
        user_rol = str(st.session_state.get('user', {}).get('rol', '')).strip().upper()
        return user_rol in ['ADMIN', 'ADMINISTRADOR']
    
    @staticmethod
    def can_view_own_data() -> bool:
        """SIMPLIFICACIÓN: Admin acceso total, estudiante solo sus datos"""
        user_rol = str(st.session_state.get('user', {}).get('rol', '')).strip().upper()
        if user_rol in ['ADMIN', 'ADMINISTRADOR']:
            return True
        return user_rol == 'ESTUDIANTE'
    
    @staticmethod
    def can_view_inscriptions() -> bool:
        """SIMPLIFICACIÓN: Todos los roles pueden ver inscripciones"""
        return True
    
    @staticmethod
    def can_view_taller_list() -> bool:
        """SIMPLIFICACIÓN: Todos los roles pueden ver talleres"""
        return True
    
    @staticmethod
    def can_inscribirse() -> bool:
        """SIMPLIFICACIÓN: Admin acceso total, estudiante inscribirse"""
        user_rol = str(st.session_state.get('user', {}).get('rol', '')).strip().upper()
        if user_rol in ['ADMIN', 'ADMINISTRADOR']:
            return True
        return user_rol == 'ESTUDIANTE'
    
    @staticmethod
    def can_view_any_data() -> bool:
        """Verificar si puede ver cualquier dato (admin tiene acceso total)"""
        # PRIORIDAD ABSOLUTA: Admin ve TODO sin restricciones
        return SeguridadFOC26.is_admin()
    
    @staticmethod
    def can_manage_users() -> bool:
        """Verificar si puede gestionar usuarios (solo admin)"""
        return SeguridadFOC26.is_admin()
    
    @staticmethod
    def can_access_all_modules() -> bool:
        """Verificar si puede acceder a todos los módulos (solo admin)"""
        return SeguridadFOC26.is_admin()

# Decoradores para seguridad
def admin_required(func: Callable) -> Callable:
    """Decorador para requerir rol de administrador"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not SeguridadFOC26.is_admin():
            st.error("Acceso denegado. Se requiere rol de Administrador.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def profesor_required(func: Callable) -> Callable:
    """Decorador para requerir rol de profesor"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not SeguridadFOC26.is_profesor() and not SeguridadFOC26.is_admin():
            st.error("Acceso denegado. Se requiere rol de Profesor.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def estudiante_required(func: Callable) -> Callable:
    """Decorador para requerir rol de estudiante"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not SeguridadFOC26.is_estudiante():
            st.error("Acceso denegado. Se requiere rol de Estudiante.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def login_required(func: Callable) -> Callable:
    """Decorador para requerir login"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'user' not in st.session_state:
            st.error("Acceso denegado. Debe iniciar sesión.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

# Funciones de validación de identidad
def validar_acceso_propio_datos(cedula_registro: str) -> bool:
    """Validar que el usuario solo vea sus propios datos"""
    user_cedula = SeguridadFOC26.get_user_cedula()
    
    # Admin puede ver todos los datos
    if SeguridadFOC26.is_admin():
        return True
    
    # Estudiante solo puede ver sus propios datos
    if SeguridadFOC26.is_estudiante():
        return user_cedula == cedula_registro
    
    # Profesor no puede ver datos de otros estudiantes
    return False

def validar_acceso_taller_propio(id_profesor_taller: int, id_usuario_profesor: int) -> bool:
    """Validar que el profesor solo vea sus talleres"""
    # Admin puede ver todos los talleres
    if SeguridadFOC26.is_admin():
        return True
    
    # Profesor solo puede ver sus talleres
    if SeguridadFOC26.is_profesor():
        return id_profesor_taller == id_usuario_profesor
    
    # Estudiante no puede ver gestión de talleres
    return False

def filtrar_datos_por_usuario(query_result: list, campo_cedula: str = 'cedula_usuario') -> list:
    """SIMPLIFICACIÓN: Admin acceso total, otros con filtros"""
    # SIMPLIFICACIÓN: Si es Admin acceso total
    user_rol = str(st.session_state.get('user', {}).get('rol', '')).strip().upper()
    if user_rol in ['ADMIN', 'ADMINISTRADOR']:
        return query_result
    
    user_cedula = SeguridadFOC26.get_user_cedula()
    if not user_cedula:
        return []
    
    # Filtrar por cédula del usuario (solo para no-admin)
    return [item for item in query_result if item.get(campo_cedula) == user_cedula]

# Funciones de UI para seguridad
def mostrar_boton_eliminar(key: str = None) -> bool:
    """Determina si mostrar botón eliminar"""
    if not SeguridadFOC26.can_delete_any():
        return False
    
    if key:
        return st.button("Eliminar", key=f"eliminar_{key}", type="secondary")
    return st.button("Eliminar", type="secondary")

def mostrar_boton_crear_taller(key: str = None) -> bool:
    """Determina si mostrar botón crear taller"""
    if not SeguridadFOC26.can_create_taller():
        return False
    
    if key:
        return st.button("Crear Taller", key=f"crear_taller_{key}", type="primary")
    return st.button("Crear Taller", type="primary")

def mostrar_boton_inscribirse(key: str = None) -> bool:
    """Determina si mostrar botón inscribirse"""
    if not SeguridadFOC26.can_inscribirse():
        return False
    
    if key:
        return st.button("Inscribirse", key=f"inscribirse_{key}", type="primary")
    return st.button("Inscribirse", type="primary")

def mostrar_alerta_permisos_denegados(mensaje: str = "No tiene permisos para realizar esta acción."):
    """Muestra alerta de permisos denegados"""
    st.warning(mensaje)

def mostrar_panel_permisos():
    """Muestra panel de información de permisos del usuario actual"""
    if 'user' in st.session_state:
        with st.expander("Información de Permisos", expanded=False):
            user_role = SeguridadFOC26.get_user_role()
            user_cedula = SeguridadFOC26.get_user_cedula()
            
            st.write(f"**Rol:** {user_role}")
            st.write(f"**Cédula:** {user_cedula}")
            
            st.write("**Permisos Activos:**")
            
            # UNIFICACIÓN DE ROLES: Comparación robusta ADMIN/ADMINISTRADOR
            user_rol = str(st.session_state.get('user', {}).get('rol', '')).strip().upper()
            if user_rol in ['ADMIN', 'ADMINISTRADOR']:
                st.success("ROL ADMINISTRADOR - ACCESO COMPLETO")
                st.write("- Ver talleres: Sí")
                st.write("- Crear talleres: Sí")
                st.write("- Eliminar registros: Sí")
                st.write("- Inscribirse: Sí")
                st.write("- Ver datos propios: Sí")
                st.write("- Gestionar usuarios: Sí")
                st.write("- Acceso a todos los módulos: Sí")
                st.write("- Ver todos los datos: Sí")
            else:
                st.write(f"- Ver talleres: {'Sí' if SeguridadFOC26.can_view_taller_list() else 'No'}")
                st.write(f"- Crear talleres: {'Sí' if SeguridadFOC26.can_create_taller() else 'No'}")
                st.write(f"- Eliminar registros: {'Sí' if SeguridadFOC26.can_delete_any() else 'No'}")
                st.write(f"- Inscribirse: {'Sí' if SeguridadFOC26.can_inscribirse() else 'No'}")
                st.write(f"- Ver datos propios: {'Sí' if SeguridadFOC26.can_view_own_data() else 'No'}")

# Funciones de logging de seguridad
def log_acceso_denegado(funcion: str, motivo: str = ""):
    """Registra intentos de acceso denegado"""
    user_cedula = SeguridadFOC26.get_user_cedula()
    user_role = SeguridadFOC26.get_user_role()
    
    log_msg = f"ACCESO DENEGADO - Función: {funcion} - Usuario: {user_cedula} ({user_role})"
    if motivo:
        log_msg += f" - Motivo: {motivo}"
    
    print(f"SECURITY LOG: {log_msg}")

def log_acceso_concedido(funcion: str, detalles: str = ""):
    """Registra accesos exitosos"""
    user_cedula = SeguridadFOC26.get_user_cedula()
    user_role = SeguridadFOC26.get_user_role()
    
    log_msg = f"ACCESO CONCEDIDO - Función: {funcion} - Usuario: {user_cedula} ({user_role})"
    if detalles:
        log_msg += f" - Detalles: {detalles}"
    
    print(f"SECURITY LOG: {log_msg}")
