"""The web server that puts the agent on the network.

Start it with:

    uv run main.py

It serves the ADK agent at http://localhost:8000/ using the AG-UI protocol,
the "language" that the CopilotKit frontend speaks.
"""

import os

from dotenv import load_dotenv

load_dotenv()  # read backend/.env BEFORE anything else looks at the environment

from tracing import setup_tracing

tracing_enabled = setup_tracing()  # must run before the agent is created

import uvicorn
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from fastapi import FastAPI
from google.adk.apps import App, ResumabilityConfig

from agent import MODEL_NAME, root_agent

# An ADK "App" wraps the agent together with app-level settings.
# is_resumable=True lets a run PAUSE when the agent calls a frontend tool,
# wait for the browser to draw the component, and then continue.
adk_app = App(
    name="reporting_app",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)

# ADKAgent is the bridge: it translates between ADK events and AG-UI events.
agui_agent = ADKAgent.from_app(
    adk_app,
    user_id="student",            # one shared demo user (there is no login in this tutorial)
    use_in_memory_services=True,  # keep chat sessions in memory (they are lost on restart)
)

app = FastAPI(title="Agentic UI tutorial - reporting agent")
add_adk_fastapi_endpoint(app, agui_agent, path="/")


@app.get("/health")
def health():
    """Open http://localhost:8000/health in a browser to check the server is up."""
    return {"status": "ok", "model": MODEL_NAME, "tracing": tracing_enabled}


def missing_settings() -> list[str]:
    """Names of the .env settings (API keys) that the chosen model still needs."""
    if "/" not in MODEL_NAME:  # Gemini, used natively by ADK
        has_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        return [] if has_key else ["GOOGLE_API_KEY"]
    import litellm  # every other provider goes through LiteLLM, which knows what each one needs

    return litellm.validate_environment(model=MODEL_NAME)["missing_keys"]


if __name__ == "__main__":
    port = int(os.getenv("PORT") or 8000)
    print(f"Model:            {MODEL_NAME}")
    print(f"Phoenix tracing:  {'ON' if tracing_enabled else 'off'}")
    print(f"Agent endpoint:   http://localhost:{port}/")
    if missing := missing_settings():
        print(f"\nWARNING: missing in backend/.env: {', '.join(missing)}")
        print("The server will start, but the agent cannot answer until you add it.\n")
    uvicorn.run(app, host="127.0.0.1", port=port)
