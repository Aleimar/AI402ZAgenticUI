import type { ReactNode } from "react";

/**
 * A one-line status shown INSIDE the chat for every tool call, for example:
 *   ✓ Added chart - Monthly revenue
 * While the tool is still running it shows a spinner instead of the check mark.
 */
export function ToolChip({ done, children }: { done: boolean; children: ReactNode }) {
  return (
    <div className="my-1 flex items-center gap-2 rounded-lg border border-line bg-plane px-3 py-1.5 text-xs text-ink-2">
      {done ? (
        <span className="font-semibold text-[#006300]" aria-label="done">
          ✓
        </span>
      ) : (
        <span
          className="size-3 animate-spin rounded-full border-2 border-axis border-t-accent"
          aria-label="working"
        />
      )}
      <span className="min-w-0 truncate">{children}</span>
    </div>
  );
}

/** The chip for the backend tool. Click it to see the SQL the agent wrote. */
export function SqlChip({ sql, done }: { sql?: string; done: boolean }) {
  return (
    <details className="my-1 rounded-lg border border-line bg-plane px-3 py-1.5 text-xs text-ink-2">
      <summary className="flex cursor-pointer list-none items-center gap-2">
        {done ? (
          <span className="font-semibold text-[#006300]" aria-label="done">
            ✓
          </span>
        ) : (
          <span
            className="size-3 animate-spin rounded-full border-2 border-axis border-t-accent"
            aria-label="working"
          />
        )}
        <span>{done ? "Queried the database" : "Querying the database…"}</span>
        <span className="ml-auto text-muted">show SQL</span>
      </summary>
      <pre className="mt-2 overflow-x-auto whitespace-pre-wrap font-mono text-[11px] text-ink">{sql}</pre>
    </details>
  );
}
