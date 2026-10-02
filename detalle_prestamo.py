# Importamos datetime y timedelta para manejo de operaciones con fechas
from datetime import datetime, timedelta
# Importamos la clase abstracta Material
from material import Material
# Importamos la clase Libro
from libro import Libro
# Importamos la enumeracion de estados
from estados import EstadoMaterial

# Definicion de la clase DetallePrestamo que modela un item particular dentro de una transaccion de prestamo
class DetallePrestamo:
    """Clase que representa un ítem individual dentro de una solicitud de préstamo."""

    # Constructor que inicializa el material, fechas de inicio y vencimiento, y estado de devolucion
    def __init__(
        self,
        material: Material,
        fecha_inicio: datetime = None,
        fecha_vencimiento: datetime = None,
        renovaciones_usadas: int = 0,
        devuelto: bool = False,
        fecha_devolucion: datetime = None
    ):
        # Validamos que se haya suministrado un objeto material
        if not material:
            # Lanzamos error si no hay material
            raise ValueError("El detalle del préstamo debe asociar un material válido.")

        # Asignamos la referencia al objeto material
        self.material: Material = material
        # Asignamos la fecha de inicio del prestamo o la fecha y hora actual por defecto
        self.fecha_inicio: datetime = fecha_inicio or datetime.now()
        
        # Evaluamos si se proporciono una fecha de vencimiento explicita
        if fecha_vencimiento:
            # Si se paso explicitamente, la asignamos directamente
            self.fecha_vencimiento: datetime = fecha_vencimiento
        else:
            # Si no, calculamos sumando la cantidad de dias permitidos por el tipo de material
            self.fecha_vencimiento: datetime = self.fecha_inicio + timedelta(days=self.material.get_dias_prestamo())

        # Asignamos el contador de renovaciones que han sido utilizadas
        self.renovaciones_usadas: int = int(renovaciones_usadas)
        # Asignamos el estado booleano de devolucion
        self.devuelto: bool = bool(devuelto)
        # Asignamos la fecha en que se efectuo la devolucion si existe
        self.fecha_devolucion: datetime = fecha_devolucion

    # Metodo para extender la vigencia del prestamo
    def renovar(self) -> str:
        """Extiende la fecha de vencimiento según la política del material."""
        # Validamos que el item no haya sido devuelto ya
        if self.devuelto:
            # Lanzamos excepcion
            raise ValueError("No se puede renovar un ítem que ya fue devuelto.")

        # Validamos que el material no este reportado como perdido
        if self.material.estado == EstadoMaterial.EXTRAVIADO:
            # Lanzamos excepcion
            raise ValueError("No se puede renovar un material reportado como extraviado.")

        # Consultamos el limite maximo de renovaciones permitidas por el material
        max_renov = self.material.get_max_renovaciones()
        # Verificamos si ya alcanzo o supero el limite
        if self.renovaciones_usadas >= max_renov:
            # Lanzamos excepcion informando el limite
            raise ValueError(f"Límite de renovaciones alcanzado ({self.renovaciones_usadas}/{max_renov}) para este material.")

        # Obtenemos la cantidad de dias de extension segun el material
        dias = self.material.get_dias_prestamo()
        # Sumamos los dias a la fecha de vencimiento actual
        self.fecha_vencimiento += timedelta(days=dias)
        # Incrementamos en uno el contador de renovaciones usadas
        self.renovaciones_usadas += 1
        # Retornamos mensaje de exito
        return f"Renovación exitosa. Nueva fecha de vencimiento: {self.fecha_vencimiento.strftime('%Y-%m-%d')}"

    # Metodo para reportar el material como extraviado
    def marcar_perdido(self) -> None:
        """Marca el material asociado como extraviado."""
        # Invocamos el metodo correspondiente en el objeto material
        self.material.marcar_extraviado()

    # Metodo para procesar la devolucion fisica del item
    def registrar_devolucion(self, fecha_entrega: datetime = None) -> None:
        """Marca el ítem como devuelto y restaura el estado del material."""
        # Cambiamos la bandera booleana a True
        self.devuelto = True
        # Registramos la fecha de entrega
        self.fecha_devolucion = fecha_entrega or datetime.now()
        # Cambiamos el estado del material de vuelta a DISPONIBLE
        self.material.devolver()

    # Metodo para calcular la cantidad de dias de atraso respecto al plazo estipulado
    def dias_de_retraso(self, fecha_referencia: datetime = None) -> int:
        """Calcula cuántos días de retraso tiene el ítem respecto a la fecha de vencimiento."""
        # Determinamos la fecha de corte: fecha de devolucion si ya devolvio, o fecha actual si sigue en mora
        fecha_evaluar = self.fecha_devolucion if self.devuelto else (fecha_referencia or datetime.now())
        # Si la fecha de corte supera el vencimiento
        if fecha_evaluar > self.fecha_vencimiento:
            # Calculamos y retornamos la diferencia en dias
            return (fecha_evaluar.date() - self.fecha_vencimiento.date()).days
        # Si entrego a tiempo o no ha vencido, retornamos 0
        return 0

    # Serializa el detalle a un diccionario JSON
    def to_dict(self) -> dict:
        # Retornamos el diccionario estructurado
        return {
            "codigo_material": self.material.codigo,
            "fecha_inicio": self.fecha_inicio.strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_vencimiento": self.fecha_vencimiento.strftime("%Y-%m-%d %H:%M:%S"),
            "renovaciones_usadas": self.renovaciones_usadas,
            "devuelto": self.devuelto,
            "fecha_devolucion": self.fecha_devolucion.strftime("%Y-%m-%d %H:%M:%S") if self.fecha_devolucion else None
        }

    # Representacion en texto del detalle del prestamo
    def __str__(self) -> str:
        # Definimos etiqueta visual del estado
        estado_str = "✅ Devuelto" if self.devuelto else ("⚠️ EXTRAVIADO" if self.material.estado == EstadoMaterial.EXTRAVIADO else "⏳ En préstamo")
        # Retornamos el detalle formateado
        return (
            f"  - [{self.material.codigo}] {self.material.titulo} | "
            f"Vence: {self.fecha_vencimiento.strftime('%Y-%m-%d')} | "
            f"Renovaciones: {self.renovaciones_usadas}/{self.material.get_max_renovaciones()} | "
            f"Estado: {estado_str}"
        )
