-- Script para poblar permisos iniciales RBAC
-- SICADFOC 2026 - Control de Acceso Basado en Roles

-- Insertar permisos para Administrador (acceso total)
INSERT INTO permisos_rol (rol, modulo_nombre, puede_ver, puede_consultar, puede_editar, puede_eliminar, activo)
VALUES
('Administrador', 'Gestión Estudiantil', true, true, true, true, true),
('Administrador', 'Gestión Profesores', true, true, true, true, true),
('Administrador', 'Registro Estudiantes', true, true, true, true, true),
('Administrador', 'Registro Profesores', true, true, true, true, true),
('Administrador', 'Formación Complementaria', true, true, true, true, true),
('Administrador', 'Inscripciones Unificadas', true, true, true, true, true),
('Administrador', 'Gestión Formación Complementaria', true, true, true, true, true),
('Administrador', 'Certificados', true, true, true, true, true),
('Administrador', 'Reportes', true, true, true, true, true),
('Administrador', 'Gestión Usuarios', true, true, true, true, true),
('Administrador', 'Registrar Usuario', true, true, true, true, true),
('Administrador', 'Gestión de Permisos', true, true, true, true, true),
('Administrador', 'Gestión Carreras', true, true, true, true, true)
ON CONFLICT (rol, modulo_nombre) DO NOTHING;

-- Insertar permisos para Profesor
INSERT INTO permisos_rol (rol, modulo_nombre, puede_ver, puede_consultar, puede_editar, puede_eliminar, activo)
VALUES
('Profesor', 'Gestión Estudiantil', true, true, false, false, true),
('Profesor', 'Gestión Profesores', true, true, false, false, true),
('Profesor', 'Formación Complementaria', true, true, true, false, true),
('Profesor', 'Inscripciones Unificadas', true, true, true, false, true),
('Profesor', 'Gestión Formación Complementaria', true, true, true, false, true),
('Profesor', 'Certificados', true, true, true, false, true),
('Profesor', 'Reportes', true, true, false, false, true)
ON CONFLICT (rol, modulo_nombre) DO NOTHING;

-- Insertar permisos para Estudiante
INSERT INTO permisos_rol (rol, modulo_nombre, puede_ver, puede_consultar, puede_editar, puede_eliminar, activo)
VALUES
('Estudiante', 'Gestión Estudiantil', true, false, false, false, true),
('Estudiante', 'Formación Complementaria', true, true, false, false, true),
('Estudiante', 'Inscripciones Unificadas', true, true, false, false, true),
('Estudiante', 'Certificados', true, true, false, false, true),
('Estudiante', 'Reportes', true, false, false, false, true)
ON CONFLICT (rol, modulo_nombre) DO NOTHING;