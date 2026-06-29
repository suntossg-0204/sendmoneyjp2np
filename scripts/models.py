from dataclasses import dataclass
from datetime import datetime


@dataclass
class RateSnapshot:
    company: str
    rate: float
    source_url: str
    currency_pair: str = "JPY-NPR"
    service_fee: int = 0
    atm_fee: int = 0
    deposit_method: str = "Online"
    status: str = "success"
    collected_at: str = ""

    def __post_init__(self):
        if not self.collected_at:
            self.collected_at = datetime.now().isoformat(timespec="seconds")