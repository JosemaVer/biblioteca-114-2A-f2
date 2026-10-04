"""
Subclase Multimedia que hereda de Material.
Sobrescribe getDiasPrestamo() retornando 3 días y getMaxRenovaciones() retornando 0.
"""
from model.material import Material
from model.estados import EstadoMaterial


class Multimedia(Material):
    """
    Representa material audiovisual (DVD, BluRay, CD interactivo, etc.).
    - Días de préstamo: 3 días.
    - Renovaciones permitidas: 0 renovaciones.
    """
    def __init__(self, codigo: str, titulo: str, formato: str = "DVD",
                 valor_reposicion_usd: float = 0.0, estado: EstadoMaterial = EstadoMaterial.DISPONIBLE):
        super().__init__(codigo, titulo, estado, valor_reposicion_usd)
        self.formato = formato

    # ================================
    # Getter y Setter: Formato
    # ================================
    @property
    def formato(self) -> str:
        return self.__formato

    @formato.setter
    def formato(self, valor: str):
        if not valor or not isinstance(valor, str) or not valor.strip():
            raise ValueError("El formato audiovisual no puede estar vacío (ej. DVD, BluRay).")
        self.__formato = valor.strip().upper()

    # =======================================
    # Polimorfismo: Reglas para Multimedia
    # =======================================
    def getDiasPrestamo(self) -> int:
        """El material multimedia se presta por 3 días."""
        return 3

    def getMaxRenovaciones(self) -> int:
        """El material multimedia no admite renovaciones."""
        return 0

    def __str__(self) -> str:
        return f"[Multimedia/{self.formato} - {self.codigo}] {self.titulo} | Estado: {self.estado.value}"
