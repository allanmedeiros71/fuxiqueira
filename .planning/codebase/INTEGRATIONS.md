# External Integrations

**Analysis Date:** 2026-05-27

## APIs & External Services

**Bioimpedance / health devices:**
- Not detected — no SDK or API client for smart scales; users enter measurement values manually via `MeasurementForm` (`measurements/forms.py`, `measurements/views.py`)

**Third-party HTTP APIs:**
- None in Python dependencies or application code — no `requests`, `httpx`, or vendor SDKs in `requirements.txt` or `*.py`

**CDN (browser-loaded assets):**
- Tailwind CSS — styling via script tag in `templates/base.html`
- Chart.js — evolution charts on dashboard (`templates/measurements/dashboard.html`, `templates/base.html`)
- HTMX — partial-page interactions (script in `templates/base.html`; project docs reference HTMX but most UI is full page loads)

## Data Storage

**Databases:**
- PostgreSQL (primary for Docker and documented local dev)
  - Engine: `django.db.backends.postgresql` when `DB_NAME` is not `db.sqlite3` (`bioimpedancia/settings.py`)
  - Connection vars: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` via `python-decouple`
  - Client: Django ORM + `psycopg2-binary`
  - Compose service: `db` image `postgres:15` (`docker-compose.yml`)
- SQLite (optional dev fallback)
  - Trigger: `DB_NAME=db.sqlite3` in environment
  - File: `BASE_DIR / "db.sqlite3"` (`bioimpedancia/settings.py`)
  - Listed in `.gitignore` as `db.sqlite3`

**File Storage:**
- Local filesystem only
  - User photos: `Measurement.foto_frente`, `foto_perfil`, `foto_costas` with `upload_to="fotos/%Y/%m/"` (`measurements/models.py`)
  - `MEDIA_ROOT` = `media/`, `MEDIA_URL` = `/media/` (`bioimpedancia/settings.py`)
  - Served by Django in `DEBUG` (`bioimpedancia/urls.py`) or Nginx in Docker (`nginx.conf` `location /media/`)
  - Processing: Pillow (`requirements.txt`)

**Caching:**
- None — no Redis, Memcached, or Django cache backend configured

## Authentication & Identity

**Auth Provider:**
- Custom Django authentication (no OAuth/SAML/social login)
  - Custom user model: `accounts.User` extending `AbstractUser` (`accounts/models.py`, `AUTH_USER_MODEL` in `bioimpedancia/settings.py`)
  - Login identifier: `email` (`USERNAME_FIELD = "email"`)
  - Session-based auth: Django sessions + `AuthenticationMiddleware` (`bioimpedancia/settings.py`)
  - Views: `accounts/views.py` (`CustomLoginView`, `CustomLogoutView`, `SignUpView`)
  - URLs: `accounts/urls.py` under `/accounts/`
  - Password validators: Django defaults in `AUTH_PASSWORD_VALIDATORS`
- User approval workflow (application-level, not external IdP):
  - New signups set `is_active=False` (`accounts/forms.py` `CustomUserCreationForm.save`)
  - Staff/superuser approves via `measurements/views.py` (`aprovar_usuario`, `rejeitar_usuario`) at `/admin/aprovar/`, `/admin/rejeitar/`
  - Admin gate: `is_staff` or `is_superuser` (`measurements/views.py` `is_admin`)
- Django admin: `/admin/` (`bioimpedancia/urls.py`, `accounts/admin.py`, `measurements/admin.py`)

## Monitoring & Observability

**Error Tracking:**
- None — no Sentry, Rollbar, or similar

**Logs:**
- Django default logging (no custom `LOGGING` dict in `bioimpedancia/settings.py`)
- `*.log` and `logs/` gitignored (`.gitignore`)
- Docker: `docker-compose logs -f web` per `README.md`

## CI/CD & Deployment

**Hosting:**
- Self-hosted / local Docker Compose — Nginx + Gunicorn + PostgreSQL (`docker-compose.yml`, `nginx.conf`, `Dockerfile`)
- Public entry: host port `80` (Nginx), app port `8000` exposed on `web` service

**CI Pipeline:**
- Not detected — no `.github/workflows/`, GitLab CI, or similar

## Environment Configuration

**Required env vars (production-like):**
- `SECRET_KEY` — Django secret
- `DEBUG` — boolean (`False` in Compose `web` service)
- `ALLOWED_HOSTS` — comma-separated hosts
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` — PostgreSQL (Compose sets these inline on `web` service)

**Optional env vars:**
- `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` — SMTP (`bioimpedancia/settings.py`; defaults to console backend locally)

**Secrets location:**
- Local: `.env` (gitignored; exists in dev workspaces) loaded by `python-decouple`
- Docker Compose: inline `environment` on `web` service for DB and email (development defaults; replace for real production)
- Template only in repo: `.env.example`

**CSRF / browser:**
- `CSRF_TRUSTED_ORIGINS` hardcoded for localhost preview ports in `bioimpedancia/settings.py` (not env-driven)

## Email

**Outbound SMTP:**
- Django `EMAIL_*` settings via `config()` (`bioimpedancia/settings.py`)
- Default dev: `django.core.mail.backends.console.EmailBackend`
- Docker stack: SMTP to **Mailpit** (`EMAIL_HOST=mailpit`, port `1025`, TLS off) — service `mailpit` image `axllent/mailpit`, UI on host port `8025` (`docker-compose.yml`)
- Documented optional provider: Gmail SMTP placeholders in `.env.example` (commented)
- **Note:** No `send_mail` or notification views in `*.py` — email backend is configured but not actively used by application flows yet

## Webhooks & Callbacks

**Incoming:**
- None — no webhook endpoints or signature verification

**Outgoing:**
- None — no callbacks to external systems

## Internal JSON endpoints

**AJAX (not external integrations):**
- `JsonResponse` from `measurements/views.py` for form/profile actions (e.g. password change, measurement delete) — same-origin Django views, not public API

## Integration summary table

| Integration        | Role                          | Config / entry                         |
|--------------------|-------------------------------|----------------------------------------|
| PostgreSQL         | Primary persistence           | `DB_*`, `docker-compose.yml` `db`      |
| SQLite             | Optional local DB             | `DB_NAME=db.sqlite3`                   |
| Local media        | Progress photos               | `MEDIA_*`, `measurements/models.py`    |
| Mailpit (Docker)   | Dev SMTP capture              | `docker-compose.yml`, `EMAIL_*` on web |
| CDN (Tailwind/Chart/HTMX) | Frontend assets        | `templates/base.html`                  |
| Django sessions    | Auth                          | `bioimpedancia/settings.py` middleware |

---

*Integration audit: 2026-05-27*
