import requests

URL = "https://yeheyremit.jp/assets/fees-CyaQqTnL.js"

text = requests.get(URL, timeout=30).text

print("=" * 80)
print("FIRST 12000 CHARS")
print("=" * 80)
print(text[:12000])

print("=" * 80)
print("MATCHES")
print("=" * 80)

for keyword in ["NPR", "PHP", "rate", "fee", "firestore", "collection"]:
    print(f"\n--- {keyword} ---")
    idx = text.lower().find(keyword.lower())
    if idx != -1:
        print(text[max(0, idx - 500):idx + 1000])