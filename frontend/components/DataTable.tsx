import type { TableWidget } from "@/lib/types";

// "$1,204.50", "12%", "-3" ... look like numbers, so we right-align them.
const looksNumeric = (cell: string) => /^[-+$€£₱]?[\d,.]+\s?[%KMB]?$/.test(cell.trim());

/** A small table for when the exact figures matter. */
export function DataTable({ title, columns, rows }: TableWidget) {
  return (
    <div className="widget-in rounded-xl border border-line bg-surface p-4">
      <h3 className="text-sm font-semibold text-ink">{title}</h3>
      <div className="mt-3 overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-axis text-ink-2">
              {columns.map((column, index) => (
                <th
                  key={index}
                  className={`px-2 py-2 font-medium ${rows.every((row) => looksNumeric(row[index] ?? "")) ? "text-right" : ""}`}
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr key={rowIndex} className="border-b border-grid last:border-0">
                {columns.map((_, index) => {
                  const cell = row[index] ?? "";
                  return (
                    <td
                      key={index}
                      className={`px-2 py-2 text-ink ${looksNumeric(cell) ? "text-right tabular-nums" : ""}`}
                    >
                      {cell}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
