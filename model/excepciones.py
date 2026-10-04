"""
Módulo de Excepciones Propias de Negocio.
Heredan de Exception para representar las dos reglas que impiden operaciones en la biblioteca.
"""

class SocioConMultaException(Exception):
    """
    Regla de Negocio 1:
    Se lanza cuando se intenta registrar un préstamo a un socio que tiene multas pendientes de pago.
    """
    def __init__(self, mensaje: str = "Operación denegada: El socio posee multas pendientes y no puede solicitar préstamos."):
        super().__init__(mensaje)


class MaterialNoDisponibleException(Exception):
    """
    Regla de Negocio 2:
    Se lanza cuando se intenta prestar un material que no se encuentra en estado DISPONIBLE (ej. ya está PRESTADO).
    """
    def __init__(self, mensaje: str = "Operación denegada: El material seleccionado no está disponible para préstamo."):
        super().__init__(mensaje)
