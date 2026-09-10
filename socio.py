from persona import Persona

# Definicion de la clase Socio que hereda de Persona
class Socio(Persona):
    # Metodo constructor que inicializa los atributos heredados y propios del socio
    def __init__(self, rut: str, nombre: str, apellido1: str, apellido2: str, email: str, numero_socio: int = None):
        # Llamada al constructor de la clase padre (Persona) con la validacion de RUT incluida
        super().__init__(rut, nombre, apellido1, apellido2, email)
        # Asignacion del numero de socio y lista de prestamos activos
        self.numero_socio: int = numero_socio
        self.prestamos_activos: list = []

    # Metodo para representar la informacion del socio
    def __str__(self) -> str:
        base_info = super().__str__()
        return f"Socio #{self.numero_socio} - {base_info}"
