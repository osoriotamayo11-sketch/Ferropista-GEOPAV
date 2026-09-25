# -*- coding: utf-8 -*-
"""
OE 5 - Actividad 4 (fila 34) - Densidad lineal de siniestros georreferenciados por la ANSV
y tasa post-tunel del paso como COTA INFERIOR.
Semillero de Investigacion GEOPAV - Universidad de Ibague - Paz y Region 2026B

LEE, NO RECALCULA LO QUE YA CALCULO OTRO SCRIPT
  Hechos y abscisas: Act3_Siniestros/microdato_ANSV_hechos.csv y cruce_prensa_ANSV.csv
  (procesar_microdato_ANSV_OE5.py). TPD: Act1_Aforos. Trazado y DEM: OE 1.

POR QUE UNA DENSIDAD LINEAL Y NO UN MAPA DE CALOR 2D
  Una carretera es una linea: un KDE en dos dimensiones reparte densidad sobre el monte.
  Aqui la densidad se estima sobre la abscisa de la Ruta 4003 (km = PR + distancia/1000).
  [H] Nucleo gaussiano, ancho de banda 1,5 km; cada HECHO pesa 1 (no cada victima: un solo
  bus con 24 lesionados dominaria la figura).

ADVERTENCIA QUE LA FIGURA LLEVA ESCRITA
  El anexo solo trae lo que la ANSV pudo georreferenciar desde el campo de direccion de
  Medicina Legal. De 8 siniestros fatales de prensa 2022-2025 en el corredor, solo 2 estan.
  La figura muestra donde se pudo georreferenciar, no donde esta el riesgo.

TASA POST-TUNEL (formula del libro de la Act 4): f / (TPD * 365 * L * anios) * 1e8
  f = fallecidos del anexo en el paso, 2021-2025 (anios completos). L = 45 km (est. 244).
  [H] No hay aforo del paso posterior a 2019: se usan dos TPD, media 2015-2018 de la
  estacion 244 y peaje Cajamarca 2019. Es COTA INFERIOR por subregistro. No se compara
  con 7,66 (2015-2019): otra fuente (sectores criticos) y otro criterio.
"""
import csv, json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.colors import LightSource, LinearSegmentedColormap

BASE = os.path.dirname(os.path.abspath(__file__))
OE5 = os.path.dirname(BASE); RAIZ = os.path.dirname(OE5)
ACT1 = os.path.join(OE5, "Act1_Aforos"); ACT3 = os.path.join(OE5, "Act3_Siniestros")
VIS = os.path.join(OE5, "Visuales"); OE1 = os.path.join(RAIZ, "OE1_Topografia")

AZUL, AZUL_CLARO = "#193F77", "#7BA0D4"
GRIS, TINTA, SUAVE = "#94A3B8", "#0F2449", "#5B6B80"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": "#CBD5E1",
                     "axes.labelcolor": TINTA, "text.color": TINTA,
                     "xtick.color": SUAVE, "ytick.color": SUAVE})
es = lambda v, d=0: f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def leer(ruta, sep=","):
    with open(ruta, encoding="utf-8-sig") as fh: return list(csv.DictReader(fh, delimiter=sep))

H = leer(os.path.join(ACT3, "microdato_ANSV_hechos.csv"))
for h in H:
    h["km"] = float(h["km"]); h["fallecidos"] = int(h["fallecidos"]); h["lesionados"] = int(h["lesionados"])
PR = leer(os.path.join(ACT3, "cruce_prensa_ANSV.csv"))
RES = json.load(open(os.path.join(ACT3, "microdato_ANSV_resumen.json"), encoding="utf-8"))
LC, LJ, FIN = RES["limites_tramo_km"]["calarca"], RES["limites_tramo_km"]["cajamarca"], RES["limites_tramo_km"]["fin"]

