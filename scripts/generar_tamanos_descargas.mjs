// Calcula el tamaño real (bytes) de los archivos de descarga que muestran los
// componentes de la web, para no escribir a mano un tamaño que después queda
// desactualizado. Se corre a mano cuando cambia alguno de estos archivos;
// escribe src/data/descargas_tamanos.json, que los componentes solo leen.
import { statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve } from 'node:path';
import { writeFileSync } from 'node:fs';

const RAIZ = resolve(dirname(fileURLToPath(import.meta.url)), '..');

const ARCHIVOS = [
  '/oe3/descargas/OE3_Act1_Planos_geologicos_portales.pdf',
  '/oe3/descargas/OE3_Act1_Lamina_geologia_portales.pdf',
  '/oe3/descargas/OE3_Act2_Mapa_susceptibilidad.pdf',
  '/oe3/lamina_portales_geologia.jpg',
  '/oe3/mapa_susceptibilidad.jpg',
  '/oe5/graficos_siniestralidad.jpg',
  '/oe5/densidad_lineal.jpg',
];

const tamanos = {};
for (const ruta of ARCHIVOS) {
  const abs = join(RAIZ, 'public', ruta);
  tamanos[ruta] = statSync(abs).size;
}

const salida = {
  generado_por: 'scripts/generar_tamanos_descargas.mjs',
  tamanos_bytes: tamanos,
};

writeFileSync(join(RAIZ, 'src/data/descargas_tamanos.json'), JSON.stringify(salida, null, 1) + '\n');
console.log('src/data/descargas_tamanos.json actualizado con', ARCHIVOS.length, 'archivos.');
