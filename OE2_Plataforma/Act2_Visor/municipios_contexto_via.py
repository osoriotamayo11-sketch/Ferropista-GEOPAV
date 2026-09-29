# -*- coding: utf-8 -*-
"""Municipios de contexto: los que cruza la vía actual (Ruta 40) y no están en el área de estudio.

El área de estudio del OE 1 son los municipios que cruza el TÚNEL (Ibagué, Cajamarca, Calarcá); de ella
salen porcentajes [CP] que no deben cambiar. La vía actual cruza además otros municipios (Salento, 3,9 km):
se dibujan como contexto para que la vía no se vea «por fuera» de los mapas.
Lee OE1_Topografia/Act1_DEM/limites_igac_tol_qui.geojson [F, IGAC] y limites_area_estudio.geojson,
y via_actual_ruta40.geojson. Escribe public/data/municipios_contexto_via.geojson (simplificado a 0,0005°)
y la copia OE2_Plataforma/Act2_Visor/municipios_contexto_via.geojson. Requiere shapely.
"""
import json, os
from shapely.geometry import shape, mapping, LineString
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))
todos = J(RAIZ, "OE1_Topografia", "Act1_DEM", "limites_igac_tol_qui.geojson")
estudio = {f["properties"]["MpNombre"] for f in J(RAIZ, "OE1_Topografia", "Act1_DEM", "limites_area_estudio.geojson")["features"]}
via = [LineString(f["geometry"]["coordinates"]) for f in J(AQUI, "via_actual_ruta40.geojson")["features"]]
feats = []
for f in todos["features"]:
    n = f["properties"]["MpNombre"]
    if n in estudio: continue
    g = shape(f["geometry"])
    km = sum(g.intersection(l).length for l in via) * 111.0   # aproximación en grados → km, solo para el reporte
    if km > 0:
        feats.append({"type": "Feature", "properties": {"MpNombre": n, "Depto": f["properties"].get("Depto"), "rol": "contexto",
                      "via_km_aprox": round(km, 1)}, "geometry": mapping(g.simplify(0.0005, preserve_topology=True))})
out = {"type": "FeatureCollection", "name": "municipios_contexto_via", "fuente": "IGAC, límites municipales [F]; selección por cruce con la vía actual [CP]", "features": feats}
for r in (os.path.join(AQUI, "municipios_contexto_via.geojson"), os.path.join(RAIZ, "public", "data", "municipios_contexto_via.geojson")):
    json.dump(out, open(r, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print([(f["properties"]["MpNombre"], f["properties"]["via_km_aprox"]) for f in feats])
