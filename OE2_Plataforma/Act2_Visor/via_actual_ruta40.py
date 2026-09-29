# -*- coding: utf-8 -*-
"""Vía actual del corredor: Ruta Nacional 40 entre Ibagué y Calarcá (paso de La Línea).

Capa de contexto para todos los mapas del proyecto (láminas del OE 1, OE 3 y OE 5 y relieve 3D del
sitio). Fuente [F]: OpenStreetMap (© colaboradores de OpenStreetMap, licencia ODbL), consultada por la
API Overpass.

Método [CP]:
  1. Se bajan las vías highway=trunk|trunk_link|primary|primary_link de la ventana del corredor.
  2. Se identifica el Túnel de La Línea como la vía tunnel=yes más larga de la ventana.
  3. Se arma el grafo sin atender el sentido de circulación (interesa el trazado, no el sentido) y se
     penaliza ×3 el costo de las vías cuyo ref no contiene «40», para que el camino siga la ruta
     nacional y no calles o vías alternas.
  4. Camino más corto por cuatro puntos: nodo de la Ruta 40 más cercano al portal oriental del OE 1 →
     boca oriental del túnel → boca occidental → nodo de la Ruta 40 más cercano a Armenia (inicio de la
     Ruta 4003 de la ANSV, para que el mapa de siniestros del OE 5 cubra todo el tramo).
Control: el túnel debe medir entre 7,5 y 10,5 km (8,6 km según INVÍAS [F]); si no, el script se detiene.
Donde la vía es de doble calzada queda una sola: a la escala de los mapas no se distinguen.

Salidas (WGS 84, lon/lat), tramos con propiedad «tunel»:
  OE2_Plataforma/Act2_Visor/via_actual_ruta40.geojson
  public/data/via_actual_ruta40.geojson      (la consume el relieve 3D del sitio)
Uso: python via_actual_ruta40.py. Solo biblioteca estándar.
"""
import heapq, json, math, os, urllib.parse, urllib.request, datetime

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PORTAL_E = (-75.1960, 4.3640); PORTAL_W = (-75.6520, 4.4800)          # [CP] OE 1, src/data/proyecto.ts
ARMENIA = (-75.6811, 4.5339)   # extremo occidental: la vía se prolonga hasta Armenia, inicio de la Ruta 4003 de la ANSV (sesión 16)
CAJA = (4.30, -75.75, 4.56, -75.10)                                  # sur, oeste, norte, este
SERVIDORES = ["https://overpass-api.de/api/interpreter", "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
              "https://overpass.kumi.systems/api/interpreter"]
Q = f'[out:json][timeout:170];way["highway"~"^(trunk|trunk_link|primary|primary_link)$"]({",".join(map(str, CAJA))});out tags geom;'

def baja():
    for s in SERVIDORES:
        try:
            req = urllib.request.Request(s, data=urllib.parse.urlencode({"data": Q}).encode(), headers={"User-Agent": "GEOPAV-Ferropista/1.0"})
            with urllib.request.urlopen(req, timeout=175) as r:
                return json.load(r), s
        except Exception as e:
            print("falló", s, e)
    raise SystemExit("PARADA: ningún servidor Overpass respondió.")

def dist(a, b):  # haversine, m
    la1, la2 = math.radians(a[1]), math.radians(b[1])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(math.radians(b[0] - a[0]) / 2) ** 2
    return 2 * 6371008.8 * math.asin(math.sqrt(h))

d, servidor = baja()
G = {}; TUN = {}; es40 = set(); tunel = None
for w in d["elements"]:
    pts = [(round(p["lon"], 7), round(p["lat"], 7)) for p in w["geometry"]]
    t = w["tags"].get("tunnel") == "yes"; r40 = "40" in w["tags"].get("ref", "")
    if t:
        L = sum(dist(a, b) for a, b in zip(pts, pts[1:]))
        if tunel is None or L > tunel[0]: tunel = (L, pts[0], pts[-1], w["tags"].get("name"))
    for a, b in zip(pts, pts[1:]):
        L = dist(a, b); c = L if r40 else 3 * L
        G.setdefault(a, []).append((b, c)); G.setdefault(b, []).append((a, c)); TUN[(a, b)] = TUN[(b, a)] = t
        if r40: es40.update((a, b))
