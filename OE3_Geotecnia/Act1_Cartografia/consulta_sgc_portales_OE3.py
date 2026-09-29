# -*- coding: utf-8 -*-
"""OE 3 · Act 1 — Consulta a servicios ArcGIS REST del SGC en los dos portales.

Qué hace: para cada portal (coordenadas de src/data/proyecto.ts, [CP] del OE 1) consulta
  1) la unidad cronoestratigráfica bajo el punto (Mapa Geológico de Colombia 2023, capa 733),
  2) las unidades a 5 km (misma capa),
  3) las fallas a 10 km y su distancia mínima al portal (capa 704),
  4) Aa, Av, Ae, Ad y zona de amenaza NSR-10 del municipio,
  5) las dataciones U–Pb del Catálogo de Dataciones Radiométricas 2015 a 20 km.
Escribe consulta_sgc_portales_OE3.json. Solo biblioteca estándar; distancias con
aproximación equirrectangular local (error < 0,5 % a estas distancias).
Escala del mapa nacional: 1:1.000.000. No sustituye la plancha 1:100.000.
"""
import json, math, urllib.parse, urllib.request, datetime

SGC = "https://srvags.sgc.gov.co/arcgis/rest/services"
GEO = SGC + "/Mapa_Geologico_Colombia/Mapa_Geologico_Colombia_V2023/MapServer"
NSR = SGC + "/Zonas_amenaza_Sismica_NR10/Municipios_Amenaza_NR10/MapServer/0"
DAT = SGC + "/Catalogo_Dataciones_Radiometricas_Colombia/Catalogo_Dataciones_Radiometricas_Colombia_2015/MapServer/0"
PORTALES = {"oriental_Ibague": (-75.1960, 4.3640), "occidental_Calarca": (-75.6520, 4.4800)}

def q(url, lon, lat, dist=None, fields="*", geom=False):
    p = {"geometry": f"{lon},{lat}", "geometryType": "esriGeometryPoint", "inSR": 4326, "outSR": 4326,
         "spatialRel": "esriSpatialRelIntersects", "outFields": fields,
         "returnGeometry": str(geom).lower(), "f": "json"}
    if dist: p.update(distance=dist, units="esriSRUnit_Meter")
    with urllib.request.urlopen(url + "/query?" + urllib.parse.urlencode(p), timeout=90) as r:
        d = json.load(r)
    if "error" in d: raise RuntimeError(d["error"])
    return d["features"]

def km(lon, lat, x, y):
    return math.hypot((x - lon) * 111.32 * math.cos(math.radians(lat)), (y - lat) * 110.57)

def dist_seg(lon, lat, a, b):
    ax, ay = (a[0]-lon)*111.32*math.cos(math.radians(lat)), (a[1]-lat)*110.57
    bx, by = (b[0]-lon)*111.32*math.cos(math.radians(lat)), (b[1]-lat)*110.57
    dx, dy = bx-ax, by-ay; L = dx*dx+dy*dy
    t = 0 if L == 0 else max(0, min(1, -(ax*dx+ay*dy)/L))
    return math.hypot(ax+t*dx, ay+t*dy)

out = {"generado": datetime.datetime.now().isoformat(timespec="seconds"), "portales": {}}
for nombre, (lon, lat) in PORTALES.items():
    r = {"lon": lon, "lat": lat}
    campos = "SimboloUC,Edad,Descripcion"
    r["unidad_bajo_portal"] = [f["attributes"] for f in q(GEO + "/733", lon, lat, fields=campos)]
    vistos = {}
    for f in q(GEO + "/733", lon, lat, 5000, campos):
        vistos[f["attributes"]["SimboloUC"]] = f["attributes"]
    r["unidades_5km"] = list(vistos.values())
    fallas = {}
    for f in q(GEO + "/704", lon, lat, 10000, "NombreFalla,Tipo", True):
        a = f["attributes"]; k = (a.get("NombreFalla") or "(sin nombre)", a.get("Tipo"))
        d = min(dist_seg(lon, lat, p[i], p[i+1]) for p in f["geometry"]["paths"] for i in range(len(p)-1))
        fallas[k] = min(d, fallas.get(k, 1e9))
    r["fallas_10km"] = sorted([{"nombre": k[0], "tipo": k[1], "dist_km": round(v, 1)} for k, v in fallas.items()], key=lambda x: x["dist_km"])
    r["nsr10"] = [{k: f["attributes"][k] for k in ("NOMBRE_MUNICIPIO", "CÓDIGO_MUNICIPIO", "AA", "AV", "AE", "AD", "ZONA_AMENAZA_SÍSMICA")} for f in q(NSR, lon, lat)]
    dat = []
    for f in q(DAT, lon, lat, 20000, "*", True):
        a = f["attributes"]
        if "U" in (a["METODODATACION"] or "") and "Pb" in (a["METODODATACION"] or ""):
            dat.append({"dist_km": round(km(lon, lat, f["geometry"]["x"], f["geometry"]["y"]), 1),
                        "unidad": a["UNIDADGEOLOGICA"], "litologia": a["LITOLOGIA"], "edad_Ma": a["EDADMA"],
                        "error_Ma": a["ERRORMA"], "metodo": a["METODODATACION"], "referencia": a["CITAREFERENCIA"]})
    r["dataciones_UPb_20km"] = sorted(dat, key=lambda x: x["dist_km"])
    out["portales"][nombre] = r

with open("consulta_sgc_portales_OE3.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)
print(json.dumps({n: {"unidad": [u["SimboloUC"] + " " + u["Edad"] for u in p["unidad_bajo_portal"]],
                      "fallas": [(x["nombre"], x["dist_km"]) for x in p["fallas_10km"]],
                      "nsr10": p["nsr10"], "UPb_5_mas_cercanas": [(x["dist_km"], x["unidad"], x["edad_Ma"]) for x in p["dataciones_UPb_20km"][:5]]}
                  for n, p in out["portales"].items()}, ensure_ascii=False, indent=1))
