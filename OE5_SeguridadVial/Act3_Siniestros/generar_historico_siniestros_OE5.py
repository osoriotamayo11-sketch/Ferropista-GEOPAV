# -*- coding: utf-8 -*-
"""
OE 5 - Actividad 3 (fila 33 del Cronograma)
Recopilacion de reportes de siniestralidad de la ANSV para los municipios del corredor.
Producto: Historico_siniestros_OE5.pdf   (mas dos CSV de respaldo)

Semillero de Investigacion GEOPAV - Universidad de Ibague - Paz y Region 2026B

FUENTES  [F]
  ANSV - Sectores Criticos de Siniestralidad Vial   datos.gov.co  rs3u-8r4q
  ANSV - Sectores Criticos por Exceso de Velocidad  datos.gov.co  24ny-2dhf

El script descarga los DOS conjuntos NACIONALES completos y filtra en local. Se descarga
todo a proposito: la pregunta de esta actividad es que hay y que NO hay en cada municipio
del corredor, y eso no se puede responder pidiendo solo lo que ya se espera encontrar.
"""

import csv
import json
import os
import urllib.request

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle, KeepTogether)

# El script vive en Act3_Siniestros/ y escribe el PDF y los CSV en esa misma carpeta.
BASE = os.path.dirname(os.path.abspath(__file__))
DATOS = BASE
SALIDA = os.path.join(BASE, "Historico_siniestros_OE5.pdf")

API = "https://www.datos.gov.co/resource"
REC_SINIESTROS = "rs3u-8r4q"
REC_VELOCIDAD = "24ny-2dhf"

MUNICIPIOS_CORREDOR = ["IBAGUÉ", "CAJAMARCA", "CALARCÁ", "ARMENIA"]

AZUL = colors.HexColor("#193F77")
VERDE = colors.HexColor("#0F7B55")
GRIS = colors.HexColor("#475569")
GRIS_CLARO = colors.HexColor("#F1F5F9")
LINEA = colors.HexColor("#CBD5E1")


# ------------------------------------------------------------------ datos
def descargar(recurso):
    url = f"{API}/{recurso}.json?$limit=50000"
    with urllib.request.urlopen(url, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def guardar_csv(filas, ruta, campos):
    with open(ruta, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=campos, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for f in filas:
            w.writerow(f)


def confianza(z):
    """Niveles estandar de Getis-Ord Gi*."""
    a = abs(z)
    if a >= 2.58:
        return "99 %"
    if a >= 1.96:
        return "95 %"
    if a >= 1.65:
        return "90 %"
    return "no significativo"


def es_co(v, dec=0):
    s = f"{v:,.{dec}f}"
    return s.replace(",", "@").replace(".", ",").replace("@", ".")


# ------------------------------------------------------------------ estilos
ss = getSampleStyleSheet()
P = ParagraphStyle("P", parent=ss["Normal"], fontName="Helvetica", fontSize=9.5,
                   leading=13.5, alignment=TA_JUSTIFY, spaceAfter=6, textColor=colors.black)
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=15,
                    leading=19, textColor=AZUL, spaceBefore=2, spaceAfter=3)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=11,
                    leading=15, textColor=AZUL, spaceBefore=13, spaceAfter=5)
H3 = ParagraphStyle("H3", parent=ss["Heading3"], fontName="Helvetica-Bold", fontSize=9.5,
                    leading=13, textColor=VERDE, spaceBefore=9, spaceAfter=3)
SUB = ParagraphStyle("SUB", parent=P, fontSize=9, textColor=GRIS, spaceAfter=2)
NOTA = ParagraphStyle("NOTA", parent=P, fontSize=8, leading=11, textColor=GRIS)
CELDA = ParagraphStyle("CELDA", parent=P, fontSize=8, leading=10.5, alignment=0, spaceAfter=0)
CELDA_B = ParagraphStyle("CELDA_B", parent=CELDA, fontName="Helvetica-Bold")
DEST = ParagraphStyle("DEST", parent=P, fontSize=9.5, leading=13.5,
                      leftIndent=8, rightIndent=8, spaceBefore=6, spaceAfter=8,
                      borderPadding=7, backColor=GRIS_CLARO, borderColor=LINEA, borderWidth=0.6)


