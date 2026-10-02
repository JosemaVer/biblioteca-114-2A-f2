# Importamos la clase base Persona
from persona import Persona
# Importamos la clase Multa para tipar la lista de sanciones
from multa import Multa

# Definicion de la clase Socio que hereda de Persona y modela a los lectores de la biblioteca
class Socio(Persona):
    """Clase Socio que hereda de Persona y modela a los usuarios del sistema de préstamos."""

    # Constructor que inicializa los datos personales, de contacto y el identificador de socio
    def __init__(
        self,
        rut: str,
        nombre: str,
        apellido1: str,
        apellido2: str,
        email: str,
        direccion: str = "No especificada",
        numero_socio: int = None
    ):
        # Invocamos el constructor de Persona que ejecuta la validacion de RUT por Modulo 11
        super().__init__(rut, nombre, apellido1, apellido2, email)
        # Asignamos la direccion residencial del socio
        self.direccion: str = direccion.strip()
        # Asignamos el numero de carnet o identificador de socio
        self.numero_socio: int = numero_socio
        # Inicializamos la lista de multas asociadas al socio
        self.multas: list[Multa] = []

    # Metodo para asociar una nueva multa al socio
    def agregar_multa(self, multa: Multa) -> None:
        # Anadimos la multa a la coleccion interna
        self.multas.append(multa)

    # Metodo para consultar si el socio tiene impedimento por multas impagas
    def tiene_multa_pendiente(self) -> bool:
        """Verifica si el socio registra alguna multa en estado Pendiente."""
        # Retorna True si al menos una multa de la lista esta en estado PENDIENTE
        return any(m.esta_pendiente() for m in self.multas)

    # Metodo para calcular la deuda acumulada total
    def total_deuda_multas(self) -> float:
        """Retorna la suma total adeudada en multas pendientes."""
        # Suma los montos de todas las multas que sigan pendientes de pago
        return sum(m.monto for m in self.multas if m.esta_pendiente())

    # Serializa los datos del socio a un diccionario JSON
    def to_dict(self) -> dict:
        # Retornamos el mapeo de atributos
        return {
            "rut": self.rut,
            "nombre": self.nombre,
            "apellido1": self.apellido1,
            "apellido2": self.apellido2,
            "email": self.email,
            "direccion": self.direccion,
            "numero_socio": self.numero_socio
        }

    # Metodo de fabrica para instanciar un Socio a partir de datos guardados
    @classmethod
    def from_dict(cls, data: dict) -> "Socio":
        # Creamos y retornamos la nueva instancia de Socio
        return cls(
            rut=data["rut"],
            nombre=data["nombre"],
            apellido1=data["apellido1"],
            apellido2=data["apellido2"],
            email=data["email"],
            direccion=data.get("direccion", "No especificada"),
            numero_socio=data.get("numero_socio")
        )

    # Representacion en cadena de texto del socio
    def __str__(self) -> str:
        # Indicamos visualmente si esta al dia o en mora
        estado_multas = "⚠️ Con Deuda Pendiente" if self.tiene_multa_pendiente() else "✅ Al día"
        # Concatenamos la informacion heredada de Persona con los datos de Socio
        return f"Socio #{self.numero_socio or 'N/A'} - {super().__str__()} | Dirección: {self.direccion} | Estado: {estado_multas}"
