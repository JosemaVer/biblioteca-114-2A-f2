# 📚 Biblioteca Municipal Cordillera - Sistema de Gestión Seguro
**Evaluación Sumativa N°2: Programación Orientada a Objeto Seguro**
**Asignatura:** Programación Orientada a Objeto Seguro (TI3V21)
**Institución:** INACAP - Sede Puente Alto
**Autores:** Nelson Bonomi y José Vergara
**Docente:** Michael Arjel

---

## 📋 Descripción del Proyecto
El **Sistema de Gestión para la Biblioteca Municipal Cordillera** es una aplicación desarrollada en Python que implementa los paradigmas de **Programación Orientada a Objetos (POO)**, persistencia relacional en **SQLite** mediante el patrón **DAO (Data Access Object)**, seguridad contra **Inyección SQL**, validación de datos de entrada mediante el algoritmo **Módulo 11** para el RUT chileno, y consumo resiliente de servicios externos mediante una **API REST (mindicador.cl)** con tolerancia a fallos.

---

## 🏗️ Arquitectura del Sistema
El código sigue una estricta separación de responsabilidades en capas:

```text
biblioteca-114-2A-f2/
│
├── model/                      <-- CAPA DE DOMINIO Y POO
│   ├── estados.py              <-- Enums: EstadoMaterial, EstadoMulta
│   ├── excepciones.py          <-- Excepciones propias (Reglas de Negocio)
│   ├── persona.py              <-- Clase base Persona (validación RUT Módulo 11)
│   ├── socio.py                <-- Subclase Socio (dirección y multas asociadas)
│   ├── empleado.py             <-- Clase abstracta Empleado (credenciales)
│   ├── roles.py                <-- Subclases Bibliotecaria y Administradora
│   ├── material.py             <-- Clase abstracta Material
│   ├── libro.py                <-- Subclase Libro (14 días, 1 ren., cálculo USD)
│   ├── revista.py              <-- Subclase Revista (7 días, 0 ren.)
│   ├── multimedia.py           <-- Subclase Multimedia (3 días, 0 ren.)
│   ├── multa.py                <-- Clase Multa (monto, estados)
│   ├── detalle_prestamo.py     <-- Línea de detalle de préstamo
│   └── prestamo.py             <-- Transacción de préstamo
│
├── dao/                        <-- CAPA DE PERSISTENCIA (SQLite)
│   ├── conexion.py             <-- Conexión a SQLite y creación de tablas
│   ├── material_dao.py         <-- CRUD parametrizado de Materiales
│   ├── socio_dao.py            <-- CRUD parametrizado de Socios y Multas
│   └── prestamo_dao.py         <-- Transacciones atómicas de Préstamos y Detalles
│
├── services/                   <-- CAPA DE INTEGRACIÓN EXTERNA
│   ├── api_dolar.py            <-- Consumo de mindicador.cl con timeout y fallback
│   └── passwords.py            <-- Hash y verificación de contraseñas
│
├── data/                       <-- Datos locales creados al iniciar
│   └── biblioteca.db           <-- Base SQLite local (no se versiona)
│
├── main.py                     <-- Menú interactivo CLI con control de errores
├── requirements.txt            <-- Dependencias del proyecto (requests)
└── README.md                   <-- Documentación y justificaciones de seguridad
```

---

## ⚙️ Requisitos e Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/JosemaVer/biblioteca-114-2A-f2.git
cd biblioteca-114-2A-f2
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación
```bash
python main.py
```

En el primer inicio se crea `data/biblioteca.db` con sus tablas, cuentas de demostración y datos de ejemplo si las tablas correspondientes están vacías. Esta base de datos es local y está excluida de Git: cada clon mantiene sus propios registros. Los datos ingresados en un computador no se transfieren al de otro usuario.

---

## 🔒 Decisiones de Seguridad Implementadas

### 1. Prevención Total contra Inyección SQL (SQL Injection)
- **Problema:** Concatenar entradas del usuario en sentencias SQL (`f"SELECT * FROM ... WHERE codigo = '{codigo}'"`) permite manipular la consulta original.
- **Solución implementada:** Todas las operaciones de base de datos en la capa `dao/` utilizan **consultas parametrizadas con marcadores de posición (`?`)**.
- **Ejemplo en código (`dao/material_dao.py`):**
  ```python
  # Consulta 100% segura contra inyección SQL:
  cursor.execute("SELECT * FROM materiales WHERE codigo = ?", (codigo.strip().upper(),))
  ```

