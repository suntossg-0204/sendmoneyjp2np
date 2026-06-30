import requests
import json

url = "https://exchange.city-remit.net/api/rates"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

response = requests.get(url, headers=headers, timeout=30)

print("STATUS:", response.status_code)
print("=" * 80)

try:
    print(json.dumps(response.json(), indent=2, ensure_ascii=False)[:10000])
except Exception:
    print(response.text[:10000])