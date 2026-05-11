-- MIGRACIÓN DE HOMOLOGACIÓN DE CÉDULAS
-- Normalizar todas las cédulas existentes al formato V-XXXXX
-- Esto asegura consistencia en todo el sistema

-- 1. VERIFICAR ESTADO ACTUAL
SELECT 'ESTADO ANTES DE MIGRACIÓN' as info;
SELECT 
    cedula_usuario,
    CASE 
        WHEN cedula_usuario LIKE 'V-%' THEN 'CORRECTO'
        WHEN cedula_usuario LIKE 'E-%' THEN 'CORRECTO'
        WHEN cedula_usuario ~ '^[0-9]+$' THEN 'SIN PREFIJO'
        ELSE 'OTRO FORMATO'
    END as formato_actual
FROM usuarios 
ORDER BY cedula_usuario;

-- 2. MIGRACIÓN PRINCIPAL - TABLA USUARIOS
BEGIN;

-- Actualizar cédulas sin prefijo a formato V-
UPDATE usuarios 
SET cedula_usuario = 'V-' || cedula_usuario
WHERE cedula_usuario ~ '^[0-9]+$' 
AND cedula_usuario NOT LIKE 'V-%' 
AND cedula_usuario NOT LIKE 'E-%';

-- Actualizar cédulas con prefijo minúscula a mayúscula
UPDATE usuarios 
SET cedula_usuario = 'V' || UPPER(SUBSTRING(cedula_usuario, 2))
WHERE cedula_usuario ~ '^[vV]-[0-9]+$';

-- Actualizar cédulas con prefijo minúscula E a mayúscula
UPDATE usuarios 
SET cedula_usuario = 'E' || UPPER(SUBSTRING(cedula_usuario, 2))
WHERE cedula_usuario ~ '^[eE]-[0-9]+$';

COMMIT;

-- 3. VERIFICAR RESULTADO
SELECT 'ESTADO DESPUÉS DE MIGRACIÓN' as info;
SELECT 
    cedula_usuario,
    CASE 
        WHEN cedula_usuario LIKE 'V-%' THEN 'CORRECTO'
        WHEN cedula_usuario LIKE 'E-%' THEN 'CORRECTO'
        ELSE 'SIN NORMALIZAR'
    END as formato_actual
FROM usuarios 
ORDER BY cedula_usuario;

-- 4. MIGRACIÓN DE TABLAS RELACIONADAS (si existen)

-- Tabla persona (si existe)
BEGIN;
UPDATE persona 
SET cedula = 'V-' || cedula
WHERE cedula ~ '^[0-9]+$' 
AND cedula NOT LIKE 'V-%' 
AND cedula NOT LIKE 'E-%';

UPDATE persona 
SET cedula = 'V' || UPPER(SUBSTRING(cedula, 2))
WHERE cedula ~ '^[vV]-[0-9]+$';

UPDATE persona 
SET cedula = 'E' || UPPER(SUBSTRING(cedula, 2))
WHERE cedula ~ '^[eE]-[0-9]+$';
COMMIT;

-- Tabla estudiantes (si existe)
BEGIN;
UPDATE estudiantes 
SET cedula_estudiante = 'V-' || cedula_estudiante
WHERE cedula_estudiante ~ '^[0-9]+$' 
AND cedula_estudiante NOT LIKE 'V-%' 
AND cedula_estudiante NOT LIKE 'E-%';

UPDATE estudiantes 
SET cedula_estudiante = 'V' || UPPER(SUBSTRING(cedula_estudiante, 2))
WHERE cedula_estudiante ~ '^[vV]-[0-9]+$';

UPDATE estudiantes 
SET cedula_estudiante = 'E' || UPPER(SUBSTRING(cedula_estudiante, 2))
WHERE cedula_estudiante ~ '^[eE]-[0-9]+$';
COMMIT;

-- Tabla profesores (si existe)
BEGIN;
UPDATE profesores 
SET cedula_profesor = 'V-' || cedula_profesor
WHERE cedula_profesor ~ '^[0-9]+$' 
AND cedula_profesor NOT LIKE 'V-%' 
AND cedula_profesor NOT LIKE 'E-%';

UPDATE profesores 
SET cedula_profesor = 'V' || UPPER(SUBSTRING(cedula_profesor, 2))
WHERE cedula_profesor ~ '^[vV]-[0-9]+$';

UPDATE profesores 
SET cedula_profesor = 'E' || UPPER(SUBSTRING(cedula_profesor, 2))
WHERE cedula_profesor ~ '^[eE]-[0-9]+$';
COMMIT;

-- Tabla inscripciones (si existe)
BEGIN;
UPDATE inscripciones 
SET cedula_estudiante = 'V-' || cedula_estudiante
WHERE cedula_estudiante ~ '^[0-9]+$' 
AND cedula_estudiante NOT LIKE 'V-%' 
AND cedula_estudiante NOT LIKE 'E-%';

UPDATE inscripciones 
SET cedula_estudiante = 'V' || UPPER(SUBSTRING(cedula_estudiante, 2))
WHERE cedula_estudiante ~ '^[vV]-[0-9]+$';

UPDATE inscripciones 
SET cedula_estudiante = 'E' || UPPER(SUBSTRING(cedula_estudiante, 2))
WHERE cedula_estudiante ~ '^[eE]-[0-9]+$';
COMMIT;

-- 5. VERIFICACIÓN FINAL DE CONSISTENCIA
SELECT 'VERIFICACIÓN FINAL DE CONSISTENCIA' as info;

-- Contar usuarios por formato
SELECT 
    CASE 
        WHEN cedula_usuario LIKE 'V-%' THEN 'VENEZOLANO'
        WHEN cedula_usuario LIKE 'E-%' THEN 'EXTRANJERO'
        ELSE 'SIN CLASIFICAR'
    END as tipo_documento,
    COUNT(*) as cantidad
FROM usuarios 
GROUP BY 
    CASE 
        WHEN cedula_usuario LIKE 'V-%' THEN 'VENEZOLANO'
        WHEN cedula_usuario LIKE 'E-%' THEN 'EXTRANJERO'
        ELSE 'SIN CLASIFICAR'
    END
ORDER BY cantidad DESC;

-- Mostrar usuarios actualizados
SELECT 
    'USUARIOS ACTUALIZADOS' as info,
    cedula_usuario,
    login_usuario,
    rol
FROM usuarios 
ORDER BY cedula_usuario;

SELECT 'MIGRACIÓN COMPLETADA - TODAS LAS CÉDULAS NORMALIZADAS A FORMATO V-XXXXX O E-XXXXX' as mensaje;
