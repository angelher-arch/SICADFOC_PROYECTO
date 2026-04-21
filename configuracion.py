#!/usr/bin/env python3
# Módulo de Configuración - Valores Fijos para SICADFOC 2026

# Configuración de Carreras
CARRERAS = [
    "Ingeniería de Sistemas",
    "Ingeniería Civil",
    "Ingeniería Mecánica",
    "Ingeniería Eléctrica",
    "Ingeniería Química",
    "Administración",
    "Contaduría",
    "Economía",
    "Derecho",
    "Psicología",
    "Comunicación Social"
]

# Configuración de Semestres
SEMESTRES = [
    "I Semestre",
    "II Semestre", 
    "III Semestre",
    "IV Semestre",
    "V Semestre",
    "VI Semestre",
    "VII Semestre",
    "VIII Semestre",
    "IX Semestre",
    "X Semestre"
]

# Configuración de Estados de Registro
ESTADOS_REGISTRO = [
    "Activo",
    "Inactivo",
    "Suspendido",
    "Egresado"
]

# Configuración de Géneros
GENEROS = [
    "Masculino",
    "Femenino",
    "Otro"
]

# Configuración de Tipos de Taller
TIPOS_TALLER = [
    "Programación",
    "Base de Datos",
    "Redes",
    "Seguridad Informática",
    "Desarrollo Web",
    "Mantenimiento de Hardware",
    "Ofimática",
    "Diseño Gráfico"
]

# Configuración de Niveles Académicos
NIVELES_ACADEMICOS = [
    "Básico",
    "Intermedio", 
    "Avanzado",
    "Especializado"
]

def get_carreras():
    """Retorna lista de carreras disponibles"""
    return CARRERAS

def get_semestres():
    """Retorna lista de semestres disponibles"""
    return SEMESTRES

def get_estados_registro():
    """Retorna lista de estados de registro"""
    return ESTADOS_REGISTRO

def get_generos():
    """Retorna lista de géneros disponibles"""
    return GENEROS

def get_tipos_taller():
    """Retorna lista de tipos de taller disponibles"""
    return TIPOS_TALLER

def get_niveles_academicos():
    """Retorna lista de niveles académicos disponibles"""
    return NIVELES_ACADEMICOS

def validar_carrera(carrera):
    """Valida si una carrera existe en la configuración"""
    return carrera in CARRERAS

def validar_semestre(semestre):
    """Valida si un semestre existe en la configuración"""
    return semestre in SEMESTRES

def validar_estado_registro(estado):
    """Valida si un estado de registro existe en la configuración"""
    return estado in ESTADOS_REGISTRO

def validar_genero(genero):
    """Valida si un género existe en la configuración"""
    return genero in GENEROS

def validar_tipo_taller(tipo):
    """Valida si un tipo de taller existe en la configuración"""
    return tipo in TIPOS_TALLER

def validar_nivel_academico(nivel):
    """Valida si un nivel académico existe en la configuración"""
    return nivel in NIVELES_ACADEMICOS
