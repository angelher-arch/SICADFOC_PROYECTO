import os
import random
import datetime
import re

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

import psycopg2
from psycopg2.extras import RealDictCursor


def load_environment():
    if load_dotenv is not None:
        load_dotenv()

    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url

    raise EnvironmentError(
        'La variable de entorno DATABASE_URL no está definida. Este script solo debe ejecutarse contra la base de datos de Railway, no contra la base local.'
    )


def connect_database(dsn):
    return psycopg2.connect(dsn)


def fetch_one(cursor, query, params=None):
    cursor.execute(query, params or ())
    return cursor.fetchone()


def insert_persona(cursor, nombre, apellido, cedula, email, telefono, direccion, fecha_nacimiento, genero):
    existing = fetch_one(cursor, 'SELECT id FROM persona WHERE cedula = %s OR email = %s', (cedula, email))
    if existing:
        return existing['id']

    cursor.execute(
        '''
        INSERT INTO persona (nombre, apellido, cedula, telefono, email, direccion, fecha_nacimiento, genero)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        ''',
        (nombre, apellido, cedula, telefono, email, direccion, fecha_nacimiento, genero)
    )
    return cursor.fetchone()['id']


def insert_usuario(cursor, id_persona, cedula_usuario, login_usuario, email, contrasena, rol):
    existing = fetch_one(cursor, 'SELECT id FROM usuario WHERE cedula_usuario = %s OR login_usuario = %s OR email = %s',
                         (cedula_usuario, login_usuario, email))
    if existing:
        return existing['id']

    cursor.execute(
        '''
        INSERT INTO usuario (id_persona, cedula_usuario, login_usuario, email, contrasena, rol, activo)
        VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        RETURNING id
        ''',
        (id_persona, cedula_usuario, login_usuario, email, contrasena, rol)
    )
    return cursor.fetchone()['id']


def insert_estudiante(cursor, id_persona, id_usuario, codigo_estudiantil, carrera, semestre_actual, estado):
    existing = fetch_one(cursor, 'SELECT id_estudiante FROM estudiante WHERE codigo_estudiantil = %s', (codigo_estudiantil,))
    if existing:
        return existing['id_estudiante']

    cursor.execute(
        '''
        INSERT INTO estudiante (id_persona, id_usuario, codigo_estudiantil, carrera, semestre_actual, estado)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id_estudiante
        ''',
        (id_persona, id_usuario, codigo_estudiantil, carrera, semestre_actual, estado)
    )
    return cursor.fetchone()['id_estudiante']


def insert_profesor(cursor, id_persona, id_usuario, cedula_profesor, correo_personal, codigo_profesor, especialidad, departamento, categoria, estado):
    existing = fetch_one(cursor, 'SELECT id_profesor FROM profesor WHERE cedula_profesor = %s OR codigo_profesor = %s',
                         (cedula_profesor, codigo_profesor))
    if existing:
        return existing['id_profesor']

    cursor.execute(
        '''
        INSERT INTO profesor (id_persona, id_usuario, cedula_profesor, correo_personal, codigo_profesor, especialidad, departamento, categoria, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id_profesor
        ''',
        (id_persona, id_usuario, cedula_profesor, correo_personal, codigo_profesor, especialidad, departamento, categoria, estado)
    )
    return cursor.fetchone()['id_profesor']


def insert_taller(cursor, codigo, nombre_taller, descripcion, duracion_horas, cupos_maximos, requisitos, estado):
    existing = fetch_one(cursor, 'SELECT id_taller FROM taller WHERE codigo = %s OR nombre_taller = %s',
                         (codigo, nombre_taller))
    if existing:
        return existing['id_taller']

    cursor.execute(
        '''
        INSERT INTO taller (codigo, nombre_taller, descripcion, duracion_horas, cupos_maximos, requisitos, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id_taller
        ''',
        (codigo, nombre_taller, descripcion, duracion_horas, cupos_maximos, requisitos, estado)
    )
    return cursor.fetchone()['id_taller']


def generar_cedulas_unicas(cantidad, prefijo='V'):
    cedulas = set()
    while len(cedulas) < cantidad:
        numero = random.randint(10000000, 99999999)
        cedula = f"{prefijo}{numero}"
        cedulas.add(cedula)
    return list(cedulas)


def generar_correo(nombre, apellido, dominio):
    base = f"{nombre[0]}{apellido}".lower()
    base = re.sub(r'[^a-z0-9]', '', base)
    numero = random.randint(1, 99)
    return f"{base}{numero}@{dominio}"


