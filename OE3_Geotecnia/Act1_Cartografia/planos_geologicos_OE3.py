# -*- coding: utf-8 -*-
"""OE 3 · Actividad 1 (fila 49 del Cronograma) — Producto: «Planos geológicos», documento PDF.
Recopilación de la cartografía geológica del Servicio Geológico Colombiano para las planchas del corredor.

CONSOLIDA, NO RECALCULA. Toda cifra se lee de:
  ubicacion_portales_planchas_OE3.json  (ubicar_portales_planchas_OE3.py)
  consulta_sgc_portales_OE3.json        (consulta_sgc_portales_OE3.py)
y la lámina ../Visuales/lamina_portales_geologia_OE3.png (lamina_portales_OE3.py).
Las huellas md5 de las cuatro fuentes del SGC se calculan al generar el PDF y se comparan con las
registradas el 25 sep 2026: si un archivo cambió, el script se detiene.
Salida: Planos_geologicos_portales_OE3.pdf. Requiere reportlab y Pillow.
"""
import hashlib, json, os, sys
from PIL import Image as PILImage
AQUI = os.path.dirname(os.path.abspath(__file__)); OE3 = os.path.dirname(AQUI); sys.path.insert(0, OE3)
from plantilla_documentos_OE3 import *          # noqa: F401,F403
from reportlab.platypus import CondPageBreak

J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))
ubi = J(AQUI, "ubicacion_portales_planchas_OE3.json"); sgc = J(AQUI, "consulta_sgc_portales_OE3.json")["portales"]
SALIDA = os.path.join(AQUI, "Planos_geologicos_portales_OE3.pdf")
LAMINA = os.path.join(OE3, "Visuales", "lamina_portales_geologia_OE3.png")

FUENTES = [  # archivo, md5 registrado (25 sep 2026), descripción, escala, autoría
    ("Plancha_244_Ibague_mapa.pdf", "ea51243701d8c2cf027a69b20ccb1970", "Plancha 244 Ibagué — mapa geológico", "1:100.000",
     "Mosquera, Núñez y Vesga (1982), INGEOMINAS; transformada a MAGNA-SIRGAS"),
    ("Memoria_244_Ibague.pdf", "e7554cecf0d760cf4157418be2d5d8ad", "Memoria explicativa de la plancha 244 (388 págs., escaneo)", "—",
     "INGEOMINAS / SGC"),
    ("Plancha_243_Armenia_mapa.pdf", "cda70137b4c6478f79dadcacc3a60401", "Plancha 243 Armenia — mapa geológico", "1:100.000",
     "McCourt et al. (1985), INGEOMINAS"),
    ("Resena_243_Armenia.pdf", "9cda8aed4f385cdfcf24043616b233ea", "Reseña explicativa de la plancha 243", "—", "INGEOMINAS / SGC"),
]
for arch, md5, *_ in FUENTES:
    h = hashlib.md5(open(os.path.join(AQUI, arch), "rb").read()).hexdigest()
    if h != md5:
        raise SystemExit(f"PARADA: {arch} tiene md5 {h} y se registró {md5}. La fuente cambió: revisar antes de publicar.")
print("control OK: las cuatro fuentes del SGC conservan su md5")

UNIDAD = {  # lectura de la leyenda impresa de cada plancha [F] (misma redacción que la lámina)
    "oriental_Ibague": ("244", "Contacto entre <b>PCAn</b> (Neises y Anfibolitas de Tierradentro: neises cuarzo-feldespático-biotíticos, "
                        "anfibolitas) y <b>Jcdi</b> (Batolito de Ibagué: granodiorita biotítico-hornbléndica, con variaciones a cuarzodiorita y cuarzomonzonita)"),
    "occidental_Calarca": ("243", "Borde de un lente de <b>Kqv</b> (Complejo Quebradagrande, miembro volcánico: diabasas y andesitas) dentro de "
                           "<b>Kqs</b> (miembro sedimentario: grauvacas, lutitas, chert, calizas); Formación Armenia (<b>TQa</b>) al W"),
}
NOMBRE = {"oriental_Ibague": "Portal oriental — Ibagué (DANE 73001)", "occidental_Calarca": "Portal occidental — Calarcá (DANE 63130)"}
COL = lambda *w: [x * mm for x in w]

