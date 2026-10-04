"""
Roles específicos de empleados: Bibliotecaria y Administradora.
"""
from model.empleado import Empleado


class Bibliotecaria(Empleado):
    """
    Rol encargado de la atención de mesón: préstamos y devoluciones.
    """
    def __init__(self, rut: str, nombre: str, id_empleado: str, clave_acceso: str):
        super().__init__(rut, nombre, id_empleado, clave_acceso)

    def __str__(self) -> str:
        return f"[Bibliotecaria] {self.nombre} (ID: {self.id_empleado})"


class Administradora(Empleado):
    """
    Rol encargado de la gestión general: altas/bajas de material y condonación de multas.
    """
    def __init__(self, rut: str, nombre: str, id_empleado: str, clave_acceso: str):
        super().__init__(rut, nombre, id_empleado, clave_acceso)

    def __str__(self) -> str:
        return f"[Administradora] {self.nombre} (ID: {self.id_empleado})"
