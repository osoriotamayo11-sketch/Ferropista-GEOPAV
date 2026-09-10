'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  ClipboardList, Target, CalendarDays, User, CheckCircle2, Circle, Loader2,
  ChevronDown, FileText, AlertTriangle, Globe,
} from 'lucide-react';
import {
  PLAN_ACCION, OBJETIVO_GENERAL, BLOQUES, NOTA_PARALELISMO, ODS, LIMITACIONES,
  EQUIPO, type ObjetivoEspecifico, type EstadoItem,
} from '@/data/proyecto';

const ESTADO_UI: Record<EstadoItem, { texto: string; clase: string; Icono: React.ElementType }> = {
  completado: { texto: 'Completado', clase: 'bg-gmae-50 text-gmae-700 border-gmae-300', Icono: CheckCircle2 },
  en_curso:   { texto: 'En curso',   clase: 'bg-uni-50 text-uni-700 border-uni-200',       Icono: Loader2 },
  pendiente:  { texto: 'Pendiente',  clase: 'bg-slate-100 text-slate-600 border-slate-300',    Icono: Circle },
};

const COLOR_BLOQUE: Record<number, string> = {
  1: 'text-uni-600 bg-blue-500/10 border-blue-500/30',
  2: 'text-acred-600 bg-amber-500/10 border-amber-500/30',
  3: 'text-gmae-600 bg-emerald-500/10 border-emerald-500/30',
};

