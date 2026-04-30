
# SICADFOC 2026 - Sistema Integral de Control Académico y Formación

## Descripción

Sistema integral para la gestión académica y formación complementaria del Instituto Universitario Jesús Obrero (IUJO).

## Características Principales

- **Gestión Estudiantil**: Registro y seguimiento de estudiantes
- **Gestión de Profesores**: Administración del personal docente
- **Formación Complementaria**: Gestión de talleres y certificaciones
- **Control de Acceso**: Sistema de permisos dinámicos por roles
- **Generación de Certificados**: Certificados con códigos únicos
- **Reportes**: Sistema de reportes académicos

## Tecnologías Utilizadas

- **Backend**: Python 3.9+
- **Frontend**: Streamlit
- **Base de Datos**: PostgreSQL
- **ORM**: SQLAlchemy con psycopg2
- **Autenticación**: Sistema propio con SHA-256

## Instalación

### Prerrequisitos

- Python 3.9 o superior
- PostgreSQL 12 o superior
- Git

### Pasos de Instalación

1. **Clonar el repositorio**
   `ash
   git clone https://github.com/usuario/sicadfoc2026.git
   cd sicadfoc2026
   `

2. **Crear entorno virtual**
   `ash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # o
   venv\Scripts\activate  # Windows
   `

3. **Instalar dependencias**
   `ash
   pip install -r requirements.txt
   `

4. **Configurar base de datos**
   `ash
   # Crear base de datos PostgreSQL
   createdb sicadfoc2026
   
   # Ejecutar script de sincronización
   psql -d sicadfoc2026 -f sincronizacion_tablas.sql
   `

5. **Configurar variables de entorno**
   `ash
   cp .env.example .env
   # Editar .env con sus credenciales
   `

6. **Ejecutar la aplicación**
   `ash
   streamlit run main.py
   `

## Configuración

### Variables de Entorno (.env)

`env
# Configuración de Base de Datos
DATABASE_URL=postgresql://usuario:password@localhost:5432/sicadfoc2026

# Configuración de Administrador
ADMIN_CEDULA=V-14300385
ADMIN_EMAIL=admin@iujo.edu.ve
ADMIN_LOGIN=admin
ADMIN_PASSWORD=admin123

# Configuración del Sistema
DEBUG=False
PORT=8501
`

## Usuarios por Defecto

### Administrador Principal
- **Cédula**: 14300385
- **Login**: ahernandez
- **Contraseña**: admin123
- **Rol**: Administrador

### Administrador Secundario
- **Cédula**: V-5430424
- **Login**: jmontezuma
- **Contraseña**: admin123456
- **Rol**: Administrador

## Estructura del Proyecto

`
sicadfoc2026/
|-- main.py                    # Aplicación principal
|-- database.py               # Gestión de base de datos
|-- seguridad.py              # Autenticación y permisos
|-- formacion_complementaria.py # Módulo de formación
|-- gestor_certificaciones.py  # Gestión de certificados
|-- styles.py                 # Estilos de la interfaz
|-- requirements.txt           # Dependencias de Python
|-- sincronizacion_tablas.sql # Estructura de la BD
|-- assets/                   # Recursos estáticos
|-- media/                    # Archivos generados
-- README.md                 # Este archivo
`

## Despliegue

### Render.com

1. Conectar repositorio a Render
2. Configurar variables de entorno
3. Desplegar automáticamente

### Railway

1. Crear nuevo proyecto en Railway
2. Conectar repositorio GitHub
3. Configurar base de datos PostgreSQL
4. Desplegar aplicación

### Heroku

1. Crear app en Heroku
2. Configurar add-on PostgreSQL
3. Establecer variables de entorno
4. Hacer deploy

## Soporte

Para soporte técnico, contactar al equipo de desarrollo del IUJO.

## Licencia

Este proyecto es propiedad del Instituto Universitario Jesús Obrero.
