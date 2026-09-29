# -*- coding: utf-8 -*-
"""Plantilla ReportLab de los productos del OE 3 (estándar de presentación del semillero GEOPAV).

Portada con logos y ficha; tabla de contenido; índices de tablas, figuras y anexos con número de
página (construcción iterativa); encabezado con logo de la Universidad a la izquierda y de GEOPAV a
la derecha, filete verde; «Tabla N.»/«Figura N.» con fuente debajo; verde #178E2C principal y azul
#193F77 secundario. Admite páginas apaisadas para planos (plantilla «h»).
Derivada de OE5_SeguridadVial/Act5_Informe/informe_diagnostico_OE5.py (rev. 3).
"""
import os
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, Image, NextPageTemplate, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

OE3 = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(OE3)
LOGO_U = os.path.join(REPO, "public", "logo-unibague.png"); LOGO_G = os.path.join(REPO, "public", "logo-geopav.png")
VERDE = colors.HexColor("#178E2C"); AZUL = colors.HexColor("#193F77"); FONDO = colors.HexColor("#F1F7F2")
GRIS = colors.HexColor("#475569"); LINEA = colors.HexColor("#CBD5E1")
LETRA = letter; APAIS = landscape(letter); MARGEN = 23 * mm

def es_co(v, dec=1):
    return f"{v:,.{dec}f}".replace(",", "@").replace(".", ",").replace("@", ".")

def _fuente():
    for reg, neg, cur, nc in [
        ("/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf", "/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf",
         "/usr/share/fonts/truetype/crosextra/Carlito-Italic.ttf", "/usr/share/fonts/truetype/crosextra/Carlito-BoldItalic.ttf"),
        (r"C:\Windows\Fonts\calibri.ttf", r"C:\Windows\Fonts\calibrib.ttf", r"C:\Windows\Fonts\calibrii.ttf", r"C:\Windows\Fonts\calibriz.ttf")]:
        if all(os.path.exists(x) for x in (reg, neg, cur, nc)):
            for n, f in (("Txt", reg), ("Txt-B", neg), ("Txt-I", cur), ("Txt-BI", nc)): pdfmetrics.registerFont(TTFont(n, f))
            registerFontFamily("Txt", normal="Txt", bold="Txt-B", italic="Txt-I", boldItalic="Txt-BI")
            return "Txt", "Txt-B", "Txt-I"
    return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"
F_REG, F_BOLD, F_ITAL = _fuente()

ss = getSampleStyleSheet()
P = ParagraphStyle("P", parent=ss["Normal"], fontName=F_REG, fontSize=11, leading=16.5, alignment=TA_JUSTIFY, spaceAfter=9, textColor=colors.HexColor("#1F2933"))
H1 = ParagraphStyle("H1x", parent=ss["Heading1"], fontName=F_BOLD, fontSize=17, leading=22, textColor=VERDE, spaceBefore=6, spaceAfter=12)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName=F_BOLD, fontSize=16, leading=21, textColor=VERDE, spaceBefore=16, spaceAfter=10, keepWithNext=1)
H3 = ParagraphStyle("H3", parent=ss["Heading3"], fontName=F_BOLD, fontSize=12.5, leading=17, textColor=AZUL, spaceBefore=12, spaceAfter=6, keepWithNext=1)
NOTA = ParagraphStyle("NOTA", parent=P, fontSize=9.5, leading=13.5, textColor=GRIS)
CELDA = ParagraphStyle("CELDA", parent=P, fontSize=9.3, leading=12.5, alignment=0, spaceAfter=0)
CELDA_B = ParagraphStyle("CELDA_B", parent=CELDA, fontName=F_BOLD, textColor=colors.white)
DEST = ParagraphStyle("DEST", parent=P, leftIndent=10, rightIndent=10, spaceBefore=8, spaceAfter=12, borderPadding=9, backColor=FONDO, borderColor=VERDE, borderWidth=0.6)
TIT_TABLA = ParagraphStyle("TIT_TABLA", parent=P, fontName=F_BOLD, fontSize=10.5, leading=14, textColor=AZUL, alignment=0, spaceBefore=8, spaceAfter=5, keepWithNext=1)
FUENTE = ParagraphStyle("FUENTE", parent=P, fontName=F_ITAL, fontSize=9, leading=12, textColor=GRIS, alignment=0, spaceBefore=4, spaceAfter=12)
TOC1 = ParagraphStyle("TOC1", parent=P, fontSize=11, leading=19, alignment=0, spaceAfter=0)
TOC2 = ParagraphStyle("TOC2", parent=TOC1, leftIndent=18, textColor=GRIS)
IDX = ParagraphStyle("IDX", parent=P, fontSize=10.5, leading=16, alignment=0, spaceAfter=0)
CONT = {"T": 0, "F": 0, "A": 0}

