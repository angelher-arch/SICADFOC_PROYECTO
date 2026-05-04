-- Script para crear tabla de certificados extemporáneos
-- SICADFOC 2026 - Instituto Universitario Jesus Obrero
-- Ejecutar este script en PostgreSQL para crear la tabla necesaria

-- Verificar y crear tabla certificados_extemporaneos
CREATE TABLE IF NOT EXISTS certificados_extemporaneos (
    id_certificado SERIAL PRIMARY KEY,
    nombre_taller VARCHAR(255) NOT NULL,
    nombre_estudiante VARCHAR(255) NOT NULL,
    duracion VARCHAR(50) NOT NULL,
    objetivo TEXT,
    texto_ocr TEXT,
    imagen_certificado TEXT,  -- Almacenado como base64
    fecha_procesamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cedula_usuario_procesador VARCHAR(20) NOT NULL,
    estado VARCHAR(20) DEFAULT 'procesado',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_certificados_extemporaneos_estudiante ON certificados_extemporaneos(nombre_estudiante);
CREATE INDEX IF NOT EXISTS idx_certificados_extemporaneos_taller ON certificados_extemporaneos(nombre_taller);
CREATE INDEX IF NOT EXISTS idx_certificados_extemporaneos_fecha ON certificados_extemporaneos(fecha_procesamiento);
CREATE INDEX IF NOT EXISTS idx_certificados_extemporaneos_procesador ON certificados_extemporaneos(cedula_usuario_procesador);

-- Crear trigger para actualizar fecha_actualización
CREATE OR REPLACE FUNCTION actualizar_fecha_actualizacion_certificados()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_actualizar_certificados ON certificados_extemporaneos;
CREATE TRIGGER trigger_actualizar_certificados
    BEFORE UPDATE ON certificados_extemporaneos
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_actualizacion_certificados();

-- Verificar estructura de la tabla
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'certificados_extemporaneos' 
ORDER BY ordinal_position;

-- Insertar datos de prueba (opcional)
/*
INSERT INTO certificados_extemporaneos (
    nombre_taller, 
    nombre_estudiante, 
    duracion, 
    objetivo, 
    texto_ocr, 
    imagen_certificado, 
    cedula_usuario_procesador
) VALUES (
    'Introducción a Python',
    'Juan Pérez García',
    '40 horas',
    'Aprender los fundamentos de programación en Python',
    'Texto OCR de ejemplo...',
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
    'V-12345678'
);
*/

-- Mostrar registros existentes para verificar
SELECT 
    id_certificado,
    nombre_taller,
    nombre_estudiante,
    duracion,
    fecha_procesamiento,
    estado
FROM certificados_extemporaneos 
ORDER BY id_certificado DESC
LIMIT 10;

RAISE NOTICE 'Tabla certificados_extemporaneos creada exitosamente.';
