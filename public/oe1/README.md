# Láminas del Objetivo Específico 1 — versión web

Estos archivos son copias, listas para servir en el sitio, de las láminas producidas
en `OE1_Topografia/Visuales/`. El original de cada una queda en esa carpeta y en las
carpetas de evidencia en Drive; aquí solo está la versión optimizada para la web.

| Archivo web | Origen en el repositorio | Tratamiento |
|---|---|---|
| `perfil_longitudinal.png` | `OE1_Topografia/Visuales/perfil_longitudinal.png` (2700×1120, 224 kB) | copia sin modificar |
| `cobertura_tunel.png` | `OE1_Topografia/Visuales/cobertura_tunel.png` (2700×1380, 224 kB) | copia sin modificar |
| `mapa_OE1_layout.png` | `OE1_Topografia/Visuales/mapa_OE1_layout.png` (4960×3507, 4,0 MB) | reducido a 1800 px de ancho, paleta de 256 colores → 340 kB |

## Reproducir la reducción

```bash
python public/oe1/reducir_lamina.py
```

El script está en esta misma carpeta. Reduce solo la lámina de layout: pasa a fondo
blanco, escala a 1800 px de ancho con remuestreo Lanczos conservando la proporción,
cuantiza a 256 colores y guarda con compresión PNG. Resultado: 1800×1273 px, ~340 kB,
con el texto legible.

Copia de las otras dos láminas (sin cambios):

```bash
cp OE1_Topografia/Visuales/perfil_longitudinal.png public/oe1/perfil_longitudinal.png
cp OE1_Topografia/Visuales/cobertura_tunel.png      public/oe1/cobertura_tunel.png
```
