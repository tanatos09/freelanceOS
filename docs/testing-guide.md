# 🧪 Testovací Dokumentace – freelanceOS

Kompletní průvodce testováním projektu freelanceOS.

---

## 📋 Obsah

1. [Přehled testovací strategie](#přehled-testovací-strategie)
2. [Struktura testů](#struktura-testů)
3. [Instalace závislostí](#instalace-závislostí)
4. [Spuštění testů](#spuštění-testů)
5. [Psaní testů](#psaní-testů)
6. [Fixtures a Factories](#fixtures-a-factories)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Přehled testovací strategie

Projekt používá **pytest** s **pytest-django** pro testování. Strategie se dělí na:

| Typ        | Popis                                    | Příklady              |
|------------|------------------------------------------|----------------------|
| **Unit**   | Testy jednotlivých komponent            | Modely, Serializers  |
| **Integration** | Testy API endpointů                | API testy            |
| **Edge Cases** | Testy okrajových případů          | Validace, Permisse   |

### Pokrytí

- **Modely**: vytvoření, validace, vztahy
- **Serializers**: validace, transformace
- **API**: CRUD operace, filtrování, hledání
- **Permissions**: autorizace, ownership
- **Edge Cases**: chybná data, neautentifikace

---

## Struktura testů

```
freelanceos/
├── tests/                          # Globální testovací infrastruktura
│   ├── __init__.py
│   ├── conftest.py                 # Globální pytest fixtures
│   ├── factories.py                # Factory Boy factories
│   └── utils.py                    # Helper funkce
│
├── users/tests/                    # Testy aplikace users
│   ├── __init__.py
│   ├── conftest.py                 # Lokální fixtures
│   ├── test_models.py             # Testy User a UserProfile modelů
│   ├── test_serializers.py        # Testy serializerů
│   └── test_api.py                # API endpoint testy
│
├── clients/tests/                  # Testy aplikace clients
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_serializers.py
│   └── test_api.py
│
├── projects/tests/                 # Testy aplikace projects
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_serializers.py
│   └── test_api.py
│
└── pytest.ini                      # Pytest konfigurace
```

---

## Instalace závislostí

### 1. Install pytest a pytest-django

```bash
pip install pytest pytest-django pytest-cov pytest-timeout
pip install factory-boy
```

Nebo přes requirements:
```bash
pip install -r requirements/testing.txt
```

### 2. Ověřit instalaci

```bash
pytest --version
```

---

## Spuštění testů

### Všechny testy

```bash
pytest
```

### Testy konkrétní aplikace

```bash
# Users testy
pytest users/tests/

# Clients testy
pytest clients/tests/

# Projects testy
pytest projects/tests/
```

### Konkrétní test soubor

```bash
pytest users/tests/test_models.py
pytest clients/tests/test_api.py
```

### Konkrétní test třída

```bash
pytest users/tests/test_models.py::TestUserModelCreation
```

### Konkrétní test funkce

```bash
pytest users/tests/test_models.py::TestUserModelCreation::test_create_user_success
```

---

## Pokročilé spuštění

### Markery (tag)

```bash
# Pouze unit testy
pytest -m unit

# Pouze integrační testy
pytest -m integration

# Edge cases
pytest -m edge_cases

# Vše kromě pomalých testů
pytest -m "not slow"

# Kombinace
pytest -m "unit or integration" --co
```

### Verbose režim

```bash
# Detailní výstup
pytest -vv

# Zobrazit print statements
pytest -s

# Zobrazit pokrytí kódu
pytest --cov
```

### Spuštění s debuggingem

```bash
# Zastavit na chybě a spustit pdb
pytest --pdb

# Zastavit na prvním selhání
pytest -x

# Zastavit po N selháních
pytest --maxfail=3
```

### Generování zpráv

```bash
# HTML report pokrytí
pytest --cov=users,clients,projects --cov-report=html
# Otevřít: htmlcov/index.html

# JUnit XML report
pytest --junit-xml=junit.xml

# Coverage report v terminálu
pytest --cov --cov-report=term-missing
```

---

## Psaní testů

### Základní struktura

```python
import pytest
from rest_framework import status

pytestmark = pytest.mark.unit  # Přiřadit marker


class TestSomethingModel:
    """Testy pro model Something."""
    
    def test_something_success(self, user):
        """Test: Krátka popiska."""
        # Arrange
        data = {'key': 'value'}
        
        # Act
        result = user.do_something(data)
        
        # Assert
        assert result is True
    
    def test_something_validation(self, db):
        """Test: Validace selhá."""
        with pytest.raises(ValueError):
            invalid_operation()
```

### Použití fixtures

```python
def test_something(user, client_obj, project):
    """Fixtures se automaticky vkládají."""
    assert user.email == 'testuser@example.com'
    assert client_obj.user == user
```

### API testy

```python
class TestSomeEndpoint:
    """Testy pro API endpoint."""
    
    def test_endpoint_authenticated(self, auth_client, user):
        """Test: Autentifikovaný uživatel."""
        response = auth_client.get('/api/v1/endpoint/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_endpoint_unauthenticated(self, api_client):
        """Test: Neautentifikovaný přístup."""
        response = api_client.get('/api/v1/endpoint/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

---

## Fixtures a Factories

### Dostupné globální fixtures

**Uživatelé:**
- `user` – běžný uživatel (testuser@example.com)
- `user_alt` – druhý uživatel
- `superuser` – admin uživatel

**Objekty:**
- `client_obj` – jeden klient
- `clients_list` – seznam 5 klientů
- `project` – jeden projekt
- `projects_list` – seznam 5 projektů

**API:**
- `api_client` – REST API klient bez autentifikace
- `auth_client` – autentifikovaný API klient
- `access_token` – JWT access token
- `refresh_token` – JWT refresh token
- `tokens` – oba tokeny

### Vytváření vlastních fixtures

V `app/tests/conftest.py`:

```python
@pytest.fixture
def my_fixture(user):
    """Moje custom fixture."""
    return SomeObject.objects.create(user=user)
```

### Použití Factory Boy

```python
from tests.factories import UserFactory, ClientFactory

# V testu
user = UserFactory(email='custom@example.com', password='pass123')
client = ClientFactory(user=user, name='Custom Client')
```

---

## Best Practices

### ✅ DO: Dobré praktiky

```python
# 1. Jasná jména testů
✓ def test_user_creates_successfully(self, user):
✗ def test_user(self):

# 2. Jeden assert za test (obvykle)
✓ def test_email_validation(self):
✗ def test_user_model(self):  # příliš mnoho assertů

# 3. Používej fixtures
✓ def test_something(self, user):
✗ def test_something(self):
✗     user = User.objects.create_user(...)

# 4. Markuj testy
✓ @pytest.mark.unit
✗ # žádný marker

# 5. Edge cases
✓ def test_negative_budget_rejected(self):
✗ # pouze happy path testy

# 6. Testuj chyby
✓ def test_duplicate_email_fails(self):
✗ # pouze happy path

# 7. Testuj přístupová práva
✓ def test_user_cannot_see_other_users_data(self):
✗ # chybějí permission testy
```

### ❌ DON'T: Špatné praktiky

```python
# Hardcoded hodnoty
✗ def test_something(self):
✗     response = api_client.get('/api/v1/clients/123/')

# Testovací data v datasetu
✗ def test_something(self):
✗     # Spoléhání se na jiný test

# Side effects
✗ def test_something(self):
✗     user.delete()  # Ovlivňuje další testy

# Pomalé testy bez @pytest.mark.slow
✗ def test_something(self):
✗     time.sleep(5)

# Hardcoded hesla
✗ password = 'secretpassword123'  # Use fixtures!
```

---

## Troubleshooting

### Test selhal: "Table does not exist"

**Příčina:** TestCase nevytvořil test DB

**Řešení:**
```bash
pytest --create-db
# nebo
pytest --nomigrations  # Přeskočit migrace
```

### Import Error: "No module named 'app'"

**Příčina:** PYTHONPATH není nastaven

**Řešení:**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Test je pomalý

**Příčina:** Asset na DB, API volání, apod.

**Řešení:**
```python
# Markuj jako slow
@pytest.mark.slow
def test_something_slow(self):
    ...

# Spusť bez slow testů
pytest -m "not slow"
```

### Fixtures není dostupná

**Příčina:** Fixture je v špatném conftest.py

**Řešení:**
- Globální fixtures: `tests/conftest.py`
- App-specific fixtures: `app/tests/conftest.py`
- Pytest hledá v pořadí: lokální → globální

### Test je flaky (občas selhá)

**Příčina:** Race conditions, timing issues

**Řešení:**
```python
# Spusť opakovaně
pytest --count=10

# Spusť jednotlivě
pytest -x --tb=short
```

---

## Kontinuální integrace

### GitHub Actions příklad

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - run: pip install -r requirements/testing.txt
      - run: pytest --cov
```

---

## Užitečné příkazy

```bash
# Všechna běžná pravidla
pytest

# Detailní výstup + zalte si print statements
pytest -vv -s

# Jenom unit testy
pytest -m unit

# Jenom API testy s HTML reportem
pytest -m integration --cov --cov-report=html

# Spuštění v watch módu (vyžaduje pytest-watch)
ptw

# Spuštění specifické app
pytest users/

# Spuštění a zastavení na chybě
pytest -x

# Spuštění s debuggerem
pytest --pdb
```

---

## Further Reading

- [pytest documentation](https://docs.pytest.org/)
- [pytest-django](https://pytest-django.readthedocs.io/)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Factory Boy](https://factory-boy.readthedocs.io/)

---

**Poslední update:** 2026-03-08  
**verze:** 1.0
