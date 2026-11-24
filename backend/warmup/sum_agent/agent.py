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
def sum_two_numbers(a: float, b: float) -> float:
    """Return the sum of two numbers.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The sum of a and b.
    """
    return a + b

def difference_two_numbers(a: float, b: float) -> float:
    """Return the difference of two numbers.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The difference of a and b.
    """
    return a - b

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
    name="sum_agent",
    model=model,
    description="It takes 2 numbers and returns their sum.",
    instruction=(
        "When the user asks to sum two numbers, call sum_two_numbers "
        "When the user asks to difference two numbers, call difference_two_numbers "
        "to get the result. Never guess a number. Answer in one or two sentences."
    ),
    tools=[sum_two_numbers, difference_two_numbers],
)
