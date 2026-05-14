from database import execute_query
try:
    # Verificar si la tabla carrera existe
    query = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'carrera')"
    resultado = execute_query(query, fetch_one=True)
    print(f'Tabla carrera existe: {resultado["exists"]}')

    if resultado['exists']:
        # Verificar carreras
        count_query = 'SELECT COUNT(*) as count FROM carrera'
        count_result = execute_query(count_query, fetch_one=True)
        print(f'Carreras en tabla: {count_result["count"]}')

        if count_result['count'] == 0:
            print('No hay carreras, ejecutando precarga...')
            from gestion_carreras import precargar_carreras_iniciales
            precargar_carreras_iniciales()
    else:
        print('Tabla carrera no existe')

except Exception as e:
    print(f'Error: {e}')