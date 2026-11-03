"""Configuración de la aplicación (se puede cambiar con variables de entorno)."""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "cambia-esta-clave-en-produccion")

    # Por defecto SQLite (no requiere instalar nada).
    # Para MySQL: DATABASE_URL=mysql+pymysql://usuario:clave@localhost/ticket_turno
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(INSTANCE_DIR, "ticket_turno.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False

    # Administrador que se crea la primera vez que corre la app
    ADMIN_USUARIO = os.environ.get("ADMIN_USUARIO", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin123")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
