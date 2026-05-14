from database import execute_query
try:
    count_query = 'SELECT COUNT(*) as count FROM carrera'
    count_result = execute_query(count_query, fetch_one=True)
    print(f'Carreras en tabla: {count_result["count"]}')

    if count_result['count'] > 0:
        query = 'SELECT id_carrera, nombre_carrera, descripcion_carrera, activo FROM carrera LIMIT 5'
        resultado = execute_query(query, fetch_all=True)
        print('Primeras carreras:')
        for c in resultado:
            print(f'  {c["id_carrera"]}: {c["nombre_carrera"]} - Activo: {c.get("activo", False)}')

except Exception as e:
    print(f'Error: {e}')