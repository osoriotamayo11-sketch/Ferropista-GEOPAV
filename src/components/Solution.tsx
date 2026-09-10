'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Layers, Zap, ShieldCheck, ArrowRight } from 'lucide-react';
import { TRAZADO, OPERACION, ACTUAL, AMBIENTAL } from '@/data/proyecto';

export const Solution: React.FC = () => {
  const steps = [
    {
      number: '01',
      title: 'Estación Terminal Intermodal (Ibagué / Armenia)',
      description:
        'Los vehículos de carga ingresan a una de las dos grandes estaciones logísticas previstas en los portales del túnel. [Ponencia, dia. 20]',
    },
    {
      number: '02',
      title: 'Peaje y Embarque Ro-Ro (Roll-on Roll-off)',
      description:
        `Las tractomulas suben a plataformas ferroviarias. La fuente asigna ${OPERACION.tPeajeCarga.valor} al conjunto de peaje y carga. [Ponencia, dia. 23]`,
    },
    {
      number: '03',
      title: 'Tránsito Eléctrico Subterráneo',
      description:
        `Convoyes de ${OPERACION.longitudTren.valor} con locomotora, vagón para conductores y ${OPERACION.tractomulasTren.valor}. El desplazamiento toma ${OPERACION.tDesplazamiento.valor}, lo que implica una velocidad comercial de ${OPERACION.velComercial.valor} sobre los 44 km de túnel principal [cálculo propio]. [Ponencia, dia. 20 y 23]`,
    },
    {
      number: '04',
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
      title: 'Túnel de Base de 58 km',
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
            Sustituimos el ascenso de 3,300 msnm por un <strong className="text-uni-900 font-medium">túnel de base de 58 km</strong> a baja altura (~1,250 msnm). Un sistema ferroviario eléctrico continuo que transfiere vehículos pesados entre Ibagué y Armenia.
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
              <h3 className="text-2xl sm:text-3xl font-bold text-uni-900 mt-1">¿Cómo funciona el Sistema Intermodal Piggyback?</h3>
            </div>
            <p className="text-sm text-slate-500 max-w-md mt-4 md:mt-0">
              Integración fluida de la flota vehicular pesada nacional al sistema ferroviario de alta capacidad.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 relative">
            {steps.map((step, idx) => (
              <div key={idx} className="relative space-y-3">
                <div className="text-4xl font-black text-slate-800 font-mono">{step.number}</div>
                <h4 className="text-base font-bold text-uni-900 leading-snug">{step.title}</h4>
                <p className="text-xs text-slate-500 leading-relaxed font-light">{step.description}</p>
                {idx < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-6 right-0 translate-x-1/2 text-slate-700">
                    <ArrowRight className="w-5 h-5" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </motion.div>

      </div>
    </section>
  );
};
