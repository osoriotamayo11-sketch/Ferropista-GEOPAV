'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import { ArrowRight, Menu, X } from 'lucide-react';

interface HeaderProps {
  onOpenSpecs: () => void;
}

/* `corto` es la etiqueta de la barra de escritorio; `texto` la del menu desplegable.
   La barra tiene ancho limitado: con nueve etiquetas largas se desborda. */
const ENLACES = [
  { href: '#problematica', texto: 'Problemática',       corto: 'Problemática' },
  { href: '#solucion',     texto: 'Solución Intermodal', corto: 'Solución' },
  { href: '#impactos',     texto: 'Impactos',            corto: 'Impactos' },
  { href: '#dashboard',    texto: 'Dashboard',           corto: 'Dashboard' },
  { href: '#mapa',         texto: 'Mapa',                corto: 'Mapa' },
  { href: '#plan',         texto: 'Plan de Acción',      corto: 'Plan' },
  { href: '#oe1',          texto: 'Síntesis OE 1',       corto: 'OE 1' },
  { href: '#oe2',          texto: 'Síntesis OE 2',       corto: 'OE 2' },
  { href: '#oe5',          texto: 'Síntesis OE 5',       corto: 'OE 5' },
];

export const Header: React.FC<HeaderProps> = ({ onOpenSpecs }) => {
  const [menuAbierto, setMenuAbierto] = useState(false);

  return (
    <header className="sticky top-0 z-40 w-full bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-[0_1px_0_0_rgba(25,63,119,0.06)]">
      {/* Franja institucional superior */}
      <div className="h-1 w-full bg-gradient-to-r from-uni-700 via-uni-500 to-gmae-600" />
      <div className="hidden sm:block bg-uni-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-8 flex items-center justify-between text-[11px] tracking-wide">
          <span className="font-semibold uppercase">Semillero de Investigación GEOPAV · Ingeniería Civil</span>
          <span className="font-mono text-uni-100">Semestre Paz y Región 2026B</span>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-[68px] gap-4">

          {/* Identidad institucional */}
          <a href="#" className="flex items-center gap-4 min-w-0 group">
            <Image
              src="/logo-unibague.png"
              alt="Universidad de Ibagué"
              width={669}
              height={179}
              priority
              className="h-9 sm:h-10 w-auto shrink-0"
            />

            {/* Logo del semillero: la Universidad es la institucion, GEOPAV el
                autor del analisis. Van juntos y separados por un filete. */}
            <span className="hidden h-8 w-px shrink-0 bg-slate-200 sm:block" />
            <Image
              src="/logo-geopav.png"
              alt="Semillero de Investigación GEOPAV"
              width={256}
              height={256}
              priority
              className="hidden h-9 w-auto shrink-0 sm:block"
            />
          </a>

          {/* Navegación de escritorio */}
          <nav className="hidden xl:flex items-center gap-4 text-[13px] font-medium shrink min-w-0">
            {ENLACES.map((e) => (
              <a
                key={e.href}
                href={e.href}
                className="text-slate-600 hover:text-uni-700 transition-colors whitespace-nowrap"
              >
                {e.corto}
              </a>
            ))}
          </nav>

          {/* Acciones */}
          <div className="hidden xl:flex items-center gap-3 shrink-0">
            <button
              onClick={onOpenSpecs}
              className="inline-flex items-center justify-center px-5 py-2.5 text-xs font-semibold rounded-lg bg-uni-700 hover:bg-uni-800 text-white shadow-sm transition-colors active:scale-95"
            >
              <span>Ver ficha técnica</span>
              <ArrowRight className="w-3.5 h-3.5 ml-2" />
            </button>
          </div>

          {/* Disparador móvil */}
          <div className="flex items-center xl:hidden">
            <button
              onClick={() => setMenuAbierto(!menuAbierto)}
              aria-label="Abrir menú"
              className="p-2 rounded-lg bg-slate-100 text-slate-600 hover:text-uni-700 border border-slate-200"
            >
              {menuAbierto ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>

        </div>
      </div>

      {/* Menú móvil */}
      {menuAbierto && (
        <div className="xl:hidden bg-white border-b border-slate-200 px-4 pt-2 pb-6 space-y-1">
          {ENLACES.map((e) => (
            <a
              key={e.href}
              href={e.href}
              onClick={() => setMenuAbierto(false)}
              className="block px-3 py-2.5 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100 hover:text-uni-700"
            >
              {e.texto}
            </a>
          ))}
          <div className="pt-3">
            <button
              onClick={() => { setMenuAbierto(false); onOpenSpecs(); }}
              className="w-full py-3 px-4 rounded-lg bg-uni-700 hover:bg-uni-800 text-white font-semibold text-sm flex items-center justify-center gap-2 shadow-sm"
            >
              <span>Ver ficha técnica</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </header>
  );
};
