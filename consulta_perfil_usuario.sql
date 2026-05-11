-- Script para consultar el perfil/rol de las cédulas específicas
-- Verificar qué rol tienen las cédulas: 14300385, V-14300385, V-14300385

-- Consulta principal para todas las variantes de la cédula
SELECT 
    cedula_usuario,
    nombre_usuario,
    apellido_usuario,
    rol,
    email,
    estado,
    fecha_creacion
FROM usuarios 
WHERE cedula_usuario IN ('14300385', 'V-14300385', 'v-14300385')
ORDER BY cedula_usuario;

-- Consulta alternativa si la tabla tiene diferente estructura
SELECT 
    cedula,
    nombre,
    apellido,
    perfil,
    correo,
    estatus,
    fecha_registro
FROM usuarios 
WHERE cedula IN ('14300385', 'V-14300385', 'v-14300385')
ORDER BY cedula;

-- Consulta para verificar si existe alguna tabla de roles/perfiles
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND (table_name LIKE '%rol%' OR table_name LIKE '%perfil%' OR table_name LIKE '%permiso%');

-- Consulta para ver estructura de la tabla usuarios
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'usuarios' 
AND table_schema = 'public'
ORDER BY ordinal_position;
