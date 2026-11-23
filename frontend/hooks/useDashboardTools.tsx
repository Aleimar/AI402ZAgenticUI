"use client";

// ============================================================================
//  UI AS TOOLS  -  the most important file of this tutorial
// ============================================================================
//
// A "tool" is a function that the LLM is allowed to call. Normally tools live
// on the server (see backend/tools.py). The tools in THIS file live in the
// browser: each one puts a React component on the screen.
//
// useFrontendTool({...}) does two things:
//   1. It tells the agent that the tool exists: its name, its description and
//      its parameters. The agent sees it exactly like a Python tool.
//   2. When the agent calls the tool, CopilotKit runs `handler` right here in
//      the browser, with the arguments the LLM chose.
//
// So "the agent builds a dashboard" really means: the LLM decides WHICH
// components to show and WITH WHAT data, and our React code decides HOW they look.

import { ToolCallStatus, useFrontendTool, useRenderTool } from "@copilotkit/react-core/v2";
import type { Dispatch, SetStateAction } from "react";
import { z } from "zod";

import { SqlChip, ToolChip } from "@/components/ToolChip";
import type { DashboardState, Widget } from "@/lib/types";

type SetDashboard = Dispatch<SetStateAction<DashboardState | null>>;

/** Add one component to the dashboard (starting a dashboard if there is none yet). */
function addWidget(setDashboard: SetDashboard, widget: Widget) {
  setDashboard((current) => {
    const dashboard = current ?? { title: "Dashboard", widgets: [] };
    // If the same tool call arrives twice, replace the component instead of duplicating it.
    const others = dashboard.widgets.filter((existing) => existing.id !== widget.id);
    return { ...dashboard, widgets: [...others, widget] };
  });
}

