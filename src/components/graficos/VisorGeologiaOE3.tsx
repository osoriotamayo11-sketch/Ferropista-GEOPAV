'use client';

/**
 * VisorGeologiaOE3 — «La roca en la boca del túnel»: un visor por portal sobre
 * el recorte de la plancha geológica 1:100.000, con zoom (rueda o pellizco) y
 * arrastre. Portal, barra de escala y flecha de norte se dibujan en un SVG que
 * comparte la misma transformación CSS que la imagen, así que quedan alineados
 * en cualquier nivel de zoom. Al pasar el mouse o enfocar una unidad de la
 * leyenda, su máscara (`u.mascara`) se resalta con `mask-image` y el resto se
 * atenúa. Todo sale de `src/data/oe3_geologia.json`; ninguna cifra se escribe aquí.
 */

import React, { useCallback, useRef, useState } from 'react';
import oe3Geologia from '@/data/oe3_geologia.json';

type UnidadGeologica = (typeof oe3Geologia.portales)[number]['unidades'][number];
type PortalGeologia = (typeof oe3Geologia.portales)[number];

const es = (v: number, d = 0) =>
  v.toLocaleString('es-CO', { minimumFractionDigits: d, maximumFractionDigits: d });

const ZOOM_MIN = 1;
const ZOOM_MAX = 6;

function distancia(a: React.PointerEvent, b: React.PointerEvent) {
  return Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
}

