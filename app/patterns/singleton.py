"""Patrón de diseño SINGLETON.

Cualquier clase que use `metaclass=SingletonMeta` tendrá una sola instancia
en toda la aplicación: la primera vez que se crea se guarda, y las siguientes
llamadas devuelven ese mismo objeto.

Se usa en: Database (ORM), SolicitudService y CaptchaService.
"""


class SingletonMeta(type):
    _instancias = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instancias:
            cls._instancias[cls] = super().__call__(*args, **kwargs)
        return cls._instancias[cls]
