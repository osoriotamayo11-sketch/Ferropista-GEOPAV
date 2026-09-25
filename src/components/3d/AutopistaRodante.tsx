'use client';

/**
 * AutopistaRodante — cuatro escenas 3D del proceso operativo de la autopista rodante
 * [F, dia. 19]: estación, embarque por el extremo, desplazamiento en el túnel y descarga.
 *
 * ESQUEMA ILUSTRATIVO. Ninguna proporción es métrica; el convoy real tiene hasta 750 m,
 * locomotora, vagón para conductores, 35 plataformas y 2 plataformas de acceso en los
 * extremos [F, dia. 23]. Aquí se dibujan unas pocas plataformas.
 *
 * Procedencia: boceto `paz-y-region-gemini/src/components/3d/PiggybackSteps.tsx`
 * (Gemini, sep 2026). Cambios frente al boceto:
 *  - «Piggyback» se retira: la fuente llama al sistema «autopista rodante» (el camión
 *    completo viaja en la plataforma y el conductor en un vagón aparte), no transporte
 *    de semirremolques sin tractor, que es lo que «piggyback» designa.
 *  - Se añade el vagón para conductores y el pantógrafo: la fuente dibuja un tren
 *    eléctrico con coche de conductores detrás de la locomotora [F, dia. 23].
 *  - Se retira `<Environment preset="city" />`, que descarga un HDR de un CDN externo
 *    en tiempo de ejecución. Se sustituye por luz hemisférica, como en EscenaComparativa.
 *  - Sin sombras, `dpr` acotado y `frameloop` controlado desde fuera: el lienzo se
 *    detiene fuera de pantalla y queda estático con «reducir movimiento».
 *  - Escena 03 reencuadrada: el boceto dejaba media tarjeta de terreno vacío.
 */

import { useRef, useMemo, type ReactNode } from 'react';
import * as THREE from 'three';
import { useFrame, Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { Truck, Wagon, Locomotive, TRUCK_COLORS } from './Vehicles';

/* ═══════ Vagón para conductores y pantógrafo [F, dia. 23] ═══════ */

function VagonConductores() {
  return (
    <group>
      <mesh position={[0, 0.16, 0]} castShadow>
        <boxGeometry args={[1.45, 0.42, 0.38]} />
        <meshStandardMaterial color="#0F7B55" roughness={0.5} metalness={0.2} />
      </mesh>
      {[-0.5, -0.25, 0, 0.25, 0.5].map((wx) => (
        <group key={wx}>
          <mesh position={[wx, 0.22, 0.191]}>
            <planeGeometry args={[0.16, 0.12]} />
            <meshStandardMaterial color="#D8EEF7" roughness={0.1} />
          </mesh>
          <mesh position={[wx, 0.22, -0.191]} rotation={[0, Math.PI, 0]}>
            <planeGeometry args={[0.16, 0.12]} />
            <meshStandardMaterial color="#D8EEF7" roughness={0.1} />
          </mesh>
        </group>
      ))}
      {[-0.45, -0.12, 0.12, 0.45].map((wx) => (
        <mesh key={wx} position={[wx, -0.09, 0]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.07, 0.07, 0.42, 8]} />
          <meshStandardMaterial color="#1F2937" roughness={0.9} />
        </mesh>
      ))}
    </group>
  );
}

function Pantografo() {
  return (
    <group position={[0.15, 0.27, 0]}>
      <mesh position={[-0.08, 0.1, 0]} rotation={[0, 0, -0.6]}>
        <boxGeometry args={[0.02, 0.24, 0.02]} />
        <meshStandardMaterial color="#374151" metalness={0.6} roughness={0.4} />
      </mesh>
      <mesh position={[0.08, 0.1, 0]} rotation={[0, 0, 0.6]}>
        <boxGeometry args={[0.02, 0.24, 0.02]} />
        <meshStandardMaterial color="#374151" metalness={0.6} roughness={0.4} />
      </mesh>
      <mesh position={[0, 0.2, 0]}>
        <boxGeometry args={[0.04, 0.02, 0.3]} />
        <meshStandardMaterial color="#374151" metalness={0.6} roughness={0.4} />
      </mesh>
    </group>
  );
}

