'use client';

/**
 * Terreno3D — relieve real del área de estudio levantado del DEM.
 *
 * A diferencia de las escenas comparativas del encabezado, aquí TODO sale de
 * datos: el relieve del Copernicus DEM GLO-30 recortado al área de estudio, el
 * trazado calculado en el OE 1 y los límites municipales del IGAC.
 *
 * Insumos (en `public/`):
 *   · /oe1/dem_estudio_90m.tif        DEM recortado a Ibagué + Cajamarca +
 *                                     Calarcá con margen, remuestreado a ~93 m,
 *                                     Int16 con DEFLATE. 0,70 MB.
 *   · /data/trazado_tunel.geojson     Eje recto entre portales, 106 vértices,
 *                                     52.211,8 m, pendiente 0,9587 % [CP].
 *   · /data/limites_area_estudio.geojson  Límites municipales [F, IGAC].
 *
 * Correcciones frente al boceto `paz-y-region-gemini`:
 *  1. PROPORCIÓN. El boceto usaba una malla cuadrada de 20 × 20 para un área de
 *     93 × 51 km, deformando la geografía un 82 %. Aquí el plano toma la
 *     relación de aspecto real del bbox.
 *  2. ESCALA VERTICAL. El boceto normalizaba la altura al rango del ráster, de
 *     modo que cambiar de DEM cambiaba en silencio la escala del relieve. Aquí
 *     la altura se calcula en unidades de mundo reales y la exageración es un
 *     factor explícito y declarado en la leyenda.
 *  3. LEYENDA. Los cortes de elevación estaban escritos a mano (450 … 5.250).
 *     Ahora se derivan del ráster que se está mostrando.
 *  4. RELLENO. El DEM del boceto tenía 55,9 % de píxeles `-9999` por recorte de
 *     máscara; al normalizar con recorte, todos caían a la cota mínima y se
 *     renderizaban como una meseta plana. El DEM nuevo es un recorte
 *     rectangular sin huecos.
 *  5. PORTALES. La leyenda del boceto los anunciaba pero la escena no los
 *     dibujaba. Se toman de los extremos del propio trazado, sin duplicar la
 *     fuente de verdad.
 *
 * LÍMITE DECLARADO — ESTE RELIEVE NO ES MÉTRICO. El DEM que carga esta vista
 * está remuestreado de 30 m a ~93 m por bilineal, y ese promediado sube las
 * cotas en ladera empinada. Comprobado sobre el archivo servido: en el portal
 * oriental el ráster aligerado da 962 msnm donde el DEM a 30 m del OE 1 da 951,
 * y la cota máxima del terreno sobre el eje da 3.287 msnm contra los 3.393 de
 * `cifras_OE1.json`. Sirve para ver la montaña que el túnel atraviesa; no para
 * leer alturas. Toda cifra publicada sale del cálculo del OE 1, nunca de este
 * modelo.
 */

import { useEffect, useMemo, useState } from 'react';
import * as THREE from 'three';
import { fromArrayBuffer } from 'geotiff';
import { Canvas } from '@react-three/fiber';
import { Line, OrbitControls } from '@react-three/drei';

/** Ancho del terreno en unidades de mundo. El alto se deriva del bbox. */
const WORLD_WIDTH = 20;
/** Exageración vertical del relieve. Se declara en la leyenda. */
const EXAGERACION_V = 3;

const RUTA_DEM = '/oe1/dem_estudio_90m.tif';
const RUTA_TRAZADO = '/data/trazado_tunel.geojson';
const RUTA_LIMITES = '/data/limites_area_estudio.geojson';

interface DemData {
  width: number;
  height: number;
  elevations: Float32Array;
  bbox: [number, number, number, number];
  minElev: number;
  maxElev: number;
  worldDepth: number;
  metrosPorUnidad: number;
}

type GeoJson = {
  features: { geometry: { type: string; coordinates: unknown } }[];
};

/* ═══════ Paleta hipsométrica ═══════ */
const RAMPA = ['#2d5a27', '#8fa855', '#d4be8c', '#8b5e4a', '#423e3b'];

