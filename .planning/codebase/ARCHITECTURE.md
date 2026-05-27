<!-- refreshed: 2026-05-27 -->
# Architecture

**Analysis Date:** 2026-05-27

## System Overview

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                         Browser (mobile-first UI)                        │
│  Tailwind CDN · Chart.js · HTMX · templates + `static/css/`           │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ HTTP
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Nginx (prod) — `nginx.conf`  →  proxy `/` to Gunicorn                  │
│              static `/static/` · media `/media/` from Docker volumes     │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Django 4.2 WSGI — `bioimpedancia/wsgi.py` · `manage.py`                │
│  Middleware stack · Sessions · CSRF · Auth (`bioimpedancia/settings.py`) │
├──────────────────────┬──────────────────────┬───────────────────────────┤
│  `accounts/`         │  `measurements/`     │  `django.contrib.admin`   │
│  Auth & User model   │  Measurements CRUD   │  Model admin UI           │
│  CBV login/signup    │  Dashboard, charts   │  at `/admin/`             │
└──────────┬───────────┴──────────┬───────────┴─────────────┬─────────────┘
           │                      │                         │
           └──────────────────────┼─────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  PostgreSQL (prod/Docker) or SQLite (`DB_NAME=db.sqlite3`)              │
│  Media files on disk — `media/` (`MEDIA_ROOT` in settings)              │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| URL router | Mounts admin, accounts, and measurements routes | `bioimpedancia/urls.py` |
| Settings | Apps, DB, static/media, auth model, email, crispy | `bioimpedancia/settings.py` |
| Custom User | Profile fields, email login, approval via `is_active` | `accounts/models.py` |
| Auth views | Login, logout, signup (inactive until approved) | `accounts/views.py` |
| Auth forms | Registration and profile editing | `accounts/forms.py` |
| Measurement | Bioimpedance records, photos, IMC on save | `measurements/models.py` |
| App views | Dashboard, CRUD, admin approval UI, chart payloads | `measurements/views.py` |
| Forms | Measurement input widgets (mobile-friendly) | `measurements/forms.py` |
| Templates | Server-rendered pages, extends `base.html` | `templates/` |
| Django Admin | Staff UI for User and Measurement models | `accounts/admin.py`, `measurements/admin.py` |

## Pattern Overview

**Overall:** Classic Django **MTV** monolith — server-rendered HTML, thin split into two domain apps, **no REST API** and **no separate service layer**.

**Key Characteristics:**
- **Function-based views (FBV)** dominate `measurements/views.py`; **class-based views (CBV)** only in `accounts/views.py` for auth.
- **Fat views:** query logic, chart JSON assembly, and health interpretations live in view functions (e.g. `get_interpretacoes` in `measurements/views.py`).
- **Forms as boundary:** `ModelForm` / `UserCreationForm` subclasses validate and persist; views attach `request.user` and redirect with Django messages.
- **Custom admin workflow** uses `is_active=False` on signup and staff-only views for approve/reject — parallel to but separate from Django’s built-in admin.

## Layers

**Presentation (templates + static):**
- Purpose: HTML UI, Chart.js charts, navigation, mobile menu JS in `templates/base.html`.
- Location: `templates/`, `static/css/`
- Contains: Django templates (`{% extends 'base.html' %}`, `{% load crispy_forms_tags %}` where used), CSS (`style.css`, `auth.css`).
- Depends on: View context dicts; CDN scripts (Tailwind, Chart.js, HTMX).
- Used by: All authenticated and auth flows.

**URL / routing:**
- Purpose: Map paths to views; include app URLconfs.
- Location: `bioimpedancia/urls.py`, `accounts/urls.py`, `measurements/urls.py`
- Contains: `path()` / `include()` definitions; DEBUG-only static/media serving in root urls.
- Depends on: View callables and Django auth URL names for password reset.
- Used by: HTTP entry.

**Views (controllers):**
- Purpose: Auth checks, ORM queries, context building, redirects, optional HTMX `JsonResponse`.
- Location: `accounts/views.py`, `measurements/views.py`
- Contains: `@login_required`, `@user_passes_test(is_admin)`, POST handlers.
- Depends on: Models, forms, `messages`, `json`.
- Used by: Templates via `render()`.

**Forms:**
- Purpose: Input validation and widget attrs (Tailwind classes inline).
- Location: `accounts/forms.py`, `measurements/forms.py`
- Depends on: Models; crispy bootstrap5 pack configured globally in settings.
- Used by: Views and some templates (manual fields in `adicionar_medicao.html`).

