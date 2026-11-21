"""Reservas y transiciones de estado protegidas por validaciones."""

from enum import Enum
from decimal import Decimal

from .entidades import Cliente
from .registros import LOGGER
from .servicios import Servicio
from .errores import DatoInvalidoError, OperacionNoPermitidaError, ServicioNoDisponibleError
from .validaciones import entero_positivo


class EstadoReserva(Enum):
    """Estados posibles; ayuda a evitar cadenas inconsistentes."""

    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    PROCESADA = "procesada"


class Reserva:
    """Relaciona un cliente, un servicio y la duración contratada."""

    def __init__(self, identificador: int, cliente: Cliente, servicio: Servicio, duracion: int):
        self.__id = entero_positivo(identificador, "El identificador de reserva")
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("La reserva requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("La reserva requiere un servicio válido.")
        servicio.validar_parametros(duracion)
        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion = duracion
        self.__estado = EstadoReserva.PENDIENTE
        self.__costo_final = None

    @property
    def id(self) -> int:
        return self.__id

    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        return self.__servicio

    @property
    def estado(self) -> EstadoReserva:
        return self.__estado

    @property
    def duracion(self) -> int:
        return self.__duracion

    @property
    def costo_final(self) -> Decimal | None:
        return self.__costo_final

    def confirmar(self) -> None:
        """Solo confirma una reserva pendiente y con servicio disponible."""
        if self.__estado is not EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError("Solo se puede confirmar una reserva pendiente.")
        if not self.__servicio.disponible:
            raise ServicioNoDisponibleError("El servicio no está disponible para confirmar.")
        self.__estado = EstadoReserva.CONFIRMADA

    def cancelar(self) -> None:
        """Permite cancelar únicamente reservas pendientes o confirmadas."""
        if self.__estado not in (EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA):
            raise OperacionNoPermitidaError("Esta reserva ya no se puede cancelar.")
        self.__estado = EstadoReserva.CANCELADA

    def procesar(self, impuesto=0, descuento=0) -> Decimal:
        """Calcula el valor antes de marcar la reserva como procesada."""
        if self.__estado is not EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError("Solo se puede procesar una reserva confirmada.")
        try:
            # Se llama al método polimórfico del servicio correspondiente.
            costo = self.__servicio.calcular_costo(self.__duracion, impuesto, descuento)
        except (DatoInvalidoError, ArithmeticError):
            # Conservamos el estado CONFIRMADA si falla el cálculo.
            raise
        else:
            self.__costo_final = costo
            self.__estado = EstadoReserva.PROCESADA
            return costo
        finally:
            # El intento queda identificado incluso si el cálculo falló.
            LOGGER.info("Terminó el intento de cálculo de la reserva #%s", self.id)

    def describir(self) -> str:
        return (f"Reserva #{self.id}: {self.cliente.nombre} / {self.servicio.nombre} "
                f"({self.duracion} h), estado={self.estado.value}")
