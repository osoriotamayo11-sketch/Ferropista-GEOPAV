# -*- coding: utf-8 -*-
"""
OE 3 · Actividad 4 — Memoria de cálculo de la capacidad portante admisible por Meyerhof (NSR-10, Título H).
Sesión 18 (28 sep 2026).

Salida: OE3_Geotecnia/Act4_Capacidad/Memoria_capacidad_portante_OE3.xlsx

Entradas:
  - Suelos S1 y S2 (c, φ, γ; mínimo/típico/máximo) LEÍDOS del producto de la Act 3
    (OE3_Geotecnia/Act3_Parametros/Cuadro_parametros_adoptados_OE3.xlsx, hoja «Suelos»). No se copian a mano.
  - Geometría, nivel freático, módulo E, asentamiento admisible: hipótesis [H] declaradas abajo.
Método:
  - Meyerhof (1963): factores y correcciones de forma y profundidad según EM 1110-1-1905, tabla 4-3
    (leída sobre la imagen renderizada, p. 4-5) y control contra la tabla 4-4 (p. 4-6).
  - Asentamiento elástico indicativo: FHWA NHI-06-089 ec. 8-19 y tabla 8-13 (Cd), E y ν de
    FHWA NHI-06-088 tabla 5-16 (leídas sobre imagen renderizada).
  - NSR-10: H.4.2.3 (admisible = menor entre falla/FS y asentamiento), tabla H.4.7-1 (FS indirectos),
    tabla H.2.4-1 (FSB directos mínimos), H.4.9 (límites de asentamiento). Verificadas en el texto de la norma.
Todas las cifras del cálculo son FÓRMULAS de Excel. El único valor que calcula Python y se escribe como número
es el factor de reducción de resistencia equivalente F de la hoja «Chequeo H.2.4-1» (bisección), y la misma hoja
lo comprueba con fórmulas. Después de correr: recalcular con recalc.py (skill xlsx) o abriendo en Excel.
"""
import hashlib
import math
import os

from openpyxl import Workbook, load_workbook
from openpyxl.comments import Comment
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
ACT3 = os.path.join(RAIZ, "OE3_Geotecnia", "Act3_Parametros", "Cuadro_parametros_adoptados_OE3.xlsx")
SALIDA = os.path.join(AQUI, "Memoria_capacidad_portante_OE3.xlsx")

# Fuentes descargadas (ignoradas en git). Si están, se comprueba que sean las mismas que se leyeron.
MD5_FUENTES = {
    "EM_1110-1-1905.pdf": "f41333aad5dd4596b72af799819eb55b",
    "FHWA_NHI-06-088.pdf": "520fb5568921bf65386df3beada7435d",
    "FHWA_NHI-06-089.pdf": "9795a31e29cebf81defefe386b6d80a2",
}

VERDE, AZUL, GRIS, ROJO = "178E2C", "193F77", "475569", "9A3412"
F = "Arial"
fino = Side(style="thin", color="CBD5E1")
BORDE = Border(left=fino, right=fino, top=fino, bottom=fino)
ENTRADA = Font(name=F, size=10, color="0000FF")
ENLACE = Font(name=F, size=10, color="008000")
NORMAL = Font(name=F, size=10)
NEGRA = Font(name=F, size=10, bold=True)
CAB = Font(name=F, size=10, bold=True, color="FFFFFF")
FILL_CAB = PatternFill("solid", fgColor=AZUL)
FILL_H = PatternFill("solid", fgColor="FFF7D6")
FILL_RES = PatternFill("solid", fgColor="E8F3EA")
NOTA = Font(name=F, size=9, italic=True, color=GRIS)

TSF_KPA = 95.76  # FHWA NHI-06-088, nota de la tabla 5-16: 1 tsf = 95,76 kPa

# ---------------------------------------------------------------- hipótesis [H]
DF = 1.5            # m, profundidad de desplante
GAMMA_W = 9.81      # kN/m³
RHO_ADM = 0.025     # m, asentamiento admisible adoptado
CD = 0.99           # FHWA 089 tabla 8-13, cuadrada rígida, centro
ANCHOS = (1.5, 2.0, 3.0)
NF_CASOS = ("NF en la base", "NF profundo")
FS_IND = (("CM + CV normal", 3.0, 1.50), ("CM + CV máxima", 2.5, 1.25), ("CM + CV normal + sismo seudoestático", 1.5, 1.10))
# E (tsf) y ν de FHWA NHI-06-088 tabla 5-16; asignación del material a la fila de la tabla = [H]
MODULOS = {
    "S1": dict(fila="Silt", tsf=(20, 110, 200), nu=0.33, nu_rango="0,30-0,35",
               nota="Limo arenoso residual → fila «Silt» 20-200 tsf [H: asignación]. Típico = punto medio [H]."),
    "S2": dict(fila="Clay, soft sensitive", tsf=(25, 87.5, 150), nu=0.45, nu_rango="0,4-0,5 (no drenado)",
               nota="Ceniza alofánica CL-SC, sensible al saturarse → fila «Clay: soft sensitive» 25-150 tsf [H: asignación]. Típico = punto medio [H]."),
}
CASOS = ("Mínimo", "Típico", "Máximo")


