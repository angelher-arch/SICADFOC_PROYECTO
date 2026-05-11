-- =====================================================
-- ANÁLISIS DEL ERROR: Desplazamiento de Columnas
-- =====================================================
-- Error: el valor nulo en la columna «id_taller» viola la restricción de no nulo
-- Fila detectada: (17, null, Desarrollo de Aplicaciones con Streamlit., [Descripción larga...], 20, IU-FOC-2026-1-4, 14300385, fecha, null)
-- =====================================================

-- ANÁLISIS DE LA FILA FALLIDA:
-- Posición 1: 17 (id_formacion?)
-- Posición 2: null (id_taller - ESTE ES EL PROBLEMA)
-- Posición 3: Desarrollo de Aplicaciones con Streamlit. (nombre)
-- Posición 4: [Descripción larga...] (descripcion)
-- Posición 5: 20 (horas)
-- Posición 6: IU-FOC-2026-1-4 (codigo_certificado)
-- Posición 7: 14300385 (id_usuario)
-- Posición 8: fecha (fecha_creacion?)
-- Posición 9: null (codigo_referencia?)

-- PROBLEMAS IDENTIFICADOS:
-- 1. id_taller está recibiendo NULL cuando debería ser auto-generado
-- 2. El INSERT no especifica columnas explícitamente, causando desplazamiento
-- 3. Posible confusión entre id_formacion y id_taller

-- SOLUCIÓN REQUERIDA:
-- INSERT INTO formacion_complementaria (nombre, descripcion, horas, codigo_certificado, id_usuario, codigo_referencia)
-- VALUES (%s, %s, %s, %s, %s, %s)
-- OMITIR id_taller (debe ser auto-generado por SERIAL)
-- OMITIR id_formacion (es auto-incremental)
-- OMITIR fecha_creacion (tiene DEFAULT)

-- VERIFICACIÓN DE ESTRUCTURA REAL:
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default,
    ordinal_position
FROM information_schema.columns 
WHERE table_name = 'formacion_complementaria' 
AND table_schema = 'public'
ORDER BY ordinal_position;
