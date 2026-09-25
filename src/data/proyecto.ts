/**
 * FUENTE ÚNICA DE VERDAD DEL PROYECTO FERROPISTA
 * ------------------------------------------------------------------
 * Semillero de Investigación GEOPAV · Semestre Paz y Región 2026B
 * Universidad de Ibagué · Tramo Ibagué – Armenia
 *
 * Ningún componente debe declarar cifras propias. Toda cifra que se
 * muestre en la interfaz se importa desde este archivo y arrastra su
 * marca de origen. Así es imposible que dos secciones se contradigan.
 *
 * MARCAS DE ORIGEN
 *   F   Dato tomado de la ponencia de referencia, con diapositiva.
 *   CP  Cálculo propio del semillero, reproducible de forma independiente.
 *   H   Hipótesis de trabajo del semillero. NO es un dato medido.
 *   DA  Dato abierto pendiente de consultar en la fuente oficial.
 *
 * REGLA: si una cifra no puede recibir una de estas cuatro marcas,
 * no entra a este archivo y no se publica.
 */

export type Marca = 'F' | 'CP' | 'H' | 'DA';

export interface Dato {
  /** Valor ya formateado para mostrar en pantalla. */
  valor: string;
  /** Valor numérico crudo, cuando aplica (gráficas, cálculos). */
  n?: number;
  marca: Marca;
  /** De dónde sale. Se muestra al usuario. */
  fuente: string;
  /** Matiz o advertencia que debe acompañar al dato. */
  nota?: string;
}

export const FUENTE_PRIMARIA = {
  cita:
    'Fernández Ordóñez, H. O. (2025). Túnel para cruce férreo de la Cordillera Central de los Andes ' +
    'y semilla para la Estrella Andina [Ponencia]. XX Seminario Andino de Túneles y Obras Subterráneas ' +
    '— II ExpoTúneles, Sociedad Antioqueña de Ingenieros y Arquitectos. Medellín, 8 de octubre de 2025.',
  autor: 'Ing. Hernán Otoniel Fernández Ordóñez',
  proponentes: 'ARCS y UC Consult',
  evento: 'XX Seminario Andino de Túneles y Obras Subterráneas — II ExpoTúneles (SAI)',
  fecha: '8 de octubre de 2025',
  sitio: 'https://www.ferropista.com',
  advertencia:
    'La ponencia es un documento de promoción de una iniciativa privada orientada a una Asociación ' +
    'Público Privada. Sus cifras de impacto son estimaciones del proponente, no resultados auditados ' +
    'por un tercero independiente. Verificarlas es el objeto del trabajo de este semillero.',
} as const;

const p = (n: number) => `Ponencia Fernández O. (2025), diapositiva ${n}`;
const CALC = 'Cálculo propio del Semillero GEOPAV';
const HIP = 'Hipótesis de trabajo del Semillero GEOPAV — sin verificar';

export const ETIQUETA_MARCA: Record<Marca, string> = {
  F: 'Dato de la ponencia',
  CP: 'Cálculo propio del semillero',
  H: 'Hipótesis de trabajo — sin verificar',
  DA: 'Pendiente de fuente oficial',
};

export const COLOR_MARCA: Record<Marca, string> = {
  F: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
  CP: 'bg-blue-500/10 text-blue-300 border-blue-500/30',
  H: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
  DA: 'bg-slate-500/10 text-slate-300 border-slate-500/30',
};

/* ================================================================
   1. TRAZADO Y GEOMETRÍA
   ================================================================ */
export const TRAZADO = {
  longitudTotal:   { valor: '58 km',      n: 58,   marca: 'F'  as Marca, fuente: p(20) },
  tunelPrincipal:  { valor: '44 km',      n: 44,   marca: 'F'  as Marca, fuente: p(20) },
  cotaIbague:      { valor: '950 msnm',   n: 950,  marca: 'F'  as Marca, fuente: p(20),
                     nota: 'Portal oriental. El punto calculado cae en jurisdicción de Ibagué, Tolima (DANE 73001), a 9,2 km del casco urbano (~1.285 msnm), no en Coello.' },
  cotaArmenia:     { valor: '1.450 msnm', n: 1450, marca: 'F'  as Marca, fuente: p(20) },
  cotaPasoActual:  { valor: '3.300 msnm', n: 3300, marca: 'F'  as Marca, fuente: p(20),
                     nota: 'Cota del Alto de La Línea que el túnel de base evita.' },
  desnivel:        { valor: '500 m',      n: 500,  marca: 'CP' as Marca, fuente: CALC,
                     nota: '1.450 − 950 = 500 m entre portales.' },
  pendienteMedia:  { valor: '0,86 %',     n: 0.86, marca: 'CP' as Marca, fuente: CALC,
                     nota: 'i = (1.450 − 950) m / 58.000 m = 0,00862. Es la pendiente media entre portales; el trazado real puede requerir tramos de mayor pendiente y contrapendientes de drenaje.' },
  pendienteCriterio:{ valor: '< 1,5 %',   n: 1.5,  marca: 'H'  as Marca, fuente: HIP,
                     nota: 'Límite adoptado por el semillero para tracción ferroviaria de carga pesada. La ponencia no declara pendiente.' },
  configuracion:   { valor: '7 túneles de 7 a 8 km',  marca: 'F' as Marca, fuente: p(20) },
  estaciones:      { valor: '2 estaciones logísticas', marca: 'F' as Marca, fuente: p(20) },
} as const;

/* ================================================================
   2. EXCAVACIÓN
   ================================================================ */
export const EXCAVACION = {
  tunelesPrincipales: { valor: '64,2 km',      n: 64.2,    marca: 'F' as Marca, fuente: p(22), nota: 'Incluye el bypass central.' },
  galerias:           { valor: '16,0 km',      n: 16.0,    marca: 'F' as Marca, fuente: p(22) },
  volumenTuneles:     { valor: '8.450.000 m³', n: 8450000, marca: 'F' as Marca, fuente: p(22) },
  volumenGalerias:    { valor: '820.000 m³',   n: 820000,  marca: 'F' as Marca, fuente: p(22) },
  tbm:                { valor: 'mín. 27,5 km', n: 27.5,    marca: 'F' as Marca, fuente: p(22) },
  convencional:       { valor: '36,7 km',      n: 36.7,    marca: 'F' as Marca, fuente: p(22) },
  verificacion:       { valor: '27,5 + 36,7 = 64,2 km',    marca: 'CP' as Marca, fuente: CALC,
                        nota: 'La partición declarada cierra exactamente con la longitud de túneles principales.' },
  reparto:            { valor: '43 % mecanizado / 57 % convencional', marca: 'CP' as Marca, fuente: CALC,
                        nota: 'Proporción notable: en túneles de base europeos comparables la fracción mecanizada suele ser mayor, lo que sugiere que el proponente anticipa geología adversa en más de la mitad del trazado. El objetivo específico 4 debe contrastarlo con la cartografía del SGC.' },
} as const;

/* ================================================================
   3. OPERACIÓN
   ================================================================ */
