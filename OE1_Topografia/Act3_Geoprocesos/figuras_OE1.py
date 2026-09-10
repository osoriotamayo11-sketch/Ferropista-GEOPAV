# -*- coding: utf-8 -*-
"""
OE 1 — Generación de las figuras del análisis topográfico
Semillero de Investigación GEOPAV · Universidad de Ibagué · Paz y Región 2026B
Responsable: Tamayo Osorio Miguel Ángel

Produce las tres figuras del objetivo específico 1:
  1. perfil_longitudinal.png / .pdf   — perfil del terreno y rasante del túnel
  2. cobertura_tunel.png  / .pdf      — cobertura y distribución por rangos
  3. mapa_trazado.png     / .pdf      — relieve sombreado con el trazado

REQUISITO: ejecutar antes  procesamiento_OE1.py  (descarga el DEM y crea el mosaico).

Ejecutar:  python figuras_OE1.py

PALETA — no es decorativa, sigue reglas de accesibilidad:
  Azul #2a78d6 : el dato (la rasante, el trazado). Es el acento.
  Gris #898781 : el contexto (el terreno). Es deliberadamente sin color.
  Rampa azul de 5 pasos claro->oscuro para la cobertura: es una escala de
  MAGNITUD, por eso un solo tono. Nunca un arcoíris.
"""
import numpy as np, json, io, os, sys, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.colors import LightSource, LinearSegmentedColormap
from matplotlib.patches import Patch, PathPatch
from matplotlib.path import Path as MplPath
import rasterio
from rasterio.windows import from_bounds

INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#898781', '#e1e0d9'
ACC, ACC_L, TIERRA = '#2a78d6', '#cde2fb', '#d9d5cb'
SURF = '#fcfcfb'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9})
PIE_FUENTE = ('Fuente del terreno: Copernicus DEM GLO-30 (ESA/Airbus), ~30 m. '
              'Cotas de portal según Fernández O. (2025), diapositiva 20.')

# Salida SIEMPRE en OE1_Topografia/Visuales/, sin importar desde dónde se lance
# el intérprete. Los PDF se escriben con CreationDate nulo para que dos corridas
# den el mismo byte (matplotlib mete la hora de la corrida por defecto).
RAIZ_FIG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D_VIS    = os.path.join(RAIZ_FIG, 'Visuales')
os.makedirs(D_VIS, exist_ok=True)

def _guardar(fig, nombre):
    for e in ('png', 'pdf'):
        kw = {'metadata': {'CreationDate': None}} if e == 'pdf' else {}
        fig.savefig(os.path.join(D_VIS, f'{nombre}.{e}'), facecolor=SURF, **kw)

def _num(v, dec=0):
    """Formato es-CO: punto de miles, coma decimal (constitución del proyecto)."""
    s = f'{v:,.{dec}f}'                 # estilo en-US: 2,031.4
    return s.replace(',', '\x00').replace('.', ',').replace('\x00', '.')

def marco(ax, ejes_y=True):
    ax.set_facecolor(SURF)
    if ejes_y: ax.grid(axis='y', color=GRID, lw=.7); ax.set_axisbelow(True)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    for s in ('bottom', 'left'): ax.spines[s].set_color('#c3c2b7')
    ax.tick_params(colors=MUTED, labelsize=8.5, length=0)

