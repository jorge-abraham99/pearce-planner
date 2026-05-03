import type { ScheduledOperation } from "@/lib/types";

type Props = {
  rows: ScheduledOperation[];
};

export function ScheduleTable({ rows }: Props) {
  return (
    <section className="panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Generated schedule</p>
          <h2>Stage plan</h2>
        </div>
        <span>{rows.length} operations</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Order</th>
              <th>Baler Type</th>
              <th>Stage</th>
              <th>Date</th>
              <th className="numeric">Scheduled Hours</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td colSpan={5} className="empty-cell">
                  Run a calculation to show the generated schedule.
                </td>
              </tr>
            ) : (
              rows.map((row) => (
                <tr key={`${row.order_id}-${row.stage}-${row.scheduled_week}`}>
                  <td>{row.order_id}</td>
                  <td>{row.baler_type}</td>
                  <td>{row.stage}</td>
                  <td>{row.scheduled_week}</td>
                  <td className="numeric">{row.required_hours}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
