# TABLA COMPARATIVA: CAMPOS BD vs CAMPOS DEL CÓDIGO

## 📊 **ANÁLISIS DEL ERROR**

**Error detectado:** `(17, null, Desarrollo de Aplicaciones con Streamlit., [Descripción larga...], 20, IU-FOC-2026-1-4, 14300385, fecha, null)`

## 🔍 **DETECCIÓN DE PROBLEMAS**

| Posición | Valor Recibido | Campo Esperado | Problema |
|----------|----------------|----------------|----------|
| 1 | 17 | id_formacion | ✅ Auto-incremental |
| 2 | **null** | **id_taller** | ❌ **ERROR CRÍTICO** |
| 3 | Desarrollo de Aplicaciones con Streamlit. | nombre | ✅ Correcto |
| 4 | [Descripción larga...] | descripcion | ❌ **Campo no existe** |
| 5 | 20 | horas | ✅ Correcto |
| 6 | IU-FOC-2026-1-4 | codigo_certificado | ✅ Correcto |
| 7 | 14300385 | id_usuario | ✅ Correcto |
| 8 | fecha | fecha_creacion | ✅ Auto-generado |
| 9 | null | codigo_referencia | ❌ **Campo nuevo** |

## 🗂️ **ESTRUCTURA REAL DE LA TABLA (Según el error)**

```sql
-- Orden real de columnas en la tabla:
CREATE TABLE public.formacion_complementaria (
    id_formacion SERIAL PRIMARY KEY,      -- Posición 1
    id_taller INTEGER NOT NULL,          -- Posición 2 ❌ PROBLEMA
    nombre VARCHAR,                      -- Posición 3 ✅
    descripcion TEXT,                    -- Posición 4 ❌ NO EXISTE?
    horas INTEGER,                       -- Posición 5 ✅
    codigo_certificado VARCHAR,           -- Posición 6 ✅
    id_usuario VARCHAR,                  -- Posición 7 ✅
    fecha_creacion TIMESTAMP DEFAULT NOW(), -- Posición 8 ✅
    codigo_referencia VARCHAR            -- Posición 9 ❌ CAMPO NUEVO
);
```

## 📝 **CAMPOS QUE EL CÓDIGO ESTÁ ENVIANDO**

### ❌ **CÓDIGO ANTERIOR (INCORRECTO)**
```python
datos_iniciales = {
    "nombre": nombre,                    # ✅ Posición 3
    "descripcion": descripcion,          # ❌ Posición 4 (no existe?)
    "horas": 20,                      # ✅ Posición 5
    "codigo_certificado": codigo_auto,  # ✅ Posición 6
    "id_usuario": st.session_state.cedula # ✅ Posición 7
}
```

### ✅ **CÓDIGO CORREGIDO**
```python
datos_iniciales = {
    "nombre": nombre,                    # ✅ Posición 3
    "horas": 20,                      # ✅ Posición 5
    "codigo_certificado": codigo_auto,  # ✅ Posición 6
    "id_usuario": st.session_state.cedula # ✅ Posición 7
}
```

## 🎯 **SOLUCIÓN APLICADA**

### **INSERT EXPLÍCITO CORRECTO**
```sql
INSERT INTO public.formacion_complementaria 
    (nombre, horas, codigo_certificado, id_usuario) 
VALUES 
    (%s, %s, %s, %s) 
RETURNING id_taller;
```

### **QUÉ CAMBIOS SE HICIERON**
1. ❌ **Eliminado `descripcion`** - Campo no existe en la tabla
2. ❌ **Eliminado `id_taller`** - Se genera automáticamente con SERIAL
3. ✅ **Columnas explícitas** - Evita desplazamiento
4. ✅ **RETURNING id_taller** - Obtiene el ID generado

## 📋 **VARIABLES DE STREAMLIT QUE SE PASAN AL EXECUTE()**

| Variable Streamlit | Valor Ejemplo | Columna BD | Estado |
|-------------------|---------------|-------------|---------|
| `nombre` | "Desarrollo de Aplicaciones con Streamlit" | nombre | ✅ |
| `horas` | 20 | horas | ✅ |
| `codigo_certificado` | "IU-FOC-2026-1-4" | codigo_certificado | ✅ |
| `id_usuario` | "14300385" | id_usuario | ✅ |

## 🔧 **DIAGNÓSTICO FINAL**

**Problema principal:** El INSERT no especificaba columnas explícitamente, causando que PostgreSQL intentara insertar valores en el orden incorrecto, incluyendo `NULL` en `id_taller`.

**Solución:** Especificar columnas explícitamente y omitir campos que no existen o son auto-generados.
