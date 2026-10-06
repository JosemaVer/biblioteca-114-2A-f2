"""
Clase base Persona con encapsulamiento y validación real de RUT chileno (Módulo 11).
"""

class Persona:
    """
    Clase base para toda persona registrada en el sistema.
    Aplica encapsulamiento mediante atributos privados (__rut, __nombre).
    """
    def __init__(self, rut: str, nombre: str, *, validar_rut: bool = True):
        # Asignamos a través de las propiedades para activar la validación en los setters
        self.__validar_rut = validar_rut
        self.rut = rut
        self.nombre = nombre

    # ==========================
    # Getter y Setter para RUT
    # ==========================
    @property
    def rut(self) -> str:
        """Retorna el RUT de la persona."""
        return self.__rut

    @rut.setter
    def rut(self, valor: str):
        """Valida y asigna el RUT chileno mediante el algoritmo Módulo 11."""
        if not valor or not isinstance(valor, str):
            raise ValueError("El RUT no puede estar vacío.")
        
        if self.__validar_rut and not self.validar_rut(valor):
            raise ValueError(f"El RUT '{valor}' no es válido (dígito verificador incorrecto o formato inválido).")
        
        self.__rut = self.formatear_rut(valor)

    # =============================
    # Getter y Setter para Nombre
    # =============================
    @property
    def nombre(self) -> str:
        """Retorna el nombre de la persona."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str):
        """Valida que el nombre no esté vacío."""
        if not valor or not isinstance(valor, str) or not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self.__nombre = valor.strip()

    # ======================================================
    # Algoritmo Módulo 11 para Validar RUT Chileno
    # ======================================================
    @staticmethod
    def formatear_rut(rut_completo: str) -> str:
        """
        Normaliza el RUT a formato canónico estándar 'XXXXXXXX-X' sin puntos.
        """
        limpio = str(rut_completo).replace("-", "").replace(".", "").upper().strip()
        if len(limpio) < 2:
            return limpio
        return f"{limpio[:-1]}-{limpio[-1]}"

    @staticmethod
    def validar_rut(rut_completo: str) -> bool:
        """
        Valida un RUT chileno usando el algoritmo oficial de Módulo 11.
        Acepta formatos como '12.345.678-5', '12345678-5' o '123456785'.
        """
        limpio = rut_completo.replace("-", "").replace(".", "").upper().strip()
        if len(limpio) < 2:
            return False

        cuerpo = limpio[:-1]
        dv_ingresado = limpio[-1]

        if not cuerpo.isdigit():
            return False

        # Multiplicación ponderada con la serie 2, 3, 4, 5, 6, 7
        suma = 0
        multiplicador = 2
        for digito in reversed(cuerpo):
            suma += int(digito) * multiplicador
            multiplicador = 2 if multiplicador == 7 else multiplicador + 1

        resto = suma % 11
        dv_esperado = 11 - resto
        if dv_esperado == 11:
            dv_calculado = "0"
        elif dv_esperado == 10:
            dv_calculado = "K"
        else:
            dv_calculado = str(dv_esperado)

        return dv_ingresado == dv_calculado

    def __str__(self) -> str:
        return f"{self.nombre} (RUT: {self.rut})"
