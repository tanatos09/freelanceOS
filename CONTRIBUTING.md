# Přispívání do FreelanceOS

Děkuji za zájem o přispívání! Projekt je stále v aktivním vývoji a přispívání je vítáno.

---

## 🚀 Jak Začít

### Předpoklady

- Python 3.10+
- PostgreSQL 12+ (pro testování databáze)
- Git
- pytest a development tools

### Setup pro Přispívání

```bash
# 1. Fork repository a klonuj si ho
git clone https://github.com/yourusername/freelanceos.git
cd freelanceos

# 2. Vytvoř virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# nebo
.\venv\Scripts\Activate.ps1  # Windows (PowerShell)

# 3. Instaluj dev dependencies
pip install -r requirements-dev.txt

# 4. Zkopíruj .env file
cp .env.example .env

# 5. Vytvořit a vyplnit .env
# - Vygeneruj SECRET_KEY
# - NastavDatabase credentials
# - Nastav ALLOWED_HOSTS=localhost,127.0.0.1

# 6. Spusť migrace
python manage.py migrate

# 7. Spusť testy (měly by projít)
pytest
```

---

## 📋 Workflow

### 1. Vytvoř Feature Branch

```bash
# Aktualizuj main
git checkout main
git pull origin main

# Vytvoř nový branch (descriptive name)
git checkout -b feature/amazing-feature
# nebo
git checkout -b fix/security-issue
# nebo
git checkout -b docs/api-reference
```

### 2. Implementuj Změny

```bash
# Pracuj na tvém featurů
# Psaní testů pro nový kód
# Refactoruj a zlepšuj stávající kód
```

### 3. Formátování & Linting

```bash
# Code formatting
black .

# Import sorting
isort .

# Linting check
flake8

# Pokud máš problémy:
black . --check     # Pouze check
isort . --check     # Pouze check
```

### 4. Spusť Testy

```bash
# Všechny testy
pytest

# S coverage
pytest --cov=. --cov-report=html

# Specifický test file
pytest tests/test_models.py

# Specifický test
pytest tests/test_models.py::test_user_creation

# Verbose
pytest -vv -s
```

### 5. Commit & Push

```bash
# Commit s descriptive message
git commit -m "feat: add workcommit commit tracking

- Přidej description field
- Implementuj commit logic
- Přidej API endpoint

Fixes #123"

# Push na tvůj fork
git push origin feature/amazing-feature
```

### 6. Otevři Pull Request

- Jdi na GitHub
- Otevři Pull Request vůči `main` branchi
- Vyplň PR template
- Čekej na review

---

## 📝 Commit Message Convention

