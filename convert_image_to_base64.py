#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert_image_to_base64.py - Script para convertir IUJO-Sede.png a base64
SICADFOC 2026 - Instituto Universitario Jesus Obrero
"""

import base64
from pathlib import Path

def convert_image_to_base64():
    """Convertir IUJO-Sede.png a base64 para CSS"""
    image_path = Path(__file__).parent / "IUJO-Sede.png"
    
    if not image_path.exists():
        print(f"❌ No se encontró la imagen: {image_path}")
        return None
    
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
        print(f"✅ Imagen convertida exitosamente")
        print(f"📁 Ruta: {image_path}")
        print(f"📏 Tamaño base64: {len(encoded_string)} caracteres")
        
        return encoded_string
        
    except Exception as e:
        print(f"❌ Error convirtiendo imagen: {e}")
        return None

if __name__ == "__main__":
    base64_image = convert_image_to_base64()
    
    if base64_image:
        # Guardar en un archivo para referencia
        output_path = Path(__file__).parent / "IUJO-Sede_base64.txt"
        with open(output_path, "w") as f:
            f.write(base64_image)
        print(f"💾 Guardado en: {output_path}")
        
        # Mostrar primeros caracteres para verificar
        print(f"🔍 Inicio del base64: {base64_image[:100]}...")
