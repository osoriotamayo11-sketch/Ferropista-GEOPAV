# -*- coding: utf-8 -*-
"""OE 3 · Act 2 — Mapa base de susceptibilidad y amenaza por movimientos en masa en los portales.
A3 apaisado → ../Visuales/mapa_susceptibilidad_OE3.png (200 ppp), .jpg y .pdf.

No escribe cifras a mano. Lee:
  Datos/{susc,amen,inv}_<portal>.geojson   (descargar_capas_mapa_OE3.py; SGC, SIMMA 1:100.000)
  consulta_amenaza_mm_OE3.json             (consulta_amenaza_mm_OE3.py: clases en el punto y en 3 km)
  pendiente_portales_OE3.json              (pendiente_portales_OE3.py: Copernicus GLO-30)
  ../../dem_corredor.tif                   (solo para el sombreado del relieve)
Ejecutar desde cualquier carpeta: python mapa_susceptibilidad_OE3.py. Requiere numpy, matplotlib,
shapely, tifffile, Pillow.
"""
import json, math, os, textwrap
import numpy as np, tifffile
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, PathPatch
from matplotlib.path import Path as MPath
from matplotlib.lines import Line2D
from shapely.geometry import shape
from PIL import Image
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Comun"))
from lamina_institucional import dibujar_via, FUENTE_VIA  # vía actual (sesión 16)

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI); REPO = os.path.dirname(RAIZ)
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))
amz = J(AQUI, "consulta_amenaza_mm_OE3.json")["portales"]
pen = J(AQUI, "pendiente_portales_OE3.json")["portales"]
VERDE, AZUL, GRIS = "#178E2C", "#193F77", "#475569"
num = lambda x, d=1: f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
# Rampa secuencial de un solo tono (naranja → rojo oscuro) para magnitud creciente.
COL = {"Muy baja": "#FFF5E6", "Baja": "#FDE2BF", "Media": "#F6C68F", "Alta": "#D9591E", "Muy Alta": "#7F1D0B"}
SUSMM = {1: "Muy baja", 2: "Baja", 3: "Media", 4: "Alta", 5: "Muy Alta"}
PORTALES = [("oriental_Ibague", "Portal oriental — Ibagué (DANE 73001)", "244"),
            ("occidental_Calarca", "Portal occidental — Calarcá (DANE 63130)", "243")]

# ---- DEM para el sombreado
t = tifffile.TiffFile(os.path.join(REPO, "dem_corredor.tif")); pg = t.pages[0]
px = pg.tags["ModelPixelScaleTag"].value[0]; tp = pg.tags["ModelTiepointTag"].value; X0, Y0 = tp[3], tp[4]
Z = pg.asarray().astype("float64")

def sombreado(caja, lat):
    lo0, la0, lo1, la1 = caja
    f0, f1 = int((Y0 - la1) / px), int(math.ceil((Y0 - la0) / px)); c0, c1 = int((lo0 - X0) / px), int(math.ceil((lo1 - X0) / px))
    z = Z[f0:f1 + 1, c0:c1 + 1]
    dx = px * 111320 * math.cos(math.radians(lat)); dy = px * 110574
    gy, gx = np.gradient(z, dy, dx)
    pend = np.arctan(np.hypot(gx, gy)); asp = np.arctan2(-gx, gy)
    az, alt = math.radians(315), math.radians(45)
    hs = np.sin(alt) * np.cos(pend) + np.cos(alt) * np.sin(pend) * np.cos(az - asp - math.pi / 2)
    ext = (X0 + c0 * px, X0 + (c1 + 1) * px, Y0 - (f1 + 1) * px, Y0 - f0 * px)
    return np.clip(hs, 0, 1), ext

def dibuja_poligonos(ax, gj, clase):
    """Rellena cada polígono respetando sus huecos (camino compuesto) y lo contornea en blanco."""
    for f in gj["features"]:
        g = shape(f["geometry"]); c = COL[clase(f["properties"])]
        for p in (g.geoms if hasattr(g, "geoms") else [g]):
            if p.geom_type != "Polygon": continue
            anillos = [np.asarray(p.exterior.coords)] + [np.asarray(h.coords) for h in p.interiors]
            v = np.concatenate(anillos); cod = []
            for r in anillos: cod += [MPath.MOVETO] + [MPath.LINETO] * (len(r) - 2) + [MPath.CLOSEPOLY]
            ax.add_patch(PathPatch(MPath(v, cod), fc=c, ec="white", lw=.5, alpha=.55, zorder=2))

