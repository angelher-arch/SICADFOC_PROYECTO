-- FOC26DB - Base de Datos para SICADFOC 2026
-- Instituto Universitario Jesus Obrero
-- Sistema de Informacion de Control Academico de Formacion Complementaria
-- Version: 2.0 - FINAL
-- Fecha: 8 de Abril de 2026
-- Encoding: UTF-8

-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla: Persona
CREATE TABLE IF NOT EXISTS persona (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) UNIQUE,
    telefono VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    direccion TEXT,
    fecha_nacimiento DATE,
    genero VARCHAR(10),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Usuario
CREATE TABLE IF NOT EXISTS usuario (
    id SERIAL PRIMARY KEY,
    id_persona INTEGER REFERENCES persona(id),
    cedula_usuario VARCHAR(20) UNIQUE NOT NULL,
    login_usuario VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL CHECK (rol IN ('Administrador', 'Profesor', 'Estudiante')),
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Estudiante
CREATE TABLE IF NOT EXISTS estudiante (
    id_estudiante SERIAL PRIMARY KEY,
    id_persona INTEGER REFERENCES persona(id),
    id_usuario INTEGER REFERENCES usuario(id),
    codigo_estudiante VARCHAR(20) UNIQUE,
    carrera VARCHAR(100),
    semestre INTEGER,
    indice_academico DECIMAL(3,2),
    estado VARCHAR(20) DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo', 'Suspendido')),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Profesor
CREATE TABLE IF NOT EXISTS profesor (
    id_profesor SERIAL PRIMARY KEY,
    id_persona INTEGER REFERENCES persona(id),
    id_usuario INTEGER REFERENCES usuario(id),
    cedula_profesor VARCHAR(20) UNIQUE NOT NULL,
    codigo_profesor VARCHAR(20) UNIQUE,
    correo_personal VARCHAR(100),
    especialidad VARCHAR(100),
    departamento VARCHAR(100),
    categoria VARCHAR(50),
    estado VARCHAR(20) DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo', 'Suspendido')),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Taller
CREATE TABLE IF NOT EXISTS taller (
    id_taller SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre_taller VARCHAR(200) NOT NULL,
    descripcion TEXT,
    duracion_horas INTEGER DEFAULT 40,
    cupos_maximos INTEGER DEFAULT 30,
    requisitos TEXT,
    estado VARCHAR(20) DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo', 'Suspendido')),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Inscripcion
CREATE TABLE IF NOT EXISTS inscripcion (
    id_inscripcion SERIAL PRIMARY KEY,
    id_taller INTEGER REFERENCES taller(id_taller),
    id_estudiante INTEGER REFERENCES estudiante(id_estudiante),
    id_profesor INTEGER REFERENCES profesor(id_profesor),
    fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'Activa' CHECK (estado IN ('Activa', 'Cancelada', 'Completada')),
    nota_final DECIMAL(5,2),
    observaciones TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Notas
CREATE TABLE IF NOT EXISTS notas (
    id_nota SERIAL PRIMARY KEY,
    id_inscripcion INTEGER REFERENCES inscripcion(id_inscripcion),
    id_estudiante INTEGER REFERENCES estudiante(id_estudiante),
    id_taller INTEGER REFERENCES taller(id_taller),
    id_profesor INTEGER REFERENCES profesor(id_profesor),
    parcial1 DECIMAL(5,2),
    parcial2 DECIMAL(5,2),
    parcial3 DECIMAL(5,2),
    trabajo_final DECIMAL(5,2),
    nota_final DECIMAL(5,2),
    estado VARCHAR(20) DEFAULT 'Pendiente' CHECK (estado IN ('Pendiente', 'Aprobado', 'Reprobado')),
    observaciones TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Transaccion
CREATE TABLE IF NOT EXISTS transaccion (
    id_transaccion SERIAL PRIMARY KEY,
    id_usuario INTEGER REFERENCES usuario(id),
    tipo_transaccion VARCHAR(50) NOT NULL,
    descripcion TEXT,
    id_referencia INTEGER,
    tabla_referencia VARCHAR(50),
    estado VARCHAR(20) DEFAULT 'Completada',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices para optimización
CREATE INDEX IF NOT EXISTS idx_usuario_cedula ON usuario(cedula_usuario);
CREATE INDEX IF NOT EXISTS idx_usuario_login ON usuario(login_usuario);
CREATE INDEX IF NOT EXISTS idx_persona_cedula ON persona(cedula);
CREATE INDEX IF NOT EXISTS idx_estudiante_codigo ON estudiante(codigo_estudiante);
CREATE INDEX IF NOT EXISTS idx_profesor_cedula ON profesor(cedula_profesor);
CREATE INDEX IF NOT EXISTS idx_taller_codigo ON taller(codigo);
CREATE INDEX IF NOT EXISTS idx_inscripcion_taller ON inscripcion(id_taller);
CREATE INDEX IF NOT EXISTS idx_inscripcion_estudiante ON inscripcion(id_estudiante);
CREATE INDEX IF NOT EXISTS idx_notas_estudiante ON notas(id_estudiante);
CREATE INDEX IF NOT EXISTS idx_transaccion_usuario ON transaccion(id_usuario);

-- Función para actualizar timestamps
CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para actualizar timestamps
CREATE TRIGGER trg_persona_actualizar 
    BEFORE UPDATE ON persona 
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trg_usuario_actualizar 
    BEFORE UPDATE ON usuario 
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trg_estudiante_actualizar 
    BEFORE UPDATE ON estudiante 
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trg_profesor_actualizar 
    BEFORE UPDATE ON profesor 
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trg_taller_actualizar 
    BEFORE UPDATE ON taller 
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trg_inscripcion_actualizar 
    BEFORE UPDATE ON inscripcion 
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trg_notas_actualizar 
    BEFORE UPDATE ON notas 
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

-- Datos iniciales
INSERT INTO persona (nombre, apellido, email, cedula, telefono) 
VALUES ('Administrador', 'Sistema', 'admin@iujo.edu', 'V-00000000', '+58-212-0000000')
ON CONFLICT (email) DO NOTHING;

INSERT INTO usuario (cedula_usuario, login_usuario, email, contrasena, rol, activo) 
VALUES ('V-00000000', 'admin', 'admin@iujo.edu', 'change_me', 'Administrador', TRUE)
ON CONFLICT (login_usuario) DO NOTHING;

-- Ejemplos de talleres
INSERT INTO taller (codigo, nombre_taller, descripcion, duracion_horas, cupos_maximos, estado)
VALUES 
    ('TALLER-001', 'Introducción a la Programación', 'Curso básico de programación para principiantes', 40, 30, 'Activo'),
    ('TALLER-002', 'Base de Datos SQL', 'Fundamentos de bases de datos relacionales', 40, 25, 'Activo'),
    ('TALLER-003', 'Desarrollo Web', 'Desarrollo de aplicaciones web con HTML, CSS y JavaScript', 60, 20, 'Activo')
ON CONFLICT (codigo) DO NOTHING;
