# Importamos la clase abstracta Material
from material import Material
# Importamos la enumeracion EstadoMaterial
from estados import EstadoMaterial

# Definicion de la clase Revista que hereda de Material
class Revista(Material):
    """Clase que representa una revista o publicacion periodica en la biblioteca."""

    # Constructor que recibe los datos de la revista incluyendo numero de edicion
    def __init__(
        self,
        codigo: str,
        titulo: str,
        numero_edicion: int,
        autor: str = "Varios",
        anio: int = None,
        estado: EstadoMaterial = EstadoMaterial.DISPONIBLE
    ):
        # Invocamos el constructor de Material
        super().__init__(codigo, titulo, autor, anio, estado)
        # Validamos que el numero de edicion sea un entero mayor a cero
        if int(numero_edicion) <= 0:
            # Si es menor o igual a cero, lanzamos excepcion
            raise ValueError("El número de edición debe ser un entero positivo.")
        # Asignamos el numero de edicion
        self.numero_edicion: int = int(numero_edicion)

    # Implementacion concreta del plazo: las revistas se prestan por 7 dias
    def get_dias_prestamo(self) -> int:
        # Retorna 7 dias
        return 7

    # Implementacion concreta de renovaciones: maximo 1 renovacion para revistas
    def get_max_renovaciones(self) -> int:
        # Retorna 1
        return 1

    # Serializa los datos de la revista a diccionario
    def to_dict(self) -> dict:
        # Obtenemos los campos comunes
        data = super().to_dict()
        # Anadimos el atributo propio de revista
        data.update({
            "numero_edicion": self.numero_edicion
        })
        # Retornamos los datos completos
        return data

    # Metodo de fabrica para instanciar Revista desde un diccionario guardado
    @classmethod
    def from_dict(cls, data: dict) -> "Revista":
        # Retornamos la nueva instancia con los datos parseados
        return cls(
            codigo=data["codigo"],
            titulo=data["titulo"],
            numero_edicion=data["numero_edicion"],
            autor=data.get("autor", "Varios"),
            anio=data.get("anio"),
            estado=EstadoMaterial(data.get("estado", "Disponible"))
        )

    # Representacion en cadena de texto de la revista
    def __str__(self) -> str:
        # Retornamos la representacion formateada
        return f"📰 [Revista] {super().__str__()} | Edición #{self.numero_edicion}"
