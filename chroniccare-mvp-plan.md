# ChronicCare AI — Hackathon MVP Implementation Plan

## Overview

Build a complete, demo-ready hackathon MVP on top of the existing ChronicCareAI skeleton.
The goal is to extend — not rewrite — what works, adding a patient-facing dashboard, a
healthcare-provider dashboard, trend charts, an agent-tools layer, and provider alerts,
while keeping all AI inference in IBM Granite 4-H Small and all numerical logic deterministic.

**User decisions recorded:**
- `/` redirects to `/patient` — the patient dashboard is the homepage
- Provider dashboard: risk analysis is triggered manually per patient row click, not on page load

### What already works (do NOT touch)
- `ai/watsonx_client.py` — Granite 4-H Small via watsonx.ai, `.env` loading, prompt template
- `health/risk_engine.py` — deterministic 5-factor risk scoring (score 0–7, levels Low/Moderate/High/Critical)
- `health/trend_engine.py` — first-vs-last-row delta trend detection from CSV
- `app.py` — Flask routes `/` and `/analyze`
- `data/patient_data.csv` — P001 five-day history
- `.env` configuration

### What needs to be built

| Area | Gap |
|------|-----|
| Agent tools layer | `ai/agent_tools.py` — wraps existing functions as named tools |
| Expanded CSV data | Three patients (Diabetes, Hypertension, Heart Condition) with 7-day history |
| Expanded risk engine | Condition-aware thresholds and `generate_health_summary` tool |
| Provider alert logic | `create_provider_alert` tool in agent layer |
| New Flask routes | `/patient`, `/provider`, `/api/history/<id>`, `/api/alert` |
| Patient dashboard | `templates/patient.html` — charts + AI summary |
| Provider dashboard | `templates/provider.html` — patient list, alerts table, charts |
| Chart rendering | Chart.js for glucose, BP, heart rate, sleep trend charts |
| Shared layout | `templates/base.html` or inline shared styles |
| `requirements.txt` | Missing from project |

---

## Sub-Tasks

---

### Sub-Task 1 — Create `requirements.txt` and expand `data/patient_data.csv`

**Status:** `[x] done`

**Intent:**
Provide a reproducible install manifest (needed for any hackathon judge to run the project)
and expand the synthetic dataset so three distinct patients exist — one per supported condition.
This data is consumed by `detect_trends()` and displayed in charts. No existing code changes.

**Expected Outcomes:**
- `requirements.txt` lists all four runtime dependencies
- `data/patient_data.csv` contains three patients: P001 (Diabetes), P002 (Hypertension), P003 (Heart Condition), each with 7 rows (days)
- Running `python health/trend_engine.py` after the change still works for P001
- `detect_trends("P002")` and `detect_trends("P003")` return non-empty trend dicts

**Todo List:**
1. Create `requirements.txt` with `flask`, `pandas`, `ibm-watsonx-ai`, `python-dotenv`
2. Append 7 rows for P002 (Hypertension patient, age 58) to the CSV — values should show a worsening BP trend so the demo is compelling
3. Append 7 rows for P003 (Heart Condition patient, age 67) to the CSV — values should show elevated heart rate and worsening trend
4. Keep all P001 rows intact

**Relevant Context:**
- CSV columns: `patient_id,date,glucose,systolic_bp,diastolic_bp,heart_rate,sleep_hours,medication_adherence`
- `detect_trends()` in `health/trend_engine.py` reads this file at `"data/patient_data.csv"` (CWD-relative)
- Only `patient_id`, `date`, `glucose`, `systolic_bp`, `diastolic_bp`, `heart_rate`, `sleep_hours` are used by trend engine (medication_adherence column exists but is not read there)

---

### Sub-Task 2 — Create `ai/agent_tools.py` (agent tools layer)

**Status:** `[x] done`

