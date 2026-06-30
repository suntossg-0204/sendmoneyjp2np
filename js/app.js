const amountInput = document.getElementById("amountInput");
const depositMethod = document.getElementById("depositMethod");
const companyList = document.getElementById("companyList");
const lastUpdated = document.getElementById("lastUpdated");
const bestCompany = document.getElementById("bestCompany");
const bestReceived = document.getElementById("bestReceived");
const differenceAmount = document.getElementById("differenceAmount");

let dashboardData = null;
let pricingRules = {};

function formatNpr(value) {
  return `NPR ${Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
}

function formatJpy(value) {
  return `¥${Math.ceil(Number(value)).toLocaleString()}`;
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

function calculateFee(rule, amount) {
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

function calculateCompanyCost(company, targetNpr, method) {
  const rate = Number(company.rate || 0);
  const rules = pricingRules[company.company_name] || {};

  if (!rate) {
    return {
      ...company,
      remittance_amount: 0,
      service_fee: 0,
      deposit_fee: 0,
      required_jpy: 0
    };
  }

  const remittanceAmount = Math.ceil(targetNpr / rate);
  const serviceFee = calculateFee(rules.service_fee, remittanceAmount);
  const depositRule = rules.deposit_methods?.[method] || {};
  const depositFee = calculateFee(depositRule, remittanceAmount);
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
  const method = depositMethod ? depositMethod.value : "bank_transfer";

  const companies = dashboardData.companies
    .map(company => calculateCompanyCost(company, targetNpr, method))
    .sort((a, b) => a.required_jpy - b.required_jpy);

  const best = companies[0];
  const second = companies[1];
  const bestCost = best ? best.required_jpy : 0;

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
            Exchange Rate: ${Number(company.rate).toFixed(6)} (As of ${formatTime(company.collected_at)})
          </div>
          <div class="company-meta">
            Service Fee: ${formatJpy(company.service_fee || 0)}
          </div>
          <div class="company-meta">
            Deposit Fee: ${formatJpy(company.deposit_fee || 0)}
          </div>
          <div class="company-meta">
            Status: <span class="status ${health.className}">${health.label}</span>
          </div>
        </div>

        <div class="company-result">
          <div class="rate">Total you pay</div>
          <div class="received">${formatJpy(company.required_jpy)}</div>
		  <div class="company-meta">
           ${index === 0 ? `<div class="company-meta best-price">🏆 Best Price</div>` : ""}
          </div>
          <div class="company-meta">
            Remittance amount: ${formatJpy(company.remittance_amount)}
          </div>
          <div class="company-meta">
            Nepal receives ${formatNpr(targetNpr)}
          </div>
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

    render();
  } catch (error) {
    companyList.innerHTML = "<p>Could not load dashboard data.</p>";
    console.error(error);
  }
}

amountInput.addEventListener("input", render);
if (depositMethod) depositMethod.addEventListener("change", render);

loadDashboard();