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
 *  - Sin sombras (el lienzo compartido no activa `shadows`): se retiraron `castShadow`,
 *    `receiveShadow` y la configuración de `shadow-map` del `directionalLight`, que no
 *    tenían efecto.
 *  - Escena 03 reencuadrada: el boceto dejaba media tarjeta de terreno vacío.
 *  - Movimiento: cada vehículo sigue una línea de tiempo por tramos (entrada con
 *    aceleración → pausa → salida con aceleración → reinicio) con «smoothstep» en vez
 *    de velocidad lineal constante, y se desvanece (escala) en los 0,3 s antes y después
 *    de cada reinicio, así el salto de posición nunca se ve. El convoy de la escena 03
 *    cruza a velocidad constante (es un tren en crucero) y se dibuja por duplicado,
 *    desfasado medio ciclo, para que el túnel no quede vacío mientras el otro da la vuelta.
 *  - Cada tarjeta monta su propio <Canvas> (como antes de introducir el lienzo
 *    compartido, que se retiró: el <div position:fixed> del lienzo vivía dentro de la
 *    tarjeta con transform de framer-motion, así que quedaba mal alineado durante la
 *    animación de entrada y al hacer scroll). La cámara, las luces y la niebla se
 *    declaran directamente dentro del <Canvas> de esta escena.
 *  - Rocas de la escena 03 instanciadas (`<Instances>`/`<Instance>` de drei): antes cada
 *    una tenía su propia malla y material; ahora comparten geometría y hay un material
 *    por capa de color (3 en total).
 */

import { useRef, useMemo, useState, type RefObject } from 'react';
import * as THREE from 'three';
import { Canvas, useFrame } from '@react-three/fiber';
import { PerspectiveCamera, Instances, Instance } from '@react-three/drei';
import { Truck, Wagon, Locomotive, TRUCK_COLORS } from './Vehicles';
import Humo from './Humo';

/* ═══════ Ayudante de movimiento común a las cuatro escenas ═══════ */

/** Smoothstep: acelera al salir, decelera al llegar. `t` se acota a [0, 1]. */
function suave(t: number): number {
  const c = t < 0 ? 0 : t > 1 ? 1 : t;
  return c * c * (3 - 2 * c);
}

/** Cicla `tiempo` sobre una serie de tramos (en segundos) y da el tramo activo y su progreso 0..1. */
function fasear(tiempo: number, tramos: number[]): { fase: number; p: number } {
  const total = tramos.reduce((a, b) => a + b, 0);
  let resto = tiempo % total;
  for (let i = 0; i < tramos.length; i++) {
    if (resto < tramos[i]) return { fase: i, p: tramos[i] > 0 ? resto / tramos[i] : 1 };
    resto -= tramos[i];
  }
  return { fase: tramos.length - 1, p: 1 };
}

/** Duración (s) del desvanecido de entrada/salida: el vehículo nunca "salta" a la vista. */
const DESVANECER = 0.3;
const ESCALA_MIN = 0.0001; // evita escala exactamente 0 (matrices degeneradas)

/** Progreso de aparición al inicio de una fase, dados su progreso 0..1 y su duración en segundos. */
function aparece(p: number, duracionFase: number): number {
  if (duracionFase <= 0) return 1;
  return suave(Math.min(1, (p * duracionFase) / DESVANECER));
}

/** Progreso de desaparición al final de una fase, dados su progreso 0..1 y su duración en segundos. */
function desaparece(p: number, duracionFase: number): number {
  if (duracionFase <= 0) return 1;
  const restante = (1 - p) * duracionFase;
  return restante < DESVANECER ? suave(restante / DESVANECER) : 1;
}

/* ═══════ Vagón para conductores y pantógrafo [F, dia. 23] ═══════ */

function VagonConductores() {
  return (
    <group>
      <mesh position={[0, 0.16, 0]}>
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
    <mesh position={[0, -0.01, 0]} rotation={[-Math.PI / 2, 0, 0]}>
      <planeGeometry args={[30, 20]} />
      <meshStandardMaterial color={color} roughness={0.8} />
    </mesh>
  );
}