def tabla(datos, anchos, cabecera=True):
    t = Table(datos, colWidths=anchos, repeatRows=1 if cabecera else 0, hAlign="LEFT")
    est = [
        ("GRID", (0, 0), (-1, -1), 0.4, LINEA),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]
    if cabecera:
        est += [("BACKGROUND", (0, 0), (-1, 0), AZUL),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)]
    t.setStyle(TableStyle(est))
    return t


def encabezado_pie(canv, doc):
    canv.saveState()
    canv.setStrokeColor(LINEA)
    canv.setLineWidth(0.5)
    canv.line(20 * mm, A4[1] - 15 * mm, A4[0] - 20 * mm, A4[1] - 15 * mm)
    canv.setFont("Helvetica", 7.5)
    canv.setFillColor(GRIS)
    canv.drawString(20 * mm, A4[1] - 13 * mm,
                    "OE 5 · Actividad 3 · Histórico de siniestros — Semillero GEOPAV, Universidad de Ibagué")
    canv.line(20 * mm, 15 * mm, A4[0] - 20 * mm, 15 * mm)
    canv.drawString(20 * mm, 11 * mm, "Ferropista Cordillera Central · Paz y Región 2026B")
    canv.drawRightString(A4[0] - 20 * mm, 11 * mm, f"Página {doc.page}")
    canv.restoreState()