**Intent:**
Introduce a named-tools wrapper that organises the five required agent functions:
`calculate_risk`, `get_patient_history`, `detect_trends`, `generate_health_summary`, and
`create_provider_alert`. This layer is what the Flask routes and future extensions call;
it keeps `app.py` clean and satisfies the hackathon "agent-style tools" requirement.
`ask_granite()` in `watsonx_client.py` is called only from `generate_health_summary` — no other file imports it directly after this change.

**Expected Outcomes:**
- `ai/agent_tools.py` exports five callable functions matching the required tool names
- `generate_health_summary(patient, risk_result, trends)` calls `ask_granite()` and returns the text string
- `create_provider_alert(patient, risk_result)` returns a structured dict with `patient_id`, `risk_level`, `risk_score`, `warnings`, `timestamp`, `message` — no external call, purely deterministic
- `get_patient_history(patient_id)` reads the CSV and returns a list of dicts (one per row), sorted by date
- `calculate_risk` and `detect_trends` are re-exported references to the existing functions (thin wrappers or direct imports — no duplication of logic)
- No existing file is modified in this sub-task

**Todo List:**
1. Create `ai/agent_tools.py`
2. Import `calculate_risk` from `health.risk_engine` and re-export it
3. Import `detect_trends` from `health.trend_engine` and re-export it
4. Implement `get_patient_history(patient_id)` — reads `data/patient_data.csv`, filters by `patient_id`, returns list of row dicts sorted by `date`
5. Implement `generate_health_summary(patient, risk_result, trends)` — builds combined context dict and calls `ask_granite(patient, {"risk": risk_result, "trends": trends})`; returns string
6. Implement `create_provider_alert(patient, risk_result)` — returns alert dict only when `risk_level` is "High" or "Critical"; returns `None` otherwise; uses `datetime.utcnow()` for timestamp
7. Remove the module-level inline test code side-effect: in this file, do NOT call any function at the module level

**Relevant Context:**
- `ask_granite(patient_data, risk_result)` signature in `ai/watsonx_client.py` — second arg is named `risk_result` but currently receives `combined_result` from `app.py`; this inconsistency is fixed here by always passing `{"risk": ..., "trends": ...}` as the second argument and updating the Granite prompt accordingly in Sub-Task 3
- `get_patient_history` must use `Path(__file__).resolve().parent.parent / "data/patient_data.csv"` — NOT a CWD-relative path — so it works regardless of where Flask is launched from

---

### Sub-Task 3 — Update `ai/watsonx_client.py` prompt to use trends

**Status:** `[ ] pending`

**Intent:**
Fix the latent gap documented in AGENTS.md: the `ask_granite()` prompt currently only
references `patient_data` and `risk_result` dict keys, but `app.py` passes a combined dict
containing both `risk` and `trends`. The prompt never surfaces trend data to Granite.
This sub-task makes Granite actually use the trend analysis in its response.

**Expected Outcomes:**
- `ask_granite(patient_data, combined)` prompt template references both `combined["risk"]` and `combined["trends"]`
- Granite response explicitly addresses worsening trends when present
- The 6-point output structure is preserved (risk summary, observations, concerns, lifestyle, medication, when to contact professional)
- The disclaimer language is preserved exactly

**Todo List:**
1. In `ai/watsonx_client.py`, update the f-string prompt to extract `risk` and `trends` from the second argument
2. Add a "Historical Trend Analysis:" section to the prompt between "Risk Engine Result" and "Provide:"
3. Keep all IMPORTANT bullet disclaimers unchanged
4. Do not change function signature, credentials setup, or model ID

**Relevant Context:**
- `ask_granite(patient_data, risk_result)` — second parameter is passed `{"risk": risk_result, "trends": trend_result}` by `app.py`
- The prompt must remain patient-friendly and concise

---

### Sub-Task 4 — Extend `health/risk_engine.py` with condition-aware thresholds

**Status:** `[ ] pending`

**Intent:**
The current `calculate_risk()` applies the same thresholds regardless of whether the patient
has Diabetes, Hypertension, or a Heart Condition. Condition-aware scoring makes the demo
medically coherent and differentiates the three patient profiles. The scoring scale and
return dict shape must stay identical so no callers break.

