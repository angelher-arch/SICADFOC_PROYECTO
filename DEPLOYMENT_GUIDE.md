# 🚀 Guía de Despliegue FOC26 - GitHub + Render

## ✅ Estado Actual
- ✅ Repositorio Git inicializado
- ✅ Todos los archivos commited (18 archivos)
- ✅ Rama principal: `main`
- ✅ Configuración de Git completada
- ✅ Archivo .gitattributes agregado
- ✅ Todas las pruebas pasaron

## 📋 Próximos Pasos

### 1. Crear Repositorio en GitHub

1. Ve a https://github.com y crea una cuenta (si no tienes)
2. Haz clic en "New repository"
3. Configura:
   - **Repository name**: `foc26` o `foc26-sistema-academico`
   - **Description**: `Sistema de Información de Control Académico de Formación Complementaria - IUJO`
   - **Visibility**: Public o Private (recomendado Private para producción)
4. **NO marques** "Add a README file" ni ".gitignore" (ya los tenemos)
5. Haz clic en "Create repository"

### 2. Conectar y Subir a GitHub

Ejecuta estos comandos (reemplaza `TU_USUARIO` con tu username de GitHub):

```bash
cd c:\Users\USR\OneDrive\Desktop\Proyecto_FOC26.2

# Conectar con GitHub (reemplaza TU_USUARIO)
& "C:\Program Files\Git\bin\git.exe" remote add origin https://github.com/TU_USUARIO/foc26.git

# Subir el código
& "C:\Program Files\Git\bin\git.exe" push -u origin main
```

### 3. Desplegar en Render

1. Ve a https://render.com y crea una cuenta
2. Haz clic en "New" → "Web Service"
3. Conecta tu cuenta de GitHub
4. Selecciona el repositorio `foc26`
5. Configura el servicio:
   - **Name**: `foc26-sistema-academico`
   - **Environment**: `Python 3`
   - **Build Command**: (dejar vacío, usa requirements.txt)
   - **Start Command**: `streamlit run FOC26.py --server.port $PORT --server.headless true`

### 4. Configurar Variables de Entorno en Render

En la sección "Environment" del servicio, agrega estas variables:

```
# Base de datos PostgreSQL (configurar después de crear DB)
DB_NAME=foc26db
DB_USER=tu_usuario_postgres
DB_PASSWORD=tu_password_segura
DB_HOST=tu_host_render.render.com
DB_PORT=5432

# Configuración Admin
ADMIN_CEDULA=V-00000000
ADMIN_EMAIL=admin@iujo.edu
ADMIN_LOGIN=admin
ADMIN_PASSWORD=tu_password_muy_segura
ADMIN_ROLE=Admin

# Modo producción
DEBUG_MODE=false
```

### 5. Crear Base de Datos PostgreSQL en Render

1. En Render, crea un nuevo "PostgreSQL"
2. Configura:
   - **Name**: `foc26-database`
   - **Database**: `foc26db`
   - **User**: crea un usuario
   - **Password**: genera una contraseña segura
3. Una vez creado, copia la "Internal Database URL" y extrae los valores para las variables de entorno

### 6. Ejecutar Script de Base de Datos

Después de que la DB esté creada, conecta vía pgAdmin o psql y ejecuta:
```sql
-- Ejecutar el contenido de database/FOC26DB.sql
```

### 7. ¡Desplegar!

1. En Render, haz clic en "Create Web Service"
2. Espera a que se complete el build (5-10 minutos)
3. Una vez desplegado, accede a la URL proporcionada por Render
4. El sistema estará listo con:
   - Usuario admin: `admin` / contraseña que configuraste
   - Módulo de versiones mostrando "Render" como plataforma

## 🔍 Verificación Post-Despliegue

1. Accede a la URL de Render
2. Inicia sesión con las credenciales admin
3. Verifica en "ℹ️ Información del Sistema" que muestre:
   - Plataforma: Render
   - Último commit: visible
   - Versión: v1.0.0

## 🆘 Solución de Problemas

### Error de Build en Render:
- Verifica que `requirements.txt` tenga las versiones correctas
- Revisa los logs de build en Render

### Error de Base de Datos:
- Confirma que las variables de entorno sean correctas
- Verifica que la DB esté creada y accesible

### Error de Inicio de Sesión:
- El usuario admin se crea automáticamente al primer inicio
- Verifica las variables ADMIN_* en Render

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs en Render
2. Ejecuta `python test_deployment.py` localmente
3. Verifica la configuración de variables de entorno

¡El sistema FOC26 está listo para producción! 🎉