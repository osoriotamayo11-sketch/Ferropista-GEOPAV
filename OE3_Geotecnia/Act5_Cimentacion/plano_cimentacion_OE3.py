# -*- coding: utf-8 -*-
"""
OE 3 · Actividad 5 — Paso 2 de 3: PLANO del esquema de cimentación de las terminales Ro-Ro.

Lee cimentacion_conceptual_OE3.json (paso 1) y dibuja UNA sola geometría hacia dos salidas:
  - Plano_cimentacion_terminales_OE3.dxf  (abre en AutoCAD; unidades en metros, capas por elemento)
  - ../Visuales/plano_cimentacion_terminales_OE3.pdf / .png  (lámina con Comun/lamina_institucional.py)
Ninguna dimensión geotécnica se escribe a mano: anchos B de zapata, cargas y rampa salen del JSON.
Requiere ezdxf y matplotlib.
"""
import json
import os
import sys

import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

AQUI = os.path.dirname(os.path.abspath(__file__))
OE3 = os.path.dirname(AQUI)
RAIZ = os.path.dirname(OE3)
sys.path.insert(0, os.path.join(RAIZ, "Comun"))
from lamina_institucional import encabezado, pie, VERDE, AZUL, GRIS  # noqa: E402

D = json.load(open(os.path.join(AQUI, "cimentacion_conceptual_OE3.json"), encoding="utf-8"))
HY = {k: v["valor"] for k, v in D["hipotesis"].items()}
DXF_OUT = os.path.join(AQUI, "Plano_cimentacion_terminales_OE3.dxf")
VIS = os.path.join(OE3, "Visuales")
os.makedirs(VIS, exist_ok=True)


def es(v, d=2):
    return f"{v:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def B_adoptado(z, suelo):
    for r in D["zapatas"]:
        if r["zapata"] == z and r["suelo"] == suelo and r["caso"] == "Típico" and r["nf"] == "NF en la base":
            return r["B_m"]
    raise SystemExit(f"DETENIDO: sin B típico para {z} {suelo}")


BZ = {(z, s): B_adoptado(z, s) for z in ("Z-1", "Z-2") for s in ("S1", "S2")}
HZ = {z: D["cargas"][z]["h_m"] for z in ("Z-1", "Z-2")}
DF = D["constantes"]["Df_m"]
PED = 0.40  # pedestal [H]

# ------------------------------------------------------------------ primitivas comunes
class Dibujo:
    def __init__(self):
        self.vistas = {}

    def vista(self, nombre):
        self.vistas[nombre] = []
        self.act = self.vistas[nombre]

    def linea(self, p, q, capa, ls="-"):
        self.act.append(("L", p, q, capa, ls))

    def rect(self, x, y, w, h, capa, relleno=None):
        self.act.append(("R", x, y, w, h, capa, relleno))

    def poli(self, pts, capa, relleno=None):
        self.act.append(("P", pts, capa, relleno))

    def texto(self, x, y, t, h, capa, ha="left"):
        self.act.append(("T", x, y, t, h, capa, ha))

    def cota(self, p, q, off, t, capa="COTAS"):
        self.act.append(("C", p, q, off, t, capa))


COL = {"VIA": "#6B7280", "MARQUESINA": AZUL, "ZAPATAS": VERDE, "EDIFICIO": "#7C3AED", "RAMPA": "#B45309",
       "TERRENO": "#8B6B4A", "CONCRETO": "#475569", "COTAS": "#111827", "TEXTO": "#111827"}
ACI = {"VIA": 8, "MARQUESINA": 5, "ZAPATAS": 3, "EDIFICIO": 6, "RAMPA": 30, "TERRENO": 32, "CONCRETO": 250, "COTAS": 7, "TEXTO": 7}

d = Dibujo()
L = HY["anden_longitud_m"]; luz = HY["marquesina_luz_m"]; sep = HY["marquesina_separacion_m"]
Lr = D["rampa"]["longitud_m"]; ar = HY["rampa_ancho_m"]
Ex, Ey = HY["edificio_planta_m"]; le = HY["edificio_luz_m"]

# Vista A — planta general (esquemática)
d.vista("A")
for yv in (-0.72, 0.72):
    d.linea((-Lr - 30, yv), (L + Lr + 30, yv), "VIA")
