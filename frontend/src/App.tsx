import { useState } from "react";
import { ArgumentForm } from "./components/ArgumentForm";
import { LoadingState } from "./components/LoadingState";
import { ResultCards } from "./components/ResultCards";
import { analyzeArgument } from "./api/client";
import type { AnalyzeResponse } from "./types";
import "./App.css";

type Status = "idle" | "loading" | "error" | "done";

export default function App() {
  const [status, setStatus] = useState<Status>("idle");
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(
    factPattern: string,
    argument: string,
    files: File[],
  ) {
    setStatus("loading");
    setError(null);
    try {
      const response = await analyzeArgument(factPattern, argument, files);
      setResult(response);
      setStatus("done");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      setStatus("error");
    }
  }

  return (
    <main className="app">
      <h1>Argument Stress-Test</h1>
      <p className="subtitle">
        Test your legal argument against the strongest counterarguments the
        opposing side could raise.
      </p>
      <ArgumentForm onSubmit={handleSubmit} disabled={status === "loading"} />
      {status === "loading" && <LoadingState />}
      {status === "error" && <p className="error">{error}</p>}
      {status === "done" && result && <ResultCards result={result} />}
    </main>
  );
}
