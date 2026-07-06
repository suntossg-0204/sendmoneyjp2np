import { isBusinessRateTime } from "./utils.js";

export function renderMarket(companies) {
  const marketHigh = document.getElementById("marketHigh");
  const marketLow = document.getElementById("marketLow");
  const marketAverage = document.getElementById("marketAverage");
  const marketSpread = document.getElementById("marketSpread");
  if (!marketHigh || !marketLow || !marketAverage || !marketSpread) return;

  const rates = companies.map(c => Number(c.rate)).filter(Number.isFinite);
  if (!rates.length) return;

  const highestCompany = companies.reduce((a, b) => Number(a.rate) > Number(b.rate) ? a : b);
  const lowestCompany = companies.reduce((a, b) => Number(a.rate) < Number(b.rate) ? a : b);
  const highest = Number(highestCompany.rate);
  const lowest = Number(lowestCompany.rate);
  const average = rates.reduce((a, b) => a + b, 0) / rates.length;
  const spread = lowest ? ((highest - lowest) / lowest) * 100 : 0;

  marketHigh.textContent = highest.toFixed(6);
  marketLow.textContent = lowest.toFixed(6);
  marketAverage.textContent = average.toFixed(6);
  marketSpread.textContent = `${spread.toFixed(2)}%`;

  const highLabel = document.getElementById("marketHighCompany");
  const lowLabel = document.getElementById("marketLowCompany");
  if (highLabel) highLabel.textContent = `🏆 ${highestCompany.company_name}`;
  if (lowLabel) lowLabel.textContent = `📉 ${lowestCompany.company_name}`;
}

export function renderMarketIntelligence(companies, historyData) {
  const box = document.getElementById("marketIntelligence");
  if (!box) return;

  const insights = companies.map(company => {
    const records = (historyData[company.company_name] || [])
      .filter(record => isBusinessRateTime(record.collected_at))
      .sort((a, b) => new Date(a.collected_at) - new Date(b.collected_at));
    const rates = records.map(r => Number(r.rate));
    if (rates.length < 2) return { company_name: company.company_name, change: 0, volatility: 0 };
    return {
      company_name: company.company_name,
      change: rates[rates.length - 1] - rates[0],
      volatility: Math.max(...rates) - Math.min(...rates)
    };
  });

  const biggestGainer = [...insights].sort((a, b) => b.change - a.change)[0];
  const biggestLoser = [...insights].sort((a, b) => a.change - b.change)[0];
  const mostVolatile = [...insights].sort((a, b) => b.volatility - a.volatility)[0];
  const improvingCount = insights.filter(i => i.change > 0).length;

  box.innerHTML = `
    <div class="intelligence-item"><span>🏆 Leader Today</span><strong>${companies[0].company_name}</strong></div>
    <div class="intelligence-item"><span>📈 Biggest Gainer</span><strong>${biggestGainer.company_name}<br>+${biggestGainer.change.toFixed(4)}</strong></div>
    <div class="intelligence-item"><span>📉 Biggest Loser</span><strong>${biggestLoser.company_name}<br>${biggestLoser.change.toFixed(4)}</strong></div>
    <div class="intelligence-item"><span>🔥 Most Volatile</span><strong>${mostVolatile.company_name}<br>${mostVolatile.volatility.toFixed(4)}</strong></div>
    <div class="intelligence-item"><span>🟢 Improving</span><strong>${improvingCount}/${insights.length}</strong></div>`;
}
