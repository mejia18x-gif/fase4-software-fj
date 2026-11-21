"""Servicios abstractos y sus tres especializaciones polimórficas."""

from abc import abstractmethod
from decimal import Decimal

from .entidades import Entidad
from .errores import DatoInvalidoError
from .validaciones import dinero_positivo, entero_positivo, texto_no_vacio, valor_final


class Servicio(Entidad):
    """Contrato general que obliga a calcular, validar y describir."""

    def __init__(self, identificador: int, nombre: str, tarifa: int, disponible=True):
        super().__init__(identificador)
        self._nombre = texto_no_vacio(nombre, "El nombre del servicio", minimo=3)
        self._tarifa = dinero_positivo(tarifa, "La tarifa")
        if type(disponible) is not bool:
            raise DatoInvalidoError("La disponibilidad debe ser True o False.")
        self._disponible = disponible

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool) -> None:
        if type(estado) is not bool:
            raise DatoInvalidoError("La disponibilidad debe ser True o False.")
        self._disponible = estado

    @property
    def tarifa(self) -> Decimal:
        return self._tarifa

    @abstractmethod
    def validar_parametros(self, duracion: int) -> None:
        """Comprueba que la duración corresponda al servicio concreto."""

    @abstractmethod
    def calcular_costo(self, duracion: int, impuesto=0, descuento=0) -> Decimal:
        """Parámetros opcionales permiten variantes de cálculo de costo."""

    @abstractmethod
    def describir(self) -> str:
        """Entrega una descripción particular del servicio."""


class ServicioSala(Servicio):
    """Reserva de salas por horas; incluye una tarifa fija de limpieza."""

    LIMPIEZA = Decimal("10000")

    def __init__(self, identificador, nombre, tarifa, capacidad, ubicacion, disponible=True):
        super().__init__(identificador, nombre, tarifa, disponible)
        self.__capacidad = entero_positivo(capacidad, "La capacidad")
        self.__ubicacion = texto_no_vacio(ubicacion, "La ubicación")

    def validar_parametros(self, duracion: int) -> None:
        entero_positivo(duracion, "La duración", maximo=12)

    def calcular_costo(self, duracion: int, impuesto=0, descuento=0) -> Decimal:
        self.validar_parametros(duracion)
        subtotal = self.tarifa * duracion + self.LIMPIEZA
        return valor_final(subtotal, impuesto, descuento)

    def describir(self) -> str:
        return f"Sala #{self.id}: {self.nombre}, capacidad {self.__capacidad}, {self.__ubicacion}"


class AlquilerEquipo(Servicio):
    """Alquiler de equipos por horas con duración máxima de 72 horas."""

    def __init__(self, identificador, nombre, tarifa, equipo, disponible=True):
        super().__init__(identificador, nombre, tarifa, disponible)
        self.__equipo = texto_no_vacio(equipo, "El tipo de equipo")

    def validar_parametros(self, duracion: int) -> None:
        entero_positivo(duracion, "La duración", maximo=72)

    def calcular_costo(self, duracion: int, impuesto=0, descuento=0) -> Decimal:
        self.validar_parametros(duracion)
        return valor_final(self.tarifa * duracion, impuesto, descuento)

    def describir(self) -> str:
        return f"Equipo #{self.id}: {self.nombre}, tipo {self.__equipo}"


class AsesoriaEspecializada(Servicio):
    """Asesorías especializadas por horas, hasta ocho horas por reserva."""

    def __init__(self, identificador, nombre, tarifa, especialidad, disponible=True):
        super().__init__(identificador, nombre, tarifa, disponible)
        self.__especialidad = texto_no_vacio(especialidad, "La especialidad")

    def validar_parametros(self, duracion: int) -> None:
        entero_positivo(duracion, "La duración", maximo=8)

    def calcular_costo(self, duracion: int, impuesto=0, descuento=0) -> Decimal:
        self.validar_parametros(duracion)
        return valor_final(self.tarifa * duracion, impuesto, descuento)

    def describir(self) -> str:
        return f"Asesoría #{self.id}: {self.nombre}, área {self.__especialidad}"
