'use client';

/**
 * GraficosOE5 — la exposición medida y la serie histórica de tránsito del
 * objetivo específico 5, dibujadas en el navegador a partir de
 * `src/data/siniestralidad_oe5.json`.
 *
 * Sustituyen a los paneles de serie temporal de las láminas PNG que antes
 * ocupaban su lugar. Las láminas siguen existiendo: son el entregable subido
 * a Drive y quedan enlazadas para descarga bajo cada gráfico.
 *
 * MÉTODO DECLARADO — leer antes de tocar las cifras rotuladas:
 * la media de doce meses del peaje Cocora es una media PONDERADA POR DÍAS
 * (total de vehículos de los últimos doce meses ÷ días de esos meses = 365),
 * no el promedio de los TPD mensuales. Las dos difieren: ponderada da 4.954
 * y el promedio simple daría 4.945. La cifra que publica el sitio en
 * `SEGURIDAD_VIAL.mediciones` es la ponderada, y es la que se rotula aquí.
 * Por eso el valor se lee de `resumen`, nunca se recalcula sobre la serie
 * dibujada.
 *
 * Color, según la convención del proyecto: gris para el contexto, azul
 * institucional para el dato. En el gráfico de Cocora el dato de interés es
 * la carga pesada — es la que el túnel captaría — y el total es el contexto.
 * En la serie de INVÍAS, azul para las dos estaciones que caen entre los
 * portales del trazado del OE 1 y gris para la que queda fuera.
 */

import React from 'react';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import datosOE5 from '@/data/siniestralidad_oe5.json';

const AZUL = '#193F77';
const AZUL_MEDIO = '#2a78d6';
const GRIS = '#94a3b8';
const GRIS_CLARO = '#cbd5e1';

type PuntoCocora = { mes: string; dias: number; tpd: number; tpd_pes: number; t: number };
type PuntoInvias = { anio: number; tpd: number; pct_pesada: number | null };
type Estacion = {
  estacion: string;
  /** Nombre del sector normalizado a español; `sector_csv` guarda el literal de INVÍAS. */
  sector: string;
  sector_csv: string;
  longitud_km: number;
  en_corredor: boolean;
  serie: PuntoInvias[];
};

const COCORA = datosOE5.cocora.serie as PuntoCocora[];
const COCORA_RESUMEN = datosOE5.cocora.resumen;
const ESTACIONES = datosOE5.invias.estaciones as Estacion[];

const es = (n: number, dec = 0) =>
  n.toLocaleString('es-CO', { minimumFractionDigits: dec, maximumFractionDigits: dec });

const MESES_CORTO = [
  'ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic',
];

/** '2026-05' -> 'may 2026' */
const mesLargo = (mes: string) => {
  const [a, m] = mes.split('-');
  return `${MESES_CORTO[Number(m) - 1]} ${a}`;
};

/* ------------------------------------------------------------- tooltips */

const TipCocora: React.FC<any> = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload as PuntoCocora;
  const pct = (d.tpd_pes / d.tpd) * 100;
  return (
    <div className="rounded-lg border border-slate-200 bg-white/95 p-3 shadow-lg backdrop-blur-sm">
      <p className="mb-1.5 border-b border-slate-200 pb-1 font-mono text-[11px] font-bold text-uni-900">
        {mesLargo(d.mes)} · {d.dias} días
      </p>
      <dl className="space-y-0.5 text-[11px]">
        <div className="flex items-center gap-2">
          <span className="h-0.5 w-3.5 shrink-0" style={{ background: GRIS }} />
          <dt className="text-slate-500">Todos los vehículos</dt>
          <dd className="ml-auto font-semibold text-slate-700">{es(d.tpd)} veh/día</dd>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-0.5 w-3.5 shrink-0" style={{ background: AZUL }} />
          <dt className="text-slate-500">Carga pesada</dt>
          <dd className="ml-auto font-semibold text-slate-700">{es(d.tpd_pes)} veh/día</dd>
        </div>
        <div className="flex items-center gap-2 border-t border-slate-100 pt-1">
          <dt className="text-slate-500">Participación pesada</dt>
          <dd className="ml-auto font-bold text-uni-900">{es(pct, 1)} %</dd>
        </div>
      </dl>
    </div>
  );
};