function colorPorAltura(t: number, out: THREE.Color) {
  const c = THREE.MathUtils.clamp(t, 0, 1) * (RAMPA.length - 1);
  const i = Math.min(Math.floor(c), RAMPA.length - 2);
  out.set(RAMPA[i]).lerp(new THREE.Color(RAMPA[i + 1]), c - i);
  return out;
}

/* ═══════ Superficie del terreno ═══════ */
function Terreno({ dem }: { dem: DemData }) {
  const geometry = useMemo(() => {
    const segX = 320;
    const segY = Math.max(32, Math.round(segX * (dem.worldDepth / WORLD_WIDTH)));
    const geo = new THREE.PlaneGeometry(WORLD_WIDTH, dem.worldDepth, segX, segY);

    const pos = geo.attributes.position;
    const uv = geo.attributes.uv;
    const colors = new Float32Array(pos.count * 3);
    const tmp = new THREE.Color();
    const rango = Math.max(1, dem.maxElev - dem.minElev);

    for (let i = 0; i < pos.count; i++) {
      const u = uv.getX(i);
      const v = uv.getY(i);

      const px = Math.min(Math.floor(u * dem.width), dem.width - 1);
      const py = Math.min(Math.floor((1 - v) * dem.height), dem.height - 1);
      const elev = dem.elevations[py * dem.width + px];

      // Altura en unidades de mundo reales, con exageración explícita.
      pos.setZ(i, ((elev - dem.minElev) / dem.metrosPorUnidad) * EXAGERACION_V);

      const c = colorPorAltura((elev - dem.minElev) / rango, tmp);
      colors[i * 3] = c.r;
      colors[i * 3 + 1] = c.g;
      colors[i * 3 + 2] = c.b;
    }

    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geo.computeVertexNormals();
    return geo;
  }, [dem]);

  return (
    <mesh geometry={geometry} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
      <meshStandardMaterial vertexColors roughness={0.95} />
    </mesh>
  );
}

/* ═══════ Proyección de coordenadas geográficas al mundo 3D ═══════ */
function usarProyector(dem: DemData) {
  return (lon: number, lat: number, alzada = 0.04) => {
    const [minLon, minLat, maxLon, maxLat] = dem.bbox;
    const u = (lon - minLon) / (maxLon - minLon);
    const v = (lat - minLat) / (maxLat - minLat);

    const x = u * WORLD_WIDTH - WORLD_WIDTH / 2;
    const z = -(v * dem.worldDepth - dem.worldDepth / 2);

    const px = Math.min(Math.max(Math.floor(u * dem.width), 0), dem.width - 1);
    const py = Math.min(Math.max(Math.floor((1 - v) * dem.height), 0), dem.height - 1);
    const elev = dem.elevations[py * dem.width + px];

    const y = ((elev - dem.minElev) / dem.metrosPorUnidad) * EXAGERACION_V + alzada;
    return new THREE.Vector3(x, y, z);
  };
}

/** Recorre cualquier geometría GeoJSON y devuelve sus anillos como listas de coordenadas. */
function anillos(gj: GeoJson | null): number[][][] {
  if (!gj?.features) return [];
  const out: number[][][] = [];
  for (const f of gj.features) {
    const { type, coordinates } = f.geometry as { type: string; coordinates: never };
    if (type === 'LineString') out.push(coordinates as unknown as number[][]);
    else if (type === 'MultiLineString' || type === 'Polygon') {
      for (const r of coordinates as unknown as number[][][]) out.push(r);
    } else if (type === 'MultiPolygon') {
      for (const p of coordinates as unknown as number[][][][]) for (const r of p) out.push(r);
    }
  }
  return out;
}

