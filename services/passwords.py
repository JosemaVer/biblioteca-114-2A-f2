"""Hashing y verificación de contraseñas de empleados."""
import hashlib
import hmac
import secrets


_ALGORITHM = "pbkdf2_sha256"
_ITERATIONS = 600_000
_SALT_BYTES = 16
_DIGEST_BYTES = 32


def es_hash_clave(valor: str) -> bool:
    """Indica si el valor tiene el formato de hash usado por el sistema."""
    partes = valor.split("$")
    if len(partes) != 4 or partes[0] != _ALGORITHM:
        return False

    try:
        iteraciones = int(partes[1])
        sal = bytes.fromhex(partes[2])
        digest = bytes.fromhex(partes[3])
    except ValueError:
        return False

    return (
        1 <= iteraciones <= 1_000_000
        and len(sal) == _SALT_BYTES
        and len(digest) == _DIGEST_BYTES
    )


def hashear_clave(clave: str) -> str:
    """Genera un hash PBKDF2-SHA256 con sal aleatoria para una contraseña."""
    sal = secrets.token_bytes(_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        clave.encode("utf-8"),
        sal,
        _ITERATIONS,
        dklen=_DIGEST_BYTES,
    )
    return f"{_ALGORITHM}${_ITERATIONS}${sal.hex()}${digest.hex()}"


def verificar_clave(clave: str, hash_guardado: str) -> bool:
    """Compara una contraseña con un hash guardado sin revelar tiempos útiles."""
    if not es_hash_clave(hash_guardado):
        return False

    _, iteraciones, sal_hex, digest_guardado = hash_guardado.split("$")
    digest_calculado = hashlib.pbkdf2_hmac(
        "sha256",
        clave.encode("utf-8"),
        bytes.fromhex(sal_hex),
        int(iteraciones),
        dklen=_DIGEST_BYTES,
    ).hex()
    return hmac.compare_digest(digest_calculado, digest_guardado)
