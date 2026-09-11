import pandas as pd


def detect_trends(patient_id):

    file_path = "data/patient_data.csv"

    df = pd.read_csv(file_path)

    patient_data = df[df["patient_id"] == patient_id].copy()

    if patient_data.empty:
        return {"message": "No patient history found."}

    patient_data = patient_data.sort_values("date")

    trends = {}

    # Glucose trend
    glucose_change = (
        patient_data["glucose"].iloc[-1]
        - patient_data["glucose"].iloc[0]
    )

    if glucose_change > 20:
        trends["glucose"] = "Increasing"

    elif glucose_change < -20:
        trends["glucose"] = "Decreasing"

    else:
        trends["glucose"] = "Stable"

    # Blood pressure trend
    bp_change = (
        patient_data["systolic_bp"].iloc[-1]
        - patient_data["systolic_bp"].iloc[0]
    )

    if bp_change > 10:
        trends["blood_pressure"] = "Increasing"

    elif bp_change < -10:
        trends["blood_pressure"] = "Decreasing"

    else:
        trends["blood_pressure"] = "Stable"

    # Heart rate trend
    hr_change = (
        patient_data["heart_rate"].iloc[-1]
        - patient_data["heart_rate"].iloc[0]
    )

    if hr_change > 10:
        trends["heart_rate"] = "Increasing"

    elif hr_change < -10:
        trends["heart_rate"] = "Decreasing"

    else:
        trends["heart_rate"] = "Stable"

    # Sleep trend
    sleep_change = (
        patient_data["sleep_hours"].iloc[-1]
        - patient_data["sleep_hours"].iloc[0]
    )

    if sleep_change < -1:
        trends["sleep"] = "Decreasing"

    elif sleep_change > 1:
        trends["sleep"] = "Improving"

    else:
        trends["sleep"] = "Stable"

    return trends


if __name__ == "__main__":
    result = detect_trends("P001")

    print("========== TREND ANALYSIS ==========")

    for metric, trend in result.items():
        print(metric, ":", trend)