import { useEffect, useState } from "react";

export type LoadingPhase = "weaknesses" | "counterarguments";

const TOTAL_STEPS = 2;

const PHASE_INFO: Record<LoadingPhase, { step: number; label: string }> = {
  weaknesses: { step: 1, label: "Analyzuji slabiny argumentu…" },
  counterarguments: { step: 2, label: "Hledám protiargumenty…" },
};

export function LoadingState({ phase }: { phase: LoadingPhase }) {
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  useEffect(() => {
    const startedAt = Date.now();
    const intervalId = setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - startedAt) / 1000));
    }, 1000);
    return () => clearInterval(intervalId);
  }, []);

  const { step, label } = PHASE_INFO[phase];
  const completedSteps = step - 1;
  const percent = Math.round((completedSteps / TOTAL_STEPS) * 100);

  return (
    <div className="loading" role="status">
      <div className="loading-header">
        <span className="loading-dot" aria-hidden="true" />
        <p className="loading-label">
          Krok {step} z {TOTAL_STEPS} · {label}
        </p>
        <span className="loading-time">{elapsedSeconds} s</span>
      </div>
      <div
        className="progress-track"
        role="progressbar"
        aria-valuenow={percent}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div className="progress-fill" style={{ width: `${percent}%` }} />
      </div>
      <p className="progress-percent">{percent} % hotovo</p>
    </div>
  );
}
