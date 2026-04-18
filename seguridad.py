#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Seguridad y Permisología para SICADFOC 2026
Control de acceso por roles y validación de identidad
"""

import functools
import streamlit as st
import random
import re
import hashlib
from typing import Callable, Any
from configuracion import get_carreras, get_semestres, get_estados_registro, get_generos
from transacciones import TransaccionFOC26

# Roles del sistema
ROLES = {
    'Administrador': 'admin',
    'Profesor': 'profesor',
    'Estudiante': 'estudiante'
}

def hash_password(password: str) -> str:
    """Genera un hash SHA-256 para la contraseña dada."""
    if password is None:
        return None
    return hashlib.sha256(str(password).strip().encode('utf-8')).hexdigest()


def is_sha256_hash(value: str) -> bool:
    """Determina si un valor es un hash SHA-256 hex válido."""
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verifica una contraseña contra el valor almacenado (hash o texto plano)."""
    if stored_password is None or provided_password is None:
        return False
    stored = str(stored_password).strip()
    provided = str(provided_password).strip()
    if is_sha256_hash(stored):
        return stored == hash_password(provided)
    return stored == provided

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


# Funciones de registro modular
def _reset_registro_step():
    """Inicializa el estado de registro en Streamlit."""
    for key in [
        'registro_paso', 'registro_cedula', 'registro_datos_basicos',
        'registro_captcha', 'registro_captcha_respuesta', 'registro_usuario_id',
        'registro_persona_id', 'registro_usuario_creado', 'registro_rol'
    ]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state['registro_paso'] = 'cedula'
    st.session_state['registro_cedula'] = ''
    st.session_state['registro_datos_basicos'] = {}
    st.session_state['registro_usuario_creado'] = False
    st.session_state['registro_rol'] = 'Estudiante'


def _buscar_usuario_por_cedula(db, cedula):
    """Busca si la cédula ya existe en la tabla usuario."""
    if not cedula:
        return None
    query = "SELECT id, rol, email, login_usuario FROM usuario WHERE cedula_usuario = %s"
    resultado = db.ejecutar_consulta(query, (cedula.strip(),))
    return resultado[0] if resultado else None


def _generar_captcha_registro():
    """Genera un captcha simple de suma para registro."""
    if 'registro_captcha' not in st.session_state or not st.session_state.get('registro_captcha'):
        a = random.randint(4, 9)
        b = random.randint(1, 9)
        st.session_state['registro_captcha'] = f"{a} + {b}"
        st.session_state['registro_captcha_respuesta'] = str(a + b)


