'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, ReferenceDot,
} from 'recharts';
import { Mountain, TrendingDown, Layers, FileText, ExternalLink, Info } from 'lucide-react';
import datos from '@/data/perfil_oe1.json';
import { GEO, TRAZADO, EQUIPO } from '@/data/proyecto';

type Punto = { pk: number; t: number; r: number; c: number };
const PERFIL = datos.perfil as Punto[];
const RANGOS = datos.rangos as { label: string; km: number; pct: number }[];
const R = datos.resumen;

/* Paleta: azul = el dato (rasante), gris = el contexto (terreno).
   Rampa azul de 5 pasos para la cobertura porque es una escala de MAGNITUD. */
const ACC = '#193F77';
const STEPS = ['#cde2fb', '#9ec5f4', '#5598e7', '#2a78d6', '#184f95'];

const fmt = (n: number) => n.toLocaleString('es-CO');

const TooltipPerfil = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const d: Punto = payload[0].payload;
  return (
    <div className="bg-slate-50 border border-slate-300 rounded-xl shadow-2xl px-4 py-3 text-xs space-y-1.5">
      <p className="font-bold text-uni-900 border-b border-slate-200 pb-1.5">
        PK {d.pk.toFixed(1).replace('.', ',')} km
      </p>
      <div className="flex items-center justify-between gap-6">
        <span className="text-slate-500">Terreno</span>
        <span className="font-mono font-bold text-slate-700">{fmt(d.t)} msnm</span>
      </div>
      <div className="flex items-center justify-between gap-6">
        <span className="text-uni-600">Rasante del túnel</span>
        <span className="font-mono font-bold text-uni-700">{fmt(d.r)} msnm</span>
      </div>
      <div className="flex items-center justify-between gap-6 pt-1.5 border-t border-slate-200">
        <span className="text-slate-600 font-semibold">Cobertura</span>
        <span className="font-mono font-bold text-uni-900">{fmt(d.c)} m</span>
      </div>
    </div>
  );
};

const Dato: React.FC<{ valor: string; etiqueta: string; nota?: string }> = ({ valor, etiqueta, nota }) => (
  <div className="rounded-xl bg-slate-50 border border-slate-200 p-4">
    <span className="block text-2xl font-black text-uni-900 leading-none">{valor}</span>
    <span className="block text-xs text-slate-600 font-semibold mt-1.5">{etiqueta}</span>
    {nota && <span className="block text-[10px] text-slate-500 mt-0.5 font-mono">{nota}</span>}
  </div>
);

