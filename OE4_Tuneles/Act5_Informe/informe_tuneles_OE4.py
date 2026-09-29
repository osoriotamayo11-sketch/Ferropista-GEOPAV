# -*- coding: utf-8 -*-
"""OE 4 · Actividad 5 — «Informe de túneles» · Documento PDF (informe de métodos constructivos subterráneos).

CONSOLIDA, NO RECALCULA. Lee los JSON de las Act 1-4 del OE 4 y las láminas de OE4_Tuneles/Visuales/.
Plantilla: OE3_Geotecnia/plantilla_documentos_OE3.py (estándar del semillero). Salida: Informe_tuneles_OE4.pdf
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
OE4 = os.path.dirname(AQUI)
RAIZ = os.path.dirname(OE4)
sys.path.insert(0, os.path.join(RAIZ, "OE3_Geotecnia"))
from plantilla_documentos_OE3 import *          # noqa: F401,F403

J = lambda *p: json.load(open(os.path.join(OE4, *p), encoding="utf-8"))
A1 = J("Act1_Litologia", "matriz_litologica_OE4.json")
A2 = J("Act2_Sectorizacion", "sectorizacion_TBM_OE4.json")
A3 = J("Act3_Sostenimiento", "sostenimiento_OE4.json")
A4 = J("Act4_Ventilacion", "ventilacion_OE4.json")
VIS = os.path.join(OE4, "Visuales")
SALIDA = os.path.join(AQUI, "Informe_tuneles_OE4.pdf")
COL = lambda *w: [x * mm for x in w]
km = lambda m: es_co(m / 1000, 1)


def cuerpo(doc):
    S = []; A = S.append
    Lt = A2["longitud_m"]
    r2 = A2["resumen_m"]
    A(Paragraph("Marcas de origen: <b>[F]</b> fuente citada · <b>[CP]</b> cálculo propio reproducible · <b>[H]</b> hipótesis declarada · <b>[DA]</b> dato pendiente.", NOTA))
    A(Paragraph("1. Objeto, alcance y resultado", H2))
    A(Paragraph("Este informe cierra el OE 4. Estructura, a nivel conceptual, la metodología de excavación del túnel de base Ferropista entre "
                "Ibagué y Calarcá: dónde conviene una tuneladora y dónde el método convencional, qué sostenimiento primario exigiría este último "
                "y cómo se ventilaría el túnel. Se apoya solo en cartografía geológica regional del Servicio Geológico Colombiano, en el trazado "
                "y la cobertura del OE 1 y en fuentes técnicas publicadas; no hay sondeos a la cota del túnel.", P))
    A(Paragraph(f"<b>Resultado.</b> Con parámetros típicos, {km(r2['Típico']['FAVORABLE'])} km de los {km(Lt)} km del eje "
                f"({es_co(100 * r2['Típico']['FAVORABLE'] / Lt, 0)} %) son favorables para una tuneladora de doble escudo: rocas graníticas y "
                "gneises del lado oriental y el pórfido central. El resto exige método convencional, sobre todo por <b>squeezing</b> (cierre "
                "de la sección por fluencia del macizo) en los esquistos del Complejo Cajamarca y en el Complejo Quebradagrande bajo coberturas de "
                "500 a 2.000 m. La proporción cambia mucho con los parámetros: de "
                f"{es_co(100 * r2['Mínimo']['FAVORABLE'] / Lt, 0)} % a {es_co(100 * r2['Máximo']['FAVORABLE'] / Lt, 0)} % favorable. "
                "La propuesta del proponente (43 % con tuneladora, dia. 22) cae dentro de ese rango, pero no se puede confirmar sin exploración.", DEST))
    A(Paragraph("2. Caracterización del macizo (Act 1)", H2))
    titulo_tabla("Tramos litológicos del eje según el Mapa Geológico de Colombia 2023", S)
    A(tabla(filas(["Tramo", "Abscisas (km)", "Unidad MGC", "Litología", "Cobertura media (m)"],
                  [[t["tramo"], f"{es_co(t['pk_ini'] / 1000, 1)} – {es_co(t['pk_fin'] / 1000, 1)}", t["simbolo"], t["descripcion"], es_co(t["cob_med"], 0)]
                   for t in A1["tramos"]]), COL(14, 26, 24, 80, 26)))
    A(fuente("Matriz_litologica_OE4.xlsx (Act 1), a partir de los servicios del SGC [F] y del perfil del OE 1 [CP]."))
    fm = [f for f in A1["fallas"] if f["fuente"] == "MGC 2023"]
    A(Paragraph(f"El mapa 1:1.000.000 marca {len(fm)} fallas que cortan el eje: " + "; ".join(f"{f['nombre']} (PK {es_co(f['pk'] / 1000, 1)} km)" for f in fm) +
                ". Todas coinciden con el Atlas 2007 a menos de 300 m. La cartografía del Tolima añade al menos una en el PK 26,8 km.", P))
    ll = A1["analogo_linea"]
    A(Paragraph(f"<b>Análogo medido: el Túnel de La Línea.</b> Su extremo oriental está a {es_co(ll['geometria']['dist_extremos'][0], 0)} m en planta del eje "
                f"(PK {es_co(ll['geometria']['pk_extremos'][0] / 1000, 1)} km) y cruza el mismo macizo unos 1.000 m por encima de la rasante. "
                f"Allí se atravesaron 8 zonas de falla que suman {es_co(ll['suma_fallas_m'], 0)} m, el {es_co(100 * ll['fraccion_en_falla'], 0)} % del túnel "
                f"(Dávila, 2015) [F→CP]; con solo las fallas del mapa nacional este eje tendría entre {es_co(100 * A1['fraccion_en_falla_MGC'][0], 1)} y "
                f"{es_co(100 * A1['fraccion_en_falla_MGC'][2], 1)} % en falla. El mapa regional subestima las fallas, y así se declara.", P))
    A(Paragraph("3. Sectorización para tuneladora (Act 2)", H2))
    A(Paragraph(f"Para cada abscisa se estimó la resistencia del macizo σcm y la deformación del túnel sin soporte ε = 0,2·(σcm/p0)⁻² de Hoek y "
                f"Marinos (2000), con p0 = γ·cobertura [F/H]. Es favorable para tuneladora si ε < {es_co(A2['umbrales']['A'], 0)} % y la roca intacta "
                f"tiene al menos {es_co(A2['umbrales']['sci_dos'], 0)} MPa (campo principal de la tuneladora de doble escudo, DAUB 2025) [F]; "
                f"condicionada si ε está entre 1 y 2,5 %; desfavorable si ε ≥ 2,5 %, en zona de falla o en el emboquille (cobertura < 2 D = "
                f"{es_co(A2['H_emboquille_m'], 0)} m) [H].", P))
    titulo_tabla("Longitud del eje por aptitud para tuneladora", S)
    A(tabla(filas(["Caso de parámetros", "Favorable (km)", "Condicionada (km)", "Desfavorable → convencional (km)"],
                  [[c, km(r2[c]["FAVORABLE"]), km(r2[c]["CONDICIONADA"]), km(r2[c]["DESFAVORABLE"])] for c in ("Mínimo", "Típico", "Máximo")] +
                  [["Propuesta (dia. 22) [F]", "27,5 de 64,2 km de túneles", "—", "36,7 km"]]), COL(44, 36, 36, 50)))
    A(fuente("sectorizacion_TBM_OE4.json [CP]; la propuesta cuenta los túneles principales con bypass (64,2 km), no solo el eje."))
    A(Paragraph("4. Sostenimiento primario de los tramos convencionales (Act 3)", H2))
    r3 = A3["resumen_m"]
    A(Paragraph(f"La presión de soporte que limita la deformación al {es_co(A3['eps_obj'], 0)} % se despejó de la ecuación 4 de Hoek y Marinos (2000) "
                f"y se comparó, con un factor de {es_co(A3['FS'], 1)}, con la capacidad de cinco clases de sostenimiento (figura 8 de Hoek, cap. 12) [F/CP/H]. "
                f"Con parámetros típicos, {km(r3['Típico']['S-V'])} km quedan en la clase S-V: la presión requerida supera cualquier sostenimiento "
                f"rígido y hace falta sostenimiento cedente con deformación controlada. Con parámetros máximos baja a {km(r3['Máximo']['S-V'])} km. "
                "La experiencia de La Línea, donde la solera plana falló en la Falla de La Soledad, respalda cerrar el anillo con contrabóveda en "
                "las clases S-III a S-V (Dávila, 2015) [F].", P))
    titulo_tabla("Longitud por clase de sostenimiento (km)", S)
    cls = ["TBM", "S-I", "S-II", "S-III", "S-IV", "S-V"]
    A(tabla(filas(["Caso"] + ["Tuneladora" if c == "TBM" else c for c in cls],
                  [[c] + [km(r3[c][k]) for k in cls] for c in ("Mínimo", "Típico", "Máximo")]), COL(26, 24, 20, 20, 20, 20, 20)))
    A(fuente("sostenimiento_OE4.json (Act 3) [CP]."))
    A(Paragraph("5. Ventilación longitudinal (Act 4)", H2))
    A(Paragraph("Se plantea ventilación longitudinal: en operación, el efecto pistón del tren y ventiladores de chorro en los portales; en incendio, "
                "impulsión hacia el fuego con velocidad igual o mayor que la crítica y extracción en una estación central, aprovechando el bypass "
                "de cruce de convoyes de la ponencia (dia. 23) [H]. La velocidad crítica se calculó con las ecuaciones de NFPA 502 para incendios "
                "de camión de 70 a 200 MW, el rango de diseño que adoptó esa norma tras los ensayos de Runehamar (Ingason, 2008) [F].", P))
    titulo_tabla("Velocidad crítica y caudal de aire por potencia del incendio", S)
    A(tabla(filas(["Potencia del incendio", "Velocidad crítica (m/s)", "Caudal (m³/s)"],
                  [[f"{c['HRR_MW']} MW", es_co(c["Vc_m_s"], 2), es_co(c["caudal_m3_s"], 0)] for c in A4["casos"]]), COL(50, 50, 50)))
    A(fuente(f"ventilacion_OE4.json [CP]; sección de {es_co(A4['area_m2'], 1)} m² (dia. 22) [CP de F]."))
    A(Paragraph("6. Metodología recomendada", H2))
    for t in [
        "<b>Tuneladora de doble escudo</b> en los tramos graníticos y gnéisicos del lado oriental (≈ PK 0,7-16 km, con los cruces de las fallas "
        "de Ibagué y Chapetón-Pericos preparados con tratamiento previo) y en el pórfido central, si la exploración confirma parámetros típicos o mejores.",
        "<b>Método convencional con sostenimiento cedente</b> en los esquistos (T4, T6) y en el Complejo Quebradagrande (T7) bajo coberturas "
        "altas, con avances cortos, contrabóveda cerrada y monitoreo de convergencias (clases C-E de Hoek y Marinos, 2000).",
        "<b>Frentes múltiples</b> desde galerías de acceso intermedias (la ponencia prevé 16 km de galerías) para no depender de un solo frente "
        "en 30 km de terreno difícil [H].",
        "<b>Exploración previa decisiva:</b> galería piloto como la de La Línea, sondeos profundos orientados en T4, T6 y T7, ensayos de fluencia en "
        "esquistos grafíticos y medición del esfuerzo in situ y de la temperatura de la roca.",
    ]:
        A(Paragraph("• " + t, P))
    A(Paragraph("7. Qué no afirma este informe", H2))
    for t in ["No es un diseño: todos los parámetros de macizo son regionales o supuestos; los resultados son rangos.",
              "No evalúa el agua subterránea, la temperatura de la roca, los gases ni la sismicidad durante la construcción.",
              "No verifica la sección transversal, el gálibo ni la vía: la ponencia no los publica.",
              "No reemplaza el análisis numérico que Hoek y Marinos recomiendan cuando el squeezing es significativo."]:
        A(Paragraph("• " + t, P))
    A(Paragraph("<i>Nota de elaboración: preparado con apoyo de IA (Claude, de Anthropic). Cada cifra se lee de los JSON de los scripts de las Act 1-4; "
                "las fuentes se leyeron en el original descargado.</i>", ParagraphStyle("NE", parent=FUENTE, spaceBefore=0, spaceAfter=0)))
    A(Paragraph("Referencias", H2))
    for r_ in ["Servicio Geológico Colombiano (2023). Mapa Geológico de Colombia 1:1.000.000; Atlas Geológico de Colombia 2007 1:500.000; geología del Tolima y del Quindío. Servicios ArcGIS REST.",
               "Hoek, E. y Marinos, P. (2000). Predicting tunnel squeezing problems in weak heterogeneous rock masses. Tunnels and Tunnelling International.",
               "Hoek, E. Practical Rock Engineering, cap. 12 «Tunnels in weak rock». Rocscience.",
               "DAUB (2025). Recommendations for the Selection of Tunnel Boring Machines, apéndice 3.2.",
               "Castro Caicedo, Á. J. y Pérez Pérez, D. M. (2013). Correlaciones entre las clasificaciones Q y RMR en el túnel exploratorio de La Línea. Boletín de Ciencias de la Tierra 34.",
               "Dávila, H. (2015). Túnel II Centenario, terrenos encontrados y su análisis de comportamiento. Revista Vial.",
               "Ingason, H. (2008). State of the art of tunnel fire research. Fire Safety Science 9, IAFSS.",
               "Thunderhead Engineering (2026). Critical velocity in tunnel fires (ecuaciones de NFPA 502). Documentación de PyroSim 2026.1.",
               "Fernández Ordóñez, H. O. (2025). Túnel para cruce férreo de la Cordillera Central de los Andes. XX Seminario Andino de Túneles, SAI."]:
        A(Paragraph(r_, NOTA))
    # anexos
    w = APAIS[0] - 2 * MARGEN
    for letra, img, tit, fte in (("A", "plano_sectorizacion_TBM_OE4.png", "Plano de sectorización para tuneladora (Act 2)", "sectorizacion_TBM_OE4.py [CP]; DXF: Plano_sectorizacion_TBM_OE4.dxf"),
                                 ("B", "diagrama_ventilacion_OE4.png", "Diagrama de flujo de aire (Act 4)", "ventilacion_OE4.py [CP]")):
        A(NextPageTemplate("h")); A(PageBreak())
        A(Marca("A", f"Anexo {letra}. {tit}"))
        A(Paragraph(f"Anexo {letra}. {tit}", H2))
        figura(os.path.join(VIS, img), tit, fte, S, w * 0.8, w * 0.8 * 2338 / 3308)
    return S


META = {"rotulo": "OE 4 · Actividad 5 · Producto", "titulo": "Informe de métodos constructivos subterráneos",
        "subtitulo": "Tuneladora frente a método convencional en el túnel de base Ferropista, a partir de la geología regional del macizo",
        "ficha": [("Objetivo específico", "OE 4 — Estructurar la metodología de excavación recomendada, contrastando el método mecanizado con tuneladora frente al método convencional"),
                  ("Actividad", "Act 5. Elaboración del informe de métodos constructivos subterráneos"),
                  ("Entregable / formato", "Informe de túneles · Documento PDF"),
                  ("Periodo", "Bloque 2 del cronograma: 5 oct – 7 nov 2026"),
                  ("Responsable asignado", "Castaño Cifuentes Maicol Stiven"),
                  ("Apoyo en la ejecución", "Tamayo Osorio Miguel Ángel, con apoyo de IA (Claude)")],
        "pie": "Semillero GEOPAV · Ferropista Cordillera Central · OE 4 – Act 5", "fecha": "Septiembre de 2026",
        "titulo_pdf": "Informe de métodos constructivos subterráneos - OE 4 Act 5 - Semillero GEOPAV"}
generar(SALIDA, META, cuerpo)
print("PDF escrito:", SALIDA)
