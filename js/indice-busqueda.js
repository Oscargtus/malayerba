---
# Índice del buscador: Jekyll lo genera solo con todos los artículos y páginas.
---
window.MALAYERBA_INDICE = [
{%- for post in site.posts %}
	{
		"url": {{ post.url | remove_first: "/" | jsonify }},
		"titulo": {{ post.title | jsonify }},
		"descripcion": {{ post.extracto | default: "" | jsonify }},
		"encabezados": {% assign _cat = site.data.categorias | where: "id", post.categoria | first %}{{ _cat.nombre | default: "" | jsonify }},
		"texto": {{ post.content | strip_html | strip_newlines | truncatewords: 250 | jsonify }}
	},
{%- endfor %}
{%- assign paginas = "sobre-nosotros.html,contacto.html,archivo.html" | split: "," %}
{%- for p in site.pages %}
	{%- assign u = p.url | remove_first: "/" %}
	{%- if paginas contains u %}
	{
		"url": {{ u | jsonify }},
		"titulo": {{ p.title | jsonify }},
		"descripcion": "",
		"encabezados": "",
		"texto": {{ p.content | strip_html | strip_newlines | truncatewords: 150 | jsonify }}
	},
	{%- endif %}
{%- endfor %}
	null
].filter(Boolean);
