# Inventario de imágenes – Plantopia (Jekyll)

Todas las imágenes son **placeholders** en `assets/placeholders/`, con su nombre y tamaño escritos dentro (excepto el logo de Plantopia, que está en `assets/marca/`).
Para reemplazar una: guarda tu imagen con **exactamente el mismo nombre** (mayúsculas incluidas) y sobrescribe el archivo.

Para **artículos nuevos** puedes crear tus propias imágenes en otra carpeta (por ejemplo `assets/fotos/`) y
ponerlas en el campo `imagen:` del artículo. No hace falta seguir el esquema IMG-POST-xx.

## Artículos (una imagen por artículo, se usa en todas partes)

Cada artículo usa **una sola imagen 3:2** (ideal 1200×800). El sitio la muestra completa en el artículo y en las tarjetas,
y la recorta desde el centro donde la caja tiene otra proporción (miniaturas de la barra lateral, selector de la
portada, tarjetas anchas de video/galería). Deja lo importante de la foto cerca del centro.

| Placeholder | Dónde se usa | Tamaño ideal | Notas |
|---|---|---|---|
| IMG-POST-01.jpg … IMG-POST-04.jpg | campo `imagen:` de los 4 artículos de ejemplo (`_posts/`, uno por sección) | 1200×800 (3:2) | Tarjeta, artículo, relacionados, miniaturas, buscador |
| IMG-POST-12.jpg | `sobre-nosotros.md` (`imagen:`) | 1200×800 (3:2) | Imagen principal de "Sobre nosotros" |

## Portada

| Placeholder | Dónde se usa | Tamaño ideal | Notas |
|---|---|---|---|
| IMG-HERO-01.jpg … IMG-HERO-04.jpg | `imagen_portada:` de los 4 artículos de ejemplo (todos destacados) | 1920×845 | Fondo del slideshow; el título va encima (usa una imagen oscura o suave) |

## Compartidas en todo el sitio

| Placeholder | Dónde se configura | Tamaño ideal | Notas |
|---|---|---|---|
| assets/marca/plantopia-logo.webp | `_includes/marca.html` | 164×240 (fondo transparente) | Logo de Plantopia junto a la edición (`_config.yml` → `edicion`). Altura: `--logo-size` en `style.css` (56 px; 44 px en móvil). En la portada lleva una placa blanca |
| assets/marca/plantopia-favicon.png, plantopia-apple-touch.png | `_includes/head.html` | 64×64 y 180×180 | Ícono de la pestaña y del acceso directo en móviles |
| IMG-AVATAR-01.jpg | `_config.yml` → `perfil.imagen` | 180×180 | Perfil de la revista en la barra lateral (se ve en círculo) |
| IMG-AVATAR-02.jpg | `_config.yml` → `perfil.imagen_menu_lateral` | 215×215 | Perfil en el panel lateral (botón ☰) |
| IMG-AVATAR-03.jpg, IMG-AVATAR-04.jpg | `_data/autores.yml` → `foto` | 270×270 | Fotos de autores (caja del artículo y equipo en "Sobre nosotros") |
| IMG-BANNER-01.jpg | `_includes/barra-lateral.html` | 370×415 | Espacio publicitario de la barra lateral |
| IMG-BG-01.jpg | `_layouts/interior.html` (o `imagen_cabecera:` en cada página) | 1920×200 | Fondo de la cabecera de páginas interiores |
| IMG-GALLERY-01.jpg … IMG-GALLERY-09.jpg | `_data/galeria.yml` | 275×240 | Franja de imágenes antes del pie |

## Fondos en CSS (`style.css`)

Texturas decorativas de la plantilla (`images/bg-pattern*.jpg`). Ninguna página las usa; se conservan porque
`style.css` las referencia. Los fondos de contenido (IMG-HERO, IMG-BG) van en el HTML, no en el CSS.
