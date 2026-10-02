# Importamos la clase Enum desde el modulo estandar enum para crear enumeraciones con nombre
from enum import Enum

# Definicion de la enumeracion EstadoMaterial para representar los posibles estados fisicos/logicos de un recurso
class EstadoMaterial(Enum):
    # Estado cuando el material esta disponible en estanteria para prestamo
    DISPONIBLE = "Disponible"
    # Estado cuando el material fue prestado a un socio y esta en circulacion
    PRESTADO = "Prestado"
    # Estado cuando el material fue reportado como perdido o extraviado
    EXTRAVIADO = "Extraviado"

    # Metodo especial para representar el valor textual al convertir la enumeracion a string
    def __str__(self) -> str:
        # Retorna el valor en texto legible asignado a la constante
        return self.value

# Definicion de la enumeracion EstadoMulta para representar el ciclo de vida de una sancion monetaria
class EstadoMulta(Enum):
    # Estado cuando la multa fue generada y aun no ha sido saldada por el socio
    PENDIENTE = "Pendiente"
    # Estado cuando el socio pago el monto total de la deuda
    PAGADA = "Pagada"
    # Estado cuando una Administradora perdona o anula el cobro de la multa
    CONDONADA = "Condonada"

    # Metodo especial para representar el valor textual al convertir la enumeracion a string
    def __str__(self) -> str:
        # Retorna el valor legible asignado a la constante
        return self.value
