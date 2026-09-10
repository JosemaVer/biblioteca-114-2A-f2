from persona import Persona

# Definicion de la clase Empleado que hereda de Persona
class Empleado(Persona):
    # Metodo constructor que inicializa los atributos heredados y propios del empleado
    def __init__(self, rut: str, nombre: str, apellido1: str, apellido2: str, email: str, cargo: str = "Bibliotecario"):
        # Llamada al constructor de la clase padre (Persona) con la validacion de RUT incluida
        super().__init__(rut, nombre, apellido1, apellido2, email)
        # Asignacion del cargo del empleado en la biblioteca
        self.cargo: str = cargo

    # Metodo para representar la informacion del empleado
    def __str__(self) -> str:
        base_info = super().__str__()
        return f"Empleado [{self.cargo}] - {base_info}"
