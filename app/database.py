"""Acceso al ORM (SQLAlchemy) mediante un Singleton."""
from flask_sqlalchemy import SQLAlchemy

from app.patterns import SingletonMeta


class Database(metaclass=SingletonMeta):
    """Singleton: una sola conexión/ORM compartida por toda la aplicación."""

    def __init__(self):
        self.orm = SQLAlchemy()

    def init_app(self, app):
        self.orm.init_app(app)


db = Database().orm