def tabla(datos, anchos):
    t = Table(datos, colWidths=anchos, repeatRows=1, hAlign="LEFT")
    est = [("GRID", (0, 0), (-1, -1), 0.4, LINEA), ("VALIGN", (0, 0), (-1, -1), "TOP"),
           ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
           ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
           ("BACKGROUND", (0, 0), (-1, 0), AZUL)]
    est += [("BACKGROUND", (0, i), (-1, i), FONDO) for i in range(2, len(datos), 2)]
    t.setStyle(TableStyle(est)); return t

def filas(cab, cuerpo):
    return [[Paragraph(x, CELDA_B) for x in cab]] + [[Paragraph(str(c), CELDA) for c in f] for f in cuerpo]

class Marca(Flowable):
    def __init__(self, tipo, texto): super().__init__(); self.tipo = tipo; self.texto = texto
    def wrap(self, *a): return (0, 0)
    def draw(self): self.canv._doctemplate.idx[self.tipo].append((self.texto, self.canv.getPageNumber()))

class TituloIndexado(Paragraph):
    def __init__(self, texto, estilo, tipo): super().__init__(texto, estilo); self._tipo = tipo; self._texto = texto
    def draw(self):
        self.canv._doctemplate.idx[self._tipo].append((self._texto, self.canv.getPageNumber())); super().draw()

def titulo_tabla(texto, S):
    CONT["T"] += 1; S.append(TituloIndexado(f"Tabla {CONT['T']}. {texto}", TIT_TABLA, "T"))

def figura(ruta, texto, fuente_txt, S, ancho, alto):
    CONT["F"] += 1; t = f"Figura {CONT['F']}. {texto}"
    S.append(TituloIndexado(t, ParagraphStyle("TF", parent=TIT_TABLA, alignment=1), "F"))
    S.append(Image(ruta, width=ancho, height=alto))
    S.append(Paragraph("Fuente: " + fuente_txt, ParagraphStyle("FF", parent=FUENTE, alignment=1)))

def fuente(texto): return Paragraph("Fuente: " + texto, FUENTE)

class Indice(Flowable):
    def __init__(self, doc, tipo, vacio): super().__init__(); self.doc = doc; self.tipo = tipo; self.vacio = vacio
    def wrap(self, aw, ah):
        der = ParagraphStyle("der", parent=IDX, alignment=2)
        self.t = Table([[Paragraph(a, IDX), Paragraph(str(b), der)] for a, b in (self.doc.semilla[self.tipo] or [(self.vacio, "")])],
                       colWidths=[aw - 15 * mm, 15 * mm])
        self.t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.3, LINEA), ("VALIGN", (0, 0), (-1, -1), "BOTTOM")]))
        return self.t.wrap(aw, ah)
    def draw(self): self.t.drawOn(self.canv, 0, 0)

class Doc(BaseDocTemplate):
    def handle_documentBegin(self):
        self.idx = {"T": [], "F": [], "A": []}; super().handle_documentBegin()
    def afterFlowable(self, f):
        if isinstance(f, Paragraph) and f.style.name in ("H2", "H3"):
            clave = "h%d" % id(f); self.canv.bookmarkPage(clave)
            self.notify("TOCEntry", (0 if f.style.name == "H2" else 1, f.getPlainText(), self.page, clave))

