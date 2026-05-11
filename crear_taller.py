#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crear_taller.py - Módulo simplificado para creación de talleres
SICADFOC 2026 - Instituto Universitario Jesus Obrero
"""

import streamlit as st
from datetime import datetime

def modulo_crear_taller(conn):
    st.markdown("### Registrar Nuevo Taller")
    
    # El formulario debe replicar visualmente la imagen image_81b236.png
    with st.form("form_registro_taller", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre del Taller*")
            desc = st.text_area("Descripción*")
            f_ini = st.date_input("Fecha de Inicio*")
            f_fin = st.date_input("Fecha de Fin*")
            
        with col2:
            cupo = st.number_input("Cupo Máximo*", min_value=1, value=30)
            cohorte = st.selectbox("Cohorte*", [1, 2, 3, 4, 5, 6])
            estado = st.selectbox("Estado", ["Activo", "Inactivo"])
            tomo = st.text_input("Tomo*", value="4")
            folio = st.text_input("Folio*", value="12")
            facilitador = st.text_input("Facilitador*", placeholder="Nombre del docente")

        # Mostrar código de certificado dinámicamente mientras se llena el formulario
        if all([f_ini, cohorte, tomo]):
            cod_cert_preview = f"IU-FOC-{f_ini.year}-{cohorte}-{tomo}"
            st.info(f"📜 **Código de Certificado:** `{cod_cert_preview}`")

        if st.form_submit_button("Crear Taller"):
            # VALIDACIÓN DE CAMPOS OBLIGATORIOS
            if not nombre or not facilitador:
                st.error("Por favor, rellene los campos obligatorios (*)")
                return

            try:
                # 1. Generar Código de Certificado y Capturar Auditoría
                codigo_validado = f"IU-FOC-{f_ini.year}-{cohorte}-{tomo}"
                usuario_creador = st.session_state.get('cedula')
                if not usuario_creador:
                    st.error("Debe iniciar sesión para crear un taller.")
                    return
                id_estado = 1  # Valor por defecto para estado activo

                query_profesor = "SELECT cedula_profesor FROM profesor WHERE cedula_profesor = %s"
                cursor = conn.cursor()
                cursor.execute(query_profesor, (facilitador,))
                profesor_valido = cursor.fetchone()
                cedula_profesor = profesor_valido[0] if profesor_valido else None

                if facilitador and not cedula_profesor:
                    st.warning(
                        "El facilitador ingresado no corresponde a una cédula de profesor registrada. "
                        "El taller se creará sin profesor asignado."
                    )

                query_taller = """
                    INSERT INTO taller (
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
                    RETURNING id_taller;
                """

                valores_taller = (
                    nombre,
                    desc,
                    cedula_profesor,
                    cupo,
                    20,
                    f_ini,
                    f_fin,
                    estado.lower(),
                    'regular'
                )

                cursor.execute(query_taller, valores_taller)
                id_taller = cursor.fetchone()[0]

                query_formacion = """
                    INSERT INTO formacion_complementaria (
                        id_taller,
                        nombre,
                        descripcion,
                        horas,
                        codigo_certificado,
                        id_usuario
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id_formacion;
                """

                valores_formacion = (
                    id_taller,
                    nombre,
                    desc,
                    20,
                    codigo_validado,
                    usuario_creador
                )

                cursor.execute(query_formacion, valores_formacion)
                id_formacion = cursor.fetchone()[0]
                conn.commit()

                st.success(f"Taller creado con éxito. id_taller={id_taller}, id_formacion={id_formacion}")
                
            except Exception as e:
                # Mostrar solo el error técnico simplificado
                st.error(f"Error en la escritura de datos: {str(e)}")
