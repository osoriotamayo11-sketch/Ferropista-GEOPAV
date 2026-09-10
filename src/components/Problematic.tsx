'use client';

import React, { useState } from 'react';
import { AlertTriangle, Clock, TrendingUp, CloudRain, Truck, X, BookOpen, ExternalLink, ShieldAlert } from 'lucide-react';
import { ACTUAL, FUENTE_PRIMARIA } from '@/data/proyecto';

interface ProblemItem {
  id: string;
  icon: React.ElementType;
  iconColor: string;
  bgColor: string;
  borderColor: string;
  title: string;
  subtitle: string;
  description: string;
  expandedText: string;
  source: string;
  stat: string;
  statLabel: string;
}

export const Problematic: React.FC = () => {
  const [selectedProblem, setSelectedProblem] = useState<ProblemItem | null>(null);

  const problems: ProblemItem[] = [
    {
      id: 'siniestralidad',
      icon: AlertTriangle,
      iconColor: 'text-red-700',
      bgColor: 'bg-red-500/10',
      borderColor: 'border-red-500/30',
      title: 'Siniestralidad Vial de Alta Gravedad',
      subtitle: 'Descensos prolongados de alta montaña',
      description:
        'El paso del Alto de La Línea registra siniestros viales de alta gravedad asociados a los descensos prolongados: volcamientos e incendios de tractomulas, y colisiones con víctimas múltiples.',
      expandedText:
        'La ponencia de referencia documenta la siniestralidad del paso de forma cualitativa, mediante casos de prensa entre 2022 y 2025: volcamiento e incendio de tractomulas, siniestros de bus con víctimas múltiples y cierres de vía por accidentes en los túneles del sector. No aporta ninguna tasa anual agregada. ' +
        'El Semillero GEOPAV cerró ese vacío en el objetivo específico 5: el conjunto rs3u-8r4q de la ANSV entrega punto de referencia, latitud, longitud y fallecidos por sector crítico, de modo que cada uno se ubica sobre la vía. Cruzado con la serie histórica de tránsito de INVÍAS resulta una tasa de 7,66 fallecidos por cada 100 millones de vehículos-kilómetro en el paso, y 4,56 en el corredor completo. La línea base es de 2015 a 2019, anterior al Túnel de La Línea, y por tanto sobrestima el riesgo del corredor actual.',
      source: FUENTE_PRIMARIA.cita + ' — diapositivas 11 a 13 (documentación cualitativa).',
      stat: '2022–2025',
      statLabel: 'periodo de siniestros graves documentados por la fuente',
    },
    {
      id: 'eficiencia',
      icon: TrendingUp,
      iconColor: 'text-acred-600',
      bgColor: 'bg-amber-500/10',
      borderColor: 'border-amber-500/30',
      title: 'Baja Eficiencia de Operación',
      subtitle: 'Velocidad media inferior a 20 km/h',
      description:
        'El transporte de carga opera en el paso a una velocidad media inferior a 20 km/h, con costos de operación vehicular altos y servicio irregular.',
      expandedText:
        'El perfil del trazado actual obliga a los vehículos de carga a ascender desde los 950 msnm de Ibagué hasta los 3.300 msnm del Alto de La Línea, para descender después a los 1.450 msnm de Armenia. La ponencia caracteriza las condiciones de movilidad resultantes como costos de operación vehicular altos, impactos ambientales negativos y servicio irregular con velocidad media inferior a 20 km/h. ' +
        'La cuantificación del sobrecosto logístico no está en la fuente y no se publica aquí: debe construirla el semillero en el objetivo específico 6, mediante una matriz propia de costos operativos unitarios.',
      source: FUENTE_PRIMARIA.cita + ' — diapositivas 13 y 20.',
      stat: ACTUAL.velocidadMedia.valor,
      statLabel: 'velocidad media de operación del transporte de carga',
    },
    {
      id: 'tiempo',
      icon: Clock,
      iconColor: 'text-acred-600',
      bgColor: 'bg-orange-500/10',
      borderColor: 'border-orange-500/30',
      title: 'Tiempo de Cruce del Paso',
      subtitle: 'Cuello de botella del corredor',
      description:
        'El tiempo medio de cruce del paso es de 4 horas. El Alto de La Línea es el cuello de botella del principal corredor logístico del país.',
      expandedText:
        'La ponencia declara un tiempo medio de paso de 4 horas para los camiones y lo contrasta con los 70 minutos de tiempo integrado que ofrecería el sistema Ferropista. En términos agregados estima los tiempos de viaje de los usuarios de la Ruta 40 en 7,0 millones de horas al año, frente a 1,7 millones con la Ferropista. ' +
        'Nota crítica del semillero: la propia fuente presenta una inconsistencia interna. La diapositiva 28 reporta 5,0 millones de horas ahorradas al año, mientras que el gráfico de la diapositiva 29 arroja 5,3 millones. La diferencia es del 6 %. Se documenta el rango en lugar de escoger un valor en silencio.',
      source: FUENTE_PRIMARIA.cita + ' — diapositivas 28 y 29.',
      stat: ACTUAL.tiempoCruce.valor,
      statLabel: 'tiempo medio de cruce declarado por la fuente',
    },
    {
      id: 'volumen',
      icon: Truck,
      iconColor: 'text-slate-400',
      bgColor: 'bg-slate-500/10',
      borderColor: 'border-slate-500/30',
      title: 'Volumen de Carga Creciente',
      subtitle: 'Infraestructura operando al límite',
      description:
        'Por el paso circulan 2.100 camiones grandes y 1.700 medianos al día, equivalentes a 1,39 millones de vehículos pesados al año, con una tasa de crecimiento del 3 % anual.',
      expandedText:
        'Los aforos de INVÍAS de 2017 que cita la ponencia registran 2.100 camiones grandes y 1.700 camiones medianos por día en el Alto de La Línea, equivalentes a 1.390.000 vehículos pesados al año sobre un total de 2,3 millones de vehículos. Con una tasa de crecimiento del 3 % anual, la previsión para 2030 es de 1.700.000 vehículos pesados al año, volumen comparable al del Eurotúnel entre Francia y el Reino Unido. ' +
        'El tránsito continuo de carga pesada en ascenso sostiene un consumo de combustible y unas emisiones evitables, y mantiene una presión permanente de intervención sobre los ecosistemas de alta montaña de la Cordillera Central.',
      source: FUENTE_PRIMARIA.cita + ' — diapositivas 10 y 17 (aforos INVÍAS 2017).',
      stat: '1,39 M',
      statLabel: 'vehículos pesados al año, creciendo al 3 % anual',
    },
  ];

  return (
    <section id="problematica" className="py-24 bg-white relative overflow-hidden border-t border-b border-slate-200">
      {/* Subtle Background Glow */}
      <div className="absolute top-1/2 left-0 w-96 h-96 bg-red-600/5 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-amber-600/5 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-700 text-xs font-semibold uppercase tracking-wider">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Diagnóstico del Corredor Actual</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-uni-900 tracking-tight">
            La Problemática del Alto de La Línea
          </h2>
          <p className="text-base sm:text-lg text-slate-500 leading-relaxed">
            El paso por la Cordillera Central es el mayor obstáculo para la competitividad comercial de Colombia. Haz clic en cualquier tarjeta para examinar el análisis técnico extendido y la fuente oficial.
          </p>
        </div>

        {/* Problems Grid (Interactive Cards) */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {problems.map((problem) => {
            const Icon = problem.icon;
            return (
              <div
                key={problem.id}
                onClick={() => setSelectedProblem(problem)}
                className="group relative rounded-2xl bg-white/80 p-6 border border-slate-200 hover:border-red-500/50 transition-all duration-300 flex flex-col justify-between hover:-translate-y-1 hover:shadow-xl hover:shadow-red-950/20 cursor-pointer"
              >
                <div>
                  <div className={`w-12 h-12 rounded-xl ${problem.bgColor} ${problem.borderColor} border flex items-center justify-center mb-5 group-hover:scale-110 transition-transform`}>
                    <Icon className={`w-6 h-6 ${problem.iconColor}`} />
                  </div>
                  <h3 className="text-xl font-bold text-uni-900 mb-1 group-hover:text-red-700 transition-colors">
                    {problem.title}
                  </h3>
                  <p className="text-xs font-medium text-slate-500 mb-3">{problem.subtitle}</p>
                  <p className="text-sm text-slate-600 leading-relaxed font-light mb-6">
                    {problem.description}
                  </p>
                </div>

                <div className="pt-4 border-t border-slate-900 flex items-end justify-between">
                  <div>
                    <div className="text-2xl font-black text-uni-900 group-hover:text-red-700 transition-colors">
                      {problem.stat}
                    </div>
                    <div className="text-[11px] text-slate-500">{problem.statLabel}</div>
                  </div>
                  <span className="text-xs text-red-700 font-mono underline opacity-0 group-hover:opacity-100 transition-opacity">
                    Ver informe +
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Current vs Target Comparison Card */}
        <div className="mt-12 rounded-2xl bg-slate-50 p-6 sm:p-8 border border-slate-200 flex flex-col lg:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-acred-600 shrink-0">
              <Truck className="w-8 h-8" />
            </div>
            <div>
              <h4 className="text-lg font-bold text-uni-900">Impacto en la Cadena Logística Nacional</h4>
              <p className="text-sm text-slate-500">
                El Alto de La Línea es el cuello de botella del corredor Bogotá – Buenaventura, con 28 millones de habitantes en su área de influencia. [Ponencia, dia. 17]
              </p>
            </div>
          </div>
          <div className="flex items-center gap-6 shrink-0 text-right">
            <div className="text-center lg:text-right">
              <span className="block text-xs text-slate-500 font-mono">Vehículos pesados (2017)</span>
              <span className="text-xl font-bold text-red-700">1.390.000 /año</span>
            </div>
            <div className="h-8 w-px bg-slate-100 hidden sm:block"></div>
            <div className="text-center lg:text-right">
              <span className="block text-xs text-slate-500 font-mono">Proyección a 2030</span>
              <span className="text-xl font-bold text-red-700">1.700.000 /año</span>
            </div>
          </div>
        </div>

      </div>

      {/* Interactive Modal for Problem Details */}
      {selectedProblem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-white/80 backdrop-blur-md transition-opacity"
            onClick={() => setSelectedProblem(null)}
          />

          {/* Modal Container */}
          <div className="relative w-full max-w-2xl bg-white border border-slate-200 rounded-3xl shadow-2xl shadow-red-950/30 z-10 my-8 overflow-hidden">
            
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-slate-200 bg-slate-50">
              <div className="flex items-center gap-3">
                <div className={`p-3 rounded-xl ${selectedProblem.bgColor} ${selectedProblem.borderColor} border`}>
                  <selectedProblem.icon className={`w-6 h-6 ${selectedProblem.iconColor}`} />
                </div>
                <div>
                  <span className="text-xs font-mono font-semibold text-red-700 uppercase tracking-wider">
                    Análisis Ampliado de Problemática
                  </span>
                  <h3 className="text-xl font-bold text-uni-900">{selectedProblem.title}</h3>
                </div>
              </div>
              <button
                onClick={() => setSelectedProblem(null)}
                className="p-2 rounded-lg text-slate-500 hover:text-uni-900 hover:bg-slate-100 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 sm:p-8 space-y-6">
              
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                <div>
                  <span className="text-xs text-slate-500 font-mono">Métrica Relevante</span>
                  <p className="text-2xl font-black text-red-700">{selectedProblem.stat}</p>
                </div>
                <div className="text-right text-xs text-slate-600 font-medium max-w-[200px]">
                  {selectedProblem.statLabel}
                </div>
              </div>

              <div className="space-y-2">
                <h4 className="text-sm font-bold text-uni-900 flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-acred-600" />
                  Diagnóstico Geotécnico y Logístico
                </h4>
                <p className="text-sm text-slate-600 leading-relaxed font-light">
                  {selectedProblem.expandedText}
                </p>
              </div>

              {/* Source Field */}
              <div className="p-4 rounded-xl bg-white/80 border border-slate-200 space-y-1">
                <div className="flex items-center gap-2 text-xs font-bold text-acred-600">
                  <BookOpen className="w-4 h-4" />
                  <span>Fuente de la información:</span>
                </div>
                <p className="text-xs text-slate-600 font-mono leading-relaxed">
                  {selectedProblem.source}
                </p>
              </div>

            </div>

            {/* Modal Footer */}
            <div className="p-4 sm:p-6 border-t border-slate-200 bg-slate-50 flex justify-end">
              <button
                onClick={() => setSelectedProblem(null)}
                className="px-6 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-700 text-uni-900 font-semibold text-xs transition-colors"
              >
                Cerrar Detalle
              </button>
            </div>

          </div>
        </div>
      )}

    </section>
  );
};
