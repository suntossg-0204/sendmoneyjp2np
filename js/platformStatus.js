import { formatSmartTime } from "./utils.js";

export function renderPlatformStatus(operationsData) {
  if (!operationsData) return;

  const status = operationsData.status || "unknown";
  const collectors = operationsData.collectors || {};
  const pipeline = operationsData.pipeline || {};
  const automation = operationsData.automation || {};

  const statusLabel =
    status === "healthy" ? "Healthy" :
    status === "warning" ? "Partial Issues" :
    "Unknown";

  setText("overviewHealthLabel", statusLabel);
  setText("platformLastRun", formatSmartTime(operationsData.generated_at));
  setText("platformCollectors", `${collectors.success ?? "-"} / ${collectors.total ?? "-"}`);
  setText("platformRuntime", pipeline.duration_seconds ? `${pipeline.duration_seconds}s` : "-");
  setText("platformAutomation", automation.frequency ? "Hourly" : "-");
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}