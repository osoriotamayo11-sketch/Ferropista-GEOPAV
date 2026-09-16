'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Mountain, ShieldCheck, Zap, Gauge, MapPin } from 'lucide-react';
import heroDictionary from '@/locales/hero.json';
import { TRAZADO, OPERACION } from '@/data/proyecto';
import EsquemaHero3D from './EsquemaHero3D';

/* El sitio es monolingue en espanol. El diccionario se conserva porque
   agrupa los textos del hero en un solo lugar. */
export const Hero: React.FC = () => {
  const dict = heroDictionary.es;

  return (
    <section className="relative overflow-hidden bg-slate-50 pt-16 pb-20 transition-colors duration-300">
      {/* Fondos */}
      <div className="absolute inset-0 bg-grid-pattern opacity-40 pointer-events-none" />
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[500px] bg-gradient-to-tr from-uni-200/40 via-uni-100/40 to-steel-700/10 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-slate-50 to-transparent pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10 w-full space-y-12">

        {/* Titular */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="mx-auto max-w-4xl space-y-7 text-center"
        >
          <h1 className="text-balance text-4xl font-extrabold leading-[1.1] tracking-tight text-uni-900 sm:text-5xl lg:text-6xl">
            {dict.title_part1}{' '}
            <span className="bg-gradient-to-r from-uni-700 via-uni-600 to-gmae-600 bg-clip-text text-transparent">
              {dict.title_highlight}
            </span>{' '}
            {dict.title_part2}
          </h1>

          {/* Filete corto: cierra el titular y marca el eje de simetría */}
          <div className="mx-auto h-1 w-24 rounded-full bg-gradient-to-r from-uni-600 to-gmae-500" />

          <p className="mx-auto max-w-2xl text-pretty text-base font-light leading-relaxed text-slate-600 sm:text-lg">
            La <strong className="font-semibold text-uni-900">{dict.subtitle_brand}</strong> {dict.subtitle_text}
          </p>

          {/* Métricas rápidas. Cada una conserva su diapositiva de origen. */}
          <div className="mx-auto grid max-w-3xl grid-cols-1 gap-y-6 divide-y divide-slate-200 border-t border-slate-200 pt-8 sm:grid-cols-3 sm:gap-y-0 sm:divide-x sm:divide-y-0">
            <div className="space-y-1.5 px-2 pt-6 sm:pt-0">
              <div className="flex items-baseline justify-center gap-1.5 text-3xl font-black text-uni-900 sm:text-4xl">
                <span>{dict.metric1_val}</span>
                <span className="text-sm font-semibold text-gmae-600">{dict.metric1_unit}</span>
              </div>
              <div className="mx-auto max-w-[26ch] text-xs font-medium leading-snug text-slate-500">
                {dict.metric1_label}
              </div>
            </div>

            <div className="space-y-1.5 px-2 pt-6 sm:pt-0">
              <div className="flex items-baseline justify-center gap-1.5 text-3xl font-black text-uni-900 sm:text-4xl">
                <span>{dict.metric2_val}</span>
                <span className="text-sm font-semibold text-uni-600">{dict.metric2_unit}</span>
              </div>
              <div className="mx-auto max-w-[26ch] text-xs font-medium leading-snug text-slate-500">
                {dict.metric2_label}
              </div>
            </div>

            <div className="space-y-1.5 px-2 pt-6 sm:pt-0">
              <div className="flex items-baseline justify-center gap-1.5 text-3xl font-black text-uni-900 sm:text-4xl">
                <span>{dict.metric3_val}</span>
                <span className="text-sm font-semibold text-gmae-600">{dict.metric3_unit}</span>
              </div>
              <div className="mx-auto max-w-[26ch] text-xs font-medium leading-snug text-slate-500">
                {dict.metric3_label}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Ficha del eje, en horizontal para que los esquemas respiren */}
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.15, ease: 'easeOut' }}
        >
          <div className="relative rounded-2xl bg-gradient-to-b from-white via-white to-slate-50 p-6 sm:p-8 border border-slate-200 shadow-lg shadow-uni-900/10">

            {/* Encabezado de la ficha.
                El rótulo "Esquema preliminar" pasa a chip alineado a la derecha:
                califica toda la ficha, no es una tercera línea del título. */}
            <div className="flex flex-col gap-3 border-b border-slate-200 pb-5 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-3.5">
                <div className="shrink-0 rounded-xl border border-uni-200 bg-uni-50 p-3 text-uni-700">
                  <MapPin className="h-5 w-5" />
                </div>
                <div className="space-y-0.5">
                  <h3 className="text-base font-bold leading-tight text-uni-900 sm:text-lg">
                    Eje Interoceánico Bogotá – Buenaventura
                  </h3>
                  <p className="flex items-center gap-1.5 text-xs text-slate-500">
                    <span className="font-medium text-slate-600">Sub-tramo crítico</span>
                    <span className="text-slate-300">│</span>
                    <span className="font-mono">Ibagué ↔ Armenia</span>
                  </p>
                </div>
              </div>

              <span className="inline-flex w-fit items-center gap-1.5 self-start rounded-full border border-gmae-200 bg-gmae-50 px-3 py-1 font-mono text-[10px] font-semibold uppercase tracking-wider text-gmae-700 sm:self-auto">
                <span className="h-1.5 w-1.5 rounded-full bg-gmae-500" />
                Esquema preliminar
              </span>
            </div>

            {/* Los dos modos de cruce, uno al lado del otro.
                Las escenas son esquemas ilustrativos: el relieve es procedural
                y no proviene del modelo de elevacion. El terreno real, levantado
                del DEM, esta en la seccion del objetivo especifico 1. */}
            <div className="grid gap-6 py-6 lg:grid-cols-2">
              <div className="space-y-2">
                <div className="flex flex-wrap justify-between gap-x-3 text-xs font-medium">
                  <span className="text-red-700 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-red-500"></span>
                    Vía Convencional La Línea
                  </span>
                  <span className="text-slate-500 font-mono">Alta montaña (3.300 msnm · dia. 20)</span>
                </div>
                <EsquemaHero3D
                  scenario="convencional"
                  badge="4 h de cruce (dia. 29)"
                  badgeClassName="bg-red-700 border-red-500/30"
                  height={300}
                />
              </div>

              <div className="space-y-2">
                <div className="flex flex-wrap justify-between gap-x-3 text-xs font-medium">
                  <span className="text-gmae-600 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-gmae-500 animate-pulse"></span>
                    Ferropista Cordillera Central
                  </span>
                  <span className="text-slate-500 font-mono">Portales: 950 y 1.450 msnm (dia. 20)</span>
                </div>
                <EsquemaHero3D
                  scenario="ferropista"
                  badge="Túnel base 58 km · 30 min de cruce (dia. 20 y 23)"
                  badgeClassName="bg-gmae-600 border-emerald-500/40 font-bold"
                  height={300}
                />
              </div>
            </div>

            {/* Parámetros */}
            <div className="grid grid-cols-2 gap-3 pt-4 border-t border-slate-200 text-xs text-slate-600 lg:grid-cols-4">
              <div className="flex items-center gap-2 bg-slate-50/60 p-2.5 rounded-lg border border-slate-200">
                <Zap className="w-4 h-4 text-uni-500 shrink-0" />
                <span>Tractomulas sobre plataformas (dia. 23)</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-50/60 p-2.5 rounded-lg border border-slate-200">
                <ShieldCheck className="w-4 h-4 text-gmae-600 shrink-0" />
                <span>Pendiente media {TRAZADO.pendienteMedia.valor} [{TRAZADO.pendienteMedia.marca}]</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-50/60 p-2.5 rounded-lg border border-slate-200">
                <Gauge className="w-4 h-4 text-uni-600 shrink-0" />
                <span>{OPERACION.capacidadDiaria.valor} [{OPERACION.capacidadDiaria.marca}]</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-50/60 p-2.5 rounded-lg border border-slate-200">
                <Mountain className="w-4 h-4 text-acred-600 shrink-0" />
                <span>Evita el paso a 3.300 msnm</span>
              </div>
            </div>

            <p className="pt-3 text-[11px] leading-snug text-slate-500">
              El ciclo declarado por la ponencia es de 70 min: 25 de cargue, 30 de cruce y
              15 de descargue (dia. 23). El cruce del túnel es la fracción de 30 min.
            </p>

          </div>
        </motion.div>

      </div>
    </section>
  );
};
