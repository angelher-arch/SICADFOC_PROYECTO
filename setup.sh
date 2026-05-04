#!/bin/bash
# SICADFOC 26 - Setup para Despliegue en Render
# Instalación de dependencias de sistema y configuración inicial

set -e  # Detener en caso de error

echo "🚀 Iniciando setup para SICADFOC 26 en Render..."

# Actualizar paquetes del sistema
echo "📦 Actualizando paquetes del sistema..."
apt-get update -y

# Instalar dependencias de sistema para procesamiento de imágenes y OCR
echo "🔧 Instalando dependencias de sistema..."
apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    libharfbuzz0 \
    libxcb-shm0 \
    libxcb-xfixes0

# Verificar instalación de Tesseract
echo "🔍 Verificando instalación de Tesseract..."
if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version | cut -d' ' -f1)
    echo "✅ Tesseract $TESSERACT_VERSION instalado correctamente"
else
    echo "❌ Error: Tesseract no se pudo instalar"
    exit 1
fi

# Mostrar información del sistema
echo "📊 Información del sistema:"
echo "Python: $(python --version)"
echo "Tesseract: $(tesseract --version)"
echo "Directorio actual: $(pwd)"

echo "✅ Setup completado exitosamente"
echo "🌐 El sistema está listo para el despliegue en Render"
