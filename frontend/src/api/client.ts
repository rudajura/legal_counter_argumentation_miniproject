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
    throw new Error(`Analýza slabin se nezdařila (HTTP ${response.status})`);
  }

  return response.json();
}

export async function extractFactPattern(files: File[]): Promise<string> {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }

  const response = await fetch(`${API_BASE_URL}/api/extract/fact-pattern`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Extrakce skutkového stavu se nezdařila (HTTP ${response.status})`);
  }

  const body: { fact_pattern: string } = await response.json();
  return body.fact_pattern;
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
    throw new Error(`Generování protiargumentů se nezdařilo (HTTP ${response.status})`);
  }

  return response.json();
}

interface StreamAnalysisCallbacks {
  onWeaknesses: (data: WeaknessesResponse) => void;
  onResult: (data: AnalyzeResponse) => void;
  onError: (message: string) => void;
}

export async function streamAnalysis(
  factPattern: string,
  argument: string,
  files: File[],
  callbacks: StreamAnalysisCallbacks,
): Promise<void> {
  const formData = new FormData();
  formData.append("fact_pattern", factPattern);
  formData.append("argument", argument);
  for (const file of files) {
    formData.append("files", file);
  }

  const response = await fetch(`${API_BASE_URL}/api/analyze/stream`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok || !response.body) {
    throw new Error(`Streamovaná analýza se nezdařila (HTTP ${response.status})`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let terminalEventDispatched = false;
  const markTerminal = () => {
    terminalEventDispatched = true;
  };

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let boundary = buffer.indexOf("\n\n");
    while (boundary !== -1) {
      dispatchSseFrame(buffer.slice(0, boundary), callbacks, markTerminal);
      buffer = buffer.slice(boundary + 2);
      boundary = buffer.indexOf("\n\n");
    }
  }

  if (!terminalEventDispatched) {
    throw new Error("Spojení bylo přerušeno dříve, než analýza skončila.");
  }
}

function dispatchSseFrame(
  frame: string,
  callbacks: StreamAnalysisCallbacks,
  markTerminal: () => void,
): void {
  const eventLine = frame.split("\n").find((line) => line.startsWith("event: "));
  const dataLine = frame.split("\n").find((line) => line.startsWith("data: "));
  if (!eventLine || !dataLine) return;

  const eventType = eventLine.slice("event: ".length);
  const data = JSON.parse(dataLine.slice("data: ".length));

  if (eventType === "weaknesses") {
    callbacks.onWeaknesses(data as WeaknessesResponse);
  } else if (eventType === "result") {
    callbacks.onResult(data as AnalyzeResponse);
    markTerminal();
  } else if (eventType === "error") {
    callbacks.onError((data as { message: string }).message);
    markTerminal();
  }
}
