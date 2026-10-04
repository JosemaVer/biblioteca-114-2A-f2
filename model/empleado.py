"""
Clase abstracta Empleado que hereda de Persona.
"""
from model.persona import Persona


class Empleado(Persona):
    """
    Clase base para el personal de la biblioteca.
    Hereda de Persona (rut, nombre) y añade id_empleado y clave_acceso.
    """
    def __init__(self, rut: str, nombre: str, id_empleado: str, clave_acceso: str):
        super().__init__(rut, nombre)
        self.id_empleado = id_empleado
        self.clave_acceso = clave_acceso

    # ==================================
    # Getter y Setter para ID Empleado
    # ==================================
    @property
    def id_empleado(self) -> str:
        return self.__id_empleado

    @id_empleado.setter
    def id_empleado(self, valor: str):
        if not valor or not str(valor).strip():
            raise ValueError("El ID de empleado no puede estar vacío.")
        self.__id_empleado = str(valor).strip()

    # ==================================
    # Getter y Setter para Clave
    # ==================================
    @property
    def clave_acceso(self) -> str:
        return self.__clave_acceso

    @clave_acceso.setter
    def clave_acceso(self, valor: str):
        if not valor or not str(valor).strip():
            raise ValueError("La clave de acceso no puede estar vacía.")
        self.__clave_acceso = str(valor).strip()

    def autenticar(self, clave_ingresada: str) -> bool:
        """Verifica si la contraseña ingresada coincide con la clave de acceso."""
        return self.__clave_acceso == clave_ingresada.strip()

    def __str__(self) -> str:
        return f"{self.nombre} (ID: {self.id_empleado})"
