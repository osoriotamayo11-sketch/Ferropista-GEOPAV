'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { Header } from '@/components/Header';
import { Hero } from '@/components/Hero';
import { Problematic } from '@/components/Problematic';
import { PlanDeAccion } from '@/components/PlanDeAccion';
import { SintesisOE1 } from '@/components/SintesisOE1';
import { SintesisOE2 } from '@/components/SintesisOE2';
import { SintesisOE5 } from '@/components/SintesisOE5';
import { Solution } from '@/components/Solution';
import { ImpactsGrid } from '@/components/ImpactsGrid';
import { Dashboard } from '@/components/Dashboard';
import { TechnicalSpecsModal } from '@/components/TechnicalSpecsModal';
import { Footer } from '@/components/Footer';

/* El visor del trazado monta un lienzo WebGL, asi que se carga en el cliente. */
const ProjectMap = dynamic(
  () => import('@/components/ProjectMap').then((mod) => mod.ProjectMap),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-[550px] bg-slate-50 rounded-3xl border border-slate-200 flex items-center justify-center">
        <div className="text-slate-500 font-mono text-sm animate-pulse">
          Cargando el relieve del corredor…
        </div>
      </div>
    ),
  }
);

export default function Home() {
  const [isSpecsOpen, setIsSpecsOpen] = useState(false);

  return (
    <main className="min-h-screen bg-slate-50 text-slate-800 font-sans selection:bg-uni-700 selection:text-white">
      <Header onOpenSpecs={() => setIsSpecsOpen(true)} />

      <Hero />

      {/* Problemática */}
      <Problematic />

      {/* Solución intermodal */}
      <Solution />

      {/* Grid de impactos */}
      <ImpactsGrid />

      {/* Dashboard de eficiencia operativa */}
      <Dashboard />

      {/* Trazado del túnel sobre el relieve del DEM — OE 1 */}
      <ProjectMap />

      {/* Plan de Acción del Semestre Paz y Región 2026B */}
      <PlanDeAccion />

      {/* Síntesis, láminas y evidencias del OE 1 (objetivo cerrado) */}
      <SintesisOE1 />

      {/* Consulta ciudadana del OE 2 (objetivo en curso, con la consulta abierta) */}
      <SintesisOE2 />

      {/* Síntesis y tasa de siniestralidad del OE 5 (objetivo cerrado) */}
      <SintesisOE5 />

      {/* Modal de detalles técnicos, abierto desde el encabezado y el pie */}
      <TechnicalSpecsModal
        isOpen={isSpecsOpen}
        onClose={() => setIsSpecsOpen(false)}
      />

      <Footer onOpenSpecs={() => setIsSpecsOpen(true)} />
    </main>
  );
}
