"""
ESQUEMA DE ROLES - SICADFOC 2026
Definición de estructura de roles con PostgreSQL y llaves foráneas
DBA Senior & Full-Stack - WindSurf
"""
import logging
from sqlalchemy import create_engine, text

# Importar conexión desde módulo independiente
from .connection import get_engine_local

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Definición de roles y permisos
ROLES_DEFINICION = {
    'Administrador': {
        'id': 1,
        'nombre': 'Administrador',
        'descripcion': 'Acceso completo al sistema',
        'permisos': [
            'usuario.crear', 'usuario.editar', 'usuario.eliminar', 'usuario.ver',
            'rol.crear', 'rol.editar', 'rol.ver',
            'curso.crear', 'curso.editar', 'curso.eliminar', 'curso.ver',
            'taller.crear', 'taller.editar', 'taller.eliminar', 'taller.ver',
            'auditoria.ver', 'sistema.configurar', 'sistema.backup'
        ],
        'nivel_acceso': 100
    },
    'Profesor': {
        'id': 2,
        'nombre': 'Profesor',
        'descripcion': 'Acceso a funciones docentes',
        'permisos': [
            'curso.ver', 'curso.editar_propios',
            'taller.crear', 'taller.editar_propios', 'taller.ver_propios',
            'estudiante.ver', 'estudiante.calificar',
            'auditoria.ver_propia',
            'material.cargar', 'material.editar_propios'
        ],
        'nivel_acceso': 50
    },
    'Estudiante': {
        'id': 3,
        'nombre': 'Estudiante',
        'descripcion': 'Acceso limitado a funciones estudiantiles',
        'permisos': [
            'curso.ver', 'curso.inscribirse',
            'taller.ver', 'taller.inscribirse',
            'material.ver', 'material.descargar',
            'propio.perfil.ver', 'propio.perfil.editar'
        ],
        'nivel_acceso': 10
    }
}

