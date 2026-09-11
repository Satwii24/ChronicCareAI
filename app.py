from flask import Flask, render_template, request, jsonify, redirect

from health.risk_engine import calculate_risk
from health.trend_engine import detect_trends
from ai.watsonx_client import ask_granite
from ai.agent_tools import get_patient_history, create_provider_alert


app = Flask(__name__)

# ---------------------------------------------------------------------------
# Demo patient registry
# ---------------------------------------------------------------------------
DEMO_PATIENTS = [
    {"patient_id": "P001", "name": "Alex Johnson",   "age": 45, "condition": "Diabetes"},
    {"patient_id": "P002", "name": "Maria Garcia",   "age": 58, "condition": "Hypertension"},
    {"patient_id": "P003", "name": "David Lee",      "age": 67, "condition": "Heart Condition"},
]


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return redirect("/patient")


@app.route("/patient")
def patient_dashboard():
    return render_template("patient.html")


@app.route("/provider")
def provider_dashboard():
    return render_template("provider.html")


# ---------------------------------------------------------------------------
# Existing analysis route — unchanged
# ---------------------------------------------------------------------------

@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.get_json()

    patient = {
        "patient_id": data.get("patient_id", "P001"),
        "age": int(data.get("age", 45)),
        "condition": data.get("condition", "Diabetes"),
        "glucose": float(data.get("glucose", 0)),
        "systolic_bp": float(data.get("systolic_bp", 0)),
        "diastolic_bp": float(data.get("diastolic_bp", 0)),
        "heart_rate": float(data.get("heart_rate", 0)),
        "sleep_hours": float(data.get("sleep_hours", 0)),
        "medication_adherence": data.get(
            "medication_adherence", "Taken"
        )
    }

    # Calculate current risk
    risk_result = calculate_risk(patient)

    # Analyze historical trends
    trend_result = detect_trends(patient["patient_id"])

    # Send current data + risk + trends to Granite
    combined_result = {
        "risk": risk_result,
        "trends": trend_result
    }

    ai_response = ask_granite(
        patient,
        combined_result
    )

    return jsonify({
        "patient": patient,
        "risk": risk_result,
        "trends": trend_result,
        "ai_response": ai_response
    })


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@app.route("/api/patients")
def api_patients():
    return jsonify(DEMO_PATIENTS)


@app.route("/api/history/<patient_id>")
def api_history(patient_id):
    history = get_patient_history(patient_id)
    return jsonify(history)


@app.route("/api/alert", methods=["POST"])
def api_alert():
    data = request.get_json()

    patient = {
        "patient_id": data.get("patient_id", "P001"),
        "age": int(data.get("age", 45)),
        "condition": data.get("condition", "Unknown"),
        "glucose": float(data.get("glucose", 0)),
        "systolic_bp": float(data.get("systolic_bp", 0)),
        "diastolic_bp": float(data.get("diastolic_bp", 0)),
        "heart_rate": float(data.get("heart_rate", 0)),
        "sleep_hours": float(data.get("sleep_hours", 0)),
        "medication_adherence": data.get("medication_adherence", "Taken")
    }

    risk_result = calculate_risk(patient)
    alert = create_provider_alert(patient, risk_result)

    return jsonify({"alert": alert})


if __name__ == "__main__":
    app.run(debug=True)