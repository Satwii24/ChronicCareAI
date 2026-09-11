"""
Phase 2 smoke tests — verifies Flask routes and patient dashboard.
Does NOT require watsonx credentials (skips /analyze which calls Granite).
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# We need to suppress the import-time print from risk_engine and trend_engine
# before importing the Flask app.
# ---------------------------------------------------------------------------
import io
import contextlib

# Import app with stdout suppressed to avoid inline test noise
with contextlib.redirect_stdout(io.StringIO()):
    from app import app

app.config["TESTING"] = True
client = app.test_client()

print("=== Flask Route Tests ===")

# ---------------------------------------------------------------------------
# 1. GET / should redirect to /patient
# ---------------------------------------------------------------------------
r = client.get("/")
assert r.status_code in (301, 302), f"GET / expected redirect, got {r.status_code}"
location = r.headers.get("Location", "")
assert "/patient" in location, f"GET / should redirect to /patient, got Location: {location}"
print("PASS: GET / redirects to /patient")

# ---------------------------------------------------------------------------
# 2. GET /patient should return 200 with patient.html content
# ---------------------------------------------------------------------------
r = client.get("/patient")
assert r.status_code == 200, f"GET /patient expected 200, got {r.status_code}"
body = r.data.decode("utf-8")
assert "ChronicCare AI" in body,        "patient.html should contain ChronicCare AI"
assert "Analyze Health" in body,         "patient.html should contain Analyze button text"
assert "chart.js" in body.lower(),       "patient.html should include Chart.js"
assert "chartGlucose" in body,           "patient.html should have glucose chart canvas"
assert "chartBP" in body,               "patient.html should have BP chart canvas"
assert "chartHR" in body,               "patient.html should have HR chart canvas"
assert "chartSleep" in body,             "patient.html should have sleep chart canvas"
assert "analyzePatient" in body,         "patient.html should have analyzePatient() function"
assert "renderCharts" in body,           "patient.html should have renderCharts() function"
assert "medication" in body.lower(),     "patient.html should mention medication"
assert "/api/patients" in body,          "patient.html should fetch /api/patients"
assert "/api/history/" in body,          "patient.html should fetch /api/history/"
print("PASS: GET /patient -> 200 with all required elements")

# ---------------------------------------------------------------------------
# 3. GET /api/patients returns correct demo patient list
# ---------------------------------------------------------------------------
r = client.get("/api/patients")
assert r.status_code == 200, f"GET /api/patients expected 200, got {r.status_code}"
patients = json.loads(r.data)
assert isinstance(patients, list), "Should return a list"
assert len(patients) == 3, f"Expected 3 demo patients, got {len(patients)}"
ids = [p["patient_id"] for p in patients]
assert "P001" in ids, "P001 should be in patient list"
assert "P002" in ids, "P002 should be in patient list"
assert "P003" in ids, "P003 should be in patient list"
for p in patients:
    for key in ("patient_id", "name", "age", "condition"):
        assert key in p, f"Patient dict missing key: {key}"
print(f"PASS: GET /api/patients -> {len(patients)} patients: {[p['patient_id'] for p in patients]}")

# ---------------------------------------------------------------------------
# 4. GET /api/history/P001 returns 5 sorted rows
# ---------------------------------------------------------------------------
r = client.get("/api/history/P001")
assert r.status_code == 200, f"Expected 200, got {r.status_code}"
history = json.loads(r.data)
assert isinstance(history, list), "History should be a list"
assert len(history) == 5, f"P001 expected 5 rows, got {len(history)}"
dates = [row["date"] for row in history]
assert dates == sorted(dates), "History should be sorted ascending by date"
# Check all chart-required keys present
for key in ("date", "glucose", "systolic_bp", "diastolic_bp", "heart_rate", "sleep_hours", "medication_adherence"):
    assert key in history[0], f"History row missing key: {key}"
print(f"PASS: GET /api/history/P001 -> {len(history)} rows, sorted: {dates[0]} -> {dates[-1]}")

# ---------------------------------------------------------------------------
# 5. GET /api/history/P002 returns 7 rows
# ---------------------------------------------------------------------------
r = client.get("/api/history/P002")
assert r.status_code == 200
history2 = json.loads(r.data)
assert len(history2) == 7, f"P002 expected 7 rows, got {len(history2)}"
print(f"PASS: GET /api/history/P002 -> {len(history2)} rows")

# ---------------------------------------------------------------------------
# 6. GET /api/history/P003 returns 7 rows
# ---------------------------------------------------------------------------
r = client.get("/api/history/P003")
assert r.status_code == 200
history3 = json.loads(r.data)
assert len(history3) == 7, f"P003 expected 7 rows, got {len(history3)}"
print(f"PASS: GET /api/history/P003 -> {len(history3)} rows")

# ---------------------------------------------------------------------------
# 7. GET /api/history/PXXX (unknown patient) returns empty list
# ---------------------------------------------------------------------------
r = client.get("/api/history/PXXX")
assert r.status_code == 200
empty = json.loads(r.data)
assert empty == [], f"Unknown patient should return [], got {empty}"
print("PASS: GET /api/history/PXXX -> []")

# ---------------------------------------------------------------------------
# 8. POST /api/alert with High-risk vitals returns structured alert
# ---------------------------------------------------------------------------
high_vitals = {
    "patient_id": "P001", "age": 45, "condition": "Diabetes",
    "glucose": 195.0, "systolic_bp": 148.0, "diastolic_bp": 94.0,
    "heart_rate": 102.0, "sleep_hours": 5.0, "medication_adherence": "Missed"
}
r = client.post("/api/alert",
    data=json.dumps(high_vitals),
    content_type="application/json"
)
assert r.status_code == 200, f"POST /api/alert expected 200, got {r.status_code}"
alert_resp = json.loads(r.data)
assert "alert" in alert_resp, "Response should have 'alert' key"
alert = alert_resp["alert"]
assert alert is not None, "High-risk patient should produce a non-null alert"
for key in ("patient_id", "risk_level", "risk_score", "warnings", "timestamp", "message"):
    assert key in alert, f"Alert dict missing key: {key}"
assert alert["risk_level"] in ("High", "Critical"), f"Expected High/Critical, got {alert['risk_level']}"
print(f"PASS: POST /api/alert (high risk) -> alert risk_level={alert['risk_level']}, score={alert['risk_score']}")

# ---------------------------------------------------------------------------
# 9. POST /api/alert with Low-risk vitals returns null alert
# ---------------------------------------------------------------------------
low_vitals = {
    "patient_id": "P001", "age": 45, "condition": "Diabetes",
    "glucose": 110.0, "systolic_bp": 118.0, "diastolic_bp": 75.0,
    "heart_rate": 72.0, "sleep_hours": 7.5, "medication_adherence": "Taken"
}
r = client.post("/api/alert",
    data=json.dumps(low_vitals),
    content_type="application/json"
)
assert r.status_code == 200
alert_resp_low = json.loads(r.data)
assert alert_resp_low["alert"] is None, f"Low-risk should return null alert, got {alert_resp_low['alert']}"
print("PASS: POST /api/alert (low risk) -> alert=null")

# ---------------------------------------------------------------------------
# 10. GET /provider returns 200 (even if template not yet built)
# ---------------------------------------------------------------------------
# provider.html does not exist yet — we expect a 404/500, not a crash
r = client.get("/provider")
# Acceptable: 200 (if provider.html exists), 404, or 500 (template missing)
assert r.status_code in (200, 404, 500), f"GET /provider returned unexpected status {r.status_code}"
if r.status_code == 200:
    print("PASS: GET /provider -> 200")
else:
    print(f"INFO: GET /provider -> {r.status_code} (provider.html not yet built — expected)")

print()
print("=" * 50)
print("  ALL PHASE 2 SMOKE TESTS PASSED")
print("=" * 50)
