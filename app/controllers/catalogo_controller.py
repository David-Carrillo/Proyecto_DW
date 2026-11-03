"""CRUD genérico para los catálogos (Niveles, Municipios, Asuntos).

Una sola clase sirve para los tres catálogos gracias al polimorfismo:
todos heredan de `Catalogo` y tienen los mismos métodos.
"""
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.controllers.base import Controlador
from app.models import Asunto, Municipio, Nivel


class CatalogoController(Controlador):
    nombre = "catalogos"
    prefijo = "/admin/catalogos"

    MODELOS = {"niveles": Nivel, "municipios": Municipio, "asuntos": Asunto}

    def registrar_rutas(self):
        self.ruta("/", self.indice)
        self.ruta("/<tipo>", self.lista)
        self.ruta("/<tipo>/nuevo", self.formulario, methods=["GET", "POST"], endpoint="nuevo")
        self.ruta("/<tipo>/<int:id_>/editar", self.formulario, methods=["GET", "POST"])
        self.ruta("/<tipo>/<int:id_>/activo", self.alternar_activo, methods=["POST"])
        self.ruta("/<tipo>/<int:id_>/eliminar", self.eliminar, methods=["POST"])

    def _modelo(self, tipo):
        return self.MODELOS.get(tipo) or abort(404)

    @login_required
    def indice(self):
        return redirect(url_for("catalogos.lista", tipo="niveles"))

    @login_required
    def lista(self, tipo):
        modelo = self._modelo(tipo)
        return render_template("admin/catalogo_lista.html", tipo=tipo, modelo=modelo,
                               registros=modelo.ordenados(), catalogos=self.MODELOS)

    @login_required
    def formulario(self, tipo, id_=None):
        modelo = self._modelo(tipo)
        registro = modelo.obtener(id_) if id_ else modelo()
        if id_ and not registro:
            abort(404)

        error = None
        if request.method == "POST":
            nombre = " ".join(request.form.get("nombre", "").split())
            if len(nombre) < 2:
                error = "Escriba un nombre de al menos 2 caracteres."
            elif modelo.existe_nombre(nombre, excluir_id=id_):
                error = "Ya existe un registro con ese nombre."
            else:
                registro.nombre = nombre
                registro.activo = request.form.get("activo") == "on"
                registro.guardar()
                flash(f"«{nombre}» guardado.", "ok")
                return redirect(url_for("catalogos.lista", tipo=tipo))
            registro.nombre = nombre

        return render_template("admin/catalogo_form.html", tipo=tipo, modelo=modelo,
                               registro=registro, error=error, catalogos=self.MODELOS)

    @login_required
    def alternar_activo(self, tipo, id_):
        registro = self._modelo(tipo).obtener(id_) or abort(404)
        registro.activo = not registro.activo
        registro.guardar()
        flash(f"«{registro.nombre}» ahora está {'activo' if registro.activo else 'inactivo'}.", "ok")
        return redirect(url_for("catalogos.lista", tipo=tipo))

    @login_required
    def eliminar(self, tipo, id_):
        registro = self._modelo(tipo).obtener(id_) or abort(404)
        if registro.en_uso():
            flash(f"«{registro.nombre}» tiene solicitudes registradas; "
                  "no se puede eliminar, pero puede desactivarlo.", "error")
        else:
            registro.eliminar()
            flash(f"«{registro.nombre}» eliminado.", "ok")
        return redirect(url_for("catalogos.lista", tipo=tipo))
