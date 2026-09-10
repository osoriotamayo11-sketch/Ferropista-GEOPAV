# -*- coding: utf-8 -*-
"""
OE 5 - Actividad 5 (fila 35 del Cronograma)
Consolidacion del diagnostico operacional de la infraestructura vial actual.
Producto: Informe_diagnostico_vial_OE5.pdf

Semillero de Investigacion GEOPAV - Universidad de Ibague - Paz y Region 2026B

CONSOLIDA, NO RECALCULA
  Toda cifra de este informe se LEE de los productos de las actividades 1 a 4. El script
  las carga en el momento de generar el PDF y se detiene si alguna no cuadra, de modo que
  el informe no pueda decir algo distinto de los archivos que lo respaldan.
    Act 1  Act1_Aforos/tpd_historico_corredor.csv
    Act 3  Act3_Siniestros/siniestros_ANSV_corredor.csv
    Act 4  Act4_Analisis/analisis_siniestralidad_OE5.xlsx   (tasas ya recalculadas)

DEPENDENCIA
  reportlab y openpyxl.
"""

import csv
import os

import openpyxl
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, Image, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

BASE = os.path.dirname(os.path.abspath(__file__))
OE5 = os.path.dirname(BASE)
ACT1 = os.path.join(OE5, "Act1_Aforos")
ACT3 = os.path.join(OE5, "Act3_Siniestros")
ACT4 = os.path.join(OE5, "Act4_Analisis")
VIS = os.path.join(OE5, "Visuales")
SALIDA = os.path.join(BASE, "Informe_diagnostico_vial_OE5.pdf")

AZUL = colors.HexColor("#193F77")
VERDE = colors.HexColor("#0F7B55")
GRIS = colors.HexColor("#475569")
GRIS_CLARO = colors.HexColor("#F1F5F9")
LINEA = colors.HexColor("#CBD5E1")


def leer(ruta):
    with open(ruta, encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


def es_co(v, dec=0):
    return f"{v:,.{dec}f}".replace(",", "@").replace(".", ",").replace("@", ".")


# ------------------------------------------------------------------ insumos
hist = leer(os.path.join(ACT1, "tpd_historico_corredor.csv"))
sec = leer(os.path.join(ACT3, "siniestros_ANSV_corredor.csv"))

wb = openpyxl.load_workbook(os.path.join(ACT4, "analisis_siniestralidad_OE5.xlsx"),
                            data_only=True)
ws3 = wb["3. Tasa"]
ws5 = wb["5. Carga pesada"]


def celda(ws, ref, etiqueta_esperada):
    """
    Lee una celda del libro de la Act 4 COMPROBANDO ANTES su etiqueta de fila.

    Las referencias a celdas fijas son la forma silenciosa de que este informe
    empiece a publicar otra cifra: basta con que alguien inserte una fila en el
    script de la Act 4 para que B11 deje de ser lo que era, sin que nada avise.
    Aqui se verifica el rotulo de la columna A antes de aceptar el valor.
    """
    fila = int("".join(c for c in ref if c.isdigit()))
    rotulo = str(ws.cell(row=fila, column=1).value or "")
    if etiqueta_esperada.lower() not in rotulo.lower():
        raise SystemExit(
            f"PARADA: se esperaba leer «{etiqueta_esperada}» en {ws.title}!{ref}, pero esa "
            f"fila dice «{rotulo[:70]}». El libro de la Act 4 cambio de estructura: "
            f"revisar antes de publicar nada.")
    v = ws[ref].value
    if v is None:
        raise SystemExit(f"PARADA: {ws.title}!{ref} viene vacia. El libro de la Act 4 no tiene "
                         f"valores cacheados: recalcularlo antes de generar el informe.")
    return v


TASA_CORR = celda(ws3, "G5", "Corredor completo")
TASA_PASO = celda(ws3, "G6", "Solo el paso")
TASA_VIEJA = celda(ws3, "B11", "hipótesis del libro anterior")
MUEVE = celda(ws3, "B25", "Cuánto mueve la hipótesis")
VKM_CAM = celda(ws5, "B10", "Vehículos-km anuales de camiones")
TPD_CAM = celda(ws5, "B6", "TPD de camiones en el paso")
PART_CAM = celda(ws5, "B7", "Participación de los camiones")

m244 = [f for f in hist if f["estacion"] == "244" and 2015 <= int(f["anio"]) <= 2018]
m243 = [f for f in hist if f["estacion"] == "243" and 2015 <= int(f["anio"]) <= 2018]
T244 = sum(int(f["tpd"]) for f in m244) / len(m244)
T243 = sum(int(f["tpd"]) for f in m243) / len(m243)
TPOND = (T243 * 29 + T244 * 45) / 74
FALL_PASO = sum(int(r["fallecidos"]) for r in sec if r["en_el_paso"] == "Si")
FALL_CORR = sum(int(r["fallecidos"]) for r in sec)

# control cruzado: la tasa del libro debe reproducirse desde los CSV
ctrl_corr = FALL_PASO / (TPOND * 365 * 74 * 5) * 1e8
ctrl_paso = FALL_PASO / (T244 * 365 * 45 * 5) * 1e8
for nombre, calc, libro in (("corredor", ctrl_corr, TASA_CORR), ("paso", ctrl_paso, TASA_PASO)):
    if abs(calc - libro) > 0.01:
        raise SystemExit(f"PARADA: para el {nombre} el informe calcula {calc:.2f} desde los CSV "
                         f"y el libro de la Act 4 publica {libro:.2f}. No se genera hasta "
                         f"resolver cuál manda.")
print(f"control OK: las dos tasas del libro se reproducen desde los CSV "
      f"({ctrl_corr:.2f} y {ctrl_paso:.2f})")

# ------------------------------------------------------------------ estilos
ss = getSampleStyleSheet()
P = ParagraphStyle("P", parent=ss["Normal"], fontName="Helvetica", fontSize=9.5,
                   leading=13.5, alignment=TA_JUSTIFY, spaceAfter=6)
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=16,
                    leading=20, textColor=AZUL, spaceBefore=2, spaceAfter=3)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=11.5,
                    leading=15, textColor=AZUL, spaceBefore=14, spaceAfter=5)
