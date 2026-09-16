# Ferropista Cordillera Central — análisis del Semillero GEOPAV

Análisis independiente de la propuesta de **túnel de base ferroviario «Ferropista»** para el
cruce de la Cordillera Central en el tramo Ibagué – Armenia (corredor Bogotá – Buenaventura,
paso del Alto de La Línea).

**Semillero de Investigación GEOPAV** · Programa de Ingeniería Civil · Universidad de Ibagué
Semestre Paz y Región 2026B.

Sitio publicado: **https://ferropista.vercel.app**

> **Postura.** El semillero **no representa ni promueve** la iniciativa. La analiza y la
> verifica de forma independiente. La Ferropista es una propuesta privada de ARCS / UC Consult
> presentada en el XX Seminario Andino de Túneles (SAI, Medellín, 8 de octubre de 2025); sus
> cifras son estimaciones del proponente, no auditadas por un tercero.

---

## Qué aporta este trabajo

No la conclusión, sino **el método**: cada cifra publicada lleva marca de origen y las
inconsistencias de la fuente se documentan en lugar de resolverse en silencio.

| Marca | Significado | Qué exige |
|---|---|---|
| `F` | Dato de la ponencia | Número de diapositiva citado |
| `CP` | Cálculo propio | Script publicado que lo reproduce |
| `H` | Hipótesis | Supuesto declarado en el texto, no escondido en el código |
| `DA` | Dato abierto por consultar | Fuente identificada y pendiente de descarga |

Una cifra sin marca no entra al sitio, ni al Plan de Acción, ni a una memoria.

---

## Qué hay en este repositorio

| Carpeta | Contenido |
|---|---|
| `src/` | Aplicación Next.js del sitio. `src/data/proyecto.ts` es la **fuente de verdad numérica**: ningún componente declara cifras propias |
| `OE1_Topografia/` | Objetivo 1 — perfil del corredor y trazado preliminar sobre modelo de elevación digital. Scripts de PyQGIS, carteras, GeoJSON y láminas |
| `OE2_Plataforma/` | Objetivo 2 — esquema de la base de datos de la consulta ciudadana |
| `OE5_SeguridadVial/` | Objetivo 5 — aforos de INVÍAS y de la ANI, sectores críticos de la ANSV, cálculo de la tasa de siniestralidad y sus figuras |
| `public/` | Láminas y recursos publicados en el sitio |

Estado a 16 de septiembre de 2026: **objetivos 1 y 5 cerrados**, objetivo 2 en curso con la
consulta ciudadana abierta. Los objetivos 3, 4, 6 y 7 empiezan en los bloques siguientes del
semestre.

---

## Qué NO está aquí, y por qué

Este espejo publica **el código y la evidencia reproducible**, no los datos brutos que
cualquiera puede descargar de su fuente original. Lo omitido y dónde conseguirlo:

- **Teselas del modelo de elevación Copernicus DEM GLO-30** (~43 MB cada una). Son obra de
  ESA/Airbus y se descargan sin registro del bucket público `copernicus-dem-30m` en AWS:
  - `Copernicus_DSM_COG_10_N04_00_W075_00_DEM.tif`
  - `Copernicus_DSM_COG_10_N04_00_W076_00_DEM.tif`
- **`dem_corredor.tif`** (91 MB) y **`DEM_area_estudio.tif`**. Son recortes derivados de esas
  teselas; `OE1_Topografia/Act3_Geoprocesos/procesamiento_OE1.py` los regenera.
- **Los límites municipales crudos del IGAC** (8,4 MB). El mismo script los descarga y recorta.
- **La ponencia de referencia en PDF.** Es obra de un tercero y no se redistribuye. Está citada
  diapositiva por diapositiva en `src/data/proyecto.ts`.
- **Variables de entorno.** Ninguna credencial se versiona, aquí ni en el repositorio de trabajo.

Sí se conserva `OE1_Topografia/Act1_DEM/DEM_corredor_recorte.tif` (16 MB): es el ráster exacto
sobre el que se calcularon las cotas publicadas, y sin él las cifras no serían reproducibles.

---

## Por qué este repositorio no tiene historial

Es un **espejo**: un único commit con el árbol de trabajo tal como está hoy, exportado con
`git archive`. El repositorio de desarrollo es privado y se queda así.

La razón se documenta en vez de disimularse. Una versión temprana del proyecto, redactada con
ayuda de un asistente sin verificación, incluía cifras inventadas, citas atribuidas a entidades
que nunca las publicaron y una identidad institucional falsa. Todo eso se purgó del árbol de
trabajo y quedó registrado en `CLAUDE.md`, pero **sigue existiendo en los commits antiguos**,
que por eso no se hacen públicos. Publicar el historial completo sería republicar el error.

Este espejo no sustituye esa historia: la declara.

---

## Fuentes de los datos

- **Copernicus DEM GLO-30** — ESA / Airbus. Modelo de elevación, ~30 m.
- **INVÍAS** — serie histórica de volúmenes de tránsito, estaciones 243, 244 y 245.
- **ANSV** — Agencia Nacional de Seguridad Vial, conjunto `rs3u-8r4q` de datos.gov.co
  (sectores críticos y fallecidos 2015–2019).
- **ANI** — conjunto `8yi9-t44c` de datos.gov.co (aforo del peaje Cocora).
- **IGAC** — límites municipales de Tolima y Quindío.
- **Fernández Ordóñez, H. O. (2025)** — *Túnel para cruce férreo de la Cordillera Central de
  los Andes y semilla para la Estrella Andina*. XX Seminario Andino de Túneles y Obras
  Subterráneas, SAI, Medellín, 8 de octubre de 2025.

---

## Equipo

| Integrante | Objetivos |
|---|---|
| Tamayo Osorio Miguel Ángel | 1 · 3 |
| Castaño Cifuentes Maicol Stiven | 4 · 5 |
| Torrente Parra Daniel Ignacio | 2 · 6 |
| Todo el equipo | 7 |

Trabajo académico de pregrado. Los análisis son de nivel conceptual y no constituyen diseño
de ingeniería.
