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
import math
import re

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
from model.roles import Administradora
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


def leer_texto_no_vacio_o_cancelar(mensaje: str) -> str | None:
    """Solicita un texto no vacío o permite cancelar ingresando 0."""
    while True:
        valor = input(mensaje).strip()
        if valor == "0":
            return None
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


def rut_tiene_formato(rut: str) -> bool:
    """Valida la estructura del RUT sin comprobar su dígito verificador."""
    return re.fullmatch(
        r"(?:\d{7,8}|\d{1,2}(?:\.\d{3}){2})-[\dKk]",
        rut.strip(),
    ) is not None


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
    """Autentica a un empleado mediante su RUT y contraseña."""
    global EMPLEADO_ACTUAL

    while True:
        print("\n" + "="*60)
        print("      BIBLIOTECA MUNICIPAL CORDILLERA - INICIO DE SESIÓN")
        print("="*60)
        rut = input("RUT (0 para salir): ").strip().upper()
        if rut == "0":
            print("\n[!] Saliendo del sistema...")
            sys.exit(0)
        if not rut_tiene_formato(rut):
            print("[!] Formato de RUT inválido. Use, por ejemplo, 1111111-1.")
            continue

        empleado = PrestamoDAO.obtener_empleado_por_rut(rut)
        clave = input("Contraseña: ")
        if empleado and empleado.autenticar(clave):
            EMPLEADO_ACTUAL = empleado
            print(
                f"\n[OK] Sesión iniciada correctamente como: "
                f"{EMPLEADO_ACTUAL.nombre} [{EMPLEADO_ACTUAL.__class__.__name__}]"
            )
            return

        print("\n[!] RUT o contraseña incorrectos. Intente nuevamente.")


def menu_sesion():
    """Permite volver a autenticar o cambiar la contraseña de la sesión actual."""
    global EMPLEADO_ACTUAL
    while True:
        rol_nombre = EMPLEADO_ACTUAL.__class__.__name__
        print("\n" + "="*60)
        print("  3. GESTIÓN DE SESIÓN DE MESÓN")
        print("="*60)
        print(f"  Usuario Activo:  {EMPLEADO_ACTUAL.nombre}")
        print(f"  RUT:             {EMPLEADO_ACTUAL.rut}")
        print(f"  Rol Actual:      {rol_nombre}")
        print("-" * 60)
        print("  1. Cambiar de usuario (requiere contraseña)")
        print("  2. Cambiar mi contraseña")
        print("  0. Volver al menú principal")
        print("="*60)

        opc = input("Seleccione una opción [0-2]: ").strip()

        if opc == "1":
            iniciar_sesion()
        elif opc == "2":
            clave_actual = input("Contraseña actual: ")
            if not EMPLEADO_ACTUAL.autenticar(clave_actual):
                print("[!] La contraseña actual es incorrecta.")
                continue

            nueva_clave = input("Nueva contraseña (mínimo 8 caracteres): ")
            if len(nueva_clave) < 8:
                print("[!] La contraseña debe tener al menos 8 caracteres.")
                continue
            confirmacion = input("Repita la nueva contraseña: ")
            if nueva_clave != confirmacion:
                print("[!] Las contraseñas no coinciden.")
                continue

            if PrestamoDAO.actualizar_clave_acceso(
                EMPLEADO_ACTUAL.id_empleado,
                nueva_clave,
            ):
                EMPLEADO_ACTUAL.clave_acceso = nueva_clave
                print("[OK] Contraseña actualizada correctamente.")
            else:
                print("[!] No se pudo actualizar la contraseña del empleado.")
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
    danos = MaterialDAO.listar_ultimos_danos()
    print("\n" + "="*112)
    print("  CATÁLOGO DE MATERIALES REGISTRADOS")
    print("="*112)
    if not materiales:
        print("No hay materiales registrados en la base de datos.")
        return

    print(
        f"{'CÓDIGO':<10} | {'TIPO':<12} | {'TÍTULO':<30} | "
        f"{'REPOSICIÓN':>18} | {'ESTADO':<14} | {'PRÉSTAMO'}"
    )
    print("-" * 112)
    for m in materiales:
        tipo = m.__class__.__name__
        prestamo_info = f"{m.getDiasPrestamo()} días / {m.getMaxRenovaciones()} ren."
        if isinstance(m, Libro) and not m.es_extranjero:
            valor_reposicion = f"${m.valor_reposicion_pesos:,.0f} CLP"
        else:
            valor_reposicion = f"${m.valor_reposicion_usd:,.2f} USD"
        print(
            f"{m.codigo:<10} | {tipo:<12} | {m.titulo[:30]:<30} | "
            f"{valor_reposicion:>18} | {m.estado.value:<14} | {prestamo_info}"
        )
        if m.codigo in danos:
            dano = danos[m.codigo]
            print(
                f"   Último daño: {dano['categoria']} - {dano['descripcion']} "
                f"(registrado {dano['fecha']})"
            )
    print("-" * 112)


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


