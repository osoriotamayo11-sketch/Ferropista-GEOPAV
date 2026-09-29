# -*- coding: utf-8 -*-
"""Utilidades compartidas por los productos del OE 6 (eficiencia logística).

- Registro de fuentes con md5 calculado al vuelo (nada de hashes escritos a mano).
- Lectura del SICE-TAC: la consulta oficial guardada en PDF por el usuario (29 sep 2026) y el
  listado oficial de distancias por tipo de terreno (corte 01-09-2026).
- Estilos y portada de los Excel según el estándar del semillero (verde #178E2C principal,
  azul #193F77 secundario; hoja «Portada» con logos, ficha e índice; «Tabla N.» en cada hoja).
Requiere openpyxl y pypdf.
"""
import hashlib
import json
import os
import re
import warnings

warnings.filterwarnings("ignore")
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

OE6 = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(OE6)
FUENTES = os.path.join(OE6, "Fuentes")
FECHA = "29 sep 2026"

# ---------------------------------------------------------------- fuentes
REF = {
    "PON": "Fernández Ordóñez, H. O. (2025). Túnel para cruce férreo de la Cordillera Central de los Andes y semilla para la Estrella Andina. "
           "XX Seminario Andino de Túneles y Obras Subterráneas, SAI, Medellín, 8 oct 2025. Fuente primaria del proyecto.",
    "SICETAC": "Ministerio de Transporte. SICE-TAC, consulta pública (plc.mintransporte.gov.co), periodo de referencia 20260901: tractocamión 3S3, "
               "portacontenedores, contenedor cargado, cargado, 2 h de cargue y 2 h de descargue. Rutas 14037 (Ibagué–Calarcá) y 15393 (Calarcá–Ibagué). "
               "Consultado y guardado en PDF el 29 sep 2026.",
    "SICETAC_DIST": "Ministerio de Transporte, Oficina de Regulación Económica. Distancias por tipo de terreno, rutas SICE-TAC, corte 01-09-2026 (xlsx).",
    "SICETAC_PEAJ": "Ministerio de Transporte. Peajes por rutas con tarifas, SICE-TAC, corte 01-09-2026 (xlsx).",
    "RES2024": "Ministerio de Transporte. Resolución 20243040057465 del 26-11-2024, protocolo SICE-TAC (anexo), págs. 13-14.",
    "RES2026": "Ministerio de Transporte. Resolución 20263040018445 de 2026 (14-05-2026), actualización del SICE-TAC.",
    "CAF": "CAF (2024). Evaluación ex post: Proyecto Cruce de la Cordillera Central – Túnel II Centenario (Colombia), pág. 8 (impactos esperados).",
    "INVIAS": "INVÍAS. Cruce de la Cordillera Central – preguntas frecuentes. https://crucecordilleracentral.invias.gov.co/faqs.php (consultado 29 sep 2026).",
    "INVIAS_PMT": "Infobae (4 ago 2026), con declaraciones del INVÍAS: emergencia del PR 47+0380 a 47+0480 (Calle Larga, Cajamarca) desde el 25 jul 2026; "
                  "paso a un carril con «pare y siga» y alternancia de una hora por sentido.",
    "PRENSA_8H": "Semana (2 sep 2026): el alcalde de Cajamarca reporta trancones de 8 a 10 horas una o dos veces por semana; reapertura de ambos carriles prevista el 30 sep 2026.",
    "OSRM": "OpenStreetMap vía OSRM (router.project-osrm.org) y Nominatim, consultados el 29 sep 2026; respuestas crudas en Act2_TiempoFerropista/Datos/.",
    "OE1": "OE 1 del semillero: OE1_Topografia/cifras_OE1.json y Act2_Portales/puntos_control_portales.geojson (portales adoptados).",
}
_pon = [f for f in os.listdir(RAIZ) if "SAI-" in f and f.lower().endswith(".pdf")] if os.path.isdir(RAIZ) else []
ARCHIVOS = {
    "PON": os.path.join(RAIZ, _pon[0]) if _pon else os.path.join(RAIZ, "ponencia_SAI_no_encontrada.pdf"),
    "SICETAC_IBG_CAL": os.path.join(FUENTES, "sicetac_IBG_CAL_3S3.pdf"),
    "SICETAC_CAL_IBG": os.path.join(FUENTES, "sicetac_CAL_IBG_3S3.pdf"),
    "SICETAC_DIST": os.path.join(FUENTES, "DISTANCIAS_TIPO_DE_TERRENO_RUTAS_SICETAC-2026-09-01.xlsx"),
    "SICETAC_PEAJ": os.path.join(FUENTES, "PeajesPorRutasConTarifas_SICETAC_2026-09-01.xlsx"),
    "RES2024": os.path.join(FUENTES, "Anexo_Resolucion_20243040057465.pdf"),
    "RES2026": os.path.join(FUENTES, "Resolucion_20263040018445_14-05-2026_SICE-TAC.pdf"),
    "CAF": os.path.join(FUENTES, "caf_expost_linea_2024.pdf"),
}


