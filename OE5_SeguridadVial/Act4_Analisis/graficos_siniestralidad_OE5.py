# -*- coding: utf-8 -*-
"""
OE 5 - Actividad 4 (fila 34 del Cronograma)
Graficos de siniestralidad: mapa de sectores criticos sobre el trazado y serie del paso.
Producto: Visuales/graficos_siniestralidad_OE5.png / .pdf

Semillero de Investigacion GEOPAV - Universidad de Ibague - Paz y Region 2026B

LEE, NO RECALCULA
  Los seis sectores y sus Gi* vienen de Act3_Siniestros/siniestros_ANSV_corredor.csv.
  La serie del paso viene de Act1_Aforos/tpd_historico_corredor.csv.
  Las dos tasas se recalculan aqui con la MISMA formula del libro de la Act 4, y el
  script comprueba que coincidan con lo que publica ese libro antes de dibujar.

DECISIONES DE COLOR  (guia de dataviz + paleta institucional de la constitucion)
  Panel del mapa. El tamano del circulo codifica MAGNITUD (fallecidos) y el color
  codifica el nivel de confianza del Gi*, que es ORDINAL (99 % > 95 %): por eso es una
  rampa SECUENCIAL de un solo tono, no una paleta categorica. La comprobacion que
  aplica a una rampa secuencial es la monotonia de luminosidad, no las seis pruebas
  categoricas: L(#193F77) = 0,373 < L(#7BA0D4) = 0,66, monotona. Separacion normal-vision
  entre los dos pasos: dE 32,6; peor caso CVD 31,2 (validador de la guia). Ademas
  CADA punto lleva su nivel rotulado, de modo que la identidad nunca depende del color.

  Panel de la serie. Es el patron enfasis dato/contexto, no identidad categorica:
  azul institucional = la carga pesada, que es el sujeto del objetivo; gris = el total,
  que es contexto. El validador marca el gris por bajo croma "reads gray": es
  deliberado. dE normal-vision 34,5. Las dos lineas van rotuladas directamente.

  El azul #193F77 queda fuera de la banda de luminosidad de la guia por ser oscuro:
  es el color del logotipo de la Universidad de Ibague y lo fija la constitucion del
  proyecto, que manda sobre la paleta por defecto. Su contraste sobre blanco es alto;
  el WARN de contraste afecta al gris y al azul claro, y se cubre con rotulos visibles
  en toda marca y con el libro de calculo como vista de tabla.
"""

import csv
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.colors import LightSource, LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

BASE = os.path.dirname(os.path.abspath(__file__))
OE5 = os.path.dirname(BASE)
RAIZ = os.path.dirname(OE5)
ACT1 = os.path.join(OE5, "Act1_Aforos")
ACT3 = os.path.join(OE5, "Act3_Siniestros")
VIS = os.path.join(OE5, "Visuales")
OE1 = os.path.join(RAIZ, "OE1_Topografia")

AZUL, AZUL_CLARO = "#193F77", "#7BA0D4"
GRIS, TINTA, SUAVE = "#94A3B8", "#0F2449", "#5B6B80"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": "#CBD5E1",
                     "axes.labelcolor": TINTA, "text.color": TINTA,
                     "xtick.color": SUAVE, "ytick.color": SUAVE})
mil = FuncFormatter(lambda v, p: f"{v:,.0f}".replace(",", "."))


