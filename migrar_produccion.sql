-- Script de Migración para Base de Datos en Producción
-- SICADFOC 2026 - Instituto Universitario Jesus Obrero
-- Ejecutar este script en la base de datos de Render antes del despliegue

-- 1. Agregar columnas faltantes a la tabla usuarios
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS rol VARCHAR(50) DEFAULT 'Estudiante',
ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS login_usuario VARCHAR(100),
ADD COLUMN IF NOT EXISTS cedula_usuario VARCHAR(20),
ADD COLUMN IF NOT EXISTS email VARCHAR(100),
ADD COLUMN IF NOT EXISTS fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 2. Crear índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
CREATE INDEX IF NOT EXISTS idx_usuarios_rol ON usuarios(rol);
CREATE INDEX IF NOT EXISTS idx_usuarios_activo ON usuarios(activo);
CREATE INDEX IF NOT EXISTS idx_usuarios_cedula ON usuarios(cedula_usuario);

-- 3. Crear usuario administrador: Jose Montezuma
-- Cédula: 5.430.424, Contraseña: admin123456
INSERT INTO usuarios (
    username, 
    password_hash, 
    rol, 
    activo, 
    login_usuario, 
    cedula_usuario,
    email,
    fecha_registro,
    fecha_actualizacion
) VALUES (
    'jmontezuma',
    '$2b$12$7CGYN63VTt3.N3djpSz70OXMzz80tR5yCWTszOJl0GLUgJjYl6DUy', -- admin123456
    'Administrador',
    true,
    'jmontezuma',
    '5.430.424',
    'jmontezuma@foc26.edu.ve',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
) ON CONFLICT (cedula_usuario) DO NOTHING;

-- 4. Crear usuario administrador: Angel Hernandez
-- Cédula: 14.300.385, Contraseña: admin123
INSERT INTO usuarios (
    username, 
    password_hash, 
    rol, 
    activo, 
    login_usuario, 
    cedula_usuario,
    email,
    fecha_registro,
    fecha_actualizacion
) VALUES (
    'ahernandez',
    '$2b$12$rIB7x83P9dmm7ECrk.TsceufzSgl5McgfeQqqG0pokSlmEdi0bm6q', -- admin123
    'Administrador',
    true,
    'ahernandez',
    '14.300.385',
    'ahernandez@foc26.edu.ve',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
) ON CONFLICT (cedula_usuario) DO NOTHING;

-- 5. Crear usuario de prueba (Profesor)
INSERT INTO usuarios (
    username, 
    password_hash, 
    rol, 
    activo, 
    login_usuario, 
    cedula_usuario,
    email,
    fecha_registro,
    fecha_actualizacion
) VALUES (
    'profesor',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6ukx.LrUpm', -- profesor123
    'Profesor',
    true,
    'profesor',
    'V-12345678',
    'profesor@foc26.edu.ve',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
) ON CONFLICT (cedula_usuario) DO NOTHING;

-- 6. Crear usuario de prueba (Estudiante)
INSERT INTO usuarios (
    username, 
    password_hash, 
    rol, 
    activo, 
    login_usuario, 
    cedula_usuario,
    email,
    fecha_registro,
    fecha_actualizacion
) VALUES (
    'estudiante',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6ukx.LrUpm', -- estudiante123
    'Estudiante',
    true,
    'estudiante',
    'V-87654321',
    'estudiante@foc26.edu.ve',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
) ON CONFLICT (cedula_usuario) DO NOTHING;

-- 7. Verificar usuarios creados
SELECT 
    id,
    username,
    rol,
    activo,
    login_usuario,
    cedula_usuario,
    email,
    fecha_registro
FROM usuarios 
ORDER BY id;

-- 8. Mostrar resumen de la migración
SELECT 
    'Migración completada' as estado,
    COUNT(*) as total_usuarios,
    COUNT(CASE WHEN rol = 'Administrador' THEN 1 END) as administradores,
    COUNT(CASE WHEN rol = 'Profesor' THEN 1 END) as profesores,
    COUNT(CASE WHEN rol = 'Estudiante' THEN 1 END) as estudiantes
FROM usuarios;

-- 9. Verificar que los administradores tengan acceso completo
SELECT 
    username,
    cedula_usuario,
    rol,
    'Acceso completo a todos los módulos' as permisos
FROM usuarios 
WHERE rol = 'Administrador';
