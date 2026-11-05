// Formulario público "Ticket de Turno": registrar y modificar.
// Se comunica con el servidor por la API REST (/api/...).
// Las mismas reglas de validación se repiten en app/services/validador.py

class ClienteAPI {
    async peticion(metodo, url, datos) {
        const opciones = { method: metodo, headers: { "Content-Type": "application/json" } };
        if (datos) opciones.body = JSON.stringify(datos);
        const resp = await fetch(url, opciones);
        const json = await resp.json().catch(() => ({}));
        return { status: resp.status, ...json };
    }
    catalogos()                 { return this.peticion("GET", "/api/catalogos"); }
    consultar(curp, turno)      { return this.peticion("GET", `/api/solicitudes/consulta?curp=${encodeURIComponent(curp)}&turno=${encodeURIComponent(turno)}`); }
    registrar(datos)            { return this.peticion("POST", "/api/solicitudes", datos); }
    actualizar(id, datos)       { return this.peticion("PUT", `/api/solicitudes/${id}`, datos); }
}

class Validador {
    static RE_NOMBRE = /^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+( [A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*$/;
    static RE_CURP = /^[A-Z][AEIOUX][A-Z]{2}\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])[HM](AS|BC|BS|CC|CL|CM|CS|CH|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|NL|OC|PL|QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS|NE)[B-DF-HJ-NP-TV-Z]{3}[A-Z\d]\d$/;
    static RE_TEL = /^\d{10}$/;
    static RE_CORREO = /^[^\s@]+@[^\s@]+\.[A-Za-z]{2,}$/;

    static nombre(v, obligatorio) {
        if (!v) return obligatorio ? "Campo obligatorio." : "";
        if (!Validador.RE_NOMBRE.test(v)) return "Solo letras y espacios.";
        if (v.length < 2) return "Mínimo 2 caracteres.";
        return "";
    }
    static curp(v) {
        if (!v) return "La CURP es obligatoria.";
        if (v.length !== 18) return "Debe tener 18 caracteres.";
        return Validador.RE_CURP.test(v) ? "" : "Formato de CURP inválido.";
    }

    // Cada regla devuelve "" si es válido o el mensaje de error
    static reglas = {
        tramitante: v => Validador.nombre(v, true),
        curp:       v => Validador.curp(v),
        nombre:     v => Validador.nombre(v, true),
        paterno:    v => Validador.nombre(v, true),
        materno:    v => Validador.nombre(v, false),
        telefono:   v => (!v || Validador.RE_TEL.test(v)) ? "" : "Debe tener 10 dígitos.",
        celular:    v => !v ? "El celular es obligatorio." : (Validador.RE_TEL.test(v) ? "" : "Debe tener 10 dígitos."),
        correo:     v => !v ? "El correo es obligatorio." : (Validador.RE_CORREO.test(v) ? "" : "Correo inválido (ej. usuario@dominio.com)."),
        nivel_id:     v => v ? "" : "Seleccione un nivel.",
        municipio_id: v => v ? "" : "Seleccione un municipio.",
        asunto_id:    v => v ? "" : "Seleccione un asunto.",
    };
}

