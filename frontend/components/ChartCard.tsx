"use client";

import { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { formatValue } from "@/lib/format";
import type { ChartPoint, ChartWidget, ValueFormat } from "@/lib/types";

// Chart colors. Bars and lines show ONE series, so they use one color.
// Only the "share" chart needs several, always in this fixed order.
const ACCENT = "#2a78d6";
const SHARE_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"];
const INK = "#0b0b0b";
const INK_2 = "#52514e";
const MUTED = "#898781";
const GRID = "#e1e0d9";
const AXIS = "#c3c2b7";
const SURFACE = "#fcfcfb";

type ChartProps = { data: ChartPoint[]; format: ValueFormat };

/** The card around every chart: title, a chart/table switch, and the chart itself. */
export function ChartCard({ chartType, title, data, valueFormat }: ChartWidget) {
  const [showTable, setShowTable] = useState(false);

  return (
    <div className="widget-in min-w-0 rounded-xl border border-line bg-surface p-4">
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-sm font-semibold text-ink">{title}</h3>
        <button
          type="button"
          onClick={() => setShowTable((value) => !value)}
          className="shrink-0 rounded-md border border-line px-2 py-0.5 text-xs text-ink-2 hover:bg-plane"
        >
          {showTable ? "Show chart" : "Show data"}
        </button>
      </div>

      <div className="mt-3">
        {data.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted">No data to show.</p>
        ) : showTable ? (
          <ChartDataTable data={data} format={valueFormat} />
        ) : chartType === "line" ? (
          <LineView data={data} format={valueFormat} />
        ) : chartType === "share" ? (
          <ShareView data={data} format={valueFormat} />
        ) : (
          <BarView data={data} format={valueFormat} />
        )}
      </div>
    </div>
  );
}

/** Line chart: how a value changes over time. */
function LineView({ data, format }: ChartProps) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
        <CartesianGrid vertical={false} stroke={GRID} />
        <XAxis
          dataKey="label"
          tickLine={false}
          axisLine={{ stroke: AXIS }}
          tick={{ fill: MUTED, fontSize: 12 }}
          interval="equidistantPreserveStart"
          minTickGap={4}
        />
        <YAxis
          width={56}
          tickLine={false}
          axisLine={false}
          tick={{ fill: MUTED, fontSize: 12 }}
          tickFormatter={(value: number) => formatValue(value, format, true)}
        />
        <Tooltip content={<ChartTooltip format={format} />} cursor={{ stroke: AXIS }} />
        <Line
          dataKey="value"
          stroke={ACCENT}
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
          dot={data.length <= 12 ? { r: 4, fill: ACCENT, stroke: SURFACE, strokeWidth: 2 } : false}
          activeDot={{ r: 5, fill: ACCENT, stroke: SURFACE, strokeWidth: 2 }}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

/** Horizontal bars: compare categories or show a ranking. Long names stay readable. */
function BarView({ data, format }: ChartProps) {
  const longestLabel = Math.max(...data.map((point) => point.label.length));
  const labelWidth = Math.min(190, Math.max(56, longestLabel * 7 + 12));
  const shorten = (label: string) => (label.length > 26 ? `${label.slice(0, 25)}…` : label);

  return (
    <ResponsiveContainer width="100%" height={data.length * 34 + 16}>
      <BarChart data={data} layout="vertical" margin={{ top: 0, right: 64, bottom: 0, left: 0 }}>
        <XAxis type="number" hide />
        <YAxis
          type="category"
          dataKey="label"
          width={labelWidth}
          tickLine={false}
          axisLine={{ stroke: AXIS }}
          tick={{ fill: INK_2, fontSize: 12 }}
          tickFormatter={shorten}
          interval={0}
        />
        <Tooltip content={<ChartTooltip format={format} />} cursor={{ fill: "rgba(11, 11, 11, 0.04)" }} />
        <Bar dataKey="value" fill={ACCENT} barSize={18} radius={[0, 4, 4, 0]} isAnimationActive={false}>
          <LabelList
            dataKey="value"
            position="right"
            fill={INK}
            fontSize={12}
            formatter={(value) => formatValue(Number(value), format, true)}
          />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

/** Share of a total: one bar split into parts (a clearer cousin of the pie chart). */
function ShareView({ data, format }: ChartProps) {
  // Biggest part first. More than 6 parts are hard to read, so the tail becomes "Other".
  const sorted = [...data].filter((point) => point.value > 0).sort((a, b) => b.value - a.value);
  const parts = sorted.slice(0, sorted.length > 6 ? 5 : 6);
  if (sorted.length > 6) {
    const rest = sorted.slice(5).reduce((sum, point) => sum + point.value, 0);
    parts.push({ label: "Other", value: rest });
  }
  const total = parts.reduce((sum, point) => sum + point.value, 0);
  const percent = (value: number) => `${((value / total) * 100).toFixed(0)}%`;
  const describe = (point: ChartPoint) =>
    `${point.label}: ${formatValue(point.value, format)} (${percent(point.value)})`;

  return (
    <div>
      <div className="flex h-7 gap-0.5" role="img" aria-label={parts.map(describe).join(", ")}>
        {parts.map((point, index) => (
          <div
            key={point.label}
            title={describe(point)}
            className="flex min-w-0 items-center rounded px-1.5 text-xs font-medium"
            style={{
              width: `${(point.value / total) * 100}%`,
              background: SHARE_COLORS[index],
              color: index === 3 ? INK : "#ffffff", // dark text on the yellow part
            }}
          >
            {/* Print the percentage only when the part is wide enough to hold it. */}
            {point.value / total >= 0.08 ? percent(point.value) : ""}
          </div>
        ))}
      </div>

      <ul className="mt-4 space-y-1.5 text-sm">
        {parts.map((point, index) => (
          <li key={point.label} className="flex items-center gap-2">
            <span className="size-2.5 shrink-0 rounded-sm" style={{ background: SHARE_COLORS[index] }} />
            <span className="min-w-0 flex-1 truncate text-ink-2">{point.label}</span>
            <span className="tabular-nums text-ink">{formatValue(point.value, format)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

/** The same data as a plain table, for people who prefer (or need) numbers. */
function ChartDataTable({ data, format }: ChartProps) {
  return (
    <table className="w-full text-sm">
      <tbody>
        {data.map((point) => (
          <tr key={point.label} className="border-b border-grid last:border-0">
            <td className="py-1.5 text-ink-2">{point.label}</td>
            <td className="py-1.5 text-right tabular-nums text-ink">{formatValue(point.value, format)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

/** The little box that follows the mouse. The value is big, the label is small. */
function ChartTooltip({
  active,
  payload,
  label,
  format,
}: {
  active?: boolean;
  payload?: ReadonlyArray<{ value?: unknown }>;
  label?: string | number;
  format: ValueFormat;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-line bg-surface px-3 py-2 shadow-md">
      <div className="text-sm font-semibold text-ink">{formatValue(Number(payload[0].value), format)}</div>
      <div className="text-xs text-ink-2">{label}</div>
    </div>
  );
}
