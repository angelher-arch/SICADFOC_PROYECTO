-- =====================================================
-- SCRIPT DE SINCRONIZACIÓN DE TABLAS SICADFOC 2026
-- Basado en nombres reales de DBeaver (español)
-- =====================================================

-- Verificar y crear tablas faltantes según lista de DBeaver:
-- 'asistencia', 'auditoria', 'carrera', 'certificado', 'configuracion', 
-- 'configuracion_permisos', 'estudiante', 'evaluacion', 'formacion', 
-- 'formacion_complementaria', 'inscripcion', 'nota', 'permisos', 'persona', 
-- 'profesor', 'semestre', 'taller', 'usuario', 'usuarios', 
-- 'val_estado_registro', 'val_nivel_academico', 'val_sexo', 'val_tipo_taller'

-- =====================================================
-- TABLAS PRINCIPALES DE USUARIOS Y PERSONAS
-- =====================================================

-- Tabla de usuarios (principal)
CREATE TABLE IF NOT EXISTS usuarios (
    cedula_usuario VARCHAR(20) PRIMARY KEY,
    login_usuario VARCHAR(100) NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL,
    activo BOOLEAN DEFAULT true,
    email VARCHAR(100),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de datos personales
CREATE TABLE IF NOT EXISTS persona (
    cedula VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE,
    telefono VARCHAR(20),
    direccion TEXT,
    email_personal VARCHAR(100),
    sexo CHAR(1),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cedula) REFERENCES usuarios(cedula_usuario) ON UPDATE CASCADE
);

-- =====================================================
-- TABLAS ACADÉMICAS
-- =====================================================

-- Tabla de carreras
CREATE TABLE IF NOT EXISTS carrera (
    id_carrera SERIAL PRIMARY KEY,
    nombre_carrera VARCHAR(100) NOT NULL UNIQUE,
    descripcion_carrera TEXT,
    cantidad_semestres INTEGER DEFAULT 10,
    codigo_carrera VARCHAR(20) UNIQUE,
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de estudiantes
CREATE TABLE IF NOT EXISTS estudiante (
    cedula_estudiante VARCHAR(20) PRIMARY KEY,
    indice_academico DECIMAL(5,2) DEFAULT 0.00,
    semestre_actual INTEGER DEFAULT 1,
    id_carrera INTEGER NOT NULL,
    estado_registro VARCHAR(20) DEFAULT 'Activo',
    fecha_ingreso DATE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cedula_estudiante) REFERENCES persona(cedula) ON UPDATE CASCADE,
    FOREIGN KEY (id_carrera) REFERENCES carrera(id_carrera) ON UPDATE CASCADE
);

-- Tabla de profesores
CREATE TABLE IF NOT EXISTS profesor (
    cedula_profesor VARCHAR(20) PRIMARY KEY,
    especialidad VARCHAR(100),
    fecha_contratacion DATE,
    categoria VARCHAR(50),
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cedula_profesor) REFERENCES persona(cedula) ON UPDATE CASCADE
);

-- =====================================================
-- TABLAS DE FORMACIÓN COMPLEMENTARIA
-- =====================================================

-- Tabla de talleres
CREATE TABLE IF NOT EXISTS taller (
    id_taller SERIAL PRIMARY KEY,
    nombre_taller VARCHAR(100) NOT NULL,
    descripcion_taller TEXT,
    cedula_profesor VARCHAR(20),
    capacidad_maxima INTEGER DEFAULT 30,
    duracion_horas INTEGER DEFAULT 20,
    fecha_inicio DATE,
    fecha_fin DATE,
    estado VARCHAR(20) DEFAULT 'activo',
    tipo_taller VARCHAR(50) DEFAULT 'regular',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cedula_profesor) REFERENCES profesor(cedula_profesor) ON UPDATE CASCADE
);

-- Tabla de formacion complementaria
CREATE TABLE IF NOT EXISTS formacion_complementaria (
    id_formacion SERIAL PRIMARY KEY,
    id_taller INTEGER NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    horas INTEGER DEFAULT 20,
    codigo_certificado VARCHAR(50),
    id_usuario VARCHAR(20),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_taller) REFERENCES taller(id_taller) ON UPDATE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(cedula_usuario) ON UPDATE CASCADE
);

-- Tabla de inscripciones
CREATE TABLE IF NOT EXISTS inscripcion (
    id_inscripcion SERIAL PRIMARY KEY,
    cedula_estudiante VARCHAR(20) NOT NULL,
    id_formacion INTEGER NOT NULL,
    fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    calificacion DECIMAL(5,2),
    estado VARCHAR(20) DEFAULT 'inscrito',
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cedula_estudiante) REFERENCES estudiante(cedula_estudiante) ON UPDATE CASCADE,
    FOREIGN KEY (id_formacion) REFERENCES formacion_complementaria(id_formacion) ON UPDATE CASCADE,
    UNIQUE(cedula_estudiante, id_formacion)
);

