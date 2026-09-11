# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Stack
- Python 3.13, Flask, pandas, `ibm-watsonx-ai`, `python-dotenv`
- No `requirements.txt` or `pyproject.toml` — dependencies are implicit; install manually via pip.

## Run / Test Commands
```bash
# Start the Flask app
python app.py

# Integration test: risk engine + Granite AI (requires .env with valid credentials)
python test_ai.py

# Connectivity smoke-test for watsonx credentials only
python test_watsonx.py

# Run individual engine modules directly (each has inline test at bottom)
python health/risk_engine.py
python health/trend_engine.py
```
No pytest or test framework — tests are plain scripts executed with `python`.

## Critical Environment Setup
`.env` must live in the **project root** (next to `app.py`).  
Required keys: `WATSONX_APIKEY`, `WATSONX_PROJECT_ID`, `WATSONX_URL`.  
`ai/watsonx_client.py` resolves `.env` via `Path(__file__).parent.parent / ".env"` — moving the file will break loading.  
`test_watsonx.py` uses `Path(__file__).parent / ".env"` (same directory) — it expects `.env` in the project root too when run from there.

## Architecture: Request Flow
```
POST /analyze  →  calculate_risk(patient)          [health/risk_engine.py]
               →  detect_trends(patient_id)         [health/trend_engine.py]
               →  ask_granite(patient, combined)    [ai/watsonx_client.py]
               →  jsonify({patient, risk, trends, ai_response})
```

## Non-Obvious Patterns

### `health/trend_engine.py`
- `detect_trends()` hard-codes the CSV path as `"data/patient_data.csv"` (relative to CWD).  
  **Must be run from project root** or it will fail with a FileNotFoundError.
- Trends are computed as first-vs-last row delta only — no averaging or smoothing.
- Only patient `P001` exists in the sample CSV; other IDs return `{"message": "No patient history found."}`.

### `health/risk_engine.py` and `health/trend_engine.py`
- Both files contain inline test code at module level (no `if __name__ == "__main__":` guard).  
  Importing either module will execute the test print statements.

### `ai/watsonx_client.py`
- Model ID: `"ibm/granite-4-h-small"` — hardcoded, not configurable via env.
- Credentials are read at **module import time** (top-level `os.getenv` calls) — `.env` must be loaded before import.
- `ask_granite()` creates a new `ModelInference` instance on every call (no connection reuse).

## Code Style
- 4-space indentation, snake_case throughout.
- Imports: stdlib → third-party → local, one blank line between groups.
- No type annotations anywhere in the codebase.
- Long expressions broken across lines with parentheses (see `trend_engine.py` pandas chaining style).
- No linter config files present; follow PEP 8 manually.
