# -*- coding: utf-8 -*-
"""
OE 5 - Diagnostico de seguridad vial del corredor Ibague - Armenia.
Descarga y filtrado de las dos series que alimentan la memoria metodologica,
el libro de calculo y la figura.  Ejecutar con:  python descarga_datos_OE5.py

Semillero de Investigacion GMAE - Universidad de Ibague - Paz y Region 2026B.

Fuentes (marca F):
  ANSV  - Sectores Criticos de Siniestralidad Vial   datos.gov.co  rs3u-8r4q
  ANI   - Trafico Vehicular                          datos.gov.co  8yi9-t44c

El filtro del corredor es GEOGRAFICO y esta escrito aqui una sola vez, para que
la memoria, el Excel y la figura no puedan discrepar entre si.
"""
import csv, json, urllib.request, calendar, os

BASE = 'https://www.datos.gov.co/resource'
# Ventana del corredor Ibague - Armenia, entre los portales del OE 1.
LON_MIN, LON_MAX = -75.72, -75.19
LAT_MIN, LAT_MAX = 4.25, 4.65
# Categorias tarifarias de la ANI agrupadas por tipo de vehiculo.
PESADOS = {'III', 'IV', 'V', 'IIIE'}
LIVIANOS = {'I', 'IE'}
BUSES = {'II', 'IIE'}


def traer(recurso, params):
    url = f'{BASE}/{recurso}.json?' + '&'.join(f'{k}={v}' for k, v in params.items())
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))


def paso1_siniestros():
    """Fallecidos por sector critico dentro del corredor de analisis."""
    filas = []
    for depto in ('QUIND%C3%8DO', 'TOLIMA', 'RISARALDA'):
        filas += traer('rs3u-8r4q', {'departamento': depto, '$limit': 1000})
    sel = [r for r in filas
           if LON_MIN <= float(r['longitud']) <= LON_MAX
           and LAT_MIN <= float(r['latitud']) <= LAT_MAX]
    sel.sort(key=lambda r: -int(r['fallecidos']))
    cols = ['departamento', 'municipio', 'entidad', 'tramo', 'pr',
            'fallecidos', 'latitud', 'longitud', 'gizscore', 'gipvalue']
    with open('siniestros_ANSV_corredor.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(cols + ['en_el_paso'])
        for r in sel:
            w.writerow([r.get(c, '') for c in cols] +
                       ['Si' if (r.get('tramo') or '') == 'Calarcá - Ibagué' else 'No'])
    total = sum(int(r['fallecidos']) for r in sel)
    paso = sum(int(r['fallecidos']) for r in sel if (r.get('tramo') or '') == 'Calarcá - Ibagué')
    print(f'[1] siniestros: {len(sel)} sectores | {total} fallecidos en el corredor | {paso} en el paso')
    return sel


def paso2_aforos():
    """Aforo mensual del peaje Cocora, agrupado por tipo de vehiculo."""
    filas = traer('8yi9-t44c', {'peaje': 'COCORA', '$limit': 5000})
    mes = {}
    for r in filas:
        m = r['desde'][:7]
        c = r['categoriatarifa']
        g = ('pesados' if c in PESADOS else
             'livianos' if c in LIVIANOS else
             'buses' if c in BUSES else 'otros')
        d = mes.setdefault(m, {'livianos': 0, 'buses': 0, 'pesados': 0, 'otros': 0})
        d[g] += int(r['cantidadtrafico'])
    salida = []
    for m in sorted(mes):
        y, mm = int(m[:4]), int(m[5:7])
        dias = calendar.monthrange(y, mm)[1]
        d = mes[m]
        total = sum(d.values())
        salida.append({'mes': m, 'dias': dias, 'total': total, **d,
                       'tpd': round(total / dias, 1),
                       'tpd_pes': round(d['pesados'] / dias, 1)})
    with open('aforos_cocora_mensual.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=list(salida[0]), delimiter=';')
        w.writeheader(); w.writerows(salida)
    u = salida[-12:]
    T = sum(r['total'] for r in u); P = sum(r['pesados'] for r in u); D = sum(r['dias'] for r in u)
    print(f'[2] aforos: {len(salida)} meses | ultimos 12: TPD {T/D:,.0f} | pesados {P/D:,.0f} '
          f'({100*P/T:.1f} %)'.replace(',', '.'))
    return salida


def paso3_tasa(sel, aforos, longitud_km=60.0, tpd_historico=3000.0, anios=5):
    """Tasa por exposicion. Los dos ultimos argumentos son HIPOTESIS (marca H)."""
    f = sum(int(r['fallecidos']) for r in sel if (r.get('tramo') or '') == 'Calarcá - Ibagué')
    vehkm = tpd_historico * 365 * longitud_km * anios
    tasa = f / vehkm * 1e8
    print(f'[3] tasa = {tasa:.1f} fallecidos por 100 millones de veh-km '
          f'(HIPOTESIS: L={longitud_km:g} km, TPD={tpd_historico:g})')
    print('    ADVERTENCIA: los fallecidos son 2015-2019 y el aforo verificado es 2021-2026.')
    print('    El Tunel de La Linea abrio el 4 de septiembre de 2020. No son divisibles entre si.')
    return tasa


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')
    s = paso1_siniestros()
    a = paso2_aforos()
    paso3_tasa(s, a)
    print('\nArchivos escritos: siniestros_ANSV_corredor.csv, aforos_cocora_mensual.csv')
