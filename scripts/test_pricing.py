from core.pricing import calculate_total_cost

companies = [
    ("Wise", 0.9328),
    ("Panda Remit", 0.9310),
    ("Japan Remit Finance", 0.9290),
    ("City Express", 0.9240),
    ("WorldRemit", 0.9141),
    ("SBI Remit", 0.9310),
]

for company, rate in companies:
    result = calculate_total_cost(
        company_name=company,
        target_npr=100000,
        rate=rate,
        deposit_method="bank_transfer"
    )

    print(company, result)s