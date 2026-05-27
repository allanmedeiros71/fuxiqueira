# Coding Conventions

**Analysis Date:** 2026-05-27

## Naming Patterns

**Files:**
- Use lowercase with underscores for Python modules: `models.py`, `views.py`, `forms.py`, `urls.py` inside Django apps.
- App packages: `accounts/`, `measurements/`; project config package: `bioimpedancia/`.
- Templates mirror URL/feature names in Portuguese: `templates/measurements/adicionar_medicao.html`, `templates/accounts/login_standalone.html`.
- Static assets under `static/css/` with descriptive names: `style.css`, `auth.css`.

**Functions and views:**
- Use `snake_case` for view functions and helpers: `adicionar_medicao`, `get_interpretacoes`, `aprovar_usuario`, `is_admin` in `measurements/views.py`.
- URL `name` arguments use `snake_case` Portuguese identifiers: `adicionar_medicao`, `editar_perfil`, `trocar_senha` in `measurements/urls.py`.

**Variables:**
- Use `snake_case` for locals and context keys: `ultima_medicao`, `chart_data`, `usuarios_pendentes_list`.
- Domain names in Portuguese: `medicao`, `medicoes`, `usuario`, `comparacoes`.

**Classes:**
- Use `PascalCase` for Django models, forms, and class-based views: `User`, `Measurement`, `CustomUserCreationForm`, `SignUpView` in `accounts/models.py`, `accounts/forms.py`, `accounts/views.py`.
- Admin classes: `UserAdmin`, `MeasurementAdmin` in `accounts/admin.py`, `measurements/admin.py`.

**Models and fields:**
- Model names in English (`User`, `Measurement`); field names in Portuguese where domain-specific: `nome`, `data_nascimento`, `altura`, `meta_peso`, `percentual_gordura`, `foto_frente` in `accounts/models.py`, `measurements/models.py`.
- `related_name` on FKs in Portuguese: `related_name="medicoes"` on `Measurement.usuario`.

## Code Style

**Formatting:**
- No project-level formatter or linter config detected (no `pyproject.toml`, `ruff.toml`, `.flake8`, `setup.cfg`, `black`, or `pre-commit`).
- Follow PEP 8 informally: 4-space indentation, blank lines between top-level definitions.
- **Quote style is mixed:** prefer double quotes for new Python code in `measurements/` and `accounts/` (e.g. `measurements/views.py`, `bioimpedancia/settings.py`). Some files use single quotes (`bioimpedancia/urls.py`, `accounts/urls.py`, `accounts/admin.py`, `manage.py`). When editing a file, match the dominant quote style in that file.

**Linting:**
- Not configured. Before adding CI, introduce one tool (e.g. Ruff) at repo root and run it on `accounts/`, `measurements/`, `bioimpedancia/`.

## Import Organization

**Order:**
1. Standard library (`import json`, `from pathlib import Path`)
2. Third-party Django and dependencies (`from django.contrib import messages`, `from decouple import config`)
3. Local app imports (`from accounts.models import User`, `from .models import Measurement`)

**Patterns:**
- Use absolute imports across apps: `from accounts.models import User as CustomUser` in `measurements/views.py`.
- Use relative imports within the same app: `from .forms import MeasurementForm`, `from .models import User` in `accounts/forms.py`.
- Lazy/local imports are acceptable for cycle avoidance or narrow scope: `from accounts.forms import UserProfileForm` inside `editar_perfil` in `measurements/views.py`; duplicate `from django.utils import timezone` inside `editar_medicao`.

**Path aliases:**
- None. Django apps are referenced by package name (`accounts`, `measurements`, `bioimpedancia`).

## Error Handling

**Patterns:**
- **HTTP 404:** Use `get_object_or_404(Model, ...)` with ownership checks, e.g. `get_object_or_404(Measurement, id=medicao_id, usuario=request.user)` in `measurements/views.py` (`editar_medicao`, `excluir_medicao`).
- **Form validation:** Standard Django `form.is_valid()` / `form.save()`; on failure, set flash messages and re-render template (`editar_perfil`, `trocar_senha`, `adicionar_medicao` in `measurements/views.py`).
- **User feedback:** Use `django.contrib.messages` — `messages.success` for happy paths, `messages.error` for validation failures. Messages are in Brazilian Portuguese.
- **Auth failures:** Rely on `@login_required` and `@user_passes_test(is_admin)` rather than manual checks in view bodies.
- **HTMX/API-style responses:** After mutations, if `request.headers.get("HX-Request")`, return `JsonResponse({"success": True})` instead of redirect (`adicionar_medicao`, `editar_medicao`, `excluir_medicao` in `measurements/views.py`).
- No custom exception classes, no structured logging of errors, no API error envelope beyond `JsonResponse`.

## Logging

**Framework:** Not used in application code (no `logging` imports in `accounts/` or `measurements/`).

**Patterns:**
- Rely on Django runserver/Gunicorn and server access logs for HTTP errors.
- For new server-side diagnostics, use `logging.getLogger(__name__)` in the module that owns the behavior; avoid `print()`.

## Comments

**When to Comment:**
- Module docstrings on Django entry/config files: `bioimpedancia/settings.py`, `bioimpedancia/urls.py`, `manage.py`.
- Inline comments for non-obvious business rules in Portuguese, e.g. approval flow in `accounts/forms.py` (`user.is_active = False`), section headers in `measurements/views.py` (dashboard stats, chart prep).
- Prefer self-explanatory names over comments for straightforward CRUD.

