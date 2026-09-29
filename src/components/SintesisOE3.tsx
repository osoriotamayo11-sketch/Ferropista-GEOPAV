'use client';

/**
 * SintesisOE3 — la sección del objetivo específico 3 en la portada.
 *
 * Sin tarjeta-resumen ni carpetas de evidencia: eso vive en el Plan de Acción
 * (`PlanDeAccion.tsx`). Esta sección presenta lo que el OE 3 ya produjo: la
 * ficha de cada portal (leída de `src/data/oe3_portales.json`), un mapa
 * interactivo por portal (`MapaPortalOE3`, que carga `public/data/oe3_mapas.json`
 * con fetch) y las descargas.
 *
 * Ningún número se escribe a mano aquí: todo sale del JSON.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Mountain, FileText, MapPin } from 'lucide-react';
import { PLAN_ACCION } from '@/data/proyecto';
import { METODO_OE } from '@/data/metodo_oe';
import oe3Data from '@/data/oe3_portales.json';
import { MapaPortalOE3 } from '@/components/graficos/MapasOE3';
import { VisorGeologiaOE3 } from '@/components/graficos/VisorGeologiaOE3';
import ComoSeHizo from './ComoSeHizo';
import DescargaArchivo from './DescargaArchivo';

type Portal = (typeof oe3Data.portales)[number];

const ESTADO_TEXTO: Record<string, string> = {
  completado: 'completado',
  en_curso: 'en curso',
  pendiente: 'pendiente',
};

const es = (v: number, d = 0) =>
  v.toLocaleString('es-CO', { minimumFractionDigits: d, maximumFractionDigits: d });

/* Códigos de susceptibilidad a movimientos en masa (SGC): 1 muy baja … 5 muy alta. */
const SUSMM_TEXTO: Record<number, string> = {
  1: 'muy baja', 2: 'baja', 3: 'media', 4: 'alta', 5: 'muy alta',
};
const textoSusceptibilidad = (codigos: readonly number[]) => {
  const texto = (c: number) => SUSMM_TEXTO[c] ?? String(c);
  const [primero, ...resto] = codigos;
  if (resto.length === 0) return `susceptibilidad ${texto(primero)}`;
  return `susceptibilidad ${texto(primero)}, en el límite con ${resto.map(texto).join(', ')}`;
};

/* Marca local: en el OE 3 el origen no es la ponencia sino la cartografía del
   SGC, así que no se reutiliza el chip global (su tooltip dice «dato de la
   ponencia», que aquí sería falso). */
type MarcaOE3 = 'F' | 'CP';
const CHIP_OE3: Record<MarcaOE3, { texto: string; clase: string }> = {
  F: { texto: 'Dato del Servicio Geológico Colombiano', clase: 'bg-emerald-500/10 text-emerald-700 border-emerald-500/30' },
  CP: { texto: 'Cálculo propio del semillero', clase: 'bg-blue-500/10 text-blue-700 border-blue-500/30' },
};
const ChipOE3: React.FC<{ marca: MarcaOE3 }> = ({ marca }) => {
  const { texto, clase } = CHIP_OE3[marca];
  return (
    <span title={texto} className={`shrink-0 text-[9px] font-bold px-1.5 py-0.5 rounded border ${clase}`}>
      {marca}
    </span>
  );
};

/* Fila etiqueta/valor con su marca, para no repetir el mismo layout doce veces. */
const Fila: React.FC<{ etiqueta: string; marca: MarcaOE3; children: React.ReactNode }> = ({
  etiqueta, marca, children,
}) => (
  <div className="flex items-start justify-between gap-3 py-2 border-b border-slate-100 last:border-0">
    <div className="min-w-0">
      <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-500">{etiqueta}</p>
      <div className="text-xs text-slate-700 leading-relaxed">{children}</div>
    </div>
    <ChipOE3 marca={marca} />
  </div>
);

