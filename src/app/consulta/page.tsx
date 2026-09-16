import React from 'react';
import type { Metadata } from 'next';
import { ConsultaCiudadana } from '@/components/ConsultaCiudadana';

export const metadata: Metadata = {
  title: 'Consulta ciudadana · Percepción de riesgo vial | Semillero GEOPAV',
  description:
    'Consulta ciudadana del Semillero GEOPAV sobre percepción de riesgo vial en el paso del Alto de La Línea, corredor Ibagué – Armenia. Objetivo específico 2, Paz y Región 2026B.',
  /* Indexable desde que la consulta está abierta: el OE 2 la difunde por canales
     digitales y tiene que ser encontrable. */
  robots: { index: true, follow: true },
};

export default function ConsultaPage() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-800 font-sans">
      <ConsultaCiudadana />
      <footer className="border-t border-slate-200 py-8">
        <p className="max-w-3xl mx-auto px-4 sm:px-6 text-xs text-slate-500 leading-relaxed">
          Semillero de Investigación GEOPAV · Ingeniería Civil · Universidad de Ibagué ·
          Semestre Paz y Región 2026B. El semillero analiza la iniciativa Ferropista de
          forma independiente: no la representa ni la promueve.{' '}
          <a href="/" className="text-uni-700 font-semibold hover:underline">
            Volver al sitio
          </a>
        </p>
      </footer>
    </main>
  );
}
