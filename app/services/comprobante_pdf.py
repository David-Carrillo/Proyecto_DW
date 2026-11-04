"""Genera el comprobante PDF de una solicitud, con código QR de la CURP."""
from datetime import datetime
from io import BytesIO

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


class ComprobantePDF:
    AZUL = colors.HexColor("#1f3b63")
    GRIS = colors.HexColor("#5b6472")
    LINEA = colors.HexColor("#d5dae1")
    FONDO = colors.HexColor("#f2f5f9")

    def __init__(self, solicitud):
        self.s = solicitud
        self.ancho, self.alto = letter

    def generar(self) -> bytes:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setTitle(f"Comprobante {self.s.folio}")
        c.setAuthor("Ticket de Turno")
        self._encabezado(c)
        self._turno(c)
        self._qr(c)
        self._datos(c)
        self._pie(c)
        c.showPage()
        c.save()
        return buffer.getvalue()

    # ---- secciones -----------------------------------------------------
    def _encabezado(self, c):
        c.setFillColor(self.AZUL)
        c.rect(0, self.alto - 3 * cm, self.ancho, 3 * cm, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(2 * cm, self.alto - 1.75 * cm, "Ticket de Turno")
        c.setFont("Helvetica", 11)
        c.drawString(2 * cm, self.alto - 2.45 * cm, "Comprobante de solicitud de atención")
        c.setFont("Helvetica", 9)
        c.drawRightString(self.ancho - 2 * cm, self.alto - 1.75 * cm, f"Folio: {self.s.folio}")
        c.drawRightString(self.ancho - 2 * cm, self.alto - 2.45 * cm,
                          f"Fecha: {self.s.creado:%d/%m/%Y %H:%M}")

    def _turno(self, c):
        y = self.alto - 9.2 * cm
        c.setFillColor(self.FONDO)
        c.setStrokeColor(self.LINEA)
        c.roundRect(2 * cm, y, 11 * cm, 5.2 * cm, 8, stroke=1, fill=1)
        c.setFillColor(self.GRIS)
        c.setFont("Helvetica", 11)
        c.drawCentredString(7.5 * cm, y + 4.3 * cm, "SU NÚMERO DE TURNO ES")
        c.setFillColor(self.AZUL)
        c.setFont("Helvetica-Bold", 64)
        c.drawCentredString(7.5 * cm, y + 1.9 * cm, str(self.s.turno))
        c.setFillColor(self.GRIS)
        c.setFont("Helvetica", 11)
        c.drawCentredString(7.5 * cm, y + 0.8 * cm, f"Municipio: {self.s.municipio.nombre}")

    def _qr(self, c):
        tam = 5.2 * cm
        x, y = self.ancho - 2 * cm - tam, self.alto - 9.2 * cm
        widget = QrCodeWidget(self.s.curp)  # el QR contiene la CURP del alumno
        x1, y1, x2, y2 = widget.getBounds()
        dibujo = Drawing(tam, tam, transform=[tam / (x2 - x1), 0, 0, tam / (y2 - y1), 0, 0])
        dibujo.add(widget)
        renderPDF.draw(dibujo, c, x, y)
        c.setFillColor(self.GRIS)
        c.setFont("Helvetica", 8)
        c.drawCentredString(x + tam / 2, y - 0.4 * cm, "CURP del alumno")

    def _datos(self, c):
        filas = [
            ("Datos del alumno", None),
            ("Nombre", self.s.nombre_completo),
            ("CURP", self.s.curp),
            ("Nivel", self.s.nivel.nombre),
            ("Municipio", self.s.municipio.nombre),
            ("Datos de la solicitud", None),
            ("Asunto", self.s.asunto.nombre),
            ("Realiza el trámite", self.s.tramitante),
            ("Celular", self.s.celular),
            ("Teléfono", self.s.telefono or "—"),
            ("Correo", self.s.correo),
            ("Estatus", self.s.estatus),
        ]
        y = self.alto - 11 * cm
        for etiqueta, valor in filas:
            if valor is None:  # subtítulo de sección
                y -= 0.3 * cm
                c.setFillColor(self.AZUL)
                c.setFont("Helvetica-Bold", 12)
                c.drawString(2 * cm, y, etiqueta)
                c.setStrokeColor(self.AZUL)
                c.line(2 * cm, y - 0.2 * cm, self.ancho - 2 * cm, y - 0.2 * cm)
                y -= 0.9 * cm
                continue
            c.setFillColor(self.GRIS)
            c.setFont("Helvetica", 10)
            c.drawString(2.3 * cm, y, etiqueta)
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(7 * cm, y, str(valor))
            c.setStrokeColor(self.LINEA)
            c.line(2 * cm, y - 0.25 * cm, self.ancho - 2 * cm, y - 0.25 * cm)
            y -= 0.75 * cm

    def _pie(self, c):
        c.setFillColor(self.GRIS)
        c.setFont("Helvetica", 9)
        textos = [
            "Presente este comprobante el día de su atención junto con una identificación oficial.",
            f"Para modificar su solicitud use su CURP y su número de turno ({self.s.turno}) en la opción «Modificar solicitud».",
            f"Generado el {datetime.now():%d/%m/%Y a las %H:%M}.",
        ]
        y = 2.6 * cm
        for t in textos:
            c.drawCentredString(self.ancho / 2, y, t)
            y -= 0.5 * cm
