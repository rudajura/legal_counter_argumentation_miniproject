import {
  useRef,
  useState,
  type DragEvent,
  type FormEvent,
  type KeyboardEvent,
} from "react";
import { demoExamples } from "../data/demoExamples";

interface ArgumentFormProps {
  onSubmit: (factPattern: string, argument: string, files: File[]) => void;
  disabled: boolean;
}

export function ArgumentForm({ onSubmit, disabled }: ArgumentFormProps) {
  const [factPattern, setFactPattern] = useState("");
  const [argument, setArgument] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit(factPattern, argument, files);
  }

  function loadDemo(index: number) {
    setFactPattern(demoExamples[index].factPattern);
    setArgument(demoExamples[index].argument);
  }

  function addFiles(fileList: FileList) {
    const pdfs = Array.from(fileList).filter(
      (file) => file.type === "application/pdf",
    );
    if (pdfs.length > 0) {
      setFiles((prev) => [...prev, ...pdfs]);
    }
  }

  function removeFile(index: number) {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  }

  function openFileDialog() {
    if (!disabled) fileInputRef.current?.click();
  }

  function handleDropzoneKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openFileDialog();
    }
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    if (disabled) return;
    addFiles(event.dataTransfer.files);
  }

  return (
    <form onSubmit={handleSubmit} className="argument-form">
      <div>
        <p className="quick-start-label">Rychlý start</p>
        <div className="demo-buttons">
          {demoExamples.map((demo, index) => (
            <button
              type="button"
              key={demo.label}
              className="chip-button"
              onClick={() => loadDemo(index)}
              disabled={disabled}
            >
              {demo.label}
            </button>
          ))}
        </div>
      </div>

      <div className="form-grid">
        <label className="field">
          <span className="field-heading">Skutkový stav</span>
          <textarea
            value={factPattern}
            onChange={(event) => setFactPattern(event.target.value)}
            rows={8}
            required
            disabled={disabled}
            placeholder="Popište relevantní fakta případu…"
          />
        </label>

        <label className="field">
          <span className="field-heading">Můj argument / stanovisko</span>
          <textarea
            value={argument}
            onChange={(event) => setArgument(event.target.value)}
            rows={8}
            required
            disabled={disabled}
            placeholder="Formulujte právní argument, který chcete otestovat…"
          />
        </label>
      </div>

      <div className="field">
        <span className="field-heading">Přiložené dokumenty (nepovinné)</span>
        <div
          className={
            "dropzone" +
            (isDragging ? " dropzone-active" : "") +
            (disabled ? " dropzone-disabled" : "")
          }
          role="button"
          tabIndex={disabled ? -1 : 0}
          aria-label="Nahrát PDF dokumenty"
          aria-disabled={disabled}
          onClick={openFileDialog}
          onKeyDown={handleDropzoneKeyDown}
          onDragOver={(event) => {
            event.preventDefault();
            if (!disabled) setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
        >
          <svg
            className="dropzone-icon"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path d="M12 3v12m0-12 4 4m-4-4-4 4" />
            <path d="M5 17v2a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-2" />
          </svg>
          <p>
            <strong>Přetáhněte PDF soubory</strong> nebo klikněte pro výběr
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            multiple
            hidden
            onChange={(event) => {
              if (event.target.files) addFiles(event.target.files);
              event.target.value = "";
            }}
            disabled={disabled}
          />
        </div>

        {files.length > 0 && (
          <ul className="file-chips">
            {files.map((file, index) => (
              <li className="file-chip" key={`${file.name}-${index}`}>
                <span className="file-chip-name">{file.name}</span>
                <button
                  type="button"
                  className="file-chip-remove"
                  onClick={() => removeFile(index)}
                  disabled={disabled}
                  aria-label={`Odebrat ${file.name}`}
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <button type="submit" className="submit-button" disabled={disabled}>
        Otestovat můj argument
      </button>
    </form>
  );
}
