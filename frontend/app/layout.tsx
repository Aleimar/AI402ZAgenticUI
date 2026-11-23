import type { Metadata } from "next";
import type { ReactNode } from "react";
import { CopilotKit } from "@copilotkit/react-core/v2";

import "./globals.css";
import "@copilotkit/react-core/v2/styles.css";

export const metadata: Metadata = {
  title: "BrightCart Reports - Agentic UI tutorial",
  description: "Ask a question, get a dashboard. Google ADK + CopilotKit.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body suppressHydrationWarning>
        {/*
          <CopilotKit> connects every component inside it to the agent.
          - runtimeUrl: where our CopilotKit runtime lives (app/api/copilotkit)
          - agent:      which agent to talk to. Must match the name in route.ts
          - enableInspector: set it to true to get CopilotKit's debugging panel,
            a floating button that shows every event the agent sends
        */}
        <CopilotKit
          runtimeUrl="/api/copilotkit"
          agent="reporting_agent"
          useSingleEndpoint={false}
          enableInspector={false}
        >
          {children}
        </CopilotKit>
      </body>
    </html>
  );
}
