# -*- coding: utf-8 -*-
"""OE 3 · Act 1 — Lámina «Geología en los portales» (A3 apaisado, PNG 200 ppp + PDF).

No escribe cifras a mano: lee
  Act1_Cartografia/ubicacion_portales_planchas_OE3.json  (escala de los recortes)
  Act1_Cartografia/consulta_sgc_portales_OE3.json        (unidad 1:1 M, fallas, NSR-10, U–Pb)
  Act2_Amenaza/consulta_amenaza_mm_OE3.json               (amenaza 1:100 k, inventario SIMMA)
y los recortes portal_24x_recorte.png que genera ubicar_portales_planchas_OE3.py.
Las descripciones de unidad en el punto son lectura de la leyenda impresa de cada plancha [F].
Ejecutar desde OE3_Geotecnia/:  python Act1_Cartografia/lamina_portales_OE3.py
"""
import json, os, textwrap
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow, Rectangle
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI); REPO = os.path.dirname(RAIZ)
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))
ubi = J(AQUI, "ubicacion_portales_planchas_OE3.json")
sgc = J(AQUI, "consulta_sgc_portales_OE3.json")["portales"]
amz = J(RAIZ, "Act2_Amenaza", "consulta_amenaza_mm_OE3.json")["portales"]
VERDE, AZUL, GRIS = "#178E2C", "#193F77", "#475569"
num = lambda x, d=1: f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")

PANELES = [
    ("244", "oriental_Ibague", "Portal oriental — Ibagué, Tolima (DANE 73001)",
     "Plancha 244 Ibagué, 1:100.000 (Mosquera, Núñez y Vesga, 1982; SGC)",
     "Contacto PCAn / Jcdi: Neises y Anfibolitas de Tierradentro (neises cuarzo-feldespático-\n"
     "biotíticos, anfibolitas) con el Batolito de Ibagué (granodiorita biotítico-hornbléndica, con variaciones a cuarzodiorita y cuarzomonzonita)"),
    ("243", "occidental_Calarca", "Portal occidental — Calarcá, Quindío (DANE 63130)",
     "Plancha 243 Armenia, 1:100.000 (McCourt et al., 1985; SGC)",
     "Borde de lente Kqv (Quebradagrande, miembro volcánico: diabasas y andesitas) dentro de\n"
     "Kqs (miembro sedimentario: grauvacas, lutitas, chert, calizas); TQa (Fm. Armenia) al W"),
]

fig = plt.figure(figsize=(16.54, 11.69))  # A3 apaisado
fig.patch.set_facecolor("white")
for f, rect in (("logo-unibague.png", [0.012, 0.905, 0.13, 0.08]), ("logo-geopav.png", [0.925, 0.905, 0.06, 0.08])):
    p = os.path.join(REPO, "public", f)
    if os.path.exists(p):
        ax = fig.add_axes(rect); ax.imshow(Image.open(p)); ax.axis("off")
fig.text(0.5, 0.955, "Geología en los emboquilles del túnel — OE 3, Actividad 1", ha="center", fontsize=20, color=VERDE, weight="bold")
fig.text(0.5, 0.925, "Ubicación de los portales del OE 1 sobre la cartografía geológica 1:100.000 del SGC · Semillero GEOPAV, Universidad de Ibagué · Paz y Región 2026B",
         ha="center", fontsize=10.5, color=AZUL)
fig.add_artist(plt.Line2D([0.015, 0.985], [0.895, 0.895], color=VERDE, lw=2))

