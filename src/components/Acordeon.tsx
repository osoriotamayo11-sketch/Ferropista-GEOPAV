'use client';

/**
 * Acordeon — bloque plegable reutilizable.
 *
 * Mismo patrón de interacción que las tarjetas de objetivo del Plan de Acción:
 * un botón de cabecera que gira el chevron y revela el contenido. Se extrae
 * aquí para que las síntesis de los objetivos específicos no repitan el
 * mecanismo ni se desvíen del comportamiento del Plan.
 *
 * Por defecto viene plegado: estas secciones son el respaldo metodológico,
 * no lo primero que el visitante necesita leer.
 */

import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';

interface Props {
  titulo: string;
  /** Línea corta bajo el título: qué hay dentro. */
  resumen?: string;
  icono?: React.ReactNode;
  /** Etiqueta a la derecha del título (por ejemplo, cuántos elementos trae). */
  contador?: string;
  abiertoPorDefecto?: boolean;
  /** Fondo del bloque. Por defecto blanco. */
  tono?: 'blanco' | 'gris';
  children: React.ReactNode;
}

export const Acordeon: React.FC<Props> = ({
  titulo,
  resumen,
  icono,
  contador,
  abiertoPorDefecto = false,
  tono = 'blanco',
  children,
}) => {
  const [abierto, setAbierto] = useState(abiertoPorDefecto);
  const fondo = tono === 'gris' ? 'bg-slate-50' : 'bg-white';

  return (
    <div className={`overflow-hidden rounded-2xl border border-slate-200 ${fondo}`}>
      <button
        type="button"
        onClick={() => setAbierto((v) => !v)}
        aria-expanded={abierto}
        className="flex w-full items-center gap-3 p-5 text-left transition-colors hover:bg-slate-50"
      >
        {icono && <span className="shrink-0">{icono}</span>}

        <div className="min-w-0 flex-1">
          <h3 className="text-base font-bold leading-snug text-uni-900 sm:text-lg">{titulo}</h3>
          {resumen && <p className="mt-0.5 text-xs leading-relaxed text-slate-500">{resumen}</p>}
        </div>

        {contador && (
          <span className="hidden shrink-0 rounded-full border border-slate-200 bg-white px-2.5 py-0.5 font-mono text-[10px] text-slate-500 sm:inline">
            {contador}
          </span>
        )}

        <ChevronDown
          className={`h-5 w-5 shrink-0 text-slate-500 transition-transform ${abierto ? 'rotate-180' : ''}`}
        />
      </button>

      {abierto && <div className="border-t border-slate-200 p-5 sm:p-7">{children}</div>}
    </div>
  );
};

export default Acordeon;
