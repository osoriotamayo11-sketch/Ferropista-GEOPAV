# -*- coding: utf-8 -*-
"""OE 3 · Act 2 — Pendiente local del terreno en los portales (Copernicus DEM GLO-30).

Lee ../../dem_corredor.tif (EPSG 4326, paso 1"), calcula la pendiente por el método de Horn
(ventana 3x3) con el tamaño de píxel convertido a metros en la latitud de cada portal, y reporta:
  - cota y pendiente en el píxel del portal (control: cotas [CP] del OE 1, 951,0 y 1.451,5 msnm);
  - media, mediana, percentil 90 y máximo de la pendiente en círculos de 100, 250 y 500 m;
  - % del área de cada círculo con pendiente > 15°, > 25° y > 35°;
  - orientación (aspecto) media de la ladera en 250 m.
Portales = coordenadas [CP] del OE 1 (src/data/proyecto.ts).
Uso: python pendiente_portales_OE3.py  → pendiente_portales_OE3.json. Requiere numpy y tifffile.
"""
import json, math, os, datetime
import numpy as np, tifffile

DEM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "dem_corredor.tif")
PORTALES = {"oriental_Ibague": (-75.1960, 4.3640), "occidental_Calarca": (-75.6520, 4.4800)}
COTA_OE1 = {"oriental_Ibague": 951.0, "occidental_Calarca": 1451.5}
RADIOS = (100, 250, 500)
SALIDA = "pendiente_portales_OE3.json"

t = tifffile.TiffFile(DEM); pg = t.pages[0]
esc = pg.tags["ModelPixelScaleTag"].value; tp = pg.tags["ModelTiepointTag"].value
x0, y0, px = tp[3], tp[4], esc[0]           # esquina superior izquierda del píxel (0,0); PixelIsArea
z = pg.asarray().astype("float64")

def fila_col(lon, lat):
    return int(math.floor((y0 - lat) / px)), int(math.floor((lon - x0) / px))

out = {"fuente_dem": "Copernicus DEM GLO-30 (dem_corredor.tif, 1\" ≈ 30 m)", "metodo": "Horn 3x3",
       "calculado": datetime.datetime.now().isoformat(timespec="seconds"), "portales": {}}
for n, (lon, lat) in PORTALES.items():
    f, c = fila_col(lon, lat); m = 40
    w = z[f - m:f + m + 1, c - m:c + m + 1]
    dx = px * 111320.0 * math.cos(math.radians(lat)); dy = px * 110574.0
    a, b, cc, d, e, ff, g, h, i = (w[:-2, :-2], w[:-2, 1:-1], w[:-2, 2:], w[1:-1, :-2], w[1:-1, 1:-1], w[1:-1, 2:], w[2:, :-2], w[2:, 1:-1], w[2:, 2:])
    dzdx = ((cc + 2 * ff + i) - (a + 2 * d + g)) / (8 * dx)
    dzdy = ((g + 2 * h + i) - (a + 2 * b + cc)) / (8 * dy)          # positivo hacia el sur
    pend = np.degrees(np.arctan(np.hypot(dzdx, dzdy)))
    asp = (np.degrees(np.arctan2(-dzdx, dzdy)) + 360) % 360        # dirección hacia donde baja la ladera (0 = N)
    k = m - 1                                                       # centro en la malla recortada
    yy, xx = np.mgrid[-k:k + 1, -k:k + 1]; dist = np.hypot(xx * dx, yy * dy)
    r = {"lon": lon, "lat": lat, "fila_col": [f, c], "pixel_m": [round(dx, 1), round(dy, 1)],
         "cota_pixel_msnm": round(float(z[f, c]), 1), "cota_OE1_msnm": COTA_OE1[n],
         "pendiente_pixel_grados": round(float(pend[k, k]), 1), "circulos": {}}
    for R in RADIOS:
        s = pend[dist <= R]
        r["circulos"][str(R)] = {"n_pixeles": int(s.size), "media": round(float(s.mean()), 1),
            "mediana": round(float(np.median(s)), 1), "p90": round(float(np.percentile(s, 90)), 1),
            "max": round(float(s.max()), 1), "pct_mayor_15": round(100 * float((s > 15).mean()), 1),
            "pct_mayor_25": round(100 * float((s > 25).mean()), 1), "pct_mayor_35": round(100 * float((s > 35).mean()), 1),
            "desnivel_m": round(float(w[1:-1, 1:-1][dist <= R].max() - w[1:-1, 1:-1][dist <= R].min()), 1)}
    s = asp[dist <= 250]; rad = np.radians(s)
    r["aspecto_medio_250m_grados"] = round(float((np.degrees(np.arctan2(np.sin(rad).mean(), np.cos(rad).mean())) + 360) % 360))
    out["portales"][n] = r
json.dump(out, open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
for n, r in out["portales"].items():
    print(n, r["cota_pixel_msnm"], "vs", r["cota_OE1_msnm"], "| px", r["pendiente_pixel_grados"], "°", r["circulos"], "asp", r["aspecto_medio_250m_grados"])
