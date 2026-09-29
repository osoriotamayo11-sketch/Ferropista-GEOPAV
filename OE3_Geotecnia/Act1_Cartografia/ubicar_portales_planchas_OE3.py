# -*- coding: utf-8 -*-
"""OE 3 · Act 1 — Ubica los portales sobre las planchas geológicas 1:100.000 (SGC).

Georreferenciación sin SIG, reproducible:
  1. Renderiza la plancha a 144 ppp con pdftoppm y detecta las líneas grises de la
     cuadrícula de 5 km (píxeles grises R≈G≈B en 80–175 que cubren >25 % de la fila/columna).
  2. Ajusta la escala con todas las líneas (separación 138–145 pt = 5 km a 1:100.000) y
     calibra el valor de la primera línea (múltiplo de 5 km) con los rótulos impresos de
     meridianos y paralelos: se elige el que deja el menor residuo. E0/N0 son solo semilla.
  3. Proyecta el portal con pyproj al sistema de la plancha (MAGNA-SIRGAS, origen Bogotá
     EPSG:3116 para la 244; origen Oeste EPSG:3115 para la 243, según su leyenda).
  4. Control: proyecta los meridianos rotulados (75°10', 75°20', 75°30', 75°40', 75°50')
     y mide la distancia al rótulo impreso en el PDF (pdftotext -bbox).
  Resultado 25 sep 2026: residuo ≤ 3 pt (≈ 0,1 km) en la 244; en la 243 desfase constante
     de 11,6 pt en ambos meridianos (anclaje del rótulo), paralelos ≤ 0,6 pt.
  5. Recorta ±110 pt (≈3,9 km) alrededor del portal a 288 ppp y marca el punto.
Salida: ubicacion_portales_planchas_OE3.json y portal_<plancha>_recorte.png.
"""
import json, os, re, subprocess, tempfile, numpy as np
TMP = tempfile.gettempdir()  # los renders completos no se escriben en la carpeta del proyecto
from PIL import Image, ImageDraw
from pyproj import Transformer

PLANCHAS = {
    "244": {"pdf": "Plancha_244_Ibague_mapa.pdf", "epsg": 3116, "E0": 840000, "N0": 995000,
            "portal": ("oriental_Ibague", -75.1960, 4.3640), "meridianos": [-75.5, -75 - 20/60, -75 - 10/60]},
    "243": {"pdf": "Plancha_243_Armenia_mapa.pdf", "epsg": 3115, "E0": 1125000, "N0": 995000,
            "portal": ("occidental_Calarca", -75.6520, 4.4800), "meridianos": [-75 - 50/60, -75 - 40/60]},
}

def lineas(png):
    a = np.array(Image.open(png).convert("RGB")).astype(int)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    g = (abs(R - G) < 12) & (abs(G - B) < 12) & (R > 80) & (R < 175)
    h, w = g.shape
    sub = g[int(h * .15):int(h * .65), int(w * .2):int(w * .6)]
    col, row = g[int(h*.15):int(h*.65), :].mean(0), g[:, int(w*.2):int(w*.6)].mean(1)
    def pk(v):
        idx = [i for i in range(1, len(v) - 1) if v[i] > .25 and v[i] >= v[i-1] and v[i] >= v[i+1]]
        grupos = []
        for i in idx:
            if grupos and i - grupos[-1][-1] <= 3: grupos[-1].append(i)
            else: grupos.append([i])
        return [sum(gr) / len(gr) / 2 for gr in grupos]   # a puntos (72 por pulgada)
    return pk(col), pk(row)

def regular(v, paso_min=138, paso_max=145):
    """Conserva la serie de líneas con separación ~constante (5 km)."""
    mejor = []
    for i in range(len(v)):
        s = [v[i]]
        for x in v[i+1:]:
            if paso_min <= x - s[-1] <= paso_max: s.append(x)
        if len(s) > len(mejor): mejor = s
    return mejor

