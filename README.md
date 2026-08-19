# Argument Stress-Test

PoC tool that stress-tests a legal argument against the strongest
counterarguments the opposing side could raise. The user enters a fact
pattern and their own argument (optionally attaching PDFs); a reasoning
model (Claude, extended thinking) first finds weaknesses, then turns each
into an opposing counsel's counterargument with a strength estimate.

Why: CODEXIS AI helps build one-sided argumentation but does not generate
the opposing side's counterarguments. This tool exists as a "stress test"
for an argument before it's actually used.

See [task.md](task.md) for the full specification and
[docs/superpowers/plans/2026-08-19-argumentacni-oponentura.md](docs/superpowers/plans/2026-08-19-argumentacni-oponentura.md)
for the implementation plan.

## Running it

### Prerequisites

Python 3.11+ and Node.js 20+. The frontend pins `vite@6` / `@vitejs/plugin-react@4`
for compatibility down to Node 18/20/22 (verified working on Node 22.8).

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env  # fill in ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env  # default value works with the backend above
npm run dev
```

Open `http://localhost:5173`.

## Tests (backend)

```bash
cd backend
source .venv/bin/activate
pytest -v
```
