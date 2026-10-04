"""
=============================================================================
SISTEMA DE GESTIÓN - BIBLIOTECA MUNICIPAL CORDILLERA
Asignatura: Programación Orientada a Objetos Seguro
Autores: Nelson Bonomi y José Vergara
=============================================================================
Menú interactivo estructurado en 4 módulos principales con control de acceso
por roles (Bibliotecaria vs Administradora), cálculo de reposición con API Dólar,
y validaciones rigurosas de negocio.
"""
import sys
import os

# Agregamos la ruta base para asegurar importaciones relativas limpias
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dao.conexion import inicializar_base_datos
from dao.material_dao import MaterialDAO
from dao.socio_dao import SocioDAO
from dao.prestamo_dao import PrestamoDAO
from model.estados import EstadoMaterial, EstadoMulta
from model.excepciones import SocioConMultaException, MaterialNoDisponibleException
from model.persona import Persona
from model.socio import Socio
from model.libro import Libro
from model.revista import Revista
from model.multimedia import Multimedia
from model.prestamo import Prestamo
from model.roles import Administradora, Bibliotecaria
from model.empleado import Empleado
from services.api_dolar import obtener_valor_dolar


# Variable global para mantener la sesión del empleado activo en el mesón
EMPLEADO_ACTUAL: Empleado | None = None


# =============================================================================
# FUNCIONES AUXILIARES DE ENTRADA Y VALIDACIÓN
# =============================================================================

def leer_texto_no_vacio(mensaje: str) -> str:
    """Solicita un texto y no permite valores vacíos ni solo espacios."""
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("[!] Error: El campo no puede quedar en blanco. Intente nuevamente.")


def leer_entero_positivo(mensaje: str) -> int:
    """Solicita un número entero positivo."""
    while True:
        entrada = input(mensaje).strip()
        try:
            numero = int(entrada)
            if numero > 0:
                return numero
            print("[!] Error: Debe ingresar un número entero mayor a 0.")
        except ValueError:
            print(f"[!] Error: '{entrada}' no es un número entero válido. Ingrese solo dígitos.")


def leer_flotante_no_negativo(mensaje: str) -> float:
    """Solicita un número flotante mayor o igual a 0."""
    while True:
        entrada = input(mensaje).strip().replace(",", ".")
        try:
            numero = float(entrada)
            if numero >= 0:
                return numero
            print("[!] Error: El valor no puede ser negativo.")
        except ValueError:
            print(f"[!] Error: '{entrada}' no es un número válido. Ingrese un monto numérico.")


def leer_rut_validado(mensaje: str) -> str:
    """Solicita un RUT y valida el dígito verificador mediante Módulo 11."""
    while True:
        entrada = input(mensaje).strip()
        if Persona.validar_rut(entrada):
            return Persona.formatear_rut(entrada)
        print(f"[!] Error: El RUT '{entrada}' es INVÁLIDO (dígito verificador incorrecto o formato inválido).")
        print("    [Ejemplo: 12.345.678-5 o 12345678-5]")


def es_administradora() -> bool:
    """Verifica si el empleado con sesión activa es Administradora."""
    global EMPLEADO_ACTUAL
    return isinstance(EMPLEADO_ACTUAL, Administradora) or (
        EMPLEADO_ACTUAL and getattr(EMPLEADO_ACTUAL, 'rol', '') == "Administradora"
    )


def requerir_administradora(accion: str) -> bool:
    """Valida si el usuario actual tiene permisos de Administradora para una acción."""
    if not es_administradora():
        print("\n" + "!"*65)
        print(f"  [ACCESO DENEGADO]: La acción '{accion}'")
        print("  es exclusiva de la ADMINISTRADORA del sistema.")
        print(f"  Rol actual: {EMPLEADO_ACTUAL.__class__.__name__} ({EMPLEADO_ACTUAL.nombre})")
        print("!"*65)
        input("\nPresione Enter para continuar...")
        return False
    return True


# =============================================================================
# MÓDULO 3: GESTIÓN DE SESIÓN (LOGIN Y CAMBIO DE ROL)
# =============================================================================