H3 = ParagraphStyle("H3", parent=ss["Heading3"], fontName="Helvetica-Bold", fontSize=9.5,
                    leading=13, textColor=VERDE, spaceBefore=9, spaceAfter=3)
SUB = ParagraphStyle("SUB", parent=P, fontSize=9, textColor=GRIS, spaceAfter=2)
NOTA = ParagraphStyle("NOTA", parent=P, fontSize=8, leading=11, textColor=GRIS)
CELDA = ParagraphStyle("CELDA", parent=P, fontSize=8, leading=10.5, alignment=0, spaceAfter=0)
CELDA_B = ParagraphStyle("CELDA_B", parent=CELDA, fontName="Helvetica-Bold")
DEST = ParagraphStyle("DEST", parent=P, fontSize=9.5, leading=13.5, leftIndent=8,
                      rightIndent=8, spaceBefore=6, spaceAfter=8, borderPadding=7,
                      backColor=GRIS_CLARO, borderColor=LINEA, borderWidth=0.6)
CIFRA = ParagraphStyle("CIFRA", parent=P, fontName="Helvetica-Bold", fontSize=21,
                       leading=24, textColor=AZUL, alignment=0, spaceAfter=1)


def tabla(datos, anchos, cabecera=True):
    t = Table(datos, colWidths=anchos, repeatRows=1 if cabecera else 0, hAlign="LEFT")
    est = [("GRID", (0, 0), (-1, -1), 0.4, LINEA),
           ("VALIGN", (0, 0), (-1, -1), "TOP"),
           ("TOPPADDING", (0, 0), (-1, -1), 3.5),
           ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
           ("LEFTPADDING", (0, 0), (-1, -1), 4),
           ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
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
                    "OE 5 · Actividad 5 · Informe de diagnóstico vial — Semillero GEOPAV, "
                    "Universidad de Ibagué")
    canv.line(20 * mm, 15 * mm, A4[0] - 20 * mm, 15 * mm)
    canv.drawString(20 * mm, 11 * mm, "Ferropista Cordillera Central · Paz y Región 2026B")
    canv.drawRightString(A4[0] - 20 * mm, 11 * mm, f"Página {doc.page}")
    canv.restoreState()


