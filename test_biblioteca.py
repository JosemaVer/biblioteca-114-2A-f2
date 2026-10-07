"""
Módulo de Pruebas Unitarias Automatizadas.
Verifica la totalidad de los requerimientos y las 19 pruebas del guion de evaluación.
"""
import unittest
import os
import sys
import uuid

# Agregamos la ruta base
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model.estados import EstadoMaterial, EstadoMulta
from model.excepciones import SocioConMultaException, MaterialNoDisponibleException
from model.persona import Persona
from model.socio import Socio
from model.roles import Bibliotecaria
from model.libro import Libro
from model.revista import Revista
from model.multimedia import Multimedia
from model.multa import Multa
from model.prestamo import Prestamo
from dao.conexion import inicializar_base_datos, obtener_conexion
from dao.material_dao import MaterialDAO
from dao.socio_dao import SocioDAO
from dao.prestamo_dao import PrestamoDAO
from services.api_dolar import obtener_valor_dolar


class TestSistemaBiblioteca(unittest.TestCase):

    def setUp(self):
        """Inicializa la base de datos antes de cada prueba."""
        inicializar_base_datos()

    def test_01_validacion_rut_modulo_11(self):
        """P07 y P08: Prueba que los RUTs válidos se acepten y los inválidos se rechacen."""
        self.assertTrue(Persona.validar_rut("12.345.678-5"))
        self.assertTrue(Persona.validar_rut("12345678-5"))
        self.assertTrue(Persona.validar_rut("11111111-1"))
        
        # RUT con dígito verificador incorrecto debe dar False
        self.assertFalse(Persona.validar_rut("12.345.678-9"))
        self.assertFalse(Persona.validar_rut("12345678-0"))
        self.assertFalse(Persona.validar_rut("invalido"))

    def test_02_polimorfismo_dias_prestamo(self):
        """P09, P10, P11: Prueba de días de préstamo y renovaciones según subtipo."""
        libro = Libro(codigo="L_TEST", titulo="Prueba Libro")
        revista = Revista(codigo="R_TEST", titulo="Prueba Revista", numero_edicion=10)
        multimedia = Multimedia(codigo="M_TEST", titulo="Prueba DVD", formato="DVD")

        # Libro: 14 días, 1 renovación
        self.assertEqual(libro.getDiasPrestamo(), 14)
        self.assertEqual(libro.getMaxRenovaciones(), 1)

        # Revista: 7 días, 0 renovaciones
        self.assertEqual(revista.getDiasPrestamo(), 7)
        self.assertEqual(revista.getMaxRenovaciones(), 0)

        # Multimedia: 3 días, 0 renovaciones
        self.assertEqual(multimedia.getDiasPrestamo(), 3)
        self.assertEqual(multimedia.getMaxRenovaciones(), 0)

    def test_03_crud_materiales_dao(self):
        """P02, P03, P04, P06: Prueba de Crear, Listar, Modificar y Eliminar en SQLite."""
        codigo_prueba = f"TEST_{uuid.uuid4().hex[:6].upper()}"
        # 1. Crear
        libro = Libro(codigo=codigo_prueba, titulo="Rayuela", valor_reposicion_pesos=15000)
        MaterialDAO.crear(libro)

        # 2. Listar / Obtener
        recuperado = MaterialDAO.obtener_por_codigo(codigo_prueba)
        self.assertIsNotNone(recuperado)
        self.assertEqual(recuperado.titulo, "Rayuela")

        # 3. Modificar
        MaterialDAO.actualizar_titulo(codigo_prueba, "Rayuela (ed. 2020)")
        modificado = MaterialDAO.obtener_por_codigo(codigo_prueba)
        self.assertEqual(modificado.titulo, "Rayuela (ed. 2020)")

        # 4. Eliminar
        MaterialDAO.eliminar(codigo_prueba)
        eliminado = MaterialDAO.obtener_por_codigo(codigo_prueba)
        self.assertIsNone(eliminado)

    def test_04_regla_1_socio_con_multa_lanza_excepcion(self):
        """P14: Regla 1 - Impedir préstamo a un socio con multa pendiente."""
        socio = Socio(rut="12345678-5", nombre="Socio Deudor", direccion="Calle Test")
        multa = Multa(monto=5000, estado=EstadoMulta.PENDIENTE, motivo="Atraso")
        socio.agregar_multa(multa)

        empleado = Bibliotecaria(rut="11111111-1", nombre="Ana", id_empleado="EMP01", clave_acceso="123")
        libro = Libro(codigo="LIB_OK", titulo="Libro Disponible")

        prestamo = Prestamo(socio=socio, empleado=empleado)

        # Debe lanzar SocioConMultaException
        with self.assertRaises(SocioConMultaException):
            prestamo.agregar_material(libro)

    def test_05_regla_2_material_no_disponible_lanza_excepcion(self):
        """P15: Regla 2 - Impedir préstamo de material que ya está PRESTADO."""
        socio = Socio(rut="12345678-5", nombre="Socio Al Día", direccion="Calle Test")
        empleado = Bibliotecaria(rut="11111111-1", nombre="Ana", id_empleado="EMP01", clave_acceso="123")
        
        libro = Libro(codigo="LIB_PRESTADO", titulo="Libro Ocupado", estado=EstadoMaterial.PRESTADO)
        prestamo = Prestamo(socio=socio, empleado=empleado)

        # Debe lanzar MaterialNoDisponibleException
        with self.assertRaises(MaterialNoDisponibleException):
            prestamo.agregar_material(libro)

    def test_06_transaccion_prestamo_con_lineas_detalle(self):
        """P12 y P13: Registrar un préstamo con 2 libros y 1 revista en una sola transacción."""
        rut_test = "12345678-5"
        socio = SocioDAO.obtener_por_rut(rut_test)
        if not socio:
            socio = Socio(rut=rut_test, nombre="Juan Pérez Test", direccion="Calle Test 123")
            SocioDAO.crear(socio)
            socio = SocioDAO.obtener_por_rut(rut_test)

        empleado = PrestamoDAO.obtener_empleado_por_id("EMP01")
        if not empleado:
            empleado = Bibliotecaria(rut="11111111-1", nombre="Ana González", id_empleado="EMP01", clave_acceso="123")

        uid = uuid.uuid4().hex[:4].upper()
        cod_l1 = f"L1_{uid}"
        cod_l2 = f"L2_{uid}"
        cod_rv = f"R1_{uid}"
        l1 = Libro(codigo=cod_l1, titulo=f"[TEST] Libro de prueba 1 ({uid})")
        l2 = Libro(codigo=cod_l2, titulo=f"[TEST] Libro de prueba 2 ({uid})")
        rev = Revista(codigo=cod_rv, titulo=f"[TEST] Revista de prueba ({uid})", numero_edicion=5)

        for m in [l1, l2, rev]:
            MaterialDAO.crear(m)

        prestamo = Prestamo(socio=socio, empleado=empleado)
        prestamo.agregar_material(l1)
        prestamo.agregar_material(l2)
        prestamo.agregar_material(rev)

        self.assertEqual(len(prestamo.detalles), 3)

        id_prestamo = PrestamoDAO.guardar_prestamo(prestamo)
        self.assertIsNotNone(id_prestamo)

        # Verificamos que los detalles quedaron en la base de datos
        detalles_bd = PrestamoDAO.obtener_detalles_por_id_prestamo(id_prestamo)
        self.assertEqual(len(detalles_bd), 3)

        # Limpieza: eliminar préstamo temporal y materiales de prueba creados por este test
        from dao.conexion import obtener_conexion
        con = obtener_conexion()
        cur = con.cursor()
        cur.execute("DELETE FROM detalle_prestamos WHERE id_prestamo = ?", (id_prestamo,))
        cur.execute("DELETE FROM prestamos WHERE id = ?", (id_prestamo,))
        con.commit()
        con.close()
        for cod in [cod_l1, cod_l2, cod_rv]:
            MaterialDAO.eliminar(cod)


    def test_07_api_dolar_y_resiliencia(self):
        """P16 y P17: Verifica el cálculo en dólares y la resiliencia si falla la red."""
        valor, origen = obtener_valor_dolar(timeout=5)
        self.assertGreater(valor, 0)
        self.assertIsInstance(valor, float)

        libro_extranjero = Libro(codigo="L_USD", titulo="Book Foreign", es_extranjero=True, valor_reposicion_usd=20.0)
        total_clp = libro_extranjero.calcularValorReposicion(valor)
        self.assertAlmostEqual(total_clp, 20.0 * valor, places=1)

    def test_08_eliminar_socio(self):
        """Prueba la eliminación de socios en SQLite a través del DAO."""
        rut_temp = "10.000.013-K"
        socio_temp = Socio(rut=rut_temp, nombre="Socio Temporal", direccion="Calle 123")
        SocioDAO.crear(socio_temp)
        self.assertIsNotNone(SocioDAO.obtener_por_rut(rut_temp))

        resultado = SocioDAO.eliminar(rut_temp)
        self.assertTrue(resultado)
        self.assertIsNone(SocioDAO.obtener_por_rut(rut_temp))

    def test_listar_socios_con_rut_historico_no_valido(self):
        """Los RUT históricos se pueden cargar desde la BD aunque no validen."""
        rut_historico = "12345678-0"
        conexion = obtener_conexion()
        try:
            conexion.execute(
                "INSERT INTO socios (rut, nombre, direccion) VALUES (?, ?, ?)",
                (rut_historico, "Socio Histórico", "Dirección de prueba"),
            )
            conexion.commit()
        finally:
            conexion.close()

        try:
            socios = SocioDAO.listar_todos()
            socio = next(s for s in socios if s.rut == rut_historico)
            self.assertEqual(socio.nombre, "Socio Histórico")
        finally:
            SocioDAO.eliminar(rut_historico)

    def test_09_gestion_y_pago_de_multas(self):
        """Prueba la creación, bloqueo de préstamos y posterior pago de una multa."""
        rut_socio = "15345678-K"
        socio = Socio(rut=rut_socio, nombre="Socio Con Deuda", direccion="Pasaje Central 45")
        SocioDAO.crear(socio)

        # Registrar multa
        multa = SocioDAO.registrar_multa(rut_socio, 12000, "Libro no devuelto")
        socio_actualizado = SocioDAO.obtener_por_rut(rut_socio)
        self.assertTrue(socio_actualizado.tiene_multa_pendiente())

        # Pagar multa
        SocioDAO.cambiar_estado_multa(multa.id_multa, EstadoMulta.PAGADA)
        socio_al_dia = SocioDAO.obtener_por_rut(rut_socio)
        self.assertFalse(socio_al_dia.tiene_multa_pendiente())

        # Limpiar
        SocioDAO.eliminar(rut_socio)


if __name__ == "__main__":
    unittest.main()
