"""
Reducción reproducible de la lámina de layout del OE 1 para la web.

La lámina OE1_Topografia/Visuales/mapa_OE1_layout.png se genera a 4.960 px de ancho
(≈ 4,2 MB), un tamaño pensado para impresión que no puede servirse tal cual en el sitio.
Este script la lleva a 1.800 px de ancho conservando la proporción, la reduce a una
paleta de 256 colores (una lámina cartográfica usa pocos colores planos, así que la
paleta no degrada el texto) y la deja en public/oe1/mapa_OE1_layout.png por debajo
de 900 kB.

Las otras dos láminas (perfil_longitudinal.png y cobertura_tunel.png) pesan ~224 kB
y se copian sin modificar.

Uso:
    python public/oe1/reducir_lamina.py

Comando equivalente en una línea (Pillow):
    python -c "from PIL import Image; im=Image.open('OE1_Topografia/Visuales/mapa_OE1_layout.png').convert('RGBA'); b=Image.new('RGB',im.size,'white'); b.paste(im,mask=im.split()[-1]); w=1800; b=b.resize((w,round(b.height*w/b.width)),Image.LANCZOS); b.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).save('public/oe1/mapa_OE1_layout.png',optimize=True)"
"""
from pathlib import Path
from PIL import Image

RAIZ = Path(__file__).resolve().parents[2]
ORIGEN = RAIZ / "OE1_Topografia" / "Visuales" / "mapa_OE1_layout.png"
DESTINO = RAIZ / "public" / "oe1" / "mapa_OE1_layout.png"
ANCHO_OBJETIVO = 1800

def main() -> None:
    im = Image.open(ORIGEN)
    # Fondo blanco: el layout de QGIS/matplotlib no usa transparencia real y pasar a
    # RGB reduce el peso a la mitad sin cambiar lo que se ve.
    if im.mode in ("RGBA", "LA", "P"):
        fondo = Image.new("RGB", im.size, "white")
        im = im.convert("RGBA")
        fondo.paste(im, mask=im.split()[-1])
        im = fondo
    alto = round(im.height * ANCHO_OBJETIVO / im.width)
    im = im.resize((ANCHO_OBJETIVO, alto), Image.LANCZOS)
    im = im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(DESTINO, format="PNG", optimize=True)
    kb = DESTINO.stat().st_size / 1024
    print(f"{DESTINO.relative_to(RAIZ)} -> {im.width}x{im.height} px, {kb:.0f} kB")

if __name__ == "__main__":
    main()
