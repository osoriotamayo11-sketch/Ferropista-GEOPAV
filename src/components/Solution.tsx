'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Layers, Zap, ShieldCheck, ArrowRight } from 'lucide-react';
import { TRAZADO, OPERACION, ACTUAL, AMBIENTAL } from '@/data/proyecto';
import PasoAutopista3D from './PasoAutopista3D';

/* ---------------------------------------------------------------------------
 * Esquemas del proceso operativo.
 *
 * Son PICTOGRAMAS propios, dibujados en SVG: representan la operacion descrita
 * por la ponencia, no miden nada. No llevan cifra alguna para que nadie los lea
 * como dato; los numeros van en el texto de cada paso, con su diapositiva.
 * Se dibujan en linea y no pesan: no hay imagenes externas que se rompan.
 * ------------------------------------------------------------------------- */

const UNI = '#193F77';
const UNI_CLARO = '#8aa7d1';
const VERDE = '#0F7B55';
const GRIS = '#94a3b8';
const GRIS_SUAVE = '#e2e8f0';

function Tractomula({ x, y, escala = 1, color = UNI }: { x: number; y: number; escala?: number; color?: string }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${escala})`}>
      <rect x="0" y="-9" width="26" height="9" rx="1.5" fill={color} opacity="0.85" />
      <path d="M27 -9 h6 l3 5 v4 h-9 z" fill={color} />
      <circle cx="7" cy="1" r="2.2" fill="#0f172a" />
      <circle cx="19" cy="1" r="2.2" fill="#0f172a" />
      <circle cx="32" cy="1" r="2.2" fill="#0f172a" />
    </g>
  );
}

function EsquemaPaso({ paso }: { paso: '01' | '02' | '03' | '04' }) {
  const comun = {
    viewBox: '0 0 170 96',
    className: 'h-full w-full',
    role: 'img' as const,
  };

  if (paso === '01') {
    return (
      <svg {...comun} aria-label="Estación terminal intermodal con vehículos de carga en el patio de acceso">
        <rect x="0" y="0" width="170" height="96" rx="10" fill="#f8fafc" />
        <path d="M18 52 L50 34 L82 52 V80 H18 Z" fill={UNI} opacity="0.12" />
        <path d="M18 52 L50 34 L82 52" fill="none" stroke={UNI} strokeWidth="2.2" strokeLinejoin="round" />
        <rect x="18" y="52" width="64" height="28" fill="none" stroke={UNI} strokeWidth="2.2" />
        <rect x="30" y="62" width="13" height="18" fill={UNI} opacity="0.32" />
        <rect x="57" y="62" width="13" height="18" fill={UNI} opacity="0.32" />
        <line x1="4" y1="80" x2="166" y2="80" stroke={GRIS} strokeWidth="2" />
        <line x1="90" y1="87" x2="162" y2="87" stroke={GRIS_SUAVE} strokeWidth="3" strokeDasharray="7 6" />
        <Tractomula x={92} y={80} escala={0.8} color={UNI} />
        <Tractomula x={128} y={80} escala={0.8} color={UNI_CLARO} />
        <line x1="99" y1="62" x2="99" y2="46" stroke={GRIS} strokeWidth="1.8" />
        <rect x="86" y="36" width="26" height="10" rx="2.5" fill={VERDE} />
        <line x1="90" y1="41" x2="108" y2="41" stroke="#ffffff" strokeWidth="1.6" strokeLinecap="round" opacity="0.85" />
      </svg>
    );
  }

  if (paso === '02') {
    return (
      <svg {...comun} aria-label="Peaje y embarque: la tractomula sube por la rampa a la plataforma ferroviaria">
        <rect x="0" y="0" width="170" height="96" rx="10" fill="#f8fafc" />
        <line x1="4" y1="86" x2="70" y2="86" stroke={GRIS} strokeWidth="2" />
        <rect x="12" y="54" width="22" height="32" fill={UNI} opacity="0.14" stroke={UNI} strokeWidth="1.8" />
        <path d="M8 54 h30 l-4 -7 h-22 z" fill={UNI} />
        <rect x="17" y="60" width="12" height="9" rx="1" fill="#ffffff" stroke={UNI} strokeWidth="1.2" />
        <circle cx="35" cy="70" r="2" fill="#b3261e" />
        <line x1="35" y1="70" x2="62" y2="70" stroke="#b3261e" strokeWidth="3" strokeLinecap="round" />
        <line x1="41" y1="70" x2="41" y2="76" stroke="#b3261e" strokeWidth="1.4" opacity="0.5" />
        <line x1="53" y1="70" x2="53" y2="76" stroke="#b3261e" strokeWidth="1.4" opacity="0.5" />
        <path d="M62 86 L100 70" stroke={GRIS} strokeWidth="3.5" strokeLinecap="round" />
        <line x1="96" y1="82" x2="166" y2="82" stroke={GRIS} strokeWidth="2.4" />
        <line x1="96" y1="87" x2="166" y2="87" stroke={GRIS_SUAVE} strokeWidth="2" />
        <rect x="100" y="70" width="60" height="8" rx="1.5" fill={UNI} opacity="0.28" stroke={UNI} strokeWidth="1.6" />
        <circle cx="110" cy="80" r="3" fill="#0f172a" />
        <circle cx="124" cy="80" r="3" fill="#0f172a" />
        <circle cx="138" cy="80" r="3" fill="#0f172a" />
        <circle cx="152" cy="80" r="3" fill="#0f172a" />
        <g transform="translate(66 84) rotate(-23)">
          <Tractomula x={0} y={0} escala={0.72} color={UNI} />
        </g>
        <path d="M74 46 q22 -12 44 0" fill="none" stroke={VERDE} strokeWidth="2.2" strokeLinecap="round" />
        <path d="M112 42 l8 5 -8 5 z" fill={VERDE} />
      </svg>
    );
  }

  if (paso === '03') {
    return (
      <svg {...comun} aria-label="Convoy eléctrico atravesando el túnel de base bajo la cordillera">
        <rect x="0" y="0" width="170" height="96" rx="10" fill="#f8fafc" />
        <path d="M8 72 L44 26 L74 54 L104 18 L152 72 Z" fill={VERDE} opacity="0.13" />
        <path d="M8 72 L44 26 L74 54 L104 18 L152 72" fill="none" stroke={VERDE} strokeWidth="2" strokeLinejoin="round" />
        <path d="M120 40 h22" stroke={VERDE} strokeWidth="2" strokeLinecap="round" />
        <path d="M140 36 l8 4 -8 4 z" fill={VERDE} />
        <rect x="6" y="66" width="158" height="20" rx="10" fill="#ffffff" stroke={UNI} strokeWidth="2" />
        <line x1="14" y1="70" x2="156" y2="70" stroke={UNI_CLARO} strokeWidth="1.2" strokeDasharray="4 4" />
        <rect x="22" y="74" width="22" height="8" rx="2" fill={UNI} />
        <rect x="48" y="75" width="26" height="7" rx="1.5" fill={UNI} opacity="0.4" />
        <rect x="78" y="75" width="26" height="7" rx="1.5" fill={UNI} opacity="0.4" />
        <rect x="108" y="75" width="26" height="7" rx="1.5" fill={UNI} opacity="0.4" />
        <line x1="12" y1="84" x2="158" y2="84" stroke={GRIS} strokeWidth="1.6" />
      </svg>
    );
  }

  return (
    <svg {...comun} aria-label="Descarga en el portal opuesto y continuación del viaje por carretera">
      <rect x="0" y="0" width="170" height="96" rx="10" fill="#f8fafc" />
      <rect x="10" y="52" width="56" height="8" rx="1.5" fill={UNI} opacity="0.28" stroke={UNI} strokeWidth="1.6" />
      <circle cx="20" cy="62" r="3" fill="#0f172a" />
      <circle cx="36" cy="62" r="3" fill="#0f172a" />
      <circle cx="52" cy="62" r="3" fill="#0f172a" />
      <line x1="6" y1="68" x2="72" y2="68" stroke={GRIS} strokeWidth="2.2" />
      <path d="M66 56 L100 82" stroke={GRIS} strokeWidth="3.5" strokeLinecap="round" />
      <line x1="96" y1="86" x2="166" y2="86" stroke={GRIS} strokeWidth="2.4" />
      <line x1="100" y1="91" x2="162" y2="91" stroke={GRIS_SUAVE} strokeWidth="3" strokeDasharray="8 6" />
      <Tractomula x={112} y={86} escala={0.85} color={VERDE} />
      <path d="M112 40 h34" stroke={VERDE} strokeWidth="2.2" strokeLinecap="round" />
      <path d="M144 36 l8 4 -8 4 z" fill={VERDE} />
      <text x="112" y="32" fontSize="10" fill={VERDE} fontFamily="monospace">ruta</text>
    </svg>
  );
}

export const Solution: React.FC = () => {
  const steps = [
    {
      number: '01' as const,
      title: 'Estación Terminal Intermodal (Ibagué / Armenia)',
      description:
        'Los vehículos de carga ingresan a una de las dos grandes estaciones logísticas previstas en los portales del túnel. [Ponencia, dia. 20]',
    },
    {
      number: '02' as const,
      title: 'Peaje y Embarque Ro-Ro (Roll-on Roll-off)',
      description:
        `Las tractomulas suben a plataformas ferroviarias. La fuente asigna ${OPERACION.tPeajeCarga.valor} al conjunto de peaje y carga. [Ponencia, dia. 23]`,
    },
    {
      number: '03' as const,
      title: 'Tránsito Eléctrico Subterráneo',
      description:
        `Convoyes de ${OPERACION.longitudTren.valor} con locomotora, vagón para conductores y ${OPERACION.tractomulasTren.valor}. El desplazamiento toma ${OPERACION.tDesplazamiento.valor}, lo que implica una velocidad comercial de ${OPERACION.velComercial.valor} sobre los 44 km de túnel principal [cálculo propio]. [Ponencia, dia. 20 y 23]`,
    },
    {
      number: '04' as const,
      title: 'Descarga y Continuación de Ruta',
      description:
        `La descarga toma ${OPERACION.tDescarga.valor}. El ciclo completo suma ${OPERACION.tCicloTotal.valor}, frente a las ${ACTUAL.tiempoCruce.valor} del paso actual. Nótese que solo 30 de esos 70 minutos son desplazamiento: los otros 40 son operación en terminal. [Ponencia, dia. 23 y 29]`,
    },
  ];

  const cards = [
    {
      icon: Layers,
      iconColor: 'text-uni-600',
      bgColor: 'bg-blue-600/10',
      borderColor: 'border-blue-500/30',
      hoverBorder: 'hover:border-blue-500/50',
      title: 'Túnel de Base: 58 km de Trazado',
      description:
        `Túnel de base de montaña que evita el ascenso a los ${TRAZADO.cotaPasoActual.valor} del Alto de La Línea. La construcción se plantea en ${TRAZADO.configuracion.valor}, con excavación mixta entre tuneladora y método convencional. [Ponencia, dia. 20 y 22]`,
      bullets: [
        `Longitud total ${TRAZADO.longitudTotal.valor}; túnel principal ${TRAZADO.tunelPrincipal.valor}`,
        `Pendiente media ${TRAZADO.pendienteMedia.valor} [cálculo propio del semillero]`,
        `Portales: ${TRAZADO.cotaIbague.valor} en Ibagué y ${TRAZADO.cotaArmenia.valor} en Armenia`,
      ],
      bulletDot: 'bg-blue-400',
    },
    {
      icon: Zap,
      iconColor: 'text-gmae-600',
      bgColor: 'bg-emerald-600/10',
      borderColor: 'border-emerald-500/30',
      hoverBorder: 'hover:border-emerald-500/50',
      title: 'Tracción Eléctrica',
      description:
        `El cambio modal a tracción eléctrica permite reducir en un ${AMBIENTAL.reduccionGEI.valor} las emisiones de gases de efecto invernadero y los consumos energéticos del cruce. No es cero: la huella real depende de la matriz de generación eléctrica del país. [Ponencia, dia. 25]`,
      bullets: [
        `${AMBIENTAL.geiEvitados.valor} de emisiones evitadas a 50 años`,
        `${AMBIENTAL.combustible.valor} de combustible ahorrados en 2030`,
        'Huella de carbono de la construcción: no reportada por la fuente',
      ],
      bulletDot: 'bg-gmae-500',
    },
    {
      icon: ShieldCheck,
      iconColor: 'text-uni-500',
      bgColor: 'bg-sky-600/10',
      borderColor: 'border-sky-500/30',
      hoverBorder: 'hover:border-sky-500/50',
      title: 'Operación Protegida del Clima',
      description:
        `El trazado subterráneo sustrae el cruce de las condiciones de alta montaña. La fuente prevé una fase inicial de ${OPERACION.trenesDia.valor} y contempla ventilación longitudinal con pozos de extracción intermedios. [Ponencia, dia. 20]`,
      bullets: [
        `Capacidad ${OPERACION.capacidadDiaria.valor} [cálculo propio: 140 trenes × 35 tractomulas]`,
        `Cruce de convoyes en ${OPERACION.cruceConvoyes.valor.toLowerCase()}`,
        'Sistemas de seguridad y señalización: pendientes de diseño de detalle',
      ],
      bulletDot: 'bg-sky-400',
    },
  ];

  return (
    <section id="solucion" className="py-24 bg-slate-50 relative overflow-hidden transition-colors duration-300">
      {/* Radial Background Accent */}
      <div className="absolute top-0 right-1/4 w-[600px] h-[600px] bg-blue-600/10 blur-[130px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 left-1/4 w-[600px] h-[600px] bg-emerald-600/10 blur-[130px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header with Framer Motion */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="text-center max-w-3xl mx-auto space-y-4 mb-20"
        >
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-uni-600 text-xs font-semibold uppercase tracking-wider">
            <Zap className="w-3.5 h-3.5 text-uni-600" />
            <span>Propuesta de Solución Analizada</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-uni-900 tracking-tight">
            La Solución Intermodal de Baja Cota
          </h2>
          <p className="text-base sm:text-lg text-slate-600 leading-relaxed font-light">
            La propuesta analizada sustituye el ascenso a los {TRAZADO.cotaPasoActual.valor} del Alto de La Línea por <strong className="text-uni-900 font-medium">{TRAZADO.longitudTotal.valor} de trazado con un túnel principal de {TRAZADO.tunelPrincipal.valor}</strong>, entre portales a {TRAZADO.cotaIbague.valor} y {TRAZADO.cotaArmenia.valor}: un sistema ferroviario eléctrico que transporta los camiones entre Ibagué y Armenia. [Ponencia, dia. 20]
          </p>
        </motion.div>

        {/* Highlight Architecture Cards with Staggered Framer Motion Animation */}
        <div className="grid lg:grid-cols-3 gap-8 mb-20">
          {cards.map((card, index) => {
            const Icon = card.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.15 }}
                className={`rounded-2xl bg-gradient-to-b from-white to-slate-50 p-8 border border-slate-200 relative overflow-hidden group ${card.hoverBorder} transition-all duration-300`}
              >
                <div className={`w-14 h-14 rounded-2xl ${card.bgColor} ${card.borderColor} border flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                  <Icon className={`w-7 h-7 ${card.iconColor}`} />
                </div>
                <h3 className="text-2xl font-bold text-uni-900 mb-3">{card.title}</h3>
                <p className="text-slate-600 text-sm leading-relaxed mb-6 font-light">
                  {card.description}
                </p>
                <ul className="space-y-2.5 text-xs text-slate-600 font-mono">
                  {card.bullets.map((bullet, idx) => (
                    <li key={idx} className="flex items-center gap-2">
                      <span className={`w-1.5 h-1.5 rounded-full ${card.bulletDot}`}></span>
                      <span>{bullet}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            );
          })}
        </div>

        {/* How It Works: Step by Step Workflow with Framer Motion */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="rounded-3xl bg-white border border-slate-200 p-8 sm:p-12"
        >
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 pb-6 border-b border-slate-200">
            <div>
              <span className="text-xs font-mono font-semibold text-gmae-600 tracking-wider uppercase">Proceso Operativo</span>
              <h3 className="text-2xl sm:text-3xl font-bold text-uni-900 mt-1">¿Cómo funciona la autopista rodante?</h3>
            </div>
            <p className="text-sm text-slate-500 max-w-md mt-4 md:mt-0">
              El camión completo sube a una plataforma ferroviaria y el conductor viaja en un vagón aparte. La fuente llama al sistema «autopista rodante». [Ponencia, dia. 19 y 23]
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 relative">
            {steps.map((step, idx) => (
              <div key={idx} className="relative space-y-3">
                {/* Esquema del paso. Ilustrativo, sin escala ni cifras. */}
                <div className="relative overflow-hidden rounded-xl border border-slate-200 bg-slate-50">
                  <PasoAutopista3D paso={step.number} respaldo={<EsquemaPaso paso={step.number} />} />
                  <span className="absolute left-3 top-2 font-mono text-2xl font-black text-uni-900/70">
                    {step.number}
                  </span>
                </div>
                <h4 className="text-base font-bold leading-snug text-uni-900">{step.title}</h4>
                <p className="text-xs font-light leading-relaxed text-slate-500">{step.description}</p>
                {idx < steps.length - 1 && (
                  <div className="absolute top-12 right-0 hidden translate-x-1/2 text-slate-300 lg:block">
                    <ArrowRight className="h-5 w-5" />
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Tiempos de operación [F, dia. 23] frente al paso actual [F, dia. 29] */}
          <div className="mt-10 space-y-3">
            <div className="flex items-baseline justify-between gap-4">
              <span className="text-xs font-mono font-semibold uppercase tracking-wider text-gmae-600">Tiempos de operación</span>
              <span className="text-xs text-slate-500">[Ponencia, dia. 23]</span>
            </div>
            <div className="flex h-12 w-full overflow-hidden rounded-lg text-[11px] font-semibold text-white sm:text-xs">
              {[
                { t: 'Peaje y carga', v: OPERACION.tPeajeCarga, c: 'bg-gmae-600' },
                { t: 'Desplazamiento', v: OPERACION.tDesplazamiento, c: 'bg-uni-700' },
                { t: 'Descarga', v: OPERACION.tDescarga, c: 'bg-amber-600' },
              ].map((f) => (
                <div key={f.t} className={`flex flex-col items-center justify-center px-1 text-center ${f.c}`}
                     style={{ width: `${(f.v.n / OPERACION.tCicloTotal.n) * 100}%` }}>
                  <span className="leading-tight">{f.t}</span>
                  <span className="font-mono">{f.v.valor}</span>
                </div>
              ))}
            </div>
            <p className="text-xs leading-relaxed text-slate-600">
              Total <strong className="text-uni-900">{OPERACION.tCicloTotal.valor}</strong> por cruce, frente a
              {' '}<strong className="text-uni-900">{ACTUAL.tiempoCruce.valor}</strong> del paso actual como valor medio
              [Ponencia, dia. 29]. Solo {OPERACION.tDesplazamiento.valor} son desplazamiento: el resto es operación
              en terminal. Las cifras son del proponente, no auditadas.
            </p>
          </div>

          <p className="mt-8 border-t border-slate-200 pt-4 font-mono text-[11px] leading-relaxed text-slate-500">
            Los cuatro esquemas son escenas 3D ilustrativas, sin escala ni medida, adaptadas por el
            semillero de un boceto propio: ilustran la secuencia operativa que describe la ponencia.
            El convoy real mide {OPERACION.longitudTren.valor} y lleva {OPERACION.tractomulasTren.valor}; aquí
            se dibujan unas pocas plataformas. Los valores van en el texto de cada paso y en la
            barra de tiempos, con su diapositiva de origen.
          </p>
        </motion.div>

      </div>
    </section>
  );
};