const TarjetaPortal: React.FC<{ portal: Portal }> = ({ portal: p }) => {
  const altaPct = p.amenaza_3km_pct.Alta;
  const distAlta = p.amenaza_alta_dist_m;

  return (
    <div className="rounded-2xl bg-white border border-slate-200 p-5 sm:p-6 space-y-1">
      <div className="flex items-start justify-between gap-3 pb-3 mb-1 border-b border-slate-200">
        <div>
          <h4 className="text-base font-bold text-uni-900">{p.nombre}</h4>
          <p className="text-xs text-slate-500">{p.municipio} · {es(p.cota_msnm, 1)} msnm</p>
        </div>
        <MapPin className="w-4 h-4 text-uni-600 shrink-0 mt-1" />
      </div>

      <Fila etiqueta="Unidad en la plancha geológica" marca="F">
        <span className="font-semibold">{p.unidad_plancha.plancha}</span>
        <p className="text-slate-500">{p.unidad_plancha.texto}</p>
      </Fila>

      <Fila etiqueta="Unidad 1:1.000.000" marca="F">
        <span className="font-mono font-semibold">{p.unidad_1M.simbolo}</span> · {p.unidad_1M.edad}
      </Fila>

      <Fila etiqueta="Falla más cercana" marca="F">
        {p.falla_mas_cercana.nombre === '(sin nombre)' ? 'Falla sin nombre' : p.falla_mas_cercana.nombre}
        {p.falla_mas_cercana.tipo !== 'Falla' && <> ({p.falla_mas_cercana.tipo.toLowerCase()})</>}
        {' '}·{' '}
        <span className="font-semibold">{es(p.falla_mas_cercana.dist_km, 1)} km</span>
      </Fila>

      <Fila etiqueta="NSR-10 — zonificación sísmica del municipio" marca="F">
        Aa = <span className="font-semibold">{es(p.nsr10.Aa, 2)}</span> · Av ={' '}
        <span className="font-semibold">{es(p.nsr10.Av, 2)}</span> · zona {p.nsr10.zona}
      </Fila>

      <Fila etiqueta="Amenaza por movimientos en masa en el punto" marca="F">
        <span className="font-semibold">{p.amenaza_punto}</span>
        {' '}· {textoSusceptibilidad(p.susceptibilidad_punto)}
      </Fila>

      <Fila etiqueta="Amenaza alta en el círculo de 3 km" marca="CP">
        <span className="font-semibold">{es(altaPct, 1)} %</span> del área
        {distAlta != null && <> · a {es(distAlta)} m del punto más cercano</>}
      </Fila>

      <Fila etiqueta="Eventos SIMMA en el círculo de 3 km" marca="CP">
        <span className="font-semibold">{p.inventario_simma_3km}</span>
      </Fila>

      <Fila etiqueta="Pendiente del entorno (250 m)" marca="CP">
        media <span className="font-semibold">{es(p.pendiente_250m.media, 1)}°</span> · p90{' '}
        <span className="font-semibold">{es(p.pendiente_250m.p90, 1)}°</span> ·{' '}
        {es(p.pendiente_250m.pct_mayor_25, 1)} % del entorno {'>'} 25°
      </Fila>

      <Fila etiqueta="Distancia a la vía actual (Ruta 40)" marca="CP">
        <span className="font-semibold">{es(p.dist_via_actual_km, 1)} km</span>
      </Fila>
    </div>
  );
};