d.rect(0, -luz / 2, L, luz, "MARQUESINA")
for i in range(int(L / sep) + 1):
    for ys in (-luz / 2, luz / 2):
        d.rect(i * sep - 0.5, ys - 0.5, 1.0, 1.0, "ZAPATAS", "Z")
for x0, sgn in ((0, -1), (L, 1)):
    xa, xb = (x0 - Lr, x0) if sgn < 0 else (x0, x0 + Lr)
    d.rect(xa, -ar / 2, xb - xa, ar, "RAMPA", "R")
d.rect(30, luz / 2 + 14, Ex, Ey, "EDIFICIO")
for i in range(int(Ex / le) + 1):
    for k in range(int(Ey / le) + 1):
        d.rect(30 + i * le - 1.25, luz / 2 + 14 + k * le - 1.25, 2.5, 2.5, "ZAPATAS", "Z")
d.linea((-Lr - 30, -luz / 2 - 12), (L + Lr + 30, -luz / 2 - 12), "VIA", "--")
d.texto(L / 2, luz / 2 + 6, f"MARQUESINA METÁLICA · {int(L)} m × {es(luz, 0)} m · pórticos cada {es(sep, 0)} m · zapatas Z-1", 5, "TEXTO", "center")
d.texto(30 + Ex + 4, luz / 2 + 14 + Ey / 2, f"EDIFICIO DE CONTROL {es(Ex, 0)} × {es(Ey, 0)} m\nzapatas Z-2", 4, "TEXTO")
d.texto(-Lr / 2, -ar / 2 - 7, "RAMPA R-1", 5, "TEXTO", "center")
d.texto(L + Lr / 2, -ar / 2 - 7, "RAMPA R-1", 5, "TEXTO", "center")
d.texto(L / 2, -luz / 2 - 7, "Vía de acceso y cola de tractomulas (esquemática)", 5, "TEXTO", "center")
d.texto(L / 2, 1.8, "Vía férrea", 3, "TEXTO", "center")
d.cota((0, -luz / 2 - 25), (L, -luz / 2 - 24), 0, f"{int(L)} m (tren de hasta 750 m [F, dia. 23])")


def zapata(nombre, z):
    h = HZ[z]
    b1, b2 = BZ[(z, "S1")], BZ[(z, "S2")]
    b = max(b1, b2)
    d.vista(nombre)
    # planta (izquierda)
    d.rect(-b / 2, -b / 2, b, b, "ZAPATAS")
    if b1 != b2:
        bm = min(b1, b2)
        d.rect(-bm / 2, -bm / 2, bm, bm, "ZAPATAS")
    d.rect(-PED / 2, -PED / 2, PED, PED, "CONCRETO", "C")
    d.cota((-b / 2, -b / 2 - 0.35), (b / 2, -b / 2 - 0.35), 0, "B (ver cuadro)")
    d.texto(0, b / 2 + 0.35, "PLANTA", 0.22, "TEXTO", "center")
    # corte (derecha)
    ox = b + 1.6
    d.linea((ox - b / 2 - 0.8, 0), (ox + b / 2 + 0.8, 0), "TERRENO")
    d.rect(ox - b / 2, -DF, b, h, "CONCRETO", "C")
    d.rect(ox - PED / 2, -DF + h, PED, DF - h + 0.3, "CONCRETO", "C")
    d.rect(ox - b / 2, -DF - 0.10, b, 0.10, "TERRENO", "S")
    d.cota((ox + b / 2 + 0.35, -DF), (ox + b / 2 + 0.35, 0), 0, f"Df = {es(DF, 2)} m")
    d.cota((ox - b / 2 - 0.35, -DF), (ox - b / 2 - 0.35, -DF + h), -1, f"h = {es(h, 2)} m")
    d.texto(ox, 0.55, "CORTE", 0.22, "TEXTO", "center")
    d.texto(ox, -DF - 0.45, "Solado 0,10 m · suelo S1/S2", 0.16, "TEXTO", "center")


zapata("Z1", "Z-1")
zapata("Z2", "Z-2")

