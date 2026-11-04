// Dashboard: lee /api/estadisticas (API REST) y dibuja las gráficas en SVG.
// Las gráficas son clases propias (sin librerías), así funcionan sin internet.

const SVG_NS = "http://www.w3.org/2000/svg";
const COLORES = { Pendiente: "#fab219", Resuelto: "#0ca30c" };
const ESTATUS = ["Pendiente", "Resuelto"];

function svg(etiqueta, atributos = {}, padre = null) {
    const el = document.createElementNS(SVG_NS, etiqueta);
    Object.entries(atributos).forEach(([k, v]) => el.setAttribute(k, v));
    if (padre) padre.appendChild(el);
    return el;
}

class Tooltip {
    constructor() {
        this.el = document.createElement("div");
        this.el.className = "tooltip oculto";
        document.body.appendChild(this.el);
    }
    mostrar(evento, html) {
        this.el.innerHTML = html;
        this.el.classList.remove("oculto");
        const x = Math.min(evento.clientX + 14, window.innerWidth - this.el.offsetWidth - 8);
        this.el.style.left = x + "px";
        this.el.style.top = (evento.clientY + 14) + "px";
    }
    ocultar() { this.el.classList.add("oculto"); }
}

class Grafica {
    constructor(contenedor, tooltip) {
        this.contenedor = contenedor;
        this.tooltip = tooltip;
    }
    limpiar() { this.contenedor.innerHTML = ""; }
    conTooltip(elemento, html) {
        elemento.addEventListener("mousemove", e => this.tooltip.mostrar(e, html));
        elemento.addEventListener("mouseleave", () => this.tooltip.ocultar());
        elemento.addEventListener("click", e => this.tooltip.mostrar(e, html));  // táctil
    }
    leyenda() {
        const div = document.createElement("div");
        div.className = "leyenda";
        div.innerHTML = ESTATUS.map(e => `<span><i class="punto" style="background:${COLORES[e]}"></i>${e}</span>`).join("");
        this.contenedor.appendChild(div);
    }
}

class GraficaDona extends Grafica {
    dibujar(resumen) {
        this.limpiar();
        const total = resumen.total;
        const t = 200, cx = 100, cy = 100, r = 80, grosor = 30;
        const lienzo = svg("svg", { viewBox: `0 0 ${t} ${t}`, class: "svg-dona", role: "img",
            "aria-label": `Pendientes ${resumen.Pendiente}, resueltas ${resumen.Resuelto}` }, this.contenedor);
        svg("circle", { cx, cy, r, fill: "none", stroke: "#eceef1", "stroke-width": grosor }, lienzo);

        const circunferencia = 2 * Math.PI * r;
        let acumulado = 0;
        ESTATUS.forEach(e => {
            const valor = resumen[e];
            if (!total || !valor) return;
            const largo = circunferencia * valor / total;
            const separacion = valor === total ? 0 : 2;
            const arco = svg("circle", {
                cx, cy, r, fill: "none", stroke: COLORES[e], "stroke-width": grosor,
                "stroke-dasharray": `${Math.max(largo - separacion, 0)} ${circunferencia}`,
                "stroke-dashoffset": -acumulado,
                transform: `rotate(-90 ${cx} ${cy})`, class: "segmento",
            }, lienzo);
            this.conTooltip(arco, `<strong>${e}</strong>: ${valor} (${Math.round(valor * 100 / total)}%)`);
            acumulado += largo;
        });

        const centro = svg("text", { x: cx, y: cy - 2, "text-anchor": "middle", class: "dona-total" }, lienzo);
        centro.textContent = total;
        const sub = svg("text", { x: cx, y: cy + 18, "text-anchor": "middle", class: "dona-sub" }, lienzo);
        sub.textContent = "solicitudes";
        this.leyenda();
    }
}

