# Archivos para Despliegue en GitHub y Render

## Lista Exacta de Archivos para Subir

### Archivos Principales (OBLIGATORIOS)
- `FOC26.py` - Aplicación principal
- `requirements.txt` - Dependencias Python
- `runtime.txt` - Versión Python (python-3.9.16)
- `Procfile` - Configuración de ejecución para Render
- `schema_final.sql` - Esquema completo de base de datos

### Módulos del Sistema
- `configuracion.py` - Configuración de valores fijos
- `formacion_complementaria.py` - Gestión de talleres e inscripciones
- `gestion_estudiantil.py` - Gestión de estudiantes
- `transacciones.py` - Lógica transaccional
- `ui_estilos.py` - Estilos IUJO
- `version.py` - Información de versión

### Configuración y Documentación
- `.env.example` - Plantilla de variables de entorno
- `.env.render` - Configuración específica para Render
- `.env.production` - Configuración para producción
- `.gitignore` - Archivos a ignorar en Git
- `README.md` - Documentación del proyecto
- `DEPLOYMENT_GUIDE.md` - Guía de despliegue
- `DEPLOYMENT_FILES.md` - Este archivo

### Carpetas
- `assets/` - Recursos estáticos (logo IUJO)
- `database/` - Backup de esquema SQL (opcional)

## Archivos que NO DEBEN Subirse
- `__pycache__/` - Cache de Python
- `*.pyc` - Archivos compilados
- `.env` - Variables de entorno locales
- `*.log` - Archivos de log
- `*.tmp` - Archivos temporales
- `*.png`, `*.jpg` - Imágenes excepto en assets/
- `*.pptx` - Presentaciones
- `inspect_db.py` - Scripts de depuración
- `test_*.py` - Archivos de prueba

## Configuración en Render

### Variables de Entorno (Configurar en Render Dashboard)
```
DB_NAME=FOC26DB
DB_USER=postgres
DB_PASSWORD=tu_password_render
DB_HOST=tu_host_render.render.com
DB_PORT=5432
DEBUG_MODE=false
ADMIN_CEDULA=V-00000000
ADMIN_EMAIL=admin@iujo.edu
ADMIN_LOGIN=admin
ADMIN_PASSWORD=tu_password_admin
ADMIN_ROLE=Administrador
```

### Build Command
```
pip install -r requirements.txt
```

### Start Command
```
streamlit run FOC26.py --server.port $PORT --server.address 0.0.0.0
```

## Estructura Final del Repositorio
```
SICADFOC-2026/
|-- FOC26.py
|-- requirements.txt
|-- runtime.txt
|-- Procfile
|-- schema_final.sql
|-- configuracion.py
|-- formacion_complementaria.py
|-- gestion_estudiantil.py
|-- transacciones.py
|-- ui_estilos.py
|-- version.py
|-- .env.example
|-- .env.render
|-- .env.production
|-- .gitignore
|-- README.md
|-- DEPLOYMENT_GUIDE.md
|-- DEPLOYMENT_FILES.md
|-- assets/
|   |-- Logo_IUJO.png
|-- database/
|   |-- FOC26DB.sql
```

## Verificación Antes del Despliegue
1. [ ] Todos los archivos principales están presentes
2. [ ] requirements.txt contiene todas las dependencias
3. [ ] runtime.txt especifica python-3.9.16
4. [ ] Procfile está configurado correctamente
5. [ ] schema_final.sql es completo y actualizado
6. [ ] Variables de entorno configuradas en Render
7. [ ] Base de datos PostgreSQL creada en Render
8. [ ] Esquema aplicado usando schema_final.sql
