# MAPEO DETALLADO DE LA FILA DE ERROR

## 🚨 **ERROR DETECTADO**

**Fila fallida:** `(19, null, null, null, 20, IU-FOC-2026-1-4, null, 2026-05-10 10:44...)`

## 📊 **ANÁLISIS POSICIÓN POR POSICIÓN**

| Posición | Valor en Fila | Columna BD | Análisis |
|----------|----------------|-------------|----------|
| **1** | **19** | **id_formacion** | ✅ **ID auto-incremental del registro** |
| **2** | **null** | **id_taller** | ❌ **ERROR CRÍTICO** - Debe ser INTEGER auto-generado |
| **3** | **null** | **nombre** | ❌ **PROBLEMA** - Campo no se está insertando |
| **4** | **null** | **descripcion** | ❌ **PROBLEMA** - Campo no se está insertando |
| **5** | **20** | **horas** | ✅ **Valor por defecto** - Se está insertando correctamente |
| **6** | **IU-FOC-2026-1-4** | **codigo_certificado** | ✅ **Campo correcto** - Se está insertando |
| **7** | **null** | **id_usuario** | ❌ **PROBLEMA** - Campo no se está insertando |
| **8** | **2026-05-10 10:44...** | **fecha_creacion** | ✅ **Auto-generado** - TIMESTAMP por defecto |
| **9** | **null** | **codigo_referencia** | ❌ **PROBLEMA** - Campo no se está insertando |

## 🔍 **DIAGNÓSTICO DEL PROBLEMA**

### **¿Por qué hay tantos NULLs consecutivos?**

El problema fundamental es que el INSERT actual **NO especifica columnas explícitamente**. PostgreSQL está interpretando:

```sql
INSERT INTO public.formacion_complementaria VALUES (%s)
```

Como si fuera:

```sql
INSERT INTO public.formacion_complementaria 
(id_formacion, id_taller, nombre, descripcion, horas, codigo_certificado, id_usuario, fecha_creacion, codigo_referencia) 
VALUES (DEFAULT, %s, DEFAULT, DEFAULT, DEFAULT, %s, DEFAULT, DEFAULT, DEFAULT)
```

### **¿Qué representa el 19?**
- Es el **id_formacion** auto-incremental del registro
- No es el id_taller (que es null y causa el error)

## 🎯 **SOLUCIÓN REQUERIDA**

### **INSERT EXPLÍCITO CORRECTO**
```sql
INSERT INTO public.formacion_complementaria 
    (nombre, horas, codigo_certificado, id_usuario) 
VALUES 
    (%s, %s, %s, %s) 
RETURNING id_taller;
```

### **VALORES CORRECTOS**
```python
valores = [
    nombre,                    # Posición 3: nombre del taller
    20,                        # Posición 5: horas por defecto
    codigo_auto,              # Posición 6: código del certificado
    st.session_state.cedula    # Posición 7: ID del usuario
]
```

## 🔧 **ESTRUCTURA FINAL ESPERADA**

Después del INSERT con RETURNING y UPDATE:

| Columna | Valor Esperado |
|----------|----------------|
| id_formacion | 19 (auto-incremental) |
| id_taller | **123** (GENERADO POR SERIAL) |
| nombre | **"Desarrollo de Aplicaciones con Streamlit"** |
| descripcion | **NULL** (permitido) |
| horas | **20** |
| codigo_certificado | **"IU-FOC-2026-1-4"** |
| id_usuario | **"14300385"** |
| fecha_creacion | **2026-05-10 10:44...** |
| codigo_referencia | **"IU-FOC-2026-1-4-123-Desarrollo_de_Aplicaciones_con_Streamlit"** |

## 📋 **CONCLUSIÓN**

El problema es que el INSERT no especifica columnas explícitamente, causando que PostgreSQL intente insertar NULL en id_taller (que es NOT NULL) y otros campos obligatorios.
