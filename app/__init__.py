"""Patrón de diseño FACTORY: AppFactory arma y devuelve la aplicación Flask
ya configurada (base de datos, login, controladores, observadores)."""
import os

from flask import Flask, render_template
from flask_login import LoginManager

from app.database import Database, db
from config import Config


class AppFactory:

    @classmethod
    def crear(cls, config=Config) -> Flask:
        app = Flask(__name__, instance_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "instance"))
        app.config.from_object(config)
        os.makedirs(app.instance_path, exist_ok=True)

        Database().init_app(app)
        cls._login(app)
        cls._controladores(app)
        cls._errores(app)

        with app.app_context():
            from app.services import Seeder
            db.create_all()
            Seeder(app).ejecutar()
        cls._observadores()
        return app

    @staticmethod
    def _login(app):
        from app.models import Usuario
        gestor = LoginManager(app)
        gestor.login_view = "auth.login"
        gestor.login_message = "Inicie sesión para entrar a la parte administrativa."
        gestor.login_message_category = "error"
        gestor.user_loader(lambda id_: Usuario.obtener(int(id_)))

    @staticmethod
    def _controladores(app):
        from app.controllers import CONTROLADORES
        for clase in CONTROLADORES:
            app.register_blueprint(clase().bp)

    @staticmethod
    def _observadores():
        from app.services import BitacoraObservador, ConsolaObservador, SolicitudService
        servicio = SolicitudService()
        servicio.suscribir(BitacoraObservador())
        servicio.suscribir(ConsolaObservador())

    @staticmethod
    def _errores(app):
        mensajes = {403: "No tiene permiso para ver esta página.",
                    404: "La página que busca no existe."}
        for codigo, mensaje in mensajes.items():
            app.register_error_handler(
                codigo, lambda e, c=codigo, m=mensaje: (render_template("error.html", codigo=c, mensaje=m), c))


def create_app(config=Config) -> Flask:
    return AppFactory.crear(config)
