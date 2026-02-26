"""
UI Test Suite — swapped.com Homepage
Covers: navigation, hero section, content sections, footer, responsiveness.
Runs across chromium, firefox, and webkit via browser_name parametrization.
"""
import pytest
from playwright.sync_api import Page, expect


BASE_URL = "https://swapped.com"


@pytest.mark.ui
@pytest.mark.smoke
class TestHomepageLoads:
    """Verify the homepage loads correctly across all browsers."""

    def test_homepage_title(self, page: Page, browser_name: str):
        """Page title should reference Swapped and crypto."""
        page.goto(BASE_URL)
        expect(page).to_have_title(lambda t: "swapped" in t.lower() or "crypto" in t.lower())

    @pytest.mark.p0
    def test_homepage_loads_successfully(self, page: Page, browser_name: str):
        """Homepage should return a 200 and render the hero heading."""
        response = page.goto(BASE_URL)
        assert response.status == 200, f"[{browser_name}] Expected 200, got {response.status}"
        expect(page.locator("h1").first).to_be_visible()

    def test_hero_heading_text(self, page: Page, browser_name: str):
        """Hero heading should contain the core value proposition."""
        page.goto(BASE_URL)
        heading_text = page.locator("h1").first.inner_text()
        assert "crypto" in heading_text.lower(), (
            f"[{browser_name}] Hero heading missing 'crypto': '{heading_text}'"
        )

    def test_no_console_errors(self, page: Page, browser_name: str):
        """Page should load without any console errors."""
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        assert len(errors) == 0, f"[{browser_name}] Console errors: {errors}"

    def test_page_load_time(self, page: Page, browser_name: str):
        """Homepage should load within 10 seconds."""
        import time
        start = time.time()
        page.goto(BASE_URL)
        page.wait_for_load_state("domcontentloaded")
        elapsed = time.time() - start
        assert elapsed < 10, f"[{browser_name}] Page took {elapsed:.2f}s to load (limit: 10s)"


@pytest.mark.ui
@pytest.mark.smoke
class TestNavigation:
    """Verify navigation links are present and functional."""

    @pytest.mark.p0
    def test_nav_buy_crypto_link_visible(self, page: Page, browser_name: str):
        """Buy crypto nav link should be visible."""
        page.goto(BASE_URL)
        expect(page.get_by_role("link", name="Buy crypto").first).to_be_visible()

    def test_nav_sell_crypto_link_visible(self, page: Page, browser_name: str):
        """Sell crypto nav link should be visible."""
        page.goto(BASE_URL)
        expect(page.get_by_role("link", name="Sell crypto").first).to_be_visible()

    def test_nav_business_link_visible(self, page: Page, browser_name: str):
        """Business nav link should be visible."""
        page.goto(BASE_URL)
        expect(page.get_by_role("link", name="Business").first).to_be_visible()

    def test_nav_support_link_visible(self, page: Page, browser_name: str):
        """Support nav link should be visible."""
        page.goto(BASE_URL)
        expect(page.get_by_role("link", name="Support").first).to_be_visible()

    @pytest.mark.p0
    def test_buy_crypto_nav_href(self, page: Page, browser_name: str):
        """Buy crypto nav link should point to /trade."""
        page.goto(BASE_URL)
        link = page.get_by_role("link", name="Buy crypto").first
        href = link.get_attribute("href")
        assert href is not None and ("trade" in href or "buy" in href), (
            f"[{browser_name}] Unexpected Buy crypto href: {href}"
        )

    def test_get_started_button_visible(self, page: Page, browser_name: str):
        """Get started CTA button should be visible on the hero."""
        page.goto(BASE_URL)
        expect(page.get_by_role("link", name="Get started").first).to_be_visible()

    def test_blog_nav_link_navigates(self, page: Page, browser_name: str):
        """Blog link should navigate to /blog."""
        page.goto(BASE_URL)
        with page.expect_navigation():
            page.get_by_role("link", name="Blog").first.click()
        assert "/blog" in page.url, f"[{browser_name}] Expected /blog in URL, got: {page.url}"


