from database import execute_query
try:
    # Crear tabla permisos_rol específicamente
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS public.permisos_rol (
        id SERIAL PRIMARY KEY,
        rol VARCHAR(50) NOT NULL,
        modulo_nombre VARCHAR(100) NOT NULL,
        puede_ver BOOLEAN NOT NULL DEFAULT FALSE,
        puede_consultar BOOLEAN NOT NULL DEFAULT FALSE,
        puede_editar BOOLEAN NOT NULL DEFAULT FALSE,
        puede_eliminar BOOLEAN NOT NULL DEFAULT FALSE,
        activo BOOLEAN NOT NULL DEFAULT TRUE,
        fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (rol, modulo_nombre)
    );
    '''

    execute_query(create_table_sql)
    print('✅ Tabla permisos_rol creada exitosamente')

    # Agregar comentario
    comment_sql = "COMMENT ON TABLE public.permisos_rol IS 'Control de Acceso Basado en Roles (RBAC) - Permisos granulares por módulo y rol';"
    execute_query(comment_sql)
    print('✅ Comentario agregado a tabla permisos_rol')

except Exception as e:
    print(f'❌ Error: {e}')