# version.py - Módulo de control de versiones para FOC26

import os
from datetime import datetime

# Versión actual del sistema
VERSION = "1.0.0"
BUILD_DATE = "2026-04-08"
BUILD_TIME = datetime.now().strftime("%H:%M:%S")

# Información de despliegue
DEPLOY_PLATFORM = os.getenv('RENDER', 'Local Development')
GIT_COMMIT = os.getenv('RENDER_GIT_COMMIT', 'N/A')
GIT_BRANCH = os.getenv('RENDER_GIT_BRANCH', 'main')

def get_version_info():
    """Retorna información completa de la versión"""
    return {
        'version': VERSION,
        'build_date': BUILD_DATE,
        'build_time': BUILD_TIME,
        'platform': DEPLOY_PLATFORM,
        'git_commit': GIT_COMMIT[:8] if GIT_COMMIT != 'N/A' else 'N/A',
        'git_branch': GIT_BRANCH
    }

def display_version_info():
    """Muestra información de versión en formato legible"""
    info = get_version_info()
    return f"""
**Versión:** {info['version']}
**Fecha de Build:** {info['build_date']} {info['build_time']}
**Plataforma:** {info['platform']}
**Commit:** {info['git_commit']}
**Branch:** {info['git_branch']}
"""

def get_short_version():
    """Retorna versión corta para display"""
    return f"v{VERSION} ({BUILD_DATE})"