"""
Clase Prestamo: Representa la transacción completa de préstamo realizada por un socio.
Aplica las 2 reglas de negocio y lanza las excepciones correspondientes.
"""
from datetime import date, datetime
from model.socio import Socio
from model.empleado import Empleado
from model.material import Material
from model.detalle_prestamo import DetallePrestamo
from model.estados import EstadoMaterial
from model.excepciones import SocioConMultaException, MaterialNoDisponibleException


class Prestamo:
    """
    Transacción de préstamo que agrupa 1 o más materiales solicitados por un Socio y atendidos por un Empleado.
    """
    def __init__(self, socio: Socio, empleado: Empleado, fecha_registro=None, id_prestamo: int = None):
        self.id_prestamo = id_prestamo
        self.socio = socio
        self.empleado = empleado
        self.__detalles = []

        if fecha_registro is None:
            self.__fecha_registro = date.today()
        elif isinstance(fecha_registro, str):
            self.__fecha_registro = datetime.strptime(fecha_registro, "%Y-%m-%d").date()
        elif isinstance(fecha_registro, (datetime, date)):
            self.__fecha_registro = fecha_registro if isinstance(fecha_registro, date) else fecha_registro.date()
        else:
            raise ValueError("Fecha de registro inválida.")

    # ==========================
    # Getters y Setters
    # ==========================
    @property
    def socio(self) -> Socio:
        return self.__socio

    @socio.setter
    def socio(self, valor: Socio):
        if not isinstance(valor, Socio):
            raise TypeError("El socio debe ser una instancia válida de Socio.")
        self.__socio = valor

    @property
    def empleado(self) -> Empleado:
        return self.__empleado

    @empleado.setter
    def empleado(self, valor: Empleado):
        if not isinstance(valor, Empleado):
            raise TypeError("El empleado debe ser una instancia válida de Empleado.")
        self.__empleado = valor

    @property
    def fecha_registro(self) -> date:
        return self.__fecha_registro

    @property
    def detalles(self) -> list:
        """Retorna la lista de líneas de detalle del préstamo."""
        return self.__detalles

    # ==========================================================
    # Lógica de Negocio: Agregar Material y Validar Reglas
    # ==========================================================
    def agregar_material(self, material: Material) -> DetallePrestamo:
        """
        Agrega un material al préstamo aplicando las reglas de negocio:
        - Regla 1: El socio no debe tener multas pendientes (SocioConMultaException).
        - Regla 2: El material debe estar disponible (MaterialNoDisponibleException).
        """
        # REGLA 1: Verificar multas del socio
        if self.socio.tiene_multa_pendiente():
            raise SocioConMultaException(
                f"No se puede realizar el préstamo: El socio {self.socio.nombre} (RUT: {self.socio.rut}) registra multas pendientes."
            )

        # REGLA 2: Verificar disponibilidad del material
        if not material.esta_disponible():
            raise MaterialNoDisponibleException(
                f"No se puede prestar '{material.titulo}' (Código: {material.codigo}): Su estado actual es '{material.estado.value}'."
            )

        # Si cumple ambas reglas, se genera la línea de detalle
        detalle = DetallePrestamo(material=material)
        self.__detalles.append(detalle)
        
        # Marcamos el material como PRESTADO
        material.estado = EstadoMaterial.PRESTADO
        return detalle

    def __str__(self) -> str:
        return f"Préstamo #{self.id_prestamo or 'Nuevo'} | Fecha: {self.fecha_registro} | Socio: {self.socio.nombre} | {len(self.detalles)} ítems"
