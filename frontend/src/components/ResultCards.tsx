import type { AnalyzeResponse } from "../types";
import { AnalysisCard } from "./AnalysisCard";

export function ResultCards({ result }: { result: AnalyzeResponse }) {
  return (
    <section className="results" aria-label="Výsledky analýzy">
      <p className="field-heading">Shrnutí</p>
      <p className="summary">{result.summary}</p>
      <div className="cards">
        {result.items.map((item, index) => (
          <AnalysisCard key={index} weakness={item.weakness} item={item} />
        ))}
      </div>
    </section>
  );
}
