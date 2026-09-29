'use client';

/**
 * LaminasOE5 — el contenido de las láminas de la Act 4 del OE 5, dibujado en el
 * navegador en lugar de mostrarse como imagen:
 *   - MapaSiniestralidadOE5: un solo mapa con selector de tres estados que
 *     fusiona los seis sectores críticos 2015–2019 (Gi*) y el microdato ANSV
 *     georreferenciado 2021 – mar 2026, sobre el trazado del OE 1. Con el
 *     microdato activo, la vía se pinta tramo a tramo según su densidad lineal
 *     de siniestros (`via_densidad`) en vez de dibujarse de un solo color.
 *   - PrensaMicrodatoOE5: la tabla de cruce entre el microdato y los siniestros
 *     fatales que documentó la prensa, para el plegado homónimo.
 *
 * Datos: `src/data/mapas_oe5.json`, generado por
 * OE5_SeguridadVial/Act4_Analisis/exportar_web_OE5.py. Ninguna cifra se escribe aquí.
 * El fondo de los mapas es un sombreado del DEM (Copernicus GLO-30) en EPSG:4686, así que
 * la conversión longitud/latitud → píxel es lineal dentro de la ventana declarada.
 * Las láminas JPG siguen siendo el entregable y quedan enlazadas para descarga.
 */

import React, { useState } from 'react';
import mapas from '@/data/mapas_oe5.json';

const AZUL = '#193F77';
const AZUL_CLARO = '#7BA0D4';
const TINTA = '#0F2449';
/* Rampa de densidad de siniestros sobre la vía: un solo tono, naranja claro a
   rojo oscuro, con un paso medio para que el contraste se note sobre el
   relieve incluso a d bajas. El extremo claro (d=0) es más saturado que un
   simple beige para que los tramos sin siniestros se distingan del fondo. */
const DENSIDAD_CLARO: [number, number, number] = [243, 201, 154]; // #F3C99A
const DENSIDAD_MEDIO: [number, number, number] = [240, 138, 60]; // #F08A3C
const DENSIDAD_OSCURO: [number, number, number] = [140, 29, 11]; // #8C1D0B

const es = (v: number, d = 0) =>
  v.toLocaleString('es-CO', { minimumFractionDigits: d, maximumFractionDigits: d });

type Ventana = { bounds: number[]; img: string };

/** Proyección lineal lon/lat → coordenadas del viewBox (ancho 1000). */
function proyector(v: Ventana) {
  const [lon0, lat0, lon1, lat1] = v.bounds;
  const W = 1000;
  const H = (W * (lat1 - lat0)) / (lon1 - lon0);
  return {
    W,
    H,
    x: (lon: number) => ((lon - lon0) / (lon1 - lon0)) * W,
    y: (lat: number) => ((lat1 - lat) / (lat1 - lat0)) * H,
  };
}
type Proyector = ReturnType<typeof proyector>;

function Fondo({ v, children, etiqueta }: { v: Ventana; children: React.ReactNode; etiqueta: string }) {
  const p = proyector(v);
  return (
    <svg viewBox={`0 0 ${p.W} ${p.H}`} className="h-auto w-full rounded-lg border border-slate-200 bg-slate-100"
         role="img" aria-label={etiqueta}>
      <image href={v.img} x={0} y={0} width={p.W} height={p.H} preserveAspectRatio="none" />
      {children}
    </svg>
  );
}

function Rotulo({ x, y, texto, ancla = 'middle', tam = 15, color = '#5B6B80' }:
  { x: number; y: number; texto: string; ancla?: 'start' | 'middle' | 'end'; tam?: number; color?: string }) {
  return (
    <text x={x} y={y} textAnchor={ancla} fontSize={tam} fontWeight={700} fill={color}
          stroke="white" strokeWidth={4} paintOrder="stroke" style={{ pointerEvents: 'none' }}>
      {texto}
    </text>
  );
}

/** Vía actual (Ruta 40) [F, OSM], de un solo color: se usa cuando el microdato no está activo. */
function ViaActualCapa({ p }: { p: Proyector }) {
  return (
    <g>
      {mapas.via.map((seg, i) => {
        const pts = seg.coords.map(([lo, la]) => `${p.x(lo)},${p.y(la)}`).join(' ');
        return (
          <polyline key={i} points={pts} fill="none" stroke="#7A2E12" strokeWidth={2.5}
                     strokeOpacity={seg.tunel ? 0.35 : 1} strokeLinecap="round" />
        );
      })}
    </g>
  );
}

