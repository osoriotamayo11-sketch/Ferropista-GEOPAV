# Ferropista Cordillera Central — Semillero GEOPAV

Sitio de análisis académico del **Semillero de Investigación GEOPAV**, Universidad de Ibagué,
Semestre Paz y Región 2026B. Es el producto del **objetivo específico 2** del Plan de Acción.

Analiza una propuesta de terceros: el túnel de base ferroviario "Ferropista" en el tramo
Ibagué – Armenia, iniciativa privada de **ARCS y UC Consult**.

## REGLA NÚMERO UNO: ninguna cifra sin fuente

Este proyecto tuvo que ser saneado porque una versión anterior contenía ~45 cifras inventadas,
citas fabricadas atribuidas a INVÍAS, ANSV, DNP y SGC, y una identidad institucional falsa
("Consorcio Ferropista Cordillera Central", con dominio, correo y teléfono inexistentes).

**No inventes datos, fuentes, contactos ni identidad institucional. Nunca. Bajo ningún
pretexto, ni siquiera como placeholder o dato de ejemplo.**

Si necesitas un valor que no tienes, usa la marca `DA` (dato abierto pendiente) y deja
explícito que falta. Es preferible una página que diga "pendiente" a una que mienta.

## Fuente única de verdad: `src/data/proyecto.ts`

Toda cifra que aparezca en la interfaz se importa de ahí. **Ningún componente declara cifras
propias.** Eso hace estructuralmente imposible que dos secciones se contradigan.

Cada dato lleva su marca de origen:

| Marca | Significado |
|---|---|
| `F`  | Dato de la ponencia de referencia, citando la diapositiva |
| `CP` | Cálculo propio del semillero, reproducible de forma independiente |
| `H`  | Hipótesis de trabajo — NO es un dato medido, y así debe rotularse |
| `DA` | Dato abierto pendiente de consultar en fuente oficial |

Flujo para agregar cualquier cifra nueva:

1. Entra primero a `src/data/proyecto.ts`, con su marca y su fuente.
2. Solo después se consume desde el componente.
3. Si no puede recibir marca `F`, `CP`, `H` o `DA`, no se publica.

## Fuente primaria del proyecto

Fernández Ordóñez, H. O. (2025). *Túnel para cruce férreo de la Cordillera Central de los
Andes y semilla para la Estrella Andina* [Ponencia]. XX Seminario Andino de Túneles y Obras
Subterráneas — II ExpoTúneles, Sociedad Antioqueña de Ingenieros y Arquitectos. Medellín,
8 de octubre de 2025. Iniciativa de ARCS y UC Consult. 38 diapositivas.

Es un documento de **promoción de una iniciativa privada** hacia una APP. Sus cifras de
impacto son estimaciones del proponente, no auditadas por un tercero. Verificarlas es
justamente el objeto del trabajo del semillero.

## Datos clave verificados (no los cambies sin revisar la ponencia)

| Dato | Valor | Diapositiva |
|---|---|---|
| Longitud total / túnel principal | 58 km / 44 km | 20 |
| CAPEX | US$ 2.800 millones | 20 |
| Cotas de portales Ibagué / Armenia | 950 / 1.450 msnm | 20 |
| Cota evitada del paso actual | 3.300 msnm | 20 |
| Fase inicial | 140 trenes/día, 35 tractomulas por tren | 20 |
| Excavación TBM / convencional | mín. 27,5 km / 36,7 km | 22 |
| Ciclo de operación | 25 + 30 + 15 = 70 min | 23 |
| Tránsito (INVÍAS 2017) | 2.100 grandes + 1.700 medianos/día | 10 |
| Velocidad media actual | < 20 km/h | 13 |
| Tiempo de cruce actual | 4 h (valor medio) | 29 |
| Reducción de GEI y energía | 90 % (NO es cero) | 25 |
| Costos externos evitados a 50 años | $COP 138,5 billones | 26 |
| Recaudo fiscal a 50 años | $COP 60,2 billones (NO son ahorros) | 28 |

Cálculos propios: pendiente media **0,86 %** = (1.450 − 950) / 58.000 · capacidad diaria
**4.900 veh/día** = 140 × 35 · velocidad comercial implícita **88 km/h** = 44 km / 0,5 h.

## Errores que NO deben reaparecer

- Atribuir a la Ferropista los **150.000 empleos de construcción y 25.000 de O&M**: son del
  proyecto **Estrella Andina** (590 km, US$ 18,2 mil millones), diapositiva 32.
