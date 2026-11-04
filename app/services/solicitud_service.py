"""Lógica de negocio de las solicitudes.

Aquí se usan tres patrones de diseño:
- FACTORY   -> SolicitudFactory crea objetos Solicitud ya con su turno.
- SINGLETON -> SolicitudService tiene una sola instancia en la app.
- OBSERVER  -> SolicitudService (sujeto) avisa a sus observadores en cada cambio.
"""
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

from app.database import db
from app.models import Solicitud
from app.patterns import SingletonMeta, Sujeto
from app.services.validador import ValidadorSolicitud


class GestorTurnos:
    """Cada municipio lleva su propio consecutivo: 1, 2, 3 ... n."""

    @staticmethod
    def siguiente(municipio_id: int) -> int:
        ultimo = (db.session.query(func.max(Solicitud.turno))
                  .filter(Solicitud.municipio_id == municipio_id).scalar())
        return (ultimo or 0) + 1


class SolicitudFactory:
    """Factory: centraliza cómo se construye una Solicitud nueva."""

    @staticmethod
    def crear(datos: dict) -> Solicitud:
        solicitud = Solicitud(**datos)
        solicitud.turno = GestorTurnos.siguiente(datos["municipio_id"])
        solicitud.estatus = Solicitud.PENDIENTE
        return solicitud


class ResultadoOperacion:
    """Respuesta uniforme de los métodos del servicio."""

    def __init__(self, solicitud=None, errores=None, turno_cambiado=False):
        self.solicitud = solicitud
        self.errores = errores or {}
        self.turno_cambiado = turno_cambiado

    @property
    def ok(self) -> bool:
        return not self.errores


class SolicitudService(Sujeto, metaclass=SingletonMeta):

    # ---- consultas -----------------------------------------------------
    def obtener(self, id_):
        return Solicitud.obtener(id_)

    def por_curp_y_turno(self, curp: str, turno) -> Solicitud | None:
        try:
            turno = int(turno)
        except (TypeError, ValueError):
            return None
        return (Solicitud.query
                .filter_by(curp=(curp or "").strip().upper(), turno=turno)
                .order_by(Solicitud.creado.desc()).first())

    def buscar(self, texto: str = "", estatus: str = "", municipio_id=None):
        """Busca por CURP o por nombre (alumno o quien hace el trámite)."""
        consulta = Solicitud.query
        for palabra in (texto or "").split():
            patron = f"%{palabra}%"
            consulta = consulta.filter(or_(
                Solicitud.curp.ilike(patron),
                Solicitud.nombre.ilike(patron),
                Solicitud.paterno.ilike(patron),
                Solicitud.materno.ilike(patron),
                Solicitud.tramitante.ilike(patron),
            ))
        if estatus in Solicitud.ESTATUS:
            consulta = consulta.filter(Solicitud.estatus == estatus)
        if municipio_id:
            consulta = consulta.filter(Solicitud.municipio_id == municipio_id)
        return consulta.order_by(Solicitud.creado.desc()).all()

    # ---- operaciones ---------------------------------------------------
    def registrar(self, entrada: dict) -> ResultadoOperacion:
        validador = ValidadorSolicitud()
        if not validador.validar(entrada):
            return ResultadoOperacion(errores=validador.errores)

        for _ in range(3):  # reintenta si dos personas piden turno al mismo tiempo
            solicitud = SolicitudFactory.crear(validador.datos)
            try:
                solicitud.guardar()
                break
            except IntegrityError:
                db.session.rollback()
        else:
            return ResultadoOperacion(errores={"general": "No se pudo asignar el turno, intente de nuevo."})

        self.notificar("registrada", solicitud)
        return ResultadoOperacion(solicitud)

    def actualizar(self, solicitud: Solicitud, entrada: dict, estatus=None) -> ResultadoOperacion:
        validador = ValidadorSolicitud()
        if not validador.validar(entrada):
            return ResultadoOperacion(errores=validador.errores)

        datos = validador.datos
        cambia_municipio = datos["municipio_id"] != solicitud.municipio_id
        if cambia_municipio:  # al cambiar de municipio se toma turno en el nuevo
            datos["turno"] = GestorTurnos.siguiente(datos["municipio_id"])
        for campo, valor in datos.items():
            setattr(solicitud, campo, valor)
        if estatus in Solicitud.ESTATUS:
            solicitud.estatus = estatus
        solicitud.guardar()

        self.notificar("modificada", solicitud)
        return ResultadoOperacion(solicitud, turno_cambiado=cambia_municipio)

    def cambiar_estatus(self, solicitud: Solicitud, estatus: str) -> ResultadoOperacion:
        if estatus not in Solicitud.ESTATUS:
            return ResultadoOperacion(errores={"estatus": "Estatus inválido."})
        solicitud.estatus = estatus
        solicitud.guardar()
        self.notificar(f"marcada {estatus.lower()}", solicitud)
        return ResultadoOperacion(solicitud)

    def eliminar(self, solicitud: Solicitud) -> None:
        resumen = f"{solicitud.folio} ({solicitud.curp})"
        solicitud.eliminar()
        self.notificar("eliminada", resumen)
