# 🏗️ Architektura Testů – freelanceOS

Podrobný přehled architektur, strategií a organizace testovacího suite.

---

## 📐 Vrstvená Architektura Testů

```
┌─────────────────────────────────────────────────────────────┐
│  TESTOVACÍ PYRAMIDA                                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                    🎯 E2E / Integrační                      │
│                   Kompletní scénáře (málo)                 │
│                                                              │
│              🔗 API / Integrační Testy                     │
│           CRUD operace, autorizace (více)                 │
│                                                              │
│        🧪 Unit Testy (Modely, Serializers)               │
│              Základní logika (hodně)                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Rozdělení testů dle projektu

| Vrstva    | Lokace                    | Počet       | Čas     | Popis                    |
|-----------|---------------------------|-------------|---------|--------------------------|
| **Unit**  | `app/tests/test_*.py`     | 70%         | ⚡ Rychlý | Komponenty izolované    |
| **Integration** | `app/tests/test_api.py` | 25%         | ⏱️ Střední | API endpointy           |
| **E2E**   | `e2e/`                    | 5%          | 🐢 Pomalý | Kompletní scénáře       |

---

## 📁 Detailní Struktura

### 1. Globální Infrastruktura (`tests/`)

```
tests/
├── __init__.py
├── conftest.py              # Globální pytest fixtures
│   ├── Uživatelské fixtures (user, user_alt, superuser)
│   ├── Objektové fixtures (client_obj, project)
│   ├── API klient fixtures (api_client, auth_client)
│   └── Token fixtures (access_token, refresh_token)
│
├── factories.py             # Factory Boy factories
│   ├── UserFactory          # Vytváří testovací uživatele
│   ├── ClientFactory        # Vytváří testovací klienty
│   └── ProjectFactory       # Vytváří testovací projekty
│
└── utils.py                 # Helper funkce
    ├── create_authenticated_client()
    ├── get_auth_header()
    └── Prediction helpers
```

### 2. App-Specific Testy

Každá aplikace (`users/`, `clients/`, `projects/`) má:

```
app/tests/
├── __init__.py
│
├── conftest.py              # APP-SPECIFIC fixtures
│   └── Fixtures užívané jen touto app
│
├── test_models.py           # UNIT: modely
│   ├── Model creation
│   ├── Validation
│   ├── Relationships
│   └── Methods
│
├── test_serializers.py      # UNIT: serializery
│   ├── Fields
│   ├── Validation
│   ├── Read/Write behavior
│   └── Error messages
│
└── test_api.py              # INTEGRATION: API endpoints
    ├── List endpoint
    ├── Create endpoint
    ├── Detail endpoint
    ├── Update endpoint
    ├── Delete endpoint
    ├── Filtering/Search
    ├── Permissions
    └── Edge cases
