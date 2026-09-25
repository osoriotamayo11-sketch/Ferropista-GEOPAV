'use client';

/**
 * SintesisOE2 — la sección del objetivo específico 2 en la portada.
 *
 * El OE 2 es el único objetivo cuyo producto está vivo mientras el semestre corre:
 * la consulta ciudadana. Por eso esta sección no presenta resultados —todavía no
 * los hay— sino una invitación a participar y la declaración de qué se pregunta y
 * qué no se guarda. Los resultados llegarán cuando cierre la ventana de recolección.
 *
 * Instrumento vigente: el OFICIAL, avalado por la entidad receptora (versión
 * 'oficial-2026-09'). Eso se dice aquí y se repite en la propia página de la
 * consulta.
 */

import React from 'react';
import { motion } from 'framer-motion';
import {
  Users, CheckCircle2, Circle, Loader2, ArrowRight, ShieldCheck, ListChecks, Clock,
  FolderOpen, ExternalLink,
} from 'lucide-react';
import { PLAN_ACCION, EQUIPO, type EstadoItem } from '@/data/proyecto';
import Acordeon from './Acordeon';

/**
 * Carpetas de Google Drive de las cinco actividades del OE 2, en orden de actividad.
 * Son las mismas que el Google Sheet oficial referencia en su columna
 * «Carpeta de Google Drive». Verificadas abiertas sin sesión el 18 sep 2026.
 */
const DRIVE_URLS_OE2 = [
  'https://drive.google.com/drive/folders/1Uc76S1A3TmD2-JeTnOtIvp6m_0Q-Lc2v',
  'https://drive.google.com/drive/folders/1tjaDUkU04ZWvX1MJH0XkPW2ZC0N7DDOB',
  'https://drive.google.com/drive/folders/1AJJXG6WE2qvNJ0cYZ_7_HOOXxNpmGTkH',
  'https://drive.google.com/drive/folders/1oU26wwyBRw1DdW8M_H1sQpqBcyyB8XRd',
  'https://drive.google.com/drive/folders/1avkuU9JmbhRok1t_EEgyH4hBSkaEi0AW',
];

const ESTADO_UI: Record<EstadoItem, { texto: string; clase: string; Icono: React.ComponentType<{ className?: string }> }> = {
  completado: { texto: 'Completado', clase: 'bg-gmae-50 text-gmae-700 border-gmae-300', Icono: CheckCircle2 },
  en_curso:   { texto: 'En curso',   clase: 'bg-uni-50 text-uni-700 border-uni-200',    Icono: Loader2 },
  pendiente:  { texto: 'Pendiente',  clase: 'bg-slate-100 text-slate-600 border-slate-300', Icono: Circle },
};

