# -*- coding: utf-8 -*-
"""OE 3 · Actividad 5 — Paso 3 de 3: INFORME PDF «Esquema de cimentación e informe».

CONSOLIDA, NO RECALCULA. Toda cifra se lee de cimentacion_conceptual_OE3.json (paso 1) y la figura del plano
de ../Visuales/plano_cimentacion_terminales_OE3.png (paso 2). Plantilla: ../plantilla_documentos_OE3.py.
Salida: Informe_cimentacion_terminales_OE3.pdf. Requiere reportlab.
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__)); OE3 = os.path.dirname(AQUI); sys.path.insert(0, OE3)
from plantilla_documentos_OE3 import *          # noqa: F401,F403

D = json.load(open(os.path.join(AQUI, "cimentacion_conceptual_OE3.json"), encoding="utf-8"))
SALIDA = os.path.join(AQUI, "Informe_cimentacion_terminales_OE3.pdf")
PLANO = os.path.join(OE3, "Visuales", "plano_cimentacion_terminales_OE3.png")
HY = D["hipotesis"]; K = D["constantes"]; CG = D["cargas"]
COL = lambda *w: [x * mm for x in w]


def v(k, dec=2):
    x = HY[k]["valor"]
    if isinstance(x, list):
        return " × ".join(es_co(y, dec) for y in x)
    return es_co(x, dec)


def zap(z, s, caso, nf="NF en la base"):
    for r in D["zapatas"]:
        if r["zapata"] == z and r["suelo"] == s and r["caso"] == caso and r["nf"] == nf:
            return r


# control interno: el nivel freático no cambia el B (gobierna el asentamiento, que no depende del NF)
IGUAL_NF = all(zap(z, s, c)["B_m"] == zap(z, s, c, "NF profundo")["B_m"]
               for z in ("Z-1", "Z-2") for s in ("S1", "S2") for c in ("Mínimo", "Típico", "Máximo"))
PORT = {"S1": "Oriental (Ibagué) · S1", "S2": "Occidental (Calarcá) · S2"}


def cuerpo(doc):
    S = []; A = S.append
    A(Paragraph("Marcas de origen: <b>[F]</b> dato de fuente externa citada · <b>[CP]</b> cálculo propio reproducible por un script "
                "publicado · <b>[H]</b> hipótesis declarada. Ninguna cifra entra sin marca.", NOTA))
    # 1
    A(Paragraph("1. Objeto y alcance", H2))
    A(Paragraph("Este producto cierra el OE 3. Plantea, a nivel conceptual, la cimentación superficial de las estructuras de superficie de "
                "las dos terminales Ro-Ro del túnel (portal oriental en Ibagué y portal occidental en Calarcá): la marquesina del andén de "
                "carga, el edificio de control y la rampa de acceso de las tractomulas. Usa la capacidad admisible estimada en la Act 4 y "
                "los parámetros de la Act 3.", P))
    A(Paragraph("<b>No es un diseño para construcción.</b> Los parámetros del suelo son análogos publicados, no ensayos del sitio; la "
                "fuente primaria no describe las terminales más allá de su número y de la longitud de los trenes. Por eso la geometría y "
                "las cargas son hipótesis declaradas, y el resultado se presenta para el caso típico con su rango mínimo–máximo. Su valor "
                "es mostrar qué tan sensible es la cimentación a la incertidumbre del suelo y qué exploración la resolvería.", DEST))
    # 2
    A(Paragraph("2. Insumos y encadenamiento", H2))
    A(Paragraph(f"El cálculo lee los parámetros y los factores de seguridad de la memoria de la Act 4 y usa las mismas ecuaciones. Antes de "
                f"dimensionar, el script reproduce los 36 valores de capacidad admisible de la Act 4; la diferencia relativa máxima fue "
                f"{D['control_act4_dif_relativa']:.1e} [CP]. Df = {es_co(K['Df_m'], 2)} m, asentamiento admisible "
                f"{es_co(K['rho_adm_m'] * 1000, 0)} mm, FSICP {es_co(K['FSICP'], 1)} y FSBM {es_co(K['FSBM'], 2)} (NSR-10 tablas H.4.7-1 y H.2.4-1) [F].", P))
    titulo_tabla("Hipótesis de geometría y cargas de las terminales", S)
    filas_h = []
    for k, etq in (("anden_longitud_m", "Longitud del andén (m)"), ("marquesina_luz_m", "Luz de la marquesina (m)"),
                   ("marquesina_separacion_m", "Separación entre pórticos (m)"), ("marquesina_altura_libre_m", "Altura libre de la marquesina (m)"),
                   ("cubierta_tablero_kPa", "Tablero metálico de cubierta (kPa)"), ("cubierta_estructura_kPa", "Estructura metálica de cubierta (kPa)"),
                   ("cubierta_Lr_kPa", "Carga viva de cubierta Lr (kPa)"), ("edificio_planta_m", "Planta del edificio de control (m)"),
                   ("edificio_luz_m", "Luz de los pórticos del edificio (m)"), ("losa_espesor_m", "Espesor equivalente de losa (m)"),
                   ("oficinas_particiones_kPa", "Particiones fijas de mampostería (kPa)"), ("oficinas_afinado_kPa", "Afinado de piso y cubierta (kPa)"),
                   ("oficinas_L_kPa", "Carga viva de oficinas y cubierta (kPa)"), ("tractomula_3S3_kN", "Tractomula 3S3 (kN)"),
                   ("tridem_kN", "Eje trídem de 12 llantas (kN)"), ("factor_dinamico", "Factor dinámico en la rampa"),
                   ("rampa_losa_m", "Losa de la rampa (m)"), ("rampa_base_m", "Base granular (m)"), ("rampa_altura_m", "Desnivel de la rampa (m)"),
                   ("rampa_pendiente", "Pendiente de la rampa")):
        filas_h.append([etq, v(k, 1 if "kN" in k and "kPa" not in k else 2), HY[k]["marca"], HY[k]["justificacion"]])
    A(tabla(filas(["Hipótesis", "Valor", "Marca", "Justificación o fuente"], filas_h), COL(52, 20, 13, 85)))
    A(fuente("cimentacion_conceptual_OE3.json; NSR-10 Título B; Resolución 4100 de 2004 del Ministerio de Transporte; ponencia Fernández (2025), dia. 20 y 23."))
    # 3
    A(Paragraph("3. Cargas sobre la cimentación", H2))
    A(Paragraph("Cargas de servicio sin mayorar, como pide H.2.4.3 para comparar con la capacidad admisible. El peso propio de la zapata "
                f"y del relleno sobre ella se suma como {es_co(K['gamma_relleno_kN_m3'], 0)} kN/m³ × Df [H]. El concreto reforzado pesa "
                f"{es_co(K['gamma_concreto_kN_m3'], 2)} kN/m³ (2.400 kg/m³, tabla B.3.2-1) [F→CP].", P))
    titulo_tabla("Cargas de servicio por apoyo", S)
    A(tabla(filas(["Zapata", "Estructura", "Área aferente (m²)", "PD (kN)", "PL (kN)", "P (kN)", "Combinación"],
                  [[z, CG[z]["estructura"], es_co(CG[z]["area_aferente_m2"], 0), es_co(CG[z]["PD_kN"], 1), es_co(CG[z]["PL_kN"], 1),
                    f"<b>{es_co(CG[z]['P_kN'], 1)}</b>", CG[z]["combinacion"]] for z in ("Z-1", "Z-2")]),
            COL(15, 45, 20, 17, 17, 17, 39)))
    A(fuente("cimentacion_conceptual_OE3.py [CP] con cargas de la NSR-10 Título B [F] y geometría [H] (tabla 1)."))
    # 4
    A(Paragraph("4. Dimensionamiento de las zapatas aisladas", H2))
    A(Paragraph(f"Para cada zapata se busca el menor ancho B (cuadrado, en pasos de {es_co(K['paso_B_m'], 1)} m, desde {es_co(K['B_min_m'], 1)} m "
                f"como mínimo constructivo hasta {es_co(K['B_max_m'], 1)} m) que cumple P/B² + peso de zapata y relleno ≤ qadm(B). La capacidad "
                "admisible se recalcula para cada B porque, en este suelo, disminuye al crecer B: la gobierna el asentamiento.", P))
    if IGUAL_NF:
        A(Paragraph("En todos los casos el B resultó igual con el nivel freático en la base o profundo [CP]; la tabla muestra el caso con el "
                    "nivel freático en la base.", NOTA))
    for z in ("Z-1", "Z-2"):
        titulo_tabla(f"Dimensionamiento de la zapata {z} por portal y caso de parámetros", S)
        cuerpo_t = []
        for s in ("S1", "S2"):
            for c in ("Mínimo", "Típico", "Máximo"):
                r = zap(z, s, c)
                B = f"<b>{es_co(r['B_m'], 1)}</b>" if r["B_m"] else "<b>no cumple con B ≤ 6 m</b>"
                cuerpo_t.append([PORT[s], c, B, es_co(r["q_act_kPa"], 0), es_co(r["qadm_kPa"], 0), r["gobierna"]])
        A(tabla(filas(["Portal · suelo", "Caso", "B (m)", "q actuante (kPa)", "qadm (kPa)", "Gobierna"], cuerpo_t), COL(50, 20, 32, 24, 20, 24)))
        A(fuente("cimentacion_conceptual_OE3.json [CP]. q actuante y qadm con el B adoptado (o con B = 6 m si no hay solución)."))
    A(Paragraph("<b>Lectura.</b> La marquesina es liviana: con el mínimo constructivo de 1,0 m basta en casi todos los casos, y solo el suelo "
                "S1 con parámetros mínimos pide un poco más. El edificio de control es el caso crítico: con parámetros típicos necesita "
                f"zapatas de {es_co(zap('Z-2', 'S1', 'Típico')['B_m'], 1)} m en Ibagué y {es_co(zap('Z-2', 'S2', 'Típico')['B_m'], 1)} m en Calarcá, "
                "y con los mínimos ninguna zapata aislada cumple.", P))
    # 5
    A(Paragraph("5. Alternativas donde la zapata aislada no cumple", H2))
    L = D["losa_edificio"]
    A(Paragraph(f"<b>Losa de cimentación del edificio.</b> Se revisa una losa de {es_co(L['espesor_m'], 2)} m bajo toda la planta de "
                f"{es_co(L['planta_m'][0], 0)} × {es_co(L['planta_m'][1], 0)} m, con presión uniforme de {es_co(L['q_uniforme_kPa'], 1)} kPa [CP] "
                f"y Cd = {es_co(L['Cd'], 2)} (rectángulo L/B = 1,5, promedio; FHWA NHI-06-089 tabla 8-13) [F].", P))
    titulo_tabla("Losa de cimentación del edificio de control", S)
    A(tabla(filas(["Portal · suelo", "Caso", "q (kPa)", "qadm (kPa)", "Gobierna", "¿Cumple?"],
                  [[PORT[x["suelo"]], x["caso"], es_co(x["q_act_kPa"], 1), es_co(x["qadm_kPa"], 1), x["gobierna"], "Sí" if x["cumple"] else "<b>No</b>"]
                   for x in L["casos"]]), COL(50, 20, 22, 22, 26, 20)))
    A(fuente("cimentacion_conceptual_OE3.json [CP]."))
    R = D["rampa"]
    A(Paragraph(f"<b>Rampa de acceso.</b> Losa de concreto sobre base granular y relleno compactado, de {es_co(R['longitud_m'], 1)} m de largo. "
                f"El trídem de la tractomula, con el factor dinámico, se reparte 2:1 a través de la losa y la base sobre "
                f"{es_co(R['area_reparticion_m2'], 1)} m²: {es_co(R['q_tridem_kPa'], 1)} kPa, más {es_co(R['q_peso_propio_kPa'], 1)} kPa de peso propio, "
                f"en total {es_co(R['q_total_kPa'], 1)} kPa en la subrasante [CP].", P))
    titulo_tabla("Presión de la rampa sobre la subrasante", S)
    A(tabla(filas(["Portal · suelo", "Caso", "Ancho equivalente (m)", "q (kPa)", "qadm (kPa)", "¿Cumple?"],
                  [[PORT[x["suelo"]], x["caso"], es_co(x["B_eq_m"], 2), es_co(x["q_act_kPa"], 1), es_co(x["qadm_kPa"], 1), "Sí" if x["cumple"] else "<b>No</b>"]
                   for x in R["casos"]]), COL(50, 20, 30, 22, 22, 20)))
    A(fuente("cimentacion_conceptual_OE3.json [CP]; carga del trídem de la Resolución 4100 de 2004, art. 9 [F]."))
    A(Paragraph("Con los parámetros mínimos, la losa del edificio y la rampa tampoco cumplen. En ese escenario, las opciones son sustituir "
                "o mejorar el suelo bajo la cimentación (material granular compactado) o pasar a cimentación profunda. Elegir entre ellas "
                "requiere la exploración de la sección 7.", P))
    # 6
    A(Paragraph("6. Condiciones de sitio que el esquema no resuelve", H2))
    sm, pe = D["sismo_SGC"], D["pendiente_Act2"]
    for t_ in [
        f"<b>Sismo.</b> Ibagué: Aa {es_co(sm['oriental_Ibague']['Aa'], 2)}, amenaza {sm['oriental_Ibague']['zona'].lower()}; Calarcá: Aa "
        f"{es_co(sm['occidental_Calarca']['Aa'], 2)}, amenaza {sm['occidental_Calarca']['zona'].lower()} (SGC, zonificación NSR-10) [F]. "
        "Las zapatas se dimensionaron con cargas verticales; faltan la combinación sísmica con momentos y el amarre con vigas de "
        "cimentación que exige la NSR-10.",
        f"<b>Ladera del portal oriental.</b> La pendiente media en 250 m es {es_co(pe['oriental_Ibague']['media_250m'], 1)}° y el percentil 90 "
        f"es {es_co(pe['oriental_Ibague']['p90_250m'], 1)}° (Act 2) [CP]. Una terminal de 750 m exige explanación y análisis de estabilidad "
        "global (NSR-10 H.4.2.1 d).",
        "<b>Viento.</b> No se calculó (NSR-10 B.6). En una marquesina abierta el arranque por succión puede gobernar el tamaño de la zapata Z-1.",
        "<b>Ceniza volcánica del portal occidental.</b> Es sensible a la saturación y puede colapsar; hace falta un ensayo de colapso "
        "(NSR-10 H.4.8).",
        "<b>Diseño estructural.</b> Los espesores h y los pedestales son preliminares; el refuerzo, el punzonamiento y el cortante se "
        "diseñan con NSR-10 C.15.",
    ]:
        A(Paragraph("• " + t_, P))
    # 7
    A(Paragraph("7. Conclusiones y exploración requerida", H2))
    for t_ in [
        "En los dos portales la cimentación la gobierna el <b>asentamiento</b>, no la resistencia al corte. El dato que más reduce la "
        "incertidumbre es el <b>módulo de deformación</b> del suelo.",
        f"Con parámetros típicos, las zapatas aisladas funcionan: Z-1 de {es_co(zap('Z-1', 'S1', 'Típico')['B_m'], 1)} m en los dos portales; Z-2 de "
        f"{es_co(zap('Z-2', 'S1', 'Típico')['B_m'], 1)} m (Ibagué) y {es_co(zap('Z-2', 'S2', 'Típico')['B_m'], 1)} m (Calarcá).",
        "Con parámetros mínimos el edificio y la rampa necesitan mejoramiento del suelo o cimentación profunda: el rango de la Act 4 "
        "abarca soluciones de tipo distinto, no solo de tamaño distinto.",
        "Exploración mínima en cada portal (NSR-10 H.3): sondeos con SPT hasta la roca; piezómetros; triaxiales CU o CD; consolidación y "
        "colapso en la ceniza; sísmica de refracción o MASW. Detalle en la hoja «Limitaciones» de la memoria de la Act 4.",
    ]:
        A(Paragraph("• " + t_, P))
    A(Paragraph("<i>Nota de elaboración: preparado con apoyo de IA (Claude, de Anthropic). Cada cifra se lee del JSON del script citado, "
                "que reproduce la memoria de la Act 4 antes de calcular; las cargas se verificaron en el texto de la NSR-10 y de la "
                "Resolución 4100 de 2004.</i>", ParagraphStyle("NE", parent=FUENTE, spaceBefore=0, spaceAfter=0)))
    # Anexo A
    A(NextPageTemplate("h")); A(PageBreak())
    A(Marca("A", "Anexo A. Plano del esquema de cimentación"))
    A(Paragraph("Anexo A. Plano del esquema de cimentación", H2))
    w = APAIS[0] - 2 * MARGEN
    figura(PLANO, "Esquema conceptual de cimentación de las terminales Ro-Ro",
           "plano_cimentacion_OE3.py → Visuales/plano_cimentacion_terminales_OE3 (A3; también en AutoCAD: Plano_cimentacion_terminales_OE3.dxf) [CP]",
           S, w * 0.80, w * 0.80 * 2338 / 3308)
    return S


META = {"rotulo": "OE 3 · Actividad 5 · Producto", "titulo": "Esquema de cimentación de las terminales Ro-Ro",
        "subtitulo": "Diseño conceptual de la cimentación superficial en los portales de Ibagué y Calarcá",
        "ficha": [("Objetivo específico", "OE 3 — Estimar la capacidad portante preliminar del terreno de fundación de las infraestructuras de superficie en los portales"),
                  ("Actividad", "Act 5. Diseño conceptual de la cimentación superficial de las terminales de carga Ro-Ro"),
                  ("Entregable / formato", "Esquema de cimentación e informe · Plano AutoCAD / PDF"),
                  ("Periodo", "Bloque 2 del cronograma: 5 oct – 7 nov 2026"),
                  ("Responsable asignado", "Tamayo Osorio Miguel Ángel")],
        "pie": "Semillero GEOPAV · Ferropista Cordillera Central · OE 3 – Act 5", "fecha": "Septiembre de 2026",
        "titulo_pdf": "Esquema de cimentación de las terminales Ro-Ro - OE 3 Act 5 - Semillero GEOPAV"}
generar(SALIDA, META, cuerpo)
print("PDF escrito:", SALIDA)
