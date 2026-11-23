"""Backend tools: the things the agent can do on the SERVER.

In this project there is exactly one backend tool, `run_sql_query`, which lets
the agent read the SQLite database. A tool in Google ADK is just a normal
Python function: ADK reads the function name, the type hints and the
docstring, and sends them to the LLM so it knows when and how to call it.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "sales.db"
MAX_ROWS = 50  # never send more than this many rows back to the LLM


def _connect() -> sqlite3.Connection:
    """Open the database in READ-ONLY mode, so the agent can never change data."""
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"{DB_PATH} not found. Create it with: uv run data/seed_database.py"
        )
    return sqlite3.connect(f"{DB_PATH.as_uri()}?mode=ro", uri=True)


def run_sql_query(sql: str) -> dict:
    """Run one read-only SQL query on the BrightCart sales database and return the rows.

    Use this tool whenever you need numbers. The database is SQLite.

    Args:
        sql: A single SQLite SELECT statement. Aggregate inside SQL (SUM, COUNT,
            GROUP BY, ORDER BY, LIMIT) so that the result is small.

    Returns:
        On success: {"status": "success", "columns": [...], "rows": [[...], ...], "row_count": 3}
        On failure: {"status": "error", "error_message": "..."} - read the message,
        fix the SQL and try again.
    """
    statement = sql.strip().rstrip(";").strip()
    if not statement.lower().startswith(("select", "with")):
        return {"status": "error", "error_message": "Only SELECT statements are allowed."}
    if ";" in statement:
        return {"status": "error", "error_message": "Send one statement at a time (no ';')."}

    try:
        connection = _connect()
        try:
            cursor = connection.execute(statement)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchmany(MAX_ROWS + 1)
        finally:
            connection.close()
    except (sqlite3.Error, FileNotFoundError) as error:
        return {"status": "error", "error_message": str(error)}

    result = {
        "status": "success",
        "columns": columns,
        "rows": [list(row) for row in rows[:MAX_ROWS]],
        "row_count": min(len(rows), MAX_ROWS),
    }
    if len(rows) > MAX_ROWS:
        result["note"] = f"Only the first {MAX_ROWS} rows are shown. Aggregate or add LIMIT."
    return result


def describe_database() -> str:
    """Describe the tables and columns as text. We paste this into the agent's
    instructions so the LLM knows what it can query without spending a tool call."""
    connection = _connect()
    try:
        lines = []
        tables = connection.execute(
            "SELECT name, type FROM sqlite_master "
            "WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' ORDER BY type, name"
        ).fetchall()
        for name, kind in tables:
            row_count = connection.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            lines.append(f"{kind.upper()} {name} ({row_count:,} rows)")
            columns = connection.execute(f'PRAGMA table_info("{name}")').fetchall()
            for _, column, column_type, *_ in columns:
                if not column_type:  # calculated columns of a view have no declared type
                    sample = connection.execute(
                        f'SELECT typeof("{column}") FROM "{name}" LIMIT 1'
                    ).fetchone()
                    column_type = sample[0].upper() if sample else "TEXT"
                detail = f"  - {column} {column_type}"
                # For text columns with only a few different values, list the values.
                # This stops the LLM from guessing things like region = 'Western'.
                if column_type == "TEXT":
                    values = connection.execute(
                        f'SELECT DISTINCT "{column}" FROM "{name}" ORDER BY 1 LIMIT 13'
                    ).fetchall()
                    if len(values) <= 12:
                        detail += " -- one of: " + ", ".join(repr(v[0]) for v in values)
                lines.append(detail)
            lines.append("")
        first_day, last_day = connection.execute(
            "SELECT MIN(order_date), MAX(order_date) FROM orders"
        ).fetchone()
        lines.append(f"Dates are TEXT in YYYY-MM-DD format. Orders go from {first_day} to {last_day}.")
        return "\n".join(lines)
    finally:
        connection.close()