/** Interpola en dos pasos: claro → medio (t 0–0,5) y medio → oscuro (t 0,5–1). */
function colorDensidad(t: number) {
  const c = Math.max(0, Math.min(1, t));
  const [a, b] = c < 0.5 ? [DENSIDAD_CLARO, DENSIDAD_MEDIO] : [DENSIDAD_MEDIO, DENSIDAD_OSCURO];
  const local = c < 0.5 ? c / 0.5 : (c - 0.5) / 0.5;
  const rgb = a.map((v, i) => Math.round(v + (b[i] - v) * local));
  return `rgb(${rgb.join(',')})`;
}

/** Vía coloreada tramo a tramo por su densidad lineal de siniestros (microdato ANSV) [CP].
    El halo blanco se dibuja UNA sola vez como polilínea continua (los 305 tramos de
    via_densidad son contiguos, cada uno empieza donde termina el anterior), para que
    se lea sobre el relieve y sobre el trazado del túnel, encima de los cuales se
    dibuja siempre esta capa. Los tramos coloreados van encima del halo, con extremos
    a escuadra: como comparten vértices exactos y el mismo ancho, no dejan costuras. */
function ViaDensidadCapa({ p }: { p: Proyector }) {
  const tramos = mapas.via_densidad.tramos;
  const max = mapas.via_densidad.max;
  const puntosHalo = [tramos[0].c[0], ...tramos.map((t) => t.c[1])]
    .map(([lo, la]) => `${p.x(lo)},${p.y(la)}`)
    .join(' ');

  return (
    <g>
      <polyline points={puntosHalo} fill="none" stroke="white" strokeWidth={10}
                strokeLinecap="round" strokeLinejoin="round" />
      {tramos.map((t, i) => {
        const [[lo0, la0], [lo1, la1]] = t.c;
        return (
          <line key={i} x1={p.x(lo0)} y1={p.y(la0)} x2={p.x(lo1)} y2={p.y(la1)}
                stroke={colorDensidad(t.d / max)} strokeWidth={7}
                strokeLinecap="butt" strokeLinejoin="round" />
        );
      })}
    </g>
  );
}

function Ficha({ titulo, filas }: { titulo: string; filas: [string, string][] }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs">
      <p className="mb-2 font-bold text-uni-900">{titulo}</p>
      <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1">
        {filas.map(([k, v]) => (
          <React.Fragment key={k}>
            <dt className="text-slate-500">{k}</dt>
            <dd className="font-semibold text-slate-700">{v}</dd>
          </React.Fragment>
        ))}
      </dl>
    </div>
  );
}

/* =================================================================== mapa único */

type Sector = (typeof mapas.sectores)[number];
type Punto = (typeof mapas.microdato.puntos)[number];
type Capa = 'gi' | 'microdato' | 'ambos';

const OPCIONES_CAPA: { k: Capa; label: string }[] = [
  { k: 'gi', label: '2015–2019 · sectores críticos (Gi*)' },
  { k: 'microdato', label: '2021 – mar 2026 · microdato ANSV' },
  { k: 'ambos', label: 'Ambos' },
];

