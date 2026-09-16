'use client';

/**
 * Consulta ciudadana de percepción de riesgo vial — objetivo específico 2.
 *
 * Único instrumento de dato primario del proyecto. Alimenta el OE 5 y el OE 7.
 *
 * Estado: ABIERTA desde el 15 sep 2026. Las respuestas se guardan en Supabase y
 * quedan marcadas con la versión del cuestionario (ver src/app/api/consulta/route.ts).
 *
 * El instrumento vigente es el borrador propio del semillero: el oficial, avalado
 * por la interlocutora, todavía no ha llegado. Eso se declara en pantalla, porque
 * quien responde tiene derecho a saber en qué estado está lo que está contestando.
 * Cuando llegue el oficial se sustituyen las preguntas y se cambia la versión; las
 * respuestas ya recogidas no se tocan ni se mezclan en silencio.
 */

import React, { useState } from 'react';
import { ShieldAlert, Check, AlertTriangle, Send, Info } from 'lucide-react';

export const ALMACENAMIENTO_ACTIVO = true;

/*
 * Los controles de opción se dibujan aquí en vez de usar los nativos: el preflight
 * de Tailwind les quita el borde y, en el render de producción, la casilla del
 * consentimiento aparecía como un cuadro relleno que se lee como si ya estuviera
 * aceptada. En un consentimiento informado eso no es un detalle estético.
 */
const Casilla: React.FC<{ marcada: boolean; redonda?: boolean }> = ({ marcada, redonda }) => (
  <span
    aria-hidden
    className={`w-[18px] h-[18px] shrink-0 border flex items-center justify-center transition ${
      redonda ? 'rounded-full' : 'rounded-[5px]'
    } ${marcada ? 'bg-uni-700 border-uni-700' : 'bg-white border-slate-300'}`}
  >
    {marcada &&
      (redonda ? (
        <span className="w-2 h-2 rounded-full bg-white" />
      ) : (
        <Check className="w-3 h-3 text-white" strokeWidth={3} />
      ))}
  </span>
);

type Opcion = { v: string; t: string };
type Item = {
  id: string;
  n: number;
  pregunta: string;
  tipo: 'radio' | 'multi' | 'escala' | 'texto';
  opciones?: Opcion[];
  max?: number;
  obligatorio?: boolean;
  nota?: string;
};

const o = (...pares: [string, string][]): Opcion[] => pares.map(([v, t]) => ({ v, t }));

