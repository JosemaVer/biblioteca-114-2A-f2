# Importamos sys para operaciones del sistema
import sys
# Importamos la clase controladora Biblioteca
from biblioteca import Biblioteca
# Importamos la subclase Libro
from libro import Libro
# Importamos la subclase Revista
from revista import Revista
# Importamos la subclase Multimedia
from multimedia import Multimedia
# Importamos la clase base Persona para validaciones estaticas de RUT
from persona import Persona
# Importamos las enumeraciones de estado
from estados import EstadoMaterial, EstadoMulta

# Funcion auxiliar para leer texto asegurando que no este vacio
def leer_texto_no_vacio(prompt: str) -> str:
    """Solicita una entrada al usuario y reintenta hasta que no esté vacía."""
    # Bucle infinito hasta obtener valor valido o interrupcion
    while True:
        # Bloque de captura de errores de entrada
        try:
            # Solicitamos la cadena y eliminamos espacios laterales
            valor = input(prompt).strip()
            # Si contiene caracteres
            if valor:
                # Retornamos el valor valido
                return valor
            # Si esta vacio avisamos al usuario
            print("⚠️  El campo no puede estar vacío. Intente nuevamente.")
        # Capturamos si el usuario presiona Ctrl+C o fin de flujo
        except (KeyboardInterrupt, EOFError):
            # Informamos cancelacion
            print("\nOperación cancelada por el usuario.")
            # Retornamos None para abortar
            return None

# Funcion auxiliar para leer un entero dentro de un rango determinado
def leer_entero(prompt: str, minimo: int = None, maximo: int = None) -> int:
    """Solicita un entero validando rango y evitando caídas por ValueError."""
    # Bucle de reintento
    while True:
        # Bloque try para atrapar no numericos
        try:
            # Leemos la entrada
            texto = input(prompt).strip()
            # Verificamos si no escribio nada
            if not texto:
                # Mensaje de advertencia
                print("⚠️  Debe ingresar un número.")
                # Continuamos en el bucle
                continue
            # Convertimos a entero (puede lanzar ValueError)
            num = int(texto)
            # Validamos cota inferior
            if minimo is not None and num < minimo:
                # Mensaje de rango
                print(f"⚠️  El número debe ser mayor o igual a {minimo}.")
                # Reintentamos
                continue
            # Validamos cota superior
            if maximo is not None and num > maximo:
                # Mensaje de rango
                print(f"⚠️  El número debe ser menor o igual a {maximo}.")
                # Reintentamos
                continue
            # Retornamos el numero validado
            return num
        # Si no es un entero valido
        except ValueError:
            # Mensaje explicativo
            print("⚠️  Entrada inválida. Ingrese un número entero válido.")
        # Captura de interrupcion
        except (KeyboardInterrupt, EOFError):
            # Mensaje
            print("\nOperación cancelada.")
            # Retornamos None
            return None

# Funcion auxiliar para leer decimales positivos
def leer_float(prompt: str, minimo: float = 0.0) -> float:
    """Solicita un número decimal validando que sea numérico y positivo."""
    # Bucle de reintento
    while True:
        # Bloque seguro
        try:
            # Leemos el texto
            texto = input(prompt).strip()
            # Convertimos a flotante
            num = float(texto)
            # Validamos minimo
            if num < minimo:
                # Mensaje de error
                print(f"⚠️  El valor debe ser mayor o igual a {minimo}.")
                # Continuamos
                continue
            # Retornamos el decimal
            return num
        # Si escribieron letras
        except ValueError:
            # Notificamos al usuario
            print("⚠️  Entrada inválida. Ingrese un valor numérico decimal válido.")
        # Captura de cancelacion
        except (KeyboardInterrupt, EOFError):
            # Notificamos
            print("\nOperación cancelada.")
            # Retornamos None
            return None