export const OPERACION = {
  trenesDia:      { valor: '140 trenes/día',  n: 140, marca: 'F' as Marca, fuente: p(20), nota: 'Fase inicial.' },
  tractomulasTren:{ valor: '35 tractomulas',  n: 35,  marca: 'F' as Marca, fuente: p(20) },
  longitudTren:   { valor: 'hasta 750 m',     n: 750, marca: 'F' as Marca, fuente: p(23) },
  composicion:    { valor: 'Locomotora + vagón para conductores + 35 plataformas + 2 plataformas de acceso', marca: 'F' as Marca, fuente: p(23) },
  tPeajeCarga:    { valor: '25 min', n: 25, marca: 'F' as Marca, fuente: p(23) },
  tDesplazamiento:{ valor: '30 min', n: 30, marca: 'F' as Marca, fuente: p(23) },
  tDescarga:      { valor: '15 min', n: 15, marca: 'F' as Marca, fuente: p(23) },
  tCicloTotal:    { valor: '70 min', n: 70, marca: 'F' as Marca, fuente: p(23),
                    nota: 'Solo 30 de los 70 minutos son desplazamiento. Los otros 40 son operación en terminal, lo que hace del diseño de las estaciones Ro-Ro un factor crítico de la eficiencia real.' },
  capacidadDiaria:{ valor: '4.900 tractomulas/día', n: 4900, marca: 'CP' as Marca, fuente: CALC,
                    nota: '140 trenes/día × 35 tractomulas por tren.' },
  velComercial:   { valor: '≈ 88 km/h', n: 88, marca: 'CP' as Marca, fuente: CALC,
                    nota: '44 km de túnel principal en 30 min de desplazamiento.' },
  cruceConvoyes:  { valor: 'Bypass central', marca: 'F' as Marca, fuente: p(23) },
} as const;

/* ================================================================
   4. SITUACIÓN ACTUAL DEL CORREDOR
   ================================================================ */
export const ACTUAL = {
  velocidadMedia:  { valor: '< 20 km/h',     n: 20,      marca: 'F' as Marca, fuente: p(13) },
  tiempoCruce:     { valor: '4 horas',       n: 240,     marca: 'F' as Marca, fuente: p(29), nota: 'Valor medio declarado por la ponencia.' },
  camionesGrandes: { valor: '2.100 veh/día', n: 2100,    marca: 'F' as Marca, fuente: p(10), nota: 'Aforo INVÍAS 2017 citado por la ponencia.' },
  camionesMedianos:{ valor: '1.700 veh/día', n: 1700,    marca: 'F' as Marca, fuente: p(10), nota: 'Aforo INVÍAS 2017 citado por la ponencia.' },
  pesadosAnio:     { valor: '1.390.000 veh/año', n: 1390000, marca: 'F' as Marca, fuente: p(10) },
  vehiculosTotales:{ valor: '2,3 millones (2017)', n: 2300000, marca: 'F' as Marca, fuente: p(17) },
  crecimiento:     { valor: '3 % anual',     n: 3,       marca: 'F' as Marca, fuente: p(10) },
  pesados2030:     { valor: '1.700.000 veh/año', n: 1700000, marca: 'F' as Marca, fuente: p(10) },
  captacionGrandes:  { valor: '90 %', n: 90, marca: 'F' as Marca, fuente: p(10),
                       nota: 'Porcentaje del flujo actual de camiones grandes que se prevé captar hacia la Ferropista en 2030. No es composición de un tren.' },
  captacionMedianos: { valor: '60 %', n: 60, marca: 'F' as Marca, fuente: p(10),
                       nota: 'Porcentaje del flujo actual de camiones medianos que se prevé captar hacia la Ferropista en 2030.' },
  /* RESUELTO por el objetivo específico 5 (9 sep 2026). La tasa se calcula y se
     publica: ver SEGURIDAD_VIAL, que es donde viven las cifras y sus notas. */
  siniestralidad:  { valor: '7,66 fallecidos / 100 M veh-km', n: 7.6605, marca: 'CP' as Marca, fuente: CALC,
                     nota: 'Tasa del paso Calarcá – Cajamarca (45 km): 42 fallecidos de la ANSV entre 2015 y 2019, sobre el tránsito medido por INVÍAS en la estación 244 para el mismo periodo. Sobre los 74 km del corredor completo la tasa es 4,56. La ponencia no aporta ninguna tasa: la documenta de forma cualitativa con casos de prensa entre 2022 y 2025 (diapositivas 11 y 12). La línea base es anterior al Túnel de La Línea y sobrestima el riesgo actual.' },
  pendienteVia:    { valor: 'Pendiente de verificación', marca: 'DA' as Marca,
                     fuente: 'Pendiente: cartera de diseño geométrico de la Ruta 40 (INVÍAS)',
                     nota: 'La ponencia no declara la pendiente de la vía actual. La Ruta 40 es vía nacional primaria, con pendientes máximas de diseño del orden del 6 al 8 %.' },
} as const;

/* ================================================================
   4b. SEGURIDAD VIAL DEL CORREDOR — RESULTADO DEL OBJETIVO ESPECÍFICO 5
   ================================================================
   Cerrado el 9 sep 2026. Todas las cifras se leen del libro
   OE5_SeguridadVial/Act4_Analisis/analisis_siniestralidad_OE5.xlsx,
   que las calcula por fórmula desde las entradas medidas de la hoja 2.
   Ninguna se escribió a mano aquí sin recalcularla de forma independiente.

   La tasa dejó de ser hipótesis el 8 sep 2026: la serie histórica de TPD de
   INVÍAS (estaciones 243 y 244) puso el aforo en el MISMO periodo y la MISMA
   vía que los fallecidos de la ANSV. Antes de eso el sitio publicaba que la
   tasa no era calculable; esa afirmación quedó obsoleta y se retiró.
   ================================================================ */
const ANSV = 'ANSV, conjunto rs3u-8r4q (datos.gov.co), fallecidos 2015–2019';
const INVIAS_TPD = 'INVÍAS, serie histórica de volúmenes de tránsito 1997–2018';

