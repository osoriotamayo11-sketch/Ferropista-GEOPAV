# -*- coding: utf-8 -*-
"""
OE 4 · Actividad 2 — Definición de los tramos con condiciones favorables para excavación mecanizada con tuneladora.
Producto: «Esquema de sectorización» · Plano AutoCAD / PDF. Sesión 18 (29 sep 2026).

Entradas (no se escribe ninguna cifra geológica a mano):
  - ../Act1_Litologia/matriz_litologica_OE4.json (tramos, juegos σci/mi/GSI, fallas, zona de falla)
  - OE1_Topografia/Act5_Perfil/perfil_continuo.csv (PK, cota de terreno y de rasante, cobertura)
Método, por abscisa del perfil (≈ 35 m) y para los casos mínimo / típico / máximo de parámetros:
  1. σcm = (0,0034·mi^0,8)·σci·{1,029 + 0,025·e^(−0,1·mi)}^GSI      Hoek y Marinos (2000), ec. 1  [F]
  2. p0 = γ·H, con H = cobertura del OE 1 y γ de la Act 1                                            [H]
  3. ε (%) = 0,2·(σcm/p0)^−2 (túnel sin soporte)                      Hoek y Marinos (2000), fig. 3 [F]
     Clases A < 1 %, B 1-2,5 %, C 2,5-5 %, D 5-10 %, E > 10 %          Hoek y Marinos (2000), fig. 7 [F]
  4. En la zona de influencia de cada falla del MGC (ancho típico de la Act 1): σci × 0,25 y GSI de falla [H].
  5. Resistencia de la roca intacta frente a los campos de aplicación de la DAUB (2025) para tuneladora de doble
     escudo (DOS): σci < 25 MPa = «o» (aplicación ampliada); ≥ 25 MPa = «+» (campo principal)            [F]
  6. Regla de sectorización [H] (declarada, se ajusta en un solo sitio):
       FAVORABLE     ε < 1 % (clase A) y σci ≥ 25 MPa, fuera de zona de falla
       CONDICIONADA  ε 1-2,5 % (clase B) o 5 ≤ σci < 25 MPa: tuneladora de doble escudo con sobreexcavación
                     y reservas de empuje; riesgo de atrapamiento controlable
       DESFAVORABLE  ε ≥ 2,5 % (clases C-E: cerchas pesadas, paraguas y refuerzo de frente, incompatibles con el
                     escudo), zona de falla, o cobertura < 2 diámetros junto a los portales (emboquille)
     Tramos de menos de 200 m se asimilan al vecino más desfavorable [H].
     La clase de sectorización del plano usa el caso TÍPICO; mínimo y máximo se reportan como sensibilidad.
Salidas: sectorizacion_TBM_OE4.json, Plano_sectorizacion_TBM_OE4.dxf y ../../OE4_Tuneles/Visuales/plano_sectorizacion_TBM_OE4.pdf/.png
Requiere ezdxf, matplotlib; lámina con Comun/lamina_institucional.py.
"""
import csv
import json
import math
import os
import sys

import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

AQUI = os.path.dirname(os.path.abspath(__file__))
OE4 = os.path.dirname(AQUI)
RAIZ = os.path.dirname(OE4)
sys.path.insert(0, os.path.join(RAIZ, "Comun"))
from lamina_institucional import encabezado, pie, VERDE, AZUL, GRIS  # noqa: E402

ACT1 = os.path.join(OE4, "Act1_Litologia", "matriz_litologica_OE4.json")
PERFIL = os.path.join(RAIZ, "OE1_Topografia", "Act5_Perfil", "perfil_continuo.csv")
SAL_JSON = os.path.join(AQUI, "sectorizacion_TBM_OE4.json")
SAL_DXF = os.path.join(AQUI, "Plano_sectorizacion_TBM_OE4.dxf")
VIS = os.path.join(OE4, "Visuales")
os.makedirs(VIS, exist_ok=True)

