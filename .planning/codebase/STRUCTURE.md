# Codebase Structure

**Analysis Date:** 2026-05-27

## Directory Layout

```
fuxiqueira/                          # Repo root (product name: Fuxiqueira)
├── bioimpedancia/                   # Django project package (settings, root URLs, WSGI)
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/                        # Auth app: custom User, login/signup/password reset
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   ├── apps.py
│   └── migrations/
├── measurements/                    # Domain app: measurements, dashboard, custom admin UI
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   ├── apps.py
│   └── migrations/
├── templates/                       # Project-wide templates (DIRS in settings)
│   ├── base.html
│   ├── accounts/
│   └── measurements/
├── static/                          # Dev static files (STATICFILES_DIRS)
│   └── css/
├── media/                           # User uploads (runtime; often gitignored)
├── manage.py                        # Django CLI entry
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── .env.example                     # Env template (copy to .env locally)
└── README.md
```

## Directory Purposes

**`bioimpedancia/`:**
- Purpose: Django project configuration — not a reusable app.
- Contains: `settings.py`, root `urls.py`, WSGI/ASGI.
- Key files: `bioimpedancia/settings.py`, `bioimpedancia/urls.py`

**`accounts/`:**
- Purpose: Identity — custom user model, registration, login/logout, password reset URLs.
- Contains: `User` model, CBVs, `CustomUserCreationForm`, `UserProfileForm`.
- Key files: `accounts/models.py`, `accounts/views.py`, `accounts/urls.py`

**`measurements/`:**
- Purpose: Core product — bioimpedance records, dashboard, history, profile/password pages, staff approval UI.
- Contains: `Measurement` model, FBVs, `MeasurementForm`, app URLconf mounted at site root.
- Key files: `measurements/models.py`, `measurements/views.py`, `measurements/urls.py`

**`templates/`:**
- Purpose: All HTML; shared chrome in `base.html`.
- Contains: `accounts/*` (login standalone, password reset), `measurements/*` (dashboard, forms, admin page).
- Key files: `templates/base.html`, `templates/measurements/dashboard.html`

**`static/`:**
- Purpose: CSS and assets collected to `staticfiles/` in Docker build.
- Contains: `static/css/style.css`, `static/css/auth.css`
- Key files: Referenced via `{% static %}` in templates

**`media/`:**
- Purpose: Uploaded measurement photos (`ImageField` → `fotos/%Y/%m/`).
- Generated: Yes (runtime uploads)
- Committed: Typically no (check `.gitignore`)

**`.planning/codebase/`:**
- Purpose: GSD architecture/stack docs for planners and executors.
- Generated: By mapping agents
- Committed: Yes (project documentation)

## Key File Locations

**Entry Points:**
- `manage.py`: Local dev and management commands (`migrate`, `createsuperuser`, `runserver`).
- `bioimpedancia/wsgi.py`: Production WSGI application object for Gunicorn.
- `bioimpedancia/urls.py`: Top-level URL routing.

**Configuration:**
- `bioimpedancia/settings.py`: Installed apps, DB, static/media, `AUTH_USER_MODEL`, crispy, email, login URLs.
- `.env.example`: Documented env var names (use `.env` locally — do not commit secrets).
- `docker-compose.yml`: Postgres, web, nginx, mailpit services.
- `nginx.conf`: Reverse proxy and static/media aliases.

**Core Logic:**
- `accounts/models.py`: `User` custom model.
- `measurements/models.py`: `Measurement` model and IMC `save()` hook.
- `measurements/views.py`: Dashboard, CRUD, admin approval, `get_interpretacoes`.
- `accounts/forms.py` / `measurements/forms.py`: Input validation and widgets.

**Testing:**
- Not detected: no `tests.py` or `tests/` package in apps.

## Naming Conventions

**Files:**
- Django apps: lowercase single word (`accounts`, `measurements`).
- Python modules: lowercase with underscores (`views.py`, `forms.py`).
- Templates: lowercase with underscores, grouped by area (`editar_medicao.html`, `login_standalone.html`).
- Migrations: auto-generated numeric prefix (`0001_initial.py`, `0002_...`).

