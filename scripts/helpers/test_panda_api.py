import requests
import json

url = "https://prod.pandaremit.com/pricing/rate/JPY/NPR"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

response = requests.get(url, headers=headers)

print("Status:", response.status_code)
print()

try:
    data = response.json()
    print(json.dumps(data, indent=4, ensure_ascii=False))
except Exception:
    print(response.text)