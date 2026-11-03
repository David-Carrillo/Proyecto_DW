"""MODELO (la M de MVC): clases mapeadas a tablas con el ORM SQLAlchemy."""
from .base import ModeloBase
from .catalogos import Catalogo, Nivel, Municipio, Asunto
from .solicitud import Solicitud
from .usuario import Usuario
from .bitacora import Bitacora
