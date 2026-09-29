# -*- coding: utf-8 -*-
"""OE 3 — Datos del sitio web (sección OE 3). Consolida, no recalcula.

Lee Act1_Cartografia/consulta_sgc_portales_OE3.json, Act2_Amenaza/consulta_amenaza_mm_OE3.json,
Act2_Amenaza/pendiente_portales_OE3.json y la vía actual (OE2_Plataforma/Act2_Visor/via_actual_ruta40.geojson),
y escribe src/data/oe3_portales.json, que consume el componente del sitio. Única cifra nueva:
la distancia de cada portal a la vía actual [CP] (mínima a los vértices de la polilínea, haversine).
Uso: python OE3_Geotecnia/exportar_web_OE3.py
"""
import json, math, os
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))
sgc = J(AQUI, "Act1_Cartografia", "consulta_sgc_portales_OE3.json")["portales"]
amz = J(AQUI, "Act2_Amenaza", "consulta_amenaza_mm_OE3.json")["portales"]
pen = J(AQUI, "Act2_Amenaza", "pendiente_portales_OE3.json")["portales"]
via = J(RAIZ, "OE2_Plataforma", "Act2_Visor", "via_actual_ruta40.geojson")
vert = [tuple(c) for f in via["features"] for c in f["geometry"]["coordinates"]]

def dist(a, b):
    la1, la2 = math.radians(a[1]), math.radians(b[1])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(math.radians(b[0] - a[0]) / 2) ** 2
    return 2 * 6371008.8 * math.asin(math.sqrt(h))

UNIDAD_PLANCHA = {  # lectura de la leyenda impresa de cada plancha [F]; misma redacción que el producto de la Act 1
    "oriental_Ibague": {"plancha": "244 Ibagué (1982)", "texto": "Contacto entre PCAn (Neises y Anfibolitas de Tierradentro) y Jcdi (Batolito de Ibagué, granodiorita)"},
    "occidental_Calarca": {"plancha": "243 Armenia (1985)", "texto": "Borde de un lente de Kqv (Quebradagrande volcánico: diabasas y andesitas) dentro de Kqs (sedimentario: grauvacas, lutitas, chert, calizas)"},
}
out = {"generado_por": "OE3_Geotecnia/exportar_web_OE3.py", "portales": []}
for key, nombre, mun in (("oriental_Ibague", "Portal oriental", "Ibagué, Tolima"), ("occidental_Calarca", "Portal occidental", "Calarcá, Quindío")):
    s, a, p = sgc[key], amz[key], pen[key]; n = s["nsr10"][0]; c = a["amenaza_100k_3km"]
    alta = c.get("Alta", {}); malta = c.get("Muy Alta", {})
    out["portales"].append({
        "id": key, "nombre": nombre, "municipio": mun, "lat": a["lat"], "lon": a["lon"], "cota_msnm": p["cota_pixel_msnm"],
        "unidad_plancha": UNIDAD_PLANCHA[key], "unidad_1M": {"simbolo": s["unidad_bajo_portal"][0]["SimboloUC"], "edad": s["unidad_bajo_portal"][0]["Edad"]},
        "falla_mas_cercana": {"nombre": s["fallas_10km"][0]["nombre"], "tipo": s["fallas_10km"][0]["tipo"], "dist_km": s["fallas_10km"][0]["dist_km"]},
        "nsr10": {"Aa": n["AA"], "Av": n["AV"], "zona": n["ZONA_AMENAZA_SÍSMICA"]},
        "susceptibilidad_punto": [x["SUSMM"] for x in a["susceptibilidad_100k_en_punto"]],
        "amenaza_punto": a["amenaza_100k_en_punto"][0]["CATAME"],
        "amenaza_3km_pct": {k: v["area_pct"] for k, v in c.items()},
        "amenaza_alta_dist_m": alta.get("dist_m"), "amenaza_muy_alta_dist_m": malta.get("dist_m"),
        "inventario_simma_3km": len(a["inventario_simma_3km"]),
        "pendiente_250m": {"media": p["circulos"]["250"]["media"], "p90": p["circulos"]["250"]["p90"], "pct_mayor_25": p["circulos"]["250"]["pct_mayor_25"]},
        "dist_via_actual_km": round(min(dist((a["lon"], a["lat"]), v) for v in vert) / 1000, 1),
    })
