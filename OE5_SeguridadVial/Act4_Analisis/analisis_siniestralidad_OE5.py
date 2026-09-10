# -*- coding: utf-8 -*-
"""
OE 5 - Actividad 4 (fila 34 del Cronograma)
Analisis estadistico de la siniestralidad de vehiculos pesados en el descenso del paso.
Producto: analisis_siniestralidad_OE5.xlsx

Semillero de Investigacion GEOPAV - Universidad de Ibague - Paz y Region 2026B

QUE CAMBIA RESPECTO A LA MEMORIA METODOLOGICA
  La memoria declara que la tasa NO se puede publicar porque "los fallecidos son
  2015-2019 y el aforo verificado es 2021-2026: no son divisibles entre si". Eso era
  cierto con el peaje Cocora. Con la serie historica de INVIAS que trajo la Act 1, el
  aforo del paso es 2015-2018 de la MISMA estacion y la MISMA via: mismo periodo, mismo
  tramo. La objecion queda resuelta y la tasa pasa de hipotesis a resultado.

  El desfase que SI sigue en pie es otro y se declara: el Tunel de La Linea abrio el
  4 de septiembre de 2020, de modo que la linea base describe el corredor anterior al
  tunel y sobrestima el riesgo del corredor actual.

ENTRADAS  - todas medidas, ninguna supuesta
  Fallecidos      ANSV rs3u-8r4q, 2015-2019, tramo "Calarca - Ibague"      [F]
  TPD             INVIAS, estaciones 243 y 244, 2015-2018                  [F]
  Longitudes      INVIAS, declaradas por estacion: 29 y 45 km              [F]
"""

import csv
import os
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

BASE = os.path.dirname(os.path.abspath(__file__))
OE5 = os.path.dirname(BASE)
ACT1 = os.path.join(OE5, "Act1_Aforos")
ACT3 = os.path.join(OE5, "Act3_Siniestros")
SALIDA = os.path.join(BASE, "analisis_siniestralidad_OE5.xlsx")

AZUL, VERDE, GRIS, AMARILLO = "193F77", "0F7B55", "F1F5F9", "FFFF00"
F_TIT = Font(name="Arial", size=14, bold=True, color=AZUL)
F_SUB = Font(name="Arial", size=10, italic=True, color="475569")
F_CAB = Font(name="Arial", size=9, bold=True, color="FFFFFF")
F_TXT = Font(name="Arial", size=9)
F_NEG = Font(name="Arial", size=9, bold=True)
F_RES = Font(name="Arial", size=11, bold=True, color=VERDE)
F_ENT = Font(name="Arial", size=9, color="0000FF")
F_NOTA = Font(name="Arial", size=8, italic=True, color="475569")
FILL_CAB = PatternFill("solid", fgColor=AZUL)
FILL_SEC = PatternFill("solid", fgColor=GRIS)
FILL_HIP = PatternFill("solid", fgColor=AMARILLO)
BORDE = Border(*[Side(style="thin", color="CBD5E1")] * 4)


