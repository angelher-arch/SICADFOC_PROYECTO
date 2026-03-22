import os
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# Configuración específica para Render (Nube)
RENDER_DATABASE_URL = "postgresql://foc26_user:Q3RHTJux7xKlIigalJo2ptEFaTXoo88E@dpg-d6sr7ovdiees73cj1580-a/foc26"

def crear_engine_nube():
    """Crea el engine de base de datos para la nube (Render)"""
    print("🚀 Creando conexión a base de datos en la nube (Render)")
    return create_engine(RENDER_DATABASE_URL)

# Engine global para la nube
engine_nube = crear_engine_nube()

def get_connection_espejo():
    """Obtiene conexión a la base de datos espejo (nube)"""
    try:
        return engine_nube
    except Exception as e:
        print(f"Error conexión nube: {e}")
        return None

def get_info_espejo():
    """Retorna información de la conexión a la nube"""
    return {
        "host": "dpg-d6sr7ovdiees73cj1580-a.oregon-postgres.render.com",
        "user": "foc26_user",
        "database": "foc26",
        "port": "5432",
        "environment": "cloud",
        "provider": "render"
    }

def ejecutar_query_nube(query, params=None):
    """Ejecuta queries en la base de datos de la nube"""
    try:
        with engine_nube.connect() as conn:
            if params:
                result = conn.execute(text(query), params)
            else:
                result = conn.execute(text(query))
            
            if query.strip().upper().startswith('SELECT'):
                return pd.DataFrame(result.fetchall(), columns=result.keys())
            else:
                conn.commit()
                return {"affected": result.rowcount}
    except Exception as e:
        print(f"Error ejecutando query en nube: {e}")
        return None

def obtener_datos_nube(tabla=None):
    """Obtiene datos específicos de la nube"""
    try:
        if tabla:
            query = f"SELECT * FROM {tabla}"
            return ejecutar_query_nube(query)
        else:
            # Obtener información general
            info = get_info_espejo()
            
            # Verificar tablas
            query = "SELECT name FROM sqlite_master WHERE type='table'"
            # Nota: Esto es para SQLite, para PostgreSQL sería diferente
            query_pg = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            """
            
            with engine_nube.connect() as conn:
                result = conn.execute(text(query_pg))
                tablas = [row[0] for row in result.fetchall()]
            
            return {
                "conexion": info,
                "tablas": tablas,
                "total_tablas": len(tablas)
            }
    except Exception as e:
        print(f"Error obteniendo datos de nube: {e}")
        return None

def sincronizar_con_espejo(datos_locales, tabla_destino):
    """Sincroniza datos locales con la base de datos espejo (nube)"""
    try:
        print(f"🔄 Sincronizando datos a tabla {tabla_destino} en la nube...")
        
        with engine_nube.connect() as conn:
            # Limpiar tabla destino (opcional, dependiendo de la estrategia)
            conn.execute(text(f"DELETE FROM {tabla_destino}"))
            
            # Insertar datos
            for _, row in datos_locales.iterrows():
                # Convertir row a diccionario
                datos_dict = row.to_dict()
                
                # Construir query INSERT dinámicamente
                columnas = list(datos_dict.keys())
                valores = list(datos_dict.values())
                
                placeholders = [f":{col}" for col in columnas]
                query = f"""
                INSERT INTO {tabla_destino} ({', '.join(columnas)}) 
                VALUES ({', '.join(placeholders)})
                """
                
                conn.execute(text(query), datos_dict)
            
            conn.commit()
            
        print(f"✅ Sincronización completada: {len(datos_locales)} registros en {tabla_destino}")
        return True, f"Sincronizados {len(datos_locales)} registros en {tabla_destino}"
        
    except Exception as e:
        print(f"Error en sincronización con espejo: {e}")
        return False, f"Error: {str(e)}"

def verificar_conexion_nube():
    """Verifica si la conexión a la nube está activa"""
    try:
        with engine_nube.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_result = result.fetchone()
            
        if test_result and test_result[0] == 1:
            print("✅ Conexión a nube (Render) establecida correctamente")
            return True
        else:
            print("❌ Error en conexión a nube")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando conexión a nube: {e}")
        return False

def obtener_metricas_nube():
    """Obtiene métricas desde la base de datos en la nube"""
    try:
        with engine_nube.connect() as conn:
            # Contar usuarios
            result_usuarios = conn.execute(text("SELECT COUNT(*) FROM usuario WHERE activo = TRUE"))
            total_usuarios = result_usuarios.fetchone()[0]
            
            # Contar estudiantes (rol = 'estudiante')
            result_estudiantes = conn.execute(text("SELECT COUNT(*) FROM usuario WHERE rol = 'estudiante' AND activo = TRUE"))
            total_estudiantes = result_estudiantes.fetchone()[0]
            
            # Contar profesores (rol = 'profesor')
            result_profesores = conn.execute(text("SELECT COUNT(*) FROM usuario WHERE rol = 'profesor' AND activo = TRUE"))
            total_profesores = result_profesores.fetchone()[0]
            
            # Contar talleres/formaciones
            try:
                result_talleres = conn.execute(text("SELECT COUNT(*) FROM taller WHERE activo = TRUE"))
                total_talleres = result_talleres.fetchone()[0]
            except:
                total_talleres = 0
            
            return {
                "usuarios": total_usuarios,
                "estudiantes": total_estudiantes,
                "profesores": total_profesores,
                "talleres": total_talleres
            }
            
    except Exception as e:
        print(f"Error obteniendo métricas de nube: {e}")
        return {
            "usuarios": 0,
            "estudiantes": 0,
            "profesores": 0,
            "talleres": 0
        }

def sincronizar_espejo_a_render():
    """Función principal de sincronización desde espejo local a Render"""
    try:
        print("🔄 Iniciando sincronización desde espejo local a Render...")
        
        # Importar base de datos local
        from database import ejecutar_query as ejecutar_query_local
        
        # Obtener datos locales del espejo
        tablas_a_sincronizar = [
            'rol', 'usuario', 'persona', 'profesor', 
            'taller', 'formacion_complementaria', 'inscripcion'
        ]
        
        total_registros = 0
        for tabla in tablas_a_sincronizar:
            try:
                # Obtener datos locales
                datos_locales = ejecutar_query_local(f"SELECT * FROM {tabla}", engine=engine_nube)
                
                if datos_locales is not None and len(datos_locales) > 0:
                    # Sincronizar con la nube
                    exito, mensaje = sincronizar_con_espejo(datos_locales, tabla)
                    
                    if exito:
                        total_registros += len(datos_locales)
                        print(f"✅ {tabla}: {len(datos_locales)} registros sincronizados")
                    else:
                        print(f"❌ Error sincronizando {tabla}: {mensaje}")
                else:
                    print(f"⚠️ Tabla {tabla} vacía o no encontrada")
                    
            except Exception as e:
                print(f"❌ Error procesando tabla {tabla}: {e}")
        
        mensaje_final = f"Sincronización completada: {total_registros} registros totales"
        print(f"🎉 {mensaje_final}")
        return True, mensaje_final
        
    except Exception as e:
        error_msg = f"Error general en sincronización: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

# Función de inicialización para pruebas
def test_connection_to_render():
    """Prueba la conexión a Render"""
    print("🧪 Probando conexión a Render...")
    return verificar_conexion_nube()

if __name__ == "__main__":
    # Prueba de conexión
    if test_connection_to_render():
        print("✅ Conexión a Render exitosa")
        
        # Obtener métricas
        metricas = obtener_metricas_nube()
        print(f"Métricas: {metricas}")
    else:
        print("❌ Falló conexión a Render")
