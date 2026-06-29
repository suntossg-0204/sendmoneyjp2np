import requests
import json

urls = [
    "https://www.jpremit.com/api/fetch/foreign-exchange-rates",
    "https://www.jpremit.com/api/fetch/country/fx/rate",
    "https://www.jpremit.com/api/country/service/fee/all",
]

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}

for url in urls:
    print("=" * 80)
    print(url)
    print("=" * 80)

    try:
        response = requests.get(url, headers=headers, timeout=30)
        print("STATUS:", response.status_code)

        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False)[:5000])
        except Exception:
            print(response.text[:5000])

    except Exception as e:
        print("ERROR:", e)