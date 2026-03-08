# Testing Guide for FreelanceOS

This document describes how to run tests, measure coverage, execute E2E tests, and perform code quality checks for the FreelanceOS project.

> **Note**: All commands should be run from the project root directory after activating the Python virtual environment.

---

## Quick Start

### 1. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### 2. Run All Tests

```bash
# Using pytest (recommended)
pytest

# Or using Django test runner
python manage.py test

# With coverage
python manage.py test users --verbosity=2
```

### 3. Check Code Quality

```bash
# Linting with flake8
flake8 .

# Import sorting with isort
isort . --profile=black --check-only

# Format with black (optional)
black .
```

### 4. E2E Tests (Playwright)

```bash
# Start Django server first
python manage.py runserver

# In another terminal, run E2E tests
python -m pytest e2e/test_auth_flow.py -v
```

---

## Detailed Commands

### Coverage Measurement

Generate coverage reports for the `users` application:

**Windows:**
```batch
scripts\run_coverage.bat
```

**Linux/macOS:**
```bash
bash scripts/run_coverage.sh
```

**Manual:**
```bash
coverage run --source='.' manage.py test users
coverage report -m
coverage html  # Generates htmlcov/index.html
```

**Output:**
- `coverage_report.txt` - Text report with line-by-line coverage
- `htmlcov/index.html` - Interactive HTML coverage report

**Current Status:** ✅ **99% coverage** on users app

---

### Edge-Case API Tests

Comprehensive tests for edge cases, security, and race conditions:

```bash
# Run edge-case tests
python manage.py test users.tests_edgecases

# Run with verbose output
python manage.py test users.tests_edgecases -v 2

# Run specific test class
python manage.py test users.tests_edgecases.EdgeCaseInputTests

# Run specific test method
python manage.py test users.tests_edgecases.EdgeCaseInputTests.test_extremely_long_email
```

**Test Categories:**

1. **Race Conditions** (`RaceConditionTests`)
   - Concurrent registration with same email
   - Database consistency checks
   - Tests: 2

2. **Token Expiration** (`RefreshTokenExpirationTests`)
   - Expired token handling
   - Token lifecycle
   - Tests: 3

3. **Token Blacklisting** (`TokenBlacklistTests`)
   - Double logout prevention
   - Token invalidation
   - Tests: 2

4. **Edge Case Inputs** (`EdgeCaseInputTests`)
   - Extremely long emails
   - Special characters in email
   - Password validation
   - Missing required fields
   - Tests: 5

5. **Login Edge Cases** (`LoginEdgeCaseTests`)
   - Wrong password handling
   - Nonexistent user handling
   - Inactive user login
   - Case-insensitive email
   - Tests: 4

**Total:** 16 edge-case tests (all passing ✅)

---

### End-to-End (E2E) UI Tests

Playwright-based tests for complete UI workflows:

**Windows:**
```batch
scripts\run_e2e.bat
```

**Linux/macOS:**
```bash
bash scripts/run_e2e.sh
```

**Manual (headless):**
```bash
# Start Django dev server
python manage.py runserver &

# Run E2E tests
python -m pytest e2e/test_auth_flow.py -v --tb=short

# With headed browser (see what happens)
HEADED=true python -m pytest e2e/test_auth_flow.py -v
```

**Test Scenarios:**

1. **Registration Flow** - Sign up form → successful registration → redirect
2. **Login Flow** - Login form → dashboard access → user info display
3. **Logout Flow** - Logout button → session invalidation → redirect to public page
4. **Invalid Credentials** - Wrong email/password → error display
5. **Responsive Design** - Mobile viewport → form accessibility

**Output:**
- `e2e_report.txt` - Test execution report
- Browser console for debugging (in headed mode)

**Requirements:**
- Django development server running on http://localhost:8000
- Playwright browsers installed (auto-install on first run)
- Base URL configurable via `BASE_URL` environment variable

---

### Code Quality & Linting

#### Flake8 (Style & Errors)

```bash
# Check all files
flake8 .

# Check specific file
flake8 core/views.py

# Ignore specific errors
flake8 . --ignore=E501,W503
```

**Output:** `lint_report.txt`

**Common Issues:**
- `W293` - Blank line contains whitespace
- `E302` - Expected 2 blank lines
- `E501` - Line too long
- `F401` - Unused import

#### isort (Import Formatting)