out = {}
for n, p in PLANCHAS.items():
    subprocess.run(["pdftoppm", "-r", "144", "-png", "-singlefile", p["pdf"], os.path.join(TMP, f"_tmp_{n}")], check=True)
    cols, rows = lineas(os.path.join(TMP, f"_tmp_{n}.png"))
    cols, rows = regular(cols), regular(rows)
    kx = (cols[-1] - cols[0]) / (5 * (len(cols) - 1))          # pt por km
    ky = (rows[-1] - rows[0]) / (5 * (len(rows) - 1))
    tr = Transformer.from_crs(4326, p["epsg"], always_xy=True)
    bb = subprocess.run(["pdftotext", "-bbox", p["pdf"], "-"], capture_output=True, text=True).stdout
    rot = [(float(a), float(b), t) for a, b, t in re.findall(r'xMin="([\d.]+)" yMin="([\d.]+)"[^>]*>([^<]*)<', bb)]
    def etq_lon(m):
        g, mi = int(abs(m)), round((abs(m) - int(abs(m))) * 60); return f"{g}°{mi:02d}&apos;0&quot;W"
    def res_E(E0):
        r = []
        for m in p["meridianos"]:
            xm = cols[0] + (tr.transform(m, 4.5)[0] - E0) / 1000 * kx
            xs = [a for a, b, t in rot if t == etq_lon(m)]
            if xs: r.append(min(abs(a - xm) for a in xs))
        return max(r)
    def res_N(N0):
        r = []
        for la, t in ((4 + 20/60, "4°20&apos;0&quot;N"), (4.5, "4°30&apos;0&quot;N")):
            ym = rows[0] + (N0 - tr.transform(p["meridianos"][0], la)[1]) / 1000 * ky
            ys = [b for a, b, tt in rot if tt == t]
            if ys: r.append(min(abs(b - ym) for b in ys))
        return max(r)
    tr = Transformer.from_crs(4326, p["epsg"], always_xy=True)
    p["E0"] = min((p["E0"] + k * 5000 for k in range(-3, 4)), key=res_E)
    p["N0"] = min((p["N0"] + k * 5000 for k in range(-3, 4)), key=res_N)
    X = lambda E: cols[0] + (E - p["E0"]) / 1000 * kx
    Y = lambda N: rows[0] + (p["N0"] - N) / 1000 * ky
    nombre, lon, lat = p["portal"]
    E, N = tr.transform(lon, lat)
    x, y = X(E), Y(N)
    # control con los rótulos de meridianos
    ctrl = []
    for m in p["meridianos"]:
        g, mi = int(abs(m)), round((abs(m) - int(abs(m))) * 60)
        etiqueta = f"{g}°{mi:02d}&apos;0&quot;W"
        xs = [a for a, b, t in rot if t == etiqueta]
        xm = X(tr.transform(m, 4.5)[0])
        if xs: ctrl.append({"meridiano": etiqueta.replace("&apos;", "'").replace("&quot;", '"'),
                            "x_calculado_pt": round(xm, 1), "x_rotulo_pt": round(min(xs, key=lambda a: abs(a - xm)), 1)})
    # recorte
    r, h = 288, 110; s = r / 72
    X0, Y0, W = int((x - h) * s), int((y - h) * s), int(2 * h * s)
    subprocess.run(["pdftoppm", "-r", str(r), "-png", "-singlefile", "-x", str(X0), "-y", str(Y0), "-W", str(W), "-H", str(W),
                    p["pdf"], f"portal_{n}_recorte"], check=True)
    im = Image.open(f"portal_{n}_recorte.png").convert("RGB"); d = ImageDraw.Draw(im)
    cx, cy = x * s - X0, y * s - Y0
    for rr in (10, 11, 12): d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(255, 0, 0))
    for a, b in ((-40, -14), (14, 40)):
        d.line([cx + a, cy, cx + b, cy], fill=(255, 0, 0), width=3); d.line([cx, cy + a, cx, cy + b], fill=(255, 0, 0), width=3)
    im.save(f"portal_{n}_recorte.png")
    out[n] = {"portal": nombre, "lon": lon, "lat": lat, "epsg": p["epsg"], "E": round(E), "N": round(N),
              "lineas_E_pt": [round(c, 2) for c in cols], "lineas_N_pt": [round(c, 2) for c in rows],
              "escala_pt_km": [round(kx, 3), round(ky, 3)], "E_primera_linea": p["E0"], "N_primera_linea": p["N0"],
              "residuo_max_meridianos_pt": round(res_E(p["E0"]), 1), "residuo_max_paralelos_pt": round(res_N(p["N0"]), 1), "portal_pt": [round(x, 1), round(y, 1)],
              "control_meridianos": ctrl, "px_por_km_recorte": round(kx * s, 1),
              "nota_control": "x_rotulo_pt es el inicio (xMin) del texto del rótulo; un desfase igual en todos los meridianos indica anclaje del texto, no error de escala."}
json.dump(out, open("ubicacion_portales_planchas_OE3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(json.dumps({k: {c: v[c] for c in ("portal", "E", "N", "E_primera_linea", "N_primera_linea", "escala_pt_km", "portal_pt", "residuo_max_meridianos_pt", "residuo_max_paralelos_pt", "control_meridianos")} for k, v in out.items()}, ensure_ascii=False, indent=1))
