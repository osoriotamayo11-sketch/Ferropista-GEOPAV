'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  ShieldAlert, CheckCircle2, Circle, Loader2, AlertTriangle, MapPin, Gauge,
  Download, FolderOpen, Route, ExternalLink,
} from 'lucide-react';
import {
  SEGURIDAD_VIAL as SV, PLAN_ACCION, EQUIPO,
  ETIQUETA_MARCA, COLOR_MARCA, type Dato, type Marca, type EstadoItem,
} from '@/data/proyecto';
import Acordeon from './Acordeon';
import { ExposicionCocora, TransitoInvias } from './graficos/GraficosOE5';

/* Mismo chip de marca de origen que el resto del sitio. */
const ChipMarca: React.FC<{ marca: Marca }> = ({ marca }) => (
  <span
    title={ETIQUETA_MARCA[marca]}
    className={`shrink-0 text-[9px] font-bold px-1.5 py-0.5 rounded border ${COLOR_MARCA[marca]}`}
  >
    {marca}
  </span>
);

const ESTADO_UI: Record<EstadoItem, { texto: string; clase: string; Icono: React.ComponentType<{ className?: string }> }> = {
  completado: { texto: 'Completado', clase: 'bg-gmae-50 text-gmae-700 border-gmae-300', Icono: CheckCircle2 },
  en_curso:   { texto: 'En curso',   clase: 'bg-uni-50 text-uni-700 border-uni-200',    Icono: Loader2 },
  pendiente:  { texto: 'Pendiente',  clase: 'bg-slate-100 text-slate-600 border-slate-300', Icono: Circle },
};

