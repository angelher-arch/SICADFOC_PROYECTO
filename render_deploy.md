# Guía de Despliegue - SICADFOC 2026 en Render

## Configuración de Variables de Entorno en Render

### 1. Variables de Base de Datos
```
DATABASE_URL=postgresql://user:password@host:port/database
```
- **Prioridad 1**: Si existe `DATABASE_URL`, se conecta a Render Cloud
- **Fallback**: Si no existe, usa configuración local

### 2. Variables de Administrador
```
ADMIN_CEDULA=V-00000000
ADMIN_EMAIL=admin@iujo.edu
ADMIN_LOGIN=admin
ADMIN_PASSWORD=tu_contraseña_segura
ADMIN_ROLE=Admin
```

### 3. Variables de Debug (opcional)
```
DEBUG_MODE=False
```

## Pasos de Despliegue

### 1. Preparar el Repositorio
```bash
# Asegurar que requirements.txt esté actualizado
pip install -r requirements.txt

# Verificar estructura del proyecto
ls -la
```

### 2. Configurar Render
1. Crear nuevo servicio web en Render
2. Conectar al repositorio GitHub
3. Configurar variables de entorno
4. Establecer comando de inicio:
   ```
   streamlit run FOC26.py --server.port=$PORT --server.address=0.0.0.0
   ```

### 3. Migración de Datos
```bash
# Ejecutar script de migración
python migracion_render.py
```

## Verificación de Despliegue

### 1. Conexión a Base de Datos
- Verificar logs de conexión
- Confirmar que usa `DATABASE_URL`
- Probar autenticación con cédula

### 2. Funcionalidad Clave
- Login con cédula y contraseña
- Navegación entre módulos
- Consultas a base de datos

## Troubleshooting

### Error de Conexión
```bash
# Verificar DATABASE_URL
echo $DATABASE_URL

# Probar conexión local
python -c "from conexion_postgresql import ConexionPostgreSQL; print(ConexionPostgreSQL().probar_conexion())"
```

### Error de Autenticación
- Verificar que el login use cédula (no email)
- Confirmar que el admin esté creado

### Problemas de UI
- Verificar assets/Logo_IUJO.png
- Confirmar banner "Instituto Universitario Jesús Obrero"

## Estructura de Archivos Crítica

```
FOC26.py                 # Aplicación principal
conexion_postgresql.py   # Gestión de conexión dinámica
requirements.txt         # Dependencias
migracion_render.py     # Script de migración
.env.example            # Plantilla de variables de entorno
assets/Logo_IUJO.png    # Logo institucional
```

## Comandos Útiles

### Local Development
```bash
streamlit run FOC26.py
```

### Testing de Conexión
```bash
python conexion_postgresql.py
```

### Migración de Datos
```bash
python migracion_render.py
```

### Verificar Logs en Render
```bash
# En el dashboard de Render, revisar logs del servicio
# Buscar mensajes de conexión y autenticación
```

## Consideraciones de Seguridad

1. **Contraseñas**: Usar contraseñas seguras en variables de entorno
2. **DATABASE_URL**: No exponer en código fuente
3. **SSL**: La conexión usa SSL por defecto
4. **Autenticación**: Solo por cédula, no email

## Soporte

- Revisar logs de Render para errores específicos
- Verificar configuración de variables de entorno
- Confirmar que la base de datos Render esté activa
- Validar estructura de tablas antes de migrar
