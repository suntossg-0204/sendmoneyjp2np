import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path("data/rates.json")

companies = [
    {"company": "Wise", "rate": 0.9460},
    {"company": "Panda Remit", "rate": 0.9451},
    {"company": "SBI Remit", "rate": 0.9440}
]

now = datetime.now().isoformat(timespec="seconds")

if DATA_FILE.exists():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
else:
    data = {"last_updated": "", "rates": []}

for item in companies:
    data["rates"].append({
        "datetime": now,
        "company": item["company"],
        "rate": item["rate"]
    })

data["last_updated"] = now

DATA_FILE.write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("Rates updated:", now)
