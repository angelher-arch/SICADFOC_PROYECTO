from database import execute_query
try:
    # Verificar carreras existentes
    query = 'SELECT id_carrera, nombre_carrera, activo FROM carrera'
    resultado = execute_query(query, fetch_all=True)
    print(f'Carreras encontradas: {len(resultado)}')
    for carrera in resultado:
        print(f'  ID: {carrera["id_carrera"]}, Nombre: {carrera["nombre_carrera"]}, Activo: {carrera.get("activo", "NULL")}')

    # Si hay carreras pero ninguna activa, activar todas
    if resultado and not any(c.get('activo', False) for c in resultado):
        print('\nActivando todas las carreras...')
        update_query = 'UPDATE carrera SET activo = true'
        execute_query(update_query)
        print('Todas las carreras activadas')

except Exception as e:
    print(f'Error: {e}')