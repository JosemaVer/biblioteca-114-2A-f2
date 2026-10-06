"""Pruebas para el acceso y la visibilidad de opciones según el rol."""
import contextlib
import io
import os
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import main
import dao.conexion as conexion_db
from dao.conexion import inicializar_base_datos, obtener_conexion
from dao.prestamo_dao import PrestamoDAO
from model.roles import Administradora, Bibliotecaria
from services.passwords import es_hash_clave, hashear_clave, verificar_clave


class TestAutenticacionYRoles(unittest.TestCase):

    def test_hash_de_contrasena(self):
        hash_clave = hashear_clave("clave de prueba")
        self.assertNotEqual(hash_clave, "clave de prueba")
        self.assertTrue(es_hash_clave(hash_clave))
        self.assertTrue(verificar_clave("clave de prueba", hash_clave))
        self.assertFalse(verificar_clave("clave incorrecta", hash_clave))

    def test_migracion_y_autenticacion_de_empleados_iniciales(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta_db = os.path.join(carpeta, "biblioteca.db")
            with (
                patch.object(conexion_db, "DB_FOLDER", carpeta),
                patch.object(conexion_db, "DB_PATH", ruta_db),
            ):
                inicializar_base_datos()
                conexion = obtener_conexion()
                empleados = conexion.execute(
                    """
                    SELECT id_empleado, rol, clave_acceso
                    FROM empleados
                    ORDER BY rowid
                    """
                ).fetchall()
                conexion.close()

                self.assertEqual(
                    [(fila[0], fila[1]) for fila in empleados],
                    [("ADM01", "Administradora"), ("EMP01", "Bibliotecaria")],
                )
                self.assertTrue(
                    all(es_hash_clave(fila[2]) for fila in empleados)
                )
                administradora = PrestamoDAO.obtener_empleado_por_id("ADM01")
                bibliotecaria = PrestamoDAO.obtener_empleado_por_id("EMP01")
                self.assertIsInstance(administradora, Administradora)
                self.assertIsInstance(bibliotecaria, Bibliotecaria)
                self.assertTrue(administradora.autenticar("admin123"))
                self.assertTrue(bibliotecaria.autenticar("root123"))

    def test_migra_roles_de_cuentas_de_demostracion_existentes(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta_db = os.path.join(carpeta, "biblioteca.db")
            with (
                patch.object(conexion_db, "DB_FOLDER", carpeta),
                patch.object(conexion_db, "DB_PATH", ruta_db),
            ):
                inicializar_base_datos()
                conexion = obtener_conexion()
                conexion.execute("DELETE FROM empleados")
                conexion.executemany(
                    """
                    INSERT INTO empleados
                    (id_empleado, rut, nombre, clave_acceso, rol)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            "EMP01",
                            "11111111-1",
                            "Ana González",
                            hashear_clave("admin123"),
                            "Bibliotecaria",
                        ),
                        (
                            "ADM01",
                            "22222222-2",
                            "María Cordillera",
                            hashear_clave("root123"),
                            "Administradora",
                        ),
                    ],
                )
                conexion.commit()
                conexion.close()

                inicializar_base_datos()
                administradora = PrestamoDAO.obtener_empleado_por_rut("11111111-1")
                empleados = PrestamoDAO.listar_empleados()

        self.assertIsInstance(administradora, Administradora)
        self.assertTrue(administradora.autenticar("admin123"))
        self.assertEqual(empleados[0].nombre, "Ana González")
        self.assertIsInstance(empleados[0], Administradora)

    def test_migra_clave_legacy_y_guarda_cambios_con_hash(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta_db = os.path.join(carpeta, "biblioteca.db")
            conexion = sqlite3.connect(ruta_db)
            conexion.execute("""
                CREATE TABLE empleados (
                    id_empleado TEXT PRIMARY KEY,
                    rut TEXT NOT NULL,
                    nombre TEXT NOT NULL,
                    clave_acceso TEXT NOT NULL,
                    rol TEXT NOT NULL
                )
            """)
            conexion.execute(
                "INSERT INTO empleados VALUES (?, ?, ?, ?, ?)",
                ("TEST01", "11111111-1", "Usuario de prueba", "legacy-secret", "Bibliotecaria"),
            )
            conexion.commit()
            conexion.close()

            with (
                patch.object(conexion_db, "DB_FOLDER", carpeta),
                patch.object(conexion_db, "DB_PATH", ruta_db),
            ):
                inicializar_base_datos()
                conexion = obtener_conexion()
                clave_guardada = conexion.execute(
                    "SELECT clave_acceso FROM empleados WHERE id_empleado = ?",
                    ("TEST01",),
                ).fetchone()[0]
                conexion.close()
                self.assertTrue(es_hash_clave(clave_guardada))
                empleado = PrestamoDAO.obtener_empleado_por_id("TEST01")
                self.assertTrue(empleado.autenticar("legacy-secret"))
                self.assertTrue(
                    PrestamoDAO.actualizar_clave_acceso(
                        "TEST01",
                        "new-secure-password",
                    )
                )
                empleado_actualizado = PrestamoDAO.obtener_empleado_por_id("TEST01")
                self.assertTrue(empleado_actualizado.autenticar("new-secure-password"))
                self.assertFalse(empleado_actualizado.autenticar("legacy-secret"))

    def test_login_por_rut_sin_validacion_modulo_11(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta_db = os.path.join(carpeta, "biblioteca.db")
            with (
                patch.object(conexion_db, "DB_FOLDER", carpeta),
                patch.object(conexion_db, "DB_PATH", ruta_db),
            ):
                inicializar_base_datos()
                conexion = obtener_conexion()
                conexion.execute(
                    """
                    INSERT INTO empleados
                    (id_empleado, rut, nombre, clave_acceso, rol)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        "TEST01",
                        "1111111-1",
                        "Usuario con RUT de prueba",
                        hashear_clave("clave-prueba"),
                        "Bibliotecaria",
                    ),
                )
                conexion.commit()
                conexion.close()

                empleado = PrestamoDAO.obtener_empleado_por_rut("1111111-1")
                self.assertIsNotNone(empleado)
                self.assertTrue(empleado.autenticar("clave-prueba"))

                salida = io.StringIO()
                with (
                    patch.object(main, "EMPLEADO_ACTUAL", None),
                    patch(
                        "builtins.input",
                        side_effect=["1111111-1", "clave-prueba"],
                    ),
                    contextlib.redirect_stdout(salida),
                ):
                    main.iniciar_sesion()
                    self.assertEqual(main.EMPLEADO_ACTUAL.rut, "1111111-1")

                self.assertIn("Sesión iniciada correctamente", salida.getvalue())

    def test_login_rechaza_rut_sin_formato_antes_de_pedir_clave(self):
        salida = io.StringIO()
        with (
            patch.object(main, "EMPLEADO_ACTUAL", None),
            patch("builtins.input", side_effect=["11111-1", "0"]),
            patch("sys.exit", side_effect=SystemExit),
            contextlib.redirect_stdout(salida),
        ):
            with self.assertRaises(SystemExit):
                main.iniciar_sesion()

        self.assertIn("Formato de RUT inválido", salida.getvalue())

    def test_formato_rut_acepta_ejemplo_sin_validar_digito(self):
        self.assertTrue(main.rut_tiene_formato("1111111-1"))
        self.assertTrue(main.rut_tiene_formato("11.111.111-1"))
        self.assertFalse(main.rut_tiene_formato("11111-1"))
        self.assertFalse(main.rut_tiene_formato("11111111"))

    def test_menu_catalogo_filtra_acciones_por_rol(self):
        casos = (
            (Bibliotecaria, False),
            (Administradora, True),
        )
        for tipo_empleado, es_admin in casos:
            empleado = tipo_empleado(
                rut="11111111-1",
                nombre="Personal de prueba",
                id_empleado="TEST01",
                clave_acceso="clave de prueba",
            )
            salida = io.StringIO()
            with (
                patch.object(main, "EMPLEADO_ACTUAL", empleado),
                patch("builtins.input", return_value="0"),
                contextlib.redirect_stdout(salida),
            ):
                main.menu_catalogo()

            self.assertEqual(
                "Registrar nuevo material" in salida.getvalue(),
                es_admin,
            )
            self.assertEqual(
                "Listar catálogo de materiales" in salida.getvalue(),
                True,
            )

    def test_menu_socios_oculta_eliminacion_a_bibliotecaria(self):
        for tipo_empleado, puede_eliminar in (
            (Bibliotecaria, False),
            (Administradora, True),
        ):
            empleado = tipo_empleado(
                rut="11111111-1",
                nombre="Personal de prueba",
                id_empleado="TEST01",
                clave_acceso="clave de prueba",
            )
            salida = io.StringIO()
            with (
                patch.object(main, "EMPLEADO_ACTUAL", empleado),
                patch("builtins.input", return_value="0"),
                contextlib.redirect_stdout(salida),
            ):
                main.menu_socios()

            self.assertEqual(
                "Eliminar socio" in salida.getvalue(),
                puede_eliminar,
            )

    def test_menu_multas_filtra_condonacion(self):
        for tipo_empleado, puede_condonar in (
            (Bibliotecaria, False),
            (Administradora, True),
        ):
            empleado = tipo_empleado(
                rut="11111111-1",
                nombre="Personal de prueba",
                id_empleado="TEST01",
                clave_acceso="clave de prueba",
            )
            salida = io.StringIO()
            with (
                patch.object(main, "EMPLEADO_ACTUAL", empleado),
                patch.object(
                    main.SocioDAO,
                    "cambiar_estado_multa",
                    return_value=False,
                ),
                patch("builtins.input", return_value="1"),
                contextlib.redirect_stdout(salida),
            ):
                main.menu_pagar_o_condonar_multa()

            self.assertEqual(
                "Condonar multa" in salida.getvalue(),
                puede_condonar,
            )


if __name__ == "__main__":
    unittest.main()
