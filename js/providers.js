import { formatJpy, formatTime, formatSmartTime, formatDateTime, getProviderLogo, getProviderHealth, isBusinessRateTime } from "./utils.js";

let historyChart = null;
let selectedCompany = null;
let cachedRender = null;
let cachedHistoryData = null;

export function renderCompanyCards(companies, trendsData, historyData, rerender) {
  cachedRender = rerender;
  cachedHistoryData = historyData;
  const companyList = document.getElementById("companyList");
  if (!companyList) return;

  companyList.innerHTML = companies.map((company, index) => {
    const health = getProviderHealth(company);
    const rank = index === 0 ? "🥇" : index === 1 ? "🥈" : index === 2 ? "🥉" : index + 1;
    const extraCost = company.required_jpy - companies[0].required_jpy;
    const trend = trendsData[company.company_name] || { direction: "same", change: 0 };
    const trendIcon = trend.direction === "up" ? "📈" : trend.direction === "down" ? "📉" : "➖";
    const trendClass = trend.direction === "up" ? "trend-up" : trend.direction === "down" ? "trend-down" : "trend-flat";
    const trendValue = `${trend.direction === "up" ? "+" : trend.direction === "down" ? "-" : ""}${Math.abs(Number(trend.change || 0)).toFixed(4)}`;

    return `
      <div class="company-card ${index === 0 ? "best-card" : ""}">
        <div class="company-main" data-company="${company.company_name}">
          <div class="provider-logo">${getProviderLogo(company.company_name)}<small>${rank}</small></div>
          <div class="company-info">
            <div class="company-name">${company.company_name}</div>
            <div class="company-badges">
              <span class="badge-rate">💱 ${Number(company.rate).toFixed(6)}</span>
              <span class="${trendClass}">${trendIcon} ${trendValue}</span>
              <span class="badge-time">🕒 ${formatSmartTime(company.rate_last_changed || company.collected_at)}</span>
              <span class="badge ${health.className}">${health.icon} ${health.label}</span>
            </div>
          </div>
          <div class="company-result">
            <div class="rate">Total you pay</div>
            <div class="received">${formatJpy(company.required_jpy)}</div>
            ${index === 0 ? `<div class="company-meta best-price">🏆 Best Price</div>` : `<div class="company-meta extra-cost">+${formatJpy(extraCost)} vs Best</div>`}
          </div>
        </div>
        ${selectedCompany === company.company_name ? renderInlineHistory(company.company_name) : ""}
      </div>`;
  }).join("");

  companyList.querySelectorAll(".company-main").forEach(row => {
    row.addEventListener("click", () => showHistory(row.dataset.company));
  });

  if (selectedCompany) {
    setTimeout(() => {
      renderProviderPanel(selectedCompany, companies);
      renderHistoryStats(selectedCompany, historyData);
      renderHistoryChart(selectedCompany, historyData);
    }, 0);
  }
}

function renderInlineHistory(companyName) {
  const safe = companyName.replace(/\s+/g, "-");
  return `
    <div class="provider-panel">
      <div class="provider-panel-header">
        <div class="provider-panel-title">Provider Intelligence</div>
        <div id="panel-health-${safe}"></div>
      </div>

      <div id="panel-summary-${safe}" class="provider-panel-grid"></div>

      <div class="history-inline">
        <div class="history-title">📈 Today's Rate Movement</div>
        <div id="stats-${safe}" class="history-stats"></div>
        <canvas id="chart-${safe}"></canvas>
      </div>
    </div>
  `;
}

function renderProviderPanel(companyName, companies) {
  const company = companies.find(c => c.company_name === companyName);
  if (!company) return;

  const safe = companyName.replace(/\s+/g, "-");
  const summaryBox = document.getElementById(`panel-summary-${safe}`);
  const healthBox = document.getElementById(`panel-health-${safe}`);
  const health = getProviderHealth(company);

  if (healthBox) {
    healthBox.innerHTML = `<span class="badge ${health.className}">${health.icon} ${health.label}</span>`;
  }

  if (!summaryBox) return;

  summaryBox.innerHTML = `
    <div class="provider-panel-item">
      <span>💱 Current Rate</span>
      <strong>${Number(company.rate).toFixed(6)}</strong>
    </div>
    <div class="provider-panel-item">
      <span>💴 Total You Pay</span>
      <strong>${formatJpy(company.required_jpy)}</strong>
    </div>
    <div class="provider-panel-item">
      <span>💳 Service Fee</span>
      <strong>${formatJpy(company.service_fee || 0)}</strong>
    </div>
    <div class="provider-panel-item">
      <span>🏧 Deposit Fee</span>
      <strong>${formatJpy(company.deposit_fee || 0)}</strong>
    </div>
    <div class="provider-panel-item">
      <span>🕒 Last Check</span>
      <strong>${formatSmartTime(company.collected_at)}</strong>
    </div>
    <div class="provider-panel-item">
      <span>📈 Last Rate Change</span>
      <strong>${formatSmartTime(company.rate_last_changed || company.collected_at)}</strong>
    </div>
    <div class="provider-panel-item">
      <span>📅 Exact Check Time</span>
      <strong>${formatDateTime(company.collected_at)}</strong>
    </div>
  `;
}

