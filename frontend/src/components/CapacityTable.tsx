import type { CapacityUsage } from "@/lib/types";

type Props = {
  rows: CapacityUsage[];
};

export function CapacityTable({ rows }: Props) {
  return (
    <section className="panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Weekly capacity</p>
          <h2>Capacity usage</h2>
        </div>
        <span>{rows.length} week-stage rows</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Skill</th>
              <th className="numeric">Available</th>
              <th className="numeric">Used</th>
              <th className="numeric">Remaining</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td colSpan={5} className="empty-cell">
                  Run a calculation to show capacity usage.
                </td>
              </tr>
            ) : (
              rows.map((row) => (
                <tr key={`${row.week_start}-${row.stage}`}>
                  <td>{row.week_start}</td>
                  <td>{row.stage}</td>
                  <td className="numeric">{row.available_hours}</td>
                  <td className="numeric">{row.used_hours}</td>
                  <td className="numeric">{row.remaining_hours}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
