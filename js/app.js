const amountInput = document.getElementById("amountInput");
const depositMethod = document.getElementById("depositMethod");
const companyList = document.getElementById("companyList");
const lastUpdated = document.getElementById("lastUpdated");
const bestCompany = document.getElementById("bestCompany");
const bestReceived = document.getElementById("bestReceived");
const differenceAmount = document.getElementById("differenceAmount");
const feeSettings = document.getElementById("feeSettings");
const resetFees = document.getElementById("resetFees");
const smartRecommendation = document.getElementById("smartRecommendation");

let dashboardData = null;
let pricingRules = {};
let userFees = {};

function formatNpr(value) {
  return `NPR ${Number(value).toLocaleString(undefined, {
    maximumFractionDigits: 2
  })}`;
}

function formatJpy(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "¥0";
  return `¥${Math.ceil(number).toLocaleString()}`;
}

function formatTime(value) {
  if (!value) return "-";

  const date = new Date(value + "+09:00");

  return date.toLocaleTimeString("ja-JP", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false
  });
}

function getHealthStatus(value) {
  if (!value) return { label: "No data", className: "bad" };

  const collected = new Date(value + "+09:00");
  const now = new Date();
  const diffMinutes = (now - collected) / 1000 / 60;

  if (diffMinutes <= 30) return { label: "Live", className: "good" };
  if (diffMinutes <= 120) return { label: "Stale", className: "warn" };

  return { label: "Old", className: "bad" };
}

function getDefaultFee(rule, amount = 100000) {
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

function initializeUserFees() {
  const targetNpr = Number(amountInput.value || 100000);

  for (const company of dashboardData.companies) {
    const name = company.company_name;
    const rules = pricingRules[name] || {};

    userFees[name] = {
      service_fee: getDefaultFee(rules.service_fee, targetNpr),
      deposit_fee: 0
    };
  }

  const savedFees = localStorage.getItem("remittracker_user_fees");

  if (savedFees) {
    userFees = {
      ...userFees,
      ...JSON.parse(savedFees)
    };
  }
}

function applyDepositMethodDefaults() {
  const method = depositMethod ? depositMethod.value : "bank_transfer";

  for (const company of dashboardData.companies) {
    const name = company.company_name;

    if (!userFees[name]) continue;

    if (method === "bank_transfer") {
      userFees[name].deposit_fee = 0;
      continue;
    }

    switch (name) {
      case "SBI Remit":
      case "Japan Remit Finance":
      case "City Express":
      case "PayForex":
      case "Yehey Remit":
      case "Panda Remit":
        userFees[name].deposit_fee = 330;
        break;

      default:
        userFees[name].deposit_fee = 0;
    }
  }

  localStorage.setItem("remittracker_user_fees", JSON.stringify(userFees));
}

function renderFeeSettings() {
  feeSettings.innerHTML = `
    <p class="settings-note">
      Default fees are loaded automatically. Edit them if your bank charges different fees or if a campaign/promotion applies.
    </p>

    <div class="fee-grid">
      <div class="fee-row fee-header">
        <strong>Company</strong>
        <strong>Service Fee (¥)</strong>
        <strong>Deposit Fee (¥)</strong>
      </div>

      ${dashboardData.companies.map(company => {
        const name = company.company_name;
        const fees = userFees[name] || { service_fee: 0, deposit_fee: 0 };

        return `
          <div class="fee-row">
            <strong>${name}</strong>

            <input
              type="number"
              min="0"
              value="${fees.service_fee}"
              data-company="${name}"
              data-fee-type="service_fee"
            />

            <input
              type="number"
              min="0"
              value="${fees.deposit_fee}"
              data-company="${name}"
              data-fee-type="deposit_fee"
            />
          </div>
        `;
      }).join("")}
    </div>
  `;
}

function calculateCompanyCost(company, targetNpr) {
  const rate = Number(company.rate || 0);

  if (!rate || !targetNpr) {
    return {
      ...company,
      remittance_amount: 0,
      service_fee: 0,
      deposit_fee: 0,
      required_jpy: 0
    };
  }

  const remittanceAmount = Math.ceil(targetNpr / rate);

  const serviceFee = Number(userFees[company.company_name]?.service_fee || 0);
  const depositFee = Number(userFees[company.company_name]?.deposit_fee || 0);

  const totalJpy = remittanceAmount + serviceFee + depositFee;

  return {
    ...company,
    remittance_amount: remittanceAmount,
    service_fee: serviceFee,
    deposit_fee: depositFee,
    required_jpy: totalJpy
  };
}

function render() {
  if (!dashboardData) return;

  const targetNpr = Number(amountInput.value || 0);

  const companies = dashboardData.companies
    .map(company => calculateCompanyCost(company, targetNpr))
    .sort((a, b) => a.required_jpy - b.required_jpy);

  const best = companies[0];
  const second = companies[1];
  const saving = second
  ? second.required_jpy - best.required_jpy
  : 0;

smartRecommendation.innerHTML = `
<strong>${best.company_name}</strong> is the cheapest option based on your current fee settings.<br>
You'll save <strong>${formatJpy(saving)}</strong> compared with <strong>${second.company_name}</strong>.
`;

  lastUpdated.textContent = dashboardData.last_updated || "-";
  bestCompany.textContent = best ? best.company_name : "-";
  bestReceived.textContent = best ? formatJpy(best.required_jpy) : "-";

  differenceAmount.textContent =
    best && second ? formatJpy(second.required_jpy - best.required_jpy) : "-";

  companyList.innerHTML = companies.map((company, index) => {
    const health = getHealthStatus(company.collected_at);

    return `
      <div class="company-card">
        <div class="rank">${index + 1}</div>

        <div>
          <div class="company-name">${company.company_name}</div>
          <div class="company-meta">
            Rate: ${Number(company.rate).toFixed(6)}
          </div>
          
          <div class="company-meta">
            Updated: ${formatTime(company.collected_at)}
           <span class="status ${health.className}">${health.label}</span>
          </div>
        </div>

        <div class="company-result">
          <div class="rate">Total you pay</div>
          <div class="received">${formatJpy(company.required_jpy)}</div>

          ${index === 0 ? `<div class="company-meta best-price">🏆 Best Price</div>` : ""}
        </div>
      </div>
    `;
  }).join("");
}

async function loadDashboard() {
  try {
    const [dashboardResponse, pricingResponse] = await Promise.all([
      fetch("data/dashboard.json", { cache: "no-store" }),
      fetch("data/pricing_rules.json", { cache: "no-store" })
    ]);

    dashboardData = await dashboardResponse.json();
    pricingRules = await pricingResponse.json();

    initializeUserFees();
    applyDepositMethodDefaults();
    renderFeeSettings();
    render();
  } catch (error) {
    companyList.innerHTML = "<p>Could not load dashboard data.</p>";
    console.error(error);
  }
}

amountInput.addEventListener("input", () => {
  render();
});

if (depositMethod) {
  depositMethod.addEventListener("change", () => {
    applyDepositMethodDefaults();
    renderFeeSettings();
    render();
  });
}

feeSettings.addEventListener("input", (e) => {
  if (e.target.tagName !== "INPUT") return;

  const company = e.target.dataset.company;
  const feeType = e.target.dataset.feeType;

  userFees[company][feeType] = Number(e.target.value || 0);

  localStorage.setItem("remittracker_user_fees", JSON.stringify(userFees));

  render();
});

resetFees.addEventListener("click", () => {
  localStorage.removeItem("remittracker_user_fees");

  userFees = {};
  initializeUserFees();
  applyDepositMethodDefaults();
  renderFeeSettings();
  render();
});

loadDashboard();