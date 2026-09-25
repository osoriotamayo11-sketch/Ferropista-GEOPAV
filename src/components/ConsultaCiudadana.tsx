'use client';

/**
 * Consulta ciudadana sobre la Ferropista — objetivo específico 2.
 *
 * Único instrumento de dato primario del proyecto. Alimenta el OE 5 y el OE 7.
 *
 * Estado: ABIERTA desde el 15 sep 2026. Las respuestas se guardan en Supabase y
 * quedan marcadas con la versión del cuestionario (ver src/app/api/consulta/route.ts).
 *
 * Instrumento vigente: el OFICIAL, avalado por la entidad receptora (versión
 * 'oficial-2026-09'). Las preguntas se importan de
 * OE2_Plataforma/Act3_Instrumento/instrumento_oficial_2026-09.json —fuente única,
 * nunca transcritas a mano— y las respuestas se guardan en la tabla
 * consulta_oe2_oficial, separada de la tabla del instrumento borrador anterior
 * (consulta_oe2), que se conserva intacta y nunca se mezcla en silencio con esta.
 */

import React, { useState } from 'react';
import { ShieldAlert, Check, AlertTriangle, Send, Info } from 'lucide-react';
import { TRAZADO, OPERACION, ACTUAL, ECONOMICO } from '@/data/proyecto';
import instrumentoRaw from '../../OE2_Plataforma/Act3_Instrumento/instrumento_oficial_2026-09.json';

export const ALMACENAMIENTO_ACTIVO = true;

/* ----------------------------------------------------------------------
   Instrumento oficial: tipado propio sobre el JSON importado. El JSON es
   la fuente única de los textos de pregunta; aquí solo se define la forma.
   ---------------------------------------------------------------------- */
interface ItemInstrumento {
  n: number;
  texto: string;
  solo_para: string | null;
  opciones: string[];
  tipo: 'radio' | 'likert5' | 'texto';
}
interface InstrumentoOficial {
  version: string;
  fuente: string;
  escala_likert5: string[];
  items: ItemInstrumento[];
}
const instrumento = instrumentoRaw as InstrumentoOficial;
const ESCALA = instrumento.escala_likert5;

/* Códigos de las respuestas cerradas de las preguntas 1 y 2. No están en el
   JSON (que solo trae los textos que ve la persona); vienen del esquema de
   la tabla consulta_oe2_oficial (OE2_Plataforma/esquema_consulta_oficial.sql)
   y se emparejan por posición con las opciones del JSON, en su mismo orden. */
const RELACION_VALORES = ['carga', 'particular', 'comerciante', 'residente', 'trabajador', 'otro'] as const;
type RelacionValor = (typeof RELACION_VALORES)[number];
const PERFILES_CON_BLOQUE: RelacionValor[] = ['carga', 'particular', 'residente', 'comerciante'];

const FRECUENCIA_VALORES = ['diario', 'varias_semana', 'una_semana', 'algunas_mes', 'ocasional', 'nunca'] as const;

const item = (n: number, soloPara: string | null = null) =>
  instrumento.items.find((i) => i.n === n && i.solo_para === soloPara)!;

const Q1 = item(1);
const Q2 = item(2);
const LIKERT_COMUNES = instrumento.items
  .filter((i) => i.tipo === 'likert5' && i.solo_para === null)
  .sort((a, b) => a.n - b.n);
const BLOQUE_PERFIL: Record<RelacionValor, ItemInstrumento[]> = PERFILES_CON_BLOQUE.reduce(
  (acc, perfil) => {
    acc[perfil] = instrumento.items.filter((i) => i.solo_para === perfil).sort((a, b) => a.n - b.n);
    return acc;
  },
  {} as Record<RelacionValor, ItemInstrumento[]>
);
const Q16 = item(16);
const Q17 = item(17);

const limpiarOtro = (texto: string) => texto.replace(/[:\s]*_+\s*$/, '').trim();

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

