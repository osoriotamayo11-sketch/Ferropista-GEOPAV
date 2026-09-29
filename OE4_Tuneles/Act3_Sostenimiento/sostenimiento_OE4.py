# -*- coding: utf-8 -*-
"""
OE 4 · Actividad 3 — Definición de los tramos críticos para excavación convencional y de su sostenimiento primario.
Paso 1 de 2 (cálculo): produce sostenimiento_OE4.json, que consume cuadro_sostenimientos_OE4.py (PDF).

Entradas: ../Act2_Sectorizacion/sectorizacion_TBM_OE4.json (sectores, ε y p0 por abscisa) y
          ../Act1_Litologia/matriz_litologica_OE4.json (parámetros de macizo). Ninguna cifra geológica a mano.
Método por abscisa (caso TÍPICO de parámetros; mínimo y máximo como sensibilidad):
  1. σcm y p0 como en la Act 2 (Hoek y Marinos, 2000, ec. 1; p0 = γ·H).
  2. Presión de soporte pi necesaria para limitar la deformación a ε_obj (%), despejando la ec. 4 de
     Hoek y Marinos (2000):  δi/do = (0,002 − 0,0025·pi/po)·(σcm/po)^(2,4·pi/po − 2)   (bisección) [F→CP]
  3. Capacidad de cada clase de sostenimiento = suma de las capacidades de sus elementos para el diámetro
     equivalente D de la Act 2, con las fórmulas de la figura 8 de Hoek (Practical Rock Engineering, cap. 12),
     leídas sobre la imagen renderizada [F]. Sumar capacidades de elementos de distinta rigidez es una
     simplificación optimista [H], y la figura supone anillo cerrado y carga simétrica (Hoek la advierte).
  4. Clase asignada = la más liviana cuya capacidad ≥ FS · pi requerida. Si ninguna alcanza: clase S-V (soporte
     cedente / deformación controlada), que Hoek y Marinos asocian a la clase E y exige análisis numérico.
Umbrales y combinaciones = hipótesis [H], editables en un solo sitio (CLASES_SOPORTE, EPS_OBJ, FS).
"""
import json
import math
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
OE4 = os.path.dirname(AQUI)
ACT1 = os.path.join(OE4, "Act1_Litologia", "matriz_litologica_OE4.json")
ACT2 = os.path.join(OE4, "Act2_Sectorizacion", "sectorizacion_TBM_OE4.json")
SALIDA = os.path.join(AQUI, "sostenimiento_OE4.json")

EPS_OBJ = 1.0      # %, deformación objetivo con soporte: límite de la clase A de Hoek y Marinos (2000) [H]
FS = 1.5           # factor sobre la presión requerida [H]
L_MIN = 200.0      # m, longitud mínima de tramo (igual que la Act 2) [H]
CASOS = ("Mínimo", "Típico", "Máximo")
SUF = {"Mínimo": "min", "Típico": "tip", "Máximo": "max"}


# Figura 8 de Hoek, cap. 12 — pimax (MPa) para un túnel de diámetro D (m) y espaciamiento s (m) [F]
def lanzado(esp_mm, D):
    k = {50: (3.8, -0.99), 100: (7.3, -0.98), 150: (10.6, -0.97), 300: (19.1, -0.92)}[esp_mm]
    return k[0] * D ** k[1]


def cercha_wf305(D, s):      # ala ancha 305 mm, 97 kg/m (curva 1)
    return 19.9 * D ** -1.23 / s


def cercha_i203(D, s):       # sección I 203 mm, 52 kg/m (curva 5)
    return 11.1 * D ** -1.33 / s


def pernos25(s):             # perno de 25 mm en malla s × s (curva 11)
    return 0.267 / s ** 2


