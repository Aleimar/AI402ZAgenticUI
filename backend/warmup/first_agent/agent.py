"""Warm-up: the smallest useful Google ADK agent.

This file is NOT part of the dashboard app. It exists so you can meet ADK on
its own first. Try it in ADK's built-in test page:

    uv run adk web warmup --port 8001

then open http://localhost:8001

An agent is three things: a MODEL, INSTRUCTIONS and TOOLS.
"""

import os
import sqlite3
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

DB_PATH = Path(__file__).parents[2] / "data" / "sales.db"


# ---------------------------------------------------------------------------
# 1. A TOOL is a normal Python function.
#    ADK shows the LLM its name, its parameters and its docstring. The LLM
#    reads them to decide WHEN to call the function and WITH WHAT arguments.
# ---------------------------------------------------------------------------
def get_revenue_by_region(year: int) -> dict:
    """Get BrightCart's total revenue for each sales region in one year.

    Args:
        year: The year to report on. The data covers 2024 and 2025.

    Returns:
        A dictionary such as {"year": 2025, "revenue_usd": {"West": 335318.0, ...}}.
    """
    connection = sqlite3.connect(DB_PATH)
    try:
        rows = connection.execute(
            "SELECT region, ROUND(SUM(revenue)) FROM sales WHERE order_year = ? "
            "GROUP BY region ORDER BY 2 DESC",
            (str(year),),
        ).fetchall()
    finally:
        connection.close()
    if not rows:
        return {"status": "error", "error_message": f"There is no data for {year}."}
    return {"status": "success", "year": year, "revenue_usd": dict(rows)}


# ---------------------------------------------------------------------------
# 2. The MODEL. Same rule as the main app: a plain name is a Gemini model,
#    "provider/model" goes through LiteLLM (step 9 of the tutorial).
# ---------------------------------------------------------------------------
MODEL_NAME = os.getenv("MODEL") or "gemini-4-hydrogen"
model = LiteLlm(model=MODEL_NAME) if "/" in MODEL_NAME else MODEL_NAME

# ---------------------------------------------------------------------------
# 3. The AGENT puts model, instructions and tools together.
#    `adk web` looks for a variable with exactly this name: root_agent.
# ---------------------------------------------------------------------------
root_agent = LlmAgent(
    name="first_agent",
    model=model,
    description="Answers questions about BrightCart revenue by region.",
    instruction=(
        "You are a helpful assistant for BrightCart, a retail company. "
        "When the user asks about revenue or regions, call get_revenue_by_region "
        "to get real numbers. Never guess a number. Answer in one or two sentences."
    ),
    tools=[get_revenue_by_region],
)