def iniciar_sesion():
    """Permite seleccionar o autenticar el empleado que atiende en el mesón de forma obligatoria."""
    global EMPLEADO_ACTUAL

    while True:
        empleados = PrestamoDAO.listar_empleados()

        print("\n" + "="*60)
        print("      BIBLIOTECA MUNICIPAL CORDILLERA - INICIO DE SESIÓN")
        print("="*60)
        
        if empleados:
            print("Seleccione el empleado que atiende en mesón:")
            for idx, emp in enumerate(empleados, 1):
                rol_nombre = emp.__class__.__name__
                print(f"  {idx}. [{emp.id_empleado}] {emp.nombre:<20} | Rol: {rol_nombre:<14} | RUT: {emp.rut}")
            print("  3. Ingresar RUT de empleado manualmente")
            print("  0. Salir del programa")
            print("-" * 60)

            opc = input("Seleccione una opción: ").strip().upper()
            
            if opc.isdigit() and 1 <= int(opc) <= len(empleados):
                EMPLEADO_ACTUAL = empleados[int(opc) - 1]
                print(f"\n[OK] Sesión iniciada correctamente como: {EMPLEADO_ACTUAL.nombre} [{EMPLEADO_ACTUAL.__class__.__name__}]")
                return
            elif opc == "R":
                rut_in = leer_rut_validado("Ingrese RUT del empleado (ej. 11111111-1 o 22222222-2): ")
                emp = PrestamoDAO.obtener_empleado_por_rut(rut_in)
                if emp:
                    EMPLEADO_ACTUAL = emp
                    print(f"\n[OK] Sesión iniciada correctamente como: {EMPLEADO_ACTUAL.nombre} [{EMPLEADO_ACTUAL.__class__.__name__}]")
                    return
                else:
                    print("\n" + "!"*65)
                    print(f"  [ACCESO DENEGADO]: No existe ningún empleado registrado")
                    print(f"  con el RUT '{rut_in}'.")
                    print("!"*65)
            elif opc == "0":
                print("\n[!] Saliendo del sistema...")
                sys.exit(0)
            else:
                print(f"[!] Opción '{opc}' no válida. Seleccione un empleado de la lista o ingrese un RUT válido.")
        else:
            print("[!] Error crítico: No hay empleados registrados en la base de datos.")
            sys.exit(1)


def menu_sesion():
    """Muestra y permite cambiar la sesión activa de mesón."""
    global EMPLEADO_ACTUAL
    while True:
        rol_nombre = EMPLEADO_ACTUAL.__class__.__name__
        print("\n" + "="*60)
        print("  3. GESTIÓN DE SESIÓN DE MESÓN")
        print("="*60)
        print(f"  Usuario Activo:  {EMPLEADO_ACTUAL.nombre}")
        print(f"  ID Empleado:     {EMPLEADO_ACTUAL.id_empleado}")
        print(f"  RUT:             {EMPLEADO_ACTUAL.rut}")
        print(f"  Rol Actual:      {rol_nombre}")
        print("-" * 60)
        print("  1. Cambiar a Administradora (ADM01 - María Cordillera)")
        print("  2. Cambiar a Bibliotecaria (EMP01 - Ana González)")
        print("  3. Buscar empleado por RUT")
        print("  0. Volver al menú principal")
        print("="*60)

        opc = input("Seleccione una opción [0-3]: ").strip()

        if opc == "1":
            emp = PrestamoDAO.obtener_empleado_por_id("ADM01")
            if emp:
                EMPLEADO_ACTUAL = emp
                print(f"\n[OK] Sesión cambiada a: {EMPLEADO_ACTUAL.nombre} [Administradora]")
            else:
                print("[!] Error al cargar Administradora.")
        elif opc == "2":
            emp = PrestamoDAO.obtener_empleado_por_id("EMP01")
            if emp:
                EMPLEADO_ACTUAL = emp
                print(f"\n[OK] Sesión cambiada a: {EMPLEADO_ACTUAL.nombre} [Bibliotecaria]")
            else:
                print("[!] Error al cargar Bibliotecaria.")
        elif opc == "3":
            rut_in = leer_rut_validado("Ingrese RUT del empleado: ")
            emp = PrestamoDAO.obtener_empleado_por_rut(rut_in)
            if emp:
                EMPLEADO_ACTUAL = emp
                print(f"\n[OK] Sesión cambiada a: {EMPLEADO_ACTUAL.nombre} [{EMPLEADO_ACTUAL.__class__.__name__}]")
            else:
                print(f"[!] No existe empleado registrado con RUT '{rut_in}'.")
        elif opc == "0":
            break
        else:
            print("[!] Opción no válida.")


# =============================================================================
# MÓDULO 1: GESTIÓN DE CATÁLOGO (MATERIALES)
# =============================================================================

