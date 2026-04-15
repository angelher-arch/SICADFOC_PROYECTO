# 🚀 SICADFOC 2026 - Guía de Despliegue en Railway

## 📋 Lista de Archivos para Despliegue

### ✅ Archivos Obligatorios (Subir al repositorio):
```
FOC26.py                    # Aplicación principal
seguridad.py                 # Módulo de seguridad y permisos
formacion_complementaria.py   # Módulo de formación complementaria
transacciones.py             # Módulo de transacciones
configuracion.py             # Configuración del sistema
conexion_postgresql.py       # Módulo de conexión a BD
gestion_estudiantil.py      # Módulo de gestión estudiantil
ui_estilos.py               # Estilos CSS de la interfaz
version.py                  # Información de versión
requirements.txt             # Dependencias de Python
Procfile                    # Comando de inicio para Railway
runtime.txt                 # Versión de Python
schema_final.sql            # Esquema completo de BD
```

### ❌ Archivos a Ignorar (NO subir):
```
__pycache__/               # Caché de Python
*.pyc                      # Archivos compilados
.env                        # Variables de entorno locales
debug_admin.py             # Scripts de depuración
*.log                       # Archivos de log
venv/                       # Entorno virtual local
.venv/                      # Entorno virtual local
.DS_Store                    # Archivos de macOS
Thumbs.db                    # Archivos de Windows
```

## 🔧 Configuración de Conexión Dinámica

### 📦 Variables de Entorno (Railway):
- `DATABASE_URL`: URL completa de conexión PostgreSQL
- `PORT`: Puerto de la aplicación (por defecto 8501)

### 🔒 Estructura de Conexión Segura:
- Prioridad 1: `DATABASE_URL` (Railway)
- Prioridad 2: Credenciales locales (fallback)
- SSL obligatorio: `sslmode='require'`
- Manejo robusto de excepciones

## 📦 Archivos de Configuración para Railway

### requirements.txt:
```
streamlit==1.28.1
psycopg2-binary==2.9.7
pandas==2.1.4
python-dotenv==1.0.0
gunicorn==21.2.0
```

### Procfile:
```
web: streamlit run FOC26.py --server.port=$PORT --server.address=0.0.0.0
```

### runtime.txt:
```
python-3.11.7
```

## 🚀 Comandos de Despliegue

### 1. Preparar Repositorio:
```bash
git add FOC26.py seguridad.py formacion_complementaria.py transacciones.py configuracion.py conexion_postgresql.py gestion_estudiantil.py ui_estilos.py version.py
git add requirements.txt Procfile runtime.txt schema_final.sql
git commit -m "SICADFOC 2026 - Ready for Railway deployment"
git push origin main
```

### 2. Configurar Railway:
1. Conectar repositorio a Railway
2. Configurar variable `DATABASE_URL`
3. Establecer puerto `PORT=8501`
4. Desplegar automáticamente

### 3. Verificar Despliegue:
- URL: `https://tu-app.railway.app`
- Logs: Dashboard de Railway
- BD: PostgreSQL Panel

## 🔐 Consideraciones de Seguridad

### ✅ Implementado:
- Sin credenciales hardcoded
- Conexión con SSL obligatorio
- Variables de entorno priorizadas
- Manejo seguro de excepciones
- Logs sin información sensible

### 🚨 Importante:
- Nunca subir archivos `.env`
- Usar siempre variables de entorno
- Verificar conexión SSL con Railway
- Monitorear logs de despliegue

## 📊 Checklist Final

- [ ] Todos los archivos obligatorios subidos
- [ ] Archivos sensibles ignorados
- [ ] Variables de entorno configuradas
- [ ] Conexión SSL verificada
- [ ] Aplicación funciona en Railway
- [ ] Logs sin errores críticos

---

**SICADFOC 2026 - Sistema Integral de Control Académico de Formación Complementaria**
**Versión: 1.0.0 | Listo para producción en Railway**
