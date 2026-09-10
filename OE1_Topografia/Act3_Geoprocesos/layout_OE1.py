# -*- coding: utf-8 -*-
"""
OE 1 — Diseño de impresión (layout) del mapa topográfico
Semillero de Investigación GEOPAV · Universidad de Ibagué · Paz y Región 2026B
Responsable: Tamayo Osorio Miguel Ángel

Ejecuta con la Python de QGIS en modo standalone:
  "C:\\Program Files\\QGIS 3.44.13\\bin\\python-qgis-ltr.bat" layout_OE1.py

El script:
  A) Corrige la fuente de las etiquetas de "Portales (control)" y reconstruye
     la leyenda de "DEM elevacion (pseudocolor)" con estadísticas reales.
  B) Crea un diseño de impresión A3 apaisado llamado "Mapa_OE1".
  C) Exporta a PNG 300 ppp y PDF vectorial.
  D) Guarda el proyecto .qgz para que el layout quede dentro.
  E) Escribe un registro append en registro_geoprocesos.log.
"""

import os, sys
from pathlib import Path
from datetime import datetime, timezone

# ── rutas relativas al propio script ────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent          # Act3_Geoprocesos
OE1_DIR    = SCRIPT_DIR.parent                        # OE1_Topografia
QGZ_PATH   = OE1_DIR / "OE1_trazado.qgz"
LOGO_PATH  = OE1_DIR / "logo_unibague.png"
VIS_DIR    = OE1_DIR / "Visuales"
LOG_PATH   = OE1_DIR / "Act1_DEM" / "registro_geoprocesos.log"
OUT_PNG    = VIS_DIR / "mapa_OE1_layout.png"
OUT_PDF    = VIS_DIR / "mapa_OE1_layout.pdf"

# ── cifras del OE 1: única fuente de verdad, ninguna cifra se escribe a mano ─
import json
CIF_PATH = OE1_DIR / "cifras_OE1.json"
with open(CIF_PATH, encoding="utf-8") as fh:
    CIF = json.load(fh)

def num(v, dec):
    """Formato es-CO: punto de miles, coma decimal."""
    s = f"{v:,.{dec}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")

import csv
PERFIL = OE1_DIR / "Act5_Perfil" / "perfil_continuo.csv"
with open(PERFIL, encoding="utf-8-sig") as fh:
    filas = list(csv.DictReader(fh))
_fmax = max(filas, key=lambda r: float(r["Cobertura_m"]))
PK_COB_MAX_KM = float(_fmax["PK_m"]) / 1000.0

# ── inicialización standalone de QGIS ───────────────────────────────────────

from qgis.core import (
    QgsApplication, QgsProject, QgsRasterBandStats,
    QgsRasterShader, QgsColorRampShader, QgsSingleBandPseudoColorRenderer,
    QgsTextFormat, QgsTextBufferSettings,
    QgsPrintLayout, QgsLayoutItemMap, QgsLayoutItemLabel,
    QgsLayoutItemPicture, QgsLayoutItemLegend, QgsLayoutItemScaleBar,
    QgsLayoutPoint, QgsLayoutSize, QgsUnitTypes,
    QgsLayoutExporter, QgsLayoutItemPage,
    QgsRectangle, QgsCoordinateReferenceSystem,
    QgsLayoutMeasurement,
)
from qgis.core import Qgis
from qgis.PyQt.QtCore import QRectF, QSizeF, Qt
from qgis.PyQt.QtGui import QColor, QFont

# Iniciar QgsApplication
prefix = os.environ.get("QGIS_PREFIX_PATH",
                         r"C:\Program Files\QGIS 3.44.13\apps\qgis-ltr")
QgsApplication.setPrefixPath(prefix, True)
qgs = QgsApplication([], True)
qgs.initQgis()

from qgis.PyQt.QtGui import QFontDatabase
_fams = QFontDatabase().families()
print(f"Fuentes disponibles: {len(_fams)}")
if len(_fams) < 10 or not any(f.startswith("Arial") for f in _fams):
    sys.exit("ERROR: la base de fuentes de Qt no cargo. El PNG saldria "
             "con rectangulos negros. Ejecuta desde la Consola de "
             "Python de QGIS Desktop.")

QGIS_VER = Qgis.version()
print(f"QGIS {QGIS_VER} inicializado en modo standalone.")

# ── abrir el proyecto ───────────────────────────────────────────────────────
project = QgsProject.instance()
if not project.read(str(QGZ_PATH)):
    sys.exit(f"ERROR: no se pudo abrir {QGZ_PATH}")
print(f"Proyecto abierto: {QGZ_PATH.name}")

# ── funciones auxiliares ────────────────────────────────────────────────────
def capa(nombre):
    """Busca una capa por nombre exacto."""
    hits = project.mapLayersByName(nombre)
    if not hits:
        raise RuntimeError(f"Capa «{nombre}» no encontrada en el proyecto.")
    return hits[0]


def fmt_miles(v):
    """Formatea un entero con separador de miles punto (es-CO)."""
    return f"{int(v):,}".replace(",", ".")


def bbox_geojson(path, keep=None):
    """Bounding box (xmin, ymin, xmax, ymax) de un GeoJSON, leyendo el archivo
    (no coordenadas a mano). `keep(props)->bool` filtra features."""
    data = json.load(open(path, encoding="utf-8"))
    xs, ys = [], []

    def _walk(c):
        if isinstance(c, (list, tuple)):
            if c and isinstance(c[0], (int, float)):
                xs.append(c[0]); ys.append(c[1])
            else:
                for e in c:
                    _walk(e)

    for f in data["features"]:
        if keep and not keep(f.get("properties", {}) or {}):
            continue
        _walk(f["geometry"]["coordinates"])
    return min(xs), min(ys), max(xs), max(ys)


