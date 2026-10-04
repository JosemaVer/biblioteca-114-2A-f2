"""
Subclase Libro que hereda de Material.
Sobrescribe getDiasPrestamo() retornando 14 días y getMaxRenovaciones() retornando 1.
"""
from model.material import Material
from model.estados import EstadoMaterial


class Libro(Material):
    """
    Representa un libro en la biblioteca.
    - Días de préstamo: 14 días.
    - Renovaciones permitidas: 1 renovación.
    - Permite calcular el valor en pesos si fue adquirido en dólares (extranjero).
    """
    def __init__(self, codigo: str, titulo: str, es_extranjero: bool = False,
                 valor_reposicion_usd: float = 0.0, valor_reposicion_pesos: int = 0,
                 estado: EstadoMaterial = EstadoMaterial.DISPONIBLE):
        super().__init__(codigo, titulo, estado, valor_reposicion_usd)
        self.es_extranjero = bool(es_extranjero)
        self.valor_reposicion_pesos = valor_reposicion_pesos

    # ========================================
    # Getter y Setter: Valor Reposición Pesos
    # ========================================
    @property
    def valor_reposicion_pesos(self) -> int:
        return self.__valor_reposicion_pesos

    @valor_reposicion_pesos.setter
    def valor_reposicion_pesos(self, valor: int):
        try:
            num = int(valor)
            if num < 0:
                raise ValueError("El valor en pesos no puede ser negativo.")
            self.__valor_reposicion_pesos = num
        except (TypeError, ValueError):
            raise ValueError("El valor en pesos debe ser un número entero válido.")

    # ====================================
    # Polimorfismo: Reglas para Libro
    # ====================================
    def getDiasPrestamo(self) -> int:
        """Los libros se prestan por 14 días."""
        return 14

    def getMaxRenovaciones(self) -> int:
        """Los libros se pueden renovar 1 vez."""
        return 1

    def calcularValorReposicion(self, valor_dolar_dia: float) -> float:
        """
        Calcula el valor de reposición final en CLP.
        Si es extranjero, multiplica el valor en USD por el dólar del día;
        de lo contrario, devuelve el valor en pesos fijado.
        """
        if self.es_extranjero:
            if valor_dolar_dia <= 0:
                raise ValueError("El valor del dólar debe ser mayor a 0.")
            return round(self.valor_reposicion_usd * valor_dolar_dia, 2)
        return float(self.valor_reposicion_pesos)

    def __str__(self) -> str:
        origen = "Extranjero" if self.es_extranjero else "Nacional"
        return f"[Libro - {self.codigo}] {self.titulo} | {origen} | Estado: {self.estado.value}"
