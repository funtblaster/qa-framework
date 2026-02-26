import pytest
from playwright.sync_api import sync_playwright, Browser, Page
from tests.ui.pages.home_page import HomePage
from tests.ui.pages.trade_page import TradePage

BASE_URL = "https://swapped.com"

BROWSERS = ["chromium", "firefox", "webkit"]


def pytest_generate_tests(metafunc):
    """Parametrize browser fixture across chromium, firefox, and webkit."""
    if "browser_name" in metafunc.fixturenames:
        metafunc.parametrize("browser_name", BROWSERS)


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture()
def browser(playwright_instance, browser_name):
    """Launch the appropriate browser for each test."""
    headless = True
    if browser_name == "chromium":
        b: Browser = playwright_instance.chromium.launch(headless=headless)
    elif browser_name == "firefox":
        b: Browser = playwright_instance.firefox.launch(headless=headless)
    elif browser_name == "webkit":
        b: Browser = playwright_instance.webkit.launch(headless=headless)
    else:
        raise ValueError(f"Unknown browser: {browser_name}")
    yield b
    b.close()


@pytest.fixture()
def page(browser) -> Page:
    """Create a new browser context and page for each test."""
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        locale="en-US",
    )
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture()
def mobile_page(browser) -> Page:
    """Create a mobile-sized page for responsive tests."""
    context = browser.new_context(
        viewport={"width": 390, "height": 844},
        user_agent=(
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        ),
        locale="en-US",
    )
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture()
def home_page(page) -> HomePage:
    hp = HomePage(page)
    page.goto(f"{BASE_URL}{HomePage.URL}")
    hp.wait_for_load()
    return hp


@pytest.fixture()
def trade_page(page) -> TradePage:
    tp = TradePage(page)
    page.goto(f"{BASE_URL}{TradePage.URL}")
    tp.wait_for_load()
    return tp


@pytest.fixture()
def mobile_home_page(mobile_page) -> HomePage:
    hp = HomePage(mobile_page)
    mobile_page.goto(f"{BASE_URL}{HomePage.URL}")
    hp.wait_for_load()
    return hp
