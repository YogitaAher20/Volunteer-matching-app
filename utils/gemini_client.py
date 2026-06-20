import logging
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check and configure Gemini API key
api_key = os.getenv("GEMINI_API_KEY", "")
api_key_present = bool(api_key and api_key.strip() and api_key != "your_gemini_api_key_here")
is_configured = False

if api_key_present:
    try:
        genai.configure(api_key=api_key)
        is_configured = True
        logger.info("Gemini API key detected. Attempting model initialization.")
    except Exception as exc:
        is_configured = False
        logger.exception("Gemini configuration failed: %s", exc)
else:
    logger.warning("Gemini API key is missing or placeholder.")


def get_gemini_model(model_name="gemini-2.5-flash"):
    """
    Returns a configured GenerativeModel instance if the API is configured.

    Args:
        model_name (str): The Gemini model identifier

    Returns:
        genai.GenerativeModel or None: A configured model instance or None if setup failed
    """
    if not api_key_present:
        logger.warning("Gemini model was not created because the API key is missing.")
        return None

    if not is_configured:
        logger.warning("Gemini model was not created because configuration failed.")
        return None

    try:
        model = genai.GenerativeModel(model_name)
        logger.info("Gemini model created successfully: %s", model_name)
        return model
    except Exception as exc:
        logger.exception("Gemini model creation failed for %s: %s", model_name, exc)
        return None
