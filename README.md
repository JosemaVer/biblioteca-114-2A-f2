# 📚 Biblioteca - 114-2A-f2

Repositorio del proyecto y bitácora de seguimiento para el módulo **Biblioteca (114-2A-f2)**.

---

## 📋 Información del Módulo

- **Módulo / Asignatura:** Biblioteca (114-2A-f2)
- **Autor / Estudiante:** JosemaVer
- **Estado del Proyecto:** En progreso 🚀

---

## 🎯 Objetivos

1. Implementar la solución técnica y de gestión requerida para el sistema de biblioteca.
2. Mantener un registro cronológico y estructurado de los avances, decisiones técnicas y actividades realizadas.
3. Versionar el código fuente y la documentación a través de Git y GitHub.

---

## 📓 Bitácora de Actividades

| Sesión / Fecha | Tema / Actividad Principal | Avances y Entregables | Notas / Pendientes |
| :--- | :--- | :--- | :--- |
| **09/09/2026** | Inicialización del Repositorio | Creación del repositorio público, estructura base y plantilla de bitácora. | Definir primeros requerimientos, clases y modelado del sistema. |
| **21/09/2026** | Implementación Modelo UML y Lógica de Negocio | Clases base, materiales, roles, multas, préstamos, persistencia JSON y CLI robusto con manejo de excepciones. | Sistema 100% operativo y verificado con pruebas unitarias. |
| **04/10/2026** | Refactorización de la arquitectura | Separación en módulos `model/`, `dao/` y `services/`; actualización del CLI, persistencia SQLite y pruebas. | Completado |

---

### 📝 Registro Detallado de Sesiones

#### Sesión 1: Inicialización del Repositorio (09/09/2026)
- **Actividades realizadas:**
  - Creación y configuración del repositorio remoto en GitHub.
  - Creación del directorio local del proyecto en `Documents\Programación\biblioteca-114-2A-f2`.
  - Creación del archivo de bitácora inicial (`README.md`).

#### Sesión 2: Arquitectura Completa y Menú Interactivo (21/09/2026)
- **Actividades realizadas:**
  - Implementación de enumeraciones (`EstadoMaterial`, `EstadoMulta`) en `estados.py`.
  - Jerarquía de materiales: `Material` (abstracta), `Libro`, `Revista` y `Multimedia`.
  - Jerarquía de empleados y roles: `Bibliotecaria` y `Administradora` en `roles.py`.
  - Lógica de multas y préstamos: `Multa`, `DetallePrestamo`, `Prestamo` y actualización de `Socio`.
  - Controlador central `Biblioteca` en `biblioteca.py` con persistencia automática en formato JSON.
  - Menú CLI interactivo en `main.py` blindado con validaciones de tipos y captura de excepciones (`try/except`).
  - Suite de pruebas unitarias en `test_biblioteca.py` pasando al 100%.

#### Sesión 4: Revisión y consolidación de la arquitectura (03–04/10/2026)

- **Actividades realizadas:**
  - Se reorganizó el proyecto en capas: `model/` para las entidades y reglas de dominio, `dao/` para la persistencia y `services/` para integraciones externas.
  - Se trasladaron las clases del dominio a `model/` y se actualizaron sus importaciones y usos desde el menú de `main.py`.
  - Se consolidó la persistencia en SQLite mediante `dao/conexion.py` y los DAO de materiales, socios y préstamos, con consultas parametrizadas y operaciones transaccionales.
  - Se centralizó el consumo de la API del dólar en `services/api_dolar.py`, incluyendo timeout y manejo de errores de conexión.
  - Se actualizaron las pruebas automatizadas para la arquitectura y persistencia actuales.
- **Verificación:** Se ejecutaron las 9 pruebas de `test_biblioteca.py`; todas finalizaron correctamente.
- **Entregable:** Refactorización publicada en GitHub en el commit `5572ec6`.
