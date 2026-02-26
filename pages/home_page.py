from .base_page import BasePage


class HomePage(BasePage):
    URL = "/"

    def __init__(self, page):
        super().__init__(page)
        self.hero_heading = page.locator("h1").first
        self.buy_crypto_nav = page.get_by_role("link", name="Buy crypto").first
        self.sell_crypto_nav = page.get_by_role("link", name="Sell crypto").first
        self.get_started_btn = page.get_by_role("link", name="Get started").first
        self.buy_crypto_hero_btn = page.get_by_role("link", name="Buy crypto").nth(1)
        self.trustpilot_section = page.locator("text=Trusted by 1.8M+")
        self.fee_comparison_table = page.locator("text=Among the lowest fees")
        self.steps_section = page.locator("text=Buy crypto in 3 simple steps")
        self.newsletter_input = page.get_by_role("textbox").first
        self.footer_home_link = page.locator("footer").get_by_role("link", name="Home").first
        self.footer_privacy_link = page.get_by_role("link", name="Privacy policy").first
        self.footer_terms_link = page.get_by_role("link", name="Terms of use").first
        self.cookie_policy_link = page.get_by_role("link", name="Cookie policy").first
        self.blog_link = page.get_by_role("link", name="Blog").first
        self.support_link = page.get_by_role("link", name="Support").first
        self.view_all_coins_link = page.get_by_role("link", name="View all coins")
        self.payment_methods_link = page.get_by_role("link", name="See all payment options")
