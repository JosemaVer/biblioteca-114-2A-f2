# Importamos la clase base Empleado
from empleado import Empleado
# Importamos la clase Socio
from socio import Socio
# Importamos la clase abstracta Material
from material import Material
# Importamos la clase DetallePrestamo
from detalle_prestamo import DetallePrestamo
# Importamos la clase Multa
from multa import Multa

# Definicion del rol Bibliotecaria con permisos para operar prestamos y devoluciones
class Bibliotecaria(Empleado):
    """Rol de Bibliotecaria con permisos para operar préstamos y devoluciones."""

    # Constructor que fija por defecto el cargo a Bibliotecaria
    def __init__(self, rut: str, nombre: str, apellido1: str, apellido2: str, email: str):
        # Invocamos el constructor de Empleado
        super().__init__(rut, nombre, apellido1, apellido2, email, cargo="Bibliotecaria")

    # Metodo para generar un nuevo prestamo validando solvencia del socio y disponibilidad de items
    def registrar_prestamo(self, socio: Socio, items: list[Material], id_prestamo: int) -> "Prestamo":
        # Importamos localmente Prestamo para evitar dependencias circulares
        from prestamo import Prestamo
        # Validamos si el socio registra multas impagas
        if socio.tiene_multa_pendiente():
            # Lanzamos excepcion si el socio tiene deuda
            raise ValueError(f"El socio {socio.nombre} {socio.apellido1} tiene multas pendientes de pago y no puede pedir préstamos.")

        # Validamos que se incluya al menos un item
        if not items:
            # Lanzamos excepcion si la lista esta vacia
            raise ValueError("Debe incluir al menos un material para generar el préstamo.")

        # Verificamos la disponibilidad individual de cada recurso solicitado
        for item in items:
            # Si algun item no esta disponible
            if not item.esta_disponible():
                # Lanzamos excepcion indicando cual es el item no disponible
                raise ValueError(f"El ítem '{item.titulo}' ({item.codigo}) no se encuentra disponible.")

        # Creamos la cabecera de prestamo
        nuevo_prestamo = Prestamo(id_prestamo=id_prestamo, socio=socio, empleado=self)
        # Anadimos cada material validado
        for item in items:
            nuevo_prestamo.agregar_detalle(item)

        # Retornamos el prestamo listo
        return nuevo_prestamo

    # Metodo para registrar la devolucion de un item y liquidar posibles multas por dias de atraso
    def registrar_devolucion(self, detalle: DetallePrestamo, valor_multa_dia: float = 1000.0) -> float:
        """Registra la devolución y devuelve el monto de multa generado si hubo retraso."""
        # Verificamos si ya habia sido devuelto
        if detalle.devuelto:
            # Lanzamos excepcion
            raise ValueError(f"El material '{detalle.material.titulo}' ya había sido devuelto.")

        # Calculamos si hubo dias de retraso
        dias_retraso = detalle.dias_de_retraso()
        # Marcamos la devolucion fisica
        detalle.registrar_devolucion()

        # Si hubo atraso calculamos el cobro
        if dias_retraso > 0:
            # Retornamos el total de multa calculado
            return dias_retraso * valor_multa_dia
        # Si no hubo atraso retornamos 0.0
        return 0.0

    # Representacion en texto
    def __str__(self) -> str:
        # Retornamos formato con rol
        return f"👩‍💼 [Bibliotecaria] {self.nombre} {self.apellido1} (RUT: {self.rut})"


# Definicion del rol Administradora con permisos de alta/baja de inventario y condonacion de multas
class Administradora(Empleado):
    """Rol de Administradora con permisos para dar de alta/baja material y condonar multas."""

    # Constructor que fija por defecto el cargo a Administradora
    def __init__(self, rut: str, nombre: str, apellido1: str, apellido2: str, email: str):
        # Invocamos el constructor de Empleado
        super().__init__(rut, nombre, apellido1, apellido2, email, cargo="Administradora")

    # Metodo para registrar e ingresar un nuevo material al catalogo general
    def dar_alta_material(self, inventario: list[Material], material: Material) -> None:
        # Validamos que no exista un material con el mismo codigo unico
        if any(m.codigo == material.codigo for m in inventario):
            # Lanzamos excepcion si el codigo ya existe
            raise ValueError(f"Ya existe un material registrado con el código '{material.codigo}'.")
        # Anadimos el nuevo material al inventario
        inventario.append(material)

    # Metodo para retirar o eliminar un material del catalogo
    def eliminar_material(self, inventario: list[Material], codigo: str) -> Material:
        # Buscamos el material por codigo en la lista
        material = next((m for m in inventario if m.codigo == codigo.upper()), None)
        # Validamos si se encontro
        if not material:
            # Lanzamos excepcion si no existe
            raise ValueError(f"No se encontró ningún material con el código '{codigo}'.")
        # Validamos que el material no este prestado
        if not material.esta_disponible():
            # Lanzamos excepcion
            raise ValueError(f"No se puede eliminar el material '{material.titulo}' porque no está en estado Disponible.")
        # Removemos el material de la coleccion
        inventario.remove(material)
        # Retornamos el material removido
        return material

    # Metodo para perdonar o anular una multa
    def condonar_multa(self, multa: Multa) -> None:
        # Invocamos el metodo condonar de la multa
        multa.condonar()

    # Representacion en texto
    def __str__(self) -> str:
        # Retornamos formato con rol de Administradora
        return f"👑 [Administradora] {self.nombre} {self.apellido1} (RUT: {self.rut})"
