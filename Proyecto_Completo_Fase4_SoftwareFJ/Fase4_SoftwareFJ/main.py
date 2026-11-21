"""Ejecuta una simulación secuencial de operaciones exitosas y fallidas.

Uso: python main.py
No requiere instalar librerías adicionales.
"""

from pathlib import Path

from software_fj.errores import ErrorSoftwareFJ
from software_fj.gestor import GestorSoftwareFJ
from software_fj.registros import configurar_logs, LOGGER


def realizar(numero, descripcion, accion, debe_fallar=False):
    """Aísla los errores de cada caso para que la ejecución continúe."""
    print(f"{numero:02d}. {descripcion}")
    try:
        resultado = accion()
    except ErrorSoftwareFJ as error:
        # Las excepciones controladas ya se han registrado en el gestor.
        correcto = debe_fallar
        print(f"    {'OK (error controlado)' if correcto else 'FALLO'}: {error}")
        return correcto
    except Exception as error:
        # Red de seguridad para fallos imprevistos: no oculta el traceback del log.
        LOGGER.exception("Error inesperado en operación de prueba %s", numero)
        print(f"    FALLO inesperado: {type(error).__name__}")
        return False
    else:
        correcto = not debe_fallar
        # Los objetos se presentan mediante su descripción, no su dirección de memoria.
        texto = resultado.describir() if hasattr(resultado, "describir") else resultado
        resumen = f" -> {texto}" if resultado is not None else ""
        print(f"    {'OK' if correcto else 'FALLO: se esperaba un error'}{resumen}")
        return correcto
    finally:
        print()  # La siguiente operación siempre comienza en una línea nueva.


def iniciar_simulacion():
    ruta_log = configurar_logs()
    gestor = GestorSoftwareFJ()
    casos = [
        ("Registrar cliente válido", lambda: gestor.registrar_cliente(101, "Ana Valdez", "ana@correo.com", "3001234567"), False),
        ("Rechazar correo inválido", lambda: gestor.registrar_cliente(102, "Pedro Mora", "correo_invalido", "3101234567"), True),
        ("Registrar segundo cliente", lambda: gestor.registrar_cliente(102, "Sergio Ríos", "sergio@correo.com", "3111234567"), False),
        ("Rechazar cliente duplicado", lambda: gestor.registrar_cliente(101, "Luis Gil", "luis@correo.com", "3121234567"), True),
        ("Crear servicio de sala", lambda: gestor.registrar_sala(201, "Sala de reuniones", 50000, 12, "Sede principal"), False),
        ("Rechazar tarifa negativa", lambda: gestor.registrar_sala(205, "Sala defectuosa", -1000, 10, "Sede principal"), True),
        ("Crear alquiler de equipo", lambda: gestor.registrar_equipo(202, "Portátil empresarial", 25000, "Computador"), False),
        ("Crear asesoría", lambda: gestor.registrar_asesoria(203, "Asesoría de redes", 80000, "Redes"), False),
        ("Crear servicio no disponible", lambda: gestor.registrar_equipo(204, "Proyector", 15000, "Proyector", False), False),
        ("Crear reserva válida", lambda: gestor.crear_reserva(301, 101, 201, 2).describir(), False),
        ("Confirmar reserva", lambda: gestor.confirmar_reserva(301).describir(), False),
        ("Procesar con impuesto y descuento", lambda: gestor.procesar_reserva(301, impuesto=19, descuento=10), False),
        ("Rechazar servicio no disponible", lambda: gestor.crear_reserva(302, 102, 204, 2), True),
        ("Rechazar duración cero", lambda: gestor.crear_reserva(303, 102, 202, 0), True),
        ("Crear otra reserva", lambda: gestor.crear_reserva(304, 102, 202, 3).describir(), False),
        ("Cancelar una reserva", lambda: gestor.cancelar_reserva(304).describir(), False),
        ("Impedir procesar reserva cancelada", lambda: gestor.procesar_reserva(304), True),
        ("Reservar asesoría", lambda: gestor.crear_reserva(305, 101, 203, 1).describir(), False),
        ("Confirmar asesoría", lambda: gestor.confirmar_reserva(305).describir(), False),
        ("Procesar asesoría", lambda: gestor.procesar_reserva(305), False),
        ("Rechazar teléfono con letras", lambda: gestor.registrar_cliente(103, "María Díaz", "maria@correo.com", "numero"), True),
        ("Rechazar sala sin capacidad", lambda: gestor.registrar_sala(206, "Sala pequeña", 5000, 0, "Piso 2"), True),
        ("Rechazar cliente inexistente", lambda: gestor.crear_reserva(306, 999, 202, 1), True),
        ("Crear reserva para revisar descuentos", lambda: gestor.crear_reserva(307, 102, 202, 2).describir(), False),
        ("Confirmar nueva reserva", lambda: gestor.confirmar_reserva(307).describir(), False),
        ("Rechazar descuento mayor al 100%", lambda: gestor.procesar_reserva(307, descuento=125), True),
        ("Recuperarse y procesar correctamente", lambda: gestor.procesar_reserva(307, descuento=10), False),
    ]
    aciertos = 0
    for numero, (descripcion, accion, debe_fallar) in enumerate(casos, start=1):
        aciertos += realizar(numero, descripcion, accion, debe_fallar)
    print(f"RESULTADO: {aciertos}/{len(casos)} operaciones cumplieron el resultado esperado.")
    print(f"REGISTROS: {len(gestor.clientes)} clientes, {len(gestor.servicios)} servicios, {len(gestor.reservas)} reservas.")
    print(f"LOG: {ruta_log.relative_to(Path(__file__).resolve().parent)}")
    return aciertos == len(casos)


if __name__ == "__main__":
    raise SystemExit(0 if iniciar_simulacion() else 1)