const BLOQUES: { titulo: string; descripcion?: string; items: Item[] }[] = [
  {
    titulo: 'A · Su relación con el paso',
    items: [
      {
        id: 'perfil', n: 1, tipo: 'radio', obligatorio: true,
        pregunta: '¿Cuál describe mejor su relación con el paso del Alto de La Línea?',
        opciones: o(
          ['carga', 'Conductor de carga pesada'],
          ['pasajeros', 'Conductor de transporte de pasajeros'],
          ['particular', 'Conductor particular'],
          ['habitante', 'Habitante de la zona, no conduzco por el paso'],
          ['otro', 'Otro'],
        ),
      },
      {
        id: 'municipio', n: 2, tipo: 'radio', obligatorio: true,
        pregunta: 'Municipio donde vive o tiene su base de operación',
        opciones: o(
          ['ibague', 'Ibagué'], ['coello', 'Coello'], ['cajamarca', 'Cajamarca'],
          ['calarca', 'Calarcá'], ['otro_tolima', 'Otro del Tolima'],
          ['otro_quindio', 'Otro del Quindío'], ['fuera', 'Fuera de ambos departamentos'],
        ),
      },
      {
        id: 'frecuencia', n: 3, tipo: 'radio', obligatorio: true,
        pregunta: '¿Con qué frecuencia cruza el paso?',
        opciones: o(
          ['diario', 'A diario'], ['semana', 'Varias veces por semana'],
          ['mes', 'Varias veces al mes'], ['anio', 'Pocas veces al año'], ['nunca', 'Nunca'],
        ),
      },
      {
        id: 'franja', n: 4, tipo: 'radio',
        pregunta: '¿En qué franja lo cruza con más frecuencia?',
        opciones: o(
          ['madrugada', 'Madrugada'], ['manana', 'Mañana'], ['tarde', 'Tarde'],
          ['noche', 'Noche'], ['varia', 'Varía'],
        ),
      },
    ],
  },
  {
    titulo: 'B · Percepción de riesgo',
    items: [
      {
        id: 'riesgo', n: 5, tipo: 'escala', obligatorio: true,
        pregunta: '¿Qué tan riesgoso considera el paso?',
        nota: '1 = nada riesgoso · 5 = extremadamente riesgoso',
      },
      {
        id: 'sectores', n: 6, tipo: 'multi', max: 3,
        pregunta: '¿Qué sectores percibe como los más peligrosos?',
        nota: 'Máximo tres',
        opciones: o(
          ['subida_cajamarca', 'Subida desde Cajamarca'],
          ['cima', 'Cima del Alto de La Línea'],
          ['descenso_calarca', 'Descenso hacia Calarcá'],
          ['urbano_calarca', 'Casco urbano de Calarcá'],
          ['ibague_coello', 'Tramo Ibagué – Coello'],
          ['no_sabe', 'No sabría decir'],
        ),
      },
      {
        id: 'causas', n: 7, tipo: 'multi', max: 3,
        pregunta: '¿A qué atribuye principalmente el riesgo?',
        nota: 'Máximo tres',
        opciones: o(
          ['geometria', 'Geometría de la vía'], ['pavimento', 'Estado del pavimento'],
          ['clima', 'Niebla o lluvia'], ['velocidad', 'Velocidad de otros vehículos'],
          ['adelantamientos', 'Adelantamientos indebidos'],
          ['carga_lenta', 'Vehículos de carga lentos o averiados'],
          ['senalizacion', 'Falta de señalización'], ['derrumbes', 'Derrumbes'],
          ['otro', 'Otro'],
        ),
      },
      {
        id: 'accidente', n: 8, tipo: 'radio',
        pregunta: '¿Ha presenciado o estado involucrado en un accidente en este paso?',
        nota: 'No se piden detalles',
        opciones: o(['si', 'Sí'], ['no', 'No']),
      },
      {
        id: 'cambio', n: 9, tipo: 'radio',
        pregunta: '¿Qué tanto ha cambiado el riesgo en los últimos cinco años?',
        opciones: o(
          ['empeoro_mucho', 'Empeoró mucho'], ['empeoro_algo', 'Empeoró algo'],
          ['igual', 'Sigue igual'], ['mejoro_algo', 'Mejoró algo'],
          ['mejoro_mucho', 'Mejoró mucho'], ['no_sabe', 'No sabe'],
        ),
      },
    ],
  },
  {
    titulo: 'C · Operación y vida diaria',
    items: [
      {
        id: 'tiempo', n: 10, tipo: 'radio',
        pregunta: '¿Cuánto tarda normalmente en cruzar?',
        opciones: o(
          ['menos2', 'Menos de 2 horas'], ['2a3', 'Entre 2 y 3 horas'],
          ['3a4', 'Entre 3 y 4 horas'], ['4a6', 'Entre 4 y 6 horas'],
          ['mas6', 'Más de 6 horas'],
        ),
      },
      {
        id: 'impredecible', n: 11, tipo: 'escala',
        pregunta: '¿Qué tan impredecible es ese tiempo?',
        nota: '1 = siempre igual · 5 = completamente impredecible',
      },
      {
        id: 'afectacion', n: 12, tipo: 'multi', max: 2,
        pregunta: '¿Qué es lo que más le afecta?',
        nota: 'Máximo dos',
        opciones: o(
          ['costos', 'Costos de operación'], ['entregas', 'Tiempos de entrega'],
          ['fatiga', 'Descanso y fatiga'], ['familia', 'Vida familiar'],
          ['precios', 'Precio de lo que compro'], ['ninguna', 'Ninguna'],
        ),
      },
    ],
  },
  {
    titulo: 'D · Sobre la propuesta de túnel',
    descripcion:
      'El semillero analiza esta iniciativa de forma independiente. No la representa ni la promueve.',
    items: [
      {
        id: 'conocia', n: 13, tipo: 'radio',
        pregunta: '¿Había oído hablar de una propuesta de túnel ferroviario para este paso?',
        opciones: o(['si', 'Sí'], ['no', 'No']),
      },
      {
        id: 'efecto', n: 14, tipo: 'radio',
        pregunta: 'Si se construyera, ¿qué efecto esperaría sobre el riesgo vial del paso?',
        opciones: o(
          ['reduce_mucho', 'Lo reduciría mucho'], ['reduce_algo', 'Lo reduciría algo'],
          ['ninguno', 'Ningún efecto'], ['aumenta', 'Lo aumentaría'], ['no_sabe', 'No sabe'],
        ),
      },
      {
        id: 'preocupacion', n: 15, tipo: 'radio',
        pregunta: '¿Cuál sería su principal preocupación frente a una obra así?',
        opciones: o(
          ['ambiental', 'Impacto ambiental'],
          ['predios', 'Afectación a predios y comunidades'],
          ['empleo', 'Empleo local'], ['costo', 'Costo público'],
          ['inconclusa', 'Que no se termine'], ['ninguna', 'Ninguna'], ['otra', 'Otra'],
        ),
      },
    ],
  },
  {
    titulo: 'E · Lo que quiera agregar',
    items: [
      {
        id: 'comentario', n: 16, tipo: 'texto',
        pregunta: '¿Algo que deba saberse sobre este paso y que no le hayamos preguntado?',
        nota: 'Opcional, máximo 300 caracteres',
      },
    ],
  },
];

