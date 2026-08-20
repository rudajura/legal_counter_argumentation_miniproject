# Argument Stress-Test (Analýza protiargumentů)

*[Česká verze](README.cs.md)*

A PoC tool that stress-tests a legal argument against the strongest
counterarguments the opposing side could raise. The user enters a fact
pattern and their own argument (optionally with attached PDF documents), and
a reasoning model (OpenAI, e.g. GPT-5.5) first finds weaknesses in the
argument, then turns each weakness into an opposing counsel's
counterargument, complete with a strength estimate and reasoning.

## Screenshots

**Input form** — fact pattern, your own argument, optional PDF attachments,
and two demo examples for a quick try:

![Input form](images/overview.png)

**Analysis result** — a risk summary plus cards for each weakness,
counterargument, strength estimate, and reasoning:

![Counterargument analysis](images/counter-arguments.png)

## How the app works

The analysis runs in two phases that feed into each other and stream into
the UI in real time over Server-Sent Events:

1. **Phase 1 — finding weaknesses.** The model receives the fact pattern and
   the user's argument and, acting as a legal analyst, identifies the 3–5
   weakest points in the argument (unsupported claims, disputable legal
   characterizations, missing evidence, alternative readings of the law).
2. **Phase 2 — counterarguing.** The model switches into the role of
   opposing counsel and, for each weakness found, formulates the strongest
   realistic counterargument, rates its strength (`low` / `medium` /
   `high`), adds brief reasoning, and finishes with an overall risk summary.

Both phases stream partial items (JSON array elements) as soon as the model
finishes them — the user sees weaknesses and counterarguments appear
progressively, instead of waiting for the whole generation to complete.

## Features

- **Two-phase AI analysis** — weaknesses first, then counterarguments with a
  strength estimate (low/medium/high) and reasoning, topped off with an
  overall summary.
- **Streamed results (SSE)** — a live progress bar, elapsed time, and
  weakness/counterargument cards fill in as they arrive, without waiting for
  the full response.
- **PDF attachment upload** — drag & drop or file picker, any number of
  PDFs; text is extracted from them (pypdf) and appended to the fact
  pattern.
- **Automatic fact-pattern extraction from PDF** — a "Extract fact pattern
  from PDF" button lets a smaller/faster model (`gpt-5.4-nano`) summarize
  just the facts from the uploaded documents (termination notice, contract,
  lawsuit…) into the fact-pattern field, with no legal assessment.
- **Demo examples** — two preset cases (defective work claim, invalid
  termination) for trying the tool instantly without writing your own text.
- **Error handling** — an error in any phase of the stream (e.g. an OpenAI
  API outage) is shown to the user as a readable message, and the connection
  is also checked for premature termination.

## Architecture

```
frontend (React 19 + Vite + TypeScript)
   │  fetch + Server-Sent Events
   ▼
backend (FastAPI, async)
   │  OpenAI Responses API (streamed structured output, JSON schema)
   ▼
OpenAI (reasoning model, e.g. gpt-5.5 / gpt-5.6-terra)
```

- **Backend** (`backend/app`): a FastAPI application. `main.py` defines the
  endpoints, `openai_client.py` calls the OpenAI Responses API with a strict
  JSON schema and, for the streaming endpoint, incrementally parses the
  array of items (`streaming_json.py`) before the full response completes.
  `pdf_extract.py` extracts text from PDFs (pypdf), `sse.py` formats SSE
  events. Prompts live in `backend/tools/prompts/` (phase 1, phase 2, fact
  extraction).
- **Frontend** (`frontend/src`): `ArgumentForm` (input form, upload, demo
  examples), `LoadingState` (phase-aware progress bar), `AnalysisCard` /
  `ResultCards` (rendering weaknesses and counterarguments), `api/client.ts`
  (SSE stream parsing).

## Running it

### Docker

```bash
cp backend/.env.example backend/.env  # fill in OPENAI_API_KEY
docker compose up --build
```

Open `http://localhost:5173` — same ports and CORS setup as local dev, just
containerized, so the browser talks to the frontend and backend directly on
their own ports.

### Configuration (`backend/.env`)

| Variable                  | Meaning                                                       | Default         |
|----------------------------|-----------------------------------------------------------------|-----------------|
| `OPENAI_API_KEY`          | OpenAI API key (required)                                     | —               |
| `OPENAI_MODEL`            | Reasoning model for phases 1 and 2 (weaknesses, counterarguments) | `gpt-5.5`    |
| `OPENAI_REASONING_EFFORT` | Reasoning effort level (`low` / `medium` / `high`)             | `high`          |
| `OPENAI_EXTRACTION_MODEL` | Faster model for extracting the fact pattern from PDFs         | `gpt-5.4-nano`  |

## Tests (backend)

```bash
cd backend
source .venv/bin/activate
pytest -v
```

Tests cover the API endpoints, the OpenAI client, PDF extraction, prompts,
schemas, SSE formatting, and incremental JSON stream parsing.

## License

[MIT](LICENSE)
