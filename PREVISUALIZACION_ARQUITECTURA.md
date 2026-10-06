# 📋 Previsualización: Arquitectura y Modelos Base (Fase 1 y 2)

---

## 1. Arquitectura de Carpetas y Archivos

```text
biblioteca-114-2A-f2/
│
├── data/                       <-- Carpeta para la base de datos
│   └── biblioteca.db           <-- Base de datos SQLite
│
├── model/                      <-- Capa de Modelo (POO)
│   ├── __init__.py
│   ├── estados.py              <-- Enums: EstadoMaterial, EstadoMulta
│   ├── excepciones.py          <-- Excepciones de negocio personalizadas
│   ├── persona.py              <-- Clase base Persona (validación de RUT con algoritmo Módulo 11)
│   ├── socio.py                <-- Clase Socio (hereda de Persona, multas y dirección)
│   ├── empleado.py             <-- Clase abstracta Empleado (hereda de Persona, credenciales)
│   ├── roles.py                <-- Bibliotecaria y Administradora
│   ├── material.py             <-- Clase abstracta Material
│   ├── libro.py                <-- Clase Libro (14 días, cálculo valor USD con API)
│   ├── revista.py              <-- Clase Revista (7 días)
│   ├── multimedia.py           <-- Clase Multimedia (3 días)
│   ├── multa.py                <-- Clase Multa
│   ├── detalle_prestamo.py     <-- Línea de detalle de préstamo
│   └── prestamo.py             <-- Transacción de préstamo
│
├── dao/                        <-- Capa de Persistencia (SQLite seguro con '?')
│   ├── __init__.py
│   ├── conexion.py             <-- Conexión a SQLite y creación automática de tablas
│   ├── material_dao.py         <-- CRUD de Materiales
│   ├── socio_dao.py            <-- CRUD de Socios
│   └── prestamo_dao.py         <-- Transacción de Préstamos y sus Detalles
│
├── services/                   <-- Servicios externos
│   ├── __init__.py
│   └── api_dolar.py            <-- Consulta a mindicador.cl con timeout y valor de contingencia (984.82 CLP)
│
├── main.py                     <-- Menú interactivo CLI con validación de entradas
├── requirements.txt            <-- requests==2.32.3
└── README.md                   <-- Documentación y justificaciones de seguridad e IA
```

---

## 2. Previsualización de Código: Primer Bloque

### Archivo 1: `model/estados.py`
```python
"""
Módulo de Estados del Sistema.
Define las opciones fijas mediante Enumeraciones (Enum).
"""
from enum import Enum


class EstadoMaterial(Enum):
    """Estados posibles para un material en la biblioteca."""
    DISPONIBLE = "Disponible"
    PRESTADO = "Prestado"
    EXTRAVIADO = "Extraviado"


class EstadoMulta(Enum):
    """Estados posibles para una multa de un socio."""
    PENDIENTE = "Pendiente"
    PAGADA = "Pagada"
    CONDONADA = "Condonada"
```

---

### Archivo 2: `model/excepciones.py`
```python
"""
Módulo de Excepciones Propias de Negocio.
Heredan de Exception para representar las dos reglas que impiden operaciones.
"""

class SocioConMultaException(Exception):
    """Regla 1: Impide prestar material a un socio que tenga multas pendientes."""
    def __init__(self, mensaje: str = "Operación cancelada: El socio registra multas pendientes."):
        super().__init__(mensaje)


class MaterialNoDisponibleException(Exception):
    """Regla 2: Impide prestar un material que no esté en estado DISPONIBLE."""
    def __init__(self, mensaje: str = "Operación cancelada: El material no está disponible para préstamo."):
        super().__init__(mensaje)
```

---

