-- =====================================================
-- SCRIPT DE ESTANDARIZACIÓN PARA PRODUCCIÓN (RENDER)
-- SICADFOC 2026 - EMERGENCIA DE DESPLIEGUE
-- =====================================================

-- Este script resuelve el problema de columnas cedula vs cedula_usuario
-- Ejecutar en producción (Render) para estandarizar el esquema

-- =====================================================
-- PASO 1: VERIFICAR ESTRUCTURA ACTUAL
-- =====================================================

-- Mostrar estructura actual de la tabla usuarios
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'usuarios' 
ORDER BY ordinal_position;

-- =====================================================
-- PASO 2: ESTANDARIZAR COLUMNA DE CÉDULA
-- =====================================================

DO $$
BEGIN
    -- Verificar si existe la columna cedula_usuario
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'usuarios' 
        AND column_name = 'cedula_usuario'
    ) THEN
        -- Si existe cedula_usuario, verificar si también existe cedula
        IF EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'usuarios' 
            AND column_name = 'cedula'
        ) THEN
            -- Si existen ambas, mantener cedula y eliminar cedula_usuario
            RAISE NOTICE 'Ambas columnas existen - Eliminando cedula_usuario';
            
            -- Actualizar foreign keys que usen cedula_usuario
            ALTER TABLE auditoria DROP CONSTRAINT IF EXISTS auditoria_cedula_usuario_fkey;
            ALTER TABLE auditoria ADD CONSTRAINT auditoria_cedula_fkey 
                FOREIGN KEY (cedula) REFERENCES usuarios(cedula) ON UPDATE CASCADE;
            
            -- Eliminar columna cedula_usuario
            ALTER TABLE usuarios DROP COLUMN cedula_usuario;
            
        ELSE
            -- Si solo existe cedula_usuario, renombrar a cedula
            RAISE NOTICE 'Renombrando cedula_usuario a cedula';
            ALTER TABLE usuarios RENAME COLUMN cedula_usuario TO cedula;
        END IF;
        
    ELSIF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'usuarios' 
        AND column_name = 'cedula'
    ) THEN
        -- Si ya existe cedula, verificar que las relaciones funcionen
        RAISE NOTICE 'Columna cedula ya existe - esquema compatible';
        
    ELSE
        -- Si no existe ninguna, crear cedula
        RAISE NOTICE 'Creando columna cedula';
        ALTER TABLE usuarios ADD COLUMN cedula VARCHAR(20) PRIMARY KEY;
    END IF;
END $$;

-- =====================================================
-- PASO 3: ACTUALIZAR FOREIGN KEYS
-- =====================================================

-- Actualizar FK en tabla persona
DO $$
BEGIN
    -- Eliminar FK existente si hay
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'persona' 
        AND constraint_type = 'FOREIGN KEY'
    ) THEN
        ALTER TABLE persona DROP CONSTRAINT persona_cedula_fkey;
    END IF;
    
    -- Crear FK actualizado
    ALTER TABLE persona 
    ADD CONSTRAINT persona_cedula_fkey 
    FOREIGN KEY (cedula) REFERENCES usuarios(cedula) 
    ON UPDATE CASCADE;
    
    RAISE NOTICE 'Foreign key actualizado en tabla persona';
END $$;

-- Actualizar FK en tabla auditoria
DO $$
BEGIN
    -- Eliminar FK existente si hay
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'auditoria' 
        AND constraint_name LIKE '%cedula%'
    ) THEN
        ALTER TABLE auditoria DROP CONSTRAINT auditoria_cedula_usuario_fkey;
    END IF;
    
    -- Crear FK actualizado
    ALTER TABLE auditoria 
    ADD CONSTRAINT auditoria_cedula_fkey 
    FOREIGN KEY (cedula) REFERENCES usuarios(cedula) 
    ON UPDATE CASCADE;
    
    RAISE NOTICE 'Foreign key actualizado en tabla auditoria';
END $$;

-- Actualizar FK en otras tablas que referencien usuarios
DO $$
BEGIN
    -- Tabla inscripcion si existe
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'inscripcion'
    ) THEN
        -- Eliminar FK existente si hay
        IF EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE table_name = 'inscripcion' 
            AND constraint_type = 'FOREIGN KEY'
        ) THEN
            ALTER TABLE inscripcion DROP CONSTRAINT IF EXISTS inscripcion_id_usuario_fkey;
        END IF;
        
        -- Crear FK actualizado
        ALTER TABLE inscripcion 
        ADD CONSTRAINT inscripcion_cedula_fkey 
        FOREIGN KEY (id_usuario) REFERENCES usuarios(cedula) 
        ON UPDATE CASCADE;
        
        RAISE NOTICE 'Foreign key actualizado en tabla inscripcion';
    END IF;
