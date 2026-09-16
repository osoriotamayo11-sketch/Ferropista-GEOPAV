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
  icon: React.ComponentType<{ className?: string }>;
  iconColor: string;
  iconBg: string;
  summary: string;
  points: string[];
  detailedSpecs: string[];
  /* Cabecera del detalle. Antes eran fotos tomadas de un servicio externo por
     enlace directo: no estaban bajo control del semillero y dejaron de cargar,
     de modo que la ficha se abria con el hueco de una imagen rota. Las de ahora
     son generadas para el proyecto y viven en el propio repositorio, en
     public/impactos/, reducidas a 1.400 px de ancho.
     No documentan nada: ilustran el tema de la ficha y por eso no llevan pie
     de fuente ni marca de origen. */
  panelImagen: string;
  panelDegradado: string;
  panelRotulo: string;
  /* Acento del pie de la tarjeta. Antes solo la ficha ambiental lo tenia, por
     una condicion escrita a mano sobre su id; ahora cada una lleva el suyo. */
  pieFondo: string;
  pieCifra: string;
  tituloHover: string;
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
      panelImagen: '/impactos/economico.webp',
      panelDegradado: 'from-uni-800 via-uni-700 to-uni-500',
      pieFondo: 'bg-uni-50 border-t-uni-200',
      pieCifra: 'text-uni-700',
      tituloHover: 'group-hover:text-uni-700',
      panelRotulo: 'Logística de carga pesada e intermodalidad',
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
      panelImagen: '/impactos/social.webp',
      panelDegradado: 'from-uni-700 via-uni-500 to-uni-300',
      pieFondo: 'bg-sky-50 border-t-sky-200',
      pieCifra: 'text-sky-700',
      tituloHover: 'group-hover:text-sky-700',
      panelRotulo: 'Población y desarrollo del área de influencia',
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
      panelImagen: '/impactos/ambiental.webp',
      panelDegradado: 'from-gmae-800 via-gmae-600 to-gmae-400',
      pieFondo: 'bg-gmae-50 border-t-gmae-200',
      pieCifra: 'text-gmae-600',
      tituloHover: 'group-hover:text-gmae-600',
      panelRotulo: 'Ecosistema de alta montaña y descarbonización',
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
      panelImagen: '/impactos/seguridad.webp',
      panelDegradado: 'from-acred-600 via-acred-500 to-acred-400',
      pieFondo: 'bg-amber-50 border-t-amber-200',
      pieCifra: 'text-acred-600',
      tituloHover: 'group-hover:text-acred-600',
      panelRotulo: 'Tunelería, operación protegida y seguridad vial',
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
                  <h3 className={`mb-3 mt-1 text-2xl font-extrabold text-uni-900 transition-colors ${item.tituloHover}`}>
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
                <div className={`-mx-8 -mb-8 flex items-center justify-between rounded-b-3xl border-t p-8 ${item.pieFondo}`}>
                  <div>
                    <div className={`text-3xl font-black ${item.pieCifra}`}>
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
              
              {/* Cabecera del detalle: imagen propia del repositorio.
                  El degradado del color de la ficha queda de fondo mientras
                  carga y como tinte bajo el rotulo. */}
              <div className={`relative h-56 w-full overflow-hidden rounded-2xl border border-slate-200 bg-gradient-to-br ${selectedImpact.panelDegradado}`}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={selectedImpact.panelImagen}
                  alt={selectedImpact.panelRotulo}
                  width={1400}
                  height={515}
                  loading="lazy"
                  className="h-full w-full object-cover"
                />

                <div className="absolute left-5 top-5 flex items-center gap-3">
                  <div className="rounded-2xl border border-white/25 bg-slate-900/35 p-2.5 backdrop-blur-sm">
                    <selectedImpact.icon className="h-6 w-6 text-white" />
                  </div>
                  <span className="rounded-full bg-slate-900/35 px-2.5 py-1 font-mono text-[10px] font-semibold uppercase tracking-widest text-white backdrop-blur-sm">
                    {selectedImpact.category}
                  </span>
                </div>

                <div className="absolute inset-x-0 bottom-0 h-28 bg-gradient-to-t from-slate-900/75 via-slate-900/35 to-transparent" />
                <div className="absolute bottom-4 left-4 right-4 flex items-end justify-between gap-3">
                  <span className="rounded-lg bg-slate-900/45 px-3 py-1 font-mono text-xs text-white backdrop-blur-sm">
                    {selectedImpact.panelRotulo}
                  </span>
                  <span className="whitespace-nowrap rounded-lg border border-white/25 bg-slate-900/55 px-3 py-1 text-xl font-black text-white backdrop-blur-sm">
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
