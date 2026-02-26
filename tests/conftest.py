"""
tests/conftest.py
──────────────────
Global fixtures available to every test in the suite.

Fixture scopes:
  session  – created once per pytest session (e.g. browser launch)
  module   – created once per test module
  function – created and torn down for each test (default)

Add domain-specific fixtures in the relevant conftest.py:
  tests/api/conftest.py        → API auth fixtures
  tests/ui/conftest.py         → Browser page fixtures
  tests/integration/conftest.py
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Generator

import allure
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from config.settings import settings
from utils.api_client import ApiClient

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") else logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

# ── Directories ───────────────────────────────────────────────────────────────
REPORTS_DIR = Path(__file__).parent.parent / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
TRACES_DIR = REPORTS_DIR / "traces"
VIDEOS_DIR = REPORTS_DIR / "videos"

for d in [SCREENSHOTS_DIR, TRACES_DIR, VIDEOS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Pytest hooks
# ─────────────────────────────────────────────────────────────────────────────

def pytest_configure(config):
    """Register custom markers (also listed in pytest.ini)."""
    for marker in [
        "smoke: Fast sanity checks",
        "regression: Full regression suite",
        "p0: Critical path",
        "p1: High priority",
        "p2: Medium priority",
        "api: API tests",
        "ui: UI tests",
        "integration: Integration tests",
        "slow: Slow tests",
        "flaky: Quarantined flaky tests",
    ]:
        config.addinivalue_line("markers", marker)


def pytest_runtest_makereport(item, call):
    """Attach screenshot / trace to Allure report on UI test failure."""
    if call.when == "call" and call.excinfo:
        page: Page | None = item.funcargs.get("page")
        if page and settings.screenshot_on_failure:
            screenshot_path = SCREENSHOTS_DIR / f"{item.nodeid.replace('/', '_').replace('::', '_')}.png"
            try:
                page.screenshot(path=str(screenshot_path), full_page=True)
                allure.attach.file(
                    str(screenshot_path),
                    name="screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception as exc:
                logger.warning("Could not capture screenshot: %s", exc)


# ─────────────────────────────────────────────────────────────────────────────
# API Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def api_client() -> Generator[ApiClient, None, None]:
    """
    Session-scoped API client.
    Reused across all tests — do NOT mutate auth state unless you restore it.
    """
    with ApiClient() as client:
        yield client


@pytest.fixture
def fresh_api_client() -> Generator[ApiClient, None, None]:
    """
    Function-scoped API client with a clean auth state.
    Use this when a test needs to authenticate as a specific user.
    """
    with ApiClient() as client:
        yield client


# ─────────────────────────────────────────────────────────────────────────────
# Browser / Playwright Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Generator[Browser, None, None]:
    """Session-scoped browser instance. Shared across all UI tests."""
    browser_type = getattr(playwright_instance, settings.browser.value)
    b = browser_type.launch(
        headless=settings.headless,
        slow_mo=settings.slow_mo,
    )
    yield b
    b.close()


@pytest.fixture
def browser_context(browser: Browser, tmp_path) -> Generator[BrowserContext, None, None]:
    """
    Function-scoped browser context — each test gets a clean session
    (no shared cookies, local storage, etc.).
    """
    context_options: dict = {
        "viewport": {
            "width": settings.viewport_width,
            "height": settings.viewport_height,
        },
        "record_video_dir": str(VIDEOS_DIR) if settings.video_on_failure else None,
    }

    if settings.trace_on_failure:
        ctx = browser.new_context(**{k: v for k, v in context_options.items() if v is not None})
        ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
    else:
        ctx = browser.new_context(**{k: v for k, v in context_options.items() if v is not None})

    yield ctx

    if settings.trace_on_failure:
        trace_path = TRACES_DIR / f"{id(ctx)}.zip"
        ctx.tracing.stop(path=str(trace_path))

    ctx.close()


@pytest.fixture
def page(browser_context: BrowserContext) -> Generator[Page, None, None]:
    """Function-scoped Playwright Page. The most commonly used UI fixture."""
    p = browser_context.new_page()
    p.set_default_timeout(15_000)   # 15 second default element timeout
    p.set_default_navigation_timeout(30_000)
    yield p
    p.close()


# ─────────────────────────────────────────────────────────────────────────────
# Utility Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def base_url() -> str:
    return settings.base_url


@pytest.fixture(scope="session")
def api_base_url() -> str:
    return settings.api_base_url
