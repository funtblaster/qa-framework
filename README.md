# QA Automation Framework

A generic, production-ready Python test automation framework built with **Pytest**, **Playwright**, and **httpx**. Designed to work with any website or web API.

---

## 📁 Project Structure

```
qa_framework/
├── config/
│   ├── settings.py          # Environment config & base URLs
│   └── environments/
│       ├── local.env
│       ├── staging.env
│       └── production.env
├── tests/
│   ├── conftest.py          # Global fixtures
│   ├── api/
│   │   ├── conftest.py      # API-specific fixtures
│   │   └── test_api_example.py
│   ├── ui/
│   │   ├── conftest.py      # Browser/page fixtures
│   │   ├── pages/           # Page Object Models
│   │   │   ├── base_page.py
│   │   │   └── example_page.py
│   │   └── test_ui_example.py
│   └── integration/
│       └── test_integration_example.py
├── utils/
│   ├── api_client.py        # Reusable HTTP client wrapper
│   ├── data_factory.py      # Test data generation
│   ├── assertions.py        # Custom assertion helpers
│   └── retry.py             # Retry / flakiness helpers
├── reports/                 # Allure output directory
├── .github/
│   └── workflows/
│       ├── pr_gate.yml      # Fast PR check (<5 min)
│       └── nightly.yml      # Full regression suite
├── pytest.ini               # Pytest configuration
├── pyproject.toml           # Dependencies & tooling config
└── Makefile                 # Common dev commands
```

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
# Using pip
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium
```

### 2. Configure your environment

```bash
cp config/environments/local.env .env
# Edit .env with your target website's base URL and credentials
```

### 3. Run tests

```bash
# All tests
make test

# UI tests only
make test-ui

# API tests only
make test-api

# With Allure report
make test-report
```

---

## ⚙️ Configuration

Set the following in your `.env` file (or as environment variables):

| Variable          | Description                        | Default                  |
|-------------------|------------------------------------|--------------------------|
| `BASE_URL`        | Target website base URL            | `http://localhost:3000`  |
| `API_BASE_URL`    | API base URL                       | `http://localhost:3000`  |
| `TEST_ENV`        | Environment name                   | `local`                  |
| `HEADLESS`        | Run browser headless               | `true`                   |
| `SLOW_MO`         | Playwright slow-mo (ms)            | `0`                      |
| `BROWSER`         | Browser: chromium / firefox / webkit | `chromium`             |
| `TEST_USERNAME`   | Login username for test account    | —                        |
| `TEST_PASSWORD`   | Login password for test account    | —                        |
| `API_TOKEN`       | Bearer token for API auth          | —                        |
| `REQUEST_TIMEOUT` | HTTP request timeout (seconds)     | `30`                     |

---

## 🏷️ Test Markers

Tests are tagged with pytest markers for selective execution:

```bash
pytest -m smoke          # Fast sanity checks
pytest -m regression     # Full regression suite
pytest -m p0             # Critical path tests
pytest -m p1             # High priority
pytest -m p2             # Medium priority
pytest -m api            # API tests only
pytest -m ui             # UI tests only
pytest -m slow           # Tests that take >10s
```

---

## 📊 Reporting

Allure reports are generated automatically:

```bash
make test-report         # Run tests + open Allure report
```

---

## 🔁 CI/CD

- **PR Gate** (`.github/workflows/pr_gate.yml`): Runs `smoke` + `p0` tests on every pull request. Target: under 5 minutes.
- **Nightly** (`.github/workflows/nightly.yml`): Runs the full regression suite. Publishes Allure report as a GitHub Pages artefact.

---

## 🧩 Extending the Framework

### Add a new Page Object

```python
# tests/ui/pages/my_page.py
from .base_page import BasePage

class MyPage(BasePage):
    URL = "/my-page"

    def __init__(self, page):
        super().__init__(page)
        self.heading = page.locator("h1")
        self.submit_btn = page.get_by_role("button", name="Submit")

    def submit(self):
        self.submit_btn.click()
        self.wait_for_load()
```

### Add a new API test

```python
# tests/api/test_my_endpoint.py
import pytest
from utils.assertions import assert_status, assert_schema

@pytest.mark.api
@pytest.mark.p1
def test_my_endpoint(api_client):
    response = api_client.get("/api/my-endpoint")
    assert_status(response, 200)
    assert response.json()["key"] == "expected_value"
```
