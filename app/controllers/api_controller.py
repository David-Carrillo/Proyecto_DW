"""API REST (JSON). Cada recurso es una clase MethodView.

Recurso                                   Métodos    Acceso
/api/catalogos                            GET        público
/api/solicitudes                          GET        admin   (lista / búsqueda ?q=)
/api/solicitudes                          POST       público (registrar)
/api/solicitudes/<id>                     GET        admin
/api/solicitudes/<id>                     PUT        público con CURP+turno / admin
/api/solicitudes/<id>                     DELETE     admin
/api/solicitudes/<id>/estatus             PATCH      admin
/api/solicitudes/consulta?curp=&turno=    GET        público (para modificar)
/api/estadisticas?municipio_id=           GET        admin   (dashboard)
"""
from functools import wraps

from flask import jsonify, request, url_for
from flask.views import MethodView
from flask_login import current_user

from app.controllers.base import Controlador
from app.models import Asunto, Municipio, Nivel
from app.services import EstadisticasService, SolicitudService


def solo_admin(funcion):
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify(ok=False, error="Requiere iniciar sesión como administrador."), 401
        return funcion(*args, **kwargs)
    return envoltura


class RecursoAPI(MethodView):
    """Clase padre de los recursos REST con utilidades comunes."""

    def __init__(self):
        self.servicio = SolicitudService()

    @staticmethod
    def json_entrada() -> dict:
        return request.get_json(silent=True) or {}

    @staticmethod
    def no_encontrado():
        return jsonify(ok=False, error="Solicitud no encontrada."), 404

    @staticmethod
    def respuesta_solicitud(resultado, codigo=200):
        if not resultado.ok:
            return jsonify(ok=False, errores=resultado.errores), 400
        s = resultado.solicitud
        return jsonify(ok=True, turno_cambiado=resultado.turno_cambiado, solicitud=s.to_dict(),
                       comprobante=url_for("publico.comprobante", id_=s.id, curp=s.curp)), codigo


class CatalogosAPI(MethodView):
    def get(self):
        def lista(modelo):
            return [{"id": r.id, "nombre": r.nombre} for r in modelo.ordenados(solo_activos=True)]
        return jsonify(niveles=lista(Nivel), municipios=lista(Municipio), asuntos=lista(Asunto))


class SolicitudesAPI(RecursoAPI):

    @solo_admin
    def get(self, id_=None):
        if id_ is None:
            encontradas = self.servicio.buscar(request.args.get("q", ""),
                                               request.args.get("estatus", ""),
                                               request.args.get("municipio_id", type=int))
            return jsonify(total=len(encontradas), solicitudes=[s.to_dict() for s in encontradas])
        solicitud = self.servicio.obtener(id_)
        return jsonify(solicitud.to_dict()) if solicitud else self.no_encontrado()

    def post(self):
        return self.respuesta_solicitud(self.servicio.registrar(self.json_entrada()), 201)

    def put(self, id_):
        solicitud = self.servicio.obtener(id_)
        if not solicitud:
            return self.no_encontrado()
        datos = self.json_entrada()
        if not current_user.is_authenticated:
            # El público debe comprobar que es su solicitud: CURP + turno originales
            original = self.servicio.por_curp_y_turno(datos.get("auth_curp"), datos.get("auth_turno"))
            if not original or original.id != solicitud.id:
                return jsonify(ok=False, error="La CURP y el turno no coinciden."), 403
            estatus = None
        else:
            estatus = datos.get("estatus")
        return self.respuesta_solicitud(self.servicio.actualizar(solicitud, datos, estatus))

    @solo_admin
    def delete(self, id_):
        solicitud = self.servicio.obtener(id_)
        if not solicitud:
            return self.no_encontrado()
        self.servicio.eliminar(solicitud)
        return jsonify(ok=True)


class ConsultaAPI(RecursoAPI):
    def get(self):
        solicitud = self.servicio.por_curp_y_turno(request.args.get("curp"), request.args.get("turno"))
        if not solicitud:
            return jsonify(ok=False, error="No existe una solicitud con esa CURP y ese turno."), 404
        return jsonify(ok=True, solicitud=solicitud.to_dict())


class EstatusAPI(RecursoAPI):
    @solo_admin
    def patch(self, id_):
        solicitud = self.servicio.obtener(id_)
        if not solicitud:
            return self.no_encontrado()
        resultado = self.servicio.cambiar_estatus(solicitud, self.json_entrada().get("estatus"))
        return self.respuesta_solicitud(resultado)


class EstadisticasAPI(MethodView):
    def __init__(self):
        self.servicio = EstadisticasService()

    @solo_admin
    def get(self):
        municipio_id = request.args.get("municipio_id", type=int)
        return jsonify(resumen=self.servicio.resumen(municipio_id),
                       por_municipio=self.servicio.por_municipio(municipio_id))


class ApiController(Controlador):
    nombre = "api"
    prefijo = "/api"

    def registrar_rutas(self):
        solicitudes = SolicitudesAPI.as_view("solicitudes")
        self.ruta("/catalogos", CatalogosAPI.as_view("catalogos"))
        self.ruta("/solicitudes", solicitudes, methods=["GET", "POST"])
        self.ruta("/solicitudes/<int:id_>", solicitudes, methods=["GET", "PUT", "DELETE"])
        self.ruta("/solicitudes/consulta", ConsultaAPI.as_view("consulta"))
        self.ruta("/solicitudes/<int:id_>/estatus", EstatusAPI.as_view("estatus"), methods=["PATCH"])
        self.ruta("/estadisticas", EstadisticasAPI.as_view("estadisticas"))
