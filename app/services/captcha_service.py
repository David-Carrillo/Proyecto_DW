"""Captcha de imagen para el login de administradores (hecho con Pillow)."""
import random
from io import BytesIO

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from app.patterns import SingletonMeta


class CaptchaService(metaclass=SingletonMeta):
    CARACTERES = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sin 0/O ni 1/I para no confundir
    LONGITUD = 5
    CLAVE_SESION = "captcha_texto"

    def __init__(self):
        self._fuente = self._cargar_fuente(34)

    @staticmethod
    def _cargar_fuente(tam):
        for nombre in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf",
                       "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
            try:
                return ImageFont.truetype(nombre, tam)
            except OSError:
                continue
        return ImageFont.load_default(size=tam)

    def nuevo_texto(self) -> str:
        return "".join(random.choices(self.CARACTERES, k=self.LONGITUD))

    def imagen(self, texto: str) -> bytes:
        ancho, alto = 190, 64
        img = Image.new("RGB", (ancho, alto), (238, 241, 245))
        dibujo = ImageDraw.Draw(img)

        for _ in range(6):  # líneas de ruido
            dibujo.line([(random.randint(0, ancho), random.randint(0, alto)) for _ in range(2)],
                        fill=self._color(120, 190), width=2)

        x = 12
        for letra in texto:  # cada letra con rotación y color distinto
            capa = Image.new("RGBA", (44, 56), (0, 0, 0, 0))
            ImageDraw.Draw(capa).text((6, 4), letra, font=self._fuente, fill=self._color(20, 100))
            capa = capa.rotate(random.randint(-28, 28), resample=Image.BICUBIC, expand=False)
            img.paste(capa, (x, random.randint(0, 8)), capa)
            x += 34

        for _ in range(250):  # puntos de ruido
            dibujo.point((random.randint(0, ancho - 1), random.randint(0, alto - 1)),
                         fill=self._color(60, 200))

        salida = BytesIO()
        img.filter(ImageFilter.SMOOTH).save(salida, "PNG")
        return salida.getvalue()

    def verificar(self, sesion, respuesta: str) -> bool:
        esperado = sesion.pop(self.CLAVE_SESION, None)  # se usa una sola vez
        return bool(esperado) and (respuesta or "").strip().upper() == esperado

    @staticmethod
    def _color(minimo, maximo):
        return tuple(random.randint(minimo, maximo) for _ in range(3))
