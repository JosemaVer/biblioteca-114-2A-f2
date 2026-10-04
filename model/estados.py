"""
Módulo de Estados del Sistema.
Define las opciones fijas mediante Enumeraciones (Enum).
"""
from enum import Enum


class EstadoMaterial(Enum):
    """
    Representa los estados posibles en los que puede encontrarse un material.
    - DISPONIBLE: El material está en estantería listo para préstamo.
    - PRESTADO: El material está actualmente en manos de un socio.
    - EXTRAVIADO: El material fue reportado como perdido.
    """
    DISPONIBLE = "Disponible"
    PRESTADO = "Prestado"
    EXTRAVIADO = "Extraviado"


class EstadoMulta(Enum):
    """
    Representa los estados de una multa aplicada a un socio.
    - PENDIENTE: La multa está impaga e impide nuevos préstamos.
    - PAGADA: La multa fue cancelada por el socio.
    - CONDONADA: La multa fue perdonada administrativamente.
    """
    PENDIENTE = "Pendiente"
    PAGADA = "Pagada"
    CONDONADA = "Condonada"
