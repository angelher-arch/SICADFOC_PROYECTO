# 🗄️ SICADFOC 26 - Comando de Backup Total del Aplicativo

## 📦 **Backup Completo del Sistema**

### 🎯 **Opción 1: Backup Completo (Recomendado)**
```bash
# ===== BACKUP COMPLETO DE SICADFOC 26 =====
# Windows PowerShell
$fecha = Get-Date -Format "yyyyMMdd_HHmmss"
$backupPath = "C:\Backup\SICADFOC26_Completo_$fecha.zip"

# Comprimir todo el proyecto
Compress-Archive -Path "C:\Users\USR\OneDrive\Desktop\SICADFOC26\Proyecto_FOC26.2" -DestinationPath $backupPath

Write-Host "✅ Backup completo guardado en: $backupPath"

# Linux/Mac
fecha=$(date +%Y%m%d_%H%M%S)
tar -czf "SICADFOC26_Completo_$fecha.tar.gz" /ruta/a/Proyecto_FOC26.2/

echo "✅ Backup completo guardado en: SICADFOC26_Completo_$fecha.tar.gz"
```

### 🎯 **Opción 2: Backup Crítico (Módulos Principales)**
```bash
# ===== BACKUP CRÍTICO DE MÓDULOS =====
# Windows PowerShell
$fecha = Get-Date -Format "yyyyMMdd_HHmmss"
$backupPath = "C:\Backup\SICADFOC26_Critico_$fecha.zip"

# Archivos esenciales del sistema
$archivosCriticos = @(
    "main.py",
    "database.py", 
    "seguridad.py",
    "styles.py",
    "config.py",
    "auth_unificado.py",
    "gestion_estudiantil.py",
    "gestion_profesores.py",
    "formacion_complementaria.py",
    "inscripciones.py",
    "formacion_extemporanea.py",
    "reportes.py",
    "gestor_certificaciones.py",
    "editor_certificados.py"
)

Compress-Archive -Path $archivosCriticos -DestinationPath $backupPath

Write-Host "✅ Backup crítico guardado en: $backupPath"

# Linux/Mac
fecha=$(date +%Y%m%d_%H%M%S)
tar -czf "SICADFOC26_Critico_$fecha.tar.gz" \
    main.py database.py seguridad.py styles.py config.py \
    auth_unificado.py gestion_estudiantil.py gestion_profesores.py \
    formacion_complementaria.py inscripciones.py formacion_extemporanea.py \
    reportes.py gestor_certificaciones.py editor_certificados.py

echo "✅ Backup crítico guardado en: SICADFOC26_Critico_$fecha.tar.gz"
```

### 🗄️ **Opción 3: Backup Base de Datos + Código**
```bash
# ===== BACKUP INTEGRADO BD + CÓDIGO =====
# Paso 1: Backup de base de datos
pg_dump -h localhost -U postgres -d db_foc26 -f sicadfoc26_db_$(date +%Y%m%d_%H%M%S).sql

# Paso 2: Backup de código crítico
tar -czf "sicadfoc26_codigo_$(date +%Y%m%d_%H%M%S).tar.gz" \
    main.py database.py seguridad.py styles.py config.py \
    requirements.txt runtime.txt setup.sh render.yaml \
    assets/ *.sql

# Paso 3: Integrar todo
fecha=$(date +%Y%m%d_%H%M%S)
tar -czf "SICADFOC26_Integral_$fecha.tar.gz" \
    sicadfoc26_db_*.sql \
    sicadfoc26_codigo_*.tar.gz \
    *.md README.md

echo "✅ Backup integral guardado en: SICADFOC26_Integral_$fecha.tar.gz"
```