destino = os.path.join(RAIZ, "src", "data", "oe3_portales.json")
json.dump(out, open(destino, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("escrito", destino, [(x["id"], x["dist_via_actual_km"]) for x in out["portales"]])

# ---------------------------------------------------------------- mapas dinámicos (sesión 16)
# Para el mapa interactivo de cada portal: fondo de relieve (JPEG con sus límites) y capas vectoriales
# recortadas a un círculo de 3,3 km, sin partes menores a ~0,18 ha (píxeles sueltos), simplificadas a
# 0,0003° (≈ 33 m) y redondeadas a 5 decimales. Se publican en public/data/oe3_mapas.json (carga diferida), de Act2_Amenaza/Datos/*.geojson (descargar_capas_mapa_OE3.py, SGC).
import numpy as np, tifffile
from PIL import Image
from shapely.geometry import shape, mapping, box, LineString
from matplotlib.colors import LightSource

t = tifffile.TiffFile(os.path.join(RAIZ, "dem_corredor.tif")); pg = t.pages[0]
PX = pg.tags["ModelPixelScaleTag"].value[0]; TP = pg.tags["ModelTiepointTag"].value; X0, Y0 = TP[3], TP[4]
Z = pg.asarray().astype("float64")
SUSMM = {1: "Muy baja", 2: "Baja", 3: "Media", 4: "Alta", 5: "Muy Alta"}

from shapely.geometry import Point, Polygon, MultiPolygon
from shapely import affinity

def _limpia(geo, area_min=1.5e-7):
    """Quita partes y huecos menores a ~0,18 ha: son píxeles sueltos de la zonificación ráster del SGC."""
    partes = geo.geoms if hasattr(geo, "geoms") else [geo]
    buenas = [Polygon(p.exterior, [h for h in p.interiors if Polygon(h).area >= area_min])
              for p in partes if p.geom_type == "Polygon" and p.area >= area_min]
    return MultiPolygon(buenas) if len(buenas) != 1 else buenas[0]

def capa(nombre, key, clase):
    g = J(AQUI, "Act2_Amenaza", "Datos", f"{nombre}_{key}.geojson"); out = []
    lon, lat = amz[key]["lon"], amz[key]["lat"]
    # Círculo de 3,3 km (3 km + margen) como elipse en grados: solo se publica el entorno que el mapa muestra.
    circ = affinity.scale(Point(lon, lat).buffer(1.0, 64), 3300 / (111320 * math.cos(math.radians(lat))), 3300 / 110574)
    for f in g["features"]:
        geo = shape(f["geometry"]).buffer(0).intersection(circ)
        if geo.is_empty: continue
        geo = _limpia(geo)
        if geo.is_empty: continue
        geo = geo.simplify(0.0003, preserve_topology=True)
        gj = json.loads(json.dumps(mapping(geo), default=list))
        def r(c): return [round(c[0], 5), round(c[1], 5)] if isinstance(c[0], float) else [r(x) for x in c]
        gj["coordinates"] = r(gj["coordinates"])
        out.append({"clase": clase(f["properties"]), "geometry": gj})
    return out, g["ventana_grados"]

mapas = {"generado_por": "OE3_Geotecnia/exportar_web_OE3.py", "radio_m": 3000, "portales": {}}
vias = [LineString(f["geometry"]["coordinates"]) for f in via["features"]]
for key in ("oriental_Ibague", "occidental_Calarca"):
    susc, caja = capa("susc", key, lambda p: SUSMM[p["SUSMM"]])
    amen, _ = capa("amen", key, lambda p: p["CATAME"])
    inv = J(AQUI, "Act2_Amenaza", "Datos", f"inv_{key}.geojson")["features"]
    lo0, la0, lo1, la1 = caja
    f0, f1 = int((Y0 - la1) / PX), int(np.ceil((Y0 - la0) / PX)); c0, c1 = int((lo0 - X0) / PX), int(np.ceil((lo1 - X0) / PX))
    dem = Z[f0:f1 + 1, c0:c1 + 1]
    lat = (la0 + la1) / 2; dx = PX * 111320 * np.cos(np.radians(lat)); dy = PX * 110574
    hs = LightSource(azdeg=315, altdeg=45).hillshade(dem, vert_exag=1.5, dx=dx, dy=dy)
    img = Image.fromarray((255 * (0.35 + 0.65 * hs)).clip(0, 255).astype("uint8"), "L").resize((900, 900), Image.LANCZOS)
    img.save(os.path.join(RAIZ, "public", "oe3", f"relieve_{key}.jpg"), quality=84, optimize=True, progressive=True)
    lim = [X0 + c0 * PX, Y0 - (f1 + 1) * PX, X0 + (c1 + 1) * PX, Y0 - f0 * PX]      # [oeste, sur, este, norte] del ráster recortado
    via_clip = []
    for f, l in zip(via["features"], vias):
        g = l.intersection(box(*lim))
        for part in (g.geoms if hasattr(g, "geoms") else [g]):
            if not part.is_empty and part.geom_type == "LineString":
                via_clip.append({"tunel": f["properties"]["tunel"], "coords": [[round(x, 5), round(y, 5)] for x, y in part.simplify(0.0001).coords]})
    mapas["portales"][key] = {"relieve": f"/oe3/relieve_{key}.jpg", "limites": [round(v, 6) for v in lim],
        "portal": [amz[key]["lon"], amz[key]["lat"]], "susceptibilidad": susc, "amenaza": amen,
        "inventario": [{"lon": f["geometry"]["coordinates"][0], "lat": f["geometry"]["coordinates"][1], "subtipo": f["properties"].get("SUBTIPO")} for f in inv],
        "via": via_clip}
d2 = os.path.join(RAIZ, "public", "data", "oe3_mapas.json")
json.dump(mapas, open(d2, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"), default=list)
print("escrito", d2, os.path.getsize(d2) // 1024, "kB")
