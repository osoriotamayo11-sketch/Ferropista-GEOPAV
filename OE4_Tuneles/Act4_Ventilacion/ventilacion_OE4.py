# -*- coding: utf-8 -*-
"""
OE 4 · Actividad 4 — Planteamiento conceptual del sistema de ventilación longitudinal del túnel.
Producto: «Diagrama de flujo de aire» · Esquema gráfico (JPG). Sesión 18 (29 sep 2026).

Qué calcula [CP]
  Velocidad crítica que impide el retroceso del humo (backlayering) con las ecuaciones de NFPA 502, en la forma
  citada por Thunderhead Engineering (documentación de PyroSim 2026.1), resueltas por iteración:
      Vc = K1·Kg·(g·H·Q / (ρ·cp·A·Tf))^(1/3)       Tf = Q / (ρ·cp·A·Vc) + T
  K1 = 0,606 [F]; Kg = 1 (factor de pendiente para túnel a nivel; la rasante del OE 1 tiene 0,96 %) [H].
  Caudal de aire = Vc · A.
Entradas
  - A: área de excavación media de los túneles principales, 8.450.000 m³ / 64,2 km (ponencia, dia. 22) [CP de F],
    leída de la Act 2 (sectorizacion_TBM_OE4.json).
  - Q: potencia del incendio de diseño de un camión pesado (HGV). Ingason (2008): 13-202 MW medidos; NFPA 502 (ed.
    2008) adoptó 70-200 MW con base en los ensayos de Runehamar [F]. Se usan 70, 100 y 200 MW y se toma como calor
    convectivo cedido al aire el 70 % [H].
  - ρ del aire a la cota media de la rasante con atmósfera isoterma (escala 8.400 m) [H]; cp = 1,005 kJ/kg·K; T = 293 K [H].
  - H (altura de la sección) = diámetro equivalente de la Act 2 [H].
Dibuja el esquema de ventilación longitudinal (operación normal, incendio y estación central) con los resultados.
Salidas: ventilacion_OE4.json, ../Visuales/diagrama_ventilacion_OE4.jpg (entregable) y .png
"""
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

AQUI = os.path.dirname(os.path.abspath(__file__))
OE4 = os.path.dirname(AQUI)
RAIZ = os.path.dirname(OE4)
sys.path.insert(0, os.path.join(RAIZ, "Comun"))
from lamina_institucional import encabezado, pie, VERDE, AZUL, GRIS  # noqa: E402

A2 = json.load(open(os.path.join(OE4, "Act2_Sectorizacion", "sectorizacion_TBM_OE4.json"), encoding="utf-8"))
SALIDA = os.path.join(AQUI, "ventilacion_OE4.json")
VIS = os.path.join(OE4, "Visuales")

K1, KG, G, CP = 0.606, 1.0, 9.81, 1.005
T0 = 293.0
FRACCION_CONVECTIVA = 0.70
HRR_MW = (70, 100, 200)


def velocidad_critica(Q_kw, A, H, rho):
    Vc = 2.0
    for _ in range(200):
        Tf = Q_kw / (rho * CP * A * Vc) + T0
        nuevo = K1 * KG * (G * H * Q_kw / (rho * CP * A * Tf)) ** (1 / 3)
        if abs(nuevo - Vc) < 1e-9:
            break
        Vc = nuevo
    return Vc, Q_kw / (rho * CP * A * Vc) + T0


def main():
    A = A2["area_excavacion_m2"]
    H = A2["D_eq_m"]
    puntos = A2["puntos"]
    z_media = sum(p["rasante"] for p in puntos) / len(puntos)
    rho = 1.204 * math.exp(-z_media / 8400)
    casos = []
    for hrr in HRR_MW:
        Qc = hrr * 1000 * FRACCION_CONVECTIVA
        Vc, Tf = velocidad_critica(Qc, A, H, rho)
        # verificación: las dos ecuaciones se cumplen a la vez
        assert abs(Vc - K1 * KG * (G * H * Qc / (rho * CP * A * Tf)) ** (1 / 3)) < 1e-6
        casos.append(dict(HRR_MW=hrr, Q_conv_kW=Qc, Vc_m_s=Vc, Tf_K=Tf, caudal_m3_s=Vc * A))
    L = A2["longitud_m"]
    cob_max = max(p["H"] for p in puntos)
    salida = dict(generado_por="OE4_Tuneles/Act4_Ventilacion/ventilacion_OE4.py", area_m2=A, altura_m=H, z_media_rasante=z_media, rho=rho,
                  K1=K1, Kg=KG, cp=CP, T0=T0, fraccion_convectiva=FRACCION_CONVECTIVA, casos=casos, longitud_m=L, cobertura_max_m=cob_max)
    json.dump(salida, open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for c in casos:
        print(c["HRR_MW"], "MW → Vc", round(c["Vc_m_s"], 2), "m/s; Tf", round(c["Tf_K"] - 273.15), "°C; caudal", round(c["caudal_m3_s"]), "m³/s")
    print("ρ", round(rho, 3), "z media", round(z_media), "A", round(A, 1), "H", round(H, 2))
    dibujar(salida)


def flecha(ax, x0, x1, y, color, lw=2.2, ms=14):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="-|>", mutation_scale=ms, color=color, lw=lw))


