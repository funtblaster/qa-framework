.PHONY: install test test-ui test-api test-integration test-smoke test-p0 \
        test-report test-parallel lint format typecheck clean

# ─── Setup ────────────────────────────────────────────────────────────────────
install:
	pip install -e ".[dev]"
	playwright install chromium

# ─── Test Suites ──────────────────────────────────────────────────────────────
test:
	pytest

test-ui:
	pytest -m ui

test-api:
	pytest -m api

test-integration:
	pytest -m integration

test-smoke:
	pytest -m smoke

test-p0:
	pytest -m p0

# PR gate: smoke + p0 tests, parallel, fast
test-pr:
	pytest -m "smoke or p0" -n auto --timeout=300

# Full nightly: all tests, parallel
test-nightly:
	pytest -n auto

# ─── Reporting ────────────────────────────────────────────────────────────────
test-report: test
	allure serve reports/allure-results

# ─── Code Quality ─────────────────────────────────────────────────────────────
lint:
	ruff check .

format:
	black .
	ruff check --fix .

typecheck:
	mypy .

# ─── Cleanup ──────────────────────────────────────────────────────────────────
clean:
	rm -rf reports/allure-results reports/coverage .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
