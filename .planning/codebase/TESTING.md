# Testing Patterns

**Analysis Date:** 2026-05-27

## Test Framework

**Runner:**
- Django built-in test runner (ships with Django 4.2.7 in `requirements.txt`).
- Config: implicit via `manage.py` and `bioimpedancia/settings.py` — no dedicated `pytest.ini`, `setup.cfg`, or `tox.ini`.

**Assertion library:**
- `unittest` assertions via `django.test.TestCase` / `SimpleTestCase` (standard Django pattern).

**Dependencies:**
- No `pytest`, `pytest-django`, `factory_boy`, `model_bakery`, or `coverage` in `requirements.txt`.

**Run commands:**
```bash
# Activate venv, install deps, run migrations first
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate

# Run all tests (none exist yet — discovers tests.py / tests/ packages)
python manage.py test

# Run one app when tests exist
python manage.py test accounts
python manage.py test measurements

# Verbose
python manage.py test --verbosity=2

# Keep DB between runs (faster iteration)
python manage.py test --keepdb
```

**Docker:**
```bash
docker-compose exec web python manage.py test
```

## Current State

**Automated tests:** Not detected.

- No `accounts/tests.py`, `measurements/tests.py`, or `tests/` packages.
- No `test_*.py` or `*_test.py` files in the repository.
- No GitHub Actions or other CI workflow under `.github/`.
- `.gitignore` includes `.pytest_cache/`, `.coverage`, `htmlcov/` — tooling placeholders only, not active use.

**Manual / operational testing:**
- `PROJECT_STATUS.md` references manual verification (e.g. camera capture, Mailpit for email in Docker).
- PostgreSQL healthcheck in `docker-compose.yml` (`pg_isready`) — infrastructure only, not application tests.

## Recommended Test File Organization

**Location (prescriptive — adopt when adding tests):**
- Co-locate per Django app: `accounts/tests/` and `measurements/tests/`.
- Split modules by concern:
  - `accounts/tests/test_models.py`
  - `accounts/tests/test_forms.py`
  - `accounts/tests/test_views.py`
  - `measurements/tests/test_models.py`
  - `measurements/tests/test_views.py`

**Naming:**
- Files: `test_<area>.py`
- Classes: `class MeasurementModelTests(TestCase):`
- Methods: `def test_imc_calculated_on_save_when_missing(self):`

**Structure:**
```
fuxiqueira/
├── accounts/
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_forms.py
│       └── test_views.py
├── measurements/
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       └── test_views.py
└── manage.py
```

## Test Structure

**Suite organization (recommended pattern aligned with codebase):**
```python
from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import User
from measurements.models import Measurement


class DashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="tester",
            email="tester@example.com",
            password="safe-pass-123",
            nome="Tester",
            data_nascimento="1990-01-01",
            altura="1.75",
            is_active=True,
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_dashboard_ok_for_authenticated_user(self):
        self.client.login(username="tester", password="safe-pass-123")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
```

**Patterns:**
- **Setup:** Create users with all `REQUIRED_FIELDS` from `accounts/models.py` (`username`, `nome`, `data_nascimento`, `altura`; email as `USERNAME_FIELD`).
- **Inactive users:** Default signup sets `is_active=False` in `accounts/forms.py` — assert login blocked until approval.
- **Teardown:** Django `TestCase` wraps each test in a transaction and rolls back DB changes.
- **Assertions:** `assertEqual`, `assertContains`, `assertRedirects`, `assertFalse(self.user.medicoes.exists())`.

## Mocking

**Framework:** `unittest.mock` (stdlib) — sufficient for this project size.

**Patterns:**
```python
from unittest.mock import patch

@patch("measurements.views.timezone")
def test_interpretacoes_use_local_time(mock_tz, ...):
    ...
```

**What to mock:**
- Email sending (`EMAIL_BACKEND` in tests can stay `django.core.mail.backends.locmem.EmailBackend` via test settings override).
- External SMTP — never hit real `EMAIL_HOST` in tests.
- Time-dependent logic in `get_interpretacoes` (`measurements/views.py`) if assertions depend on “today”.

**What NOT to mock:**
- Django ORM for model and view integration tests — use `TestCase` database.
- `form.is_valid()` / `save()` flows — exercise real forms in `accounts/forms.py`, `measurements/forms.py`.

## Fixtures and Factories

**Test data:**
- No factories exist today. Prefer small helper functions in `accounts/tests/factories.py` until volume justifies `factory_boy`:

