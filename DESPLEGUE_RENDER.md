# Guía de Despliegue - SICADFOC 2026 en Render

## Overview
Guía completa para desplegar el Sistema Integral de Control Académico de Formación Continua (SICADFOC 2026) en la plataforma Render.

## Requisitos Previos

1. **Cuenta en Render** (https://render.com)
2. **Repositorio en GitHub** con el código del proyecto
3. **Base de datos PostgreSQL** en Render
4. **Python 3.9+** configurado en el proyecto

## Paso 1: Configuración de Base de Datos en Render

### 1.1 Crear Base de Datos PostgreSQL
1. Iniciar sesión en Render
2. Ir a "New" > "PostgreSQL"
3. Configurar:
   - **Nombre**: `sicadfoc26-db`
   - **Plan**: Free (para desarrollo) o pago para producción
   - **Región**: La más cercana a tus usuarios
   - **PostgreSQL Version**: 14+ (recomendado 15)
4. Esperar a que se cree la instancia

### 1.2 Obtener Credenciales de la Base de Datos
Una vez creada la BD, Render mostrará las credenciales:
```
Connection URI: postgresql://username:password@host:port/database
Internal Connection URI: postgresql://username:password@host:port/database
```

## Paso 2: Configuración del Servicio Web

### 2.1 Crear Servicio Web
1. En Render, ir a "New" > "Web Service"
2. Conectar al repositorio de GitHub
3. Configurar los siguientes parámetros:

#### Configuración Básica
- **Name**: `sicadfoc26-app`
- **Root Directory**: `./` (raíz del proyecto)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run main.py --server.port=$PORT --server.address=0.0.0.0`

#### Configuración Avanzada
- **Instance Type**: `Free` (desarrollo) o `Standard` (producción)
- **Health Check Path**: `/`
- **Auto-Deploy**: Activar para despliegues automáticos

### 2.2 Variables de Entorno (CRÍTICO)

En la sección "Environment" del servicio web, agregar las siguientes variables:

#### Variable Principal - Conexión a Base de Datos
```
DATABASE_URL = postgresql://username:password@host:port/database
```
**IMPORTANTE**: Reemplazar con la Connection URI obtenida en el paso 1.2

#### Variables Opcionales
```
ENVIRONMENT = production
DEBUG = false
```

## Paso 3: Verificación de Configuración Dual

El sistema está configurado para detectar automáticamente el entorno:

### Producción (Render) - Prioridad 1
- **Detecta**: `DATABASE_URL` presente
- **Usa**: Conexión externa PostgreSQL
- **SSL**: `sslmode='require'` (obligatorio para Render)
- **Logs**: "DETECTADO ENTORNO DE PRODUCCIÓN (RENDER)"

### Desarrollo Local - Prioridad 2
- **Detecta**: `DATABASE_URL` ausente
- **Usa**: `localhost:5432/db_foc26`
- **SSL**: `sslmode='prefer'` (opcional)
- **Logs**: "DETECTADO ENTORNO LOCAL"

## Paso 4: Archivos de Configuración

### 4.1 requirements.txt (Verificar contenido)
```
streamlit>=1.28.0
psycopg2-binary>=2.9.0
pandas>=1.5.0
pillow>=9.0.0
python-dotenv>=1.0.0
```

### 4.2 .gitignore (Verificar exclusiones)
```
__pycache__/
*.pyc
.env
.streamlit/
backups_seguridad/
*.log
*.sql
*.zip
```

### 4.3 main.py (Verificar configuración)
El archivo debe incluir:
```python
if __name__ == "__main__":
    main()
```

## Paso 5: Despliegue y Verificación

### 5.1 Primer Despliegue
1. Hacer commit y push de los cambios a GitHub
2. Render iniciará el despliegue automáticamente
3. Verificar los logs en el panel de Render

### 5.2 Verificación de Funcionamiento
Una vez desplegado, verificar:

1. **Conexión a Base de Datos**
   - En los logs debe aparecer: "DETECTADO ENTORNO DE PRODUCCIÓN (RENDER)"
   - Debe mostrar la configuración de conexión externa

2. **Funcionalidad Básica**
   - La aplicación debe cargar en la URL proporcionada por Render
   - El login debe funcionar correctamente

3. **Módulos Principales**
   - Registro de usuarios
   - Gestión de estudiantes
   - Gestión de profesores
   - Formación complementaria

## Paso 6: Solución de Problemas Comunes

### 6.1 Error de Conexión a Base de Datos
**Síntoma**: "could not connect to server"
**Solución**:
1. Verificar que `DATABASE_URL` esté correctamente configurada
2. Confirmar que la base de datos esté en estado "Available"
3. Revisar que no haya errores de tipeo en las credenciales

### 6.2 Error de SSL
**Síntoma**: "sslmode requires SSL connection"
**Solución**:
1. Asegurar que `sslmode='require'` esté configurado
2. Verificar que la BD PostgreSQL en Render tenga SSL activado

### 6.3 Error de Importación
**Síntoma**: "ModuleNotFoundError"
**Solución**:
1. Verificar que `requirements.txt` esté completo
2. Revisar que no haya importaciones circulares
3. Limpiar caché de Render: "Manual Deploy" > "Clear Build Cache"

### 6.4 Error de Permiso
**Síntoma**: "permission denied for table"
**Solución**:
1. Verificar que el usuario de BD tenga los permisos necesarios
2. Revisar que las tablas existan en la base de datos

## Paso 7: Mantenimiento y Monitoreo

### 7.1 Logs del Sistema
- **Render Dashboard**: Logs de despliegue y runtime
- **Application Logs**: Logs específicos de la aplicación
- **Database Logs**: Logs de PostgreSQL

### 7.2 Backup Automático
Render realiza backups automáticos de la base de datos. Para backup adicional:
```bash
# Ejecutar script de backup local si es necesario
python backup_sistema.py
```

### 7.3 Monitoreo de Rendimiento
- **Render Metrics**: CPU, memoria, red
- **Database Metrics**: Conexiones, consultas lentas
- **Custom Metrics**: Logs de errores y transacciones

## Paso 8: Configuración de Dominio Personalizado (Opcional)

### 8.1 Configurar Dominio
1. En el servicio web, ir a "Custom Domains"
2. Agregar el dominio personalizado
3. Configurar DNS según instrucciones de Render

### 8.2 SSL Automático
Render proporciona certificados SSL gratuitos automáticamente para dominios personalizados.

## Paso 9: Escalado y Producción

### 9.1 Plan de Producción
Para entorno de producción:
- **Database**: Plan pago con backups automáticos
- **Web Service**: Plan Standard o superior
- **Monitoring**: Configurar alertas y métricas

### 9.2 Configuración de Producción
```
DATABASE_URL = postgresql://user:pass@host:port/db
ENVIRONMENT = production
DEBUG = false
SECRET_KEY = tu-secret-key-aqui
```

## Checklist Final de Despliegue

- [ ] Base de datos PostgreSQL creada en Render
- [ ] DATABASE_URL configurada correctamente
- [ ] requirements.txt actualizado y completo
- [ ] .gitignore configurado para excluir archivos sensibles
- [ ] Código push a GitHub
- [ ] Servicio web creado en Render
- [ ] Variables de entorno configuradas
- [ ] Despliegue exitoso
- [ ] Aplicación funcional en URL de Render
- [ ] Login y módulos principales funcionando
- [ ] Logs sin errores críticos

## Contacto de Soporte

- **Render Documentation**: https://render.com/docs
- **GitHub Issues**: Para problemas específicos del código
- **Database Support**: Para problemas de PostgreSQL en Render

---

**Nota**: Esta guía asume que ya tienes una base de datos funcional con las tablas del SICADFOC 2026 creadas. Si necesitas crear la estructura inicial, ejecuta el script de sincronización proporcionado en el repositorio.
