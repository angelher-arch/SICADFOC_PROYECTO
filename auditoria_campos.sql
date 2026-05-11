-- =====================================================
-- AUDITORÍA DE CAMPOS - formacion_complementaria
-- =====================================================
-- Sistema: SICADFOC 2026 - Instituto Universitario Jesús Obrero
-- Propósito: Verificar estructura exacta de la tabla y detectar problemas
-- =====================================================

-- 1. Verificar estructura completa de la tabla
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default,
    character_maximum_length,
    ordinal_position
FROM information_schema.columns 
WHERE table_name = 'formacion_complementaria' 
AND table_schema = 'public'
ORDER BY ordinal_position;

-- 2. Verificar PRIMARY KEY y restricciones
SELECT 
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    tc.is_deferrable,
    tc.initially_deferred
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.table_name = 'formacion_complementaria'
AND tc.table_schema = 'public'
ORDER BY tc.constraint_type, kcu.ordinal_position;

-- 3. Verificar si hay secuencias asociadas
SELECT 
    sequence_name,
    start_value,
    increment_by,
    max_value,
    min_value,
    cache_value,
    last_value,
    is_called
FROM information_schema.sequences 
WHERE sequence_schema = 'public'
AND (sequence_name LIKE '%formacion_complementaria%' 
     OR sequence_name LIKE '%id_taller%');

-- 4. Verificar datos existentes para entender el patrón
SELECT 
    id_formacion,
    id_taller,
    nombre,
    codigo_certificado,
    codigo_referencia,
    id_usuario,
    fecha_creacion
FROM public.formacion_complementaria 
ORDER BY id_formacion DESC 
LIMIT 5;

-- 5. Verificar tipos de datos específicos
SELECT 
    a.attname AS column_name,
    pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
    CASE 
        WHEN a.attidentity = 'd' THEN 'DEFAULT'
        WHEN a.attidentity = 'a' THEN 'ALWAYS'
        ELSE 'NONE'
    END AS identity_type,
    CASE 
        WHEN a.attnotnull THEN 'NOT NULL'
        ELSE 'NULL'
    END AS nullable,
    pg_get_expr(d.adbin, d.adrelid) AS default_value
FROM pg_attribute a
LEFT JOIN pg_attrdef d ON a.attrelid = d.adrelid AND a.attnum = d.adnum
WHERE a.attrelid = 'public.formacion_complementaria'::regclass
AND a.attnum > 0
AND NOT a.attisdropped
ORDER BY a.attnum;
