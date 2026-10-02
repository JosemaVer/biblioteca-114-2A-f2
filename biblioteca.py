# Importamos os para manipulacion de rutas de archivos en el sistema operativo
import os
# Importamos json para lectura y escritura de bases de datos locales en formato JSON
import json
# Importamos datetime para parseo y formateo de fechas
from datetime import datetime
# Importamos la clase abstracta Material
from material import Material
# Importamos la subclase Libro
from libro import Libro
# Importamos la subclase Revista
from revista import Revista
# Importamos la subclase Multimedia
from multimedia import Multimedia
# Importamos la clase Socio
from socio import Socio
# Importamos los roles especializados de Empleado
from roles import Bibliotecaria, Administradora
# Importamos la cabecera Prestamo
from prestamo import Prestamo
# Importamos la linea DetallePrestamo
from detalle_prestamo import DetallePrestamo
# Importamos la clase Multa
from multa import Multa
# Importamos las enumeraciones de estados
from estados import EstadoMaterial, EstadoMulta

# Definimos la ruta absoluta hacia el directorio 'data' dentro de la carpeta del proyecto
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Definicion de la clase controladora principal del sistema
class Biblioteca:
    """Clase controladora central que gestiona el inventario, usuarios, préstamos y persistencia."""

    # Constructor que inicializa los parametros globales de la biblioteca y colecciones
    def __init__(self, nombre: str = "Biblioteca Central", valor_multa_dia: float = 1000.0, valor_dolar_dia: float = 950.0):
        # Asignamos el nombre de la institucion
        self.nombre: str = nombre
        # Asignamos la tarifa de cobro por dia de atraso
        self.valor_multa_dia: float = valor_multa_dia
        # Asignamos la cotizacion del dolar para reposicion
        self.valor_dolar_dia: float = valor_dolar_dia

        # Inicializamos la lista de materiales catalogados
        self.materiales: list[Material] = []
        # Inicializamos el diccionario de socios indexado por RUT
        self.socios: dict[str, Socio] = {}
        # Inicializamos el diccionario de personal indexado por RUT
        self.empleados: dict[str, object] = {}
        # Inicializamos el registro historico de prestamos
        self.prestamos: list[Prestamo] = []
        # Inicializamos el registro historico de multas
        self.multas: list[Multa] = []

        # Invocamos la inicializacion de datos (carga de disco o datos semilla)
        self._inicializar_datos_base()

    # Metodo interno para cargar datos persistentes o sembrar datos iniciales
    def _inicializar_datos_base(self):
        """Carga datos desde disco o genera datos de prueba si no existen."""
        # Creamos el directorio data si aun no existe
        os.makedirs(DATA_DIR, exist_ok=True)
        # Intentamos cargar los datos desde los archivos JSON
        cargado = self.cargar_datos()
        # Si no existian archivos previos
        if not cargado:
            # Creamos los registros semilla por defecto
            self._crear_datos_semilla()
            # Guardamos inmediatamente en disco los nuevos archivos
            self.guardar_datos()

    # Metodo interno que genera datos de prueba validos
    def _crear_datos_semilla(self):
        """Crea datos iniciales para poder probar el sistema de inmediato."""
        # Bloque protegido contra errores
        try:
            # Creamos instancia de Administradora con RUT valido
            admin = Administradora("11.111.111-1", "Beatriz", "González", "Ríos", "admin@biblioteca.cl")
            # Creamos instancia de Bibliotecaria con RUT valido
            biblio = Bibliotecaria("12.345.678-5", "Ana", "Morales", "López", "ana.morales@biblioteca.cl")
            # Registramos a las empleadas en el diccionario
            self.empleados[admin.rut] = admin
            self.empleados[biblio.rut] = biblio

            # Creamos socios iniciales con RUTs validos
            s1 = Socio("22.222.222-2", "Carlos", "Soto", "Morales", "carlos.soto@email.com", direccion="Av. Libertador 1234", numero_socio=101)
            s2 = Socio("18.888.888-8", "Valeria", "Araya", "Pérez", "valeria.araya@email.com", direccion="Los Copihues 456", numero_socio=102)
            # Registramos los socios en el diccionario
            self.socios[s1.rut] = s1
            self.socios[s2.rut] = s2

            # Creamos materiales de prueba de distintos tipos
            l1 = Libro("LIB-001", "Cien Años de Soledad", "Gabriel García Márquez", 1967, es_extranjero=False, valor_reposicion_pesos=18000)
            l2 = Libro("LIB-002", "Clean Code", "Robert C. Martin", 2008, es_extranjero=True, valor_reposicion_dolares=45.0)
            r1 = Revista("REV-001", "National Geographic", numero_edicion=154, autor="Varios", anio=2024)
            m1 = Multimedia("MUL-001", "Inception Blu-Ray", formato="Blu-Ray", autor="Christopher Nolan", anio=2010)

            # Anadimos todos los materiales a la coleccion
            self.materiales.extend([l1, l2, r1, m1])
        # Captura de error si ocurre fallo al instanciar
        except Exception as e:
            # Imprimimos el error
            print(f"Error generando datos iniciales: {e}")

    # ==================== GESTIÓN DE MATERIALES ====================

    # Metodo para buscar un material por su codigo unico exacto
    def buscar_material(self, codigo: str) -> Material:
        # Limpiamos y normalizamos el codigo a mayusculas
        codigo_limpio = codigo.strip().upper()
        # Iteramos sobre el inventario
        for m in self.materiales:
            # Si el codigo coincide
            if m.codigo == codigo_limpio:
                # Retornamos el material
                return m
        # Si no se encuentra retornamos None
        return None

    # Metodo para buscar coincidencias parciales por titulo o autor
    def buscar_materiales_por_titulo(self, termino: str) -> list[Material]:
        # Normalizamos el termino a minusculas
        t = termino.strip().lower()
        # Retornamos la lista de materiales cuyo titulo o autor contengan el termino
        return [m for m in self.materiales if t in m.titulo.lower() or t in m.autor.lower()]

    # Metodo para dar de alta un material validando permisos de Administradora
    def agregar_material(self, admin_rut: str, material: Material) -> None:
        # Buscamos al empleado por su RUT
        admin = self.empleados.get(admin_rut)
        # Verificamos si existe y si posee el rol Administradora
        if not admin or not isinstance(admin, Administradora):
            # Lanzamos error de permisos si no es Administradora
            raise PermissionError("Solo un usuario con rol de Administradora puede dar de alta materiales.")
        # Invocamos el metodo dar_alta_material de la Administradora
        admin.dar_alta_material(self.materiales, material)
        # Guardamos los cambios inmediatamente en disco
        self.guardar_datos()

    # Metodo para dar de baja un material del inventario
    def eliminar_material(self, admin_rut: str, codigo: str) -> Material:
        # Buscamos a la Administradora
        admin = self.empleados.get(admin_rut)
        # Verificamos que sea Administradora
        if not admin or not isinstance(admin, Administradora):
            # Lanzamos error de permisos
            raise PermissionError("Solo un usuario con rol de Administradora puede dar de baja materiales.")
        # Ejecutamos la eliminacion
        mat = admin.eliminar_material(self.materiales, codigo)
        # Persistimos los cambios
        self.guardar_datos()
        # Retornamos el objeto eliminado
        return mat

    # ==================== GESTIÓN DE SOCIOS Y EMPLEADOS ====================

    # Metodo para registrar un nuevo socio en el sistema
    def registrar_socio(self, rut: str, nombre: str, apellido1: str, apellido2: str, email: str, direccion: str) -> Socio:
        # Validamos que el RUT no este previamente registrado
        if rut in self.socios:
            # Lanzamos excepcion por duplicado
            raise ValueError(f"Ya existe un socio registrado con el RUT {rut}.")
        # Calculamos correlativo para el numero de socio
        num_socio = len(self.socios) + 101
        # Creamos la instancia de Socio (valida RUT automaticamente)
        nuevo_socio = Socio(rut=rut, nombre=nombre, apellido1=apellido1, apellido2=apellido2, email=email, direccion=direccion, numero_socio=num_socio)
        # Guardamos en el diccionario de socios
        self.socios[nuevo_socio.rut] = nuevo_socio
        # Persistimos en JSON
        self.guardar_datos()
        # Retornamos el socio creado
        return nuevo_socio

    # Metodo para buscar un socio comparando RUTs limpios (sin puntos ni guion)
    def buscar_socio(self, rut: str) -> Socio:
        # Iteramos por los socios registrados
        for r, socio in self.socios.items():
            # Limpiamos ambos RUTs para comparacion robusta
            if r.replace(".", "").replace("-", "").upper() == rut.replace(".", "").replace("-", "").strip().upper():
                # Retornamos la coincidencia
                return socio
        # Si no se encuentra retornamos None
        return None

    # Metodo para buscar un empleado comparando RUTs limpios
    def buscar_empleado(self, rut: str):
        # Iteramos por los empleados
        for r, emp in self.empleados.items():
            # Limpiamos ambos RUTs
            if r.replace(".", "").replace("-", "").upper() == rut.replace(".", "").replace("-", "").strip().upper():
                # Retornamos el empleado
                return emp
        # Si no se encuentra retornamos None
        return None

    # ==================== GESTIÓN DE PRÉSTAMOS ====================

    # Metodo central para realizar un prestamo validando todas las reglas
    def realizar_prestamo(self, rut_empleada: str, rut_socio: str, codigos_materiales: list[str]) -> Prestamo:
        # Buscamos al personal que atiende
        empleada = self.buscar_empleado(rut_empleada)
        # Verificamos si existe
        if not empleada:
            # Lanzamos error
            raise ValueError("La empleada que atiende no está registrada.")
        # Verificamos si tiene permisos de atencion (Bibliotecaria o Administradora)
        if not isinstance(empleada, Bibliotecaria) and not isinstance(empleada, Administradora):
            # Lanzamos error de permisos
            raise PermissionError("El empleado no tiene permisos para realizar préstamos.")

        # Buscamos al socio solicitante
        socio = self.buscar_socio(rut_socio)
        # Verificamos si existe
        if not socio:
            # Lanzamos error si no esta registrado
            raise ValueError("El socio indicado no está registrado.")

        # Verificamos si el socio registra multas pendientes
        if socio.tiene_multa_pendiente():
            # Lanzamos excepcion con el monto de la deuda
            raise ValueError(f"El socio {socio.nombre} tiene multas pendientes (${socio.total_deuda_multas():,.0f}) y no puede solicitar préstamos.")

        # Inicializamos lista de items a prestar
        items: list[Material] = []
        # Iteramos por cada codigo solicitado
        for cod in codigos_materiales:
            # Buscamos el material en catalogo
            mat = self.buscar_material(cod)
            # Validamos si existe
            if not mat:
                # Lanzamos excepcion si el codigo no existe
                raise ValueError(f"El material con código '{cod}' no existe en el catálogo.")
            # Validamos si esta disponible para prestamo
            if not mat.esta_disponible():
                # Lanzamos excepcion si ya esta prestado o extraviado
                raise ValueError(f"El material '{mat.titulo}' ({mat.codigo}) ya está prestado o extraviado.")
            # Agregamos a la lista de items
            items.append(mat)

        # Generamos el nuevo ID de prestamo correlativo
        id_prestamo = len(self.prestamos) + 1
        # Creamos la cabecera del prestamo
        nuevo_prestamo = Prestamo(id_prestamo=id_prestamo, socio=socio, empleado=empleada)
        # Agregamos cada item
        for item in items:
            nuevo_prestamo.agregar_detalle(item)

        # Guardamos el prestamo en la lista general
        self.prestamos.append(nuevo_prestamo)
        # Guardamos los cambios en disco
        self.guardar_datos()
        # Retornamos el prestamo generado
        return nuevo_prestamo

    # Metodo para renovar un material prestado
    def renovar_material(self, codigo_material: str) -> str:
        # Buscamos en orden inverso para revisar los prestamos mas recientes
        for prestamo in reversed(self.prestamos):
            # Iteramos por los detalles del prestamo
            for detalle in prestamo.detalles:
                # Si coincide el codigo y el item aun no fue devuelto
                if detalle.material.codigo == codigo_material.upper() and not detalle.devuelto:
                    # Validamos que el socio no haya caido en mora por otras multas
                    if prestamo.socio.tiene_multa_pendiente():
                        # Lanzamos excepcion si el socio tiene multas
                        raise ValueError(f"El socio tiene multas pendientes y no puede renovar.")
                    # Ejecutamos la renovacion en el detalle
                    resultado = detalle.renovar()
                    # Persistimos los cambios
                    self.guardar_datos()
                    # Retornamos el mensaje
                    return resultado
        # Si no se encontro ningun prestamo activo con ese material lanzamos error
        raise ValueError(f"No se encontró un préstamo activo para el material '{codigo_material}'.")

    # Metodo para procesar la devolucion de un material
    def registrar_devolucion(self, codigo_material: str) -> tuple[DetallePrestamo, float]:
        # Buscamos en los prestamos mas recientes
        for prestamo in reversed(self.prestamos):
            # Iteramos sobre sus detalles
            for detalle in prestamo.detalles:
                # Si coincide el codigo y no ha sido devuelto
                if detalle.material.codigo == codigo_material.upper() and not detalle.devuelto:
                    # Calculamos los dias de atraso
                    dias_retraso = detalle.dias_de_retraso()
                    # Marcamos la devolucion
                    detalle.registrar_devolucion()
                    # Inicializamos monto de multa en 0
                    multa_monto = 0.0

                    # Si hubo retraso
                    if dias_retraso > 0:
                        # Calculamos el cobro de la multa
                        multa_monto = dias_retraso * self.valor_multa_dia
                        # Generamos ID correlativo de multa
                        id_multa = len(self.multas) + 1
                        # Creamos el objeto Multa
                        nueva_multa = Multa(
                            id_multa=id_multa,
                            rut_socio=prestamo.socio.rut,
                            monto=multa_monto,
                            motivo=f"Atraso de {dias_retraso} días en devolución de '{detalle.material.titulo}'"
                        )
                        # Anadimos la multa al registro global
                        self.multas.append(nueva_multa)
                        # Anadimos la multa a la cuenta del socio
                        prestamo.socio.agregar_multa(nueva_multa)

                    # Persistimos los datos
                    self.guardar_datos()
                    # Retornamos el detalle y el monto generado
                    return detalle, multa_monto

        # Si no se encontro el item pendiente lanzamos error
        raise ValueError(f"No se encontró un préstamo activo pendiente de devolución para el material '{codigo_material}'.")

    # Metodo para reportar un material extraviado o destruido
    def reportar_perdida(self, codigo_material: str) -> tuple[DetallePrestamo, float]:
        # Buscamos en prestamos recientes
        for prestamo in reversed(self.prestamos):
            # Iteramos detalles
            for detalle in prestamo.detalles:
                # Si coincide el codigo y sigue activo
                if detalle.material.codigo == codigo_material.upper() and not detalle.devuelto:
                    # Marcamos el material como EXTRAVIADO
                    detalle.marcar_perdido()
                    
                    # Costo base por defecto
                    monto_reposicion = 20000.0
                    # Si es un Libro, calculamos su valor exacto (considerando dolares si es extranjero)
                    if isinstance(detalle.material, Libro):
                        monto_reposicion = detalle.material.calcular_valor_reposicion(self.valor_dolar_dia)
                    
                    # Generamos ID de multa
                    id_multa = len(self.multas) + 1
                    # Creamos la multa por costo de reposicion
                    nueva_multa = Multa(
                        id_multa=id_multa,
                        rut_socio=prestamo.socio.rut,
                        monto=monto_reposicion,
                        motivo=f"Pérdida/Extravío del material '{detalle.material.titulo}'"
                    )
                    # Registramos la multa
                    self.multas.append(nueva_multa)
                    prestamo.socio.agregar_multa(nueva_multa)
                    # Guardamos en disco
                    self.guardar_datos()
                    # Retornamos el detalle y el costo
                    return detalle, monto_reposicion

        # Lanzamos error si no se encontro el prestamo
        raise ValueError(f"No se encontró ningún préstamo activo asociado al código '{codigo_material}'.")

    # ==================== GESTIÓN DE MULTAS ====================

    # Metodo para procesar el pago de una multa
    def pagar_multa(self, id_multa: int) -> Multa:
        # Buscamos la multa por su ID
        for m in self.multas:
            # Si coincide el ID
            if m.id_multa == id_multa:
                # Ejecutamos el pago
                m.pagar()
                # Persistimos en disco
                self.guardar_datos()
                # Retornamos la multa actualizada
                return m
        # Lanzamos error si no se encuentra
        raise ValueError(f"No se encontró ninguna multa con el ID #{id_multa}.")

    # Metodo para condonar una multa requiriendo autorizacion de Administradora
    def condonar_multa(self, admin_rut: str, id_multa: int) -> Multa:
        # Buscamos a la Administradora
        admin = self.empleados.get(admin_rut)
        # Verificamos que sea Administradora
        if not admin or not isinstance(admin, Administradora):
            # Lanzamos excepcion de permisos
            raise PermissionError("Solo un usuario con rol de Administradora puede condonar multas.")
        
        # Buscamos la multa
        for m in self.multas:
            # Si coincide el ID
            if m.id_multa == id_multa:
                # La Administradora condona la multa
                admin.condonar_multa(m)
                # Persistimos cambios
                self.guardar_datos()
                # Retornamos la multa condonada
                return m
        # Lanzamos error si no se encuentra
        raise ValueError(f"No se encontró ninguna multa con el ID #{id_multa}.")

    # ==================== PERSISTENCIA EN JSON ====================

    # Metodo para serializar y guardar todas las entidades en archivos JSON
    def guardar_datos(self) -> None:
        # Bloque seguro para evitar interrupciones
        try:
            # Guardamos la lista de Materiales
            with open(os.path.join(DATA_DIR, "materiales.json"), "w", encoding="utf-8") as f:
                json.dump([m.to_dict() for m in self.materiales], f, indent=4, ensure_ascii=False)

            # Guardamos el diccionario de Socios
            with open(os.path.join(DATA_DIR, "socios.json"), "w", encoding="utf-8") as f:
                json.dump([s.to_dict() for s in self.socios.values()], f, indent=4, ensure_ascii=False)

            # Guardamos la lista de Multas
            with open(os.path.join(DATA_DIR, "multas.json"), "w", encoding="utf-8") as f:
                json.dump([m.to_dict() for m in self.multas], f, indent=4, ensure_ascii=False)

            # Guardamos la lista de Prestamos
            with open(os.path.join(DATA_DIR, "prestamos.json"), "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in self.prestamos], f, indent=4, ensure_ascii=False)

        # Captura de error de escritura
        except Exception as e:
            # Informamos en consola
            print(f"Error al guardar datos: {e}")

    # Metodo para deserializar y reconstruir todos los objetos desde disco
    def cargar_datos(self) -> bool:
        # Definimos las rutas de los cuatro archivos
        mat_path = os.path.join(DATA_DIR, "materiales.json")
        soc_path = os.path.join(DATA_DIR, "socios.json")
        mul_path = os.path.join(DATA_DIR, "multas.json")
        pre_path = os.path.join(DATA_DIR, "prestamos.json")

        # Verificamos si existen los archivos minimos
        if not (os.path.exists(mat_path) and os.path.exists(soc_path)):
            # Retornamos False si faltan archivos base
            return False

        # Bloque de lectura protegida
        try:
            # Inicializamos las empleadas base
            admin = Administradora("11.111.111-1", "Beatriz", "González", "Ríos", "admin@biblioteca.cl")
            biblio = Bibliotecaria("12.345.678-5", "Ana", "Morales", "López", "ana.morales@biblioteca.cl")
            self.empleados[admin.rut] = admin
            self.empleados[biblio.rut] = biblio

            # Cargamos la coleccion de Materiales
            self.materiales = []
            with open(mat_path, "r", encoding="utf-8") as f:
                # Iteramos por cada diccionario guardado
                for item in json.load(f):
                    t = item.get("tipo")
                    # Reconstruimos segun el tipo correspondiente
                    if t == "Libro":
                        self.materiales.append(Libro.from_dict(item))
                    elif t == "Revista":
                        self.materiales.append(Revista.from_dict(item))
                    elif t == "Multimedia":
                        self.materiales.append(Multimedia.from_dict(item))

            # Cargamos la coleccion de Socios
            self.socios = {}
            with open(soc_path, "r", encoding="utf-8") as f:
                for item in json.load(f):
                    s = Socio.from_dict(item)
                    self.socios[s.rut] = s

            # Cargamos la coleccion de Multas y las asociamos a cada socio
            self.multas = []
            if os.path.exists(mul_path):
                with open(mul_path, "r", encoding="utf-8") as f:
                    for item in json.load(f):
                        m = Multa.from_dict(item)
                        self.multas.append(m)
                        # Si el socio existe, asociamos la multa a su objeto
                        if m.rut_socio in self.socios:
                            self.socios[m.rut_socio].agregar_multa(m)

            # Cargamos la coleccion de Prestamos
            self.prestamos = []
            if os.path.exists(pre_path):
                with open(pre_path, "r", encoding="utf-8") as f:
                    for item in json.load(f):
                        socio = self.socios.get(item["rut_socio"])
                        empleado = self.empleados.get(item["rut_empleado"]) or admin
                        if not socio:
                            continue
                        
                        detalles = []
                        # Reconstruimos cada linea de detalle del prestamo
                        for d_item in item["detalles"]:
                            mat = self.buscar_material(d_item["codigo_material"])
                            if not mat:
                                continue
                            f_ini = datetime.strptime(d_item["fecha_inicio"], "%Y-%m-%d %H:%M:%S")
                            f_ven = datetime.strptime(d_item["fecha_vencimiento"], "%Y-%m-%d %H:%M:%S")
                            f_dev = datetime.strptime(d_item["fecha_devolucion"], "%Y-%m-%d %H:%M:%S") if d_item.get("fecha_devolucion") else None
                            
                            det = DetallePrestamo(
                                material=mat,
                                fecha_inicio=f_ini,
                                fecha_vencimiento=f_ven,
                                renovaciones_usadas=d_item.get("renovaciones_usadas", 0),
                                devuelto=d_item.get("devuelto", False),
                                fecha_devolucion=f_dev
                            )
                            detalles.append(det)

                        f_reg = datetime.strptime(item["fecha_registro"], "%Y-%m-%d %H:%M:%S")
                        prestamo = Prestamo(id_prestamo=item["id_prestamo"], socio=socio, empleado=empleado, fecha_registro=f_reg, detalles=detalles)
                        self.prestamos.append(prestamo)

            # Retornamos True indicando exito en la carga
            return True
        # Captura de excepciones en lectura
        except Exception as e:
            # Informamos en consola
            print(f"Advertencia: no se pudieron cargar los datos previos ({e}). Se usarán datos por defecto.")
            # Retornamos False
            return False
