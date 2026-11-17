---
layout: pagina
title: Sobre nosotros
imagen: assets/placeholders/IMG-POST-12.jpg
imagen_alt: "Puestos con toldos amarillos en la Feria de Medioambiente de Cheste"
---

## Sobre Plantopia

**Plantopia** es una revista digital sobre **Formación Profesional e innovación educativa**, con la mirada puesta en la FP, la sostenibilidad y el medio rural.

> Cada proyecto es una semilla: la innovación crece en el aula.

## Qué publicamos

Además de la revista, en Plantopia publicamos:

- **Cuadernos de campo**, como *La resinación*, de la colección *Aprovechamientos Forestales*.
- **Cuadernos del profesor**.
- **Material didáctico**.

## Una edición cada tres meses

La revista tiene una **publicación trimestral**: sale una nueva edición cada tres meses.

## Colabora con nosotros

Si quieres colaborar con Plantopia, escríbenos a [plantopia.es@gmail.com](mailto:plantopia.es@gmail.com).

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
