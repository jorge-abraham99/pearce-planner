import { CalendarCheck, Clock, Gauge } from "lucide-react";
import type { ScheduleResult as ScheduleResultType } from "@/lib/types";

type Props = {
  result: ScheduleResultType | null;
};

function displayStage(stage: string) {
  return stage.charAt(0).toUpperCase() + stage.slice(1);
}

export function ScheduleResult({ result }: Props) {
  if (!result) {
    return (
      <section className="panel result-empty">
        <p className="eyebrow">Scheduling result</p>
        <h2>No delivery date calculated yet</h2>
        <p>Select a baler type and run the calculation to generate a temporary schedule.</p>
      </section>
    );
  }

  return (
    <section className="result-grid" aria-label="Scheduling result">
      <article className="metric primary">
        <div className="metric-icon">
          <CalendarCheck size={22} aria-hidden="true" />
        </div>
        <span>Recommended Promise Date</span>
        <strong>{result.recommended_promise_date}</strong>
      </article>
      <article className="metric">
        <div className="metric-icon">
          <Clock size={22} aria-hidden="true" />
        </div>
        <span>Earliest Feasible Completion</span>
        <strong>{result.earliest_completion_date}</strong>
      </article>
      <article className="metric">
        <div className="metric-icon">
          <Gauge size={22} aria-hidden="true" />
        </div>
        <span>Main Bottleneck</span>
        <strong>{displayStage(result.bottleneck_stage)}</strong>
      </article>
      <article className="panel assumptions">
        <p className="eyebrow">Assumptions</p>
        <ul>
          {result.assumptions.map((assumption) => (
            <li key={assumption}>{assumption}</li>
          ))}
        </ul>
      </article>
    </section>
  );
}