const TarjetaPregunta: React.FC<{ n: number; texto: string; obligatoria?: boolean; children: React.ReactNode }> = ({
  n,
  texto,
  obligatoria = true,
  children,
}) => (
  <div className="rounded-2xl bg-white border border-slate-200 p-5">
    <p className="text-sm font-semibold text-uni-900 leading-snug">
      <span className="text-slate-400 mr-2">{n}.</span>
      {texto}
      {obligatoria && <span className="text-acred-600 ml-1">*</span>}
    </p>
    {children}
  </div>
);

const ListaLikert: React.FC<{ valor: number | undefined; onCambiar: (n: number) => void }> = ({
  valor,
  onCambiar,
}) => (
  <div className="mt-3 space-y-1.5">
    {ESCALA.map((etiqueta, idx) => {
      const n = idx + 1;
      return (
        <button
          key={n}
          type="button"
          role="radio"
          aria-checked={valor === n}
          onClick={() => onCambiar(n)}
          className="flex items-center gap-3 text-sm text-slate-700 py-1.5 w-full text-left hover:text-uni-800"
        >
          <Casilla redonda marcada={valor === n} />
          {etiqueta}
        </button>
      );
    })}
  </div>
);

type Respuestas = {
  relacion?: RelacionValor;
  relacionOtro?: string;
  frecuencia?: (typeof FRECUENCIA_VALORES)[number];
  [preguntaLikertOTexto: string]: string | number | undefined;
};

const claveLikert = (n: number) => `p${n < 10 ? '0' + n : n}`;