# Huellas de los archivos con que se calcularon los productos del 29 sep 2026. Si un archivo cambia, el script se detiene.
MD5_ESPERADO = {
    "PON": "2e7d264eb6d98f368dc9a6bd5bf5bd6d",
    "SICETAC_IBG_CAL": "c991f42266763925dbb7f1ff4d959ed5",
    "SICETAC_CAL_IBG": "d5db8d1a5738d305169b755f79936152",
    "SICETAC_DIST": "0da631933a44d12069e59806877b8982",
    "SICETAC_PEAJ": "fc08f828f3d1785a0a236a0cdc44a8c2",
    "RES2024": "4b904c9c93e17704b40d7829009435d5",
    "RES2026": "28f13ac110aa2ecd716f217ffac04e11",
    "CAF": "e37299dc391fa062e9b2e7d508630d62",
}


def fuente_verificada(clave):
    """Ruta del archivo de una fuente, tras comprobar su md5. Se detiene si falta o si no coincide."""
    ruta = ARCHIVOS[clave]
    if not os.path.exists(ruta):
        raise SystemExit(f"ALTO: falta la fuente {clave} ({os.path.relpath(ruta, RAIZ)}). Ver REF['{clave.split('_')[0]}'] para descargarla.")
    h = md5(ruta)
    if clave in MD5_ESPERADO and h != MD5_ESPERADO[clave]:
        raise SystemExit(f"ALTO: la fuente {clave} cambió (md5 {h}, esperado {MD5_ESPERADO[clave]}). Revisar antes de recalcular.")
    return ruta


