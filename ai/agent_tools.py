"""
ai/agent_tools.py

Agent-style tool functions for ChronicCare AI.

Exports five named tools:
    calculate_risk        -- deterministic risk scoring (re-exported)
    get_patient_history   -- load a patient's CSV history as a list of dicts
    detect_trends         -- trend detection from CSV history (re-exported)
    generate_health_summary -- call Granite AI for a patient-friendly summary
    create_provider_alert -- build a structured provider alert for High/Critical patients
"""

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from health.risk_engine import calculate_risk          # re-export
from health.trend_engine import detect_trends          # re-export
from ai.watsonx_client import ask_granite

# Absolute path to CSV — works regardless of CWD
_CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "patient_data.csv"


# ---------------------------------------------------------------------------
# Tool: get_patient_history
# ---------------------------------------------------------------------------

def get_patient_history(patient_id):
    """
    Return a patient's full history from the CSV as a list of row dicts,
    sorted ascending by date.

    Returns an empty list if the patient_id is not found.
    """
    df = pd.read_csv(_CSV_PATH)
    patient_rows = df[df["patient_id"] == patient_id].copy()
    if patient_rows.empty:
        return []
    patient_rows = patient_rows.sort_values("date")
    return patient_rows.to_dict(orient="records")


# ---------------------------------------------------------------------------
# Tool: generate_health_summary
# ---------------------------------------------------------------------------

def generate_health_summary(patient, risk_result, trends):
    """
    Call IBM Granite 4-H Small to produce a patient-friendly health summary.

    Args:
        patient     -- dict with patient demographics and current vitals
        risk_result -- dict from calculate_risk: {risk_score, risk_level, warnings}
        trends      -- dict from detect_trends: {glucose, blood_pressure, heart_rate, sleep}

    Returns:
        str — the AI-generated summary text
    """
    combined = {
        "risk": risk_result,
        "trends": trends
    }
    return ask_granite(patient, combined)


# ---------------------------------------------------------------------------
# Tool: create_provider_alert
# ---------------------------------------------------------------------------

def create_provider_alert(patient, risk_result):
    """
    Build a structured provider alert for patients at High or Critical risk.

    Args:
        patient     -- dict with at least patient_id and condition
        risk_result -- dict from calculate_risk: {risk_score, risk_level, warnings}

    Returns:
        dict with alert details, or None if risk is Low or Moderate
    """
    risk_level = risk_result.get("risk_level", "Low")

    if risk_level not in ("High", "Critical"):
        return None

    patient_id = patient.get("patient_id", "Unknown")
    condition = patient.get("condition", "Unknown")
    risk_score = risk_result.get("risk_score", 0)
    warnings = risk_result.get("warnings", [])

    message = (
        f"ALERT: Patient {patient_id} ({condition}) has reached {risk_level} risk "
        f"(score {risk_score}/7). Immediate review recommended. "
        f"Triggered warnings: {'; '.join(warnings) if warnings else 'None'}. "
        "This is a monitoring aid — not a clinical diagnosis. "
        "Please consult a qualified healthcare professional."
    )

    return {
        "patient_id": patient_id,
        "condition": condition,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "warnings": warnings,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": message
    }