export const SEGURIDAD_VIAL = {
  nota:
    'Línea base de siniestralidad del corredor Ibagué – Calarcá sobre la Ruta Nacional 40. ' +
    'Describe el corredor ANTERIOR al Túnel de La Línea, que entró en operación el 4 de ' +
    'septiembre de 2020: sobrestima el riesgo del corredor actual, y así se declara.',

  /* --- El resultado --- */
  tasaCorredor:   { valor: '4,56', n: 4.5601, marca: 'CP' as Marca, fuente: CALC,
                    nota: 'Fallecidos por cada 100 millones de vehículos-kilómetro. 42 fallecidos sobre los 74 km del tramo que la ANSV nombra «Calarcá – Ibagué», con TPD ponderado por longitud de 6.820 veh/día y 5 años de registro.' },
  tasaPaso:       { valor: '7,66', n: 7.6605, marca: 'CP' as Marca, fuente: CALC,
                    nota: 'Los mismos 42 fallecidos sobre los 45 km del descenso Calarcá – Cajamarca, donde caen los cuatro sectores críticos que los aportan, con el TPD medido de la estación 244. Es mayor porque concentra la misma mortalidad en menos kilómetros.' },
  tasaAnterior:   { valor: '12,79', n: 12.7854, marca: 'H' as Marca, fuente: HIP,
                    nota: 'La cifra que el semillero publicaba antes del 8 sep 2026. Sus dos entradas eran supuestos: TPD de 3.000 veh/día y 60 km de tramo. El tránsito real del paso es más del doble del supuesto, así que la tasa medida es un 36 % de la anterior.' },
  tasaControl52:  { valor: '5,65', n: 5.6458, marca: 'CP' as Marca, fuente: CALC,
                    nota: 'Fila de control, no resultado: los 52 fallecidos de los seis sectores sobre los 74 km. Incluye los diez del tramo a cargo de la ANI, que no pertenecen al cruce. Sirve de cota superior.' },

  /* --- Las entradas, todas medidas --- */
  fallecidosPaso:     { valor: '42', n: 42, marca: 'F' as Marca, fuente: ANSV,
                        nota: 'Cuatro sectores críticos del tramo «Calarcá – Ibagué» a cargo de INVÍAS: PR 86 con 21, PR 6 con 11, y PR 10 con 9 y con 1.' },
  fallecidosCorredor: { valor: '52', n: 52, marca: 'F' as Marca, fuente: ANSV,
                        nota: 'Los seis sectores críticos del corredor, todos en jurisdicción de Calarcá (Quindío). Los dos restantes, con 10 fallecidos, están a cargo de la ANI.' },
  sectoresCriticos:   { valor: '6', n: 6, marca: 'F' as Marca, fuente: ANSV,
                        nota: 'Caben en 3,6 km del descenso hacia Calarcá, medidos por la distancia haversine entre los puntos extremos.' },
  tpdPaso:            { valor: '6.676 veh/día', n: 6676, marca: 'F' as Marca, fuente: INVIAS_TPD,
                        nota: 'Estación 244, sector Calarcá – Cajamarca, media 2015–2018. Es la entrada que faltaba: pone el aforo en el mismo periodo que los fallecidos.' },
  tpdCorredor:        { valor: '6.820 veh/día', n: 6820, marca: 'CP' as Marca, fuente: CALC,
                        nota: 'Ponderado por longitud entre la estación 244 (6.676 veh/día, 45 km) y la 243 (7.043 veh/día, 29 km).' },
  longitudCorredor:   { valor: '74 km', n: 74, marca: 'F' as Marca, fuente: INVIAS_TPD,
                        nota: 'Suma de las longitudes que INVÍAS declara para sus dos estaciones del corredor: 45 + 29 km. No es una medición del semillero.' },
  longitudPaso:       { valor: '45 km', n: 45, marca: 'F' as Marca, fuente: INVIAS_TPD,
                        nota: 'Longitud declarada por INVÍAS para la estación 244, el paso de la cordillera.' },
  participacionPesada:{ valor: '55,5 %', n: 55.54, marca: 'CP' as Marca, fuente: CALC,
                        nota: 'Camiones sobre el total del paso, con la composición vehicular que publica INVÍAS. Esa clase incluye los camiones de dos ejes, que en peaje caen en categoría II: es cota superior, no comparable con el 17,9 % del peaje Cocora.' },
  exposicionPesada:   { valor: '60.903.900 veh-km/año', n: 60903900, marca: 'CP' as Marca, fuente: CALC,
                        nota: '3.708 camiones/día × 45 km × 365. Es la exposición anual del grupo que la Ferropista captaría.' },
  sensibilidadHipotesis:{ valor: '1,0 %', n: 1.0, marca: 'CP' as Marca, fuente: CALC,
                        nota: 'Cuánto mueve la tasa la única hipótesis que queda: suponer que 2019 tuvo un tránsito parecido al de 2015–2018. Sustituyendo con el aforo medido del peaje Cajamarca de 2019 (6.351 veh/día) la tasa del paso pasa de 7,66 a 7,74.' },

  /* Los seis sectores críticos, tal como los entrega la fuente [F]. */
  sectores: [
    { pr: 'PR 86', fallecidos: 21, confianza: '99 %', entidad: 'INVÍAS', enPaso: true },
    { pr: 'PR 6',  fallecidos: 11, confianza: '99 %', entidad: 'INVÍAS', enPaso: true },
    { pr: 'PR 85', fallecidos: 9,  confianza: '99 %', entidad: 'ANI',    enPaso: false },
    { pr: 'PR 10', fallecidos: 9,  confianza: '95 %', entidad: 'INVÍAS', enPaso: true },
    { pr: 'PR 85', fallecidos: 1,  confianza: '99 %', entidad: 'ANI',    enPaso: false },
    { pr: 'PR 10', fallecidos: 1,  confianza: '95 %', entidad: 'INVÍAS', enPaso: true },
  ],

  /* Las cuatro mediciones del corredor. NO son una serie temporal: son cuatro
     puntos de medición con criterios de clasificación distintos [CP sobre F]. */
  mediciones: [
    { punto: 'Estación 244 · INVÍAS (tramo, 45 km)',   periodo: 'Media 2015–2018',   tpd: 6676, pesada: 55.5 },
    { punto: 'Estación 243 · INVÍAS (tramo, 29 km)',   periodo: 'Media 2015–2017',   tpd: 7043, pesada: 54.3 },
    { punto: 'Peaje Cajamarca · PR 24+020 (punto)',    periodo: '2019',              tpd: 6351, pesada: 32.9 },
    { punto: 'Peaje Cocora · K 13+750 (punto)',        periodo: 'Jun 2025 – may 2026', tpd: 4954, pesada: 17.9 },
  ],

  /* Lo que el objetivo NO puede afirmar. Se publica junto al resultado. */
  limites: [
    'Cuántas muertes evitaría la Ferropista. Eso exige un modelo de siniestralidad calibrado con microdatos por siniestro — tipo de vehículo, causa, condición de la víctima — que no están publicados para este corredor. El microdato que la ANSV entregó por solicitud (oficio 20265000140371, 22 sep 2026) solo incluye lo que pudo georreferenciarse: de los siniestros fatales de prensa de 2022 a 2025 contiene dos. Con ese subregistro no se calibra un modelo.',
    'Que la tasa de hoy sea esta. La línea base es anterior al Túnel de La Línea (4 sep 2020) y sobrestima el riesgo del corredor actual. Con el microdato posterior al túnel, la tasa del paso 2021–2025 da 3,65 a 3,83 fallecidos por 10⁸ veh-km, pero es una cota inferior (subregistro y TPD supuesto, sin aforo del paso después de 2019) y no se compara con 7,66: otra fuente y otro criterio.',
    'Que el lado tolimense sea más seguro. El conjunto de sectores críticos 2015–2019 no marca ninguno en Cajamarca ni en el tramo Cajamarca – Ibagué, pero el microdato 2021 – mar 2026 que entregó la ANSV sí registra en ese tramo 35 hechos, con 7 fallecidos y 58 lesionados. La ausencia era de sector crítico, no de siniestros. Que ese lado tenga menos mortalidad por kilómetro no puede afirmarse: el microdato tiene subregistro.',
    'Comparar la participación de carga pesada entre la serie por estación (54–56 %) y los peajes (18–33 %). La clase «camiones» de INVÍAS incluye los de dos ejes, que en peaje caen en categoría II. Las dos lecturas se publican por separado y no se promedian.',
    'Que el Túnel de La Línea haya resuelto el riesgo del paso. La propia ponencia lo documenta con recortes de prensa en las diapositivas 11 y 12: siete siniestros entre 2022 y 2025 -dos en 2022, uno en 2023, uno en 2024 (tres hermanos, túnel Las Mariposas) y tres en 2025 (túnel Los Azulejos, el puente helicoidal y una tractomula que cayó a un abismo descendiendo a Calarcá)-, a los que el semillero suma uno más verificado por su cuenta (22 de mayo de 2024, un fallecido, Infobae). El recorte de la tractomula al abismo se publica en la ponencia sin fecha visible; el semillero la fechó el 14 de abril de 2025 abriendo la noticia original de El Tiempo, que no reporta fallecidos ni heridos de consideración. El más grave es el bus de la Universidad Alexander von Humboldt, que cayó del puente helicoidal el 24 de mayo de 2025: 10 muertos según El Tiempo el mismo día, 11 según Infobae al día siguiente; se documenta el rango porque ninguna fuente posterior lo fija. El microdato que la ANSV entregó en septiembre de 2026 solo contiene dos de estos hechos: el bus del 14 de diciembre de 2023 (2 fallecidos) y el del puente helicoidal (9 fallecidos georreferenciados, frente a 10–11 en prensa). Ninguno entra en la tasa: son de prensa, sin PR ni Gi* de la ANSV, y mezclarlos con ese dataset repetiría el error ya corregido de comparar los peajes Cocora y Cajamarca. El túnel reduce la exposición, no la elimina.',
  ],

  /* Mapa de calor: por qué es lineal y no en 2D. */
  porQueNoKde:
    'El mapa de calor clásico no se publica; en su lugar se publica una densidad lineal. El insumo ' +
    'ya existe: la ANSV entregó por solicitud el microdato georreferenciado 2021 – mar 2026 de la ' +
    'Ruta 4003 (118 víctimas en 70 hechos). Pero un estimador de densidad en dos dimensiones reparte ' +
    'sobre el monte lo que ocurre en una línea, así que la densidad se calcula a lo largo de la vía, ' +
    'contando hechos y no víctimas. Y se lee con una advertencia: el microdato solo trae lo que se ' +
    'pudo georreferenciar, y el ascenso al Alto de La Línea está subrepresentado: de ocho siniestros ' +
    'fatales de prensa, figuran dos. La figura muestra dónde se pudo georreferenciar, no dónde está ' +
    'el riesgo. Para 2015–2019 se mantiene el mapa de sectores críticos con el Gi* de la propia fuente.',
} as const;

