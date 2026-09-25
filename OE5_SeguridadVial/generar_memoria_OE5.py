# -*- coding: utf-8 -*-
"""
OE 5 - Memoria metodologica de la cuantificacion de la siniestralidad vial.
Producto: Memoria_metodologica_OE5_siniestralidad_rev4.pdf

REVISION 4 (23 sep 2026): incorpora el microdato georreferenciado que la ANSV entrego por
solicitud (oficio 20265000140371). Las revisiones 1 a 3 no tenian script generador en el
repositorio; desde esta revision la memoria se genera con este script, que comparte el
formato de presentacion del informe de la Act 5 (ferropista/estandar-presentacion-documentos.md).

Semillero de Investigacion GEOPAV - Universidad de Ibague - Paz y Region 2026B

LEE, NO ESCRIBE CIFRAS A MANO
    Act 1  Act1_Aforos/tpd_historico_corredor.csv
    Act 2  Act2_Clasificacion/matriz_aforos_clasificada_OE5.xlsx  (hoja 5, con guardia de rotulo)
    Act 3  Act3_Siniestros/siniestros_ANSV_corredor.csv, microdato_ANSV_resumen.json, cruce_prensa_ANSV.csv
    Act 4  Act4_Analisis/analisis_siniestralidad_OE5.xlsx (guardia de rotulo), tasa_post_tunel_OE5.json
  Se detiene si las tasas del libro no se reproducen desde los CSV o la del JSON desde sus entradas.

DEPENDENCIA
  reportlab y openpyxl.
"""

import csv
import json
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
OE5 = BASE
ACT1 = os.path.join(OE5, "Act1_Aforos")
ACT3 = os.path.join(OE5, "Act3_Siniestros")
ACT4 = os.path.join(OE5, "Act4_Analisis")
VIS = os.path.join(OE5, "Visuales")
SALIDA = os.path.join(BASE, "Memoria_metodologica_OE5_siniestralidad_rev4.pdf")
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

# microdato ANSV georreferenciado por solicitud (oficio 20265000140371) y tasa posterior al túnel
with open(os.path.join(ACT3, "microdato_ANSV_resumen.json"), encoding="utf-8") as fh:
    microdato = json.load(fh)
with open(os.path.join(ACT4, "tasa_post_tunel_OE5.json"), encoding="utf-8") as fh:
    post_tunel = json.load(fh)

_ctrl_h1 = (post_tunel["fallecidos_paso_2021_2025"]
            / (post_tunel["tpd_H1_est244_media_2015_2018"] * 365 * post_tunel["L_km"] * post_tunel["anios"])
            * 1e8)
if abs(_ctrl_h1 - post_tunel["tasa_H1"]) > 0.01:
    raise SystemExit(f"PARADA: tasa_H1 recalculada ({_ctrl_h1:.2f}) no coincide con "
                     f"tasa_post_tunel_OE5.json ({post_tunel['tasa_H1']:.2f}).")
