import os
from pathlib import Path
from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

# Load .env from the main project folder
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key    = os.getenv("WATSONX_APIKEY")
project_id = os.getenv("WATSONX_PROJECT_ID")
url        = os.getenv("WATSONX_URL")

# Chat parameters — max_tokens controls response length (chat API uses max_tokens,
# not max_new_tokens). 600 is enough for the 6-point summary with room to spare.
_CHAT_PARAMS = {"max_tokens": 600, "temperature": 0.7}


def ask_granite(patient_data, risk_result):

    credentials = Credentials(
        api_key=api_key,
        url=url
    )

    model = ModelInference(
        model_id="ibm/granite-4-h-small",
        credentials=credentials,
        project_id=project_id
    )

    risk   = risk_result.get("risk",   risk_result) if isinstance(risk_result, dict) else risk_result
    trends = risk_result.get("trends", {})           if isinstance(risk_result, dict) else {}

    prompt = (
        "You are ChronicCare AI, an AI assistant for chronic disease monitoring.\n\n"
        "You help patients and healthcare providers understand health-monitoring data.\n\n"
        "IMPORTANT:\n"
        "- Do not diagnose diseases.\n"
        "- Do not prescribe medicines.\n"
        "- Do not change medication doses.\n"
        "- Do not replace healthcare professionals.\n"
        "- This is a monitoring and decision-support system.\n\n"
        f"Synthetic Patient Data:\n{patient_data}\n\n"
        f"Risk Engine Result:\n{risk}\n\n"
        f"Historical Trend Analysis:\n{trends}\n\n"
        "Provide:\n"
        "1. Risk summary\n"
        "2. Important observations\n"
        "3. Possible concerns or trends (reference the historical trend data above when relevant)\n"
        "4. General lifestyle suggestions\n"
        "5. Medication adherence reminder if applicable\n"
        "6. When to consider contacting a healthcare professional\n\n"
        "Clearly mention that this is a monitoring aid and not a medical diagnosis.\n"
        "Keep the response simple and patient-friendly."
    )

    # Use the chat API (replaces the deprecated /ml/v1/text/generation endpoint).
    result = model.chat(
        messages=[{"role": "user", "content": prompt}],
        params=_CHAT_PARAMS
    )

    return result["choices"][0]["message"]["content"]