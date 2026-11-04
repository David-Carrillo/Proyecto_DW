"""Parte pública: registrar y modificar solicitud, descargar comprobante."""
from io import BytesIO

from flask import abort, render_template, request, send_file
from flask_login import current_user

from app.controllers.base import Controlador
from app.services import ComprobantePDF, SolicitudService


class PublicoController(Controlador):
    nombre = "publico"

    def __init__(self):
        self.servicio = SolicitudService()
        super().__init__()

    def registrar_rutas(self):
        self.ruta("/", self.registrar)
        self.ruta("/modificar", self.modificar)
        self.ruta("/comprobante/<int:id_>", self.comprobante)

    def registrar(self):
        return render_template("publico/solicitud.html", modo="registrar")

    def modificar(self):
        return render_template("publico/solicitud.html", modo="modificar")

    def comprobante(self, id_):
        solicitud = self.servicio.obtener(id_) or abort(404)
        # El público solo puede ver su comprobante si conoce la CURP
        curp = request.args.get("curp", "").strip().upper()
        if not current_user.is_authenticated and curp != solicitud.curp:
            abort(403)
        pdf = ComprobantePDF(solicitud).generar()
        return send_file(BytesIO(pdf), mimetype="application/pdf",
                         as_attachment=request.args.get("descargar") == "1",
                         download_name=f"comprobante_{solicitud.folio}.pdf")
