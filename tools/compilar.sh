#!/bin/zsh
# Compila el sitio en la carpeta _site/ y revisa los enlaces.
# Uso (desde la carpeta malayerba-jekyll):  ./tools/compilar.sh
# El contenido de _site/ es lo que se sube a un hosting propio por FTP.
cd "$(dirname "$0")/.."
export PATH="/opt/homebrew/opt/ruby@3.3/bin:$PATH" LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
[ -d vendor/bundle ] || { bundle config set --local path vendor/bundle; bundle install; }
JEKYLL_ENV=production bundle exec jekyll build && python3 tools/verificar.py && ruby tools/verificar-cms.rb
