# -*- coding: utf-8 -*-
"""
OE 1 — Análisis topográfico del trazado del túnel de base Ferropista
Semillero de Investigación GEOPAV · Universidad de Ibagué · Paz y Región 2026B
Responsable: Tamayo Osorio Miguel Ángel

Versión 2 (7 sep 2026). Reemplaza la versión del 1 sep 2026.

QUÉ CAMBIÓ Y POR QUÉ
  1. La versión 1 leía 'dem_corredor.tif' pero NUNCA escribía el recorte
     'DEM_corredor_recorte.tif' que se entregó como evidencia. Ese recorte se hizo
     por fuera y quedó desplazado una columna (~30 m), por lo que las cotas leídas
     en él no reproducían las publicadas. Ahora el recorte lo genera este script,
     con una ventana alineada a la malla del mosaico.
  2. La versión 1 no escribía el trazado ni la cartera: solo imprimía al log. Los
     archivos entregados eran anteriores a la ejecución del script. Ahora todos los
     productos del OE 1 salen de esta única corrida.
  3. La búsqueda de portales usaba 'cE[::7]' y 'cW[::7]', descartando seis de cada
     siete candidatos sin justificación. Se evalúan todos los pares.
  4. La tolerancia de cota TOL era 15 m y no estaba declarada. Se comprobó que ese
     parámetro, y no el método, decide dónde caen los portales: variarlo entre 2 y
     15 m mueve la longitud 690 m y el porcentaje de cobertura > 700 m en 12 puntos.
     Se adopta TOL = 2 m [H] y se publica la tabla de sensibilidad completa.
  5. La cartera tenía paso irregular (34,8 a 522,5 m), terminaba 174 m antes del
     portal y arrancaba con cobertura −0,4 m por redondear la rasante. Ahora el paso
     es regular de 500 m, cierra en el portal y la cobertura en el PK 0 es 0,0 m
     por construcción.

Ejecutar:  python procesamiento_OE1.py
Requiere:  rasterio, pyproj, numpy, openpyxl, shapely, pyshp

FUENTES
  Terreno : Copernicus DEM GLO-30 (ESA/Airbus), ~30 m, EPSG:4326.
            https://copernicus-dem-30m.s3.amazonaws.com/
  Límites : IGAC — capa «municipios» del servicio de ordenamiento territorial,
            con código DANE. Servicio ArcGIS REST público, sin registro:
            https://mapas.igac.gov.co/server/rest/services/ordenamientoterritorial/
            clasificacionsegunley617del2000/MapServer/0
  Portales: cotas 950 y 1450 msnm según Fernández Ordóñez, H. O. (2025),
            "Túnel para cruce férreo de la Cordillera Central de los Andes",
            XX Seminario Andino de Túneles, Medellín, diapositiva 20.

MARCAS DE ORIGEN
  [F]  dato de la ponencia   [CP] cálculo propio   [H] hipótesis
"""
import os, json, csv, zipfile
try:
    import shapefile          # pyshp: escribe los .shp que consume el proyecto QGIS
except ImportError:
    shapefile = None
import numpy as np, rasterio
from rasterio.merge import merge
from rasterio.windows import from_bounds
from pyproj import Geod
from datetime import datetime, timezone

# ----------------------------------------------------------------------------- rutas
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../OE1_Topografia
D_ACT1 = os.path.join(RAIZ, 'Act1_DEM')
D_ACT2 = os.path.join(RAIZ, 'Act2_Portales')
D_ACT4 = os.path.join(RAIZ, 'Act4_Trazado')
D_ACT5 = os.path.join(RAIZ, 'Act5_Perfil')
for d in (D_ACT1, D_ACT2, D_ACT4, D_ACT5): os.makedirs(d, exist_ok=True)

# salidas nombradas que consumen la comprobación del área de estudio y el layout
MOSAICO_DEM       = 'dem_corredor.tif'   # mosaico de los dos tiles Copernicus (raíz del repo)
OUT_DEM_RECORTE   = os.path.join(D_ACT1, 'DEM_corredor_recorte.tif')
OUT_DEM_AREA      = os.path.join(D_ACT1, 'DEM_area_estudio.tif')
OUT_LIM_AREA      = os.path.join(D_ACT1, 'limites_area_estudio.geojson')
OUT_DEPARTAMENTOS = os.path.join(D_ACT1, 'departamentos_colombia_igac.geojson')

LOG = []
def log(m):
    linea = f"[{datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S} UTC] {m}"
    print(linea); LOG.append(linea)

# ------------------------------------------------------------------------ parámetros
TILES = {
 'cop30_N04W076.tif': 'https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N04_00_W076_00_DEM/Copernicus_DSM_COG_10_N04_00_W076_00_DEM.tif',
 'cop30_N04W075.tif': 'https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N04_00_W075_00_DEM/Copernicus_DSM_COG_10_N04_00_W075_00_DEM.tif',
}
VALIDACION = [("Ibagué",4.4389,-75.2322,1285), ("Armenia",4.5339,-75.6811,1483),
              ("Cajamarca",4.4267,-75.4275,1813), ("Calarcá",4.5222,-75.6497,1536)]

COTA_E, COTA_W   = 950.0, 1450.0   # [F, p.20] cotas objetivo de portal
TOL              = 2.0             # [H] tolerancia de cota adoptada. Ver tabla de sensibilidad
PASO_BUSQUEDA    = 0.002           # [H] ~222 m; malla de candidatos

