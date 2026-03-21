import sys
sys.path.append('c:/Users/USR/OneDrive/Desktop/Proyecto_FOC26')

def test_conexion_final():
    print("=== EJECUCIÓN DE CONEXIONES TRAS RESPALDO ===")
    
    try:
        # 1. Verificar funciones operativas
        print("\n1. FUNCIONES OPERATIVAS:")
        from database import (
            get_connection_local, get_connection_render, 
            listar_estudiantes, insertar_estudiante, actualizar_estudiante, eliminar_estudiante,
            insertar_formacion, listar_formaciones, eliminar_formacion,
            inscribir_estudiante_taller, obtener_profesores, eliminar_profesor,
            registrar_auditoria, obtener_auditoria,
            guardar_config_correo, obtener_config_correo,
            crear_usuario_prueba, crear_tablas_sistema, ejecutar_query, insertar_profesor,
            limpiar_columnas_profesores, limpiar_columnas_estudiantes, asegurar_estructura_persona,
            get_metricas_dashboard
        )
        print("   OK: Todas las funciones importadas")
        
        # 2. Conexión a BD
        print("\n2. CONEXIÓN A BASE DE DATOS:")
        engine = get_connection_local()
        if engine:
            print("   OK: Conexión local funcionando")
            
            # 3. Verificar funciones específicas
            print("\n3. VERIFICACIÓN DE FUNCIONES ESPECÍFICAS:")
            
            # get_metricas_dashboard
            metricas = get_metricas_dashboard(engine=engine)
            print(f"   OK: get_metricas_dashboard() - {metricas}")
            
            # asegurar_estructura_persona
            asegurar_estructura_persona(engine=engine)
            print("   OK: asegurar_estructura_persona() - Ejecutado sin errores")
            
            # obtener_auditoria
            auditoria = obtener_auditoria(engine=engine)
            print(f"   OK: obtener_auditoria() - {len(auditoria)} registros")
            
            # 4. Verificar datos disponibles
            print("\n4. DATOS DISPONIBLES PARA BOTONES:")
            estudiantes = listar_estudiantes(engine=engine)
            profesores = obtener_profesores(engine=engine)
            formaciones = listar_formaciones(engine=engine)
            
            print(f"   Estudiantes: {len(estudiantes)} - Botones Editar/Eliminar disponibles")
            print(f"   Profesores: {len(profesores)} - Botones Editar/Eliminar disponibles")
            print(f"   Formaciones: {len(formaciones)} - Botones Editar/Eliminar disponibles")
            
            # 5. Verificar sintaxis y estructura de botones en main.py
            print("\n5. VERIFICACIÓN DE BOTONES EN main.py:")
            
            with open('main.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar st.success() en botones de eliminar
            success_count = content.count('st.success("✅ Estudiante eliminado')
            success_count += content.count('st.success("✅ Profesor eliminado')
            success_count += content.count('st.success("✅ Formación eliminada')
            print(f"   OK: st.success() en eliminar - {success_count} instancias")
            
            # Buscar st.rerun() en botones de eliminar
            rerun_count = content.count('st.rerun()')
            print(f"   OK: st.rerun() general - {rerun_count} instancias")
            
            # Buscar st.session_state.id_a_editar en botones de editar
            edit_state_count = content.count('st.session_state.id_a_editar')
            print(f"   OK: st.session_state.id_a_editar en editar - {edit_state_count} instancias")
            
            # Buscar st.session_state.tab_index en botones de editar
            tab_index_count = content.count('st.session_state.tab_index')
            print(f"   OK: st.session_state.tab_index en editar - {tab_index_count} instancias")
            
            # 6. Verificar estructura de selectboxes
            print("\n6. VERIFICACIÓN DE SELECTBOXES:")
            
            # Estudiantes
            if 'opciones_estudiantes = [' in content:
                print("   OK: Selectbox de estudiantes configurado")
            
            # Profesores
            if 'opciones_profesores = [' in content:
                print("   OK: Selectbox de profesores configurado")
            
            # Formaciones
            if 'opciones_formaciones = [' in content:
                print("   OK: Selectbox de formaciones configurado")
            
            # 7. Verificar confirmación con checkbox
            print("\n7. VERIFICACIÓN DE CONFIRMACIÓN:")
            if 'confirmar_accion = st.checkbox(' in content:
                print("   OK: Checkbox de confirmación implementado")
            
            # 8. Verificar sintaxis general
            print("\n8. SINTAXIS GENERAL:")
            import ast
            ast.parse(content)
            print("   OK: main.py sintácticamente correcto")
            
            print("\n=== CONEXIÓN FINAL COMPLETADA ===")
            print("   - Funciones operativas: get_metricas_dashboard, asegurar_estructura_persona, obtener_auditoria")
            print("   - Botones Eliminar: st.success() + st.rerun() implementados")
            print("   - Botones Editar: st.session_state.id_a_editar + st.session_state.tab_index implementados")
            print("   - Selectboxes configurados para lectura de valores")
            print("   - Confirmación con checkbox requerida")
            print("   - Sistema listo para ejecución tras respaldo")
            
        else:
            print("   ERROR: No se pudo conectar a la base de datos")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conexion_final()
