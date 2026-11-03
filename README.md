# Ticket de Turno

Aplicación web para solicitar turnos de atención. Backend en **Python + Flask**, ORM **SQLAlchemy**, base de datos **SQLite** (cambiable a MySQL), arquitectura **MVC** y **100 % orientada a objetos**.

## Cómo correrlo en Visual Studio Code

1. Abre la carpeta `ticket_turno` en VS Code.
2. Abre una terminal (Ctrl + ñ) y crea el entorno virtual:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
   (En Mac/Linux: `source venv/bin/activate`)
3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
4. Ejecuta:
   ```
   python run.py
   ```
5. Abre http://127.0.0.1:5000

La primera vez se crea la base de datos `instance/ticket_turno.db` con los catálogos y un administrador:

| Usuario | Contraseña |
|---|---|
| `admin` | `Admin123` |

> Para empezar con la base de datos vacía, borra la carpeta `instance/` y vuelve a correr la app.

## Estructura (MVC)

```
ticket_turno/
├── run.py                       # punto de entrada
├── config.py                    # configuración (BD, clave secreta, admin)
├── requirements.txt
└── app/
    ├── __init__.py              # AppFactory  → patrón FACTORY
    ├── database.py              # Database    → patrón SINGLETON (ORM)
    ├── patterns/                # SingletonMeta, Observador/Sujeto
    ├── models/          (M)     # clases mapeadas con el ORM
    │   ├── base.py              # ModeloBase: guardar(), eliminar(), to_dict()
    │   ├── catalogos.py         # Catalogo → Nivel, Municipio, Asunto (herencia)
    │   ├── solicitud.py
    │   ├── usuario.py
    │   └── bitacora.py
    ├── services/                # lógica de negocio
    │   ├── solicitud_service.py # SolicitudService, SolicitudFactory, GestorTurnos
    │   ├── validador.py         # validación del lado servidor
    │   ├── comprobante_pdf.py   # PDF con código QR de la CURP
    │   ├── captcha_service.py   # captcha de imagen
    │   ├── estadisticas_service.py
    │   ├── observadores.py      # BitacoraObservador, ConsolaObservador
    │   └── seeder.py            # datos iniciales
    ├── controllers/     (C)     # cada controlador es una clase
    │   ├── publico_controller.py
    │   ├── auth_controller.py   # login con captcha / logout
    │   ├── admin_controller.py  # dashboard y CRUD de solicitudes
    │   ├── catalogo_controller.py
    │   └── api_controller.py    # API REST (MethodView)
    ├── templates/       (V)     # vistas HTML (Jinja2)
    └── static/                  # CSS responsivo y JS (también con clases)
```

## Cómo cumple cada punto

| # | Requisito | Dónde está |
|---|---|---|
| — | Orientado a objetos | Modelos, servicios, controladores y JS son clases; herencia (`Catalogo`, `Controlador`, `RecursoAPI`, `Grafica`) |
| — | MVC | `models/` · `templates/` · `controllers/` |
| — | No PHP | Python + Flask |
| — | Responsivo | `static/css/styles.css`: menú hamburguesa, tablas como tarjetas en celular |
| 1 | Login con captcha | `/admin/login` · `auth_controller.py` · `captcha_service.py` |
| 2 | Registrar y modificar (CURP + turno), PDF, turno por municipio | `/` y `/modificar` · `GestorTurnos` · `comprobante_pdf.py` |
| 3 | QR con la CURP en el PDF | `ComprobantePDF._qr()` |
| 4 | Consulta por CURP o nombre, CRUD, estatus Resuelto/Pendiente | `/admin/solicitudes` |
| 5 | CRUD de catálogos | `/admin/catalogos` (Niveles, Municipios, Asuntos) |
| 6 | Cerrar sesión y menú | barra superior (`base.html`) |
| 7 | API REST | `api_controller.py` (tabla abajo) |
| 8 | Dashboard con gráficas filtrable por municipio | `/admin/dashboard` · `static/js/dashboard.js` |
| 9 | Git | ver sección **Git** |
| 10 | ORM | SQLAlchemy en todos los accesos a datos |
| 11 | Patrones de diseño | **Singleton**, **Factory** y **Observer** (abajo) |

### Patrones de diseño

- **Singleton** — `patterns/singleton.py`. `Database`, `SolicitudService` y `CaptchaService` tienen una sola instancia.
- **Factory** — `AppFactory` arma la aplicación; `SolicitudFactory` crea solicitudes ya con su turno asignado.
- **Observer** — `SolicitudService` (sujeto) avisa a `BitacoraObservador` y `ConsolaObservador` cada vez que se registra, modifica, elimina o cambia el estatus de una solicitud. La bitácora se ve en el dashboard.

### API REST

| Método | URL | Acceso | Uso |
|---|---|---|---|
| GET | `/api/catalogos` | público | llena los selects del formulario |
| POST | `/api/solicitudes` | público | registrar solicitud |
| GET | `/api/solicitudes/consulta?curp=&turno=` | público | buscar para modificar |
| PUT | `/api/solicitudes/<id>` | público (con CURP + turno) o admin | modificar |
| GET | `/api/solicitudes?q=` | admin | listar / buscar |
| GET | `/api/solicitudes/<id>` | admin | ver una |
| DELETE | `/api/solicitudes/<id>` | admin | eliminar |
| PATCH | `/api/solicitudes/<id>/estatus` | admin | cambiar estatus |
| GET | `/api/estadisticas?municipio_id=` | admin | datos del dashboard |

El formulario público y el dashboard consumen esta API con `fetch`.

### Reglas de negocio

- El turno empieza en **1 para cada municipio** y sube de uno en uno. Si al modificar se cambia de municipio, se asigna el siguiente turno de ese municipio.
- Para modificar, el usuario debe dar la **CURP y el número de turno**.
- Un registro de catálogo con solicitudes no se puede borrar, solo desactivar (deja de salir en el formulario).

## Usar MySQL (opcional)

```
pip install pymysql
set DATABASE_URL=mysql+pymysql://usuario:clave@localhost/ticket_turno
python run.py
```
Las tablas se crean solas gracias al ORM.

## Git

Desde la terminal de VS Code (o la pestaña *Source Control*):

```
git init
git add .
git commit -m "Estructura MVC con Flask y SQLAlchemy"
git branch -M main
git remote add origin https://github.com/USUARIO/ticket_turno.git
git push -u origin main
```

Para demostrar actividad, cada integrante trabaja en una rama y la une con *merge* o *pull request*, por ejemplo:

```
git checkout -b feature/dashboard
# ...cambios...
git add .
git commit -m "Dashboard con gráficas por estatus y municipio"
git push -u origin feature/dashboard
# en GitHub: abrir Pull Request y hacer merge a main
```
