# 🚨 Comandos de Emergencia Alpine - Limpieza de Cache Git

## 🔄 **Limpieza Completa de Cache Git**

### 📦 **Paso 1: Limpiar Cache de Git**
```bash
# Limpiar todo el cache de Git (archivos rastreados)
git rm -r --cached .

# Limpiar también archivos no rastreados
git clean -fd

# Resetear al último commit
git reset --hard HEAD
```

### 📦 **Paso 2: Agregar Solo Archivos Alpine**
```bash
# Agregar solo los archivos Alpine optimizados
git add Dockerfile
git add requirements.txt
git add main.py
git add database.py
git add seguridad.py
git add styles.py
git add config.py
git add auth_unificado.py
git add formacion_extemporanea.py

# Agregar módulos académicos esenciales
git add gestion_estudiantil.py
git add gestion_profesores.py
git add formacion_complementaria.py
git add inscripciones.py
git add reportes.py
git add gestor_certificaciones.py
git add editor_certificados.py

# Agregar configuración
git add runtime.txt
git add .env.example
git add .gitignore

# Agregar recursos
git add assets/

# Agregar SQL esenciales
git add sincronizacion_tablas.sql
git add actualizar_bd_cohorte.sql
git add crear_tabla_certificados_extemporaneos.sql

# Agregar documentación mínima
git add README.md
```

### 📦 **Paso 3: Commit de Emergencia Alpine**
```bash
git commit -m "🚨 EMERGENCIA ALPINE - Dockerfile de emergencia

🐳 Cambio crítico:
• FROM python:3.11-alpine (evita apt-get exit code: 100)
• apk add --no-cache en lugar de apt-get
• tesseract-ocr tesseract-ocr-data-spa
• postgresql-dev libpq-dev gcc musl-dev
• jpeg-dev zlib-dev para procesamiento

📦 Requirements mínimos:
• Solo librerías esenciales para prueba de vida
• streamlit pandas psycopg2-binary pytesseract pillow
• Sin versiones fijas para máxima compatibilidad

🎯 Objetivo: Prueba de vida del contenedor Alpine
🚀 Listo para despliegue inmediato en Render"
```

### 📦 **Paso 4: Forzar Push a GitHub**
```bash
# Forzar push para sobreescribir versión anterior
git push --force-with-lease origin main

# Si falla, usar fuerza bruta
git push --force origin main
```

## 🚨 **Comando Todo en Uno**

### ⚡ **Ejecución Rápida**
```bash
# ===== COMANDO COMPLETO DE EMERGENCIA ALPINE =====

# 1. Limpieza total
git rm -r --cached . && git clean -fd && git reset --hard HEAD

# 2. Agregar archivos Alpine
git add Dockerfile requirements.txt main.py database.py seguridad.py styles.py config.py auth_unificado.py formacion_extemporanea.py gestion_estudiantil.py gestion_profesores.py formacion_complementaria.py inscripciones.py reportes.py gestor_certificaciones.py editor_certificados.py runtime.txt .env.example .gitignore assets/ sincronizacion_tablas.sql actualizar_bd_cohorte.sql crear_tabla_certificados_extemporaneos.sql README.md

# 3. Commit de emergencia
git commit -m "🚨 EMERGENCIA ALPINE - Dockerfile de emergencia

🐳 Cambio crítico:
• FROM python:3.11-alpine (evita apt-get exit code: 100)
• apk add --no-cache en lugar de apt-get
• tesseract-ocr tesseract-ocr-data-spa
• postgresql-dev libpq-dev gcc musl-dev
• jpeg-dev zlib-dev para procesamiento

📦 Requirements mínimos:
• Solo librerías esenciales para prueba de vida
• streamlit pandas psycopg2-binary pytesseract pillow
• Sin versiones fijas para máxima compatibilidad

🎯 Objetivo: Prueba de vida del contenedor Alpine
🚀 Listo para despliegue inmediato en Render"

# 4. Forzar push
git push --force-with-lease origin main
```

## ✅ **Verificación Post-Despliegue**

### 🔍 **Verificar que se subió Alpine**
```bash
# Verificar que Dockerfile Alpine esté en el repositorio
git show HEAD:Dockerfile | head -5

# Debe mostrar: FROM python:3.11-alpine

# Verificar requirements.txt mínimo
git show HEAD:requirements.txt

# Debe mostrar solo las 7 librerías esenciales
```

### 🚀 **Monitoreo en Render**
```bash
# 1. Activar despliegue automático en Render
# 2. Monitorear construcción (debe usar Alpine ahora)
# 3. Buscar logs: "apk add --no-cache"
# 4. Verificar que no haya "exit code: 100"
# 5. Confirmar que Tesseract se instale con Alpine
```

## 🎯 **Estado de Emergencia**

**🚨 Sistema en modo emergencia Alpine:**
- **Imagen base**: python:3.11-alpine
- **Gestor de paquetes**: apk (no apt-get)
- **Dependencias mínimas**: Solo esenciales
- **Cache limpio**: Sin rastros de versión anterior
- **Forzado**: Push con --force para asegurar actualización

**🚀 Objetivo: Prueba de vida del contenedor Alpine en Render.**
