"""
DAO para Materiales (Libros, Revistas y Multimedia).
Implementa CRUD completo utilizando consultas parametrizadas (?) para prevenir inyección SQL.
"""
from dao.conexion import obtener_conexion
from model.estados import EstadoMaterial
from model.material import Material
from model.libro import Libro
from model.revista import Revista
from model.multimedia import Multimedia


class MaterialDAO:
    """
    Data Access Object para la gestión de materiales en SQLite.
    """

    @staticmethod
    def crear(material: Material) -> bool:
        """
        Inserta un nuevo material en la base de datos con consultas parametrizadas.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        tipo = material.__class__.__name__
        valor_usd = material.valor_reposicion_usd
        estado_txt = material.estado.value
        
        valor_pesos = 0
        es_extranjero = 0
        numero_edicion = 1
        formato = "DVD"

        if isinstance(material, Libro):
            valor_pesos = material.valor_reposicion_pesos
            es_extranjero = 1 if material.es_extranjero else 0
        elif isinstance(material, Revista):
            numero_edicion = material.numero_edicion
        elif isinstance(material, Multimedia):
            formato = material.formato

        try:
            # Consulta 100% parametrizada con '?'
            cursor.execute("""
                INSERT INTO materiales (
                    codigo, tipo, titulo, estado, valor_reposicion_usd,
                    valor_reposicion_pesos, es_extranjero, numero_edicion, formato
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                material.codigo, tipo, material.titulo, estado_txt, valor_usd,
                valor_pesos, es_extranjero, numero_edicion, formato
            ))
            conexion.commit()
            return True
        except Exception as e:
            conexion.rollback()
            raise e
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_codigo(codigo: str) -> Material | None:
        """
        Busca un material por su código único de forma segura.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Consulta parametrizada con '?'
        cursor.execute("SELECT * FROM materiales WHERE codigo = ?", (codigo.strip().upper(),))
        fila = cursor.fetchone()
        conexion.close()

        if fila:
            return MaterialDAO._fila_a_objeto(fila)
        return None

    @staticmethod
    def listar_todos() -> list[Material]:
        """
        Retorna la lista completa de materiales registrados en la biblioteca.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM materiales ORDER BY codigo ASC")
        filas = cursor.fetchall()
        conexion.close()

        return [MaterialDAO._fila_a_objeto(f) for f in filas]

    @staticmethod
    def actualizar_titulo(codigo: str, nuevo_titulo: str) -> bool:
        """
        Actualiza el título de un material existente.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE materiales 
            SET titulo = ? 
            WHERE codigo = ?
        """, (nuevo_titulo.strip(), codigo.strip().upper()))

        filas_afectadas = cursor.rowcount
        conexion.commit()
        conexion.close()
        return filas_afectadas > 0

    @staticmethod
    def actualizar_estado(codigo: str, nuevo_estado: EstadoMaterial) -> bool:
        """
        Actualiza el estado de un material (Disponible, Prestado, Extraviado).
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE materiales 
            SET estado = ? 
            WHERE codigo = ?
        """, (nuevo_estado.value, codigo.strip().upper()))

        filas_afectadas = cursor.rowcount
        conexion.commit()
        conexion.close()
        return filas_afectadas > 0

    @staticmethod
    def eliminar(codigo: str) -> bool:
        """
        Elimina un material de la base de datos por su código.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("DELETE FROM materiales WHERE codigo = ?", (codigo.strip().upper(),))
        filas_afectadas = cursor.rowcount
        conexion.commit()
        conexion.close()
        return filas_afectadas > 0

    @staticmethod
    def _fila_a_objeto(fila) -> Material:
        """
        Convierte una tupla de la base de datos a su respectiva instancia de objeto (Polimorfismo).
        """
        codigo, tipo, titulo, estado_str, valor_usd, valor_pesos, es_extranjero, num_edicion, formato = fila
        estado = EstadoMaterial(estado_str)

        if tipo == "Libro":
            return Libro(
                codigo=codigo,
                titulo=titulo,
                es_extranjero=bool(es_extranjero),
                valor_reposicion_usd=valor_usd,
                valor_reposicion_pesos=valor_pesos,
                estado=estado
            )
        elif tipo == "Revista":
            return Revista(
                codigo=codigo,
                titulo=titulo,
                numero_edicion=num_edicion,
                valor_reposicion_usd=valor_usd,
                estado=estado
            )
        elif tipo == "Multimedia":
            return Multimedia(
                codigo=codigo,
                titulo=titulo,
                formato=formato,
                valor_reposicion_usd=valor_usd,
                estado=estado
            )
        else:
            raise ValueError(f"Tipo de material '{tipo}' no soportado.")
