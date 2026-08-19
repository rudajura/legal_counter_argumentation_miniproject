import { useState, type FormEvent } from "react";
import { demoExamples } from "../data/demoExamples";

interface ArgumentFormProps {
  onSubmit: (factPattern: string, argument: string, files: File[]) => void;
  disabled: boolean;
}

export function ArgumentForm({ onSubmit, disabled }: ArgumentFormProps) {
  const [factPattern, setFactPattern] = useState("");
  const [argument, setArgument] = useState("");
  const [files, setFiles] = useState<File[]>([]);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit(factPattern, argument, files);
  }

  function loadDemo(index: number) {
    setFactPattern(demoExamples[index].factPattern);
    setArgument(demoExamples[index].argument);
  }

  return (
    <form onSubmit={handleSubmit} className="argument-form">
      <div className="demo-buttons">
        {demoExamples.map((demo, index) => (
          <button
            type="button"
            key={demo.label}
            onClick={() => loadDemo(index)}
            disabled={disabled}
          >
            Load demo: {demo.label}
          </button>
        ))}
      </div>

      <label>
        Fact pattern
        <textarea
          value={factPattern}
          onChange={(event) => setFactPattern(event.target.value)}
          rows={6}
          required
          disabled={disabled}
        />
      </label>

      <label>
        My argument / position
        <textarea
          value={argument}
          onChange={(event) => setArgument(event.target.value)}
          rows={6}
          required
          disabled={disabled}
        />
      </label>

      <label>
        Attach PDF documents (optional)
        <input
          type="file"
          accept="application/pdf"
          multiple
          onChange={(event) => setFiles(Array.from(event.target.files ?? []))}
          disabled={disabled}
        />
      </label>

      <button type="submit" disabled={disabled}>
        Test my argument
      </button>
    </form>
  );
}