- Presentar los **$COP 60,2 billones** como ahorros: son recaudo fiscal del Estado.
- Decir que el tiempo de cruce baja a **30 minutos**: esos son solo de desplazamiento. El
  ciclo integrado es de **70 minutos**, porque hay 40 de operación en terminal.
- Decir **cero emisiones**: la fuente dice 90 % de reducción.
- Afirmar pendientes del **12 %** en la Ruta 40: es vía nacional primaria, 6–8 % de diseño.
- Capacidad de **30.000 veh/día**: son 4.900.
- Cualquier cifra de siniestralidad anual: la ponencia solo la documenta cualitativamente con
  casos de prensa. La cuantificación es el objetivo específico 5, con datos de la ANSV.

## Identidad del sitio

Trabajo académico del Semillero GEOPAV, Universidad de Ibagué. **No representa a ARCS ni a
UC Consult y no habla por ellos.** El sitio oficial del proyecto es ferropista.com.

No agregues correos, teléfonos, dominios ni razones sociales que no existan.

## Plan de Acción

`PLAN_ACCION` en `src/data/proyecto.ts` define 7 objetivos específicos (2 por integrante más
1 conjunto), 5 actividades cada uno, mínimo 1 producto por objetivo. La sección `#plan` del
sitio lo renderiza, y la lista de entregables de `DownloadSection` se deriva automáticamente
filtrando las actividades de tipo `Producto`.

Para actualizar el avance, edita el campo `estado` (`pendiente` | `en_curso` | `completado`)
del objetivo o de la actividad. No toques el componente.

| OE | Responsable | Bloque |
|---|---|---|
| 1 Topografía y trazado (DEM) | Tamayo Osorio Miguel Ángel | 1 sep – 3 oct |
| 2 Plataforma web y consulta ciudadana | Torrente Parra Daniel Ignacio | 1 sep – 3 oct |
| 5 Diagnóstico vial (TPDA y siniestralidad) | Castaño Cifuentes Maicol Stiven | 1 sep – 3 oct |
| 3 Geotecnia de portales | Tamayo Osorio Miguel Ángel | 5 oct – 7 nov |
| 4 Métodos de excavación | Castaño Cifuentes Maicol Stiven | 5 oct – 7 nov |
| 6 Eficiencia logística | Torrente Parra Daniel Ignacio | 5 oct – 7 nov |
| 7 Integración y entrega | Todo el equipo | 9 – 27 nov |

## Mapa: trazado preliminar

`ProjectMap.tsx` dibuja un trazado **indicativo, no métrico**. Los portales graficados están
a 50,9 km en línea recta, pero la ponencia declara 44 km de túnel principal sobre 58 km de
tramo. Esa diferencia se resuelve en el **OE 1** con un Modelo de Elevación Digital.

Cuando el OE 1 produzca el GeoJSON, se actualiza `GEO` en la capa de datos y el mapa se
corrige solo. No ajustes coordenadas a ojo para "que cuadre".

## Comandos

```bash
npm run dev      # desarrollo en localhost:3000
npm run build    # build de producción — debe pasar antes de cualquier push
npm run lint
npx tsc --noEmit # chequeo de tipos
```

Vercel despliega automáticamente al hacer push a `main`.

## Stack

Next 15 (App Router) · React 19 · TypeScript · Tailwind · Leaflet + react-leaflet (importado
con `ssr: false`, no lo cambies) · Recharts · Framer Motion · Supabase.

`.env.local` tiene `NEXT_PUBLIC_SUPABASE_URL` y `SUPABASE_SERVICE_ROLE_KEY`. **La service
role key solo se usa en servidor, nunca en código que llegue al navegador.**

## Pendiente

- Tabla de Supabase para la consulta ciudadana del OE 2. Requisitos: no almacenar IP ni
  identificador de dispositivo; políticas RLS que permitan insertar pero no leer desde el
  cliente. El esquema está en `05_Instrumento_Consulta_Ciudadana.docx`.
- Definir `NEXT_PUBLIC_SITE_URL` en Vercel con la URL real del despliegue.

## Verificación antes de dar algo por terminado

1. `npm run build` pasa.
2. Mirar la página renderizada, no solo hacer grep. Tres datos inventados sobrevivieron a una
   revisión por texto y solo aparecieron al ver una captura del render.
3. Ninguna cifra nueva sin su marca de origen.