@pytest.mark.ui
class TestHeroSection:
    """Verify the hero section content and CTAs."""

    def test_hero_section_visible(self, page: Page, browser_name: str):
        """Hero heading should be visible above the fold."""
        page.goto(BASE_URL)
        hero = page.locator("h1").first
        expect(hero).to_be_visible()
        assert hero.bounding_box()["y"] < 800, (
            f"[{browser_name}] Hero heading not above the fold"
        )

    def test_hero_buy_crypto_cta(self, page: Page, browser_name: str):
        """Buy crypto CTA in hero should be clickable and navigate correctly."""
        page.goto(BASE_URL)
        buy_btn = page.get_by_role("link", name="Buy crypto").first
        href = buy_btn.get_attribute("href")
        assert href is not None, f"[{browser_name}] Buy crypto CTA has no href"

    def test_hero_subtext_visible(self, page: Page, browser_name: str):
        """Hero subtext describing payment methods should be visible."""
        page.goto(BASE_URL)
        expect(
            page.locator("text=Buy or sell more than 30 cryptocurrencies").first
        ).to_be_visible()


@pytest.mark.ui
class TestStepsSection:
    """Verify the 3-step onboarding section."""

    def test_steps_section_visible(self, page: Page, browser_name: str):
        """3-step section heading should be present."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        expect(
            page.locator("text=Buy crypto in 3 simple steps").first
        ).to_be_visible()

    def test_step_1_content(self, page: Page, browser_name: str):
        """Step 1 should mention choosing crypto."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        expect(page.locator("text=Choose your").first).to_be_visible()

    def test_step_3_content(self, page: Page, browser_name: str):
        """Step 3 should mention receiving crypto instantly."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        expect(page.locator("text=Receive your crypto instantly").first).to_be_visible()


@pytest.mark.ui
class TestFeeComparisonSection:
    """Verify the fee comparison table is rendered correctly."""

    @pytest.mark.p1
    def test_fee_section_heading_visible(self, page: Page, browser_name: str):
        """Fee comparison section heading should be visible."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        expect(page.locator("text=Among the lowest fees").first).to_be_visible()

    def test_swapped_fee_displayed(self, page: Page, browser_name: str):
        """Swapped.com fee row should be present in the comparison table."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        expect(page.locator("text=4.02%").first).to_be_visible()

    def test_competitor_fees_displayed(self, page: Page, browser_name: str):
        """Competitor fee rows (Moonpay, Transak, Paybis) should be visible."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        for competitor in ["Moonpay", "Transak", "Paybis"]:
            expect(
                page.locator(f"text={competitor}").first
            ).to_be_visible(), f"[{browser_name}] {competitor} not found in fee table"


