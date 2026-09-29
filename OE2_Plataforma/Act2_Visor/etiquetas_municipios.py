"""
Puntos de etiqueta de los municipios del visor 3D (sesión 17).

Entrada : public/data/limites_area_estudio.geojson   (área de estudio, IGAC)
          public/data/municipios_contexto_via.geojson (contexto, IGAC)
          public/data/trazado_tunel.geojson           (trazado del OE 1)
          public/data/via_actual_ruta40.geojson       (vía actual, OSM)
          public/oe1/dem_estudio_90m.tif              (extensión del relieve)
Salida  : public/data/etiquetas_municipios.json

Método: cada polígono se recorta a la extensión del DEM (lo que se ve en el
visor), se le quita una franja de 1,5 km alrededor del trazado y de la vía
para que el nombre no tape las líneas, y se toma su polo de inaccesibilidad
(shapely.polylabel): el punto interior más alejado del borde. Si la franja
dejara el polígono vacío, se usa el polígono recortado sin franja.
"""
import json, os
from PIL import Image
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union
from shapely.ops import polylabel

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
P = lambda *a: os.path.join(RAIZ, *a)
J = lambda p: json.load(open(p, encoding="utf-8"))

im = Image.open(P("public", "oe1", "dem_estudio_90m.tif"))
tp, sc = im.tag_v2[33922], im.tag_v2[33550]; w, h = im.size
x0, y1 = tp[3], tp[4]
ext = box(x0, y1 - h * sc[1], x0 + w * sc[0], y1)
margen = ext.buffer(-0.01)  # ~1 km dentro del borde del relieve

KM = 1 / 111.0
lineas = []
for f in ("trazado_tunel.geojson", "via_actual_ruta40.geojson"):
    for ft in J(P("public", "data", f))["features"]:
        lineas.append(shape(ft["geometry"]))
franja = unary_union(lineas).buffer(1.5 * KM)

salida = []
for f, rol in (("limites_area_estudio.geojson", "estudio"), ("municipios_contexto_via.geojson", "contexto")):
    for ft in J(P("public", "data", f))["features"]:
        g = shape(ft["geometry"]).intersection(margen)
        if g.is_empty:
            continue
        libre = g.difference(franja)
        base = libre if not libre.is_empty and libre.area > 0.02 * g.area else g
        if base.geom_type == "MultiPolygon":
            base = max(base.geoms, key=lambda p: p.area)
        pt = polylabel(base, tolerance=0.0005)
        salida.append({"nombre": ft["properties"]["MpNombre"], "rol": rol,
                       "lon": round(pt.x, 5), "lat": round(pt.y, 5),
                       "fuera_de_franja": base is not g})

json.dump({"generado_por": "OE2_Plataforma/Act2_Visor/etiquetas_municipios.py",
           "metodo": "polylabel del polígono recortado al relieve, sin franja de 1,5 km alrededor del trazado y la vía",
           "etiquetas": salida}, open(P("public", "data", "etiquetas_municipios.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
for s in salida: print(s)
