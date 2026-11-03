"""Llena los catálogos y crea el administrador la primera vez."""
from app.database import db
from app.models import Asunto, Municipio, Nivel, Usuario


class Seeder:
    NIVELES = ["Preescolar", "Primaria", "Secundaria"]
    MUNICIPIOS = [
        "Abasolo", "Acuña", "Allende", "Arteaga", "Candela", "Castaños",
        "Cuatro Ciénegas", "Escobedo", "Francisco I. Madero", "Frontera",
        "General Cepeda", "Guerrero", "Hidalgo", "Jiménez", "Juárez", "Lamadrid",
        "Matamoros", "Monclova", "Morelos", "Múzquiz", "Nadadores", "Nava",
        "Ocampo", "Parras", "Piedras Negras", "Progreso", "Ramos Arizpe",
        "Sabinas", "Sacramento", "Saltillo", "San Buenaventura",
        "San Juan de Sabinas", "San Pedro", "Sierra Mojada", "Torreón", "Viesca",
        "Villa Unión", "Zaragoza",
    ]
    ASUNTOS = [
        "Inscripción", "Reinscripción", "Cambio de escuela", "Duplicado de certificado",
        "Revalidación de estudios", "Equivalencia de estudios",
        "Corrección de datos en documentos", "Otro",
    ]

    def __init__(self, app):
        self.app = app

    def ejecutar(self):
        self._catalogo(Nivel, self.NIVELES)
        self._catalogo(Municipio, self.MUNICIPIOS)
        self._catalogo(Asunto, self.ASUNTOS)
        self._admin()
        db.session.commit()

    @staticmethod
    def _catalogo(modelo, nombres):
        if modelo.query.first() is None:
            db.session.add_all(modelo(nombre=n) for n in nombres)

    def _admin(self):
        if Usuario.query.first() is None:
            admin = Usuario(usuario=self.app.config["ADMIN_USUARIO"], nombre="Administrador")
            admin.establecer_password(self.app.config["ADMIN_PASSWORD"])
            db.session.add(admin)
