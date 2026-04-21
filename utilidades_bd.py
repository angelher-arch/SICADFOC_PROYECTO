#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UTILIDADES BASE DE DATOS - SICADFOC 2026
Funciones para normalización y manejo de base de datos
"""

import re

def normalizar_cedula(cedula):
    """
    Normaliza la cédula al formato V-XXXXXXXX
    
    Args:
        cedula (str): Cédula en cualquier formato
        
    Returns:
        str: Cédula normalizada en formato V-XXXXXXXX
    """
    if not cedula:
        return None
    
    # Limpiar y convertir a string
    cedula = str(cedula).strip()
    
    # Si ya está en formato correcto, devolverla
    if re.match(r'^V-\d{7,8}$', cedula):
        return cedula
    
    # Extraer solo los números
    numeros = re.findall(r'\d+', cedula)
    if not numeros:
        return None
    
    # Tomar todos los números encontrados y unirlos
    solo_numeros = ''.join(numeros)
    
    # Validar que tenga entre 7 y 8 dígitos
    if len(solo_numeros) < 7 or len(solo_numeros) > 8:
        return None
    
    # Formatear como V-XXXXXXXX
    return f"V-{solo_numeros}"

def verificar_cedula_existente(db, cedula):
    """
    Verifica si una cédula ya existe en la base de datos
    
    Args:
        db: Conexión a base de datos
        cedula (str): Cédula a verificar
        
    Returns:
        bool: True si existe, False si no
    """
    try:
        query = "SELECT COUNT(*) as total FROM usuario WHERE cedula_usuario = %s"
        resultado = db.ejecutar_consulta(query, (cedula,))
        
        if resultado and resultado[0]['total'] > 0:
            return True
        return False
        
    except Exception:
        return False

def insertar_usuario_normalizado(db, datos_usuario):
    """
    Inserta un usuario con cédula normalizada, verificación y transacción explícita
    
    Args:
        db: Conexión a base de datos
        datos_usuario (dict): Datos del usuario
        
    Returns:
        dict: Resultado de la operación
    """
    cursor = None
    try:
        # Normalizar cédula
        cedula_normalizada = normalizar_cedula(datos_usuario.get('cedula'))
        if not cedula_normalizada:
            return {
                'exito': False,
                'error': 'Formato de cédula inválido. Debe contener entre 7 y 8 dígitos.'
            }
        
        # Verificar si ya existe
        if verificar_cedula_existente(db, cedula_normalizada):
            return {
                'exito': False,
                'error': f'La cédula {cedula_normalizada} ya está registrada en el sistema.'
            }
        
        # Generar hash de contraseña
        import hashlib
        contrasena_hash = hashlib.sha256(datos_usuario['contrasena'].encode()).hexdigest()
        
        # Obtener cursor y ejecutar con transacción explícita
        cursor = db.db.cursor()
        
        try:
            # Iniciar transacción explícita
            cursor.execute("BEGIN")
            
            # Insertar con las columnas reales de la tabla
            query = """
            INSERT INTO usuario (cedula_usuario, cedula, contrasena, rol, login_usuario, email, activo)
            VALUES (%s, %s, %s, %s, %s, %s, true)
            """
            
            cursor.execute(query, (
                cedula_normalizada,           # cedula_usuario
                cedula_normalizada,           # cedula
                contrasena_hash,              # contrasena
                datos_usuario['rol'],         # rol
                datos_usuario['login'],        # login_usuario
                datos_usuario['email']         # email
            ))
            
            # Commit explícito
            db.db.commit()
            
            # Validación post-escritura: verificar que el registro persistió
            query_verificar = "SELECT COUNT(*) as total FROM usuario WHERE cedula_usuario = %s"
            cursor.execute(query_verificar, (cedula_normalizada,))
            resultado_verificar = cursor.fetchone()
            
            if resultado_verificar['total'] == 0:
                # Si no existe después del commit, hubo un problema
                db.db.rollback()
                return {
                    'exito': False,
                    'error': f'Error crítico: El usuario {cedula_normalizada} no persistió en la base de datos después del commit.'
                }
            
            return {
                'exito': True,
                'cedula': cedula_normalizada,
                'mensaje': f'Usuario {cedula_normalizada} registrado exitosamente.'
            }
            
        except Exception as e:
            # Rollback en caso de error
            if cursor:
                try:
                    db.db.rollback()
                except:
                    pass
            return {
                'exito': False,
                'error': f'Error en el registro: {str(e)}'
            }
        finally:
            # Cierre seguro del cursor
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
        
    except Exception as e:
        return {
            'exito': False,
            'error': f'Error en la transacción: {str(e)}'
        }
