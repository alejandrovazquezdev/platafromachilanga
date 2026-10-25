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
     Asistente Chilanga
     ------------------------------------------------------------ */
  const chat = $('[data-chat]');
  const chatPanel = $('[data-chat-panel]');
  const chatToggle = $('[data-chat-toggle]');
  const chatCerrar = $('[data-chat-cerrar]');
  const chatForm = $('[data-chat-form]');
  const chatInput = $('#chat-input');
  const chatMensajes = $('[data-chat-mensajes]');
  const chatSugerencias = $('[data-chat-sugerencias]');
  const historialChat = [];
  let enviandoChat = false;

  const abrirChat = () => {
    if (!chatPanel || !chatToggle) return;
    chatPanel.hidden = false;
    chatToggle.setAttribute('aria-expanded', 'true');
    chat.classList.add('is-abierto');
    window.setTimeout(() => chatInput?.focus(), 120);
  };

  const cerrarChat = () => {
    if (!chatPanel || !chatToggle) return;
    chatPanel.hidden = true;
    chatToggle.setAttribute('aria-expanded', 'false');
    chat.classList.remove('is-abierto');
  };

  const burbuja = (texto, tipo) => {
    if (!chatMensajes) return null;
    const div = document.createElement('div');
    div.className = `chat-burbuja chat-burbuja--${tipo}`;
    div.textContent = texto;
    chatMensajes.appendChild(div);
    chatMensajes.scrollTop = chatMensajes.scrollHeight;
    return div;
  };

  const enviarChat = async (texto) => {
    const pregunta = (texto || '').trim();
    if (!pregunta || enviandoChat) return;
    enviandoChat = true;
    burbuja(pregunta, 'user');
    historialChat.push({ role: 'user', content: pregunta });
    if (chatInput) chatInput.value = '';
    const escribiendo = burbuja('Escribiendo…', 'bot chat-burbuja--escribiendo');
    try {
      const respuesta = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrfToken,
        },
        body: JSON.stringify({ messages: historialChat.slice(-8) }),
      });
      const data = await respuesta.json().catch(() => ({}));
      escribiendo?.remove();
      const reply = data.reply || 'No pude responder ahora. Revisa las preguntas frecuentes.';
      burbuja(reply, 'bot');
      historialChat.push({ role: 'assistant', content: reply });
    } catch (error) {
      escribiendo?.remove();
      burbuja('No pude conectar con el asistente. Revisa tu conexión e intenta de nuevo.', 'bot');
    } finally {
      enviandoChat = false;
    }
  };

  if (chatToggle && chatPanel) {
    chatToggle.addEventListener('click', () => {
      if (chatPanel.hidden) abrirChat();
      else cerrarChat();
    });
  }
  if (chatCerrar) chatCerrar.addEventListener('click', cerrarChat);
  if (chatForm) {
    chatForm.addEventListener('submit', (event) => {
      event.preventDefault();
      enviarChat(chatInput?.value || '');
    });
  }
  if (chatSugerencias) {
    chatSugerencias.addEventListener('click', (event) => {
      const boton = event.target.closest('[data-chat-sugerencia]');
      if (!boton) return;
      enviarChat(boton.getAttribute('data-chat-sugerencia'));
    });
  }
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && chatPanel && !chatPanel.hidden) {
      cerrarChat();
      chatToggle?.focus();
    }
  });

  /* ------------------------------------------------------------
     Notificaciones Web Push
     ------------------------------------------------------------ */
  const csrfMeta = document.querySelector('meta[name="csrf-token"]');
  const vapidMeta = document.querySelector('meta[name="vapid-public-key"]');
  const avisoPush = document.querySelector('[data-aviso-push]');
  const csrfToken = csrfMeta ? csrfMeta.content : '';
  const vapidKey = vapidMeta ? vapidMeta.content : '';
  const soportaPush =
    'Notification' in window && 'serviceWorker' in navigator && 'PushManager' in window;

  const base64ToUint8 = (base64) => {
    const padding = '='.repeat((4 - (base64.length % 4)) % 4);
    const normalizado = (base64 + padding).replace(/-/g, '+').replace(/_/g, '/');
    const raw = atob(normalizado);
    return Uint8Array.from([...raw].map((c) => c.charCodeAt(0)));
  };

  const registrarSW = async () => {
    if (!('serviceWorker' in navigator)) throw new Error('Sin service worker');
    return navigator.serviceWorker.register('/sw.js', { scope: '/' });
  };

  const ocultarAvisoPush = (definitivo = false) => {
    if (!avisoPush) return;
    avisoPush.hidden = true;
    if (definitivo) {
      localStorage.setItem('chilangaton-avisos-cerrado', String(Date.now()));
    }
  };

  const mensajeAviso = (texto) => {
    if (!avisoPush) return;
    const p = avisoPush.querySelector('.aviso-push__texto p');
    if (p) p.textContent = texto;
    avisoPush.hidden = false;
  };

  const activarAvisos = async () => {
    if (!soportaPush || !vapidKey) {
      mensajeAviso('Este navegador no permite avisos o el servicio no está configurado.');
      return;
    }
    try {
      const permiso = await Notification.requestPermission();
      if (permiso !== 'granted') {
        mensajeAviso('No se activaron los avisos. Puedes habilitarlos desde la configuración del navegador.');
        return;
      }
      await registrarSW();
      const registro = await navigator.serviceWorker.ready;
      let suscripcion = await registro.pushManager.getSubscription();
      if (!suscripcion) {
        suscripcion = await registro.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: base64ToUint8(vapidKey),
        });
      }
      const respuesta = await fetch('/api/notificaciones/suscribir', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrfToken,
        },
        body: JSON.stringify(suscripcion),
      });
      if (!respuesta.ok) throw new Error('No se pudo guardar la suscripción');
      if (avisoPush) {
        mensajeAviso('Listo. Te avisaremos cuando haya algo importante para tu comercio.');
        window.setTimeout(() => ocultarAvisoPush(false), 3200);
      }
    } catch (error) {
      mensajeAviso('No pudimos activar los avisos en este dispositivo. Intenta desde Chrome o Safari actualizado.');
    }
  };

  document.addEventListener('click', (event) => {
    if (event.target.closest('[data-activar-avisos]')) {
      event.preventDefault();
      activarAvisos();
    }
    if (event.target.closest('[data-cerrar-aviso]')) {
      event.preventDefault();
      ocultarAvisoPush(true);
    }
  });

  const prepararAvisoPush = async () => {
    if (!avisoPush || !soportaPush || !vapidKey) return;
    if (!window.matchMedia('(max-width: 720px)').matches) return;
    const cerrado = Number(localStorage.getItem('chilangaton-avisos-cerrado') || 0);
    if (cerrado && Date.now() - cerrado < 30 * 24 * 60 * 60 * 1000) return;
    if (Notification.permission === 'denied') return;
    if (Notification.permission === 'granted') {
      try {
        const registro = await navigator.serviceWorker.getRegistration('/');
        const suscripcion = registro ? await registro.pushManager.getSubscription() : null;
        if (suscripcion) return;
      } catch (error) {
        return;
      }
    }
    window.setTimeout(() => {
      avisoPush.hidden = false;
    }, 2800);
  };

  window.addEventListener('load', prepararAvisoPush);


  /* ------------------------------------------------------------
     Mapa del registro + geocodificación (Nominatim)
     ------------------------------------------------------------ */
  const iniciarMapaRegistro = () => {
    const contenedor = document.querySelector('#mapa-registro');
    if (!contenedor || typeof window.L === 'undefined') return;

    const latInput = document.querySelector('[data-lat-input]');
    const lngInput = document.querySelector('[data-lng-input]');
    const labelInput = document.querySelector('[data-ubicacion-label]');
    const estado = document.querySelector('[data-geocodificar-estado]');
    const inicialLat = parseFloat(contenedor.dataset.lat);
    const inicialLng = parseFloat(contenedor.dataset.lng);
    const hayInicial = Number.isFinite(inicialLat) && Number.isFinite(inicialLng);

    const mapa = window.L.map(contenedor, { scrollWheelZoom: false }).setView(
      hayInicial ? [inicialLat, inicialLng] : [19.4326, -99.1332],
      hayInicial ? 16 : 11
    );

    window.L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
      { maxZoom: 16, maxNativeZoom: 16, attribution: 'Tiles &copy; Esri' }
    ).addTo(mapa);

    const icono = window.L.divIcon({
      className: 'pin-mapa',
      html: '<span></span>',
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });

    let marcador = hayInicial ? window.L.marker([inicialLat, inicialLng], { icon: icono, draggable: true }).addTo(mapa) : null;

    const guardar = (lat, lng, etiqueta) => {
      if (latInput) latInput.value = lat.toFixed(6);
      if (lngInput) lngInput.value = lng.toFixed(6);
      if (etiqueta && labelInput) labelInput.value = etiqueta.slice(0, 300);
      if (estado) estado.textContent = 'Ubicación lista. Puedes arrastrar el pin para ajustarla.';
    };

    const ponerMarcador = (lat, lng, etiqueta) => {
      if (marcador) mapa.removeLayer(marcador);
      marcador = window.L.marker([lat, lng], { icon: icono, draggable: true }).addTo(mapa);
      marcador.on('dragend', () => {
        const pos = marcador.getLatLng();
        guardar(pos.lat, pos.lng, '');
      });
      mapa.setView([lat, lng], 16);
      guardar(lat, lng, etiqueta);
    };

    if (marcador) {
      marcador.on('dragend', () => {
        const pos = marcador.getLatLng();
        guardar(pos.lat, pos.lng, '');
      });
    }

    mapa.on('click', (evento) => ponerMarcador(evento.latlng.lat, evento.latlng.lng, ''));
    contenedor.classList.add('mapa--listo');

    window.ChilangatonMapa = { ponerMarcador };

    const boton = document.querySelector('[data-geocodificar]');
    const entrada = document.querySelector('#busqueda-ubicacion');
    if (boton && entrada) {
      const buscar = async () => {
        const q = entrada.value.trim();
        if (q.length < 5) {
          if (estado) estado.textContent = 'Escribe una dirección o colonia más completa.';
          return;
        }
        boton.disabled = true;
        if (estado) estado.textContent = 'Buscando la dirección…';
        try {
          const respuesta = await fetch(`/api/geocodificar?q=${encodeURIComponent(q)}`);
          const datos = await respuesta.json();
          if (!datos.ok) {
            if (estado) estado.textContent = datos.error || 'No encontramos esa dirección.';
            return;
          }
          ponerMarcador(datos.lat, datos.lng, datos.label);
          const alcaldiaSelect = document.querySelector('select[name="alcaldia"]');
          if (alcaldiaSelect && datos.alcaldia) {
            const opcion = [...alcaldiaSelect.options].find((o) => o.value === datos.alcaldia);
            if (opcion) alcaldiaSelect.value = datos.alcaldia;
          }
          const coloniaInput = document.querySelector('input[name="colonia"]');
          if (coloniaInput && !coloniaInput.value && datos.colonia) coloniaInput.value = datos.colonia;
          const calleInput = document.querySelector('input[name="calle"]');
          if (calleInput && !calleInput.value && datos.calle) calleInput.value = datos.calle;
          if (estado) estado.textContent = `Ubicación encontrada: ${datos.label}`;
        } catch (error) {
          if (estado) estado.textContent = 'No pudimos buscar la dirección. Intenta de nuevo.';
        } finally {
          boton.disabled = false;
        }
      };
      boton.addEventListener('click', buscar);
      entrada.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
          event.preventDefault();
          buscar();
        }
      });
    }
  };

  window.addEventListener('load', iniciarMapaRegistro);

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

    window.L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
      {
        maxZoom: 16,
        maxNativeZoom: 16,
        attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
      }
    ).addTo(mapa);
    window.L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}',
      { maxZoom: 16, maxNativeZoom: 16, pane: 'overlayPane' }
    ).addTo(mapa);

    const icono = window.L.divIcon({
      className: 'pin-mapa',
      html: '<span></span>',
      iconSize: [28, 28],
      iconAnchor: [14, 28],
      popupAnchor: [0, -26],
    });

    const marcadores = [];
    const marcadoresPorSlug = new Map();
    datos.forEach((item) => {
      if (typeof item.lat !== 'number' || typeof item.lng !== 'number') return;
      const marcador = window.L.marker([item.lat, item.lng], { icon: icono }).addTo(mapa);
      const metodos = (item.metodos || []).join(', ');
      marcador.bindPopup(
        `<strong>${escapar(item.nombre)}</strong>` +
          `${escapar(item.tipo)} · ${escapar(item.giro)}<br>` +
          `${escapar(item.colonia)}, ${escapar(item.alcaldia)}<br>` +
          `<span>${item.abierto ? 'Abierto ahora' : 'Cerrado ahora'} · ${escapar(item.horario)}</span><br>` +
          `${metodos ? escapar(metodos) + '<br>' : ''}` +
          `<a href="/comercio/${encodeURIComponent(item.slug)}">Ver ficha</a>`
      );
      marcadores.push(marcador);
      marcadoresPorSlug.set(item.slug, marcador);
    });

    if (marcadores.length === 1) {
      mapa.setView(marcadores[0].getLatLng(), 15);
    } else if (marcadores.length > 1) {
      mapa.fitBounds(window.L.featureGroup(marcadores).getBounds().pad(0.18));
    } else {
      mapa.setView([19.4326, -99.1332], 11);
    }

    contenedor.classList.add('mapa--listo');

    document.querySelectorAll('[data-centrar-comercio]').forEach((boton) => {
      boton.addEventListener('click', () => {
        const marcador = marcadoresPorSlug.get(boton.getAttribute('data-centrar-comercio'));
        if (!marcador) return;
        mapa.setView(marcador.getLatLng(), 15);
        marcador.openPopup();
        contenedor.scrollIntoView({ behavior: 'smooth', block: 'center' });
        document.querySelectorAll('.tarjeta-comercio.is-seleccionada').forEach((card) => card.classList.remove('is-seleccionada'));
        const tarjeta = boton.closest('.tarjeta-comercio');
        if (tarjeta) tarjeta.classList.add('is-seleccionada');
      });
    });

    const botonUbicacion = document.querySelector('[data-centrar-ubicacion]');
    const estadoUbicacion = document.querySelector('[data-ubicacion-estado]');
    if (botonUbicacion && contenedor.id === 'mapa-directorio') {
      botonUbicacion.addEventListener('click', () => {
        if (!navigator.geolocation) {
          if (estadoUbicacion) estadoUbicacion.textContent = 'Tu navegador no comparte la ubicación.';
          return;
        }
        if (estadoUbicacion) estadoUbicacion.textContent = 'Buscando tu ubicación…';
        navigator.geolocation.getCurrentPosition(
          (posicion) => {
            const { latitude, longitude } = posicion.coords;
            mapa.setView([latitude, longitude], 14);
            window.L.circleMarker([latitude, longitude], {
              radius: 9,
              color: '#bc955c',
              weight: 3,
              fillColor: '#9f2241',
              fillOpacity: 1,
            })
              .addTo(mapa)
              .bindPopup('Tu ubicación aproximada')
              .openPopup();
            if (estadoUbicacion) estadoUbicacion.textContent = 'Mapa centrado en tu ubicación.';
          },
          () => {
            if (estadoUbicacion) estadoUbicacion.textContent = 'No diste permiso de ubicación. Puedes buscar por alcaldía.';
          },
          { enableHighAccuracy: true, timeout: 8000 }
        );
      });
    }
  };

  window.addEventListener('load', iniciarMapa);
})();
