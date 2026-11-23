import { ChartCard } from "@/components/ChartCard";
import { DataTable } from "@/components/DataTable";
import { KpiCard } from "@/components/KpiCard";
import type { ChartWidget, DashboardState, KpiWidget, TableWidget } from "@/lib/types";

/** The canvas on the left. It draws whatever the agent has put into `dashboard`. */
export function Dashboard({ dashboard }: { dashboard: DashboardState | null }) {
  if (!dashboard) return <EmptyState />;

  // Group the components so the layout is always: numbers, then charts, then tables.
  const kpis = dashboard.widgets.filter((widget): widget is KpiWidget => widget.kind === "kpi");
  const charts = dashboard.widgets.filter((widget): widget is ChartWidget => widget.kind === "chart");
  const tables = dashboard.widgets.filter((widget): widget is TableWidget => widget.kind === "table");

  return (
    <div className="mx-auto max-w-5xl space-y-4 p-6">
      <header className="widget-in">
        <h1 className="text-2xl font-semibold text-ink">{dashboard.title}</h1>
        {dashboard.subtitle && <p className="mt-1 text-sm text-ink-2">{dashboard.subtitle}</p>}
      </header>

      {kpis.length > 0 && (
        <section className="grid grid-cols-[repeat(auto-fit,minmax(180px,1fr))] gap-4">
          {kpis.map((widget) => (
            <KpiCard key={widget.id} {...widget} />
          ))}
        </section>
      )}

      {charts.length > 0 && (
        <section className={`grid items-start gap-4 ${charts.length > 1 ? "lg:grid-cols-2" : ""}`}>
          {charts.map((widget) => (
            <ChartCard key={widget.id} {...widget} />
          ))}
        </section>
      )}

      {tables.map((widget) => (
        <DataTable key={widget.id} {...widget} />
      ))}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex h-full items-center justify-center p-6">
      <div className="max-w-md text-center">
        <div className="mx-auto flex size-12 items-center justify-center rounded-xl border border-line bg-surface text-2xl">
          📊
        </div>
        <h1 className="mt-4 text-xl font-semibold text-ink">Your dashboard will appear here</h1>
        <p className="mt-2 text-sm text-ink-2">
          Ask a question about BrightCart sales in the chat. The agent will query the database and
          then build this page for you, one component at a time.
        </p>
      </div>
    </div>
  );
}