def panel(ax, key, capa, titulo):
    lon, lat = amz[key]["lon"], amz[key]["lat"]
    gj = J(AQUI, "Datos", f"{capa}_{key}.geojson"); caja = gj["ventana_grados"]
    hs, ext = sombreado(caja, lat)
    ax.imshow(hs, extent=ext, cmap="gray", vmin=0, vmax=1, zorder=1, interpolation="bilinear")
    dibuja_poligonos(ax, gj, (lambda p: SUSMM[p["SUSMM"]]) if capa == "susc" else (lambda p: p["CATAME"]))
    r_lon = 3000 / (111320 * math.cos(math.radians(lat))); r_lat = 3000 / 110574
    th = np.linspace(0, 2 * math.pi, 200)
    ax.plot(lon + r_lon * np.cos(th), lat + r_lat * np.sin(th), color=AZUL, lw=1.1, ls="--", zorder=5)
    inv = J(AQUI, "Datos", f"inv_{key}.geojson")["features"]
    for f in inv:
        x, y = f["geometry"]["coordinates"][:2]
        ax.plot(x, y, marker="^", ms=8, mfc="black", mec="white", mew=.8, zorder=10)
    dibujar_via(ax, lw=1.8, z=4.5)
    ax.plot(lon, lat, marker="+", ms=18, mew=2.2, color=AZUL, zorder=7)
    ax.plot(lon, lat, marker="o", ms=7, mfc="none", mec=AZUL, mew=1.6, zorder=7)
    ax.set_xlim(caja[0], caja[2]); ax.set_ylim(caja[1], caja[3]); ax.set_aspect(1 / math.cos(math.radians(lat)))
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_color(GRIS)
    ax.set_title(titulo, fontsize=10.5, color=AZUL, weight="bold", loc="left")
    # barra de 1 km y norte
    km = 1000 / (111320 * math.cos(math.radians(lat))); x0 = caja[0] + 0.004; y0 = caja[1] + 0.004
    ax.add_patch(plt.Rectangle((x0 - .0015, y0 - .002), km + .003, .0065, fc="white", alpha=.85, zorder=8))
    ax.plot([x0, x0 + km], [y0, y0], color="black", lw=3.5, zorder=9)
    ax.text(x0 + km / 2, y0 + .0012, "1 km", ha="center", fontsize=8, weight="bold", zorder=9)
    ax.annotate("N", xy=(caja[2] - .005, caja[3] - .004), xytext=(caja[2] - .005, caja[3] - .013), ha="center", fontsize=9,
                weight="bold", zorder=9, arrowprops=dict(arrowstyle="-|>", color="black", lw=1.6))

fig = plt.figure(figsize=(16.54, 11.69)); fig.patch.set_facecolor("white")
for f, rect in (("logo-unibague.png", [0.012, 0.905, 0.13, 0.08]), ("logo-geopav.png", [0.925, 0.905, 0.06, 0.08])):
    p = os.path.join(REPO, "public", f)
    if os.path.exists(p):
        a = fig.add_axes(rect); a.imshow(Image.open(p)); a.axis("off")
fig.text(0.5, 0.955, "Mapa base de susceptibilidad por movimientos en masa — OE 3, Actividad 2", ha="center", fontsize=19, color=VERDE, weight="bold")
fig.text(0.5, 0.925, "Entorno de 3 km de los portales del OE 1 sobre la zonificación 1:100.000 del SGC (SIMMA) · Semillero GEOPAV, Universidad de Ibagué · Paz y Región 2026B",
         ha="center", fontsize=10.5, color=AZUL)
fig.add_artist(Line2D([0.015, 0.985], [0.895, 0.895], color=VERDE, lw=2))

