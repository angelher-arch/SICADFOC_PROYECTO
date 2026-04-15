-- FOC26DB - Base de Datos para SICADFOC 2026
-- Instituto Universitario Jesus Obrero
-- Sistema de Informacion de Control Academico de Formacion Complementaria
-- Version: 2.0
-- Fecha: 7 de Abril de 2026
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
    cedula_usuario VARCHAR(20) UNIQUE,
    login_usuario VARCHAR(100) UNIQUE,
    email VARCHAR(100) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL CHECK (rol IN ('Administrador', 'Profesor', 'Estudiante')),
    activo BOOLEAN DEFAULT TRUE,
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

-- Tabla: Formacion
CREATE TABLE IF NOT EXISTS formacion (
    id_formacion SERIAL PRIMARY KEY,
    id_taller INTEGER REFERENCES taller(id_taller),
    codigo_cohorte VARCHAR(50) UNIQUE NOT NULL,
    nombre_cohorte VARCHAR(200) NOT NULL,
    descripcion TEXT,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    cupos_maximos INTEGER DEFAULT 30,
    cupos_disponibles INTEGER DEFAULT 30,
    instructor VARCHAR(100),
    estado VARCHAR(20) DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo', 'Finalizado', 'Cancelado', 'Pospuesto')),
    observacion_estado TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Inscripcion
CREATE TABLE IF NOT EXISTS inscripcion (
    id_inscripcion SERIAL PRIMARY KEY,
    id_formacion INTEGER REFERENCES formacion(id_formacion),
    id_usuario INTEGER REFERENCES usuario(id),
    fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'Activa' CHECK (estado IN ('Activa', 'Cancelada', 'Completada', 'Abandonada')),
    calificacion DECIMAL(5,2),
    certificado_emitido BOOLEAN DEFAULT FALSE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(id_formacion, id_usuario)
);

-- Tabla: Asistencia
CREATE TABLE IF NOT EXISTS asistencia (
    id_asistencia SERIAL PRIMARY KEY,
    id_inscripcion INTEGER REFERENCES inscripcion(id_inscripcion),
    fecha_asistencia DATE NOT NULL,
    estado VARCHAR(20) DEFAULT 'Presente' CHECK (estado IN ('Presente', 'Ausente', 'Tarde', 'Justificado')),
    observaciones TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(id_inscripcion, fecha_asistencia)
);

-- Tabla: Evaluacion
CREATE TABLE IF NOT EXISTS evaluacion (
    id_evaluacion SERIAL PRIMARY KEY,
    id_formacion INTEGER REFERENCES formacion(id_formacion),
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(50) DEFAULT 'Parcial' CHECK (tipo IN ('Parcial', 'Final', 'Practica', 'Proyecto')),
    fecha_evaluacion DATE NOT NULL,
    ponderacion DECIMAL(5,2) DEFAULT 10.00,
    estado VARCHAR(20) DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo')),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Nota
CREATE TABLE IF NOT EXISTS nota (
    id_nota SERIAL PRIMARY KEY,
    id_evaluacion INTEGER REFERENCES evaluacion(id_evaluacion),
    id_inscripcion INTEGER REFERENCES inscripcion(id_inscripcion),
    calificacion DECIMAL(5,2) NOT NULL,
    observaciones TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(id_evaluacion, id_inscripcion)
);

-- Tabla: Certificado
CREATE TABLE IF NOT EXISTS certificado (
    id_certificado SERIAL PRIMARY KEY,
    id_inscripcion INTEGER REFERENCES inscripcion(id_inscripcion),
    codigo_certificado VARCHAR(50) UNIQUE NOT NULL,
    fecha_emision DATE DEFAULT CURRENT_DATE,
    fecha_vencimiento DATE,
    estado VARCHAR(20) DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Revocado', 'Expirado')),
    url_certificado TEXT,
    entregado BOOLEAN DEFAULT FALSE,
    fecha_entrega DATE,
    enviado_correo BOOLEAN DEFAULT FALSE,
    adjunto_url TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Configuracion
CREATE TABLE IF NOT EXISTS configuracion (
    id_config SERIAL PRIMARY KEY,
    clave VARCHAR(100) UNIQUE NOT NULL,
    valor TEXT,
    descripcion TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Estudiante
CREATE TABLE IF NOT EXISTS estudiante (
    id_estudiante SERIAL PRIMARY KEY,
    id_persona INTEGER REFERENCES persona(id),
    id_usuario INTEGER REFERENCES usuario(id),
    codigo_estudiantil VARCHAR(50) UNIQUE NOT NULL,
    carrera VARCHAR(100),
    semestre_actual VARCHAR(50),
    estado VARCHAR(50) DEFAULT 'Activo',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Profesor
CREATE TABLE IF NOT EXISTS profesor (
    id_profesor SERIAL PRIMARY KEY,
    id_persona INTEGER UNIQUE REFERENCES persona(id) ON DELETE CASCADE,
    id_usuario INTEGER UNIQUE REFERENCES usuario(id) ON DELETE CASCADE,
    cedula_profesor VARCHAR(20) UNIQUE NOT NULL,
    correo_personal VARCHAR(100),
    codigo_profesor VARCHAR(50) UNIQUE,
    especialidad VARCHAR(100),
    departamento VARCHAR(100),
    categoria VARCHAR(100),
    estado VARCHAR(20) DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo')),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_profesor_departamento ON profesor(departamento);
CREATE INDEX IF NOT EXISTS idx_profesor_estado ON profesor(estado);

-- Tabla: Horario de Formacion
CREATE TABLE IF NOT EXISTS horario_formacion (
    id_horario SERIAL PRIMARY KEY,
    id_formacion INTEGER REFERENCES formacion(id_formacion),
    dia_semana VARCHAR(20) NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Solicitud de Taller
CREATE TABLE IF NOT EXISTS solicitud_taller (
    id_solicitud SERIAL PRIMARY KEY,
    id_usuario INTEGER REFERENCES usuario(id),
    titulo_propuesto VARCHAR(200),
    descripcion TEXT,
    tipo_taller VARCHAR(100),
    carreras_autorizadas TEXT,
    semestres_autorizados TEXT,
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'Pendiente' CHECK (estado IN ('Pendiente', 'Aceptada', 'Rechazada')),
    observacion TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Auditoria
CREATE TABLE IF NOT EXISTS auditoria (
    id_auditoria SERIAL PRIMARY KEY,
    id_transaccion VARCHAR(50),
    id_usuario INTEGER REFERENCES usuario(id),
    tipo_transaccion VARCHAR(100),
    accion VARCHAR(100) NOT NULL,
    tabla_afectada VARCHAR(100),
    registro_id INTEGER,
    valores_anteriores TEXT,
    valores_nuevos TEXT,
    ip_address VARCHAR(50),
    fecha_accion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_usuario_email ON usuario(email);
CREATE INDEX IF NOT EXISTS idx_usuario_activo ON usuario(activo);
CREATE INDEX IF NOT EXISTS idx_taller_estado ON taller(estado);
CREATE INDEX IF NOT EXISTS idx_formacion_estado ON formacion(estado);
CREATE INDEX IF NOT EXISTS idx_formacion_fechas ON formacion(fecha_inicio, fecha_fin);
CREATE INDEX IF NOT EXISTS idx_inscripcion_usuario ON inscripcion(id_usuario);
CREATE INDEX IF NOT EXISTS idx_inscripcion_formacion ON inscripcion(id_formacion);
CREATE INDEX IF NOT EXISTS idx_inscripcion_estado ON inscripcion(estado);
CREATE INDEX IF NOT EXISTS idx_asistencia_fecha ON asistencia(fecha_asistencia);
CREATE INDEX IF NOT EXISTS idx_evaluacion_fecha ON evaluacion(fecha_evaluacion);
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON auditoria(fecha_accion);
CREATE INDEX IF NOT EXISTS idx_auditoria_usuario ON auditoria(id_usuario);

-- Triggers para actualizar timestamps
CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar triggers a tablas que necesiten actualización automática
CREATE TRIGGER trg_persona_timestamp 
    BEFORE UPDATE ON persona 
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trg_usuario_timestamp 
    BEFORE UPDATE ON usuario 
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trg_taller_timestamp 
    BEFORE UPDATE ON taller 
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trg_formacion_timestamp 
    BEFORE UPDATE ON formacion 
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trg_inscripcion_timestamp 
    BEFORE UPDATE ON inscripcion 
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trg_asistencia_timestamp 
    BEFORE UPDATE ON asistencia 
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trg_evaluacion_timestamp 
    BEFORE UPDATE ON evaluacion 
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trg_nota_timestamp 
    BEFORE UPDATE ON nota 
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trg_profesor_timestamp 
    BEFORE UPDATE ON profesor 
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trg_certificado_timestamp 
    BEFORE UPDATE ON certificado 
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TRIGGER trg_configuracion_timestamp 
    BEFORE UPDATE ON configuracion 
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

-- Datos iniciales

-- Insertar configuración básica
INSERT INTO configuracion (clave, valor, descripcion) VALUES
('nombre_institucion', 'Instituto Universitario Jesus Obrero', 'Nombre de la institucion'),
('siglas_institucion', 'IUJO', 'Siglas de la institucion'),
('anio_academico', '2026', 'Anio academico actual'),
('version_sistema', '2.0', 'Version del sistema SICADFOC'),
('email_admin', 'admin@iujo.edu', 'Email del administrador'),
('telefono_institucion', '+58-212-1234567', 'Telefono de la institucion'),
('direccion_institucion', 'Caracas, Venezuela', 'Direccion de la institucion')
ON CONFLICT (clave) DO NOTHING;

-- Insertar usuario administrador
INSERT INTO persona (nombre, apellido, email, cedula, telefono) VALUES
('Administrador', 'Sistema', 'admin@iujo.edu', 'V-00000000', '+58-212-0000000')
ON CONFLICT (email) DO NOTHING;

INSERT INTO usuario (id_persona, cedula_usuario, login_usuario, email, contrasena, rol, activo) VALUES
(1, 'V-00000000', 'admin', 'admin@iujo.edu', 'admin123', 'Administrador', TRUE)
ON CONFLICT (email) DO NOTHING;

-- Insertar talleres de formacion complementaria
INSERT INTO taller (codigo, nombre_taller, descripcion, duracion_horas, cupos_maximos, estado) VALUES
('TFC01', 'Inteligencia Artificial Basica', 'Introduccion a los conceptos fundamentales de IA', 40, 30, 'Activo'),
('TFC02', 'Etica Profesional', 'Principios eticos en el ejercicio profesional', 20, 50, 'Activo'),
('TFC03', 'Herramientas Digitales', 'Uso eficiente de herramientas digitales modernas', 30, 40, 'Activo'),
('TFC04', 'Programacion Python', 'Curso intensivo de programacion en Python', 60, 25, 'Activo'),
('TFC05', 'Base de Datos SQL', 'Fundamentos de bases de datos relacionales', 40, 30, 'Activo'),
('TFC06', 'Redes de Computadoras', 'Conceptos basicos de redes y comunicaciones', 40, 30, 'Activo'),
('TFC07', 'Desarrollo Web Full Stack', 'Frontend y backend con tecnologias modernas', 80, 20, 'Activo'),
('TFC08', 'Seguridad Informatica', 'Principios de seguridad cibernetica', 40, 30, 'Activo'),
('TFC09', 'Cloud Computing', 'Servicios en la nube y arquitecturas cloud', 40, 30, 'Activo'),
('TFC10', 'Machine Learning', 'Algoritmos de aprendizaje automatico', 60, 25, 'Activo')
ON CONFLICT (codigo) DO NOTHING;

-- Insertar formaciones para el trimestre actual
INSERT INTO formacion (id_taller, codigo_cohorte, nombre_cohorte, descripcion, fecha_inicio, fecha_fin, cupos_maximos, cupos_disponibles, instructor, estado) VALUES
(1, 'TFC01_202604', 'IA Basica - Abril 2026', 'Formacion en IA Basica para el trimestre Abril-Junio', '2026-04-01', '2026-06-30', 30, 25, 'Dr. Juan Perez', 'Activo'),
(2, 'TFC02_202604', 'Etica Profesional - Abril 2026', 'Formacion en Etica Profesional para el trimestre Abril-Junio', '2026-04-15', '2026-05-15', 50, 45, 'Lic. Maria Garcia', 'Activo'),
(3, 'TFC03_202604', 'Herramientas Digitales - Abril 2026', 'Formacion en Herramientas Digitales para el trimestre Abril-Junio', '2026-04-01', '2026-05-30', 40, 35, 'Ing. Carlos Rodriguez', 'Activo'),
(4, 'TFC04_202604', 'Python - Abril 2026', 'Formacion en Programacion Python para el trimestre Abril-Junio', '2026-04-01', '2026-07-31', 25, 20, 'MSc. Ana Martinez', 'Activo'),
(5, 'TFC05_202604', 'SQL - Abril 2026', 'Formacion en Base de Datos SQL para el trimestre Abril-Junio', '2026-04-15', '2026-06-15', 30, 28, 'Ing. Luis Hernandez', 'Activo')
ON CONFLICT (codigo_cohorte) DO NOTHING;

-- Comentarios para documentacion
COMMENT ON DATABASE FOC26DB IS 'Base de datos para SICADFOC 2026 - Instituto Universitario Jesus Obrero';
COMMENT ON TABLE persona IS 'Informacion personal de todas las personas del sistema';
COMMENT ON TABLE usuario IS 'Cuentas de acceso al sistema con roles y permisos';
COMMENT ON TABLE taller IS 'Catalogo de talleres de formacion complementaria';
COMMENT ON TABLE formacion IS 'Cohortes o ediciones de talleres con fechas especificas';
COMMENT ON TABLE inscripcion IS 'Registro de estudiantes inscritos en formaciones';
COMMENT ON TABLE asistencia IS 'Control de asistencia por fecha y estudiante';
COMMENT ON TABLE evaluacion IS 'Evaluaciones y examenes por formacion';
COMMENT ON TABLE nota IS 'Calificaciones de estudiantes por evaluacion';
COMMENT ON TABLE certificado IS 'Certificados emitidos a estudiantes';
COMMENT ON TABLE configuracion IS 'Parametros de configuracion del sistema';
COMMENT ON TABLE auditoria IS 'Registro de auditoria de cambios en el sistema';

-- Finalizacion del script
SELECT 'FOC26DB - Base de datos creada exitosamente' as mensaje;
