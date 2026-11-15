---
layout: pagina
title: Sobre nosotros
imagen: assets/placeholders/IMG-POST-12.jpg
---

## Sobre Plantopia

Párrafo de presentación de la revista: qué es Plantopia, qué publica y por qué existe. Texto de ejemplo para reemplazar.

> Una frase que resuma el espíritu de la revista. Texto de ejemplo.

Segundo párrafo: línea editorial, periodicidad, cómo colaborar. Texto de ejemplo para reemplazar.

## Equipo

<ul class="equipo">
{%- for autor in site.data.autores %}
	<li id="{{ autor.id }}">
		<img src="{{ autor.foto }}" alt="" width="135" height="135" loading="lazy" decoding="async">
		<div>
			<h3>{{ autor.nombre }}</h3>
			<p>{{ autor.bio }}</p>
		</div>
	</li>
{%- endfor %}
</ul>