def clases_soporte(D):
    return [
        dict(clase="S-I", nombre="Pernos de 25 mm en malla de 1,5 × 1,5 m + concreto lanzado de 100 mm", cap=pernos25(1.5) + lanzado(100, D),
             excavacion="Sección completa o bóveda y banco; avance 3-4 m", hm="A"),
        dict(clase="S-II", nombre="Pernos de 25 mm en malla de 1,0 × 1,0 m + concreto lanzado de 150 mm con fibra", cap=pernos25(1.0) + lanzado(150, D),
             excavacion="Bóveda y banco; avance 2-3 m", hm="B"),
        dict(clase="S-III", nombre="Cerchas I 203 mm cada 1,0 m + concreto lanzado de 300 mm + pernos de 25 mm a 1,0 m", cap=cercha_i203(D, 1.0) + lanzado(300, D) + pernos25(1.0),
             excavacion="Bóveda y banco con contrabóveda (solera) cerrada pronto; avance 1-1,5 m", hm="C"),
        dict(clase="S-IV", nombre="Cerchas de ala ancha 305 mm cada 0,75 m embebidas en concreto lanzado de 300 mm + contrabóveda + paraguas de micropilotes y refuerzo del frente",
             cap=cercha_wf305(D, 0.75) + lanzado(300, D), excavacion="Secciones parciales; avance ≤ 1 m; presostenimiento", hm="D"),
        dict(clase="S-V", nombre="Soporte cedente (cerchas con juntas deslizantes o elementos compresibles) con sobreexcavación, refuerzo del frente y revestimiento diferido",
             cap=None, excavacion="Deformación controlada; diseño por análisis numérico 3D", hm="E"),
    ]