def _fit_extent(x0, y0, x1, y1, item_w, item_h, pad=0.0):
    """Devuelve un QgsRectangle ya ajustado al aspecto del item de layout y
    centrado en el bbox, para que QGIS no recorte al fijar la extensión
    (setExtent ajusta el aspecto de forma inconsistente con un proyecto ya
    cargado). `pad` es margen relativo a cada lado."""
    from qgis.core import QgsRectangle as _R
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    w, h = (x1 - x0) * (1 + 2 * pad), (y1 - y0) * (1 + 2 * pad)
    ar = item_w / item_h
    if w / h < ar:
        w = h * ar
    else:
        h = w / ar
    return _R(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


# rutas de insumos que produce procesamiento_OE1.py
DEM_AREA_PATH   = OE1_DIR / "Act1_DEM" / "DEM_area_estudio.tif"
LIM_AREA_PATH   = OE1_DIR / "Act1_DEM" / "limites_area_estudio.geojson"
DEPTOS_PATH     = OE1_DIR / "Act1_DEM" / "departamentos_colombia_igac.geojson"
TOLQUI_PATH     = OE1_DIR / "Act1_DEM" / "limites_igac_tol_qui.geojson"
AZUL_INST       = "25,63,119,255"          # #193F77, azul institucional

# ═══════════════════════════════════════════════════════════════════════════
# A0) Repuntar las capas de DEM al recorte del área de estudio
#     (setDataSource: NO se borran ni se renombran; la comprobación D0 sigue
#     vigente). El relieve queda recortado a los tres municipios.
# ═══════════════════════════════════════════════════════════════════════════
from qgis.core import QgsDataProvider

if not DEM_AREA_PATH.exists():
    sys.exit(f"ERROR: falta {DEM_AREA_PATH}. Ejecuta antes procesamiento_OE1.py.")
for _nom in ("DEM elevacion (pseudocolor)", "DEM relieve sombreado (hillshade)"):
    _lyr = capa(_nom)
    _lyr.setDataSource(str(DEM_AREA_PATH), _nom, "gdal",
                       QgsDataProvider.ProviderOptions())
    if not _lyr.isValid():
        sys.exit(f"ERROR: «{_nom}» quedó inválida tras setDataSource a "
                 f"{DEM_AREA_PATH.name}. Se detiene.")
    print(f"A0) «{_nom}» ahora lee {DEM_AREA_PATH.name} (isValid: {_lyr.isValid()}).")

# Quitar del mapa principal las capas que no aportan al mensaje y no tienen
# entrada en convenciones: la máscara (el relieve va recortado) y el andamiaje
# de verificación del DEM. NO se eliminan del proyecto, sólo se desmarcan del
# árbol (la D0 comprueba nombres, no visibilidad).
_root_tree = project.layerTreeRoot()
for _nom in ("mascara_exterior", "limites_contexto",
             "puntos_verificacion_DEM", "Muestreado"):
    _hits = project.mapLayersByName(_nom)
    if not _hits:
        print(f"A0) «{_nom}» no está en el proyecto, se omite.")
        continue
    _n = _root_tree.findLayer(_hits[0].id())
    if _n is not None:
        _n.setItemVisibilityChecked(False)
    print(f"A0) «{_nom}» desmarcada del mapa principal (sigue en el proyecto).")

# ═══════════════════════════════════════════════════════════════════════════
# A1) Corregir fuente de etiquetas de "Portales (control)"
# ═══════════════════════════════════════════════════════════════════════════
lyr_port = capa("Portales (control)")
if lyr_port.labelsEnabled():
    labeling = lyr_port.labeling()
    if labeling is not None:
        settings = labeling.settings()
        tf = settings.format()
        fnt = tf.font()
        fnt.setFamily("Arial")
        fnt.setPointSizeF(9)
        fnt.setBold(True)
        tf.setFont(fnt)
        tf.setSize(9)
        tf.setSizeUnit(QgsUnitTypes.RenderPoints)
        # buffer blanco 1 mm
        buf = tf.buffer()
        buf.setEnabled(True)
        buf.setSize(1)
        buf.setSizeUnit(QgsUnitTypes.RenderMillimeters)
        buf.setColor(QColor(255, 255, 255))
        tf.setBuffer(buf)
        settings.setFormat(tf)
        labeling.setSettings(settings)
        lyr_port.setLabeling(labeling)
        lyr_port.triggerRepaint()
        print("A1) Fuente de etiquetas de «Portales (control)» → Arial 9 bold + buffer.")
else:
    print("A1) Advertencia: etiquetas no habilitadas en «Portales (control)».")

# ═══════════════════════════════════════════════════════════════════════════
# A2) Reconstruir la leyenda de "DEM elevacion (pseudocolor)" con stats
# ═══════════════════════════════════════════════════════════════════════════
lyr_dem = capa("DEM elevacion (pseudocolor)")
dp = lyr_dem.dataProvider()
stats = dp.bandStatistics(1, QgsRasterBandStats.All)
dem_min = stats.minimumValue
dem_max = stats.maximumValue
print(f"A2) Estadísticas reales DEM: mín = {dem_min:.2f}, máx = {dem_max:.2f}")

# Rampa hipsométrica idéntica a figuras_OE1.py: NO termina en blanco, para que
# la cordillera alta (la masa de roca sobre el túnel) no se lea como vacío.
# Los valores se reparten entre HIPSO_VMIN y HIPSO_VMAX, no entre dem_min/dem_max.
HIPSO_HEX = ['#2e6b45', '#5b8f4e', '#98ac5c', '#c9b97e',
             '#c2a184', '#a2705d', '#7d4b52', '#513349']
HIPSO_VMIN, HIPSO_VMAX = 450.0, 5250.0   # el recorte a los 3 municipios entra al Nevado del Tolima (459,7 a 5217,3 msnm)

n_classes = len(HIPSO_HEX)
step = (HIPSO_VMAX - HIPSO_VMIN) / (n_classes - 1)
values = [HIPSO_VMIN + i * step for i in range(n_classes)]
colors = [QColor(h) for h in HIPSO_HEX]

items = []
for v, c in zip(values, colors):
    label = f"{fmt_miles(v)} msnm"
    items.append(QgsColorRampShader.ColorRampItem(v, c, label))

shader_func = QgsColorRampShader()
shader_func.setColorRampType(QgsColorRampShader.Interpolated)
shader_func.setColorRampItemList(items)

shader = QgsRasterShader()
shader.setRasterShaderFunction(shader_func)

renderer = QgsSingleBandPseudoColorRenderer(dp, 1, shader)
lyr_dem.setRenderer(renderer)
lyr_dem.setOpacity(0.80)   # sube la presencia del relieve (antes 0.55)
lyr_dem.triggerRepaint()
print("A2) Leyenda de «DEM elevacion (pseudocolor)» reconstruida con 8 clases "
      "hipsométricas (misma rampa que figuras_OE1.py).")

# ═══════════════════════════════════════════════════════════════════════════
# B) Crear diseño de impresión "Mapa_OE1"
# ═══════════════════════════════════════════════════════════════════════════
LAYOUT_NAME = "Mapa_OE1"

# Idempotencia: eliminar layout previo si existe
manager = project.layoutManager()
old = manager.layoutByName(LAYOUT_NAME)
if old:
    manager.removeLayout(old)
    print(f"B) Layout anterior «{LAYOUT_NAME}» eliminado.")

layout = QgsPrintLayout(project)
layout.initializeDefaults()
layout.setName(LAYOUT_NAME)

# Página A3 apaisada (420 × 297 mm)
page = layout.pageCollection().page(0)
page.setPageSize(QgsLayoutSize(420, 297, QgsUnitTypes.LayoutMillimeters))

MARGIN = 10  # mm

# ── dimensiones de zonas ────────────────────────────────────────────────────
BAR_W = 100   # barra lateral derecha
MAP_W = 420 - 2 * MARGIN - BAR_W - 5  # ancho de la columna izquierda (5 mm gap)
MAP_H = 297 - 2 * MARGIN
MAP_X = MARGIN
MAP_Y = MARGIN
BAR_X = MAP_X + MAP_W + 5
BAR_Y = MARGIN
CONTENT_W = BAR_W  # ancho disponible en la barra lateral

# ── geometría de la lámina rediseñada (todo derivado de lo anterior) ────────
IZQ_X   = MARGIN
IZQ_W   = MAP_W                    # ancho de la columna izquierda
MAPA_H  = 175                      # alto del mapa principal
INF_Y   = MARGIN + MAPA_H + 5      # inicio de la banda inferior izquierda
INF_H   = 297 - MARGIN - INF_Y     # alto de la banda inferior
# La banda inferior izquierda va entera para los dos insets de localización
# (ver B1: COL_W / AREA_W). Convenciones, elevación, escala y norte están en la
# barra lateral derecha.

# ── Mapa principal (arriba a la izquierda) ─────────────────────────────────
map_item = QgsLayoutItemMap(layout)
map_item.attemptMove(QgsLayoutPoint(IZQ_X, MARGIN, QgsUnitTypes.LayoutMillimeters))
map_item.attemptResize(QgsLayoutSize(IZQ_W, MAPA_H, QgsUnitTypes.LayoutMillimeters))

# Encuadre = bbox de limites_area_estudio.geojson con 3 % de margen a cada lado
_ax0, _ay0, _ax1, _ay1 = bbox_geojson(LIM_AREA_PATH)
map_item.setExtent(_fit_extent(_ax0, _ay0, _ax1, _ay1, IZQ_W, MAPA_H, pad=0.03))
map_item.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

# Marco fino gris
map_item.setFrameEnabled(True)
map_item.setFrameStrokeColor(QColor(120, 120, 120))
map_item.setFrameStrokeWidth(QgsLayoutMeasurement(0.2, QgsUnitTypes.LayoutMillimeters))

layout.addLayoutItem(map_item)

# Cuadrícula de coordenadas
from qgis.core import QgsLayoutItemMapGrid
grid = QgsLayoutItemMapGrid("Graticule", map_item)
grid.setStyle(QgsLayoutItemMapGrid.Cross)
grid.setCrossLength(2)
grid.setIntervalX(0)  # 0 = automático
grid.setIntervalY(0)

# Etiquetas en los cuatro lados
grid.setAnnotationEnabled(True)
grid.setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, QgsLayoutItemMapGrid.Top)
grid.setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, QgsLayoutItemMapGrid.Bottom)
grid.setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, QgsLayoutItemMapGrid.Left)
grid.setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, QgsLayoutItemMapGrid.Right)
grid.setAnnotationDirection(QgsLayoutItemMapGrid.Horizontal, QgsLayoutItemMapGrid.Top)
grid.setAnnotationDirection(QgsLayoutItemMapGrid.Horizontal, QgsLayoutItemMapGrid.Bottom)
grid.setAnnotationDirection(QgsLayoutItemMapGrid.Vertical, QgsLayoutItemMapGrid.Left)
grid.setAnnotationDirection(QgsLayoutItemMapGrid.Vertical, QgsLayoutItemMapGrid.Right)