const Badge: React.FC<{ estado: EstadoItem }> = ({ estado }) => {
  const { texto, clase, Icono } = ESTADO_UI[estado];
  return (
    <span className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full border ${clase}`}>
      <Icono className={`w-3 h-3 ${estado === 'en_curso' ? 'animate-spin' : ''}`} />
      {texto}
    </span>
  );
};

const TarjetaObjetivo: React.FC<{ oe: ObjetivoEspecifico }> = ({ oe }) => {
  const [abierto, setAbierto] = useState(oe.estado === 'en_curso');
  const productos = oe.actividades.filter((a) => a.tipo === 'Producto').length;

  return (
    <div className="rounded-2xl bg-slate-50 border border-slate-200 overflow-hidden">
      <button
        onClick={() => setAbierto((v) => !v)}
        className="w-full text-left p-5 hover:bg-white transition-colors"
        aria-expanded={abierto}
      >
        <div className="flex items-start gap-4">
          <div className="shrink-0 w-11 h-11 rounded-xl bg-white border border-slate-200 flex flex-col items-center justify-center">
            <span className="text-[9px] font-mono text-slate-500 leading-none">OE</span>
            <span className="text-lg font-black text-uni-900 leading-none">{oe.numero}</span>
          </div>

          <div className="flex-1 min-w-0 space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <Badge estado={oe.estado} />
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${COLOR_BLOQUE[oe.bloque]}`}>
                Bloque {oe.bloque}
              </span>
              <span className="text-[10px] font-mono text-slate-500">{oe.inicio} → {oe.fin}</span>
            </div>

            <p className="text-sm text-slate-700 leading-relaxed">{oe.titulo}</p>

            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-slate-500">
              <span className="inline-flex items-center gap-1.5">
                <User className="w-3.5 h-3.5 text-slate-500" />
                {oe.responsable}
              </span>
              <span className="text-slate-600">·</span>
              <span>{oe.linea}</span>
              <span className="text-slate-600">·</span>
              <span>{oe.actividades.length} actividades · {productos} productos</span>
            </div>
          </div>

          <ChevronDown className={`w-5 h-5 text-slate-500 shrink-0 transition-transform ${abierto ? 'rotate-180' : ''}`} />
        </div>
      </button>

      {abierto && (
        <div className="border-t border-slate-200 divide-y divide-slate-200/60">
          {oe.actividades.map((a) => (
            <div key={a.n} className="p-4 pl-5 sm:pl-20 flex flex-col sm:flex-row sm:items-start gap-3">
              <div className="shrink-0 flex items-center gap-2 sm:w-16">
                <span className="text-[10px] font-mono text-slate-500">Act {a.n}</span>
              </div>
              <div className="flex-1 min-w-0 space-y-1.5">
                <p className="text-xs text-slate-600 leading-relaxed">{a.titulo}</p>
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[10px] text-slate-500 font-mono">
                  <span>{a.inicio} → {a.fin}</span>
                  <span className={a.tipo === 'Producto' ? 'text-acred-600/90 font-bold' : 'text-violet-400/80'}>
                    {a.tipo}
                  </span>
                  <span className="inline-flex items-center gap-1">
                    <FileText className="w-3 h-3" />
                    {a.entregable} · {a.formato}
                  </span>
                </div>
              </div>
              <div className="shrink-0"><Badge estado={a.estado} /></div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export const PlanDeAccion: React.FC = () => {
  const total = PLAN_ACCION.reduce((s, o) => s + o.actividades.length, 0);
  const productos = PLAN_ACCION.reduce((s, o) => s + o.actividades.filter((a) => a.tipo === 'Producto').length, 0);
  const porBloque = (n: number) => PLAN_ACCION.filter((o) => o.bloque === n);

  return (
    <section id="plan" className="py-24 bg-white relative overflow-hidden border-t border-b border-slate-200">
      <div className="absolute top-1/4 left-0 w-96 h-96 bg-blue-600/5 blur-[130px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-emerald-600/5 blur-[130px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">

        {/* Encabezado */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-uni-600 text-xs font-semibold uppercase tracking-wider">
            <ClipboardList className="w-3.5 h-3.5" />
            <span>Plan de Acción · {EQUIPO.programa}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-uni-900 tracking-tight">
            Cómo vamos a estudiar esta propuesta
          </h2>
          <p className="text-base sm:text-lg text-slate-500 leading-relaxed">
            Este sitio es el cuaderno de trabajo público del {EQUIPO.semillero} de la {EQUIPO.universidad}.
            Aquí queda visible qué nos comprometimos a hacer, quién responde por cada frente y en qué va cada cosa.
          </p>
        </div>

        {/* Objetivo general */}
        <div className="rounded-2xl bg-slate-50 border border-blue-500/25 p-6 sm:p-8 mb-10">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-blue-600/10 border border-blue-500/30 text-uni-600 shrink-0">
              <Target className="w-6 h-6" />
            </div>
            <div className="space-y-2">
              <h3 className="text-sm font-bold text-slate-600 uppercase tracking-wider">Objetivo general</h3>
              <p className="text-base text-slate-800 leading-relaxed">{OBJETIVO_GENERAL}</p>
              <p className="text-xs text-slate-500 leading-relaxed pt-2 border-t border-slate-200">
                El verbo es <span className="text-slate-600 font-semibold">analizar</span>, no evaluar la viabilidad.
                La evaluación de viabilidad de una obra de US$ 2.800 millones es un estudio de prefactibilidad que ya
                hizo el proponente y que excede el alcance de un semillero en un semestre. Lo que aportamos es
                caracterización propia y verificación independiente de sus órdenes de magnitud.
              </p>
            </div>
          </div>
        </div>

        {/* Cifras del plan */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
          {[
            { v: '7',  l: 'objetivos específicos', s: '2 por integrante + 1 conjunto' },
            { v: String(total), l: 'actividades',  s: 'mínimo 5 por objetivo' },
            { v: String(productos), l: 'productos', s: 'mínimo 1 por objetivo' },
            { v: '3',  l: 'integrantes',           s: 'Ingeniería Civil' },
          ].map((k) => (
            <div key={k.l} className="rounded-xl bg-slate-50 border border-slate-200 p-4 text-center">
              <span className="block text-3xl font-black text-uni-900">{k.v}</span>
              <span className="block text-xs text-slate-600 font-semibold mt-1">{k.l}</span>
              <span className="block text-[10px] text-slate-500 mt-0.5">{k.s}</span>
            </div>
          ))}
        </div>

        {/* Bloques del cronograma */}
        <div className="grid md:grid-cols-3 gap-4 mb-4">
          {BLOQUES.map((b) => (
            <div key={b.n} className={`rounded-xl border p-4 ${COLOR_BLOQUE[b.n]} bg-slate-50`}>
              <div className="flex items-center gap-2 mb-1">
                <CalendarDays className="w-4 h-4" />
                <span className="text-sm font-bold">Bloque {b.n}</span>
              </div>
              <p className="text-xs font-mono text-slate-600">{b.rango}</p>
              <p className="text-[11px] text-slate-500 mt-1.5 leading-relaxed">{b.descripcion}</p>
              <p className="text-[11px] text-slate-500 mt-2 pt-2 border-t border-slate-200">
                {porBloque(b.n).map((o) => `OE ${o.numero}`).join(' · ')}
              </p>
            </div>
          ))}
        </div>
        <p className="text-xs text-slate-500 leading-relaxed mb-10 max-w-3xl">{NOTA_PARALELISMO}</p>

        {/* Objetivos específicos */}
        <h3 className="text-lg font-bold text-uni-900 mb-4">Objetivos específicos y estado</h3>
        <div className="space-y-3 mb-12">
          {PLAN_ACCION.slice().sort((a, b) => a.numero - b.numero).map((oe, i) => (
            <motion.div
              key={oe.id}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.35, delay: i * 0.04 }}
            >
              <TarjetaObjetivo oe={oe} />
            </motion.div>
          ))}
        </div>

        {/* ODS */}
        <div className="rounded-2xl bg-slate-50 border border-slate-200 p-6 sm:p-8 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Globe className="w-5 h-5 text-gmae-600" />
            <h3 className="text-lg font-bold text-uni-900">Objetivos de Desarrollo Sostenible</h3>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-3">
            {ODS.map((o) => (
              <div key={o.n} className="p-3 rounded-xl bg-white border border-slate-200">
                <span className="block text-2xl font-black text-gmae-600">{o.n}</span>
                <span className="block text-xs font-semibold text-slate-700 mt-1">{o.nombre}</span>
                <span className="block text-[11px] text-slate-500 mt-1.5 leading-relaxed">{o.relacion}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Limitaciones */}
        <div className="rounded-2xl bg-amber-500/5 border border-amber-500/25 p-6 sm:p-8">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-5 h-5 text-acred-600" />
            <h3 className="text-lg font-bold text-uni-900">Limitaciones que declaramos de entrada</h3>
          </div>
          <p className="text-xs text-slate-500 mb-4 leading-relaxed max-w-3xl">
            Declarar los límites del alcance antes de empezar es lo que separa un trabajo académico serio de una
            repetición acrítica de la fuente. Estas son las nuestras.
          </p>
          <ul className="space-y-2.5">
            {LIMITACIONES.map((l, i) => (
              <li key={i} className="flex gap-3 text-xs text-slate-600 leading-relaxed">
                <span className="shrink-0 text-acred-600 font-mono">{String(i + 1).padStart(2, '0')}</span>
                <span>{l}</span>
              </li>
            ))}
          </ul>
        </div>

      </div>
    </section>
  );
};
