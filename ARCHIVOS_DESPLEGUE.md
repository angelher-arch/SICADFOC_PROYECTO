# ARCHIVOS NECESARIOS PARA DESPLIEGUE - SICADFOC 2026

## Checklist Completo de Archivos para Despliegue en Render

### 1. ARCHIVOS OBLIGATORIOS (CRÍTICOS)

#### Archivos Principales de la Aplicación
```
main.py                     - Aplicación principal Streamlit
database.py                 - Gestión de base de datos con conexión dual
seguridad.py                - Sistema de permisos y autorización
auth_unificado.py           - Sistema de autenticación unificado
formacion_complementaria.py - Módulo de formación complementaria
gestion_estudiantil.py      - Módulo de gestión de estudiantes
gestion_profesores.py       - Módulo de gestión de profesores
gestion_carreras.py         - Módulo de gestión de carreras
gestion_permisos.py         - Módulo de gestión de permisos
reportes.py                 - Módulo de informes y reportes
gestor_certificaciones.py   - Gestor de certificaciones
```

#### Archivos de Configuración
```
requirements.txt            - Dependencias Python
render.yaml                 - Configuración de despliegue Render
.gitignore                  - Exclusiones de Git
runtime.txt                 - Versión Python (opcional)
```

#### Base de Datos
```
sincronizacion_tablas.sql   - Estructura inicial de base de datos
```

### 2. ARCHIVOS OPCIONALES (RECOMENDADOS)

#### Documentación
```
README.md                   - Documentación del proyecto
DESPLEGUE_RENDER.md         - Guía detallada de despliegue
ARCHIVOS_DESPLEGUE.md       - Este archivo
```

#### Utilidades
```
backup_sistema.py           - Sistema de backup completo
```

### 3. ARCHIVOS A EXCLUIR (NO SUBIR A GIT)

Estos archivos están excluidos en .gitignore:

#### Archivos Sensibles
```
.env                        - Variables de entorno locales
*.log                       - Logs del sistema
backups_seguridad/          - Carpeta de backups
__pycache__/                - Caché Python
```

#### Archivos de Desarrollo
```
.vscode/                    - Configuración VS Code
.idea/                      - Configuración PyCharm
*.pyc, *.pyo               - Bytecode Python
```

#### Archivos Temporales
```
*.tmp, *.bak               - Archivos temporales
*.db, *.sqlite             - Bases de datos locales
```

### 4. VERIFICACIÓN DE ARCHIVOS CRÍTICOS

#### Estado Actual Verificado:
- [x] **main.py** - Importado correctamente
- [x] **database.py** - Conexión dual implementada
- [x] **requirements.txt** - Dependencias completas
- [x] **render.yaml** - Configuración Render lista
- [x] **.gitignore** - Exclusiones configuradas
- [x] **streamlit** - Versión 1.55.0 funcionando

#### Conexión a Base de Datos:
- [x] **Local**: Detecta ausencia de DATABASE_URL
- [x] **Producción**: Detecta DATABASE_URL de Render
- [x] **SSL**: sslmode='require' para producción

### 5. CONTENIDO DE ARCHIVOS CLAVE

#### requirements.txt
```
streamlit>=1.28.0
psycopg2-binary>=2.9.0
pandas>=1.5.0
pillow>=9.0.0
python-dotenv>=1.0.0
```

#### render.yaml (Configuración Principal)
```yaml
services:
  - type: web
    name: sicadfoc-2026
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run main.py --server.port $PORT --server.address 0.0.0.0
    healthCheckPath: /
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: PYTHON_VERSION
        value: 3.11
```

#### .gitignore (Exclusiones Principales)
```
__pycache__/
*.pyc
.env
.streamlit/
backups_seguridad/
*.log
*.sql
*.zip
```

### 6. ESTRUCTURA DE CARPETAS RECOMENDADA

```
Proyecto_FOC26.2/
|
|-- main.py                    # Aplicación principal
|-- database.py                # Conexión a BD
|-- seguridad.py               # Permisos
|-- auth_unificado.py          # Autenticación
|-- formacion_complementaria.py
|-- gestion_estudiantil.py
|-- gestion_profesores.py
|-- gestion_carreras.py
|-- gestion_permisos.py
|-- reportes.py
|-- gestor_certificaciones.py
|
|-- requirements.txt           # Dependencias
|-- render.yaml                # Config Render
|-- .gitignore                 # Exclusiones Git
|-- README.md                  # Documentación
|-- DESPLEGUE_RENDER.md        # Guía despliegue
|
|-- sincronizacion_tablas.sql  # Estructura BD
|-- backup_sistema.py          # Backup (opcional)
|
|-- assets/                    # Recursos estáticos
|-- media/                     # Archivos multimedia
```

### 7. PASOS FINALES DE PREPARACIÓN

#### Antes de Subir a GitHub:
1. [ ] Verificar que todos los archivos críticos estén presentes
2. [ ] Confirmar que requirements.txt esté completo
3. [ ] Validar que render.yaml esté configurado
4. [ ] Probar localmente: `streamlit run main.py`
5. [ ] Ejecutar: `git status` para revisar cambios

#### Variables de Entorno en Render:
```
DATABASE_URL = postgresql://username:password@host:port/database
ENVIRONMENT = production
DEBUG = false
```

### 8. COMANDOS DE VERIFICACIÓN

#### Verificar Dependencias:
```bash
pip install -r requirements.txt
```

#### Verificar Aplicación:
```bash
streamlit run main.py
```

#### Verificar Conexión Dual:
```bash
# Local (sin DATABASE_URL)
python -c "from database import db_manager; print('Local OK')"

# Producción (con DATABASE_URL)
export DATABASE_URL="postgresql://..."
python -c "from database import db_manager; print('Producción OK')"
```

### 9. CHECKLIST FINAL DE DESPLIEGUE

#### Archivos Obligatorios para Subir:
- [ ] main.py
- [ ] database.py
- [ ] seguridad.py
- [ ] auth_unificado.py
- [ ] formacion_complementaria.py
- [ ] gestion_estudiantil.py
- [ ] gestion_profesores.py
- [ ] gestion_carreras.py
- [ ] gestion_permisos.py
- [ ] reportes.py
- [ ] gestor_certificaciones.py
- [ ] requirements.txt
- [ ] render.yaml
- [ ] .gitignore
- [ ] sincronizacion_tablas.sql

#### Archivos Opcionales pero Recomendados:
- [ ] README.md
- [ ] DESPLEGUE_RENDER.md
- [ ] backup_sistema.py

#### Configuración en Render:
- [ ] Crear base de datos PostgreSQL
- [ ] Configurar DATABASE_URL
- [ ] Configurar variables de entorno
- [ ] Desplegar desde GitHub

---

**ESTADO**: Todos los archivos críticos están verificados y listos para despliegue.

**PRÓXIMO PASO**: Subir a GitHub y configurar el despliegue en Render siguiendo la guía DESPLEGUE_RENDER.md.