grid_font = QFont("Arial", 7)
grid_fmt = QgsTextFormat()
grid_fmt.setFont(grid_font)
grid_fmt.setSize(7)
grid_fmt.setSizeUnit(QgsUnitTypes.RenderPoints)
grid.setAnnotationTextFormat(grid_fmt)

map_item.grids().addGrid(grid)
print("B) Mapa principal creado con cuadrícula.")

# ═══════════════════════════════════════════════════════════════════════════
# B1) Mapa de localización de dos niveles (abajo a la izquierda)
# ═══════════════════════════════════════════════════════════════════════════
from qgis.core import (QgsVectorLayer, QgsSingleSymbolRenderer,
                       QgsFillSymbol, QgsLayoutItemMapOverview,
                       QgsPalLayerSettings, QgsVectorLayerSimpleLabeling)

for _p in (DEPTOS_PATH, TOLQUI_PATH, LIM_AREA_PATH):
    if not _p.exists():
        sys.exit(f"ERROR: falta {_p}. Ejecuta antes procesamiento_OE1.py.")


def _reset_layer(nombre):
    """Evita acumular capas auxiliares al re-ejecutar el script."""
    for _l in project.mapLayersByName(nombre):
        project.removeMapLayer(_l.id())


def _fill(color, outline="255,255,255,255", width="0.1"):
    return QgsSingleSymbolRenderer(QgsFillSymbol.createSimple(
        {"color": color, "outline_color": outline, "outline_width": width,
         "outline_style": "solid"}))


