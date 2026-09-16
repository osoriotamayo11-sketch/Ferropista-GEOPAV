'use client';

/**
 * ConventionalRoad — la carretera sobre la montaña y su flota animada.
 *
 * ESQUEMA ILUSTRATIVO. El trazado de la vía, el número de vehículos y su
 * velocidad son de composición, no medidos. El único rasgo que sí busca
 * reflejar un dato de la fuente es el avance a tirones del escenario
 * convencional: la ponencia declara velocidad media < 20 km/h en el paso
 * actual [F, dia. 13].
 *
 * Cambios frente al boceto `paz-y-region-gemini`: la composición de la flota
 * pasa de `Math.random()` a un generador con semilla, para que la escena sea
 * idéntica en cada montaje.
 */

import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Car, Truck, CAR_COLORS, TRUCK_COLORS } from './Vehicles';
import { getMountainHeight } from './Mountain';

const rawPoints2D: [number, number][] = [
  [-20, 6], [-15, 6], [-11, 5],
  [-8, 3], [-4, 4], [0, 1], [4, 2], [8, 4], [11, 5],
  [15, 6], [20, 6],
];

const roadPoints = rawPoints2D.map(([x, z]) =>
  new THREE.Vector3(x, getMountainHeight(x, z) + 0.1, z),
);

const curve = new THREE.CatmullRomCurve3(roadPoints, false, 'centripetal');

function AnimatedVehicle({
  type, offset, speed, colorIdx,
}: { type: 'car' | 'truck'; offset: number; speed: number; colorIdx: number }) {
  const group = useRef<THREE.Group>(null);
  const position = useMemo(() => new THREE.Vector3(), []);
  const target = useMemo(() => new THREE.Vector3(), []);

  useFrame(({ clock }) => {
    if (!group.current) return;
    const time = clock.getElapsedTime();
    // Avance a tirones: acelera, casi se detiene, vuelve a arrancar.
    const flow = (time * speed) + Math.sin(time * 1.5) * (speed * 0.6);
    let t = (flow + offset) % 1.0;
    if (t < 0) t += 1.0;

    curve.getPointAt(t, position);
    curve.getPointAt((t + 0.01) % 1.0, target);

    position.y = getMountainHeight(position.x, position.z) + 0.34;
    target.y = getMountainHeight(target.x, target.z) + 0.34;

    group.current.position.copy(position);
    group.current.lookAt(target);
    group.current.rotateY(Math.PI / 2);
  });

  if (type === 'car') {
    return (
      <group ref={group}>
        <Car color={CAR_COLORS[colorIdx % CAR_COLORS.length]} />
      </group>
    );
  }

  const truckColors = TRUCK_COLORS[colorIdx % TRUCK_COLORS.length];
  return (
    <group ref={group}>
      <Truck bodyColor={truckColors.body} cabColor={truckColors.cab} />
    </group>
  );
}

interface Props {
  /** Con camiones = escenario convencional; sin ellos = los camiones van en el tren. */
  showTrucks?: boolean;
  /** Vehículos en la vía. El boceto usaba 40 / 25. */
  vehicleCount?: number;
}

export default function ConventionalRoad({ showTrucks = true, vehicleCount }: Props) {
  const roadGeometry = useMemo(() => {
    const segments = 256;
    const pts = curve.getPoints(segments);
    const vertices: number[] = [];
    const indices: number[] = [];
    const halfWidth = 0.6;

    for (let i = 0; i <= segments; i++) {
      const p = pts[i];
      p.y = getMountainHeight(p.x, p.z) + 0.22;

      const t = curve.getTangent(i / segments);
      const right = new THREE.Vector3(t.x, 0, t.z).normalize().cross(new THREE.Vector3(0, 1, 0)).normalize();

      const leftP = p.clone().add(right.clone().multiplyScalar(halfWidth));
      leftP.y = p.y;

      const rightP = p.clone().add(right.clone().multiplyScalar(-halfWidth));
      rightP.y = p.y;

      vertices.push(leftP.x, leftP.y, leftP.z);
      vertices.push(rightP.x, rightP.y, rightP.z);
    }

    for (let i = 0; i < segments; i++) {
      const a = i * 2;
      const b = i * 2 + 1;
      const c = (i + 1) * 2;
      const d = (i + 1) * 2 + 1;
      indices.push(a, d, b);
      indices.push(a, c, d);
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geo.setIndex(indices);
    geo.computeVertexNormals();
    return geo;
  }, []);

  const vehicles = useMemo(() => {
    const count = vehicleCount ?? (showTrucks ? 40 : 25);
    const baseSpeed = showTrucks ? 0.015 : 0.04;
    // Generador con semilla: misma escena en cada montaje.
    let seed = showTrucks ? 7 : 13;
    const random = () => {
      const x = Math.sin(seed++) * 10000;
      return x - Math.floor(x);
    };
    const arr = [];
    for (let i = 0; i < count; i++) {
      const type: 'car' | 'truck' = showTrucks && random() > 0.7 ? 'truck' : 'car';
      arr.push({ id: i, type, offset: i / count, speed: baseSpeed, colorIdx: i });
    }
    return arr;
  }, [showTrucks, vehicleCount]);

  return (
    <group>
      <mesh geometry={roadGeometry} receiveShadow castShadow>
        <meshStandardMaterial color="#64748B" roughness={0.9} metalness={0.1} />
      </mesh>

      {vehicles.map((v) => (
        <AnimatedVehicle key={v.id} type={v.type} offset={v.offset} speed={v.speed} colorIdx={v.colorIdx} />
      ))}
    </group>
  );
}