def md5(ruta):
    if not os.path.exists(ruta):
        return "no disponible en esta copia"
    h = hashlib.md5()
    with open(ruta, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def texto_pdf(ruta):
    from pypdf import PdfReader
    return "\n".join((p.extract_text() or "") for p in PdfReader(ruta).pages)


def es(v, dec=1):
    """Formato numérico es-CO: coma decimal, punto de miles."""
    return f"{v:,.{dec}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def num(s):
    """'$1,255,108.00' -> 1255108.0 (el SICE-TAC publica en formato en-US)."""
    return float(s.replace("$", "").replace(",", "").strip())


# ---------------------------------------------------------------- SICE-TAC
RUTAS = {"IBG_CAL": {"id": 14037, "nombre": "Ibagué → Calarcá", "pdf": "SICETAC_IBG_CAL"},
         "CAL_IBG": {"id": 15393, "nombre": "Calarcá → Ibagué", "pdf": "SICETAC_CAL_IBG"}}
TERRENOS = ["Plano", "Ondulado", "Montaña", "Urbano", "Afirmado"]


def leer_sicetac(clave):
    """Lee la consulta SICE-TAC guardada en PDF. Devuelve un dict con todo lo que usa el OE 6."""
    t = texto_pdf(fuente_verificada(RUTAS[clave]["pdf"]))
    M = r"\$?([\d,]+(?:\.\d{1,2})?)"

    def uno(pat):
        m = re.search(pat, t, re.S)
        if not m:
            raise ValueError(f"No se encontró «{pat}» en la consulta SICE-TAC {clave}")
        return num(m.group(1))

    d = {"ruta": RUTAS[clave]["nombre"], "ruta_id": RUTAS[clave]["id"]}
    d["periodo"] = re.search(r"Periodo de referencia \(AAAAMMDD\):\s*(\d{8})", t).group(1)
    d["config"] = re.search(r"configuracion:\s*(Tractocami[^\n]+)", t).group(1).strip()
    d["costo_hora"] = uno(r"Costo Hora\s*" + M)
    d["horas_espera"] = uno(r"Horas de Espera\s*([\d.]+)")
    d["costo_espera"] = uno(r"Costo Tiempos de Espera\s*" + M)
    d["costo_mov_carga"] = uno(r"Costo Movilización\s*Carga\s*" + M)
    d["costo_total_viaje"] = uno(r"Costo Total del Viaje\s*i?\s*" + M)
    d["cf_mes"] = uno(r"Subtotal Costos Fijos\s*" + M)
    d["cf_viaje"] = uno(r"Subtotal Costos Fijos\s*\$[\d,.]+\s*" + M)
    d["cv_viaje"] = uno(r"Subtotal Costos Variables\s*\$[\d,.]+\s*" + M)
    d["otros_viaje"] = uno(r"Subtotal Otros Costos\s*\$[\d,.]+\s*" + M)
    for k, pat in [("combustible", r"VARIABLE Combustible"), ("peajes", r"VARIABLE Peajes"), ("llantas", r"VARIABLE Llantas"),
                   ("lubricantes", r"VARIABLE Lubricantes"), ("filtros", r"VARIABLE Filtros"),
                   ("mantenimiento", r"VARIABLE Mantenimiento y Reparación"), ("lavado", r"VARIABLE Lavado y Engrase"),
                   ("imprevistos", r"VARIABLE Imprevistos\([\d.]+%\)\s*\$[\d,.]+")]:
        d["v_" + k] = uno(pat + r"\s*\$[\d,.]+\s*" + M) if k != "imprevistos" else uno(pat + r"\s*" + M)
    d["tasa_imprevistos"] = float(re.search(r"Imprevistos\(([\d.]+)%\)", t).group(1)) / 100
    d["o_comisiones"] = uno(r"OTROS Comisiones \+ Factor\s*Prestacional\s*\$[\d,.]+\s*" + M)
    d["o_admin"] = uno(r"OTROS Factor Administrativo\([\d.]+%\)\s*\$[\d,.]+\s*" + M)
    d["o_rete"] = uno(r"OTROS Retefuente \+ ICA[^$]*\$[\d,.]+\s*" + M)
    d["horas_habiles_mes"] = uno(r"Horas Hábiles del mes\s*i?\s*([\d.]+)")
    d["acpm"] = uno(r"Valor Combustible galón ACPM\s*i?\s*" + M)
    d["toneladas"] = uno(r"Toneladas de la Configuración\s*(\d+\.\d)")
    dist = re.search(r"Distancia \(Km\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", t).groups()
    d["dist_total_km"] = float(dist[0]); d["dist_km"] = dict(zip(TERRENOS, map(float, dist[1:])))
    vel = re.search(r"Velocidad Promedio \(Km/h\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", t).groups()
    d["vel_kmh"] = dict(zip(TERRENOS, map(float, vel)))
    d["horas_viaje_pub"] = uno(r"Horas de viaje\s+([\d.]+)")
    cons = re.search(r"\(Km/gln\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", t).groups()
    d["rend_kmgal"] = dict(zip(TERRENOS, map(float, cons)))
    d["factor_viajes"] = uno(r"Factor de viajes\s*([\d.]+)")
    d["horas_recorrido"] = uno(r"Horas Recorrido \(Viaje \+\s*Espera\)\s*([\d.]+)")
    # por kilómetro, de las tablas de parámetros
    d["km_llantas"] = uno(r"Total llantas\s*" + M)
    d["km_lubricantes"] = uno(r"Total Lubricantes\s*" + M)
    d["km_filtros"] = uno(r"Total filtros\s*" + M)
    d["km_mantenimiento"] = uno(r"Total Sistemas de Mantenimiento\s*" + M)
    d["km_lavado"] = uno(r"Total lavado y engrase\s*" + M)
    d["peajes_lista"] = peajes_ruta(RUTAS[clave]["id"])
    if abs(sum(v for _, v in d["peajes_lista"]) - d["v_peajes"]) > 1:
        raise ValueError(f"Peajes del listado oficial ≠ peajes de la consulta ({clave})")
    return d


def peajes_ruta(ruta_id, categoria=5):
    """Peajes de una ruta en el listado oficial SICE-TAC (categoría V = tractocamión 3S3)."""
    from openpyxl import load_workbook
    ws = load_workbook(fuente_verificada("SICETAC_PEAJ"), read_only=True).active
    out = []
    for f in ws.iter_rows(min_row=6, values_only=True):
        if f[0] == ruta_id:
            out.append((f"{f[3]}", float(f[6 + categoria])))
    return out


def distancias_oficiales():
    """Distancias por tipo de terreno de las dos rutas en el listado oficial (verificación cruzada con el PDF)."""
    from openpyxl import load_workbook
    ws = load_workbook(fuente_verificada("SICETAC_DIST"), read_only=True).active
    out = {}
    for fila in ws.iter_rows(min_row=6, values_only=True):
        for clave, r in RUTAS.items():
            if fila[0] == r["id"]:
                out[clave] = {"nombre_oficial": fila[3], "total": float(fila[5]),
                              "km": dict(zip(TERRENOS, [float(fila[6]), float(fila[7]), float(fila[8]), float(fila[9]), float(fila[10])]))}
    return out


def texto_contiene(clave, frases):
    """Comprueba que el PDF de una fuente contiene literalmente las frases citadas (evita citas de memoria)."""
    t = re.sub(r"\s+", " ", texto_pdf(fuente_verificada(clave)))
    faltan = [f for f in frases if re.sub(r"\s+", " ", f) not in t]
    if faltan:
        raise ValueError(f"La fuente {clave} no contiene: {faltan}")
    return True


# ---------------------------------------------------------------- Excel
F = "Calibri"
VERDE, AZUL, GRIS, ROJO = "178E2C", "193F77", "475569", "B91C1C"
NORMAL, NEGRA = Font(name=F, size=10), Font(name=F, size=10, bold=True)
ENTRADA, ENLACE = Font(name=F, size=10, color="0000FF"), Font(name=F, size=10, color="008000")
CAB = Font(name=F, size=10, bold=True, color="FFFFFF")
_L = Side(style="thin", color="CBD5E1")
BORDE = Border(left=_L, right=_L, top=_L, bottom=_L)
FILL_CAB, FILL_H, FILL_RES = PatternFill("solid", fgColor=AZUL), PatternFill("solid", fgColor="FFF7D6"), PatternFill("solid", fgColor="E8F3EA")
FMT_H, FMT_MIN, FMT_KM, FMT_COP, FMT_PCT = '#,##0.00" h"', '#,##0.0" min"', '#,##0.00" km"', '"$"#,##0', '0.0%'


def cab(ws, fila, textos, anchos=None, col0=1):
    for j, t in enumerate(textos, start=col0):
        c = ws.cell(fila, j, t)
        c.font, c.fill, c.border = CAB, FILL_CAB, BORDE
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    if anchos:
        for j, w in enumerate(anchos, start=col0):
            ws.column_dimensions[ws.cell(1, j).column_letter].width = w
    ws.row_dimensions[fila].height = 42


def c(ws, r, col, v, fuente=NORMAL, fmt=None, h=False, wrap=False, fill=None):
    x = ws.cell(r, col, v)
    x.font, x.border = fuente, BORDE
    x.alignment = Alignment(wrap_text=wrap, vertical="top")
    if fmt:
        x.number_format = fmt
    if h:
        x.fill = FILL_H
    if fill:
        x.fill = fill
    return x


def tit(ws, t, fila=1):
    ws.cell(fila, 1, t).font = Font(name=F, size=13, bold=True, color=AZUL)


def nota(ws, r, t, color=GRIS, ancho=8):
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ancho)
    x = ws.cell(r, 1, t)
    x.font = Font(name=F, size=9, italic=True, color=color)
    x.alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[r].height = max(15, 13 * (1 + len(t) // 150))


def portada(wb, titulo, subtitulo, actividad, entregable, hojas, pie, advertencia):
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
    p["B8"] = titulo
    p["B8"].font = Font(name=F, size=18, bold=True, color=VERDE)
    p["B9"] = subtitulo
    p["B9"].font = Font(name=F, size=12, color=AZUL)
    ficha = [
        ("Objetivo", "OE 6: Determinar la eficiencia logística del sistema intermodal Ferropista, calculando la reducción de tiempos de ciclo y de costos "
                     "operativos frente a la operación actual por la Ruta 40."),
        ("Actividad", actividad),
        ("Entregable / formato", entregable),
        ("Periodo", "Bloque 2 del Plan de Acción (5 oct - 7 nov 2026)"),
        ("Responsable asignado", "Torrente Parra Daniel Ignacio"),
        ("Apoyo en la ejecución", "Tamayo Osorio Miguel Ángel, con apoyo de IA (Claude)"),
        ("Semillero", "Semillero de Investigación GEOPAV · Ingeniería Civil · Universidad de Ibagué · Paz y Región 2026B"),
        ("Fecha de elaboración", FECHA),
        ("Advertencia", advertencia),
    ]
    for i, (k, v) in enumerate(ficha):
        r = 11 + i
        p.cell(r, 2, k).font = NEGRA
        p.cell(r, 2).alignment = Alignment(vertical="top", wrap_text=True)
        p.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
        x = p.cell(r, 3, v)
        x.font = NORMAL if k != "Advertencia" else Font(name=F, size=10, bold=True, color=ROJO)
        x.alignment = Alignment(wrap_text=True, vertical="top")
        p.row_dimensions[r].height = 30 if len(v) < 110 else (58 if len(v) < 260 else 86)
    r = 11 + len(ficha) + 1
    p.cell(r, 2, "Índice de hojas (tabla de contenido)").font = Font(name=F, size=12, bold=True, color=AZUL)
    r += 1
    for h_, d in hojas:
        p.cell(r, 2, h_).font = NEGRA
        p.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
        p.cell(r, 3, d).font = NORMAL
        p.cell(r, 3).alignment = Alignment(wrap_text=True, vertical="top")
        p.row_dimensions[r].height = 15 if len(d) < 105 else 30
        r += 1
    r += 1
    p.merge_cells(start_row=r, start_column=2, end_row=r + 4, end_column=7)
    x = p.cell(r, 2, pie + " Convención: azul = entrada leída de una fuente; verde = valor leído de otro producto del OE 6; fondo amarillo = hipótesis [H]; "
                          "negro = fórmula. Marcas: [F] fuente citada · [CP] cálculo propio reproducible · [H] hipótesis declarada · [DA] dato por consultar. "
                          "Elaborado con apoyo de IA (Claude) y verificado contra las fuentes.")
    x.font = Font(name=F, size=9, italic=True, color=GRIS)
    x.alignment = Alignment(wrap_text=True, vertical="top")
    return p


def hoja_fuentes(wb, claves, n_tabla):
    ws = wb.create_sheet("Fuentes")
    ws.sheet_view.showGridLines = False
    tit(ws, f"Tabla {n_tabla}. Fuentes citadas y huella md5 de los archivos usados")
    cab(ws, 3, ["Clave", "Referencia", "Archivo local", "md5"], [14, 100, 46, 36])
    r = 4
    for k in claves:
        ruta = ARCHIVOS.get(k)
        c(ws, r, 1, k, NEGRA)
        c(ws, r, 2, REF.get(k, REF.get(k.split("_")[0], "")), wrap=True)
        c(ws, r, 3, os.path.relpath(ruta, RAIZ).replace("\\", "/") if ruta else "—", wrap=True)
        c(ws, r, 4, md5(ruta) if ruta else "—")
        ws.row_dimensions[r].height = 44
        r += 1
    return ws


def guardar_json(ruta, d):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


def leer_json(*partes):
    with open(os.path.join(OE6, *partes), encoding="utf-8") as f:
        return json.load(f)