**Expected Outcomes:**
- `calculate_risk(patient)` checks `patient.get("condition", "")` and applies condition-specific scoring additions
- For Diabetes: elevated glucose threshold remains 180; add check for glucose > 250 as a second-tier warning ("Critically high glucose")
- For Hypertension: lower the BP trigger to systolic > 130 or diastolic > 85 for an additional +1 warning ("Hypertension threshold reached")
- For Heart Condition: heart rate > 90 (lower than the current 100) adds a warning ("Elevated heart rate for cardiac patient")
- Return dict shape `{"risk_score": int, "risk_level": str, "warnings": list}` is unchanged
- Existing `calculate_risk` tests in `test_ai.py` for P001/Diabetes still pass

**Todo List:**
1. Add condition-aware block in `calculate_risk()` after existing generic checks
2. Add Diabetes-specific second-tier glucose check
3. Add Hypertension-specific lower BP threshold check
4. Add Heart Condition-specific lower heart-rate threshold check
5. Do NOT change the risk classification bands (Low/Moderate/High/Critical thresholds)
6. Do NOT add or remove keys from the return dict
7. Remove the module-level inline test execution code (wrap it in `if __name__ == "__main__":`)

**Relevant Context:**
- `calculate_risk` is imported in `app.py`, `test_ai.py`, and will be imported in `ai/agent_tools.py`
- The inline test patient (glucose=185, systolic_bp=145, condition="Diabetes") should still yield "High" or "Critical"

---

### Sub-Task 5 — Add new Flask routes to `app.py`

**Status:** `[x] done`

**Intent:**
Introduce the routes that back the two new dashboards and the provider alert endpoint.
The existing `/` and `/analyze` routes are unchanged. New routes are thin orchestration:
they call agent tools and return JSON or render templates.

**Expected Outcomes:**
- `GET /` redirects to `/patient`
- `GET /patient` renders `templates/patient.html`
- `GET /provider` renders `templates/provider.html`
- `GET /api/history/<patient_id>` returns `get_patient_history(patient_id)` as JSON array
- `GET /api/patients` returns a hardcoded list of demo patients: `[{patient_id, name, age, condition}]` for P001, P002, P003
- `POST /api/alert` accepts `{patient_id, ...vitals}`, runs `calculate_risk`, runs `create_provider_alert`, returns alert dict or `{"alert": null}` if no alert

**Todo List:**
1. Add import of `get_patient_history`, `create_provider_alert`, `generate_health_summary` from `ai.agent_tools`; add `redirect` to the Flask import
2. Change `GET /` route body to `return redirect("/patient")`
3. Add `GET /patient` route
4. Add `GET /provider` route
5. Add `GET /api/history/<patient_id>` route
6. Add `GET /api/patients` route with hardcoded demo patient list including name, age, condition for P001/P002/P003
7. Add `POST /api/alert` route
8. Keep existing `POST /analyze` route exactly as-is

**Relevant Context:**
- `app.py` currently imports: `calculate_risk`, `detect_trends`, `ask_granite`
- After this sub-task, `ask_granite` should no longer be imported directly in `app.py` — `generate_health_summary` from `agent_tools` replaces it
- `app.run(debug=True)` stays at bottom

---

### Sub-Task 6 — Create `templates/patient.html` (Patient Dashboard)

**Status:** `[x] done`

**Intent:**
Replace the current single-page form with a dedicated patient-facing dashboard. This page
shows the patient's current vitals input form, real-time risk level with color coding,
AI-generated patient-friendly summary from Granite, medication adherence reminder, and
four trend charts. It is the primary demo view for the patient persona.