function showHistory(companyName) {
  selectedCompany = selectedCompany === companyName ? null : companyName;
  if (historyChart) {
    historyChart.destroy();
    historyChart = null;
  }
  if (cachedRender) cachedRender();
}

function getCompanyHistoryRecords(companyName, historyData) {
  return (historyData[companyName] || [])
    .filter(record => isBusinessRateTime(record.collected_at))
    .sort((a, b) => new Date(a.collected_at) - new Date(b.collected_at));
}

function renderHistoryStats(companyName, historyData) {
  const records = getCompanyHistoryRecords(companyName, historyData);
  const statsBox = document.getElementById(`stats-${companyName.replace(/\s+/g, "-")}`);
  if (!statsBox) return;
  if (!records.length) {
    statsBox.innerHTML = `
<div>
    <span>⏳ Waiting</span>
    <strong>More data needed</strong>
</div>`;
    return;
  }
  const rates = records.map(r => Number(r.rate));
  const opening = rates[0];
  const current = rates[rates.length - 1];
  const highest = Math.max(...rates);
  const lowest = Math.min(...rates);
  const change = current - opening;
  const volatility = highest - lowest;
  const changeText = `${change > 0 ? "+" : change < 0 ? "-" : ""}${Math.abs(change).toFixed(4)}`;
  const changeIcon = change > 0 ? "📈" : change < 0 ? "📉" : "➖";
  statsBox.innerHTML = `
    <div><span>Current</span><strong>${current.toFixed(6)}</strong></div>
    <div><span>Opening</span><strong>${opening.toFixed(6)}</strong></div>
    <div><span>Highest</span><strong>${highest.toFixed(6)}</strong></div>
    <div><span>Lowest</span><strong>${lowest.toFixed(6)}</strong></div>
    <div><span>Today's Change</span><strong>${changeIcon} ${changeText}</strong></div>
    <div><span>Volatility</span><strong>${volatility.toFixed(4)}</strong></div>
    <div><span>Updates</span><strong>${records.length}</strong></div>`;
}

function renderHistoryChart(companyName, historyData) {
  const records = getCompanyHistoryRecords(companyName, historyData);
  if (!records.length || typeof Chart === "undefined") return;
  const canvas = document.getElementById(`chart-${companyName.replace(/\s+/g, "-")}`);
  if (!canvas) return;
  if (historyChart) historyChart.destroy();
  const rates = records.map(r => Number(r.rate));
  const isUp = rates[rates.length - 1] >= rates[0];

  const minRate = Math.min(...rates);
  const maxRate = Math.max(...rates);
  const midRate = (minRate + maxRate) / 2;
  const minimumRange = 0.006;
  const actualRange = maxRate - minRate;
  const chartRange = Math.max(actualRange, minimumRange);
  const yMin = Math.max(0, midRate - chartRange / 2);
  const yMax = midRate + chartRange / 2;

  const ctx = canvas.getContext("2d");
  historyChart = new Chart(canvas, {
    type: "line",
    data: {
      labels: records.map(r => formatTime(r.collected_at)),
      datasets: [{
        label: companyName,
        data: rates,
        tension: 0.35,
        fill: true,
        backgroundColor: isUp ? "rgba(22, 163, 74, 0.15)" : "rgba(220, 38, 38, 0.12)",
        borderColor: isUp ? "#16a34a" : "#dc2626",
        borderWidth: 3,
        pointRadius: rates.map((_, i) => i === rates.length - 1 ? 6 : 3),
        pointBackgroundColor: isUp ? "#16a34a" : "#dc2626",
        pointBorderColor: "#ffffff",
        pointBorderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
  x: {
    ticks: {
      maxRotation: 0,
      autoSkip: true,
      maxTicksLimit: 8
    }
  },
  y: {
    min: yMin,
    max: yMax,
    ticks: {
      callback: v => Number(v).toFixed(4)
    }
  }
}
    }
  });
}
