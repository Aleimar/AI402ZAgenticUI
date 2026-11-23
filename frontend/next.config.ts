import type { NextConfig } from "next";
import { fileURLToPath } from "node:url";

const nextConfig: NextConfig = {
  // The CopilotKit runtime runs on the server; let Node load it as-is.
  serverExternalPackages: ["@copilotkit/runtime"],
  // Treat this folder as the project root, even if a parent folder has a lockfile.
  turbopack: { root: fileURLToPath(new URL(".", import.meta.url)) },
  // Do not let `next dev` write AGENTS.md / CLAUDE.md files into the project.
  agentRules: false,
  // Hide the floating Next.js badge so it does not cover the dashboard.
  devIndicators: false,
};

export default nextConfig;