**Models (data):**
- Purpose: Persistence, relations, light domain logic (IMC calculation on `Measurement.save`).
- Location: `accounts/models.py`, `measurements/models.py`
- Depends on: Django ORM only.
- Used by: Views, admin, migrations under `*/migrations/`.

**Infrastructure:**
- Purpose: Process model, DB, reverse proxy, email capture in Docker.
- Location: `Dockerfile`, `docker-compose.yml`, `nginx.conf`, `bioimpedancia/wsgi.py`
- Depends on: `python-decouple` env vars (never commit `.env`).

## Data Flow

### Primary request path (authenticated dashboard)

1. Request hits `bioimpedancia/urls.py` → `include('measurements.urls')` with prefix `''`.
2. `measurements/urls.py` maps `""` → `dashboard` (`measurements/views.py`).
3. `@login_required` ensures session user; view loads `request.user.medicoes` (related name on `Measurement.usuario`).
4. View builds `chart_data` as Python dict → `json.dumps` into template context (`measurements/views.py` ~90–116).
5. `get_interpretacoes(ultima_medicao)` adds display strings for IMC, fat %, etc. (`measurements/views.py` ~122–183).
6. `render(request, "measurements/dashboard.html", context)` — template parses `chart_data` in inline script for Chart.js.

### Signup and approval flow

1. `POST /accounts/signup/` → `SignUpView` + `CustomUserCreationForm` (`accounts/views.py`, `accounts/forms.py`).
2. `form.save()` sets `user.is_active = False` (`accounts/forms.py` ~27–28).
3. User logs in only after staff sets `is_active=True` via `aprovar_usuario` or Django admin (`measurements/views.py` ~46–51, `accounts/admin.py`).
4. `CustomLoginView` redirects authenticated users to named route `dashboard` (`accounts/views.py` ~13–14).

### Add measurement flow

1. `GET/POST /adicionar/` → `adicionar_medicao` (`measurements/views.py` ~220–241).
2. `MeasurementForm` validates POST; view sets `medicao.usuario = request.user`, may compute IMC from `request.user.altura`.
3. `medicao.save()` triggers model `save()` IMC fallback (`measurements/models.py` ~30–33).
4. On success: `messages.success` + redirect `dashboard`, or `JsonResponse` if `HX-Request` header present.
5. Photos stored under `media/fotos/%Y/%m/` via `ImageField` on model.

### Production deploy path

1. `docker-compose` starts `db` (Postgres 15), `web` (migrate + Gunicorn), `nginx`, `mailpit`.
2. Nginx proxies `/` to `web:8000`, serves collected static and media from volumes (`docker-compose.yml`, `nginx.conf`).
3. Gunicorn loads `bioimpedancia.wsgi:application` (`Dockerfile`, `docker-compose.yml` web command).

**State Management:**
- **Server-side session** via `django.contrib.sessions` and auth middleware; no client state store.
- **Flash messages** via `django.contrib.messages` (`MESSAGE_TAGS` maps to Bootstrap alert classes in `bioimpedancia/settings.py`).
- **Chart state** recomputed per request from ORM; embedded as JSON string in HTML.

## Key Abstractions

**Custom User (`AUTH_USER_MODEL = "accounts.User"`):**
- Purpose: Email-as-username login, profile (nome, altura, metas), age property.
- Examples: `accounts/models.py`, referenced as `ForeignKey` in `measurements/models.py`.
- Pattern: Extend `AbstractUser`; `USERNAME_FIELD = "email"`.

**Measurement aggregate per user:**
- Purpose: Time-series bioimpedance readings and optional progress photos.
- Examples: `measurements/models.py`; accessed as `user.medicoes` (`related_name="medicoes"`).
- Pattern: FK to User, default ordering `-data_hora`; IMC derived from peso + user altura.

**Admin gate (`is_admin`):**
- Purpose: Restrict custom admin pages to `is_superuser` or `is_staff`.
- Examples: `measurements/views.py` ~17–18, decorators on `admin_view`, `aprovar_usuario`, `rejeitar_usuario`.
- Pattern: `@user_passes_test(is_admin)` — not a Django permission codename.

**Chart payload contract:**
- Purpose: Single JSON blob for Chart.js datasets.
- Examples: Built in `dashboard` and `historico` views with keys `labels`, `peso`, `imc`, `percentual_gordura`, etc.
- Pattern: `chart_data: json.dumps(chart_data)` in template context — keep keys stable when adding metrics.

