# Software FJ - Fase 4, Programación UNAD 213023

**Sistema integral de gestión de clientes, servicios y reservas**, desarrollado en Python 3.10+ sin bases de datos y sin dependencias de terceros.

## Archivos

```text
Fase4_SoftwareFJ/
├── main.py                    # Simulación de operaciones (27 casos)
├── datos_informe.json        # Datos personalizables del informe
├── generar_informe.py        # Regeneración opcional del PDF
├── DOCUMENTACION.md          # Explicación detallada de los módulos
├── software_fj/
│   ├── __init__.py            # Interfaz del paquete
│   ├── entidades.py           # Entidad abstracta y Cliente
│   ├── servicios.py           # Servicio abstracto y tres especializaciones
│   ├── reservas.py            # Reserva, estados y transiciones
│   ├── gestor.py              # Listas de objetos y operaciones del sistema
│   ├── errores.py             # Excepciones personalizadas
│   ├── validaciones.py        # Validaciones estrictas y cálculo monetario
│   └── registros.py           # Logs y decorador de errores
├── pruebas/
│   └── test_sistema.py        # Pruebas automatizadas con unittest
├── logs/
│   └── eventos.log            # Archivo que se genera al ejecutar la demo
├── evidencias/
│   ├── simulacion.txt         # Salida real de la simulación
│   └── pruebas_unitarias.txt  # Salida real de las pruebas
└── Informe_Fase4_SoftwareFJ.pdf  # Portada, introducción, enlace, conclusiones y referencias
```

## Ejecución

Abrir una terminal en esta carpeta:

```bash
python main.py
```

Ejecutar las pruebas:

```bash
python -m unittest discover -s pruebas -v
```

En algunos sistemas el comando se llama `python3` en lugar de `python`.

## Características

- La clase abstracta `Entidad` define el ID y la descripción.
- `Cliente` encapsula nombre, correo y teléfono mediante atributos privados y propiedades de lectura.
- La clase abstracta `Servicio` exige describir, validar y calcular costos.
- `ServicioSala`, `AlquilerEquipo` y `AsesoriaEspecializada` implementan y sobrescriben esos métodos, demostrando polimorfismo.
- `Reserva` controla las transiciones `pendiente -> confirmada -> procesada`, o `pendiente/confirmada -> cancelada`.
- `GestorSoftwareFJ` mantiene clientes, servicios y reservas en **listas privadas**, expuestas como tuplas de consulta.
- Las operaciones inválidas se aíslan mediante excepciones propias y bloques `try/except`, `try/except/else/finally`. La búsqueda de registros demuestra encadenamiento con `raise ... from ...`.
- Las variantes de costos emplean **parámetros opcionales** (`impuesto` y `descuento`) como aproximación a la sobrecarga de métodos en Python; Python no hace sobrecarga por firmas como Java o C++.
- Cada operación registrada por el gestor genera un evento `INFO` si es exitosa o `ERROR` si falla. Se escriben mensajes de validación sin nombres, teléfonos ni correos de clientes.
- Toda la información del negocio permanece en memoria mientras la aplicación está abierta. **No se usan bases de datos ni archivos de persistencia de clientes/reservas**: los archivos se reservan para logs y evidencias de pruebas.

## Reglas de negocio adoptadas para la simulación

Estos valores son **decisiones de implementación**, no tarifas ni límites especificados por la guía:

| Tipo de servicio | Cálculo base | Duración permitida |
|---|---|---|
| Sala | tarifa/hora × horas + COP 10.000 de limpieza | 1 a 12 horas |
| Equipo | tarifa/hora × horas | 1 a 72 horas |
| Asesoría | tarifa/hora × horas | 1 a 8 horas |

Cálculo de descuento e impuesto (porcentajes 0 a 100):

`total = (subtotal × (1 - descuento / 100)) × (1 + impuesto / 100)`

Los valores monetarios se manejan con `Decimal`, redondeados a dos decimales.

## Guía para publicar en GitHub

1. Crear un repositorio vacío nuevo en GitHub con nombre `fase4-software-fj`.
2. Desde esta carpeta ejecutar `git init`, `git add .` y `git commit -m "Fase 4: sistema Software FJ"`.
3. Elegir la rama `main` usando `git branch -M main`.
4. Configurar el repositorio: `git remote add origin URL_REAL_DEL_REPOSITORIO` (sustituye el texto por la dirección real).
5. Subir el código: `git push -u origin main`.
6. Abrir `datos_informe.json` y completar `estudiante`, `grupo`, `tutor` y `repositorio_github`.
7. Para actualizar el PDF ejecutar `python generar_informe.py` (requiere `pip install reportlab`; esto **solo aplica a la generación del informe**, no al programa).
8. Comprobar que el PDF actualizado incluya la dirección real antes de entregar.

> **Importante:** la guía de la UNAD denomina la actividad como colaborativa. El proyecto está organizado para que una sola persona pueda implementarlo, pero ello no modifica los lineamientos formales del curso; no se deben atribuir aportes a compañeros que no hayan participado.

## Referencias de la actividad

- UNAD. *Guía de aprendizaje para el desarrollo del componente práctico del curso Programación 213023*.
- UNAD. *Anexo 3 - Problema a desarrollar Fase 4*.
- Python Software Foundation. *El tutorial de Python: errores y excepciones*. https://docs.python.org/es/3.12/tutorial/errors.html
