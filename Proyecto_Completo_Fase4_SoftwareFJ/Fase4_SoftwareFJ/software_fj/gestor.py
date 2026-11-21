"""Gestor del proyecto: usa listas en memoria y coordina las operaciones."""

from .entidades import Cliente
from .errores import (DatoInvalidoError, RegistroDuplicadoError,
                      RegistroNoEncontradoError, ServicioNoDisponibleError)
from .registros import registrar_operacion
from .reservas import Reserva
from .servicios import AsesoriaEspecializada, AlquilerEquipo, ServicioSala
from .validaciones import entero_positivo


class GestorSoftwareFJ:
    """No utiliza bases de datos; almacena temporalmente objetos en listas."""

    def __init__(self):
        self.__clientes = []
        self.__servicios = []
        self.__reservas = []

    @property
    def clientes(self) -> tuple:
        return tuple(self.__clientes)

    @property
    def servicios(self) -> tuple:
        return tuple(self.__servicios)

    @property
    def reservas(self) -> tuple:
        return tuple(self.__reservas)

    @staticmethod
    def __buscar(lista, identificador, nombre):
        entero_positivo(identificador, f"El ID de {nombre}")
        try:
            return next(objeto for objeto in lista if objeto.id == identificador)
        except StopIteration as error:
            # Encadenamiento: preserva la causa original de la excepción.
            raise RegistroNoEncontradoError(f"No existe {nombre} con ID {identificador}.") from error

    def __comprobar_id(self, lista, identificador, nombre):
        entero_positivo(identificador, f"El ID de {nombre}")
        if any(objeto.id == identificador for objeto in lista):
            raise RegistroDuplicadoError(f"Ya existe {nombre} con ID {identificador}.")

    @registrar_operacion
    def registrar_cliente(self, identificador, nombre, correo, telefono) -> Cliente:
        self.__comprobar_id(self.__clientes, identificador, "cliente")
        cliente = Cliente(identificador, nombre, correo, telefono)
        if any(c.correo == cliente.correo for c in self.__clientes):
            raise RegistroDuplicadoError("El correo ya está registrado.")
        self.__clientes.append(cliente)
        return cliente

    @registrar_operacion
    def registrar_sala(self, identificador, nombre, tarifa, capacidad, ubicacion, disponible=True):
        self.__comprobar_id(self.__servicios, identificador, "servicio")
        servicio = ServicioSala(identificador, nombre, tarifa, capacidad, ubicacion, disponible)
        self.__servicios.append(servicio)
        return servicio

    @registrar_operacion
    def registrar_equipo(self, identificador, nombre, tarifa, equipo, disponible=True):
        self.__comprobar_id(self.__servicios, identificador, "servicio")
        servicio = AlquilerEquipo(identificador, nombre, tarifa, equipo, disponible)
        self.__servicios.append(servicio)
        return servicio

    @registrar_operacion
    def registrar_asesoria(self, identificador, nombre, tarifa, especialidad, disponible=True):
        self.__comprobar_id(self.__servicios, identificador, "servicio")
        servicio = AsesoriaEspecializada(identificador, nombre, tarifa, especialidad, disponible)
        self.__servicios.append(servicio)
        return servicio

    @registrar_operacion
    def crear_reserva(self, identificador, id_cliente, id_servicio, duracion) -> Reserva:
        self.__comprobar_id(self.__reservas, identificador, "reserva")
        cliente = self.__buscar(self.__clientes, id_cliente, "cliente")
        servicio = self.__buscar(self.__servicios, id_servicio, "servicio")
        if not servicio.disponible:
            raise ServicioNoDisponibleError("El servicio elegido no está disponible.")
        reserva = Reserva(identificador, cliente, servicio, duracion)
        self.__reservas.append(reserva)
        return reserva

    @registrar_operacion
    def confirmar_reserva(self, identificador):
        reserva = self.__buscar(self.__reservas, identificador, "reserva")
        reserva.confirmar()
        return reserva

    @registrar_operacion
    def cancelar_reserva(self, identificador):
        reserva = self.__buscar(self.__reservas, identificador, "reserva")
        reserva.cancelar()
        return reserva

    @registrar_operacion
    def procesar_reserva(self, identificador, impuesto=0, descuento=0):
        reserva = self.__buscar(self.__reservas, identificador, "reserva")
        return reserva.procesar(impuesto, descuento)

    @registrar_operacion
    def cambiar_disponibilidad(self, id_servicio, disponible: bool):
        servicio = self.__buscar(self.__servicios, id_servicio, "servicio")
        servicio.disponible = disponible
        return servicio
