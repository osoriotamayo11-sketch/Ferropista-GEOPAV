'use client';

/**
 * LaminasOE5 — el contenido de las dos láminas de la Act 4 del OE 5, dibujado en el
 * navegador en lugar de mostrarse como imagen:
 *   - MapaSectoresOE5: los seis sectores críticos 2015–2019 sobre el trazado del OE 1,
 *     con el detalle del descenso a Calarcá.
 *   - DensidadLinealOE5: el microdato ANSV 2021 – mar 2026 (mapa de puntos, cruce con
 *     prensa, franja de densidad lineal y hechos por kilómetro).
 *
 * Datos: `src/data/mapas_oe5.json`, generado por
 * OE5_SeguridadVial/Act4_Analisis/exportar_web_OE5.py. Ninguna cifra se escribe aquí.
 * El fondo de los mapas es un sombreado del DEM (Copernicus GLO-30) en EPSG:4686, así que
 * la conversión longitud/latitud → píxel es lineal dentro de la ventana declarada.
 * Las láminas PNG siguen siendo el entregable y quedan enlazadas para descarga.
 */

import React, { useMemo, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceArea,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import mapas from '@/data/mapas_oe5.json';

const AZUL = '#193F77';
const AZUL_CLARO = '#7BA0D4';
const GRIS = '#94A3B8';
const TINTA = '#0F2449';

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

/* =================================================================== sectores */

type Sector = (typeof mapas.sectores)[number];

export function MapaSectoresOE5() {
  const [detalle, setDetalle] = useState(false);
  const [sel, setSel] = useState<number | null>(0);
  const v: Ventana = detalle ? mapas.descenso : mapas.corredor;
  const p = proyector(v);
  const fmax = Math.max(...mapas.sectores.map((s) => s.fallecidos));
  /* Mismo orden que la lámina: fallecidos de mayor a menor y, en empate, de oeste a este. */
  const orden = [...mapas.sectores].sort((a, b) => b.fallecidos - a.fallecidos || a.lon - b.lon);
  const radio = (s: Sector) => (detalle ? 16 : 7) + (detalle ? 30 : 16) * Math.sqrt(s.fallecidos / fmax);
  const s = sel !== null ? orden[sel] : null;
  const pts = mapas.trazado.map(([lo, la]) => `${p.x(lo)},${p.y(la)}`).join(' ');

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2 text-[11px]">
        <button onClick={() => setDetalle(false)}
                className={`rounded-full border px-3 py-1 font-semibold ${!detalle ? 'border-uni-700 bg-uni-700 text-white' : 'border-slate-300 bg-white text-slate-600'}`}>
          Corredor completo
        </button>
        <button onClick={() => setDetalle(true)}
                className={`rounded-full border px-3 py-1 font-semibold ${detalle ? 'border-uni-700 bg-uni-700 text-white' : 'border-slate-300 bg-white text-slate-600'}`}>
          Detalle del descenso a Calarcá (3,6 km)
        </button>
        <span className="text-slate-500">Toca un círculo para ver su ficha.</span>
      </div>
      <div className="grid gap-4 lg:grid-cols-[1fr_260px]">
        <Fondo v={v} etiqueta="Sectores críticos de la ANSV sobre el trazado del túnel">
          <polyline points={pts} fill="none" stroke="white" strokeWidth={7} strokeLinecap="round" />
          <polyline points={pts} fill="none" stroke={AZUL} strokeWidth={3.5} strokeLinecap="round" />
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
          {orden.map((sec, i) => (
            <g key={i} onClick={() => setSel(i)} onMouseEnter={() => setSel(i)} style={{ cursor: 'pointer' }}>
              <circle cx={p.x(sec.lon)} cy={p.y(sec.lat)} r={radio(sec)}
                      fill={sec.confianza === '99 %' ? AZUL : AZUL_CLARO} fillOpacity={0.9}
                      stroke={sel === i ? '#F59E0B' : 'white'} strokeWidth={sel === i ? 4 : 2.5} />
              {detalle && (() => {
                /* Si el círculo se pisa con uno anterior, su número sale afuera con línea guía;
                   la posición del círculo no se mueve. */
                const cx = p.x(sec.lon), cy = p.y(sec.lat);
                const previos = orden.slice(0, i).filter((o) => Math.hypot(p.x(o.lon) - cx, p.y(o.lat) - cy) < 60).length;
                if (!previos) {
                  return <text x={cx} y={cy + 6} textAnchor="middle" fontSize={17} fontWeight={800}
                               fill="white" style={{ pointerEvents: 'none' }}>{i + 1}</text>;
                }
                const ang = 2.4 + 1.1 * previos;
                const lx = cx + 90 * Math.cos(ang), ly = cy - 90 * Math.sin(ang);
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
          {s && (
            <Ficha titulo={`${s.pr} · ${s.tramo}`} filas={[
              ['Fallecidos 2015–2019', es(s.fallecidos)],
              ['Confianza Gi*', `${s.confianza} (z = ${es(s.gi_z, 2)})`],
              ['A cargo de', s.entidad],
              ['¿Entra en la tasa?', s.en_tasa ? 'Sí' : 'No — tramo de la ANI'],
            ]} />
          )}
          <ul className="space-y-1.5 text-[11px] text-slate-600">
            <li className="flex items-center gap-2"><span className="h-3 w-3 rounded-full" style={{ background: AZUL }} />Sector crítico · 99 % de confianza</li>
            <li className="flex items-center gap-2"><span className="h-3 w-3 rounded-full" style={{ background: AZUL_CLARO }} />Sector crítico · 95 % de confianza</li>
            <li className="flex items-center gap-2"><span className="h-0.5 w-5" style={{ background: AZUL }} />Trazado del túnel (OE 1)</li>
            <li>Tamaño del círculo = fallecidos 2015–2019.</li>
          </ul>
        </div>
      </div>
      <p className="text-[11px] leading-relaxed text-slate-500">
        Fuente: ANSV, Sectores Críticos de Siniestralidad Vial (rs3u-8r4q) [F]; nivel de confianza leído del
        Getis-Ord Gi* que publica la propia fuente. Trazado: OE 1 [CP]. Relieve: Copernicus DEM GLO-30.
      </p>
    </div>
  );
}

/* =================================================================== microdato */

const MD = mapas.microdato;
type Punto = (typeof MD.puntos)[number];

function FranjaDensidad() {
  const vals = MD.densidad.valores;
  const max = Math.max(...vals);
  const paso = MD.densidad.paso_km;
  const fin = MD.resumen.limites_tramo_km.fin;
  const W = 1000;
  const color = (v: number) => {
    const t = v / max;
    const a = [247, 249, 251], b = [123, 160, 212], c = [25, 63, 119];
    const m = (u: number[], w: number[], k: number) => u.map((x, i) => Math.round(x + (w[i] - x) * k));
    const rgb = t < 0.5 ? m(a, b, t / 0.5) : m(b, c, (t - 0.5) / 0.5);
    return `rgb(${rgb.join(',')})`;
  };
  const x = (km: number) => 24 + (km / fin) * (W - 48);
  const L = MD.resumen.limites_tramo_km;
  return (
    <svg viewBox={`0 0 ${W} 70`} className="h-auto w-full" role="img" aria-label="Franja de densidad lineal de hechos">
      {vals.map((v, i) => (
        <rect key={i} x={x(i * paso)} y={10} width={x(paso) - x(0) + 0.6} height={34} fill={color(v)} />
      ))}
      <rect x={x(0)} y={10} width={x(fin) - x(0)} height={34} fill="none" stroke="#CBD5E1" />
      {[L.calarca, L.cajamarca].map((k) => (
        <line key={k} x1={x(k)} x2={x(k)} y1={4} y2={50} stroke="#5B6B80" strokeDasharray="3 3" />
      ))}
      {[0, 10, 20, 30, 40, 50, 60, 70, 80].map((k) => (
        <text key={k} x={x(k)} y={64} fontSize={11} textAnchor="middle" fill="#64748B">km {k}</text>
      ))}
    </svg>
  );
}

function TipKm({ active, payload }: { active?: boolean; payload?: { payload: Record<string, number | string> }[] }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-2 text-[11px] shadow">
      <p className="font-bold text-uni-900">km {d.km_desde} – {d.km_hasta}</p>
      <p className="text-slate-600">{d.tramo}</p>
      <p>Hechos: <b>{d.hechos}</b> (con fallecido: {d.hechos_fatales})</p>
      <p>Fallecidos: <b>{d.fallecidos}</b> · Lesionados: <b>{d.lesionados}</b></p>
    </div>
  );
}

export function DensidadLinealOE5() {
  const [sel, setSel] = useState<number | null>(0);
  const v: Ventana = mapas.corredor;
  const p = proyector(v);
  const nmax = Math.max(...MD.puntos.map((q) => q.hechos));
  const pts = mapas.trazado.map(([lo, la]) => `${p.x(lo)},${p.y(la)}`).join(' ');
  const barras = useMemo(
    () => MD.por_km.map((r) => ({ ...r, no_fatales: r.hechos - r.hechos_fatales, etiqueta: r.km_desde })),
    [],
  );
  const q: Punto | null = sel !== null ? MD.puntos[sel] : null;
  const R = MD.resumen;
  const T = MD.tasa_post_tunel;
  const L = R.limites_tramo_km;

  return (
    <div className="space-y-5">
      <p className="text-xs leading-relaxed text-slate-600">
        <b>{es(R.victimas)} víctimas</b> ({es(R.fallecidos)} fallecidos, {es(R.lesionados)} lesionados) en{' '}
        <b>{es(R.hechos)} hechos</b> y solo {R.puntos_distintos_hechos} puntos distintos, entre el{' '}
        {R.periodo[0].split('-').reverse().join('/')} y el {R.periodo[1].split('-').reverse().join('/')}. Tasa del paso 2021–2025, como cota inferior [H]: <b>{es(T.tasa_H1, 2)}</b> a{' '}
        <b>{es(T.tasa_H2, 2)}</b> fallecidos por 10<sup>8</sup> veh-km; no es comparable con la de 2015–2019.
      </p>

      {/* A · mapa */}
      <div className="grid gap-4 lg:grid-cols-[1fr_260px]">
        <div>
          <p className="mb-2 text-xs font-bold text-uni-900">A · Dónde cayeron los hechos</p>
          <Fondo v={v} etiqueta="Puntos georreferenciados por la ANSV en la Ruta 4003">
            <polyline points={pts} fill="none" stroke={GRIS} strokeWidth={3} strokeDasharray="10 7" />
            <Rotulo x={p.x(-75.640)} y={p.y(4.505)} texto="Calarcá" />
            <Rotulo x={p.x(-75.427)} y={p.y(4.420)} texto="Cajamarca" />
            <Rotulo x={p.x(-75.245)} y={p.y(4.385)} texto="Ibagué" />
            {MD.puntos.map((pt, i) => (
              <circle key={i} cx={p.x(pt.lon)} cy={p.y(pt.lat)} r={6 + 18 * Math.sqrt(pt.hechos / nmax)}
                      fill={pt.fallecidos ? AZUL : AZUL_CLARO} fillOpacity={0.9}
                      stroke={sel === i ? '#F59E0B' : 'white'} strokeWidth={sel === i ? 4 : 2}
                      style={{ cursor: 'pointer' }} onClick={() => setSel(i)} onMouseEnter={() => setSel(i)} />
            ))}
          </Fondo>
        </div>
        <div className="space-y-3 lg:pt-6">
          {q && (
            <Ficha titulo={`km ${es(q.km, 1)} · ${q.municipio}`} filas={[
              ['Tramo', q.tramo],
              ['Hechos', `${es(q.hechos)} (${es(q.hechos_fatales)} con fallecido)`],
              ['Fallecidos', es(q.fallecidos)],
              ['Lesionados', es(q.lesionados)],
            ]} />
          )}
          <ul className="space-y-1.5 text-[11px] text-slate-600">
            <li className="flex items-center gap-2"><span className="h-3 w-3 rounded-full" style={{ background: AZUL }} />Punto con al menos un fallecido</li>
            <li className="flex items-center gap-2"><span className="h-3 w-3 rounded-full" style={{ background: AZUL_CLARO }} />Punto solo con lesionados</li>
            <li className="flex items-center gap-2"><span className="h-0.5 w-5 border-t-2 border-dashed" style={{ borderColor: GRIS }} />Trazado del túnel (OE 1)</li>
            <li>Tamaño = hechos en ese punto. El punto de Calarcá urbano con {R.punto_mas_cargado_hechos.hechos} hechos
              parece un punto por defecto de la georreferenciación.</li>
          </ul>
        </div>
      </div>

      {/* B · prensa */}
      <div>
        <p className="mb-2 text-xs font-bold text-uni-900">
          B · ¿Están en el anexo los fatales conocidos por prensa? Figuran {R.prensa.en_anexo} de {R.prensa.total}.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[520px] text-left text-[11px]">
            <thead className="bg-uni-800 text-white">
              <tr>{['Fecha', 'Hecho', 'Muertos en prensa', 'En el anexo'].map((h) => <th key={h} className="px-2 py-1.5 font-semibold">{h}</th>)}</tr>
            </thead>
            <tbody>
              {MD.prensa.map((r) => {
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
      </div>

      {/* C · franja */}
      <div>
        <p className="mb-1 text-xs font-bold text-uni-900">
          C · Densidad lineal de hechos a lo largo de la Ruta 4003 (núcleo gaussiano, banda {es(MD.densidad.bw_km, 1)} km [H])
        </p>
        <FranjaDensidad />
      </div>

      {/* D · barras */}
      <div>
        <p className="mb-1 text-xs font-bold text-uni-900">D · Hechos por kilómetro (pasa el cursor por una barra)</p>
        <div className="h-[260px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barras} margin={{ top: 22, right: 8, left: 0, bottom: 8 }} barCategoryGap={1}>
              <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" vertical={false} />
              <ReferenceArea x1={Math.floor(L.calarca)} x2={Math.floor(L.cajamarca)} fill="#EEF2F7"
                             label={{ value: 'Paso Calarcá – Cajamarca · 45 km', position: 'insideTop', fontSize: 11, fill: TINTA }} />
              <XAxis dataKey="etiqueta" interval={9} tick={{ fill: '#64748b', fontSize: 11 }} stroke="#94a3b8"
                     tickFormatter={(k) => `km ${k}`} />
              <YAxis allowDecimals={false} tick={{ fill: '#64748b', fontSize: 11 }} stroke="#94a3b8" width={32} />
              <Tooltip content={<TipKm />} cursor={{ fill: 'rgba(148,163,184,0.15)' }} />
              <Bar dataKey="hechos_fatales" stackId="h" fill={AZUL} name="Hechos con fallecido" />
              <Bar dataKey="no_fatales" stackId="h" fill={AZUL_CLARO} name="Hechos solo con lesionados" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <p className="text-[11px] leading-relaxed text-slate-500">
          Entre el km 11 y el 41 —el ascenso y el Alto de La Línea— el anexo registra {R.paso_km_11_a_41.hechos} hechos
          y {R.paso_km_11_a_41.fallecidos} fallecido. La figura muestra dónde se pudo georreferenciar, no dónde está el riesgo.
        </p>
      </div>

      <p className="text-[11px] leading-relaxed text-slate-500">
        Fuente: ANSV – Observatorio Nacional de Seguridad Vial, oficio 20265000140371 del 22 sep 2026 (solicitud de
        D. Torrente), fuente primaria INMLCF [F]. Hechos, abscisa y tramos: procesar_microdato_ANSV_OE5.py [CP] [H].
        Prensa: El Tiempo, El Espectador, Infobae.
      </p>
    </div>
  );
}
