"""
test_dashboard.py

Patient dashboard content tests — verifies every requirement for the
patient dashboard and visualization phase. No watsonx credentials needed.
"""

import sys
import os
import json
import io
import contextlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Suppress import-time print side-effects from engines
with contextlib.redirect_stdout(io.StringIO()):
    from app import app

app.config["TESTING"] = True
client = app.test_client()

print("=== Patient Dashboard Content Tests ===")
print()

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def get_patient_html():
    r = client.get("/patient")
    assert r.status_code == 200, f"GET /patient returned {r.status_code}"
    return r.data.decode("utf-8")

body = get_patient_html()

# ---------------------------------------------------------------------------
# 1. Page loads successfully
# ---------------------------------------------------------------------------
r = client.get("/patient")
assert r.status_code == 200
assert r.content_type.startswith("text/html")
print("PASS 01: GET /patient returns 200 HTML")

# ---------------------------------------------------------------------------
# 2. Professional header and branding
# ---------------------------------------------------------------------------
assert "ChronicCare AI" in body
assert "AI-Powered Chronic Disease Monitoring" in body
assert "#123c69" in body, "Brand color #123c69 must be present in CSS"
print("PASS 02: Header and branding present")

# ---------------------------------------------------------------------------
# 3. Patient selector dropdown wired to /api/patients
# ---------------------------------------------------------------------------
assert "patientSelect" in body
assert "/api/patients" in body
assert "onPatientChange" in body
print("PASS 03: Patient selector dropdown present and wired")

# ---------------------------------------------------------------------------
# 4. Chart.js loaded and all 4 chart canvases present
# ---------------------------------------------------------------------------
assert "chart.js" in body.lower(), "Chart.js CDN must be included"
assert 'id="chartGlucose"' in body,  "Glucose chart canvas missing"
assert 'id="chartBP"'      in body,  "Blood pressure chart canvas missing"
assert 'id="chartHR"'      in body,  "Heart rate chart canvas missing"
assert 'id="chartSleep"'   in body,  "Sleep chart canvas missing"
print("PASS 04: Chart.js loaded; all 4 chart canvases present")

# ---------------------------------------------------------------------------
# 5. renderCharts() function defined
# ---------------------------------------------------------------------------
assert "function renderCharts" in body
assert "chartGlucose" in body
assert "chartBP" in body
assert "chartHR" in body
assert "chartSleep" in body
print("PASS 05: renderCharts() function defined with all 4 metrics")

# ---------------------------------------------------------------------------
# 6. loadPatientHistory() calls /api/history/
# ---------------------------------------------------------------------------
assert "loadPatientHistory" in body
assert "/api/history/" in body
print("PASS 06: loadPatientHistory() function present and calls /api/history/")

# ---------------------------------------------------------------------------
# 7. Risk score and level display elements present
# ---------------------------------------------------------------------------
assert 'id="riskBadge"'   in body,  "Risk badge element missing"
assert 'id="riskLevel"'   in body,  "Risk level element missing"
assert 'id="riskScore"'   in body,  "Risk score element missing"
assert 'id="riskHeading"' in body,  "Risk heading element missing"
# Color-coded risk classes
assert "risk-low"      in body
assert "risk-moderate" in body
assert "risk-high"     in body
assert "risk-critical" in body
print("PASS 07: Risk score/level display elements and color coding present")

# ---------------------------------------------------------------------------
# 8. Warnings list element present
# ---------------------------------------------------------------------------
assert 'id="warningsList"' in body
print("PASS 08: Warnings list element present")

# ---------------------------------------------------------------------------
# 9. Trends panel with all 4 trend indicators present
# ---------------------------------------------------------------------------
assert 'id="trendGlucose"' in body
assert 'id="trendBP"'      in body
assert 'id="trendHR"'      in body
assert 'id="trendSleep"'   in body
assert "renderTrends"      in body
print("PASS 09: Trends panel with all 4 metrics present")

# ---------------------------------------------------------------------------
# 10. Analyze Health button present
# ---------------------------------------------------------------------------
assert "Analyze Health" in body
assert "analyzePatient" in body
assert 'id="analyzeBtn"' in body
print("PASS 10: Analyze Health button present")

# ---------------------------------------------------------------------------
# 11. Granite AI health summary section present
# ---------------------------------------------------------------------------
assert 'id="aiResponse"'          in body
assert "Granite AI Health Summary" in body
assert "IBM Granite 4-H Small"     in body
assert "watsonx.ai"               in body
print("PASS 11: Granite AI health summary section present")

# ---------------------------------------------------------------------------
# 12. Medication adherence information and reminder present
# ---------------------------------------------------------------------------
assert 'id="medBanner"'          in body
assert "Medication Reminder"     in body
assert "medication_adherence"    in body
assert "missed"                  in body.lower()
assert "prescribed"              in body.lower()
print("PASS 12: Medication adherence info and reminder present")

# ---------------------------------------------------------------------------
# 13. Lifestyle recommendations panel present
# ---------------------------------------------------------------------------
assert 'id="lifestyleList"'            in body, "lifestyleList element missing"
assert "Lifestyle Recommendations"     in body, "Section header missing"
assert "LIFESTYLE_TIPS"                in body, "LIFESTYLE_TIPS data object missing"
assert "renderLifestyleTips"           in body, "renderLifestyleTips function missing"
assert "extractLifestyleSuggestions"   in body, "extractLifestyleSuggestions function missing"
assert "Diabetes" in body and "Hypertension" in body and "Heart Condition" in body, \
    "Lifestyle tips should cover all three conditions"
