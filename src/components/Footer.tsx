'use client';

import React from 'react';
import Image from 'next/image';
import { GraduationCap, Mail, MapPin, BookOpen, ArrowRight, ExternalLink } from 'lucide-react';

interface FooterProps {
  onOpenSpecs: () => void;
}

export const Footer: React.FC<FooterProps> = ({ onOpenSpecs }) => {
  return (
    <footer className="bg-uni-700 border-t border-uni-500/60 text-uni-200 text-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10">
          
          {/* Col 1 & 2: Institutional Identity */}
          <div className="lg:col-span-2 space-y-4">
            <div className="rounded-xl bg-white px-4 py-3 inline-block">
              <Image
                src="/logo-unibague.png"
                alt="Universidad de Ibagué"
                width={669}
                height={179}
                className="h-9 w-auto"
              />
            </div>

            <div className="flex items-center gap-3">
              <Image
                src="/logo-geopav.png"
                alt="Semillero de Investigación GEOPAV"
                width={256}
                height={256}
                className="h-11 w-11 shrink-0 rounded-lg bg-white/95 p-1"
              />
              <div>
                <span className="text-base font-bold text-white tracking-tight block leading-tight">
                  Semillero de Investigación GEOPAV
                </span>
                <span className="text-[11px] text-uni-200 block">
                  Universidad de Ibagué · Programa de Ingeniería Civil
                </span>
              </div>
            </div>

            <p className="text-xs text-uni-200 leading-relaxed max-w-sm">
              Trabajo académico del Semestre Paz y Región 2026B. Evaluación técnica, socioeconómica y ambiental de la propuesta de túnel de base ferroviario Ferropista Cordillera Central en el tramo Ibagué – Armenia. Las cifras provienen de la ponencia de ARCS / UC Consult (2025) y están en verificación independiente por el semillero.
            </p>

            <div className="pt-2 flex items-center gap-3">
              <button
                onClick={onOpenSpecs}
                className="px-4 py-2 rounded-lg bg-uni-600 hover:bg-uni-700 text-white border border-uni-500/60 text-xs font-semibold flex items-center gap-2 transition-colors"
              >
                <span>Ficha Técnica del Análisis</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Col 3: Navigation */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-white uppercase tracking-wider">Secciones del Análisis</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <a href="#problematica" className="hover:text-white transition-colors">Diagnóstico del Corredor</a>
              </li>
              <li>
                <a href="#solucion" className="hover:text-white transition-colors">Solución Intermodal</a>
              </li>
              <li>
                <a href="#impactos" className="hover:text-white transition-colors">Evaluación de Impactos</a>
              </li>
              <li>
                <button onClick={onOpenSpecs} className="hover:text-white transition-colors text-left">
                  Parámetros Técnicos
                </button>
              </li>
            </ul>
          </div>

          {/* Col 4: Portal locations */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-white uppercase tracking-wider">Nodos del Corredor</h4>
            <ul className="space-y-2 text-xs">
              <li className="flex items-center gap-2">
                <MapPin className="w-3.5 h-3.5 text-uni-100" />
                <span>Portal oriental · extremo Ibagué · Ibagué, Tolima</span>
              </li>
              <li className="flex items-center gap-2">
                <MapPin className="w-3.5 h-3.5 text-uni-100" />
                <span>Portal occidental · extremo Armenia · Calarcá, Quindío</span>
              </li>
              <li className="flex items-center gap-2">
                <BookOpen className="w-3.5 h-3.5 text-uni-100" />
                <span>Eje Bogotá – Buenaventura</span>
              </li>
            </ul>
          </div>

          {/* Col 5: Academic identity */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-white uppercase tracking-wider">Responsable Académico</h4>
            <ul className="space-y-2 text-xs">
              <li className="flex items-center gap-2">
                <GraduationCap className="w-3.5 h-3.5 text-uni-100" />
                <span>Semillero de Investigación GEOPAV</span>
              </li>
              <li className="flex items-center gap-2">
                <Mail className="w-3.5 h-3.5 text-uni-100" />
                <span>Universidad de Ibagué</span>
              </li>
            </ul>
            <div className="pt-2 space-y-1">
              <span className="inline-block px-2.5 py-1 rounded bg-uni-600 border border-uni-500/60 text-[10px] text-uni-200">
                Semestre Paz y Región 2026B
              </span>
              <span className="inline-block px-2.5 py-1 rounded bg-uni-600 border border-uni-500/60 text-[10px] text-uni-200 ml-1">
                Programa de Ingeniería Civil
              </span>
            </div>
          </div>

        </div>

        {/* Bottom line */}
        <div className="mt-12 pt-8 border-t border-uni-500/60 flex flex-col sm:flex-row items-center justify-between text-xs text-uni-100 gap-4">
          <div>
            © {new Date().getFullYear()} Semillero de Investigación GEOPAV — Universidad de Ibagué. Trabajo académico.
          </div>
          <div className="flex gap-6">
            <a href="https://www.ferropista.com" target="_blank" rel="noopener noreferrer" className="hover:text-uni-100 transition-colors inline-flex items-center gap-1">
              Fuente: ferropista.com
              <ExternalLink className="w-3 h-3" />
            </a>
            <a href="#plan" className="hover:text-uni-100 transition-colors">Plan de Acción</a>
          </div>
        </div>

      </div>
    </footer>
  );
};
