# Sistema de diseño gubernamental adaptado

> Fuente: `~/dev/negocia-cdmx` (SvelteKit + Tailwind). Esta aplicación lo replica
> con **Flask + Jinja + HTML/CSS/JS**, sin Svelte ni Tailwind.

## 1. Qué se extrajo de NegociaCDMX

| Elemento | Archivo fuente | Uso en Chilangatón |
|---|---|---|
| Guinda institucional | `src/app.css` (`--color-gob`) | Color primario, botones, enlaces, cifras |
| Guinda oscuro / claro / suave | `src/app.css` | Hover, estados, fondos de tarjetas |
| Fondo neutro cálido | `src/app.css` + `+page.svelte` | Papel `#FBF8F3` y secciones alternas |
| Tipografía Inter | `src/app.css` | Toda la interfaz, con fallback del sistema |
| Header blanco con borde | `SiteHeader.svelte` | Header sticky con logo y navegación |
| Marca con logo + nombre | `Brand.svelte` | Logo oficial + wordmark “Chilangatón” |
| Campos redondeados con foco guinda | `Field.svelte` | Inputs, selects, textareas y radio cards |
| Contenedor `max-w-5xl` | `+page.svelte` | Contenedor de 1180 px |
| Tarjetas `rounded-xl border` | `+page.svelte` | Beneficios, fichas, panel y pasos |
| Aviso de privacidad y consentimiento | `PrivacyNotice.svelte` / registro | Página de aviso y checkbox obligatorio |
| Logo oficial | `static/logo.png` | Header, footer y favicon (recortado) |

## 2. Tokens finales

```css
--guinda: #9f2241;          /* primario */
--guinda-oscuro: #7a1a33;   /* hover y footer */
--guinda-claro: #c14a68;
--guinda-suave: #f7e9ed;    /* fondos y chips */
--oro: #bc955c;             /* acento institucional */
--oro-oscuro: #8f6c3b;
--oro-suave: #f3e8d6;
--tinta: #231a1d;
--tinta-suave: #6e5f64;
--papel: #fbf8f3;
--borde: #e7ddd4;
--radio: 16px;
--radio-grande: 24px;
```

La tipografía es **Inter** (400/500/600/700/800), con `letter-spacing` negativo en
titulares. Se carga desde Google Fonts y tiene fallback al sistema.

## 3. Componentes

- **Header institucional:** franja guinda con “Chilangatón 2026 · Reto 1”,
  header blanco sticky, logo oficial, navegación y CTA guinda.
- **Hero:** titular grande, bajada, dos CTAs, sellos de confianza y una composición
  visual con ficha de comercio, mapa decorativo y flores del logo oficial.
- **Botones:** primario (guinda), secundario (blanco con borde), fantasma y blanco
  sobre fondo guinda. Altura mínima 46 px; 54 px en tamaño grande.
- **Tarjetas:** borde cálido, fondo blanco, radio 16 px, sombra suave; hover con
  elevación mínima.
- **Formularios:** labels visibles, ayudas, errores con `role="alert"`, foco con
  anillo guinda, radio cards accesibles y consentimiento explícito.
- **Progreso:** barra lateral en escritorio y barra superior en móvil.
- **Mapas:** Leaflet + teselas claras de Esri (Light Gray), con pin guinda y atribución.

## 4. Decisiones de adaptación

- **Sin Svelte:** se usan plantillas Jinja y rutas Flask; el diseño se traslada a
  CSS propio con variables.
- **Sin Tailwind:** se conserva la escala visual (contenedor, radios, spacings,
  estados) en CSS legible.
- **Sin Mapbox:** Leaflet + Esri Light Gray para no depender de una API key.
- **Sin iconos externos:** sprite de SVG inline para mantener el peso bajo.
- **Logo oficial:** se usa el activo de NegociaCDMX; el sitio se declara
  explícitamente como **prototipo no oficial** en el footer y el aviso de privacidad.
- **Accesibilidad:** `lang="es-MX"`, skip link, landmarks, labels, `aria-invalid`,
  `aria-describedby`, foco visible y `prefers-reduced-motion`.

## 5. Archivos

- `app/static/css/estilos.css` — tokens, componentes y responsive.
- `app/static/img/logo-gobierno-*` — logo oficial en PNG/WebP.
- `app/static/img/mapa-flores.png` — recorte decorativo del logo.
- `app/static/img/favicon.png` — escudo recortado.
- `app/static/js/app.js` — navegación, productos, horarios, mapas y copiado.

## Ajustes de carácter (2026-10-25)

Se retiraron las tarjetas flotantes y la animación del hero, se aplanó la banda
CTA y se quitaron las etiquetas de “Reto 1”/“Prototipo” de la cabecera. La
intención es que la plataforma se lea como un servicio público cotidiano y no
como una maqueta de producto.