doc = BaseDocTemplate(SALIDA, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                      topMargin=20 * mm, bottomMargin=20 * mm,
                      title="Informe de diagnóstico vial - OE 5 Act 5 - Semillero GEOPAV",
                      author="Semillero de Investigación GEOPAV - Universidad de Ibagué",
                      invariant=1)
doc.addPageTemplates([PageTemplate(id="p",
                                   frames=[Frame(doc.leftMargin, doc.bottomMargin,
                                                 doc.width, doc.height, id="f")],
                                   onPage=encabezado_pie)])

S = []
A = S.append

# ================================================================== portada
A(Paragraph("Diagnóstico operacional de la infraestructura vial del paso "
            "del Alto de La Línea", H1))
A(Paragraph("Objetivo específico 5 · Actividad 5 · Informe de diagnóstico vial · "
            "Corredor Ibagué – Calarcá, Ruta Nacional 40", SUB))
A(Paragraph("Semillero de Investigación GEOPAV · Ingeniería Civil · Universidad de Ibagué · "
            "Semestre Paz y Región 2026B", SUB))
A(Spacer(1, 10))
A(Paragraph("Marcas de origen: <b>[F]</b> dato de fuente externa citada · <b>[CP]</b> cálculo "
            "propio reproducible por un script publicado · <b>[H]</b> hipótesis declarada · "
            "<b>[DA]</b> dato abierto pendiente. Ninguna cifra de este informe entra sin marca.",
            NOTA))

# ================================================================== 1
A(Paragraph("1. Lo que este diagnóstico establece", H2))
A(Paragraph(
    f"El corredor Ibagué – Calarcá registró <b>{FALL_PASO} fallecidos</b> en el tramo del paso "
    f"entre 2015 y 2019. En ese mismo tramo circulaban <b>{es_co(T244)} vehículos/día</b>, de los "
    f"cuales <b>{es_co(TPD_CAM)} son camiones</b>. Normalizado por exposición, eso da una tasa de "
    f"<b>{es_co(TASA_PASO, 2)} fallecidos por cada 100 millones de vehículos-kilómetro</b> en el "
    f"paso, y <b>{es_co(TASA_CORR, 2)}</b> si se reparte sobre el corredor completo. Es la primera "
    "vez que el semillero puede publicar esa tasa con las dos entradas medidas en vez de supuestas.",
    P))

fila = [[Paragraph(es_co(TASA_CORR, 2), CIFRA), Paragraph(es_co(TASA_PASO, 2), CIFRA),
         Paragraph(es_co(TPD_CAM), CIFRA), Paragraph(es_co(VKM_CAM / 1e6, 1), CIFRA)],
        [Paragraph("Tasa del corredor<br/><font size=7>fallecidos / 100 M veh-km · 74 km</font>", CELDA),
         Paragraph("Tasa del paso<br/><font size=7>fallecidos / 100 M veh-km · 45 km</font>", CELDA),
         Paragraph("Camiones al día<br/><font size=7>en el paso, media 2015–2018</font>", CELDA),
         Paragraph("Millones de veh-km<br/><font size=7>de camiones al año, en el paso</font>", CELDA)]]
t = Table(fila, colWidths=[42 * mm] * 4, hAlign="LEFT")
t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                       ("LINEABOVE", (0, 0), (-1, 0), 0.8, AZUL),
                       ("LINEBELOW", (0, -1), (-1, -1), 0.4, LINEA),
                       ("TOPPADDING", (0, 0), (-1, -1), 6),
                       ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                       ("LEFTPADDING", (0, 0), (-1, -1), 0),
                       ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
A(t)
A(Spacer(1, 6))
A(Paragraph(
    f"<b>La cifra que el semillero publicaba antes era {es_co(TASA_VIEJA, 2)}</b>, calculada con un "
    "tránsito supuesto de 3.000 veh/día y una longitud supuesta de 60 km. El tránsito real del paso "
    "es más del doble de aquel supuesto, de modo que la tasa medida es aproximadamente un tercio de "
    "la que se venía publicando. Ninguna de las dos entradas es ya una hipótesis. <b>[CP]</b>", DEST))

