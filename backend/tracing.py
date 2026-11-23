"""Optional tracing with Arize Phoenix.

Phoenix is an open-source observability tool for LLM apps. When tracing is on,
every run of the agent is recorded as a "trace": you can see each LLM call
(with the full prompt), each tool call, how long it took and how many tokens
it used. Open http://localhost:6006 to look at them.

Tracing is OFF unless PHOENIX_COLLECTOR_ENDPOINT is set in .env, so the app
works fine when Phoenix is not running.
"""

import os


def setup_tracing() -> bool:
    """Turn tracing on if PHOENIX_COLLECTOR_ENDPOINT is set. Returns True if on."""
    if not os.getenv("PHOENIX_COLLECTOR_ENDPOINT"):
        return False

    from openinference.instrumentation.google_adk import GoogleADKInstrumentor
    from phoenix.otel import register

    # 1. Create a "tracer provider": the object that ships traces to Phoenix.
    #    It reads the address from PHOENIX_COLLECTOR_ENDPOINT.
    tracer_provider = register(
        project_name=os.getenv("PHOENIX_PROJECT_NAME", "agentic-ui-tutorial"),
        protocol="http/protobuf",  # send over HTTP to <endpoint>/v1/traces
        batch=True,                # send in the background so the agent is never slowed down
        set_global_tracer_provider=False,  # trace only the agent, not every HTTP request
        verbose=False,
    )

    # 2. Instrument Google ADK: from now on every agent run, LLM call and
    #    tool call is recorded automatically. No changes to agent.py needed.
    GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)
    return True
