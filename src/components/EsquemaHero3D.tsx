'use client';

/**
 * EsquemaHero3D — envoltura de carga para las escenas 3D del encabezado.
 *
 * Sustituye las dos polilíneas SVG decorativas que ocupaban ese lugar y que no
 * representaban ningún dato.
 *
 * Las escenas son ESQUEMAS ILUSTRATIVOS: el relieve es procedural, no sale del
 * modelo de elevación. Cada tarjeta lo declara. El terreno real está en la
 * sección del OE 1.
 *
 * La carga es diferida y fuera del render inicial (`ssr: false`): three.js y
 * sus acompañantes pesan alrededor de 1,2 MB sin comprimir y no deben entrar
 * en la ruta crítica del encabezado.
 */

import dynamic from 'next/dynamic';
import { useEffect, useRef, useState } from 'react';

const EscenaComparativa = dynamic(() => import('./3d/EscenaComparativa'), {
  ssr: false,
  loading: () => <Marcador />,
});

function Marcador() {
  return (
    <div className="flex h-full w-full items-center justify-center bg-gradient-to-b from-sky-50 to-slate-100">
      <span className="animate-pulse font-mono text-[10px] tracking-wide text-slate-400">
        cargando esquema…
      </span>
    </div>
  );
}

interface Props {
  scenario: 'convencional' | 'ferropista';
  /** Etiqueta flotante sobre la escena. Debe traer su marca y diapositiva. */
  badge: string;
  badgeClassName?: string;
  height?: number;
}

export default function EsquemaHero3D({
  scenario,
  badge,
  badgeClassName = '',
  height = 300,
}: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  // Solo se monta el lienzo cuando la tarjeta entra en pantalla.
  useEffect(() => {
    const nodo = ref.current;
    if (!nodo) return;
    if (typeof IntersectionObserver === 'undefined') {
      setVisible(true);
      return;
    }
    const obs = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting) {
          setVisible(true);
          obs.disconnect();
        }
      },
      { rootMargin: '120px' },
    );
    obs.observe(nodo);
    return () => obs.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className="relative w-full overflow-hidden rounded-lg border border-slate-200 bg-slate-50"
      style={{ height }}
    >
      {visible ? (
        <EscenaComparativa scenario={scenario} height={height} calidad="media" />
      ) : (
        <Marcador />
      )}

      <span
        className={`pointer-events-none absolute right-2 top-2 rounded border px-1.5 py-0.5 font-mono text-[10px] text-white ${badgeClassName}`}
      >
        {badge}
      </span>

      <span className="pointer-events-none absolute bottom-1.5 left-2 rounded bg-white/85 px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-wide text-slate-600 backdrop-blur-[1px]">
        Esquema ilustrativo · relieve no topográfico
      </span>
    </div>
  );
}
