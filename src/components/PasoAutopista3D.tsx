'use client';

/**
 * PasoAutopista3D — envoltura de las escenas 3D del proceso operativo (Solution).
 *
 * - Carga diferida y sin SSR: three.js no entra en la ruta crítica.
 * - Se monta al acercarse a la pantalla y se detiene al salir de ella
 *   (frameloop 'demand'), así cuatro lienzos no consumen GPU a la vez.
 * - Con «reducir movimiento» la escena queda estática.
 * - Si WebGL falla, se muestra el pictograma SVG propio que había antes.
 */

import dynamic from 'next/dynamic';
import { Component, useEffect, useRef, useState, type ReactNode } from 'react';
import type { PasoAutopista } from './3d/AutopistaRodante';

const AutopistaRodante = dynamic(() => import('./3d/AutopistaRodante'), {
  ssr: false,
  loading: () => (
    <div className="flex h-full w-full items-center justify-center bg-sky-50">
      <span className="animate-pulse font-mono text-[10px] tracking-wide text-slate-400">cargando esquema…</span>
    </div>
  ),
});

class Respaldo extends Component<{ respaldo: ReactNode; children: ReactNode }, { fallo: boolean }> {
  state = { fallo: false };
  static getDerivedStateFromError() {
    return { fallo: true };
  }
  render() {
    return this.state.fallo ? this.props.respaldo : this.props.children;
  }
}

export default function PasoAutopista3D({ paso, respaldo }: { paso: PasoAutopista; respaldo: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  const [montado, setMontado] = useState(false);
  const [enPantalla, setEnPantalla] = useState(false);
  const [quieto, setQuieto] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia?.('(prefers-reduced-motion: reduce)');
    setQuieto(!!mq?.matches);
    const nodo = ref.current;
    if (!nodo || typeof IntersectionObserver === 'undefined') {
      setMontado(true);
      setEnPantalla(true);
      return;
    }
    const obs = new IntersectionObserver(
      ([e]) => {
        setEnPantalla(e.isIntersecting);
        if (e.isIntersecting) setMontado(true);
      },
      { rootMargin: '150px' },
    );
    obs.observe(nodo);
    return () => obs.disconnect();
  }, []);

  return (
    <div ref={ref} className="aspect-[4/3] w-full">
      {montado ? (
        <Respaldo respaldo={respaldo}>
          <AutopistaRodante paso={paso} animar={enPantalla && !quieto} />
        </Respaldo>
      ) : (
        respaldo
      )}
    </div>
  );
}
