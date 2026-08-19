import type { AnalyzeResponse } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function analyzeArgument(
  factPattern: string,
  argument: string,
  files: File[],
): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append("fact_pattern", factPattern);
  formData.append("argument", argument);
  for (const file of files) {
    formData.append("files", file);
  }

  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Analysis failed (HTTP ${response.status})`);
  }

  return response.json();
}