function LocomotoraElectrica() {
  return (
    <group>
      <Locomotive />
      <Pantografo />
    </group>
  );
}

/* ═══════ Componentes Base Reutilizables ═══════ */

function Ground({ color = "#e2e8f0" }) {
  return (
    <mesh position={[0, -0.01, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
      <planeGeometry args={[30, 20]} />
      <meshStandardMaterial color={color} roughness={0.8} />
    </mesh>
  );
}

function AsphaltStrip({ position = [0, 0, 0] as [number, number, number], length = 10, width = 1.2 }) {
  const segmentCount = Math.floor(length);
  return (
    <group position={position} rotation={[-Math.PI / 2, 0, 0]}>
      <mesh receiveShadow>
        <planeGeometry args={[length, width]} />
        <meshStandardMaterial color="#374151" roughness={0.9} />
      </mesh>
      {/* Línea punteada central */}
      {Array.from({ length: segmentCount }).map((_, i) => (
        <mesh key={i} position={[-length / 2 + i + 0.5, 0.01, 0]}>
          <planeGeometry args={[0.5, 0.04]} />
          <meshStandardMaterial color="#FFFFFF" />
        </mesh>
      ))}
    </group>
  );
}

function Bollard({ position }: { position: [number, number, number] }) {
  return (
    <mesh position={position} castShadow>
      <cylinderGeometry args={[0.06, 0.06, 0.3, 8]} />
      <meshStandardMaterial color="#EAB308" roughness={0.4} />
      <mesh position={[0, 0.1, 0]}>
        <cylinderGeometry args={[0.065, 0.065, 0.05, 8]} />
        <meshStandardMaterial color="#111827" />
      </mesh>
    </mesh>
  );
}

function Rails({ length = 10, position = [0, 0, 0] as [number, number, number] }) {
  const sleepers = Math.floor(length / 0.4);
  return (
    <group position={position}>
      {/* Balasto */}
      <mesh position={[0, 0.02, 0]} receiveShadow>
        <boxGeometry args={[length, 0.04, 0.8]} />
        <meshStandardMaterial color="#78716c" roughness={1} />
      </mesh>
      {/* Rieles (Metal) */}
      <mesh position={[0, 0.06, 0.18]} castShadow>
        <boxGeometry args={[length, 0.04, 0.02]} />
        <meshStandardMaterial color="#9ca3af" metalness={0.8} roughness={0.3} />
      </mesh>
      <mesh position={[0, 0.06, -0.18]} castShadow>
        <boxGeometry args={[length, 0.04, 0.02]} />
        <meshStandardMaterial color="#9ca3af" metalness={0.8} roughness={0.3} />
      </mesh>
      {/* Durmientes (Madera) */}
      {Array.from({ length: sleepers }).map((_, i) => (
        <mesh key={i} position={[-length / 2 + i * 0.4 + 0.2, 0.04, 0]} castShadow>
          <boxGeometry args={[0.1, 0.02, 0.6]} />
          <meshStandardMaterial color="#451a03" roughness={0.9} />
        </mesh>
      ))}
    </group>
  );
}

function Ramp({ position = [0,0,0] as [number,number,number], heightDiff = 0.15, horizontalLength = 1.8, flip = false }: { position?: [number,number,number]; heightDiff?: number; horizontalLength?: number; flip?: boolean }) {
  const rampLength = Math.sqrt(horizontalLength * horizontalLength + heightDiff * heightDiff);
  const angle = Math.atan2(heightDiff, horizontalLength);
  const dir = flip ? -1 : 1;
  
  return (
    <group position={position}>
      {/* Rampa principal */}
      <group position={[dir * horizontalLength / 2, heightDiff / 2, 0]} rotation={[0, 0, dir * angle]}>
        <mesh castShadow receiveShadow>
          <boxGeometry args={[rampLength, 0.05, 0.5]} />
          <meshStandardMaterial color="#607D8B" metalness={0.5} roughness={0.4} />
        </mesh>
        {/* Barandas laterales */}
        <mesh position={[0, 0.15, 0.24]} castShadow>
          <boxGeometry args={[rampLength, 0.25, 0.02]} />
          <meshStandardMaterial color="#78909C" metalness={0.4} roughness={0.5} />
        </mesh>
        <mesh position={[0, 0.15, -0.24]} castShadow>
          <boxGeometry args={[rampLength, 0.25, 0.02]} />
          <meshStandardMaterial color="#78909C" metalness={0.4} roughness={0.5} />
        </mesh>
      </group>
    </group>
  );
}

function LightPole({ position }: { position: [number, number, number] }) {
  return (
    <group position={position}>
      <mesh position={[0, 0.6, 0]} castShadow>
        <cylinderGeometry args={[0.03, 0.04, 1.2, 6]} />
        <meshStandardMaterial color="#616161" metalness={0.6} roughness={0.4} />
      </mesh>
      {/* Brazo horizontal */}
      <mesh position={[0.2, 1.15, 0]} rotation={[0, 0, Math.PI / 6]}>
        <cylinderGeometry args={[0.02, 0.02, 0.4, 4]} />
        <meshStandardMaterial color="#616161" metalness={0.6} roughness={0.4} />
      </mesh>
      {/* Foco */}
      <mesh position={[0.35, 1.1, 0]}>
        <sphereGeometry args={[0.05, 6, 6]} />
        <meshStandardMaterial color="#FFF9C4" emissive="#FFF9C4" emissiveIntensity={0.5} />
      </mesh>
    </group>
  );
}

function BarrierFence({ position, length = 3 }: { position: [number, number, number]; length?: number }) {
  const postCount = Math.floor(length / 0.8) + 1;
  return (
    <group position={position}>
      {/* Barra horizontal */}
      <mesh position={[0, 0.35, 0]}>
        <boxGeometry args={[length, 0.04, 0.03]} />
        <meshStandardMaterial color="#E0E0E0" metalness={0.5} roughness={0.3} />
      </mesh>
      <mesh position={[0, 0.2, 0]}>
        <boxGeometry args={[length, 0.04, 0.03]} />
        <meshStandardMaterial color="#E0E0E0" metalness={0.5} roughness={0.3} />
      </mesh>
      {/* Postes */}
      {Array.from({ length: postCount }, (_, i) => {
        const x = -length / 2 + i * (length / (postCount - 1));
        return (
          <mesh key={i} position={[x, 0.25, 0]} castShadow>
            <boxGeometry args={[0.04, 0.5, 0.04]} />
            <meshStandardMaterial color="#BDBDBD" metalness={0.4} roughness={0.5} />
          </mesh>
        );
      })}
    </group>
  );
}


function SmokeParticle({ offset }: { offset: number }) {
  const ref = useRef<THREE.Mesh>(null);
  useFrame(({ clock }) => {
    if (!ref.current) return;
    const t = (clock.getElapsedTime() + offset) % 1.5;
    const progress = t / 1.5;

    // Sube y se va ligeramente hacia atrás
    ref.current.position.y = progress * 0.4;
    ref.current.position.x = -progress * 0.3;

    // Crece
    const scale = 1 + progress * 2.5;
    ref.current.scale.set(scale, scale, scale);

    // Se desvanece
    if (ref.current.material) {
      (ref.current.material as THREE.MeshStandardMaterial).opacity = 1 - progress;
    }
  });
  
  return (
    <mesh ref={ref}>
      <sphereGeometry args={[0.03, 4, 4]} />
      <meshStandardMaterial color="#B0BEC5" transparent opacity={0.8} depthWrite={false} flatShading />
    </mesh>
  );
}

function AnimatedSmoke({ position }: { position: [number, number, number] }) {
  return (
    <group position={position}>
      <SmokeParticle offset={0} />
      <SmokeParticle offset={0.5} />
      <SmokeParticle offset={1.0} />
    </group>
  );
}

/* ═══════ Contenedor StepCard ═══════ */

interface LienzoProps {
  cameraPosition: [number, number, number];
  cameraFov: number;
  cameraTarget?: [number, number, number];
  noFog?: boolean;
  frameloop: 'always' | 'never' | 'demand';
  children: ReactNode;
}

function Lienzo({ cameraPosition, cameraFov, cameraTarget, noFog, frameloop, children }: LienzoProps) {
  return (
    <div className="relative h-full w-full bg-sky-50">
      <Canvas dpr={[1, 1.75]} frameloop={frameloop} camera={{ position: cameraPosition, fov: cameraFov }}>
        <ambientLight intensity={0.4} />
        <directionalLight position={[5, 10, 5]} intensity={1.4} castShadow
          shadow-mapSize-width={1024} shadow-mapSize-height={1024}
          shadow-camera-near={0.5} shadow-camera-far={30}
          shadow-camera-left={-8} shadow-camera-right={8}
          shadow-camera-top={8} shadow-camera-bottom={-8} />
        <directionalLight position={[-3, 5, -3]} intensity={0.3} color="#B0C4DE" />
        
        <hemisphereLight args={['#DCEBF5', '#4A5D3A', 0.55]} />
        
        {/* Cámaras fijas sin rotación ni zoom */}
        <OrbitControls 
          makeDefault 
          target={cameraTarget || [0, 0, 0]} 
          enableZoom={false} 
          enablePan={false} 
          enableRotate={false} 
        />
        
        {!noFog && <fog attach="fog" args={['#E8EEF2', 15, 35]} />}
        
        {children}
      </Canvas>
    </div>
  );
}

/* ═══════ Paso 01: Estación Terminal ═══════ */

function Step01Scene() {
  const truckRef = useRef<THREE.Group>(null);
  
  useFrame(({ clock }) => {
    if (!truckRef.current) return;
    const t = (clock.getElapsedTime() % 6) / 6;
    const x = -8 + t * 16;
    truckRef.current.position.set(x, 0.21, 3.5);
  });

  return (
    <group>
      <Ground color="#90A4AE" />
      
      {/* Edificio de la terminal, más estrecho y movido hacia atrás */}
      <group position={[0, 0, -2.5]}>
        <mesh position={[0, 1.1, -1.9]} castShadow><boxGeometry args={[3.4, 2.2, 0.2]} /><meshStandardMaterial color="#CFD8DC" /></mesh>
        <mesh position={[-1.6, 1.1, -1]} castShadow><boxGeometry args={[0.2, 2.2, 2]} /><meshStandardMaterial color="#CFD8DC" /></mesh>
        <mesh position={[1.6, 1.1, -1]} castShadow><boxGeometry args={[0.2, 2.2, 2]} /><meshStandardMaterial color="#CFD8DC" /></mesh>
        <mesh position={[-0.85, 2.4, 0]} rotation={[0, 0, 0.2]} castShadow><boxGeometry args={[1.8, 0.1, 4.4]} /><meshStandardMaterial color="#78909C" /></mesh>
        <mesh position={[0.85, 2.4, 0]} rotation={[0, 0, -0.2]} castShadow><boxGeometry args={[1.8, 0.1, 4.4]} /><meshStandardMaterial color="#78909C" /></mesh>
      </group>

      {/* 2 Camiones estáticos, parqueados profundo bajo el techo */}
      <group position={[-0.8, 0.21, -2.5]} rotation={[0, 0.4, 0]} scale={1.3}>
        <Truck bodyColor={TRUCK_COLORS[0].body} cabColor={TRUCK_COLORS[0].cab} />
      </group>
      <group position={[0.8, 0.21, -2.5]} rotation={[0, 0.4, 0]} scale={1.3}>
        <Truck bodyColor={TRUCK_COLORS[3].body} cabColor={TRUCK_COLORS[3].cab} />
      </group>

      {/* Vía férrea en el medio */}
      <Rails length={20} position={[0, 0, 0.5]} />
      <group position={[-2, 0.15, 0.5]}>
        <LocomotoraElectrica />
      </group>
      <group position={[-0.2, 0.1, 0.5]}>
        <VagonConductores />
      </group>
      <group position={[1.4, 0.1, 0.5]}>
        <Wagon />
      </group>

      {/* Elementos decorativos urbanos agregados */}
      <BarrierFence position={[0, 0, 1.8]} length={20} />
      
      {/* Postes de luz separados de la baranda (hacia el asfalto) */}
      <LightPole position={[-4, 0, 2.5]} />
      <LightPole position={[4, 0, 2.5]} />
      
      <Bollard position={[-1.5, 0, -0.5]} />
      <Bollard position={[1.5, 0, -0.5]} />

      {/* Vía de asfalto al frente */}
      <AsphaltStrip position={[0, 0, 3.5]} length={16} width={1.8} />
      
      <group ref={truckRef} position={[-8, 0.21, 3.5]} scale={1.3}>
        <Truck bodyColor={TRUCK_COLORS[5].body} cabColor={TRUCK_COLORS[5].cab} />
        <AnimatedSmoke position={[0.18, 0.28, 0.14]} />
      </group>
    </group>
  );
}

/* ═══════ Paso 02: Embarque Ro-Ro ═══════ */

function Step02Scene() {
  const truckRef = useRef<THREE.Group>(null);
  
  useFrame(({ clock }) => {
    if (!truckRef.current) return;
    const t = (clock.getElapsedTime() % 5) / 5;
    
    let x, y;
    if (t <= 0.4) {
      const p = t / 0.4;
      x = -5.5 + p * (-4 - -5.5);
      y = 0.21;
    } else {
      const p = (t - 0.4) / 0.6;
      x = -4 + p * (-1.4 - -4);
      y = 0.21;
      if (x >= -4 && x <= -2.2) {
        const ratio = (x - -4) / (-2.2 - -4);
        y = 0.21 + ratio * (0.36 - 0.21);
      } else if (x > -2.2) {
        y = 0.36;
      }
    }
    
    truckRef.current.position.set(x, y, 0);
  });

  return (
    <group>
      <Ground color="#90A4AE" />
      <AsphaltStrip position={[-3, 0, 0]} length={6} width={1.2} />
      <Rails length={12} position={[0.5, 0, 0]} />
      
      <group position={[3.5, 0.15, 0]}>
        <LocomotoraElectrica />
      </group>
      <group position={[1.8, 0.1, 0]}>
        <VagonConductores />
      </group>
      <group position={[0.2, 0.1, 0]}>
        <Wagon>
          <group position={[0, 0.25, 0]} scale={1.3}>
            <Truck bodyColor={TRUCK_COLORS[5].body} cabColor={TRUCK_COLORS[5].cab} />
          </group>
        </Wagon>
      </group>
      <group position={[-1.4, 0.1, 0]}>
        <Wagon />
      </group>
      
      <Ramp position={[-4, 0, 0]} heightDiff={0.15} horizontalLength={1.8} />
      
      <group ref={truckRef} position={[-5.5, 0.21, 0]} scale={1.3}>
        <Truck bodyColor={TRUCK_COLORS[0].body} cabColor={TRUCK_COLORS[0].cab} />
        <AnimatedSmoke position={[0.18, 0.28, 0.14]} />
      </group>
      
      <Bollard position={[-3, 0, 1]} />
      <Bollard position={[-1, 0, 1]} />

      <LightPole position={[-4, 0, -2]} />
      <LightPole position={[4, 0, -2]} />
      <BarrierFence position={[0, 0, -1]} length={10} />
    </group>
  );
}

/* ═══════ Paso 03: Tránsito Subterráneo ═══════ */

function Step03Scene() {
  const convoyRef = useRef<THREE.Group>(null);
  useFrame(({ clock }) => {
    if (!convoyRef.current) return;
    const t = (clock.getElapsedTime() % 6) / 6;
    const x = -8 + t * 16;
    convoyRef.current.position.set(x, 0, 0);
  });

  const mountainRocks = useMemo(() => {
    const arr = [];
    for (let i = -16; i <= 16; i++) {
      const x = i * 1.0;
      // Capa 1: Borde exacto del techo (radio pequeño para no atravesar y=2.4)
      const r1 = 0.6 + Math.abs(Math.sin(i)) * 0.4;
      arr.push(
        <mesh key={`r1-${i}`} position={[x, 2.4 + r1, -0.2]} rotation={[Math.sin(i), Math.cos(i), 0]} castShadow receiveShadow>
          <dodecahedronGeometry args={[r1]} />
          <meshStandardMaterial color="#43A047" roughness={0.9} flatShading />
        </mesh>
      );
      // Capa 2: Llenado medio
      const r2 = 1.2 + Math.abs(Math.cos(i)) * 0.8;
      arr.push(
        <mesh key={`r2-${i}`} position={[x + 0.5, 3.5 + r2, -0.8]} rotation={[Math.cos(i), Math.sin(i), 0]} castShadow receiveShadow>
          <dodecahedronGeometry args={[r2]} />
          <meshStandardMaterial color="#388E3C" roughness={0.9} flatShading />
        </mesh>
      );
      // Capa 3: Picos de fondo
      if (Math.abs(i) % 2 === 0) {
        const r3 = 2.5 + Math.abs(Math.sin(i*2)) * 2;
        arr.push(
          <mesh key={`r3-${i}`} position={[x - 0.5, 6 + r3, -1.8]} rotation={[0, Math.sin(i), Math.cos(i)]} castShadow receiveShadow>
            <dodecahedronGeometry args={[r3]} />
            <meshStandardMaterial color="#2E7D32" roughness={0.9} flatShading />
          </mesh>
        );
      }
    }
    return arr;
  }, []);

  return (
    <group>
      {/* Corte de la roca bajo el piso del túnel: la escena es una sección, no un paisaje */}
      <mesh position={[0, -3, 0.6]}>
        <boxGeometry args={[40, 6, 1.2]} />
        <meshStandardMaterial color="#5D5348" roughness={1} />
      </mesh>
      
      {/* Montaña 3D (Núcleo sólido + Rocas densas) */}
      <group>
        {/* Núcleo sólido para sellar fugas de luz (0 clipping garantizado) */}
        {/* Pared trasera (z <= -1.2) */}
        <mesh position={[0, 6, -2.2]} receiveShadow castShadow>
          <boxGeometry args={[40, 12, 2]} />
          <meshStandardMaterial color="#1B5E20" roughness={1} />
        </mesh>
        {/* Techo macizo (y >= 2.4, z de -1.2 a 0) */}
        <mesh position={[0, 7.2, -0.6]} receiveShadow castShadow>
          <boxGeometry args={[40, 9.6, 1.2]} />
          <meshStandardMaterial color="#1B5E20" roughness={1} />
        </mesh>
        
        {/* Rocas pequeñas y densas decorando el frente */}
        {mountainRocks}
      </group>
      
      <mesh position={[0, 1.2, 0]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[1.2, 1.2, 20, 32, 1, true, Math.PI / 2, Math.PI]} />
        <meshStandardMaterial color="#546E7A" roughness={0.9} side={THREE.DoubleSide} />
      </mesh>
      
      {/* Piso oscuro exclusivo del túnel */}
      <mesh position={[0, 0.05, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[20, 2.4]} />
        <meshStandardMaterial color="#37474F" />
      </mesh>
      
      <Rails length={20} position={[0, 0.06, 0]} />
      
      <mesh position={[0, 2.2, 0]} rotation={[0, 0, Math.PI/2]}>
        <cylinderGeometry args={[0.015, 0.015, 20, 4]} />
        <meshStandardMaterial color="#B0BEC5" />
      </mesh>
      
      <group ref={convoyRef} position={[-8, 0, 0]}>
        <group position={[3, 0.15, 0]}>
          <LocomotoraElectrica />
        </group>
        <group position={[1.4, 0.1, 0]}>
          <VagonConductores />
        </group>
        {[1, 2, 3].map(i => (
          <group key={i} position={[3 - 1.6 - i * 1.6, 0.1, 0]}>
            <Wagon>
              <group position={[0, 0.25, 0]} scale={1.3}>
                <Truck
                  bodyColor={TRUCK_COLORS[i % TRUCK_COLORS.length].body}
                  cabColor={TRUCK_COLORS[(i + 1) % TRUCK_COLORS.length].cab}
                />
              </group>
            </Wagon>
          </group>
        ))}
      </group>
    </group>
  );
}

/* ═══════ Paso 04: Descarga y Ruta ═══════ */

function Step04Scene() {
  const truckRef = useRef<THREE.Group>(null);
  
  useFrame(({ clock }) => {
    if (!truckRef.current) return;
    const t = (clock.getElapsedTime() % 5) / 5;
    
    let x, y;
    if (t <= 0.6) {
      const p = t / 0.6;
      x = 1.4 + p * (3.95 - 1.4);
      y = 0.36;
      if (x >= 2.15 && x <= 3.95) {
        const ratio = (x - 2.15) / (3.95 - 2.15);
        y = 0.36 - ratio * (0.36 - 0.21);
      }
    } else {
      const p = (t - 0.6) / 0.4;
      const easedP = p * p;
      x = 3.95 + easedP * (6 - 3.95);
      y = 0.21;
    }
    
    truckRef.current.position.set(x, y, 0);
  });

  return (
    <group>
      <Ground color="#90A4AE" />
      
      <Rails length={20} position={[-0.5, 0, 0]} />
      <AsphaltStrip position={[7, 0, 0]} length={8} width={1.2} />
      
      <group position={[-3.5, 0.15, 0]}>
        <LocomotoraElectrica />
      </group>
      <group position={[-1.8, 0.1, 0]}>
        <VagonConductores />
      </group>
      <group position={[-0.2, 0.1, 0]}>
        <Wagon>
          <group position={[0, 0.25, 0]} scale={1.3}>
            <Truck bodyColor={TRUCK_COLORS[5].body} cabColor={TRUCK_COLORS[5].cab} />
          </group>
        </Wagon>
      </group>
      <group position={[1.4, 0.1, 0]}>
        <Wagon />
      </group>
      
      <Ramp position={[2.15, 0, 0]} heightDiff={0.15} horizontalLength={1.8} flip={true} />
      
      <group ref={truckRef} position={[1.4, 0.36, 0]} scale={1.3}>
        <Truck bodyColor={TRUCK_COLORS[0].body} cabColor={TRUCK_COLORS[0].cab} />
        <AnimatedSmoke position={[0.18, 0.28, 0.14]} />
      </group>
      
      <group position={[5, 0, 1]}>
        <mesh position={[0, 0.5, 0]}>
          <cylinderGeometry args={[0.04, 0.04, 1, 6]} />
          <meshStandardMaterial color="#757575" roughness={0.7} />
        </mesh>
        <mesh position={[0, 1.05, 0]}>
          <boxGeometry args={[0.9, 0.4, 0.03]} />
          <meshStandardMaterial color="#1B5E20" />
        </mesh>
        <mesh position={[0, 1.05, 0.016]}>
          <planeGeometry args={[0.7, 0.2]} />
          <meshStandardMaterial color="#FFFFFF" />
        </mesh>
      </group>
      
      <Bollard position={[2, 0, 1]} />
      <Bollard position={[3.5, 0, 1]} />
      <Bollard position={[5, 0, 1]} />

      <LightPole position={[-4, 0, -2]} />
      <LightPole position={[4, 0, -2]} />
      <BarrierFence position={[0, 0, -1]} length={10} />
    </group>
  );
}

/* ═══════ Exportación ═══════ */

export type PasoAutopista = '01' | '02' | '03' | '04';

const CAMARAS: Record<PasoAutopista, { pos: [number, number, number]; fov: number; target?: [number, number, number]; noFog?: boolean }> = {
  '01': { pos: [8.3, 6.3, 8.3], fov: 35 },
  '02': { pos: [7.3, 5.3, 7.3], fov: 35 },
  '03': { pos: [0, 1.4, 12], fov: 34, target: [0, 1.4, 0], noFog: true },
  '04': { pos: [8.3, 5.3, 7.3], fov: 35, target: [1, 0, 0] },
};

export default function AutopistaRodante({ paso, animar }: { paso: PasoAutopista; animar: boolean }) {
  const c = CAMARAS[paso];
  return (
    <Lienzo cameraPosition={c.pos} cameraFov={c.fov} cameraTarget={c.target} noFog={c.noFog}
            frameloop={animar ? 'always' : 'demand'}>
      {paso === '01' && <Step01Scene />}
      {paso === '02' && <Step02Scene />}
      {paso === '03' && <Step03Scene />}
      {paso === '04' && <Step04Scene />}
    </Lienzo>
  );
}
