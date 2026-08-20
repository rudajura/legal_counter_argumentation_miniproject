import type { CounterargumentItem, Strength } from "../types";

const STRENGTH_LABEL: Record<Strength, string> = {
  low: "Nízká",
  medium: "Střední",
  high: "Vysoká",
};

interface AnalysisCardProps {
  weakness: string;
  item: CounterargumentItem | null;
}

export function AnalysisCard({ weakness, item }: AnalysisCardProps) {
  return (
    <article className="card" data-strength={item?.strength}>
      <p className="field-heading">Slabina</p>
      <h3 className="card-title">{weakness}</h3>

      <p className="field-heading">Protiargument</p>
      {item ? (
        <p className="counterargument">{item.counterargument}</p>
      ) : (
        <p className="counterargument counterargument--pending">
          Protiargument se připravuje…
        </p>
      )}

      {item && (
        <div className="seal">
          <span className="seal-ring">
            <span className="visually-hidden">Síla protiargumentu: </span>
            {STRENGTH_LABEL[item.strength]}
          </span>
        </div>
      )}

      <p className="field-heading">Odůvodnění</p>
      {item ? (
        <p className="reasoning">{item.reasoning}</p>
      ) : (
        <p className="reasoning reasoning--pending">…</p>
      )}
    </article>
  );
}