Používáme [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Příklady:**

```
feat(timer): add commit tracking functionality

- Implement WorkCommit model with description
- Add start/commit/stop/resume workflow
- Include API endpoints for timer management

Closes #42

---

fix(auth): fix JWT token blacklisting on logout

Previously, refresh tokens were not properly blacklisted
when user logged out. This could allow token reuse attacks.

Fixes #15

---

docs(readme): update installation instructions

Add Windows PowerShell commands and clarify PostgreSQL setup.

---

refactor(models): extract service layer from views

Move business logic from views into dedicated service classes
for better testability and reusability.

---

style: format code with black and isort

---

chore(deps): upgrade django to 4.2 LTS
```

**Typy:**
- `feat`: Nový feature
- `fix`: Bug fix
- `docs`: Dokumentace
- `style`: Formatting (bez logických změn)
- `refactor`: Refaktoring kódu
- `perf`: Performance improvement
- `test`: Přidání/úprava testů
- `chore`: Maintenance (deps, config, atd.)

---

## 🧪 Testování

### Psaní Testů

Testy by měly pokrývat:

1. **Unit testy** – Jednotlivé funkce/metody
2. **Integration testy** – Workflow a API endpointy
3. **Edge cases** – Hraniční podmínky, chyby

### Test Structure

```python
# tests/test_models.py
import pytest
from tests.factories import UserFactory, ClientFactory

class TestClientModel:
    """Client model tests."""
    
    def test_client_creation(self):
        """Client can be created with valid data."""
        # Arrange
        user = UserFactory()
        
        # Act
        client = ClientFactory(user=user, name="Test Client")
        
        # Assert
        assert client.user == user
        assert client.name == "Test Client"
    
    def test_client_requires_name(self):
        """Client creation fails without name."""
        user = UserFactory()
        
        with pytest.raises(ValueError):
            ClientFactory(user=user, name="")
    
    @pytest.mark.integration
    def test_client_deletion_cascades(self):
        """Deleting client also deletes related projects."""
        # Arrange
        user = UserFactory()
        client = ClientFactory(user=user)
        project = ProjectFactory(client=client)
        
        # Act
        client.delete()
        
        # Assert
        assert not Project.objects.filter(id=project.id).exists()


# tests/test_api.py
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.factories import UserFactory

class TestAuthAPI:
    """Authentication API tests."""
    
    @pytest.fixture
    def api_client(self):
        """Create API client."""
        return APIClient()
    
    def test_register(self, api_client):
        """User can register."""
        # Act
        response = api_client.post('/api/auth/register/', {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password2': 'securepass123',
        })
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user']['email'] == 'newuser@example.com'
        assert 'access' in response.data
        assert 'refresh' in response.data
```

### Příkazy

```bash
# Všechny testy
pytest

# Specifická kategorie
pytest -m unit        # Pouze unit tests
pytest -m integration # Pouze integration tests

# Verbose output
pytest -vv

# Zastavit na první selhání
pytest -x

# Poslední selhání
pytest --lf

# Parallel execution
pytest -n 4

# Coverage report
pytest --cov=. --cov-report=html
# Otevři htmlcov/index.html v prohlížeči

# Bez coverage
pytest -p no:cov
```

---

## 🔒 Bezpečnostní Pravidla

### Při Psaní Kódu

- ✅ Nikdy neuchovávej hardcoded secrets
- ✅ Používej environment variables z `.env`
- ✅ Ověřuj input (validace na modelu i serializeru)
- ✅ Kontroluj permissions (IsAuthenticated, custom permissions)
- ✅ Používej ORM (nikdy surové SQL pro user input)
- ✅ Psaní CSRF-safe endpointů (POST/PUT/DELETE vyžadují token)

### Bezpečnostní Audit Before PR

```bash
# Zkontroluj, zda nemáš secrets v kódu
grep -r "SECRET_KEY\|PASSWORD\|API_KEY" --include="*.py" \
  --exclude-dir=.git --exclude-dir=venv --exclude-dir=.venv
  
# Zkontroluj, zda test data nejsou v production
grep -r "test_user\|testpass" --include="*.py" core/ users/ projects/

# Linting including security
flake8
```

---

## 🎯 Oblasti Vývoje

### Prioritní Úkoly

1. **Frontend** – Django template -> React migration
2. **Multi-user** – Workspace separation
3. **Reporting** – Invoice generation, analytics
4. **Integrations** – Stripe, Slack, atd.

### Issue Labels

- `good first issue` – Ideální pro nováčky
- `help wanted` – Potřebujeme pomoc
- `bug` – Bug report
- `enhancement` – Feature request
- `documentation` – Docs improvement
- `security` – Bezpečnostní problém
- `performance` – Performance issue

### Jak Zvolit Task

```
1. Podívej se na GitHub Issues
2. Komentuj: "Mám zájem pracovat na tomto"
3. Počkej na schválení maintainera
4. Pracuj na tom
5. Otevři PR
```

---

## 📚 Dokumentace

### Types of Documentation

1. **Code Comments** – Vysvětlování "proč", ne "co"
   ```python
   # ❌ BAD
   i = i + 1  # Increment i
   
   # ✅ GOOD
   # Move to next page for pagination
   current_page = current_page + 1
   ```

2. **Docstrings** – Google style
   ```python
   def get_user_projects(user, status=None):
       """Get all projects for a user, optionally filtered by status.
       
       Args:
           user (User): The user whose projects to retrieve
           status (str, optional): Filter by project status (new, active, done)
       
       Returns:
           QuerySet: Filtered projects
           
       Raises:
           ValueError: If status is not valid
           
       Example:
           >>> user = User.objects.get(id=1)
           >>> projects = get_user_projects(user, status='active')
       """
   ```

3. **README Updates** – Pro nové features
4. **API Documentation** – Endpointy v README

---

## 🤖 CI/CD

Projekt má:

- **GitHub Actions** – Testy, linting, coverage
- **Pre-push hooks** – Automatická kontrola (black, isort, flake8)

To spustí se na každém Push.

---

## 💬 Code Review

### Čeho se Chceme Ujistit

✅ Kód je čitelný a dobře strukturovaný  
✅ Jsou napsány testy  
✅ Dokumentace je aktuální  
✅ Bezpečnostní best practices  
✅ Performance je akceptovatelné  
✅ Žádné breaking changes bez diskuse  

### Podpora Review Feedbacku

- Jsme zde abychom pomáhali, ne kritizovat
- Pokud máš otázky, zeptej se!
- Pushbacku na constructive feedback je normální

---

## ⚡ Performance Guide

### Queries

```python
# ❌ BAD – N+1 query
for project in projects:
    print(project.client.name)  # SELECT na each iteration

# ✅ GOOD – Single query
projects = projects.select_related('client')
for project in projects:
    print(project.client.name)
```

### Pagination

```python
# ❌ BAD – Všechny records najednou
users = User.objects.all()

# ✅ GOOD – Paginated
from rest_framework.pagination import PageNumberPagination
# (Already configured in settings)
```

### Caching

```python
# ✅ GOOD – Cache expensive operations
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache 5 minut
def expensive_view(request):
    return Response(data)
```

---

## 🐛 Reporting Issues

### Security Issues

⚠️ **NIKDY** neukládej bezpečnostní bugs na GitHub!

Místo toho:
1. Pošli email: frank@example.com
2. Zahrň detaily a proof-of-concept
3. Počkej na potvrzení a řešení

### Ostatní Issues

```
## Description
Jasný popis problému

## Steps to Reproduce
1. Krok 1
2. Krok 2
3. ...

## Expected Behavior
Co by mělo být

## Actual Behavior
Co se stane

## Environment
- Python: 3.10
- Django: 6.0
- OS: Windows/Mac/Linux
```

---

## 🎓 Tipy pro Úspěch

1. **Start Small** – Začni s dokumentací nebo malými bugfixy
2. **Ask Questions** – Žádné hloupé otázky, opravdu
3. **Read the Code** – Nauč se strukturou projectu
4. **Test Locally** – Testuj změny předtím, než pushneš
5. **Keep PRs Small** – Menší == Snazší review == Rychlejší merge
6. **Be Patient** – Maintainers mají svojeJoby :)

---

## 📞 Potřebuješ Pomoc?

- 💬 [GitHub Discussions](https://github.com/yourusername/freelanceos/discussions)
- 🐛 [GitHub Issues](https://github.com/yourusername/freelanceos/issues)
- 📧 Email: frank@example.com

---

**Děkuji za přispívání! 🙏**