export const ConsultaCiudadana: React.FC = () => {
  const [consentimiento, setConsentimiento] = useState(false);
  const [r, setR] = useState<Respuestas>({});
  const [enviando, setEnviando] = useState(false);
  const [resultado, setResultado] = useState<'ok' | 'pendiente' | 'error' | null>(null);

  const enviado = resultado === 'ok';
  const necesitaBloquePerfil = !!r.relacion && PERFILES_CON_BLOQUE.includes(r.relacion);

  const faltantes: number[] = [];
  if (!r.relacion) faltantes.push(1);
  if (!r.frecuencia) faltantes.push(2);
  LIKERT_COMUNES.forEach((it) => {
    if (r[claveLikert(it.n)] === undefined) faltantes.push(it.n);
  });
  if (necesitaBloquePerfil) {
    if (r.p14 === undefined) faltantes.push(14);
    if (r.p15 === undefined) faltantes.push(15);
  }

  const puedeEnviar = consentimiento && faltantes.length === 0 && !enviando && !enviado;

  const setRelacion = (v: RelacionValor) =>
    setR((p) => ({
      ...p,
      relacion: v,
      relacionOtro: v === 'otro' ? p.relacionOtro : undefined,
      p14: undefined,
      p15: undefined,
    }));

  const setLikert = (n: number, v: number) => setR((p) => ({ ...p, [claveLikert(n)]: v }));

  const enviar = async () => {
    setEnviando(true);
    setResultado(null);
    try {
      const res = await fetch('/api/consulta', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          consentimiento,
          relacion: r.relacion,
          relacion_otro: r.relacion === 'otro' ? r.relacionOtro || null : null,
          frecuencia: r.frecuencia,
          p03: r.p03, p04: r.p04, p05: r.p05, p06: r.p06, p07: r.p07,
          p08: r.p08, p09: r.p09, p10: r.p10, p11: r.p11, p12: r.p12, p13: r.p13,
          p14: necesitaBloquePerfil ? r.p14 ?? null : null,
          p15: necesitaBloquePerfil ? r.p15 ?? null : null,
          p16_beneficio: typeof r.p16 === 'string' && r.p16.length > 0 ? r.p16 : null,
          p17_impacto: typeof r.p17 === 'string' && r.p17.length > 0 ? r.p17 : null,
        }),
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

      {ALMACENAMIENTO_ACTIVO ? (
        <div className="rounded-2xl border border-uni-200 bg-uni-50 p-4 mb-8 flex gap-3">
          <Info className="w-5 h-5 text-uni-600 shrink-0 mt-0.5" />
          <p className="text-sm text-slate-700 leading-relaxed">
            <strong>La consulta está abierta y su respuesta sí se guarda.</strong> Instrumento
            oficial, avalado por la entidad receptora.
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
          Conocimiento y percepción ciudadana de la Ferropista
        </h1>
        <p className="text-sm text-slate-600 leading-relaxed mt-4">
          Semillero de Investigación GEOPAV · Ingeniería Civil · Universidad de Ibagué ·
          Semestre Paz y Región 2026B. Esta consulta recoge qué tanto conocen y qué opinan
          de la propuesta de túnel ferroviario quienes usan y habitan el corredor
          Ibagué – Armenia. Toma unos cinco minutos.
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
          onClick={() => { if (!enviado) setConsentimiento((v) => !v); }}
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

      <fieldset disabled={!consentimiento || enviado} className={consentimiento ? '' : 'opacity-40'}>

        {/* Bloque 1: relación con el corredor */}
        <section className="mb-8">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500 mb-4">
            Su relación con el corredor
          </h2>
          <div className="space-y-4">
            <TarjetaPregunta n={Q1.n} texto={Q1.texto}>
              <div className="mt-3 space-y-1.5">
                {Q1.opciones.map((texto, idx) => {
                  const valor = RELACION_VALORES[idx];
                  return (
                    <button
                      key={valor}
                      type="button"
                      role="radio"
                      aria-checked={r.relacion === valor}
                      onClick={() => setRelacion(valor)}
                      className="flex items-center gap-3 text-sm text-slate-700 py-1.5 w-full text-left hover:text-uni-800"
                    >
                      <Casilla redonda marcada={r.relacion === valor} />
                      {valor === 'otro' ? limpiarOtro(texto) : texto}
                    </button>
                  );
                })}
              </div>
              {r.relacion === 'otro' && (
                <input
                  type="text"
                  maxLength={100}
                  value={r.relacionOtro ?? ''}
                  onChange={(e) => setR((p) => ({ ...p, relacionOtro: e.target.value }))}
                  placeholder="Especifique (opcional)"
                  className="mt-3 w-full rounded-xl border border-slate-200 p-3 text-sm text-slate-700 focus:outline-none focus:border-uni-400 bg-white placeholder:text-slate-400 [color-scheme:light]"
                />
              )}
            </TarjetaPregunta>

            <TarjetaPregunta n={Q2.n} texto={Q2.texto}>
              <div className="mt-3 space-y-1.5">
                {Q2.opciones.map((texto, idx) => {
                  const valor = FRECUENCIA_VALORES[idx];
                  return (
                    <button
                      key={valor}
                      type="button"
                      role="radio"
                      aria-checked={r.frecuencia === valor}
                      onClick={() => setR((p) => ({ ...p, frecuencia: valor }))}
                      className="flex items-center gap-3 text-sm text-slate-700 py-1.5 w-full text-left hover:text-uni-800"
                    >
                      <Casilla redonda marcada={r.frecuencia === valor} />
                      {texto}
                    </button>
                  );
                })}
              </div>
            </TarjetaPregunta>
          </div>
        </section>

        {/* Bloque 2: conocimiento y opinión */}
        <section className="mb-8">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500 mb-4">
            Conocimiento y opinión sobre la Ferropista
          </h2>
          <div className="space-y-4">
            {LIKERT_COMUNES.filter((it) => it.n === 3).map((it) => (
              <TarjetaPregunta key={it.n} n={it.n} texto={it.texto}>
                <ListaLikert valor={r[claveLikert(it.n)] as number | undefined} onCambiar={(v) => setLikert(it.n, v)} />
              </TarjetaPregunta>
            ))}

            {/* Recuadro informativo, antes de la pregunta 4 */}
            <div className="rounded-2xl border border-uni-200 bg-uni-50 p-5">
              <h3 className="text-xs font-bold uppercase tracking-wider text-uni-700 mb-2">
                Qué propone la iniciativa
              </h3>
              <p className="text-sm text-slate-700 leading-relaxed">
                Una iniciativa privada propone un túnel ferroviario bajo la Cordillera
                Central entre Ibagué y Calarcá: {TRAZADO.longitudTotal.n} km de trazado, con
                un túnel principal de {TRAZADO.tunelPrincipal.n} km. Funcionaría como
                autopista rodante: los camiones suben con sus conductores a un tren
                eléctrico y cruzan en unos {OPERACION.tCicloTotal.n} minutos, incluidas
                carga y descarga, frente a unas {ACTUAL.tiempoCruce.valor} por el Alto de
                La Línea hoy. El proponente estima su costo en {ECONOMICO.capex.valor}. Son
                cifras del proponente, no verificadas por un tercero. El semillero GEOPAV
                analiza la iniciativa de forma independiente; no la representa ni la
                promueve.
              </p>
              <p className="text-[11px] text-slate-500 mt-3">
                Fuente: Fernández Ordóñez (2025), ponencia SAI, dia. 20, 23 y 29.
              </p>
            </div>

            {LIKERT_COMUNES.filter((it) => it.n !== 3).map((it) => (
              <TarjetaPregunta key={it.n} n={it.n} texto={it.texto}>
                <ListaLikert valor={r[claveLikert(it.n)] as number | undefined} onCambiar={(v) => setLikert(it.n, v)} />
              </TarjetaPregunta>
            ))}
          </div>
        </section>

        {/* Bloque 3: preguntas según el perfil */}
        {necesitaBloquePerfil && r.relacion && (
          <section className="mb-8">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500 mb-4">
              Preguntas según su perfil
            </h2>
            <div className="space-y-4">
              {BLOQUE_PERFIL[r.relacion].map((it) => {
                const clave = it.n === 14 ? 'p14' : 'p15';
                return (
                  <TarjetaPregunta key={clave} n={it.n} texto={it.texto}>
                    <ListaLikert
                      valor={r[clave] as number | undefined}
                      onCambiar={(v) => setR((p) => ({ ...p, [clave]: v }))}
                    />
                  </TarjetaPregunta>
                );
              })}
            </div>
          </section>
        )}

        {/* Bloque 4: para terminar */}
        <section className="mb-8">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500 mb-4">
            Para terminar
          </h2>
          <div className="space-y-4">
            {[Q16, Q17].map((it) => {
              const clave = it.n === 16 ? 'p16' : 'p17';
              const valor = typeof r[clave] === 'string' ? (r[clave] as string) : '';
              return (
                <TarjetaPregunta key={clave} n={it.n} texto={it.texto} obligatoria={false}>
                  <textarea
                    maxLength={500}
                    rows={3}
                    value={valor}
                    onChange={(e) => setR((p) => ({ ...p, [clave]: e.target.value }))}
                    className="mt-3 w-full rounded-xl border border-slate-200 p-3 text-sm text-slate-700 focus:outline-none focus:border-uni-400 bg-white placeholder:text-slate-400 [color-scheme:light]"
                    placeholder="Opcional"
                  />
                  <p className="text-[11px] text-slate-400 mt-1 text-right">{valor.length} / 500</p>
                </TarjetaPregunta>
              );
            })}
          </div>
        </section>
      </fieldset>

      {/* Envío */}
      <div className="rounded-2xl bg-white border border-slate-200 p-5 sm:p-6">
        {faltantes.length > 0 && consentimiento && (
          <p className="text-xs text-slate-500 mb-3">
            Faltan por responder las preguntas obligatorias:{' '}
            {faltantes.slice().sort((a, b) => a - b).join(', ')}.
          </p>
        )}
        <button
          type="button"
          disabled={!puedeEnviar}
          onClick={enviar}
          className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-uni-700 text-white text-sm font-bold disabled:bg-slate-300 disabled:cursor-not-allowed hover:bg-uni-800 transition"
        >
          <Send className="w-4 h-4" />
          {enviado ? 'Respuesta enviada' : enviando ? 'Enviando…' : 'Enviar respuestas'}
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
            · Mide percepción y opinión declaradas, no verifica técnicamente la propuesta.
            Esa verificación —geotecnia, excavación, tránsito, siniestralidad— es el objeto
            de los demás objetivos específicos del semillero, con sus propias fuentes.
          </li>
        </ul>
      </section>
    </div>
  );
};
