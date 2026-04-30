# 📁 ESTRUCTURA COMPLETA PARA GITHUB - SICADFOC 2026

## 🗂️ Estructura de Carpetas y Archivos

```
sicadfoc-2026/
├── 📄 Archivos Principales
│   ├── main.py                           # Aplicación principal Streamlit
│   ├── requirements.txt                  # Dependencias Python
│   ├── render.yaml                      # Configuración de Render
│   ├── Procfile                         # Comando de inicio
│   ├── runtime.txt                      # Versión Python 3.11
│   ├── .env.example                     # Plantilla variables de entorno
│   ├── .gitignore                       # Archivos ignorados
│   └── .gitattributes                   # Configuración Git
│
├── 🔧 Configuración y Base de Datos
│   ├── config.py                        # Configuración general
│   ├── config_unificado.py              # Configuración unificada
│   ├── database.py                      # Conexión a base de datos
│   ├── servicio_unificado_optimizado.py # Servicio optimizado
│   ├── limpiar_conexiones.py            # Limpieza de conexiones
│   ├── script_estandarizacion_produccion.sql # Script producción
│   └── sincronizacion_tablas.sql        # Sincronización tablas
│
├── 🎓 Módulos Académicos
│   ├── gestion_estudiantil.py           # Gestión de estudiantes
│   ├── gestion_profesores.py            # Gestión de profesores
│   ├── gestion_carreras.py              # Gestión de carreras
│   ├── gestion_permisos.py              # Gestión de permisos
│   ├── formacion_complementaria.py      # Formación complementaria
│   ├── reportes.py                      # Módulo de reportes
│   └── gestor_certificaciones.py        # Gestor de certificaciones
│
├── 🔐 Seguridad y Autenticación
│   ├── seguridad.py                     # Sistema de autenticación
│   ├── auth_unificado.py                # Autenticación unificada
│   └── database_compatibilidad.py        # Compatibilidad BD
│
├── 🎨 Interfaz y Estilos
│   ├── styles.py                        # Estilos CSS
│   └── assets/                          # Recursos visuales
│       └── (archivos de imágenes, logos, etc.)
│
├── 📊 Reportes y Análisis
│   ├── reportes.py                      # Ya incluido en módulos académicos
│   └── (archivos adicionales de reportes si es necesario)
│
├── 🗄️ Base de Datos y Scripts
│   ├── script_estandarizacion_produccion.sql # Principal
│   ├── sincronizacion_tablas.sql        # Sincronización
│   └── (scripts adicionales si es necesario)
│
├── 🔧 Utilidades y Herramientas
│   ├── debug_streamlit.py               # Debug de Streamlit
│   ├── verificar_conexiones.py          # Verificación de conexiones
│   ├── reiniciar_forzado.bat            # Reinicio forzado (Windows)
│   ├── reiniciar_postgresql.bat         # Reinicio PostgreSQL (Windows)
│   └── verificar_conexiones.bat        # Verificación (Windows)
│
├── 📋 Documentación
│   ├── README.md                         # Documentación principal
│   ├── DEPLOYMENT_GUIDE.md               # Guía de despliegue
│   ├── DEPLOYMENT_CHECKLIST.md           # Checklist de despliegue
│   ├── COMANDOS_DESPLIEGUE.md            # Comandos de despliegue
│   └── GITHUB_STRUCTURE.md               # Esta guía
│
├── 🗂️ Carpetas de Desarrollo y Backup
│   ├── .git/                            # Control de versiones
│   ├── .vscode/                          # Configuración VS Code
│   ├── __pycache__/                      # Cache Python (ignorado por Git)
│   ├── backup_limpieza/                  # Backup de limpieza
│   ├── backup_limpieza_final/           # Backup final
│   └── backups_seguridad/                # Backups de seguridad
│
└── 📁 Media y Archivos Temporales
    ├── media/                           # Archivos multimedia
    └── uploads/                         # Archivos subidos (si aplica)
```

---

## 📋 Archivos Esenciales para Despliegue

### 🔥 Mínimo Indispensable
```
📄 main.py                    # Aplicación principal
📄 requirements.txt            # Dependencias
📄 render.yaml                # Configuración Render
📄 Procfile                   # Comando inicio
📄 runtime.txt                # Versión Python
📄 .env.example               # Variables de entorno
```

### ⚙️ Configuración Completa
```
📄 config.py                  # Configuración general
📄 database.py                # Base de datos
📄 servicio_unificado_optimizado.py  # Servicio BD
📄 seguridad.py               # Autenticación
📄 script_estandarizacion_produccion.sql  # Script BD
```