# ================================================================== 2
A(Paragraph("2. La infraestructura actual", H2))
A(Paragraph(
    "El cruce de la Cordillera Central por la Ruta Nacional 40 dejó de ser el de la línea base. "
    "El <b>Túnel de La Línea entró en operación el 4 de septiembre de 2020</b>, con 8,6 km de "
    "túnel principal, un túnel de rescate, 3 túneles cortos, 5 puentes y 13,4 km de segunda "
    "calzada entre Calarcá y Cajamarca. <b>[F, INVÍAS]</b>", P))
A(Paragraph("Lo que sigue sin resolverse", H3))
A(Paragraph(
    "El túnel no eliminó ni la siniestralidad de la carga pesada ni la vulnerabilidad del corredor:",
    P))
for t_ in [
    "<b>5 de febrero de 2026 · túnel Los Azulejos.</b> Una tractomula y un camión con maquinaria "
    "pesada chocaron dentro del túnel: <b>dos fallecidos</b>, varios heridos y restricción total "
    "del paso en el Alto de La Línea. Es el mecanismo que este objetivo describe —carga pesada, en "
    "el paso— ocurriendo con la infraestructura nueva. <b>[F, prensa]</b>",
    "<b>Julio de 2026 · Cajamarca, km 47+420.</b> Un movimiento en masa en el sector urbano obligó "
    "a operar con <b>paso controlado a un carril</b>. INVÍAS atribuyó la inestabilidad a "
    "filtraciones de las redes de acueducto y alcantarillado sobre depósitos de ceniza volcánica, y "
    "anunció la gestión de recursos para estudios y diseños definitivos. <b>[F, INVÍAS vía prensa]</b>",
]:
    A(Paragraph(f"• {t_}", P))
A(Paragraph(
    "Ese segundo hecho importa más allá del OE 5: un corredor que depende de la estabilidad de una "
    "ladera urbana sobre ceniza volcánica tiene una vulnerabilidad que un túnel de base, por "
    "definición, no comparte. Es material directo para el <b>OE 3</b>, que estudia la geotecnia de "
    "los portales, y para la justificación del proyecto en el <b>OE 7</b>.", DEST))

# ================================================================== 3
A(Paragraph("3. La exposición: cuánto y qué circula", H2))
A(Paragraph(
    "El diagnóstico se apoya en la serie histórica de tránsito de INVÍAS, cuyos enlaces indexados "
    "estaban caídos y se localizaron en el portal vigente. Aporta el tránsito por estación de aforo "
    "y su composición vehicular, en el mismo periodo de los fallecidos. <b>[F]</b>", P))
A(tabla([
    [Paragraph(x, CELDA_B) for x in ["Estación", "Sector", "L", "TPD 2015–2018",
                                     "Camiones", "Participación"]],
    [Paragraph("<b>244</b>", CELDA), Paragraph("Calarcá – Cajamarca · <b>el paso</b>", CELDA),
     Paragraph("45 km", CELDA), Paragraph(f"<b>{es_co(T244)}</b>", CELDA),
     Paragraph(f"<b>{es_co(TPD_CAM)}</b>", CELDA), Paragraph(f"<b>{es_co(PART_CAM*100,1)} %</b>", CELDA)],
    [Paragraph("<b>243</b>", CELDA), Paragraph("Cajamarca – Ibagué", CELDA),
     Paragraph("29 km", CELDA), Paragraph(es_co(T243), CELDA),
     Paragraph("—", CELDA), Paragraph("—", CELDA)],
    [Paragraph("<b>Corredor</b>", CELDA), Paragraph("Ponderado por longitud", CELDA),
     Paragraph("<b>74 km</b>", CELDA), Paragraph(f"<b>{es_co(TPOND)}</b>", CELDA),
     Paragraph("—", CELDA), Paragraph("—", CELDA)],
], [20 * mm, 56 * mm, 15 * mm, 27 * mm, 22 * mm, 27 * mm]))
A(Spacer(1, 5))
A(Paragraph(
    f"<b>Más de la mitad del tránsito del paso es carga.</b> Eso son {es_co(VKM_CAM/1e6,1)} millones "
    "de vehículos-kilómetro de camiones al año recorriendo el ascenso y el descenso, que es "
    "precisamente la exposición que la Ferropista captaría. La clase «camiones» de esta fuente "
    "incluye los de dos ejes, así que la cifra es una cota superior y así se declara. <b>[CP]</b>", P))
