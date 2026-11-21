"""Configuración del registro de sucesos y manejo central de errores."""

import logging
from functools import wraps
from pathlib import Path

from .errores import ErrorSoftwareFJ

LOGGER = logging.getLogger("software_fj")


def configurar_logs(archivo=None) -> Path:
    """Registra INFO y ERROR en texto, sin exponer datos personales."""
    ruta = Path(archivo) if archivo is not None else Path(__file__).resolve().parent.parent / "logs" / "eventos.log"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    LOGGER.setLevel(logging.INFO)
    LOGGER.propagate = False
    # Evita duplicar registros cuando se ejecuta la demo varias veces.
    for controlador in list(LOGGER.handlers):
        LOGGER.removeHandler(controlador)
        controlador.close()
    controlador = logging.FileHandler(ruta, encoding="utf-8")
    controlador.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    LOGGER.addHandler(controlador)
    return ruta


def registrar_operacion(funcion):
    """Decorador que demuestra try/except/else/finally y registra los errores."""

    @wraps(funcion)
    def ejecutor(*argumentos, **opciones):
        try:
            resultado = funcion(*argumentos, **opciones)
        except ErrorSoftwareFJ as error:
            LOGGER.error("%s: %s", funcion.__name__, error)
            raise
        except (TypeError, ValueError, ArithmeticError) as error:
            LOGGER.exception("Fallo no previsto durante %s", funcion.__name__)
            raise ErrorSoftwareFJ("No fue posible completar la operación.") from error
        else:
            LOGGER.info("Operación correcta: %s", funcion.__name__)
            return resultado
        finally:
            # Este bloque se ejecuta tanto si hubo éxito como si hubo error.
            LOGGER.debug("Finalizó %s", funcion.__name__)

    return ejecutor
