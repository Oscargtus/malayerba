"""Reduce y limpia las fotos subidas desde Pages CMS (las usa .github/workflows/reducir-fotos.yml).

Uso:  python tools/reducir-fotos.py ARCHIVO [ARCHIVO ...]

Para cada JPG de assets/fotos (máx. 1600 px de ancho) o assets/portadas (máx. 1920 px):
  - lo gira según la orientación EXIF (las fotos del iPad vienen "tumbadas" con una marca),
  - lo reduce si es más ancho que el máximo,
  - lo guarda en JPG calidad 82 SIN metadatos (quita la ubicación GPS, el modelo del iPad, etc.).
Las fotos que ya cumplen (ancho correcto y sin EXIF) no se tocan, así que se puede ejecutar varias veces.
Necesita Pillow (pip install pillow).
"""
import os
import sys

from PIL import Image, ImageOps

ANCHO_MAXIMO = {"assets/fotos/": 1600, "assets/portadas/": 1920}
CALIDAD = 82


def ancho_maximo(ruta):
    ruta = ruta.replace(os.sep, "/")
    for carpeta, ancho in ANCHO_MAXIMO.items():
        if ruta.startswith(carpeta):
            return ancho
    return None


def procesar(ruta):
    maximo = ancho_maximo(ruta)
    if maximo is None or not ruta.lower().endswith((".jpg", ".jpeg")) or not os.path.isfile(ruta):
        return False
    with Image.open(ruta) as im:
        tiene_exif = bool(im.info.get("exif"))
        if im.width <= maximo and not tiene_exif:
            return False
        icc = im.info.get("icc_profile")  # el perfil de color se conserva (no tiene datos personales)
        foto = ImageOps.exif_transpose(im).convert("RGB")
    antes_w, antes_kb = foto.width, os.path.getsize(ruta) // 1024
    if foto.width > maximo:
        alto = round(foto.height * maximo / foto.width)
        foto = foto.resize((maximo, alto), Image.LANCZOS)
    extra = {"icc_profile": icc} if icc else {}
    foto.save(ruta, "JPEG", quality=CALIDAD, optimize=True, progressive=True, **extra)
    print(f"{ruta}: {antes_w} px → {foto.width} px, {antes_kb} KB → {os.path.getsize(ruta) // 1024} KB, sin metadatos")
    return True


if __name__ == "__main__":
    cambiadas = [r for r in sys.argv[1:] if procesar(r)]
    print(f"Fotos procesadas: {len(cambiadas)}")
