import type { AnalyzeResponse, Strength } from "../types";

const STRENGTH_COLOR: Record<Strength, string> = {
  low: "#2e7d32",
  medium: "#f9a825",
  high: "#c62828",
};

const STRENGTH_LABEL: Record<Strength, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
};

export function ResultCards({ result }: { result: AnalyzeResponse }) {
  return (
    <div className="results">
      <p className="summary">{result.summary}</p>
      <div className="cards">
        {result.items.map((item, index) => (
          <div
            className="card"
            key={index}
            style={{ borderLeftColor: STRENGTH_COLOR[item.strength] }}
          >
            <h3>{item.weakness}</h3>
            <p className="counterargument">{item.counterargument}</p>
            <span
              className="badge"
              style={{ backgroundColor: STRENGTH_COLOR[item.strength] }}
            >
              Strength: {STRENGTH_LABEL[item.strength]}
            </span>
            <p className="reasoning">{item.reasoning}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