def es(v, d=1):
    return f"{v:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def dibujar(S):
    Lk = S["longitud_m"] / 1000
    fig = plt.figure(figsize=(16.54, 11.69))
    top = encabezado(fig, "Esquema conceptual de ventilación longitudinal del túnel",
                     "OE 4 · Actividad 4 — Flujo de aire en operación normal y en incendio de un camión, con la velocidad crítica de NFPA 502")
    bot = pie(fig, "Fuentes: área de excavación de la ponencia (dia. 22) [CP de F]; incendios de camiones pesados de 13 a 202 MW y valores de diseño de 70 a 200 MW de NFPA 502 (2008), según Ingason (2008) [F]; "
                   "ecuaciones de velocidad crítica de NFPA 502 citadas por Thunderhead Engineering (PyroSim 2026.1) [F]; fracción convectiva, densidad y temperatura del aire, "
                   "estación central y galerías [H]. Longitud y cotas del OE 1. Script: OE4_Tuneles/Act4_Ventilacion/ventilacion_OE4.py. "
                   "Elaborado con apoyo de IA (Claude) y verificado. ESQUEMA CONCEPTUAL: no sustituye el diseño de ventilación ni el análisis de riesgo.")
    Hh = top - bot

    def panel(y0, h, titulo, est_izq=False):
        ax = fig.add_axes([0.05, y0, 0.90, h])
        ax.set_xlim(-3, Lk + 3); ax.set_ylim(0, 10); ax.axis("off")
        ax.set_title(titulo, fontsize=10.5, color=AZUL, loc="left")
        ax.add_patch(Rectangle((0, 3.5), Lk, 3, facecolor="#F3F4F6", edgecolor="#374151", lw=1.2))
        ax.text(-0.3, 5, "Portal\noriental\n(Ibagué)", ha="right", va="center", fontsize=8)
        ax.text(Lk + 0.3, 5, "Portal\noccidental\n(Calarcá)", ha="left", va="center", fontsize=8)
        xc = Lk / 2
        ax.add_patch(Rectangle((xc - 1.2, 3.0), 2.4, 4.0, facecolor="#E0F2FE", edgecolor=AZUL, lw=1, ls="--"))
        ax.text(xc + (1.6 if est_izq else 0), 7.3, "Estación central (bypass de cruce de convoyes, dia. 23)\ncon extracción de humo y salida a galería de acceso [H]",
                ha="left" if est_izq else "center", fontsize=7.5, color=AZUL)
        for x in (0.8, 1.6, Lk - 1.6, Lk - 0.8):
            ax.add_patch(Rectangle((x - 0.25, 6.0), 0.5, 0.35, color="#6B7280"))
        ax.text(1.2, 6.6, "Ventiladores de chorro (jet fans) [H]", fontsize=7, color=GRIS)
        return ax

    # A. operación normal
    a1 = panel(bot + Hh * 0.70, Hh * 0.25, "A. Operación normal: el tren empuja el aire (efecto pistón) y los ventiladores de portal lo complementan en el sentido de marcha")
    for x in range(3, int(Lk) - 2, 6):
        if not (7 <= x <= 20):
            flecha(a1, x, x + 3.5, 5, "#2563EB")
    a1.add_patch(Rectangle((8, 4.1), 12, 1.8, facecolor="#1F2937", alpha=0.85))
    a1.text(14, 5, "Tren de 750 m con 35 camiones (dia. 20-23) →", color="white", ha="center", va="center", fontsize=7.5)
    a1.text(Lk / 2, 2.2, "Los motores de los camiones van apagados en el tren: el aire fresco retira calor de frenos, equipos y roca [H]; con coberturas de hasta "
            f"{es(S['cobertura_max_m'], 0)} m la roca estará caliente y el enfriamiento puede gobernar el caudal normal (no calculado).", ha="center", fontsize=7.8, color=GRIS)
    # B. incendio en la mitad oriental
    a2 = panel(bot + Hh * 0.37, Hh * 0.25, est_izq=True, titulo="B. Incendio de un camión en el tren: el tren sigue hasta la estación o el portal; el aire se impulsa hacia el humo con v ≥ Vc")
    xf = 16
    a2.add_patch(Rectangle((xf - 1.5, 4.1), 3, 1.8, facecolor="#1F2937", alpha=0.85))
    a2.text(xf, 6.9, "Incendio", ha="center", color="#B91C1C", fontsize=9, weight="bold")
    for x in range(1, xf - 3, 4):
        flecha(a2, x, x + 2.8, 5, "#2563EB")
    a2.text((xf - 2) / 2, 2.6, "Aire fresco con v ≥ Vc: sin retroceso de humo del lado de evacuación", ha="center", fontsize=7.6, color="#1D4ED8")
    for x in range(xf + 2, int(Lk / 2) - 2, 3):
        flecha(a2, x, x + 2.2, 5.6, "#6B7280", lw=3)
    a2.text((xf + Lk / 2) / 2 + 0.5, 2.6, "Humo hacia la extracción de la estación central", ha="center", fontsize=7.6, color="#374151")
    flecha(a2, Lk / 2, Lk / 2, 7.0, "#6B7280")
    a2.annotate("", xy=(Lk / 2, 9.4), xytext=(Lk / 2, 7.0), arrowprops=dict(arrowstyle="-|>", color="#6B7280", lw=2.5))
    for x in range(int(Lk) - 3, int(Lk / 2) + 3, -4):
        flecha(a2, x, x - 2.8, 4.4, "#2563EB")
    a2.text(Lk * 0.78, 2.6, "El tramo occidental también empuja hacia la estación: el humo queda confinado entre el fuego y la extracción", ha="center", fontsize=7.6, color="#1D4ED8")
    # C. cuadro de resultados
    ax = fig.add_axes([0.05, bot + 0.01, 0.9, Hh * 0.30]); ax.axis("off")
    ax.set_title("C. Velocidad crítica y caudal de aire para el incendio de diseño (NFPA 502, iteración) [CP]", fontsize=10.5, color=AZUL, loc="left")
    filas = [[f"{c['HRR_MW']} MW", f"{es(c['Q_conv_kW'] / 1000, 0)} MW", es(c["Vc_m_s"], 2), es(c["Tf_K"] - 273.15, 0), es(c["caudal_m3_s"], 0)] for c in S["casos"]]
    tb = ax.table(cellText=filas, colLabels=["Potencia del incendio (HRR)", "Calor al aire (70 %) [H]", "Velocidad crítica Vc (m/s)", "Temperatura media de gases Tf (°C)",
                                           "Caudal de aire Vc·A (m³/s)"], loc="upper left", cellLoc="center", colWidths=[0.18, 0.18, 0.18, 0.22, 0.2])
    tb.auto_set_font_size(False); tb.set_fontsize(8.5); tb.scale(1, 1.6)
    for (r, c), cel in tb.get_celld().items():
        cel.set_edgecolor("#CBD5E1")
        if r == 0:
            cel.set_facecolor(AZUL); cel.get_text().set_color("white"); cel.get_text().set_weight("bold")
    ax.text(0, 0.18, f"Datos: sección A = {es(S['area_m2'], 1)} m², altura H = {es(S['altura_m'], 2)} m, K1 = 0,606, Kg = 1, cp = 1,005 kJ/kg·K, T = 20 °C, "
                     f"ρ = {es(S['rho'], 3)} kg/m³ (cota media de la rasante {es(S['z_media_rasante'], 0)} msnm). Longitud del túnel {es(S['longitud_m'] / 1000, 1)} km (OE 1).",
            fontsize=8, color=GRIS, transform=ax.transAxes)
    ax.text(0, 0.05, "Pendiente: pérdidas de carga y número de ventiladores, enfriamiento por calor de la roca, efecto pistón y presiones transitorias, "
                     "ubicación real de las galerías de acceso (16 km según la ponencia) y análisis cuantitativo de riesgo.", fontsize=8, color="#9A3412", transform=ax.transAxes)
    for ext, kw in (("jpg", dict(dpi=200, pil_kwargs={"quality": 92})), ("png", dict(dpi=200))):
        fig.savefig(os.path.join(VIS, f"diagrama_ventilacion_OE4.{ext}"), **kw)
    plt.close(fig)


if __name__ == "__main__":
    main()
