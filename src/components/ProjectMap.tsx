'use client';

/**
 * ProjectMap — seccion del trazado del objetivo especifico 1.
 *
 * El visor paso de un mapa Leaflet con teselas de CARTO a un relieve 3D
 * levantado del propio modelo de elevacion del proyecto. Motivos:
 *   1. Las teselas `basemaps.cartocdn.com` dejaron de servirse sin llave de
 *      API y estampaban la marca «API KEY REQUIRED» sobre todo el mapa.
 *   2. El trazado de un tunel de base se entiende por el relieve que atraviesa,
 *      y ese relieve es justamente el producto del objetivo especifico 1.
 *
 * El encabezado, la barra de estado y el pie de esta seccion se conservan.
 */

import React from 'react';
import dynamic from 'next/dynamic';
import { Navigation, Mountain, ShieldCheck, Zap, MousePointer2, Move3d } from 'lucide-react';
import { GEO } from '@/data/proyecto';

const Terreno3D = dynamic(() => import('./3d/Terreno3D'), {
  ssr: false,
  loading: () => (
    <div className="flex h-[560px] w-full items-center justify-center bg-slate-50">
      <div className="flex items-center gap-3 font-mono text-sm text-slate-500">
        <Navigation className="h-5 w-5 animate-spin text-uni-600" />
        <span>Cargando el relieve del corredor…</span>
      </div>
    </div>
  ),
});

export const ProjectMap: React.FC = () => {
  return (
    <section id="mapa" className="py-24 bg-white/40 relative overflow-hidden border-t border-slate-200">
      {/* Glow ambient background */}
      <div className="absolute top-0 right-1/3 w-[600px] h-[500px] bg-blue-600/10 blur-[130px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">

        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-14">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-gmae-600 text-xs font-semibold uppercase tracking-wider">
            <Navigation className="w-4 h-4 text-gmae-600" />
            <span>Trazado Subterráneo de Alta Cota</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-uni-900 tracking-tight">
            Geolocalización e Interconexión Regional
          </h2>
          <p className="text-base sm:text-lg text-slate-600 leading-relaxed font-light">
            Alineamiento de <strong className="text-uni-900 font-medium">{GEO.longitud.valor}</strong> entre el portal oriental, en Ibagué (Tolima), y el portal occidental, en Calarcá (Quindío), calculado sobre el modelo de elevación digital en el objetivo específico 1. La ponencia nombra los extremos del corredor «Ibagué» y «Armenia»; la jurisdicción de cada portal se verificó contra la capa de municipios del IGAC. La ponencia declara un corredor total de 58 km con tramos a cielo abierto entre siete túneles; lo que se dibuja aquí es el túnel de base continuo.
          </p>
        </div>

        {/* Map Container Wrapper */}
        <div className="relative rounded-3xl overflow-hidden border border-slate-200 shadow-2xl bg-slate-50">

          {/* Map Status Bar Header */}
          <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-gmae-500 animate-pulse"></div>
              <span className="text-xs font-mono font-bold text-uni-900 tracking-wide">
                TRAZADO CALCULADO CON DEM — OBJETIVO ESPECÍFICO 1
              </span>
            </div>

            {/* Aqui iba una leyenda que repetia palabra por palabra las convenciones
                dibujadas dentro del propio visor. Se retira: la leyenda vive en el
                visor, junto a lo que nombra. En su lugar, como usarlo. */}
            <div className="flex flex-wrap items-center justify-center gap-x-5 gap-y-1.5 font-mono text-[11px] text-slate-500">
              <span className="flex items-center gap-1.5">
                <MousePointer2 className="h-3.5 w-3.5 text-slate-400" />
                Arrastra para girar
              </span>
              <span className="flex items-center gap-1.5">
                <Move3d className="h-3.5 w-3.5 text-slate-400" />
                Rueda para acercar
              </span>
              <span className="text-slate-400">Convenciones dentro del visor</span>
            </div>
          </div>

          {/* Relieve 3D levantado del DEM */}
          <Terreno3D height={560} />

          {/* Fichas de los portales, antes en los globos del mapa */}
          <div className="grid gap-4 border-t border-slate-200 bg-white/70 p-6 sm:grid-cols-2">
            <div className="space-y-2 rounded-xl border border-slate-200 bg-white p-4">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[10px] font-bold uppercase text-uni-600">Portal oriental</span>
                <span className="font-mono text-[10px] text-slate-500">{GEO.cotaPortalIbague} msnm [CP]</span>
              </div>
              <h4 className="text-sm font-bold text-uni-900">Portal de Ibagué</h4>
              <p className="text-xs leading-relaxed text-slate-600">
                Portal oriental, en jurisdicción de Ibagué, Tolima (DANE 73001). Localizado sobre el DEM buscando la cota de 950 msnm que declara la ponencia, con tolerancia de 2 m. Criterio geométrico: pendiente de verificación geotécnica en el OE 3.
              </p>
            </div>

            <div className="space-y-2 rounded-xl border border-slate-200 bg-white p-4">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[10px] font-bold uppercase text-gmae-600">Portal occidental</span>
                <span className="font-mono text-[10px] text-slate-500">{GEO.cotaPortalArmenia} msnm [CP]</span>
              </div>
              <h4 className="text-sm font-bold text-uni-900">Portal de Calarcá</h4>
              <p className="text-xs leading-relaxed text-slate-600">
                Portal occidental hacia el Eje Cafetero y Buenaventura, en jurisdicción de Calarcá, Quindío (DANE 63130) y no de Armenia, como se publicó al principio. Localizado sobre el DEM buscando la cota de 1.450 msnm de la ponencia, con tolerancia de 2 m.
              </p>
            </div>
          </div>

          {/* Map Footer Information */}
          <div className="bg-slate-50 p-6 border-t border-slate-200 grid sm:grid-cols-3 gap-4 text-xs text-slate-600">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20 text-uni-600">
                <Mountain className="w-4 h-4" />
              </div>
              <div>
                <span className="text-slate-500 block font-mono text-[11px]">Desnivel entre portales</span>
                <span className="font-bold text-uni-900">{GEO.desnivel.valor} — pendiente {GEO.pendiente.valor} [CP]</span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-gmae-600">
                <Zap className="w-4 h-4" />
              </div>
              <div>
                <span className="text-slate-500 block font-mono text-[11px]">Tiempo de cruce</span>
                <span className="font-bold text-uni-900">70 min de ciclo total (dia. 23)</span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-sky-500/10 border border-sky-500/20 text-uni-500">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <div>
                <span className="text-slate-500 block font-mono text-[11px]">Longitud del alineamiento</span>
                <span className="font-bold text-uni-900">{GEO.longitud.valor} · pendiente {GEO.pendiente.valor}</span>
              </div>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
};
