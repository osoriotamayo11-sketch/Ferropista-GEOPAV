'use client';

/**
 * Mountain — relieve de la escena comparativa.
 *
 * ADVERTENCIA DE MÉTODO: la superficie que dibuja este componente es
 * PROCEDURAL E INVENTADA (`getMountainHeight` combina senos y cosenos). No
 * proviene del modelo de elevación digital ni de ningún dato del proyecto.
 * Sirve como esquema ilustrativo del contraste entre cruzar la montaña por
 * encima y atravesarla por debajo. El terreno real, levantado del DEM
 * Copernicus GLO-30, está en `Terreno3D.tsx` (sección del OE 1).
 *
 * Cambios frente al boceto `paz-y-region-gemini`:
 *  - Los árboles pasan de meshes individuales a InstancedMesh: el boceto
 *    generaba 1.000 árboles × 3 meshes = 3.000 draw calls por escena.
 *  - Densidad y resolución de malla parametrizadas, para bajarlas en las
 *    tarjetas pequeñas del encabezado.
 */

import { useMemo, useLayoutEffect, useRef } from 'react';
import * as THREE from 'three';

const roadNodes: [number, number][] = [
  [-20, 6], [-16, 5], [-13, 6],
  [-11, 5], [-9.5, 4], [-8, 3], [-6, 3.5], [-4, 4], [-2, 2.5],
  [0, 1], [2, 1.5], [4, 2], [6, 3], [8, 4], [9.5, 4.5], [11, 5],
  [13, 6], [16, 5], [20, 6],
];

function getRoadInfo(x: number, z: number) {
  let minDist = 1000;
  let nearestX = x;
  let nearestZ = z;
  for (let i = 0; i < roadNodes.length - 1; i++) {
    const [x1, z1] = roadNodes[i];
    const [x2, z2] = roadNodes[i + 1];
    const A = x - x1, B = z - z1, C = x2 - x1, D = z2 - z1;
    const dot = A * C + B * D;
    const lenSq = C * C + D * D;
    let param = -1;
    if (lenSq !== 0) param = dot / lenSq;
    let xx, zz;
    if (param < 0) { xx = x1; zz = z1; }
    else if (param > 1) { xx = x2; zz = z2; }
    else { xx = x1 + param * C; zz = z1 + param * D; }
    const dist = Math.hypot(x - xx, z - zz);
    if (dist < minDist) {
      minDist = dist;
      nearestX = xx;
      nearestZ = zz;
    }
  }
  return { dist: minDist, nx: nearestX, nz: nearestZ };
}

/* ═══════ Altura del relieve (compartida con la carretera y los vehículos) ═══════ */
export function getMountainHeight(x: number, z: number): number {
  const roadInfo = getRoadInfo(x, z);
  const dist = roadInfo.dist;

  let blend = 1.0;
  if (dist < 0.7) {
    blend = 0.0;
  } else if (dist < 2.5) {
    blend = (dist - 0.7) / 1.8;
    blend = blend * blend * (3 - 2 * blend);
  }

  const effX = x * blend + roadInfo.nx * (1 - blend);
  const effZ = z * blend + roadInfo.nz * (1 - blend);

  const distToCenter = Math.sqrt(effX * effX + effZ * effZ);
  const baseHeight = Math.max(0, 6.5 - distToCenter * 0.65);

  let noise = Math.sin(effX * 1.5) * Math.cos(effZ * 1.5) * 0.3;
  noise += Math.sin(effX * 0.5) * 0.6;

  let y = baseHeight + noise * blend;

  let trenchBlend = 0.0;
  if (Math.abs(x) > 9.0) {
    const dz = Math.abs(z - (-2));
    let latBlend = 0.0;
    if (dz < 1.6) {
      latBlend = 1.0;
    } else if (dz < 3.0) {
      const t = (dz - 1.6) / 1.4;
      latBlend = 1.0 - (t * t * (3 - 2 * t));
    }
    trenchBlend = latBlend;
  }

  if (trenchBlend > 0) {
    y = y * (1 - trenchBlend) + 0.10 * trenchBlend;
  }

  if (y < -1.4) y = -1.4;

  return y;
}

/* ═══════ Arbolado instanciado ═══════ */
type TreeData = { pos: [number, number, number]; scale: number };

