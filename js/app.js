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
  return `¥${Number(value).toLocaleString()}`;
}

function calculateReceived(amount, company) {
  const fee = Number(company.service_fee || 0);
  const rate = Number(company.rate || 0);
  return Math.max(amount - fee, 0) * rate;
}

function render() {
  if (!dashboardData) return;

  const amount = Number(amountInput.value || 0);

  const companies = dashboardData.companies
    .map(company => ({
      ...company,
      received_npr: calculateReceived(amount, company)
    }))
    .sort((a, b) => b.received_npr - a.received_npr);

  const best = companies[0];
  const second = companies[1];

  lastUpdated.textContent = dashboardData.last_updated || "-";
  bestCompany.textContent = best ? best.company_name : "-";
  bestReceived.textContent = best ? formatNpr(best.received_npr) : "-";

  differenceAmount.textContent =
    best && second
      ? formatNpr(best.received_npr - second.received_npr)
      : "-";

  companyList.innerHTML = companies.map((company, index) => `
    <div class="company-card">
      <div class="rank">${index + 1}</div>
      <div>
        <div class="company-name">${company.company_name}</div>
        <div class="company-meta">
          Rate: ${Number(company.rate).toFixed(6)} · Fee: ${formatJpy(company.service_fee || 0)}
        </div>
      </div>
      <div class="company-result">
        <div class="rate">${Number(company.rate).toFixed(6)}</div>
        <div class="received">${formatNpr(company.received_npr)}</div>
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