### 🎓 Módulos Funcionales
```
📄 gestion_estudiantil.py     # Estudiantes
📄 gestion_profesores.py      # Profesores
📄 gestion_carreras.py        # Carreras
📄 gestion_permisos.py        # Permisos
📄 formacion_complementaria.py # Formación complementaria
📄 reportes.py                # Reportes
📄 styles.py                  # Estilos
```

---

## 🚀 Instrucciones para GitHub

### 1. Crear Repositorio
```bash
# 1. Ir a GitHub.com
# 2. Click "New repository"
# 3. Nombre: sicadfoc-2026
# 4. Descripción: SICADFOC 2026 - Sistema Integral de Control Académico
# 5. Público o Privado (según preferencia)
# 6. Inicializar con README.md
# 7. Click "Create repository"
```

### 2. Clonar y Preparar
```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/sicadfoc-2026.git
cd sicadfoc-2026

# Copiar archivos del proyecto (mantener estructura)
# NO copiar carpetas de backup o __pycache__

# Configurar .env
cp .env.example .env
# Editar .env con valores de producción (NO subir a GitHub)
```

### 3. Primer Commit
```bash
# Agregar todos los archivos
git add .

# Primer commit
git commit -m "🚀 Initial deployment setup - SICADFOC 2026

- ✅ Main Streamlit application
- ✅ Render configuration
- ✅ Database setup scripts
- ✅ All academic modules
- ✅ Security and authentication
- ✅ Documentation and guides

Ready for production deployment!"

# Push a GitHub
git push origin main
```

---

## 🔧 Configuración de .gitignore

### Archivos que NO deben subirse a GitHub:
```
# Variables de entorno
.env

# Cache de Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so

# Logs
*.log
logs/

# Base de datos local
*.db
*.sqlite
*.sqlite3

# IDE y editores
.vscode/
.idea/
*.swp
*.swo

# Backup y temporales
backup_limpieza/
backup_limpieza_final/
backups_seguridad/
*.bak
*.tmp

# Sistema operativo
.DS_Store
Thumbs.db

# Render específico
.render/
```

---

## 📦 Archivos de Configuración Detallados

### requirements.txt
```txt
streamlit
psycopg2-binary
python-dotenv
pandas
```

### render.yaml
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
        sync: false
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

### Procfile
```
web: streamlit run main.py --server.port $PORT --server.address 0.0.0.0
```

### runtime.txt
```
python-3.11
```

---

## 🔗 Flujo de Trabajo de Despliegue

### 1. Desarrollo Local
```bash
# Trabajar en local con .env development
APP_ENV=development
DB_HOST=localhost
# ... otras configuraciones locales
```

### 2. Preparación para Producción
```bash
# Actualizar .env.example si es necesario
# Probar todos los módulos
# Ejecutar pruebas de escritura en BD
# Verificar que todo funcione
```

### 3. Push a GitHub
```bash
git add .
git commit -m "🔧 Update: [descripción del cambio]"
git push origin main
```

### 4. Despliegue Automático en Render
- Render detecta cambios automáticamente
- Comienza el build
- Se despliega la nueva versión

---

## 📋 Verificación Final

### ✅ Antes de Push
- [ ] Todos los archivos necesarios están en GitHub
- [ ] .gitignore está configurado correctamente
- [ ] .env.example está actualizado
- [ ] render.yaml está configurado
- [ ] requirements.txt está completo
- [ ] No hay archivos sensibles en el repositorio

### ✅ Después de Despliegue
- [ ] Aplicación responde correctamente
- [ ] Base de datos está conectada
- [ ] Todos los módulos funcionan
- [ ] No hay errores en los logs
- [ ] Health checks están OK

---

## 🎯 Resumen de Arquitectura

### 🏗️ Estructura Modular
- **Principal**: `main.py` - Orquesta toda la aplicación
- **Configuración**: `config.py`, `database.py` - Configuración centralizada
- **Seguridad**: `seguridad.py` - Autenticación y permisos
- **Módulos**: Cada área funcional en su propio archivo
- **Estilos**: `styles.py` - Interfaz consistente

### 🔗 Conexiones
- **Base de Datos**: PostgreSQL con pool de conexiones
- **Autenticación**: Sistema unificado de usuarios
- **Permisos**: Configuración dinámica por rol
- **UI**: Streamlit con estilos personalizados

### 🚀 Optimizaciones
- **Cache**: Conexiones cacheadas
- **Pool**: Gestión eficiente de conexiones
- **Queries**: Optimizadas para producción
- **UI**: Liviana y rápida

---

**🎯 ESTRUCTURA COMPLETA - SISTEMA LISTO PARA GITHUB Y RENDER**
