# Láminas del objetivo específico 5 para la web

`graficos_siniestralidad.png` es la copia reducida para el sitio de
`OE5_SeguridadVial/Visuales/graficos_siniestralidad_OE5.png`, que se genera a
3.100 px de ancho (≈ 2,1 MB) para impresión y no puede servirse tal cual.

La reducción es la misma que la del OE 1: 1.800 px de ancho conservando la
proporción, fondo blanco en lugar de canal alfa y paleta de 256 colores sin
tramado. La lámina usa pocos colores planos, así que la paleta no degrada el
texto. Resultado: 1.800 × 952 px, ≈ 457 kB.

Comando equivalente en una línea (Pillow), desde la raíz del repositorio:

    python -c "from PIL import Image; im=Image.open('OE5_SeguridadVial/Visuales/graficos_siniestralidad_OE5.png').convert('RGBA'); b=Image.new('RGB',im.size,'white'); b.paste(im,mask=im.split()[-1]); w=1800; b=b.resize((w,round(b.height*w/b.width)),Image.LANCZOS); b.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).save('public/oe5/graficos_siniestralidad.png',optimize=True)"

## La segunda lámina

`siniestralidad.png` es la copia reducida de
`OE5_SeguridadVial/Visuales/siniestralidad_OE5.png`, que produce `fig_oe5.py`.
Se genera a 2.700 px de ancho y se reduce con el mismo procedimiento.
Resultado: 1.800 × 787 px, ≈ 121 kB.

    python -c "from PIL import Image; im=Image.open('OE5_SeguridadVial/Visuales/siniestralidad_OE5.png').convert('RGBA'); b=Image.new('RGB',im.size,'white'); b.paste(im,mask=im.split()[-1]); w=1800; b=b.resize((w,round(b.height*w/b.width)),Image.LANCZOS); b.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).save('public/oe5/siniestralidad.png',optimize=True)"

Hasta el 10 sep 2026 esta lámina no se publicaba porque su pie decía
«Semillero GMAE». El script se corrigió ese día (GEOPAV) y de paso se numeraron
los seis sectores críticos: dos pares comparten punto de referencia (PR 10 y
PR 85) y los rótulos anteriores se repetían.

## La tercera lámina

`densidad_lineal.png` es la copia reducida de
`OE5_SeguridadVial/Visuales/densidad_lineal_OE5.png`, que produce
`densidad_lineal_OE5.py` a partir del microdato ANSV georreferenciado
(oficio 20265000140371). Se genera a 3.100 px de ancho y se reduce con el
mismo procedimiento. Resultado: 1.800 × 1.092 px, ≈ 358 kB.

    python -c "from PIL import Image; im=Image.open('OE5_SeguridadVial/Visuales/densidad_lineal_OE5.png').convert('RGBA'); b=Image.new('RGB',im.size,'white'); b.paste(im,mask=im.split()[-1]); w=1800; b=b.resize((w,round(b.height*w/b.width)),Image.LANCZOS); b.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).save('public/oe5/densidad_lineal.png',optimize=True)"

## Relieve de fondo de los mapas interactivos

`relieve_corredor.jpg` y `relieve_descenso.jpg` son sombreados (hillshade) del
DEM Copernicus GLO-30 (EPSG:4686) del área de estudio, generados por
`OE5_SeguridadVial/Act4_Analisis/exportar_web_OE5.py` junto con
`src/data/mapas_oe5.json`. Sirven de fondo a los mapas interactivos de
`src/components/graficos/LaminasOE5.tsx` (mapa de sectores críticos y detalle
del descenso). Las láminas PNG de arriba se conservan aparte como entregable
descargable; no las reemplazan.