print(f"control OK: tasa_H1 posterior al túnel se reproduce desde el JSON ({_ctrl_h1:.2f})")

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
    canv.drawString(MARGEN, H - 82 * mm, "OE 5 · Memoria metodológica")
    tit = Paragraph("Memoria metodológica: cuantificación de la siniestralidad vial",
                    ParagraphStyle("pt", fontName=F_BOLD, fontSize=26, leading=32, textColor=AZUL))
    w, h = tit.wrap(W - 2 * MARGEN, 100 * mm); tit.drawOn(canv, MARGEN, H - 88 * mm - h)
    sub = Paragraph("Corredor de análisis Ibagué – Calarcá, Ruta Nacional 40 · Revisión 4",
                    ParagraphStyle("ps", fontName=F_REG, fontSize=14, leading=19, textColor=GRIS))
    w2, h2 = sub.wrap(W - 2 * MARGEN, 30 * mm); sub.drawOn(canv, MARGEN, H - 96 * mm - h - h2)
    ficha = [("Objetivo específico", "OE 5 — Volúmenes de tránsito de vehículos pesados e índices de siniestralidad del paso de La Línea"),
             ("Actividades que respalda", "Act 1 a Act 5"),
             ("Responsable asignado", "Castaño Cifuentes Maicol Stiven"),
             ("Revisión", "4 · incorpora el microdato ANSV 2021 – mar 2026 (oficio 20265000140371)")]
    t = Table([[Paragraph(f"<b>{k}</b>", CELDA), Paragraph(v, CELDA)] for k, v in ficha],
              colWidths=[52 * mm, W - 2 * MARGEN - 52 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), FONDO), ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINEA),
                           ("LINEABOVE", (0, 0), (-1, 0), 1, VERDE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    t.wrap(W - 2 * MARGEN, 100 * mm); t.drawOn(canv, MARGEN, 36 * mm)
    canv.setFont(F_REG, 10); canv.setFillColor(GRIS)
    canv.drawString(MARGEN, 22 * mm, "Programa de Ingeniería Civil · Universidad de Ibagué · Ibagué, Tolima")
    canv.drawRightString(W - MARGEN, 22 * mm, "23 de septiembre de 2026")
    canv.restoreState()


def encabezado_pie(canv, doc):
    W, H = LETRA
    canv.saveState()
    if os.path.exists(LOGO_U):
        canv.drawImage(LOGO_U, MARGEN, H - 22.5 * mm, width=44 * mm, height=44 * mm * 179 / 669, mask="auto")
    if os.path.exists(LOGO_G):
        canv.drawImage(LOGO_G, W - MARGEN - 12.5 * mm, H - 24 * mm, width=12.5 * mm, height=12.5 * mm, mask="auto")
    canv.setFont(F_REG, 9); canv.setFillColor(GRIS)
    canv.drawRightString(W - MARGEN - 15.5 * mm, H - 17.5 * mm, "OE 5 · Memoria metodológica")
    canv.setStrokeColor(VERDE); canv.setLineWidth(1.2); canv.line(MARGEN, H - 26 * mm, W - MARGEN, H - 26 * mm)
    canv.setStrokeColor(LINEA); canv.setLineWidth(0.6); canv.line(MARGEN, 18 * mm, W - MARGEN, 18 * mm)
    canv.drawString(MARGEN, 13 * mm, "Semillero GEOPAV · Ferropista Cordillera Central · OE 5 – Memoria metodológica")
    canv.drawRightString(W - MARGEN, 13 * mm, f"Página {doc.page}")
    canv.restoreState()


def construir_documento(cuerpo_fn):
    """Repite la construcción hasta que los índices de tablas, figuras y anexos se estabilizan."""
    previo = {"T": [], "F": [], "A": []}
    for _ in range(4):
        CONT.update({"T": 0, "F": 0, "A": 0})
        doc = Doc(SALIDA, pagesize=LETRA, leftMargin=MARGEN, rightMargin=MARGEN,
                  topMargin=32 * mm, bottomMargin=25 * mm,
                  title="Memoria metodológica - OE 5 - Semillero GEOPAV (rev. 4)",
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


# ------------------------------------------------------------------ insumos propios de la memoria
wbm = openpyxl.load_workbook(os.path.join(OE5, "Act2_Clasificacion", "matriz_aforos_clasificada_OE5.xlsx"), data_only=True)
wsm = wbm["5. Matriz consolidada"]
MATRIZ = []
for fila, esperado in ((5, "Estacion 244"), (6, "Estacion 243"), (7, "Peaje Cajamarca"), (8, "Peaje Cocora")):
    if esperado.lower() not in str(wsm.cell(row=fila, column=1).value or "").lower():
        raise SystemExit(f"PARADA: la matriz de la Act 2 cambió de estructura (fila {fila}, se esperaba «{esperado}»).")
    MATRIZ.append([wsm.cell(row=fila, column=c).value for c in (4, 5, 9)])
    if any(v is None for v in MATRIZ[-1]):
        raise SystemExit("PARADA: la matriz de la Act 2 no tiene valores cacheados.")
TASA_CTRL = celda(ws3, "G7", "Control")
TPD_CAJ19 = celda(ws3, "B22", "TPD del peaje Cajamarca en 2019")
TASA_ESC = celda(ws3, "B24", "Tasa del paso con ese escenario")
with open(os.path.join(ACT3, "cruce_prensa_ANSV.csv"), encoding="utf-8-sig") as fh:
    prensa = list(csv.DictReader(fh))
MD, PT = microdato, post_tunel
TR = MD["por_tramo"]
for clave in ("Armenia – Calarcá (fuera)", "Paso Calarcá – Cajamarca", "Cajamarca – Ibagué"):
    if clave not in TR:
        raise SystemExit(f"PARADA: microdato_ANSV_resumen.json no trae el tramo «{clave}».")
C = lambda t: Paragraph(t, CELDA)
CB = lambda t: Paragraph(t, CELDA_B)


def vinetas(lista, S):
    for t_ in lista:
        S.append(Paragraph(f"• {t_}", ParagraphStyle("V", parent=P, leftIndent=12, firstLineIndent=-8)))


def cuerpo(doc):
    S = []
    A = S.append
    # ================================================================== presentación
    A(Paragraph("Presentación del documento", H2))
    A(Paragraph("<b>Documento:</b> define el procedimiento con el que el semillero construye la línea base de "
                "siniestralidad del corredor, la normaliza por exposición y declara lo que puede y no puede "
                "concluirse a partir de ella.", P))
    A(Paragraph("<b>Estado de los datos:</b> las cifras de la línea base se descargaron y verificaron contra las "
                "fuentes entre el 2 y el 9 de septiembre de 2026. El microdato georreferenciado de la ANSV se "
                "recibió el 22 de septiembre de 2026 y se procesó el 23.", P))
    titulo_tabla("Historial de revisiones", S)
    A(tabla([[CB(x) for x in ["Revisión", "Fecha", "Qué cambió"]],
             [C("1"), C("2 sep 2026"), C("Versión inicial: concluía que la tasa no era publicable.")],
             [C("2"), C("9 sep 2026"), C("Tasa publicable con la serie histórica de INVÍAS. Ver sección 0.1.")],
             [C("3"), C("16 sep 2026"), C("Presentación corregida según el tutor. Sin cambios de contenido.")],
             [C("<b>4</b>"), C("<b>23 sep 2026</b>"), C("<b>Incorpora el microdato ANSV 2021 – marzo 2026. Ver sección 0.2.</b>")]],
            [22 * mm, 28 * mm, doc.width - 50 * mm]))
    A(fuente("elaboración propia del semillero."))
    A(Paragraph("Marcas de origen usadas en todo el documento — <b>F</b>: cifra tomada de una fuente externa, "
                "citada. <b>CP</b>: cálculo propio del semillero, reproducible. <b>H</b>: hipótesis adoptada, no "
                "medida. <b>DA</b>: dato abierto pendiente de consulta.", NOTA))

    # ================================================================== 0
    A(Paragraph("0. Qué cambió entre revisiones", H2))
    A(Paragraph("0.1 De la versión 1 a la revisión 2", H3))
    A(Paragraph("La versión del 2 de septiembre concluía que la tasa de siniestralidad no era publicable. Esa "
                "conclusión era correcta con los datos de entonces y dejó de serlo el 8 de septiembre. Se registra "
                "el cambio en lugar de reescribir el documento en silencio:", P))
    vinetas([
        "La objeción central era que los fallecidos de la ANSV son de 2015–2019 y el único aforo verificado, el "
        "del peaje Cocora, empieza en octubre de 2021: numerador y denominador no eran divisibles entre sí. La "
        "serie histórica de volúmenes de tránsito de INVÍAS, localizada el 8 de septiembre, aforó la MISMA vía y "
        "el MISMO tramo entre 2015 y 2018. La objeción cayó y la tasa pasó de hipótesis a resultado.",
        "Las dos incógnitas que se declaraban abiertas —la longitud del tramo y el aforo histórico— quedaron "
        "cerradas con dato medido, no con hipótesis. INVÍAS declara la longitud por estación.",
        "Las coordenadas de los portales eran las de la versión 1 del objetivo específico 1, obsoletas. Se "
        "sustituyeron por las vigentes.",
        "La numeración de actividades de la sección 7 se ajustó al Cronograma oficial del Plan de Acción.",
        "La versión 1 llamaba al semillero «GMAE». El nombre correcto es GEOPAV."], S)
    A(Paragraph("0.2 De la revisión 3 a la revisión 4", H3))
    A(Paragraph("El 22 de septiembre de 2026 la ANSV respondió una solicitud radicada por Daniel Torrente el 9 de "
                "septiembre (oficio 20265000140371) y entregó el microdato georreferenciado de siniestros de la Ruta "
                "4003 entre enero de 2021 y marzo de 2026. Cinco afirmaciones de la revisión 3 dejan de sostenerse "
                "tal como estaban escritas:", P))
    vinetas([
        "«El único dato georreferenciado público son seis puntos» y «el microdato solo se encontró publicado para "
        "Bogotá». El microdato para este corredor existe y se obtiene por solicitud; sigue sin ser público. "
        "Secciones 3, 6 y 9.",
        "«No hay dato para cuantificar el riesgo posterior al túnel». Ahora hay una cota inferior. Sección 6.",
        "«Ninguna fuente reporta nada en el lado tolimense». Es cierto solo para el conjunto de sectores críticos "
        "2015–2019. Sección 4.",
        "«No se hace mapa de calor». Se hace una densidad lineal a lo largo de la vía, no un mapa de calor en dos "
        "dimensiones. Sección 6 y Anexo A.",
        "La revisión 3 decía que en los 45 km del paso «caen los seis sectores críticos». Caen los cuatro que "
        "aportan los 42 fallecidos de la tasa; los otros dos son del tramo de la ANI. Tabla 2 y sección 6."], S)
    A(Paragraph("Nada de lo anterior cambia las tasas 2015–2019: el microdato es otra fuente, de otro periodo, "
                "con otro criterio, y no se mezcla con la línea base.", DEST))

    # ================================================================== 1
    A(Paragraph("1. El problema, en una frase", H2))
    A(Paragraph("Contar muertos en un tramo de vía es como contar goles sin saber cuántos partidos se jugaron. Un "
                "tramo con veinte fallecidos y un millón de vehículos al año es más seguro que uno con cinco "
                "fallecidos y diez mil. Por eso la siniestralidad no se mide en muertos: se mide en muertos por "
                "unidad de exposición.", P))
    A(Paragraph("Este documento fija cómo obtenemos ambas cosas —los fallecidos y la exposición— para el corredor "
                "Ibagué – Calarcá, y hasta dónde llega lo que podemos afirmar con ellas.", P))

    # ================================================================== 2
    A(Paragraph("2. Delimitación del tramo de análisis", H2))
    A(Paragraph("La ponencia de ARCS / UC Consult declara «4 horas de cruce» sin especificar entre qué dos puntos. "
                "Cuatro horas para 130 km y cuatro horas para 40 km describen situaciones distintas. El semillero "
                "fija el alcance de forma explícita:", P))
    A(Paragraph("<b>Corredor de análisis:</b> Ibagué – Calarcá sobre la Ruta Nacional 40, entre los dos portales "
                "del túnel de base determinados en el objetivo específico 1: portal oriental 4,3640 N / 75,1960 W "
                "(Ibagué, Tolima) y portal occidental 4,4800 N / 75,6520 W (Calarcá, Quindío). Son las coordenadas "
                "vigentes de cifras_OE1.json v2 <b>[CP]</b>.", P))
    A(Paragraph("<b>Subtramo del paso:</b> el cruce de la cordillera propiamente dicho, entre Calarcá y Cajamarca, "
                "que INVÍAS afora en su estación 244.", P))
    A(Paragraph("El portal occidental cae en Calarcá y no en Armenia, verificado contra la capa de municipios del "
                "IGAC. Por eso el tramo Armenia – Calarcá, que INVÍAS afora aparte en su estación 245, queda fuera "
                "del corredor. Si se analizara el corredor completo Ibagué – Armenia serían 79 km en lugar de 74. "
                "Las dos definiciones de tramo se publican juntas, con su denominador declarado:", P))
    titulo_tabla("Definiciones del tramo de análisis", S)
    A(tabla([[CB(x) for x in ["Definición", "Longitud", "Cómo se compone", "Marca"]],
             [C("Corredor entre portales"), C("74 km"), C("Estación 244 (45 km) + estación 243 (29 km). Es el tramo "
                                                           "que la ANSV nombra «Calarcá – Ibagué»."), C("F")],
             [C("Solo el paso"), C("45 km"), C("Estación 244, sector Calarcá – Cajamarca. Es donde caen los cuatro "
                                              "sectores críticos que aportan los 42 fallecidos de la tasa."), C("F")]],
            [40 * mm, 22 * mm, doc.width - 80 * mm, 18 * mm]))
    A(fuente("elaboración propia del semillero con base en la ANSV y el INVÍAS."))
    A(Paragraph("El microdato de la ANSV usa la abscisa continua de la Ruta 4003, de Armenia (PR 0) a Ibagué "
                "(PR 80+194). Para leerlo con las mismas definiciones se asigna el paso a los km 5,0 a 50,365 y el "
                "tramo Cajamarca – Ibagué a los km 50,365 a 80,194. El límite de Calarcá en el km 5,0 sale de la "
                "longitud INVÍAS de la estación 245 y es una hipótesis <b>[H]</b>; el de Cajamarca lo declara el "
                "propio anexo de la ANSV <b>[F]</b>.", P))

    # ================================================================== 3
    A(Paragraph("3. Fuentes de datos verificadas", H2))
    titulo_tabla("Fuentes de datos verificadas", S)
    A(tabla([[CB(x) for x in ["Fuente", "Entidad", "Qué aporta", "Periodo", "Marca"]],
             [C("Sectores Críticos de Siniestralidad Vial (rs3u-8r4q)"), C("ANSV"), C("Fallecidos por punto de referencia, con coordenadas y estadístico Gi*"), C("2015–2019"), C("F")],
             [C("Velocidad de vehículos de carga"), C("ANSV"), C("Excesos por encima de 80 km/h por tramo"), C("—"), C("F")],
             [C("<b>Microdato georreferenciado de siniestros, Ruta 4003</b> (oficio 20265000140371)"), C("ANSV – ONSV; fuente primaria INMLCF"),
              C("Una fila por víctima, con coordenadas, PR, tipo de usuario, circunstancia y gravedad. Solo lo que pudo georreferenciarse"), C("ene 2021 – mar 2026"), C("F")],
             [C("Tráfico Vehicular ANI (8yi9-t44c)"), C("ANI"), C("Vehículos por peaje y categoría, mensual — peaje Cocora"), C("oct 2021 – may 2026"), C("F")],
             [C("Serie histórica de TPD 1997–2018"), C("INVÍAS"), C("TPD anual y composición vehicular por estación de aforo"), C("1997–2018"), C("F")],
             [C("Serie histórica de TPD 2019"), C("INVÍAS"), C("Aforo mensual por peaje — peaje Cajamarca"), C("2019"), C("F")],
             [C("Ficha del Túnel de La Línea"), C("INVÍAS"), C("Fecha de apertura y longitud de la obra que cambió el corredor"), C("2020"), C("F")],
             [C("Forensis"), C("Medicina Legal"), C("Fallecidos por municipio después de 2019"), C("anual"), C("DA")]],
            [44 * mm, 26 * mm, doc.width - 112 * mm, 26 * mm, 16 * mm]))
    A(fuente("entidades citadas en la propia tabla."))
    A(Paragraph("La serie histórica de INVÍAS estuvo marcada DA durante semanas porque sus enlaces indexados "
                "responden 404. Los archivos viven en invias.gov.co/publicaciones/4154/documentos-tecnicos/, que "
                "sirve las descargas por loader.php con el parámetro idFile. Descargados el 8 de septiembre de 2026 "
                "y verificados por sha256 contra una segunda descarga.", NOTA))
    A(Paragraph("El microdato de la ANSV no es de acceso abierto: se obtuvo por solicitud. Trae edad, sexo, fecha y "
                "lugar de cada víctima, así que <b>el semillero no publica el archivo crudo</b> ni el oficio (que "
                "contiene un correo personal); publica los agregados y el script que los produce.", P))
    A(Paragraph("Un defecto de origen en la fuente, corregido en la extracción", H3))
    A(Paragraph("INVÍAS publica la composición vehicular como un texto del tipo autos-buses-camiones (por ejemplo "
                "35-10-55). Excel convirtió parte de esos valores a fecha: 22-09-69 quedó guardado como 1969-09-22, "
                "y otros como número de serie. El script de extracción lo revierte leyendo día-mes-año y valida que "
                "los tres porcentajes sumen 100 ± 1. Se recuperaron 61 de 62 registros; el único descartado es la "
                "estación 245 en 2003, cuyo valor de origen (850-5-10) no suma 100.", P))

    # ================================================================== 4
    A(Paragraph("4. Línea base de fallecidos", H2))
    A(Paragraph("El conjunto Sectores Críticos de la ANSV entrega fallecidos acumulados por punto de referencia, con "
                "coordenadas, tramo, entidad a cargo y el estadístico de puntos calientes Getis-Ord Gi*. Filtrado al "
                "corredor arroja seis sectores críticos, todos en jurisdicción de Calarcá (Quindío), que caben en "
                "3,6 km del descenso:", P))
    titulo_tabla("Sectores críticos de la ANSV en el corredor, 2015–2019", S)
    conf = lambda z: "99 %" if abs(z) >= 2.58 else "95 %" if abs(z) >= 1.96 else "90 %" if abs(z) >= 1.65 else "n.s."
    filas = [[CB(x) for x in ["Punto de referencia", "Fallecidos 2015–2019", "Confianza Gi*", "Entidad", "¿Entra en la tasa?"]]]
    for r in sorted(sec, key=lambda r: -int(r["fallecidos"])):
        filas.append([C(f"PR {r['pr']}"), C(r["fallecidos"]), C(conf(float(r["gizscore"]))),
                      C("ANI" if r["entidad"].upper().startswith("ANI") else "INVÍAS"),
                      C("Sí" if r["en_el_paso"] == "Si" else "No — tramo de la ANI")])
    filas.append([C("<b>Total del corredor</b>"), C(f"<b>{FALL_CORR}</b>"), C(""), C(""), C(f"<b>{FALL_PASO} entran en la tasa</b>")])
    A(tabla(filas, [38 * mm, 32 * mm, 28 * mm, 26 * mm, doc.width - 124 * mm]))
    A(fuente("ANSV, conjunto Sectores Críticos de Siniestralidad Vial (datos.gov.co, rs3u-8r4q) [F]."))
    A(Paragraph(f"Los cuatro sectores del tramo «Calarcá – Ibagué» a cargo de INVÍAS suman {FALL_PASO} fallecidos y son "
                f"los que entran en la tasa. Los dos a cargo de la ANI, con {FALL_CORR - FALL_PASO} fallecidos, "
                "pertenecen al tramo La Paila – Calarcá y no al cruce de la cordillera: se calculan aparte como fila "
                "de control. Los niveles de confianza son los de la propia fuente: |z| ≥ 2,58 corresponde al 99 %, "
                "≥ 1,96 al 95 % y ≥ 1,65 al 90 %.", P))
    A(Paragraph("El lado tolimense: acotado con el microdato", H3))
    A(Paragraph("Ninguno de los dos conjuntos nacionales de la ANSV marca sectores críticos en Cajamarca ni en el "
                "tramo Cajamarca – Ibagué, aunque la ANSV sí cubre el Tolima en otras partes, con 10 sectores "
                "críticos y 137 fallecidos en Ibagué, Alvarado, Coyaima, Espinal y Flandes. Para el conjunto de "
                "velocidad la ausencia tiene explicación de método: solo registra vehículos de carga por encima de "
                "80 km/h, y el paso se opera por debajo de 20 km/h. La ausencia ahí indica congestión, no seguridad.", P))
    t3 = TR["Cajamarca – Ibagué"]
    A(Paragraph(f"El microdato 2021 – marzo 2026 registra en el tramo Cajamarca – Ibagué {t3['hechos']} hechos, con "
                f"{t3['fallecidos']} fallecidos y {t3['lesionados']} lesionados <b>[F]</b>. La ausencia en el conjunto "
                "de sectores críticos era de sector crítico, no de siniestros. Para 2015 – 2019 la explicación sigue "
                "pidiendo el contraste con Forensis <b>[DA]</b>.", P))
    A(Paragraph("Microdato posterior al túnel, 2021 – marzo 2026", H3))
    A(Paragraph(f"El anexo de la ANSV trae {MD['victimas']} víctimas —{MD['fallecidos']} fallecidos y "
                f"{MD['lesionados']} lesionados— entre el {MD['periodo'][0][8:10]}/{MD['periodo'][0][5:7]}/{MD['periodo'][0][:4]} "
                f"y el {MD['periodo'][1][8:10]}/{MD['periodo'][1][5:7]}/{MD['periodo'][1][:4]}. El anexo no trae "
                f"identificador de siniestro: el semillero agrupa en un mismo <b>hecho</b> las víctimas con igual "
                f"fecha, municipio y punto de referencia <b>[H]</b>, lo que da {MD['hechos']} hechos en solo "
                f"{MD['puntos_distintos_hechos']} puntos distintos <b>[CP]</b>. El script comprueba antes que los "
                "registros reproducen las tablas resumen que la propia ANSV incluyó en el anexo.", P))
    titulo_tabla("Microdato de la ANSV por tramo, 2021 – marzo 2026", S)
    filas = [[CB(x) for x in ["Tramo", "Hechos", "Hechos fatales", "Fallecidos", "Lesionados"]]]
    for k in ("Armenia – Calarcá (fuera)", "Paso Calarcá – Cajamarca", "Cajamarca – Ibagué"):
        d = TR[k]; filas.append([C(k), C(str(d["hechos"])), C(str(d["hechos_fatales"])), C(str(d["fallecidos"])), C(str(d["lesionados"]))])
    A(tabla(filas, [doc.width - 112 * mm, 28 * mm, 28 * mm, 28 * mm, 28 * mm]))
    A(fuente("ANSV, oficio 20265000140371 y su anexo [F]; agrupación y tramos del semillero, "
             "Act3_Siniestros/procesar_microdato_ANSV_OE5.py [CP] [H]."))
    k11 = MD["paso_km_11_a_41"]
    A(Paragraph(f"Entre el km 11 y el 41 —el ascenso y el Alto de La Línea— el anexo registra {k11['hechos']} hechos y "
                f"{k11['fallecidos']} fallecido. Los registros se concentran en las entradas de Calarcá, Cajamarca e "
                f"Ibagué, y un solo punto de Calarcá urbano acumula {MD['punto_mas_cargado_hechos']['hechos']} hechos, "
                "lo que sugiere un punto por defecto de la georreferenciación. Para medir cuánto falta se cruzó el "
                "anexo con los siniestros fatales que el semillero ya había verificado en prensa:", P))
    titulo_tabla("Siniestros fatales de prensa frente al microdato de la ANSV", S)
    filas = [[CB(x) for x in ["Fecha", "Hecho", "Muertos en prensa", "En el anexo"]]]
    for r in prensa:
        y, m, d = r["fecha"].split("-")
        si = r["en_anexo_ANSV"] == "si"
        filas.append([C(f"{d}/{m}/{y}"), C(r["hecho"]), C(r["muertos_prensa"].replace("no indicado", "s. d.")),
                      C(f"<b>Sí · {r['fallecidos_anexo']}</b>" if si else "No")])
    A(tabla(filas, [24 * mm, doc.width - 74 * mm, 26 * mm, 24 * mm]))
    A(fuente("El Tiempo, El Espectador e Infobae, verificados en el medio original; cruce con ±1 día, "
             "Act3_Siniestros/cruce_prensa_ANSV.csv [CP]."))
    A(Paragraph(f"Figuran {MD['prensa']['en_anexo']} de {MD['prensa']['total']}. El microdato es útil para saber dónde "
                "registra la ANSV siniestros después del túnel, pero <b>subregistra justo el ascenso</b>, que es "
                "donde la prensa sitúa la mayoría de los fatales. Se lee con esa advertencia en todo el documento.", DEST))

    # ================================================================== 5
    A(Paragraph("5. Exposición: el denominador", H2))
    A(Paragraph("La exposición se mide en puntos de aforo distintos, con criterios de clasificación distintos, y las "
                "lecturas no son intercambiables. El documento las publica por separado:", P))
    titulo_tabla("Puntos de medición de la exposición", S)
    nombres = ["Estación 244 · INVÍAS — tramo del paso, 45 km", "Estación 243 · INVÍAS — Cajamarca – Ibagué, 29 km",
               "Peaje Cajamarca · PR 24+020 — punto", "Peaje Cocora · K 13+750 — punto"]
    filas = [[CB(x) for x in ["Punto de medición", "Periodo", "TPD total", "Carga pesada", "Marca"]]]
    for n, (per, tpd, part) in zip(nombres, MATRIZ):
        filas.append([C(n), C(str(per).replace("Anio ", "").replace("-", "–")), C(es_co(tpd)), C(es_co(part * 100, 1) + " %"), C("F")])
    A(tabla(filas, [doc.width - 106 * mm, 36 * mm, 24 * mm, 28 * mm, 18 * mm]))
    A(fuente("INVÍAS (serie histórica por estación) y ANI (tráfico por peaje), vía "
             "Act2_Clasificacion/matriz_aforos_clasificada_OE5.xlsx [F]."))
    A(Paragraph("Las cuatro filas NO son una serie temporal. Son cuatro mediciones del mismo corredor en puntos y con "
                "criterios distintos. Leerlas como evolución —«la carga pesada pasó del 32,9 % en 2019 al 17,9 % "
                "hoy»— mezcla dos peajes distintos y no es defendible.", P))
    A(Paragraph("Por qué las participaciones no son comparables entre sí", H3))
    titulo_tabla("Homologación de clases vehiculares entre peajes y estaciones de aforo", S)
    A(tabla([[CB(x) for x in ["Clase", "En los peajes", "En la serie por estación de INVÍAS"]],
             [C("Livianos"), C("Categoría I"), C("«autos»")],
             [C("Intermedios"), C("Categoría II — buses y camión de dos ejes"), C("«buses»")],
             [C("Carga pesada"), C("Categorías III a VII — tres o más ejes"), C("«camiones»")]],
            [34 * mm, (doc.width - 34 * mm) / 2, (doc.width - 34 * mm) / 2]))
    A(fuente("INVÍAS y ANI; homologación del semillero [CP]."))
    A(Paragraph("La serie por estación publica solo tres porcentajes y su clase «camiones» incluye los de dos ejes, "
                "que en peaje caen en categoría II. Por eso su participación de carga pesada (54–56 %) es "
                "sistemáticamente mayor que la del peaje (18–33 %). Las dos lecturas no se promedian: la estación "
                "244 sirve de cota superior, no de valor central.", P))
    A(Paragraph("Cocora y Cajamarca son dos peajes distintos", H3))
    A(Paragraph("El peaje Cocora está en el K 13+750 de la segunda calzada Ibagué – Cajamarca y lo administra la "
                "concesión APP GICA de la ANI. El peaje Cajamarca está en el PR 24+020 de la carretera Armenia – "
                "Ibagué y lo administra INVÍAS. Los separan unos 10 km y Cocora está aguas abajo del ascenso, de modo "
                "que capta tráfico local que nunca cruza la cordillera. Sus series no se comparan sin homologar el "
                "punto de medición.", P))
    A(Paragraph("Exposición de la carga pesada en el paso", H3))
    A(Paragraph(f"Con la composición de la estación 244 sobre los 45 km del paso: {es_co(TPD_CAM)} camiones al día, es "
                f"decir {es_co(VKM_CAM)} vehículos-kilómetro al año de carga pesada cruzando la cordillera "
                "<b>[CP]</b>. Es la exposición del grupo que la Ferropista captaría, y el 90 % de captación que "
                "declara la ponencia <b>[F, dia. 10]</b> es una cifra del proponente, no auditada.", P))

    # ================================================================== 6
    A(Paragraph("6. La tasa normalizada", H2))
    A(Paragraph("La unidad estándar en ingeniería de seguridad vial es el número de fallecidos por cada cien "
                "millones de vehículos-kilómetro recorridos:", P))
    A(Paragraph("<font face='Courier' size=9>Tasa = fallecidos ÷ (TPD × 365 × L × años) × 10</font>"
                "<font face='Courier' size=9><super>8</super></font>", P))
    A(Paragraph("donde L es la longitud del tramo en kilómetros y TPD el tránsito promedio diario del mismo periodo "
                "en que se contaron los fallecidos.", P))
    titulo_tabla("Tasa de mortalidad normalizada por exposición, 2015–2019", S)
    A(tabla([[CB(x) for x in ["Ámbito", "Fallecidos", "TPD", "L (km)", "Años", "Tasa", "Marca"]],
             [C("Corredor entre portales"), C(str(FALL_PASO)), C(es_co(TPOND)), C("74"), C("5"), C(f"<b>{es_co(TASA_CORR, 2)}</b>"), C("CP")],
             [C("Solo el paso — estación 244"), C(str(FALL_PASO)), C(es_co(T244)), C("45"), C("5"), C(f"<b>{es_co(TASA_PASO, 2)}</b>"), C("CP")],
             [C("Control · los 52 del corredor"), C(str(FALL_CORR)), C(es_co(TPOND)), C("74"), C("5"), C(es_co(TASA_CTRL, 2)), C("CP")],
             [C("Lo que publicaba el libro anterior"), C(str(FALL_PASO)), C("3.000"), C("60"), C("5"), C(es_co(TASA_VIEJA, 2)), C("H")]],
            [doc.width - 116 * mm, 22 * mm, 20 * mm, 16 * mm, 14 * mm, 22 * mm, 16 * mm]))
    A(fuente("OE5_SeguridadVial/Act4_Analisis/analisis_siniestralidad_OE5.xlsx [CP]."))
    A(Paragraph(f"El TPD del corredor, {es_co(TPOND)} veh/día, es la ponderación por longitud de las dos estaciones: "
                f"({es_co(T243)} × 29 + {es_co(T244)} × 45) ÷ 74 <b>[CP]</b>. Las dos primeras filas usan los mismos "
                f"{FALL_PASO} fallecidos y difieren solo en el denominador: la primera los reparte sobre los 74 km del "
                "tramo que la ANSV nombra; la segunda, sobre los 45 km donde caen los cuatro sectores que los aportan. "
                "La segunda es mayor porque concentra la misma mortalidad en menos kilómetros.", P))
    A(Paragraph(f"<b>La cifra anterior era casi tres veces la real, y se dice en voz alta.</b> El semillero publicaba "
                f"{es_co(TASA_VIEJA, 2)} porque asumía un tránsito de 3.000 vehículos al día y un tramo de 60 km. "
                "Ambas entradas eran supuestos. La cifra queda retirada y se registra aquí para que el cambio sea "
                "auditable.", NOTA))
    A(Paragraph("La hipótesis del año faltante, declarada y acotada", H3))
    A(Paragraph(f"El registro de fallecidos cubre cinco años (2015–2019); el aforo de INVÍAS cubre cuatro en la "
                "estación 244 y tres en la 243. El cálculo supone que 2019 tuvo un tránsito parecido <b>[H]</b>. No es "
                f"una hipótesis ciega: el peaje Cajamarca de 2019 midió {es_co(TPD_CAJ19)} veh/día, y sustituyéndolo "
                f"la tasa del paso pasa de {es_co(TASA_PASO, 2)} a {es_co(TASA_ESC, 2)}, un movimiento del "
                f"{es_co(MUEVE * 100, 1)} % que no cambia ninguna conclusión <b>[CP]</b>.", P))
    A(Paragraph("El desfase de fondo sigue en pie. El Túnel de La Línea entró en operación el 4 de septiembre de "
                "2020 y cambió la geometría, la velocidad de operación y la composición del tránsito. La línea base "
                "describe el corredor ANTERIOR al túnel y por tanto SOBRESTIMA el riesgo del corredor actual.", DEST))
    A(Paragraph("Tasa posterior al túnel, como cota inferior", H3))
    A(Paragraph(f"Con el microdato se puede calcular una tasa del paso para 2021–2025 (cinco años completos): "
                f"{PT['fallecidos_paso_2021_2025']} fallecidos en los 45 km. No existe aforo del paso posterior a 2019, "
                "así que el TPD es una hipótesis <b>[H]</b> y se prueban dos valores:", P))
    titulo_tabla("Tasa del paso posterior al túnel, 2021–2025", S)
    A(tabla([[CB(x) for x in ["Hipótesis de TPD", "TPD", "Fallecidos", "Tasa", "Marca"]],
             [C("Estación 244, media 2015–2018"), C(es_co(PT["tpd_H1_est244_media_2015_2018"])), C(str(PT["fallecidos_paso_2021_2025"])), C(f"<b>{es_co(PT['tasa_H1'], 2)}</b>"), C("CP · H")],
             [C("Peaje Cajamarca, 2019"), C(es_co(PT["tpd_H2_peaje_cajamarca_2019"])), C(str(PT["fallecidos_paso_2021_2025"])), C(f"<b>{es_co(PT['tasa_H2'], 2)}</b>"), C("CP · H")],
             [C("Estación 244, sin los fallecidos del km 5,0"), C(es_co(PT["tpd_H1_est244_media_2015_2018"])), C(str(PT["fallecidos_si_se_excluye_km_5_0"])), C(es_co(PT["tasa_H1_sin_borde"], 2)), C("CP · H")]],
            [doc.width - 94 * mm, 24 * mm, 24 * mm, 24 * mm, 22 * mm]))
    A(fuente("Act4_Analisis/densidad_lineal_OE5.py y tasa_post_tunel_OE5.json [CP]; el script reproduce 7,66 como "
             "control antes de calcular."))
    A(Paragraph("La última fila existe porque los dos fallecidos del bus del 14 de diciembre de 2023 caen exactamente "
                "en el km 5,0, el límite supuesto entre Calarcá y el paso. <b>Es una cota inferior</b> por el "
                "subregistro de la sección 4 y <b>no se compara con la tasa 2015–2019</b>: otra fuente y otro "
                "criterio. Lo que sí dice es que la tasa posterior al túnel no es despreciable.", P))
    A(Paragraph("El mapa de calor: por qué es lineal", H3))
    A(Paragraph("La revisión 3 decía que no se hacía mapa de calor porque no había insumo. Con el microdato el insumo "
                "existe, y la respuesta cambia de «no» a «no en dos dimensiones»:", P))
    vinetas([
        "Un estimador de densidad en dos dimensiones reparte sobre el monte lo que ocurre en una línea. Por eso la "
        "densidad se calcula a lo largo de la abscisa de la vía (núcleo gaussiano, ancho de banda 1,5 km <b>[H]</b>).",
        "Cuenta <b>hechos</b> y no víctimas: un solo bus con 24 lesionados dominaría la figura.",
        "Lleva escrita la advertencia del subregistro: muestra dónde se pudo georreferenciar, no dónde está el riesgo.",
        "Para 2015–2019 se mantiene el mapa de sectores críticos, con el color tomado del Gi* de la propia fuente: "
        "hacer un mapa de calor sobre esos seis puntos sería el mapa de calor de un mapa de calor."], S)
    A(Paragraph("La lámina está en el Anexo A.", P))

    # ================================================================== 7
    A(Paragraph("7. Procedimiento, actividad por actividad", H2))
    A(Paragraph("La numeración es la del Cronograma oficial del Plan de Acción, filas 31 a 35 del Google Sheet.", NOTA))
    A(Paragraph("Actividad 1 (fila 31) — Extracción de las series de volúmenes de tránsito de INVÍAS", H3))
    vinetas([
        "Descargar los dos libros de la serie histórica y verificar su sha256 contra una segunda descarga.",
        "Barrer TODAS las estaciones de la vía 4003 en Tolima, Quindío y Valle y marcar cada una con "
        "en_corredor_portales, de modo que la exclusión de la 245 sea una decisión visible.",
        "Revertir la conversión a fecha de la composición vehicular y validar que sume 100 ± 1.",
        "Descargar de datos.gov.co los dos conjuntos nacionales de la ANSV completos, sin filtrar a mano."], S)
    A(Paragraph("<b>Producto:</b> base de datos cruda de aforos, en CSV y Excel. Verificador.", P))
    A(Paragraph("Actividad 2 (fila 32) — Clasificación vehicular del TPDA y depuración del flujo de carga pesada", H3))
    vinetas([
        "Homologar las clases de los peajes y de la serie por estación según la sección 5.",
        "Calcular el TPD mensual dividiendo el total del mes entre sus días calendario.",
        "Construir la matriz consolidada por referencia a las hojas de origen. Ninguna cifra a mano."], S)
    A(Paragraph("<b>Producto 10:</b> matriz de aforos clasificada, en Excel, con 635 fórmulas vivas.", P))
    A(Paragraph("Actividad 3 (fila 33) — Recopilación de reportes de siniestralidad de la ANSV", H3))
    vinetas([
        "Recortar el corredor sobre los conjuntos nacionales y publicar el recorte junto al conjunto completo.",
        "Calcular todas las cifras del histórico desde el conjunto, sin escribirlas, y distinguir siempre de cuál "
        "de los dos conjuntos sale cada una.",
        "Procesar el microdato de la ANSV con procesar_microdato_ANSV_OE5.py: comprobar que reproduce las tablas "
        "resumen de la propia ANSV, agrupar víctimas en hechos, calcular la abscisa, asignar tramos y cruzar con "
        "la prensa. Publicar solo agregados, sin edad ni sexo de las víctimas."], S)
    A(Paragraph("<b>Producto:</b> histórico de siniestros, en PDF (revisión 2, con la sección del microdato). Verificador.", P))
    A(Paragraph("Actividad 4 (fila 34) — Análisis estadístico de la siniestralidad de vehículos pesados en el descenso", H3))
    vinetas([
        "Aplicar la fórmula de la sección 6 con la longitud declarada y el aforo medido, en las dos definiciones de tramo.",
        "Declarar la hipótesis del año faltante y acotarla contra el peaje Cajamarca de 2019.",
        "Producir el mapa de sectores críticos sobre el trazado con el Gi* de la fuente, y la densidad lineal sobre "
        "el microdato con densidad_lineal_OE5.py. No se hace mapa de calor en dos dimensiones.",
        "Calcular la tasa posterior al túnel como cota inferior, con el TPD declarado como hipótesis."], S)
    A(Paragraph("<b>Producto 11:</b> análisis y gráficos de siniestralidad, en Excel, PNG y PDF, con 115 fórmulas vivas "
                "y figuras deterministas.", P))
    A(Paragraph("Actividad 5 (fila 35) — Consolidación del diagnóstico operacional de la infraestructura vial", H3))
    vinetas([
        "Generar el informe leyendo las cifras del libro de la actividad 4 y de los JSON del microdato en el momento "
        "de escribir el PDF. Ninguna cifra tecleada.",
        "Proteger esa lectura con una guardia de rótulo que aborta si el libro cambió de estructura.",
        "Recalcular las tasas de forma independiente y detener la generación si difieren en más de 0,01."], S)
    A(Paragraph("<b>Producto 12:</b> informe de diagnóstico vial, en PDF (revisión 3).", P))
    A(Paragraph("Los blindajes se probaron a propósito: se alteró un rótulo del libro y el script se detuvo con código "
                "1, y se forzó una diferencia en la tasa y el informe no se generó. Esta memoria usa los mismos "
                "blindajes: no se genera si el libro, la matriz o los JSON del microdato no cuadran.", NOTA))

    # ================================================================== 8
    A(Paragraph("8. Qué podemos afirmar y qué no", H2))
    A(Paragraph("Sostenible", H3))
    vinetas([
        "La tasa de mortalidad 2015–2019 normalizada por exposición, con las dos entradas medidas, en sus dos "
        "definiciones de tramo.",
        "La línea base georreferenciada de fallecidos, con su periodo, su entidad a cargo y sus sesgos declarados.",
        "La participación de la carga pesada en cada punto de aforo, con la advertencia de que no son comparables.",
        "La exposición anual en vehículos-kilómetro de la carga pesada que hace el cruce.",
        "Que la línea base es anterior al Túnel de La Línea y sobrestima la siniestralidad del corredor actual.",
        "Dónde registra la ANSV siniestros georreferenciados después del túnel, y cuánto subregistra: de ocho "
        "siniestros fatales de prensa, dos."], S)
    A(Paragraph("No sostenible", H3))
    vinetas([
        "Cuántas muertes evitaría la Ferropista. Exige un modelo calibrado con microdatos completos por siniestro. "
        "El que entregó la ANSV solo incluye lo que pudo georreferenciarse; con ese subregistro no se calibra un modelo.",
        "Que la tasa de hoy es la de 2015–2019, o que es la de 2021–2025: la primera es anterior al túnel y la "
        "segunda es solo una cota inferior.",
        "Que el lado tolimense tiene menos mortalidad por kilómetro. El microdato muestra que ahí sí hay siniestros, "
        "pero su subregistro no permite comparar.",
        "Que el vehículo pesado es el causante de los fallecidos del microdato: el campo registra el tipo de usuario "
        "de la víctima, no el vehículo que causó el siniestro."], S)
    A(Paragraph("Lo que el semillero aporta no es una predicción, sino una caracterización del riesgo por "
                "exposición: quién está expuesto, cuánto, y qué le pasa a esa exposición si la carga pesada deja de "
                "hacer el descenso.", P))

    # ================================================================== 9
    A(Paragraph("9. Limitaciones declaradas", H2))
    vinetas([
        "El conjunto de sectores críticos reporta únicamente fallecidos y es un producto derivado de análisis "
        "espacial, no el microdato por siniestro.",
        "El microdato de la ANSV solo trae lo que pudo georreferenciarse desde el campo de dirección de Medicina "
        "Legal; subregistra el ascenso. No es de acceso abierto y el crudo no se publica.",
        "El «hecho» del microdato es una agrupación del semillero <b>[H]</b>: un mismo siniestro registrado en dos "
        "puntos cuenta como dos hechos.",
        "El límite entre Calarcá y el paso en el km 5,0 es una hipótesis <b>[H]</b>; dos fallecidos caen justo en él.",
        "No hay aforo del paso posterior a 2019: la tasa 2021–2025 usa TPD supuestos <b>[H]</b>.",
        "El periodo 2015–2019 es anterior a la entrada en operación del Túnel de La Línea.",
        "La composición de la estación 244 salta de 60–69 % de camiones a 44 % en 2018. Ese año aislado no se usa "
        "hasta contrastarlo <b>[DA]</b>.",
        "No existe un denominador nacional de vehículos-kilómetro publicado; la comparación con el promedio del "
        "país queda pendiente <b>[DA]</b>.",
        "Los siniestros posteriores al túnel documentados por prensa se verificaron en el medio original; no entran "
        "en la tasa 2015–2019 ni se mezclan con el microdato."], S)

    # ================================================================== 10
    A(Paragraph("10. Trazabilidad", H2))
    titulo_tabla("Archivos que respaldan esta memoria", S)
    A(tabla([[CB(x) for x in ["Carpeta", "Contenido"]],
             [C("Act1_Aforos/"), C("Los libros de INVÍAS, el aforo mensual del peaje Cocora, las series extraídas en CSV y los scripts de descarga y extracción.")],
             [C("Act2_Clasificacion/"), C("La matriz de aforos clasificada y el script que la construye.")],
             [C("Act3_Siniestros/"), C("Los dos conjuntos nacionales de la ANSV, el recorte del corredor, el histórico en PDF y su script; "
                                       "procesar_microdato_ANSV_OE5.py y sus agregados (hechos, por km, cruce con prensa, resumen). "
                                       "El anexo crudo y el oficio de la ANSV se conservan fuera del repositorio público.")],
             [C("Act4_Analisis/"), C("El libro de la tasa, los scripts de análisis y figuras, densidad_lineal_OE5.py y tasa_post_tunel_OE5.json.")],
             [C("Act5_Informe/"), C("El informe de diagnóstico vial en PDF y el script que lo genera.")],
             [C("Visuales/"), C("Las láminas de siniestralidad y de densidad lineal, en PNG y PDF.")],
             [C("(raíz del objetivo)"), C("Esta memoria, el script que la genera (generar_memoria_OE5.py) y las revisiones anteriores, que se conservan.")]],
            [42 * mm, doc.width - 42 * mm]))
    A(fuente("carpeta OE5_SeguridadVial del repositorio del proyecto."))

    # ================================================================== anexo A
    lam = os.path.join(VIS, "densidad_lineal_OE5.png")
    if not os.path.exists(lam):
        raise SystemExit("PARADA: falta Visuales/densidad_lineal_OE5.png (Anexo A).")
    A(PageBreak())
    A(Marca("A", "Anexo A. Densidad lineal de siniestros georreferenciados por la ANSV"))
    A(Paragraph("Anexo A. Densidad lineal de siniestros georreferenciados por la ANSV", H2))
    CONT["F"] += 1
    tf = f"Figura {CONT['F']}. Densidad lineal de siniestros georreferenciados, Ruta 4003, 2021 – marzo 2026"
    A(Marca("F", tf))
    A(Paragraph(tf, ParagraphStyle("TF", parent=TIT_TABLA, alignment=1)))
    A(Image(lam, width=doc.width, height=doc.width * 1880 / 3100))
    A(Paragraph("Fuente: ANSV, oficio 20265000140371 (solicitud de D. Torrente); figura generada por "
                "Act4_Analisis/densidad_lineal_OE5.py [CP]. Muestra dónde se pudo georreferenciar, no dónde está el "
                "riesgo.", ParagraphStyle("FF", parent=FUENTE, alignment=1)))
    A(Spacer(1, 14))
    A(Paragraph("<i>Nota de elaboración: la revisión 3 corrigió la presentación según el tutor. La revisión 4 incorpora "
                "el microdato georreferenciado que la ANSV entregó por solicitud, la densidad lineal y la tasa "
                "posterior al túnel como cota inferior, y corrige la mención a los «seis sectores» del paso. Ambas "
                "contaron con apoyo de un asistente de inteligencia artificial (Claude, de Anthropic); el semillero "
                "verificó el resultado, y el script que genera esta memoria se detiene si alguna cifra no cuadra con "
                "sus archivos de origen.</i>", FUENTE))
    return S


doc = construir_documento(cuerpo)
print("PDF escrito:", SALIDA)
