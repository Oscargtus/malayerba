#!/bin/zsh
# Publica en GitHub todos los cambios de esta carpeta (artículos, fotos, textos…).
# GitHub Pages vuelve a compilar el sitio en 1–2 minutos.
#
# Uso (desde la carpeta malayerba-jekyll):
#   ./tools/publicar.sh "Nuevo artículo: la ciudad"
#
# Antes de publicar revisa los enlaces con ./tools/compilar.sh
set -e
cd "$(dirname "$0")/.."
MENSAJE="${1:-Actualizar la revista}"
if [ -z "$(git status --porcelain)" ]; then
  echo "No hay cambios para publicar."; exit 0
fi
echo "Cambios que se van a publicar:"
git status --short
git add -A
git commit -q -m "$MENSAJE"
GH=(-c credential.helper= -c 'credential.helper=!gh auth git-credential')
# trae primero lo que se haya cambiado en la web de GitHub
git "${GH[@]}" pull -q --rebase
git "${GH[@]}" push -q
echo "Publicado. En 1–2 minutos estará en https://oscargtus.github.io/plantopia/"
