'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Mountain, Download } from 'lucide-react';
import {
  GEO, TRAZADO, PLAN_ACCION, EQUIPO,
  ETIQUETA_MARCA, COLOR_MARCA, type Dato, type Marca,
} from '@/data/proyecto';
import { METODO_OE } from '@/data/metodo_oe';
import ComoSeHizo from './ComoSeHizo';
import { PerfilOE1, CoberturaOE1 } from './graficos/GraficosOE1';

/* Chip de marca de origen — mismo patrón visual que la ficha técnica del sitio. */
const ChipMarca: React.FC<{ marca: Marca }> = ({ marca }) => (
  <span
    title={ETIQUETA_MARCA[marca]}
    className={`shrink-0 text-[9px] font-bold px-1.5 py-0.5 rounded border ${COLOR_MARCA[marca]}`}
  >
    {marca}
  </span>
);

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

/* Gráficos del objetivo. Cada uno sustituye a la lámina PNG que ocupaba su
   lugar: la lámina sigue siendo el entregable y queda enlazada para descarga.
   La curva se dibuja sobre 401 puntos que incluyen el de cobertura máxima, de
   modo que pasa por la cifra que rotula. Las cifras agregadas —media y rangos—
   siguen siendo del cálculo sobre 1.500 puntos; el pie de cada gráfico lo dice. */
const GRAFICOS = [
  {
    id: 'perfil',
    titulo: 'Perfil longitudinal del terreno y de la rasante',
    pie: 'Cota del terreno sobre el eje del trazado y rasante de pendiente constante entre portales, con la cobertura resultante punto a punto. La curva se dibuja sobre 401 puntos remuestreados del cálculo sobre 1.500, incluido el punto de cobertura máxima: el pico rotulado es un punto real de la curva. La cobertura media se promedia sobre los 1.500. Fuente del terreno: Copernicus DEM GLO-30 (ESA/Airbus), ~30 m.',
    lamina: '/oe1/perfil_longitudinal.png',
  },
  {
    id: 'cobertura',
    titulo: 'Cobertura sobre la clave del túnel',
    pie: 'Espesor de roca sobre el túnel a lo largo del trazado y su distribución por rangos, insumo para la selección del método de excavación en el objetivo específico 4. La clasificación de rangos es propia del semillero, no una norma. La curva pasa por el máximo rotulado; la media y los porcentajes por rango se calculan sobre los 1.500 puntos. Fuente del terreno: Copernicus DEM GLO-30.',
    lamina: '/oe1/cobertura_tunel.png',
  },
] as const;

/* La lámina de trazado se conserva como imagen: es un mapa compuesto, no una
   serie que el navegador pueda volver a dibujar. El relieve interactivo del
   corredor vive en la sección del mapa. */
const LAMINA_MAPA = {
  src: '/oe1/mapa_trazado.jpg', w: 1800, h: 979,
  titulo: 'Lámina de trazado sobre el área de estudio',
  pie: 'Trazado preliminar entre portales sobre el relieve sombreado de Ibagué, Cajamarca y Calarcá, con la vía actual (Ruta 40) y mapas de localización. Lámina con formato institucional, exportada a 1.800 px de ancho para la web por Comun/exportar_laminas_web.py. Fuente del relieve: Copernicus DEM GLO-30. Vía: © colaboradores de OpenStreetMap.',
};

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

export const SintesisOE1: React.FC = () => {
  const oe1 = PLAN_ACCION.find((o) => o.id === 'oe1');
  if (!oe1) return null;

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

        </div>

        {/* 3. Láminas */}
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

              {g.id === 'perfil' ? <PerfilOE1 /> : <CoberturaOE1 />}

              <div className="mt-4 flex flex-col gap-3 border-t border-slate-200 pt-3 sm:flex-row sm:items-start sm:justify-between">
                <p className="max-w-3xl text-[11px] leading-relaxed text-slate-500">{g.pie}</p>
                <a
                  href={g.lamina}
                  download
                  className="inline-flex shrink-0 items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-[11px] font-semibold text-uni-600 transition-colors hover:border-uni-300 hover:text-uni-700"
                >
                  <Download className="h-3.5 w-3.5 shrink-0" />
                  Descargar la lámina (PNG)
                </a>
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
            <p className="mt-3 text-[11px] leading-relaxed text-slate-500">{LAMINA_MAPA.pie}</p>
          </motion.figure>
        </div>

        {/* 4. Método reproducible, plegado: es el respaldo, no la portada del objetivo */}
        <div className="mb-4">
        <ComoSeHizo
          porQue={METODO_OE.oe1.porQue}
          paraQue={METODO_OE.oe1.paraQue}
          como={[]}
          noAfirma={[
            `El DEM tiene un error medio absoluto de ${GEO.errorDEM.valor} contra las cotas de cascos ` +
              'urbanos, del orden de un píxel. El trazado es de nivel conceptual, no un levantamiento topográfico.',
            'La ubicación de los portales responde a un criterio geométrico, no geotécnico: falta cruzarla ' +
              'con la susceptibilidad a movimientos en masa, que es el objetivo específico 3.',
            ...METODO_OE.oe1.noAfirma,
          ]}
          resumen="El modelo de elevación, la localización de los portales, el criterio de la rasante y las limitaciones declaradas."
        >
          <div className="space-y-3">
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
        </ComoSeHizo>
        </div>

        <p className="text-[11px] text-slate-500 leading-relaxed">
          {GEO.nota} · Trabajo del {EQUIPO.semillero}, {EQUIPO.universidad}. Criterio de pendiente
          máxima ({TRAZADO.pendienteCriterio.valor}): hipótesis del semillero, la ponencia no la declara.
        </p>

      </div>
    </section>
  );
};
