'use client';

/**
 * GraficosOE1 — el perfil longitudinal y la cobertura del objetivo específico 1,
 * dibujados en el navegador a partir de `src/data/perfil_oe1.json`.
 *
 * Sustituyen a las dos láminas PNG que antes ocupaban su lugar en la página.
 * Las láminas siguen existiendo: son el entregable subido a Drive y quedan
 * enlazadas para descarga bajo cada gráfico.
 *
 * LÍMITE DECLARADO — leer antes de tocar las cifras rotuladas:
 * el archivo que consume el sitio es un SUBMUESTREO de 401 puntos del perfil
 * calculado sobre 1.500, y el remuestreo fuerza la inclusión del punto de
 * cobertura máxima y del de cota máxima del terreno. Por eso la curva SÍ pasa
 * hoy por la cifra que rotula: 2.031 m en el PK 42,84. Hasta el 15 sep 2026 el
 * archivo tenía 188 puntos y su máximo era 1.999 m en el PK 42,7, que no era el
 * publicado; esa incoherencia queda resuelta.
 * Lo que sigue sin leerse de la curva son las cifras agregadas —la cobertura
 * media de 840 m y los porcentajes por rango—, que son promedios sobre los
 * 1.500 puntos del cálculo y no sobre los 401 dibujados. Se toman de `resumen`
 * y de `rangos`, que el propio archivo trae, y el pie del gráfico lo dice.
 *
 * Color, según la convención del proyecto: gris para el contexto (el terreno),
 * azul institucional para el dato (la rasante). La cobertura usa una rampa
 * secuencial de un solo tono, de claro a oscuro, con luminancia monótona
 * decreciente (0,743 → 0,537 → 0,302 → 0,188 → 0,080).
 */

import React, { useMemo, useState } from 'react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  Line,
  ReferenceDot,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import perfilOE1 from '@/data/perfil_oe1.json';

const AZUL = '#193F77';
const GRIS = '#94a3b8';
const GRIS_TRAMA = '#cbd5e1';

/** Rampa secuencial de un solo tono para la magnitud de cobertura. */
const RAMPA_COBERTURA = ['#cde2fb', '#9ec5f4', '#5598e7', '#2a78d6', '#184f95'];

type Punto = { pk: number; t: number; r: number; c: number };
const PERFIL = perfilOE1.perfil as Punto[];
const RANGOS = perfilOE1.rangos as { label: string; km: number; pct: number }[];
const RESUMEN = perfilOE1.resumen;

const es = (n: number, dec = 0) =>
  n.toLocaleString('es-CO', { minimumFractionDigits: dec, maximumFractionDigits: dec });

/* ---------------------------------------------------------------- tooltips */

const TipPerfil: React.FC<any> = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload as Punto;
  return (
    <div className="rounded-lg border border-slate-200 bg-white/95 p-3 shadow-lg backdrop-blur-sm">
      <p className="mb-1.5 border-b border-slate-200 pb-1 font-mono text-[11px] font-bold text-uni-900">
        PK {es(Number(label), 1)} km
      </p>
      <dl className="space-y-0.5 text-[11px]">
        <div className="flex items-center gap-2">
          <span className="h-0.5 w-3.5 shrink-0" style={{ background: GRIS }} />
          <dt className="text-slate-500">Terreno</dt>
          <dd className="ml-auto font-semibold text-slate-700">{es(d.t)} msnm</dd>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-0.5 w-3.5 shrink-0" style={{ background: AZUL }} />
          <dt className="text-slate-500">Rasante</dt>
          <dd className="ml-auto font-semibold text-slate-700">{es(d.r)} msnm</dd>
        </div>
        <div className="flex items-center gap-2 border-t border-slate-100 pt-1">
          <dt className="text-slate-500">Cobertura</dt>
          <dd className="ml-auto font-bold text-uni-900">{es(d.c)} m</dd>
        </div>
      </dl>
    </div>
  );
};

const TipCobertura: React.FC<any> = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload as Punto;
  return (
    <div className="rounded-lg border border-slate-200 bg-white/95 p-3 shadow-lg backdrop-blur-sm">
      <p className="mb-1 font-mono text-[11px] font-bold text-uni-900">PK {es(Number(label), 1)} km</p>
      <p className="text-[11px] text-slate-500">
        Cobertura <span className="font-bold text-uni-900">{es(d.c)} m</span>
      </p>
      <p className="text-[10px] text-slate-400">Terreno {es(d.t)} · rasante {es(d.r)} msnm</p>
    </div>
  );
};

/* ------------------------------------------------- perfil longitudinal */

