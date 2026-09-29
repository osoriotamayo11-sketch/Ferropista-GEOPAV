'use client';

/**
 * MapaPortalOE3 — mapa SVG interactivo por portal (OE 3).
 *
 * Carga /data/oe3_mapas.json con fetch (no con import): el archivo pesa
 * ~200 KB y no debe sumarse al First Load JS de la página. Las dos instancias
 * (portal oriental y occidental) comparten una única descarga vía caché de
 * módulo.
 *
 * Proyección: equirectangular local, corrigiendo el ancho por cos(latitud
 * media) para que el círculo de 3 km se dibuje como círculo y no como elipse.
 * El fondo (relieve JPG) cubre exactamente `limites`, así que se estira al
 * mismo viewBox sin recortes.
 */

import React, { useEffect, useMemo, useState } from 'react';

const RUTA_OE3_MAPAS = '/data/oe3_mapas.json';

type Geometry = { type: string; coordinates: unknown };
type ZonaGeo = { clase: string; geometry: Geometry };
type PuntoInventario = { lon: number; lat: number; subtipo: string };
type TramoVia = { tunel: boolean; coords: [number, number][] };
type PortalMapa = {
  relieve: string;
  limites: [number, number, number, number];
  portal: [number, number];
  susceptibilidad: ZonaGeo[];
  amenaza: ZonaGeo[];
  inventario: PuntoInventario[];
  via: TramoVia[];
};
type OE3Mapas = { radio_m: number; portales: Record<string, PortalMapa> };

const ORDEN_CLASES = ['Baja', 'Media', 'Alta', 'Muy Alta'] as const;
const COLOR_CLASE: Record<string, string> = {
  Baja: '#FDE2BF',
  Media: '#F6C68F',
  Alta: '#D9591E',
  'Muy Alta': '#7F1D0B',
};

const PIE_MAPA =
  'SGC, SIMMA 1:100.000 [F]; círculo de 3 km, recorte y simplificación [CP]. El mapa no muestra ' +
  'píxeles sueltos menores a ~0,18 ha; los porcentajes de la barra se calcularon sobre la capa completa.';

/* Descarga única compartida por todas las instancias del mapa. */
let cacheOE3Mapas: Promise<OE3Mapas> | null = null;
function cargarOE3Mapas(): Promise<OE3Mapas> {
  if (!cacheOE3Mapas) {
    cacheOE3Mapas = fetch(RUTA_OE3_MAPAS).then((r) => {
      if (!r.ok) throw new Error(`oe3_mapas.json ${r.status}`);
      return r.json() as Promise<OE3Mapas>;
    });
  }
  return cacheOE3Mapas;
}

function crearProyector(limites: [number, number, number, number]) {
  const [oeste, sur, este, norte] = limites;
  const latMedia = (sur + norte) / 2;
  const mPorGradoLon = 111_320 * Math.cos((latMedia * Math.PI) / 180);
  const mPorGradoLat = 110_540;
  const anchoM = (este - oeste) * mPorGradoLon;
  const altoM = (norte - sur) * mPorGradoLat;
  const VIEW_W = 1000;
  const escala = VIEW_W / anchoM;
  const VIEW_H = altoM * escala;
  return {
    x: (lon: number) => (lon - oeste) * mPorGradoLon * escala,
    y: (lat: number) => (norte - lat) * mPorGradoLat * escala,
    escala,
    VIEW_W,
    VIEW_H,
  };
}
type Proyector = ReturnType<typeof crearProyector>;

function anillosDePoligono(geom: Geometry): number[][][] {
  const { type, coordinates } = geom;
  if (type === 'Polygon') return coordinates as unknown as number[][][];
  if (type === 'MultiPolygon') return (coordinates as unknown as number[][][][]).flat();
  return [];
}

function pathDeGeometria(geom: Geometry, p: Proyector): string {
  return anillosDePoligono(geom)
    .map((anillo) => `M${anillo.map(([lon, lat]) => `${p.x(lon).toFixed(1)},${p.y(lat).toFixed(1)}`).join('L')}Z`)
    .join(' ');
}

/* ═══════ Barra apilada de amenaza en el círculo de 3 km ═══════ */
function BarraAmenaza3km({ pct }: { pct: Record<string, number | undefined> }) {
  const clasesPresentes = ORDEN_CLASES.filter((c) => pct[c] != null);
  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-1.5">
        <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-500">
          Amenaza en el círculo de 3 km
        </p>
        <span
          title="Cálculo propio del semillero"
          className="shrink-0 rounded border border-blue-500/30 bg-blue-500/10 px-1 py-0.5 text-[9px] font-bold text-blue-700"
        >
          CP
        </span>
      </div>
      <div className="flex h-4 w-full overflow-hidden rounded-md border border-slate-200">
        {clasesPresentes.map((c) => (
          <div key={c} title={`${c}: ${pct[c] ?? 0} %`} style={{ width: `${pct[c] ?? 0}%`, backgroundColor: COLOR_CLASE[c] }} />
        ))}
      </div>
      <div className="flex flex-wrap gap-x-3 gap-y-0.5 text-[10px] text-slate-500">
        {clasesPresentes.map((c) => (
          <span key={c} className="inline-flex items-center gap-1">
            <span className="h-2 w-2 rounded-sm" style={{ backgroundColor: COLOR_CLASE[c] }} />
            {c} {(pct[c] ?? 0).toLocaleString('es-CO', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} %
          </span>
        ))}
      </div>
    </div>
  );
}