def menu_crear_material():
    """Registra nuevo material. Exclusivo de Administradora."""
    if not requerir_administradora("Dar de alta nuevo material en catálogo"):
        return

    print("\n" + "="*50)
    print("  [+] REGISTRAR NUEVO MATERIAL (Alta)")
    print("="*50)
    print("1. Libro")
    print("2. Revista")
    print("3. Multimedia (DVD / BluRay)")
    
    opc = input("Seleccione el tipo de material [1-3]: ").strip()
    codigo = leer_texto_no_vacio("Ingrese código único del material (ej. LIB03, REV02): ").upper()
    
    if MaterialDAO.obtener_por_codigo(codigo) is not None:
        print(f"[!] Error: Ya existe un material registrado con el código '{codigo}'.")
        return

    titulo = leer_texto_no_vacio("Ingrese título del material: ")

    if opc == "1":
        print("\n¿El libro es nacional o importado/extranjero?")
        print("1. Nacional (precio fijo en pesos CLP)")
        print("2. Extranjero (adquirido en dólares USD)")
        tipo_precio = input("Opción [1/2]: ").strip()
        
        if tipo_precio == "2":
            es_extranjero = True
            valor_usd = leer_flotante_no_negativo("Ingrese valor de reposición en Dólares (USD): ")
            valor_pesos = 0
        else:
            es_extranjero = False
            valor_usd = 0.0
            valor_pesos = int(leer_flotante_no_negativo("Ingrese valor de reposición en Pesos (CLP): "))
            
        nuevo_mat = Libro(codigo=codigo, titulo=titulo, es_extranjero=es_extranjero,
                          valor_reposicion_usd=valor_usd, valor_reposicion_pesos=valor_pesos)

    elif opc == "2":
        edicion = leer_entero_positivo("Ingrese número de edición: ")
        valor_usd = leer_flotante_no_negativo("Ingrese valor de reposición estimado (USD): ")
        nuevo_mat = Revista(codigo=codigo, titulo=titulo, numero_edicion=edicion, valor_reposicion_usd=valor_usd)

    elif opc == "3":
        formato = leer_texto_no_vacio("Ingrese formato audiovisual (ej. DVD, BluRay, CD): ").upper()
        valor_usd = leer_flotante_no_negativo("Ingrese valor de reposición estimado (USD): ")
        nuevo_mat = Multimedia(codigo=codigo, titulo=titulo, formato=formato, valor_reposicion_usd=valor_usd)

    else:
        print("[!] Opción no válida. Operación cancelada.")
        return

    MaterialDAO.crear(nuevo_mat)
    print(f"\n[OK] Material '{nuevo_mat.titulo}' (Código: {nuevo_mat.codigo}) dado de alta con éxito.")
    print(f"     Días de préstamo: {nuevo_mat.getDiasPrestamo()} | Renovaciones: {nuevo_mat.getMaxRenovaciones()}")


def menu_listar_materiales():
    """Muestra el catálogo completo de materiales registrados."""
    materiales = MaterialDAO.listar_todos()
    print("\n" + "="*85)
    print("  CATÁLOGO DE MATERIALES REGISTRADOS")
    print("="*85)
    if not materiales:
        print("No hay materiales registrados en la base de datos.")
        return

    print(f"{'CÓDIGO':<10} | {'TIPO':<12} | {'TÍTULO':<32} | {'ESTADO':<14} | {'PRÉSTAMO'}")
    print("-" * 85)
    for m in materiales:
        tipo = m.__class__.__name__
        prestamo_info = f"{m.getDiasPrestamo()} días / {m.getMaxRenovaciones()} ren."
        print(f"{m.codigo:<10} | {tipo:<12} | {m.titulo[:30]:<32} | {m.estado.value:<14} | {prestamo_info}")
    print("-" * 85)


def menu_modificar_material():
    """Modifica el título de un material. Exclusivo de Administradora."""
    if not requerir_administradora("Modificar material del catálogo"):
        return

    print("\n" + "="*50)
    print("  MODIFICAR MATERIAL")
    print("="*50)
    codigo = leer_texto_no_vacio("Ingrese el código del material a modificar: ").upper()
    mat = MaterialDAO.obtener_por_codigo(codigo)
    if not mat:
        print(f"[!] Error: No se encontró ningún material con el código '{codigo}'.")
        return

    print(f"Título actual: {mat.titulo}")
    nuevo_titulo = leer_texto_no_vacio("Ingrese el nuevo título: ")
    MaterialDAO.actualizar_titulo(codigo, nuevo_titulo)
    print(f"[OK] Título del material '{codigo}' actualizado a '{nuevo_titulo}'.")


