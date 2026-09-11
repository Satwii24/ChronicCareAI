from health.risk_engine import calculate_risk
from ai.watsonx_client import ask_granite


patient = {
    "patient_id": "P001",
    "age": 45,
    "condition": "Diabetes",
    "glucose": 185,
    "systolic_bp": 145,
    "diastolic_bp": 92,
    "heart_rate": 91,
    "sleep_hours": 5.5,
    "medication_adherence": "Missed"
}

# Calculate risk
risk_result = calculate_risk(patient)

print("========== RISK ENGINE ==========")
print("Risk Score:", risk_result["risk_score"])
print("Risk Level:", risk_result["risk_level"])
print("Warnings:", risk_result["warnings"])

# Send result to Granite
print("\n========== GRANITE AI ==========")

ai_response = ask_granite(patient, risk_result)

print(ai_response)