# Instrucciones para Configurar OCR - Formación Extemporánea

## 📋 Resumen
Este documento explica cómo configurar el motor OCR (Tesseract) para el módulo de Formación Complementaria Extemporánea en SICADFOC 2026.

## 🔧 Requisitos Previos

### 1. Instalar Tesseract OCR
**Windows:**
```cmd
# Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
# O usar chocolatey:
choco install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-spa
```

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang
```

### 2. Instalar Python pytesseract
```cmd
pip install pytesseract
pip install pillow
```

### 3. Configurar Variable de Entorno (Windows)
```cmd
# Agregar al PATH del sistema
C:\Program Files\Tesseract-OCR
```

O en Python:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## 🗄️ Configuración Base de Datos

### Ejecutar Script SQL
```cmd
cd "c:\Users\USR\OneDrive\Desktop\SICADFOC26\Proyecto_FOC26.2"
psql -h localhost -U postgres -d db_foc26 -f crear_tabla_certificados_extemporaneos.sql
```

### O usando pgAdmin
1. Conectarse a `db_foc26`
2. Abrir Query Tool
3. Ejecutar el contenido de `crear_tabla_certificados_extemporaneos.sql`

## ✅ Verificación

### 1. Verificar Tesseract
```cmd
tesseract --version
```

### 2. Verificar Python
```python
import pytesseract
from PIL import Image
print("OCR disponible:", pytesseract.get_languages(config=''))
```

### 3. Verificar Base de Datos
```sql
SELECT COUNT(*) FROM certificados_extemporaneos;
```

## 🚀 Uso del Módulo

### Acceso al Sistema
1. Iniciar Streamlit: `streamlit run main.py`
2. Iniciar sesión como administrador
3. Hacer clic en "Formación Extemporánea"

### Flujo de Trabajo
1. **Subir Imagen**: Seleccionar certificado escaneado (JPG/PNG)
2. **Procesar OCR**: Click en "Extraer Datos con OCR"
3. **Validar Datos**: Revisar y corregir información extraída
4. **Guardar**: Almacenar en base de datos

### Campos Extraídos
- **Nombre del Taller**: Título del curso/taller
- **Nombre del Estudiante**: Participante del certificado
- **Duración**: Total de horas (ej: "40 horas")
- **Objetivo**: Competencias o propósitos del taller

## 🔧 Solución de Problemas

### Error: "OCR no disponible"
```bash
# Instalar Tesseract
pip install pytesseract
# Configurar PATH o variable de entorno
```

### Error: "Language not supported"
```bash
# Instalar paquete de español
sudo apt install tesseract-ocr-spa  # Linux
brew install tesseract-lang         # macOS
# Windows ya incluye español por defecto
```

### Error: "Tabla no existe"
```sql
-- Ejecutar script de creación
\i crear_tabla_certificados_extemporaneos.sql
```

### Error de permisos
```sql
-- Verificar permisos del usuario
GRANT ALL PRIVILEGES ON certificados_extemporaneos TO postgres;
```

## 📊 Características del Sistema

### Motor OCR
- **Motor**: Tesseract OCR
- **Idioma**: Español (spa)
- **Formatos**: JPG, JPEG, PNG
- **Procesamiento**: Extracción de texto y patrones

### Extracción Inteligente
- **Patrones RegEx**: Para identificar campos específicos
- **Validación**: Revisión manual de datos extraídos
- **Corrección**: Edición de datos antes de guardar

### Almacenamiento
- **Base de Datos**: PostgreSQL local
- **Imágenes**: Base64 (en BD)
- **Texto OCR**: Completo para referencia
- **Metadatos**: Fecha, usuario procesador, estado

## 🎯 Mejores Prácticas

### Calidad de Imágenes
- **Resolución**: Mínimo 300 DPI
- **Formato**: JPG o PNG sin compresión excesiva
- **Iluminación**: Buena luz, sin sombras
- **Orientación**: Texto horizontal y legible

### Validación de Datos
- **Revisar siempre** los datos extraídos por OCR
- **Corregir errores** comunes de reconocimiento
- **Verificar nombres** y duraciones específicas
- **Completar objetivos** si no se extraen bien

### Mantenimiento
- **Limpiar registros** antiguos periódicamente
- **Optimizar imágenes** para reducir tamaño
- **Actualizar Tesseract** a últimas versiones
- **Monitorear calidad** del reconocimiento

## 📞 Soporte

Si experimenta problemas:
1. Verificar instalación de Tesseract
2. Confirmar configuración de PATH
3. Ejecutar script SQL de tabla
4. Revisar logs de Streamlit
5. Contactar administrador del sistema