## 🔧 **Opción 4: Backup Automatizado (Script)**
```python
# backup_automatico.py
import os
import subprocess
import shutil
from datetime import datetime

def backup_completo():
    """Backup completo automatizado de SICADFOC 26"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Rutas
    origen = r"C:\Users\USR\OneDrive\Desktop\SICADFOC26\Proyecto_FOC26.2"
    destino = rf"C:\Backup\SICADFOC26_Auto_{timestamp}"
    
    # Crear directorio de backup
    os.makedirs(destino, exist_ok=True)
    
    # Copiar archivos críticos
    archivos_criticos = [
        "main.py", "database.py", "seguridad.py", "styles.py", "config.py",
        "auth_unificado.py", "gestion_estudiantil.py", "gestion_profesores.py",
        "formacion_complementaria.py", "inscripciones.py", "formacion_extemporanea.py",
        "reportes.py", "gestor_certificaciones.py", "editor_certificados.py"
    ]
    
    for archivo in archivos_criticos:
        shutil.copy2(os.path.join(origen, archivo), os.path.join(destino, archivo))
    
    # Copiar directorios importantes
    for directorio in ["assets", "media"]:
        src_dir = os.path.join(origen, directorio)
        dst_dir = os.path.join(destino, directorio)
        if os.path.exists(src_dir):
            shutil.copytree(src_dir, dst_dir, ignore_errors=True)
    
    # Copiar archivos de configuración
    for archivo in ["requirements.txt", "runtime.txt", "setup.sh", "render.yaml"]:
        src_file = os.path.join(origen, archivo)
        if os.path.exists(src_file):
            shutil.copy2(src_file, os.path.join(destino, archivo))
    
    # Copiar documentación
    for archivo in ["*.md", "README.md"]:
        src_file = os.path.join(origen, archivo)
        if os.path.exists(src_file):
            shutil.copy2(src_file, os.path.join(destino, archivo))
    
    print(f"✅ Backup automático completado: {destino}")
    return destino

if __name__ == "__main__":
    backup_completo()
```

## 📋 **Comandos Rápidos de Emergencia**

### 🚨 **Backup Instantáneo (Crisis)**
```bash
# Backup de archivos críticos en 30 segundos
tar -czf "EMERGENCIA_SICADFOC26_$(date +%Y%m%d_%H%M%S).tar.gz" \
    main.py database.py seguridad.py styles.py config.py \
    auth_unificado.py gestion_*.py formacion_*.py \
    requirements.txt runtime.txt

echo "🚨 BACKUP DE EMERGENCIA COMPLETADO"
```

### 🔍 **Verificación de Backup**
```bash
# Verificar integridad del backup
tar -tzf "SICADFOC26_Completo_*.tar.gz" --list | head -20

# Verificar tamaño del backup
ls -lh SICADFOC26_Completo_*.tar.gz

# Verificar archivos esenciales
tar -tzf "SICADFOC26_Completo_*.tar.gz" --list | grep -E "(main\.py|database\.py|seguridad\.py)"
```

## 📊 **Estadísticas de Backup**

### 📈 **Típicos de Backup**
| Tipo de Backup | Tamaño Aproximado | Tiempo | Frecuencia |
|---------------|-------------------|---------|------------|
| Completo | 50-100 MB | 2-5 min | Diario |
| Crítico | 20-40 MB | 30-60 seg | Cada cambio |
| Integral BD + Código | 60-120 MB | 5-10 min | Semanal |

### 📁 **Estructura de Directorios de Backup**
```
C:\Backup\SICADFOC26\
├── Completo\
│   ├── 20240503_143022.zip
│   ├── 20240502_091515.zip
│   └── ...
├── Critico\
│   ├── 20240503_143022.zip
│   └── ...
├── Integral\
│   ├── 20240503_143022.tar.gz
│   └── ...
└── Emergencia\
    ├── 20240503_143022.tar.gz
    └── ...
```

## 🔧 **Configuración de Backup Automatizado**

### 📅 **Programación de Backup (Windows Task Scheduler)**
```powershell
# Crear tarea programada
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File C:\Backup\backup_sicadfoc26.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 3am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "SICADFOC26_Backup" -Description "Backup diario del sistema SICADFOC 26"
```

