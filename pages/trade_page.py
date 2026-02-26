from .base_page import BasePage


class TradePage(BasePage):
    URL = "/trade"

    def __init__(self, page):
        super().__init__(page)
        self.page_container = page.locator("body")
        self.buy_tab = page.get_by_role("tab", name="Buy").first
        self.sell_tab = page.get_by_role("tab", name="Sell").first
        self.crypto_selector = page.locator("[data-testid='crypto-selector']")
        self.amount_input = page.get_by_role("spinbutton").first
        self.payment_method_selector = page.locator("[data-testid='payment-method']")
        self.proceed_btn = page.get_by_role("button", name="Proceed").first
        self.get_started_btn = page.get_by_role("button", name="Get started").first
