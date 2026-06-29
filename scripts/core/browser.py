from playwright.sync_api import sync_playwright
from config import HEADLESS, TIMEOUT, USER_AGENT


def open_page(url):
    playwright = sync_playwright().start()

    browser = playwright.chromium.launch(headless=HEADLESS)

    page = browser.new_page(
        user_agent=USER_AGENT
    )

    page.set_default_timeout(TIMEOUT)
    page.goto(url, wait_until="networkidle", timeout=TIMEOUT)

    return playwright, browser, page
