# SICADFOC 26 - Dockerfile para Despliegue en Render
# Contenedor optimizado con dependencias de sistema y binarios pre-compilados

FROM python:3.11-slim

# Variables de entorno para optimización y logs instantáneos
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias de sistema de forma robusta
RUN apt-get update -y

RUN apt-get install -y --fix-missing \
    # Tesseract OCR con lenguaje español (esencial para Formación Extemporánea)
    tesseract-ocr \
    tesseract-ocr-spa \
    libtesseract-dev \
    # Dependencias para psycopg2 (base de datos PostgreSQL)
    libpq-dev \
    gcc \
    python3-dev \
    # Dependencias para procesamiento de imágenes y OpenCV
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    libharfbuzz0 \
    libxcb-shm0 \
    libxcb-xfixes0 \
    # Herramientas esenciales del sistema
    curl \
    wget \
    git \
    # Limpieza de caché para reducir tamaño del contenedor
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Verificar instalación de Tesseract OCR
RUN tesseract --version && \
    echo "✅ Tesseract OCR instalado correctamente" && \
    tesseract --list-langs | grep spa && \
    echo "✅ Soporte para español confirmado"

# Copiar requirements.txt primero para optimizar caché de Docker
COPY requirements.txt .

# Instalar dependencias Python con binarios pre-compilados
# Evita errores de compilación en el servidor
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    --only-binary :all: \
    --requirement requirements.txt

# Copiar archivos de la aplicación
COPY . .

# Crear directorios necesarios para la aplicación
RUN mkdir -p /app/media /app/logs /app/temp

# Establecer permisos para scripts (si existen)
RUN chmod +x setup.sh 2>/dev/null || true

# Exponer puerto 8501 (puerto por defecto de Streamlit)
EXPOSE 8501

# Comando de inicio para producción en Render
CMD ["streamlit", "run", "main.py", "--server.port", "$PORT", "--server.address", "0.0.0.0"]