# Funcion auxiliar para leer y validar un RUT chileno
def leer_rut_valido(prompt: str) -> str:
    """Solicita un RUT y valida usando el algoritmo de Módulo 11 de Persona."""
    # Bucle de reintento
    while True:
        # Bloque try
        try:
            # Leemos la cadena
            rut = input(prompt).strip()
            # Validamos con el metodo estatico de Persona
            if Persona.validar_rut(rut):
                # Si es valido retornamos el RUT
                return rut
            # Si no es valido informamos el formato esperado
            print("❌ RUT inválido. Debe tener formato chileno con dígito verificador correcto (Ej: 12.345.678-5 o 12345678-5).")
        # Captura de cancelacion
        except (KeyboardInterrupt, EOFError):
            # Notificamos cancelacion
            print("\nOperación cancelada.")
            # Retornamos None
            return None

# Submenu para operaciones de materiales
def menu_materiales(biblioteca: Biblioteca):
    # Bucle del submenu
    while True:
        # Dibujamos encabezado
        print("\n" + "="*45)
        print("        📦 CATÁLOGO E INVENTARIO")
        print("="*45)
        print("1. Listar todos los materiales")
        print("2. Buscar material por código o título")
        print("3. Registrar nuevo material (Rol Admin)")
        print("4. Dar de baja material (Rol Admin)")
        print("0. Volver al menú principal")
        print("="*45)

        # Leemos opcion entre 0 y 4
        opc = leer_entero("Seleccione una opción: ", 0, 4)
        # Si es cancelar o 0, salimos al menu superior
        if opc is None or opc == 0:
            break

        # Opcion 1: Listar
        if opc == 1:
            print("\n--- Listado de Materiales en Biblioteca ---")
            # Si no hay inventario
            if not biblioteca.materiales:
                print("No hay materiales en el inventario.")
            # Si hay materiales
            else:
                # Iteramos e imprimimos cada uno
                for mat in biblioteca.materiales:
                    print(f"  {mat}")

        # Opcion 2: Buscar
        elif opc == 2:
            # Solicitamos termino de busqueda
            termino = leer_texto_no_vacio("Ingrese código o palabra clave del título/autor: ")
            # Si cancelo continuamos
            if not termino:
                continue
            # Buscamos por codigo exacto
            mat = biblioteca.buscar_material(termino)
            # Si se encontro por codigo
            if mat:
                print("\nMaterial encontrado por código exacto:")
                print(f"  {mat}")
            # Si no, buscamos por coincidencias de titulo o autor
            else:
                resultados = biblioteca.buscar_materiales_por_titulo(termino)
                # Si hubo coincidencias
                if resultados:
                    print(f"\nSe encontraron {len(resultados)} coincidencias:")
                    # Iteramos resultados
                    for m in resultados:
                        print(f"  {m}")
                # Si no hubo ninguna coincidencia
                else:
                    print(f"❌ No se encontraron materiales que coincidan con '{termino}'.")

        # Opcion 3: Alta de material
        elif opc == 3:
            print("\n--- Alta de Nuevo Material ---")
            # Solicitamos RUT de la Administradora
            admin_rut = leer_rut_valido("Ingrese RUT de Administradora autorizada (Ej: 11.111.111-1): ")
            # Si cancelo continuamos
            if not admin_rut:
                continue

            # Mostramos opciones de tipo
            print("\nSeleccione tipo de material:")
            print("  1. Libro")
            print("  2. Revista")
            print("  3. Multimedia (CD/DVD/Blu-ray)")
            # Leemos opcion 1 a 3
            tipo = leer_entero("Opción (1-3): ", 1, 3)

            # Leemos campos comunes
            codigo = leer_texto_no_vacio("Código único (Ej: LIB-100, REV-200): ")
            titulo = leer_texto_no_vacio("Título: ")
            autor = leer_texto_no_vacio("Autor / Creador: ")
            anio = leer_entero("Año de publicación: ", 1500, 2030)

            # Bloque try para capturar validaciones de dominio
            try:
                nuevo_material = None
                # Rama Libro
                if tipo == 1:
                    ext = leer_texto_no_vacio("¿Es libro extranjero? (s/n): ").lower() == "s"
                    if ext:
                        val_usd = leer_float("Valor de reposición en Dólares (USD): ", 1.0)
                        nuevo_material = Libro(codigo, titulo, autor, anio, es_extranjero=True, valor_reposicion_dolares=val_usd)
                    else:
                        val_clp = leer_float("Valor de reposición en Pesos ($CLP): ", 1000.0)
                        nuevo_material = Libro(codigo, titulo, autor, anio, es_extranjero=False, valor_reposicion_pesos=val_clp)
                # Rama Revista
                elif tipo == 2:
                    edicion = leer_entero("Número de edición: ", 1)
                    nuevo_material = Revista(codigo, titulo, numero_edicion=edicion, autor=autor, anio=anio)
                # Rama Multimedia
                elif tipo == 3:
                    formato = leer_texto_no_vacio("Formato (DVD, Blu-Ray, CD, Digital): ")
                    nuevo_material = Multimedia(codigo, titulo, formato=formato, autor=autor, anio=anio)

                # Invocamos el alta en la biblioteca
                biblioteca.agregar_material(admin_rut, nuevo_material)
                # Notificamos exito
                print(f"✅ ¡Material '{titulo}' registrado exitosamente!")
            # Captura de errores de negocio o permisos
            except (ValueError, PermissionError) as e:
                # Imprimimos mensaje de error
                print(f"❌ Error al dar de alta material: {e}")

        # Opcion 4: Baja de material
        elif opc == 4:
            print("\n--- Baja de Material ---")
            # Leemos RUT admin
            admin_rut = leer_rut_valido("Ingrese RUT de Administradora: ")
            # Si cancelo continuamos
            if not admin_rut:
                continue
            # Leemos codigo
            codigo = leer_texto_no_vacio("Ingrese código del material a eliminar: ")
            # Bloque seguro
            try:
                # Eliminamos material
                mat_eliminado = biblioteca.eliminar_material(admin_rut, codigo)
                # Notificamos
                print(f"✅ Se eliminó con éxito el material: {mat_eliminado.titulo}")
            # Capturamos fallos
            except (ValueError, PermissionError) as e:
                # Mostramos error
                print(f"❌ Error: {e}")

