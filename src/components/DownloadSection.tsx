'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { FileText, ExternalLink, Clock, CheckCircle2, Circle, BookOpen } from 'lucide-react';
import { PLAN_ACCION, FUENTE_PRIMARIA, EQUIPO } from '@/data/proyecto';

export const DownloadSection: React.FC = () => {
  // Los entregables se derivan del Plan de Acción: no se anuncia nada que no esté planeado.
  const entregables = PLAN_ACCION
    .flatMap((oe) => oe.actividades
      .filter((a) => a.tipo === 'Producto')
      .map((a) => ({ oe: oe.numero, nombre: a.entregable, formato: a.formato, fin: a.fin, estado: a.estado })));

  const listos = entregables.filter((e) => e.estado === 'completado').length;

  return (
    <section id="entregables" className="py-20 bg-white relative overflow-hidden border-t border-slate-200">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-gradient-to-r from-blue-600/10 via-emerald-600/10 to-sky-600/10 blur-[140px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          className="relative rounded-3xl bg-gradient-to-br from-white via-white to-slate-50 p-8 sm:p-12 border border-slate-200 shadow-2xl overflow-hidden"
        >
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-uni-700 via-uni-600 to-uni-500" />

          <div className="space-y-8">

            <div className="space-y-4 max-w-3xl">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-uni-600 text-xs font-semibold uppercase tracking-wider">
                <FileText className="w-4 h-4" />
                <span>Entregables del semestre</span>
              </div>

              <h2 className="text-3xl sm:text-4xl font-extrabold text-uni-900 tracking-tight leading-tight">
                Qué vamos a publicar y cuándo
              </h2>

              <p className="text-base text-slate-600 font-light leading-relaxed">
                Todavía no hay documentos para descargar: el semestre apenas arranca. Esta es la lista de los{' '}
                {entregables.length} productos comprometidos en el Plan de Acción, con su fecha de entrega.
                Se irán publicando aquí a medida que se completen.
              </p>

              <div className="flex items-center gap-3 text-xs font-mono">
                <span className="text-gmae-600">{listos} publicados</span>
                <span className="text-slate-600">·</span>
                <span className="text-slate-500">{entregables.length - listos} en preparación</span>
              </div>
            </div>

            {/* Lista de entregables */}
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {entregables.map((e, i) => (
                <div
                  key={`${e.oe}-${i}`}
                  className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-start gap-3"
                >
                  {e.estado === 'completado'
                    ? <CheckCircle2 className="w-4 h-4 text-gmae-600 shrink-0 mt-0.5" />
                    : <Circle className="w-4 h-4 text-slate-600 shrink-0 mt-0.5" />}
                  <div className="min-w-0 space-y-1">
                    <p className="text-xs font-semibold text-slate-700 leading-snug">{e.nombre}</p>
                    <p className="text-[10px] text-slate-500 font-mono">
                      OE {e.oe} · {e.formato}
                    </p>
                    <p className="text-[10px] text-slate-500 font-mono inline-flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {e.fin}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Fuente real */}
            <div className="rounded-2xl bg-slate-50 border border-slate-200 p-5 sm:p-6 space-y-3">
              <div className="flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-uni-600" />
                <h3 className="text-sm font-bold text-slate-700">
                  ¿Buscas la propuesta original, no nuestro análisis?
                </h3>
              </div>
              <p className="text-xs text-slate-500 leading-relaxed">
                La Ferropista es una iniciativa privada de {FUENTE_PRIMARIA.proponentes}. Este sitio es
                un trabajo académico del {EQUIPO.semillero} que la estudia desde fuera; no representamos
                a sus proponentes ni hablamos por ellos. La información oficial del proyecto está en su
                propio sitio.
              </p>
              <a
                href={FUENTE_PRIMARIA.sitio}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-xs font-semibold text-uni-600 hover:text-uni-700 transition-colors"
              >
                ferropista.com
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
              <p className="text-[11px] text-slate-500 leading-relaxed pt-3 border-t border-slate-200">
                {FUENTE_PRIMARIA.cita}
              </p>
            </div>

          </div>
        </motion.div>
      </div>
    </section>
  );
};
