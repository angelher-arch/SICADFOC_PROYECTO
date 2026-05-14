from database import execute_query
try:
    # Verificar permisos cargados
    query = 'SELECT rol, modulo_nombre, puede_ver, puede_consultar, puede_editar, puede_eliminar FROM permisos_rol ORDER BY rol, modulo_nombre'
    resultado = execute_query(query, fetch_all=True)

    print(f'Permisos RBAC cargados: {len(resultado)}')
    for p in resultado[:10]:  # Mostrar primeros 10
        print(f'{p["rol"]} - {p["modulo_nombre"]}: V={p["puede_ver"]} C={p["puede_consultar"]} E={p["puede_editar"]} D={p["puede_eliminar"]}')

    # Probar función tiene_permiso
    from seguridad import tiene_permiso

    # Test Administrador
    admin_test = tiene_permiso('Administrador', 'Gestión Estudiantil', 'editar')
    print(f'\nTest Administrador editar Gestión Estudiantil: {admin_test}')

    # Test Profesor
    prof_test = tiene_permiso('Profesor', 'Gestión Estudiantil', 'editar')
    print(f'Test Profesor editar Gestión Estudiantil: {prof_test}')

    prof_ver = tiene_permiso('Profesor', 'Gestión Estudiantil', 'ver')
    print(f'Test Profesor ver Gestión Estudiantil: {prof_ver}')

    # Test Estudiante
    est_test = tiene_permiso('Estudiante', 'Gestión Estudiantil', 'editar')
    print(f'Test Estudiante editar Gestión Estudiantil: {est_test}')

except Exception as e:
    print(f'Error: {e}')