### Archivo 3: `model/persona.py`
```python
"""
Clase base Persona con encapsulamiento y validación real de RUT chileno (Módulo 11).
"""

class Persona:
    def __init__(self, rut: str, nombre: str):
        # Validamos en el setter antes de guardar en las variables privadas
        self.rut = rut
        self.nombre = nombre

    # --- Getter y Setter para RUT ---
    @property
    def rut(self) -> str:
        return self.__rut

    @rut.setter
    def rut(self, valor: str):
        if not valor or not isinstance(valor, str):
            raise ValueError("El RUT no puede estar vacío.")

        limpio = valor.strip().replace(".", "").upper()
        if not self.validar_rut(limpio):
            raise ValueError(f"El RUT '{valor}' no es válido (dígito verificador incorrecto o formato inválido).")

        self.__rut = limpio

    # --- Getter y Setter para Nombre ---
    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not isinstance(valor, str) or not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self.__nombre = valor.strip()

    # --- Algoritmo Módulo 11 para Validar RUT Chileno ---
    @staticmethod
    def validar_rut(rut_completo: str) -> bool:
        """
        Valida un RUT chileno usando el algoritmo oficial de Módulo 11.
        Acepta formatos como '12345678-5' o '123456785'.
        """
        limpio = rut_completo.replace("-", "").replace(".", "").upper().strip()
        if len(limpio) < 2:
            return False

        cuerpo = limpio[:-1]
        dv_ingresado = limpio[-1]

        if not cuerpo.isdigit():
            return False

        # Cálculo de la suma ponderada
        suma = 0
        multiplicador = 2
        for digito in reversed(cuerpo):
            suma += int(digito) * multiplicador
            multiplicador = 2 if multiplicador == 7 else multiplicador + 1

        resto = suma % 11
        dv_esperado = 11 - resto
        if dv_esperado == 11:
            dv_calculado = "0"
        elif dv_esperado == 10:
            dv_calculado = "K"
        else:
            dv_calculado = str(dv_esperado)

        return dv_ingresado == dv_calculado
```

---

### Archivo 4: `model/socio.py`
```python
"""
Clase Socio que hereda de Persona y gestiona dirección y estado de multas.
"""
from model.persona import Persona
from model.estados import EstadoMulta


class Socio(Persona):
    def __init__(self, rut: str, nombre: str, direccion: str):
        # Llamamos al constructor de la clase padre Persona
        super().__init__(rut, nombre)
        self.direccion = direccion
        self.__multas = []  # Lista de objetos Multa asociados al socio

    @property
    def direccion(self) -> str:
        return self.__direccion

    @direccion.setter
    def direccion(self, valor: str):
        if not valor or not isinstance(valor, str) or not valor.strip():
            raise ValueError("La dirección no puede estar vacía.")
        self.__direccion = valor.strip()

    @property
    def multas(self) -> list:
        return self.__multas

    def agregar_multa(self, multa):
        """Asocia una nueva multa al socio."""
        self.__multas.append(multa)

    def tiene_multa_pendiente(self) -> bool:
        """
        Verifica si el socio tiene al menos una multa en estado PENDIENTE.
        Retorna True si tiene multas impagas, False si está al día.
        """
        for multa in self.__multas:
            if multa.estado == EstadoMulta.PENDIENTE:
                return True
        return False
```

---

### Archivo 5: `model/empleado.py` y `model/roles.py`
```python
"""
Jerarquía de Empleados: Empleado (base), Bibliotecaria y Administradora.
"""
from model.persona import Persona


class Empleado(Persona):
    """Clase base para todos los trabajadores de la biblioteca."""
    def __init__(self, rut: str, nombre: str, id_empleado: str, clave_acceso: str):
        super().__init__(rut, nombre)
        self.id_empleado = id_empleado
        self.clave_acceso = clave_acceso

    @property
    def id_empleado(self) -> str:
        return self.__id_empleado

    @id_empleado.setter
    def id_empleado(self, valor: str):
        if not valor or not str(valor).strip():
            raise ValueError("El ID de empleado no puede estar vacío.")
        self.__id_empleado = str(valor).strip()

    @property
    def clave_acceso(self) -> str:
        return self.__clave_acceso

    @clave_acceso.setter
    def clave_acceso(self, valor: str):
        if not valor or not str(valor).strip():
            raise ValueError("La clave de acceso no puede estar vacía.")
        self.__clave_acceso = str(valor).strip()


class Bibliotecaria(Empleado):
    """Rol encargado de la atención de préstamos y devoluciones."""
    def __init__(self, rut: str, nombre: str, id_empleado: str, clave_acceso: str):
        super().__init__(rut, nombre, id_empleado, clave_acceso)


class Administradora(Empleado):
    """Rol encargado de la gestión de materiales y condonación de multas."""
    def __init__(self, rut: str, nombre: str, id_empleado: str, clave_acceso: str):
        super().__init__(rut, nombre, id_empleado, clave_acceso)
```
