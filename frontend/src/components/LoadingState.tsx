import { useEffect, useState } from "react";

export type LoadingPhase = "weaknesses" | "counterarguments";

const PHASE_LABEL: Record<LoadingPhase, string> = {
  weaknesses: "Analyzuji slabiny argumentu…",
  counterarguments: "Hledám protiargumenty…",
};

interface LoadingStateProps {
  phase: LoadingPhase;
  percent: number;
}

export function LoadingState({ phase, percent }: LoadingStateProps) {
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  useEffect(() => {
    const startedAt = Date.now();
    const intervalId = setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - startedAt) / 1000));
    }, 1000);
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="loading" role="status">
      <div className="loading-header">
        <span className="loading-dot" aria-hidden="true" />
        <p className="loading-label">{PHASE_LABEL[phase]}</p>
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
