#!/usr/bin/env python3
"""
Verificador de enlaces y recursos de malayerba.

Uso: primero compila el sitio (tools/compilar.sh o "bundle exec jekyll build"), luego:
    python3 tools/verificar.py            -> revisa la carpeta _site/
    python3 tools/verificar.py otra/carpeta

Revisa todos los .html y .css del sitio:
  - href, src, srcset, poster, action, url(...) (en CSS y en atributos style)
  - que cada archivo local exista, respetando MAYÚSCULAS/minúsculas
    (GitHub Pages distingue "Foto.jpg" de "foto.jpg")
  - que las rutas sean relativas (nada que empiece con "/", "file:", "localhost")
  - que los anclas "#id" apunten a un id que exista en la página destino
Avisa (sin marcar error) de enlaces externos (http/https), para que los revises.
Termina con código 1 si hay errores.
"""
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(PROYECTO, "_site")
SKIP_DIRS = {"scss", "tools", ".git"}
JS_HASH_OK = {"#"}  # enlaces "#" usados por JavaScript (abrir/cerrar menú lateral)

errors, warnings = [], []


def exists_exact(path):
    """True si el archivo existe con las mayúsculas exactas."""
    path = os.path.normpath(path)
    if not os.path.exists(path):
        return False
    rel = os.path.relpath(path, SITE)
    cur = SITE
    for part in rel.split(os.sep):
        if part == "..":
            cur = os.path.dirname(cur)
            continue
        if part not in os.listdir(cur):
            return False
        cur = os.path.join(cur, part)
    return True


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if v is None:
                continue
            if k == "id":
                self.ids.add(v)
            elif k in ("href", "src", "poster", "action", "data-src"):
                self.refs.append((tag, k, v, self.getpos()[0]))
            elif k == "srcset":
                for part in v.split(","):
                    if part.strip():
                        self.refs.append((tag, k, part.split()[0], self.getpos()[0]))
            elif k == "style":
                for u in re.findall(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", v):
                    self.refs.append((tag, "style url()", u, self.getpos()[0]))


def page_ids(path, cache={}):
    if path not in cache:
        c = Collector()
        c.feed(open(path, encoding="utf-8").read())
        cache[path] = c.ids
    return cache[path]


def check(ref, base_file, where):
    ref = ref.strip()
    if not ref or ref.startswith(("data:", "mailto:", "tel:", "javascript:")):
        if ref == "":
            errors.append(f"{where}: enlace vacío")
        return
    if ref.startswith(("http://", "https://", "//")):
        host = urlsplit(ref if not ref.startswith("//") else "https:" + ref).hostname or ""
        if host in ("localhost", "127.0.0.1") or host.endswith(".local"):
            errors.append(f"{where}: URL local absoluta -> {ref}")
        else:
            warnings.append(f"{where}: enlace externo -> {ref}")
        return
    if ref.startswith(("/", "file:")):
        errors.append(f"{where}: ruta absoluta (debe ser relativa) -> {ref}")
        return
    parts = urlsplit(ref)
    target_rel = unquote(parts.path)
    if not target_rel:  # solo "#algo"
        if ref in JS_HASH_OK or base_file.endswith(".css"):
            return
        if parts.fragment and parts.fragment not in page_ids(base_file):
            errors.append(f"{where}: ancla inexistente -> {ref}")
        return
    target = os.path.join(os.path.dirname(base_file), target_rel)
    if not exists_exact(target):
        errors.append(f"{where}: archivo no encontrado (o mayúsculas distintas) -> {ref}")
        return
    if os.path.relpath(os.path.normpath(target), SITE).startswith(".."):
        errors.append(f"{where}: apunta fuera de la carpeta del sitio -> {ref}")
        return
    if parts.fragment and target.endswith(".html") and parts.fragment not in page_ids(target):
        errors.append(f"{where}: ancla inexistente -> {ref}")


def main():
    if not os.path.isdir(SITE):
        print(f"No existe {SITE}. Compila primero el sitio.")
        sys.exit(1)
    html_files, css_files = [], []
    for root, dirs, files in os.walk(SITE):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            p = os.path.join(root, f)
            if f.endswith(".html"):
                html_files.append(p)
            elif f.endswith(".css"):
                css_files.append(p)

    for p in sorted(html_files):
        rel = os.path.relpath(p, SITE)
        c = Collector()
        c.feed(open(p, encoding="utf-8").read())
        for tag, attr, ref, line in c.refs:
            if attr == "action" and ref == "#":
                continue  # formularios sin backend todavía
            check(ref, p, f"{rel}:{line} <{tag} {attr}>")

    for p in sorted(css_files):
        rel = os.path.relpath(p, SITE)
        for n, line in enumerate(open(p, encoding="utf-8"), 1):
            for u in re.findall(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", line):
                check(u, p, f"{rel}:{n} url()")

    print(f"Revisados: {len(html_files)} HTML, {len(css_files)} CSS\n")
    if warnings:
        print(f"AVISOS ({len(warnings)}) – enlaces externos, revisar a mano:")
        for w in sorted(set(warnings)):
            print("  ·", w)
        print()
    if errors:
        print(f"ERRORES ({len(errors)}):")
        for e in errors:
            print("  ✗", e)
        sys.exit(1)
    print("✓ Sin enlaces ni recursos rotos. Todas las rutas locales son relativas.")


if __name__ == "__main__":
    main()