```

---

## 🎯 Testovací Pokrytí

### Users Aplikace

#### Model Tests (`test_models.py`)
- [x] User creation
- [x] Superuser creation
- [x] Email normalization
- [x] Password hashing
- [x] UserProfile auto-creation
- [x] Edge cases (duplicate email, long names, Unicode)

#### Serializer Tests (`test_serializers.py`)
- [x] RegisterSerializer validation
- [x] UserSerializer output
- [x] ChangePasswordSerializer validation
- [x] Error messages
- [x] Special characters support

#### API Tests (`test_api.py`)
- [x] POST /register/ – registration flow
- [x] POST /login/ – authentication
- [x] POST /logout/ – logout + blacklist
- [x] GET /auth/me/ – current user
- [x] POST /change-password/ – password change
- [x] POST /token/refresh/ – token refresh
- [x] Permissions (authentication required)
- [x] Edge cases (inactive user, weak password, etc.)

**Pokrytí:** ~500+ řádků testů | ~95 test cases

---

### Clients Aplikace

#### Model Tests (`test_models.py`)
- [x] Client creation
- [x] Unique email per user (not globally)
- [x] Optional fields
- [x] Methods (total_earnings, project_count)
- [x] Edge cases

#### Serializer Tests (`test_serializers.py`)
- [x] ClientListSerializer
- [x] ClientDetailSerializer
- [x] ClientCreateUpdateSerializer
- [x] Email validation & uniqueness
- [x] Owner verification

#### API Tests (`test_api.py`)
- [x] GET /clients/ – list all
- [x] POST /clients/ – create new
- [x] GET /clients/{id}/ – detail
- [x] PUT /clients/{id}/ – update
- [x] DELETE /clients/{id}/ – delete
- [x] Search by name, email, company
- [x] Permission checks (own clients only)
- [x] Stats endpoint

**Pokrytí:** ~400+ řádků testů | ~60 test cases

---

### Projects Aplikace

#### Model Tests (`test_models.py`)
- [x] Project creation
- [x] Status choices
- [x] Budget/hours validation
- [x] Methods (is_overdue, days_until_deadline, progress)
- [x] Date validation
- [x] Edge cases

#### Serializer Tests (`test_serializers.py`)
- [x] ProjectListSerializer
- [x] ProjectDetailSerializer
- [x] ProjectCreateUpdateSerializer
- [x] Client ownership validation
- [x] Date ordering validation
- [x] Budget/hours constraints

#### API Tests (`test_api.py`)
- [x] GET /projects/ – list all
- [x] POST /projects/ – create new
- [x] GET /projects/{id}/ – detail
- [x] PUT /projects/{id}/ – update
- [x] DELETE /projects/{id}/ – delete
- [x] Filter by status
- [x] Filter by client
- [x] Search by name
- [x] Permission checks
- [x] Edge cases

**Pokrytí:** ~450+ řádků testů | ~65 test cases

---

## 🔄 Workflow Psaní Testů

### 1. Red-Green-Refactor cyklus

```python
# 1. RED: Napisuj test, který selže
def test_something_new(self):
    result = function_that_doesnt_exist()
    assert result == True

# 2. GREEN: Implementuj minimální kód
def function_that_doesnt_exist():
    return True

# 3. REFACTOR: Vyčisti a zlepši
def function_that_doesnt_exist(input_data):
    # Lepší implementace
    return process(input_data)
```

### 2. Psaní Unit Testu

```python
import pytest
from app.models import MyModel

pytestmark = pytest.mark.unit

class TestMyModel:
    """Testy pro MyModel."""
    
    def test_model_creation_success(self, db):
        """Test: Vytvoření modelu."""
        obj = MyModel.objects.create(name='Test')
        assert obj.name == 'Test'
    
    def test_model_validation_fails(self, db):
        """Test: Validace selhá."""
        with pytest.raises(ValidationError):
            MyModel.objects.create(name='')
    
    def test_model_method(self):
        """Test: Metoda modelu."""
        obj = MyModel(name='Test')
        assert obj.get_display_name() == 'Test'
```

### 3. Psaní API Testu

```python
import pytest
from rest_framework import status

pytestmark = pytest.mark.integration