-- Tabla de solicitudes extemporáneas
CREATE TABLE IF NOT EXISTS solicitudes_extemporaneas (
    id_solicitud SERIAL PRIMARY KEY,
    cedula_solicitante VARCHAR(20) NOT NULL,
    tipo_solicitud VARCHAR(50) NOT NULL,
    taller_original VARCHAR(100),
    motivo_solicitud TEXT NOT NULL,
    fecha_solicitud DATE NOT NULL,
    fecha_deseada DATE,
    urgencia VARCHAR(20) DEFAULT 'Media',
    descripcion TEXT,
    archivo_soporte VARCHAR(255),
    contenido_archivo BYTEA,
    estado VARCHAR(20) DEFAULT 'Pendiente',
    fecha_revision TIMESTAMP,
    revisado_por VARCHAR(20),
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cedula_solicitante) REFERENCES persona(cedula) ON UPDATE CASCADE,
    FOREIGN KEY (revisado_por) REFERENCES usuarios(cedula_usuario) ON UPDATE CASCADE
);

-- =====================================================
-- TABLAS DE EVALUACIÓN Y CERTIFICACIÓN
-- =====================================================

-- Tabla de evaluaciones
CREATE TABLE IF NOT EXISTS evaluacion (
    id_evaluacion SERIAL PRIMARY KEY,
    cedula_estudiante VARCHAR(20) NOT NULL,
    id_taller INTEGER NOT NULL,
    tipo_evaluacion VARCHAR(50),
    calificacion DECIMAL(5,2),
    fecha_evaluacion DATE,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cedula_estudiante) REFERENCES estudiante(cedula_estudiante) ON UPDATE CASCADE,
    FOREIGN KEY (id_taller) REFERENCES taller(id_taller) ON UPDATE CASCADE
);

-- Tabla de notas
CREATE TABLE IF NOT EXISTS nota (
    id_nota SERIAL PRIMARY KEY,
    cedula_estudiante VARCHAR(20) NOT NULL,
    id_evaluacion INTEGER NOT NULL,
    valor_nota DECIMAL(5,2),
    ponderacion DECIMAL(5,2),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cedula_estudiante) REFERENCES estudiante(cedula_estudiante) ON UPDATE CASCADE,
    FOREIGN KEY (id_evaluacion) REFERENCES evaluacion(id_evaluacion) ON UPDATE CASCADE
);

-- Tabla de certificados
CREATE TABLE IF NOT EXISTS certificado (
    id_certificado SERIAL PRIMARY KEY,
    cedula_estudiante VARCHAR(20) NOT NULL,
    id_taller INTEGER,
    tipo_certificado VARCHAR(50) NOT NULL,
    fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    codigo_verificacion VARCHAR(50) UNIQUE,
    estado VARCHAR(20) DEFAULT 'emitido',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cedula_estudiante) REFERENCES estudiante(cedula_estudiante) ON UPDATE CASCADE,
    FOREIGN KEY (id_taller) REFERENCES taller(id_taller) ON UPDATE CASCADE
);

-- =====================================================
-- TABLAS DE CONTROL Y ASISTENCIA
-- =====================================================

-- Tabla de asistencia
CREATE TABLE IF NOT EXISTS asistencia (
    id_asistencia SERIAL PRIMARY KEY,
    cedula_estudiante VARCHAR(20) NOT NULL,
    id_taller INTEGER NOT NULL,
    fecha_asistencia DATE,
    estado_asistencia VARCHAR(20) DEFAULT 'presente',
    observaciones TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cedula_estudiante) REFERENCES estudiante(cedula_estudiante) ON UPDATE CASCADE,
    FOREIGN KEY (id_taller) REFERENCES taller(id_taller) ON UPDATE CASCADE
);

-- Tabla de auditoria
CREATE TABLE IF NOT EXISTS auditoria (
    id_auditoria SERIAL PRIMARY KEY,
    fecha_auditoria TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cedula_usuario VARCHAR(20),
    accion VARCHAR(100) NOT NULL,
    modulo VARCHAR(50),
    descripcion TEXT,
    ip_address VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cedula_usuario) REFERENCES usuarios(cedula_usuario) ON UPDATE CASCADE
);

-- =====================================================
-- TABLAS DE CONFIGURACIÓN Y PERMISOS
-- =====================================================

