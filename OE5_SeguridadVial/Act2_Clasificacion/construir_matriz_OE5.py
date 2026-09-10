# -*- coding: utf-8 -*-
"""
OE 5 - Actividad 2 (fila 32 del Cronograma)
Clasificacion vehicular del TPDA y depuracion del flujo de carga pesada.
Producto: matriz_aforos_clasificada_OE5.xlsx

Semillero de Investigacion GEOPAV - Universidad de Ibague - Paz y Region 2026B

Consume unicamente los CSV de Act1_Aforos/, producidos por la Act 1.
No recalcula nada que ya este publicado: lee y clasifica.
"""

import csv
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# El script vive en Act2_Clasificacion/. Los CSV de entrada los produce la Act 1 y
# viven en Act1_Aforos/; la salida se escribe aqui mismo.
BASE = os.path.dirname(os.path.abspath(__file__))
OE5 = os.path.dirname(BASE)
DATOS = os.path.join(OE5, "Act1_Aforos")
SALIDA = os.path.join(BASE, "matriz_aforos_clasificada_OE5.xlsx")

AZUL = "193F77"      # institucional Universidad de Ibague
VERDE = "0F7B55"     # GEOPAV
GRIS = "F1F5F9"
AMARILLO = "FFFF00"

F_TIT = Font(name="Arial", size=14, bold=True, color=AZUL)
F_SUB = Font(name="Arial", size=10, italic=True, color="475569")
F_CAB = Font(name="Arial", size=9, bold=True, color="FFFFFF")
F_TXT = Font(name="Arial", size=9)
F_NEG = Font(name="Arial", size=9, bold=True)
F_ENT = Font(name="Arial", size=9, color="0000FF")     # entrada / hipotesis
F_NOTA = Font(name="Arial", size=8, italic=True, color="475569")
FILL_CAB = PatternFill("solid", fgColor=AZUL)
FILL_SEC = PatternFill("solid", fgColor=GRIS)
FILL_HIP = PatternFill("solid", fgColor=AMARILLO)
BORDE = Border(*[Side(style="thin", color="CBD5E1")] * 4)