/* ================================================================
   5. IMPACTOS
   ================================================================ */
export const AMBIENTAL = {
  reduccionGEI:      { valor: '90 %',              n: 90,   marca: 'F' as Marca, fuente: p(25),
                       nota: 'Reducción de emisiones GEI y consumos energéticos del cruce. No es cero: la huella real depende de la matriz de generación eléctrica del país y de las emisiones incorporadas en la construcción.' },
  geiEvitados:       { valor: '26,8 Mt de CO₂e',   n: 26.8, marca: 'F' as Marca, fuente: p(26), nota: 'Acumulado a 50 años.' },
  combustible:       { valor: '37,2 M de galones', n: 37.2, marca: 'F' as Marca, fuente: p(26), nota: 'Ahorro proyectado para el año 2030.' },
  costosExternos:    { valor: '$COP 138,5 billones', n: 138.5, marca: 'F' as Marca, fuente: p(26),
                       nota: 'Ahorro a 50 años en congestión, polución, seguridad vial y ruido. Es el indicador que conecta simultáneamente los ejes ambiental y de seguridad vial.' },
  huellaConstruccion:{ valor: 'No reportada por la fuente', marca: 'DA' as Marca,
                       fuente: 'Vacío identificado por el Semillero GEOPAV',
                       nota: 'La ponencia cuantifica el beneficio de la operación pero no la huella de construir 8.450.000 m³ de excavación más el concreto de revestimiento. El balance neto de carbono no puede cerrarse sin ese dato.' },
} as const;

export const ECONOMICO = {
  ahorroTransporte2030: { valor: '$COP 2,5 billones', n: 2.5,  marca: 'F' as Marca, fuente: p(28), nota: 'Sector transporte, año 2030.' },
  recaudoFiscal:        { valor: '$COP 60,2 billones', n: 60.2, marca: 'F' as Marca, fuente: p(28),
                          nota: 'RECAUDO FISCAL para todo Colombia a 50 años. No son ahorros del usuario: son ingresos del Estado. Confundir ambos conceptos invalida cualquier análisis costo-beneficio.' },
  nuevosTraficos:       { valor: '$COP 14,5 billones', n: 14.5, marca: 'F' as Marca, fuente: p(28), nota: 'Inducción de nuevos tráficos, todo Colombia a 50 años.' },
  incrementoPIB:        { valor: '+0,25 %',            n: 0.25, marca: 'F' as Marca, fuente: p(28) },
  productividad:        { valor: '×3',                 n: 3,    marca: 'F' as Marca, fuente: p(28), nota: 'Productividad del sector transporte en 2030.' },
  horasAhorradas:       { valor: '5,0 – 5,3 M h/año',  n: 5.15, marca: 'F' as Marca, fuente: `${p(28)} y ${p(29)}`,
                          nota: 'INCONSISTENCIA DE LA FUENTE: la diapositiva 28 reporta 5,0 millones de horas al año; la 29, mediante el gráfico de tiempos de viaje (Ruta 40: 7,0 M h/año; Ferropista: 1,7 M h/año), arroja 5,3. Diferencia del 6 %. El semillero documenta el rango en lugar de escoger un valor en silencio.' },
  horasRuta40:          { valor: '7,0 M h/año',        n: 7.0,  marca: 'F' as Marca, fuente: p(29) },
  horasFerropista:      { valor: '1,7 M h/año',        n: 1.7,  marca: 'F' as Marca, fuente: p(29) },
  capex:                { valor: 'US$ 2.800 millones', n: 2800, marca: 'F' as Marca, fuente: p(20) },
  peaje:                { valor: 'Inferior a los costos operacionales de la vía alternativa', marca: 'F' as Marca, fuente: p(19),
                          nota: 'La ponencia no cuantifica en porcentaje la reducción de costos de flete. Cualquier cifra de ese tipo debe construirla el semillero en el objetivo específico 6.' },
  reduccionFlete:       { valor: 'Pendiente de cálculo propio', marca: 'DA' as Marca,
                          fuente: 'Pendiente: matriz de costos operativos — objetivo específico 6' },
} as const;

export const SOCIAL = {
  poblacionEje:      { valor: '1,1 millones',  n: 1100000,  marca: 'F' as Marca, fuente: p(27), nota: 'Eje Ibagué – Cajamarca – Armenia.' },
  poblacionDptos:    { valor: '4 millones',    n: 4000000,  marca: 'F' as Marca, fuente: p(27), nota: 'Quindío, Tolima, Risaralda y Caldas.' },
  poblacionRegion:   { valor: '28 millones',   n: 28000000, marca: 'F' as Marca, fuente: `${p(17)} y ${p(27)}`, nota: 'Región Central de Colombia / área de influencia del corredor.' },
  objetivosSociales: { valor: 'Integración regional, progreso de la población, equidad y seguridad, y oportunidades de formación y producción', marca: 'F' as Marca, fuente: p(27) },
  empleo:            { valor: 'No reportado para la Ferropista', marca: 'DA' as Marca,
                       fuente: 'Vacío identificado por el Semillero GEOPAV',
                       nota: 'La ponencia NO cuantifica el empleo atribuible a la Ferropista. Las cifras de 150.000 empleos en construcción y 25.000 en O&M pertenecen al proyecto Estrella Andina (diapositiva 32), que es 10 veces mayor. Atribuirlas al túnel de 58 km infla el proyecto en un orden de magnitud.' },
} as const;

/* ================================================================
   6. ESTRELLA ANDINA — proyecto macro, NO es la Ferropista
   ================================================================ */
export const ESTRELLA_ANDINA = {
  advertencia:
    'Estrella Andina es el proyecto macro del que la Ferropista es la primera pieza. Sus cifras NO ' +
    'son atribuibles al túnel Ibagué – Armenia y se presentan aquí únicamente como contexto.',
  longitud:   { valor: '590 km',              n: 590,      marca: 'F' as Marca, fuente: p(32) },
  costo:      { valor: 'US$ 18,2 mil millones', n: 18200,  marca: 'F' as Marca, fuente: p(32) },
  poblacion:  { valor: '34 millones',         n: 34000000, marca: 'F' as Marca, fuente: p(32), nota: 'DANE 2020.' },
  viajeros:   { valor: '20 millones/año',     n: 20000000, marca: 'F' as Marca, fuente: p(32), nota: 'Previsión 2030.' },
  empleoObra: { valor: '150.000 empleos',     n: 150000,   marca: 'F' as Marca, fuente: p(32), nota: 'Construcción, instalaciones y fabricación de material. DE ESTRELLA ANDINA, no de la Ferropista.' },
  empleoOyM:  { valor: '25.000 empleos',      n: 25000,    marca: 'F' as Marca, fuente: p(32), nota: 'Operación y mantenimiento. DE ESTRELLA ANDINA, no de la Ferropista.' },
  servicio:   { valor: 'Pasajeros y cargas ligeras, vía doble, ancho estándar, tracción eléctrica', marca: 'F' as Marca, fuente: p(32) },
} as const;