def menu_eliminar_material():
    """Elimina un material del catálogo. Exclusivo de Administradora."""
    if not requerir_administradora("Eliminar material del catálogo"):
        return

    print("\n" + "="*50)
    print("  ELIMINAR MATERIAL DEL CATÁLOGO")
    print("="*50)
    codigo = leer_texto_no_vacio("Ingrese el código del material a eliminar: ").upper()
    mat = MaterialDAO.obtener_por_codigo(codigo)
    if not mat:
        print(f"[!] Error: No se encontró ningún material con el código '{codigo}'.")
        return

    confirmar = input(f"¿Está seguro de eliminar permanentemente '{mat.titulo}' ({mat.codigo})? [S/N]: ").strip().upper()
    if confirmar == "S":
        MaterialDAO.eliminar(codigo)
        print(f"[OK] Material '{codigo}' eliminado exitosamente del catálogo.")
    else:
        print("Operación cancelada.")


def menu_catalogo():
    """Submenú agrupado para la gestión de catálogo."""
    while True:
        print("\n" + "="*60)
        print("  1. GESTIÓN DE CATÁLOGO")
        print("="*60)
        print("  1. Listar catálogo de materiales")
        print("  2. Registrar nuevo material (Alta) [Solo Administradora]")
        print("  3. Modificar título de material [Solo Administradora]")
        print("  4. Eliminar material [Solo Administradora]")
        print("  0. Volver al menú principal")
        print("="*60)

        opc = input("Seleccione una opción [0-4]: ").strip()
        if opc == "1":
            menu_listar_materiales()
        elif opc == "2":
            menu_crear_material()
        elif opc == "3":
            menu_modificar_material()
        elif opc == "4":
            menu_eliminar_material()
        elif opc == "0":
            break
        else:
            print("[!] Opción no válida.")


# =============================================================================
# MÓDULO 2: GESTIÓN DE SOCIOS Y MULTAS (INCLUYE COBRO POR PÉRDIDA Y DÓLAR)
# =============================================================================

def menu_registrar_socio():
    """Registra un nuevo socio con validación Módulo 11."""
    print("\n" + "="*50)
    print("  REGISTRAR NUEVO SOCIO")
    print("="*50)
    rut = leer_rut_validado("Ingrese RUT del socio (con o sin puntos/guion): ")
    
    if SocioDAO.obtener_por_rut(rut) is not None:
        print(f"[!] Error: Ya existe un socio registrado con el RUT '{rut}'.")
        return

    nombre = leer_texto_no_vacio("Ingrese nombre completo del socio: ")
    direccion = leer_texto_no_vacio("Ingrese dirección de residencia: ")

    nuevo_socio = Socio(rut=rut, nombre=nombre, direccion=direccion)
    SocioDAO.crear(nuevo_socio)
    print(f"\n[OK] Socio '{nuevo_socio.nombre}' (RUT: {nuevo_socio.rut}) registrado exitosamente.")


def menu_listar_socios():
    """Lista todos los socios y su estado de multas."""
    socios = SocioDAO.listar_todos()
    print("\n" + "="*85)
    print("  LISTADO DE SOCIOS")
    print("="*85)
    if not socios:
        print("No hay socios registrados en el sistema.")
        return

    print(f"{'RUT':<14} | {'NOMBRE':<25} | {'ESTADO DEUDA':<16} | {'DIRECCIÓN'}")
    print("-" * 85)
    for s in socios:
        estado = "[CON MULTAS]" if s.tiene_multa_pendiente() else "[AL DÍA]"
        print(f"{s.rut:<14} | {s.nombre[:23]:<25} | {estado:<16} | {s.direccion}")
    print("-" * 85)