/* ═══════ Límites municipales: un solo buffer para todos los anillos ═══════ */
function Limites({ dem, data }: { dem: DemData; data: GeoJson | null }) {
  const geometry = useMemo(() => {
    const proyectar = usarProyector(dem);
    const verts: number[] = [];
    for (const anillo of anillos(data)) {
      for (let i = 0; i < anillo.length - 1; i++) {
        const a = proyectar(anillo[i][0], anillo[i][1], 0.06);
        const b = proyectar(anillo[i + 1][0], anillo[i + 1][1], 0.06);
        verts.push(a.x, a.y, a.z, b.x, b.y, b.z);
      }
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
    return geo;
  }, [dem, data]);

  if (!data) return null;
  return (
    <lineSegments geometry={geometry}>
      <lineBasicMaterial color="#1f2937" transparent opacity={0.75} />
    </lineSegments>
  );
}

/* ═══════ Trazado del túnel y portales ═══════ */
function Trazado({ dem, data }: { dem: DemData; data: GeoJson | null }) {
  const { puntos, portales } = useMemo(() => {
    const proyectar = usarProyector(dem);
    const rs = anillos(data);
    const linea = rs[0] ?? [];
    return {
      puntos: linea.map((c) => proyectar(c[0], c[1], 0.1)),
      portales: linea.length
        ? [proyectar(linea[0][0], linea[0][1], 0.12), proyectar(linea[linea.length - 1][0], linea[linea.length - 1][1], 0.12)]
        : [],
    };
  }, [dem, data]);

  if (puntos.length < 2) return null;

  return (
    <group>
      <Line points={puntos} color="#0033cc" lineWidth={3} />
      {portales.map((p, i) => (
        <mesh key={i} position={p}>
          <sphereGeometry args={[0.12, 16, 16]} />
          <meshStandardMaterial color="#6e2b34" emissive="#6e2b34" emissiveIntensity={0.35} />
        </mesh>
      ))}
    </group>
  );
}

/* ═══════ Componente público ═══════ */
export default function Terreno3D({ height = 560 }: { height?: number }) {
  const [dem, setDem] = useState<DemData | null>(null);
  const [trazado, setTrazado] = useState<GeoJson | null>(null);
  const [limites, setLimites] = useState<GeoJson | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [leyendaAbierta, setLeyendaAbierta] = useState(true);

  useEffect(() => {
    let vivo = true;

    (async () => {
      try {
        const res = await fetch(RUTA_DEM);
        if (!res.ok) throw new Error(`DEM ${res.status}`);
        const tiff = await fromArrayBuffer(await res.arrayBuffer());
        const image = await tiff.getImage();

        const bbox = image.getBoundingBox() as [number, number, number, number];
        const width = image.getWidth();
        const height_ = image.getHeight();
        const raw = (await image.readRasters())[0] as ArrayLike<number>;

        const elevations = new Float32Array(raw.length);
        let minElev = Infinity;
        let maxElev = -Infinity;
        for (let i = 0; i < raw.length; i++) {
          const v = raw[i];
          elevations[i] = v;
          if (v > -1000 && v < 9000) {
            if (v < minElev) minElev = v;
            if (v > maxElev) maxElev = v;
          }
        }

        // Dimensiones reales del recorte, para no deformar la geografía.
        const [minLon, minLat, maxLon, maxLat] = bbox;
        const latMedia = (minLat + maxLat) / 2;
        const anchoM = (maxLon - minLon) * 111_320 * Math.cos((latMedia * Math.PI) / 180);
        const altoM = (maxLat - minLat) * 110_570;

        if (!vivo) return;
        setDem({
          width,
          height: height_,
          elevations,
          bbox,
          minElev,
          maxElev,
          worldDepth: WORLD_WIDTH * (altoM / anchoM),
          metrosPorUnidad: anchoM / WORLD_WIDTH,
        });
      } catch (e) {
        if (vivo) setError(e instanceof Error ? e.message : 'No se pudo cargar el DEM');
      }
    })();

    (async () => {
      try {
        const [tr, li] = await Promise.all([fetch(RUTA_TRAZADO), fetch(RUTA_LIMITES)]);
        if (!vivo) return;
        if (tr.ok) setTrazado(await tr.json());
        if (li.ok) setLimites(await li.json());
      } catch {
        /* las capas vectoriales son accesorias: el relieve se muestra igual */
      }
    })();

    return () => { vivo = false; };
  }, []);

  const cortes = useMemo(() => {
    if (!dem) return [];
    return Array.from({ length: 5 }, (_, i) =>
      Math.round(dem.minElev + ((dem.maxElev - dem.minElev) * i) / 4),
    );
  }, [dem]);

  return (
    <div className="relative w-full bg-slate-50" style={{ height }}>
      {/* Convenciones. Panel plegable y mas angosto que el anterior: ocupaba una
          esquina entera del visor y tapaba el relieve, que es lo que hay que ver.
          Plegado deja solo el boton; la nota metodologica se muestra aparte. */}
      <div className="absolute left-3 top-3 z-10 max-w-[min(15rem,60%)]">
        <button
          type="button"
          onClick={() => setLeyendaAbierta((v) => !v)}
          aria-expanded={leyendaAbierta}
          className="flex w-full items-center justify-between gap-3 rounded-md border border-slate-200 bg-white/80 px-2.5 py-1.5 text-[11px] font-bold text-slate-700 shadow-sm backdrop-blur-sm transition-colors hover:bg-white"
        >
          <span>Convenciones</span>
          <span className="font-mono text-[10px] font-normal text-slate-400">
            {leyendaAbierta ? 'ocultar −' : 'mostrar +'}
          </span>
        </button>

        {leyendaAbierta && (
          <div className="mt-1.5 rounded-md border border-slate-200 bg-white/80 p-2.5 text-[11px] text-slate-700 shadow-sm backdrop-blur-sm">
            <div className="mb-1.5 flex items-center gap-2">
              <span className="h-2 w-2 shrink-0 rounded-full" style={{ backgroundColor: '#6e2b34' }} />
              <span>Portales del túnel</span>
            </div>
            <div className="mb-1.5 flex items-center gap-2">
              <span className="h-[3px] w-5 shrink-0" style={{ backgroundColor: '#0033cc' }} />
              <span>Trazado (preliminar) [CP]</span>
            </div>
            <div className="mb-2.5 flex items-center gap-2">
              <span className="h-2.5 w-4 shrink-0 border border-slate-800" />
              <span>Municipios [F, IGAC]</span>
            </div>

            <h4 className="mb-1 text-[10px] font-bold uppercase tracking-wide text-slate-500">
              Elevación (msnm)
            </h4>
            <div className="flex h-2.5 w-full overflow-hidden rounded-sm">
              {RAMPA.map((c) => (
                <div key={c} className="flex-1" style={{ backgroundColor: c }} />
              ))}
            </div>
            <div className="mt-0.5 flex w-full justify-between font-mono text-[9px] text-slate-500">
              <span>{cortes[0]?.toLocaleString('es-CO')}</span>
              <span>{cortes[Math.floor(cortes.length / 2)]?.toLocaleString('es-CO')}</span>
              <span>{cortes[cortes.length - 1]?.toLocaleString('es-CO')}</span>
            </div>
          </div>
        )}
      </div>

      {/* Nota metodologica: al pie, fuera del paso de la vista */}
      <p className="pointer-events-none absolute inset-x-3 bottom-2 z-10 text-center font-mono text-[9px] leading-snug text-slate-500">
        Copernicus DEM GLO-30 remuestreado a ~93 m, exageración vertical ×{EXAGERACION_V}. Relieve
        ilustrativo: las cotas publicadas se calculan sobre el DEM a 30 m en el objetivo específico 1.
      </p>

      {!dem && !error && (
        <div className="absolute inset-0 z-10 flex items-center justify-center font-mono text-sm text-slate-500">
          Procesando el modelo digital de elevación…
        </div>
      )}
      {error && (
        <div className="absolute inset-0 z-10 flex items-center justify-center px-6 text-center font-mono text-sm text-red-700">
          No se pudo cargar el modelo de elevación ({error}).
        </div>
      )}

      <Canvas dpr={[1, 1.75]} camera={{ position: [0, 10, 13.5], fov: 48 }}>
        <ambientLight intensity={0.75} />
        <hemisphereLight args={['#EAF2F8', '#3B4A3A', 0.5]} />
        <directionalLight position={[6, 18, 6]} intensity={1.3} />

        {dem && (
          <group>
            <Terreno dem={dem} />
            <Limites dem={dem} data={limites} />
            <Trazado dem={dem} data={trazado} />
          </group>
        )}

        <OrbitControls target={[0, 0.9, 0]} maxPolarAngle={Math.PI / 2 - 0.08} minDistance={6} maxDistance={40} />
      </Canvas>
    </div>
  );
}