## Entry Points

**Development server:**
- Location: `manage.py`
- Triggers: `python manage.py runserver`
- Responsibilities: Sets `DJANGO_SETTINGS_MODULE=bioimpedancia.settings`, runs Django dev server.

**WSGI (production):**
- Location: `bioimpedancia/wsgi.py`
- Triggers: Gunicorn (`Dockerfile` CMD, `docker-compose.yml` web service)
- Responsibilities: Expose `application` for HTTP workers.

**Root URLconf:**
- Location: `bioimpedancia/urls.py`
- Triggers: Every HTTP request
- Responsibilities: `/admin/` → Django admin; `/accounts/` → auth; `/` → measurements routes.

## Architectural Constraints

- **Threading:** Sync WSGI workers (Gunicorn); no async views or Channels detected.
- **Global state:** None beyond Django settings and ORM connection pool; no custom singletons.
- **Auth required:** All measurement routes use `@login_required` except none on measurements urls — accounts handles public login/signup/password reset only.
- **Database switch:** `DB_NAME == "db.sqlite3"` selects SQLite file at project root; any other name uses Postgres env vars (`bioimpedancia/settings.py` ~73–92).
- **Custom user:** Must use `get_user_model()` or `accounts.models.User` — do not use `django.contrib.auth.models.User` for FKs.
- **Media uploads:** `client_max_body_size 20M` in `nginx.conf`; forms use `enctype="multipart/form-data"` where photos are included.

## Anti-Patterns

### URL collision on `/admin/`

**What happens:** `bioimpedancia/urls.py` registers `path('admin/', admin.site.urls)` before `include('measurements.urls')`, while `measurements/urls.py` also defines `path("admin/", views.admin_view, name="admin")`.
**Why it's wrong:** First match wins at request time — browser visits to `/admin/` hit **Django admin**, not the custom `admin_view` template at `templates/measurements/admin.html`. The named URL `{% url 'admin' %}` still resolves to `measurements.views.admin_view`, causing confusion between link target and resolved route order.
**Do this instead:** Mount custom admin under a distinct prefix (e.g. `path('gestao/', ...)` or `path('aprovacoes/', ...)`) and update menu links in `templates/base.html`.

### Fat views with embedded domain rules

**What happens:** `get_interpretacoes()` (~60 lines) and chart assembly duplicate between `dashboard` and `historico` inside `measurements/views.py`.
**Why it's wrong:** Hard to test, reuse, or change clinical thresholds without touching HTTP layer.
**Do this instead:** Extract to `measurements/services/interpretacoes.py` or `measurements/utils.py` and unit-test thresholds; keep views thin (query + call helper + render).

### HTMX-ready backend without HTMX markup

**What happens:** Views branch on `request.headers.get("HX-Request")` (`measurements/views.py` ~235–236, 260–261, 305–306) but templates have **no** `hx-*` attributes (grep across `templates/`).
**Why it's wrong:** Dead code path; README claims HTMX interactions that are mostly unused.
**Do this instead:** Either add `hx-post` / `hx-target` on forms and partial templates, or remove HX branches and use standard redirects only.

### Signup sets inactive but login form does not explain state

**What happens:** Inactive users hit Django’s default login failure for disabled accounts.
**Why it's wrong:** Poor UX for “awaiting approval” flow documented in README.
**Do this instead:** Override `CustomLoginView.form_invalid` or use a custom authentication form with a clear message when `user.is_active` is False.

## Error Handling

**Strategy:** Django defaults — form errors in context, HTTP 404 via `get_object_or_404` scoped by `usuario=request.user` on measurement edits/deletes.

**Patterns:**
- `messages.success` / `messages.error` after mutations (`measurements/views.py`, `accounts/views.py`).
- Ownership check: `get_object_or_404(Measurement, id=medicao_id, usuario=request.user)` prevents cross-user access.
- HTMX POST success returns `JsonResponse({"success": True})` without standardized error JSON.

## Cross-Cutting Concerns

**Logging:** Not configured beyond Django defaults; no structured logging module.

**Validation:** Model field constraints + `ModelForm` / `UserCreationForm`; password validators from `AUTH_PASSWORD_VALIDATORS` in settings.

**Authentication:** Session cookies; `LOGIN_URL = "/accounts/login/"`, `LOGIN_REDIRECT_URL = "/dashboard/"`; email-based `User.USERNAME_FIELD`; staff approval via `is_active`.

---

*Architecture analysis: 2026-05-27*
