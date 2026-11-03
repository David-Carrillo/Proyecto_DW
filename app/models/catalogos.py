"""Catálogos del modelo de datos: Nivel, Municipio y Asunto.

Los tres heredan de `Catalogo`, así comparten columnas y métodos (herencia).
"""
from app.database import db
from app.models.base import ModeloBase


class Catalogo(ModeloBase):
    __abstract__ = True

    TITULO = "Catálogo"
    ORDENAR_POR_NOMBRE = False

    nombre = db.Column(db.String(100), nullable=False, unique=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    @classmethod
    def ordenados(cls, solo_activos=False):
        consulta = cls.query
        if solo_activos:
            consulta = consulta.filter_by(activo=True)
        orden = cls.nombre if cls.ORDENAR_POR_NOMBRE else cls.id
        return consulta.order_by(orden).all()

    @classmethod
    def existe_nombre(cls, nombre, excluir_id=None):
        consulta = cls.query.filter(db.func.lower(cls.nombre) == nombre.lower())
        if excluir_id:
            consulta = consulta.filter(cls.id != excluir_id)
        return consulta.first() is not None

    def en_uso(self) -> bool:
        return len(self.solicitudes) > 0

    def __repr__(self):
        return f"<{type(self).__name__} {self.nombre}>"


class Nivel(Catalogo):
    __tablename__ = "niveles"
    TITULO = "Niveles educativos"
    solicitudes = db.relationship("Solicitud", back_populates="nivel")


class Municipio(Catalogo):
    __tablename__ = "municipios"
    TITULO = "Municipios"
    ORDENAR_POR_NOMBRE = True
    solicitudes = db.relationship("Solicitud", back_populates="municipio")


class Asunto(Catalogo):
    __tablename__ = "asuntos"
    TITULO = "Asuntos"
    solicitudes = db.relationship("Solicitud", back_populates="asunto")
