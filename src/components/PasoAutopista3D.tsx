'use client';

/**
 * PasoAutopista3D — envoltura de las escenas 3D del proceso operativo (Solution).
 *
 * - Carga diferida y sin SSR: three.js no entra en la ruta crítica.
 * - Cada tarjeta monta su propio <Canvas> (ver `3d/AutopistaRodante`), con su
 *   propio IntersectionObserver: se monta al acercarse a la pantalla y detiene
 *   el render (frameloop 'never') al salir de ella. Anima siempre que está en
 *   pantalla, igual que EscenaComparativa — no respeta «reducir movimiento»,
 *   porque los esquemas comparativos del encabezado tampoco lo hacen.
 * - Si WebGL falla, se muestra el pictograma SVG propio que había antes. El
 *   límite de error es por tarjeta.
 */

import dynamic from 'next/dynamic';
import { Component, useEffect, useRef, useState, type ReactNode } from 'react';
import type { PasoAutopista } from './3d/AutopistaRodante';

const AutopistaEscena = dynamic(() => import('./3d/AutopistaRodante'), {
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

  useEffect(() => {
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
          <AutopistaEscena paso={paso} enPantalla={enPantalla} />
        </Respaldo>
      ) : (
        respaldo
      )}
    </div>
  );
}