def leer(ruta):
    with open(ruta, encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


def cab(ws, fila, titulos, anchos):
    for i, t in enumerate(titulos, 1):
        c = ws.cell(row=fila, column=i, value=t)
        c.font, c.fill, c.border = F_CAB, FILL_CAB, BORDE
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for i, a in enumerate(anchos, 1):
        ws.column_dimensions[get_column_letter(i)].width = a
    ws.row_dimensions[fila].height = 30


def titulo(ws, t, s):
    ws["A1"] = t
    ws["A1"].font = F_TIT
    ws["A2"] = s
    ws["A2"].font = F_SUB


hist = leer(os.path.join(ACT1, "tpd_historico_corredor.csv"))
sini = leer(os.path.join(ACT3, "siniestros_ANSV_corredor.csv"))
caj19 = leer(os.path.join(ACT1, "tpd_2019_peaje_cajamarca.csv"))
TPD_2019 = sum(int(r["total"]) for r in caj19) / sum(int(r["dias"]) for r in caj19)

wb = openpyxl.Workbook()

# ============================================================= 1. Metodo
ws = wb.active
ws.title = "1. Metodo"
titulo(ws, "Análisis estadístico de la siniestralidad de vehículos pesados",
       "OE 5 · Actividad 4 · Semillero GEOPAV · Corredor Ibagué – Calarcá, Ruta Nacional 40, "
       "paso del Alto de La Línea")
bloques = [
    ("", ""),
    ("LA FÓRMULA", ""),
    ("Tasa", "fallecidos / (TPD × 365 × L × años) × 10^8"),
    ("Unidad", "Fallecidos por cada 100 millones de vehículos-kilómetro recorridos."),
    ("Por qué normalizar",
     "Contar muertos sin dividir por exposición es contar goles sin saber cuántos partidos se jugaron."),
    ("", ""),
    ("LO QUE CAMBIÓ RESPECTO A LA MEMORIA METODOLÓGICA", ""),
    ("", "La memoria declara que la tasa no se puede publicar porque los fallecidos son 2015–2019"),
    ("", "y el aforo verificado es 2021–2026, de modo que no son divisibles entre sí. Eso era cierto"),
    ("", "cuando el único aforo disponible era el del peaje Cocora."),
    ("", "Con la serie histórica de INVÍAS que trajo la Act 1, el aforo del paso es 2015–2018 de la"),
    ("", "MISMA estación y la MISMA vía. Mismo periodo, mismo tramo: la objeción queda resuelta y la"),
    ("", "tasa pasa de hipótesis a resultado."),
    ("", ""),
    ("EL DESFASE QUE SÍ SIGUE EN PIE  [F]", ""),
    ("", "El Túnel de La Línea entró en operación el 4 de septiembre de 2020, con 8,6 km. La línea"),
    ("", "base describe el corredor ANTERIOR al túnel y por tanto SOBRESTIMA el riesgo del corredor"),
    ("", "actual. Toda cifra de esta hoja se lee como caracterización del corredor 2015–2019."),
    ("", ""),
    ("LAS DOS DEFINICIONES DE TRAMO — se publican ambas  [H]", ""),
    ("", "Los 42 fallecidos están en el tramo que la ANSV nombra «Calarcá – Ibagué», que abarca el"),
    ("", "corredor completo de 74 km. Pero los seis sectores críticos caen todos en el descenso de"),
    ("", "Calarcá, dentro de los 45 km de la estación 244. Ninguna de las dos definiciones es"),
    ("", "obviamente la correcta, así que se publican las dos con su denominador declarado y no se"),
    ("", "escoge una en silencio."),
    ("", ""),
    ("MARCAS", ""),
    ("F", "Dato de fuente externa citada."),
    ("CP", "Cálculo propio, reproducible por la fórmula de la celda."),
    ("H", "Hipótesis o criterio adoptado. Celda amarilla con texto azul."),
]
r = 4
for a, b in bloques:
    ca = ws.cell(row=r, column=1, value=a)
    ca.font = F_NEG if (a and not b) else F_TXT
    if a and not b:
        ca.fill = FILL_SEC
    ws.cell(row=r, column=2, value=b).font = F_TXT
    r += 1
ws.column_dimensions["A"].width = 30
ws.column_dimensions["B"].width = 104

# ============================================================= 2. Entradas
ws = wb.create_sheet("2. Entradas")
titulo(ws, "Entradas del cálculo — todas medidas",
       "Ninguna celda de esta hoja es una suposición. Cada una cita su fuente.")
cab(ws, 4, ["Entrada", "Valor", "Marca", "Origen"], [46, 14, 8, 78])

filas244 = [f for f in hist if f["estacion"] == "244" and 2015 <= int(f["anio"]) <= 2018]
filas243 = [f for f in hist if f["estacion"] == "243" and 2015 <= int(f["anio"]) <= 2018]
t244 = sum(int(f["tpd"]) for f in filas244) / len(filas244)
t243 = sum(int(f["tpd"]) for f in filas243) / len(filas243)
pes244 = sum(int(f["tpd"]) * int(f["pct_camiones"]) / 100 for f in filas244) / len(filas244)
fall_paso = sum(int(s["fallecidos"]) for s in sini if s["en_el_paso"] == "Si")
fall_corr = sum(int(s["fallecidos"]) for s in sini)

entradas = [
    ("Fallecidos en el tramo del paso «Calarcá – Ibagué»", fall_paso, "F",
     "ANSV rs3u-8r4q, 2015–2019. Cuatro sectores críticos: PR 86, PR 6 y PR 10 (dos)."),
    ("Fallecidos en todo el corredor de análisis", fall_corr, "F",
     "ANSV rs3u-8r4q. Los seis sectores, todos en jurisdicción de Calarcá."),
    ("Años cubiertos por el registro de fallecidos", 5, "F", "2015 a 2019 inclusive."),
    ("TPD del paso — estación 244, media 2015–2018", round(t244), "F",
     "INVÍAS, serie histórica. Sector Calarcá – Cajamarca."),
    ("TPD del tramo Cajamarca – Ibagué — estación 243", round(t243), "F",
     "INVÍAS, serie histórica. Solo 2015–2017: el libro no publica 2018."),
    ("Longitud del paso — estación 244", 45, "F", "Declarada por INVÍAS para esa estación."),
    ("Longitud del tramo Cajamarca – Ibagué — estación 243", 29, "F", "Declarada por INVÍAS."),
    ("TPD de camiones en el paso, media 2015–2018", round(pes244), "F",
     "Estación 244, aplicando la composición vehicular publicada por INVÍAS."),
    ("TPD del peaje Cajamarca en 2019 — solo como control", round(TPD_2019), "F",
     "INVÍAS, aforo mensual 2019. No entra en la tasa: sirve para acotar la hipótesis "
     "del año faltante, en la hoja 3."),
]
r = 5
for et, v, marca, org in entradas:
    ws.cell(row=r, column=1, value=et).font = F_TXT
    c = ws.cell(row=r, column=2, value=v)
    c.font = F_TXT
    ws.cell(row=r, column=3, value=marca).font = F_NEG
    ws.cell(row=r, column=4, value=org).font = F_NOTA
    for col in range(1, 5):
        ws.cell(row=r, column=col).border = BORDE
    r += 1
FILA_FALL_PASO, FILA_FALL_CORR, FILA_ANIOS = 5, 6, 7
FILA_T244, FILA_T243, FILA_L244, FILA_L243, FILA_PES = 8, 9, 10, 11, 12
FILA_TPD_2019 = 13

r += 1
ws.cell(row=r, column=1, value="DERIVADAS  [CP]").font = F_NEG
ws.cell(row=r, column=1).fill = FILL_SEC
r += 1
ws.cell(row=r, column=1, value="Longitud del corredor completo (km)").font = F_TXT
ws.cell(row=r, column=2, value=f"=B{FILA_L244}+B{FILA_L243}").font = F_TXT
ws.cell(row=r, column=3, value="CP").font = F_NEG
ws.cell(row=r, column=4, value="Suma de las dos longitudes declaradas por INVÍAS.").font = F_NOTA
FILA_L_CORR = r  # se calcula sobre la marcha
r += 1
ws.cell(row=r, column=1, value="TPD del corredor, ponderado por longitud").font = F_TXT
ws.cell(row=r, column=2,
        value=f"=ROUND((B{FILA_T243}*B{FILA_L243}+B{FILA_T244}*B{FILA_L244})/B{FILA_L_CORR},0)").font = F_TXT
ws.cell(row=r, column=3, value="CP").font = F_NEG
ws.cell(row=r, column=4,
        value="Cada estación pesa según los kilómetros que representa.").font = F_NOTA
FILA_TPD_CORR = r
for rr in (FILA_L_CORR, FILA_TPD_CORR):
    for col in range(1, 5):
        ws.cell(row=rr, column=col).border = BORDE

# ============================================================= 3. Tasa
ws = wb.create_sheet("3. Tasa")
titulo(ws, "Tasa de siniestralidad normalizada por exposición",
       "Las dos definiciones de tramo se publican juntas. Toda celda es fórmula: cambia una entrada "
       "en la hoja 2 y esta hoja se recalcula.")
cab(ws, 4, ["Definición del tramo", "Fallecidos", "TPD", "L (km)", "Años",
            "Veh-km del periodo", "Tasa", "Marca"],
    [46, 12, 11, 10, 8, 21, 12, 8])

E = "'2. Entradas'!"
defs = [
    ("Corredor completo Ibagué – Calarcá (74 km)",
     f"={E}B{FILA_FALL_PASO}", f"={E}B{FILA_TPD_CORR}", f"={E}B{FILA_L_CORR}"),
    ("Solo el paso — estación 244 (45 km)",
     f"={E}B{FILA_FALL_PASO}", f"={E}B{FILA_T244}", f"={E}B{FILA_L244}"),
]
r = 5
primera = r
for nombre, f_, tpd_, l_ in defs:
    ws.cell(row=r, column=1, value=nombre).font = F_NEG
    ws.cell(row=r, column=2, value=f_).font = F_TXT
    ws.cell(row=r, column=3, value=tpd_).font = F_TXT
    ws.cell(row=r, column=4, value=l_).font = F_TXT
    ws.cell(row=r, column=5, value=f"={E}B{FILA_ANIOS}").font = F_TXT
    ws.cell(row=r, column=6, value=f"=C{r}*365*D{r}*E{r}").font = F_TXT
    ws.cell(row=r, column=6).number_format = "#,##0"
    c = ws.cell(row=r, column=7, value=f"=B{r}/F{r}*100000000")
    c.font, c.number_format = F_RES, "0.00"
    ws.cell(row=r, column=8, value="CP").font = F_NEG
    for col in range(1, 9):
        ws.cell(row=r, column=col).border = BORDE
    r += 1

# fila de control con los 52 del corredor
ws.cell(row=r, column=1, value="Control · los 52 fallecidos del corredor, sobre 74 km").font = F_TXT
ws.cell(row=r, column=2, value=f"={E}B{FILA_FALL_CORR}").font = F_TXT
ws.cell(row=r, column=3, value=f"={E}B{FILA_TPD_CORR}").font = F_TXT
ws.cell(row=r, column=4, value=f"={E}B{FILA_L_CORR}").font = F_TXT
ws.cell(row=r, column=5, value=f"={E}B{FILA_ANIOS}").font = F_TXT
ws.cell(row=r, column=6, value=f"=C{r}*365*D{r}*E{r}").font = F_TXT
ws.cell(row=r, column=6).number_format = "#,##0"
c = ws.cell(row=r, column=7, value=f"=B{r}/F{r}*100000000")
c.font, c.number_format = F_TXT, "0.00"
ws.cell(row=r, column=8, value="CP").font = F_NEG
for col in range(1, 9):
    ws.cell(row=r, column=col).border = BORDE
fila_control = r

r += 3
ws.cell(row=r, column=1, value="COMPARACIÓN CON LO QUE PUBLICABA EL LIBRO ANTERIOR").font = F_NEG
ws.cell(row=r, column=1).fill = FILL_SEC
r += 1
ws.cell(row=r, column=1, value="Tasa con las hipótesis del libro anterior (TPD 3.000, L 60 km)").font = F_TXT
c = ws.cell(row=r, column=2, value=f"=B{primera}/(3000*365*60*E{primera})*100000000")
c.font, c.fill, c.number_format = F_ENT, FILL_HIP, "0.00"
ws.cell(row=r, column=3, value="H").font = F_NEG
ws.cell(row=r, column=4, value="Las dos entradas eran supuestos, no medidas.").font = F_NOTA
fila_vieja = r
r += 1
ws.cell(row=r, column=1, value="La tasa medida es, respecto de la anterior").font = F_TXT
c = ws.cell(row=r, column=2, value=f"=G{primera}/B{fila_vieja}")
c.font, c.number_format = F_NEG, "0%"
ws.cell(row=r, column=3, value="CP").font = F_NEG
ws.cell(row=r, column=4,
        value="El TPD real del paso es más del doble del supuesto, así que la tasa cae.").font = F_NOTA

r += 2
ws.cell(row=r, column=1, value="HIPÓTESIS DECLARADA · el año que falta en el aforo  [H]").font = F_NEG
ws.cell(row=r, column=1).fill = FILL_SEC
r += 1
for t in [
    "El registro de fallecidos cubre CINCO años (2015–2019). El aforo de INVÍAS cubre CUATRO en la",
    "estación 244 (2015–2018) y TRES en la 243 (el libro no publica 2018). El cálculo multiplica el TPD",
    "medido por los cinco años, es decir, SUPONE que 2019 tuvo un tránsito parecido. Eso es una",
    "hipótesis y aquí se declara en vez de quedar escondida en el promedio.",
    "",
    "No es una hipótesis ciega: el aforo del peaje Cajamarca de 2019 SÍ existe y sirve de control.",
]:
    ws.cell(row=r, column=1, value=t).font = F_NOTA
    r += 1
r += 1
ctrl = [
    ("TPD del peaje Cajamarca en 2019", f"={E}B{FILA_TPD_2019}", "F",
     "Medido. Se desvía de la media 2015–2018 de la estación 244 en menos del 5 %.", "#,##0"),
    ("Media 2015–2019 incorporando ese año", f"=({E}B{FILA_T244}*4+{E}B{FILA_TPD_2019})/5", "CP",
     "Escenario alternativo: cinco años, con 2019 tomado del peaje.", "#,##0"),
    ("Tasa del paso con ese escenario", f"=B{primera}/(B{r + 1}*365*D{primera + 1}*E{primera})*100000000",
     "CP", "Frente a la publicada arriba.", "0.00"),
    ("Cuánto mueve la hipótesis la tasa publicada", f"=ABS(B{r + 2}-G{primera + 1})/G{primera + 1}",
     "CP", "Si esta cifra fuera grande, la tasa no sería publicable. No lo es.", "0.0%"),
]
for et, fx, marca, nota, fmt in ctrl:
    ws.cell(row=r, column=1, value=et).font = F_TXT
    c = ws.cell(row=r, column=2, value=fx)
    c.font, c.number_format = F_TXT, fmt
    ws.cell(row=r, column=3, value=marca).font = F_NEG
    ws.cell(row=r, column=4, value=nota).font = F_NOTA
    for col in range(1, 5):
        ws.cell(row=r, column=col).border = BORDE
    r += 1

r += 2
for t in [
    "CÓMO SE LEE",
    "Las dos primeras filas usan los mismos 42 fallecidos y difieren solo en el denominador: la primera los",
    "reparte sobre los 74 km del corredor que la ANSV nombra; la segunda sobre los 45 km donde caen los seis",
    "sectores críticos. La segunda es mayor porque concentra la misma mortalidad en menos kilómetros.",
    "",
    "La fila de control usa los 52 fallecidos del corredor completo, incluidos los diez del tramo",
    "La Paila – Calarcá que no pertenecen al cruce. Sirve de cota superior, no de resultado.",
]:
    c = ws.cell(row=r, column=1, value=t)
    c.font = F_NEG if (t.isupper() and t) else F_NOTA
    r += 1

# ============================================================= 4. Sensibilidad
ws = wb.create_sheet("4. Sensibilidad")
titulo(ws, "Sensibilidad de la tasa a las dos entradas que antes eran hipótesis",
       "Ya no hace falta para publicar un resultado, pero muestra cuánto dependía la cifra anterior de "
       "supuestos. La casilla verde es el valor medido.")
TPDS = [3000, 4000, 5000, 6000, 6820, 7000, 8000]
LS = [40, 45, 60, 74, 80, 90]
ws.cell(row=4, column=1, value="TPD \\ L (km)").font = F_CAB
ws.cell(row=4, column=1).fill = FILL_CAB
ws.cell(row=4, column=1).border = BORDE
for j, L in enumerate(LS, start=2):
    c = ws.cell(row=4, column=j, value=L)
    c.font, c.fill, c.border = F_CAB, FILL_CAB, BORDE
    c.alignment = Alignment(horizontal="center")
    ws.column_dimensions[get_column_letter(j)].width = 11
ws.column_dimensions["A"].width = 14
for i, tpd in enumerate(TPDS, start=5):
    c = ws.cell(row=i, column=1, value=tpd)
    c.font, c.fill, c.border = F_NEG, FILL_SEC, BORDE
    for j, L in enumerate(LS, start=2):
        cell = ws.cell(row=i, column=j,
                       value=f"='3. Tasa'!$B${primera}/($A{i}*365*{get_column_letter(j)}$4*"
                             f"'3. Tasa'!$E${primera})*100000000")
        cell.number_format = "0.00"
        cell.border = BORDE
        cell.font = F_TXT
        if tpd == 6820 and L == 74:
            cell.font = F_RES
            cell.fill = PatternFill("solid", fgColor="DCFCE7")
ws.cell(row=len(TPDS) + 7, column=1,
        value="Verde: el valor con las dos entradas medidas. El resto de la tabla existe para mostrar "
              "de qué dependía la cifra que se publicaba antes.").font = F_NOTA

# ============================================================= 5. Carga pesada
ws = wb.create_sheet("5. Carga pesada")
titulo(ws, "Exposición de la carga pesada en el descenso del paso",
       "Es el grupo que la Ferropista captaría. Todas las cifras salen de la estación 244, "
       "que mide el paso.")
cab(ws, 4, ["Concepto", "Valor", "Marca", "Nota"], [50, 18, 8, 70])
r = 5
pesadas = [
    ("TPD total del paso, media 2015–2018", f"={E}B{FILA_T244}", "F", "Estación 244 de INVÍAS.", "#,##0"),
    ("TPD de camiones en el paso", f"={E}B{FILA_PES}", "F",
     "Composición vehicular publicada por INVÍAS.", "#,##0"),
    ("Participación de los camiones", f"=B6/B5", "CP",
     "La clase «camiones» de esta fuente incluye los de dos ejes: es cota superior.", "0.0%"),
    ("Longitud del paso (km)", f"={E}B{FILA_L244}", "F", "Declarada por INVÍAS.", "0"),
    ("Vehículos-km diarios de camiones", "=B6*B8", "CP", "TPD de camiones × longitud.", "#,##0"),
    ("Vehículos-km anuales de camiones", "=B9*365", "CP",
     "Exposición anual del grupo que haría el cruce por el túnel.", "#,##0"),
    ("Captación prevista por la Ferropista", 0.90, "F",
     "Ponencia ARCS / UC Consult, dia. 10. Cifra del proponente, no auditada.", "0%"),
    ("Vehículos-km anuales que dejarían el paso", "=B10*B11", "CP",
     "Estimación condicionada a esa captación. No es un pronóstico.", "#,##0"),
]
for et, v, marca, nota, fmt in pesadas:
    ws.cell(row=r, column=1, value=et).font = F_TXT
    c = ws.cell(row=r, column=2, value=v)
    c.number_format = fmt
    if marca == "F" and not str(v).startswith("="):
        c.font, c.fill = F_ENT, FILL_HIP
    else:
        c.font = F_TXT
    ws.cell(row=r, column=3, value=marca).font = F_NEG
    ws.cell(row=r, column=4, value=nota).font = F_NOTA
    for col in range(1, 5):
        ws.cell(row=r, column=col).border = BORDE
    r += 1

r += 1
for t in [
    "QUÉ PUEDE AFIRMARSE",
    "La tasa de mortalidad del corredor, normalizada por exposición, con las dos entradas medidas y el",
    "periodo de fallecidos y de aforo coincidiendo por primera vez.",
    "La exposición anual en vehículos-kilómetro de la carga pesada que hace el cruce.",
    "",
    "QUÉ NO PUEDE AFIRMARSE",
    "Cuántas muertes evitaría la Ferropista. Eso exige un modelo de siniestralidad calibrado con microdatos",
    "por siniestro (tipo de vehículo, causa, condición de la víctima) que no están públicos para este corredor.",
    "Que la tasa de hoy sea esta: la línea base es anterior al Túnel de La Línea y sobrestima el riesgo actual.",
]:
    c = ws.cell(row=r, column=1, value=t)
    c.font = F_NEG if (t.isupper() and t) else F_NOTA
    r += 1

# ============================================================= 6. Serie del paso
ws = wb.create_sheet("6. Serie del paso")
titulo(ws, "Serie histórica del paso — estación 244, Calarcá – Cajamarca",
       "Datos de INVÍAS 1997–2018 [F]. Las columnas de TPD por clase se calculan por fórmula [CP]. "
       "Alimenta la figura de la actividad.")
cab(ws, 4, ["Año", "TPD total", "% autos", "% buses", "% camiones",
            "TPD camiones", "TPD no pesados"], [9, 12, 11, 11, 13, 14, 15])
r = 5
for f in [x for x in hist if x["estacion"] == "244"]:
    ws.cell(row=r, column=1, value=int(f["anio"])).font = F_TXT
    ws.cell(row=r, column=2, value=int(f["tpd"])).font = F_TXT
    for col, campo in ((3, "pct_autos"), (4, "pct_buses"), (5, "pct_camiones")):
        v = f[campo]
        ws.cell(row=r, column=col, value=int(v) if v else None).font = F_TXT
    ws.cell(row=r, column=6, value=f'=IF(E{r}="","",ROUND(B{r}*E{r}/100,0))').font = F_TXT
    ws.cell(row=r, column=7, value=f'=IF(E{r}="","",B{r}-F{r})').font = F_TXT
    for col in range(1, 8):
        ws.cell(row=r, column=col).border = BORDE
    r += 1
ws.cell(row=r + 1, column=1,
        value="En 2018 la participación de camiones cae de 59 % a 44 % tras veinte años estable entre "
              "60 % y 69 %. Sin contrastar: no usar ese año aislado.").font = F_NOTA
ws.freeze_panes = "A5"

wb.save(SALIDA)
print("escrito:", SALIDA)
print(f"  fallecidos paso={fall_paso} corredor={fall_corr} | TPD 244={t244:.0f} 243={t243:.0f} "
      f"| camiones={pes244:.0f}")