/* ═══════ Mapa + barra de un portal ═══════ */
interface MapaPortalOE3Props {
  portalId: string;
  amenaza3kmPct: Record<string, number | undefined>;
}

export const MapaPortalOE3: React.FC<MapaPortalOE3Props> = ({ portalId, amenaza3kmPct }) => {
  const [datos, setDatos] = useState<OE3Mapas | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [capa, setCapa] = useState<'susceptibilidad' | 'amenaza'>('susceptibilidad');

  useEffect(() => {
    let vivo = true;
    cargarOE3Mapas()
      .then((d) => { if (vivo) setDatos(d); })
      .catch((e) => { if (vivo) setError(e instanceof Error ? e.message : 'error'); });
    return () => { vivo = false; };
  }, []);

  const portal = datos?.portales[portalId];
  const proyector = useMemo(() => (portal ? crearProyector(portal.limites) : null), [portal]);

  if (error) {
    return (
      <p className="rounded-xl border border-red-200 bg-red-50 p-4 text-xs text-red-700">
        No se pudo cargar el mapa del portal ({error}).
      </p>
    );
  }
  if (!portal || !proyector || !datos) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl border border-slate-200 bg-slate-50 text-xs text-slate-400">
        Cargando mapa…
      </div>
    );
  }

  const zonas = capa === 'susceptibilidad' ? portal.susceptibilidad : portal.amenaza;
  const radioPx = datos.radio_m * proyector.escala;
  const centro = { x: proyector.x(portal.portal[0]), y: proyector.y(portal.portal[1]) };

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        {(['susceptibilidad', 'amenaza'] as const).map((c) => (
          <button
            key={c}
            type="button"
            onClick={() => setCapa(c)}
            className={`rounded-lg px-3 py-1.5 text-[11px] font-semibold capitalize transition-colors ${
              capa === c ? 'bg-uni-700 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            {c}
          </button>
        ))}
      </div>

      <svg
        viewBox={`0 0 ${proyector.VIEW_W} ${proyector.VIEW_H}`}
        className="w-full rounded-lg border border-slate-200 bg-white"
      >
        <image href={portal.relieve} x={0} y={0} width={proyector.VIEW_W} height={proyector.VIEW_H} preserveAspectRatio="none" />

        {zonas.map((z, i) => (
          <path key={i} d={pathDeGeometria(z.geometry, proyector)} fill={COLOR_CLASE[z.clase] ?? '#9ca3af'} fillOpacity={0.55} />
        ))}

        <circle cx={centro.x} cy={centro.y} r={radioPx} fill="none" stroke="#1f2937" strokeDasharray="4 3" strokeWidth={1.5} />

        {portal.via.map((tramo, i) => (
          <path
            key={i}
            d={tramo.coords.map(([lon, lat], j) => `${j === 0 ? 'M' : 'L'}${proyector.x(lon).toFixed(1)},${proyector.y(lat).toFixed(1)}`).join('')}
            fill="none"
            stroke="#7A2E12"
            strokeWidth={3}
            strokeDasharray={tramo.tunel ? '6 4' : undefined}
            strokeOpacity={tramo.tunel ? 0.55 : 1}
          />
        ))}

        {portal.inventario.map((pt, i) => {
          const x = proyector.x(pt.lon);
          const y = proyector.y(pt.lat);
          const s = 5;
          return (
            <polygon key={i} points={`${x},${y - s} ${x - s},${y + s} ${x + s},${y + s}`} fill="#111827" stroke="#ffffff" strokeWidth={0.6}>
              <title>{pt.subtipo}</title>
            </polygon>
          );
        })}

        <g stroke="#111827" strokeWidth={2}>
          <line x1={centro.x - 9} y1={centro.y} x2={centro.x + 9} y2={centro.y} />
          <line x1={centro.x} y1={centro.y - 9} x2={centro.x} y2={centro.y + 9} />
        </g>
      </svg>

      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[10px] text-slate-500">
        {ORDEN_CLASES.map((c) => (
          <span key={c} className="inline-flex items-center gap-1">
            <span className="h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: COLOR_CLASE[c], opacity: 0.7 }} />
            {c}
          </span>
        ))}
        <span className="inline-flex items-center gap-1">
          <span className="h-0 w-4 border-t border-dashed border-slate-700" /> círculo de 3 km
        </span>
        <span className="inline-flex items-center gap-1">
          <span className="h-0 w-4 border-t-2" style={{ borderColor: '#7A2E12' }} /> vía actual
        </span>
        <span className="inline-flex items-center gap-1">
          <svg width="9" height="9" viewBox="0 0 9 9"><polygon points="4.5,0.5 0.5,8.5 8.5,8.5" fill="#111827" /></svg>
          evento SIMMA
        </span>
      </div>

      <BarraAmenaza3km pct={amenaza3kmPct} />

      <p className="text-[10px] leading-relaxed text-slate-400">{PIE_MAPA}</p>
    </div>
  );
};

export default MapaPortalOE3;
