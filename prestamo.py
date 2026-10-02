# Importamos datetime para registrar la fecha del prestamo
from datetime import datetime
# Importamos la clase Socio
from socio import Socio
# Importamos la clase Empleado
from empleado import Empleado
# Importamos la clase DetallePrestamo
from detalle_prestamo import DetallePrestamo
# Importamos la clase Material
from material import Material

# Definicion de la clase Prestamo que representa la cabecera del documento de prestamo
class Prestamo:
    """Clase Cabecera del Préstamo que asocia un Socio, un Empleado y múltiples ítems."""

    # Constructor de la cabecera de prestamo
    def __init__(
        self,
        id_prestamo: int,
        socio: Socio,
        empleado: Empleado,
        fecha_registro: datetime = None,
        detalles: list[DetallePrestamo] = None
    ):
        # Validamos que se proporcione un socio
        if not socio:
            # Lanzamos error si falta el socio
            raise ValueError("El préstamo debe estar asignado a un socio.")
        # Validamos que se proporcione el empleado que atiende
        if not empleado:
            # Lanzamos error si falta el empleado
            raise ValueError("El préstamo debe estar registrado por un empleado.")

        # Asignamos el identificador numerico del prestamo
        self.id_prestamo: int = int(id_prestamo)
        # Asignamos la referencia al socio
        self.socio: Socio = socio
        # Asignamos la referencia al empleado responsable
        self.empleado: Empleado = empleado
        # Asignamos la fecha y hora de creacion
        self.fecha_registro: datetime = fecha_registro or datetime.now()
        # Inicializamos o asignamos la lista de lineas de detalle
        self.detalles: list[DetallePrestamo] = detalles if detalles is not None else []

    # Metodo para agregar un item de material bibliografico al prestamo
    def agregar_detalle(self, material: Material) -> DetallePrestamo:
        """Agrega un material al préstamo y actualiza su estado a Prestado."""
        # Verificamos si el material esta libre
        if not material.esta_disponible():
            # Lanzamos excepcion si no esta disponible
            raise ValueError(f"El material '{material.titulo}' no está disponible.")
        
        # Marcamos el material como PRESTADO
        material.prestar()
        # Creamos una nueva linea de detalle con la fecha del prestamo
        detalle = DetallePrestamo(material=material, fecha_inicio=self.fecha_registro)
        # Anadimos la linea de detalle a la lista del prestamo
        self.detalles.append(detalle)
        # Retornamos el objeto detalle creado
        return detalle

    # Metodo para verificar si todos los libros/revistas del prestamo ya fueron devueltos
    def esta_completamente_devuelto(self) -> bool:
        """Indica si todos los ítems del préstamo fueron devueltos."""
        # Retorna True si hay detalles y todos tienen el flag devuelto en True
        return len(self.detalles) > 0 and all(d.devuelto for d in self.detalles)

    # Serializa la cabecera y sus detalles a diccionario JSON
    def to_dict(self) -> dict:
        # Retornamos el diccionario completo
        return {
            "id_prestamo": self.id_prestamo,
            "rut_socio": self.socio.rut,
            "rut_empleado": self.empleado.rut,
            "fecha_registro": self.fecha_registro.strftime("%Y-%m-%d %H:%M:%S"),
            "detalles": [d.to_dict() for d in self.detalles]
        }

    # Representacion visual del ticket de prestamo
    def __str__(self) -> str:
        # Definimos el estado global del ticket
        estado = "Completado (Devuelto)" if self.esta_completamente_devuelto() else "Activo / Pendiente"
        # Construimos el encabezado del ticket
        cadena = (
            f"\n========================================\n"
            f"📄 PRÉSTAMO #{self.id_prestamo} [{estado}]\n"
            f"Fecha Registro : {self.fecha_registro.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Socio          : {self.socio.nombre} {self.socio.apellido1} (RUT: {self.socio.rut})\n"
            f"Atendido por   : {self.empleado.nombre} {self.empleado.apellido1} ({getattr(self.empleado, 'cargo', 'Empleado')})\n"
            f"Ítems prestados:\n"
        )
        # Iteramos agregando cada detalle con su estado
        for det in self.detalles:
            cadena += f"{det}\n"
        # Cerramos la linea separadora
        cadena += "========================================"
        # Retornamos la cadena construida
        return cadena
