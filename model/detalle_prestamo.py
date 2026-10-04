"""
Clase DetallePrestamo: Representa cada ítem o ejemplar prestado dentro de una transacción de préstamo.
"""
from datetime import datetime, timedelta, date
from model.material import Material
from model.estados import EstadoMaterial


class DetallePrestamo:
    """
    Línea de detalle que asocia un material prestado con su fecha de vencimiento y renovaciones.
    """
    def __init__(self, material: Material, fecha_vencimiento=None, renovaciones_usadas: int = 0, id_detalle: int = None):
        self.id_detalle = id_detalle
        self.material = material
        self.renovaciones_usadas = renovaciones_usadas
        
        # Si no se especifica fecha de vencimiento, se calcula sumando getDiasPrestamo() a la fecha actual
        if fecha_vencimiento is None:
            dias = self.material.getDiasPrestamo()
            self.__fecha_vencimiento = date.today() + timedelta(days=dias)
        elif isinstance(fecha_vencimiento, str):
            self.__fecha_vencimiento = datetime.strptime(fecha_vencimiento, "%Y-%m-%d").date()
        elif isinstance(fecha_vencimiento, (datetime, date)):
            self.__fecha_vencimiento = fecha_vencimiento if isinstance(fecha_vencimiento, date) else fecha_vencimiento.date()
        else:
            raise ValueError("Formato de fecha de vencimiento no válido.")

    # ==========================================
    # Getter y Setter: Material
    # ==========================================
    @property
    def material(self) -> Material:
        return self.__material

    @material.setter
    def material(self, valor: Material):
        if not isinstance(valor, Material):
            raise TypeError("El objeto asociado debe ser una instancia de Material (Libro, Revista o Multimedia).")
        self.__material = valor

    # ==========================================
    # Getter: Fecha de Vencimiento
    # ==========================================
    @property
    def fecha_vencimiento(self) -> date:
        return self.__fecha_vencimiento

    # ==========================================
    # Getter y Setter: Renovaciones Usadas
    # ==========================================
    @property
    def renovaciones_usadas(self) -> int:
        return self.__renovaciones_usadas

    @renovaciones_usadas.setter
    def renovaciones_usadas(self, valor: int):
        try:
            num = int(valor)
            if num < 0:
                raise ValueError("Las renovaciones no pueden ser negativas.")
            self.__renovaciones_usadas = num
        except (TypeError, ValueError):
            raise ValueError("Las renovaciones deben ser un número entero.")

    # ==========================================
    # Lógica de Negocio: Renovar y Marcar Perdido
    # ==========================================
    def renovar(self) -> bool:
        """
        Intenta renovar el préstamo del material.
        Verifica si el material permite renovaciones según su polimorfismo (getMaxRenovaciones()).
        """
        max_renovaciones = self.material.getMaxRenovaciones()
        if self.__renovaciones_usadas < max_renovaciones:
            dias_extra = self.material.getDiasPrestamo()
            self.__fecha_vencimiento = self.__fecha_vencimiento + timedelta(days=dias_extra)
            self.__renovaciones_usadas += 1
            return True
        return False

    def marcar_perdido(self):
        """Marca el material asociado como EXTRAVIADO."""
        self.material.estado = EstadoMaterial.EXTRAVIADO

    def __str__(self) -> str:
        return f"- {self.material.titulo} | Vence: {self.fecha_vencimiento} | Renovaciones: {self.renovaciones_usadas}/{self.material.getMaxRenovaciones()}"
