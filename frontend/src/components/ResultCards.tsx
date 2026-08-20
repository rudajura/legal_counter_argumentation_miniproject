import type { AnalyzeResponse, Strength } from "../types";

const STRENGTH_LABEL: Record<Strength, string> = {
  low: "Nízká",
  medium: "Střední",
  high: "Vysoká",
};

export function ResultCards({ result }: { result: AnalyzeResponse }) {
  return (
    <section className="results" aria-label="Výsledky analýzy">
      <p className="field-heading">Shrnutí</p>
      <p className="summary">{result.summary}</p>
      <div className="cards">
        {result.items.map((item, index) => (
          <article className="card" data-strength={item.strength} key={index}>
            <p className="field-heading">Slabina</p>
            <h3 className="card-title">{item.weakness}</h3>

            <p className="field-heading">Protiargument</p>
            <p className="counterargument">{item.counterargument}</p>

            <div className="seal">
              <span className="seal-ring">
                <span className="visually-hidden">
                  Síla protiargumentu:{" "}
                </span>
                {STRENGTH_LABEL[item.strength]}
              </span>
            </div>

            <p className="field-heading">Odůvodnění</p>
            <p className="reasoning">{item.reasoning}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