# Vista R — corte longitudinal de la rampa
d.vista("R")
hr = HY["rampa_altura_m"]; el = HY["rampa_losa_m"]; eb = HY["rampa_base_m"]
d.linea((-4, 0), (Lr + 6, 0), "TERRENO")
d.poli([(0, 0), (Lr, hr), (Lr + 4, hr), (Lr + 4, 0)], "RAMPA", "R")
d.poli([(0, 0), (Lr, hr), (Lr + 4, hr), (Lr + 4, hr - el), (Lr, hr - el), (0, -el)], "CONCRETO", "C")
d.poli([(0, -el), (Lr, hr - el), (Lr + 4, hr - el), (Lr + 4, hr - el - eb), (Lr, hr - el - eb), (0, -el - eb)], "TERRENO", "S")
d.cota((0, -1.1), (Lr, -1.1), 0, f"{es(Lr, 1)} m · pendiente {es(HY['rampa_pendiente'] * 100, 0)} %")
d.cota((Lr + 4.6, 0), (Lr + 4.6, hr), 0, f"{es(hr, 2)} m")
d.texto(Lr / 2 - 1, 1.5, f"Losa {es(el, 2)} m sobre base granular {es(eb, 2)} m (relleno compactado)", 0.35, "TEXTO", "center")
d.texto(Lr + 2, hr + 0.4, "Plataforma del vagón", 0.3, "TEXTO", "center")

# ------------------------------------------------------------------ cuadro y notas (texto, compartido)
cuadro = [("Elemento", "Estructura", "P servicio (kN)", "B oriental S1 (m)", "B occidental S2 (m)", "h (m)")]
for z in ("Z-1", "Z-2"):
    cg = D["cargas"][z]
    cuadro.append((z, cg["estructura"].split(" (")[0], es(cg["P_kN"], 0), es(BZ[(z, "S1")], 1), es(BZ[(z, "S2")], 1), es(HZ[z], 2)))
cuadro.append(("R-1", "Rampa de tractomulas (3S3)", f"{es(D['rampa']['q_total_kPa'], 0)} kPa", "losa sobre terreno", "losa sobre terreno", es(el, 2)))
NOTAS = [
    "ESQUEMA CONCEPTUAL, NO APTO PARA CONSTRUCCIÓN. Parámetros del suelo análogos (Act 3) y admisible como rango (Act 4).",
    "B adoptado = caso típico con NF en la base; zapatas cuadradas, carga centrada; Df y ρadm = 25 mm de la Act 4.",
    "Con los parámetros MÍNIMOS ninguna zapata aislada ≤ 6 m sirve para el edificio y la rampa exige sustituir el suelo: la exploración (NSR-10 H.3) decide.",
    "No incluye viento (NSR-10 B.6), que puede gobernar el arranque de la marquesina, ni el diseño estructural (NSR-10 C.15).",
]


# ------------------------------------------------------------------ salida DXF
doc = ezdxf.new("R2010", setup=True)
doc.units = ezdxf.units.M
for capa, aci in ACI.items():
    doc.layers.add(capa, color=aci)
msp = doc.modelspace()
ORIG = {"A": (0, 0), "Z1": (0, -90), "Z2": (20, -90), "R": (45, -90)}
for nom, prims in d.vistas.items():
    ox, oy = ORIG[nom]
    for p in prims:
        t = p[0]
        if t == "L":
            _, a, b, capa, ls = p
            msp.add_line((a[0] + ox, a[1] + oy), (b[0] + ox, b[1] + oy), dxfattribs={"layer": capa, "linetype": "DASHED" if ls == "--" else "CONTINUOUS"})
        elif t == "R":
            _, x, y, w, h, capa, rel = p
            pts = [(x + ox, y + oy), (x + w + ox, y + oy), (x + w + ox, y + h + oy), (x + ox, y + h + oy)]
            msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": capa})
            if rel:
                hat = msp.add_hatch(color=ACI[capa], dxfattribs={"layer": capa})
                hat.paths.add_polyline_path(pts, is_closed=True)
                if rel in ("C", "S"):
                    hat.set_pattern_fill("ANSI31" if rel == "C" else "AR-SAND", scale=0.05)
        elif t == "P":
            _, pts, capa, rel = p
            pts2 = [(a + ox, b + oy) for a, b in pts]
            msp.add_lwpolyline(pts2, close=True, dxfattribs={"layer": capa})
        elif t == "T":
            _, x, y, s, h, capa, ha = p
            al = {"left": ezdxf.enums.TextEntityAlignment.LEFT, "center": ezdxf.enums.TextEntityAlignment.CENTER}[ha]
            msp.add_text(s, height=h, dxfattribs={"layer": capa}).set_placement((x + ox, y + oy), align=al)
        elif t == "C":
            _, a, b, off, s, capa = p
            dim = msp.add_aligned_dim(p1=(a[0] + ox, a[1] + oy), p2=(b[0] + ox, b[1] + oy), distance=0.2,
                                      text=s, dxfattribs={"layer": capa}, override={"dimtxt": 0.18 if nom != "A" else 3, "dimasz": 0.12 if nom != "A" else 2})
            dim.render()
