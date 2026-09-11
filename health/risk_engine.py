def calculate_risk(patient):
    score = 0
    warnings = []

    # --- Generic checks ---
    if patient["glucose"] > 180:
        score += 2
        warnings.append("Elevated glucose reading")

    if patient["systolic_bp"] > 140 or patient["diastolic_bp"] > 90:
        score += 2
        warnings.append("Elevated blood pressure")

    if patient["heart_rate"] > 100:
        score += 1
        warnings.append("High heart rate")

    if patient["medication_adherence"].lower() == "missed":
        score += 1
        warnings.append("Medication dose missed")

    if patient["sleep_hours"] < 6:
        score += 1
        warnings.append("Low sleep duration")

    # --- Condition-aware checks ---
    condition = patient.get("condition", "").strip()

    if condition == "Diabetes":
        # Second-tier glucose warning for critically elevated values
        if patient["glucose"] > 250:
            score += 1
            warnings.append("Critically high glucose")

    elif condition == "Hypertension":
        # Lower BP trigger for hypertension patients
        if patient["systolic_bp"] > 130 or patient["diastolic_bp"] > 85:
            score += 1
            warnings.append("Hypertension threshold reached")

    elif condition == "Heart Condition":
        # Elevated heart rate threshold is lower for cardiac patients
        if patient["heart_rate"] > 90:
            score += 1
            warnings.append("Elevated heart rate for cardiac patient")

    # --- Risk classification ---
    if score <= 1:
        risk_level = "Low"
    elif score <= 3:
        risk_level = "Moderate"
    elif score <= 5:
        risk_level = "High"
    else:
        risk_level = "Critical"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "warnings": warnings
    }


if __name__ == "__main__":
    # Test patient data
    patient = {
        "glucose": 185,
        "systolic_bp": 145,
        "diastolic_bp": 92,
        "heart_rate": 91,
        "medication_adherence": "Missed",
        "sleep_hours": 5.5,
        "condition": "Diabetes"
    }

    result = calculate_risk(patient)

    print("Risk Score:", result["risk_score"])
    print("Risk Level:", result["risk_level"])
    print("Warnings:")

    for warning in result["warnings"]:
        print("-", warning)