# Los dos mapas de localización van LADO A LADO en toda la banda inferior
# izquierda. Anchos distintos a propósito: Colombia es vertical, el área de
# estudio apaisada.
COL_W  = 75
AREA_X = IZQ_X + COL_W + 5
AREA_W = IZQ_W - COL_W - 5

# ── Inset Colombia ────────────────────────────────────────────────────────
_reset_layer("Departamentos (localizacion)")
_reset_layer("Tolima y Quindio (localizacion)")
dep_all = QgsVectorLayer(str(DEPTOS_PATH), "Departamentos (localizacion)", "ogr")
if not dep_all.isValid():
    sys.exit("ERROR: no se pudo cargar departamentos_colombia_igac.geojson.")
dep_all.setRenderer(_fill("238,238,238,255"))
project.addMapLayer(dep_all, False)          # registrada, fuera del árbol

dep_est = QgsVectorLayer(str(DEPTOS_PATH), "Tolima y Quindio (localizacion)", "ogr")
if not dep_est.setSubsetString("DeNombre IN ('Tolima', 'Quindío')"):
    print("B1) AVISO: el filtro de Tolima/Quindío no se aplicó; se resalta todo.")
dep_est.setRenderer(_fill(AZUL_INST))
project.addMapLayer(dep_est, False)

col_map = QgsLayoutItemMap(layout)
col_map.setFollowVisibilityPreset(False)
col_map.setLayers([dep_est, dep_all])
col_map.attemptMove(QgsLayoutPoint(IZQ_X, INF_Y, QgsUnitTypes.LayoutMillimeters))
col_map.attemptResize(QgsLayoutSize(COL_W, INF_H, QgsUnitTypes.LayoutMillimeters))
_cx0, _cy0, _cx1, _cy1 = bbox_geojson(
    DEPTOS_PATH, keep=lambda p: "San Andrés" not in (p.get("DeNombre") or ""))