# Submenu para socios
def menu_socios(biblioteca: Biblioteca):
    # Bucle del menu
    while True:
        # Dibujamos opciones
        print("\n" + "="*45)
        print("          👥 GESTIÓN DE SOCIOS")
        print("="*45)
        print("1. Listar socios registrados")
        print("2. Buscar socio por RUT y ver estado de multas")
        print("3. Registrar nuevo socio")
        print("0. Volver al menú principal")
        print("="*45)

        # Leemos opcion
        opc = leer_entero("Seleccione una opción: ", 0, 3)
        # Salida
        if opc is None or opc == 0:
            break

        # Listado
        if opc == 1:
            print("\n--- Listado de Socios ---")
            if not biblioteca.socios:
                print("No hay socios registrados.")
            else:
                for socio in biblioteca.socios.values():
                    print(f"  {socio}")

        # Busqueda y estado de cuenta
        elif opc == 2:
            rut = leer_rut_valido("Ingrese RUT del socio: ")
            if not rut:
                continue
            socio = biblioteca.buscar_socio(rut)
            if not socio:
                print(f"❌ No se encontró ningún socio con el RUT {rut}.")
            else:
                print("\n" + "-"*40)
                print(f"👤 {socio}")
                print(f"Total Deuda Pendiente: ${socio.total_deuda_multas():,.0f}")
                if socio.multas:
                    print("Historial de Multas:")
                    for m in socio.multas:
                        print(f"   • {m}")
                else:
                    print("   (Sin multas en su historial)")
                print("-"*40)

        # Registro de socio
        elif opc == 3:
            print("\n--- Registro de Nuevo Socio ---")
            rut = leer_rut_valido("RUT (Ej: 12.345.678-5): ")
            if not rut:
                continue
            nombre = leer_texto_no_vacio("Nombre: ")
            apellido1 = leer_texto_no_vacio("Primer Apellido: ")
            apellido2 = leer_texto_no_vacio("Segundo Apellido: ")
            email = leer_texto_no_vacio("Correo Electrónico: ")
            direccion = leer_texto_no_vacio("Dirección: ")

            try:
                nuevo = biblioteca.registrar_socio(rut, nombre, apellido1, apellido2, email, direccion)
                print(f"✅ Socio #{nuevo.numero_socio} ({nuevo.nombre} {nuevo.apellido1}) registrado con éxito.")
            except ValueError as e:
                print(f"❌ Error al registrar socio: {e}")