# ---------------------------------------------------------------------------
# VENTANAS DE BÚSQUEDA — HIPÓTESIS DE DISEÑO, NO UN DETALLE DE IMPLEMENTACIÓN
#
# El criterio de selección minimiza la distancia entre portales, así que empuja
# el portal oriental lo más al oeste que pueda. La ventana oriental lo frena:
# el portal adoptado cae a unos 440 m de su borde occidental, es decir, la
# ventana es una restricción ACTIVA y no un simple contorno de búsqueda.
#
# Se conservan deliberadamente, porque codifican una decisión de ingeniería:
# el portal oriental debe quedar en la aproximación oriental de Ibagué, que es
# el extremo que nombra la ponencia. Al ampliarlas el túnel se acorta 2,5 km
# pero el portal se traslada a Rovira y el trazado pasa a cruzar cinco
# municipios, incluido Córdoba (Quindío): deja de ser el corredor
# Ibagué – Armenia analizado. La tabla de sensibilidad que produce el paso 6
# publica ese contraste en lugar de esconderlo.
# ---------------------------------------------------------------------------
VENT_E           = ((4.30,4.50), (-75.20,-75.00))  # [H] ventana portal oriental
VENT_W           = ((4.45,4.60), (-75.75,-75.60))  # [H] ventana portal occidental
VENTANAS_SENS    = [   # variantes para la tabla de sensibilidad del paso 6
    ("adoptada",            ((4.30,4.50), (-75.20,-75.00)), ((4.45,4.60), (-75.75,-75.60))),
    ("oriental ampliada",   ((4.30,4.50), (-75.32,-75.00)), ((4.45,4.60), (-75.75,-75.60))),
    ("occidental ampliada", ((4.30,4.50), (-75.20,-75.00)), ((4.45,4.60), (-75.75,-75.48))),
    ("ambas ampliadas",     ((4.30,4.55), (-75.32,-75.00)), ((4.40,4.62), (-75.78,-75.48))),
]
CRITERIO_PEND    = 1.5             # [H] % máximo adoptado para tracción férrea de carga
PRJ_WGS84 = ('GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",'
             '6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],'
             'UNIT["Degree",0.0174532925199433]]')