# ------------------------------------------------------------------ main
def main():
    sin = descargar(REC_SINIESTROS)
    vel = descargar(REC_VELOCIDAD)

    guardar_csv(sin, os.path.join(DATOS, "ansv_sectores_criticos_nacional.csv"),
                ["departamento", "municipio", "divipola", "entidad", "tramo", "pr",
                 "fallecidos", "latitud", "longitud", "gizscore", "gipvalue", "nombre"])
    guardar_csv(vel, os.path.join(DATOS, "ansv_velocidad_nacional.csv"),
                ["departamento", "municipio", "divipola", "entidad", "pr",
                 "icount", "clasificacion", "latitud", "longitud"])

    def norm(x):
        return (x or "").strip().upper()

    corredor = [r for r in sin if norm(r.get("tramo")) == "CALARCÁ - IBAGUÉ"]
    calarca = [r for r in sin if norm(r.get("municipio")) == "CALARCÁ"]
    en_mun = {m: [r for r in sin if norm(r.get("municipio")) == m] for m in MUNICIPIOS_CORREDOR}
    vel_mun = {m: [r for r in vel if norm(r.get("municipio")) == m] for m in MUNICIPIOS_CORREDOR}

    tolima_sin = [r for r in sin if norm(r.get("departamento")) == "TOLIMA"]
    tot_tolima = sum(int(r["fallecidos"]) for r in tolima_sin)
    otros = sorted({(r["municipio"] or "").title() for r in tolima_sin
                    if norm(r.get("municipio")) != "IBAGUÉ"})
    municipios_tolima = ", ".join(otros[:-1]) + " y " + otros[-1] if len(otros) > 1 else otros[0]

    tot_calarca = sum(int(r["fallecidos"]) for r in calarca)
    tot_paso = sum(int(r["fallecidos"]) for r in corredor)

    doc = BaseDocTemplate(SALIDA, pagesize=A4,
                          leftMargin=20 * mm, rightMargin=20 * mm,
                          topMargin=20 * mm, bottomMargin=20 * mm,
                          title="Histórico de siniestros - OE 5 Act 3 - Semillero GEOPAV",
                          author="Semillero de Investigación GEOPAV - Universidad de Ibagué",
                          invariant=1)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
    doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=encabezado_pie)])

    S = []
    A = S.append

    A(Paragraph("Histórico de siniestros del corredor Ibagué – Calarcá", H1))
    A(Paragraph("Objetivo específico 5 · Actividad 3 · Recopilación de reportes de siniestralidad "
                "de la ANSV para los municipios del corredor", SUB))
    A(Paragraph("Semillero de Investigación GEOPAV · Ingeniería Civil · Universidad de Ibagué · "
                "Semestre Paz y Región 2026B · Ruta Nacional 40, paso del Alto de La Línea", SUB))
    A(Spacer(1, 8))

    A(Paragraph("Marcas de origen: <b>[F]</b> dato de fuente externa citada · <b>[CP]</b> cálculo "
                "propio reproducible · <b>[H]</b> hipótesis declarada · <b>[DA]</b> dato abierto "
                "pendiente de consulta. Una cifra sin marca no entra a este documento.", NOTA))

    # ---------------------------------------------------------- 1
    A(Paragraph("1. Qué recopila este documento y por qué se descargó todo el país", H2))
    A(Paragraph(
        "Esta actividad no busca los siniestros del corredor: busca <b>qué reporta y qué no reporta "
        "la ANSV en cada municipio del corredor</b>. Son preguntas distintas. La primera se responde "
        "filtrando; la segunda solo se responde descargando el conjunto nacional completo y mirando "
        "también donde no se espera encontrar nada. Por eso el script descarga los "
        f"<b>{es_co(len(sin))} registros</b> del conjunto de sectores críticos de siniestralidad y los "
        f"<b>{es_co(len(vel))} registros</b> del conjunto de sectores críticos por exceso de velocidad, "
        "y filtra en local.", P))

    A(Paragraph("Los dos conjuntos consultados", H3))
    A(tabla([
        [Paragraph("Conjunto", CELDA_B), Paragraph("Qué mide, según la ANSV", CELDA_B),
         Paragraph("Base y periodo", CELDA_B), Paragraph("Registros", CELDA_B)],
        [Paragraph("Sectores Críticos de Siniestralidad Vial<br/><font size=7>rs3u-8r4q</font>", CELDA),
         Paragraph("Tramos homogéneos de máximo 10 km sobre la red vial nacional primaria y "
                   "secundaria, con siniestros <b>con fatalidades</b>.", CELDA),
         Paragraph("SPOA (Fiscalía), que coincide en su gran mayoría con Medicina Legal. "
                   "<b>2015 – 2019</b>.", CELDA),
         Paragraph(es_co(len(sin)), CELDA)],
        [Paragraph("Sectores Críticos por Exceso de Velocidad<br/><font size=7>24ny-2dhf</font>", CELDA),
         Paragraph("Tramos de 1 km donde se registran vehículos <b>de carga</b> que superan "
                   "los 80 km/h. Clasifica por velocidad promedio del sector.", CELDA),
         Paragraph("NAVISAF, <b>año 2020</b>, sobre 970.000 registros de velocidad.", CELDA),
         Paragraph(es_co(len(vel)), CELDA)],
    ], [42 * mm, 55 * mm, 47 * mm, 18 * mm]))
    A(Spacer(1, 4))
    A(Paragraph("Ambos son de la Agencia Nacional de Seguridad Vial, cobertura nacional, "
                "actualización anual, publicados en datos.gov.co. <b>[F]</b>", NOTA))

    # ---------------------------------------------------------- 2
    A(Paragraph("2. Línea base: los sectores críticos del corredor", H2))
    A(Paragraph(
        f"Dentro del corredor de análisis hay <b>{len(calarca)} sectores críticos</b>, "
        f"con <b>{tot_calarca} fallecidos</b> acumulados en el periodo 2015 – 2019. De ellos, "
        f"<b>{tot_paso} corresponden al tramo «Calarcá – Ibagué»</b> a cargo de INVÍAS, que es el "
        "cruce de la cordillera propiamente dicho. <b>[F]</b>", P))

    filas = [[Paragraph(x, CELDA_B) for x in
              ["Municipio", "Entidad", "Tramo", "PR", "Fall.", "Coordenadas",
               "Gi* z", "Confianza"]]]
    for r in sorted(calarca, key=lambda x: -int(x["fallecidos"])):
        z = float(r["gizscore"])
        filas.append([
            Paragraph(r["municipio"], CELDA),
            Paragraph(r.get("entidad", ""), CELDA),
            Paragraph(r.get("tramo") or "<i>(sin dato)</i>", CELDA),
            Paragraph(str(r.get("pr", "")), CELDA),
            Paragraph(f"<b>{r['fallecidos']}</b>", CELDA),
            Paragraph(f"{float(r['latitud']):.4f} / {float(r['longitud']):.4f}".replace(".", ","), CELDA),
            Paragraph(es_co(z, 3), CELDA),
            Paragraph(confianza(z), CELDA),
        ])
    A(tabla(filas, [19 * mm, 25 * mm, 26 * mm, 9 * mm, 11 * mm, 32 * mm, 15 * mm, 25 * mm]))

    A(Spacer(1, 5))
    A(Paragraph("Cómo se lee la columna Gi*", H3))
    A(Paragraph(
        "<b>El conjunto ya trae hecho el análisis de puntos calientes.</b> Los campos "
        "<font face='Courier' size=8>GiZScore</font> y <font face='Courier' size=8>GiPValue</font> "
        "son el resultado del estadístico <b>Getis-Ord Gi*</b>, que mide si una concentración de "
        "fallecidos es mayor de lo que cabría esperar por azar. La confianza se lee con los umbrales "
        "estándar del estadístico: |z| ≥ 2,58 → 99 %; |z| ≥ 1,96 → 95 %; |z| ≥ 1,65 → 90 %. <b>[CP]</b>", P))
    A(Paragraph(
        "<b>Consecuencia metodológica:</b> el semillero no calcula ningún mapa de calor propio. "
        "Hacer una estimación de densidad sobre estos puntos sería el mapa de calor de un mapa de "
        "calor. Además, con seis puntos ningún estimador de densidad tiene sentido estadístico, y el "
        "método clásico reparte densidad en dos dimensiones mientras que una carretera es una línea: "
        "las manchas se saldrían de la vía. La visualización del objetivo usa el Gi* que la fuente ya "
        "publica.", DEST))

    # ---------------------------------------------------------- 3
    A(Paragraph("3. Revisión municipio por municipio", H2))
    A(Paragraph(
        "La actividad pide los reportes «para los municipios del corredor». Esto es lo que hay en "
        "cada uno, en los dos conjuntos: <b>[F]</b>", P))

    filas = [[Paragraph(x, CELDA_B) for x in
              ["Municipio", "Sectores críticos de siniestralidad", "Fallecidos",
               "Sectores críticos por velocidad", "Dónde están"]]]
    detalle = {
        "IBAGUÉ": "Vía <b>Ibagué – Girardot</b> y salida nororiental hacia Alvarado. "
                  "Ninguno en la vía al paso.",
        "CAJAMARCA": "—",
        "CALARCÁ": "Los seis, sobre el descenso del paso.",
        "ARMENIA": "—",
    }
    for m in MUNICIPIOS_CORREDOR:
        s = en_mun[m]
        v = vel_mun[m]
        fall = sum(int(r["fallecidos"]) for r in s)
        filas.append([
            Paragraph(m.title(), CELDA_B),
            Paragraph(f"<b>{len(s)}</b>" if s else "ninguno", CELDA),
            Paragraph(str(fall) if s else "—", CELDA),
            Paragraph(f"<b>{len(v)}</b>" if v else "ninguno", CELDA),
            Paragraph(detalle[m], CELDA),
        ])
    A(tabla(filas, [24 * mm, 33 * mm, 18 * mm, 30 * mm, 57 * mm]))

    # ---------------------------------------------------------- 4
    A(Paragraph("4. El hallazgo del lado tolimense", H2))
    A(Paragraph(
        "<b>Ni el conjunto de siniestralidad ni el de velocidad reportan un solo punto en el tramo "
        "Cajamarca – Ibagué, ni en el municipio de Cajamarca.</b> Los seis sectores críticos del "
        "corredor están en jurisdicción de Calarcá, Quindío. Esto exigía verificar si la ausencia era "
        "real o si el filtro geográfico del semillero la había producido.", P))
    A(Paragraph("Lo que descartó la revisión nacional", H3))
    A(Paragraph(
        f"<b>No es falta de cobertura departamental.</b> La ANSV reporta <b>{len(tolima_sin)} sectores "
        f"críticos en el Tolima</b>, con <b>{tot_tolima} fallecidos</b>, e incluye el municipio de "
        f"Ibagué: un sector en el tramo Ibagué – Girardot con 13 fallecidos. Los demás están en "
        f"{municipios_tolima}. El departamento está cubierto; lo que no aparece es la vía al "
        f"paso. <b>[F]</b>", P))
    A(Paragraph(
        "<b>La ausencia en el conjunto de velocidad sí tiene explicación técnica, y es coherente.</b> "
        "Ese conjunto solo registra tramos donde vehículos de carga <b>superan los 80 km/h</b>. En el "
        "paso del Alto de La Línea la velocidad media de operación es inferior a 20 km/h "
        "<b>[F, ponencia dia. 13]</b>. Ningún camión alcanza el umbral, de modo que el paso no puede "
        "aparecer en ese conjunto por construcción del método. La ausencia no indica seguridad: indica "
        "congestión. Es, de hecho, una confirmación independiente de la velocidad que declara la "
        "fuente primaria.", DEST))
    A(Paragraph("Lo que queda abierto", H3))
    A(Paragraph(
        "Para el conjunto de siniestralidad la pregunta sigue viva y solo admite dos lecturas: "
        "o el descenso hacia Calarcá concentra efectivamente la mortalidad del cruce —coherente con "
        "el mecanismo del descenso prolongado con carga pesada—, o el tramo tolimense no superó el "
        "umbral con el que la ANSV define un sector crítico. <b>El semillero no escoge en silencio.</b> "
        "Se dirime contrastando con las cifras municipales de Forensis para Cajamarca e Ibagué del "
        "mismo periodo 2015 – 2019: si allí aparecen fallecidos en vía que la ANSV no georreferenció, "
        "manda la segunda lectura. <b>[DA]</b>", P))

    # ---------------------------------------------------------- 5
    A(Paragraph("5. Limitaciones declaradas", H2))
    for t in [
        "El conjunto reporta <b>únicamente fallecidos</b>: no incluye heridos ni siniestros con solo "
        "daños materiales. La línea base es de mortalidad, no de siniestralidad total.",
        "Es un <b>producto derivado</b> de análisis espacial, no el microdato por siniestro. No permite "
        "reconstruir cada evento ni conocer el tipo de vehículo implicado. Se buscó el microdato "
        "georreferenciado por siniestro y solo se encontró publicado para Bogotá; para carreteras "
        "nacionales no se localizó ninguno de acceso abierto. <b>[DA]</b>",
        "El periodo <b>2015 – 2019 es anterior</b> a la entrada en operación del Túnel de La Línea "
        "(4 de septiembre de 2020, 8,6 km), que cambió la geometría, la velocidad de operación y la "
        "composición del tránsito. La línea base describe un corredor que ya no es el actual y "
        "<b>sobrestima</b> la siniestralidad de hoy.",
        "El conjunto de velocidad usa datos de <b>2020</b>, un año atípico por las restricciones de "
        "movilidad. Se usa aquí solo como control de cobertura, no como medida de exposición.",
        "Un «sector crítico» es una categoría de la ANSV con su propio umbral, no un censo de siniestros: "
        "que un tramo no aparezca no significa que no haya tenido fallecidos.",
    ]:
        A(Paragraph(f"• {t}", P))

    # ---------------------------------------------------------- 6
    A(Paragraph("6. Trazabilidad", H2))
    A(Paragraph(
        "Este documento y los dos CSV de respaldo los genera "
        "<font face='Courier' size=8>Act3_Siniestros/generar_historico_siniestros_OE5.py</font>, que descarga "
        "los conjuntos en el momento de ejecutarse. Cualquier persona puede reproducirlo, o verificar "
        "un registro entrando directamente a los conjuntos:", P))
    A(tabla([
        [Paragraph("Archivo", CELDA_B), Paragraph("Contenido", CELDA_B)],
        [Paragraph("<font face='Courier' size=7>Act3_Siniestros/ansv_sectores_criticos_nacional.csv</font>", CELDA),
         Paragraph(f"Los {es_co(len(sin))} registros nacionales del conjunto rs3u-8r4q, sin filtrar.", CELDA)],
        [Paragraph("<font face='Courier' size=7>Act3_Siniestros/ansv_velocidad_nacional.csv</font>", CELDA),
         Paragraph(f"Los {es_co(len(vel))} registros nacionales del conjunto 24ny-2dhf, sin filtrar.", CELDA)],
        [Paragraph("<font face='Courier' size=7>Act3_Siniestros/siniestros_ANSV_corredor.csv</font>", CELDA),
         Paragraph("Los seis sectores del corredor, producido por descarga_datos_OE5.py.", CELDA)],
    ], [92 * mm, 70 * mm]))
    A(Spacer(1, 5))
    A(Paragraph(
        "Conjuntos en línea: <font face='Courier' size=8>datos.gov.co/d/rs3u-8r4q</font> y "
        "<font face='Courier' size=8>datos.gov.co/d/24ny-2dhf</font>. La API devuelve el conjunto "
        "completo en JSON añadiendo <font face='Courier' size=8>/resource/&lt;id&gt;.json?$limit=50000</font>.", NOTA))

    doc.build(S)
    print("PDF escrito:", SALIDA)
    print(f"  siniestralidad: {len(sin)} registros nacionales | corredor: {len(calarca)} sectores, "
          f"{tot_calarca} fallecidos ({tot_paso} en el paso)")
    print(f"  velocidad:      {len(vel)} registros nacionales | Cajamarca y Calarca: "
          f"{len(vel_mun['CAJAMARCA'])} y {len(vel_mun['CALARCÁ'])}")


if __name__ == "__main__":
    main()
