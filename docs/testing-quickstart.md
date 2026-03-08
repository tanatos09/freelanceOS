# 🚀 Quick Start Guide – Testování

Rychlý návodka pro začátek testování freelanceOS.

---

## 5-Minute Setup

### 1️⃣ Install

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install
pip install -r requirements/testing.txt
```

### 2️⃣ Run Tests

```bash
# Všechny testy
pytest

# Detailně
pytest -vv -s

# Jen jednu app
pytest users/tests/
```

### 3️⃣ View Coverage Report

```bash
# Generovat HTML report
pytest --cov --cov-report=html

# Otevřit report
# Windows: start htmlcov/index.html
# macOS: open htmlcov/index.html
# Linux: firefox htmlcov/index.html
```

---

## Common Commands

```bash
# Všechny testy se jménem detailů
pytest -vv

# Slušechni test s výstupem print()
pytest -s

# Zastavit na prvním selhání
pytest -x

# Spustit jen poslední selhané
pytest --lf

# Spustit konkrétní test
pytest users/tests/test_models.py::TestUserModelCreation::test_create_user_success

# Filtr podle markeru
pytest -m unit          # Jenom unit testy
pytest -m integration   # Jenom API testy

# Paralelní spuštění (4x rychlejší)
pytest -n 4

# Pokrytí kódu
pytest --cov
```

---

## Test Structure

Každá aplikace má 3 testy:

```
app/tests/
├── test_models.py      ← Testy modelů
├── test_serializers.py ← Testy serializerů
└── test_api.py         ← Testy API
```

---

## Writing New Tests

### Model Test Template

```python
import pytest

pytestmark = pytest.mark.unit

class TestMyModel:
    def test_creation_success(self, db):
        """Test: Vytvoření."""
        obj = MyModel.objects.create(name='Test')
        assert obj.name == 'Test'
```

### API Test Template

```python
import pytest
from rest_framework import status

pytestmark = pytest.mark.integration

class TestMyEndpoint:
    def test_list_success(self, auth_client):
        """Test: List endpoint."""
        response = auth_client.get('/api/v1/items/')
        assert response.status_code == status.HTTP_200_OK
```

---

## Available Fixtures

```python
# Users
def test_something(user, user_alt, superuser):
    pass

# Objects
def test_something(client_obj, project, clients_list):
    pass

# API
def test_something(api_client, auth_client):
    pass

# Tokens
def test_something(access_token, refresh_token):
    pass
```

See `tests/conftest.py` for more.

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| "Table does not exist" | `pytest --create-db` |
| "No module named" | Check PYTHONPATH |
| Test is slow | Mark with `@pytest.mark.slow` |
| Flaky test | Run with `pytest --count=10` |

---

## Learn More

- 📖 **TESTING_GUIDE.md** – Detailní průvodce
- 🏗️ **TESTING_ARCHITECTURE.md** – Architektura a strategie
- 📋 **TEST_SUITE_SUMMARY.md** – Shrnutí

---

## Next Steps

1. ✅ Spustit všechny testy: `pytest`
2. View pokrytí: `pytest --cov --cov-report=html`
3. Napsat nový test pro nový feature
4. Přidej do CI/CD pipeline

**Happy Testing!** 🎉

---

**Verze:** 1.0  
**Poslední update:** 2026-03-08
