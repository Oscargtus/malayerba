# malayerba – revista digital (versión Jekyll)

Escribes los artículos en **Markdown** (texto simple) y Jekyll arma el sitio completo: portada,
secciones, archivo, artículos relacionados, buscador, RSS y sitemap.
El header, el menú, la barra lateral y el pie están en **un solo lugar** (`_includes/`), no copiados en cada página.

- **Para publicar en GitHub Pages no necesitas instalar nada:** GitHub compila el sitio solo cada vez que subes cambios.
- **En tu Mac**, Ruby y Jekyll (ya instalados) sirven para **ver una vista previa** antes de publicar.

## Qué hay en esta carpeta

| Carpeta / archivo | Para qué |
|---|---|
| `_posts/` | **Los artículos** (un archivo `.md` por artículo) |
| `_drafts/plantilla-articulo.md` | Plantilla para copiar al escribir un artículo |
| `assets/fotos/` | **Tus fotos** (vacía al principio) |
| `assets/placeholders/` | Imágenes grises de ejemplo, para reemplazar (ver `IMAGENES.md`) |
| `_data/` | Menú, secciones, autores, redes, enlaces, galería |
| `_config.yml` | Nombre de la revista, textos generales, dirección del sitio |
| `sobre-nosotros.md`, `contacto.html` | Páginas de texto |
| `tools/` | Comandos: vista previa, compilar/revisar, preparar fotos |
| `_layouts/`, `_includes/`, `style.css` | Diseño (normalmente no hace falta tocarlos) |
| `_site/`, `vendor/` | Se generan solos. **No se editan ni se suben a GitHub** |

---

## Paso 1. Abrir la vista previa

En la Terminal, desde la carpeta `malayerba-jekyll`:

```bash
./tools/vista-previa.sh
```

Abre <http://localhost:4000>. Déjala abierta mientras trabajas: cada vez que guardas un archivo, la página se recarga sola.
Para detenerla: `Ctrl + C`.

> Si cambias `_config.yml`, detén la vista previa (`Ctrl + C`) y vuelve a abrirla: ese archivo solo se lee al arrancar.

## Paso 2. Preparar las fotos

Hay dos casos.

### A) Reemplazar un placeholder (logo, portada, perfil, banner…)

1. Busca en `IMAGENES.md` qué placeholder quieres cambiar y su tamaño ideal (por ejemplo `IMG-BANNER-01.jpg`, 370×415).
2. Guarda tu imagen en `assets/placeholders/` con **exactamente el mismo nombre**, sobrescribiendo el gris.
   - Mismo nombre y misma extensión, **en minúsculas**: `IMG-BANNER-01.jpg` (no `.JPG`, `.jpeg` ni `.png`).
   - El logo es la excepción: `IMG-LOGO-01.svg` debe ser un archivo **SVG**.
3. No hay que tocar ningún código. Si la proporción es distinta a la ideal, la imagen se adapta sin deformarse,
   pero puede verse más alta o más baja.

### B) Fotos nuevas para tus artículos

Guárdalas en `assets/fotos/`, con nombres simples: minúsculas, sin acentos ni espacios (`la-ciudad.jpg`).

La forma más fácil es usar el comando incluido, que convierte cualquier foto (JPG, PNG, HEIC del iPhone) a `.jpg`,
la reduce a un tamaño adecuado para la web y le pone el nombre correcto:

```bash
./tools/preparar-foto.sh ~/Desktop/IMG_4521.HEIC assets/fotos/la-ciudad.jpg
```

Truco: escribe `./tools/preparar-foto.sh ` y **arrastra la foto desde el Finder** a la Terminal para pegar su ruta.

Para una imagen de portada (slideshow) usa ancho 1920:

```bash
./tools/preparar-foto.sh ~/Desktop/portada.jpg assets/fotos/la-ciudad-portada.jpg 1920
```

Tamaños recomendados:

| Uso | Proporción / tamaño | Campo |
|---|---|---|
| Imagen del artículo | 3:2 (ideal 1200×800) | `imagen:` |
| Portada (slideshow) | 1920×845 | `imagen_portada:` |
| Foto de autor | cuadrada (270×270) | `foto:` en `_data/autores.yml` |

La imagen del artículo se usa en todas partes (tarjetas, miniaturas, buscador) y se recorta desde el centro
donde hace falta: deja lo importante cerca del centro.

## Paso 3. Escribir un artículo

1. Copia `_drafts/plantilla-articulo.md` dentro de `_posts/`.
2. Renómbralo como `AAAA-MM-DD-titulo-corto.md`, por ejemplo `2026-12-01-la-ciudad.md`.
   - La fecha es la de publicación (los artículos se ordenan por fecha).
   - `titulo-corto` será la dirección del artículo: `la-ciudad.html`. Sin acentos, espacios ni mayúsculas.
3. Rellena los datos de arriba (entre las dos líneas `---`):
   - `title`, `categoria` (id de `_data/categorias.yml`), `autor` (id de `_data/autores.yml`),
   - `imagen: assets/fotos/la-ciudad.jpg`, `imagen_alt` (qué se ve en la foto), `extracto`, `etiquetas`.