**Docstrings:**
- Use triple-quoted docstrings on non-trivial helpers: `get_interpretacoes(medicao)` in `measurements/views.py`.
- Django model `Meta` and `help_text` on fields carry user-facing documentation (`measurements/models.py`).

## Function Design

**Size:**
- Keep view functions focused on request/response orchestration; extract pure logic when a view exceeds ~80 lines or repeats calculations. Example candidate: `get_interpretacoes` (~60 lines) in `measurements/views.py` — keep as a module-level helper or move to `measurements/services.py` if it grows.

**Parameters:**
- Views take `(request)` or `(request, medicao_id)` / `(request, user_id)` matching URL converters in `measurements/urls.py`.
- Admin helper: `is_admin(user)` returns boolean for `@user_passes_test`.

**Return values:**
- HTML: `render(request, "app/template.html", context)`.
- Redirects: `redirect("url_name")` after POST success.
- JSON: `JsonResponse` only for HTMX success paths today.

## Module Design

**Exports:**
- No package-level `__all__`. Views are imported in `urls.py` via `from . import views` or explicit class imports in `accounts/urls.py`.
- Models/forms are imported where needed; no barrel `__init__.py` re-exports.

**Barrel files:**
- Not used.

## Django-Specific Conventions

**Apps:**
- `accounts`: auth, custom `User`, signup/login (`accounts/views.py`, `accounts/forms.py`).
- `measurements`: dashboard, CRUD medições, admin UI custom (`measurements/views.py`).
- Register apps in `INSTALLED_APPS` in `bioimpedancia/settings.py`; set `AUTH_USER_MODEL = "accounts.User"`.

**Views:**
- **Class-based views** for auth flows extending Django generics: `CustomLoginView`, `SignUpView` in `accounts/views.py`.
- **Function-based views** with decorators for domain features in `measurements/views.py`.

**Forms:**
- Subclass `UserCreationForm` / `ModelForm` in `accounts/forms.py`, `measurements/forms.py`.
- Put Tailwind utility classes in widget `attrs` on forms (repeat pattern: `w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500`).
- New inactive users: set `user.is_active = False` in `CustomUserCreationForm.save()`.

**Models:**
- Implement `__str__` returning human-readable Portuguese labels.
- Put cross-cutting persistence logic in `save()` when appropriate (IMC auto-calc in `Measurement.save()` in `measurements/models.py`).
- Ordering via `Meta.ordering` (e.g. `["-data_hora"]`).

**URLs:**
- Root: `bioimpedancia/urls.py` — `admin/`, `accounts/`, include `measurements.urls` at `""`.
- Named routes required for `{% url %}` and `redirect()`; use consistent `name=` strings.

**Templates:**
- Extend `templates/base.html`; set `{% block title %}` and `{% block content %}`.
- Language: `lang="pt-br"` in `templates/base.html`.
- Load static with `{% load static %}`; CSRF on all POST forms.
- Crispy Forms: `{% load crispy_forms_tags %}` in some measurement templates; several forms render fields manually — when adding fields, either use Crispy consistently or follow the manual Tailwind input pattern in `templates/measurements/adicionar_medicao.html`.

**Configuration:**
- Environment via `python-decouple` `config()` in `bioimpedancia/settings.py`; never commit `.env` (see `.env.example` for variable names only).
- Locale: `LANGUAGE_CODE = "pt-br"`, `TIME_ZONE = "America/Sao_Paulo"`.

**Security:**
- Always `@login_required` on user data views.
- Staff/admin custom UI: `@user_passes_test(is_admin)` where `is_admin` checks `is_superuser or is_staff`.
- Scope querysets to `request.user` for measurements.
- Use `@require_POST` for destructive actions (`excluir_medicao`).

## Frontend Conventions (Templates / Static)

- Mobile-first Tailwind via CDN in `templates/base.html`.
- Chart data passed as JSON string in context: `"chart_data": json.dumps(chart_data)` from `measurements/views.py`.
- Custom CSS in `static/css/style.css` and `static/css/auth.css`.
- Portuguese UI copy throughout templates.

## Duplication to Avoid

- IMC calculation appears in `Measurement.save()`, `adicionar_medicao`, and `editar_medicao`. Prefer model `save()` or a single helper rather than copying `round(float(peso) / (float(altura) ** 2), 2)` in views.
- Chart payload construction is duplicated between `dashboard` and `historico` in `measurements/views.py` — extract a small function if extending metrics.

## Where to Add New Code

| Change | Location |
|--------|----------|
| New user field | `accounts/models.py` + migration + `accounts/forms.py` + templates under `templates/accounts/` |
| New measurement field | `measurements/models.py` + migration + `measurements/forms.py` + templates under `templates/measurements/` |
| New authenticated page | `measurements/views.py` (or `accounts/views.py`), route in `measurements/urls.py`, template in `templates/` |
| Admin-only feature | Decorators on view in `measurements/views.py`; link from `templates/base.html` admin menu block |
| Settings / integration | `bioimpedancia/settings.py` + `.env.example` (names only, no secrets) |

---

*Convention analysis: 2026-05-27*