def _crear_persona_usuario_basico(db, datos):
    """Crea la persona y el usuario básico con rol seleccionado."""
    try:
        if not datos.get('contrasena'):
            return {'exito': False, 'error': 'Contraseña no proporcionada para el usuario.'}

        query_persona = """
            INSERT INTO persona (nombre, apellido, email, cedula, telefono, direccion)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        params_persona = (
            datos['nombre'],
            datos['apellido'],
            datos['email'],
            datos['cedula'],
            datos.get('telefono', None),
            datos.get('direccion', None)
        )
        persona_result = db.ejecutar_consulta(query_persona, params_persona)
        if not persona_result:
            return {'exito': False, 'error': 'No fue posible crear el registro de persona.'}

        persona_id = persona_result[0].get('id')
        if not persona_id:
            return {'exito': False, 'error': 'No se obtuvo el ID de persona.'}

        query_usuario = """
            INSERT INTO usuario (id_persona, cedula_usuario, login_usuario, email, contrasena, rol, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        params_usuario = (
            persona_id,
            datos['cedula'],
            datos['email'],
            datos['email'],
            hash_password(datos['contrasena']),
            datos['rol'],
            True
        )
        usuario_result = db.ejecutar_consulta(query_usuario, params_usuario)
        if not usuario_result:
            return {'exito': False, 'error': 'No fue posible crear el registro de usuario.'}

        usuario_id = usuario_result[0].get('id')
        if not usuario_id:
            return {'exito': False, 'error': 'No se obtuvo el ID de usuario.'}

        return {
            'exito': True,
            'id_persona': persona_id,
            'id_usuario': usuario_id
        }
    except Exception as e:
        return {'exito': False, 'error': str(e)}


def _insertar_perfil_estudiante(db, persona_id, usuario_id, datos):
    """Inserta el perfil de estudiante usando IDs existentes."""
    try:
        trans = TransaccionFOC26(db.connection)
        id_sexo = trans.obtener_id_sexo(datos.get('genero'))
        id_carrera = trans.obtener_id_carrera(datos.get('carrera'))
        id_semestre = trans.obtener_id_semestre(datos.get('semestre'))
        id_estado = trans.obtener_id_estado_registro(datos.get('estado'))

        query_estudiante = """
            INSERT INTO estudiante (
                cedula_estudiante,
                nombres,
                apellidos,
                id_sexo,
                telefono,
                correo,
                id_carrera,
                id_semestre_formacion,
                id_estado_registro,
                id_usuario,
                id_persona
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            datos.get('codigo_estudiantil', datos['cedula']),
            datos['nombre'],
            datos['apellido'],
            id_sexo,
            datos.get('telefono'),
            datos['email'],
            id_carrera,
            id_semestre,
            id_estado,
            usuario_id,
            persona_id
        )
        result = db.ejecutar_consulta(query_estudiante, params)
        if result is None:
            return {'exito': False, 'error': 'Error al crear el perfil de estudiante.'}
        return {'exito': True}
    except Exception as e:
        return {'exito': False, 'error': str(e)}


def _insertar_perfil_profesor(db, persona_id, usuario_id, datos):
    """Inserta el perfil de profesor usando IDs existentes."""
    try:
        query_profesor = """
            INSERT INTO profesor (
                id_persona,
                id_usuario,
                cedula_profesor,
                correo_personal,
                codigo_profesor,
                especialidad,
                departamento,
                categoria,
                estado
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            persona_id,
            usuario_id,
            datos['cedula'],
            datos.get('correo_personal'),
            datos.get('codigo_profesor'),
            datos.get('especialidad'),
            datos.get('departamento'),
            datos.get('categoria'),
            datos.get('estado', 'Activo')
        )
        result = db.ejecutar_consulta(query_profesor, params)
        if result is None:
            return {'exito': False, 'error': 'Error al crear el perfil de profesor.'}
        return {'exito': True}
    except Exception as e:
        return {'exito': False, 'error': str(e)}


def registro_usuario_dinamico(db):
    """Flujo de registro dinámico con validación de cédula, captcha y perfil por rol."""
    if not db:
        st.error("Base de datos no disponible.")
        return

    if 'registro_paso' not in st.session_state:
        _reset_registro_step()

    st.markdown("## Registrarse")

    # Paso A: Cédula inicial
    if st.session_state['registro_paso'] == 'cedula':
        with st.form("form_registro_cedula"):
            cedula = st.text_input(
                "Cédula", placeholder="V12345678",
                value=st.session_state.get('registro_cedula', '')
            )
            continuar = st.form_submit_button("Continuar")

        if continuar:
            cedula = str(cedula).strip()
            if not cedula:
                st.error("Ingrese una cédula válida.")
                return

            if not db.conectar():
                st.error("No se puede conectar a la base de datos. Verifique su conexión.")
                return

            if _buscar_usuario_por_cedula(db, cedula):
                st.warning("Esta cédula ya se encuentra registrada. Por favor, inicie sesión.")
                st.session_state['registro_paso'] = 'existente'
                return

            st.session_state['registro_cedula'] = cedula
            st.session_state['registro_paso'] = 'datos_basicos'

    if st.session_state['registro_paso'] == 'existente':
        st.warning("Esta cédula ya se encuentra registrada. Por favor, inicie sesión.")
        if st.button("Registrar otra cédula"):
            _reset_registro_step()
        return

    # Paso B: Datos generales del usuario
    if st.session_state['registro_paso'] == 'datos_basicos':
        with st.form("form_registro_basicos"):
            nombre = st.text_input("Nombre", value=st.session_state['registro_datos_basicos'].get('nombre', ''))
            apellido = st.text_input("Apellido", value=st.session_state['registro_datos_basicos'].get('apellido', ''))
            email = st.text_input("Correo Electrónico", value=st.session_state['registro_datos_basicos'].get('email', ''))
            rol = st.selectbox(
                "Rol",
                ['Estudiante', 'Profesor'],
                index=0 if st.session_state.get('registro_rol', 'Estudiante') == 'Estudiante' else 1
            )
            continuar = st.form_submit_button("Continuar")

        if continuar:
            nombre = str(nombre).strip()
            apellido = str(apellido).strip()
            email = str(email).strip()
            if not nombre or not apellido or not email:
                st.error("Complete todos los campos obligatorios.")
                return
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.error("Formato de correo electrónico inválido.")
                return

            st.session_state['registro_datos_basicos'] = {
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'rol': rol,
                'cedula': st.session_state.get('registro_cedula', '')
            }
            st.session_state['registro_rol'] = rol
            _generar_captcha_registro()
            st.session_state['registro_paso'] = 'captcha'

    # Paso C: CAPTCHA, creación de contraseña y creación del usuario básico
    if st.session_state['registro_paso'] == 'captcha':
        st.markdown("### Validación CAPTCHA")
        _generar_captcha_registro()
        pregunta = st.session_state.get('registro_captcha', '0 + 0')

        with st.form("form_registro_captcha"):
            contrasena = st.text_input("Crear Contraseña*", type="password", placeholder="Mínimo 8 caracteres", help="Cree una contraseña segura")
            confirmar_contrasena = st.text_input("Confirmar Contraseña*", type="password", placeholder="Repita la contraseña", help="Debe coincidir con la contraseña creada")
            st.write(f"Resuelve el siguiente cálculo para continuar: **{pregunta}**")
            captcha_respuesta = st.text_input("Resultado", value="")

            contrasenas_validas = (
                contrasena and confirmar_contrasena and contrasena == confirmar_contrasena and len(contrasena) >= 8
            )
            registrar = st.form_submit_button("Registrar", disabled=not (contrasenas_validas and captcha_respuesta))

            if contrasena and confirmar_contrasena and contrasena != confirmar_contrasena:
                st.warning("Las contraseñas no coinciden.")
            elif contrasena and len(contrasena) < 8:
                st.warning("La contraseña debe tener al menos 8 caracteres.")

        if registrar:
            if not contrasena or not confirmar_contrasena:
                st.error("Por favor, complete los campos de contraseña.")
                return

            if contrasena != confirmar_contrasena:
                st.error("Las contraseñas no coinciden.")
                return

            if len(contrasena) < 8:
                st.error("La contraseña debe tener al menos 8 caracteres.")
                return

            if not captcha_respuesta or captcha_respuesta.strip() != st.session_state.get('registro_captcha_respuesta', ''):
                st.error("Código CAPTCHA incorrecto. Intenta nuevamente.")
                _generar_captcha_registro()
                return

            datos_basicos = st.session_state['registro_datos_basicos']
            datos_contrasena = dict(datos_basicos)
            datos_contrasena['contrasena'] = contrasena
            creador = _crear_persona_usuario_basico(db, datos_contrasena)
            if not creador['exito']:
                st.error(f"Error al crear el usuario: {creador.get('error', 'Error desconocido')}")
                return

            st.success("Usuario creado correctamente. Complete el perfil según su rol.")
            st.session_state['registro_usuario_creado'] = True
            st.session_state['registro_persona_id'] = creador['id_persona']
            st.session_state['registro_usuario_id'] = creador['id_usuario']
            if datos_basicos['rol'] == 'Estudiante':
                st.session_state['registro_paso'] = 'perfil_estudiante'
            else:
                st.session_state['registro_paso'] = 'perfil_profesor'

    # Paso D: Perfil detallado según rol
    if st.session_state['registro_paso'] == 'perfil_estudiante':
        st.markdown("### Completa tu perfil de estudiante")
        with st.form("form_perfil_estudiante"):
            carrera = st.selectbox("Carrera", get_carreras())
            semestre = st.selectbox("Semestre", get_semestres())
            genero = st.selectbox("Género", get_generos())
            estado = st.selectbox("Estado", get_estados_registro())
            telefono = st.text_input("Teléfono")
            direccion = st.text_input("Dirección")
            codigo_estudiantil = st.text_input("Código Estudiantil (opcional)")
            guardar = st.form_submit_button("Guardar perfil de estudiante")

        if guardar:
            perfil = {
                'nombre': st.session_state['registro_datos_basicos']['nombre'],
                'apellido': st.session_state['registro_datos_basicos']['apellido'],
                'email': st.session_state['registro_datos_basicos']['email'],
                'cedula': st.session_state['registro_cedula'],
                'genero': genero,
                'carrera': carrera,
                'semestre': semestre,
                'estado': estado,
                'telefono': telefono,
                'codigo_estudiantil': codigo_estudiantil
            }
            resultado = _insertar_perfil_estudiante(
                db,
                st.session_state['registro_persona_id'],
                st.session_state['registro_usuario_id'],
                perfil
            )
            if resultado['exito']:
                st.success("Registro completado con éxito. Ya puede iniciar sesión con su cédula y la contraseña creada.")
                _reset_registro_step()
            else:
                st.error(f"Error guardando el perfil de estudiante: {resultado.get('error', '')}")

    if st.session_state['registro_paso'] == 'perfil_profesor':
        st.markdown("### Completa tu perfil de profesor")
        with st.form("form_perfil_profesor"):
            especialidad = st.text_input("Especialidad")
            departamento = st.text_input("Departamento")
            correo_personal = st.text_input("Correo Personal")
            codigo_profesor = st.text_input("Código Profesor")
            estado = st.selectbox("Estado", ['Activo', 'Inactivo'])
            guardar = st.form_submit_button("Guardar perfil de profesor")

        if guardar:
            perfil = {
                'cedula': st.session_state['registro_cedula'],
                'correo_personal': correo_personal,
                'codigo_profesor': codigo_profesor,
                'especialidad': especialidad,
                'departamento': departamento,
                'categoria': None,
                'estado': estado,
                'nombre': st.session_state['registro_datos_basicos']['nombre'],
                'apellido': st.session_state['registro_datos_basicos']['apellido'],
                'email': st.session_state['registro_datos_basicos']['email']
            }
            resultado = _insertar_perfil_profesor(
                db,
                st.session_state['registro_persona_id'],
                st.session_state['registro_usuario_id'],
                perfil
            )
            if resultado['exito']:
                st.success("Registro completado con éxito. Ya puede iniciar sesión con su cédula y la contraseña creada.")
                _reset_registro_step()
            else:
                st.error(f"Error guardando el perfil de profesor: {resultado.get('error', '')}")


def _buscar_usuario_por_cedula_y_email(db, cedula, email):
    """Busca un usuario por cédula y correo registrado."""
    if not cedula or not email:
        return None
    query = "SELECT id FROM usuario WHERE cedula_usuario = %s AND email = %s"
    resultado = db.ejecutar_consulta(query, (cedula.strip(), email.strip()))
    return resultado[0] if resultado else None


def _actualizar_contrasena_usuario(db, usuario_id, nueva_contrasena):
    """Actualiza la contraseña de un usuario en la base de datos."""
    if not usuario_id or not nueva_contrasena:
        return False
    query = "UPDATE usuario SET contrasena = %s WHERE id = %s"
    resultado = db.ejecutar_consulta(query, (hash_password(nueva_contrasena), usuario_id))
    return resultado is not None


def modulo_recuperacion_contrasena(db):
    """Interfaz de recuperación de contraseña por cédula y correo."""
    if not db:
        st.error("Base de datos no disponible.")
        return

    if 'recuperacion_paso' not in st.session_state:
        st.session_state['recuperacion_paso'] = 'inicio'

    st.markdown("## Recuperación de Contraseña")

    if st.session_state['recuperacion_paso'] == 'inicio':
        with st.form("form_recuperacion_datos"):
            cedula = st.text_input("Cédula de Identidad", placeholder="V12345678")
            email = st.text_input("Correo Electrónico Registrado", placeholder="usuario@iujo.edu")
            validar = st.form_submit_button("Validar datos")

        if validar:
            cedula = str(cedula).strip()
            email = str(email).strip()
            if not cedula or not email:
                st.error("Por favor, ingrese la cédula y el correo electrónico registrados.")
                return

            if not db.conectar():
                st.error("No se puede conectar a la base de datos. Verifique su conexión.")
                return

            usuario = _buscar_usuario_por_cedula_y_email(db, cedula, email)
            if not usuario:
                st.error("La cédula y el correo no coinciden con ningún usuario.")
                return

            st.success("Validación exitosa. Ingrese su nueva contraseña.")
            st.session_state['recuperacion_usuario_id'] = usuario['id']
            st.session_state['recuperacion_paso'] = 'nueva_contrasena'
            st.experimental_rerun()

    if st.session_state['recuperacion_paso'] == 'nueva_contrasena':
        with st.form("form_recuperacion_clave"):
            nueva_contrasena = st.text_input("Nueva Contraseña", type="password", placeholder="Mínimo 8 caracteres")
            confirmar_nueva_contrasena = st.text_input("Confirmar Nueva Contraseña", type="password", placeholder="Repita la nueva contraseña")
            cambiar = st.form_submit_button(
                "Cambiar contraseña",
                disabled=not (
                    nueva_contrasena and confirmar_nueva_contrasena and nueva_contrasena == confirmar_nueva_contrasena and len(nueva_contrasena) >= 8
                )
            )

            if nueva_contrasena and confirmar_nueva_contrasena and nueva_contrasena != confirmar_nueva_contrasena:
                st.warning("Las contraseñas no coinciden.")
            elif nueva_contrasena and len(nueva_contrasena) < 8:
                st.warning("La contraseña debe tener al menos 8 caracteres.")

        if cambiar:
            if not nueva_contrasena or not confirmar_nueva_contrasena:
                st.error("Complete ambos campos de contraseña.")
                return
            if nueva_contrasena != confirmar_nueva_contrasena:
                st.error("Las contraseñas no coinciden.")
                return
            if len(nueva_contrasena) < 8:
                st.error("La contraseña debe tener al menos 8 caracteres.")
                return

            usuario_id = st.session_state.get('recuperacion_usuario_id')
            if not usuario_id:
                st.error("No se encontró el usuario para actualizar la contraseña.")
                return

            exito = _actualizar_contrasena_usuario(db, usuario_id, nueva_contrasena)
            if exito:
                st.success("Contraseña actualizada con éxito. Ya puede iniciar sesión con su cédula y su nueva contraseña.")
                for key in ['recuperacion_paso', 'recuperacion_usuario_id', 'mostrar_recuperacion']:
                    if key in st.session_state:
                        del st.session_state[key]
            else:
                st.error("No se pudo actualizar la contraseña. Intente nuevamente.")

        if st.button("Cancelar recuperación"):
            for key in ['recuperacion_paso', 'recuperacion_usuario_id', 'mostrar_recuperacion']:
                if key in st.session_state:
                    del st.session_state[key]
            st.experimental_rerun()
