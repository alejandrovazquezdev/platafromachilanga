# Chilangatón · Plataforma de comercio popular

Prototipo para el **Reto 1 — Comercio popular y barrial** del Chilangatón 2026.
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
| `/panel` | Panel del comercio |
| `/aviso-de-privacidad` | Aviso de privacidad |
| `/salud` | Health check |

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
DATABASE_URL=sqlite:///instance/chilangaton.db
```

## Pruebas

```bash
python -m pytest -q
```

Cubren páginas públicas, salud, CSRF, flujo completo de registro y edición.

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
