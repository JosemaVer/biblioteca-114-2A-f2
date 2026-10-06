"""
Módulo de Conexión y Gestión de Esquema SQLite.
Garantiza la creación de carpetas, base de datos y tablas al iniciar el sistema.
"""
import os
import sqlite3
from services.passwords import es_hash_clave, hashear_clave


DB_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_FOLDER, "biblioteca.db")


def obtener_conexion() -> sqlite3.Connection:
    """
    Retorna una conexión activa a la base de datos SQLite.
    Crea el directorio 'data/' si no existe.
    """
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER, exist_ok=True)

    conexion = sqlite3.connect(DB_PATH)
    # Habilitamos soporte para claves foráneas
    conexion.execute("PRAGMA foreign_keys = ON;")
    return conexion


def inicializar_base_datos():
    """
    Crea las tablas necesarias en la base de datos SQLite si aún no existen.
    Inserta datos iniciales de prueba si la base de datos es nueva.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # 1. Tabla Materiales (Almacena Libros, Revistas y Multimedia)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materiales (
            codigo TEXT PRIMARY KEY,
            tipo TEXT NOT NULL,
            titulo TEXT NOT NULL,
            estado TEXT NOT NULL,
            valor_reposicion_usd REAL DEFAULT 0.0,
            valor_reposicion_pesos INTEGER DEFAULT 0,
            es_extranjero INTEGER DEFAULT 0,
            numero_edicion INTEGER DEFAULT 1,
            formato TEXT DEFAULT 'DVD'
        );
    """)

    # 2. Tabla Socios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS socios (
            rut TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            direccion TEXT NOT NULL
        );
    """)

    # 3. Tabla Empleados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS empleados (
            id_empleado TEXT PRIMARY KEY,
            rut TEXT NOT NULL,
            nombre TEXT NOT NULL,
            clave_acceso TEXT NOT NULL,
            rol TEXT NOT NULL
        );
    """)

    # 4. Tabla Multas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS multas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rut_socio TEXT NOT NULL,
            monto REAL NOT NULL,
            estado TEXT NOT NULL,
            motivo TEXT NOT NULL,
            FOREIGN KEY (rut_socio) REFERENCES socios(rut) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS danos_materiales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_material TEXT NOT NULL,
            rut_socio TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            porcentaje REAL NOT NULL,
            valor_reposicion_clp REAL NOT NULL,
            monto_multa REAL NOT NULL,
            fecha_registro TEXT NOT NULL,
            id_multa INTEGER NOT NULL,
            FOREIGN KEY (codigo_material) REFERENCES materiales(codigo),
            FOREIGN KEY (rut_socio) REFERENCES socios(rut),
            FOREIGN KEY (id_multa) REFERENCES multas(id)
        );
    """)

    # 5. Tabla Préstamos (Cabecera de transacción)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prestamos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rut_socio TEXT NOT NULL,
            id_empleado TEXT NOT NULL,
            fecha_registro TEXT NOT NULL,
            FOREIGN KEY (rut_socio) REFERENCES socios(rut),
            FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
        );
    """)

    # 6. Tabla Detalle de Préstamos (Líneas de la transacción)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_prestamos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_prestamo INTEGER NOT NULL,
            codigo_material TEXT NOT NULL,
            fecha_vencimiento TEXT NOT NULL,
            renovaciones_usadas INTEGER DEFAULT 0,
            fecha_devolucion TEXT,
            dias_multa_calculados INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (id_prestamo) REFERENCES prestamos(id) ON DELETE CASCADE,
            FOREIGN KEY (codigo_material) REFERENCES materiales(codigo)
        );
    """)

    cursor.execute("PRAGMA table_info(detalle_prestamos);")
    columnas_detalle = {fila[1] for fila in cursor.fetchall()}
    migrar_prestamos_existentes = "fecha_devolucion" not in columnas_detalle

    if migrar_prestamos_existentes:
        cursor.execute("ALTER TABLE detalle_prestamos ADD COLUMN fecha_devolucion TEXT;")
    if "dias_multa_calculados" not in columnas_detalle:
        cursor.execute("""
            ALTER TABLE detalle_prestamos
            ADD COLUMN dias_multa_calculados INTEGER NOT NULL DEFAULT 0;
        """)

    if migrar_prestamos_existentes:
        cursor.execute("""
            UPDATE detalle_prestamos
            SET fecha_devolucion = date('now', 'localtime')
            WHERE fecha_devolucion IS NULL
              AND (
                  NOT EXISTS (
                      SELECT 1
                      FROM materiales m
                      WHERE m.codigo = detalle_prestamos.codigo_material
                        AND m.estado = 'Prestado'
                  )
                  OR id <> (
                      SELECT MAX(dp.id)
                      FROM detalle_prestamos dp
                      JOIN materiales m ON m.codigo = dp.codigo_material
                      WHERE dp.codigo_material = detalle_prestamos.codigo_material
                        AND m.estado = 'Prestado'
                  )
              );
        """)

    conexion.commit()

    # Insertamos datos base de ejemplo si está vacía la tabla empleados y materiales
    cursor.execute("SELECT COUNT(*) FROM empleados;")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO empleados (id_empleado, rut, nombre, clave_acceso, rol)
            VALUES (?, ?, ?, ?, ?)
        """, ("ADM01", "11111111-1", "Ana González", hashear_clave("admin123"), "Administradora"))
        cursor.execute("""
            INSERT INTO empleados (id_empleado, rut, nombre, clave_acceso, rol)
            VALUES (?, ?, ?, ?, ?)
        """, ("EMP01", "22222222-2", "María Cordillera", hashear_clave("root123"), "Bibliotecaria"))

    # Corrige los roles de las cuentas de demostración creadas por versiones anteriores.
    cursor.execute("""
        UPDATE empleados
        SET rol = 'Administradora'
        WHERE id_empleado = 'EMP01'
          AND rut = '11111111-1'
          AND rol = 'Bibliotecaria'
    """)
    cursor.execute("""
        UPDATE empleados
        SET rol = 'Bibliotecaria'
        WHERE id_empleado = 'ADM01'
          AND rut = '22222222-2'
          AND rol = 'Administradora'
    """)

    # Migra las claves existentes en texto plano durante la actualización.
    cursor.execute("SELECT id_empleado, clave_acceso FROM empleados;")
    for id_empleado, clave in cursor.fetchall():
        if not es_hash_clave(clave):
            cursor.execute(
                "UPDATE empleados SET clave_acceso = ? WHERE id_empleado = ?",
                (hashear_clave(clave), id_empleado),
            )

    cursor.execute("SELECT COUNT(*) FROM socios;")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO socios (rut, nombre, direccion)
            VALUES (?, ?, ?)
        """, ("12345678-5", "Juan Pérez", "Av. Concha y Toro 1234, Puente Alto"))
        cursor.execute("""
            INSERT INTO socios (rut, nombre, direccion)
            VALUES (?, ?, ?)
        """, ("98765432-1", "Camila Silva", "Las Nieves 567, Puente Alto"))

    cursor.execute("SELECT COUNT(*) FROM materiales;")
    if cursor.fetchone()[0] == 0:
        # Libros iniciales
        cursor.execute("""
            INSERT INTO materiales (codigo, tipo, titulo, estado, valor_reposicion_usd, valor_reposicion_pesos, es_extranjero)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("LIB01", "Libro", "Cien Años de Soledad", "Disponible", 0.0, 18000, 0))
        cursor.execute("""
            INSERT INTO materiales (codigo, tipo, titulo, estado, valor_reposicion_usd, valor_reposicion_pesos, es_extranjero)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("LIB02", "Libro", "Clean Code", "Disponible", 35.0, 0, 1))
        # Revista
        cursor.execute("""
            INSERT INTO materiales (codigo, tipo, titulo, estado, valor_reposicion_usd, numero_edicion)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("REV01", "Revista", "National Geographic", "Disponible", 5.0, 245))
        # Multimedia
        cursor.execute("""
            INSERT INTO materiales (codigo, tipo, titulo, estado, valor_reposicion_usd, formato)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("MED01", "Multimedia", "Documental Cosmos HD", "Disponible", 15.0, "BluRay"))

    conexion.commit()
    conexion.close()
