'use client';

/**
 * Humo — penacho de escape para vehículos de las escenas 3D.
 *
 * Extraído de `AutopistaRodante.tsx` (antes `SmokeParticle`/`AnimatedSmoke`) para
 * reutilizarlo en `ConventionalRoad.tsx`. La geometría es un singleton de módulo
 * y los materiales se cachean por configuración (partículas × opacidad máxima):
 * no se crea un recurso nuevo por partícula ni por vehículo. Todas las
 * instancias comparten la misma fórmula ligada al reloj global, así que
 * mutar un material compartido desde varias instancias en el mismo cuadro es
 * seguro (el resultado es idéntico sin importar cuál escriba último).
 */

import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const CICLO = 1.5;

const GEOMETRIA = new THREE.SphereGeometry(0.03, 4, 4);

const cacheMateriales = new Map<string, THREE.MeshStandardMaterial[]>();

function materialesPara(particulas: number, opacidadMax: number) {
  const clave = `${particulas}:${opacidadMax}`;
  let materiales = cacheMateriales.get(clave);
  if (!materiales) {
    materiales = Array.from({ length: particulas }, () => new THREE.MeshStandardMaterial({
      color: '#B0BEC5',
      transparent: true,
      opacity: opacidadMax,
      depthWrite: false,
      flatShading: true,
    }));
    cacheMateriales.set(clave, materiales);
  }
  return materiales;
}

interface HumoProps {
  position: [number, number, number];
  /** Partículas del penacho. La autopista rodante usa 3 (escape de tractomula). */
  particulas?: number;
  /** Opacidad máxima de cada partícula antes de desvanecerse. */
  opacidadMax?: number;
}

export default function Humo({ position, particulas = 3, opacidadMax = 0.8 }: HumoProps) {
  const meshes = useRef<(THREE.Mesh | null)[]>([]);
  const materiales = materialesPara(particulas, opacidadMax);

  useFrame(({ clock }) => {
    const time = clock.getElapsedTime();
    for (let i = 0; i < particulas; i++) {
      const mesh = meshes.current[i];
      if (!mesh) continue;
      const t = (time + i * 0.5) % CICLO;
      const progress = t / CICLO;

      // Sube y se va ligeramente hacia atrás.
      mesh.position.y = progress * 0.4;
      mesh.position.x = -progress * 0.3;

      // Crece y se desvanece.
      const scale = 1 + progress * 2.5;
      mesh.scale.set(scale, scale, scale);
      materiales[i].opacity = (1 - progress) * opacidadMax;
    }
  });

  return (
    <group position={position}>
      {materiales.map((material, i) => (
        <mesh
          key={i}
          ref={(el) => { meshes.current[i] = el; }}
          geometry={GEOMETRIA}
          material={material}
        />
      ))}
    </group>
  );
}
