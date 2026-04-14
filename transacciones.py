#!/usr/bin/env python3
# Módulo de Lógica Transaccional para SICADFOC 2026

import psycopg2
from datetime import datetime
import json
import uuid

class TransaccionFOC26:
    """Clase para manejar transacciones FOC-2026-XXXX"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        
    def _obtener_id_por_nombre(self, tabla, columna_id, columna_nombre, valor):
        """Obtener un id referenciado por su nombre en tablas de valor."""
        try:
            if not valor:
                return None
            with self.db.cursor() as cursor:
                cursor.execute(
                    f"SELECT {columna_id} FROM {tabla} WHERE LOWER({columna_nombre}) = LOWER(%s) LIMIT 1",
                    (valor.strip(),)
                )
                fila = cursor.fetchone()
                return fila[columna_id] if fila else None
        except Exception:
            return None

    def obtener_id_carrera(self, nombre_carrera):
        return self._obtener_id_por_nombre('carrera', 'id_carrera', 'nombre_carrera', nombre_carrera)

    def obtener_id_semestre(self, nombre_semestre):
        return self._obtener_id_por_nombre('semestre', 'id_semestre', 'nombre_semestre', nombre_semestre)

    def obtener_id_estado_registro(self, estado):
        return self._obtener_id_por_nombre('val_estado_registro', 'id_estado', 'estado', estado)

    def obtener_id_sexo(self, sexo):
        return self._obtener_id_por_nombre('val_sexo', 'id_sexo', 'sexo', sexo)

    def generar_id_transaccion(self):
        """Generar ID de transacción único FOC-2026-XXXX"""
        timestamp = datetime.now().strftime("%Y%m%d")
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"FOC-{timestamp}-{random_suffix}"
    
    def registrar_transaccion(self, tipo, descripcion, id_usuario=None, detalles=None):
        """Registrar transacción en el sistema"""
        try:
            with self.db.cursor() as cursor:
                id_transaccion = self.generar_id_transaccion()
                
                # Insertar en tabla de auditoría
                cursor.execute("""
                    INSERT INTO auditoria (id_transaccion, tipo_transaccion, descripcion, id_usuario, detalles, fecha_hora)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (id_transaccion, tipo, descripcion, id_usuario, detalles, datetime.now()))
                
                self.db.commit()
                print(f"Transacción registrada: {id_transaccion} - {descripcion}")
                return id_transaccion
                
        except Exception as e:
            self.db.rollback()
            print(f"Error registrando transacción: {e}")
            return None

    def validar_cedula_perfil(self, cedula, rol_objetivo):
        """Validar que la cédula no exista ya en un perfil con rol distinto."""
        try:
            cedula = str(cedula).strip()
            with self.db.cursor() as cursor:
                cursor.execute(
                    "SELECT u.rol FROM usuario u JOIN persona p ON u.id_persona = p.id WHERE p.cedula = %s",
                    (cedula,)
                )
                existente = cursor.fetchone()
                if existente:
                    if existente['rol'] != rol_objetivo:
                        return False, f"La cédula ya existe como {existente['rol']}"
                    return False, f"La cédula ya existe como {rol_objetivo}"
                return True, None
        except Exception as e:
            print(f"Error validando cédula: {e}")
            return False, str(e)

    def crear_estudiante_transaccional(self, datos_estudiante):
        """Crear estudiante con control transaccional"""
        try:
            cedula = str(datos_estudiante['cedula']).strip()
            valido, error = self.validar_cedula_perfil(cedula, 'Estudiante')
            if not valido:
                return {
                    'id_transaccion': None,
                    'id_persona': None,
                    'id_usuario': None,
                    'exito': False,
                    'error': error
                }

            with self.db.cursor() as cursor:
                id_transaccion = self.generar_id_transaccion()
                cursor.execute("BEGIN")

                # 1. Insertar en tabla persona
                cursor.execute("""
                    INSERT INTO persona (nombre, apellido, email, cedula, telefono, fecha_nacimiento, genero, direccion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    datos_estudiante['nombre'],
                    datos_estudiante['apellido'],
                    datos_estudiante['email'],
                    cedula,
                    datos_estudiante['telefono'],
                    datos_estudiante['fecha_nacimiento'],
                    datos_estudiante['genero'],
                    datos_estudiante['direccion']
                ))

                id_persona = cursor.fetchone()['id']

                # 2. Insertar en tabla usuario usando cédula como login y contraseña temporal
                cursor.execute("""
                    INSERT INTO usuario (id_persona, cedula_usuario, login_usuario, email, contrasena, rol, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    id_persona,
                    cedula,
                    cedula,
                    datos_estudiante['email'],
                    cedula,
                    'Estudiante',
                    True
                ))

                id_usuario = cursor.fetchone()['id']

                # 3. Insertar en tabla estudiante usando el esquema local vigente
                id_sexo = self.obtener_id_sexo(datos_estudiante.get('genero'))
                id_carrera = self.obtener_id_carrera(datos_estudiante.get('carrera'))
                id_semestre = self.obtener_id_semestre(datos_estudiante.get('semestre_actual'))
                id_estado = self.obtener_id_estado_registro(datos_estudiante.get('estado'))

                cursor.execute("""
                    INSERT INTO estudiante (
                        cedula_estudiante,
                        nombres,
                        apellidos,
                        id_sexo,
                        telefono,
                        correo,
                        id_carrera,
                        id_semestre_formacion,
                        id_estado_registro,
                        id_usuario,
                        id_persona
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    datos_estudiante.get('codigo_estudiantil', cedula),
                    datos_estudiante['nombre'],
                    datos_estudiante['apellido'],
                    id_sexo,
                    datos_estudiante.get('telefono'),
                    datos_estudiante.get('email'),
                    id_carrera,
                    id_semestre,
                    id_estado,
                    id_usuario,
                    id_persona
                ))

                # 4. Registrar transacción
                cursor.execute("""
                    INSERT INTO auditoria (id_transaccion, tipo_transaccion, descripcion, id_usuario, detalles, fecha_hora)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    id_transaccion,
                    'CREAR_ESTUDIANTE',
                    f'Creación de estudiante: {datos_estudiante["nombre"]} {datos_estudiante["apellido"]}',
                    id_usuario,
                    f'Carrera: {datos_estudiante["carrera"]}, Semestre: {datos_estudiante["semestre_actual"]}',
                    datetime.now()
                ))

                self.db.commit()
                print(f"Estudiante creado transaccionalmente: {id_transaccion}")
                return {
                    'id_transaccion': id_transaccion,
                    'id_persona': id_persona,
                    'id_usuario': id_usuario,
                    'exito': True
                }

        except Exception as e:
            self.db.rollback()
            print(f"Error en transacción de estudiante: {e}")
            return {
                'id_transaccion': None,
                'id_persona': None,
                'id_usuario': None,
                'exito': False,
                'error': str(e)
            }

    def crear_profesor_transaccional(self, datos_profesor):
        """Crear profesor con control transaccional"""
        try:
            cedula = str(datos_profesor['cedula']).strip()
            valido, error = self.validar_cedula_perfil(cedula, 'Profesor')
            if not valido:
                return {
                    'id_transaccion': None,
                    'id_persona': None,
                    'id_usuario': None,
                    'id_profesor': None,
                    'exito': False,
                    'error': error
                }

            with self.db.cursor() as cursor:
                id_transaccion = self.generar_id_transaccion()
                cursor.execute("BEGIN")

                cursor.execute("""
                    INSERT INTO persona (nombre, apellido, email, cedula, telefono, direccion)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    datos_profesor['nombre'],
                    datos_profesor['apellido'],
                    datos_profesor['email'],
                    cedula,
                    datos_profesor['telefono'],
                    datos_profesor.get('direccion')
                ))
                id_persona = cursor.fetchone()['id']

                cursor.execute("""
                    INSERT INTO usuario (id_persona, cedula_usuario, login_usuario, email, contrasena, rol, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    id_persona,
                    cedula,
                    cedula,
                    datos_profesor['email'],
                    cedula,
                    'Profesor',
                    True
                ))
                id_usuario = cursor.fetchone()['id']

                cursor.execute("""
                    INSERT INTO profesor (id_persona, id_usuario, cedula_profesor, correo_personal, codigo_profesor, especialidad, departamento, categoria, estado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_profesor
                """, (
                    id_persona,
                    id_usuario,
                    cedula,
                    datos_profesor.get('correo_personal'),
                    datos_profesor.get('codigo_profesor'),
                    datos_profesor.get('especialidad'),
                    datos_profesor.get('departamento'),
                    datos_profesor.get('categoria'),
                    datos_profesor.get('estado', 'Activo')
                ))
                id_profesor = cursor.fetchone()['id_profesor']

                cursor.execute("""
                    INSERT INTO auditoria (id_transaccion, tipo_transaccion, descripcion, id_usuario, detalles, fecha_hora)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    id_transaccion,
                    'CREAR_PROFESOR',
                    f'Creación de profesor: {datos_profesor["nombre"]} {datos_profesor["apellido"]}',
                    id_usuario,
                    f'Especialidad: {datos_profesor.get("especialidad")}, Departamento: {datos_profesor.get("departamento")}',
                    datetime.now()
                ))

                self.db.commit()
                return {
                    'id_transaccion': id_transaccion,
                    'id_persona': id_persona,
                    'id_usuario': id_usuario,
                    'id_profesor': id_profesor,
                    'exito': True
                }
        except Exception as e:
            self.db.rollback()
            print(f"Error en transacción de profesor: {e}")
            return {
                'id_transaccion': None,
                'id_persona': None,
                'id_usuario': None,
                'id_profesor': None,
                'exito': False,
                'error': str(e)
            }

    def crear_taller_transaccional(self, datos_taller, cedula_profesor=None, horarios=None):
        """Crear taller y formación programada con profesor por cédula."""
        try:
            with self.db.cursor() as cursor:
                id_transaccion = self.generar_id_transaccion()
                cursor.execute("BEGIN")

                instructor_text = None
                if cedula_profesor:
                    profesor = self.obtener_profesor_por_cedula(cedula_profesor)
                    if profesor:
                        instructor_text = f"{profesor['cedula_profesor']} - {profesor['nombre']} {profesor['apellido']}"
                    else:
                        instructor_text = str(cedula_profesor).strip()

                horario_detalle = None
                if horarios:
                    horario_detalle = '; '.join([f"{h['dia_semana']} {h['hora_inicio']}-{h['hora_fin']}" for h in horarios])

                descripcion_ampliada = datos_taller.get('descripcion', '')
                if horario_detalle:
                    descripcion_ampliada = f"{descripcion_ampliada}\nHorario: {horario_detalle}" if descripcion_ampliada else f"Horario: {horario_detalle}"
                if datos_taller.get('codigo'):
                    descripcion_ampliada = f"Código: {datos_taller['codigo']}\n{descripcion_ampliada}" if descripcion_ampliada else f"Código: {datos_taller['codigo']}"

                cursor.execute(
                    "INSERT INTO taller (id_tipo_taller, nombre_taller, ampliacion, id_estado_registro) VALUES (%s, %s, %s, %s) RETURNING id_taller",
                    (
                        1,
                        datos_taller['nombre_taller'],
                        descripcion_ampliada,
                        1
                    )
                )
                id_taller = cursor.fetchone()['id_taller']

                cursor.execute(
                    "INSERT INTO formacion (id_taller, codigo_cohorte, nombre_cohorte, descripcion, fecha_inicio, fecha_fin, cupos_maximos, cupos_disponibles, instructor, estado, observacion_estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_formacion",
                    (
                        id_taller,
                        datos_taller['codigo'],
                        datos_taller['nombre_taller'],
                        datos_taller.get('descripcion'),
                        datos_taller['fecha_inicio'],
                        datos_taller['fecha_fin'],
                        datos_taller.get('cupos_maximos', 30),
                        datos_taller.get('cupos_maximos', 30),
                        instructor_text,
                        datos_taller.get('estado', 'Activo'),
                        datos_taller.get('observacion_estado', 'Creado automáticamente')
                    )
                )
                id_formacion = cursor.fetchone()['id_formacion']

                cursor.execute(
                    "INSERT INTO auditoria (id_transaccion, tipo_transaccion, accion, tabla_afectada, registro_id, valores_nuevos, fecha_accion) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (
                        id_transaccion,
                        'CREAR_TALLER',
                        f'Creación de taller y formación: {datos_taller["nombre_taller"]}',
                        'taller/formacion',
                        id_formacion,
                        json.dumps({'codigo': datos_taller['codigo'], 'nombre_taller': datos_taller['nombre_taller'], 'profesor': instructor_text}),
                        datetime.now()
                    )
                )

                self.db.commit()
                return {
                    'id_transaccion': id_transaccion,
                    'id_taller': id_taller,
                    'id_formacion': id_formacion,
                    'exito': True
                }
        except Exception as e:
            self.db.rollback()
            print(f"Error en transacción de taller: {e}")
            return {
                'id_transaccion': None,
                'id_taller': None,
                'id_formacion': None,
                'exito': False,
                'error': str(e)
            }

    def inscribir_estudiante_taller_transaccional(self, id_usuario, id_formacion):
        """Inscribir estudiante en una formación con control transaccional"""
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    "SELECT estado, cupos_disponibles FROM formacion WHERE id_formacion = %s",
                    (id_formacion,)
                )
                formacion = cursor.fetchone()
                if not formacion:
                    return {'exito': False, 'error': 'Formación no encontrada'}
                if formacion['estado'] != 'Activo':
                    return {'exito': False, 'error': 'La formación no está activa'}
                if formacion['cupos_disponibles'] <= 0:
                    return {'exito': False, 'error': 'No hay cupos disponibles'}

                cursor.execute(
                    "SELECT 1 FROM inscripcion WHERE id_usuario = %s AND id_formacion = %s",
                    (id_usuario, id_formacion)
                )
                if cursor.fetchone():
                    return {'exito': False, 'error': 'El estudiante ya está inscrito en esta formación'}

                id_transaccion = self.generar_id_transaccion()
                cursor.execute("BEGIN")

                cursor.execute(
                    "INSERT INTO inscripcion (id_formacion, id_usuario, fecha_inscripcion, estado) VALUES (%s, %s, %s, %s) RETURNING id_inscripcion",
                    (
                        id_formacion,
                        id_usuario,
                        datetime.now(),
                        'Activa'
                    )
                )

                id_inscripcion = cursor.fetchone()['id_inscripcion']
                cursor.execute(
                    "UPDATE formacion SET cupos_disponibles = cupos_disponibles - 1, actualizado_en = CURRENT_TIMESTAMP WHERE id_formacion = %s",
                    (id_formacion,)
                )

                cursor.execute(
                    "INSERT INTO auditoria (id_transaccion, tipo_transaccion, accion, tabla_afectada, registro_id, valores_nuevos, fecha_accion) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (
                        id_transaccion,
                        'INSCRIPCION_FORMACION',
                        f'Inscripción en formación - Usuario: {id_usuario}, Formación: {id_formacion}',
                        'inscripcion',
                        id_inscripcion,
                        json.dumps({'id_usuario': id_usuario, 'id_formacion': id_formacion}),
                        datetime.now()
                    )
                )

                self.db.commit()
                return {
                    'id_transaccion': id_transaccion,
                    'id_inscripcion': id_inscripcion,
                    'exito': True
                }
        except Exception as e:
            self.db.rollback()
            print(f"Error en inscripción transaccional: {e}")
            return {
                'id_transaccion': None,
                'id_inscripcion': None,
                'exito': False,
                'error': str(e)
            }
    
    def consultar_transacciones_usuario(self, id_usuario, fecha_inicio=None, fecha_fin=None):
        """Consultar transacciones de un usuario"""
        try:
            with self.db.cursor() as cursor:
                query = """
                    SELECT id_transaccion, tipo_transaccion, descripcion, fecha_hora, detalles
                    FROM auditoria
                    WHERE id_usuario = %s
                """
                params = [id_usuario]
                
                if fecha_inicio:
                    query += " AND fecha_hora >= %s"
                    params.append(fecha_inicio)
                    
                if fecha_fin:
                    query += " AND fecha_hora <= %s"
                    params.append(fecha_fin)
                    
                query += " ORDER BY fecha_hora DESC"
                
                cursor.execute(query, params)
                transacciones = cursor.fetchall()
                
                return transacciones
                
        except Exception as e:
            print(f"Error consultando transacciones: {e}")
            return []
    
    def obtener_resumen_transacciones(self, fecha_inicio=None, fecha_fin=None):
        """Obtener resumen de transacciones del sistema"""
        try:
            with self.db.cursor() as cursor:
                query = """
                    SELECT tipo_transaccion, COUNT(*) as total
                    FROM auditoria
                    WHERE 1=1
                """
                params = []
                
                if fecha_inicio:
                    query += " AND fecha_hora >= %s"
                    params.append(fecha_inicio)
                    
                if fecha_fin:
                    query += " AND fecha_hora <= %s"
                    params.append(fecha_fin)
                    
                query += " GROUP BY tipo_transaccion ORDER BY total DESC"
                
                cursor.execute(query, params)
                resumen = cursor.fetchall()
                
                return resumen
                
        except Exception as e:
            print(f"Error en resumen de transacciones: {e}")
            return []

    def obtener_usuario_por_cedula(self, cedula):
        """Obtener registro de usuario usando cédula como llave principal"""
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    "SELECT u.* FROM usuario u JOIN persona p ON u.id_persona = p.id WHERE p.cedula = %s",
                    (cedula.strip(),)
                )
                return cursor.fetchone()
        except Exception as e:
            print(f"Error obteniendo usuario por cédula: {e}")
            return None

    def buscar_estudiantes(self, cedula=None, nombre=None, carrera=None, semestre=None):
        """Buscar estudiantes con filtros dinámicos usando coincidencia parcial."""
        try:
            with self.db.cursor() as cursor:
                query = """
                    SELECT p.id, p.nombre, p.apellido, p.cedula, p.email, p.telefono,
                           u.login_usuario, e.cedula_estudiante, c.nombre_carrera AS carrera,
                           s.nombre_semestre AS semestre_actual, v.estado AS estado
                    FROM persona p
                    JOIN usuario u ON p.id = u.id_persona
                    JOIN estudiante e ON u.id = e.id_usuario
                    LEFT JOIN carrera c ON e.id_carrera = c.id_carrera
                    LEFT JOIN semestre s ON e.id_semestre_formacion = s.id_semestre
                    LEFT JOIN val_estado_registro v ON e.id_estado_registro = v.id_estado
                    WHERE u.rol = 'Estudiante'
                """
                params = []

                if cedula:
                    query += " AND p.cedula ILIKE %s"
                    params.append(f"%{str(cedula).strip()}%")
                if nombre:
                    query += " AND (p.nombre ILIKE %s OR p.apellido ILIKE %s)"
                    params.extend([f"%{nombre}%", f"%{nombre}%"])
                if carrera:
                    query += " AND c.nombre_carrera ILIKE %s"
                    params.append(f"%{carrera}%")
                if semestre:
                    query += " AND s.nombre_semestre ILIKE %s"
                    params.append(f"%{semestre}%")

                query += " ORDER BY p.apellido, p.nombre"
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error buscando estudiantes: {e}")
            return []

    def buscar_profesores(self, cedula=None, nombre=None, departamento=None):
        """Buscar profesores con filtros dinámicos usando coincidencia parcial."""
        try:
            with self.db.cursor() as cursor:
                query = """
                    SELECT p.id, p.nombre, p.apellido, p.cedula, p.email, p.telefono,
                           u.login_usuario, pr.id_profesor, pr.cedula_profesor, pr.correo_personal, pr.codigo_profesor, pr.especialidad, pr.departamento, pr.categoria, pr.estado
                    FROM persona p
                    JOIN usuario u ON p.id = u.id_persona
                    JOIN profesor pr ON pr.id_persona = p.id
                    WHERE u.rol = 'Profesor'
                """
                params = []

                if cedula:
                    query += " AND p.cedula ILIKE %s"
                    params.append(f"%{str(cedula).strip()}%")
                if nombre:
                    query += " AND (p.nombre ILIKE %s OR p.apellido ILIKE %s)"
                    params.extend([f"%{nombre}%", f"%{nombre}%"])
                if departamento:
                    query += " AND pr.departamento ILIKE %s"
                    params.append(f"%{departamento}%")

                query += " ORDER BY p.apellido, p.nombre"
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error buscando profesores: {e}")
            return []

    def obtener_profesores_activos(self):
        """Devuelve profesores activos para selección de instructor."""
        try:
            with self.db.cursor() as cursor:
                cursor.execute("""
                    SELECT pr.id_profesor, pr.cedula_profesor, p.nombre, p.apellido, pr.especialidad, pr.departamento
                    FROM profesor pr
                    JOIN persona p ON pr.id_persona = p.id
                    JOIN usuario u ON pr.id_usuario = u.id
                    WHERE u.activo = TRUE AND pr.estado = 'Activo'
                    ORDER BY p.apellido, p.nombre
                """)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error obteniendo profesores activos: {e}")
            return []

    def obtener_profesor_por_cedula(self, cedula):
        """Obtener datos de profesor usando cédula como identificador."""
        try:
            cedula = str(cedula).strip()
            with self.db.cursor() as cursor:
                cursor.execute("""
                    SELECT pr.*, p.nombre, p.apellido, p.cedula, p.email as email_personal, u.email as email_institucional, u.id AS id_usuario
                    FROM profesor pr
                    JOIN persona p ON pr.id_persona = p.id
                    JOIN usuario u ON pr.id_usuario = u.id
                    WHERE pr.cedula_profesor = %s
                """, (cedula,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error obteniendo profesor por cédula: {e}")
            return None

    def obtener_estudiante_por_cedula(self, cedula):
        """Obtener datos de estudiante usando cédula como identificador."""
        try:
            cedula = str(cedula).strip()
            with self.db.cursor() as cursor:
                cursor.execute("""
                    SELECT e.*, p.nombre, p.apellido, p.cedula, p.email as email_personal, u.email as email_institucional, u.id AS id_usuario
                    FROM estudiante e
                    JOIN usuario u ON e.id_usuario = u.id
                    JOIN persona p ON e.id_persona = p.id
                    WHERE p.cedula = %s
                """, (cedula,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error obteniendo estudiante por cédula: {e}")
            return None

    def generar_codigo_certificado(self):
        """Generar un código correlativo de certificado basado en el año actual."""
        try:
            with self.db.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as total FROM certificado")
                contador = cursor.fetchone()['total'] or 0
                next_num = contador + 1
                return f"CERT-{datetime.now().year}-{next_num:04d}"
        except Exception as e:
            print(f"Error generando código de certificado: {e}")
            return f"CERT-{datetime.now().year}-0000"

    def crear_formacion(self, datos_formacion, horarios=None, carreras_autorizadas=None, semestres_autorizados=None):
        """Crear una nueva formación con horarios y autorizaciones"""
        try:
            with self.db.cursor() as cursor:
                cursor.execute("BEGIN")

                cursor.execute(
                    "INSERT INTO formacion (id_taller, codigo_cohorte, nombre_cohorte, descripcion, fecha_inicio, fecha_fin, cupos_maximos, cupos_disponibles, instructor, estado, observacion_estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_formacion",
                    (
                        datos_formacion['id_taller'],
                        datos_formacion['codigo_cohorte'],
                        datos_formacion['nombre_cohorte'],
                        datos_formacion.get('descripcion'),
                        datos_formacion['fecha_inicio'],
                        datos_formacion['fecha_fin'],
                        datos_formacion.get('cupos_maximos', 30),
                        datos_formacion.get('cupos_maximos', 30),
                        datos_formacion.get('instructor'),
                        datos_formacion.get('estado', 'Activo'),
                        datos_formacion.get('observacion_estado')
                    )
                )
                id_formacion = cursor.fetchone()['id_formacion']

                if horarios:
                    for horario in horarios:
                        cursor.execute(
                            "INSERT INTO horario_formacion (id_formacion, dia_semana, hora_inicio, hora_fin) VALUES (%s, %s, %s, %s)",
                            (
                                id_formacion,
                                horario['dia_semana'],
                                horario['hora_inicio'],
                                horario['hora_fin']
                            )
                        )

                if carreras_autorizadas or semestres_autorizados:
                    cursor.execute(
                        "INSERT INTO solicitud_taller (id_usuario, titulo_propuesto, descripcion, tipo_taller, carreras_autorizadas, semestres_autorizados, estado, observacion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (
                            None,
                            datos_formacion['nombre_cohorte'],
                            datos_formacion.get('descripcion'),
                            datos_formacion.get('tipo_taller'),
                            ','.join(carreras_autorizadas) if carreras_autorizadas else None,
                            ','.join(semestres_autorizados) if semestres_autorizados else None,
                            'Aceptada',
                            'Creado desde solicitud de formación'
                        )
                    )

                self.db.commit()
                return {
                    'exito': True,
                    'id_formacion': id_formacion
                }
        except Exception as e:
            self.db.rollback()
            print(f"Error creando formación: {e}")
            return {
                'exito': False,
                'error': str(e)
            }

    def actualizar_formacion(self, id_formacion, datos_actualizados, horarios=None):
        """Actualizar formación y horarios vinculados"""
        try:
            with self.db.cursor() as cursor:
                cursor.execute("BEGIN")

                set_clauses = []
                params = []
                for key, value in datos_actualizados.items():
                    set_clauses.append(f"{key} = %s")
                    params.append(value)

                if set_clauses:
                    params.append(id_formacion)
                    cursor.execute(
                        f"UPDATE formacion SET {', '.join(set_clauses)}, actualizado_en = CURRENT_TIMESTAMP WHERE id_formacion = %s",
                        params
                    )

                if horarios is not None:
                    cursor.execute("DELETE FROM horario_formacion WHERE id_formacion = %s", (id_formacion,))
                    for horario in horarios:
                        cursor.execute(
                            "INSERT INTO horario_formacion (id_formacion, dia_semana, hora_inicio, hora_fin) VALUES (%s, %s, %s, %s)",
                            (
                                id_formacion,
                                horario['dia_semana'],
                                horario['hora_inicio'],
                                horario['hora_fin']
                            )
                        )

                self.db.commit()
                return {'exito': True, 'id_formacion': id_formacion}
        except Exception as e:
            self.db.rollback()
            print(f"Error actualizando formación: {e}")
            return {'exito': False, 'error': str(e)}

    def cambiar_estado_formacion(self, id_formacion, nuevo_estado, observacion):
        """Cambiar estado de una formación y registrar la observación obligatoria"""
        if not observacion or observacion.strip() == '':
            return {'exito': False, 'error': 'Observación obligatoria para el cambio de estado'}

        try:
            with self.db.cursor() as cursor:
                cursor.execute("BEGIN")
                cursor.execute(
                    "UPDATE formacion SET estado = %s, observacion_estado = %s, actualizado_en = CURRENT_TIMESTAMP WHERE id_formacion = %s",
                    (nuevo_estado, observacion.strip(), id_formacion)
                )
                self.db.commit()
                return {'exito': True, 'id_formacion': id_formacion}
        except Exception as e:
            self.db.rollback()
            print(f"Error cambiando estado de formación: {e}")
            return {'exito': False, 'error': str(e)}

    def asignar_nota(self, cedula, id_formacion, id_evaluacion, calificacion, observaciones=None):
        """Asignar nota a un estudiante por evaluación usando cédula como llave"""
        try:
            usuario = self.obtener_usuario_por_cedula(cedula)
            if not usuario:
                return {'exito': False, 'error': 'Usuario no encontrado'}

            with self.db.cursor() as cursor:
                cursor.execute("BEGIN")
                cursor.execute(
                    "SELECT id_inscripcion FROM inscripcion WHERE id_usuario = %s AND id_formacion = %s",
                    (usuario['id_usuario'], id_formacion)
                )
                registro = cursor.fetchone()
                if not registro:
                    self.db.rollback()
                    return {'exito': False, 'error': 'Inscripción no encontrada para la formación'}

                id_inscripcion = registro['id_inscripcion']
                cursor.execute(
                    "INSERT INTO nota (id_evaluacion, id_inscripcion, calificacion, observaciones) VALUES (%s, %s, %s, %s) ON CONFLICT (id_evaluacion, id_inscripcion) DO UPDATE SET calificacion = EXCLUDED.calificacion, observaciones = EXCLUDED.observaciones, actualizado_en = CURRENT_TIMESTAMP",
                    (id_evaluacion, id_inscripcion, calificacion, observaciones)
                )
                self.db.commit()
                return {'exito': True, 'id_inscripcion': id_inscripcion}
        except Exception as e:
            self.db.rollback()
            print(f"Error asignando nota: {e}")
            return {'exito': False, 'error': str(e)}

    def registrar_asistencia(self, cedula, id_formacion, fecha_asistencia, estado, observaciones=None):
        """Registrar asistencia o incidencia de un estudiante por sesión"""
        try:
            usuario = self.obtener_usuario_por_cedula(cedula)
            if not usuario:
                return {'exito': False, 'error': 'Usuario no encontrado'}

            with self.db.cursor() as cursor:
                cursor.execute("BEGIN")
                cursor.execute(
                    "SELECT id_inscripcion FROM inscripcion WHERE id_usuario = %s AND id_formacion = %s",
                    (usuario['id_usuario'], id_formacion)
                )
                registro = cursor.fetchone()
                if not registro:
                    self.db.rollback()
                    return {'exito': False, 'error': 'Inscripción no encontrada para la formación'}

                id_inscripcion = registro['id_inscripcion']
                cursor.execute(
                    "INSERT INTO asistencia (id_inscripcion, fecha_asistencia, estado, observaciones) VALUES (%s, %s, %s, %s) ON CONFLICT (id_inscripcion, fecha_asistencia) DO UPDATE SET estado = EXCLUDED.estado, observaciones = EXCLUDED.observaciones, actualizado_en = CURRENT_TIMESTAMP",
                    (id_inscripcion, fecha_asistencia, estado, observaciones)
                )
                self.db.commit()
                return {'exito': True, 'id_inscripcion': id_inscripcion}
        except Exception as e:
            self.db.rollback()
            print(f"Error registrando asistencia: {e}")
            return {'exito': False, 'error': str(e)}

    def crear_solicitud_taller(self, cedula, datos_solicitud):
        """Crear solicitud de taller desde propuesta de estudiante"""
        try:
            usuario = self.obtener_usuario_por_cedula(cedula)
            if not usuario:
                return {'exito': False, 'error': 'Usuario no encontrado'}

            with self.db.cursor() as cursor:
                cursor.execute("BEGIN")
                cursor.execute(
                    "INSERT INTO solicitud_taller (id_usuario, titulo_propuesto, descripcion, tipo_taller, carreras_autorizadas, semestres_autorizados, estado, observacion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_solicitud",
                    (
                        usuario['id_usuario'],
                        datos_solicitud['titulo_propuesto'],
                        datos_solicitud.get('descripcion'),
                        datos_solicitud.get('tipo_taller'),
                        ','.join(datos_solicitud.get('carreras_autorizadas', [])) if datos_solicitud.get('carreras_autorizadas') else None,
                        ','.join(datos_solicitud.get('semestres_autorizados', [])) if datos_solicitud.get('semestres_autorizados') else None,
                        'Pendiente',
                        datos_solicitud.get('observacion')
                    )
                )
                id_solicitud = cursor.fetchone()['id_solicitud']
                self.db.commit()
                return {'exito': True, 'id_solicitud': id_solicitud}
        except Exception as e:
            self.db.rollback()
            print(f"Error creando solicitud de taller: {e}")
            return {'exito': False, 'error': str(e)}

    def procesar_solicitudes(self, ids_solicitudes, accion, observacion, datos_taller=None):
        """Aceptar o rechazar solicitudes y crear formaciones cuando se acepta"""
        if accion not in ('Aceptar', 'Rechazar'):
            return {'exito': False, 'error': 'Acción inválida'}

        if not observacion or observacion.strip() == '':
            return {'exito': False, 'error': 'Observación obligatoria'}

        try:
            with self.db.cursor() as cursor:
                cursor.execute("BEGIN")
                for id_solicitud in ids_solicitudes:
                    cursor.execute(
                        "SELECT id_usuario, titulo_propuesto, descripcion, tipo_taller, carreras_autorizadas, semestres_autorizados FROM solicitud_taller WHERE id_solicitud = %s",
                        (id_solicitud,)
                    )
                    solicitud = cursor.fetchone()
                    if not solicitud:
                        continue

                    estado = 'Aceptada' if accion == 'Aceptar' else 'Rechazada'
                    cursor.execute(
                        "UPDATE solicitud_taller SET estado = %s, observacion = %s, actualizado_en = CURRENT_TIMESTAMP WHERE id_solicitud = %s",
                        (estado, observacion.strip(), id_solicitud)
                    )

                    if accion == 'Aceptar' and datos_taller:
                        cursor.execute(
                            "INSERT INTO formacion (id_taller, codigo_cohorte, nombre_cohorte, descripcion, fecha_inicio, fecha_fin, cupos_maximos, cupos_disponibles, instructor, estado, observacion_estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (
                                datos_taller['id_taller'],
                                datos_taller['codigo_cohorte'],
                                datos_taller['nombre_cohorte'],
                                datos_taller.get('descripcion'),
                                datos_taller['fecha_inicio'],
                                datos_taller['fecha_fin'],
                                datos_taller.get('cupos_maximos', 30),
                                datos_taller.get('cupos_maximos', 30),
                                datos_taller.get('instructor'),
                                'Activo',
                                f'Creado desde solicitud {id_solicitud}'
                            )
                        )
                self.db.commit()
                return {'exito': True, 'procesadas': len(ids_solicitudes)}
        except Exception as e:
            self.db.rollback()
            print(f"Error procesando solicitudes: {e}")
            return {'exito': False, 'error': str(e)}

    def adjuntar_certificado(self, id_inscripcion, codigo_certificado, url_certificado, fecha_vencimiento=None):
        """Adjuntar certificado a una inscripción y marcarlo pendiente de entrega"""
        try:
            with self.db.cursor() as cursor:
                cursor.execute("BEGIN")
                cursor.execute(
                    "INSERT INTO certificado (id_inscripcion, codigo_certificado, url_certificado, fecha_vencimiento, estado, entregado, enviado_correo, adjunto_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (codigo_certificado) DO UPDATE SET url_certificado = EXCLUDED.url_certificado, fecha_vencimiento = EXCLUDED.fecha_vencimiento, estado = EXCLUDED.estado, adjunto_url = EXCLUDED.adjunto_url, actualizado_en = CURRENT_TIMESTAMP",
                    (id_inscripcion, codigo_certificado, url_certificado, fecha_vencimiento, 'Activo', False, False, url_certificado)
                )
                self.db.commit()
                return {'exito': True}
        except Exception as e:
            self.db.rollback()
            print(f"Error adjuntando certificado: {e}")
            return {'exito': False, 'error': str(e)}

    def marcar_certificado_entregado(self, codigo_certificado, fecha_entrega=None):
        """Marcar certificado como entregado"""
        try:
            with self.db.cursor() as cursor:
                cursor.execute("BEGIN")
                cursor.execute(
                    "UPDATE certificado SET entregado = TRUE, fecha_entrega = %s, actualizado_en = CURRENT_TIMESTAMP WHERE codigo_certificado = %s",
                    (fecha_entrega or datetime.now().date(), codigo_certificado)
                )
                self.db.commit()
                return {'exito': True}
        except Exception as e:
            self.db.rollback()
            print(f"Error marcando certificado entregado: {e}")
            return {'exito': False, 'error': str(e)}

    def enviar_certificado_correo(self, codigo_certificado, direccion_email):
        """Marcar certificado como enviado por correo (simulación)"""
        try:
            with self.db.cursor() as cursor:
                cursor.execute("BEGIN")
                cursor.execute(
                    "UPDATE certificado SET enviado_correo = TRUE, actualizado_en = CURRENT_TIMESTAMP WHERE codigo_certificado = %s",
                    (codigo_certificado,)
                )
                self.db.commit()
                return {'exito': True, 'mensaje': f'Certificado {codigo_certificado} marcado como enviado a {direccion_email}'}
        except Exception as e:
            self.db.rollback()
            print(f"Error enviando certificado por correo: {e}")
            return {'exito': False, 'error': str(e)}

    def reporte_inscritos_culminados(self, estado_filtrado=None):
        """Reporte de estudiantes inscritos y culminados por estado"""
        try:
            with self.db.cursor() as cursor:
                query = """
                    SELECT p.cedula, p.nombre, p.apellido, u.login_usuario, f.nombre_cohorte, t.nombre_taller, i.estado as estado_inscripcion
                    FROM inscripcion i
                    JOIN usuario u ON i.id_usuario = u.id
                    JOIN persona p ON u.id_persona = p.id
                    JOIN formacion f ON i.id_formacion = f.id_formacion
                    JOIN taller t ON f.id_taller = t.id_taller
                    WHERE 1=1
                """
                params = []
                if estado_filtrado:
                    query += " AND i.estado = %s"
                    params.append(estado_filtrado)
                query += " ORDER BY p.apellido, p.nombre"
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error generando reporte de inscritos y culminados: {e}")
            return []

    def reporte_certificados(self, entregado=None):
        """Reporte de certificados entregados vs pendientes"""
        try:
            with self.db.cursor() as cursor:
                query = """
                    SELECT c.codigo_certificado, p.cedula, p.nombre, p.apellido, t.nombre_taller, f.nombre_cohorte, c.entregado, c.enviado_correo, c.fecha_entrega
                    FROM certificado c
                    JOIN inscripcion i ON c.id_inscripcion = i.id_inscripcion
                    JOIN usuario u ON i.id_usuario = u.id
                    JOIN persona p ON u.id_persona = p.id
                    JOIN formacion f ON i.id_formacion = f.id_formacion
                    JOIN taller t ON f.id_taller = t.id_taller
                    WHERE 1=1
                """
                params = []
                if entregado is not None:
                    query += " AND c.entregado = %s"
                    params.append(entregado)
                query += " ORDER BY c.fecha_emision DESC"
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error generando reporte de certificados: {e}")
            return []

    def historial_estudiantil_por_cedula(self, cedula):
        """Consulta integral de historial estudiantil usando cédula"""
        try:
            with self.db.cursor() as cursor:
                query = """
                    SELECT p.cedula, p.nombre, p.apellido, e.cedula_estudiante AS codigo_estudiantil,
                           c.nombre_carrera AS carrera, s.nombre_semestre AS semestre_actual,
                           t.nombre_taller, f.nombre_cohorte, i.estado as estado_inscripcion,
                           n.calificacion as nota, c.codigo_certificado, c.entregado, c.fecha_entrega
                    FROM persona p
                    JOIN usuario u ON p.id = u.id_persona
                    LEFT JOIN estudiante e ON u.id = e.id_usuario
                    LEFT JOIN carrera c ON e.id_carrera = c.id_carrera
                    LEFT JOIN semestre s ON e.id_semestre_formacion = s.id_semestre
                    LEFT JOIN inscripcion i ON u.id = i.id_usuario
                    LEFT JOIN formacion f ON i.id_formacion = f.id_formacion
                    LEFT JOIN taller t ON f.id_taller = t.id_taller
                    LEFT JOIN nota n ON i.id_inscripcion = n.id_inscripcion
                    LEFT JOIN certificado c ON i.id_inscripcion = c.id_inscripcion
                    WHERE p.cedula = %s
                    ORDER BY f.fecha_inicio DESC
                """
                cursor.execute(query, (cedula.strip(),))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error consultando historial estudiantil: {e}")
            return []

    def consultar_solicitudes(self, estado=None):
        """Consultar solicitudes de taller con filtros de estado"""
        try:
            with self.db.cursor() as cursor:
                query = "SELECT * FROM solicitud_taller WHERE 1=1"
                params = []
                if estado:
                    query += " AND estado = %s"
                    params.append(estado)
                query += " ORDER BY fecha_solicitud DESC"
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error consultando solicitudes: {e}")
            return []
