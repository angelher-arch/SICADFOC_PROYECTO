-- =====================================================
-- MIGRACIÓN: Agregar campo codigo_referencia a formacion_complementaria
-- =====================================================
-- Sistema: SICADFOC 2026 - Instituto Universitario Jesús Obrero
-- Propósito: Mantener id_taller como INTEGER y agregar código de referencia concatenado
-- =====================================================

-- 1. Agregar nuevo campo codigo_referencia
ALTER TABLE formacion_complementaria 
ADD COLUMN codigo_referencia VARCHAR(100);

-- 2. Crear índice para búsquedas rápidas
CREATE INDEX idx_formacion_complementaria_codigo_referencia 
ON formacion_complementaria(codigo_referencia);

-- 3. Actualizar registros existentes con formato de código
-- Formato: {codigo_certificado}-{id_taller}-{nombre_taller}
UPDATE formacion_complementaria 
SET codigo_referencia = 
    CASE 
        WHEN codigo_certificado IS NOT NULL AND nombre IS NOT NULL
        THEN codigo_certificado || '-' || id_taller || '-' || LEFT(nombre, 30)
        ELSE 'SIN-CODIGO-' || id_taller
    END
WHERE codigo_referencia IS NULL;

-- 4. Verificar la migración
SELECT 
    id_formacion,
    id_taller,
    nombre,
    codigo_certificado,
    codigo_referencia,
    fecha_creacion
FROM formacion_complementaria 
ORDER BY id_formacion;

-- =====================================================
-- ESTRUCTURA FINAL ESPERADA:
-- =====================================================
-- id_formacion: SERIAL PRIMARY KEY (auto-incremental)
-- id_taller: INTEGER (mantenido como entero para relaciones)
-- nombre: VARCHAR (nombre del taller)
-- descripcion: TEXT
-- horas: INTEGER
-- codigo_certificado: VARCHAR (ej: IU-FOC-2026-1-004)
-- codigo_referencia: VARCHAR (ej: IU-FOC-2026-1-004-123-Taller de Python)
-- id_usuario: VARCHAR
-- fecha_creacion: TIMESTAMP
-- =====================================================

-- Consulta para verificar estructura final
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'formacion_complementaria' 
ORDER BY ordinal_position;