const TipInvias: React.FC<any> = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-slate-200 bg-white/95 p-3 shadow-lg backdrop-blur-sm">
      <p className="mb-1.5 border-b border-slate-200 pb-1 font-mono text-[11px] font-bold text-uni-900">
        {label}
      </p>
      <dl className="space-y-0.5 text-[11px]">
        {payload.map((s: any) => (
          <div key={s.dataKey} className="flex items-center gap-2">
            <span className="h-0.5 w-3.5 shrink-0" style={{ background: s.color }} />
            <dt className="text-slate-500">Estación {String(s.dataKey).replace('e', '')}</dt>
            <dd className="ml-auto font-semibold text-slate-700">
              {s.value == null ? 'sin dato' : `${es(s.value)} veh/día`}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
};

/* ------------------------------------------- exposición en el peaje Cocora */

export const ExposicionCocora: React.FC = () => (
  <div className="space-y-4">
    <div className="h-[320px] w-full sm:h-[400px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={COCORA} margin={{ top: 26, right: 18, left: 4, bottom: 12 }}>
          <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" vertical={false} />

          <XAxis
            dataKey="t"
            type="number"
            domain={[2021.6, 2026.45]}
            ticks={[2022, 2023, 2024, 2025, 2026]}
            tickFormatter={(v) => String(Math.round(v))}
            stroke="#94a3b8"
            tick={{ fill: '#64748b', fontSize: 11 }}
          />
          <YAxis
            domain={[0, 7200]}
            ticks={[0, 1000, 2000, 3000, 4000, 5000, 6000, 7000]}
            tickFormatter={(v) => es(v)}
            stroke="#94a3b8"
            tick={{ fill: '#64748b', fontSize: 11 }}
            width={66}
            label={{
              value: 'Tránsito promedio diario (veh/día)',
              angle: -90,
              position: 'insideLeft',
              fill: '#64748b',
              fontSize: 11,
              style: { textAnchor: 'middle' },
            }}
          />

          <Tooltip content={<TipCocora />} cursor={{ stroke: '#94a3b8', strokeDasharray: '4 4' }} />
          <Legend verticalAlign="top" height={30} iconType="plainline" wrapperStyle={{ fontSize: 11 }} />

          {/* Medias de los últimos doce meses. Ponderadas por días — ver el
              encabezado del archivo. Se leen de `resumen`, no de la serie. */}
          <ReferenceLine
            y={COCORA_RESUMEN.tpd_medio_12m}
            stroke={GRIS}
            strokeDasharray="6 4"
            label={{
              value: `media 12 meses  ${es(COCORA_RESUMEN.tpd_medio_12m)}`,
              position: 'insideTopLeft',
              fill: '#64748b',
              fontSize: 11,
              fontWeight: 700,
            }}
          />
          <ReferenceLine
            y={COCORA_RESUMEN.tpd_pesado_medio_12m}
            stroke={AZUL}
            strokeDasharray="6 4"
            label={{
              value: `media 12 meses  ${es(COCORA_RESUMEN.tpd_pesado_medio_12m)}`,
              position: 'insideBottomLeft',
              fill: AZUL,
              fontSize: 11,
              fontWeight: 700,
            }}
          />

          <Line
            type="linear"
            dataKey="tpd"
            name="Todos los vehículos"
            stroke={GRIS}
            strokeWidth={1.6}
            dot={false}
            activeDot={{ r: 4, fill: GRIS, stroke: '#fff', strokeWidth: 2 }}
          />
          <Line
            type="linear"
            dataKey="tpd_pes"
            name="Carga pesada (categorías III a VII)"
            stroke={AZUL}
            strokeWidth={2.2}
            dot={false}
            activeDot={{ r: 4, fill: AZUL, stroke: '#fff', strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>

    <p className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-[11px] leading-relaxed text-slate-500">
      <strong className="text-slate-700">Cómo se calcula la media rotulada.</strong>{' '}
      {COCORA_RESUMEN.metodo} La ventana va de {COCORA_RESUMEN.ventana_12m_texto} ({COCORA_RESUMEN.dias_ventana}{' '}
      días). La serie mensual es volátil —octubre de 2021 es un mes de apertura parcial y diciembre
      dispara el tráfico de pasajeros—, de modo que la cifra que entra en la tasa es la media anual,
      no un mes suelto. La carga pesada, en cambio, apenas se mueve: es {es(COCORA_RESUMEN.pct_pesada_12m, 1)} %
      del total.
    </p>
  </div>
);

/* ------------------------------------ serie histórica de INVÍAS 1997–2018 */

/** Serie ancha: un registro por año, una columna por estación. */
const SERIE_INVIAS = (() => {
  const anios = new Set<number>();
  ESTACIONES.forEach((e) => e.serie.forEach((p) => anios.add(p.anio)));
  return Array.from(anios)
    .sort((a, b) => a - b)
    .map((anio) => {
      const fila: Record<string, number | null> = { anio };
      ESTACIONES.forEach((e) => {
        const p = e.serie.find((x) => x.anio === anio);
        fila[`e${e.estacion}`] = p ? p.tpd : null;
      });
      return fila;
    });
})();

/* Trazos escritos completos y literales: Tailwind no ve una clase compuesta
   en tiempo de ejecución, y aquí además son colores de SVG, no clases. */
const TRAZO_ESTACION: Record<string, { color: string; ancho: number }> = {
  e243: { color: AZUL, ancho: 2.2 },
  e244: { color: AZUL_MEDIO, ancho: 2.2 },
  e245: { color: GRIS_CLARO, ancho: 1.6 },
};

export const TransitoInvias: React.FC = () => (
  <div className="space-y-4">
    <div className="h-[320px] w-full sm:h-[400px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={SERIE_INVIAS} margin={{ top: 26, right: 18, left: 4, bottom: 12 }}>
          <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" vertical={false} />

          <XAxis
            dataKey="anio"
            type="number"
            domain={[1997, 2018]}
            ticks={[1997, 2000, 2003, 2006, 2009, 2012, 2015, 2018]}
            stroke="#94a3b8"
            tick={{ fill: '#64748b', fontSize: 11 }}
          />
          <YAxis
            domain={[0, 18000]}
            ticks={[0, 4000, 8000, 12000, 16000]}
            tickFormatter={(v) => es(v)}
            stroke="#94a3b8"
            tick={{ fill: '#64748b', fontSize: 11 }}
            width={66}
            label={{
              value: 'Tránsito promedio diario (veh/día)',
              angle: -90,
              position: 'insideLeft',
              fill: '#64748b',
              fontSize: 11,
              style: { textAnchor: 'middle' },
            }}
          />

          <Tooltip content={<TipInvias />} cursor={{ stroke: '#94a3b8', strokeDasharray: '4 4' }} />
          <Legend verticalAlign="top" height={30} iconType="plainline" wrapperStyle={{ fontSize: 11 }} />

          {ESTACIONES.map((e) => {
            /* Si el archivo de datos trajera una estación nueva, cae en el
               trazo de contexto en vez de romper el gráfico. */
            const trazo = TRAZO_ESTACION[`e${e.estacion}`] ?? { color: GRIS, ancho: 1.6 };
            return (
              <Line
                key={e.estacion}
                type="linear"
                dataKey={`e${e.estacion}`}
                name={`${e.estacion} · ${e.sector} · ${e.longitud_km} km${
                  e.en_corredor ? '' : ' (fuera del paso)'
                }`}
                stroke={trazo.color}
                strokeWidth={trazo.ancho}
                strokeDasharray={e.en_corredor ? undefined : '5 4'}
                connectNulls={false}
                dot={false}
                activeDot={{ r: 4, fill: trazo.color, stroke: '#fff', strokeWidth: 2 }}
              />
            );
          })}
        </LineChart>
      </ResponsiveContainer>
    </div>

    <p className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-[11px] leading-relaxed text-slate-500">
      <strong className="text-slate-700">Qué mirar y qué no concluir.</strong> Las dos series
      continuas son los tramos que quedan entre los portales del trazado del objetivo específico 1;
      la punteada, Armenia – Calarcá, queda fuera del paso y es tráfico urbano de Armenia: por eso
      dobla a las otras en volumen y apenas lleva carga. Los huecos son años sin publicación en la
      serie de INVÍAS —2009 y 2010 en la estación 244, 2009 en la 243— y se dejan vacíos en lugar de
      interpolarse. El promedio de la estación 244 entre 2015 y 2018 es{' '}
      <strong className="text-slate-700">{es(datosOE5.invias.resumen.est244_tpd_2015_2018)} veh/día</strong>,
      y es el denominador de la tasa del paso.
    </p>
  </div>
);
