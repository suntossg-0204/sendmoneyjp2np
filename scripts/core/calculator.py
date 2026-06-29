from typing import List


def calculate_received(amount_jpy: float, rate: float, fee_jpy: float = 0):
    send_amount = max(amount_jpy - fee_jpy, 0)
    return round(send_amount * rate, 2)


def rank_companies(amount_jpy: float, companies: List[dict]):
    results = []

    for company in companies:
        received = calculate_received(
            amount_jpy,
            company["rate"],
            company.get("service_fee", 0)
        )

        company["received_npr"] = received
        results.append(company)

    results.sort(
        key=lambda x: x["received_npr"],
        reverse=True
    )

    return results