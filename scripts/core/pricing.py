import json
from pathlib import Path
import math

RULES_PATH = Path("data/pricing_rules.json")


def load_rules():
    with open(RULES_PATH, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def calculate_fee(rule, amount):
    if not rule:
        return 0

    if "fee" in rule:
        return rule["fee"]

    if rule.get("type") == "fixed":
        return rule.get("value", 0)

    if rule.get("type") == "tiered" or "tiers" in rule:
        for tier in rule.get("tiers", []):
            if amount <= tier["max"]:
                return tier["fee"]

    return 0


def calculate_total_cost(
    company_name,
    target_npr,
    rate,
    deposit_method="bank_transfer"
):
    rules = load_rules()
    company_rules = rules.get(company_name, {})

    remittance_amount = math.ceil(target_npr / rate)

    service_fee = calculate_fee(
        company_rules.get("service_fee"),
        remittance_amount
    )

    deposit_rule = company_rules.get("deposit_methods", {}).get(
        deposit_method,
        {}
    )

    deposit_fee = calculate_fee(deposit_rule, remittance_amount)

    total_jpy = remittance_amount + service_fee + deposit_fee

    return {
        "remittance_amount": remittance_amount,
        "service_fee": service_fee,
        "deposit_fee": deposit_fee,
        "total_jpy": total_jpy
    }