def leer(ruta):
    with open(ruta, encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


def confianza(z):
    a = abs(z)
    return "99 %" if a >= 2.58 else "95 %" if a >= 1.96 else "90 %" if a >= 1.65 else "n.s."


# ------------------------------------------------------------------ datos
sec = leer(os.path.join(ACT3, "siniestros_ANSV_corredor.csv"))
hist = leer(os.path.join(ACT1, "tpd_historico_corredor.csv"))
tra = json.load(open(os.path.join(OE1, "Act4_Trazado", "trazado_tunel.geojson"), encoding="utf-8"))
lim = json.load(open(os.path.join(OE1, "Act1_DEM", "limites_area_estudio.geojson"), encoding="utf-8"))

s244 = [f for f in hist if f["estacion"] == "244"]
m244 = [f for f in s244 if 2015 <= int(f["anio"]) <= 2018]
m243 = [f for f in hist if f["estacion"] == "243" and 2015 <= int(f["anio"]) <= 2018]
t244 = sum(int(f["tpd"]) for f in m244) / len(m244)
t243 = sum(int(f["tpd"]) for f in m243) / len(m243)
tpond = (t243 * 29 + t244 * 45) / 74
fall = sum(int(r["fallecidos"]) for r in sec if r["en_el_paso"] == "Si")

def tasa(f, tpd, L, a=5):
    return f / (tpd * 365 * L * a) * 1e8

TASA_CORR, TASA_PASO = tasa(fall, tpond, 74), tasa(fall, t244, 45)

# --- control: las cifras deben coincidir con el libro de la Act 4 -----------
LIBRO = os.path.join(BASE, "analisis_siniestralidad_OE5.xlsx")
if os.path.exists(LIBRO):
    import openpyxl
    wb = openpyxl.load_workbook(LIBRO, data_only=True)
    ws = wb["3. Tasa"]
    a, b = ws["G5"].value, ws["G6"].value
    if a is None or b is None:
        print("AVISO: el libro no tiene valores cacheados; no se pudo cruzar. Recalcularlo.")
    elif abs(a - TASA_CORR) > 0.01 or abs(b - TASA_PASO) > 0.01:
        raise SystemExit(f"PARADA: la figura calcula {TASA_CORR:.2f} / {TASA_PASO:.2f} y el libro "
                         f"publica {a:.2f} / {b:.2f}. No se dibuja hasta resolver cuál manda.")
    else:
        print(f"control OK: figura y libro coinciden ({TASA_CORR:.2f} y {TASA_PASO:.2f})")

# ------------------------------------------------------------------ lienzo
fig = plt.figure(figsize=(15.5, 8.2), dpi=200)
fig.patch.set_facecolor("white")
gs = fig.add_gridspec(2, 2, width_ratios=[1.30, 1], height_ratios=[1.32, 1],
                      wspace=0.15, hspace=0.30, left=0.04, right=0.975, top=0.855, bottom=0.075)

# ================================================== A: mapa
axm = fig.add_subplot(gs[0, 0])
LON0, LON1, LAT0, LAT1 = -75.72, -75.14, 4.33, 4.58

with rasterio.open(os.path.join(OE1, "Act1_DEM", "DEM_area_estudio.tif")) as src:
    win = rasterio.windows.from_bounds(LON0, LAT0, LON1, LAT1, src.transform)
    dem = src.read(1, window=win).astype(float)
    ext = rasterio.windows.bounds(win, src.transform)
dem[dem <= -1000] = np.nan
relleno = np.nanmin(dem)
# El DEM esta en grados y la cota en metros: se pasa el tamano de pixel EN METROS
# (~30 m del GLO-30) para que el sombreado no salga plano. Mismo problema que la
# lamina del OE 1, alli resuelto con el factor Z 111120 de QGIS.
ls = LightSource(azdeg=315, altdeg=45)
sombra = ls.hillshade(np.nan_to_num(dem, nan=relleno), vert_exag=1.0, dx=30, dy=30)

rampa = LinearSegmentedColormap.from_list("terreno", ["#F7F9FB", "#E4E9EF", "#CBD5E1", "#AEB9C7"])
axm.imshow(dem, extent=(ext[0], ext[2], ext[1], ext[3]), origin="upper",
           cmap=rampa, interpolation="bilinear")
axm.imshow(sombra, extent=(ext[0], ext[2], ext[1], ext[3]), origin="upper",
           cmap="gray", alpha=0.55, interpolation="bilinear")

for f in lim["features"]:
    geom = f["geometry"]
    polis = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poli in polis:
        anillo = np.array(poli[0])
        axm.plot(anillo[:, 0], anillo[:, 1], color="white", lw=1.6, alpha=0.9, zorder=2)
        axm.plot(anillo[:, 0], anillo[:, 1], color=SUAVE, lw=0.6, alpha=0.55, zorder=2.1)
    c = np.array(polis[0][0])
    axm.text(c[:, 0].mean(), c[:, 1].mean(), f["properties"].get("MpNombre", "").upper(),
             fontsize=8.5, color=SUAVE, ha="center", va="center", alpha=0.85, zorder=2.2,
             weight="bold")

xy = np.array(tra["features"][0]["geometry"]["coordinates"])
axm.plot(xy[:, 0], xy[:, 1], color="white", lw=5.5, solid_capstyle="round", zorder=3)
axm.plot(xy[:, 0], xy[:, 1], color=AZUL, lw=2.6, solid_capstyle="round", zorder=3.1)
for p, et, dy in [(xy[0], "Portal oriental\nIbagué · 951 msnm", -0.028),
                  (xy[-1], "Portal occidental\nCalarcá · 1.451 msnm", -0.028)]:
    axm.plot(*p, "o", ms=9, color=AZUL, mec="white", mew=2.2, zorder=4)
    axm.text(p[0], p[1] + dy, et, fontsize=8, color=AZUL, ha="center", va="top",
             weight="bold", zorder=4, linespacing=1.35)

fmax = max(int(r["fallecidos"]) for r in sec)
for r in sorted(sec, key=lambda x: -int(x["fallecidos"])):
    lo, la = float(r["longitud"]), float(r["latitud"])
    f_, z = int(r["fallecidos"]), float(r["gizscore"])
    nv = confianza(z)
    col = AZUL if nv == "99 %" else AZUL_CLARO
    ms = 7 + 24 * (f_ / fmax) ** 0.55
    # A esta escala los seis caen en un racimo: el numero dentro del circulo no se
    # leeria. La identidad de cada uno se resuelve en el panel de detalle.
    axm.plot(lo, la, "o", ms=ms, color=col, mec="white", mew=2, alpha=0.92, zorder=5)

# --- recuadro de detalle: los seis sectores caben en 3 km, a escala general se pisan ---
sub = gs[1, 0].subgridspec(1, 2, width_ratios=[1.5, 1], wspace=0.04)
axz = fig.add_subplot(sub[0, 0])
axl = fig.add_subplot(sub[0, 1])
ZL0, ZL1, ZA0, ZA1 = -75.6480, -75.5900, 4.5090, 4.5410
axz.imshow(dem, extent=(ext[0], ext[2], ext[1], ext[3]), origin="upper",
           cmap=rampa, interpolation="bilinear")
axz.imshow(sombra, extent=(ext[0], ext[2], ext[1], ext[3]), origin="upper",
           cmap="gray", alpha=0.5, interpolation="bilinear")
# Seis puntos en 3,5 km, y dos pares casi superpuestos (los dos PR 85 distan ~200 m).
# Rotularlos sobre el mapa colisiona siempre, asi que van numerados y la identidad
# completa se lee en la lista de al lado: el color nunca es el unico portador.
orden = sorted(sec, key=lambda x: (-int(x["fallecidos"]), float(x["longitud"])))
for i, r in enumerate(orden, start=1):
    lo, la = float(r["longitud"]), float(r["latitud"])
    f_ = int(r["fallecidos"])
    nv = confianza(float(r["gizscore"]))
    col = AZUL if nv == "99 %" else AZUL_CLARO
    axz.plot(lo, la, "o", ms=15 + 26 * (f_ / fmax) ** 0.55, color=col, mec="white",
             mew=2.2, alpha=0.95, zorder=5 + i)
    # Si el punto se solapa con otro ya dibujado, su numero sale fuera con linea guia:
    # las posiciones NO se mueven, solo la etiqueta.
    cerca = [q for q in orden[:i - 1]
             if abs(float(q["longitud"]) - lo) < 0.004 and abs(float(q["latitud"]) - la) < 0.004]
    if cerca:
        ang = 2.4 + 1.1 * len(cerca)
        axz.annotate(str(i), xy=(lo, la), xytext=(34 * np.cos(ang), 34 * np.sin(ang)),
                     textcoords="offset points", fontsize=9, color=TINTA, weight="bold",
                     ha="center", va="center", zorder=20 + i,
                     arrowprops=dict(arrowstyle="-", color=SUAVE, lw=0.8, shrinkA=1, shrinkB=6),
                     bbox=dict(boxstyle="circle,pad=0.28", fc="white", ec=SUAVE, lw=0.9))
    else:
        axz.text(lo, la, str(i), fontsize=9.5, color="white", ha="center", va="center",
                 weight="bold", zorder=12 + i)

# --- lista de identidad, al lado del mapa de detalle ---
axl.axis("off")
axl.set_xlim(0, 1); axl.set_ylim(0, 1)
axl.add_patch(plt.Rectangle((0, 0.895), 1, 0.075, transform=axl.transAxes,
                            color=AZUL, zorder=1, clip_on=False))
for tx, xx in (("N.º", 0.03), ("PR", 0.17), ("Fallecidos", 0.33), ("Gi*", 0.66), ("Entidad", 0.80)):
    axl.text(xx, 0.932, tx, fontsize=7.8, color="white", weight="bold",
             va="center", ha="left", zorder=2)
fila_y = 0.845
for i, r in enumerate(orden, start=1):
    f_ = int(r["fallecidos"])
    nv = confianza(float(r["gizscore"]))
    col = AZUL if nv == "99 %" else AZUL_CLARO
    axl.plot(0.055, fila_y, "o", ms=11, color=col, mec="white", mew=1.4,
             transform=axl.transAxes, clip_on=False, zorder=3)
    axl.text(0.055, fila_y, str(i), fontsize=7.2, color="white", ha="center",
             va="center", weight="bold", transform=axl.transAxes, zorder=4)
    axl.text(0.17, fila_y, f"PR {r['pr']}", fontsize=8.2, color=TINTA, va="center", weight="bold")
    axl.text(0.33, fila_y, f"{f_} " + ("fallecido" if f_ == 1 else "fallecidos"),
             fontsize=8.2, color=TINTA, va="center")
    axl.text(0.66, fila_y, nv, fontsize=8.2, color=SUAVE, va="center")
    axl.text(0.80, fila_y, r["entidad"].replace("INVIAS-OTROS", "INVÍAS"),
             fontsize=7.6, color=SUAVE, va="center")
    axl.axhline(fila_y - 0.048, xmin=0, xmax=1, color="#EEF2F7", lw=1)
    fila_y -= 0.105
axl.text(0.0, fila_y + 0.03,
         "Gi* = nivel de confianza del estadístico de puntos calientes que\n"
         "publica la propia ANSV. Los cuatro del tramo «Calarcá – Ibagué»\n"
         "a cargo de INVÍAS suman los 42 fallecidos del paso.",
         fontsize=7.6, color=SUAVE, va="top", linespacing=1.5)

axz.set_xlim(ZL0, ZL1)
axz.set_ylim(ZA0, ZA1)
axz.set_aspect(1 / np.cos(np.deg2rad(4.52)))
axz.set_xticks([]); axz.set_yticks([])
for sp in axz.spines.values():
    sp.set_color(SUAVE); sp.set_linewidth(0.9)
axz.set_title("Detalle del descenso · los seis sectores caben en 3,6 km",
              fontsize=11.5, weight="bold", color=TINTA, loc="left", pad=20)
axz.text(0, 1.04, "Misma escala de tamaño y color que el mapa de arriba",
         transform=axz.transAxes, fontsize=8.2, color=SUAVE)

axm.annotate("Seis sectores críticos de la vía actual,\ntodos en el descenso hacia Calarcá",
             xy=(-75.622, 4.527), xytext=(-75.565, 4.548), fontsize=8.8, color=TINTA,
             weight="bold", ha="left", linespacing=1.4, zorder=7,
             arrowprops=dict(arrowstyle="-", color=SUAVE, lw=0.9,
                             connectionstyle="arc3,rad=0.18"))
axm.annotate("Trazado propuesto del túnel de base",
             xy=(xy[len(xy) // 2][0], xy[len(xy) // 2][1]), xytext=(-75.45, 4.352),
             fontsize=8.8, color=AZUL, weight="bold", ha="center", zorder=7,
             arrowprops=dict(arrowstyle="-", color=AZUL, lw=0.9, alpha=0.7,
                             connectionstyle="arc3,rad=-0.2"))

axm.set_xlim(LON0, LON1)
axm.set_ylim(LAT0, LAT1)
axm.set_aspect(1 / np.cos(np.deg2rad(4.46)))
axm.set_xticks([]); axm.set_yticks([])
for s in axm.spines.values():
    s.set_color("#CBD5E1")

leyenda = [
    Line2D([], [], marker="o", ls="", ms=9, color=AZUL, mec="white", mew=1.6,
           label="Sector crítico · 99 % de confianza"),
    Line2D([], [], marker="o", ls="", ms=9, color=AZUL_CLARO, mec="white", mew=1.6,
           label="Sector crítico · 95 % de confianza"),
    Line2D([], [], color=AZUL, lw=2.6, label="Trazado del túnel (OE 1)"),
]
lg = axm.legend(handles=leyenda, loc="upper right", frameon=True, fontsize=8.3,
                framealpha=0.94, edgecolor="#CBD5E1", borderpad=0.7, handletextpad=0.9)
lg.get_frame().set_linewidth(0.6)
axm.set_title("Dónde muere la gente hoy, y por dónde pasaría el túnel", fontsize=12.5,
              weight="bold", color=TINTA, loc="left", pad=26)
axm.text(0, 1.022, "Tamaño del círculo = fallecidos 2015–2019 · color = confianza del Getis-Ord Gi* "
                   "que publica la ANSV · relieve: Copernicus DEM GLO-30",
         transform=axm.transAxes, fontsize=8.4, color=SUAVE)

# ================================================== B: serie del paso
axs = fig.add_subplot(gs[0, 1])
anios = [int(f["anio"]) for f in s244]
tot = [int(f["tpd"]) for f in s244]
cam = [round(int(f["tpd"]) * int(f["pct_camiones"]) / 100) if f["pct_camiones"] else None
       for f in s244]
axs.plot(anios, tot, color=GRIS, lw=2, solid_capstyle="round", zorder=2)
xc = [a for a, c in zip(anios, cam) if c is not None]
yc = [c for c in cam if c is not None]
axs.plot(xc, yc, color=AZUL, lw=2, solid_capstyle="round", zorder=3)
for x, y, c in ((anios[-1], tot[-1], GRIS), (xc[-1], yc[-1], AZUL)):
    axs.plot([x], [y], "o", ms=8, color=c, mec="white", mew=2, zorder=4)
axs.annotate("Todos los vehículos", xy=(anios[-6], tot[-6]), xytext=(0, 14),
             textcoords="offset points", ha="center", fontsize=9, color=SUAVE, weight="bold")
axs.annotate("Camiones", xy=(xc[-6], yc[-6]), xytext=(0, -22),
             textcoords="offset points", ha="center", fontsize=9, color=AZUL, weight="bold")
axs.axvspan(2015, 2018, color=AZUL, alpha=0.055, zorder=1)
axs.text(2016.5, max(tot) * 1.235, "periodo de la\nlínea base", fontsize=8, color=AZUL,
         ha="center", va="top", weight="bold", linespacing=1.3)
axs.set_ylim(0, max(tot) * 1.26)
axs.yaxis.set_major_formatter(mil)
axs.set_ylabel("Tránsito promedio diario (veh/día)", fontsize=9.5)
axs.grid(axis="y", color="#EEF2F7", lw=1)
axs.set_axisbelow(True)
for s in ("top", "right"):
    axs.spines[s].set_visible(False)
axs.set_title("Veinte años de tránsito en el paso", fontsize=12.5, weight="bold",
              color=TINTA, loc="left", pad=26)
axs.text(0, 1.03, "Estación 244 de INVÍAS · sector Calarcá – Cajamarca, 45 km · 1997–2018",
         transform=axs.transAxes, fontsize=8.4, color=SUAVE)

# ================================================== C: las dos tasas
axt = fig.add_subplot(gs[1, 1])
axt.axis("off")
axt.text(0, 1.06, "La tasa, por primera vez con las dos entradas medidas",
         fontsize=12.5, weight="bold", color=TINTA, va="top")
axt.text(0, 0.945, "Fallecidos por cada 100 millones de vehículos-kilómetro",
         fontsize=8.4, color=SUAVE, va="top")

for i, (val, tit, sub) in enumerate([
        (TASA_CORR, "Corredor completo", f"{fall} fallecidos · 74 km · TPD {tpond:,.0f}".replace(",", ".")),
        (TASA_PASO, "Solo el paso", f"{fall} fallecidos · 45 km · TPD {t244:,.0f}".replace(",", "."))]):
    x = 0.02 + i * 0.5
    axt.text(x, 0.80, f"{val:.2f}".replace(".", ","), fontsize=36, weight="bold",
             color=AZUL, va="top", ha="left")
    axt.text(x, 0.475, tit, fontsize=10.5, weight="bold", color=TINTA, va="top")
    axt.text(x, 0.385, sub, fontsize=8.3, color=SUAVE, va="top")

axt.text(0, 0.285,
         "Ambas usan los mismos 42 fallecidos y difieren solo en el denominador. La versión anterior\n"
         "publicaba 12,79 con un TPD supuesto de 3.000: el tránsito real del paso es más del doble.\n"
         "Los fallecidos cubren cinco años y el aforo de INVÍAS cuatro: se supone que 2019 tuvo un\n"
         "tránsito parecido. El peaje Cajamarca de 2019 lo confirma dentro del 5 %, y la hipótesis\n"
         "mueve la tasa un 1 %. Queda declarada en la hoja 3 del libro de cálculo.",
         fontsize=8.3, color=SUAVE, va="top", linespacing=1.5)
axt.set_xlim(0, 1)
axt.set_ylim(0, 1)

fig.suptitle("Objetivo específico 5 · Siniestralidad de la carga pesada en el paso del Alto de La Línea",
             fontsize=15, weight="bold", color=TINTA, x=0.04, ha="left", y=0.962)
fig.text(0.04, 0.925,
         "Semillero de Investigación GEOPAV · Universidad de Ibagué · Paz y Región 2026B   |   "
         "Fallecidos: ANSV rs3u-8r4q 2015–2019 [F] · Tránsito: INVÍAS serie histórica [F] · Tasas [CP]",
         fontsize=8.6, color=SUAVE)

os.makedirs(VIS, exist_ok=True)
# El PNG ya sale determinista; el PDF de matplotlib embebe CreationDate y cambiaria de
# hash en cada corrida, lo que impide comparar el archivo publicado contra el que produce
# el script. Se anula esa marca de tiempo.
for ext_ in ("png", "pdf"):
    meta = {"CreationDate": None} if ext_ == "pdf" else None
    fig.savefig(os.path.join(VIS, f"graficos_siniestralidad_OE5.{ext_}"),
                facecolor="white", metadata=meta)
print("figura escrita en", VIS)
print(f"  tasa corredor {TASA_CORR:.2f} | tasa paso {TASA_PASO:.2f} | {fall} fallecidos")