if not 7500 <= tunel[0] <= 10500:
    raise SystemExit(f"PARADA: la vía en túnel más larga mide {tunel[0]:.0f} m; se esperaban ≈ 8.600 m (Túnel de La Línea).")
cerca40 = lambda p: min(es40, key=lambda n: dist(n, p))
nE, nW = cerca40(PORTAL_E), cerca40(ARMENIA)
bocaE, bocaW = sorted([tunel[1], tunel[2]], key=lambda p: -p[0])       # la de mayor longitud (menos negativa) es la oriental

def camino(s, t):
    D = {s: 0}; P = {}; h = [(0, s)]
    while h:
        c, u = heapq.heappop(h)
        if u == t: break
        if c > D[u]: continue
        for v, k in G[u]:
            if c + k < D.get(v, 1e18): D[v] = c + k; P[v] = u; heapq.heappush(h, (c + k, v))
    if t not in P: raise SystemExit(f"PARADA: no hay camino entre {s} y {t}.")
    r = [t]
    while r[-1] != s: r.append(P[r[-1]])
    return r[::-1]

cam = [nE]
for a, b in ((nE, bocaE), (bocaE, bocaW), (bocaW, nW)): cam += camino(a, b)[1:]
L_tot = sum(dist(a, b) for a, b in zip(cam, cam[1:]))
L_tun = sum(dist(a, b) for a, b in zip(cam, cam[1:]) if TUN[(a, b)])
L_no40 = sum(dist(a, b) for a, b in zip(cam, cam[1:]) if not (a in es40 and b in es40))
tramos = []; actual = [cam[0]]; estado = TUN[(cam[0], cam[1])]
for a, b in zip(cam, cam[1:]):
    if TUN[(a, b)] != estado: tramos.append((estado, actual)); actual = [a]; estado = TUN[(a, b)]
    actual.append(b)
tramos.append((estado, actual))
out = {"type": "FeatureCollection", "name": "via_actual_ruta40",
       "fuente": "© colaboradores de OpenStreetMap (ODbL), API Overpass: " + servidor,
       "osm_base": d["osm3s"].get("timestamp_osm_base"), "consultado": datetime.datetime.now().isoformat(timespec="seconds"),
       "metodo": "Camino más corto por la red trunk/primary (vías sin ref 40 penalizadas ×3) desde el nodo de la Ruta 40 más cercano al portal oriental del OE 1 hasta Armenia, pasando por el Túnel de La Línea [CP]",
       "tunel_osm": tunel[3], "longitud_m": round(L_tot, 1), "longitud_tunel_m": round(L_tun, 1), "longitud_fuera_ref40_m": round(L_no40, 1),
       "distancia_extremo_a_referencia_m": {"oriental_portal_E": round(dist(nE, PORTAL_E)), "occidental_Armenia": round(dist(nW, ARMENIA))},
       "features": [{"type": "Feature", "properties": {"tunel": t, "longitud_m": round(sum(dist(a, b) for a, b in zip(p, p[1:])), 1)},
                     "geometry": {"type": "LineString", "coordinates": [list(x) for x in p]}} for t, p in tramos]}
for ruta in (os.path.join(RAIZ, "OE2_Plataforma", "Act2_Visor", "via_actual_ruta40.geojson"),
             os.path.join(RAIZ, "public", "data", "via_actual_ruta40.geojson")):
    json.dump(out, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"vía {L_tot/1000:.2f} km · túnel «{tunel[3]}» {L_tun/1000:.2f} km · fuera de ref 40 {L_no40/1000:.2f} km · "
      f"{len(cam)} vértices, {len(tramos)} tramos · extremos a {out['distancia_extremo_a_referencia_m']} m · OSM {out['osm_base']}")
