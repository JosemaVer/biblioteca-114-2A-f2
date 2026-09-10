# Definicion de la clase Persona
class Persona:
    # Metodo estatico para validar el formato y digito verificador del RUT chileno (Modulo 11)
    @staticmethod
    def validar_rut(rut: str) -> bool:
        # Limpiar el RUT eliminando puntos, guiones y espacios en blanco
        rut_limpio = rut.replace(".", "").replace("-", "").strip().upper()

        # Verificar que tenga un largo minimo y maximo valido (cuerpo numerico y digito verificador)
        if len(rut_limpio) < 8 or len(rut_limpio) > 9:
            return False

        # Separar el cuerpo numerico y el digito verificador proporcionado
        cuerpo = rut_limpio[:-1]
        dv_ingresado = rut_limpio[-1]

        # Comprobar que el cuerpo este compuesto unicamente por digitos
        if not cuerpo.isdigit():
            return False

        # Algoritmo de calculo Modulo 11
        suma = 0
        multiplicador = 2

        # Iterar sobre el cuerpo de derecha a izquierda
        for caracter in reversed(cuerpo):
            suma += int(caracter) * multiplicador
            multiplicador += 1
            if multiplicador > 7:
                multiplicador = 2

        # Calcular el digito verificador esperado
        resto = suma % 11
        resultado = 11 - resto

        if resultado == 11:
            dv_esperado = "0"
        elif resultado == 10:
            dv_esperado = "K"
        else:
            dv_esperado = str(resultado)

        # Comparar si el digito verificador ingresado coincide con el calculado
        return dv_ingresado == dv_esperado

    # Metodo constructor que inicializa los atributos y valida el RUT al instanciar
    def __init__(self, rut: str, nombre: str, apellido1: str, apellido2: str, email: str):
        # Validar el RUT antes de registrar al usuario
        if not Persona.validar_rut(rut):
            raise ValueError(f"El RUT '{rut}' ingresado no es valido.")

        # Asignacion de atributos de la instancia con tipado
        self.rut: str = rut.strip()
        self.nombre: str = nombre.strip()
        self.apellido1: str = apellido1.strip()
        self.apellido2: str = apellido2.strip()
        self.email: str = email.strip()

    # Metodo para representar la informacion completa de la persona
    def __str__(self) -> str:
        return f"{self.nombre} {self.apellido1} {self.apellido2} (RUT: {self.rut}, Email: {self.email})"
