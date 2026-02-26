"""
tests/ui/conftest.py
─────────────────────
UI-specific fixtures: pre-built page objects, authenticated sessions.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from config.settings import settings
from tests.ui.pages import LoginPage


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    lp = LoginPage(page)
    lp.navigate()
    return lp


@pytest.fixture
def authenticated_page(page: Page) -> Page:
    """
    Returns a page that is already logged in using configured test credentials.
    Use this fixture in tests that require authentication.
    """
    if not settings.test_username or not settings.test_password:
        pytest.skip("TEST_USERNAME / TEST_PASSWORD not configured")

    login = LoginPage(page)
    login.navigate()
    login.login_and_wait(settings.test_username, settings.test_password)
    return page
