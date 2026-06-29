from dataclasses import dataclass, field
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
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.collected_at:
            self.collected_at = datetime.now().isoformat(timespec="seconds")