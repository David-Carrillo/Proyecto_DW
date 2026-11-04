"""Observadores concretos que reaccionan a los eventos de SolicitudService."""
from flask import current_app

from app.models import Bitacora, Solicitud
from app.patterns import Observador


def _describir(solicitud) -> str:
    if isinstance(solicitud, Solicitud):
        return f"{solicitud.folio} - {solicitud.nombre_completo} ({solicitud.curp})"
    return str(solicitud)


class BitacoraObservador(Observador):
    """Guarda cada movimiento en la tabla bitácora (se ve en el dashboard)."""

    def actualizar(self, evento, solicitud):
        Bitacora(evento=evento, detalle=_describir(solicitud)[:200]).guardar()


class ConsolaObservador(Observador):
    """Escribe el movimiento en la terminal de VS Code."""

    def actualizar(self, evento, solicitud):
        current_app.logger.info("Solicitud %s: %s", evento, _describir(solicitud))
