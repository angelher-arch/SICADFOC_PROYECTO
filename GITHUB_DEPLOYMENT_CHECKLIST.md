# GitHub Deployment Checklist - SICADFOC 2026

## Archivos Necesarios para Despliegue en GitHub

### Archivos Obligatorios (Subir al repositorio)

#### 1. **Aplicación Principal**
- `FOC26.py` - Aplicación Streamlit principal
- `seguridad.py` - Módulo de seguridad y permisos
- `formacion_complementaria.py` - Módulo de formación complementaria
- `transacciones.py` - Módulo de transacciones
- `gestion_estudiantil.py` - Módulo de gestión estudiantil
- `configuracion.py` - Configuración del sistema
- `conexion_postgresql.py` - Conexión dinámica a PostgreSQL
- `ui_estilos.py` - Estilos CSS de la interfaz
- `version.py` - Información de versión

#### 2. **Base de Datos**
- `database/FOC26DB.sql` - Esquema completo de la base de datos

#### 3. **Configuración de Despliegue**
- `requirements.txt` - Dependencias de Python
- `Procfile` - Comando de inicio para Railway
- `runtime.txt` - Versión de Python (python-3.11.7)

#### 4. **Documentación**
- `README.md` - Documentación del proyecto
- `DEPLOY_RAILWAY.md` - Guía de despliegue en Railway

#### 5. **Configuración Git**
- `.gitignore` - Archivos a ignorar
- `.gitattributes` - Configuración de atributos Git

### Archivos Opcionales (Pueden incluirse)

#### Scripts de Configuración
- `setup_railway_simple.py` - Script para configurar BD Railway
- `seed_data.py` - Script de datos de prueba

#### Documentación Adicional
- `DEPLOYMENT_GUIDE.md` - Guía general de despliegue
- `DEPLOYMENT_FILES.md` - Lista de archivos de despliegue

### Archivos a EXCLUIR (NO subir)

#### Archivos de Entorno
- `.env*` - Archivos de variables de entorno
- `__pycache__/` - Caché de Python
- `.venv/` - Entorno virtual
- `*.pyc` - Archivos compilados

#### Scripts de Desarrollo
- `setup_railway_db.py` - Script con errores
- `setup_railway_db_fixed.py` - Script alternativo
- `load_test_data.py` - Script de carga de datos
- `view_seeded_data.sql` - SQL de consulta

#### Archivos Temporales
- `*.log` - Archivos de log
- `debug_admin.py` - Scripts de depuración
- `.DS_Store` - Archivos de macOS
- `Thumbs.db` - Archivos de Windows

---

## Comandos para Preparar Repositorio

### 1. Inicializar Git (si no está hecho)
```bash
git init
```

### 2. Configurar .gitignore
```bash
# Archivos ya existentes
.env*
__pycache__/
*.pyc
.venv/
*.log
debug_admin.py
.DS_Store
Thumbs.db
setup_railway_db*.py
load_test_data.py
view_seeded_data.sql
```

### 3. Agregar archivos obligatorios
```bash
git add FOC26.py seguridad.py formacion_complementaria.py transacciones.py
git add gestion_estudiantil.py configuracion.py conexion_postgresql.py ui_estilos.py version.py
git add database/FOC26DB.sql
git add requirements.txt Procfile runtime.txt
git add README.md DEPLOY_RAILWAY.md
git add .gitignore .gitattributes
```

### 4. Opcional: Agregar scripts útiles
```bash
git add setup_railway_simple.py seed_data.py
git add DEPLOYMENT_GUIDE.md DEPLOYMENT_FILES.md
```

### 5. Commit y Push
```bash
git commit -m "SICADFOC 2026 - Ready for Railway deployment"
git branch -M main
git remote add origin https://github.com/tu-usuario/sicad-foc26.git
git push -u origin main
```

---

## Verificación Final

### Checklist Antes de Push
- [ ] Todos los archivos obligatorios están agregados
- [ ] .gitignore está configurado correctamente
- [ ] requirements.txt incluye todas las dependencias
- [ ] Procfile tiene el comando correcto
- [ ] runtime.txt especifica python-3.11.7
- [ ] No hay credenciales en el código
- [ ] DATABASE_URL está configurada para Railway
- [ ] README.md está actualizado

### Archivos Mínimos Indispensables
```
FOC26.py
seguridad.py
formacion_complementaria.py
transacciones.py
gestion_estudiantil.py
configuracion.py
conexion_postgresql.py
ui_estilos.py
version.py
database/FOC26DB.sql
requirements.txt
Procfile
runtime.txt
README.md
.gitignore
```

---

## Variables de Entorno para Railway

En el panel de Railway, configurar:
- `DATABASE_URL`: postgresql://postgres:UbZFWoDDCUyhbSrVhWVOHsmWqJhpjjop@hopper.proxy.rlwy.net:38358/railway
- `PORT`: 8501

---

**SICADFOC 2026 - Ready for GitHub and Railway Deployment**
