# SICADFOC 26 - Dockerfile Optimizado Final
# Contenedor con python:3.11-slim y binarios pre-compilados

FROM python:3.11-slim

# Variables de entorno para optimización y logs instantáneos
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias de sistema para PostgreSQL y compilación
RUN apt-get update -y && apt-get install -y --fix-missing \
    # Tesseract OCR con lenguaje español
    tesseract-ocr \
    tesseract-ocr-spa \
    libtesseract-dev \
    # Dependencias para PostgreSQL (crucial para FOC26DB)
    libpq-dev \
    gcc \
    python3-dev \
    # Procesamiento de imágenes
    libjpeg-dev \
    zlib1g-dev \
    # Herramientas esenciales
    curl \
    # Limpieza de caché
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Verificar instalación de Tesseract OCR
RUN tesseract --version && \
    echo "✅ Tesseract OCR instalado correctamente" && \
    tesseract --list-langs | grep spa && \
    echo "✅ Soporte para español confirmado"

# Copiar requirements.txt primero para optimizar caché de Docker
COPY requirements.txt .

# Instalar dependencias Python con binarios pre-compilados (EVITA COMPILACIÓN)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --only-binary :all: -r requirements.txt

# Copiar archivos de la aplicación
COPY . .

# Crear directorios necesarios para la aplicación
RUN mkdir -p /app/media /app/logs /app/temp

# Exponer puerto 8501 (puerto por defecto de Streamlit)
EXPOSE 8501

# Comando de inicio para producción en Render
CMD ["streamlit", "run", "main.py", "--server.port", "$PORT", "--server.address", "0.0.0.0"]