/* ================================================================
   7. FICHA TÉCNICA PRELIMINAR — hipótesis del semillero
   ================================================================ */
export const HIPOTESIS_TECNICAS = {
  advertencia:
    'Los parámetros de esta sección NO provienen de la ponencia. Son hipótesis de trabajo que el ' +
    'semillero adopta para poder razonar sobre el sistema, con la justificación de ingeniería de cada ' +
    'una. No son especificaciones del proyecto y no deben citarse como tales.',
  anchoVia:      { valor: '1.435 mm', marca: 'H' as Marca, fuente: HIP,
                   nota: 'Ancho estándar UIC. La ponencia lo declara para Estrella Andina (diapositiva 32); se asume continuidad para la Ferropista, pero no está confirmado.' },
  seccionTunel:  { valor: 'Por definir', marca: 'DA' as Marca, fuente: 'Vacío de la fuente',
                   nota: 'La ponencia no reporta sección transversal ni gálibo. Sin ese dato no puede verificarse el volumen de excavación declarado ni dimensionarse la ventilación.' },
  ventilacion:   { valor: 'Longitudinal con pozos de extracción intermedios', marca: 'F' as Marca, fuente: p(20),
                   nota: 'La tracción eléctrica elimina emisiones de combustión dentro del túnel, pero el sistema debe manejar la carga térmica de la tracción y el control de humos ante un incendio de la carga transportada.' },
  normativa:     { valor: 'NFPA 130 y fichas UIC como marco de referencia', marca: 'H' as Marca, fuente: HIP,
                   nota: 'La NFPA 130 está orientada a sistemas de transporte de pasajeros y no cubre directamente una autopista rodante de carga. Para esta tipología las referencias pertinentes son las fichas UIC, la especificación europea TSI-SRT y la experiencia operativa del Eurotúnel. En Colombia no existe norma específica para túneles ferroviarios de esta tipología: es un vacío normativo que el semillero señala como hallazgo. El semillero no puede afirmar que un diseño cumple una norma, porque no dispone del diseño.' },
  geotecnia: {
    df:        { valor: '1,00 m',  n: 1.0,  marca: 'H' as Marca, fuente: HIP, nota: 'Profundidad de desplante. Rango de sensibilidad: 0,80 – 1,50 m.' },
    cohesion:  { valor: '14 kPa',  n: 14,   marca: 'H' as Marca, fuente: HIP, nota: 'Cohesión interceptada. Rango de sensibilidad: 10 – 20 kPa.' },
    fs:        { valor: '3,0',     n: 3.0,  marca: 'H' as Marca, fuente: 'NSR-10, Título H' },
    metodo:    { valor: 'Meyerhof (NSR-10, Título H)', marca: 'H' as Marca, fuente: 'NSR-10, Título H' },
    limitacion:'No existe exploración de subsuelo del corredor accesible al semillero: ni sondeos, ni ensayos SPT, ni caracterización de laboratorio en los sitios de portal. Ningún valor de capacidad portante calculado con estas hipótesis puede usarse para diseño. El producto del objetivo específico 3 es una memoria metodológica que demuestra el procedimiento y acota órdenes de magnitud.',
  },
} as const;

/* ================================================================
   8. TRAZADO GEORREFERENCIADO — preliminar
   ================================================================ */
