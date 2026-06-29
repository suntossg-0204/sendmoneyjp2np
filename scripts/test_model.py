from models import RateSnapshot

snapshot = RateSnapshot(
    company="Wise",
    rate=0.9336,
    source_url="https://wise.com"
)

print(snapshot)