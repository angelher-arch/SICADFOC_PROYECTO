-- =====================================================
-- VERIFICACIÓN DE ESTRUCTURA DE TABLA formacion_complementaria
-- =====================================================
-- Sistema: SICADFOC 2026 - Instituto Universitario Jesús Obrero
-- Propósito: Verificar estructura actual y configuración de auto-incremento
-- =====================================================

-- 1. Verificar estructura completa de la tabla
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'formacion_complementaria' 
AND table_schema = 'public'
ORDER BY ordinal_position;

-- 2. Verificar si id_taller tiene secuencia configurada
SELECT 
    a.attname AS column_name,
    pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
    CASE 
        WHEN a.attidentity = 'd' THEN 'DEFAULT'
        WHEN a.attidentity = 'a' THEN 'ALWAYS'
        ELSE 'NONE'
    END AS identity_type,
    pg_get_expr(d.adbin, d.adrelid) AS default_expr
FROM pg_attribute a
LEFT JOIN pg_attrdef d ON a.attrelid = d.adrelid AND a.attnum = d.adnum
WHERE a.attrelid = 'public.formacion_complementaria'::regclass
AND a.attnum > 0
AND NOT a.attisdropped
ORDER BY a.attnum;

-- 3. Verificar secuencias existentes
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
AND sequence_name LIKE '%formacion_complementaria%'
OR sequence_name LIKE '%id_taller%';

-- 4. Verificar PRIMARY KEY
SELECT 
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.table_name = 'formacion_complementaria'
AND tc.table_schema = 'public'
AND tc.constraint_type = 'PRIMARY KEY';

-- 5. Verificar datos existentes
SELECT 
    COUNT(*) as total_registros,
    MAX(id_taller) as max_id_taller,
    MIN(id_taller) as min_id_taller
FROM public.formacion_complementaria;
