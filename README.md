# 🎓 SICADFOC 2026 - Sistema de Gestión Académica

## � Configuración de Entorno

### ⚠️ IMPORTANTE: Configuración de Codificación UTF-8

Para evitar errores de codificación en Windows, asegúrese de configurar la variable de entorno:

```bash
# Para Windows (Command Prompt)
set PYTHONUTF8=1

# Para Windows (PowerShell)
$env:PYTHONUTF8=1

# Para Windows (Git Bash)
export PYTHONUTF8=1
```

Alternativamente, puede ejecutar la aplicación con:

```bash
# Windows Command Prompt
set PYTHONUTF8=1 && streamlit run app/main.py

# Windows PowerShell
$env:PYTHONUTF8=1; streamlit run app/main.py
```

**Nota:** El sistema incluye configuración automática de UTF-8 en el código, pero establecer esta variable de entorno garantiza compatibilidad máxima en Windows.

## �📁 Estructura Modular

```
Proyecto_FOC26/
├── app/                          # Aplicación principal
│   ├── main.py                   # Punto de entrada
│   ├── database.py               # Conexión a base de datos
│   ├── ui/                       # Componentes de interfaz
│   │   ├── ui_components.py     # UI modular
│   │   ├── css/
│   │   │   └── diseños_streamlit.css
│   │   └── assets/
│   │       └── iujo-logo.png
│   ├── modules/                  # Módulos funcionales
│   │   ├── formacion_complementaria/
│   │   │   ├── formacion_complementaria_db.py
│   │   │   └── formacion_complementaria_ui.py
│   │   ├── upload_module.py
│   │   └── cloud_sync.py
│   └── config/                   # Configuración
│       ├── production_config.py
│       ├── requirements.txt
│       ├── Procfile
│       └── render.yaml
├── data/                         # Datos y almacenamiento
│   ├── foc26_limpio.db
│   └── storage/
├── tests/                        # Pruebas unitarias
├── docs/                         # Documentación
└── README.md                     # Este archivo
```

## 🚀 Ejecución

### Desarrollo Local
```bash
cd app
streamlit run main.py
```

### Producción (Render)
```bash
# La configuración está en render.yaml
# Los requisitos están en requirements.txt
```

## 📋 Módulos

### 🎨 UI Components
- Interfaz de usuario modular
- Componentes reutilizables
- Diseño responsivo

### 💾 Database
- Conexión a PostgreSQL/SQLite
- Gestión de transacciones
- Modelos de datos

### 📚 Formación Complementaria
- Gestión de cursos y talleres
- Subida de certificados
- Validación de datos

### ☁️ Cloud Sync
- Sincronización con Render
- Gestión de archivos
- Monitoreo de estado

## 🔧 Configuración

### Variables de Entorno
- `DATABASE_URL`: URL de base de datos
- `SECRET_KEY`: Clave secreta de sesión
- `APP_ENVIRONMENT`: ambiente (development/production)

### Base de Datos
- **Desarrollo**: SQLite (foc26_limpio.db)
- **Producción**: PostgreSQL en Render

## 📊 Estado del Proyecto

- ✅ **100% Operativo**
- ✅ **Estructura Modular**
- ✅ **Listo para Pruebas en Nube**
- ✅ **Perfiles Configurados**

## 🎯 Próximos Pasos

1. **Pruebas de Usuario**: Iniciar desde la nube
2. **Creación de Perfiles**: Validar roles y permisos
3. **Monitoreo**: Implementar logging y métricas
4. **Optimización**: Mejorar rendimiento

---

**🎓 IUJO - SICADFOC 2026**
**Versión: 2.0 Modular**
**Estado: Producción Ready**