class GraficaBarras extends Grafica {
    dibujar(filas) {
        this.limpiar();
        if (!filas.length) return;
        const ancho = 640, izq = 130, der = 40, altoFila = 30, arriba = 8, abajo = 26;
        const alto = arriba + filas.length * altoFila + abajo;
        const maximo = Math.max(...filas.map(f => f.Pendiente + f.Resuelto), 1);
        const paso = this.pasoEje(maximo);
        const tope = Math.ceil(maximo / paso) * paso;
        const escala = v => (ancho - izq - der) * v / tope;

        const lienzo = svg("svg", { viewBox: `0 0 ${ancho} ${alto}`, class: "svg-barras", role: "img",
            "aria-label": "Solicitudes por municipio y estatus" }, this.contenedor);

        for (let v = 0; v <= tope; v += paso) {  // cuadrícula y eje X
            const x = izq + escala(v);
            svg("line", { x1: x, x2: x, y1: arriba, y2: alto - abajo, class: v ? "rejilla" : "eje" }, lienzo);
            const txt = svg("text", { x, y: alto - 8, "text-anchor": "middle", class: "eje-texto" }, lienzo);
            txt.textContent = v;
        }

        filas.forEach((f, i) => {
            const y = arriba + i * altoFila + 6, h = altoFila - 12;
            const nombre = svg("text", { x: izq - 10, y: y + h / 2 + 4, "text-anchor": "end", class: "eje-texto" }, lienzo);
            nombre.textContent = f.municipio.length > 17 ? f.municipio.slice(0, 16) + "…" : f.municipio;

            let x = izq;
            ESTATUS.forEach(e => {
                if (!f[e]) return;
                const w = escala(f[e]);
                const barra = svg("rect", { x, y, width: Math.max(w - 2, 1), height: h, rx: 4,
                    fill: COLORES[e], class: "segmento" }, lienzo);
                this.conTooltip(barra, `<strong>${f.municipio}</strong><br>${e}: ${f[e]}`);
                x += w;
            });
            const total = svg("text", { x: x + 6, y: y + h / 2 + 4, class: "eje-texto total-barra" }, lienzo);
            total.textContent = f.Pendiente + f.Resuelto;
        });
        this.leyenda();
    }

    pasoEje(maximo) {
        const bruto = maximo / 5;
        const potencia = Math.pow(10, Math.floor(Math.log10(Math.max(bruto, 1))));
        return [1, 2, 5, 10].map(m => m * potencia).find(p => p >= bruto) || potencia * 10;
    }
}

class Dashboard {
    constructor() {
        this.filtro = document.getElementById("filtroMunicipio");
        const tooltip = new Tooltip();
        this.dona = new GraficaDona(document.getElementById("graficaDona"), tooltip);
        this.barras = new GraficaBarras(document.getElementById("graficaBarras"), tooltip);
        this.filtro.addEventListener("change", () => this.cargar());
        this.cargar();
    }

    async cargar() {
        const id = this.filtro.value;
        const resp = await fetch("/api/estadisticas" + (id ? `?municipio_id=${id}` : ""));
        if (resp.status === 401) { location.href = "/admin/login"; return; }
        const datos = await resp.json();
        this.tiles(datos.resumen);
        this.tabla(datos.por_municipio);

        const vacio = datos.resumen.total === 0;
        document.querySelectorAll(".sin-datos").forEach(p => p.classList.toggle("oculto", !vacio));
        document.querySelectorAll(".lienzo").forEach(l => l.classList.toggle("oculto", vacio));
        if (!vacio) {
            this.dona.dibujar(datos.resumen);
            this.barras.dibujar(datos.por_municipio);
        }
    }

    tiles(r) {
        document.getElementById("tTotal").textContent = r.total;
        document.getElementById("tPendiente").textContent = r.Pendiente;
        document.getElementById("tResuelto").textContent = r.Resuelto;
        document.getElementById("tPorcentaje").textContent =
            r.total ? Math.round(r.Resuelto * 100 / r.total) + "%" : "–";
        const nombre = this.filtro.value ? this.filtro.selectedOptions[0].text : "todos los municipios";
        document.getElementById("tituloDona").textContent = `Estatus · ${nombre}`;
    }

    tabla(filas) {
        const cuerpo = document.getElementById("tablaMunicipios");
        cuerpo.innerHTML = filas.length ? "" : '<tr><td colspan="4" class="centrado">Sin datos</td></tr>';
        filas.forEach(f => {
            const tr = document.createElement("tr");
            [f.municipio, f.Pendiente, f.Resuelto, f.Pendiente + f.Resuelto].forEach(v => {
                const td = document.createElement("td");
                td.textContent = v;
                tr.appendChild(td);
            });
            cuerpo.appendChild(tr);
        });
    }
}

new Dashboard();
