// The shape of everything that can appear on the dashboard.

export type ChartPoint = { label: string; value: number };
export type ChartType = "bar" | "line" | "share";
export type ValueFormat = "number" | "currency" | "percent";

export type KpiWidget = {
  id: string;
  kind: "kpi";
  label: string;
  value: string;
  caption?: string;
};

export type ChartWidget = {
  id: string;
  kind: "chart";
  chartType: ChartType;
  title: string;
  data: ChartPoint[];
  valueFormat: ValueFormat;
};

export type TableWidget = {
  id: string;
  kind: "table";
  title: string;
  columns: string[];
  rows: string[][];
};

export type Widget = KpiWidget | ChartWidget | TableWidget;

export type DashboardState = {
  title: string;
  subtitle?: string;
  widgets: Widget[];
};