col_map.setExtent(_fit_extent(_cx0, _cy0, _cx1, _cy1, COL_W, INF_H, pad=0.03))
col_map.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
col_map.setFrameEnabled(True)
col_map.setFrameStrokeColor(QColor(120, 120, 120))
col_map.setFrameStrokeWidth(QgsLayoutMeasurement(0.2, QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(col_map)

# Marcador rojo grueso sobre el área de estudio (a esa escala es un punto)
_ov = QgsLayoutItemMapOverview("ext-principal", col_map)
_ov.setLinkedMap(map_item)
_ov.setEnabled(True)
_ov.setFrameSymbol(QgsFillSymbol.createSimple(
    {"color": "208,2,27,0", "outline_color": "208,2,27,255",     # #D0021B
     "outline_style": "solid", "outline_width": "0.8"}))
col_map.overviews().addOverview(_ov)

# ── Inset área de estudio ─────────────────────────────────────────────────
_reset_layer("Municipios Tol-Qui (localizacion)")
_reset_layer("Area de estudio (localizacion)")
muni_lyr = QgsVectorLayer(str(TOLQUI_PATH), "Municipios Tol-Qui (localizacion)",
                          "ogr")
if not muni_lyr.isValid():
    sys.exit("ERROR: no se pudo cargar limites_igac_tol_qui.geojson.")
muni_lyr.setRenderer(_fill("226,226,226,255"))
project.addMapLayer(muni_lyr, False)

est_lyr = QgsVectorLayer(str(LIM_AREA_PATH), "Area de estudio (localizacion)",
                         "ogr")
if not est_lyr.isValid():
    sys.exit("ERROR: no se pudo cargar limites_area_estudio.geojson para el inset.")
est_lyr.setRenderer(_fill(AZUL_INST, width="0.2"))

_pls = QgsPalLayerSettings()
_pls.fieldName = "MpNombre"
_ptf = QgsTextFormat()
_ptf.setFont(QFont("Arial", 6))
_ptf.setSize(6)
_ptf.setSizeUnit(QgsUnitTypes.RenderPoints)
_ptf.setColor(QColor(255, 255, 255))
_pbuf = QgsTextBufferSettings()
_pbuf.setEnabled(True)
_pbuf.setSize(0.8)
_pbuf.setSizeUnit(QgsUnitTypes.RenderMillimeters)
_pbuf.setColor(QColor(30, 30, 30))
_ptf.setBuffer(_pbuf)
_pls.setFormat(_ptf)
est_lyr.setLabeling(QgsVectorLayerSimpleLabeling(_pls))
est_lyr.setLabelsEnabled(True)
project.addMapLayer(est_lyr, False)

est_map = QgsLayoutItemMap(layout)
est_map.setFollowVisibilityPreset(False)
# dep_all al fondo como contexto gris: llena el marco apaisado sin bandas blancas
est_map.setLayers([capa("Trazado tunel (preliminar)"), est_lyr, muni_lyr, dep_all])
est_map.attemptMove(QgsLayoutPoint(AREA_X, INF_Y, QgsUnitTypes.LayoutMillimeters))
est_map.attemptResize(QgsLayoutSize(AREA_W, INF_H, QgsUnitTypes.LayoutMillimeters))
_ex0, _ey0, _ex1, _ey1 = bbox_geojson(LIM_AREA_PATH)
est_map.setExtent(_fit_extent(_ex0, _ey0, _ex1, _ey1, AREA_W, INF_H, pad=0.25))
est_map.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
est_map.setBackgroundEnabled(True)
est_map.setBackgroundColor(QColor(238, 238, 238))   # sin blancos por huecos de simplificación
est_map.setFrameEnabled(True)
est_map.setFrameStrokeColor(QColor(120, 120, 120))
est_map.setFrameStrokeWidth(QgsLayoutMeasurement(0.2, QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(est_map)


def _rotulo_inset(texto, x):
    """Rótulo en un recuadro blanco sobre la esquina superior izquierda del inset."""
    _l = QgsLayoutItemLabel(layout)
    _l.setText(texto)
    _lf = QgsTextFormat()
    _lf.setFont(QFont("Arial", 7))
    _lf.setSize(7)
    _lf.setSizeUnit(QgsUnitTypes.RenderPoints)
    _l.setTextFormat(_lf)
    _l.setBackgroundEnabled(True)
    _l.setBackgroundColor(QColor(255, 255, 255, 225))
    try:
        _l.setMarginX(1.2); _l.setMarginY(0.6)
    except Exception:
        pass
    _l.attemptMove(QgsLayoutPoint(x + 1.2, INF_Y + 1.2,
                                  QgsUnitTypes.LayoutMillimeters))
    _l.attemptResize(QgsLayoutSize(30, 5.2, QgsUnitTypes.LayoutMillimeters))
    _l.setHAlign(Qt.AlignLeft)
    _l.setVAlign(Qt.AlignVCenter)
    layout.addLayoutItem(_l)


_rotulo_inset("Colombia", IZQ_X)
_rotulo_inset("Área de estudio", AREA_X)
print("B1) Insets de localización lado a lado (Colombia + área de estudio).")

# ── Barra lateral derecha ──────────────────────────────────────────────────
y_cursor = BAR_Y  # cursor vertical en la barra lateral

# Logo institucional (sólo si existe)
if LOGO_PATH.exists():
    logo = QgsLayoutItemPicture(layout)
    logo.setPicturePath(str(LOGO_PATH))
    logo_h = 25  # mm de alto
    logo.attemptMove(QgsLayoutPoint(BAR_X, y_cursor, QgsUnitTypes.LayoutMillimeters))
    logo.attemptResize(QgsLayoutSize(CONTENT_W, logo_h, QgsUnitTypes.LayoutMillimeters))
    logo.setResizeMode(QgsLayoutItemPicture.ZoomResizeFrame)
    layout.addLayoutItem(logo)
    y_cursor += logo_h + 4
    print("B) Logo institucional insertado.")
else:
    y_cursor += 2
    print("B) Logo no encontrado, se omite sin error.")

# Título
lbl_title = QgsLayoutItemLabel(layout)
lbl_title.setText("Trazado preliminar del túnel de base\nIbagué - Armenia")
lbl_title.setFont(QFont("Arial", 14))
fmt_title = QgsTextFormat()
fmt_title.setFont(QFont("Arial", 14))
fmt_title.setSize(14)
fmt_title.setSizeUnit(QgsUnitTypes.RenderPoints)
fnt_t = fmt_title.font()
fnt_t.setBold(True)
fmt_title.setFont(fnt_t)
lbl_title.setTextFormat(fmt_title)
lbl_title.attemptMove(QgsLayoutPoint(BAR_X, y_cursor, QgsUnitTypes.LayoutMillimeters))
lbl_title.attemptResize(QgsLayoutSize(CONTENT_W, 22, QgsUnitTypes.LayoutMillimeters))
lbl_title.setHAlign(Qt.AlignLeft)
lbl_title.setVAlign(Qt.AlignTop)
layout.addLayoutItem(lbl_title)
y_cursor += 24

# Subtítulo
lbl_sub = QgsLayoutItemLabel(layout)
lbl_sub.setText("Objetivo específico 1 — Análisis topográfico")
fmt_sub = QgsTextFormat()
fmt_sub.setFont(QFont("Arial", 10))
fmt_sub.setSize(10)
fmt_sub.setSizeUnit(QgsUnitTypes.RenderPoints)
lbl_sub.setTextFormat(fmt_sub)
lbl_sub.attemptMove(QgsLayoutPoint(BAR_X, y_cursor, QgsUnitTypes.LayoutMillimeters))
lbl_sub.attemptResize(QgsLayoutSize(CONTENT_W, 10, QgsUnitTypes.LayoutMillimeters))
lbl_sub.setHAlign(Qt.AlignLeft)
lbl_sub.setVAlign(Qt.AlignTop)
layout.addLayoutItem(lbl_sub)
y_cursor += 13

# Bloque institucional
lbl_inst = QgsLayoutItemLabel(layout)
lbl_inst.setText(
    "Universidad de Ibagué\n"
    "Semestre Paz y Región 2026B\n"
    "Semillero de Investigación GEOPAV\n"
    "Responsable: Tamayo Osorio Miguel Ángel"
)
fmt_inst = QgsTextFormat()
fmt_inst.setFont(QFont("Arial", 8))
fmt_inst.setSize(8)
fmt_inst.setSizeUnit(QgsUnitTypes.RenderPoints)
lbl_inst.setTextFormat(fmt_inst)
lbl_inst.attemptMove(QgsLayoutPoint(BAR_X, y_cursor, QgsUnitTypes.LayoutMillimeters))
lbl_inst.attemptResize(QgsLayoutSize(CONTENT_W, 22, QgsUnitTypes.LayoutMillimeters))
lbl_inst.setHAlign(Qt.AlignLeft)
lbl_inst.setVAlign(Qt.AlignTop)
layout.addLayoutItem(lbl_inst)
y_cursor += 24

# Descripción breve
lbl_desc = QgsLayoutItemLabel(layout)
lbl_desc.setText(
    "Alineamiento recto entre portales obtenido sobre el modelo de "
    "elevación digital Copernicus DEM GLO-30 (~30 m). Longitud "
    f"{num(CIF['longitud_km'], 2)} km, desnivel {num(CIF['desnivel_m'], 1)} m, "
    f"pendiente de rasante {num(CIF['pendiente_pct'], 3)} % (criterio < "
    f"{num(CIF['criterio_pendiente_pct'], 1)} %). Cobertura máxima "
    f"{num(CIF['cobertura_max_m'], 0)} m en el PK {num(PK_COB_MAX_KM, 1)}. "
    "La ubicación de los portales responde a un criterio geométrico, no "
    "geotécnico: falta cruzarla con la susceptibilidad a movimientos en "
    "masa. Documento de nivel conceptual; no constituye diseño."
)
print(f"CIFRAS PUBLICADAS: long={CIF['longitud_km']} km · "
      f"desnivel={CIF['desnivel_m']} m · pend={CIF['pendiente_pct']} % · "
      f"cob_max={CIF['cobertura_max_m']} m · PK={PK_COB_MAX_KM:.1f} km")
fmt_desc = QgsTextFormat()
fmt_desc.setFont(QFont("Arial", 8))
fmt_desc.setSize(8)
fmt_desc.setSizeUnit(QgsUnitTypes.RenderPoints)
lbl_desc.setTextFormat(fmt_desc)
lbl_desc.attemptMove(QgsLayoutPoint(BAR_X, y_cursor, QgsUnitTypes.LayoutMillimeters))
lbl_desc.attemptResize(QgsLayoutSize(CONTENT_W, 36, QgsUnitTypes.LayoutMillimeters))
lbl_desc.setHAlign(Qt.AlignJustify)
lbl_desc.setVAlign(Qt.AlignTop)
layout.addLayoutItem(lbl_desc)
y_cursor += 38   # encadenado: sin hueco grande hasta las convenciones

# ═══════════════════════════════════════════════════════════════════════════
# Barra lateral derecha (cont.): convenciones, elevación, escala, norte
#   apiladas bajo la descripción y encima del pie de créditos; y_cursor encadena.
# ═══════════════════════════════════════════════════════════════════════════
from qgis.core import QgsLegendStyle, QgsLayoutItemShape

# ── Convenciones ─────────────────────────────────────────────────────────
legend = QgsLayoutItemLegend(layout)
legend.setTitle("Convenciones")
legend.setLinkedMap(map_item)
legend.setAutoUpdateModel(False)
legend.setResizeToContents(False)

for style_type in [QgsLegendStyle.Title, QgsLegendStyle.Subgroup,
                   QgsLegendStyle.Group, QgsLegendStyle.SymbolLabel]:
    st = legend.style(style_type)
    tf_leg = st.textFormat()
    tf_leg.setFont(QFont("Arial", 8))
    tf_leg.setSize(8)
    tf_leg.setSizeUnit(QgsUnitTypes.RenderPoints)
    st.setTextFormat(tf_leg)
    legend.setStyle(style_type, st)

st_title = legend.style(QgsLegendStyle.Title)
tf_title = st_title.textFormat()
tf_title.setFont(QFont("Arial", 9))
tf_title.setSize(9)
tf_title.setSizeUnit(QgsUnitTypes.RenderPoints)
fnt_leg_t = tf_title.font()
fnt_leg_t.setBold(True)
tf_title.setFont(fnt_leg_t)
st_title.setTextFormat(tf_title)
legend.setStyle(QgsLegendStyle.Title, st_title)

# Quitar del modelo de la leyenda las capas ráster y el andamiaje de trabajo:
# deben quedar SOLO las tres entradas de convenciones.
_QUITAR_LEYENDA = {
    "DEM elevacion (pseudocolor)", "DEM relieve sombreado (hillshade)",
    "mascara_exterior", "limites_contexto",
    "puntos_verificacion_DEM", "Muestreado",
}
for _nodo in list(legend.model().rootGroup().findLayers()):
    if _nodo.layer() is not None and _nodo.layer().name() in _QUITAR_LEYENDA:
        _nodo.parent().removeChildNode(_nodo)

# Renombrar las tres entradas restantes SIN tocar el nombre real de la capa
# (setName() renombra la capa del proyecto; setCustomProperty no).
RENOMBRES = {
    "Portales (control)":         "Portales del túnel",
    "Trazado tunel (preliminar)": "Trazado del túnel (preliminar)",
    "limites_area_estudio":       "Área de estudio: Ibagué, Cajamarca y Calarcá",
}
for nodo in legend.model().rootGroup().findLayers():
    nuevo = RENOMBRES.get(nodo.layer().name())
    if nuevo:
        nodo.setCustomProperty("legend/title-label", nuevo)
        legend.model().refreshLayerLegend(nodo)

_leg_h = 30
legend.attemptMove(QgsLayoutPoint(BAR_X, y_cursor, QgsUnitTypes.LayoutMillimeters))
legend.attemptResize(QgsLayoutSize(CONTENT_W, _leg_h, QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(legend)
y_cursor += _leg_h + 4
print("B) Convenciones (3 entradas) en la barra lateral.")

# ── Barra hipsométrica ───────────────────────────────────────────────────
lbl_hip = QgsLayoutItemLabel(layout)
lbl_hip.setText("Elevación del terreno (msnm)")
fmt_hip = QgsTextFormat()
_fnt_hip = QFont("Arial", 8)
_fnt_hip.setBold(True)
fmt_hip.setFont(_fnt_hip)
fmt_hip.setSize(8)
fmt_hip.setSizeUnit(QgsUnitTypes.RenderPoints)
lbl_hip.setTextFormat(fmt_hip)
lbl_hip.attemptMove(QgsLayoutPoint(BAR_X, y_cursor, QgsUnitTypes.LayoutMillimeters))
lbl_hip.attemptResize(QgsLayoutSize(CONTENT_W, 5, QgsUnitTypes.LayoutMillimeters))
lbl_hip.setHAlign(Qt.AlignLeft)
lbl_hip.setVAlign(Qt.AlignTop)
layout.addLayoutItem(lbl_hip)
y_cursor += 6

HIP_BAR_H = 5
_seg_w = CONTENT_W / len(HIPSO_HEX)
for _i, _hx in enumerate(HIPSO_HEX):
    _rect = QgsLayoutItemShape(layout)
    _rect.setShapeType(QgsLayoutItemShape.Rectangle)
    _rect.attemptMove(QgsLayoutPoint(BAR_X + _i * _seg_w, y_cursor,
                                     QgsUnitTypes.LayoutMillimeters))
    _rect.attemptResize(QgsLayoutSize(_seg_w, HIP_BAR_H,
                                      QgsUnitTypes.LayoutMillimeters))
    _rect.setSymbol(QgsFillSymbol.createSimple(
        {"color": _hx, "outline_style": "no"}))
    layout.addLayoutItem(_rect)
y_cursor += HIP_BAR_H + 1

_TICK_W = 24
for _txt, _frac, _al in [("450", 0.0, Qt.AlignLeft),
                         ("1.650", 0.25, Qt.AlignHCenter),
                         ("2.850", 0.50, Qt.AlignHCenter),
                         ("4.050", 0.75, Qt.AlignHCenter),
                         ("5.250", 1.0, Qt.AlignRight)]:
    _t = QgsLayoutItemLabel(layout)
    _t.setText(_txt)
    _ft = QgsTextFormat()
    _ft.setFont(QFont("Arial", 7))
    _ft.setSize(7)
    _ft.setSizeUnit(QgsUnitTypes.RenderPoints)
    _t.setTextFormat(_ft)
    if _al == Qt.AlignLeft:
        _x = BAR_X
    elif _al == Qt.AlignRight:
        _x = BAR_X + CONTENT_W - _TICK_W
    else:
        _x = BAR_X + _frac * CONTENT_W - _TICK_W / 2
    _t.attemptMove(QgsLayoutPoint(_x, y_cursor, QgsUnitTypes.LayoutMillimeters))
    _t.attemptResize(QgsLayoutSize(_TICK_W, 4, QgsUnitTypes.LayoutMillimeters))
    _t.setHAlign(_al)
    _t.setVAlign(Qt.AlignTop)
    layout.addLayoutItem(_t)
y_cursor += 5

lbl_hnote = QgsLayoutItemLabel(layout)
lbl_hnote.setText("valores fuera de rango se representan con el color del extremo")
fmt_hnote = QgsTextFormat()
_fnt_hn = QFont("Arial", 7)
_fnt_hn.setItalic(True)
fmt_hnote.setFont(_fnt_hn)
fmt_hnote.setSize(7)
fmt_hnote.setSizeUnit(QgsUnitTypes.RenderPoints)
lbl_hnote.setTextFormat(fmt_hnote)
lbl_hnote.attemptMove(QgsLayoutPoint(BAR_X, y_cursor, QgsUnitTypes.LayoutMillimeters))
lbl_hnote.attemptResize(QgsLayoutSize(CONTENT_W, 5, QgsUnitTypes.LayoutMillimeters))
lbl_hnote.setHAlign(Qt.AlignLeft)
lbl_hnote.setVAlign(Qt.AlignTop)
layout.addLayoutItem(lbl_hnote)
y_cursor += 8
print("B) Barra hipsométrica en la barra lateral.")

# ── Barra de escala: 4 segmentos de 5 km (0 a 20 km) ─────────────────────
scalebar = QgsLayoutItemScaleBar(layout)
scalebar.setLinkedMap(map_item)
scalebar.setStyle("Line Ticks Up")
scalebar.setUnits(QgsUnitTypes.DistanceKilometers)
scalebar.setNumberOfSegments(4)
scalebar.setNumberOfSegmentsLeft(0)
scalebar.setUnitsPerSegment(5)  # 5 km por segmento -> 0 a 20 km
scalebar.setUnitLabel("km")
scalebar.attemptMove(QgsLayoutPoint(BAR_X, y_cursor, QgsUnitTypes.LayoutMillimeters))
scalebar.attemptResize(QgsLayoutSize(CONTENT_W, 12, QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(scalebar)
y_cursor += 15
print("B) Barra de escala (0-20 km) en la barra lateral.")

# ── Flecha de norte ─────────────────────────────────────────────────────
north = QgsLayoutItemPicture(layout)
svg_dir = Path(prefix) / "svg" / "arrows"
svg_candidates = ["NorthArrow_02.svg", "NorthArrow_01.svg"]
svg_path = None
for c in svg_candidates:
    p = svg_dir / c
    if p.exists():
        svg_path = str(p)
        break
if svg_path is None:
    for i in range(1, 12):
        p = svg_dir / f"NorthArrow_{i:02d}.svg"
        if p.exists():
            svg_path = str(p)
            break

if svg_path:
    north.setPicturePath(svg_path)
    north.attemptMove(QgsLayoutPoint(BAR_X + CONTENT_W / 2 - 7.5,
                                     y_cursor, QgsUnitTypes.LayoutMillimeters))
    north.attemptResize(QgsLayoutSize(15, 15, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(north)
    y_cursor += 18
    print(f"B) Flecha de norte: {Path(svg_path).name}")
else:
    y_cursor += 4
    print("B) Advertencia: no se encontró SVG de flecha de norte.")

# ── Pie de créditos (encadenado tras la flecha de norte) ─────────────────
fecha_hoy = datetime.now().strftime("%Y-%m-%d")
lbl_credits = QgsLayoutItemLabel(layout)
lbl_credits.setText(
    "Fuente del relieve: Copernicus DEM GLO-30 (ESA/Airbus), EPSG:4326.\n"
    "Portales y trazado: cálculo propio del semillero [CP], script\n"
    f"procesamiento_OE1.py. Fecha de elaboración: {fecha_hoy}."
)
fmt_credits = QgsTextFormat()
fmt_credits.setFont(QFont("Arial", 7))
fmt_credits.setSize(7)
fmt_credits.setSizeUnit(QgsUnitTypes.RenderPoints)
fmt_credits.setColor(QColor(128, 128, 128))
lbl_credits.setTextFormat(fmt_credits)
lbl_credits.attemptMove(QgsLayoutPoint(BAR_X, y_cursor + 3,
                                       QgsUnitTypes.LayoutMillimeters))
lbl_credits.attemptResize(QgsLayoutSize(CONTENT_W, 18, QgsUnitTypes.LayoutMillimeters))
lbl_credits.setHAlign(Qt.AlignLeft)
lbl_credits.setVAlign(Qt.AlignTop)
layout.addLayoutItem(lbl_credits)
print("B) Pie de créditos añadido al final de la barra lateral.")

# ── Registrar layout en el proyecto ─────────────────────────────────────────
manager.addLayout(layout)
print(f"B) Layout «{LAYOUT_NAME}» creado.")

# ═══════════════════════════════════════════════════════════════════════════
# C) Exportar PNG y PDF
# ═══════════════════════════════════════════════════════════════════════════
VIS_DIR.mkdir(parents=True, exist_ok=True)

exporter = QgsLayoutExporter(layout)

# PNG a 300 ppp
png_settings = QgsLayoutExporter.ImageExportSettings()
png_settings.dpi = 300
res_png = exporter.exportToImage(str(OUT_PNG), png_settings)
if res_png == QgsLayoutExporter.Success:
    print(f"C) PNG exportado: {OUT_PNG}")
else:
    print(f"C) ERROR al exportar PNG (código {res_png})")

# PDF vectorial
pdf_settings = QgsLayoutExporter.PdfExportSettings()
pdf_settings.dpi = 300
res_pdf = exporter.exportToPdf(str(OUT_PDF), pdf_settings)
if res_pdf == QgsLayoutExporter.Success:
    print(f"C) PDF exportado: {OUT_PDF}")
else:
    print(f"C) ERROR al exportar PDF (código {res_pdf})")

# ═══════════════════════════════════════════════════════════════════════════
# D) Guardar el proyecto
# ═══════════════════════════════════════════════════════════════════════════
for _n in ("Portales (control)", "Trazado tunel (preliminar)",
           "limites_area_estudio", "DEM elevacion (pseudocolor)",
           "DEM relieve sombreado (hillshade)"):
    if not project.mapLayersByName(_n):
        sys.exit(f"ERROR: la capa «{_n}» perdió su nombre original. "
                 f"NO se guarda el .qgz.")
print("D0) Nombres de capa intactos: verificado.")

if project.write():
    print(f"D) Proyecto guardado: {QGZ_PATH}")
else:
    print("D) ERROR al guardar el proyecto.")

# ═══════════════════════════════════════════════════════════════════════════
# E) Registro en log
# ═══════════════════════════════════════════════════════════════════════════
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
log_lines = [
    f"[{ts} UTC] === layout_OE1.py ===",
    f"[{ts} UTC]   QGIS {QGIS_VER}",
    f"[{ts} UTC]   DEM mín: {dem_min:.2f}  máx: {dem_max:.2f}",
    f"[{ts} UTC]   PNG: {OUT_PNG.resolve()}",
    f"[{ts} UTC]   PDF: {OUT_PDF.resolve()}",
    "",
]
with open(LOG_PATH, "a", encoding="utf-8") as f:
    f.write("\n".join(log_lines))
print(f"E) Registro añadido a {LOG_PATH}")

# ── Resumen final ───────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"  Versión de QGIS: {QGIS_VER}")
print(f"  DEM mín: {dem_min:.2f}   máx: {dem_max:.2f}")
print(f"  PNG: {OUT_PNG.resolve()}")
print(f"  PDF: {OUT_PDF.resolve()}")
print("=" * 60)

# ── limpiar ─────────────────────────────────────────────────────────────────
qgs.exitQgis()
