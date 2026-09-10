'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { Header } from '@/components/Header';
import { Hero } from '@/components/Hero';
import { Problematic } from '@/components/Problematic';
import { PlanDeAccion } from '@/components/PlanDeAccion';
import { PerfilTunel } from '@/components/PerfilTunel';
import { SintesisOE1 } from '@/components/SintesisOE1';
import { SintesisOE5 } from '@/components/SintesisOE5';
import { Solution } from '@/components/Solution';
import { ImpactsGrid } from '@/components/ImpactsGrid';
import { Dashboard } from '@/components/Dashboard';
import { ContactForm } from '@/components/ContactForm';
import { DownloadSection } from '@/components/DownloadSection';
import { TechnicalSpecsModal } from '@/components/TechnicalSpecsModal';
import { Footer } from '@/components/Footer';

// Dynamic import for Leaflet map component with ssr disabled to prevent window undefined during SSR
const ProjectMap = dynamic(
  () => import('@/components/ProjectMap').then((mod) => mod.ProjectMap),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-[550px] bg-slate-50 rounded-3xl border border-slate-200 flex items-center justify-center">
        <div className="text-slate-500 font-mono text-sm animate-pulse">
          Cargando Mapa Interactivo del Trazado Subterráneo...
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

      <Hero onOpenSpecs={() => setIsSpecsOpen(true)} />

      {/* Problemática Section */}
      <Problematic />

      {/* Solución Intermodal Section (Framer Motion) */}
      <Solution />

      {/* Grid de 4 Impactos Section (Framer Motion) */}
      <ImpactsGrid />

      {/* Dashboard de Eficiencia Operativa (Framer Motion + Recharts) */}
      <Dashboard />

      {/* Mapa Interactivo del Trazado Subterráneo (React-Leaflet) */}
      <ProjectMap />

      {/* Perfil del túnel — resultado propio del OE 1 */}
      <PerfilTunel />

      {/* Síntesis, láminas y evidencias del OE 1 (objetivo cerrado) */}
      <SintesisOE1 />

      {/* Síntesis y tasa de siniestralidad del OE 5 (objetivo cerrado) */}
      <SintesisOE5 />

      {/* Plan de Acción del Semestre Paz y Región 2026B */}
      <PlanDeAccion />

      {/* Download Section (Framer Motion Banner CTA) */}
      <DownloadSection />

      {/* Formulario de Contacto Corporativo (Backend Integration + API Route) */}
      <ContactForm />

      {/* Modal de Detalles Técnicos */}
      <TechnicalSpecsModal
        isOpen={isSpecsOpen}
        onClose={() => setIsSpecsOpen(false)}
      />

      {/* Footer Component */}
      <Footer onOpenSpecs={() => setIsSpecsOpen(true)} />
    </main>
  );
}
