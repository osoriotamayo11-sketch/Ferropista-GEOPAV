# -*- coding: utf-8 -*-
"""Copias web de las láminas del proyecto (sesión 16).

Las láminas originales (200 ppp, para impresión y Drive) quedan en <OE>/Visuales/. El sitio sirve
copias reducidas a 1.800 px de ancho (remuestreo Lanczos): las láminas con relieve en JPEG calidad 88 y las
gráficas planas en PNG de 256 colores, como hacía
public/oe1/reducir_lamina.py con la lámina de QGIS. Este script reemplaza a aquel para todas las láminas.
Uso: python Comun/exportar_laminas_web.py   (imprime ancho × alto de cada copia, para el sitio)
"""
import os
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAMINAS = [  # origen → destino web
    ("OE1_Topografia/Visuales/mapa_trazado.png", "public/oe1/mapa_trazado.jpg"),
    ("OE1_Topografia/Visuales/perfil_longitudinal.png", "public/oe1/perfil_longitudinal.png"),
    ("OE1_Topografia/Visuales/cobertura_tunel.png", "public/oe1/cobertura_tunel.png"),
    ("OE5_SeguridadVial/Visuales/siniestralidad_OE5.png", "public/oe5/siniestralidad.png"),
    ("OE5_SeguridadVial/Visuales/graficos_siniestralidad_OE5.png", "public/oe5/graficos_siniestralidad.jpg"),
    ("OE5_SeguridadVial/Visuales/densidad_lineal_OE5.png", "public/oe5/densidad_lineal.jpg"),
    ("OE3_Geotecnia/Visuales/lamina_portales_geologia_OE3.png", "public/oe3/lamina_portales_geologia.jpg"),
    ("OE3_Geotecnia/Visuales/mapa_susceptibilidad_OE3.png", "public/oe3/mapa_susceptibilidad.jpg"),
]
ANCHO = 1800
for o, d in LAMINAS:
    im = Image.open(os.path.join(RAIZ, o)).convert("RGB")
    im = im.resize((ANCHO, round(im.height * ANCHO / im.width)), Image.LANCZOS)
    os.makedirs(os.path.dirname(os.path.join(RAIZ, d)), exist_ok=True)
    if d.endswith(".jpg"):   # láminas con relieve sombreado: la paleta de 256 colores altera los tonos
        im.save(os.path.join(RAIZ, d), quality=88, optimize=True, progressive=True)
    else:                    # gráficas de colores planos
        im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(os.path.join(RAIZ, d), optimize=True)
    print(f"{d}: {im.width}×{im.height}, {os.path.getsize(os.path.join(RAIZ, d)) // 1024} kB")