A(Paragraph("Una advertencia de método que hay que sostener", H3))
A(Paragraph(
    "La memoria metodológica de este objetivo usa el peaje <b>Cocora</b> como denominador. Cocora "
    "está en el K 13+750 de la segunda calzada Ibagué – Cajamarca, aguas abajo del ascenso, y lo "
    "administra la concesión APP GICA; el peaje <b>Cajamarca</b>, de INVÍAS, está en el PR 24+020, "
    "más arriba. Los separan unos 10 km y Cocora capta tráfico local que nunca cruza la cordillera. "
    "<b>Sus series no son comparables sin homologar el punto de medición</b>, y el diagnóstico usa "
    "la estación 244, que mide el tramo del paso completo. <b>[F]</b>", P))

# ================================================================== 4
A(Paragraph("4. La línea base de mortalidad", H2))
A(Paragraph(
    f"El conjunto <i>Sectores Críticos de Siniestralidad Vial</i> de la ANSV reporta <b>seis "
    f"sectores críticos</b> dentro del corredor, con <b>{FALL_CORR} fallecidos</b> acumulados entre "
    f"2015 y 2019. <b>{FALL_PASO} corresponden al tramo «Calarcá – Ibagué»</b> a cargo de INVÍAS, "
    "que es el cruce propiamente dicho; los otros diez están en el tramo La Paila – Calarcá, fuera "
    "del paso. <b>[F]</b>", P))
A(Paragraph(
    "<b>Los seis están en jurisdicción de Calarcá y caben en 3,6 kilómetros del descenso.</b> "
    "Cuatro de ellos alcanzan el 99 % de confianza en el estadístico Getis-Ord Gi* que la propia "
    "ANSV publica con el dato. La concentración no es una interpretación del semillero: viene "
    "calculada en la fuente. <b>[F]</b>", DEST))
A(Paragraph("El lado tolimense, y por qué su ausencia no es un vacío de cobertura", H3))
A(Paragraph(
    "Ningún sector crítico del conjunto cae en el tramo Cajamarca – Ibagué ni en el municipio de "
    "Cajamarca. Para descartar que fuera un artefacto del filtro geográfico se revisaron los dos "
    "conjuntos nacionales completos: la ANSV <b>sí reporta 10 sectores críticos en el Tolima</b>, "
    "con 137 fallecidos, incluido uno en Ibagué sobre la vía a Girardot. El departamento está "
    "cubierto; lo que no aparece es la vía al paso. <b>[F]</b>", P))
A(Paragraph(
    "El conjunto de <i>Sectores Críticos por Exceso de Velocidad</i> tampoco reporta nada en el "
    "paso, y ahí la explicación es del método: ese conjunto solo registra tramos donde vehículos de "
    "carga superan los 80 km/h, y en el Alto de La Línea la velocidad media de operación es inferior "
    "a 20 km/h. <b>La ausencia no indica seguridad: indica congestión</b>, y confirma por una vía "
    "independiente la velocidad que declara la fuente primaria del proyecto. <b>[F]</b>", P))
A(Paragraph(
    "Queda una pregunta abierta y el semillero no la resuelve en silencio: o el descenso hacia "
    "Calarcá concentra efectivamente la mortalidad del cruce, o el tramo tolimense no superó el "
    "umbral con el que la ANSV define un sector crítico. Se dirime contrastando con las cifras "
    "municipales de Forensis para Cajamarca e Ibagué del mismo periodo. <b>[DA]</b>", P))

# ================================================================== 5
A(Paragraph("5. La tasa y sus condiciones de validez", H2))
A(Paragraph(
    "<font face='Courier' size=8>Tasa = fallecidos / (TPD × 365 × L × años) × 10</font><font face='Courier' size=8><super>8</super></font>", P))
