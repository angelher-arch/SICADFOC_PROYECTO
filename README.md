# 🎓 SICADFOC 2026 - Sistema de Información Académica

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28.1-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17.9-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Sistema integral de gestión académica para el Instituto Universitario Jesus Obrero, enfocado en la administración de formación complementaria y control académico.

## 🌟 Características Principales

### 👥 Gestión de Usuarios
- **Múltiples roles:** Administrador, Profesor, Estudiante
- **Control de accesos** por módulo y función
- **Autenticación segura** con hash SHA-256
- **Superadministradores** con bypass de emergencia

### 📚 Módulos Académicos
- **Registro de estudiantes** y profesores
- **Gestión de carreras** y semestres
- **Historial académico** completo
- **Índices académicos** y seguimiento

### 🔧 Formación Complementaria
- **Talleres y cursos** especializados
- **Inscripciones** automatizadas
- **Certificaciones** digitales
- **Gestión de horarios** y recursos

### 📊 Reportes y Análisis
- **Reportes dinámicos** por período
- **Estadísticas académicas** en tiempo real
- **Exportación** a múltiples formatos
- **Dashboards** interactivos

## 🚀 Inicio Rápido

### 📋 Prerrequisitos
- Python 3.11+
- PostgreSQL 12+
- Streamlit 1.28+

### 🔧 Instalación Local

```bash
# Clonar el repositorio
git clone https://github.com/your-username/sicadfoc-2026.git
cd sicadfoc-2026

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
# Editar .env con sus credenciales PostgreSQL
cp .env.example .env

# Ejecutar el sistema
streamlit run main.py
```

### 🌐 Acceso al Sistema

Abrir en navegador: `http://localhost:8501`

#### 👑 Credenciales de Administrador
- **Usuario:** V-14300385
- **Contraseña:** admin123
- **Nombre:** Angel Hernandez

Otros administradores disponibles:
- V-5.430.424 / admin123 (Jose Montezuma)
- V-12345678 / admin123 (Carlos Rodriguez)

## 🏗️ Arquitectura

### 📁 Estructura del Proyecto
```
sicadfoc-2026/
├── main.py                    # Aplicación principal Streamlit
├── database.py               # Gestión de base de datos
├── seguridad.py              # Sistema de permisos y seguridad
├── registro_estudiantes.py    # Módulo de estudiantes
├── registro_profesores.py    # Módulo de profesores
├── formacion_complementaria.py # Gestión de talleres
├── gestion_estudiantil.py   # Gestión académica
├── reportes.py               # Sistema de reportes
├── usuarios.py               # Gestión de usuarios
├── sincronizacion_tablas.sql # Esquema de base de datos
├── requirements.txt          # Dependencias Python
├── render.yaml              # Configuración de despliegue
├── .env.example             # Variables de entorno
└── DEPLOYMENT.md            # Guía de despliegue
```

### 🗄️ Base de Datos

**PostgreSQL** con las siguientes tablas principales:
- `usuarios` - Gestión de usuarios y roles
- `persona` - Datos personales
- `estudiante` - Información académica
- `profesor` - Datos de profesores
- `carrera` - Carreras universitarias
- `taller` - Talleres y cursos
- `formacion_complementaria` - Formación adicional

## 🔐 Seguridad

### 🛡️ Características de Seguridad
- **Hash SHA-256** para contraseñas
- **Roles dinámicos** con permisos granulares
- **Validación de acceso** por módulo
- **Bypass de emergencia** para administradores
- **Conexión segura** a base de datos

### 👤 Roles del Sistema
- **👑 Administrador:** Acceso completo a todos los módulos
- **👨‍🏫 Profesor:** Gestión de estudiantes y talleres propios
- **👨‍🎓 Estudiante:** Consulta de datos propios e inscripciones

## 🚀 Despliegue

### ☁️ Render (Recomendado)

1. **Fork** el repositorio
2. **Conectar** con Render Dashboard
3. **Crear** Web Service
4. **Configurar** variables de entorno:
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/db_foc26
   PYTHON_VERSION=3.11
   ```
5. **Desplegar** automáticamente

Ver guía completa en [DEPLOYMENT.md](DEPLOYMENT.md)

### 🐳 Docker

```bash
# Construir imagen
docker build -t sicadfoc-2026 .

# Ejecutar contenedor
docker run -p 8501:8501 sicadfoc-2026
```

## 📊 Módulos del Sistema

### 🎓 Gestión Académica
- ✅ Registro de estudiantes
- ✅ Gestión de profesores
- ✅ Historial académico
- ✅ Control de índices
- ✅ Gestión de carreras

### 📚 Formación Complementaria
- ✅ Creación de talleres
- ✅ Inscripciones automáticas
- ✅ Control de cupos
- ✅ Certificaciones
- ✅ Seguimiento

### ⚙️ Administración
- ✅ Gestión de usuarios
- ✅ Configuración de permisos
- ✅ Mantenimiento del sistema
- ✅ Backups automáticos
- ✅ Reportes de sistema

## 🔧 Desarrollo

### 🛠️ Tecnologías Utilizadas
- **Backend:** Python 3.11
- **Frontend:** Streamlit 1.28.1
- **Base de Datos:** PostgreSQL 17.9
- **ORM:** psycopg2 con RealDictCursor
- **Seguridad:** hashlib SHA-256
- **Despliegue:** Render PaaS

### 📝 Estándares de Código
- **PEP 8** para Python
- **UTF-8** para todo el código
- **Type hints** donde sea aplicable
- **Documentación** en docstrings
- **Testing** con pytest

## 🤝 Contribuir

1. **Fork** el proyecto
2. **Crear** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** cambios (`git commit -m 'Add amazing feature'`)
4. **Push** al branch (`git push origin feature/amazing-feature`)
5. **Abrir** Pull Request

## 📄 Licencia

Este proyecto está bajo licencia MIT - ver archivo [LICENSE](LICENSE) para detalles.

## 📞 Soporte

### 📧 Contacto
- **Email:** admin@iujo.edu
- **Issues:** [GitHub Issues](https://github.com/your-username/sicadfoc-2026/issues)
- **Wiki:** [Documentación Completa](https://github.com/your-username/sicadfoc-2026/wiki)

### 🏢 Institución
**Instituto Universitario Jesus Obrero**
- Dirección: Caracas, Venezuela
- Teléfono: +58-212-1234567
- Email: info@iujo.edu
- Web: www.iujo.edu.ve

---

## 🎯 Versión Actual

**Versión:** 3.0.0  
**Fecha:** 28 de Abril de 2026  
**Estado:** ✅ Producción Lista

---

**⭐ Si este proyecto te ayuda, dale una estrella!**
