# Importamos la clase abstracta base Material
from material import Material
# Importamos la enumeracion de estados
from estados import EstadoMaterial

# Definicion de la clase Multimedia que hereda de Material
class Multimedia(Material):
    """Clase que representa un recurso multimedia (CD, DVD, Blu-Ray, etc.)."""

    # Constructor que inicializa los atributos de un item multimedia
    def __init__(
        self,
        codigo: str,
        titulo: str,
        formato: str,
        autor: str = "Desconocido",
        anio: int = None,
        estado: EstadoMaterial = EstadoMaterial.DISPONIBLE
    ):
        # Llamamos al constructor de la clase padre Material
        super().__init__(codigo, titulo, autor, anio, estado)
        # Validamos que el formato especificado no este vacio
        if not formato or not formato.strip():
            # Si esta vacio, lanzamos un error de valor
            raise ValueError("El formato multimedia no puede estar vacío (ej: DVD, Blu-ray, CD, Digital).")
        # Asignamos el formato eliminando espacios en blanco sobrantes
        self.formato: str = formato.strip()

    # Plazo de prestamo reducido para material multimedia: 3 dias
    def get_dias_prestamo(self) -> int:
        # Retorna el entero 3
        return 3

    # Politica de renovacion: no se permite renovar multimedia para alta rotacion
    def get_max_renovaciones(self) -> int:
        # Retorna 0 renovaciones
        return 0

    # Serializa a diccionario
    def to_dict(self) -> dict:
        # Extraemos el diccionario base
        data = super().to_dict()
        # Anadimos el atributo formato
        data.update({
            "formato": self.formato
        })
        # Retornamos los datos combinados
        return data

    # Metodo constructor a partir de diccionario
    @classmethod
    def from_dict(cls, data: dict) -> "Multimedia":
        # Instanciamos el objeto con los datos del diccionario
        return cls(
            codigo=data["codigo"],
            titulo=data["titulo"],
            formato=data["formato"],
            autor=data.get("autor", "Desconocido"),
            anio=data.get("anio"),
            estado=EstadoMaterial(data.get("estado", "Disponible"))
        )

    # Representacion en texto legible
    def __str__(self) -> str:
        # Retornamos el formato junto a los datos del material
        return f"💿 [Multimedia] {super().__str__()} | Formato: {self.formato}"