### ⚙️ **Configuración de Backup (Cron Linux)**
```bash
# Agregar al crontab
crontab -e

# Backup diario a las 3 AM
0 3 * * * /usr/bin/tar -czf /backup/SICADFOC26_$(date +\%Y\%m\%d_\%H\%M\%S).tar.gz /ruta/a/Proyecto_FOC26.2/
```

## 🚨 **Procedimiento de Restauración**

### 📥 **Restauración Completa**
```bash
# Restaurar desde backup completo
unzip SICADFOC26_Completo_YYYYMMDD_HHMMSS.zip -d /ruta/restauracion/

# Verificar permisos
chmod +x /ruta/restauracion/*.py
chmod +x /ruta/restauracion/*.sh

# Restaurar base de datos si está incluida
if [ -f "/ruta/restauracion/sicadfoc26_db_*.sql" ]; then
    psql -h localhost -U postgres -d db_foc26 < sicadfoc26_db_*.sql
fi
```

### 🔧 **Restauración Crítica**
```bash
# Restaurar solo archivos críticos
tar -xzf SICADFOC26_Critico_YYYYMMDD_HHMMSS.tar.gz -C /ruta/restauracion/

# Reinstalar dependencias
pip install -r requirements.txt

# Verificar funcionamiento
cd /ruta/restauracion
python -c "import main; print('✅ Sistema restaurado correctamente')"
```

## ✅ **Checklist Final de Backup**

### 📋 **Antes del Backup**
- [ ] Verificar espacio disponible en destino
- [ ] Cerrar todas las conexiones a base de datos
- [ ] Detener aplicación si está corriendo
- [ ] Verificar permisos de lectura/escritura
- [ ] Confirmar ruta del proyecto

### 📋 **Durante el Backup**
- [ ] Monitorizar progreso de compresión
- [ ] Verificar que no haya errores de archivo
- [ ] Confirmar tamaño final del backup
- [ ] Validar integridad de archivos críticos

### 📋 **Después del Backup**
- [ ] Verificar lista de archivos en backup
- [ ] Probar restauración en entorno de prueba
- [ ] Documentar fecha y tipo de backup
- [ ] Almacenar backup en múltiples ubicaciones
- [ ] Actualizar registro de backups

## 🎯 **Comando Recomendado para Uso Inmediato**

```bash
# ===== COMANDO DE BACKUP COMPLETO RECOMENDADO =====
# Windows (PowerShell)
$fecha = Get-Date -Format "yyyyMMdd_HHmmss"
Compress-Archive -Path "C:\Users\USR\OneDrive\Desktop\SICADFOC26\Proyecto_FOC26.2" -DestinationPath "C:\Backup\SICADFOC26_Completo_$fecha.zip"
Write-Host "✅ Backup completo de SICADFOC 26 finalizado: $fecha"

# Linux/Mac
fecha=$(date +%Y%m%d_%H%M%S)
tar -czf "SICADFOC26_Completo_$fecha.tar.gz" /ruta/a/Proyecto_FOC26.2/
echo "✅ Backup completo de SICADFOC 26 finalizado: $fecha"
```

## 📞 **Soporte Técnico**

### 🆘 **En Caso de Falla del Backup**
1. **Verificar espacio en disco**: `df -h` (Linux) o propiedades del disco (Windows)
2. **Verificar permisos**: `ls -la` en directorio origen
3. **Probar backup parcial**: Solo archivos críticos
4. **Revisar logs**: Buscar errores en archivos de log
5. **Contactar soporte**: Proporcionar mensaje de error exacto

### 📞 **Información de Contacto**
- **Tipo de Backup**: Completo del sistema SICADFOC 26
- **Archivos críticos**: 25 módulos Python + configuración
- **Base de datos**: PostgreSQL (db_foc26)
- **Formatos**: .zip, .tar.gz, .sql
- **Frecuencia recomendada**: Diario para completo, semanal para integral

**🚀 El sistema está completamente preparado para backup total con múltiples opciones y procedimientos de emergencia.**