-- Tabla de configuración del sistema
CREATE TABLE IF NOT EXISTS configuracion (
    id_configuracion SERIAL PRIMARY KEY,
    parametro VARCHAR(50) NOT NULL UNIQUE,
    valor TEXT NOT NULL,
    descripcion TEXT,
    tipo_parametro VARCHAR(20) DEFAULT 'texto',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de permisos
CREATE TABLE IF NOT EXISTS permisos (
    id_permiso SERIAL PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL,
    modulo VARCHAR(50) NOT NULL,
    accion VARCHAR(50) NOT NULL,
    datos_propios BOOLEAN DEFAULT false,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(nombre_rol, modulo, accion)
);

-- Tabla de configuración de permisos
CREATE TABLE IF NOT EXISTS configuracion_permisos (
    id_config_permiso SERIAL PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL,
    nombre_modulo VARCHAR(50) NOT NULL,
    nombre_accion VARCHAR(50) NOT NULL,
    acceso_limitado_propio BOOLEAN DEFAULT false,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(nombre_rol, nombre_modulo, nombre_accion)
);

-- =====================================================
-- TABLAS DE VALIDACIÓN (CATÁLOGOS)
-- =====================================================

-- Tabla de validación de estados de registro
CREATE TABLE IF NOT EXISTS val_estado_registro (
    id_estado_registro SERIAL PRIMARY KEY,
    nombre_estado VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de validación de niveles académicos
CREATE TABLE IF NOT EXISTS val_nivel_academico (
    id_nivel_academico SERIAL PRIMARY KEY,
    nombre_nivel VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de validación de sexos
CREATE TABLE IF NOT EXISTS val_sexo (
    id_sexo SERIAL PRIMARY KEY,
    codigo_sexo CHAR(1) NOT NULL UNIQUE,
    nombre_sexo VARCHAR(20) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de validación de tipos de taller
CREATE TABLE IF NOT EXISTS val_tipo_taller (
    id_tipo_taller SERIAL PRIMARY KEY,
    nombre_tipo VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLA DE SEMESTRES
-- =====================================================

-- Tabla de semestres
CREATE TABLE IF NOT EXISTS semestre (
    id_semestre SERIAL PRIMARY KEY,
    nombre_semestre VARCHAR(50) NOT NULL,
    anio_academico VARCHAR(10),
    fecha_inicio DATE,
    fecha_fin DATE,
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INSERCIÓN DE DATOS INICIALES EN TABLAS DE VALIDACIÓN
-- =====================================================

-- Estados de registro
INSERT INTO val_estado_registro (nombre_estado, descripcion) VALUES 
('Activo', 'Estudiante activo en el sistema'),
('Inactivo', 'Estudiante inactivo temporalmente'),
('Egresado', 'Estudiante que ha completado sus estudios'),
('Retirado', 'Estudiante que se ha retirado permanentemente')
ON CONFLICT (nombre_estado) DO NOTHING;

-- Niveles académicos
INSERT INTO val_nivel_academico (nombre_nivel, descripcion) VALUES 
('Bachiller', 'Nivel de educación media'),
('Técnico', 'Nivel de educación técnica'),
('Profesional', 'Nivel de educación universitaria'),
('Postgrado', 'Nivel de educación de postgrado')
ON CONFLICT (nombre_nivel) DO NOTHING;

-- Sexos
INSERT INTO val_sexo (codigo_sexo, nombre_sexo, descripcion) VALUES 
('M', 'Masculino', 'Género masculino'),
('F', 'Femenino', 'Género femenino'),
('O', 'Otro', 'Otro género')
ON CONFLICT (codigo_sexo) DO NOTHING;

-- Tipos de taller
INSERT INTO val_tipo_taller (nombre_tipo, descripcion) VALUES 
('Regular', 'Taller regular del plan de estudios'),
('Intensivo', 'Taller de duración intensiva'),
('Online', 'Taller modalidad virtual'),
('Presencial', 'Taller modalidad presencial')
ON CONFLICT (nombre_tipo) DO NOTHING;

-- =====================================================
-- COMENTARIOS FINALES
-- =====================================================

COMMENT ON TABLE usuarios IS 'Tabla principal de usuarios del sistema';
COMMENT ON TABLE persona IS 'Datos personales de usuarios';
COMMENT ON TABLE carrera IS 'Carreras académicas ofrecidas';
COMMENT ON TABLE estudiante IS 'Información académica de estudiantes';
COMMENT ON TABLE profesor IS 'Información profesional de profesores';
COMMENT ON TABLE taller IS 'Talleres y cursos de formación';
COMMENT ON TABLE formacion_complementaria IS 'Programas de formación complementaria';
COMMENT ON TABLE inscripcion IS 'Inscripciones a talleres y cursos';
COMMENT ON TABLE evaluacion IS 'Evaluaciones académicas';
COMMENT ON TABLE nota IS 'Calificaciones detalladas';
COMMENT ON TABLE certificado IS 'Certificados emitidos';
COMMENT ON TABLE inscripcion IS 'Inscripciones a talleres y cursos';
COMMENT ON TABLE solicitudes_extemporaneas IS 'Solicitudes extemporáneas de formación';
COMMENT ON TABLE auditoria IS 'Registro de auditoría del sistema';
COMMENT ON TABLE configuracion IS 'Parámetros de configuración';
COMMENT ON TABLE permisos IS 'Permisos del sistema';
COMMENT ON TABLE configuracion_permisos IS 'Configuración dinámica de permisos';
COMMENT ON TABLE val_estado_registro IS 'Catálogo de estados de registro';
COMMENT ON TABLE val_nivel_academico IS 'Catálogo de niveles académicos';
COMMENT ON TABLE val_sexo IS 'Catálogo de sexos';
COMMENT ON TABLE val_tipo_taller IS 'Catálogo de tipos de taller';
COMMENT ON TABLE semestre IS 'Períodos semestrales académicos';

-- =====================================================
-- FIN DEL SCRIPT DE SINCRONIZACIÓN
-- =====================================================
