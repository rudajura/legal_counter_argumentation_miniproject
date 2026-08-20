import { useState } from "react";
import { ArgumentForm } from "./components/ArgumentForm";
import { LoadingState, type LoadingPhase } from "./components/LoadingState";
import { ResultCards } from "./components/ResultCards";
import { streamAnalysis } from "./api/client";
import type { AnalyzeResponse } from "./types";
import "./App.css";

type Status = "idle" | "loading" | "error" | "done";

export default function App() {
  const [status, setStatus] = useState<Status>("idle");
  const [phase, setPhase] = useState<LoadingPhase>("weaknesses");
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(
    factPattern: string,
    argument: string,
    files: File[],
  ) {
    setStatus("loading");
    setPhase("weaknesses");
    setError(null);
    try {
      await streamAnalysis(factPattern, argument, files, {
        onWeaknesses: () => {
          setPhase("counterarguments");
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
        {status === "loading" && <LoadingState phase={phase} />}
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
