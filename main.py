from persona import Persona
from empleado import Empleado
from socio import Socio


def main():
    print("=== PRUEBAS DEL SISTEMA DE BIBLIOTECA ===")

    # 1. Creación de una Persona con RUT válido
    print("\n1. Creando instancia de Persona...")
    try:
        persona1 = Persona("12.345.678-5", "Juan", "Pérez", "González", "juan.perez@email.com")
        print(f"Éxito: {persona1}")
    except ValueError as e:
        print(f"Error al crear persona: {e}")

    # 2. Creación de un Empleado
    print("\n2. Creando instancia de Empleado...")
    try:
        empleado1 = Empleado("11.111.111-1", "María", "López", "Araya", "maria.lopez@biblioteca.cl", cargo="Jefa de Biblioteca")
        print(f"Éxito: {empleado1}")
    except ValueError as e:
        print(f"Error al crear empleado: {e}")

    # 3. Creación de un Socio y manejo de préstamos
    print("\n3. Creando instancia de Socio...")
    try:
        socio1 = Socio("22.222.222-2", "Carlos", "Soto", "Morales", "carlos.soto@email.com", numero_socio=101)
        print(f"Éxito: {socio1}")
        
        # Agregando préstamos al socio
        socio1.prestamos_activos.append("El Principito")
        socio1.prestamos_activos.append("Cien Años de Soledad")
        print(f"Préstamos activos de {socio1.nombre}: {socio1.prestamos_activos}")
    except ValueError as e:
        print(f"Error al crear socio: {e}")

    # 4. Prueba de validación con un RUT inválido
    print("\n4. Probando validación de RUT con un RUT inválido...")
    try:
        persona_invalida = Persona("12.345.678-0", "Falso", "RUT", "Prueba", "fake@email.com")
        print(persona_invalida)
    except ValueError as e:
        print(f"Captura de excepción esperada: {e}")

    print("\n=== PRUEBAS FINALIZADAS ===")


if __name__ == "__main__":
    main()
