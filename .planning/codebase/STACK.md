# Technology Stack

**Analysis Date:** 2026-05-27

## Languages

**Primary:**
- Python 3.11 (Docker base image in `Dockerfile`) — application runtime, Django apps (`accounts/`, `measurements/`, `bioimpedancia/`)
- Python 3.12 (local `venv/` per `venv/pyvenv.cfg`) — development; README requires 3.11+

**Secondary:**
- HTML (Django templates) — `templates/`, including `templates/base.html`, `templates/accounts/`, `templates/measurements/`
- CSS — `static/css/style.css`, `static/css/auth.css` (subset of Tailwind-like utilities, not a build pipeline)
- JavaScript (inline in templates) — menu mobile, Chart.js setup, HTMX config in `templates/base.html` and `templates/measurements/dashboard.html`

## Runtime

**Environment:**
- CPython via Docker (`python:3.11-slim` in `Dockerfile`) or local virtualenv (`venv/`)
- WSGI: Gunicorn (`gunicorn` in `requirements.txt`, `bioimpedancia/wsgi.py`)
- ASGI entry exists but unused for async: `bioimpedancia/asgi.py`

**Package Manager:**
- pip (implicit; no `pyproject.toml` or `Pipfile`)
- Lockfile: **missing** — only pinned versions in `requirements.txt`

## Frameworks

**Core:**
- Django 4.2.7 — monolithic web app (`manage.py`, project package `bioimpedancia/`)
- django-crispy-forms 2.1 + crispy-bootstrap5 0.7 — form rendering (`bioimpedancia/settings.py` `CRISPY_*`, forms in `accounts/forms.py`, `measurements/forms.py`)

**Testing:**
- Not detected — no test runner in `requirements.txt`, no `tests.py` or `test_*.py` files

**Build/Dev:**
- django-extensions 3.2.3 — dev utilities (`INSTALLED_APPS` in `bioimpedancia/settings.py`)
- Gunicorn 21.2.0 — production WSGI server (`Dockerfile` CMD, `docker-compose.yml` `web` service)
- Docker Compose 3.8 — multi-container dev/prod-like stack (`docker-compose.yml`)
- Nginx (official `nginx:alpine` image) — reverse proxy and static/media serving (`nginx.conf`, `docker-compose.yml`)

## Key Dependencies

**Critical:**
- `Django==4.2.7` — routing, ORM, auth, admin, templates
- `psycopg2-binary==2.9.9` — PostgreSQL driver when `DB_NAME` ≠ `db.sqlite3` (`bioimpedancia/settings.py`)
- `python-decouple==3.8` — environment-based settings via `config()` in `bioimpedancia/settings.py`
- `Pillow==10.1.0` — `ImageField` on `Measurement` (`measurements/models.py`)

**Infrastructure:**
- `gunicorn==21.2.0` — app server behind Nginx
- PostgreSQL 15 (`postgres:15` in `docker-compose.yml`) — primary database in Docker/local docs

**Frontend (CDN, not pip):**
- Tailwind CSS — `https://cdn.tailwindcss.com` in `templates/base.html`
- Chart.js — `https://cdn.jsdelivr.net/npm/chart.js` in `templates/base.html` (loaded twice in same file)
- HTMX 1.9.10 — `https://unpkg.com/htmx.org@1.9.10` in `templates/base.html` (configured; limited `hx-*` usage in templates)

## Configuration

**Environment:**
- `python-decouple` `config()` reads from process environment and, by convention, a `.env` file in the project root (not committed; listed in `.gitignore`)
- Template for local setup: `.env.example` (documents `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DB_*`, optional email vars)
- `.env` file **present** in workspace (gitignored) — do not commit; copy from `.env.example` for new environments
- Django settings module: `bioimpedancia.settings` (`manage.py`, `bioimpedancia/wsgi.py`)

**Key configs required:**
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` — security and host allowlist (`bioimpedancia/settings.py`)
- `DB_NAME` (+ `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` for PostgreSQL) — set `DB_NAME=db.sqlite3` to use SQLite file at project root instead of Postgres
- Optional email: `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`

**Build:**
- `Dockerfile` — install deps, `collectstatic`, run Gunicorn on port 8000
- `docker-compose.yml` — `db`, `web`, `mailpit`, `nginx` services with named volumes for Postgres, static, and media
- `nginx.conf` — proxy to `web:8000`, serve `/static/` and `/media/` from volumes
- No `webpack`, `vite`, or Node toolchain — static assets are committed under `static/` and collected to `staticfiles/`

## Platform Requirements

**Development:**
- Python 3.11+ and pip (`README.md`)
- Optional: PostgreSQL locally, or SQLite via `DB_NAME=db.sqlite3`
- Virtualenv recommended: `python -m venv venv` then `pip install -r requirements.txt`
- Run: `python manage.py runserver` (`manage.py`)
- Migrations: `accounts/migrations/`, `measurements/migrations/`

**Production:**
- Docker Compose stack: Nginx (port 80) → Gunicorn (`web:8000`) → PostgreSQL (`db`)
- `DEBUG=False` and strong `SECRET_KEY` expected in production (documented in `.env.example` comments)
- `STATIC_ROOT` = `staticfiles/` (populated by `collectstatic` in `Dockerfile`)
- `MEDIA_ROOT` = `media/` (user-uploaded photos; volume `media_volume` in Compose)
- Locale: `LANGUAGE_CODE = "pt-br"`, `TIME_ZONE = "America/Sao_Paulo"` (`bioimpedancia/settings.py`)

---

*Stack analysis: 2026-05-27*
