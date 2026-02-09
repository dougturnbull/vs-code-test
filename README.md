# FastAPI Calculator

A small FastAPI app that serves a modern calculator UI and exposes a JSON API endpoint for evaluating expressions.

## Features

- Modern calculator UI served from `static/`
- `POST /api/calc` returns results as JSON
- Safe expression evaluation (no `eval`): supports
  - `+`, `-`, `*`, `/`
  - exponent: `^` (also accepts `**`)
  - parentheses: `(`, `)`
  - square root: `sqrt(x)` (UI has a `√` button)
- Light/dark theme toggle in the UI (persisted in `localStorage`)

## Requirements

- Python 3.10+ (you’re currently using Python 3.13)

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install fastapi "uvicorn[standard]"
```

## Run

### Option 1: Run via `calculator.py`

```bash
python calculator.py
```

Then open:

- http://127.0.0.1:8000

### Option 2: Run via uvicorn

```bash
uvicorn calculator:app --reload --host 127.0.0.1 --port 8000
```

## API

### Calculate

Request:

```bash
curl -sS http://127.0.0.1:8000/api/calc \
  -H 'Content-Type: application/json' \
  -d '{"expression":"sqrt(2^2 + 3^2)"}'
```

Response:

```json
{"result":3.605551275463989}
```

## Project Layout

- `calculator.py` — FastAPI app + expression evaluator
- `static/` — UI assets (`index.html`, `styles.css`, `app.js`)

## Notes

- The API intentionally only supports a small set of operators/functions for safety.
