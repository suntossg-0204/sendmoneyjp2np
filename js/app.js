const amountInput = document.getElementById("amountInput");
const depositMethod = document.getElementById("depositMethod");
const companyList = document.getElementById("companyList");

const lastUpdated = document.getElementById("lastUpdated");
const headerLastUpdated = document.getElementById("headerLastUpdated");

const feeSettings = document.getElementById("feeSettings");
const resetFees = document.getElementById("resetFees");
const smartRecommendation = document.getElementById("smartRecommendation");

const marketHigh = document.getElementById("marketHigh");
const marketLow = document.getElementById("marketLow");
const marketAverage = document.getElementById("marketAverage");
const marketSpread = document.getElementById("marketSpread");
const marketHighCompany = document.getElementById("marketHighCompany");
const marketLowCompany = document.getElementById("marketLowCompany");
const todaySummary = document.getElementById("todaySummary");
const marketIntelligence = document.getElementById("marketIntelligence");
const refreshData = document.getElementById("refreshData");

const DISPLAY_CONFIG = {
  businessStartHour: 9,
  businessEndHour: 21,
  excludedWeekdays: [6] // Saturday only
};

let dashboardData = null;
let pricingRules = {};
let trendsData = {};
let userFees = {};
let historyData = {};
let selectedCompany = null;
let historyChart = null;

function renderTodaySummary(companies){

    if(!todaySummary) return;

    const rates = companies.map(c=>Number(c.rate));

    const highest = Math.max(...rates);
    const lowest = Math.min(...rates);

    const spread = highest-lowest;

    const best = companies[0];

    todaySummary.innerHTML=`

        <div class="summary-item">
            <span>Best Provider</span>
            <strong>${best.company_name}</strong>
        </div>

        <div class="summary-item">
            <span>Highest Rate</span>
            <strong>${highest.toFixed(6)}</strong>
        </div>

        <div class="summary-item">
            <span>Lowest Rate</span>
            <strong>${lowest.toFixed(6)}</strong>
        </div>

        <div class="summary-item">
            <span>Market Spread</span>
            <strong>${spread.toFixed(4)}</strong>
        </div>

    `;
}

function formatJpy(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "¥0";
  return `¥${Math.ceil(number).toLocaleString()}`;
}

function formatDateTime(value) {
  if (!value) return "-";

  const date = new Date(value + "+09:00");

  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  const h = String(date.getHours()).padStart(2, "0");
  const min = String(date.getMinutes()).padStart(2, "0");

  return `${y}/${m}/${d} ${h}:${min} JST`;
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

  if (diffMinutes <= 90) return { label: "Live", className: "good" };
  if (diffMinutes <= 180) return { label: "Recent", className: "warn" };

  return { label: "Old", className: "bad" };
}

