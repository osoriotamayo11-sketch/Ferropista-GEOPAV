# -*- coding: utf-8 -*-
"""OE 3 · Act 2 — Descarga de capas SGC para el mapa base de susceptibilidad.

Para cada portal baja, en una ventana de ±0,032° (≈ 3,5 km) alrededor del punto:
  susc  → Susceptibilidad por movimientos en masa 1:100.000 (SIMMA/CapasTematicasXEscalas/MapServer/20)
  amen  → Amenaza relativa por movimientos en masa 1:100.000 (SIMMA/CapasTematicasXEscalas/MapServer/15)
  inv   → Inventario SIMMA de movimientos en masa (SIMMA/Capas_Principales/MapServer/1)
Escribe Datos/<capa>_<portal>.geojson (EPSG 4326), recortado a la ventana.
Uso: python descargar_capas_mapa_OE3.py <portal> <capa>   (sin argumentos: todo; puede tardar varios minutos)
Requiere shapely.
"""
import json, os, sys, urllib.parse, urllib.request, datetime
from shapely.geometry import shape, box, mapping

SGC = "https://srvags.sgc.gov.co/arcgis/rest/services/"
PORTALES = {"oriental_Ibague": (-75.1960, 4.3640), "occidental_Calarca": (-75.6520, 4.4800)}
CAPAS = {"susc": ("SIMMA/CapasTematicasXEscalas/MapServer/20", "SUSMM,LEYENDA,PLANCHA"),
         "amen": ("SIMMA/CapasTematicasXEscalas/MapServer/15", "CATAME,PLANCHA"),
         "inv": ("SIMMA/Capas_Principales/MapServer/1", "INV_MOVIMIENTO_MASA_ID,TIPO,SUBTIPO")}
D = 0.032
# maxAllowableOffset = 0,0001° (≈ 11 m): generalización del servidor, muy por debajo del error de la escala 1:100.000.
AQUI = os.path.dirname(os.path.abspath(__file__))

def baja(portal, capa):
    lon, lat = PORTALES[portal]; svc, campos = CAPAS[capa]
    p = {"geometry": f"{lon-D},{lat-D},{lon+D},{lat+D}", "geometryType": "esriGeometryEnvelope", "inSR": 4326,
         "outSR": 4326, "spatialRel": "esriSpatialRelIntersects", "outFields": campos, "returnGeometry": "true", "maxAllowableOffset": 0.0001, "geometryPrecision": 6, "f": "geojson"}
    with urllib.request.urlopen(SGC + svc + "/query?" + urllib.parse.urlencode(p), timeout=900) as r:
        g = json.load(r)
    if "error" in g: raise RuntimeError(g["error"])
    caja = box(lon - D, lat - D, lon + D, lat + D); feats = []
    for f in g["features"]:
        geo = shape(f["geometry"])
        if geo.geom_type not in ("Point", "MultiPoint"): geo = geo.buffer(0).intersection(caja)
        if not geo.is_empty: feats.append({"type": "Feature", "properties": f["properties"], "geometry": mapping(geo)})
    out = {"type": "FeatureCollection", "fuente": SGC + svc, "consultado": datetime.datetime.now().isoformat(timespec="seconds"),
           "ventana_grados": [lon - D, lat - D, lon + D, lat + D], "features": feats}
    ruta = os.path.join(AQUI, "Datos", f"{capa}_{portal}.geojson")
    json.dump(out, open(ruta, "w", encoding="utf-8"), ensure_ascii=False)
    print(portal, capa, len(feats), "entidades →", ruta)

sel_p = [sys.argv[1]] if len(sys.argv) > 1 else list(PORTALES)
sel_c = [sys.argv[2]] if len(sys.argv) > 2 else list(CAPAS)
for p in sel_p:
    for c in sel_c: baja(p, c)
