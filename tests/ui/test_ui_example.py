"""
tests/ui/test_ui_example.py
────────────────────────────
Example UI tests demonstrating framework usage.
Replace with tests tailored to your application.

Run with:
    pytest tests/ui/ -v
    pytest -m ui -v
    pytest -m smoke -v
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from config.settings import settings
from tests.ui.pages import LoginPage
from utils.assertions import assert_url_contains


# ─────────────────────────────────────────────────────────────────────────────
# Smoke Tests — run on every commit
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.p0
class TestHomePage:
    """Basic smoke checks that the site is up and reachable."""

    def test_homepage_loads(self, page: Page, base_url: str):
        """The homepage should return a 200 and display the page title."""
        response = page.goto(base_url)
        assert response is not None, "No response received"
        assert response.status == 200, f"Expected 200, got {response.status}"
        assert page.title() != "", "Page title is empty"

    def test_homepage_has_no_console_errors(self, page: Page, base_url: str):
        """No critical JavaScript errors should appear on the homepage."""
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        assert not errors, f"Console errors found: {errors}"

    def test_page_does_not_have_broken_links(self, page: Page, base_url: str):
        """
        Check all same-domain links on the homepage return 2xx.
        Skips external links and anchor links.
        """
        page.goto(base_url)
        links = page.eval_on_selector_all(
            "a[href]",
            "els => els.map(e => e.href).filter(h => h && !h.startsWith('#'))"
        )

        broken = []
        for link in links[:20]:  # limit to first 20 for speed
            if base_url in link or link.startswith("/"):
                resp = page.request.get(link)
                if not (200 <= resp.status < 400):
                    broken.append((link, resp.status))

        assert not broken, f"Broken links found: {broken}"


# ─────────────────────────────────────────────────────────────────────────────
# Auth Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.ui
@pytest.mark.p0
class TestAuthentication:
    """Login / logout flows."""

    def test_login_page_renders(self, login_page: LoginPage):
        """Login form should be visible and accessible."""
        login_page.assert_login_form_visible()

    def test_login_with_invalid_credentials(self, login_page: LoginPage):
        """Invalid credentials should show an error message, not log in."""
        login_page.login("nonexistent@example.com", "wrong_password_123")
        login_page.assert_error_visible()
        # Should stay on the login page
        assert "/login" in login_page.current_url or "/" == login_page.current_url

    @pytest.mark.skipif(
        not settings.test_username,
        reason="TEST_USERNAME not configured"
    )
    def test_login_with_valid_credentials(self, login_page: LoginPage):
        """Valid credentials should redirect away from the login page."""
        login_page.login(settings.test_username, settings.test_password)
        login_page.page.wait_for_load_state("networkidle")
        assert "/login" not in login_page.current_url, (
            "Still on login page after valid credentials — check TEST_USERNAME/PASSWORD"
        )

    def test_login_empty_form_submission(self, login_page: LoginPage):
        """Submitting empty form should show validation errors."""
        login_page.submit_button.click()
        # Should either show HTML5 validation or a custom error
        # Adjust assertion based on your app's behaviour
        assert "/login" in login_page.current_url or login_page.is_visible("[role=alert]")


# ─────────────────────────────────────────────────────────────────────────────
# Navigation & Routing Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.ui
@pytest.mark.p1
class TestNavigation:
    """Basic navigation and routing checks."""

    def test_404_page_renders(self, page: Page, base_url: str):
        """Non-existent routes should render a 404 page, not a blank screen."""
        page.goto(f"{base_url}/this-page-definitely-does-not-exist-xyz-123")
        page.wait_for_load_state("domcontentloaded")
        # Either HTTP 404 or the app renders a custom 404 — check content
        body = page.locator("body").inner_text()
        assert len(body.strip()) > 0, "404 page has no content"

    def test_back_forward_navigation(self, page: Page, base_url: str):
        """Browser back/forward should work correctly."""
        page.goto(base_url)
        initial_url = page.url

        # Navigate to a second page if possible
        first_link = page.locator("a[href]").first
        if first_link.count() > 0:
            first_link.click()
            page.wait_for_load_state("domcontentloaded")
            page.go_back()
            page.wait_for_load_state("domcontentloaded")
            assert page.url == initial_url


# ─────────────────────────────────────────────────────────────────────────────
# Accessibility Checks
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.ui
@pytest.mark.p2
class TestAccessibility:
    """Basic accessibility checks."""

    def test_images_have_alt_text(self, page: Page, base_url: str):
        """All images should have alt attributes."""
        page.goto(base_url)
        images_without_alt = page.eval_on_selector_all(
            "img:not([alt])",
            "els => els.map(e => e.src)"
        )
        assert not images_without_alt, (
            f"Images missing alt text: {images_without_alt}"
        )

    def test_page_has_main_landmark(self, page: Page, base_url: str):
        """Page should have a <main> landmark for screen readers."""
        page.goto(base_url)
        main = page.locator("main, [role=main]")
        assert main.count() >= 1, "Page is missing a <main> landmark"

    def test_form_inputs_have_labels(self, login_page: LoginPage):
        """All form inputs should have associated labels."""
        unlabelled = login_page.page.eval_on_selector_all(
            "input:not([type=hidden]):not([type=submit]):not([type=button])",
            """els => els.filter(el => {
                const id = el.id;
                const label = id ? document.querySelector('label[for="' + id + '"]') : null;
                const ariaLabel = el.getAttribute('aria-label');
                const ariaLabelledBy = el.getAttribute('aria-labelledby');
                return !label && !ariaLabel && !ariaLabelledBy;
            }).map(e => e.outerHTML.slice(0, 80))"""
        )
        assert not unlabelled, (
            f"Form inputs without labels: {unlabelled}"
        )