function isBusinessRateTime(value) {
  if (!value) return false;

  const date = new Date(value + "+09:00");
  const now = new Date();

  const isToday =
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate();

  const isAllowedDay = !DISPLAY_CONFIG.excludedWeekdays.includes(date.getDay());
  const isOperatingHour =
    date.getHours() >= DISPLAY_CONFIG.businessStartHour &&
    date.getHours() < DISPLAY_CONFIG.businessEndHour;

  return isToday && isAllowedDay && isOperatingHour;
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

function getCompanyHistoryRecords(companyName) {
  return (historyData[companyName] || [])
    .filter(record => isBusinessRateTime(record.collected_at))
    .sort((a, b) => new Date(a.collected_at) - new Date(b.collected_at));
}

function initializeUserFees() {
  const targetNpr = Number(amountInput?.value || 100000);
  userFees = {};

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
  if (!dashboardData) return;

  const method = depositMethod?.value || "bank_transfer";

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
  if (!feeSettings || !dashboardData) return;

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

function renderMarket(companies) {
  if (!marketHigh || !marketLow || !marketAverage || !marketSpread) return;

  const rates = companies
    .map(company => Number(company.rate))
    .filter(rate => Number.isFinite(rate));

  if (!rates.length) return;

  const highestCompany = companies.reduce((a, b) =>
    Number(a.rate) > Number(b.rate) ? a : b
  );

  const lowestCompany = companies.reduce((a, b) =>
    Number(a.rate) < Number(b.rate) ? a : b
  );

  const highest = Number(highestCompany.rate);
  const lowest = Number(lowestCompany.rate);
  const average = rates.reduce((a, b) => a + b, 0) / rates.length;
  const spread = lowest ? ((highest - lowest) / lowest) * 100 : 0;

  marketHigh.textContent = highest.toFixed(6);
  marketLow.textContent = lowest.toFixed(6);
  marketAverage.textContent = average.toFixed(6);
  marketSpread.textContent = `${spread.toFixed(2)}%`;

  if (marketHighCompany) {
    marketHighCompany.textContent = `🏆 ${highestCompany.company_name}`;
  }

  if (marketLowCompany) {
    marketLowCompany.textContent = `📉 ${lowestCompany.company_name}`;
  }
}

function renderRecommendation(best, second, targetNpr) {
  if (!smartRecommendation || !best) return;

  const saving = second ? second.required_jpy - best.required_jpy : 0;

  smartRecommendation.innerHTML = `
    <div class="recommendation-main">🏆 TODAY'S BEST CHOICE</div>
    <div class="recommendation-provider">${best.company_name}</div>
    <div class="recommendation-cost">${formatJpy(best.required_jpy)}</div>

    <div class="recommendation-note">
      Family receives <strong>NPR ${Number(targetNpr).toLocaleString()}</strong>.
      ${
        second
          ? `You save <strong>${formatJpy(saving)}</strong> compared with <strong>${second.company_name}</strong>.`
          : "Only one provider available."
      }
    </div>

    <div class="recommendation-updated">
      🕒 Updated ${formatDateTime(best.collected_at)}
    </div>
  `;
}

function renderSummary() {
  if (lastUpdated) {
    lastUpdated.textContent = formatDateTime(dashboardData.last_updated);
  }

  if (headerLastUpdated) {
    headerLastUpdated.textContent = formatDateTime(dashboardData.last_updated);
  }
}

function renderCompanyCards(companies) {
  if (!companyList) return;

  companyList.innerHTML = companies.map((company, index) => {
    const health = getHealthStatus(company.collected_at);

    const rank =
      index === 0 ? "🥇" :
      index === 1 ? "🥈" :
      index === 2 ? "🥉" :
      index + 1;

    const extraCost = company.required_jpy - companies[0].required_jpy;

    const trend = trendsData[company.company_name] || {
      direction: "same",
      change: 0
    };

    const trendIcon =
      trend.direction === "up" ? "📈" :
      trend.direction === "down" ? "📉" :
      "➖";

    const trendClass =
      trend.direction === "up" ? "trend-up" :
      trend.direction === "down" ? "trend-down" :
      "trend-flat";

    const trendValue =
      `${trend.direction === "up" ? "+" : trend.direction === "down" ? "-" : ""}${Math.abs(Number(trend.change || 0)).toFixed(4)}`;

    return `
      <div class="company-card ${index === 0 ? "best-card" : ""}">

        <div class="company-main"
             onclick="showHistory('${company.company_name}')">

          <div class="rank">${rank}</div>

          <div class="company-info">
            <div class="company-name">${company.company_name}</div>

            <div class="company-badges">
              <span class="badge-rate">💱 ${Number(company.rate).toFixed(6)}</span>
              <span class="${trendClass}">${trendIcon} ${trendValue}</span>
              <span class="badge-time">🕒 ${formatTime(company.collected_at)}</span>
              <span class="badge ${health.className}">${health.label}</span>
            </div>
          </div>

          <div class="company-result">
            <div class="rate">Total you pay</div>
            <div class="received">${formatJpy(company.required_jpy)}</div>

            ${
              index === 0
                ? `<div class="company-meta best-price">🏆 Best Price</div>`
                : `<div class="company-meta extra-cost">+${formatJpy(extraCost)} vs Best</div>`
            }
          </div>

        </div>

        ${
          selectedCompany === company.company_name
            ? `
              <div class="history-inline">
                <div class="history-title">📈 Rate History</div>

                <div
                  id="stats-${company.company_name.replace(/\s+/g, "-")}"
                  class="history-stats">
                </div>

                <canvas id="chart-${company.company_name.replace(/\s+/g, "-")}"></canvas>
              </div>
            `
            : ""
        }

      </div>
    `;
  }).join("");
}

function renderMarketIntelligence(companies) {
  if (!marketIntelligence) return;

  const insights = companies.map(company => {
    const records = getCompanyHistoryRecords(company.company_name);
    const rates = records.map(r => Number(r.rate));

    if (rates.length < 2) {
      return {
        company_name: company.company_name,
        change: 0,
        volatility: 0
      };
    }

    const opening = rates[0];
    const current = rates[rates.length - 1];
    const highest = Math.max(...rates);
    const lowest = Math.min(...rates);

    return {
      company_name: company.company_name,
      change: current - opening,
      volatility: highest - lowest
    };
  });

  const biggestGainer = [...insights].sort((a, b) => b.change - a.change)[0];
  const biggestLoser = [...insights].sort((a, b) => a.change - b.change)[0];
  const mostVolatile = [...insights].sort((a, b) => b.volatility - a.volatility)[0];
  const improvingCount = insights.filter(i => i.change > 0).length;

  marketIntelligence.innerHTML = `
    <div class="intelligence-item">
      <span>🏆 Leader Today</span>
      <strong>${companies[0].company_name}</strong>
    </div>

    <div class="intelligence-item">
      <span>📈 Biggest Gainer</span>
      <strong>${biggestGainer.company_name}<br>+${biggestGainer.change.toFixed(4)}</strong>
    </div>

    <div class="intelligence-item">
      <span>📉 Biggest Loser</span>
      <strong>${biggestLoser.company_name}<br>${biggestLoser.change.toFixed(4)}</strong>
    </div>

    <div class="intelligence-item">
      <span>🔥 Most Volatile</span>
      <strong>${mostVolatile.company_name}<br>${mostVolatile.volatility.toFixed(4)}</strong>
    </div>

    <div class="intelligence-item">
      <span>🟢 Improving</span>
      <strong>${improvingCount}/${insights.length}</strong>
    </div>
  `;
}

function render() {
  if (!dashboardData) return;

  const targetNpr = Number(amountInput?.value || 0);

  const companies = dashboardData.companies
    .map(company => calculateCompanyCost(company, targetNpr))
    .sort((a, b) => a.required_jpy - b.required_jpy);

  const best = companies[0];
  const second = companies[1];

  renderMarket(companies);
  renderMarketIntelligence(companies);
  renderRecommendation(best, second, targetNpr);
  renderSummary();
  renderCompanyCards(companies);
}

function renderHistoryStats(companyName) {
  const records = getCompanyHistoryRecords(companyName);
  const statsId = `stats-${companyName.replace(/\s+/g, "-")}`;
  const statsBox = document.getElementById(statsId);

  if (!statsBox) return;

  if (!records.length) {
    statsBox.innerHTML = `
      <div>
        <span>No data</span>
        <strong>-</strong>
      </div>
    `;
    return;
  }

  const rates = records.map(r => Number(r.rate));

  const opening = rates[0];
  const current = rates[rates.length - 1];
  const highest = Math.max(...rates);
  const lowest = Math.min(...rates);
  const change = current - opening;
  const volatility = highest - lowest;

  const changeText =
    `${change > 0 ? "+" : change < 0 ? "-" : ""}${Math.abs(change).toFixed(4)}`;

  const changeIcon =
    change > 0 ? "📈" : change < 0 ? "📉" : "➖";

  statsBox.innerHTML = `
    <div>
      <span>Current</span>
      <strong>${current.toFixed(6)}</strong>
    </div>

    <div>
      <span>Opening</span>
      <strong>${opening.toFixed(6)}</strong>
    </div>

    <div>
      <span>Highest</span>
      <strong>${highest.toFixed(6)}</strong>
    </div>

    <div>
      <span>Lowest</span>
      <strong>${lowest.toFixed(6)}</strong>
    </div>

    <div>
      <span>Today's Change</span>
      <strong>${changeIcon} ${changeText}</strong>
    </div>

    <div>
      <span>Volatility</span>
      <strong>${volatility.toFixed(4)}</strong>
    </div>

    <div>
      <span>Updates</span>
      <strong>${records.length}</strong>
    </div>
  `;
}

function renderHistoryChart(companyName) {
  const records = getCompanyHistoryRecords(companyName);

  if (!records.length || typeof Chart === "undefined") return;

  const canvasId = `chart-${companyName.replace(/\s+/g, "-")}`;
  const canvas = document.getElementById(canvasId);

  if (!canvas) return;

  if (historyChart) {
    historyChart.destroy();
  }

  const rates = records.map(r => Number(r.rate));
  const firstRate = rates[0];
  const lastRate = rates[rates.length - 1];
  const isUp = lastRate >= firstRate;

  const ctx = canvas.getContext("2d");

  const gradient = ctx.createLinearGradient(0, 0, 0, 350);
  gradient.addColorStop(0, isUp ? "rgba(22, 163, 74, 0.25)" : "rgba(220, 38, 38, 0.22)");
  gradient.addColorStop(1, "rgba(255, 255, 255, 0)");

  historyChart = new Chart(canvas, {
    type: "line",
    data: {
      labels: records.map(r => formatTime(r.collected_at)),
      datasets: [{
        label: companyName,
        data: rates,
        tension: 0.35,
        fill: true,
        backgroundColor: gradient,
        borderColor: isUp ? "#16a34a" : "#dc2626",
        borderWidth: 3,
        pointRadius: rates.map((_, i) => i === rates.length - 1 ? 6 : 3),
        pointHoverRadius: 7,
        pointBackgroundColor: isUp ? "#16a34a" : "#dc2626",
        pointBorderColor: "#ffffff",
        pointBorderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      resizeDelay: 200,
      interaction: {
        mode: "index",
        intersect: false
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            title: items => items[0].label,
            label: item => `Rate: ${Number(item.raw).toFixed(6)}`
          }
        }
      },
      scales: {
        x: {
          ticks: {
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: 8
          }
        },
        y: {
          ticks: {
            callback: value => Number(value).toFixed(4)
          }
        }
      }
    }
  });
}

function showHistory(companyName) {
  if (selectedCompany === companyName) {
    selectedCompany = null;

    if (historyChart) {
      historyChart.destroy();
      historyChart = null;
    }

    render();
    return;
  }

  selectedCompany = companyName;
  render();

  setTimeout(() => {
    renderHistoryStats(companyName);
    renderHistoryChart(companyName);
  }, 0);
}

async function loadDashboard() {
  try {
    const [
      dashboardResponse,
      pricingResponse,
      trendsResponse,
      historyResponse
    ] = await Promise.all([
      fetch("data/dashboard.json", { cache: "no-store" }),
      fetch("data/pricing_rules.json", { cache: "no-store" }),
      fetch("data/trends.json", { cache: "no-store" }),
      fetch("data/history.json", { cache: "no-store" })
    ]);

    dashboardData = await dashboardResponse.json();
    pricingRules = await pricingResponse.json();
    trendsData = await trendsResponse.json();
    historyData = await historyResponse.json();

    initializeUserFees();
    applyDepositMethodDefaults();
    renderFeeSettings();
    render();
  } catch (error) {
    if (companyList) companyList.innerHTML = "";
    console.error(error);
  }
}

if (amountInput) {
  amountInput.addEventListener("input", render);
}

if (depositMethod) {
  depositMethod.addEventListener("change", () => {
    applyDepositMethodDefaults();
    renderFeeSettings();
    render();
  });
}

if (feeSettings) {
  feeSettings.addEventListener("input", (e) => {
    if (e.target.tagName !== "INPUT") return;

    const company = e.target.dataset.company;
    const feeType = e.target.dataset.feeType;

    if (!userFees[company]) return;

    userFees[company][feeType] = Number(e.target.value || 0);
    localStorage.setItem("remittracker_user_fees", JSON.stringify(userFees));

    render();
  });
}

if (resetFees) {
  resetFees.addEventListener("click", () => {
    localStorage.removeItem("remittracker_user_fees");

    userFees = {};
    initializeUserFees();
    applyDepositMethodDefaults();
    renderFeeSettings();
    render();
  });
}

if (refreshData) {
  refreshData.addEventListener("click", async () => {

    refreshData.disabled = true;

    refreshData.style.transform = "rotate(720deg)";
    refreshData.style.transition = "0.8s";

    selectedCompany = null;

    if(historyChart){
        historyChart.destroy();
        historyChart = null;
    }

    await loadDashboard();

    setTimeout(()=>{

        refreshData.style.transform = "rotate(0deg)";
        refreshData.disabled = false;

    },300);

});
}

loadDashboard();