# Submenu para prestamos
def menu_prestamos(biblioteca: Biblioteca):
    # Bucle
    while True:
        # Encabezado
        print("\n" + "="*45)
        print("        📖 PRÉSTAMOS Y DEVOLUCIONES")
        print("="*45)
        print("1. Realizar nuevo préstamo")
        print("2. Registrar devolución de material")
        print("3. Renovar préstamo de material")
        print("4. Reportar material extraviado / perdido")
        print("5. Ver préstamos activos e históricos")
        print("0. Volver al menú principal")
        print("="*45)

        # Leer opcion
        opc = leer_entero("Seleccione una opción: ", 0, 5)
        if opc is None or opc == 0:
            break

        # Nuevo prestamo
        if opc == 1:
            print("\n--- Solicitud de Préstamo ---")
            rut_empleada = leer_rut_valido("RUT de la Bibliotecaria que atiende (Ej: 12.345.678-5): ")
            if not rut_empleada:
                continue
            rut_socio = leer_rut_valido("RUT del Socio solicitante: ")
            if not rut_socio:
                continue

            codigos_str = leer_texto_no_vacio("Códigos de los materiales a prestar (separados por coma): ")
            if not codigos_str:
                continue
            codigos = [c.strip() for c in codigos_str.split(",") if c.strip()]

            try:
                prestamo = biblioteca.realizar_prestamo(rut_empleada, rut_socio, codigos)
                print(f"\n✅ ¡Préstamo registrado exitosamente!")
                print(prestamo)
            except (ValueError, PermissionError) as e:
                print(f"❌ No se pudo concretar el préstamo: {e}")

        # Devolucion
        elif opc == 2:
            print("\n--- Devolución de Material ---")
            codigo = leer_texto_no_vacio("Código del material a devolver: ")
            if not codigo:
                continue
            try:
                detalle, monto_multa = biblioteca.registrar_devolucion(codigo)
                print(f"✅ Devolución procesada para '{detalle.material.titulo}'.")
                if monto_multa > 0:
                    print(f"⚠️  Se generó una MULTA por atraso de: ${monto_multa:,.0f}")
                else:
                    print("👍 Devolución dentro del plazo. Sin multas.")
            except ValueError as e:
                print(f"❌ Error al devolver: {e}")

        # Renovacion
        elif opc == 3:
            print("\n--- Renovación de Préstamo ---")
            codigo = leer_texto_no_vacio("Código del material a renovar: ")
            if not codigo:
                continue
            try:
                msg = biblioteca.renovar_material(codigo)
                print(f"✅ {msg}")
            except ValueError as e:
                print(f"❌ Error al renovar: {e}")

        # Extravio
        elif opc == 4:
            print("\n--- Reporte de Material Extraviado ---")
            codigo = leer_texto_no_vacio("Código del material extraviado: ")
            if not codigo:
                continue
            try:
                detalle, costo = biblioteca.reportar_perdida(codigo)
                print(f"⚠️  Material '{detalle.material.titulo}' marcado como EXTRAVIADO.")
                print(f"💵 Se ha emitido una multa por costo de reposición de: ${costo:,.0f} al socio.")
            except ValueError as e:
                print(f"❌ Error: {e}")

        # Listar prestamos
        elif opc == 5:
            print("\n--- Registro de Préstamos ---")
            if not biblioteca.prestamos:
                print("No existen préstamos en el historial.")
            else:
                for p in biblioteca.prestamos:
                    print(p)

