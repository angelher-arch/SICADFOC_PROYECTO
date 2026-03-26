# 🚀 INSTRUCCIONES DE GIT PARA DESPLIEGUE EN RENDER
# =================================================================

## 📋 ESTADO ACTUAL DEL PROYECTO

✅ **Archivos de configuración listos:**
- `requirements.txt` - Dependencias actualizadas para producción
- `render.yaml` - Configuración completa de Render
- `.env.example` - Variables de entorno documentadas
- `database.py` - Conexión dinámica con `os.getenv('DATABASE_URL')`
- `Procfile` - Comando de inicio para Streamlit
- `.gitignore` - Archivos sensibles protegidos

## 🔧 PASOS PARA EL DESPLIEGUE

### 1. Inicializar Repositorio Git (si no existe)
```bash
# Verificar si ya hay un repositorio
git status

# Si no existe, inicializar
git init
git config user.name "Tu Nombre"
git config user.email "tu-email@ejemplo.com"
```

### 2. Agregar Archivos y Hacer Commit
```bash
# Agregar todos los archivos
git add .

# Verificar qué se va a subir (debe mostrar los archivos clave)
git status

# Hacer commit inicial
git commit -m "ci: add render deployment configuration and requirements"
```

### 3. Conectar con GitLab
```bash
# Agregar remote de GitLab (reemplazar con tu repo real)
git remote add origin https://gitlab.com/tu-usuario/sicadfoc-2026.git

# Verificar remote configurado
git remote -v
```

### 4. Push a GitLab (Dispara Auto-Deploy)
```bash
# Push inicial (dispara despliegue automático en Render)
git push -u origin main

# Para futuros cambios
git add .
git commit -m "tu mensaje de commit"
git push origin main
```

## ⚙️ CONFIGURACIÓN EN RENDER

### 1. Conectar Cuenta de GitLab
1. Ir a [Render Dashboard](https://dashboard.render.com)
2. Clic en "New +" → "Web Service"
3. Seleccionar "GitLab"
4. Autorizar acceso a tu cuenta de GitLab
5. Seleccionar repositorio `sicadfoc-2026`

### 2. Configurar Variables de Entorno
En el dashboard de Render, agregar estas variables:

```
DATABASE_URL=postgresql://usuario:password@host:port/database
SECRET_KEY=tu-secret-key-generado-aleatoriamente
STREAMLIT_SERVER_PORT=$PORT
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### 3. Base de Datos (Opción A - Render PostgreSQL)
- Render crea automáticamente una base de datos PostgreSQL
- Copiar la URL del dashboard de Render
- Pegar en variable `DATABASE_URL`

### 4. Base de Datos (Opción B - Externa)
- Usar tu propio PostgreSQL
- Configurar URL manualmente en `DATABASE_URL`

## 🌐 VERIFICACIÓN DEL DESPLIEGUE

### URL de la Aplicación
```
https://sicadfoc-app.onrender.com
```

### Health Check
```
https://sicadfoc-app.onrender.com/
```

### Logs y Monitoreo
- Ver logs en: Dashboard de Render → Logs
- Monitorear estado: Dashboard de Render → Services

## 🛠️ SOLUCIÓN DE PROBLEMAS COMUNES

### Error: "Application failed to start"
**Causa:** Problema con el comando de inicio
**Solución:** Verificar `Procfile` y `startCommand` en `render.yaml`

### Error: "Database connection failed"
**Causa:** `DATABASE_URL` incorrecta
**Solución:** Verificar URL en dashboard de Render

### Error: "Module not found"
**Causa:** Dependencia faltante en `requirements.txt`
**Solución:** Agregar dependencia faltante

### Error: "Port already in use"
**Causa:** Configuración incorrecta de puerto
**Solución:** Usar `$PORT` variable de Render

## 📝 COMANDOS ÚTILES

### Ver estado del repositorio
```bash
git status
git log --oneline
git remote -v
```

### Forzar push (si hay problemas)
```bash
git push -f origin main
```

### Ver últimos commits
```bash
git log --oneline -10
```

### Limpiar cache de Git
```bash
git clean -fd
git reset --hard HEAD
```

## 🔄 FLUJO DE TRABAJO RECOMENDADO

### Para cambios futuros:
```bash
# 1. Hacer cambios en el código
# 2. Probar localmente
streamlit run main.py

# 3. Agregar cambios
git add .
git commit -m "feat: agregar nueva funcionalidad"

# 4. Subir (dispara deploy automático)
git push origin main

# 5. Verificar despliegue en dashboard de Render
```

## ⚠️ NOTAS IMPORTANTES

1. **NUNCA subir `.env`** al repositorio (ya está en `.gitignore`)
2. **SIEMPRE probar localmente** antes de hacer push
3. **MONITOREAR logs** en dashboard de Render
4. **PLAN FREE** tiene limitaciones (15 min inactividad)
5. **BACKUPS** automáticos solo en planes pagos

## 📚 DOCUMENTACIÓN ADICIONAL

- [Render Docs](https://render.com/docs)
- [Streamlit Deploy Guide](https://docs.streamlit.io/knowledge-base/tutorials/deploy)
- [GitLab Integration](https://render.com/docs/gitlab)

## 🎯 CHECKLIST FINAL

- [ ] Repositorio Git inicializado
- [ ] Archivos clave presentes
- [ ] Variables de entorno configuradas en Render
- [ ] Base de datos conectada
- [ ] Aplicación accesible en URL
- [ ] Logs sin errores críticos
- [ ] Health check funcionando

================================================================
¡Listo para desplegar! 🚀
