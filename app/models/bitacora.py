from datetime import datetime

from app.database import db
from app.models.base import ModeloBase


class Bitacora(ModeloBase):
    """Historial de movimientos; lo llena el observador BitacoraObservador."""
    __tablename__ = "bitacora"

    evento = db.Column(db.String(30), nullable=False)
    detalle = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.now)

    @classmethod
    def recientes(cls, limite=10):
        return cls.query.order_by(cls.fecha.desc(), cls.id.desc()).limit(limite).all()
