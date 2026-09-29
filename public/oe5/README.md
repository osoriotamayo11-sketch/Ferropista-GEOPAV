# Láminas del objetivo específico 5 para la web

Las tres láminas de abajo, y las del OE 1 y el OE 3, se generan en un solo paso con
`Comun/exportar_laminas_web.py`, que reemplazó a los comandos Pillow sueltos que
documentaba antes este archivo.

`graficos_siniestralidad.jpg` es la copia reducida para el sitio de
`OE5_SeguridadVial/Visuales/graficos_siniestralidad_OE5.png`, que se genera a
3.100 px de ancho (≈ 2,1 MB) para impresión y no puede servirse tal cual.

La reducción es la misma para las tres: 1.800 px de ancho conservando la
proporción y remuestreo Lanczos. Las láminas con relieve sombreado (esta y
`densidad_lineal.jpg`) se guardan en JPEG calidad 88, porque una paleta de 256
colores degrada el degradado del relieve. Resultado: 1.800 × 1.150 px.

```bash
python Comun/exportar_laminas_web.py
```

## La segunda lámina

`siniestralidad.png` es la copia reducida de
`OE5_SeguridadVial/Visuales/siniestralidad_OE5.png`, que produce `fig_oe5.py`.
Se genera a 2.700 px de ancho. Es una gráfica de colores planos, así que se
guarda en PNG de 256 colores sin tramado en lugar de JPEG. Resultado:
1.800 × 787 px, ≈ 121 kB.

Hasta el 10 sep 2026 esta lámina no se publicaba porque su pie decía
«Semillero GMAE». El script se corrigió ese día (GEOPAV) y de paso se numeraron
los seis sectores críticos: dos pares comparten punto de referencia (PR 10 y
PR 85) y los rótulos anteriores se repetían.

## La tercera lámina

`densidad_lineal.jpg` es la copia reducida de
`OE5_SeguridadVial/Visuales/densidad_lineal_OE5.png`, que produce
`densidad_lineal_OE5.py` a partir del microdato ANSV georreferenciado
(oficio 20265000140371). Se genera a 3.100 px de ancho. Lleva relieve
sombreado de fondo, así que se guarda en JPEG calidad 88. Resultado:
1.800 × 1.266 px.

## Relieve de fondo de los mapas interactivos

`relieve_corredor.jpg` y `relieve_descenso.jpg` son sombreados (hillshade) del
DEM Copernicus GLO-30 (EPSG:4686) del área de estudio, generados por
`OE5_SeguridadVial/Act4_Analisis/exportar_web_OE5.py` junto con
`src/data/mapas_oe5.json`. Sirven de fondo a los mapas interactivos de
`src/components/graficos/LaminasOE5.tsx` (mapa de sectores críticos y detalle
del descenso). Las láminas de arriba se conservan aparte como entregable
descargable; no las reemplazan.
