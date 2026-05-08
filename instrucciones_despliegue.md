# Instrucciones para Replicar Base de Datos en Producción

## 🚀 Pasos para Configurar la Base de Datos en Render

### 1. Ejecutar Script de Migración

#### Opción A: Via Panel de Render
1. Inicia sesión en [Render Dashboard](https://dashboard.render.com)
2. Ve a tu servicio de base de datos PostgreSQL
3. Haz clic en "Query" o "SQL Shell"
4. Copia y pega el contenido del archivo `migrar_produccion.sql`
5. Ejecuta el script

#### Opción B: Via psql (Terminal)
```bash
# Conectar a la base de datos de Render
psql "postgresql://foc26db_user:IZfArPXgOciy8iKsiRDbOosUiR7BAc8u@dpg-d7gfpi28qa3s73ci36d0-a.oregon-postgres.render.com/foc26db"

# Ejecutar el script
\i migrar_produccion.sql
```

### 2. Verificar Usuarios Creados

Después de ejecutar el script, deberías ver:

```
 id | username    |     rol      | activo | login_usuario | cedula_usuario |        email        
----+-------------+--------------+--------+---------------+----------------+--------------------
  1 | jmontezuma  | Administrador| t      | jmontezuma    | 5.430.424      | jmontezuma@foc26.edu.ve
  2 | ahernandez  | Administrador| t      | ahernandez    | 14.300.385     | ahernandez@foc26.edu.ve
  3 | profesor    | Profesor     | t      | profesor      | V-12345678     | profesor@foc26.edu.ve
  4 | estudiante  | Estudiante   | t      | estudiante    | V-87654321     | estudiante@foc26.edu.ve
```

### 3. Credenciales de Acceso

| Usuario | Contraseña | Cédula | Rol | Acceso |
|---------|------------|--------|-----|--------|
| jmontezuma | admin123456 | 5.430.424 | Administrador | Acceso completo a todos los módulos |
| ahernandez | admin123 | 14.300.385 | Administrador | Acceso completo a todos los módulos |
| profesor | profesor123 | V-12345678 | Profesor | Gestión de talleres |
| estudiante | estudiante123 | V-87654321 | Estudiante | Inscripciones y consultas |

### 4. Configurar Variables de Entorno en Render

En tu servicio de Streamlit en Render, asegúrate de tener:

```
DATABASE_URL=postgresql://foc26db_user:IZfArPXgOciy8iKsiRDbOosUiR7BAc8u@dpg-d7gfpi28qa3s73ci36d0-a.oregon-postgres.render.com/foc26db
```

### 5. Desplegar la Aplicación

Sube los archivos esenciales a Render:

1. **Archivos principales**:
   - main.py
   - database.py
   - config.py
   - auth_unificado.py
   - seguridad.py
   - Todos los módulos .py

2. **Configuración**:
   - requirements.txt
   - Procfile
   - runtime.txt
   - render.yaml

### 6. Primer Acceso

1. Visita la URL de tu aplicación en Render
2. Inicia sesión con uno de los administradores:

**Opción A: Jose Montezuma**
- Usuario: `jmontezuma`
- Contraseña: `admin123456`
- Cédula: `5.430.424`

**Opción B: Angel Hernandez**
- Usuario: `ahernandez`
- Contraseña: `admin123`
- Cédula: `14.300.385`

Ambos usuarios tienen acceso completo a todos los módulos sin restricciones.

### 7. Pasos Siguientes

1. **Cambiar contraseñas** de los usuarios iniciales
2. **Crear usuarios reales** según necesites
3. **Configurar permisos** según los roles
4. **Verificar módulos** funcionen correctamente

---

## 🛠️ Solución de Problemas

### Error: "column does not exist"
- **Causa**: El script de migración no se ejecutó
- **Solución**: Ejecuta `migrar_produccion.sql` completamente

### Error: "no such user"
- **Causa**: Los usuarios no se crearon
- **Solución**: Verifica la salida del script, reejecuta si es necesario

### Error: "authentication failed"
- **Causa**: Contraseña incorrecta
- **Solución**: Usa las contraseñas por defecto: admin123, profesor123, estudiante123

---

## 📋 Checklist de Despliegue

- [ ] Ejecutar script de migración SQL
- [ ] Verificar usuarios creados (3 usuarios)
- [ ] Configurar DATABASE_URL en Render
- [ ] Subir archivos esenciales
- [ ] Probar acceso con usuario admin
- [ ] Cambiar contraseñas por defecto
- [ ] Crear usuarios reales
- [ ] Verificar todos los módulos funcionen

---

## 🎯 Confirmación Final

Cuando veas este resultado en la consulta SQL, la migración está completa:

```
              estado              | total_usuarios | administradores | profesores | estudiantes
----------------------------------+----------------+-----------------+------------+-------------
 Migración completada              |              3 |               1 |          1 |           1
```

¡Tu aplicación estará lista para producción!