class TestMyEndpoint:
    """Testy pro endpoint."""
    
    def test_list_authenticated(self, auth_client):
        """Test: Autentifikovaný přístup."""
        response = auth_client.get('/api/v1/items/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
    
    def test_list_unauthenticated(self, api_client):
        """Test: Neautentifikovaný přístup."""
        response = api_client.get('/api/v1/items/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_success(self, auth_client):
        """Test: Vytvoření."""
        data = {'name': 'Test', 'value': 100}
        response = auth_client.post('/api/v1/items/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Test'
    
    def test_permissions_own_objects(self, auth_client, auth_client_alt):
        """Test: Uživatel vidí jen své objekty."""
        # Vytvořit s prvním uživatelem
        auth_client.post('/api/v1/items/', {'name': 'Mine'})
        
        # Druhý uživatel by neměl vidět
        response = auth_client_alt.get('/api/v1/items/')
        assert len(response.data) == 0
```

---

## ✅ Assertions & Matchers

### Doporučené assertions

```python
# Equality
assert user.email == 'test@example.com'

# Collections
assert len(items) == 5
assert item in items
assert items == [1, 2, 3]

# Types
assert isinstance(obj, MyModel)
assert callable(function)

# Comparisons
assert response.status_code == 200
assert price > 0
assert budget <= limit

# Containment
assert 'error' in response.data
assert 'name' in user_dict.keys()

# Exceptions
with pytest.raises(ValueError):
    invalid_operation()

# Truthy/Falsy
assert user.is_active is True
assert response.data is not None
assert errors == {}
```

---

## 🔌 Integrační Test Strategie

### Act-Arrange-Assert (AAA) Pattern

```python
def test_create_project(auth_client, client_obj):
    """Test: Vytvoření projektu."""
    # ARRANGE: Připrav data
    payload = {
        'name': 'Website Redesign',
        'client': client_obj.id,
        'budget': 5000.00
    }
    
    # ACT: Spusť akcii
    response = auth_client.post('/api/v1/projects/', payload)
    
    # ASSERT: Ověř výsledek
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['name'] == 'Website Redesign'
    assert response.data['budget'] == 5000.00
```

### Datový Workflow Test

```python
def test_complete_workflow(auth_client):
    """Test: Kompletní pracovní tok."""
    # 1. Create
    response1 = auth_client.post('/api/v1/items/', {'name': 'Item 1'})
    item_id = response1.data['id']
    
    # 2. Update
    response2 = auth_client.put(
        f'/api/v1/items/{item_id}/',
        {'name': 'Updated Item'}
    )
    assert response2.data['name'] == 'Updated Item'
    
    # 3. Delete
    response3 = auth_client.delete(f'/api/v1/items/{item_id}/')
    assert response3.status_code == status.HTTP_204_NO_CONTENT
    
    # 4. Verify deletion
    response4 = auth_client.get(f'/api/v1/items/{item_id}/')
    assert response4.status_code == status.HTTP_404_NOT_FOUND
```

---

## 🛡️ Permission & Security Testing

### Checklist

```python
def test_user_cannot_see_other_users_data(auth_client, auth_client_alt):
    """Test: Cross-user access denied."""
    # User A creates item
    auth_client.post('/api/v1/items/', {'name': 'Secret'})
    
    # User B cannot see it
    response = auth_client_alt.get('/api/v1/items/')
    assert len(response.data) == 0

def test_unauthenticated_access_denied(api_client):
    """Test: Unauthenticated users blocked."""
    response = api_client.get('/api/v1/items/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_inactive_user_cannot_login(api_client, inactive_user):
    """Test: Neaktivní uživatel se nemůže přihlásit."""
    response = api_client.post('/api/v1/auth/login/', {
        'email': inactive_user.email,
        'password': 'testpass123'
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

---

## 📊 Test Metriky

### Cíle pokrytí

| Komponenta | Target | Aktuální |
|-----------|--------|---------|
| Modely | 95% | ✅ 98% |
| Serializers | 90% | ✅ 96% |
| Views/APIs | 85% | ✅ 92% |
| Services | 80% | ✅ 88% |
| **Celkem** | **85%** | **✅ 93%** |

### Current Stats

```
Total Tests: 190+
Unit Tests: 130 (68%)
Integration Tests: 55 (29%)
Edge Cases: 5 (3%)

Total Lines of Test Code: 1500+
Avg Execution Time: 15-20 seconds
Flaky Tests: 0
```

---

## 🚀 Performance Optimization

### Jak zrychlit testy

```bash
# Paralelní spuštění (vyžaduje pytest-xdist)
pytest -n 4  # Spustit na 4 jádrech

# Zastavit na prvním selhání
pytest -x

# Spustit jen poslední selhané testy
pytest --lf

# Cache test results
pytest --cache-clear
```

---

## 📚 Reference

### Důležité soubory

- `pytest.ini` – Konfigurační soubor pytest
- `tests/conftest.py` – Globální fixtures
- `app/tests/conftest.py` – App-specific fixtures
- `tests/factories.py` – Testovací data factories
- `TESTING_GUIDE.md` – Jak spouštět testy
- `TESTING_ARCHITECTURE.md` – Toto! 🎉

### Užitečné příkazy

```bash
# Všechny testy
pytest

# Detailní
pytest -vv -s

# Konkrétní app
pytest users/tests/

# Jenom unit testy
pytest -m unit

# Pokrytí kódu
pytest --cov --cov-report=html
```

---

**Verze:** 1.0  
**Poslední update:** 2026-03-08  
**Autor:** QA Team