def menu_actualizar_precio_material():
    """Actualiza el valor de reposición de un material. Exclusivo de Administradora."""
    if not requerir_administradora("Actualizar el precio de un material"):
        return

    print("\n" + "="*50)
    print("  ACTUALIZAR PRECIO DE MATERIAL")
    print("="*50)
    codigo = leer_texto_no_vacio("Ingrese el código del material: ").upper()
    material = MaterialDAO.obtener_por_codigo(codigo)
    if not material:
        print(f"[!] Error: No se encontró ningún material con el código '{codigo}'.")
        return

    if isinstance(material, Libro):
        if material.es_extranjero:
            print(f"Valor actual: ${material.valor_reposicion_usd:,.2f} USD")
            valor = leer_flotante_no_negativo("Ingrese el nuevo valor en dólares (USD): ")
        else:
            print(f"Valor actual: ${material.valor_reposicion_pesos:,.0f} CLP")
            while True:
                valor = leer_flotante_no_negativo(
                    "Ingrese el nuevo valor en pesos (CLP, sin centavos): "
                )
                if valor.is_integer():
                    break
                print("[!] El precio en pesos debe ser un número entero.")
    else:
        print(f"Valor actual: ${material.valor_reposicion_usd:,.2f} USD")
        valor = leer_flotante_no_negativo("Ingrese el nuevo valor en dólares (USD): ")

    actualizado = MaterialDAO.actualizar_precio_reposicion(
        material.codigo,
        valor,
    )
    if actualizado:
        unidad = "USD" if not isinstance(material, Libro) or material.es_extranjero else "CLP"
        print(f"[OK] Precio de reposición de '{material.titulo}' actualizado a ${valor:,.2f} {unidad}.")
    else:
        print(f"[!] No se pudo actualizar el precio del material '{material.codigo}'.")


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
    opciones = [
        ("Listar catálogo de materiales", menu_listar_materiales),
    ]
    if es_administradora():
        opciones.extend([
            ("Registrar nuevo material", menu_crear_material),
            ("Modificar título de material", menu_modificar_material),
            ("Eliminar material", menu_eliminar_material),
            ("Actualizar precio de material", menu_actualizar_precio_material),
        ])

    while True:
        print("\n" + "="*60)
        print("  1. GESTIÓN DE CATÁLOGO")
        print("="*60)
        for numero, (descripcion, _) in enumerate(opciones, 1):
            print(f"  {numero}. {descripcion}")
        print("  0. Volver al menú principal")
        print("="*60)

        opc = input(f"Seleccione una opción [0-{len(opciones)}]: ").strip()
        if opc == "0":
            break
        if opc.isdigit() and 1 <= int(opc) <= len(opciones):
            opciones[int(opc) - 1][1]()
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

    while True:
        entrada = leer_texto_no_vacio_o_cancelar(
            "Ingrese RUT del socio (con o sin puntos/guion; 0 para volver): "
        )
        if entrada is None:
            print("Registro cancelado. Volviendo al menú de socios.")
            return
        if Persona.validar_rut(entrada):
            rut = Persona.formatear_rut(entrada)
            break
        print(f"[!] Error: El RUT '{entrada}' es INVÁLIDO (dígito verificador incorrecto o formato inválido).")
        print("    [Ejemplo: 12.345.678-5 o 12345678-5]")
    
    if SocioDAO.obtener_por_rut(rut) is not None:
        print(f"[!] Error: Ya existe un socio registrado con el RUT '{rut}'.")
        return

    nombre = leer_texto_no_vacio_o_cancelar(
        "Ingrese nombre completo del socio (0 para volver): "
    )
    if nombre is None:
        print("Registro cancelado. Volviendo al menú de socios.")
        return

    direccion = leer_texto_no_vacio_o_cancelar(
        "Ingrese dirección de residencia (0 para volver): "
    )
    if direccion is None:
        print("Registro cancelado. Volviendo al menú de socios.")
        return

    nuevo_socio = Socio(rut=rut, nombre=nombre, direccion=direccion)
    SocioDAO.crear(nuevo_socio)
    print(f"\n[OK] Socio '{nuevo_socio.nombre}' (RUT: {nuevo_socio.rut}) registrado exitosamente.")