/* ═══════ El visor de un portal: imagen + overlay SVG, con zoom/pan propios ═══════ */
function VisorPortal({ portal: p }: { portal: PortalGeologia }) {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [hoverIdx, setHoverIdx] = useState<number | null>(null);
  const contenedorRef = useRef<HTMLDivElement | null>(null);
  const punteros = useRef(new Map<number, { x: number; y: number }>());
  const distanciaPrevia = useRef<number | null>(null);
  const arrastre = useRef<{ x: number; y: number } | null>(null);

  const restablecer = useCallback(() => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  }, []);

  const manejarRueda = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    setZoom((z) => Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, z - e.deltaY * 0.0025)));
  }, []);

  const manejarPointerDown = useCallback((e: React.PointerEvent) => {
    (e.target as Element).setPointerCapture?.(e.pointerId);
    punteros.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (punteros.current.size === 1) arrastre.current = { x: e.clientX, y: e.clientY };
    if (punteros.current.size === 2) {
      const [a, b] = [...punteros.current.values()];
      distanciaPrevia.current = Math.hypot(a.x - b.x, a.y - b.y);
    }
  }, []);

  const manejarPointerMove = useCallback((e: React.PointerEvent) => {
    if (!punteros.current.has(e.pointerId)) return;
    punteros.current.set(e.pointerId, { x: e.clientX, y: e.clientY });

    if (punteros.current.size === 2) {
      const [a, b] = [...punteros.current.values()];
      const d = Math.hypot(a.x - b.x, a.y - b.y);
      if (distanciaPrevia.current) {
        const factor = d / distanciaPrevia.current;
        setZoom((z) => Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, z * factor)));
      }
      distanciaPrevia.current = d;
      return;
    }

    if (punteros.current.size === 1 && arrastre.current) {
      const dx = e.clientX - arrastre.current.x;
      const dy = e.clientY - arrastre.current.y;
      arrastre.current = { x: e.clientX, y: e.clientY };
      setPan((v) => ({ x: v.x + dx, y: v.y + dy }));
    }
  }, []);

  const manejarPointerUp = useCallback((e: React.PointerEvent) => {
    punteros.current.delete(e.pointerId);
    distanciaPrevia.current = null;
    if (punteros.current.size === 0) arrastre.current = null;
  }, []);

  const unidadActiva: UnidadGeologica | null = hoverIdx !== null ? p.unidades[hoverIdx] : null;
  const [px, py] = p.portal_px;
  const L = p.lado_px;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-2">
        <h4 className="text-sm font-bold text-uni-900 sm:text-base">{p.nombre}</h4>
        <button
          type="button"
          onClick={restablecer}
          className="shrink-0 rounded-full border border-slate-300 bg-white px-2.5 py-1 text-[10px] font-semibold text-slate-600 hover:border-uni-300 hover:text-uni-700"
        >
          Restablecer
        </button>
      </div>

      <div
        ref={contenedorRef}
        onWheel={manejarRueda}
        onPointerDown={manejarPointerDown}
        onPointerMove={manejarPointerMove}
        onPointerUp={manejarPointerUp}
        onPointerCancel={manejarPointerUp}
        onPointerLeave={manejarPointerUp}
        className="relative aspect-square w-full touch-none overflow-hidden rounded-lg border border-slate-200 bg-slate-100"
        style={{ cursor: zoom > 1 ? 'grab' : 'default' }}
      >
        <div
          className="absolute inset-0"
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: 'center center',
          }}
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={p.imagen}
            alt={`Recorte de la plancha geológica en el ${p.nombre}`}
            className="absolute inset-0 h-full w-full select-none object-cover"
            draggable={false}
          />

          {unidadActiva && (
            <>
              <div className="absolute inset-0 bg-black/35" />
              <div
                className="absolute inset-0"
                style={{
                  backgroundColor: unidadActiva.color,
                  opacity: 0.6,
                  WebkitMaskImage: `url(${unidadActiva.mascara})`,
                  maskImage: `url(${unidadActiva.mascara})`,
                  WebkitMaskSize: '100% 100%',
                  maskSize: '100% 100%',
                  WebkitMaskRepeat: 'no-repeat',
                  maskRepeat: 'no-repeat',
                }}
              />
            </>
          )}

          <svg viewBox={`0 0 ${L} ${L}`} className="absolute inset-0 h-full w-full" style={{ pointerEvents: 'none' }}>
            {/* Marcador del portal: círculo rojo con cruz */}
            <circle cx={px} cy={py} r={L * 0.014} fill="none" stroke="#dc2626" strokeWidth={L * 0.004} />
            <line x1={px - L * 0.022} y1={py} x2={px + L * 0.022} y2={py} stroke="#dc2626" strokeWidth={L * 0.004} />
            <line x1={px} y1={py - L * 0.022} x2={px} y2={py + L * 0.022} stroke="#dc2626" strokeWidth={L * 0.004} />

            {/* Barra de escala: 1 km */}
            <g>
              <line
                x1={L * 0.04} y1={L * 0.94} x2={L * 0.04 + p.px_por_km} y2={L * 0.94}
                stroke="#0f172a" strokeWidth={L * 0.004}
              />
              <line x1={L * 0.04} y1={L * 0.93} x2={L * 0.04} y2={L * 0.95} stroke="#0f172a" strokeWidth={L * 0.004} />
              <line
                x1={L * 0.04 + p.px_por_km} y1={L * 0.93} x2={L * 0.04 + p.px_por_km} y2={L * 0.95}
                stroke="#0f172a" strokeWidth={L * 0.004}
              />
              <text
                x={L * 0.04 + p.px_por_km / 2} y={L * 0.91} textAnchor="middle" fontSize={L * 0.028}
                fontWeight={700} fill="#0f172a" stroke="white" strokeWidth={L * 0.01} paintOrder="stroke"
              >
                1 km
              </text>
            </g>

            {/* Flecha de norte */}
            <g transform={`translate(${L * 0.92}, ${L * 0.1})`}>
              <line x1={0} y1={L * 0.05} x2={0} y2={-L * 0.03} stroke="#0f172a" strokeWidth={L * 0.004} />
              <polygon
                points={`0,${-L * 0.05} ${-L * 0.018},${-L * 0.018} ${L * 0.018},${-L * 0.018}`}
                fill="#0f172a"
              />
              <text
                x={0} y={L * 0.08} textAnchor="middle" fontSize={L * 0.03} fontWeight={700} fill="#0f172a"
                stroke="white" strokeWidth={L * 0.01} paintOrder="stroke"
              >
                N
              </text>
            </g>
          </svg>
        </div>
      </div>

      {/* Leyenda: accesible por teclado (botones) */}
      <div className="space-y-1.5">
        {p.unidades.map((u, i) => (
          <button
            key={u.simbolo}
            type="button"
            onMouseEnter={() => setHoverIdx(i)}
            onFocus={() => setHoverIdx(i)}
            onMouseLeave={() => setHoverIdx((v) => (v === i ? null : v))}
            onBlur={() => setHoverIdx((v) => (v === i ? null : v))}
            className={`flex w-full items-start gap-2.5 rounded-lg border px-2.5 py-2 text-left transition-colors ${
              hoverIdx === i ? 'border-uni-300 bg-uni-50' : 'border-slate-200 bg-white'
            }`}
          >
            <span
              className="mt-0.5 h-4 w-4 shrink-0 rounded border border-slate-300"
              style={{ backgroundColor: u.color }}
            />
            <span className="min-w-0 flex-1">
              <span className="flex flex-wrap items-baseline gap-x-1.5 gap-y-0.5">
                <span className="font-mono text-[11px] font-bold text-slate-700">{u.simbolo}</span>
                <span className="text-xs font-semibold text-uni-900">{u.nombre}</span>
                <span className="text-[10px] text-slate-500">· {u.edad}</span>
                <span className="text-[10px] font-semibold text-slate-500">
                  · {u.dist_portal_m === 0 ? 'bajo el portal' : `a ${es(u.dist_portal_m)} m del portal`}
                </span>
                <span
                  title="Cálculo propio del semillero"
                  className="shrink-0 rounded border border-blue-500/30 bg-blue-500/10 px-1 py-0.5 text-[9px] font-bold text-blue-700"
                >
                  CP
                </span>
              </span>
              <span className="mt-0.5 flex items-start gap-1.5 text-[11px] leading-relaxed text-slate-500">
                <span>{u.descripcion}</span>
                <span
                  title="Dato de la ponencia de referencia / la plancha geológica"
                  className="mt-0.5 shrink-0 rounded border border-emerald-500/30 bg-emerald-500/10 px-1 py-0.5 text-[9px] font-bold text-emerald-700"
                >
                  F
                </span>
              </span>
            </span>
          </button>
        ))}
      </div>

      <p className="text-[11px] leading-relaxed text-slate-500">
        {p.fuente} Ubicación del portal ±0,1 km. Recorte de ≈{es(p.lado_km, 2)} km de lado.
      </p>
    </div>
  );
}

export function VisorGeologiaOE3() {
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {oe3Geologia.portales.map((p) => (
        <VisorPortal key={p.id} portal={p} />
      ))}
    </div>
  );
}

export default VisorGeologiaOE3;