# ------------------------------------------------------------------ hipótesis y umbrales
UMBRAL_A, UMBRAL_B = 1.0, 2.5            # % de deformación (HM00, fig. 7) [F]; su uso como corte TBM es [H]
SCI_DOS_MAIN, SCI_DOS_MIN = 25.0, 5.0    # MPa, DAUB 2025 apéndice 3.2 (DOS) [F]
AREA_EXCAVACION_M2 = 8_450_000 / 64_200  # m², volumen / longitud de los túneles principales (ponencia dia. 22) [CP de F]
D_EQ = math.sqrt(4 * AREA_EXCAVACION_M2 / math.pi)
H_EMBOQUILLE = 2 * D_EQ                  # cobertura mínima para excavar con tuneladora lejos del emboquille [H]
CASOS = ("Mínimo", "Típico", "Máximo")
SUF = {"Mínimo": "min", "Típico": "tip", "Máximo": "max"}
L_MIN = 200.0                            # m, longitud mínima de un tramo de sectorización [H]
CLASES = [("A", 0, 1), ("B", 1, 2.5), ("C", 2.5, 5), ("D", 5, 10), ("E", 10, 1e9)]
COLOR_SECTOR = {"FAVORABLE": "#178E2C", "CONDICIONADA": "#CF9013", "DESFAVORABLE": "#B91C1C"}


def sigma_cm(sci, mi, gsi):
    return 0.0034 * mi ** 0.8 * sci * (1.029 + 0.025 * math.exp(-0.1 * mi)) ** gsi


def clase(eps):
    for c, a, b in CLASES:
        if a <= eps < b:
            return c
    return "E"