**Expected Outcomes:**
- Page loads at `http://localhost:5000/patient`
- Patient selector dropdown pre-populates from `/api/patients`
- On patient select, history loads from `/api/history/<id>` and charts render
- Form submits to `/analyze`, result section shows: risk badge (color-coded by level), risk score, warnings list, Granite AI summary
- Four Chart.js line charts: Glucose, Systolic BP, Heart Rate, Sleep Hours — each plotting 7-day history
- Medication adherence reminder banner appears when last reading was "Missed"
- Color scheme: Low=green, Moderate=amber, High=orange, Critical=red
- Professional UI using the existing `#123c69` brand color
- Page is fully self-contained (no external CSS frameworks requiring internet except Chart.js CDN)

**Todo List:**
1. Create `templates/patient.html`
2. Add header matching existing `#123c69` brand style
3. Add patient selector `<select>` populated via `/api/patients` fetch on page load
4. Add vitals input form (same fields as `index.html`; pre-fills defaults when patient is selected based on their last CSV row)
5. Add "Analyze" button calling `analyzePatient()` JS function posting to `/analyze`
6. Add result section with: risk level badge (color-coded), risk score, warnings list, Granite AI response
7. Add Chart.js CDN script tag
8. Add four canvas elements for trend charts
9. Implement `renderCharts(history)` JS function: extracts dates + metric arrays from `/api/history` response and draws line charts
10. Add medication adherence reminder banner (shown/hidden based on last CSV row `medication_adherence` value)
11. Auto-trigger chart render when patient is selected from dropdown

**Relevant Context:**
- Chart.js CDN: `https://cdn.jsdelivr.net/npm/chart.js`
- `/api/history/<patient_id>` returns list of row dicts with keys: `patient_id, date, glucose, systolic_bp, diastolic_bp, heart_rate, sleep_hours, medication_adherence`
- `/analyze` response shape: `{patient, risk: {risk_score, risk_level, warnings}, trends, ai_response}`
- Keep `index.html` unchanged — it remains accessible at `/`

---

### Sub-Task 7 — Create `templates/provider.html` (Provider Dashboard)

**Status:** `[ ] pending`

**Intent:**
Build the healthcare-provider view showing all three demo patients as a summary table,
active alerts for High/Critical patients, and per-patient detail with trend charts when
a patient row is selected. This is the second primary demo view.

**Expected Outcomes:**
- Page loads at `http://localhost:5000/provider`
- Patient summary table shows all three patients with: ID, name, age, condition — risk level column reads "Pending" until provider clicks the row
- Clicking a patient row triggers: fetch `/api/history/<id>` to render trend charts; post last row vitals to `/analyze` to get risk level, warnings, and Granite summary
- Detail panel updates with risk badge, warnings, Granite summary after analysis completes
- Alert banner appears in detail panel if analysed patient is High or Critical
- "Generate Alert" button appears in detail panel for High/Critical patients; posts to `/api/alert`; renders structured alert card
- Charts: same four metrics as patient dashboard (Glucose, Systolic BP, Heart Rate, Sleep Hours)
- Provider-specific language in UI (e.g., "Clinical Risk Level", "Provider Alert")

**Todo List:**
1. Create `templates/provider.html`
2. Add header with "ChronicCare AI — Provider Dashboard" and brand styling
3. On page load: fetch `/api/patients` and populate the patient summary table (name, age, condition, risk = "Pending")
4. On row click: fetch `/api/history/<id>`, render four trend charts, post last-row vitals to `/analyze`, populate detail panel
5. Detail panel: risk badge, score, warnings, Granite AI summary
6. If `risk_level` is "High" or "Critical": show alert banner and "Generate Alert" button in detail panel
7. "Generate Alert" button posts `{patient_id, ...last_vitals}` to `/api/alert`, renders returned alert dict as a styled card
8. Alert card shows: patient name, risk level badge, risk score, warnings list, alert message, timestamp

**Relevant Context:**
- `/api/patients` returns: `[{patient_id, name, age, condition}]`
- `/api/history/<id>` last row = most recent vitals; use `history[history.length - 1]` in JS
- Risk level colors: Low=#28a745, Moderate=#ffc107, High=#fd7e14, Critical=#dc3545
- `/api/alert` returns: `{patient_id, risk_level, risk_score, warnings, timestamp, message}` or `{alert: null}`