def leer_csv(nombre):
    with open(os.path.join(DATOS, nombre), encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


def num(s):
    """'4.954,3' -> 4954.3 ; '' -> None"""
    if s is None or str(s).strip() == "":
        return None
    return float(str(s).replace(".", "").replace(",", "."))


def cab(ws, fila, titulos, anchos=None):
    for i, t in enumerate(titulos, start=1):
        c = ws.cell(row=fila, column=i, value=t)
        c.font, c.fill, c.border = F_CAB, FILL_CAB, BORDE
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    if anchos:
        for i, a in enumerate(anchos, start=1):
            ws.column_dimensions[get_column_letter(i)].width = a
    ws.row_dimensions[fila].height = 30


def titulo(ws, texto, subtitulo):
    ws["A1"] = texto
    ws["A1"].font = F_TIT
    ws["A2"] = subtitulo
    ws["A2"].font = F_SUB


# ---------------------------------------------------------------- datos
hist = leer_csv("tpd_historico_corredor.csv")
caj = leer_csv("tpd_2019_peaje_cajamarca.csv")
coc = leer_csv("aforos_cocora_mensual.csv")

wb = openpyxl.Workbook()

# ============================================================ 1. Metodo
ws = wb.active
ws.title = "1. Metodo"
titulo(ws, "Matriz de aforos clasificada - OE 5, Actividad 2",
       "Clasificacion vehicular del TPDA y depuracion del flujo de carga pesada "
       "| Semillero GEOPAV | Corredor Ibague - Calarca, Ruta Nacional 40")

filas = [
    ("", ""),
    ("MARCAS DE ORIGEN", ""),
    ("F", "Dato tomado de una fuente externa, citada."),
    ("CP", "Calculo propio del semillero, reproducible por la formula de la celda."),
    ("H", "Hipotesis adoptada. Celda con fondo amarillo y texto azul."),
    ("", ""),
    ("FUENTES", ""),
    ("Serie historica TPD 1997-2018", "INVIAS, idFile=30450. Extraida por Scripts/extraccion_TPD_INVIAS.py  [F]"),
    ("Serie historica TPD 2019", "INVIAS, idFile=1678. Peaje Cajamarca, PR 24+020  [F]"),
    ("Trafico Vehicular ANI", "datos.gov.co 8yi9-t44c. Peaje Cocora, K 13+750  [F]"),
    ("", ""),
    ("HOMOLOGACION DE CLASES  [H]", ""),
    ("Livianos", "Peajes: categoria I. Serie por estacion: 'autos'."),
    ("Intermedios", "Peajes: categoria II (buses y camion de 2 ejes). Serie por estacion: 'buses'."),
    ("Carga pesada", "Peajes: categorias III a VII (3 o mas ejes). Serie por estacion: 'camiones'."),
    ("", ""),
    ("LIMITACION DE LA HOMOLOGACION", ""),
    ("", "La serie por estacion publica solo tres porcentajes (autos-buses-camiones) y su clase"),
    ("", "'camiones' INCLUYE los de dos ejes, que en el peaje caen en categoria II. Por eso la"),
    ("", "participacion de carga pesada de la serie por estacion es sistematicamente MAYOR que la"),
    ("", "del peaje. Las dos lecturas se publican por separado y no se promedian."),
    ("", ""),
    ("ADVERTENCIA - TRES PUNTOS DE MEDICION DISTINTOS  [F]", ""),
    ("Estacion 244 INVIAS", "Aforo de tramo Calarca - Cajamarca, 45 km. Es el paso de La Linea."),
    ("Peaje Cajamarca", "PR 24+020 carretera Armenia - Ibague. Administra INVIAS."),
    ("Peaje Cocora", "K 13+750 Segunda Calzada Ibague - Cajamarca. Administra la concesion APP GICA (ANI)."),
    ("", "Cocora y Cajamarca estan separados unos 10 km. Cocora, mas abajo, capta trafico local que"),
    ("", "no sube al paso. Las series NO se empalman en una sola linea de tiempo: cada punto de"),
    ("", "medicion se reporta por separado y la comparacion entre ellos se declara como tal."),
    ("", ""),
    ("HITO QUE PARTE LA SERIE  [F]", ""),
    ("", "El Tunel de La Linea entro en operacion el 4 de septiembre de 2020, con 8,6 km. Todo lo"),
    ("", "anterior a esa fecha describe un corredor distinto del actual."),
]
r = 4
for a, b in filas:
    ws.cell(row=r, column=1, value=a).font = F_NEG if b == "" and a else F_TXT
    ws.cell(row=r, column=2, value=b).font = F_TXT
    if a and b == "":
        ws.cell(row=r, column=1).fill = FILL_SEC
    r += 1
ws.column_dimensions["A"].width = 34
ws.column_dimensions["B"].width = 100

# ================================================ 2. Serie INVIAS por estacion
ws = wb.create_sheet("2. Serie INVIAS estacion")
titulo(ws, "Serie historica de TPD por estacion de aforo - INVIAS 1997-2018",
       "Columnas A-L: dato de la fuente [F]. Columnas M-P: clasificacion [CP], calculadas por formula.")
cab(ws, 4, ["Estacion", "Depto", "Sector", "Codigo via", "L (km)",
            "En corredor", "Anio", "TPD total", "% autos", "% buses", "% camiones",
            "TPD livianos", "TPD intermedios", "TPD carga pesada", "Participacion pesada"],
    [9, 10, 24, 11, 8, 11, 7, 11, 9, 9, 11, 13, 15, 16, 18])

r = 5
for f in hist:
    ws.cell(row=r, column=1, value=int(f["estacion"])).font = F_TXT
    ws.cell(row=r, column=2, value=f["departamento"]).font = F_TXT
    ws.cell(row=r, column=3, value=f["sector"]).font = F_TXT
    ws.cell(row=r, column=4, value=f["codigo_via"]).font = F_TXT
    ws.cell(row=r, column=5, value=int(f["longitud_km"])).font = F_TXT
    ws.cell(row=r, column=6, value=f["en_corredor_portales"]).font = F_TXT
    ws.cell(row=r, column=7, value=int(f["anio"])).font = F_TXT
    ws.cell(row=r, column=8, value=int(f["tpd"])).font = F_TXT
    for col, campo in ((9, "pct_autos"), (10, "pct_buses"), (11, "pct_camiones")):
        v = f[campo]
        ws.cell(row=r, column=col, value=int(v) if v else None).font = F_TXT
    # clasificacion por formula
    ws.cell(row=r, column=12, value=f"=IF(I{r}=\"\",\"\",ROUND($H{r}*I{r}/100,0))").font = F_TXT
    ws.cell(row=r, column=13, value=f"=IF(J{r}=\"\",\"\",ROUND($H{r}*J{r}/100,0))").font = F_TXT
    ws.cell(row=r, column=14, value=f"=IF(K{r}=\"\",\"\",ROUND($H{r}*K{r}/100,0))").font = F_TXT
    c = ws.cell(row=r, column=15, value=f"=IF(K{r}=\"\",\"\",K{r}/100)")
    c.font, c.number_format = F_TXT, "0.0%"
    for col in range(1, 16):
        ws.cell(row=r, column=col).border = BORDE
    r += 1
fin_hist = r - 1
ws.cell(row=r + 1, column=1,
        value="La clase 'camiones' de esta fuente incluye los de dos ejes: su participacion no es "
              "comparable con la categoria III+ de los peajes.").font = F_NOTA
ws.freeze_panes = "A5"

# ================================================ 3. Peaje Cajamarca 2019
ws = wb.create_sheet("3. Peaje Cajamarca 2019")
titulo(ws, "Aforo mensual por categoria tarifaria - Peaje Cajamarca (INVIAS), 2019",
       "Columnas A-F: dato de la fuente [F]. Columnas G-J: clasificacion [CP].")
cab(ws, 4, ["Mes", "Dias", "Total", "Cat I livianos", "Cat II intermedios",
            "Cat III+ carga pesada", "TPD total", "TPD livianos", "TPD carga pesada",
            "Participacion pesada"],
    [10, 7, 12, 14, 16, 19, 12, 13, 16, 18])
r = 5
for f in caj:
    ws.cell(row=r, column=1, value=f["mes"]).font = F_TXT
    ws.cell(row=r, column=2, value=int(f["dias"])).font = F_TXT
    ws.cell(row=r, column=3, value=f"=SUM(D{r}:F{r})").font = F_TXT
    ws.cell(row=r, column=4, value=int(f["livianos"])).font = F_TXT
    ws.cell(row=r, column=5, value=int(f["intermedios"])).font = F_TXT
    ws.cell(row=r, column=6, value=int(f["pesados"])).font = F_TXT
    ws.cell(row=r, column=7, value=f"=ROUND(C{r}/B{r},0)").font = F_TXT
    ws.cell(row=r, column=8, value=f"=ROUND(D{r}/B{r},0)").font = F_TXT
    ws.cell(row=r, column=9, value=f"=ROUND(F{r}/B{r},0)").font = F_TXT
    c = ws.cell(row=r, column=10, value=f"=F{r}/C{r}")
    c.font, c.number_format = F_TXT, "0.0%"
    for col in range(1, 11):
        ws.cell(row=r, column=col).border = BORDE
    r += 1
tot_caj = r
ws.cell(row=r, column=1, value="AÑO 2019").font = F_NEG
for col, letra in ((2, "B"), (3, "C"), (4, "D"), (5, "E"), (6, "F")):
    c = ws.cell(row=r, column=col, value=f"=SUM({letra}5:{letra}{r-1})")
    c.font, c.fill, c.border = F_NEG, FILL_SEC, BORDE
ws.cell(row=r, column=7, value=f"=ROUND(C{r}/B{r},0)").font = F_NEG
ws.cell(row=r, column=8, value=f"=ROUND(D{r}/B{r},0)").font = F_NEG
ws.cell(row=r, column=9, value=f"=ROUND(F{r}/B{r},0)").font = F_NEG
c = ws.cell(row=r, column=10, value=f"=F{r}/C{r}")
c.font, c.number_format = F_NEG, "0.0%"
for col in range(1, 11):
    ws.cell(row=r, column=col).fill = FILL_SEC
    ws.cell(row=r, column=col).border = BORDE
ws.freeze_panes = "A5"

# ================================================ 4. Peaje Cocora
ws = wb.create_sheet("4. Peaje Cocora 21-26")
titulo(ws, "Aforo mensual por categoria - Peaje Cocora (concesion APP GICA / ANI), oct 2021 - may 2026",
       "Columnas A-G: dato de la fuente [F]. Columnas H-K: clasificacion [CP].")
cab(ws, 4, ["Mes", "Dias", "Total", "Livianos", "Buses (Cat II)", "Carga pesada (Cat III+)",
            "Otros", "TPD total", "TPD livianos", "TPD carga pesada", "Participacion pesada"],
    [10, 7, 12, 12, 14, 20, 9, 12, 13, 16, 18])
r = 5
for f in coc:
    ws.cell(row=r, column=1, value=f["mes"]).font = F_TXT
    ws.cell(row=r, column=2, value=int(f["dias"])).font = F_TXT
    ws.cell(row=r, column=3, value=f"=SUM(D{r}:G{r})").font = F_TXT
    ws.cell(row=r, column=4, value=int(f["livianos"])).font = F_TXT
    ws.cell(row=r, column=5, value=int(f["buses"])).font = F_TXT
    ws.cell(row=r, column=6, value=int(f["pesados"])).font = F_TXT
    ws.cell(row=r, column=7, value=int(f["otros"])).font = F_TXT
    ws.cell(row=r, column=8, value=f"=ROUND(C{r}/B{r},0)").font = F_TXT
    ws.cell(row=r, column=9, value=f"=ROUND(D{r}/B{r},0)").font = F_TXT
    ws.cell(row=r, column=10, value=f"=ROUND(F{r}/B{r},0)").font = F_TXT
    c = ws.cell(row=r, column=11, value=f"=F{r}/C{r}")
    c.font, c.number_format = F_TXT, "0.0%"
    for col in range(1, 12):
        ws.cell(row=r, column=col).border = BORDE
    r += 1
fin_coc = r - 1
ini_12 = fin_coc - 11
ws.cell(row=r, column=1, value="ULT. 12 MESES").font = F_NEG
for col, letra in ((2, "B"), (3, "C"), (4, "D"), (5, "E"), (6, "F"), (7, "G")):
    c = ws.cell(row=r, column=col, value=f"=SUM({letra}{ini_12}:{letra}{fin_coc})")
    c.font, c.fill, c.border = F_NEG, FILL_SEC, BORDE
ws.cell(row=r, column=8, value=f"=ROUND(C{r}/B{r},0)").font = F_NEG
ws.cell(row=r, column=9, value=f"=ROUND(D{r}/B{r},0)").font = F_NEG
ws.cell(row=r, column=10, value=f"=ROUND(F{r}/B{r},0)").font = F_NEG
c = ws.cell(row=r, column=11, value=f"=F{r}/C{r}")
c.font, c.number_format = F_NEG, "0.0%"
for col in range(1, 12):
    ws.cell(row=r, column=col).fill = FILL_SEC
    ws.cell(row=r, column=col).border = BORDE
tot_coc = r
ws.cell(row=r + 2, column=1,
        value="La columna 'Otros' solo tiene valor en oct-dic 2021 y se suma al total sin "
              "clasificar: la fuente no dice que categoria es.").font = F_NOTA
ws.freeze_panes = "A5"

# ================================================ 5. Matriz consolidada
ws = wb.create_sheet("5. Matriz consolidada")
titulo(ws, "Matriz de aforos clasificada - TPD por clase y punto de medicion",
       "Toda celda de esta hoja es una referencia [CP] a las hojas 2, 3 y 4. No hay ningun numero escrito a mano.")
cab(ws, 4, ["Punto de medicion", "Administra", "Ubicacion", "Periodo",
            "TPD total", "TPD livianos", "TPD intermedios", "TPD carga pesada",
            "Participacion pesada", "Base de la clasificacion"],
    [24, 16, 46, 19, 11, 13, 16, 17, 19, 46])

# estacion 244, media 2015-2018 -> localizar filas
filas244 = [i for i, f in enumerate(hist) if f["estacion"] == "244" and 2015 <= int(f["anio"]) <= 2018]
r244 = [5 + i for i in filas244]
filas243 = [i for i, f in enumerate(hist) if f["estacion"] == "243" and 2015 <= int(f["anio"]) <= 2018]
r243 = [5 + i for i in filas243]


def rango(rs, col):
    return f"'2. Serie INVIAS estacion'!{col}{rs[0]}:{col}{rs[-1]}"


r = 5
ws.cell(row=r, column=1, value="Estacion 244 INVIAS").font = F_NEG
ws.cell(row=r, column=2, value="INVIAS").font = F_TXT
ws.cell(row=r, column=3, value="Tramo Calarca - Cajamarca (45 km) - el paso").font = F_TXT
ws.cell(row=r, column=4, value="Media 2015-2018").font = F_TXT
ws.cell(row=r, column=5, value=f"=ROUND(AVERAGE({rango(r244,'H')}),0)").font = F_TXT
ws.cell(row=r, column=6, value=f"=ROUND(AVERAGE({rango(r244,'L')}),0)").font = F_TXT
ws.cell(row=r, column=7, value=f"=ROUND(AVERAGE({rango(r244,'M')}),0)").font = F_TXT
ws.cell(row=r, column=8, value=f"=ROUND(AVERAGE({rango(r244,'N')}),0)").font = F_TXT
ws.cell(row=r, column=9, value=f"=H{r}/E{r}").number_format = "0.0%"
ws.cell(row=r, column=10, value="Composicion % de la fuente; 'camiones' incluye 2 ejes").font = F_TXT

r = 6
ws.cell(row=r, column=1, value="Estacion 243 INVIAS").font = F_NEG
ws.cell(row=r, column=2, value="INVIAS").font = F_TXT
ws.cell(row=r, column=3, value="Tramo Cajamarca - Ibague (29 km)").font = F_TXT
ws.cell(row=r, column=4, value="Media 2015-2017").font = F_TXT
ws.cell(row=r, column=5, value=f"=ROUND(AVERAGE({rango(r243,'H')}),0)").font = F_TXT
ws.cell(row=r, column=6, value=f"=ROUND(AVERAGE({rango(r243,'L')}),0)").font = F_TXT
ws.cell(row=r, column=7, value=f"=ROUND(AVERAGE({rango(r243,'M')}),0)").font = F_TXT
ws.cell(row=r, column=8, value=f"=ROUND(AVERAGE({rango(r243,'N')}),0)").font = F_TXT
ws.cell(row=r, column=9, value=f"=H{r}/E{r}").number_format = "0.0%"
ws.cell(row=r, column=10, value="Composicion % de la fuente; 'camiones' incluye 2 ejes").font = F_TXT

r = 7
ws.cell(row=r, column=1, value="Peaje Cajamarca").font = F_NEG
ws.cell(row=r, column=2, value="INVIAS").font = F_TXT
ws.cell(row=r, column=3, value="PR 24+020 Armenia - Ibague").font = F_TXT
ws.cell(row=r, column=4, value="Anio 2019").font = F_TXT
ws.cell(row=r, column=5, value=f"='3. Peaje Cajamarca 2019'!G{tot_caj}").font = F_TXT
ws.cell(row=r, column=6, value=f"='3. Peaje Cajamarca 2019'!H{tot_caj}").font = F_TXT
ws.cell(row=r, column=7, value=f"=ROUND('3. Peaje Cajamarca 2019'!E{tot_caj}/'3. Peaje Cajamarca 2019'!B{tot_caj},0)").font = F_TXT
ws.cell(row=r, column=8, value=f"='3. Peaje Cajamarca 2019'!I{tot_caj}").font = F_TXT
ws.cell(row=r, column=9, value=f"=H{r}/E{r}").number_format = "0.0%"
ws.cell(row=r, column=10, value="Categoria tarifaria III+ = 3 o mas ejes").font = F_TXT

r = 8
ws.cell(row=r, column=1, value="Peaje Cocora").font = F_NEG
ws.cell(row=r, column=2, value="APP GICA (ANI)").font = F_TXT
ws.cell(row=r, column=3, value="K 13+750 Segunda Calzada Ibague - Cajamarca").font = F_TXT
ws.cell(row=r, column=4, value="Jun 2025 - may 2026").font = F_TXT
ws.cell(row=r, column=5, value=f"='4. Peaje Cocora 21-26'!H{tot_coc}").font = F_TXT
ws.cell(row=r, column=6, value=f"='4. Peaje Cocora 21-26'!I{tot_coc}").font = F_TXT
ws.cell(row=r, column=7, value=f"=ROUND('4. Peaje Cocora 21-26'!E{tot_coc}/'4. Peaje Cocora 21-26'!B{tot_coc},0)").font = F_TXT
ws.cell(row=r, column=8, value=f"='4. Peaje Cocora 21-26'!J{tot_coc}").font = F_TXT
ws.cell(row=r, column=9, value=f"=H{r}/E{r}").number_format = "0.0%"
ws.cell(row=r, column=10, value="Categoria tarifaria III+ = 3 o mas ejes").font = F_TXT

for rr in range(5, 9):
    for col in range(1, 11):
        ws.cell(row=rr, column=col).border = BORDE
        if ws.cell(row=rr, column=col).font is None:
            ws.cell(row=rr, column=col).font = F_TXT
    ws.cell(row=rr, column=9).font = F_TXT

nota = [
    "",
    "COMO SE LEE ESTA MATRIZ",
    "Las filas 5 y 6 miden un TRAMO completo y clasifican por composicion porcentual; las filas 7 y 8 miden un",
    "PUNTO y clasifican por categoria tarifaria. Por eso la participacion de carga pesada de las dos primeras es",
    "mayor: su clase 'camiones' incluye los de dos ejes, que en el peaje son categoria II.",
    "",
    "Las cuatro filas NO forman una serie temporal. Son cuatro mediciones distintas del mismo corredor, en puntos",
    "y con criterios distintos. Cualquier comparacion entre filas debe declarar esa diferencia.",
]
r = 11
for t in nota:
    c = ws.cell(row=r, column=1, value=t)
    c.font = F_NEG if t.isupper() and t else F_NOTA
    r += 1

# ================================================ 6. Depuracion carga pesada
ws = wb.create_sheet("6. Depuracion pesada")
titulo(ws, "Depuracion del flujo de carga pesada",
       "Aisla el flujo de carga pesada del corredor y estima la porcion captable por la Ferropista. "
       "Celdas amarillas = hipotesis editables.")

r = 4
ws.cell(row=r, column=1, value="ENTRADAS").font = F_NEG
ws.cell(row=r, column=1).fill = FILL_SEC
r = 5
entradas = [
    ("Punto de medicion adoptado como proxy del paso", "Peaje Cajamarca", "H",
     "Peaje Cajamarca (PR 24+020). Esta mas arriba que Cocora y capta mejor lo que sube al paso."),
    ("TPD de carga pesada, peaje Cajamarca 2019", "='5. Matriz consolidada'!H7", "CP",
     "Categoria III+ del aforo de INVIAS."),
    ("TPD de carga pesada, peaje Cocora jun25-may26", "='5. Matriz consolidada'!H8", "CP",
     "Categoria III+ del aforo de la ANI."),
    ("TPD de carga pesada, estacion 244 media 2015-2018", "='5. Matriz consolidada'!H5", "CP",
     "Incluye camiones de dos ejes: cota superior."),
    ("Captacion prevista de vehiculos grandes", 0.90, "F",
     "Ponencia ARCS/UC Consult, dia. 10. Es cifra del proponente, no auditada."),
    ("Longitud del corredor entre portales (km)", 74, "F",
     "INVIAS: 29 km estacion 243 + 45 km estacion 244."),
]
for etiqueta, valor, marca, fuente in entradas:
    ws.cell(row=r, column=1, value=etiqueta).font = F_TXT
    c = ws.cell(row=r, column=2, value=valor)
    if marca == "H":
        c.font, c.fill = F_ENT, FILL_HIP
    elif marca == "F":
        c.font, c.fill = F_ENT, FILL_HIP
    else:
        c.font = F_TXT
    if etiqueta.startswith("Captacion"):
        c.number_format = "0%"
    ws.cell(row=r, column=3, value=marca).font = F_NEG
    ws.cell(row=r, column=4, value=fuente).font = F_NOTA
    for col in range(1, 5):
        ws.cell(row=r, column=col).border = BORDE
    r += 1

r += 1
ws.cell(row=r, column=1, value="RESULTADOS  [CP]").font = F_NEG
ws.cell(row=r, column=1).fill = FILL_SEC
r += 1
resultados = [
    ("Vehiculos-km diarios de carga pesada en el corredor", "=B6*$B$10",
     "TPD pesada x longitud del corredor."),
    ("Vehiculos-km anuales de carga pesada", "=B{r0}*365".format(r0=r),
     "Exposicion anual del grupo que la Ferropista captaria."),
    ("Vehiculos-km anuales evitados con la captacion prevista", "=B{r1}*$B$9".format(r1=r + 1),
     "Aplicando la captacion de la ponencia. Es una estimacion condicionada, no un pronostico."),
    ("Diferencia entre puntos de medicion (Cajamarca 2019 - Cocora hoy)", "=B6-B7",
     "Cuanta carga pesada mide de mas el punto alto. NO es una caida temporal: son dos peajes."),
    ("Cota superior segun la estacion 244", "=B8",
     "Incluye camiones de 2 ejes. Sirve de techo, no de valor central."),
]
for etiqueta, formula, nota_txt in resultados:
    ws.cell(row=r, column=1, value=etiqueta).font = F_TXT
    ws.cell(row=r, column=2, value=formula).font = F_TXT
    ws.cell(row=r, column=2).number_format = "#,##0"
    ws.cell(row=r, column=3, value="CP").font = F_NEG
    ws.cell(row=r, column=4, value=nota_txt).font = F_NOTA
    for col in range(1, 5):
        ws.cell(row=r, column=col).border = BORDE
    r += 1

r += 1
cierre = [
    "QUE PUEDE AFIRMARSE CON ESTA MATRIZ",
    "El volumen de carga pesada del corredor esta MEDIDO en peaje, no supuesto, en dos puntos y dos periodos.",
    "La exposicion anual en vehiculos-kilometro de ese grupo es calculable y reproducible.",
    "",
    "QUE NO PUEDE AFIRMARSE",
    "Que la carga pesada haya caido entre 2019 y hoy: los dos numeros vienen de peajes distintos, separados 10 km,",
    "y el de abajo capta trafico local. Homologar los puntos de medicion es requisito antes de cualquier serie unica.",
    "Cuantos vehiculos dejarian de subir: la captacion del 90 % es cifra del proponente y entra como hipotesis.",
]
for t in cierre:
    c = ws.cell(row=r, column=1, value=t)
    c.font = F_NEG if t.isupper() and t else F_NOTA
    r += 1

ws.column_dimensions["A"].width = 54
ws.column_dimensions["B"].width = 16
ws.column_dimensions["C"].width = 6
ws.column_dimensions["D"].width = 74

wb.save(SALIDA)
print("escrito:", SALIDA)
print("hojas:", wb.sheetnames)
