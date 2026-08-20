import type { AnalyzeResponse, Weakness, WeaknessesResponse } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function analyzeWeaknesses(
  factPattern: string,
  argument: string,
  files: File[],
): Promise<WeaknessesResponse> {
  const formData = new FormData();
  formData.append("fact_pattern", factPattern);
  formData.append("argument", argument);
  for (const file of files) {
    formData.append("files", file);
  }

  const response = await fetch(`${API_BASE_URL}/api/analyze/weaknesses`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Weakness analysis failed (HTTP ${response.status})`);
  }

  return response.json();
}

export async function generateCounterarguments(
  weaknesses: Weakness[],
  fullFactPattern: string,
  argument: string,
): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE_URL}/api/analyze/counterarguments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      weaknesses,
      full_fact_pattern: fullFactPattern,
      argument,
    }),
  });

  if (!response.ok) {
    throw new Error(`Counterargument generation failed (HTTP ${response.status})`);
  }

  return response.json();
}
