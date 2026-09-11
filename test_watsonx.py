import os
from pathlib import Path
from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

# Find .env in the same folder as this Python file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("WATSONX_APIKEY")
project_id = os.getenv("WATSONX_PROJECT_ID")
url = os.getenv("WATSONX_URL")

print("Connecting to IBM watsonx.ai...")
print("Project ID loaded:", bool(project_id))
print("Region:", url)

if not api_key or not project_id or not url:
    print("\nERROR: .env values are missing.")
    print("Make sure .env is in the same folder as test_watsonx.py")
    exit()

credentials = Credentials(
    api_key=api_key,
    url=url
)

model = ModelInference(
    model_id="ibm/granite-4-h-small",
    credentials=credentials,
    project_id=project_id
)

response = model.generate_text(
    prompt="Say hello to ChronicCare AI in one short sentence."
)

print("\nGranite response:")
print(response)