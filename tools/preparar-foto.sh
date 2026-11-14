#!/bin/zsh
# Prepara una foto para la web: la convierte a JPG, la reduce de tamaño y la guarda con el nombre que quieras.
# Usa "sips", que viene con macOS (no hay que instalar nada).
#
# Uso (desde la carpeta malayerba-jekyll):
#   ./tools/preparar-foto.sh  ORIGEN  DESTINO  [ANCHO]
#
# Ejemplos:
#   ./tools/preparar-foto.sh ~/Desktop/IMG_4521.HEIC assets/fotos/la-ciudad.jpg
#   ./tools/preparar-foto.sh ~/Desktop/portada.png  assets/placeholders/IMG-HERO-01.jpg 1920
#
# ANCHO (opcional): ancho máximo en píxeles. Por defecto 1600. La proporción no cambia.
set -e
if [ $# -lt 2 ]; then
  sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'
  exit 1
fi
ORIGEN="${1:A}"; DESTINO="$2"; ANCHO="${3:-1600}"   # ${1:A} = ruta completa del original
cd "$(dirname "$0")/.."
[ -f "$ORIGEN" ] || { echo "No encuentro el archivo: $ORIGEN"; exit 1; }
case "$DESTINO" in
  *.jpg) ;;
  *) echo "El destino debe terminar en .jpg (minúsculas), p. ej. assets/fotos/mi-foto.jpg"; exit 1 ;;
esac
NOMBRE="$(basename "$DESTINO")"
if print -r -- "$NOMBRE" | LC_ALL=C grep -q '[^A-Za-z0-9._-]'; then
  echo "Usa en el nombre solo letras sin acentos, números, guiones y puntos: $NOMBRE"; exit 1
fi
mkdir -p "$(dirname "$DESTINO")"
ANCHO_ACTUAL=$(sips -g pixelWidth "$ORIGEN" | awk '/pixelWidth/{print $2}')
if [ "$ANCHO_ACTUAL" -gt "$ANCHO" ]; then
  sips -s format jpeg -s formatOptions 82 --resampleWidth "$ANCHO" "$ORIGEN" --out "$DESTINO" >/dev/null
else
  sips -s format jpeg -s formatOptions 82 "$ORIGEN" --out "$DESTINO" >/dev/null
fi
TAM=$(sips -g pixelWidth -g pixelHeight "$DESTINO" | awk '/pixel/{printf $2" "}')
PESO=$(du -h "$DESTINO" | cut -f1)
echo "Listo: $DESTINO  (${TAM% }px, $PESO)"
