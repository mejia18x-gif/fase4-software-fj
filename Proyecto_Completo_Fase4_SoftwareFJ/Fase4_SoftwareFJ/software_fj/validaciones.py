"""Validaciones reutilizables de datos, identificadores y valores monetarios."""

import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from .errores import DatoInvalidoError

CENTAVO = Decimal("0.01")


def entero_positivo(valor, nombre: str, maximo=None) -> int:
    """Acepta únicamente enteros positivos; evita confundir True con 1."""
    if type(valor) is not int or valor <= 0:
        raise DatoInvalidoError(f"{nombre} debe ser un entero positivo.")
    if maximo is not None and valor > maximo:
        raise DatoInvalidoError(f"{nombre} no puede superar {maximo}.")
    return valor


def texto_no_vacio(valor, nombre: str, minimo: int = 1) -> str:
    """Rechaza cadenas vacías o con solo espacios."""
    if not isinstance(valor, str) or len(valor.strip()) < minimo:
        raise DatoInvalidoError(f"{nombre} debe tener al menos {minimo} carácter(es).")
    return valor.strip()


def dinero_positivo(valor, nombre: str) -> Decimal:
    """Convierte a Decimal y rechaza importes negativos, NaN e infinitos."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float, str, Decimal)):
        raise DatoInvalidoError(f"{nombre} debe ser un número positivo.")
    try:
        numero = Decimal(str(valor).strip())
    except (InvalidOperation, ValueError, OverflowError) as error:
        raise DatoInvalidoError(f"{nombre} contiene un valor numérico inválido.") from error
    if not numero.is_finite() or numero <= 0:
        raise DatoInvalidoError(f"{nombre} debe ser mayor que cero y finito.")
    return numero


def porcentaje(valor, nombre: str) -> Decimal:
    """Valida porcentajes entre 0 y 100 incluidos."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float, str, Decimal)):
        raise DatoInvalidoError(f"{nombre} debe ser un porcentaje numérico.")
    try:
        numero = Decimal(str(valor).strip())
    except (InvalidOperation, ValueError, OverflowError) as error:
        raise DatoInvalidoError(f"{nombre} no tiene un formato válido.") from error
    if not numero.is_finite() or not (Decimal("0") <= numero <= Decimal("100")):
        raise DatoInvalidoError(f"{nombre} debe estar entre 0 y 100.")
    return numero


def valor_final(subtotal: Decimal, impuesto=0, descuento=0) -> Decimal:
    """Aplica primero descuento y luego impuesto; redondea a 2 decimales."""
    tasa_impuesto = porcentaje(impuesto, "El impuesto")
    tasa_descuento = porcentaje(descuento, "El descuento")
    try:
        total = subtotal * (1 - tasa_descuento / 100) * (1 + tasa_impuesto / 100)
        return total.quantize(CENTAVO, rounding=ROUND_HALF_UP)
    except (InvalidOperation, OverflowError) as error:
        raise DatoInvalidoError("No se puede calcular el costo con estos valores.") from error


def correo_valido(valor: str) -> str:
    """Comprueba una estructura básica de correo sin requerir internet."""
    correo = texto_no_vacio(valor, "El correo")
    if len(correo) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", correo):
        raise DatoInvalidoError("El correo no tiene un formato válido.")
    return correo.lower()


def telefono_valido(valor: str) -> str:
    """Admite entre 7 y 15 dígitos, representados como texto."""
    if not isinstance(valor, str) or not valor.isascii() or not valor.isdigit():
        raise DatoInvalidoError("El teléfono debe contener solo dígitos.")
    if not 7 <= len(valor) <= 15:
        raise DatoInvalidoError("El teléfono debe tener entre 7 y 15 dígitos.")
    return valor
