"""
DAO para Préstamos y Detalle de Préstamos.
Gestiona la transacción completa de préstamo y la persistencia de sus líneas de detalle.
"""
from dao.conexion import obtener_conexion
from dao.socio_dao import SocioDAO
from dao.material_dao import MaterialDAO
from model.prestamo import Prestamo
from model.detalle_prestamo import DetallePrestamo
from model.roles import Bibliotecaria, Administradora
from model.empleado import Empleado
from model.estados import EstadoMaterial


class PrestamoDAO:
    """
    Data Access Object para registrar y consultar transacciones de préstamo en SQLite.
    """

    @staticmethod
    def guardar_prestamo(prestamo: Prestamo) -> int:
        """
        Guarda la cabecera del préstamo y todas sus líneas de detalle en una sola transacción atómica.
        Actualiza el estado de los materiales en la base de datos a PRESTADO.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            # 1. Insertar la cabecera del préstamo
            cursor.execute("""
                INSERT INTO prestamos (rut_socio, id_empleado, fecha_registro)
                VALUES (?, ?, ?)
            """, (prestamo.socio.rut, prestamo.empleado.id_empleado, str(prestamo.fecha_registro)))

            id_prestamo = cursor.lastrowid
            prestamo.id_prestamo = id_prestamo

            # 2. Insertar cada línea de detalle y actualizar el estado del material
            for detalle in prestamo.detalles:
                cursor.execute("""
                    INSERT INTO detalle_prestamos (
                        id_prestamo, codigo_material, fecha_vencimiento, renovaciones_usadas
                    ) VALUES (?, ?, ?, ?)
                """, (
                    id_prestamo,
                    detalle.material.codigo,
                    str(detalle.fecha_vencimiento),
                    detalle.renovaciones_usadas
                ))

                # Actualizamos el estado del material en la base de datos a PRESTADO
                cursor.execute("""
                    UPDATE materiales 
                    SET estado = ? 
                    WHERE codigo = ?
                """, (EstadoMaterial.PRESTADO.value, detalle.material.codigo))

            conexion.commit()
            return id_prestamo

        except Exception as e:
            conexion.rollback()
            raise e
        finally:
            conexion.close()

    @staticmethod
    def listar_todos() -> list[dict]:
        """
        Retorna la lista de todos los préstamos registrados con su resumen de detalles.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT p.id, p.fecha_registro, s.nombre, s.rut, e.nombre, e.id_empleado
            FROM prestamos p
            JOIN socios s ON p.rut_socio = s.rut
            JOIN empleados e ON p.id_empleado = e.id_empleado
            ORDER BY p.id DESC
        """)
        filas = cursor.fetchall()
        conexion.close()

        resultado = []
        for f in filas:
            detalles = PrestamoDAO.obtener_detalles_por_id_prestamo(f[0])
            resultado.append({
                "id": f[0],
                "fecha": f[1],
                "socio_nombre": f[2],
                "socio_rut": f[3],
                "empleado_nombre": f[4],
                "empleado_id": f[5],
                "detalles": detalles
            })
        return resultado

    @staticmethod
    def obtener_detalles_por_id_prestamo(id_prestamo: int) -> list[dict]:
        """
        Recupera las líneas de detalle asociadas a un préstamo específico.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT dp.id, dp.codigo_material, m.titulo, m.tipo, dp.fecha_vencimiento, dp.renovaciones_usadas
            FROM detalle_prestamos dp
            JOIN materiales m ON dp.codigo_material = m.codigo
            WHERE dp.id_prestamo = ?
        """, (id_prestamo,))
        filas = cursor.fetchall()
        conexion.close()

        return [{
            "id_detalle": f[0],
            "codigo": f[1],
            "titulo": f[2],
            "tipo": f[3],
            "fecha_vencimiento": f[4],
            "renovaciones": f[5]
        } for f in filas]

    @staticmethod
    def obtener_empleado_por_id(id_empleado: str) -> Empleado | None:
        """Recupera un empleado por su ID."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT rut, nombre, id_empleado, clave_acceso, rol FROM empleados WHERE id_empleado = ?", (id_empleado.strip().upper(),))
        fila = cursor.fetchone()
        conexion.close()

        if not fila:
            return None

        rut, nombre, id_emp, clave, rol = fila
        if rol == "Administradora":
            return Administradora(rut=rut, nombre=nombre, id_empleado=id_emp, clave_acceso=clave)
        return Bibliotecaria(rut=rut, nombre=nombre, id_empleado=id_emp, clave_acceso=clave)

    @staticmethod
    def obtener_empleado_por_rut(rut: str) -> Empleado | None:
        """Recupera un empleado por su RUT."""
        from model.persona import Persona
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        rut_norm = Persona.formatear_rut(rut)
        rut_limpio = rut.replace("-", "").replace(".", "").upper().strip()

        cursor.execute("""
            SELECT rut, nombre, id_empleado, clave_acceso, rol 
            FROM empleados 
            WHERE rut = ? OR REPLACE(REPLACE(rut, '.', ''), '-', '') = ?
        """, (rut_norm, rut_limpio))
        fila = cursor.fetchone()
        conexion.close()

        if not fila:
            return None

        rut_db, nombre, id_emp, clave, rol = fila
        if rol == "Administradora":
            return Administradora(rut=rut_db, nombre=nombre, id_empleado=id_emp, clave_acceso=clave)
        return Bibliotecaria(rut=rut_db, nombre=nombre, id_empleado=id_emp, clave_acceso=clave)

    @staticmethod
    def listar_empleados() -> list[Empleado]:
        """Retorna todos los empleados registrados en el sistema."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT rut, nombre, id_empleado, clave_acceso, rol FROM empleados ORDER BY id_empleado ASC")
        filas = cursor.fetchall()
        conexion.close()

        empleados = []
        for f in filas:
            rut, nombre, id_emp, clave, rol = f
            if rol == "Administradora":
                empleados.append(Administradora(rut=rut, nombre=nombre, id_empleado=id_emp, clave_acceso=clave))
            else:
                empleados.append(Bibliotecaria(rut=rut, nombre=nombre, id_empleado=id_emp, clave_acceso=clave))
        return empleados

    @staticmethod
    def devolver_material(codigo_material: str) -> bool:
        """Marca un material como DISPONIBLE nuevamente."""
        return MaterialDAO.actualizar_estado(codigo_material, EstadoMaterial.DISPONIBLE)
