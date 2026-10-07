"""
Clase Socio que hereda de Persona y gestiona la dirección y el estado de multas del usuario.
"""
from model.persona import Persona
from model.estados import EstadoMulta


class Socio(Persona):
    """
    Representa a un socio lector de la biblioteca.
    Hereda de Persona (rut y nombre) y añade su dirección y control de multas.
    """
    def __init__(
        self,
        rut: str,
        nombre: str,
        direccion: str,
        *,
        validar_rut: bool = True,
    ):
        # Invocamos al constructor de la clase padre Persona
        super().__init__(rut, nombre, validar_rut=validar_rut)
        self.direccion = direccion
        self.__multas = []  # Lista privada de objetos Multa

    # ================================
    # Getter y Setter para Dirección
    # ================================
    @property
    def direccion(self) -> str:
        """Retorna la dirección de residencia del socio."""
        return self.__direccion

    @direccion.setter
    def direccion(self, valor: str):
        """Valida que la dirección no esté vacía."""
        if not valor or not isinstance(valor, str) or not valor.strip():
            raise ValueError("La dirección no puede estar vacía.")
        self.__direccion = valor.strip()

    # ================================
    # Gestión de Multas del Socio
    # ================================
    @property
    def multas(self) -> list:
        """Retorna la lista de multas asociadas al socio."""
        return self.__multas

    def agregar_multa(self, multa):
        """Asocia una nueva multa a la lista del socio."""
        self.__multas.append(multa)

    def tiene_multa_pendiente(self) -> bool:
        """
        Verifica si el socio tiene al menos una multa en estado PENDIENTE.
        Retorna True si tiene deudas pendientes, False si está al día.
        """
        for multa in self.__multas:
            # Comparamos tanto si es enum como si es string por compatibilidad
            estado_val = multa.estado.value if hasattr(multa.estado, 'value') else str(multa.estado)
            if estado_val == EstadoMulta.PENDIENTE.value:
                return True
        return False

    def __str__(self) -> str:
        estado_deuda = "CON MULTAS" if self.tiene_multa_pendiente() else "AL DÍA"
        return f"Socio: {self.nombre} | RUT: {self.rut} | Dir: {self.direccion} | Estado: {estado_deuda}"
