# SICADFOC 26 - Dockerfile de Emergencia Alpine
# Contenedor ligero con Alpine Linux para evitar problemas de apt

FROM python:3.11-alpine

# Variables de entorno para optimización y logs instantáneos
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias de sistema con Alpine
RUN apk add --no-cache \
    # Tesseract OCR con lenguaje español
    tesseract-ocr \
    tesseract-ocr-data-spa \
    # Dependencias para PostgreSQL
    postgresql-dev \
    libpq-dev \
    # Compiladores y desarrollo
    gcc \
    musl-dev \
    # Procesamiento de imágenes
    jpeg-dev \
    zlib-dev \
    # Herramientas esenciales
    curl

# Verificar instalación de Tesseract OCR
RUN tesseract --version && \
    echo "✅ Tesseract OCR instalado correctamente" && \
    tesseract --list-langs | grep spa && \
    echo "✅ Soporte para español confirmado"

# Copiar requirements.txt primero para optimizar caché de Docker
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --requirement requirements.txt

# Copiar archivos de la aplicación
COPY . .

# Crear directorios necesarios para la aplicación
RUN mkdir -p /app/media /app/logs /app/temp

# Exponer puerto 8501 (puerto por defecto de Streamlit)
EXPOSE 8501

# Comando de inicio para producción en Render
CMD ["streamlit", "run", "main.py", "--server.port", "$PORT", "--server.address", "0.0.0.0"]