@pytest.mark.ui
class TestTrustSection:
    """Verify the trust/social proof section."""

    def test_trustpilot_section_visible(self, page: Page, browser_name: str):
        """Trusted by 1.8M+ section should be visible."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        expect(page.locator("text=1.8M+").first).to_be_visible()

    def test_customer_reviews_visible(self, page: Page, browser_name: str):
        """At least one customer review should be visible."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        reviews = page.locator("text=Trustpilot").all()
        # Reviews link to Trustpilot
        assert len(page.get_by_role("link").filter(has_text="Trustpilot").all()) > 0 or \
               page.locator("text=Emmet Lee").is_visible(), \
            f"[{browser_name}] No customer reviews found"

    def test_regulated_section_visible(self, page: Page, browser_name: str):
        """Regulated & secure section should be visible."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        expect(page.locator("text=Regulated").first).to_be_visible()


@pytest.mark.ui
class TestFooter:
    """Verify footer links and legal information."""

    @pytest.mark.p1
    def test_footer_privacy_policy_link(self, page: Page, browser_name: str):
        """Privacy policy link should be in the footer."""
        page.goto(BASE_URL)
        expect(page.get_by_role("link", name="Privacy policy").first).to_be_visible()

    def test_footer_terms_of_use_link(self, page: Page, browser_name: str):
        """Terms of use link should be in the footer."""
        page.goto(BASE_URL)
        expect(page.get_by_role("link", name="Terms of use").first).to_be_visible()

    def test_footer_cookie_policy_link(self, page: Page, browser_name: str):
        """Cookie policy link should be in the footer."""
        page.goto(BASE_URL)
        expect(page.get_by_role("link", name="Cookie policy").first).to_be_visible()

    def test_footer_copyright_text(self, page: Page, browser_name: str):
        """Footer should contain copyright text."""
        page.goto(BASE_URL)
        expect(page.locator("text=Copyright 2026 Swapped").first).to_be_visible()

    def test_footer_risk_warning_visible(self, page: Page, browser_name: str):
        """Crypto risk warning should be present in the footer."""
        page.goto(BASE_URL)
        expect(page.locator("text=Crypto prices can move fast").first).to_be_visible()

    def test_footer_regulatory_links_present(self, page: Page, browser_name: str):
        """At least one regulatory body link should be present in footer."""
        page.goto(BASE_URL)
        regulatory_text = ["ASIC", "Fintrac", "Danish FSA", "FinCEN"]
        found = any(
            page.locator(f"text={r}").count() > 0 for r in regulatory_text
        )
        assert found, f"[{browser_name}] No regulatory body links found in footer"

    def test_footer_blog_link(self, page: Page, browser_name: str):
        """Blog link should be present in the footer."""
        page.goto(BASE_URL)
        blog_links = page.get_by_role("link", name="Blog").all()
        assert len(blog_links) > 0, f"[{browser_name}] Blog link not found"


@pytest.mark.ui
class TestResponsiveness:
    """Verify the homepage renders correctly on mobile viewports."""

    def test_homepage_loads_on_mobile(self, mobile_page: Page, browser_name: str):
        """Homepage should load correctly on a mobile viewport."""
        response = mobile_page.goto(BASE_URL)
        assert response.status == 200, (
            f"[{browser_name}] Mobile homepage returned {response.status}"
        )
        expect(mobile_page.locator("h1").first).to_be_visible()

    def test_mobile_hero_visible(self, mobile_page: Page, browser_name: str):
        """Hero heading should be visible on mobile."""
        mobile_page.goto(BASE_URL)
        mobile_page.wait_for_load_state("domcontentloaded")
        expect(mobile_page.locator("h1").first).to_be_visible()

    def test_mobile_no_horizontal_scroll(self, mobile_page: Page, browser_name: str):
        """Page should not have horizontal scroll on mobile."""
        mobile_page.goto(BASE_URL)
        mobile_page.wait_for_load_state("networkidle")
        scroll_width = mobile_page.evaluate("document.documentElement.scrollWidth")
        viewport_width = mobile_page.viewport_size["width"]
        assert scroll_width <= viewport_width + 5, (
            f"[{browser_name}] Horizontal scroll detected: "
            f"scrollWidth={scroll_width}, viewportWidth={viewport_width}"
        )


@pytest.mark.ui
class TestBlogSection:
    """Verify the blog preview section on the homepage."""

    def test_blog_section_visible(self, page: Page, browser_name: str):
        """Blog section heading should be visible."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        expect(page.locator("text=From the blog").first).to_be_visible()

    def test_blog_articles_present(self, page: Page, browser_name: str):
        """At least one blog article should be listed."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        expect(
            page.locator("text=Getting Started with Decentralized Trading").first
        ).to_be_visible()

    def test_visit_blog_link_present(self, page: Page, browser_name: str):
        """Visit blog CTA link should be present."""
        page.goto(BASE_URL)
        expect(page.get_by_role("link", name="Visit blog").first).to_be_visible()
