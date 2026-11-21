"""Pruebas automáticas con unittest (biblioteca estándar de Python)."""

import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from software_fj.entidades import Cliente, Entidad
from software_fj.errores import (
    DatoInvalidoError, ErrorSoftwareFJ, OperacionNoPermitidaError, RegistroDuplicadoError,
    RegistroNoEncontradoError, ServicioNoDisponibleError,
)
from software_fj.gestor import GestorSoftwareFJ
from software_fj.registros import configurar_logs
from software_fj.reservas import EstadoReserva, Reserva
from software_fj.servicios import AsesoriaEspecializada, AlquilerEquipo, Servicio, ServicioSala


class PruebasSoftwareFJ(unittest.TestCase):
    """Cada prueba comienza con un gestor nuevo para evitar dependencias."""

    @classmethod
    def setUpClass(cls):
        cls.temporal = tempfile.TemporaryDirectory()
        cls.archivo_log = Path(cls.temporal.name) / "pruebas.log"
        configurar_logs(cls.archivo_log)

    @classmethod
    def tearDownClass(cls):
        # Cierra los manejadores antes de borrar el directorio temporal.
        configurar_logs(Path(cls.temporal.name) / "cierre.log")
        from software_fj.registros import LOGGER
        for controlador in list(LOGGER.handlers):
            LOGGER.removeHandler(controlador)
            controlador.close()
        cls.temporal.cleanup()

    def setUp(self):
        self.gestor = GestorSoftwareFJ()
        self.cliente = self.gestor.registrar_cliente(1, "Ana Torres", "ana@ejemplo.com", "3001234567")
        self.sala = self.gestor.registrar_sala(10, "Sala Norte", 50000, 8, "Piso 1")

    def test_entidad_abstracta_no_instanciable(self):
        with self.assertRaises(TypeError):
            Entidad(1)

    def test_servicio_abstracto_no_instanciable(self):
        with self.assertRaises(TypeError):
            Servicio(11, "Servicio", 1000)

    def test_cliente_valido(self):
        self.assertEqual(self.cliente.nombre, "Ana Torres")
        self.assertEqual(self.cliente.correo, "ana@ejemplo.com")

    def test_correo_invalido(self):
        with self.assertRaises(DatoInvalidoError):
            self.gestor.registrar_cliente(2, "Sergio Pinto", "sin_arroba", "3001112233")

    def test_telefono_invalido(self):
        with self.assertRaises(DatoInvalidoError):
            self.gestor.registrar_cliente(2, "Sergio Pinto", "sergio@ejemplo.com", "numero")

    def test_nombre_corto(self):
        with self.assertRaises(DatoInvalidoError):
            self.gestor.registrar_cliente(2, "A", "nuevo@ejemplo.com", "3001112233")

    def test_id_booleano_invalido(self):
        with self.assertRaises(DatoInvalidoError):
            self.gestor.registrar_cliente(True, "Carla López", "carla@ejemplo.com", "3001112233")

    def test_cliente_duplicado(self):
        with self.assertRaises(RegistroDuplicadoError):
            self.gestor.registrar_cliente(1, "Carla López", "carla@ejemplo.com", "3001112233")

    def test_correo_duplicado_case_insensitive(self):
        with self.assertRaises(RegistroDuplicadoError):
            self.gestor.registrar_cliente(2, "Carla López", "ANA@EJEMPLO.COM", "3001112233")

    def test_servicios_especializados_y_polimorfismo(self):
        equipo = self.gestor.registrar_equipo(11, "Equipo Dell", 30000, "Portátil")
        asesoria = self.gestor.registrar_asesoria(12, "Sesión de redes", 75000, "Redes")
        self.assertIsInstance(self.sala, Servicio)
        self.assertIsInstance(equipo, Servicio)
        self.assertIsInstance(asesoria, Servicio)
        self.assertEqual([s.calcular_costo(2) for s in (self.sala, equipo, asesoria)],
                         [Decimal("110000.00"), Decimal("60000.00"), Decimal("150000.00")])

    def test_precio_negativo(self):
        with self.assertRaises(DatoInvalidoError):
            self.gestor.registrar_equipo(11, "Equipo defectuoso", -30, "Portátil")

    def test_precio_nan(self):
        with self.assertRaises(DatoInvalidoError):
            self.gestor.registrar_equipo(11, "Equipo defectuoso", "NaN", "Portátil")

    def test_precio_infinito(self):
        with self.assertRaises(DatoInvalidoError):
            self.gestor.registrar_equipo(11, "Equipo defectuoso", float("inf"), "Portátil")

    def test_servicio_duplicado(self):
        with self.assertRaises(RegistroDuplicadoError):
            self.gestor.registrar_equipo(10, "Equipo", 1000, "Portátil")

    def test_capacidad_invalida(self):
        with self.assertRaises(DatoInvalidoError):
            self.gestor.registrar_sala(11, "Sala Este", 20000, 0, "Piso 2")

    def test_disponibilidad_invalida(self):
        with self.assertRaises(DatoInvalidoError):
            self.gestor.registrar_equipo(11, "Equipo", 1000, "Portátil", disponible="sí")

    def test_duracion_cero(self):
        with self.assertRaises(DatoInvalidoError):
            self.gestor.crear_reserva(20, 1, 10, 0)

    def test_duracion_excede_limite_sala(self):
        with self.assertRaises(DatoInvalidoError):
            self.gestor.crear_reserva(20, 1, 10, 13)

    def test_no_disponible(self):
        self.gestor.cambiar_disponibilidad(10, False)
        with self.assertRaises(ServicioNoDisponibleError):
            self.gestor.crear_reserva(20, 1, 10, 2)

    def test_busqueda_inexistente_con_causa(self):
        with self.assertRaises(RegistroNoEncontradoError) as captura:
            self.gestor.crear_reserva(20, 999, 10, 2)
        self.assertIsInstance(captura.exception.__cause__, StopIteration)

    def test_reserva_valida(self):
        reserva = self.gestor.crear_reserva(20, 1, 10, 2)
        self.assertEqual(reserva.estado, EstadoReserva.PENDIENTE)
        self.gestor.confirmar_reserva(20)
        self.assertEqual(reserva.estado, EstadoReserva.CONFIRMADA)

    def test_confirmar_dos_veces(self):
        self.gestor.crear_reserva(20, 1, 10, 1)
        self.gestor.confirmar_reserva(20)
        with self.assertRaises(OperacionNoPermitidaError):
            self.gestor.confirmar_reserva(20)

    def test_procesar_sin_confirmar(self):
        self.gestor.crear_reserva(20, 1, 10, 2)
        with self.assertRaises(OperacionNoPermitidaError):
            self.gestor.procesar_reserva(20)

    def test_impuesto_descuento(self):
        self.gestor.crear_reserva(20, 1, 10, 2)
        self.gestor.confirmar_reserva(20)
        self.assertEqual(self.gestor.procesar_reserva(20, 19, 10), Decimal("117810.00"))

    def test_descuento_invalido_no_cambia_estado(self):
        reserva = self.gestor.crear_reserva(20, 1, 10, 2)
        self.gestor.confirmar_reserva(20)
        with self.assertRaises(DatoInvalidoError):
            self.gestor.procesar_reserva(20, descuento=120)
        self.assertEqual(reserva.estado, EstadoReserva.CONFIRMADA)
        self.assertIsNone(reserva.costo_final)
        self.assertEqual(self.gestor.procesar_reserva(20), Decimal("110000.00"))

    def test_cancelar_y_no_procesar(self):
        reserva = self.gestor.crear_reserva(20, 1, 10, 2)
        self.gestor.cancelar_reserva(20)
        self.assertEqual(reserva.estado, EstadoReserva.CANCELADA)
        with self.assertRaises(OperacionNoPermitidaError):
            self.gestor.procesar_reserva(20)

    def test_cancelar_procesada_prohibido(self):
        self.gestor.crear_reserva(20, 1, 10, 2)
        self.gestor.confirmar_reserva(20)
        self.gestor.procesar_reserva(20)
        with self.assertRaises(OperacionNoPermitidaError):
            self.gestor.cancelar_reserva(20)

    def test_estado_invalido_no_confirmar(self):
        self.gestor.crear_reserva(20, 1, 10, 2)
        self.gestor.cambiar_disponibilidad(10, False)
        with self.assertRaises(ServicioNoDisponibleError):
            self.gestor.confirmar_reserva(20)

    def test_lista_no_modificable(self):
        with self.assertRaises(AttributeError):
            self.gestor.clientes.append(Cliente(2, "Pepe Díaz", "pepe@ejemplo.com", "3001234444"))

    def test_logging_errores(self):
        with self.assertRaises(DatoInvalidoError):
            self.gestor.crear_reserva(20, 1, 10, -2)
        from software_fj.registros import LOGGER
        for controlador in LOGGER.handlers:
            controlador.flush()
        texto = self.archivo_log.read_text(encoding="utf-8")
        self.assertIn("ERROR", texto)
        self.assertIn("crear_reserva", texto)
        self.assertNotIn("ana@ejemplo.com", texto)

    def test_estado_solo_lectura(self):
        reserva = self.gestor.crear_reserva(20, 1, 10, 2)
        with self.assertRaises(AttributeError):
            reserva.estado = EstadoReserva.CONFIRMADA

    def test_manejo_parametros_faltantes(self):
        # El decorador convierte TypeError en una excepción controlada.
        with self.assertRaises(ErrorSoftwareFJ) as captura:
            self.gestor.registrar_cliente(2, "Carla López", "carla@ejemplo.com")
        self.assertIsInstance(captura.exception.__cause__, TypeError)


if __name__ == "__main__":
    unittest.main(verbosity=2)
