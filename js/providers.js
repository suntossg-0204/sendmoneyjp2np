import {
  formatJpy,
  formatChartLabel,
  formatSmartTime,
  formatDateTime,
  getProviderLogo,
  getProviderHealth,
  isBusinessRateTime
} from "./utils.js";

let historyChart = null;
let selectedCompany = null;
let cachedRender = null;
let cachedHistoryData = null;
let selectedHistoryRange = "today";
let isHistoryOpen = false;

export function renderCompanyCards(
  companies,
  trendsData,
  historyData,
  rerender
) {
  cachedRender = rerender;
  cachedHistoryData = historyData;

  const companyList = document.getElementById("companyList");
  if (!companyList) return;

  companyList.innerHTML = companies
    .map((company, index) => {
      const health = getProviderHealth(company);

      const rank =
        index === 0
          ? "🥇"
          : index === 1
            ? "🥈"
            : index === 2
              ? "🥉"
              : index + 1;

      const extraCost =
        company.required_jpy - companies[0].required_jpy;

      const trend =
        trendsData[company.company_name] || {
          direction: "same",
          change: 0
        };

      const trendIcon =
        trend.direction === "up"
          ? "📈"
          : trend.direction === "down"
            ? "📉"
            : "➖";

      const trendClass =
        trend.direction === "up"
          ? "trend-up"
          : trend.direction === "down"
            ? "trend-down"
            : "trend-flat";

      const trendValue =
        `${trend.direction === "up" ? "+" : trend.direction === "down" ? "-" : ""}` +
        `${Math.abs(Number(trend.change || 0)).toFixed(4)}`;

      return `
        <div class="company-card ${index === 0 ? "best-card" : ""}">
          <div class="company-main" data-company="${company.company_name}">
            <div class="provider-logo">
              ${getProviderLogo(company.company_name)}
              <small>${rank}</small>
            </div>

            <div class="company-info">
              <div class="company-name">${company.company_name}</div>

              <div class="company-badges">
                <span class="badge-rate">
                  💱 ${Number(company.rate).toFixed(6)}
                </span>

                <span class="${trendClass}">
                  ${trendIcon} ${trendValue}
                </span>

                <span class="badge-time">
                  🕒 ${formatSmartTime(
                    company.rate_last_changed || company.collected_at
                  )}
                </span>

                <span class="badge ${health.className}">
                  ${health.icon} ${health.label}
                </span>
              </div>
            </div>

            <div class="company-result">
              <div class="rate">Total you pay</div>
              <div class="received">
                ${formatJpy(company.required_jpy)}
              </div>

              ${
                index === 0
                  ? `<div class="company-meta best-price">🏆 Best Price</div>`
                  : `<div class="company-meta extra-cost">
                       +${formatJpy(extraCost)} vs Best
                     </div>`
              }
            </div>
          </div>

          ${
            selectedCompany === company.company_name
              ? renderInlineHistory(company.company_name)
              : ""
          }
        </div>
      `;
    })
    .join("");

  companyList.querySelectorAll(".company-main").forEach(row => {
    row.addEventListener("click", () => {
      showHistory(row.dataset.company);
    });
  });

  if (selectedCompany) {
    setTimeout(() => {
      renderProviderPanel(
        selectedCompany,
        companies,
        historyData
      );

      renderHistoryControls(selectedCompany);
      renderHistoryStats(selectedCompany, historyData);
      renderHistoryChart(selectedCompany, historyData);
      bindHistoryOpenState(selectedCompany);
    }, 0);
  }
}

function renderInlineHistory(companyName) {
  const safe = companyName.replace(/\s+/g, "-");

  return `
    <div class="provider-panel">
      <div class="provider-panel-header">
        <div class="provider-panel-title">
          Provider Intelligence
        </div>

        <div id="panel-health-${safe}"></div>
      </div>

      <div
        id="panel-summary-${safe}"
        class="provider-panel-grid"
      ></div>

      <div
        id="rate-timeline-${safe}"
        class="rate-timeline"
      ></div>

      <details
        class="history-inline"
        ${isHistoryOpen ? "open" : ""}
      >
        <summary
          id="history-title-${safe}"
          class="history-title"
        >
          📈 <strong>Rate Trend</strong>
        </summary>

        <div
          id="history-controls-${safe}"
          class="history-controls"
        ></div>

        <div
          id="stats-${safe}"
          class="history-stats"
        ></div>

        <canvas id="chart-${safe}"></canvas>
      </details>
    </div>
  `;
}

