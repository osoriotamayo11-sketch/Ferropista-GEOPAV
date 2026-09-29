# -*- coding: utf-8 -*-
"""
OE 6 · Actividad 1 — Levantamiento de los tiempos de ciclo actuales del cruce por la Ruta 40.
Producto: «Registro de tiempos» · Documento Excel (verificador). Sesión 19 (29 sep 2026).

Qué hace
  1. Lee la consulta oficial SICE-TAC (Mintransporte, periodo 20260901) de las rutas 14037 Ibagué→Calarcá y
     15393 Calarcá→Ibagué: km por tipo de terreno y velocidad promedio del tractocamión 3S3 cargado. Contrasta los km
     con el listado oficial de distancias por terreno (corte 01-09-2026). Recalcula las horas de viaje y las compara
     con las que publica el SICE-TAC.
  2. Arma tres escenarios de tiempo del cruce cabecera–cabecera, por sentido:
        mínimo  = modelo SICE-TAC (flujo libre, velocidades oficiales por terreno)             [F→CP]
        típico  = 4 h, «Paso actual: 4 horas (valor medio)»                                     [F, dia. 29]
        máximo  = típico + 1 h de espera del «pare y siga» con alternancia horaria por sentido  [F→CP]
                  (INVÍAS, emergencia del PR 47+380, Calle Larga, desde el 25 jul 2026)
     El evento extremo (trancones de 8 a 10 h, prensa, sep 2026) se registra aparte y NO entra al promedio.
  3. Registra los controles externos: ahorros del Túnel de La Línea (INVÍAS 50 min; CAF 80 min, ex ante),
     velocidad media < 20 km/h (dia. 13) y distancias de OpenStreetMap (Act 2).
  4. Escribe registro_tiempos_ruta40_OE6.json (lo lee la Act 2) y Registro_tiempos_ciclo_Ruta40_OE6.xlsx.
Tiempo de ciclo de la carretera = tiempo de conducción entre cabeceras, sin cargue ni descargue de la mercancía
(esas horas son iguales con o sin Ferropista y se tratan en la Act 3). Requiere openpyxl y pypdf.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
import comun_OE6 as C  # noqa: E402
from openpyxl import Workbook  # noqa: E402

SALIDA_X = os.path.join(AQUI, "Registro_tiempos_ciclo_Ruta40_OE6.xlsx")
SALIDA_J = os.path.join(AQUI, "registro_tiempos_ruta40_OE6.json")

# [F] Fuente primaria, leído sobre la diapositiva renderizada (dia. 29) y en su texto.
T_TIPICO_H = 4.0
# [F] INVÍAS (vía Infobae, 4 ago 2026): «alternancia horaria entre direcciones (una hora hacia Ibagué, otra hacia Armenia)».
ESPERA_MAX_PARE_SIGA_H = 1.0
# Controles externos (no entran al cálculo)
CONTROLES = [
    ("INVÍAS", "Ahorro del Cruce de la Cordillera Central, carga pesada, Calarcá–Cajamarca", "≈ 50 min", "Velocidad de 15 a 60 km/h", "INVIAS", "Declarado en la web del INVÍAS; no dice si es medido o esperado."),
    ("CAF", "Ahorro del Túnel II Centenario, vehículos pesados", "80 min", "Velocidad de 18 a 60 km/h, tramo Cajamarca–Calarcá", "CAF",
     "Impacto ESPERADO en la estructuración; la propia CAF anota que no se documentó línea base (pág. 8)."),
    ("Ponencia", "Velocidad media actual del tramo Ibagué–Armenia", "< 20 km/h", "«Servicio irregular»", "PON", "[F, dia. 13]"),
    ("Prensa", "Evento extremo: trancones en Calle Larga (Cajamarca)", "8 a 10 h", "Una o dos veces por semana, jul–sep 2026", "PRENSA_8H",
     "Declaración del alcalde de Cajamarca; reapertura de ambos carriles prevista el 30 sep 2026. No entra al promedio."),
]


def main():
    C.texto_contiene("PON", ["Paso actual: 4 horas (valor medio)", "Velocidad media < 20 km/h"])
    C.texto_contiene("CAF", ["80 minutos para vehículos pesados", "de 18 km/h a 60 km/h"])
    oficial = C.distancias_oficiales()
    S = {"sentidos": {}, "escenarios": ["Mínimo", "Típico", "Máximo"]}
    for k in C.RUTAS:
        d = C.leer_sicetac(k)
        for t in C.TERRENOS:  # el PDF de la consulta y el listado oficial deben coincidir
            assert abs(d["dist_km"][t] - oficial[k]["km"][t]) < 0.005, (k, t)
        horas = {t: d["dist_km"][t] / d["vel_kmh"][t] for t in C.TERRENOS}
        h_min = sum(horas.values())
        assert abs(h_min - d["horas_viaje_pub"]) < 0.005, (k, h_min, d["horas_viaje_pub"])
        esc = {"Mínimo": h_min, "Típico": T_TIPICO_H, "Máximo": T_TIPICO_H + ESPERA_MAX_PARE_SIGA_H}
        S["sentidos"][k] = {"ruta": d["ruta"], "ruta_id": d["ruta_id"], "km_total": d["dist_total_km"], "km": d["dist_km"],
                            "vel_kmh": d["vel_kmh"], "horas_terreno": horas, "horas_pub_sicetac": d["horas_viaje_pub"],
                            "horas": esc, "vel_media_kmh": {e: d["dist_total_km"] / h for e, h in esc.items()},
                            "nombre_oficial": oficial[k]["nombre_oficial"]}
    S["ida_vuelta_h"] = {e: sum(S["sentidos"][k]["horas"][e] for k in C.RUTAS) for e in S["escenarios"]}
    S["parametros"] = {"t_tipico_h": T_TIPICO_H, "espera_max_pare_siga_h": ESPERA_MAX_PARE_SIGA_H}
    S["controles"] = [dict(zip(["quien", "que", "valor", "detalle", "fuente", "nota"], x)) for x in CONTROLES]
    S["md5"] = {k: C.md5(C.ARCHIVOS[k]) for k in ["PON", "SICETAC_IBG_CAL", "SICETAC_CAL_IBG", "SICETAC_DIST", "CAF"]}
    C.guardar_json(SALIDA_J, S)
    excel(S)
    for k, v in S["sentidos"].items():
        print(v["ruta"], {e: round(h, 3) for e, h in v["horas"].items()}, "km", v["km_total"])
    print("ida y vuelta", {e: round(h, 3) for e, h in S["ida_vuelta_h"].items()})


def excel(S):
    wb = Workbook()
    C.portada(wb, "Registro de tiempos de ciclo del cruce por la Ruta 40",
              "Objetivo específico 6 · Actividad 1 — Tiempos actuales Ibagué–Calarcá para tractocamión 3S3",
              "1. Levantamiento de los tiempos de ciclo actuales del cruce por la Ruta 40",
              "Registro de tiempos · Documento Excel",
              [("Tramos", "Tabla 1. Distancia, velocidad y horas por tipo de terreno según el SICE-TAC (dos sentidos)"),
               ("Escenarios", "Tabla 2. Tiempo de ciclo del cruce por sentido: mínimo, típico y máximo · Tabla 3. Ida y vuelta"),
               ("Controles", "Tabla 4. Controles externos y evento extremo (no entran al cálculo)"),
               ("Fuentes", "Tabla 5. Fuentes citadas y huella md5")],
              "Índice de tablas: tablas 1 a 5 según el índice de hojas. Índice de figuras: no tiene. Índice de anexos: no tiene; las consultas SICE-TAC "
              "quedan en OE6_Logistica/Fuentes/. Script: OE6_Logistica/Act1_TiemposRuta40/registro_tiempos_ruta40_OE6.py.",
              "El tiempo mínimo es el MODELO oficial del SICE-TAC (flujo libre), no una medición. El típico es la cifra del proponente, no auditada. "
              "No hay aforo propio de tiempos de viaje: los resultados son un rango.")
    # ---- Tabla 1
    ws = wb.create_sheet("Tramos"); ws.sheet_view.showGridLines = False
    C.tit(ws, "Tabla 1. Distancia, velocidad promedio y horas de viaje por tipo de terreno (SICE-TAC, 3S3 cargado)")
    C.cab(ws, 3, ["Sentido", "Terreno", "Distancia (km)", "Velocidad promedio (km/h)", "Horas de viaje", "Marca"], [22, 14, 14, 16, 14, 30])
    r = 4
    filas_total = {}
    for k, v in S["sentidos"].items():
        r0 = r
        for t in C.TERRENOS:
            C.c(ws, r, 1, v["ruta"]); C.c(ws, r, 2, t)
            C.c(ws, r, 3, v["km"][t], C.ENTRADA, "0.00"); C.c(ws, r, 4, v["vel_kmh"][t], C.ENTRADA, "0.00")
            C.c(ws, r, 5, f"=C{r}/D{r}", fmt="0.000"); C.c(ws, r, 6, "[F] SICE-TAC · horas [CP]")
            r += 1
        C.c(ws, r, 1, v["ruta"], C.NEGRA); C.c(ws, r, 2, "Total", C.NEGRA)
        C.c(ws, r, 3, f"=SUM(C{r0}:C{r - 1})", C.NEGRA, "0.00", fill=C.FILL_RES)
        C.c(ws, r, 4, f"=C{r}/E{r}", C.NEGRA, "0.00", fill=C.FILL_RES)
        C.c(ws, r, 5, f"=SUM(E{r0}:E{r - 1})", C.NEGRA, "0.000", fill=C.FILL_RES)
        C.c(ws, r, 6, f"SICE-TAC publica {C.es(v['horas_pub_sicetac'], 2)} h (control)")
        filas_total[k] = r
        r += 2
    C.nota(ws, r, "Distancias del listado oficial «Distancias por tipo de terreno rutas SICE-TAC 01-09-2026» (idénticas a las de la consulta guardada). "
                  "Los dos sentidos tienen distinta longitud (85,01 frente a 76,17 km): así lo registra el Ministerio y OpenStreetMap confirma la asimetría "
                  "(Act 2). La columna D de la fila total es la velocidad media resultante.", ancho=6)
    # ---- Tabla 2 y 3
    es = wb.create_sheet("Escenarios"); es.sheet_view.showGridLines = False
    C.tit(es, "Tabla 2. Tiempo de ciclo del cruce cabecera–cabecera por sentido y escenario")
    C.cab(es, 3, ["Sentido", "Escenario", "Horas", "Minutos", "Velocidad media (km/h)", "Cómo se obtiene", "Marca"], [22, 12, 11, 11, 14, 62, 16])
    es["I3"] = "Parámetros"; es["I3"].font = C.NEGRA
    es["I4"] = "Tiempo típico (h)"; C.c(es, 4, 10, S["parametros"]["t_tipico_h"], C.ENTRADA, "0.00", h=False)
    es["I5"] = "Espera máx. pare y siga (h)"; C.c(es, 5, 10, S["parametros"]["espera_max_pare_siga_h"], C.ENTRADA, "0.00")
    es.column_dimensions["I"].width = 26; es.column_dimensions["J"].width = 10
    r = 4
    fila_esc = {}
    for k, v in S["sentidos"].items():
        ft = filas_total[k]
        for e, form, como, marca in [
            ("Mínimo", f"=Tramos!E{ft}", "Suma de horas por terreno del SICE-TAC (Tabla 1): flujo libre con velocidades oficiales", "[F→CP]"),
            ("Típico", "=$J$4", "«Paso actual: 4 horas (valor medio)», fuente primaria", "[F, dia. 29]"),
            ("Máximo", "=$J$4+$J$5", "Típico + 1 h: alternancia horaria por sentido del pare y siga del INVÍAS (PR 47+380, desde 25 jul 2026)", "[F→CP]")]:
            C.c(es, r, 1, v["ruta"]); C.c(es, r, 2, e, C.NEGRA)
            C.c(es, r, 3, form, fmt="0.000"); C.c(es, r, 4, f"=C{r}*60", fmt="0.0")
            C.c(es, r, 5, f"=Tramos!C{ft}/C{r}", fmt="0.0"); C.c(es, r, 6, como, wrap=True); C.c(es, r, 7, marca)
            es.row_dimensions[r].height = 28
            fila_esc[(k, e)] = r
            r += 1
        r += 1
    r += 1
    es.cell(r, 1, "Tabla 3. Ciclo de ida y vuelta (Ibagué → Calarcá → Ibagué), sin cargue ni descargue").font = C.Font(name=C.F, size=13, bold=True, color=C.AZUL)
    r += 2
    C.cab(es, r, ["Escenario", "Horas", "Minutos"], col0=1)
    r += 1
    for e in S["escenarios"]:
        a, b = fila_esc[("IBG_CAL", e)], fila_esc[("CAL_IBG", e)]
        C.c(es, r, 1, e, C.NEGRA); C.c(es, r, 2, f"=C{a}+C{b}", C.NEGRA, "0.000", fill=C.FILL_RES); C.c(es, r, 3, f"=B{r}*60", fmt="0.0")
        r += 1
    r += 1
    C.nota(es, r, "Lectura: el modelo oficial (mínimo) supone flujo libre; los 4 h del proponente equivalen a una velocidad media de unos 20 km/h, "
                  "coherente con su propia afirmación «< 20 km/h» (dia. 13). El máximo representa la operación con un paso restringido como el de "
                  "jul–sep 2026; el corredor ha tenido emergencias recurrentes, pero no hay estadística pública de frecuencia: por eso se trata como "
                  "escenario y no como promedio.", ancho=7)
    # ---- Tabla 4
    co = wb.create_sheet("Controles"); co.sheet_view.showGridLines = False
    C.tit(co, "Tabla 4. Controles externos y evento extremo (se registran; no entran al cálculo)")
    C.cab(co, 3, ["Quién", "Qué", "Valor", "Detalle", "Fuente", "Nota"], [12, 44, 12, 34, 12, 60])
    r = 4
    for x in S["controles"]:
        for j, cl in enumerate(["quien", "que", "valor", "detalle", "fuente", "nota"], 1):
            C.c(co, r, j, x[cl], C.ENTRADA if cl == "valor" else C.NORMAL, wrap=True)
        co.row_dimensions[r].height = 44
        r += 1
    r += 1
    C.nota(co, r, "INVÍAS y CAF no coinciden (50 frente a 80 min) y CAF aclara que su cifra es un impacto esperado sin línea base. Ninguna de las dos "
                  "mide el cruce completo Ibagué–Calarcá: solo el tramo del túnel. Por eso se usan como control de orden de magnitud.", ancho=6)
    C.hoja_fuentes(wb, ["PON", "SICETAC_IBG_CAL", "SICETAC_CAL_IBG", "SICETAC_DIST", "CAF", "INVIAS", "INVIAS_PMT", "PRENSA_8H"], 5)
    for w in wb.worksheets:
        w.sheet_properties.pageSetUpPr.fitToPage = True
    wb.save(SALIDA_X)


if __name__ == "__main__":
    main()
