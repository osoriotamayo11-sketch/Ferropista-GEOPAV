/**
 * metodo_oe.ts — textos del bloque «Cómo se hizo» de cada objetivo específico.
 *
 * Redactados por el orquestador y aprobados por Migue el 27 sep 2026 (sesión 17).
 * Estructura común: por qué · para qué · cómo · qué no afirma y limitaciones.
 * Aquí solo va el texto que no existía en el sitio. Donde el componente ya tenía
 * el método (OE 1, OE 5) o los límites (OE 5: SV.limites; OE 1: dos limitaciones
 * con cifras de proyecto.ts), el componente los conserva y este archivo aporta
 * lo que falta. No contiene cifras nuevas: las que aparecen ya están publicadas.
 */

export interface MetodoOE {
  porQue: string;
  paraQue: string;
  /** Párrafos del método. Vacío = el componente conserva su texto actual. */
  como: readonly string[];
  /** Límites adicionales o completos, según el objetivo (ver comentario de cada uno). */
  noAfirma: readonly string[];
}

export const METODO_OE: Record<'oe1' | 'oe2' | 'oe3' | 'oe5', MetodoOE> = {
  oe1: {
    porQue:
      'La ponencia solo da las cotas de los portales (950 y 1.450 msnm) y las longitudes (44 y 58 km). ' +
      'No publica trazado, perfil ni cobertura, y sin eso no se sabe dónde queda el túnel ni cuánta roca tiene encima.',
    paraQue:
      'Fija los portales y el eje. Esas coordenadas son la entrada del OE 3 (terreno de los portales), ' +
      'del OE 4 (método de excavación según la cobertura) y del mapa del sitio.',
    como: [], // el componente conserva su párrafo actual
    // Se AGREGA a las dos limitaciones que ya muestra el componente:
    noAfirma: [
      'El eje es una línea recta (geodésica) entre los portales, porque la ponencia no publica el trazado real.',
    ],
  },
  oe2: {
    porQue:
      'El proyecto era solo documental. Sin participación de la comunidad no cumple lo que exige Paz y Región, ' +
      'y ninguna entidad mide lo que opinan quienes usan el corredor.',
    paraQue:
      'Es el único dato primario del proyecto. Se contrasta con la siniestralidad del OE 5 y alimenta el impacto social del OE 7.',
    como: [
      'La encuesta vive en el propio sitio y las respuestas se guardan en una base de datos. Usa el instrumento oficial ' +
        'avalado por la entidad receptora: 17 preguntas, anónima y sin datos de contacto. Cada respuesta queda marcada ' +
        'con la versión del cuestionario que la produjo.',
      'Recibe respuestas hasta el 3 de octubre de 2026 y se difunde por canales digitales. Al cierre, las respuestas ' +
        'se consolidan en Excel (actividad 5).',
    ],
    noAfirma: [
      'No es una muestra estadística del corredor: responde quien se entera y quiere.',
      'Mide conocimiento y percepción de la propuesta, no el riesgo real, que es lo que calcula el OE 5.',
      'Nada impide que una persona responda más de una vez: el bloqueo después de enviar solo dura mientras la página siga abierta.',
    ],
  },
  oe3: {
    porQue:
      'La ponencia no tiene exploración del subsuelo en los portales, y los portales del OE 1 se ubicaron solo por geometría. ' +
      'Antes de hablar de cimentar las terminales hay que saber qué terreno hay debajo.',
    paraQue:
      'Describir, en cada portal, la geología, la exigencia sísmica y la amenaza por movimientos en masa. Sobre eso se ' +
      'construyen los parámetros (actividad 3), la capacidad portante admisible como rango (actividad 4) y el esquema de ' +
      'cimentación de las terminales Ro-Ro (actividad 5).',
    como: [
      'Cada portal se ubicó sobre las planchas geológicas 1:100.000 del SGC (244 Ibagué y 243 Armenia) calibrando la ' +
        'cuadrícula de 5 km de cada plancha, con una precisión de unos ±0,1 km. Las unidades geológicas se identificaron ' +
        'por su color en la leyenda impresa de cada plancha.',
      'Se consultaron los servicios en línea del SGC: mapa geológico 2023, fallas, zonificación sísmica NSR-10, amenaza y ' +
        'susceptibilidad 1:100.000 e inventario de movimientos en masa (SIMMA). La pendiente se calculó sobre el modelo de ' +
        'elevación del OE 1, en círculos de 250 m y 3 km alrededor de cada portal.',
    ],
    noAfirma: [
      'No hay exploración del subsuelo: todo sale de cartografía de 1982 y 1985 a escala 1:100.000.',
      'Los dos portales quedan en contacto entre dos rocas (a 110 m y a 70 m de la unidad vecina): correr el portal unos ' +
        'cientos de metros cambia la roca de la boca del túnel.',
      'No hay espesor publicado de roca meteorizada.',
      'La zonificación NSR-10 es municipal; no es microzonificación.',
      'La amenaza es relativa a escala 1:100.000; no es un análisis de estabilidad del talud de entrada.',
      'La capacidad portante será un rango, no un valor para diseñar.',
    ],
  },
  oe5: {
    porQue:
      'La ponencia promete beneficios en seguridad vial, pero no publica ninguna tasa de siniestralidad del paso. ' +
      'Sin una línea base no hay contra qué comparar.',
    paraQue:
      'Dejar una tasa medida del paso actual (fallecidos por 100 millones de vehículos-km, 2015–2019) contra la cual ' +
      'evaluar cualquier beneficio. Alimenta el OE 7.',
    como: [], // el componente conserva su texto actual, SIN el recuadro del 12,79
    noAfirma: [], // se usan los SV.limites de proyecto.ts, sin cambios de texto
  },
};