const BadgeEstado: React.FC<{ estado: EstadoItem }> = ({ estado }) => {
  const { texto, clase, Icono } = ESTADO_UI[estado];
  return (
    <span className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full border ${clase}`}>
      <Icono className={`w-3 h-3 ${estado === 'en_curso' ? 'animate-spin' : ''}`} />
      {texto}
    </span>
  );
};

const Cifra: React.FC<{ etiqueta: string; dato: Dato }> = ({ etiqueta, dato }) => (
  <div className="rounded-xl bg-slate-50 border border-slate-200 p-4 flex flex-col gap-1.5">
    <div className="flex items-start justify-between gap-2">
      <span className="text-[11px] text-slate-500 font-semibold leading-snug">{etiqueta}</span>
      <ChipMarca marca={dato.marca} />
    </div>
    <span className="text-xl font-black text-uni-900 leading-none break-words">{dato.valor}</span>
    {dato.nota && <span className="text-[10px] text-slate-500 leading-relaxed break-words">{dato.nota}</span>}
  </div>
);

/* La tasa, en grande. Es el resultado del objetivo. */
const Tasa: React.FC<{ titulo: string; pie: string; dato: Dato; tenue?: boolean }> = ({
  titulo, pie, dato, tenue = false,
}) => (
  <div
    className={`rounded-2xl border p-5 sm:p-6 flex flex-col gap-2 ${
      tenue ? 'bg-slate-50 border-slate-200' : 'bg-white border-uni-200'
    }`}
  >
    <div className="flex items-start justify-between gap-2">
      <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">{titulo}</span>
      <ChipMarca marca={dato.marca} />
    </div>
    <span className={`text-5xl sm:text-6xl font-black leading-none ${tenue ? 'text-slate-400' : 'text-uni-800'}`}>
      {dato.valor}
    </span>
    <span className="text-[11px] font-semibold text-slate-600">{pie}</span>
    {dato.nota && <span className="text-[10px] text-slate-500 leading-relaxed">{dato.nota}</span>}
  </div>
);

/* Gráficos del objetivo. Cada uno sustituye al panel de serie temporal de la
   lámina PNG que ocupaba su lugar; la lámina sigue siendo el entregable y
   queda enlazada para descarga. Las cifras rotuladas salen del resumen del
   archivo de datos —media ponderada por días—, no de la curva. */
const GRAFICOS = [
  {
    id: 'cocora',
    titulo: 'Exposición medida en el peaje Cocora',
    pie:
      'Tránsito promedio diario en el peaje Cocora (vía Ibagué – Cajamarca, RN40-03, km 13+800), ' +
      'total y carga pesada, mes a mes entre octubre de 2021 y mayo de 2026. Las dos líneas ' +
      'punteadas son la media de los últimos doce meses, que es la cifra que el sitio publica. ' +
      'Fuente: ANI, conjunto 8yi9-t44c de datos.gov.co; el tránsito promedio diario es cálculo propio.',
    lamina: '/oe5/siniestralidad.png',
  },
  {
    id: 'invias',
    titulo: 'Veinte años de tránsito medido por INVÍAS',
    pie:
      'Serie histórica de volúmenes de tránsito de INVÍAS, 1997 a 2018, en las tres estaciones del ' +
      'corredor. La 243 y la 244 son los tramos que quedan entre los portales del trazado del ' +
      'objetivo específico 1; la 245 queda fuera del paso. De aquí sale el denominador de la tasa: ' +
      'esta serie es la que cerró la brecha entre los fallecidos de 2015–2019 y el aforo del peaje, ' +
      'que solo empieza en 2021. La lámina que contiene este panel se muestra completa más abajo.',
    lamina: null,
  },
] as const;

/* La lámina compuesta se conserva como imagen: lleva el mapa de sectores
   sobre el trazado y el detalle del descenso, que no son series que el
   navegador pueda volver a dibujar. Mismo criterio que la lámina de trazado
   del objetivo específico 1. */
const LAMINA_MAPA = {
  src: '/oe5/graficos_siniestralidad.png',
  w: 1800,
  h: 952,
  titulo: 'Sectores críticos sobre el trazado y detalle del descenso a Calarcá',
  pie:
    'Los seis sectores críticos de la ANSV situados sobre el trazado del túnel del objetivo 1, con ' +
    'el detalle del descenso hacia Calarcá. El tamaño del círculo es el número de fallecidos y el ' +
    'color es el nivel de confianza del estadístico Getis-Ord Gi* que publica la propia ANSV. ' +
    'Relieve: Copernicus DEM GLO-30. La lámina incluye además los dos paneles que arriba ya se ' +
    'ofrecen como gráficos interrogables.',
};

/* Carpetas de evidencia del OE 5, una por actividad. Las URL se transcribieron
   del Google Sheet oficial y cada una se comprobó abriéndola: la página de
   Drive devolvió el nombre de carpeta que aparece en `entregable`. Los cuatro
   identificadores de Drive llevan caracteres ambiguos (I mayúscula frente a l
   minúscula), así que NO se editan a ojo: si alguno cambia, se vuelve a
   comprobar contra el título que devuelve Drive. */
const EVIDENCIAS_OE5: { n: number; carpeta: string; entregable: string; formato: string; contenido: string; url: string }[] = [
  {
    n: 1, carpeta: 'Act1_Aforos',
    entregable: 'Base de datos cruda de aforos', formato: 'CSV / Excel',
    contenido: 'Descarga de los conjuntos de la ANI y de INVÍAS, extracción del TPD y las series mensual y anual.',
    url: 'https://drive.google.com/drive/folders/1U6_3pOBWwg5jYce3BPSIgoqu7l1Qr-Ee',
  },
  {
    n: 2, carpeta: 'Act2_Clasificacion',
    entregable: 'Matriz de aforos clasificada', formato: 'Excel',
    contenido: 'Matriz de aforos clasificada por categoría de vehículo, con el script que la construye.',
    url: 'https://drive.google.com/drive/folders/1mRSthAfPSelGi76fgveG0S2wvfknZKg-',
  },
  {
    n: 3, carpeta: 'Act3_Siniestros',
    entregable: 'Histórico de siniestros', formato: 'PDF',
    contenido: 'Sectores críticos y velocidades de la ANSV, el recorte del corredor y el histórico de siniestros.',
    url: 'https://drive.google.com/drive/folders/1NSoocY8sdQSCLIt-1QvF9o45HsSXNAAc',
  },
  {
    n: 4, carpeta: 'Act4_Analisis',
    entregable: 'Gráficos de siniestralidad', formato: 'Excel / JPG',
    contenido: 'Cálculo de la tasa por 100 millones de vehículos-kilómetro y los scripts de las figuras.',
    url: 'https://drive.google.com/drive/folders/1GF6qQQfEPoMKyT3MbPl8PGb8I5ex3VR7',
  },
  {
    n: 5, carpeta: 'Act5_Informe',
    entregable: 'Informe de diagnóstico vial', formato: 'PDF',
    contenido: 'Informe de diagnóstico vial y memoria metodológica.',
    url: 'https://drive.google.com/drive/folders/1xbAuxTOUZcZkolGr7h2_U-efjul17K2k',
  },
];

export const SintesisOE5: React.FC = () => {
  const oe5 = PLAN_ACCION.find((o) => o.id === 'oe5');
  if (!oe5) return null;

  const maxFallecidos = Math.max(...SV.sectores.map((s) => s.fallecidos));
  const maxTpd = Math.max(...SV.mediciones.map((m) => m.tpd));

  return (
    <section id="oe5" className="py-24 bg-slate-50 relative overflow-hidden border-t border-slate-200">
      <div className="absolute top-1/4 left-0 w-[500px] h-[400px] bg-uni-600/5 blur-[130px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-red-600/5 blur-[130px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">

        {/* Encabezado */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-gmae-600 text-xs font-semibold uppercase tracking-wider">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Objetivo específico 5 · Síntesis y evidencias</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-uni-900 tracking-tight">
            Siniestralidad del paso: la tasa, por primera vez medida
          </h2>
          <p className="text-base sm:text-lg text-slate-500 leading-relaxed">
            La ponencia no aporta ninguna tasa de siniestralidad y este semillero tampoco podía
            calcularla: los fallecidos que publica la ANSV son de 2015 a 2019 y el único aforo
            disponible empezaba en octubre de 2021. La serie histórica de tránsito de INVÍAS cerró
            esa brecha. Hoy el numerador y el denominador comparten estación, vía y periodo.
          </p>
        </div>

        {/* 1. Estado del objetivo */}
        <div className="rounded-2xl bg-white border border-gmae-300/60 p-6 sm:p-8 mb-6">
          <div className="flex flex-wrap items-center gap-3 mb-4">
            <BadgeEstado estado={oe5.estado} />
            <span className="text-[11px] font-mono text-slate-500">{oe5.inicio} → {oe5.fin}</span>
            <span className="text-[11px] text-slate-500">· Responsable: {oe5.responsable}</span>
          </div>
          <p className="text-sm text-slate-700 leading-relaxed mb-5">{oe5.titulo}</p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-3">
            {oe5.actividades.map((a) => {
              const { Icono } = ESTADO_UI[a.estado];
              const tinte = a.estado === 'completado' ? 'text-gmae-600'
                : a.estado === 'en_curso' ? 'text-uni-600' : 'text-slate-400';
              return (
                <div key={a.n} className="rounded-xl bg-slate-50 border border-slate-200 p-3 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono text-slate-500">Act {a.n}</span>
                    <Icono className={`w-3.5 h-3.5 ${tinte} ${a.estado === 'en_curso' ? 'animate-spin' : ''}`} />
                  </div>
                  <p className="text-[11px] text-slate-600 leading-snug">{a.entregable}</p>
                  <p className="text-[10px] font-mono text-slate-400">{a.inicio} → {a.fin}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* 2. El resultado: la tasa. Dos cifras, no tres: la anterior se movió
               al acordeón del método, donde queda auditable sin competir con
               el resultado vigente. */}
        <div className="rounded-2xl bg-white border border-slate-200 p-5 sm:p-7 mb-6">
          <div className="flex items-center gap-2 mb-1.5">
            <Gauge className="w-4 h-4 text-uni-600" />
            <h3 className="text-lg font-bold text-uni-900">La tasa normalizada por exposición</h3>
          </div>
          <p className="text-xs text-slate-500 mb-5 max-w-3xl leading-relaxed">
            Contar muertos sin dividir por exposición es contar goles sin saber cuántos partidos se
            jugaron. La unidad estándar es <strong className="text-slate-700">fallecidos por cada
            100 millones de vehículos-kilómetro</strong>: fallecidos ÷ (TPD × 365 × longitud × años).
            Las dos cifras usan los mismos 42 fallecidos y difieren solo en el denominador.
            Ninguna de las dos definiciones de tramo es obviamente la correcta, así que se publican
            ambas en lugar de escoger una en silencio.
          </p>
          <div className="grid md:grid-cols-2 gap-4">
            <Tasa titulo="Corredor completo · 74 km" pie="42 fallecidos · TPD 6.820 · 5 años" dato={SV.tasaCorredor} />
            <Tasa titulo="Solo el paso · 45 km" pie="42 fallecidos · TPD 6.676 · 5 años" dato={SV.tasaPaso} />
          </div>
        </div>

        {/* 3. Entradas medidas */}
        <div className="rounded-2xl bg-white border border-slate-200 p-5 sm:p-7 mb-6">
          <h3 className="text-lg font-bold text-uni-900 mb-1.5">Las entradas del cálculo</h3>
          <p className="text-xs text-slate-500 mb-5 max-w-3xl leading-relaxed">
            Ninguna es una suposición. Cada una cita su fuente: la ANSV para los fallecidos, INVÍAS
            para el tránsito y las longitudes de tramo.
          </p>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <Cifra etiqueta="Fallecidos en el tramo del paso" dato={SV.fallecidosPaso} />
            <Cifra etiqueta="Fallecidos en todo el corredor" dato={SV.fallecidosCorredor} />
            <Cifra etiqueta="Sectores críticos del corredor" dato={SV.sectoresCriticos} />
            <Cifra etiqueta="Tránsito medido en el paso" dato={SV.tpdPaso} />
            <Cifra etiqueta="Tránsito del corredor, ponderado" dato={SV.tpdCorredor} />
            <Cifra etiqueta="Longitud del corredor" dato={SV.longitudCorredor} />
            <Cifra etiqueta="Longitud del paso" dato={SV.longitudPaso} />
            <Cifra etiqueta="Participación de la carga pesada" dato={SV.participacionPesada} />
            <Cifra etiqueta="Exposición anual de la carga pesada" dato={SV.exposicionPesada} />
            <Cifra etiqueta="Cuánto mueve la única hipótesis" dato={SV.sensibilidadHipotesis} />
            <Cifra etiqueta="Control: los 52 fallecidos sobre 74 km" dato={SV.tasaControl52} />
          </div>
        </div>

        {/* 4. Los gráficos, sustituyendo los paneles de serie de las láminas */}
        <div className="mb-6 space-y-4">
          {GRAFICOS.map((g, i) => (
            <motion.figure
              key={g.id}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.4, delay: i * 0.05 }}
              className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-6"
            >
              <figcaption className="mb-4 flex items-start justify-between gap-3">
                <h3 className="text-sm font-bold text-uni-900 sm:text-base">{g.titulo}</h3>
                <ChipMarca marca="CP" />
              </figcaption>

              {g.id === 'cocora' ? <ExposicionCocora /> : <TransitoInvias />}

              <div className="mt-4 flex flex-col gap-3 border-t border-slate-200 pt-3 sm:flex-row sm:items-start sm:justify-between">
                <p className="max-w-3xl text-[11px] leading-relaxed text-slate-500">{g.pie}</p>
                {g.lamina && (
                  <a
                    href={g.lamina}
                    download
                    className="inline-flex shrink-0 items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-[11px] font-semibold text-uni-600 transition-colors hover:border-uni-300 hover:text-uni-700"
                  >
                    <Download className="h-3.5 w-3.5 shrink-0" />
                    Descargar la lámina (PNG)
                  </a>
                )}
              </div>
            </motion.figure>
          ))}

          <motion.figure
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-60px' }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-5"
          >
            <figcaption className="mb-3 flex items-start justify-between gap-3">
              <h3 className="text-sm font-bold text-uni-900 sm:text-base">{LAMINA_MAPA.titulo}</h3>
              <ChipMarca marca="CP" />
            </figcaption>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={LAMINA_MAPA.src}
              alt={LAMINA_MAPA.titulo}
              width={LAMINA_MAPA.w}
              height={LAMINA_MAPA.h}
              loading="lazy"
              className="h-auto w-full rounded-lg border border-slate-200 bg-white"
            />
            <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <p className="max-w-3xl text-[11px] leading-relaxed text-slate-500">{LAMINA_MAPA.pie}</p>
              <a
                href={LAMINA_MAPA.src}
                download
                className="inline-flex shrink-0 items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-[11px] font-semibold text-uni-600 transition-colors hover:border-uni-300 hover:text-uni-700"
              >
                <Download className="h-3.5 w-3.5 shrink-0" />
                Descargar la lámina (PNG)
              </a>
            </div>
          </motion.figure>
        </div>

        {/* 5. Los seis sectores críticos */}
        <div className="rounded-2xl bg-white border border-slate-200 p-5 sm:p-7 mb-6">
          <div className="flex items-center gap-2 mb-1.5">
            <MapPin className="w-4 h-4 text-uni-600" />
            <h3 className="text-lg font-bold text-uni-900">Los seis sectores críticos del corredor</h3>
            <ChipMarca marca="F" />
          </div>
          <p className="text-xs text-slate-500 mb-5 max-w-3xl leading-relaxed">
            Todos caen en jurisdicción de Calarcá, Quindío, en 3,6 km del descenso. Los cuatro a cargo
            de INVÍAS, en el tramo que la ANSV nombra «Calarcá – Ibagué», suman los 42 fallecidos que
            entran en la tasa; los dos a cargo de la ANI no pertenecen al cruce y quedan fuera.
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-xs min-w-[520px]">
              <thead>
                <tr className="text-left text-[10px] uppercase tracking-wider text-slate-500 border-b border-slate-200">
                  <th className="py-2 pr-3 font-bold">Punto de referencia</th>
                  <th className="py-2 pr-3 font-bold">Fallecidos 2015–2019</th>
                  <th className="py-2 pr-3 font-bold">Confianza Gi*</th>
                  <th className="py-2 pr-3 font-bold">Entidad</th>
                  <th className="py-2 font-bold">¿Entra en la tasa?</th>
                </tr>
              </thead>
              <tbody>
                {SV.sectores.map((s, i) => (
                  <tr key={`${s.pr}-${i}`} className="border-b border-slate-100 last:border-0">
                    <td className="py-2 pr-3 font-mono font-semibold text-slate-700">{s.pr}</td>
                    <td className="py-2 pr-3">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-uni-900 w-6">{s.fallecidos}</span>
                        <span
                          className={`h-2 rounded-sm ${s.enPaso ? 'bg-uni-700' : 'bg-slate-300'}`}
                          style={{ width: `${(s.fallecidos / maxFallecidos) * 100}px` }}
                        />
                      </div>
                    </td>
                    <td className="py-2 pr-3 text-slate-600">{s.confianza}</td>
                    <td className="py-2 pr-3 text-slate-600">{s.entidad}</td>
                    <td className="py-2">
                      {s.enPaso
                        ? <span className="text-gmae-700 font-semibold">Sí</span>
                        : <span className="text-slate-400">No · tramo de la ANI</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 6. Las cuatro mediciones del corredor */}
        <div className="rounded-2xl bg-white border border-slate-200 p-5 sm:p-7 mb-6">
          <h3 className="text-lg font-bold text-uni-900 mb-1.5">Cuatro mediciones del mismo corredor</h3>
          <p className="text-xs text-slate-500 mb-5 max-w-3xl leading-relaxed">
            <strong className="text-slate-700">No son una serie temporal.</strong> Son cuatro puntos de
            medición con criterios de clasificación distintos. La clase «camiones» de la serie por
            estación de INVÍAS incluye los de dos ejes, que en peaje caen en categoría II: por eso su
            participación de carga pesada es sistemáticamente mayor. Las dos lecturas no se promedian.
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-xs min-w-[560px]">
              <thead>
                <tr className="text-left text-[10px] uppercase tracking-wider text-slate-500 border-b border-slate-200">
                  <th className="py-2 pr-3 font-bold">Punto de medición</th>
                  <th className="py-2 pr-3 font-bold">Periodo</th>
                  <th className="py-2 pr-3 font-bold">TPD</th>
                  <th className="py-2 font-bold">Carga pesada</th>
                </tr>
              </thead>
              <tbody>
                {SV.mediciones.map((m) => (
                  <tr key={m.punto} className="border-b border-slate-100 last:border-0">
                    <td className="py-2 pr-3 font-semibold text-slate-700">{m.punto}</td>
                    <td className="py-2 pr-3 text-slate-500 font-mono text-[11px]">{m.periodo}</td>
                    <td className="py-2 pr-3">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-uni-900 w-12">{m.tpd.toLocaleString('es-CO')}</span>
                        <span
                          className="h-2 rounded-sm bg-uni-500"
                          style={{ width: `${(m.tpd / maxTpd) * 90}px` }}
                        />
                      </div>
                    </td>
                    <td className="py-2 font-semibold text-slate-600">
                      {m.pesada.toLocaleString('es-CO')} %
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 7. Método, plegado: es el respaldo, no la portada del objetivo.
               Aquí vive también la corrección del 12,79: se mueve de la vista
               principal, pero no se borra — el cambio tiene que seguir siendo
               auditable desde el sitio público. */}
        <div className="mb-4">
          <Acordeon
            titulo="Cómo se hizo, y la corrección que hubo por el camino"
            resumen="Las tres fuentes, la fórmula de la tasa, el criterio de la media de doce meses y la cifra que el semillero publicaba antes."
            icono={<Route className="h-5 w-5 text-uni-600" />}
            contador="método"
          >
            <div className="max-w-3xl space-y-3 text-xs leading-relaxed text-slate-600">
              <p>
                El numerador son los fallecidos de los sectores críticos que publica la{' '}
                <strong className="text-uni-900">ANSV</strong> en el conjunto rs3u-8r4q de
                datos.gov.co, acumulados entre 2015 y 2019. El denominador es la exposición:
                tránsito promedio diario × 365 × longitud del tramo × años de registro, con el
                tránsito tomado de la <strong className="text-uni-900">serie histórica de volúmenes
                de tránsito de INVÍAS</strong> en las estaciones 243 y 244, y las longitudes de tramo
                declaradas por la misma entidad. El aforo del peaje Cocora, del conjunto 8yi9-t44c de
                la <strong className="text-uni-900">ANI</strong>, no entra en la tasa: mide un punto,
                no un tramo, y empieza en 2021, cuatro años después del último fallecido registrado.
                Sirve para describir la exposición de hoy.
              </p>
              <p>
                La media de doce meses del peaje es una{' '}
                <strong className="text-uni-900">media ponderada por días</strong>: el total de
                vehículos de los últimos doce meses dividido entre los días de esos meses, no el
                promedio de los doce TPD mensuales. Las dos difieren en unos nueve vehículos al día y
                se deja constancia de cuál se usa para que un tercero reproduzca la cifra exacta.
              </p>
            </div>

            <div className="mt-4 rounded-xl bg-amber-500/5 border border-amber-500/25 p-4">
              <div className="flex items-center gap-2 text-[11px] font-bold text-acred-600 uppercase tracking-wider mb-2">
                <AlertTriangle className="w-3.5 h-3.5" />
                La corrección, dicha en voz alta
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                El semillero publicaba <strong className="text-slate-700">12,79</strong>, casi tres
                veces la cifra real, porque sus dos entradas eran supuestos: un tránsito de 3.000
                vehículos al día y un tramo de 60 km. El tránsito medido del paso es más del doble
                del supuesto y el tramo son 74 km declarados por INVÍAS. La cifra anterior queda
                retirada de la vista principal y se conserva aquí, con su marca de hipótesis, para
                que el cambio siga siendo auditable desde el propio sitio.
              </p>
              <div className="mt-4 max-w-sm">
                <Tasa
                  titulo="Lo que publicábamos antes"
                  pie="TPD 3.000 y 60 km, ambos supuestos"
                  dato={SV.tasaAnterior}
                  tenue
                />
              </div>
            </div>
          </Acordeon>
        </div>

        {/* 8. Límites del objetivo, también plegados */}
        <div className="mb-4">
          <Acordeon
            titulo="Qué no afirma este objetivo"
            resumen="Lo que la línea base no puede sostener, declarado junto al resultado y no en letra pequeña."
            icono={<AlertTriangle className="h-5 w-5 text-acred-600" />}
            contador={`${SV.limites.length} límites`}
          >
            <ul className="space-y-2.5 text-xs text-slate-600 leading-relaxed max-w-4xl">
              {SV.limites.map((l) => (
                <li key={l} className="flex gap-2">
                  <span className="text-slate-400 shrink-0">·</span>
                  <span>{l}</span>
                </li>
              ))}
            </ul>
          </Acordeon>
        </div>

        {/* 9. Evidencias */}
        <Acordeon
          titulo="Carpetas de evidencia"
          resumen="Una carpeta de Drive por actividad, con los datos y los scripts tal como se entregaron."
          icono={<FolderOpen className="h-5 w-5 text-gmae-600" />}
          contador={`${EVIDENCIAS_OE5.length} carpetas`}
          tono="gris"
        >
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {EVIDENCIAS_OE5.map((e) => (
              <a
                key={e.carpeta}
                href={e.url}
                target="_blank"
                rel="noopener noreferrer"
                className="group flex items-start gap-3 rounded-xl bg-white border border-slate-200 p-4 hover:border-uni-300 transition-colors"
              >
                <FolderOpen className="w-4 h-4 text-gmae-600 shrink-0 mt-0.5" />
                <div className="min-w-0 flex-1">
                  <p className="text-[10px] font-mono text-slate-500">Actividad {e.n} · {e.formato}</p>
                  <p className="text-xs font-semibold text-slate-700 leading-snug mt-0.5">{e.entregable}</p>
                  <p className="text-[11px] leading-relaxed text-slate-500 mt-1">{e.contenido}</p>
                </div>
                <ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover:text-uni-600 shrink-0" />
              </a>
            ))}
          </div>

          <p className="mt-4 border-t border-slate-200 pt-3 text-[11px] leading-relaxed text-slate-500">
            {SV.nota} · Trabajo del {EQUIPO.semillero}, {EQUIPO.universidad}. Fallecidos: ANSV,
            conjunto rs3u-8r4q de datos.gov.co. Tránsito: serie histórica de volúmenes de tránsito
            de INVÍAS, estaciones 243 y 244, y conjunto 8yi9-t44c de la ANI para el peaje Cocora.
          </p>
        </Acordeon>

      </div>
    </section>
  );
};
