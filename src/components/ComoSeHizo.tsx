'use client';

/**
 * ComoSeHizo — bloque común «Cómo se hizo» para los objetivos específicos.
 *
 * Mismo Acordeon que ya usaba el OE1: por qué, para qué, cómo (con espacio para
 * contenido extra vía `children`) y, al cierre, el recuadro amarillo «Qué no
 * afirma y sus limitaciones». Los textos de por qué/para qué/cómo/límites
 * vienen SIEMPRE de `METODO_OE` en `src/data/metodo_oe.ts`; este componente no
 * declara texto propio del método, solo la estructura visual.
 */

import React from 'react';
import { AlertTriangle, Route } from 'lucide-react';
import Acordeon from './Acordeon';

interface Props {
  porQue: string;
  paraQue: string;
  /** Párrafos del método. Puede venir vacío cuando todo el contenido de "Cómo" llega por `children`. */
  como: readonly string[];
  /** Límites y qué no afirma. Puede venir vacío cuando llegan por `children` (no es el caso de uso previsto). */
  noAfirma: readonly string[];
  resumen?: string;
  icono?: React.ReactNode;
  contador?: string;
  /** Contenido adicional dentro de "Cómo", después de los párrafos de `como`. */
  children?: React.ReactNode;
}

export const ComoSeHizo: React.FC<Props> = ({
  porQue,
  paraQue,
  como,
  noAfirma,
  resumen = 'Por qué, para qué y cómo se hizo este objetivo, y qué no afirma.',
  icono = <Route className="h-5 w-5 text-uni-600" />,
  contador = 'método',
  children,
}) => (
  <Acordeon titulo="Cómo se hizo" resumen={resumen} icono={icono} contador={contador}>
    <div className="max-w-3xl space-y-4 text-xs leading-relaxed text-slate-600">
      <div>
        <h4 className="mb-1 text-sm font-bold text-uni-900">Por qué</h4>
        <p>{porQue}</p>
      </div>
      <div>
        <h4 className="mb-1 text-sm font-bold text-uni-900">Para qué</h4>
        <p>{paraQue}</p>
      </div>
      <div>
        <h4 className="mb-1 text-sm font-bold text-uni-900">Cómo</h4>
        {como.length > 0 && (
          <div className="space-y-3">
            {como.map((p, i) => (
              <p key={i}>{p}</p>
            ))}
          </div>
        )}
        {children}
      </div>
    </div>

    {noAfirma.length > 0 && (
      <div className="mt-4 rounded-xl bg-amber-500/5 border border-amber-500/25 p-4">
        <div className="flex items-center gap-2 text-[11px] font-bold text-acred-600 uppercase tracking-wider mb-2">
          <AlertTriangle className="w-3.5 h-3.5" />
          Qué no afirma y sus limitaciones
        </div>
        <ul className="space-y-1.5 text-xs text-slate-600 leading-relaxed">
          {noAfirma.map((l, i) => (
            <li key={i} className="flex gap-2">
              <span className="text-slate-400 shrink-0">·</span>
              <span>{l}</span>
            </li>
          ))}
        </ul>
      </div>
    )}
  </Acordeon>
);

export default ComoSeHizo;
