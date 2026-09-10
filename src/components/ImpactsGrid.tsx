'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { DollarSign, Users, Leaf, ShieldCheck, ArrowUpRight, X, CheckCircle2, Layers, Sparkles } from 'lucide-react';
import { ACTUAL, OPERACION, ECONOMICO, SOCIAL, AMBIENTAL, EXCAVACION, ESTRELLA_ANDINA } from '@/data/proyecto';

interface ImpactItem {
  id: string;
  category: string;
  title: string;
  badge: string;
  badgeStyle: string;
  borderHover: string;
  icon: React.ElementType;
  iconColor: string;
  iconBg: string;
  summary: string;
  points: string[];
  detailedSpecs: string[];
  imageUrl: string;
  imageAlt: string;
  highlightStat: string;
  highlightLabel: string;
}

export const ImpactsGrid: React.FC = () => {
  const [selectedImpact, setSelectedImpact] = useState<ImpactItem | null>(null);

  const impacts: ImpactItem[] = [
    {
      id: 'economico',
      category: 'Eficiencia & Mercado',
      title: 'Impacto Económico',
      badge: 'Competitividad País',
      badgeStyle: 'bg-uni-50 text-uni-700 border-uni-200',
      borderHover: 'hover:border-blue-500/60 hover:shadow-blue-500/10',
      icon: DollarSign,
      iconColor: 'text-uni-600',
      iconBg: 'bg-blue-500/10 border-blue-500/20',
      summary:
        'Reducción del tiempo y del costo de cruce en el tramo crítico del corredor Bogotá – Buenaventura. Cifras estimadas por el proponente de la iniciativa, pendientes de verificación independiente.',
      points: [
        `Ahorros de ${ECONOMICO.ahorroTransporte2030.valor} para el sector transporte en 2030. [Fuente, dia. 28]`,
        `Reducción del tiempo de cruce de ${ACTUAL.tiempoCruce.valor} a ${OPERACION.tCicloTotal.valor} de tiempo integrado. [Fuente, dia. 23 y 29]`,
        `Ahorro de ${ECONOMICO.horasAhorradas.valor} de viaje para los usuarios de la Ruta 40. [Fuente, dia. 28 y 29]`,
        `Multiplicación por 3 de la productividad del sector transporte en 2030. [Fuente, dia. 28]`,
      ],
      detailedSpecs: [
        `Recaudo fiscal de ${ECONOMICO.recaudoFiscal.valor} para todo Colombia a 50 años. ATENCIÓN: es recaudo del Estado, no ahorro del usuario. [Fuente, dia. 28]`,
        `Inducción de nuevos tráficos por ${ECONOMICO.nuevosTraficos.valor} a 50 años. [Fuente, dia. 28]`,
        `Incremento del PIB nacional de ${ECONOMICO.incrementoPIB.valor}. [Fuente, dia. 28]`,
        `Inversión estimada (CAPEX): ${ECONOMICO.capex.valor}. [Fuente, dia. 20]`,
        'Reducción porcentual del flete: NO reportada por la fuente. Debe calcularla el semillero en el objetivo específico 6.',
      ],
      imageUrl: 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=800&q=80',
      imageAlt: 'Logística de carga pesada e intermodalidad',
      highlightStat: ECONOMICO.ahorroTransporte2030.valor,
      highlightLabel: 'de ahorro para el sector transporte en 2030 (dia. 28)',
    },
    {
      id: 'social',
      category: 'Territorio & Desarrollo',
      title: 'Impacto Social',
      badge: 'Integración Regional',
      badgeStyle: 'bg-uni-50 text-uni-600 border-uni-200',
      borderHover: 'hover:border-sky-500/60 hover:shadow-sky-500/10',
      icon: Users,
      iconColor: 'text-uni-500',
      iconBg: 'bg-sky-500/10 border-sky-500/20',
      summary:
        'Integración regional del eje Ibagué – Cajamarca – Armenia. La fuente define tres anillos de población beneficiada, pero no cuantifica el empleo atribuible a la Ferropista.',
      points: [
        `${SOCIAL.poblacionEje.valor} de habitantes en el eje Ibagué – Cajamarca – Armenia: ciudad, empleo y crecimiento. [Fuente, dia. 27]`,
        `${SOCIAL.poblacionDptos.valor} en Quindío, Tolima, Risaralda y Caldas: accesibilidad, innovación e integración. [Fuente, dia. 27]`,
        `${SOCIAL.poblacionRegion.valor} en la Región Central: competitividad, equidad y liderazgo. [Fuente, dia. 27]`,
        'Objetivos declarados: integración regional, progreso de la población, equidad y seguridad, y oportunidades de formación y producción. [Fuente, dia. 27]',
      ],
      detailedSpecs: [
        'La ponencia NO cuantifica el empleo atribuible a la Ferropista. Este vacío se declara en lugar de llenarse con una estimación.',
        `Las cifras de ${ESTRELLA_ANDINA.empleoObra.valor} en construcción y ${ESTRELLA_ANDINA.empleoOyM.valor} en operación pertenecen al proyecto Estrella Andina de ${ESTRELLA_ANDINA.longitud.valor}, no al túnel de 58 km. [Fuente, dia. 32]`,
        'Atribuir esas cifras a la Ferropista infla el proyecto en un orden de magnitud.',
        'La percepción de la comunidad del corredor es dato primario que este semillero recoge mediante consulta ciudadana (objetivo específico 2).',
      ],
      imageUrl: 'https://images.unsplash.com/photo-1541888946425-d0fbb186a5b7?auto=format&fit=crop&w=800&q=80',
      imageAlt: 'Ingeniería y desarrollo social regional',
      highlightStat: SOCIAL.poblacionEje.valor,
      highlightLabel: 'de habitantes en el eje Ibagué – Cajamarca – Armenia (dia. 27)',
    },
    {
      id: 'ambiental',
      category: 'Descarbonización del Cruce',
      title: 'Impacto Ambiental',
      badge: 'Reducción del 90 %',
      badgeStyle: 'bg-gmae-50 text-gmae-700 border-gmae-300',
      borderHover: 'hover:border-emerald-500/80 hover:shadow-emerald-500/20 ring-1 ring-emerald-500/20',
      icon: Leaf,
      iconColor: 'text-gmae-600',
      iconBg: 'bg-emerald-500/20 border-emerald-500/40',
      summary:
        'Reducción del 90 % de emisiones y consumos energéticos del cruce por cambio modal a tracción eléctrica. No es cero: el balance neto depende de la matriz eléctrica y de la huella de construcción.',
      points: [
        `Reducción del ${AMBIENTAL.reduccionGEI.valor} de las emisiones GEI y de los consumos energéticos del cruce. [Fuente, dia. 25]`,
        `${AMBIENTAL.geiEvitados.valor} de emisiones evitadas acumuladas a 50 años. [Fuente, dia. 26]`,
        `Ahorro de ${AMBIENTAL.combustible.valor} de combustible en 2030. [Fuente, dia. 26]`,
        'Menor presión de intervención superficial sobre los ecosistemas de alta montaña al derivar el tráfico pesado al subsuelo.',
      ],
      detailedSpecs: [
        'La reducción es del 90 %, no del 100 %. La tracción eléctrica elimina las emisiones directas dentro del túnel, pero la huella real depende de la matriz de generación eléctrica del país.',
        `Vacío identificado: la fuente no reporta la huella de carbono de la construcción, pese a implicar ${EXCAVACION.volumenTuneles.valor} de excavación en túneles principales y ${EXCAVACION.volumenGalerias.valor} en galerías. [Fuente, dia. 22]`,
        'El balance neto real es la diferencia entre las emisiones evitadas en operación y las incorporadas en la construcción. Ese balance no está publicado.',
        'Estimar el orden de magnitud del material sobrante y su disposición es un aporte propio del objetivo específico 7.',
      ],
      imageUrl: 'https://images.unsplash.com/photo-1511497584788-876761c1598f?auto=format&fit=crop&w=800&q=80',
      imageAlt: 'Ecosistema de montaña y conservación hídrica',
      highlightStat: AMBIENTAL.reduccionGEI.valor,
      highlightLabel: 'de reducción de emisiones GEI del cruce (dia. 25)',
    },
    {
      id: 'seguridad',
      category: 'Seguridad Vial',
      title: 'Seguridad Vial',
      badge: 'Costos Externos Evitados',
      badgeStyle: 'bg-acred-400/15 text-acred-600 border-acred-400/50',
      borderHover: 'hover:border-amber-500/60 hover:shadow-amber-500/10',
      icon: ShieldCheck,
      iconColor: 'text-acred-600',
      iconBg: 'bg-amber-500/10 border-amber-500/20',
      summary:
        'Trasladar la carga pesada a plataformas ferroviarias elimina la exposición al descenso prolongado, condición asociada a los siniestros de alta gravedad del paso.',
      points: [
        `Ahorro en costos externos —congestión, polución, seguridad vial y ruido— de ${AMBIENTAL.costosExternos.valor} a 50 años. [Fuente, dia. 26]`,
        'Eliminación de la exposición de la carga pesada al descenso prolongado de alta montaña.',
        'Liberación de la calzada de la Ruta 40 del tráfico pesado lento, en beneficio de los vehículos livianos. [Fuente, dia. 29]',
        `Sistema de ventilación longitudinal con pozos de extracción intermedios. [Fuente, dia. 20]`,
      ],
      detailedSpecs: [
        'Los $COP 138,5 billones son el indicador que conecta simultáneamente los ejes ambiental y de seguridad vial, y es la cifra más robusta disponible en la fuente para este eje.',
        'La reducción porcentual de siniestros NO está cuantificada por la fuente y no se estima aquí.',
        'Marco normativo de referencia: NFPA 130 y fichas UIC. La NFPA 130 está orientada a transporte de pasajeros y no cubre directamente una autopista rodante de carga.',
        'En Colombia no existe norma técnica específica para túneles ferroviarios de esta tipología. Ese vacío normativo es un hallazgo del semillero.',
      ],
      imageUrl: 'https://images.unsplash.com/photo-1508873696983-2df515122519?auto=format&fit=crop&w=800&q=80',
      imageAlt: 'Infraestructura de tunelería y seguridad',
      highlightStat: AMBIENTAL.costosExternos.valor,
      highlightLabel: 'en costos externos evitados a 50 años (dia. 26)',
    },
  ];

  return (
    <section id="impactos" className="py-24 bg-white/40 /40 relative overflow-hidden border-t border-slate-200 transition-colors duration-300">
      {/* Background Accent Lines */}
      <div className="absolute inset-0 bg-grid-pattern opacity-20 pointer-events-none" />
      <div className="absolute top-1/3 right-0 w-[500px] h-[500px] bg-emerald-500/5 blur-[140px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header with Framer Motion */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="text-center max-w-3xl mx-auto space-y-4 mb-16"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 border border-slate-300 text-slate-600 text-xs font-semibold uppercase tracking-wider">
            <span>Cuadrícula de Beneficios Integrales</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-uni-900 tracking-tight">
            Evaluación de Impactos
          </h2>
          <p className="text-base sm:text-lg text-slate-600 leading-relaxed font-light">
            Análisis de la propuesta en cuatro dimensiones: económica, social, ambiental y de seguridad vial. Haz clic en cada tarjeta para consultar la ficha ampliada con datos y fuentes.
          </p>
        </motion.div>

        {/* 4 Cards Grid with Framer Motion Staggered Animations */}
        <div className="grid md:grid-cols-2 gap-8">
          {impacts.map((item, index) => {
            const Icon = item.icon;
            const isEmerald = item.id === 'ambiental';

            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.15 }}
                onClick={() => setSelectedImpact(item)}
                className={`group relative rounded-3xl bg-slate-50/90 p-8 border border-slate-200/90 transition-all duration-300 flex flex-col justify-between ${item.borderHover} shadow-xl cursor-pointer`}
              >
                <div>
                  {/* Top Bar inside Card */}
                  <div className="flex items-center justify-between gap-4 mb-6">
                    <div className={`w-14 h-14 rounded-2xl ${item.iconBg} border flex items-center justify-center group-hover:scale-105 transition-transform`}>
                      <Icon className={`w-7 h-7 ${item.iconColor}`} />
                    </div>
                    <span className={`px-3 py-1 rounded-full border text-xs font-semibold tracking-wide ${item.badgeStyle}`}>
                      {item.badge}
                    </span>
                  </div>

                  {/* Titles */}
                  <span className="text-xs font-mono font-medium text-slate-500 uppercase tracking-wider">
                    {item.category}
                  </span>
                  <h3 className={`text-2xl font-extrabold text-uni-900 mb-3 mt-1 ${isEmerald ? 'group-hover:text-gmae-600' : 'group-hover:text-uni-600'} transition-colors`}>
                    {item.title}
                  </h3>

                  {/* Summary */}
                  <p className="text-sm text-slate-600 leading-relaxed font-light mb-6">
                    {item.summary}
                  </p>

                  {/* Bullet points */}
                  <ul className="space-y-3 mb-8">
                    {item.points.map((pt, idx) => (
                      <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-600 leading-normal">
                        <ArrowUpRight className={`w-4 h-4 shrink-0 mt-0.5 ${item.iconColor}`} />
                        <span>{pt}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Card Footer Metric */}
                <div className={`pt-6 border-t border-slate-900 flex items-center justify-between ${isEmerald ? 'bg-gmae-50 -mx-8 -mb-8 p-8 rounded-b-3xl border-t-gmae-200' : ''}`}>
                  <div>
                    <div className={`text-3xl font-black ${isEmerald ? 'text-gmae-600' : 'text-uni-900'}`}>
                      {item.highlightStat}
                    </div>
                    <div className="text-xs text-slate-500 font-medium">{item.highlightLabel}</div>
                  </div>
                  
                  <div className="text-xs text-uni-600 font-mono font-bold flex items-center gap-1 group-hover:text-gmae-600 transition-colors">
                    <span>Ver Detalles +</span>
                    <ArrowUpRight className="w-3.5 h-3.5" />
                  </div>
                </div>

              </motion.div>
            );
          })}
        </div>

      </div>

      {/* Interactive Modal for Impact Details */}
      {selectedImpact && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-slate-50/85 backdrop-blur-md transition-opacity"
            onClick={() => setSelectedImpact(null)}
          />

          {/* Modal Container */}
          <div className="relative w-full max-w-3xl bg-white border border-slate-200 rounded-3xl shadow-2xl z-10 my-8 overflow-hidden">
            
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 sm:p-8 border-b border-slate-200 bg-slate-50">
              <div className="flex items-center gap-3">
                <div className={`p-3 rounded-xl ${selectedImpact.iconBg} border`}>
                  <selectedImpact.icon className={`w-6 h-6 ${selectedImpact.iconColor}`} />
                </div>
                <div>
                  <span className="text-xs font-mono font-semibold text-gmae-600 uppercase tracking-wider">
                    Ficha Técnica de Impacto
                  </span>
                  <h3 className="text-xl sm:text-2xl font-bold text-uni-900">{selectedImpact.title}</h3>
                </div>
              </div>
              <button
                onClick={() => setSelectedImpact(null)}
                className="p-2 rounded-lg text-slate-500 hover:text-uni-900 hover:bg-slate-100 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Modal Content Body */}
            <div className="p-6 sm:p-8 space-y-6 max-h-[75vh] overflow-y-auto">
              
              {/* Representative Image Container */}
              <div className="relative w-full h-56 rounded-2xl overflow-hidden border border-slate-200 shadow-inner group">
                <img
                  src={selectedImpact.imageUrl}
                  alt={selectedImpact.imageAlt}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-50 via-slate-100/60 to-transparent" />
                <div className="absolute bottom-4 left-4 right-4 flex justify-between items-end">
                  <span className="text-xs font-mono text-slate-600 bg-white/80 px-3 py-1 rounded-lg border border-slate-200">
                    {selectedImpact.imageAlt}
                  </span>
                  <span className="text-xl font-black text-white bg-blue-600/80 px-3 py-1 rounded-lg">
                    {selectedImpact.highlightStat}
                  </span>
                </div>
              </div>

              {/* Detailed Specs Bullet Points */}
              <div className="space-y-4">
                <h4 className="text-sm font-bold text-uni-900 uppercase tracking-wider flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-gmae-600" />
                  Especificaciones Cuantitativas Reales
                </h4>
                <div className="grid sm:grid-cols-2 gap-3">
                  {selectedImpact.detailedSpecs.map((spec, idx) => (
                    <div key={idx} className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                      <div className="flex items-center gap-2 text-xs font-semibold text-gmae-600">
                        <CheckCircle2 className="w-4 h-4 shrink-0" />
                        <span>Métrica #{idx + 1}</span>
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed font-light">
                        {spec}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* Modal Footer */}
            <div className="p-4 sm:p-6 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
              <span className="text-xs text-slate-500 font-mono">
                Semillero GEOPAV · Universidad de Ibagué · Paz y Región 2026B
              </span>
              <button
                onClick={() => setSelectedImpact(null)}
                className="px-6 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-700 text-uni-900 font-semibold text-xs transition-colors"
              >
                Cerrar Ficha
              </button>
            </div>

          </div>
        </div>
      )}

    </section>
  );
};
