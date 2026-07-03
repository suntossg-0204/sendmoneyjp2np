from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo


def jst_now():
    return datetime.now(ZoneInfo("Asia/Tokyo")).replace(tzinfo=None).isoformat(timespec="seconds")


@dataclass
class RateSnapshot:
    company: str
    rate: float
    currency_pair: str = "JPY-NPR"
    service_fee: int = 0
    atm_fee: int = 0
    deposit_method: str = "Online"
    source_url: str = ""
    metadata: dict = field(default_factory=dict)
    collected_at: str = ""

    def __post_init__(self):
        if not self.collected_at:
            self.collected_at = jst_now()