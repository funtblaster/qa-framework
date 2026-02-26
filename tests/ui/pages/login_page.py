"""
tests/ui/pages/login_page.py
─────────────────────────────
Example Page Object for a login page.
Replace selectors with those matching your actual application.

To add more pages:
    1. Create a new file in tests/ui/pages/
    2. Inherit from BasePage
    3. Define URL, locators, and action methods
    4. Import and use in your test files
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from .base_page import BasePage


class LoginPage(BasePage):
    URL = "/login"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        # ── Locators ──────────────────────────────────────────────────────────
        # Using accessible role/label selectors is preferred over CSS/XPath.
        # These are generic defaults — update to match your app.

        self.email_input = page.get_by_label("Email")
        self.password_input = page.get_by_label("Password")
        self.submit_button = page.get_by_role("button", name="Log in")
        self.error_message = page.get_by_role("alert")
        self.forgot_password_link = page.get_by_role("link", name="Forgot password")

    # ── Actions ───────────────────────────────────────────────────────────────

    def login(self, email: str, password: str) -> None:
        """Fill credentials and submit the login form."""
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.submit_button.click()

    def login_and_wait(self, email: str, password: str, redirect_fragment: str = "/") -> None:
        """Login and wait for redirect to the expected post-login URL."""
        self.login(email, password)
        self.wait_for_url(redirect_fragment)

    def get_error_text(self) -> str:
        return self.error_message.inner_text()

    # ── Assertions ────────────────────────────────────────────────────────────

    def assert_error_visible(self, message: str | None = None) -> None:
        expect(self.error_message).to_be_visible()
        if message:
            expect(self.error_message).to_contain_text(message)

    def assert_login_form_visible(self) -> None:
        expect(self.email_input).to_be_visible()
        expect(self.password_input).to_be_visible()
        expect(self.submit_button).to_be_visible()
