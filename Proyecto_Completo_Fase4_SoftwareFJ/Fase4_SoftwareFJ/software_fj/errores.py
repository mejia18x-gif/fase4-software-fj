"""Excepciones propias: permiten dar mensajes claros sin detener el sistema."""


class ErrorSoftwareFJ(Exception):
    """Clase base para todos los errores controlados de la aplicación."""


class DatoInvalidoError(ErrorSoftwareFJ):
    """Se presenta cuando un valor no cumple las reglas de validación."""


class RegistroDuplicadoError(ErrorSoftwareFJ):
    """Se presenta cuando un identificador o un correo ya existe."""


class RegistroNoEncontradoError(ErrorSoftwareFJ):
    """Se presenta cuando no existe el cliente, servicio o reserva buscado."""


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """Se presenta cuando el servicio solicitado no está disponible."""


class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """Se presenta al intentar una transición de estado no permitida."""
