from abc import ABC, abstractmethod
from core.browser import open_page
from core.debug import save_failure_screenshot


class BaseCollector(ABC):
    COMPANY = ""
    URL = ""
    SERVICE_FEE = 0
    ATM_FEE = 0
    DEPOSIT_METHOD = "Online"

    def collect(self):
        playwright = None
        browser = None

        try:
            playwright, browser, page = open_page(self.URL)

            rate = self.extract_rate(page)

            return self.build_snapshot(rate)

        except Exception:
            if browser:
                try:
                    save_failure_screenshot(page, self.COMPANY)
                except Exception:
                    pass
            raise

        finally:
            if browser:
                browser.close()
            if playwright:
                playwright.stop()

    @abstractmethod
    def extract_rate(self, page):
        pass

    def build_snapshot(self, rate):
        from models import RateSnapshot

        return RateSnapshot(
            company=self.COMPANY,
            rate=rate,
            source_url=self.URL,
            service_fee=self.SERVICE_FEE,
            atm_fee=self.ATM_FEE,
            deposit_method=self.DEPOSIT_METHOD
        )