class FormularioSolicitud {
    constructor() {
        this.api = new ClienteAPI();
        this.form = document.getElementById("formTurno");
        this.boton = document.getElementById("btnGenerar");
        this.modo = this.form.dataset.modo;          // "registrar" o "modificar"
        this.ids = Object.keys(Validador.reglas);
        this.edicion = null;                          // {id, curp, turno} al modificar
        this.cargarCatalogos();
        this.restriccionesDeEscritura();
        this.validacionEnVivo();
        this.form.addEventListener("submit", e => this.enviar(e));
        document.getElementById("btnCerrar").addEventListener("click", () => this.cerrarModal());
        if (this.modo === "modificar") {
            document.getElementById("formBuscar").addEventListener("submit", e => this.buscar(e));
            document.getElementById("buscarCurp").addEventListener("input", e => {
                e.target.value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, "");
            });
        }
    }

    $(id) { return document.getElementById(id); }

    async cargarCatalogos() {
        const datos = await this.api.catalogos();
        const llenar = (id, lista) => lista.forEach(item => this.$(id).add(new Option(item.nombre, item.id)));
        llenar("nivel_id", datos.niveles);
        llenar("municipio_id", datos.municipios);
        llenar("asunto_id", datos.asuntos);
    }

    valor(id) {
        let v = this.$(id).value.trim().replace(/\s+/g, " ");
        return id === "curp" ? v.toUpperCase() : v;
    }

    mostrar(id, mensaje) {
        const el = this.$(id);
        if (!el) return;
        const campo = el.closest(".campo");
        campo.querySelector(".error").textContent = mensaje;
        campo.classList.toggle("invalido", !!mensaje);
        campo.classList.toggle("valido", !mensaje);
    }

    validarCampo(id) {
        const mensaje = Validador.reglas[id](this.valor(id));
        this.mostrar(id, mensaje);
        return !mensaje;
    }

    restriccionesDeEscritura() {
        ["telefono", "celular"].forEach(id => this.$(id).addEventListener("input", e => {
            e.target.value = e.target.value.replace(/\D/g, "").slice(0, 10);
        }));
        ["tramitante", "nombre", "paterno", "materno"].forEach(id => this.$(id).addEventListener("input", e => {
            e.target.value = e.target.value.replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]/g, "");
        }));
        this.$("curp").addEventListener("input", e => {
            e.target.value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, "");
        });
    }

    validacionEnVivo() {
        this.ids.forEach(id => {
            const el = this.$(id);
            el.addEventListener("blur", () => this.validarCampo(id));
            el.addEventListener("change", () => this.validarCampo(id));
            el.addEventListener("input", () => {
                if (el.closest(".campo").classList.contains("invalido")) this.validarCampo(id);
            });
        });
    }

    async buscar(e) {
        e.preventDefault();
        const curp = this.$("buscarCurp").value.trim().toUpperCase();
        const turno = this.$("buscarTurno").value.trim();
        const error = this.$("errorBuscar");
        error.textContent = "";
        if (Validador.curp(curp) || !turno) {
            error.textContent = "Escriba una CURP válida y su número de turno.";
            return;
        }
        const opciones = this.$("opcionesSolicitud");
        opciones.innerHTML = "";
        opciones.classList.add("oculto");
        this.form.classList.add("oculto");

        const r = await this.api.consultar(curp, turno);
        if (!r.ok) {
            error.textContent = r.error || "No se encontró la solicitud.";
            return;
        }
        if (r.solicitudes.length === 1) {
            this.cargarEdicion(r.solicitudes[0], curp, turno);
            return;
        }
        // Mismo turno en varios municipios: el usuario elige cuál modificar
        const aviso = document.createElement("p");
        aviso.textContent = `Hay ${r.solicitudes.length} solicitudes con esa CURP y el turno ${turno}. Elija cuál desea modificar:`;
        opciones.appendChild(aviso);
        r.solicitudes.forEach(s => {
            const boton = document.createElement("button");
            boton.type = "button";
            boton.className = "opcion-solicitud";
            boton.innerHTML = `<strong>${s.municipio}</strong> · Turno ${s.turno} (${s.folio})<br>` +
                              `<span class="ayuda">${s.asunto} · ${s.nivel} · ${s.estatus}</span>`;
            boton.addEventListener("click", () => {
                opciones.querySelectorAll(".opcion-solicitud").forEach(b => b.classList.remove("seleccionada"));
                boton.classList.add("seleccionada");
                this.cargarEdicion(s, curp, turno);
            });
            opciones.appendChild(boton);
        });
        opciones.classList.remove("oculto");
    }

    cargarEdicion(s, curp, turno) {
        this.edicion = { id: s.id, curp, turno };
        this.ids.forEach(id => { this.$(id).value = s[id] ?? ""; this.mostrar(id, ""); });
        this.$("infoEdicion").textContent =
            `Editando turno ${s.turno} de ${s.municipio} (folio ${s.folio}) · Estatus: ${s.estatus}`;
        this.form.classList.remove("oculto");
        this.form.scrollIntoView({ behavior: "smooth" });
    }

    async enviar(e) {
        e.preventDefault();
        const resultados = this.ids.map(id => this.validarCampo(id));
        if (resultados.includes(false)) {
            this.$(this.ids[resultados.indexOf(false)]).focus();
            return;
        }
        const datos = {};
        this.ids.forEach(id => datos[id] = this.valor(id));

        this.boton.disabled = true;
        try {
            let r;
            if (this.modo === "modificar" && this.edicion) {
                datos.auth_curp = this.edicion.curp;
                datos.auth_turno = this.edicion.turno;
                r = await this.api.actualizar(this.edicion.id, datos);
            } else {
                r = await this.api.registrar(datos);
            }
            if (!r.ok) {
                if (r.errores) Object.entries(r.errores).forEach(([id, msg]) => this.mostrar(id, msg));
                else alert(r.error || "No se pudo guardar la solicitud.");
                return;
            }
            this.abrirModal(r);
        } catch (err) {
            alert("No se pudo conectar con el servidor.");
        } finally {
            this.boton.disabled = false;
        }
    }

    abrirModal(r) {
        const s = r.solicitud;
        const modificando = this.modo === "modificar";
        this.$("tituloModal").textContent = modificando ? "¡Solicitud actualizada!" : "¡Turno generado!";
        this.$("numTurno").textContent = s.turno;
        this.$("detalleTurno").textContent = `${s.nombre_completo} — ${s.asunto} (${s.municipio})`;
        this.$("notaTurno").textContent = r.turno_cambiado
            ? "Como cambió de municipio, se le asignó un turno nuevo. Guarde este número."
            : "Guarde su CURP y su número de turno para modificar su solicitud.";
        this.$("btnDescargar").href = r.comprobante + "&descargar=1";
        this.$("btnVerPdf").href = r.comprobante;
        if (modificando) this.edicion = { id: s.id, curp: s.curp, turno: s.turno };
        this.$("modal").classList.remove("oculto");
    }

    cerrarModal() {
        this.$("modal").classList.add("oculto");
        if (this.modo === "registrar") {
            this.form.reset();
            document.querySelectorAll("#formTurno .campo").forEach(c => {
                c.classList.remove("valido", "invalido");
                c.querySelector(".error").textContent = "";
            });
        }
    }
}

new FormularioSolicitud();
