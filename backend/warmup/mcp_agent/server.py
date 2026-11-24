"""Warm-up: a tiny MCP server.

MCP (Model Context Protocol) is a standard way to offer tools to ANY agent.
In first_agent the tool lived inside the agent's own file. Here the tools live
in this separate program, the MCP SERVER. An agent (the MCP CLIENT) starts
this program, asks "which tools do you have?" and then calls them.

Nobody runs this file by hand in normal use. Two programs start it for you:

    the MCP Inspector, a test page for MCP servers (run inside backend/):

        npx @modelcontextprotocol/inspector@2.16.0 uv run warmup/mcp_agent/server.py

    the ADK agent in agent.py, every time it needs the tools.

Important: this server talks to its client through stdin and stdout.
Never use print() in this file. It would corrupt the conversation.
"""

import sqlite3
from pathlib import Path

from mcp.server.mcpserver import MCPServer

DB_PATH = Path(__file__).parents[2] / "data" / "sales.db"

# ---------------------------------------------------------------------------
# 1. The SERVER. The name is what clients such as the Inspector display.
# ---------------------------------------------------------------------------
mcp = MCPServer("brightcart-sales")


def run_query(sql: str, parameters: tuple) -> list:
    """Run one SELECT on the sales database and return the rows."""
    connection = sqlite3.connect(DB_PATH)
    try:
        return connection.execute(sql, parameters).fetchall()
    finally:
        connection.close()


# ---------------------------------------------------------------------------
# 2. The TOOLS. Still normal Python functions, as in first_agent.
#    @mcp.tool() registers the function with the server. The server sends the
#    name, the parameters and the docstring to every client that connects.
# ---------------------------------------------------------------------------
@mcp.tool()
def get_top_products(year: int, limit: int = 5) -> dict:
    """Get BrightCart's best-selling products in one year, ranked by revenue.

    Args:
        year: The year to report on. The data covers 2024 and 2025.
        limit: How many products to return. The default is 5.
    """
    rows = run_query(
        "SELECT product_name, ROUND(SUM(revenue)) FROM sales WHERE order_year = ? "
        "GROUP BY product_name ORDER BY 2 DESC LIMIT ?",
        (str(year), limit),
    )
    if not rows:
        return {"status": "error", "error_message": f"There is no data for {year}."}
    return {"status": "success", "year": year, "revenue_usd": dict(rows)}


@mcp.tool()
def get_revenue_by_month(year: int) -> dict:
    """Get BrightCart's total revenue for each month of one year.

    Args:
        year: The year to report on. The data covers 2024 and 2025.
    """
    rows = run_query(
        "SELECT order_month, ROUND(SUM(revenue)) FROM sales WHERE order_year = ? "
        "GROUP BY order_month ORDER BY order_month",
        (str(year),),
    )
    if not rows:
        return {"status": "error", "error_message": f"There is no data for {year}."}
    return {"status": "success", "year": year, "revenue_usd": dict(rows)}


# ---------------------------------------------------------------------------
# 3. START the server. "stdio" means: the client starts this file as a child
#    process and the two talk through stdin and stdout. No port, no URL.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run(transport="stdio")