def menu_registrar_multa():
    """Registra manualmente una multa pendiente a un socio existente."""
    print("\n" + "="*60)
    print("  ASIGNAR MULTA MANUAL A SOCIO")
    print("="*60)

    rut = leer_rut_validado("Ingrese RUT del socio: ")
    socio = SocioDAO.obtener_por_rut(rut)
    if not socio:
        print(f"[!] No existe un socio registrado con el RUT '{rut}'.")
        return

    monto = leer_entero_positivo("Ingrese monto de la multa en CLP: ")

    motivo = leer_texto_no_vacio("Ingrese el motivo de la multa: ")
    confirmar = input(
        f"¿Confirmar multa de ${monto:,.0f} CLP a {socio.nombre}? [S/N]: "
    ).strip().upper()
    if confirmar != "S":
        print("Operación cancelada.")
        return

    multa = SocioDAO.registrar_multa(socio.rut, monto, motivo)
    print(
        f"\n[OK] Multa #{multa.id_multa} por ${multa.monto:,.0f} CLP "
        f"registrada para {socio.nombre}."
    )


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
    Registra un daño parcial o pérdida total y calcula la multa sobre el valor de reposición.
    """
    print("\n" + "="*70)
    print("  REGISTRO DE DAÑO O PÉRDIDA DE MATERIAL")
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

    print("\nSeleccione el nivel del daño:")
    print("1. Leve - rayado o mancha superficial (25%)")
    print("2. Moderado - falta una hoja o tapa dañada (50%)")
    print("3. Grave - varias hojas faltantes o daño que dificulta el uso (75%)")
    print("4. Pérdida total - extraviado o inutilizable (100%)")
    categoria_opcion = input("Seleccione una opción [1-4]: ").strip()
    categorias = {
        "1": "Leve",
        "2": "Moderado",
        "3": "Grave",
        "4": "Pérdida total",
    }
    categoria = categorias.get(categoria_opcion)
    if categoria is None:
        print("[!] Opción no válida. Operación cancelada.")
        return

    descripcion = leer_texto_no_vacio(
        "Describa el daño (ej. falta una hoja, falta la tapa, está rayado): "
    )

    valor_reposicion_clp = 0.0
    if isinstance(mat, Libro):
        if mat.es_extranjero:
            print("\n[*] El libro es extranjero (adquirido en USD).")
            print(f"    Valor base: ${mat.valor_reposicion_usd:,.2f} USD")
            print("[*] Consultando cotización del Dólar en vivo desde API (mindicador.cl)...")
            valor_dolar, origen = obtener_valor_dolar(timeout=5)
            valor_reposicion_clp = mat.calcularValorReposicion(valor_dolar)
            print(f"    Cotización dólar ({origen}): ${valor_dolar:,.2f} CLP")
        else:
            valor_reposicion_clp = mat.valor_reposicion_pesos
            print(f"\n[*] Libro nacional con valor de reposición: ${valor_reposicion_clp:,.0f} CLP")
    else:
        if mat.valor_reposicion_usd > 0:
            print(f"\n[*] Material importado con valor base de ${mat.valor_reposicion_usd:,.2f} USD.")
            print("[*] Consultando cotización del Dólar en vivo desde API...")
            valor_dolar, origen = obtener_valor_dolar(timeout=5)
            valor_reposicion_clp = mat.valor_reposicion_usd * valor_dolar
            print(f"    Cotización dólar ({origen}): ${valor_dolar:,.2f} CLP")
        else:
            valor_reposicion_clp = leer_flotante_no_negativo(
                "El material no tiene valor de reposición cargado. "
                "Ingrese su valor de reposición en CLP: "
            )

    if not math.isfinite(valor_reposicion_clp) or valor_reposicion_clp <= 0:
        print("[!] El material no tiene un valor de reposición registrado.")
        valor_reposicion_clp = leer_entero_positivo(
            "Ingrese el valor de reposición en CLP para calcular la multa: "
        )

    porcentaje = PrestamoDAO.PORCENTAJES_DANO[categoria]
    monto_multa = int(round(valor_reposicion_clp * porcentaje / 100))
    print(f"    Categoría: {categoria} ({porcentaje}%)")
    print(f"    Valor de reposición: ${valor_reposicion_clp:,.0f} CLP")
    print(f"    Multa a aplicar: ${monto_multa:,.0f} CLP")

    confirmar = input(
        f"\n¿Confirmar multa de ${monto_multa:,.0f} CLP a {socio.nombre}? [S/N]: "
    ).strip().upper()
    if confirmar == "S":
        try:
            resultado = PrestamoDAO.registrar_dano(
                mat.codigo,
                socio.rut,
                categoria,
                descripcion,
                valor_reposicion_clp,
            )
        except ValueError as error:
            print(f"[!] No se pudo registrar el daño: {error}")
            return
        print(
            f"\n[OK] Multa #{resultado['id_multa']} por "
            f"${resultado['monto_multa']:,.0f} CLP aplicada a {socio.nombre}."
        )
        if categoria == "Pérdida total":
            print(f"     Material '{mat.codigo}' marcado como EXTRAVIADO.")
        else:
            print(f"     Material '{mat.codigo}' permanece disponible para préstamos.")
            print(f"     Daño registrado: {categoria} - {descripcion}.")
        if resultado["multa_atraso"]:
            print(
                f"     Multa adicional por atraso: "
                f"${resultado['multa_atraso']['monto']:,.0f} CLP."
            )
        print("     El socio ha quedado bloqueado para solicitar préstamos hasta saldar la deuda.")
    else:
        print("Operación cancelada.")


def menu_pagar_o_condonar_multa():
    """Permite pagar multas (Bibliotecaria/Admin) o condonar multas (Solo Administradora)."""
    opciones = [
        ("Pagar multa específica por ID", "1"),
        ("Pagar todas las multas pendientes de un socio", "2"),
    ]
    if es_administradora():
        opciones.append(("Condonar multa", "3"))

    print("\n" + "="*60)
    print("  GESTIÓN DE PAGO Y CONDONACIÓN DE MULTAS")
    print("="*60)
    for numero, (descripcion, _) in enumerate(opciones, 1):
        print(f"{numero}. {descripcion}")
    opc = input(f"Seleccione una opción [1-{len(opciones)}]: ").strip()
    if opc.isdigit() and 1 <= int(opc) <= len(opciones):
        opc = opciones[int(opc) - 1][1]

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
    opciones = [
        ("Registrar nuevo socio", menu_registrar_socio),
        ("Listar socios y estado general", menu_listar_socios),
        ("Consultar y detallar multas (Por socio o general)", menu_consultar_multas),
        ("Registrar daño o pérdida de material y aplicar multa", menu_cobrar_reposicion_libro_perdido),
        ("Pagar o condonar multas", menu_pagar_o_condonar_multa),
    ]
    if es_administradora():
        opciones.append(("Eliminar socio", menu_eliminar_socio))
    opciones.append(("Asignar multa manual a socio", menu_registrar_multa))

    while True:
        print("\n" + "="*60)
        print("  2. GESTIÓN DE SOCIOS Y MULTAS")
        print("="*60)
        for numero, (descripcion, _) in enumerate(opciones, 1):
            print(f"  {numero}. {descripcion}")
        print("  0. Volver al menú principal")
        print("="*60)

        opc = input(f"Seleccione una opción [0-{len(opciones)}]: ").strip()
        if opc == "0":
            break
        if opc.isdigit() and 1 <= int(opc) <= len(opciones):
            opciones[int(opc) - 1][1]()
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

    monto_multa = PrestamoDAO.devolver_material(mat.codigo)
    if monto_multa is None:
        print(f"[!] No se encontró un préstamo activo para el material '{mat.codigo}'.")
        return

    print(f"\n[OK] Material '{mat.titulo}' ({mat.codigo}) devuelto exitosamente.")
    print("     Estado actualizado a: DISPONIBLE.")
    if monto_multa > 0:
        print(f"     Se registró una multa automática por atraso de ${monto_multa:,.0f} CLP.")


def menu_consultar_prestamos():
    """Consulta el historial de préstamos de un socio identificado por su RUT."""
    print("\n" + "="*85)
    print("  CONSULTA DE HISTORIAL DE PRÉSTAMOS POR SOCIO")
    print("="*85)

    rut = leer_rut_validado("Ingrese el RUT del socio: ")
    socio = SocioDAO.obtener_por_rut(rut)
    if not socio:
        print(f"[!] No existe un socio registrado con el RUT '{rut}'.")
        return

    prestamos = [
        prestamo for prestamo in PrestamoDAO.listar_todos()
        if prestamo["socio_rut"] == socio.rut
    ]
    if not prestamos:
        print(f"No hay préstamos registrados para {socio.nombre} ({socio.rut}).")
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
    multas_atraso = PrestamoDAO.procesar_multas_atraso()
    if multas_atraso:
        total_multas = sum(multa["monto"] for multa in multas_atraso)
        print(
            f"[OK] Se actualizaron {len(multas_atraso)} multa(s) automática(s) "
            f"por atraso, por un total de ${total_multas:,.0f} CLP."
        )
    iniciar_sesion()

    while True:
        rol_nombre = EMPLEADO_ACTUAL.__class__.__name__
        print("\n" + "="*60)
        print("      BIBLIOTECA MUNICIPAL CORDILLERA - SISTEMA")
        print(f"   Sesión: {EMPLEADO_ACTUAL.nombre} [Rol: {rol_nombre}]")
        print("="*60)
        print("  1. Catálogo de Materiales (Libros, Revistas, Videos)")
        print("  2. Socios y Multas (Registro, Historial, Pérdidas con API Dólar)")
        print("  3. Mi sesión (Cambiar usuario o contraseña)")
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
