"use client";

import { useEffect, useState } from "react";
import { AlertCircle } from "lucide-react";
import { BalerSelector } from "@/components/BalerSelector";
import { CapacityTable } from "@/components/CapacityTable";
import { CurrentOrdersTable } from "@/components/CurrentOrdersTable";
import { DataTables } from "@/components/DataTables";
import { ScheduleResult } from "@/components/ScheduleResult";
import { ScheduleTable } from "@/components/ScheduleTable";
import { getBalerTypes, getTables, scheduleBaler } from "@/lib/api";
import type { ScheduleResult as ScheduleResultType, TablesResponse } from "@/lib/types";

export default function Home() {
  const [balerTypes, setBalerTypes] = useState<string[]>([]);
  const [selectedBalerType, setSelectedBalerType] = useState("");
  const [tables, setTables] = useState<TablesResponse | null>(null);
  const [result, setResult] = useState<ScheduleResultType | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    async function loadInitialData() {
      try {
        const [types, sourceTables] = await Promise.all([getBalerTypes(), getTables()]);
        setBalerTypes(types);
        setSelectedBalerType(types[0] ?? "");
        setTables(sourceTables);
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Unable to load planner data.");
      }
    }

    loadInitialData();
  }, []);

  async function handleSubmit() {
    if (!selectedBalerType) {
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const scheduleResult = await scheduleBaler(selectedBalerType);
      setResult(scheduleResult);
      setTables(await getTables());
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to calculate delivery date.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <header className="app-header">
        <div>
          <p className="eyebrow">Pearce planning demo</p>
          <h1>Pearce Delivery Date Planner</h1>
          <p>
            Select a baler type to estimate the earliest credible delivery date against the current order book and
            available labour capacity.
          </p>
        </div>
      </header>

      {error ? (
        <div className="error-banner" role="alert">
          <AlertCircle size={18} aria-hidden="true" />
          {error}
        </div>
      ) : null}

      <CurrentOrdersTable orders={tables?.orders ?? []} isLoading={!tables && !error} />

      <div className="layout-grid">
        <BalerSelector
          balerTypes={balerTypes}
          selectedBalerType={selectedBalerType}
          isLoading={isLoading}
          onSelect={setSelectedBalerType}
          onSubmit={handleSubmit}
        />
        <ScheduleResult result={result} />
      </div>

      <div className="tables-grid">
        <ScheduleTable rows={result?.schedule ?? []} />
        <CapacityTable rows={result?.capacity_usage ?? []} />
      </div>

      <DataTables tables={tables} />
    </main>
  );
}