def zip_determinista(ruta_zip, entradas):
    """Escribe un .zip reproducible. 'entradas': lista de (nombre_en_el_zip, bytes).
    date_time fijo (1980-01-01) y external_attr constante -> dos corridas dan bytes
    idénticos. No se usa zipf.write(ruta): guardaría la mtime real del disco."""
    with zipfile.ZipFile(ruta_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for nombre, datos in entradas:
            zi = zipfile.ZipInfo(filename=nombre, date_time=(1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o600 << 16
            zf.writestr(zi, datos)

def escribir_shp(ruta_sin_ext, tipo, registros, campos):
    """Escribe .shp/.shx/.dbf/.prj/.cpg. Sin esto el proyecto QGIS dibujaría la
    geometría vieja, porque el .qgz referencia shapefiles, no GeoJSON."""
    if shapefile is None:
        log(f"  AVISO: pyshp no instalado, no se escribió {os.path.basename(ruta_sin_ext)}.shp")
        return False
    w = shapefile.Writer(ruta_sin_ext, shapeType=tipo)
    for nombre, tipo_c, tam, dec in campos: w.field(nombre, tipo_c, tam, dec)
    for geom, attrs in registros:
        if tipo == shapefile.POINT: w.point(*geom)
        else: w.line([geom])
        w.record(*attrs)
    w.close()
    open(ruta_sin_ext + '.prj', 'w', encoding='utf-8').write(PRJ_WGS84)
    open(ruta_sin_ext + '.cpg', 'w', encoding='utf-8').write('UTF-8')
    # El .zip que se entrega lo arma este script, no la mano, con las cinco
    # extensiones en orden y empaquetado reproducible.
    zip_ruta = ruta_sin_ext + '_SHP.zip'
    base = os.path.basename(ruta_sin_ext)
    entradas = []
    for e in ('shp', 'shx', 'dbf', 'prj', 'cpg'):
        with open(ruta_sin_ext + '.' + e, 'rb') as fh:
            entradas.append((base + '.' + e, fh.read()))
    zip_determinista(zip_ruta, entradas)
    log(f"  zip -> {os.path.relpath(zip_ruta, RAIZ)}")
    return True

PASO_CARTERA     = 500.0           # [H] m entre abscisas de la cartera
N_PERFIL         = 1500            # [H] puntos del perfil continuo
RECORTE          = dict(oeste=-75.82, este=-75.03, sur=4.20, norte=4.65)  # [H] ventana del recorte
TOLS_SENS        = [2.0, 5.0, 10.0, 15.0]   # tolerancias de la tabla de sensibilidad
VENTANA_MAPA     = (-75.76, 4.30, -75.10, 4.60)   # [H] encuadre de la figura del mapa
IGAC_MUNICIPIOS  = ('https://mapas.igac.gov.co/server/rest/services/ordenamientoterritorial/'
                    'clasificacionsegunley617del2000/MapServer/0/query')
IGAC_DEPARTAMENTOS = ('https://mapas.igac.gov.co/server/rest/services/'
                      'ordenamientoterritorial/clasificacionsegunley617del2000/'
                      'MapServer/1/query')
DEPTOS           = ("Tolima", "Quindío")    # departamentos que cubren el corredor

g = Geod(ellps='WGS84')

# ------------------------------------------------------------------------- utilidades
def cota_en(band, src, la, lo):
    """Cota del píxel que contiene el punto. Muestreo por vecino más cercano [H]."""
    r, c = src.index(lo, la)
    return float(band[r, c])

def buscar_candidatos(band, src, objetivo, ventana, tol):
    (la0,la1),(lo0,lo1) = ventana
    return [(la, lo, cota_en(band,src,la,lo))
            for la in np.arange(la0, la1, PASO_BUSQUEDA)
            for lo in np.arange(lo0, lo1, PASO_BUSQUEDA)
            if abs(cota_en(band,src,la,lo) - objetivo) <= tol]

def par_mas_corto(cE, cW):
    """Criterio de selección: par que MINIMIZA la distancia -> túnel más corto.
    Es un criterio geométrico, NO geotécnico. Debe cruzarse con el OE 3."""
    return min(((g.inv(o[1],o[0],w[1],w[0])[2], o, w) for o in cE for w in cW),
               key=lambda t: t[0])

def punto_en_pk(PE, PW, pk):
    """Coordenadas exactas a la abscisa pk, sobre la misma geodésica portal-portal."""
    az = g.inv(PE[1], PE[0], PW[1], PW[0])[0]
    lo, la, _ = g.fwd(PE[1], PE[0], az, pk)
    return la, lo

def perfil_continuo(band, src, PE, PW, L, n=N_PERFIL):
    pts = g.npts(PE[1],PE[0],PW[1],PW[0], n-2)
    coords = [(PE[0],PE[1])] + [(la,lo) for lo,la in pts] + [(PW[0],PW[1])]
    filas, acum, prev = [], 0.0, None
    for la,lo in coords:
        if prev: acum += g.inv(prev[1],prev[0],lo,la)[2]
        prev = (la,lo)
        ter = cota_en(band,src,la,lo)
        ras = PE[2] + (PW[2]-PE[2]) * (acum/L)
        filas.append(dict(pk=acum, lat=la, lon=lo, terreno=ter, rasante=ras,
                          cobertura=ter-ras))
    return filas

def abscisa(pk):
    return f"K{int(pk//1000)}+{pk%1000:06.2f}"

# ------------------------------------------------------------------------------ pasos
def paso1_dem():
    import urllib.request
    log("PASO 1 — Mosaico del DEM y recorte del corredor")
    for f,u in TILES.items():
        if not os.path.exists(f):
            log(f"  descargando {f} ..."); urllib.request.urlretrieve(u,f); log(f"  descargado {f}")
        else: log(f"  ya existe {f}")
    srcs = [rasterio.open(f) for f in TILES]
    arr, tr = merge(srcs)
    meta = srcs[0].meta.copy()
    meta.update(driver='GTiff', height=arr.shape[1], width=arr.shape[2],
                transform=tr, compress='deflate')
    with rasterio.open('dem_corredor.tif','w',**meta) as d: d.write(arr)
    for s in srcs: s.close()
    log(f"  mosaico dem_corredor.tif  {arr.shape[2]}x{arr.shape[1]} px")

    # Recorte ALINEADO A LA MALLA: la ventana se redondea a píxeles enteros, por eso
    # las cotas leídas en el recorte son idénticas a las del mosaico.
    with rasterio.open('dem_corredor.tif') as m:
        w = from_bounds(RECORTE['oeste'], RECORTE['sur'], RECORTE['este'],
                        RECORTE['norte'], m.transform).round_offsets().round_lengths()
        rec = m.read(1, window=w)
        pm = m.meta.copy()
        pm.update(height=rec.shape[0], width=rec.shape[1],
                  transform=m.window_transform(w), compress='deflate')
        ruta = os.path.join(D_ACT1,'DEM_corredor_recorte.tif')
        with rasterio.open(ruta,'w',**pm) as d: d.write(rec,1)
    log(f"  recorte DEM_corredor_recorte.tif  {rec.shape[1]}x{rec.shape[0]} px  (alineado a la malla)")
    return ruta

def paso2_validar(band, src):
    log("PASO 2 — Validación del DEM contra cotas conocidas")
    difs = []
    for n,la,lo,ref in VALIDACION:
        v = cota_en(band,src,la,lo); difs.append(v-ref)
        log(f"  {n:<12} DEM {v:7.0f}  ref {ref:5d}  dif {v-ref:+6.0f} m")
    ema = np.abs(difs).mean()
    log(f"  error medio absoluto: {ema:.0f} m  (aceptable para DEM de ~30 m)")
    return ema

def paso3_portales(band, src):
    log("PASO 3 — Localización de portales por cota objetivo")
    log(f"  criterio: par que minimiza la distancia, entre candidatos con |cota-objetivo| <= TOL")
    log(f"  TOL adoptada = {TOL:.0f} m [H]")
    sens = []
    for t in TOLS_SENS:
        cE = buscar_candidatos(band,src,COTA_E,VENT_E,t)
        cW = buscar_candidatos(band,src,COTA_W,VENT_W,t)
        if not cE or not cW: continue
        d,(laE,loE,vE),(laW,loW,vW) = par_mas_corto(cE,cW)
        pf = perfil_continuo(band,src,(laE,loE,vE),(laW,loW,vW),d)
        cob = np.array([f['cobertura'] for f in pf])
        # se redondea AQUÍ: un CSV con quince decimales y con -9,66e-11 en la
        # cobertura mínima se lee como ruido, no como resultado.
        sens.append(dict(tol_m=t, n_cand_E=len(cE), n_cand_W=len(cW),
                         lat_E=round(laE,4), lon_E=round(loE,4), cota_E=round(vE,1),
                         lat_W=round(laW,4), lon_W=round(loW,4), cota_W=round(vW,1),
                         longitud_m=round(d,1), desnivel_m=round(vW-vE,1),
                         pendiente_pct=round(100*(vW-vE)/d,4),
                         cob_max_m=round(float(cob.max()),1),
                         cob_media_m=round(float(cob.mean()),1),
                         cob_min_m=round(float(cob.min()),1) + 0.0,
                         pct_cob_mayor_700=round(float(100*(cob>700).mean()),1)))
        log(f"  TOL {t:5.1f} m -> cand {len(cE):4d}/{len(cW):4d}  L {d:9,.1f} m  "
            f"pend {100*(vW-vE)/d:6.4f} %  cob>700m {100*(cob>700).mean():5.1f} %")
    with open(os.path.join(D_ACT2,'portales_sensibilidad.csv'),'w',newline='',encoding='utf-8-sig') as fh:
        wcsv = csv.DictWriter(fh, fieldnames=list(sens[0].keys())); wcsv.writeheader()
        for r in sens: wcsv.writerow(r)
    log(f"  tabla de sensibilidad -> Act2_Portales/portales_sensibilidad.csv")

    ad = next(s for s in sens if s['tol_m']==TOL)
    PE = (ad['lat_E'], ad['lon_E'], ad['cota_E'])
    PW = (ad['lat_W'], ad['lon_W'], ad['cota_W'])
    L  = ad['longitud_m']
    log(f"  ADOPTADO  portal oriental   {PE[0]:.4f},{PE[1]:.4f}  {PE[2]:.1f} msnm "
        f"(objetivo {COTA_E:.0f}, dif {PE[2]-COTA_E:+.1f} m)")
    log(f"  ADOPTADO  portal occidental {PW[0]:.4f},{PW[1]:.4f}  {PW[2]:.1f} msnm "
        f"(objetivo {COTA_W:.0f}, dif {PW[2]-COTA_W:+.1f} m)")
    log(f"  ADOPTADO  distancia entre portales: {L:,.1f} m = {L/1000:.3f} km")

    return PE, PW, L, sens

def paso4_trazado(band, src, PE, PW, L):
    log("PASO 4 — Trazado en planta")
    pf = perfil_continuo(band,src,PE,PW,L,N_PERFIL)
    # vértices del trazado: abscisas exactas cada PASO_CARTERA m, más el portal final
    pks = list(np.arange(0.0, L, PASO_CARTERA)) + [L]
    verts = []
    for pk in pks:
        la, lo = punto_en_pk(PE, PW, pk); verts.append((lo, la))
    verts[0] = (PE[1], PE[0]); verts[-1] = (PW[1], PW[0])
    largo = sum(g.inv(verts[i][0],verts[i][1],verts[i+1][0],verts[i+1][1])[2]
                for i in range(len(verts)-1))
    dist_al_portal = g.inv(verts[-1][0],verts[-1][1],PW[1],PW[0])[2]
    geo = {"type":"FeatureCollection","name":"trazado_tunel",
      "crs":{"type":"name","properties":{"name":"urn:ogc:def:crs:OGC:1.3:CRS84"}},
      "features":[{"type":"Feature","properties":{
        "nombre":"Trazado del túnel de base Ferropista (eje recto entre portales)",
        "longitud_geodesica_m":round(L,1),"longitud_poligonal_m":round(largo,1),
        "n_vertices":len(verts),"cota_portal_E_msnm":round(PE[2],1),
        "cota_portal_W_msnm":round(PW[2],1),"pendiente_pct":round(100*(PW[2]-PE[2])/L,4),
        "marca":"CP","fuente_cotas":"[F, p.20] 950 / 1450 msnm; TOL 2 m [H]"},
        "geometry":{"type":"LineString","coordinates":[[round(x,6),round(y,6)] for x,y in verts]}}]}
    with open(os.path.join(D_ACT4,'trazado_tunel.geojson'),'w',encoding='utf-8') as fh:
        json.dump(geo,fh,ensure_ascii=False,indent=1)
    log(f"  vértices: {len(verts)}   longitud poligonal {largo:,.1f} m   "
        f"geodésica {L:,.1f} m   dif {largo-L:+.1f} m")
    log(f"  cierre en el portal occidental: {dist_al_portal:.2f} m")
    log("  trazado -> Act4_Trazado/trazado_tunel.geojson")
    if escribir_shp(os.path.join(D_ACT4,'trazado_tunel'), 3,
        [([list(v) for v in verts],
          ['Trazado tunel de base Ferropista', round(L,1), len(verts),
           round(PE[2],1), round(PW[2],1), round(100*(PW[2]-PE[2])/L,4), 'CP'])],
        [('nombre','C',60,0),('long_m','N',12,1),('n_vertices','N',6,0),
         ('cota_E','N',10,1),('cota_W','N',10,1),('pend_pct','N',8,4),('marca','C',4,0)]):
        log("  trazado -> Act4_Trazado/trazado_tunel.shp (reemplaza el v1)")
    return pf, verts, largo, dist_al_portal

def paso5_cartera(band, src, pf, PE, PW, L):
    log("PASO 5 — Cartera de rasantes y perfil longitudinal")
    filas = []
    for pk in list(np.arange(0.0, L, PASO_CARTERA)) + [L]:
        la, lo = punto_en_pk(PE, PW, pk)
        if pk == 0.0: la, lo = PE[0], PE[1]
        if pk == L:   la, lo = PW[0], PW[1]
        ter = cota_en(band, src, la, lo)
        ras = PE[2] + (PW[2]-PE[2]) * (pk/L)
        filas.append(dict(pk=pk, lat=la, lon=lo, terreno=ter, rasante=ras,
                          cobertura=ter-ras))
    pasos = np.diff([f['pk'] for f in filas])
    cob = np.array([f['cobertura'] for f in filas])
    cabec = ['PK_m','Abscisa','Latitud','Longitud','Cota_terreno_msnm',
             'Cota_rasante_msnm','Cobertura_m']
    def fila(f): return [round(f['pk'],1), abscisa(f['pk']), round(f['lat'],6),
                         round(f['lon'],6), round(f['terreno'],1),
                         round(f['rasante'],1), round(f['cobertura'],1)]
    with open(os.path.join(D_ACT5,'cartera_rasantes.csv'),'w',newline='',encoding='utf-8-sig') as fh:
        w=csv.writer(fh); w.writerow(cabec); [w.writerow(fila(f)) for f in filas]
    try:
        from openpyxl import Workbook
        from datetime import datetime as _dt
        wb=Workbook(); ws=wb.active; ws.title='Cartera'; ws.append(cabec)
        for f in filas: ws.append(fila(f))
        for i,anch in enumerate([10,14,12,12,18,18,13],1):
            ws.column_dimensions[chr(64+i)].width=anch
        ws.freeze_panes='A2'
        # fuente de no determinismo (2): docProps/core.xml lleva created/modified
        # con la hora de la corrida. Se fijan a una fecha constante, PERO
        # wb.save() (save_workbook) vuelve a pisar properties.modified con la hora
        # actual justo antes de escribir. Se evita llamando directamente al
        # ExcelWriter, que es la parte que sí queremos y no lleva ese override.
        from openpyxl.writer.excel import ExcelWriter
        from zipfile import ZipFile, ZIP_DEFLATED
        wb.properties.created  = _dt(1980, 1, 1)
        wb.properties.modified = _dt(1980, 1, 1)
        ruta_xlsx = os.path.join(D_ACT5,'cartera_rasantes.xlsx')
        with ZipFile(ruta_xlsx, 'w', ZIP_DEFLATED, allowZip64=True) as _arch:
            ExcelWriter(wb, _arch).save()
        # fuente de no determinismo (1): ExcelWriter sella cada entrada del zip con
        # la hora de la corrida. Se reescribe con date_time fijo, en el mismo orden.
        with zipfile.ZipFile(ruta_xlsx) as _zx:
            _entradas = [(n, _zx.read(n)) for n in _zx.namelist()]
        zip_determinista(ruta_xlsx, _entradas)
        log("  cartera -> Act5_Perfil/cartera_rasantes.csv y .xlsx")
    except ImportError:
        log("  cartera -> Act5_Perfil/cartera_rasantes.csv  (openpyxl ausente: sin .xlsx)")
    with open(os.path.join(D_ACT5,'perfil_continuo.csv'),'w',newline='',encoding='utf-8-sig') as fh:
        w=csv.writer(fh); w.writerow(cabec)
        for f in pf: w.writerow(fila(f))
    log(f"  abscisas: {len(filas)}   paso mín {pasos.min():.1f} m  máx {pasos.max():.1f} m")
    log(f"  última abscisa: {abscisa(filas[-1]['pk'])}  (portal en {abscisa(L)})")
    log(f"  cobertura en el PK 0: {cob[0]:+.1f} m")
    log(f"  perfil continuo ({len(pf)} puntos) -> Act5_Perfil/perfil_continuo.csv")
    return filas, pasos


def paso6_municipios(band, src, PE, PW, L, verts):
    """Determina el área de estudio: los municipios que CRUZA el trazado.
    No se asume cuáles son; se calcula por intersección contra los polígonos del
    IGAC. Fue así como se detectó que el portal occidental está en Calarcá y no
    en Armenia, como decían los entregables de la versión 1."""
    import urllib.request, urllib.parse
    from shapely.geometry import shape, LineString, box, mapping
    from shapely.ops import unary_union
    log("PASO 6 — Área de estudio: municipios que cruza el trazado")

    cache = 'limites_igac_%s.geojson' % '_'.join(d[:3].lower() for d in DEPTOS)
    if not os.path.exists(cache):
        q = urllib.parse.urlencode({
            'where': "Depto IN (%s)" % ','.join("'%s'" % d for d in DEPTOS),
            'outFields': 'MpCodigo,MpNombre,Depto,MpArea',
            'returnGeometry': 'true', 'outSR': '4326', 'f': 'geojson'})
        log(f"  descargando límites del IGAC ({', '.join(DEPTOS)}) ...")
        urllib.request.urlretrieve(f"{IGAC_MUNICIPIOS}?{q}", cache)
    mun = json.load(open(cache, encoding='utf-8'))
    log(f"  {len(mun['features'])} municipios cargados desde {cache}")

    linea = LineString([tuple(v) for v in verts])
    ventana = box(*VENTANA_MAPA)
    estudio, contexto = [], []
    for f in mun['features']:
        geo = shape(f['geometry'])          # 'geo', no 'g': 'g' es el objeto Geod global
        if not geo.is_valid: geo = geo.buffer(0)
        pr = f['properties']
        if geo.intersects(linea):
            inter = geo.intersection(linea)
            partes = [inter] if inter.geom_type == 'LineString' else list(inter.geoms)
            largo = sum(g.geometry_length(p) for p in partes)   # longitud geodésica real
            estudio.append((pr, largo, geo))
        elif geo.intersects(ventana):
            contexto.append((pr, geo.intersection(ventana.buffer(0.02))))

    tot = sum(x[1] for x in estudio)
    feats_e = []
    for pr, largo, geo in sorted(estudio, key=lambda t: -t[1]):
        log(f"  {pr['MpNombre']:<12} {pr['Depto']:<8} DANE {pr['MpCodigo']}   "
            f"{largo:9,.1f} m   {100*largo/tot:5.1f} %")
        feats_e.append({"type": "Feature", "properties": {
            "MpNombre": pr['MpNombre'], "Depto": pr['Depto'], "MpCodigo": pr['MpCodigo'],
            "area_ha": round(pr['MpArea'], 2), "trazado_m": round(largo, 1),
            "pct_trazado": round(100*largo/tot, 1), "rol": "area de estudio", "marca": "CP"},
            "geometry": mapping(geo)})
    log(f"  {'SUMA':<12} {'':<8} {'':<10}   {tot:9,.1f} m   "
        f"(geodésica del trazado: {L:,.1f} m, dif {tot-L:+.1f} m)")

    def guardar(nombre, feats):
        json.dump({"type": "FeatureCollection", "name": nombre,
                   "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
                   "features": feats},
                  open(os.path.join(D_ACT1, nombre + '.geojson'), 'w', encoding='utf-8'),
                  ensure_ascii=False)
    guardar('limites_area_estudio', feats_e)
    guardar('limites_contexto', [{"type": "Feature", "properties": {
        "MpNombre": pr['MpNombre'], "Depto": pr['Depto'], "MpCodigo": pr['MpCodigo'],
        "rol": "contexto", "marca": "F"}, "geometry": mapping(geo)} for pr, geo in contexto])
    velo = ventana.difference(unary_union([shape(f['geometry']) for f in feats_e]))
    guardar('mascara_exterior', [{"type": "Feature", "properties": {
        "nombre": "Fuera del area de estudio", "marca": "CP"}, "geometry": mapping(velo)}])
    log(f"  contexto: {len(contexto)} municipios vecinos dentro del encuadre del mapa")
    log("  -> Act1_DEM/limites_area_estudio.geojson, limites_contexto.geojson, mascara_exterior.geojson")

    # ¿en qué municipio cae cada portal? Esto es lo que corrige el rótulo.
    from shapely.geometry import Point
    ubic = {}
    for nom, pt in (('oriental', Point(PE[1], PE[0])), ('occidental', Point(PW[1], PW[0]))):
        hit = [pr for pr, _, geo in estudio if geo.contains(pt)]
        ubic[nom] = {'municipio': hit[0]['MpNombre'], 'depto': hit[0]['Depto'],
                     'cod_dane': hit[0]['MpCodigo']} if hit else None
        log(f"  portal {nom:<11} -> {ubic[nom]}")

    # --- sensibilidad a la ventana de búsqueda -------------------------------
    # La ventana oriental es una restricción ACTIVA: el portal adoptado cae a
    # ~440 m de su borde occidental. Se publica qué pasaría al ampliarla.
    log("  sensibilidad a la ventana de búsqueda:")
    todos = [(pr, geo) for pr, geo in
             [(f['properties'], shape(f['geometry'])) for f in mun['features']]]
    def municipio_de(lo, la):
        pt = Point(lo, la)
        r = [pr['MpNombre'] for pr, geo in todos if geo.contains(pt)]
        return r[0] if r else 'fuera de Tolima/Quindío'
    filas_v = []
    for eti, vE, vW in VENTANAS_SENS:
        cE = buscar_candidatos(band, src, COTA_E, vE, TOL)
        cW = buscar_candidatos(band, src, COTA_W, vW, TOL)
        if not cE or not cW: continue
        d, (aE, oE, zE), (aW, oW, zW) = par_mas_corto(cE, cW)
        mE, mW = municipio_de(oE, aE), municipio_de(oW, aW)
        pegado = abs(oE - vE[1][0]) < 0.0051
        filas_v.append(dict(ventana=eti, n_cand_E=len(cE), n_cand_W=len(cW),
                            lat_E=round(aE,4), lon_E=round(oE,4), cota_E=round(zE,1),
                            municipio_E=mE, lat_W=round(aW,4), lon_W=round(oW,4),
                            cota_W=round(zW,1), municipio_W=mW, longitud_m=round(d,1),
                            pendiente_pct=round(100*(zW-zE)/d,4),
                            portal_E_pegado_al_borde='si' if pegado else 'no'))
        log(f"    {eti:<20} L {d:9,.1f} m  pend {100*(zW-zE)/d:6.4f} %  "
            f"portal E en {mE:<10} {'(pegado al borde)' if pegado else ''}")
    with open(os.path.join(D_ACT2,'ventanas_sensibilidad.csv'),'w',newline='',encoding='utf-8-sig') as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas_v[0].keys())); w.writeheader()
        for r in filas_v: w.writerow(r)
    log("  -> Act2_Portales/ventanas_sensibilidad.csv")

    # --- puntos de control de portales, con jurisdicción ---------------------
    # El rótulo distingue dos cosas que la versión 1 confundía:
    #   'extremo'   = cómo nombra la ponencia ese extremo del corredor  [F, p.20]
    #   'municipio' = dónde cae realmente el portal calculado            [CP]
    # El portal occidental está en Calarcá, NO en Armenia.
    def rot(nom, extremo, u):
        return f"Portal {nom} · extremo {extremo} · {u['municipio']}, {u['depto']}"
    geo = {"type":"FeatureCollection","name":"puntos_control_portales",
      "crs":{"type":"name","properties":{"name":"urn:ogc:def:crs:OGC:1.3:CRS84"}},
      "features":[
        {"type":"Feature","properties":{
            "nombre": rot('oriental','Ibagué',ubic['oriental']),
            "extremo_corredor":"Ibagué","extremo_marca":"F, dia. 20",
            "municipio":ubic['oriental']['municipio'],"depto":ubic['oriental']['depto'],
            "cod_dane":ubic['oriental']['cod_dane'],
            "cota_msnm":round(PE[2],1),"cota_objetivo_msnm":COTA_E,"tol_m":TOL,"marca":"CP"},
         "geometry":{"type":"Point","coordinates":[PE[1],PE[0]]}},
        {"type":"Feature","properties":{
            "nombre": rot('occidental','Armenia',ubic['occidental']),
            "extremo_corredor":"Armenia","extremo_marca":"F, dia. 20",
            "municipio":ubic['occidental']['municipio'],"depto":ubic['occidental']['depto'],
            "cod_dane":ubic['occidental']['cod_dane'],
            "cota_msnm":round(PW[2],1),"cota_objetivo_msnm":COTA_W,"tol_m":TOL,"marca":"CP"},
         "geometry":{"type":"Point","coordinates":[PW[1],PW[0]]}}]}
    with open(os.path.join(D_ACT2,'puntos_control_portales.geojson'),'w',encoding='utf-8') as fh:
        json.dump(geo,fh,ensure_ascii=False,indent=1)
    log("  portales -> Act2_Portales/puntos_control_portales.geojson")
    base = os.path.join(D_ACT2,'puntos_control_portales')
    if escribir_shp(base, 1,
        [((PE[1],PE[0]), ['Portal oriental', 'Ibagué', ubic['oriental']['municipio'],
                          ubic['oriental']['depto'], ubic['oriental']['cod_dane'],
                          round(PE[2],1), COTA_E, TOL, 'CP']),
         ((PW[1],PW[0]), ['Portal occidental','Armenia', ubic['occidental']['municipio'],
                          ubic['occidental']['depto'], ubic['occidental']['cod_dane'],
                          round(PW[2],1), COTA_W, TOL, 'CP'])],
        [('nombre','C',20,0),('extremo','C',12,0),('municipio','C',20,0),('depto','C',12,0),
         ('cod_dane','C',6,0),('cota_msnm','N',10,1),('cota_obj','N',10,1),
         ('tol_m','N',6,1),('marca','C',4,0)]):
        log("  portales -> Act2_Portales/puntos_control_portales.shp")
    return feats_e, ubic


def _pixeles_con_dato(ruta):
    """Píxeles con valor válido (distinto de nodata) en un ráster de una banda."""
    with rasterio.open(ruta) as s:
        a = s.read(1); nd = s.nodata
    if nd is None:
        return int(a.size)
    if isinstance(nd, float) and np.isnan(nd):
        return int(np.count_nonzero(~np.isnan(a)))
    return int(np.count_nonzero(a != nd))


def paso_departamentos():
    """Descarga la capa de departamentos del IGAC: capa 1 del MISMO MapServer que
    los municipios (capa 0). Solo alimenta el mapa de localización del layout; no
    entra en ningún cálculo del OE 1. El servicio NO admite paginación
    ('Pagination is not supported'), así que se pide todo y se cuenta en local."""
    import urllib.request, urllib.parse, time
    log("PASO 1b — Capa de departamentos del IGAC (localización del layout)")
    q = urllib.parse.urlencode({
        'where': '1=1', 'outFields': '*', 'returnGeometry': 'true',
        'geometryPrecision': '4', 'maxAllowableOffset': '0.01',
        'outSR': '4326', 'f': 'geojson'})
    url = f"{IGAC_DEPARTAMENTOS}?{q}"
    log("  descargando departamentos (sin resultRecordCount) ...")
    ultimo = None
    for intento in range(1, 6):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                crudo = r.read()
            dep = json.loads(crudo)
            if 'features' not in dep:
                raise ValueError(f"respuesta sin 'features': {crudo[:200]!r}")
            open(OUT_DEPARTAMENTOS, 'wb').write(crudo)
            break
        except Exception as e:
            ultimo = e
            log(f"  intento {intento}/5 falló ({e}); reintento en 8 s")
            time.sleep(8)
    else:
        raise SystemExit(f"ERROR: no se pudo descargar la capa de departamentos "
                         f"del IGAC tras 5 intentos ({ultimo}).")
    dep = json.load(open(OUT_DEPARTAMENTOS, encoding='utf-8'))
    nombres = {f.get('properties', {}).get('DeNombre') for f in dep['features']}
    n = len(dep['features'])
    log(f"  departamentos: {n}")
    faltan = [d for d in ('Tolima', 'Quindío') if d not in nombres]
    if n != 33 or faltan:
        raise SystemExit(
            f"ERROR: descarga de departamentos inconsistente (features={n}, "
            f"faltan={faltan}). Se detiene: sin esta capa el layout no puede "
            f"dibujar la localización.")
    log(f"  verificado: 33 features e incluye Tolima y Quindío -> "
        f"{os.path.relpath(OUT_DEPARTAMENTOS, RAIZ)}")


def paso_dem_area(filas):
    """Recorta el DEM al contorno del área de estudio (los tres municipios que
    cruza el trazado). Se corta desde el MOSAICO 'dem_corredor.tif' (lon -76..-74,
    lat 4..5), NO desde DEM_corredor_recorte.tif, cuya ventana no cubre la esquina
    nororiental de Ibagué. Es un insumo SOLO de dibujo: no cambia ninguna cifra
    (el análisis sigue leyendo DEM_corredor_recorte.tif)."""
    log("PASO 8 — Recorte del DEM al área de estudio")
    n_rec = _pixeles_con_dato(OUT_DEM_RECORTE)

    hecho, via = False, None
    try:
        from osgeo import gdal
        gdal.UseExceptions()
        gdal.Warp(
            str(OUT_DEM_AREA),                  # Act1_DEM\DEM_area_estudio.tif
            str(MOSAICO_DEM),                   # dem_corredor.tif (mosaico completo)
            cutlineDSName=str(OUT_LIM_AREA),    # limites_area_estudio.geojson
            cropToCutline=True,
            dstNodata=-9999,
            dstAlpha=False,
            multithread=True,
        )
        hecho, via = True, "gdal.Warp"
    except Exception as e:
        log(f"  gdal.Warp no disponible ({e}); se prueba rasterio.mask.mask")
    if not hecho:
        try:
            import rasterio.mask
            geoms = [f['geometry'] for f in
                     json.load(open(OUT_LIM_AREA, encoding='utf-8'))['features']]
            with rasterio.open(MOSAICO_DEM) as srcr:
                img, tr = rasterio.mask.mask(srcr, geoms, crop=True, nodata=-9999)
                meta = srcr.meta.copy()
            meta.update(height=img.shape[1], width=img.shape[2], transform=tr,
                        nodata=-9999, compress='deflate')
            with rasterio.open(OUT_DEM_AREA, 'w', **meta) as d:
                d.write(img)
            hecho, via = True, "rasterio.mask.mask"
        except Exception as e:
            raise SystemExit(
                f"ERROR: gdal.Warp y rasterio.mask.mask fallaron los dos ({e}). "
                f"No se puede generar el DEM del área de estudio.")
    log(f"  recorte por {via} (fuente: mosaico {MOSAICO_DEM})")

    # --- los bounds deben cubrir TODO el bbox de los tres municipios ----------
    _mun = json.load(open(OUT_LIM_AREA, encoding='utf-8'))
    _xs, _ys = [], []

    def _walk(c):
        if isinstance(c, (list, tuple)):
            if c and isinstance(c[0], (int, float)):
                _xs.append(c[0]); _ys.append(c[1])
            else:
                for e in c:
                    _walk(e)
    for f in _mun['features']:
        _walk(f['geometry']['coordinates'])
    mx0, my0, mx1, my1 = min(_xs), min(_ys), max(_xs), max(_ys)
    with rasterio.open(OUT_DEM_AREA) as db:
        b = db.bounds
        px = max(abs(db.transform.a), abs(db.transform.e))
    log(f"  bounds DEM_area_estudio.tif: O {b.left:.4f}  S {b.bottom:.4f}  "
        f"E {b.right:.4f}  N {b.top:.4f}")
    log(f"  bbox de los tres municipios:  O {mx0:.4f}  S {my0:.4f}  "
        f"E {mx1:.4f}  N {my1:.4f}   (objetivo mínimo O -75.805 S 4.237 E -74.966 N 4.701)")
    tol = 2 * px   # holgura ~2 píxeles: redondeo de ventana + redondeo de las cifras del enunciado
    cubre = (b.left <= mx0 + tol and b.bottom <= my0 + tol
             and b.right >= mx1 - tol and b.top >= my1 - tol
             and b.left <= -75.805 + tol and b.bottom <= 4.237 + tol
             and b.right >= -74.966 - tol and b.top >= 4.701 - tol)
    if not cubre:
        raise SystemExit(
            f"ERROR: los bounds de DEM_area_estudio.tif no cubren el área de "
            f"estudio completa. bounds=({b.left:.4f},{b.bottom:.4f},{b.right:.4f},"
            f"{b.top:.4f}) vs bbox municipios=({mx0:.4f},{my0:.4f},{mx1:.4f},{my1:.4f}).")
    log("  bounds cubren el área de estudio completa: OK")

    n_area = _pixeles_con_dato(OUT_DEM_AREA)
    log(f"  píxeles con dato: recorte del corredor {n_rec:,}  ->  "
        f"área de estudio {n_area:,}  "
        f"({'OK, menor' if n_area < n_rec else 'FALLA: no es menor'})")
    if not n_area < n_rec:
        raise SystemExit(
            f"ERROR: el DEM del área de estudio ({n_area} px) no tiene menos "
            f"píxeles con dato que el del corredor ({n_rec} px).")

    with rasterio.open(OUT_DEM_AREA) as da:
        banda = da.read(1); nd = da.nodata; h, w = banda.shape
        malas = []
        for f in filas:
            r, c = da.index(f['lon'], f['lat'])
            if not (0 <= r < h and 0 <= c < w) or banda[r, c] == nd:
                malas.append(round(f['pk'], 1))
    log(f"  cota del DEM recortado en las {len(filas)} abscisas de la cartera: "
        f"{len(malas)} en nodata")
    if malas:
        raise SystemExit(
            f"ERROR: {len(malas)} abscisas de la cartera caen en nodata del DEM "
            f"recortado (PK {malas} m). El contorno municipal no cubre todo el "
            f"trazado y el recorte no se puede aplicar.")
    log(f"  las {len(filas)} abscisas de la cartera tienen dato en el DEM "
        f"recortado -> {os.path.relpath(OUT_DEM_AREA, RAIZ)}")


if __name__ == '__main__':
    log("=== OE 1 · Semillero GEOPAV · procesamiento v2 ===")
    ruta_rec = paso1_dem()
    paso_departamentos()
    src = rasterio.open('dem_corredor.tif'); band = src.read(1)
    ema = paso2_validar(band, src)
    PE, PW, L, sens = paso3_portales(band, src)
    pf, verts, largo, cierre = paso4_trazado(band, src, PE, PW, L)
    filas, pasos = paso5_cartera(band, src, pf, PE, PW, L)
    feats_mun, ubic_portales = paso6_municipios(band, src, PE, PW, L, verts)
    paso_dem_area(filas)

    # comprobación: el recorte entregado debe dar exactamente lo mismo que el mosaico
    log("PASO 7 — Comprobación de coherencia mosaico / recorte")
    with rasterio.open(ruta_rec) as rc:
        b2 = rc.read(1); ok = True
        for n,la,lo in [("portal E",PE[0],PE[1]),("portal W",PW[0],PW[1])]+[(v[0],v[1],v[2]) for v in VALIDACION]:
            r,c = rc.index(lo,la); v2 = float(b2[r,c]); v1 = cota_en(band,src,la,lo)
            estado = "OK" if abs(v1-v2)<1e-6 else "DIFIERE"
            if estado=="DIFIERE": ok=False
            log(f"  {n:<12} mosaico {v1:8.1f}   recorte {v2:8.1f}   {estado}")
    log(f"  coherencia mosaico/recorte: {'CORRECTA' if ok else 'FALLIDA'}")

    cobA = np.array([f['cobertura'] for f in pf])
    terA = np.array([f['terreno'] for f in pf])
    pend = 100*(PW[2]-PE[2])/L
    cifras = dict(
      version="2", fecha=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
      tol_adoptada_m=TOL,
      portal_oriental=dict(lat=round(PE[0],4),lon=round(PE[1],4),cota_msnm=round(PE[2],1)),
      portal_occidental=dict(lat=round(PW[0],4),lon=round(PW[1],4),cota_msnm=round(PW[2],1)),
      longitud_m=round(L,1), longitud_km=round(L/1000,3),
      desnivel_m=round(PW[2]-PE[2],1), pendiente_pct=round(pend,4),
      criterio_pendiente_pct=CRITERIO_PEND, cumple_pendiente=bool(pend<CRITERIO_PEND),
      cota_max_terreno_msnm=round(float(terA.max()),1),
      cobertura_max_m=round(float(cobA.max()),1),
      cobertura_media_m=round(float(cobA.mean()),1),
      cobertura_min_m=round(float(cobA.min()),1),
      pct_trazado_cobertura_mayor_700m=round(float(100*(cobA>700).mean()),1),
      n_abscisas_cartera=len(filas), paso_cartera_m=PASO_CARTERA,
      error_medio_absoluto_dem_m=round(float(ema),1),
      cierre_trazado_portal_m=round(cierre,2),
      portal_oriental_ubicacion=ubic_portales['oriental'],
      portal_occidental_ubicacion=ubic_portales['occidental'],
      area_estudio=[{k: f['properties'][k] for k in
                     ('MpNombre','Depto','MpCodigo','trazado_m','pct_trazado')}
                    for f in feats_mun],
      sensibilidad=[{k:(round(v,4) if isinstance(v,float) else v) for k,v in s.items()} for s in sens])
    with open(os.path.join(RAIZ,'cifras_OE1.json'),'w',encoding='utf-8') as fh:
        json.dump(cifras,fh,ensure_ascii=False,indent=2)
    log("  cifras congeladas -> cifras_OE1.json  (fuente de verdad del OE 1)")
    src.close()
    log("=== fin ===")
    open(os.path.join(D_ACT1,'registro_geoprocesos.log'),'w',encoding='utf-8').write("\n".join(LOG)+"\n")
    print("\nRegistro escrito en Act1_DEM/registro_geoprocesos.log")