def generar(salida, meta, cuerpo_fn):
    """meta: dict con rotulo, titulo, subtitulo, ficha [(k, v)], pie, fecha, titulo_pdf."""
    def portada(canv, doc):
        W, H = LETRA; canv.saveState()
        canv.setFillColor(VERDE); canv.rect(0, H - 9 * mm, W, 9 * mm, stroke=0, fill=1)
        canv.setFillColor(AZUL); canv.rect(0, H - 11.5 * mm, W, 2.5 * mm, stroke=0, fill=1)
        if os.path.exists(LOGO_U): canv.drawImage(LOGO_U, MARGEN, H - 46 * mm, width=82 * mm, height=82 * mm * 179 / 669, mask="auto")
        if os.path.exists(LOGO_G): canv.drawImage(LOGO_G, W - MARGEN - 26 * mm, H - 48.5 * mm, width=26 * mm, height=26 * mm, mask="auto")
        canv.setFillColor(GRIS); canv.setFont(F_BOLD, 11)
        canv.drawString(MARGEN, H - 63 * mm, "SEMESTRE PAZ Y REGIÓN 2026B · SEMILLERO DE INVESTIGACIÓN GEOPAV")
        canv.setStrokeColor(VERDE); canv.setLineWidth(2); canv.line(MARGEN, H - 67 * mm, W - MARGEN, H - 67 * mm)
        canv.setFillColor(VERDE); canv.setFont(F_BOLD, 13); canv.drawString(MARGEN, H - 82 * mm, meta["rotulo"])
        tit = Paragraph(meta["titulo"], ParagraphStyle("pt", fontName=F_BOLD, fontSize=26, leading=32, textColor=AZUL))
        w, h = tit.wrap(W - 2 * MARGEN, 100 * mm); tit.drawOn(canv, MARGEN, H - 88 * mm - h)
        sub = Paragraph(meta["subtitulo"], ParagraphStyle("ps", fontName=F_REG, fontSize=14, leading=19, textColor=GRIS))
        w2, h2 = sub.wrap(W - 2 * MARGEN, 30 * mm); sub.drawOn(canv, MARGEN, H - 96 * mm - h - h2)
        t = Table([[Paragraph(f"<b>{k}</b>", CELDA), Paragraph(v, CELDA)] for k, v in meta["ficha"]], colWidths=[52 * mm, W - 2 * MARGEN - 52 * mm])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), FONDO), ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINEA),
                               ("LINEABOVE", (0, 0), (-1, 0), 1, VERDE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        t.wrap(W - 2 * MARGEN, 100 * mm); t.drawOn(canv, MARGEN, 36 * mm)
        canv.setFont(F_REG, 10); canv.setFillColor(GRIS)
        canv.drawString(MARGEN, 22 * mm, "Programa de Ingeniería Civil · Universidad de Ibagué · Ibagué, Tolima")
        canv.drawRightString(W - MARGEN, 22 * mm, meta["fecha"]); canv.restoreState()

    def encabezado(canv, doc):
        W, H = canv._pagesize; canv.saveState()
        if os.path.exists(LOGO_U): canv.drawImage(LOGO_U, MARGEN, H - 22.5 * mm, width=44 * mm, height=44 * mm * 179 / 669, mask="auto")
        if os.path.exists(LOGO_G): canv.drawImage(LOGO_G, W - MARGEN - 12.5 * mm, H - 24 * mm, width=12.5 * mm, height=12.5 * mm, mask="auto")
        canv.setFont(F_REG, 9); canv.setFillColor(GRIS)
        canv.drawRightString(W - MARGEN - 15.5 * mm, H - 17.5 * mm, meta["rotulo"])
        canv.setStrokeColor(VERDE); canv.setLineWidth(1.2); canv.line(MARGEN, H - 26 * mm, W - MARGEN, H - 26 * mm)
        canv.setStrokeColor(LINEA); canv.setLineWidth(0.6); canv.line(MARGEN, 18 * mm, W - MARGEN, 18 * mm)
        canv.drawString(MARGEN, 13 * mm, meta["pie"]); canv.drawRightString(W - MARGEN, 13 * mm, f"Página {doc.page}"); canv.restoreState()

    previo = {"T": [], "F": [], "A": []}
    for _ in range(4):
        CONT.update({"T": 0, "F": 0, "A": 0})
        doc = Doc(salida, pagesize=LETRA, leftMargin=MARGEN, rightMargin=MARGEN, topMargin=32 * mm, bottomMargin=25 * mm,
                  title=meta["titulo_pdf"], author="Semillero de Investigación GEOPAV - Universidad de Ibagué", invariant=1)
        doc.semilla = previo
        fr = Frame(MARGEN, 25 * mm, LETRA[0] - 2 * MARGEN, LETRA[1] - 57 * mm, id="f")
        frh = Frame(MARGEN, 22 * mm, APAIS[0] - 2 * MARGEN, APAIS[1] - 51 * mm, id="fh")
        doc.addPageTemplates([PageTemplate(id="portada", frames=[fr], onPage=portada, pagesize=LETRA),
                              PageTemplate(id="p", frames=[fr], onPage=encabezado, pagesize=LETRA),
                              PageTemplate(id="h", frames=[frh], onPage=encabezado, pagesize=APAIS)])
        toc = TableOfContents(); toc.levelStyles = [TOC1, TOC2]
        pre = [NextPageTemplate("p"), PageBreak(), Paragraph("Tabla de contenido", H1), toc, PageBreak(),
               Paragraph("Índice de tablas", H1), Indice(doc, "T", "Este documento no contiene tablas."), Spacer(1, 16),
               Paragraph("Índice de figuras", H1), Indice(doc, "F", "Este documento no contiene figuras."), Spacer(1, 16),
               Paragraph("Índice de anexos", H1), Indice(doc, "A", "Este documento no contiene anexos."), PageBreak()]
        doc.multiBuild(pre + cuerpo_fn(doc))
        if doc.idx == previo: return doc
        previo = doc.idx
    return doc
