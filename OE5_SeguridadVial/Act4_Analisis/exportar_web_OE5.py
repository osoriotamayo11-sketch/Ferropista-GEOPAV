# -*- coding: utf-8 -*-
"""
OE 5 - Exporta al sitio los datos de las dos láminas de la Act 4 para dibujarlas en el
navegador (mapa de sectores críticos y densidad lineal del microdato ANSV).
Semillero de Investigación GEOPAV - Universidad de Ibagué - Paz y Región 2026B

LEE, NO RECALCULA LO QUE YA CALCULÓ OTRO SCRIPT:
  Act3_Siniestros/siniestros_ANSV_corredor.csv          sectores críticos 2015-2019 [F]
  Act3_Siniestros/microdato_ANSV_hechos.csv, _por_km.csv, cruce_prensa_ANSV.csv, _resumen.json
  Act4_Analisis/tasa_post_tunel_OE5.json
  OE1_Topografia/Act4_Trazado/trazado_tunel.geojson, Act1_DEM/DEM_area_estudio.tif
ESCRIBE:
  src/data/mapas_oe5.json            (sin fechas ni datos por víctima: solo agregados por punto)
  public/oe5/relieve_corredor.jpg    sombreado del DEM, fondo del mapa del corredor
  public/oe5/relieve_descenso.jpg    sombreado del DEM, fondo del detalle del descenso
La densidad lineal usa el mismo núcleo y ancho de banda que densidad_lineal_OE5.py [H].
"""
import csv, json, os
import numpy as np
import rasterio
from matplotlib.colors import LightSource, LinearSegmentedColormap
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
OE5 = os.path.dirname(BASE); RAIZ = os.path.dirname(OE5)
ACT3 = os.path.join(OE5, "Act3_Siniestros"); OE1 = os.path.join(RAIZ, "OE1_Topografia")
DEM = os.path.join(OE1, "Act1_DEM", "DEM_area_estudio.tif")
PUB = os.path.join(RAIZ, "public", "oe5"); DATA = os.path.join(RAIZ, "src", "data")

CORREDOR = (-75.70, -75.15, 4.33, 4.58)     # misma ventana que la lámina de densidad
DESCENSO = (-75.6480, -75.5900, 4.5090, 4.5410)  # misma ventana que el detalle de la lámina
BW = 1.5

def leer(ruta, sep=","):
    with open(ruta, encoding="utf-8-sig") as fh: return list(csv.DictReader(fh, delimiter=sep))

def relieve(ventana, ancho_px, salida):
    lon0, lon1, lat0, lat1 = ventana
    with rasterio.open(DEM) as src:
        win = rasterio.windows.from_bounds(lon0, lat0, lon1, lat1, src.transform)
        dem = src.read(1, window=win).astype(float); ext = rasterio.windows.bounds(win, src.transform)
    dem[dem <= -1000] = np.nan
    base = np.nan_to_num(dem, nan=np.nanmin(dem))
    sombra = LightSource(azdeg=315, altdeg=45).hillshade(base, vert_exag=1.0, dx=30, dy=30)
    rampa = LinearSegmentedColormap.from_list("t", ["#F7F9FB", "#E4E9EF", "#CBD5E1", "#AEB9C7"])
    n = (base - np.nanmin(base)) / (np.nanmax(base) - np.nanmin(base))
    color = rampa(n)[..., :3]
    mezcla = color * (0.45 + 0.55 * sombra[..., None])
    img = Image.fromarray((np.clip(mezcla, 0, 1) * 255).astype(np.uint8))
    alto = round(ancho_px * img.height / img.width)
    img.resize((ancho_px, alto), Image.LANCZOS).save(salida, quality=84, optimize=True, progressive=True)
    return [round(v, 6) for v in ext]  # [lon0, lat0, lon1, lat1] reales de la ventana leída

