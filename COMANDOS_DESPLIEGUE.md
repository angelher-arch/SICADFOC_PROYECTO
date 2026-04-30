# COMANDOS PARA DESPLIEGUE EN GITHUB

## PASO 1: INICIAR REPOSITORIO GIT

```bash
git init
git add .
git commit -m "Initial commit - SICADFOC 2026 Sistema Integral"
```

## PASO 2: CREAR REPOSITORIO EN GITHUB

1. Ir a https://github.com
2. Iniciar sesión con tu cuenta
3. Click en "New repository"
4. Nombre: sicadfoc2026
5. Descripción: Sistema Integral de Control Académico y Formación IUJO
6. Seleccionar "Public" o "Private"
7. NO marcar "Initialize with README" (ya tenemos uno)
8. Click en "Create repository"

## PASO 3: CONECTAR REPOSITORIO LOCAL CON GITHUB

```bash
git remote add origin https://github.com/TU_USERNAME/sicadfoc2026.git
git branch -M main
git push -u origin main
```

## PASO 4: DESPLIEGUE EN RENDER.COM

1. Ir a https://render.com
2. Iniciar sesión con GitHub
3. Click en "New +" -> "Web Service"
4. Conectar el repositorio sicadfoc2026
5. Configurar:
   - Name: sicadfoc2026
   - Runtime: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: streamlit run main.py --server.port=10000 --server.address=0.0.0.0
6. Configurar variables de entorno:
   - DATABASE_URL: postgresql://usuario:password@host:puerto/database
   - PYTHONPATH: /opt/render/project/src
7. Click en "Create Web Service"

## COMANDOS COMPLETOS DE DESPLIEGUE

### Copiar y pegar estos comandos en terminal:

```bash
# 1. Inicializar Git
git init
git add .
git commit -m "Initial commit - SICADFOC 2026"

# 2. Conectar con GitHub (reemplazar TU_USERNAME)
git remote add origin https://github.com/TU_USERNAME/sicadfoc2026.git
git branch -M main
git push -u origin main

# 3. Para futuros cambios
git add .
git commit -m "Descripción del cambio"
git push origin main
```

## ARCHIVOS QUE SE SUBIRÁN A GITHUB

Archivos esenciales que se incluirán:
- main.py
- database.py
- seguridad.py
- gestor_certificaciones.py
- formacion_complementaria.py
- styles.py
- requirements.txt
- sincronizacion_tablas.sql
- README.md
- .gitignore
- config.py
- auth_unificado.py
- gestion_estudiantil.py
- gestion_profesores.py
- gestion_carreras.py
- gestion_permisos.py
- reportes.py
- assets/

## ARCHIVOS QUE NO SE SUBIRÁN (POR .GITIGNORE)

Archivos excluidos por seguridad/limpieza:
- __pycache__/
- *.log
- .env
- media/
- backups_seguridad/
- *.db
- *.sqlite
- .vscode/

## VERIFICACIÓN ANTES DE SUBIR

Ejecutar estos comandos para verificar:

```bash
# Verificar archivos que se subirán
git status

# Verificar tamaño del repositorio
du -sh .

# Verificar que no hay datos sensibles
git status --porcelain
```

## DESPLIEGUE COMPLETADO

1. Respaldo creado: RESPALDO_SICADFOC_20260429_230641
2. Archivos esenciales identificados
3. .gitignore configurado
4. requirements.txt actualizado
5. README.md completo
6. Comandos de despliegue generados

El proyecto está listo para desplegarse en GitHub y Render.com.
