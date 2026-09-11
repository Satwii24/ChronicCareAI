"""
Phase 1 smoke tests — no .env / watsonx credentials required.
Tests CSV trends, get_patient_history, calculate_risk re-export,
detect_trends re-export, and create_provider_alert.
"""

import sys
import os

# Run from project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# 1. CSV trend verification
# ---------------------------------------------------------------------------
from health.trend_engine import detect_trends

p001 = detect_trends("P001")
p002 = detect_trends("P002")
p003 = detect_trends("P003")

print("=== CSV TREND CHECK ===")
print("P001 trends:", p001)
print("P002 trends:", p002)
print("P003 trends:", p003)

assert p001 != {"message": "No patient history found."}, "P001 missing from CSV"
assert p002 != {"message": "No patient history found."}, "P002 missing from CSV"
assert p003 != {"message": "No patient history found."}, "P003 missing from CSV"

assert p001.get("glucose") == "Increasing", (
    f"P001 glucose expected Increasing, got {p001.get('glucose')}"
)
assert p002.get("blood_pressure") == "Increasing", (
    f"P002 BP expected Increasing, got {p002.get('blood_pressure')}"
)
assert p003.get("heart_rate") == "Increasing", (
    f"P003 HR expected Increasing, got {p003.get('heart_rate')}"
)
print("PASS: All trend assertions OK")

# ---------------------------------------------------------------------------
# 2. get_patient_history
# ---------------------------------------------------------------------------
from ai.agent_tools import get_patient_history

h001 = get_patient_history("P001")
h002 = get_patient_history("P002")
h003 = get_patient_history("P003")
h_missing = get_patient_history("P999")

print()
print("=== get_patient_history ===")
print(f"P001: {len(h001)} rows, first={h001[0]['date']}, last={h001[-1]['date']}")
print(f"P002: {len(h002)} rows, first={h002[0]['date']}, last={h002[-1]['date']}")
print(f"P003: {len(h003)} rows, first={h003[0]['date']}, last={h003[-1]['date']}")
print(f"P999: {h_missing}")

assert len(h001) == 5, f"P001 expected 5 rows, got {len(h001)}"
assert len(h002) == 7, f"P002 expected 7 rows, got {len(h002)}"
assert len(h003) == 7, f"P003 expected 7 rows, got {len(h003)}"
assert h_missing == [], f"P999 expected [], got {h_missing}"
# Verify sorted ascending
assert h001[0]["date"] < h001[-1]["date"], "P001 history not sorted ascending"
assert h002[0]["date"] < h002[-1]["date"], "P002 history not sorted ascending"
print("PASS: get_patient_history OK")

# ---------------------------------------------------------------------------
# 3. calculate_risk (re-export)
# ---------------------------------------------------------------------------
from ai.agent_tools import calculate_risk

r = calculate_risk({
    "patient_id": "P001", "age": 45, "condition": "Diabetes",
    "glucose": 185, "systolic_bp": 145, "diastolic_bp": 92,
    "heart_rate": 91, "sleep_hours": 5.5, "medication_adherence": "Missed"
})
print()
print("=== calculate_risk ===")
print("Result:", r)
assert r["risk_level"] in ("High", "Critical"), (
    f"Expected High or Critical for P001 demo vitals, got {r['risk_level']}"
)
assert isinstance(r["warnings"], list) and len(r["warnings"]) > 0
assert "risk_score" in r and "risk_level" in r and "warnings" in r
print("PASS: calculate_risk OK")

# ---------------------------------------------------------------------------
# 4. detect_trends re-export
# ---------------------------------------------------------------------------
from ai.agent_tools import detect_trends as dt

t = dt("P002")
print()
print("=== detect_trends re-export ===")
print("P002 trends:", t)
assert "blood_pressure" in t, "blood_pressure key missing from P002 trends"
print("PASS: detect_trends re-export OK")

# ---------------------------------------------------------------------------
# 5. create_provider_alert
# ---------------------------------------------------------------------------
from ai.agent_tools import create_provider_alert

patient = {"patient_id": "P001", "condition": "Diabetes"}
high_risk = {"risk_level": "High",     "risk_score": 4, "warnings": ["Elevated glucose", "Elevated BP"]}
crit_risk = {"risk_level": "Critical", "risk_score": 6, "warnings": ["Elevated glucose"]}
low_risk  = {"risk_level": "Low",      "risk_score": 1, "warnings": []}
mod_risk  = {"risk_level": "Moderate", "risk_score": 2, "warnings": []}

alert_high = create_provider_alert(patient, high_risk)
alert_crit = create_provider_alert(patient, crit_risk)
alert_low  = create_provider_alert(patient, low_risk)
alert_mod  = create_provider_alert(patient, mod_risk)

print()
print("=== create_provider_alert ===")
print("High  alert keys:", list(alert_high.keys()) if alert_high else None)
print("Crit  alert risk_level:", alert_crit["risk_level"] if alert_crit else None)
print("Low   returns None:", alert_low is None)
print("Mod   returns None:", alert_mod is None)
print("High  message snippet:", alert_high["message"][:80] if alert_high else None)

assert alert_high is not None, "High risk should produce an alert"
assert alert_crit is not None, "Critical risk should produce an alert"
assert alert_low  is None,     "Low risk should return None"
assert alert_mod  is None,     "Moderate risk should return None"

required_keys = {"patient_id", "condition", "risk_level", "risk_score", "warnings", "timestamp", "message"}
missing = required_keys - set(alert_high.keys())
assert not missing, f"Alert dict missing keys: {missing}"

assert "ALERT" in alert_high["message"], "Alert message should start with ALERT"
assert "monitoring aid" in alert_high["message"], "Alert should include monitoring disclaimer"
assert alert_crit["risk_level"] == "Critical"
assert alert_high["risk_level"] == "High"
print("PASS: create_provider_alert OK")

print()
print("=" * 45)
print("  ALL PHASE 1 SMOKE TESTS PASSED")
print("=" * 45)
