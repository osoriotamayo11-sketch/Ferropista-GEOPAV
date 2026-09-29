'use client';

/**
 * SintesisOE5 — la sección del objetivo específico 5, en un solo hilo:
 * la respuesta corta, cuánto tránsito hay, dónde ocurren los siniestros, qué
 * tan grave es el corredor antes y después del túnel de La Línea, y —plegados,
 * porque son el respaldo y no la portada— cómo se hizo y qué no afirma este
 * objetivo. Ninguna cifra se escribe a mano: salen de `SEGURIDAD_VIAL` en
 * `proyecto.ts`, de `siniestralidad_oe5.json` (vía GraficosOE5) y de
 * `mapas_oe5.json` (vía LaminasOE5 y el rango post-túnel de aquí abajo).
 */

import React from 'react';
import {
  ShieldAlert, Gauge, AlertTriangle,
} from 'lucide-react';
import {
  SEGURIDAD_VIAL as SV, PLAN_ACCION, EQUIPO,
  ETIQUETA_MARCA, COLOR_MARCA, type Dato, type Marca,
} from '@/data/proyecto';
import { METODO_OE } from '@/data/metodo_oe';
import mapas from '@/data/mapas_oe5.json';
import Acordeon from './Acordeon';
import ComoSeHizo from './ComoSeHizo';
import DescargaArchivo from './DescargaArchivo';
import { ExposicionCocora, TransitoInvias } from './graficos/GraficosOE5';
import { MapaSiniestralidadOE5, PrensaMicrodatoOE5 } from './graficos/LaminasOE5';

const es = (v: number, d = 0) =>
  v.toLocaleString('es-CO', { minimumFractionDigits: d, maximumFractionDigits: d });

/* Mismo chip de marca de origen que el resto del sitio. */
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

/* Rango post-túnel, construido aquí porque su fuente es mapas_oe5.json (el
   microdato ANSV 2021 – mar 2026), no proyecto.ts: es la salida directa de
   procesar_microdato_ANSV_OE5.py, igual que el resto de cifras que ese
   archivo alimenta en LaminasOE5. Marca H: es cota inferior, no comparable. */
const TASA_POST_TUNEL = mapas.microdato.tasa_post_tunel;
const DATO_TASA_POST_TUNEL: Dato = {
  valor: `${es(TASA_POST_TUNEL.tasa_H1, 2)} – ${es(TASA_POST_TUNEL.tasa_H2, 2)}`,
  marca: 'H',
  fuente: 'ANSV, oficio 20265000140371 (microdato georreferenciado 2021 – mar 2026); INVÍAS y peaje Cajamarca para el tránsito supuesto',
  nota: 'Cota inferior, no comparable: subregistro de georreferenciación (2 de 8 fatales de prensa) y sin aforo del paso después de 2019.',
};

