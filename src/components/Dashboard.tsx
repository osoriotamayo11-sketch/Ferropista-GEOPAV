'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList,
} from 'recharts';
import { BarChart3, Clock, Hourglass, ArrowDownRight, Activity } from 'lucide-react';
import { ACTUAL, OPERACION, ECONOMICO } from '@/data/proyecto';

export const Dashboard: React.FC = () => {
  // Data 1: Tiempo de cruce del paso (minutos) — Ponencia, dia. 23 y 29
  const timeData = [
    {
      name: 'Ruta 40 (Actual)',
      minutos: ACTUAL.tiempoCruce.n,
      label: '4,0 horas — valor medio (dia. 29)',
      color: '#b3261e',
    },
    {
      name: 'Ferropista (Propuesta)',
      minutos: OPERACION.tCicloTotal.n,
      label: '70 min de tiempo integrado (dia. 23)',
      color: '#0F7B55',
    },
  ];

  // Data 2: Tiempos de viaje agregados de los usuarios (millones de horas/año) — Ponencia, dia. 29
  // Sustituye a la antigua grafica de "costos anuales", cuyas cifras no existian en ninguna fuente.
  const horasData = [
    {
      name: 'Ruta 40 (Actual)',
      horas: ECONOMICO.horasRuta40.n,
      label: '7,0 millones de horas/año (dia. 29)',
      color: '#CF9013',
    },
    {
      name: 'Ferropista (Propuesta)',
      horas: ECONOMICO.horasFerropista.n,
      label: '1,7 millones de horas/año (dia. 29)',
      color: '#3d63a0',
    },
  ];

  /* Data 3: reduccion relativa.
     Las dos metricas estan en unidades distintas (minutos y millones de horas/ano);
     graficarlas en un mismo eje lineal aplasta la segunda hasta hacerla invisible.
     Se grafica el porcentaje de reduccion, que si es comparable, y se dejan
     los valores absolutos como etiqueta. Calculo propio [CP] sobre cifras F. */
  const pct = (a: number, b: number) => ((a - b) / a) * 100;
  const reduccionData = [
    {
      metrica: 'Tiempo de cruce',
      reduccion: pct(ACTUAL.tiempoCruce.n, OPERACION.tCicloTotal.n),
      antes: `${ACTUAL.tiempoCruce.n} min`,
      despues: `${OPERACION.tCicloTotal.n} min`,
      fuente: 'dia. 23 y 29',
    },
    {
      metrica: 'Horas de viaje al año',
      reduccion: pct(ECONOMICO.horasRuta40.n, ECONOMICO.horasFerropista.n),
      antes: '7,0 M h/año',
      despues: '1,7 M h/año',
      fuente: 'dia. 29',
    },
  ];

  // Custom Tooltip component for Recharts
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white border border-slate-300 p-4 rounded-xl shadow-xl text-xs space-y-2">
          <p className="font-bold text-uni-900 text-sm border-b border-slate-200 pb-1">{label}</p>
          {payload.map((entry: any, index: number) => (
            <div key={`item-${index}`} className="flex items-center justify-between gap-4">
              <span className="flex items-center gap-1.5" style={{ color: entry.color }}>
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
                {entry.name}:
              </span>
              <span className="font-mono font-bold text-uni-900">
                {entry.value} {label.includes('Tiempo') ? 'min' : 'M h/año'}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };


  // Tooltip de la grafica de reduccion relativa: muestra el antes/despues real
  const TooltipReduccion = ({ active, payload }: any) => {
    if (!active || !payload?.length) return null;
    const d = payload[0].payload;
    return (
      <div className="bg-white border border-slate-300 p-4 rounded-xl shadow-xl text-xs space-y-1.5">
        <p className="font-bold text-uni-900 text-sm border-b border-slate-200 pb-1">{d.metrica}</p>
        <div className="flex items-center justify-between gap-6">
          <span className="text-red-700">Ruta 40 (actual)</span>
          <span className="font-mono font-bold text-uni-900">{d.antes}</span>
        </div>
        <div className="flex items-center justify-between gap-6">
          <span className="text-gmae-600">Ferropista (propuesta)</span>
          <span className="font-mono font-bold text-uni-900">{d.despues}</span>
        </div>
        <div className="flex items-center justify-between gap-6 pt-1.5 border-t border-slate-200">
          <span className="text-slate-600 font-semibold">Reducción</span>
          <span className="font-mono font-bold text-gmae-600">
            {d.reduccion.toFixed(1).replace('.', ',')} %
          </span>
        </div>
        <p className="text-[10px] text-slate-500 font-mono pt-1">Ponencia, {d.fuente}</p>
      </div>
    );
  };

  return (
    <section id="dashboard" className="py-24 bg-slate-50 relative overflow-hidden border-t border-slate-200 transition-colors duration-300">
      {/* Background radial glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[500px] bg-gradient-to-r from-blue-600/10 via-emerald-600/10 to-sky-600/10 blur-[140px] pointer-events-none rounded-full" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header with Framer Motion */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="text-center max-w-3xl mx-auto space-y-4 mb-16"
        >
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-uni-600 text-xs font-semibold uppercase tracking-wider">
            <BarChart3 className="w-4 h-4 text-uni-600" />
            <span>Análisis Comparativo Técnico & Operacional</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-uni-900 tracking-tight">
            Dashboard de Eficiencia Operativa
          </h2>
          <p className="text-base sm:text-lg text-slate-600 leading-relaxed font-light">
            Comparativa directa entre la infraestructura vial actual del corredor del Alto de La Línea (Ruta 40) y la propuesta intermodal de la <strong className="text-uni-900 font-medium">Ferropista Cordillera Central</strong>.
          </p>
        </motion.div>

        {/* Quick Highlights Summary Cards with Framer Motion */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="grid md:grid-cols-2 gap-6 mb-12"
        >
          {/* Card 1: Tiempo */}
          <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-lg">
            <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-gmae-600">
                <Clock className="w-7 h-7" />
              </div>
              <div>
                <span className="text-xs text-slate-500 font-mono">Reducción en Tiempo de Tránsito</span>
                <div className="text-2xl font-black text-uni-900 flex items-center gap-2">
                  <span>240 min</span>
                  <ArrowDownRight className="w-5 h-5 text-gmae-600" />
                  <span className="text-gmae-600">70 min</span>
                </div>
              </div>
            </div>
            <div className="hidden sm:block text-right shrink-0 pl-4">
              <span className="text-2xl font-black text-gmae-600">&minus;70,8 %</span>
              <span className="block text-[11px] text-slate-500">Ahorro de Tiempo</span>
            </div>
            </div>
            <p className="mt-4 border-t border-slate-200 pt-3 text-xs leading-relaxed text-slate-500">
              <strong className="font-semibold text-slate-600">Qué compara:</strong> lo que hoy tarda un
              vehículo de carga en cruzar el paso, frente al ciclo completo de la propuesta — cargue,
              cruce y descargue, no solo el cruce. El porcentaje es cálculo propio [CP] sobre las dos
              cifras de la ponencia.
            </p>
          </div>

          {/* Card 2: Horas de viaje */}
          <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-lg">
            <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-uni-600">
                <Hourglass className="w-7 h-7" />
              </div>
              <div>
                <span className="text-xs text-slate-500 font-mono">Horas de viaje de los usuarios</span>
                <div className="text-xl lg:text-2xl font-black text-uni-900 flex items-center gap-2 whitespace-nowrap">
                  <span>7,0 M h</span>
                  <ArrowDownRight className="w-5 h-5 text-uni-600 shrink-0" />
                  <span className="text-uni-600">1,7 M h</span>
                  <span className="text-xs font-mono text-slate-500 font-normal">/año</span>
                </div>
              </div>
            </div>
            <div className="hidden sm:block text-right shrink-0 pl-4">
              <span className="text-2xl font-black text-uni-600 whitespace-nowrap">5,0 &ndash; 5,3 M</span>
              <span className="block text-[11px] text-slate-500">Ahorro anual de horas [dia. 28 y 29]</span>
            </div>
            </div>
            <p className="mt-4 border-t border-slate-200 pt-3 text-xs leading-relaxed text-slate-500">
              <strong className="font-semibold text-slate-600">Qué compara:</strong> las horas que el
              conjunto de usuarios del corredor pasa viajando en un año, antes y después. Se publica un
              rango porque la fuente da dos valores del ahorro en dos diapositivas distintas: 5,0 en la
              28 y 5,3 en la 29. No se escoge uno en silencio.
            </p>
          </div>
        </motion.div>

        {/* Recharts BarCharts Grid with Framer Motion */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="grid lg:grid-cols-2 gap-8"
        >
          {/* Chart 1: Tiempo de Tránsito */}
          <div className="rounded-3xl bg-white p-6 sm:p-8 border border-slate-200 shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-200">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-lg bg-red-500/10 border border-red-500/20 text-red-700">
                    <Clock className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-uni-900 text-lg">Tiempo de Tránsito (Minutos)</h3>
                    <p className="text-xs text-slate-500">Ibagué ↔ Armenia (Cruce de Cordillera)</p>
                    <p className="mt-1 max-w-xs text-[11px] leading-snug text-slate-400">
                      Cada barra es un tiempo extremo a extremo en minutos: en rojo el paso actual, en
                      verde el ciclo integrado de la propuesta.
                    </p>
                  </div>
                </div>
                <span className="px-2.5 py-1 rounded bg-slate-100 text-slate-600 text-xs font-mono">
                  Minutos totales
                </span>
              </div>

              {/* Recharts Component */}
              <div className="h-72 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={timeData} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                    <XAxis dataKey="name" stroke="#64748b" tick={{ fill: '#475569', fontSize: 12 }} />
                    <YAxis stroke="#64748b" tick={{ fill: '#475569', fontSize: 12 }} unit=" min" />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="minutos" radius={[8, 8, 0, 0]} barSize={55}>
                      {timeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500 font-mono">
              <span>Ruta 40: 240 min (Congestión y montaña)</span>
              <span className="text-gmae-600 font-bold">Ferropista: 70 min</span>
            </div>
          </div>

          {/* Chart 2: Horas de viaje de los usuarios */}
          <div className="rounded-3xl bg-white p-6 sm:p-8 border border-slate-200 shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-200">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-acred-600">
                    <Hourglass className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-uni-900 text-lg">Tiempos de viaje (M horas/año)</h3>
                    <p className="text-xs text-slate-500">Tiempo agregado de los usuarios del corredor</p>
                    <p className="mt-1 max-w-xs text-[11px] leading-snug text-slate-400">
                      No es el tiempo de un viaje sino la suma anual de todos los usuarios del corredor.
                      La diferencia entre las dos barras es el ahorro que declara la fuente.
                    </p>
                  </div>
                </div>
                <span className="px-2.5 py-1 rounded bg-slate-100 text-slate-600 text-xs font-mono shrink-0 whitespace-nowrap">
                  M horas/año
                </span>
              </div>

              {/* Recharts Component */}
              <div className="h-72 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={horasData} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                    <XAxis dataKey="name" stroke="#64748b" tick={{ fill: '#475569', fontSize: 12 }} />
                    <YAxis stroke="#64748b" tick={{ fill: '#475569', fontSize: 12 }} unit=" M h" />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="horas" radius={[8, 8, 0, 0]} barSize={55}>
                      {horasData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500 font-mono">
              <span>Ruta 40: 7,0 M h/año (Ponencia, dia. 29)</span>
              <span className="text-uni-600 font-bold">Ferropista: 1,7 M h/año</span>
            </div>
          </div>
        </motion.div>

        {/* Grouped Comparative Double BarChart Full Width */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.3 }}
          className="mt-8 rounded-3xl bg-white border border-slate-200 p-6 sm:p-8"
        >
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 pb-4 border-b border-slate-200 gap-2">
            <div>
              <h3 className="text-xl font-bold text-uni-900 flex items-center gap-2">
                <Activity className="w-5 h-5 text-gmae-600" />
                Reducción relativa por métrica
              </h3>
              <p className="text-xs text-slate-500">
                Cuánto baja cada indicador al pasar de la Ruta 40 a la Ferropista. Pasa el cursor para ver los valores absolutos.
              </p>
            </div>
            <span className="px-2.5 py-1 rounded bg-slate-100 text-slate-600 text-xs font-mono shrink-0">
              % de reducción [CP]
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={reduccionData}
                layout="vertical"
                margin={{ top: 10, right: 60, left: 10, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
                <XAxis
                  type="number"
                  domain={[0, 100]}
                  ticks={[0, 25, 50, 75, 100]}
                  unit=" %"
                  stroke="#64748b"
                  tick={{ fill: '#475569', fontSize: 12 }}
                />
                <YAxis
                  type="category"
                  dataKey="metrica"
                  width={150}
                  stroke="#64748b"
                  tick={{ fill: '#0f2449', fontSize: 13 }}
                />
                <Tooltip content={<TooltipReduccion />} cursor={{ fill: '#eef3fa' }} />
                <Bar dataKey="reduccion" fill="#0F7B55" radius={[0, 6, 6, 0]} barSize={38}>
                  <LabelList
                    dataKey="reduccion"
                    position="right"
                    formatter={(v: any) => `${Number(v).toFixed(1).replace('.', ',')} %`}
                    fill="#0f2449"
                    fontSize={13}
                    fontWeight={700}
                  />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <p className="mt-4 pt-4 border-t border-slate-200 text-[11px] text-slate-500 font-mono leading-relaxed">
            Las dos métricas están en unidades distintas (minutos y millones de horas/año), así que se
            grafica la reducción porcentual, que sí es comparable. Valores absolutos: 240 &rarr; 70 min
            (dia. 23 y 29) y 7,0 &rarr; 1,7 M h/año (dia. 29).
          </p>
        </motion.div>

      </div>
    </section>
  );
};
