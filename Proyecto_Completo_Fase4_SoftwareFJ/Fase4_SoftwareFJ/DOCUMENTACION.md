# Documentación técnica y guía de comprensión del código

## Objetivo

Demostrar los requisitos del **Anexo 3 de la Fase 4 del curso Programación (213023)**, mediante un sistema en memoria que administre clientes, servicios y reservas, registre los errores y continúe ejecutándose ante entradas incorrectas.

## 1. Flujo principal (`main.py`)

1. `iniciar_simulacion()` configura el registro de errores, crea un `GestorSoftwareFJ` y define las operaciones que van a ejecutarse.
2. Las operaciones se guardan como tuplas con una descripción, una función y un indicador que dice si el caso **debe fallar** para considerarse correcto.
3. `realizar()` ejecuta cada función dentro de un bloque `try`.
4. `except ErrorSoftwareFJ` interpreta las validaciones y operaciones inválidas sin detener el bucle.
5. `except Exception` evita que un error inesperado detenga toda la simulación y lo registra con detalle técnico.
6. `else` muestra el resultado de las operaciones exitosas.
7. `finally` separa visualmente los casos, independientemente del resultado.
8. Al terminar se imprime la cantidad de resultados que coincidieron con lo esperado. Si alguno no coincide, el programa termina con un código de salida distinto de cero.

## 2. Entidades abstractas y clientes (`entidades.py`)

- `Entidad` utiliza `ABC` y `@abstractmethod`, por lo que no se puede crear directamente. Valida que cada identificador sea un entero positivo.
- `Cliente` hereda de `Entidad` y completa el método `describir`.
- Los atributos `__nombre`, `__correo` y `__telefono` se encapsulan; sus propiedades permiten lectura, pero no modificación directa.
- La descripción pública no muestra correo ni teléfono, lo que evita incluirlos en mensajes de salida y registros comunes.

## 3. Servicios polimórficos (`servicios.py`)

- `Servicio` también es abstracta: toda especialización debe implementar `validar_parametros`, `calcular_costo` y `describir`.
- `ServicioSala` valida entre 1 y 12 horas y agrega una tarifa fija de limpieza de 10.000 COP.
- `AlquilerEquipo` valida entre 1 y 72 horas, sin cargo adicional.
- `AsesoriaEspecializada` valida entre 1 y 8 horas, sin cargo adicional.
- El programa puede llamar `calcular_costo` en cualquiera de esas clases usando la misma interfaz. Eso muestra **polimorfismo**.
- `calcular_costo(duracion, impuesto=0, descuento=0)` admite llamadas con uno, dos o tres parámetros de negocio. Esto representa **variantes mediante parámetros opcionales**, el mecanismo sugerido en el enunciado, y no una sobrecarga por firmas como en otros lenguajes.

## 4. Reservas (`reservas.py`)

- `EstadoReserva` usa una enumeración de estados válidos.
- El constructor exige una instancia de `Cliente`, una instancia de `Servicio` y una duración válida.
- `confirmar()` exige que la reserva esté pendiente y el servicio disponible.
- `cancelar()` solo permite cancelar reservas pendientes o confirmadas.
- `procesar()` exige confirmación y ejecuta el cálculo del servicio; solo cambia a `PROCESADA` si el cálculo terminó sin errores.
- Si aparece un error de porcentaje o de duración, la reserva conserva el estado previo; esa recuperación permite corregir y volver a intentar.

## 5. Control de datos y dinero (`validaciones.py`)

- `entero_positivo()` no acepta números negativos, cero ni valores booleanos usados como enteros.
- `texto_no_vacio()` rechaza nombres y campos vacíos.
- `correo_valido()` comprueba una estructura básica de correo; no intenta verificar cuentas reales por internet.
- `telefono_valido()` exige entre 7 y 15 dígitos ASCII.
- `dinero_positivo()` utiliza `Decimal` para evitar errores típicos de representación de dinero y rechaza `NaN`, valores infinitos o negativos.
- `porcentaje()` exige un valor entre 0 y 100, inclusive.
- `valor_final()` aplica primero descuento y después impuesto; redondea a dos decimales mediante `ROUND_HALF_UP`.

## 6. Excepciones (`errores.py`)

- `ErrorSoftwareFJ` es la clase base para los errores controlados.
- `DatoInvalidoError` identifica datos que no cumplen reglas de negocio.
- `RegistroDuplicadoError` avisa si se repite un ID o un correo.
- `RegistroNoEncontradoError` avisa si no existe el objeto buscado.
- `ServicioNoDisponibleError` avisa que no se puede utilizar un servicio inactivo.
- `OperacionNoPermitidaError` impide cambios inválidos de estado.

## 7. Gestión en listas (`gestor.py`)

- `GestorSoftwareFJ` almacena objetos en tres listas privadas: clientes, servicios y reservas.
- Las propiedades públicas devuelven tuplas para impedir cambios directos mediante `.append()`.
- `registrar_cliente` valida registros y duplicaciones de ID y correo.
- `registrar_sala`, `registrar_equipo` y `registrar_asesoria` crean las tres categorías de servicio.
- `crear_reserva` busca el cliente y servicio mediante sus ID, verifica disponibilidad y valida duración.
- `confirmar_reserva`, `cancelar_reserva` y `procesar_reserva` llaman los métodos del objeto `Reserva`.
- El método privado `__buscar()` transforma `StopIteration` en una excepción de negocio usando `raise ... from ...`, preservando la causa original del fallo.
- Cada operación pública usa el decorador `@registrar_operacion` para centralizar el registro de resultados y errores.

## 8. Registro de eventos (`registros.py`)

- `configurar_logs()` prepara el archivo `logs/eventos.log`, crea su carpeta si falta y establece formato con fecha, nivel y mensaje.
- `registrar_operacion()` ejecuta la función envuelta dentro de `try/except/else/finally`.
- Si ocurre un error propio, lo escribe como `ERROR` y lo vuelve a lanzar para que la capa superior decida cómo mostrarlo.
- Si ocurre un error básico no previsto (`TypeError`, `ValueError` o `ArithmeticError`), registra el detalle y lo encadena dentro de `ErrorSoftwareFJ` para mantener una interfaz estable.
- Si hay éxito, guarda un evento `INFO`.
- Los mensajes evitan incluir nombres, teléfonos y correos de clientes.

## 9. Evidencias de funcionamiento

- `evidencias/simulacion.txt`: salida capturada de la ejecución real de `python main.py`. Contiene **27 operaciones** con resultado correcto, incluyendo errores esperados y recuperación.
- `evidencias/pruebas_unitarias.txt`: resultado real de `python -m unittest discover -s pruebas -v`, con **32 pruebas correctas**.
- `logs/eventos.log`: registro real producido durante la simulación.

## 10. Aspectos por personalizar antes de entregar

Los valores de negocio (tarifas, topes de horas, cargo fijo) fueron elegidos para realizar una simulación consistente. El anexo no indica cifras fijas. El enlace real de GitHub y los datos de portada se deben completar en `datos_informe.json` para regenerar el PDF. La guía considera la actividad colaborativa, por lo que deben respetarse las instrucciones formales del curso sin atribuir participación a personas que no hayan participado.