def menu_consultar_multas():
    """Permite listar todas las multas o detallar las multas de un socio por RUT."""
    print("\n" + "="*60)
    print("  CONSULTAR Y DETALLAR MULTAS")
    print("="*60)
    print("1. Ver todas las multas del sistema")
    print("2. Detallar multas de un socio específico por RUT")
    opc = input("Seleccione una opción [1/2]: ").strip()

    if opc == "1":
        multas = SocioDAO.listar_todas_las_multas()
        print("\n" + "="*85)
        print("  HISTORIAL GENERAL DE MULTAS")
        print("="*85)
        if not multas:
            print("No existen multas registradas en el sistema.")
            return

        print(f"{'ID':<6} | {'RUT SOCIO':<14} | {'NOMBRE SOCIO':<20} | {'MONTO (CLP)':<12} | {'ESTADO':<12} | {'MOTIVO'}")
        print("-" * 85)
        for m in multas:
            print(f"#{m['id']:<5} | {m['rut_socio']:<14} | {m['nombre_socio'][:18]:<20} | ${m['monto']:<11,.0f} | {m['estado']:<12} | {m['motivo']}")
        print("-" * 85)

    elif opc == "2":
        rut = leer_rut_validado("Ingrese RUT del socio a consultar: ")
        socio = SocioDAO.obtener_por_rut(rut)
        if not socio:
            print(f"[!] Error: No se encontró ningún socio con el RUT '{rut}'.")
            return

        print("\n" + "="*80)
        print(f"  HISTORIAL DE MULTAS - SOCIO: {socio.nombre} (RUT: {socio.rut})")
        print("="*80)
        if not socio.multas:
            print("El socio no tiene ningún registro de multas. Se encuentra AL DÍA.")
            return

        total_pendiente = 0.0
        print(f"{'ID':<6} | {'MONTO (CLP)':<14} | {'ESTADO':<14} | {'MOTIVO'}")
        print("-" * 80)
        for m in socio.multas:
            estado_str = m.estado.value if hasattr(m.estado, 'value') else str(m.estado)
            print(f"#{m.id_multa:<5} | ${m.monto:<13,.0f} | {estado_str:<14} | {m.motivo}")
            if estado_str == EstadoMulta.PENDIENTE.value:
                total_pendiente += m.monto
        print("-" * 80)
        if total_pendiente > 0:
            print(f"[*] DEUDA TOTAL PENDIENTE: ${total_pendiente:,.0f} CLP -> [BLOQUEADO PARA PRÉSTAMOS]")
        else:
            print("[*] ESTADO GENERAL: AL DÍA (Todas las multas se encuentran saldadas)")
        print("="*80)


def menu_cobrar_reposicion_libro_perdido():
    """
    Registra el cobro por un libro o material perdido:
    - Si es extranjero, calcula el valor según el dólar del día vía API en tiempo real.
    - Si es nacional, aplica el valor fijo en pesos.
    - Marca el material como EXTRAVIADO y genera la multa pendiente al socio.
    """
    print("\n" + "="*70)
    print("  COBRO DE VALOR DE REPOSICIÓN POR MATERIAL EXTRAVIADO/PERDIDO")
    print("="*70)

    rut = leer_rut_validado("Ingrese RUT del socio responsable de la pérdida: ")
    socio = SocioDAO.obtener_por_rut(rut)
    if not socio:
        print(f"[!] Error: Socio con RUT '{rut}' no encontrado.")
        return

    codigo = leer_texto_no_vacio("Ingrese código del material extraviado (ej. LIB02): ").upper()
    mat = MaterialDAO.obtener_por_codigo(codigo)
    if not mat:
        print(f"[!] Error: No se encontró material con código '{codigo}'.")
        return

    print(f"\nMaterial: {mat.titulo} ({mat.__class__.__name__})")
    print(f"Estado actual: {mat.estado.value}")

    # Cálculo del valor de reposición
    monto_clp = 0
    if isinstance(mat, Libro):
        if mat.es_extranjero:
            print("\n[*] El libro es extranjero (adquirido en USD).")
            print(f"    Valor base: ${mat.valor_reposicion_usd:,.2f} USD")
            print("[*] Consultando cotización del Dólar en vivo desde API (mindicador.cl)...")
            valor_dolar, origen = obtener_valor_dolar(timeout=5)
            monto_clp = mat.calcularValorReposicion(valor_dolar)
            print(f"    Cotización dólar ({origen}): ${valor_dolar:,.2f} CLP")
            print(f"    Valor total de reposición a cobrar: ${monto_clp:,.0f} CLP")
        else:
            monto_clp = mat.valor_reposicion_pesos
            print(f"\n[*] Libro nacional con valor de reposición fijo: ${monto_clp:,.0f} CLP")
    else:
        # Revista o Multimedia con valor en USD
        if mat.valor_reposicion_usd > 0:
            print(f"\n[*] Material importado con valor base de ${mat.valor_reposicion_usd:,.2f} USD.")
            print("[*] Consultando cotización del Dólar en vivo desde API...")
            valor_dolar, origen = obtener_valor_dolar(timeout=5)
            monto_clp = int(round(mat.valor_reposicion_usd * valor_dolar))
            print(f"    Cotización dólar: ${valor_dolar:,.2f} CLP | Total: ${monto_clp:,.0f} CLP")
        else:
            monto_clp = int(leer_flotante_no_negativo("Ingrese monto a cobrar en CLP por reposición: "))

    motivo = f"Reposición por pérdida de {mat.__class__.__name__} '{mat.titulo}' ({mat.codigo})"
    
    confirmar = input(f"\n¿Confirmar multa de ${monto_clp:,.0f} CLP a {socio.nombre}? [S/N]: ").strip().upper()
    if confirmar == "S":
        # 1. Registrar la multa
        multa = SocioDAO.registrar_multa(socio.rut, monto_clp, motivo)
        # 2. Actualizar estado del material a EXTRAVIADO
        MaterialDAO.actualizar_estado(mat.codigo, EstadoMaterial.EXTRAVIADO)
        print(f"\n[OK] Multa #{multa.id_multa} por ${monto_clp:,.0f} CLP aplicada con éxito a {socio.nombre}.")
        print(f"     Material '{mat.codigo}' marcado como EXTRAVIADO en la base de datos.")
        print("     El socio ha quedado bloqueado para solicitar préstamos hasta saldar la deuda.")
    else:
        print("Operación cancelada.")


