-- init_database_schema.sql
-- Script recomendado para crear las tablas mínimas que usa el sistema
-- Ejecútalo en la base de datos de producción solo si estás seguro de que la tabla no existe.

SET search_path = public;

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

CREATE TABLE IF NOT EXISTS public.persona (
    cedula VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    apellido VARCHAR(120) NOT NULL,
    email VARCHAR(180),
    telefono VARCHAR(50),
    direccion TEXT,
    fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.profesor (
    cedula_profesor VARCHAR(20) PRIMARY KEY,
    especialidad VARCHAR(120),
    estado VARCHAR(50) DEFAULT 'Activo',
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.estudiante (
    cedula_estudiante VARCHAR(20) PRIMARY KEY,
    nombres VARCHAR(120) NOT NULL,
    apellidos VARCHAR(120) NOT NULL,
    id_carrera INTEGER,
    semestre_actual INTEGER,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW()
);

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

COMMENT ON TABLE public.usuarios IS 'Usuarios del sistema, autenticación y roles';
COMMENT ON TABLE public.formacion_complementaria IS 'Registros de formación complementaria asociados a talleres';
COMMENT ON TABLE public.taller IS 'Información de talleres y actividades formativas';
