'use client';

/**
 * TunnelFerropista — el túnel de base y los convoyes que lo cruzan.
 *
 * ESQUEMA ILUSTRATIVO. Las proporciones del túnel, los portales y el convoy
 * no son métricas. Datos reales detrás del esquema, para el texto que lo
 * acompaña, nunca para leer del dibujo:
 *   · Convoy: locomotora + vagón para conductores + 35 plataformas
 *     + 2 plataformas de acceso [F, dia. 23]. Aquí se dibujan 5 plataformas.
 *   · Longitud de tren: hasta 750 m [F, dia. 23].
 *   · Frecuencia declarada en fase inicial: 140 trenes/día [F, dia. 20].
 *   · Ciclo de operación: 25 + 30 + 15 = 70 min [F, dia. 23]; de esos,
 *     30 min son el desplazamiento. El ciclo completo NO es el tiempo de túnel.
 */

import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Locomotive, Wagon, Truck, TRUCK_COLORS } from './Vehicles';

function TunnelPortal({ x, isLeft }: { x: number; isLeft: boolean }) {
  const dir = isLeft ? -1 : 1;
  return (
    <group position={[x, 0, -2]}>
      <mesh position={[0, 0, 0]} rotation={[0, Math.PI / 2, 0]} castShadow>
        <torusGeometry args={[1.6, 0.25, 16, 32, Math.PI]} />
        <meshStandardMaterial color="#A9C0CE" roughness={0.7} />
      </mesh>
      <mesh position={[-dir * 0.1, 0, 0]} rotation={[0, dir * Math.PI / 2, 0]}>
        <circleGeometry args={[1.6, 32, 0, Math.PI]} />
        <meshBasicMaterial color="#05080A" />
      </mesh>
    </group>
  );
}

function TunnelBody() {
  const len = 17.8;
  return (
    <mesh position={[0, 0, -2]} rotation={[0, 0, Math.PI / 2]} receiveShadow>
      <cylinderGeometry args={[1.6, 1.6, len, 24, 1, true, 0, Math.PI]} />
      <meshStandardMaterial color="#5A6D7A" roughness={0.9} side={THREE.DoubleSide} />
    </mesh>
  );
}

function Train() {
  return (
    <group position={[0, 0.35, -2]}>
      <group position={[1.5, 0, 0]}>
        <Locomotive />
      </group>
      {[0, 1, 2, 3, 4].map((i) => (
        <group position={[-1.7 - i * 1.7, 0, 0]} key={i}>
          <Wagon />
          <group position={[0, 0.3, 0]}>
            <Truck
              bodyColor={TRUCK_COLORS[i % TRUCK_COLORS.length].body}
              cabColor={TRUCK_COLORS[(i + 1) % TRUCK_COLORS.length].cab}
            />
          </group>
        </group>
      ))}
    </group>
  );
}

export default function TunnelFerropista() {
  const train1Ref = useRef<THREE.Group>(null);
  const train2Ref = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime() % 8;

    const updateTrain = (ref: React.RefObject<THREE.Group | null>, delay: number) => {
      if (!ref.current) return;
      const localT = (t + 8 - delay) % 8;

      if (localT < 6) {
        ref.current.position.x = -11.5 + (localT / 6) * 30;
        ref.current.visible = true;
      } else {
        ref.current.visible = false;
      }
    };

    updateTrain(train1Ref, 0);
    updateTrain(train2Ref, 4);
  });

  return (
    <group>
      <mesh position={[0, 0.15, -2]} receiveShadow>
        <boxGeometry args={[40, 0.05, 1.2]} />
        <meshStandardMaterial color="#4B5563" roughness={0.9} />
      </mesh>
      <mesh position={[0, 0.18, -1.7]} receiveShadow>
        <boxGeometry args={[40, 0.02, 0.05]} />
        <meshStandardMaterial color="#9CA3AF" metalness={0.8} roughness={0.2} />
      </mesh>
      <mesh position={[0, 0.18, -2.3]} receiveShadow>
        <boxGeometry args={[40, 0.02, 0.05]} />
        <meshStandardMaterial color="#9CA3AF" metalness={0.8} roughness={0.2} />
      </mesh>

      <TunnelBody />
      <TunnelPortal x={-9} isLeft />
      <TunnelPortal x={9} isLeft={false} />

      <group ref={train1Ref} visible={false}>
        <Train />
      </group>
      <group ref={train2Ref} visible={false}>
        <Train />
      </group>
    </group>
  );
}
