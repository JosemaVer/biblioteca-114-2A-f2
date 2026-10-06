"""
DAO para Préstamos y Detalle de Préstamos.
Gestiona la transacción completa de préstamo y la persistencia de sus líneas de detalle.
"""
import math
from datetime import date
from dao.conexion import obtener_conexion
from model.prestamo import Prestamo
from model.roles import Bibliotecaria, Administradora
from model.empleado import Empleado
from model.estados import EstadoMaterial
from services.passwords import hashear_clave


class PrestamoDAO:
    """
    Data Access Object para registrar y consultar transacciones de préstamo en SQLite.
    """
    MULTA_DIARIA_POR_TIPO = {
        "Libro": 1000,
        "Revista": 500,
        "Multimedia": 1500,
    }
    PORCENTAJES_DANO = {
        "Leve": 25,
        "Moderado": 50,
        "Grave": 75,
        "Pérdida total": 100,
    }

    @staticmethod
    def _aplicar_multa_atraso(cursor, fila: tuple, fecha_actual: date) -> dict | None:
        id_detalle, rut_socio, codigo, titulo, tipo, vencimiento, dias_calculados = fila
        dias_atraso = (fecha_actual - date.fromisoformat(vencimiento)).days
        dias_nuevos = dias_atraso - dias_calculados
        if dias_nuevos <= 0:
            return None

        monto = dias_nuevos * PrestamoDAO.MULTA_DIARIA_POR_TIPO[tipo]
        cursor.execute("""
            INSERT INTO multas (rut_socio, monto, estado, motivo)
            VALUES (?, ?, 'Pendiente', ?)
        """, (
            rut_socio,
            monto,
            f"Atraso de {titulo} ({codigo}): {dias_nuevos} día(s) adicionales",
        ))
        cursor.execute("""
            UPDATE detalle_prestamos
            SET dias_multa_calculados = ?
            WHERE id = ?
        """, (dias_atraso, id_detalle))

        return {"rut_socio": rut_socio, "monto": monto, "dias": dias_nuevos}

    @staticmethod
    def procesar_multas_atraso(fecha_actual: date | None = None) -> list[dict]:
        """Registra los días de atraso aún no cobrados de todos los préstamos activos."""
        hoy = fecha_actual or date.today()
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                SELECT dp.id, p.rut_socio, m.codigo, m.titulo, m.tipo,
                       dp.fecha_vencimiento, dp.dias_multa_calculados
                FROM detalle_prestamos dp
                JOIN prestamos p ON p.id = dp.id_prestamo
                JOIN materiales m ON m.codigo = dp.codigo_material
                WHERE dp.fecha_devolucion IS NULL
                  AND m.estado = ?
                ORDER BY dp.id
            """, (EstadoMaterial.PRESTADO.value,))
            filas = cursor.fetchall()
            multas = []
            for fila in filas:
                multa = PrestamoDAO._aplicar_multa_atraso(cursor, fila, hoy)
                if multa is not None:
                    multas.append(multa)
            conexion.commit()
            return multas
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

    @staticmethod
    def registrar_dano(
        codigo_material: str,
        rut_socio: str,
        categoria: str,
        descripcion: str,
        valor_reposicion_clp: float,
    ) -> dict:
        """Registra el daño, su multa y la devolución del material en una transacción."""
        if categoria not in PrestamoDAO.PORCENTAJES_DANO:
            raise ValueError(f"Categoría de daño no reconocida: {categoria}")
        if not math.isfinite(valor_reposicion_clp) or valor_reposicion_clp <= 0:
            raise ValueError("El valor de reposición debe ser un monto finito mayor que cero.")
        if not descripcion.strip():
            raise ValueError("La descripción del daño no puede quedar vacía.")

        codigo = codigo_material.strip().upper()
        hoy = date.today()
        porcentaje = PrestamoDAO.PORCENTAJES_DANO[categoria]
        monto_multa = int(round(valor_reposicion_clp * porcentaje / 100))
        estado_final = (
            EstadoMaterial.EXTRAVIADO
            if categoria == "Pérdida total"
            else EstadoMaterial.DISPONIBLE
        )
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                "SELECT estado FROM materiales WHERE codigo = ?",
                (codigo,),
            )
            material = cursor.fetchone()
            if not material:
                raise ValueError(f"No existe el material '{codigo}'.")
            if material[0] == EstadoMaterial.EXTRAVIADO.value:
                raise ValueError(f"El material '{codigo}' ya está registrado como extraviado.")

            cursor.execute("""
                SELECT dp.id, p.rut_socio, m.codigo, m.titulo, m.tipo,
                       dp.fecha_vencimiento, dp.dias_multa_calculados
                FROM detalle_prestamos dp
                JOIN prestamos p ON p.id = dp.id_prestamo
                JOIN materiales m ON m.codigo = dp.codigo_material
                WHERE dp.codigo_material = ?
                  AND dp.fecha_devolucion IS NULL
                  AND m.estado = ?
                ORDER BY dp.id DESC
                LIMIT 1
            """, (codigo, EstadoMaterial.PRESTADO.value))
            detalle_activo = cursor.fetchone()
            multa_atraso = None
            if detalle_activo:
                if detalle_activo[1] != rut_socio:
                    raise ValueError(
                        f"El material '{codigo}' está prestado a otro socio "
                        f"({detalle_activo[1]})."
                    )
                multa_atraso = PrestamoDAO._aplicar_multa_atraso(
                    cursor, detalle_activo, hoy
                )
                cursor.execute("""
                    UPDATE detalle_prestamos
                    SET fecha_devolucion = ?
                    WHERE id = ?
                """, (hoy.isoformat(), detalle_activo[0]))

            cursor.execute("""
                INSERT INTO multas (rut_socio, monto, estado, motivo)
                VALUES (?, ?, 'Pendiente', ?)
            """, (
                rut_socio,
                monto_multa,
                f"Daño {categoria.lower()} en {codigo}: {descripcion.strip()}",
            ))
            id_multa = cursor.lastrowid
            cursor.execute("""
                INSERT INTO danos_materiales (
                    codigo_material, rut_socio, categoria, descripcion,
                    porcentaje, valor_reposicion_clp, monto_multa,
                    fecha_registro, id_multa
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                codigo,
                rut_socio,
                categoria,
                descripcion.strip(),
                porcentaje,
                valor_reposicion_clp,
                monto_multa,
                hoy.isoformat(),
                id_multa,
            ))
            cursor.execute("""
                UPDATE materiales
                SET estado = ?
                WHERE codigo = ?
            """, (estado_final.value, codigo))
            conexion.commit()
            return {
                "id_multa": id_multa,
                "monto_multa": monto_multa,
                "porcentaje": porcentaje,
                "multa_atraso": multa_atraso,
                "estado": estado_final.value,
            }
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

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

        cursor.execute("""
            SELECT rut, nombre, id_empleado, clave_acceso, rol
            FROM empleados
            ORDER BY CASE WHEN rol = 'Administradora' THEN 0 ELSE 1 END,
                     id_empleado ASC
        """)
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
    def actualizar_clave_acceso(id_empleado: str, clave: str) -> bool:
        """Actualiza la contraseña de un empleado guardando únicamente su hash."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE empleados SET clave_acceso = ? WHERE id_empleado = ?",
            (hashear_clave(clave), id_empleado.strip().upper()),
        )
        actualizado = cursor.rowcount > 0
        conexion.commit()
        conexion.close()
        return actualizado

    @staticmethod
    def devolver_material(codigo_material: str) -> int | None:
        """Cobra los días de atraso pendientes y marca el material como devuelto."""
        hoy = date.today()
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                SELECT dp.id, p.rut_socio, m.codigo, m.titulo, m.tipo,
                       dp.fecha_vencimiento, dp.dias_multa_calculados
                FROM detalle_prestamos dp
                JOIN prestamos p ON p.id = dp.id_prestamo
                JOIN materiales m ON m.codigo = dp.codigo_material
                WHERE dp.codigo_material = ?
                  AND dp.fecha_devolucion IS NULL
                  AND m.estado = ?
                ORDER BY dp.id DESC
                LIMIT 1
            """, (codigo_material.strip().upper(), EstadoMaterial.PRESTADO.value))
            fila = cursor.fetchone()
            if not fila:
                conexion.rollback()
                return None

            multa = PrestamoDAO._aplicar_multa_atraso(cursor, fila, hoy)
            cursor.execute("""
                UPDATE detalle_prestamos
                SET fecha_devolucion = ?
                WHERE id = ?
            """, (hoy.isoformat(), fila[0]))
            cursor.execute("""
                UPDATE materiales
                SET estado = ?
                WHERE codigo = ?
            """, (EstadoMaterial.DISPONIBLE.value, codigo_material.strip().upper()))
            conexion.commit()
            return multa["monto"] if multa else 0
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()
