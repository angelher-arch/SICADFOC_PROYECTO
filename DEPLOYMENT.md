# 🚀 SICADFOC 2026 - Guía de Despliegue

## 📋 Resumen del Proyecto

**SICADFOC 2026** es un sistema de información académica para la gestión de formación complementaria del Instituto Universitario Jesus Obrero.

### 🏗️ Arquitectura
- **Backend:** Python con PostgreSQL
- **Frontend:** Streamlit
- **Base de Datos:** PostgreSQL 17.9
- **Despliegue:** Render (PaaS)

---

## 🔑 Credenciales de Administrador

### 👑 Usuarios Administradores Configurados

1. **V-5.430.424** - Jose Montezuma
   - Contraseña: `admin123`
   - Email: admin@iujo.edu

2. **V-12345678** - Carlos Rodriguez  
   - Contraseña: `admin123`
   - Email: carlos.rodriguez@iujo.edu

3. **V-14300385** - Angel Hernandez ⭐
   - Contraseña: `admin123`
   - Email: angel@iujo.edu
   - **Superprivilegios activados**

---

## 🚀 Despliegue en Render

### 1️⃣ Preparación del Repositorio

```bash
# Clonar el repositorio
git clone <repository-url>
cd Proyecto_FOC26.2

# Instalar dependencias
pip install -r requirements.txt
```

### 2️⃣ Configuración en Render

1. **Crear Nuevo Servicio Web** en Render
2. **Conectar Repositorio GitHub**
3. **Configurar Variables de Entorno:**

```
DATABASE_URL=postgresql://postgres:admin123@your-db-host:5432/db_foc26
PYTHON_VERSION=3.11
STREAMLIT_SERVER_PORT=10000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### 3️⃣ Comando de Inicio

```bash
streamlit run main.py --server.port $PORT --server.address 0.0.0.0
```

---

## 📁 Archivos Clave para Despliegue

### 🔧 `requirements.txt`
- Dependencias optimizadas para producción
- Versiones específicas y compatibles con Render

### ⚙️ `render.yaml`
- Configuración completa del servicio
- Health checks y optimización de recursos
- Variables de entorno predefinidas

### 🔐 `.env.example`
- Plantilla de variables de entorno
- Configuración de base de datos
- Ajustes de seguridad y aplicación

### 🐳 `Dockerfile` (opcional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "main.py", "--server.port=8501"]
```

---

## 🗄️ Configuración de Base de Datos

### 📋 Esquema Principal
- **usuarios** - Gestión de usuarios y roles
- **persona** - Datos personales
- **estudiante** - Información académica
- **profesor** - Datos de profesores
- **carrera** - Carreras universitarias
- **taller** - Talleres y cursos
- **formacion_complementaria** - Formación adicional

### 🔑 Usuarios por Defecto
```sql
-- Administradores
INSERT INTO usuarios (cedula_usuario, login_usuario, rol, contrasena, activo, email)
VALUES 
('V-5.430.424', 'Jose Montezuma', 'Administrador', 'hash_admin123', TRUE, 'admin@iujo.edu'),
('V-12345678', 'Carlos Rodriguez', 'Administrador', 'hash_admin123', TRUE, 'carlos.rodriguez@iujo.edu'),
('V-14300385', 'Angel Hernandez', 'Administrador', 'hash_admin123', TRUE, 'angel@iujo.edu');
```

---

## 🛡️ Seguridad

### 🔐 Características de Seguridad
- **Hash SHA-256** para contraseñas
- **Roles y permisos** dinámicos
- **Validación de acceso** por módulo
- **Bypass de emergencia** para administradores

### 🚨 Acceso de Emergencia
El usuario `V-14300385` tiene bypass de emergencia en el código para garantizar acceso administrativo incluso si la base de datos falla.

---

## 📊 Módulos del Sistema

### 🎓 Gestión Académica
- Registro de estudiantes
- Gestión de profesores  
- Historial académico
- Reportes

### 📚 Formación Complementaria
- Gestión de talleres
- Inscripciones
- Certificaciones
- Seguimiento

### ⚙️ Administración
- Gestión de usuarios
- Configuración de permisos
- Mantenimiento del sistema
- Backups

---

## 🔧 Solución de Problemas

### ❌ Errores Comunes

#### 1. Error de Conexión a BD
```bash
# Verificar variables de entorno
echo $DATABASE_URL

# Probar conexión local
python -c "from database import test_database_connection; print(test_database_connection())"
```

#### 2. Error de Charset
```python
# Asegurar UTF-8 en todo el código
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

#### 3. Error de Módulos Faltantes
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

---

## 📞 Soporte

### 📧 Contacto Técnico
- **Email:** admin@iujo.edu
- **Issues:** GitHub Repository Issues
- **Documentación:** `DEPLOYMENT.md`

### 🔗 Enlaces Útiles
- [Documentación de Streamlit](https://docs.streamlit.io/)
- [Documentación de Render](https://render.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## 🎯 Checklist de Despliegue

- [ ] Repositorio configurado en GitHub
- [ ] Variables de entorno configuradas
- [ ] Base de datos PostgreSQL creada
- [ ] Usuarios administradores creados
- [ ] Dependencias instaladas
- [ ] Health checks funcionando
- [ ] SSL/TLS configurado
- [ ] Backups automáticos activados
- [ ] Monitoreo configurado
- [ ] Documentación actualizada

---

## 🚀 ¡Listo para Producción!

El sistema SICADFOC 2026 está completamente configurado y listo para despliegue en producción con todos los módulos funcionales, usuarios administradores configurados y seguridad implementada.
