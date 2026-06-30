const amountInput = document.getElementById("amountInput");
const companyList = document.getElementById("companyList");
const lastUpdated = document.getElementById("lastUpdated");
const bestCompany = document.getElementById("bestCompany");
const bestReceived = document.getElementById("bestReceived");
const differenceAmount = document.getElementById("differenceAmount");

let dashboardData = null;

function formatNpr(value) {
  return `NPR ${Number(value).toLocaleString(undefined, {
    maximumFractionDigits: 2
  })}`;
}

function formatJpy(value) {
  return `¥${Math.ceil(Number(value)).toLocaleString()}`;
}

function calculateRequiredJpy(targetNpr, company) {
  const fee = Number(company.service_fee || 0);
  const rate = Number(company.rate || 0);

  if (!rate) return 0;

  return Math.ceil((targetNpr / rate) + fee);
}

function render() {
  if (!dashboardData) return;

  const targetNpr = Number(amountInput.value || 0);

  const companies = dashboardData.companies
    .map(company => ({
      ...company,
      required_jpy: calculateRequiredJpy(targetNpr, company)
    }))
    .sort((a, b) => a.required_jpy - b.required_jpy);

  const best = companies[0];
  const second = companies[1];

  lastUpdated.textContent = dashboardData.last_updated || "-";
  bestCompany.textContent = best ? best.company_name : "-";
  bestReceived.textContent = best ? formatJpy(best.required_jpy) : "-";

  differenceAmount.textContent =
    best && second
      ? formatJpy(second.required_jpy - best.required_jpy)
      : "-";

    companyList.innerHTML = companies.map((company, index) => `
    <div class="company-card">
      <div class="rank">${index + 1}</div>

      <div>
        <div class="company-name">${company.company_name}</div>
        <div class="company-meta">
          Exchange Rate: ${Number(company.rate).toFixed(6)}
        </div>
        <div class="company-meta">
          Service Fee: ${formatJpy(company.service_fee || 0)}
        </div>
      </div>

      <div class="company-result">
        <div class="rate">You need to send</div>
        <div class="received">${formatJpy(company.required_jpy)}</div>
        <div class="company-meta">Nepal receives ${formatNpr(targetNpr)}</div>
      </div>
    </div>
  `).join("");
}

async function loadDashboard() {
  try {
    const response = await fetch("data/dashboard.json", { cache: "no-store" });
    dashboardData = await response.json();
    render();
  } catch (error) {
    companyList.innerHTML = "<p>Could not load dashboard data.</p>";
    console.error(error);
  }
}

amountInput.addEventListener("input", render);
loadDashboard();