def menu_pagar_o_condonar_multa():
    """Permite pagar multas (Bibliotecaria/Admin) o condonar multas (Solo Administradora)."""
    print("\n" + "="*60)
    print("  GESTIÓN DE PAGO Y CONDONACIÓN DE MULTAS")
    print("="*60)
    print("1. Pagar multa específica por ID (Bibliotecaria / Administradora)")
    print("2. Pagar TODAS las multas pendientes de un socio")
    print("3. Condonar multa [Solo Administradora]")
    opc = input("Seleccione una opción [1-3]: ").strip()

    if opc == "1":
        id_m = leer_entero_positivo("Ingrese el ID de la multa a pagar: ")
        if SocioDAO.cambiar_estado_multa(id_m, EstadoMulta.PAGADA):
            print(f"\n[OK] Multa #{id_m} marcada como PAGADA exitosamente.")
        else:
            print(f"[!] No se encontró la multa #{id_m}.")

    elif opc == "2":
        rut = leer_rut_validado("Ingrese RUT del socio a dejar al día: ")
        socio = SocioDAO.obtener_por_rut(rut)
        if not socio:
            print(f"[!] Error: Socio '{rut}' no encontrado.")
            return

        filas = SocioDAO.pagar_todas_las_multas_socio(socio.rut)
        if filas > 0:
            print(f"\n[OK] Se pagaron {filas} multa(s) pendientes de {socio.nombre}.")
            print("     El socio ahora se encuentra AL DÍA para solicitar préstamos.")
        else:
            print(f"El socio {socio.nombre} no registraba multas pendientes.")

    elif opc == "3":
        if not requerir_administradora("Condonar una multa"):
            return
        id_m = leer_entero_positivo("Ingrese el ID de la multa a condonar: ")
        if SocioDAO.cambiar_estado_multa(id_m, EstadoMulta.CONDONADA):
            print(f"\n[OK] Multa #{id_m} CONDONADA administrativamente por {EMPLEADO_ACTUAL.nombre}.")
        else:
            print(f"[!] No se encontró la multa #{id_m}.")


def menu_eliminar_socio():
    """Elimina un socio. Exclusivo de Administradora."""
    if not requerir_administradora("Eliminar socio"):
        return

    print("\n" + "="*50)
    print("  ELIMINAR SOCIO")
    print("="*50)
    rut = leer_rut_validado("Ingrese RUT del socio a eliminar: ")
    socio = SocioDAO.obtener_por_rut(rut)
    if not socio:
        print(f"[!] Error: No se encontró ningún socio con el RUT '{rut}'.")
        return

    confirmar = input(f"¿Está seguro de eliminar a '{socio.nombre}' (RUT: {socio.rut}) y sus registros? [S/N]: ").strip().upper()
    if confirmar == "S":
        SocioDAO.eliminar(socio.rut)
        print(f"[OK] Socio '{socio.nombre}' eliminado exitosamente.")
    else:
        print("Operación cancelada.")


def menu_socios():
    """Submenú agrupado para la gestión de socios y multas."""
    while True:
        print("\n" + "="*60)
        print("  2. GESTIÓN DE SOCIOS Y MULTAS")
        print("="*60)
        print("  1. Registrar nuevo socio (Validación RUT Módulo 11)")
        print("  2. Listar socios y estado general")
        print("  3. Consultar y detallar multas (Por socio o general)")
        print("  4. Cobrar reposición por libro/material perdido (API Dólar)")
        print("  5. Pagar o condonar multas")
        print("  6. Eliminar socio [Solo Administradora]")
        print("  0. Volver al menú principal")
        print("="*60)

        opc = input("Seleccione una opción [0-6]: ").strip()
        if opc == "1":
            menu_registrar_socio()
        elif opc == "2":
            menu_listar_socios()
        elif opc == "3":
            menu_consultar_multas()
        elif opc == "4":
            menu_cobrar_reposicion_libro_perdido()
        elif opc == "5":
            menu_pagar_o_condonar_multa()
        elif opc == "6":
            menu_eliminar_socio()
        elif opc == "0":
            break
        else:
            print("[!] Opción no válida.")


