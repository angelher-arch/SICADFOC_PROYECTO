# Scripts de Prueba - SICADFOC 2026

## 📋 Descripción
Scripts de prueba para validar la funcionalidad de creación de talleres y compatibilidad con PostgreSQL en entornos de nube.

## 🧪 Scripts Disponibles

### 0. `run_all_tests.py` (Script Maestro)
**Propósito**: Ejecuta todas las pruebas de validación automáticamente.

**Funcionalidades**:
- ✅ Ejecuta todas las pruebas en secuencia
- ✅ Reporte detallado de resultados
- ✅ Timeout de 30s por prueba
- ✅ Resumen final con estadísticas
- ✅ Código de salida para integración CI/CD

**Uso**:
```bash
python run_all_tests.py
```

**Salida esperada**:
```
🧪 SUITE DE PRUEBAS - SICADFOC 2026
============================================================
📅 Fecha: 2024-01-15 14:30:45
🌐 Entorno: Producción
============================================================

============================================================
🚀 EJECUTANDO: test_returning_id.py
📋 Descripción: Prueba RETURNING id en PostgreSQL
============================================================
...
✅ test_returning_id.py: EXITOSO

============================================================
🚀 EJECUTANDO: test_campos_nuevos.py
📋 Descripción: Prueba campos nuevos (cohorte, tomo, folio)
============================================================
...
✅ test_campos_nuevos.py: EXITOSO

============================================================
🚀 EJECUTANDO: test_crear_taller.py
📋 Descripción: Prueba completa creación de taller ficticio
============================================================
...
✅ test_crear_taller.py: EXITOSO

============================================================
📊 RESUMEN FINAL DE PRUEBAS
============================================================
1. test_returning_id.py: ✅ PASÓ
2. test_campos_nuevos.py: ✅ PASÓ
3. test_crear_taller.py: ✅ PASÓ

📈 Total de pruebas: 3
✅ Exitosas: 3
❌ Fallidas: 0
📊 Tasa de éxito: 100.0%

🎉 TODAS LAS PRUEBAS PASARON EXITOSAMENTE
El sistema está listo para despliegue en producción.
```

### 1. `test_crear_taller.py`
**Propósito**: Prueba completa de creación de taller ficticio con todos los campos nuevos.

**Funcionalidades probadas**:
- ✅ Inserción en tabla `taller` con todos los campos
- ✅ Inserción en tabla `formacion_complementaria`
- ✅ RETURNING id_taller e id_formacion
- ✅ Transacciones con commit/rollback
- ✅ Verificación de datos insertados
- ✅ Compatibilidad con PostgreSQL en la nube

**Uso**:
```bash
python test_crear_taller.py
```

**Limpieza de datos de prueba**:
```bash
python test_crear_taller.py --clean
```

### 2. `test_returning_id.py`
**Propósito**: Prueba específica del RETURNING id en PostgreSQL.

**Funcionalidades probadas**:
- ✅ INSERT con RETURNING id_taller
- ✅ Compatibilidad con diferentes versiones de PostgreSQL
- ✅ Funcionamiento en entornos locales y nube

**Uso**:
```bash
python test_returning_id.py
```

### 3. `test_campos_nuevos.py`
**Propósito**: Prueba específica de campos nuevos (cohorte, tomo, folio).

**Funcionalidades probadas**:
- ✅ Lógica de generación de código certificado
- ✅ Campos cohorte (1 o 2), tomo y folio
- ✅ Formato IU-FOC-{año}-{cohorte}-{tomo}
- ✅ Integración con formulario de talleres

**Uso**:
```bash
python test_campos_nuevos.py
```

## 📊 Datos de Prueba

### Taller Ficticio (`test_crear_taller.py`)
- **Nombre**: "Taller de Prueba - Introducción a Python Avanzado"
- **Descripción**: Descripción detallada del taller
- **Fechas**: 2026-06-01 al 2026-06-05
- **Capacidad**: 25 estudiantes
- **Duración**: 20 horas
- **Cohorte**: 1
- **Tomo**: "001"
- **Folio**: "12345"
- **Código Certificado**: `IU-FOC-2026-1-001`

## 🔍 Validaciones Realizadas

### Campos Nuevos
- ✅ `cohorte` (1 o 2)
- ✅ `tomo` (string para código)
- ✅ `folio` (string para código)
- ✅ Generación automática de `codigo_certificado`

### Compatibilidad PostgreSQL
- ✅ RETURNING id funciona en entornos de nube
- ✅ Transacciones con AUTOCOMMIT
- ✅ Inserciones con FK constraints
- ✅ Manejo de errores y rollback

### Integridad de Datos
- ✅ Relación taller → formacion_complementaria
- ✅ Campos NOT NULL respetados
- ✅ Tipos de datos correctos
- ✅ Constraints de unicidad

## 🚀 Ejecución en Entornos

### Desarrollo Local
```bash
# Configurar variables de entorno
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=db_foc26
export DB_USER=postgres
export DB_PASSWORD=your_password

# Ejecutar pruebas
python test_crear_taller.py
python test_returning_id.py
```

### Producción (Railway/Render)
```bash
# La aplicación detecta automáticamente DATABASE_URL
# Ejecutar pruebas
python test_crear_taller.py
python test_returning_id.py
```

## 📈 Resultados Esperados

### Salida Exitosa
```
🧪 INICIANDO PRUEBA: Creación de Taller Ficticio
============================================================
📋 DATOS DEL TALLER FICTICIO:
   nombre: Taller de Prueba - Introducción a Python Avanzado
   descripcion: Taller ficticio creado para validar...
   ...

🔌 Estableciendo conexión a la base de datos...
✅ Conexión establecida correctamente

🔄 Iniciando transacción...
✅ Transacción iniciada

📝 Insertando registro en tabla 'taller'...
✅ Taller insertado correctamente. ID generado: 123

📝 Insertando registro en tabla 'formacion_complementaria'...
✅ Formación complementaria insertada correctamente. ID generado: 456

🔍 Verificando inserción...
✅ Taller verificado en BD
✅ Formación complementaria verificada en BD

💾 Confirmando transacción...
✅ Transacción confirmada exitosamente

🎉 PRUEBA COMPLETADA EXITOSAMENTE
============================================================
📊 RESUMEN:
   • Taller creado: ID 123
   • Formación creada: ID 456
   • Código certificado: IU-FOC-2026-1-001
   • RETURNING id: ✅ Funciona correctamente
   • Campos nuevos: ✅ cohorte, tomo, folio incluidos
   • Entorno nube: ✅ Compatible con PostgreSQL
```

## 🛠️ Solución de Problemas

### Error de Conexión
- Verificar `DATABASE_URL` en producción
- Verificar credenciales en desarrollo local
- Confirmar que PostgreSQL esté ejecutándose

### Error RETURNING
- PostgreSQL versión < 8.2 no soporta RETURNING
- Verificar sintaxis: `RETURNING id_taller`
- Confirmar que la tabla tiene columna `id_taller` SERIAL

### Error de Permisos
- Usuario debe tener permisos INSERT en las tablas
- Verificar que las tablas existan (ejecutar `sincronizacion_tablas.sql`)

## 📝 Notas Importantes

- Los scripts crean datos ficticios que permanecen en la BD
- Usar `--clean` para eliminar datos de prueba
- Compatible con PostgreSQL 9.0+ (RETURNING disponible desde 8.2)
- Funciona en entornos con y sin SSL
- Manejo automático de diferentes configuraciones de conexión