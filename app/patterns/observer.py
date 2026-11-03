"""Patrón de diseño OBSERVER.

`Sujeto` mantiene una lista de observadores y les avisa cuando ocurre un
evento. SolicitudService es el sujeto: cada vez que se registra, modifica,
elimina o cambia de estatus una solicitud, notifica a sus observadores
(por ejemplo, el que guarda la bitácora en la base de datos).
"""
from abc import ABC, abstractmethod


class Observador(ABC):
    @abstractmethod
    def actualizar(self, evento: str, solicitud) -> None:
        """Se ejecuta cuando el sujeto notifica un evento."""


class Sujeto:
    def __init__(self):
        self._observadores = []

    def suscribir(self, observador: Observador) -> None:
        if not any(type(o) is type(observador) for o in self._observadores):
            self._observadores.append(observador)

    def desuscribir(self, observador: Observador) -> None:
        self._observadores.remove(observador)

    def notificar(self, evento: str, solicitud) -> None:
        for observador in self._observadores:
            observador.actualizar(evento, solicitud)