def main():
    A1 = json.load(open(ACT1, encoding="utf-8"))
    perfil = [dict(pk=float(r["PK_m"]), terreno=float(r["Cota_terreno_msnm"]), rasante=float(r["Cota_rasante_msnm"]), H=float(r["Cobertura_m"]))
              for r in csv.DictReader(open(PERFIL, encoding="utf-8-sig"))]
    L_perfil = perfil[-1]["pk"]
    k = L_perfil / A1["longitud_eje_m"]      # PK de la Act 1 (proyección plana EPSG 3116) → PK geodésico del OE 1
    tramos = [dict(t, a=t["pk_ini"] * k, b=t["pk_fin"] * k) for t in A1["tramos"]]
    ancho_falla = A1["zona_falla"]["ancho_m"][1]
    fallas = [dict(f, pk_g=f["pk"] * k) for f in A1["fallas"] if f["fuente"] == "MGC 2023"]
    gamma = A1["gamma_roca_MN_m3"]
    zf = A1["zona_falla"]

    puntos = []
    for p in perfil:
        t = next(t for t in tramos if t["a"] - 1 <= p["pk"] <= t["b"] + 1)
        en_falla = any(abs(p["pk"] - f["pk_g"]) <= ancho_falla / 2 for f in fallas)
        H = max(p["H"], 0.0)
        p0 = gamma * H
        res = {}
        for ci, caso in enumerate(CASOS):
            peor = None
            for jg in t["juegos"]:
                sci, mi, gsi = jg["sci"][ci], jg["mi"][ci], jg["gsi"][ci]
                if en_falla:
                    sci, gsi = sci * zf["sci_factor"], zf["gsi"][ci]
                scm = sigma_cm(sci, mi, gsi)
                eps = 0.2 * (scm / p0) ** -2 if p0 > 0 else 0.0
                r = dict(juego=jg["id"], sci=sci, mi=mi, gsi=gsi, scm=scm, eps=eps)
                if peor is None or eps > peor["eps"]:
                    peor = r
            peor["clase"] = clase(peor["eps"])
            if H < H_EMBOQUILLE:
                sector = "DESFAVORABLE"; motivo = "Emboquille (cobertura < 2 D)"
            elif en_falla:
                sector = "DESFAVORABLE"; motivo = "Zona de falla"
            elif peor["eps"] >= UMBRAL_B:
                sector = "DESFAVORABLE"; motivo = f"Squeezing clase {peor['clase']}"
            elif peor["eps"] >= UMBRAL_A or peor["sci"] < SCI_DOS_MAIN:
                sector = "CONDICIONADA"; motivo = f"Squeezing clase {peor['clase']}" if peor["eps"] >= UMBRAL_A else "σci < 25 MPa"
            else:
                sector = "FAVORABLE"; motivo = "Clase A y σci ≥ 25 MPa"
            if peor["sci"] < SCI_DOS_MIN and sector != "DESFAVORABLE":
                sector, motivo = "DESFAVORABLE", "σci < 5 MPa"
            res[caso] = dict(peor, sector=sector, motivo=motivo, p0=p0)
        puntos.append(dict(pk=p["pk"], terreno=p["terreno"], rasante=p["rasante"], H=H, tramo=t["tramo"], simbolo=t["simbolo"], en_falla=en_falla, casos=res))

    # tramos continuos por sector (caso típico) y longitudes por caso
    def agrupar(caso):
        g = []
        for i, pt in enumerate(puntos):
            s = pt["casos"][caso]["sector"]
            pk0 = pt["pk"] if i == 0 else (puntos[i - 1]["pk"] + pt["pk"]) / 2
            pk1 = pt["pk"] if i == len(puntos) - 1 else (pt["pk"] + puntos[i + 1]["pk"]) / 2
            if g and g[-1]["sector"] == s:
                g[-1]["pk_fin"] = pk1
                g[-1]["motivos"].add(pt["casos"][caso]["motivo"])
            else:
                g.append(dict(sector=s, pk_ini=pk0, pk_fin=pk1, motivos={pt["casos"][caso]["motivo"]}))
        # tramos de menos de L_MIN se asimilan al vecino más desfavorable (no se cambia de método por 100 m) [H]
        orden = {"FAVORABLE": 0, "CONDICIONADA": 1, "DESFAVORABLE": 2}
        cambio = True
        while cambio:
            cambio = False
            for i, x in enumerate(g):
                if x["pk_fin"] - x["pk_ini"] < L_MIN and len(g) > 1:
                    vec = [v for v in (g[i - 1] if i > 0 else None, g[i + 1] if i + 1 < len(g) else None) if v]
                    dest = max(vec, key=lambda v: orden[v["sector"]])
                    dest["pk_ini"], dest["pk_fin"] = min(dest["pk_ini"], x["pk_ini"]), max(dest["pk_fin"], x["pk_fin"])
                    dest["motivos"] |= x["motivos"]
                    g.pop(i)
                    # fusiona vecinos iguales que quedaron contiguos
                    j = 0
                    while j < len(g) - 1:
                        if g[j]["sector"] == g[j + 1]["sector"]:
                            g[j]["pk_fin"] = g[j + 1]["pk_fin"]; g[j]["motivos"] |= g[j + 1]["motivos"]; g.pop(j + 1)
                        else:
                            j += 1
                    cambio = True
                    break
        for x in g:
            x["longitud"] = x["pk_fin"] - x["pk_ini"]
            x["motivos"] = sorted(x["motivos"])
        return g

    grupos = {c: agrupar(c) for c in CASOS}
    resumen = {c: {s: sum(x["longitud"] for x in grupos[c] if x["sector"] == s) for s in COLOR_SECTOR} for c in CASOS}
    eps_max = {c: max(p["casos"][c]["eps"] for p in puntos) for c in CASOS}
    salida = dict(generado_por="OE4_Tuneles/Act2_Sectorizacion/sectorizacion_TBM_OE4.py", factor_pk=k, longitud_m=L_perfil,
                  area_excavacion_m2=AREA_EXCAVACION_M2, D_eq_m=D_EQ, H_emboquille_m=H_EMBOQUILLE, umbrales=dict(A=UMBRAL_A, B=UMBRAL_B, sci_dos=SCI_DOS_MAIN, sci_min=SCI_DOS_MIN),
                  ancho_falla_m=ancho_falla, resumen_m=resumen, eps_max=eps_max, grupos=grupos,
                  tramos=[dict(tramo=t["tramo"], simbolo=t["simbolo"], a=t["a"], b=t["b"]) for t in tramos],
                  fallas=[dict(nombre=f["nombre"], pk=f["pk_g"]) for f in fallas],
                  puntos=[dict(pk=p["pk"], H=p["H"], terreno=p["terreno"], rasante=p["rasante"], tramo=p["tramo"], en_falla=p["en_falla"],
                               **{f"eps_{SUF[c]}": p["casos"][c]["eps"] for c in CASOS},
                               **{f"sector_{SUF[c]}": p["casos"][c]["sector"] for c in CASOS},
                               clase_tip=p["casos"]["Típico"]["clase"], juego_tip=p["casos"]["Típico"]["juego"]) for p in puntos],
                  fuente_propuesta=dict(tbm_km=27.5, convencional_km=36.7, total_km=64.2, nota="Ponencia dia. 22: túneles principales incl. bypass [F]"))
    json.dump(salida, open(SAL_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("resumen (m):", {c: {s: round(v) for s, v in r.items()} for c, r in resumen.items()})
    print("ε máx (%):", {c: round(v, 2) for c, v in eps_max.items()}, "D_eq", round(D_EQ, 2), "H_emb", round(H_EMBOQUILLE, 1))
    for x in grupos["Típico"]:
        print(round(x["pk_ini"]), round(x["pk_fin"]), x["sector"], x["motivos"])
    dibujar(salida, puntos)


def dibujar(S, puntos):
    pk = [p["pk"] / 1000 for p in puntos]
    fig = plt.figure(figsize=(16.54, 11.69))
    top = encabezado(fig, "Sectorización del túnel para excavación con tuneladora",
                     "OE 4 · Actividad 2 — Perfil longitudinal, geología del MGC 2023, fallas, deformación esperada (Hoek y Marinos, 2000) y aptitud para TBM")
    bot = pie(fig, "Fuentes: perfil y cobertura del OE 1 [CP]; unidades y fallas del Mapa Geológico de Colombia 2023, SGC [F]; parámetros de macizo de la Act 1 del OE 4 y de la Act 3 del OE 3 [F/H]; "
                   "σcm y deformación ε = 0,2·(σcm/p0)⁻² de Hoek y Marinos (2000) [F]; campos de aplicación de tuneladora de doble escudo, DAUB (2025) apéndice 3.2 [F]; "
                   "regla de sectorización y zona de falla [H]. Script: OE4_Tuneles/Act2_Sectorizacion/sectorizacion_TBM_OE4.py. Archivo AutoCAD: Plano_sectorizacion_TBM_OE4.dxf. "
                   "Elaborado con apoyo de IA (Claude) y verificado. ESQUEMA CONCEPTUAL: no sustituye la exploración ni el diseño.")
    H_ = top - bot
    # 1. perfil
    ax1 = fig.add_axes([0.06, bot + H_ * 0.60, 0.90, H_ * 0.33])
    ax1.fill_between(pk, [p["rasante"] for p in puntos], [p["terreno"] for p in puntos], color="#E5E7EB", lw=0)
    ax1.plot(pk, [p["terreno"] for p in puntos], color="#6B7280", lw=1, label="Terreno (Copernicus GLO-30, OE 1)")
    ax1.plot(pk, [p["rasante"] for p in puntos], color=AZUL, lw=1.6, label="Rasante del túnel (OE 1)")
    for t in S["tramos"]:
        ax1.axvline(t["a"] / 1000, color="#9CA3AF", lw=0.5, ls=":")
        ax1.text((t["a"] + t["b"]) / 2000, 3550, f"{t['tramo']}\n{t['simbolo']}", ha="center", va="top", fontsize=7.2, color=GRIS)
    for f in S["fallas"]:
        ax1.axvline(f["pk"] / 1000, color="#B91C1C", lw=1.1)
        ax1.text(f["pk"] / 1000 + 0.15, 700, f["nombre"].replace("Falla de ", "F. "), rotation=90, fontsize=6.8, color="#B91C1C", va="bottom")
    ax1.set_ylim(600, 3600); ax1.set_xlim(0, S["longitud_m"] / 1000)
    ax1.set_ylabel("Cota (msnm)", fontsize=9); ax1.tick_params(labelsize=8)
    ax1.legend(loc="lower center", bbox_to_anchor=(0.6, 0.0), ncol=2, fontsize=7.5, frameon=False)
    ax1.set_title("A. Perfil longitudinal con tramos litológicos (MGC 2023) y fallas cartografiadas — PK en km desde el portal oriental (Ibagué)", fontsize=10, color=AZUL, loc="left")
    # 2. deformación
    ax2 = fig.add_axes([0.06, bot + H_ * 0.28, 0.90, H_ * 0.25])
    ax2.text(0.3, 14, "Clase E", fontsize=7, color=GRIS, va="center")
    for c, a, b in CLASES[:4]:
        ax2.axhspan(a, b, color={"A": "#ECFDF5", "B": "#FEF9C3", "C": "#FFEDD5", "D": "#FEE2E2"}[c], lw=0)
        ax2.text(0.3, (a + b) / 2 if b < 20 else a + 1, f"Clase {c}", fontsize=7, color=GRIS, va="center")
    ax2.fill_between(pk, [min(p["casos"]["Máximo"]["eps"], 20) for p in puntos], [min(p["casos"]["Mínimo"]["eps"], 20) for p in puntos],
                     color="#93C5FD", alpha=0.5, lw=0, label="Rango mínimo–máximo de parámetros")
    ax2.plot(pk, [min(p["casos"]["Típico"]["eps"], 20) for p in puntos], color=AZUL, lw=1.4, label="Caso típico")
    ax2.set_yscale("symlog", linthresh=1); ax2.set_ylim(0, 20); ax2.set_xlim(0, S["longitud_m"] / 1000)
    ax2.set_yticks([0, 1, 2.5, 5, 10, 20]); ax2.set_yticklabels(["0", "1", "2,5", "5", "10", "≥ 20"])
    ax2.set_ylabel("ε = cierre / diámetro (%)", fontsize=9); ax2.tick_params(labelsize=8)
    ax2.legend(loc="upper right", fontsize=7.5, frameon=False)
    ax2.set_title("B. Deformación esperada del túnel sin soporte, ε = 0,2·(σcm/p0)⁻² (Hoek y Marinos, 2000), con p0 = γ·cobertura", fontsize=10, color=AZUL, loc="left")
    # 3. sectorización
    ax3 = fig.add_axes([0.06, bot + H_ * 0.15, 0.90, H_ * 0.07])
    for i, caso in enumerate(("Máximo", "Típico", "Mínimo")):
        for g in S["grupos"][caso]:
            ax3.add_patch(Rectangle((g["pk_ini"] / 1000, i), g["longitud"] / 1000, 0.8, color=COLOR_SECTOR[g["sector"]], lw=0))
    ax3.set_xlim(0, S["longitud_m"] / 1000); ax3.set_ylim(-0.1, 2.9)
    ax3.set_yticks([0.4, 1.4, 2.4]); ax3.set_yticklabels(["Parámetros máx.", "TÍPICO", "Parámetros mín."], fontsize=7.5)
    ax3.set_xlabel("PK (km)", fontsize=9); ax3.tick_params(axis="x", labelsize=8)
    ax3.set_title("C. Aptitud para tuneladora de doble escudo (verde favorable · ocre condicionada · rojo desfavorable → método convencional)", fontsize=10, color=AZUL, loc="left")
    # 4. cuadro
    ax4 = fig.add_axes([0.06, bot + 0.005, 0.90, H_ * 0.11]); ax4.axis("off")
    filas = []
    for caso in CASOS:
        r = S["resumen_m"][caso]
        tot = sum(r.values())
        filas.append([caso] + [f"{r[s] / 1000:.1f} km ({100 * r[s] / tot:.0f} %)".replace(".", ",") for s in COLOR_SECTOR])
    filas.append(["Propuesta (dia. 22)", f"TBM mín. {S['fuente_propuesta']['tbm_km']:.1f} km de 64,2 km (43 %)".replace(".", ","), "—",
                  f"Convencional {S['fuente_propuesta']['convencional_km']:.1f} km (57 %)".replace(".", ",")])
    tb = ax4.table(cellText=filas, colLabels=["Caso de parámetros", "Favorable TBM", "Condicionada", "Desfavorable (convencional)"], loc="upper left", cellLoc="left",
                   colWidths=[0.16, 0.28, 0.2, 0.3])
    tb.auto_set_font_size(False); tb.set_fontsize(7.8); tb.scale(1, 1.25)
    for (r_, c_), cel in tb.get_celld().items():
        cel.set_edgecolor("#CBD5E1")
        if r_ == 0:
            cel.set_facecolor(AZUL); cel.get_text().set_color("white"); cel.get_text().set_weight("bold")
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(VIS, f"plano_sectorizacion_TBM_OE4.{ext}"), dpi=200 if ext == "png" else None)
    plt.close(fig)

    # ---------------- DXF: perfil a escala horizontal 1:1 (m) y vertical ×5, bandas de sectorización
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.M
    capas = {"TERRENO": 8, "RASANTE": 5, "FALLAS": 1, "TRAMOS": 9, "FAVORABLE": 3, "CONDICIONADA": 40, "DESFAVORABLE": 1, "TEXTO": 7}
    for n, c in capas.items():
        doc.layers.add(n, color=c)
    msp = doc.modelspace()
    V = 5.0  # exageración vertical
    msp.add_lwpolyline([(p["pk"], p["terreno"] * V) for p in puntos], dxfattribs={"layer": "TERRENO"})
    msp.add_lwpolyline([(p["pk"], p["rasante"] * V) for p in puntos], dxfattribs={"layer": "RASANTE"})
    for f in S["fallas"]:
        msp.add_line((f["pk"], 500 * V), (f["pk"], 3600 * V), dxfattribs={"layer": "FALLAS"})
        msp.add_text(f["nombre"], height=250, dxfattribs={"layer": "FALLAS", "rotation": 90}).set_placement((f["pk"] - 120, 600 * V))
    for t in S["tramos"]:
        msp.add_line((t["a"], 500 * V), (t["a"], 3600 * V), dxfattribs={"layer": "TRAMOS", "linetype": "DASHED"})
        msp.add_text(f"{t['tramo']} {t['simbolo']}", height=250, dxfattribs={"layer": "TRAMOS"}).set_placement(((t["a"] + t["b"]) / 2, 3700 * V),
                                                                                                         align=ezdxf.enums.TextEntityAlignment.CENTER)
    y0 = 300 * V
    for i, caso in enumerate(("Típico", "Mínimo", "Máximo")):
        y = y0 - i * 700
        msp.add_text(f"Sectorización · parámetros {caso.lower()}", height=220, dxfattribs={"layer": "TEXTO"}).set_placement((-9000, y + 100))
        for g in S["grupos"][caso]:
            pts = [(g["pk_ini"], y), (g["pk_fin"], y), (g["pk_fin"], y + 450), (g["pk_ini"], y + 450)]
            msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": g["sector"]})
            h = msp.add_hatch(color=capas[g["sector"]], dxfattribs={"layer": g["sector"]})
            h.paths.add_polyline_path(pts, is_closed=True)
    for j in range(0, int(S["longitud_m"]) + 1, 5000):
        msp.add_text(f"K{j // 1000}+000", height=200, dxfattribs={"layer": "TEXTO"}).set_placement((j, y0 - 2300), align=ezdxf.enums.TextEntityAlignment.CENTER)
    msp.add_text("Semillero GEOPAV · Universidad de Ibagué · Ferropista · OE 4 Act 2 · Sectorización para tuneladora · Horizontal en m, vertical ×5 · Esquema conceptual",
                 height=300, dxfattribs={"layer": "TEXTO"}).set_placement((0, y0 - 3200))
    doc.header["$INSUNITS"] = 6
    doc.saveas(SAL_DXF)


if __name__ == "__main__":
    main()