4. Escribe el texto debajo. Guía rápida de Markdown:

   | Escribes | Obtienes |
   |---|---|
   | `## Subtítulo` | un subtítulo |
   | `**negrita**` / `*cursiva*` | **negrita** / *cursiva* |
   | `[texto](https://...)` | un enlace |
   | `> frase citada` | una cita destacada |
   | `- punto` | una lista |
   | `![descripción](assets/fotos/otra-foto.jpg)` | una imagen dentro del texto |

5. Guarda y mira el resultado en la vista previa.

- **Destacado en la portada:** añade `destacado: true` e `imagen_portada:` (1920×845). Los 5 destacados más recientes salen en el slideshow.
- **Video o galería de fotos:** mira las opciones comentadas en la plantilla.
- **Borrar un artículo:** borra su archivo de `_posts/`.

## Paso 4. Editar el resto del sitio

| Qué | Dónde |
|---|---|
| Nombre de la revista, descripción, texto del perfil y del pie | `_config.yml` |
| Menú principal | `_data/menu.yml` |
| Secciones (categorías) | `_data/categorias.yml` + un archivo `categoria-<id>.html` por sección |
| Autores | `_data/autores.yml` |
| Redes sociales (un ícono aparece solo cuando tiene `url`) | `_data/redes.yml` |
| Enlaces del pie / de la barra superior | `_data/enlaces.yml` / `_data/barra_superior.yml` |
| Franja de imágenes antes del pie | `_data/galeria.yml` |
| Textos de "Sobre nosotros" y "Contacto" | `sobre-nosotros.md`, `contacto.html` |
| Estilos | `style.css` (secciones *malayerba* al final) |

**Añadir una sección:** añade el bloque en `_data/categorias.yml`, copia `categoria-1.html` como
`categoria-<id-nuevo>.html` y cambia dentro `categoria:` y `title:`. El menú y el pie la incluyen solos.

## Paso 5. Revisar antes de publicar

```bash
./tools/compilar.sh
```

Compila el sitio en `_site/` y comprueba que todos los enlaces e imágenes existan (con mayúsculas exactas)
y que todas las rutas sean relativas. Si algo falla, te dice el archivo y la línea.

## Paso 6. Publicar

### En GitHub Pages (recomendado)

El sitio está publicado en **https://oscargtus.github.io/malayerba/** (repositorio `Oscargtus/malayerba`).
Esta carpeta ya está conectada al repositorio, así que para publicar cambios basta con:

```bash
./tools/compilar.sh                                  # revisa que no haya enlaces rotos
./tools/publicar.sh "Nuevo artículo: la ciudad"      # sube los cambios a GitHub
```

`publicar.sh` sube todo lo que cambió (artículos, fotos, textos) usando tu sesión de GitHub (`gh`).
En 1–2 minutos el sitio se actualiza; si algo falla, mira la pestaña *Actions* del repositorio.

**Sin Terminal** (para un cambio puntual): en la web del repositorio entra en la carpeta correspondiente
(`_posts/`, `assets/fotos/`, `assets/placeholders/`…), usa *Add file → Upload files* y pulsa *Commit changes*.
`publicar.sh` trae esos cambios de la web automáticamente antes de subir los tuyos.

### En un hosting propio (FTP)

1. Pon la dirección final en `_config.yml` → `url:`.
2. Ejecuta `./tools/compilar.sh`.
3. Sube **el contenido de `_site/`** (no la carpeta del proyecto) a tu hosting por FTP. Repite cada vez que cambies algo.

## Si algo no se ve bien

| Problema | Solución |
|---|---|
| Una imagen no aparece | Revisa que el nombre coincida exactamente, mayúsculas y extensión incluidas (`.jpg`). `./tools/compilar.sh` te dice cuál falla |
| Un artículo no aparece | El nombre del archivo debe empezar con la fecha `AAAA-MM-DD-` y la fecha no puede ser futura |
| Cambié `_config.yml` y no pasa nada | Reinicia la vista previa (`Ctrl + C` y `./tools/vista-previa.sh`) |
| En GitHub el sitio no se actualiza | Mira la pestaña *Actions* del repositorio: si hay un error en rojo, dice el archivo |

## Notas técnicas

- Jekyll 3.10 y la gema `github-pages` (las mismas versiones que usa GitHub), Ruby 3.3 (Homebrew).
- Artículos y páginas quedan en la raíz del sitio (`mi-articulo.html`), así las rutas relativas
  funcionan igual en GitHub Pages y en cualquier hosting.
- Plugins: `jekyll-feed` (`feed.xml`, RSS) y `jekyll-sitemap` (`sitemap.xml` y `robots.txt`).
- El buscador funciona en el navegador sin servicios externos: `js/indice-busqueda.js` se genera solo.
- Fuentes (Fraunces + Source Serif 4) y jQuery 3.7.1 están dentro del sitio: sin dependencias externas.
- La versión estática original está en `../malayerba/` como referencia.
