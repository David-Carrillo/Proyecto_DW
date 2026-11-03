from datetime import datetime

from app.database import db
from app.models.base import ModeloBase


class Solicitud(ModeloBase):
    """Solicitud de ticket de turno. El turno es consecutivo POR MUNICIPIO."""
    __tablename__ = "solicitudes"
    __table_args__ = (
        db.UniqueConstraint("municipio_id", "turno", name="uq_turno_por_municipio"),
    )

    PENDIENTE = "Pendiente"
    RESUELTO = "Resuelto"
    ESTATUS = (PENDIENTE, RESUELTO)

    turno = db.Column(db.Integer, nullable=False)
    tramitante = db.Column(db.String(80), nullable=False)
    curp = db.Column(db.String(18), nullable=False, index=True)
    nombre = db.Column(db.String(40), nullable=False)
    paterno = db.Column(db.String(40), nullable=False)
    materno = db.Column(db.String(40))
    telefono = db.Column(db.String(10))
    celular = db.Column(db.String(10), nullable=False)
    correo = db.Column(db.String(80), nullable=False)
    estatus = db.Column(db.String(10), nullable=False, default=PENDIENTE)
    creado = db.Column(db.DateTime, nullable=False, default=datetime.now)
    actualizado = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    nivel_id = db.Column(db.Integer, db.ForeignKey("niveles.id"), nullable=False)
    municipio_id = db.Column(db.Integer, db.ForeignKey("municipios.id"), nullable=False)
    asunto_id = db.Column(db.Integer, db.ForeignKey("asuntos.id"), nullable=False)

    nivel = db.relationship("Nivel", back_populates="solicitudes")
    municipio = db.relationship("Municipio", back_populates="solicitudes")
    asunto = db.relationship("Asunto", back_populates="solicitudes")

    @property
    def nombre_completo(self) -> str:
        return " ".join(p for p in (self.nombre, self.paterno, self.materno) if p)

    @property
    def folio(self) -> str:
        """Ej. SAL-0007 (3 letras del municipio + turno)."""
        prefijo = "".join(c for c in self.municipio.nombre.upper() if c.isalpha())[:3]
        return f"{prefijo}-{self.turno:04d}"

    @property
    def resuelta(self) -> bool:
        return self.estatus == self.RESUELTO

    def to_dict(self) -> dict:
        datos = super().to_dict()
        datos.update(
            folio=self.folio,
            nombre_completo=self.nombre_completo,
            nivel=self.nivel.nombre,
            municipio=self.municipio.nombre,
            asunto=self.asunto.nombre,
        )
        return datos

    def __repr__(self):
        return f"<Solicitud {self.folio} {self.curp}>"
