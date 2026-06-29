from core.calculator import rank_companies

companies = [
    {
        "company_name": "Wise",
        "rate": 0.9330,
        "service_fee": 0
    },
    {
        "company_name": "Panda",
        "rate": 0.9309,
        "service_fee": 400
    }
]

result = rank_companies(100000, companies)

for r in result:
    print(r)