def fig1_perfil(pkk, ter, ras, pend, cif):
    fig, ax = plt.subplots(figsize=(13.5, 5.6), dpi=200); fig.patch.set_facecolor(SURF)
    BASE = 400
    ax.fill_between(pkk, ras, ter, where=(ter > ras), color=ACC_L, alpha=.55, lw=0, zorder=2)
    ax.fill_between(pkk, BASE, ter, color=TIERRA, lw=0, zorder=1)
    ax.plot(pkk, ter, color=MUTED, lw=1.1, zorder=3, label='Perfil del terreno (Copernicus DEM GLO-30)')
    ax.plot(pkk, ras, color=ACC, lw=2.0, zorder=5,
            label=f'Rasante del túnel de base — {pend:.3f} %'.replace('.', ','))
    i = int((ter - ras).argmax())
    ax.plot([pkk[i]]*2, [ras[i], ter[i]], color=ACC, lw=1.0, ls=(0, (4, 3)), zorder=6)
    ax.annotate(f'Cobertura máxima  {_num(ter[i]-ras[i])} m\nPK {_num(pkk[i], 1)}  ·  terreno {_num(ter[i])} msnm',
        xy=(pkk[i], (ras[i]+ter[i])/2), xytext=(13.5, 3320), color=INK, fontsize=8.5,
        fontweight='bold', ha='left', va='center', linespacing=1.5,
        arrowprops=dict(arrowstyle='-', color=ACC, lw=.9, alpha=.8,
                        connectionstyle='angle,angleA=0,angleB=90,rad=6', shrinkA=6, shrinkB=4), zorder=7)
    # El extremo del corredor lo nombra la ponencia (Ibagué / Armenia) [F, dia. 20];
    # el municipio donde cae el portal lo determina el paso 6 contra el IGAC [CP].
    # El portal occidental está en Calarcá, no en Armenia.
    def _cota(v): return f'{v:,.0f}'.replace(',', '.') + ' msnm'
    _uo, _uw = cif['portal_oriental_ubicacion'], cif['portal_occidental_ubicacion']
    for x, y, lab, ha, dx in [
            (pkk[0],  ras[0],  f"PORTAL ORIENTAL\nextremo Ibagué · {_uo['municipio']}, {_uo['depto']}\n{_cota(ras[0])}", 'left', 1.4),
            (pkk[-1], ras[-1], f"PORTAL OCCIDENTAL\nextremo Armenia · {_uw['municipio']}, {_uw['depto']}\n{_cota(ras[-1])}", 'right', -1.4)]:
        ax.plot([x], [y], 'o', ms=7.5, mfc=SURF, mec=ACC, mew=2.2, zorder=8)
        ax.annotate(lab, xy=(x+dx, 640), color=INK, fontsize=8.2, fontweight='bold',
                    ha=ha, va='center', linespacing=1.6, zorder=8)
    ax.set_xlim(-1.8, pkk[-1]+2); ax.set_ylim(BASE, 3900)
    ax.set_xlabel('Abscisa desde el portal oriental  (km)', color=INK2, labelpad=8)
    ax.set_ylabel('Cota  (msnm)', color=INK2, labelpad=7)
    ax.xaxis.set_major_locator(MultipleLocator(5)); ax.yaxis.set_major_locator(MultipleLocator(500))
    marco(ax)
    ax.legend(loc='upper left', frameon=False, fontsize=8.5, handlelength=1.9,
              bbox_to_anchor=(0.004, 0.995), labelcolor=INK2)
    fig.suptitle('Perfil longitudinal del túnel de base — tramo Ibagué – Armenia',
                 x=.008, y=.982, ha='left', fontsize=13.5, fontweight='bold', color=INK)
    fig.text(.008, .932, 'Semillero GEOPAV · Paz y Región 2026B · Objetivo específico 1 — cálculo propio [CP]',
             ha='left', fontsize=8.5, color=MUTED)
    _lon = f'{pkk[-1]:.2f}'.replace('.', ',')
    _pen = f'{pend:.3f}'.replace('.', ',')
    fig.text(.008, .015, f'Alineamiento recto entre portales · longitud {_lon} km · '
             f'pendiente {_pen} % (criterio adoptado < 1,5 %)\n{PIE_FUENTE}',
             ha='left', fontsize=7.5, color=MUTED, linespacing=1.6)
    fig.subplots_adjust(left=.052, right=.988, top=.87, bottom=.175)
    _guardar(fig, 'perfil_longitudinal')
    plt.close(fig); print('  figura 1: perfil_longitudinal')

