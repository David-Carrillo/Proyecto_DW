from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import db
from app.models.base import ModeloBase


class Usuario(UserMixin, ModeloBase):
    """Administrador que entra a la parte privada."""
    __tablename__ = "usuarios"

    usuario = db.Column(db.String(40), nullable=False, unique=True)
    nombre = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    def establecer_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def verificar_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return self.activo

    @classmethod
    def por_usuario(cls, usuario: str):
        return cls.query.filter_by(usuario=usuario.strip()).first()
