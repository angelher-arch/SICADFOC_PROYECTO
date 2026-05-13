-- Script para corregir la tabla inscripciones_talleres
-- Ejecutar solo si la tabla ya existe y tiene el tipo de dato incorrecto

-- Primero verificar si la columna existe y su tipo
DO $$
DECLARE
    old_constraint_name TEXT;
BEGIN
    -- Verificar si la columna id_facilitador existe y es INTEGER
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'inscripciones_talleres'
        AND column_name = 'id_facilitador'
        AND data_type = 'integer'
    ) THEN
        RAISE NOTICE 'La columna id_facilitador es INTEGER, procediendo con la migración...';

        -- Buscar y eliminar la constraint de foreign key existente si existe
        SELECT con.conname INTO old_constraint_name
        FROM pg_constraint con
        JOIN pg_class rel ON rel.oid = con.conrelid
        JOIN pg_attribute att ON att.attrelid = con.conrelid AND att.attnum = ANY(con.conkey)
        WHERE rel.relname = 'inscripciones_talleres'
        AND att.attname = 'id_facilitador'
        AND con.contype = 'f';

        IF old_constraint_name IS NOT NULL THEN
            EXECUTE 'ALTER TABLE public.inscripciones_talleres DROP CONSTRAINT ' || old_constraint_name;
            RAISE NOTICE 'Constraint eliminada: %', old_constraint_name;
        END IF;

        -- Crear columna temporal VARCHAR
        ALTER TABLE public.inscripciones_talleres ADD COLUMN id_facilitador_temp VARCHAR(20);

        -- Migrar datos: convertir INTEGER a cédula_profesor usando JOIN con taller
        UPDATE public.inscripciones_talleres
        SET id_facilitador_temp = t.cedula_profesor
        FROM public.taller t
        WHERE public.inscripciones_talleres.id_taller = t.id_taller;

        -- Para registros donde no se encontró cedula_profesor, usar un valor por defecto o NULL
        UPDATE public.inscripciones_talleres
        SET id_facilitador_temp = 'SIN-DEFINIR'
        WHERE id_facilitador_temp IS NULL;

        -- Eliminar columna antigua
        ALTER TABLE public.inscripciones_talleres DROP COLUMN id_facilitador;

        -- Renombrar columna nueva
        ALTER TABLE public.inscripciones_talleres RENAME COLUMN id_facilitador_temp TO id_facilitador;

        -- Agregar la foreign key constraint correcta
        ALTER TABLE public.inscripciones_talleres
        ADD CONSTRAINT fk_inscripciones_facilitador
        FOREIGN KEY (id_facilitador) REFERENCES public.profesor(cedula_profesor);

        RAISE NOTICE 'Migración completada: id_facilitador cambiado de INTEGER a VARCHAR(20)';

    ELSE
        RAISE NOTICE 'La columna id_facilitador ya tiene el tipo correcto o no existe';
    END IF;
END $$;

        RAISE NOTICE 'Columna id_facilitador corregida de INTEGER a VARCHAR(20)';
    ELSE
        RAISE NOTICE 'La columna id_facilitador ya tiene el tipo correcto o no existe';
    END IF;
END $$;