def crear_estudiantes(cursor, cantidad=50):
    nombres = [
        'Ana', 'Carlos', 'María', 'Jorge', 'Luis', 'Andrea', 'Miguel', 'Daniela',
        'Fernando', 'Valentina', 'José', 'Natalia', 'David', 'Sofía', 'Ricardo',
        'Camila', 'Juan', 'Paola', 'Diego', 'Gabriela', 'Alejandro', 'Isabel',
        'Santiago', 'Laura', 'Miguel', 'Fernanda'
    ]
    apellidos = [
        'Hernández', 'González', 'Martínez', 'Rodríguez', 'Pérez', 'López', 'García',
        'Jiménez', 'Gómez', 'Sánchez', 'Ramírez', 'Torres', 'Flores', 'Díaz',
        'Rivas', 'Paredes', 'Suárez', 'Vivas', 'Vargas', 'Duarte'
    ]
    carreras = [
        'Ingeniería de Sistemas', 'Administración', 'Contaduría Pública', 'Derecho',
        'Psicología', 'Comunicación Social', 'Ingeniería Civil', 'Ingeniería Electrónica',
        'Publicidad', 'Educación', 'Arquitectura', 'Medicina', 'Diseño Gráfico',
        'Turismo', 'Economía'
    ]
    estados = ['Activo', 'Inactivo', 'Suspendido']
    generos = ['Masculino', 'Femenino', 'Otro']
    dominios = ['iujo.edu', 'gmail.com', 'hotmail.com', 'yahoo.com']

    cedulas = generar_cedulas_unicas(cantidad)
    for idx in range(cantidad):
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        cedula = cedulas[idx]
        email = f"{nombre.lower()}.{apellido.lower()}{random.randint(10,99)}@{random.choice(dominios)}"
        contrasena = 'Estudiante123'
        carrera = random.choice(carreras)
        semestre = f"{random.randint(1, 10)}"
        estado = random.choices(estados, [0.8, 0.15, 0.05])[0]
        genero = random.choice(generos)
        telefono = f"+58-4{random.randint(10,99)}-{random.randint(1000000,9999999)}"
        direccion = f"Av. {random.choice(['Bolívar', 'Sucre', 'Urdaneta', 'Rojas'])} #{random.randint(1, 200)}-{random.randint(1, 100)}"
        fecha_nacimiento = datetime.date(random.randint(1998, 2006), random.randint(1, 12), random.randint(1, 28))
        codigo_estudiantil = f"EST2026-{idx + 1:03d}"

        id_persona = insert_persona(cursor, nombre, apellido, cedula, email, telefono, direccion, fecha_nacimiento, genero)
        id_usuario = insert_usuario(cursor, id_persona, cedula, email, email, contrasena, 'Estudiante')
        insert_estudiante(cursor, id_persona, id_usuario, codigo_estudiantil, carrera, semestre, estado)


def crear_profesores(cursor, cantidad=50):
    nombres = [
        'Marta', 'Roberto', 'Patricia', 'Andrés', 'Silvia', 'Nelson', 'Mariana',
        'Alberto', 'Liliana', 'Héctor', 'Lorena', 'Gustavo', 'Beatriz', 'Ángel',
        'Yolanda', 'César', 'Claudia', 'Raúl', 'Karina', 'Oscar'
    ]
    apellidos = [
        'Pérez', 'Ruiz', 'Morales', 'Navarro', 'Ramos', 'Cordero', 'Suarez',
        'Perdomo', 'Salas', 'Guerrero', 'Herrera', 'Arias', 'Maldonado', 'Quintero',
        'Mendoza', 'Vega', 'Cruz', 'Rojas', 'Lara', 'Sosa'
    ]
    especialidades = [
        'Matemáticas Aplicadas', 'Programación', 'Gestión de Proyectos', 'Ética Profesional',
        'Contabilidad', 'Comunicación Digital', 'Sociología', 'Estadística', 'Economía',
        'Recursos Humanos', 'Derecho Administrativo', 'Psicología Organizacional'
    ]
    departamentos = [
        'Ingeniería', 'Ciencias Sociales', 'Administración', 'Humanidades',
        'Ciencias Económicas', 'Educación', 'Comunicación'
    ]
    categorias = ['Titular', 'Asociado', 'Adjunto', 'Invitado']
    dominios = ['iujo.edu', 'profesores.iujo.edu', 'gmail.com', 'outlook.com']

    cedulas = generar_cedulas_unicas(cantidad, prefijo='V')
    for idx in range(cantidad):
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        cedula = cedulas[idx]
        email = f"{nombre.lower()}.{apellido.lower()}{random.randint(10,99)}@{random.choice(dominios)}"
        correo_personal = f"{nombre[0].lower()}{apellido.lower()}{random.randint(100,999)}@{random.choice(['gmail.com', 'hotmail.com', 'outlook.com'])}"
        contrasena = 'Profesor123'
        telefono = f"+58-2{random.randint(100,999)}-{random.randint(1000000,9999999)}"
        direccion = f"Calle {random.choice(['El Peñón', 'La Paz', 'La Florida', 'Las Mercedes'])} #{random.randint(10, 200)}"
        fecha_nacimiento = datetime.date(random.randint(1975, 1995), random.randint(1, 12), random.randint(1, 28))
        especialidad = random.choice(especialidades)
        departamento = random.choice(departamentos)
        categoria = random.choice(categorias)
        estado = random.choices(['Activo', 'Inactivo'], [0.9, 0.1])[0]
        codigo_profesor = f"PROF-2026-{idx + 1:03d}"

        id_persona = insert_persona(cursor, nombre, apellido, cedula, email, telefono, direccion, fecha_nacimiento, 'Masculino' if random.random() < 0.5 else 'Femenino')
        id_usuario = insert_usuario(cursor, id_persona, cedula, email, email, contrasena, 'Profesor')
        insert_profesor(cursor, id_persona, id_usuario, cedula, correo_personal, codigo_profesor, especialidad, departamento, categoria, estado)


