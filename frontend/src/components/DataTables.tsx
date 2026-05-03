import type { TablesResponse } from "@/lib/types";

type Props = {
  tables: TablesResponse | null;
};

export function DataTables({ tables }: Props) {
  if (!tables) {
    return (
      <section className="panel">
        <p className="eyebrow">Input data</p>
        <h2>Planning assumptions</h2>
        <p className="muted">Loading source tables...</p>
      </section>
    );
  }

  return (
    <section className="data-stack">
      <div className="section-heading standalone">
        <div>
          <p className="eyebrow">Input data</p>
          <h2>Planning assumptions</h2>
        </div>
        <p>The schedule is calculated from stage-level labour requirements, weekly worker capacity, and the settings below.</p>
      </div>
      <DataTable
        title="Labour requirements"
        rows={tables.labour_requirements}
        columns={[
          ["baler_type", "Baler Type"],
          ["stage", "Stage"],
          ["sequence_order", "Sequence"],
          ["required_hours", "Hours"],
        ]}
      />
      <DataTable
        title="Workers"
        rows={tables.workers}
        columns={[
          ["worker_id", "Worker"],
          ["worker_name", "Name"],
          ["skill", "Skill"],
          ["hours_per_week", "Hours / Week"],
        ]}
      />
      <section className="panel settings-panel">
        <h3>Settings</h3>
        <dl>
          {Object.entries(tables.settings).map(([key, value]) => (
            <div key={key}>
              <dt>{key.replaceAll("_", " ")}</dt>
              <dd>{value}</dd>
            </div>
          ))}
        </dl>
      </section>
    </section>
  );
}

function DataTable<T extends Record<string, string | number>>({
  title,
  rows,
  columns,
}: {
  title: string;
  rows: T[];
  columns: [keyof T, string][];
}) {
  return (
    <section className="panel">
      <h3>{title}</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              {columns.map(([key, label]) => (
                <th key={String(key)}>{label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="empty-cell">
                  No rows.
                </td>
              </tr>
            ) : (
              rows.map((row, index) => (
                <tr key={index}>
                  {columns.map(([key]) => (
                    <td key={String(key)}>{row[key]}</td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
