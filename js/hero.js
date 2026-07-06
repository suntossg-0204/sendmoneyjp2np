import { formatJpy, formatNpr, formatRelativeTime, getProviderLogo } from "./utils.js";

export function renderHero({ analyticsData, companies, targetNpr }) {
  if (!analyticsData || !companies?.length) return;

  const best = companies[0];
  const second = companies[1];
  const saving = second ? second.required_jpy - best.required_jpy : 0;
  const market = analyticsData.market || {};
  const health = analyticsData.collector_health || {};

  setText("overviewBestValue", best.company_name);
  setText("overviewBestCost", formatJpy(best.required_jpy));
  setText("overviewReceiveAmount", formatNpr(targetNpr));
  setText("overviewUpdated", formatRelativeTime(best.collected_at));
  setHTML("overviewBestLogo", getProviderLogo(best.company_name));

  const savings = document.getElementById("overviewSavings");
  if (savings) {
    savings.textContent = second ? `💰 You save ${formatJpy(saving)} vs ${second.company_name}` : "";
    savings.style.display = second ? "inline-flex" : "none";
  }

  setText("overviewHighestRate", market.highest_rate ? Number(market.highest_rate).toFixed(6) : "-");
  setText("overviewAverageRate", market.average_rate ? Number(market.average_rate).toFixed(6) : "-");

  const low = Number(market.lowest_rate || 0);
  const high = Number(market.highest_rate || 0);
  const spreadPercent = low ? ((high - low) / low) * 100 : 0;
  setText("overviewSpread", `${spreadPercent.toFixed(2)}%`);

  const success = health.success ?? "-";
  const total = health.total ?? "-";
  setText("overviewCollectors", `${success} / ${total}`);
  setText("overviewHealthLabel", Number(success) === Number(total) ? "Healthy" : "Check");
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}
function setHTML(id, value) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = value;
}
