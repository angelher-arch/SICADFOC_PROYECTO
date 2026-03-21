import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Monitor de Gabinetes - SICADFOC", page_icon="⚡")

st.title("⚡ Monitor de Infraestructura de Datos")
st.info("Esta herramienta valida la conexión con los gabinetes Local y Render.")

# --- PRUEBA 1: GABINETE LOCAL ---
st.header("1. Gabinete Local (PC)")
try:
    # Intentamos importar tu conexión original
    from database import obtener_conexion
    conn_local = obtener_conexion()
    if conn_local:
        st.success("✅ Conexión LOCAL establecida con éxito.")
        # Prueba de lectura rápida
        df_local = pd.read_sql("SELECT current_database(), current_user", conn_local)
        st.write("Datos del servidor local:", df_local)
        conn_local.close()
except Exception as e:
    st.error(f"❌ Fallo en Gabinete Local: {e}")

st.divider()

# --- PRUEBA 2: GABINETE RENDER (NUBE) ---
st.header("2. Gabinete Render (Nube)")
try:
    # Usamos la URL simplificada de los secretos
    if "postgres" in st.secrets:
        url_render = st.secrets["postgres"]["url"]
        conn_render = psycopg2.connect(url_render)
        st.success("✅ Conexión a RENDER establecida con éxito.")
        
        # Consultar la versión de la base de datos en la nube
        cur = conn_render.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        st.code(f"Motor en la nube: {version[0]}")
        
        # Verificar si existen tablas
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tablas = cur.fetchall()
        if tablas:
            st.warning(f"Tablas encontradas en Render: {[t[0] for t in tablas]}")
        else:
            st.info("El gabinete en la nube está conectado pero vacío (sin tablas).")
            
        cur.close()
        conn_render.close()
    else:
        st.warning("⚠️ No se encontró la configuración 'url' en .streamlit/secrets.toml")
except Exception as e:
    st.error(f"❌ Fallo en Gabinete Render: {e}")