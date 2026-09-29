'use client';

/**
 * DescargaArchivo — enlace de descarga con formato y tamaño reales, mismo
 * estilo que usaba OE1 (icono Download, borde, texto uni-600). El tamaño sale
 * de `descargas_tamanos.json`, calculado del archivo en `public/` por
 * `scripts/generar_tamanos_descargas.mjs`: nunca se escribe a mano.
 */

import React from 'react';
import { Download } from 'lucide-react';
import tamanos from '@/data/descargas_tamanos.json';

const TAMANOS_BYTES: Record<string, number> = tamanos.tamanos_bytes;

function formatoTamano(bytes: number): string {
  const mb = bytes / (1024 * 1024);
  if (mb >= 1) {
    return `${mb.toLocaleString('es-CO', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} MB`;
  }
  const kb = Math.round(bytes / 1024);
  return `${kb.toLocaleString('es-CO')} KB`;
}

interface Props {
  href: string;
  etiqueta: string;
  formato: string;
  className?: string;
}

export const DescargaArchivo: React.FC<Props> = ({ href, etiqueta, formato, className }) => {
  const bytes = TAMANOS_BYTES[href];
  return (
    <a
      href={href}
      download
      className={
        className ??
        'inline-flex shrink-0 items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-[11px] font-semibold text-uni-600 transition-colors hover:border-uni-300 hover:text-uni-700'
      }
    >
      <Download className="h-3.5 w-3.5 shrink-0" />
      {etiqueta} ({formato}{bytes ? `, ${formatoTamano(bytes)}` : ''})
    </a>
  );
};

export default DescargaArchivo;
