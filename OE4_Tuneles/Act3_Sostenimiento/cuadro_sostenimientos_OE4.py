# -*- coding: utf-8 -*-
"""OE 4 · Actividad 3 — Paso 2 de 2: «Cuadro de sostenimientos» · Documento PDF.

CONSOLIDA, NO RECALCULA: lee sostenimiento_OE4.json (paso 1), sectorizacion_TBM_OE4.json (Act 2) y
matriz_litologica_OE4.json (Act 1). Dibuja la figura de presión de soporte requerida y arma el PDF con la
plantilla del estándar (OE3_Geotecnia/plantilla_documentos_OE3.py). Salida: Cuadro_sostenimientos_OE4.pdf
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = os.path.dirname(os.path.abspath(__file__))
OE4 = os.path.dirname(AQUI)
RAIZ = os.path.dirname(OE4)
sys.path.insert(0, os.path.join(RAIZ, "OE3_Geotecnia"))
from plantilla_documentos_OE3 import *          # noqa: F401,F403

S3 = json.load(open(os.path.join(AQUI, "sostenimiento_OE4.json"), encoding="utf-8"))
S2 = json.load(open(os.path.join(OE4, "Act2_Sectorizacion", "sectorizacion_TBM_OE4.json"), encoding="utf-8"))
S1 = json.load(open(os.path.join(OE4, "Act1_Litologia", "matriz_litologica_OE4.json"), encoding="utf-8"))
SALIDA = os.path.join(AQUI, "Cuadro_sostenimientos_OE4.pdf")
FIG = os.path.join(OE4, "Visuales", "presion_soporte_OE4.png")
COL = lambda *w: [x * mm for x in w]
km = lambda m: es_co(m / 1000, 1)


def figura_presion():
    pk = [p["pk"] / 1000 for p in S3["puntos"]]
    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    for caso, color, lw in (("min", "#B91C1C", 0.8), ("tip", "#193F77", 1.5), ("max", "#178E2C", 0.8)):
        ax.plot(pk, [max(p[f"pi_fs_{caso}"], 0.01) for p in S3["puntos"]], color=color, lw=lw,
                label={"min": "Parámetros mínimos", "tip": "Parámetros típicos", "max": "Parámetros máximos"}[caso])
    for c in S3["clases"]:
        if c["cap"]:
            ax.axhline(c["cap"], color="#6B7280", lw=0.7, ls="--")
            ax.text(52.4, c["cap"], f" {c['clase']} ({es_co(c['cap'], 2)} MPa)", fontsize=7, va="center", color="#374151")
    for x in S2["grupos"]["Típico"]:
        if x["sector"] == "FAVORABLE":
            ax.axvspan(x["pk_ini"] / 1000, x["pk_fin"] / 1000, color="#DCFCE7", lw=0)
    ax.set_yscale("log"); ax.set_ylim(0.01, 200); ax.set_xlim(0, 52.2)
    ax.set_xlabel("PK (km desde el portal oriental)"); ax.set_ylabel("FS · pi requerida (MPa)")
    ax.legend(fontsize=7.5, loc="upper left", frameon=False)
    ax.grid(True, which="major", lw=0.3, color="#E5E7EB")
    fig.tight_layout(); fig.savefig(FIG, dpi=200); plt.close(fig)


def cuerpo(doc):
    S = []; A = S.append
    D = S3["D_m"]
    A(Paragraph("Marcas de origen: <b>[F]</b> fuente citada · <b>[CP]</b> cálculo propio reproducible · <b>[H]</b> hipótesis declarada.", NOTA))
    A(Paragraph("1. Objeto y alcance", H2))
    A(Paragraph("Este cuadro define, para los tramos del túnel que la Act 2 no asigna a la tuneladora, la clase de sostenimiento primario "
                "que haría falta con método convencional (perforación y voladura o excavación mecánica por fases). Es un nivel conceptual: "
                "los parámetros del macizo son rangos regionales sin sondeos a la profundidad del túnel, por eso se entrega el caso típico "
                "y su sensibilidad a los parámetros mínimos y máximos.", P))
    A(Paragraph("<b>Hallazgo principal.</b> Con parámetros típicos, cerca de "
                f"{km(S3['resumen_m']['Típico']['S-V'])} km del túnel quedan en la clase S-V: la presión de soporte necesaria para "
                "limitar la deformación supera la capacidad de cualquier sostenimiento rígido y hace falta un sostenimiento cedente con "
                "deformación controlada. Coincide con los esquistos del Complejo Cajamarca y del Complejo Quebradagrande bajo coberturas de "
                "500 a 2.000 m. Con parámetros máximos ese tramo baja a "
                f"{km(S3['resumen_m']['Máximo']['S-V'])} km: la exploración decide entre los dos escenarios.", DEST))
    A(Paragraph("2. Método", H2))
    A(Paragraph(f"(1) Resistencia del macizo σcm con la ecuación 1 de Hoek y Marinos (2000) y esfuerzo in situ p0 = γ·H, con la cobertura "
                f"del OE 1 y γ = {S1['gamma_roca_MN_m3']} MN/m³ [H]. (2) Presión de soporte pi que limita la deformación a "
                f"{es_co(S3['eps_obj'], 1)} % (límite de la clase A), despejando por bisección la ecuación 4 de Hoek y Marinos (2000) [CP]. "
                f"(3) Se exige una capacidad de {es_co(S3['FS'], 1)} veces pi [H]. (4) La capacidad de cada clase es la suma de las capacidades "
                f"de sus elementos para el diámetro equivalente D = {es_co(D, 2)} m (área de excavación de la ponencia, dia. 22 [CP]), con las "
                "fórmulas de la figura 8 de Hoek, cap. 12 [F]. (5) En las zonas de falla del MGC 2023 (ancho típico "
                f"{es_co(S2['ancho_falla_m'], 0)} m) la resistencia se reduce como en la Act 2 [H].", P))
    A(Paragraph("Limitaciones del método: la figura 8 supone anillos cerrados y carga simétrica; sumar capacidades de elementos de rigidez "
                "distinta sobreestima la capacidad conjunta; la ecuación 4 es un ajuste a soluciones cerradas de túnel circular en campo "
                "hidrostático. Hoek y Marinos recomiendan análisis numérico donde el squeezing sea significativo.", NOTA))
    titulo_tabla("Capacidad de los elementos de sostenimiento para el diámetro equivalente del túnel", S)
    elem = [("Concreto lanzado 100 mm, 28 días", "7,3·D^-0,98", 7.3 * D ** -0.98), ("Concreto lanzado 150 mm, 28 días", "10,6·D^-0,97", 10.6 * D ** -0.97),
            ("Concreto lanzado 300 mm, 28 días", "19,1·D^-0,92", 19.1 * D ** -0.92), ("Perno de 25 mm, malla 1,0 × 1,0 m", "0,267/s²", 0.267),
            ("Perno de 25 mm, malla 1,5 × 1,5 m", "0,267/s²", 0.267 / 2.25), ("Cercha I 203 mm cada 1,0 m", "11,1·D^-1,33/s", 11.1 * D ** -1.33),
            ("Cercha de ala ancha 305 mm cada 0,75 m", "19,9·D^-1,23/s", 19.9 * D ** -1.23 / 0.75)]
    A(tabla(filas(["Elemento", "Fórmula (fig. 8, Hoek) [F]", f"pimax para D = {es_co(D, 2)} m (MPa) [CP]"],
                  [[a, b, es_co(c, 2)] for a, b, c in elem]), COL(70, 50, 50)))
    A(fuente("Hoek, E. Practical Rock Engineering, cap. 12 «Tunnels in weak rock», figura 8 (leída sobre la imagen renderizada); cálculo propio."))
    A(Paragraph("3. Clases de sostenimiento primario", H2))
    titulo_tabla("Clases de sostenimiento primario y su capacidad", S)
    A(tabla(filas(["Clase", "Sostenimiento primario", "Excavación", "Clase de Hoek y Marinos", "Capacidad (MPa)"],
                  [[c["clase"], c["nombre"], c["excavacion"], c["hm"], es_co(c["cap"], 2) if c["cap"] else "Deformación controlada"] for c in S3["clases"]]),
            COL(14, 70, 44, 20, 22)))
    A(fuente("Composición de clases [H], inspirada en la figura 7 de Hoek y Marinos (2000) [F]; capacidades de la tabla 1 [CP]."))
    A(Paragraph("4. Tramos críticos para excavación convencional (caso típico)", H2))
    titulo_tabla("Tramos con método convencional y su clase de sostenimiento, parámetros típicos", S)
    fil = []
    for x in S3["grupos"]["Típico"]:
        if x["clase"] == "TBM":
            continue
        fil.append([f"K{es_co(x['pk_ini'] / 1000, 3)} – K{es_co(x['pk_fin'] / 1000, 3)}", es_co(x["longitud"], 0), x["clase"],
                    es_co(x["pi_max"], 2), ", ".join(x["tramos"]), "Sí" if x["falla"] else "No"])
    A(tabla(filas(["Abscisas (km)", "Longitud (m)", "Clase", "FS·pi máx. (MPa)", "Tramos litológicos (Act 1)", "Incluye zona de falla"], fil),
            COL(40, 22, 16, 26, 36, 30)))
    A(fuente("sostenimiento_OE4.json [CP]. Tramos de menos de 200 m se asimilan al vecino más desfavorable [H]. Los tramos favorables para tuneladora (Act 2) no se listan."))
    titulo_tabla("Longitud por clase de sostenimiento según el caso de parámetros (km)", S)
    cl = ["TBM"] + [c["clase"] for c in S3["clases"]]
    A(tabla(filas(["Caso"] + ["Tuneladora" if c == "TBM" else c for c in cl],
                  [[caso] + [km(S3["resumen_m"][caso][c]) for c in cl] for caso in ("Mínimo", "Típico", "Máximo")]), COL(26, 24, 20, 20, 20, 20, 20)))
    A(fuente("sostenimiento_OE4.json [CP]. Los tramos para tuneladora son los del caso típico de la Act 2 en los tres casos."))
    figura(FIG, "Presión de soporte requerida (FS·pi) a lo largo del túnel y capacidad de las clases S-I a S-IV",
           "sostenimiento_OE4.py y cuadro_sostenimientos_OE4.py [CP]; en verde claro, tramos favorables para tuneladora (Act 2)", S, 160 * mm, 160 * mm * 4.2 / 9.5)
    A(Paragraph("5. Lo que enseña el Túnel de La Línea", H2))
    A(Paragraph("El Túnel de La Línea cruza el mismo macizo unos 1.000 m por encima de la rasante (Act 1). Dávila (2015) reporta que en la "
                "Falla de La Soledad la solera plana instalada durante la excavación de la sección superior falló por grandes deformaciones, "
                "que el análisis indicó que el sostenimiento inicial debía cerrarse con solera curva, y recomienda un revestimiento final "
                "continuo de concreto con solera en todo el túnel [F]. Por eso las clases S-III a S-V de este cuadro cierran el anillo con "
                "contrabóveda. Con coberturas hasta dos veces mayores que las de La Línea, las deformaciones en este túnel serían mayores.", P))
    A(Paragraph("6. Qué no afirma este cuadro", H2))
    for t in ["No es un diseño de sostenimiento: no hay RMR, Q ni GSI medidos a la cota del túnel; el GSI es una hipótesis por litología.",
              "No considera agua a presión ni el efecto de la orientación de la foliación, que en esquistos controla la sobreexcavación.",
              "Las capacidades son de anillos cerrados en carga simétrica; en la práctica son menores.",
              "La exploración que lo convierte en diseño: sondeos profundos orientados en los tramos T4, T6 y T7, galerías piloto (como en La Línea), "
              "ensayos triaxiales y de fluencia en esquistos grafíticos, medición del esfuerzo in situ y monitoreo de convergencias."]:
        A(Paragraph("• " + t, P))
    A(Paragraph("<i>Nota de elaboración: preparado con apoyo de IA (Claude, de Anthropic). Cada cifra se lee de los JSON de los scripts citados; "
                "las fórmulas se verificaron sobre las imágenes de las fuentes.</i>", ParagraphStyle("NE", parent=FUENTE, spaceBefore=0, spaceAfter=0)))
    A(Paragraph("Referencias", H2))
    for r_ in ["Hoek, E. y Marinos, P. (2000). Predicting tunnel squeezing problems in weak heterogeneous rock masses. Tunnels and Tunnelling International. "
               "https://static.rocscience.cloud/assets/resources/learning/hoek/Predicting-Tunnel-Squeezing-Problems-in-Weak-Heterogeneous-Rock-Masses-2000.pdf",
               "Hoek, E. Practical Rock Engineering, cap. 12 «Tunnels in weak rock». https://static.rocscience.cloud/assets/resources/learning/hoek/Practical-Rock-Engineering-Chapter-12-Tunnels-in-Weak-Rock-Remediated.pdf",
               "Dávila, H. (2015). Túnel II Centenario, terrenos encontrados y su análisis de comportamiento en el corto y largo plazo. Revista Vial.",
               "Fernández Ordóñez, H. O. (2025). Túnel para cruce férreo de la Cordillera Central de los Andes. XX Seminario Andino de Túneles, SAI. Dia. 22.",
               "Semillero GEOPAV (2026). OE 4, Act 1 (matriz litológica) y Act 2 (sectorización para tuneladora)."]:
        A(Paragraph(r_, NOTA))
    return S


figura_presion()
META = {"rotulo": "OE 4 · Actividad 3 · Producto", "titulo": "Cuadro de sostenimientos del túnel",
        "subtitulo": "Tramos críticos para excavación convencional y su sostenimiento primario",
        "ficha": [("Objetivo específico", "OE 4 — Estructurar la metodología de excavación recomendada, contrastando el método mecanizado con tuneladora frente al método convencional"),
                  ("Actividad", "Act 3. Definición de los tramos críticos para excavación convencional y de su sostenimiento primario"),
                  ("Entregable / formato", "Cuadro de sostenimientos · Documento Word / PDF"),
                  ("Periodo", "Bloque 2 del cronograma: 5 oct – 7 nov 2026"),
                  ("Responsable asignado", "Castaño Cifuentes Maicol Stiven"),
                  ("Apoyo en la ejecución", "Tamayo Osorio Miguel Ángel, con apoyo de IA (Claude)")],
        "pie": "Semillero GEOPAV · Ferropista Cordillera Central · OE 4 – Act 3", "fecha": "Septiembre de 2026",
        "titulo_pdf": "Cuadro de sostenimientos - OE 4 Act 3 - Semillero GEOPAV"}
generar(SALIDA, META, cuerpo)
print("PDF escrito:", SALIDA)