export const PerfilOE1: React.FC = () => (
  <div className="h-[340px] w-full sm:h-[420px]">
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={PERFIL} margin={{ top: 28, right: 18, left: 4, bottom: 12 }}>
        <defs>
          <linearGradient id="oe1-terreno" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={GRIS} stopOpacity={0.38} />
            <stop offset="100%" stopColor={GRIS} stopOpacity={0.08} />
          </linearGradient>
        </defs>

        <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" vertical={false} />

        <XAxis
          dataKey="pk"
          type="number"
          domain={[0, RESUMEN.longitud_km]}
          ticks={[0, 10, 20, 30, 40, 50]}
          tickFormatter={(v) => es(v)}
          stroke="#94a3b8"
          tick={{ fill: '#64748b', fontSize: 11 }}
          label={{
            value: 'Abscisa desde el portal oriental (km)',
            position: 'insideBottom',
            offset: -6,
            fill: '#64748b',
            fontSize: 11,
          }}
        />
        <YAxis
          domain={[500, 3600]}
          ticks={[500, 1000, 1500, 2000, 2500, 3000, 3500]}
          tickFormatter={(v) => es(v)}
          stroke="#94a3b8"
          tick={{ fill: '#64748b', fontSize: 11 }}
          width={52}
          label={{
            value: 'Cota (msnm)',
            angle: -90,
            position: 'insideLeft',
            fill: '#64748b',
            fontSize: 11,
            style: { textAnchor: 'middle' },
          }}
        />

        <Tooltip content={<TipPerfil />} cursor={{ stroke: '#94a3b8', strokeDasharray: '4 4' }} />
        <Legend verticalAlign="top" height={30} iconType="plainline" wrapperStyle={{ fontSize: 11 }} />

        <Area
          type="monotone"
          dataKey="t"
          name="Perfil del terreno (Copernicus DEM GLO-30)"
          stroke={GRIS_TRAMA}
          strokeWidth={1.6}
          fill="url(#oe1-terreno)"
          dot={false}
          activeDot={{ r: 4, fill: GRIS, stroke: '#fff', strokeWidth: 2 }}
        />
        <Line
          type="linear"
          dataKey="r"
          name={`Rasante del túnel de base — ${es(RESUMEN.pendiente_pct, 3)} %`}
          stroke={AZUL}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4, fill: AZUL, stroke: '#fff', strokeWidth: 2 }}
        />

        {/* Portales: los dos extremos del alineamiento */}
        <ReferenceDot x={0} y={RESUMEN.portal_e_msnm} r={5} fill="#fff" stroke={AZUL} strokeWidth={2} />
        <ReferenceDot
          x={RESUMEN.longitud_km}
          y={RESUMEN.portal_w_msnm}
          r={5}
          fill="#fff"
          stroke={AZUL}
          strokeWidth={2}
        />

        {/* Cobertura máxima. La cifra es la del cálculo a 1.500 puntos. */}
        <ReferenceLine
          x={RESUMEN.cobertura_max_pk}
          stroke={AZUL}
          strokeDasharray="4 4"
          strokeOpacity={0.6}
          label={{
            value: `Cobertura máxima ${es(RESUMEN.cobertura_max_m)} m · PK ${es(RESUMEN.cobertura_max_pk, 1)}`,
            position: 'top',
            fill: '#0f2449',
            fontSize: 11,
            fontWeight: 700,
          }}
        />
      </AreaChart>
    </ResponsiveContainer>
  </div>
);

/* ------------------------------------------------------------ cobertura */

