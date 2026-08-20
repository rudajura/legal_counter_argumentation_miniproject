import { useState } from "react";
import { ArgumentForm } from "./components/ArgumentForm";
import { LoadingState, type LoadingPhase } from "./components/LoadingState";
import { ResultCards } from "./components/ResultCards";
import { AnalysisCard } from "./components/AnalysisCard";
import { streamAnalysis } from "./api/client";
import type { AnalyzeResponse, CounterargumentItem, Weakness } from "./types";
import "./App.css";

type Status = "idle" | "loading" | "error" | "done";

// Phase 1 targets 3-5 weaknesses (see backend/tools/prompts/weakness_analysis.py);
// used only to estimate progress before the exact count is known.
const EXPECTED_WEAKNESS_COUNT = 4;

function computePercent(
  phase: LoadingPhase,
  weaknesses: Weakness[],
  items: CounterargumentItem[],
): number {
  if (phase === "weaknesses") {
    const estimate = Math.min(weaknesses.length / EXPECTED_WEAKNESS_COUNT, 0.9);
    return Math.round(estimate * 50);
  }
  const total = weaknesses.length || 1;
  const estimate = Math.min(items.length / total, 1);
  return 50 + Math.round(estimate * 50);
}

export default function App() {
  const [status, setStatus] = useState<Status>("idle");
  const [phase, setPhase] = useState<LoadingPhase>("weaknesses");
  const [weaknesses, setWeaknesses] = useState<Weakness[]>([]);
  const [items, setItems] = useState<CounterargumentItem[]>([]);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(
    factPattern: string,
    argument: string,
    files: File[],
  ) {
    setStatus("loading");
    setPhase("weaknesses");
    setWeaknesses([]);
    setItems([]);
    setError(null);
    try {
      await streamAnalysis(factPattern, argument, files, {
        onWeaknessItem: (weakness) => {
          setWeaknesses((prev) => [...prev, weakness]);
        },
        onWeaknesses: (data) => {
          setWeaknesses(data.weaknesses);
          setPhase("counterarguments");
        },
        onCounterargumentItem: (item) => {
          setItems((prev) => [...prev, item]);
        },
        onResult: (response) => {
          setResult(response);
          setStatus("done");
        },
        onError: (message) => {
          setError(message);
          setStatus("error");
        },
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Neznámá chyba");
      setStatus("error");
    }
  }

  return (
    <div className="page">
      <main className="app">
        <header className="masthead">
          <div className="seal-mark" aria-hidden="true">
            §
          </div>
          <div>
            <h1>Analýza protiargumentů</h1>
            <p className="subtitle">
              Otestujte svůj právní argument proti nejsilnějším
              protiargumentům, které by mohla vznést protistrana.
            </p>
          </div>
        </header>

        <ArgumentForm
          onSubmit={handleSubmit}
          disabled={status === "loading"}
        />
        {status === "loading" && (
          <>
            <LoadingState
              phase={phase}
              percent={computePercent(phase, weaknesses, items)}
            />
            {weaknesses.length > 0 && (
              <div className="cards">
                {weaknesses.map((weakness, index) => (
                  <AnalysisCard
                    key={index}
                    weakness={weakness.weakness}
                    item={
                      items.find((item) => item.weakness === weakness.weakness) ??
                      null
                    }
                  />
                ))}
              </div>
            )}
          </>
        )}
        {status === "error" && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        {status === "done" && result && <ResultCards result={result} />}
      </main>
    </div>
  );
}
