"""Genera el informe PDF de la Fase 4 a partir de datos_informe.json.

Requiere reportlab SOLO para regenerar el PDF; el sistema de reservas
(main.py y pruebas) no lo necesita.
"""

import json
from html import escape
from pathlib import Path

import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether,
)

BASE = Path(__file__).resolve().parent
SALIDA = BASE / "Informe_Fase4_SoftwareFJ.pdf"
DATOS = json.loads((BASE / "datos_informe.json").read_text(encoding="utf-8"))

# Preferimos DejaVu en Linux; ReportLab incluye Vera como respaldo para Windows.
fuentes_linux = Path("/usr/share/fonts/truetype/dejavu")
if (fuentes_linux / "DejaVuSans.ttf").exists():
    fuente_normal = fuentes_linux / "DejaVuSans.ttf"
    fuente_negrita = fuentes_linux / "DejaVuSans-Bold.ttf"
else:
    carpeta_reportlab = Path(reportlab.__file__).resolve().parent / "fonts"
    fuente_normal = carpeta_reportlab / "Vera.ttf"
    fuente_negrita = carpeta_reportlab / "VeraBd.ttf"
pdfmetrics.registerFont(TTFont("DejaVu", str(fuente_normal)))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(fuente_negrita)))
pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold")

NAVY = colors.HexColor("#1B314D")
LIGHT = colors.HexColor("#F2F5F8")
CYAN = colors.HexColor("#287DA1")
GRAY = colors.HexColor("#65758A")

ESTILOS = {
    "portada_centro": ParagraphStyle(
        "portada_centro", fontName="DejaVu-Bold", fontSize=13, leading=20,
        alignment=TA_CENTER, textColor=NAVY, spaceAfter=12),
    "portada_titulo": ParagraphStyle(
        "portada_titulo", fontName="DejaVu-Bold", fontSize=17, leading=25,
        alignment=TA_CENTER, textColor=NAVY, spaceAfter=14),
    "portada_sub": ParagraphStyle(
        "portada_sub", fontName="DejaVu", fontSize=11.2, leading=18,
        alignment=TA_CENTER, textColor=NAVY),
    "titulo": ParagraphStyle(
        "titulo", fontName="DejaVu-Bold", fontSize=12, leading=17,
        textColor=NAVY, spaceAfter=10, spaceBefore=15),
    "cuerpo": ParagraphStyle(
        "cuerpo", fontName="DejaVu", fontSize=9.8, leading=16,
        alignment=TA_JUSTIFY, spaceAfter=10),
    "item": ParagraphStyle(
        "item", fontName="DejaVu", fontSize=9.4, leading=15,
        leftIndent=18, firstLineIndent=-10, spaceAfter=7),
    "ref": ParagraphStyle(
        "ref", fontName="DejaVu", fontSize=9.2, leading=15,
        leftIndent=21, firstLineIndent=-21, spaceAfter=10),
    "aviso": ParagraphStyle(
        "aviso", fontName="DejaVu", fontSize=9, leading=14,
        textColor=NAVY, spaceAfter=8),
    "tabla": ParagraphStyle(
        "tabla", fontName="DejaVu", fontSize=8.7, leading=13),
}


def p(texto, estilo="cuerpo"):
    return Paragraph(texto, ESTILOS[estilo])


def pie(canvas, doc):
    canvas.saveState()
    ancho, alto = letter
    if doc.page > 1:
        canvas.setStrokeColor(colors.HexColor("#DCE4EB"))
        canvas.line(2.4 * cm, alto - 2.1 * cm, ancho - 2.4 * cm, alto - 2.1 * cm)
        canvas.setFont("DejaVu", 8)
        canvas.setFillColor(GRAY)
        canvas.drawString(2.4 * cm, alto - 1.85 * cm, "UNAD  |  Programación 213023  |  Fase 4")
        canvas.drawRightString(ancho - 2.4 * cm, 1.65 * cm, f"Página {doc.page}")
    canvas.restoreState()


