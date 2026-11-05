"""Parte privada: dashboard y administración de solicitudes."""
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.controllers.base import Controlador
from app.models import Asunto, Bitacora, Municipio, Nivel, Solicitud
from app.services import SolicitudService


class AdminController(Controlador):
    nombre = "admin"
    prefijo = "/admin"

    def __init__(self):
        self.servicio = SolicitudService()
        super().__init__()

    def registrar_rutas(self):
        self.ruta("/", self.inicio)
        self.ruta("/dashboard", self.dashboard)
        self.ruta("/solicitudes", self.lista)
        self.ruta("/solicitudes/nueva", self.nueva, methods=["GET", "POST"])
        self.ruta("/solicitudes/<int:id_>/editar", self.editar, methods=["GET", "POST"])
        self.ruta("/solicitudes/<int:id_>/estatus", self.estatus, methods=["POST"])
        self.ruta("/solicitudes/<int:id_>/eliminar", self.eliminar, methods=["POST"])

    @staticmethod
    def _catalogos():
        return dict(niveles=Nivel.ordenados(True), municipios=Municipio.ordenados(True),
                    asuntos=Asunto.ordenados(True))

    @login_required
    def inicio(self):
        return redirect(url_for("admin.dashboard"))

    @login_required
    def dashboard(self):
        return render_template("admin/dashboard.html",
                               municipios=Municipio.ordenados(),
                               bitacora=Bitacora.recientes(8))

    @login_required
    def lista(self):
        q = request.args.get("q", "").strip()
        estatus = request.args.get("estatus", "")
        municipio_id = request.args.get("municipio_id", type=int)
        solicitudes = self.servicio.buscar(q, estatus, municipio_id)
        return render_template("admin/solicitudes.html", solicitudes=solicitudes, q=q,
                               estatus=estatus, municipio_id=municipio_id,
                               municipios=Municipio.ordenados())

    @login_required
    def nueva(self):
        datos, errores = {}, {}
        if request.method == "POST":
            datos = request.form.to_dict()
            resultado = self.servicio.registrar(datos)
            if resultado.ok:
                s = resultado.solicitud
                flash(f"Solicitud registrada: turno {s.turno} en {s.municipio.nombre}.", "ok")
                return redirect(url_for("admin.lista"))
            errores = resultado.errores
        return render_template("admin/solicitud_form.html", solicitud=None, datos=datos,
                               errores=errores, **self._catalogos())

    @login_required
    def editar(self, id_):
        solicitud = self.servicio.obtener(id_) or abort(404)
        datos, errores = solicitud.to_dict(), {}
        if request.method == "POST":
            datos = request.form.to_dict()
            resultado = self.servicio.actualizar(solicitud, datos, datos.get("estatus"))
            if resultado.ok:
                aviso = f" Nuevo turno: {solicitud.turno}." if resultado.turno_cambiado else ""
                flash(f"Solicitud {solicitud.folio} actualizada.{aviso}", "ok")
                return redirect(url_for("admin.lista"))
            errores = resultado.errores
        return render_template("admin/solicitud_form.html", solicitud=solicitud, datos=datos,
                               errores=errores, estatus_opciones=Solicitud.ESTATUS,
                               **self._catalogos())

    @login_required
    def estatus(self, id_):
        solicitud = self.servicio.obtener(id_) or abort(404)
        nuevo = request.form.get("estatus") or (
            Solicitud.PENDIENTE if solicitud.resuelta else Solicitud.RESUELTO)
        self.servicio.cambiar_estatus(solicitud, nuevo)
        flash(f"{solicitud.folio} marcada como {solicitud.estatus}.", "ok")
        return redirect(request.referrer or url_for("admin.lista"))

    @login_required
    def eliminar(self, id_):
        solicitud = self.servicio.obtener(id_) or abort(404)
        folio = solicitud.folio
        self.servicio.eliminar(solicitud)
        flash(f"Solicitud {folio} eliminada.", "ok")
        return redirect(url_for("admin.lista"))