export const PerfilTunel: React.FC = () => {
  const [abierto, setAbierto] = useState(false);
  const iMax = PERFIL.reduce((m, p, i) => (p.c > PERFIL[m].c ? i : m), 0);

  return (
    <section id="perfil" className="py-24 bg-slate-50 relative overflow-hidden border-t border-slate-200">
      <div className="absolute top-1/3 left-1/4 w-[600px] h-[400px] bg-blue-600/5 blur-[140px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">

        <div className="text-center max-w-3xl mx-auto space-y-4 mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-uni-600 text-xs font-semibold uppercase tracking-wider">
            <Mountain className="w-3.5 h-3.5" />
            <span>Objetivo específico 1 · Análisis propio</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-uni-900 tracking-tight">
            El perfil del túnel, calculado por nosotros
          </h2>
          <p className="text-base sm:text-lg text-slate-500 leading-relaxed">
            No es una cifra de la ponencia: es el resultado de procesar un modelo de elevación digital
            del corredor. Pasa el cursor sobre el perfil para ver la cota del terreno y la cobertura
            del túnel en cualquier punto.
          </p>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Dato valor={GEO.longitud.valor} etiqueta="Longitud del alineamiento" nota="entre portales" />
          <Dato valor={GEO.pendiente.valor} etiqueta="Pendiente de rasante" nota={`criterio ${TRAZADO.pendienteCriterio.valor}`} />
          <Dato valor={`${fmt(R.cobertura_max_m)} m`} etiqueta="Cobertura máxima" nota={`PK ${fmt(R.cobertura_max_pk)}`} />
          <Dato valor={`${fmt(R.cobertura_media_m)} m`} etiqueta="Cobertura media" nota="sobre 1.500 puntos" />
        </div>

        {/* Perfil interactivo */}
        <motion.div
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ duration: .6 }}
          className="rounded-2xl bg-white border border-slate-200 p-5 sm:p-7"
        >
          <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
            <h3 className="text-lg font-bold text-uni-900">Perfil longitudinal del terreno y del túnel</h3>
            <div className="flex items-center gap-5 text-xs">
              <span className="inline-flex items-center gap-2 text-slate-500">
                <span className="w-4 h-0.5 bg-slate-500 rounded" /> Terreno
              </span>
              <span className="inline-flex items-center gap-2 text-slate-600">
                <span className="w-4 h-1 rounded" style={{ background: ACC }} /> Rasante del túnel
              </span>
            </div>
          </div>

          <div className="h-[380px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={PERFIL} margin={{ top: 10, right: 16, left: 4, bottom: 16 }}>
                <defs>
                  <linearGradient id="gTerreno" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#9ec5f4" stopOpacity={0.30} />
                    <stop offset="100%" stopColor="#9ec5f4" stopOpacity={0.04} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="pk" type="number" domain={[0, 52.212]}
                  ticks={[0, 10, 20, 30, 40, 50]} tickFormatter={(v) => `${v}`}
                  stroke="#64748b" tick={{ fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#cbd5e1' }}
                  label={{ value: 'Abscisa desde el portal oriental (km)', position: 'insideBottom',
                           offset: -10, fill: '#475569', fontSize: 11 }} />
                <YAxis domain={[400, 3800]} ticks={[500, 1500, 2500, 3500]}
                  stroke="#64748b" tick={{ fontSize: 11 }} tickLine={false} axisLine={false}
                  tickFormatter={(v) => fmt(v)}
                  label={{ value: 'Cota (msnm)', angle: -90, position: 'insideLeft',
                           fill: '#475569', fontSize: 11, style: { textAnchor: 'middle' } }} />
                <Tooltip content={<TooltipPerfil />} cursor={{ stroke: ACC, strokeWidth: 1, strokeDasharray: '4 4' }} />
                <Area type="monotone" dataKey="t" stroke="#64748b" strokeWidth={1.2}
                      fill="url(#gTerreno)" dot={false} isAnimationActive={false} name="Terreno" />
                <Line type="linear" dataKey="r" stroke={ACC} strokeWidth={2.4}
                      dot={false} isAnimationActive={false} name="Rasante" />
                <ReferenceLine x={PERFIL[iMax].pk} stroke={ACC} strokeDasharray="4 4" strokeOpacity={.7} />
                <ReferenceDot x={PERFIL[0].pk} y={PERFIL[0].r} r={5} fill="#ffffff" stroke={ACC} strokeWidth={2.4} />
                <ReferenceDot x={PERFIL[PERFIL.length - 1].pk} y={PERFIL[PERFIL.length - 1].r}
                              r={5} fill="#ffffff" stroke={ACC} strokeWidth={2.4} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-4 mt-4 pt-4 border-t border-slate-200 text-[11px] text-slate-500">
            <span>Portal oriental · Ibagué, Tolima · {GEO.cotaPortalIbague} msnm · Portal occidental · Calarcá, Quindío · {fmt(GEO.cotaPortalArmenia)} msnm</span>
            <span className="font-mono">{GEO.fuenteDEM}</span>
          </div>
        </motion.div>

        {/* Distribución de cobertura */}
        <div className="mt-6 rounded-2xl bg-white border border-slate-200 p-5 sm:p-7">
          <div className="flex items-center gap-2 mb-1.5">
            <Layers className="w-4 h-4 text-uni-600" />
            <h3 className="text-lg font-bold text-uni-900">Cuánto túnel va bajo cuánta montaña</h3>
          </div>
          <p className="text-xs text-slate-500 mb-5 max-w-3xl leading-relaxed">
            La cobertura condiciona el método de excavación. El {fmt(R.pct_sobre_700)} % del trazado va con
            más de 700 m de roca encima — el insumo que necesita el objetivo específico 4 para
            contrastar tuneladora contra voladura.
          </p>

          <div className="flex w-full h-12 rounded-lg overflow-hidden">
            {RANGOS.map((r, i) => (
              <div key={r.label} style={{ width: `${r.pct}%`, background: STEPS[i] }}
                   className="flex items-center justify-center relative group cursor-default">
                {r.pct > 8 && (
                  <span className={`text-[11px] font-bold ${i >= 3 ? 'text-uni-900' : 'text-slate-900'}`}>
                    {r.pct.toFixed(0)} %
                  </span>
                )}
                <div className="absolute bottom-full mb-2 hidden group-hover:block z-10 whitespace-nowrap bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-[11px] shadow-xl">
                  <span className="text-uni-900 font-bold">{r.label}</span>
                  <span className="text-slate-500"> · {r.km.toLocaleString('es-CO', { maximumFractionDigits: 1 })} km · {fmt(r.pct)} %</span>
                </div>
              </div>
            ))}
          </div>
          <div className="flex flex-wrap gap-x-5 gap-y-2 mt-3">
            {RANGOS.map((r, i) => (
              <span key={r.label} className="inline-flex items-center gap-2 text-[11px] text-slate-500">
                <span className="w-3 h-3 rounded-sm" style={{ background: STEPS[i] }} />
                {r.label}
              </span>
            ))}
          </div>
          <p className="text-[10px] text-slate-600 mt-4">
            Los cinco rangos son una clasificación propia del semillero, no una norma técnica.
          </p>
        </div>

        {/* Metodología */}
        <div className="mt-6 rounded-2xl bg-white border border-slate-200 overflow-hidden">
          <button onClick={() => setAbierto(v => !v)}
                  className="w-full text-left p-5 sm:p-7 hover:bg-white transition-colors"
                  aria-expanded={abierto}>
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                <FileText className="w-5 h-5 text-uni-600 shrink-0 mt-0.5" />
                <div>
                  <h3 className="text-lg font-bold text-uni-900">¿De dónde salen estos números?</h3>
                  <p className="text-xs text-slate-500 mt-1">
                    Método, fuentes y limitaciones. Todo es reproducible.
                  </p>
                </div>
              </div>
              <span className="text-xs text-uni-600 font-semibold shrink-0">
                {abierto ? 'Ocultar' : 'Ver método'}
              </span>
            </div>
          </button>

          {abierto && (
            <div className="px-5 sm:px-7 pb-7 space-y-5 border-t border-slate-200 pt-5">
              <div className="grid sm:grid-cols-2 gap-5">
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">Cómo se hizo</h4>
                  <ol className="space-y-1.5 text-xs text-slate-500 leading-relaxed list-decimal list-inside">
                    <li>Descarga del Copernicus DEM GLO-30 (ESA/Airbus) del corredor.</li>
                    <li>Validación contra cotas de cascos urbanos: error medio 35 m, del orden de un píxel.</li>
                    <li>Búsqueda sobre el DEM de los puntos a 950 y 1.450 msnm que declara la ponencia.</li>
                    <li>Selección del par de portales que minimiza la distancia entre ellos.</li>
                    <li>Extracción del perfil del terreno en 1.500 puntos sobre la geodésica.</li>
                    <li>Cálculo de la rasante, la pendiente y la cobertura punto a punto.</li>
                  </ol>
                </div>
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">Qué NO afirma este análisis</h4>
                  <ul className="space-y-1.5 text-xs text-slate-500 leading-relaxed">
                    <li>· La ubicación de portales es geométrica, no geotécnica. Falta cruzarla con riesgo de remoción en masa.</li>
                    <li>· Un DEM de 30 m sirve para prefactibilidad; no es un levantamiento topográfico.</li>
                    <li>· El GLO-30 es un modelo de superficie: incluye vegetación y edificaciones.</li>
                    <li>· La rasante recta no es un diseño vertical definitivo.</li>
                    <li>· El criterio de pendiente menor al 1,5 % es una hipótesis nuestra; la ponencia no la declara.</li>
                  </ul>
                </div>
              </div>

              <div className="rounded-xl bg-emerald-500/5 border border-emerald-500/25 p-4 space-y-2">
                <div className="flex items-center gap-2 text-xs font-bold text-white uppercase tracking-wider">
                  <Info className="w-3.5 h-3.5" />
                  Dos comprobaciones que sostienen el resultado
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  <strong className="text-uni-900">La cota máxima del terreno da {fmt(R.cota_max_terreno)} msnm</strong> y la
                  ponencia declara 3.300 msnm para el paso del Alto de La Línea. Dos fuentes independientes convergen.
                </p>
                <p className="text-xs text-slate-600 leading-relaxed">
                  <strong className="text-uni-900">Los {GEO.longitud.valor} no contradicen los 58 km de la ponencia:</strong> esos 58 son
                  el corredor completo, con tramos a cielo abierto entre los siete túneles; el túnel principal
                  declarado son 44 km. La recta entre portales queda entre ambos valores.
                </p>
              </div>

              <p className="text-[11px] text-slate-500 leading-relaxed border-t border-slate-200 pt-4">
                {GEO.nota} · Análisis del {EQUIPO.semillero}, {EQUIPO.universidad}.
              </p>
              <a href="https://www.ferropista.com" target="_blank" rel="noopener noreferrer"
                 className="inline-flex items-center gap-2 text-xs font-semibold text-uni-600 hover:text-uni-700">
                Propuesta original de ARCS / UC Consult
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          )}
        </div>

      </div>
    </section>
  );
};
