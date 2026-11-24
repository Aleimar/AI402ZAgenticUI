"""Warm-up: an ADK agent that gets its tools from an MCP server.

This file is NOT part of the dashboard app. Do first_agent first.

In first_agent the tool was a Python function in the same file. Here the
agent has NO tool functions at all. It connects to the MCP server in
server.py (same folder) and uses whatever tools that server offers.

Try it in ADK's built-in test page:

    uv run adk web warmup --port 8001

then open http://localhost:8001 and pick mcp_agent at the top left.
"""

import os
import sys
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

SERVER_FILE = Path(__file__).parent / "server.py"

# ---------------------------------------------------------------------------
# 1. HOW TO START the MCP server: a command plus its arguments.
#    sys.executable is the Python that runs this agent (the one in .venv),
#    so this is the same as typing:  python warmup/mcp_agent/server.py
# ---------------------------------------------------------------------------
server_params = StdioServerParameters(
    command=sys.executable,
    args=[str(SERVER_FILE)],
)

# ---------------------------------------------------------------------------
# 2. The MCP TOOLSET is the MCP client. It starts the server, asks it for its
#    list of tools and hands them to the agent as normal ADK tools.
#    timeout: how many seconds to wait for the server to start.
# ---------------------------------------------------------------------------
sales_tools = McpToolset(
    connection_params=StdioConnectionParams(server_params=server_params, timeout=15),
)

# ---------------------------------------------------------------------------
# 3. The MODEL. Same rule as the main app: a plain name is a Gemini model,
#    "provider/model" goes through LiteLLM (step 9 of the tutorial).
# ---------------------------------------------------------------------------
MODEL_NAME = os.getenv("MODEL") or "gemini-4-hydrogen"
model = LiteLlm(model=MODEL_NAME) if "/" in MODEL_NAME else MODEL_NAME

# ---------------------------------------------------------------------------
# 4. The AGENT. The only new thing: tools=[...] holds a toolset, not functions.
# ---------------------------------------------------------------------------
root_agent = LlmAgent(
    name="mcp_agent",
    model=model,
    description="Answers questions about BrightCart products and monthly revenue.",
    instruction=(
        "You are a helpful assistant for BrightCart, a retail company. "
        "Use your tools to get real numbers about best-selling products and "
        "monthly revenue. Never guess a number. Answer in one or two sentences."
    ),
    tools=[sales_tools],
)