type Respuestas = Record<string, string | string[] | number | undefined>;

export const ConsultaCiudadana: React.FC = () => {
  const [consentimiento, setConsentimiento] = useState(false);
  const [r, setR] = useState<Respuestas>({});
  const [enviando, setEnviando] = useState(false);
  const [resultado, setResultado] = useState<'ok' | 'pendiente' | 'error' | null>(null);

  const obligatorios = BLOQUES.flatMap((b) => b.items).filter((i) => i.obligatorio);
  const faltantes = obligatorios.filter((i) => r[i.id] === undefined);
  const puedeEnviar = consentimiento && faltantes.length === 0 && !enviando;

  const setRadio = (id: string, v: string) => setR((p) => ({ ...p, [id]: v }));

  const setMulti = (id: string, v: string, max: number) =>
    setR((p) => {
      const actual = Array.isArray(p[id]) ? (p[id] as string[]) : [];
      if (actual.includes(v)) return { ...p, [id]: actual.filter((x) => x !== v) };
      if (actual.length >= max) return p;
      return { ...p, [id]: [...actual, v] };
    });

  const enviar = async () => {
    setEnviando(true);
    setResultado(null);
    try {
      const res = await fetch('/api/consulta', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ consentimiento, ...r }),
      });
      if (res.status === 501) setResultado('pendiente');
      else if (res.ok) setResultado('ok');
      else setResultado('error');
    } catch {
      setResultado('error');
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-12">

      {/* Estado real del instrumento. Se retira —no se reescribe— cuando entre el
          cuestionario oficial avalado por la interlocutora. */}
      {ALMACENAMIENTO_ACTIVO ? (
        <div className="rounded-2xl border border-uni-200 bg-uni-50 p-4 mb-8 flex gap-3">
          <Info className="w-5 h-5 text-uni-600 shrink-0 mt-0.5" />
          <p className="text-sm text-slate-700 leading-relaxed">
            <strong>La consulta está abierta y su respuesta sí se guarda.</strong> El
            cuestionario es la versión del semillero; está pendiente del aval de la
            entidad receptora. Si esa revisión cambia alguna pregunta, las respuestas
            recogidas hasta entonces se analizan aparte y no se mezclan con las nuevas.
          </p>
        </div>
      ) : (
        <div className="rounded-2xl border border-acred-400/40 bg-acred-400/10 p-4 mb-8 flex gap-3">
          <AlertTriangle className="w-5 h-5 text-acred-600 shrink-0 mt-0.5" />
          <p className="text-sm text-slate-700 leading-relaxed">
            <strong>Vista previa del instrumento.</strong> Está en revisión y todavía no
            recoge respuestas: lo que escriba aquí <strong>no se guarda</strong>. Esta
            página existe para revisar las preguntas antes de abrir la consulta.
          </p>
        </div>
      )}

      <header className="mb-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gmae-600/10 border border-gmae-600/20 text-gmae-600 text-xs font-semibold uppercase tracking-wider mb-4">
          <ShieldAlert className="w-3.5 h-3.5" />
          Objetivo específico 2 · Consulta ciudadana
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-uni-900 leading-tight">
          Percepción de riesgo vial en el paso del Alto de La Línea
        </h1>
        <p className="text-sm text-slate-600 leading-relaxed mt-4">
          Semillero de Investigación GEOPAV · Ingeniería Civil · Universidad de Ibagué ·
          Semestre Paz y Región 2026B. Esta consulta recoge cómo perciben el riesgo quienes
          usan y habitan el corredor Ibagué – Armenia. Toma unos cinco minutos.
        </p>
      </header>

      {/* Consentimiento */}
      <section className="rounded-2xl bg-white border border-slate-200 p-5 sm:p-6 mb-8">
        <h2 className="text-base font-bold text-uni-900 mb-3">Antes de empezar</h2>
        <p className="text-xs text-slate-600 leading-relaxed mb-4">
          Esta consulta es anónima y voluntaria. No se piden nombre, cédula, teléfono ni
          correo, y no se registra su dirección IP ni su dispositivo. Las respuestas se usan
          solo con fines académicos y se publican agregadas, nunca individuales. Puede
          abandonarla en cualquier momento. Tratamiento de datos conforme a la Ley
          Estatutaria 1581 de 2012.
        </p>
        <button
          type="button"
          role="checkbox"
          aria-checked={consentimiento}
          onClick={() => setConsentimiento((v) => !v)}
          className="flex items-start gap-3 text-left w-full"
        >
          <span className="mt-0.5">
            <Casilla marcada={consentimiento} />
          </span>
          <span className="text-sm font-semibold text-slate-800">
            Entiendo y acepto participar.
          </span>
        </button>
      </section>

      {/* Bloques */}
      <fieldset disabled={!consentimiento} className={consentimiento ? '' : 'opacity-40'}>
        {BLOQUES.map((b) => (
          <section key={b.titulo} className="mb-8">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500 mb-1">
              {b.titulo}
            </h2>
            {b.descripcion && (
              <p className="text-xs text-slate-500 leading-relaxed mb-4">{b.descripcion}</p>
            )}

            <div className="space-y-4 mt-4">
              {b.items.map((item) => (
                <div key={item.id} className="rounded-2xl bg-white border border-slate-200 p-5">
                  <p className="text-sm font-semibold text-uni-900 leading-snug">
                    <span className="text-slate-400 mr-2">{item.n}.</span>
                    {item.pregunta}
                    {item.obligatorio && <span className="text-acred-600 ml-1">*</span>}
                  </p>
                  {item.nota && (
                    <p className="text-[11px] text-slate-500 mt-1">{item.nota}</p>
                  )}

                  {item.tipo === 'escala' && (
                    <div className="flex gap-2 mt-4">
                      {[1, 2, 3, 4, 5].map((n) => (
                        <button
                          key={n}
                          type="button"
                          onClick={() => setR((p) => ({ ...p, [item.id]: n }))}
                          className={`w-11 h-11 rounded-xl border text-sm font-bold transition ${
                            r[item.id] === n
                              ? 'bg-uni-700 border-uni-700 text-white'
                              : 'bg-white border-slate-200 text-slate-600 hover:border-uni-400'
                          }`}
                        >
                          {n}
                        </button>
                      ))}
                    </div>
                  )}

                  {item.tipo === 'radio' && item.opciones && (
                    <div className="mt-3 space-y-1.5">
                      {item.opciones.map((op) => (
                        <button
                          key={op.v}
                          type="button"
                          role="radio"
                          aria-checked={r[item.id] === op.v}
                          onClick={() => setRadio(item.id, op.v)}
                          className="flex items-center gap-3 text-sm text-slate-700 py-1.5 w-full text-left hover:text-uni-800"
                        >
                          <Casilla redonda marcada={r[item.id] === op.v} />
                          {op.t}
                        </button>
                      ))}
                    </div>
                  )}

                  {item.tipo === 'multi' && item.opciones && (
                    <div className="mt-3 space-y-1.5">
                      {item.opciones.map((op) => {
                        const sel = Array.isArray(r[item.id])
                          ? (r[item.id] as string[]).includes(op.v)
                          : false;
                        return (
                          <button
                            key={op.v}
                            type="button"
                            role="checkbox"
                            aria-checked={sel}
                            onClick={() => setMulti(item.id, op.v, item.max ?? 99)}
                            className="flex items-center gap-3 text-sm text-slate-700 py-1.5 w-full text-left hover:text-uni-800"
                          >
                            <Casilla marcada={sel} />
                            {op.t}
                          </button>
                        );
                      })}
                    </div>
                  )}

                  {item.tipo === 'texto' && (
                    <textarea
                      maxLength={300}
                      rows={3}
                      value={typeof r[item.id] === 'string' ? (r[item.id] as string) : ''}
                      onChange={(e) => setR((p) => ({ ...p, [item.id]: e.target.value }))}
                      className="mt-3 w-full rounded-xl border border-slate-200 p-3 text-sm text-slate-700 focus:outline-none focus:border-uni-400"
                      placeholder="Opcional"
                    />
                  )}
                </div>
              ))}
            </div>
          </section>
        ))}
      </fieldset>

      {/* Envío */}
      <div className="rounded-2xl bg-white border border-slate-200 p-5 sm:p-6">
        {faltantes.length > 0 && consentimiento && (
          <p className="text-xs text-slate-500 mb-3">
            Faltan por responder las preguntas obligatorias:{' '}
            {faltantes.map((f) => f.n).join(', ')}.
          </p>
        )}
        <button
          type="button"
          disabled={!puedeEnviar}
          onClick={enviar}
          className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-uni-700 text-white text-sm font-bold disabled:bg-slate-300 disabled:cursor-not-allowed hover:bg-uni-800 transition"
        >
          <Send className="w-4 h-4" />
          {enviando ? 'Enviando…' : 'Enviar respuestas'}
        </button>

        {resultado === 'ok' && (
          <p className="mt-4 text-sm text-gmae-700 font-semibold flex items-center gap-2">
            <Check className="w-4 h-4" /> Gracias. Su respuesta quedó registrada.
          </p>
        )}
        {resultado === 'pendiente' && (
          <p className="mt-4 text-sm text-slate-600 flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-acred-600 shrink-0 mt-0.5" />
            La consulta todavía no está abierta: esta es una vista previa y su respuesta
            no se guardó.
          </p>
        )}
        {resultado === 'error' && (
          <p className="mt-4 text-sm text-acred-600">
            No se pudo enviar. Intente de nuevo más tarde.
          </p>
        )}
      </div>

      {/* Límites declarados de entrada */}
      <section className="mt-10 rounded-2xl bg-slate-100 border border-slate-200 p-5 sm:p-6">
        <h2 className="text-sm font-bold text-uni-900 mb-3">Qué no permite concluir esta consulta</h2>
        <ul className="space-y-2 text-xs text-slate-600 leading-relaxed">
          <li>
            · La difusión es digital y la participación es voluntaria, de modo que la muestra
            no es probabilística: los resultados describen a quienes respondieron y no se
            pueden extrapolar al total de usuarios del corredor.
          </li>
          <li>· Deja por fuera a quien no usa canales digitales.</li>
          <li>
            · Mide percepción, no riesgo medido. La tasa de siniestralidad del corredor es
            resultado del objetivo específico 5 y se calcula con datos de la ANSV y aforos;
            las dos cosas no se mezclan.
          </li>
          <li>· La pregunta 8 es autorreporte y no se verifica.</li>
        </ul>
      </section>
    </div>
  );
};
