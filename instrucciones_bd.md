# Instrucciones para Actualizar Base de Datos - Agregar Cohorte

## 📋 Resumen
Este documento explica cómo actualizar la base de datos local PostgreSQL para agregar la columna `cohorte` y actualizar el formato del `codigo_certificado`.

## 🗄️ Cambios Requeridos

### 1. Columna Cohorte en `formacion_complementaria`
- **Tipo**: INTEGER
- **Obligatorio**: Sí (NOT NULL)
- **Valor por defecto**: 1

### 2. Actualizar longitud de `codigo_certificado`
- **Formato actual**: VARCHAR(50)
- **Nuevo formato**: VARCHAR(100)
- **Nuevo formato de código**: `IU-FOC-[Año]-[Cohorte]-[Tomo]`
- **Ejemplo**: `IU-FOC-2026-1-001`

## 🚀 Ejecución Manual

### Opción 1: Usar pgAdmin
1. Abre pgAdmin y conecta a `db_foc26`
2. Ejecuta el siguiente SQL:

```sql
-- Agregar columna cohorte
ALTER TABLE formacion_complementaria ADD COLUMN cohorte INTEGER NOT NULL DEFAULT 1;

-- Actualizar longitud de codigo_certificado
ALTER TABLE formacion_complementaria ALTER COLUMN codigo_certificado TYPE VARCHAR(100);
```

### Opción 2: Usar línea de comandos (Windows)
```cmd
cd "c:\Users\USR\OneDrive\Desktop\SICADFOC26\Proyecto_FOC26.2"
psql -h localhost -U postgres -d db_foc26 -f actualizar_bd_cohorte.sql
```

### Opción 3: Usar línea de comandos (PowerShell)
```powershell
Set-Location "c:\Users\USR\OneDrive\Desktop\SICADFOC26\Proyecto_FOC26.2"
psql -h localhost -U postgres -d db_foc26 -f actualizar_bd_cohorte.sql
```

## ✅ Verificación

Después de ejecutar el script, verifica los cambios:

```sql
-- Verificar estructura de la tabla
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'formacion_complementaria' 
ORDER BY ordinal_position;

-- Verificar datos existentes
SELECT id_formacion, nombre, codigo_certificado, cohorte 
FROM formacion_complementaria 
ORDER BY id_formacion;
```

## 🔧 Solución de Problemas

### Si psql no está en el PATH
1. Instala PostgreSQL o asegúrate que esté en el PATH
2. O usa la ruta completa: `"C:\Program Files\PostgreSQL\16\bin\psql.exe"`

### Si necesitas contraseña
```cmd
psql -h localhost -U postgres -W -d db_foc26 -f actualizar_bd_cohorte.sql
```

### Si la base de datos tiene otro nombre
Reemplaza `db_foc26` con el nombre correcto de tu base de datos.

## 📝 Notas Importantes

- El script incluye verificaciones para no ejecutar cambios si ya existen
- La columna `cohorte` se agrega con valor por defecto 1 para registros existentes
- El nuevo formato de código se genera automáticamente en la aplicación
- Los registros existentes conservarán sus códigos actuales

## 🎯 Prueba Final

Después de actualizar la BD:
1. Inicia la aplicación Streamlit
2. Ve a Formación Complementaria → Crear Taller
3. Completa todos los campos incluyendo Cohorte
4. Verifica que el código se genere como: `IU-FOC-2026-1-001`
5. Guarda y verifica que se almacene correctamente en la BD