# cuadro y notas en el DXF
y = -110
msp.add_text("CUADRO DE CIMENTACIONES", height=0.8, dxfattribs={"layer": "TEXTO"}).set_placement((0, y))
for fila in cuadro:
    y -= 1.2
    msp.add_text("   |   ".join(fila), height=0.5, dxfattribs={"layer": "TEXTO"}).set_placement((0, y))
y -= 2
for n in NOTAS:
    y -= 1.0
    msp.add_text(n, height=0.45, dxfattribs={"layer": "TEXTO"}).set_placement((0, y))
msp.add_text("Semillero GEOPAV · Universidad de Ibagué · Ferropista · OE 3 Act 5 · Plano conceptual de cimentación de las terminales Ro-Ro · Unidades: m",
             height=0.6, dxfattribs={"layer": "TEXTO"}).set_placement((0, y - 2))
doc.header["$INSUNITS"] = 6
doc.saveas(DXF_OUT)
print("DXF:", DXF_OUT)

# ------------------------------------------------------------------ salida lámina (matplotlib)
HATCH = {"Z": None, "R": None, "C": "////", "S": "...."}


def pintar(ax, nom, recorte=None, fs_esc=1.0):
    for p in d.vistas[nom]:
        t = p[0]
        if t == "L":
            _, a, b, capa, ls = p
            ax.plot([a[0], b[0]], [a[1], b[1]], color=COL[capa], lw=0.9, ls=ls)
        elif t == "R":
            _, x, y, w, h, capa, rel = p
            fc = {"Z": COL[capa], "R": "#FDE7C8"}.get(rel, "none")
            ax.add_patch(Rectangle((x, y), w, h, fill=fc != "none", facecolor=fc, edgecolor=COL[capa], lw=0.9, hatch=HATCH.get(rel)))
        elif t == "P":
            _, pts, capa, rel = p
            fc = {"R": "#FDE7C8"}.get(rel, "none")
            ax.add_patch(Polygon(pts, closed=True, fill=fc != "none", facecolor=fc, edgecolor=COL[capa], lw=0.9, hatch=HATCH.get(rel)))
        elif t == "T":
            _, x, y, s, h, capa, ha = p
            ax.text(x, y, s, fontsize=7 * fs_esc, ha=ha, va="center", color=COL[capa], clip_on=True)
        elif t == "C":
            _, a, b, off, s, capa = p
            ax.annotate("", a, b, arrowprops=dict(arrowstyle="<->", lw=0.7, color=COL[capa]))
            vert = abs(a[0] - b[0]) < 1e-9
            izq = vert and off < 0
            ax.text((a[0] + b[0]) / 2 + ((-0.08 if izq else 0.08) if vert else 0), (a[1] + b[1]) / 2 + (0 if vert else 0.06 * (1 if nom != "A" else 30)),
                    s, fontsize=6.3 * fs_esc, ha=("right" if izq else "left") if vert else "center", va="center" if vert else "bottom", color=COL[capa])
    ax.set_aspect("equal")
    ax.axis("off")
    if recorte:
        ax.set_xlim(*recorte[0]); ax.set_ylim(*recorte[1])
    else:
        ax.autoscale_view()