def construir():
    reporte = SimpleDocTemplate(
        str(SALIDA), pagesize=letter,
        topMargin=2.65 * cm, bottomMargin=2.3 * cm,
        leftMargin=2.55 * cm, rightMargin=2.55 * cm,
        title="Fase 4 - Sistema Integral Software FJ",
        author="Trabajo académico de Programación 213023 - UNAD",
    )
    historia = []

    # Portada: los datos no facilitados permanecen visibles como campos pendientes.
    historia.extend([
        Spacer(1, 1.2 * cm),
        p("UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA", "portada_centro"),
        p("Escuela de Ciencias Básicas, Tecnología e Ingeniería (ECBTI)", "portada_sub"),
        p("Ingeniería de Sistemas", "portada_sub"),
        Spacer(1, 2.5 * cm),
        p("FASE 4 - PRÁCTICAS SIMULADAS", "portada_titulo"),
        p("Sistema integral de gestión de clientes, servicios y reservas", "portada_centro"),
        p("Empresa simulada: Software FJ", "portada_sub"),
        Spacer(1, 2.1 * cm),
        p(f"<b>Presentado por:</b> {escape(DATOS['estudiante'])}", "portada_sub"),
        p(f"<b>Grupo:</b> {escape(DATOS['grupo'])}", "portada_sub"),
        p(f"<b>Tutor:</b> {escape(DATOS['tutor'])}", "portada_sub"),
        p("Curso: Programación (213023)", "portada_sub"),
        Spacer(1, 2.2 * cm),
        p("Noviembre de 2026", "portada_sub"),
        PageBreak(),
    ])

    historia.append(p("Introducción", "titulo"))
    historia.append(p(
        "En esta fase desarrollé un programa en Python para una empresa ficticia llamada Software FJ. "
        "La idea es que pueda registrar clientes, ofrecer servicios de salas, alquiler de equipos y "
        "asesorías, y llevar el control de las reservas sin usar una base de datos. Quise que el programa "
        "no se detuviera cuando alguien ingresara información incorrecta, porque ese es uno de los "
        "problemas que más se presentan cuando una aplicación comienza a utilizarse."
    ))
    historia.append(p(
        "Para construirlo organicé el código en clases y módulos que se encargan de tareas diferentes. "
        "Apliqué los principios de abstracción, herencia, encapsulación y polimorfismo; además, incorporé "
        "excepciones personalizadas, validaciones, controles de estados de reserva y un archivo que "
        "registra los eventos y errores. Al final ejecuté simulaciones y pruebas automáticas para "
        "comprobar cómo responde el sistema cuando una operación sale bien o presenta una falla."
    ))

    historia.append(p("Enlace del repositorio de GitHub", "titulo"))
    enlace = DATOS["repositorio_github"].strip()
    if enlace:
        historia.append(p(f"Repositorio del proyecto: <link href='{escape(enlace, quote=True)}' color='#176c9c'>{escape(enlace)}</link>"))
    else:
        historia.append(p(
            "<b>PENDIENTE DE COMPLETAR:</b> todavía no se ha proporcionado una URL real de GitHub. "
            "Una vez publicado el código, se debe actualizar el campo "
            "<b>repositorio_github</b> en el archivo <b>datos_informe.json</b> y generar nuevamente este PDF.",
            "aviso"
        ))

    historia.append(p("Descripción y comprobación del funcionamiento", "titulo"))
    historia.append(p(
        "El sistema está dividido en módulos para clientes, servicios, reservas, validaciones, "
        "excepciones, gestión y registros. La información se conserva en listas durante la ejecución; "
        "los archivos se utilizan solamente para registrar eventos, errores y resultados de verificación."
    ))

    tabla_datos = [
        [p("Componente", "tabla"), p("Función verificada", "tabla")],
        [p("Clientes", "tabla"), p("Registros válidos e inválidos y control de duplicados.", "tabla")],
        [p("Servicios", "tabla"), p("Tres clases especializadas, costos y disponibilidad.", "tabla")],
        [p("Reservas", "tabla"), p("Creación, confirmación, procesamiento y cancelación.", "tabla")],
        [p("Excepciones", "tabla"), p("Errores controlados, encadenamiento y archivo de logs.", "tabla")],
    ]
    t = Table(tabla_datos, colWidths=[3.05 * cm, 10.4 * cm], hAlign="LEFT", repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
        ("TEXTCOLOR", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFBFC")]),
        ("LINEBELOW", (0, 0), (-1, 0), 1, CYAN),
        ("GRID", (0, 1), (-1, -1), 0.25, colors.HexColor("#E1E8EF")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    historia.append(t)
    historia.append(Spacer(1, 0.3 * cm))
    historia.append(p(
        "<b>Resultados verificados:</b> las 27 operaciones de la simulación tuvieron el resultado "
        "esperado y las 32 pruebas de unittest finalizaron correctamente. Las salidas están en "
        "<b>evidencias/</b> y el registro de eventos en <b>logs/eventos.log</b>."
    ))

    historia.append(p("Conclusiones", "titulo"))
    historia.append(p(
        "Con este trabajo comprendí mejor cómo organizar un programa grande en varias clases y cómo "
        "hacer que cada una cumpla una función concreta. La herencia y el polimorfismo me permitieron "
        "trabajar con diferentes tipos de servicios sin repetir toda la lógica del sistema."
    ))
    historia.append(p(
        "La parte más importante fue el manejo de errores. Al probar datos incorrectos, reservas "
        "canceladas, servicios no disponibles y descuentos fuera de rango, pude comprobar que el "
        "programa informa lo sucedido y continúa con las operaciones siguientes. También entendí "
        "por qué es útil guardar un registro de estos eventos para revisar los fallos después."
    ))
    historia.append(p(
        "Finalmente, las pruebas me ayudaron a corregir detalles que no siempre se detectan al "
        "leer el código. Considero que el resultado cumple el propósito de la fase: demostrar el "
        "funcionamiento de una aplicación orientada a objetos y el control de excepciones sin usar "
        "bases de datos."
    ))

    historia.append(p("Referencias bibliográficas", "titulo"))
    historia.append(p(
        "Universidad Nacional Abierta y a Distancia. (s. f.). <i>Guía de aprendizaje para el desarrollo "
        "del componente práctico del curso Programación 213023</i> [Guía de aprendizaje].", "ref"
    ))
    historia.append(p(
        "Universidad Nacional Abierta y a Distancia. (s. f.). <i>Anexo 3: Problema a desarrollar. "
        "Fase 4</i> [Material del curso Programación 213023].", "ref"
    ))
    historia.append(p(
        "Van Rossum, G., &amp; Drake Jr., F. L. (2024). <i>El tutorial de Python: Errores y "
        "excepciones</i>. Python Software Foundation. "
        "https://docs.python.org/es/3.12/tutorial/errors.html", "ref"
    ))
    reporte.build(historia, onFirstPage=pie, onLaterPages=pie)
    print(f"Informe generado: {SALIDA}")


if __name__ == "__main__":
    construir()
