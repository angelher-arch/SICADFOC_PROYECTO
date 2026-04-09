# FOC26 - Sistema de Información de Control Académico de Formación Complementaria

Sistema web desarrollado con Streamlit para la gestión académica del Instituto Universitario Jesús Obrero (IUJO).

## Características

- **Autenticación**: Login con cédula como identificador principal
- **Gestión de Estudiantes**: Registro y administración de estudiantes
- **Formación Complementaria**: Módulos para cursos y talleres
- **Base de Datos**: PostgreSQL con esquema optimizado
- **Interfaz**: Diseño responsivo y profesional

## Configuración

1. **Variables de Entorno** (ver `.env.example`):
   - `DB_NAME`: Nombre de la base de datos
   - `DB_USER`: Usuario de PostgreSQL
   - `DB_PASSWORD`: Contraseña de PostgreSQL
   - `DB_HOST`: Host de la base de datos
   - `DB_PORT`: Puerto de la base de datos
   - `ADMIN_*`: Configuración del usuario administrador

2. **Dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Base de Datos**:
   - Ejecutar `database/FOC26DB.sql` en PostgreSQL
   - Configurar las variables de entorno

## Despliegue en Render

1. **Crear aplicación** en Render (https://render.com)
2. **Configurar variables de entorno** desde `.env.example`
3. **Conectar repositorio** de GitHub
4. **Desplegar automáticamente**

### Variables de Entorno en Render:
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `ADMIN_CEDULA`, `ADMIN_EMAIL`, `ADMIN_LOGIN`, `ADMIN_PASSWORD`, `ADMIN_ROLE`
- `DEBUG_MODE=false`

## Configuración de GitHub

1. **Instalar Git** (si no está instalado):
   ```bash
   # Windows (con winget)
   winget install --id Git.Git -e --source winget
   
   # O descargar desde: https://git-scm.com/download/win
   ```

2. **Configurar Git**:
   ```bash
   git config --global user.name "Tu Nombre"
   git config --global user.email "tu.email@ejemplo.com"
   ```

3. **Inicializar y subir repositorio**:
   ```bash
   cd Proyecto_FOC26.2
   git init
   git add .
   git commit -m "Initial commit - FOC26 Sistema Académico"
   git branch -M main
   git remote add origin https://github.com/tu-usuario/foc26.git
   git push -u origin main
   ```

## Desarrollo Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos local
# Ejecutar database/FOC26DB.sql

# Ejecutar aplicación
streamlit run FOC26.py
```

## Estructura del Proyecto

```
├── FOC26.py                 # Aplicación principal
├── version.py               # Control de versiones
├── configuracion.py         # Configuraciones del sistema
├── transacciones.py         # Lógica de transacciones
├── gestion_estudiantil.py   # Módulo de estudiantes
├── formacion_complementaria.py # Módulo de formación
├── ui_estilos.py           # Estilos CSS
├── database/               # Esquemas de base de datos
├── assets/                 # Recursos estáticos
├── requirements.txt        # Dependencias Python
├── Procfile               # Configuración Render
├── .env.example           # Variables de entorno
├── .env.render            # Configuración Render
└── .gitignore            # Archivos ignorados
```

## Información de Versión

El sistema incluye un módulo de control de versiones (`version.py`) que muestra:
- Versión actual
- Fecha de build
- Plataforma de despliegue
- Información de Git (commit, branch)

Esta información se muestra en el dashboard principal bajo "ℹ️ Información del Sistema".

## Licencia

Instituto Universitario Jesús Obrero - 2026