export function MapaSiniestralidadOE5() {
  const [capa, setCapa] = useState<Capa>('gi');
  const [detalle, setDetalle] = useState(false);
  const [soloCalor, setSoloCalor] = useState(false);
  const [selSector, setSelSector] = useState<number | null>(null);
  const [selPunto, setSelPunto] = useState<number | null>(null);

  const v: Ventana = detalle ? mapas.descenso : mapas.corredor;
  const p = proyector(v);
  const pts = mapas.trazado.map(([lo, la]) => `${p.x(lo)},${p.y(la)}`).join(' ');

  const mostrarGi = capa === 'gi' || capa === 'ambos';
  const mostrarMicrodato = capa === 'microdato' || capa === 'ambos';
  /* «Solo calor» únicamente aplica junto al microdato: en el estado Gi* puro
     no hay vía coloreada que aislar, así que ahí los círculos siempre se ven. */
  const ocultarCirculos = soloCalor && mostrarMicrodato;

  const fmax = Math.max(...mapas.sectores.map((s) => s.fallecidos));
  const ordenSectores = [...mapas.sectores].sort((a, b) => b.fallecidos - a.fallecidos || a.lon - b.lon);
  const radioSector = (s: Sector) => (detalle ? 16 : 7) + (detalle ? 30 : 16) * Math.sqrt(s.fallecidos / fmax);

  const nmax = Math.max(...mapas.microdato.puntos.map((q) => q.hechos));
  /* Radio máximo ~60 % del de los sectores Gi*, para que no compitan con la vía coloreada. */
  const radioPunto = (q: Punto) => 0.6 * ((detalle ? 10 : 6) + (detalle ? 22 : 18) * Math.sqrt(q.hechos / nmax));

  const sectorSel: Sector | null = selSector !== null ? ordenSectores[selSector] : null;
  const puntoSel: Punto | null = selPunto !== null ? mapas.microdato.puntos[selPunto] : null;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2 text-[11px]">
        {OPCIONES_CAPA.map((op) => (
          <button
            key={op.k}
            type="button"
            onClick={() => setCapa(op.k)}
            className={`rounded-full border px-3 py-1 font-semibold ${
              capa === op.k ? 'border-uni-700 bg-uni-700 text-white' : 'border-slate-300 bg-white text-slate-600'
            }`}
          >
            {op.label}
          </button>
        ))}
        {mostrarMicrodato && (
          <button
            type="button"
            onClick={() => setSoloCalor((v) => !v)}
            className={`rounded-full border px-3 py-1 font-semibold ${
              soloCalor ? 'border-uni-700 bg-uni-700 text-white' : 'border-slate-300 bg-white text-slate-600'
            }`}
          >
            Solo calor
          </button>
        )}
        <button
          type="button"
          onClick={() => setDetalle((d) => !d)}
          className={`ml-auto rounded-full border px-3 py-1 font-semibold ${
            detalle ? 'border-uni-700 bg-uni-700 text-white' : 'border-slate-300 bg-white text-slate-600'
          }`}
        >
          {detalle ? 'Ver corredor completo' : 'Acercar al descenso a Calarcá (3,6 km)'}
        </button>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_260px]">
        <Fondo v={v} etiqueta="Siniestralidad del corredor Ibagué – Calarcá">
          {!mostrarMicrodato && <ViaActualCapa p={p} />}

          {/* Los círculos del microdato van debajo de la vía coloreada: son
              contexto de dónde cae cada hecho, no compiten con el calor. */}
          {mostrarMicrodato && !ocultarCirculos && mapas.microdato.puntos.map((pt, i) => (
            <circle key={`m${i}`} cx={p.x(pt.lon)} cy={p.y(pt.lat)} r={radioPunto(pt)}
                    fill={TINTA} fillOpacity={0.25}
                    stroke={selPunto === i ? '#F59E0B' : TINTA} strokeWidth={selPunto === i ? 3 : 1.5}
                    style={{ cursor: 'pointer' }} onClick={() => setSelPunto(i)} onMouseEnter={() => setSelPunto(i)} />
          ))}

          <polyline points={pts} fill="none" stroke="white" strokeWidth={7} strokeLinecap="round" />
          <polyline points={pts} fill="none" stroke={AZUL} strokeWidth={3.5} strokeLinecap="round" />

          {/* La vía coloreada por densidad va encima del trazado del túnel y
              de la vía actual/Túnel de La Línea que dibuja ViaActualCapa. */}
          {mostrarMicrodato && <ViaDensidadCapa p={p} />}

          {!detalle && (
            <>
              {(['oriental', 'occidental'] as const).map((k) => {
                const [lo, la] = mapas.portales[k];
                return (
                  <g key={k}>
                    <circle cx={p.x(lo)} cy={p.y(la)} r={8} fill={AZUL} stroke="white" strokeWidth={3} />
                    <Rotulo x={p.x(lo) + (k === 'oriental' ? 12 : -8)} y={p.y(la) + 28}
                            texto={k === 'oriental' ? 'Portal oriental · Ibagué' : 'Portal occidental · Calarcá'}
                            ancla={k === 'oriental' ? 'end' : 'start'} tam={14} color={AZUL} />
                  </g>
                );
              })}
              <Rotulo x={p.x(-75.427)} y={p.y(4.428)} texto="CAJAMARCA" />
            </>
          )}

          {mostrarGi && !ocultarCirculos && ordenSectores.map((sec, i) => (
            <g key={`s${i}`} onClick={() => setSelSector(i)} onMouseEnter={() => setSelSector(i)} style={{ cursor: 'pointer' }}>
              <circle cx={p.x(sec.lon)} cy={p.y(sec.lat)} r={radioSector(sec)}
                      fill={sec.confianza === '99 %' ? AZUL : AZUL_CLARO} fillOpacity={0.9}
                      stroke={selSector === i ? '#F59E0B' : 'white'} strokeWidth={selSector === i ? 4 : 2.5} />
              {detalle && (() => {
                /* Si el círculo se pisa con uno anterior, su número sale afuera con línea guía;
                   la posición del círculo no se mueve. */
                const cx = p.x(sec.lon);
                const cy = p.y(sec.lat);
                const previos = ordenSectores.slice(0, i).filter((o) => Math.hypot(p.x(o.lon) - cx, p.y(o.lat) - cy) < 60).length;
                if (!previos) {
                  return <text x={cx} y={cy + 6} textAnchor="middle" fontSize={17} fontWeight={800}
                               fill="white" style={{ pointerEvents: 'none' }}>{i + 1}</text>;
                }
                const ang = 2.4 + 1.1 * previos;
                const lx = cx + 90 * Math.cos(ang);
                const ly = cy - 90 * Math.sin(ang);
                return (
                  <g style={{ pointerEvents: 'none' }}>
                    <line x1={cx} y1={cy} x2={lx} y2={ly} stroke="#5B6B80" strokeWidth={1.5} />
                    <circle cx={lx} cy={ly} r={15} fill="white" stroke="#5B6B80" strokeWidth={1.5} />
                    <text x={lx} y={ly + 6} textAnchor="middle" fontSize={16} fontWeight={800} fill={TINTA}>{i + 1}</text>
                  </g>
                );
              })()}
            </g>
          ))}
        </Fondo>

        <div className="space-y-3">
          {mostrarGi && !ocultarCirculos && sectorSel && (
            <Ficha titulo={`${sectorSel.pr} · ${sectorSel.tramo}`} filas={[
              ['Fallecidos 2015–2019', es(sectorSel.fallecidos)],
              ['Confianza Gi*', `${sectorSel.confianza} (z = ${es(sectorSel.gi_z, 2)})`],
              ['A cargo de', sectorSel.entidad],
              ['¿Entra en la tasa?', sectorSel.en_tasa ? 'Sí' : 'No — tramo de la ANI'],
            ]} />
          )}
          {mostrarMicrodato && !ocultarCirculos && puntoSel && (
            <Ficha titulo={`km ${es(puntoSel.km, 1)} · ${puntoSel.municipio}`} filas={[
              ['Tramo', puntoSel.tramo],
              ['Hechos', `${es(puntoSel.hechos)} (${es(puntoSel.hechos_fatales)} con fallecido)`],
              ['Fallecidos', es(puntoSel.fallecidos)],
              ['Lesionados', es(puntoSel.lesionados)],
            ]} />
          )}
          <ul className="space-y-1.5 text-[11px] text-slate-600">
            {mostrarGi && !ocultarCirculos && (
              <>
                <li className="flex items-center gap-2"><span className="h-3 w-3 rounded-full" style={{ background: AZUL }} />Sector crítico · 99 % de confianza</li>
                <li className="flex items-center gap-2"><span className="h-3 w-3 rounded-full" style={{ background: AZUL_CLARO }} />Sector crítico · 95 % de confianza</li>
              </>
            )}
            {mostrarMicrodato && !ocultarCirculos && (
              <li className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full border-[1.5px]" style={{ borderColor: TINTA, background: TINTA, opacity: 0.25 }} />
                Punto del microdato · tamaño = hechos
              </li>
            )}
            <li className="flex items-center gap-2"><span className="h-0.5 w-5" style={{ background: AZUL }} />Trazado del túnel (OE 1)</li>
            {!mostrarMicrodato && (
              <li className="flex items-center gap-2"><span className="h-0.5 w-5" style={{ background: '#7A2E12' }} />Vía actual, Ruta 40 [F, OSM]</li>
            )}
            <li className="flex items-center gap-2"><span className="h-0.5 w-5 opacity-35" style={{ background: '#7A2E12' }} />Túnel de La Línea (2020)</li>
          </ul>

          {mostrarMicrodato && (
            <div className="space-y-1 border-t border-slate-200 pt-3">
              <div className="flex items-center gap-1.5">
                <span className="text-[11px] font-semibold text-slate-600">
                  Siniestros por km de vía, núcleo gaussiano, banda 1,5 km
                </span>
                <span
                  title="Cálculo propio del semillero"
                  className="shrink-0 rounded border border-blue-500/30 bg-blue-500/10 px-1 py-0.5 text-[9px] font-bold text-blue-700"
                >
                  CP
                </span>
              </div>
              <div
                className="h-2.5 w-full rounded-sm"
                style={{ background: `linear-gradient(90deg, rgb(${DENSIDAD_CLARO.join(',')}), rgb(${DENSIDAD_MEDIO.join(',')}), rgb(${DENSIDAD_OSCURO.join(',')}))` }}
              />
              <div className="flex justify-between text-[10px] text-slate-500">
                <span>0</span>
                <span>máx. {es(mapas.via_densidad.max, 1)} siniestros/km</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <p className="text-[11px] leading-relaxed text-slate-500">
        {mostrarGi && 'Sectores críticos: ANSV, Sectores Críticos de Siniestralidad Vial (rs3u-8r4q) [F]; nivel de confianza leído del Getis-Ord Gi* que publica la propia fuente. '}
        {mostrarMicrodato && 'Microdato: ANSV, oficio 20265000140371 del 22 sep 2026 (solicitud de D. Torrente), fuente primaria INMLCF [F]; densidad, abscisa y tramos: procesar_microdato_ANSV_OE5.py [CP]. '}
        Trazado: OE 1 [CP]. Relieve: Copernicus DEM GLO-30. Vía: © colaboradores de OpenStreetMap.
      </p>
    </div>
  );
}