export const SintesisOE3: React.FC = () => {
  const oe3 = PLAN_ACCION.find((o) => o.id === 'oe3');
  if (!oe3) return null;

  return (
    <section id="oe3" className="py-24 bg-slate-50 relative overflow-hidden border-t border-slate-200">
      <div className="absolute top-1/4 right-0 w-[500px] h-[400px] bg-amber-600/5 blur-[130px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-uni-600/5 blur-[130px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">

        {/* Encabezado */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-acred-600 text-xs font-semibold uppercase tracking-wider">
            <Mountain className="w-3.5 h-3.5" />
            <span>Objetivo específico 3 · Geotecnia de portales — {ESTADO_TEXTO[oe3.estado]}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-uni-900 tracking-tight">
            El terreno bajo los portales, antes de diseñar sobre él
          </h2>
          <p className="text-base sm:text-lg text-slate-500 leading-relaxed">
            El OE 3 no entrega capacidad portante de diseño: entrega rangos por unidad litológica,
            con sensibilidad, y las exploraciones de subsuelo que harían falta.
          </p>
        </div>

        {/* Fichas de portal */}
        <div className="grid gap-4 lg:grid-cols-2 mb-6">
          {oe3Data.portales.map((p) => (
            <TarjetaPortal key={p.id} portal={p} />
          ))}
        </div>

        {/* La roca en la boca del túnel: visor de geología 1:100.000, antes de
            los mapas de susceptibilidad. */}
        <div className="mb-6">
          <h3 className="mb-1.5 text-lg font-bold text-uni-900">La roca en la boca del túnel</h3>
          <p className="mb-5 max-w-3xl text-xs leading-relaxed text-slate-500">
            El recorte de la plancha geológica 1:100.000 del Servicio Geológico Colombiano en cada
            portal, con zoom y las unidades identificadas por su color en la leyenda impresa.
          </p>
          <VisorGeologiaOE3 />
          <div className="mt-4 flex flex-wrap gap-2.5">
            <DescargaArchivo
              href="/oe3/descargas/OE3_Act1_Lamina_geologia_portales.pdf"
              etiqueta="Descargar la lámina de geología de los portales"
              formato="PDF"
            />
            <DescargaArchivo
              href="/oe3/lamina_portales_geologia.jpg"
              etiqueta="Descargar la lámina de geología de los portales"
              formato="JPG"
            />
          </div>
        </div>

        {/* Documento completo de la actividad 1, tarjeta propia junto al visor */}
        <div className="mb-6 rounded-2xl border border-slate-200 bg-white p-5 sm:p-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-3">
              <FileText className="mt-0.5 h-5 w-5 shrink-0 text-uni-600" />
              <div>
                <h4 className="text-sm font-bold text-uni-900">Planos geológicos de los portales</h4>
                <p className="mt-0.5 max-w-xl text-xs leading-relaxed text-slate-500">
                  Documento completo de la actividad 1: 9 páginas con los planos, las tablas por
                  portal y la lectura geotécnica.
                </p>
              </div>
            </div>
            <DescargaArchivo
              href="/oe3/descargas/OE3_Act1_Planos_geologicos_portales.pdf"
              etiqueta="Descargar el documento"
              formato="PDF"
            />
          </div>
        </div>

        {/* Mapas interactivos de susceptibilidad, por portal */}
        <div className="mb-6">
          <div className="grid gap-4 lg:grid-cols-2">
            {oe3Data.portales.map((p, i) => (
              <motion.div
                key={p.id}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-60px' }}
                transition={{ duration: 0.4, delay: i * 0.05 }}
                className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-5"
              >
                <h3 className="mb-3 text-sm font-bold text-uni-900 sm:text-base">{p.nombre}</h3>
                <MapaPortalOE3 portalId={p.id} amenaza3kmPct={p.amenaza_3km_pct} />
              </motion.div>
            ))}
          </div>
          <div className="mt-4 flex flex-wrap gap-2.5">
            <DescargaArchivo
              href="/oe3/descargas/OE3_Act2_Mapa_susceptibilidad.pdf"
              etiqueta="Descargar el mapa de susceptibilidad"
              formato="PDF"
            />
            <DescargaArchivo
              href="/oe3/mapa_susceptibilidad.jpg"
              etiqueta="Descargar el mapa de susceptibilidad"
              formato="JPG"
            />
          </div>
        </div>

        {/* Cómo se hizo, y qué no afirma */}
        <div className="mb-4">
          <ComoSeHizo
            porQue={METODO_OE.oe3.porQue}
            paraQue={METODO_OE.oe3.paraQue}
            como={METODO_OE.oe3.como}
            noAfirma={METODO_OE.oe3.noAfirma}
            resumen="Cómo se ubicaron los portales sobre la cartografía del SGC, qué servicios en línea se consultaron y las limitaciones de trabajar a 1:100.000."
          />
        </div>

      </div>
    </section>
  );
};
