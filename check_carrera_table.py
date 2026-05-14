from database import execute_query
try:
    # Verificar estructura de la tabla carrera
    query = """
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'carrera'
    ORDER BY ordinal_position
    """
    resultado = execute_query(query, fetch_all=True)
    print('Estructura de la tabla carrera:')
    for col in resultado:
        print(f'  {col["column_name"]}: {col["data_type"]} ({col["is_nullable"]})')

    # Verificar si existe la columna activo
    activo_exists = any(col['column_name'] == 'activo' for col in resultado)
    print(f'\nColumna activo existe: {activo_exists}')

    if not activo_exists:
        print('\nAgregando columna activo...')
        alter_query = 'ALTER TABLE carrera ADD COLUMN activo BOOLEAN DEFAULT true'
        execute_query(alter_query)
        print('Columna activo agregada exitosamente')

except Exception as e:
    print(f'Error: {e}')