# =============================================================================
# MÓDULO 4: TRANSACCIONES (PRÉSTAMOS, DEVOLUCIONES Y CONSULTAS)
# =============================================================================

def menu_realizar_prestamo():
    """
    Registra una transacción de préstamo evaluando rigurosamente:
    1. Que el socio no tenga multas pendientes (SocioConMultaException).
    2. Que cada material esté DISPONIBLE (MaterialNoDisponibleException).
    """
    global EMPLEADO_ACTUAL
    print("\n" + "="*60)
    print("  REGISTRAR NUEVA TRANSACCIÓN DE PRÉSTAMO")
    print("="*60)

    # 1. Identificar al Socio
    rut_socio = leer_rut_validado("Ingrese RUT del socio solicitante: ")
    socio = SocioDAO.obtener_por_rut(rut_socio)
    if not socio:
        print(f"[!] Error: El socio con RUT '{rut_socio}' no existe en el sistema.")
        return

    # VALIDACIÓN INICIAL DE MULTAS
    if socio.tiene_multa_pendiente():
        print("\n" + "!"*70)
        print(f"  [REGLA DE NEGOCIO INFRINGIDA]: El socio {socio.nombre} (RUT: {socio.rut})")
        print("  registra MULTAS PENDIENTES. No está autorizado para solicitar préstamos.")
        print("  Debe saldar sus deudas antes de realizar una nueva solicitud.")
        print("!"*70)
        return

    # Instanciamos la transacción con el empleado activo en el mesón
    prestamo = Prestamo(socio=socio, empleado=EMPLEADO_ACTUAL)

    print(f"\nAtendiendo a: {socio.nombre} | Atendido por: {EMPLEADO_ACTUAL.nombre} [{EMPLEADO_ACTUAL.__class__.__name__}]")
    print("Ingrese los códigos de los materiales a prestar (ej. LIB01, REV01).")
    print("Escriba 'FIN' para procesar el préstamo.\n")

    while True:
        codigo = input("Ingrese código de material ('FIN' para terminar): ").strip().upper()
        if codigo == "FIN":
            break
        if not codigo:
            continue

        mat = MaterialDAO.obtener_por_codigo(codigo)
        if not mat:
            print(f"[!] No existe material con código '{codigo}'.")
            continue

        # Intentamos agregar el material evaluando las reglas del negocio
        try:
            prestamo.agregar_material(mat)
            print(f"   [+] Agregado: {mat.titulo} ({mat.__class__.__name__} - {mat.getDiasPrestamo()} días de préstamo)")

        except SocioConMultaException as error_multa:
            print(f"\n[BLOQUEO DE NEGOCIO]: {error_multa}")
            print("   Operación cancelada. El préstamo no se guardará.\n")
            return

        except MaterialNoDisponibleException as error_disponibilidad:
            print(f"\n[MATERIAL NO DISPONIBLE]: {error_disponibilidad}")
            print("   Este ejemplar no puede ser incluido en el préstamo.\n")

    if not prestamo.detalles:
        print("\n[!] No se seleccionó ningún material válido. Préstamo cancelado.")
        return

    # Guardamos atómicamente en SQLite
    try:
        id_prestamo = PrestamoDAO.guardar_prestamo(prestamo)
        print("\n" + "="*65)
        print(f"  [OK] PRÉSTAMO #{id_prestamo} REGISTRADO EXITOSAMENTE EN LA BASE DE DATOS")
        print("="*65)
        print(f"Socio:    {socio.nombre} ({socio.rut})")
        print(f"Atendido: {EMPLEADO_ACTUAL.nombre} [{EMPLEADO_ACTUAL.__class__.__name__}]")
        print(f"Fecha:    {prestamo.fecha_registro}")
        print("Líneas de Detalle registradas:")
        for det in prestamo.detalles:
            print(f"   - [{det.material.codigo}] {det.material.titulo} -> Vencimiento: {det.fecha_vencimiento}")
        print("="*65)

    except Exception as e:
        print(f"[!] Error al persistir el préstamo: {e}")


