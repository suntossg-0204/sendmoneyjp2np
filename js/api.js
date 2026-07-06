export async function loadData() {
  const [dashboardResponse, pricingResponse, trendsResponse, historyResponse, analyticsResponse] = await Promise.all([
    fetch("data/dashboard.json", { cache: "no-store" }),
    fetch("data/pricing_rules.json", { cache: "no-store" }),
    fetch("data/trends.json", { cache: "no-store" }),
    fetch("data/history.json", { cache: "no-store" }),
    fetch("data/analytics.json", { cache: "no-store" })
  ]);

  return {
    dashboardData: await dashboardResponse.json(),
    pricingRules: await pricingResponse.json(),
    trendsData: await trendsResponse.json(),
    historyData: await historyResponse.json(),
    analyticsData: await analyticsResponse.json()
  };
}
