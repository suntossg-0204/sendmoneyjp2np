from pathlib import Path
import sys
import requests

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(ROOT))
sys.path.append(str(PROJECT_ROOT))

from models import RateSnapshot

URL = "https://api.worldremit.com/graphql"


QUERY = """
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


def collect():
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
        "query": QUERY
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-WR-PLATFORM": "web",
        "Origin": "https://www.worldremit.com",
        "Referer": "https://www.worldremit.com/"
    }

    response = requests.post(
        URL,
        headers=headers,
        json=payload,
        timeout=30
    )

    response.raise_for_status()
    data = response.json()

    result = data["data"]["createCalculation"]

    if result.get("errors"):
        raise Exception(result["errors"])

    calculation = result["calculation"]

    return RateSnapshot(
        company="WorldRemit",
        rate=float(calculation["exchangeRate"]["value"]),
        source_url=URL,
        service_fee=float(
            calculation["informativeSummary"]["fee"]["value"]["amount"]
        ),
        deposit_method="Online",
        metadata={
            "send": calculation["send"],
            "receive": calculation["receive"],
            "fee": calculation["informativeSummary"]["fee"],
            "total_to_pay": calculation["informativeSummary"]["totalToPay"]["amount"]
        }
    )


if __name__ == "__main__":
    print(collect())