function Trees({ data }: { data: TreeData[] }) {
  const trunk = useRef<THREE.InstancedMesh>(null);
  const coneLow = useRef<THREE.InstancedMesh>(null);
  const coneTop = useRef<THREE.InstancedMesh>(null);

  useLayoutEffect(() => {
    const dummy = new THREE.Object3D();
    const apply = (ref: THREE.InstancedMesh | null, yLocal: number) => {
      if (!ref) return;
      data.forEach((t, i) => {
        dummy.position.set(t.pos[0], t.pos[1] + yLocal * t.scale, t.pos[2]);
        dummy.scale.setScalar(t.scale);
        dummy.updateMatrix();
        ref.setMatrixAt(i, dummy.matrix);
      });
      ref.instanceMatrix.needsUpdate = true;
      ref.computeBoundingSphere();
    };
    apply(trunk.current, 0.2);
    apply(coneLow.current, 0.6);
    apply(coneTop.current, 0.9);
  }, [data]);

  if (data.length === 0) return null;

  return (
    <group>
      <instancedMesh ref={trunk} args={[undefined, undefined, data.length]} castShadow>
        <cylinderGeometry args={[0.05, 0.08, 0.4, 5]} />
        <meshStandardMaterial color="#5D4037" roughness={0.9} />
      </instancedMesh>
      <instancedMesh ref={coneLow} args={[undefined, undefined, data.length]} castShadow>
        <coneGeometry args={[0.4, 0.6, 5]} />
        <meshStandardMaterial color="#2E7D32" roughness={0.8} flatShading />
      </instancedMesh>
      <instancedMesh ref={coneTop} args={[undefined, undefined, data.length]} castShadow>
        <coneGeometry args={[0.3, 0.5, 5]} />
        <meshStandardMaterial color="#388E3C" roughness={0.8} flatShading />
      </instancedMesh>
    </group>
  );
}

interface MountainProps {
  /** Número de árboles a sembrar. El boceto usaba 1.000. */
  treeCount?: number;
  /** Subdivisiones de la malla del terreno. El boceto usaba 128 × 64 × 128. */
  segments?: [number, number, number];
}

export default function Mountain({
  treeCount = 420,
  segments = [96, 48, 96],
}: MountainProps) {
  const geometry = useMemo(() => {
    const geo = new THREE.BoxGeometry(40, 4, 16, segments[0], segments[1], segments[2]);
    geo.translate(0, -2, 0);

    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const y = pos.getY(i);
      const z = pos.getZ(i);

      const t = y / -4.0;
      const topY = getMountainHeight(x, z);
      const bottomY = -1.5;
      const newY = topY + t * (bottomY - topY);

      pos.setY(i, newY);
    }
    geo.computeVertexNormals();

    const colors = new Float32Array(pos.count * 3);
    const colorRock = new THREE.Color('#4A5D23');
    const colorGrass = new THREE.Color('#7CB342');

    for (let i = 0; i < pos.count; i++) {
      const y = pos.getY(i);
      const normalY = geo.attributes.normal.getY(i);
      const steepness = 1.0 - normalY;

      let mixRatio = steepness > 0.4 ? 1.0 : steepness / 0.4;
      if (y < 0.2) mixRatio = 0.0;

      const c = colorGrass.clone().lerp(colorRock, mixRatio);
      colors[i * 3] = c.r;
      colors[i * 3 + 1] = c.g;
      colors[i * 3 + 2] = c.b;
    }
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    return geo;
  }, [segments]);

  const trees = useMemo(() => {
    let seed = 42;
    const random = () => {
      const x = Math.sin(seed++) * 10000;
      return x - Math.floor(x);
    };

    const positions: TreeData[] = [];
    for (let i = 0; i < treeCount; i++) {
      const x = -20 + random() * 40;
      const z = -8 + random() * 16;
      const y = getMountainHeight(x, z);

      let minDist = 100;
      for (const [rx, rz] of roadNodes) {
        const d = Math.hypot(x - rx, z - rz);
        if (d < minDist) minDist = d;
      }

      const inStation = (x > -1 && x < 11 && z > -2.0 && z < 2.0);
      const inPortalLeft = (x > -11 && x < -7 && z > -4.5 && z < 0.5);
      const inPortalRight = (x > 7 && x < 11 && z > -4.5 && z < 0.5);
      const inTracks = (z > -2.8 && z < -1.2);

      if (minDist > 1.2 && !inStation && !inPortalLeft && !inPortalRight && !inTracks && y > -1.0) {
        positions.push({ pos: [x, y, z], scale: 0.5 + random() * 0.5 });
      }
    }
    return positions;
  }, [treeCount]);

  return (
    <group>
      <mesh geometry={geometry} receiveShadow castShadow>
        {[...Array(6)].map((_, i) => (
          <meshStandardMaterial
            key={i}
            attach={`material-${i}`}
            color={i === 2 ? '#6EAC70' : '#3E2723'}
            roughness={0.9}
            flatShading
          />
        ))}
      </mesh>

      <Trees data={trees} />
    </group>
  );
}
