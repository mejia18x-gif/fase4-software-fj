"""Entidad abstracta y cliente encapsulado."""

from abc import ABC, abstractmethod

from .validaciones import entero_positivo, texto_no_vacio, correo_valido, telefono_valido


class Entidad(ABC):
    """Representa cualquier objeto del negocio con ID y descripción."""

    def __init__(self, identificador: int):
        self._id = entero_positivo(identificador, "El identificador")

    @property
    def id(self) -> int:
        """ID solo de lectura para evitar modificaciones accidentales."""
        return self._id

    @abstractmethod
    def describir(self) -> str:
        """Cada entidad concreta decide cómo describirse."""


class Cliente(Entidad):
    """Mantiene los datos privados y evita valores incorrectos."""

    def __init__(self, identificador: int, nombre: str, correo: str, telefono: str):
        super().__init__(identificador)
        self.__nombre = texto_no_vacio(nombre, "El nombre", minimo=3)
        self.__correo = correo_valido(correo)
        self.__telefono = telefono_valido(telefono)

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def correo(self) -> str:
        return self.__correo

    @property
    def telefono(self) -> str:
        return self.__telefono

    def describir(self) -> str:
        # No mostrar correo ni teléfono en la salida por privacidad.
        return f"Cliente #{self.id}: {self.nombre}"