export const CoberturaOE1: React.FC = () => {
  const [rangoActivo, setRangoActivo] = useState<number | null>(null);

  const umbrales = useMemo(() => [100, 300, 700, 1200], []);

  return (
    <div className="space-y-5">
      <div className="h-[300px] w-full sm:h-[360px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={PERFIL} margin={{ top: 26, right: 18, left: 4, bottom: 12 }}>
            <defs>
              <linearGradient id="oe1-cobertura" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={RAMPA_COBERTURA[4]} stopOpacity={0.95} />
                <stop offset="55%" stopColor={RAMPA_COBERTURA[2]} stopOpacity={0.8} />
                <stop offset="100%" stopColor={RAMPA_COBERTURA[0]} stopOpacity={0.65} />
              </linearGradient>
            </defs>

            <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" vertical={false} />

            <XAxis
              dataKey="pk"
              type="number"
              domain={[0, RESUMEN.longitud_km]}
              ticks={[0, 10, 20, 30, 40, 50]}
              tickFormatter={(v) => es(v)}
              stroke="#94a3b8"
              tick={{ fill: '#64748b', fontSize: 11 }}
              label={{
                value: 'Abscisa desde el portal oriental (km)',
                position: 'insideBottom',
                offset: -6,
                fill: '#64748b',
                fontSize: 11,
              }}
            />
            <YAxis
              domain={[0, 2200]}
              ticks={[0, 500, 1000, 1500, 2000]}
              tickFormatter={(v) => es(v)}
              stroke="#94a3b8"
              tick={{ fill: '#64748b', fontSize: 11 }}
              width={52}
              label={{
                value: 'Cobertura sobre la clave (m)',
                angle: -90,
                position: 'insideLeft',
                fill: '#64748b',
                fontSize: 11,
                style: { textAnchor: 'middle' },
              }}
            />

            <Tooltip content={<TipCobertura />} cursor={{ stroke: '#94a3b8', strokeDasharray: '4 4' }} />

            {/* Umbrales de la clasificación por rangos, en gris: son contexto */}
            {umbrales.map((u) => (
              <ReferenceLine key={u} y={u} stroke="#e2e8f0" strokeWidth={1} />
            ))}

            <Area
              type="monotone"
              dataKey="c"
              name="Cobertura sobre la clave"
              stroke={RAMPA_COBERTURA[4]}
              strokeWidth={1.6}
              fill="url(#oe1-cobertura)"
              dot={false}
              activeDot={{ r: 4, fill: RAMPA_COBERTURA[4], stroke: '#fff', strokeWidth: 2 }}
            />

            <ReferenceLine
              y={RESUMEN.cobertura_media_m}
              stroke="#475569"
              strokeDasharray="6 4"
              label={{
                value: `media ${es(RESUMEN.cobertura_media_m)} m`,
                position: 'insideTopRight',
                fill: '#475569',
                fontSize: 11,
              }}
            />
            <ReferenceDot
              x={RESUMEN.cobertura_max_pk}
              y={RESUMEN.cobertura_max_m}
              r={5}
              fill="#fff"
              stroke={RAMPA_COBERTURA[4]}
              strokeWidth={2}
              label={{
                value: `${es(RESUMEN.cobertura_max_m)} m · PK ${es(RESUMEN.cobertura_max_pk, 1)}`,
                position: 'top',
                fill: '#0f2449',
                fontSize: 11,
                fontWeight: 700,
              }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Distribución por rangos. Antes vivía suelta entre las cifras del
          objetivo, repitiendo lo que la lámina ya mostraba; aquí queda junto
          a la curva de la que sale. */}
      <div>
        <div className="mb-2 flex flex-wrap items-baseline gap-x-2">
          <h4 className="text-sm font-bold text-slate-700">Distribución de la longitud por rango de cobertura</h4>
          <span className="font-mono text-[10px] text-slate-400">
            los rangos son una clasificación propia del semillero, no una norma
          </span>
        </div>

        <div className="flex h-9 w-full overflow-hidden rounded-lg">
          {RANGOS.map((r, i) => (
            <button
              key={r.label}
              type="button"
              onMouseEnter={() => setRangoActivo(i)}
              onMouseLeave={() => setRangoActivo(null)}
              onFocus={() => setRangoActivo(i)}
              onBlur={() => setRangoActivo(null)}
              style={{ width: `${r.pct}%`, background: RAMPA_COBERTURA[i] }}
              className={`flex items-center justify-center border-r-2 border-white transition-opacity last:border-r-0 ${
                rangoActivo !== null && rangoActivo !== i ? 'opacity-45' : 'opacity-100'
              }`}
              aria-label={`${r.label}: ${es(r.km, 1)} km, ${es(r.pct, 1)} por ciento`}
            >
              {r.pct >= 8 && (
                <span className={`text-[11px] font-bold ${i >= 3 ? 'text-white' : 'text-uni-900'}`}>
                  {es(r.pct, 1)} %
                </span>
              )}
            </button>
          ))}
        </div>

        <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5">
          {RANGOS.map((r, i) => (
            <div
              key={r.label}
              className={`flex items-start gap-2 text-[11px] transition-opacity ${
                rangoActivo !== null && rangoActivo !== i ? 'opacity-45' : 'opacity-100'
              }`}
            >
              <span
                className="mt-0.5 h-3 w-3 shrink-0 rounded-sm"
                style={{ background: RAMPA_COBERTURA[i] }}
              />
              <span className="text-slate-500">
                <span className="font-semibold text-slate-600">{r.label}</span>
                <br />
                {es(r.km, 1)} km · {es(r.pct, 1)} %
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