def md5(ruta):
    h = hashlib.md5()
    with open(ruta, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def comprobar_fuentes():
    for nombre, esperado in MD5_FUENTES.items():
        ruta = os.path.join(AQUI, "Fuentes", nombre)
        if os.path.exists(ruta):
            real = md5(ruta)
            if real != esperado:
                raise SystemExit(f"DETENIDO: {nombre} cambió (md5 {real} ≠ {esperado}). Revisar antes de regenerar.")
            print("md5 ok", nombre)
        else:
            print("aviso: fuente no presente en disco (se descarga del enlace de la hoja «Marcas y fuentes»):", nombre)


def leer_act3():
    """Devuelve {S1: {'c': (min,tip,max), 'phi': ..., 'gamma': ...}, S2: ...} leído de la hoja Suelos."""
    wb = load_workbook(ACT3, data_only=False)
    ws = wb["Suelos"]
    out, filas = {}, {}
    for r in range(5, ws.max_row + 1):
        juego, par = ws.cell(r, 1).value, ws.cell(r, 4).value
        if juego not in ("S1", "S2") or not par:
            continue
        clave = "c" if par.startswith("c") else ("phi" if par.startswith("φ") else ("gamma" if par.startswith("γ") else None))
        if clave is None:
            continue
        vals = tuple(float(ws.cell(r, j).value) for j in (6, 7, 8))
        if not (vals[0] <= vals[1] <= vals[2]):
            raise SystemExit(f"DETENIDO: rango incoherente en Act 3, {juego} {par}: {vals}")
        out.setdefault(juego, {})[clave] = vals
        filas[(juego, clave)] = (r, par, ws.cell(r, 5).value, ws.cell(r, 9).value, ws.cell(r, 10).value)
    for j in ("S1", "S2"):
        for k in ("c", "phi", "gamma"):
            if k not in out.get(j, {}):
                raise SystemExit(f"DETENIDO: falta {j} {k} en la hoja Suelos de la Act 3")
    return out, filas


# ---------------------------------------------------------------- Meyerhof en Python (solo para el chequeo H.2.4-1
# y para la verificación independiente; el libro calcula con fórmulas propias)
def meyerhof_qult(c, phi, gam, gam_ef, B, Df):
    kp = math.tan(math.radians(45 + phi / 2)) ** 2
    nq = math.exp(math.pi * math.tan(math.radians(phi))) * kp
    nc = (nq - 1) / math.tan(math.radians(phi))
    ng = (nq - 1) * math.tan(math.radians(1.4 * phi))
    sc, sq = 1 + 0.2 * kp, 1 + 0.1 * kp            # B'/W' = 1 (cuadrada)
    dc, dq = 1 + 0.2 * math.sqrt(kp) * Df / B, 1 + 0.1 * math.sqrt(kp) * Df / B
    q = gam * Df
    return c * nc * sc * dc + q * nq * sq * dq + 0.5 * gam_ef * B * ng * sq * dq


def factor_equivalente(c, phi, gam, gam_ef, B, Df, fs_ind):
    """F tal que qult(c/F, atan(tanφ/F)) = qult/FS_ind (bisección)."""
    objetivo = meyerhof_qult(c, phi, gam, gam_ef, B, Df) / fs_ind
    lo, hi = 1.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        ph = math.degrees(math.atan(math.tan(math.radians(phi)) / mid))
        if meyerhof_qult(c / mid, ph, gam, gam_ef, B, Df) > objetivo:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---------------------------------------------------------------- utilidades de estilo
def cabecera(ws, fila, textos, anchos=None, col0=1):
    for j, t in enumerate(textos, start=col0):
        c = ws.cell(fila, j, t)
        c.font, c.fill, c.border = CAB, FILL_CAB, BORDE
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    if anchos:
        for j, w in enumerate(anchos, start=col0):
            ws.column_dimensions[ws.cell(1, j).column_letter].width = w


def titulo(ws, texto, fila=1):
    ws.cell(fila, 1, texto).font = Font(name=F, size=13, bold=True, color=AZUL)


def celda(ws, r, c, v, fuente=NORMAL, fmt=None, h=False, wrap=False, fill=None):
    x = ws.cell(r, c, v)
    x.font, x.border = fuente, BORDE
    x.alignment = Alignment(wrap_text=wrap, vertical="top")
    if fmt:
        x.number_format = fmt
    if h:
        x.fill = FILL_H
    if fill:
        x.fill = fill
    return x


def nota(ws, r, texto, color=GRIS, col=1):
    x = ws.cell(r, col, texto)
    x.font = Font(name=F, size=9, italic=True, color=color)
    return x


def main():
    comprobar_fuentes()
    suelos, filas_act3 = leer_act3()
    wb = Workbook()

    # ============================================================ Portada
    p = wb.active
    p.title = "Portada"
    p.sheet_view.showGridLines = False
    for col, w in zip("ABCDEFGH", (3, 24, 22, 22, 22, 22, 22, 3)):
        p.column_dimensions[col].width = w
    for nombre, cel in (("logo-unibague.png", "B2"), ("logo-geopav.png", "F2")):
        ruta = os.path.join(RAIZ, "public", nombre)
        if os.path.exists(ruta):
            im = XLImage(ruta)
            k = 70 / im.height
            im.height, im.width = 70, int(im.width * k)
            p.add_image(im, cel)
    p["B8"] = "Memoria de cálculo de la capacidad portante admisible"
    p["B8"].font = Font(name=F, size=18, bold=True, color=VERDE)
    p["B9"] = "Objetivo específico 3 · Actividad 4 — Formulación de Meyerhof bajo el Título H de la NSR-10"
    p["B9"].font = Font(name=F, size=12, color=AZUL)
    ficha = [
        ("Objetivo", "OE 3: Estimar la capacidad portante preliminar del terreno de fundación de las infraestructuras de superficie en los portales de Ibagué y Armenia"),
        ("Actividad", "4. Cálculo de la capacidad portante admisible por la formulación de Meyerhof (NSR-10, Título H)"),
        ("Entregable / formato", "Memoria de cálculo · Documento Excel"),
        ("Periodo", "Bloque 2 del Plan de Acción (5 oct - 7 nov 2026)"),
        ("Responsable asignado", "Tamayo Osorio Miguel Ángel"),
        ("Semillero", "Semillero de Investigación GEOPAV · Ingeniería Civil · Universidad de Ibagué · Paz y Región 2026B"),
        ("Portales", "Oriental (Ibagué) sobre suelo S1 · Occidental (municipio de Calarcá) sobre suelo S2"),
        ("Fecha de elaboración", "28 sep 2026"),
        ("Advertencia", "RESULTADO NO APTO PARA DISEÑO. Ningún parámetro proviene de exploración en los portales: son análogos publicados e hipótesis declaradas (Act 3). "
                        "La capacidad admisible se entrega como RANGO para mostrar la sensibilidad y dimensionar la exploración que exige la NSR-10 (capítulo H.3) antes de cualquier diseño."),
    ]
    for i, (k, v) in enumerate(ficha):
        r = 11 + i
        p.cell(r, 2, k).font = NEGRA
        p.cell(r, 2).alignment = Alignment(vertical="top", wrap_text=True)
        p.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
        c = p.cell(r, 3, v)
        c.font = NORMAL if k != "Advertencia" else Font(name=F, size=10, bold=True, color=ROJO)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        p.row_dimensions[r].height = 30 if len(v) < 110 else 60
    r = 11 + len(ficha) + 1
    p.cell(r, 2, "Índice de hojas (tabla de contenido)").font = Font(name=F, size=12, bold=True, color=AZUL)
    r += 1
    indice = [
        ("Resumen", "Tabla 1. Capacidad admisible por portal y ancho de zapata (rango, FS 3,0)"),
        ("Entradas", "Tabla 2. Parámetros del suelo (desde la Act 3) · Tabla 3. Hipótesis de cálculo · Tabla 4. Factores de seguridad NSR-10"),
        ("Cálculo", "Tabla 5. Meyerhof: factores, capacidad última, admisible por falla y por asentamiento (36 casos)"),
        ("Chequeo H.2.4-1", "Tabla 6. Factor de seguridad directo equivalente frente a la tabla H.2.4-1"),
        ("Verificación", "Tabla 7. Control de los factores Nc, Nq, Nγ contra la tabla 4-4 de EM 1110-1-1905"),
        ("Limitaciones", "Tabla 8. Qué no afirma esta memoria · Tabla 9. Exploración mínima para convertir el rango en diseño"),
        ("Marcas y fuentes", "Tabla 10. Marcas F / CP / H · Tabla 11. Fuentes citadas"),
    ]
    for h_, d in indice:
        p.cell(r, 2, h_).font = NEGRA
        p.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
        p.cell(r, 3, d).font = NORMAL
        r += 1
    r += 1
    p.merge_cells(start_row=r, start_column=2, end_row=r + 3, end_column=7)
    c = p.cell(r, 2, "Índice de tablas: tablas 1 a 11, una o dos por hoja, según el índice de hojas. Índice de figuras: no tiene figuras. "
                     "Índice de anexos: no tiene anexos; las fuentes descargadas se listan en la tabla 11. "
                     "Convención: texto azul = entrada editable; texto verde = valor enlazado desde otra hoja; fondo amarillo = hipótesis [H]; fondo verde = resultado. "
                     "Elaborado con apoyo de IA (Claude) y verificado contra las fuentes citadas, leídas en el original descargado. "
                     "Script: OE3_Geotecnia/Act4_Capacidad/memoria_capacidad_portante_OE3.py")
    c.font = Font(name=F, size=9, italic=True, color=GRIS)
    c.alignment = Alignment(wrap_text=True, vertical="top")

    # ============================================================ Entradas
    e = wb.create_sheet("Entradas")
    e.sheet_view.showGridLines = False
    titulo(e, "Tabla 2. Parámetros del suelo de fundación (leídos del producto de la Act 3) y módulo de deformación")
    nota(e, 2, "c, φ y γ: copiados por el script desde Cuadro_parametros_adoptados_OE3.xlsx (hoja «Suelos»); no se editan aquí. E y ν: FHWA NHI-06-088, tabla 5-16.")
    cabecera(e, 4, ["Juego", "Portal", "Parámetro", "Unidad", "Mínimo", "Típico", "Máximo", "Marca", "Origen"],
             [8, 20, 34, 9, 11, 11, 11, 8, 70])
    portal = {"S1": "Oriental (Ibagué)", "S2": "Occidental (Calarcá)"}
    ref = {}  # (juego, par) -> fila
    r = 5
    for j in ("S1", "S2"):
        for k, etiqueta, u in (("c", None, "kPa"), ("phi", None, "°"), ("gamma", None, "kN/m³")):
            fila3, par3, u3, marca3, fte3 = filas_act3[(j, k)]
            celda(e, r, 1, j, NEGRA)
            celda(e, r, 2, portal[j])
            celda(e, r, 3, par3, wrap=True)
            celda(e, r, 4, u3)
            for col, v in zip((5, 6, 7), suelos[j][k]):
                celda(e, r, col, v, ENLACE, "0.0", h=(marca3 == "H"))
            celda(e, r, 8, marca3, NEGRA)
            celda(e, r, 9, f"Act 3, hoja Suelos, fila {fila3} (fuente {fte3})", wrap=True)
            ref[(j, k)] = r
            r += 1
        m = MODULOS[j]
        celda(e, r, 1, j, NEGRA)
        celda(e, r, 2, portal[j])
        celda(e, r, 3, "E (módulo de Young, drenado equivalente)")
        celda(e, r, 4, "kPa")
        for col, v in zip((5, 6, 7), m["tsf"]):
            celda(e, r, col, v, ENTRADA, "#,##0", h=True)  # tsf; se reescribe como fórmula abajo
        celda(e, r, 8, "F / H", NEGRA)
        celda(e, r, 9, f"FHWA 088 tabla 5-16, {m['nota']}", wrap=True)
        e.row_dimensions[r].height = 42
        ref[(j, "E")] = r
        r += 1
        celda(e, r, 1, j, NEGRA)
        celda(e, r, 2, portal[j])
        celda(e, r, 3, "ν (relación de Poisson)")
        celda(e, r, 4, "—")
        for col in (5, 6, 7):
            celda(e, r, col, m["nu"], ENTRADA, "0.00", h=True)
        celda(e, r, 8, "F / H", NEGRA)
        celda(e, r, 9, f"FHWA 088 tabla 5-16: {m['nu_rango']}; se adopta un valor único [H].", wrap=True)
        ref[(j, "nu")] = r
        r += 1
    # r == 15
    r += 1
    e.cell(r, 1, "Tabla 3. Hipótesis de cálculo").font = Font(name=F, size=13, bold=True, color=AZUL)
    r += 1
    cabecera(e, r, ["#", "Hipótesis", "Valor", "Unidad", "Marca", "Justificación", "", "", ""], col0=1)
    e.merge_cells(start_row=r, start_column=6, end_row=r, end_column=9)
    hip_ini = r + 1
    hipotesis = [
        ("Df, profundidad de desplante", DF, "m", "H", "Zapata aislada típica de nave o marquesina de terminal; la fuente no trae estructuras de las terminales Ro-Ro."),
        ("γw, peso unitario del agua", GAMMA_W, "kN/m³", "F", "Constante física."),
        ("ρadm, asentamiento admisible", RHO_ADM, "m", "H", "Conservador frente a NSR-10 H.4.9: si el diferencial ≈ total (portales sobre contactos litológicos), 25 mm ≈ A/300 con A = 7,5 m (pórticos de concreto, tabla H.4.9-1). Límite total NSR-10 H.4.9.2: 300 mm."),
        ("Cd, factor de forma y rigidez", CD, "—", "F", "FHWA 089 tabla 8-13, cuadrada rígida (0,99)."),
        ("B'/W', relación ancho/largo", 1.0, "—", "H", "Zapata cuadrada, carga centrada (sin excentricidad ni inclinación)."),
        ("1 tsf en kPa", TSF_KPA, "kPa", "F", "FHWA 088, nota de la tabla 5-16."),
    ]
    celdas_h = {}
    for i, (h_, v, u, mk, just) in enumerate(hipotesis, start=1):
        rr = hip_ini + i - 1
        celda(e, rr, 1, i, NEGRA)
        celda(e, rr, 2, h_, wrap=True)
        celda(e, rr, 3, v, ENTRADA, "0.000" if v < 1 else "0.00", h=(mk == "H"))
        celda(e, rr, 4, u)
        celda(e, rr, 5, mk, NEGRA)
        celda(e, rr, 6, just, wrap=True)
        e.merge_cells(start_row=rr, start_column=6, end_row=rr, end_column=9)
        e.row_dimensions[rr].height = 44 if len(just) > 90 else 22
        celdas_h[h_.split(",")[0]] = f"Entradas!$C${rr}"
    tsf_cel = celdas_h["1 tsf en kPa"].replace("Entradas!", "")
    for j in ("S1", "S2"):
        for col, v in zip((5, 6, 7), MODULOS[j]["tsf"]):
            e.cell(ref[(j, "E")], col).value = f"={v}*{tsf_cel}"
    r = hip_ini + len(hipotesis) + 1
    e.cell(r, 1, "Tabla 4. Factores de seguridad del Título H de la NSR-10 (verificados en el texto de la norma)").font = Font(name=F, size=13, bold=True, color=AZUL)
    r += 1
    cabecera(e, r, ["#", "Condición", "FSICP mín. (tabla H.4.7-1)", "FSBM mín. diseño (tabla H.2.4-1)", "Marca"], col0=1)
    fs_ini = r + 1
    for i, (cond, fsi, fsb) in enumerate(FS_IND, start=1):
        rr = fs_ini + i - 1
        celda(e, rr, 1, i, NEGRA)
        celda(e, rr, 2, cond, wrap=True)
        celda(e, rr, 3, fsi, ENTRADA, "0.0")
        celda(e, rr, 4, fsb, ENTRADA, "0.00")
        celda(e, rr, 5, "F", NEGRA)
    r = fs_ini + len(FS_IND) + 1
    nota(e, r, "Fuente: NSR-10 Título H, H.4.7.1 (tabla H.4.7-1) y H.2.4.3 (tabla H.2.4-1). La NSR-10 no impone Meyerhof: H.4.2.1 admite métodos analíticos con experiencia documentada.")
    e.freeze_panes = "A5"
    DFc, GWc, RHOc, CDc, BWc = (celdas_h["Df"], celdas_h["γw"], celdas_h["ρadm"], celdas_h["Cd"], celdas_h["B'/W'"])
    FSc = [f"Entradas!$C${fs_ini + i}" for i in range(3)]
    FSBc = [f"Entradas!$D${fs_ini + i}" for i in range(3)]

    # ============================================================ Cálculo
    k = wb.create_sheet("Cálculo")
    k.sheet_view.showGridLines = False
    titulo(k, "Tabla 5. Capacidad portante por Meyerhof (1963) y admisible según NSR-10 H.4.2.3 — zapatas cuadradas, carga vertical centrada")
    nota(k, 2, "qult = c·Nc·sc·dc + q·Nq·sq·dq + ½·γ'·B·Nγ·sγ·dγ (EM 1110-1-1905 ec. 4-1 y tabla 4-3). q = γ·Df. γ' = γ − γw con NF en la base; γ' = γ con NF profundo. "
                "Asentamiento: ρ = Cd·Δp·B·(1−ν²)/E (FHWA 089 ec. 8-19) → q_s = ρadm·E/(Cd·B·(1−ν²)) + γ·Df. Todo [CP].")
    hdr = ["Juego", "Portal", "Caso", "B (m)", "Nivel freático", "c (kPa)", "φ (°)", "γ (kN/m³)", "γ' bajo la base", "q = γ·Df (kPa)",
           "Nφ = tan²(45+φ/2)", "Nq", "Nc", "Nγ", "sc", "sq = sγ", "dc", "dq = dγ", "qult (kPa)",
           "qult / FSICP 3,0 (kPa)", "qult con resistencia ÷ FSBM 1,50 (kPa)", "qadm por falla (kPa)", "E (kPa)", "q por asentamiento (kPa)",
           "qadm NSR-10 H.4.2.3 (kPa)", "Gobierna", "qadm falla CM+CV máx. (kPa)", "qadm falla con sismo (kPa)"]
    anchos = [7, 18, 9, 7, 15, 8, 7, 9, 9, 10, 10, 9, 9, 9, 7, 8, 7, 8, 11, 11, 12, 11, 10, 12, 13, 16, 12, 12]
    cabecera(k, 4, hdr, anchos)
    aux_ini = 30  # columnas auxiliares de resistencia reducida (AD en adelante)
    aux_hdr = []
    for fsb_txt in ("1,50", "1,25", "1,10"):
        aux_hdr += [f"φ/FSB {fsb_txt} (°)", f"Nφ ({fsb_txt})", f"Nq ({fsb_txt})", f"Nc ({fsb_txt})", f"Nγ ({fsb_txt})", f"qult reducida {fsb_txt} (kPa)"]
    cabecera(k, 4, aux_hdr, [10] * len(aux_hdr), col0=aux_ini)
    k.cell(3, aux_ini, "Columnas auxiliares: resistencia reducida por el FSBM de la tabla H.2.4-1 (c/FSBM y arctan(tanφ/FSBM))").font = NEGRA
    k.row_dimensions[4].height = 58
    filas_calc = {}
    r = 5
    colE = {0: "E", 1: "F", 2: "G"}
    L_ = lambda n: k.cell(1, n).column_letter
    for j in ("S1", "S2"):
        for ci, caso in enumerate(CASOS):
            for B in ANCHOS:
                for nf in NF_CASOS:
                    col = colE[ci]
                    celda(k, r, 1, j, NEGRA)
                    celda(k, r, 2, portal[j])
                    celda(k, r, 3, caso)
                    celda(k, r, 4, B, ENTRADA, "0.0", h=True)
                    celda(k, r, 5, nf, h=True)
                    celda(k, r, 6, f"=Entradas!{col}{ref[(j, 'c')]}", ENLACE, "0.0")
                    celda(k, r, 7, f"=Entradas!{col}{ref[(j, 'phi')]}", ENLACE, "0.0")
                    celda(k, r, 8, f"=Entradas!{col}{ref[(j, 'gamma')]}", ENLACE, "0.0")
                    celda(k, r, 9, f'=IF(E{r}="NF en la base",H{r}-{GWc},H{r})', NORMAL, "0.00")
                    celda(k, r, 10, f"=H{r}*{DFc}", NORMAL, "0.0")
                    celda(k, r, 11, f"=TAN(RADIANS(45+G{r}/2))^2", NORMAL, "0.000")
                    celda(k, r, 12, f"=EXP(PI()*TAN(RADIANS(G{r})))*K{r}", NORMAL, "0.00")
                    celda(k, r, 13, f"=(L{r}-1)/TAN(RADIANS(G{r}))", NORMAL, "0.00")
                    celda(k, r, 14, f"=(L{r}-1)*TAN(RADIANS(1.4*G{r}))", NORMAL, "0.00")
                    celda(k, r, 15, f"=1+0.2*K{r}*{BWc}", NORMAL, "0.000")
                    celda(k, r, 16, f"=1+0.1*K{r}*{BWc}", NORMAL, "0.000")
                    celda(k, r, 17, f"=1+0.2*SQRT(K{r})*{DFc}/D{r}", NORMAL, "0.000")
                    celda(k, r, 18, f"=1+0.1*SQRT(K{r})*{DFc}/D{r}", NORMAL, "0.000")
                    celda(k, r, 19, f"=F{r}*M{r}*O{r}*Q{r}+J{r}*L{r}*P{r}*R{r}+0.5*I{r}*D{r}*N{r}*P{r}*R{r}", NORMAL, "#,##0")
                    # auxiliares: una terna por FSBM
                    qred = []
                    for fi in range(3):
                        c0 = aux_ini + 6 * fi
                        ph, kp, nq, nc, ng, qr = (L_(c0 + x) for x in range(6))
                        celda(k, r, c0, f"=DEGREES(ATAN(TAN(RADIANS(G{r}))/{FSBc[fi]}))", NORMAL, "0.00")
                        celda(k, r, c0 + 1, f"=TAN(RADIANS(45+{ph}{r}/2))^2", NORMAL, "0.000")
                        celda(k, r, c0 + 2, f"=EXP(PI()*TAN(RADIANS({ph}{r})))*{kp}{r}", NORMAL, "0.00")
                        celda(k, r, c0 + 3, f"=({nq}{r}-1)/TAN(RADIANS({ph}{r}))", NORMAL, "0.00")
                        celda(k, r, c0 + 4, f"=({nq}{r}-1)*TAN(RADIANS(1.4*{ph}{r}))", NORMAL, "0.00")
                        sq_ = f"(1+0.1*{kp}{r}*{BWc})"
                        dq_ = f"(1+0.1*SQRT({kp}{r})*{DFc}/D{r})"
                        celda(k, r, c0 + 5, f"=F{r}/{FSBc[fi]}*{nc}{r}*(1+0.2*{kp}{r}*{BWc})*(1+0.2*SQRT({kp}{r})*{DFc}/D{r})"
                                            f"+J{r}*{nq}{r}*{sq_}*{dq_}+0.5*I{r}*D{r}*{ng}{r}*{sq_}*{dq_}", NORMAL, "#,##0")
                        qred.append(f"{qr}{r}")
                    celda(k, r, 20, f"=S{r}/{FSc[0]}", NORMAL, "#,##0")
                    celda(k, r, 21, f"={qred[0]}", NORMAL, "#,##0")
                    celda(k, r, 22, f"=MIN(T{r},U{r})", NORMAL, "#,##0")
                    celda(k, r, 23, f"=Entradas!{col}{ref[(j, 'E')]}", ENLACE, "#,##0")
                    celda(k, r, 24, f"={RHOc}*W{r}/({CDc}*D{r}*(1-Entradas!{col}{ref[(j, 'nu')]}^2))+J{r}", NORMAL, "#,##0")
                    celda(k, r, 25, f"=MIN(V{r},X{r})", NEGRA, "#,##0", fill=FILL_RES)
                    celda(k, r, 26, f'=IF(X{r}<V{r},"Asentamiento",IF(T{r}<=U{r},"Falla (FSICP)","Falla (FSB directo)"))', NORMAL)
                    celda(k, r, 27, f"=MIN(S{r}/{FSc[1]},{qred[1]})", NORMAL, "#,##0")
                    celda(k, r, 28, f"=MIN(S{r}/{FSc[2]},{qred[2]})", NORMAL, "#,##0")
                    filas_calc[(j, caso, B, nf)] = r
                    r += 1
    nota(k, r + 1, "Admisible por falla (col. V) = menor entre qult/FSICP (tabla H.4.7-1) y la presión que agota la resistencia reducida por el FSBM (tabla H.2.4-1): así se cumple H.4.7.1, "
                   "que exige demostrar ambos. Con φ alto el FSICP 3,0 por sí solo NO garantiza FSB ≥ 1,50 (ver hoja «Chequeo H.2.4-1»).")
    nota(k, r + 2, "Columnas AA y AB: admisibles por falla para CM+CV máxima (2,5 y 1,25) y con sismo seudoestático (1,5 y 1,10). El sismo entra solo por los FS: "
                   "no se reduce qult por fuerzas inerciales ni se evalúa licuación o pérdida de resistencia (H.4.2.1 e). El asentamiento se compara solo con CM+CV normal.")
    nota(k, r + 3, "Fuente: EM 1110-1-1905 (tablas 4-3 y 4-4), FHWA NHI-06-089 (ec. 8-19, tabla 8-13), FHWA NHI-06-088 (tabla 5-16), NSR-10 Título H. Parámetros de la Act 3.")
    k.freeze_panes = "F5"

    # ============================================================ Chequeo H.2.4-1
    ch = wb.create_sheet("Chequeo H.2.4-1")
    ch.sheet_view.showGridLines = False
    titulo(ch, "Tabla 6. Factor de seguridad básico directo equivalente (FSB) frente a la tabla H.2.4-1 de la NSR-10 — zapata de B = 2,0 m")
    nota(ch, 2, "H.4.7.1 exige demostrar que los FS indirectos implican FSB directos ≥ tabla H.2.4-1. FSB = F tal que qult(c/F, arctan(tanφ/F)) = qult/FSICP. "
                "F lo calcula el script por bisección [CP]; las columnas I a O lo comprueban con fórmulas: la razón de la columna O debe ser igual a FSICP.")
    hdr = ["Juego", "Caso", "Nivel freático", "Condición", "FSICP", "qult (kPa)", "F = FSB equivalente [CP]", "FSBM mín. (H.2.4-1)",
           "c/F (kPa)", "φ reducido (°)", "Nφ", "Nq", "Nc", "Nγ", "qult/qult reducido", "¿El FSICP solo cumple H.2.4-1?"]
    cabecera(ch, 4, hdr, [7, 9, 15, 30, 8, 10, 12, 11, 9, 10, 8, 8, 8, 8, 12, 10])
    ch.row_dimensions[4].height = 44
    r = 5
    Bc = 2.0
    minimo_fsb = []
    for j in ("S1", "S2"):
        for ci, caso in enumerate(CASOS):
            for nf in NF_CASOS:
                rc = filas_calc[(j, caso, Bc, nf)]
                c_, ph, g = (suelos[j][x][ci] for x in ("c", "phi", "gamma"))
                ge = g - GAMMA_W if nf == "NF en la base" else g
                for fi, (cond, fsi, fsb) in enumerate(FS_IND):
                    Fv = factor_equivalente(c_, ph, g, ge, Bc, DF, fsi)
                    minimo_fsb.append((Fv - fsb, j, caso, nf, cond, Fv))
                    celda(ch, r, 1, j, NEGRA)
                    celda(ch, r, 2, caso)
                    celda(ch, r, 3, nf)
                    celda(ch, r, 4, cond, wrap=True)
                    celda(ch, r, 5, f"={FSc[fi]}", ENLACE, "0.0")
                    celda(ch, r, 6, f"='Cálculo'!S{rc}", ENLACE, "#,##0")
                    celda(ch, r, 7, round(Fv, 4), NORMAL, "0.000")
                    celda(ch, r, 8, f"={FSBc[fi]}", ENLACE, "0.00")
                    celda(ch, r, 9, f"='Cálculo'!F{rc}/G{r}", NORMAL, "0.00")
                    celda(ch, r, 10, f"=DEGREES(ATAN(TAN(RADIANS('Cálculo'!G{rc}))/G{r}))", NORMAL, "0.00")
                    celda(ch, r, 11, f"=TAN(RADIANS(45+J{r}/2))^2", NORMAL, "0.000")
                    celda(ch, r, 12, f"=EXP(PI()*TAN(RADIANS(J{r})))*K{r}", NORMAL, "0.00")
                    celda(ch, r, 13, f"=(L{r}-1)/TAN(RADIANS(J{r}))", NORMAL, "0.00")
                    celda(ch, r, 14, f"=(L{r}-1)*TAN(RADIANS(1.4*J{r}))", NORMAL, "0.00")
                    qred = (f"(I{r}*M{r}*(1+0.2*K{r}*{BWc})*(1+0.2*SQRT(K{r})*{DFc}/{Bc})"
                            f"+'Cálculo'!J{rc}*L{r}*(1+0.1*K{r}*{BWc})*(1+0.1*SQRT(K{r})*{DFc}/{Bc})"
                            f"+0.5*'Cálculo'!I{rc}*{Bc}*N{r}*(1+0.1*K{r}*{BWc})*(1+0.1*SQRT(K{r})*{DFc}/{Bc}))")
                    celda(ch, r, 15, f"=F{r}/{qred}", NORMAL, "0.000")
                    celda(ch, r, 16, f'=IF(G{r}>=H{r},"Sí","NO")', NEGRA, fill=FILL_RES)
                    ch.row_dimensions[r].height = 28
                    r += 1
    nota(ch, r + 1, "Lectura: «NO» significa que aplicar solo el FSICP a qult deja un FSB directo menor que el mínimo de la tabla H.2.4-1. Por eso la hoja «Cálculo» toma como admisible por falla "
                    "el menor de los dos criterios (columna V y columnas AA-AB); con esa regla el FSB directo es ≥ FSBM en todos los casos.", ROJO)
    ch.freeze_panes = "E5"

    # ============================================================ Resumen
    z = wb.create_sheet("Resumen", 1)
    z.sheet_view.showGridLines = False
    titulo(z, "Tabla 1. Capacidad portante admisible por portal y ancho de zapata — CM + CV normal (FS 3,0), NSR-10 H.4.2.3")
    nota(z, 2, "Rango, no valor de diseño. Mínimo: parámetros mínimos y NF en la base. Máximo: parámetros máximos y NF profundo. Df = 1,5 m. Valores en kPa, desde la hoja «Cálculo».")
    hdr = ["Portal", "Suelo", "B (m)", "Mínimo", "Típico, NF en la base", "Típico, NF profundo", "Máximo", "Gobierna en el típico con NF profundo", "qult típico, NF profundo"]
    cabecera(z, 4, hdr, [22, 44, 8, 11, 13, 13, 11, 18, 14])
    z.row_dimensions[4].height = 44
    mat = {"S1": "S1 · suelo residual sobre PCAn / Jcdi (análogo del Batolito Antioqueño)",
           "S2": "S2 · cobertura de cenizas alofánicas sobre Kqs / Kqv (análogo de Pereira)"}
    r = 5
    for j in ("S1", "S2"):
        for B in ANCHOS:
            cols = [filas_calc[(j, "Mínimo", B, "NF en la base")], filas_calc[(j, "Típico", B, "NF en la base")],
                    filas_calc[(j, "Típico", B, "NF profundo")], filas_calc[(j, "Máximo", B, "NF profundo")]]
            celda(z, r, 1, portal[j], NEGRA)
            celda(z, r, 2, mat[j], wrap=True)
            celda(z, r, 3, B, NORMAL, "0.0")
            for i, rc in enumerate(cols):
                celda(z, r, 4 + i, f"='Cálculo'!Y{rc}", NEGRA if i in (0, 3) else NORMAL, "#,##0", fill=FILL_RES)
            celda(z, r, 8, f"='Cálculo'!Z{cols[2]}")
            celda(z, r, 9, f"='Cálculo'!S{cols[2]}", NORMAL, "#,##0")
            z.row_dimensions[r].height = 30
            r += 1
    r += 1
    nota(z, r, "Cómo leerlo: la amplitud entre «Mínimo» y «Máximo» mide la incertidumbre de los parámetros análogos. Solo la exploración del capítulo H.3 (hoja «Limitaciones») permite cerrarla.", ROJO)
    nota(z, r + 1, "Donde gobierna el asentamiento, aumentar B no aumenta la admisible: el límite lo pone el módulo E [H], no la resistencia al corte.")
    nota(z, r + 2, "Fuente: hoja «Cálculo» (Tabla 5). Marcas: resultados [CP]; entradas F y H según la Tabla 2.")

    # ============================================================ Verificación
    v = wb.create_sheet("Verificación")
    v.sheet_view.showGridLines = False
    titulo(v, "Tabla 7. Control de las fórmulas de Nq, Nc y Nγ (Meyerhof) contra la tabla 4-4 de EM 1110-1-1905")
    nota(v, 2, "Valores de la tabla 4-4 leídos sobre la imagen renderizada de la p. 4-6 (PDF p. 45). Tolerancia: redondeo a 2 decimales de la tabla.")
    cabecera(v, 4, ["φ (°)", "Nq tabla", "Nq fórmula", "Nc tabla", "Nc fórmula", "Nγ tabla", "Nγ fórmula", "Máx. diferencia", "¿Coincide?"],
             [8, 10, 11, 10, 11, 10, 11, 13, 11])
    TABLA_44 = [(22, 7.82, 16.88, 4.07), (24, 9.60, 19.32, 5.72), (26, 11.85, 22.25, 8.00), (28, 14.72, 25.80, 11.19),
                (30, 18.40, 30.14, 15.67), (32, 23.18, 35.49, 22.02), (34, 29.44, 42.16, 31.15)]
    for i, (ph, nq, nc, ng) in enumerate(TABLA_44):
        rr = 5 + i
        celda(v, rr, 1, ph, ENTRADA)
        celda(v, rr, 2, nq, ENTRADA, "0.00")
        celda(v, rr, 3, f"=EXP(PI()*TAN(RADIANS(A{rr})))*TAN(RADIANS(45+A{rr}/2))^2", NORMAL, "0.00")
        celda(v, rr, 4, nc, ENTRADA, "0.00")
        celda(v, rr, 5, f"=(C{rr}-1)/TAN(RADIANS(A{rr}))", NORMAL, "0.00")
        celda(v, rr, 6, ng, ENTRADA, "0.00")
        celda(v, rr, 7, f"=(C{rr}-1)*TAN(RADIANS(1.4*A{rr}))", NORMAL, "0.00")
        celda(v, rr, 8, f"=MAX(ABS(C{rr}-B{rr}),ABS(E{rr}-D{rr}),ABS(G{rr}-F{rr}))", NORMAL, "0.000")
        celda(v, rr, 9, f'=IF(H{rr}<=0.006,"Sí","NO")', NEGRA, fill=FILL_RES)
    nota(v, 5 + len(TABLA_44) + 1, "Cubre φ de 22° a 34°, el intervalo de los parámetros S1 (27-32°) y S2 (23-33°) y de los φ reducidos del chequeo H.2.4-1.")

    # ============================================================ Limitaciones
    lm = wb.create_sheet("Limitaciones")
    lm.sheet_view.showGridLines = False
    titulo(lm, "Tabla 8. Qué no afirma esta memoria y sus limitaciones")
    cabecera(lm, 3, ["#", "Limitación", "Consecuencia", "Referencia"], [5, 60, 60, 26])
    lims = [
        ("Los parámetros c, φ y γ son análogos publicados (Batolito Antioqueño; cenizas de Pereira), no del sitio.", "El rango puede no contener el valor real del portal.", "Act 3; NSR-10 H.3"),
        ("S2 usa c y φ de ensayos UU (no drenados, esfuerzos totales) en ceniza no saturada, combinados con peso sumergido cuando el NF está en la base.",
         "Mezcla de enfoques en esfuerzos totales y efectivos: se acepta solo como sensibilidad.", "NSR-10 H.2.4.2; BBM13"),
        ("No se cuantifica la falla por corte local ni por punzonamiento (suelos sueltos o sensibles, como la ceniza alofánica al saturarse).",
         "En S2 y en S1 con cohesión nula, qult real puede ser menor que la de corte general.", "NSR-10 H.4.2.1; EM 1110-1-1905 §1-2"),
        ("No se considera la influencia de taludes próximos. El portal oriental tiene pendiente media de 16,7° y p90 de 31,1° en 250 m (Act 2).",
         "Una zapata cerca de la ladera tiene menor capacidad; exige análisis de estabilidad global.", "NSR-10 H.4.2.1 d; Act 2 OE 3"),
        ("Carga vertical centrada: sin excentricidad, sin inclinación, zapata cuadrada.", "Las fuerzas de frenado y sismo de una terminal reducen la capacidad.", "NSR-10 H.4.2.1 b; H.4.10"),
        ("El sismo entra solo por el FS 1,5; no se evalúan licuación, densificación ni pérdida de resistencia.", "La combinación sísmica queda sin verificar en rigor.", "NSR-10 H.4.2.1 e; capítulo H.7"),
        ("Asentamiento elástico con E de tabla genérica y medio homogéneo; no se calcula consolidación ni asentamiento secundario ni colapso por saturación de la ceniza.",
         "El criterio de servicio es indicativo; el límite de 25 mm es una hipótesis.", "NSR-10 H.4.2.2, H.4.8, H.4.9"),
        ("Un solo método (Meyerhof). EM 1110-1-1905 recomienda contrastar con dos o más modelos.", "Sin contraste Hansen / Vesic.", "EM 1110-1-1905 §4-2"),
        ("La roca (R1-R4) no entra: está bajo la cobertura y Meyerhof es un método para suelo.", "Si la exploración encuentra roca a poca profundidad, cambia el método y el orden de magnitud.", "Act 3, hoja Roca"),
    ]
    for i, (a, b, c_) in enumerate(lims, start=1):
        rr = 3 + i
        celda(lm, rr, 1, i, NEGRA)
        celda(lm, rr, 2, a, wrap=True)
        celda(lm, rr, 3, b, wrap=True)
        celda(lm, rr, 4, c_, wrap=True)
        lm.row_dimensions[rr].height = 46
    rr = 3 + len(lims) + 2
    lm.cell(rr, 1, "Tabla 9. Exploración mínima para convertir el rango en un valor de diseño").font = Font(name=F, size=13, bold=True, color=AZUL)
    cabecera(lm, rr + 1, ["#", "Ensayo o actividad", "Qué resuelve", "Referencia"])
    exps = [
        ("Sondeos con SPT y recuperación de muestras en cada portal, hasta roca o hasta la profundidad que fije el capítulo H.3.", "Espesor de S1 / S2, estratigrafía, N para E y φ.", "NSR-10 H.3"),
        ("Piezómetros o registro del nivel freático en los sondeos.", "Elimina la bifurcación «NF en la base / NF profundo».", "NSR-10 H.4.2.1 a"),
        ("Triaxiales CU con medición de presión de poros (o CD) sobre muestras inalteradas.", "c′ y φ′ efectivos del sitio.", "NSR-10 H.2.4"),
        ("Consolidación unidimensional y ensayo de colapso por inundación en la ceniza.", "Asentamientos por consolidación y colapso.", "NSR-10 H.4.8"),
        ("Sísmica de refracción o MASW.", "Profundidad de roca y Vs para el perfil sísmico.", "NSR-10 A.2.4"),
        ("Clasificación, límites de Atterberg, humedad natural y peso unitario.", "γ del sitio y clasificación SCUS (H.2.5).", "NSR-10 H.2.5"),
    ]
    for i, (a, b, c_) in enumerate(exps, start=1):
        r2 = rr + 1 + i
        celda(lm, r2, 1, i, NEGRA)
        celda(lm, r2, 2, a, wrap=True)
        celda(lm, r2, 3, b, wrap=True)
        celda(lm, r2, 4, c_, wrap=True)
        lm.row_dimensions[r2].height = 32

    # ============================================================ Marcas y fuentes
    m = wb.create_sheet("Marcas y fuentes")
    m.sheet_view.showGridLines = False
    titulo(m, "Tabla 10. Marcas de origen")
    cabecera(m, 3, ["Marca", "Significado"], [12, 110])
    for i, (a, b) in enumerate((("F", "Dato de fuente publicada, leído en el documento original descargado"),
                                ("CP", "Cálculo propio, reproducible con las fórmulas de este libro y el script citado"),
                                ("H", "Hipótesis o supuesto del semillero, declarado; fondo amarillo en las celdas"))):
        celda(m, 4 + i, 1, a, NEGRA)
        celda(m, 4 + i, 2, b)
    m["A9"] = "Tabla 11. Fuentes citadas"
    m["A9"].font = Font(name=F, size=13, bold=True, color=AZUL)
    cabecera(m, 10, ["Clave", "Referencia", "Enlace / ruta"], [12, 110, 70])
    m.column_dimensions["C"].width = 70
    fuentes = [
        ("ACT3", "Semillero GEOPAV (2026). Cuadro de parámetros geotécnicos adoptados y su rango de sensibilidad. OE 3, Act 3 (suelos S1 y S2).",
         "OE3_Geotecnia/Act3_Parametros/Cuadro_parametros_adoptados_OE3.xlsx"),
        ("EM1905", "U.S. Army Corps of Engineers (1992). EM 1110-1-1905 Bearing Capacity of Soils. Ec. 4-1, tabla 4-3 (Meyerhof 1953, 1963) p. 4-5, tabla 4-4 p. 4-6, §1-2 d (nivel freático), §4-2.",
         "https://pdhlibrary.com/sites/default/files/EM%201110-1-1905%20-%20Bearing%20Capacity%20of%20Soils%20.pdf (md5 f41333aa…)"),
        ("FHWA088", "FHWA (2006). Soils and Foundations Reference Manual, Vol. I, FHWA NHI-06-088. Tabla 5-16 «Elastic constants of various soils», p. 5-85.",
         "https://www.fhwa.dot.gov/engineering/geotech/pubs/nhi06088.pdf (md5 520fb556…)"),
        ("FHWA089", "FHWA (2006). Soils and Foundations Reference Manual, Vol. II, FHWA NHI-06-089. Ec. 8-19 y tabla 8-13 (Cd), p. 8-58 y 8-59.",
         "https://www.fhwa.dot.gov/engineering/geotech/pubs/nhi06089.pdf (md5 9795a31e…)"),
        ("NSR10", "NSR-10, Título H: H.2.4 (tabla H.2.4-1), H.4.2.1-H.4.2.3, H.4.7.1 (tabla H.4.7-1), H.4.8, H.4.9 (tabla H.4.9-1). Verificado en el texto de la norma.",
         "https://www.scg.org.co/Titulo-H-NSR-10-Decreto%20Final-2010-01-14.pdf"),
        ("ACT2", "Semillero GEOPAV (2026). Mapa base de susceptibilidad y pendientes locales de los portales. OE 3, Act 2.",
         "OE3_Geotecnia/Act2_Amenaza/pendiente_portales_OE3.json"),
    ]
    for i, (a, b, c_) in enumerate(fuentes):
        celda(m, 11 + i, 1, a, NEGRA)
        celda(m, 11 + i, 2, b, wrap=True)
        celda(m, 11 + i, 3, c_, wrap=True)
        m.row_dimensions[11 + i].height = 34

    for hoja in wb.worksheets:  # impresión: horizontal, ajustada al ancho de la página
        hoja.page_setup.orientation = "landscape"
        hoja.page_setup.fitToWidth, hoja.page_setup.fitToHeight = 1, 0
        hoja.sheet_properties.pageSetUpPr.fitToPage = True
    wb.save(SALIDA)
    peor = min(minimo_fsb)
    print("escrito", SALIDA)
    print("FSB equivalente: menor margen", round(peor[0], 3), peor[1:])


if __name__ == "__main__":
    main()