def fig2_cobertura(pkk, cob, L):
    STEPS = ['#cde2fb', '#9ec5f4', '#5598e7', '#2a78d6', '#184f95']
    RANGOS = [(0, 100), (100, 300), (300, 700), (700, 1200), (1200, 1e9)]
    ETIQ = ['0 – 100 m', '100 – 300 m', '300 – 700 m', '700 – 1.200 m', '> 1.200 m']
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(13.5, 6.9), dpi=200,
                                  gridspec_kw={'height_ratios': [2.15, 1], 'hspace': .42})
    fig.patch.set_facecolor(SURF)
    for (lo, hi), col in zip(RANGOS, STEPS):
        ax.fill_between(pkk, 0, cob, where=(cob >= lo) & (cob < hi), color=col, lw=0)
    ax.plot(pkk, cob, color='#184f95', lw=.8, alpha=.55)
    i = int(cob.argmax())
    ax.plot([pkk[i]], [cob[i]], 'o', ms=7, mfc=SURF, mec='#184f95', mew=2, zorder=5)
    ax.annotate(f'{_num(cob[i])} m · PK {_num(pkk[i], 1)}',
                xy=(pkk[i], cob[i]), xytext=(pkk[i]-2.2, cob[i]+140),
                ha='right', fontsize=8.5, fontweight='bold', color=INK)
    ax.axhline(cob.mean(), color=MUTED, lw=1, ls=(0, (5, 4)))
    ax.annotate(f'media {cob.mean():.0f} m', xy=(1.0, cob.mean()+60), ha='left', fontsize=8, color=INK2)
    ax.set_ylabel('Cobertura sobre la clave  (m)', color=INK2, labelpad=7)
    ax.set_xlabel('Abscisa desde el portal oriental  (km)', color=INK2, labelpad=6)
    ax.set_xlim(0, pkk[-1]); ax.set_ylim(0, cob.max()*1.16)
    ax.xaxis.set_major_locator(MultipleLocator(5)); ax.yaxis.set_major_locator(MultipleLocator(500))
    marco(ax)
    ax.legend(handles=[Patch(facecolor=c, label=e) for c, e in zip(STEPS, ETIQ)],
              loc='upper left', frameon=False, fontsize=8.2, ncol=5, handlelength=1.5,
              columnspacing=1.4, labelcolor=INK2, bbox_to_anchor=(0, 1.13))
    x = 0; segs = []
    for (lo, hi), col in zip(RANGOS, STEPS):
        m = (cob >= lo) & (cob < hi); km = m.mean()*L
        ax2.barh(0, km, left=x, height=.52, color=col, edgecolor=SURF, lw=2)
        txt = f'{km:.1f} km\n{100*m.mean():.0f} %'.replace('.', ',', 1)
        t = ax2.annotate(txt, xy=(x+km/2, 0), ha='center', va='center', fontsize=8.2,
            fontweight='bold', linespacing=1.35,
            color='#ffffff' if col in ('#2a78d6', '#184f95') else INK)
        segs.append((t, x, km, txt))
        x += km
    # Todos los rangos se rotulan siempre. El criterio de dónde va la etiqueta no
    # es un umbral fijo en km: se mide el ancho real del texto ya compuesto contra
    # el ancho del segmento en píxeles. Si no cabe holgadamente, la etiqueta sale
    # DEBAJO de la barra, en color INK y con una línea que apunta a su segmento.
    fig.canvas.draw()
    for t, x0, km, txt in segs:
        p0 = ax2.transData.transform((x0, 0))[0]
        p1 = ax2.transData.transform((x0 + km, 0))[0]
        if t.get_window_extent().width <= (p1 - p0) * 0.78:
            continue
        cx = x0 + km / 2
        t.remove()
        ax2.annotate(txt, xy=(cx, -.26), xytext=(cx, -.52), ha='center', va='top',
            fontsize=8.2, fontweight='bold', linespacing=1.35, color=INK, annotation_clip=False,
            arrowprops=dict(arrowstyle='-', color=INK, lw=.8, shrinkA=1, shrinkB=1))
    ax2.set_xlim(0, L); ax2.set_ylim(-.95, .5); ax2.set_yticks([]); ax2.set_facecolor(SURF)
    ax2.set_xlabel('Longitud del trazado  (km)', color=INK2, labelpad=6)
    ax2.xaxis.set_major_locator(MultipleLocator(5))
    for s in ('top', 'right', 'left'): ax2.spines[s].set_visible(False)
    ax2.spines['bottom'].set_color('#c3c2b7'); ax2.tick_params(colors=MUTED, labelsize=8.5, length=0)
    ax2.set_title('Distribución de la longitud del túnel por rango de cobertura',
                  loc='left', fontsize=9.5, fontweight='bold', color=INK, pad=9)
    fig.suptitle('Cobertura del túnel de base — insumo para la selección del método de excavación',
                 x=.008, y=.982, ha='left', fontsize=13.5, fontweight='bold', color=INK)
    fig.text(.008, .935, 'Semillero GEOPAV · Paz y Región 2026B · Objetivo específico 1 — cálculo propio [CP] · alimenta el OE 4',
             ha='left', fontsize=8.5, color=MUTED)
    fig.text(.008, .014, 'Cobertura = cota del terreno − cota de la rasante, sobre 1.500 puntos del alineamiento.\n'
             'Los rangos son una clasificación propia del semillero, no una norma.',
             ha='left', fontsize=7.4, color=MUTED, linespacing=1.6)
    fig.subplots_adjust(left=.055, right=.985, top=.845, bottom=.115)
    _guardar(fig, 'cobertura_tunel')
    plt.close(fig); print('  figura 2: cobertura_tunel')

