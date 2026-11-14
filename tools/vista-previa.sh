#!/bin/zsh
# Vista previa de malayerba con recarga automática: http://localhost:4000
# Uso (desde la carpeta malayerba-jekyll):  ./tools/vista-previa.sh
# Para detenerla: Ctrl + C
cd "$(dirname "$0")/.."
export PATH="/opt/homebrew/opt/ruby@3.3/bin:$PATH" LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
[ -d vendor/bundle ] || { bundle config set --local path vendor/bundle; bundle install; }
exec bundle exec jekyll serve --port "${PORT:-4000}" --livereload "$@"