```python
from datetime import date
from accounts.models import User

def make_user(**kwargs):
    defaults = {
        "username": "user1",
        "email": "user1@example.com",
        "password": "pass12345",
        "nome": "Usuário Teste",
        "data_nascimento": date(1990, 5, 15),
        "altura": "1.70",
        "is_active": True,
    }
    defaults.update(kwargs)
    password = defaults.pop("password")
    user = User.objects.create_user(**defaults)
    user.set_password(password)
    user.save()
    return user
```

**Measurement fixture fields** (from `measurements/models.py`): `peso`, `imc`, `percentual_gordura`, `percentual_massa_muscular`, `metabolismo_basal`, `idade_metabolica`, `indice_gordura_visceral`.

## Test Settings

**Database:**
- Django creates a separate test database for PostgreSQL configs in `bioimpedancia/settings.py`.
- For fast local unit tests, optional `DJANGO_SETTINGS_MODULE` override or `settings.py` branch with `DB_NAME=db.sqlite3` (already supported when `DB_NAME == "db.sqlite3"`).

**Media:**
- Use `tempfile` / `django.test.override_settings(MEDIA_ROOT=...)` when testing `ImageField` uploads (`foto_frente`, etc.).

## Coverage

**Requirements:** None enforced in repo.

**View coverage (when adding tooling):**
```bash
pip install coverage
coverage run --source='accounts,measurements' manage.py test
coverage report
coverage html   # output in htmlcov/ (gitignored)
```

## Test Types

**Unit tests:**
- Model: `Measurement.save()` auto-IMC when `usuario.altura` set (`measurements/models.py`).
- Model: `User.idade` property (`accounts/models.py`).
- Form: `CustomUserCreationForm` sets `is_active=False` (`accounts/forms.py`).
- Pure helper: `get_interpretacoes` thresholds (`measurements/views.py`) — can use `SimpleTestCase` with a minimal mock measurement object.

**Integration tests (priority):**
- Signup → inactive user cannot log in.
- Admin `aprovar_usuario` / `rejeitar_usuario` (`measurements/views.py`) — staff-only, 302 + message.
- CRUD medições scoped to owner: user A cannot `editar_medicao` / `excluir_medicao` for user B (expect 404).
- `excluir_medicao` requires POST (`@require_POST`).
- Dashboard/historico return 200 and include `chart_data` context key.

**HTMX behavior:**
```python
response = self.client.post(
    reverse("adicionar_medicao"),
    data={...},
    HTTP_HX_REQUEST="true",
)
self.assertEqual(response.status_code, 200)
self.assertJSONEqual(response.content, b'{"success": true}')
```
Pattern from `request.headers.get("HX-Request")` checks in `measurements/views.py`.

**E2E tests:**
- Not used. Browser flows (Chart.js, Tailwind CDN, camera capture) are manual. Playwright/Cypress only if product requirements demand it.

## High-Priority Coverage Gaps

| Area | Risk | Files |
|------|------|-------|
| User approval workflow | Wrong users gain access | `accounts/forms.py`, `measurements/views.py` |
| Measurement ownership | IDOR on edit/delete | `measurements/views.py` |
| IMC calculation | Wrong health metrics | `measurements/models.py`, views |
| Admin gate | Non-staff access to admin UI | `is_admin`, `measurements/views.py` |
| Signup inactive default | Active users without approval | `accounts/forms.py` |

## Adding Tests to the Workflow

1. Create `accounts/tests/` and `measurements/tests/` as above.
2. Add optional dev dependencies in a `requirements-dev.txt` (`pytest-django`, `coverage`) — keep `requirements.txt` lean for production Docker image in `Dockerfile`.
3. Add CI (e.g. `.github/workflows/test.yml`) running `python manage.py test` against SQLite or service PostgreSQL.
4. Run tests before PRs; do not commit `.env` or real credentials.

## Common Patterns

**Async testing:**
- Not applicable — views are synchronous Django functions/classes.

**Error testing:**
```python
def test_editar_medicao_404_for_other_user(self):
    owner = make_user(username="owner", email="owner@example.com")
    other = make_user(username="other", email="other@example.com")
    medicao = Measurement.objects.create(usuario=owner, ...)
    self.client.login(username="other", password="pass12345")
    response = self.client.get(
        reverse("editar_medicao", kwargs={"medicao_id": medicao.pk})
    )
    self.assertEqual(response.status_code, 404)
```

**Messages framework:**
```python
from django.contrib.messages import get_messages

response = self.client.post(...)
messages = list(get_messages(response.wsgi_request))
self.assertTrue(any("sucesso" in str(m).lower() for m in messages))
```

**Class-based signup:**
- Use `Client.post(reverse("signup"), data={...})` and assert redirect to `login` and inactive user in DB.

---

*Testing analysis: 2026-05-27*