```bash
# Check import order
isort . --profile=black --check-only

# Fix import order automatically
isort . --profile=black
```

**Configuration:** Uses Black profile with 100-char line length

#### Black (Code Formatting - Optional)

```bash
# Format all Python files
black .

# Check without modifying
black . --check
```

**Windows Script:**
```batch
scripts\run_lints.bat
```

**Linux/macOS Script:**
```bash
bash scripts/run_lints.sh
```

---

## Test Database

Tests use a separate test database to avoid affecting production data.

```bash
# Preserve test database between runs (faster)
python manage.py test --keepdb

# Rebuild test database each time
python manage.py test  # (default)

# Delete test database
python manage.py test --no-input --verbosity=0 && echo "Test DB cleaned"
```

---

## Debugging Failed Tests

### Verbose Output

```bash
python manage.py test users -v 2  # Level 2 verbosity

python manage.py test users -v 3  # Level 3 (very detailed)
```

### Run Single Test Class

```bash
python manage.py test users.tests_edgecases.EdgeCaseInputTests
```

### Run Single Test Method

```bash
python manage.py test users.tests_edgecases.EdgeCaseInputTests.test_password_mismatch
```

### E2E Debugging

Enable headed mode to see browser:
```bash
python -m pytest e2e/test_auth_flow.py -v -s  # -s for stdout

# In Windows:
set HEADLESS=false && python -m pytest e2e/test_auth_flow.py -v
```

Add breakpoints in tests:
```python
browser.pause()  # Playwright will pause execution
```

---

## Continuous Testing

### Watch Mode (Auto-rerun on file changes)

```bash
# Install pytest-watch
pip install pytest-watch

# Run in watch mode
ptw -- users/

# With coverage
ptw -- --cov=users users/
```

### Coverage Threshold

Add to your CI/CD to enforce minimum coverage:
```bash
coverage report --fail-under=85
```

---

## Reports Location

| Report | Location | Format | Purpose |
|--------|----------|--------|---------|
| Coverage Report | `coverage_report.txt` | Text | Line-by-line coverage metrics |
| HTML Coverage | `htmlcov/index.html` | HTML | Interactive coverage visualization |
| Lint Report | `lint_report.txt` | Text | Linting issues and warnings |
| E2E Report | `e2e_report.txt` | Text | E2E test execution results |
| Test Database | `.test_freelanceos` | PostgreSQL | Temporary test database |

---

## Environment Variables

```bash
# E2E Tests
BASE_URL=http://localhost:8000    # Django server URL
HEADLESS=true                      # Run browser headless (default)
HEADLESS=false                     # Show browser during E2E tests

# Coverage
DJANGO_SETTINGS_MODULE=core.settings

# Logging
PYTHONLOGGING=DEBUG
```

---

## Troubleshooting

### Test Database Connection Error

```
Error: got an unexpected keyword argument 'init_command'
```

**Solution:** Update your `settings.py` PostgreSQL configuration if using an older version.

### Playwright Browser Not Found

```bash
# Install Playwright browsers
playwright install

# Or auto-install on first run
python -m pytest e2e/test_auth_flow.py
```

### Flake8 Config Not Working

Ensure `.flake8` is in the project root:
```bash
flake8 . --config=.flake8
```

### isort Import Order Issues

```bash
# View what isort would change
isort . --profile=black --diff

# Apply changes
isort . --profile=black
```

---

## Best Practices

✅ **Do:**
- Run tests before committing code
- Keep test database clean with `--keepdb`
- Review coverage reports regularly
- Run linting on modified files
- Use meaningful test names

❌ **Don't:**
- Modify production settings for tests
- Hardcode test data in fixtures
- Ignore failing tests
- Skip edge-case testing
- Leave whitespace in code

---

## CI/CD Integration

For automated testing in CI/CD pipelines (GitHub Actions, GitLab CI, etc.):

```yaml
# Example: GitHub Actions
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Run tests
        run: python manage.py test users --keepdb
      - name: Check coverage
        run: coverage run --source='.' manage.py test users && coverage report --fail-under=85
      - name: Run lints
        run: flake8 . && isort . --check-only
```

---

## Additional Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Playwright Documentation](https://playwright.dev/python/)
- [flake8 Documentation](https://flake8.pycqa.org/)

---

**Last Updated:** March 8, 2026  
**Project:** FreelanceOS  
**Python Version:** 3.12+  
**Django Version:** 6.0+
