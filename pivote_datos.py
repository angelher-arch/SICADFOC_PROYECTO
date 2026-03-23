import os
import pandas as pd
from datetime import datetime
import hashlib

# Importar ambas bases de datos
import database  # Base local
import database_espejo  # Base nube (Render)

def obtener_id_registro(registro, tabla):
    """Obtiene un identificador único para un registro según la tabla"""
    if tabla == 'usuario':
        return str(registro.get('email', '')).lower()
    elif tabla == 'persona':
        return str(registro.get('cedula', ''))
    elif tabla == 'profesor':
        return str(registro.get('cedula', ''))
    elif tabla == 'taller':
        return str(registro.get('id_taller', ''))
    elif tabla == 'formacion_complementaria':
        return str(registro.get('id_formacion', ''))
    elif tabla == 'inscripcion':
        # Combinación única
        return f"{registro.get('cedula_estudiante', '')}-{registro.get('id_taller', '')}"
    else:
        # Para otras tablas, usar hash del registro completo
        registro_str = str(sorted(registro.items()))
        return hashlib.md5(registro_str.encode()).hexdigest()[:16]

def sincronizar_hacia_nube(tabla):
    """
    Sincroniza datos locales hacia la nube usando lógica de Upsert
    Si existe, actualiza; si no, inserta
    """
    try:
        print(f"🔄 Iniciando sincronización hacia nube - Tabla: {tabla}")
        
        # Obtener datos locales
        query_local = f"SELECT * FROM {tabla}"
        datos_locales = database.ejecutar_query(query_local, engine=database.engine)
        
        if datos_locales is None or len(datos_locales) == 0:
            print(f"⚠️ No hay datos locales en tabla {tabla}")
            return False, f"No hay datos locales en {tabla}"
        
        # Obtener datos existentes en nube
        query_nube = f"SELECT * FROM {tabla}"
        datos_nube = database_espejo.ejecutar_query_nube(query_nube)
        
        # Crear diccionario de registros existentes en nube
        registros_nube = {}
        if datos_nube is not None and len(datos_nube) > 0:
            for _, registro in datos_nube.iterrows():
                id_registro = obtener_id_registro(registro.to_dict(), tabla)
                registros_nube[id_registro] = registro.to_dict()
        
        # Procesar cada registro local
        actualizados = 0
        insertados = 0
        errores = 0
        
        with database_espejo.engine_nube.connect() as conn_nube:
            for _, registro_local in datos_locales.iterrows():
                try:
                    registro_dict = registro_local.to_dict()
                    id_registro = obtener_id_registro(registro_dict, tabla)
                    
                    if id_registro in registros_nube:
                        # Actualizar registro existente
                        columnas = list(registro_dict.keys())
                        valores = list(registro_dict.values())
                        
                        # Construir UPDATE dinámico
                        set_clause = ", ".join([f"{col} = :{col}" for col in columnas])
                        
                        # Obtener clave primaria para WHERE
                        if tabla == 'usuario':
                            where_clause = "email = :email"
                        elif tabla == 'persona':
                            where_clause = "cedula = :cedula"
                        elif tabla == 'profesor':
                            where_clause = "cedula = :cedula"
                        elif tabla == 'taller':
                            where_clause = "id_taller = :id_taller"
                        elif tabla == 'formacion_complementaria':
                            where_clause = "id_formacion = :id_formacion"
                        else:
                            # Para otras tablas, usar todas las columnas en WHERE
                            where_conditions = [f"{col} = :{col}" for col in columnas]
                            where_clause = " AND ".join(where_conditions)
                        
                        update_query = f"""
                        UPDATE {tabla} 
                        SET {set_clause} 
                        WHERE {where_clause}
                        """
                        
                        conn_nube.execute(database_espejo.text(update_query), registro_dict)
                        actualizados += 1
                        print(f"✅ Actualizado: {tabla} - {id_registro}")
                        
                    else:
                        # Insertar nuevo registro
                        columnas = list(registro_dict.keys())
                        placeholders = [f":{col}" for col in columnas]
                        
                        insert_query = f"""
                        INSERT INTO {tabla} ({', '.join(columnas)}) 
                        VALUES ({', '.join(placeholders)})
                        """
                        
                        conn_nube.execute(database_espejo.text(insert_query), registro_dict)
                        insertados += 1
                        print(f"➕ Insertado: {tabla} - {id_registro}")
                        
                except Exception as e:
                    errores += 1
                    print(f"❌ Error procesando registro: {e}")
                    continue
            
            conn_nube.commit()
        
        # Registrar sincronización
        registrar_log_sincronizacion(tabla, "hacia_nube", {
            "registros_procesados": len(datos_locales),
            "actualizados": actualizados,
            "insertados": insertados,
            "errores": errores
        })
        
        mensaje = f"Sincronización {tabla} → Nube: {insertados} insertados, {actualizados} actualizados, {errores} errores"
        print(f"🎉 {mensaje}")
        
        return True, mensaje
        
    except Exception as e:
        error_msg = f"Error en sincronización hacia nube ({tabla}): {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def traer_de_nube(tabla):
    """
    Descarga datos de Render y los guarda en la base local foc26
    """
    try:
        print(f"⬇️ Iniciando descarga desde nube - Tabla: {tabla}")
        
        # Obtener datos de la nube
        query_nube = f"SELECT * FROM {tabla}"
        datos_nube = database_espejo.ejecutar_query_nube(query_nube)
        
        if datos_nube is None or len(datos_nube) == 0:
            print(f"⚠️ No hay datos en nube para tabla {tabla}")
            return False, f"No hay datos en nube para {tabla}"
        
        # Limpiar tabla local
        with database.engine.connect() as conn_local:
            conn_local.execute(database.text(f"DELETE FROM {tabla}"))
            conn_local.commit()
            print(f"🗑️ Tabla local {tabla} limpiada")
        
        # Insertar datos locales
        insertados = 0
        errores = 0
        
        with database.engine.connect() as conn_local:
            for _, registro_nube in datos_nube.iterrows():
                try:
                    registro_dict = registro_nube.to_dict()
                    columnas = list(registro_dict.keys())
                    placeholders = [f":{col}" for col in columnas]
                    
                    insert_query = f"""
                    INSERT INTO {tabla} ({', '.join(columnas)}) 
                    VALUES ({', '.join(placeholders)})
                    """
                    
                    conn_local.execute(database.text(insert_query), registro_dict)
                    insertados += 1
                    
                except Exception as e:
                    errores += 1
                    print(f"❌ Error insertando registro: {e}")
                    continue
            
            conn_local.commit()
        
        # Registrar sincronización
        registrar_log_sincronizacion(tabla, "desde_nube", {
            "registros_procesados": len(datos_nube),
            "insertados": insertados,
            "errores": errores
        })
        
        mensaje = f"Descarga Nube → {tabla}: {insertados} insertados, {errores} errores"
        print(f"🎉 {mensaje}")
        
        return True, mensaje
        
    except Exception as e:
        error_msg = f"Error en descarga desde nube ({tabla}): {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def registrar_log_sincronizacion(tabla, direccion, detalles):
    """Registra un log de sincronización en la base local"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Crear tabla de logs si no existe
        crear_tabla_logs = """
        CREATE TABLE IF NOT EXISTS log_sincronizacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            tabla TEXT NOT NULL,
            direccion TEXT NOT NULL,
            detalles TEXT,
            exito INTEGER DEFAULT 1
        )
        """
        
        with database.engine.connect() as conn:
            conn.execute(database.text(crear_tabla_logs))
            
            # Insertar log
            insert_log = """
            INSERT INTO log_sincronizacion (timestamp, tabla, direccion, detalles)
            VALUES (:timestamp, :tabla, :direccion, :detalles)
            """
            
            conn.execute(database.text(insert_log), {
                'timestamp': timestamp,
                'tabla': tabla,
                'direccion': direccion,
                'detalles': str(detalles)
            })
            
            conn.commit()
            
        print(f"📝 Log de sincronización registrado: {tabla} - {direccion}")
        
    except Exception as e:
        print(f"❌ Error registrando log: {e}")

def obtener_ultima_sincronizacion(tabla=None):
    """Obtiene la última sincronización registrada"""
    try:
        if tabla:
            query = """
            SELECT timestamp, tabla, direccion, detalles 
            FROM log_sincronizacion 
            WHERE tabla = :tabla 
            ORDER BY timestamp DESC 
            LIMIT 1
            """
            resultado = database.ejecutar_query(query, params={'tabla': tabla}, engine=database.engine)
        else:
            query = """
            SELECT timestamp, tabla, direccion, detalles 
            FROM log_sincronizacion 
            ORDER BY timestamp DESC 
            LIMIT 10
            """
            resultado = database.ejecutar_query(query, engine=database.engine)
        
        return resultado
        
    except Exception as e:
        print(f"❌ Error obteniendo logs: {e}")
        return None

def sincronizar_todas_tablas_hacia_nube():
    """Sincroniza todas las tablas hacia la nube"""
    tablas = ['usuario', 'persona', 'profesor', 'taller', 'formacion_complementaria', 'inscripcion']
    
    resultados = []
    for tabla in tablas:
        exito, mensaje = sincronizar_hacia_nube(tabla)
        resultados.append({
            'tabla': tabla,
            'exito': exito,
            'mensaje': mensaje
        })
    
    return resultados

def traer_todas_tablas_desde_nube():
    """Trae todas las tablas desde la nube"""
    tablas = ['usuario', 'persona', 'profesor', 'taller', 'formacion_complementaria', 'inscripcion']
    
    resultados = []
    for tabla in tablas:
        exito, mensaje = traer_de_nube(tabla)
        resultados.append({
            'tabla': tabla,
            'exito': exito,
            'mensaje': mensaje
        })
    
    return resultados

if __name__ == "__main__":
    # Prueba de sincronización
    print("🧪 Probando sincronización de datos...")
    
    # Probar sincronización hacia nube
    exito, mensaje = sincronizar_hacia_nube('usuario')
    print(f"Resultado: {exito} - {mensaje}")
    
    # Probar descarga desde nube
    exito, mensaje = traer_de_nube('usuario')
    print(f"Resultado: {exito} - {mensaje}")