### 2. Encapsulamiento y Validación en Setters
- Los atributos se definen privados (`__atributo`).
- Se utiliza `@property` para la lectura y `@atributo.setter` para validar tipos, rangos numéricos y strings vacíos antes de su asignación.
- **Validación del RUT:** Se implementó el algoritmo oficial de **Módulo 11** en `model/persona.py`, verificando la suma ponderada del dígito verificador.

### 3. Reglas de Negocio mediante Excepciones Propias
- **Regla 1 (`SocioConMultaException`):** No se permite prestar material a socios con multas pendientes.
- **Regla 2 (`MaterialNoDisponibleException`):** No se permite prestar material cuyo estado sea diferente a `DISPONIBLE`.
- Ambas se lanzan desde la capa de dominio (`model/prestamo.py`) y son capturadas en `main.py` con `try/except` sin interrumpir la ejecución del programa.
- **Multas manuales y por atraso:** Desde "Gestión de Socios y Multas" se pueden asignar multas manuales a socios registrados. Los préstamos vencidos generan multas diarias de $1.000 por libro, $500 por revista y $1.500 por multimedia; se acumulan al iniciar el sistema y al devolver el material, sin volver a cobrar los días ya procesados.
- **Daños de materiales:** Al reportar daño se clasifica como leve (25%), moderado (50%) o grave (75%) del valor de reposición, y se guarda una descripción del daño. Un daño parcial deja el material disponible; la pérdida total aplica el 100% y marca el material como extraviado.
- **Precios del catálogo:** La administradora puede actualizar el valor de reposición desde "Gestión de Catálogo". Los libros conservan su moneda de origen (CLP o USD); revistas y multimedia usan USD.

### 4. Acceso por rol y protección de contraseñas
- El ingreso solicita el RUT del empleado con estructura `1234567-8` o `12.345.678-9` y su contraseña. El texto ingresado en la contraseña se muestra en pantalla; evite hacerlo en lugares compartidos.
- Las contraseñas se guardan como hashes PBKDF2-SHA256 con sal aleatoria; no se guardan en texto plano. Al iniciar, las claves en texto plano de bases de datos existentes se migran automáticamente.
- Las opciones de catálogo, socios y multas se filtran según el rol. Las acciones administrativas también conservan comprobaciones de permisos al ejecutarse.
- Para cambiar de usuario hay que volver a autenticarse. Cada empleado puede cambiar su contraseña desde "Mi sesión" después de validar la actual; las nuevas contraseñas deben tener al menos 8 caracteres.
- Las cuentas de demostración se crean en `dao/conexion.py`, dentro de `inicializar_base_datos()`: la Administradora se registra primero con RUT `11111111-1` / contraseña inicial `admin123` (ID `ADM01`), seguida de la Bibliotecaria con RUT `22222222-2` / contraseña inicial `root123` (ID `EMP01`). Las bases anteriores corrigen automáticamente los roles de estas cuentas al iniciar. En SQLite, la tabla `empleados` guarda las contraseñas como hashes; no es posible leerlas directamente desde la base de datos. Cámbielas desde "Mi sesión" antes de usar datos reales.

### 5. Consumo Resiliente de API con Timeout
- La consulta a `https://mindicador.cl/api/dolar` cuenta con un parámetro `timeout=5`.
- Si se pierde la conexión a internet o el servidor no responde, se captura `requests.RequestException`, se emite una advertencia clara por consola y se utiliza un **valor de contingencia configurado ($984.82 CLP)**, garantizando la continuidad operativa del sistema.

---

## 🤖 Registro y Análisis de Asistencia con Inteligencia Artificial

| Código Sugerido por IA | Decisión Adoptada | Razón Técnica y Justificación |
| :--- | :--- | :--- |
| **Persistencia inicial en archivos JSON planos** | ❌ **Descartado / Reemplazado** | La rúbrica de la Unidad 2 y 3 exige persistencia relacional en SQLite con capa DAO y prevención de inyección SQL mediante consultas parametrizadas (`?`). |
| **Generación de consultas SQL con `f-strings`** | ❌ **Rechazado tajantemente** | La interpolación de cadenas genera vulnerabilidades críticas de Inyección SQL. Se refactorizó todo a tuplas parametrizadas con `?`. |
| **Validación de RUT con algoritmo Módulo 11 en setter** | ✅ **Adoptado e Integrado** | Asegura que ningún objeto `Persona` o `Socio` pueda crearse con un identificador tributario erróneo o falsificado. |
| **Consumo de API Dólar con Timeout y Fallback** | ✏️ **Modificado y Ajustado** | La IA sugirió un `try/except` genérico. Se ajustó para capturar específicamente `requests.exceptions.Timeout` y `requests.exceptions.RequestException`, retornando el valor observado del dólar de octubre 2026 ($984.82 CLP). |