def cuerpo(doc):
    S = []; A = S.append
    A(Paragraph("Marcas de origen: <b>[F]</b> dato de fuente externa citada · <b>[CP]</b> cálculo propio reproducible por un script "
                "publicado · <b>[H]</b> hipótesis declarada · <b>[DA]</b> dato abierto pendiente. Ninguna cifra entra sin marca.", NOTA))
    # 1
    A(Paragraph("1. Objeto y alcance", H2))
    A(Paragraph("Este producto reúne la cartografía geológica oficial del Servicio Geológico Colombiano (SGC) que cubre los dos "
                "emboquilles del túnel de base analizado y ubica sobre ella los portales definidos en el OE 1. Es el insumo de las "
                "actividades siguientes del OE 3: la identificación de zonas susceptibles a movimientos en masa (Act 2) y la definición "
                "de parámetros geotécnicos por unidad litológica (Act 3).", P))
    A(Paragraph("<b>Alcance:</b> la cartografía 1:100.000 localiza unidades y estructuras con una precisión del orden de cientos de "
                "metros. No describe el espesor del suelo ni del perfil de meteorización y no sustituye la exploración de subsuelo; "
                "por eso el OE 3 entrega rangos de parámetros y no valores de diseño.", DEST))
    # 2
    A(Paragraph("2. Cartografía recopilada", H2))
    A(Paragraph("Se descargaron del SGC las dos planchas geológicas 1:100.000 que contienen los portales y sus textos explicativos. "
                "Además se consultaron los servicios ArcGIS REST del SGC para el Mapa Geológico de Colombia 2023 (1:1.000.000), la "
                "zonificación sísmica de la NSR-10 por municipio y el catálogo de dataciones radiométricas.", P))
    titulo_tabla("Cartografía del SGC recopilada para los portales", S)
    A(tabla(filas(["Documento", "Escala", "Autoría", "Archivo (md5)"],
                  [[d, e, a, f"<font size=7>{f}<br/>{m}</font>"] for f, m, d, e, a in FUENTES]), COL(52, 18, 48, 52)))
    A(fuente("carpeta OE3_Geotecnia/Act1_Cartografia; md5 comprobado por planos_geologicos_OE3.py al generar este documento [CP]."))
    titulo_tabla("Servicios del SGC consultados", S)
    A(tabla(filas(["Servicio", "Uso en este producto"], [
        ["Mapa Geológico de Colombia 2023, 1:1.000.000 (unidades y fallas)", "Unidad cronoestratigráfica bajo cada portal; fallas a menos de 10 km"],
        ["Zonificación de amenaza sísmica NSR-10 por municipio", "Coeficientes Aa, Av, Ae y Ad del municipio de cada portal"],
        ["Catálogo de dataciones radiométricas (2015)", "Edades U–Pb a menos de 20 km del portal oriental"]]), COL(85, 85)))
    A(fuente("consulta_sgc_portales_OE3.py → consulta_sgc_portales_OE3.json, consultado el " + J(AQUI, "consulta_sgc_portales_OE3.json")["generado"][:10] + " [F]."))
    # 3
    A(Paragraph("3. Ubicación de los portales sobre las planchas", H2))
    A(Paragraph("Los portales son los del OE 1, localizados sobre el Copernicus DEM GLO-30 por criterio geométrico <b>[CP]</b>. Para "
                "ubicarlos sobre cada plancha sin programa SIG se detectó en el PDF la cuadrícula de 5 km (≈ 28,3 pt/km, es decir, "
                "1:100.000), se calibró con los rótulos de meridianos y paralelos y se proyectó el portal al sistema de la plancha "
                "(MAGNA-SIRGAS, EPSG 3116 en la 244 y EPSG 3115 en la 243). La tabla " + str(CONT["T"] + 1) + " resume el control de la calibración.", P))
    TAB_CAL = CONT["T"] + 1
    t = []
    for pl in ("244", "243"):
        u = ubi[pl]
        t.append([f"<b>{pl}</b>", f"{es_co(u['lat'], 4)} N; {es_co(u['lon'], 4)}", f"EPSG {u['epsg']}",
                  f"E {es_co(u['E'], 0)} · N {es_co(u['N'], 0)}", f"{es_co(u['escala_pt_km'][0], 3)} / {es_co(u['escala_pt_km'][1], 3)}",
                  f"{es_co(u['residuo_max_meridianos_pt'])} / {es_co(u['residuo_max_paralelos_pt'])}"])
    titulo_tabla("Georreferenciación de los portales sobre las planchas 1:100.000", S)
    A(tabla(filas(["Plancha", "Portal (WGS 84)", "Sistema", "Coordenadas planas (m)", "Escala pt/km (E / N)", "Residuo máx. pt (merid. / paral.)"], t),
            COL(16, 34, 20, 40, 28, 32)))
    A(fuente("ubicar_portales_planchas_OE3.py → ubicacion_portales_planchas_OE3.json [CP]."))
    A(Paragraph("En la plancha 244 el residuo de 3 pt equivale a unos 0,1 km. En la 243 el desfase de los meridianos es el mismo en los "
                "dos rótulos: corresponde al punto de anclaje del texto, no a un error de escala. La precisión de la ubicación es del "
                "orden de ±0,1 km, más el error propio de una cartografía 1:100.000.", P))
    # 4
    A(CondPageBreak(120 * mm)); A(Paragraph("4. Geología en los emboquilles", H2))
    for key in ("oriental_Ibague", "occidental_Calarca"):
        s = sgc[key]; pl, uni = UNIDAD[key]; n = s["nsr10"][0]; u1 = s["unidad_bajo_portal"][0]
        A(CondPageBreak(90 * mm)); A(Paragraph(NOMBRE[key], H3))
        titulo_tabla(f"Síntesis geológica del {NOMBRE[key].split(' — ')[0].lower()}", S)
        A(tabla(filas(["Aspecto", "Resultado", "Marca"], [
            [f"Unidad en el punto, plancha {pl} (1:100.000)", uni, "[F]"],
            ["Unidad en el punto, Mapa Geológico 2023 (1:1 M)", f"<b>{u1['SimboloUC']}</b> — {u1['Edad']}: {u1['Descripcion']}", "[F]"],
            ["Otras unidades a menos de 5 km (1:1 M)", ", ".join(f"{x['SimboloUC']} ({x['Edad']})" for x in s["unidades_5km"] if x["SimboloUC"] != u1["SimboloUC"]), "[F]"],
            ["Fallas a menos de 10 km (1:1 M)", "; ".join(("Falla sin nombre" if x["nombre"] == "(sin nombre)" else x["nombre"]) + (f" ({x['tipo'].lower()})" if x["tipo"] != "Falla" else "") + f" a {es_co(x['dist_km'])} km" for x in s["fallas_10km"]), "[F] / distancia [CP]"],
            [f"NSR-10, municipio de {n['NOMBRE_MUNICIPIO'].title()}", f"Aa {es_co(n['AA'], 2)} · Av {es_co(n['AV'], 2)} · Ae {es_co(n['AE'], 2)} · Ad {es_co(n['AD'], 2)} · amenaza sísmica <b>{n['ZONA_AMENAZA_SÍSMICA'].lower()}</b>", "[F]"],
        ]), COL(48, 104, 18)))
        A(fuente("planchas del SGC (tabla 1) y consulta_sgc_portales_OE3.json. Las distancias se miden desde el portal del OE 1."))
    A(Paragraph("La edad de la roca del portal oriental", H3))
    A(Paragraph("La plancha de 1982 llama «neises precámbricos» (<b>PCAn</b>) a la franja en la que cae el portal, y el mapa 2023 la "
                "rotula <b>P-Pi</b>, Pérmico. El Batolito de Ibagué, con el que hace contacto, es Jurásico. Las dataciones U–Pb más "
                "cercanas al portal son pérmicas, lo que apoya la edad del mapa 2023 (tabla " + str(CONT["T"] + 1) + ").", P))
    d = sgc["oriental_Ibague"]["dataciones_UPb_20km"][:6]
    titulo_tabla("Dataciones U–Pb a menos de 10 km del portal oriental", S)
    A(tabla(filas(["Distancia (km)", "Unidad", "Litología", "Edad (Ma)", "Referencia"],
                  [[es_co(x["dist_km"]), x["unidad"], x["litologia"], f"{x['edad_Ma']} {x['error_Ma'] or ''}", x["referencia"]] for x in d]),
            COL(22, 44, 30, 30, 44)))
    A(fuente("Catálogo de dataciones radiométricas del SGC (2015) [F]; distancias [CP]."))
    A(Paragraph("<b>[H]</b> La franja PCAn sería el metagranito pérmico que el mapa 2023 rotula P-Pi. Es una interpretación, no una "
                "datación en el punto. Para la geotecnia lo que importa es que el emboquille oriental está en <b>neis o metagranito "
                "foliado</b>, un material con anisotropía, en contacto con <b>granodiorita maciza</b>.", DEST))
    # 5
    A(Paragraph("5. Lectura geotécnica y exploración que exige", H2))
    for t_ in [
        "<b>Los dos portales caen sobre contactos litológicos.</b> Fueron elegidos en el OE 1 por un criterio geométrico. Un "
        "corrimiento de unos cientos de metros cambia la roca del emboquille. Por eso la Act 3 entregará parámetros por unidad, "
        "dos juegos por portal, y no un valor único.",
        "<b>El portal occidental es el más desfavorable</b>, por litología y por sismo. El Complejo Quebradagrande es un macizo "
        "heterogéneo, con lutitas carbonosas y zonas de cizalla junto al Sistema Romeral. La Falla de Silvia-Pijao (cubierta) está a "
        f"{es_co(sgc['occidental_Calarca']['fallas_10km'][0]['dist_km'])} km, y Calarcá está en amenaza sísmica alta. [F]",
        "<b>No hay dato publicado del espesor del suelo y del saprolito en ninguno de los dos portales</b> [DA]; la memoria de la "
        "plancha 244 describe una meteorización intensa.",
        "<b>Exploración mínima para decidir qué unidad manda en cada emboquille:</b> sondeos con recuperación de núcleo, sísmica "
        "de refracción o MASW, y ensayos índice sobre suelo y roca.",
    ]:
        A(Paragraph("• " + t_, P))
    A(Paragraph("<i>Nota de elaboración: preparado con apoyo de IA (Claude, de Anthropic). Cada cifra se lee de los archivos de los scripts citados, contrastados con las fuentes del SGC.</i>", ParagraphStyle("NE", parent=FUENTE, spaceBefore=0, spaceAfter=0)))
    # Anexo A: plano
    A(NextPageTemplate("h")); A(PageBreak())
    A(Marca("A", "Anexo A. Plano geológico de los emboquilles"))
    A(Paragraph("Anexo A. Plano geológico de los emboquilles", H2))
    w = APAIS[0] - 2 * MARGEN
    figura(LAMINA, "Geología en los emboquilles del túnel sobre las planchas 244 y 243 del SGC",
           "lamina_portales_OE3.py → Visuales/lamina_portales_geologia_OE3 (A3; PDF vectorial disponible en la misma carpeta) [CP]",
           S, w * 0.79, w * 0.79 * 2338 / 3308)
    # Anexo B: recortes
    A(NextPageTemplate("p")); A(PageBreak())
    A(Marca("A", "Anexo B. Recortes de las planchas en cada portal"))
    A(Paragraph("Anexo B. Recortes de las planchas en cada portal", H2))
    lado = es_co(PILImage.open(os.path.join(AQUI, "portal_244_recorte.png")).width / ubi["244"]["px_por_km_recorte"])
    A(Paragraph(f"Recortes de {lado} km de lado centrados en cada portal, sin rótulos añadidos salvo la cruz del portal. La barra de "
                "escala del plano (anexo A) se calcula con la calibración de la tabla " + str(TAB_CAL) + ".", P))
    for pl, key in (("244", "oriental_Ibague"), ("243", "occidental_Calarca")):
        figura(os.path.join(AQUI, f"portal_{pl}_recorte.png"), f"Recorte de la plancha {pl} en el {NOMBRE[key].split(' — ')[0].lower()}",
               f"Plancha {pl} del SGC (tabla 1); recorte de ubicar_portales_planchas_OE3.py [CP]", S, 76 * mm, 76 * mm)
    return S

META = {"rotulo": "OE 3 · Actividad 1 · Verificador", "titulo": "Planos geológicos de los portales del túnel",
        "subtitulo": "Cartografía del Servicio Geológico Colombiano en los emboquilles de Ibagué y Calarcá",
        "ficha": [("Objetivo específico", "OE 3 — Estimar la capacidad portante preliminar del terreno de fundación de las infraestructuras de superficie en los portales"),
                  ("Actividad", "Act 1. Recopilación de la cartografía geológica del Servicio Geológico Colombiano para las planchas del corredor"),
                  ("Entregable / formato", "Planos geológicos · Documento PDF"),
                  ("Periodo", "Bloque 2 del cronograma: 5 oct – 7 nov 2026"),
                  ("Responsable asignado", "Tamayo Osorio Miguel Ángel")],
        "pie": "Semillero GEOPAV · Ferropista Cordillera Central · OE 3 – Act 1", "fecha": "Septiembre de 2026",
        "titulo_pdf": "Planos geológicos de los portales - OE 3 Act 1 - Semillero GEOPAV"}
generar(SALIDA, META, cuerpo)
print("PDF escrito:", SALIDA)