def pi_requerida(scm, p0, eps_obj):
    """pi (MPa) tal que la ec. 4 de HM00 dé ε = eps_obj. 0 si sin soporte ya cumple."""
    if p0 <= 0:
        return 0.0
    r = scm / p0

    def eps(pi):
        x = pi / p0
        return 100 * (0.002 - 0.0025 * x) * r ** (2.4 * x - 2)

    if eps(0) <= eps_obj:
        return 0.0
    lo, hi = 0.0, 0.8 * p0          # la ec. 4 se anula en pi/p0 = 0,8
    for _ in range(100):
        mid = (lo + hi) / 2
        if eps(mid) > eps_obj:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def main():
    A1 = json.load(open(ACT1, encoding="utf-8"))
    A2 = json.load(open(ACT2, encoding="utf-8"))
    D = A2["D_eq_m"]
    CL = clases_soporte(D)
    gamma = A1["gamma_roca_MN_m3"]
    tramos = {t["tramo"]: t for t in A1["tramos"]}
    zf = A1["zona_falla"]

    def sigma_cm(sci, mi, gsi):
        return 0.0034 * mi ** 0.8 * sci * (1.029 + 0.025 * math.exp(-0.1 * mi)) ** gsi

    puntos = []
    for p in A2["puntos"]:
        t = tramos[p["tramo"]]
        fila = dict(pk=p["pk"], H=p["H"], tramo=p["tramo"], en_falla=p["en_falla"], sector_tip=p["sector_tip"])
        for ci, caso in enumerate(CASOS):
            p0 = gamma * p["H"]
            peor = None
            for jg in t["juegos"]:
                sci, mi, gsi = jg["sci"][ci], jg["mi"][ci], jg["gsi"][ci]
                if p["en_falla"]:
                    sci, gsi = sci * zf["sci_factor"], zf["gsi"][ci]
                scm = sigma_cm(sci, mi, gsi)
                pi = pi_requerida(scm, p0, EPS_OBJ)
                if peor is None or pi > peor["pi"]:
                    peor = dict(juego=jg["id"], scm=scm, pi=pi)
            req = FS * peor["pi"]
            cl = next((c for c in CL if c["cap"] is not None and c["cap"] >= req), CL[-1])
            if req == 0:
                cl = CL[0]
            fila[caso] = dict(p0=p0, **peor, pi_fs=req, clase=cl["clase"])
        puntos.append(fila)

    # tramos continuos por clase (solo donde la Act 2 dice método convencional, caso típico)
    def agrupar(caso, solo_conv):
        g = []
        tbm = [(x["pk_ini"], x["pk_fin"]) for x in A2["grupos"]["Típico"] if x["sector"] == "FAVORABLE"]
        for i, pt in enumerate(puntos):
            conv = not any(a <= pt["pk"] <= b for a, b in tbm)
            c = pt[caso]["clase"] if (conv or not solo_conv) else "TBM"
            pk0 = pt["pk"] if i == 0 else (puntos[i - 1]["pk"] + pt["pk"]) / 2
            pk1 = pt["pk"] if i == len(puntos) - 1 else (pt["pk"] + puntos[i + 1]["pk"]) / 2
            if g and g[-1]["clase"] == c:
                g[-1]["pk_fin"] = pk1
                g[-1]["pi_max"] = max(g[-1]["pi_max"], pt[caso]["pi_fs"])
                g[-1]["tramos"].add(pt["tramo"])
                g[-1]["falla"] |= pt["en_falla"]
            else:
                g.append(dict(clase=c, pk_ini=pk0, pk_fin=pk1, pi_max=pt[caso]["pi_fs"], tramos={pt["tramo"]}, falla=pt["en_falla"]))
        orden = {"TBM": -1, "S-I": 0, "S-II": 1, "S-III": 2, "S-IV": 3, "S-V": 4}
        cambio = True
        while cambio:
            cambio = False
            for i, x in enumerate(g):
                if x["pk_fin"] - x["pk_ini"] < L_MIN and len(g) > 1 and x["clase"] != "TBM":
                    vec = [v for v in (g[i - 1] if i > 0 else None, g[i + 1] if i + 1 < len(g) else None) if v and v["clase"] != "TBM"]
                    if not vec:
                        continue
                    dest = max(vec, key=lambda v: orden[v["clase"]])
                    dest["clase"] = max((dest["clase"], x["clase"]), key=lambda c: orden[c])
                    dest["pk_ini"], dest["pk_fin"] = min(dest["pk_ini"], x["pk_ini"]), max(dest["pk_fin"], x["pk_fin"])
                    dest["pi_max"] = max(dest["pi_max"], x["pi_max"]); dest["tramos"] |= x["tramos"]; dest["falla"] |= x["falla"]
                    g.pop(i)
                    j = 0
                    while j < len(g) - 1:
                        if g[j]["clase"] == g[j + 1]["clase"]:
                            g[j]["pk_fin"] = g[j + 1]["pk_fin"]; g[j]["pi_max"] = max(g[j]["pi_max"], g[j + 1]["pi_max"])
                            g[j]["tramos"] |= g[j + 1]["tramos"]; g[j]["falla"] |= g[j + 1]["falla"]; g.pop(j + 1)
                        else:
                            j += 1
                    cambio = True
                    break
        for x in g:
            x["longitud"] = x["pk_fin"] - x["pk_ini"]
            x["tramos"] = sorted(x["tramos"])
        return g

    grupos = {c: agrupar(c, True) for c in CASOS}
    resumen = {c: {k["clase"]: sum(x["longitud"] for x in grupos[c] if x["clase"] == k["clase"]) for k in CL} for c in CASOS}
    for c in CASOS:
        resumen[c]["TBM"] = sum(x["longitud"] for x in grupos[c] if x["clase"] == "TBM")
    salida = dict(generado_por="OE4_Tuneles/Act3_Sostenimiento/sostenimiento_OE4.py", D_m=D, eps_obj=EPS_OBJ, FS=FS, L_min=L_MIN,
                  clases=CL, grupos=grupos, resumen_m=resumen,
                  puntos=[dict(pk=p["pk"], H=p["H"], tramo=p["tramo"], sector_tip=p["sector_tip"],
                               **{f"{k}_{SUF[c]}": p[c][k] for c in CASOS for k in ("pi_fs", "clase")}) for p in puntos])
    json.dump(salida, open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("D", round(D, 2), {c["clase"]: (round(c["cap"], 2) if c["cap"] else None) for c in CL})
    for c in CASOS:
        print(c, {k: round(v) for k, v in resumen[c].items()})
    for x in grupos["Típico"]:
        print(round(x["pk_ini"]), round(x["pk_fin"]), x["clase"], round(x["pi_max"], 2), x["tramos"], x["falla"])


if __name__ == "__main__":
    main()