---

## 📓 Bitácora de Actividades

| Sesión / Fecha | Tema / Actividad Principal | Avances y Entregables | Estado |
| :--- | :--- | :--- | :--- |
| **09/09/2026** | Inicialización del Repositorio | Creación del repositorio público, estructura base y bitácora. | Completado |
| **21/09/2026** | Implementación Modelo UML v1 | Clases base, diagramas iniciales y pruebas de consola. | Completado |
| **02/10/2026** | Arquitectura Final Evaluada (Sumativa 2) | Implementación de `model/`, `dao/` (SQLite parametrizado), consumo API dólar con timeout, validación Módulo 11, excepciones propias y suite de tests. | 100% Operativo 🚀 |
| **04/10/2026** | Refactorización de la arquitectura | Separación en módulos `model/`, `dao/` y `services/`; actualización del CLI, persistencia SQLite y pruebas. | Completado |
| **05/10/2026** | Corrección de roles y autenticación | Migración de cuentas de demostración para asignar correctamente el rol de Administradora; credenciales con hash, orden del listado y pruebas aisladas en SQLite. Se documentó también la ejecución normal del sistema sin reutilizar un lanzador de depuración obsoleto. | Completado |
| **06/10/2026** | Consolidación de versión para entrega | Pago de multas mediante selección desde la lista de pendientes, carga de socios con RUT históricos y actualización de instrucciones, persistencia local y bitácora. Se excluyeron los scripts de pruebas y la previsualización de arquitectura de la rama `main`. | Completado |

### 📝 Registro Detallado de Sesiones

#### Sesión 4: Revisión y consolidación de la arquitectura (03–04/10/2026)

- **Actividades realizadas:**
  - Se reorganizó el proyecto en capas: `model/` para las entidades y reglas de dominio, `dao/` para la persistencia y `services/` para integraciones externas.
  - Se trasladaron las clases del dominio a `model/` y se actualizaron sus importaciones y usos desde el menú de `main.py`.
  - Se consolidó la persistencia en SQLite mediante `dao/conexion.py` y los DAO de materiales, socios y préstamos, con consultas parametrizadas y operaciones transaccionales.
  - Se centralizó el consumo de la API del dólar en `services/api_dolar.py`, incluyendo timeout y manejo de errores de conexión.
  - Se actualizaron las pruebas automatizadas para la arquitectura y persistencia actuales.
- **Verificación:** Se ejecutaron las 9 pruebas de `test_biblioteca.py`; todas finalizaron correctamente.
- **Entregable:** Refactorización publicada en GitHub en el commit `5572ec6`.

#### Sesión 5: Corrección de autenticación y roles (05/10/2026)

- **Actividades realizadas:**
  - Se corrigió la discrepancia entre los datos de demostración y los roles almacenados: la cuenta de Ana González (RUT `11111111-1`) queda como Administradora.
  - Se agregó una migración acotada por ID y RUT para actualizar automáticamente el rol de las cuentas de demostración ya existentes, sin cambiar sus identificadores ni las referencias de préstamos.
  - Se ordenó el listado de empleados para mostrar primero a la Administradora y se alinearon las credenciales documentadas con las cuentas sembradas por el sistema.
  - Se añadieron pruebas con una base SQLite temporal para verificar la migración, el rol devuelto al autenticar y las credenciales con contraseña hasheada.
  - Se documentó cómo iniciar `main.py` directamente con el intérprete del entorno virtual cuando se reutiliza un comando de depuración `debugpy` que ya no tiene un proceso escuchando.
- **Verificación:** Las pruebas enfocadas de creación de cuentas y migración de roles finalizaron correctamente; Pylance no reportó errores en los archivos modificados.

#### Sesión 6: Consolidación de la versión para entrega (06/10/2026)

- **Actividades realizadas:**
  - Se actualizó el pago de una multa específica para mostrar las multas pendientes y permitir elegir su ID, rechazando identificadores que no estén en la lista.
  - Se ajustó la carga de socios desde SQLite para admitir RUT históricos ya almacenados, manteniendo la validación al registrar socios nuevos.
  - Se integró en `main` la versión de desarrollo y se retiraron de la entrega los dos archivos de pruebas y la previsualización de arquitectura.
  - Se actualizaron las instrucciones de instalación y la documentación de la base SQLite local, además de esta bitácora.
- **Verificación:** Antes de retirar los scripts de prueba de la versión de entrega, se ejecutaron las 10 pruebas automatizadas y se verificó el flujo de selección de multas.
- **Entregable:** Versión consolidada en la rama `main`.