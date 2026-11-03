from datetime import datetime

from app.database import db


class ModeloBase(db.Model):
    """Clase padre de todos los modelos: id y operaciones comunes del ORM."""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

    def guardar(self):
        db.session.add(self)
        db.session.commit()
        return self

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self) -> dict:
        datos = {}
        for columna in self.__table__.columns:
            valor = getattr(self, columna.name)
            datos[columna.name] = valor.isoformat() if isinstance(valor, datetime) else valor
        return datos

    @classmethod
    def obtener(cls, id_):
        return db.session.get(cls, id_)
