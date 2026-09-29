# -*- coding: utf-8 -*-
"""OE 6 · Actividad 5 — «Informe económico-logístico» · Documento PDF (reporte de eficiencia logística comparada).

CONSOLIDA, NO RECALCULA. Lee los JSON de las Act 1-4 del OE 6, dibuja dos figuras (Visuales/) y arma el PDF con la
plantilla del semillero (OE3_Geotecnia/plantilla_documentos_OE3.py). Salida: Informe_economico_logistico_OE6.pdf
Requiere reportlab, matplotlib, pypdf.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
OE6 = os.path.dirname(AQUI)
RAIZ = os.path.dirname(OE6)
sys.path.insert(0, OE6)
sys.path.insert(0, os.path.join(RAIZ, "OE3_Geotecnia"))
import comun_OE6 as C  # noqa: E402
from plantilla_documentos_OE3 import *  # noqa: E402,F401,F403

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

A1 = C.leer_json("Act1_TiemposRuta40", "registro_tiempos_ruta40_OE6.json")
A2 = C.leer_json("Act2_TiempoFerropista", "tiempo_ciclo_ferropista_OE6.json")
A3 = C.leer_json("Act3_CostosUnitarios", "matriz_costos_unitarios_OE6.json")
A4 = C.leer_json("Act4_Ahorros", "modelo_ahorros_OE6.json")
VIS = os.path.join(OE6, "Visuales")
SALIDA = os.path.join(AQUI, "Informe_economico_logistico_OE6.pdf")
COL = lambda *w: [x * mm for x in w]
K = list(C.RUTAS)
AZ, GR, TX = "#193F77", "#94A3B8", "#1F2933"
e1, e0, e2 = (lambda v: C.es(v, 1)), (lambda v: C.es(v, 0)), (lambda v: C.es(v, 2))
pesos = lambda v: "$ " + C.es(v, 0)


def figuras():
    os.makedirs(VIS, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": "#CBD5E1", "axes.labelcolor": TX,
                         "xtick.color": "#475569", "ytick.color": "#475569"})
    # Figura 1 · tiempos
    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=200)
    y = 0
    ticks, labs = [], []
    for k in K:
        for nombre, H, col in [("Ruta 40", A1["sentidos"][k]["horas"], GR), ("Ferropista", A2["sentidos"][k]["horas"], AZ)]:
            ax.barh(y, H["Típico"], height=0.62, color=col, zorder=2)
            ax.plot([H["Mínimo"], H["Máximo"]], [y, y], color=TX, lw=1.2, zorder=3)
            for xx in (H["Mínimo"], H["Máximo"]):
                ax.plot([xx, xx], [y - 0.16, y + 0.16], color=TX, lw=1.2, zorder=3)
            ax.text(H["Máximo"] + 0.08, y, f"{e2(H['Típico'])} h  (rango {e2(H['Mínimo'])}–{e2(H['Máximo'])})", va="center", fontsize=8.5, color=TX)
            ticks.append(y); labs.append(f"{A1['sentidos'][k]['ruta']}\n{nombre}")
            y += 0.8
        y += 0.5
    ax.set_yticks(ticks, labs, fontsize=8.5); ax.invert_yaxis()
    ax.set_xlabel("Horas de cabecera a cabecera (sin cargue ni descargue de la mercancía)")
    ax.set_xlim(0, 7.6); ax.grid(axis="x", color="#E2E8F0", zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); f1 = os.path.join(VIS, "tiempos_ciclo_OE6.png"); fig.savefig(f1); plt.close(fig)
    # Figura 2 · costo por cruce
    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=200)
    y = 0
    ticks, labs = [], []
    for k in K:
        R = A4["sentidos"][k]["rangos"]
        for nombre, key, col in [("Ruta 40", "c_carretera", GR), ("Ferropista sin tarifa", "c_ferropista_sin_tarifa", AZ)]:
            v = {x: R[x][key] / 1000 for x in R}
            lo, hi = min(v.values()), max(v.values())
            ax.barh(y, v["Central"], height=0.62, color=col, zorder=2)
            ax.plot([lo, hi], [y, y], color=TX, lw=1.2, zorder=3)
            for xx in (lo, hi):
                ax.plot([xx, xx], [y - 0.16, y + 0.16], color=TX, lw=1.2, zorder=3)
            ax.text(hi + 12, y, f"{e0(v['Central'])} mil $  (rango {e0(lo)}–{e0(hi)})", va="center", fontsize=8.5, color=TX)
            ticks.append(y); labs.append(f"{A1['sentidos'][k]['ruta']}\n{nombre}")
            y += 0.8
        y += 0.5
    ax.set_yticks(ticks, labs, fontsize=8.5); ax.invert_yaxis()
    ax.set_xlabel("Costo de operación de un cruce, tractocamión 3S3 (miles de $ de sep 2026)")
    ax.set_xlim(0, 1650); ax.grid(axis="x", color="#E2E8F0", zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); f2 = os.path.join(VIS, "costo_cruce_OE6.png"); fig.savefig(f2); plt.close(fig)
    return f1, f2


def cuerpo(doc):
    f1, f2 = figuras()
    S = []; A = S.append
    s1, s2 = (A1["sentidos"][k] for k in K)
    f_1, f_2 = (A2["sentidos"][k] for k in K)
    p1, p2 = (A4["sentidos"][k]["rangos"] for k in K)
    u = A3["unitarios"]
    an30 = A4["anual"]["2030"]
    A(Paragraph("Marcas de origen: <b>[F]</b> fuente citada · <b>[CP]</b> cálculo propio reproducible · <b>[H]</b> hipótesis declarada · <b>[DA]</b> dato pendiente.", NOTA))
    A(Paragraph("1. Objeto, alcance y resultado", H2))
    A(Paragraph("Este informe cierra el OE 6. Compara el cruce de un tractocamión entre Ibagué y Calarcá por la Ruta 40 con el mismo cruce usando la "
                "Ferropista, en tiempo de ciclo y en costo de operación, y proyecta el ahorro anual para el sector transportador. Todo cálculo sale de "
                "fuentes oficiales descargadas (SICE-TAC del Ministerio de Transporte, INVÍAS, CAF) y de la fuente primaria del proyecto; lo que ninguna "
                "fuente dice se declara como hipótesis.", P))
    A(Paragraph(f"<b>Resultado.</b> En el escenario típico, el cruce pasa de {e2(s1['horas']['Típico'])} h por carretera a {e2(f_1['horas']['Típico'])} h con "
                f"Ferropista (−{e0(100 * f_1['reduccion_pct']['Central'])} %), no a 70 min como dice la fuente: a los 70 min de operación ferroviaria hay "
                f"que sumarles unos {e0(f_1['km_acceso'])} km de acceso por carretera y la espera del tren. Si la carretera funciona en flujo libre, la "
                f"ventaja en tiempo casi desaparece ({e2(p1['Bajo']['dh'])} h hacia Calarcá y {e2(p2['Bajo']['dh'])} h hacia Ibagué). En costo, la "
                f"Ferropista sí es claramente más barata porque el camión no quema combustible en la montaña ni paga peajes: el ahorro bruto por cruce, "
                f"antes de la tarifa del servicio, va de {pesos(min(p1['Bajo']['tarifa_indiferencia'], p2['Bajo']['tarifa_indiferencia']))} a "
                f"{pesos(max(p1['Alto']['tarifa_indiferencia'], p2['Alto']['tarifa_indiferencia']))}. Con la demanda del proponente, en 2030 suma entre "
                f"{e0(an30['rangos']['Bajo']['ahorro_bruto'] / 1e9)} y {e0(an30['rangos']['Alto']['ahorro_bruto'] / 1e9)} mil millones de pesos al año, "
                f"frente a los 2,5 billones que afirma la fuente.", DEST))
    # 2
    A(Paragraph("2. Tiempo de ciclo actual por la Ruta 40 (Act 1)", H2))
    A(Paragraph("Se tomaron las rutas oficiales del SICE-TAC 14037 (Ibagué → Calarcá) y 15393 (Calarcá → Ibagué) con sus kilómetros por tipo de "
                "terreno y las velocidades promedio del tractocamión 3S3 cargado. Los dos sentidos no miden lo mismo: "
                f"{e2(s1['km_total'])} km de ida y {e2(s2['km_total'])} km de regreso; OpenStreetMap confirma la asimetría. Se definieron tres escenarios:", P))
    titulo_tabla("Tiempo de cruce cabecera–cabecera por la Ruta 40, tractocamión 3S3", S)
    A(tabla(filas(["Escenario", s1["ruta"], s2["ruta"], "Cómo se obtiene", "Marca"],
                  [["Mínimo", f"{e2(s1['horas']['Mínimo'])} h", f"{e2(s2['horas']['Mínimo'])} h", "Modelo SICE-TAC en flujo libre (Σ km / velocidad por terreno)", "[F→CP]"],
                   ["Típico", f"{e2(s1['horas']['Típico'])} h", f"{e2(s2['horas']['Típico'])} h", "«Paso actual: 4 horas (valor medio)»", "[F, dia. 29]"],
                   ["Máximo", f"{e2(s1['horas']['Máximo'])} h", f"{e2(s2['horas']['Máximo'])} h", "Típico + 1 h del pare y siga con alternancia horaria (INVÍAS, jul–sep 2026)", "[F→CP]"]]),
            COL(20, 26, 26, 76, 22)))
    A(fuente("Registro_tiempos_ciclo_Ruta40_OE6.xlsx (Act 1), con el SICE-TAC (periodo 20260901), la ponencia y el INVÍAS."))
    A(Paragraph("Los 4 h de la fuente equivalen a unos 20 km/h de velocidad media, coherentes con su propia afirmación «&lt; 20 km/h» (dia. 13). Los "
                "ahorros que INVÍAS (≈ 50 min) y CAF (80 min, impacto esperado sin línea base) atribuyen al Túnel de La Línea solo cubren el tramo "
                "Cajamarca–Calarcá y se usan como control. Los trancones de 8 a 10 h reportados en septiembre de 2026 por el alcalde de Cajamarca se "
                "registran como evento extremo y no entran al promedio.", P))
    # 3
    A(Paragraph("3. Tiempo de ciclo con Ferropista (Act 2)", H2))
    A(Paragraph(f"La fuente da el ciclo de operación: peaje y carga 25 min, desplazamiento 30 min y descarga 15 min, en total 70 min (dia. 23), con "
                f"{A2['trenes_dia']} trenes/día de hasta {A2['camiones_tren']} tractomulas (dia. 20). No dice dónde quedan las terminales ni cómo "
                f"se reparten los trenes. Se supuso que las terminales están en los portales del OE 1 y que los trenes se reparten por igual entre "
                f"sentidos durante 24 h, lo que da un tren cada {e1(A2['intervalo_min'])} min. Los accesos cabecera–terminal suman "
                f"{e1(f_1['km_acceso'])} km por sentido (OpenStreetMap), recorridos a las velocidades del SICE-TAC.", P))
    titulo_tabla("Tiempo de ciclo con Ferropista y reducción frente a la Ruta 40", S)
    rows = []
    for k in K:
        f = A2["sentidos"][k]
        for x, (er, ef) in {"Bajo": ("Mínimo", "Máximo"), "Central": ("Típico", "Típico"), "Alto": ("Máximo", "Mínimo")}.items():
            rows.append([f["ruta"], x, f"{e2(f['horas_carretera'][er])} h", f"{e2(f['horas'][ef])} h", f"{e2(f['reduccion_h'][x])} h", f"{e0(100 * f['reduccion_pct'][x])} %"])
    A(tabla(filas(["Sentido", "Rango", "Ruta 40", "Ferropista", "Reducción", "Reducción (%)"], rows), COL(34, 20, 24, 26, 24, 24)))
    A(fuente("Memoria_tiempos_logisticos_OE6.xlsx (Act 2). Bajo = carretera mínima frente a Ferropista máxima; alto = al revés [CP]."))
    figura(f1, "Tiempo de cruce por la Ruta 40 y con Ferropista (barra = típico; línea = mínimo–máximo)",
           "Act 1 y Act 2 del OE 6 [CP], con SICE-TAC, ponencia (dia. 20, 23 y 29), INVÍAS y OpenStreetMap.", S, 165 * mm, 82.5 * mm)
    # 4
    A(Paragraph("4. Costos operativos unitarios (Act 3)", H2))
    A(Paragraph("El SICE-TAC es el sistema oficial de costos eficientes del transporte de carga por carretera. Se consultó para un tractocamión 3S3 "
                "portacontenedor con contenedor cargado en las dos rutas y se descompuso su costo en unidades: una hora de vehículo (costos fijos) y "
                "un kilómetro recorrido (combustible, llantas, mantenimiento y demás). Con esas unidades se reprodujo el costo que publica el "
                f"Ministerio con una diferencia máxima de {C.es(100 * max(abs(v) for s in A3['sentidos'].values() for v in s['error_rel'].values()), 4)} %.", P))
    titulo_tabla("Costos unitarios del tractocamión 3S3 (pesos de septiembre de 2026)", S)
    A(tabla(filas(["Unidad de costo", "Valor", "Nota"],
                  [["Costo fijo por hora de vehículo", pesos(u["cf_hora"]) + "/h", "Capital, salario, seguros, impuestos y demás, entre 230 h hábiles al mes"],
                   ["Costo por hora con otros costos", pesos(u["costo_hora_total"]) + "/h", "Coincide con el «costo hora» publicado"],
                   ["Variable por km sin combustible", pesos(u["cv_km_sin_comb"]) + "/km", "Llantas, lubricantes, filtros, mantenimiento, lavado + 7,5 % de imprevistos"],
                   ["Combustible, terreno plano", pesos(u["comb_km"]["Plano"]) + "/km", f"ACPM {pesos(A3['sentidos']['IBG_CAL']['insumos']['acpm'])}/galón"],
                   ["Combustible, terreno montañoso", pesos(u["comb_km"]["Montaña"]) + "/km", "El doble que en plano"],
                   ["Factor de otros costos", f"{C.es(100 * u['f_otros'], 2)} %", "Comisiones y prestaciones, administrativo, retefuente e ICA"],
                   ["Peajes Ibagué → Calarcá / regreso", f"{pesos(A3['sentidos']['IBG_CAL']['insumos']['v_peajes'])} / {pesos(A3['sentidos']['CAL_IBG']['insumos']['v_peajes'])}", "Cocora solo cobra en sentido Ibagué–Cajamarca"]]),
            COL(56, 36, 78)))
    A(fuente("Matriz_costos_unitarios_OE6.xlsx (Act 3), con el SICE-TAC (Mintransporte, periodo 20260901) [F→CP]."))
    # 5
    A(Paragraph("5. Ahorros operativos (Act 4)", H2))
    A(Paragraph("El costo de un cruce por carretera suma horas de vehículo, combustible por terreno, desgaste por kilómetro y peajes. Con Ferropista, el "
                "camión sigue pagando sus horas (va sobre el tren), pero no gasta combustible ni se desgasta en la montaña; solo recorre los accesos. "
                "La fuente no publica la tarifa del servicio, así que se calculó la <b>tarifa de indiferencia</b>: la máxima con la que al "
                "transportador le da igual una opción u otra, que es también el ahorro bruto a repartir entre el operador y el transportador. "
                "Es el principio que la propia fuente declara: «Peaje más bajo que los costos operacionales de la vía alternativa» (dia. 19).", P))
    titulo_tabla("Costo de un cruce y tarifa de indiferencia por sentido y rango", S)
    rows = []
    for k in K:
        for x, y in A4["sentidos"][k]["rangos"].items():
            rows.append([A4["sentidos"][k]["ruta"], x, pesos(y["c_carretera"]), pesos(y["c_ferropista_sin_tarifa"]), pesos(y["tarifa_indiferencia"]), f"{e0(100 * y['reduccion_pct_sin_tarifa'])} %"])
    A(tabla(filas(["Sentido", "Rango", "Ruta 40", "Ferropista sin tarifa", "Tarifa de indiferencia", "Reducción"], rows), COL(32, 18, 28, 32, 36, 24)))
    A(fuente("Modelo_ahorros_operativos_OE6.xlsx (Act 4) [CP]."))
    figura(f2, "Costo de operación de un cruce por la Ruta 40 y con Ferropista antes de tarifa (barra = central; línea = rango)",
           "Act 4 del OE 6 [CP], con costos eficientes SICE-TAC (sep 2026).", S, 165 * mm, 82.5 * mm)
    titulo_tabla("Proyección anual con la demanda de la fuente (tractocamiones)", S)
    rows = []
    for a in ("2026", "2030"):
        v = A4["anual"][a]
        for x, y in v["rangos"].items():
            rows.append([a, e0(v["camiones_dia_captados"]), x, e0(y["ahorro_bruto"] / 1e9), e2(y["horas_grandes"] / 1e6), e0(y["ahorro_transportador"]["0.5"] / 1e9)])
    A(tabla(filas(["Año", "Camiones/día captados", "Rango", "Ahorro bruto (miles de millones $)", "Horas ahorradas (millones)", "Con tarifa al 50 % (miles de millones $)"], rows),
            COL(16, 26, 18, 38, 32, 40)))
    A(fuente("Modelo_ahorros_operativos_OE6.xlsx (Act 4): 2.100 grandes camiones/día (INVÍAS 2017), 3 % anual y 90 % de captación [F, dia. 10]; "
             "mitad por sentido [H]; pesos constantes de sep 2026 [H]."))
    A(Paragraph(f"La demanda captada en 2030 ({e0(an30['camiones_dia_captados'])} camiones/día) ocupa el {e0(100 * an30['ocupacion_capacidad'])} % de la "
                f"capacidad de la fase inicial ({e0(A2['capacidad_camiones_dia'])} camiones/día): la capacidad no limita.", P))
    # 6
    A(Paragraph("6. Contraste con las cifras de la fuente", H2))
    c30 = an30["rangos"]
    titulo_tabla("Cifras de la fuente frente a este análisis (año 2030)", S)
    A(tabla(filas(["Indicador", "Fuente", "Este análisis", "Lectura"],
                  [["Tiempo de cruce", "4 h → 70 min (−71 %) [F, dia. 29]", f"{e2(s1['horas']['Típico'])} h → {e2(f_1['horas']['Típico'])} h (−{e0(100 * f_1['reduccion_pct']['Central'])} %)",
                    "La fuente omite accesos y espera del tren"],
                   ["Horas ahorradas al año", "5,0 M h (dia. 28); la dia. 29 rotula 5,3", f"{e2((c30['Central']['horas_grandes'] + c30['Central']['horas_medianos_H']) / 1e6)} M h (central, grandes + medianos [H])",
                    "No alcanza con camiones; la fuente no dice qué vehículos cuenta"],
                   ["Ahorro del sector transporte", "$COP 2,5 billones [F, dia. 28]", f"{C.es(c30['Bajo']['ahorro_bruto'] / 1e12, 2)} a {C.es(c30['Alto']['ahorro_bruto'] / 1e12, 2)} billones (bruto, tractocamiones)",
                    "Solo costos de operación; sin valor del tiempo de la carga ni externalidades"]]),
            COL(32, 42, 50, 46)))
    A(fuente("Ponencia (dia. 28 y 29) [F]; Act 1, 2 y 4 del OE 6 [CP]."))
    A(Paragraph("La diferencia no prueba que la fuente esté equivocada: la fuente no explica cómo obtuvo sus cifras (qué vehículos, qué valor del "
                "tiempo, qué año de precios). Muestra, en cambio, qué parte se puede reproducir con datos oficiales de costo de operación: entre el "
                f"{e0(100 * c30['Bajo']['ahorro_bruto'] / (A4['contraste_fuente']['ahorro_bill_dia28'] * 1e12))} % y el {e0(100 * c30['Alto']['ahorro_bruto'] / (A4['contraste_fuente']['ahorro_bill_dia28'] * 1e12))} % del ahorro anunciado.", P))
    # 7
    A(Paragraph("7. Hipótesis y limitaciones", H2))
    for t in ["Las terminales se suponen en los portales del OE 1 [H]. El portal oriental queda sobre una vía rural (Vía a la Montañita); una terminal para "
              "trenes de 35 tractomulas exigiría accesos nuevos o mejorados que aquí no se costean.",
              "140 trenes/día repartidos por igual entre sentidos y 24 h de servicio [H]. Con menos horas de operación, la espera del tren crece.",
              "La tarifa de la Ferropista no es pública: el ahorro calculado es un techo que se reparte entre operador y transportador.",
              "Un solo vehículo representativo (3S3 portacontenedor, costos eficientes SICE-TAC). Los costos eficientes son un piso regulatorio, no el "
              "costo observado de una flota.",
              "El combustible y el desgaste dependen de los kilómetros y del terreno, no de la demora [H]; en congestión real el consumo sube, así que "
              "el ahorro por carretera congestionada está subestimado.",
              "La demanda es la del proponente (INVÍAS 2017 proyectado al 3 %). Los 90 % de captación de 2030 se aplican también a 2026 [H].",
              "No se incluyen el valor del tiempo de la carga ni de los conductores más allá del costo laboral del SICE-TAC, ni la siniestralidad (OE 5) "
              "ni las emisiones (OE 7)."]:
        A(Paragraph("• " + t, P))
    # 8
    A(Paragraph("8. Referencias", H2))
    for k in ["PON", "SICETAC", "SICETAC_DIST", "SICETAC_PEAJ", "RES2024", "RES2026", "CAF", "INVIAS", "INVIAS_PMT", "PRENSA_8H", "OSRM", "OE1"]:
        A(Paragraph(C.REF[k], NOTA))
    A(Paragraph("Anexos", H2))
    for n, t in [("Anexo A", "Registro_tiempos_ciclo_Ruta40_OE6.xlsx — Act 1"), ("Anexo B", "Memoria_tiempos_logisticos_OE6.xlsx — Act 2"),
                 ("Anexo C", "Matriz_costos_unitarios_OE6.xlsx — Act 3"), ("Anexo D", "Modelo_ahorros_operativos_OE6.xlsx — Act 4"),
                 ("Anexo E", "Consultas SICE-TAC en PDF y fuentes descargadas — OE6_Logistica/Fuentes/")]:
        A(Marca("A", f"{n}. {t}")); A(Paragraph(f"<b>{n}.</b> {t}", P))
    A(Paragraph("Nota de elaboración", H3))
    A(Paragraph("Documento elaborado con apoyo de IA (Claude) en el semillero GEOPAV. Cada cifra sale de un script publicado en OE6_Logistica/ que lee "
                "las fuentes descargadas; las consultas SICE-TAC las hizo el equipo en el portal del Ministerio de Transporte y se guardaron en PDF. "
                "Responsable asignado del OE 6: Torrente Parra Daniel Ignacio; apoyo en la ejecución: Tamayo Osorio Miguel Ángel.", NOTA))
    return S


if __name__ == "__main__":
    meta = {"rotulo": "OE 6 · Actividad 5 · Informe económico-logístico",
            "titulo": "Eficiencia logística comparada: Ruta 40 frente a Ferropista",
            "subtitulo": "Tiempos de ciclo, costos operativos y ahorros para el sector transportador en el cruce Ibagué–Calarcá",
            "ficha": [("Objetivo", "OE 6: Determinar la eficiencia logística del sistema intermodal Ferropista, calculando la reducción de tiempos de ciclo y de costos operativos frente a la operación actual por la Ruta 40."),
                      ("Actividad", "5. Redacción del reporte de eficiencia logística comparada"),
                      ("Entregable / formato", "Informe económico-logístico · Documento PDF"),
                      ("Periodo", "Bloque 2 del Plan de Acción (5 oct - 7 nov 2026)"),
                      ("Responsable asignado", "Torrente Parra Daniel Ignacio"),
                      ("Apoyo en la ejecución", "Tamayo Osorio Miguel Ángel, con apoyo de IA (Claude)")],
            "pie": "Semillero GEOPAV · Universidad de Ibagué · Paz y Región 2026B", "fecha": C.FECHA,
            "titulo_pdf": "Informe económico-logístico OE 6 - Ferropista"}
    generar(SALIDA, meta, cuerpo)
    print("OK", SALIDA)
