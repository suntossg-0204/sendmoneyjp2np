export function getDefaultFee(rule, amount = 100000) {
  if (!rule) return 0;
  if ("fee" in rule) return Number(rule.fee);
  if (rule.type === "fixed") return Number(rule.value || 0);
  if (rule.type === "tiered" || rule.tiers) {
    for (const tier of rule.tiers || []) {
      if (amount <= Number(tier.max)) return Number(tier.fee);
    }
  }
  return 0;
}

export function getDynamicServiceFee(company, targetNpr, pricingRules) {
  const rate = Number(company.rate || 0);
  if (!rate || !targetNpr) return 0;
  const remittanceAmount = Math.ceil(targetNpr / rate);
  const rules = pricingRules[company.company_name] || {};
  return getDefaultFee(rules.service_fee, remittanceAmount);
}

export function calculateCompanyCost(company, targetNpr, pricingRules, userFees) {
  const rate = Number(company.rate || 0);
  if (!rate || !targetNpr) {
    return { ...company, remittance_amount: 0, service_fee: 0, deposit_fee: 0, required_jpy: 0 };
  }

  const remittanceAmount = Math.ceil(targetNpr / rate);
  const feeState = userFees[company.company_name] || {};
  const serviceFee = feeState.service_fee_manually_changed
    ? Number(feeState.service_fee || 0)
    : getDynamicServiceFee(company, targetNpr, pricingRules);
  const depositFee = Number(feeState.deposit_fee || 0);

  return {
    ...company,
    remittance_amount: remittanceAmount,
    service_fee: serviceFee,
    deposit_fee: depositFee,
    required_jpy: remittanceAmount + serviceFee + depositFee
  };
}
