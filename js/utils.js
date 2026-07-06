import { PROVIDER_LOGOS, DISPLAY_CONFIG } from "./config.js";

export function formatJpy(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "¥0";
  return `¥${Math.ceil(number).toLocaleString()}`;
}

export function formatNpr(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "रु0";
  return `रु${Math.ceil(number).toLocaleString()}`;
}

export function formatDateTime(value) {
  if (!value) return "-";
  const date = new Date(value + "+09:00");
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  const h = String(date.getHours()).padStart(2, "0");
  const min = String(date.getMinutes()).padStart(2, "0");
  return `${y}/${m}/${d} ${h}:${min} JST`;
}

export function formatRelativeTime(value) {
  if (!value) return "-";
  const date = new Date(value + "+09:00");
  const now = new Date();
  const diffMinutes = Math.max(0, Math.round((now - date) / 1000 / 60));
  if (diffMinutes < 1) return "just now";
  if (diffMinutes < 60) return `${diffMinutes} min ago`;
  const diffHours = Math.round(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours} hr ago`;
  return formatDateTime(value);
}

export function formatTime(value) {
  if (!value) return "-";
  const date = new Date(value + "+09:00");
  return date.toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit", hour12: false });
}

export function getProviderLogo(companyName) {
  const logoEntry = PROVIDER_LOGOS[companyName];
  const fallback = companyName.substring(0, 2).toUpperCase();

  if (!logoEntry) {
    return `<div class="logo-fallback">${fallback}</div>`;
  }

  const paths = Array.isArray(logoEntry) ? logoEntry : [logoEntry];
  const [primary, secondary] = paths;

  const onError = secondary
    ? `this.onerror=function(){this.outerHTML='<div class=&quot;logo-fallback&quot;>${fallback}</div>'};this.src='${secondary}'`
    : `this.outerHTML='<div class=&quot;logo-fallback&quot;>${fallback}</div>'`;

  return `<img class="provider-logo-image" src="${primary}" alt="${companyName}" onerror="${onError}">`;
}

export function getProviderHealth(company) {
  if (company.rate_status === "fresh" && company.health_status === "success") {
    return { label: "LIVE", className: "good", icon: "●" };
  }
  if (company.rate_status === "stale" || company.health_status === "failed") {
    return { label: "STALE", className: "warn", icon: "●" };
  }
  return { label: "UNKNOWN", className: "bad", icon: "●" };
}

export function isBusinessRateTime(value) {
  if (!value) return false;
  const date = new Date(value + "+09:00");
  const now = new Date();
  const isToday = date.getFullYear() === now.getFullYear() && date.getMonth() === now.getMonth() && date.getDate() === now.getDate();
  const isOperatingHour = date.getHours() >= DISPLAY_CONFIG.businessStartHour && date.getHours() < DISPLAY_CONFIG.businessEndHour;
  return isToday && isOperatingHour;
}