# ------------------------------------------------------------ tasa post-tunel
hist = leer(os.path.join(ACT1, "tpd_historico_corredor.csv"), ";")
m244 = [int(f["tpd"]) for f in hist if f["estacion"] == "244" and 2015 <= int(f["anio"]) <= 2018]
T244 = sum(m244) / len(m244)
caj = leer(os.path.join(ACT1, "tpd_2019_peaje_cajamarca.csv"), ";")
TCAJ = sum(int(f["total"]) for f in caj) / sum(int(f["dias"]) for f in caj)
tasa = lambda f, tpd, L=45, a=5: f / (tpd * 365 * L * a) * 1e8
paso = [h for h in H if h["tramo"] == "Paso Calarcá – Cajamarca" and 2021 <= int(h["anio"]) <= 2025]
F = sum(h["fallecidos"] for h in paso)
F_sin_borde = sum(h["fallecidos"] for h in paso if h["km"] > LC)
assert F == sum(RES["paso_por_anio"][str(a)]["fallecidos"] for a in range(2021, 2026)), "PARADA: fallecidos del paso no cuadran con el resumen"
TASAS = {
    "fallecidos_paso_2021_2025": F, "fallecidos_si_se_excluye_km_5_0": F_sin_borde,
    "tpd_H1_est244_media_2015_2018": round(T244, 1), "tpd_H2_peaje_cajamarca_2019": round(TCAJ, 1),
    "L_km": 45, "anios": 5,
    "tasa_H1": round(tasa(F, T244), 2), "tasa_H2": round(tasa(F, TCAJ), 2),
    "tasa_H1_sin_borde": round(tasa(F_sin_borde, T244), 2),
    "naturaleza": "cota inferior: subregistro de georreferenciacion (2 de 8 fatales de prensa)",
    "comparable_con_7_66": False,
}
# control: la formula reproduce la tasa publicada del paso (42 fallecidos, est. 244, 2015-2019)
assert abs(tasa(42, T244) - 7.66) < 0.01, "PARADA: la formula no reproduce 7,66"
json.dump(TASAS, open(os.path.join(BASE, "tasa_post_tunel_OE5.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2, sort_keys=True)
print(json.dumps(TASAS, ensure_ascii=False, indent=1))

# ------------------------------------------------------------ densidad lineal
BW = 1.5
x = np.linspace(0, FIN, 1605)
kmh = np.array([h["km"] for h in H])
dens = np.exp(-0.5 * ((x[:, None] - kmh[None, :]) / BW) ** 2).sum(1) / (BW * np.sqrt(2 * np.pi))  # hechos/km

# ------------------------------------------------------------ lienzo
fig = plt.figure(figsize=(15.5, 9.4), dpi=200); fig.patch.set_facecolor("white")
gs = fig.add_gridspec(3, 2, width_ratios=[1.35, 1], height_ratios=[1.55, 0.16, 0.95],
                      wspace=0.12, hspace=0.42, left=0.045, right=0.975, top=0.86, bottom=0.115)

# ---- A: mapa de ubicacion
axm = fig.add_subplot(gs[0, 0])
LON0, LON1, LAT0, LAT1 = -75.70, -75.15, 4.33, 4.58
with rasterio.open(os.path.join(OE1, "Act1_DEM", "DEM_area_estudio.tif")) as src:
    win = rasterio.windows.from_bounds(LON0, LAT0, LON1, LAT1, src.transform)
    dem = src.read(1, window=win).astype(float); ext = rasterio.windows.bounds(win, src.transform)
dem[dem <= -1000] = np.nan
sombra = LightSource(azdeg=315, altdeg=45).hillshade(np.nan_to_num(dem, nan=np.nanmin(dem)), vert_exag=1.0, dx=30, dy=30)
rampa = LinearSegmentedColormap.from_list("t", ["#F7F9FB", "#E4E9EF", "#CBD5E1", "#AEB9C7"])
E = (ext[0], ext[2], ext[1], ext[3])
axm.imshow(dem, extent=E, origin="upper", cmap=rampa, interpolation="bilinear")
axm.imshow(sombra, extent=E, origin="upper", cmap="gray", alpha=0.55, interpolation="bilinear")
tra = json.load(open(os.path.join(OE1, "Act4_Trazado", "trazado_tunel.geojson"), encoding="utf-8"))
xy = np.array(tra["features"][0]["geometry"]["coordinates"])
axm.plot(xy[:, 0], xy[:, 1], color=GRIS, lw=2, ls=(0, (4, 3)), zorder=3)
pts = {}
for h in H:
    k = (float(h["lon"]), float(h["lat"])); p = pts.setdefault(k, {"n": 0, "f": 0, "km": h["km"]})
    p["n"] += 1; p["f"] += h["fallecidos"]
nmax = max(p["n"] for p in pts.values())
for (lo, la), p in sorted(pts.items(), key=lambda t: -t[1]["n"]):
    axm.plot(lo, la, "o", ms=5 + 20 * (p["n"] / nmax) ** 0.5, color=AZUL if p["f"] else AZUL_CLARO,
             mec="white", mew=1.6, alpha=0.93, zorder=5)
for (lo, la), p in pts.items():
    if p["n"] >= 4:
        dxy = {1.992: (10, 8), 65.0: (-14, -22), 51.964: (10, 10), 79.0: (6, 14)}.get(p["km"], (8, 9))
        axm.annotate(f"km {es(p['km'], 1)} · {p['n']} hechos", (lo, la), xytext=dxy, textcoords="offset points", ha="left" if dxy[0] > 0 else "right",
                     fontsize=7.8, color=TINTA, weight="bold", zorder=6,
                     bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.8))
for nom, lo, la in [("Calarcá", -75.640, 4.512), ("Cajamarca", -75.427, 4.428), ("Ibagué", -75.245, 4.392)]:
    axm.text(lo, la, nom, fontsize=9, color=SUAVE, weight="bold", ha="center", va="top", zorder=4)
axm.set_xlim(LON0, LON1); axm.set_ylim(LAT0, LAT1); axm.set_xticks([]); axm.set_yticks([])
axm.set_title("A · Dónde cayeron los 70 hechos: solo 28 puntos distintos", loc="left", fontsize=11, weight="bold", color=TINTA)
axm.plot([], [], "o", color=AZUL, ms=8, label="Punto con al menos un fallecido")
axm.plot([], [], "o", color=AZUL_CLARO, ms=8, label="Punto solo con lesionados")
axm.plot([], [], color=GRIS, lw=2, ls=(0, (4, 3)), label="Trazado del túnel de base (OE 1)")
axm.legend(loc="lower right", fontsize=8, frameon=True, framealpha=0.9, edgecolor="#CBD5E1")

# ---- B: cruce con prensa
axp = fig.add_subplot(gs[0, 1]); axp.set_xlim(0, 1); axp.set_ylim(len(PR) + 0.6, -1.1); axp.axis("off")
axp.set_title("B · ¿Están en el anexo los fatales conocidos por prensa?", loc="left", fontsize=11, weight="bold", color=TINTA)
axp.text(0.00, -0.5, "Fecha", fontsize=8.5, color=SUAVE, weight="bold")
axp.text(0.20, -0.5, "Hecho", fontsize=8.5, color=SUAVE, weight="bold")
axp.text(0.73, -0.5, "Muertos\nprensa", fontsize=8.5, color=SUAVE, weight="bold", va="center")
axp.text(0.88, -0.5, "En el\nanexo", fontsize=8.5, color=SUAVE, weight="bold", va="center")
for i, r in enumerate(PR):
    si = r["en_anexo_ANSV"] == "si"
    col = TINTA if si else SUAVE
    y, m, d = r["fecha"].split("-")
    axp.text(0.00, i + 0.35, f"{d}/{m}/{y}", fontsize=8.6, color=col)
    axp.text(0.20, i + 0.35, r["hecho"].replace("Linea", "Línea").replace("Tunel", "Túnel").replace("Calarca", "Calarcá").replace("camion", "camión"), fontsize=8.6, color=col)
    axp.text(0.73, i + 0.35, r["muertos_prensa"].replace("no indicado", "s. d."), fontsize=8.6, color=col)
    axp.text(0.88, i + 0.35, f"Sí · {r['fallecidos_anexo']}" if si else "No", fontsize=8.6,
             color=AZUL if si else SUAVE, weight="bold")
    axp.plot([0, 1], [i + 0.62, i + 0.62], color="#E2E8F0", lw=0.7)
axp.text(0.00, len(PR) + 0.45, f"{RES['prensa']['en_anexo']} de {RES['prensa']['total']} figuran. "
         "Faltan seis; al menos cinco, en La Línea o sus túneles.", fontsize=8.8, color=TINTA, weight="bold")

# ---- C: franja de densidad lineal
axs = fig.add_subplot(gs[1, :])
rs = LinearSegmentedColormap.from_list("r", ["#F7F9FB", "#C9D7EC", AZUL_CLARO, AZUL])
axs.imshow(dens[None, :], aspect="auto", cmap=rs, extent=(0, FIN, 0, 1), vmin=0, interpolation="bilinear")
axs.set_yticks([]); axs.set_xticks([]); axs.set_xlim(0, FIN)
axs.set_title("C · Densidad lineal de hechos a lo largo de la Ruta 4003 (núcleo gaussiano, banda 1,5 km)",
              loc="left", fontsize=11, weight="bold", color=TINTA)
axs.text(FIN, 1.35, f"máx. {es(dens.max(), 1)} hechos/km", fontsize=8, color=SUAVE, ha="right", va="bottom",
         transform=axs.transData)

# ---- D: barras por km
axb = fig.add_subplot(gs[2, :], sharex=axs)
K = leer(os.path.join(ACT3, "microdato_ANSV_por_km.csv"))
k0 = np.array([int(r["km_desde"]) for r in K]); hf = np.array([int(r["hechos_fatales"]) for r in K])
hn = np.array([int(r["hechos"]) for r in K]) - hf
axb.bar(k0 + 0.5, hf, width=0.85, color=AZUL, label="Hechos con fallecido")
axb.bar(k0 + 0.5, hn, width=0.85, bottom=hf, color=AZUL_CLARO, label="Hechos solo con lesionados")
axb.axvspan(LC, LJ, color="#EEF2F7", zorder=0)
for xv in (LC, LJ): axb.axvline(xv, color=SUAVE, lw=0.8, ls=":")
ytop = max(hf + hn) * 1.5
for a, b, t in [(0, LC, "Armenia–\nCalarcá\n(fuera)"), (LC, LJ, "Paso Calarcá – Cajamarca · 45 km (est. INVÍAS 244)"),
                (LJ, FIN, "Cajamarca – Ibagué · 29 km (est. 243)")]:
    axb.text((a + b) / 2, ytop * 0.97, t, ha="center", va="top", fontsize=8.5, color=TINTA, weight="bold")
axb.set_ylim(0, ytop); axb.set_xlim(0, 81)
axb.set_title("D · Hechos por kilómetro de abscisa", loc="left", fontsize=11, weight="bold", color=TINTA)
axb.set_ylabel("Hechos por km", fontsize=9)
axb.set_xlabel("Abscisa de la Ruta 4003, km desde Armenia (PR + distancia)  →  Ibagué", fontsize=9)
axb.spines[["top", "right"]].set_visible(False)
axb.legend(loc="upper left", bbox_to_anchor=(0.075, 0.80), fontsize=8, frameon=False)
p11 = RES["paso_km_11_a_41"]
axb.annotate(f"km 11 – 41 (ascenso y Alto de La Línea):\n{p11['hechos']} hechos, {p11['fallecidos']} fallecido",
             xy=(26, 1.1), xytext=(26, ytop * 0.58), ha="center", fontsize=8.5, color=TINTA,
             arrowprops=dict(arrowstyle="-", color=SUAVE, lw=0.8))

# ---- encabezado y pie
fig.text(0.045, 0.955, "OE 5 · Act 4 — Siniestros georreferenciados por la ANSV en la Ruta 4003, 2021 – marzo 2026",
         fontsize=15, weight="bold", color=TINTA)
fig.text(0.045, 0.918, f"{RES['victimas']} víctimas ({RES['fallecidos']} fallecidos, {RES['lesionados']} lesionados) en "
         f"{RES['hechos']} hechos. La figura muestra dónde se pudo georreferenciar, no dónde está el riesgo: "
         "el ascenso está subrepresentado.", fontsize=10, color=SUAVE)
fig.text(0.045, 0.888, f"Tasa del paso 2021–2025, cota inferior [H]: {es(TASAS['tasa_H1'], 2)} a {es(TASAS['tasa_H2'], 2)} "
         f"fallecidos por 10⁸ veh-km ({F} fallecidos del anexo; sin aforo del paso posterior a 2019). "
         "No es comparable con la tasa 2015–2019 (7,66): otra fuente y otro criterio.", fontsize=9, color=TINTA)
fig.text(0.045, 0.035, "[F] ANSV – Observatorio Nacional de Seguridad Vial, oficio 20265000140371 del 22 sep 2026 y anexo "
         "Sint_Via_LaLinea_CodTramo_4003 (fuente primaria INMLCF). Prensa: El Tiempo, El Espectador, Infobae (ver memoria del OE 5).",
         fontsize=7.6, color=SUAVE)
fig.text(0.045, 0.021, "[CP] procesar_microdato_ANSV_OE5.py · densidad_lineal_OE5.py.  [H] Hecho = misma fecha, municipio y PR; "
         "límite Calarcá en km 5,0 (longitud INVÍAS est. 245); banda 1,5 km; TPD 2015–2018 y 2019.", fontsize=7.6, color=SUAVE)
fig.text(0.045, 0.007, "Semillero de Investigación GEOPAV · Universidad de Ibagué · Paz y Región 2026B", fontsize=7.6, color=SUAVE)

os.makedirs(VIS, exist_ok=True)
fig.savefig(os.path.join(VIS, "densidad_lineal_OE5.png"), dpi=200, facecolor="white")
fig.savefig(os.path.join(VIS, "densidad_lineal_OE5.pdf"), facecolor="white", metadata={"CreationDate": None})
print("OK", os.path.join(VIS, "densidad_lineal_OE5.png"))