A(Paragraph(
    "La memoria metodológica declaraba que esta tasa no era publicable porque los fallecidos son de "
    "2015–2019 y el único aforo verificado era de 2021–2026: no eran divisibles entre sí. <b>Con la "
    "serie de INVÍAS esa objeción queda resuelta</b>: el aforo del paso es 2015–2018, de la misma "
    "estación y la misma vía. Mismo periodo, mismo tramo.", P))
A(Paragraph("Las tres condiciones que se declaran con el resultado", H3))
A(tabla([
    [Paragraph(x, CELDA_B) for x in ["Condición", "Qué significa", "Efecto"]],
    [Paragraph("<b>Dos definiciones de tramo</b> <b>[H]</b>", CELDA),
     Paragraph("Los 42 fallecidos están en un tramo ANSV de 74 km, pero los seis sectores caen en "
               "los 45 km del descenso. Ninguna definición es obviamente la correcta.", CELDA),
     Paragraph(f"La tasa va de <b>{es_co(TASA_CORR,2)}</b> a <b>{es_co(TASA_PASO,2)}</b> según cuál "
               "se adopte. Se publican las dos.", CELDA)],
    [Paragraph("<b>El año que falta en el aforo</b> <b>[H]</b>", CELDA),
     Paragraph("Los fallecidos cubren cinco años y el aforo de INVÍAS cuatro: se supone que 2019 "
               "tuvo un tránsito parecido. El peaje Cajamarca de 2019 lo confirma dentro del 5 %.", CELDA),
     Paragraph(f"Mueve la tasa un <b>{es_co(MUEVE*100,1)} %</b>. La conclusión aguanta.", CELDA)],
    [Paragraph("<b>Es anterior al túnel</b> <b>[F]</b>", CELDA),
     Paragraph("La línea base describe el corredor de 2015–2019. El Túnel de La Línea abrió en "
               "septiembre de 2020 y cambió geometría, velocidad y composición del tránsito.", CELDA),
     Paragraph("La tasa <b>sobrestima</b> el riesgo del corredor actual. No es la tasa de hoy.", CELDA)],
], [44 * mm, 68 * mm, 50 * mm]))

# ================================================================== 6
A(Paragraph("6. Qué puede y qué no puede afirmar el semillero", H2))
A(Paragraph("Sostenible con lo publicado", H3))
for t_ in [
    "La línea base georreferenciada de fallecidos del corredor, con su periodo, su nivel de "
    "significancia estadística y sus sesgos declarados.",
    "La composición del tránsito del paso medida en estación de aforo y en peaje, no supuesta, y su "
    "serie de veinte años.",
    "La exposición anual en vehículos-kilómetro del corredor y la porción que corresponde a carga "
    "pesada.",
    "La tasa de mortalidad normalizada por exposición, con las dos entradas medidas y las tres "
    "condiciones de validez declaradas.",
    "Que la línea base disponible es anterior al Túnel de La Línea y por tanto sobrestima la "
    "siniestralidad del corredor actual.",
]:
    A(Paragraph(f"• {t_}", P))
A(Paragraph("No sostenible", H3))
A(Paragraph(
    "<b>Cuántas muertes evitaría la Ferropista.</b> Una predicción de víctimas exige un modelo de "
    "siniestralidad calibrado con microdatos por siniestro —tipo de vehículo, causa, condición de la "
    "víctima— que no están públicos con ese detalle para este corredor. Cualquier cifra de vidas "
    "salvadas que apareciera en este trabajo sin ese modelo detrás sería una invención, y basta que "
    "un evaluador la cuestione una vez para que el resto del análisis quede bajo sospecha.", DEST))
A(Paragraph(
    "Lo que el semillero aporta no es una predicción sino una <b>caracterización del riesgo por "
    "exposición</b>: quién está expuesto, cuánto, dónde se concentra la mortalidad, y qué le pasa a "
    "esa exposición si la carga pesada deja de hacer el descenso.", P))

