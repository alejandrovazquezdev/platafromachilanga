(() => {
  'use strict';

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

  /* ------------------------------------------------------------
     Navegación móvil
     ------------------------------------------------------------ */
  const toggle = $('[data-menu-toggle]');
  const nav = $('#menu-principal');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const abierto = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!abierto));
      nav.classList.toggle('is-open', !abierto);
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) {
        toggle.setAttribute('aria-expanded', 'false');
        nav.classList.remove('is-open');
        toggle.focus();
      }
    });
  }

  const header = $('[data-header]');
  if (header) {
    const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 8);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ------------------------------------------------------------
     Copiar enlace
     ------------------------------------------------------------ */
  const copiar = async (texto) => {
    try {
      await navigator.clipboard.writeText(texto);
      return true;
    } catch (err) {
      const area = document.createElement('textarea');
      area.value = texto;
      area.setAttribute('readonly', '');
      area.style.position = 'fixed';
      area.style.opacity = '0';
      document.body.appendChild(area);
      area.select();
      let ok = false;
      try {
        ok = document.execCommand('copy');
      } catch (e) {
        ok = false;
      }
      document.body.removeChild(area);
      return ok;
    }
  };

  const avisarCopiado = (boton, ok) => {
    if (!boton) return;
    const original = boton.innerHTML;
    boton.innerHTML = ok
      ? '<svg class="btn__icono" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m4 12.5 5 5L20 6.5"/></svg> Copiado'
      : 'No se pudo copiar';
    boton.disabled = true;
    window.setTimeout(() => {
      boton.innerHTML = original;
      boton.disabled = false;
    }, 1800);
  };

  $$('[data-copiar]').forEach((boton) => {
    boton.addEventListener('click', async () => {
      const target = $(boton.getAttribute('data-copiar'));
      if (!target) return;
      avisarCopiado(boton, await copiar(target.value));
    });
  });

  $$('[data-copiar-texto]').forEach((boton) => {
    boton.addEventListener('click', async () => {
      avisarCopiado(boton, await copiar(boton.getAttribute('data-copiar-texto') || ''));
    });
  });

  /* ------------------------------------------------------------
     Formulario de registro: horarios y tianguis
     ------------------------------------------------------------ */
  $$('[data-horario]').forEach((bloque) => {
    const actualizar = (fila) => {
      const check = $('[data-horario-check]', fila);
      const horas = $$('[data-horario-hora]', fila);
      const abierta = check ? check.checked : true;
      fila.classList.toggle('is-cerrado', !abierta);
      horas.forEach((h) => {
        h.disabled = !abierta;
      });
    };
    $$('.horario__fila', bloque).forEach((fila) => {
      const check = $('[data-horario-check]', fila);
      if (check) check.addEventListener('change', () => actualizar(fila));
      actualizar(fila);
    });
  });

  const previewColonia = document.querySelector('[data-preview-colonia]');
  const previewAlcaldia = document.querySelector('[data-preview-alcaldia]');
  const inputColonia = document.querySelector('input[name="colonia"]');
  const inputAlcaldia = document.querySelector('select[name="alcaldia"]');
  if (previewColonia && inputColonia) {
    const actualizar = () => {
      previewColonia.textContent = inputColonia.value.trim() || 'Tu colonia';
    };
    inputColonia.addEventListener('input', actualizar);
    actualizar();
  }
  if (previewAlcaldia && inputAlcaldia) {
    const actualizar = () => {
      previewAlcaldia.textContent = inputAlcaldia.value || 'tu alcaldía';
    };
    inputAlcaldia.addEventListener('change', actualizar);
    actualizar();
  }

  const tipoRadios = $$('input[name="tipo"]');
  const tianguisCampos = $('[data-tianguis-campos]');
  if (tipoRadios.length && tianguisCampos) {
    const actualizar = () => {
      const tipo = tipoRadios.find((r) => r.checked)?.value;
      tianguisCampos.hidden = tipo !== 'tianguis';
    };
    tipoRadios.forEach((r) => r.addEventListener('change', actualizar));
    actualizar();
  }

  /* ------------------------------------------------------------
     Productos dinámicos
     ------------------------------------------------------------ */
  const productos = $('[data-productos]');
  const plantilla = $('#plantilla-producto');
  const agregar = $('[data-agregar-producto]');
  const contador = $('[data-contador-productos]');
  const MAX_PRODUCTOS = 6;

  const actualizarContador = () => {
    if (!productos || !contador) return;
    const n = $$('[data-producto]', productos).length;
    contador.textContent = `${n} de ${MAX_PRODUCTOS} productos`;
    contador.style.color = n >= MAX_PRODUCTOS ? 'var(--rojo)' : '';
  };

  const conectarQuitar = (fila) => {
    const quitar = $('[data-quitar-producto]', fila);
    if (!quitar) return;
    quitar.addEventListener('click', () => {
      const filas = $$('[data-producto]', productos);
      if (filas.length === 1) {
        $$('input', fila).forEach((i) => {
          i.value = '';
        });
      } else {
        fila.remove();
      }
      actualizarContador();
    });
  };

  if (productos) {
    $$('[data-producto]', productos).forEach(conectarQuitar);
    if (agregar && plantilla) {
      agregar.addEventListener('click', () => {
        const n = $$('[data-producto]', productos).length;
        if (n >= MAX_PRODUCTOS) {
          actualizarContador();
          return;
        }
        const clon = plantilla.content.cloneNode(true);
        const fila = clon.querySelector('[data-producto]');
        productos.appendChild(clon);
        conectarQuitar(fila);
        const primerInput = $('input', fila);
        if (primerInput) primerInput.focus();
        actualizarContador();
      });
    }
    actualizarContador();
  }

  /* ------------------------------------------------------------
     Evitar doble envío
     ------------------------------------------------------------ */
  $$('form').forEach((form) => {
    form.addEventListener('submit', () => {
      const boton = form.querySelector('button[type="submit"]');
      if (boton && !boton.disabled) {
        boton.disabled = true;
        boton.dataset.textoOriginal = boton.textContent;
        boton.textContent = 'Guardando…';
      }
    });
  });

  /* ------------------------------------------------------------
     Mapa (Leaflet)
     ------------------------------------------------------------ */
  const escapar = (texto) =>
    String(texto ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');

  const iniciarMapa = () => {
    if (typeof window.L === 'undefined') return;
    const contenedor = $('#mapa-directorio') || $('#mapa-ficha');
    if (!contenedor) return;

    const datosEl = $('#datos-mapa');
    let datos = [];
    try {
      datos = datosEl ? JSON.parse(datosEl.textContent || '[]') : [];
    } catch (e) {
      datos = [];
    }

    const mapa = window.L.map(contenedor, {
      scrollWheelZoom: false,
      zoomControl: true,
    });

    window.L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 20,
      subdomains: 'abcd',
      attribution: '&copy; OpenStreetMap &copy; CARTO',
    }).addTo(mapa);

    const icono = window.L.divIcon({
      className: 'pin-mapa',
      html: '<span></span>',
      iconSize: [28, 28],
      iconAnchor: [14, 28],
      popupAnchor: [0, -26],
    });

    const marcadores = [];
    datos.forEach((item) => {
      if (typeof item.lat !== 'number' || typeof item.lng !== 'number') return;
      const marcador = window.L.marker([item.lat, item.lng], { icon: icono }).addTo(mapa);
      marcador.bindPopup(
        `<strong>${escapar(item.nombre)}</strong>` +
          `${escapar(item.tipo)} · ${escapar(item.alcaldia)}<br>` +
          `<a href="/comercio/${encodeURIComponent(item.slug)}">Ver ficha</a>`
      );
      marcadores.push(marcador);
    });

    if (marcadores.length === 1) {
      mapa.setView(marcadores[0].getLatLng(), 15);
    } else if (marcadores.length > 1) {
      mapa.fitBounds(window.L.featureGroup(marcadores).getBounds().pad(0.18));
    } else {
      mapa.setView([19.4326, -99.1332], 11);
    }

    contenedor.classList.add('mapa--listo');
  };

  window.addEventListener('load', iniciarMapa);
})();
