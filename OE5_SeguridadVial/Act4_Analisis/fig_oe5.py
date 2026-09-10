# -*- coding: utf-8 -*-
"""
Figura del OE 5 - siniestralidad vial.  Semillero GEOPAV - Universidad de Ibague.
Se alimenta de los mismos archivos que la memoria y el libro de calculo, para que
la figura no pueda decir algo distinto de las tablas.

Paleta: azul institucional #193F77 = el dato; gris #94A3B8 = el contexto.
Es un patron de enfasis, no una paleta categorica: el gris es gris a proposito.
Separacion normal-vision entre ambos: dE 34,5 (validador de la guia de dataviz).
El gris queda por debajo de 3:1 contra el fondo, de modo que se rotula
directamente en vez de depender solo del color.
"""
import csv
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

AZUL, GRIS, TINTA, SUAVE = '#193F77', '#94A3B8', '#0F2449', '#5B6B80'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.edgecolor': '#CBD5E1',
                     'axes.labelcolor': TINTA, 'text.color': TINTA,
                     'xtick.color': SUAVE, 'ytick.color': SUAVE})
mil = FuncFormatter(lambda v, p: f'{v:,.0f}'.replace(',', '.'))

def leer(ruta, num):
    with open(ruta, encoding='utf-8-sig') as f:
        filas = list(csv.DictReader(f, delimiter=';'))
    for r in filas:
        for k in num:
            r[k] = float(r[k]) if '.' in r[k] else int(r[k])
    return filas

# Los dos CSV los produce descarga_datos_OE5.py; la figura no vuelve a filtrar nada.
BASE = os.path.dirname(os.path.abspath(__file__))
OE5 = os.path.dirname(BASE)
ACT1 = os.path.join(OE5, 'Act1_Aforos')
ACT3 = os.path.join(OE5, 'Act3_Siniestros')
VIS = os.path.join(OE5, 'Visuales')

aforos = leer(os.path.join(ACT1, 'aforos_cocora_mensual.csv'), ['dias','total','livianos','buses','pesados','otros','tpd','tpd_pes'])
sin    = leer(os.path.join(ACT3, 'siniestros_ANSV_corredor.csv'), ['fallecidos'])

fig = plt.figure(figsize=(13.5, 5.9), dpi=200)
fig.patch.set_facecolor('white')
# wspace amplio: los rotulos numerados del panel derecho son largos y sin holgura
# invaden el area de trazado del panel izquierdo.
gs = fig.add_gridspec(1, 2, width_ratios=[1.26, 1], wspace=0.40,
                      left=0.055, right=0.975, top=0.78, bottom=0.24)

# ---------------- A: exposicion ----------------
ax = fig.add_subplot(gs[0, 0]); ax.set_facecolor('white')
x = list(range(len(aforos)))
tot = [a['tpd'] for a in aforos]; pes = [a['tpd_pes'] for a in aforos]
ax.plot(x, tot, color=GRIS, lw=2, solid_capstyle='round')
ax.plot(x, pes, color=AZUL, lw=2, solid_capstyle='round')
ax.annotate('Todos los vehículos', xy=(x[-1], tot[-1]), xytext=(-6, 30),
            textcoords='offset points', ha='right', fontsize=9.5, color=SUAVE, weight='bold')
ax.annotate('Carga pesada', xy=(x[-1], pes[-1]), xytext=(-6, 26),
            textcoords='offset points', ha='right', fontsize=9.5, color=AZUL, weight='bold')
for xi, yi, c in [(x[-1], tot[-1], GRIS), (x[-1], pes[-1], AZUL)]:
    ax.plot([xi], [yi], 'o', ms=6, color=c, mec='white', mew=2, zorder=5)
u = aforos[-12:]
m_tot = sum(a['total'] for a in u) / sum(a['dias'] for a in u)
m_pes = sum(a['pesados'] for a in u) / sum(a['dias'] for a in u)
for m, c, t in [(m_tot, GRIS, f'media 12 meses  {m_tot:,.0f}'.replace(',', '.')),
                (m_pes, AZUL, f'media 12 meses  {m_pes:,.0f}'.replace(',', '.'))]:
    ax.axhline(m, color=c, lw=1, ls=(0, (4, 4)), alpha=.85, zorder=1)
    ax.text(0.4, m + 90, t, fontsize=8.5, color=c, weight='bold')
