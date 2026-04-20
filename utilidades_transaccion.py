#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UTILIDADES DE TRANSACCIÓN - SICADFOC 2026
Patrón robusto para operaciones de base de datos con transacciones seguras
"""

def ejecutar_transaccion(db, query, params=None, operacion="INSERT"):
    """
    Ejecuta una operación de base de datos con patrón try-commit-finally
    
    Args:
        db: Conexión a base de datos
        query (str): Consulta SQL a ejecutar
        params (tuple): Parámetros de la consulta
        operacion (str): Tipo de operación para logging
        
    Returns:
        dict: Resultado de la operación
    """
    cursor = None
    try:
        # Obtener cursor
        cursor = db.db.cursor()
        
        # Ejecutar consulta
        cursor.execute(query, params or ())
        
        # Commit explícito - CRÍTICO
        db.db.commit()
        
        # Para INSERT con RETURNING, obtener el resultado
        if operacion.upper() == "INSERT" and "RETURNING" in query.upper():
            resultado = cursor.fetchone()
            return {
                'exito': True,
                'resultado': resultado,
                'mensaje': f'{operacion} ejecutado exitosamente'
            }
        
        # Para UPDATE/DELETE, obtener filas afectadas
        filas_afectadas = cursor.rowcount
        
        return {
            'exito': True,
            'filas_afectadas': filas_afectadas,
            'mensaje': f'{operacion} ejecutado exitosamente'
        }
        
    except Exception as e:
        # Rollback en caso de error - CRÍTICO
        if cursor and hasattr(db, 'db') and db.db:
            try:
                db.db.rollback()
            except:
                pass
        
        return {
            'exito': False,
            'error': f'Error en {operacion}: {str(e)}'
        }
    finally:
        # Cierre seguro del cursor - CRÍTICO
        if cursor:
            try:
                cursor.close()
            except:
                pass

def ejecutar_consulta_segura(db, query, params=None):
    """
    Ejecuta consulta SELECT con manejo seguro de cursor
    
    Args:
        db: Conexión a base de datos
        query (str): Consulta SQL
        params (tuple): Parámetros
        
    Returns:
        list: Resultados de la consulta
    """
    cursor = None
    try:
        cursor = db.db.cursor()
        cursor.execute(query, params or ())
        resultado = cursor.fetchall()
        return resultado
    except Exception as e:
        print(f"Error en consulta segura: {e}")
        return None
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
