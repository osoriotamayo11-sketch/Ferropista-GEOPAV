# -*- coding: utf-8 -*-
"""Marco institucional común a las láminas del proyecto (matplotlib).

Mismo formato que las láminas del OE 3 (sesión 15): logos de la Universidad de Ibagué a la izquierda
y del semillero GEOPAV a la derecha, título en verde GEOPAV #178E2C, subtítulo en azul #193F77,
filete verde bajo el encabezado y otro sobre el pie de fuentes. Ver
ferropista/estandar-presentacion-documentos.md (verde principal, azul secundario).

Uso:
    import sys, os; sys.path.insert(0, os.path.join(<raíz del repo>, "Comun"))
    from lamina_institucional import encabezado, pie, dibujar_via, VERDE, AZUL, GRIS
    arriba = encabezado(fig, "Título", "Subtítulo")      # fracción de figura bajo el encabezado
    abajo  = pie(fig, "Fuentes …")                        # fracción de figura sobre el pie
    fig.subplots_adjust(top=arriba - 0.02, bottom=abajo + 0.03)

`dibujar_via(ax)` pinta la vía actual (Ruta 40, OpenStreetMap) desde
OE2_Plataforma/Act2_Visor/via_actual_ruta40.geojson, que produce via_actual_ruta40.py.
"""
import json, os, textwrap
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERDE, AZUL, GRIS, TINTA = "#178E2C", "#193F77", "#475569", "#111827"
VIA = os.path.join(RAIZ, "OE2_Plataforma", "Act2_Visor", "via_actual_ruta40.geojson")
COLOR_VIA = "#7A2E12"          # pardo rojizo: se distingue del azul del trazado y del verde del relieve

def _logo(fig, archivo, x, y, alto_in, ancla="izq"):
    """Coloca un logo y devuelve su ancho en pulgadas (0 si falta el archivo)."""
    p = os.path.join(RAIZ, "public", archivo)
    if not os.path.exists(p): return 0.0
    im = Image.open(p); W, H = fig.get_size_inches()
    ancho_in = alto_in * im.width / im.height
    x0 = x if ancla == "izq" else x - ancho_in / W
    ax = fig.add_axes([x0, y, ancho_in / W, alto_in / H]); ax.imshow(im); ax.axis("off")
    return ancho_in

def encabezado(fig, titulo, subtitulo, alto_in=1.05):
    """Dibuja el encabezado y devuelve la fracción vertical donde termina (filete verde)."""
    W, H = fig.get_size_inches(); fig.patch.set_facecolor("white")
    y_filete = 1 - alto_in / H
    wi = _logo(fig, "logo-unibague.png", 0.012, y_filete + 0.18 / H, alto_in * 0.68, "izq")
    wd = _logo(fig, "logo-geopav.png", 0.988, y_filete + 0.14 / H, alto_in * 0.74, "der")
    # El título se centra en el espacio libre entre logos y se reduce si no cabe.
    x0 = 0.012 + (wi + 0.25) / W; x1 = 0.988 - (wd + 0.25) / W; libre_in = (x1 - x0) * W
    fs_t = min(19.0, libre_in * 72 / (0.60 * len(titulo)))
    fs_s = min(10.2, libre_in * 72 / (0.53 * len(subtitulo)))
    xc = (x0 + x1) / 2
    fig.text(xc, 1 - 0.36 / H, titulo, ha="center", va="center", fontsize=fs_t, color=VERDE, weight="bold")
    fig.text(xc, 1 - 0.70 / H, subtitulo, ha="center", va="center", fontsize=fs_s, color=AZUL)
    fig.add_artist(Line2D([0.012, 0.988], [y_filete] * 2, color=VERDE, lw=2))
    return y_filete

def pie(fig, texto, ancho_car=None, fs=8.2):
    """Pie de fuentes en gris con filete verde; devuelve la fracción vertical del filete."""
    W, H = fig.get_size_inches()
    ancho_car = ancho_car or int(W * 14.2)
    lineas = []
    for par in texto.split("\n"): lineas += textwrap.wrap(par, ancho_car) or [""]
    alto_in = 0.16 + len(lineas) * fs * 1.5 / 72
    fig.text(0.015, (alto_in - 0.08) / H, "\n".join(lineas), fontsize=fs, va="top", color=GRIS, linespacing=1.5)
    y = (alto_in + 0.02) / H
    fig.add_artist(Line2D([0.012, 0.988], [y] * 2, color=VERDE, lw=1))
    return y

def dibujar_via(ax, lw=1.6, z=4.2, casing=True, transformar=None):
    """Pinta la Ruta 40 actual; los tramos en túnel van a trazos. Devuelve los manejadores de leyenda."""
    g = json.load(open(VIA, encoding="utf-8"))
    for f in g["features"]:
        xs, ys = zip(*f["geometry"]["coordinates"])
        if transformar: xs, ys = transformar(xs, ys)
        if f["properties"]["tunel"]:
            ax.plot(xs, ys, color=COLOR_VIA, lw=lw, ls=(0, (2.2, 1.4)), zorder=z, solid_capstyle="butt")
        else:
            if casing: ax.plot(xs, ys, color="white", lw=lw + 1.6, zorder=z - 0.05, alpha=.9, solid_capstyle="round")
            ax.plot(xs, ys, color=COLOR_VIA, lw=lw, zorder=z, solid_capstyle="round")
    return [Line2D([], [], color=COLOR_VIA, lw=lw, label="Vía actual, Ruta 40 [F, OSM]"),
            Line2D([], [], color=COLOR_VIA, lw=lw, ls=(0, (2.2, 1.4)), label="Tramos en túnel (Túnel de La Línea, 2020)")]

FUENTE_VIA = ("Vía actual: Ruta Nacional 40 según OpenStreetMap (© colaboradores de OpenStreetMap, ODbL), "
              "extraída por via_actual_ruta40.py [F]")
