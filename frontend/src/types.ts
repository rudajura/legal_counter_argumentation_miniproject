export type Strength = "low" | "medium" | "high";

export interface Weakness {
  weakness: string;
  description: string;
}

export interface WeaknessesResponse {
  weaknesses: Weakness[];
  full_fact_pattern: string;
}

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