fig = plt.figure(figsize=(16.54, 11.69))  # A3 apaisado
top = encabezado(fig, "Esquema conceptual de cimentación de las terminales Ro-Ro",
                 "OE 3 · Actividad 5 — Zapatas aisladas de la marquesina y del edificio de control, y rampa de tractomulas (portales de Ibagué y Calarcá)")
bot = pie(fig, "Fuentes: cargas NSR-10 Título B (tablas B.3.2-1, B.3.4.1-4, B.3.4.3-1, B.4.2.1-1, B.4.2.1-2) [F]; tractomula 3S3 y eje trídem, "
               "Resolución 4100 de 2004 del Ministerio de Transporte, arts. 8 y 9 [F]; longitud del tren, ponencia Fernández (2025) dia. 23 [F]; "
               "capacidad admisible de la memoria de la Act 4 (Meyerhof, NSR-10 H.4) [CP]; geometría de estructuras [H]. "
               "Script: OE3_Geotecnia/Act5_Cimentacion/plano_cimentacion_OE3.py (lee cimentacion_conceptual_OE3.json). Archivo AutoCAD: Plano_cimentacion_terminales_OE3.dxf. "
               "Elaborado con apoyo de IA (Claude) y verificado.")
H_ = top - bot
ax1 = fig.add_axes([0.02, bot + H_ * 0.70, 0.96, H_ * 0.28]); pintar(ax1, "A", recorte=((-Lr - 32, L + Lr + 32), (-luz / 2 - 30, luz / 2 + 40)), fs_esc=1.1)
ax1.set_title("A. Planta general esquemática de una terminal (misma disposición en los dos portales)", fontsize=10, color=AZUL, loc="left")
ax1b = fig.add_axes([0.02, bot + H_ * 0.38, 0.40, H_ * 0.30]); pintar(ax1b, "A", recorte=((-Lr - 3, 100), (-luz / 2 - 20, luz / 2 + 36)), fs_esc=1.0)
ax1b.set_title("A'. Detalle del extremo de la terminal (rampa, primeros pórticos y edificio)", fontsize=10, color=AZUL, loc="left")
ax2 = fig.add_axes([0.44, bot + H_ * 0.38, 0.26, H_ * 0.30]); pintar(ax2, "Z1")
ax2.set_title("B. Zapata Z-1 (marquesina)", fontsize=10, color=AZUL, loc="left")
ax3 = fig.add_axes([0.72, bot + H_ * 0.38, 0.27, H_ * 0.30]); pintar(ax3, "Z2")
ax3.set_title("C. Zapata Z-2 (edificio de control)", fontsize=10, color=AZUL, loc="left")
ax4 = fig.add_axes([0.02, bot + H_ * 0.03, 0.40, H_ * 0.30]); pintar(ax4, "R", recorte=((-4, Lr + 7), (-1.8, 2.2)))
ax4.set_title("D. Corte longitudinal de la rampa R-1", fontsize=10, color=AZUL, loc="left")
ax5 = fig.add_axes([0.44, bot + H_ * 0.03, 0.55, H_ * 0.31]); ax5.axis("off")
tb = ax5.table(cellText=cuadro[1:], colLabels=cuadro[0], loc="upper left", cellLoc="left", colWidths=[0.07, 0.36, 0.13, 0.15, 0.16, 0.07])
tb.auto_set_font_size(False); tb.set_fontsize(7.6); tb.scale(1, 1.45)
for (r, c), cel in tb.get_celld().items():
    cel.set_edgecolor("#CBD5E1")
    if r == 0:
        cel.set_facecolor(AZUL); cel.get_text().set_color("white"); cel.get_text().set_weight("bold")
ax5.set_title("E. Cuadro de cimentaciones (caso típico, NF en la base)", fontsize=10, color=AZUL, loc="left")
for i, n in enumerate(NOTAS):
    ax5.text(0, 0.36 - i * 0.085, f"{i + 1}. {n}", fontsize=7.6, color="#9A3412" if i in (0, 2) else GRIS, transform=ax5.transAxes, wrap=True)
for ext in ("pdf", "png"):
    fig.savefig(os.path.join(VIS, f"plano_cimentacion_terminales_OE3.{ext}"), dpi=200 if ext == "png" else None)
print("lámina:", os.path.join(VIS, "plano_cimentacion_terminales_OE3.pdf"))