for i, (key, tit, pl) in enumerate(PORTALES):
    xb = 0.025 + i * 0.49
    fig.text(xb, 0.83, tit, fontsize=13, color=AZUL, weight="bold")
    panel(fig.add_axes([xb, 0.44, 0.232, 0.36]), key, "susc", f"Susceptibilidad · plancha {pl}")
    panel(fig.add_axes([xb + 0.24, 0.44, 0.232, 0.36]), key, "amen", f"Amenaza relativa · plancha {pl}")
    a, p = amz[key], pen[key]
    sus = ", ".join(SUSMM[x["SUSMM"]].lower() for x in a["susceptibilidad_100k_en_punto"])
    cl = "; ".join(f"{c.lower()} {num(v['area_pct'])} %" + (f" (la más cercana a {num(v['dist_m'], 0)} m)" if v["dist_m"] > 0 else "")
                   for c, v in sorted(a["amenaza_100k_3km"].items(), key=lambda kv: -kv[1]["area_pct"]))
    inv = a["inventario_simma_3km"]; mun = a["resumen_municipal_amenaza_100k_pct_area"][0]
    c250, c500 = p["circulos"]["250"], p["circulos"]["500"]
    geo = " / ".join(x["UNIGMF"] for x in a["geomorfologia_100k_en_punto"])
    txt = (f"Susceptibilidad 1:100.000 en el punto [F]: {sus}" + (" (límite entre dos clases)" if len(a['susceptibilidad_100k_en_punto']) > 1 else "") + "\n"
           f"Amenaza relativa 1:100.000 en el punto [F]: {a['amenaza_100k_en_punto'][0]['CATAME'].lower()}\n"
           f"Amenaza en el círculo de 3 km [CP]: {cl}\n"
           f"Geomorfología aplicada 1:100.000 [F]: {geo}\n"
           f"Inventario SIMMA a 3 km [F]: {len(inv)} evento(s)" + (": " + ", ".join(f"{x['SUBTIPO'].lower()} a {num(x['dist_km'])} km" for x in inv) if inv else "") + "\n"
           f"Pendiente del terreno, GLO-30 [CP]: {num(p['pendiente_pixel_grados'])}° en el píxel del portal; en 250 m media {num(c250['media'])}°, "
           f"p90 {num(c250['p90'])}°, {num(c250['pct_mayor_25'])} % del área > 25°; en 500 m máx. {num(c500['max'])}° y desnivel {num(c500['desnivel_m'], 0)} m\n"
           f"Cota del píxel {num(p['cota_pixel_msnm'])} msnm (control: {num(p['cota_OE1_msnm'])} msnm del OE 1) · ladera orientada a {p['aspecto_medio_250m_grados']}°\n"
           f"Municipio de {mun['MUNICIPIO']}, % del área por amenaza (Mapa Nacional 1:100.000) [F]: media {num(mun['SUM_MEDIA'])} · "
           f"alta {num(mun['SUM_ALTA'])} · muy alta {num(mun['SUM_MUY_AL'])}")
    txt = "\n".join(textwrap.fill(l, 108, subsequent_indent="   ") for l in txt.split("\n"))
    fig.text(xb, 0.425, txt, fontsize=8.9, va="top", color="#111827", linespacing=1.45)

ley = [Patch(fc=COL[k], ec=GRIS, lw=.4, alpha=.8, label=k.capitalize()) for k in ("Baja", "Media", "Alta", "Muy Alta")]
ley += [Line2D([], [], marker="+", ms=12, mew=2, color=AZUL, ls="none", label="Portal del OE 1 [CP]"),
        Line2D([], [], color=AZUL, ls="--", lw=1.1, label="Círculo de 3 km"),
        Line2D([], [], marker="^", ms=7, mfc="black", mec="white", ls="none", label="Movimiento en masa inventariado (SIMMA)")]
ley += dibujar_via(fig.add_axes([0, 0, 0.001, 0.001], visible=False))[:1]
fig.legend(handles=ley, loc="lower center", bbox_to_anchor=(0.5, 0.17), ncol=8, fontsize=8.6, frameon=False, handlelength=1.6)

nota = ("Fuentes [F]: Servicio Geológico Colombiano, SIMMA — Zonificación de susceptibilidad (capa 20) y de amenaza relativa por movimientos en masa (capa 15), escala 1:100.000, planchas 244 y 243; "
        "inventario de movimientos en masa; Mapa Nacional de Amenaza por Movimientos en Masa 1:100.000. Relieve: Copernicus DEM GLO-30 (sombreado, sol a 315°/45°). "
        "Geometrías generalizadas por el servidor a 0,0001° (≈ 11 m), muy por debajo del error de la escala 1:100.000. " + FUENTE_VIA + ".\n"
        "Lectura: la zonificación 1:100.000 sirve para ubicar el problema, no para diseñar; los dos portales quedan en clase media con zonas de amenaza alta a ≈ 0,3 km. "
        "Las condiciones del emboquille (espesor de suelo y saprolito, agua, discontinuidades) solo las resuelve la exploración de subsuelo.\n"
        "Scripts: descargar_capas_mapa_OE3.py · consulta_amenaza_mm_OE3.py · pendiente_portales_OE3.py · via_actual_ruta40.py · mapa_susceptibilidad_OE3.py. Servicios consultados el "
        + a["consultado"][:10] + ". Elaborado con apoyo de IA (Claude) y verificado contra las fuentes citadas.")
fig.add_artist(Line2D([0.015, 0.985], [0.12, 0.12], color=VERDE, lw=1))
fig.text(0.02, 0.11, "\n".join(textwrap.fill(l, 235) for l in nota.split("\n")), fontsize=8.2, va="top", color=GRIS, linespacing=1.5)
os.makedirs(os.path.join(RAIZ, "Visuales"), exist_ok=True)
base = os.path.join(RAIZ, "Visuales", "mapa_susceptibilidad_OE3")
fig.savefig(base + ".png", dpi=200); fig.savefig(base + ".pdf")
Image.open(base + ".png").convert("RGB").save(base + ".jpg", quality=92)
print("ok", base)
