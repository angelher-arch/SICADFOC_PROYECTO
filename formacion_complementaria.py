# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import date
from database import get_connection, execute_query
from seguridad import tiene_permiso, SeguridadFOC26

def gestion_formacion_complementaria(rol_usuario):
    """Módulo principal de formación complementaria con pestañas"""
    
    # Validación de sesión con respaldo de auditoría
    if 'cedula' not in st.session_state:
        st.session_state.cedula = None

    # Validación de permisos con bypass para administrador
    if not tiene_permiso(rol_usuario, 'Formación Complementaria', 'crear'):
        st.error("No tiene permisos para acceder a este módulo")
        return
    
    # Validar administrador con la lógica centralizada de seguridad
    is_admin = SeguridadFOC26.is_admin() or (rol_usuario and rol_usuario.strip().lower() in ['administrador', 'admin'])
    if not is_admin:
        # Validar usuario conectado para roles no administradores
        if not st.session_state.cedula:
            st.error("El usuario de sesión no existe en la base de datos. Inicie sesión nuevamente con un usuario válido.")
            return
    st.title("Formación Complementaria")
    
    # Configuración de pestañas
    tab1, tab2 = st.tabs(["Crear Taller", "Listar Talleres"])
    
    with tab1:
        crear_taller(rol_usuario)
    
    with tab2:
        listar_talleres()

def crear_taller(rol_usuario):
    """Crear taller usando mapeo por diccionario"""
    st.markdown("### Nuevo Taller")
    
    # Usar contenedor único para evitar conflicto con otros formularios
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre del Taller*", placeholder="Introducción a Python")
            descripcion = st.text_area("Descripción*", placeholder="Taller básico de programación en Python")
            fecha_inicio = st.date_input("Fecha de Inicio*", value=date.today())
            fecha_fin = st.date_input("Fecha de Fin*", value=date.today())
            
        with col2:
            cupo = st.number_input("Cupo Máximo*", min_value=1, value=30)
            cohorte = st.selectbox("Cohorte*", options=[1, 2], format_func=lambda x: str(x), index=0, help="Seleccione la cohorte del taller")
            tomo = st.text_input("Tomo*", placeholder="001", help="Número de tomo del certificado")
            folio = st.text_input("Folio*", placeholder="12345", help="Número de folio del certificado")
            facilitador = st.text_input("Facilitador", placeholder="Nombre del facilitador")
        
        # Mostrar vista previa del código (generación en tiempo real)
        if tomo and cohorte:
            codigo_generado = f"IU-FOC-{fecha_inicio.year}-{cohorte}-{tomo}"
            st.info(f"📜 Código del Certificado: {codigo_generado}")
        else:
            st.info("📜 Código del Certificado: Complete los campos de cohorte y tomo")
        
        submit_taller = st.button("Crear Taller", type="primary")
        
        if submit_taller:
            # Generación automática justo antes de validar
            if tomo and cohorte:
                codigo_auto = f"IU-FOC-{fecha_inicio.year}-{cohorte}-{tomo}"
            else:
                codigo_auto = ""
            
            # Validar solo los campos que el usuario SÍ toca (excluir código_certificado)
            campos_obligatorios = [nombre, descripcion, fecha_inicio, fecha_fin, cupo, cohorte, tomo, folio, facilitador]
            
            # Depuración: Mostrar qué campos están vacíos
            if not all(campos_obligatorios):
                st.error("Por favor, complete todos los campos obligatorios (*)")
                st.write("Campos faltantes:")
                if not nombre:
                    st.write("❌ Nombre del Taller*")
                if not descripcion:
                    st.write("❌ Descripción*")
                if not fecha_inicio:
                    st.write("❌ Fecha de Inicio*")
                if not fecha_fin:
                    st.write("❌ Fecha de Fin*")
                if not cupo:
                    st.write("❌ Cupo Máximo*")
                if not cohorte:
                    st.write("❌ Cohorte*")
                if not tomo:
                    st.write("❌ Tomo*")
                if not folio:
                    st.write("❌ Folio*")
                if not facilitador:
                    st.write("❌ Facilitador*")
                return
            
            if all(campos_obligatorios):
                try:
                    # Validación de fechas
                    if fecha_fin < fecha_inicio:
                        st.error("La fecha de fin no puede ser anterior a la fecha de inicio")
                        return
                    
                    # Validación de cupo
                    if cupo < 1:
                        st.error("El cupo máximo debe ser al menos 1")
                        return
                    
                    # 1. Crear un registro padre en la tabla taller para satisfacer la restricción FK
                    conn = get_connection()
                    cursor = conn.cursor()
                    try:
                        conn.rollback()
                        cursor.execute(
                            "SELECT cedula_usuario FROM usuarios WHERE cedula_usuario = %s",
                            (st.session_state.cedula,)
                        )
                        usuario_existe = cursor.fetchone() is not None
                        if not usuario_existe:
                            st.error("El usuario de sesión no existe en la base de datos. Inicie sesión nuevamente con un usuario válido.")
                            return

                        profesor_cedula = None
                        if facilitador:
                            cursor.execute(
                                "SELECT cedula_profesor FROM profesor WHERE cedula_profesor = %s",
                                (facilitador,)
                            )
                            fila_profesor = cursor.fetchone()
                            if fila_profesor:
                                profesor_cedula = fila_profesor[0]
                            else:
                                st.warning(
                                    "El facilitador ingresado no corresponde a una cédula de profesor válida. "
                                    "El taller se creará sin profesor asignado."
                                )

                        query_taller = """
                            INSERT INTO public.taller (
                                nombre_taller,
                                descripcion_taller,
                                cedula_profesor,
                                capacidad_maxima,
                                duracion_horas,
                                fecha_inicio,
                                fecha_fin,
                                estado,
                                tipo_taller
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id_taller
                        """

                        valores_taller = (
                            nombre,
                            descripcion,
                            profesor_cedula,
                            cupo,
                            20,
                            fecha_inicio,
                            fecha_fin,
                            'activo',
                            'regular'
                        )

                        cursor.execute(query_taller, valores_taller)
                        id_taller_creado = cursor.fetchone()[0]

                        query_formacion = """
                            INSERT INTO public.formacion_complementaria (
                                id_taller,
                                nombre,
                                descripcion,
                                horas,
                                codigo_certificado,
                                id_usuario
                            ) VALUES (%s, %s, %s, %s, %s, %s)
                            RETURNING id_formacion
                        """

                        valores_formacion = (
                            id_taller_creado,
                            nombre,
                            descripcion,
                            20,
                            codigo_auto,
                            st.session_state.cedula
                        )

                        cursor.execute(query_formacion, valores_formacion)
                        id_formacion_creado = cursor.fetchone()[0]
                        conn.commit()

                        st.success(
                            f"Taller creado con éxito. id_taller={id_taller_creado}, id_formacion={id_formacion_creado}"
                        )
                        st.rerun()

                    except Exception as e:
                        conn.rollback()
                        st.error(f"Fallo en inserción dinámica: {e}")

                    finally:
                        if 'conn' in locals():
                            conn.close()
                            
                except Exception as e:
                    st.error(f"Error al crear taller: {str(e)}")
            else:
                st.error("Por favor, complete todos los campos obligatorios (*)")

