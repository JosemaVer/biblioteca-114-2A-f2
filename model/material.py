"""
Clase base abstracta Material.
Define atributos comunes y métodos polimórficos getDiasPrestamo() y getMaxRenovaciones().
"""
from abc import ABC, abstractmethod
from model.estados import EstadoMaterial


class Material(ABC):
    """
    Clase abstracta que representa cualquier recurso prestable de la biblioteca.
    No puede instanciarse directamente; se deben usar sus subclases (Libro, Revista, Multimedia).
    """
    def __init__(self, codigo: str, titulo: str, estado: EstadoMaterial = EstadoMaterial.DISPONIBLE, valor_reposicion_usd: float = 0.0):
        self.codigo = codigo
        self.titulo = titulo
        self.estado = estado
        self.valor_reposicion_usd = valor_reposicion_usd

    # ==========================
    # Getter y Setter de Código
    # ==========================
    @property
    def codigo(self) -> str:
        return self.__codigo

    @codigo.setter
    def codigo(self, valor: str):
        if not valor or not str(valor).strip():
            raise ValueError("El código del material no puede estar vacío.")
        self.__codigo = str(valor).strip().upper()

    # ==========================
    # Getter y Setter de Título
    # ==========================
    @property
    def titulo(self) -> str:
        return self.__titulo

    @titulo.setter
    def titulo(self, valor: str):
        if not valor or not isinstance(valor, str) or not valor.strip():
            raise ValueError("El título del material no puede estar vacío.")
        self.__titulo = valor.strip()

    # ==========================
    # Getter y Setter de Estado
    # ==========================
    @property
    def estado(self) -> EstadoMaterial:
        return self.__estado

    @estado.setter
    def estado(self, valor):
        if isinstance(valor, str):
            # Mapeo flexible desde string
            for em in EstadoMaterial:
                if em.value.upper() == valor.strip().upper() or em.name.upper() == valor.strip().upper():
                    self.__estado = em
                    return
            raise ValueError(f"Estado de material '{valor}' no reconocido.")
        elif isinstance(valor, EstadoMaterial):
            self.__estado = valor
        else:
            raise ValueError("El estado debe ser una instancia de EstadoMaterial o texto válido.")

    # =======================================
    # Getter y Setter de Valor Reposición USD
    # =======================================
    @property
    def valor_reposicion_usd(self) -> float:
        return self.__valor_reposicion_usd

    @valor_reposicion_usd.setter
    def valor_reposicion_usd(self, valor: float):
        try:
            num = float(valor)
            if num < 0:
                raise ValueError("El valor de reposición no puede ser negativo.")
            self.__valor_reposicion_usd = num
        except (TypeError, ValueError):
            raise ValueError("El valor de reposición debe ser un número válido mayor o igual a cero.")

    # ================================================
    # Métodos Polimórficos (Sobrescritos en subclases)
    # ================================================
    @abstractmethod
    def getDiasPrestamo(self) -> int:
        """Retorna la cantidad de días permitidos para el préstamo según el tipo de material."""
        pass

    @abstractmethod
    def getMaxRenovaciones(self) -> int:
        """Retorna la cantidad máxima de renovaciones permitidas."""
        pass

    def esta_disponible(self) -> bool:
        """Verifica si el material está listo para ser prestado."""
        return self.__estado == EstadoMaterial.DISPONIBLE

    def __str__(self) -> str:
        return f"[{self.codigo}] {self.titulo} ({self.estado.value})"