def crear_tablas_roles(engine):
    """Crear tablas de roles y permisos en la base de datos"""
    
    queries = [
        # Tabla de roles
        """
        CREATE TABLE IF NOT EXISTS rol (
            id_rol INTEGER PRIMARY KEY,
            nombre_rol VARCHAR(50) UNIQUE NOT NULL,
            descripcion TEXT,
            nivel_acceso INTEGER DEFAULT 0,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Tabla de permisos
        """
        CREATE TABLE IF NOT EXISTS permiso (
            id_permiso SERIAL PRIMARY KEY,
            nombre_permiso VARCHAR(100) UNIQUE NOT NULL,
            descripcion TEXT,
            modulo VARCHAR(50) NOT NULL,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Tabla de relación roles-permisos
        """
        CREATE TABLE IF NOT EXISTS rol_permiso (
            id_rol INTEGER NOT NULL,
            id_permiso INTEGER NOT NULL,
            concedido_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id_rol, id_permiso),
            FOREIGN KEY (id_rol) REFERENCES rol(id_rol) ON DELETE CASCADE,
            FOREIGN KEY (id_permiso) REFERENCES permiso(id_permiso) ON DELETE CASCADE
        )
        """,
        
        # Tabla de usuarios actualizada con FK a rol
        """
        CREATE TABLE IF NOT EXISTS usuario_temp (
            id INTEGER PRIMARY KEY,
            login VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            contrasena VARCHAR(255) NOT NULL,
            rol VARCHAR(50) DEFAULT 'estudiante',
            activo BOOLEAN DEFAULT TRUE,
            correo_verificado BOOLEAN DEFAULT FALSE,
            id_rol INTEGER,
            id_persona INTEGER,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_rol) REFERENCES rol(id_rol),
            FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
        )
        """,
        
        # Tabla de auditoría de roles
        """
        CREATE TABLE IF NOT EXISTS auditoria_roles (
            id_auditoria SERIAL PRIMARY KEY,
            id_usuario INTEGER NOT NULL,
            accion VARCHAR(50) NOT NULL,
            tabla_afectada VARCHAR(50),
            id_registro_afectado INTEGER,
            valores_antiguos JSONB,
            valores_nuevos JSONB,
            ip_address VARCHAR(45),
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES usuario(id)
        )
        """
    ]
    
    try:
        with engine.connect() as conn:
            for query in queries:
                conn.execute(text(query))
            conn.commit()
        logger.info("✅ Tablas de roles creadas exitosamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error creando tablas de roles: {e}")
        return False

def poblar_roles_y_permisos(engine):
    """Poblar tablas de roles y permisos con datos iniciales"""
    
    try:
        with engine.connect() as conn:
            # Insertar roles
            for rol_key, rol_data in ROLES_DEFINICION.items():
                # Verificar si el rol ya existe
                check_rol = conn.execute(text("SELECT id_rol FROM rol WHERE nombre_rol = :nombre"), 
                                       {'nombre': rol_data['nombre']}).fetchone()
                
                if not check_rol:
                    # Insertar nuevo rol
                    conn.execute(text("""
                        INSERT INTO rol (id_rol, nombre_rol, descripcion, nivel_acceso)
                        VALUES (:id, :nombre, :descripcion, :nivel)
                    """), {
                        'id': rol_data['id'],
                        'nombre': rol_data['nombre'],
                        'descripcion': rol_data['descripcion'],
                        'nivel': rol_data['nivel_acceso']
                    })
                    logger.info(f"✅ Rol '{rol_data['nombre']}' creado")
            
            # Insertar permisos únicos
            permisos_unicos = set()
            for rol_data in ROLES_DEFINICION.values():
                permisos_unicos.update(rol_data['permisos'])
            
            for permiso in permisos_unicos:
                # Extraer módulo y nombre del permiso
                partes = permiso.split('.')
                modulo = partes[0] if len(partes) > 1 else 'general'
                nombre_permiso = permiso
                
                # Verificar si el permiso ya existe
                check_permiso = conn.execute(text("SELECT id_permiso FROM permiso WHERE nombre_permiso = :nombre"), 
                                           {'nombre': nombre_permiso}).fetchone()
                
                if not check_permiso:
                    # Insertar nuevo permiso
                    conn.execute(text("""
                        INSERT INTO permiso (nombre_permiso, descripcion, modulo)
                        VALUES (:nombre, :descripcion, :modulo)
                    """), {
                        'nombre': nombre_permiso,
                        'descripcion': f"Permiso para {permiso.replace('.', ' ')}",
                        'modulo': modulo
                    })
                    logger.info(f"✅ Permiso '{nombre_permiso}' creado")
            
            # Asignar permisos a roles
            for rol_key, rol_data in ROLES_DEFINICION.items():
                rol_id = rol_data['id']
                
                for permiso in rol_data['permisos']:
                    # Obtener ID del permiso
                    permiso_result = conn.execute(text("SELECT id_permiso FROM permiso WHERE nombre_permiso = :nombre"), 
                                                {'nombre': permiso}).fetchone()
                    
                    if permiso_result:
                        permiso_id = permiso_result[0]
                        
                        # Verificar si la relación ya existe
                        check_relacion = conn.execute(text("""
                            SELECT COUNT(*) FROM rol_permiso 
                            WHERE id_rol = :rol AND id_permiso = :permiso
                        """), {'rol': rol_id, 'permiso': permiso_id}).fetchone()[0]
                        
                        if check_relacion == 0:
                            # Insertar relación rol-permiso
                            conn.execute(text("""
                                INSERT INTO rol_permiso (id_rol, id_permiso)
                                VALUES (:rol, :permiso)
                            """), {'rol': rol_id, 'permiso': permiso_id})
                            
                            logger.info(f"✅ Permiso '{permiso}' asignado a rol '{rol_data['nombre']}'")
                    else:
                        logger.warning(f"⚠️ No se encontró permiso '{permiso}'")
            
            conn.commit()
            logger.info("✅ Roles y permisos poblados exitosamente")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error poblando roles y permisos: {e}")
        return False

def migrar_usuarios_a_nuevo_esquema(engine):
    """Migrar usuarios existentes al nuevo esquema de roles"""
    
    try:
        with engine.connect() as conn:
            # Verificar si existe la tabla usuario original
            check_tabla = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='usuario'
            """)).fetchone()
            
            if check_tabla:
                # Obtener usuarios existentes
                usuarios = conn.execute(text("SELECT id, email, rol FROM usuario")).fetchall()
                
                for usuario in usuarios:
                    id_usuario = usuario[0]
                    email = usuario[1]
                    rol_actual = usuario[2].lower()
                    
                    # Mapear rol actual a nuevo ID
                    rol_id_mapping = {
                        'administrador': 1,
                        'profesor': 2,
                        'estudiante': 3
                    }
                    
                    id_rol = rol_id_mapping.get(rol_actual, 3)  # Default a estudiante
                    
                    # Actualizar usuario con nuevo rol
                    conn.execute(text("""
                        UPDATE usuario 
                        SET id_rol = :id_rol 
                        WHERE id = :id_usuario
                    """), {'id_rol': id_rol, 'id_usuario': id_usuario})
                    
                    logger.info(f"✅ Usuario {email} migrado a rol {rol_actual} (ID: {id_rol})")
                
                conn.commit()
                logger.info("✅ Migración de usuarios completada")
                return True
            else:
                logger.info("ℹ️ No se encontró tabla usuario para migrar")
                return True
                
    except Exception as e:
        logger.error(f"❌ Error en migración de usuarios: {e}")
        return False

def verificar_estructura_roles(engine):
    """Verificar que la estructura de roles esté correctamente implementada"""
    
    try:
        with engine.connect() as conn:
            # Verificar tablas
            tablas_requeridas = ['rol', 'permiso', 'rol_permiso', 'auditoria_roles']
            tablas_existentes = []
            
            for tabla in tablas_requeridas:
                check = conn.execute(text(f"""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='{tabla}'
                """)).fetchone()
                
                if check:
                    tablas_existentes.append(tabla)
            
            # Verificar roles
            roles = conn.execute(text("SELECT id_rol, nombre_rol FROM rol ORDER BY id_rol")).fetchall()
            
            # Verificar permisos por rol
            permisos_por_rol = {}
            for rol in roles:
                id_rol, nombre_rol = rol
                permisos = conn.execute(text("""
                    SELECT p.nombre_permiso 
                    FROM permiso p
                    JOIN rol_permiso rp ON p.id_permiso = rp.id_permiso
                    WHERE rp.id_rol = :id_rol
                    ORDER BY p.modulo, p.nombre_permiso
                """), {'id_rol': id_rol}).fetchall()
                
                permisos_por_rol[nombre_rol] = [p[0] for p in permisos]
            
            return {
                'tablas_creadas': tablas_existentes,
                'roles_existentes': roles,
                'permisos_por_rol': permisos_por_rol,
                'estructura_completa': len(tablas_existentes) == len(tablas_requeridas)
            }
            
    except Exception as e:
        logger.error(f"❌ Error verificando estructura de roles: {e}")
        return None

def inicializar_sistema_roles(engine):
    """Función principal para inicializar todo el sistema de roles"""
    
    logger.info("🚀 Inicializando sistema de roles...")
    
    # 1. Crear tablas
    if not crear_tablas_roles(engine):
        return False
    
    # 2. Poblar roles y permisos
    if not poblar_roles_y_permisos(engine):
        return False
    
    # 3. Migrar usuarios existentes
    if not migrar_usuarios_a_nuevo_esquema(engine):
        return False
    
    # 4. Verificar estructura
    verificacion = verificar_estructura_roles(engine)
    
    if verificacion and verificacion['estructura_completa']:
        logger.info("✅ Sistema de roles inicializado correctamente")
        return True
    else:
        logger.error("❌ Error en la inicialización del sistema de roles")
        return False

if __name__ == "__main__":
    # Ejecutar inicialización
    engine = get_engine_local()
    exito = inicializar_sistema_roles(engine)
    
    if exito:
        print("🎉 Sistema de roles inicializado exitosamente")
    else:
        print("❌ Error en la inicialización del sistema de roles")
