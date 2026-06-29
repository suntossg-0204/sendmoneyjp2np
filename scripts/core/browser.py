from playwright.sync_api import sync_playwright
from config import HEADLESS, TIMEOUT, USER_AGENT


def open_page(url, wait_until="domcontentloaded"):
    playwright = sync_playwright().start()

    browser = playwright.chromium.launch(headless=HEADLESS)

    context = browser.new_context(
        ignore_https_errors=True,
        user_agent=USER_AGENT
    )

    page = context.new_page()

    page.set_default_timeout(TIMEOUT)
    page.goto(url, wait_until=wait_until, timeout=TIMEOUT)

    return playwright, browser, page