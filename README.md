# Assets - SICADFOC 2026

## 📁 **Directorio de Assets**

Este directorio contiene todos los recursos visuales y estáticos del sistema SICADFOC 2026.

### 🖼️ **Imágenes Institucionales**

#### **Logo IUJO**
- **Archivo**: `Logo_IUJO.png`
- **Descripción**: Logo principal del Instituto Universitario Jesús Obrero
- **Uso**: Header de la aplicación, sidebar, documentos
- **Dimensiones**: 120x60px (escalable)
- **Formato**: PNG con transparencia

#### **Sede IUJO**
- **Archivo**: `IUJO-Sede.png`
- **Descripción**: Fotografía de la sede institucional
- **Uso**: Fondo principal de la aplicación (con filtro de oscurecimiento)
- **Dimensiones**: 1920x1080px (escalable)
- **Formato**: PNG de alta calidad

### 🎨 **Uso en el Sistema**

#### **Rutas Relativas**
Todas las imágenes se cargan usando rutas relativas para garantizar portabilidad:

```python
# Logo en login
<img src="./Logo_IUJO.png" alt="Logo IUJO">

# Fondo principal
background: url('./IUJO-Sede.png') center/cover no-repeat;
```

#### **Aplicación de Estilos**
Las imágenes se integran con el sistema de estilos CSS:

- **Dark Mode**: Filtro de `brightness(0.4)` para la imagen de sede
- **Glassmorphism**: Efectos de desenfoque y transparencia
- **Responsive**: Ajuste automático según tamaño de pantalla

### 📂 **Estructura de Directorio**

```
assets/
├── README.md                 # Este archivo
├── Logo_IUJO.png           # Logo institucional
├── IUJO-Sede.png           # Fotografía de la sede
└── [futuros assets...]     # Espacio para recursos adicionales
```

### 🔧 **Mantenimiento**

#### **Agregar Nuevos Assets**
1. Colocar archivos en este directorio
2. Usar rutas relativas en el código
3. Actualizar este README.md

#### **Optimización de Imágenes**
- Formato: PNG para logos con transparencia
- Compresión: Balance entre calidad y tamaño
- Dimensiones: Optimizadas para web

### 📋 **Especificaciones Técnicas**

#### **Requisitos de Imágenes**
- **Formatos**: PNG, JPG, SVG
- **Tamaño máximo**: 2MB por archivo
- **Resolución**: 72 DPI para web
- **Optimización**: Comprimidas sin pérdida visible de calidad

#### **Compatibilidad**
- **Navegadores**: Chrome, Firefox, Safari, Edge
- **Dispositivos**: Desktop, Tablet, Mobile
- **Sistemas**: Windows, Linux, macOS

---

**📌 Nota**: Este directorio está diseñado para ser autocontenido y portable, garantizando que el sistema funcione en cualquier entorno sin dependencias externas.