function renderProviderPanel(
  companyName,
  companies,
  historyData
) {
  const company = companies.find(
    item => item.company_name === companyName
  );

  if (!company) return;

  const safe = companyName.replace(/\s+/g, "-");

  const summaryBox = document.getElementById(
    `panel-summary-${safe}`
  );

  const healthBox = document.getElementById(
    `panel-health-${safe}`
  );

  const health = getProviderHealth(company);

  if (healthBox) {
    healthBox.innerHTML = `
      <span class="badge ${health.className}">
        ${health.icon} ${health.label}
      </span>
    `;
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
      <strong>
        ${formatSmartTime(company.collected_at)}
      </strong>
    </div>

    <div class="provider-panel-item">
      <span>📈 Last Rate Change</span>
      <strong>
        ${formatSmartTime(
          company.rate_last_changed || company.collected_at
        )}
      </strong>
    </div>

    <div class="provider-panel-item">
      <span>📅 Exact Check Time</span>
      <strong>
        ${formatDateTime(company.collected_at)}
      </strong>
    </div>
  `;

  renderRateTimeline(companyName, historyData);
}

function renderRateTimeline(companyName, historyData) {
  const safe = companyName.replace(/\s+/g, "-");

  const timelineBox = document.getElementById(
    `rate-timeline-${safe}`
  );

  if (!timelineBox) return;

  const records = (historyData[companyName] || [])
    .map(record => ({
      rate: Number(record.rate),
      collected_at: record.collected_at
    }))
    .filter(record => Number.isFinite(record.rate))
    .sort(
      (a, b) =>
        new Date(a.collected_at) -
        new Date(b.collected_at)
    );

  const changes = [];

  for (const record of records) {
    const previous = changes[changes.length - 1];

    if (!previous || previous.rate !== record.rate) {
      changes.push(record);
    }
  }

  const recentChanges = changes.slice(-6).reverse();

  if (!recentChanges.length) {
    timelineBox.innerHTML = "";
    return;
  }

  timelineBox.innerHTML = `
    <div class="rate-timeline-title">
      📈 Rate Activity
    </div>

    <div class="rate-activity-list">
      ${recentChanges
        .map((change, index) => {
          const previous = recentChanges[index + 1];

          const difference = previous
            ? change.rate - previous.rate
            : 0;

          const direction =
            difference > 0
              ? "up"
              : difference < 0
                ? "down"
                : "flat";

          const symbol =
            difference > 0
              ? "▲"
              : difference < 0
                ? "▼"
                : "—";

          const differenceText = previous
            ? `${difference > 0 ? "+" : ""}${difference.toFixed(6)}`
            : "Initial";

          return `
            <div class="rate-activity-item ${direction}">
              <div class="rate-activity-marker">
                ${symbol}
              </div>

              <div class="rate-activity-content">
                <div class="rate-activity-main">
                  <strong>
                    ${change.rate.toFixed(6)}
                  </strong>

                  <span class="rate-activity-change">
                    ${differenceText}
                  </span>
                </div>

                <div class="rate-activity-time">
                  ${formatSmartTime(change.collected_at)}
                </div>
              </div>
            </div>
          `;
        })
        .join("")}
    </div>
  `;
}

function showHistory(companyName) {
  const isClosing = selectedCompany === companyName;

  selectedCompany = isClosing ? null : companyName;

  if (isClosing) {
    isHistoryOpen = false;
  }

  if (historyChart) {
    historyChart.destroy();
    historyChart = null;
  }

  if (cachedRender) {
    cachedRender();
  }
}

function getCompanyHistoryRecords(
  companyName,
  historyData
) {
  const now = new Date();

  return (historyData[companyName] || [])
    .filter(record => {
      const date = new Date(
        `${record.collected_at}+09:00`
      );

      if (selectedHistoryRange === "today") {
        return isBusinessRateTime(
          record.collected_at
        );
      }

      const differenceDays =
        (now - date) / 1000 / 60 / 60 / 24;

      if (selectedHistoryRange === "7d") {
        return differenceDays <= 7;
      }

      if (selectedHistoryRange === "30d") {
        return differenceDays <= 30;
      }

      return true;
    })
    .sort(
      (a, b) =>
        new Date(a.collected_at) -
        new Date(b.collected_at)
    );
}

function bindHistoryOpenState(companyName) {
  const safe = companyName.replace(/\s+/g, "-");

  const title = document.getElementById(
    `history-title-${safe}`
  );

  const details = title?.closest("details.history-inline");

  if (!details) return;

  details.addEventListener("toggle", () => {
    isHistoryOpen = details.open;

    if (details.open) {
      renderHistoryChart(
        companyName,
        cachedHistoryData
      );
    }
  });
}

function renderHistoryControls(companyName) {
  const safe = companyName.replace(/\s+/g, "-");

  const controls = document.getElementById(
    `history-controls-${safe}`
  );

  if (!controls) return;

  const title = document.getElementById(
    `history-title-${safe}`
  );

  if (title) {
    const titleMap = {
      today:
        '📈 <strong>Rate Trend</strong> — Today',
      "7d":
        '📈 <strong>Rate Trend</strong> — 7D',
      "30d":
        '📈 <strong>Rate Trend</strong> — 30D'
    };

    title.innerHTML =
      titleMap[selectedHistoryRange] ||
      '📈 <strong>Rate Trend</strong>';
  }

  const ranges = [
    { key: "today", label: "Today" },
    { key: "7d", label: "7D" },
    { key: "30d", label: "30D" }
  ];

  controls.innerHTML = ranges
    .map(
      range => `
        <button
          class="history-range-btn ${
            selectedHistoryRange === range.key
              ? "active"
              : ""
          }"
          data-range="${range.key}"
          type="button"
        >
          ${range.label}
        </button>
      `
    )
    .join("");

  controls
    .querySelectorAll(".history-range-btn")
    .forEach(button => {
      button.addEventListener(
        "click",
        event => {
          event.preventDefault();
          event.stopPropagation();

          selectedHistoryRange =
            button.dataset.range;

          isHistoryOpen = true;

          renderHistoryControls(companyName);
          renderHistoryStats(
            companyName,
            cachedHistoryData
          );
          renderHistoryChart(
            companyName,
            cachedHistoryData
          );
        }
      );
    });
}

function renderHistoryStats(
  companyName,
  historyData
) {
  const records = getCompanyHistoryRecords(
    companyName,
    historyData
  );

  const safe = companyName.replace(/\s+/g, "-");

  const statsBox = document.getElementById(
    `stats-${safe}`
  );

  if (!statsBox) return;

  if (!records.length) {
    statsBox.innerHTML = `
      <div>
        <span>⏳ Waiting</span>
        <strong>More data needed</strong>
      </div>
    `;
    return;
  }

  const rates = records.map(record =>
    Number(record.rate)
  );

  const opening = rates[0];
  const current = rates[rates.length - 1];
  const highest = Math.max(...rates);
  const lowest = Math.min(...rates);
  const todayChange = current - opening;
  const volatility = highest - lowest;

  let changeIcon = "—";
  let changeClass = "neutral";

  if (todayChange > 0) {
    changeIcon = "▲";
    changeClass = "positive";
  } else if (todayChange < 0) {
    changeIcon = "▼";
    changeClass = "negative";
  }

  const sign = todayChange > 0 ? "+" : "";

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

      <strong class="history-change ${changeClass}">
        ${changeIcon} ${sign}${todayChange.toFixed(4)}
      </strong>
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

function renderHistoryChart(
  companyName,
  historyData
) {
  const records = getCompanyHistoryRecords(
    companyName,
    historyData
  );

  if (
    !records.length ||
    typeof Chart === "undefined"
  ) {
    return;
  }

  const safe = companyName.replace(/\s+/g, "-");

  const canvas = document.getElementById(
    `chart-${safe}`
  );

  if (!canvas) return;

  if (historyChart) {
    historyChart.destroy();
  }

  const rates = records.map(record =>
    Number(record.rate)
  );

  const isUp =
    rates[rates.length - 1] >= rates[0];

  const minimumRate = Math.min(...rates);
  const maximumRate = Math.max(...rates);
  const middleRate =
    (minimumRate + maximumRate) / 2;

  const minimumRange = 0.006;
  const actualRange =
    maximumRate - minimumRate;

  const chartRange = Math.max(
    actualRange,
    minimumRange
  );

  const yMin = Math.max(
    0,
    middleRate - chartRange / 2
  );

  const yMax =
    middleRate + chartRange / 2;

  const labels = [];
  let previousLabel = "";

  for (const record of records) {
    const label = formatChartLabel(
      record.collected_at,
      selectedHistoryRange
    );

    if (selectedHistoryRange === "today") {
      labels.push(label);
      continue;
    }

    if (label === previousLabel) {
      labels.push("");
    } else {
      labels.push(label);
      previousLabel = label;
    }
  }

  historyChart = new Chart(canvas, {
    type: "line",

    data: {
      labels,

      datasets: [
        {
          label: companyName,
          data: rates,
          tension: 0.35,
          fill: true,

          backgroundColor: isUp
            ? "rgba(22, 163, 74, 0.15)"
            : "rgba(220, 38, 38, 0.12)",

          borderColor: isUp
            ? "#16a34a"
            : "#dc2626",

          borderWidth: 3,

          pointRadius: rates.map(
            (_, index) =>
              index === rates.length - 1
                ? 6
                : 3
          ),

          pointBackgroundColor: isUp
            ? "#16a34a"
            : "#dc2626",

          pointBorderColor: "#ffffff",
          pointBorderWidth: 2
        }
      ]
    },

    options: {
      responsive: true,
      maintainAspectRatio: false,

      plugins: {
        legend: {
          display: false
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
          min: yMin,
          max: yMax,

          ticks: {
            callback: value =>
              Number(value).toFixed(4)
          }
        }
      }
    }
  });
}