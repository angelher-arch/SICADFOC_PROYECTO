# 🚀 SICADFOC 2026 - Guía Completa de Despliegue

## 📋 Índice
1. [Archivos Necesarios](#archivos-necesarios)
2. [Configuración de Render](#configuración-de-render)
3. [Base de Datos PostgreSQL](#base-de-datos-postgresql)
4. [Despliegue Paso a Paso](#despliegue-paso-a-paso)
5. [Verificación y Pruebas](#verificación-y-pruebas)
6. [Solución de Problemas](#solución-de-problemas)

---

## 📁 Archivos Necesarios

### Archivos Principales (Requeridos)
```
📄 main.py                    # Aplicación principal Streamlit
📄 requirements.txt            # Dependencias Python
📄 render.yaml                # Configuración de Render
📄 .env.example               # Plantilla de variables de entorno
📄 Procfile                   # Comando de inicio de Render
📄 runtime.txt                # Versión de Python
```

### Archivos de Configuración
```
📄 config.py                  # Configuración general
📄 config_unificado.py        # Configuración unificada
📄 database.py                # Conexión a base de datos
📄 servicio_unificado_optimizado.py  # Servicio optimizado
```

### Módulos del Sistema
```
📄 seguridad.py               # Sistema de autenticación
📄 gestion_estudiantil.py     # Módulo de estudiantes
📄 gestion_profesores.py      # Módulo de profesores
📄 gestion_carreras.py        # Módulo de carreras
📄 gestion_permisos.py        # Gestión de permisos
📄 formacion_complementaria.py # Formación complementaria
📄 reportes.py                # Módulo de reportes
📄 styles.py                  # Estilos CSS
```

### Archivos de Base de Datos
```
📄 script_estandarizacion_produccion.sql  # Estandarización para producción
📄 sincronizacion_tablas.sql              # Sincronización de tablas
```

### Archivos de Documentación
```
📄 README.md                  # Documentación principal
📄 COMANDOS_DESPLIEGUE.md      # Comandos de despliegue
📄 DEPLOYMENT_GUIDE.md        # Esta guía
```

---

## ⚙️ Configuración de Render

### 1. render.yaml (Ya configurado)
```yaml
services:
  - type: web
    name: sicadfoc-2026
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run main.py --server.port $PORT --server.address 0.0.0.0
    healthCheckPath: /
    
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
      - key: PORT
        value: 10000
      - key: DATABASE_URL
        sync: false  # Configurar en dashboard de Render
      - key: STREAMLIT_SERVER_PORT
        value: $PORT
      - key: STREAMLIT_SERVER_ADDRESS
        value: 0.0.0.0
      - key: STREAMLIT_SERVER_HEADLESS
        value: true
    
    autoDeploy: true
    healthCheck:
      path: /
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3
    
    resources:
      memory: 512Mi
      cpu: 0.25
```

### 2. Procfile (Ya configurado)
```
web: streamlit run main.py --server.port $PORT --server.address 0.0.0.0
```

### 3. runtime.txt (Ya configurado)
```
python-3.11
```

---

## 🗄️ Base de Datos PostgreSQL

### Configuración en Render
1. **Crear Base de Datos PostgreSQL**:
   - Ir a Render Dashboard
   - New → PostgreSQL
   - Nombre: `sicadfoc-db`
   - Plan: Free
   - Región: Más cercana a tus usuarios

2. **Variables de Entorno**:
   ```bash
   DATABASE_URL=postgresql://usuario:password@host:port/database
   APP_ENV=production
   ```

### Script de Estandarización
Ejecutar `script_estandarizacion_produccion.sql` en la base de datos de Render:
```sql
-- Este script:
-- 1. Estandariza columna cedula vs cedula_usuario
-- 2. Actualiza foreign keys
-- 3. Crea índices para optimización
-- 4. Configura permisos básicos
-- 5. Verifica integridad de datos
```

---

## 🚀 Despliegue Paso a Paso

### Paso 1: Preparar Repositorio GitHub
```bash
# 1. Crear repositorio en GitHub
# 2. Clonar localmente
git clone https://github.com/tu-usuario/sicadfoc-2026.git
cd sicadfoc-2026

# 3. Copiar archivos del proyecto
# (Todos los archivos listados arriba)

# 4. Configurar .env
cp .env.example .env
# Editar .env con valores de producción

# 5. Subir a GitHub
git add .
git commit -m "Initial deployment setup"
git push origin main
```

### Paso 2: Configurar Render
1. **Conectar GitHub**:
   - Ir a Render Dashboard
   - New → Web Service
   - Connect to GitHub
   - Seleccionar repositorio `sicadfoc-2026`

2. **Configurar Servicio**:
   - Nombre: `sicadfoc-2026`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run main.py --server.port $PORT --server.address 0.0.0.0`

3. **Configurar Variables de Entorno**:
   ```bash
   DATABASE_URL=postgresql://usuario:password@host:port/database
   APP_ENV=production
   PYTHONUNBUFFERED=1
   ```

### Paso 3: Configurar Base de Datos
1. **Crear PostgreSQL**:
   - New → PostgreSQL
   - Nombre: `sicadfoc-db`
   - Plan: Free

2. **Ejecutar Script de Estandarización**:
   - Ir a Database Dashboard
   - Query → New Query
   - Pegar contenido de `script_estandarizacion_produccion.sql`
   - Ejecutar

3. **Conectar Aplicación a Base de Datos**:
   - Ir a servicio web
   - Environment → Add Environment Variable
   - `DATABASE_URL`: Copiar URL de PostgreSQL

### Paso 4: Despliegue Automático
- Render detectará cambios automáticamente
- El despliegue comenzará después del push
- Esperar a que el build termine

---

## ✅ Verificación y Pruebas

### 1. Verificar Despliegue
```bash
# Verificar logs en Render Dashboard
# Verificar health check: https://tu-app.onrender.com/
```

### 2. Pruebas Funcionales
- **Acceso a la aplicación**: https://tu-app.onrender.com/
- **Inicio de sesión**: Con usuarios de prueba
- **Módulos principales**:
  - Gestión Estudiantil
  - Gestión Profesores
  - Gestión Carreras
  - Formación Complementaria

### 3. Pruebas de Base de Datos
```sql
-- Verificar conexión
SELECT COUNT(*) FROM usuarios;

-- Verificar datos de prueba
SELECT * FROM usuarios WHERE rol = 'Administrador' LIMIT 1;
```

---

## 🔧 Solución de Problemas

### Problemas Comunes

#### 1. Error de Conexión a Base de Datos
```bash
# Verificar DATABASE_URL
echo $DATABASE_URL

# Verificar que la base de datos esté activa
# En Render Dashboard → PostgreSQL → Status
```

#### 2. Error de Columnas (cedula vs cedula_usuario)
```sql
-- Ejecutar script de estandarización
-- En Render Database Dashboard
-- Query → New Query → Pegar script_estandarizacion_produccion.sql
```

#### 3. Error de Importación
```bash
# Verificar requirements.txt
cat requirements.txt

# Verificar que todos los archivos estén en el repositorio
git ls-files
```

#### 4. Error de Permiso
```bash
# Verificar variables de entorno
# En Render Dashboard → Web Service → Environment
```

### Logs y Monitoreo
- **Render Dashboard**: Logs en tiempo real
- **Health Checks**: Estado del servicio
- **Métricas**: Uso de CPU y memoria

---

## 📝 Checklist Final

### Antes del Despliegue
- [ ] Todos los archivos necesarios están en GitHub
- [ ] .env.example está configurado
- [ ] render.yaml está configurado
- [ ] requirements.txt está completo
- [ ] Script de base de datos está listo

### Después del Despliegue
- [ ] Aplicación responde correctamente
- [ ] Base de datos está conectada
- [ ] Usuarios pueden iniciar sesión
- [ ] Módulos funcionan correctamente
- [ ] No hay errores en los logs

### Monitoreo Continuo
- [ ] Revisar logs diariamente
- [ ] Verificar métricas de uso
- [ ] Actualizar dependencias cuando sea necesario
- [ ] Mantener copias de seguridad

---

## 🆘 Soporte

### Contacto
- **Documentación**: Este archivo y README.md
- **Logs**: Render Dashboard
- **Issues**: GitHub Issues del repositorio

### Recursos Adicionales
- [Render Documentation](https://render.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**🎯 Listo para producción! Sigue esta guía y tu aplicación SICADFOC 2026 estará desplegada y funcionando en minutos.**
