-- Script para actualizar la base de datos local y agregar la columna cohorte
-- SICADFOC 2026 - Instituto Universitario Jesus Obrero
-- Ejecutar este script en PostgreSQL para actualizar la estructura de la base de datos

-- 1. Verificar y actualizar la tabla formacion_complementaria
-- Agregar columna cohorte si no existe
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'formacion_complementaria' AND column_name = 'cohorte'
    ) THEN
        ALTER TABLE formacion_complementaria ADD COLUMN cohorte INTEGER NOT NULL DEFAULT 1;
        RAISE NOTICE 'Columna cohorte agregada a formacion_complementaria';
    ELSE
        RAISE NOTICE 'Columna cohorte ya existe en formacion_complementaria';
    END IF;
END $$;

-- 2. Verificar y actualizar la longitud del campo codigo_certificado
-- Aumentar a 100 caracteres para soportar el nuevo formato IU-FOC-[Año]-[Cohorte]-[Tomo]
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'formacion_complementaria' 
        AND column_name = 'codigo_certificado'
        AND character_maximum_length < 50
    ) THEN
        ALTER TABLE formacion_complementaria ALTER COLUMN codigo_certificado TYPE VARCHAR(100);
        RAISE NOTICE 'Columna codigo_certificado actualizada a VARCHAR(100)';
    ELSE
        RAISE NOTICE 'Columna codigo_certificado ya tiene longitud adecuada o no existe';
    END IF;
END $$;

-- 3. Verificar la estructura actual de la tabla
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'formacion_complementaria' 
ORDER BY ordinal_position;

-- 4. Mostrar registros existentes para verificar
SELECT 
    id_formacion,
    nombre,
    codigo_certificado,
    COALESCE(cohorte, 1) as cohorte_actual
FROM formacion_complementaria 
ORDER BY id_formacion;

-- 5. Actualizar códigos existentes al nuevo formato (opcional)
-- Solo ejecutar si quieres actualizar registros existentes
/*
UPDATE formacion_complementaria 
SET codigo_certificado = 
    CASE 
        WHEN codigo_certificado ~ '^IU-FOC-\d{4}-\d+-\d+$' THEN codigo_certificado
        WHEN codigo_certificado IS NOT NULL THEN 
            'IU-FOC-' || EXTRACT(YEAR FROM CURRENT_DATE) || '-' || COALESCE(cohorte, 1) || '-' || LPAD(COALESCE(tomo, '001'), 3, '0')
        ELSE NULL
    END
WHERE codigo_certificado IS NOT NULL;
*/

-- 6. Insertar datos de prueba para verificar (opcional)
/*
INSERT INTO formacion_complementaria (id_taller, nombre, descripcion, codigo_certificado, cohorte)
VALUES 
(1, 'Taller de Prueba 1', 'Descripción de prueba', 'IU-FOC-2026-1-001', 1),
(2, 'Taller de Prueba 2', 'Descripción de prueba', 'IU-FOC-2026-2-001', 2);
*/

RAISE NOTICE 'Actualización de base de datos completada. Verifique los resultados arriba.';
