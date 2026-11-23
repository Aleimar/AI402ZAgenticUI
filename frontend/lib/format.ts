import type { ValueFormat } from "./types";

/**
 * Turn a raw number into text for a chart.
 *   formatValue(961056, "currency")        -> "$961,056"
 *   formatValue(961056, "currency", true)  -> "$961.1K"   (compact, for axes and labels)
 *   formatValue(40.9, "percent")           -> "40.9%"
 */
export function formatValue(value: number, format: ValueFormat, compact = false): string {
  if (format === "percent") {
    return `${value.toLocaleString("en-US", { maximumFractionDigits: 1 })}%`;
  }
  return new Intl.NumberFormat("en-US", {
    style: format === "currency" ? "currency" : "decimal",
    currency: "USD",
    notation: compact ? "compact" : "standard",
    minimumFractionDigits: 0,
    maximumFractionDigits: compact ? 1 : 2,
  }).format(value);
}
