# -*- coding: utf-8 -*-
"""
OE 5 - Actividad 5 (fila 35 del Cronograma)
Consolidacion del diagnostico operacional de la infraestructura vial actual.
Producto: Informe_diagnostico_vial_OE5_v2.pdf

REVISION 2 (16 sep 2026): presentacion corregida segun el tutor. Portada, tabla de
contenido, indices de tablas, figuras y anexos, logo de la Universidad en el encabezado,
titulo y fuente en cada tabla, verde GEOPAV como color principal y azul como secundario.
El contenido y los controles de las cifras no cambian. Ver
ferropista/estandar-presentacion-documentos.md.

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
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, Image, KeepTogether,
                                NextPageTemplate, PageBreak, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

BASE = os.path.dirname(os.path.abspath(__file__))
OE5 = os.path.dirname(BASE)
ACT1 = os.path.join(OE5, "Act1_Aforos")
ACT3 = os.path.join(OE5, "Act3_Siniestros")
ACT4 = os.path.join(OE5, "Act4_Analisis")
VIS = os.path.join(OE5, "Visuales")
SALIDA = os.path.join(BASE, "Informe_diagnostico_vial_OE5_v2.pdf")
RAIZ = os.path.dirname(OE5)
LOGO_U = os.path.join(RAIZ, "public", "logo-unibague.png")
LOGO_G = os.path.join(RAIZ, "public", "logo-geopav.png")

VERDE = colors.HexColor("#178E2C")   # principal: logo del semillero GEOPAV
AZUL = colors.HexColor("#193F77")    # secundario: Universidad de Ibagué
FONDO = colors.HexColor("#F1F7F2")
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

# ------------------------------------------------------------------ fuentes
def _registrar_fuente():
    """Carlito (Linux) o Calibri (Windows), que comparten métricas. Si no hay ninguna, Helvetica."""
    candidatos = [
        ("/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf", "/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf",
         "/usr/share/fonts/truetype/crosextra/Carlito-Italic.ttf", "/usr/share/fonts/truetype/crosextra/Carlito-BoldItalic.ttf"),
        (r"C:\Windows\Fonts\calibri.ttf", r"C:\Windows\Fonts\calibrib.ttf",
         r"C:\Windows\Fonts\calibrii.ttf", r"C:\Windows\Fonts\calibriz.ttf"),
    ]
    for reg, neg, cur, nc in candidatos:
        if all(os.path.exists(x) for x in (reg, neg, cur, nc)):
            pdfmetrics.registerFont(TTFont("Txt", reg)); pdfmetrics.registerFont(TTFont("Txt-B", neg))
            pdfmetrics.registerFont(TTFont("Txt-I", cur)); pdfmetrics.registerFont(TTFont("Txt-BI", nc))
            registerFontFamily("Txt", normal="Txt", bold="Txt-B", italic="Txt-I", boldItalic="Txt-BI")
            return "Txt", "Txt-B", "Txt-I"
    return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"


F_REG, F_BOLD, F_ITAL = _registrar_fuente()

# ------------------------------------------------------------------ estilos
ss = getSampleStyleSheet()
P = ParagraphStyle("P", parent=ss["Normal"], fontName=F_REG, fontSize=11, leading=16.5,
                   alignment=TA_JUSTIFY, spaceAfter=9, textColor=colors.HexColor("#1F2933"))
H1 = ParagraphStyle("H1x", parent=ss["Heading1"], fontName=F_BOLD, fontSize=17, leading=22,
                    textColor=VERDE, spaceBefore=6, spaceAfter=12)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName=F_BOLD, fontSize=16, leading=21,
                    textColor=VERDE, spaceBefore=16, spaceAfter=10, keepWithNext=1)
H3 = ParagraphStyle("H3", parent=ss["Heading3"], fontName=F_BOLD, fontSize=12.5, leading=17,
                    textColor=AZUL, spaceBefore=12, spaceAfter=6, keepWithNext=1)
SUB = ParagraphStyle("SUB", parent=P, fontSize=10.5, textColor=GRIS, spaceAfter=4)
NOTA = ParagraphStyle("NOTA", parent=P, fontSize=9.5, leading=13.5, textColor=GRIS)
CELDA = ParagraphStyle("CELDA", parent=P, fontSize=9.5, leading=13, alignment=0, spaceAfter=0)
CELDA_B = ParagraphStyle("CELDA_B", parent=CELDA, fontName=F_BOLD, textColor=colors.white)
DEST = ParagraphStyle("DEST", parent=P, leftIndent=10, rightIndent=10, spaceBefore=8,
                      spaceAfter=12, borderPadding=9, backColor=FONDO, borderColor=VERDE,
                      borderWidth=0.6)
CIFRA = ParagraphStyle("CIFRA", parent=P, fontName=F_BOLD, fontSize=21, leading=24,
                       textColor=AZUL, alignment=0, spaceAfter=1)
TIT_TABLA = ParagraphStyle("TIT_TABLA", parent=P, fontName=F_BOLD, fontSize=10.5, leading=14,
                           textColor=AZUL, alignment=0, spaceBefore=8, spaceAfter=5, keepWithNext=1)
FUENTE = ParagraphStyle("FUENTE", parent=P, fontName=F_ITAL, fontSize=9, leading=12,
                        textColor=GRIS, alignment=0, spaceBefore=4, spaceAfter=12)
TOC1 = ParagraphStyle("TOC1", parent=P, fontSize=11, leading=19, alignment=0, spaceAfter=0)
TOC2 = ParagraphStyle("TOC2", parent=TOC1, leftIndent=18, textColor=GRIS)
IDX = ParagraphStyle("IDX", parent=P, fontSize=10.5, leading=16, alignment=0, spaceAfter=0)

LETRA = letter
MARGEN = 23 * mm


def tabla(datos, anchos, cabecera=True):
    t = Table(datos, colWidths=anchos, repeatRows=1 if cabecera else 0, hAlign="LEFT")
    est = [("GRID", (0, 0), (-1, -1), 0.4, LINEA),
           ("VALIGN", (0, 0), (-1, -1), "TOP"),
           ("TOPPADDING", (0, 0), (-1, -1), 4.5),
           ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
           ("LEFTPADDING", (0, 0), (-1, -1), 5),
           ("RIGHTPADDING", (0, 0), (-1, -1), 5)]
    if cabecera:
        est += [("BACKGROUND", (0, 0), (-1, 0), AZUL),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)]
        for i in range(2, len(datos), 2):
            est.append(("BACKGROUND", (0, i), (-1, i), FONDO))
    t.setStyle(TableStyle(est))
    return t


class Marca(Flowable):
    """Registra una entrada de índice (T tabla, F figura, A anexo) con su página."""
    def __init__(self, tipo, texto):
        super().__init__(); self.tipo = tipo; self.texto = texto
    def wrap(self, *a):
        return (0, 0)
    def draw(self):
        self.canv._doctemplate.idx[self.tipo].append((self.texto, self.canv.getPageNumber()))


class Indice(Flowable):
    """Índice con número de página, resuelto con la pasada anterior (ver construir())."""
    def __init__(self, doc, tipo, vacio):
        super().__init__(); self.doc = doc; self.tipo = tipo; self.vacio = vacio
    def wrap(self, aw, ah):
        filas = self.doc.semilla[self.tipo] or [(self.vacio, "")]
        der = ParagraphStyle("der", parent=IDX, alignment=2)
        self.t = Table([[Paragraph(a, IDX), Paragraph(str(b), der)] for a, b in filas],
                       colWidths=[aw - 15 * mm, 15 * mm])
        self.t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.3, LINEA),
                                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM")]))
        return self.t.wrap(aw, ah)
    def draw(self):
        self.t.drawOn(self.canv, 0, 0)


CONT = {"T": 0, "F": 0, "A": 0}


class TituloIndexado(Paragraph):
    """Título que registra su propia página: así conserva keepWithNext con lo que titula."""
    def __init__(self, texto, estilo, tipo):
        super().__init__(texto, estilo); self._tipo = tipo; self._texto = texto
    def draw(self):
        self.canv._doctemplate.idx[self._tipo].append((self._texto, self.canv.getPageNumber()))
        super().draw()


def titulo_tabla(texto, lista):
    CONT["T"] += 1
    t = f"Tabla {CONT['T']}. {texto}"
    lista.append(TituloIndexado(t, TIT_TABLA, "T"))


def fuente(texto):
    return Paragraph("Fuente: " + texto, FUENTE)


class Doc(BaseDocTemplate):
    def handle_documentBegin(self):
        self.idx = {"T": [], "F": [], "A": []}
        super().handle_documentBegin()

    def afterFlowable(self, f):
        if isinstance(f, Paragraph) and f.style.name in ("H2", "H3"):
            nivel = 0 if f.style.name == "H2" else 1
            clave = "h%d" % id(f)
            self.canv.bookmarkPage(clave)
            self.notify("TOCEntry", (nivel, f.getPlainText(), self.page, clave))


def portada(canv, doc):
    W, H = LETRA
    canv.saveState()
    canv.setFillColor(VERDE); canv.rect(0, H - 9 * mm, W, 9 * mm, stroke=0, fill=1)
    canv.setFillColor(AZUL); canv.rect(0, H - 11.5 * mm, W, 2.5 * mm, stroke=0, fill=1)
    if os.path.exists(LOGO_U):
        canv.drawImage(LOGO_U, MARGEN, H - 46 * mm, width=82 * mm, height=82 * mm * 179 / 669, mask="auto")
    if os.path.exists(LOGO_G):
        canv.drawImage(LOGO_G, W - MARGEN - 26 * mm, H - 48.5 * mm, width=26 * mm, height=26 * mm, mask="auto")
    canv.setFillColor(GRIS); canv.setFont(F_BOLD, 11)
    canv.drawString(MARGEN, H - 63 * mm, "SEMESTRE PAZ Y REGIÓN 2026B · SEMILLERO DE INVESTIGACIÓN GEOPAV")
    canv.setStrokeColor(VERDE); canv.setLineWidth(2); canv.line(MARGEN, H - 67 * mm, W - MARGEN, H - 67 * mm)
    canv.setFillColor(VERDE); canv.setFont(F_BOLD, 13)
    canv.drawString(MARGEN, H - 82 * mm, "OE 5 · Actividad 5 · Producto")
    tit = Paragraph("Informe de diagnóstico operacional de la infraestructura vial del paso del Alto de La Línea",
                    ParagraphStyle("pt", fontName=F_BOLD, fontSize=26, leading=32, textColor=AZUL))
    w, h = tit.wrap(W - 2 * MARGEN, 100 * mm); tit.drawOn(canv, MARGEN, H - 88 * mm - h)
    sub = Paragraph("Corredor Ibagué – Calarcá, Ruta Nacional 40 · Revisión 2",
                    ParagraphStyle("ps", fontName=F_REG, fontSize=14, leading=19, textColor=GRIS))
    w2, h2 = sub.wrap(W - 2 * MARGEN, 30 * mm); sub.drawOn(canv, MARGEN, H - 96 * mm - h - h2)
    ficha = [("Objetivo específico", "OE 5 — Diagnóstico vial: tránsito y siniestralidad del paso de La Línea"),
             ("Actividad", "Act 5. Consolidación del diagnóstico operacional de la infraestructura vial actual"),
             ("Entregable / formato", "Informe de diagnóstico vial · Documento PDF"),
             ("Periodo en el Plan de Acción", "29 sep 2026 – 3 oct 2026"),
             ("Responsable asignado", "Castaño Cifuentes Maicol Stiven"),
             ("Revisión", "2 · corrección de presentación solicitada por el tutor")]
    t = Table([[Paragraph(f"<b>{k}</b>", CELDA), Paragraph(v, CELDA)] for k, v in ficha],
              colWidths=[52 * mm, W - 2 * MARGEN - 52 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), FONDO), ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINEA),
                           ("LINEABOVE", (0, 0), (-1, 0), 1, VERDE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    t.wrap(W - 2 * MARGEN, 100 * mm); t.drawOn(canv, MARGEN, 36 * mm)
    canv.setFont(F_REG, 10); canv.setFillColor(GRIS)
    canv.drawString(MARGEN, 22 * mm, "Programa de Ingeniería Civil · Universidad de Ibagué · Ibagué, Tolima")
    canv.drawRightString(W - MARGEN, 22 * mm, "Septiembre de 2026")
    canv.restoreState()


def encabezado_pie(canv, doc):
    W, H = LETRA
    canv.saveState()
    if os.path.exists(LOGO_U):
        canv.drawImage(LOGO_U, MARGEN, H - 22.5 * mm, width=44 * mm, height=44 * mm * 179 / 669, mask="auto")
    if os.path.exists(LOGO_G):
        canv.drawImage(LOGO_G, W - MARGEN - 12.5 * mm, H - 24 * mm, width=12.5 * mm, height=12.5 * mm, mask="auto")
    canv.setFont(F_REG, 9); canv.setFillColor(GRIS)
    canv.drawRightString(W - MARGEN - 15.5 * mm, H - 17.5 * mm, "OE 5 · Actividad 5 · Producto")
    canv.setStrokeColor(VERDE); canv.setLineWidth(1.2); canv.line(MARGEN, H - 26 * mm, W - MARGEN, H - 26 * mm)
    canv.setStrokeColor(LINEA); canv.setLineWidth(0.6); canv.line(MARGEN, 18 * mm, W - MARGEN, 18 * mm)
    canv.drawString(MARGEN, 13 * mm, "Semillero GEOPAV · Ferropista Cordillera Central · OE 5 – Act 5")
    canv.drawRightString(W - MARGEN, 13 * mm, f"Página {doc.page}")
    canv.restoreState()


def construir_documento(cuerpo_fn):
    """Repite la construcción hasta que los índices de tablas, figuras y anexos se estabilizan."""
    previo = {"T": [], "F": [], "A": []}
    for _ in range(4):
        CONT.update({"T": 0, "F": 0, "A": 0})
        doc = Doc(SALIDA, pagesize=LETRA, leftMargin=MARGEN, rightMargin=MARGEN,
                  topMargin=32 * mm, bottomMargin=25 * mm,
                  title="Informe de diagnóstico vial - OE 5 Act 5 - Semillero GEOPAV (rev. 2)",
                  author="Semillero de Investigación GEOPAV - Universidad de Ibagué", invariant=1)
        doc.semilla = previo
        fr = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
        doc.addPageTemplates([PageTemplate(id="portada", frames=[fr], onPage=portada),
                              PageTemplate(id="p", frames=[fr], onPage=encabezado_pie)])
        toc = TableOfContents(); toc.levelStyles = [TOC1, TOC2]
        pre = [NextPageTemplate("p"), PageBreak(),
               Paragraph("Tabla de contenido", H1), toc, PageBreak(),
               Paragraph("Índice de tablas", H1), Indice(doc, "T", "Este documento no contiene tablas."), Spacer(1, 16),
               Paragraph("Índice de figuras", H1), Indice(doc, "F", "Este documento no contiene figuras."), Spacer(1, 16),
               Paragraph("Índice de anexos", H1), Indice(doc, "A", "Este documento no contiene anexos."), PageBreak()]
        doc.multiBuild(pre + cuerpo_fn(doc))
        if doc.idx == previo:
            return doc
        previo = doc.idx
    return doc


def cuerpo(doc):
    S = []
    A = S.append
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
    titulo_tabla("Cifras principales del diagnóstico", S)
    t = Table(fila, colWidths=[42 * mm] * 4, hAlign="LEFT")
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("LINEABOVE", (0, 0), (-1, 0), 0.8, AZUL),
                           ("LINEBELOW", (0, -1), (-1, -1), 0.4, LINEA),
                           ("TOPPADDING", (0, 0), (-1, -1), 6),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
    A(t)
    A(fuente("Act4_Analisis/analisis_siniestralidad_OE5.xlsx, hojas «3. Tasa» y «5. Carga pesada» [CP]."))
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
    titulo_tabla("Tránsito y composición por estación de aforo, 2015–2018", S)
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
    A(fuente("INVÍAS, serie histórica de TPD (Act1_Aforos/tpd_historico_corredor.csv) [F]; ponderación por longitud [CP]."))
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
    titulo_tabla("Condiciones de validez de la tasa de mortalidad", S)
    A(tabla([
        [Paragraph(x, CELDA_B) for x in ["Condición", "Qué significa", "Efecto"]],
        [Paragraph("<b>Dos definiciones de tramo</b> <b>[H]</b>", CELDA),
         Paragraph("Los 42 fallecidos están en un tramo ANSV de 74 km, pero los cuatro sectores que los "
                   "aportan caen en los 45 km del descenso. Ninguna definición es obviamente la correcta.", CELDA),
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
    A(fuente("Act4_Analisis/analisis_siniestralidad_OE5.xlsx y memoria metodológica del OE 5 (revisión 2)."))

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
    titulo_tabla("Productos de las actividades 1 a 4 que respaldan este informe", S)
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
    A(fuente("carpetas OE5_SeguridadVial/Act1_Aforos a Act4_Analisis del repositorio del proyecto."))
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
        A(PageBreak())
        A(Marca("A", "Anexo A. Lámina de gráficos de la Actividad 4"))
        A(Paragraph("Anexo A. Lámina de gráficos de la Actividad 4", H2))
        CONT["F"] += 1
        tf = f"Figura {CONT['F']}. Exposición y siniestralidad del corredor, lámina de la Actividad 4"
        A(Marca("F", tf))
        A(Paragraph(tf, ParagraphStyle("TF", parent=TIT_TABLA, alignment=1)))
        A(Image(lam, width=doc.width, height=doc.width * 1639 / 3100))
        A(Paragraph("Fuente: OE5_SeguridadVial/Visuales/graficos_siniestralidad_OE5.png, generada por "
                    "Act4_Analisis/graficos_siniestralidad_OE5.py [CP].", ParagraphStyle("FF", parent=FUENTE, alignment=1)))
    A(Spacer(1, 14))
    A(Paragraph("<i>Nota de elaboración: la revisión 2 de este informe corrige su presentación con apoyo de un "
                "asistente de inteligencia artificial (Claude, de Anthropic). El contenido y los controles de las "
                "cifras son los de la revisión 1, y el semillero verificó el resultado.</i>", FUENTE))


    return S


doc = construir_documento(cuerpo)
print("PDF escrito:", SALIDA)
print(f"  tasas {TASA_CORR:.2f} / {TASA_PASO:.2f} | {FALL_PASO} fallecidos en el paso "
      f"| {FALL_CORR} en el corredor")
