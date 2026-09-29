# Láminas del Objetivo Específico 1 — versión web

Estos archivos son copias, listas para servir en el sitio, de las láminas producidas
en `OE1_Topografia/Visuales/`. El original de cada una queda en esa carpeta y en las
carpetas de evidencia en Drive; aquí solo está la versión optimizada para la web.

Las tres se generan con `Comun/exportar_laminas_web.py`, que reemplazó al antiguo
`public/oe1/reducir_lamina.py` (solo reducía la lámina de layout) para las láminas
de todos los objetivos.

| Archivo web | Origen en el repositorio | Tratamiento |
|---|---|---|
| `mapa_trazado.jpg` | `OE1_Topografia/Visuales/mapa_trazado.png` | reducido a 1.800 px de ancho, JPEG calidad 88 (lleva relieve sombreado) |
| `perfil_longitudinal.png` | `OE1_Topografia/Visuales/perfil_longitudinal.png` | reducido a 1.800 px de ancho, paleta de 256 colores |
| `cobertura_tunel.png` | `OE1_Topografia/Visuales/cobertura_tunel.png` | reducido a 1.800 px de ancho, paleta de 256 colores |

## Reproducir las copias web

```bash
python Comun/exportar_laminas_web.py
```

El script vive en `Comun/` y regenera las copias web de todos los objetivos (OE 1,
OE 3 y OE 5) en un solo paso: remuestreo Lanczos a 1.800 px de ancho, JPEG calidad 88
para las láminas con relieve sombreado y PNG de 256 colores sin tramado para las
gráficas de colores planos.
