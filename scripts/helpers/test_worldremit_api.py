import requests
import json

url = "https://api.worldremit.com/graphql"

query = """
mutation createCalculation(
  $amount: BigDecimal!,
  $type: CalculationType!,
  $sendCountryCode: CountryCode!,
  $sendCurrencyCode: CurrencyCode!,
  $receiveCountryCode: CountryCode!,
  $receiveCurrencyCode: CurrencyCode!,
  $payOutMethodCode: String,
  $correspondentId: String
) {
  createCalculation(
    calculationInput: {
      amount: $amount,
      send: {country: $sendCountryCode, currency: $sendCurrencyCode},
      type: $type,
      receive: {country: $receiveCountryCode, currency: $receiveCurrencyCode},
      payOutMethodCode: $payOutMethodCode,
      correspondentId: $correspondentId
    }
  ) {
    calculation {
      send { amount currency }
      receive { amount currency }
      exchangeRate { value crossedOutValue }
      informativeSummary {
        fee { value { amount currency } type }
        totalToPay { amount }
      }
    }
        errors {
      __typename
      ... on GenericCalculationError {
        message
      }
      ... on ValidationCalculationError {
        message
        type
        code
        description
      }
    }
  }
}
"""

payload = {
    "operationName": "createCalculation",
    "variables": {
        "amount": 100000,
        "type": "SEND",
        "sendCountryCode": "JP",
        "sendCurrencyCode": "JPY",
        "receiveCountryCode": "NP",
        "receiveCurrencyCode": "NPR",
        "payOutMethodCode": "",
        "correspondentId": ""
    },
    "query": query
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-WR-PLATFORM": "web",
    "Origin": "https://www.worldremit.com",
    "Referer": "https://www.worldremit.com/"
}

response = requests.post(url, headers=headers, json=payload, timeout=30)

print("STATUS:", response.status_code)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))