def listar_talleres():
    """Listar talleres con opción de edición"""
    st.markdown("### Listado de Talleres")
    
    try:
        # Conexión a base de datos
        conn = get_connection()
        cursor = conn.cursor()
        
        # Consulta SQL
        query = """
            SELECT fc.id_taller,
                   fc.nombre AS nombre_taller,
                   t.fecha_inicio,
                   t.capacidad_maxima
            FROM formacion_complementaria fc
            LEFT JOIN taller t ON fc.id_taller = t.id_taller
            ORDER BY t.fecha_inicio DESC
        """

        cursor.execute(query)
        resultados = cursor.fetchall()

        if resultados:
            df = pd.DataFrame(resultados, columns=['ID', 'Nombre del Taller', 'Fecha Inicio', 'Capacidad Máxima'])

            # Mostrar tabla
            st.dataframe(df, use_container_width=True)
            
            # Selector de ID para edición
            st.markdown("### Editar Taller")
            id_seleccionado = st.number_input(
                "Ingrese el ID del taller a editar:",
                min_value=1,
                step=1,
                help="Ingrese el número de ID del taller que desea editar"
            )
            
            if st.button("Cargar Taller para Edición", type="primary"):
                if id_seleccionado:
                    # Verificar que el taller exista
                    query_check = "SELECT id_taller FROM formacion_complementaria WHERE id_taller = %s"
                    cursor.execute(query_check, (id_seleccionado,))
                    
                    if cursor.fetchone():
                        st.success(f"Taller ID {id_seleccionado} cargado para edición")
                        # Aquí se prepararía el terreno para el módulo de actualización
                        st.info("Función de edición en desarrollo...")
                    else:
                        st.error(f"No existe un taller con ID {id_seleccionado}")
                else:
                    st.error("Por favor, ingrese un ID válido")
        else:
            st.info("No hay talleres registrados")
            
    except Exception as e:
        st.error(f"Error al cargar talleres: {str(e)}")
        
    finally:
        if 'conn' in locals():
            conn.close()

# Función para exportar el motor de formación (compatibilidad)
def modulo_formacion_complementaria():
    """Función principal del módulo para compatibilidad con main.py"""
    rol_usuario = st.session_state.get('rol', '')
    gestion_formacion_complementaria(rol_usuario)

# Variable para compatibilidad con código existente
motor_formacion = None
