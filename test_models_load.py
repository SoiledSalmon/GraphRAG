
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("GEMINI_API_KEY not found in environment.")
    exit(1)

genai.configure(api_key=api_key)

_MODELS_TO_TRY = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-2.0-flash-001",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-3-pro-preview",
    "gemini-3-flash-preview",
    "gemma-3-27b-it",
    "gemma-3-12b-it",
    "gemma-3-4b-it",
    "gemma-3-1b-it",
    "deep-research-pro-preview-12-2025"
]

print("Verifying model initialization...")
success_count = 0
for model_name in _MODELS_TO_TRY:
    try:
        # Just check if we can initialize the model object
        model = genai.GenerativeModel(model_name)
        print(f"✓ {model_name} initialized")
        success_count += 1
    except Exception as e:
        print(f"❌ {model_name} failed: {e}")

print(f"\nVerification complete: {success_count}/{len(_MODELS_TO_TRY)} models successfully initialized.")
