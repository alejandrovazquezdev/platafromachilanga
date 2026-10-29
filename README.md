# Centlalli · Plataforma de comercio popular

Prototipo para el **Reto 1 — Comercio popular y barrial** de Centlalli.
Permite registrar mercados, tianguis y tiendas de barrio, publicar su ficha,
explorar un directorio y conocer su panel de visibilidad.

> **Prototipo no oficial.** No es un sitio del Gobierno de la Ciudad de México.
> Los comercios del directorio son datos de demostración.

## Stack

- **Flask 3.1** + Jinja + SQLAlchemy + SQLite.
- **HTML/CSS/JS** sin Svelte ni Tailwind.
- **Gunicorn** en producción.
- **GitHub Actions + runner self-hosted** para CI/CD desde `main`.
- **Nginx + Let's Encrypt** en `chilangaton.devs-quarkz.com`.

## Pantallas

| Ruta | Pantalla |
|---|---|
| `/` | Landing del reto, beneficios, datos, FAQ |
| `/como-funciona` | Qué implica registrarse, requisitos y privacidad |
| `/registro/paso-1..4` | Wizard de registro |
| `/registro/confirmacion/<folio>` | Confirmación, folio y QR |
| `/directorio` | Directorio con filtros y mapa |
| `/comercio/<slug>` | Ficha pública |
| `/iniciar-sesion` | Login del negocio (diseño del equipo, funcional) |
| `/panel` | Dashboard del negocio: datos y alta de productos |
| `/salir` | Cerrar sesión |
| `/noticias` | Noticias útiles: regulación, apoyos, trámites |
| `/marco-legal` | Lo legal en simple, con fuentes oficiales |
| `/preguntas-frecuentes` | FAQ completa |
| `/digitaliza` | Punto de venta, inventario y diagnóstico |
| `/aviso-de-privacidad` | Aviso de privacidad |
| `/salud` | Health check |
| `/admin/login` | Panel secreto de operación (noticias y notificaciones) |

## Desarrollo local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
flask run --port 5110
```

Abre <http://127.0.0.1:5110>.

La base SQLite se crea en `instance/chilangaton.db` y se llena con 8 comercios de
demostración. Para reiniciar los datos:

```bash
rm instance/chilangaton.db
flask init-db
```

Variables opcionales en `.env` (ver `.env.example`):

```
SECRET_KEY=...
# DATABASE_URL=sqlite:////ruta/absoluta/instance/chilangaton.db
ADMIN_PASSWORD=...
VAPID_PUBLIC_KEY=...
VAPID_PRIVATE_KEY_PATH=vapid_private.pem
VAPID_SUBJECT=mailto:equipo@centlalli.mx
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5.6-luna
```

El módulo de notificaciones push requiere HTTPS (excepto `localhost`) y un navegador
con Push API. En iPhone, Safari exige agregar el sitio a la pantalla de inicio.

## Pruebas

```bash
python -m pytest -q
```

Cubren páginas públicas, salud, CSRF, flujo completo de registro, edición, noticias,
búsqueda difusa, digitalización, suscripciones push y acceso al panel de operación.

## Cuenta del negocio y dashboard

El registro pide **correo y contraseña**; con ellos se crea una cuenta (`Cuenta`) ligada
al comercio. El login usa el diseño original de `IS.html` y el dashboard usa el de
`dashboard.html` + `dashboard.css`, sin rediseñarlos.

- Login: `/iniciar-sesion` (también `/login`).
- Dashboard: `/panel`.
- Productos: el formulario del dashboard crea productos reales y se reflejan en la
  ficha pública.
- La contraseña se guarda con hash de Werkzeug; nunca en texto plano.
- Cuenta demo para probar: `donamari@chilangaton.mx` / `Centlalli2026`.
  Es solo para el hackathon; cámbiale la contraseña o elimínala antes de un uso real.

## Módulos nuevos

- **Noticias**: 6 contenidos hardcodeados en `app/data/seed.py`; el admin puede crear
  más y se guardan en SQLite.
- **Marco legal**: resumen informativo con enlaces a CDMX, SEDECO, SAT, LFPDPPP,
  COFEPRIS y PROFECO. No es asesoría legal.
- **Digitaliza**: módulo de punto de venta, inventario y diagnóstico. Se inspira en
  la operación de caja/inventario de MERP (`main`), **sin pasarela de pagos**; es un
  beneficio del registro y captura solicitudes de diagnóstico.
- **Chatbot “Centli”**: asistente con OpenAI (`gpt-5.6-luna`) que responde dudas
  de la web. La API key vive solo en `.env` del servidor.
- **Notificaciones Web Push**: prompt móvil, service worker, VAPID y envío desde el
  panel de operación.
- **Panel secreto**: `/admin/login` (no enlazado en la web). Contraseña en
  `ADMIN_PASSWORD` dentro de `.env`; sin ella, el panel responde 404.

## Búsqueda y mapa

- Búsqueda difusa en directorio y noticias: ignora acentos, mayúsculas y tolera
  errores leves (`app/search.py`).
- Mapa con Leaflet + Esri Light Gray, geocodificación gratuita con Nominatim
  (`/api/geocodificar`) y “Centrar en mi ubicación” con la geolocalización del
  navegador.
- Los datos de demostración están hardcodeados; el registro y las altas del admin
  persisten en SQLite.

## Diseño

El sistema visual se extrajo de `~/dev/negocia-cdmx` (identidad gubernamental
CDMX): guinda `#9F2241`, oro `#BC955C`, papel cálido, Inter y componentes
redondeados. El detalle está en [`docs/diseno-gubernamental.md`](docs/diseno-gubernamental.md).
Las decisiones del módulo de registro están en [`docs/registro.md`](docs/registro.md).

## Despliegue

- Directorio: `/var/www/platafromachilanga`
- Servicio: `platafromachilanga.service` (gunicorn en `127.0.0.1:5110`)
- Nginx: `chilangaton.devs-quarkz.com`
- Base: `instance/chilangaton.db`
- Workflow: `.github/workflows/ci.yml` (push a `main` → test → deploy → health)

### Operación en el VPS

```bash
sudo systemctl status platafromachilanga
sudo journalctl -u platafromachilanga -n 80 --no-pager
sudo systemctl restart platafromachilanga
curl -fsS http://127.0.0.1:5110/salud
```

## Estructura

```
app/
  __init__.py        fábrica Flask, CSRF, cabeceras, seed
  models.py          Comercio y Producto
  constants.py       catálogos y etiquetas
  routes/            main, registro, directorio, panel
  templates/         base + pantallas
  static/            CSS, JS, logo y recortes
  data/seed.py       8 comercios de demostración
docs/                diseño y modelo
tests/               pytest
```