for i, (pl, key, tit, fuente, unidad) in enumerate(PANELES):
    x0 = 0.03 + i * 0.49
    ax = fig.add_axes([x0, 0.33, 0.45, 0.54])
    im = Image.open(os.path.join(AQUI, f"portal_{pl}_recorte.png")); ax.imshow(im); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_color(GRIS)
    ax.set_title(tit, fontsize=13, color=AZUL, weight="bold", loc="left")
    kpx = ubi[pl]["px_por_km_recorte"]; w, h = im.size
    ax.add_patch(Rectangle((20, h - 70), kpx + 40, 55, color="white", alpha=.85))
    ax.plot([40, 40 + kpx], [h - 35, h - 35], color="black", lw=4)
    ax.text(40 + kpx / 2, h - 45, "1 km", ha="center", fontsize=10, weight="bold")
    ax.add_patch(Rectangle((w - 80, 15), 62, 90, color="white", alpha=.85))
    ax.add_patch(FancyArrow(w - 49, 85, 0, -50, width=6, head_width=22, head_length=18, color="black"))
    ax.text(w - 49, 100, "N", ha="center", fontsize=11, weight="bold")
    s, a = sgc[key], amz[key]
    fallas = "; ".join(f"{x['nombre']} {num(x['dist_km'])} km" for x in s["fallas_10km"][:3])
    nsr = s["nsr10"][0]
    cl = a["amenaza_100k_3km"]
    otras = ", ".join(f"{c} a {num(v['dist_m'] / 1000)} km ({num(v['area_pct'])} % del círculo de 3 km)"
                      for c, v in cl.items() if v["dist_m"] > 0)
    inv = a["inventario_simma_3km"]
    txt = (f"Unidad en el punto (plancha 1:100.000) [F]:\n{unidad}\n"
           f"Mapa Geológico de Colombia 2023 (1:1 M) [F]: {s['unidad_bajo_portal'][0]['SimboloUC']} — {s['unidad_bajo_portal'][0]['Edad']}\n"
           f"Fallas a ≤ 10 km (1:1 M) [CP]: {fallas}\n"
           f"NSR-10 [F]: Aa = {num(nsr['AA'], 2)} · Av = {num(nsr['AV'], 2)} · amenaza sísmica {nsr['ZONA_AMENAZA_SÍSMICA'].lower()}\n"
           f"Amenaza por movimientos en masa 1:100.000 [F]: {a['amenaza_100k_en_punto'][0]['CATAME'].lower()} en el punto; {otras} [CP]\n"
           f"Inventario SIMMA a 3 km [F]: {len(inv)} evento(s)" + (f", el más cercano a {num(inv[0]['dist_km'])} km ({inv[0]['SUBTIPO'].lower()})" if inv else ""))
    txt = "\n".join(textwrap.fill(l, 100, subsequent_indent="   ") for l in txt.split("\n"))
    fig.text(x0, 0.315, txt, fontsize=9.2, va="top", color="#111827", linespacing=1.45)
    fig.text(x0, 0.125, f"Fuente del recorte: {fuente}. Cruz roja: portal del OE 1 [CP].", fontsize=8.5, color=GRIS, style="italic")

nota = ("Método [CP]: la cuadrícula de 5 km del PDF de cada plancha se detecta y se calibra con sus rótulos de meridianos y paralelos; el portal se proyecta a MAGNA-SIRGAS "
        "(EPSG 3116 en la 244, 3115 en la 243). Precisión de ubicación ≈ ±0,1 km, más el error propio de la cartografía 1:100.000.\n"
        "Lectura: los dos portales, elegidos por criterio geométrico en el OE 1, caen sobre contactos litológicos; un corrimiento de unos cientos de metros cambia la roca del emboquille. "
        "Esta lámina no reemplaza la exploración de subsuelo.\n"
        "Scripts: consulta_sgc_portales_OE3.py · ubicar_portales_planchas_OE3.py · Act2_Amenaza/consulta_amenaza_mm_OE3.py · lamina_portales_OE3.py. "
        "Servicios ArcGIS REST del Servicio Geológico Colombiano, consultados el " + a["consultado"][:10] + ". "
        "Elaborado con apoyo de IA (Claude) y verificado contra las fuentes citadas.")
fig.add_artist(plt.Line2D([0.015, 0.985], [0.105, 0.105], color=VERDE, lw=1))
fig.text(0.02, 0.095, nota, fontsize=8.3, va="top", color=GRIS, wrap=True, linespacing=1.5)
os.makedirs(os.path.join(RAIZ, "Visuales"), exist_ok=True)
for ext, kw in (("png", {"dpi": 200}), ("pdf", {})):
    fig.savefig(os.path.join(RAIZ, "Visuales", f"lamina_portales_geologia_OE3.{ext}"), **kw)
print("ok")
