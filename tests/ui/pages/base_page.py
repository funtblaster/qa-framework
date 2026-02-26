"""
tests/ui/pages/base_page.py
────────────────────────────
Base class for all Page Object Models.

Every page object should inherit from BasePage and:
  1. Define a URL class variable
  2. Define locators for all interactive elements
  3. Add action methods (click_submit, fill_form, etc.)
  4. Add assertion helpers (assert_heading_visible, etc.)

Usage:
    class LoginPage(BasePage):
        URL = "/login"

        def __init__(self, page):
            super().__init__(page)
            self.email_input = page.get_by_label("Email")
            self.password_input = page.get_by_label("Password")
            self.submit_btn = page.get_by_role("button", name="Log in")

        def login(self, email, password):
            self.email_input.fill(email)
            self.password_input.fill(password)
            self.submit_btn.click()
            self.wait_for_load()
"""

from __future__ import annotations

import logging
from typing import Any

from playwright.sync_api import Page, expect

from config.settings import settings

logger = logging.getLogger(__name__)


class BasePage:
    """
    Base class for Page Object Models.
    Provides common navigation, wait, and assertion helpers.
    """

    #: Relative path for this page, e.g. "/login" or "/dashboard"
    URL: str = "/"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.base_url = settings.base_url

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate(self, path: str | None = None) -> "BasePage":
        """Navigate to this page's URL (or an override path)."""
        url = f"{self.base_url}{path or self.URL}"
        logger.debug("Navigating to: %s", url)
        self.page.goto(url)
        self.wait_for_load()
        return self

    def navigate_absolute(self, url: str) -> "BasePage":
        self.page.goto(url)
        self.wait_for_load()
        return self

    def reload(self) -> "BasePage":
        self.page.reload()
        self.wait_for_load()
        return self

    def go_back(self) -> "BasePage":
        self.page.go_back()
        self.wait_for_load()
        return self

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_load(self, state: str = "domcontentloaded") -> "BasePage":
        """Wait for the page network to become idle after navigation."""
        self.page.wait_for_load_state(state)
        return self

    def wait_for_url(self, url_fragment: str, timeout: int = 10_000) -> "BasePage":
        self.page.wait_for_url(f"**{url_fragment}**", timeout=timeout)
        return self

    def wait_for_selector(self, selector: str, timeout: int = 10_000) -> Any:
        return self.page.wait_for_selector(selector, timeout=timeout)

    def wait_for_text(self, text: str, timeout: int = 10_000) -> None:
        self.page.get_by_text(text).wait_for(timeout=timeout)

    # ── State Helpers ─────────────────────────────────────────────────────────

    @property
    def current_url(self) -> str:
        return self.page.url

    @property
    def title(self) -> str:
        return self.page.title()

    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).inner_text()

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).is_visible()

    def scroll_to_bottom(self) -> None:
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # ── Assertions ────────────────────────────────────────────────────────────

    def assert_url_contains(self, fragment: str) -> None:
        assert fragment in self.current_url, (
            f"Expected URL to contain '{fragment}', got '{self.current_url}'"
        )

    def assert_title_contains(self, text: str) -> None:
        assert text.lower() in self.title.lower(), (
            f"Expected title to contain '{text}', got '{self.title}'"
        )

    def assert_visible(self, selector: str) -> None:
        expect(self.page.locator(selector)).to_be_visible()

    def assert_text_visible(self, text: str) -> None:
        expect(self.page.get_by_text(text, exact=False)).to_be_visible()

    def assert_not_visible(self, selector: str) -> None:
        expect(self.page.locator(selector)).not_to_be_visible()

    def assert_input_value(self, selector: str, expected: str) -> None:
        expect(self.page.locator(selector)).to_have_value(expected)

    def take_screenshot(self, name: str = "screenshot") -> bytes:
        return self.page.screenshot(full_page=True)
