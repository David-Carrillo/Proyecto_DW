"""Login con captcha y cierre de sesión de administradores."""
from flask import flash, redirect, render_template, request, session, url_for, make_response
from flask_login import current_user, login_required, login_user, logout_user

from app.controllers.base import Controlador
from app.models import Usuario
from app.services import CaptchaService


class AuthController(Controlador):
    nombre = "auth"
    prefijo = "/admin"

    def __init__(self):
        self.captcha = CaptchaService()
        super().__init__()

    def registrar_rutas(self):
        self.ruta("/login", self.login, methods=["GET", "POST"])
        self.ruta("/logout", self.logout, methods=["POST"])
        self.ruta("/captcha.png", self.imagen_captcha)

    def login(self):
        if current_user.is_authenticated:
            return redirect(url_for("admin.dashboard"))

        if request.method == "POST":
            usuario = request.form.get("usuario", "")
            password = request.form.get("password", "")
            captcha_ok = self.captcha.verificar(session, request.form.get("captcha", ""))
            cuenta = Usuario.por_usuario(usuario)

            if not captcha_ok:
                flash("El código captcha no coincide. Intente de nuevo.", "error")
            elif not cuenta or not cuenta.verificar_password(password) or not cuenta.activo:
                flash("Usuario o contraseña incorrectos.", "error")
            else:
                login_user(cuenta)
                session.permanent = False
                flash(f"Bienvenido, {cuenta.nombre}.", "ok")
                destino = request.args.get("next", "")
                return redirect(destino if destino.startswith("/admin") else url_for("admin.dashboard"))

            return render_template("auth/login.html", usuario=usuario), 401

        return render_template("auth/login.html")

    @login_required
    def logout(self):
        logout_user()
        session.clear()
        flash("Sesión cerrada correctamente.", "ok")
        return redirect(url_for("auth.login"))

    def imagen_captcha(self):
        texto = self.captcha.nuevo_texto()
        session[CaptchaService.CLAVE_SESION] = texto
        respuesta = make_response(self.captcha.imagen(texto))
        respuesta.headers["Content-Type"] = "image/png"
        respuesta.headers["Cache-Control"] = "no-store"
        return respuesta
