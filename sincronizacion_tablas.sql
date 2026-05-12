-- sincronizacion_tablas.sql
-- Script de sincronización automática para SICADFOC 2026
-- Ejecuta CREATE TABLE IF NOT EXISTS para asegurar que todas las tablas existan

SET search_path = public;

-- Tabla usuarios (autenticación y roles)
CREATE TABLE IF NOT EXISTS public.usuarios (
    cedula_usuario VARCHAR(20) PRIMARY KEY,
    login_usuario VARCHAR(120) UNIQUE NOT NULL,
    username VARCHAR(120),
    contrasena VARCHAR(256),
    password_hash VARCHAR(256),
    rol VARCHAR(50) NOT NULL DEFAULT 'Estudiante',
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    modulos_permitidos TEXT,
    fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tabla persona (datos personales)
CREATE TABLE IF NOT EXISTS public.persona (
    id SERIAL PRIMARY KEY,
    cedula VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(120) NOT NULL,
    apellido VARCHAR(120) NOT NULL,
    email VARCHAR(180),
    telefono VARCHAR(50),
    fecha_nacimiento DATE,
    genero VARCHAR(20),
    direccion TEXT,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tabla carrera (carreras académicas)
CREATE TABLE IF NOT EXISTS public.carrera (
    id_carrera SERIAL PRIMARY KEY,
    nombre_carrera VARCHAR(200) UNIQUE NOT NULL,
    descripcion_carrera TEXT,
    codigo_carrera VARCHAR(20),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tabla profesor
CREATE TABLE IF NOT EXISTS public.profesor (
    cedula_profesor VARCHAR(20) PRIMARY KEY,
    especialidad VARCHAR(120),
    estado VARCHAR(50) DEFAULT 'Activo',
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla estudiante
CREATE TABLE IF NOT EXISTS public.estudiante (
    cedula_estudiante VARCHAR(20) PRIMARY KEY,
    id_persona INTEGER REFERENCES public.persona(id),
    id_carrera INTEGER REFERENCES public.carrera(id_carrera),
    semestre_actual INTEGER DEFAULT 1,
    estado_registro VARCHAR(50) DEFAULT 'Activo',
    fecha_ingreso DATE DEFAULT CURRENT_DATE,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tabla taller
CREATE TABLE IF NOT EXISTS public.taller (
    id_taller SERIAL PRIMARY KEY,
    nombre_taller TEXT NOT NULL,
    descripcion_taller TEXT,
    cedula_profesor VARCHAR(20) REFERENCES public.profesor(cedula_profesor),
    capacidad_maxima INTEGER NOT NULL DEFAULT 0,
    duracion_horas INTEGER NOT NULL DEFAULT 0,
    fecha_inicio DATE,
    fecha_fin DATE,
    estado VARCHAR(50) DEFAULT 'activo',
    tipo_taller VARCHAR(50) DEFAULT 'regular'
);

-- Tabla formacion_complementaria
CREATE TABLE IF NOT EXISTS public.formacion_complementaria (
    id_formacion SERIAL PRIMARY KEY,
    id_taller INTEGER NOT NULL REFERENCES public.taller(id_taller),
    nombre TEXT NOT NULL,
    descripcion TEXT,
    horas INTEGER NOT NULL DEFAULT 0,
    codigo_certificado VARCHAR(120),
    id_usuario VARCHAR(20) REFERENCES public.usuarios(cedula_usuario),
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    codigo_referencia VARCHAR(120)
);

-- Tabla configuracion_permisos
CREATE TABLE IF NOT EXISTS public.configuracion_permisos (
    id SERIAL PRIMARY KEY,
    rol VARCHAR(50) NOT NULL,
    modulo VARCHAR(100) NOT NULL,
    accion VARCHAR(50) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (rol, modulo, accion)
);

-- Tabla permisos
CREATE TABLE IF NOT EXISTS public.permisos (
    id SERIAL PRIMARY KEY,
    rol VARCHAR(50) NOT NULL,
    modulo VARCHAR(100) NOT NULL,
    accion VARCHAR(50) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (rol, modulo, accion)
);

-- Comentarios en las tablas principales
COMMENT ON TABLE public.usuarios IS 'Usuarios del sistema, autenticación y roles';
COMMENT ON TABLE public.persona IS 'Datos personales de usuarios del sistema';
COMMENT ON TABLE public.carrera IS 'Carreras académicas disponibles';
COMMENT ON TABLE public.estudiante IS 'Estudiantes registrados con relación a persona y carrera';
COMMENT ON TABLE public.profesor IS 'Profesores del sistema';
COMMENT ON TABLE public.taller IS 'Talleres y actividades formativas';
COMMENT ON TABLE public.formacion_complementaria IS 'Registros de formación complementaria asociados a talleres';
COMMENT ON TABLE public.configuracion_permisos IS 'Configuración de permisos por rol';
COMMENT ON TABLE public.permisos IS 'Permisos activos del sistema';

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_persona_cedula ON public.persona(cedula);
CREATE INDEX IF NOT EXISTS idx_estudiante_id_persona ON public.estudiante(id_persona);
CREATE INDEX IF NOT EXISTS idx_estudiante_id_carrera ON public.estudiante(id_carrera);
CREATE INDEX IF NOT EXISTS idx_usuarios_login ON public.usuarios(login_usuario);
CREATE INDEX IF NOT EXISTS idx_usuarios_rol ON public.usuarios(rol);