/* =================================================================== prensa */

/** Cruce entre el microdato y los siniestros fatales que documentó la prensa. */
export function PrensaMicrodatoOE5() {
  const R = mapas.microdato.resumen;
  return (
    <div className="space-y-3">
      <p className="text-xs leading-relaxed text-slate-600">
        De los <strong className="text-slate-700">{R.prensa.total}</strong> siniestros fatales que
        documentó la prensa entre 2022 y 2025, el anexo de la ANSV georreferencia{' '}
        <strong className="text-slate-700">{R.prensa.en_anexo}</strong>.
      </p>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[520px] text-left text-[11px]">
          <thead className="bg-uni-800 text-white">
            <tr>{['Fecha', 'Hecho', 'Muertos en prensa', 'En el anexo'].map((h) => <th key={h} className="px-2 py-1.5 font-semibold">{h}</th>)}</tr>
          </thead>
          <tbody>
            {mapas.microdato.prensa.map((r) => {
              const [y, m, d] = r.fecha.split('-');
              const si = r.en_anexo_ANSV === 'si';
              return (
                <tr key={r.fecha} className={`border-b border-slate-100 ${si ? 'text-slate-800' : 'text-slate-500'}`}>
                  <td className="px-2 py-1.5 font-mono">{`${d}/${m}/${y}`}</td>
                  <td className="px-2 py-1.5">{r.hecho}</td>
                  <td className="px-2 py-1.5">{r.muertos_prensa.replace('no indicado', 's. d.')}</td>
                  <td className="px-2 py-1.5 font-semibold" style={{ color: si ? AZUL : undefined }}>
                    {si ? `Sí · ${r.fallecidos_anexo}` : 'No'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="text-[11px] leading-relaxed text-slate-500">
        Fuente: ANSV – Observatorio Nacional de Seguridad Vial, oficio 20265000140371 del 22 sep 2026
        (solicitud de D. Torrente) [F]. Prensa: El Tiempo, El Espectador, Infobae.
      </p>
    </div>
  );
}
