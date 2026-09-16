'use client';

/**
 * Vehicles — modelos low-poly para las escenas comparativas.
 *
 * Procedencia: boceto `paz-y-region-gemini` (React Three Fiber), integrado al
 * sitio del semillero GEOPAV. Geometría sin cambios respecto al boceto.
 *
 * ESQUEMA ILUSTRATIVO. Ninguna proporción de estos modelos es métrica.
 */

import type { ReactNode } from 'react';
import * as THREE from 'three';

/* ═══════ Paleta ═══════ */
export const TRUCK_COLORS = [
  { body: '#C07B52', cab: '#D4956A' },
  { body: '#B06050', cab: '#C8796A' },
  { body: '#C8A050', cab: '#DCBA6A' },
  { body: '#E53935', cab: '#EF5350' },
  { body: '#455A64', cab: '#78909C' },
  { body: '#F57C00', cab: '#FF9800' },
  { body: '#5D4037', cab: '#8D6E63' },
];

export const CAR_COLORS = [
  '#6B9DC2', '#7BAD8A', '#C4869E', '#8D84A8', '#D4A05C', '#1E88E5', '#43A047',
];

/* ═══════ Auto liviano ═══════ */
export function Car({ color = '#6B9DC2' }: { color?: string }) {
  return (
    <group>
      <mesh castShadow>
        <boxGeometry args={[0.5, 0.18, 0.24]} />
        <meshStandardMaterial color={color} roughness={0.6} metalness={0.2} />
      </mesh>
      <mesh position={[0.02, 0.14, 0]} castShadow>
        <boxGeometry args={[0.24, 0.13, 0.22]} />
        <meshStandardMaterial color={color} roughness={0.6} metalness={0.2} />
      </mesh>
      <mesh position={[0.02, 0.14, 0.115]}>
        <planeGeometry args={[0.2, 0.09]} />
        <meshStandardMaterial color="#D1E0ED" transparent opacity={0.7} roughness={0.1} metalness={0.3} side={THREE.DoubleSide} />
      </mesh>
      {[-0.15, 0.15].map((wx) => (
        <mesh key={wx} position={[wx, -0.1, 0]} rotation={[Math.PI / 2, 0, 0]} castShadow>
          <cylinderGeometry args={[0.06, 0.06, 0.28, 8]} />
          <meshStandardMaterial color="#2D3748" roughness={0.9} />
        </mesh>
      ))}
    </group>
  );
}

/* ═══════ Tractomula ═══════ */
export function Truck({ bodyColor = '#C07B52', cabColor = '#D4956A' }: { bodyColor?: string; cabColor?: string }) {
  return (
    <group>
      <mesh position={[-0.15, 0.05, 0]} castShadow>
        <boxGeometry args={[0.65, 0.32, 0.28]} />
        <meshStandardMaterial color={bodyColor} roughness={0.7} metalness={0.1} />
      </mesh>
      <mesh position={[0.32, 0, 0]} castShadow>
        <boxGeometry args={[0.28, 0.28, 0.26]} />
        <meshStandardMaterial color={cabColor} roughness={0.6} metalness={0.15} />
      </mesh>
      <mesh position={[0.47, 0.04, 0]}>
        <planeGeometry args={[0.01, 0.14]} />
        <meshStandardMaterial color="#D1E0ED" transparent opacity={0.7} roughness={0.1} metalness={0.3} side={THREE.DoubleSide} />
      </mesh>
      {[-0.32, -0.08, 0.22, 0.38].map((wx) => (
        <mesh key={wx} position={[wx, -0.14, 0]} rotation={[Math.PI / 2, 0, 0]} castShadow>
          <cylinderGeometry args={[0.07, 0.07, 0.32, 8]} />
          <meshStandardMaterial color="#1A202C" roughness={0.9} />
        </mesh>
      ))}
      <mesh position={[0.18, 0.22, 0.14]}>
        <cylinderGeometry args={[0.02, 0.02, 0.1, 6]} />
        <meshStandardMaterial color="#555" roughness={0.9} />
      </mesh>
    </group>
  );
}

/* ═══════ Locomotora ═══════ */
export function Locomotive() {
  return (
    <group>
      <mesh castShadow>
        <boxGeometry args={[1.4, 0.45, 0.38]} />
        <meshStandardMaterial color="#4A6E8B" roughness={0.5} metalness={0.3} />
      </mesh>
      <mesh position={[-0.45, 0.28, 0]} castShadow>
        <boxGeometry args={[0.45, 0.22, 0.36]} />
        <meshStandardMaterial color="#3A5872" roughness={0.5} metalness={0.3} />
      </mesh>
      <mesh position={[-0.45, 0.32, 0.19]}>
        <planeGeometry args={[0.3, 0.12]} />
        <meshStandardMaterial color="#A5C6DF" transparent opacity={0.8} roughness={0.1} side={THREE.DoubleSide} />
      </mesh>
      <mesh position={[0.71, 0, 0]}>
        <sphereGeometry args={[0.05, 8, 8]} />
        <meshStandardMaterial color="#F5E6C8" emissive="#F5E6C8" emissiveIntensity={0.5} />
      </mesh>
      {[-0.45, -0.15, 0.1, 0.35].map((wx) => (
        <mesh key={wx} position={[wx, -0.26, 0]} rotation={[Math.PI / 2, 0, 0]} castShadow>
          <cylinderGeometry args={[0.09, 0.09, 0.42, 8]} />
          <meshStandardMaterial color="#1F2937" roughness={0.9} />
        </mesh>
      ))}
    </group>
  );
}

/* ═══════ Plataforma portavehículos ═══════
   La fuente describe el convoy como locomotora + vagón para conductores +
   35 plataformas + 2 plataformas de acceso [F, dia. 23]. La escena dibuja
   cinco plataformas: es un esquema, no el convoy completo. */
export function Wagon({ children }: { children?: ReactNode }) {
  return (
    <group>
      <mesh castShadow>
        <boxGeometry args={[1.5, 0.1, 0.38]} />
        <meshStandardMaterial color="#7B8C9A" roughness={0.7} metalness={0.15} />
      </mesh>
      <mesh position={[-0.85, 0, 0]}>
        <boxGeometry args={[0.12, 0.06, 0.12]} />
        <meshStandardMaterial color="#B0B8C2" roughness={0.8} />
      </mesh>
      {[-0.45, -0.12, 0.12, 0.45].map((wx) => (
        <mesh key={wx} position={[wx, -0.09, 0]} rotation={[Math.PI / 2, 0, 0]} castShadow>
          <cylinderGeometry args={[0.07, 0.07, 0.42, 8]} />
          <meshStandardMaterial color="#1F2937" roughness={0.9} />
        </mesh>
      ))}
      {children}
    </group>
  );
}
