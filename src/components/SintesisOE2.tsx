'use client';

/**
 * SintesisOE2 — la sección del objetivo específico 2 en la portada.
 *
 * El OE 2 es el único objetivo cuyo producto está vivo mientras el semestre corre:
 * la consulta ciudadana. Por eso esta sección no presenta resultados —todavía no
 * los hay— sino qué es la consulta, qué mide, cómo se responde y para qué sirve,
 * más la invitación a participar. Los resultados llegarán cuando cierre la
 * ventana de recolección.
 *
 * Instrumento vigente: el OFICIAL, avalado por la entidad receptora (versión
 * 'oficial-2026-09'). Eso se dice aquí y se repite en la propia página de la
 * consulta.
 */

import React from 'react';
import { motion } from 'framer-motion';
import {
  Users, ArrowRight, ShieldCheck, ListChecks, Clock,
} from 'lucide-react';
import { PLAN_ACCION } from '@/data/proyecto';
import { METODO_OE } from '@/data/metodo_oe';
import ComoSeHizo from './ComoSeHizo';

/* Los cuatro puntos de "Qué es la consulta", en el mismo orden en que se
   presentan al visitante. Texto acordado con el equipo; no son cifras sueltas
   sino la descripción del instrumento, así que no pasan por proyecto.ts. */
const QUE_ES_LA_CONSULTA = [
  {
    titulo: 'Qué es',
    texto: 'Una encuesta en línea y anónima para quienes usan o habitan el corredor Ibagué – Armenia: conductores de vehículos de carga y particulares, residentes, comerciantes y trabajadores de la zona.',
  },
  {
    titulo: 'Qué mide',
    texto: 'Qué tanto se conoce la propuesta de la Ferropista y cómo se perciben sus efectos: movilidad, seguridad vial, desarrollo económico y empleo, las posibles afectaciones a quienes hoy viven del tránsito de carga, y el grado de aceptación del proyecto.',
  },
  {
    titulo: 'Cómo',
    texto: '17 preguntas: 2 sobre el uso del corredor, 11 en escala de acuerdo, 2 según el perfil (carga, particular, residente o comerciante) y 2 abiertas sobre el principal beneficio y el principal impacto. Toma unos cinco minutos.',
  },
  {
    titulo: 'Para qué',
    texto: 'Es el único dato primario del proyecto: recoge la voz de los usuarios del corredor, que ninguna entidad mide. Sus resultados se contrastan con la siniestralidad del OE 5 y alimentan la integración del OE 7. Recibe respuestas hasta el 3 de octubre de 2026.',
  },
];

export const SintesisOE2: React.FC = () => {
  const oe2 = PLAN_ACCION.find((o) => o.id === 'oe2');
  if (!oe2) return null;

  return (
    <section id="oe2" className="py-24 bg-white relative overflow-hidden border-t border-slate-200">
      <div className="absolute top-1/3 right-0 w-[500px] h-[400px] bg-gmae-600/5 blur-[130px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-uni-600/5 blur-[130px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">

        {/* Encabezado */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-gmae-600 text-xs font-semibold uppercase tracking-wider">
            <Users className="w-3.5 h-3.5" />
            <span>Objetivo específico 2 · Plataforma y consulta ciudadana</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-uni-900 tracking-tight">
            Qué es la consulta
          </h2>
        </div>

        {/* Qué es la consulta: los cuatro puntos, textuales */}
        <div className="mb-10 grid gap-4 sm:grid-cols-2">
          {QUE_ES_LA_CONSULTA.map((p) => (
            <div key={p.titulo} className="rounded-xl border border-slate-200 bg-slate-50 p-4 sm:p-5">
              <p className="text-xs font-bold uppercase tracking-wide text-uni-700">{p.titulo}</p>
              <p className="mt-1.5 text-sm leading-relaxed text-slate-600">{p.texto}</p>
            </div>
          ))}
        </div>

        {/* 2. La llamada a participar */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-60px' }}
          transition={{ duration: 0.4 }}
          className="rounded-2xl border border-uni-200 bg-uni-50 p-6 sm:p-8 mb-6"
        >
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-2xl space-y-3">
              <h3 className="text-xl sm:text-2xl font-bold text-uni-900">
                Si cruza el Alto de La Línea, su respuesta hace falta
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Transportadores, conductores y habitantes de Ibagué, Coello, Cajamarca y
                Calarcá. Es anónima, son unos cinco minutos, y no se piden datos de contacto
                de ninguna clase.
              </p>
              <div className="flex flex-wrap gap-x-5 gap-y-2 pt-1">
                <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-slate-600">
                  <Clock className="w-3.5 h-3.5 text-uni-600 shrink-0" /> Unos 5 minutos
                </span>
                <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-slate-600">
                  <ShieldCheck className="w-3.5 h-3.5 text-gmae-600 shrink-0" /> Anónima, sin datos de contacto
                </span>
                <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-slate-600">
                  <ListChecks className="w-3.5 h-3.5 text-uni-600 shrink-0" /> 17 preguntas, según su perfil
                </span>
              </div>
            </div>

            <a
              href="/consulta"
              className="group inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-uni-700 px-6 py-4 text-sm font-bold text-white transition-colors hover:bg-uni-800"
            >
              Responder la consulta
              <ArrowRight className="h-4 w-4 shrink-0 transition-transform group-hover:translate-x-0.5" />
            </a>
          </div>

          <p className="mt-6 border-t border-uni-200 pt-4 text-[11px] leading-relaxed text-slate-500">
            El cuestionario vigente es el instrumento oficial, avalado por la entidad
            receptora. Cada respuesta queda marcada con la versión que la produjo, de modo
            que las respuestas recogidas con el instrumento anterior se analizan aparte y
            nunca se mezclan en silencio con estas.
          </p>
        </motion.div>

        <div className="mb-4">
          <ComoSeHizo
            porQue={METODO_OE.oe2.porQue}
            paraQue={METODO_OE.oe2.paraQue}
            como={METODO_OE.oe2.como}
            noAfirma={METODO_OE.oe2.noAfirma}
            resumen="Por qué existe la consulta, el instrumento que usa, el calendario y qué no puede concluirse de sus respuestas."
          />
        </div>

      </div>
    </section>
  );
};