export const SintesisOE5: React.FC = () => {
  const oe5 = PLAN_ACCION.find((o) => o.id === 'oe5');
  if (!oe5) return null;

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

        {/* 1. La respuesta corta */}
        <div className="rounded-2xl bg-white border border-slate-200 p-5 sm:p-7 mb-6">
          <div className="flex items-center gap-2 mb-1.5">
            <Gauge className="w-4 h-4 text-uni-600" />
            <h3 className="text-lg font-bold text-uni-900">La respuesta corta</h3>
          </div>
          <p className="text-xs text-slate-500 mb-5 max-w-3xl leading-relaxed">
            La unidad estándar es <strong className="text-slate-700">fallecidos por cada 100
            millones de vehículos-kilómetro</strong>. La tasa de hoy es la línea base 2015–2019,
            anterior al Túnel de La Línea; el rango 2021–2025 es apenas una cota inferior y no se
            compara con ella.
          </p>
          <div className="grid md:grid-cols-3 gap-4">
            <Tasa titulo="Tasa del paso · 2015–2019" pie="Fallecidos por 100 M veh-km" dato={SV.tasaPaso} />
            <Tasa titulo="Fallecidos del paso · 2015–2019" pie="Cuatro sectores críticos de la ANSV" dato={SV.fallecidosPaso} />
            <Tasa titulo="Tasa del paso · 2021–2025" pie="Rango, cota inferior, no comparable" dato={DATO_TASA_POST_TUNEL} tenue />
          </div>
        </div>

        {/* 2. Cuánto tránsito hay */}
        <div className="rounded-2xl bg-white border border-slate-200 p-5 sm:p-7 mb-6">
          <h3 className="text-lg font-bold text-uni-900 mb-1.5">Cuánto tránsito hay</h3>
          <p className="text-xs text-slate-500 mb-5 max-w-3xl leading-relaxed">
            El denominador de la tasa. La serie histórica de INVÍAS pone el aforo en el mismo
            periodo que los fallecidos; el peaje Cocora mide la exposición de hoy, cuatro años
            después del último fallecido registrado.
          </p>

          <div className="space-y-8">
            <div>
              <div className="mb-3 flex items-start justify-between gap-3">
                <h4 className="text-sm font-bold text-uni-900">Exposición medida en el peaje Cocora</h4>
                <ChipMarca marca="CP" />
              </div>
              <ExposicionCocora />
            </div>
            <div>
              <div className="mb-3 flex items-start justify-between gap-3">
                <h4 className="text-sm font-bold text-uni-900">Veinte años de tránsito medido por INVÍAS</h4>
                <ChipMarca marca="CP" />
              </div>
              <TransitoInvias />
            </div>
          </div>

          <div className="mt-7 border-t border-slate-200 pt-6">
            <h4 className="text-sm font-bold text-uni-900 mb-1.5">Las entradas del cálculo</h4>
            <p className="text-xs text-slate-500 mb-4 max-w-3xl leading-relaxed">
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
        </div>

        {/* 3. Dónde ocurren */}
        <div className="rounded-2xl bg-white border border-slate-200 p-5 sm:p-7 mb-6">
          <div className="flex items-center gap-2 mb-1.5">
            <ShieldAlert className="w-4 h-4 text-uni-600" />
            <h3 className="text-lg font-bold text-uni-900">Dónde ocurren</h3>
          </div>
          <p className="text-xs text-slate-500 mb-5 max-w-3xl leading-relaxed">
            Dos fuentes, dos periodos, un mismo corredor: los seis sectores críticos que la ANSV
            identificó con el estadístico Getis-Ord Gi* para 2015–2019, y el microdato
            georreferenciado que entregó por solicitud para 2021 – marzo de 2026.
          </p>
          <MapaSiniestralidadOE5 />

          <div className="mt-4 flex flex-wrap gap-2.5">
            <DescargaArchivo
              href="/oe5/graficos_siniestralidad.jpg"
              etiqueta="Descargar sectores críticos y detalle del descenso a Calarcá"
              formato="JPG"
            />
            <DescargaArchivo
              href="/oe5/densidad_lineal.jpg"
              etiqueta="Descargar la densidad lineal del microdato ANSV"
              formato="JPG"
            />
          </div>

          <div className="mt-4">
            <Acordeon
              titulo="¿Están en el anexo los fatales conocidos por prensa?"
              resumen="Cruce entre el microdato de la ANSV y los siniestros fatales que documentó la prensa entre 2022 y 2025."
              icono={<AlertTriangle className="h-5 w-5 text-acred-600" />}
              contador={`${mapas.microdato.resumen.prensa.en_anexo} de ${mapas.microdato.resumen.prensa.total}`}
              tono="gris"
            >
              <PrensaMicrodatoOE5 />
            </Acordeon>
          </div>
        </div>

        {/* 4. Qué tan grave, antes y después del túnel (2020) */}
        <div className="rounded-2xl bg-white border border-slate-200 p-5 sm:p-7 mb-6">
          <h3 className="text-lg font-bold text-uni-900 mb-1.5">Qué tan grave, antes y después del túnel (2020)</h3>
          <p className="text-xs text-slate-500 mb-5 max-w-3xl leading-relaxed">
            Contar muertos sin dividir por exposición es contar goles sin saber cuántos partidos se
            jugaron. Las dos tasas 2015–2019 usan los mismos 42 fallecidos y difieren solo en el
            denominador; el rango 2021–2025 es harina de otro costal.
          </p>
          <div className="grid md:grid-cols-3 gap-4 mb-6">
            <Tasa titulo="Corredor completo · 74 km · 2015–2019" pie="42 fallecidos · TPD 6.820 · 5 años" dato={SV.tasaCorredor} />
            <Tasa titulo="Solo el paso · 45 km · 2015–2019" pie="42 fallecidos · TPD 6.676 · 5 años" dato={SV.tasaPaso} />
            <Tasa titulo="Solo el paso · 2021–2025" pie="Rango, cota inferior" dato={DATO_TASA_POST_TUNEL} tenue />
          </div>
          <div className="space-y-3 max-w-4xl text-xs leading-relaxed text-slate-600">
            <p>{SV.limites[1]}</p>
            <p>{SV.limites[4]}</p>
          </div>
        </div>

        {/* 5. Cómo se hizo, y qué no afirma: plegado, es el respaldo, no la
               portada del objetivo. Incluye las cuatro mediciones del
               corredor, que no son una serie temporal. */}
        <div className="mb-4">
          <ComoSeHizo
            porQue={METODO_OE.oe5.porQue}
            paraQue={METODO_OE.oe5.paraQue}
            como={METODO_OE.oe5.como}
            noAfirma={SV.limites}
            resumen="Las tres fuentes, la fórmula de la tasa y las cuatro mediciones del mismo corredor."
          >
            <div className="space-y-3">
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

            <div className="mt-5">
              <h4 className="text-sm font-bold text-uni-900 mb-1.5">Cuatro mediciones del mismo corredor</h4>
              <p className="text-xs text-slate-500 mb-4 leading-relaxed">
                <strong className="text-slate-700">No son una serie temporal.</strong> Son cuatro
                puntos de medición con criterios de clasificación distintos. La clase «camiones» de
                la serie por estación de INVÍAS incluye los de dos ejes, que en peaje caen en
                categoría II: por eso su participación de carga pesada es sistemáticamente mayor.
                Las dos lecturas no se promedian.
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
                          <span className="font-bold text-uni-900">{m.tpd.toLocaleString('es-CO')}</span> veh/día
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
          </ComoSeHizo>
        </div>

        <p className="text-[11px] leading-relaxed text-slate-500">
          {SV.nota} · Trabajo del {EQUIPO.semillero}, {EQUIPO.universidad}. Fallecidos: ANSV,
          conjunto rs3u-8r4q de datos.gov.co. Tránsito: serie histórica de volúmenes de tránsito
          de INVÍAS, estaciones 243 y 244, y conjunto 8yi9-t44c de la ANI para el peaje Cocora.
        </p>

      </div>
    </section>
  );
};