function AsphaltStrip({ position = [0, 0, 0] as [number, number, number], length = 10, width = 1.2 }) {
  const segmentCount = Math.floor(length);
  return (
    <group position={position} rotation={[-Math.PI / 2, 0, 0]}>
      <mesh>
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
    <mesh position={position}>
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
      <mesh position={[0, 0.02, 0]}>
        <boxGeometry args={[length, 0.04, 0.8]} />
        <meshStandardMaterial color="#78716c" roughness={1} />
      </mesh>
      {/* Rieles (Metal) */}
      <mesh position={[0, 0.06, 0.18]}>
        <boxGeometry args={[length, 0.04, 0.02]} />
        <meshStandardMaterial color="#9ca3af" metalness={0.8} roughness={0.3} />
      </mesh>
      <mesh position={[0, 0.06, -0.18]}>
        <boxGeometry args={[length, 0.04, 0.02]} />
        <meshStandardMaterial color="#9ca3af" metalness={0.8} roughness={0.3} />
      </mesh>
      {/* Durmientes (Madera) */}
      {Array.from({ length: sleepers }).map((_, i) => (
        <mesh key={i} position={[-length / 2 + i * 0.4 + 0.2, 0.04, 0]}>
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
        <mesh>
          <boxGeometry args={[rampLength, 0.05, 0.5]} />
          <meshStandardMaterial color="#607D8B" metalness={0.5} roughness={0.4} />
        </mesh>
        {/* Barandas laterales */}
        <mesh position={[0, 0.15, 0.24]}>
          <boxGeometry args={[rampLength, 0.25, 0.02]} />
          <meshStandardMaterial color="#78909C" metalness={0.4} roughness={0.5} />
        </mesh>
        <mesh position={[0, 0.15, -0.24]}>
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
      <mesh position={[0, 0.6, 0]}>
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
          <mesh key={i} position={[x, 0.25, 0]}>
            <boxGeometry args={[0.04, 0.5, 0.04]} />
            <meshStandardMaterial color="#BDBDBD" metalness={0.4} roughness={0.5} />
          </mesh>
        );
      })}
    </group>
  );
}

/* ═══════ Paso 01: Estación Terminal ═══════ */

const P01_X_INICIO = -8;
const P01_X_PAUSA = 0;
const P01_X_FIN = 8;
const P01_TRAMOS = [2.6, 1.3, 2.6, 1.5]; // entrada, pausa frente al edificio, salida, reinicio (oculto)

function Step01Scene() {
  const truckRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    if (!truckRef.current) return;
    const { fase, p } = fasear(clock.getElapsedTime(), P01_TRAMOS);
    let x = P01_X_INICIO;
    let escala = 1;
    if (fase === 0) {
      x = P01_X_INICIO + suave(p) * (P01_X_PAUSA - P01_X_INICIO);
      escala = aparece(p, P01_TRAMOS[0]);
    } else if (fase === 1) {
      x = P01_X_PAUSA;
    } else if (fase === 2) {
      x = P01_X_PAUSA + suave(p) * (P01_X_FIN - P01_X_PAUSA);
      escala = desaparece(p, P01_TRAMOS[2]);
    } else {
      x = P01_X_INICIO;
      escala = 0;
    }
    truckRef.current.position.set(x, 0.21, 3.5);
    const s = 1.3 * Math.max(escala, ESCALA_MIN);
    truckRef.current.scale.set(s, s, s);
  });

  return (
    <group>
      <Ground color="#90A4AE" />

      {/* Edificio de la terminal, más estrecho y movido hacia atrás */}
      <group position={[0, 0, -2.5]}>
        <mesh position={[0, 1.1, -1.9]}><boxGeometry args={[3.4, 2.2, 0.2]} /><meshStandardMaterial color="#CFD8DC" /></mesh>
        <mesh position={[-1.6, 1.1, -1]}><boxGeometry args={[0.2, 2.2, 2]} /><meshStandardMaterial color="#CFD8DC" /></mesh>
        <mesh position={[1.6, 1.1, -1]}><boxGeometry args={[0.2, 2.2, 2]} /><meshStandardMaterial color="#CFD8DC" /></mesh>
        <mesh position={[-0.85, 2.4, 0]} rotation={[0, 0, 0.2]}><boxGeometry args={[1.8, 0.1, 4.4]} /><meshStandardMaterial color="#78909C" /></mesh>
        <mesh position={[0.85, 2.4, 0]} rotation={[0, 0, -0.2]}><boxGeometry args={[1.8, 0.1, 4.4]} /><meshStandardMaterial color="#78909C" /></mesh>
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

      <group ref={truckRef} position={[P01_X_INICIO, 0.21, 3.5]} scale={1.3}>
        <Truck bodyColor={TRUCK_COLORS[5].body} cabColor={TRUCK_COLORS[5].cab} />
        <Humo position={[0.18, 0.28, 0.14]} particulas={3} opacidadMax={0.8} />
      </group>
    </group>
  );
}