def fig3_mapa(PE, PW, cob):
    W, S, E, N = -75.76, 4.30, -75.10, 4.60
    with rasterio.open('dem_corredor.tif') as src:
        win = from_bounds(W, S, E, N, src.transform)
        dem = src.read(1, window=win).astype('float64'); tr = src.window_transform(win)
    # Rampa hipsométrica que NO termina en blanco: la cordillera alta (3.000 a
    # 3.900 msnm) es justamente la masa de roca sobre el túnel, y en blanco se
    # leía como vacío. El extremo alto conserva color y oscurece con la cota.
    cmap = LinearSegmentedColormap.from_list('hipso',
        ['#2e6b45', '#5b8f4e', '#98ac5c', '#c9b97e', '#c2a184', '#a2705d', '#7d4b52', '#513349'])
    ls = LightSource(azdeg=315, altdeg=45)
    dx = abs(tr.a)*111320*np.cos(np.deg2rad(4.45)); dy = abs(tr.e)*110540
    rgb = ls.shade(dem, cmap=cmap, blend_mode='soft', vert_exag=2.2, dx=dx, dy=dy, vmin=500, vmax=3900)
    fig, ax = plt.subplots(figsize=(13.5, 6.6), dpi=200); fig.patch.set_facecolor(SURF)
    ax.imshow(rgb, extent=[W, E, S, N], origin='upper', interpolation='bilinear')

    # --- máscara de área de estudio -----------------------------------------
    # El relieve se pinta a todo color dentro de los municipios que cruza el
    # trazado y desaturado fuera de ellos. No se recorta el ráster: se conserva
    # el contexto de la cordillera. Límites: IGAC, capa de municipios.
    _D1 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Act1_DEM')
    def _geo(n):
        r = os.path.join(_D1, n)
        return json.load(io.open(r, encoding='utf-8')) if os.path.exists(r) else None
    def _anillos(geom):
        if geom['type'] == 'Polygon': return [geom['coordinates']]
        if geom['type'] == 'MultiPolygon': return geom['coordinates']
        return []

    _est = _geo('limites_area_estudio.geojson')
    if _est:
        from rasterio.features import rasterize
        dentro = rasterize([(f['geometry'], 1) for f in _est['features']],
                           out_shape=dem.shape, transform=tr, fill=0,
                           dtype='uint8', all_touched=True).astype(bool)
        gris = rgb[..., :3] @ np.array([.2126, .7152, .0722])      # luminancia
        fuera = np.dstack([gris]*3) * .34 + .66                    # gris muy claro
        rgb = np.where(dentro[..., None], rgb[..., :3], fuera)
        ax.imshow(rgb, extent=[W, E, S, N], origin='upper', interpolation='bilinear', zorder=1.5)

    _ctx = _geo('limites_contexto.geojson')
    if _ctx:
        for f in _ctx['features']:
            for poly in _anillos(f['geometry']):
                for anillo in poly:
                    a = np.array(anillo)
                    ax.plot(a[:, 0], a[:, 1], color='#b0aea2', lw=.6, zorder=2.6)
    if _est:
        for f in _est['features']:
            for poly in _anillos(f['geometry']):
                for anillo in poly:
                    a = np.array(anillo)
                    ax.plot(a[:, 0], a[:, 1], color='#ffffff', lw=3.0, zorder=2.8, alpha=.85)
                    ax.plot(a[:, 0], a[:, 1], color='#3d3b34', lw=1.35, zorder=3)

    lx, ly = [PE[1], PW[1]], [PE[0], PW[0]]
    ax.plot(lx, ly, color='#ffffff', lw=5.0, solid_capstyle='round', zorder=4, alpha=.85)
    ax.plot(lx, ly, color=ACC, lw=2.6, solid_capstyle='round', zorder=5,
            label='Trazado preliminar del túnel de base')
    def _msnm(v):                      # separador de miles es-CO, sin tocar otras comas
        return f'{v:,.0f}'.replace(',', '.') + ' msnm'
    for x, y, lab, ha, off in [(PE[1], PE[0], 'Portal oriental\nIbagué, Tolima\n' + _msnm(PE[2]), 'left', .012),
                               (PW[1], PW[0], 'Portal occidental\nCalarcá, Quindío\n' + _msnm(PW[2]), 'right', -.012)]:
        ax.plot([x], [y], 'o', ms=10, mfc='#ffffff', mec=ACC, mew=2.8, zorder=7)
        ax.annotate(lab, xy=(x+off, y-.030), ha=ha, va='top', fontsize=8.4, fontweight='bold',
            color=INK, zorder=8, linespacing=1.45,
            bbox=dict(boxstyle='round,pad=0.32', fc='#ffffff', ec='none', alpha=.88))
    for lo, la, n in [(-75.30, 4.545, 'IBAGUÉ'), (-75.48, 4.345, 'CAJAMARCA'), (-75.63, 4.505, 'CALARCÁ')]:
        ax.annotate(n, xy=(lo, la), ha='center', fontsize=9.2, color='#3d3b34',
                    fontweight='bold', zorder=3.4, alpha=.75)
    for lo, la, n in [(-75.2322, 4.4389, 'Ibagué'), (-75.4275, 4.4267, 'Cajamarca'),
                      (-75.6497, 4.5222, 'Calarcá'), (-75.6811, 4.5339, 'Armenia')]:
        ax.plot([lo], [la], 's', ms=5, mfc='#1a1a19', mec='#ffffff', mew=1.1, zorder=6)
        ax.annotate(n, xy=(lo, la+.015), ha='center', fontsize=8.2, color=INK, fontweight='bold',
            zorder=7, bbox=dict(boxstyle='round,pad=0.22', fc='#ffffff', ec='none', alpha=.82))
    i = int(cob.argmax()); fr = i/(len(cob)-1)
    mx, my = lx[0]+(lx[1]-lx[0])*fr, ly[0]+(ly[1]-ly[0])*fr
    ax.plot([mx], [my], '^', ms=9, mfc='#eda100', mec='#ffffff', mew=1.4, zorder=7)
    ax.annotate(f'Cobertura máxima\n{cob.max():,.0f} m'.replace(',', '.'), xy=(mx, my), xytext=(mx-.005, my+.062),
        ha='center', fontsize=8, fontweight='bold', color=INK, zorder=8, linespacing=1.4,
        arrowprops=dict(arrowstyle='-', color='#eda100', lw=1.2, shrinkB=2),
        bbox=dict(boxstyle='round,pad=0.28', fc='#ffffff', ec='none', alpha=.88))
    x0, y0 = W+.035, S+.022; km10 = 10000/(111320*np.cos(np.deg2rad(4.45)))
    ax.plot([x0, x0+km10], [y0]*2, color=INK, lw=3.2, solid_capstyle='butt', zorder=9)
    ax.plot([x0, x0+km10/2], [y0]*2, color='#ffffff', lw=3.2, solid_capstyle='butt', zorder=10)
    for xx, lb in [(x0, '0'), (x0+km10/2, '5'), (x0+km10, '10 km')]:
        ax.annotate(lb, xy=(xx, y0+.009), ha='center', fontsize=7.4, color=INK, fontweight='bold', zorder=10)
    ax.annotate('N', xy=(E-.030, N-.048), ha='center', fontsize=11, fontweight='bold', color=INK, zorder=10)
    ax.annotate('▲', xy=(E-.030, N-.032), ha='center', fontsize=10, color=INK, zorder=10)
    ax.set_xlim(W, E); ax.set_ylim(S, N); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_edgecolor('#c3c2b7'); s.set_linewidth(.8)
    from matplotlib.lines import Line2D
    _h = [Line2D([], [], color=ACC, lw=2.6, label='Trazado preliminar del túnel de base'),
          Line2D([], [], color='#4a4840', lw=1.15, label='Municipios del área de estudio'),
          Line2D([], [], color='#b9b7ab', lw=.55, label='Límite municipal (contexto)')]
    ax.legend(handles=_h, loc='upper left', frameon=True, facecolor='#ffffff', edgecolor='none',
              framealpha=.9, fontsize=8.0, handlelength=2.2, labelcolor=INK2)
    cax = fig.add_axes([.845, .16, .016, .30])
    cax.imshow(np.linspace(3900, 500, 256).reshape(-1, 1), aspect='auto', cmap=cmap, extent=[0, 1, 500, 3900])
    cax.set_xticks([]); cax.yaxis.tick_right(); cax.set_yticks([500, 1500, 2500, 3500])
    cax.tick_params(labelsize=7.2, colors=MUTED, length=0)
    cax.set_title('msnm', fontsize=7.2, color=MUTED, pad=5)
    for s in cax.spines.values(): s.set_edgecolor('#c3c2b7'); s.set_linewidth(.6)
    fig.suptitle('Trazado preliminar del túnel de base — corredor Ibagué – Armenia',
                 x=.008, y=.978, ha='left', fontsize=13.5, fontweight='bold', color=INK)
    fig.text(.008, .928, 'Semillero GEOPAV · Paz y Región 2026B · Objetivo específico 1 — cálculo propio [CP]',
             ha='left', fontsize=8.5, color=MUTED)
    fig.text(.008, .018, 'Relieve sombreado: Copernicus DEM GLO-30 (ESA/Airbus), ~30 m, EPSG:4326 · '
             'exageración vertical 2,2× · iluminación 315°/45° · Límites municipales: IGAC, capa de municipios [F]\n'
             'Área de estudio: los tres municipios que cruza el trazado — Ibagué 39,2 %, Cajamarca 42,7 %, Calarcá 18,1 % [CP]\n' + PIE_FUENTE,
             ha='left', fontsize=7.4, color=MUTED, linespacing=1.6)
    fig.subplots_adjust(left=.012, right=.83, top=.90, bottom=.125)
    _guardar(fig, 'mapa_trazado')
    plt.close(fig); print('  figura 3: mapa_trazado')

