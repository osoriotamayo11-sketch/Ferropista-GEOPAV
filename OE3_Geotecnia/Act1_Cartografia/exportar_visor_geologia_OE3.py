# -*- coding: utf-8 -*-
"""
Datos del visor web de geología de los portales — OE 3, Actividad 1 (sesión 17).

Entrada : Plancha_244_Ibague_mapa.pdf, Plancha_243_Armenia_mapa.pdf  (SGC/INGEOMINAS, 1:100.000)
          ubicacion_portales_planchas_OE3.json  (posición del portal en la plancha, escala)
Salida  : public/oe3/geologia/<portal>.jpg           recorte limpio (sin la cruz) a 288 ppp
          public/oe3/geologia/<portal>_<unidad>.png  máscara de cada unidad (para resaltarla)
          src/data/oe3_geologia.json                 datos del visor

Método [CP]: las planchas son PDF vectoriales con rellenos de color plano. El color de cada
unidad se leyó en su recuadro de la leyenda impresa [F] y coincide exactamente con el relleno
del mapa. La máscara de una unidad son los píxeles del recorte con ese color exacto, con un
cierre morfológico de 5 px (tapa curvas de nivel y rótulos que la cruzan) y una apertura de 9 px
(quita vías y líneas dibujadas con el mismo gris del Cono Aluvial, ≈ 80 m de ancho mínimo retenido). El área de cada
unidad en el recorte y su distancia al portal se miden sobre esa máscara con la escala
px_por_km del recorte (≈113 px/km). Las descripciones de las unidades son la leyenda impresa
de cada plancha, transcrita [F].
"""
import json, os, subprocess
import numpy as np
from PIL import Image, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
DEST_IMG = os.path.join(RAIZ, "public", "oe3", "geologia")
os.makedirs(DEST_IMG, exist_ok=True)
ubi = json.load(open(os.path.join(AQUI, "ubicacion_portales_planchas_OE3.json"), encoding="utf-8"))

R, H = 288, 110                 # mismos parámetros del recorte de la lámina (ubicar_portales_planchas_OE3.py)
S = R / 72

PLANCHAS = {
  "244": {"pdf": "Plancha_244_Ibague_mapa.pdf", "nombre": "Portal oriental — Ibagué, Tolima",
          "fuente": "Plancha 244 Ibagué, 1:100.000 (Mosquera, Núñez y Vesga, 1982; INGEOMINAS/SGC). Leyenda impresa de la plancha.",
          "unidades": [
    ("Qca", "#999999", "Cono Aluvial de Ibagué", "Cuaternario",
     "Cantos de rocas extrusivas e intrusivas y algunas metamórficas, en matriz arenácea y areno-tobácea."),
    ("Tsh", "#ffff80", "Formación Honda", "Terciario",
     "Areniscas, arcillolitas y niveles conglomeráticos de color gris verdoso, ocasionalmente coloración rojiza."),
    ("Tad", "#ffd1dd", "Rocas hipoabisales", "Terciario",
     "Rocas porfiríticas y afaníticas de composición dacítica–andesítica."),
    ("Jcdi", "#f2c0d9", "Batolito de Ibagué", "Mesozoico (Jurásico)",
     "Granodiorita biotítico-hornbléndica, medio a grosogranular, con variaciones texturales y composicionales a cuarzodiorita y cuarzomonzonita."),
    ("PCAn", "#bc9e8f", "Neises y Anfibolitas de Tierradentro", "Precámbrico",
     "Predominantemente neises cuarzo-feldespático-biotíticos."),
    ("PCAa", "#d9c4bf", "Neises y Anfibolitas de Tierradentro", "Precámbrico",
     "Anfibolitas y neises anfibólicos con efectos diaftoríticos, con intercalaciones menores de neises micáceos y mármoles."),
  ]},
  "243": {"pdf": "Plancha_243_Armenia_mapa.pdf", "nombre": "Portal occidental — Calarcá, Quindío",
          "fuente": "Plancha 243 Armenia, 1:100.000 (McCourt, Mosquera, Nivia y Núñez, 1985; INGEOMINAS/SGC). Leyenda impresa de la plancha.",
          "unidades": [
    ("TQa", "#ffffb3", "Formación Armenia", "Plio-pleistoceno",
     "Depósitos no consolidados, cenizas volcánicas, flujos de lodo y depósitos de piedemonte."),
    ("Kqs", "#65ff00", "Formación Quebradagrande — miembros sedimentarios-volcánicos", "Cretácico (Aptiano)",
     "Principalmente rocas sedimentarias marinas: grauvacas, areniscas, calizas, lutitas y chert. Intercalaciones de vulcanitas básicas. Localmente cataclasadas."),
    ("Kqv", "#ffccdb", "Formación Quebradagrande — rocas volcánicas", "Cretácico (Aptiano)",
     "Intercalaciones de rocas volcánicas submarinas de composición intermedia a básica, principalmente diabasas y andesitas. Localmente estructuras almohadilladas. Sectores de intensa cataclasis."),
    ("Kdi", "#ffccff", "Complejo de Córdoba", "Cretácico",
     "Principalmente diorita con variaciones composicionales a granodiorita. Edad 77 ± 3 m.a. (K/Ar)."),
    ("Ku", "#f7bac0", "Rocas ultramáficas", "Cretácico",
     "Rocas ultramáficas serpentinizadas y tectonizadas. Localmente con fragmentos de eclogitas y anfibolitas eclogíticas."),
  ]},
}

