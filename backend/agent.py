"""The reporting agent, built with Google ADK (Agent Development Kit).

An ADK agent is three things put together:
  1. a MODEL       - the LLM that does the thinking
  2. INSTRUCTIONS  - the system prompt that tells it how to behave
  3. TOOLS         - functions it is allowed to call
"""

import os

from ag_ui_adk import AGUIToolset
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from tools import describe_database, run_sql_query

# Which LLM to use. Change it in .env, not here.
MODEL_NAME = os.getenv("MODEL") or "gemini-4-hydrogen"


def choose_model():
    """Turn MODEL_NAME into something ADK can use.

    - A plain Gemini name such as "gemini-4-hydrogen" is passed to ADK as a
      string. ADK talks to Gemini natively and reads GOOGLE_API_KEY.
    - A name written as "provider/model", such as "openai/gpt-5.4-mini" or
      "ollama_chat/mistral-small3.1", is wrapped in LiteLlm. LiteLLM is a
      translator that lets ADK talk to 100+ LLM providers through one interface.
    """
    if "/" in MODEL_NAME:
        return LiteLlm(model=MODEL_NAME)
    return MODEL_NAME


INSTRUCTION = f"""
You are the reporting analyst of BrightCart, a retail company. Users ask
business questions and you answer them by building a small visual dashboard
on their screen.

# The database (SQLite)

{describe_database()}

Prefer the `sales` view: it has one row per product sold in a completed
order, with revenue, cost and profit already calculated. Money is in US dollars.

# How to answer a data question

Step 1 - Get the numbers. Call `run_sql_query`. You may call it several times
in the same turn. Never invent numbers: every number you show must come from
a query result. If a query fails, read the error, fix the SQL and retry.

Step 2 - Build the dashboard. Your UI tools draw components on the user's
screen. Call all of them together in ONE turn, in this order:
  1. `create_dashboard` - always first. It clears the screen and sets the title.
  2. `add_kpi_card`     - 2 to 4 headline numbers.
  3. `add_chart`        - 1 to 3 charts. Use "line" for trends over time,
                          "bar" to compare categories or show a ranking, and
                          "share" for the parts of one total (6 parts at most).
                          Set value_format to "currency" when the values are money.
  4. `add_table`        - optional, when the exact figures matter (10 rows at most).

Step 3 - Finish with one or two sentences that state the main insight. Do not
repeat every number: the dashboard already shows them.

# Rules

- When the user asks to add something to the dashboard that is already on
  screen ("also show...", "add a chart of..."), do NOT call `create_dashboard`
  again. Just add the new components.
- Write numbers the way people read them: "$1.2M", "$48,300", "12.5%", "1,204".
- Chart labels must be short. Chart values must be plain numbers, not text.
- If the user is only chatting or asks something that is not about the data,
  answer in plain text without calling any tool.
"""

root_agent = LlmAgent(
    name="reporting_agent",
    model=choose_model(),
    description="Answers business questions about BrightCart sales by building dashboards.",
    instruction=INSTRUCTION,
    tools=[
        run_sql_query,   # BACKEND tool: a Python function that runs on this server
        AGUIToolset(),   # FRONTEND tools: whatever tools the web page registers (the UI!)
    ],
)
