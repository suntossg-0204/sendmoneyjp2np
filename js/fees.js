import { getDefaultFee, getDynamicServiceFee } from "./pricing.js";

export function initializeUserFees(dashboardData, pricingRules, targetNpr) {
  let userFees = {};
  for (const company of dashboardData.companies) {
    const name = company.company_name;
    const rules = pricingRules[name] || {};
    userFees[name] = { service_fee: getDefaultFee(rules.service_fee, targetNpr), deposit_fee: 0 };
  }
  const savedFees = localStorage.getItem("remittracker_user_fees");
  if (savedFees) userFees = { ...userFees, ...JSON.parse(savedFees) };
  return userFees;
}

export function applyDepositMethodDefaults(dashboardData, userFees, method) {
  const atmProviders = new Set(["SBI Remit", "Japan Remit Finance", "City Express", "PayForex", "Yehey Remit", "Panda Remit"]);
  for (const company of dashboardData.companies) {
    const name = company.company_name;
    if (!userFees[name]) continue;
    userFees[name].deposit_fee = method === "deposit_card_atm" && atmProviders.has(name) ? 330 : 0;
  }
  localStorage.setItem("remittracker_user_fees", JSON.stringify(userFees));
  return userFees;
}

export function renderFeeSettings({ feeSettings, dashboardData, pricingRules, userFees, targetNpr }) {
  if (!feeSettings || !dashboardData) return;
  feeSettings.innerHTML = `
    <p class="settings-note">Default fees are loaded automatically. Edit them if your bank charges different fees or if a campaign/promotion applies.</p>
    <div class="fee-grid">
      <div class="fee-row fee-header"><strong>Company</strong><strong>Service Fee (¥)</strong><strong>Deposit Fee (¥)</strong></div>
      ${dashboardData.companies.map(company => {
        const name = company.company_name;
        const fees = userFees[name] || { service_fee: 0, deposit_fee: 0, service_fee_manually_changed: false };
        const serviceFee = fees.service_fee_manually_changed
          ? Number(fees.service_fee || 0)
          : getDynamicServiceFee(company, targetNpr, pricingRules);
        return `
          <div class="fee-row">
            <strong>${name}</strong>
            <input type="number" min="0" value="${serviceFee}" data-company="${name}" data-fee-type="service_fee" />
            <input type="number" min="0" value="${fees.deposit_fee || 0}" data-company="${name}" data-fee-type="deposit_fee" />
          </div>`;
      }).join("")}
    </div>`;
}