print("PASS 13: Lifestyle recommendations panel present with condition-specific tips")

# ---------------------------------------------------------------------------
# 14. Tips cover all three supported conditions
# ---------------------------------------------------------------------------
assert "low-glycaemic" in body or "glycaemic" in body, "Diabetes-specific tip missing"
assert "sodium" in body or "blood pressure medication" in body.lower(), "Hypertension-specific tip missing"
assert "cardiac" in body or "heart-healthy" in body, "Heart Condition-specific tip missing"
print("PASS 14: Condition-specific lifestyle content verified for all 3 conditions")

# ---------------------------------------------------------------------------
# 15. Disclaimer present
# ---------------------------------------------------------------------------
assert "monitoring and decision-support tool" in body
assert "does not diagnose" in body
assert "synthetic demo data" in body
print("PASS 15: Monitoring disclaimer present")

# ---------------------------------------------------------------------------
# 16. Navigation to provider view present
# ---------------------------------------------------------------------------
assert 'href="/provider"' in body
assert "Provider View" in body
print("PASS 16: Navigation link to provider view present")

# ---------------------------------------------------------------------------
# 17. Responsive layout CSS present
# ---------------------------------------------------------------------------
assert "@media" in body
assert "max-width" in body
print("PASS 17: Responsive/mobile CSS media queries present")

# ---------------------------------------------------------------------------
# 18. /api/patients returns correct structure for all 3 demo patients
# ---------------------------------------------------------------------------
r = client.get("/api/patients")
assert r.status_code == 200
patients = json.loads(r.data)
assert len(patients) == 3
conditions = {p["condition"] for p in patients}
assert "Diabetes"        in conditions
assert "Hypertension"    in conditions
assert "Heart Condition" in conditions
for p in patients:
    assert all(k in p for k in ("patient_id", "name", "age", "condition"))
print("PASS 18: /api/patients returns 3 patients covering all 3 conditions")

# ---------------------------------------------------------------------------
# 19. /api/history returns correct data structure for chart rendering
# ---------------------------------------------------------------------------
r = client.get("/api/history/P001")
h = json.loads(r.data)
assert len(h) >= 1
row = h[0]
chart_keys = ("date", "glucose", "systolic_bp", "diastolic_bp", "heart_rate", "sleep_hours", "medication_adherence")
for k in chart_keys:
    assert k in row, f"History row missing chart key: {k}"
# Verify dates are sorted (required by renderCharts)
dates = [r["date"] for r in h]
assert dates == sorted(dates), "History must be sorted ascending for correct chart rendering"
print("PASS 19: /api/history returns all chart-required keys, sorted by date")

# ---------------------------------------------------------------------------
# 20. Medication adherence info visible in history (last row drives banner)
# ---------------------------------------------------------------------------
r = client.get("/api/history/P001")
h = json.loads(r.data)
last = h[-1]
assert "medication_adherence" in last
assert last["medication_adherence"] in ("Taken", "Missed")
# P001 last row should be Missed (from CSV)
assert last["medication_adherence"] == "Missed", \
    f"P001 last row medication should be Missed, got {last['medication_adherence']}"
print("PASS 20: P001 last row medication_adherence=Missed (triggers banner in JS)")

# ---------------------------------------------------------------------------
# 21. POST /api/alert returns structured alert for high-risk vitals
# ---------------------------------------------------------------------------
vitals = {
    "patient_id": "P001", "age": 45, "condition": "Diabetes",
    "glucose": 195, "systolic_bp": 148, "diastolic_bp": 94,
    "heart_rate": 102, "sleep_hours": 5, "medication_adherence": "Missed"
}
r = client.post("/api/alert", data=json.dumps(vitals), content_type="application/json")
alert_resp = json.loads(r.data)
alert = alert_resp["alert"]
assert alert is not None
assert alert["risk_level"] in ("High", "Critical")
assert "message" in alert and "monitoring aid" in alert["message"]
print(f"PASS 21: POST /api/alert high-risk -> risk_level={alert['risk_level']}")

# ---------------------------------------------------------------------------
# 22. POST /api/alert returns null for low-risk vitals
# ---------------------------------------------------------------------------
low_vitals = {
    "patient_id": "P001", "age": 45, "condition": "Diabetes",
    "glucose": 110, "systolic_bp": 115, "diastolic_bp": 75,
    "heart_rate": 70, "sleep_hours": 7.5, "medication_adherence": "Taken"
}
r = client.post("/api/alert", data=json.dumps(low_vitals), content_type="application/json")
assert json.loads(r.data)["alert"] is None
print("PASS 22: POST /api/alert low-risk -> alert=null")

# ---------------------------------------------------------------------------
# 23. GET / redirects to /patient
# ---------------------------------------------------------------------------
r = client.get("/")
assert r.status_code in (301, 302)
assert "/patient" in r.headers.get("Location", "")
print("PASS 23: GET / redirects to /patient")

# ---------------------------------------------------------------------------
# 24. lifestyleAiNote element present in HTML for JS to populate
# ---------------------------------------------------------------------------
assert 'id="lifestyleAiNote"' in body
print("PASS 24: lifestyleAiNote element present for AI snippet display")

print()
print("=" * 55)
print("  ALL 24 PATIENT DASHBOARD TESTS PASSED")
print("=" * 55)