/* ═══════ Paso 02: Embarque Ro-Ro ═══════ */

const P02_X_INICIO = -5.5;
const P02_X_PLATAFORMA = -1.4;
const P02_Y_SUELO = 0.21;
const P02_Y_PLATAFORMA = 0.36;
const P02_TRAMOS = [2.4, 1.4, 0.8, 1.4]; // entrada (sube rampa), embarcado sobre la plataforma, se desvanece, reinicio (oculto)

function Step02Scene() {
  const truckRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    if (!truckRef.current) return;
    const { fase, p } = fasear(clock.getElapsedTime(), P02_TRAMOS);
    let x = P02_X_INICIO;
    let y = P02_Y_SUELO;
    let escala = 1;

    if (fase === 0) {
      const sp = suave(p);
      if (sp <= 0.4) {
        const q = sp / 0.4;
        x = P02_X_INICIO + q * (-4 - P02_X_INICIO);
        y = P02_Y_SUELO;
      } else {
        const q = (sp - 0.4) / 0.6;
        x = -4 + q * (P02_X_PLATAFORMA - -4);
        y = P02_Y_SUELO;
        if (x >= -4 && x <= -2.2) {
          const ratio = (x - -4) / (-2.2 - -4);
          y = P02_Y_SUELO + ratio * (P02_Y_PLATAFORMA - P02_Y_SUELO);
        } else if (x > -2.2) {
          y = P02_Y_PLATAFORMA;
        }
      }
      escala = aparece(p, P02_TRAMOS[0]);
    } else if (fase === 1) {
      x = P02_X_PLATAFORMA;
      y = P02_Y_PLATAFORMA;
    } else if (fase === 2) {
      // El camión ya embarcado se desvanece: el tren se lo lleva fuera de cuadro.
      x = P02_X_PLATAFORMA;
      y = P02_Y_PLATAFORMA;
      escala = 1 - suave(p);
    } else {
      x = P02_X_INICIO;
      y = P02_Y_SUELO;
      escala = 0;
    }

    truckRef.current.position.set(x, y, 0);
    const s = 1.3 * Math.max(escala, ESCALA_MIN);
    truckRef.current.scale.set(s, s, s);
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

      <group ref={truckRef} position={[P02_X_INICIO, 0.21, 0]} scale={1.3}>
        <Truck bodyColor={TRUCK_COLORS[0].body} cabColor={TRUCK_COLORS[0].cab} />
        <Humo position={[0.18, 0.28, 0.14]} particulas={3} opacidadMax={0.8} />
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

const P03_MEDIO = 10; // mitad del recorrido, en x
const P03_VELOCIDAD = 2.2; // unidades/segundo, crucero constante
const P03_ZONA_DESVANECIDO = 1.6;

function posicionConvoy(
  tiempo: number,
  faseInicial: number,
  ref: RefObject<THREE.Group | null>,
) {
  if (!ref.current) return;
  const largo = P03_MEDIO * 2;
  let avance = (tiempo * P03_VELOCIDAD + faseInicial * largo) % largo;
  if (avance < 0) avance += largo;
  const x = -P03_MEDIO + avance;

  let escala = 1;
  if (x > P03_MEDIO - P03_ZONA_DESVANECIDO) {
    escala = suave((P03_MEDIO - x) / P03_ZONA_DESVANECIDO);
  } else if (x < -P03_MEDIO + P03_ZONA_DESVANECIDO) {
    escala = suave((x + P03_MEDIO) / P03_ZONA_DESVANECIDO);
  }

  ref.current.position.set(x, 0, 0);
  const s = Math.max(escala, ESCALA_MIN);
  ref.current.scale.set(s, s, s);
}

function ConvoyContenido({ colorOffset = 0 }: { colorOffset?: number }) {
  return (
    <>
      <group position={[3, 0.15, 0]}>
        <LocomotoraElectrica />
      </group>
      <group position={[1.4, 0.1, 0]}>
        <VagonConductores />
      </group>
      {[1, 2, 3].map((i) => (
        <group key={i} position={[3 - 1.6 - i * 1.6, 0.1, 0]}>
          <Wagon>
            <group position={[0, 0.25, 0]} scale={1.3}>
              <Truck
                bodyColor={TRUCK_COLORS[(i + colorOffset) % TRUCK_COLORS.length].body}
                cabColor={TRUCK_COLORS[(i + 1 + colorOffset) % TRUCK_COLORS.length].cab}
              />
            </group>
          </Wagon>
        </group>
      ))}
    </>
  );
}

function Step03Scene() {
  const convoyARef = useRef<THREE.Group>(null);
  const convoyBRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    posicionConvoy(t, 0, convoyARef);
    posicionConvoy(t, 0.5, convoyBRef);
  });

  const capas = useMemo(() => {
    type Roca = { posicion: [number, number, number]; rotacion: [number, number, number]; escala: number };
    const capa1: Roca[] = [];
    const capa2: Roca[] = [];
    const capa3: Roca[] = [];
    for (let i = -16; i <= 16; i++) {
      const x = i * 1.0;
      // Capa 1: Borde exacto del techo (radio pequeño para no atravesar y=2.4)
      const r1 = 0.6 + Math.abs(Math.sin(i)) * 0.4;
      capa1.push({ posicion: [x, 2.4 + r1, -0.2], rotacion: [Math.sin(i), Math.cos(i), 0], escala: r1 });
      // Capa 2: Llenado medio
      const r2 = 1.2 + Math.abs(Math.cos(i)) * 0.8;
      capa2.push({ posicion: [x + 0.5, 3.5 + r2, -0.8], rotacion: [Math.cos(i), Math.sin(i), 0], escala: r2 });
      // Capa 3: Picos de fondo
      if (Math.abs(i) % 2 === 0) {
        const r3 = 2.5 + Math.abs(Math.sin(i * 2)) * 2;
        capa3.push({ posicion: [x - 0.5, 6 + r3, -1.8], rotacion: [0, Math.sin(i), Math.cos(i)], escala: r3 });
      }
    }
    return { capa1, capa2, capa3 };
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
        <mesh position={[0, 6, -2.2]}>
          <boxGeometry args={[40, 12, 2]} />
          <meshStandardMaterial color="#1B5E20" roughness={1} />
        </mesh>
        {/* Techo macizo (y >= 2.4, z de -1.2 a 0) */}
        <mesh position={[0, 7.2, -0.6]}>
          <boxGeometry args={[40, 9.6, 1.2]} />
          <meshStandardMaterial color="#1B5E20" roughness={1} />
        </mesh>

        {/* Rocas pequeñas y densas decorando el frente: una malla y un material por capa de color */}
        <Instances limit={capas.capa1.length} range={capas.capa1.length}>
          <dodecahedronGeometry args={[1]} />
          <meshStandardMaterial color="#43A047" roughness={0.9} flatShading />
          {capas.capa1.map((r, i) => (
            <Instance key={i} position={r.posicion} rotation={r.rotacion} scale={r.escala} />
          ))}
        </Instances>
        <Instances limit={capas.capa2.length} range={capas.capa2.length}>
          <dodecahedronGeometry args={[1]} />
          <meshStandardMaterial color="#388E3C" roughness={0.9} flatShading />
          {capas.capa2.map((r, i) => (
            <Instance key={i} position={r.posicion} rotation={r.rotacion} scale={r.escala} />
          ))}
        </Instances>
        <Instances limit={capas.capa3.length} range={capas.capa3.length}>
          <dodecahedronGeometry args={[1]} />
          <meshStandardMaterial color="#2E7D32" roughness={0.9} flatShading />
          {capas.capa3.map((r, i) => (
            <Instance key={i} position={r.posicion} rotation={r.rotacion} scale={r.escala} />
          ))}
        </Instances>
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

      <group ref={convoyARef}>
        <ConvoyContenido />
      </group>
      <group ref={convoyBRef}>
        <ConvoyContenido colorOffset={3} />
      </group>
    </group>
  );
}