# Submenu para multas
def menu_multas(biblioteca: Biblioteca):
    # Bucle
    while True:
        # Encabezado
        print("\n" + "="*45)
        print("          💰 GESTIÓN DE MULTAS")
        print("="*45)
        print("1. Listar todas las multas")
        print("2. Pagar multa")
        print("3. Condonar multa (Rol Administradora)")
        print("0. Volver al menú principal")
        print("="*45)

        # Leer opcion
        opc = leer_entero("Seleccione una opción: ", 0, 3)
        if opc is None or opc == 0:
            break

        # Listar multas
        if opc == 1:
            print("\n--- Registro General de Multas ---")
            if not biblioteca.multas:
                print("No hay multas registradas en el sistema.")
            else:
                for m in biblioteca.multas:
                    print(f"  {m}")

        # Pagar multa
        elif opc == 2:
            id_m = leer_entero("Ingrese ID de la multa a pagar: ", 1)
            if id_m is None:
                continue
            try:
                multa = biblioteca.pagar_multa(id_m)
                print(f"✅ ¡Multa #{multa.id_multa} pagada con éxito! Estado: {multa.estado.value}")
            except ValueError as e:
                print(f"❌ Error al pagar multa: {e}")

        # Condonar multa
        elif opc == 3:
            admin_rut = leer_rut_valido("Ingrese RUT de la Administradora: ")
            if not admin_rut:
                continue
            id_m = leer_entero("Ingrese ID de la multa a condonar: ", 1)
            if id_m is None:
                continue
            try:
                multa = biblioteca.condonar_multa(admin_rut, id_m)
                print(f"✅ ¡Multa #{multa.id_multa} condonada con éxito! Estado: {multa.estado.value}")
            except (ValueError, PermissionError) as e:
                print(f"❌ Error al condonar multa: {e}")

# Funcion principal que inicia la aplicacion
def main():
    # Bloque de inicio controlado
    try:
        # Instanciamos la biblioteca con sus parametros de operacion
        biblioteca = Biblioteca(nombre="Biblioteca DUOC / Santo Tomás", valor_multa_dia=1000.0, valor_dolar_dia=950.0)
    # Captura de error critico
    except Exception as e:
        # Notificamos y terminamos
        print(f"Error crítico al inicializar la base de datos de biblioteca: {e}")
        return

    # Bucle principal de la interfaz
    while True:
        # Bloque seguro para el menu principal
        try:
            # Dibujamos el menu principal
            print("\n" + "╔" + "═"*48 + "╗")
            print(f"║   SISTEMA DE GESTIÓN: {biblioteca.nombre.center(23)} ║")
            print("╠" + "═"*48 + "╣")
            print("║  1. 📦 Gestión de Materiales e Inventario       ║")
            print("║  2. 👥 Gestión de Socios                        ║")
            print("║  3. 📖 Préstamos, Devoluciones y Renovaciones  ║")
            print("║  4. 💰 Gestión de Multas y Pagos                ║")
            print("║  0. 🚪 Guardar y Salir                          ║")
            print("╚" + "═"*48 + "╝")

            # Leemos la opcion seleccionada
            opc = leer_entero("Seleccione una opción: ", 0, 4)
            # Salida del sistema
            if opc is None or opc == 0:
                print("\nGuardando cambios y saliendo del sistema...")
                # Guardamos los datos antes de salir
                biblioteca.guardar_datos()
                print("¡Hasta pronto!\n")
                # Rompemos el bucle
                break

            # Navegamos a cada submenu segun la opcion
            if opc == 1:
                menu_materiales(biblioteca)
            elif opc == 2:
                menu_socios(biblioteca)
            elif opc == 3:
                menu_prestamos(biblioteca)
            elif opc == 4:
                menu_multas(biblioteca)

        # Capturamos Ctrl+C en cualquier momento para salir guardando datos
        except KeyboardInterrupt:
            print("\n\nSaliendo de forma segura...")
            biblioteca.guardar_datos()
            break
        # Capturamos cualquier error inesperado para que el programa no se caiga
        except Exception as e:
            print(f"\n⚠️  Ocurrió un error imprevisto: {e}. El sistema se recuperó con éxito.")

# Punto de entrada de ejecucion
if __name__ == "__main__":
    # Ejecutamos la funcion main
    main()
