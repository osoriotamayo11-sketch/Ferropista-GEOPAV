'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Mountain, ShieldCheck, Zap, Gauge, MapPin, Layers, FileText } from 'lucide-react';
import heroDictionary from '@/locales/hero.json';
import { TRAZADO, OPERACION } from '@/data/proyecto';

interface HeroProps {
  onOpenSpecs: () => void;
}

/* El sitio es monolingue en espanol. El diccionario se conserva porque
   agrupa los textos del hero en un solo lugar. */
export const Hero: React.FC<HeroProps> = ({ onOpenSpecs }) => {
  const dict = heroDictionary.es;

  return (
    <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden bg-slate-50 pt-12 pb-20 transition-colors duration-300">
      {/* Background Gradients & Grid */}
      <div className="absolute inset-0 bg-grid-pattern opacity-40 pointer-events-none" />
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[500px] bg-gradient-to-tr from-uni-200/40 via-uni-100/40 to-steel-700/10 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-slate-50 to-transparent pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10 w-full">
        <div className="grid lg:grid-cols-12 gap-12 items-center">
          
          {/* Main Hero Content with Framer Motion Slide-Up Animation */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className="lg:col-span-7 space-y-8 text-center lg:text-left"
          >
            {/* Top Tag/Badge */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-uni-50 border border-uni-200 text-uni-700 text-xs font-semibold tracking-wide uppercase">
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-gmae-500 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span>{dict.badge_tag}</span>
              <span className="text-uni-300">|</span>
              <span className="text-uni-600">{dict.badge_year}</span>
            </div>

            {/* Title */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-uni-900 leading-[1.1]">
              {dict.title_part1}{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-uni-700 via-uni-600 to-gmae-600">
                {dict.title_highlight}
              </span>{' '}
              {dict.title_part2}
            </h1>

            {/* Subtitle */}
            <p className="text-lg sm:text-xl text-slate-600 max-w-2xl font-light leading-relaxed">
              La <strong className="text-uni-900 font-semibold">{dict.subtitle_brand}</strong> {dict.subtitle_text}
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-2">
              <button
                onClick={onOpenSpecs}
                className="w-full sm:w-auto px-8 py-4 rounded-xl bg-uni-700 hover:bg-uni-600 text-white font-bold text-base shadow-xl shadow-engineering-900/25 transition-all duration-300 flex items-center justify-center gap-3 group border border-uni-500 active:scale-95"
              >
                <FileText className="w-5 h-5 text-uni-800 group-hover:scale-110 transition-transform" />
                <span>{dict.cta_specs}</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>

              <a
                href="#solucion"
                className="w-full sm:w-auto px-7 py-4 rounded-xl bg-white hover:bg-slate-100 text-slate-700 hover:text-uni-900 font-semibold text-base border border-slate-300/80 transition-all duration-300 flex items-center justify-center gap-2 group"
              >
                <span>{dict.cta_solution}</span>
                <Layers className="w-4 h-4 text-slate-500 group-hover:text-uni-600 transition-colors" />
              </a>
            </div>

            {/* Quick Metrics Bar */}
            <div className="pt-8 border-t border-slate-200 grid grid-cols-3 gap-4">
              <div className="space-y-1">
                <div className="text-2xl sm:text-3xl font-black text-uni-900 flex items-baseline justify-center lg:justify-start gap-1">
                  <span>{dict.metric1_val}</span>
                  <span className="text-sm font-semibold text-gmae-600">{dict.metric1_unit}</span>
                </div>
                <div className="text-xs text-slate-500 font-medium">{dict.metric1_label}</div>
              </div>
              
              <div className="space-y-1 border-x border-slate-200 px-2 sm:px-4">
                <div className="text-2xl sm:text-3xl font-black text-uni-900 flex items-baseline justify-center lg:justify-start gap-1">
                  <span>{dict.metric2_val}</span>
                  <span className="text-sm font-semibold text-uni-600">{dict.metric2_unit}</span>
                </div>
                <div className="text-xs text-slate-500 font-medium">{dict.metric2_label}</div>
              </div>

              <div className="space-y-1">
                <div className="text-2xl sm:text-3xl font-black text-uni-900 flex items-baseline justify-center lg:justify-start gap-1">
                  <span>{dict.metric3_val}</span>
                  <span className="text-sm font-semibold text-gmae-600">{dict.metric3_unit}</span>
                </div>
                <div className="text-xs text-slate-500 font-medium">{dict.metric3_label}</div>
              </div>
            </div>

          </motion.div>

          {/* Right Visual Element with Framer Motion Fade-In Scale Animation */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2, ease: 'easeOut' }}
            className="lg:col-span-5 relative"
          >
            <div className="relative rounded-2xl bg-gradient-to-b from-white via-white to-slate-50 p-6 sm:p-8 border border-slate-200 shadow-lg shadow-uni-900/10">
              
              {/* Card Header */}
              <div className="flex items-center justify-between pb-6 border-b border-slate-200">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-lg bg-uni-50 border border-uni-200 text-uni-700">
                    <MapPin className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-uni-900 text-base">Eje Interoceánico Bogotá – Buenaventura</h3>
                    <p className="text-xs text-slate-500">Sub-tramo crítico: Ibagué ↔ Armenia</p>
                  </div>
                </div>
                <span className="px-2.5 py-1 rounded bg-gmae-50 border border-gmae-200 text-gmae-700 text-xs font-mono font-semibold">
                  ESQUEMA PRELIMINAR
                </span>
              </div>

              {/* Visual Schema: Altitude profile comparison */}
              <div className="py-6 space-y-6">
                {/* Traditional Highway Route */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-red-700 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-red-500"></span>
                      Vía Convencional La Línea
                    </span>
                    <span className="text-slate-500 font-mono">Alta montaña (3.300 msnm · dia. 20)</span>
                  </div>
                  <div className="h-10 w-full bg-slate-50 rounded-lg p-2 flex items-center border border-red-500/20 relative overflow-hidden">
                    <svg className="w-full h-full text-red-500/60 stroke-current fill-none stroke-[2]" viewBox="0 0 300 30" preserveAspectRatio="none">
                      <path d="M0,25 Q40,5 80,28 T160,2 T240,25 T300,20" />
                    </svg>
                    <span className="absolute right-3 text-[10px] font-mono text-white bg-red-700 px-1.5 py-0.5 rounded border border-red-500/30">
                      4 h de cruce (dia. 29)
                    </span>
                  </div>
                </div>

                {/* Ferropista Tunnel Route */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-gmae-600 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-gmae-500 animate-pulse"></span>
                      Ferropista Cordillera Central
                    </span>
                    <span className="text-slate-500 font-mono">Portales: 950 y 1.450 msnm (dia. 20)</span>
                  </div>
                  <div className="h-12 w-full bg-slate-50 rounded-lg p-2 flex items-center border border-emerald-500/40 relative overflow-hidden bg-gradient-to-r from-uni-50 via-white to-gmae-50">
                    <div className="w-full h-2 bg-gradient-to-r from-blue-500 via-sky-400 to-emerald-400 rounded-full relative">
                      <div className="absolute -top-1 right-1/4 w-4 h-4 bg-gmae-500 rounded-full blur-[2px] animate-pulse"></div>
                    </div>
                    <span className="absolute right-3 text-[10px] font-mono text-white bg-gmae-600 px-2 py-0.5 rounded border border-emerald-500/40 font-bold">
                      Túnel base 58 km | 70 min (dia. 20 y 23)
                    </span>
                  </div>
                </div>
              </div>

              {/* Interactive Features List */}
              <div className="grid grid-cols-2 gap-3 pt-4 border-t border-slate-200 text-xs text-slate-600">
                <div className="flex items-center gap-2 bg-slate-50/60 p-2.5 rounded-lg border border-slate-200">
                  <Zap className="w-4 h-4 text-uni-500 shrink-0" />
                  <span>Autopista rodante Ro-Ro</span>
                </div>
                <div className="flex items-center gap-2 bg-slate-50/60 p-2.5 rounded-lg border border-slate-200">
                  <ShieldCheck className="w-4 h-4 text-gmae-600 shrink-0" />
                  <span>Pendiente media {TRAZADO.pendienteMedia.valor} [CP]</span>
                </div>
                <div className="flex items-center gap-2 bg-slate-50/60 p-2.5 rounded-lg border border-slate-200">
                  <Gauge className="w-4 h-4 text-uni-600 shrink-0" />
                  <span>Capacidad {OPERACION.capacidadDiaria.valor} [CP]</span>
                </div>
                <div className="flex items-center gap-2 bg-slate-50/60 p-2.5 rounded-lg border border-slate-200">
                  <Mountain className="w-4 h-4 text-acred-600 shrink-0" />
                  <span>Evita el paso a 3.300 msnm</span>
                </div>
              </div>

            </div>
          </motion.div>

        </div>
      </div>
    </section>
  );
};
