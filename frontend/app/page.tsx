"use client";

import { CopilotChat, useConfigureSuggestions } from "@copilotkit/react-core/v2";
import { useState } from "react";

import { Dashboard } from "@/components/Dashboard";
import { useDashboardTools } from "@/hooks/useDashboardTools";
import type { DashboardState } from "@/lib/types";

export default function Page() {
  // The whole dashboard is ordinary React state. It starts empty (null).
  const [dashboard, setDashboard] = useState<DashboardState | null>(null);

  // Hand the agent the tools that change this state. See hooks/useDashboardTools.tsx.
  useDashboardTools(setDashboard);

  // Clickable example questions shown in the chat before the first message.
  useConfigureSuggestions({
    suggestions: [
      { title: "2025 overview", message: "How did sales perform in 2025?" },
      { title: "Best products", message: "What are our top 5 products by revenue?" },
      { title: "Regions", message: "Compare revenue and profit across regions." },
      { title: "Channels", message: "How is revenue split between sales channels?" },
    ],
  });

  return (
    <div className="flex h-dvh flex-col lg:flex-row">
      {/* Left: the dashboard that the agent builds */}
      <main className="min-h-0 min-w-0 flex-1 overflow-y-auto">
        <Dashboard dashboard={dashboard} />
      </main>

      {/* Right: the chat */}
      <aside className="h-[55dvh] shrink-0 border-t border-line bg-white lg:h-auto lg:w-[420px] lg:border-l lg:border-t-0">
        <CopilotChat
          labels={{
            welcomeMessageText: "Hi! Ask me anything about BrightCart sales and I will build a dashboard for you.",
            chatInputPlaceholder: "Ask about sales, products, regions…",
          }}
          // Hide the small copy-button toolbar under each message to keep the chat compact.
          messageView={{ assistantMessage: { toolbarVisible: false } }}
        />
      </aside>
    </div>
  );
}
