# Ferropista Cordillera Central — análisis del Semillero GEOPAV

Análisis independiente de la iniciativa privada de túnel de base ferroviario
"Ferropista", tramo Ibagué – Armenia (paso del Alto de La Línea), realizado por el
Semillero de Investigación GEOPAV, Ingeniería Civil, Universidad de Ibagué,
en el marco del Semestre Paz y Región 2026B.

**El semillero no representa ni promueve la iniciativa. La analiza y la verifica.**

## Qué hay aquí

Espejo público del repositorio de trabajo. Contiene el sitio (Next.js), los
scripts, los datos y las memorias de cada objetivo específico, de modo que un
tercero pueda rehacer cada cálculo.

| Objetivo | Estado | Dónde |
|---|---|---|
| OE 1 · Topografía del trazado | cerrado | `OE1_Topografia/` |
| OE 5 · Seguridad vial | cerrado | `OE5_SeguridadVial/` |
| OE 2 · Plataforma y consulta ciudadana | en curso | `src/` |
| OE 3, 4, 6, 7 | no iniciados | — |

Sitio publicado: https://ferropista.vercel.app

## Cómo leer las cifras

Toda cifra lleva marca de origen y ninguna entra sin ella:

| Marca | Significado |
|---|---|
| `F` | Dato de la ponencia de referencia, citando la diapositiva |
| `CP` | Cálculo propio, reproducible con el script publicado |
| `H` | Hipótesis declarada, no un dato medido |
| `DA` | Dato abierto pendiente de consultar |

La fuente primaria analizada es Fernández Ordóñez, H. O. (2025), *Túnel para
cruce férreo de la Cordillera Central de los Andes y semilla para la Estrella
Andina*, XX Seminario Andino de Túneles y Obras Subterráneas, SAI, Medellín,
8 de octubre de 2025. Es un documento de promoción de una iniciativa privada
hacia una APP: sus cifras son estimaciones del proponente, no auditadas por un
tercero. El aporte del semillero es el método de verificación, no la conclusión.

## Qué no incluye este espejo

- El historial de commits del repositorio de trabajo.
- El proyecto de QGIS `OE1_trazado.qgz`, que guarda rutas absolutas de la
  máquina donde se hizo y no es portable.
- Rásteres de gran tamaño que los scripts regeneran a partir de fuentes abiertas
  (Copernicus DEM GLO-30, límites del IGAC).
