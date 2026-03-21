# Testování FreelanceOS

## Quick Start

```bash
pip install -r requirements-dev.txt
pytest
```

## Příkazy

```bash
pytest                          # Všechny testy
pytest -vv -s                   # Verbose s print výstupem
pytest -m unit                  # Jen unit testy
pytest -m integration           # Jen API testy
pytest -x                       # Stop na prvním failure
pytest --lf                     # Jen poslední failed
pytest -n 4                     # Paralelní běh (4 jádra)
pytest --cov --cov-report=html  # Coverage HTML report
```

## Co se testuje

| Úroveň | Co | Příklad |
|---------|-----|---------|
| **Unit** | Modely, serializéry | Validace polí, model metody |
| **Integration** | API endpointy | CRUD operace, filtry, permissions |
| **Edge cases** | Hraniční stavy | Duplicity, prázdné hodnoty, neplatná data |
| **E2E** | Browser flow | Registrace → login → dashboard (Playwright) |

## Struktura testů

```
tests/
├── conftest.py     # Globální fixtures (user, client, project, auth_client)
├── factories.py    # UserFactory, ClientFactory, ProjectFactory, WorkCommitFactory
└── utils.py        # Helpery (create_authenticated_client, assert_error_response)

{app}/tests/
├── conftest.py         # App-specifické fixtures
├── test_models.py      # Unit testy modelů
├── test_serializers.py # Unit testy serializérů
└── test_api.py         # Integration testy API
```

## Markers

```ini
# pytest.ini
@pytest.mark.unit           # Modely, serializéry
@pytest.mark.integration    # API endpointy
@pytest.mark.edge_cases     # Hraniční podmínky
@pytest.mark.slow           # Pomalé testy (>1s)
```

## E2E testy

```bash
# Vyžaduje běžící Django server
python manage.py runserver &
python -m pytest e2e/ -v
```