---

### Sub-Task 8 — Fix inline test side-effects in `health/trend_engine.py`

**Status:** `[ ] pending`

**Intent:**
The module-level test code in `health/trend_engine.py` prints to stdout on every import,
polluting Flask startup logs. Wrapping it in `if __name__ == "__main__":` is a one-line
fix that prevents import side effects without changing any logic.

**Expected Outcomes:**
- `from health.trend_engine import detect_trends` in Flask produces no console output
- `python health/trend_engine.py` still prints the trend analysis output
- `detect_trends()` logic is completely unchanged

**Todo List:**
1. In `health/trend_engine.py`, wrap lines 82–88 (the `# Test` block) in `if __name__ == "__main__":`
2. Verify the `detect_trends` function body itself is not modified

**Relevant Context:**
- `risk_engine.py` has the same issue; it was addressed in Sub-Task 4
- `trend_engine.py` lines 82–88: `result = detect_trends("P001")` and print loop

---

### Sub-Task 9 — Create `requirements.txt` (if not done in Sub-Task 1)

> Note: `requirements.txt` is covered in Sub-Task 1. This sub-task slot is reserved for
> end-to-end smoke test validation once all sub-tasks are complete.

**Status:** `[ ] pending`

**Intent:**
Verify the full application runs end-to-end and the demo flow works as described below.

**Expected Outcomes:**
- `pip install -r requirements.txt` succeeds
- `python app.py` starts without any import-time print statements
- `GET /` returns the original index page
- `GET /patient` renders patient dashboard with charts
- `GET /provider` renders provider dashboard with patient table
- `POST /analyze` with P001 data returns risk + trends + AI response
- `GET /api/history/P001` returns 7 rows (5 existing + wait: still 5 per spec, no change needed to P001 count)
- `GET /api/history/P002` returns 7 rows for the hypertension patient
- `POST /api/alert` with High/Critical patient returns structured alert
- No import-time stdout from any module

**Todo List:**
1. Run `python app.py` and confirm no print side-effects on startup
2. Open browser, visit `/patient`, select P001, verify charts render and analysis works
3. Visit `/provider`, verify patient table and alert banner display correctly
4. Trigger alert for P002 or P003, verify alert card appears
5. Update AGENTS.md to reflect new routes and file structure

---

## Final Demo Flow

```
Demo persona 1 — Patient View
  1. Open /patient
  2. Select "P001 — Diabetes" from dropdown
  3. Charts auto-render showing 5-day worsening trends
  4. Click "Analyze" — Granite generates patient-friendly summary
  5. Medication reminder banner appears (last reading: Missed)

Demo persona 2 — Provider View
  1. Open /provider
  2. All three patients appear in summary table with risk badges
  3. Alert banner highlights P001 (Critical) and P002/P003 if High/Critical
  4. Click P001 row → detail panel opens with charts and last AI summary
  5. Click "Generate Alert" → alert card appears with timestamp, warnings, message
```

---

## File Map

### Files to create
| File | Sub-Task |
|------|----------|
| `requirements.txt` | 1 |
| `ai/agent_tools.py` | 2 |
| `templates/patient.html` | 6 |
| `templates/provider.html` | 7 |

### Files to modify
| File | Sub-Task | Change |
|------|----------|--------|
| `data/patient_data.csv` | 1 | Add P002, P003 rows |
| `ai/watsonx_client.py` | 3 | Update prompt to use trends |
| `health/risk_engine.py` | 4 | Condition-aware thresholds + `if __name__` guard |
| `health/trend_engine.py` | 8 | `if __name__` guard on inline test |
| `app.py` | 5 | Add new routes |

### Files to leave unchanged
| File | Reason |
|------|--------|
| `test_ai.py` | Works; still valid for integration smoke-testing |
| `test_watsonx.py` | Works; connectivity test unchanged |
| `.env` | User-managed credential file |
