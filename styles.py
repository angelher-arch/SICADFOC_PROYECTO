#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
styles.py - Módulo de Estilos Dinámicos y Contraste Automático
SICADFOC 2026 - Instituto Universitario Jesus Obrero
Sistema de ajuste automático de contraste para máxima legibilidad
"""

import streamlit as st
from typing import Dict, Any, Tuple
import re

class EstiloDinamico:
    """Clase para gestión de estilos dinámicos con contraste automático"""
    
    def __init__(self):
        """Inicialización del gestor de estilos"""
        self.cache_estilos = {}
    
    def calcular_luminosidad(self, color: str) -> float:
        """
        Calcular la luminosidad relativa de un color
        Fórmula WCAG: (0.299 * R + 0.587 * G + 0.114 * B) / 255
        """
        try:
            # Limpiar el color y convertir a RGB
            color = color.replace('#', '').strip()
            
            if len(color) == 3:  # Formato #RGB
                r = int(color[0] * 2, 16)
                g = int(color[1] * 2, 16)  
                b = int(color[2] * 2, 16)
            elif len(color) == 6:  # Formato #RRGGBB
                r = int(color[0:2], 16)
                g = int(color[2:4], 16)
                b = int(color[4:6], 16)
            elif color.startswith('rgb'):  # Formato rgb(r, g, b)
                rgb_values = re.findall(r'\d+', color)
                r, g, b = map(int, rgb_values[:3])
            elif color.startswith('rgba'):  # Formato rgba(r, g, b, a)
                rgb_values = re.findall(r'\d+', color)
                r, g, b = map(int, rgb_values[:3])
            else:
                return 0.5  # Valor por defecto
            
            # Calcular luminosidad usando fórmula WCAG
            luminosidad = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return luminosidad
            
        except Exception:
            return 0.5  # Valor por defecto en caso de error
    
    def determinar_color_texto(self, color_fondo: str) -> str:
        """
        Determinar el color del texto basado en el contraste con el fondo
        """
        luminosidad = self.calcular_luminosidad(color_fondo)
        
        # Umbral de decisión (basado en WCAG)
        if luminosidad > 0.5:
            # Fondo claro -> texto oscuro
            return '#1E1E1E'  # Negro suave
        else:
            # Fondo oscuro -> texto claro
            return '#FFFFFF'  # Blanco
    
    def generar_css_contraste(self, selector: str, color_fondo: str) -> str:
        """
        Generar CSS con contraste automático para un selector específico
        """
        color_texto = self.determinar_color_texto(color_fondo)
        
        # Calcular color de sombra para mejorar legibilidad
        if color_texto == '#1E1E1E':
            # Texto oscuro sobre fondo claro -> sombra clara
            color_sombra = 'rgba(255, 255, 255, 0.8)'
        else:
            # Texto claro sobre fondo oscuro -> sombra oscura
            color_sombra = 'rgba(0, 0, 0, 0.8)'
        
        css = f"""
        {selector} {{
            color: {color_texto} !important;
            text-shadow: 1px 1px 2px {color_sombra};
            font-weight: 500;
        }}
        """
        
        return css
    
    def obtener_estilos_globales(self) -> str:
        """
        Obtener estilos CSS globales con contraste dinámico
        """
        # Cache para evitar regeneración
        cache_key = 'estilos_globales'
        if cache_key in self.cache_estilos:
            return self.cache_estilos[cache_key]
        
        # Cargar imagen IUJO-Sede como base64
        try:
            # Importar la imagen base64 desde el archivo
            import os
            base64_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'IUJO-Sede_base64.txt')
            with open(base64_path, 'r') as f:
                iujo_base64 = f.read().strip()
        except:
            # Fallback si no se puede cargar la imagen
            iujo_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        # Estilos base con contraste automático y fondo IUJO
        estilos = f"""
        <style>
        /* Estilos base con contraste dinámico */
        .stApp {{
            background-color: #0E1117;
            color: #FFFFFF;
            position: relative;
        }}
        
        /* Fondo de imagen IUJO transparente */
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url('data:image/png;base64,{iujo_base64}');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            opacity: 0.05;
            z-index: -1000;
            pointer-events: none;
        }}
        
        /* Asegurar que TODO el contenido esté por encima del fondo */
        * {{
            position: relative;
            z-index: auto !important;
        }}
        
        /* Forzar que todos los elementos de Streamlit estén encima del fondo */
        .stApp > div,
        .stApp > div > div,
        .stApp > div > div > div,
        .stApp > div > div > div > div,
        .stApp > div > div > div > div > div,
        .stApp > div > div > div > div > div > div,
        .main,
        .main .block-container,
        .element-container,
        .stForm,
        .stTextInput,
        .stButton,
        .stSelectbox,
        .stTextArea,
        .stAlert,
        .stSuccess,
        .stError,
        .stWarning,
        .stInfo,
        .stMarkdown,
        .stHeader,
        .stSubheader,
        .stTitle,
        .stCaption,
        .stDataFrame,
        .stMetric,
        .stPlotlyChart,
        .stColumns,
        .stTabs,
        .stExpander,
        .stSidebar,
        .stSidebar > div,
        .stSidebar > div > div,
        .stSidebar > div > div > div,
        .stSidebar > div > div > div > div,
        .login-form,
        .registration-form,
        .auth-container,
        .streamlit-container {{
            position: relative;
            z-index: 1 !important;
            background-color: inherit !important;
        }}
        
        /* Asegurar que los inputs y botones sean completamente funcionales */
        input, button, select, textarea {{
            position: relative;
            z-index: 2 !important;
        }}
        
        /* Contenedores transparentes - ajuste automático */
        .transparent-container {{
            background-color: rgba(255, 255, 255, 0.85);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            color: #1E1E1E !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
            font-weight: 500;
        }}
        
        /* Tablas de configuración - fondo claro */
        .config-table {{
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 8px;
            padding: 15px;
            color: #1E1E1E !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
            font-weight: 500;
        }}
        
        .config-table p {{
            color: #1E1E1E !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
            font-weight: 500;
            margin: 5px 0;
        }}
        
        .config-table strong {{
            color: #0D47A1 !important;
            font-weight: 700;
        }}
        
        /* Contenedores de información */
        .info-container {{
            background-color: rgba(255, 255, 255, 0.85);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            color: #1E1E1E !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
            font-weight: 500;
        }}
        
        .info-container p, .info-container div {{
            color: #1E1E1E !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
            font-weight: 500;
        }}
        
        /* Indicadores de estado */
        .status-indicator {{
            font-size: 1.2em;
            font-weight: bold;
            color: #1E1E1E !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
        }}
        
        /* Texto general en contenedores claros */
        .dark-text {{
            color: #1E1E1E !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
            font-weight: 500;
        }}
        
        /* Headers en contenedores claros */
        .container-header {{
            color: #0D47A1 !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.9);
            font-weight: 700;
            font-size: 1.1em;
        }}
        
        /* Asegurar contraste en todos los elementos de texto */
        .stMarkdown p, .stMarkdown div, .stMarkdown span {{
            background-color: transparent !important;
        }}
        
        /* Corrección para Streamlit */
        .element-container p {{
            color: inherit !important;
        }}
        
        /* Estilos para formularios */
        .stTextInput > div > div > input {{
            color: #1E1E1E !important;
            background-color: rgba(255, 255, 255, 0.95) !important;
        }}
        
        .stSelectbox > div > div > select {{
            color: #1E1E1E !important;
            background-color: rgba(255, 255, 255, 0.95) !important;
        }}
        
        .stTextArea > div > div > textarea {{
            color: #1E1E1E !important;
            background-color: rgba(255, 255, 255, 0.95) !important;
        }}
        
        /* DataFrames */
        .dataframe {{
            color: #1E1E1E !important;
        }}
        
        .dataframe th {{
            background-color: rgba(13, 71, 161, 0.1) !important;
            color: #0D47A1 !important;
            font-weight: 700;
        }}
        
        .dataframe td {{
            background-color: rgba(255, 255, 255, 0.8) !important;
            color: #1E1E1E !important;
            border-bottom: 1px solid rgba(0, 0, 0, 0.1) !important;
        }}
        
        /* Métricas */
        .metric-container {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            border-radius: 8px;
            padding: 15px;
            color: #1E1E1E !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
        }}
        
        .metric-label {{
            color: #0D47A1 !important;
            font-weight: 700;
        }}
        
        .metric-value {{
            color: #1E1E1E !important;
            font-weight: 600;
        }}
        
        /* Botones */
        .stButton > button {{
            color: #FFFFFF !important;
            font-weight: 600;
        }}
        
        /* Expander */
        .streamlit-expanderHeader {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            color: #1E1E1E !important;
            font-weight: 600;
        }}
        
        .streamlit-expanderContent {{
            background-color: rgba(255, 255, 255, 0.85) !important;
            color: #1E1E1E !important;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(255, 255, 255, 0.1);
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(255, 255, 255, 0.2);
            color: #FFFFFF !important;
        }}
        
        /* Alertas y mensajes */
        .stAlert {{
            border-radius: 8px;
        }}
        
        .stSuccess {{
            background-color: rgba(76, 175, 80, 0.1) !important;
            color: #2E7D32 !important;
            border-left: 4px solid #4CAF50;
        }}
        
        .stError {{
            background-color: rgba(244, 67, 54, 0.1) !important;
            color: #C62828 !important;
            border-left: 4px solid #F44336;
        }}
        
        .stWarning {{
            background-color: rgba(255, 152, 0, 0.1) !important;
            color: #F57C00 !important;
            border-left: 4px solid #FF9800;
        }}
        
        .stInfo {{
            background-color: rgba(33, 150, 243, 0.1) !important;
            color: #1976D2 !important;
            border-left: 4px solid #2196F3;
        }}
        
        </style>
        """
        
        # Cache del resultado
        self.cache_estilos[cache_key] = estilos
        return estilos
    
    def aplicar_estilos_pagina(self):
        """
        Aplicar estilos globales a la página actual
        """
        css_global = self.obtener_estilos_globales()
        st.markdown(css_global, unsafe_allow_html=True)
    
    def generar_contenedor_legible(self, contenido: str, clase_css: str = "info-container") -> str:
        """
        Generar un contenedor con estilos de contraste automático
        """
        return f'<div class="{clase_css}">{contenido}</div>'
    
    def obtener_estilo_texto_adaptativo(self, color_fondo: str) -> Dict[str, str]:
        """
        Obtener estilo de texto adaptativo para un color de fondo específico
        """
        color_texto = self.determinar_color_texto(color_fondo)
        
        if color_texto == '#1E1E1E':
            # Texto oscuro
            return {
                'color': '#1E1E1E',
                'text_shadow': '1px 1px 2px rgba(255, 255, 255, 0.8)',
                'font_weight': '500'
            }
        else:
            # Texto claro
            return {
                'color': '#FFFFFF',
                'text_shadow': '1px 1px 2px rgba(0, 0, 0, 0.8)',
                'font_weight': '500'
            }

# Instancia global del gestor de estilos
gestor_estilos = EstiloDinamico()

def aplicar_estilos_sicad():
    """
    Función de conveniencia para aplicar estilos SICADFOC
    """
    gestor_estilos.aplicar_estilos_pagina()

def crear_contenedor_transparente(contenido: str, adicional_css: str = "") -> str:
    """
    Crear un contenedor transparente con estilos de contraste
    """
    css_adicional = f" style='{adicional_css}'" if adicional_css else ""
    return f'<div class="transparent-container"{css_adicional}>{contenido}</div>'

def crear_tabla_configuracion(contenido: str) -> str:
    """
    Crear una tabla de configuración con estilos legibles
    """
    return f'<div class="config-table">{contenido}</div>'

def texto_adaptativo(texto: str, color_fondo: str = "rgba(255, 255, 255, 0.85)") -> str:
    """
    Generar texto con contraste adaptativo
    """
    estilo = gestor_estilos.obtener_estilo_texto_adaptativo(color_fondo)
    css = f"color: {estilo['color']} !important; text-shadow: {estilo['text_shadow']}; font-weight: {estilo['font_weight']};"
    return f'<span style="{css}">{texto}</span>'
