# SICADFOC 26 - Dockerfile Optimizado para Render
# Imagen base ligera con Python 3.11 y dependencias precompiladas

FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias de sistema para Tesseract y procesamiento de imágenes
RUN apt-get update && apt-get install -y \
    # Tesseract OCR y lenguaje español
    tesseract-ocr \
    tesseract-ocr-spa \
    libtesseract-dev \
    # Dependencias para procesamiento de imágenes (OpenCV)
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
    # Herramientas de sistema
    curl \
    wget \
    git \
    # Limpieza
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Verificar instalación de Tesseract
RUN tesseract --version && \
    echo "✅ Tesseract instalado correctamente"

# Copiar requirements.txt primero para caché de Docker
COPY requirements.txt .

# Instalar dependencias Python con binarios precompilados (evitar compilación)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    --only-binary=:all: \
    --requirement requirements.txt

# Copiar archivos de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/media /app/logs

# Establecer permisos
RUN chmod +x setup.sh 2>/dev/null || true

# Exponer puerto de Streamlit
EXPOSE 8501

# Comando de ejecución para producción
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
