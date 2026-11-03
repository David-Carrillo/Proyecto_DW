"""CONTROLADOR (la C de MVC): reciben la petición, usan servicios y modelos,
y regresan una vista (HTML) o JSON (API REST)."""
from .publico_controller import PublicoController
from .auth_controller import AuthController
from .admin_controller import AdminController
from .catalogo_controller import CatalogoController
from .api_controller import ApiController

CONTROLADORES = (PublicoController, AuthController, AdminController,
                 CatalogoController, ApiController)
