# Importamos la clase abstracta base Material
from material import Material
# Importamos la enumeracion EstadoMaterial
from estados import EstadoMaterial

# Definicion de la clase Libro que hereda de la clase base Material
class Libro(Material):
    """Clase que representa un libro en la biblioteca."""

    # Constructor con parametros especificos para Libros (extranjero, reposicion en CLP o USD)
    def __init__(
        self,
        codigo: str,
        titulo: str,
        autor: str = "Desconocido",
        anio: int = None,
        es_extranjero: bool = False,
        valor_reposicion_pesos: float = 15000.0,
        valor_reposicion_dolares: float = 20.0,
        estado: EstadoMaterial = EstadoMaterial.DISPONIBLE
    ):
        # Invocamos el constructor de la clase padre Material para inicializar atributos comunes
        super().__init__(codigo, titulo, autor, anio, estado)
        # Convertimos y asignamos el flag booleano que indica si el libro es importado/extranjero
        self.es_extranjero: bool = bool(es_extranjero)
        # Asignamos el costo base de reposicion en Pesos Chilenos
        self.valor_reposicion_pesos: float = float(valor_reposicion_pesos)
        # Asignamos el costo base de reposicion en Dolares Americanos
        self.valor_reposicion_dolares: float = float(valor_reposicion_dolares)

    # Implementacion concreta del metodo abstracto: los libros se prestan por 14 dias
    def get_dias_prestamo(self) -> int:
        # Retorna el entero 14 dias
        return 14

    # Implementacion concreta del metodo abstracto: los libros permiten hasta 2 renovaciones
    def get_max_renovaciones(self) -> int:
        # Retorna el entero 2
        return 2

    # Metodo para calcular el costo de reposicion aplicando el cambio de divisa si corresponde
    def calcular_valor_reposicion(self, valor_dolar_dia: float = 950.0) -> float:
        """Calcula el valor de reposición en pesos chilenos según si es nacional o importado."""
        # Verificamos si el libro fue catalogado como extranjero
        if self.es_extranjero:
            # Multiplicamos el valor en dolares por la cotizacion del dia y redondeamos a 2 decimales
            return round(self.valor_reposicion_dolares * valor_dolar_dia, 2)
        # Si es nacional, retornamos directamente el valor en pesos chilenos
        return float(self.valor_reposicion_pesos)

    # Serializa el libro a un diccionario incluyendo sus atributos propios
    def to_dict(self) -> dict:
        # Obtenemos el diccionario base de la clase padre
        data = super().to_dict()
        # Anadimos los campos especificos de libro
        data.update({
            "es_extranjero": self.es_extranjero,
            "valor_reposicion_pesos": self.valor_reposicion_pesos,
            "valor_reposicion_dolares": self.valor_reposicion_dolares
        })
        # Retornamos el diccionario completo
        return data

    # Metodo de clase para reconstruir una instancia de Libro a partir de un diccionario JSON
    @classmethod
    def from_dict(cls, data: dict) -> "Libro":
        # Instanciamos la clase con los valores desempaquetados del diccionario
        return cls(
            codigo=data["codigo"],
            titulo=data["titulo"],
            autor=data.get("autor", "Desconocido"),
            anio=data.get("anio"),
            es_extranjero=data.get("es_extranjero", False),
            valor_reposicion_pesos=data.get("valor_reposicion_pesos", 15000.0),
            valor_reposicion_dolares=data.get("valor_reposicion_dolares", 20.0),
            estado=EstadoMaterial(data.get("estado", "Disponible"))
        )

    # Representacion textual del libro
    def __str__(self) -> str:
        # Determinamos el texto de origen segun el atributo booleano
        origen = "Extranjero" if self.es_extranjero else "Nacional"
        # Concatenamos el formato base con el origen
        return f"📖 [Libro] {super().__str__()} | Origen: {origen}"
