"""Convierte el subrayado de Pages CMS (++texto++) en subrayado real (<u>texto</u>).

El editor de Pages CMS guarda el subrayado como ++texto++, que Jekyll (kramdown) no entiende
y muestra tal cual. Este script lo cambia por <u>texto</u>, que sí se ve subrayado en la web.
Si después se vuelve a editar el artículo en Pages CMS, el editor lo reconoce como subrayado.

Uso:  python3 tools/convertir-subrayado.py ARCHIVO.md [ARCHIVO.md ...]
Lo ejecuta .github/workflows/ajustes-automaticos.yml con los artículos guardados.
Solo cambia el texto del artículo (no el front matter) y no toca bloques de código ni `código`.
"""
import re
import sys

# ++texto++ : sin espacio justo después de abrir ni justo antes de cerrar, en una sola línea
SUBRAYADO = re.compile(r"\+\+(?=\S)([^\n]*?\S)\+\+")
CODIGO_EN_LINEA = re.compile(r"(`+)(.+?)\1")
# markdown="span" hace que Jekyll (kramdown) aplique también la negrita/cursiva que haya dentro
REEMPLAZO = r'<u markdown="span">\1</u>'


def convertir_linea(linea):
    partes, pos = [], 0
    for m in CODIGO_EN_LINEA.finditer(linea):  # deja intacto lo que va entre `comillas`
        partes.append(SUBRAYADO.sub(REEMPLAZO, linea[pos:m.start()]))
        partes.append(m.group(0))
        pos = m.end()
    partes.append(SUBRAYADO.sub(REEMPLAZO, linea[pos:]))
    return "".join(partes)


def convertir(texto):
    lineas = texto.split("\n")
    inicio = 0
    if lineas and lineas[0].strip() == "---":  # salta el front matter
        for i in range(1, len(lineas)):
            if lineas[i].strip() == "---":
                inicio = i + 1
                break
    en_codigo = False
    for i in range(inicio, len(lineas)):
        if lineas[i].lstrip().startswith(("```", "~~~")):
            en_codigo = not en_codigo
            continue
        if not en_codigo:
            lineas[i] = convertir_linea(lineas[i])
    return "\n".join(lineas)


if __name__ == "__main__":
    cambiados = 0
    for ruta in sys.argv[1:]:
        if not ruta.endswith((".md", ".markdown")):
            continue
        try:
            with open(ruta, encoding="utf-8") as f:
                original = f.read()
        except FileNotFoundError:
            continue
        nuevo = convertir(original)
        if nuevo != original:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(nuevo)
            print(f"{ruta}: subrayado convertido")
            cambiados += 1
    print(f"Artículos con subrayado convertido: {cambiados}")
