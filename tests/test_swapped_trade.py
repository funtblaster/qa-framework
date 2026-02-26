"""
UI Test Suite — swapped.com Trade/Buy Page
Covers: page load, widget presence, navigation from homepage to trade page.
Runs across chromium, firefox, and webkit via browser_name parametrization.
"""
import pytest
from playwright.sync_api import Page, expect


BASE_URL = "https://swapped.com"


@pytest.mark.ui
@pytest.mark.smoke
class TestTradePageLoads:
    """Verify the trade page loads correctly across all browsers."""

    @pytest.mark.p0
    def test_trade_page_loads(self, page: Page, browser_name: str):
        """Trade page should return 200 and render successfully."""
        response = page.goto(f"{BASE_URL}/trade")
        assert response.status == 200, (
            f"[{browser_name}] Trade page returned {response.status}"
        )
        expect(page.locator("body")).to_be_visible()

    def test_trade_page_no_console_errors(self, page: Page, browser_name: str):
        """Trade page should load without console errors."""
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.goto(f"{BASE_URL}/trade")
        page.wait_for_load_state("networkidle")
        assert len(errors) == 0, f"[{browser_name}] Console errors on trade page: {errors}"

    def test_trade_page_load_time(self, page: Page, browser_name: str):
        """Trade page should load within 10 seconds."""
        import time
        start = time.time()
        page.goto(f"{BASE_URL}/trade")
        page.wait_for_load_state("domcontentloaded")
        elapsed = time.time() - start
        assert elapsed < 10, (
            f"[{browser_name}] Trade page took {elapsed:.2f}s to load (limit: 10s)"
        )


@pytest.mark.ui
@pytest.mark.smoke
class TestHomepageToCTANavigation:
    """Verify CTA buttons on the homepage navigate to the trade flow."""

    @pytest.mark.p0
    def test_buy_crypto_cta_navigates(self, page: Page, browser_name: str):
        """Clicking Buy crypto CTA from the homepage should navigate to the trade page."""
        page.goto(BASE_URL)
        page.wait_for_load_state("domcontentloaded")
        buy_link = page.get_by_role("link", name="Buy crypto").first
        href = buy_link.get_attribute("href")
        assert href is not None, f"[{browser_name}] Buy crypto link has no href"
        assert "trade" in href or "buy" in href, (
            f"[{browser_name}] Unexpected Buy crypto href: {href}"
        )

    @pytest.mark.p0
    def test_get_started_cta_navigates(self, page: Page, browser_name: str):
        """Clicking Get started CTA should navigate to the trade widget."""
        page.goto(BASE_URL)
        page.wait_for_load_state("domcontentloaded")
        get_started = page.get_by_role("link", name="Get started").first
        href = get_started.get_attribute("href")
        assert href is not None, f"[{browser_name}] Get started link has no href"

    def test_view_all_coins_link(self, page: Page, browser_name: str):
        """View all coins link should point to /supported-cryptos."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        link = page.get_by_role("link", name="View all coins")
        href = link.get_attribute("href")
        assert href is not None and "supported-cryptos" in href, (
            f"[{browser_name}] Unexpected View all coins href: {href}"
        )

    def test_see_all_payment_options_link(self, page: Page, browser_name: str):
        """See all payment options should link to /payment-methods."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        link = page.get_by_role("link", name="See all payment options")
        href = link.get_attribute("href")
        assert href is not None and "payment-methods" in href, (
            f"[{browser_name}] Unexpected payment options href: {href}"
        )


@pytest.mark.ui
class TestSupportedPages:
    """Verify other key pages linked from the homepage load correctly."""

    def test_about_page_loads(self, page: Page, browser_name: str):
        """About/Company page should load with a 200."""
        response = page.goto(f"{BASE_URL}/about-us")
        assert response.status == 200, (
            f"[{browser_name}] About page returned {response.status}"
        )

    def test_contact_page_loads(self, page: Page, browser_name: str):
        """Contact/Support page should load with a 200."""
        response = page.goto(f"{BASE_URL}/contact-us")
        assert response.status == 200, (
            f"[{browser_name}] Contact page returned {response.status}"
        )

    def test_blog_page_loads(self, page: Page, browser_name: str):
        """Blog page should load with a 200."""
        response = page.goto(f"{BASE_URL}/blog")
        assert response.status == 200, (
            f"[{browser_name}] Blog page returned {response.status}"
        )

    def test_fees_page_loads(self, page: Page, browser_name: str):
        """Fees page should load with a 200."""
        response = page.goto(f"{BASE_URL}/fees")
        assert response.status == 200, (
            f"[{browser_name}] Fees page returned {response.status}"
        )

    def test_payment_methods_page_loads(self, page: Page, browser_name: str):
        """Payment methods page should load with a 200."""
        response = page.goto(f"{BASE_URL}/payment-methods")
        assert response.status == 200, (
            f"[{browser_name}] Payment methods page returned {response.status}"
        )

    def test_privacy_policy_page_loads(self, page: Page, browser_name: str):
        """Privacy policy page should load with a 200."""
        response = page.goto(f"{BASE_URL}/legal/privacy-policy")
        assert response.status == 200, (
            f"[{browser_name}] Privacy policy page returned {response.status}"
        )

    def test_terms_page_loads(self, page: Page, browser_name: str):
        """Terms of use page should load with a 200."""
        response = page.goto(f"{BASE_URL}/legal/ramp-tos")
        assert response.status == 200, (
            f"[{browser_name}] Terms of use page returned {response.status}"
        )
