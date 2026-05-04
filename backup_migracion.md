# SICADFOC 26 - Protocolo de Backup y Migración a Render

## 🗄️ Comando de Backup (Base de Datos Local DB_FOC26)

### Backup Completo de la Base de Datos Local
```bash
# Desde terminal local (Windows PowerShell o CMD)
pg_dump -h localhost -U postgres -d db_foc26 -f sicadfoc26_backup_$(date +%Y%m%d_%H%M%S).sql

# Opción con compresión (recomendado)
pg_dump -h localhost -U postgres -d db_foc26 -f sicadfoc26_backup_$(date +%Y%m%d_%H%M%S).sql.gz --compress=9

# Con contraseña (si es requerida)
PGPASSWORD=admin123 pg_dump -h localhost -U postgres -d db_foc26 -f sicadfoc26_backup_$(date +%Y%m%d_%H%M%S).sql
```

### Backup Específico de Tablas Críticas
```bash
# Backup de tablas principales
pg_dump -h localhost -U postgres -d db_foc26 -t usuarios -t persona -t estudiante -f sicadfoc26_critical_$(date +%Y%m%d_%H%M%S).sql
```

## 🚀 Instrucciones de Migración a Render (FOC26DB)

### 1. Preparación del Ambiente Render
```bash
# Variables de entorno requeridas en Render
DATABASE_URL=postgresql://usuario:password@host:5432/foc26db?sslmode=require
APP_DEBUG=false
APP_LOG_LEVEL=WARNING
```

### 2. Restauración del Backup en Render
```bash
# Desde el shell de Render
psql $DATABASE_URL < sicadfoc26_backup_YYYYMMDD_HHMMSS.sql

# Si el backup está comprimido
gunzip -c sicadfoc26_backup_YYYYMMDD_HHMMSS.sql.gz | psql $DATABASE_URL
```

### 3. Verificación de Estructura Crítica
```sql
-- Verificar que las tablas principales existan
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('usuarios', 'persona', 'estudiante', 'profesor', 'formacion_complementaria')
ORDER BY table_name;

-- Verificar estructura de formacion_complementaria
\d formacion_complementaria

-- Verificar campos específicos
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'formacion_complementaria' 
AND column_name IN ('codigo_formacion', 'cohorte')
ORDER BY ordinal_position;
```

### 4. Validación de Datos Migrados
```sql
-- Conteo de registros principales
SELECT 
    'usuarios' as tabla, COUNT(*) as registros FROM usuarios
UNION ALL
SELECT 
    'persona' as tabla, COUNT(*) as registros FROM persona
UNION ALL
SELECT 
    'estudiante' as tabla, COUNT(*) as registros FROM estudiante
UNION ALL
SELECT 
    'formacion_complementaria' as tabla, COUNT(*) as registros FROM formacion_complementaria
ORDER BY tabla;
```

## 🔧 Configuración SSL para Render

### Parámetros de Conexión Segura
```
# DATABASE_URL para producción
postgresql://usuario:password@host:5432/foc26db?sslmode=require&sslcert=/path/to/cert.pem&sslkey=/path/to/key.pem

# Configuración en config.py (automática)
if is_production():
    self.config['sslmode'] = 'require'  # Forzar SSL para Render
```

## 📋 Checklist de Despliegue

### ✅ Antes del Despliegue
- [ ] Backup completo de DB_FOC26 local
- [ ] Verificar estructura de tablas críticas
- [ ] Confirmar versión de Python (3.11.8)
- [ ] Validar requirements.txt completo
- [ ] Preparar variables de entorno Render

### ✅ Durante el Despliegue
- [ ] Ejecutar setup.sh en Render
- [ ] Verificar instalación de Tesseract
- [ ] Restaurar backup en FOC26DB
- [ ] Validar conexión SSL
- [ ] Probar autenticación por cédula

### ✅ Después del Despliegue
- [ ] Verificar estilos dinámicos web
- [ ] Probar módulo de Formación Extemporánea
- [ ] Validar generación de reportes
- [ ] Confirmar contraste automático
- [ ] Monitorear logs de errores

## 🚨 Comandos de Emergencia

### Rollback si falla el despliegue
```bash
# Restaurar backup anterior rápidamente
psql $DATABASE_URL < backup_anterior.sql

# Verificar estado del sistema
SELECT 'usuarios', COUNT(*) FROM usuarios
UNION ALL
SELECT 'estudiantes', COUNT(*) FROM estudiante;
```

### Diagnóstico de Conexión
```bash
# Probar conexión a Render
psql $DATABASE_URL -c "SELECT version();"

# Verificar tablas disponibles
psql $DATABASE_URL -c "\dt"
```

## 📞 Soporte Técnico

### Información de Depuración
- **Ambiente Local**: DB_FOC26 (localhost:5432)
- **Ambiente Producción**: FOC26DB (Render + SSL)
- **Versión Python**: 3.11.8
- **Framework**: Streamlit 1.39.0
- **Base de Datos**: PostgreSQL con psycopg2-binary

### Contacto de Emergencia
- **Technology Coordinator**: Reportar cualquier discrepancia en estructura
- **Database Administrator**: Para problemas de conexión SSL
- **Render Support**: Para configuración de despliegue