**Directories:**
- App directories match `AppConfig.name` in `apps.py`.
- Template subdirs mirror app names (`templates/accounts/`, `templates/measurements/`).

**Python symbols:**
- Models: PascalCase (`User`, `Measurement`).
- Views/functions: snake_case (`adicionar_medicao`, `get_interpretacoes`).
- URL names: snake_case (`adicionar_medicao`, `editar_perfil`, `aprovar_usuario`).
- Related names: Portuguese domain terms (`medicoes` on User → Measurement FK).

**Routes (public URLs):**
- Auth under `/accounts/` (`accounts/urls.py`).
- App features at site root: `/`, `/adicionar/`, `/historico/`, `/editar/<id>/`, etc. (`measurements/urls.py`).
- Django built-in admin: `/admin/` (`bioimpedancia/urls.py`).

## Where to Add New Code

**New measurement field or behavior:**
- Model + migration: `measurements/models.py` → `python manage.py makemigrations measurements`
- Form fields/widgets: `measurements/forms.py`
- View logic and chart keys: `measurements/views.py` (`dashboard`, `historico` if graphed)
- Template display: `templates/measurements/dashboard.html`, `historico.html`, `adicionar_medicao.html`, `editar_medicao.html`
- Staff list columns (optional): `measurements/admin.py`

**New user profile field:**
- Model: `accounts/models.py`
- Signup: `accounts/forms.py` (`CustomUserCreationForm`)
- Profile edit: `accounts/forms.py` (`UserProfileForm`) — used from `measurements/views.py` `editar_perfil`
- Template: `templates/measurements/editar_perfil.html`
- Django admin fieldsets: `accounts/admin.py`

**New authenticated page:**
- View in `measurements/views.py` (or `accounts/views.py` if auth-only)
- `path()` in `measurements/urls.py` (or `accounts/urls.py`)
- Template under `templates/measurements/` or `templates/accounts/`
- Nav link in `templates/base.html` (desktop + mobile menu blocks)

**New auth flow:**
- Prefer CBV in `accounts/views.py` matching existing `CustomLoginView` / `SignUpView` style
- Register route in `accounts/urls.py`
- Template under `templates/accounts/`; use `*_standalone.html` pattern for pages without main nav

**Shared presentation / assets:**
- Global layout or CDN scripts: `templates/base.html`
- CSS: `static/css/style.css` (app) or `static/css/auth.css` (auth pages)

**Utilities or services (recommended for new non-trivial logic):**
- No `services/` package exists today — introduce `measurements/services/` or `measurements/utils.py` rather than growing `views.py` further.

**Infrastructure / deploy:**
- Python deps: `requirements.txt`
- Container: `Dockerfile`, `docker-compose.yml`
- Proxy: `nginx.conf`

## Special Directories

**`*/migrations/`:**
- Purpose: Django schema history per app.
- Generated: Yes (`makemigrations`)
- Committed: Yes — always commit migration files with model changes.

**`staticfiles/`:**
- Purpose: `collectstatic` output in Docker (`STATIC_ROOT`).
- Generated: Yes in build (`Dockerfile` runs `collectstatic`)
- Committed: No (build artifact / volume)

**`media/`:**
- Purpose: User-uploaded images.
- Generated: Yes at runtime
- Committed: No

**`venv/` or local env:**
- Purpose: Local Python virtualenv if used.
- Committed: No (standard practice)

## URL Map (quick reference)

| Path | View | App |
|------|------|-----|
| `/` | `dashboard` | measurements |
| `/adicionar/` | `adicionar_medicao` | measurements |
| `/historico/` | `historico` | measurements |
| `/editar/<id>/` | `editar_medicao` | measurements |
| `/excluir/<id>/` | `excluir_medicao` (POST) | measurements |
| `/editar-perfil/` | `editar_perfil` | measurements |
| `/trocar-senha/` | `trocar_senha` | measurements |
| `/admin/` (name `admin`) | `admin_view` | measurements — **conflicts with Django admin URL order** |
| `/accounts/login/` | `CustomLoginView` | accounts |
| `/accounts/signup/` | `SignUpView` | accounts |
| `/admin/` (Django) | `admin.site.urls` | contrib — registered first in root urls |

---

*Structure analysis: 2026-05-27*