et = [(i, a['mes']) for i, a in enumerate(aforos) if a['mes'].endswith('-01')]
ax.set_xticks([i for i, _ in et]); ax.set_xticklabels([m[:4] for _, m in et], fontsize=9)
ax.set_ylim(0, max(tot) * 1.18); ax.yaxis.set_major_formatter(mil)
ax.set_ylabel('Tránsito promedio diario (veh/día)', fontsize=10)
ax.grid(axis='y', color='#EEF2F7', lw=1); ax.set_axisbelow(True)
for s in ('top', 'right'): ax.spines[s].set_visible(False)
ax.set_title('Exposición medida en el peaje Cocora', fontsize=12.5, weight='bold',
             color=TINTA, loc='left', pad=30)
ax.text(0, 1.035, 'Vía Ibagué – Cajamarca, RN40-03, km 13+800 · ANI, oct 2021 – may 2026',
        transform=ax.transAxes, fontsize=9, color=SUAVE)

# ---------------- B: sectores criticos ----------------
ax2 = fig.add_subplot(gs[0, 1]); ax2.set_facecolor('white')
sec = sorted(sin, key=lambda r: r['fallecidos'])
# Dos pares de sectores comparten PR (10 y 10, 85 y 85): son puntos distintos con el
# mismo punto de referencia entero, de modo que el rotulo se numera para no repetirse.
et2 = [f"Sector {len(sec)-i}  ·  {'Paso' if r['en_el_paso']=='Si' else 'Fuera'}  ·  PR {r['pr'] or 'sd'}"
       for i, r in enumerate(sec)]
val = [r['fallecidos'] for r in sec]
col = [AZUL if r['en_el_paso'] == 'Si' else GRIS for r in sec]
y = list(range(len(sec)))
ax2.barh(y, val, color=col, height=0.62)
for yi, v in zip(y, val):
    ax2.text(v + 0.45, yi, str(v), va='center', fontsize=10, weight='bold', color=TINTA)
ax2.set_yticks(y); ax2.set_yticklabels(et2, fontsize=9.5)
ax2.set_xlim(0, max(val) * 1.22)
ax2.set_xlabel('Fallecidos acumulados 2015 – 2019', fontsize=10, labelpad=8)
ax2.grid(axis='x', color='#EEF2F7', lw=1); ax2.set_axisbelow(True)
for s in ('top', 'right', 'left'): ax2.spines[s].set_visible(False)
ax2.tick_params(axis='y', length=0)
ax2.set_title('Sectores críticos del corredor Ibagué – Armenia', fontsize=12.5,
              weight='bold', color=TINTA, loc='left', pad=30)
ax2.text(0, 1.035, 'ANSV · los seis están en jurisdicción de Calarcá (Quindío)',
         transform=ax2.transAxes, fontsize=9, color=SUAVE)

fig.suptitle('Objetivo específico 5 · Línea base de siniestralidad y exposición del corredor',
             fontsize=14.5, weight='bold', color=TINTA, x=0.055, ha='left', y=0.955)
fig.text(0.055, 0.018,
         'Fuentes: ANSV, conjunto rs3u-8r4q (fallecidos 2015–2019, marca F) · ANI, conjunto 8yi9-t44c '
         '(aforo del peaje Cocora, marca F). El tránsito promedio diario es cálculo propio [CP]:\n'
         'total mensual dividido entre los días del mes. La serie mensual es volátil, de modo que el análisis usa la media de los últimos doce meses.\n'
         'Las dos series están en la misma unidad y comparten un solo eje. Semillero GEOPAV · Universidad de Ibagué · Paz y Región 2026B.',
         fontsize=8, color=SUAVE, va='bottom')
fig.savefig(os.path.join(VIS, 'siniestralidad_OE5.png'), facecolor='white')
fig.savefig(os.path.join(VIS, 'siniestralidad_OE5.pdf'), facecolor='white')
print('figura escrita')
