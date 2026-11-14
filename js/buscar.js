/*
 * malayerba – buscador sin servidor.
 * Busca en js/indice-busqueda.js (se regenera con: python3 tools/indice_busqueda.py)
 * y muestra los resultados debajo de cualquier formulario .search-form de la página.
 */
(function () {
	"use strict";

	function normalizar(texto) {
		return String(texto || "")
			.toLowerCase()
			.normalize("NFD")
			.replace(/[̀-ͯ]/g, "");
	}

	function escapar(texto) {
		var div = document.createElement("div");
		div.textContent = texto;
		return div.innerHTML;
	}

	function buscar(consulta) {
		var indice = window.MALAYERBA_INDICE || [];
		var terminos = normalizar(consulta).split(/\s+/).filter(Boolean);
		if (!terminos.length) {
			return [];
		}
		var resultados = [];
		indice.forEach(function (pagina) {
			var titulo = normalizar(pagina.titulo + " " + pagina.encabezados);
			var todo = normalizar([pagina.titulo, pagina.descripcion, pagina.encabezados, pagina.texto].join(" "));
			var puntos = 0;
			for (var i = 0; i < terminos.length; i++) {
				if (todo.indexOf(terminos[i]) === -1) {
					return; // todas las palabras deben aparecer
				}
				puntos += titulo.indexOf(terminos[i]) !== -1 ? 3 : 1;
			}
			resultados.push({ pagina: pagina, puntos: puntos });
		});
		resultados.sort(function (a, b) { return b.puntos - a.puntos; });
		return resultados.slice(0, 8);
	}

	function mostrar(form, consulta) {
		var caja = form.parentNode.querySelector(".resultados-busqueda");
		if (!caja) {
			caja = document.createElement("div");
			caja.className = "resultados-busqueda";
			caja.setAttribute("aria-live", "polite");
			form.parentNode.insertBefore(caja, form.nextSibling);
		}
		if (!consulta.trim()) {
			caja.innerHTML = "";
			return;
		}
		var resultados = buscar(consulta);
		if (!resultados.length) {
			caja.innerHTML = '<p class="sin-resultados">Sin resultados para «' + escapar(consulta) + '».</p>';
			return;
		}
		caja.innerHTML = "<ul>" + resultados.map(function (r) {
			var p = r.pagina;
			return '<li><a href="' + escapar(p.url) + '">' + escapar(p.titulo) + "</a>" +
				(p.descripcion ? "<span>" + escapar(p.descripcion) + "</span>" : "") + "</li>";
		}).join("") + "</ul>";
	}

	document.addEventListener("submit", function (evento) {
		var form = evento.target;
		if (!form.classList || !form.classList.contains("search-form")) {
			return;
		}
		evento.preventDefault();
		var campo = form.querySelector('input[type="search"]');
		mostrar(form, campo ? campo.value : "");
	});
})();