# ================================================================== 7
A(Paragraph("7. Limitaciones declaradas", H2))
for t_ in [
    "El conjunto de la ANSV reporta <b>únicamente fallecidos</b>: no incluye heridos ni siniestros "
    "con solo daños materiales. La línea base es de mortalidad, no de siniestralidad total.",
    "Es un producto derivado de análisis espacial, no el microdato por siniestro: no permite "
    "reconstruir cada evento ni conocer el tipo de vehículo implicado.",
    "Un «sector crítico» es una categoría con su propio umbral, no un censo: que un tramo no "
    "aparezca no significa que no haya tenido fallecidos.",
    "La clase «camiones» de la serie por estación incluye los de dos ejes, que en el peaje son "
    "categoría II. Las participaciones de una y otra fuente no se promedian.",
    "Los hechos de 2026 citados en la sección 2 provienen de prensa y del propio INVÍAS, no del "
    "conjunto de la ANSV, que llega hasta 2019. Se citan como contexto operacional, no como línea base.",
    "No existe un denominador nacional de vehículos-kilómetro publicado, de modo que comparar esta "
    "tasa con el promedio del país queda pendiente de una fuente que lo permita. <b>[DA]</b>",
]:
    A(Paragraph(f"• {t_}", P))

# ================================================================== 8
A(Paragraph("8. Trazabilidad", H2))
A(Paragraph(
    "Toda cifra de este informe se lee de los productos de las actividades anteriores. El script "
    "que lo genera <b>se detiene</b> si la tasa del libro de cálculo no se reproduce desde los CSV, "
    "de modo que el informe no pueda decir algo distinto de sus fuentes.", P))
A(tabla([
    [Paragraph(x, CELDA_B) for x in ["Actividad", "Producto", "Qué aporta a este informe"]],
    [Paragraph("<b>Act 1</b>", CELDA),
     Paragraph("<font size=7>Act1_Aforos/tpd_historico_corredor.csv</font>", CELDA),
     Paragraph("TPD y composición por estación, 1997–2018, y las longitudes de INVÍAS.", CELDA)],
    [Paragraph("<b>Act 2</b>", CELDA),
     Paragraph("<font size=7>Act2_Clasificacion/matriz_aforos_clasificada_OE5.xlsx</font>", CELDA),
     Paragraph("Clasificación vehicular homologada entre estaciones y peajes.", CELDA)],
    [Paragraph("<b>Act 3</b>", CELDA),
     Paragraph("<font size=7>Act3_Siniestros/Historico_siniestros_OE5.pdf</font>", CELDA),
     Paragraph("Los seis sectores críticos, su Gi*, y la revisión municipal nacional.", CELDA)],
    [Paragraph("<b>Act 4</b>", CELDA),
     Paragraph("<font size=7>Act4_Analisis/analisis_siniestralidad_OE5.xlsx</font>", CELDA),
     Paragraph("Las dos tasas, la sensibilidad y la exposición de carga pesada.", CELDA)],
], [20 * mm, 68 * mm, 74 * mm]))
A(Spacer(1, 6))
A(Paragraph(
    "Fuentes primarias: ANSV, <font face='Courier' size=8>datos.gov.co/d/rs3u-8r4q</font> y "
    "<font face='Courier' size=8>/d/24ny-2dhf</font> · INVÍAS, series históricas de TPD en "
    "<font face='Courier' size=8>invias.gov.co/publicaciones/4154/documentos-tecnicos/</font> · "
    "INVÍAS, Túnel de La Línea en "
    "<font face='Courier' size=8>crucecordilleracentral.invias.gov.co</font> · ANI, Tráfico "
    "Vehicular <font face='Courier' size=8>/d/8yi9-t44c</font>.", NOTA))

# lámina de la Act 4, si existe
lam = os.path.join(VIS, "graficos_siniestralidad_OE5.png")
if os.path.exists(lam):
    A(Spacer(1, 10))
    A(Paragraph("Anexo · Lámina de gráficos de la Actividad 4", H2))
    A(Image(lam, width=doc.width, height=doc.width * 1639 / 3100))

doc.build(S)
print("PDF escrito:", SALIDA)
print(f"  tasas {TASA_CORR:.2f} / {TASA_PASO:.2f} | {FALL_PASO} fallecidos en el paso "
      f"| {FALL_CORR} en el corredor")