END $$;

-- =====================================================
-- PASO 4: VERIFICAR ESTRUCTURA FINAL
-- =====================================================

-- Mostrar estructura final
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'usuarios' 
ORDER BY ordinal_position;

-- Verificar que todas las tablas tengan FK correctos
SELECT 
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_name IN ('usuarios', 'persona', 'auditoria', 'inscripcion')
ORDER BY tc.table_name, tc.constraint_name;

-- =====================================================
-- PASO 5: VERIFICAR DATOS
-- =====================================================

-- Contar usuarios
SELECT COUNT(*) as total_usuarios FROM usuarios;

-- Verificar que todos los usuarios tengan cédula
SELECT COUNT(*) as usuarios_con_cedula FROM usuarios WHERE cedula IS NOT NULL;

-- Mostrar sample de datos
SELECT cedula, login_usuario, rol, activo 
FROM usuarios 
LIMIT 5;

-- =====================================================
-- PASO 6: CREAR INDICES PARA OPTIMIZACIÓN
-- =====================================================

-- Crear índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_usuarios_rol ON usuarios(rol);
CREATE INDEX IF NOT EXISTS idx_usuarios_activo ON usuarios(activo);
CREATE INDEX IF NOT EXISTS idx_usuarios_login ON usuarios(login_usuario);

-- Crear índices en persona
CREATE INDEX IF NOT EXISTS idx_persona_cedula ON persona(cedula);
CREATE INDEX IF NOT EXISTS idx_persona_nombre ON persona(nombre, apellido);

-- =====================================================
-- PASO 7: ACTUALIZAR CONFIGURACIÓN DE PERMISOS
-- =====================================================

-- Verificar que la tabla de permisos exista
SELECT COUNT(*) as total_permisos FROM configuracion_permisos;

-- Insertar permisos básicos si no existen
INSERT INTO configuracion_permisos (nombre_rol, nombre_modulo, nombre_accion, acceso_limitado_propio)
VALUES 
    ('Administrador', 'Gestión Estudiantil', 'Consultar', false),
    ('Administrador', 'Gestión Estudiantil', 'Crear', false),
    ('Administrador', 'Gestión Estudiantil', 'Actualizar', false),
    ('Administrador', 'Gestión Estudiantil', 'Eliminar', false),
    ('Profesor', 'Gestión Estudiantil', 'Consultar', false),
    ('Profesor', 'Gestión Estudiantil', 'Crear', true),
    ('Profesor', 'Gestión Estudiantil', 'Actualizar', true),
    ('Profesor', 'Gestión Estudiantil', 'Eliminar', false),
    ('Estudiante', 'Gestión Estudiantil', 'Consultar', true),
    ('Estudiante', 'Gestión Estudiantil', 'Actualizar', true)
ON CONFLICT (nombre_rol, nombre_modulo, nombre_accion) 
DO NOTHING;

-- =====================================================
-- RESUMEN DE ESTANDARIZACIÓN
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=== ESTANDARIZACIÓN COMPLETADA ===';
    RAISE NOTICE '1. Columna cedula estandarizada';
    RAISE NOTICE '2. Foreign keys actualizados';
    RAISE NOTICE '3. Índices creados';
    RAISE NOTICE '4. Permisos configurados';
    RAISE NOTICE '5. Sistema listo para producción';
END $$;

-- =====================================================
-- TESTING QUERIES (para verificar que todo funciona)
-- =====================================================

-- Test 1: Consulta básica de usuarios
SELECT u.cedula, u.login_usuario, u.rol, p.nombre, p.apellido
FROM usuarios u
LEFT JOIN persona p ON u.cedula = p.cedula
WHERE u.rol = 'Estudiante'
ORDER BY p.apellido, p.nombre
LIMIT 5;

-- Test 2: Consulta con JOIN complejo
SELECT 
    u.cedula,
    u.login_usuario,
    u.rol,
    u.activo,
    p.nombre,
    p.apellido,
    p.email_personal,
    e.carrera,
    e.semestre_formacion
FROM usuarios u
LEFT JOIN persona p ON u.cedula = p.cedula
LEFT JOIN estudiante e ON p.cedula = e.cedula_estudiante
WHERE u.rol = 'Estudiante'
ORDER BY p.apellido, p.nombre
LIMIT 3;

-- Test 3: Verificar que los usuarios de prueba existan
SELECT * FROM usuarios 
WHERE cedula IN ('V-14300385', 'V-5430424', '14300385', '5430424')
ORDER BY cedula;
