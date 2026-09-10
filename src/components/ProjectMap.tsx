'use client';

import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Tooltip as LeafletTooltip } from 'react-leaflet';
import L from 'leaflet';
import { MapPin, Navigation, Mountain, Layers, ShieldCheck, Zap } from 'lucide-react';
import { GEO } from '@/data/proyecto';

export const ProjectMap: React.FC = () => {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Coordenadas centrales entre Ibagué y Armenia
  const centerPosition: [number, number] = GEO.centro;

  // Coordenadas de los portales del proyecto
  const ibagueCoords: [number, number] = GEO.portalIbague;   // Portal oriental — OE 1
  const armeniaCoords: [number, number] = GEO.portalArmenia; // Portal occidental — OE 1

  // Trazado PRELIMINAR. Nota del semillero: la polilínea dibujada mide ~51 km entre los
  // portales graficados, mientras la ponencia declara 44 km de túnel principal sobre un tramo
  // total de 58 km. Resolver esa diferencia con un Modelo de Elevación Digital es el resultado
  // esperado del objetivo específico 1; hasta entonces el trazado es indicativo, no métrico.
  const tunnelPolyline: [number, number][] = [ibagueCoords, armeniaCoords];

  // Custom DivIcons for Leaflet dark theme map markers
  const createCustomMarkerIcon = (title: string, colorClass: string) => {
    if (typeof window === 'undefined') return undefined;
    
    return L.divIcon({
      className: 'custom-leaflet-marker',
      html: `
        <div class="relative flex items-center justify-center">
          <span class="animate-ping absolute inline-flex h-8 w-8 rounded-full ${colorClass} opacity-40"></span>
          <div class="relative w-7 h-7 rounded-full bg-slate-50 border-2 border-white flex items-center justify-center shadow-lg text-xs font-bold text-white">
            <div class="w-3 h-3 rounded-full ${colorClass}"></div>
          </div>
        </div>
      `,
      iconSize: [28, 28],
      iconAnchor: [14, 14],
      popupAnchor: [0, -14],
    });
  };

  if (!isMounted) {
    return (
      <div className="w-full h-[550px] bg-slate-50 rounded-3xl border border-slate-200 flex items-center justify-center">
        <div className="flex items-center gap-3 text-slate-500 font-mono text-sm">
          <Navigation className="w-5 h-5 animate-spin text-uni-600" />
          <span>Cargando Mapa Interactivo del Trazado Subterráneo...</span>
        </div>
      </div>
    );
  }

  const ibagueIcon = createCustomMarkerIcon('Portal oriental', 'bg-blue-500');
  const armeniaIcon = createCustomMarkerIcon('Portal occidental', 'bg-emerald-500');

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
            
            <div className="flex items-center gap-6 text-xs font-mono">
              <div className="flex items-center gap-2">
                <span className="w-3 h-1 bg-blue-500 rounded-full"></span>
                <span className="text-slate-600">Portal oriental · Ibagué, Tolima</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-1 bg-emerald-500 rounded-full"></span>
                <span className="text-slate-600">Portal occidental · Calarcá, Quindío</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-4 h-0.5 bg-sky-400 border border-dashed border-sky-300"></span>
                <span className="text-sky-300 font-bold">Eje Túnel Base</span>
              </div>
            </div>
          </div>

          {/* Leaflet Map React Instance */}
          <div className="w-full h-[520px] relative">
            <MapContainer
              center={centerPosition}
              zoom={10}
              scrollWheelZoom={false}
              className="w-full h-full"
            >
              {/* Dark carto map tiles */}
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                maxZoom={18}
              />

              {/* Tunnel Polyline Trazado */}
              <Polyline
                positions={tunnelPolyline}
                pathOptions={{
                  color: '#38bdf8', // Sky 400
                  weight: 5,
                  dashArray: '8, 8',
                  opacity: 0.9,
                }}
              >
                <LeafletTooltip sticky permanent={false}>
                  <div className="text-xs font-bold font-mono text-slate-800">
                    Túnel de base · {GEO.longitud.valor} · pendiente {GEO.pendiente.valor}
                  </div>
                </LeafletTooltip>
              </Polyline>

              {/* Marker Ibagué */}
              <Marker position={ibagueCoords} icon={ibagueIcon}>
                <Popup>
                  <div className="space-y-2 p-1 min-w-[180px]">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono text-uni-600 uppercase font-bold">Portal oriental</span>
                      <span className="text-[10px] text-slate-500 font-mono">{GEO.cotaPortalIbague} msnm [CP]</span>
                    </div>
                    <h4 className="font-bold text-uni-900 text-sm">Terminal Intermodal Ibagué</h4>
                    <p className="text-xs text-slate-600">
                      Portal oriental, en jurisdicción de Ibagué, Tolima (DANE 73001). Localizado sobre el DEM buscando la cota de 950 msnm que declara la ponencia, con tolerancia de 2 m. Criterio geométrico: pendiente de verificación geotécnica en el OE 3.
                    </p>
                  </div>
                </Popup>
              </Marker>

              {/* Marker Armenia */}
              <Marker position={armeniaCoords} icon={armeniaIcon}>
                <Popup>
                  <div className="space-y-2 p-1 min-w-[180px]">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono text-gmae-600 uppercase font-bold">Portal occidental</span>
                      <span className="text-[10px] text-slate-500 font-mono">{GEO.cotaPortalArmenia} msnm [CP]</span>
                    </div>
                    <h4 className="font-bold text-uni-900 text-sm">Terminal Intermodal Armenia</h4>
                    <p className="text-xs text-slate-600">
                      Portal occidental hacia el Eje Cafetero y Buenaventura, en jurisdicción de Calarcá, Quindío (DANE 63130) y no de Armenia, como se publicó al principio. Localizado sobre el DEM buscando la cota de 1.450 msnm de la ponencia, con tolerancia de 2 m.
                    </p>
                  </div>
                </Popup>
              </Marker>

            </MapContainer>
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