def menu_devolver_material():
    """Registra la devolución de un material, retornándolo al estado DISPONIBLE."""
    print("\n" + "="*60)
    print("  REGISTRAR DEVOLUCIÓN DE MATERIAL")
    print("="*60)
    codigo = leer_texto_no_vacio("Ingrese código del material a devolver: ").upper()
    mat = MaterialDAO.obtener_por_codigo(codigo)

    if not mat:
        print(f"[!] Error: No existe material con código '{codigo}'.")
        return

    if mat.estado == EstadoMaterial.DISPONIBLE:
        print(f"[!] El material '{mat.titulo}' ({mat.codigo}) ya se encuentra DISPONIBLE en estantería.")
        return

    PrestamoDAO.devolver_material(mat.codigo)
    print(f"\n[OK] Material '{mat.titulo}' ({mat.codigo}) devuelto exitosamente.")
    print("     Estado actualizado a: DISPONIBLE.")


def menu_consultar_prestamos():
    """Consulta los préstamos registrados en la base de datos junto a sus líneas de detalle."""
    prestamos = PrestamoDAO.listar_todos()
    print("\n" + "="*85)
    print("  CONSULTA DE HISTORIAL DE PRÉSTAMOS Y LÍNEAS DE DETALLE (SQLite)")
    print("="*85)
    if not prestamos:
        print("No hay préstamos registrados en la base de datos.")
        return

    for p in prestamos:
        print(f"\n[PRÉSTAMO #{p['id']}] Fecha: {p['fecha']} | Socio: {p['socio_nombre']} ({p['socio_rut']})")
        print(f"   Atendido por: {p['empleado_nombre']} (ID: {p['empleado_id']})")
        print("   Líneas de Detalle:")
        for d in p["detalles"]:
            print(f"     * [{d['codigo']}] {d['titulo']} ({d['tipo']}) | Vence: {d['fecha_vencimiento']} | Renovaciones: {d['renovaciones']}")
    print("\n" + "="*85)


def menu_transacciones():
    """Submenú agrupado para préstamos y devoluciones."""
    while True:
        print("\n" + "="*60)
        print("  4. GESTIÓN DE TRANSACCIONES")
        print("="*60)
        print("  1. Registrar Préstamo de material (1 o más ítems)")
        print("  2. Registrar Devolución de material")
        print("  3. Consultar Historial de Préstamos y Detalles")
        print("  0. Volver al menú principal")
        print("="*60)

        opc = input("Seleccione una opción [0-3]: ").strip()
        if opc == "1":
            menu_realizar_prestamo()
        elif opc == "2":
            menu_devolver_material()
        elif opc == "3":
            menu_consultar_prestamos()
        elif opc == "0":
            break
        else:
            print("[!] Opción no válida.")


# =============================================================================
# MENÚ PRINCIPAL AGRUPADO EN 4 OPCIONES
# =============================================================================

def menu_principal():
    """Bucle principal de la aplicación simplificado en 4 módulos."""
    inicializar_base_datos()
    iniciar_sesion()

    while True:
        rol_nombre = EMPLEADO_ACTUAL.__class__.__name__
        print("\n" + "="*60)
        print("      BIBLIOTECA MUNICIPAL CORDILLERA - SISTEMA")
        print(f"   Sesión: {EMPLEADO_ACTUAL.nombre} [Rol: {rol_nombre}]")
        print("="*60)
        print("  1. Catálogo de Materiales (Libros, Revistas, Videos)")
        print("  2. Socios y Multas (Registro, Historial, Pérdidas con API Dólar)")
        print("  3. Sesión de Mesón (Cambiar Bibliotecaria / Administradora)")
        print("  4. Transacciones (Préstamos, Devoluciones, Historial)")
        print("  0. Salir del programa")
        print("="*60)

        opcion = input("Seleccione una opción [0-4]: ").strip()

        try:
            if opcion == "1":
                menu_catalogo()
            elif opcion == "2":
                menu_socios()
            elif opcion == "3":
                menu_sesion()
            elif opcion == "4":
                menu_transacciones()
            elif opcion == "0":
                print("\n[!] Gracias por utilizar el Sistema de la Biblioteca Municipal Cordillera.")
                print("    Cerrando sesión de forma segura...\n")
                break
            else:
                print(f"\n[!] Opción '{opcion}' no válida. Seleccione un número entre 0 y 4.")
        except Exception as error_inesperado:
            print(f"\n[!] Error inesperado: {error_inesperado}")
            print("    El sistema se recuperó y continuará operando normalmente.\n")


if __name__ == "__main__":
    menu_principal()