const BadgeEstado: React.FC<{ estado: EstadoItem }> = ({ estado }) => {
  const { texto, clase, Icono } = ESTADO_UI[estado];
  return (
    <span className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full border ${clase}`}>
      <Icono className={`w-3 h-3 ${estado === 'en_curso' ? 'animate-spin' : ''}`} />
      {texto}
    </span>
  );
};

/* Los bloques del cuestionario oficial, en el mismo orden en que se presentan en
   /consulta. Si allí cambian, aquí también: es la promesa que se le hace a quien
   decide si entra o no. Preguntas: OE2_Plataforma/Act3_Instrumento/instrumento_oficial_2026-09.json */
const BLOQUES_CONSULTA = [
  { letra: 'A', titulo: 'Su relación con el corredor', detalle: 'Si conduce carga, es particular, comerciante, residente o trabajador de la zona; con qué frecuencia usa el corredor.' },
  { letra: 'B', titulo: 'Conocimiento y opinión sobre la Ferropista', detalle: 'Qué tanto conoce la propuesta y su opinión sobre movilidad, seguridad vial, economía, empleo y confianza en el proyecto.' },
  { letra: 'C', titulo: 'Preguntas según su perfil', detalle: 'Dos preguntas adicionales para transportadores de carga, particulares, residentes o comerciantes.' },
  { letra: 'D', titulo: 'Lo que quiera añadir', detalle: 'Dos preguntas abiertas y opcionales sobre el principal beneficio y el principal impacto negativo que espera.' },
];

const NO_SE_GUARDA = [
  'Nombre, cédula, teléfono o correo: no se piden en ninguna pregunta.',
  'Dirección IP o identificador de dispositivo: el servidor no lee ninguna cabecera de red, y así está escrito en el código publicado.',
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
            El único dato que no sale de un archivo
          </h2>
          <p className="text-base sm:text-lg text-slate-500 leading-relaxed">
            Todo lo demás de este sitio se calcula sobre datos publicados por INVÍAS, la ANSV,
            la ANI y un modelo de elevación. Falta lo que ninguna entidad mide: qué tanto
            conocen y qué opinan de la propuesta de la Ferropista quienes usan y habitan el
            corredor. Esta consulta lo pregunta directamente, y es el único dato primario
            del proyecto.
          </p>
        </div>

        {/* 1. Estado del objetivo */}
        <div className="rounded-2xl bg-white border border-gmae-300/60 p-6 sm:p-8 mb-6">
          <div className="flex flex-wrap items-center gap-3 mb-4">
            <BadgeEstado estado={oe2.estado} />
            <span className="text-[11px] font-mono text-slate-500">{oe2.inicio} → {oe2.fin}</span>
            <span className="text-[11px] text-slate-500">· Responsable: {oe2.responsable}</span>
          </div>
          <p className="text-sm text-slate-700 leading-relaxed mb-5">{oe2.titulo}</p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-3">
            {oe2.actividades.map((a, i) => {
              const { Icono } = ESTADO_UI[a.estado];
              const tinte = a.estado === 'completado' ? 'text-gmae-600'
                : a.estado === 'en_curso' ? 'text-uni-600' : 'text-slate-400';
              return (
                <a
                  key={a.n}
                  href={DRIVE_URLS_OE2[i]}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group flex flex-col rounded-xl bg-slate-50 border border-slate-200 p-3 space-y-1.5 hover:border-uni-300 hover:bg-white transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono text-slate-500">Act {a.n}</span>
                    <Icono className={`w-3.5 h-3.5 ${tinte} ${a.estado === 'en_curso' ? 'animate-spin' : ''}`} />
                  </div>
                  <p className="text-[11px] text-slate-600 leading-snug">{a.entregable}</p>
                  <p className="text-[10px] font-mono text-slate-400">{a.inicio} → {a.fin}</p>
                  <span className="flex items-center gap-1.5 pt-1.5 mt-auto border-t border-slate-200 text-[10px] font-semibold text-uni-700">
                    <FolderOpen className="w-3 h-3 shrink-0" />
                    Ver evidencia en Drive
                    <ExternalLink className="w-2.5 h-2.5 shrink-0 text-slate-400 group-hover:text-uni-600" />
                  </span>
                </a>
              );
            })}
          </div>
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

        {/* 3. Qué se pregunta, plegado */}
        <div className="mb-4">
          <Acordeon
            titulo="Qué se pregunta"
            resumen="Los bloques del cuestionario, en el mismo orden en que aparecen."
            icono={<ListChecks className="h-5 w-5 text-uni-600" />}
            contador={`${BLOQUES_CONSULTA.length} bloques`}
          >
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {BLOQUES_CONSULTA.map((b) => (
                <div key={b.letra} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                  <p className="font-mono text-[11px] font-bold text-uni-700">Bloque {b.letra}</p>
                  <p className="mt-0.5 text-xs font-semibold leading-snug text-slate-700">{b.titulo}</p>
                  <p className="mt-1.5 text-[11px] leading-relaxed text-slate-500">{b.detalle}</p>
                </div>
              ))}
            </div>
          </Acordeon>
        </div>

        {/* 4. Qué no se guarda, plegado */}
        <Acordeon
          titulo="Qué no se guarda"
          resumen="Lo que la consulta no recoge, y por qué se puede comprobar en vez de creerlo."
          icono={<ShieldCheck className="h-5 w-5 text-gmae-600" />}
          contador={`${NO_SE_GUARDA.length} puntos`}
          tono="gris"
        >
          <ul className="max-w-4xl space-y-2.5 text-xs leading-relaxed text-slate-600">
            {NO_SE_GUARDA.map((n) => (
              <li key={n} className="flex gap-2">
                <span className="shrink-0 text-slate-400">·</span>
                <span>{n}</span>
              </li>
            ))}
          </ul>
          <p className="mt-4 border-t border-slate-200 pt-3 text-[11px] leading-relaxed text-slate-500">
            Las respuestas se almacenan con seguridad a nivel de fila: quien visita el sitio
            puede depositar una respuesta y no puede leer ninguna, ni la suya. Se publican
            siempre agregadas, nunca individuales. Trabajo del {EQUIPO.semillero},{' '}
            {EQUIPO.universidad}.
          </p>
        </Acordeon>

      </div>
    </section>
  );
};