/* ═══════ Paso 04: Descarga y Ruta ═══════ */

const P04_X_PLATAFORMA = 1.4;
const P04_Y_PLATAFORMA = 0.36;
const P04_X_RAMPA_FIN = 3.95;
const P04_Y_SUELO = 0.21;
const P04_X_FIN = 6.5;
const P04_TRAMOS = [2.2, 1.1, 2.3, 1.4]; // entrada (aparece y baja la rampa), pausa al bajar de la plataforma, salida acelerando, reinicio (oculto)

function Step04Scene() {
  const truckRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    if (!truckRef.current) return;
    const { fase, p } = fasear(clock.getElapsedTime(), P04_TRAMOS);
    let x = P04_X_PLATAFORMA;
    let y = P04_Y_PLATAFORMA;
    let escala = 1;

    if (fase === 0) {
      const sp = suave(p);
      x = P04_X_PLATAFORMA + sp * (P04_X_RAMPA_FIN - P04_X_PLATAFORMA);
      y = P04_Y_PLATAFORMA;
      if (x >= 2.15 && x <= P04_X_RAMPA_FIN) {
        const ratio = (x - 2.15) / (P04_X_RAMPA_FIN - 2.15);
        y = P04_Y_PLATAFORMA - ratio * (P04_Y_PLATAFORMA - P04_Y_SUELO);
      } else if (x > P04_X_RAMPA_FIN) {
        y = P04_Y_SUELO;
      }
      escala = aparece(p, P04_TRAMOS[0]);
    } else if (fase === 1) {
      // Pausa justo al bajar de la plataforma, antes de tomar la vía.
      x = P04_X_RAMPA_FIN;
      y = P04_Y_SUELO;
    } else if (fase === 2) {
      const sp = p * p; // acelera al alejarse, como el resto de la ruta
      x = P04_X_RAMPA_FIN + sp * (P04_X_FIN - P04_X_RAMPA_FIN);
      y = P04_Y_SUELO;
      escala = desaparece(p, P04_TRAMOS[2]);
    } else {
      x = P04_X_PLATAFORMA;
      y = P04_Y_PLATAFORMA;
      escala = 0;
    }

    truckRef.current.position.set(x, y, 0);
    const s = 1.3 * Math.max(escala, ESCALA_MIN);
    truckRef.current.scale.set(s, s, s);
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

      <group ref={truckRef} position={[P04_X_PLATAFORMA, 0.36, 0]} scale={1.3}>
        <Truck bodyColor={TRUCK_COLORS[0].body} cabColor={TRUCK_COLORS[0].cab} />
        <Humo position={[0.18, 0.28, 0.14]} particulas={3} opacidadMax={0.8} />
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

const CAMARAS: Record<PasoAutopista, { pos: [number, number, number]; fov: number; target: [number, number, number]; noFog?: boolean }> = {
  '01': { pos: [8.3, 6.3, 8.3], fov: 35, target: [0, 0, 0] },
  '02': { pos: [7.3, 5.3, 7.3], fov: 35, target: [0, 0, 0] },
  '03': { pos: [0, 1.4, 12], fov: 34, target: [0, 1.4, 0], noFog: true },
  '04': { pos: [8.3, 5.3, 7.3], fov: 35, target: [1, 0, 0] },
};

/** Marca (una sola vez) que el lienzo ya pintó su primer cuadro. */
function MarcaPintado({ onPintado }: { onPintado: () => void }) {
  const hecho = useRef(false);
  useFrame(() => {
    if (!hecho.current) {
      hecho.current = true;
      onPintado();
    }
  });
  return null;
}

/**
 * Contenido de una tarjeta: <Canvas> propio con cámara, luces y niebla. Sin
 * OrbitControls: las cámaras son fijas, apuntadas con `lookAt` en vez de con
 * controles de órbita.
 *
 * `frameloop` es 'always' mientras la tarjeta está en pantalla (`enPantalla`) o
 * mientras no se ha pintado ningún cuadro todavía; solo pasa a 'never' una vez
 * pintado al menos un cuadro y fuera de pantalla — 'never' no hace render inicial,
 * así que usarlo antes de pintar dejaría la tarjeta en blanco.
 */
export default function AutopistaEscena({ paso, enPantalla }: { paso: PasoAutopista; enPantalla: boolean }) {
  const c = CAMARAS[paso];
  const [pintado, setPintado] = useState(false);
  const frameloop = enPantalla || !pintado ? 'always' : 'never';

  return (
    <div className="h-full w-full bg-sky-50">
      <Canvas dpr={[1, 1.5]} frameloop={frameloop}>
        <PerspectiveCamera
          makeDefault
          position={c.pos}
          fov={c.fov}
          onUpdate={(cam) => cam.lookAt(c.target[0], c.target[1], c.target[2])}
        />
        <color attach="background" args={['#f0f9ff']} />
        {!c.noFog && <fog attach="fog" args={['#E8EEF2', 15, 35]} />}

        <ambientLight intensity={0.4} />
        <directionalLight position={[5, 10, 5]} intensity={1.4} />
        <directionalLight position={[-3, 5, -3]} intensity={0.3} color="#B0C4DE" />
        <hemisphereLight args={['#DCEBF5', '#4A5D3A', 0.55]} />

        {paso === '01' && <Step01Scene />}
        {paso === '02' && <Step02Scene />}
        {paso === '03' && <Step03Scene />}
        {paso === '04' && <Step04Scene />}

        {!pintado && <MarcaPintado onPintado={() => setPintado(true)} />}
      </Canvas>
    </div>
  );
}
