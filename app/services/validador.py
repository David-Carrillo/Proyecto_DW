"""Validación de solicitudes del lado del servidor.

Son las mismas reglas que aplica el navegador en static/js/solicitud.js,
pero aquí se vuelven a revisar porque nunca hay que confiar en el cliente.
"""
import re

from app.models import Asunto, Municipio, Nivel


class ValidadorSolicitud:
    RE_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?: [A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*$")
    RE_CURP = re.compile(
        r"^[A-Z][AEIOUX][A-Z]{2}\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])[HM]"
        r"(AS|BC|BS|CC|CL|CM|CS|CH|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|NL|OC|PL|QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS|NE)"
        r"[B-DF-HJ-NP-TV-Z]{3}[A-Z\d]\d$"
    )
    RE_TEL = re.compile(r"^\d{10}$")
    RE_CORREO = re.compile(r"^[^\s@]+@[^\s@]+\.[A-Za-z]{2,}$")

    CAMPOS_TEXTO = ("tramitante", "curp", "nombre", "paterno", "materno",
                    "telefono", "celular", "correo")
    CATALOGOS = {"nivel_id": (Nivel, "nivel"),
                 "municipio_id": (Municipio, "municipio"),
                 "asunto_id": (Asunto, "asunto")}

    def __init__(self):
        self.errores = {}
        self.datos = {}

    def validar(self, entrada: dict) -> bool:
        """Limpia y valida. Deja el resultado en self.datos y self.errores."""
        self.errores, self.datos = {}, {}
        for campo in self.CAMPOS_TEXTO:
            self.datos[campo] = " ".join(str(entrada.get(campo) or "").split())
        self.datos["curp"] = self.datos["curp"].upper()

        self._nombre("tramitante", obligatorio=True)
        self._nombre("nombre", obligatorio=True)
        self._nombre("paterno", obligatorio=True)
        self._nombre("materno", obligatorio=False)
        self._curp()
        self._telefonos()
        self._correo()
        self._catalogos(entrada)
        return not self.errores

    # ---- reglas individuales -------------------------------------------
    def _nombre(self, campo, obligatorio):
        v = self.datos[campo]
        if not v:
            if obligatorio:
                self.errores[campo] = "Campo obligatorio."
        elif not self.RE_NOMBRE.match(v):
            self.errores[campo] = "Solo letras y espacios."
        elif len(v) < 2:
            self.errores[campo] = "Mínimo 2 caracteres."

    def _curp(self):
        v = self.datos["curp"]
        if not v:
            self.errores["curp"] = "La CURP es obligatoria."
        elif len(v) != 18:
            self.errores["curp"] = "Debe tener 18 caracteres."
        elif not self.RE_CURP.match(v):
            self.errores["curp"] = "Formato de CURP inválido."

    def _telefonos(self):
        tel, cel = self.datos["telefono"], self.datos["celular"]
        if tel and not self.RE_TEL.match(tel):
            self.errores["telefono"] = "Debe tener 10 dígitos."
        if not cel:
            self.errores["celular"] = "El celular es obligatorio."
        elif not self.RE_TEL.match(cel):
            self.errores["celular"] = "Debe tener 10 dígitos."

    def _correo(self):
        v = self.datos["correo"]
        if not v:
            self.errores["correo"] = "El correo es obligatorio."
        elif not self.RE_CORREO.match(v):
            self.errores["correo"] = "Correo inválido (ej. usuario@dominio.com)."

    def _catalogos(self, entrada):
        for campo, (modelo, etiqueta) in self.CATALOGOS.items():
            try:
                id_ = int(entrada.get(campo) or 0)
            except (TypeError, ValueError):
                id_ = 0
            registro = modelo.obtener(id_) if id_ else None
            if not registro or not registro.activo:
                self.errores[campo] = f"Seleccione un {etiqueta}."
            else:
                self.datos[campo] = id_
