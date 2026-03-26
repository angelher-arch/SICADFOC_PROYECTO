# 🚀 SICADFOC 2026 - INSTRUCCIONES DEPLOY EN RENDER

## ✅ **ESTADO ACTUAL DEL SISTEMA**

- ✅ **Base de datos optimizada** con seeders IUJO
- ✅ **Registro y login funcionales** sin errores
- ✅ **Carga masiva optimizada** con threading
- ✅ **CSS limpio** y modular
- ✅ **Configuración producción** lista
- ✅ **Archivos de deploy** preparados

## 📋 **PASOS PARA DEPLOY EN RENDER**

### **1. SUBIR CÓDIGO A GITLAB/GITHUB**

```bash
git add .
git commit -m "Deploy SICADFOC 2026 - Production Ready"
git push origin main
```

### **2. CONFIGURAR RENDER**

1. **Crear nuevo Web Service** en [Render](https://render.com)
2. **Conectar repositorio** GitLab/GitHub
3. **Configurar Build**:
   - Runtime: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run main.py --server.port $PORT --server.address 0.0.0.0`

### **3. VARIABLES DE ENTORNO (CRÍTICO)**

Configurar en el panel de Render:

#### **Base de Datos:**
```
DATABASE_URL=postgresql://usuario_real:password_real@host_real:5432/database_real
```

#### **Aplicación:**
```
SECRET_KEY=tu-secret-key-generada-con-python-secrets
APP_ENVIRONMENT=production
STREAMLIT_SERVER_PORT=$PORT
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
```

#### **Correo SMTP:**
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-correo@gmail.com
SMTP_PASSWORD=tu-app-password-16-chars
```

### **4. GENERAR SECRET_KEY**

```python
import secrets
print(secrets.token_urlsafe(32))
```

### **5. CONFIGURAR BASE DE DATOS**

Opción A: **Base de datos externa**
- Usar PostgreSQL externo (recomendado)
- Configurar `DATABASE_URL` con datos reales

Opción B: **Base de datos Render**
- Crear PostgreSQL en Render
- Copiar connection string al `DATABASE_URL`

### **6. EJECUTAR SEEDERS**

Una vez deployado, ejecutar en la terminal de Render:

```bash
python seed_data_iujo.py
```

## 🔧 **ARCHIVOS CLAVE PARA DEPLOY**

- ✅ `requirements.txt` - Dependencias optimizadas
- ✅ `Procfile` - Comando de inicio
- ✅ `render.yaml` - Configuración completa
- ✅ `main.py` - Aplicación optimizada
- ✅ `production_config.py` - Configuración producción
- ✅ `database.py` - Base de datos sincronizada

## 🧪 **TESTS ANTES DE DEPLOY**

```bash
# Test de conexión a base de datos
python test_production_db.py

# Test de configuración
python deploy_render.py
```

## 📊 **CONFIGURACIÓN DE RECURSOS**

### **Plan Free (Recomendado para inicio):**
- RAM: 512MB
- CPU: Shared
- Build: 15min
- Sleep after 15min inactividad

### **Plan Starter (Producción):**
- RAM: 2GB
- CPU: 2 cores
- Build: 30min
- No sleep

## 🚨 **CONFIGURACIÓN POST-DEPLOY**

### **1. Verificar health check:**
```
https://tu-app.onrender.com/
```

### **2. Ejecutar seeders:**
```bash
# En terminal Render
python seed_data_iujo.py
```

### **3. Test de registro:**
- Crear cuenta de prueba
- Verificar login
- Validar carga masiva

## 🔍 **MONITOREO**

### **Logs en Render:**
- Dashboard → Services → Logs
- Buscar errores de conexión
- Verificar startup logs

### **Métricas:**
- Uso de RAM/CPU
- Tiempo de respuesta
- Errores 500

## 🎯 **URL DE PRODUCCIÓN**

Una vez deployado:
```
https://sicadfoc-app.onrender.com
```

## 📞 **SOPORTE**

### **Errores comunes:**
1. **DATABASE_URL inválida** → Verificar formato
2. **SECRET_KEY faltante** → Generar nueva
3. **Build fallido** → Revisar requirements.txt
4. **App no inicia** → Verificar Procfile

### **Comandos de debug:**
```bash
# Ver logs en tiempo real
render logs sicadfoc-app

# Reiniciar servicio
render restart sicadfoc-app
```

## 🎉 **LISTO PARA PRODUCCIÓN**

El sistema está completamente optimizado y listo para deploy en Render con:

- ✅ Base de datos con datos reales IUJO
- ✅ Registro sin errores
- ✅ Login funcional
- ✅ Carga masiva optimizada
- ✅ Configuración producción lista
- ✅ Tests de validación completados

**¡SICADFOC 2026 listo para producción!** 🎓🚀