if __name__ == '__main__':
    print('Generando figuras del OE 1...')
    # Las cifras NO se recalculan aquí: se leen de los productos de procesamiento_OE1.py.
    # Un script produce los datos y otro los consume; así las figuras no pueden
    # discrepar de la cartera, la memoria ni el sitio web.
    import csv, os
    # Selector opcional de figuras por línea de comandos, sin librerías nuevas:
    #   python figuras_OE1.py        -> las tres
    #   python figuras_OE1.py 1 2    -> solo perfil y cobertura
    sel = {int(a) for a in sys.argv[1:] if a.isdigit()} or {1, 2, 3}
    RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cif = json.load(io.open(os.path.join(RAIZ, 'cifras_OE1.json'), encoding='utf-8'))
    filas = list(csv.DictReader(io.open(os.path.join(RAIZ, 'Act5_Perfil',
                 'perfil_continuo.csv'), encoding='utf-8-sig')))
    PE = (cif['portal_oriental']['lat'], cif['portal_oriental']['lon'],
          cif['portal_oriental']['cota_msnm'])
    PW = (cif['portal_occidental']['lat'], cif['portal_occidental']['lon'],
          cif['portal_occidental']['cota_msnm'])
    L, pend = cif['longitud_m'], cif['pendiente_pct']
    pkk = np.array([float(f['PK_m']) for f in filas])/1000
    ter = np.array([float(f['Cota_terreno_msnm']) for f in filas])
    ras = np.array([float(f['Cota_rasante_msnm']) for f in filas])
    cob = ter - ras
    if 1 in sel: fig1_perfil(pkk, ter, ras, pend, cif)
    if 2 in sel: fig2_cobertura(pkk, cob, L/1000)
    if 3 in sel: fig3_mapa(PE, PW, cob)
    print(f'Listo. {len(sel)} figura(s) en PNG y PDF.')
