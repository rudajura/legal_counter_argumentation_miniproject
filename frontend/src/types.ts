export type Strength = "low" | "medium" | "high";

export interface CounterargumentItem {
  weakness: string;
  counterargument: string;
  strength: Strength;
  reasoning: string;
}

export interface AnalyzeResponse {
  summary: string;
  items: CounterargumentItem[];
}
