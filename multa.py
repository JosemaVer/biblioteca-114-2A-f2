# Importamos datetime para registrar marcas de tiempo exactas
from datetime import datetime
# Importamos la enumeracion EstadoMulta para tipar los estados de la multa
from estados import EstadoMulta

# Definicion de la clase Multa para gestionar sanciones por atrasos o perdidas
class Multa:
    """Clase que representa una sanción económica por retraso o pérdida."""

    # Constructor que inicializa los valores de la multa
    def __init__(self, id_multa: int, rut_socio: str, monto: float, motivo: str = "Atraso en devolución", estado: EstadoMulta = EstadoMulta.PENDIENTE, fecha_emision: str = None):
        # Validamos que el monto no sea un valor negativo
        if monto < 0:
            # Lanzamos excepcion si el monto es menor que cero
            raise ValueError("El monto de la multa no puede ser negativo.")

        # Asignamos el identificador numerico de la multa
        self.id_multa: int = int(id_multa)
        # Asignamos el RUT del socio infractor
        self.rut_socio: str = rut_socio.strip()
        # Asignamos el valor en dinero de la multa
        self.monto: float = float(monto)
        # Asignamos el motivo de la infraccion
        self.motivo: str = motivo.strip()
        # Asignamos el estado inicial de la multa asegurando que sea una instancia de EstadoMulta
        self.estado: EstadoMulta = estado if isinstance(estado, EstadoMulta) else EstadoMulta(estado)
        # Asignamos la fecha de emision actual si no se proporciona una
        self.fecha_emision: str = fecha_emision or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Metodo para procesar el pago de la multa por parte del socio
    def pagar(self) -> None:
        """Marca la multa como pagada."""
        # Verificamos si la multa ya habia sido pagada previamente
        if self.estado == EstadoMulta.PAGADA:
            # Lanzamos error para evitar pagos duplicados
            raise ValueError("La multa ya se encuentra pagada.")
        # Verificamos si la multa fue perdonada previamente
        if self.estado == EstadoMulta.CONDONADA:
            # Lanzamos error ya que no requiere recaudacion
            raise ValueError("La multa está condonada y no requiere pago.")
        # Cambiamos el estado a PAGADA
        self.estado = EstadoMulta.PAGADA

    # Metodo para condonar/perdonar la multa (accion exclusiva de Administradora)
    def condonar(self) -> None:
        """Marca la multa como condonada (perdonada)."""
        # Validamos que no se intente condonar una multa que ya fue cobrada y pagada
        if self.estado == EstadoMulta.PAGADA:
            # Lanzamos excepcion
            raise ValueError("No se puede condonar una multa que ya fue pagada.")
        # Cambiamos el estado a CONDONADA
        self.estado = EstadoMulta.CONDONADA

    # Metodo auxiliar que indica si la multa sigue impaga y activa
    def esta_pendiente(self) -> bool:
        # Retorna True si el estado es PENDIENTE
        return self.estado == EstadoMulta.PENDIENTE

    # Serializa la multa a diccionario para almacenamiento JSON
    def to_dict(self) -> dict:
        # Retornamos el mapeo de campos
        return {
            "id_multa": self.id_multa,
            "rut_socio": self.rut_socio,
            "monto": self.monto,
            "motivo": self.motivo,
            "estado": self.estado.value,
            "fecha_emision": self.fecha_emision
        }

    # Metodo de fabrica para reconstruir la Multa desde un diccionario JSON
    @classmethod
    def from_dict(cls, data: dict) -> "Multa":
        # Creamos y retornamos la instancia con los valores cargados
        return cls(
            id_multa=data["id_multa"],
            rut_socio=data["rut_socio"],
            monto=data["monto"],
            motivo=data.get("motivo", "Atraso en devolución"),
            estado=EstadoMulta(data.get("estado", "Pendiente")),
            fecha_emision=data.get("fecha_emision")
        )

    # Representacion en texto de la multa
    def __str__(self) -> str:
        # Retornamos los datos formateados con moneda y fecha
        return f"Multa #{self.id_multa} | Socio RUT: {self.rut_socio} | Monto: ${self.monto:,.0f} | Motivo: {self.motivo} | Estado: {self.estado.value} | Fecha: {self.fecha_emision}"
