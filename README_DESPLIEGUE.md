# Guía de Despliegue - SICADFOC

## Despliegue en Render (Producción)

### 1. Configuración de Variables de Entorno

Configure las siguientes variables de entorno en el dashboard de Render:

#### Base de Datos (Opción 1 - URL completa)
```
RENDER_DB_URL=postgresql://usuario:password@host:puerto/database?sslmode=require
```

#### Base de Datos (Opción 2 - Variables individuales)
```
RENDER_DB_HOST=your-render-db-host.com
RENDER_DB_PORT=5432
RENDER_DB_NAME=your_database_name
RENDER_DB_USER=your_username
RENDER_DB_PASSWORD=your_password
```

#### Variables adicionales (opcional)
```
ENVIRONMENT=production
DEBUG=false
```

### 2. Despliegue Automático

1. **Suba el código a GitHub**
   ```bash
   git add .
   git commit -m "Despliegue SICADFOC"
   git push origin main
   ```

2. **Conecte Render con GitHub**
   - Vaya a [Render Dashboard](https://dashboard.render.com)
   - Cree un nuevo "Web Service"
   - Conecte su repositorio de GitHub
   - Configure las variables de entorno

3. **Configure el Build Command**
   ```
   pip install -r requirements.txt
   ```

4. **Configure el Start Command**
   ```
   streamlit run main.py --server.port=$PORT --server.address=0.0.0.0
   ```

### 3. Configuración Local (Desarrollo)

Para desarrollo local, cree un archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
```

Edite el archivo `.env` con sus credenciales locales.

## Características Implementadas

### ✅ Responsive Design
- **layout="wide"**: Aprovecha mejor las pantallas de laptops
- **st.container()**: Contenedores flexibles para móviles
- **use_container_width=True**: Botones adaptables al ancho de pantalla

### ✅ Variables de Entorno
- **os.environ.get()**: Para variables de entorno locales
- **st.secrets**: Para secrets de Streamlit Cloud
- **Múltiples fallbacks**: Conexión robusta a base de datos

### ✅ Botones Optimizados
- **22 botones** con `use_container_width=True`
- **3 contenedores** st.container() para diseño flexible
- **Diseño responsive**: Se adapta a teléfonos y tablets

## Archivos de Configuración

### `.env.example`
Variables de entorno para desarrollo local.

### `.streamlit/secrets.toml.example`
Configuración para despliegue en Streamlit Cloud/Render.

## Verificación de Despliegue

El sistema incluye verificación automática de:
- ✅ Configuración de página responsive
- ✅ Contenedores flexibles
- ✅ Botones adaptables
- ✅ Variables de entorno
- ✅ Conexión a base de datos
- ✅ Sintaxis correcta

## Soporte

Para problemas de despliegue:
1. Verifique las variables de entorno
2. Revise los logs de Render
3. Confirme la conexión a base de datos
4. Valide la sintaxis del código

## Seguridad

- Las contraseñas no están expuestas en el código
- Uso de variables de entorno y secrets
- Conexión SSL requerida para Render
- Validación de entradas de usuario
