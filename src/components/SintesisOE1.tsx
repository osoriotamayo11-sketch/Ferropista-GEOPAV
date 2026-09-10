'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  Mountain, CheckCircle2, Circle, Loader2, ExternalLink, FolderOpen,
  Download, Route, AlertTriangle,
} from 'lucide-react';
import {
  GEO, TRAZADO, PLAN_ACCION, EQUIPO,
  ETIQUETA_MARCA, COLOR_MARCA, type Dato, type Marca, type EstadoItem,
} from '@/data/proyecto';

/* Chip de marca de origen — mismo patrón visual que la ficha técnica del sitio. */
const ChipMarca: React.FC<{ marca: Marca }> = ({ marca }) => (
  <span
    title={ETIQUETA_MARCA[marca]}
    className={`shrink-0 text-[9px] font-bold px-1.5 py-0.5 rounded border ${COLOR_MARCA[marca]}`}
  >
    {marca}
  </span>
);

const ESTADO_UI: Record<EstadoItem, { texto: string; clase: string; Icono: React.ElementType }> = {
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

/* Láminas: copias para web en public/oe1/. Dimensiones intrínsecas para no provocar
   reflow; el CSS las hace responsivas (w-full h-auto). */
const LAMINAS = [
  {
    src: '/oe1/perfil_longitudinal.png', w: 2700, h: 1120,
    titulo: 'Perfil longitudinal del terreno y de la rasante',
    pie: 'Cota del terreno sobre el eje del trazado y rasante de pendiente constante entre portales, con la cobertura resultante punto a punto. Fuente del terreno: Copernicus DEM GLO-30 (ESA/Airbus), ~30 m.',
  },
  {
    src: '/oe1/cobertura_tunel.png', w: 2700, h: 1380,
    titulo: 'Cobertura sobre la clave del túnel',
    pie: 'Espesor de roca sobre el túnel a lo largo del trazado y su distribución por rangos. La clasificación de rangos es propia del semillero, no una norma. Fuente del terreno: Copernicus DEM GLO-30.',
  },
  {
    src: '/oe1/mapa_OE1_layout.png', w: 1800, h: 1273,
    titulo: 'Lámina de trazado sobre el área de estudio',
    pie: 'Trazado preliminar entre portales sobre el relieve sombreado de Ibagué, Cajamarca y Calarcá, con mapas de localización. Reducida a 1.800 px de ancho para la web; el script de reducción está en public/oe1/. Fuente del relieve: Copernicus DEM GLO-30.',
  },
];

const TESELAS_DEM = [
  {
    etiqueta: 'Tesela N04 W075 (.tif)',
    url: 'https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N04_00_W075_00_DEM/Copernicus_DSM_COG_10_N04_00_W075_00_DEM.tif',
  },
  {
    etiqueta: 'Tesela N04 W076 (.tif)',
    url: 'https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N04_00_W076_00_DEM/Copernicus_DSM_COG_10_N04_00_W076_00_DEM.tif',
  },
];

/* Carpetas de evidencia en Drive, una por actividad del OE 1 (mismo orden). */
const DRIVE_URLS = [
  'https://drive.google.com/drive/folders/1CxNK5UbqVdSd2U4ztWD9Jd9RdPOhsmmp',
  'https://drive.google.com/drive/folders/15gj-oMTUpBU6aGaq8fbCgJhXUqqE35is',
  'https://drive.google.com/drive/folders/1JIdzRzPqSSSQ796kyU_DwZKBn7r9mVU5',
  'https://drive.google.com/drive/folders/1yAHR7WxP4S3KajXwSPL0Spq1r9-2Qool',
  'https://drive.google.com/drive/folders/1eG9D18st1T2Jxmj1b9gzXKLby_HClmTO',
];

export const SintesisOE1: React.FC = () => {
  const oe1 = PLAN_ACCION.find((o) => o.id === 'oe1');
  if (!oe1) return null;

  const evidencias = oe1.actividades.map((a, i) => ({ ...a, url: DRIVE_URLS[i] }));

  return (
    <section id="oe1" className="py-24 bg-white relative overflow-hidden border-t border-slate-200">
      <div className="absolute top-1/4 right-0 w-[500px] h-[400px] bg-blue-600/5 blur-[130px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-emerald-600/5 blur-[130px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">

        {/* Encabezado */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-gmae-600 text-xs font-semibold uppercase tracking-wider">
            <Mountain className="w-3.5 h-3.5" />
            <span>Objetivo específico 1 · Síntesis y evidencias</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-uni-900 tracking-tight">
            Topografía del trazado: objetivo cerrado
          </h2>
          <p className="text-base sm:text-lg text-slate-500 leading-relaxed">
            El primer objetivo del semillero — caracterizar el perfil del corredor con un modelo de
            elevación digital y definir el trazado preliminar del túnel — quedó completado. Aquí están
            las cifras que produjo, las láminas, el método para reproducirlo y las carpetas de evidencia.
          </p>
        </div>

        {/* 1. Estado del objetivo */}
        <div className="rounded-2xl bg-slate-50 border border-gmae-300/60 p-6 sm:p-8 mb-6">
          <div className="flex flex-wrap items-center gap-3 mb-4">
            <BadgeEstado estado={oe1.estado} />
            <span className="text-[11px] font-mono text-slate-500">{oe1.inicio} → {oe1.fin}</span>
            <span className="text-[11px] text-slate-500">· Responsable: {oe1.responsable}</span>
          </div>
          <p className="text-sm text-slate-700 leading-relaxed mb-5">{oe1.titulo}</p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-3">
            {oe1.actividades.map((a) => {
              const { Icono } = ESTADO_UI[a.estado];
              const tinte = a.estado === 'completado' ? 'text-gmae-600'
                : a.estado === 'en_curso' ? 'text-uni-600' : 'text-slate-400';
              return (
                <div key={a.n} className="rounded-xl bg-white border border-slate-200 p-3 space-y-1.5">
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

        {/* 2. Cifras clave desde GEO */}
        <div className="rounded-2xl bg-white border border-slate-200 p-5 sm:p-7 mb-6">
          <h3 className="text-lg font-bold text-uni-900 mb-1.5">Cifras que produjo el objetivo</h3>
          <p className="text-xs text-slate-500 mb-5 max-w-3xl leading-relaxed">
            Todas se leen de la fuente única de verdad del sitio. La marca indica el origen:
            cálculo propio del semillero (CP) o hipótesis de trabajo (H).
          </p>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <Cifra etiqueta="Longitud del alineamiento" dato={GEO.longitud} />
            <Cifra etiqueta="Pendiente de la rasante" dato={GEO.pendiente} />
            <Cifra etiqueta="Desnivel entre portales" dato={GEO.desnivel} />
            <Cifra etiqueta="Cota máxima del terreno" dato={GEO.cotaMaxTerreno} />
            <Cifra etiqueta="Cobertura máxima" dato={GEO.coberturaMax} />
            <Cifra etiqueta="Abscisa de la cobertura máxima" dato={GEO.coberturaMaxPk} />
            <Cifra etiqueta="Cobertura media" dato={GEO.coberturaMedia} />
            <Cifra etiqueta="Trazado con más de 700 m de cobertura" dato={GEO.pctCobertura700} />
            <Cifra etiqueta="Trazado con más de 1.200 m de cobertura" dato={GEO.pctCobertura1200} />
            <Cifra etiqueta="Error medio absoluto del DEM" dato={GEO.errorDEM} />
            <Cifra etiqueta="Tolerancia de cota adoptada" dato={GEO.toleranciaCota} />
            <Cifra etiqueta="Abscisas de la cartera" dato={GEO.nAbscisas} />
          </div>

          {/* Distribución de cobertura por rangos */}
          <div className="mt-6 pt-5 border-t border-slate-200">
            <div className="flex items-center gap-2 mb-3">
              <h4 className="text-sm font-bold text-slate-700">Distribución de la cobertura por rangos</h4>
              <ChipMarca marca="CP" />
              <span className="text-[10px] text-slate-400">sobre 1.500 puntos del perfil</span>
            </div>
            <div className="flex w-full h-10 rounded-lg overflow-hidden border border-slate-200">
              {GEO.distribucionCobertura.map((r, i) => {
                const tono = ['#cde2fb', '#9ec5f4', '#5598e7', '#2a78d6', '#184f95'][i];
                return (
                  <div
                    key={r.rango}
                    style={{ width: `${r.pct}%`, background: tono }}
                    className="flex items-center justify-center"
                    title={`${r.rango} · ${r.km.toLocaleString('es-CO')} km · ${r.pct.toLocaleString('es-CO')} %`}
                  >
                    {r.pct >= 8 && (
                      <span className={`text-[10px] font-bold ${i >= 3 ? 'text-white' : 'text-uni-900'}`}>
                        {r.pct.toLocaleString('es-CO')} %
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
            <div className="mt-3 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
              {GEO.distribucionCobertura.map((r, i) => (
                <div key={r.rango} className="flex items-start gap-2 text-[11px] text-slate-500">
                  <span
                    className="w-3 h-3 rounded-sm shrink-0 mt-0.5"
                    style={{ background: ['#cde2fb', '#9ec5f4', '#5598e7', '#2a78d6', '#184f95'][i] }}
                  />
                  <span>
                    <span className="font-semibold text-slate-600">{r.rango}</span><br />
                    {r.km.toLocaleString('es-CO')} km · {r.pct.toLocaleString('es-CO')} %
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 3. Láminas */}
        <div className="space-y-4 mb-6">
          {LAMINAS.map((l, i) => (
            <motion.figure
              key={l.src}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.4, delay: i * 0.05 }}
              className="rounded-2xl bg-white border border-slate-200 p-4 sm:p-5"
            >
              <figcaption className="flex items-start justify-between gap-3 mb-3">
                <h3 className="text-sm sm:text-base font-bold text-uni-900">{l.titulo}</h3>
                <ChipMarca marca="CP" />
              </figcaption>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={l.src}
                alt={l.titulo}
                width={l.w}
                height={l.h}
                loading="lazy"
                className="w-full h-auto rounded-lg border border-slate-200 bg-white"
              />
              <p className="text-[11px] text-slate-500 leading-relaxed mt-3">{l.pie}</p>
            </motion.figure>
          ))}
        </div>

        {/* 4. Método reproducible */}
        <div className="rounded-2xl bg-white border border-slate-200 p-5 sm:p-7 mb-6">
          <div className="flex items-center gap-2 mb-3">
            <Route className="w-4 h-4 text-uni-600" />
            <h3 className="text-lg font-bold text-uni-900">Cómo se hizo, y qué no afirma</h3>
          </div>
          <div className="space-y-3 text-xs text-slate-600 leading-relaxed max-w-3xl">
            <p>
              Se descargó el <strong className="text-uni-900">Copernicus DEM GLO-30</strong> (ESA/Airbus,
              ~30 m), un modelo de elevación de acceso libre y sin registro. Los portales se localizaron
              sobre el DEM buscando los píxeles a 950 y 1.450 msnm que declara la ponencia, con una
              tolerancia declarada de {GEO.toleranciaCota.valor}, y se escogió el par que minimiza la
              distancia entre ellos. El alineamiento es la <strong className="text-uni-900">geodésica
              sobre el elipsoide WGS 84</strong> entre portales, discretizada en 1.500 puntos. La rasante
              es una recta de <strong className="text-uni-900">pendiente constante</strong> entre las
              cotas de portal, y la cobertura es la diferencia entre el terreno y esa rasante en cada
              punto. El procesamiento completo es un script reproducible; el registro está en las
              carpetas de evidencia.
            </p>
          </div>

          <div className="mt-4 rounded-xl bg-amber-500/5 border border-amber-500/25 p-4">
            <div className="flex items-center gap-2 text-[11px] font-bold text-acred-600 uppercase tracking-wider mb-2">
              <AlertTriangle className="w-3.5 h-3.5" />
              Dos limitaciones que se declaran de entrada
            </div>
            <ul className="space-y-1.5 text-xs text-slate-600 leading-relaxed">
              <li>
                · El DEM tiene un error medio absoluto de {GEO.errorDEM.valor} contra las cotas de
                cascos urbanos, del orden de un píxel. El trazado es de nivel conceptual, no un
                levantamiento topográfico.
              </li>
              <li>
                · La ubicación de los portales responde a un criterio geométrico, no geotécnico:
                falta cruzarla con la susceptibilidad a movimientos en masa, que es el objetivo
                específico 3.
              </li>
            </ul>
          </div>

          <div className="mt-4">
            <p className="text-[11px] font-bold text-slate-600 uppercase tracking-wider mb-2">
              Teselas del DEM usadas (descarga directa)
            </p>
            <div className="flex flex-col sm:flex-row gap-2">
              {TESELAS_DEM.map((t) => (
                <a
                  key={t.url}
                  href={t.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-xs font-semibold text-uni-600 hover:text-uni-700 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2"
                >
                  <Download className="w-3.5 h-3.5 shrink-0" />
                  {t.etiqueta}
                </a>
              ))}
            </div>
            <p className="text-[10px] text-slate-400 mt-2">
              Copernicus DEM GLO-30 · ESA/Airbus · dominio del bucket público copernicus-dem-30m (AWS).
            </p>
          </div>
        </div>

        {/* 5. Evidencias en Drive */}
        <div className="rounded-2xl bg-slate-50 border border-slate-200 p-5 sm:p-7">
          <div className="flex items-center gap-2 mb-1.5">
            <FolderOpen className="w-4 h-4 text-gmae-600" />
            <h3 className="text-lg font-bold text-uni-900">Carpetas de evidencia</h3>
          </div>
          <p className="text-xs text-slate-500 mb-5 max-w-3xl leading-relaxed">
            Una carpeta por actividad, con los archivos de trabajo tal como se entregaron.
          </p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {evidencias.map((e) => (
              <a
                key={e.n}
                href={e.url}
                target="_blank"
                rel="noopener noreferrer"
                className="group flex items-start gap-3 rounded-xl bg-white border border-slate-200 p-4 hover:border-uni-300 transition-colors"
              >
                <FolderOpen className="w-4 h-4 text-gmae-600 shrink-0 mt-0.5" />
                <div className="min-w-0 flex-1">
                  <p className="text-[10px] font-mono text-slate-500">Actividad {e.n} · {e.formato}</p>
                  <p className="text-xs font-semibold text-slate-700 leading-snug mt-0.5">{e.entregable}</p>
                </div>
                <ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover:text-uni-600 shrink-0" />
              </a>
            ))}
          </div>
          <p className="text-[11px] text-slate-500 leading-relaxed border-t border-slate-200 pt-4 mt-5">
            {GEO.nota} · Trabajo del {EQUIPO.semillero}, {EQUIPO.universidad}. Criterio de pendiente
            máxima ({TRAZADO.pendienteCriterio.valor}): hipótesis del semillero, la ponencia no la declara.
          </p>
        </div>

      </div>
    </section>
  );
};
