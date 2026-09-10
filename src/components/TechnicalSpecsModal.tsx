'use client';

import React from 'react';
import { X, ShieldCheck, HardHat, Mountain, Train, AlertTriangle } from 'lucide-react';
import {
  TRAZADO, EXCAVACION, OPERACION, HIPOTESIS_TECNICAS, VACIOS,
  FUENTE_PRIMARIA, EQUIPO, ETIQUETA_MARCA, COLOR_MARCA, type Dato,
} from '@/data/proyecto';

interface TechnicalSpecsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

/** Celda de especificación. Todo dato llega con su marca de origen visible. */
const Spec: React.FC<{ etiqueta: string; dato: Dato }> = ({ etiqueta, dato }) => (
  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
    <div className="flex items-start justify-between gap-2">
      <span className="text-xs text-slate-500 font-mono">{etiqueta}</span>
      <span
        title={`${ETIQUETA_MARCA[dato.marca]} — ${dato.fuente}`}
        className={`shrink-0 text-[9px] font-bold px-1.5 py-0.5 rounded border ${COLOR_MARCA[dato.marca]}`}
      >
        {dato.marca}
      </span>
    </div>
    <p className="text-lg font-bold text-uni-900 leading-tight">{dato.valor}</p>
    <span className="block text-[11px] text-slate-500 font-mono">{dato.fuente}</span>
    {dato.nota && <p className="text-[11px] text-slate-500 leading-relaxed pt-1">{dato.nota}</p>}
  </div>
);

const Grid: React.FC<{ icon: React.ElementType; color: string; titulo: string; children: React.ReactNode }> =
  ({ icon: Icon, color, titulo, children }) => (
  <div className="space-y-4 pt-4 first:pt-0 border-t first:border-t-0 border-slate-200">
    <h4 className="text-sm font-bold text-slate-600 uppercase tracking-wider flex items-center gap-2">
      <Icon className={`w-4 h-4 ${color}`} />
      {titulo}
    </h4>
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">{children}</div>
  </div>
);

