'use client';

/**
 * EscenaComparativa — raíz de las dos escenas 3D del encabezado.
 *
 * ESQUEMA ILUSTRATIVO: el relieve es procedural, no sale del DEM. Ver la
 * advertencia de método en `Mountain.tsx`.
 *
 * Cambios frente al boceto `paz-y-region-gemini`:
 *  - Se retiró `<Environment preset="city" />`. Ese helper de drei descarga un
 *    mapa de entorno HDR desde un CDN externo en tiempo de ejecución; el sitio
 *    no depende de recursos de terceros para renderizar. Se reemplaza por una
 *    luz hemisférica, que da un resultado equivalente sin salir a la red.
 *  - `dpr` acotado y sombras opcionales, para las tarjetas pequeñas.
 *  - `frameloop="demand"` no se usa: las escenas son animadas por definición.
 */

import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import Mountain from './Mountain';
import ConventionalRoad from './ConventionalRoad';
import TunnelFerropista from './TunnelFerropista';

interface Props {
  scenario: 'convencional' | 'ferropista';
  /** Alto del lienzo. Usa valores pequeños dentro de la tarjeta del encabezado. */
  height?: number;
  /** 'compacta' y 'media' bajan arbolado, malla y flota; solo 'plena' proyecta sombras. */
  calidad?: 'compacta' | 'media' | 'plena';
  className?: string;
}

export default function EscenaComparativa({
  scenario,
  height = 400,
  calidad = 'plena',
  className = '',
}: Props) {
  const compacta = calidad === 'compacta';
  const media = calidad === 'media';
  const ligera = compacta || media;

  return (
    <div
      className={`w-full bg-sky-50 rounded-xl overflow-hidden border border-sky-100 cursor-grab active:cursor-grabbing ${className}`}
      style={{ height }}
    >
      <Canvas
        shadows={!ligera}
        dpr={ligera ? [1, 1.75] : [1, 2]}
        camera={{ position: ligera ? [17, 11, 16] : [15, 12, 15], fov: 40 }}
      >
        <ambientLight intensity={0.45} />
        <hemisphereLight args={['#DCEBF5', '#4A5D3A', 0.55]} />
        <directionalLight
          castShadow={!ligera}
          position={[10, 15, -5]}
          intensity={1.2}
          shadow-mapSize={[1024, 1024]}
          shadow-camera-left={-10}
          shadow-camera-right={10}
          shadow-camera-top={10}
          shadow-camera-bottom={-10}
        />
        <directionalLight position={[-10, 10, 10]} intensity={0.3} color="#D5E8F2" />

        <Mountain
          treeCount={compacta ? 180 : media ? 340 : 420}
          segments={compacta ? [64, 32, 64] : [96, 48, 96]}
        />

        <ConventionalRoad
          showTrucks={scenario === 'convencional'}
          vehicleCount={compacta ? (scenario === 'convencional' ? 22 : 14) : media ? (scenario === 'convencional' ? 32 : 20) : undefined}
        />

        {scenario === 'ferropista' && <TunnelFerropista />}

        <OrbitControls
          makeDefault
          enablePan={false}
          maxPolarAngle={Math.PI / 2 - 0.05}
          minDistance={ligera ? 10 : 5}
          maxDistance={40}
        />
      </Canvas>
    </div>
  );
}