# ---------------------------------------------------------------- insumos
sec = leer(os.path.join(ACT3, "siniestros_ANSV_corredor.csv"), ";")
hechos = leer(os.path.join(ACT3, "microdato_ANSV_hechos.csv"))
por_km = leer(os.path.join(ACT3, "microdato_ANSV_por_km.csv"))
prensa = leer(os.path.join(ACT3, "cruce_prensa_ANSV.csv"))
resumen = json.load(open(os.path.join(ACT3, "microdato_ANSV_resumen.json"), encoding="utf-8"))
tasa = json.load(open(os.path.join(BASE, "tasa_post_tunel_OE5.json"), encoding="utf-8"))
tra = json.load(open(os.path.join(OE1, "Act4_Trazado", "trazado_tunel.geojson"), encoding="utf-8"))
xy = tra["features"][0]["geometry"]["coordinates"]
paso = max(1, len(xy) // 60)
trazado = [[round(p[0], 5), round(p[1], 5)] for p in xy[::paso]]
if trazado[-1] != [round(xy[-1][0], 5), round(xy[-1][1], 5)]:
    trazado.append([round(xy[-1][0], 5), round(xy[-1][1], 5)])

conf = lambda z: "99 %" if abs(z) >= 2.58 else "95 %" if abs(z) >= 1.96 else "90 %" if abs(z) >= 1.65 else "n.s."
sectores = [{"pr": "PR " + r["pr"], "fallecidos": int(r["fallecidos"]), "lon": float(r["longitud"]),
             "lat": float(r["latitud"]), "gi_z": float(r["gizscore"]), "confianza": conf(float(r["gizscore"])),
             "entidad": "ANI" if r["entidad"].upper().startswith("ANI") else "INVÍAS", "tramo": r["tramo"],
             "en_tasa": r["en_el_paso"] == "Si"} for r in sec]

puntos = {}
for h in hechos:
    k = (round(float(h["lon"]), 6), round(float(h["lat"]), 6))
    p = puntos.setdefault(k, {"lon": k[0], "lat": k[1], "km": float(h["km"]), "tramo": h["tramo"],
                              "municipio": h["municipio"], "hechos": 0, "hechos_fatales": 0,
                              "fallecidos": 0, "lesionados": 0})
    p["hechos"] += 1; p["fallecidos"] += int(h["fallecidos"]); p["lesionados"] += int(h["lesionados"])
    p["hechos_fatales"] += 1 if int(h["fallecidos"]) else 0
puntos = sorted(puntos.values(), key=lambda p: -p["hechos"])
assert sum(p["hechos"] for p in puntos) == resumen["hechos"], "PARADA: hechos no cuadran con el resumen"

fin = resumen["limites_tramo_km"]["fin"]
x = np.round(np.arange(0, fin + 1e-9, 0.25), 2)
kmh = np.array([float(h["km"]) for h in hechos])
dens = np.exp(-0.5 * ((x[:, None] - kmh[None, :]) / BW) ** 2).sum(1) / (BW * np.sqrt(2 * np.pi))

salida = {
    "_fuente": "Generado por OE5_SeguridadVial/Act4_Analisis/exportar_web_OE5.py. NO editar a mano.",
    "corredor": {"bounds": relieve(CORREDOR, 1400, os.path.join(PUB, "relieve_corredor.jpg")),
                 "img": "/oe5/relieve_corredor.jpg"},
    "descenso": {"bounds": relieve(DESCENSO, 900, os.path.join(PUB, "relieve_descenso.jpg")),
                 "img": "/oe5/relieve_descenso.jpg"},
    "trazado": trazado,
    "portales": {"oriental": trazado[0], "occidental": trazado[-1]},
    "sectores": sectores,
    "microdato": {
        "resumen": resumen, "tasa_post_tunel": tasa, "puntos": puntos,
        "por_km": [{k: (int(v) if k not in ("tramo",) else v) for k, v in r.items()} for r in por_km],
        "prensa": prensa,
        "densidad": {"bw_km": BW, "paso_km": 0.25, "valores": [round(float(v), 4) for v in dens]},
    },
}
with open(os.path.join(DATA, "mapas_oe5.json"), "w", encoding="utf-8") as fh:
    json.dump(salida, fh, ensure_ascii=False, indent=1)
print("OK", len(puntos), "puntos,", len(sectores), "sectores, trazado", len(trazado), "vértices; densidad máx", round(float(dens.max()), 2))
