"""
SEEDERS SQL - DATOS REALES IUJO PARA TABLAS MAESTRAS
DBA Senior - WindSurf
"""
import database
from sqlalchemy import text
import sys

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

print("=== SEEDERS - DATOS IUJO REALES ===")

# Get database engine
engine = database.get_engine_local()

try:
    with engine.connect() as conn:
        # 1. Sedes IUJO
        print("\n--- 1. INSERTANDO SEDES IUJO ---")
        
        sedes_data = [
            (1, 'Sede Catia', 'Av. Principal de Catia, Edif. IUJO', '0212-1234567', 'Activo'),
            (2, 'Sede Petare', 'Urbanización Petare, Calle Principal', '0212-7654321', 'Activo'),
            (3, 'Sede Caracas', 'Av. Universidad, Edif. Central', '0212-5555555', 'Activo')
        ]
        
        for sede in sedes_data:
            conn.execute(text("""
                INSERT OR IGNORE INTO sedes (id_sede, nombre, direccion, telefono, estatus)
                VALUES (:id_sede, :nombre, :direccion, :telefono, :estatus)
            """), {
                'id_sede': sede[0],
                'nombre': sede[1],
                'direccion': sede[2],
                'telefono': sede[3],
                'estatus': sede[4]
            })
            print(f"  ✅ Sede '{sede[1]}' insertada")
        
        # 2. Carreras IUJO
        print("\n--- 2. INSERTANDO CARRERAS IUJO ---")
        
        carreras_data = [
            (1, 'Ingeniería en Informática', 'INF-001', 1, 'Activo'),
            (2, 'Administración de Empresas', 'ADM-001', 1, 'Activo'),
            (3, 'Contaduría Pública', 'CON-001', 2, 'Activo'),
            (4, 'Relaciones Industriales', 'REL-001', 2, 'Activo'),
            (5, 'Ciencias Administrativas', 'CIA-001', 3, 'Activo'),
            (6, 'Sistemas de Información', 'SIS-001', 3, 'Activo')
        ]
        
        for carrera in carreras_data:
            conn.execute(text("""
                INSERT OR IGNORE INTO carreras (id_carrera, nombre, codigo, id_sede, estatus)
                VALUES (:id_carrera, :nombre, :codigo, :id_sede, :estatus)
            """), {
                'id_carrera': carrera[0],
                'nombre': carrera[1],
                'codigo': carrera[2],
                'id_sede': carrera[3],
                'estatus': carrera[4]
            })
            print(f"  ✅ Carrera '{carrera[1]}' insertada")
        
        # 3. Turnos
        print("\n--- 3. INSERTANDO TURNOS ---")
        
        turnos_data = [
            (1, 'Mañana', '6:00 AM - 12:00 PM', 'Activo'),
            (2, 'Tarde', '12:00 PM - 6:00 PM', 'Activo'),
            (3, 'Noche', '6:00 PM - 10:00 PM', 'Activo'),
            (4, 'Fin de Semana', 'Sábado y Domingo', 'Activo')
        ]
        
        for turno in turnos_data:
            conn.execute(text("""
                INSERT OR IGNORE INTO turnos (id_turno, nombre, descripcion, estatus)
                VALUES (:id_turno, :nombre, :descripcion, :estatus)
            """), {
                'id_turno': turno[0],
                'nombre': turno[1],
                'descripcion': turno[2],
                'estatus': turno[3]
            })
            print(f"  ✅ Turno '{turno[1]}' insertado")
        
        # 4. Secciones
        print("\n--- 4. INSERTANDO SECCIONES ---")
        
        secciones_data = [
            (1, '1A', 1, 1, 'Activo'),  # Informática - Mañana
            (2, '1B', 1, 2, 'Activo'),  # Informática - Tarde
            (3, '2A', 2, 1, 'Activo'),  # Administración - Mañana
            (4, '2B', 2, 2, 'Activo'),  # Administración - Tarde
            (5, '3A', 3, 1, 'Activo'),  # Contaduría - Mañana
            (6, '3B', 3, 2, 'Activo'),  # Contaduría - Tarde
            (7, '4A', 4, 1, 'Activo'),  # Relaciones Industriales - Mañana
            (8, '4B', 4, 2, 'Activo'),  # Relaciones Industriales - Tarde
            (9, '5A', 5, 3, 'Activo'),  # Ciencias Admin - Noche
            (10, '6A', 6, 4, 'Activo')  # Sistemas - Fin de Semana
        ]
        
        for seccion in secciones_data:
            conn.execute(text("""
                INSERT OR IGNORE INTO secciones (id_seccion, nombre, id_carrera, id_turno, estatus)
                VALUES (:id_seccion, :nombre, :id_carrera, :id_turno, :estatus)
            """), {
                'id_seccion': seccion[0],
                'nombre': seccion[1],
                'id_carrera': seccion[2],
                'id_turno': seccion[3],
                'estatus': seccion[4]
            })
            print(f"  ✅ Sección '{seccion[1]}' insertada")
        
        # 5. Perfiles
        print("\n--- 5. INSERTANDO PERFILES ---")
        
        perfiles_data = [
            (1, 'Administrador', 'Acceso completo al sistema', 'todos', 'Activo'),
            (2, 'Profesor', 'Gestión de PDF, auditoría, consulta', 'gestion_pdf,auditoria,consulta', 'Activo'),
            (3, 'Estudiante', 'Acceso de consulta básico', 'consulta', 'Activo'),
            (4, 'Secretaría', 'Gestión administrativa básica', 'consulta,registro_basico', 'Activo'),
            (5, 'Coordinador', 'Supervisión y reportes', 'consulta,auditoria,reportes', 'Activo')
        ]
        
        for perfil in perfiles_data:
            conn.execute(text("""
                INSERT OR IGNORE INTO perfiles (id_perfil, nombre, descripcion, permisos, estatus)
                VALUES (:id_perfil, :nombre, :descripcion, :permisos, :estatus)
            """), {
                'id_perfil': perfil[0],
                'nombre': perfil[1],
                'descripcion': perfil[2],
                'permisos': perfil[3],
                'estatus': perfil[4]
            })
            print(f"  ✅ Perfil '{perfil[1]}' insertado")
        
        conn.commit()
        
        # 6. Verificación
        print("\n--- 6. VERIFICACIÓN DE DATOS INSERTADOS ---")
        
        tablas_verificar = ['sedes', 'carreras', 'turnos', 'secciones', 'perfiles']
        
        for tabla in tablas_verificar:
            query_count = f"SELECT COUNT(*) FROM {tabla}"
            count = conn.execute(text(query_count)).scalar()
            print(f"  {tabla}: {count} registros")
        
        print("\n🎉 SEEDERS COMPLETADOS - DATOS IUJO LISTOS")
        
except Exception as e:
    print(f'❌ ERROR: {e}')
    import traceback
    traceback.print_exc()
