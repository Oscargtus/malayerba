#!/bin/zsh
# Prepara una copia limpia del proyecto para subirla a GitHub desde la web
# (sin _site/, vendor/ ni archivos temporales), dividida en dos lotes porque
# la web de GitHub acepta como máximo 100 archivos por subida.
#
# Uso (desde la carpeta malayerba-jekyll):  ./tools/preparar-subida.sh
# Resultado: ../malayerba-para-github/1-primero/  y  ../malayerba-para-github/2-despues/
set -e
cd "$(dirname "$0")/.."
DEST="../malayerba-para-github"
rm -rf "$DEST"
mkdir -p "$DEST/1-primero" "$DEST/2-despues"

# Lote 2: carpetas con muchos archivos (fuentes e imágenes)
for d in fonts assets images; do
  rsync -a --exclude '.DS_Store' "$d" "$DEST/2-despues/"
done

# Lote 1: todo lo demás
rsync -a \
  --exclude '_site' --exclude 'vendor' --exclude '.jekyll-cache' --exclude '.bundle' \
  --exclude '.sass-cache' --exclude '.DS_Store' \
  --exclude 'fonts' --exclude 'assets' --exclude 'images' \
  ./ "$DEST/1-primero/"

n1=$(find "$DEST/1-primero" -type f ! -name '.*' | wc -l | tr -d ' ')
n2=$(find "$DEST/2-despues" -type f ! -name '.*' | wc -l | tr -d ' ')
echo "Listo: $DEST"
echo "  1-primero: $n1 archivos"
echo "  2-despues: $n2 archivos"
