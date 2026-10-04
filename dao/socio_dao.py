"""
DAO para Socios y Multas.
Gestiona el registro de lectores, multas asociadas y estado de cuenta de los socios.
"""
from dao.conexion import obtener_conexion
from model.socio import Socio
from model.multa import Multa
from model.persona import Persona
from model.estados import EstadoMulta


class SocioDAO:
    """
    Data Access Object para la persistencia de Socios y Multas en SQLite.
    """

    @staticmethod
    def crear(socio: Socio) -> bool:
        """Inserta un nuevo socio en la base de datos."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        rut_normalizado = Persona.formatear_rut(socio.rut)
        try:
            cursor.execute("""
                INSERT INTO socios (rut, nombre, direccion)
                VALUES (?, ?, ?)
            """, (rut_normalizado, socio.nombre, socio.direccion))
            conexion.commit()
            return True
        except Exception as e:
            conexion.rollback()
            raise e
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_rut(rut: str) -> Socio | None:
        """
        Recupera un socio por su RUT e incluye su lista de multas activas e históricas.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        rut_normalizado = Persona.formatear_rut(rut)
        rut_limpio = rut.replace("-", "").replace(".", "").upper().strip()

        cursor.execute("""
            SELECT rut, nombre, direccion FROM socios 
            WHERE rut = ? OR REPLACE(REPLACE(rut, '.', ''), '-', '') = ?
        """, (rut_normalizado, rut_limpio))
        fila = cursor.fetchone()

        if not fila:
            conexion.close()
            return None

        socio = Socio(rut=fila[0], nombre=fila[1], direccion=fila[2])

        # Cargamos las multas asociadas
        cursor.execute("""
            SELECT id, monto, estado, motivo FROM multas 
            WHERE rut_socio = ? OR REPLACE(REPLACE(rut_socio, '.', ''), '-', '') = ?
            ORDER BY id ASC
        """, (socio.rut, rut_limpio))
        filas_multas = cursor.fetchall()
        conexion.close()

        for fm in filas_multas:
            multa = Multa(
                id_multa=fm[0],
                monto=fm[1],
                estado=EstadoMulta(fm[2]),
                motivo=fm[3],
                rut_socio=socio.rut
            )
            socio.agregar_multa(multa)

        return socio

    @staticmethod
    def listar_todos() -> list[Socio]:
        """Retorna la lista de todos los socios con sus respectivas multas cargadas."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT rut FROM socios ORDER BY nombre ASC")
        ruts = [f[0] for f in cursor.fetchall()]
        conexion.close()

        return [SocioDAO.obtener_por_rut(rut) for rut in ruts if rut]

    @staticmethod
    def registrar_multa(rut_socio: str, monto: float, motivo: str = "Atraso") -> Multa:
        """Registra una nueva multa impaga para un socio."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        rut_normalizado = Persona.formatear_rut(rut_socio)

        cursor.execute("""
            INSERT INTO multas (rut_socio, monto, estado, motivo)
            VALUES (?, ?, ?, ?)
        """, (rut_normalizado, float(monto), EstadoMulta.PENDIENTE.value, motivo))

        id_multa = cursor.lastrowid
        conexion.commit()
        conexion.close()

        return Multa(id_multa=id_multa, rut_socio=rut_normalizado, monto=monto,
                     estado=EstadoMulta.PENDIENTE, motivo=motivo)

    @staticmethod
    def listar_todas_las_multas() -> list[dict]:
        """Retorna todas las multas registradas en la base de datos con información del socio."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT m.id, m.rut_socio, s.nombre, m.monto, m.estado, m.motivo
            FROM multas m
            LEFT JOIN socios s ON m.rut_socio = s.rut
            ORDER BY m.id DESC
        """)
        filas = cursor.fetchall()
        conexion.close()

        return [{
            "id": f[0],
            "rut_socio": f[1],
            "nombre_socio": f[2] or "Desconocido",
            "monto": f[3],
            "estado": f[4],
            "motivo": f[5]
        } for f in filas]

    @staticmethod
    def cambiar_estado_multa(id_multa: int, nuevo_estado: EstadoMulta) -> bool:
        """Actualiza el estado de una multa (Pagada o Condonada)."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE multas 
            SET estado = ? 
            WHERE id = ?
        """, (nuevo_estado.value, id_multa))

        filas = cursor.rowcount
        conexion.commit()
        conexion.close()
        return filas > 0

    @staticmethod
    def pagar_todas_las_multas_socio(rut_socio: str) -> int:
        """Marca como PAGADAS todas las multas pendientes de un socio."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        rut_limpio = rut_socio.replace("-", "").replace(".", "").upper().strip()

        cursor.execute("""
            UPDATE multas 
            SET estado = ? 
            WHERE (rut_socio = ? OR REPLACE(REPLACE(rut_socio, '.', ''), '-', '') = ?)
              AND estado = ?
        """, (EstadoMulta.PAGADA.value, rut_socio, rut_limpio, EstadoMulta.PENDIENTE.value))

        filas = cursor.rowcount
        conexion.commit()
        conexion.close()
        return filas

    @staticmethod
    def eliminar(rut: str) -> bool:
        """
        Elimina un socio por su RUT junto con sus multas y préstamos asociados.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        rut_limpio = rut.replace(".", "").upper().strip()

        try:
            # Obtener el RUT exacto
            cursor.execute("SELECT rut FROM socios WHERE REPLACE(rut, '.', '') = ?", (rut_limpio,))
            fila = cursor.fetchone()
            if not fila:
                return False
            rut_exacto = fila[0]

            # Eliminar detalles de préstamos asociados
            cursor.execute("""
                DELETE FROM detalle_prestamos 
                WHERE id_prestamo IN (SELECT id FROM prestamos WHERE rut_socio = ?)
            """, (rut_exacto,))

            # Eliminar préstamos asociados
            cursor.execute("DELETE FROM prestamos WHERE rut_socio = ?", (rut_exacto,))

            # Eliminar multas asociadas
            cursor.execute("DELETE FROM multas WHERE rut_socio = ?", (rut_exacto,))

            # Eliminar socio
            cursor.execute("DELETE FROM socios WHERE rut = ?", (rut_exacto,))

            filas = cursor.rowcount
            conexion.commit()
            return filas > 0
        except Exception as e:
            conexion.rollback()
            raise e
        finally:
            conexion.close()