export const GEO = {
  /**
   * RESUELTO por el objetivo específico 1 (1 sep 2026).
   * Los portales ya NO son aproximados: se localizaron sobre el Copernicus DEM GLO-30
   * buscando los píxeles a 950 y 1450 msnm que declara la ponencia (diapositiva 20),
   * y se escogió el par que minimiza la distancia entre ellos, entre TODOS los candidatos
   * cuya cota difiere del objetivo en 2 m o menos (tolerancia adoptada [H]). Esa tolerancia,
   * y no el método, decide dónde caen los portales: variarla entre 2 y 15 m mueve la
   * longitud 690 m y el porcentaje de trazado con más de 700 m de cobertura en 12 puntos.
   * Tabla de sensibilidad: OE1_Topografia/Act2_Portales/portales_sensibilidad.csv
   * La ventana de búsqueda es la SEGUNDA hipótesis que decide el resultado, y era una
   * restricción activa: el portal oriental cae a ~440 m del borde de su propia ventana.
   * Ampliarla acorta el túnel 2.478 m pero traslada el portal a Rovira y el trazado pasa a
   * cruzar cinco municipios. Se conserva y se declara.
   * Tabla: OE1_Topografia/Act2_Portales/ventanas_sensibilidad.csv
   * Ver Memoria_calculo_OE1.docx para el método completo.
   */
  nota:
    'Trazado preliminar de nivel conceptual, obtenido con Copernicus DEM GLO-30 (~30 m). ' +
    'La ubicación de los portales responde a un criterio geométrico, no geotécnico: falta ' +
    'cruzarla con la susceptibilidad a movimientos en masa (objetivo específico 3). No constituye diseño.',
  centro:        [4.43, -75.42] as [number, number],
  portalIbague:  [4.3640, -75.1960] as [number, number],
  portalArmenia: [4.4800, -75.6520] as [number, number],
  /* Los nombres portalArmenia y cotaPortalArmenia se conservan por compatibilidad con los
     componentes que los consumen. OJO: el portal occidental NO está en Armenia, sino en
     Calarcá, Quindío (DANE 63130). «Armenia» es como la ponencia nombra el extremo del
     corredor [F, dia. 20]; la jurisdicción se verificó contra la capa de municipios del IGAC. */
  cotaPortalIbague: 951,
  cotaPortalArmenia: 1452,
  municipioPortalIbague:  { nombre: 'Ibagué',  depto: 'Tolima',  codDane: '73001' },
  municipioPortalArmenia: { nombre: 'Calarcá', depto: 'Quindío', codDane: '63130' },
  longitudKm: 52.212,
  estado: 'calculado' as const,
  fuenteDEM: 'Copernicus DEM GLO-30 (ESA/Airbus), ~30 m, EPSG:4326',
  /**
   * Por qué 52,21 km no contradice los 58 km de la ponencia: los 58 km son el corredor
   * completo, con tramos a cielo abierto entre los 7 túneles de 7 a 8 km; el túnel
   * principal declarado son 44 km. La recta entre portales queda entre ambos valores.
   */

  /* --------------------------------------------------------------------------
     CIFRAS DEL OBJETIVO ESPECÍFICO 1 — salida de cifras_OE1.json v2 (8 sep 2026).
     Producto del procesamiento reproducible del corredor sobre el Copernicus DEM
     GLO-30. Todas marca CP salvo la tolerancia de cota, que es hipótesis [H].
     Ningún componente puede volver a escribir estos números a mano: se leen de aquí.
     -------------------------------------------------------------------------- */
  longitud:         { valor: '52,212 km',    n: 52211.8, marca: 'CP' as Marca, fuente: CALC,
                      nota: 'Geodésica WGS 84 entre portales: 52.211,8 m. Los 58 km de la ponencia son el corredor completo con tramos a cielo abierto; el túnel principal declarado son 44 km. La recta entre portales queda entre ambos.' },
  pendiente:        { valor: '0,959 %',      n: 0.9586,  marca: 'CP' as Marca, fuente: CALC,
                      nota: 'i = 500,5 m / 52.211,8 m = 0,9586 %; se publica redondeada a 0,959 %. Criterio ferroviario de carga adoptado por el semillero: < 1,5 %. Cumple.' },
  desnivel:         { valor: '500,5 m',      n: 500.5,   marca: 'CP' as Marca, fuente: CALC,
                      nota: '1.451,5 − 951,0 msnm entre los portales localizados sobre el DEM.' },
  cotaMaxTerreno:   { valor: '3.393,0 msnm', n: 3393,    marca: 'CP' as Marca, fuente: CALC,
                      nota: 'Cota máxima del terreno sobre el eje del trazado, en el PK 42,8. No es comparable con los 3.300 msnm que la ponencia atribuye al paso del Alto de La Línea: ese es el paso carretero actual, que no está sobre este eje.' },
  coberturaMax:     { valor: '2.031,4 m',    n: 2031.4,  marca: 'CP' as Marca, fuente: CALC,
                      nota: 'Máximo de la diferencia terreno − rasante sobre 1.500 puntos. Ocurre en el PK 42,8.' },
  coberturaMaxPk:   { valor: 'PK 42,8',      n: 42.8,    marca: 'CP' as Marca, fuente: CALC,
                      nota: 'Abscisa de la cobertura máxima, medida desde el portal oriental.' },
  coberturaMedia:   { valor: '840,2 m',      n: 840.2,   marca: 'CP' as Marca, fuente: CALC,
                      nota: 'Promedio de la cobertura sobre los 1.500 puntos del perfil de cálculo. La curva que publica el sitio remuestrea ese perfil a 401 puntos y da 842,1 m: la diferencia de 1,9 m (0,2 %) es del remuestreo de la curva, no del cálculo.' },
  pctCobertura700:  { valor: '60,7 %',       n: 60.7,    marca: 'CP' as Marca, fuente: CALC,
                      nota: 'Fracción del trazado con más de 700 m de roca sobre la clave. Insumo del OE 4 para contrastar tuneladora frente a excavación convencional.' },
  pctCobertura1200: { valor: '20,1 %',       n: 20.1,    marca: 'CP' as Marca, fuente: CALC,
                      nota: '10,5 km del trazado con más de 1.200 m de cobertura.' },
  errorDEM:         { valor: '35 m',         n: 35,      marca: 'CP' as Marca, fuente: CALC,
                      nota: 'Error medio absoluto del DEM contrastado contra cotas de cascos urbanos. Del orden de un píxel del modelo.' },
  toleranciaCota:   { valor: '2,0 m',        n: 2.0,     marca: 'H'  as Marca, fuente: HIP,
                      nota: 'Tolerancia adoptada para aceptar un píxel del DEM como cota de portal. Es una hipótesis de trabajo, no un dato medido, y decide dónde caen los portales: la sensibilidad está tabulada en OE1_Topografia/Act2_Portales/portales_sensibilidad.csv.' },
  nAbscisas:        { valor: '106',          n: 106,     marca: 'CP' as Marca, fuente: CALC,
                      nota: 'Abscisas de la cartera de rasantes: paso de 500 m más el cierre en cada portal.' },
  cierrePortales:   { valor: '0,00 m',       n: 0,       marca: 'CP' as Marca, fuente: CALC,
                      nota: 'Diferencia entre la rasante de pendiente constante y la cota de portal en ambos extremos.' },
  /**
   * Distribución de la cobertura por rangos, sobre 1.500 puntos del perfil [CP].
   * Fuente: cifras_OE1.json v2. La sección del OE 1 la consume para la barra apilada.
   */
  distribucionCobertura: [
    { rango: '0 – 100 m',     km: 2.1,  pct: 3.9  },
    { rango: '100 – 300 m',   km: 5.2,  pct: 9.9  },
    { rango: '300 – 700 m',   km: 13.3, pct: 25.4 },
    { rango: '700 – 1.200 m', km: 21.2, pct: 40.6 },
    { rango: '> 1.200 m',     km: 10.5, pct: 20.1 },
  ],

  /** Municipios de referencia, en su ubicación real. */
  referencias: [
    { nombre: 'Ibagué',             coords: [4.4389, -75.2322] as [number, number] },
    { nombre: 'Cajamarca',          coords: [4.4267, -75.4275] as [number, number] },
    { nombre: 'Calarcá',            coords: [4.5222, -75.6497] as [number, number] },
    { nombre: 'Armenia',            coords: [4.5339, -75.6811] as [number, number] },
  ],
} as const;

/* ================================================================
   9. VACÍOS DE LA FUENTE — delimitan el alcance del semillero
   ================================================================ */
export const VACIOS = [
  { tema: 'Exploración de subsuelo en portales', consecuencia: 'Todos los parámetros geotécnicos son hipótesis; el producto es metodológico, no de diseño.' },
  { tema: 'Clasificación geomecánica (RMR) por tramos', consecuencia: 'La sectorización TBM / convencional se infiere de cartografía regional del SGC, con la incertidumbre que ello implica.' },
  { tema: 'Sección transversal y gálibo del túnel', consecuencia: 'Impide verificar el volumen de excavación declarado y dimensionar la ventilación.' },
  { tema: 'Huella de carbono de la construcción', consecuencia: 'El balance ambiental neto no puede cerrarse.' },
  { tema: 'Tasa agregada de siniestralidad del paso', consecuencia: 'La ponencia no la aporta. El semillero la construyó en el objetivo específico 5 desde la ANSV y la serie histórica de INVÍAS: 7,66 fallecidos por cada 100 millones de vehículos-kilómetro en el paso. Vacío cerrado.' },
  { tema: 'Empleo atribuible a la Ferropista', consecuencia: 'La ponencia solo reporta empleo para Estrella Andina; no puede trasladarse al túnel.' },
] as const;

export const EQUIPO = {
  semillero: 'Semillero de Investigación GEOPAV',
  universidad: 'Universidad de Ibagué',
  programa: 'Semestre Paz y Región 2026B',
  interlocutora: 'Ing. María Paula Salazar Susunaga',
  asesorRegional: 'Juan Sebastián Rojas Penagos',
  integrantes: [
    { nombre: 'Castaño Cifuentes Maicol Stiven', linea: 'Diagnóstico vial y métodos de obra subterránea' },
    { nombre: 'Tamayo Osorio Miguel Ángel',      linea: 'Topografía del trazado y geotecnia de portales' },
    { nombre: 'Torrente Parra Daniel Ignacio',   linea: 'Plataforma geoespacial, consulta ciudadana y análisis logístico' },
  ],
} as const;

/* ================================================================
   10. PLAN DE ACCIÓN — Semestre Paz y Región 2026B
   Estructura aprobada: 1 objetivo general, 2 objetivos específicos
   por integrante + 1 conjunto (7 en total), mínimo 5 actividades y
   1 producto por objetivo.
   ================================================================ */

export type EstadoItem = 'pendiente' | 'en_curso' | 'completado';

export interface Actividad {
  n: number;
  titulo: string;
  inicio: string;
  fin: string;
  tipo: 'Producto' | 'Verificador';
  entregable: string;
  formato: string;
  estado: EstadoItem;
}

export interface ObjetivoEspecifico {
  id: string;
  numero: number;
  titulo: string;
  responsable: string;
  bloque: 1 | 2 | 3;
  inicio: string;
  fin: string;
  linea: string;
  estado: EstadoItem;
  actividades: Actividad[];
}

export const OBJETIVO_GENERAL =
  'Analizar la propuesta de túnel de base ferroviario Ferropista para el cruce de la Cordillera ' +
  'Central en el tramo Ibagué – Armenia, mediante la caracterización topográfica, geotécnica y ' +
  'logística preliminar del corredor y la verificación de sus indicadores de impacto económico, ' +
  'social, ambiental y de seguridad vial, durante el semestre académico 2026B.';