hexrgb = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
salida = {"generado_por": "OE3_Geotecnia/Act1_Cartografia/exportar_visor_geologia_OE3.py",
          "metodo": "Máscara por color exacto de la leyenda + cierre de 5 px y apertura de 9 px; áreas y distancias [CP] con la escala del recorte.",
          "portales": []}

for n, p in PLANCHAS.items():
    u = ubi[n]; pid = u["portal"]; x, y = u["portal_pt"]
    X0, Y0, W = int((x - H) * S), int((y - H) * S), int(2 * H * S)
    base = os.path.join(DEST_IMG, f"_tmp_{pid}")
    subprocess.run(["pdftoppm", "-r", str(R), "-png", "-singlefile", "-x", str(X0), "-y", str(Y0),
                    "-W", str(W), "-H", str(W), os.path.join(AQUI, p["pdf"]), base], check=True)
    im = Image.open(base + ".png").convert("RGB")
    im.save(os.path.join(DEST_IMG, f"{pid}.jpg"), quality=86, optimize=True, progressive=True)
    os.replace(base + ".png", os.path.join(RAIZ, "Claude outputs", f"_borrar_{pid}_recorte_tmp.png"))  # la VM no borra
    a = np.asarray(im).astype(int)
    cx, cy = x * S - X0, y * S - Y0
    kpx = u["px_por_km_recorte"]
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    unidades = []
    for sim, col, nom, edad, desc in p["unidades"]:
        m = np.all(a == np.array(hexrgb(col)), axis=2)
        mi = (Image.fromarray((m * 255).astype("uint8"))
              .filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))    # cierre: tapa curvas y rótulos
              .filter(ImageFilter.MinFilter(9)).filter(ImageFilter.MaxFilter(9)))   # apertura: quita vías y líneas del mismo gris
        m2 = np.asarray(mi) > 0
        if m2.sum() == 0:
            print("  sin píxeles:", sim); continue
        d = np.sqrt((xx[m2] - cx) ** 2 + (yy[m2] - cy) ** 2).min() / kpx * 1000
        rgba = np.zeros((*m2.shape, 4), dtype="uint8"); rgba[m2] = (255, 255, 255, 255)
        nombre_m = f"{pid}_{sim}.png"
        Image.fromarray(rgba).convert("LA").save(os.path.join(DEST_IMG, nombre_m), optimize=True)
        unidades.append({"simbolo": sim, "color": col, "nombre": nom, "edad": edad, "descripcion": desc,
                         "area_pct": round(float(m2.mean()) * 100, 1),
                         "dist_portal_m": int(round(d, -1)),
                         "mascara": f"/oe3/geologia/{nombre_m}"})
    unidades.sort(key=lambda q: q["dist_portal_m"])
    salida["portales"].append({"id": pid, "plancha": n, "nombre": p["nombre"], "fuente": p["fuente"],
                               "imagen": f"/oe3/geologia/{pid}.jpg", "lado_px": W,
                               "px_por_km": kpx, "lado_km": round(W / kpx, 2),
                               "portal_px": [round(cx, 1), round(cy, 1)], "unidades": unidades})
    print(pid, W, [(q["simbolo"], q["area_pct"], q["dist_portal_m"]) for q in unidades])

json.dump(salida, open(os.path.join(RAIZ, "src", "data", "oe3_geologia.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
