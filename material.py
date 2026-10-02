# Importamos ABC (Abstract Base Class) y abstractmethod para obligar a las clases hijas a implementar ciertos metodos
from abc import ABC, abstractmethod
# Importamos la enumeracion EstadoMaterial para tipar y controlar el estado del recurso
from estados import EstadoMaterial

# Definicion de la clase abstracta Material que servira como plantilla base para Libros, Revistas y Multimedia
class Material(ABC):
    """Clase abstracta base para todos los materiales bibliográficos."""

    # Constructor que inicializa los atributos comunes a cualquier material bibliografico
    def __init__(self, codigo: str, titulo: str, autor: str = "Desconocido", anio: int = None, estado: EstadoMaterial = EstadoMaterial.DISPONIBLE):
        # Validamos que el codigo no sea nulo ni este en blanco
        if not codigo or not codigo.strip():
            # Si esta vacio, lanzamos un error de valor
            raise ValueError("El código del material no puede estar vacío.")
        # Validamos que el titulo no sea nulo ni este en blanco
        if not titulo or not titulo.strip():
            # Si esta vacio, lanzamos un error de valor
            raise ValueError("El título del material no puede estar vacío.")

        # Asignamos el codigo limpiando espacios y asegurando mayusculas
        self.codigo: str = codigo.strip().upper()
        # Asignamos el titulo eliminando espacios sobrantes al inicio y final
        self.titulo: str = titulo.strip()
        # Asignamos el autor eliminando espacios sobrantes
        self.autor: str = autor.strip()
        # Asignamos el anio de publicacion
        self.anio: int = anio
        # Asignamos el estado verificando si ya es una instancia de la Enum o convirtiendo el texto
        self.estado: EstadoMaterial = estado if isinstance(estado, EstadoMaterial) else EstadoMaterial(estado)

    # Decorador que indica que este metodo debe ser implementado obligatoriamente por las subclases
    @abstractmethod
    def get_dias_prestamo(self) -> int:
        """Retorna la cantidad de días permitidos para el préstamo según el tipo de material."""
        # Declaracion abstracta sin cuerpo
        pass

    # Decorador que obliga a definir la cantidad maxima de renovaciones permitidas
    @abstractmethod
    def get_max_renovaciones(self) -> int:
        """Retorna la cantidad máxima de renovaciones permitidas."""
        # Declaracion abstracta sin cuerpo
        pass

    # Metodo que consulta si el material se encuentra en condiciones de ser prestado
    def esta_disponible(self) -> bool:
        # Retorna True solo si el estado actual es DISPONIBLE
        return self.estado == EstadoMaterial.DISPONIBLE

    # Metodo para cambiar el estado a prestado tras una solicitud
    def prestar(self) -> None:
        # Verificamos si el material esta disponible antes de cambiar el estado
        if not self.esta_disponible():
            # Si no esta disponible lanzamos una excepcion explicativa
            raise ValueError(f"El material '{self.titulo}' (Código: {self.codigo}) no está disponible para préstamo (Estado actual: {self.estado.value}).")
        # Cambiamos el estado a PRESTADO
        self.estado = EstadoMaterial.PRESTADO

    # Metodo para marcar el material como devuelto a la biblioteca
    def devolver(self) -> None:
        # Restauramos el estado a DISPONIBLE
        self.estado = EstadoMaterial.DISPONIBLE

    # Metodo para reportar el material como extraviado o no devuelto
    def marcar_extraviado(self) -> None:
        # Cambiamos el estado a EXTRAVIADO
        self.estado = EstadoMaterial.EXTRAVIADO

    # Metodo para serializar el objeto a un diccionario compatible con JSON
    def to_dict(self) -> dict:
        # Retornamos los atributos clave en formato clave-valor
        return {
            "tipo": self.__class__.__name__,
            "codigo": self.codigo,
            "titulo": self.titulo,
            "autor": self.autor,
            "anio": self.anio,
            "estado": self.estado.value
        }

    # Metodo para obtener una representacion en texto legible del material
    def __str__(self) -> str:
        # Retornamos el codigo, titulo, autor, anio y estado formateados
        return f"[{self.codigo}] {self.titulo} - Autor: {self.autor} ({self.anio or 'S/A'}) [{self.estado.value}]"
