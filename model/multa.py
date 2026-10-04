"""
Clase Multa que gestiona penalizaciones monetarias asociadas a un socio.
"""
from model.estados import EstadoMulta


class Multa:
    """
    Representa una sanción monetaria a un socio (por retraso o extravío).
    """
    def __init__(self, monto: float, estado: EstadoMulta = EstadoMulta.PENDIENTE,
                 motivo: str = "Atraso en devolución", id_multa: int = None, rut_socio: str = None):
        self.id_multa = id_multa
        self.rut_socio = rut_socio
        self.monto = monto
        self.estado = estado
        self.motivo = motivo

    # ==========================
    # Getter y Setter: Monto
    # ==========================
    @property
    def monto(self) -> float:
        return self.__monto

    @monto.setter
    def monto(self, valor: float):
        try:
            num = float(valor)
            if num <= 0:
                raise ValueError("El monto de la multa debe ser mayor a 0.")
            self.__monto = round(num, 2)
        except (TypeError, ValueError):
            raise ValueError("El monto de la multa debe ser un valor numérico válido positivo.")

    # ==========================
    # Getter y Setter: Estado
    # ==========================
    @property
    def estado(self) -> EstadoMulta:
        return self.__estado

    @estado.setter
    def estado(self, valor):
        if isinstance(valor, str):
            for em in EstadoMulta:
                if em.value.upper() == valor.strip().upper() or em.name.upper() == valor.strip().upper():
                    self.__estado = em
                    return
            raise ValueError(f"Estado de multa '{valor}' no válido.")
        elif isinstance(valor, EstadoMulta):
            self.__estado = valor
        else:
            raise ValueError("El estado de la multa no es válido.")

    # ==========================
    # Métodos de Negocio
    # ==========================
    def pagar(self):
        """Marca la multa como PAGADA."""
        self.__estado = EstadoMulta.PAGADA

    def condonar(self):
        """Marca la multa como CONDONADA (perdonada administrativamente)."""
        self.__estado = EstadoMulta.CONDONADA

    def __str__(self) -> str:
        return f"Multa #{self.id_multa or 'N/A'}: ${self.monto:,.0f} CLP - Estado: {self.estado.value} ({self.motivo})"
