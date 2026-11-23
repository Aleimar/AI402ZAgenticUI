// The CopilotKit runtime: a small piece of server code that sits between the
// browser and the Python agent.
//
//   browser  ->  /api/copilotkit  ->  http://127.0.0.1:8000/  (FastAPI + ADK)
//
// The file lives in a folder called [[...slug]] so that it answers every URL
// that starts with /api/copilotkit (for example /api/copilotkit/info).

import { CopilotRuntime, createCopilotRuntimeHandler } from "@copilotkit/runtime/v2";
import { HttpAgent } from "@ag-ui/client";

const runtime = new CopilotRuntime({
  agents: {
    // "reporting_agent" is the name the frontend uses to pick this agent.
    // It must match the `agent` prop in app/layout.tsx.
    reporting_agent: new HttpAgent({
      url: process.env.AGENT_URL ?? "http://127.0.0.1:8000/",
    }),
  },
  // There is no login in this tutorial, so every visitor is the same demo user.
  identifyUser: () => ({ id: "student", name: "Student" }),
});

const handler = createCopilotRuntimeHandler({
  runtime,
  basePath: "/api/copilotkit",
});

export { handler as GET, handler as POST };
