import { Calculator } from "lucide-react";

type BalerSelectorProps = {
  balerTypes: string[];
  selectedBalerType: string;
  isLoading: boolean;
  onSelect: (balerType: string) => void;
  onSubmit: () => void;
};

export function BalerSelector({
  balerTypes,
  selectedBalerType,
  isLoading,
  onSelect,
  onSubmit,
}: BalerSelectorProps) {
  return (
    <section className="panel selector-panel">
      <div>
        <p className="eyebrow">New enquiry</p>
        <h2>Add the next customer order</h2>
      </div>
      <div className="selector-controls">
        <label>
          <span>Baler type</span>
          <select value={selectedBalerType} onChange={(event) => onSelect(event.target.value)}>
            {balerTypes.map((balerType) => (
              <option value={balerType} key={balerType}>
                {balerType}
              </option>
            ))}
          </select>
        </label>
        <button onClick={onSubmit} disabled={!selectedBalerType || isLoading}>
          <Calculator size={18} aria-hidden="true" />
          {isLoading ? "Scheduling" : "Schedule order"}
        </button>
      </div>
    </section>
  );
}
