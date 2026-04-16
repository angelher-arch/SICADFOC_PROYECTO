# SICADFOC 2026 - Sistema de Información de Control Académico

**Instituto Universitario Jesús Obrero**

![IUJO Logo](./assets/Logo_IUJO.png)

## Descripción

SICADFOC 2026 es un sistema integral de gestión académica para el control de formación complementaria en el Instituto Universitario Jesús Obrero. Esta plataforma web permite administrar estudiantes, profesores, talleres, inscripciones y generar reportes en tiempo real.

### Características Principales

- **Gestión de Usuarios**: Autenticación segura por cédula y contraseña
- **Módulo de Profesores**: Registro y administración del personal docente
- **Módulo de Estudiantes**: Gestión completa de datos estudiantiles
- **Formación Complementaria**: Administración de talleres y cursos
- **Sistema de Reportes**: Consultas dinámicas y exportación de datos
- **Panel Administrativo**: Control centralizado con roles y permisos

## Tecnologías

- **Frontend**: Streamlit 1.40.1
- **Backend**: Python 3.13.12
- **Base de Datos**: PostgreSQL con psycopg2-binary
- **Servidor**: Gunicorn (producción)
- **Despliegue**: Render Cloud Platform

## Configuración del Entorno

### Variables de Entorno

El sistema soporta dos entornos de base de datos:

#### Producción (Render Cloud)
```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

#### Desarrollo Local (Fallback)
```bash
DB_NAME=FOC26DB
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
```

#### Credenciales de Administrador
```bash
ADMIN_CEDULA=V-00000000
ADMIN_EMAIL=admin@iujo.edu
ADMIN_LOGIN=admin
ADMIN_PASSWORD=tu_contraseña_segura
ADMIN_ROLE=Admin
```

### Archivos de Configuración

- **`.env`**: Variables de entorno (no subir a Git)
- **`runtime.txt`**: Versión de Python (python-3.13.12)
- **`Procfile`**: Comandos de inicio para Render
- **`requirements.txt`**: Dependencias del proyecto

## Instalación y Ejecución

### Desarrollo Local
```bash
# Clonar el repositorio
git clone <repository-url>
cd Proyecto_FOC26.2

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Ejecutar aplicación
streamlit run FOC26.py
```

### Producción en Render
```bash
# Render automáticamente detectará:
# - runtime.txt para versión de Python
# - requirements.txt para dependencias
# - Procfile para comandos de inicio
# - Variables de entorno desde el dashboard
```

## Arquitectura del Sistema

### Estructura del Proyecto
```
Proyecto_FOC26.2/
├── FOC26.py                 # Aplicación principal
├── conexion_postgresql.py    # Gestión de base de datos
├── seguridad.py             # Módulo de autenticación
├── configuracion.py         # Configuraciones del sistema
├── styles.py               # Estilos CSS globales
├── assets/                 # Recursos estáticos
│   └── Logo_IUJO.png
├── requirements.txt         # Dependencias
├── runtime.txt            # Versión de Python
├── Procfile              # Comandos de Render
├── .env.example          # Plantilla de variables
└── .gitignore           # Archivos excluidos de Git
```

### Flujo de Conexión a Base de Datos
```
¿Existe DATABASE_URL?
    ├── SÍ → Conectar a FOC26DBCloud (Render)
    └── NO → Conectar a FOC26DB (Local)
```

## Seguridad

- **Autenticación**: Basada en cédula y contraseña hash
- **SSL**: Conexiones seguras obligatorias en producción
- **Variables de Entorno**: Credenciales nunca en código fuente
- **Control de Acceso**: Roles y permisos por módulo

## Módulos del Sistema

### 1. Dashboard Principal
- Panel de control con información general
- Navegación entre módulos
- Gestión de sesión

### 2. Gestión de Profesores
- Registro de datos personales
- Asignación de talleres
- Control de estado activo/inactivo

### 3. Gestión de Estudiantes
- Inscripción de nuevos estudiantes
- Actualización de datos académicos
- Historial de talleres cursados

### 4. Formación Complementaria
- Creación y gestión de talleres
- Control de cupos disponibles
- Asignación de profesores

### 5. Reportes
- Consultas dinámicas personalizadas
- Exportación a CSV, JSON, Excel
- Estadísticas en tiempo real

## Flujo de Trabajo

1. **Inicio de Sesión**: Cédula y contraseña
2. **Selección de Módulo**: Según rol de usuario
3. **Gestión de Datos**: CRUD en cada módulo
4. **Generación de Reportes**: Consultas y exportaciones

## Mantenimiento y Soporte

### Resolución de Problemas Comunes

#### Error de Conexión
```bash
# Verificar DATABASE_URL
echo $DATABASE_URL

# Probar conexión local
python -c "from conexion_postgresql import ConexionPostgreSQL; print(ConexionPostgreSQL().probar_conexion())"
```

#### Error de Autenticación
- Verificar que el login use cédula (no email)
- Confirmar que el usuario administrador esté creado

#### Problemas de UI
- Verificar assets/Logo_IUJO.png
- Confirmar configuración de estilos

### Actualización del Sistema
```bash
# Actualizar dependencias
pip install -r requirements.txt --upgrade

# Migrar base de datos
python migracion_render.py
```

## Contacto y Soporte

- **Instituto**: Instituto Universitario Jesús Obrero
- **Sistema**: SICADFOC 2026
- **Versión**: 2.0
- **Año**: 2026

## Licencia

Este software es propiedad del Instituto Universitario Jesús Obrero y está destinado para uso interno en la gestión académica de formación complementaria.

---

**Desarrollado con ❤️ para el Instituto Universitario Jesús Obrero**