from abc import ABC, abstractmethod

from flask import Blueprint


class Controlador(ABC):
    """Clase padre de los controladores: cada uno tiene su Blueprint y sus rutas."""

    nombre = None
    prefijo = None

    def __init__(self):
        self.bp = Blueprint(self.nombre, __name__, url_prefix=self.prefijo)
        self.registrar_rutas()

    @abstractmethod
    def registrar_rutas(self) -> None:
        """Cada controlador declara aquí sus URLs."""

    def ruta(self, regla, funcion, **opciones):
        self.bp.add_url_rule(regla, view_func=funcion, **opciones)
