"""
Subclase Revista que hereda de Material.
Sobrescribe getDiasPrestamo() retornando 7 días y getMaxRenovaciones() retornando 0.
"""
from model.material import Material
from model.estados import EstadoMaterial


class Revista(Material):
    """
    Representa una revista o publicación periódica.
    - Días de préstamo: 7 días.
    - Renovaciones permitidas: 0 renovaciones.
    """
    def __init__(self, codigo: str, titulo: str, numero_edicion: int = 1,
                 valor_reposicion_usd: float = 0.0, estado: EstadoMaterial = EstadoMaterial.DISPONIBLE):
        super().__init__(codigo, titulo, estado, valor_reposicion_usd)
        self.numero_edicion = numero_edicion

    # ========================================
    # Getter y Setter: Número de Edición
    # ========================================
    @property
    def numero_edicion(self) -> int:
        return self.__numero_edicion

    @numero_edicion.setter
    def numero_edicion(self, valor: int):
        try:
            num = int(valor)
            if num <= 0:
                raise ValueError("El número de edición debe ser mayor a cero.")
            self.__numero_edicion = num
        except (TypeError, ValueError):
            raise ValueError("El número de edición debe ser un número entero positivo.")

    # ====================================
    # Polimorfismo: Reglas para Revista
    # ====================================
    def getDiasPrestamo(self) -> int:
        """Las revistas se prestan por 7 días."""
        return 7

    def getMaxRenovaciones(self) -> int:
        """Las revistas no admiten renovaciones."""
        return 0

    def __str__(self) -> str:
        return f"[Revista - {self.codigo}] {self.titulo} (Ed. #{self.numero_edicion}) | Estado: {self.estado.value}"
