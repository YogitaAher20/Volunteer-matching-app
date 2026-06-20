import os
import traceback
from dotenv import load_dotenv
load_dotenv()
try:
    import google.generativeai as genai
except ImportError:
    print("ERROR: google-generativeai package is not installed")
    raise

print("=" * 50)
print("GEMINI DIAGNOSTIC")
print("=" * 50)
import os

print("API KEY =", os.getenv("GEMINI_API_KEY"))
# Check API Key
api_key = os.getenv("GEMINI_API_KEY")

print(f"API Key Present: {bool(api_key)}")

if not api_key:
    print("ERROR: GEMINI_API_KEY not found")
    exit()

try:
    # Configure Gemini
    genai.configure(api_key=api_key)
    print("Gemini configured successfully")

    # Create model
    model = genai.GenerativeModel("gemini-2.5-flash")

    print(f"Model object created: {model}")

    # Simple test prompt
    prompt = """
    Return ONLY valid JSON.

    {
        "status": "success",
        "message": "Gemini is working"
    }
    """

    print("\nCalling Gemini...\n")

    response = model.generate_content(prompt)

    print("SUCCESS")
    print("\nRaw Response:")
    print("-" * 50)
    print(response.text)
    print("-" * 50)

except Exception as e:
    print("\nERROR OCCURRED")
    print("-" * 50)
    print(type(e).__name__)
    print(str(e))
    print("\nFull Traceback:")
    traceback.print_exc()