# 🎓 SICADFOC 2026 - Sistema Integral de Control Académico

## 📋 Descripción

Sistema académico completo desarrollado con Streamlit para la gestión de estudiantes, profesores, formación complementaria y documentación.

## 🚀 Despliegue

### Render (Producción)
- **URL:** https://sicadfoc-app.onrender.com
- **Repositorio:** https://github.com/tu-usuario/sicadfoc-2026

### Variables de Entorno
```bash
DATABASE_URL=postgresql://user:pass@host:port/database
SECRET_KEY=tu-secret-key-generado-aleatoriamente
STREAMLIT_SERVER_PORT=$PORT
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

## 📁 Estructura del Proyecto

```
├── main.py                    # Aplicación principal
├── database.py                # Conexión y gestión de base de datos
├── ui_components.py           # Componentes de interfaz
├── formacion_complementaria.py # Módulo de formación complementaria
├── upload_module.py           # Sistema de uploads
├── requirements.txt           # Dependencias
├── render.yaml              # Configuración de despliegue
├── Procfile                 # Comando de inicio
├── .gitignore              # Archivos ignorados
├── .env.example            # Variables de entorno ejemplo
├── diseños_streamlit.css    # Estilos CSS
├── iujo-logo.png          # Logo IUJO
├── IUJO-Sede.png          # Imagen sede
└── README.md              # Este archivo
```

## 🛠️ Instalación Local

1. **Clonar el repositorio:**
```bash
git clone https://github.com/tu-usuario/sicadfoc-2026.git
cd sicadfoc-2026
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno:**
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

5. **Ejecutar aplicación:**
```bash
streamlit run main.py
```

## 🔧 Características Principales

### 📊 Módulos Académicos
- **Gestión de Usuarios:** Administración de roles y permisos
- **Gestión de Profesores:** Control de personal docente
- **Gestión de Estudiantes:** Registro y seguimiento
- **Formación Complementaria:** Cursos y certificaciones

### 📁 Sistema de Documentos
- **Carga Individual:** Subida de archivos uno por uno
- **Carga Masiva:** Procesamiento por lotes (CSV/Excel)
- **Validación:** Flujo de aprobación de documentos
- **Almacenamiento:** Dual (BLOB o sistema de archivos)

### 🎨 Interfaz de Usuario
- **Diseño Moderno:** UI limpia y responsiva
- **Navegación Intuitiva:** Sidebar organizado
- **Banner Informativo:** Animación con datos del sistema
- **Roles y Permisos:** Acceso según rol de usuario

## 📚 Tecnologías

- **Frontend:** Streamlit
- **Backend:** Python
- **Base de Datos:** PostgreSQL (Producción) / SQLite (Desarrollo)
- **Despliegue:** Render
- **Control de Versiones:** Git

## 🤝 Contribución

1. Fork del repositorio
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 📞 Contacto

- **Instituto Universitario Jesús Obrero (IUJO)**
- **Año:** 2026
- **Versión:** 2.0.0

---

**Desarrollado con ❤️ para la comunidad educativa de IUJO**