export function useDashboardTools(setDashboard: SetDashboard) {
  // --------------------------------------------------------------------------
  // Tool 1: create_dashboard  ->  clears the page and sets the title
  // --------------------------------------------------------------------------
  useFrontendTool(
    {
      name: "create_dashboard",
      description:
        "Start a new, empty dashboard on the user's screen. Removes everything that was shown before. " +
        "Call this first whenever the user asks a new question.",
      // `parameters` is a Zod schema. The LLM must send arguments that match it,
      // and every .describe() text is shown to the LLM as a hint.
      parameters: z.object({
        title: z.string().describe("Short title, e.g. 'Sales by Region, 2025'"),
        subtitle: z.string().optional().describe("One short line saying what the dashboard covers"),
      }),
      // `handler` runs in the browser when the agent calls the tool.
      // Whatever it returns is sent back to the agent as the tool result.
      handler: async ({ title, subtitle }) => {
        setDashboard({ title, subtitle, widgets: [] });
        return "Empty dashboard created. Now add components to it.";
      },
      // `render` draws a small status line in the chat for this tool call.
      render: ({ args, status }) => (
        <ToolChip done={status === ToolCallStatus.Complete}>New dashboard · {args.title}</ToolChip>
      ),
    },
    [],
  );

  // --------------------------------------------------------------------------
  // Tool 2: add_kpi_card  ->  <KpiCard />
  // --------------------------------------------------------------------------
  useFrontendTool(
    {
      name: "add_kpi_card",
      description:
        "Add a KPI card to the dashboard: one big headline number with a label. " +
        "Use it for totals, averages and growth rates.",
      parameters: z.object({
        label: z.string().describe("What the number is, e.g. 'Total revenue'"),
        value: z.string().describe("The number, already formatted for people, e.g. '$1.2M' or '12.5%'"),
        caption: z.string().optional().describe("Optional context, e.g. '+22.6% vs 2024'"),
      }),
      handler: async ({ label, value, caption }, { toolCall }) => {
        addWidget(setDashboard, { id: toolCall.id, kind: "kpi", label, value, caption });
        return `KPI card "${label}" is now on the dashboard.`;
      },
      render: ({ args, status }) => (
        <ToolChip done={status === ToolCallStatus.Complete}>KPI card · {args.label}</ToolChip>
      ),
    },
    [],
  );

  // --------------------------------------------------------------------------
  // Tool 3: add_chart  ->  <ChartCard />
  // --------------------------------------------------------------------------
  useFrontendTool(
    {
      name: "add_chart",
      description:
        "Add a chart to the dashboard. chart_type 'line' shows a trend over time (labels are dates or months, oldest first). " +
        "'bar' compares categories or shows a ranking (biggest first, 12 bars at most). " +
        "'share' shows how one total splits into parts, like a pie chart (6 parts at most).",
      parameters: z.object({
        chart_type: z.enum(["bar", "line", "share"]),
        title: z.string().describe("Chart title that names the measure, e.g. 'Monthly revenue, 2025'"),
        data: z
          .array(
            z.object({
              label: z.string().describe("Short category or date label, e.g. 'West' or '2025-03'"),
              value: z.number().describe("The plain number, e.g. 335318.5 (no $ sign, no commas)"),
            }),
          )
          .describe("The data points to plot, copied from a SQL result"),
        value_format: z
          .enum(["number", "currency", "percent"])
          .optional()
          .describe("How to print the values: 'currency' adds $, 'percent' adds %. Default 'number'."),
      }),
      handler: async ({ chart_type, title, data, value_format }, { toolCall }) => {
        // Never trust LLM output blindly: tidy the arguments before using them.
        // (A model may say "pie" although we asked for "share", or send "1200" as text.)
        const requested: string = chart_type;
        const chartType = requested === "line" ? "line" : requested === "share" || requested === "pie" ? "share" : "bar";
        const points = (data ?? []).map((point) => ({
          label: String(point.label),
          value: Number(point.value) || 0,
        }));
        addWidget(setDashboard, {
          id: toolCall.id,
          kind: "chart",
          chartType,
          title,
          data: points,
          valueFormat: value_format ?? "number",
        });
        return `${chartType} chart "${title}" with ${points.length} data points is now on the dashboard.`;
      },
      render: ({ args, status }) => (
        <ToolChip done={status === ToolCallStatus.Complete}>
          {args.chart_type ?? "…"} chart · {args.title}
        </ToolChip>
      ),
    },
    [],
  );

  // --------------------------------------------------------------------------
  // Tool 4: add_table  ->  <DataTable />
  // --------------------------------------------------------------------------
  useFrontendTool(
    {
      name: "add_table",
      description:
        "Add a table to the dashboard, for when the exact figures matter. Keep it to 10 rows at most.",
      parameters: z.object({
        title: z.string().describe("Table title"),
        columns: z.array(z.string()).describe("Column headers, e.g. ['Product', 'Units', 'Revenue']"),
        rows: z
          .array(z.array(z.string()))
          .describe("One array per row, with one text value per column, e.g. [['Yoga Mat', '412', '$13,184']]"),
      }),
      handler: async ({ title, columns, rows }, { toolCall }) => {
        // Make sure every cell is text, even if the model sent a number.
        const textRows = (rows ?? []).map((row) => row.map((cell) => String(cell ?? "")));
        addWidget(setDashboard, { id: toolCall.id, kind: "table", title, columns: columns ?? [], rows: textRows });
        return `Table "${title}" with ${textRows.length} rows is now on the dashboard.`;
      },
      render: ({ args, status }) => (
        <ToolChip done={status === ToolCallStatus.Complete}>Table · {args.title}</ToolChip>
      ),
    },
    [],
  );

  // --------------------------------------------------------------------------
  // Bonus: show the BACKEND tool in the chat too
  // --------------------------------------------------------------------------
  // run_sql_query runs in Python, not here. useRenderTool has no handler: it
  // only decides how that tool call LOOKS in the chat, so the user can see
  // (and check) the SQL that the agent wrote.
  useRenderTool(
    {
      name: "run_sql_query",
      parameters: z.object({ sql: z.string() }),
      render: ({ parameters, status }) => <SqlChip sql={parameters.sql} done={status === "complete"} />,
    },
    [],
  );
}