export const TechnicalSpecsModal: React.FC<TechnicalSpecsModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
      <div className="fixed inset-0 bg-white/80 backdrop-blur-md transition-opacity" onClick={onClose} />

      <div className="relative w-full max-w-4xl bg-white border border-slate-200 rounded-3xl shadow-2xl shadow-blue-950/50 z-10 my-8 overflow-hidden">

        {/* Header */}
        <div className="flex items-center justify-between p-6 sm:p-8 border-b border-slate-200 bg-slate-50">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-blue-600/10 border border-blue-500/30 text-uni-600">
              <HardHat className="w-6 h-6" />
            </div>
            <div>
              <span className="text-[11px] font-mono font-semibold text-acred-600 tracking-wider uppercase">
                Ficha técnica preliminar — documento académico en elaboración
              </span>
              <h3 className="text-xl sm:text-2xl font-bold text-uni-900">Ferropista Cordillera Central — Parámetros</h3>
            </div>
          </div>
          <button onClick={onClose} className="p-2 rounded-lg text-slate-500 hover:text-uni-900 hover:bg-slate-100 transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 sm:p-8 space-y-8 max-h-[75vh] overflow-y-auto">

          {/* Advertencia de lectura */}
          <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/30 space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold text-amber-300 uppercase tracking-wider">
              <AlertTriangle className="w-4 h-4" />
              Cómo leer esta ficha
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Esta no es una ficha técnica oficial del proyecto. Es el estado del análisis del{' '}
              {EQUIPO.semillero} de la {EQUIPO.universidad}. Cada parámetro lleva su marca de origen:
            </p>
            <div className="grid sm:grid-cols-2 gap-2">
              {(['F', 'CP', 'H', 'DA'] as const).map((m) => (
                <div key={m} className="flex items-center gap-2 text-[11px] text-slate-500">
                  <span className={`shrink-0 text-[9px] font-bold px-1.5 py-0.5 rounded border ${COLOR_MARCA[m]}`}>{m}</span>
                  <span>{ETIQUETA_MARCA[m]}</span>
                </div>
              ))}
            </div>
            <p className="text-[11px] text-slate-500 leading-relaxed border-t border-amber-500/20 pt-3">
              {HIPOTESIS_TECNICAS.advertencia}
            </p>
          </div>

          <Grid icon={Mountain} color="text-uni-600" titulo="1. Trazado y alineamiento">
            <Spec etiqueta="Longitud total del tramo" dato={TRAZADO.longitudTotal} />
            <Spec etiqueta="Longitud del túnel principal" dato={TRAZADO.tunelPrincipal} />
            <Spec etiqueta="Cota portal Ibagué" dato={TRAZADO.cotaIbague} />
            <Spec etiqueta="Cota portal Armenia" dato={TRAZADO.cotaArmenia} />
            <Spec etiqueta="Pendiente media resultante" dato={TRAZADO.pendienteMedia} />
            <Spec etiqueta="Criterio de pendiente máxima" dato={TRAZADO.pendienteCriterio} />
          </Grid>

          <Grid icon={HardHat} color="text-acred-600" titulo="2. Excavación">
            <Spec etiqueta="Túneles principales" dato={EXCAVACION.tunelesPrincipales} />
            <Spec etiqueta="Galerías de acceso" dato={EXCAVACION.galerias} />
            <Spec etiqueta="Excavación mecanizada (TBM)" dato={EXCAVACION.tbm} />
            <Spec etiqueta="Excavación convencional" dato={EXCAVACION.convencional} />
            <Spec etiqueta="Volumen túneles principales" dato={EXCAVACION.volumenTuneles} />
            <Spec etiqueta="Reparto de métodos" dato={EXCAVACION.reparto} />
          </Grid>

          <Grid icon={Train} color="text-gmae-600" titulo="3. Operación intermodal">
            <Spec etiqueta="Fase inicial" dato={OPERACION.trenesDia} />
            <Spec etiqueta="Longitud del tren" dato={OPERACION.longitudTren} />
            <Spec etiqueta="Tractomulas por tren" dato={OPERACION.tractomulasTren} />
            <Spec etiqueta="Ciclo total de cruce" dato={OPERACION.tCicloTotal} />
            <Spec etiqueta="Capacidad diaria" dato={OPERACION.capacidadDiaria} />
            <Spec etiqueta="Velocidad comercial implícita" dato={OPERACION.velComercial} />
          </Grid>

          <Grid icon={ShieldCheck} color="text-uni-500" titulo="4. Seguridad, ventilación y normativa">
            <Spec etiqueta="Sistema de ventilación" dato={HIPOTESIS_TECNICAS.ventilacion} />
            <Spec etiqueta="Marco normativo de referencia" dato={HIPOTESIS_TECNICAS.normativa} />
            <Spec etiqueta="Ancho de vía" dato={HIPOTESIS_TECNICAS.anchoVia} />
            <Spec etiqueta="Sección transversal y gálibo" dato={HIPOTESIS_TECNICAS.seccionTunel} />
          </Grid>

          {/* Vacíos de la fuente */}
          <div className="space-y-3 pt-4 border-t border-slate-200">
            <h4 className="text-sm font-bold text-slate-600 uppercase tracking-wider flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-slate-500" />
              5. Vacíos de información identificados
            </h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Lo que la fuente no dice delimita el alcance real de este trabajo. Declararlo es parte del análisis.
            </p>
            <div className="space-y-2">
              {VACIOS.map((v) => (
                <div key={v.tema} className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <p className="text-xs font-semibold text-slate-700">{v.tema}</p>
                  <p className="text-[11px] text-slate-500 leading-relaxed mt-0.5">{v.consecuencia}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Fuente */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
            <p className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">Fuente primaria</p>
            <p className="text-[11px] text-slate-500 leading-relaxed">{FUENTE_PRIMARIA.cita}</p>
            <p className="text-[11px] text-amber-300/80 leading-relaxed border-t border-slate-200 pt-2">
              {FUENTE_PRIMARIA.advertencia}
            </p>
          </div>

        </div>

        {/* Footer */}
        <div className="p-6 border-t border-slate-200 bg-slate-50 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-[11px] text-slate-500 font-mono text-center sm:text-left">
            Trabajo académico · {EQUIPO.semillero} · {EQUIPO.universidad} · {EQUIPO.programa}
          </div>
          <button
            onClick={onClose}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-700 text-uni-900 font-semibold text-sm transition-colors"
          >
            Cerrar
          </button>
        </div>

      </div>
    </div>
  );
};
