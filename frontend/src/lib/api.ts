import type { ScheduleResult, TablesResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function getBalerTypes(): Promise<string[]> {
  const response = await request<{ baler_types: string[] }>("/baler-types");
  return response.baler_types;
}

export async function getTables(): Promise<TablesResponse> {
  return request<TablesResponse>("/tables");
}

export async function scheduleBaler(balerType: string): Promise<ScheduleResult> {
  return request<ScheduleResult>("/schedule", {
    method: "POST",
    body: JSON.stringify({ baler_type: balerType }),
  });
}
