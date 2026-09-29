# -*- coding: utf-8 -*-
"""OE 3 · Act 2 — Amenaza por movimientos en masa en los portales (servicios SGC).

Para cada portal (coordenadas [CP] del OE 1) consulta:
  1) Zonificación de amenaza relativa por movimientos en masa 1:100.000 (SIMMA,
     CapasTematicasXEscalas capa 15): clase en el punto, distancia a cada clase y % de
     área de cada clase en un círculo de 3 km.
  2) Susceptibilidad 1:100.000 (capa 20) en el punto (ventana de ±55 m).
  3) Geomorfología aplicada a movimientos en masa 1:100.000 (capa 41) en el punto.
  4) Inventario SIMMA de movimientos en masa (Capas_Principales capa 1) a 3 km.
  5) Resumen municipal del Mapa Nacional de Amenaza 1:100.000 (capa 3).
  6) Solo portal occidental: Geomecánica del Quindío (suelos geotécnicos, capa 13;
     geología, capa 19; geomorfología, capa 22).
Uso: python consulta_amenaza_mm_OE3.py [oriental_Ibague|occidental_Calarca]
     (sin argumento corre ambos; cada portal tarda 1–3 min por el tamaño de los polígonos).
Escribe/actualiza consulta_amenaza_mm_OE3.json. Requiere shapely y pyproj.
"""
import json, math, os, sys, urllib.parse, urllib.request, datetime
from shapely.geometry import shape, Point
from shapely.ops import unary_union, transform
from pyproj import Transformer

SGC = "https://srvags.sgc.gov.co/arcgis/rest/services/"
PORTALES = {"oriental_Ibague": (-75.1960, 4.3640), "occidental_Calarca": (-75.6520, 4.4800)}
TR = Transformer.from_crs(4326, 3116, always_xy=True)
SALIDA = "consulta_amenaza_mm_OE3.json"

def get(url, p, t=170):
    with urllib.request.urlopen(url + "/query?" + urllib.parse.urlencode(p), timeout=t) as r:
        d = json.load(r)
    if "error" in d: raise RuntimeError(d["error"])
    return d

def limpia(a):
    return {k: v for k, v in a.items() if v not in (None, "", " ") and "SHAPE" not in k.upper() and k not in ("OBJECTID", "ESRI_OID")}

def en_punto(svc, lon, lat, d=0.0005, campos="*"):
    p = {"geometry": f"{lon-d},{lat-d},{lon+d},{lat+d}", "geometryType": "esriGeometryEnvelope", "inSR": 4326,
         "spatialRel": "esriSpatialRelIntersects", "outFields": campos, "returnGeometry": "false", "f": "json"}
    return [limpia(f["attributes"]) for f in get(SGC + svc, p)["features"]]

def portal(nombre, lon, lat):
    r = {"lon": lon, "lat": lat}
    zon = "SIMMA/CapasTematicasXEscalas/MapServer/15"
    r["amenaza_100k_en_punto"] = en_punto(zon, lon, lat, campos="CATAME,PLANCHA,MAPA")
    d = 0.028
    g = get(SGC + zon, {"geometry": f"{lon-d},{lat-d},{lon+d},{lat+d}", "geometryType": "esriGeometryEnvelope",
                        "inSR": 4326, "outSR": 4326, "spatialRel": "esriSpatialRelIntersects", "outFields": "CATAME",
                        "returnGeometry": "true", "f": "geojson"}, 175)
    pt = Point(TR.transform(lon, lat)); circ = pt.buffer(3000); clases = {}
    for f in g["features"]:
        geo = transform(lambda x, y, z=None: TR.transform(x, y), shape(f["geometry"])).buffer(0).intersection(circ)
        clases.setdefault(f["properties"]["CATAME"], []).append(geo)
    r["amenaza_100k_3km"] = {c: {"dist_m": round(unary_union(v).distance(pt)), "area_pct": round(100 * unary_union(v).area / circ.area, 1)}
                             for c, v in clases.items()}
    r["susceptibilidad_100k_en_punto"] = en_punto("SIMMA/CapasTematicasXEscalas/MapServer/20", lon, lat)
    r["geomorfologia_100k_en_punto"] = [{k: a[k] for k in ("CODGMF", "UNIGMF") if k in a}
                                        for a in en_punto("SIMMA/CapasTematicasXEscalas/MapServer/41", lon, lat)]
    inv = get(SGC + "SIMMA/Capas_Principales/MapServer/1", {"geometry": f"{lon},{lat}", "geometryType": "esriGeometryPoint",
              "inSR": 4326, "outSR": 4326, "distance": 3000, "units": "esriSRUnit_Meter",
              "spatialRel": "esriSpatialRelIntersects", "outFields": "INV_MOVIMIENTO_MASA_ID,TIPO,SUBTIPO",
              "returnGeometry": "true", "f": "json"})
    r["inventario_simma_3km"] = sorted([{**limpia(f["attributes"]), "dist_km": round(math.hypot(
        (f["geometry"]["x"] - lon) * 111.32 * math.cos(math.radians(lat)), (f["geometry"]["y"] - lat) * 110.57), 2)}
        for f in inv["features"]], key=lambda x: x["dist_km"])
    r["resumen_municipal_amenaza_100k_pct_area"] = en_punto(
        "Mapa_Nacional_Amenaza_Mov_Masa_100K/Mapa_Nacional_Amenaza_Movimientos_Masa_100K/MapServer/3", lon, lat)
    if nombre.startswith("occidental"):
        q = "Geomecanica_Por_Regiones/Geomecanica_del_Departamento_del_Quindio/MapServer/"
        s = en_punto(q + "13", lon, lat)
        r["quindio_suelo_geotecnico"] = [{k: a.get(k) for k in ("NOMBRE", "TAXONOMIA", "ORDEN_SUEL", "SIST_UNIFI", "SIMB_UNIFI",
                                          "PRJE_PARTI", "PROFUNDIDA", "RANG_PROF", "LIMITANTES", "COBERTURA")} for a in s]
        r["quindio_geologia_cod"] = en_punto(q + "19", lon, lat)
        r["quindio_geomorfologia_cod"] = en_punto(q + "22", lon, lat)
    return r

sel = sys.argv[1:] or list(PORTALES)
out = json.load(open(SALIDA, encoding="utf-8")) if os.path.exists(SALIDA) else {"portales": {}}
for n in sel:
    out["portales"][n] = portal(n, *PORTALES[n])
    out["portales"][n]["consultado"] = datetime.datetime.now().isoformat(timespec="seconds")
json.dump(out, open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
for n in sel:
    p = out["portales"][n]
    print(n, [a.get("CATAME") for a in p["amenaza_100k_en_punto"]], p["amenaza_100k_3km"],
          [(i.get("SUBTIPO"), i["dist_km"]) for i in p["inventario_simma_3km"]])