export const BLOQUES = [
  { n: 1 as const, rango: '1 sep – 3 oct 2026', descripcion: 'Trabajo individual en paralelo: caracterización de partida' },
  { n: 2 as const, rango: '5 oct – 7 nov 2026', descripcion: 'Trabajo individual en paralelo: análisis y modelación' },
  { n: 3 as const, rango: '9 – 27 nov 2026',    descripcion: 'Trabajo conjunto: integración, balance y entrega final' },
] as const;

export const NOTA_PARALELISMO =
  'En los bloques 1 y 2 los tres integrantes avanzan al mismo tiempo, cada uno sobre su propio ' +
  'objetivo. La simultaneidad entre objetivos no implica sobrecarga: corresponde a personas distintas.';

const A = (n: number, titulo: string, inicio: string, fin: string,
           tipo: 'Producto' | 'Verificador', entregable: string, formato: string,
           estado: EstadoItem = 'pendiente'): Actividad =>
  ({ n, titulo, inicio, fin, tipo, entregable, formato, estado });

export const PLAN_ACCION: ObjetivoEspecifico[] = [
  {
    id: 'oe1', numero: 1, bloque: 1, inicio: '1 sep 2026', fin: '3 oct 2026',
    responsable: 'Tamayo Osorio Miguel Ángel',
    linea: 'Topografía y trazado',
    estado: 'completado',
    titulo: 'Analizar el perfil topográfico del corredor Ibagué – Armenia mediante un Modelo de Elevación Digital, para definir el trazado espacial preliminar del túnel de base y verificar la pendiente longitudinal admisible para tracción ferroviaria de carga.',
    actividades: [
      A(1, 'Descarga y validación del Modelo de Elevación Digital del corredor (Copernicus DEM GLO-30, ~30 m).', '1 sep 2026', '7 sep 2026', 'Verificador', 'Repositorio ráster documentado', 'Archivo GeoTIFF', 'completado'),
      A(2, 'Georreferenciación de las cotas de los portales de Ibagué (950 msnm) y Armenia (1.450 msnm) sobre el DEM.', '8 sep 2026', '14 sep 2026', 'Verificador', 'Puntos de control de portales', 'Archivo Shapefile', 'completado'),
      A(3, 'Ejecución de los geoprocesos de trazado en QGIS: recorte del DEM, relieve sombreado, localización de portales y perfil sobre el modelo.', '15 sep 2026', '21 sep 2026', 'Verificador', 'Registro de geoprocesos', 'Captura de pantalla', 'completado'),
      A(4, 'Trazado de la ruta preliminar del túnel de base y cálculo de la pendiente longitudinal media.', '22 sep 2026', '28 sep 2026', 'Producto', 'Trazado georreferenciado del túnel', 'Archivo GeoJSON', 'completado'),
      A(5, 'Elaboración del perfil longitudinal y de la cartera de rasantes del trazado.', '29 sep 2026', '3 oct 2026', 'Producto', 'Perfil topográfico longitudinal', 'Archivo Excel / PDF', 'completado'),
    ],
  },
  {
    id: 'oe2', numero: 2, bloque: 1, inicio: '1 sep 2026', fin: '3 oct 2026',
    responsable: 'Torrente Parra Daniel Ignacio',
    linea: 'Plataforma geoespacial y consulta ciudadana',
    estado: 'en_curso',
    titulo: 'Desarrollar una plataforma web geoespacial que visualice el trazado y los indicadores del proyecto, y que aloje un instrumento de consulta ciudadana sobre percepción de riesgo vial en el corredor.',
    actividades: [
      A(1, 'Configuración del repositorio y del entorno de desarrollo de la plataforma web.', '1 sep 2026', '7 sep 2026', 'Verificador', 'Repositorio de control de versiones', 'Enlace (URL)', 'completado'),
      A(2, 'Integración del visor cartográfico con el trazado georreferenciado del objetivo 1.', '8 sep 2026', '14 sep 2026', 'Producto', 'Módulo de mapa interactivo', 'Enlace (URL)', 'completado'),
      A(3, 'Diseño y validación del instrumento de consulta ciudadana sobre percepción de riesgo vial.', '15 sep 2026', '21 sep 2026', 'Verificador', 'Cuestionario validado', 'Documento PDF', 'completado'),
      A(4, 'Integración del formulario de consulta y despliegue público de la plataforma.', '22 sep 2026', '28 sep 2026', 'Producto', 'Plataforma web publicada', 'Enlace Web (URL)', 'completado'),
      A(5, 'Difusión del instrumento y apertura de la ventana de recolección de respuestas.', '29 sep 2026', '3 oct 2026', 'Verificador', 'Registro de difusión y respuestas', 'Archivo Excel', 'en_curso'),
    ],
  },
  {
    id: 'oe5', numero: 5, bloque: 1, inicio: '1 sep 2026', fin: '3 oct 2026',
    responsable: 'Castaño Cifuentes Maicol Stiven',
    linea: 'Diagnóstico vial',
    estado: 'completado',
    titulo: 'Cuantificar los volúmenes de tránsito de vehículos pesados y los índices de siniestralidad del paso de La Línea, a partir de fuentes oficiales de INVÍAS y de la Agencia Nacional de Seguridad Vial.',
    actividades: [
      A(1, 'Extracción de las series de volúmenes de tránsito de INVÍAS para la estación del sector La Línea.', '1 sep 2026', '7 sep 2026', 'Verificador', 'Base de datos cruda de aforos', 'Archivo CSV / Excel', 'completado'),
      A(2, 'Clasificación vehicular del TPDA y depuración del flujo de carga pesada.', '8 sep 2026', '14 sep 2026', 'Producto', 'Matriz de aforos clasificada', 'Documento Excel', 'completado'),
      A(3, 'Recopilación de reportes de siniestralidad de la ANSV para los municipios del corredor.', '15 sep 2026', '21 sep 2026', 'Verificador', 'Histórico de siniestros', 'Documento PDF', 'completado'),
      A(4, 'Análisis estadístico de la siniestralidad de vehículos pesados en el descenso del paso.', '22 sep 2026', '28 sep 2026', 'Producto', 'Gráficos de siniestralidad', 'Archivo Excel / JPG', 'completado'),
      A(5, 'Consolidación del diagnóstico operacional de la infraestructura vial actual.', '29 sep 2026', '3 oct 2026', 'Producto', 'Informe de diagnóstico vial', 'Documento PDF', 'completado'),
    ],
  },
  {
    id: 'oe3', numero: 3, bloque: 2, inicio: '5 oct 2026', fin: '7 nov 2026',
    responsable: 'Tamayo Osorio Miguel Ángel',
    linea: 'Geotecnia de portales',
    estado: 'pendiente',
    titulo: 'Estimar la capacidad portante preliminar del terreno de fundación de las infraestructuras de superficie en los portales de Ibagué y Armenia, aplicando la formulación de Meyerhof bajo los lineamientos del Título H de la NSR-10.',
    actividades: [
      A(1, 'Recopilación de la cartografía geológica del Servicio Geológico Colombiano para las planchas del corredor.', '5 oct 2026', '11 oct 2026', 'Verificador', 'Planos geológicos', 'Documento PDF'),
      A(2, 'Identificación de zonas de susceptibilidad a movimientos en masa en el entorno de los portales.', '12 oct 2026', '18 oct 2026', 'Verificador', 'Mapa base de susceptibilidad', 'Documento PDF / JPG'),
      A(3, 'Definición de los parámetros geotécnicos de diseño adoptados y de su rango de sensibilidad.', '19 oct 2026', '25 oct 2026', 'Verificador', 'Cuadro de parámetros adoptados', 'Documento Excel'),
      A(4, 'Cálculo de la capacidad portante admisible por la formulación de Meyerhof (NSR-10, Título H).', '26 oct 2026', '1 nov 2026', 'Producto', 'Memoria de cálculo', 'Documento Excel'),
      A(5, 'Diseño conceptual de la cimentación superficial de las terminales de carga Ro-Ro.', '2 nov 2026', '7 nov 2026', 'Producto', 'Esquema de cimentación e informe', 'Plano AutoCAD / PDF'),
    ],
  },
  {
    id: 'oe4', numero: 4, bloque: 2, inicio: '5 oct 2026', fin: '7 nov 2026',
    responsable: 'Castaño Cifuentes Maicol Stiven',
    linea: 'Métodos de obra subterránea',
    estado: 'pendiente',
    titulo: 'Estructurar la metodología de excavación recomendada, contrastando el método mecanizado con tuneladora frente al método convencional, a partir de la caracterización geológica regional del macizo.',
    actividades: [
      A(1, 'Caracterización litológica y de zonas de falla del macizo a partir de la cartografía del SGC.', '5 oct 2026', '11 oct 2026', 'Verificador', 'Matriz litológica', 'Documento Excel'),
      A(2, 'Definición de los tramos con condiciones favorables para excavación mecanizada con tuneladora.', '12 oct 2026', '18 oct 2026', 'Producto', 'Esquema de sectorización', 'Plano AutoCAD / PDF'),
      A(3, 'Definición de los tramos críticos para excavación convencional y de su sostenimiento primario.', '19 oct 2026', '25 oct 2026', 'Producto', 'Cuadro de sostenimientos', 'Documento Word / PDF'),
      A(4, 'Planteamiento conceptual del sistema de ventilación longitudinal del túnel.', '26 oct 2026', '1 nov 2026', 'Verificador', 'Diagrama de flujo de aire', 'Esquema gráfico (JPG)'),
      A(5, 'Elaboración del informe de métodos constructivos subterráneos.', '2 nov 2026', '7 nov 2026', 'Producto', 'Informe de túneles', 'Documento PDF'),
    ],
  },
  {
    id: 'oe6', numero: 6, bloque: 2, inicio: '5 oct 2026', fin: '7 nov 2026',
    responsable: 'Torrente Parra Daniel Ignacio',
    linea: 'Eficiencia logística',
    estado: 'pendiente',
    titulo: 'Determinar la eficiencia logística del sistema intermodal Ferropista, calculando la reducción de tiempos de ciclo y de costos operativos frente a la operación actual por la Ruta 40.',
    actividades: [
      A(1, 'Levantamiento de los tiempos de ciclo actuales del cruce por la Ruta 40.', '5 oct 2026', '11 oct 2026', 'Verificador', 'Registro de tiempos', 'Documento Excel'),
      A(2, 'Cálculo del tiempo de ciclo del sistema Ferropista (carga, desplazamiento y descarga).', '12 oct 2026', '18 oct 2026', 'Producto', 'Memoria de tiempos logísticos', 'Documento Excel'),
      A(3, 'Estructuración de la matriz de costos operativos unitarios del transporte de carga.', '19 oct 2026', '25 oct 2026', 'Verificador', 'Matriz de costos unitarios', 'Documento Excel'),
      A(4, 'Proyección de los ahorros operativos anuales para el sector transportador.', '26 oct 2026', '1 nov 2026', 'Producto', 'Modelo de ahorros operativos', 'Documento Excel'),
      A(5, 'Redacción del reporte de eficiencia logística comparada.', '2 nov 2026', '7 nov 2026', 'Producto', 'Informe económico-logístico', 'Documento PDF'),
    ],
  },
  {
    id: 'oe7', numero: 7, bloque: 3, inicio: '9 nov 2026', fin: '27 nov 2026',
    responsable: 'TODO EL EQUIPO',
    linea: 'Integración y entrega',
    estado: 'pendiente',
    titulo: 'Consolidar el análisis integral del proyecto, articulando los resultados topográficos, geotécnicos, viales y logísticos con la evaluación de externalidades ambientales y de impacto social regional derivada de la consulta ciudadana.',
    actividades: [
      A(1, 'Cálculo de las emisiones de gases de efecto invernadero evitadas por el cambio modal en el cruce.', '9 nov 2026', '12 nov 2026', 'Producto', 'Matriz de emisiones GEI', 'Documento Excel'),
      A(2, 'Procesamiento y análisis de los resultados de la consulta ciudadana de percepción de riesgo.', '13 nov 2026', '16 nov 2026', 'Producto', 'Informe de resultados de la consulta', 'Documento PDF'),
      A(3, 'Ensamble de los capítulos topográfico, geotécnico, vial y logístico.', '17 nov 2026', '20 nov 2026', 'Verificador', 'Documento borrador integral', 'Documento Word'),
      A(4, 'Revisión por pares y corrección de estilo técnico del documento.', '21 nov 2026', '24 nov 2026', 'Verificador', 'Acta de revisión del equipo', 'Documento PDF'),
      A(5, 'Entrega oficial del informe final del proyecto Ferropista Cordillera Central.', '25 nov 2026', '27 nov 2026', 'Producto', 'Informe Final Paz y Región', 'Documento PDF'),
    ],
  },
];

