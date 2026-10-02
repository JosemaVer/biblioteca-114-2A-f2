import unittest
from datetime import datetime, timedelta
from biblioteca import Biblioteca
from libro import Libro
from revista import Revista
from multimedia import Multimedia
from socio import Socio
from roles import Bibliotecaria, Administradora
from estados import EstadoMaterial, EstadoMulta

class TestSistemaBiblioteca(unittest.TestCase):

    def setUp(self):
        self.biblio = Biblioteca(nombre="Biblioteca Test", valor_multa_dia=1000.0, valor_dolar_dia=950.0)
        # Limpiar listas para pruebas aisladas
        self.biblio.materiales = []
        self.biblio.socios = {}
        self.biblio.empleados = {}
        self.biblio.prestamos = []
        self.biblio.multas = []

        self.admin = Administradora("11.111.111-1", "Admin", "Test", "Uno", "admin@test.cl")
        self.bibliotecaria = Bibliotecaria("12.345.678-5", "Biblio", "Test", "Dos", "biblio@test.cl")
        self.socio = Socio("22.222.222-2", "Socio", "Test", "Tres", "socio@test.cl", "Calle 123", 101)

        self.biblio.empleados[self.admin.rut] = self.admin
        self.biblio.empleados[self.bibliotecaria.rut] = self.bibliotecaria
        self.biblio.socios[self.socio.rut] = self.socio

        self.libro = Libro("LIB-001", "Python Avanzado", "Guido van Rossum", 2020, es_extranjero=True, valor_reposicion_dolares=50.0)
        self.revista = Revista("REV-001", "Ciencia Hoy", numero_edicion=10, anio=2023)
        self.biblio.materiales.extend([self.libro, self.revista])

    def test_validacion_rut_modulo11(self):
        self.assertTrue(self.socio.validar_rut("12.345.678-5"))
        self.assertTrue(self.socio.validar_rut("11111111-1"))
        self.assertFalse(self.socio.validar_rut("12.345.678-9"))

    def test_prestamo_y_disponibilidad(self):
        self.assertTrue(self.libro.esta_disponible())
        prestamo = self.biblio.realizar_prestamo(self.bibliotecaria.rut, self.socio.rut, ["LIB-001"])
        
        self.assertEqual(len(prestamo.detalles), 1)
        self.assertFalse(self.libro.esta_disponible())
        self.assertEqual(self.libro.estado, EstadoMaterial.PRESTADO)

        # Intentar prestar el mismo libro de nuevo debe fallar
        with self.assertRaises(ValueError):
            self.biblio.realizar_prestamo(self.bibliotecaria.rut, self.socio.rut, ["LIB-001"])

    def test_renovacion_limite(self):
        self.biblio.realizar_prestamo(self.bibliotecaria.rut, self.socio.rut, ["LIB-001"])
        
        # Libro permite 2 renovaciones
        msg1 = self.biblio.renovar_material("LIB-001")
        self.assertIn("exitosa", msg1.lower())
        msg2 = self.biblio.renovar_material("LIB-001")
        self.assertIn("exitosa", msg2.lower())
        
        # Tercera renovación debe lanzar error
        with self.assertRaises(ValueError):
            self.biblio.renovar_material("LIB-001")

    def test_bloqueo_prestamo_por_multa_pendiente(self):
        from multa import Multa
        multa = Multa(id_multa=99, rut_socio=self.socio.rut, monto=5000)
        self.socio.agregar_multa(multa)
        self.biblio.multas.append(multa)

        self.assertTrue(self.socio.tiene_multa_pendiente())
        with self.assertRaises(ValueError):
            self.biblio.realizar_prestamo(self.bibliotecaria.rut, self.socio.rut, ["REV-001"])

    def test_pago_y_condonacion_multa(self):
        from multa import Multa
        multa = Multa(id_multa=1, rut_socio=self.socio.rut, monto=3000)
        self.socio.agregar_multa(multa)
        self.biblio.multas.append(multa)

        # Condonar por Administradora
        self.biblio.condonar_multa(self.admin.rut, 1)
        self.assertEqual(multa.estado, EstadoMulta.CONDONADA)
        self.assertFalse(self.socio.tiene_multa_pendiente())

    def test_devolucion_exitosa(self):
        self.biblio.realizar_prestamo(self.bibliotecaria.rut, self.socio.rut, ["REV-001"])
        detalle, multa = self.biblio.registrar_devolucion("REV-001")
        self.assertTrue(detalle.devuelto)
        self.assertEqual(self.revista.estado, EstadoMaterial.DISPONIBLE)
        self.assertEqual(multa, 0.0)

if __name__ == "__main__":
    unittest.main()
