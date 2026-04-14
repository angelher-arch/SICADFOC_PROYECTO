#!/usr/bin/env python3
"""
Script simplificado para configurar base de datos en Railway
Ejecuta tablas básicas y verifica datos de prueba
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DATABASE_URL de Railway
DATABASE_URL = "postgresql://postgres:UbZFWoDDCUyhbSrVhWVOHsmWqJhpjjop@hopper.proxy.rlwy.net:38358/railway"

class RailwayDBSetup:
    """Configuración de base de datos en Railway"""
    
    def __init__(self):
        self.database_url = DATABASE_URL
        self.connection = None
    
    def conectar(self):
        """Conectar a Railway PostgreSQL"""
        try:
            logger.info("Conectando a Railway PostgreSQL...")
            self.connection = psycopg2.connect(
                self.database_url,
                cursor_factory=RealDictCursor,
                sslmode='require'
            )
            logger.info("Conexión exitosa a Railway")
            return True
        except Exception as e:
            logger.error(f"Error conectando a Railway: {e}")
            return False
    
    def desconectar(self):
        """Desconectar de la base de datos"""
        if self.connection and not self.connection.closed:
            self.connection.close()
            logger.info("Desconexión exitosa")
    
    def crear_tablas_basicas(self):
        """Crear tablas básicas sin funciones complejas"""
        sql_statements = [
            # Extensiones
            "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
            
            # Tabla: Persona
            """
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
            """,
            
            # Tabla: Usuario
            """
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
            """,
            
            # Tabla: Estudiante
            """
            CREATE TABLE IF NOT EXISTS estudiante (
                id SERIAL PRIMARY KEY,
                id_usuario INTEGER REFERENCES usuario(id),
                cedula_estudiante VARCHAR(20) UNIQUE,
                carnet_estudiantil VARCHAR(50),
                semestre_actual INTEGER,
                indice_academico DECIMAL(3,2),
                programa_academico VARCHAR(100),
                fecha_ingreso DATE,
                estado VARCHAR(20) DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo', 'Graduado', 'Suspendido')),
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Tabla: Profesor
            """
            CREATE TABLE IF NOT EXISTS profesor (
                id SERIAL PRIMARY KEY,
                id_usuario INTEGER REFERENCES usuario(id),
                cedula_profesor VARCHAR(20) UNIQUE,
                especialidad VARCHAR(100),
                departamento VARCHAR(100),
                categoria VARCHAR(50),
                correo_personal VARCHAR(100),
                telefono_personal VARCHAR(20),
                fecha_contratacion DATE,
                estado VARCHAR(20) DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo', 'Suspendido')),
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Tabla: Taller
            """
            CREATE TABLE IF NOT EXISTS taller (
                id_taller SERIAL PRIMARY KEY,
                codigo VARCHAR(20) UNIQUE NOT NULL,
                nombre_taller VARCHAR(200) NOT NULL,
                descripcion TEXT,
                duracion_horas INTEGER DEFAULT 40,
                cupos_maximos INTEGER DEFAULT 30,
                requisitos TEXT,
                tipo_taller VARCHAR(50),
                nivel_academico VARCHAR(50),
                estado VARCHAR(20) DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo', 'Suspendido')),
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Tabla: Formacion
            """
            CREATE TABLE IF NOT EXISTS formacion (
                id_formacion SERIAL PRIMARY KEY,
                id_taller INTEGER REFERENCES taller(id_taller),
                nombre_cohorte VARCHAR(100),
                descripcion TEXT,
                fecha_inicio DATE,
                fecha_fin DATE,
                cupos_maximos INTEGER,
                cupos_disponibles INTEGER,
                instructor VARCHAR(100),
                costo DECIMAL(10,2),
                estado VARCHAR(20) DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo', 'Finalizado', 'Cancelado')),
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Tabla: Inscripcion
            """
            CREATE TABLE IF NOT EXISTS inscripcion (
                id_inscripcion SERIAL PRIMARY KEY,
                id_usuario INTEGER REFERENCES usuario(id),
                id_formacion INTEGER REFERENCES formacion(id_formacion),
                fecha_inscripcion DATE DEFAULT CURRENT_DATE,
                estado VARCHAR(20) DEFAULT 'Activa' CHECK (estado IN ('Activa', 'Cancelada', 'Completada', 'Retirada')),
                calificacion DECIMAL(3,1),
                certificado_emitido BOOLEAN DEFAULT FALSE,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Tabla: Auditoria
            """
            CREATE TABLE IF NOT EXISTS auditoria (
                id_auditoria SERIAL PRIMARY KEY,
                id_usuario INTEGER REFERENCES usuario(id),
                accion VARCHAR(100),
                tabla_afectada VARCHAR(50),
                registro_id INTEGER,
                valores_anteriores TEXT,
                valores_nuevos TEXT,
                fecha_accion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(50),
                user_agent TEXT
            );
            """
        ]
        
        try:
            with self.connection.cursor() as cursor:
                for i, statement in enumerate(sql_statements):
                    try:
                        cursor.execute(statement)
                        logger.info(f"Tabla {i+1}/{len(sql_statements)} creada exitosamente")
                    except Exception as e:
                        if "already exists" in str(e):
                            logger.info(f"Tabla {i+1} ya existe")
                        else:
                            logger.error(f"Error creando tabla {i+1}: {e}")
                
                self.connection.commit()
                logger.info("Tablas básicas creadas exitosamente")
                return True
                
        except Exception as e:
            logger.error(f"Error creando tablas: {e}")
            self.connection.rollback()
            return False
    
    def verificar_tablas(self):
        """Verificar que las tablas existan"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                tablas = cursor.fetchall()
                
                logger.info("Tablas encontradas:")
                for tabla in tablas:
                    logger.info(f"  - {tabla['table_name']}")
                
                return [tabla['table_name'] for tabla in tablas]
                
        except Exception as e:
            logger.error(f"Error verificando tablas: {e}")
            return []
    
    def contar_registros(self, tabla):
        """Contar registros en una tabla específica"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) as total FROM {tabla}")
                resultado = cursor.fetchone()
                return resultado['total']
        except Exception as e:
            logger.error(f"Error contando registros en {tabla}: {e}")
            return 0
    
    def insertar_datos_prueba_basicos(self):
        """Insertar datos de prueba básicos"""
        try:
            with self.connection.cursor() as cursor:
                # Insertar personas de prueba
                personas = [
                    ("Admin", "Sistema", "ADMIN001", "admin@sicad.foc", "admin@sicad.foc"),
                    ("Juan", "Pérez", "V12345678", "juan.perez@email.com", "juan.perez@email.com"),
                    ("María", "González", "V87654321", "maria.gonzalez@email.com", "maria.gonzalez@email.com"),
                    ("Carlos", "Rodríguez", "V11223344", "carlos.rodriguez@email.com", "carlos.rodriguez@email.com"),
                    ("Ana", "Martínez", "V55667788", "ana.martinez@email.com", "ana.martinez@email.com")
                ]
                
                for nombre, apellido, cedula, email, login in personas:
                    cursor.execute("""
                        INSERT INTO persona (nombre, apellido, cedula, email)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (email) DO NOTHING
                    """, (nombre, apellido, cedula, email))
                
                # Insertar usuarios
                usuarios = [
                    ("ADMIN001", "admin", "admin@sicad.foc", "admin123", "Administrador"),
                    ("V12345678", "juan.perez", "juan.perez@email.com", "juan123", "Profesor"),
                    ("V87654321", "maria.gonzalez", "maria.gonzalez@email.com", "maria123", "Estudiante"),
                    ("V11223344", "carlos.rodriguez", "carlos.rodriguez@email.com", "carlos123", "Profesor"),
                    ("V55667788", "ana.martinez", "ana.martinez@email.com", "ana123", "Estudiante")
                ]
                
                for cedula, login, email, password, rol in usuarios:
                    cursor.execute("""
                        INSERT INTO usuario (cedula_usuario, login_usuario, email, contrasena, rol, id_persona)
                        SELECT %s, %s, %s, %s, %s, id
                        FROM persona WHERE cedula = %s
                        ON CONFLICT (email) DO NOTHING
                    """, (cedula, login, email, password, rol, cedula))
                
                # Insertar estudiantes
                estudiantes = ["V87654321", "V55667788"]
                for cedula in estudiantes:
                    cursor.execute("""
                        INSERT INTO estudiante (cedula_estudiante, id_usuario)
                        SELECT %s, id
                        FROM usuario WHERE cedula_usuario = %s
                        ON CONFLICT (cedula_estudiante) DO NOTHING
                    """, (cedula, cedula))
                
                # Insertar profesores
                profesores = [
                    ("V12345678", "Programación", "Informática", "Titular", "juan.profesor@email.com"),
                    ("V11223344", "Bases de Datos", "Informática", "Asociado", "carlos.profesor@email.com")
                ]
                
                for cedula, especialidad, depto, categoria, correo in profesores:
                    cursor.execute("""
                        INSERT INTO profesor (cedula_profesor, id_usuario, especialidad, departamento, categoria, correo_personal)
                        SELECT %s, id, %s, %s, %s, %s
                        FROM usuario WHERE cedula_usuario = %s
                        ON CONFLICT (cedula_profesor) DO NOTHING
                    """, (cedula, especialidad, depto, categoria, correo, cedula))
                
                # Insertar talleres
                talleres = [
                    ("TAL-001", "Programación Básica", "Curso introductorio de programación", "Presencial", "Básico"),
                    ("TAL-002", "Bases de Datos", "Fundamentos de bases de datos SQL", "Virtual", "Intermedio"),
                    ("TAL-003", "Desarrollo Web", "HTML, CSS y JavaScript", "Presencial", "Básico"),
                    ("TAL-004", "Python Avanzado", "Programación avanzada en Python", "Virtual", "Avanzado"),
                    ("TAL-005", "Machine Learning", "Conceptos básicos de ML", "Presencial", "Avanzado")
                ]
                
                for codigo, nombre, descripcion, tipo, nivel in talleres:
                    cursor.execute("""
                        INSERT INTO taller (codigo, nombre_taller, descripcion, tipo_taller, nivel_academico)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (codigo) DO NOTHING
                    """, (codigo, nombre, descripcion, tipo, nivel))
                
                self.connection.commit()
                logger.info("Datos de prueba insertados exitosamente")
                return True
                
        except Exception as e:
            logger.error(f"Error insertando datos de prueba: {e}")
            self.connection.rollback()
            return False
    
    def verificar_datos_prueba(self):
        """Verificar datos de prueba"""
        try:
            tablas_esperadas = [
                'persona', 'usuario', 'estudiante', 'profesor', 
                'taller', 'formacion', 'inscripcion', 'auditoria'
            ]
            
            logger.info("Verificación de datos de prueba:")
            
            for tabla in tablas_esperadas:
                total = self.contar_registros(tabla)
                if total > 0:
                    logger.info(f"  {tabla}: {total} registros")
                else:
                    logger.warning(f"  {tabla}: 0 registros (vacía)")
            
            # Verificar usuarios específicos
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT u.id_usuario, p.nombre, p.apellido, u.rol, p.cedula
                    FROM usuario u
                    JOIN persona p ON u.id_persona = p.id
                    ORDER BY u.rol, p.nombre
                    LIMIT 10
                """)
                usuarios = cursor.fetchall()
                
                logger.info("Primeros 10 usuarios:")
                for usuario in usuarios:
                    logger.info(f"  - {usuario['nombre']} {usuario['apellido']} ({usuario['rol']}) - Cédula: {usuario['cedula']}")
                
                # Verificar talleres
                cursor.execute("""
                    SELECT nombre_taller, tipo_taller, nivel_academico
                    FROM taller
                    ORDER BY nombre_taller
                    LIMIT 5
                """)
                talleres = cursor.fetchall()
                
                logger.info("Primeros 5 talleres:")
                for taller in talleres:
                    logger.info(f"  - {taller['nombre_taller']} ({taller['tipo_taller']}, {taller['nivel_academico']})")
                
                return True
                
        except Exception as e:
            logger.error(f"Error verificando datos de prueba: {e}")
            return False
    
    def setup_completo(self):
        """Ejecutar configuración completa"""
        logger.info("Iniciando configuración completa de Railway DB...")
        
        # 1. Conectar
        if not self.conectar():
            return False
        
        try:
            # 2. Crear tablas básicas
            logger.info("Paso 1: Creando tablas básicas...")
            if not self.crear_tablas_basicas():
                return False
            
            # 3. Verificar tablas
            logger.info("Paso 2: Verificando tablas creadas...")
            tablas = self.verificar_tablas()
            if not tablas:
                logger.error("No se encontraron tablas")
                return False
            
            # 4. Insertar datos de prueba
            logger.info("Paso 3: Insertando datos de prueba...")
            self.insertar_datos_prueba_basicos()
            
            # 5. Verificar datos de prueba
            logger.info("Paso 4: Verificando datos de prueba...")
            self.verificar_datos_prueba()
            
            logger.info("Configuración completada exitosamente!")
            return True
            
        except Exception as e:
            logger.error(f"Error en configuración: {e}")
            return False
        finally:
            self.desconectar()

def main():
    """Función principal"""
    setup = RailwayDBSetup()
    
    if setup.setup_completo():
        print("Configuración completada exitosamente!")
        print("Base de datos Railway lista para producción.")
    else:
        print("Error en la configuración. Revisar logs.")

if __name__ == "__main__":
    main()
