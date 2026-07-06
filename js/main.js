import { loadData } from "./api.js";
import { calculateCompanyCost } from "./pricing.js";
import { initializeUserFees, applyDepositMethodDefaults, renderFeeSettings } from "./fees.js";
import { renderHero } from "./hero.js";
import { renderMarket, renderMarketIntelligence } from "./market.js";
import { renderCompanyCards } from "./providers.js";
import { formatDateTime } from "./utils.js";
import { initializeTheme } from "./theme.js";

const amountInput = document.getElementById("amountInput");
const depositMethod = document.getElementById("depositMethod");
const feeSettings = document.getElementById("feeSettings");
const resetFees = document.getElementById("resetFees");
const refreshData = document.getElementById("refreshData");
const headerLastUpdated = document.getElementById("headerLastUpdated");

let dashboardData = null;
let analyticsData = null;
let pricingRules = {};
let trendsData = {};
let historyData = {};
let userFees = {};

function getTargetNpr() {
  return Number(amountInput?.value || 0);
}

async function bootstrap() {
  try {
    const data = await loadData();
    dashboardData = data.dashboardData;
    pricingRules = data.pricingRules;
    trendsData = data.trendsData;
    historyData = data.historyData;
    analyticsData = data.analyticsData;

    userFees = initializeUserFees(dashboardData, pricingRules, getTargetNpr());
    userFees = applyDepositMethodDefaults(dashboardData, userFees, depositMethod?.value || "bank_transfer");
    renderFeeSettings({ feeSettings, dashboardData, pricingRules, userFees, targetNpr: getTargetNpr() });
    render();
  } catch (error) {
    console.error(error);
    const companyList = document.getElementById("companyList");
    if (companyList) companyList.innerHTML = `<div class="error-card">Could not load dashboard data. Check JSON files and console.</div>`;
  }
}

function getCalculatedCompanies() {
  return dashboardData.companies
    .map(company => calculateCompanyCost(company, getTargetNpr(), pricingRules, userFees))
    .sort((a, b) => a.required_jpy - b.required_jpy);
}

function render() {
  if (!dashboardData) return;
  const companies = getCalculatedCompanies();
  renderHero({ analyticsData, companies, targetNpr: getTargetNpr() });
  renderMarket(companies);
  renderMarketIntelligence(companies, historyData);
  renderCompanyCards(companies, trendsData, historyData, render);
  if (headerLastUpdated) headerLastUpdated.textContent = formatDateTime(dashboardData.last_updated);
}

amountInput?.addEventListener("input", () => {
  renderFeeSettings({ feeSettings, dashboardData, pricingRules, userFees, targetNpr: getTargetNpr() });
  render();
});

depositMethod?.addEventListener("change", () => {
  userFees = applyDepositMethodDefaults(dashboardData, userFees, depositMethod.value);
  renderFeeSettings({ feeSettings, dashboardData, pricingRules, userFees, targetNpr: getTargetNpr() });
  render();
});

feeSettings?.addEventListener("input", (e) => {
  if (e.target.tagName !== "INPUT") return;
  const company = e.target.dataset.company;
  const feeType = e.target.dataset.feeType;
  if (!userFees[company]) return;
  userFees[company][feeType] = Number(e.target.value || 0);
  if (feeType === "service_fee") userFees[company].service_fee_manually_changed = true;
  localStorage.setItem("remittracker_user_fees", JSON.stringify(userFees));
  render();
});

resetFees?.addEventListener("click", () => {
  localStorage.removeItem("remittracker_user_fees");
  userFees = initializeUserFees(dashboardData, pricingRules, getTargetNpr());
  userFees = applyDepositMethodDefaults(dashboardData, userFees, depositMethod?.value || "bank_transfer");
  renderFeeSettings({ feeSettings, dashboardData, pricingRules, userFees, targetNpr: getTargetNpr() });
  render();
});

refreshData?.addEventListener("click", async () => {
  refreshData.disabled = true;
  refreshData.style.transform = "rotate(720deg)";
  refreshData.style.transition = "0.8s";
  await bootstrap();
  setTimeout(() => {
    refreshData.style.transform = "rotate(0deg)";
    refreshData.disabled = false;
  }, 300);
});

initializeTheme();
bootstrap();
