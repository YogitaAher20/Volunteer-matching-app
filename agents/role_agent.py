import json
import re
import logging
from utils.gemini_client import get_gemini_model
from utils.prompts import ROLE_RECOMMENDATION_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def recommend_role_fallback(profile, reason="FALLBACK"):
    """
    Deterministic fallback rule-based matching engine if Gemini fails or is not configured.

    Args:
        profile (dict): Structured volunteer profile
        reason (str): Explanation for why fallback was used

    Returns:
        dict: Containing 'role', 'match_score', and 'reason'
    """
    logger.warning("Using rule-based fallback recommendation because: %s", reason)
    # Convert list attributes to lowercase sets for matching
    strengths_lower = {s.lower() for s in profile.get("strengths", [])}
    interests_lower = {i.lower() for i in profile.get("interests", [])}
    
    # Define rules mapping structured strengths & interests to target roles
    role_rules = [
        {
            "role": "Education Volunteer",
            "strengths": {"education & instruction"},
            "interests": {"education"},
            "reason": "(Rule-based Fallback) Your strength in instruction and learning matches our educational program needs."
        },
        {
            "role": "Social Media Volunteer",
            "strengths": {"visual design", "digital marketing"},
            "interests": {"awareness campaigns"},
            "reason": "(Rule-based Fallback) Your background in design/marketing aligns directly with our public campaigns and branding."
        },
        {
            "role": "Technical Volunteer",
            "strengths": {"software development", "research & analytics"},
            "interests": {"technology projects"},
            "reason": "(Rule-based Fallback) Your capabilities in development or analysis fit our website maintenance and data reporting tasks."
        },
        {
            "role": "Content Creator",
            "strengths": {"written communication", "video production", "visual media"},
            "interests": {"content creation"},
            "reason": "(Rule-based Fallback) Your creative media and writing strengths are a perfect match to compile stories and design newsletters."
        },
        {
            "role": "Fundraising Volunteer",
            "strengths": {"resource mobilization"},
            "interests": {"fundraising"},
            "reason": "(Rule-based Fallback) Your strength in resource mobilization will be instrumental in executing campaigns and attracting sponsorships."
        },
        {
            "role": "Event Management Volunteer",
            "strengths": {"operations & logistics"},
            "interests": {"event organization"},
            "reason": "(Rule-based Fallback) Your operations skills are suited for coordinating venues, donation drives, and logistics."
        },
        {
            "role": "Community Outreach Volunteer",
            "strengths": {"public communication", "strategic management"},
            "interests": {"community outreach", "volunteer coordination"},
            "reason": "(Rule-based Fallback) Your communication abilities match our community advocacy and volunteer management programs."
        }
    ]
    
    best_role = None
    max_score = 0
    best_reason = ""
    
    for rule in role_rules:
        strength_matches = len(strengths_lower.intersection(rule["strengths"]))
        interest_matches = len(interests_lower.intersection(rule["interests"]))
        total_matches = strength_matches + interest_matches
        
        if total_matches > 0:
            score = min(70 + (total_matches * 15), 95)
            if score > max_score:
                max_score = score
                best_role = rule["role"]
                best_reason = rule["reason"]
                
    # Fallback default role
    if not best_role:
        best_role = "Community Outreach Volunteer"
        max_score = 50
        best_reason = "(Rule-based Fallback) Your strengths and interests represent a versatile general profile. Community Outreach is our most active initiative and welcomes your general support."
        
    return {
        "role": best_role,
        "match_score": max_score,
        "reason": best_reason
    }

def _clean_json_text(text):
    """
    Removes common wrappers that can appear around LLM JSON responses.
    """
    if not text:
        return ""

    cleaned = text.strip()
    cleaned = cleaned.replace("```json", "")
    cleaned = cleaned.replace("```", "")
    cleaned = cleaned.strip()
    return cleaned


def _extract_json_object(text):
    """
    Tries to extract a JSON object from a noisy response.
    """
    cleaned = _clean_json_text(text)

    # Accept direct JSON objects.
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # Try to recover a JSON object if the model inserted extra text.
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass

    return None


def _is_probably_html(text):
    return bool(re.search(r"<[^>]+>", text))


def recommend_role(profile):
    """
    Recommends an NGO volunteer role using Gemini, falling back to rule-based if necessary.
    
    Args:
        profile (dict): Structured volunteer profile
        
    Returns:
        dict: Recommended role parameters
    """
    model = get_gemini_model()
    if not model:
        logger.warning("Gemini model is not available. Falling back to rule-based recommendation with reason: MODEL_NOT_INITIALIZED")
        return recommend_role_fallback(profile, reason="MODEL_NOT_INITIALIZED")
        
    try:
        # Build prompt using the structured profile
        prompt = ROLE_RECOMMENDATION_PROMPT.format(
            strengths=", ".join(profile.get("strengths", ["General Support"])),
            interests=", ".join(profile.get("interests", ["General Support"])),
            availability=profile.get("availability", "Weekdays (1-3 hours/week)")
        )
        logger.info("Prompt built successfully")
        logger.info("Calling Gemini role recommendation API.")
        logger.info("Gemini prompt prepared for role recommendation.")

        # Query Gemini requesting JSON configuration
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )

        text = response.text.strip() if hasattr(response, "text") else ""
        logger.info("Raw Gemini response text: %s", text)

        # If the model returns HTML or any other non-JSON response, reject it.
        if _is_probably_html(text):
            logger.warning("Gemini returned HTML-like output. Falling back to rule-based recommendation with reason: HTML_RESPONSE")
            return recommend_role_fallback(profile, reason="HTML_RESPONSE")

        data = _extract_json_object(text)
        if not isinstance(data, dict):
            logger.warning("Gemini output could not be parsed as JSON. Falling back to rule-based recommendation with reason: JSON_PARSE_ERROR")
            logger.warning("Raw output that failed parsing: %s", text)
            return recommend_role_fallback(profile, reason="JSON_PARSE_ERROR")

        # Extract response properties
        role = data.get("role")
        match_score = data.get("match_score", data.get("score", 85))

        try:
            match_score = int(match_score)
        except (TypeError, ValueError):
            match_score = 85

        reason = data.get("reason", "No reason provided by AI.")
        if not isinstance(reason, str):
            reason = str(reason)

        # Validate that Gemini returned a correct role title
        valid_roles = {
            "Education Volunteer", "Fundraising Volunteer", "Social Media Volunteer",
            "Content Creator", "Event Management Volunteer", "Community Outreach Volunteer",
            "Technical Volunteer"
        }
        
        if role in valid_roles:
            logger.info("Gemini recommendation succeeded with role: %s", role)
            return {
                "role": role,
                "match_score": match_score,
                "reason": f"(AI Recommendation) {reason}",
                "debug": {
                    "source": "gemini",
                    "raw_response": text,
                    "fallback_reason": None
                }
            }
        else:
            logger.warning(
                "Gemini returned an invalid role value %s. Falling back to rule-based recommendation with reason: INVALID_ROLE",
                role
            )
            return recommend_role_fallback(profile, reason="INVALID_ROLE")
            
    except Exception as exc:
        logger.exception("Gemini API call failed")

        return {
            "role": "ERROR",
            "match_score": 0,
            "reason": f"API_FAILURE: {type(exc).__name__}: {exc}",
            "debug": {
                "source": "exception",
                "raw_response": None,
                "fallback_reason": str(exc)
            }
        }
