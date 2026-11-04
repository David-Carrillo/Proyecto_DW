"""Datos para las gráficas del dashboard."""
from sqlalchemy import func

from app.database import db
from app.models import Municipio, Solicitud


class EstadisticasService:

    def resumen(self, municipio_id=None) -> dict:
        consulta = db.session.query(Solicitud.estatus, func.count(Solicitud.id))
        if municipio_id:
            consulta = consulta.filter(Solicitud.municipio_id == municipio_id)
        conteo = dict(consulta.group_by(Solicitud.estatus).all())
        pendientes = conteo.get(Solicitud.PENDIENTE, 0)
        resueltas = conteo.get(Solicitud.RESUELTO, 0)
        return {"Pendiente": pendientes, "Resuelto": resueltas, "total": pendientes + resueltas}

    def por_municipio(self, municipio_id=None) -> list[dict]:
        consulta = (db.session.query(Municipio.nombre, Solicitud.estatus, func.count(Solicitud.id))
                    .join(Solicitud, Solicitud.municipio_id == Municipio.id))
        if municipio_id:
            consulta = consulta.filter(Municipio.id == municipio_id)
        filas = consulta.group_by(Municipio.nombre, Solicitud.estatus).all()

        agrupado = {}
        for nombre, estatus, total in filas:
            item = agrupado.setdefault(nombre, {"municipio": nombre, "Pendiente": 0, "Resuelto": 0})
            item[estatus] = total
        return sorted(agrupado.values(), key=lambda i: -(i["Pendiente"] + i["Resuelto"]))