def crear_talleres(cursor, cantidad=25):
    nombres_talleres = [
        'Introducción a Python', 'Ética Profesional', 'Excel Avanzado', 'Comunicación Efectiva',
        'Gestión del Tiempo', 'Liderazgo y Trabajo en Equipo', 'Desarrollo de Habilidades Blandas',
        'Marketing Digital', 'Seguridad Informática Básica', 'Diseño de Presentaciones',
        'Resolución de Conflictos', 'Negotiación Profesional', 'Redacción Académica',
        'Gestión de Proyectos', 'Finanzas Personales', 'Atención al Cliente',
        'Herramientas Colaborativas', 'Inteligencia Artificial para Principiantes',
        'Creatividad e Innovación', 'Análisis de Datos', 'Planificación Estratégica',
        'TIC en el Aula', 'Desarrollo Sostenible', 'Talento Humano', 'Mindfulness para el Trabajo'
    ]
    descripciones = [
        'Taller práctico diseñado para fortalecer habilidades útiles en el entorno académico y profesional.',
        'Curso interactivo con ejercicios, casos reales y guía paso a paso.',
        'Contenido actualizado con ejemplos aplicables a situaciones reales en empresas y proyectos.',
        'Enfoque en técnicas prácticas para mejorar la productividad y el liderazgo.',
        'Aprende herramientas digitales esenciales para mejorar tu desempeño profesional.'
    ]
    estados = ['Activo', 'Inactivo', 'Suspendido']

    for idx in range(cantidad):
        nombre_taller = nombres_talleres[idx]
        codigo = f"TALLER-{idx + 1:03d}"
        descripcion = random.choice(descripciones)
        duracion_horas = random.choice([20, 24, 30, 32, 40, 48])
        cupos_maximos = random.randint(20, 60)
        requisitos = 'Ninguno' if random.random() < 0.5 else 'Conocimientos básicos del tema.'
        estado = random.choices(estados, [0.85, 0.1, 0.05])[0]

        insert_taller(cursor, codigo, nombre_taller, descripcion, duracion_horas, cupos_maximos, requisitos, estado)


def contar_registros(cursor):
    consultas = [
        ('personas', 'SELECT COUNT(*) AS total FROM persona'),
        ('usuarios', "SELECT COUNT(*) AS total FROM usuario WHERE rol = 'Estudiante' OR rol = 'Profesor' OR rol = 'Administrador'"),
        ('estudiantes', 'SELECT COUNT(*) AS total FROM estudiante'),
        ('profesores', 'SELECT COUNT(*) AS total FROM profesor'),
        ('talleres', 'SELECT COUNT(*) AS total FROM taller'),
        ('usuarios_estudiante', "SELECT COUNT(*) AS total FROM usuario WHERE rol = 'Estudiante'"),
        ('usuarios_profesor', "SELECT COUNT(*) AS total FROM usuario WHERE rol = 'Profesor'")
    ]
    resultados = {}
    for nombre, consulta in consultas:
        cursor.execute(consulta)
        resultados[nombre] = cursor.fetchone()['total']
    return resultados


def main():
    dsn = load_environment()

    print('Conectando a la base de datos usando DATABASE_URL...')
    with connect_database(dsn) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            print('Conexión exitosa.')
            crear_estudiantes(cursor, 50)
            print('50 estudiantes creados o verificados.')
            crear_profesores(cursor, 50)
            print('50 profesores creados o verificados.')
            crear_talleres(cursor, 25)
            print('25 talleres creados o verificados.')
            conn.commit()
            print('Inserciones confirmadas en la base de datos.')
            resultados = contar_registros(cursor)

    print('\nConteo final de tablas:')
    for clave, valor in resultados.items():
        print(f"- {clave}: {valor}")


if __name__ == '__main__':
    import re

    try:
        main()
    except Exception as exc:
        print(f'ERROR: {exc}')
        raise
