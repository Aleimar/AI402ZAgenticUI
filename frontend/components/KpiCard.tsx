import type { KpiWidget } from "@/lib/types";

/** One headline number, e.g. "Revenue 2025 - $961K - +22.6% vs 2024". */
export function KpiCard({ label, value, caption }: KpiWidget) {
  return (
    <div className="widget-in rounded-xl border border-line bg-surface p-4">
      <div className="text-sm text-ink-2">{label}</div>
      <div className="mt-1 text-3xl font-semibold text-ink">{value}</div>
      {caption && <div className="mt-1 text-sm text-ink-2">{caption}</div>}
    </div>
  );
}