export const ODS = [
  { n: 3,  nombre: 'Salud y bienestar',                     relacion: 'Meta 3.6: reducir las muertes y lesiones por accidentes de tránsito. Vínculo directo del eje de seguridad vial.' },
  { n: 8,  nombre: 'Trabajo decente y crecimiento económico', relacion: 'Productividad del transporte de carga y dinamización económica de Tolima y Quindío.' },
  { n: 9,  nombre: 'Industria, innovación e infraestructura', relacion: 'Infraestructura de transporte resiliente para el principal corredor logístico del país.' },
  { n: 11, nombre: 'Ciudades y comunidades sostenibles',      relacion: 'Reducción del tránsito pesado por Cajamarca y los cascos poblados del corredor.' },
  { n: 13, nombre: 'Acción por el clima',                     relacion: 'Reducción del 90 % de emisiones GEI y consumos energéticos del cruce por cambio modal.' },
] as const;

export const LIMITACIONES = [
  'La línea base de siniestralidad es anterior al Túnel de La Línea, que abrió el 4 de septiembre de 2020: los fallecidos que publica la ANSV son de 2015 a 2019. La tasa caracteriza el corredor de ese periodo y sobrestima el riesgo del corredor actual. La objeción anterior — que el aforo disponible empezaba en octubre de 2021 y no era divisible entre los mismos años — quedó resuelta el 8 de septiembre de 2026 con la serie histórica de INVÍAS, que aforó la misma vía y el mismo tramo entre 2015 y 2018.',
  'El registro de fallecidos cubre cinco años (2015–2019) y el aforo de INVÍAS cuatro (2015–2018). El cálculo supone que 2019 tuvo un tránsito parecido. La hipótesis se declara y se acota: el aforo medido del peaje Cajamarca de 2019 mueve la tasa un 1,0 %.',
  'El Modelo de Elevación Digital disponible libremente tiene resolución de 12,5 a 30 m. El trazado resultante es de nivel conceptual; no constituye un diseño geométrico.',
  'No existe exploración de subsuelo del corredor accesible al equipo. Todos los parámetros geotécnicos se declaran como hipótesis y se presentan con análisis de sensibilidad.',
  'La consulta ciudadana en línea produce una muestra no probabilística. Sus resultados son indicativos de percepción y no constituyen estadística poblacional.',
  'La fuente presenta una inconsistencia interna en las horas ahorradas (5,0 frente a 5,3 millones al año). Se documenta el rango en lugar de escoger un valor en silencio.',
] as const;
